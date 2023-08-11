"""
This script loads a given CSV into a Pandas DataFrame, and then validates it against
the SBL Pandera schema.

Run from the terminal to see the generated output.
"""

import json
import sys

import pandas as pd
from checks import SBLCheck
from pandera.errors import SchemaErrors
from schema import sblar_schema


def csv_to_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, na_filter=False)


def run_validation_on_df(df: pd.DataFrame) -> list[dict]:
    """
    Run validaition on the supplied dataframe and print a report to
    the terminal.
    """

    findings = []

    try:
        sblar_schema(df, lazy=True)
    except SchemaErrors as errors:           
        for schema_error in errors.schema_errors:
            error = schema_error["error"]
            check: SBLCheck = error.check
            column_name = error.schema.name

            fields: list[str] = [column_name]
            if check.groupby:
                fields += check.groupby # type: ignore

            # Remove duplicates, but keep as `list` for JSON-friendliness
            fields = list(set(fields))

            # built in checks such as unique=True are different than custom
            # checks unfortunately so the name needs to be accessed differently
            # FIXME: There's gotta be a better way than try/except to
            #        handle different check fail types/states
            try:
                check_name: str = check.name
                # This will either be a boolean series or a single bool
                check_output = error.check_output
            except AttributeError:
                # FIXME: What type is this?
                check_name: str = check # type: ignore
                
                # this is just a string that we'd need to parse manually
                # FIXME: This is str, not pd.Series
                check_output = error.args[0]

            if check_output is not None:
                # `check_output` must be sorted so its index lines up with `df`'s index
                check_output.sort_index(inplace=True)

                #print(check_output)

                # Filter records using Pandas's boolean indexing, where all False values
                # get filtered out. The `~` does the inverse since it's actually the
                # False values we want to keep.
                # http://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#boolean-indexing
                failed_check_fields_df = df[~check_output][fields].fillna("")

                #print(failed_check_fields_df)

                # Create list of dicts representing the failed validations and the
                # associated field data for each invalid record.
                records = []
                for idx, row in failed_check_fields_df.iterrows():
                    record = {"number": idx + 1, "field_values": {}}
                    for field in fields:
                        record["field_values"][field] = row[field]
                    records.append(record)

                validation_findings = {
                    "validation": {
                        "id": check_name,
                        "description": check.description,
                        "fields": fields,
                        "severity": "warning" if check.warning else "error",
                    },
                    "records": records,
                }

                findings.append(validation_findings)

    return findings

if __name__ == "__main__":
    csv_path = None
    try:
        csv_path = sys.argv[1]
    except IndexError:
        raise ValueError("csv_path arg not provided")
    
    print("Data load starting...")
    df = csv_to_df(csv_path)
    print("Data load complete")

    print("Data validation starting...")
    findings = run_validation_on_df(df)
    print("Data validation complete")

    if findings:
        findings_json = json.dumps(findings, indent=4)

        print(findings_json)

        validation_count = len(findings)
        findings_count = sum([len(f["records"]) for f in findings])

        print(f"{findings_count} total findings on {validation_count} validations")
        
    else:
        print("No validations errors or warnings")