import pandas as pd
import pytest

from regtech_data_validator.create_schemas import validate_phases
from regtech_data_validator.validation_results import ValidationPhase

GOOD_FILE_PATH = "./tests/data/sbl-validations-pass.csv"
BAD_FILE_PATH = "./tests/data/sbl-validations-fail.csv"


class TestValidatingSampleData:
    good_file_df = pd.read_csv(GOOD_FILE_PATH, dtype=str, na_filter=False)
    bad_file_df = pd.read_csv(BAD_FILE_PATH, dtype=str, na_filter=False)

    def test_invalid_data_file(self):
        failed_fpath = "./file-does-not-exist.csv"
        with pytest.raises(Exception) as exc:
            pd.read_csv(failed_fpath, dtype=str, na_filter=False)
        assert exc.type == FileNotFoundError

    def test_run_validation_on_good_data_invalid_lei(self):
        lei = "000TESTFIUIDDONOTUS1"
        results = validate_phases(self.good_file_df, {'lei': lei})

        assert not results.is_valid

        # Only 'uid.invalid_uid_lei' validation returned
        assert len(results.findings['validation_id'].unique()) == 1
        assert len(results.findings['validation_id'] == 'W0003') > 0
        assert results.phase == ValidationPhase.LOGICAL.value

    def test_run_validation_on_good_data_valid_lei(self):
        lei = "000TESTFIUIDDONOTUSE"
        results = validate_phases(self.good_file_df, {'lei': lei})

        assert results.is_valid
        assert results.findings.empty
        assert results.phase == ValidationPhase.LOGICAL.value

    def test_run_validation_on_bad_data_invalid_lei(self):
        lei = "000TESTFIUIDDONOTUS1"
        results = validate_phases(self.bad_file_df, {'lei': lei})

        assert not results.is_valid

        # 'uid.invalid_uid_lei' and other validations returned
        assert len(results.findings['validation_id'].unique()) > 1
        assert len(results.findings['validation_id'] == 'W0003') > 0
        assert results.phase == ValidationPhase.SYNTACTICAL.value

    def test_run_validation_on_bad_data_valid_lei(self):
        lei = "000TESTFIUIDDONOTUSE"
        results = validate_phases(self.bad_file_df, {'lei': lei})

        assert not results.is_valid

        # 'uid.invalid_uid_lei' and other validations returned
        assert len(results.findings['validation_id'].unique()) > 1
        assert results.phase == ValidationPhase.SYNTACTICAL.value
