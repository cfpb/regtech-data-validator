# RegTech Data Validator

This is a RegTech submission data parser and validator which makes use of Pandera. You can read about Pandera schemas [here](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html).  This library allows users to validate SBL Data and get any failed validations details.

## Pre-requisites

- Poetry is used as the package management tool.
- (Optional) Visual Studio Code for development.
- (Optional) Docker is needed when using Visual Studio Code / Dev Container.

## Dependencies

All packages and libraries used in this repository can be found in `pyproject.toml`

## Development

There are few files in `src/validator` that will be of interest.

- `checks.py` defines custom Pandera Check class called `SBLCheck`.
- `global_data.py` defines functions to parse NAICS and GEOIDs.
- `phase_validations.py` defines phase 1 and phase 2 Pandera schema/checks used for validating the SBLAR data.
- `check_functions.py` contains a collection of functions to be run against the data that are a bit too complex to be implemented directly within the schema as Lambda functions.
- Lastly, the file `main.py` pulls everything together and illustrates how the schema can catch the various validation errors present in our mock, invalid dataset and different LEI values.

## Development Tests

- The repo includes unit tests that can be executed using `pytest` or in Visual Studio Code.  These tests can be located under `src/tests`.
- The repo also includes 2 test datasets for manual testing, one with all valid data, and one where each line represents a different failed validation, or different permutation of of the same failed validation.
  - [`sbl-validations-pass.csv`](src/tests/data/sbl-validations-pass.csv)
  - [`sbl-validations-fail.csv`](src/tests/data/sbl-validations-fail.csv)

## Development Process and Standard

Development Process
Below are the steps the development team follows to fix issues, develop new features, etc.

1. Work in a branch
2. Create a PR to merge into main
3. The PR is automatically built, tested, and linted using github actions with PyTest, Black, Ruff, and Coverage.
4. Manual review is performed in addition to ensuring the above automatic scans are positive
5. The PR is deployed to development servers to be checked
6. The PR is merged only by a separate member in the dev team

Development standard practice

- Check functions should focus on reuse.
  - Most of the validations share logic with other validations.
- Avoid using lambdas for Check functions.
  - They do not promote reuse.
  - They are harder to debug.
  - They are harder to test.
- Check function signatures should reflect the functionality.
- Check functions should have corresponding unit tests.
  - [Unit Test](./src/tests/test_check_functions.py)
- Check definitions' name should be set to validation ID.
  - Example: "denial_reasons. enum_value_conflict"
    ![Validation ID](validation_id.png)
- Check new added lines are formatted correctly.

## Installing Dependencies

Run `poetry install` to install dependencies defined in `pyproject.toml`

```sh
# change to root directory.  In this example, this repo's root is 
#   ~/Projects/regtech-data-validator
$ cd ~/Projects/regtech-data-validator

# example of running poetry install
$ poetry install
Installing dependencies from lock file

Package operations: 25 installs, 0 updates, 0 removals

  • Installing six (1.16.0)
  • Installing iniconfig (2.0.0)
  • Installing mypy-extensions (1.0.0)
  • Installing numpy (1.25.2)
  • Installing packaging (23.1)
  • Installing pluggy (1.3.0)
  • Installing python-dateutil (2.8.2)
  • Installing pytz (2023.3.post1)
  • Installing typing-extensions (4.7.1)
  • Installing tzdata (2023.3)
  • Installing click (8.1.7): Pending...
  • Installing coverage (7.3.1): Pending...
  • Installing coverage (7.3.1): Pending...
  • Installing click (8.1.7): Downloading... 0%
  • Installing coverage (7.3.1): Pending...
  • Installing coverage (7.3.1): Downloading... 0%
  • Installing coverage (7.3.1): Downloading... 0%
  • Installing click (8.1.7): Downloading... 20%
  • Installing coverage (7.3.1): Downloading... 0%
  • Installing coverage (7.3.1): Downloading... 10%
  • Installing coverage (7.3.1): Downloading... 10%
  • Installing click (8.1.7): Downloading... 62%
  • Installing coverage (7.3.1): Downloading... 10%
  • Installing coverage (7.3.1): Downloading... 30%
  • Installing coverage (7.3.1): Downloading... 30%
  • Installing click (8.1.7): Downloading... 100%
  • Installing coverage (7.3.1): Downloading... 30%
  • Installing coverage (7.3.1): Downloading... 30%
  • Installing click (8.1.7): Installing...
  • Installing coverage (7.3.1): Downloading... 30%
  • Installing coverage (7.3.1): Downloading... 30%
  • Installing click (8.1.7)
  • Installing coverage (7.3.1): Downloading... 30%
  • Installing coverage (7.3.1): Downloading... 61%
  • Installing coverage (7.3.1): Downloading... 91%
  • Installing coverage (7.3.1): Downloading... 100%
  • Installing coverage (7.3.1): Installing...
  • Installing coverage (7.3.1)
  • Installing multimethod (1.9.1)
  • Installing pandas (2.1.0)
  • Installing pathspec (0.11.2)
  • Installing platformdirs (3.10.0)
  • Installing pydantic (1.10.12)
  • Installing pytest (7.4.0)
  • Installing typeguard (4.1.3)
  • Installing typing-inspect (0.9.0)
  • Installing wrapt (1.15.0)
  • Installing black (23.3.0)
  • Installing pandera (0.16.1)
  • Installing pytest-cov (4.1.0)
  • Installing ruff (0.0.259)

```

## Running Validator

`main.py` allows user to test csv file with and without LEI number

```sh
# Running validator using LEI and CSV file
main.py <LEI Number> <Path to CSV file>

# Running validator using just CSV file
main.py <Path to CSV file>
```

When all validations passed, it prints out :

```sh
[{'response': 'No validations errors or warnings'}]
```

When validation(s) failed, it prints out JSON data containing failed validation(s)

```sh
# Example of JSON response containing failed validation
[{'validation': {'id': 'E3000', 'name': 'uid.duplicates_in_dataset', 'description': "Any 'unique identifier' may not be used in more than one record within a small business lending application register.", 'fields': ['uid'], 'severity': 'error'}, 'records': [{'number': 5, 'field_values': {'uid': '000TESTFIUIDDONOTUSEXBXVID13XTC1'}}, {'number': 6, 'field_values': {'uid': '000TESTFIUIDDONOTUSEXBXVID13XTC1'}}]}]

```

To run `main.py` in terminal, you can use these commands.

