import os
import sys

import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # noqa: E402
sys.path.append(ROOT_DIR)  # noqa: E402

from config import CENSUS_PROCESSED_CSV_PATH, NAICS_CSV_PATH  # noqa: E402

naics_codes = {}

# global variable for geoids
census_geoids = {}


def read_naics_codes(csv_path: str = NAICS_CSV_PATH):
    """
    read NAICS CSV file with this format: (code, description)
    and populate global value: naics_codes
    """
    naics_codes.clear()
    df = pd.read_csv(csv_path, dtype=str, na_filter=False)
    for _, row in df.iterrows():
        naics_codes.update({row.iloc[0]: row.iloc[1]})


def read_geoids(csv_path: str = CENSUS_PROCESSED_CSV_PATH):
    """
    read geoids CSV file with this format: (code)
    and populate global value: census_geoids
    """
    census_geoids.clear()
    df = pd.read_csv(csv_path, dtype=str, na_filter=False)
    for _, row in df.iterrows():
        census_geoids.update({row.iloc[0]: None})
