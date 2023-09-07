import pandas as pd
import pytest

from validator import global_data
from validator.check_functions import (
    has_correct_length,
    has_no_conditional_field_conflict,
    has_valid_enum_pair,
    has_valid_fieldset_pair,
    has_valid_format,
    has_valid_multi_field_value_count,
    has_valid_value_count,
    is_date,
    is_greater_than,
    is_greater_than_or_equal_to,
    is_less_than,
    is_number,
    is_unique_column,
    is_unique_in_field,
    is_valid_code,
    is_valid_enum,
    meets_multi_value_field_restriction,
    string_contains,
)
from validator.checks import SBLCheck


class TestInvalidDateFormat:
    valid_date_format = "20231010"
    invalid_date_format_1 = "202310101"
    invalid_date_format_2 = "20231032"
    invalid_date_format_3 = "20231301"
    invalid_date_format_4 = "00001201"
    invalid_date_format_5 = "2020121"
    invalid_date_format_6 = "2020120A"

    def test_with_valid_date(self):
        assert is_date(self.valid_date_format) is True

    def test_with_invalid_date(self):
        assert is_date(self.invalid_date_format_1) is False

    def test_with_invalid_day(self):
        assert is_date(self.invalid_date_format_2) is False

    def test_with_invalid_month(self):
        assert is_date(self.invalid_date_format_3) is False

    def test_with_invalid_year(self):
        assert is_date(self.invalid_date_format_4) is False

    def test_with_invalid_format(self):
        assert is_date(self.invalid_date_format_5) is False

    def test_with_invalid_type(self):
        assert is_date(self.invalid_date_format_6) is False


class TestDuplicatesInField:
    def test_with_blank(self):
        assert is_unique_in_field("") is True

    def test_with_no_duplicates(self):
        assert is_unique_in_field("1") is True
        assert is_unique_in_field("1;2;3;4") is True

    def test_with_duplicates(self):
        assert is_unique_in_field("1;2;3;3;4") is False


class TestInvalidNumberOfValues:
    def test_with_in_range(self):
        assert has_valid_value_count("1;2;", 1, 4) is True

    def test_with_lower_range_value(self):
        assert has_valid_value_count("1", 1, 4) is True

    def test_with_invalid_lower_range_value(self):
        assert has_valid_value_count("1", 2, 4) is False

    def test_with_upper_range_value(self):
        assert has_valid_value_count("1;2", 1, 2) is True

    def test_with_invalid_upper_range_value(self):
        assert has_valid_value_count("1;2;3;4", 2, 3) is False

    def test_valid_with_no_upper_bound(self):
        assert has_valid_value_count("1;2;3;4", 1, None) is True

    def test_invalid_with_no_upper_bound(self):
        assert has_valid_value_count("1", 2, None) is False


class TestMultiValueFieldRestriction:
    def test_with_invalid_values(self):
        assert meets_multi_value_field_restriction("1;2;3", ["2"]) is False

    def test_with_valid_length(self):
        assert meets_multi_value_field_restriction("2", ["2"]) is True
        assert meets_multi_value_field_restriction("1", ["2"]) is True

    def test_with_valid_values(self):
        assert meets_multi_value_field_restriction("1;2;3", ["4"]) is True