```sh
# Test validating the "good" file
# If passing lei value, pass lei as first arg and csv_path as second arg
$ poetry run python src/validator/main.py 000TESTFIUIDDONOTUSE src/tests/data/sbl-validations-pass.csv
# else just pass the csv_path as arg
$ poetry run python src/validator/main.py src/tests/data/sbl-validations-pass.csv

# Test validating the "bad" file
$ poetry run python src/validator/main.py 000TESTFIUIDDONOTUSE src/tests/data/sbl-validations-fail.csv
# or
$ poetry run python src/validator/main.py src/tests/data/sbl-validations-fail.csv

# example of an output when validations passed:
$ poetry run python src/validator/main.py src/tests/data/sbl-validations-pass.csv
--------------------------------------------------------------------------
Performing validation on the following DataFrame.

                                       uid  app_date app_method app_recipient ct_credit_product  ... po_4_race_asian_ff po_4_race_baa_ff po_4_race_pi_ff po_4_gender_flag po_4_gender_ff
0         000TESTFIUIDDONOTUSEXGXVID11XTC1  20241201          1             1               988  ...                                                                                    
1         000TESTFIUIDDONOTUSEXGXVID12XTC1  20241201          1             1               988  ...                                                                                    
2         000TESTFIUIDDONOTUSEXGXVID13XTC1  20241201          1             1               988  ...                                                                                    
3         000TESTFIUIDDONOTUSEXGXVID14XTC1  20241201          1             1               988  ...                                                                                    
4         000TESTFIUIDDONOTUSEXGXVID21XTC1  20241201          1             1               988  ...                                                                                    
..                                     ...       ...        ...           ...               ...  ...                ...              ...             ...              ...            ...
522  000TESTFIUIDDONOTUSEXGXVIDPODEMO0XTC1  20241201          1             1               988  ...                                                                                    
523  000TESTFIUIDDONOTUSEXGXVIDPODEMO1XTC1  20241201          1             1               988  ...                                                                                    
524  000TESTFIUIDDONOTUSEXGXVIDPODEMO2XTC1  20241201          1             1               988  ...                                                                                    
525  000TESTFIUIDDONOTUSEXGXVIDPODEMO3XTC1  20241201          1             1               988  ...                                                                                    
526  000TESTFIUIDDONOTUSEXGXVIDPODEMO4XTC1  20241201          1             1               988  ...                                                                  988               

[527 rows x 81 columns]

[{'response': 'No validations errors or warnings'}]


# example of failed validation(s):
$ poetry run python src/validator/main.py src/tests/data/sbl-validations-fail.csv
--------------------------------------------------------------------------
Performing validation on the following DataFrame.

                                                uid  app_date app_method app_recipient  ... po_4_race_baa_ff po_4_race_pi_ff po_4_gender_flag po_4_gender_ff
0                                                    20241201          1             1  ...                                                                 
1                                   BXUIDXVID11XTC2  20241201          1             1  ...                                                                 
2    BXUIDXVID11XTC31234567890123456789012345678901  20241201          1             1  ...                                                                 
3                             BXUIDXVID12XTC1abcdef  20241201          1             1  ...                                                                 
4                  000TESTFIUIDDONOTUSEXBXVID13XTC1  20241201          1             1  ...                                                                 
..                                              ...       ...        ...           ...  ...              ...             ...              ...            ...
364           000TESTFIUIDDONOTUSEXBXVIDPODEMO4XTC5  20241201          1             1  ...                                               988               
365           000TESTFIUIDDONOTUSEXBXVIDPODEMO4XTC6  20241201          1             1  ...                                               988               
366           000TESTFIUIDDONOTUSEXBXVIDPODEMO4XTC7  20241201          1             1  ...                                               988               
367           000TESTFIUIDDONOTUSEXBXVIDPODEMO4XTC8  20241201          1             1  ...                                               988               
368           000TESTFIUIDDONOTUSEXBXVIDPODEMO4XTC9  20241201          1             1  ...                                               988               

[369 rows x 81 columns]

[{'validation': {'id': 'E3000', 'name': 'uid.duplicates_in_dataset', 'description': "Any 'unique identifier' may not be used in more than one record within a small business lending application register.", 'fields': ['uid'], 'severity': 'error'}, 'records': [{'number': 5, 'field_values': {'uid': '000TESTFIUIDDONOTUSEXBXVID13XTC1'}}, {'number': 6, 'field_values': {'uid': '000TESTFIUIDDONOTUSEXBXVID13XTC1'}}]}, {'validation': {'id': 'E0001', 'name': 'uid.invalid_text_length', 'description': "'Unique identifier' must be at least 21 characters in length and at most 45 characters in length.", 'fields': ['uid'], 'severity': 'error'}, 'records': [{'number': 1, 'field_values': {'uid': ''}}, {'number': 2, 'field_values': {'uid': 'BXUIDXVID11XTC2'}}, {'number': 3, 'field_values': {'uid': 'BXUIDXVID11XTC31234567890123456789012345678901'}}]}, {'validation': {'id': 'E0002', 'name': 'uid.invalid_text_pattern', 'description': "'Unique identifier' may contain any combination of numbers and/or uppercase letters (i.e., 0-9 and A-Z), and must not contain any other characters.", 'fields': ['uid'], 'severity': 'error'}, 'records': [{'number': 1, 'field_values': {'uid': ''}}, {'number': 4, 'field_values': {'uid': 'BXUIDXVID12XTC1abcdef'}}]}, {'validation': {'id': 'E0020', 'name': 'app_date.invalid_date_format', 'description': "'Application date' must be a real calendar date using YYYYMMDD format.", 'fields': ['app_date'], 'severity': 'error'}, 'records': [{'number': 8, 'field_values': {'app_date': ''}}, {'number': 9, 'field_values': {'app_date': '12012024'}}]}, {'validation': {'id': 'E0040', 'name': 'app_method.invalid_enum_value', 'description': "'Application method' must equal 1, 2, 3, or 4.", 'fields': ['app_method'], 'severity': 'error'}, 'records': [{'number': 10, 'field_values': {'app_method': ''}}, {'number': 11, 'field_values': {'app_method': '9001'}}]}, {'validation': {'id': 'E0060', 'name': 'app_recipient.invalid_enum_value', 'description': "'Application recipient' must equal 1 or 2", 'fields': ['app_recipient'], 'severity': 'error'}, 'records': [{'number': 12, 'field_values': {'app_recipient': ''}}, {'number': 13, 'field_values': {'app_recipient': '9001'}}]}, {'validation': {'id': 'E0080', 'name': 'ct_credit_product.invalid_enum_value', 'description': "'Credit product' must equal 1, 2, 3, 4, 5, 6, 7, 8, 977, or 988.", 'fields': ['ct_credit_product'], 'severity': 'error'}, 'records': [{'number': 14, 'field_values': {'ct_credit_product': ''}}, {'number': 15, 'field_values': {'ct_credit_product': '9001'}}]}, {'validation': {'id': 'E0100', 'name': 'ct_credit_product_ff.invalid_text_length', 'description': "'Free-form text field for other credit products' must not exceed 300 characters in length.", 'fields': ['ct_credit_product_ff'], 'severity': 'error'}, 'records': [{'number': 16, 'field_values': {'ct_credit_product_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0120', 'name': 'ct_guarantee.invalid_enum_value', 'description': "Each value in 'type of guarantee' (separated by  semicolons) must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 977, or 999.", 'fields': ['ct_guarantee'], 'severity': 'error'}, 'records': [{'number': 19, 'field_values': {'ct_guarantee': '9001'}}, {'number': 20, 'field_values': {'ct_guarantee': ''}}]}, {'validation': {'id': 'E0140', 'name': 'ct_guarantee_ff.invalid_text_length', 'description': "'Free-form text field for other guarantee' must not exceed 300 characters in length", 'fields': ['ct_guarantee_ff'], 'severity': 'error'}, 'records': [{'number': 24, 'field_values': {'ct_guarantee_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0160', 'name': 'ct_loan_term_flag.invalid_enum_value', 'description': "Each value in 'Loan term: NA/NP flag' (separated by  semicolons) must equal 900, 988, or 999.", 'fields': ['ct_loan_term_flag'], 'severity': 'error'}, 'records': [{'number': 29, 'field_values': {'ct_loan_term_flag': ''}}, {'number': 30, 'field_values': {'ct_loan_term_flag': '9001'}}, {'number': 33, 'field_values': {'ct_loan_term_flag': '1'}}]}, {'validation': {'id': 'E0180', 'name': 'ct_loan_term.invalid_numeric_format', 'description': "When present, 'loan term' must be a whole number.", 'fields': ['ct_loan_term'], 'severity': 'error'}, 'records': [{'number': 36, 'field_values': {'ct_loan_term': 'must be blank'}}]}, {'validation': {'id': 'E0200', 'name': 'credit_purpose.invalid_enum_value', 'description': "Each value in 'credit purpose' (separated by  semicolons) must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 977, 988, or 999.", 'fields': ['credit_purpose'], 'severity': 'error'}, 'records': [{'number': 39, 'field_values': {'credit_purpose': '1;2;9001'}}, {'number': 40, 'field_values': {'credit_purpose': ''}}]}, {'validation': {'id': 'E0220', 'name': 'credit_purpose_ff.invalid_text_length', 'description': "'Free-form text field for other credit purpose'  must not exceed 300 characters in length", 'fields': ['credit_purpose_ff'], 'severity': 'error'}, 'records': [{'number': 45, 'field_values': {'credit_purpose_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0240', 'name': 'amount_applied_for_flag.invalid_enum_value', 'description': "'Amount applied For: NA/NP flag' must equal 900, 988, or 999.", 'fields': ['amount_applied_for_flag'], 'severity': 'error'}, 'records': [{'number': 50, 'field_values': {'amount_applied_for_flag': ''}}, {'number': 51, 'field_values': {'amount_applied_for_flag': '9001'}}]}, {'validation': {'id': 'E0260', 'name': 'amount_applied_for.invalid_numeric_format', 'description': "When present, 'amount applied for' must be a numeric value.", 'fields': ['amount_applied_for'], 'severity': 'error'}, 'records': [{'number': 52, 'field_values': {'amount_applied_for': 'nonNumericValue'}}, {'number': 55, 'field_values': {'amount_applied_for': 'must be blank'}}]}, {'validation': {'id': 'E0280', 'name': 'amount_approved.invalid_numeric_format', 'description': "When present, 'amount approved or originated' must be a numeric value.", 'fields': ['amount_approved'], 'severity': 'error'}, 'records': [{'number': 56, 'field_values': {'amount_approved': 'nonNumericValue'}}]}, {'validation': {'id': 'E0300', 'name': 'action_taken.invalid_enum_value', 'description': "'Action taken' must equal 1, 2, 3, 4, or 5.", 'fields': ['action_taken'], 'severity': 'error'}, 'records': [{'number': 63, 'field_values': {'action_taken': ''}}, {'number': 64, 'field_values': {'action_taken': '9001'}}]}, {'validation': {'id': 'E0320', 'name': 'action_taken_date.invalid_date_format', 'description': "'Action taken date' must be a real calendar date using YYYYMMDD format.", 'fields': ['action_taken_date'], 'severity': 'error'}, 'records': [{'number': 65, 'field_values': {'action_taken_date': '12312024'}}]}, {'validation': {'id': 'E0001', 'name': 'denial_reasons.invalid_enum_value', 'description': "Each value in 'denial reason(s)' (separated by semicolons)must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 977, or 999.", 'fields': ['denial_reasons'], 'severity': 'error'}, 'records': [{'number': 70, 'field_values': {'denial_reasons': '9001'}}, {'number': 71, 'field_values': {'denial_reasons': ''}}, {'number': 78, 'field_values': {'denial_reasons': '999;1; 2'}}]}, {'validation': {'id': 'E0360', 'name': 'denial_reasons_ff.invalid_text_length', 'description': "'Free-form text field for other denial reason(s)'must not exceed 300 characters in length.", 'fields': ['denial_reasons_ff'], 'severity': 'error'}, 'records': [{'number': 80, 'field_values': {'denial_reasons_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0380', 'name': 'pricing_interest_rate_type.invalid_enum_value', 'description': "Each value in 'Interest rate type' (separated by  semicolons) Must equal 1, 2, 3, 4, 5, 6, or 999", 'fields': ['pricing_interest_rate_type'], 'severity': 'error'}, 'records': [{'number': 85, 'field_values': {'pricing_interest_rate_type': ''}}, {'number': 86, 'field_values': {'pricing_interest_rate_type': '9001'}}, {'number': 87, 'field_values': {'pricing_interest_rate_type': '900'}}, {'number': 94, 'field_values': {'pricing_interest_rate_type': '900'}}, {'number': 101, 'field_values': {'pricing_interest_rate_type': '900'}}]}, {'validation': {'id': 'E0400', 'name': 'pricing_init_rate_period.invalid_numeric_format', 'description': ("When present, 'initial rate period' must be a whole number.",), 'fields': ['pricing_init_rate_period'], 'severity': 'error'}, 'records': [{'number': 118, 'field_values': {'pricing_init_rate_period': 'nonNumericValue'}}]}, {'validation': {'id': 'E0420', 'name': 'pricing_fixed_rate.invalid_numeric_format', 'description': "When present, 'fixed rate: interest rate' must be a numeric value.", 'fields': ['pricing_fixed_rate'], 'severity': 'error'}, 'records': [{'number': 127, 'field_values': {'pricing_fixed_rate': 'nonNumericValue'}}]}, {'validation': {'id': 'E0460', 'name': 'pricing_adj_index_name.invalid_enum_value', 'description': "'Adjustable rate transaction: index name' must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 977, or 999.", 'fields': ['pricing_adj_index_name'], 'severity': 'error'}, 'records': [{'number': 145, 'field_values': {'pricing_adj_index_name': ''}}, {'number': 146, 'field_values': {'pricing_adj_index_name': '9001'}}]}, {'validation': {'id': 'E0480', 'name': 'pricing_adj_index_name_ff.invalid_text_length', 'description': "'Adjustable rate transaction: index name: other' must not exceed 300 characters in length.", 'fields': ['pricing_adj_index_name_ff'], 'severity': 'error'}, 'records': [{'number': 154, 'field_values': {'pricing_adj_index_name_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0500', 'name': 'pricing_adj_index_value.invalid_numeric_format', 'description': "When present, 'adjustable rate transaction: index value' must be a numeric value.", 'fields': ['pricing_adj_index_value'], 'severity': 'error'}, 'records': [{'number': 157, 'field_values': {'pricing_adj_index_value': 'nonNumericValue'}}]}, {'validation': {'id': 'E0520', 'name': 'pricing_origination_charges.invalid_numeric_format', 'description': ("When present, 'total origination charges' must be a numeric", 'value.'), 'fields': ['pricing_origination_charges'], 'severity': 'error'}, 'records': [{'number': 165, 'field_values': {'pricing_origination_charges': 'nonNumericValue'}}]}, {'validation': {'id': 'E0540', 'name': 'pricing_broker_fees.invalid_numeric_format', 'description': ("When present, 'amount of total broker fees' must be a", 'numeric value.'), 'fields': ['pricing_broker_fees'], 'severity': 'error'}, 'records': [{'number': 166, 'field_values': {'pricing_broker_fees': 'nonNumericValue'}}]}, {'validation': {'id': 'E0560', 'name': 'pricing_initial_charges.invalid_numeric_format', 'description': "When present, 'initial annual charges' must be anumeric value.", 'fields': ['pricing_initial_charges'], 'severity': 'error'}, 'records': [{'number': 167, 'field_values': {'pricing_initial_charges': 'nonNumericValue'}}]}, {'validation': {'id': 'E0580', 'name': 'pricing_mca_addcost_flag.invalid_enum_value', 'description': "'MCA/sales-based: additional cost for merchant cash advances or other sales-based financing: NA flag' must equal 900 or 999.", 'fields': ['pricing_mca_addcost_flag'], 'severity': 'error'}, 'records': [{'number': 168, 'field_values': {'pricing_mca_addcost_flag': ''}}, {'number': 169, 'field_values': {'pricing_mca_addcost_flag': '99009001'}}]}, {'validation': {'id': 'E0600', 'name': 'pricing_mca_addcost.invalid_numeric_format', 'description': "When present, 'MCA/sales-based: additional cost for merchant cash advances or other sales-based financing' must be a numeric value", 'fields': ['pricing_mca_addcost'], 'severity': 'error'}, 'records': [{'number': 171, 'field_values': {'pricing_mca_addcost': 'nonNumericValue'}}, {'number': 172, 'field_values': {'pricing_mca_addcost': 'must be blank'}}]}, {'validation': {'id': 'E0620', 'name': 'pricing_prepenalty_allowed.invalid_enum_value', 'description': "'Prepayment penalty could be imposed' must equal 1, 2, or 999.", 'fields': ['pricing_prepenalty_allowed'], 'severity': 'error'}, 'records': [{'number': 174, 'field_values': {'pricing_prepenalty_allowed': ''}}, {'number': 175, 'field_values': {'pricing_prepenalty_allowed': '9001'}}]}, {'validation': {'id': 'E0640', 'name': 'pricing_prepenalty_exists.invalid_enum_value', 'description': "'Prepayment penalty exists' must equal 1, 2, or 999.", 'fields': ['pricing_prepenalty_exists'], 'severity': 'error'}, 'records': [{'number': 176, 'field_values': {'pricing_prepenalty_exists': ''}}, {'number': 177, 'field_values': {'pricing_prepenalty_exists': '9001'}}]}, {'validation': {'id': 'E0640', 'name': 'census_tract_adr_type.invalid_enum_value', 'description': "'Census tract: type of address' must equal 1, 2, 3, or 988.", 'fields': ['census_tract_adr_type'], 'severity': 'error'}, 'records': [{'number': 178, 'field_values': {'census_tract_adr_type': ''}}, {'number': 179, 'field_values': {'census_tract_adr_type': '9001'}}]}, {'validation': {'id': 'E0680', 'name': 'census_tract_number.invalid_text_length', 'description': "When present, 'census tract: tract number' must be a GEOID with exactly 11 digits.", 'fields': ['census_tract_number'], 'severity': 'error'}, 'records': [{'number': 181, 'field_values': {'census_tract_number': '1234567890'}}, {'number': 182, 'field_values': {'census_tract_number': 'must be blank'}}]}, {'validation': {'id': 'E0700', 'name': 'gross_annual_revenue_flag.invalid_enum_value', 'description': "'Gross annual revenue: NP flag' must equal 900 or 988.", 'fields': ['gross_annual_revenue_flag'], 'severity': 'error'}, 'records': [{'number': 187, 'field_values': {'gross_annual_revenue_flag': ''}}, {'number': 188, 'field_values': {'gross_annual_revenue_flag': '99009001'}}]}, {'validation': {'id': 'E0720', 'name': 'gross_annual_revenue.invalid_numeric_format', 'description': "When present, 'gross annual revenue' must be a numeric value.", 'fields': ['gross_annual_revenue'], 'severity': 'error'}, 'records': [{'number': 189, 'field_values': {'gross_annual_revenue': 'nonNumericValue'}}, {'number': 190, 'field_values': {'gross_annual_revenue': 'must be blank'}}]}, {'validation': {'id': 'E0720', 'name': 'naics_code_flag.invalid_enum_value', 'description': "'North American Industry Classification System (NAICS) code: NP flag' must equal 900 or 988.", 'fields': ['naics_code_flag'], 'severity': 'error'}, 'records': [{'number': 192, 'field_values': {'naics_code_flag': ''}}, {'number': 193, 'field_values': {'naics_code_flag': '9001'}}]}, {'validation': {'id': 'E0761', 'name': 'naics_code.invalid_naics_format', 'description': "'North American Industry Classification System (NAICS) code' may only contain numeric characters.", 'fields': ['naics_code'], 'severity': 'error'}, 'records': [{'number': 196, 'field_values': {'naics_code': 'notDigits'}}]}, {'validation': {'id': 'E0780', 'name': 'number_of_workers.invalid_enum_value', 'description': "'Number of workers' must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, or 988.", 'fields': ['number_of_workers'], 'severity': 'error'}, 'records': [{'number': 199, 'field_values': {'number_of_workers': ''}}, {'number': 200, 'field_values': {'number_of_workers': '9001'}}]}, {'validation': {'id': 'E0800', 'name': 'time_in_business_type.invalid_enum_value', 'description': "'Time in business: type of response' must equal 1, 2, 3, or 988.", 'fields': ['time_in_business_type'], 'severity': 'error'}, 'records': [{'number': 201, 'field_values': {'time_in_business_type': ''}}, {'number': 202, 'field_values': {'time_in_business_type': '9001'}}]}, {'validation': {'id': 'E0820', 'name': 'time_in_business.invalid_numeric_format', 'description': "When present, 'time in business' must be a whole number.", 'fields': ['time_in_business'], 'severity': 'error'}, 'records': [{'number': 205, 'field_values': {'time_in_business': 'must be blank'}}]}, {'validation': {'id': 'E0840', 'name': 'business_ownership_status.invalid_enum_value', 'description': "Each value in 'business ownership status' (separated by semicolons) must equal 1, 2, 3, 955, 966, or 988.", 'fields': ['business_ownership_status'], 'severity': 'error'}, 'records': [{'number': 207, 'field_values': {'business_ownership_status': '1;2; 9001'}}, {'number': 208, 'field_values': {'business_ownership_status': ''}}]}, {'validation': {'id': 'E0860', 'name': 'num_principal_owners_flag.invalid_enum_value', 'description': "'Number of principal owners: NP flag' must equal 900 or 988.", 'fields': ['num_principal_owners_flag'], 'severity': 'error'}, 'records': [{'number': 211, 'field_values': {'num_principal_owners_flag': ''}}, {'number': 212, 'field_values': {'num_principal_owners_flag': '9001'}}]}, {'validation': {'id': 'E0880', 'name': 'num_principal_owners.invalid_enum_value', 'description': "When present, 'number of principal owners' must equal 0, 1, 2, 3, or 4.", 'fields': ['num_principal_owners'], 'severity': 'error'}, 'records': [{'number': 213, 'field_values': {'num_principal_owners': '9001'}}, {'number': 214, 'field_values': {'num_principal_owners': 'must be blank'}}]}, {'validation': {'id': 'E0900', 'name': 'po_1_ethnicity.invalid_enum_value', 'description': "When present, each value in 'ethnicity of principal owner 1' (separated by semicolons) must equal 1, 11, 12, 13, 14, 2, 966, 977, or 988.", 'fields': ['po_1_ethnicity'], 'severity': 'error'}, 'records': [{'number': 216, 'field_values': {'po_1_ethnicity': '9001;1'}}]}, {'validation': {'id': 'E0920', 'name': 'po_1_ethnicity_ff.invalid_text_length', 'description': "'Ethnicity of principal owner 1: free-form text field for other Hispanic or Latino' must not exceed 300 characters in length.", 'fields': ['po_1_ethnicity_ff'], 'severity': 'error'}, 'records': [{'number': 228, 'field_values': {'po_1_ethnicity_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0940', 'name': 'po_1_race.invalid_enum_value', 'description': "When present, each value in 'race of principal owner 1' (separated by semicolons) must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 31, 32, 33, 34, 35, 36, 37, 4, 41, 42, 43, 44, 5, 966, 971, 972, 973, 974, or 988.", 'fields': ['po_1_race'], 'severity': 'error'}, 'records': [{'number': 240, 'field_values': {'po_1_race': '9001;1'}}]}, {'validation': {'id': 'E0960', 'name': 'po_1_race_anai_ff.invalid_text_length', 'description': "'Race of principal owner 1: free-form text field for American Indian or Alaska Native Enrolled or Principal Tribe' must not exceed 300 characters in length.", 'fields': ['po_1_race_anai_ff'], 'severity': 'error'}, 'records': [{'number': 252, 'field_values': {'po_1_race_anai_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0980', 'name': 'po_1_race_asian_ff.invalid_text_length', 'description': "'Race of principal owner 1: free-form text field for other Asian' must not exceed 300 characters in length.", 'fields': ['po_1_race_asian_ff'], 'severity': 'error'}, 'records': [{'number': 264, 'field_values': {'po_1_race_asian_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1000', 'name': 'po_1_race_baa_ff.invalid_text_length', 'description': "'Race of principal owner 1: free-form text field for other Black or African American' must not exceed 300 characters in length.", 'fields': ['po_1_race_baa_ff'], 'severity': 'error'}, 'records': [{'number': 276, 'field_values': {'po_1_race_baa_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1020', 'name': 'po_1_race_pi_ff.invalid_text_length', 'description': "'Race of principal owner 1: free-form text field for other Pacific Islander race' must not exceed 300 characters in length.", 'fields': ['po_1_race_pi_ff'], 'severity': 'error'}, 'records': [{'number': 288, 'field_values': {'po_1_race_pi_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1040', 'name': 'po_1_gender_flag.invalid_enum_value', 'description': "When present, 'sex/gender of principal owner 1: NP flag' must equal 1, 966, or 988.", 'fields': ['po_1_gender_flag'], 'severity': 'error'}, 'records': [{'number': 300, 'field_values': {'po_1_gender_flag': '9001'}}]}, {'validation': {'id': 'E1060', 'name': 'po_1_gender_ff.invalid_text_length', 'description': "'Sex/gender of principal owner 1: free-form text field for self-identified sex/gender' must not exceed 300 characters in length.", 'fields': ['po_1_gender_ff'], 'severity': 'error'}, 'records': [{'number': 304, 'field_values': {'po_1_gender_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0900', 'name': 'po_2_ethnicity.invalid_enum_value', 'description': "When present, each value in 'ethnicity of principal owner 2' (separated by semicolons) must equal 1, 11, 12, 13, 14, 2, 966, 977, or 988.", 'fields': ['po_2_ethnicity'], 'severity': 'error'}, 'records': [{'number': 217, 'field_values': {'po_2_ethnicity': '9001;1'}}]}, {'validation': {'id': 'E0920', 'name': 'po_2_ethnicity_ff.invalid_text_length', 'description': "'Ethnicity of principal owner 2: free-form text field for other Hispanic or Latino' must not exceed 300 characters in length.", 'fields': ['po_2_ethnicity_ff'], 'severity': 'error'}, 'records': [{'number': 229, 'field_values': {'po_2_ethnicity_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0940', 'name': 'po_2_race.invalid_enum_value', 'description': "When present, each value in 'race of principal owner 2' (separated by semicolons) must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 31, 32, 33, 34, 35, 36, 37, 4, 41, 42, 43, 44, 5, 966, 971, 972, 973, 974, or 988.", 'fields': ['po_2_race'], 'severity': 'error'}, 'records': [{'number': 241, 'field_values': {'po_2_race': '9001;1'}}]}, {'validation': {'id': 'E0960', 'name': 'po_2_race_anai_ff.invalid_text_length', 'description': "'Race of principal owner 2: free-form text field for American Indian or Alaska Native Enrolled or Principal Tribe' must not exceed 300 characters in length.", 'fields': ['po_2_race_anai_ff'], 'severity': 'error'}, 'records': [{'number': 253, 'field_values': {'po_2_race_anai_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0980', 'name': 'po_2_race_asian_ff.invalid_text_length', 'description': "'Race of principal owner 2: free-form text field for other Asian' must not exceed 300 characters in length.", 'fields': ['po_2_race_asian_ff'], 'severity': 'error'}, 'records': [{'number': 265, 'field_values': {'po_2_race_asian_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1000', 'name': 'po_2_race_baa_ff.invalid_text_length', 'description': "'Race of principal owner 2: free-form text field for other Black or African American' must not exceed 300 characters in length.", 'fields': ['po_2_race_baa_ff'], 'severity': 'error'}, 'records': [{'number': 277, 'field_values': {'po_2_race_baa_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1020', 'name': 'po_2_race_pi_ff.invalid_text_length', 'description': "'Race of principal owner 2: free-form text field for other Pacific Islander race' must not exceed 300 characters in length.", 'fields': ['po_2_race_pi_ff'], 'severity': 'error'}, 'records': [{'number': 289, 'field_values': {'po_2_race_pi_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1040', 'name': 'po_2_gender_flag.invalid_enum_value', 'description': "When present, 'sex/gender of principal owner 2: NP flag' must equal 1, 966, or 988.", 'fields': ['po_2_gender_flag'], 'severity': 'error'}, 'records': [{'number': 301, 'field_values': {'po_2_gender_flag': '9001'}}]}, {'validation': {'id': 'E1060', 'name': 'po_2_gender_ff.invalid_text_length', 'description': "'Sex/gender of principal owner 2: free-form text field for self-identified sex/gender' must not exceed 300 characters in length.", 'fields': ['po_2_gender_ff'], 'severity': 'error'}, 'records': [{'number': 305, 'field_values': {'po_2_gender_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0900', 'name': 'po_3_ethnicity.invalid_enum_value', 'description': "When present, each value in 'ethnicity of principal owner 3' (separated by semicolons) must equal 1, 11, 12, 13, 14, 2, 966, 977, or 988.", 'fields': ['po_3_ethnicity'], 'severity': 'error'}, 'records': [{'number': 218, 'field_values': {'po_3_ethnicity': '9001;1'}}]}, {'validation': {'id': 'E0920', 'name': 'po_3_ethnicity_ff.invalid_text_length', 'description': "'Ethnicity of principal owner 3: free-form text field for other Hispanic or Latino' must not exceed 300 characters in length.", 'fields': ['po_3_ethnicity_ff'], 'severity': 'error'}, 'records': [{'number': 230, 'field_values': {'po_3_ethnicity_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0940', 'name': 'po_3_race.invalid_enum_value', 'description': "When present, each value in 'race of principal owner 3' (separated by semicolons) must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 31, 32, 33, 34, 35, 36, 37, 4, 41, 42, 43, 44, 5, 966, 971, 972, 973, 974, or 988.", 'fields': ['po_3_race'], 'severity': 'error'}, 'records': [{'number': 242, 'field_values': {'po_3_race': '9001;1'}}]}, {'validation': {'id': 'E0960', 'name': 'po_3_race_anai_ff.invalid_text_length', 'description': "'Race of principal owner 3: free-form text field for American Indian or Alaska Native Enrolled or Principal Tribe' must not exceed 300 characters in length.", 'fields': ['po_3_race_anai_ff'], 'severity': 'error'}, 'records': [{'number': 254, 'field_values': {'po_3_race_anai_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0980', 'name': 'po_3_race_asian_ff.invalid_text_length', 'description': "'Race of principal owner 3: free-form text field for other Asian' must not exceed 300 characters in length.", 'fields': ['po_3_race_asian_ff'], 'severity': 'error'}, 'records': [{'number': 266, 'field_values': {'po_3_race_asian_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1000', 'name': 'po_3_race_baa_ff.invalid_text_length', 'description': "'Race of principal owner 3: free-form text field for other Black or African American' must not exceed 300 characters in length.", 'fields': ['po_3_race_baa_ff'], 'severity': 'error'}, 'records': [{'number': 278, 'field_values': {'po_3_race_baa_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1020', 'name': 'po_3_race_pi_ff.invalid_text_length', 'description': "'Race of principal owner 3: free-form text field for other Pacific Islander race' must not exceed 300 characters in length.", 'fields': ['po_3_race_pi_ff'], 'severity': 'error'}, 'records': [{'number': 290, 'field_values': {'po_3_race_pi_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1040', 'name': 'po_3_gender_flag.invalid_enum_value', 'description': "When present, 'sex/gender of principal owner 3: NP flag' must equal 1, 966, or 988.", 'fields': ['po_3_gender_flag'], 'severity': 'error'}, 'records': [{'number': 302, 'field_values': {'po_3_gender_flag': '9001'}}]}, {'validation': {'id': 'E1060', 'name': 'po_3_gender_ff.invalid_text_length', 'description': "'Sex/gender of principal owner 3: free-form text field for self-identified sex/gender' must not exceed 300 characters in length.", 'fields': ['po_3_gender_ff'], 'severity': 'error'}, 'records': [{'number': 306, 'field_values': {'po_3_gender_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0900', 'name': 'po_4_ethnicity.invalid_enum_value', 'description': "When present, each value in 'ethnicity of principal owner 4' (separated by semicolons) must equal 1, 11, 12, 13, 14, 2, 966, 977, or 988.", 'fields': ['po_4_ethnicity'], 'severity': 'error'}, 'records': [{'number': 219, 'field_values': {'po_4_ethnicity': '9001;1'}}]}, {'validation': {'id': 'E0920', 'name': 'po_4_ethnicity_ff.invalid_text_length', 'description': "'Ethnicity of principal owner 4: free-form text field for other Hispanic or Latino' must not exceed 300 characters in length.", 'fields': ['po_4_ethnicity_ff'], 'severity': 'error'}, 'records': [{'number': 231, 'field_values': {'po_4_ethnicity_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0940', 'name': 'po_4_race.invalid_enum_value', 'description': "When present, each value in 'race of principal owner 4' (separated by semicolons) must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 31, 32, 33, 34, 35, 36, 37, 4, 41, 42, 43, 44, 5, 966, 971, 972, 973, 974, or 988.", 'fields': ['po_4_race'], 'severity': 'error'}, 'records': [{'number': 243, 'field_values': {'po_4_race': '9001;1'}}]}, {'validation': {'id': 'E0960', 'name': 'po_4_race_anai_ff.invalid_text_length', 'description': "'Race of principal owner 4: free-form text field for American Indian or Alaska Native Enrolled or Principal Tribe' must not exceed 300 characters in length.", 'fields': ['po_4_race_anai_ff'], 'severity': 'error'}, 'records': [{'number': 255, 'field_values': {'po_4_race_anai_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E0980', 'name': 'po_4_race_asian_ff.invalid_text_length', 'description': "'Race of principal owner 4: free-form text field for other Asian' must not exceed 300 characters in length.", 'fields': ['po_4_race_asian_ff'], 'severity': 'error'}, 'records': [{'number': 267, 'field_values': {'po_4_race_asian_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1000', 'name': 'po_4_race_baa_ff.invalid_text_length', 'description': "'Race of principal owner 4: free-form text field for other Black or African American' must not exceed 300 characters in length.", 'fields': ['po_4_race_baa_ff'], 'severity': 'error'}, 'records': [{'number': 279, 'field_values': {'po_4_race_baa_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1020', 'name': 'po_4_race_pi_ff.invalid_text_length', 'description': "'Race of principal owner 4: free-form text field for other Pacific Islander race' must not exceed 300 characters in length.", 'fields': ['po_4_race_pi_ff'], 'severity': 'error'}, 'records': [{'number': 291, 'field_values': {'po_4_race_pi_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}, {'validation': {'id': 'E1040', 'name': 'po_4_gender_flag.invalid_enum_value', 'description': "When present, 'sex/gender of principal owner 4: NP flag' must equal 1, 966, or 988.", 'fields': ['po_4_gender_flag'], 'severity': 'error'}, 'records': [{'number': 303, 'field_values': {'po_4_gender_flag': '9001'}}]}, {'validation': {'id': 'E1060', 'name': 'po_4_gender_ff.invalid_text_length', 'description': "'Sex/gender of principal owner 4: free-form text field for self-identified sex/gender' must not exceed 300 characters in length.", 'fields': ['po_4_gender_ff'], 'severity': 'error'}, 'records': [{'number': 307, 'field_values': {'po_4_gender_ff': '123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890XXX'}}]}]
```

