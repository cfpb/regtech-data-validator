import polars as pl
import ujson

from regtech_data_validator import global_data
from regtech_data_validator.data_formatters import df_to_csv, df_to_str, df_to_json, df_to_table, df_to_download
from regtech_data_validator.validation_results import ValidationPhase
from textwrap import dedent


class TestOutputFormat:
    # TODO: Figure out why uid.duplicates_in_dataset returns different findings for matched records
    findings_df = pl.DataFrame(
        data=[
            {
                'validation_type': 'Error',
                'validation_id': 'E3000',
                'validation_name': 'uid.duplicates_in_dataset',
                'row': 2,
                'unique_identifier': '12345678901234567890',
                'fig_link': global_data.fig_base_url + "#4.3.1",
                'scope': 'register',
                'phase': ValidationPhase.LOGICAL.value,
                'validation_description': dedent(
                    """\
                        * Any 'unique identifier' may **not** be used in more than one 
                        record within a small business lending application register.
                    """
                ),
                'field_1': 'uid',
                'value_1': '12345678901234567890',
            },
            {
                'validation_type': 'Error',
                'validation_id': 'E3000',
                'validation_name': 'uid.duplicates_in_dataset',
                'row': 3,
                'unique_identifier': '12345678901234567890',
                'fig_link': global_data.fig_base_url + "#4.3.1",
                'scope': 'register',
                'phase': ValidationPhase.LOGICAL.value,
                'validation_description': dedent(
                    """\
                        * Any 'unique identifier' may **not** be used in more than one 
                        record within a small business lending application register.
                    """
                ),
                'field_1': 'uid',
                'value_1': '12345678901234567890',
            },
            {
                'validation_type': 'Error',
                'validation_id': 'E2008',
                'validation_name': 'amount_approved.conditional_field_conflict',
                'row': 4,
                'unique_identifier': '12345678901234567891',
                'fig_link': global_data.fig_base_url + "#4.2.7",
                'scope': 'multi-field',
                'phase': ValidationPhase.LOGICAL.value,
                'validation_description': dedent(
                    """\
                        * When 'action taken' does **not** equal 1 (originated) or 
                        2 (approved but not accepted), 'amount approved or originated' must be blank.
                        * When 'action taken' equals 1 or 2, 'amount approved or originated' must **not** be blank.
                    """
                ),
                'field_1': 'action_taken',
                'value_1': '1',
                'field_2': 'amount_approved',
                'value_2': '',
            },
        ],
    )

    def test_output_polars(self):
        expected_output = dedent(
            """
                shape: (3, 13)
                ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
                │ val ┆ val ┆ val ┆ row ┆ uni ┆ fig ┆ sco ┆ pha ┆ val ┆ fie ┆ val ┆ fie ┆ val │
                │ ida ┆ ida ┆ ida ┆ --- ┆ que ┆ _li ┆ pe  ┆ se  ┆ ida ┆ ld_ ┆ ue_ ┆ ld_ ┆ ue_ │
                │ tio ┆ tio ┆ tio ┆ i64 ┆ _id ┆ nk  ┆ --- ┆ --- ┆ tio ┆ 1   ┆ 1   ┆ 2   ┆ 2   │
                │ n_t ┆ n_i ┆ n_n ┆     ┆ ent ┆ --- ┆ str ┆ str ┆ n_d ┆ --- ┆ --- ┆ --- ┆ --- │
                │ ype ┆ d   ┆ ame ┆     ┆ ifi ┆ str ┆     ┆     ┆ esc ┆ str ┆ str ┆ str ┆ str │
                │ --- ┆ --- ┆ --- ┆     ┆ er  ┆     ┆     ┆     ┆ rip ┆     ┆     ┆     ┆     │
                │ str ┆ str ┆ str ┆     ┆ --- ┆     ┆     ┆     ┆ tio ┆     ┆     ┆     ┆     │
                │     ┆     ┆     ┆     ┆ str ┆     ┆     ┆     ┆ n   ┆     ┆     ┆     ┆     │
                │     ┆     ┆     ┆     ┆     ┆     ┆     ┆     ┆ --- ┆     ┆     ┆     ┆     │
                │     ┆     ┆     ┆     ┆     ┆     ┆     ┆     ┆ str ┆     ┆     ┆     ┆     │
                ╞═════╪═════╪═════╪═════╪═════╪═════╪═════╪═════╪═════╪═════╪═════╪═════╪═════╡
                │ Err ┆ E30 ┆ uid ┆ 2   ┆ 123 ┆ htt ┆ reg ┆ Log ┆ *   ┆ uid ┆ 123 ┆ nul ┆ nul │
                │ or  ┆ 00  ┆ .du ┆     ┆ 456 ┆ ps: ┆ ist ┆ ica ┆ Any ┆     ┆ 456 ┆ l   ┆ l   │
                │     ┆     ┆ pli ┆     ┆ 789 ┆ //w ┆ er  ┆ l   ┆ 'un ┆     ┆ 789 ┆     ┆     │
                │     ┆     ┆ cat ┆     ┆ 012 ┆ ww. ┆     ┆     ┆ iqu ┆     ┆ 012 ┆     ┆     │
                │     ┆     ┆ es_ ┆     ┆ 345 ┆ con ┆     ┆     ┆ e   ┆     ┆ 345 ┆     ┆     │
                │     ┆     ┆ in_ ┆     ┆ 678 ┆ sum ┆     ┆     ┆ ide ┆     ┆ 678 ┆     ┆     │
                │     ┆     ┆ dat ┆     ┆ 90  ┆ erf ┆     ┆     ┆ nti ┆     ┆ 90  ┆     ┆     │
                │     ┆     ┆ ase ┆     ┆     ┆ ina ┆     ┆     ┆ fie ┆     ┆     ┆     ┆     │
                │     ┆     ┆ t   ┆     ┆     ┆ nce ┆     ┆     ┆ r'  ┆     ┆     ┆     ┆     │
                │     ┆     ┆     ┆     ┆     ┆ .go ┆     ┆     ┆ may ┆     ┆     ┆     ┆     │
                │     ┆     ┆     ┆     ┆     ┆ …   ┆     ┆     ┆ …   ┆     ┆     ┆     ┆     │
                │ Err ┆ E30 ┆ uid ┆ 3   ┆ 123 ┆ htt ┆ reg ┆ Log ┆ *   ┆ uid ┆ 123 ┆ nul ┆ nul │
                │ or  ┆ 00  ┆ .du ┆     ┆ 456 ┆ ps: ┆ ist ┆ ica ┆ Any ┆     ┆ 456 ┆ l   ┆ l   │
                │     ┆     ┆ pli ┆     ┆ 789 ┆ //w ┆ er  ┆ l   ┆ 'un ┆     ┆ 789 ┆     ┆     │
                │     ┆     ┆ cat ┆     ┆ 012 ┆ ww. ┆     ┆     ┆ iqu ┆     ┆ 012 ┆     ┆     │
                │     ┆     ┆ es_ ┆     ┆ 345 ┆ con ┆     ┆     ┆ e   ┆     ┆ 345 ┆     ┆     │
                │     ┆     ┆ in_ ┆     ┆ 678 ┆ sum ┆     ┆     ┆ ide ┆     ┆ 678 ┆     ┆     │
                │     ┆     ┆ dat ┆     ┆ 90  ┆ erf ┆     ┆     ┆ nti ┆     ┆ 90  ┆     ┆     │
                │     ┆     ┆ ase ┆     ┆     ┆ ina ┆     ┆     ┆ fie ┆     ┆     ┆     ┆     │
                │     ┆     ┆ t   ┆     ┆     ┆ nce ┆     ┆     ┆ r'  ┆     ┆     ┆     ┆     │
                │     ┆     ┆     ┆     ┆     ┆ .go ┆     ┆     ┆ may ┆     ┆     ┆     ┆     │
                │     ┆     ┆     ┆     ┆     ┆ …   ┆     ┆     ┆ …   ┆     ┆     ┆     ┆     │
                │ Err ┆ E20 ┆ amo ┆ 4   ┆ 123 ┆ htt ┆ mul ┆ Log ┆ *   ┆ act ┆ 1   ┆ amo ┆     │
                │ or  ┆ 08  ┆ unt ┆     ┆ 456 ┆ ps: ┆ ti- ┆ ica ┆ Whe ┆ ion ┆     ┆ unt ┆     │
                │     ┆     ┆ _ap ┆     ┆ 789 ┆ //w ┆ fie ┆ l   ┆ n   ┆ _ta ┆     ┆ _ap ┆     │
                │     ┆     ┆ pro ┆     ┆ 012 ┆ ww. ┆ ld  ┆     ┆ 'ac ┆ ken ┆     ┆ pro ┆     │
                │     ┆     ┆ ved ┆     ┆ 345 ┆ con ┆     ┆     ┆ tio ┆     ┆     ┆ ved ┆     │
                │     ┆     ┆ .co ┆     ┆ 678 ┆ sum ┆     ┆     ┆ n   ┆     ┆     ┆     ┆     │
                │     ┆     ┆ ndi ┆     ┆ 91  ┆ erf ┆     ┆     ┆ tak ┆     ┆     ┆     ┆     │
                │     ┆     ┆ tio ┆     ┆     ┆ ina ┆     ┆     ┆ en' ┆     ┆     ┆     ┆     │
                │     ┆     ┆ nal ┆     ┆     ┆ nce ┆     ┆     ┆ doe ┆     ┆     ┆     ┆     │
                │     ┆     ┆ _fi ┆     ┆     ┆ .go ┆     ┆     ┆ s   ┆     ┆     ┆     ┆     │
                │     ┆     ┆ …   ┆     ┆     ┆ …   ┆     ┆     ┆ **n ┆     ┆     ┆     ┆     │
                │     ┆     ┆     ┆     ┆     ┆     ┆     ┆     ┆ …   ┆     ┆     ┆     ┆     │
                └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
            """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = df_to_str(self.findings_df)
        assert actual_output == expected_output

    def test_output_table(self):
        expected_output = dedent(
            """
                ╭────┬────────────────────────────────────────────────────┬────────────────────────────────────────────────────┬────────────────────────────────────────────────────╮
                │    │ 0                                                  │ 1                                                  │ 2                                                  │
                ├────┼────────────────────────────────────────────────────┼────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
                │  0 │ Error                                              │ Error                                              │ Error                                              │
                │  1 │ E3000                                              │ E3000                                              │ E2008                                              │
                │  2 │ uid.duplicates_in_dataset                          │ uid.duplicates_in_dataset                          │ amount_approved.conditional_field_conflict         │
                │  3 │ 12345678901234567890                               │ 12345678901234567890                               │ 12345678901234567891                               │
                │  4 │ https://www.consumerfinance.gov/data-research/smal │ https://www.consumerfinance.gov/data-research/smal │ https://www.consumerfinance.gov/data-research/smal │
                │  5 │ register                                           │ register                                           │ multi-field                                        │
                │  6 │ Logical                                            │ Logical                                            │ Logical                                            │
                │  7 │ * Any 'unique identifier' may **not** be used in m │ * Any 'unique identifier' may **not** be used in m │ * When 'action taken' does **not** equal 1 (origin │
                │  8 │ uid                                                │ uid                                                │ action_taken                                       │
                │  9 │ 12345678901234567890                               │ 12345678901234567890                               │ 1                                                  │
                │ 10 │                                                    │                                                    │ amount_approved                                    │
                │ 11 │                                                    │                                                    │                                                    │
                ╰────┴────────────────────────────────────────────────────┴────────────────────────────────────────────────────┴────────────────────────────────────────────────────╯
            """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = df_to_table(self.findings_df)
        assert actual_output == expected_output

    def test_output_csv(self):
        expected_output = dedent(
            """
                "validation_type","validation_id","validation_name","row","unique_identifier","fig_link","scope","phase","validation_description","field_1","value_1","field_2","value_2"
                "Error","E2008","amount_approved.conditional_field_conflict",4,"12345678901234567891","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.2.7","multi-field","Logical","* When 'action taken' does **not** equal 1 (originated) or 
                2 (approved but not accepted), 'amount approved or originated' must be blank.
                * When 'action taken' equals 1 or 2, 'amount approved or originated' must **not** be blank.
                ","action_taken","1","amount_approved",""
                "Error","E3000","uid.duplicates_in_dataset",2,"12345678901234567890","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1","register","Logical","* Any 'unique identifier' may **not** be used in more than one 
                record within a small business lending application register.
                ","uid","12345678901234567890",,
                "Error","E3000","uid.duplicates_in_dataset",3,"12345678901234567890","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1","register","Logical","* Any 'unique identifier' may **not** be used in more than one 
                record within a small business lending application register.
                ","uid","12345678901234567890",,
            """
        ).strip(
            '\n'
        )  # noqa: E501

        actual_output = df_to_csv(self.findings_df)
        assert actual_output.strip('\n') == expected_output

    def test_empty_results_json(self):
        expected_output = ujson.dumps([], indent=4, escape_forward_slashes=False)
        actual_output = df_to_json(pl.DataFrame())

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
                        "fields": [{"name": "action_taken", "value": "1"}, {"name": "amount_approved", "value": ""}],
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

        actual_output = df_to_json(self.findings_df)
        assert actual_output == expected_output

    def test_download_csv(self):
        expected_output = dedent(
            """
                validation_type,validation_id,validation_name,row,unique_identifier,fig_link,validation_description,field_1,value_1,field_2,value_2
                "Error","E2008","amount_approved.conditional_field_conflict",4,"12345678901234567891","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.2.7","* When 'action taken' does **not** equal 1 (originated) or 
                2 (approved but not accepted), 'amount approved or originated' must be blank.
                * When 'action taken' equals 1 or 2, 'amount approved or originated' must **not** be blank.
                ","action_taken","1","amount_approved",""
                "Error","E3000","uid.duplicates_in_dataset",2,"12345678901234567890","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1","* Any 'unique identifier' may **not** be used in more than one 
                record within a small business lending application register.
                ","uid","12345678901234567890",,
                "Error","E3000","uid.duplicates_in_dataset",3,"12345678901234567890","https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4.3.1","* Any 'unique identifier' may **not** be used in more than one 
                record within a small business lending application register.
                ","uid","12345678901234567890",,
            """
        ).strip('\n')

        actual_output = df_to_download(self.findings_df).decode('utf-8')
        assert actual_output.strip() == expected_output

    def test_empty_download_csv(self):
        expected_output = dedent(
            """
            "validation_type","validation_id","validation_name","row","unique_identifier","fig_link","validation_description"
            """
        ).strip('\n')

        actual_output = df_to_download(pl.DataFrame()).decode('utf-8')
        assert actual_output.strip() == expected_output
