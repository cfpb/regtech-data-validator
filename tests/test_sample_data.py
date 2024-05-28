import pandas as pd
import pytest

from regtech_data_validator.create_schemas import validate_phases, ValidationPhase

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
        is_valid, findings_df, validation_phase = validate_phases(self.good_file_df, {'lei': lei})

        assert not is_valid

        # Only 'uid.invalid_uid_lei' validation returned
        assert len(findings_df['validation_id'].unique()) == 1
        assert len(findings_df['validation_id'] == 'W0003') > 0
        assert validation_phase == ValidationPhase.LOGICAL.value

    def test_run_validation_on_good_data_valid_lei(self):
        lei = "000TESTFIUIDDONOTUSE"
        is_valid, findings_df, validation_phase = validate_phases(self.good_file_df, {'lei': lei})

        assert is_valid
        assert findings_df.empty
        assert validation_phase == ValidationPhase.LOGICAL.value

    def test_run_validation_on_bad_data_invalid_lei(self):
        lei = "000TESTFIUIDDONOTUS1"
        is_valid, findings_df, validation_phase = validate_phases(self.bad_file_df, {'lei': lei})

        assert not is_valid

        # 'uid.invalid_uid_lei' and other validations returned
        assert len(findings_df['validation_id'].unique()) > 1
        assert len(findings_df['validation_id'] == 'W0003') > 0
        assert validation_phase == ValidationPhase.SYNTACTICAL.value

    def test_run_validation_on_bad_data_valid_lei(self):
        lei = "000TESTFIUIDDONOTUSE"
        is_valid, findings_df, validation_phase = validate_phases(self.bad_file_df, {'lei': lei})

        assert not is_valid

        # 'uid.invalid_uid_lei' and other validations returned
        assert len(findings_df['validation_id'].unique()) > 1
        assert validation_phase == ValidationPhase.SYNTACTICAL.value
