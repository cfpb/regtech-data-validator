"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

import pandas as pd
from pandera import Check, DataFrameSchema
from pandera.errors import SchemaErrors, SchemaError, SchemaErrorReason

from regtech_data_validator.checks import SBLCheck
from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei, PHASE_1_TYPE, PHASE_2_TYPE
from regtech_data_validator.schema_template import get_template


# Get separate schema templates for phase 1 and 2
phase_1_template = get_template()
phase_2_template = get_template()


def get_schema_by_phase_for_lei(template: dict, phase: str, context: dict[str, str] | None = None):
    for column in get_phase_1_and_2_validations_for_lei(context):
        validations = get_phase_1_and_2_validations_for_lei(context)[column]
        template[column].checks = validations[phase]

    return DataFrameSchema(template)


def get_phase_1_schema_for_lei(context: dict[str, str] | None = None):
    return get_schema_by_phase_for_lei(phase_1_template, "phase_1", context)


def get_phase_2_schema_for_lei(context: dict[str, str] | None = None):
    return get_schema_by_phase_for_lei(phase_2_template, "phase_2", context)


def _get_check_fields(check: Check, primary_column: str) -> list[str]:
    """
    Retrieves unique sorted list of fields associated with a given Check
    """

    field_set: set[str] = {primary_column}

    if check.groupby:
        field_set.update(check.groupby)  # type: ignore

    fields = sorted(list(field_set))

    return fields


def _filter_valid_records(df: pd.DataFrame, check_output: pd.Series, fields: list[str]) -> pd.DataFrame:
    """
    Return only records and fields associated with a given `Check`'s
    """

    # `check_output` must be sorted so its index lines up with `df`'s index
    sorted_check_output: pd.Series = check_output.sort_index()

    # Filter records using Pandas's boolean indexing, where all False values get filtered out.
    # The `~` does the inverse since it's actually the False values we want to keep.
    # http://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#boolean-indexing
    # We then up the index by 1 so that record_no is indexed starting with 1 instead of 0
    sorted_fields = df[~sorted_check_output][fields]
    index = [i + 1 for i in sorted_fields.index]
    sorted_fields.index = index
    failed_records_df = sorted_fields.reset_index(names='record_no')

    failed_records_df.index.rename('finding_no', inplace=True)

    return failed_records_df


def _records_to_fields(failed_records_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms a DataFrame with columns per Check field to DataFrame with a row per field
    """

    # Melts a DataFrame with the line number as the index columns for the validations's fields' values
    # into one with the validation_id, record_no, and field_name as a multiindex, and all of the validation
    # metadata merged in as well.
    failed_record_fields_df = failed_records_df.melt(
        var_name='field_name', value_name='field_value', id_vars='record_no', ignore_index=False
    )

    return failed_record_fields_df


def _add_validation_metadata(failed_check_fields_df: pd.DataFrame, check: SBLCheck):
    """
    Add SBLCheck metadata (id, name, description, severity)
    """

    validation_fields_df = (
        failed_check_fields_df.assign(validation_severity=check.severity)
        .assign(fig_link=check.fig_link)
        .assign(validation_id=check.title)
        .assign(validation_name=check.name)
        .assign(validation_desc=check.description)
    )

    return validation_fields_df


def validate(schema: DataFrameSchema, submission_df: pd.DataFrame) -> tuple[bool, pd.DataFrame]:
    """
    validate received dataframe with schema and return list of
    schema errors
    Args:
        schema (DataFrameSchema): schema to be used for validation
        submission_df (pd.DataFrame): data to be validated against the schema
    Returns:
        bool whether the given submission was valid or not
        pd.DataFrame containing validation results data
    """
    is_valid = True
    findings_df: pd.DataFrame = pd.DataFrame()
    next_finding_no: int = 1

    try:
        schema(submission_df, lazy=True)
    except SchemaErrors as err:
        is_valid = False

        # NOTE: `type: ignore` because SchemaErrors.schema_errors is supposed to be
        #       `list[dict[str,Any]]`, but it's actually of type `SchemaError`
        schema_error: SchemaError
        for schema_error in err.schema_errors:  # type: ignore
            check = schema_error.check
            column_name = schema_error.schema.name

            if schema_error.reason_code == SchemaErrorReason.COLUMN_NOT_IN_DATAFRAME:
                raise RuntimeError(schema_error) from schema_error
            if not check:
                raise RuntimeError(
                    f'SchemaError occurred with no associated Check for {column_name} column'
                ) from schema_error

            if not isinstance(check, SBLCheck):
                raise RuntimeError(
                    f'Check {check} type on {column_name} column not supported. Must be of type {SBLCheck}'
                ) from schema_error

            fields = _get_check_fields(check, column_name)

            check_output: pd.Series | None = schema_error.check_output

            if check_output is not None:
                # Filter data not associated with failed Check, and update index for merging with findings_df
                failed_records_df = _filter_valid_records(submission_df, check_output, fields)
                failed_records_df.index += next_finding_no
                next_finding_no = failed_records_df.tail(1).index + 1  # type: ignore

                failed_record_fields_df = _records_to_fields(failed_records_df)
                check_findings_df = _add_validation_metadata(failed_record_fields_df, check)

                findings_df = pd.concat([findings_df, check_findings_df])
            else:
                # The above exception handling _should_ prevent this from ever happenin, but...just in case.
                raise RuntimeError(f'No check output for "{check.name}" check.  Pandera SchemaError: {schema_error}')

    updated_df = add_uid(findings_df.sort_index(), submission_df)

    return is_valid, updated_df


def add_uid(results_df: pd.DataFrame, submission_df: pd.DataFrame) -> pd.DataFrame:
    if results_df.empty:
        return results_df
    all_uids = []
    sub_uids = submission_df['uid'].tolist()
    for index, row in results_df.iterrows():
        all_uids.append(sub_uids[int(row['record_no']) - 1])

    results_df.insert(1, "uid", all_uids, True)
    return results_df


def validate_phases(df: pd.DataFrame, context: dict[str, str] | None = None) -> tuple[bool, pd.DataFrame]:
    p1_is_valid, p1_findings = validate(get_phase_1_schema_for_lei(context), df)

    if not p1_is_valid:
        p1_findings.insert(1, "validation_phase", PHASE_1_TYPE, True)
        return p1_is_valid, p1_findings, PHASE_1_TYPE

    p2_is_valid, p2_findings = validate(get_phase_2_schema_for_lei(context), df)
    if not p2_is_valid:
        p2_findings.insert(1, "validation_phase", PHASE_2_TYPE, True)
    return p2_is_valid, p2_findings, PHASE_2_TYPE
