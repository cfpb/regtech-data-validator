import pandas as pd

from validator import global_data
from validator.check_functions import (denial_reasons_conditional_enum_value,
                                       has_correct_length,
                                       has_no_conditional_field_conflict,
                                       has_valid_enum_pair,
                                       has_valid_multi_field_value_count,
                                       has_valid_value_count, is_date,
                                       is_fieldset_equal_to,
                                       is_fieldset_not_equal_to, is_number,
                                       is_unique_in_field, is_valid_code,
                                       is_valid_enum,
                                       meets_multi_value_field_restriction)


class TestInvalidDateFormat:
    valid_date_format = "20231010"
    invalid_date_format_1 = "202310101"
    invalid_date_format_2 = "20231032"
    invalid_date_format_3 = "20231301"
    invalid_date_format_4 = "00001201"
    
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


class TestDenialReasonsConditionalEnumValue:
    def test_with_correct_action_taken_and_denial_reasons(self):
        
        #if action taken != 3 then denial_reasons must be 999
        series =  pd.Series(['999'],
                    name="denial_reasons",
                    index=[2]
                )
        result = denial_reasons_conditional_enum_value({"4":series})
        assert result.values == [True]
        
        #if action taken = 3 then denial_reasons must not contains 999
        series_2 =  pd.Series(['997'],
                    name="denial_reasons",
                    index=[2]
                )
        result_2 = denial_reasons_conditional_enum_value({"3":series_2})
        assert result_2.values == [True]
        
        #if action taken = 3 then denial_reasons must not contains 999 and
        # can have multiple values
        series_3 =  pd.Series(['997;1'],
                    name="denial_reasons",
                    index=[2]
                )
        result_3 = denial_reasons_conditional_enum_value({"3":series_3})
        assert result_3.values == [True]
       
    def test_with_incorrect_action_taken_and_denial_reasons(self):
        
        #if action taken != 3 and denial_reasons is not 999 
        #  , it should fail
        series =  pd.Series(['997'],
                    name="denial_reasons",
                    index=[2]
                )
        result = denial_reasons_conditional_enum_value({"4":series})
        assert result.values == [False]
        
        #if action taken = 3 and denial_reasons is 999
        #  , it should fail
        series_2 =  pd.Series(['999'],
                    name="denial_reasons",
                    index=[2]
                )
        result_2 = denial_reasons_conditional_enum_value({"3":series_2})
        assert result_2.values == [False]
        
         #if action taken = 3 and denial_reasons is 999
        #  , it should fail
        series_3 =  pd.Series(['997;999'],
                    name="denial_reasons",
                    index=[2]
                )
        result_3 = denial_reasons_conditional_enum_value({"3":series_3})
        assert result_3.values == [False]
        
        #if action taken = 3 then denial_reasons 
        # can have multiple values but can not contains 999 
        series_4 =  pd.Series(['997;1;999'],
                    name="denial_reasons",
                    index=[2]
                )
        result_4 = denial_reasons_conditional_enum_value({"3":series_4})
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
        assert meets_multi_value_field_restriction("1;2;3", ["2"] ) == False
        
    def test_with_valid_length(self):
        assert meets_multi_value_field_restriction("2", ["2"] ) == True
        assert meets_multi_value_field_restriction("1", ["2"] ) == True
        
    def test_with_valid_values(self):
        assert meets_multi_value_field_restriction("1;2;3", ["4"] ) == True
        
        
class TestMultiInvalidNumberOfValues:
    series =  pd.Series(['999'],
                    name="test_name",
                    index=[2]
                )
    
    def test_inside_maxlength(self):
        result = has_valid_multi_field_value_count({"4": self.series}, 5)
        assert result.values == [True]
        
    def test_on_maxlength(self):
        result = has_valid_multi_field_value_count({"4": self.series}, 2)
        assert result.values == [True]
        
    def test_outside_maxlength(self):
        result = has_valid_multi_field_value_count({"4": self.series}, 1)
        assert result.values == [False]