class TestMultiInvalidNumberOfValues:
    series = pd.Series(["999"], name="test_name", index=[2])

    blank_series = pd.Series([""], name="test_name", index=[2])

    multiple_values_series = pd.Series(["1;2;3"], name="test_name", index=[2])

    multiple_values_series_with_977 = pd.Series(
        ["1;2;3;977"], name="test_name", index=[2]
    )

    multiple_values_series_with_blanks = pd.Series(
        ["1;2;; ;3"], name="test_name", index=[2]
    )

    def test_inside_maxlength(self):
        result = has_valid_multi_field_value_count({"4": self.series}, 5)
        assert result.values == [True]

    def test_on_maxlength(self):
        result = has_valid_multi_field_value_count({"4": self.series}, 2)
        assert result.values == [True]

    def test_with_blank(self):
        result = has_valid_multi_field_value_count({"4;1": self.blank_series}, 2)
        assert result.values == [True]

    def test_invalid_length_with_blank(self):
        result = has_valid_multi_field_value_count({"4;1": self.blank_series}, 1)
        assert result.values == [False]

    def test_invalid_length_with_blank_and_ignored_values(self):
        result = has_valid_multi_field_value_count(
            {"4;1;977": self.blank_series}, 1, ignored_values={"977"}
        )
        assert result.values == [False]

    def test_valid_length_with_blank_and_ignored_values(self):
        result = has_valid_multi_field_value_count(
            {"4;1;977": self.blank_series}, 2, ignored_values={"977"}
        )
        assert result.values == [True]

    def test_outside_maxlength(self):
        result = has_valid_multi_field_value_count({"4": self.series}, 1)
        assert result.values == [False]

    def test_valid_length_with_non_blank(self):
        result = has_valid_multi_field_value_count(
            {"4;1": self.multiple_values_series}, 5
        )
        assert result.values == [True]

    def test_invalid_length_with_non_blank(self):
        result = has_valid_multi_field_value_count(
            {"4;1": self.multiple_values_series}, 4
        )
        assert result.values == [False]

    def test_valid_length_with_ignored_values(self):
        result = has_valid_multi_field_value_count(
            {"4;1": self.multiple_values_series_with_977}, 6, ignored_values={"977"}
        )
        assert result.values == [True]

        result = has_valid_multi_field_value_count(
            {"4;1;977": self.multiple_values_series_with_977}, 6, ignored_values={"977"}
        )
        assert result.values == [True]

    def test_invalid_length_with_ignored_values(self):
        result = has_valid_multi_field_value_count(
            {"4;1": self.multiple_values_series_with_977}, 5, ignored_values={"977"}
        )
        assert result.values == [False]

        result = has_valid_multi_field_value_count(
            {"4;1;977": self.multiple_values_series_with_977}, 5, ignored_values={"977"}
        )
        assert result.values == [False]

    def test_valid_length_with_blank_values(self):
        result = has_valid_multi_field_value_count(
            {"4;1;977": self.multiple_values_series_with_blanks},
            5,
            ignored_values={"977"},
        )
        assert result.values == [True]

        result = has_valid_multi_field_value_count(
            {"4;1;977": self.multiple_values_series_with_blanks}, 6
        )
        assert result.values == [True]

    def test_invalid_length_with_blank_values(self):
        result = has_valid_multi_field_value_count(
            {"4;1;977": self.multiple_values_series_with_blanks},
            4,
            ignored_values={"977"},
        )
        assert result.values == [False]

        result = has_valid_multi_field_value_count(
            {"4;1;977": self.multiple_values_series_with_blanks}, 5
        )
        assert result.values == [False]


class TestInvalidEnumValue:
    def test_with_valid_enum_values(self):
        accepted_values = ["1", "2"]
        result = is_valid_enum("1;2", accepted_values)
        assert result is True

    def test_with_is_valid_enums(self):
        accepted_values = ["1", "2"]
        result = is_valid_enum("0;3", accepted_values)
        assert result is False

    def test_with_valid_blank(self):
        accepted_values = ["1", "2"]
        result = is_valid_enum("", accepted_values, True)
        assert result is True

    def test_with_invalid_blank(self):
        accepted_values = ["1", "2"]
        result = is_valid_enum("", accepted_values)
        assert result is False


class TestIsNumber:
    def test_number_value(self):
        value = "1"
        result = is_number(value)
        assert result is True

        value = "1"
        result = is_number(value, True)
        assert result is True

    def test_non_number_value(self):
        value = "a"
        result = is_number(value)
        assert result is False

    def test_decimal_numeric_value(self):
        value = "0.1"
        result = is_number(value)
        assert result is True

        value = "0.1"
        result = is_number(value, True)
        assert result is True

    def test_alphanumeric_value(self):
        value = "abc123"
        result = is_number(value)
        assert result is False

    def test_negative_numeric_value(self):
        value = "-1"
        result = is_number(value)
        assert result is True

    def test_negative_decimal_value(self):
        value = "-0.1"
        result = is_number(value)
        assert result is True

    def test_valid_blank(self):
        value = ""
        result = is_number(value, True)
        assert result is True

    def test_invalid_blank(self):
        value = ""
        result = is_number(value, False)
        assert result is False


