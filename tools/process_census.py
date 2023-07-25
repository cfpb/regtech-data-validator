import csv
import os
import sys
import zipfile

import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # noqa: E402
sys.path.append(ROOT_DIR)  # noqa: E402

import config  # noqa: E402


# helper function to check number (float/int/negative)
def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# helper function to unzip census file and extract CSV file
def _extract_census_zip_file():
    CENSUS_TMP_CSV_PATH = config.CENSUS_RAW_ZIP_PATH + ".tmp.csv"
    # unzip and extract csv files
    with zipfile.ZipFile(config.CENSUS_RAW_ZIP_PATH, "r") as zip_ref:
        for file in zip_ref.namelist():  # iterate over files in archive
            if file[-4:] == ".csv":
                print("Extracting CSV to {}".format(CENSUS_TMP_CSV_PATH))
                with open(CENSUS_TMP_CSV_PATH, "wb") as outfile:
                    outfile.write(zip_ref.read(file))
                # it should only have one csv file
                return CENSUS_TMP_CSV_PATH


# helper function to read extracted csv file and filter only geo-tract-id
def _read_census_csv(src_path: str, csv_path: str):
    STATE_COL = config.CENSUS_STATE_COL_INDEX
    COUNTY_COL = config.CENSUS_COUNTY_COL_INDEX
    TRACT_COL = config.CENSUS_TRACT_COL_INDEX

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
    result = [[config.CENSUS_GEOID_COL]]

    # read excel file
    # and create csv data list
    for index, row in df.iterrows():
        state_value = str(row[STATE_COL])
        county_value = str(row[COUNTY_COL])
        tract_value = str(row[TRACT_COL])
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
    CSV_PATH = config.CENSUS_PROCESSED_CSV_PATH

    if os.path.isfile(CSV_PATH):
        error_msg = "Output {} csv file existed".format(CSV_PATH)
        raise FileExistsError(error_msg)

    tmp_census_csv_file = _extract_census_zip_file()
    print("Reading extracted CSV File . {}".format(tmp_census_csv_file))
    _read_census_csv(tmp_census_csv_file, CSV_PATH)
    print("Removing extracted CSV File")
    os.remove(tmp_census_csv_file)
