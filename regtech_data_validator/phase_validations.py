"""This is a mapping of column names and validations for each phase.

This mapping is used to populate the schema template object and create
an instance of a PanderaSchema object for phase 1 and phase 2."""

from regtech_data_validator import global_data
from regtech_data_validator.check_functions import (
    has_correct_length,
    has_no_conditional_field_conflict,
    has_valid_enum_pair,
    has_valid_fieldset_pair,
    has_valid_format,
    has_valid_multi_field_value_count,
    has_valid_value_count,
    is_date,
    is_date_after,
    is_date_before_in_days,
    is_date_in_range,
    is_greater_than,
    is_greater_than_or_equal_to,
    is_less_than,
    is_number,
    is_unique_column,
    is_unique_in_field,
    is_valid_code,
    is_valid_enum,
    meets_multi_value_field_restriction,
    string_contains,
)
from regtech_data_validator.checks import SBLCheck, Severity


def get_phase_1_and_2_validations_for_lei(context: dict[str, str] | None = None):
    lei: str | None = context.get('lei', None) if context else None

    return {
        "uid": {
            "phase_1": [
                SBLCheck(
                    is_unique_column,
                    id="E3000",
                    name="uid.duplicates_in_dataset",
                    description=(
                        "Any 'unique identifier' may not be used in more than one "
                        "record within a small business lending application register."
                    ),
                    severity=Severity.ERROR,
                    groupby="uid",
                ),
                SBLCheck.str_length(
                    21,
                    45,
                    id="E0001",
                    name="uid.invalid_text_length",
                    description=(
                        "'Unique identifier' must be at least 21 characters "
                        "in length and at most 45 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
                SBLCheck(
                    has_valid_format,
                    id="E0002",
                    name="uid.invalid_text_pattern",
                    description=(
                        "'Unique identifier' may contain any combination of "
                        "numbers and/or uppercase letters (i.e., 0-9 and A-Z), "
                        "and must not contain any other characters."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    regex="^[A-Z0-9]+$",
                ),
            ],
            "phase_2": [
                SBLCheck(
                    string_contains,
                    id="W0003",
                    name="uid.invalid_uid_lei",
                    description=(
                        "The first 20 characters of the 'unique identifier' should"
                        " match the Legal Entity Identifier (LEI) for the financial"
                        " institution."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    containing_value=lei,
                    end_idx=20,
                ),
            ],
        },
        "app_date": {
            "phase_1": [
                SBLCheck(
                    is_date,
                    id="E0020",
                    name="app_date.invalid_date_format",
                    description="'Application date' must be a real calendar date using YYYYMMDD format.",
                    severity=Severity.ERROR,
                    element_wise=True,
                ),
            ],
            "phase_2": [],
        },
        "app_method": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0040",
                    name="app_method.invalid_enum_value",
                    description="'Application method' must equal 1, 2, 3, or 4.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "4",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "app_recipient": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0060",
                    name="app_recipient.invalid_enum_value",
                    description="'Application recipient' must equal 1 or 2.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "ct_credit_product": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0080",
                    name="ct_credit_product.invalid_enum_value",
                    description="'Credit product' must equal 1, 2, 3, 4, 5, 6, 7, 8, 977, or 988.",
                    severity=Severity.ERROR,
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
                        "977",
                        "988",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "ct_credit_product_ff": {
            "phase_1": [
                # FIXME: built-in Pandera checks do not support add'l params like `severity`
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0100",
                    name="ct_credit_product_ff.invalid_text_length",
                    description=(
                        "'Free-form text field for other credit products' must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                )
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2000",
                    name="ct_credit_product_ff.conditional_field_conflict",
                    description=(
                        "When 'credit product' does not equal 977 (other), 'free-form"
                        " text field for other credit products' must be blank."
                        " When 'credit product' equals 977, 'free-form text field "
                        "for other credit products' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="ct_credit_product",
                    condition_values={"977"},
                ),
            ],
        },
        "ct_guarantee": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0120",
                    name="ct_guarantee.invalid_enum_value",
                    description=(
                        "Each value in 'type of guarantee' (separated by"
                        " semicolons) must equal 1, 2, 3, 4, 5, 6, 7, 8,"
                        " 9, 10, 11, 977, or 999."
                    ),
                    severity=Severity.ERROR,
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
            "phase_2": [
                SBLCheck(
                    has_valid_value_count,
                    id="E0121",
                    name="ct_guarantee.invalid_number_of_values",
                    description=(
                        "'Type of guarantee' must contain at least one and at"
                        " most five values, separated by semicolons."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    min_length=1,
                    max_length=5,
                ),
                SBLCheck(
                    is_unique_in_field,
                    id="W0123",
                    name="ct_guarantee.duplicates_in_field",
                    description="'Type of guarantee' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0122",
                    name="ct_guarantee.multi_value_field_restriction",
                    description=(
                        "When 'type of guarantee' contains 999 (no guarantee),"
                        " 'type of guarantee' should not contain more than one"
                        " value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"999"},
                ),
            ],
        },
        "ct_guarantee_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0140",
                    name="ct_guarantee_ff.invalid_text_length",
                    description="'Free-form text field for other guarantee' must not exceed 300 characters in length.",
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2001",
                    name="ct_guarantee_ff.conditional_field_conflict",
                    description=(
                        "When 'type of guarantee' does not contain 977 (other), "
                        "'free-form text field for other guarantee' must be blank. "
                        "When 'type of guarantee' contains 977, 'free-form text field"
                        " for other guarantee' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="ct_guarantee",
                    condition_values={"977"},
                ),
                SBLCheck(
                    has_valid_multi_field_value_count,
                    id="W2002",
                    name="ct_guarantee_ff.multi_invalid_number_of_values",
                    description=(
                        "'Type of guarantee' and 'free-form text field for other "
                        "guarantee' combined should not contain more than five values. "
                        "Code 977 (other), within 'type of guarantee', does not count "
                        "toward the maximum number of values for the purpose of this "
                        "validation check."
                    ),
                    severity=Severity.WARNING,
                    groupby="ct_guarantee",
                    ignored_values={"977"},
                    max_length=5,
                ),
            ],
        },
        "ct_loan_term_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0160",
                    name="ct_loan_term_flag.invalid_enum_value",
                    description="'Loan term: NA/NP flag' must equal 900, 988, or 999.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "900",
                        "988",
                        "999",
                    ],
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2003",
                    name="ct_loan_term_flag.enum_value_conflict",
                    description=(
                        "When 'credit product' equals 1 (term loan - unsecured) or 2"
                        " (term loan - secured), 'loan term: NA/NP flag' must not equal"
                        " 999 (not applicable)."
                        " When 'credit product' equals 988 (not provided by applicant"
                        " and otherwise undetermined), 'loan term: NA/NP flag' must"
                        " equal 999."
                    ),
                    severity=Severity.ERROR,
                    groupby="ct_credit_product",
                    conditions=[
                        {
                            "condition_values": {"1", "2"},
                            "is_equal_condition": True,
                            "target_value": "999",
                            "should_equal_target": False,
                        },
                        {
                            "condition_values": {"988"},
                            "is_equal_condition": True,
                            "target_value": "999",
                            "should_equal_target": True,
                        },
                    ],
                ),
            ],
        },
        "ct_loan_term": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0180",
                    name="ct_loan_term.invalid_numeric_format",
                    description="When present, 'loan term' must be a whole number.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2004",
                    name="ct_loan_term.conditional_field_conflict",
                    description=(
                        "When 'loan term: NA/NP flag' does not equal 900 (applicable "
                        "and reported), 'loan term' must be blank. When 'loan term: "
                        "NA/NP flag' equals 900, 'loan term' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="ct_loan_term_flag",
                    condition_values={"900"},
                ),
                SBLCheck(
                    is_greater_than_or_equal_to,
                    id="E0181",
                    name="ct_loan_term.invalid_numeric_value",
                    description="When present, 'loan term' must be greater than or equal to 1.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    min_value="1",
                    accept_blank=True,
                ),
                SBLCheck(
                    is_less_than,
                    id="W0182",
                    name="ct_loan_term.unreasonable_numeric_value",
                    description="When present, 'loan term' should be less than 1200 (100 years).",
                    severity=Severity.WARNING,
                    element_wise=True,
                    max_value="1200",
                    accept_blank=True,
                ),
            ],
        },
        "credit_purpose": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0200",
                    name="credit_purpose.invalid_enum_value",
                    description=(
                        "Each value in 'credit purpose' (separated by"
                        " semicolons) must equal 1, 2, 3, 4, 5, 6, 7, 8,"
                        " 9, 10, 11, 977, 988, or 999."
                    ),
                    severity=Severity.ERROR,
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
            ],
            "phase_2": [
                SBLCheck(
                    has_valid_value_count,
                    id="E0201",
                    name="credit_purpose.invalid_number_of_values",
                    description=(
                        "'Credit purpose' must contain at least one and at most three values, separated by semicolons."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    min_length=1,
                    max_length=3,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0202",
                    name="credit_purpose.multi_value_field_restriction",
                    description=(
                        "When 'credit purpose' contains 988 (not provided by applicant and otherwise undetermined) "
                        "or 999 (not applicable), "
                        "'credit purpose' should not contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={
                        "988",
                        "999",
                    },
                ),
                SBLCheck(
                    is_unique_in_field,
                    id="W0203",
                    name="credit_purpose.duplicates_in_field",
                    description="'Credit purpose' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
            ],
        },
        "credit_purpose_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0220",
                    name="credit_purpose_ff.invalid_text_length",
                    description=(
                        "'Free-form text field for other credit purpose' must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2005",
                    name="credit_purpose_ff.conditional_field_conflict",
                    description=(
                        "When 'credit purpose' does not contain 977 (other), "
                        "'free-form text field for other credit purpose' must be blank. "
                        "When 'credit purpose' contains 977 (other), 'free-form text field for "
                        "other credit purpose' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="credit_purpose",
                    condition_values={"977"},
                ),
                SBLCheck(
                    has_valid_multi_field_value_count,
                    id="W2006",
                    name="credit_purpose_ff.multi_invalid_number_of_values",
                    description=(
                        "'Credit purpose' and 'free-form text field for other credit "
                        "purpose' combined should not contain more than three values. "
                        "Code 977 (other), within 'credit purpose', does not count "
                        "toward the maximum number of values for the purpose of "
                        "this validation check."
                    ),
                    severity=Severity.WARNING,
                    groupby="credit_purpose",
                    ignored_values={"977"},
                    max_length=3,
                ),
            ],
        },
        "amount_applied_for_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0240",
                    name="amount_applied_for_flag.invalid_enum_value",
                    description="'Amount applied For: NA/NP flag' must equal 900, 988, or 999.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "900",
                        "988",
                        "999",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "amount_applied_for": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0260",
                    name="amount_applied_for.invalid_numeric_format",
                    description="When present, 'amount applied for' must be a numeric value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2007",
                    name="amount_applied_for.conditional_field_conflict",
                    description=(
                        "When 'amount applied for: NA/NP flag' does not equal 900 "
                        "(applicable and reported), 'amount applied for' must be blank. "
                        "When 'amount applied for: NA/NP flag' equals 900, "
                        "'amount applied for' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="amount_applied_for_flag",
                    condition_values={"900"},
                ),
                SBLCheck(
                    is_greater_than,
                    id="E0261",
                    name="amount_applied_for.invalid_numeric_value",
                    description="When present, 'amount applied for' must be greater than 0.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    min_value="0",
                    accept_blank=True,
                ),
            ],
        },
        "amount_approved": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0280",
                    name="amount_approved.invalid_numeric_format",
                    description="When present, 'amount approved or originated' must be a numeric value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_greater_than,
                    id="E0281",
                    name="amount_approved.invalid_numeric_value",
                    description="When present, 'amount approved or originated' must be greater than 0.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    min_value="0",
                    accept_blank=True,
                ),
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2008",
                    name="amount_approved.conditional_field_conflict",
                    description=(
                        "When 'action taken' does not equal 1 (originated) "
                        "or 2 (approved but not accepted), 'amount approved "
                        "or originated' must be blank. When 'action taken' "
                        "equals 1 or 2, 'amount approved or originated' must "
                        "not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="action_taken",
                    condition_values={"1", "2"},
                ),
            ],
        },
        "action_taken": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0300",
                    name="action_taken.invalid_enum_value",
                    description="'Action taken' must equal 1, 2, 3, 4, or 5.",
                    severity=Severity.ERROR,
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
            "phase_2": [
                SBLCheck(
                    has_valid_fieldset_pair,
                    id="E2014",
                    name="pricing_all.conditional_fieldset_conflict",
                    description=(
                        "When 'action taken' equals 3 (denied), "
                        "4 (withdrawn by applicant), or 5 "
                        "(incomplete), the following fields must"
                        " all equal 999 (not applicable): "
                        "'Interest rate type', 'MCA/sales-based: "
                        "additional cost for merchant cash advances"
                        " or other sales-based financing: NA flag', "
                        "'Prepayment penalty could be imposed', "
                        "'Prepayment penalty exists'). And the "
                        " following fields must all be blank: "
                        "'Total origination charges', 'Amount of "
                        "total broker fees', 'Initial annual charges'"
                    ),
                    severity=Severity.ERROR,
                    groupby=[
                        "pricing_interest_rate_type",
                        "pricing_mca_addcost_flag",
                        "pricing_prepenalty_allowed",
                        "pricing_prepenalty_exists",
                        "pricing_origination_charges",
                        "pricing_broker_fees",
                        "pricing_initial_charges",
                    ],
                    condition_values=["3", "4", "5"],
                    should_fieldset_key_equal_to={
                        "pricing_interest_rate_type": (0, True, "999"),
                        "pricing_mca_addcost_flag": (1, True, "999"),
                        "pricing_prepenalty_allowed": (2, True, "999"),
                        "pricing_prepenalty_exists": (3, True, "999"),
                        "pricing_origination_charges": (4, True, ""),
                        "pricing_broker_fees": (5, True, ""),
                        "pricing_initial_charges": (6, True, ""),
                    },
                ),
                SBLCheck(
                    has_valid_fieldset_pair,
                    id="E2015",
                    name="pricing_charges.conditional_fieldset_conflict",
                    description=(
                        "When 'action taken' equals 1 (originated)"
                        " or 2 (approved but not accepted), the "
                        "following fields all must not be blank: "
                        "'Total origination charges', 'Amount of "
                        "total broker fees', 'Initial annual "
                        "charges'. And the following fields must "
                        "not equal 999 (not applicable): 'Prepayment "
                        "penalty could be imposed', 'Prepayment "
                        "penalty exists'"
                    ),
                    severity=Severity.ERROR,
                    groupby=[
                        "pricing_origination_charges",
                        "pricing_broker_fees",
                        "pricing_initial_charges",
                        "pricing_prepenalty_allowed",
                        "pricing_prepenalty_exists",
                    ],
                    condition_values=["1", "2"],
                    should_fieldset_key_equal_to={
                        "pricing_origination_charges": (0, False, ""),
                        "pricing_broker_fees": (1, False, ""),
                        "pricing_initial_charges": (2, False, ""),
                        "pricing_prepenalty_allowed": (3, False, "999"),
                        "pricing_prepenalty_exists": (4, False, "999"),
                    },
                ),
            ],
        },
        "action_taken_date": {
            "phase_1": [
                SBLCheck(
                    is_date,
                    id="E0320",
                    name="action_taken_date.invalid_date_format",
                    description="'Action taken date' must be a real calendar date using YYYYMMDD format.",
                    severity=Severity.ERROR,
                    element_wise=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_date_in_range,
                    id="E0321",
                    name="action_taken_date.invalid_date_value",
                    description=(
                        "The date indicated by 'action taken date' must occur"
                        " within the current reporting period:"
                        " October 1, 2024 to December 31, 2024."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    start_date_value="20241001",
                    end_date_value="20241231",
                ),
                SBLCheck(
                    is_date_after,
                    id="E2009",
                    name="action_taken_date.date_value_conflict",
                    description="The date indicated by 'action taken date' must occur on or after 'application date'.",
                    severity=Severity.ERROR,
                    groupby="app_date",
                ),
                SBLCheck(
                    is_date_before_in_days,
                    id="W2010",
                    name="action_taken_date.unreasonable_date_value",
                    description=(
                        "The date indicated by 'application date' should"
                        " generally be less than two years (730 days) before"
                        " 'action taken date'."
                    ),
                    severity=Severity.WARNING,
                    groupby="app_date",
                    days_value=730,
                ),
            ],
        },
        "denial_reasons": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0340",
                    name="denial_reasons.invalid_enum_value",
                    description=(
                        "Each value in 'denial reason(s)' (separated by semicolons)"
                        " must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 977, or 999."
                    ),
                    severity=Severity.ERROR,
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
            ],
            "phase_2": [
                SBLCheck(
                    has_valid_value_count,
                    id="E0341",
                    name="denial_reasons.invalid_number_of_values",
                    description=(
                        "'Denial reason(s)' must contain at least one and at most four values, separated by semicolons."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    min_length=1,
                    max_length=4,
                ),
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2011",
                    name="denial_reasons.enum_value_conflict",
                    description=(
                        "When 'action taken' equals 3, 'denial reason(s)' must not "
                        "contain 999. When 'action taken' does not equal 3 (denied), 'denial "
                        "reason(s)' must equal 999 (not applicable)."
                    ),
                    severity=Severity.ERROR,
                    groupby="action_taken",
                    conditions=[
                        {
                            "condition_values": {"3"},
                            "is_equal_condition": True,
                            "target_value": "999",
                            "should_equal_target": False,
                        },
                        {
                            "condition_values": {"3"},
                            "is_equal_condition": False,
                            "target_value": "999",
                            "should_equal_target": True,
                        },
                    ],
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0340",
                    name="denial_reasons.multi_value_field_restriction",
                    description=(
                        "When 'denial reason(s)' contains 999 (not applicable), "
                        "'denial reason(s)' should not contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"999"},
                ),
                SBLCheck(
                    is_unique_in_field,
                    id="W0341",
                    name="denial_reasons.duplicates_in_field",
                    description="'Denial reason(s)' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
            ],
        },
        "denial_reasons_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    min_value=0,
                    max_value=300,
                    id="E0360",
                    name="denial_reasons_ff.invalid_text_length",
                    description=(
                        "'Free-form text field for other denial reason(s)' must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2012",
                    name="denial_reasons_ff.conditional_field_conflict",
                    description=(
                        "When 'denial reason(s)' does not contain 977 (other), field "
                        "'free-form text field for other denial reason(s)' must be "
                        "blank. When 'denial reason(s)' contains 977, 'free-form text "
                        "field for other denial reason(s)' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="denial_reasons",
                    condition_values={"977"},
                ),
                SBLCheck(
                    has_valid_multi_field_value_count,
                    id="W2013",
                    name="denial_reasons_ff.multi_invalid_number_of_values",
                    description=(
                        "'Denial reason(s)' and 'free-form text field for other "
                        "denial reason(s)' combined should not contain more than "
                        "four values. Code 977 (other), within 'Denial reason(s)', "
                        "does not count toward the maximum number of values for "
                        "the purpose of this validation check."
                    ),
                    severity=Severity.WARNING,
                    groupby="denial_reasons",
                    ignored_values={"977"},
                    max_length=4,
                ),
            ],
        },
        "pricing_interest_rate_type": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0380",
                    name="pricing_interest_rate_type.invalid_enum_value",
                    description="'Interest rate type' must equal 1, 2, 3, 4, 5, 6, or 999.",
                    severity=Severity.ERROR,
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
            "phase_2": [],
        },
        "pricing_init_rate_period": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0400",
                    name="pricing_init_rate_period.invalid_numeric_format",
                    description=(
                        "When present, 'adjustable rate transaction: initial rate period' must be a whole number."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2016",
                    name="pricing_init_rate_period.conditional_field_conflict",
                    description=(
                        "When 'interest rate type' does not equal 3 (initial rate "
                        "period > 12 months, adjustable interest), 4 (initial rate "
                        "period > 12 months, fixed interest), 5 (initial rate period "
                        "<= 12 months, adjustable interest), or 6 (initial rate period "
                        "<= 12 months, fixed interest), 'initial rate period' must "
                        "be blank. When 'interest rate type' equals 3, 4, 5, or 6, "
                        "'initial rate period' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="pricing_interest_rate_type",
                    condition_values={"3", "4", "5", "6"},
                ),
                SBLCheck(
                    is_greater_than,
                    id="E0401",
                    name="pricing_init_rate_period.invalid_numeric_value",
                    description=(
                        "When present, 'adjustable rate transaction: initial rate period' must be greater than 0."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    min_value="0",
                    accept_blank=True,
                ),
            ],
        },
        "pricing_fixed_rate": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0420",
                    name="pricing_fixed_rate.invalid_numeric_format",
                    description="When present, 'fixed rate: interest rate' must be a numeric value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2017",
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
                    severity=Severity.ERROR,
                    groupby="pricing_interest_rate_type",
                    condition_values={"2", "4", "6"},
                ),
                SBLCheck(
                    is_greater_than,
                    id="W0420",
                    name="pricing_fixed_rate.unreasonable_numeric_value",
                    description="When present, 'fixed rate: interest rate' should generally be greater than 0.1.",
                    severity=Severity.WARNING,
                    element_wise=True,
                    min_value="0.1",
                    accept_blank=True,
                ),
            ],
        },
        "pricing_adj_margin": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0440",
                    name="pricing_adj_margin.invalid_numeric_format",
                    description="When present, 'adjustable rate transaction: margin' must be a numeric value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2018",
                    name="pricing_adj_margin.conditional_field_conflict",
                    description=(
                        "When 'interest rate type' does not equal 1"
                        " (adjustable interest rate, no initial rate period),"
                        " 3 (initial rate period > 12 months, adjustable interest"
                        " rate), or 5 (initial rate period <= 12 months, adjustable "
                        "interest rate), 'adjustable rate transaction: margin' must "
                        "be blank. When 'interest rate type' equals 1, 3, or 5, "
                        "'adjustable rate transaction: margin' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="pricing_interest_rate_type",
                    condition_values={"1", "3", "5"},
                ),
                SBLCheck(
                    is_greater_than,
                    id="W0441",
                    name="pricing_adj_margin.unreasonable_numeric_value",
                    description=(
                        "When present, 'adjustable rate transaction: margin' should generally be greater than 0.1."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    min_value="0.1",
                    accept_blank=True,
                ),
            ],
        },
        "pricing_adj_index_name": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0460",
                    name="pricing_adj_index_name.invalid_enum_value",
                    description=(
                        "'Adjustable rate transaction: index name' must equal "
                        "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 977, or 999."
                    ),
                    severity=Severity.ERROR,
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
                        "977",
                        "999",
                    ],
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2019",
                    name="pricing_adj_index_name.enum_value_conflict",
                    description=(
                        "When 'interest rate type' does not equal 1 (adjustable interest"
                        " rate, no initial rate period), 3 (initial rate period > 12"
                        " months, adjustable interest rate), or 5 (initial rate"
                        " period <= 12 months, adjustable interest rate), 'adjustable"
                        " rate transaction: index name' must equal 999."
                        " When 'interest rate type' equals 1, 3, or 5, 'adjustable rate"
                        " transaction: index name' must not equal 999."
                    ),
                    severity=Severity.ERROR,
                    groupby="pricing_interest_rate_type",
                    conditions=[
                        {
                            "condition_values": {"1", "3", "5"},
                            "is_equal_condition": False,
                            "target_value": "999",
                            "should_equal_target": True,
                        },
                        {
                            "condition_values": {"1", "3", "5"},
                            "is_equal_condition": True,
                            "target_value": "999",
                            "should_equal_target": False,
                        },
                    ],
                ),
            ],
        },
        "pricing_adj_index_name_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    min_value=0,
                    max_value=300,
                    id="E0480",
                    name="pricing_adj_index_name_ff.invalid_text_length",
                    description=(
                        "'Adjustable rate transaction: index name: other' must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2020",
                    name="pricing_adj_index_name_ff.conditional_field_conflict",
                    description=(
                        "When 'adjustable rate transaction: index name' does not equal "
                        "977 (other), 'adjustable rate transaction: index name: other' "
                        "must be blank. "
                        "When 'adjustable rate transaction: index name' equals 977, "
                        "'adjustable rate transaction: index name: other' must not be "
                        "blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="pricing_adj_index_name",
                    condition_values={"977"},
                ),
            ],
        },
        "pricing_adj_index_value": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0500",
                    name="pricing_adj_index_value.invalid_numeric_format",
                    description="When present, 'adjustable rate transaction: index value' must be a numeric value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2021",
                    name="pricing_adj_index_value.conditional_field_conflict",
                    description=(
                        "When 'interest rate type' does not equal 1 (adjustable"
                        " interest rate, no initial rate period),"
                        " or 3 (initial rate period > 12 months, adjustable interest"
                        " rate), 'adjustable rate transaction: index value' must be"
                        " blank. When 'interest rate type' equals 1 or 3,"
                        " 'adjustable rate transaction: index value' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="pricing_interest_rate_type",
                    condition_values={"1", "3"},
                ),
            ],
        },
        "pricing_origination_charges": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0520",
                    name="pricing_origination_charges.invalid_numeric_format",
                    description="When present, 'total origination charges' must be a numeric value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [],
        },
        "pricing_broker_fees": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0540",
                    name="pricing_broker_fees.invalid_numeric_format",
                    description="When present, 'amount of total broker fees' must be a numeric value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [],
        },
        "pricing_initial_charges": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0560",
                    name="pricing_initial_charges.invalid_numeric_format",
                    description="When present, 'initial annual charges' must be a numeric value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [],
        },
        "pricing_mca_addcost_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0580",
                    name="pricing_mca_addcost_flag.invalid_enum_value",
                    description=(
                        "'MCA/sales-based: additional cost for merchant cash "
                        "advances or other sales-based financing: NA flag' "
                        "must equal 900 or 999."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "900",
                        "999",
                    ],
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2022",
                    name="pricing_mca_addcost_flag.enum_value_conflict",
                    description=(
                        "When 'credit product' does not equal 7 (merchant cash "
                        "advance), 8 (other sales-based financing transaction) "
                        "or 977 (other), 'MCA/sales-based: additional cost for "
                        "merchant cash advances or other sales-based financing: "
                        "NA flag' must be 999 (not applicable)."
                    ),
                    severity=Severity.ERROR,
                    groupby="ct_credit_product",
                    conditions=[
                        {
                            "condition_values": {"7", "8", "977"},
                            "is_equal_condition": False,
                            "target_value": "999",
                            "should_equal_target": True,
                        }
                    ],
                ),
            ],
        },
        "pricing_mca_addcost": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0600",
                    name="pricing_mca_addcost.invalid_numeric_format",
                    description=(
                        "When present, 'MCA/sales-based: additional cost for "
                        "merchant cash advances or other sales-based financing' "
                        "must be a numeric value."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2023",
                    name="pricing_mca_addcost.conditional_field_conflict",
                    description=(
                        "When 'MCA/sales-based: additional cost for merchant "
                        "cash advances or other sales-based financing: NA flag' "
                        "does not equal 900 (applicable), 'MCA/sales-based: "
                        "additional cost for merchant cash advances or other "
                        "sales-based financing' must be blank. When 'MCA/sales-based: "
                        "additional cost for merchant cash advances or other "
                        "sales-based financing: NA flag' equals 900, 'MCA/sales-based: "
                        "additional cost for merchant cash advances or other "
                        "sales-based financing' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="pricing_mca_addcost_flag",
                    condition_values={"900"},
                ),
            ],
        },
        "pricing_prepenalty_allowed": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0620",
                    name="pricing_prepenalty_allowed.invalid_enum_value",
                    description="'Prepayment penalty could be imposed' must equal 1, 2, or 999.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "999",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "pricing_prepenalty_exists": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0640",
                    name="pricing_prepenalty_exists.invalid_enum_value",
                    description="'Prepayment penalty exists' must equal 1, 2, or 999.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "999",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "census_tract_adr_type": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0660",
                    name="census_tract_adr_type.invalid_enum_value",
                    description="'Census tract: type of address' must equal 1, 2, 3, or 988.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "988",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "census_tract_number": {
            "phase_1": [
                SBLCheck(
                    has_correct_length,
                    id="E0680",
                    name="census_tract_number.invalid_text_length",
                    description="When present, 'census tract: tract number' must be a GEOID with exactly 11 digits.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_length=11,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2024",
                    name="census_tract_number.conditional_field_conflict",
                    description=(
                        "When 'census tract: type of address' equals 988 (not "
                        "provided by applicant and otherwise undetermined), "
                        "'census tract: tract number' must be blank. "
                        "When 'census tract: type of address' equals 1 (address"
                        " or location where the loan proceeds will principally "
                        "be applied), 2 (address or location of borrower's main "
                        "office or headquarters), or 3 (another address or "
                        "location associated with the applicant), 'census tract:"
                        " tract number' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="census_tract_adr_type",
                    conditions=[
                        {
                            "condition_values": {"1", "2", "3"},
                            "is_equal_condition": True,
                            "target_value": "",
                            "should_equal_target": False,
                        },
                        {
                            "condition_values": {"988"},
                            "is_equal_condition": True,
                            "target_value": "",
                            "should_equal_target": True,
                        },
                    ],
                ),
                SBLCheck(
                    is_valid_code,
                    id='W0680',
                    name='census_tract_number.invalid_geoid',
                    description=(
                        "When present, 'census tract: tract number' should be a valid "
                        "census tract GEOID as defined by the U.S. Census Bureau."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    accept_blank=True,
                    codes=global_data.census_geoids,
                ),
            ],
        },
        "gross_annual_revenue_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0700",
                    name="gross_annual_revenue_flag.invalid_enum_value",
                    description="'Gross annual revenue: NP flag' must equal 900 or 988.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "900",
                        "988",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "gross_annual_revenue": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0720",
                    name="gross_annual_revenue.invalid_numeric_format",
                    description="When present, 'gross annual revenue' must be a numeric value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2025",
                    name="gross_annual_revenue.conditional_field_conflict",
                    description=(
                        "When 'gross annual revenue: NP flag' does not equal 900 "
                        "(reported), 'gross annual revenue' must be blank. When "
                        "'gross annual revenue: NP flag' equals 900, "
                        "'gross annual revenue' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="gross_annual_revenue_flag",
                    condition_values={"900"},
                ),
            ],
        },
        "naics_code_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0740",
                    name="naics_code_flag.invalid_enum_value",
                    description=(
                        "'North American Industry Classification System (NAICS) code: NP flag' must equal 900 or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "900",
                        "988",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "naics_code": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0761",
                    name="naics_code.invalid_naics_format",
                    description=(
                        "'North American Industry Classification System "
                        "(NAICS) code' may only contain numeric characters."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_correct_length,
                    id="E0760",
                    name="naics_code.invalid_text_length",
                    description=(
                        "When present, 'North American Industry Classification System "
                        "(NAICS) code' must be three digits in length."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_length=3,
                    accept_blank=True,
                ),
                SBLCheck(
                    is_valid_code,
                    id="W0762",
                    name="naics_code.invalid_naics_value",
                    description=(
                        "When present, 'North American Industry Classification System "
                        "(NAICS) code' should be a valid NAICS code."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    accept_blank=True,
                    codes=global_data.naics_codes,
                ),
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2026",
                    name="naics_code.conditional_field_conflict",
                    description=(
                        "When 'North American Industry Classification System (NAICS) code: NP flag' does "
                        "not equal 900 (reported), 'North American Industry Classification System (NAICS) "
                        "code' must be blank. When 'North American Industry Classification System (NAICS) "
                        "code: NP flag' equals 900, 'North American Industry Classification System (NAICS) "
                        "code' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="naics_code_flag",
                    condition_values={"900"},
                ),
            ],
        },
        "number_of_workers": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0780",
                    name="number_of_workers.invalid_enum_value",
                    description="'Number of workers' must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, or 988.",
                    severity=Severity.ERROR,
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
                        "988",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "time_in_business_type": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0800",
                    name="time_in_business_type.invalid_enum_value",
                    description="'Time in business: type of response' must equal 1, 2, 3, or 988.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "988",
                    ],
                ),
            ],
            "phase_2": [],
        },
        "time_in_business": {
            "phase_1": [
                SBLCheck(
                    is_number,
                    id="E0820",
                    name="time_in_business.invalid_numeric_format",
                    description="When present, 'time in business' must be a whole number.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_greater_than_or_equal_to,
                    id="E0821",
                    name="time_in_business.invalid_numeric_value",
                    description="When present, 'time in business' must be greater than or equal to 0.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    min_value="0",
                    accept_blank=True,
                ),
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2027",
                    name="time_in_business.conditional_field_conflict",
                    description=(
                        "When 'time in business: type of response' does not"
                        " equal 1 (the number of years an applicant has been"
                        " in business is collected or obtained by the financial"
                        " institution), 'time in business' must be blank. When"
                        " 'time in business: type of response' equals 1,"
                        " 'time in business' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="time_in_business_type",
                    condition_values={"1"},
                ),
            ],
        },
        "business_ownership_status": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0840",
                    name="business_ownership_status.invalid_enum_value",
                    description=(
                        "Each value in 'business ownership status'"
                        " (separated by semicolons) must equal 1, 2, 3,"
                        " 955, 966, or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "955",
                        "966",
                        "988",
                    ],
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_valid_value_count,
                    id="E0841",
                    name="business_ownership_status.invalid_number_of_values",
                    description="'Business ownership status' must contain at least one value.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    min_length=1,
                ),
                SBLCheck(
                    is_unique_in_field,
                    id="W0842",
                    name="business_ownership_status.duplicates_in_field",
                    description="'Business ownership status' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0843",
                    name="business_ownership_status.multi_value_field_restriction",
                    description=(
                        "When 'business ownership status' contains 966"
                        " (the applicant responded that they did not wish"
                        " to provide this information) or 988 (not provided"
                        " by applicant), 'business ownership status' should"
                        " not contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "num_principal_owners_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0860",
                    name="num_principal_owners_flag.invalid_enum_value",
                    description="'Number of principal owners: NP flag' must equal 900 or 988.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "900",
                        "988",
                    ],
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_valid_fieldset_pair,
                    id="W2035",
                    name="po_demographics_0.conditional_fieldset_conflict",
                    description=(
                        "When 'number of principal owners' equals 0 or is blank, "
                        "demographic fields for principal owners 1, 2, 3, and 4 "
                        "should be blank."
                    ),
                    severity=Severity.WARNING,
                    groupby=[
                        "po_1_ethnicity",
                        "po_1_race",
                        "po_1_gender_flag",
                        "po_2_ethnicity",
                        "po_2_race",
                        "po_2_gender_flag",
                        "po_3_ethnicity",
                        "po_3_race",
                        "po_3_gender_flag",
                        "po_4_ethnicity",
                        "po_4_race",
                        "po_4_gender_flag",
                    ],
                    condition_values=["0", ""],
                    should_fieldset_key_equal_to={
                        "po_1_ethnicity": (0, True, ""),
                        "po_1_race": (1, True, ""),
                        "po_1_gender_flag": (2, True, ""),
                        "po_2_ethnicity": (3, True, ""),
                        "po_2_race": (4, True, ""),
                        "po_2_gender_flag": (5, True, ""),
                        "po_3_ethnicity": (6, True, ""),
                        "po_3_race": (7, True, ""),
                        "po_3_gender_flag": (8, True, ""),
                        "po_4_ethnicity": (9, True, ""),
                        "po_4_race": (10, True, ""),
                        "po_4_gender_flag": (11, True, ""),
                    },
                ),
                SBLCheck(
                    has_valid_fieldset_pair,
                    id="W2036",
                    name="po_demographics_1.conditional_fieldset_conflict",
                    description=(
                        "When 'number of principal owners' equals 1, "
                        "'ethnicity of principal owner 1', 'race of principal owner 1',"
                        " and 'sex/gender of principal owner 1: NP flag' should not be"
                        " blank. Demographic fields for principal owners 2, 3, and 4 "
                        "should be blank."
                    ),
                    severity=Severity.WARNING,
                    groupby=[
                        "po_1_ethnicity",
                        "po_1_race",
                        "po_1_gender_flag",
                        "po_2_ethnicity",
                        "po_2_race",
                        "po_2_gender_flag",
                        "po_3_ethnicity",
                        "po_3_race",
                        "po_3_gender_flag",
                        "po_4_ethnicity",
                        "po_4_race",
                        "po_4_gender_flag",
                    ],
                    condition_values=["1"],
                    should_fieldset_key_equal_to={
                        "po_1_ethnicity": (0, False, ""),
                        "po_1_race": (1, False, ""),
                        "po_1_gender_flag": (2, False, ""),
                        "po_2_ethnicity": (3, True, ""),
                        "po_2_race": (4, True, ""),
                        "po_2_gender_flag": (5, True, ""),
                        "po_3_ethnicity": (6, True, ""),
                        "po_3_race": (7, True, ""),
                        "po_3_gender_flag": (8, True, ""),
                        "po_4_ethnicity": (9, True, ""),
                        "po_4_race": (10, True, ""),
                        "po_4_gender_flag": (11, True, ""),
                    },
                ),
                SBLCheck(
                    has_valid_fieldset_pair,
                    id="W2037",
                    name="po_demographics_2.conditional_fieldset_conflict",
                    description=(
                        "When 'number of principal owners' equals 2, "
                        "'ethnicity of principal owner 1 and 2', 'race of principal "
                        "owner 1 and 2', and 'sex/gender of principal owner 1 and 2: "
                        "NP flag' should not be blank. Demographic fields for "
                        "principal owners 3 and 4 should be blank."
                    ),
                    severity=Severity.WARNING,
                    groupby=[
                        "po_1_ethnicity",
                        "po_1_race",
                        "po_1_gender_flag",
                        "po_2_ethnicity",
                        "po_2_race",
                        "po_2_gender_flag",
                        "po_3_ethnicity",
                        "po_3_race",
                        "po_3_gender_flag",
                        "po_4_ethnicity",
                        "po_4_race",
                        "po_4_gender_flag",
                    ],
                    condition_values=["2"],
                    should_fieldset_key_equal_to={
                        "po_1_ethnicity": (0, False, ""),
                        "po_1_race": (1, False, ""),
                        "po_1_gender_flag": (2, False, ""),
                        "po_2_ethnicity": (3, False, ""),
                        "po_2_race": (4, False, ""),
                        "po_2_gender_flag": (5, False, ""),
                        "po_3_ethnicity": (6, True, ""),
                        "po_3_race": (7, True, ""),
                        "po_3_gender_flag": (8, True, ""),
                        "po_4_ethnicity": (9, True, ""),
                        "po_4_race": (10, True, ""),
                        "po_4_gender_flag": (11, True, ""),
                    },
                ),
                SBLCheck(
                    has_valid_fieldset_pair,
                    id="W2038",
                    name="po_demographics_3.conditional_fieldset_conflict",
                    description=(
                        "When 'number of principal owners' equals 3, "
                        "'ethnicity of principal owner 1, 2, and 3', 'race of principal"
                        " owner 1, 2, and 3', and 'sex/gender of principal owner 1, 2, "
                        "and 3: NP flag' should not be blank. Demographic fields for "
                        "principal owner 4 should be blank."
                    ),
                    severity=Severity.WARNING,
                    groupby=[
                        "po_1_ethnicity",
                        "po_1_race",
                        "po_1_gender_flag",
                        "po_2_ethnicity",
                        "po_2_race",
                        "po_2_gender_flag",
                        "po_3_ethnicity",
                        "po_3_race",
                        "po_3_gender_flag",
                        "po_4_ethnicity",
                        "po_4_race",
                        "po_4_gender_flag",
                    ],
                    condition_values=["3"],
                    should_fieldset_key_equal_to={
                        "po_1_ethnicity": (0, False, ""),
                        "po_1_race": (1, False, ""),
                        "po_1_gender_flag": (2, False, ""),
                        "po_2_ethnicity": (3, False, ""),
                        "po_2_race": (4, False, ""),
                        "po_2_gender_flag": (5, False, ""),
                        "po_3_ethnicity": (6, False, ""),
                        "po_3_race": (7, False, ""),
                        "po_3_gender_flag": (8, False, ""),
                        "po_4_ethnicity": (9, True, ""),
                        "po_4_race": (10, True, ""),
                        "po_4_gender_flag": (11, True, ""),
                    },
                ),
                SBLCheck(
                    has_valid_fieldset_pair,
                    id="W2039",
                    name="po_demographics_4.conditional_fieldset_conflict",
                    description=(
                        "When 'number of principal owners' equals 4, "
                        "'ethnicity of principal owner 1, 2, 3, and 4', "
                        "'race of principal owner 1, 2, 3, and 4', "
                        "and 'sex/gender of principal owner 1, 2, 3, and 4: NP flag'"
                        " should not be blank."
                    ),
                    severity=Severity.WARNING,
                    groupby=[
                        "po_1_ethnicity",
                        "po_1_race",
                        "po_1_gender_flag",
                        "po_2_ethnicity",
                        "po_2_race",
                        "po_2_gender_flag",
                        "po_3_ethnicity",
                        "po_3_race",
                        "po_3_gender_flag",
                        "po_4_ethnicity",
                        "po_4_race",
                        "po_4_gender_flag",
                    ],
                    condition_values=["4"],
                    should_fieldset_key_equal_to={
                        "po_1_ethnicity": (0, False, ""),
                        "po_1_race": (1, False, ""),
                        "po_1_gender_flag": (2, False, ""),
                        "po_2_ethnicity": (3, False, ""),
                        "po_2_race": (4, False, ""),
                        "po_2_gender_flag": (5, False, ""),
                        "po_3_ethnicity": (6, False, ""),
                        "po_3_race": (7, False, ""),
                        "po_3_gender_flag": (8, False, ""),
                        "po_4_ethnicity": (9, False, ""),
                        "po_4_race": (10, False, ""),
                        "po_4_gender_flag": (11, False, ""),
                    },
                ),
            ],
        },
        "num_principal_owners": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0880",
                    name="num_principal_owners.invalid_enum_value",
                    description="When present, 'number of principal owners' must equal 0, 1, 2, 3, or 4.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=["0", "1", "2", "3", "4"],
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2028",
                    name="num_principal_owners.conditional_field_conflict",
                    description=(
                        "When 'number of principal owners: NP flag' does not equal 900 "
                        "(reported), 'number of principal owners' must be blank. "
                        "When 'number of principal owners: NP flag' equals 900, "
                        "'number of principal owners' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="num_principal_owners_flag",
                    condition_values={"900"},
                ),
            ],
        },
        "po_1_ethnicity": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0900",
                    name="po_1_ethnicity.invalid_enum_value",
                    description=(
                        "When present, each value in 'ethnicity"
                        " of principal owner 1' (separated by"
                        " semicolons) must equal 1, 11, 12,"
                        " 13, 14, 2, 966, 977, or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "11",
                        "12",
                        "13",
                        "14",
                        "2",
                        "966",
                        "977",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_unique_in_field,
                    id="W0901",
                    name="po_1_ethnicity.duplicates_in_field",
                    description="'Ethnicity of principal owner 1' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0902",
                    name="po_1_ethnicity.multi_value_field_restriction",
                    description=(
                        "When 'ethnicity of principal owner 1' contains"
                        " 966 (the applicant responded that they did"
                        " not wish to provide this information) or 988"
                        " (not provided by applicant), 'ethnicity of"
                        " principal owner: 1' should not contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_1_ethnicity_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0920",
                    name="po_1_ethnicity_ff.invalid_text_length",
                    description=(
                        "'Ethnicity of principal owner 1: free-form"
                        " text field for other Hispanic or Latino'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2040",
                    name="po_1_ethnicity_ff.conditional_field_conflict",
                    description=(
                        "When 'ethnicity of principal owner 1' does not"
                        " contain 977 (the applicant responded in the"
                        " free-form text field), 'ethnicity of principal"
                        " owner 1: free-form text field for other Hispanic"
                        " or Latino' must be blank. When 'ethnicity of principal"
                        " owner 1' contains 977, 'ethnicity of principal"
                        " owner 1: free-form text field for other Hispanic"
                        " or Latino' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_1_ethnicity",
                    condition_values={"977"},
                ),
            ],
        },
        "po_1_race": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E0940",
                    name="po_1_race.invalid_enum_value",
                    description=(
                        "When present, each value in 'race"
                        " of principal owner 1' (separated by"
                        " semicolons) must equal 1, 2, 21, 22,"
                        " 23, 24, 25, 26, 27, 3, 31, 32, 33,"
                        " 34, 35, 36, 37, 4, 41, 42, 43, 44,"
                        " 5, 966, 971, 972, 973, 974, or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "21",
                        "22",
                        "23",
                        "24",
                        "25",
                        "26",
                        "27",
                        "3",
                        "31",
                        "32",
                        "33",
                        "34",
                        "35",
                        "36",
                        "37",
                        "4",
                        "41",
                        "42",
                        "43",
                        "44",
                        "5",
                        "966",
                        "971",
                        "972",
                        "973",
                        "974",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_unique_in_field,
                    id="W0941",
                    name="po_1_race.duplicates_in_field",
                    description="'Race of principal owner 1' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0942",
                    name="po_1_race.multi_value_field_restriction",
                    description=(
                        "When 'race of principal owner 1' contains"
                        " 966 (the applicant responded that they"
                        " did not wish to provide this information)"
                        " or 988 (not provided by applicant),"
                        " 'race of principal owner: 1' should not"
                        " contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_1_race_anai_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0960",
                    name="po_1_race_anai_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 1: free-form"
                        " text field for American Indian or Alaska"
                        " Native Enrolled or Principal Tribe' must"
                        " not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2060",
                    name="po_1_race_anai_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 1' does not"
                        " contain 971 (the applicant responded in"
                        " the free-form text field for American Indian"
                        " or Alaska Native Enrolled or Principal Tribe),"
                        " 'race of principal owner 1: free-form text"
                        " field for American Indian or Alaska Native"
                        " Enrolled or Principal Tribe' must be blank."
                        " When 'race of principal owner 1' contains 971,"
                        " 'race of principal owner 1: free-form text field"
                        " for American Indian or Alaska Native Enrolled or"
                        " Principal Tribe' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_1_race",
                    condition_values={"971"},
                ),
            ],
        },
        "po_1_race_asian_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0980",
                    name="po_1_race_asian_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 1: free-form text"
                        " field for other Asian' must not exceed 300"
                        " characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2080",
                    name="po_1_race_asian_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 1' does not contain"
                        " 972 (the applicant responded in the free-form text"
                        " field for other Asian race), 'race of principal"
                        " owner 1: free-form text field for other Asian' must"
                        " be blank. When 'race of principal owner 1' contains"
                        " 972, 'race of principal owner 1: free-form text field"
                        " for other Asian' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_1_race",
                    condition_values={"972"},
                ),
            ],
        },
        "po_1_race_baa_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1000",
                    name="po_1_race_baa_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 1: free-form text"
                        " field for other Black or African American'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2100",
                    name="po_1_race_baa_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 1' does not contain 973"
                        " (the applicant responded in the free-form text field"
                        " for other Black or African race), 'race of principal"
                        " owner 1: free-form text field for other Black or African"
                        " American' must be blank. When 'race of principal owner 1'"
                        " contains 973, 'race of principal owner 1: free-form text"
                        " field for other Black or African American' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_1_race",
                    condition_values={"973"},
                ),
            ],
        },
        "po_1_race_pi_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1020",
                    name="po_1_race_pi_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 1: free-form text"
                        " field for other Pacific Islander race' must"
                        " not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2120",
                    name="po_1_race_pi_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 1' does not contain 974"
                        " (the applicant responded in the free-form text field"
                        " for other Pacific Islander race), 'race of principal"
                        " owner 1: free-form text field for other Pacific Islander"
                        " race' must be blank. When 'race of principal owner 1'"
                        " contains 974, 'Race of Principal Owner 1: Free-form Text"
                        " Field for Other Pacific Islander race' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_1_race",
                    condition_values={"974"},
                ),
            ],
        },
        "po_1_gender_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1040",
                    name="po_1_gender_flag.invalid_enum_value",
                    description="When present, 'sex/gender of principal owner 1: NP flag' must equal 1, 966, or 988.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "966",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [],
        },
        "po_1_gender_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1060",
                    name="po_1_gender_ff.invalid_text_length",
                    description=(
                        "'Sex/gender of principal owner 1: free-form"
                        " text field for self-identified sex/gender'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2140",
                    name="po_1_gender_ff.conditional_field_conflict",
                    description=(
                        "When 'sex/gender of principal owner 1: NP flag'"
                        " does not equal 1 (the applicant responded in the"
                        " free-form text field), 'sex/gender of principal"
                        " owner 1: free-form text field for self-identified"
                        " sex/gender' must be blank. When 'sex/gender of"
                        " principal owner 1: NP flag' equals 1, 'sex/gender"
                        " of principal owner 1: free-form text field for"
                        " self-identified sex/gender' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_1_gender_flag",
                    condition_values={"1"},
                ),
            ],
        },
        "po_2_ethnicity": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1080",
                    name="po_2_ethnicity.invalid_enum_value",
                    description=(
                        "When present, each value in 'ethnicity"
                        " of principal owner 2' (separated by"
                        " semicolons) must equal 1, 11, 12,"
                        " 13, 14, 2, 966, 977, or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "11",
                        "12",
                        "13",
                        "14",
                        "2",
                        "966",
                        "977",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_unique_in_field,
                    id="W1081",
                    name="po_2_ethnicity.duplicates_in_field",
                    description="'Ethnicity of principal owner 2' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1082",
                    name="po_2_ethnicity.multi_value_field_restriction",
                    description=(
                        "When 'ethnicity of principal owner 2' contains"
                        " 966 (the applicant responded that they did"
                        " not wish to provide this information) or 988"
                        " (not provided by applicant), 'ethnicity of"
                        " principal owner: 2' should not contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_2_ethnicity_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1100",
                    name="po_2_ethnicity_ff.invalid_text_length",
                    description=(
                        "'Ethnicity of principal owner 2: free-form"
                        " text field for other Hispanic or Latino'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2041",
                    name="po_2_ethnicity_ff.conditional_field_conflict",
                    description=(
                        "When 'ethnicity of principal owner 2' does not"
                        " contain 977 (the applicant responded in the"
                        " free-form text field), 'ethnicity of principal"
                        " owner 2: free-form text field for other Hispanic"
                        " or Latino' must be blank. When 'ethnicity of principal"
                        " owner 2' contains 977, 'ethnicity of principal"
                        " owner 2: free-form text field for other Hispanic"
                        " or Latino' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_2_ethnicity",
                    condition_values={"977"},
                ),
            ],
        },
        "po_2_race": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1120",
                    name="po_2_race.invalid_enum_value",
                    description=(
                        "When present, each value in 'race"
                        " of principal owner 2' (separated by"
                        " semicolons) must equal 1, 2, 21, 22,"
                        " 23, 24, 25, 26, 27, 3, 31, 32, 33,"
                        " 34, 35, 36, 37, 4, 41, 42, 43, 44,"
                        " 5, 966, 971, 972, 973, 974, or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "21",
                        "22",
                        "23",
                        "24",
                        "25",
                        "26",
                        "27",
                        "3",
                        "31",
                        "32",
                        "33",
                        "34",
                        "35",
                        "36",
                        "37",
                        "4",
                        "41",
                        "42",
                        "43",
                        "44",
                        "5",
                        "966",
                        "971",
                        "972",
                        "973",
                        "974",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_unique_in_field,
                    id="W1121",
                    name="po_2_race.duplicates_in_field",
                    description="'Race of principal owner 2' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1122",
                    name="po_2_race.multi_value_field_restriction",
                    description=(
                        "When 'race of principal owner 2' contains"
                        " 966 (the applicant responded that they"
                        " did not wish to provide this information)"
                        " or 988 (not provided by applicant),"
                        " 'race of principal owner: 2' should not"
                        " contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_2_race_anai_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1140",
                    name="po_2_race_anai_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 2: free-form"
                        " text field for American Indian or Alaska"
                        " Native Enrolled or Principal Tribe' must"
                        " not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2061",
                    name="po_2_race_anai_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 2' does not"
                        " contain 971 (the applicant responded in"
                        " the free-form text field for American Indian"
                        " or Alaska Native Enrolled or Principal Tribe),"
                        " 'race of principal owner 2: free-form text"
                        " field for American Indian or Alaska Native"
                        " Enrolled or Principal Tribe' must be blank."
                        " When 'race of principal owner 2' contains 971,"
                        " 'race of principal owner 2: free-form text field"
                        " for American Indian or Alaska Native Enrolled or"
                        " Principal Tribe' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_2_race",
                    condition_values={"971"},
                ),
            ],
        },
        "po_2_race_asian_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1160",
                    name="po_2_race_asian_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 2: free-form text"
                        " field for other Asian' must not exceed 300"
                        " characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2081",
                    name="po_2_race_asian_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 2' does not contain"
                        " 972 (the applicant responded in the free-form text"
                        " field for other Asian race), 'race of principal"
                        " owner 2: free-form text field for other Asian' must"
                        " be blank. When 'race of principal owner 2' contains"
                        " 972, 'race of principal owner 2: free-form text field"
                        " for other Asian' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_2_race",
                    condition_values={"972"},
                ),
            ],
        },
        "po_2_race_baa_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1180",
                    name="po_2_race_baa_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 2: free-form text"
                        " field for other Black or African American'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2101",
                    name="po_2_race_baa_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 2' does not contain 973"
                        " (the applicant responded in the free-form text field"
                        " for other Black or African race), 'race of principal"
                        " owner 2: free-form text field for other Black or African"
                        " American' must be blank. When 'race of principal owner 2'"
                        " contains 973, 'race of principal owner 2: free-form text"
                        " field for other Black or African American' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_2_race",
                    condition_values={"973"},
                ),
            ],
        },
        "po_2_race_pi_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1200",
                    name="po_2_race_pi_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 2: free-form text"
                        " field for other Pacific Islander race' must"
                        " not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2121",
                    name="po_2_race_pi_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 2' does not contain 974"
                        " (the applicant responded in the free-form text field"
                        " for other Pacific Islander race), 'race of principal"
                        " owner 2: free-form text field for other Pacific Islander"
                        " race' must be blank. When 'race of principal owner 2'"
                        " contains 974, 'Race of Principal Owner 2: Free-form Text"
                        " Field for Other Pacific Islander race' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_2_race",
                    condition_values={"974"},
                ),
            ],
        },
        "po_2_gender_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1220",
                    name="po_2_gender_flag.invalid_enum_value",
                    description="When present, 'sex/gender of principal owner 2: NP flag' must equal 1, 966, or 988.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "966",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [],
        },
        "po_2_gender_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1240",
                    name="po_2_gender_ff.invalid_text_length",
                    description=(
                        "'Sex/gender of principal owner 2: free-form"
                        " text field for self-identified sex/gender'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2141",
                    name="po_2_gender_ff.conditional_field_conflict",
                    description=(
                        "When 'sex/gender of principal owner 2: NP flag'"
                        " does not equal 1 (the applicant responded in the"
                        " free-form text field), 'sex/gender of principal"
                        " owner 2: free-form text field for self-identified"
                        " sex/gender' must be blank. When 'sex/gender of"
                        " principal owner 2: NP flag' equals 1, 'sex/gender"
                        " of principal owner 2: free-form text field for"
                        " self-identified sex/gender' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_2_gender_flag",
                    condition_values={"1"},
                ),
            ],
        },
        "po_3_ethnicity": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1260",
                    name="po_3_ethnicity.invalid_enum_value",
                    description=(
                        "When present, each value in 'ethnicity"
                        " of principal owner 3' (separated by"
                        " semicolons) must equal 1, 11, 12,"
                        " 13, 14, 2, 966, 977, or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "11",
                        "12",
                        "13",
                        "14",
                        "2",
                        "966",
                        "977",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_unique_in_field,
                    id="W1261",
                    name="po_3_ethnicity.duplicates_in_field",
                    description="'Ethnicity of principal owner 3' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1262",
                    name="po_3_ethnicity.multi_value_field_restriction",
                    description=(
                        "When 'ethnicity of principal owner 3' contains"
                        " 966 (the applicant responded that they did"
                        " not wish to provide this information) or 988"
                        " (not provided by applicant), 'ethnicity of"
                        " principal owner: 3' should not contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_3_ethnicity_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1280",
                    name="po_3_ethnicity_ff.invalid_text_length",
                    description=(
                        "'Ethnicity of principal owner 3: free-form"
                        " text field for other Hispanic or Latino'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2042",
                    name="po_3_ethnicity_ff.conditional_field_conflict",
                    description=(
                        "When 'ethnicity of principal owner 3' does not"
                        " contain 977 (the applicant responded in the"
                        " free-form text field), 'ethnicity of principal"
                        " owner 3: free-form text field for other Hispanic"
                        " or Latino' must be blank. When 'ethnicity of principal"
                        " owner 3' contains 977, 'ethnicity of principal"
                        " owner 3: free-form text field for other Hispanic"
                        " or Latino' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_3_ethnicity",
                    condition_values={"977"},
                ),
            ],
        },
        "po_3_race": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1300",
                    name="po_3_race.invalid_enum_value",
                    description=(
                        "When present, each value in 'race"
                        " of principal owner 3' (separated by"
                        " semicolons) must equal 1, 2, 21, 22,"
                        " 23, 24, 25, 26, 27, 3, 31, 32, 33,"
                        " 34, 35, 36, 37, 4, 41, 42, 43, 44,"
                        " 5, 966, 971, 972, 973, 974, or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "21",
                        "22",
                        "23",
                        "24",
                        "25",
                        "26",
                        "27",
                        "3",
                        "31",
                        "32",
                        "33",
                        "34",
                        "35",
                        "36",
                        "37",
                        "4",
                        "41",
                        "42",
                        "43",
                        "44",
                        "5",
                        "966",
                        "971",
                        "972",
                        "973",
                        "974",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_unique_in_field,
                    id="W1301",
                    name="po_3_race.duplicates_in_field",
                    description="'Race of principal owner 3' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1302",
                    name="po_3_race.multi_value_field_restriction",
                    description=(
                        "When 'race of principal owner 3' contains"
                        " 966 (the applicant responded that they"
                        " did not wish to provide this information)"
                        " or 988 (not provided by applicant),"
                        " 'race of principal owner: 3' should not"
                        " contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_3_race_anai_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1320",
                    name="po_3_race_anai_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 3: free-form"
                        " text field for American Indian or Alaska"
                        " Native Enrolled or Principal Tribe' must"
                        " not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2062",
                    name="po_3_race_anai_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 3' does not"
                        " contain 971 (the applicant responded in"
                        " the free-form text field for American Indian"
                        " or Alaska Native Enrolled or Principal Tribe),"
                        " 'race of principal owner 3: free-form text"
                        " field for American Indian or Alaska Native"
                        " Enrolled or Principal Tribe' must be blank."
                        " When 'race of principal owner 3' contains 971,"
                        " 'race of principal owner 3: free-form text field"
                        " for American Indian or Alaska Native Enrolled or"
                        " Principal Tribe' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_3_race",
                    condition_values={"971"},
                ),
            ],
        },
        "po_3_race_asian_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1340",
                    name="po_3_race_asian_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 3: free-form text"
                        " field for other Asian' must not exceed 300"
                        " characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2082",
                    name="po_3_race_asian_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 3' does not contain"
                        " 972 (the applicant responded in the free-form text"
                        " field for other Asian race), 'race of principal"
                        " owner 3: free-form text field for other Asian' must"
                        " be blank. When 'race of principal owner 3' contains"
                        " 972, 'race of principal owner 3: free-form text field"
                        " for other Asian' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_3_race",
                    condition_values={"972"},
                ),
            ],
        },
        "po_3_race_baa_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1360",
                    name="po_3_race_baa_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 3: free-form text"
                        " field for other Black or African American'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2102",
                    name="po_3_race_baa_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 3' does not contain 973"
                        " (the applicant responded in the free-form text field"
                        " for other Black or African race), 'race of principal"
                        " owner 3: free-form text field for other Black or African"
                        " American' must be blank. When 'race of principal owner 3'"
                        " contains 973, 'race of principal owner 3: free-form text"
                        " field for other Black or African American' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_3_race",
                    condition_values={"973"},
                ),
            ],
        },
        "po_3_race_pi_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1380",
                    name="po_3_race_pi_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 3: free-form text"
                        " field for other Pacific Islander race' must"
                        " not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2122",
                    name="po_3_race_pi_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 3' does not contain 974"
                        " (the applicant responded in the free-form text field"
                        " for other Pacific Islander race), 'race of principal"
                        " owner 3: free-form text field for other Pacific Islander"
                        " race' must be blank. When 'race of principal owner 3'"
                        " contains 974, 'Race of Principal Owner 3: Free-form Text"
                        " Field for Other Pacific Islander race' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_3_race",
                    condition_values={"974"},
                ),
            ],
        },
        "po_3_gender_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1400",
                    name="po_3_gender_flag.invalid_enum_value",
                    description="When present, 'sex/gender of principal owner 3: NP flag' must equal 1, 966, or 988.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "966",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [],
        },
        "po_3_gender_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1420",
                    name="po_3_gender_ff.invalid_text_length",
                    description=(
                        "'Sex/gender of principal owner 3: free-form"
                        " text field for self-identified sex/gender'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2142",
                    name="po_3_gender_ff.conditional_field_conflict",
                    description=(
                        "When 'sex/gender of principal owner 3: NP flag'"
                        " does not equal 1 (the applicant responded in the"
                        " free-form text field), 'sex/gender of principal"
                        " owner 3: free-form text field for self-identified"
                        " sex/gender' must be blank. When 'sex/gender of"
                        " principal owner 3: NP flag' equals 1, 'sex/gender"
                        " of principal owner 3: free-form text field for"
                        " self-identified sex/gender' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_3_gender_flag",
                    condition_values={"1"},
                ),
            ],
        },
        "po_4_ethnicity": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1440",
                    name="po_4_ethnicity.invalid_enum_value",
                    description=(
                        "When present, each value in 'ethnicity"
                        " of principal owner 4' (separated by"
                        " semicolons) must equal 1, 11, 12,"
                        " 13, 14, 2, 966, 977, or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "11",
                        "12",
                        "13",
                        "14",
                        "2",
                        "966",
                        "977",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_unique_in_field,
                    id="W1441",
                    name="po_4_ethnicity.duplicates_in_field",
                    description="'Ethnicity of principal owner 4' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1442",
                    name="po_4_ethnicity.multi_value_field_restriction",
                    description=(
                        "When 'ethnicity of principal owner 4' contains"
                        " 966 (the applicant responded that they did"
                        " not wish to provide this information) or 988"
                        " (not provided by applicant), 'ethnicity of"
                        " principal owner: 4' should not contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_4_ethnicity_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1460",
                    name="po_4_ethnicity_ff.invalid_text_length",
                    description=(
                        "'Ethnicity of principal owner 4: free-form"
                        " text field for other Hispanic or Latino'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2043",
                    name="po_4_ethnicity_ff.conditional_field_conflict",
                    description=(
                        "When 'ethnicity of principal owner 4' does not"
                        " contain 977 (the applicant responded in the"
                        " free-form text field), 'ethnicity of principal"
                        " owner 4: free-form text field for other Hispanic"
                        " or Latino' must be blank. When 'ethnicity of principal"
                        " owner 4' contains 977, 'ethnicity of principal"
                        " owner 4: free-form text field for other Hispanic"
                        " or Latino' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_4_ethnicity",
                    condition_values={"977"},
                ),
            ],
        },
        "po_4_race": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1480",
                    name="po_4_race.invalid_enum_value",
                    description=(
                        "When present, each value in 'race"
                        " of principal owner 4' (separated by"
                        " semicolons) must equal 1, 2, 21, 22,"
                        " 23, 24, 25, 26, 27, 3, 31, 32, 33,"
                        " 34, 35, 36, 37, 4, 41, 42, 43, 44,"
                        " 5, 966, 971, 972, 973, 974, or 988."
                    ),
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "2",
                        "21",
                        "22",
                        "23",
                        "24",
                        "25",
                        "26",
                        "27",
                        "3",
                        "31",
                        "32",
                        "33",
                        "34",
                        "35",
                        "36",
                        "37",
                        "4",
                        "41",
                        "42",
                        "43",
                        "44",
                        "5",
                        "966",
                        "971",
                        "972",
                        "973",
                        "974",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    is_unique_in_field,
                    id="W1481",
                    name="po_4_race.duplicates_in_field",
                    description="'Race of principal owner 4' should not contain duplicated values.",
                    severity=Severity.WARNING,
                    element_wise=True,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1482",
                    name="po_4_race.multi_value_field_restriction",
                    description=(
                        "When 'race of principal owner 4' contains"
                        " 966 (the applicant responded that they"
                        " did not wish to provide this information)"
                        " or 988 (not provided by applicant),"
                        " 'race of principal owner: 4' should not"
                        " contain more than one value."
                    ),
                    severity=Severity.WARNING,
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_4_race_anai_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1500",
                    name="po_4_race_anai_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 4: free-form"
                        " text field for American Indian or Alaska"
                        " Native Enrolled or Principal Tribe' must"
                        " not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2063",
                    name="po_4_race_anai_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 4' does not"
                        " contain 971 (the applicant responded in"
                        " the free-form text field for American Indian"
                        " or Alaska Native Enrolled or Principal Tribe),"
                        " 'race of principal owner 4: free-form text"
                        " field for American Indian or Alaska Native"
                        " Enrolled or Principal Tribe' must be blank."
                        " When 'race of principal owner 4' contains 971,"
                        " 'race of principal owner 4: free-form text field"
                        " for American Indian or Alaska Native Enrolled or"
                        " Principal Tribe' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_4_race",
                    condition_values={"971"},
                ),
            ],
        },
        "po_4_race_asian_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1520",
                    name="po_4_race_asian_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 4: free-form text"
                        " field for other Asian' must not exceed 300"
                        " characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2083",
                    name="po_4_race_asian_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 4' does not contain"
                        " 972 (the applicant responded in the free-form text"
                        " field for other Asian race), 'race of principal"
                        " owner 4: free-form text field for other Asian' must"
                        " be blank. When 'race of principal owner 4' contains"
                        " 972, 'race of principal owner 4: free-form text field"
                        " for other Asian' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_4_race",
                    condition_values={"972"},
                ),
            ],
        },
        "po_4_race_baa_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1540",
                    name="po_4_race_baa_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 4: free-form text"
                        " field for other Black or African American'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2103",
                    name="po_4_race_baa_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 4' does not contain 973"
                        " (the applicant responded in the free-form text field"
                        " for other Black or African race), 'race of principal"
                        " owner 4: free-form text field for other Black or African"
                        " American' must be blank. When 'race of principal owner 4'"
                        " contains 973, 'race of principal owner 4: free-form text"
                        " field for other Black or African American' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_4_race",
                    condition_values={"973"},
                ),
            ],
        },
        "po_4_race_pi_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1560",
                    name="po_4_race_pi_ff.invalid_text_length",
                    description=(
                        "'Race of principal owner 4: free-form text"
                        " field for other Pacific Islander race' must"
                        " not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2123",
                    name="po_4_race_pi_ff.conditional_field_conflict",
                    description=(
                        "When 'race of principal owner 4' does not contain 974"
                        " (the applicant responded in the free-form text field"
                        " for other Pacific Islander race), 'race of principal"
                        " owner 4: free-form text field for other Pacific Islander"
                        " race' must be blank. When 'race of principal owner 4'"
                        " contains 974, 'Race of Principal Owner 4: Free-form Text"
                        " Field for Other Pacific Islander race' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_4_race",
                    condition_values={"974"},
                ),
            ],
        },
        "po_4_gender_flag": {
            "phase_1": [
                SBLCheck(
                    is_valid_enum,
                    id="E1580",
                    name="po_4_gender_flag.invalid_enum_value",
                    description="When present, 'sex/gender of principal owner 4: NP flag' must equal 1, 966, or 988.",
                    severity=Severity.ERROR,
                    element_wise=True,
                    accepted_values=[
                        "1",
                        "966",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            "phase_2": [],
        },
        "po_4_gender_ff": {
            "phase_1": [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1600",
                    name="po_4_gender_ff.invalid_text_length",
                    description=(
                        "'Sex/gender of principal owner 4: free-form"
                        " text field for self-identified sex/gender'"
                        " must not exceed 300 characters in length."
                    ),
                    severity=Severity.ERROR,
                ),
            ],
            "phase_2": [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2143",
                    name="po_4_gender_ff.conditional_field_conflict",
                    description=(
                        "When 'sex/gender of principal owner 4: NP flag'"
                        " does not equal 1 (the applicant responded in the"
                        " free-form text field), 'sex/gender of principal"
                        " owner 4: free-form text field for self-identified"
                        " sex/gender' must be blank. When 'sex/gender of"
                        " principal owner 4: NP flag' equals 1, 'sex/gender"
                        " of principal owner 4: free-form text field for"
                        " self-identified sex/gender' must not be blank."
                    ),
                    severity=Severity.ERROR,
                    groupby="po_4_gender_flag",
                    condition_values={"1"},
                ),
            ],
        },
    }
