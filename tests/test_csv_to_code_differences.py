import re
from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei
import pandas as pd


class TestCSVDifferences:
    remove_formatting_codes = ["E2014", "E2015"]
    add_starting_quote = [
        "E0460",
        "E0480",
        "E0740",
        "W0901",
        "W0941",
        "W1081",
        "W1121",
        "W1261",
        "W1301",
        "W1441",
        "W1481",
    ]

    # At some point this will probably need to be updated depending on what is decided
    # in regards to formatting on the client side certain error messages that are
    # more 'robust' than others.  This works for now.
    def remove_formatting(self, code_string, csv_string):
        re_csvstring = "".join(re.findall("[a-zA-Z0-9':()/-]", csv_string))
        re_codestring = "".join(re.findall("[a-zA-Z0-9':()/-]", code_string))
        return re_codestring, re_csvstring

    def test_csv_differences(self):
        py_codes = get_phase_1_and_2_validations_for_lei()
        py_validations = [
            {"validation_id": s.title, "type": s.severity, "description": s.description}
            for s in ([v["phase_1"] for v in py_codes.values()] + [v["phase_2"] for v in py_codes.values()])
            for s in s
        ]

        csv_df = pd.read_csv(
            "https://raw.githubusercontent.com/cfpb/sbl-content/main/fig-files/validation-spec/2024-validations.csv"
        )

        missing_ids_in_code = []
        discrepancy_ids = []
        with open("errors.csv", "w") as error_file:
            error_file.write(
                'validation_id,csv_validation_category,python_validation_category,csv_description,python_description\n'
            )
            for index, row in csv_df.iterrows():
                found_py_validation = next(
                    iter([o for o in py_validations if o["validation_id"] == row["validation_id"]])
                )
                if found_py_validation:
                    if row["validation_id"] in self.remove_formatting_codes:
                        re_codestring, re_csvstring = self.remove_formatting(
                            found_py_validation["validation_id"], row["validation_id"]
                        )
                        found_py_validation["description"] = re_codestring
                        row["description"] = re_csvstring
                    # Add a single quote to certain descriptions from the CSV.  This is because
                    # Excel will strip that first single quote off when saving to a CSV, as it uses
                    # a starting single quote to signify that the rest of the data is a string.
                    # This checks if the description we're checking is one of those, and if it doesn't
                    # already start with a single quote in the CSV just in case someone saves the doc differently
                    # than with Excel
                    if row["validation_id"] in self.add_starting_quote and not row["description"].startswith("'"):
                        row["description"] = "'" + row["description"]
                    if (
                        row["type"].lower() != found_py_validation["type"].lower()
                        or row["description"] != found_py_validation["description"]
                    ):
                        # This can be used locally to run a pytest and get a csv of discrepancies, which makes
                        # for easier correcting of code/csv.
                        error_file.write(
                            f'{row["validation_id"]},{row["type"].lower()},{found_py_validation["type"].lower()},\"{row["description"]}\",\"{found_py_validation["description"]}\"\n'
                        )
                        discrepancy_ids.append(row["validation_id"])
                else:
                    missing_ids_in_code.append(row["validation_id"])

        missing_ids_in_csv = [
            p["validation_id"] for p in py_validations if p["validation_id"] not in csv_df["validation_id"].values
        ]

        # Printing out the ids during the test just for ease of determining which error/warning codes failed.
        # The above csv can then be used to fix failures
        print(f"Discrepancy IDs: {discrepancy_ids}")
        print(f"Missing IDs in CSV: {missing_ids_in_csv}")
        print(f"Missing IDs in Python: {missing_ids_in_code}")

        assert len(discrepancy_ids) == 0
        assert len(missing_ids_in_csv) == 0
        assert len(missing_ids_in_code) == 0
