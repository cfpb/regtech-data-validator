"""Create a Pandera SBLAR DataFrameSchema object.

Refer to the Pandera documentation for details. 
https://pandera.readthedocs.io/en/stable/dataframe_schemas.html

The only major modification from native Pandera is the use of custom
Check classes to differentiate between warnings and errors. """

from check_functions import (conditional_field_conflict, date_value_conflict,
                             denial_reasons_conditional_enum_value,
                             duplicates_in_field, enum_value_conflict,
                             invalid_date_format, invalid_date_value,
                             invalid_enum_value, invalid_number_of_values,
                             valid_numeric_format,
                             multi_invalid_number_of_values,
                             multi_value_field_restriction,
                             unreasonable_date_value)
from checks import SBLCheck
from pandera import Column, DataFrameSchema

sblar_schema = DataFrameSchema(
    {
        "uid": Column(
            str,
            title="Field 1: Unique identifier",
            checks=[],
        ),
        "app_date": Column(
            str,
            title="Field 2: Application date",
            checks=[],
        ),
        "app_method": Column(
            str,
            title="Field 3: Application method",
            checks=[],
        ),
        "app_recipient": Column(
            str,
            title="Field 4: Application recipient",
            checks=[
                SBLCheck(
                    invalid_enum_value,
                    name="app_recipient.invalid_enum_value",
                    description="'Application recipient' must equal 1 or 2",
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                    ],
                ),
            ],
        ),
        "ct_credit_product": Column(
            str,
            title="Field 5: Credit product",
            checks=[],
        ),
        "ct_credit_product_ff": Column(
            str,
            title="Field 6: Free-form text field for other credit products",
            checks=[],
        ),
        "ct_guarantee": Column(
            str,
            title="Field 7: Type of guarantee",
            checks=[
                SBLCheck(
                    invalid_number_of_values,
                    name="ct_guarantee.invalid_number_of_values",
                    description=(
                        "'Type of guarantee' must contain at least one and at"
                        " most five values, separated by semicolons."
                    ),
                    element_wise=True,
                    min_length=1,
                    max_length=5,
                ),
                SBLCheck(
                    duplicates_in_field,
                    warning=True,
                    name="ct_guarantee.duplicates_in_field",
                    description=(
                        "'Type of guarantee' should not contain " 
                        "duplicated values."
                    ),
                    element_wise=True,
                ),
                SBLCheck(
                    multi_value_field_restriction,
                    warning=True,
                    name="ct_guarantee.multi_value_field_restriction",
                    description=(
                        "When 'type of guarantee' contains 999 (no guarantee),"
                        " 'type of guarantee' should not contain more than one"
                        " value."
                    ),
                    element_wise=True,
                    single_values={"999"},
                ),
                SBLCheck(
                    invalid_enum_value,
                    name="ct_guarantee.invalid_enum_value",
                    description=(
                        "Each value in 'type of guarantee' (separated by "
                        " semicolons) must equal 1, 2, 3, 4, 5, 6, 7, 8,"
                        " 9, 10, 11, 977, or 999."
                    ),
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                        "10",
                        "11",
                        "977",
                        "999",
                    ],
                ),
            ],
        ),
        "ct_guarantee_ff": Column(
            str,
            title="Field 8: Free-form text field for other guarantee",
            checks=[
                SBLCheck.str_length(
                    0,
                    300,
                    name="ct_guarantee_ff.invalid_text_length",
                    description=(
                        "'Free-form text field for other guarantee' must not "
                        "exceed 300 characters in length"
                    ),
                ),
                SBLCheck(
                    conditional_field_conflict,
                    name="ct_guarantee_ff.conditional_field_conflict",
                    description=(
                        "When 'type of guarantee' does not contain 977 (other), "
                        "'free-form text field for other guarantee' must be blank. "
                        "When 'type of guarantee' contains 977, 'free-form text field"
                        " for other guarantee' must not be blank."
                    ),
                    groupby="ct_guarantee",
                    condition_values={"977"},
                ),
                SBLCheck(
                    multi_invalid_number_of_values,
                    warning=True,
                    name="ct_guarantee_ff.multi_invalid_number_of_values",
                    description=(
                        "'Type of guarantee' and 'free-form text field for other "
                        "guarantee' combined should not contain more than five values. "
                        "Code 977 (other), within 'type of guarantee', does not count "
                        "toward the maximum number of values for the purpose of this "
                        "validation check."
                    ),
                    groupby="ct_guarantee",
                    max_length=5,
                ),
            ],
        ),
        "ct_loan_term_flag": Column(
            str,
            title="Field 9: Loan term: NA/NP flag",
            checks=[
                SBLCheck(
                    invalid_enum_value,
                    name="ct_loan_term_flag.invalid_enum_value",
                    description=(
                        "Each value in 'Loan term: NA/NP flag' (separated by "
                        " semicolons) must equal 900, 988, or 999."
                    ),
                    element_wise=True,
                    accepted_values=[
                        "900",
                        "988",
                        "999",
                    ],
                ),
                SBLCheck(
                    enum_value_conflict,
                    name="ct_loan_term_flag.enum_value_conflict",
                    description=(
                        "When 'credit product' equals 1 (term loan - unsecured) or 2" 
                        "(term loan - secured), 'loan term: NA/NP flag' must not equal 999 "
                        "(not applicable)."
                        "When 'credit product' equals 988 (not provided by applicant "
                        "and otherwise undetermined), 'loan term: NA/NP flag' must equal 999."
                    ),
                    groupby="ct_credit_product",
                    condition_values1={"1", "2"},
                    condition_values2={"988"},
                    condition_value="999"
                ),

            ],
        ),
        "ct_loan_term": Column(
            str,
            title="Field 10: Loan term",
            checks=[
                SBLCheck(
                    conditional_field_conflict,
                    name="ct_loan_term.conditional_field_conflict",
                    description=(
                        "When 'loan term: NA/NP flag' does not equal 900 (applicable "
                        "and reported), 'loan term' must be blank. When 'loan term:"
                        "NA/NP flag' equals 900, 'loan term' must not be blank."
                    ),
                    groupby="ct_loan_term_flag",
                    condition_value="900",
                ),
                SBLCheck(
                    valid_numeric_format,
                    name="ct_loan_term.valid_numeric_format",
                    description="When present, 'loan term' must be a whole number.",
                    element_wise=True,
                ),
                SBLCheck.greater_than_or_equal_to(
                    min_value="1",
                    name="ct_loan_term.invalid_numeric_value",
                    description=(
                        "When present, 'loan term' must be greater than or equal"
                        "to 1."
                    ),
                ),
                SBLCheck.less_than(
                    max_value="1200",
                    name="ct_loan_term.unreasonable_numeric_value",
                    description=(
                        "When present, 'loan term' should be less than 1200"
                        "(100 years)."
                    ),
                ),
            ],
        ),
        "credit_purpose": Column(
            str,
            title="Field 11: Credit purpose",
            checks=[
                SBLCheck(
                    invalid_enum_value,
                    name="credit_purpose.invalid_enum_value",
                    description=(
                        "Each value in 'credit purpose' (separated by "
                        " semicolons) must equal 1, 2, 3, 4, 5, 6, 7, 8,"
                        " 9, 10, 11, 977, 988, or 999."
                    ),
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                        "10",
                        "11",
                        "977",
                        "988",
                        "999",
                    ],
                ),
                SBLCheck(
                    invalid_number_of_values,
                    name="credit_purpose.invalid_number_of_values",
                    description=(
                        "'Credit purpose' must contain at least one and at"
                        " most three values, separated by semicolons."
                    ),
                    element_wise=True,
                    min_length=1,
                    max_length=3,
                ),
                SBLCheck(
                    multi_value_field_restriction,
                    warning=True,
                    name="credit_purpose.multi_value_field_restriction",
                    description=(
                        "When 'credit purpose' contains 988 or 999,"
                        " 'credit purpose' should not contain more than one"
                        " value."
                    ),
                    element_wise=True,
                    single_values={
                        "988",
                        "999",
                    },
                ),
                SBLCheck(
                    duplicates_in_field,
                    warning=True,
                    name="credit_purpose.duplicates_in_field",
                    description=(
                        "'Credit purpose' should not contain "
                        " duplicated values."
                    ),
                    element_wise=True,
                ),
            ],
        ),
        "credit_purpose_ff": Column(
            str,
            title="Field 12: Free-form text field for other credit purpose",
            checks=[
                SBLCheck.str_length(
                    0,
                    300,
                    name="credit_purpose_ff.invalid_text_length",
                    description=(
                        "'Free-form text field for other credit purpose' "
                        " must not exceed 300 characters in length"
                    ),
                ),
                SBLCheck(
                    conditional_field_conflict,
                    name="credit_purpose_ff.conditional_field_conflict",
                    description=(
                        "When 'credit purpose' does not contain 977 (other), 'free-form text field for other credit purpose' "
                        " must be blank. When 'credit purpose' contains 977, 'free-form text field for other credit purpose' "
                        " must not be blank."
                    ),
                    groupby="credit_purpose",
                    condition_values={"977"},
                ),
                SBLCheck(
                    invalid_number_of_values,
                    name="credit_purpose_ff.invalid_number_of_values",
                    description=(
                        "'Other Credit purpose' must not contain more "
                        " than one other credit purpose."
                    ),
                    element_wise=True,
                    min_length=0,
                    max_length=1,
                ),
            ],
        ),
        "amount_applied_for_flag": Column(
            str,
            title="Field 13: Amount applied for: NA/NP flag",
            checks=[
                SBLCheck(
                    invalid_enum_value,
                    name="amount_applied_for_flag.invalid_enum_value",
                    description=(
                        "'Amount applied For: NA/NP flag' must equal 900, 988, or 999."
                    ),
                    element_wise=True,
                    accepted_values=[
                        "900",
                        "988",
                        "999",
                    ],
                ),

                ],
        ),
        "amount_applied_for": Column(
            str,
            title="Field 14: Amount applied for",
            checks=[
                SBLCheck(
                    conditional_field_conflict,
                    name="amount_applied_for.conditional_field_conflict",
                    description=(
                        "When 'amount applied for: NA/NP flag' does not equal 900 "
                        "(applicable and reported), 'amount applied for' must be blank."
                        "When 'amount applied for: NA/NP flag' equals 900, "
                        "'amount applied for' must not be blank."
                    ),
                    groupby="amount_applied_for_flag",
                    condition_values={"900"},
                ),
                SBLCheck(
                    valid_numeric_format,
                    name="amount_applied_for.valid_numeric_format",
                    description=(
                        "When present, 'amount applied for' must be a numeric"
                        "value."
                    ),
                    element_wise=True,
                ),
                SBLCheck.greater_than(
                    min_value="0",
                    name="amount_applied_for.invalid_numeric_value",
                    description=(
                        "When present, 'amount applied for' must be greater than 0."
                    ),
                ),

                ],
        ),
        "amount_approved": Column(
            str,
            title="Field 15: Amount approved or originated",
            checks=[
                    SBLCheck(
                        valid_numeric_format,
                        name="amount_approved.valid_numeric_format",
                        description=(
                            "When present, 'amount approved or originated' "
                            "must be a numeric value."
                        ),
                        element_wise=True,
                    ),
                    SBLCheck.greater_than(
                        min_value="0",
                        name="amount_approved.invalid_numeric_value",
                        description=(
                            "When present, 'amount approved or originated' "
                            "must be greater than 0."
                        ),
                    ),
                    SBLCheck(
                        conditional_field_conflict,
                        name="amount_approved.conditional_field_conflict",
                        description=(
                            "When 'action taken' does not equal 1 (originated) "
                            "or 2 (approved but not accepted), 'amount approved "
                            " or originated' must be blank. When 'action taken' "
                            "equals 1 or 2, 'amount approved or originated' must "
                            "not be blank."
                        ),
                        groupby="action_taken",
                        condition_values={"1", "2"},
                    ),
                ],
        ),
        "action_taken": Column(
            str,
            title="Field 16: Action taken",
            checks=[
                    SBLCheck(
                        invalid_enum_value,
                        name="action_taken.invalid_enum_value",
                        description="'Action taken' must equal 1, 2, 3, 4, or 5.",
                        element_wise=True,
                        accepted_values=[
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                        ],
                    ),
                ],
        ),
        "action_taken_date": Column(
            str,
            title="Field 17: Action taken date",
            checks=[
                SBLCheck(
                    invalid_date_format,
                    name="action_taken_date.invalid_date_format",
                    description=(
                        "'Action taken date' must be a real calendar"
                        " date using YYYYMMDD format."
                    ),
                    element_wise=True,
                ),
                SBLCheck(
                    invalid_date_value,
                    name="action_taken_date.invalid_date_value",
                    description=(
                        "The date indicated by 'action taken date' must occur"
                        " within the current reporting period:"
                        " October 1, 2024 to December 31, 2024."
                    ),
                    element_wise=True,
                    start_date_value="20241001",
                    end_date_value="20241231",
                ),
                SBLCheck(
                    date_value_conflict,
                    name="action_taken_date.date_value_conflict",
                    description=(
                        "The date indicated by ‘action taken date’"
                        " must occur on or after ‘application date’."
                    ),
                    groupby="app_date",
                ),
                SBLCheck(
                    unreasonable_date_value,
                    name="action_taken_date.unreasonable_date_value",
                    description=(
                        "The date indicated by ‘application date’ should"
                        " generally be less than two years (730 days) before"
                        " ‘action taken date’."
                    ),
                    groupby="app_date",
                    days_value=730,
                ),
            ],
        ),
        "denial_reasons": Column(
            str,
            title="Field 18: Denial reason(s)",
            checks=[
                SBLCheck(
                    invalid_enum_value,
                    name="denial_reasons.invalid_enum_value",
                    description=(
                        "Each value in 'denial reason(s)' (separated by semicolons)"
                        "must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 977, or 999."
                    ),
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                        "977",
                        "999",
                    ],
                ),
                SBLCheck(
                    invalid_number_of_values,
                    name="denial_reasons.invalid_number_of_values",
                    description=(
                        "'Denial reason(s)' must contain at least one and at most four"
                        "values, separated by semicolons."
                    ),
                    element_wise=True,
                    min_length=1,
                    max_length=4,
                ),
                SBLCheck(
                    denial_reasons_conditional_enum_value,
                    name="denial_reasons.enum_value_conflict",
                    description=(
                        "When 'action taken' equals 3, 'denial reason(s)' must not"
                        "contain 999. When 'action taken' does not equal 3, 'denial"
                        "reason(s)' must equal 999."
                    ),
                    groupby="action_taken",
                ),
                SBLCheck(
                    multi_value_field_restriction,
                    warning=True,
                    name="denial_reasons.multi_value_field_restriction",
                    description=(
                        "When 'denial reason(s)' contains 999 (not applicable),"
                        "'denial reason(s)' should not contain more than one value."
                    ),
                    element_wise=True,
                    single_values={"999"},
                ),
                SBLCheck(
                    duplicates_in_field,
                    warning=True,
                    name="denial_reasons.duplicates_in_field",
                    description=(
                        "'Denial reason(s)' should not contain " 
                        "duplicated values."
                    ),
                    element_wise=True,
                ),
            ],
        ),
        "denial_reasons_ff": Column(
            str,
            title="Field 19: Free-form text field for other denial reason(s)",
            checks=[
                SBLCheck.str_length(
                    min_value=0,
                    max_value=300,
                    name="denial_reasons_ff.invalid_text_length",
                    description=(
                        "'Free-form text field for other denial reason(s)'"
                        "must not exceed 300 characters in length."
                    ),
                ),
                SBLCheck(
                    conditional_field_conflict,
                    name="denial_reasons_ff.conditional_field_conflict",
                    description=(
                        "When 'denial reason(s)' does not contain 977 (other), field"
                        "'free-form text field for other denial reason(s)' must be"
                        "blank. When 'denial reason(s)' contains 977, 'free-form text"
                        "field for other denial reason(s)' must not be blank."
                    ),
                    groupby="denial_reasons",
                    condition_values={"977"},
                ),
            ],
        ),
        "pricing_interest_rate_type": Column(
            str,
            title="Field 20: Interest rate type",
            checks=[
                SBLCheck(
                    invalid_enum_value,
                    name="pricing_interest_rate_type.invalid_enum_value",
                    description=(
                        "Each value in 'Interest rate type' (separated by "
                        " semicolons) Must equal 1, 2, 3, 4, 5, 6, or 999"
                    ),
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "999",
                    ],
                ),
                
            ],
        ),
        "pricing_init_rate_period": Column(
            str,
            title="Field 21: Initial rate period",
            checks=[],
        ),
        "pricing_fixed_rate": Column(
            str,
            title="Field 22: Fixed rate: interest rate",
            checks=[
                SBLCheck(
                    valid_numeric_format,
                    name="pricing_fixed_rate.valid_numeric_format",
                    description=(
                        "When present, ‘fixed rate: interest rate’"
                        " must be a numeric value."
                    ),
                    element_wise=True,
                ),
                SBLCheck(
                    conditional_field_conflict,
                    name="pricing_fixed_rate.conditional_field_conflict",
                    description=(
                        "When 'interest rate type' does not equal 2"
                        " (fixed interest rate, no initial rate period),"
                        " 4 (initial rate period > 12 months, fixed interest"
                        " rate), or 6 (initial rate period <= 12 months, fixed"
                        " interest rate), 'fixed rate: interest rate' must be"
                        " blank. When 'interest rate type' equals 2, 4, or 6,"
                        " 'fixed rate: interest rate' must not be blank."
                    ),
                    groupby="pricing_interest_rate_type",
                    condition_values={"2", "4", "6"},
                ),
                SBLCheck.greater_than(
                    min_value="0.1",
                    name="pricing_fixed_rate.unreasonable_numeric_value",
                    description=(
                        "When present, ‘fixed rate: interest rate’"
                        " should generally be greater than 0.1."
                    ),
                ),
            ],
        ),
        "pricing_var_margin": Column(
            str,
            title="Field 23: Variable rate transaction: margin",
            checks=[
                SBLCheck(
                    valid_numeric_format,
                    name="pricing_var_margin.valid_numeric_format",
                    description=(
                        "When present, ‘variable rate transaction:"
                        " margin’ must be a numeric value."
                    ),
                    element_wise=True,
                ),
                SBLCheck(
                    conditional_field_conflict,
                    name="pricing_var_margin.conditional_field_conflict",
                    description=(
                        "When 'interest rate type' does not equal 1"
                        " (variable interest rate, no initial rate period),"
                        " 3 (initial rate period > 12 months, variable interest rate),"
                        " or 5 (initial rate period <= 12 months, variable interest rate),"
                        " 'variable rate transaction: margin' must be blank."
                        " When 'interest rate type' equals 1, 3, or 5, 'variable"
                        " rate transaction: margin' must not be blank."
                    ),
                    groupby="pricing_interest_rate_type",
                    condition_values={"1", "3", "5"},
                ),
                SBLCheck.greater_than(
                    min_value="0.1",
                    name="pricing_var_margin.unreasonable_numeric_value",
                    description=(
                        "When present, ‘variable rate transaction:"
                        " margin’ should generally be greater than 0.1."
                    ),
                ),
            ],
        ),
        "pricing_var_index_name": Column(
            str,
            title="Field 24: Variable rate transaction: index name",
            checks=[],
        ),
        "pricing_var_index_name_ff": Column(
            str,
            title="Field 25: Variable rate transaction: index name: other",
            checks=[],
        ),
        "pricing_var_index_value": Column(
            str,
            title="Field 26: Variable rate transaction: index value",
            checks=[],
        ),
        "pricing_origination_charges": Column(
            str,
            title="Field 27: Total origination charges",
            checks=[],
        ),
        "pricing_broker_fees": Column(
            str,
            title="Field 28: Amount of total broker fees",
            checks=[],
        ),
        "pricing_initial_charges": Column(
            str,
            title="Field 29: Initial annual charges",
            checks=[],
        ),
        "pricing_mca_addcost_flag": Column(
            str,
            title=(
                "Field 30: MCA/sales-based: additional cost for merchant cash "
                "advances or other sales-based financing: NA flag"
            ),
            checks=[],
        ),
        "pricing_mca_addcost": Column(
            str,
            title=(
                "Field 31: MCA/sales-based: additional cost for merchant cash ",
                "advances or other sales-based financing",
            ),
            checks=[],
        ),
        "pricing_prepenalty_allowed": Column(
            str,
            title="Field 32: Prepayment penalty could be imposed",
            checks=[],
        ),
        "pricing_prepenalty_exists": Column(
            str,
            title="Field 33: Prepayment penalty exists",
            checks=[],
        ),
        "census_tract_adr_type": Column(
            str,
            title="Field 34: Type of address",
            checks=[],
        ),
        "census_tract_number": Column(
            str,
            title="Field 35: Tract number",
            checks=[],
        ),
        "gross_annual_revenue_flag": Column(
            str,
            title="Field 36: Gross annual revenue: NP flag",
            checks=[],
        ),
        "gross_annual_revenue": Column(
            str,
            title="Field 37: Gross annual revenue",
            checks=[],
        ),
        "naics_code_flag": Column(
            str,
            title=(
                "Field 38: North American Industry Classification System (NAICS)"
                "code: NP flag"
            ),
            checks=[],
        ),
        "naics_code": Column(
            str,
            title=(
                "Field 39: North American Industry Classification" "System (NAICS) code"
            ),
            checks=[],
        ),
        "number_of_workers": Column(
            str,
            title="Field 40: Number of workers",
            checks=[],
        ),
        "time_in_business_type": Column(
            str,
            title="Field 41: Type of response",
            checks=[],
        ),
        "time_in_business": Column(
            str,
            title="Field 42: Time in business",
            checks=[],
        ),
        "business_ownership_status": Column(
            str,
            title="Field 43: Business ownership status",
            checks=[],
        ),
        "num_principal_owners_flag": Column(
            str,
            title="Field 44: Number of principal owners: NP flag",
            checks=[],
        ),
        "num_principal_owners": Column(
            str,
            title="Field 45: Number of principal owners",
            checks=[],
        ),
        "po_1_ethnicity": Column(
            str,
            title="Field 46: Ethnicity of principal owner 1",
            checks=[],
        ),
        "po_1_ethnicity_ff": Column(
            str,
            title=(
                "Field 47: Ethnicity of principal owner 1: free-form text field for"
                "other Hispanic or Latino ethnicity"
            ),
            checks=[],
        ),
        "po_1_race": Column(
            str,
            title="Field 48: Race of principal owner 1",
            checks=[],
        ),
        "po_1_race_anai_ff": Column(
            str,
            title=(
                "Field 49: Race of principal owner 1: free-form text field for"
                "American Indian or Alaska Native Enrolled or Principal Tribe"
            ),
            checks=[],
        ),
        "po_1_race_asian_ff": Column(
            str,
            title=(
                "Field 50: Race of principal owner 1: free-form text field for other"
                "Asian race"
            ),
            checks=[],
        ),
        "po_1_race_baa_ff": Column(
            str,
            title=(
                "Field 51: Race of principal owner 1: free-form text field for other"
                "Black or African American race"
            ),
            checks=[],
        ),
        "po_1_race_pi_ff": Column(
            str,
            title=(
                "Field 52: Race of principal owner 1: free-form text field for other"
                "Pacific Islander race"
            ),
            checks=[],
        ),
        "po_1_gender_flag": Column(
            str,
            title="Field 53: Sex/gender of principal owner 1: NP flag",
            checks=[],
        ),
        "po_1_gender_ff": Column(
            str,
            title=(
                "Field 54: Sex/gender of principal owner 1: free-form text field for"
                "self-identified sex/gender"
            ),
            checks=[],
        ),
        "po_2_ethnicity": Column(
            str,
            title="Field 55: Ethnicity of principal owner 2",
            checks=[],
        ),
        "po_2_ethnicity_ff": Column(
            str,
            title=(
                "Field 56: Ethnicity of principal owner 2: free-form text field for"
                "other Hispanic or Latino ethnicity"
            ),
            checks=[],
        ),
        "po_2_race": Column(
            str,
            title="Field 57: Race of principal owner 2",
            checks=[],
        ),
        "po_2_race_anai_ff": Column(
            str,
            title=(
                "Field 58: Race of principal owner 2: free-form text field for"
                "American Indian or Alaska Native Enrolled or Principal Tribe"
            ),
            checks=[],
        ),
        "po_2_race_asian_ff": Column(
            str,
            title=(
                "Field 59: Race of principal owner 2: free-form text field for other"
                "Asian race"
            ),
            checks=[],
        ),
        "po_2_race_baa_ff": Column(
            str,
            title=(
                "Field 60: Race of principal owner 2: free-form text field for other"
                "Black or African American race"
            ),
            checks=[],
        ),
        "po_2_race_pi_ff": Column(
            str,
            title=(
                "Field 61: Race of principal owner 2: free-form text field for other"
                "Pacific Islander race"
            ),
            checks=[],
        ),
        "po_2_gender_flag": Column(
            str,
            title="Field 62: Sex/gender of principal owner 2: NP flag",
            checks=[],
        ),
        "po_2_gender_ff": Column(
            str,
            title=(
                "Field 63: Sex/gender of principal owner 2: free-form text field for"
                "self-identified sex/gender"
            ),
            checks=[],
        ),
        "po_3_ethnicity": Column(
            str,
            title="Field 64: Ethnicity of principal owner 3",
            checks=[],
        ),
        "po_3_ethnicity_ff": Column(
            str,
            title=(
                "Field 65: Ethnicity of principal owner 3: free-form text field for"
                "other Hispanic or Latino ethnicity"
            ),
            checks=[],
        ),
        "po_3_race": Column(
            str,
            title="Field 66: Race of principal owner 3",
            checks=[],
        ),
        "po_3_race_anai_ff": Column(
            str,
            title=(
                "Field 67: Race of principal owner 3: free-form text field for"
                "American Indian or Alaska Native Enrolled or Principal Tribe"
            ),
            checks=[],
        ),
        "po_3_race_asian_ff": Column(
            str,
            title=(
                "Field 68: Race of principal owner 3: free-form text field for other"
                "Asian race"
            ),
            checks=[],
        ),
        "po_3_race_baa_ff": Column(
            str,
            title=(
                "Field 69: Race of principal owner 3: free-form text field for other"
                "Black or African American race"
            ),
            checks=[],
        ),
        "po_3_race_pi_ff": Column(
            str,
            title=(
                "Field 70: Race of principal owner 3: free-form text field for other"
                "Pacific Islander race"
            ),
            checks=[],
        ),
        "po_3_gender_flag": Column(
            str,
            title="Field 71: Sex/gender of principal owner 3: NP flag",
            checks=[],
        ),
        "po_3_gender_ff": Column(
            str,
            title=(
                "Field 72: Sex/gender of principal owner 3: free-form text field for"
                "self-identified sex/gender"
            ),
            checks=[],
        ),
        "po_4_ethnicity": Column(
            str,
            title="Field 73: Ethnicity of principal owner 4",
            checks=[],
        ),
        "po_4_ethnicity_ff": Column(
            str,
            title=(
                "Field 74: Ethnicity of principal owner 4: free-form text field for"
                "other Hispanic or Latino ethnicity"
            ),
            checks=[],
        ),
        "po_4_race": Column(
            str,
            title="Field 75: Race of principal owner 4",
            checks=[],
        ),
        "po_4_race_anai_ff": Column(
            str,
            title=(
                "Field 76: Race of principal owner 4: free-form text field for"
                "American Indian or Alaska Native Enrolled or Principal Tribe"
            ),
            checks=[],
        ),
        "po_4_race_asian_ff": Column(
            str,
            title=(
                "Field 77: Race of principal owner 4: free-form text field for other"
                "Asian race"
            ),
            checks=[],
        ),
        "po_4_race_baa_ff": Column(
            str,
            title=(
                "Field 78: Race of principal owner 4: free-form text field for other"
                "Black or African American race"
            ),
            checks=[],
        ),
        "po_4_race_pi_ff": Column(
            str,
            title=(
                "Field 79: Race of principal owner 4: free-form text field for other"
                "Pacific Islander race"
            ),
            checks=[],
        ),
        "po_4_gender_flag": Column(
            str,
            title="Field 80: Sex/gender of principal owner 4: NP flag",
            checks=[],
        ),
        "po_4_gender_ff": Column(
            str,
            title=(
                "Field 81: Sex/gender of principal owner 4: free-form text field for"
                "self-identified sex/gender"
            ),
            checks=[],
        ),
    }
)
