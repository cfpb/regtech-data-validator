import polars as pl

from regtech_data_validator.checks import Severity
from regtech_data_validator.validator import (
    validate_batch_csv,
    get_phase_1_schema_for_lei,
    get_phase_2_schema_for_lei,
    get_register_schema,
)
from regtech_data_validator.validation_results import ValidationPhase

GOOD_FILE_PATH = "./tests/data/sblar_no_findings.csv"
ALL_SYNTAX_ERRORS = "./tests/data/all_syntax_errors.csv"
ALL_LOGIC_ERRORS = "./tests/data/all_logic_errors.csv"
ALL_LOGIC_WARNINGS = "./tests/data/all_logic_warnings.csv"


class TestValidatingSampleData:

    def test_run_validation_on_good_data_invalid_lei(self):
        lei = "000TESTFIUIDDONOTUS1"
        results = list(validate_batch_csv(GOOD_FILE_PATH, {'lei': lei}))

        assert results[0][0]['validation_id'].eq('W0003').all()
        assert results[0][1] == ValidationPhase.LOGICAL.value

    def test_run_validation_on_good_data_valid_lei(self):
        lei = "123456789TESTBANK123"
        results = list(validate_batch_csv(GOOD_FILE_PATH, {'lei': lei}))

        assert len(results) == 0

    def test_all_syntax_errors(self):
        results = list(validate_batch_csv(ALL_SYNTAX_ERRORS))

        syntax_schema = get_phase_1_schema_for_lei()
        syntax_checks = [check.title for col_schema in syntax_schema.columns.values() for check in col_schema.checks]

        # check that the findings validation_id Series contains at least 1 of every syntax check id
        assert len(set(results[0][0]['validation_id'].to_list()).difference(set(syntax_checks))) == 0
        assert results[0][1] == ValidationPhase.SYNTACTICAL

    def test_all_logic_errors(self):
        findings = []
        final_phase = None
        for finding, phase in validate_batch_csv(ALL_LOGIC_ERRORS):
            print(f"Appending {finding}")
            findings.append(finding)
            final_phase = phase

        results = pl.concat(findings, how="diagonal")

        logic_schema = get_phase_2_schema_for_lei()
        register_schema = get_register_schema()
        logic_checks = [
            check.title
            for col_schema in logic_schema.columns.values()
            for check in col_schema.checks
            if check.severity == Severity.ERROR
        ]
        logic_checks.extend(
            [check.title for col_schema in register_schema.columns.values() for check in col_schema.checks]
        )

        results = results.filter(pl.col('validation_type') == 'Error')

        # check that the findings validation_id Series contains at least 1 of every logic error check id
        assert len(set(results['validation_id'].to_list()).difference(set(logic_checks))) == 0
        assert final_phase == ValidationPhase.LOGICAL

    def test_all_logic_warnings(self):
        findings = []
        final_phase = None
        for finding, phase in validate_batch_csv(ALL_LOGIC_WARNINGS, context={"lei": "000TESTFIUIDDONOTUSE"}):
            findings.append(finding)
            final_phase = phase

        results = pl.concat(findings, how="diagonal")

        logic_schema = get_phase_2_schema_for_lei()
        logic_checks = [
            check.title
            for col_schema in logic_schema.columns.values()
            for check in col_schema.checks
            if check.severity == Severity.WARNING
        ]

        results = results.filter(pl.col('validation_type') == 'Warning')

        # check that the findings validation_id Series contains at least 1 of every logic warning check id
        assert len(set(results['validation_id'].to_list()).difference(set(logic_checks))) == 0
        assert final_phase == ValidationPhase.LOGICAL
