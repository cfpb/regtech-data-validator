"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

from pathlib import Path
import polars as pl
import pandera.polars as pa
from pandera import Check
from pandera.errors import SchemaErrors, SchemaError, SchemaErrorReason

from regtech_data_validator.checks import SBLCheck
from regtech_data_validator.phase_validations import (
    get_phase_1_and_2_validations_for_lei,
    get_phase_2_register_validations,
)
from regtech_data_validator.schema_template import get_template, get_register_template
from regtech_data_validator.validation_results import ValidationPhase
from regtech_data_validator.data_formatters import format_findings

from fsspec import AbstractFileSystem, filesystem

import shutil
import os

from regtech_data_validator.phase_validations import (
    get_phase_1_schema_for_lei,
    get_phase_2_schema_for_lei,
    get_register_schema,
)

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
    # Melts the DataFrame with columns per Check field to DataFrame with a row per field
    failed_record_fields_df = failed_records_df.melt(
        variable_name='field_name', value_name='field_value', id_vars=['record_no']
    )
    return failed_record_fields_df


def _add_validation_metadata(failed_check_fields_df: pl.DataFrame, check: SBLCheck):
    # add the error/warning code from the check to the error dataframe
    validation_fields_df = failed_check_fields_df.with_columns(pl.lit(check.title).alias("validation_id"))
    return validation_fields_df


def validate(schema: pa.DataFrameSchema, submission_df: pl.LazyFrame) -> pl.DataFrame:
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
        submission_df = submission_df.with_row_index()
        schema(submission_df, lazy=True)
    except SchemaErrors as err:
        check_findings = []
        # NOTE: `type: ignore` because SchemaErrors.schema_errors is supposed to be
        #       `list[dict[str,Any]]`, but it's actually of type `SchemaError`
        schema_error: SchemaError

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

            schema_error = gather_errors(schema_error)

            fields = _get_check_fields(check, column_name)
            check_output: pl.Series | None = schema_error.check_output

            if check_output is not None:
                # Filter data not associated with failed Check, and update index for merging with findings_df
                failed_records_df = _filter_valid_records(submission_df, check_output, fields)
                failed_record_fields_df = _records_to_fields(failed_records_df)
                check_findings.append(_add_validation_metadata(failed_record_fields_df, check))
            else:
                # The above exception handling _should_ prevent this from ever happenin, but...just in case.
                raise RuntimeError(f'No check output for "{check.name}" check.  Pandera SchemaError: {schema_error}')
        if check_findings:
            findings_df = pl.concat(check_findings)

    updated_df = add_uid(findings_df, submission_df)
    return updated_df


# Add the uid for the record throwing the error/warning to the error dataframe
def add_uid(results_df: pl.DataFrame, submission_df: pl.DataFrame) -> pl.DataFrame:
    if results_df.is_empty():
        return results_df

    uid_records = results_df['record_no'] - 1
    results_df = results_df.with_columns(submission_df['uid'].gather(uid_records).alias('uid'))
    return results_df


# This function is a Generator, and will yield the results of each batch of processing, along with the
# phase (SYNTACTICAL/LOGICAL) that the findings were found.  Callers of this function will want to
# store or concat each iteration of findings
def validate_batch_csv(
    path: Path | str, context: dict[str, str] | None = None, batch_size: int = 50000, batch_count: int = 1
):
    has_syntax_errors = False
    real_path = get_real_file_path(path)
    # process the data first looking for syntax (phase 1) errors, then looking for logical (phase 2) errors/warnings
    syntax_schema = get_phase_1_schema_for_lei(context)
    syntax_checks = [check for col_schema in syntax_schema.columns.values() for check in col_schema.checks]

    logic_schema = get_phase_2_schema_for_lei(context)
    logic_checks = [check for col_schema in logic_schema.columns.values() for check in col_schema.checks]

    for findings in validate_chunks(syntax_schema, real_path, batch_size, batch_count):
        # validate, and therefore validate_chunks, can return an empty dataframe for findings
        if not findings.is_empty():
            has_syntax_errors = True
            rf = format_findings(findings,  ValidationPhase.SYNTACTICAL.value, syntax_checks)
            yield rf, ValidationPhase.SYNTACTICAL

    if not has_syntax_errors:
        # check for register-wide errors, like dupicate UIDs.  Use scan_csv as it is faster and less resource intensive
        # than reading in the whole csv and just selecting on the UID column (currently our only register level check data)
        uids = pl.scan_csv(real_path, infer_schema_length=0, missing_utf8_is_empty_string=True).select("uid").collect()
        register_schema = get_register_schema(context)
        findings = validate(register_schema, uids)
        if not findings.is_empty():
            rf = format_findings(
                findings, ValidationPhase.LOGICAL.value, [check for col_schema in register_schema.columns.values() for check in col_schema.checks]
            )
            yield rf, ValidationPhase.LOGICAL
        for findings in validate_chunks(logic_schema, real_path, batch_size, batch_count):
            # validate, and therefore validate_chunks, can return an empty dataframe for findings
            if not findings.is_empty():
                rf = format_findings(findings,  ValidationPhase.LOGICAL.value, logic_checks)
                yield rf, ValidationPhase.LOGICAL

    if os.path.isdir("/tmp/s3"):
        shutil.rmtree("/tmp/s3")


# Reads in a path to a csv in batches, using batch_size to determine number of rows to read into the buffer,
# and batch_count to determine how many batches to process in parallel.  Performance testing for large files
# shows 50K batch_size with 1 batch_count to be a nice balance of speed and resource utilization.  Increasing
# these increases resource utilization but increases speed (especially batch_count).  Reducing these, espectially
# batch_count adds processing cylces (time) but can significantly reduce resources.
def validate_chunks(schema, path, batch_size, batch_count):
    reader = pl.read_csv_batched(path, infer_schema_length=0, missing_utf8_is_empty_string=True, batch_size=batch_size)
    batches = reader.next_batches(batch_count)
    while batches:
        df = pl.concat(batches)
        findings = validate(schema, df)
        batches = reader.next_batches(batch_count)
        yield findings


def get_real_file_path(path):
    path = str(path)
    if path.startswith("s3://"):
        fs: AbstractFileSystem = filesystem(protocol="filecache", target_protocol="s3", cache_storage="/tmp/s3")
        path = fs.unstrip_protocol(path)
        with fs.open(path, "r") as f:
            return f.name
    return path


# This function adds an index column (polars dataframes do not normally have one), and filters out
# any row that did not fail a check.
def gather_errors(schema_error: SchemaError):
    schema_error.check_output = schema_error.check_output.with_row_index()
    error_indices = schema_error.check_output.filter(~pl.col("check_output"))["index"].to_list()
    schema_error.check_output = schema_error.check_output.filter(pl.col("index").is_in(error_indices))
    return schema_error
