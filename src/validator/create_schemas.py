"""Creates two DataFrameSchema objects by rendering the schema template
with validations listed in phase 1 and phase 2."""

from pandera import DataFrameSchema
from phase_validations import phase_1_and_2_validations
from schema_template import get_template

# Get separate schema templates for phase 1 and 2
phase_1_template = get_template()
phase_2_template = get_template()

for column, validations in phase_1_and_2_validations:
    phase_1_template[column].checks = validations["phase_1"]
    phase_2_template[column].checks = validations["phase_2"]

phase_1_schema = DataFrameSchema(phase_1_template)
phase_2_schema = DataFrameSchema(phase_2_template)
