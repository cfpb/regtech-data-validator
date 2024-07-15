"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""
import cProfile
import pstats

from copy import deepcopy
import math
import pandas as pd
import psutil
from pathlib import Path
import polars as pl
import pandera.polars as pa
from pandera import Check, DataFrameSchema
from pandera.errors import SchemaErrors, SchemaError, SchemaErrorReason

from regtech_data_validator.checks import SBLCheck, Severity
from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei, get_phase_2_register_validations
from regtech_data_validator.schema_template import get_template, get_register_template
from regtech_data_validator.validation_results import ValidationPhase, ValidationResults, Counts

# Get separate schema templates for phase 1 and 2
phase_1_template = get_template()
phase_2_template = get_template()
register_template = get_register_template()


def get_schema_by_phase_for_lei(template: dict, phase: str, context: dict[str, str] | None = None):
    for column in get_phase_1_and_2_validations_for_lei(context):
        validations = get_phase_1_and_2_validations_for_lei(context)[column]
        template[column].checks = validations[phase]

    return pa.DataFrameSchema(template, name=phase)


def get_phase_1_schema_for_lei(context: dict[str, str] | None = None):
    return get_schema_by_phase_for_lei(phase_1_template, ValidationPhase.SYNTACTICAL, context)


def get_phase_2_schema_for_lei(context: dict[str, str] | None = None):
    return get_schema_by_phase_for_lei(phase_2_template, ValidationPhase.LOGICAL, context)

def get_register_checks(context: dict[str, str] | None = None):
    for column in get_phase_2_register_validations(context):
        validations = get_phase_2_register_validations(context)[column]
        register_template[column].checks = validations[ValidationPhase.LOGICAL]

    return pa.DataFrameSchema(register_template, name=ValidationPhase.LOGICAL)
    

def _get_check_fields(check: Check, primary_column: str) -> list[str]:
    """
    Don't sort field list to maintain original ordering.  Use List as
    python Set does not guarantee order.
    """

    field_list = [primary_column]
    if "groupby_fields" in check._check_kwargs:
        groupby_fields = check._check_kwargs["groupby_fields"]
        if groupby_fields:
            if isinstance(groupby_fields, str):
                field_list.append(groupby_fields)
            else:
                field_list.extend(groupby_fields)
    # remove possible dupes but maintain order
    field_list = list(dict.fromkeys(field_list))
    return field_list


def _filter_valid_records(df: pl.DataFrame, check_output: pl.Series, fields: list[str]) -> pl.DataFrame:
    """
    Return only records and fields associated with a given `Check`'s
    """

    # `check_output` must be sorted so its index lines up with `df`'s index
    
    sorted_check_output = check_output["check_output"]
    #sorted_check_output: pl.Series = check_output.sort_index()

    # Filter records using Pandas's boolean indexing, where all False values get filtered out.
    # The `~` does the inverse since it's actually the False values we want to keep.
    # http://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#boolean-indexing
    # We then up the index by 1 so that record_no is indexed starting with 1 instead of 0
    fields = ["index"] + fields
    filtered_df = df.filter(~sorted_check_output)
    failed_records_df = filtered_df[fields]
    failed_records_df = failed_records_df.with_columns((pl.col("index") + 1).alias("record_no"))
    failed_records_df = failed_records_df.drop("index")
    failed_records_df = failed_records_df.with_row_index(name='finding_no')
    return failed_records_df


def _records_to_fields(failed_records_df: pl.DataFrame) -> pl.DataFrame:
    """
    Transforms a DataFrame with columns per Check field to DataFrame with a row per field
    """

    # Melts a DataFrame with the line number as the index columns for the validations's fields' values
    # into one with the validation_id, record_no, and field_name as a multiindex, and all of the validation
    # metadata merged in as well.
    failed_record_fields_df = failed_records_df.melt(
        variable_name='field_name', value_name='field_value', id_vars=['record_no', 'finding_no']
    )
    return failed_record_fields_df


def _add_validation_metadata(failed_check_fields_df: pl.DataFrame, check: SBLCheck):
    validation_fields_df = failed_check_fields_df.with_columns(pl.lit(check.title).alias("validation_id"))
    return validation_fields_df


