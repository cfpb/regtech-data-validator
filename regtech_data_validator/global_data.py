import csv
from importlib.resources import files


# global variable for NAICS codes
naics_codes: dict[str, str] = {}
naics_file_path = files('regtech_data_validator.data.naics').joinpath('2022_codes.csv')

with naics_file_path.open('r') as f:
    for row in csv.DictReader(f):
        naics_codes[row['code']] = row['title']


# global variable for Census GEOIDs
census_geoids: set[str] = set()
census_file_path = files('regtech_data_validator.data.census').joinpath('Census2023.processed.csv')

with census_file_path.open('r') as f:
    for row in csv.DictReader(f):
        census_geoids.add(row['geoid'])