class TestConditionalFieldConflict:
    def test_conditional_field_conflict_correct(self):
        # if ct_loan_term_flag != 900 then ct_loan_term must be blank
        series = pd.Series([""], name="ct_loan_term", index=[2])
        condition_values: set[str] = {"900"}

        result1 = has_no_conditional_field_conflict({"988": series}, condition_values)
        assert result1.values == [True]

        # if ct_loan_term_flag == 900 then ct_loan_term must not be blank
        series2 = pd.Series(["36"], name="ct_loan_term", index=[2])
        condition_values2: set[str] = {"900"}
        result2 = has_no_conditional_field_conflict({"900": series2}, condition_values2)
        assert result2.values == [True]

    def test_conditional_field_conflict_incorrect(self):
        # if ct_loan_term_flag != 900 then ct_loan_term must be blank
        # in this test, ct_loan_term_flag is not 900 and ct_loan_term is
        # NOT blank, so must return False
        series = pd.Series(["36"], name="ct_loan_term", index=[2])
        condition_values: set[str] = {"900"}

        result1 = has_no_conditional_field_conflict({"988": series}, condition_values)
        assert result1.values == [False]

        # if ct_loan_term_flag == 900 then ct_loan_term must not be blank
        # in this testm ct_loan_term is blank, so must return False
        series2 = pd.Series([""], name="ct_loan_term", index=[2])
        condition_values2: set[str] = {"900"}
        result2 = has_no_conditional_field_conflict({"900": series2}, condition_values2)
        assert result2.values == [False]

        series3 = pd.Series([" "], name="ct_loan_term", index=[2])
        result3 = has_no_conditional_field_conflict({"900": series3}, condition_values2)
        assert result3.values == [False]


