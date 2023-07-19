import csv
import os
import sys
import zipfile

import pandas as pd
import requests

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


"""
def _download_census_file():
    BASE_URL = config.FFIEC_CENSUS_BASE_URL
    CSV_PATH = config.CENSUS_CSV_PATH
    SRC_ZIP_FILENAME = "{}{}.zip".format(config.FFIEC_FILENAME, config.CENSUS_YEAR)
    INPUT_ZIP = "{}/{}".format(BASE_URL, SRC_ZIP_FILENAME)
    OUTPUT_ZIP = "{}/{}".format(config.CENSUS_SOURCE_PATH, SRC_ZIP_FILENAME)

    # read zip file from FFIEC Url
    print("getting data from {}".format(INPUT_ZIP))
    census_resp = requests.get(
        "https://www.ffiec.gov/Census/Census_Flat_Files/Census2020.zip",
        headers={"User-Agent": "Mozilla/5.0"},
        allow_redirects=True,
    )
    print("saving {} data to {}".format(config.CENSUS_YEAR, OUTPUT_ZIP))
    print("saving {}".format(census_resp.content))
    # save zip to local file
    with open(OUTPUT_ZIP, "wb") as infile:
        infile.write(census_resp.content)

    # unzip and extract csv files
    with zipfile.ZipFile(OUTPUT_ZIP, "r") as zip_ref:
        for file in zip_ref.namelist():  # iterate over files in archive
            if file[-4:] == ".csv":
                new_name = "{}.{}".format(config.CENSUS_YEAR, config.CENSUS_FILENAME)
                output_csv = "{}/{}".format(config.CENSUS_SOURCE_PATH, new_name)
                print("Extracting CSV file to {}".format(output_csv))
                with open(output_csv, "wb") as outfile:
                    outfile.write(zip_ref.read(file))
                # it should only have one csv file
                return output_csv
"""


def _extract_census_zip_file():
    # unzip and extract csv files
    with zipfile.ZipFile(config.CENSUS_RAW_ZIP_PATH, "r") as zip_ref:
        for file in zip_ref.namelist():  # iterate over files in archive
            if file[-4:] == ".csv":
                print("Extracting CSV to {}".format(config.CENSUS_TMP_CSV_PATH))
                with open(config.CENSUS_TMP_CSV_PATH, "wb") as outfile:
                    outfile.write(zip_ref.read(file))
                # it should only have one csv file
                return config.CENSUS_TMP_CSV_PATH


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
    print("Reading extracted CSV File")
    _read_census_csv(tmp_census_csv_file, CSV_PATH)
    print("Removing extracted CSV File")
    os.remove(tmp_census_csv_file)
