"""A collection of custom check functions for the Pandera schema.

These are functions that are outside the scope of built in checks. We
are not making use of Lambda functions within the schema because they
make testing difficult.

We may wish to split this module into separate files if it grows to an
unwieldy size. For now we'll just use a single module.

The names of the check functions should clearly indicate the purpose of
the function. This may or may not align with the name of the validation
in the fig.

Majority of these checks utilize Pandera Polars PolarsData objects.  These
objects contain a key, which is the field the check is associated with, and
a lazyframe which is then used to do the check.  This significantly improves
processing time over Pandas, as well as resource utilization.  Pandera Polars
does NOT support group_by functions, therefore a "related_fields" arg was added
to the checks that require validating data across multiple fields.

Each Pandera Polars check returns either a scalar boolean, or a lazyframe with a
'check_results' boolean column which shows if each row passed or failed the check

"""

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


def is_date(field_data: pa.PolarsData) -> bool:
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
    lf = field_data.lazyframe
    # polars striptime uses chrono format which allows for non-padded %d, so check
    # that a full 8 digits are present in the date.
    date_check = (
        pl.col(field_data.key).str.contains(r'^\d{8}$')
        & pl.col(field_data.key).str.strptime(pl.Date, "%Y%m%d", strict=False).is_not_null()
    )
    rf = lf.with_columns(date_check.alias("check_results"))
    return rf.select("check_results")


def has_valid_multi_field_value_count(
    field_data: pa.PolarsData,
    max_length: int,
    ignored_values: set[str] = set(),
    related_fields: str = "",
    separator: str = ";",
) -> pl.LazyFrame:
    lf = field_data.lazyframe

    # split the related field and check field values, strip off empty spaces and only collect non-empty values
    # this uses the polars str and list column type functions
    groupby_list = (
        pl.col(related_fields)
        .str.split(separator)
        .list.eval(pl.element().str.strip_chars())
        .list.eval(pl.element().filter(pl.element() != ""))
    )
    check_field_list = (
        pl.col(field_data.key)
        .str.split(separator)
        .list.eval(pl.element().str.strip_chars())
        .list.eval(pl.element().filter(pl.element() != ""))
    )

    # expressions to get the list count of values not in ignored_values. Polars allows you
    # to chain together expressions into a single expression reference
    groupby_lengths = groupby_list.list.set_difference(list(ignored_values)).list.len()
    field_lengths = check_field_list.list.set_difference(list(ignored_values)).list.len()

    # evaluate the expressions on the lazyframe, putting the results into the alias columnns, and
    # collect just the results of the expressions
    rf = (
        lf.with_columns([groupby_lengths.alias("groupby_length"), field_lengths.alias("field_length")])
        .select(["groupby_length", "field_length"])
        .collect()
    )
    # sum up the total lengths of the related and field values and compare to the max_length
    check_results = (rf["groupby_length"] + rf["field_length"]) <= max_length
    return pl.DataFrame({"check_results": check_results}).lazy()


def has_no_conditional_field_conflict(
    field_data: pa.PolarsData,
    condition_values: set[str] = {"977"},
    related_fields: str = "",
    separator: str = ";",
) -> pl.LazyFrame:
    """
    Validates a column's content based on another column's values.
    - if (at least one) related_fields column values is in condition_values list then create
          validation that validate current column value is not empty.
    - if related_fields column values are NOT part of condition_values list then current column
          should be empty.
    """

    lf = field_data.lazyframe
    # expression to split the related field value and alias a boolean if the intersection with the conditional values is empty
    check_col = (
        pl.col(related_fields).str.split(separator).list.set_intersection(list(condition_values)).list.len() == 0
    ).alias("check_col")
    # expression to check if the check field value is empty
    val_col = (pl.col(field_data.key).str.strip_chars().str.len_chars() == 0).alias("val_col")

    rf = lf.with_columns([check_col, val_col]).select(["check_col", "val_col"]).collect()
    rf = rf["check_col"] ^ rf["val_col"]

    # flip the results of ^ so that the check fails if one expression was True but the other False
    return pl.DataFrame({"check_results": ~rf}).lazy()


