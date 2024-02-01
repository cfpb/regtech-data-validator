from dataclasses import dataclass
from enum import StrEnum
import json, datatime
from pathlib import Path
from typing import Annotated, Optional

import pandas as pd
from tabulate import tabulate
import typer

from regtech_data_validator.create_schemas import validate_phases


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
            'validation': {'id': v_id_idx,'name': v_head.at['validation_name'],'description': v_head.at['validation_desc'],'severity': v_head.at['validation_severity'],
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
    input_df = pd.read_csv(path, dtype=str, na_filter=False)
    is_valid, findings_df = validate_phases(input_df, context_dict)

    status = 'SUCCESS'
    no_of_findings = 0

    if not is_valid:
        status = 'FAILURE'
        no_of_findings = len(findings_df.index.unique())

        match output:
            case OutputFormat.PANDAS:
                print(df_to_str(findings_df))
            case OutputFormat.CSV:
                print(df_to_csv(findings_df))
            case OutputFormat.JSON:
                print(df_to_json(findings_df))
            case OutputFormat.TABLE:
                print(df_to_table(findings_df))
            case _:
                raise ValueError(f'output format "{output}" not supported')

    typer.echo(f"status: {status}, findings: {no_of_findings}", err=True)

    # returned values are only used in unit tests
    return is_valid, findings_df


if __name__ == '__main__':
    app()
