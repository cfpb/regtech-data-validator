"""A collection of custom check functions for the Pandera schema.

These are functions that are outside the scope of built in checks. We 
are not making use of Lambda functions within the schema because they
make testing difficult. 

We may wish to split this module into separate files if it grows to an
unwieldy size. For now we'll just use a single module.

The names of the check functions should clearly indicate the purpose of
the function. This may or may not align with the name of the validation
in the fig."""


from datetime import datetime, timedelta
from typing import Dict

import re
import pandas as pd


def uli_ensure_each_record_begins_with_the_same_lei(ulis: pd.Series) -> bool:
    """Verifies that only a single LEI prefixes the list of ULIs.

    Args:
        ulis (pd.Series): ULIs supplied in the submission.

    Returns:
        bool: True indicates that only a single LEI is present. False
            otherwise.
    """

    # the lei is the first 20 characters of the supplied uli
    leis = ulis.apply(lambda s: s[:20])

    # there should only be a single lei present in the submission across
    # all records.
    return leis.nunique() == 1


def invalid_date_format(date: str) -> bool:
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


# helper function for denial_reasons_conditional_enum_value:
# check for target_value in existing values
# process series and return validations
def _get_not_contains_series_validations(series: pd.Series, target_value: str) -> dict:
    series_validations = {}
    for index, value in series.items():
        existing_values = value.split(";")
        validation = target_value not in existing_values
        series_validations[index] = validation
    return series_validations


def denial_reasons_conditional_enum_value(
    grouped_data: Dict[str, pd.Series],
) -> pd.Series:
    """
    custom validation function for denial_reasons.enum_value_conflict
    "When 'action taken' equals 3, 'denial reason(s)' must not"
    "contain 999. When 'action taken' does not equal 3, 'denial"
    "reason(s)' must equal 999."

    Args:
        grouped_data (Dict[str, pd.Series]): values from source file
        condition_values (set[str]): list of values that we will use to
            compare with values from source
        separator (str, optional): separator in the values

    Returns:
        pd.Series: list of series with updated validation
    """
    validation_holder = []
    action_taken_value = "3"
    denial_reasons_value = "999"
    for value, other_series in grouped_data.items():
        if value == action_taken_value:
            # IF action_taken is equal to 3 THEN
            #       IF denial_reasons MUST NOT contains 999
            validation_holder.append(
                pd.Series(
                    index=other_series.index,
                    name=other_series.name,
                    data=_get_not_contains_series_validations(
                        other_series, denial_reasons_value
                    ),
                )
            )
        else:
            # IF action_taken is not equal to 3 THEN
            #   IF denial_reasons MUST equal to 999
            validation_holder.append(other_series == denial_reasons_value)

    return pd.concat(validation_holder)


# helper function for multi_invalid_number_of_values:
# process series and return validations
def _get_related_series_validations(
    value_count: int, series: pd.Series, max_length: int, separator: str = ";"
) -> dict:
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
                    len(value.split(separator)), other_series, max_length
                ),
            )
        )

    return pd.concat(validation_holder)


def conditional_field_conflict(
    grouped_data: Dict[str, pd.Series],
    condition_values: set[str] = {"977"},
    separator: str = ";",
) -> pd.Series:
    """
    Validates a column's content based on another column's values.
    - if (at least one) other column values is in condition_values list then create
          validation that validate current column value is not empty.
    - if other column values are NOT part of condition_values list then current column
          values should be empty.

    Args:
        grouped_data (Dict[str, pd.Series]): parsed data/series from source file
        condition_values (list[str], optional): list of acceptable values for other
            column. Defaults to ["977"].
        separator (str, optional): character used to separate multiple values.
            Defaults to ";".

    Returns:
        pd.Series: series of current column validations
    """
    # will hold individual boolean series to be concatenated at return
    validation_holder = []
    for value, other_series in grouped_data.items():
        received_values = set(value.split(separator))
        if received_values.isdisjoint(condition_values):
            # disjoint will return TRUE if received values do not contain
            #    condition values
            # free form should be blank if acceptable values NOT existed
            # in received list
            validation_holder.append(other_series == "")
        else:
            # free form text should NOT be blank if acceptable values
            # existed in received list
            validation_holder.append(other_series != "")

    return pd.concat(validation_holder)


def duplicates_in_field(ct_value: str, separator: str = ";") -> bool:
    values = ct_value.split(separator)
    return len(set(values)) == len(values)


