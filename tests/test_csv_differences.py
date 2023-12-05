import re
from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei
import pandas as pd


class TestCSVDifferences:
    remove_formatting_codes = ["E2014", "E2015"]

    # At some point this will probably need to be updated depending on what is decided
    # in regards to formatting on the client side certain error messages that are
    # more 'robust' than others.  This works for now.
    def remove_formatting(self, code_string, csv_string):
        re_csvstring = "".join(re.findall("[a-zA-Z0-9':()/-]", csv_string))
        re_codestring = "".join(re.findall("[a-zA-Z0-9':()/-]", code_string))
        return re_codestring, re_csvstring

    def test_csv_differences(self):
        vals = get_phase_1_and_2_validations_for_lei()
        code_descs = [
            [s.title, s.severity, s.description]
            for s in ([v["phase_1"] for v in vals.values()] + [v["phase_2"] for v in vals.values()])
            for s in s
        ]

        csv_df = pd.read_csv(
            "https://raw.githubusercontent.com/cfpb/sbl-content/main/fig-files/validation-spec/2024-validations.csv"
        )
        csv_descs = list(zip(csv_df.validation_id, csv_df.type, csv_df.description))

        wrong_ids = []

        with open("errors.csv", "w") as error_file:
            for c in code_descs:
                found_cd = [d for d in csv_descs if d[0] == c[0]]
                if c[0] in self.remove_formatting_codes and len(found_cd) != 0:
                    re_codestring, re_csvstring = self.remove_formatting(c[2], found_cd[0][2])
                    c[2] = re_codestring
                    found_cd[0] = list(found_cd[0])
                    found_cd[0][2] = re_csvstring
                if len(found_cd) == 0 or found_cd[0][1].lower() != c[1].lower() or found_cd[0][2] != c[2]:
                    # This can be used locally to run a pytest and get a csv of discrepancies, which makes for easier
                    # correcting of code/csv.
                    error_file.write(
                        f'{c[0]},"{c[1]}","{found_cd[0][1] if (len(found_cd) != 0) else None}","{c[2]}","{found_cd[0][2] if (len(found_cd) != 0) else None}"\n'
                    )
                    wrong_ids.append(c)

        # Printing out the ids during the test just for ease of determining which error/warning codes failed.
        # The above csv can then be used to fix failures
        bad_ids = [i[0] for i in wrong_ids]
        if len(bad_ids) != 0:
            print(f"Bad IDs in Code: {bad_ids}")
            print(f"Total Bad IDs: {len(bad_ids)}")

        # Pull out codes that are in the csv but not in the python code
        missing_ids = [i for i in [x[0] for x in csv_descs] if i not in [y[0] for y in code_descs]]
        if len(missing_ids) != 0:
            print(f"Missing IDs in CSV: {missing_ids}")
            print(f"Total Missing IDs: {len(missing_ids)}")

        assert len(bad_ids) == 0
        assert len(missing_ids) == 0
