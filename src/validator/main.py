"""This script runs a Pandera schema object over two Pandas Dataframes. 
One contains valid SBLAR data and the other contains invalid records. 
Run from the terminal to see the generated output."""

import pandas as pd
import pandera as pa
from schema import sblar_schema

if __name__ == "__main__":
    print("I didn't actually do anything but I did run :)")
