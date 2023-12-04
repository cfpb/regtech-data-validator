from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei
import pandas as pd


class TestCSVDifferences:
    def test_csv_differences(self):
        vals = get_phase_1_and_2_validations_for_lei()
        code_descs = [
            (s.title, s.severity, s.description)
            for s in [x for l in [v['phase_1'] for v in vals.values()] for x in l]
            + [x for l in [v['phase_2'] for v in vals.values()] for x in l]
        ]

        csv_df = pd.read_csv(
            'https://raw.githubusercontent.com/cfpb/sbl-content/main/fig-files/validation-spec/2024-validations.csv'
        )
        csv_descs = list(zip(csv_df.validation_id, csv_df.type, csv_df.description))

        wrong_ids = []

        with open('errors.csv', 'w') as error_file:
            for c in code_descs:
                found_cd = [d for d in csv_descs if d[0] == c[0]]
                if len(found_cd) == 0 or found_cd[0][1].lower() != c[1].lower() or found_cd[0][2] != c[2]:
                    # This can be used locally to run a pytest and get a csv of discrepancies, which makes for easier
                    # correcting of code/csv.
                    error_file.write(
                        f'{c[0]},\"{c[1]}\",\"{found_cd[0][1] if (len(found_cd) != 0) else None}\",\"{c[2]}\",\"{found_cd[0][2] if (len(found_cd) != 0) else None}\"\n'
                    )
                    wrong_ids.append(c)

        bad_ids = [i[0] for i in wrong_ids]
        if len(bad_ids) != 0:
            print(f'Bad IDs in Code: {bad_ids}')
            print(f'Total Bad IDs: {len(bad_ids)}')

        missing_ids = [i for i in [x[0] for x in csv_descs] if i not in [y[0] for y in code_descs]]
        if len(missing_ids) != 0:
            print(f'Missing IDs in CSV: {missing_ids}')
            print(f'Total Missing IDs: {len(missing_ids)}')

        assert len(bad_ids) == 0
        assert len(missing_ids) == 0
