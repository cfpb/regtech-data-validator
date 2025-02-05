"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

import logging
from pathlib import Path
from typing import Dict, List
import polars as pl
import pandera.polars as pa
from pandera import Check
from pandera.errors import SchemaErrors, SchemaError, SchemaErrorReason

from regtech_data_validator.checks import SBLCheck, Severity

from regtech_data_validator.validation_results import ValidationPhase, Counts, ValidationResults
from regtech_data_validator.data_formatters import format_findings

from regtech_data_validator.phase_validations import (
    get_phase_1_schema_for_lei,
    get_phase_2_schema_for_lei,
    get_register_schema,
)

log = logging.getLogger(__name__)


# Gets all associated field names from the check
def _get_check_fields(check: Check, primary_column: str) -> list[str]:

    field_list = [primary_column]
    if "related_fields" in check._check_kwargs:
        related_fields = check._check_kwargs["related_fields"]
        if related_fields:
            # related_fields can be a single str or list of str
            if isinstance(related_fields, str):
                field_list.append(related_fields)
            else:
                field_list.extend(related_fields)
    # remove possible dupes but maintain order
    field_list = list(dict.fromkeys(field_list))
    return field_list


# Retrieves the row data from the original dataframe that threw errors/warnings, and pulls out the fields/values
# from the original row data that caused the error/warning
def _filter_valid_records(df: pl.DataFrame, check_output: pl.Series, fields: list[str]) -> pl.DataFrame:
    sorted_check_output = check_output["index"]
    fields = ["index"] + fields
    filtered_df = df.filter(pl.col('index').is_in(sorted_check_output))
    failed_records_df = filtered_df[fields]
    # record_no is indexed by 1 instead of 0, so offset and drop index since it's no longer needed
    failed_records_df = failed_records_df.with_columns((pl.col("index") + 1).alias("record_no"))
    failed_records_df = failed_records_df.drop("index")
    return failed_records_df


def _records_to_fields(failed_records_df: pl.DataFrame) -> pl.DataFrame:
    # Unpivot the DataFrame with columns per Check field to DataFrame with a row per field
    failed_record_fields_df = failed_records_df.unpivot(
        variable_name='field_name',
        value_name='field_value',
        index=['record_no'],
    )
    return failed_record_fields_df


def _add_validation_metadata(failed_check_fields_df: pl.DataFrame, check: SBLCheck):
    # add the error/warning code from the check to the error dataframe
    validation_fields_df = failed_check_fields_df.with_columns(pl.lit(check.title).alias("validation_id"))
    return validation_fields_df


def validate(
    schema: pa.DataFrameSchema, submission_df: pl.LazyFrame, row_start: int, process_errors: bool
) -> pl.DataFrame:
    """
    validate received dataframe with schema and return list of
    schema errors
    Args:
        schema (DataFrameSchema): schema to be used for validation
        submission_df (pl.DataFrame): data to be validated against the schema
    Returns:
        pd.DataFrame containing validation results data
    """
    findings_df: pl.DataFrame = pl.DataFrame()

    try:
        # since polars dataframes don't normally have an index column, add it, so that we can match
        # up original submission rows with rows found with errors/warnings
        submission_df = submission_df.with_row_index(offset=row_start)
        schema(submission_df, lazy=True)
    except SchemaErrors as err:
        check_findings = []
        # NOTE: `type: ignore` because SchemaErrors.schema_errors is supposed to be
        #       `list[dict[str,Any]]`, but it's actually of type `SchemaError`
        schema_error: SchemaError

        # if process_errors:
        for schema_error in err.schema_errors:
            check = schema_error.check
            column_name = schema_error.schema.name

            # CHECK_ERROR is thrown by pandera polars if the check itself has a coding error, NOT if the check data results in an error
            if (
                schema_error.reason_code is SchemaErrorReason.CHECK_ERROR
                or schema_error.reason_code is SchemaErrorReason.COLUMN_NOT_IN_DATAFRAME
            ):
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
            check_output = gather_errors(schema_error.check_output)

            if check_output is not None:
                # Filter data not associated with failed Check, and update index for merging with findings_df
                check_output = check_output.with_columns(pl.col('index').add(row_start))
                if process_errors:
                    failed_records_df = _filter_valid_records(submission_df, check_output, fields)
                    failed_record_fields_df = _records_to_fields(failed_records_df)
                    findings = _add_validation_metadata(failed_record_fields_df, check)
                else:
                    findings = _add_validation_metadata(check_output, check)
                    findings = findings.with_columns(
                        pl.lit(check.scope).alias("scope"), pl.lit(check.severity.value).alias("validation_type")
                    )
                check_findings.append(findings)
            else:
                # The above exception handling _should_ prevent this from ever happenin, but...just in case.
                raise RuntimeError(f'No check output for "{check.name}" check.  Pandera SchemaError: {schema_error}')
        if check_findings:
            findings_df = pl.concat(check_findings)

    return add_uid(findings_df, submission_df, row_start) if process_errors else findings_df