def multi_value_field_restriction(
    ct_value: str, single_values: set[str], separator: str = ";"
) -> bool:
    ct_values_set = set(ct_value.split(separator))
    if (ct_values_set.isdisjoint(single_values)) or (
        len(ct_values_set) == 1 and ct_values_set.issubset(single_values)
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


def invalid_date_value(
    date_value: str, start_date_value: str, end_date_value: str
) -> bool:
    """Checks that the date_value is within the range of the start_date_value
        and the end_date_value

    Args:
        date_value: Date input ideally within the range of the current reporting period
        start_date_value: Starting date of reporting period
        end_date_value: End date of the reporting period

    Returns: Returns True if date_value occurs within the current reporting period
    """
    try:
        date = datetime.strptime(date_value, "%Y%m%d")
        start_date = datetime.strptime(start_date_value, "%Y%m%d")
        end_date = datetime.strptime(end_date_value, "%Y%m%d")
        return start_date <= date <= end_date
    except ValueError:
        return False


def date_value_conflict(
    grouped_data: Dict[str, pd.Series],
) -> pd.Series:
    """Checks if date in column is after the date value of another column

    Args:
        grouped_data: Data grouped on before_date column

    Returns: Series with corresponding True/False validation values for the column
    """
    # will hold individual boolean series to be concatenated at return
    validation_holder = []
    for value, other_series in grouped_data.items():
        try:
            before_date = datetime.strptime(value, "%Y%m%d")
            other_series = pd.to_datetime(
                other_series
            )  # Convert other series to Date time object

            validation_holder.append(
                other_series.apply(lambda date: date >= before_date)
            )
        except ValueError:
            validation_holder.append(other_series.apply(lambda v: False))
    return pd.concat(validation_holder)


def is_number(ct_value: str) -> bool:
    """
    function to check a string is a number
    return True if value is number , False if value is not number
    This includes float values as some of the checks involve decimal values
    Args:
        ct_value (str): string value

    Returns:
        bool: True if value is number , False if value is not number
    """
    return ct_value.isdigit() or bool(re.match(r'^[-+]?[0-9]*\.?[0-9]+$', ct_value))


def enum_value_conflict(
    grouped_data: Dict[str, pd.Series],
    condition_values1: set[str] = {"1", "2"},
    condition_values2: set[str] = {"988"},
    condition_value="999",
    separator: str = ";",
) -> pd.Series:
    """
    function to get validations that validate a column's content based on other column
    values
    - if the condition_value1 is not null and received values is in condition_values1
        -other column should not equal condition_value
    - if the condition_value2 is not null and received values in condition_values2
        -other column should equal condition_value

    Args:
        grouped_data (Dict[str, pd.Series]): parsed data/series from source file
        condition_values1 (list[str], optional): list of acceptable values for first
            condition. Defaults to ["1", "2"].
        condition_values2 (list[str], optional): list of acceptable values for second
            condition. Defaults to ["988"].
        condition_value (str, optional): str values for other column. Defaults to "999".
        separator (str, optional): character used to separate multiple values.
            Defaults to ";".

    Returns:
        pd.Series: series of current column validations
    """
    # will hold individual boolean series to be concatenated at return
    validation_holder = []
    for value, other_series in grouped_data.items():
        received_values = set(value.split(separator))
        if condition_values1 is not None and received_values.issubset(
            condition_values1
        ):
            validation_holder.append(other_series != condition_value)
        elif condition_values2 is not None and received_values.issubset(
            condition_values2
        ):
            validation_holder.append(other_series == condition_value)

    return pd.concat(validation_holder)


def unreasonable_date_value(
    grouped_data: Dict[str, pd.Series], days_value: int = 730
) -> pd.Series:
    """Checks if the provided date is not beyond
       the grouped column date plus the days_value parameter
    Args:
        grouped_data: Data grouped on the initial date column
        days_value: This value is added to our grouped data to find our
            unreasonable_date value

    Returns: Series with corresponding True/False validation values for the column
    """
    # will hold individual boolean series to be concatenated at return
    validation_holder = []
    for value, other_series in grouped_data.items():
        try:
            initial_date = datetime.strptime(value, "%Y%m%d")
            unreasonable_date = initial_date + timedelta(days=days_value)
            other_series = pd.to_datetime(
                other_series
            )  # Convert other series to Date time object

            validation_holder.append(
                other_series.apply(lambda date: date < unreasonable_date)
            )
        except ValueError:
            validation_holder.append(other_series.apply(lambda v: False))
    return pd.concat(validation_holder)
