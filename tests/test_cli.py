from pathlib import Path

import pytest
from typer.testing import CliRunner

from regtech_data_validator import cli

cli_runner = CliRunner(mix_stderr=False)
pass_file = './tests/data/sblar_no_findings.csv'
fail_file = './tests/data/all_syntax_errors.csv'


class TestParseKeyValue:
    def test_parse_success(self):
        test_str = "fruit=apple"
        key_val: cli.KeyValueOpt = cli.parse_key_value(test_str)

        assert key_val.key == 'fruit'
        assert key_val.value == 'apple'

    def test_parse_fail_wrong_delimiter(self):
        test_str = "fruit:apple"

        with pytest.raises(ValueError):
            cli.parse_key_value(test_str)

    def test_parse_fail_no_delimiter(self):
        test_str = "fruitapple"

        with pytest.raises(ValueError):
            cli.parse_key_value(test_str)

    def test_parse_fail_multiple_delimiters(self):
        test_str = "fruit=apple=orange"

        with pytest.raises(ValueError):
            cli.parse_key_value(test_str)


class TestDescribeCommand:
    def test_defaults(self):
        cli.describe()


class TestValidateCommand:
    valid_lei_context = cli.KeyValueOpt('lei', '123456789TESTBANK123')
    invalid_lei_context = cli.KeyValueOpt('lei', 'XXXXXXXXXXXXXXXXXXXX')

    pass_path = Path(pass_file)
    fail_path = Path(fail_file)

    def test_pass_file_defaults(self):
        status, findings_df = cli.validate(path=self.pass_path)

        assert status == 'SUCCESS'

    def test_pass_file_with_valid_context(self):
        status, findings_df = cli.validate(path=self.pass_path, context=[self.valid_lei_context])

        assert status == 'SUCCESS'

    def test_pass_file_with_invalid_context(self):
        status, findings_df = cli.validate(path=self.pass_path, context=[self.invalid_lei_context])

        assert status == 'FAILURE'

    def test_fail_file_csv_output(self):
        status, findings_df = cli.validate(path=self.fail_path, output=cli.OutputFormat.CSV)

        assert status == 'FAILURE'

    def test_fail_file_json_output(self):
        status, findings_df = cli.validate(path=self.fail_path, output=cli.OutputFormat.JSON)

        assert status == 'FAILURE'

    def test_fail_file_pandas_output(self):
        status, findings_df = cli.validate(path=self.fail_path, output=cli.OutputFormat.POLARS)

        assert status == 'FAILURE'

    def test_fail_file_table_output(self):
        status, findings_df = cli.validate(path=self.fail_path, output=cli.OutputFormat.TABLE)

        assert status == 'FAILURE'

    def test_fail_download_output(self):
        status, findings_df = cli.validate(path=self.fail_path, output=cli.OutputFormat.DOWNLOAD)

        assert status == 'FAILURE'


class TestDescribeCli:
    """
    Test `describe` command with Typer's CLI test runner
    """

    def test_defaults(self):
        result = cli_runner.invoke(cli.app, ['describe'])

        assert result.exit_code == 0
        assert result.stdout == 'Feature coming soon...\n'


class TestValidateCli:
    """
    Test `validate` command with Typer's CLI test runner
    """

    def test_pass_file_defaults(self):
        result = cli_runner.invoke(cli.app, ['validate', pass_file])

        assert result.exit_code == 0
        assert result.stdout == '\n'
        assert result.stderr == 'Status: SUCCESS, Total Errors: 0, Validation Phase: Logical\n'

    def test_pass_file_invalid_output_arg_value(self):
        result = cli_runner.invoke(cli.app, ['validate', pass_file, '--output', 'pdf'])
        assert result.exit_code == 2
        assert "Invalid value for '--output': 'pdf' is not one of" in result.stderr

    def test_fail_file_defaults(self):
        result = cli_runner.invoke(cli.app, ['validate', fail_file])

        assert result.exit_code == 0
        assert result.stdout != ''
        assert 'Status: FAILURE' in result.stderr
        assert 'Total Errors:' in result.stderr
        assert 'Validation Phase: Syntactical' in result.stderr