def validate(schema: pa.DataFrameSchema, submission_df: pl.LazyFrame, max_errors: int = 1000000) -> ValidationResults:
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
    from datetime import datetime
    is_valid = True
    findings_df: pl.DataFrame = pl.DataFrame()
    next_finding_no: int = 1
    error_counts = warning_counts = Counts()

    try:
        start = datetime.now()
        submission_df = submission_df.with_row_count("index")
        schema(submission_df, lazy=True)
        #print(f"Validation of {schema.name} took {(datetime.now() - start).total_seconds()} seconds")
    except SchemaErrors as err:
        #print(f"Validation of {schema.name} took {(datetime.now() - start).total_seconds()} seconds")
        start = datetime.now()
        is_valid = False
        check_findings = []
        # NOTE: `type: ignore` because SchemaErrors.schema_errors is supposed to be
        #       `list[dict[str,Any]]`, but it's actually of type `SchemaError`
        schema_error: SchemaError
        
        error_counts, warning_counts = get_scope_counts(err.schema_errors)
        total_error_count = sum([error_counts.total_count, warning_counts.total_count])
        #print(f"Total Error Count: {total_error_count}")
        #if total_error_count > max_errors:
        #    err.schema_errors = trim_down_errors(err.schema_errors, max_errors)
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
            check_output: pl.Series | None = schema_error.check_output

            if check_output is not None:
                # Filter data not associated with failed Check, and update index for merging with findings_df
                failed_records_df = _filter_valid_records(submission_df, check_output, fields)
                failed_records_df = failed_records_df.with_columns((pl.col("finding_no") + next_finding_no).alias("finding_no"))
                next_finding_no = failed_records_df.tail(1)["finding_no"] + 1  # type: ignore
                failed_record_fields_df = _records_to_fields(failed_records_df)
                check_findings.append(_add_validation_metadata(failed_record_fields_df, check))
            else:
                # The above exception handling _should_ prevent this from ever happenin, but...just in case.
                raise RuntimeError(f'No check output for "{check.name}" check.  Pandera SchemaError: {schema_error}')
        findings_df = pl.concat(check_findings)
        findings_df = findings_df.sort("finding_no")

    updated_df = add_uid(findings_df, submission_df)
    results = ValidationResults(
        error_counts=error_counts,
        warning_counts=warning_counts,
        is_valid=is_valid,
        findings=updated_df,
        phase=schema.name,
    )
    #print(f"Processing of {schema.name} errors took {(datetime.now() - start).total_seconds()} seconds")
    return results


def add_uid(results_df: pl.DataFrame, submission_df: pl.DataFrame) -> pl.DataFrame:
    if results_df.is_empty:
        return results_df

    # uses pandas column operation to get list of record_no - 1 values, which would be indexes in the submission, since
    # record_no is index offset by 1, and the uid column values for that into a new series that is then
    # assigned to the results uid column.  Much simpler and faster than looping over and assigning row by row.

    results_df['uid'] = submission_df.loc[results_df['record_no'] - 1, 'uid'].values
    return results_df