class TestEnumValueConflict:
    def test_enum_value_confict_correct(self):
        pricing_mca_addcost_flag_conditions = [
            {
                "condition_values": {"1", "2"},
                "is_equal_condition": True,
                "target_value": "999",
                "should_equal_target": False,
            },
            {
                "condition_values": {"988"},
                "is_equal_condition": True,
                "target_value": "999",
                "should_equal_target": True,
            },
        ]

        # If ct_credit_product == 1, 2 then pricing_mca_addcost_flag must not equal 999
        pricing_mca_addcost_flag_series_1 = pd.Series(
            ["900"], name="pricing_mca_addcost_flag", index=[2]
        )

        ct_credit_product_1 = "1"

        pricing_mca_addcost_flag_result_1 = has_valid_enum_pair(
            {ct_credit_product_1: pricing_mca_addcost_flag_series_1},
            pricing_mca_addcost_flag_conditions,
        )
        assert pricing_mca_addcost_flag_result_1.values == [True]

        # If ct_credit_product == 988 then pricing_mca_addcost_flag must equal 999
        ct_credit_product_2 = "988"
        # Case when pricing_mca_addcost_flag = 999
        pricing_mca_addcost_flag_series_2 = pd.Series(
            ["999"], name="pricing_mca_addcost_flag", index=[2]
        )
        pricing_mca_addcost_flag_result_2 = has_valid_enum_pair(
            {ct_credit_product_2: pricing_mca_addcost_flag_series_2},
            pricing_mca_addcost_flag_conditions,
        )
        assert pricing_mca_addcost_flag_result_2.values == [True]

        # If there is more than one condition:
        """ If action_taken is equal to 3 THEN
                IF denial_reasons contains 999 THEN
                    Error
                ENDIF
            ELSEIF action_taken is not equal to 3 THEN
                IF denial_reasons is not equal to 999 THEN
                    Error
                ENDIF
            ENDIF
        """
        denial_reasons_conditions = [
            {
                "condition_values": {"3"},
                "is_equal_condition": True,
                "target_value": "999",
                "should_equal_target": False,
            },
            {
                "condition_values": {"3"},
                "is_equal_condition": False,
                "target_value": "999",
                "should_equal_target": True,
            },
        ]
        # If action_taken is 3, and denial_reasons must not equal  999,
        denial_reasons_1 = pd.Series(["988"], name="denial_reasons", index=[2])
        action_taken_1 = "3"

        denial_reason_result_1 = has_valid_enum_pair(
            {action_taken_1: denial_reasons_1}, denial_reasons_conditions
        )
        assert denial_reason_result_1.values == [True]

        # If action_taken is NOT 3, and denial_reasons must equal 999
        denial_reasons_2 = pd.Series(["999"], name="denial_reasons", index=[2])
        action_taken_2 = "1"
        denial_reason_result_2 = has_valid_enum_pair(
            {action_taken_2: denial_reasons_2}, denial_reasons_conditions
        )
        assert denial_reason_result_2.values == [True]

    def test_enum_value_confict_incorrect(self):
        pricing_mca_addcost_flag_conditions = [
            {
                "condition_values": {"1", "2"},
                "is_equal_condition": True,
                "target_value": "999",
                "should_equal_target": False,
            },
            {
                "condition_values": {"988"},
                "is_equal_condition": True,
                "target_value": "999",
                "should_equal_target": True,
            },
        ]

        # If ct_credit_product == 1, 2 then pricing_mca_addcost_flag must not equal 999
        pricing_mca_addcost_flag_series_1 = pd.Series(
            ["999"], name="pricing_mca_addcost_flag", index=[2]
        )

        ct_credit_product_1 = "1"

        pricing_mca_addcost_flag_result_1 = has_valid_enum_pair(
            {ct_credit_product_1: pricing_mca_addcost_flag_series_1},
            pricing_mca_addcost_flag_conditions,
        )
        assert pricing_mca_addcost_flag_result_1.values == [False]

        # If ct_credit_product == 988 then pricing_mca_addcost_flag must equal 999
        ct_credit_product_2 = "988"
        # Case when pricing_mca_addcost_flag = 999
        pricing_mca_addcost_flag_series_2 = pd.Series(
            ["900"], name="pricing_mca_addcost_flag", index=[2]
        )
        pricing_mca_addcost_flag_result_2 = has_valid_enum_pair(
            {ct_credit_product_2: pricing_mca_addcost_flag_series_2},
            pricing_mca_addcost_flag_conditions,
        )
        assert pricing_mca_addcost_flag_result_2.values == [False]

        # If there is more than one condition:
        """ If action_taken is equal to 3 THEN
                IF denial_reasons contains 999 THEN
                    Error
                ENDIF
            ELSEIF action_taken is not equal to 3 THEN
                IF denial_reasons is not equal to 999 THEN
                    Error
                ENDIF
            ENDIF
        """
        denial_reasons_conditions = [
            {
                "condition_values": {"3"},
                "is_equal_condition": True,
                "target_value": "999",
                "should_equal_target": False,
            },
            {
                "condition_values": {"3"},
                "is_equal_condition": False,
                "target_value": "999",
                "should_equal_target": True,
            },
        ]
        # If action_taken is 3, and denial_reasons must not equal  999,
        denial_reasons_1 = pd.Series(["999"], name="denial_reasons", index=[2])
        action_taken_1 = "3"

        denial_reason_result_1 = has_valid_enum_pair(
            {action_taken_1: denial_reasons_1}, denial_reasons_conditions
        )
        assert denial_reason_result_1.values == [False]

        # If action_taken is NOT 3, and denial_reasons must equal 999
        denial_reasons_2 = pd.Series(["988"], name="denial_reasons", index=[2])
        action_taken_2 = "1"
        denial_reason_result_2 = has_valid_enum_pair(
            {action_taken_2: denial_reasons_2}, denial_reasons_conditions
        )
        assert denial_reason_result_2.values == [False]


class TestHasCorrectLength:
    def test_with_accept_blank_value(self):
        result = has_correct_length("", 3, True)
        assert result is True

    def test_with_invalid_blank_value(self):
        result = has_correct_length("", 3, False)
        assert result is False

    def test_with_correct_length(self):
        result = has_correct_length("abc", 3, True)
        assert result is True

    def test_with_incorrect_length(self):
        result = has_correct_length("1", 3, True)
        assert result is False


