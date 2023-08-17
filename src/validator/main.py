"""
This script loads a given CSV into a Pandas DataFrame, and then validates it against
the SBL Pandera schema.

Run from the terminal to see the generated output.
"""

import os
import sys

import pandas as pd
from pandera.errors import SchemaErrors
from schema import get_schema_for_lei

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # noqa: E402
sys.path.append(PARENT_DIR)  # noqa: E402
from util import global_data  # noqa: E402


def csv_to_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, na_filter=False)


def run_validation_on_df(df: pd.DataFrame, naics: dict, geoids: dict, lei: str) -> None:
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
        schema = get_schema_for_lei(naics, geoids, lei)
        schema(df, lazy=True)
    except SchemaErrors as errors:
        for error in errors.schema_errors:
            # Name of the column in the dataframe being checked
            column_name = error["error"].schema.name
            check = error["error"].check
            check_output = error["error"].check_output
            # built in checks such as unique=True are different than custom
            # checks unfortunately so the name needs to be accessed differently
            if hasattr(check, "name"):
                check_name = check.name
                print(f"Validation `{check_name}` failed for column `{column_name}`")
                print(check_output)
                print("")
            else:
                raise AttributeError(f"{check}")


if __name__ == "__main__":
    # read and populate global naics code (this should be called only once)
    naics = global_data.read_naics_codes()

    # read and populate global census geoids (this should be called only once)
    geoids = global_data.read_geoids()

    csv_path = None
    lei: str = None
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
    run_validation_on_df(df, naics, geoids, lei)