def is_unique_in_field(
    field_data: pa.PolarsData,
    separator: str = ";",
) -> pl.LazyFrame:
    lf = field_data.lazyframe
    # simply check that the length of a unique list of values equals the original list length.
    # Otherwise, there are duplicates
    val_list = pl.col(field_data.key).str.split(separator).list
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
    field_data: pa.PolarsData,
    accepted_values: list[str],
    accept_blank: bool = False,
    separator: str = ";",
) -> bool:
    lf = field_data.lazyframe
    split_col = pl.col(field_data.key).str.split(separator)

    # format_check is two expressions.  Either the field data is empty and blanks are allowed,
    # or the split field values are all in the accepted values (difference is 0).
    format_check = ((pl.col(field_data.key).str.strip_chars() == "") & accept_blank) | (
        split_col.list.set_difference(accepted_values).list.len() == 0
    )
    rf = lf.with_columns(format_check.alias("check_results"))
    return rf.select("check_results")


def has_valid_value_count(
    field_data: pa.PolarsData, min_length: int, max_length: int = None, separator: str = ";"
) -> pl.LazyFrame:

    # checks that the split list length of the check field is between the min/max length.
    lf = field_data.lazyframe
    val_list = pl.col(field_data.key).str.split(separator).list.len()
    length_check = val_list.is_between(min_length, max_length)
    rf = lf.with_columns(length_check.alias("check_results"))
    return rf.select("check_results")


def is_date_in_range(field_data: pa.PolarsData, start_date_value: str, end_date_value: str) -> bool:

    # checks the date field value is between the start and end date.
    lf = field_data.lazyframe

    start_date = datetime.strptime(start_date_value, "%Y%m%d")
    end_date = datetime.strptime(end_date_value, "%Y%m%d")

    value_dates = pl.col(field_data.key).str.strptime(pl.Date, "%Y%m%d")
    range_check = value_dates.is_between(start_date, end_date)

    return lf.with_columns(range_check.alias("check_results")).select("check_results")