class TestIsValidCode:
    def test_with_valid_code(self):
        global_data.read_naics_codes()
        result = is_valid_code("111", False, global_data.naics_codes)
        assert result is True
        result = is_valid_code("111", True, global_data.naics_codes)
        assert result is True

    def test_with_invalid_code(self):
        global_data.read_naics_codes()
        result = is_valid_code("101", False, global_data.naics_codes)
        assert result is False
        result = is_valid_code("101", True, global_data.naics_codes)
        assert result is False

    def test_with_accepted_blank(self):
        global_data.read_naics_codes()
        result = is_valid_code("", True, global_data.naics_codes)
        assert result is True
        result = is_valid_code(" ", True, global_data.naics_codes)
        assert result is True

    def test_with_invalid_blank(self):
        global_data.read_naics_codes()
        result = is_valid_code("", False, global_data.naics_codes)
        assert result is False
        result = is_valid_code(" ", False, global_data.naics_codes)
        assert result is False


class TestIsGreaterThan:
    def test_with_greater_min_value(self):
        assert is_greater_than("1", "2") is False

    def test_with_smaller_min_value(self):
        assert is_greater_than("1", "0") is True

    def test_with_equal_value(self):
        assert is_greater_than("1", "1") is False

    def test_with_valid_blank_value(self):
        assert is_greater_than("", "2", True) is True
        assert is_greater_than(" ", "2", True) is True

    def test_with_invalid_blank_value(self):
        assert is_greater_than("", "2") is False
        assert is_greater_than(" ", "2") is False


class TestIsGreaterThanOrEqualTo:
    def test_with_greater_min_value(self):
        assert is_greater_than_or_equal_to("1", "2") is False

    def test_with_smaller_min_value(self):
        assert is_greater_than_or_equal_to("1", "0") is True

    def test_with_equal_value(self):
        assert is_greater_than_or_equal_to("1", "1") is True

    def test_with_valid_blank_value(self):
        assert is_greater_than_or_equal_to("", "2", True) is True
        assert is_greater_than_or_equal_to(" ", "2", True) is True

    def test_with_invalid_blank_value(self):
        assert is_greater_than_or_equal_to("", "2") is False
        assert is_greater_than_or_equal_to(" ", "2") is False


class TestIsLessThan:
    def test_with_greater_max_value(self):
        assert is_less_than("1", "2") is True

    def test_with_less_max_value(self):
        assert is_less_than("1", "0") is False

    def test_with_equal_max_value(self):
        assert is_less_than("1", "1") is False

    def test_with_valid_blank_space(self):
        assert is_less_than("", "1", True) is True
        assert is_less_than(" ", "1", True) is True

    def test_with_invalid_blank_space(self):
        assert is_less_than("", "1") is False
        assert is_less_than(" ", "1") is False


class TestHasValidFormat:
    def test_with_valid_data_alphanumeric(self):
        assert has_valid_format("1", "^[0-9A-Z]$") is True
        assert has_valid_format("A", "^[0-9A-Z]$") is True
        assert has_valid_format("1ABC", "^[0-9A-Z]+$") is True

    def test_with_invalid_data_alphanumeric(self):
        assert has_valid_format("a", "^[0-9A-Z]$") is False
        assert has_valid_format("aaaa", "^[0-9A-Z]+$") is False
        assert has_valid_format("!", "^[0-9A-Z]$") is False

    def test_with_accepting_blank(self):
        assert has_valid_format("", "^[0-9A-Z]+$", True) is True

    def test_with_not_accepting_blank(self):
        assert has_valid_format("", "^[0-9A-Z]+$") is False

    # tests with different regex
    def test_with_valid_data_ip(self):
        assert (
            has_valid_format(
                "192.168.0.1", "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"
            )
            is True
        )
        assert (
            has_valid_format(
                "192.168.120.100", "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"
            )
            is True
        )

    def test_with_invalid_data_ip(self):
        assert (
            has_valid_format(
                "192.168.0.1000", "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"
            )
            is False
        )
        assert (
            has_valid_format(
                "192.168.0", "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"
            )
            is False
        )


