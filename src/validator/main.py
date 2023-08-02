"""
This script loads a given CSV into a Pandas DataFrame, and then validates it against
the SBL Pandera schema.

Run from the terminal to see the generated output.
"""

import sys

import pandas as pd
from global_data import FIELD_UNIQUENESS, FIELD_UNIQUENESS_KEYWORD
from pandera.errors import SchemaErrors
from schema import sblar_schema


def csv_to_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, na_filter=False)


def run_validation_on_df(df: pd.DataFrame) -> None:
    """
    Run validaition on the supplied dataframe and print a report to
    the terminal.
    """

    print("--------------------------------------------------------------------------")
    print("Performing validation on the following DataFrame.")
    print("")
    print(df)
    print("")

    try:
        sblar_schema(df, lazy=True)
    except SchemaErrors as errors:
        for error in errors.schema_errors:
            # Name of the column in the dataframe being checked
            column_name = error["error"].schema.name

            # built in checks such as unique=True are different than custom
            # checks unfortunately so the name needs to be accessed differently
            try:
                check_name = error["error"].check.name
                # This will either be a boolean series or a single bool
                check_output = error["error"].check_output
            except AttributeError:
                check_name = error["error"].check
                # this is just a string that we'd need to parse manually
                check_output = error["error"].args[0]

            if (
                check_name == FIELD_UNIQUENESS_KEYWORD
                and FIELD_UNIQUENESS.get(column_name) is not None
            ):
                check_name = FIELD_UNIQUENESS.get(column_name)

            print(f"Validation `{check_name}` failed for column `{column_name}`")
            print(check_output)
            print("")


if __name__ == "__main__":
    csv_path = None
    try:
        csv_path = sys.argv[1]
    except IndexError:
        raise ValueError("csv_path arg not provided")

    df = csv_to_df(csv_path)
    run_validation_on_df(df)
