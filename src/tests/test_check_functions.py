import pandas as pd

from validator import global_data
from validator.check_functions import (
    denial_reasons_conditional_enum_value,
    has_correct_length,
    has_no_conditional_field_conflict,
    has_valid_enum_pair,
    has_valid_multi_field_value_count,
    has_valid_value_count,
    is_date,
    is_fieldset_equal_to,
    is_fieldset_not_equal_to,
    is_greater_than,
    is_greater_than_or_equal_to,
    is_less_than,
    is_number,
    is_unique_in_field,
    is_valid_code,
    is_valid_enum,
    meets_multi_value_field_restriction,
)


class TestInvalidDateFormat:
    valid_date_format = "20231010"
    invalid_date_format_1 = "202310101"
    invalid_date_format_2 = "20231032"
    invalid_date_format_3 = "20231301"
    invalid_date_format_4 = "00001201"
    invalid_date_format_5 = "2020121"
    invalid_date_format_6 = "2020120A"

    def test_with_valid_date(self):
        assert is_date(self.valid_date_format) == True

    def test_with_invalid_date(self):
        assert is_date(self.invalid_date_format_1) == False

    def test_with_invalid_day(self):
        assert is_date(self.invalid_date_format_2) == False

    def test_with_invalid_month(self):
        assert is_date(self.invalid_date_format_3) == False

    def test_with_invalid_year(self):
        assert is_date(self.invalid_date_format_4) == False

    def test_with_invalid_format(self):
        assert is_date(self.invalid_date_format_5) == False

    def test_with_invalid_type(self):
        assert is_date(self.invalid_date_format_6) == False


class TestDenialReasonsConditionalEnumValue:
    def test_with_correct_action_taken_and_denial_reasons(self):
        # if action taken != 3 then denial_reasons must be 999
        series = pd.Series(["999"], name="denial_reasons", index=[2])
        result = denial_reasons_conditional_enum_value({"4": series})
        assert result.values == [True]

        # if action taken = 3 then denial_reasons must not contains 999
        series_2 = pd.Series(["997"], name="denial_reasons", index=[2])
        result_2 = denial_reasons_conditional_enum_value({"3": series_2})
        assert result_2.values == [True]

        # if action taken = 3 then denial_reasons must not contains 999 and
        # can have multiple values
        series_3 = pd.Series(["997;1"], name="denial_reasons", index=[2])
        result_3 = denial_reasons_conditional_enum_value({"3": series_3})
        assert result_3.values == [True]

    def test_with_incorrect_action_taken_and_denial_reasons(self):
        # if action taken != 3 and denial_reasons is not 999
        #  , it should fail
        series = pd.Series(["997"], name="denial_reasons", index=[2])
        result = denial_reasons_conditional_enum_value({"4": series})
        assert result.values == [False]

        # if action taken = 3 and denial_reasons is 999
        #  , it should fail
        series_2 = pd.Series(["999"], name="denial_reasons", index=[2])
        result_2 = denial_reasons_conditional_enum_value({"3": series_2})
        assert result_2.values == [False]

        # if action taken = 3 and denial_reasons is 999
        #  , it should fail
        series_3 = pd.Series(["997;999"], name="denial_reasons", index=[2])
        result_3 = denial_reasons_conditional_enum_value({"3": series_3})
        assert result_3.values == [False]

        # if action taken = 3 then denial_reasons
        # can have multiple values but can not contains 999
        series_4 = pd.Series(["997;1;999"], name="denial_reasons", index=[2])
        result_4 = denial_reasons_conditional_enum_value({"3": series_4})
        assert result_4.values == [False]


class TestDuplicatesInField:
    def test_with_blank(self):
        assert is_unique_in_field("") == True

    def test_with_no_duplicates(self):
        assert is_unique_in_field("1") == True
        assert is_unique_in_field("1;2;3;4") == True

    def test_with_duplicates(self):
        assert is_unique_in_field("1;2;3;3;4") == False


class TestInvalidNumberOfValues:
    def test_with_in_range(self):
        assert has_valid_value_count("1;2;", 1, 4) == True

    def test_with_lower_range_value(self):
        assert has_valid_value_count("1", 1, 4) == True

    def test_with_invalid_lower_range_value(self):
        assert has_valid_value_count("1", 2, 4) == False

    def test_with_upper_range_value(self):
        assert has_valid_value_count("1;2", 1, 2) == True

    def test_with_invalid_upper_range_value(self):
        assert has_valid_value_count("1;2;3;4", 2, 3) == False

    def test_valid_with_no_upper_bound(self):
        assert has_valid_value_count("1;2;3;4", 1, None) == True

    def test_invalid_with_no_upper_bound(self):
        assert has_valid_value_count("1", 2, None) == False


