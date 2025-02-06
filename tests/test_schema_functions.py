import polars as pl
import pytest
import tempfile
from pathlib import Path
from polars.exceptions import ColumnNotFoundError

from regtech_data_validator.validator import validate_batch_csv
from regtech_data_validator.validation_results import ValidationPhase


@pytest.fixture
def csv_df_file(request):
    df_data = get_data(request.param) if hasattr(request, 'param') else get_data()
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.csv') as gf:
        gf.write(pl.DataFrame(df_data).write_csv())
        temp_path = Path(gf.name)
    yield temp_path
    temp_path.unlink()


@pytest.fixture
def csv_df_mission_column_file(request):
    df_data = get_data(request.param) if hasattr(request, 'param') else get_data()
    df_data = df_data.pop('uid')
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.csv') as gf:
        gf.write(pl.DataFrame(df_data).write_csv())
        temp_path = Path(gf.name)
    yield temp_path
    temp_path.unlink()


@pytest.fixture
def csv_df_same_uids_file(request):
    df_data = get_data(request.param) if hasattr(request, 'param') else get_data()
    df = pl.concat([pl.DataFrame(df_data), pl.DataFrame(df_data)])
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.csv') as gf:
        gf.write(df.write_csv())
        temp_path = Path(gf.name)
    yield temp_path
    temp_path.unlink()


def get_data(update_data: dict[str, list[str]] = {}) -> dict[str, list[str]]:
    default = {
        "uid": ["000TESTFIUIDDONOTUSEXGXVID11XTC1"],
        "app_date": ["20241201"],
        "app_method": ["1"],
        "app_recipient": ["1"],
        "ct_credit_product": ["988"],
        "ct_credit_product_ff": [""],
        "ct_guarantee": ["999"],
        "ct_guarantee_ff": [""],
        "ct_loan_term_flag": ["999"],
        "ct_loan_term": [""],
        "credit_purpose": ["999"],
        "credit_purpose_ff": [""],
        "amount_applied_for_flag": ["999"],
        "amount_applied_for": [""],
        "amount_approved": [""],
        "action_taken": ["5"],
        "action_taken_date": ["20241231"],
        "denial_reasons": ["999"],
        "denial_reasons_ff": [""],
        "pricing_interest_rate_type": ["999"],
        "pricing_init_rate_period": [""],
        "pricing_fixed_rate": [""],
        "pricing_adj_margin": [""],
        "pricing_adj_index_name": ["999"],
        "pricing_adj_index_name_ff": [""],
        "pricing_adj_index_value": [""],
        "pricing_origination_charges": [""],
        "pricing_broker_fees": [""],
        "pricing_initial_charges": [""],
        "pricing_mca_addcost_flag": ["999"],
        "pricing_mca_addcost": [""],
        "pricing_prepenalty_allowed": ["999"],
        "pricing_prepenalty_exists": ["999"],
        "census_tract_adr_type": ["988"],
        "census_tract_number": [""],
        "gross_annual_revenue_flag": ["988"],
        "gross_annual_revenue": [""],
        "naics_code_flag": ["988"],
        "naics_code": [""],
        "number_of_workers": ["988"],
        "time_in_business_type": ["988"],
        "time_in_business": [""],
        "business_ownership_status": ["988"],
        "num_principal_owners_flag": ["988"],
        "num_principal_owners": [""],
        "po_1_ethnicity": [""],
        "po_1_ethnicity_ff": [""],
        "po_1_race": [""],
        "po_1_race_anai_ff": [""],
        "po_1_race_asian_ff": [""],
        "po_1_race_baa_ff": [""],
        "po_1_race_pi_ff": [""],
        "po_1_gender_flag": [""],
        "po_1_gender_ff": [""],
        "po_2_ethnicity": [""],
        "po_2_ethnicity_ff": [""],
        "po_2_race": [""],
        "po_2_race_anai_ff": [""],
        "po_2_race_asian_ff": [""],
        "po_2_race_baa_ff": [""],
        "po_2_race_pi_ff": [""],
        "po_2_gender_flag": [""],
        "po_2_gender_ff": [""],
        "po_3_ethnicity": [""],
        "po_3_ethnicity_ff": [""],
        "po_3_race": [""],
        "po_3_race_anai_ff": [""],
        "po_3_race_asian_ff": [""],
        "po_3_race_baa_ff": [""],
        "po_3_race_pi_ff": [""],
        "po_3_gender_flag": [""],
        "po_3_gender_ff": [""],
        "po_4_ethnicity": [""],
        "po_4_ethnicity_ff": [""],
        "po_4_race": [""],
        "po_4_race_anai_ff": [""],
        "po_4_race_asian_ff": [""],
        "po_4_race_baa_ff": [""],
        "po_4_race_pi_ff": [""],
        "po_4_gender_flag": [""],
        "po_4_gender_ff": [""],
    }
    default.update(update_data)
    return default


