"""A collection of custom check functions for the Pandera schema.

These are functions that are outside the scope of built in checks or 
functionality that is a too complex for a one-line lambda function.

We may wish to split this module into separate files if it grows to an
unwieldy size. For now we'll just use a single module.

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


def date_valid_yyyymmdd(date: str) -> bool:
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


# helper function for multi_invalid_number_of_values:
# process series and return validations
def _get_related_series_validations(value_count: int, 
                                    series: pd.Series, 
                                    max_length: int, 
                                    separator: str = ";") -> dict:
    series_validations = {}
    for index, value in series.items():
        series_count = len(value.split(separator))
        series_validations[index] = (series_count + value_count) <= max_length
    return series_validations
    
def multi_invalid_number_of_values(
    grouped_data: Dict[str, pd.Series], max_length: int, separator: str = ";"
) -> pd.Series:
    validation_holder = []
    items = grouped_data.items()

    for value, other_series in items:
        validation_holder.append(
            pd.Series(
                index=other_series.index,
                name=other_series.name,
                data=_get_related_series_validations(
                    len(value.split(separator)), 
                    other_series, 
                    max_length),
            )
        )

    return pd.concat(validation_holder)


def conditional_field_conflict(
    grouped_data: Dict[str, pd.Series],
    condition_value: str = "977",
    separator: str = ";",
) -> pd.Series:
    # will hold individual boolean series to be concatenated at return
    validation_holder = []
    for value, other_series in grouped_data.items():
        if condition_value in value.split(separator):
            # free form text should NOT be blank if condition_value existed in list
            validation_holder.append(other_series != "")
        else:
            # free form should be blank if condition_value NOT existed in list
            validation_holder.append(other_series == "")
    return pd.concat(validation_holder)


def duplicates_in_field(ct_value: str, separator: str = ";") -> bool:
    values = ct_value.split(separator)
    return len(set(values)) == len(values)


def multi_value_field_restriction(
    ct_value: str, single_value: str, separator: str = ";"
) -> bool:
    ct_values_set = set(ct_value.split(separator))
    if (single_value not in ct_values_set) or (
        len(ct_values_set) == 1 and single_value in ct_values_set
    ):
        return True
    else:
        return False


def invalid_enum_value(
    ct_value: str, accepted_values: list[str], separator: str = ";"
) -> bool:
    ct_values_set = set(ct_value.split(separator))
    return ct_values_set.issubset(accepted_values)


def invalid_number_of_values(
    ct_value: str, min_length: int, max_length: int, separator: str = ";"
) -> bool:
    values_count = len(ct_value.split(separator))
    return min_length <= values_count and values_count <= max_length
