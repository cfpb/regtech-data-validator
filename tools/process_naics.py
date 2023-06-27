import csv
import os
import sys

import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # noqa
sys.path.append(ROOT_DIR) # noqa

import config

"""
filter NAICS data with only 3 digit codes

Raises:
    FileNotFoundError: when input excel file not existed
    FileExistsError: when output csv file existed
"""
if __name__ == "__main__":
    excel_path = config.naics_excel_path
    csv_path = config.naics_csv_path
    
    #check for paths
    if not os.path.isfile(excel_path):
        error_msg = "Input excel file not existed"
        raise FileNotFoundError(error_msg)
    if os.path.isfile(csv_path):
        error_msg = "Output csv file existed"
        raise FileExistsError(error_msg)
    
    df = pd.read_excel(excel_path, dtype=str, na_filter=False)
    result = []
    
    #read excel file
    # and create csv data list
    for index, row in df.iterrows():
        code = str(row[1])
        if len(code) == 3:
            a_row = [code , str(row[2])]
            result.append(a_row)
    
    #output data to csv file
    with open(csv_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(result)
    