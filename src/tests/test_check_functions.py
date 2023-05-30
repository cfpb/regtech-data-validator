from validator.check_functions import invalid_date_format


class TestInvalidDateFormat:
    valid_date_format = "202310101"
    
    def test_with_valid_date(self):
        assert invalid_date_format(self.valid_date_format) == False
