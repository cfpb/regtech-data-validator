import csv
import math
import ujson
import pandas as pd
import polars as pl

from tabulate import tabulate

from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei, get_phase_2_register_validations
from regtech_data_validator.checks import SBLCheck

from datetime import datetime
from functools import partial
from collections import OrderedDict


def get_all_checks():
    all_checks = [
        check
        for phases in get_phase_1_and_2_validations_for_lei().values()
        for checks in phases.values()
        for check in checks
    ]
    all_checks.extend([
        check
        for phases in get_phase_2_register_validations().values()
        for checks in phases.values()
        for check in checks
    ])
    return all_checks


def find_check(group_name, checks):
    gen = (check for check in checks if check.title == group_name)
    return next(gen)


def df_to_download(df: pd.DataFrame, warning_count: int = 0, error_count: int = 0, max_errors: int = 1000000) -> str:
    header = "validation_type,validation_id,validation_name,row,unique_identifier,fig_link,validation_description,"
    if df.is_empty():
        # return headers of csv for 'emtpy' report
        return header
    else:
        checks = get_all_checks()
        final_df = pl.LazyFrame()

        df = df.with_columns(pl.col('validation_id').cast(pl.Categorical(ordering='lexical'))).sort('validation_id')

        for validation_id, group in df.group_by("validation_id", maintain_order=True):
            group = group.with_columns(pl.col('record_no').cumcount().over(['record_no', 'uid']).alias('field_number'))
            df_pivot = group.pivot(
                index=[
                    "record_no",
                    "uid",
                ],
                columns="field_number",
                values=["field_name", "field_value"],
                aggregate_function="first",
            )
            df_pivot.columns = [col.replace('field_name_field_number_','field_').replace('field_value_field_number_', 'value_') if ('field_name_field_number_' in col or 'field_value_field_number_' in col) else col for col in df_pivot.columns]

            check = find_check(validation_id, checks)
            df_pivot = df_pivot.with_columns(
                validation_type = pl.lit(check.severity),
                validation_description = pl.lit(check.description),
                validation_name = pl.lit(check.name),
                fig_link = pl.lit(check.fig_link)
            )

            df_pivot = df_pivot.rename(
                mapping={
                    "record_no": "row",
                    "uid": "unique_identifier",
                }
            )
            field_columns = [col for col in df_pivot.columns if col.startswith('field_')]
            value_columns = [col for col in df_pivot.columns if col.startswith('value_')]
            sorted_columns = [col for pair in zip(field_columns, value_columns) for col in pair]

            # swap two-field errors/warnings to keep order of FIG
            if len(field_columns) == 2:
                f1_data = df_pivot['field_1']
                v1_data = df_pivot['value_1']
                df_pivot = df_pivot.with_columns(
                    field_name_1 = pl.col('field_2'),
                    field_value_1 = pl.col('value_2'),
                    field_name_2 = pl.Series(f1_data),
                    field_value_2 = pl.Series(v1_data)
                )
            df_pivot = df_pivot.with_columns(validation_id = pl.lit(validation_id))

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

            df_pivot = df_pivot.with_columns(row = pl.col('row') + 1)
            final_df = pl.concat([final_df, df_pivot.lazy()], how="diagonal")

        total_errors = warning_count + error_count
        error_type = "errors"
        if warning_count > 0:
            if error_count > 0:
                error_type = "errors and warnings"
            else:
                error_type = "warnings"

        if total_errors and total_errors > max_errors:
            msg = {"validation_type":f"Your register contains {total_errors} {error_type}, however, only {max_errors} records are displayed in this report. To see additional {error_type}, correct the listed records, and upload a new file."}
            msg_df = pl.LazyFrame([msg])
            final_df = pl.concat([msg_df, final_df], how="diagonal")
        final_df.sink_csv("test_sink.csv", quote_style='non_numeric')
    
    
def df_to_str(df: pl.DataFrame) -> str:
    with pl.option_context('display.width', None, 'display.max_rows', None):
        return str(df)


def df_to_csv(df: pl.DataFrame) -> str:
    #return df.to_csv()
    df.write_csv("syntax_errors.csv")
    return "Done"


def df_to_table(df: pl.DataFrame) -> str:
    # trim field_value field to just 50 chars, similar to DataFrame default
    table_df = df.sort_index()
    table_df['field_value'] = table_df['field_value'].str[0:50]

    # NOTE: `type: ignore` because tabulate package typing does not include Pandas
    #        DataFrame as input, but the library itself does support it. ¯\_(ツ)_/¯
    return tabulate(table_df, headers='keys', showindex=True, tablefmt='rounded_outline')  # type: ignore


def df_to_json(df: pl.DataFrame, max_records: int = 10000, max_group_size: int = None) -> str:
    start = datetime.now()
    results = df_to_dicts(df, max_records, max_group_size)
    print(f"JSON Results took {(datetime.now() - start).total_seconds()} seconds")
    return ujson.dumps(results, indent=4, escape_forward_slashes=False)


