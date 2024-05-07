# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cfpb/regtech-data-validator/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                               |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/regtech\_data\_validator/check\_functions.py   |      188 |       14 |       82 |        0 |     91% |63-67, 119-129, 283-284, 305-306, 428-429 |
| src/regtech\_data\_validator/checks.py             |       17 |        0 |        2 |        0 |    100% |           |
| src/regtech\_data\_validator/cli.py                |       60 |        5 |       22 |        2 |     91% |87-88, 109-110, 119 |
| src/regtech\_data\_validator/create\_schemas.py    |       81 |        3 |       18 |        3 |     94% |140, 145, 165 |
| src/regtech\_data\_validator/data\_formatters.py   |       61 |        1 |       26 |        4 |     94% |109->156, 128->132, 146->148, 152 |
| src/regtech\_data\_validator/global\_data.py       |       13 |        0 |        8 |        0 |    100% |           |
| src/regtech\_data\_validator/phase\_validations.py |        7 |        0 |        0 |        0 |    100% |           |
| src/regtech\_data\_validator/schema\_template.py   |        6 |        0 |        0 |        0 |    100% |           |
|                                          **TOTAL** |  **433** |   **23** |  **158** |    **9** | **93%** |           |

3 empty files skipped.


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/cfpb/regtech-data-validator/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/cfpb/regtech-data-validator/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cfpb/regtech-data-validator/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/cfpb/regtech-data-validator/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fcfpb%2Fregtech-data-validator%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/cfpb/regtech-data-validator/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.