def is_date_after(
    field_data: pa.PolarsData,
    related_fields: str = "",
) -> pl.Series:

    lf = field_data.lazyframe

    related_dates = pl.col(related_fields).str.strptime(pl.Date, "%Y%m%d")
    check_col_dates = pl.col(field_data.key).str.strptime(pl.Date, "%Y%m%d")

    # evaluates the above strings to dates expressions and puts them into new columns, and then
    # collects just those columns for comparison, verifying the related field date is less than
    # or equal to the check field date (happens on or before)
    rf = lf.with_columns([related_dates.alias("check_date_tmp"), check_col_dates.alias("v_date_tmp")])
    rf = rf.select(["check_date_tmp", "v_date_tmp"]).collect()
    check_results = rf['check_date_tmp'] <= rf['v_date_tmp']
    return pl.DataFrame({"check_results": check_results}).lazy()


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
    field_data: pa.PolarsData,
    conditions: list[list] = None,
    related_fields: str = "",
    separator: str = ";",
) -> pl.Series:
    """Validates a column's enum value based on another column's enum values.
    Args:
        field_data (Dict[str, pl.Series]): parsed data/series from source file
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
    lf = field_data.lazyframe

    # expressions to strip off white space of the related value to check, and
    # split the check field value
    related_field_value = pl.col(related_fields).str.strip_chars()
    field_values = pl.col(field_data.key).str.split(separator)
    # start with a True series, which will then be anded to for each condition
    check_results = pl.lit(True)

    for condition in conditions:
        check = check_condition(condition, field_values, related_field_value)
        # and all conditions, any failure fails the check
        check_results = check_results & check
    rf = lf.with_columns(check_results.alias("check_results"))
    return rf.select("check_results")


def check_condition(condition, field_values, related_field_value):

    # returns an expression to check if the field value list does or
    # does not contain the target value
    def field_check(field_values, target_value, should_equal_target):
        if should_equal_target:
            return field_values.list.contains(target_value)
        else:
            return ~field_values.list.contains(target_value)

    con_values = condition["condition_values"]
    target_value = condition["target_value"]
    should_equal_target = condition["should_equal_target"]

    # first build an expression based on if we're looking for
    # the related field being in a list of conditional values
    if condition["is_equal_condition"]:
        check = related_field_value.is_in(list(con_values))
    else:
        check = ~related_field_value.is_in(list(con_values))
    # next build an expression to check if the field values do or do not contain the target value
    field_check_exp = field_check(field_values, target_value, should_equal_target)

    # uses polars when/then/otherwise notation, which is basically an if/else
    # here the expression is doing
    # if the is_equal_condition check is met:
    #     return target value field check result
    # else:
    #     return True (the conditional check wasn't meant, so we're good)
    return pl.when(check).then(field_check_exp).otherwise(True)


def is_date_before_in_days(field_data: pa.PolarsData, days_value: int = 730, related_fields: str = "") -> pl.Series:

    lf = field_data.lazyframe
    # builds a dataframe by converting the check and related fields from strings to dates and putting them
    # into columns
    rf = lf.with_columns(
        [
            pl.col(related_fields).str.strptime(pl.Date, "%Y%m%d").alias("check_date_tmp"),
            pl.col(field_data.key).str.strptime(pl.Date, "%Y%m%d").alias("v_date_tmp"),
        ]
    )
    rf = rf.select(["v_date_tmp", "check_date_tmp"]).collect()

    # diff the two columns as date objects and verify the diff in days is less than the max days
    diff_values = (rf['v_date_tmp'] - rf['check_date_tmp']).dt.total_days()
    check_results = diff_values < days_value
    rf = pl.DataFrame({"check_results": check_results}).lazy()
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


def has_valid_format(field_data: pa.PolarsData, regex: str, accept_blank: bool = False) -> bool:
    lf = field_data.lazyframe

    # here format_check is two expressions, one that checks if the field value is empty and blanks are allowed,
    # or the field value meets the passed in regex
    format_check = ((pl.col(field_data.key).str.strip_chars() == "") & accept_blank) | pl.col(
        field_data.key
    ).str.contains(regex)
    rf = lf.with_columns(format_check.alias("check_results"))
    return rf.select("check_results")


def is_unique_column(field_data: pa.PolarsData, related_fields: str = "", count_limit: int = 1) -> pl.Series:

    # uses polars column is_unique() function to check there are no duplicate values
    rf = field_data.lazyframe.select(field_data.key).collect().is_unique()
    rf = pl.DataFrame({"check_results": rf}).lazy()
    return rf


def has_valid_fieldset_pair(
    field_data: pa.PolarsData,
    condition_values: list[str],
    related_fields: list[str],
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
        field_data (Dict[list[str], pl.Series]): parsed data provided by pandera
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
    lf = field_data.lazyframe

    def check_fieldset_expression(field, condition):
        idx, must_equal, target_value = condition
        operator_check = pl.col(field) == target_value if must_equal else pl.col(field) != target_value
        return operator_check

    # this builds a list of def calls to be anded together by the below expression, for each key/tuple defined
    # in the check should_fieldset_key_equal_to
    conditions = [
        check_fieldset_expression(field, condition) for field, condition in should_fieldset_key_equal_to.items()
    ]
    combinded_conditions = conditions[0]
    for cond in conditions[1:]:
        combinded_conditions &= cond

    # polars has an expression chain called when/then/otherwise which equates to the concept of if/else.
    # Here, this chain of expressions is doing:
    # if field data is not in condition_values: (don't bother checking the conditionals)
    #    return True
    # elif evaluate the anded check_fieldset_expressions: (all conditional checks have to result in True)
    #    return True
    # else:
    #   return False (field data was a condition value and one or more of the conditional checks failed)
    conditions_check = (
        pl.when(~pl.col(field_data.key).is_in(condition_values))
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
