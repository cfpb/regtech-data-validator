
import os
import sys

import pandas as pd

ROOT_DIR = \
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # noqa: E402
sys.path.append(ROOT_DIR) # noqa: E402

from config import NAICS_CSV_PATH  # noqa: E402

naics_codes = {}

def read_naics_codes():
    """
    read NAICS CSV file with this format: (code, description)
    and populate global value: naics_codes
    """
    naics_codes.clear()
    df = pd.read_csv(NAICS_CSV_PATH, dtype=str, na_filter=False)
    for _, row in df.iterrows():
        naics_codes.update({row[0]: row[1]})