class TestIsUniqueColumn:
    series = pd.Series(["ABC123"], name="id", index=[1])
    other_series = pd.Series(["DEF456"], name="id", index=[3])
    invalid_series = pd.Series(["ABC123", "ABC123"], name="id", index=[1, 2])
    multi_invalid_series = pd.Series(
        ["GHI123", "GHI123", "GHI123"], name="id", index=[3, 4, 5]
    )
    blank_value_series = pd.Series([""], name="id", index=[1])

    def test_with_valid_series(self):
        result = is_unique_column({"ABC123": self.series})
        assert result.values == [True]

    def test_with_multiple_valid_series(self):
        result = is_unique_column({"ABC123": self.series, "DEF456": self.other_series})
        assert result.values[0] and result.values[1]

    def test_with_invalid_series(self):
        result = is_unique_column({"ABC123": self.invalid_series})
        assert not result.values.all()

    def test_with_multiple_items_series(self):
        result = is_unique_column({"GHI123": self.multi_invalid_series})
        assert not result.values.all()

    def test_with_multiple_invalid_series(self):
        result = is_unique_column(
            {"ABC123": self.invalid_series, "GHI123": self.multi_invalid_series}
        )
        # ALL rows should be FALSE
        assert (
            not result.values[0]
            and not result.values[1]
            and not result.values[2]
            and not result.values[3]
            and not result.values[4]
        )

    def test_with_multiple_mix_series(self):
        result = is_unique_column(
            {"ABC123": self.invalid_series, "DEF456": self.other_series}
        )
        # first two rows should be FALSE and last Row should be TRUE
        assert not result.values[0] and not result.values[1] and result.values[2]

    def test_with_blank_value_series(self):
        result = is_unique_column({"": self.blank_value_series})
        assert result.values == [True]


class TestHasValidFieldsetPair:
    def test_with_correct_is_not_equal_condition(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, ""),
            "field2": (1, True, ""),
            "field3": (2, True, ""),
        }
        series = pd.Series(["0"], name="num_principal_owners", index=[1])
        groupby_values = tuple(["", "", ""])
        result1 = has_valid_fieldset_pair(
            {groupby_values: series}, condition_values, should_fieldset_key_equal_to
        )
        assert result1.values == [True]

    def test_with_correct_is_equal_condition(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, False, ""),
            "field2": (1, False, ""),
            "field3": (2, False, ""),
        }
        series = pd.Series(["0"], name="num_principal_owners", index=[1])
        groupby_values = tuple(["999", "999", "0"])
        result1 = has_valid_fieldset_pair(
            {groupby_values: series}, condition_values, should_fieldset_key_equal_to
        )
        assert result1.values == [True]

    def test_with_correct_is_equal_and_not_equal_conditions(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, "999"),
            "field2": (1, True, "999"),
            "field3": (2, True, "0"),
            "field4": (3, False, ""),
            "fiedl5": (4, False, ""),
        }

        series = pd.Series(["0"], name="num_principal_owners", index=[1])
        groupby_values = tuple(["999", "999", "0", "1", "2"])
        result1 = has_valid_fieldset_pair(
            {groupby_values: series}, condition_values, should_fieldset_key_equal_to
        )
        assert result1.values == [True]

    def test_with_value_not_in_condition_values(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, "999"),
            "field2": (1, True, "999"),
            "field3": (2, True, "0"),
            "fiedl4": (3, False, "1"),
            "field5": (4, False, "2"),
        }

        series = pd.Series(["2"], name="num_principal_owners", index=[1])
        groupby_values = tuple(["999", "999", "0", "1", "2"])
        result1 = has_valid_fieldset_pair(
            {groupby_values: series}, condition_values, should_fieldset_key_equal_to
        )
        assert result1.values == [True]

    def test_with_incorrect_is_not_equal_condition(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, ""),
            "field2": (1, True, ""),
            "field3": (2, True, ""),
        }

        series = pd.Series(["0"], name="num_principal_owners", index=[1])
        groupby_values = tuple(["999", "999", "999"])
        result1 = has_valid_fieldset_pair(
            {groupby_values: series}, condition_values, should_fieldset_key_equal_to
        )
        assert result1.values == [False]

    def test_with_incorrect_is_equal_condition(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, False, ""),
            "field2": (1, False, ""),
            "field3": (2, False, ""),
        }

        series = pd.Series(["0"], name="num_principal_owners", index=[1])
        groupby_values = tuple(["", "", ""])
        result1 = has_valid_fieldset_pair(
            {groupby_values: series}, condition_values, should_fieldset_key_equal_to
        )
        assert result1.values == [False]

    def test_with_incorrect_is_equal_and_not_equal_conditions(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, "999"),
            "field2": (1, True, "999"),
            "field3": (2, True, "0"),
            "field4": (3, False, ""),
            "field5": (4, False, ""),
        }

        series = pd.Series(["0"], name="num_principal_owners", index=[1])
        groupby_values = tuple(["", "", "3", "4", "5"])
        result1 = has_valid_fieldset_pair(
            {groupby_values: series}, condition_values, should_fieldset_key_equal_to
        )
        assert result1.values == [False]


