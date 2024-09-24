import boto3
import ujson
import polars as pl
import fsspec

from tabulate import tabulate

from functools import partial

from io import BytesIO


def find_check(group_name, checks):
    gen = (check for check in checks if check.title == group_name)
    return next(gen)


# Takes the error dataframe, which is a bit obscure, and translates it to a format of:
# validation_type, validation_id, validation_name, row, unique_identifier, fig_link, validation_description, scope, field_#, value_#
# which corresponds to severity, error/warning code, name of error/warning, row number in sblar, UID, fig link,
# error/warning description (markdown formatted), single/multi/register, and the fields and values associated with the error/warning.
# Each row in the final dataframe represents all data for that one finding.
def format_findings(df: pl.DataFrame, checks):
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
            columns="field_number",
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
            validation_description=pl.lit(check.description),
            validation_name=pl.lit(check.name),
            fig_link=pl.lit(check.fig_link),
            scope=pl.lit(check.scope),
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
                "validation_name",
                "row",
                "unique_identifier",
                "fig_link",
                "validation_description",
                "scope",
            ]
            + sorted_columns
        )
        final_df = pl.concat([final_df, df_pivot], how="diagonal")
    print(f"Final DF: {final_df}")
    return final_df


def df_to_download(df: pl.DataFrame, path: str = "download_report.csv"):
    if df.is_empty():
        # return headers of csv for 'emtpy' report
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
        with fsspec.open(path, mode='wb') as f:
            empty_df.write_csv(f, quote_style='non_numeric')
        return

    sorted_df = (
        df.with_columns(pl.col('validation_id').cast(pl.Categorical(ordering='lexical')))
        .sort('validation_id')
        .drop(["scope"])
    )

    if path.startswith("s3"):
        buffer = BytesIO()
        df.write_csv(buffer)
        buffer.seek(0)
        upload(path, buffer.getvalue())
    else:
        with fsspec.open(path, mode='wb') as f:
            sorted_df.write_csv(f, quote_style='non_numeric')


def upload(path: str, content: bytes) -> None:
    bucket = path.split("s3://")[1].split("/")[0]
    opath = path.split("s3://")[1].replace(bucket+"/", "")
    s3 = boto3.client("s3")
    r = s3.put_object(
        Bucket=settings.fs_upload_config.root,
        Key=opath,
        Body=content,
    )


def df_to_csv(df: pl.DataFrame) -> str:
    sorted_df = df.with_columns(pl.col('validation_id').cast(pl.Categorical(ordering='lexical'))).sort('validation_id')
    return sorted_df.write_csv(quote_style='non_numeric')


def df_to_str(df: pl.DataFrame) -> str:
    with pl.Config(tbl_width_chars=0, tbl_rows=-1, tbl_cols=-1):
        return str(df)


def df_to_table(df: pl.DataFrame) -> str:
    df = df.select([df[col].str.slice(0, 50) for col in df.columns if df[col].dtype == pl.Utf8])

    return tabulate(df, headers='keys', showindex=True, tablefmt='rounded_outline')  # type: ignore


def df_to_json(df: pl.DataFrame, max_records: int = 10000, max_group_size: int = None) -> str:
    results = df_to_dicts(df, max_records, max_group_size)
    return ujson.dumps(results, indent=4, escape_forward_slashes=False)


def df_to_dicts(df: pl.DataFrame, max_records: int = 10000, max_group_size: int = None) -> list[dict]:
    json_results = []
    if not df.is_empty():
        # polars str columns sort by entry, not lexigraphical sorting like we'd expect, so cast the column to use
        # standard python str column sorting.  Polars throws a warning at this.
        sorted_df = df.with_columns(pl.col('validation_id').cast(pl.Categorical(ordering='lexical'))).sort(
            'validation_id'
        )
        partial_process_group = partial(process_group_data, json_results=json_results)
        # collecting just the currently processed group from a lazyframe is faster and more efficient than using "apply"
        sorted_df.lazy().group_by('validation_id').map_groups(partial_process_group, schema=None).collect()
        json_results = sorted(json_results, key=lambda x: x['validation']['id'])
    return json_results


def process_group_data(group_df, json_results):
    validation_id = group_df['validation_id'].item(0)
    group_json = process_chunk(group_df, validation_id)
    if group_json:
        json_results.append(group_json)
    return group_df


def process_chunk(df: pl.DataFrame, validation_id: str) -> [dict]:
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
            'name': first_finding['validation_name'],
            'description': first_finding['validation_description'],
            'severity': first_finding['validation_type'],
            'scope': first_finding['scope'],
            'fig_link': first_finding['fig_link'],
        },
        'records': records,
    }

    return validation_info