## Running Test

This repository is using `pytest`.  If using VS Code, tests can be completed within a Dev Container.  If using local terminal or console, you can use this command `poetry run pytest` in the root directory

```sh
# example of unit tests output
$ poetry run pytest
================================================================================== test session starts ==================================================================================
platform darwin -- Python 3.11.5, pytest-7.4.0, pluggy-1.3.0 -- /Library/Caches/pypoetry/virtualenvs/regtech-data-validator-uJQWmvcM-py3.11/bin/python
cachedir: .pytest_cache
rootdir: /Projects/regtech-data-validator
configfile: pyproject.toml
testpaths: src/tests
plugins: cov-4.1.0, typeguard-4.1.3
collected 117 items                                                                                                                                                                     

src/tests/test_check_functions.py::TestInvalidDateFormat::test_with_valid_date <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED          [  0%]
src/tests/test_check_functions.py::TestInvalidDateFormat::test_with_invalid_date <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED        [  1%]
src/tests/test_check_functions.py::TestInvalidDateFormat::test_with_invalid_day <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED         [  2%]
src/tests/test_check_functions.py::TestInvalidDateFormat::test_with_invalid_month <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED       [  3%]
src/tests/test_check_functions.py::TestInvalidDateFormat::test_with_invalid_year <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED        [  4%]
src/tests/test_check_functions.py::TestInvalidDateFormat::test_with_invalid_format <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED      [  5%]
src/tests/test_check_functions.py::TestInvalidDateFormat::test_with_invalid_type <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED        [  5%]
src/tests/test_check_functions.py::TestDuplicatesInField::test_with_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED               [  6%]
src/tests/test_check_functions.py::TestDuplicatesInField::test_with_no_duplicates <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED       [  7%]
src/tests/test_check_functions.py::TestDuplicatesInField::test_with_duplicates <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED          [  8%]
src/tests/test_check_functions.py::TestInvalidNumberOfValues::test_with_in_range <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED        [  9%]
src/tests/test_check_functions.py::TestInvalidNumberOfValues::test_with_lower_range_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 10%]
src/tests/test_check_functions.py::TestInvalidNumberOfValues::test_with_invalid_lower_range_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 11%]
src/tests/test_check_functions.py::TestInvalidNumberOfValues::test_with_upper_range_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 11%]
src/tests/test_check_functions.py::TestInvalidNumberOfValues::test_with_invalid_upper_range_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 12%]
src/tests/test_check_functions.py::TestInvalidNumberOfValues::test_valid_with_no_upper_bound <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 13%]
src/tests/test_check_functions.py::TestInvalidNumberOfValues::test_invalid_with_no_upper_bound <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 14%]
src/tests/test_check_functions.py::TestMultiValueFieldRestriction::test_with_invalid_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 15%]
src/tests/test_check_functions.py::TestMultiValueFieldRestriction::test_with_valid_length <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 16%]
src/tests/test_check_functions.py::TestMultiValueFieldRestriction::test_with_valid_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 17%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_inside_maxlength <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 17%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_on_maxlength <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED    [ 18%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_with_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED      [ 19%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_invalid_length_with_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 20%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_invalid_length_with_blank_and_ignored_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 21%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_valid_length_with_blank_and_ignored_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 22%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_outside_maxlength <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 23%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_valid_length_with_non_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 23%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_invalid_length_with_non_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 24%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_valid_length_with_ignored_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 25%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_invalid_length_with_ignored_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 26%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_valid_length_with_blank_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 27%]
src/tests/test_check_functions.py::TestMultiInvalidNumberOfValues::test_invalid_length_with_blank_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 28%]
src/tests/test_check_functions.py::TestInvalidEnumValue::test_with_valid_enum_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED    [ 29%]
src/tests/test_check_functions.py::TestInvalidEnumValue::test_with_is_valid_enums <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED       [ 29%]
src/tests/test_check_functions.py::TestInvalidEnumValue::test_with_valid_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED          [ 30%]
src/tests/test_check_functions.py::TestInvalidEnumValue::test_with_invalid_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED        [ 31%]
src/tests/test_check_functions.py::TestIsNumber::test_number_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED                      [ 32%]
src/tests/test_check_functions.py::TestIsNumber::test_non_number_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED                  [ 33%]
src/tests/test_check_functions.py::TestIsNumber::test_decimal_numeric_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED             [ 34%]
src/tests/test_check_functions.py::TestIsNumber::test_alphanumeric_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED                [ 35%]
src/tests/test_check_functions.py::TestIsNumber::test_negative_numeric_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED            [ 35%]
src/tests/test_check_functions.py::TestIsNumber::test_negative_decimal_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED            [ 36%]
src/tests/test_check_functions.py::TestIsNumber::test_valid_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED                       [ 37%]
src/tests/test_check_functions.py::TestIsNumber::test_invalid_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED                     [ 38%]
src/tests/test_check_functions.py::TestConditionalFieldConflict::test_conditional_field_conflict_correct <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 39%]
src/tests/test_check_functions.py::TestConditionalFieldConflict::test_conditional_field_conflict_incorrect <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 40%]
src/tests/test_check_functions.py::TestEnumValueConflict::test_enum_value_confict_correct <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 41%]
src/tests/test_check_functions.py::TestEnumValueConflict::test_enum_value_confict_incorrect <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 41%]
src/tests/test_check_functions.py::TestHasCorrectLength::test_with_accept_blank_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED   [ 42%]
src/tests/test_check_functions.py::TestHasCorrectLength::test_with_invalid_blank_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED  [ 43%]
src/tests/test_check_functions.py::TestHasCorrectLength::test_with_correct_length <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED       [ 44%]
src/tests/test_check_functions.py::TestHasCorrectLength::test_with_incorrect_length <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED     [ 45%]
src/tests/test_check_functions.py::TestIsValidCode::test_with_valid_code <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED                [ 46%]
src/tests/test_check_functions.py::TestIsValidCode::test_with_invalid_code <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED              [ 47%]
src/tests/test_check_functions.py::TestIsValidCode::test_with_accepted_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED            [ 47%]
src/tests/test_check_functions.py::TestIsValidCode::test_with_invalid_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED             [ 48%]
src/tests/test_check_functions.py::TestIsGreaterThan::test_with_greater_min_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED       [ 49%]
src/tests/test_check_functions.py::TestIsGreaterThan::test_with_smaller_min_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED       [ 50%]
src/tests/test_check_functions.py::TestIsGreaterThan::test_with_equal_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED             [ 51%]
src/tests/test_check_functions.py::TestIsGreaterThan::test_with_valid_blank_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED       [ 52%]
src/tests/test_check_functions.py::TestIsGreaterThan::test_with_invalid_blank_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED     [ 52%]
src/tests/test_check_functions.py::TestIsGreaterThanOrEqualTo::test_with_greater_min_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 53%]
src/tests/test_check_functions.py::TestIsGreaterThanOrEqualTo::test_with_smaller_min_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 54%]
src/tests/test_check_functions.py::TestIsGreaterThanOrEqualTo::test_with_equal_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED    [ 55%]
src/tests/test_check_functions.py::TestIsGreaterThanOrEqualTo::test_with_valid_blank_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 56%]
src/tests/test_check_functions.py::TestIsGreaterThanOrEqualTo::test_with_invalid_blank_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 57%]
src/tests/test_check_functions.py::TestIsLessThan::test_with_greater_max_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED          [ 58%]
src/tests/test_check_functions.py::TestIsLessThan::test_with_less_max_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED             [ 58%]
src/tests/test_check_functions.py::TestIsLessThan::test_with_equal_max_value <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED            [ 59%]
src/tests/test_check_functions.py::TestIsLessThan::test_with_valid_blank_space <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED          [ 60%]
src/tests/test_check_functions.py::TestIsLessThan::test_with_invalid_blank_space <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED        [ 61%]
src/tests/test_check_functions.py::TestHasValidFormat::test_with_valid_data_alphanumeric <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 62%]
src/tests/test_check_functions.py::TestHasValidFormat::test_with_invalid_data_alphanumeric <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 63%]
src/tests/test_check_functions.py::TestHasValidFormat::test_with_accepting_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED        [ 64%]
src/tests/test_check_functions.py::TestHasValidFormat::test_with_not_accepting_blank <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED    [ 64%]
src/tests/test_check_functions.py::TestHasValidFormat::test_with_valid_data_ip <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED          [ 65%]
src/tests/test_check_functions.py::TestHasValidFormat::test_with_invalid_data_ip <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED        [ 66%]
src/tests/test_check_functions.py::TestIsUniqueColumn::test_with_valid_series <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED           [ 67%]
src/tests/test_check_functions.py::TestIsUniqueColumn::test_with_multiple_valid_series <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED  [ 68%]
src/tests/test_check_functions.py::TestIsUniqueColumn::test_with_invalid_series <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED         [ 69%]
src/tests/test_check_functions.py::TestIsUniqueColumn::test_with_multiple_items_series <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED  [ 70%]
src/tests/test_check_functions.py::TestIsUniqueColumn::test_with_multiple_invalid_series <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 70%]
src/tests/test_check_functions.py::TestIsUniqueColumn::test_with_multiple_mix_series <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED    [ 71%]
src/tests/test_check_functions.py::TestIsUniqueColumn::test_with_blank_value_series <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED     [ 72%]
src/tests/test_check_functions.py::TestHasValidFieldsetPair::test_with_correct_is_not_equal_condition <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 73%]
src/tests/test_check_functions.py::TestHasValidFieldsetPair::test_with_correct_is_equal_condition <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 74%]
src/tests/test_check_functions.py::TestHasValidFieldsetPair::test_with_correct_is_equal_and_not_equal_conditions <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 75%]
src/tests/test_check_functions.py::TestHasValidFieldsetPair::test_with_value_not_in_condition_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 76%]
src/tests/test_check_functions.py::TestHasValidFieldsetPair::test_with_incorrect_is_not_equal_condition <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 76%]
src/tests/test_check_functions.py::TestHasValidFieldsetPair::test_with_incorrect_is_equal_condition <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 77%]
src/tests/test_check_functions.py::TestHasValidFieldsetPair::test_with_incorrect_is_equal_and_not_equal_conditions <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED [ 78%]
src/tests/test_check_functions.py::TestIsValidId::test_with_correct_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED              [ 79%]
src/tests/test_check_functions.py::TestIsValidId::test_with_incorrect_values <- ../../../../workspaces/regtech-data-validator/src/tests/test_check_functions.py PASSED            [ 80%]
src/tests/test_checks.py::TestSBLCheck::test_no_id_check <- ../../../../workspaces/regtech-data-validator/src/tests/test_checks.py PASSED                                         [ 81%]
src/tests/test_checks.py::TestSBLCheck::test_no_name_check <- ../../../../workspaces/regtech-data-validator/src/tests/test_checks.py PASSED                                       [ 82%]
src/tests/test_checks.py::TestSBLCheck::test_name_and_id_check <- ../../../../workspaces/regtech-data-validator/src/tests/test_checks.py PASSED                                   [ 82%]
src/tests/test_global_data.py::TestGlobalData::test_valid_naics_codes <- ../../../../workspaces/regtech-data-validator/src/tests/test_global_data.py PASSED                       [ 83%]
src/tests/test_global_data.py::TestGlobalData::test_valid_geoids <- ../../../../workspaces/regtech-data-validator/src/tests/test_global_data.py PASSED                            [ 84%]
src/tests/test_global_data.py::TestGlobalData::test_invalid_naics_file <- ../../../../workspaces/regtech-data-validator/src/tests/test_global_data.py PASSED                      [ 85%]
src/tests/test_global_data.py::TestGlobalData::test_invalid_geoids_file <- ../../../../workspaces/regtech-data-validator/src/tests/test_global_data.py PASSED                     [ 86%]
src/tests/test_sample_data.py::TestValidatingSampleData::test_invalid_data_file PASSED                                                                                            [ 87%]
src/tests/test_sample_data.py::TestValidatingSampleData::test_run_validation_on_good_data_invalid_lei PASSED                                                                      [ 88%]
src/tests/test_sample_data.py::TestValidatingSampleData::test_run_validation_on_good_data_valid_lei PASSED                                                                        [ 88%]
src/tests/test_sample_data.py::TestValidatingSampleData::test_run_validation_on_bad_data_invalid_lei PASSED                                                                       [ 89%]
src/tests/test_sample_data.py::TestValidatingSampleData::test_run_validation_on_bad_data_valid_lei PASSED                                                                         [ 90%]
src/tests/test_schema_functions.py::TestValidate::test_with_valid_dataframe <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED            [ 91%]
src/tests/test_schema_functions.py::TestValidate::test_with_valid_lei <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED                  [ 92%]
src/tests/test_schema_functions.py::TestValidate::test_with_invalid_dataframe <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED          [ 93%]
src/tests/test_schema_functions.py::TestValidate::test_with_multi_invalid_dataframe <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED    [ 94%]
src/tests/test_schema_functions.py::TestValidate::test_with_invalid_lei <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED                [ 94%]
src/tests/test_schema_functions.py::TestValidatePhases::test_with_valid_data <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED           [ 95%]
src/tests/test_schema_functions.py::TestValidatePhases::test_with_valid_lei <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED            [ 96%]
src/tests/test_schema_functions.py::TestValidatePhases::test_with_invalid_data <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED         [ 97%]
src/tests/test_schema_functions.py::TestValidatePhases::test_with_multi_invalid_data_with_phase1 <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED [ 98%]
src/tests/test_schema_functions.py::TestValidatePhases::test_with_multi_invalid_data_with_phase2 <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED [ 99%]
src/tests/test_schema_functions.py::TestValidatePhases::test_with_invalid_lei <- ../../../../workspaces/regtech-data-validator/src/tests/test_schema_functions.py PASSED          [100%]

---------- coverage: platform darwin, python 3.11.5-final-0 ----------
Name                                 Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------
src/tests/__init__.py                    4      0      0      0   100%
src/tests/test_check_functions.py      418      0      0      0   100%
src/tests/test_checks.py                20      2     10      3    83%   9->exit, 16->exit, 24->exit, 25-26
src/tests/test_global_data.py           19      0      4      0   100%
src/tests/test_sample_data.py           38      0      2      0   100%
src/tests/test_schema_functions.py      78      0      0      0   100%
src/validator/__init__.py                4      0      0      0   100%
src/validator/check_functions.py       184     14     78      0    91%   55-59, 111-121, 275-276, 297-298, 420-421
src/validator/checks.py                 14      0      4      0   100%
src/validator/create_schemas.py         55      1     18      2    96%   69, 74->49
src/validator/global_data.py            18      0      4      0   100%
src/validator/main.py                   25     25      8      0     0%   8-47
src/validator/phase_validations.py       6      0      0      0   100%
src/validator/schema_template.py         6      0      0      0   100%
--------------------------------------------------------------------------------
TOTAL                                  889     42    128      5    94%
Coverage XML written to file coverage.xml


================================================================================= 117 passed in 25.14s ==================================================================================
```

