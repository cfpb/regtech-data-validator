"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

from pandera import DataFrameSchema
from phase_validations import get_phase_1_and_2_validations
from schema_template import get_template

# Get separate schema templates for phase 1 and 2


phase_1_template = get_template()
phase_2_template = get_template()


def get_schema_by_phase(template, validation, lei: str):
    for column, validations in get_phase_1_and_2_validations(lei):
        template[column].checks = validations[validation]
    return DataFrameSchema(template)


def get_phase_1_schema(lei: str):
    return get_schema_by_phase(phase_1_template, "phase_1", lei)


def get_phase_2_schema(lei: str):
    return get_schema_by_phase(phase_2_template, "phase_2", lei)
