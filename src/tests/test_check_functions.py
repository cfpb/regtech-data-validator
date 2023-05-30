from validator.check_functions import invalid_date_format


class TestInvalidDateFormat:
    valid_date_format = "20231010"
    
    def test_with_valid_date(self):
        assert invalid_date_format(self.valid_date_format) == True
