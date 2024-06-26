from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from regtech_data_validator.data_formatters import df_to_csv, df_to_str, df_to_json, df_to_table, df_to_download
from typing import Annotated, Optional

import pandas as pd
import typer
import typer.core

from regtech_data_validator.create_schemas import validate_phases

# Need to do this because the latest version of typer, if the rich package exists
# will create a Panel with borders in the error output.  This causes stderr during
# tests to have a bunch of extra characters that aren't properly rendered when NOT
# in a console.  So until typer comes up with a nice way to turn such fancy error
# output off, we set the rich import to None in typer.core so it uses basic
# error formatting.
typer.core.rich = None

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


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
    CSV = 'csv'
    JSON = 'json'
    PANDAS = 'pandas'
    TABLE = 'table'
    DOWNLOAD = 'download'


@app.command()
def describe() -> None:
    """
    Describe CFPB data submission formats and validations
    """

    print('Feature coming soon...')


@app.command(no_args_is_help=True)
def validate(
    path: Annotated[
        Path,
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
) -> tuple[bool, pd.DataFrame]:
    """
    Validate CFPB data submission
    """
    context_dict = {x.key: x.value for x in context} if context else {}
    input_df = None
    try:
        input_df = pd.read_csv(path, dtype=str, na_filter=False)
    except Exception as e:
        raise RuntimeError(e)
    validation_results = validate_phases(input_df, context_dict)

    status = 'SUCCESS'
    no_of_findings = 0
    total_errors = 0
    findings_df = pd.DataFrame()
    if not validation_results.is_valid:
        status = 'FAILURE'
        findings_df = validation_results.findings
        no_of_findings = len(findings_df.index.unique())
        warning_count = validation_results.warning_counts.total_count
        error_count = validation_results.error_counts.total_count

        match output:
            case OutputFormat.PANDAS:
                print(df_to_str(findings_df))
            case OutputFormat.CSV:
                print(df_to_csv(findings_df))
            case OutputFormat.JSON:
                print(df_to_json(findings_df))
            case OutputFormat.TABLE:
                print(df_to_table(findings_df))
            case OutputFormat.DOWNLOAD:
                print(df_to_download(findings_df, warning_count, error_count))
            case _:
                raise ValueError(f'output format "{output}" not supported')

    typer.echo(
        f"status: {status}, total errors: {total_errors}, findings: {no_of_findings}, validation phase: {validation_results.phase}",
        err=True,
    )

    # returned values are only used in unit tests
    return validation_results.is_valid, findings_df


if __name__ == '__main__':
    app()
