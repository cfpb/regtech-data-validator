import os

import pandas as pd

from config import CENSUS_PROCESSED_CSV_PATH, NAICS_CSV_PATH

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

def read_naics_codes() -> dict:
    """
    read NAICS CSV file with this format: (code, description)
    and populate global value: naics_codes
    """
    naics_codes = {}
    file = os.path.join(ROOT_DIR, NAICS_CSV_PATH)
    df = pd.read_csv(file, dtype=str, na_filter=False)
    for _, row in df.iterrows():
        naics_codes.update({row[0]: row[1]})
    return naics_codes


def read_geoids() -> dict:
    """
    read geoids CSV file with this format: (code)
    and populate global value: census_geoids
    """
    census_geoids = {}
    file = os.path.join(ROOT_DIR, CENSUS_PROCESSED_CSV_PATH)
    df = pd.read_csv(file, dtype=str, na_filter=False)
    for _, row in df.iterrows():
        census_geoids.update({row[0]: None})
    return census_geoids
