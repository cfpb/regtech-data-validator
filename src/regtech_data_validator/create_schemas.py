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
from regtech_data_validator.validation_results import ValidationPhase, ValidationResults
from regtech_data_validator.data_formatters import format_findings

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

    sorted_check_output = check_output["index"]
    fields = ["index"] + fields
    filtered_df = df.filter(pl.col('index').is_in(sorted_check_output))
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
    # into one with the record_no, finding_no, field_value and field_name
    failed_record_fields_df = failed_records_df.melt(
        variable_name='field_name', value_name='field_value', id_vars=['record_no', 'finding_no']
    )
    return failed_record_fields_df


def _add_validation_metadata(failed_check_fields_df: pl.DataFrame, check: SBLCheck):
    validation_fields_df = failed_check_fields_df.with_columns(pl.lit(check.title).alias("validation_id"))
    return validation_fields_df


def validate(schema: pa.DataFrameSchema, submission_df: pl.LazyFrame) -> ValidationResults:
    """
    validate received dataframe with schema and return list of
    schema errors
    Args:
        schema (DataFrameSchema): schema to be used for validation
        submission_df (pl.DataFrame): data to be validated against the schema
    Returns:
        bool whether the given submission was valid or not
        pd.DataFrame containing validation results data
    """
    findings_df: pl.DataFrame = pl.DataFrame()
    next_finding_no: int = 1

    try:
        submission_df = submission_df.with_row_index()
        schema(submission_df, lazy=True)
    except pl.exceptions.ColumnNotFoundError as schema_err:
        raise RuntimeError(schema_err) from schema_err
    except SchemaErrors as err:
        check_findings = []
        # NOTE: `type: ignore` because SchemaErrors.schema_errors is supposed to be
        #       `list[dict[str,Any]]`, but it's actually of type `SchemaError`
        schema_error: SchemaError

        for schema_error in err.schema_errors:

            check = schema_error.check
            column_name = schema_error.schema.name

            if schema_error.reason_code is SchemaErrorReason.CHECK_ERROR:
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
                failed_records_df = failed_records_df.with_columns(
                    (pl.col("finding_no") + next_finding_no).alias("finding_no")
                )
                next_finding_no = failed_records_df.tail(1)["finding_no"] + 1  # type: ignore
                failed_record_fields_df = _records_to_fields(failed_records_df)
                check_findings.append(_add_validation_metadata(failed_record_fields_df, check))
            else:
                # The above exception handling _should_ prevent this from ever happenin, but...just in case.
                raise RuntimeError(f'No check output for "{check.name}" check.  Pandera SchemaError: {schema_error}')
        if check_findings:
            findings_df = pl.concat(check_findings)
            findings_df = findings_df.sort("finding_no")

    updated_df = add_uid(findings_df, submission_df)
    return updated_df


def add_uid(results_df: pl.DataFrame, submission_df: pl.DataFrame) -> pl.DataFrame:
    if results_df.is_empty():
        return results_df

    uid_records = results_df['record_no'] - 1
    results_df = results_df.with_columns(submission_df['uid'].gather(uid_records).alias('uid'))
    return results_df


def validate_batch_csv(
    path: Path, context: dict[str, str] | None = None, batch_size: int = 20000, batch_count: int = 5
):
    has_syntax_errors = False

    syntax_schema = get_phase_1_schema_for_lei(context)
    syntax_checks = [check for col_schema in syntax_schema.columns.values() for check in col_schema.checks]

    logic_schema = get_phase_2_schema_for_lei(context)
    logic_checks = [check for col_schema in logic_schema.columns.values() for check in col_schema.checks]

    for findings in validate_chunks(syntax_schema, path, batch_size, batch_count):
        # validate, and therefore validate_chunks, can return an empty dataframe for findings
        if not findings.is_empty():
            has_syntax_errors = True
            rf = format_findings(findings, syntax_checks)
            yield rf, ValidationPhase.SYNTACTICAL

    if not has_syntax_errors:
        uids = pl.scan_csv(path, infer_schema_length=0, missing_utf8_is_empty_string=True).select("uid").collect()
        register_schema = get_register_checks(context)
        findings = validate(register_schema, uids)
        if not findings.is_empty():
            rf = format_findings(
                findings, [check for col_schema in register_schema.columns.values() for check in col_schema.checks]
            )
            yield rf, ValidationPhase.LOGICAL
        for findings in validate_chunks(logic_schema, path, batch_size, batch_count):
            # validate, and therefore validate_chunks, can return an empty dataframe for findings
            if not findings.is_empty():
                rf = format_findings(findings, logic_checks)
                yield rf, ValidationPhase.LOGICAL


def validate_chunks(schema, path, batch_size, batch_count):
    reader = pl.read_csv_batched(path, infer_schema_length=0, missing_utf8_is_empty_string=True, batch_size=batch_size)
    batches = reader.next_batches(batch_count)
    while batches:
        df = pl.concat(batches)
        findings = validate(schema, df)
        batches = reader.next_batches(batch_count)
        yield findings


def gather_errors(schema_error: SchemaError):
    schema_error.check_output = schema_error.check_output.with_row_index()
    error_indices = schema_error.check_output.filter(~pl.col("check_output"))["index"].to_list()
    schema_error.check_output = schema_error.check_output.filter(pl.col("index").is_in(error_indices))
    return schema_error
