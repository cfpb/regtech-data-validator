"""This script runs a Pandera schema object over two Pandas Dataframes. 
One contains valid SBLAR data and the other contains invalid records. 
Run from the terminal to see the generated output."""

import pandas as pd
import pandera as pa
from schema import sblar_schema

# here is a dataframe containing valid data
valid_sblar_df = pd.read_excel(
    "example_sblar.xlsx",
    engine="openpyxl",
    sheet_name="valid",
    dtype=str,
    na_filter=False,
)


# here is a dataframe containing bad data
invalid_sblar_df = pd.read_excel(
    "example_sblar.xlsx",
    engine="openpyxl",
    sheet_name="invalid",
    dtype=str,
    na_filter=False,
)


def run_validation_on_df(df: pd.DataFrame) -> None:
    """Run validaition on the supplied dataframe and print a report to
    the terminal."""

    print("--------------------------------------------------------------------------")
    print("Performing validation on the following DataFrame.")
    print("")
    print(df)
    print("")

    try:
        sblar_schema(df, lazy=True)
    except pa.errors.SchemaErrors as errors:
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

            print(f"Validation `{check_name}` failed for column `{column_name}`")
            print(check_output)
            print("")


if __name__ == "__main__":
    # run_validation_on_df(valid_sblar_df)
    run_validation_on_df(invalid_sblar_df)
