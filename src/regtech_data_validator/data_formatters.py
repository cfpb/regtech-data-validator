import json
import pandas as pd

from tabulate import tabulate

def df_to_download(df: pd.DataFrame) -> str:
    return df.to_csv(columns=['validation_severity', 'validation_id', 'record_no', 'uid', 'validation_desc', 'fig_anchor'])

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
    findings_by_v_id_df = df.reset_index().set_index(['validation_id', 'record_no', 'field_name'])

    for v_id_idx, v_id_df in findings_by_v_id_df.groupby(by='validation_id'):
        v_head = v_id_df.iloc[0]

        finding_json = {
            'validation': {
                'id': v_id_idx,
                'name': v_head.at['validation_name'],
                'description': v_head.at['validation_desc'],
                'severity': v_head.at['validation_severity'],
            },
            'records': [],
        }
        findings_json.append(finding_json)

        for rec_idx, rec_df in v_id_df.groupby(by='record_no'):
            record_json = {'record_no': rec_idx, 'fields': []}
            finding_json['records'].append(record_json)

            for field_idx, field_df in rec_df.groupby(by='field_name'):
                field_head = field_df.iloc[0]
                record_json['fields'].append({'name': field_idx, 'value': field_head.at['field_value']})

    json_str = json.dumps(findings_json, indent=4)

    return json_str
