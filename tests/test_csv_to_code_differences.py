from regtech_data_validator.phase_validations import (
    get_phase_1_and_2_validations_for_lei,
    get_phase_2_register_validations,
)
from regtech_data_validator.validation_results import ValidationPhase
import pandas as pd


class TestCSVDifferences:

    def test_csv_differences(self):
        py_codes = get_phase_1_and_2_validations_for_lei()
        reg_code = get_phase_2_register_validations()
        py_validations = [
            {"validation_id": s.title, "type": s.severity, "description": s.description}
            for s in (
                [v[ValidationPhase.SYNTACTICAL] for v in py_codes.values()]
                + [v[ValidationPhase.LOGICAL] for v in py_codes.values()]
                + [v[ValidationPhase.LOGICAL] for v in reg_code.values()]
            )
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