class TestMultiValueFieldRestriction:
    def test_with_invalid_values(self):
        assert meets_multi_value_field_restriction("1;2;3", ["2"]) == False

    def test_with_valid_length(self):
        assert meets_multi_value_field_restriction("2", ["2"]) == True
        assert meets_multi_value_field_restriction("1", ["2"]) == True

    def test_with_valid_values(self):
        assert meets_multi_value_field_restriction("1;2;3", ["4"]) == True


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

    def test_inside_maxlength(self):
        result = has_valid_multi_field_value_count({"4": self.series}, 5)
        assert result.values == [True]

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
        assert result == True

    def test_with_is_valid_enums(self):
        accepted_values = ["1", "2"]
        result = is_valid_enum("0;3", accepted_values)
        assert result == False

    def test_with_valid_blank(self):
        accepted_values = ["1", "2"]
        result = is_valid_enum("", accepted_values, True)
        assert result == True

    def test_with_invalid_blank(self):
        accepted_values = ["1", "2"]
        result = is_valid_enum("", accepted_values)
        assert result == False


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
        assert result == False

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
        # in this test, ct_loan_term_flag is not 900 and ct_loan_term is NOT blank, so must return False
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
        # If there is only one condition:
        """
        IF ct_credit_product is not equal to 7, 8, OR 977 THEN
            IF pricing_mca_addcost_flag is not equal to 999 THEN
                Error
            ENDIF
        ENDIF
        """

        pricing_mca_addcost_flag_conditions = [
            {
                "condition_values": {"7", "8", "977"},
                "is_equal_condition": False,
                "target_value": "999",
                "is_equal_target": False,
            }
        ]

        # If ct_credit_product != 7, 8, or 977 and pricing_mca_addcost_flag = 999, return True
        pricing_mca_addcost_flag_series_1 = pd.Series(
            ["999"], name="pricing_mca_addcost_flag", index=[2]
        )

        ct_credit_product_1 = "5"

        pricing_mca_addcost_flag_result_1 = has_valid_enum_pair(
            {ct_credit_product_1: pricing_mca_addcost_flag_series_1},
            pricing_mca_addcost_flag_conditions,
        )
        assert pricing_mca_addcost_flag_result_1.values == [True]

        # If ct_credit_product == 7, 8, or 977 then return True regardless of whether pricing_mca_addcost_flag = 999 or Not
        ct_credit_product_2 = "7;8;977"
        # Case when pricing_mca_addcost_flag = 999
        pricing_mca_addcost_flag_series_2 = pd.Series(
            ["999"], name="pricing_mca_addcost_flag", index=[2]
        )
        pricing_mca_addcost_flag_result_2 = has_valid_enum_pair(
            {ct_credit_product_2: pricing_mca_addcost_flag_series_2},
            pricing_mca_addcost_flag_conditions,
        )
        assert pricing_mca_addcost_flag_result_2.values == [True]

        # Case when pricing_mca_addcost_flag != 999
        pricing_mca_addcost_flag_series_3 = pd.Series(
            ["988"], name="pricing_mca_addcost_flag", index=[2]
        )
        pricing_mca_addcost_flag_result_3 = has_valid_enum_pair(
            {ct_credit_product_2: pricing_mca_addcost_flag_series_3},
            pricing_mca_addcost_flag_conditions,
        )
        assert pricing_mca_addcost_flag_result_3.values == [True]

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
                "is_equal_target": True,
            },
            {
                "condition_values": {"3"},
                "is_equal_condition": False,
                "target_value": "999",
                "is_equal_target": False,
            },
        ]
        # If action_taken is 3, and denial_reasons != 999, must return True
        denial_reasons_1 = pd.Series(["988"], name="denial_reasons", index=[2])
        action_taken_1 = "3"

        denial_reason_result_1 = has_valid_enum_pair(
            {action_taken_1: denial_reasons_1}, denial_reasons_conditions
        )
        assert denial_reason_result_1.values == [True]

        # If action_taken is NOT 3, and denial_reasons == 999, must return True
        denial_reasons_2 = pd.Series(["999"], name="denial_reasons", index=[2])
        action_taken_2 = "1"
        denial_reason_result_2 = has_valid_enum_pair(
            {action_taken_2: denial_reasons_2}, denial_reasons_conditions
        )
        assert denial_reason_result_2.values == [True]

    def test_enum_value_confict_incorrect(self):
        # If there is only one condition:
        """
        IF ct_credit_product is not equal to 7, 8, OR 977 THEN
            IF pricing_mca_addcost_flag is not equal to 999 THEN
                Error
            ENDIF
        ENDIF
        """

        pricing_mca_addcost_flag_conditions = [
            {
                "condition_values": {"7", "8", "977"},
                "is_equal_condition": False,
                "target_value": "999",
                "is_equal_target": False,
            }
        ]

        # If ct_credit_product != 7, 8, or 977 and pricing_mca_addcost_flag != 999, return False
        pricing_mca_addcost_flag_series_1 = pd.Series(
            ["988"], name="pricing_mca_addcost_flag", index=[2]
        )
        ct_credit_product_1 = "5"

        pricing_mca_addcost_flag_result_1 = has_valid_enum_pair(
            {ct_credit_product_1: pricing_mca_addcost_flag_series_1},
            pricing_mca_addcost_flag_conditions,
        )
        assert pricing_mca_addcost_flag_result_1.values == [False]

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
                "is_equal_target": True,
            },
            {
                "condition_values": {"3"},
                "is_equal_condition": False,
                "target_value": "999",
                "is_equal_target": False,
            },
        ]
        # If action_taken is 3, and denial_reasons == 999, must return False
        denial_reasons_1 = pd.Series(["999"], name="denial_reasons", index=[2])
        action_taken_1 = "3"

        denial_reason_result_1 = has_valid_enum_pair(
            {action_taken_1: denial_reasons_1}, denial_reasons_conditions
        )
        print(denial_reason_result_1.values)
        assert denial_reason_result_1.values == [False]

        # If action_taken is NOT 3, and denial_reasons != 999, must return False
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


