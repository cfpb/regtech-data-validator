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
    result = pd.Series(index=series.index, name=series.name, data=True)
    if condition:
        result = series == condition_value
    else:
        result = series != condition_value
    for i, v in result.items():
        if v is False:
            print(i)

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
                condition["should_equal_target"],
                other_series,
                condition["target_value"],
            )
        elif (
            condition["condition_values"] is not None
            and not condition["is_equal_condition"]
            and received_values.isdisjoint(condition["condition_values"])
        ):
            return _has_valid_enum_pair_validation_helper(
                condition["should_equal_target"],
                other_series,
                condition["target_value"],
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
                        "should_equal_target": True,
                    },
                    {
                        "condition_values": {"988"},
                        "is_equal_condition": True,
                        "target_value": "999",
                        "should_equal_target": False,
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


def _is_unique_column_helper(series: pd.Series, count_limit: int):
    """
    helper function for is_unique_column

    Args:
        series (pd.Series): series related to a row

    Returns:
        all rows validations
    """
    series_validations = {}
    check_result = series.count() <= count_limit
    for current_index, _ in series.items():
        series_validations[current_index] = check_result
    return series_validations


def is_unique_column(
    grouped_data: Dict[any, pd.Series], count_limit: int = 1
) -> pd.Series:
    """
    verify if the content of a column is unique.
    - To be used with element_wise set to false
    - To be used with group_by set to itself column
    - Return validations for each row

    Args:
        grouped_data (Dict[any, pd.Series]): rows data

    Returns:
        pd.Series: all rows validations
    """
    validation_holder = []
    for _, main_series in grouped_data.items():
        validation_holder.append(
            pd.Series(
                index=main_series.index,
                name=main_series.name,
                data=_is_unique_column_helper(main_series, count_limit),
            )
        )
    return pd.concat(validation_holder)


def _get_has_valid_fieldset_pair_eq_neq_validation_value(
    current_values: list[str],
    should_fieldset_key_equal_to: dict({str: (int, bool, str)}) = None,
) -> bool:
    # for field_name, (index, equal_to, target_value) in should_fieldset_key_equal_to:
    for index, should_equal_to, target_value in should_fieldset_key_equal_to.values():
        if should_equal_to:
            # if received value != target value, then returns False (Warning)
            if current_values[index] != target_value:
                return False
        else:
            # if received value equal target value, then returns False (Warning)
            if current_values[index] == target_value:
                return False
    # By default returns True (No Warning and fieldset pair is VALID)
    return True


def _has_valid_fieldset_pair_helper(
    current_values: list[str],
    series: pd.Series,
    condition_values: list[str],
    should_fieldset_key_equal_to: dict({str: (int, bool, str)}) = None,
):
    series_validations = {}
    for current_index, current_value in series.items():
        """Getting the validation result for comparing current_values to the
        should_fieldset_key_equal_to (target values)"""
        has_valid_fieldset_pair_eq_neq_validation_value = (
            _get_has_valid_fieldset_pair_eq_neq_validation_value(
                current_values, should_fieldset_key_equal_to
            )
        )
        """
        If current_value is in condition_values AND
        has_valid_fieldset_pair_eq_neq_validation_value is True, 
        then fieldset pair is valid (True). 

        If current_value is in condition_values AND
        has_valid_fieldset_pair_eq_neq_validation_value is False, 
        then fieldset pair is NOT valid (False). 
        """
        validation = (
            current_value in condition_values
            and has_valid_fieldset_pair_eq_neq_validation_value
        ) or current_value not in condition_values
        series_validations[current_index] = validation
    return series_validations


def has_valid_fieldset_pair(
    grouped_data: Dict[any, pd.Series],
    condition_values: list[str],
    should_fieldset_key_equal_to: dict({str: (int, bool, str)}) = None,
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
        should_fieldset_key_equal_to Dict{str, (int, bool, str)}: dict of field name
        and tuple, where the first value is the index of field in the groupby and it
        must start at zero.
        The second value in tuple should be True if the received value MUST EQUAL
        the target value, else it should be False if the received value
        MUST NOT EQUAL the target value. The third value in the tuple should be the
        target value for the fields passed in the groupby function.
        The number of tuples in the list should match the number of fields passed in
        the groupby function.
        For example:
        If the groupby function returns the values for the follwing fields:
        po_1_ethnicity, po_1_race, OR po_1_gender_flag,
        po_2_ethnicity, po_2_race, po_2_gender_flag,
        po_3_ethnicity, po_3_race, po_3_gender_flag,
        po_4_ethnicity, po_4_race, OR po_4_gender_flag

        If the condition is:

        IF num_principal_owners is equal to 1 THEN
            IF (po_1_ethnicity, po_1_race, OR po_1_gender_flag) is blank THEN
                    Warning
            ENDIF
            IF (po_2_ethnicity, po_2_race, po_2_gender_flag,
                po_3_ethnicity, po_3_race, po_3_gender_flag,
                po_4_ethnicity, po_4_race, OR po_4_gender_flag) is not blank THEN
                    Warning
            ENDIF
        ENDIF

        Then the should_fieldset_key_equal_to would be:

        should_fieldset_key_equal_to={
            "po_1_ethnicity": (0, False, ""),
            "po_1_race": (1, False, ""),
            "po_1_gender_flag": (2, False, ""),
            "po_2_ethnicity": (3, True, ""),
            "po_2_race": (4, True, ""),
            "po_2_gender_flag": (5, True, ""),
            "po_3_ethnicity": (6, True, ""),
            "po_3_race": (7, True, ""),
            "po_3_gender_flag": (8, True, ""),
            "po_4_ethnicity": (9, True, ""),
            "po_4_race": (10, True, ""),
            "po_4_gender_flag": (11, True, ""),
        },
    Returns:
        pd.Series: list of series with update validations
    """
    validation_holder = []
    for values, main_series in grouped_data.items():
        validation_holder.append(
            pd.Series(
                index=main_series.index,
                name=main_series.name,
                data=(
                    _has_valid_fieldset_pair_helper(
                        values,
                        main_series,
                        condition_values,
                        should_fieldset_key_equal_to,
                    )
                ),
                dtype=bool,
            )
        )
    return pd.concat(validation_holder)


def string_contains(
    value: str,
    containing_value: str = None,
    start_idx: int = None,
    end_idx: int = None,
) -> bool:
    """
    check if value matches containing value

    Args:
        value (str): parsed value
        containing_value (str): tcontaining value to which value is compared to
        start_idx (int): the start index if the value needs to sliced
        end_idx (int): the end index if the value needs to sliced
    Returns:
        bool: true if value matches containing_value
    """
    if containing_value is not None:
        if start_idx is not None and end_idx is not None:
            return value[start_idx:end_idx] == containing_value
        elif start_idx is not None and end_idx is None:
            return value[start_idx:] == containing_value
        elif start_idx is None and end_idx is not None:
            return value[:end_idx] == containing_value
        else:
            return value == containing_value
    else:
        return True
