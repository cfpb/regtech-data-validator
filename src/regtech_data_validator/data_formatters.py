import csv
import json
import pandas as pd

from tabulate import tabulate

more_than_2_fields = ["E2014", "E2015", "W2035", "W2036", "W2037", "W2038", "W2039"]


def df_to_download(df: pd.DataFrame) -> str:
    if df.empty:
        # return headers of csv for 'emtpy' report
        return "validation_type,validation_id,validation_name,row,unique_identifier,fig_link,validation_description"
    else:
        df.reset_index(drop=True, inplace=True)
        df = df.drop(["scope"], axis=1)

        df['field_number'] = (
            df.groupby(
                [
                    "validation_severity",
                    "validation_id",
                    "validation_name",
                    "record_no",
                    "uid",
                    "fig_link",
                    "validation_desc",
                ]
            ).cumcount()
            + 1
        )
        df_pivot = df.pivot_table(
            index=[
                "validation_severity",
                "validation_id",
                "validation_name",
                "record_no",
                "uid",
                "fig_link",
                "validation_desc",
            ],
            columns="field_number",
            values=["field_name", "field_value"],
            aggfunc="first",
        ).reset_index()

        df_pivot.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df_pivot.columns]

        df_pivot.rename(
            columns={f"field_name_{i}": f"field_{i}" for i in range(1, len(df_pivot.columns) // 2 + 1)}, inplace=True
        )
        df_pivot.rename(
            columns={f"field_value_{i}": f"value_{i}" for i in range(1, len(df_pivot.columns) // 2 + 1)}, inplace=True
        )
        df_pivot.rename(
            columns={
                "record_no": "row",
                "validation_severity": "validation_type",
                "uid": "unique_identifier",
                "validation_desc": "validation_description",
            },
            inplace=True,
        )

        field_columns = [col for col in df_pivot.columns if col.startswith('field_')]
        value_columns = [col for col in df_pivot.columns if col.startswith('value_')]
        sorted_columns = [col for pair in zip(field_columns, value_columns) for col in pair]

        df_pivot = df_pivot[
            [
                "validation_type",
                "validation_id",
                "validation_name",
                "row",
                "unique_identifier",
                "fig_link",
                "validation_description",
            ]
            + sorted_columns
        ]

        df_pivot['row'] += 1

        return df_pivot.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)


def df_to_str(df: pd.DataFrame) -> str:
    with pd.option_context('display.width', None, 'display.max_rows', None):
        return str(df)


def df_to_csv(df: pd.DataFrame) -> str:
    return df.to_csv()


def df_to_table(df: pd.DataFrame) -> str:
    # trim field_value field to just 50 chars, similar to DataFrame default
    table_df = df.drop(columns='validation_desc').sort_index()
    table_df['field_value'] = table_df['field_value'].str[0:50]

    # NOTE: `type: ignore` because tabulate package typing does not include Pandas
    #        DataFrame as input, but the library itself does support it. ¯\_(ツ)_/¯
    return tabulate(table_df, headers='keys', showindex=True, tablefmt='rounded_outline')  # type: ignore


def df_to_json(df: pd.DataFrame) -> str:
    findings_json = []

    if not df.empty:

        for _, group_df in df.groupby(['validation_id']):
            v_head = group_df.iloc[0]

            finding_json = {
                'validation': {
                    'id': v_head['validation_id'],
                    'name': v_head['validation_name'],
                    'description': v_head['validation_desc'],
                    'severity': v_head['validation_severity'],
                    'scope': v_head['scope'],
                    'fig_link': v_head['fig_link'],
                },
                'records': [],
            }
            findings_json.append(finding_json)

            for _, rec_df in group_df.groupby(by='record_no'):
                rec = rec_df.iloc[0]
                record_json = {'record_no': int(rec['record_no']), 'uid': rec['uid'], 'fields': []}
                finding_json['records'].append(record_json)

                fields = rec_df.iterrows() if v_head['validation_id'] in more_than_2_fields else rec_df[::-1].iterrows()
                for _, field_data in fields:
                    record_json['fields'].append({'name': field_data['field_name'], 'value': field_data['field_value']})
    return json.dumps(findings_json, indent=4)