class TestInvalidEnumValue:
    def test_with_valid_enum_values(self):
        accepted_values = ["1","2"]
        result = is_valid_enum("1;2", accepted_values)
        assert result == True
        
    def test_with_is_valid_enums(self):
        accepted_values = ["1","2"]
        result = is_valid_enum("0;3", accepted_values)
        assert result == False

class TestIsNumber:
    def test_number_value(self):
        value = "1"
        result = is_number(value)
        assert result == True
        
    def test_non_number_value(self):
        value = "a"
        result = is_number(value)
        assert result == False

    def test_decimal_numeric_value(self):
        value = "0.1"
        result = is_number(value)
        assert result == True

    def test_alphanumeric_value(self):
        value = "abc123"
        result = is_number(value)
        assert result == False

    def test_negative_numeric_value(self):
        value = "-1"
        result = is_number(value)
        assert result == True

    def test_negative_decimal_value(self):
        value = "-0.1"
        result = is_number(value)
        assert result == True
        
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
        series =  pd.Series([''],
                        name="ct_loan_term",
                        index=[2]
        )
        condition_values: set[str] = { "900" }
        
        result1 = has_no_conditional_field_conflict({"988":series}, condition_values)
        assert result1.values == [True]
        
        # if ct_loan_term_flag == 900 then ct_loan_term must not be blank
        series2 =  pd.Series(['36'],
                        name="ct_loan_term",
                        index=[2]
        )
        condition_values2: set[str] = { "900" }
        result2 = has_no_conditional_field_conflict({"900":series2}, condition_values2)
        assert result2.values == [True]
        
    def test_conditional_field_conflict_incorrect(self):
                         
        # if ct_loan_term_flag != 900 then ct_loan_term must be blank
        # in this test, ct_loan_term_flag is not 900 and ct_loan_term is NOT blank, so must return False
        series =  pd.Series(['36'],
                        name="ct_loan_term",
                        index=[2]
        )
        condition_values: set[str] = { "900" }
        
        result1 = has_no_conditional_field_conflict({"988":series}, condition_values)
        assert result1.values == [False]
        
        # if ct_loan_term_flag == 900 then ct_loan_term must not be blank
        # in this testm ct_loan_term is blank, so must return False
        series2 =  pd.Series([''],
                        name="ct_loan_term",
                        index=[2]
        )
        condition_values2: set[str] = { "900" }
        result2 = has_no_conditional_field_conflict({"900":series2}, condition_values2)
        assert result2.values == [False]
        
        series3 =  pd.Series([' '],
                        name="ct_loan_term",
                        index=[2]
        )
        result3 = has_no_conditional_field_conflict({"900":series3}, condition_values2)
        assert result3.values == [False]
        
