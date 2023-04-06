"""Create a Pandera SBLAR Schema object for example SBLAR data.

Refer to the Pandera documentation for details. 
https://pandera.readthedocs.io/en/stable/dataframe_schemas.html"""

from pandera import Check, Column, DataFrameSchema

from custom_checks import (
    app_date_valid_yyyymmdd,
    ct_credit_product_ff_blank_validity,
    uli_ensure_each_record_begins_with_the_same_lei,
)

sblar_schema = DataFrameSchema(
    {
        "uid": Column(
            str,
            title="Field 1: Unique Identifier",
            description="An optional, longer description that says more stuff.",
            checks=[
                Check.str_length(21, 45, title="Verify UID length", raise_warning=True),
                Check(
                    lambda s: s.nunique() == s.size,
                    title="Uniquness Check",
                    raise_warning=True,
                    description="Alternative implementation of built-in unique=True.",
                ),
                Check(
                    uli_ensure_each_record_begins_with_the_same_lei, raise_warning=True
                ),
            ],
        ),
        "app_date": Column(
            str,
            title="Field 2: Application Date",
            checks=[
                Check(
                    app_date_valid_yyyymmdd,
                    element_wise=True,
                    raise_warning=True,
                )
            ],
        ),
        "app_method": Column(
            int,
            title="Field 3: Application Method",
            coerce=True,
            checks=[Check.isin([1, 2, 3, 4], raise_warning=True)],
        ),
        "ct_credit_product": Column(
            int,
            title="Field 5: Credit Product",
            coerce=True,
            checks=[
                Check.isin([1, 2, 3, 4, 5, 6, 7, 8, 977, 988], raise_warning=True),
            ],
        ),
        "ct_credit_product_ff": Column(
            str,
            title="Field 6: Free-Form Text Field for Other Credit Products",
            checks=[
                Check.str_length(0, 300, raise_warning=True),
                Check(
                    ct_credit_product_ff_blank_validity,
                    groupby="ct_credit_product",
                    raise_warning=True,
                ),
            ],
        ),
    }
)