def df_to_dicts(df: pl.DataFrame, max_records: int = 10000, max_group_size: int = None) -> list[dict]:
    # grouping and processing keeps the process from crashing on really large error
    # dataframes (millions of errors).  We can't chunk because could cause splitting
    # related validation data across chunks, without having to add extra processing
    # for tying those objects back together.  Grouping adds a little more processing
    # time for smaller datasets but keeps really larger ones from crashing.
    fun_start = datetime.now()
    print(f"Starting df_to_dict at {fun_start}")
    checks = get_all_checks()
    trunc_procs = []
    chunk_procs = []
    loop_procs = []
    find_procs = []
    json_results = []
    result_append_procs = []
    if not df.is_empty():
        grouped_df = df.group_by('validation_id')
        if not max_group_size:
            total_errors_per_group = calculate_group_chunk_sizes(grouped_df, max_records)
        else:
            total_errors_per_group = {}
            for group_name, data in grouped_df:
                total_errors_per_group[group_name] = max_group_size
        print(f"Total Group Errors: {total_errors_per_group}")
        partial_process_group = partial(process_group_data, checks=checks, total_errors_per_group=total_errors_per_group, json_results=json_results)
        df.lazy().group_by('validation_id').map_groups(partial_process_group, schema=None).collect()
        '''
        for validation_id, group in grouped_df.__iter__():
            loop_start = datetime.now()
            print(f"Loop start: {loop_start}")
            check_start = datetime.now()
            check = find_check(validation_id, checks)
            find_procs.append((datetime.now() - check_start).total_seconds())
            t_start = datetime.now()
            truncated_group, need_to_truncate = truncate_validation_group_records(
                group, total_errors_per_group[validation_id]
            )
            trunc_procs.append((datetime.now() - t_start).total_seconds())
            p_start = datetime.now()
            group_json = process_chunk(truncated_group, validation_id, check)
            chunk_procs.append((datetime.now() - p_start).total_seconds())
            result_start = datetime.now()
            if group_json:
                group_json["validation"]["is_truncated"] = need_to_truncate
                json_results.append(group_json)
                result_append_procs.append((datetime.now() - result_start).total_seconds())
            loop_procs.append((datetime.now() - loop_start).total_seconds())
            print(f"loop time since start: {(datetime.now() - fun_start).total_seconds()} seconds")
            print(f"Loop end: {datetime.now()}")
        print(f"Finishing df_to_dict at {datetime.now()}")
        print(f"Find avg: {sum(find_procs)/len(find_procs)} for {len(find_procs)} finds, max: {max(find_procs)}")
        print(f"Trunc avg: {sum(trunc_procs)/len(trunc_procs)} for {len(trunc_procs)} truncs, max: {max(trunc_procs)}")
        print(f"Chunk avg: {sum(chunk_procs)/len(chunk_procs)} for {len(chunk_procs)} chunks, max: {max(chunk_procs)}")
        print(f"Result Append avg: {sum(result_append_procs)/len(result_append_procs)} for {len(result_append_procs)} appends, max: {max(result_append_procs)}")
        print(f"Loop avg: {sum(loop_procs)/len(loop_procs)} for {len(loop_procs)} loops, max: {max(loop_procs)}")
        sort_start = datetime.now()
        '''
        json_results = sorted(json_results, key=lambda x: x['validation']['id'])
        #print(f"Sort time: {(datetime.now() - sort_start).total_seconds()} seconds")
    return json_results

def process_group_data(group_df, checks, total_errors_per_group, json_results):
    validation_id = group_df['validation_id'].item(0)
    check = find_check(validation_id, checks)
    truncated_group, need_to_truncate = truncate_validation_group_records(
        group_df, total_errors_per_group[validation_id]
    )
    group_json = process_chunk(truncated_group, validation_id, check)
    if group_json:
        group_json["validation"]["is_truncated"] = need_to_truncate
        json_results.append(group_json)
    return group_df

def calculate_group_chunk_sizes(grouped_df, max_records):
    # This function is similar to create_schemas.trim_down_errors but focuses on number of
    # records per validation id.  It uses a ratio relative to total errors to determine
    # each group's adjusted errors relative to max_records, and then adjusts to hit max.
    error_counts = {}

    error_counts_df = grouped_df.agg(pl.col('record_no').n_unique().alias('error_count'))
    error_counts = OrderedDict(sorted(dict(zip(error_counts_df['validation_id'], error_counts_df['error_count'])).items()))
    print(f"Original Error Counts: {error_counts}")

    error_count_list = list(error_counts.values())
    total_error_count = sum(error_count_list)
    
    if total_error_count > max_records:
        error_ratios = [(count / total_error_count) for count in error_count_list]
        new_counts = [math.ceil(max_records * prop) for prop in error_ratios]
        # Adjust the counts in case we went over max.  This is very likely since we're using
        # ceil, unless we have an exact equality of the new counts.  Because of the use
        # of ceil, we will never have the sum of the new counts be less than max.
        if sum(new_counts) > max_records:
            while sum(new_counts) > max_records:
                # arbitrary reversal to contain errors in FIG order, if we need to remove
                # records from errors to fit max
                for i in reversed(range(len(new_counts))):
                    if new_counts[i] > 1:
                        new_counts[i] -= 1
                    # check if all the counts are equal to 1, then
                    # start removing those until we hit max
                    elif new_counts[i] == 1 and sum(new_counts) <= len(new_counts):
                        new_counts[i] -= 1
                    if sum(new_counts) == max_records:
                        break
        error_counts = dict(zip(error_counts.keys(), new_counts))
    return error_counts


# Cuts off the number of records.  Can't just 'head' on the group due to the dataframe structure.
# So this function uses the group error counts to truncate on record numbers
def truncate_validation_group_records(group, group_size):
    unique_record_nos = group['record_no'].unique()
    need_to_truncate = len(unique_record_nos) > group_size
    if need_to_truncate:
        unique_record_nos = unique_record_nos[:group_size]
    truncated_group = group.filter(group['record_no'].is_in(unique_record_nos))
    return truncated_group, need_to_truncate


def process_chunk(df: pl.DataFrame, validation_id: str, check: SBLCheck) -> [dict]:
    findings_json = ujson.loads(df.write_json(row_oriented=True))
    grouped_data = []
    if not findings_json:
        return

    for finding in findings_json:
        grouped_data.append(
            {
                'record_no': finding['record_no'],
                'uid': finding['uid'],
                'field_name': finding['field_name'],
                'field_value': finding['field_value'],
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
