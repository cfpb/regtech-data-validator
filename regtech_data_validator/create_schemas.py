"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

import pandas as pd
from pandera import DataFrameSchema
from pandera.errors import SchemaErrors, SchemaError

from regtech_data_validator.checks import SBLCheck
from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei
from regtech_data_validator.schema_template import get_template


# Get separate schema templates for phase 1 and 2


phase_1_template = get_template()
phase_2_template = get_template()


def get_schema_by_phase_for_lei(template: dict, phase: str, lei: str | None = None):
    for column in get_phase_1_and_2_validations_for_lei(lei):
        validations = get_phase_1_and_2_validations_for_lei(lei)[column]
        template[column].checks = validations[phase]
    return DataFrameSchema(template)


def get_phase_1_schema_for_lei(lei: str | None = None):
    return get_schema_by_phase_for_lei(phase_1_template, "phase_1", lei)


def get_phase_2_schema_for_lei(lei: str | None = None):
    return get_schema_by_phase_for_lei(phase_2_template, "phase_2", lei)


def validate(schema: DataFrameSchema, df: pd.DataFrame) -> pd.DataFrame:
    """
    validate received dataframe with schema and return list of
    schema errors
    Args:
        schema (DataFrameSchema): schema to be used for validation
        df (pd.DataFrame): data parsed into dataframe
    Returns:
        pd.DataFrame containing validation results data
    """
    findings_df: pd.DataFrame = pd.DataFrame()

    try:
        schema(df, lazy=True)
    except SchemaErrors as err:
        # WARN: SchemaErrors.schema_errors is supposed to be of type
        #       list[dict[str,Any]], but it's actually of type SchemaError
        schema_error: SchemaError
        for schema_error in err.schema_errors:  # type: ignore
            check = schema_error.check
            column_name = schema_error.schema.name

            if not check:
                raise RuntimeError(
                    f'SchemaError occurred with no associated Check for {column_name} column'
                ) from schema_error

            if not isinstance(check, SBLCheck):
                raise RuntimeError(
                    f'Check {check} type on {column_name} column not supported. Must be of type {SBLCheck}'
                ) from schema_error

            fields: list[str] = [column_name]

            if check.groupby:
                fields += check.groupby  # type: ignore

            # This will either be a boolean series or a single bool
            # Q: Is the scenario where it returns a single bool even with the above error checking?
            check_output: pd.Series = schema_error.check_output  # type: ignore

            # Remove duplicates, but keep as `list` for JSON-friendliness
            fields = list(set(fields))

            # Q: What's the scenario where `check_output` is empty?
            if not check_output.empty:
                # `check_output` must be sorted so its index lines up with `df`'s index
                check_output.sort_index(inplace=True)

                # Filter records using Pandas's boolean indexing, where all False values
                # get filtered out. The `~` does the inverse since it's actually the
                # False values we want to keep.
                # http://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#boolean-indexing
                failed_check_fields_df = df[~check_output][fields].fillna("")

                # Melts a DataFrame with the line number as the index columns for the validations's fields' values
                # into one with the validation_id, line_no, and field_name as a multiindex, and all of the validation
                # metadata merged in as well.
                #
                # from...
                #
                #   ct_loan_term_flag ct_credit_product
                # 0               999                 1
                # 1               999                 2
                #
                # ...to...
                #                                 field_value  v_sev                                v_name                                            v_desc
                # v_id  line_no field_name
                # E2003 0       ct_credit_product           1  error  ct_loan_term_flag.enum_value_conflict  When 'credit product' equals 1 (term loan - un...
                #               ct_loan_term_flag         999  error  ct_loan_term_flag.enum_value_conflict  When 'credit product' equals 1 (term loan - un...
                #       1       ct_credit_product           2  error  ct_loan_term_flag.enum_value_conflict  When 'credit product' equals 1 (term loan - un...
                #               ct_loan_term_flag         999  error  ct_loan_term_flag.enum_value_conflict  When 'credit product' equals 1 (term loan - un...
                failed_check_fields_melt_df = (
                    failed_check_fields_df.reset_index(names='line_no')
                    .melt(var_name='field_name', value_name='field_value', id_vars='line_no')
                    .assign(v_id=check.title)
                    .assign(v_sev=check.severity)
                    .assign(v_name=check.name)
                    .assign(v_desc=check.description)
                    .set_index(['v_id', 'line_no', 'field_name'])
                    .sort_index
                )
                print(failed_check_fields_melt_df)

                findings_df = pd.concat([findings_df, failed_check_fields_melt_df])

    return findings_df


def validate_phases(df: pd.DataFrame, lei: str | None = None) -> list:
    phase1_findings = validate(get_phase_1_schema_for_lei(lei), df)
    if phase1_findings:
        return phase1_findings
    else:
        phase2_findings = validate(get_phase_2_schema_for_lei((lei)), df)
        if phase2_findings:
            return phase2_findings
        else:
            return [{"response": "No validations errors or warnings"}]