#def validate_phases(
#    df: pl.DataFrame, context: dict[str, str] | None = None, max_errors: int = 1000000
#) -> ValidationResults:
def validate_phases(
    path: Path, context: dict[str, str] | None = None, max_errors: int = 1000000
) -> ValidationResults:
    syntax_results = []
    logic_results = []
    #NO BATCH
    '''
    df = pl.read_csv(path, infer_schema_length=0, missing_utf8_is_empty_string=True)
    results = validate(get_phase_1_schema_for_lei(context), df, max_errors)

    if not results.is_valid:
        return results

    results = validate(get_phase_2_schema_for_lei(context), df, max_errors)
    return results
    
    
    '''
    #SCAN
    lf = pl.scan_csv(path, infer_schema_length=0, missing_utf8_is_empty_string=True)
    all_checks = get_phase_1_and_2_validations_for_lei(context)
    for column in all_checks:
        col = all_checks[column]
        template = {column: phase_1_template[column]}
        template[column].checks = col[ValidationPhase.SYNTACTICAL]
        results = validate(pa.DataFrameSchema(template, name=ValidationPhase.SYNTACTICAL), lf.select(column).collect())
        if not results.is_valid:
            syntax_results.append(results)
            
    if not syntax_results:
        for column in all_checks:
            col = all_checks[column]
            all_column_checks =col[ValidationPhase.LOGICAL]
            cols = [column]
            for check in all_column_checks:
                if "groupby_fields" in check._check_kwargs:
                    group_columns = check._check_kwargs["groupby_fields"]
                    cols = cols + ([group_columns] if isinstance(group_columns, str) else group_columns)
            template = {c: deepcopy(phase_2_template[c]) for c in cols}
            template[column].checks = all_column_checks
            results = validate(pa.DataFrameSchema(template, name=ValidationPhase.LOGICAL), lf.select(set(cols)).collect())
            if not results.is_valid:
                logic_results.append(results)
    #BATCH
    '''
    batch_reader = pl.read_csv_batched(path, infer_schema_length=0, missing_utf8_is_empty_string=True, batch_size=100000)
    batches = batch_reader.next_batches(100)
    
    while batches:
        for df in batches:
            results = validate(get_phase_1_schema_for_lei(context), df)
            if not results.is_valid:
                syntax_results.append(results)
            
            if not syntax_results:
                logic_results.append(validate(get_phase_2_schema_for_lei(context), df, max_errors))
        batches = batch_reader.next_batches(100)
    '''
    register_results = ValidationResults(error_counts=Counts(), warning_counts=Counts(), is_valid=False, findings=pl.DataFrame(), phase=ValidationPhase.LOGICAL)
    if not syntax_results:
        uids = pl.scan_csv(path, infer_schema_length=0, missing_utf8_is_empty_string=True).select("uid").collect()
        register_results = validate(get_register_checks(context), uids, max_errors)
    
    final_results = syntax_results if syntax_results else logic_results
    single_errors = []
    multi_errors = []
    single_warns = []
    multi_warns = []
    total_errors = []
    total_warns = []
    findings = []
    valids = []
    
    for lr in final_results:
        single_errors.append(lr.error_counts.single_field_count)
        multi_errors.append(lr.error_counts.multi_field_count)
        single_warns.append(lr.warning_counts.single_field_count)
        multi_warns.append(lr.warning_counts.multi_field_count)
        total_errors.append(lr.error_counts.total_count)
        total_warns.append(lr.warning_counts.total_count)
        findings.append(lr.findings)
        valids.append(lr.is_valid)
    if not register_results.findings.is_empty:
        findings.append(register_results.findings)
    valids.append(register_results.is_valid)
    vr = ValidationResults(
        error_counts=Counts(single_field_count=sum(single_errors), multi_field_count=sum(multi_errors), register_count=register_results.error_counts.register_count, total_count=(sum(total_errors) + register_results.error_counts.total_count)),
        warning_counts=Counts(single_field_count=sum(single_warns), multi_field_count=sum(multi_warns), register_count=0, total_count=sum(total_warns)),
        findings=pl.concat(findings),
        is_valid=all(valids),
        phase=final_results[0].phase
    )
    return vr

def get_scope_counts(schema_errors: list[SchemaError]):
    singles = [
        error for error in schema_errors if isinstance(error.check, SBLCheck) and error.check.scope == 'single-field'
    ]
    single_errors = sum([(~error.check_output["check_output"]).sum()for error in singles if error.check.severity == Severity.ERROR])
    single_warnings = sum(
        [(~error.check_output["check_output"]).sum() for error in singles if error.check.severity == Severity.WARNING]
    )
    multi = [
        error for error in schema_errors if isinstance(error.check, SBLCheck) and error.check.scope == 'multi-field'
    ]
    multi_errors = sum([(~error.check_output["check_output"]).sum() for error in multi if error.check.severity == Severity.ERROR])
    multi_warnings = sum([(~error.check_output["check_output"]).sum() for error in multi if error.check.severity == Severity.WARNING])
    register_errors = sum(
        [
            (~error.check_output["check_output"]).sum()
            for error in schema_errors
            if isinstance(error.check, SBLCheck) and error.check.scope == 'register'
        ]
    )
    return Counts(
        single_field_count=single_errors,
        multi_field_count=multi_errors,
        register_count=register_errors,
        total_count=sum([single_errors, multi_errors, register_errors]),
    ), Counts(
        single_field_count=single_warnings,
        multi_field_count=multi_warnings,
        total_count=sum([single_warnings, multi_warnings]),  # There are no register-level warnings at this time
    )


def trim_down_errors(schema_errors: list[SchemaError], max_errors: int):
    error_counts = [sum(~(error.check_output["check_output"])) for error in schema_errors]
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
        error.check_output = error.check_output.with_row_count("index")
        error_indices = error.check_output.filter(~pl.col("check_output"))["index"].to_list()
        print(f"Error Indices: {error_indices}")
        keep_indices = error_indices[:new_count]
        error.check_output = error.check_output.filter(pl.col("index").is_in(keep_indices))
    return schema_errors
