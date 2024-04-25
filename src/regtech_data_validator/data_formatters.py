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
    output_json = []

    if not df.empty:
        df.reset_index(drop=True, inplace=True)
        findings_json = json.loads(df.to_json(orient='columns'))

        grouped_data = {}
        for i in range(len(findings_json['record_no'])):
            validation_id = findings_json['validation_id'][str(i)]
            if validation_id not in grouped_data:
                grouped_data[validation_id] = []
            grouped_data[validation_id].append(
                {
                    'record_no': findings_json['record_no'][str(i)],
                    'uid': findings_json['uid'][str(i)],
                    'field_name': findings_json['field_name'][str(i)],
                    'field_value': findings_json['field_value'][str(i)],
                }
            )

        for validation_id, records in grouped_data.items():
            for key, value in findings_json['validation_id'].items():
                if validation_id == value:
                    validation_key = key
                    break
            validation_info = {
                'validation': {
                    'id': validation_id,
                    'name': findings_json['validation_name'][validation_key],
                    'description': findings_json['validation_desc'][validation_key],
                    'severity': findings_json['validation_severity'][validation_key],
                    'scope': findings_json['scope'][validation_key],
                    'fig_link': findings_json['fig_link'][validation_key],
                },
                'records': [],
            }
            records_dict = {}
            for record in records:
                record_no = record['record_no']
                if record_no not in records_dict:
                    records_dict[record_no] = {'record_no': record['record_no'], 'uid': record['uid'], 'fields': []}
                records_dict[record_no]['fields'].append({'name': record['field_name'], 'value': record['field_value']})
            validation_info['records'] = list(records_dict.values())
            for record in validation_info['records']:
                if len(record['fields']) == 2:
                    record['fields'][0], record['fields'][1] = record['fields'][1], record['fields'][0]
            output_json.append(validation_info)

        output_json = sorted(output_json, key=lambda x: x['validation']['id'])
    return json.dumps(output_json, indent=4)