class TestEnumValueConflict:
    
    def test_enum_value_confict_correct(self):
        
        # if ct_credit_product = 1 or 2, if ct_loan_term_flag != 999, then return True
        series =  pd.Series(["988"],
                    name="ct_loan_term_flag",
                    index=[2]
        )
        condition_values1: set[str] = { "1", "2" }
        condition_values2 = None
        condition_value = "999"
        ct_credit_product = "1;2"
        result1 = has_valid_enum_pair({ct_credit_product:series}, condition_values1, condition_values2, condition_value)
        assert result1.values == [True]
        
        # if ct_credit_product = 988 , if ct_loan_term_flag == 999, then return True
        series =  pd.Series(["999"],
                    name="ct_loan_term",
                    index=[2]
        )
        condition_values1 = None
        condition_values2: set[str] = { "988" }
        condition_value = "999"
        ct_credit_product = "988"
        result1 = has_valid_enum_pair({ct_credit_product:series}, condition_values1, condition_values2, condition_value)
        assert result1.values == [True]
    
    def test_enum_value_confict_incorrect(self):
        
        # if ct_credit_product = 1 or 2, if ct_loan_term_flag == 999, then return False
        series =  pd.Series(["999"],
                    name="ct_loan_term_flag",
                    index=[2]
        )
        condition_values1: set[str] = { "1", "2" }
        condition_values2 = None
        condition_value = "999"
        ct_credit_product = "1;2"
        result1 = has_valid_enum_pair({ct_credit_product:series}, condition_values1, condition_values2, condition_value)
        assert result1.values == [False]
        
        # if ct_credit_product = 988 , if ct_loan_term_flag != 999, then return False
        series =  pd.Series(["988"],
                    name="ct_loan_term",
                    index=[2]
        )
        condition_values1 = None
        condition_values2: set[str] = { "988" }
        condition_value = "999"
        ct_credit_product = "988"
        result1 = has_valid_enum_pair({ct_credit_product:series}, condition_values1, condition_values2, condition_value)
        assert result1.values == [False]


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
        target_values = ["999","999","999","999","","",""]
        condition_values = ["3","4","5"]
    
        series =  pd.Series(["3"],
                    name="action_taken",
                    index=[1]
        )
        values = tuple(["999","999","999","999","","",""])
        result1 = is_fieldset_equal_to({values:series}, condition_values, target_values)
        assert result1.values == [True]
        
    def test_with_correct_other_values(self):
        target_values = ["999","999","999","999","","",""]
        condition_values = ["3","4","5"]
    
        series =  pd.Series(["2"],
                    name="action_taken",
                    index=[1]
        )
        values = tuple(["999","999","999","999","","",""])
        result1 = is_fieldset_equal_to({values:series}, condition_values, target_values)
        assert result1.values == [True]
        
    def test_with_incorrect_values(self):
        target_values = ["999","999","999","999","","",""]
        condition_values = ["3","4","5"]
    
        series =  pd.Series(["3"],
                    name="action_taken",
                    index=[1]
        )
        values = tuple(["999","999","999","","","",""])
        result1 = is_fieldset_equal_to({values:series}, condition_values, target_values)
        assert result1.values == [False]
        
    def test_with_incorrect_other_values(self):
        target_values = ["999","999","999","999","","",""]
        condition_values = ["3","4","5"]
    
        series =  pd.Series(["2"],
                    name="action_taken",
                    index=[1]
        )
        values = tuple(["999","999","999","","","",""])
        result1 = is_fieldset_equal_to({values:series}, condition_values, target_values)
        assert result1.values == [True]
        
class TestIsFieldsetNotEqualTo:
    
    def test_with_all_equal_values(self):
        target_values = ["","","","999","999"]
        condition_values = ["1","2"]
    
        series =  pd.Series(["1"],
                    name="action_taken",
                    index=[1]
        )
        values = tuple(["","","","999","999"])
        result1 = is_fieldset_not_equal_to({values:series}, 
                                           condition_values,
                                           target_values)
        assert result1.values == [False]
        
    def test_with_some_equal_values(self):
        target_values = ["1","","","999",""]
        condition_values = ["1","2"]
    
        series =  pd.Series(["1"],
                    name="action_taken",
                    index=[1]
        )
        values = tuple(["","","","999","999"])
        result1 = is_fieldset_not_equal_to({values:series}, 
                                           condition_values, 
                                           target_values)
        assert result1.values == [False]
        
    def test_with_none_equal_values(self):
        target_values = ["1","2","3","997","997"]
        condition_values = ["1","2"]
    
        series =  pd.Series(["1"],
                    name="action_taken",
                    index=[1]
        )
        values = tuple(["","","","999","999"])
        result1 = is_fieldset_not_equal_to({values:series}, 
                                           condition_values, 
                                           target_values)
        assert result1.values == [True]
        
    def test_with_different_conditional_values(self):
        target_values = ["","","","999","999"]
        condition_values = ["1","2"]
    
        series =  pd.Series(["4"],
                    name="action_taken",
                    index=[1]
        )
        values = tuple(["","","","999","999"])
        result1 = is_fieldset_not_equal_to({values:series}, 
                                           condition_values, 
                                           target_values)
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

