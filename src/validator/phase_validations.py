"""This is a mapping of column names and validations for each phase.

This mapping is used to populate the schema template object and create
an instance of a PanderaSchema object for phase 1 and phase 2."""

#! NOTE: ONLY 2 COLUMNS ARE CURRENTLY INCLUDED FOR ILLUSTRATION PURPOSES

import global_data
from check_functions import (denial_reasons_conditional_enum_value,
                             has_correct_length,
                             has_no_conditional_field_conflict,
                             has_valid_enum_pair,
                             has_valid_multi_field_value_count,
                             has_valid_value_count, is_date, is_date_after,
                             is_date_before_in_days, is_date_in_range,
                             is_fieldset_equal_to, is_fieldset_not_equal_to,
                             is_greater_than, is_greater_than_or_equal_to,
                             is_less_than, is_number, is_unique_in_field,
                             is_valid_code, is_valid_enum,
                             meets_multi_value_field_restriction)
from checks import SBLCheck

phase_1_and_2_validations = {
    "ct_guarantee": {
        "phase_1": [
            SBLCheck(
                is_valid_enum,
                name="ct_guarantee.invalid_enum_value",
                description=(
                    "Each value in 'type of guarantee' (separated by "
                    " semicolons) must equal 1, 2, 3, 4, 5, 6, 7, 8,"
                    " 9, 10, 11, 977, or 999."
                ),
                element_wise=True,
                accepted_values=[
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                    "11",
                    "977",
                    "999",
                ],
            ),
        ],
        "phase_2": [
            SBLCheck(
                has_valid_value_count,
                name="ct_guarantee.invalid_number_of_values",
                description=(
                    "'Type of guarantee' must contain at least one and at"
                    " most five values, separated by semicolons."
                ),
                element_wise=True,
                min_length=1,
                max_length=5,
            ),
            SBLCheck(
                is_unique_in_field,
                warning=True,
                name="ct_guarantee.duplicates_in_field",
                description=(
                    "'Type of guarantee' should not contain " "duplicated values."
                ),
                element_wise=True,
            ),
            SBLCheck(
                meets_multi_value_field_restriction,
                warning=True,
                name="ct_guarantee.multi_value_field_restriction",
                description=(
                    "When 'type of guarantee' contains 999 (no guarantee),"
                    " 'type of guarantee' should not contain more than one"
                    " value."
                ),
                element_wise=True,
                single_values={"999"},
            ),
        ],
    },
    "ct_loan_term": {
        "phase_1": [
            SBLCheck(
                is_number,
                name="ct_loan_term.invalid_numeric_format",
                description="When present, 'loan term' must be a whole number.",
                element_wise=True,
                accept_blank=True,
            ),
        ],
        "phase_2": [
            SBLCheck(
                has_no_conditional_field_conflict,
                name="ct_loan_term.conditional_field_conflict",
                description=(
                    "When 'loan term: NA/NP flag' does not equal 900 (applicable "
                    "and reported), 'loan term' must be blank. When 'loan term:"
                    "NA/NP flag' equals 900, 'loan term' must not be blank."
                ),
                groupby="ct_loan_term_flag",
                condition_values={"900"},
            ),
            SBLCheck(
                is_greater_than_or_equal_to,
                name="ct_loan_term.invalid_numeric_value",
                description=(
                    "When present, 'loan term' must be greater than or equal" "to 1."
                ),
                element_wise=True,
                min_value="1",
                accept_blank=True,
            ),
            SBLCheck(
                is_less_than,
                name="ct_loan_term.unreasonable_numeric_value",
                description=(
                    "When present, 'loan term' should be less than 1200" "(100 years)."
                ),
                element_wise=True,
                max_value="1200",
                accept_blank=True,
            ),
        ],
    },
}
