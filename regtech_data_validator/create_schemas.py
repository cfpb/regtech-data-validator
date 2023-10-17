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


def get_schema_by_phase_for_lei(template: dict, phase: str, lei: str|None = None):
    for column in get_phase_1_and_2_validations_for_lei(lei):
        validations = get_phase_1_and_2_validations_for_lei(lei)[column]
        template[column].checks = validations[phase]
    return DataFrameSchema(template)


def get_phase_1_schema_for_lei(lei: str|None = None):
    return get_schema_by_phase_for_lei(phase_1_template, "phase_1", lei)


def get_phase_2_schema_for_lei(lei: str|None = None):
    return get_schema_by_phase_for_lei(phase_2_template, "phase_2", lei)


def validate(schema: DataFrameSchema, df: pd.DataFrame) -> list[dict]:
    """
    validate received dataframe with schema and return list of
    schema errors
    Args:
        schema (DataFrameSchema): schema to be used for validation
        df (pd.DataFrame): data parsed into dataframe
    Returns:
        list of validation findings (warnings and errors)
    """
    findings = []
    try:
        schema(df, lazy=True)
    except SchemaErrors as err:

        # WARN: SchemaErrors.schema_errors is supposed to be of type
        #       list[dict[str,Any]], but it's actually of type SchemaError
        schema_error: SchemaError
        for schema_error in err.schema_errors: # type: ignore
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
            check_output = schema_error.check_output

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
                        "id": check.title,
                        "name": check.name,
                        "description": check.description,
                        "severity": check.severity,
                        "fields": fields,
                    },
                    "records": records,
                }

                findings.append(validation_findings)

    return findings


def validate_phases(df: pd.DataFrame, lei: str|None = None) -> list:
    phase1_findings = validate(get_phase_1_schema_for_lei(lei), df)
    if phase1_findings:
        return phase1_findings
    else:
        phase2_findings = validate(get_phase_2_schema_for_lei((lei)), df)
        if phase2_findings:
            return phase2_findings
        else:
            return [{"response": "No validations errors or warnings"}]