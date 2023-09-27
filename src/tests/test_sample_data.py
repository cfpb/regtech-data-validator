import pandas as pd
import pytest

from validator import main
from validator.create_schemas import validate_phases
from validator.sample_data import read_bad_data, read_good_data


class TestValidatingSampleData:
    valid_response = {"response": "No validations errors or warnings"}

    def test_invalid_good_data_file(self):
        failed_fpath = "./SBL_Validations_SampleData_GoodFile_03312023_1.csv"
        with pytest.raises(Exception) as exc:
            read_good_data(failed_fpath)
        assert exc.type == FileNotFoundError

    def test_invalid_bad_data_file(self):
        failed_fpath = "./SBL_Validations_SampleData_BadFile_03312023_1.csv"
        with pytest.raises(Exception) as exc:
            read_bad_data(failed_fpath)
        assert exc.type == FileNotFoundError

    def test_run_validation_on_good_data_invalid_lei(self):
        lei = "000TESTFIUIDDONOTUS1"
        good_data_df = read_good_data()
        validation_result = validate_phases(good_data_df, lei)

        assert len(validation_result) == 1
        assert validation_result[0] != self.valid_response

    def test_run_validation_on_good_data_valid_lei(self):
        lei = "000TESTFIUIDDONOTUSE"
        good_data_df = read_good_data()
        validation_result = validate_phases(good_data_df, lei)

        assert len(validation_result) == 1
        assert validation_result[0] == self.valid_response

    def test_run_validation_on_bad_data_invalid_lei(self):
        lei = "000TESTFIUIDDONOTUS1"
        bad_data_df = read_bad_data()
        validation_result = validate_phases(bad_data_df, lei)

        print(validation_result)
        assert len(validation_result) >= 1
        assert validation_result[0] != self.valid_response

    def test_run_validation_on_bad_data_valid_lei(self):
        lei = "000TESTFIUIDDONOTUSE"
        bad_data_df = read_bad_data()
        # print(bad_data_df)
        validation_result = validate_phases(bad_data_df, lei)

        assert len(validation_result) >= 1
        assert validation_result[0] != self.valid_response
