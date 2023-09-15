"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

import pandas as pd
from checks import SBLCheck
from pandera import DataFrameSchema
from pandera.errors import SchemaErrors
from phase_validations import get_phase_1_and_2_validations_for_lei
from schema_template import get_template

# Get separate schema templates for phase 1 and 2


phase_1_template = get_template()
phase_2_template = get_template()


def get_schema_by_phase_for_lei(template: dict, phase: str, lei: str = None):
    for column in get_phase_1_and_2_validations_for_lei(lei):
        validations = get_phase_1_and_2_validations_for_lei(lei)[column]
        template[column].checks = validations[phase]
    return DataFrameSchema(template)


def get_phase_1_schema_for_lei(lei: str = None):
    return get_schema_by_phase_for_lei(phase_1_template, "phase_1", lei)


def get_phase_2_schema_for_lei(lei: str = None):
    return get_schema_by_phase_for_lei(phase_2_template, "phase_2", lei)


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
            check_id = "n/a"

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

            if hasattr(check, "id"):
                check_id: str = check.id

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
                        "id": check_id,
                        "name": check_name,
                        "description": check.description,
                        "fields": fields,
                        "severity": "warning" if check.warning else "error",
                    },
                    "records": records,
                }

                findings.append(validation_findings)

    return findings


def validate_phases_by_lei(df: pd.DataFrame, lei: str) -> list:
    phase1_findings = validate(get_phase_1_schema_for_lei(lei), df)
    if phase1_findings:
        return phase1_findings
    else:
        phase2_findings = validate(get_phase_2_schema_for_lei((lei)), df)
        if phase2_findings:
            return phase2_findings
        else:
            return [{"response": "No validations errors or warnings"}]
