# An Alternative SBLAR Parser POC

This is a POC for a SBLAR file parser and validator which makes use of Pandera. You can read about Pandera schemas [here](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html).

## Dev Container Setup

The code in this repository is developed and run inside of a dev container within Visual Studio Code. These instructions will not work if using an alternative editor such as Vim or Emacs. To build, run, and attach the container to VS Code you'll need to have Docker installed on your system, and the `Dev Containers` extension installed within VS Code.

Open this repository within VS Code and press `COMMAND + SHIFT + p` on your keyboard. This will open the command bar at the top of your window. Enter `Dev Containers: Rebuild and Reopen in Container`. VS Code will open a new window and you'll see a status message towards the bottom right of your screen that the container is building and attaching. This will take a few minutes the first time because Docker needs to build the container without a build cache. You may receive a notification that VS Code wants to perform a reload because some extensions could not load. Sometimes this happens because extensions are loaded in conflicting orders and dependencies are not satisfied.

## Running the Demo

If using VS Code, setup is completed by simply running the code within a Dev Container. If you're not making use of VS Code, make your life easier and use VS Code :sunglasses:. See the instructions above for setting up the Dev Container.

There are 3 files that will be of interest. `schema.py` defines the Pandera schema used for validating the SBLAR data. A custom Pandera Check class called `NamedCheck` exists within this file as well. `check_functions.py` contains a collection of functions to be run against the data that are a bit too complex to be implemented directly within the schema as Lamba functions. Lastly, the file `main.py` pulls everything together and illustrates how the schema can catch the various validation errors present in our mock, invalid dataset.

## Test data

The repo includes 2 test datasets, one with all valid data, and one where each line
represents a different failed validation, or different permutation of of the same
failed validation.

- [`SBL_Validations_SampleData_GoodFile_03312023.csv`](SBL_Validations_SampleData_GoodFile_03312023.csv)
- [`SBL_Validations_SampleData_BadFile_03312023.csv`](SBL_Validations_SampleData_BadFile_03312023.csv)

For more details on these test files, see:

- https://github.cfpb.gov/reg-tech/sbl-data-collection/issues/330

### Usage

```sh
# Test validating the "good" file
python src/validator/main.py SBL_Validations_SampleData_GoodFile_03312023.csv

# Test validating the "bad" file
python src/validator/main.py SBL_Validations_SampleData_BadFile_03312023.csv
```

## Development / Writing Validations

* Check functions should focus on reuse.
  * Most of the validations share logic with other validations.
* Avoid using lambdas for Check functions.
  * They do not promote reuse.
  * They are harder to debug.
  * They are harder to test.
* Check function signatures should reflect the functionality.
* Check functions should have corresponding unit tests.
  * [Unit Test](/tests/test_check_functions.py)
* Check definitions' name should be set to validation ID.
  * Example: "denial_reasons. enum_value_conflict"
  * ![Validation ID](validation_id.png)
