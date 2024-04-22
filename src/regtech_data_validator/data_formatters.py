import json
import pandas as pd

from tabulate import tabulate

more_than_2_fields = ["E2014", "E2015", "W2035", "W2036", "W2037", "W2038", "W2039"]


def df_to_download(df: pd.DataFrame) -> str:
    highest_field_count = 0
    full_csv = []
    if not df.empty:

        for _, group_df in df.groupby(['validation_id', 'record_no']):
            v_head = group_df.iloc[0]
            row_data = [
                v_head['validation_severity'],
                v_head['validation_id'],
                v_head['validation_name'],
                str(v_head['record_no'] + 1),
                v_head['uid'],
                v_head['fig_link'],
                f"\"{v_head['validation_desc']}\"",
            ]
            current_count = 0
            fields = group_df.iterrows() if v_head['validation_id'] in more_than_2_fields else group_df[::-1].iterrows()
            for _, field_data in fields:
                row_data.extend([field_data['field_name'], field_data['field_value']])
                current_count += 1

            full_csv.append(",".join(row_data))
            highest_field_count = current_count if current_count > highest_field_count else highest_field_count

    field_headers = []
    for i in range(highest_field_count):
        field_headers.append(f"field_{i+1}")
        field_headers.append(f"value_{i+1}")
    full_csv.insert(
        0,
        ",".join(
            [
                "validation_type",
                "validation_id",
                "validation_name",
                "row",
                "unique_identifier",
                "fig_link",
                "validation_description",
            ]
            + field_headers
        ),
    )
    csv_string = "\n".join(full_csv)

    return csv_string


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
