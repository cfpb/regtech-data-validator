"""This script runs a Pandera schema object over two Pandas Dataframes. 
One contains valid SBLAR data and the other contains invalid records. 
Run from the terminal to see the generated output."""

import pandas as pd

from schema import sblar_schema

# here is a dataframe containing valid data
valid_sblar_df = pd.read_excel(
    "example_sblar.xlsx",
    engine="openpyxl",
    sheet_name="valid",
    dtype=str,
    na_filter=False,
)
print("Valid SBLAR Data:")
print("__________________________________________" * 3)
print(valid_sblar_df)
print("")


# uncomment to see validaiton output on valid data
# print("Running validation on valid data.....................")
# sblar_schema(valid_sblar_df)

# here is a dataframe containing bad data
invalid_sblar_df = pd.read_excel(
    "example_sblar.xlsx",
    engine="openpyxl",
    sheet_name="invalid",
    dtype=str,
    na_filter=False,
)
print("Invalid SBLAR Data:")
print("__________________________________________" * 3)
print(invalid_sblar_df)
print("Running validation on invalid data.................")
sblar_schema(invalid_sblar_df, lazy=True)
