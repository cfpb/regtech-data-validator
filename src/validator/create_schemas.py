"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

from pandera import DataFrameSchema
from phase_validations import get_phase_1_and_2_validations_for_lei
from schema_template import get_template

# Get separate schema templates for phase 1 and 2


phase_1_template = get_template()
phase_2_template = get_template()


def get_schema_by_phase_for_lei(template: dict, phase: str, lei: str = None):
    for column, validations in get_phase_1_and_2_validations_for_lei(lei):
        template[column].checks = validations[phase]
    return DataFrameSchema(template)


def get_phase_1_schema_for_lei(lei: str = None):
    return get_schema_by_phase_for_lei(phase_1_template, "phase_1", lei)


def get_phase_2_schema_for_lei(lei: str = None):
    return get_schema_by_phase_for_lei(phase_2_template, "phase_2", lei)