class TestIsFieldsetEqualTo:
    def test_with_correct_values(self):
        target_values = ["999", "999", "999", "999", "", "", ""]
        condition_values = ["3", "4", "5"]

        series = pd.Series(["3"], name="action_taken", index=[1])
        values = tuple(["999", "999", "999", "999", "", "", ""])
        result1 = is_fieldset_equal_to(
            {values: series}, condition_values, target_values
        )
        assert result1.values == [True]

    def test_with_correct_other_values(self):
        target_values = ["999", "999", "999", "999", "", "", ""]
        condition_values = ["3", "4", "5"]

        series = pd.Series(["2"], name="action_taken", index=[1])
        values = tuple(["999", "999", "999", "999", "", "", ""])
        result1 = is_fieldset_equal_to(
            {values: series}, condition_values, target_values
        )
        assert result1.values == [True]

    def test_with_incorrect_values(self):
        target_values = ["999", "999", "999", "999", "", "", ""]
        condition_values = ["3", "4", "5"]

        series = pd.Series(["3"], name="action_taken", index=[1])
        values = tuple(["999", "999", "999", "", "", "", ""])
        result1 = is_fieldset_equal_to(
            {values: series}, condition_values, target_values
        )
        assert result1.values == [False]

    def test_with_incorrect_other_values(self):
        target_values = ["999", "999", "999", "999", "", "", ""]
        condition_values = ["3", "4", "5"]

        series = pd.Series(["2"], name="action_taken", index=[1])
        values = tuple(["999", "999", "999", "", "", "", ""])
        result1 = is_fieldset_equal_to(
            {values: series}, condition_values, target_values
        )
        assert result1.values == [True]


class TestIsFieldsetNotEqualTo:
    def test_with_all_equal_values(self):
        target_values = ["", "", "", "999", "999"]
        condition_values = ["1", "2"]

        series = pd.Series(["1"], name="action_taken", index=[1])
        values = tuple(["", "", "", "999", "999"])
        result1 = is_fieldset_not_equal_to(
            {values: series}, condition_values, target_values
        )
        assert result1.values == [False]

    def test_with_some_equal_values(self):
        target_values = ["1", "", "", "999", ""]
        condition_values = ["1", "2"]

        series = pd.Series(["1"], name="action_taken", index=[1])
        values = tuple(["", "", "", "999", "999"])
        result1 = is_fieldset_not_equal_to(
            {values: series}, condition_values, target_values
        )
        assert result1.values == [False]

    def test_with_none_equal_values(self):
        target_values = ["1", "2", "3", "997", "997"]
        condition_values = ["1", "2"]

        series = pd.Series(["1"], name="action_taken", index=[1])
        values = tuple(["", "", "", "999", "999"])
        result1 = is_fieldset_not_equal_to(
            {values: series}, condition_values, target_values
        )
        assert result1.values == [True]

    def test_with_different_conditional_values(self):
        target_values = ["", "", "", "999", "999"]
        condition_values = ["1", "2"]

        series = pd.Series(["4"], name="action_taken", index=[1])
        values = tuple(["", "", "", "999", "999"])
        result1 = is_fieldset_not_equal_to(
            {values: series}, condition_values, target_values
        )
        assert result1.values == [True]


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