'''
class TestValidate:
    util = TestUtil()
    phase1_schema = get_phase_1_schema_for_lei()
    phase2_schema = get_phase_2_schema_for_lei()

    def test_with_valid_dataframe(self):
        df = pl.DataFrame(data=self.util.get_data())
        p1_results = validate(self.phase1_schema, df)
        p2_results = validate(self.phase2_schema, df)

        assert p1_results.is_valid
        assert p2_results.is_valid

    def test_with_valid_lei(self):
        lei = "000TESTFIUIDDONOTUSE"
        phase1_schema_by_lei = get_phase_1_schema_for_lei({'lei': lei})
        phase2_schema_by_lei = get_phase_2_schema_for_lei({'lei': lei})

        df = pl.DataFrame(data=self.util.get_data())

        p1_results = validate(phase1_schema_by_lei, df)
        p2_results = validate(phase2_schema_by_lei, df)

        assert p1_results.is_valid
        assert p2_results.is_valid

    def test_with_invalid_dataframe(self):
        df = pl.DataFrame(data=self.util.get_data({"ct_credit_product": ["989"]}))

        p1_results = validate(self.phase1_schema, df)
        p2_results = validate(self.phase2_schema, df)

        assert not p1_results.is_valid
        assert len(p1_results.findings) == 1
        assert p2_results.is_valid

    def test_with_multi_invalid_dataframe(self):
        df = pl.DataFrame(
            data=self.util.get_data(
                {
                    "ct_credit_product": ["989"],
                    "num_principal_owners": ["1"],
                    "action_taken": ["2"],
                }
            )
        )
        results = validate(self.phase1_schema, df)
        assert not results.is_valid
        assert len(results.findings) == 1

        results = validate(self.phase2_schema, df)
        # 4 unique findings raised
        assert results.findings['finding_no'].n_unique() == 4

    def test_with_invalid_lei(self):
        lei = "000TESTFIUIDDONOTUS1"

        phase1_schema_by_lei = get_phase_1_schema_for_lei({'lei': lei})
        phase2_schema_by_lei = get_phase_2_schema_for_lei({'lei': lei})

        df = pl.DataFrame(data=self.util.get_data({"ct_credit_product": ["989"]}))

        p1_results = validate(phase1_schema_by_lei, df)
        p2_results = validate(phase2_schema_by_lei, df)

        # 1 unique findings raised in phase 1
        assert not p1_results.is_valid
        assert p1_results.findings['finding_no'].n_unique() == 1

        # 1 unique finding raised in phase 2
        assert not p2_results.is_valid
        assert p2_results.findings['finding_no'].n_unique() == 1
'''


class TestValidatePhases:

    def test_with_valid_data(self, csv_df_file):
        results = validate_batch_csv(csv_df_file)
        assert all([r.findings.is_empty() for r in results])

    def test_with_valid_lei(self, csv_df_file):
        results = validate_batch_csv(csv_df_file, context={'lei': "000TESTFIUIDDONOTUSE"})
        assert all([r.findings.is_empty() for r in results])

    @pytest.mark.parametrize(
        "csv_df_file",
        [({"ct_credit_product": ["989"]})],
        indirect=True,
    )
    def test_with_invalid_data(self, csv_df_file):
        results = list(validate_batch_csv(csv_df_file))
        assert len(results) == 1
        assert results[0].findings.height == 1
        assert results[0].phase == ValidationPhase.SYNTACTICAL

    @pytest.mark.parametrize(
        "csv_df_file",
        [
            (
                {
                    "ct_credit_product": ["989"],
                    "num_principal_owners": ["10"],
                    "action_taken": ["20"],
                }
            )
        ],
        indirect=True,
    )
    def test_with_multi_invalid_data_with_phase1(self, csv_df_file):
        results = list(validate_batch_csv(csv_df_file))
        assert len(results) == 1
        assert results[0].findings.height == 3
        assert results[0].phase == ValidationPhase.SYNTACTICAL

    @pytest.mark.parametrize(
        "csv_df_file",
        [
            (
                {
                    "num_principal_owners_flag": ["988"],
                    "num_principal_owners": ["1"],
                    "action_taken": ["3"],
                    "pricing_interest_rate_type": ["1"],
                }
            )
        ],
        indirect=True,
    )
    def test_with_multi_invalid_data_with_phase2(self, csv_df_file):
        results = list(validate_batch_csv(csv_df_file))
        assert len(results) == 3
        assert results[2].findings.height == 7
        assert results[2].phase == ValidationPhase.LOGICAL

    def test_with_non_matching_lei(self, csv_df_file):
        results = list(validate_batch_csv(csv_df_file, context={'lei': "000TESTFIUIDDONOTUS1"}))
        assert len(results) == 3
        assert results[2].findings.height == 1
        assert results[2].findings['validation_id'].item() == 'W0003'
        assert results[2].phase == ValidationPhase.LOGICAL

    def test_column_not_found_in_df(self, csv_df_mission_column_file):
        with pytest.raises(ColumnNotFoundError) as re:
            list(validate_batch_csv(csv_df_mission_column_file))
        assert '"uid" not found' in str(re.value)

    def test_same_uids(self, csv_df_same_uids_file):
        results = list(validate_batch_csv(csv_df_same_uids_file))
        assert len(results) == 3
        assert results[1].findings.height == 2
        assert results[1].findings.select(pl.col('validation_id').eq('E3000').all()).item()
        assert results[1].phase == ValidationPhase.LOGICAL
