"""Create a Pandera SBLAR DataFrameSchema object.

Refer to the Pandera documentation for details. 
https://pandera.readthedocs.io/en/stable/dataframe_schemas.html

The only major modification from native Pandera is the use of custom
Check classes to differentiate between warnings and errors. """

from check_functions import (conditional_field_conflict, duplicates_in_field,
                             invalid_enum_value, invalid_number_of_values,
                             multi_invalid_number_of_values,
                             multi_value_field_restriction)
from checks import SBLCheck
from pandera import Column, DataFrameSchema

sblar_schema = DataFrameSchema(
    {
        "uid": Column(
            str,
            title="Field 1: Unique identifier",
            checks=[],
        ),
        "app_date": Column(
            str,
            title="Field 2: Application date",
            checks=[],
        ),
        "app_method": Column(
            str,
            title="Field 3: Application method",
            checks=[],
        ),
        "app_recipient": Column(
            str,
            title="Field 4: Application recipient",
            checks=[],
        ),
        "ct_credit_product": Column(
            str,
            title="Field 5: Credit product",
            checks=[],
        ),
        "ct_credit_product_ff": Column(
            str,
            title="Field 6: Free-form text field for other credit products",
            checks=[],
        ),
        "ct_guarantee": Column(
            str,
            title="Field 7: Type of guarantee",
            checks=[
                SBLCheck(
                    invalid_number_of_values,
                    name="ct_guarantee.invalid_number_of_values",
                    description=(
                        "‘Type of guarantee’ must contain at least one and at"
                        " most five values, separated by semicolons."
                    ),
                    element_wise=True,
                    min_length=1,
                    max_length=5,
                ),
                SBLCheck(
                    duplicates_in_field,
                    warning=True,
                    name="ct_guarantee.duplicates_in_field",
                    description=(
                        "‘Type of guarantee’ should not contain "
                        "duplicated values."
                    ),
                    element_wise=True,
                ),
                SBLCheck(
                    multi_value_field_restriction,
                    warning=True,
                    name="ct_guarantee.multi_value_field_restriction",
                    description=(
                        "When ‘type of guarantee’ contains 999 (no guarantee),"
                        " ‘type of guarantee’ should not contain more than one"
                        " value."
                    ),
                    element_wise=True,
                    single_value="999",
                ),
                SBLCheck(
                    invalid_enum_value,
                    name="ct_guarantee.invalid_enum_value",
                    description=(
                        "Each value in ‘type of guarantee’ (separated by "
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
        ),
        "ct_guarantee_ff": Column(
            str,
            title="Field 8: Free-form text field for other guarantee",
            checks=[
                SBLCheck.str_length(
                    0,
                    300,
                    name="ct_guarantee_ff.invalid_text_length",
                    description=(
                        "‘Free-form text field for other guarantee’ must not "
                        "exceed 300 characters in length"
                    ),
                ),
                SBLCheck(
                    conditional_field_conflict,
                    name="ct_guarantee_ff.conditional_field_conflict",
                    description=(
                        "When ‘type of guarantee’ does not contain 977 (other), "
                        "‘free-form text field for other guarantee’ must be blank. "
                        "When ‘type of guarantee’ contains 977, ‘free-form text field"
                        " for other guarantee’ must not be blank."
                    ),
                    groupby="ct_guarantee",
                    condition_value="977",
                ),
                SBLCheck(
                    multi_invalid_number_of_values,
                    warning=True,
                    name="ct_guarantee_ff.multi_invalid_number_of_values",
                    description=(
                        "‘Type of guarantee’ and ‘free-form text field for other "
                        "guarantee‘ combined should not contain more than five values. "
                        "Code 977 (other), within 'type of guarantee', does not count "
                        "toward the maximum number of values for the purpose of this "
                        "validation check."
                    ),
                    groupby="ct_guarantee",
                    max_length=5,
                ),      
            ],
        ),
        
    }
)
