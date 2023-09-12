# Repository Coverage



| Name                                |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| src/tests/\_\_init\_\_.py           |        4 |        0 |        0 |        0 |    100% |           |
| src/tests/test\_check\_functions.py |      418 |        0 |        0 |        0 |    100% |           |
| src/tests/test\_checks.py           |       20 |        2 |       10 |        3 |     83% |9->exit, 16->exit, 24->exit, 25-26 |
| src/validator/\_\_init\_\_.py       |        4 |        0 |        0 |        0 |    100% |           |
| src/validator/check\_functions.py   |      184 |       36 |       78 |        2 |     79% |55-59, 113-123, 288-294, 308-321, 382, 440-454, 748 |
| src/validator/checks.py             |       14 |        1 |        4 |        0 |     94% |        75 |
| src/validator/create\_schemas.py    |       29 |       29 |        4 |        0 |      0% |      4-54 |
| src/validator/global\_data.py       |       18 |        4 |        4 |        0 |     73% |     35-38 |
| src/validator/main.py               |       38 |       38 |       10 |        0 |      0% |      8-66 |
| src/validator/phase\_validations.py |        6 |        6 |        0 |        0 |      0% |      7-38 |
| src/validator/schema\_template.py   |        6 |        6 |        0 |        0 |      0% |    12-517 |
|                           **TOTAL** |  **741** |  **122** |  **110** |    **5** | **81%** |           |


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