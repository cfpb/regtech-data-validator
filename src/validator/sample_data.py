import os
import sys

import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa: E402
sys.path.append(ROOT_DIR)  # noqa: E402

GOOD_FILE_PATH = "./SBL_Validations_SampleData_GoodFile_03312023.csv"
BAD_FILE_PATH = "./SBL_Validations_SampleData_BadFile_03312023.csv"


def read_good_data(csv_path: str = GOOD_FILE_PATH):
    """reads SampleData GoodFile csv file and returns a dataframe.

    Args:
        csv_path (str, optional): _description_. Defaults to GOOD_FILE_PATH.

    Returns:
       dataframe : return csv rows as dataframe
    """

    good_data_df = pd.read_csv(csv_path, dtype=str, na_filter=False)
    return good_data_df


def read_bad_data(csv_path: str = BAD_FILE_PATH):
    """reads SampleData BadFile csv file and returns a dataframe.

    Args:
        csv_path (str, optional): _description_. Defaults to BAD_FILE_PATH.

    Returns:
       dataframe : return csv rows as dataframe
    """

    bad_data_df = pd.read_csv(csv_path, dtype=str, na_filter=False)
    return bad_data_df
