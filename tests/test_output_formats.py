import pandas as pd

from regtech_data_validator.data_formatters import df_to_csv, df_to_str, df_to_json, df_to_table
from textwrap import dedent


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
                'validation_name': 'uid.duplicates_in_dataset',
                'validation_desc': "Any 'unique identifier' may not be used in mor...",
            },
            {
                'record_no': 2,
                'field_name': 'uid',
                'field_value': '12345678901234567890',
                'validation_severity': 'error',
                'validation_id': 'E3000',
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
                    record_no field_name           field_value validation_severity validation_id            validation_name                                    validation_desc
        finding_no                                                                                                                                                            
        1                   1        uid  12345678901234567890               error         E3000  uid.duplicates_in_dataset  Any 'unique identifier' may not be used in mor...
        2                   2        uid  12345678901234567890               error         E3000  uid.duplicates_in_dataset  Any 'unique identifier' may not be used in mor...
        """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = df_to_str(self.input_df)

        assert actual_output == expected_output

    def test_output_table(self):
        expected_output = dedent(
            """
        ╭──────────────┬─────────────┬──────────────┬──────────────────────┬───────────────────────┬─────────────────┬───────────────────────────╮
        │   finding_no │   record_no │ field_name   │          field_value │ validation_severity   │ validation_id   │ validation_name           │
        ├──────────────┼─────────────┼──────────────┼──────────────────────┼───────────────────────┼─────────────────┼───────────────────────────┤
        │            1 │           1 │ uid          │ 12345678901234567890 │ error                 │ E3000           │ uid.duplicates_in_dataset │
        │            2 │           2 │ uid          │ 12345678901234567890 │ error                 │ E3000           │ uid.duplicates_in_dataset │
        ╰──────────────┴─────────────┴──────────────┴──────────────────────┴───────────────────────┴─────────────────┴───────────────────────────╯
        """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = df_to_table(self.input_df)

        assert actual_output == expected_output

    def test_output_csv(self):
        expected_output = dedent(
            """
        finding_no,record_no,field_name,field_value,validation_severity,validation_id,validation_name,validation_desc
        1,1,uid,12345678901234567890,error,E3000,uid.duplicates_in_dataset,Any 'unique identifier' may not be used in mor...
        2,2,uid,12345678901234567890,error,E3000,uid.duplicates_in_dataset,Any 'unique identifier' may not be used in mor...
        """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = df_to_csv(self.input_df)

        assert actual_output.strip('\n') == expected_output

    def test_output_json(self):
        expected_output = dedent(
            """
        [
            {
                "validation": {
                    "id": "E3000",
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

        actual_output = df_to_json(self.input_df)

        assert actual_output == expected_output