import csv
import ujson
import pandas as pd

from tabulate import tabulate

from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei
from regtech_data_validator.checks import SBLCheck

MAX_JSON_RECORDS = 10000


def get_all_checks():
    return [
        check
        for phases in get_phase_1_and_2_validations_for_lei().values()
        for checks in phases.values()
        for check in checks
    ]


def find_check(group_name, checks):
    gen = (check for check in checks if check.title == group_name)
    return next(gen)


def df_to_download(df: pd.DataFrame, total_errors: int, max_errors: int = 1000000) -> str:
    header = "validation_type,validation_id,validation_name,row,unique_identifier,fig_link,validation_description,"
    if df.empty:
        # return headers of csv for 'emtpy' report
        return header
    else:
        total_csv = ""
        largest_field_count = 1
        checks = get_all_checks()
        df.reset_index(drop=True, inplace=True)

        for validation_id, group in df.groupby("validation_id"):
            group['field_number'] = (
                group.groupby(
                    [
                        "record_no",
                        "uid",
                    ]
                ).cumcount()
                + 1
            )
            df_pivot = group.pivot_table(
                index=[
                    "record_no",
                    "uid",
                ],
                columns="field_number",
                values=["field_name", "field_value"],
                aggfunc="first",
            ).reset_index()

            df_pivot.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df_pivot.columns]

            check = find_check(validation_id, checks)
            df_pivot['validation_type'] = check.severity
            df_pivot['validation_description'] = check.description
            df_pivot['validation_name'] = check.name
            df_pivot['fig_link'] = check.fig_link

            df_pivot.rename(
                columns={
                    "record_no": "row",
                    "uid": "unique_identifier",
                },
                inplace=True,
            )
            field_columns = [col for col in df_pivot.columns if col.startswith('field_name_')]
            value_columns = [col for col in df_pivot.columns if col.startswith('field_value_')]
            sorted_columns = [col for pair in zip(field_columns, value_columns) for col in pair]
            group_field_count = len(field_columns)
            largest_field_count = largest_field_count if group_field_count <= largest_field_count else group_field_count
            # swap two-field errors/warnings to keep order of FIG
            if len(field_columns) == 2:
                f1_data = df_pivot['field_name_1']
                v1_data = df_pivot['field_value_1']
                df_pivot['field_name_1'] = df_pivot['field_name_2']
                df_pivot['field_value_1'] = df_pivot['field_value_2']
                df_pivot['field_name_2'] = f1_data
                df_pivot['field_value_2'] = v1_data
            df_pivot['validation_id'] = validation_id

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
            total_csv += df_pivot.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC, header=False)

        field_headers = []
        for i in range(largest_field_count):
            field_headers.append(f"field_{i+1}")
            field_headers.append(f"value_{i+1}")
        header += ",".join(field_headers) + "\n"

        if total_errors and total_errors > max_errors:
            header += f"The submission contained {total_errors}, but only {max_errors} will be displayed in the download report.  Fix the current errors and resubmit to see more.\n"

        csv_data = header + total_csv
        return csv_data


def df_to_str(df: pd.DataFrame) -> str:
    with pd.option_context('display.width', None, 'display.max_rows', None):
        return str(df)


def df_to_csv(df: pd.DataFrame) -> str:
    return df.to_csv()


def df_to_table(df: pd.DataFrame) -> str:
    # trim field_value field to just 50 chars, similar to DataFrame default
    table_df = df.sort_index()
    table_df['field_value'] = table_df['field_value'].str[0:50]

    # NOTE: `type: ignore` because tabulate package typing does not include Pandas
    #        DataFrame as input, but the library itself does support it. ¯\_(ツ)_/¯
    return tabulate(table_df, headers='keys', showindex=True, tablefmt='rounded_outline')  # type: ignore


def df_to_json(df: pd.DataFrame, max_records: int = 10000, max_group_size: int = None) -> str:
    return ujson.dumps(df_to_dicts(df, max_records, max_group_size), indent=4, escape_forward_slashes=False)


def df_to_dicts(df: pd.DataFrame, max_records: int = 10000, max_group_size: int = None) -> list[dict]:
    # grouping and processing keeps the process from crashing on really large error
    # dataframes (millions of errors).  We can't chunk because could cause splitting
    # related validation data across chunks, without having to add extra processing
    # for tying those objects back together.  Grouping adds a little more processing
    # time for smaller datasets but keeps really larger ones from crashing.

    checks = get_all_checks()

    json_results = []
    if not df.empty:
        grouped_df = df.groupby('validation_id', group_keys=False)
        if not max_group_size:
            total_errors_per_group = calculate_group_chunk_sizes(grouped_df, max_records)
        else:
            total_errors_per_group = {}
            for group_name, group_data in grouped_df:
                total_errors_per_group[group_name] = max_group_size
        for validation_id, group in df.groupby("validation_id"):
            check = find_check(validation_id, checks)
            truncated_group = truncate_validation_group_records(group, total_errors_per_group[validation_id])
            json_results.append(process_chunk(truncated_group, validation_id, check))
        json_results = sorted(json_results, key=lambda x: x['validation']['id'])
    return json_results


def calculate_group_chunk_sizes(grouped_df, max_records):
    # This function is similar to create_schemas.trim_down_errors but focuses on number of
    # records per validation id.  It uses a ratio relative to total errors to determine
    # each group's adjusted errors relative to max_records, and then adjusts to hit max.
    error_counts = {}
    for group_name, group_data in grouped_df:
        error_counts[group_name] = len(group_data["record_no"].unique())
    total_error_count = sum(error_counts.values())

    if total_error_count > max_records:
        error_ratios = [(count / total_error_count) for count in error_counts.values()]
        new_counts = [int(max_records * prop) for prop in error_ratios]
        # Adjust the totals by 1, but within the original number of errors per error id,
        # until we hit the max
        if sum(new_counts) < max_records:
            while sum(new_counts) < max_records:
                for i in range(len(new_counts)):
                    if new_counts[i] < list(error_counts.values())[i]:
                        new_counts[i] = new_counts[i] + 1
                        if sum(new_counts) == max_records:
                            break

        error_counts = dict(zip(error_counts.keys(), new_counts))
    return error_counts


# Cuts off the number of records.  Can't just 'head' on the group due to the dataframe structure.
# So this function uses the group error counts to truncate on record numbers
def truncate_validation_group_records(group, group_size):
    unique_record_nos = group['record_no'].unique()[:group_size]
    truncated_group = group[group['record_no'].isin(unique_record_nos)]
    return truncated_group


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
