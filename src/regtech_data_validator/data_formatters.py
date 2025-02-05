import ujson
import polars as pl

from typing import Dict, Any
from tabulate import tabulate

from functools import partial

from io import BytesIO

from regtech_data_validator.checks import SBLCheck
from regtech_data_validator.validation_results import ValidationPhase
from regtech_data_validator.phase_validations import (
    get_phase_1_schema_for_lei,
    get_phase_2_schema_for_lei,
    get_register_schema,
)


def find_check(group_name, checks):
    gen = (check for check in checks if check.title == group_name)
    return next(gen)


def get_checks(phase):
    if phase == ValidationPhase.SYNTACTICAL:
        syntax_schema = get_phase_1_schema_for_lei()
        checks = [check for col_schema in syntax_schema.columns.values() for check in col_schema.checks]
    else:
        logic_schema = get_phase_2_schema_for_lei()
        checks = [check for col_schema in logic_schema.columns.values() for check in col_schema.checks]
        register_schema = get_register_schema()
        checks.extend([check for col_schema in register_schema.columns.values() for check in col_schema.checks])
    return checks


# Takes the error dataframe, which is a bit obscure, and translates it to a format of:
# validation_type, validation_id, validation_name, row, unique_identifier, fig_link, validation_description, scope, field_#, value_#
# which corresponds to severity, error/warning code, name of error/warning, row number in sblar, UID, fig link,
# error/warning description (markdown formatted), single/multi/register, and the fields and values associated with the error/warning.
# Each row in the final dataframe represents all data for that one finding.
def format_findings(df: pl.DataFrame, phase, checks):
    final_df = pl.DataFrame()

    sorted_df = df.with_columns(pl.col('validation_id').cast(pl.Categorical(ordering='lexical'))).sort('validation_id')

    # validation_id is a tuple returned from the group_by, so we'll be getting [0] for the actual error/warning code
    for validation_id, group in sorted_df.group_by(["validation_id"], maintain_order=True):
        validation_id = validation_id[0]
        # in the error dataframe, each field is its own row, so count those and put them into field_name_field_number_#
        # and field_value_field_number_# columns to break out eventually to related field_# and value_#
        group = group.with_columns(pl.col('record_no').cum_count().over(['record_no', 'uid']).alias('field_number'))
        df_pivot = group.pivot(
            index=[
                "record_no",
                "uid",
            ],
            on="field_number",
            values=["field_name", "field_value"],
            aggregate_function="first",
        )
        df_pivot.columns = [
            (
                col.replace('field_name_', 'field_').replace('field_value_', 'value_')
                if ('field_name_' in col or 'field_value_' in col)
                else col
            )
            for col in df_pivot.columns
        ]

        check = find_check(validation_id, checks)
        # convert the SBLCheck data into column data
        df_pivot = df_pivot.with_columns(
            validation_type=pl.lit(check.severity.value),
            validation_id=pl.lit(validation_id),
            scope=pl.lit(check.scope),
            # validation_description=pl.lit(check.description),
            # validation_name=pl.lit(check.name),
            # fig_link=pl.lit(check.fig_link),
        ).rename(
            {
                "record_no": "row",
                "uid": "unique_identifier",
            }
        )
        # match field_1 with value_1, field_2 with value_2, etc
        field_columns = [col for col in df_pivot.columns if col.startswith('field_')]
        value_columns = [col for col in df_pivot.columns if col.startswith('value_')]
        sorted_columns = [col for pair in zip(field_columns, value_columns) for col in pair]

        # swap two-field errors/warnings to keep order of FIG
        if len(field_columns) == 2:
            df_pivot = df_pivot.with_columns(
                field_1=pl.col('field_2'),
                value_1=pl.col('value_2'),
                field_2=pl.col('field_1'),
                value_2=pl.col('value_1'),
            )

        # adjust row by 1 and concat group with final dataframe
        df_pivot = df_pivot.with_columns(row=pl.col('row') + 1).select(
            [
                "validation_type",
                "validation_id",
                "row",
                "unique_identifier",
                "scope",
            ]
            + sorted_columns
        )
        final_df = pl.concat([final_df, df_pivot], how="diagonal")
        final_df = final_df.with_columns(phase=pl.lit(phase))
    return final_df


