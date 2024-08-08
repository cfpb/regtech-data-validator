import polars as pl
import pandera.polars as pa

from regtech_data_validator import global_data
from regtech_data_validator.check_functions import (
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


class TestInvalidDateFormat:
    valid_date_format = "20231010"
    invalid_date_format_1 = "202310101"
    invalid_date_format_2 = "20231032"
    invalid_date_format_3 = "20231301"
    invalid_date_format_4 = "A0001201"
    invalid_date_format_5 = "2020121"
    invalid_date_format_6 = "2020120A"

    def test_with_valid_date(self):
        date_data = pa.PolarsData(pl.DataFrame({"date": self.valid_date_format}).lazy(), "date")
        results = is_date(date_data).collect()
        assert results["check_results"].eq(True).all()

    def test_with_invalid_date(self):
        date_data = pa.PolarsData(pl.DataFrame({"date": self.invalid_date_format_1}).lazy(), "date")
        results = is_date(date_data).collect()
        assert results["check_results"].eq(False).all()

    def test_with_invalid_day(self):
        date_data = pa.PolarsData(pl.DataFrame({"date": self.invalid_date_format_2}).lazy(), "date")
        results = is_date(date_data).collect()
        assert results["check_results"].eq(False).all()

    def test_with_invalid_month(self):
        date_data = pa.PolarsData(pl.DataFrame({"date": self.invalid_date_format_3}).lazy(), "date")
        results = is_date(date_data).collect()
        assert results["check_results"].eq(False).all()

    def test_with_invalid_year(self):
        date_data = pa.PolarsData(pl.DataFrame({"date": self.invalid_date_format_4}).lazy(), "date")
        results = is_date(date_data).collect()
        assert results["check_results"].eq(False).all()

    def test_with_invalid_format(self):
        date_data = pa.PolarsData(pl.DataFrame({"date": self.invalid_date_format_5}).lazy(), "date")
        results = is_date(date_data).collect()
        print(f"5 results: {results}")
        assert results["check_results"].eq(False).all()

    def test_with_invalid_type(self):
        date_data = pa.PolarsData(pl.DataFrame({"date": self.invalid_date_format_6}).lazy(), "date")
        results = is_date(date_data).collect()
        assert results["check_results"].eq(False).all()


class TestDuplicatesInField:
    def test_with_blank(self):
        unique_data = pa.PolarsData(pl.DataFrame({"unique": ""}).lazy(), "unique")
        results = is_unique_in_field(unique_data).collect()
        assert results["check_results"].eq(True).all()

    def test_with_no_duplicates(self):
        unique_data = pa.PolarsData(pl.DataFrame({"unique": "1"}).lazy(), "unique")
        results = is_unique_in_field(unique_data).collect()
        assert results["check_results"].eq(True).all()

        unique_data = pa.PolarsData(pl.DataFrame({"unique": "1;2;3;4"}).lazy(), "unique")
        results = is_unique_in_field(unique_data).collect()
        assert results["check_results"].eq(True).all()

    def test_with_duplicates(self):
        unique_data = pa.PolarsData(pl.DataFrame({"unique": "1;2;3;3;4"}).lazy(), "unique")
        results = is_unique_in_field(unique_data).collect()
        assert results["check_results"].eq(False).all()


class TestInvalidNumberOfValues:
    def test_with_in_range(self):
        count_data = pa.PolarsData(pl.DataFrame({"count": "1;2;"}).lazy(), "count")
        results = has_valid_value_count(count_data, 1, 4).collect()
        assert results["check_results"].eq(True).all()

    def test_with_lower_range_value(self):
        count_data = pa.PolarsData(pl.DataFrame({"count": "1"}).lazy(), "count")
        results = has_valid_value_count(count_data, 1, 4).collect()
        assert results["check_results"].eq(True).all()

    def test_with_invalid_lower_range_value(self):
        count_data = pa.PolarsData(pl.DataFrame({"count": "1"}).lazy(), "count")
        results = has_valid_value_count(count_data, 2, 4).collect()
        assert results["check_results"].eq(False).all()

    def test_with_upper_range_value(self):
        count_data = pa.PolarsData(pl.DataFrame({"count": "1;2"}).lazy(), "count")
        results = has_valid_value_count(count_data, 1, 2).collect()
        assert results["check_results"].eq(True).all()

    def test_with_invalid_upper_range_value(self):
        count_data = pa.PolarsData(pl.DataFrame({"count": "1;2;3;4"}).lazy(), "count")
        results = has_valid_value_count(count_data, 2, 3).collect()
        assert results["check_results"].eq(False).all()

    def test_valid_with_no_upper_bound(self):
        count_data = pa.PolarsData(pl.DataFrame({"count": "1;2;3;4"}).lazy(), "count")
        results = has_valid_value_count(count_data, 1, None).collect()
        assert results["check_results"].eq(True).all()

    def test_invalid_with_no_upper_bound(self):
        count_data = pa.PolarsData(pl.DataFrame({"count": "1"}).lazy(), "count")
        results = has_valid_value_count(count_data, 2, None).collect()
        assert results["check_results"].eq(False).all()


class TestMultiValueFieldRestriction:
    def test_with_invalid_values(self):
        assert meets_multi_value_field_restriction("1;2;3", ["2"]) is False

    def test_with_valid_length(self):
        assert meets_multi_value_field_restriction("2", ["2"]) is True
        assert meets_multi_value_field_restriction("1", ["2"]) is True

    def test_with_valid_values(self):
        assert meets_multi_value_field_restriction("1;2;3", ["4"]) is True


class TestMultiInvalidNumberOfValues:
    good_df = pa.PolarsData(pl.DataFrame({"value": "4", "other_value": "999"}).lazy(), "value")

    blank_df = pa.PolarsData(pl.DataFrame({"value": "4;1", "other_value": ""}).lazy(), "value")

    multiple_values_series = pl.Series(values=["1;2;3"], name="test_name")

    multiple_values_series_with_977 = pl.Series(values=["1;2;3;977"], name="test_name")

    multiple_values_series_with_blanks = pl.Series(values=["1;2;; ;3"], name="test_name")

    def test_inside_maxlength(self):
        good_df = pa.PolarsData(pl.DataFrame({"value": "4", "other_value": "999"}).lazy(), "value")
        results = has_valid_multi_field_value_count(good_df, max_length=5, related_fields="other_value").collect()
        assert results["check_results"].eq(True).all()

    def test_on_maxlength(self):
        good_df = pa.PolarsData(pl.DataFrame({"value": "4", "other_value": "999"}).lazy(), "value")
        results = has_valid_multi_field_value_count(good_df, max_length=2, related_fields="other_value").collect()
        assert results["check_results"].eq(True).all()

    def test_with_blank(self):
        blank_df = pa.PolarsData(pl.DataFrame({"value": "4;1", "other_value": ""}).lazy(), "value")
        results = has_valid_multi_field_value_count(blank_df, max_length=2, related_fields="other_value").collect()
        assert results["check_results"].eq(True).all()

    def test_invalid_length_with_blank(self):
        blank_df = pa.PolarsData(pl.DataFrame({"value": "4;1", "other_value": ""}).lazy(), "value")
        results = has_valid_multi_field_value_count(blank_df, max_length=1, related_fields="other_value").collect()
        assert results["check_results"].eq(False).all()

    def test_invalid_length_with_blank_and_ignored_values(self):
        blank_df = pa.PolarsData(pl.DataFrame({"value": "4;1;977", "other_value": ""}).lazy(), "value")
        results = has_valid_multi_field_value_count(
            blank_df, max_length=1, ignored_values={"977"}, related_fields="other_value"
        ).collect()
        assert results["check_results"].eq(False).all()

    def test_valid_length_with_blank_and_ignored_values(self):
        blank_df = pa.PolarsData(pl.DataFrame({"value": "4;1;977", "other_value": ""}).lazy(), "value")
        results = has_valid_multi_field_value_count(
            blank_df, max_length=2, ignored_values={"977"}, related_fields="other_value"
        ).collect()
        assert results["check_results"].eq(True).all()

    def test_outside_maxlength(self):
        max_df = pa.PolarsData(pl.DataFrame({"value": "4", "other_value": "999"}).lazy(), "value")
        results = has_valid_multi_field_value_count(max_df, max_length=1, related_fields="other_value").collect()
        assert results["check_results"].eq(False).all()

    def test_valid_length_with_multi(self):
        multi_df = pa.PolarsData(pl.DataFrame({"value": "4;1", "other_value": "1;2;3"}).lazy(), "value")
        results = has_valid_multi_field_value_count(multi_df, max_length=5, related_fields="other_value").collect()
        assert results["check_results"].eq(True).all()

    def test_invalid_length_with_multi(self):
        multi_df = pa.PolarsData(pl.DataFrame({"value": "4;1", "other_value": "1;2;3"}).lazy(), "value")
        results = has_valid_multi_field_value_count(multi_df, max_length=4, related_fields="other_value").collect()
        assert results["check_results"].eq(False).all()

    def test_valid_length_with_ignored_values(self):
        multi_df = pa.PolarsData(pl.DataFrame({"value": "4;1", "other_value": "1;2;3;977"}).lazy(), "value")
        results = has_valid_multi_field_value_count(
            multi_df, max_length=5, ignored_values={"977"}, related_fields="other_value"
        ).collect()
        assert results["check_results"].eq(True).all()

        multi_df = pa.PolarsData(pl.DataFrame({"value": "4;1;977", "other_value": "1;2;3;977"}).lazy(), "value")
        results = has_valid_multi_field_value_count(
            multi_df, max_length=5, ignored_values={"977"}, related_fields="other_value"
        ).collect()
        assert results["check_results"].eq(True).all()

    def test_invalid_length_with_ignored_values(self):
        multi_df = pa.PolarsData(pl.DataFrame({"value": "4;1", "other_value": "1;2;3;977"}).lazy(), "value")
        results = has_valid_multi_field_value_count(
            multi_df, max_length=4, ignored_values={"977"}, related_fields="other_value"
        ).collect()
        assert results["check_results"].eq(False).all()

        multi_df = pa.PolarsData(pl.DataFrame({"value": "4;1;977", "other_value": "1;2;3;977"}).lazy(), "value")
        results = has_valid_multi_field_value_count(
            multi_df, max_length=4, ignored_values={"977"}, related_fields="other_value"
        ).collect()
        assert results["check_results"].eq(False).all()

    def test_valid_length_with_blank_values(self):
        has_blank_df = pa.PolarsData(pl.DataFrame({"value": "4;1", "other_value": "1;2;; ;3"}).lazy(), "value")
        results = has_valid_multi_field_value_count(has_blank_df, max_length=5, related_fields="other_value").collect()
        assert results["check_results"].eq(True).all()

        has_blank_df = pa.PolarsData(pl.DataFrame({"value": "4;1;977", "other_value": "1;2;; ;3;977"}).lazy(), "value")
        results = has_valid_multi_field_value_count(
            has_blank_df, max_length=5, ignored_values={"977"}, related_fields="other_value"
        ).collect()
        assert results["check_results"].eq(True).all()

    def test_invalid_length_with_blank_values(self):
        has_blank_df = pa.PolarsData(pl.DataFrame({"value": "4;1", "other_value": "1;2;; ;3"}).lazy(), "value")
        results = has_valid_multi_field_value_count(has_blank_df, max_length=4, related_fields="other_value").collect()
        assert results["check_results"].eq(False).all()

        has_blank_df = pa.PolarsData(pl.DataFrame({"value": "4;1;977", "other_value": "1;2;; ;3;977"}).lazy(), "value")
        results = has_valid_multi_field_value_count(
            has_blank_df, max_length=4, ignored_values={"977"}, related_fields="other_value"
        ).collect()
        assert results["check_results"].eq(False).all()


class TestInvalidEnumValue:
    def test_with_valid_enum_values(self):
        accepted_values = ["1", "2"]
        check_df = pa.PolarsData(pl.DataFrame({"value": "1;2"}).lazy(), "value")
        results = is_valid_enum(check_df, accepted_values).collect()
        assert results["check_results"].eq(True).all()

    def test_with_is_valid_enums(self):
        accepted_values = ["1", "2"]
        check_df = pa.PolarsData(pl.DataFrame({"value": "0;3"}).lazy(), "value")
        results = is_valid_enum(check_df, accepted_values).collect()
        assert results["check_results"].eq(False).all()

    def test_with_valid_blank(self):
        accepted_values = ["1", "2"]
        check_df = pa.PolarsData(pl.DataFrame({"value": ""}).lazy(), "value")
        results = is_valid_enum(check_df, accepted_values, accept_blank=True).collect()
        assert results["check_results"].eq(True).all()

    def test_with_invalid_blank(self):
        accepted_values = ["1", "2"]
        check_df = pa.PolarsData(pl.DataFrame({"value": ""}).lazy(), "value")
        results = is_valid_enum(check_df, accepted_values).collect()
        assert results["check_results"].eq(False).all()


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
        condition_values: set[str] = {"900"}
        check_df = pa.PolarsData(pl.DataFrame({"ct_loan_term_flag": "988", "ct_loan_term": ""}).lazy(), "ct_loan_term")
        results = has_no_conditional_field_conflict(
            check_df, condition_values=condition_values, related_fields="ct_loan_term_flag"
        ).collect()
        assert results["check_results"].eq(True).all()

        # if ct_loan_term_flag == 900 then ct_loan_term must not be blank
        check_df = pa.PolarsData(
            pl.DataFrame({"ct_loan_term_flag": "900", "ct_loan_term": "36"}).lazy(), "ct_loan_term"
        )
        results = has_no_conditional_field_conflict(
            check_df, condition_values=condition_values, related_fields="ct_loan_term_flag"
        ).collect()
        assert results["check_results"].eq(True).all()

    def test_conditional_field_conflict_incorrect(self):
        # if ct_loan_term_flag != 900 then ct_loan_term must be blank
        # in this test, ct_loan_term_flag is not 900 and ct_loan_term is
        # NOT blank, so must return False
        condition_values: set[str] = {"900"}
        check_df = pa.PolarsData(
            pl.DataFrame({"ct_loan_term_flag": "988", "ct_loan_term": "36"}).lazy(), "ct_loan_term"
        )
        results = has_no_conditional_field_conflict(
            check_df, condition_values=condition_values, related_fields="ct_loan_term_flag"
        ).collect()
        assert results["check_results"].eq(False).all()

        # if ct_loan_term_flag == 900 then ct_loan_term must not be blank
        # in this test ct_loan_term is blank, so must return False
        check_df = pa.PolarsData(pl.DataFrame({"ct_loan_term_flag": "900", "ct_loan_term": ""}).lazy(), "ct_loan_term")
        results = has_no_conditional_field_conflict(
            check_df, condition_values=condition_values, related_fields="ct_loan_term_flag"
        ).collect()
        assert results["check_results"].eq(False).all()

        check_df = pa.PolarsData(pl.DataFrame({"ct_loan_term_flag": "900", "ct_loan_term": " "}).lazy(), "ct_loan_term")
        results = has_no_conditional_field_conflict(
            check_df, condition_values=condition_values, related_fields="ct_loan_term_flag"
        ).collect()
        assert results["check_results"].eq(False).all()


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
        check_df = pa.PolarsData(
            pl.DataFrame({"ct_credit_product": "1", "pricing_mca_addcost_flag": "900"}).lazy(),
            "pricing_mca_addcost_flag",
        )
        results = has_valid_enum_pair(
            check_df, conditions=pricing_mca_addcost_flag_conditions, related_fields="ct_credit_product"
        ).collect()
        assert results["check_results"].eq(True).all()

        # If ct_credit_product == 988 then pricing_mca_addcost_flag must equal 999
        check_df = pa.PolarsData(
            pl.DataFrame({"ct_credit_product": "988", "pricing_mca_addcost_flag": "999"}).lazy(),
            "pricing_mca_addcost_flag",
        )
        results = has_valid_enum_pair(
            check_df, conditions=pricing_mca_addcost_flag_conditions, related_fields="ct_credit_product"
        ).collect()
        assert results["check_results"].eq(True).all()

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
        check_df = pa.PolarsData(pl.DataFrame({"action_taken": "3", "denial_reasons": "988"}).lazy(), "denial_reasons")
        results = has_valid_enum_pair(
            check_df, conditions=denial_reasons_conditions, related_fields="action_taken"
        ).collect()
        assert results["check_results"].eq(True).all()

        # If action_taken is NOT 3, and denial_reasons must equal 999
        check_df = pa.PolarsData(pl.DataFrame({"action_taken": "1", "denial_reasons": "999"}).lazy(), "denial_reasons")
        results = has_valid_enum_pair(
            check_df, conditions=denial_reasons_conditions, related_fields="action_taken"
        ).collect()
        assert results["check_results"].eq(True).all()

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
        check_df = pa.PolarsData(
            pl.DataFrame({"ct_credit_product": "1", "pricing_mca_addcost_flag": "999"}).lazy(),
            "pricing_mca_addcost_flag",
        )
        results = has_valid_enum_pair(
            check_df, conditions=pricing_mca_addcost_flag_conditions, related_fields="ct_credit_product"
        ).collect()
        assert results["check_results"].eq(False).all()

        # If ct_credit_product == 988 then pricing_mca_addcost_flag must equal 999
        check_df = pa.PolarsData(
            pl.DataFrame({"ct_credit_product": "988", "pricing_mca_addcost_flag": "900"}).lazy(),
            "pricing_mca_addcost_flag",
        )
        results = has_valid_enum_pair(
            check_df, conditions=pricing_mca_addcost_flag_conditions, related_fields="ct_credit_product"
        ).collect()
        assert results["check_results"].eq(False).all()

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
        check_df = pa.PolarsData(pl.DataFrame({"action_taken": "3", "denial_reasons": "999"}).lazy(), "denial_reasons")
        results = has_valid_enum_pair(
            check_df, conditions=denial_reasons_conditions, related_fields="action_taken"
        ).collect()
        assert results["check_results"].eq(False).all()

        # If action_taken is NOT 3, and denial_reasons must equal 999
        check_df = pa.PolarsData(pl.DataFrame({"action_taken": "1", "denial_reasons": "988"}).lazy(), "denial_reasons")
        results = has_valid_enum_pair(
            check_df, conditions=denial_reasons_conditions, related_fields="action_taken"
        ).collect()
        assert results["check_results"].eq(False).all()


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
        result = is_valid_code("111", False, global_data.naics_codes)
        assert result is True
        result = is_valid_code("111", True, global_data.naics_codes)
        assert result is True

    def test_with_invalid_code(self):
        result = is_valid_code("101", False, global_data.naics_codes)
        assert result is False
        result = is_valid_code("101", True, global_data.naics_codes)
        assert result is False

    def test_with_accepted_blank(self):
        result = is_valid_code("", True, global_data.naics_codes)
        assert result is True
        result = is_valid_code(" ", True, global_data.naics_codes)
        assert result is True

    def test_with_invalid_blank(self):
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

    def test_with_larger_numbers(self):
        assert is_greater_than("715", "1200") is False
        assert is_greater_than("1240", "1200") is True
        assert is_greater_than("125.9", "130") is False


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

    def test_with_larger_numbers(self):
        assert is_greater_than_or_equal_to("715", "1200") is False
        assert is_greater_than_or_equal_to("1240", "1200") is True
        assert is_greater_than_or_equal_to("1200", "1200") is True
        assert is_greater_than_or_equal_to("125.9", "130") is False


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

    def test_with_larger_numbers(self):
        assert is_less_than("715", "1200") is True
        assert is_less_than("1240", "1200") is False
        assert is_less_than("125.9", "130") is True


class TestHasValidFormat:
    def test_with_valid_data_alphanumeric(self):
        check_df = pa.PolarsData(pl.DataFrame({"value": "1"}).lazy(), "value")
        results = has_valid_format(check_df, regex="^[0-9A-Z]$").collect()
        assert results["check_results"].eq(True).all()

        check_df = pa.PolarsData(pl.DataFrame({"value": "A"}).lazy(), "value")
        results = has_valid_format(check_df, regex="^[0-9A-Z]$").collect()
        assert results["check_results"].eq(True).all()

        check_df = pa.PolarsData(pl.DataFrame({"value": "1ABC"}).lazy(), "value")
        results = has_valid_format(check_df, regex="^[0-9A-Z]+$").collect()
        assert results["check_results"].eq(True).all()

    def test_with_invalid_data_alphanumeric(self):
        check_df = pa.PolarsData(pl.DataFrame({"value": "a"}).lazy(), "value")
        results = has_valid_format(check_df, regex="^[0-9A-Z]$").collect()
        assert results["check_results"].eq(False).all()

        check_df = pa.PolarsData(pl.DataFrame({"value": "aaaa"}).lazy(), "value")
        results = has_valid_format(check_df, regex="^[0-9A-Z]+$").collect()
        assert results["check_results"].eq(False).all()

        check_df = pa.PolarsData(pl.DataFrame({"value": "!"}).lazy(), "value")
        results = has_valid_format(check_df, regex="^[0-9A-Z]$").collect()
        assert results["check_results"].eq(False).all()

    def test_with_accepting_blank(self):
        check_df = pa.PolarsData(pl.DataFrame({"value": ""}).lazy(), "value")
        results = has_valid_format(check_df, regex="^[0-9A-Z]+$", accept_blank=True).collect()
        assert results["check_results"].eq(True).all()

    def test_with_not_accepting_blank(self):
        check_df = pa.PolarsData(pl.DataFrame({"value": ""}).lazy(), "value")
        results = has_valid_format(check_df, regex="^[0-9A-Z]+$").collect()
        assert results["check_results"].eq(False).all()

    # tests with different regex
    def test_with_valid_data_ip(self):
        check_df = pa.PolarsData(pl.DataFrame({"value": "192.168.0.1"}).lazy(), "value")
        results = has_valid_format(check_df, regex=r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$").collect()
        assert results["check_results"].eq(True).all()

        check_df = pa.PolarsData(pl.DataFrame({"value": "192.168.120.100"}).lazy(), "value")
        results = has_valid_format(check_df, regex=r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$").collect()
        assert results["check_results"].eq(True).all()

    def test_with_invalid_data_ip(self):
        check_df = pa.PolarsData(pl.DataFrame({"value": "192.168.0.1000"}).lazy(), "value")
        results = has_valid_format(check_df, regex=r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$").collect()
        assert results["check_results"].eq(False).all()

        check_df = pa.PolarsData(pl.DataFrame({"value": "192.168.0"}).lazy(), "value")
        results = has_valid_format(check_df, regex=r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$").collect()
        assert results["check_results"].eq(False).all()


class TestIsUniqueColumn:
    series = pl.Series(values=["ABC123"], name="id")
    other_series = pl.Series(values=["DEF456"], name="id")
    invalid_series = pl.Series(values=["ABC123", "ABC123"], name="id")
    multi_invalid_series = pl.Series(values=["GHI123", "GHI123", "GHI123"], name="id")
    blank_value_series = pl.Series(values=[""], name="id")

    def test_with_valid_series(self):
        check_df = pa.PolarsData(pl.DataFrame({"uid": "ABC123"}).lazy(), "uid")
        results = is_unique_column(check_df).collect()
        assert results["check_results"].eq(True).all()

    def test_with_multiple_valid_series(self):
        check_df = pa.PolarsData(pl.DataFrame({"uid": ["ABC123", "ABC456"]}).lazy(), "uid")
        results = is_unique_column(check_df).collect()
        assert results["check_results"].eq(True).all()

    def test_with_invalid_series(self):
        check_df = pa.PolarsData(pl.DataFrame({"uid": ["ABC123", "ABC123"]}).lazy(), "uid")
        results = is_unique_column(check_df).collect()
        assert results["check_results"].eq(False).all()

    def test_with_multiple_items_series(self):
        check_df = pa.PolarsData(pl.DataFrame({"uid": ["ABC123", "ABC456", "ABC123", "ABC456"]}).lazy(), "uid")
        results = is_unique_column(check_df).collect()
        assert results["check_results"].eq(False).all()

    def test_with_multiple_mix_series(self):
        check_df = pa.PolarsData(pl.DataFrame({"uid": ["ABC123", "ABC456", "ABC123"]}).lazy(), "uid")
        results = is_unique_column(check_df).collect()
        assert not results["check_results"][0] and results["check_results"][1] and not results["check_results"][2]

    def test_with_blank_value_series(self):
        check_df = pa.PolarsData(pl.DataFrame({"uid": [""]}).lazy(), "uid")
        results = is_unique_column(check_df).collect()
        assert results["check_results"].eq(True).all()


class TestHasValidFieldsetPair:
    def test_with_correct_is_not_equal_condition(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, ""),
            "field2": (1, True, ""),
            "field3": (2, True, ""),
        }
        check_data = {"num_principal_owners": "0", "field1": "", "field2": "", "field3": ""}

        check_df = pa.PolarsData(pl.DataFrame(check_data).lazy(), "num_principal_owners")
        results = has_valid_fieldset_pair(
            check_df,
            condition_values=condition_values,
            related_fields=["field1", "field2", "field3"],
            should_fieldset_key_equal_to=should_fieldset_key_equal_to,
        ).collect()
        assert results["check_results"].eq(True).all()

    def test_with_correct_is_equal_condition(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, False, ""),
            "field2": (1, False, ""),
            "field3": (2, False, ""),
        }
        check_data = {"num_principal_owners": "0", "field1": "999", "field2": "999", "field3": "0"}

        check_df = pa.PolarsData(pl.DataFrame(check_data).lazy(), "num_principal_owners")
        results = has_valid_fieldset_pair(
            check_df,
            condition_values=condition_values,
            related_fields=["field1", "field2", "field3"],
            should_fieldset_key_equal_to=should_fieldset_key_equal_to,
        ).collect()
        assert results["check_results"].eq(True).all()

    def test_with_correct_is_equal_and_not_equal_conditions(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, "999"),
            "field2": (1, True, "999"),
            "field3": (2, True, "0"),
            "field4": (3, False, ""),
            "field5": (4, False, ""),
        }
        check_data = {
            "num_principal_owners": "0",
            "field1": "999",
            "field2": "999",
            "field3": "0",
            "field4": "1",
            "field5": "2",
        }

        check_df = pa.PolarsData(pl.DataFrame(check_data).lazy(), "num_principal_owners")
        results = has_valid_fieldset_pair(
            check_df,
            condition_values=condition_values,
            related_fields=["field1", "field2", "field3", "field4", "field5"],
            should_fieldset_key_equal_to=should_fieldset_key_equal_to,
        ).collect()
        assert results["check_results"].eq(True).all()

    def test_with_value_not_in_condition_values(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, "999"),
            "field2": (1, True, "999"),
            "field3": (2, True, "0"),
            "field4": (3, False, "1"),
            "field5": (4, False, "2"),
        }
        check_data = {
            "num_principal_owners": "2",
            "field1": "999",
            "field2": "999",
            "field3": "0",
            "field4": "1",
            "field5": "2",
        }

        check_df = pa.PolarsData(pl.DataFrame(check_data).lazy(), "num_principal_owners")
        results = has_valid_fieldset_pair(
            check_df,
            condition_values=condition_values,
            related_fields=["field1", "field2", "field3", "field4", "field5"],
            should_fieldset_key_equal_to=should_fieldset_key_equal_to,
        ).collect()
        assert results["check_results"].eq(True).all()

    def test_with_incorrect_is_not_equal_condition(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, ""),
            "field2": (1, True, ""),
            "field3": (2, True, ""),
        }
        check_data = {"num_principal_owners": "0", "field1": "999", "field2": "999", "field3": "999"}

        check_df = pa.PolarsData(pl.DataFrame(check_data).lazy(), "num_principal_owners")
        results = has_valid_fieldset_pair(
            check_df,
            condition_values=condition_values,
            related_fields=["field1", "field2", "field3"],
            should_fieldset_key_equal_to=should_fieldset_key_equal_to,
        ).collect()
        assert results["check_results"].eq(False).all()

    def test_with_incorrect_is_equal_condition(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, False, ""),
            "field2": (1, False, ""),
            "field3": (2, False, ""),
        }
        check_data = {"num_principal_owners": "0", "field1": "", "field2": "", "field3": ""}

        check_df = pa.PolarsData(pl.DataFrame(check_data).lazy(), "num_principal_owners")
        results = has_valid_fieldset_pair(
            check_df,
            condition_values=condition_values,
            related_fields=["field1", "field2", "field3"],
            should_fieldset_key_equal_to=should_fieldset_key_equal_to,
        ).collect()
        assert results["check_results"].eq(False).all()

    def test_with_incorrect_is_equal_and_not_equal_conditions(self):
        condition_values = ["0", ""]
        should_fieldset_key_equal_to = {
            "field1": (0, True, "999"),
            "field2": (1, True, "999"),
            "field3": (2, True, "0"),
            "field4": (3, False, ""),
            "field5": (4, False, ""),
        }
        check_data = {
            "num_principal_owners": "0",
            "field1": "",
            "field2": "",
            "field3": "3",
            "field4": "4",
            "field5": "5",
        }

        check_df = pa.PolarsData(pl.DataFrame(check_data).lazy(), "num_principal_owners")
        results = has_valid_fieldset_pair(
            check_df,
            condition_values=condition_values,
            related_fields=["field1", "field2", "field3", "field4", "field5"],
            should_fieldset_key_equal_to=should_fieldset_key_equal_to,
        ).collect()
        assert results["check_results"].eq(False).all()


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
        assert string_contains("000FIUIDDONOTUSEXGXVID11XTC1", "TEST", start_idx=4, end_idx=7) is False
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
