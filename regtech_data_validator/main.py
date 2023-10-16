"""
This script loads a given CSV into a Pandas DataFrame, and then validates it against
the SBL Pandera schema.

Run from the terminal to see the generated output.
"""

import json
import sys

import pandas as pd

from regtech_data_validator.create_schemas import validate_phases


def csv_to_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, na_filter=False)


def run_validation_on_df(df: pd.DataFrame, lei: str|None) -> None:
    """
    Run validation on the supplied dataframe and print a report to
    the terminal.
    """

    validation_dict = validate_phases(df, lei)
    validation_json = json.dumps(validation_dict, indent=4)

    print(validation_json)


def main():
    csv_path = None
    lei: str|None = None
    if len(sys.argv) == 1:
        raise ValueError("csv_path arg not provided")
    elif len(sys.argv) == 2:
        csv_path = sys.argv[1]
    elif len(sys.argv) == 3:
        lei = sys.argv[1]
        csv_path = sys.argv[2]
    else:
        raise ValueError("correct number of args not provided")

    df = csv_to_df(csv_path)
    run_validation_on_df(df, lei)

if __name__ == "__main__":
    main()