class TestIsValidId:
    def test_with_correct_values(self):
        """when start_idx and end_idx are not set,
        if value matches containing_value, must return true"""
        assert string_contains("000TESTFIUIDDONOTUSE", "000TESTFIUIDDONOTUSE") is True
        """ when start_idx and end_idx are set, 
        if sliced value matches ontaining_value, must return true """
        assert (
            string_contains(
                "000TESTFIUIDDONOTUSEXGXVID11XTC1",
                "TEST",
                start_idx=3,
                end_idx=7,
            )
            is True
        )
        """ when only start_idx is set, 
        if sliced value matches containing_value, must return true """
        assert (
            string_contains(
                "000TESTFIUIDDONOTUSEXGXVID11XTC1",
                "TESTFIUIDDONOTUSEXGXVID11XTC1",
                start_idx=3,
            )
            is True
        )
        """ when only end_idx is set, 
        if sliced value matches containing_value, must return true """
        assert (
            string_contains(
                "000TESTFIUIDDONOTUSEXGXVID11XTC1",
                "000TESTFIUIDDONOTUSE",
                end_idx=20,
            )
            is True
        )

    def test_with_incorrect_values(self):
        """when start_idx and end_idx are not set,
        if value does not match containing_value, must return false"""
        assert string_contains("000TESTFIUIDDONOTUSE", "TESTFIUIDDONOTUSE") is False
        """ when start_idx and end_idx are set, 
        if sliced value does not match containing_value, must return false """
        assert (
            string_contains(
                "000FIUIDDONOTUSEXGXVID11XTC1", "TEST", start_idx=4, end_idx=7
            )
            is False
        )
        """ when only start_idx is set, 
        if sliced value does not match containing_value, must return false """
        assert (
            string_contains(
                "000TESTFIUIDDONOTUSEXGXVID11XTC1",
                "0TESTFIUIDDONOTUSEXGXVID11XTC1",
                start_idx=4,
            )
            is False
        )
        """ when only end_idx is set, 
        if sliced value does not match containing_value, must return false """
        assert (
            string_contains(
                "000TESTFIUIDDONOTUSEXGXVID11XTC1",
                "000TESTFIUIDDONOTUSEXGX",
                end_idx=20,
            )
            is False
        )


class TestSBLCheck:
    def test_no_id_check(self):
        id_check = SBLCheck(lambda: True, warning=True, name="Just a Warning")
        with pytest.raises(Exception) as exc:
            id_check

        assert "Each check must be assigned a `name` and an `id`." in str(exc.value)
        assert exc.type == ValueError

    def test_no_name_check(self):
        id_check = SBLCheck(lambda: True, id="00000", warning=True)
        with pytest.raises(Exception) as exc:
            id_check

        assert "Each check must be assigned a `name` and an `id`." in str(exc.value)
        assert exc.type == ValueError