# Add the uid for the record throwing the error/warning to the error dataframe
def add_uid(results_df: pl.DataFrame, submission_df: pl.DataFrame, offset: int) -> pl.DataFrame:
    if results_df.is_empty():
        return results_df

    uid_records = results_df['record_no'] - 1 - offset
    results_df = results_df.with_columns(submission_df['uid'].gather(uid_records).alias('uid'))
    return results_df


# This function is a Generator, and will yield the results of each batch of processing, along with the
# phase (SYNTACTICAL/LOGICAL) that the findings were found.  Callers of this function will want to
# store or concat each iteration of findings
def validate_data(
    source: Path | str | pl.LazyFrame,
    context: dict[str, str] | None = None,
    batch_size: int = 50000,
    batch_count: int = 1,
    max_errors=1000000,
):
    has_syntax_errors = False
    syntax_schema = get_phase_1_schema_for_lei(context)
    syntax_checks = [check for col_schema in syntax_schema.columns.values() for check in col_schema.checks]

    logic_schema = get_phase_2_schema_for_lei(context)
    logic_checks = [check for col_schema in logic_schema.columns.values() for check in col_schema.checks]

    all_uids = []

    batch_validation = validate_lazy_chunks if isinstance(source, pl.LazyFrame) else validate_chunks

    for validation_results, uids in batch_validation(
        syntax_schema, source, batch_size, batch_count, max_errors, syntax_checks
    ):
        all_uids.extend(uids)
        # validate, and therefore validate_chunks, can return an empty dataframe for findings
        if not validation_results.findings.is_empty():
            has_syntax_errors = True
        yield validation_results

    if not has_syntax_errors:
        yield validate_register_level(context, all_uids)

        for validation_results, _ in batch_validation(
            logic_schema, source, batch_size, batch_count, max_errors, logic_checks
        ):
            yield validation_results


def validate_batch_csv(
    path: Path | str,
    context: dict[str, str] | None = None,
    batch_size: int = 50000,
    batch_count: int = 1,
    max_errors=1000000,
):
    for results in validate_data(path, context, batch_size, batch_count, max_errors):
        yield results


def validate_lazy_frame(
    lf: pl.LazyFrame,
    context: dict[str, str] | None = None,
    batch_size: int = 50000,
    batch_count: int = 1,
    max_errors=1000000,
):
    for results in validate_data(lf, context, batch_size, batch_count, max_errors):
        yield results


# Reads in a path to a csv in batches, using batch_size to determine number of rows to read into the buffer,
# and batch_count to determine how many batches to process in parallel.  Performance testing for large files
# shows 50K batch_size with 1 batch_count to be a nice balance of speed and resource utilization.  Increasing
# these increases resource utilization but increases speed (especially batch_count).  Reducing these, espectially
# batch_count adds processing cylces (time) but can significantly reduce resources.
def validate_chunks(schema, path, batch_size, batch_count, max_errors, checks):
    reader = pl.read_csv_batched(path, infer_schema_length=0, missing_utf8_is_empty_string=True, batch_size=batch_size)
    process_errors = True
    total_count = 0
    row_start = 0
    batches = reader.next_batches(batch_count)
    while batches:
        df = pl.concat(batches)
        validation_results, total_count, process_errors = validate_chunk(
            schema, df, total_count, row_start, max_errors, process_errors, checks
        )
        row_start += df.height
        yield validation_results, df["uid"].to_list()
        batches = reader.next_batches(batch_count)


