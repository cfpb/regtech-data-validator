import pandas as pd
import ujson

from regtech_data_validator.data_formatters import df_to_csv, df_to_str, df_to_json, df_to_table, df_to_download
from textwrap import dedent


class TestOutputFormat:
    # TODO: Figure out why uid.duplicates_in_dataset returns different findings for matched records
    input_df = pd.DataFrame(
        data=[
            {
                'record_no': 1,
                'uid': '12345678901234567890',
                'field_name': 'uid',
                'field_value': '12345678901234567890',
                'validation_id': 'E3000',
            },
            {
                'record_no': 2,
                'uid': '12345678901234567890',
                'field_name': 'uid',
                'field_value': '12345678901234567890',
                'validation_id': 'E3000',
            },
            {
                'record_no': 3,
                'uid': '12345678901234567891',
                'field_name': 'action_taken',
                'field_value': '1',
                'validation_id': 'E2008',
            },
            {
                'record_no': 3,
                'uid': '12345678901234567891',
                'field_name': 'amount_approved',
                'field_value': '',
                'validation_id': 'E2008',
            },
        ],
    )
    input_df.index.name = 'finding_no'
    input_df.index += 1

    def test_output_pandas(self):
        expected_output = dedent(
            """
                        record_no                   uid       field_name           field_value validation_id
            finding_no                                                                                      
            1                   1  12345678901234567890              uid  12345678901234567890         E3000
            2                   2  12345678901234567890              uid  12345678901234567890         E3000
            3                   3  12345678901234567891     action_taken                     1         E2008
            4                   3  12345678901234567891  amount_approved                               E2008
            """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = df_to_str(self.input_df)
        assert actual_output == expected_output

    def test_output_table(self):
        expected_output = dedent(
            """
            ╭──────────────┬─────────────┬──────────────────────┬─────────────────┬──────────────────────┬─────────────────╮
            │   finding_no │   record_no │                  uid │ field_name      │ field_value          │ validation_id   │
            ├──────────────┼─────────────┼──────────────────────┼─────────────────┼──────────────────────┼─────────────────┤
            │            1 │           1 │ 12345678901234567890 │ uid             │ 12345678901234567890 │ E3000           │
            │            2 │           2 │ 12345678901234567890 │ uid             │ 12345678901234567890 │ E3000           │
            │            3 │           3 │ 12345678901234567891 │ action_taken    │ 1                    │ E2008           │
            │            4 │           3 │ 12345678901234567891 │ amount_approved │                      │ E2008           │
            ╰──────────────┴─────────────┴──────────────────────┴─────────────────┴──────────────────────┴─────────────────╯
            """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = df_to_table(self.input_df)
        assert actual_output == expected_output

    def test_output_csv(self):
        expected_output = dedent(
            """
            finding_no,record_no,uid,field_name,field_value,validation_id
            1,1,12345678901234567890,uid,12345678901234567890,E3000
            2,2,12345678901234567890,uid,12345678901234567890,E3000
            3,3,12345678901234567891,action_taken,1,E2008
            4,3,12345678901234567891,amount_approved,,E2008
            """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = df_to_csv(self.input_df)
        assert actual_output.strip('\n') == expected_output

    def test_empty_results_json(self):
        expected_output = ujson.dumps([], indent=4, escape_forward_slashes=False)
        actual_output = df_to_json(pd.DataFrame())

        assert actual_output == expected_output

    def test_output_json(self):
        results_object = [
            {
                "validation": {
                    "id": "E2008",
                    "name": "amount_approved.conditional_field_conflict",
                    "description": "* When 'action taken' does **not** equal 1 (originated) or \n2 (approved but not accepted), 'amount approved or originated' must be blank.\n* When 'action taken' equals 1 or 2, 'amount approved or originated' must **not** be blank.\n",
                    "severity": "Error",
                    "scope": "multi-field",
                    "fig_link": "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.2.7",
                    "is_truncated": False,
                },
                "records": [
                    {
                        "record_no": 3,
                        "uid": "12345678901234567891",
                        "fields": [{"name": "amount_approved", "value": ""}, {"name": "action_taken", "value": "1"}],
                    }
                ],
            },
            {
                "validation": {
                    "id": "E3000",
                    "name": "uid.duplicates_in_dataset",
                    "description": "* Any 'unique identifier' may **not** be used in more than one \nrecord within a small business lending application register.\n",
                    "severity": "Error",
                    "scope": "register",
                    "fig_link": "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1",
                    "is_truncated": False,
                },
                "records": [
                    {
                        "record_no": 1,
                        "uid": "12345678901234567890",
                        "fields": [{"name": "uid", "value": "12345678901234567890"}],
                    },
                    {
                        "record_no": 2,
                        "uid": "12345678901234567890",
                        "fields": [{"name": "uid", "value": "12345678901234567890"}],
                    },
                ],
            },
        ]
        expected_output = ujson.dumps(results_object, indent=4, escape_forward_slashes=False)

        actual_output = df_to_json(self.input_df)
        assert actual_output == expected_output

    def test_output_json_with_max_group_size(self):
        results_object = [
            {
                "validation": {
                    "id": "E2008",
                    "name": "amount_approved.conditional_field_conflict",
                    "description": "* When 'action taken' does **not** equal 1 (originated) or \n2 (approved but not accepted), 'amount approved or originated' must be blank.\n* When 'action taken' equals 1 or 2, 'amount approved or originated' must **not** be blank.\n",
                    "severity": "Error",
                    "scope": "multi-field",
                    "fig_link": "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.2.7",
                    "is_truncated": False,
                },
                "records": [
                    {
                        "record_no": 3,
                        "uid": "12345678901234567891",
                        "fields": [{"name": "amount_approved", "value": ""}, {"name": "action_taken", "value": "1"}],
                    }
                ],
            },
            {
                "validation": {
                    "id": "E3000",
                    "name": "uid.duplicates_in_dataset",
                    "description": "* Any 'unique identifier' may **not** be used in more than one \nrecord within a small business lending application register.\n",
                    "severity": "Error",
                    "scope": "register",
                    "fig_link": "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1",
                    "is_truncated": True,
                },
                "records": [
                    {
                        "record_no": 1,
                        "uid": "12345678901234567890",
                        "fields": [{"name": "uid", "value": "12345678901234567890"}],
                    },
                ],
            },
        ]
        expected_output = ujson.dumps(results_object, indent=4, escape_forward_slashes=False)

        actual_output = df_to_json(self.input_df, max_group_size=1)
        assert actual_output == expected_output

    def test_output_json_with_max_records(self):
        results_object = [
            {
                "validation": {
                    "id": "E0040",
                    "name": "app_method.invalid_enum_value",
                    "description": "* 'Application method' must equal 1, 2, 3, or 4.",
                    "severity": "Error",
                    "scope": "single-field",
                    "fig_link": "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.1.4",
                    "is_truncated": True,
                },
                "records": [
                    {"record_no": 4, "uid": "12345678901234567890", "fields": [{"name": "app_method", "value": "5"}]}
                ],
            },
            {
                "validation": {
                    "id": "E2008",
                    "name": "amount_approved.conditional_field_conflict",
                    "description": "* When 'action taken' does **not** equal 1 (originated) or \n2 (approved but not accepted), 'amount approved or originated' must be blank.\n* When 'action taken' equals 1 or 2, 'amount approved or originated' must **not** be blank.\n",
                    "severity": "Error",
                    "scope": "multi-field",
                    "fig_link": "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.2.7",
                    "is_truncated": False,
                },
                "records": [
                    {
                        "record_no": 3,
                        "uid": "12345678901234567891",
                        "fields": [{"name": "amount_approved", "value": ""}, {"name": "action_taken", "value": "1"}],
                    }
                ],
            },
        ]
        expected_output = ujson.dumps(results_object, indent=4, escape_forward_slashes=False)

        error_df = pd.DataFrame(self.input_df)
        error_df.loc[-1] = [5, '12345678901234567890', 'app_method', '5', 'E0040']
        error_df.loc[-2] = [4, '12345678901234567890', 'app_method', '5', 'E0040']
        error_df.index = error_df.index + 2
        error_df.sort_index(inplace=True)

        actual_output = df_to_json(error_df, max_records=2)
        assert actual_output == expected_output

    def test_download_csv(self):
        expected_output = dedent(
            """
            validation_type,validation_id,validation_name,row,unique_identifier,fig_link,validation_description,field_1,value_1,field_2,value_2
            "Error","E2008","amount_approved.conditional_field_conflict",4,"12345678901234567891","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.2.7","* When 'action taken' does **not** equal 1 (originated) or 
            2 (approved but not accepted), 'amount approved or originated' must be blank.
            * When 'action taken' equals 1 or 2, 'amount approved or originated' must **not** be blank.
            ","amount_approved","","action_taken","1"
            "Error","E3000","uid.duplicates_in_dataset",2,"12345678901234567890","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1","* Any 'unique identifier' may **not** be used in more than one 
            record within a small business lending application register.
            ","uid","12345678901234567890"
            "Error","E3000","uid.duplicates_in_dataset",3,"12345678901234567890","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1","* Any 'unique identifier' may **not** be used in more than one 
            record within a small business lending application register.
            ","uid","12345678901234567890"
            """
        ).strip('\n')
        actual_output = df_to_download(self.input_df, 2)
        assert actual_output.strip() == expected_output

    def test_download_max_message_csv(self):
        expected_output = dedent(
            """
            validation_type,validation_id,validation_name,row,unique_identifier,fig_link,validation_description,field_1,value_1,field_2,value_2
            The submission contained 5, but only 3 will be displayed in the download report.  Fix the current errors and resubmit to see more.
            "Error","E2008","amount_approved.conditional_field_conflict",4,"12345678901234567891","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.2.7","* When 'action taken' does **not** equal 1 (originated) or 
            2 (approved but not accepted), 'amount approved or originated' must be blank.
            * When 'action taken' equals 1 or 2, 'amount approved or originated' must **not** be blank.
            ","amount_approved","","action_taken","1"
            "Error","E3000","uid.duplicates_in_dataset",2,"12345678901234567890","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1","* Any 'unique identifier' may **not** be used in more than one 
            record within a small business lending application register.
            ","uid","12345678901234567890"
            "Error","E3000","uid.duplicates_in_dataset",3,"12345678901234567890","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1","* Any 'unique identifier' may **not** be used in more than one 
            record within a small business lending application register.
            ","uid","12345678901234567890"
            """
        ).strip('\n')
        actual_output = df_to_download(self.input_df, 5, 3)
        assert actual_output.strip() == expected_output

    def test_empty_download_csv(self):
        expected_output = dedent(
            """
            validation_type,validation_id,validation_name,row,unique_identifier,fig_link,validation_description,
            """
        ).strip('\n')
        actual_output = df_to_download(pd.DataFrame(), 0)
        assert actual_output == expected_output
