"""Create a Pandera SBLAR Schema object for example SBLAR data.

A custom Pandera Check sublcass is created called NamedCheck which
raises a ValueError if initialized without a name attribute. We could 
extend this approach to have separate subclasses for errors and
warnings.

Refer to the Pandera documentation for details. 
https://pandera.readthedocs.io/en/stable/dataframe_schemas.html"""


from pandera import Check, Column, DataFrameSchema
from pandera.backends.pandas.checks import PandasCheckBackend

from check_functions import (
    app_date_valid_yyyymmdd,
    ct_credit_product_ff_blank_validity,
    uli_ensure_each_record_begins_with_the_same_lei,
)


class NamedCheck(Check):

    """A custom Pandera.Check subclasss that requires a `name`."""

    def __init__(self, *args, **kwargs):
        if "name" not in kwargs:
            raise ValueError("Each check must be assigned a `name`.")
        super().__init__(*args, **kwargs)

    @classmethod
    def get_backend(cls, *args) -> PandasCheckBackend:
        """Assume Pandas DataFrame and return PandasCheckBackend"""
        return PandasCheckBackend


sblar_schema = DataFrameSchema(
    {
        "uid": Column(
            str,
            title="Field 1: Unique Identifier",
            description="An optional, longer description that says more stuff.",
            unique=True,
            checks=[
                NamedCheck.str_length(21, 45, name="UID Length"),
                NamedCheck(
                    uli_ensure_each_record_begins_with_the_same_lei,
                    name="Ensure LEI Uniqueness Across Records",
                ),
            ],
        ),
        "app_date": Column(
            str,
            title="Field 2: Application Date",
            checks=[
                NamedCheck(
                    app_date_valid_yyyymmdd, element_wise=True, name="Valid Date Format"
                )
            ],
        ),
        "app_method": Column(
            int,
            title="Field 3: Application Method",
            coerce=True,
            checks=[NamedCheck.isin([1, 2, 3, 4], name="1-4 Only")],
        ),
        "ct_credit_product": Column(
            int,
            title="Field 5: Credit Product",
            coerce=True,
            checks=[
                NamedCheck.isin(
                    [1, 2, 3, 4, 5, 6, 7, 8, 977, 988], name="1-8, 977, or 988 Only"
                ),
            ],
        ),
        "ct_credit_product_ff": Column(
            str,
            title="Field 6: Free-Form Text Field for Other Credit Products",
            checks=[
                NamedCheck.str_length(0, 300, name="Free Form Entry Length"),
                NamedCheck(
                    ct_credit_product_ff_blank_validity,
                    name="Valid Free Form Entry",
                    groupby="ct_credit_product",
                ),
            ],
        ),
    }
)
