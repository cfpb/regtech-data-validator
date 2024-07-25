"""A collection of custom check functions for the Pandera schema.

These are functions that are outside the scope of built in checks. We
are not making use of Lambda functions within the schema because they
make testing difficult.

We may wish to split this module into separate files if it grows to an
unwieldy size. For now we'll just use a single module.

The names of the check functions should clearly indicate the purpose of
the function. This may or may not align with the name of the validation
in the fig."""

from datetime import datetime

import pandera.polars as pa
import polars as pl
import operator


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


def comparison_helper(value: str, limit: str, accept_blank: bool, operand) -> bool:
    if not value.strip() and not accept_blank:
        return False
    elif not value.strip() and accept_blank:
        return True
    return operand(float(value), float(limit))


def begins_with_same_lei(ulis: pl.Series) -> bool:
    """Verifies that only a single LEI prefixes the list of ULIs.

    Args:
        ulis (pl.Series): ULIs supplied in the submission.

    Returns:
        bool: True indicates that only a single LEI is present. False
            otherwise.
    """

    # the lei is the first 20 characters of the supplied uli
    leis = ulis.apply(lambda s: s[:20], pl.String)

    # there should only be a single lei present in the submission across
    # all records.
    return leis.nunique() == 1


def is_date(grouped_data: pa.PolarsData) -> bool:
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

    # check for number type and length must be 8 to match YYYYMMDD
    lf = grouped_data.lazyframe
    date_check = pl.col(grouped_data.key).str.strptime(pl.Date, "%Y%m%d", strict=False).is_not_null()
    rf = lf.with_columns(date_check.alias("check_results"))
    return rf.select("check_results")


def has_valid_multi_field_value_count(
    grouped_data: pa.PolarsData,
    max_length: int,
    ignored_values: set[str] = set(),
    groupby_fields: str = "",
    separator: str = ";",
) -> pl.LazyFrame:
    lf = grouped_data.lazyframe

    groupby_list = pl.col(groupby_fields).str.split(separator).list
    check_field_list = pl.col(grouped_data.key).str.split(separator).list

    groupby_lengths = groupby_list.set_difference(list(ignored_values)).list.len()
    field_lengths = check_field_list.set_difference(list(ignored_values)).list.len()

    rf = (
        lf.with_columns([groupby_lengths.alias("groupby_length"), field_lengths.alias("field_length")])
        .select(["groupby_length", "field_length"])
        .collect()
    )

    check_results = (rf["groupby_length"] + rf["field_length"]) <= max_length

    return pl.DataFrame(check_results).lazy()


def has_no_conditional_field_conflict(
    grouped_data: pa.PolarsData,
    condition_values: set[str] = {"977"},
    groupby_fields: str = "",
    separator: str = ";",
) -> pl.LazyFrame:
    """
    Validates a column's content based on another column's values.
    - if (at least one) other column values is in condition_values list then create
          validation that validate current column value is not empty.
    - if other column values are NOT part of condition_values list then current column
          values should be empty.

    Args:
        grouped_data (Dict[str, pl.Series]): parsed data/series from source file
        condition_values (list[str], optional): list of acceptable values for other
            column. Defaults to ["977"].
        separator (str, optional): character used to separate multiple values.
            Defaults to ";".

    Returns:
        pl.Series: series of current column validations
    """
    lf = grouped_data.lazyframe
    check_col = (
        pl.col(groupby_fields).str.split(separator).list.set_intersection(list(condition_values)).list.len() == 0
    ).alias("check_col")
    val_col = (pl.col(grouped_data.key).str.strip_chars().str.len_chars() == 0).alias("val_col")
    rf = lf.with_columns([check_col, val_col]).select(["check_col", "val_col"]).collect()
    rf = rf["check_col"] ^ rf["val_col"]

    return pl.DataFrame(~rf).lazy()


def is_unique_in_field(
    grouped_data: pa.PolarsData,
    separator: str = ";",
) -> pl.LazyFrame:
    lf = grouped_data.lazyframe
    val_list = pl.col(grouped_data.key).str.split(separator).list
    unique_list = val_list.unique().list
    unique_check = val_list.len() == unique_list.len()
    rf = lf.with_columns(unique_check.alias("check_results"))
    return rf.select("check_results")


