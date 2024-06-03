"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

import math
import pandas as pd
from pandera import Check, DataFrameSchema
from pandera.errors import SchemaErrors, SchemaError, SchemaErrorReason

from regtech_data_validator.checks import SBLCheck
from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei
from regtech_data_validator.schema_template import get_template
from regtech_data_validator.validation_results import ValidationPhase, ValidationResults

PHASE_1 = "phase_1"
PHASE_2 = "phase_2"

# Get separate schema templates for phase 1 and 2
phase_1_template = get_template()
phase_2_template = get_template()


def get_schema_by_phase_for_lei(template: dict, phase: str, context: dict[str, str] | None = None):
    for column in get_phase_1_and_2_validations_for_lei(context):
        validations = get_phase_1_and_2_validations_for_lei(context)[column]
        template[column].checks = validations[phase]

    return DataFrameSchema(template, name=phase)


def get_phase_1_schema_for_lei(context: dict[str, str] | None = None):
    return get_schema_by_phase_for_lei(phase_1_template, PHASE_1, context)


def get_phase_2_schema_for_lei(context: dict[str, str] | None = None):
    return get_schema_by_phase_for_lei(phase_2_template, PHASE_2, context)


def _get_check_fields(check: Check, primary_column: str) -> list[str]:
    """
    Don't sort field list to maintain original ordering.  Use List as
    python Set does not guarantee order.
    """

    field_list = [primary_column]

    if check.groupby:
        field_list += check.groupby
    # remove possible dupes but maintain order
    field_list = list(dict.fromkeys(field_list))
    return field_list


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
    sorted_fields = df.loc[sorted_check_output[~sorted_check_output].index][fields]
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
    validation_fields_df = failed_check_fields_df.assign(validation_id=check.title)
    return validation_fields_df


def validate(schema: DataFrameSchema, submission_df: pd.DataFrame, max_errors: int = 1000000) -> ValidationResults:
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
    single_field = multi_field = register = 0

    try:
        schema(submission_df, lazy=True)
    except SchemaErrors as err:
        is_valid = False
        check_findings = []
        # NOTE: `type: ignore` because SchemaErrors.schema_errors is supposed to be
        #       `list[dict[str,Any]]`, but it's actually of type `SchemaError`
        schema_error: SchemaError
        single_field, multi_field, register = get_scope_counts(err.schema_errors)
        total_error_count = sum([single_field, multi_field, register])
        if total_error_count > max_errors:
            err.schema_errors = trim_down_errors(err.schema_errors, max_errors)
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
                check_findings.append(_add_validation_metadata(failed_record_fields_df, check))
            else:
                # The above exception handling _should_ prevent this from ever happenin, but...just in case.
                raise RuntimeError(f'No check output for "{check.name}" check.  Pandera SchemaError: {schema_error}')
        findings_df = pd.concat(check_findings)

    updated_df = add_uid(findings_df, submission_df)
    results = ValidationResults(
        single_field_count=single_field,
        multi_field_count=multi_field,
        register_count=register,
        is_valid=is_valid,
        findings=updated_df,
        phase=ValidationPhase.SYNTACTICAL.value if schema.name == PHASE_1 else ValidationPhase.LOGICAL.value,
    )
    return results


def add_uid(results_df: pd.DataFrame, submission_df: pd.DataFrame) -> pd.DataFrame:
    if results_df.empty:
        return results_df

    # uses pandas column operation to get list of record_no - 1 values, which would be indexes in the submission, since
    # record_no is index offset by 1, and the uid column values for that into a new series that is then
    # assigned to the results uid column.  Much simpler and faster than looping over and assigning row by row.

    results_df['uid'] = submission_df.loc[results_df['record_no'] - 1, 'uid'].values
    return results_df


def validate_phases(
    df: pd.DataFrame, context: dict[str, str] | None = None, max_errors: int = 1000000
) -> ValidationResults:

    results = validate(get_phase_1_schema_for_lei(context), df, max_errors)

    if not results.is_valid:
        return results

    return validate(get_phase_2_schema_for_lei(context), df, max_errors)


def get_scope_counts(schema_errors: list[SchemaError]):
    single = [
        (~error.check_output).sum()
        for error in schema_errors
        if isinstance(error.check, SBLCheck) and error.check.scope == 'single-field'
    ]
    multi = [
        (~error.check_output).sum()
        for error in schema_errors
        if isinstance(error.check, SBLCheck) and error.check.scope == 'multi-field'
    ]
    register = [
        (~error.check_output).sum()
        for error in schema_errors
        if isinstance(error.check, SBLCheck) and error.check.scope == 'register'
    ]
    return sum(single), sum(multi), sum(register)


def trim_down_errors(schema_errors: list[SchemaError], max_errors: int):
    error_counts = [sum(~error.check_output) for error in schema_errors]
    total_error_count = sum(error_counts)

    # Take the list of counts per error to determine a ratio for each,
    # relative to the total number of errors, and use that ratio in
    # relation to the max error count to determine a total count for that error
    # use a max so that we always have at least 1 (for really small ratios)
    error_ratios = [(count / total_error_count) for count in error_counts]
    new_counts = [math.ceil(max_errors * prop) for prop in error_ratios]

    # Adjust the counts in case we went over max.  This is very likely since we're using
    # ceil, unless we have an exact equality of the new counts.  Because of the use
    # of ceil, we will never have the sum of the new counts be less than max.
    if sum(new_counts) > max_errors:
        while sum(new_counts) > max_errors:
            # arbitrary reversal to contain errors in FIG order, if we need to remove
            # errors to fit max
            for i in reversed(range(len(new_counts))):
                if new_counts[i] > 1:
                    new_counts[i] -= 1
                # check if all the counts are equal to 1, then
                # start removing those until we hit max
                elif new_counts[i] == 1 and sum(new_counts) <= len(new_counts):
                    new_counts[i] -= 1
                if sum(new_counts) == max_errors:
                    break

    for error, new_count in zip(schema_errors, new_counts):
        error_indices = error.check_output[~error.check_output].index
        keep_indices = error_indices[:new_count]
        error.check_output = error.check_output.loc[keep_indices]
    return schema_errors