## Running Linter

This repository utilizing `black` and `ruff` libraries to check and fix any formatting issues

```sh
# Example of Ruff with an error
$ poetry run ruff src/                
src/tests/test_check_functions.py:205:26: E712 [*] Comparison to `False` should be `cond is False`
Found 1 error.
[*] 1 potentially fixable with the --fix option.

# Example of black with reformatted line
$ poetry run black src/               
reformatted /Projects/regtech-data-validator/src/validator/main.py

All done! ✨ 🍰 ✨
1 file reformatted, 13 files left unchanged.
```

## (Optional) Using Dev Container and Visual Studio Code Development Setup

- These instructions will not work if using an alternative editor such as Vim or Emacs.
- To build, run, and attach the container to VS Code you'll need to have Docker installed on your system, and the `Dev Containers` extension installed within VS Code.
- Open this repository within VS Code and press `COMMAND + SHIFT + p` on your keyboard. This will open the command bar at the top of your window.
- Enter `Dev Containers: Rebuild and Reopen in Container`. VS Code will open a new window and you'll see a status message towards the bottom right of your screen that the container is building and attaching.
- This will take a few minutes the first time because Docker needs to build the container without a build cache.
- You may receive a notification that VS Code wants to perform a reload because some extensions could not load. Sometimes this happens because extensions are loaded in conflicting orders and dependencies are not satisfied.
- If using VS Code, validator can be executed by running `main.py` within a Dev Container. To run `main.py`, you can run these commands in VSCode terminal.

