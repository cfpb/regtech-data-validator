"""Create a Pandera SBLAR Schema object for example SBLAR data.

Refer to the Pandera documentation for details. 
https://pandera.readthedocs.io/en/stable/dataframe_schemas.html"""


from pandera import Column, DataFrameSchema

from check_functions import (
    app_date_valid_yyyymmdd,
    ct_credit_product_ff_blank_validity,
    uli_ensure_each_record_begins_with_the_same_lei,
)
from verbose_check import VerboseCheck

sblar_schema = DataFrameSchema(
    {
        "uid": Column(
            str,
            title="Field 1: Unique Identifier",
            description="An optional, longer description that says more stuff.",
            unique=True,
            checks=[
                VerboseCheck.str_length(21, 45, name="UID Length"),
                VerboseCheck(
                    uli_ensure_each_record_begins_with_the_same_lei,
                    name="Ensure LEI Uniqueness Across Records",
                ),
            ],
        ),
        "app_date": Column(
            str,
            title="Field 2: Application Date",
            checks=[
                VerboseCheck(
                    app_date_valid_yyyymmdd, element_wise=True, name="Valid Date Format"
                )
            ],
        ),
        "app_method": Column(
            int,
            title="Field 3: Application Method",
            coerce=True,
            checks=[VerboseCheck.isin([1, 2, 3, 4], name="1-4 Only")],
        ),
        "ct_credit_product": Column(
            int,
            title="Field 5: Credit Product",
            coerce=True,
            checks=[
                VerboseCheck.isin(
                    [1, 2, 3, 4, 5, 6, 7, 8, 977, 988], name="1-8, 977, or 988 Only"
                ),
            ],
        ),
        "ct_credit_product_ff": Column(
            str,
            title="Field 6: Free-Form Text Field for Other Credit Products",
            checks=[
                VerboseCheck.str_length(0, 300, name="Free Form Entry Length"),
                VerboseCheck(
                    ct_credit_product_ff_blank_validity,
                    name="Valid Free Form Entry",
                    groupby="ct_credit_product",
                ),
            ],
        ),
    }
)