def meets_multi_value_field_restriction(ct_value: str, single_values: set[str], separator: str = ";") -> bool:
    ct_values_set = set(ct_value.split(separator))
    if (ct_values_set.isdisjoint(single_values)) or (len(ct_values_set) == 1 and ct_values_set.issubset(single_values)):
        return True
    else:
        return False


def is_valid_enum(
    grouped_data: pa.PolarsData,
    accepted_values: list[str],
    accept_blank: bool = False,
    separator: str = ";",
) -> bool:
    lf = grouped_data.lazyframe
    split_col = pl.col(grouped_data.key).str.split(separator)
    format_check = ((pl.col(grouped_data.key).str.strip_chars() == "") & accept_blank) | (
        split_col.list.set_difference(accepted_values).list.len() == 0
    )
    rf = lf.with_columns(format_check.alias("check_results"))
    return rf.select("check_results")


def has_valid_value_count(
    grouped_data: pa.PolarsData, min_length: int, max_length: int = None, separator: str = ";"
) -> pl.LazyFrame:
    lf = grouped_data.lazyframe
    val_list = pl.col(grouped_data.key).str.split(separator).list.len()
    length_check = val_list.is_between(min_length, max_length)
    rf = lf.with_columns(length_check.alias("check_results"))
    return rf.select("check_results")


def is_date_in_range(grouped_data: pa.PolarsData, start_date_value: str, end_date_value: str) -> bool:
    """Checks that the date_value is within the range of the start_date_value
        and the end_date_value

    Args:
        date_value: Date input ideally within the range of the current reporting period
        start_date_value: Starting date of reporting period
        end_date_value: End date of the reporting period

    Returns: Returns True if date_value occurs within the current reporting period
    """
    lf = grouped_data.lazyframe

    start_date = datetime.strptime(start_date_value, "%Y%m%d")
    end_date = datetime.strptime(end_date_value, "%Y%m%d")

    value_dates = pl.col(grouped_data.key).str.strptime(pl.Date, "%Y%m%d")
    range_check = value_dates.is_between(start_date, end_date)

    return lf.with_columns(range_check.alias("check_results")).select("check_results")


def is_date_after(
    grouped_data: pa.PolarsData,
    groupby_fields: str = "",
) -> pl.Series:
    """Checks if date in column is after the date value of another column

    Args:
        grouped_data: Data grouped on before_date column

    Returns: Series with corresponding True/False validation values for the column
    """
    lf = grouped_data.lazyframe

    groupby_dates = pl.col(groupby_fields).str.strptime(pl.Date, "%Y%m%d")
    check_col_dates = pl.col(grouped_data.key).str.strptime(pl.Date, "%Y%m%d")

    rf = lf.with_columns([groupby_dates.alias("check_date_tmp"), check_col_dates.alias("v_date_tmp")])
    rf = rf.select(["check_date_tmp", "v_date_tmp"]).collect()
    check_results = rf['check_date_tmp'] <= rf['v_date_tmp']
    return pl.DataFrame(check_results).lazy()


def is_number(ct_value: str, accept_blank: bool = False, is_whole: bool = False) -> bool:
    """
    function to check a string is a number
    return True if value is number , False if value is not number
    This includes float values as some of the checks involve decimal values
    Args:
        ct_value (str): string value

    Returns:
        bool: True if value is number , False if value is not number
    """
    value_check = True
    num_parser = int if is_whole else float
    try:
        num_parser(ct_value)
    except ValueError:
        value_check = False

    return _check_blank_(ct_value, value_check, accept_blank)


