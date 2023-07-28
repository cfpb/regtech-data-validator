"""A collection of custom check functions for the Pandera schema.

These are functions that are outside the scope of built in checks. We 
are not making use of Lambda functions within the schema because they
make testing difficult. 

We may wish to split this module into separate files if it grows to an
unwieldy size. For now we'll just use a single module.

The names of the check functions should clearly indicate the purpose of
the function. This may or may not align with the name of the validation
in the fig."""


import re
from datetime import datetime, timedelta
from typing import Dict

import pandas as pd


def _check_blank_(value: str, check_result: bool, accept_blank: bool = False) -> bool:
    """helper function to validate value for blank space.  if accept_blank is true
    then empty space is allowed.  If accept_blank is false then return false if
    valus is blank or return non-blank logic result

    Args:
        value (str): value from parsed data
        check_result (bool): bool value from non-blank value check
        accept_blank (bool, optional): flag to check blank. Defaults to False.

    Returns:
        bool: true if all checks passed
    """
    is_blank = not value.strip()

    if is_blank:
        return accept_blank
    else:
        return check_result


def begins_with_same_lei(ulis: pd.Series) -> bool:
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


def is_date(date: str) -> bool:
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
        # check for number type and length must be 8 to match YYYYMMDD
        if date.isdigit() and len(date) == 8:
            # if format and type is correct, verify datetime content
            datetime.strptime(date, "%Y%m%d")
            return True
        else:
            return False
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


# helper function to get non blank values
def _get_non_blank_values(values: list[str]):
    return filter(lambda v: v.strip() != "", values)


# helper function for has_valid_multi_field_value_count:
# process series and return validations
def _get_related_series_validations(
    value_count: int, series: pd.Series, max_length: int, separator: str = ";"
) -> dict:
    series_validations = {}
    for index, value in series.items():
        series_count = len(set(_get_non_blank_values(value.split(separator))))
        series_validations[index] = (series_count + value_count) <= max_length
    return series_validations


def has_valid_multi_field_value_count(
    grouped_data: Dict[str, pd.Series],
    max_length: int,
    ignored_values: set[str] = set(),
    separator: str = ";",
) -> pd.Series:
    validation_holder = []
    items = grouped_data.items()

    for value, other_series in items:
        processed_value = set(_get_non_blank_values(value.split(separator)))
        validation_holder.append(
            pd.Series(
                index=other_series.index,
                name=other_series.name,
                data=_get_related_series_validations(
                    len(processed_value - ignored_values),
                    other_series,
                    max_length,
                ),
            )
        )

    return pd.concat(validation_holder)


def _get_conditional_field_series_validations(
    series: pd.Series, conditional_func
) -> dict:
    series_validations = {}
    for index, value in series.items():
        series_validations[index] = conditional_func(value)
    return series_validations


