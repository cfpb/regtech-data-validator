import os
import sys

import pandas as pd
import pytest

from validator.create_schemas import validate_phases

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa: E402
sys.path.append(ROOT_DIR)  # noqa: E402

GOOD_FILE_PATH = "./src/tests/data/sbl-validations-pass.csv"
BAD_FILE_PATH = "./src/tests/data/sbl-validations-fail.csv"


class TestValidatingSampleData:
    valid_response = {"response": "No validations errors or warnings"}

    good_file_df = pd.read_csv(GOOD_FILE_PATH, dtype=str, na_filter=False)
    bad_file_df = pd.read_csv(BAD_FILE_PATH, dtype=str, na_filter=False)

    def test_invalid_data_file(self):
        failed_fpath = "./file-does-not-exist.csv"
        with pytest.raises(Exception) as exc:
            pd.read_csv(failed_fpath, dtype=str, na_filter=False)
        assert exc.type == FileNotFoundError

    def test_run_validation_on_good_data_invalid_lei(self):
        lei = "000TESTFIUIDDONOTUS1"
        validation_result = validate_phases(self.good_file_df, lei)

        assert len(validation_result) == 1
        assert validation_result[0] != self.valid_response

    def test_run_validation_on_good_data_valid_lei(self):
        lei = "000TESTFIUIDDONOTUSE"
        validation_result = validate_phases(self.good_file_df, lei)

        assert len(validation_result) == 1
        assert validation_result[0] == self.valid_response

    def test_run_validation_on_bad_data_invalid_lei(self):
        lei = "000TESTFIUIDDONOTUS1"
        validation_result = validate_phases(self.bad_file_df, lei)

        assert len(validation_result) >= 1
        assert validation_result[0] != self.valid_response

    def test_run_validation_on_bad_data_valid_lei(self):
        lei = "000TESTFIUIDDONOTUSE"
        validation_result = validate_phases(self.bad_file_df, lei)

        assert len(validation_result) >= 1
        assert validation_result[0] != self.valid_response
