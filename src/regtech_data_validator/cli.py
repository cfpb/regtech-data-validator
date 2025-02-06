from dataclasses import dataclass
from enum import StrEnum
from regtech_data_validator.data_formatters import df_to_csv, df_to_str, df_to_json, df_to_table, df_to_download
from typing import Annotated, Optional

import polars as pl
import typer
import typer.core

from regtech_data_validator.validator import validate_batch_csv, validate_lazy_frame
from regtech_data_validator.validation_results import ValidationPhase

# Need to do this because the latest version of typer, if the rich package exists
# will create a Panel with borders in the error output.  This causes stderr during
# tests to have a bunch of extra characters that aren't properly rendered when NOT
# in a console.  So until typer comes up with a nice way to turn such fancy error
# output off, we set the rich import to None in typer.core so it uses basic
# error formatting.
typer.core.rich = None

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


class FileType(StrEnum):
    CSV = 'csv'
    PARQUET = 'parquet'


@dataclass
class KeyValueOpt:
    key: str
    value: str


def parse_key_value(kv_str: str) -> KeyValueOpt:
    split_str = kv_str.split('=')

    if len(split_str) != 2:
        raise ValueError(f'Invalid key/value pair: {kv_str}')

    return KeyValueOpt(split_str[0], split_str[1])


class OutputFormat(StrEnum):
    JSON = 'json'
    POLARS = 'polars'
    TABLE = 'table'
    DOWNLOAD = 'download'
    CSV = 'csv'


@app.command()
def describe() -> None:
    """
    Describe CFPB data submission formats and validations
    """

    print('Feature coming soon...')


@app.command(no_args_is_help=True)
def validate(
    path: Annotated[
        str,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            show_default=False,
            help='Path of file to be validated',
        ),
    ],
    context: Annotated[
        Optional[list[KeyValueOpt]],
        typer.Option(
            parser=parse_key_value,
            metavar='<key>=<value>',
            help='[example: lei=12345678901234567890]',
            show_default=False,
        ),
    ] = None,
    output: Annotated[Optional[OutputFormat], typer.Option()] = OutputFormat.TABLE,
    filetype: Annotated[Optional[FileType], typer.Option()] = FileType.CSV,
) -> tuple[bool, pl.DataFrame]:
    """
    Validate CFPB data submission
    """
    context_dict = {x.key: x.value for x in context} if context else {}

    total_findings = 0
    final_phase = ValidationPhase.LOGICAL
    all_findings = []
    final_df = pl.DataFrame()
    if filetype == FileType.CSV:
        for validation_results in validate_batch_csv(path, context_dict, batch_size=50000, batch_count=1):
            total_findings += (
                validation_results.error_counts.total_count + validation_results.warning_counts.total_count
            )
            final_phase = validation_results.phase
            all_findings.append(validation_results)
    elif filetype == FileType.PARQUET:
        lf = pl.scan_parquet(path, allow_missing_columns=True)
        for validation_results in validate_lazy_frame(lf, context_dict, batch_size=50000, batch_count=1):
            total_findings += (
                validation_results.error_counts.total_count + validation_results.warning_counts.total_count
            )
            final_phase = validation_results.phase
            all_findings.append(validation_results)

    if all_findings:
        final_df = pl.concat([v.findings for v in all_findings], how="diagonal")

    status = "SUCCESS" if total_findings == 0 else "FAILURE"

    match output:
        case OutputFormat.CSV:
            print(df_to_csv(final_df))
        case OutputFormat.POLARS:
            print(df_to_str(final_df))
        case OutputFormat.JSON:
            print(df_to_json(final_df, max_group_size=200))
        case OutputFormat.TABLE:
            print(df_to_table(final_df))
        case OutputFormat.DOWNLOAD:
            print(df_to_download(final_df))
        case _:
            raise ValueError(f'output format "{output}" not supported')

    typer.echo(
        f"Status: {status}, Total Errors: {total_findings}, Validation Phase: {final_phase}",
        err=True,
    )

    return (status, final_df)


if __name__ == '__main__':
    app()