def has_no_conditional_field_conflict(
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
            validation_holder.append(
                pd.Series(
                    index=other_series.index,
                    name=other_series.name,
                    data=_get_conditional_field_series_validations(
                        other_series, lambda v: not v.strip()
                    ),
                )
            )
        else:
            # free form text should NOT be blank if acceptable values
            # existed in received list
            validation_holder.append(
                pd.Series(
                    index=other_series.index,
                    name=other_series.name,
                    data=_get_conditional_field_series_validations(
                        other_series, lambda v: v.strip() != ""
                    ),
                )
            )

    return pd.concat(validation_holder)


def is_unique_in_field(ct_value: str, separator: str = ";") -> bool:
    values = ct_value.split(separator)
    return len(set(values)) == len(values)


def meets_multi_value_field_restriction(
    ct_value: str, single_values: set[str], separator: str = ";"
) -> bool:
    ct_values_set = set(ct_value.split(separator))
    if (ct_values_set.isdisjoint(single_values)) or (
        len(ct_values_set) == 1 and ct_values_set.issubset(single_values)
    ):
        return True
    else:
        return False


def is_valid_enum(
    ct_value: str,
    accepted_values: list[str],
    accept_blank: bool = False,
    separator: str = ";",
) -> bool:
    ct_values_set = set(ct_value.split(separator))
    enum_check = ct_values_set.issubset(accepted_values)
    if accept_blank:
        return enum_check or not ct_value.strip()
    else:
        return enum_check


def has_valid_value_count(
    ct_value: str, min_length: int, max_length: int = None, separator: str = ";"
) -> bool:
    values_count = len(ct_value.split(separator))
    if max_length is None:
        return min_length <= values_count
    else:
        return min_length <= values_count and values_count <= max_length


def is_date_in_range(
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


def is_date_after(
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


def is_number(ct_value: str, accept_blank: bool = False) -> bool:
    """
    function to check a string is a number
    return True if value is number , False if value is not number
    This includes float values as some of the checks involve decimal values
    Args:
        ct_value (str): string value

    Returns:
        bool: True if value is number , False if value is not number
    """
    value_check = ct_value.isdigit() or bool(
        re.match(r"^[-+]?[0-9]*\.?[0-9]+$", ct_value)
    )

    return _check_blank_(ct_value, value_check, accept_blank)


def _has_valid_enum_pair_validation_helper(
    condition=True,
    series: pd.Series = None,
    condition_value=None,
) -> pd.Series:
    result = None
    if condition:
        result = series != condition_value
    else:
        result = series == condition_value
    return result


def _has_valid_enum_pair_helper(
    conditions: list[list] = None,
    received_values: set[str] = None,
    other_series: pd.Series = None,
) -> pd.Series:
    for condition in conditions:
        if (
            condition["condition_values"] is not None
            and condition["is_equal_condition"]
            and received_values.issubset(condition["condition_values"])
        ):
            return _has_valid_enum_pair_validation_helper(
                condition["is_equal_target"], other_series, condition["target_value"]
            )
        elif (
            condition["condition_values"] is not None
            and not condition["is_equal_condition"]
            and received_values.isdisjoint(condition["condition_values"])
        ):
            return _has_valid_enum_pair_validation_helper(
                condition["is_equal_target"], other_series, condition["target_value"]
            )

    return pd.Series(index=other_series.index, name=other_series.name, data=True)


def has_valid_enum_pair(
    grouped_data: Dict[str, pd.Series],
    conditions: list[list] = None,
    separator: str = ";",
) -> pd.Series:
    """Validates a column's enum value based on another column's enum values.
    Args:
        grouped_data (Dict[str, pd.Series]): parsed data/series from source file
        conditions: list of list of key-value pairs
        conditions should be passed in the following format:
            Example:
                conditions=[
                    {
                        "condition_values": {"1", "2"},
                        "is_equal_condition": True,
                        "target_value": "999",
                        "is_equal_target": True,
                    },
                    {
                        "condition_values": {"988"},
                        "is_equal_condition": True,
                        "target_value": "999",
                        "is_equal_target": False,
                    },
                ],
        separator (str, optional): character used to separate multiple values.
            Defaults to ";".


    Returns: Series with corresponding True/False validation values for the column
    """
    # will hold individual boolean series to be concatenated at return
    validation_holder = []
    for value, other_series in grouped_data.items():
        received_values = set(value.split(separator))
        validation_holder.append(
            _has_valid_enum_pair_helper(conditions, received_values, other_series)
        )
    return pd.concat(validation_holder)


def is_date_before_in_days(
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


def _is_fieldset_equal_to_helper(
    current_values: list[str],
    series: pd.Series,
    condition_values: list[str],
    target_values: list[str],
):
    series_validations = {}
    for current_index, current_value in series.items():
        validation = (
            current_value in condition_values
            and list(current_values) == list(target_values)
        ) or current_value not in condition_values
        series_validations[current_index] = validation
    return series_validations


def is_fieldset_equal_to(
    grouped_data: Dict[any, pd.Series],
    condition_values: list[str],
    equal_to_values: list[str],
) -> pd.Series:
    """conditional check to verify if groups of fields equal to specific
        values (equal_to_values) when another field is set/equal to
        condition_values.
        * Note: when we define multiple fields in group_by parameter,
                Pandera returns group_by values in the dictionary key
                as iterable string
                and the column data in the series

    Args:
        grouped_data (Dict[list[str], pd.Series]): parsed data provided by pandera
        condition_values (list[str]): list of value to be compared to main series
        equal_to_values (list[str]): list of expected values from group_by's fields.
            This list has to be in same sequence as the group_by list

    Returns:
        pd.Series: list of series with update validations
    """
    validation_holder = []
    for values, main_series in grouped_data.items():
        validation_holder.append(
            pd.Series(
                index=main_series.index,
                name=main_series.name,
                data=_is_fieldset_equal_to_helper(
                    values, main_series, condition_values, equal_to_values
                ),
            )
        )
    return pd.concat(validation_holder)


def _is_fieldset_not_equal_to_helper(
    current_values: list[str],
    series: pd.Series,
    condition_values: list[str],
    target_values: list[str],
):
    series_validations = {}
    for current_index, current_value in series.items():
        not_contains_map = list(map(lambda a, b: a != b, current_values, target_values))
        validation = (
            current_value in condition_values and all(not_contains_map)
        ) or current_value not in condition_values
        series_validations[current_index] = validation
    return series_validations


def is_fieldset_not_equal_to(
    grouped_data: Dict[any, pd.Series],
    condition_values: list[str],
    not_equal_to_values: list[str],
) -> pd.Series:
    """conditional check to verify if groups of fields NOT equal specific
        values (not_equal_to_values) when another field is set/equal to
        condition_values.
        * Note: when we define multiple fields in group_by parameter,
                Pandera returns group_by values in the dictionary key as
                iterable string and the column data in the series
    Args:
        grouped_data (Dict[list[str], pd.Series]): parsed data provided by pandera
        condition_values (list[str]): list of value to be compared to main series
        not_equal_to_values (list[str]): list of expected values from group_by's fields.
            This list has to be in same sequence as the group_by list

    Returns:
        pd.Series: list of series with update validations
    """
    validation_holder = []
    for values, main_series in grouped_data.items():
        validation_holder.append(
            pd.Series(
                index=main_series.index,
                name=main_series.name,
                data=_is_fieldset_not_equal_to_helper(
                    values, main_series, condition_values, not_equal_to_values
                ),
            )
        )
    return pd.concat(validation_holder)


def has_correct_length(
    ct_value: str, accepted_length: int, accept_blank: bool = False
) -> bool:
    """check text for correct length but allow blank
    Args:
        ct_value (str): value from file
        accepted_length (int): accepted value length
        accept_blank (bool): bool value to ignore check if value is blank

    Returns:
        bool: return true if its number and length is equal to accepted length
                or blank
    """
    value_check = len(ct_value) == accepted_length
    return _check_blank_(ct_value, value_check, accept_blank)


def is_valid_code(ct_value: str, accept_blank: bool = False, codes: dict = {}) -> bool:
    """
    check if value existed in codes keys

    Args:
        ct_value (str): parsed value
        accept_blank (bool): accept blank value
        codes (dict): dict of key -> value
    Returns:
        bool: true if blank or value is in code key list
    """
    key_check = ct_value in codes
    return _check_blank_(ct_value, key_check, accept_blank)


def is_greater_than_or_equal_to(
    value: str, min_value: str, accept_blank: bool = False
) -> bool:
    """
    check if value is greater or equal to min_value or blank
    If blank value check is not needed, use built-in 'greater_than_or_equal_to'

    Args:
        value (str): parsed value
        min_value(str): minimum value
        accept_blank (bool): accept blank value
    Returns:
        bool: true if blank or value is greater than or equal to min value
    """
    check_result = value >= min_value
    return _check_blank_(value, check_result, accept_blank)


def is_greater_than(value: str, min_value: str, accept_blank: bool = False) -> bool:
    """
    check if value is greater than min_value or blank
    If blank value check is not needed, use built-in 'greater_than'

    Args:
        value (str): parsed value
        min_value(str): minimum value
        accept_blank (bool): accept blank value
    Returns:
        bool: true if blank or value is greater than min value
    """
    check_result = value > min_value
    return _check_blank_(value, check_result, accept_blank)


def is_less_than(value: str, max_value: str, accept_blank: bool = False) -> bool:
    """
    check if value is less than max_value or blank
    If blank value check is not needed, use built-in 'less_than'

    Args:
        value (str): parsed value
        max_value(str): maximum value
        accept_blank (bool): accept blank value
    Returns:
        bool: true if blank or value is less than max
    """
    check_result = value < max_value
    return _check_blank_(value, check_result, accept_blank)


def has_valid_format(value: str, regex: str, accept_blank: bool = False) -> bool:
    return _check_blank_(value, bool(re.match(regex, value)), accept_blank)


def is_unique_column(grouped_data: Dict[any, pd.Series]) -> (bool, Dict[str, bool]):
    """
    check if a series values does not have duplicates.
    return overall status check, and detailed dictionary of index and uniqueness
    example:
        if return value is (False, {1:True, 2:False, 3:False})
        then:
            overall validation is FAILED or False
            index 1 value is unique, and index 2 and 3 values are NOT unique

    Args:
        grouped_data (Dict[any, pd.Series]): Parsed series

    Returns:
        (bool, Dict[str, bool]): validation result tuple(index, uniqueness)
    """
    # reversed dictionary to find non-unique LEI/UID
    reversed = {}
    for index, value in grouped_data.items():
        reversed.setdefault(value, set()).add(index)

    # filter reversed to get entry's index with duplicate UID
    non_unique_indexes = sum(
        [list(indexes) for _, indexes in reversed.items() if len(indexes) > 1], []
    )

    # overall validation result
    validation_result = len(non_unique_indexes) == 0

    # default result
    result = {}

    # if validation is failed then we should return index list with
    # its uniqueness value/status
    if validation_result == False:
        # create default result dict (index -> bool)
        result = dict.fromkeys(grouped_data.keys(), True)

        # update default result's indexes to false if the index is not -unique
        for non_unique_index in non_unique_indexes:
            result.update({non_unique_index: False})

    # return overall validation result and list of each index validation result
    return (len(non_unique_indexes) == 0, result)
