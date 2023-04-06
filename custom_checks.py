"""A collection of custom check functions for the Pandera schema.

These are checks that are outside the scope of built in checks or 
functionality that is a too complex for a one-line lambda function.

We may wish to split this module into separate modules for single column
validators, group by validators, whole dataset validators, etc. For now, 
we'll just use a single module.

The names of the check functions should be prefixed with the name of the
field or fields they validate."""


from datetime import datetime
from typing import Dict

import pandas as pd


def uli_ensure_each_record_begins_with_the_same_lei(ulis: pd.Series) -> bool:
    """Here's an example of an incomplete docstring. BAD BAD BAD!

    Args:
        ulis (pd.Series): _description_

    Returns:
        bool: _description_
    """

    # the lei is the first 20 characters of the supplied uli
    leis = ulis.apply(lambda s: s[:20])

    # there should only be a single lei present in the submission across
    # all records.
    return leis.nunique() == 1


def app_date_valid_yyyymmdd(date: str) -> bool:
    """Attempt datetime conversion.

    This checks whether the date string has the format %Y%m%d and
    ensures that the supplied date string can be converted to a datetime
    object. For example, 20221344 is invalid because there is no 13th
    month.

    Args:
        date (str): An input string ideally of the format yyyymmdd.

    Returns:
        bool: True indicates that the supplied date string was converted
            successfully to a datetime.datetime object without error.
    """

    try:
        datetime.strptime(date, "%Y%m%d")
        return True
    except ValueError:
        return False


def ct_credit_product_ff_blank_validity(
    grouped_data: Dict[int, pd.Series]
) -> pd.Series:
    """Checks the validity of the field `ct_credit_product_ff` based on
    the selection of `ct_credit_product`.

    The free form field should be blank unless 977 is selected.

    Args:
        grouped_data (Dict[int, pd.Series]): This is a mapping of values
            from ct_credit_product to a pd.Series containing all free
            form text entries supplied for the given value of the credit
            product field.

            Example: {977: pd.Series(["some text", "Some more text."]),
                      1: pd.Series(["", "", "I should be blank!"])}

    Returns:
        pd.Series: A boolean series specifying whether the value of
            ct_credit_product_ff is valid at the specified index.
    """

    # will hold individual boolean series to be concatenated at return
    validation_holder = []

    for ct_credit_product_value, ct_credit_product_ff_series in grouped_data.items():
        if ct_credit_product_value != 977:
            # free form text field should be blank for non 977 entries
            validation_holder.append(ct_credit_product_ff_series == "")
        else:
            # if 977 selected an explanation must be provided
            validation_holder.append(ct_credit_product_ff_series != "")

    return pd.concat(validation_holder)
