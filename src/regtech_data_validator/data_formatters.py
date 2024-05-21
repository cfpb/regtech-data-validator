import csv
import ujson
import pandas as pd

from tabulate import tabulate


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
    return ujson.dumps(df_to_dicts(df), indent=4, escape_forward_slashes=False)

def df_to_dicts(df: pd.DataFrame) -> list[dict]:
    # grouping and processing keeps the process from crashing on really large error
    # dataframes (millions of errors).  We can't chunk because could cause splitting
    # related validation data across chunks, without having to add extra processing
    # for tying those objects back together.  Grouping adds a little more processing
    # time for smaller datasets but keeps really larger ones from crashing.
    json_results = []
    if not df.empty:
        grouped_df = df.groupby('validation_id')
        for group_name, group_data in grouped_df:
            json_results.append(process_chunk(group_data, group_name))
        json_results = sorted(json_results, key=lambda x: x['validation']['id'])
    return json_results


def process_chunk(df: pd.DataFrame, validation_id: str) -> [dict]:
    df.reset_index(drop=True, inplace=True)
    findings_json = ujson.loads(df.to_json(orient='columns'))
    grouped_data = []
    for i in range(len(findings_json['record_no'])):
        grouped_data.append(
            {
                'record_no': findings_json['record_no'][str(i)],
                'uid': findings_json['uid'][str(i)],
                'field_name': findings_json['field_name'][str(i)],
                'field_value': findings_json['field_value'][str(i)],
            }
        )

    validation_info = {
        'validation': {
            'id': validation_id,
            'name': findings_json['validation_name']['0'],
            'description': findings_json['validation_desc']['0'],
            'severity': findings_json['validation_severity']['0'],
            'scope': findings_json['scope']['0'],
            'fig_link': findings_json['fig_link']['0'],
        },
        'records': [],
    }
    records_dict = {}
    for record in grouped_data:
        record_no = record['record_no']
        if record_no not in records_dict:
            records_dict[record_no] = {'record_no': record['record_no'], 'uid': record['uid'], 'fields': []}
        records_dict[record_no]['fields'].append({'name': record['field_name'], 'value': record['field_value']})
    validation_info['records'] = list(records_dict.values())

    for record in validation_info['records']:
        if len(record['fields']) == 2:
            record['fields'][0], record['fields'][1] = record['fields'][1], record['fields'][0]

    return validation_info
