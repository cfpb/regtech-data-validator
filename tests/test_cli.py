from pathlib import Path
from textwrap import dedent
import os

import pandas as pd
import pytest
from typer.testing import CliRunner

from regtech_data_validator import cli

cli_runner = CliRunner(mix_stderr=False)
data_dir = f'{os.path.dirname(os.path.realpath(__file__))}/data'
pass_file = f'{data_dir}/sbl-validations-pass.csv'
fail_file = f'{data_dir}/sbl-validations-fail.csv'


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


class TestOutputFormat:
    # TODO: Figure out why uid.duplicates_in_dataset returns different findings for matched records
    input_df = pd.DataFrame(
        data=[
            {
                'record_no': 1,
                'field_name': 'uid',
                'field_value': '12345678901234567890',
                'validation_severity': 'error',
                'validation_id': 'E3000',
                "fig_link": "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1",
                'validation_name': 'uid.duplicates_in_dataset',
                'validation_desc': "Any 'unique identifier' may not be used in mor...",
            },
            {
                'record_no': 2,
                'field_name': 'uid',
                'field_value': '12345678901234567890',
                'validation_severity': 'error',
                'validation_id': 'E3000',
                "fig_link": "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1",
                'validation_name': 'uid.duplicates_in_dataset',
                'validation_desc': "Any 'unique identifier' may not be used in mor...",
            },
        ],
    )
    input_df.index.name = 'finding_no'
    input_df.index += 1

    def test_output_pandas(self):
        expected_output = dedent(
            """
            record_no field_name           field_value validation_severity validation_id                                         fig_link            validation_name                                    validation_desc
finding_no                                                                                                                                                                                                               
1                   1        uid  12345678901234567890               error         E3000  https://www.consumerfinance.gov/data-research/...  uid.duplicates_in_dataset  Any 'unique identifier' may not be used in mor...
2                   2        uid  12345678901234567890               error         E3000  https://www.consumerfinance.gov/data-research/...  uid.duplicates_in_dataset  Any 'unique identifier' may not be used in mor...
        """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = cli.df_to_str(self.input_df)
        assert actual_output == expected_output

    def test_output_table(self):
        expected_output = dedent(
            """
              
╭──────────────┬─────────────┬──────────────┬──────────────────────┬───────────────────────┬─────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────╮
│   finding_no │   record_no │ field_name   │          field_value │ validation_severity   │ validation_id   │ fig_link                                                                                                       │ validation_name           │
├──────────────┼─────────────┼──────────────┼──────────────────────┼───────────────────────┼─────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────┤
│            1 │           1 │ uid          │ 12345678901234567890 │ error                 │ E3000           │ https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1 │ uid.duplicates_in_dataset │
│            2 │           2 │ uid          │ 12345678901234567890 │ error                 │ E3000           │ https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1 │ uid.duplicates_in_dataset │
╰──────────────┴─────────────┴──────────────┴──────────────────────┴───────────────────────┴─────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────╯
        """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = cli.df_to_table(self.input_df)
        assert actual_output == expected_output

    def test_output_csv(self):
        expected_output = dedent(
            """
        finding_no,record_no,field_name,field_value,validation_severity,validation_id,fig_link,validation_name,validation_desc
        1,1,uid,12345678901234567890,error,E3000,https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1,uid.duplicates_in_dataset,Any 'unique identifier' may not be used in mor...
        2,2,uid,12345678901234567890,error,E3000,https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1,uid.duplicates_in_dataset,Any 'unique identifier' may not be used in mor...
        """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = cli.df_to_csv(self.input_df)
        assert actual_output.strip('\n') == expected_output

    def test_output_json(self):
        expected_output = dedent(
            """
        [
            {
                "validation": {
                    "id": "E3000",
                    "fig_link": "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1",
                    "name": "uid.duplicates_in_dataset",
                    "description": "Any 'unique identifier' may not be used in mor...",
                    "severity": "error"
                },
                "records": [
                    {
                        "record_no": 1,
                        "fields": [
                            {
                                "name": "uid",
                                "value": "12345678901234567890"
                            }
                        ]
                    },
                    {
                        "record_no": 2,
                        "fields": [
                            {
                                "name": "uid",
                                "value": "12345678901234567890"
                            }
                        ]
                    }
                ]
            }
        ]
        """
        ).strip('\n')

        actual_output = cli.df_to_json(self.input_df)

        assert actual_output == expected_output


class TestDescribeCommand:
    def test_defaults(self):
        cli.describe()


class TestValidateCommand:
    valid_lei_context = cli.KeyValueOpt('lei', '000TESTFIUIDDONOTUSE')
    invalid_lei_context = cli.KeyValueOpt('lei', 'XXXXXXXXXXXXXXXXXXXX')

    pass_path = Path(pass_file)
    fail_path = Path(fail_file)

    def test_pass_file_defaults(self):
        is_valid, findings_df = cli.validate(path=self.pass_path)

        assert is_valid

    def test_pass_file_with_valid_context(self):
        is_valid, findings_df = cli.validate(path=self.pass_path, context=[self.valid_lei_context])

        assert is_valid

    def test_pass_file_with_invalid_context(self):
        is_valid, findings_df = cli.validate(path=self.pass_path, context=[self.invalid_lei_context])

        assert not is_valid

    def test_fail_file_csv_output(self):
        is_valid, findings_df = cli.validate(path=self.fail_path, output=cli.OutputFormat.CSV)

        assert not is_valid

    def test_fail_file_json_output(self):
        is_valid, findings_df = cli.validate(path=self.fail_path, output=cli.OutputFormat.JSON)

        assert not is_valid

    def test_fail_file_pandas_output(self):
        is_valid, findings_df = cli.validate(path=self.fail_path, output=cli.OutputFormat.PANDAS)

        assert not is_valid

    def test_fail_file_table_output(self):
        is_valid, findings_df = cli.validate(path=self.fail_path, output=cli.OutputFormat.TABLE)

        assert not is_valid


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
        assert result.stdout == ''
        assert result.stderr == 'status: SUCCESS, findings: 0\n'

    def test_pass_file_invalid_output_arg_value(self):
        result = cli_runner.invoke(cli.app, ['validate', pass_file, '--output', 'pdf'])

        assert result.exit_code == 2
        assert "Invalid value for '--output': 'pdf' is not one of" in result.stderr

    def test_fail_file_defaults(self):
        result = cli_runner.invoke(cli.app, ['validate', fail_file])

        assert result.exit_code == 0
        assert result.stdout != ''
        assert 'status: FAILURE, findings:' in result.stderr
