"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

from io import BytesIO

import pandas as pd
from pandera import DataFrameSchema
from pandera.errors import SchemaErrors

from .checks import SBLCheck
from .phase_validations import get_phase_1_and_2_validations
from .schema_template import get_template


def get_schemas(naics: dict, geoids: dict) -> (DataFrameSchema, DataFrameSchema):
    phase_1_template = get_template()
    phase_2_template = get_template()

    for col, validations in get_phase_1_and_2_validations(naics, geoids).items():
        phase_1_template[col].checks = validations["phase_1"]
        phase_2_template[col].checks = validations["phase_2"]

    phase_1_schema = DataFrameSchema(phase_1_template)
    phase_2_schema = DataFrameSchema(phase_2_template)

    return (phase_1_schema, phase_2_schema)


def validate(schema: DataFrameSchema, df: pd.DataFrame):
    """
    validate received dataframe with schema and return list of
    schema errors

    Args:
        schema (DataFrameSchema): schema to be used for validation
        df (pd.DataFrame): data parsed into dataframe

    Returns:
        list of schema error
    """
    findings = []
    try:
        schema(df, lazy=True)
    except SchemaErrors as errors:
        for schema_error in errors.schema_errors:
            error = schema_error["error"]
            check: SBLCheck = error.check
            column_name = error.schema.name

            fields: list[str] = [column_name]

            if hasattr(check, "name"):
                check_name: str = check.name

                if check.groupby:
                    fields += check.groupby  # type: ignore

                # This will either be a boolean series or a single bool
                check_output = error.check_output
            else:
                # This means this check's column has unique set to True.
                # we shouldn't be using Unique flag as it doesn't return series of
                # validation result .  it returns just a printout result string/txt
                raise AttributeError(f"{str(check)}")

            # Remove duplicates, but keep as `list` for JSON-friendliness
            fields = list(set(fields))

            if check_output is not None:
                # `check_output` must be sorted so its index lines up with `df`'s index
                check_output.sort_index(inplace=True)

                # Filter records using Pandas's boolean indexing, where all False values
                # get filtered out. The `~` does the inverse since it's actually the
                # False values we want to keep.
                # http://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#boolean-indexing
                failed_check_fields_df = df[~check_output][fields].fillna("")

                # Create list of dicts representing the failed validations and the
                # associated field data for each invalid record.
                records = []
                for idx, row in failed_check_fields_df.iterrows():
                    record = {"number": idx + 1, "field_values": {}}
                    for field in fields:
                        record["field_values"][field] = row[field]
                    records.append(record)

                validation_findings = {
                    "validation": {
                        "id": check_name,
                        "description": check.description,
                        "fields": fields,
                        "severity": "warning" if check.warning else "error",
                    },
                    "records": records,
                }

                findings.append(validation_findings)

    return findings


def _validate_helper(
    phase1: DataFrameSchema, phase2: DataFrameSchema, df: pd.DataFrame
) -> list:
    phase1_findings = validate(phase1, df)
    if phase1_findings:
        return phase1_findings
    else:
        phase2_findings = validate(phase2, df)
        if phase2_findings:
            return phase2_findings
        else:
            return [{"response": "No validations errors or warnings"}]


def validate_data_list(
    phase1: DataFrameSchema, phase2: DataFrameSchema, data: dict
) -> list:
    """
    validate data-dictionary entries

    Args:
        phase1 (DataFrameSchema): phase 1 schema
        phase2 (DataFrameSchema): phase 2 schema
        data (dict): data dictionary

    Returns:
        list: list of error validation
    """
    df = pd.DataFrame.from_dict(data)
    return _validate_helper(phase1, phase2, df)


def validate_raw_csv(
    phase1: DataFrameSchema, phase2: DataFrameSchema, data: bytes
) -> list:
    """
    read raw csv bytes and validate them against
    phase 1 and phase 2 checks

    Args:
        phase1 (DataFrameSchema): phase 1 checks
        phase2 (DataFrameSchema): phase 2 checks
        data (bytes): csv bytes

    Returns:
        list: list of error checks
    """
    df = pd.read_csv(BytesIO(data), dtype=str, na_filter=False)
    return _validate_helper(phase1, phase2, df)
