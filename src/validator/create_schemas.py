"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

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


def print_schema_errors(errors: SchemaErrors, phase: str):
    for error in errors.schema_errors:
        # Name of the column in the dataframe being checked
        schema_error = error["error"]
        column_name = schema_error.schema.name

        # built in checks such as unique=True are different than custom
        # checks unfortunately so the name needs to be accessed differently
        try:
            check_name = schema_error.check.name
            check_id = schema_error.check.id
            # This will either be a boolean series or a single bool
            check_output = schema_error.check_output
        except AttributeError:
            check_name = schema_error.check
            # this is just a string that we'd need to parse manually
            check_output = schema_error.args[0]

        print(
            f"{phase} Validation `{check_name}` with id: `{check_id}` \
            failed for column `{column_name}`"
        )
        print(check_output)
        print("")


def get_phase_1_schema_for_lei(lei: str = None):
    return get_schema_by_phase_for_lei(phase_1_template, "phase_1", lei)


def get_phase_2_schema_for_lei(lei: str = None):
    return get_schema_by_phase_for_lei(phase_2_template, "phase_2", lei)
