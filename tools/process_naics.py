import csv
import os
import sys

import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # noqa: E402
sys.path.append(ROOT_DIR)  # noqa: E402

import config  # noqa: E402

"""
filter NAICS data with only 3 digit codes

Raises:
    FileNotFoundError: when input excel file not existed
    FileExistsError: when output csv file existed
"""
if __name__ == "__main__":
    EXCEL_PATH = config.NAICS_EXCEL_PATH
    CSV_PATH = config.NAICS_CSV_PATH
    CODE_COL = config.NAICS_CODE_COL
    TITLE_COL = config.NAICS_TITLE_COL

    # check for paths
    if not os.path.isfile(EXCEL_PATH):
        error_msg = "Input excel file not existed"
        raise FileNotFoundError(error_msg)
    if os.path.isfile(CSV_PATH):
        error_msg = "Output csv file existed"
        raise FileExistsError(error_msg)

    df = pd.read_excel(EXCEL_PATH, dtype=str, na_filter=False)

    # add header
    result = [["code", "title"]]

    # read excel file
    # and create csv data list
    for index, row in df.iterrows():
        code = str(row[CODE_COL])
        if len(code) == 3:
            a_row = [code, str(row[TITLE_COL])]
            result.append(a_row)

    # output data to csv file
    with open(CSV_PATH, "w") as f:
        writer = csv.writer(f)
        writer.writerows(result)
