import pandas as pd

from validator.check_functions import (denial_reasons_conditional_enum_value,
                                       invalid_date_format)


class TestInvalidDateFormat:
    valid_date_format = "20231010"
    
    def test_with_valid_date(self):
        assert invalid_date_format(self.valid_date_format) == True


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