```sh
# Test validating the "good" file
# If passing lei value, pass lei as first arg and csv_path as second arg
python src/validator/main.py 000TESTFIUIDDONOTUSE src/tests/data/sbl-validations-pass.csv
# else just pass the csv_path as arg
python src/validator/main.py src/tests/data/sbl-validations-pass.csv

# Test validating the "bad" file
python src/validator/main.py 000TESTFIUIDDONOTUSE src/tests/data/sbl-validations-fail.csv
# or
python src/validator/main.py src/tests/data/sbl-validations-fail.csv
```

## Code Coverage

[![Coverage badge](https://github.com/cfpb/regtech-data-validator/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/cfpb/regtech-data-validator/tree/python-coverage-comment-action-data)
Complete coverage details can be found under [`python-coverage-comment-action-data` branch](https://github.com/cfpb/regtech-data-validator/tree/python-coverage-comment-action-data)

## Contributing

[CFPB](https://www.consumerfinance.gov/) is developing the `RegTech Data Validator` in the open to maximize transparency and encourage third party contributions. If you want to contribute, please read and abide by the terms of the [License](./LICENSE) for this project. Pull Requests are always welcome.

## Open source licensing info

1. [TERMS](./TERMS.md)
1. [LICENSE](./LICENSE)
1. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
