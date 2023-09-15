# Repository Coverage



| Name                                |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| src/tests/\_\_init\_\_.py           |        4 |        0 |        0 |        0 |    100% |           |
| src/tests/test\_check\_functions.py |      418 |        0 |        0 |        0 |    100% |           |
| src/tests/test\_checks.py           |       20 |        2 |       10 |        3 |     83% |9->exit, 16->exit, 24->exit, 25-26 |
| src/tests/test\_global\_data.py     |       19 |        0 |        4 |        0 |    100% |           |
| src/validator/\_\_init\_\_.py       |        4 |        0 |        0 |        0 |    100% |           |
| src/validator/check\_functions.py   |      184 |       36 |       78 |        2 |     79% |55-59, 111-121, 270-276, 290-299, 358, 412-422, 707 |
| src/validator/checks.py             |       14 |        1 |        4 |        0 |     94% |        73 |
| src/validator/create\_schemas.py    |       29 |       29 |        4 |        0 |      0% |      4-51 |
| src/validator/global\_data.py       |       18 |        0 |        4 |        0 |    100% |           |
| src/validator/main.py               |       38 |       38 |       10 |        0 |      0% |      8-66 |
| src/validator/phase\_validations.py |        6 |        6 |        0 |        0 |      0% |      7-38 |
| src/validator/schema\_template.py   |        6 |        6 |        0 |        0 |      0% |    12-452 |
|                           **TOTAL** |  **760** |  **118** |  **114** |    **5** | **82%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://github.com/cfpb/regtech-data-validator/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/cfpb/regtech-data-validator/tree/python-coverage-comment-action-data)

This is the one to use if your repository is private or if you don't want to customize anything.



## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.