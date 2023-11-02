from dataclasses import dataclass
from enum import StrEnum
import json
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
):
    """
    CFPB's RegTech data validation utility.
    """
    context_dict = {x.key: x.value for x in context} if context else {}

    # FIXME: Handle ParserError
    input_df = pd.read_csv(path, dtype=str, na_filter=False)
    is_valid, findings_df = validate_phases(input_df, context_dict)

    if not is_valid:
        match output:
            case OutputFormat.PANDAS:
                with pd.option_context('display.width', None, 'display.max_rows', None):
                    print(findings_df)
            case OutputFormat.CSV:
                print(findings_df.to_csv())
            case OutputFormat.JSON:
                findings_json = []
                findings_by_v_id_df = findings_df.reset_index().set_index(['validation_id', 'record_no', 'field_name'])

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

                print()
                print(json.dumps(findings_json, indent=4))

            case OutputFormat.TABLE:
                # trim field_value field to just 50 chars, similar to DataFrame default
                table_df = findings_df.drop(columns='validation_desc').sort_index()
                table_df['field_value'] = table_df['field_value'].str[0:50]

                # NOTE: `type: ignore` because tabulate package typing does not include Pandas
                #        DataFrame as input, but the library itself does support it. ¯\_(ツ)_/¯
                print(tabulate(table_df, headers='keys', showindex=True, tablefmt='rounded_outline'))  # type: ignore
            case _:
                raise ValueError(f'output format "{output}" not supported')


if __name__ == '__main__':
    app()
