import csv
import os
import sys
import zipfile

import pandas as pd

# census file col indexes
CENSUS_STATE_COL_INDEX = 2
CENSUS_COUNTY_COL_INDEX = 3
CENSUS_TRACT_COL_INDEX = 4

CENSUS_GEOID_COL = "geoid"


# helper function to check number (float/int/negative)
def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# helper function to unzip census file and extract CSV file
def _extract_census_zip_file(raw_src):
    census_tmp_csv_path = raw_src + ".tmp.csv"
    # unzip and extract csv files
    with zipfile.ZipFile(raw_src, "r") as zip_ref:
        for file in zip_ref.namelist():  # iterate over files in archive
            if file[-4:] == ".csv":
                print("Extracting CSV to {}".format(census_tmp_csv_path))
                with open(census_tmp_csv_path, "wb") as outfile:
                    outfile.write(zip_ref.read(file))
                    # it should only have one csv file

    return census_tmp_csv_path


# helper function to read extracted csv file and filter only geo-tract-id
def _process_census_csv(src_path: str, csv_path: str):

    # check paths
    if not os.path.isfile(src_path):
        error_msg = "Input {} file not existed".format(src_path)
        raise FileNotFoundError(error_msg)

    # source census file does not have header
    print("Parsing Source CSV {}".format(src_path))
    df = pd.read_csv(
        src_path, dtype=str, na_filter=False, header=None, usecols=[2, 3, 4]
    )

    # add header
    result = [[CENSUS_GEOID_COL]]

    # read excel file
    # and create csv data list
    for index, row in df.iterrows():
        state_value = str(row[CENSUS_STATE_COL_INDEX])
        county_value = str(row[CENSUS_COUNTY_COL_INDEX])
        tract_value = str(row[CENSUS_TRACT_COL_INDEX])
        if (
            _is_number(state_value)
            and _is_number(county_value)
            and _is_number(tract_value)
        ):
            geoid_value = [state_value + county_value + tract_value]
            if geoid_value not in result:
                result.append(geoid_value)

    # output data to csv file
    print("Writing to CSV {}".format(csv_path))
    with open(csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerows(result)


"""
filter Census data. 
- Read input file.
- parse 3 columns (state, county and tract).
- format it to 11 digit value
- output to defined output file
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

    tmp_census_csv_file = _extract_census_zip_file(raw_src)
    print(f"Reading extracted CSV file: {tmp_census_csv_file}")
    _process_census_csv(tmp_census_csv_file, csv_dest)
    print("Removing extracted CSV file")
    os.remove(tmp_census_csv_file)