def validate_lazy_chunks(schema, lf: pl.LazyFrame, batch_size: int, batch_count, max_errors, checks):
    process_errors = True
    total_count = 0
    row_start = 0
    df = lf.slice(row_start, batch_size).collect()
    while df.height:
        validation_results, total_count, process_errors = validate_chunk(
            schema, df, total_count, row_start, max_errors, process_errors, checks
        )
        row_start += df.height
        yield validation_results, df["uid"].to_list()
        df = lf.slice(row_start, batch_size).collect()


def validate_chunk(schema, df: pl.DataFrame, total_count, row_start, max_errors, process_errors, checks):
    log.debug("Start UID: %s, Last UID: %s", df['uid'][0], df['uid'][-1])
    validation_results = validate(schema, df, row_start, process_errors)
    if process_errors and not validation_results.is_empty():
        validation_results = format_findings(validation_results, schema.name.value, checks)

    error_counts, warning_counts = get_scope_counts(validation_results)
    results = ValidationResults(
        record_count=df.height,
        error_counts=error_counts,
        warning_counts=warning_counts,
        is_valid=((error_counts.total_count + warning_counts.total_count) == 0),
        findings=validation_results if process_errors else pl.DataFrame(),
        phase=schema.name,
    )

    total_count += error_counts.total_count + warning_counts.total_count
    log.debug("Counts: %d %d", error_counts, warning_counts)
    if total_count > max_errors and process_errors:
        log.debug("Reached max errors, adjusting results")
        process_errors = False
        head_count = results.findings.height - (total_count - max_errors)
        log.debug(
            "Results height: %d, total count: %d, head count: %d", results.findings.height, total_count, head_count
        )
        results.findings = results.findings.head(head_count)
        log.debug("Results height after heading %d", results.findings.height)

    return results, total_count, process_errors


def validate_register_level(context: Dict[str, str] | None, all_uids: List[str]):
    log.debug("Processing register logic errors")
    register_schema = get_register_schema(context)
    validation_results = validate(register_schema, pl.DataFrame({"uid": all_uids}), 0, True)
    if not validation_results.is_empty():
        validation_results = format_findings(
            validation_results,
            ValidationPhase.LOGICAL.value,
            [check for col_schema in register_schema.columns.values() for check in col_schema.checks],
        )
    error_counts, warning_counts = get_scope_counts(validation_results)
    results = ValidationResults(
        error_counts=error_counts,
        warning_counts=warning_counts,
        is_valid=((error_counts.total_count + warning_counts.total_count) == 0),
        findings=validation_results,
        phase=register_schema.name,
    )
    log.debug("Register counts: %d %d", error_counts, warning_counts)
    return results


# This function adds an index column (polars dataframes do not normally have one), and filters out
# any row that did not fail a check.
def gather_errors(check_output: pl.DataFrame):
    return check_output.with_row_index().filter(~pl.col("check_output"))


def get_scope_counts(error_frame: pl.DataFrame):
    if not error_frame.is_empty():
        single_errors = error_frame.filter(
            (pl.col("validation_type") == Severity.ERROR) & (pl.col("scope") == "single-field")
        ).height
        single_warnings = error_frame.filter(
            (pl.col("validation_type") == Severity.WARNING) & (pl.col("scope") == "single-field")
        ).height
        register_errors = error_frame.filter(
            (pl.col("validation_type") == Severity.ERROR) & (pl.col("scope") == "register")
        ).height
        multi_errors = error_frame.filter(
            (pl.col("validation_type") == Severity.ERROR) & (pl.col("scope") == "multi-field")
        ).height
        multi_warnings = error_frame.filter(
            (pl.col("validation_type") == Severity.WARNING) & (pl.col("scope") == "multi-field")
        ).height

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

    else:
        return Counts(), Counts()
