import pandas as pd

from validator.check_functions import (denial_reasons_conditional_enum_value,
                                       duplicates_in_field,
                                       invalid_date_format,
                                       invalid_number_of_values,
                                       multi_invalid_number_of_values,
                                       multi_value_field_restriction)


class TestInvalidDateFormat:
    valid_date_format = "20231010"
    invalid_date_format_1 = "202310101"
    invalid_date_format_2 = "20231032"
    invalid_date_format_3 = "20231301"
    invalid_date_format_4 = "00001201"
    
    def test_with_valid_date(self):
        assert invalid_date_format(self.valid_date_format) == True
        
    def test_with_invalid_date(self):
        assert invalid_date_format(self.invalid_date_format_1) == False
        
    def test_with_invalid_day(self):
        assert invalid_date_format(self.invalid_date_format_2) == False
        
    def test_with_invalid_month(self):
        assert invalid_date_format(self.invalid_date_format_3) == False
        
    def test_with_invalid_year(self):
        assert invalid_date_format(self.invalid_date_format_4) == False


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
        assert duplicates_in_field("") == True
        
    def test_with_no_duplicates(self):
        assert duplicates_in_field("1") == True
        assert duplicates_in_field("1;2;3;4") == True
        
    def test_with_duplicates(self):
        assert duplicates_in_field("1;2;3;3;4") == False
        

class TestInvalidNumberOfValues:
    
    def test_with_in_range(self):
        assert invalid_number_of_values("1;2;", 1, 4) == True
        
    def test_with_lower_range_value(self):
        assert invalid_number_of_values("1", 1, 4) == True
        
    def test_with_invalid_lower_range_value(self):
        assert invalid_number_of_values("1", 2, 4) == False
        
    def test_with_upper_range_value(self):
        assert invalid_number_of_values("1;2", 1, 2) == True
        
    def test_with_invalid_upper_range_value(self):
        assert invalid_number_of_values("1;2;3;4", 2, 3) == False
        

class TestMultiValueFieldRestriction:
    
    def test_with_invalid_values(self):
        assert multi_value_field_restriction("1;2;3", ["2"] ) == False
        
    def test_with_valid_length(self):
        assert multi_value_field_restriction("2", ["2"] ) == True
        assert multi_value_field_restriction("1", ["2"] ) == True
        
    def test_with_valid_values(self):
        assert multi_value_field_restriction("1;2;3", ["4"] ) == True
        
        
class TestMultiInvalidNumberOfValues:
    series =  pd.Series(['999'],
                    name="test_name",
                    index=[2]
                )
    
    def test_inside_maxlength(self):
        result = multi_invalid_number_of_values({"4": self.series}, 5)
        assert result.values == [True]
        
    def test_on_maxlength(self):
        result = multi_invalid_number_of_values({"4": self.series}, 2)
        assert result.values == [True]
        
    def test_outside_maxlength(self):
        result = multi_invalid_number_of_values({"4": self.series}, 1)
        assert result.values == [False]