def df_to_download(
    df: pl.DataFrame,
    warning_count: int = 0,
    error_count: int = 0,
    max_errors: int = 1000000,
):
    if df.is_empty():
        # return headers of csv for 'emtpy' report
        buffer = BytesIO()
        empty_df = pl.DataFrame(
            {
                "validation_type": [],
                "validation_id": [],
                "validation_name": [],
                "row": [],
                "unique_identifier": [],
                "fig_link": [],
                "validation_description": [],
            }
        )
        empty_df.write_csv(buffer, quote_style='non_numeric', include_header=True)
        buffer.seek(0)
        return buffer.getvalue()

    # get the check for the phase the results were in, so we can pull out static data from each
    # found check
    checks = get_checks(df.select(pl.first("phase")).item())

    # place the static data into a dataframe, and then join the results frame with it where the validation ids are the same.
    # This is much faster than applying the fields
    check_values = [
        {
            "validation_id": check.title,
            "validation_description": check.description,
            "validation_name": check.name,
            "fig_link": check.fig_link,
        }
        for check in checks
    ]
    checks_df = pl.DataFrame(check_values)
    joined_df = df.join(checks_df, on="validation_id")

    # Sort by validation id, order the field and value columns so they end up like field_1, value_1, field_2, value_2,...
    # and organize the columns as desired for the csv
    joined_df = joined_df.with_columns(pl.col('validation_id').cast(pl.Categorical(ordering='lexical'))).sort(
        'validation_id'
    )

    field_columns = [col for col in joined_df.columns if col.startswith('field_')]
    value_columns = [col for col in joined_df.columns if col.startswith('value_')]
    sorted_columns = [col for pair in zip(field_columns, value_columns) for col in pair]

    sorted_df = joined_df[
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

    buffer = BytesIO()
    headers = ','.join(sorted_df.columns) + '\n'
    buffer.write(headers.encode())

    total_errors = warning_count + error_count
    error_type = "errors"
    if warning_count > 0:
        if error_count > 0:
            error_type = "errors and warnings"
        else:
            error_type = "warnings"

    if total_errors and total_errors > max_errors:
        buffer.write(
            f'"Your register contains {total_errors} {error_type}, however, only {max_errors} records are displayed in this report. To see additional {error_type}, correct the listed records, and upload a new file."\n'.encode()
        )

    sorted_df.write_csv(buffer, quote_style='non_numeric', include_header=False)
    buffer.seek(0)
    return buffer.getvalue()


def df_to_csv(df: pl.DataFrame) -> str:
    sorted_df = df.with_columns(pl.col('validation_id').cast(pl.Categorical(ordering='lexical'))).sort('validation_id')
    return sorted_df.write_csv(quote_style='non_numeric')


def df_to_str(df: pl.DataFrame) -> str:
    with pl.Config(tbl_width_chars=0, tbl_rows=-1, tbl_cols=-1):
        return str(df)


def df_to_table(df: pl.DataFrame) -> str:
    df = df.select([df[col].str.slice(0, 50) for col in df.columns if df[col].dtype == pl.Utf8])

    return tabulate(df, headers='keys', showindex=True, tablefmt='rounded_outline')  # type: ignore


def df_to_json(df: pl.DataFrame, max_records: int = 10000, max_group_size: int = 200) -> str:
    results = df_to_dicts(df, max_records, max_group_size)
    return ujson.dumps(results, indent=4, escape_forward_slashes=False)


def df_to_dicts(df: pl.DataFrame, max_records: int = 10000, max_group_size: int = 200) -> list[dict]:
    json_results = []
    if not df.is_empty():
        # polars str columns sort by entry, not lexigraphical sorting like we'd expect, so cast the column to use
        # standard python str column sorting.  Polars throws a warning at this.
        sorted_df = df.with_columns(pl.col('validation_id').cast(pl.Categorical(ordering='lexical'))).sort(
            'validation_id'
        )

        checks = get_checks(df.select(pl.first("phase")).item())

        partial_process_group = partial(
            process_group_data, json_results=json_results, group_size=max_group_size, checks=checks
        )

        # collecting just the currently processed group from a lazyframe is faster and more efficient than using "apply"
        sorted_df.lazy().group_by('validation_id').map_groups(partial_process_group, schema=None).collect()
        json_results = sorted(json_results, key=lambda x: x['validation']['id'])
    return json_results


# Cuts off the number of records.  Can't just 'head' on the group due to the dataframe structure.
# So this function uses the group error counts to truncate on record numbers
def truncate_validation_group_records(group, group_size):
    need_to_truncate = group.select(pl.col('row').n_unique()).item() > group_size
    unique_record_nos = group.select('row').unique(maintain_order=True).limit(group_size)
    truncated_group = group.filter(pl.col('row').is_in(unique_record_nos['row']))
    return truncated_group, need_to_truncate


def process_group_data(group_df, json_results, group_size, checks):
    validation_id = group_df['validation_id'].item(0)
    check = find_check(validation_id, checks)
    trunc_group, need_to_truncate = truncate_validation_group_records(group_df, group_size)
    group_json = process_chunk(trunc_group, validation_id, check)
    if group_json:
        group_json["validation"]["is_truncated"] = need_to_truncate
        json_results.append(group_json)
    return group_df


def process_chunk(df: pl.DataFrame, validation_id: str, check: SBLCheck) -> Dict[str, Any]:
    # once we have a grouped dataframe, working with the data as a
    # python dict is much faster
    findings_json = ujson.loads(df.write_json())
    records = []
    if not findings_json:
        return

    for finding in findings_json:
        fields = []
        for key, value in finding.items():
            if 'field_' in key and value:
                num = key.split("_")[1]
                fields.append({"name": value, "value": finding[f"value_{num}"]})
        records.append({'record_no': finding['row'] - 1, 'uid': finding['unique_identifier'], 'fields': fields})

    first_finding = findings_json[0]

    validation_info = {
        'validation': {
            'id': validation_id,
            'name': check.name,
            'description': check.description,
            'severity': first_finding['validation_type'],
            'scope': check.scope,
            'fig_link': check.fig_link,
        },
        'records': records,
    }

    return validation_info
