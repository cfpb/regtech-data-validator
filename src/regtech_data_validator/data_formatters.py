import csv
import ujson
import pandas as pd

from tabulate import tabulate

from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei
from regtech_data_validator.checks import SBLCheck
import sys

def get_all_checks():
    return [check for phases in get_phase_1_and_2_validations_for_lei().values() for checks in phases.values() for check in checks]

'''
def df_to_download(df: pd.DataFrame) -> str:
    full_csv = ["validation_type,validation_id,validation_name,row,unique_identifier,fig_link,validation_description,"]
    if df.empty:
        # return headers of csv for 'emtpy' report
        return full_csv[0]
    else:
        json_dict = df_to_dicts(df)
        highest_field_count = 0
        for v in json_dict:
            validation = v['validation']
            current_count = 0
            for record in v['records']:
                row_data = [validation['severity'], validation['id'], validation['name'], str(record['record_no'] + 1), record['uid'], validation['fig_link'], validation['description']]
                for field in record['fields']:
                    row_data.extend([field['name'],field['value']])
                    current_count += 1
                full_csv.append(",".join(f'"{w}"' for w in row_data))
            highest_field_count = current_count if current_count > highest_field_count else highest_field_count
            
        field_headers = []
        for i in range(highest_field_count):
            field_headers.append(f"field_{i+1}")
            field_headers.append(f"value_{i+1}")
        full_csv[0] = full_csv[0] + ",".join(field_headers)
        print(f"full_csv list size: {(sys.getsizeof(full_csv) / 1024 / 1024)}")
        csv_string = "\n".join(full_csv)
        print(f"CSV string memory size: {(sys.getsizeof(csv_string) / 1024 / 1024)}")
        return csv_string
'''       
        

def df_to_download(df: pd.DataFrame) -> str:
    if df.empty:
        # return headers of csv for 'emtpy' report
        return "validation_type,validation_id,validation_name,row,unique_identifier,fig_link,validation_description"
    else:
        checks = get_all_checks()
        df.reset_index(drop=True, inplace=True)
        #df = df.drop(["scope"], axis=1)
        df['field_number'] = (
            df.groupby(
                [
                    "validation_id",
                    "record_no",
                    "uid",
                ]
            ).cumcount()
            + 1
        )
        df_pivot = df.pivot_table(
            index=[
                "validation_id",
                "record_no",
                "uid",
            ],
            columns="field_number",
            values=["field_name", "field_value"],
            aggfunc="first",
        ).reset_index()
        '''
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
        '''
        df_pivot.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df_pivot.columns]

        df_pivot.rename(
            columns={f"field_name_{i}": f"field_{i}" for i in range(1, len(df_pivot.columns) // 2 + 1)}, inplace=True
        )
        df_pivot.rename(
            columns={f"field_value_{i}": f"value_{i}" for i in range(1, len(df_pivot.columns) // 2 + 1)}, inplace=True
        )

        distinct_ids = df_pivot['validation_id'].unique()
        #data_map = {}
        for id in distinct_ids:
            check = find_check(id, checks)
            df_pivot.loc[df_pivot['validation_id'] == id, 'validation_type'] = check.severity
            df_pivot.loc[df_pivot['validation_id'] == id, 'validation_description'] = check.description
            df_pivot.loc[df_pivot['validation_id'] == id, 'validation_name'] = check.name
            df_pivot.loc[df_pivot['validation_id'] == id, 'fig_link'] = check.fig_link
            #check = find_check(id, checks)
            #data_map[id] = {
            #    "validation_type": check.severity,
            #    "validation_description": check.description,
            #    "validation_name": check.name,
            #    "fig_link": check.fig_link
            #}
        
        #df_pivot = df_pivot.join(df_pivot['validation_id'].apply(lambda x: pd.Series(data_map.get(x, {}))))
        
        '''
        df_pivot.rename(
            columns={
                "record_no": "row",
                "validation_severity": "validation_type",
                "uid": "unique_identifier",
                "validation_desc": "validation_description",
            },
            inplace=True,
        )
        '''
        df_pivot.rename(
            columns={
                "record_no": "row",
                "uid": "unique_identifier",
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
    
    checks = get_all_checks()

    json_results = []
    if not df.empty:
        grouped_df = df.groupby('validation_id')
        for group_name, group_data in grouped_df:
            check = find_check(group_name, checks)
            json_results.append(process_chunk(group_data.head(55), group_name, check))
        json_results = sorted(json_results, key=lambda x: x['validation']['id'])
    print(f"JSON list memory size: {(sys.getsizeof(json_results) / 1024 / 1024)}")
    return json_results

def find_check(group_name, checks):
    gen = (
        check for check in checks if check.title == group_name
    )
    return next(gen)

def process_chunk(df: pd.DataFrame, validation_id: str, check: SBLCheck) -> [dict]:
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
            'name': check.name,
            'description': check.description,
            'severity': check.severity,
            'scope': check.scope,
            'fig_link': check.fig_link,
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