def has_valid_enum_pair(
    grouped_data: pa.PolarsData,
    conditions: list[list] = None,
    groupby_fields: str = "",
    separator: str = ";",
) -> pl.Series:
    """Validates a column's enum value based on another column's enum values.
    Args:
        grouped_data (Dict[str, pl.Series]): parsed data/series from source file
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
    lf = grouped_data.lazyframe
    check_values = pl.col(groupby_fields).str.split(separator)
    target_values = pl.col(grouped_data.key).str.strip_chars()
    check_results = pl.lit(True)

    for condition in conditions:
        check = check_condition(condition, check_values, target_values)
        check_results = check_results & check
    rf = lf.with_columns(check_results.alias("check_results"))
    return rf.select("check_results")


def check_condition(condition, check_values, target_values):
    target_operator = operator.eq if condition["should_equal_target"] else operator.ne
    con_values = condition["condition_values"]
    target_value = condition["target_value"]

    if condition["is_equal_condition"]:
        check = check_values.list.set_intersection(list(con_values)).list.len() > 0
    else:
        check = check_values.list.set_intersection(list(con_values)).list.len() == 0
    return pl.when(check).then(target_operator(target_values, target_value)).otherwise(True)


def is_date_before_in_days(grouped_data: pa.PolarsData, days_value: int = 730, groupby_fields: str = "") -> pl.Series:
    """Checks if the provided date is not beyond
       the grouped column date plus the days_value parameter
    Args:
        grouped_data: Data grouped on the initial date column
        days_value: This value is added to our grouped data to find our
            unreasonable_date value

    Returns: Series with corresponding True/False validation values for the column
    """
    lf = grouped_data.lazyframe
    rf = lf.with_columns(
        [
            pl.col(groupby_fields).str.strptime(pl.Date, "%Y%m%d").alias("check_date_tmp"),
            pl.col(grouped_data.key).str.strptime(pl.Date, "%Y%m%d").alias("v_date_tmp"),
        ]
    )
    rf = rf.select(["v_date_tmp", "check_date_tmp"]).collect()
    diff_values = (rf['v_date_tmp'] - rf['check_date_tmp']).dt.total_days()
    check_results = diff_values < days_value
    rf = pl.DataFrame(check_results).lazy()
    return rf


def has_correct_length(ct_value: str, accepted_length: int, accept_blank: bool = False) -> bool:
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


def is_greater_than_or_equal_to(value: str, min_value: str, accept_blank: bool = False) -> bool:
    return comparison_helper(value, min_value, accept_blank, operator.ge)


def is_greater_than(value: str, min_value: str, accept_blank: bool = False) -> bool:
    return comparison_helper(value, min_value, accept_blank, operator.gt)


def is_less_than(value: str, max_value: str, accept_blank: bool = False) -> bool:
    return comparison_helper(value, max_value, accept_blank, operator.lt)


def has_valid_format(grouped_data: pa.PolarsData, regex: str, accept_blank: bool = False) -> bool:
    lf = grouped_data.lazyframe
    format_check = ((pl.col(grouped_data.key).str.strip_chars() == "") & accept_blank) | pl.col(
        grouped_data.key
    ).str.contains(regex)
    rf = lf.with_columns(format_check.alias("check_results"))
    return rf.select("check_results")


def is_unique_column(grouped_data: pa.PolarsData, groupby_fields: str = "", count_limit: int = 1) -> pl.Series:
    """
    verify if the content of a column is unique.
    - To be used with element_wise set to false
    - To be used with group_by set to itself column
    - Return validations for each row

    Args:
        grouped_data (Dict[any, pl.Series]): rows data

    Returns:
        pl.Series: all rows validations
    """
    rf = grouped_data.lazyframe.select(grouped_data.key).collect().is_unique()
    rf = pl.DataFrame(rf).lazy()
    return rf


def has_valid_fieldset_pair(
    grouped_data: pa.PolarsData,
    condition_values: list[str],
    groupby_fields: list[str],
    should_fieldset_key_equal_to: dict({str: (int, bool, str)}) = None,
) -> pl.Series:
    """conditional check to verify if groups of fields equal to specific
        values (equal_to_values) when another field is set/equal to
        condition_values.
        * Note: when we define multiple fields in group_by parameter,
                Pandera returns group_by values in the dictionary key
                as iterable string
                and the column data in the series

    Args:
        grouped_data (Dict[list[str], pl.Series]): parsed data provided by pandera
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
        pl.Series: list of series with update validations
    """
    lf = grouped_data.lazyframe

    def check_fieldset_expression(field, condition):
        idx, must_equal, target_value = condition
        operator_check = pl.col(field) == target_value if must_equal else pl.col(field) != target_value
        return operator_check

    conditions = [
        check_fieldset_expression(field, condition) for field, condition in should_fieldset_key_equal_to.items()
    ]
    combinded_conditions = conditions[0]
    for cond in conditions[1:]:
        combinded_conditions &= cond

    conditions_check = (
        pl.when(~pl.col(grouped_data.key).is_in(condition_values))
        .then(pl.lit(True))
        .when(combinded_conditions)
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
    )
    rf = lf.with_columns(conditions_check.alias("check_results"))
    return rf.select("check_results")


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
        containing_value (str): ßcontaining value to which value is compared to
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
