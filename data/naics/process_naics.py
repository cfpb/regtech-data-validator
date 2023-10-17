import csv
import os
import sys

import pandas as pd


# column header text containing naics code
NAICS_CODE_COL = "2022 NAICS US   Code"
# column header text containing naics title/description
NAICS_TITLE_COL = "2022 NAICS US Title"


"""
filter NAICS data with only 3 digit codes

Raises:
    FileNotFoundError: when input excel file not existed
    FileExistsError: when output csv file existed
"""
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <raw-src> <csv-dest>")
        exit(1)
    
    raw_src = sys.argv[1]
    csv_dest = sys.argv[2]

    if not os.path.isfile(raw_src):
        print(f"source file not existed: {raw_src}")
        exit(2)

    if os.path.isfile(csv_dest):
        print("destination file already existed: {csv_dest}")
        exit(3)

    df = pd.read_excel(raw_src, dtype=str, na_filter=False)

    print(f'source file successfully read: {raw_src}')

    # add header
    result = [["code", "title"]]

    # read excel file
    # and create csv data list
    for index, row in df.iterrows():
        code = str(row[NAICS_CODE_COL])
        if len(code) == 3:
            a_row = [code, str(row[NAICS_TITLE_COL])]
            result.append(a_row)

    # output data to csv file
    with open(csv_dest, "w") as f:
        writer = csv.writer(f)
        writer.writerows(result)

    print(f'destination file successfully written: {csv_dest}')
