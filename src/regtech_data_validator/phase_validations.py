"""This is a mapping of column names and validations for each phase
Defined in validation_results.ValidationPhase.

This mapping is used to populate the schema template object and create
an instance of a PanderaSchema object for SYNTACTICAL and LOGICAL phases"""

import pandera.polars as pa

from textwrap import dedent

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
from regtech_data_validator.schema_template import get_template, get_register_template
from regtech_data_validator.validation_results import ValidationPhase

# Get separate schema templates for phase 1 and 2
phase_1_template = get_template()
phase_2_template = get_template()
register_template = get_register_template()


def get_schema_by_phase_for_lei(template: dict, phase: str, context: dict[str, str] | None = None):
    for column in get_phase_1_and_2_validations_for_lei(context):
        validations = get_phase_1_and_2_validations_for_lei(context)[column]
        template[column].checks = validations[phase]

    return pa.DataFrameSchema(template, name=phase)


def get_phase_1_schema_for_lei(context: dict[str, str] | None = None):
    return get_schema_by_phase_for_lei(phase_1_template, ValidationPhase.SYNTACTICAL, context)


def get_phase_2_schema_for_lei(context: dict[str, str] | None = None):
    return get_schema_by_phase_for_lei(phase_2_template, ValidationPhase.LOGICAL, context)


# since we process the data in chunks/batch, we need to handle all file/register
# checks separately, as a separate set of schema and checks.
def get_register_schema(context: dict[str, str] | None = None):
    for column in get_phase_2_register_validations(context):
        validations = get_phase_2_register_validations(context)[column]
        register_template[column].checks = validations[ValidationPhase.LOGICAL]

    return pa.DataFrameSchema(register_template, name=ValidationPhase.LOGICAL)


# since we process the data in chunks/batch, we need to handle all file/register
# checks separately, as a separate set of schema and checks.
def get_phase_2_register_validations(context: dict[str, str] | None = None):
    return {
        "uid": {
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_unique_column,
                    id="E3000",
                    fig_link=global_data.fig_base_url + "#4.3.1",
                    name="uid.duplicates_in_dataset",
                    description=dedent(
                        """\
                        * Any 'unique identifier' may **not** be used in more than one 
                        record within a small business lending application register.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="register",
                    related_fields="uid",
                ),
            ]
        }
    }


def get_phase_1_and_2_validations_for_lei(context: dict[str, str] | None = None):
    lei: str | None = context.get("lei", None) if context else None

    return {
        "uid": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    21,
                    45,
                    id="E0001",
                    fig_link=global_data.fig_base_url + "#4.1.1",
                    name="uid.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Unique identifier' must be at least 21 characters in 
                        length and at most 45 characters in length.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
                SBLCheck(
                    has_valid_format,
                    id="E0002",
                    fig_link=global_data.fig_base_url + "#4.1.2",
                    name="uid.invalid_text_pattern",
                    description=dedent(
                        """\
                        * 'Unique identifier' may contain any combination of numbers 
                        and/or uppercase letters (i.e., 0-9 and A-Z), and must **not** 
                        contain any other characters.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    regex="^[A-Z0-9]+$",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    string_contains,
                    id="W0003",
                    fig_link=global_data.fig_base_url + "#4.4.1",
                    name="uid.invalid_uid_lei",
                    description=dedent(
                        """\
                        * The first 20 characters of the 'unique identifier' should
                        match the Legal Entity Identifier (LEI) for the financial institution.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    containing_value=lei,
                    end_idx=20,
                ),
            ],
        },
        "app_date": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_date,
                    id="E0020",
                    fig_link=global_data.fig_base_url + "#4.1.3",
                    name="app_date.invalid_date_format",
                    description="* 'Application date' must be a real calendar date using YYYYMMDD format.",
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "app_method": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0040",
                    fig_link=global_data.fig_base_url + "#4.1.4",
                    name="app_method.invalid_enum_value",
                    description="* 'Application method' must equal 1, 2, 3, or 4.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "4",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "app_recipient": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0060",
                    fig_link=global_data.fig_base_url + "#4.1.5",
                    name="app_recipient.invalid_enum_value",
                    description="* 'Application recipient' must equal 1 or 2.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "2",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "ct_credit_product": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0080",
                    fig_link=global_data.fig_base_url + "#4.1.6",
                    name="ct_credit_product.invalid_enum_value",
                    description="* 'Credit product' must equal 1, 2, 3, 4, 5, 6, 7, 8, 977, or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [],
        },
        "ct_credit_product_ff": {
            ValidationPhase.SYNTACTICAL: [
                # FIXME: built-in Pandera checks do not support add'l params like `severity`
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0100",
                    fig_link=global_data.fig_base_url + "#4.1.7",
                    name="ct_credit_product_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Free-form text field for other credit products' must **not** 
                        exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                )
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2000",
                    fig_link=global_data.fig_base_url + "#4.2.1",
                    name="ct_credit_product_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'credit product' does **not** equal 977 (other), 
                        'free-form text field for other credit products' must be blank.
                        * When 'credit product' equals 977, 'free-form text field for 
                        other credit products' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="ct_credit_product",
                    condition_values={"977"},
                ),
            ],
        },
        "ct_guarantee": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0120",
                    fig_link=global_data.fig_base_url + "#4.1.8",
                    name="ct_guarantee.invalid_enum_value",
                    description=dedent(
                        """\
                        * Each value in 'type of guarantee' (separated by semicolons) 
                        must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 977, or 999.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_valid_value_count,
                    id="E0121",
                    fig_link=global_data.fig_base_url + "#4.1.9",
                    name="ct_guarantee.invalid_number_of_values",
                    description=dedent(
                        """\
                        * 'Type of guarantee' must contain at least one and 
                        at most five values, separated by semicolons.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    min_length=1,
                    max_length=5,
                ),
                SBLCheck(
                    is_unique_in_field,
                    id="W0123",
                    fig_link=global_data.fig_base_url + "#4.4.3",
                    name="ct_guarantee.duplicates_in_field",
                    description="* 'Type of guarantee' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0122",
                    fig_link=global_data.fig_base_url + "#4.4.2",
                    name="ct_guarantee.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'type of guarantee' contains 999 (no guarantee), 
                        'type of guarantee' should **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"999"},
                ),
            ],
        },
        "ct_guarantee_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0140",
                    fig_link=global_data.fig_base_url + "#4.1.10",
                    name="ct_guarantee_ff.invalid_text_length",
                    description="* 'Free-form text field for other guarantee' must **not** exceed 300 characters in length.",
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2001",
                    fig_link=global_data.fig_base_url + "#4.2.2",
                    name="ct_guarantee_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'type of guarantee' does **not** contain 977 (other), 'free-form text field for other guarantee' must be blank.
                        * When 'type of guarantee' contains 977, 'free-form text field for other guarantee' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="ct_guarantee",
                    condition_values={"977"},
                ),
                SBLCheck(
                    has_valid_multi_field_value_count,
                    id="W2002",
                    fig_link=global_data.fig_base_url + "#4.5.1",
                    name="ct_guarantee_ff.multi_invalid_number_of_values",
                    description=dedent(
                        """\
                        * 'Type of guarantee' and 'free-form text field for other guarantee' 
                        combined should **not** contain more than five values. Code 977 (other), 
                        within 'type of guarantee', does **not** count toward the maximum number 
                        of values for the purpose of this validation check.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="multi-field",
                    related_fields="ct_guarantee",
                    ignored_values={"977"},
                    max_length=5,
                ),
            ],
        },
        "ct_loan_term_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0160",
                    fig_link=global_data.fig_base_url + "#4.1.11",
                    name="ct_loan_term_flag.invalid_enum_value",
                    description="* 'Loan term: NA/NP flag' must equal 900, 988, or 999.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "900",
                        "988",
                        "999",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2003",
                    fig_link=global_data.fig_base_url + "#4.2.3",
                    name="ct_loan_term_flag.enum_value_conflict",
                    description=dedent(
                        """\
                        * When 'credit product' equals 1 (term loan - unsecured) or 2 (term loan - secured), 
                        'loan term: NA/NP flag' must **not** equal 999 (not applicable).
                        * When 'credit product' equals 988 (not provided by applicant and otherwise undetermined), 
                        'loan term: NA/NP flag' must equal 999.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="ct_credit_product",
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
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0180",
                    fig_link=global_data.fig_base_url + "#4.1.12",
                    name="ct_loan_term.invalid_numeric_format",
                    description="* When present, 'loan term' must be a whole number.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                    is_whole=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2004",
                    fig_link=global_data.fig_base_url + "#4.2.4",
                    name="ct_loan_term.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'loan term: NA/NP flag' does **not** equal 900 (applicable and reported), 'loan term' must be blank.
                        * When 'loan term: NA/NP flag' equals 900, 'loan term' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="ct_loan_term_flag",
                    condition_values={"900"},
                ),
                SBLCheck(
                    is_greater_than_or_equal_to,
                    id="E0181",
                    fig_link=global_data.fig_base_url + "#4.1.13",
                    name="ct_loan_term.invalid_numeric_value",
                    description="* When present, 'loan term' must be greater than or equal to 1.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    min_value="1",
                    accept_blank=True,
                ),
                SBLCheck(
                    is_less_than,
                    id="W0182",
                    fig_link=global_data.fig_base_url + "#4.4.4",
                    name="ct_loan_term.unreasonable_numeric_value",
                    description="* When present, 'loan term' should be less than 1200 (100 years).",
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    max_value="1200",
                    accept_blank=True,
                ),
            ],
        },
        "credit_purpose": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0200",
                    fig_link=global_data.fig_base_url + "#4.1.14",
                    name="credit_purpose.invalid_enum_value",
                    description=dedent(
                        """\
                        * Each value in 'credit purpose' (separated by semicolons) 
                        must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 977, 988, or 999.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_valid_value_count,
                    id="E0201",
                    fig_link=global_data.fig_base_url + "#4.1.15",
                    name="credit_purpose.invalid_number_of_values",
                    description=dedent(
                        """\
                        * 'Credit purpose' must contain at least one and 
                        at most three values, separated by semicolons.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    min_length=1,
                    max_length=3,
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0202",
                    fig_link=global_data.fig_base_url + "#4.4.5",
                    name="credit_purpose.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'credit purpose' contains 988 (not provided by applicant and 
                        otherwise undetermined) or 999 (not applicable), 'credit purpose' 
                        should **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={
                        "988",
                        "999",
                    },
                ),
                SBLCheck(
                    is_unique_in_field,
                    id="W0203",
                    fig_link=global_data.fig_base_url + "#4.4.6",
                    name="credit_purpose.duplicates_in_field",
                    description="* 'Credit purpose' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
            ],
        },
        "credit_purpose_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0220",
                    fig_link=global_data.fig_base_url + "#4.1.16",
                    name="credit_purpose_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Free-form text field for other credit purpose' must 
                        **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2005",
                    fig_link=global_data.fig_base_url + "#4.2.5",
                    name="credit_purpose_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'credit purpose' does **not** contain 977 (other), 'free-form text 
                        field for other credit purpose' must be blank.
                        * When 'credit purpose' contains 977 (other), 'free-form text 
                        field for other credit purpose' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="credit_purpose",
                    condition_values={"977"},
                ),
                SBLCheck(
                    has_valid_multi_field_value_count,
                    id="W2006",
                    fig_link=global_data.fig_base_url + "#4.5.2",
                    name="credit_purpose_ff.multi_invalid_number_of_values",
                    description=dedent(
                        """\
                        * 'Credit purpose' and 'free-form text field for other credit 
                        purpose' combined should **not** contain more than three values. 
                        Code 977 (other), within 'credit purpose', does **not** count 
                        toward the maximum number of values for the purpose of 
                        this validation check.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="multi-field",
                    related_fields="credit_purpose",
                    ignored_values={"977"},
                    max_length=3,
                ),
            ],
        },
        "amount_applied_for_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0240",
                    fig_link=global_data.fig_base_url + "#4.1.17",
                    name="amount_applied_for_flag.invalid_enum_value",
                    description="* 'Amount applied For: NA/NP flag' must equal 900, 988, or 999.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "900",
                        "988",
                        "999",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "amount_applied_for": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0260",
                    fig_link=global_data.fig_base_url + "#4.1.18",
                    name="amount_applied_for.invalid_numeric_format",
                    description="* When present, 'amount applied for' must be a numeric value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2007",
                    fig_link=global_data.fig_base_url + "#4.2.6",
                    name="amount_applied_for.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'amount applied for: NA/NP flag' does **not** equal 
                        900 (applicable and reported), 'amount applied for' must be blank.
                        * When 'amount applied for: NA/NP flag' equals 900, 
                        'amount applied for' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="amount_applied_for_flag",
                    condition_values={"900"},
                ),
                SBLCheck(
                    is_greater_than,
                    id="E0261",
                    fig_link=global_data.fig_base_url + "#4.1.19",
                    name="amount_applied_for.invalid_numeric_value",
                    description="* When present, 'amount applied for' must be greater than 0.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    min_value="0",
                    accept_blank=True,
                ),
            ],
        },
        "amount_approved": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0280",
                    fig_link=global_data.fig_base_url + "#4.1.20",
                    name="amount_approved.invalid_numeric_format",
                    description="* When present, 'amount approved or originated' must be a numeric value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_greater_than,
                    id="E0281",
                    fig_link=global_data.fig_base_url + "#4.1.21",
                    name="amount_approved.invalid_numeric_value",
                    description="* When present, 'amount approved or originated' must be greater than 0.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    min_value="0",
                    accept_blank=True,
                ),
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2008",
                    fig_link=global_data.fig_base_url + "#4.2.7",
                    name="amount_approved.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'action taken' does **not** equal 1 (originated) or 
                        2 (approved but not accepted), 'amount approved or originated' must be blank.
                        * When 'action taken' equals 1 or 2, 'amount approved or originated' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="action_taken",
                    condition_values={"1", "2"},
                ),
            ],
        },
        "action_taken": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0300",
                    fig_link=global_data.fig_base_url + "#4.1.22",
                    name="action_taken.invalid_enum_value",
                    description="* 'Action taken' must equal 1, 2, 3, 4, or 5.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_valid_fieldset_pair,
                    id="E2014",
                    fig_link=global_data.fig_base_url + "#4.2.11",
                    name="pricing_all.conditional_fieldset_conflict",
                    description=dedent(
                        """\
                        When 'action taken' equals 3 (denied), 4 (withdrawn by applicant), or 5 (incomplete), the 
                        following fields must all equal 999 (not applicable):
                        * 'Interest rate type'
                        * 'MCA/sales-based: additional cost for merchant cash advances or other sales-based financing: NA flag'
                        * 'Prepayment penalty could be imposed'
                        * 'Prepayment penalty exists'
                        
                        And the following fields must all be blank:
                        
                        * 'Total origination charges'
                        * 'Amount of total broker fees'
                        * 'Initial annual charges'
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields=[
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
                    fig_link=global_data.fig_base_url + "#4.2.12",
                    name="pricing_charges.conditional_fieldset_conflict",
                    description=dedent(
                        """\
                        When 'action taken' equals 1 (originated) or 2 (approved but not accepted), the following 
                        fields all must **not** be blank:
                        * 'Total origination charges'
                        * 'Amount of total broker fees'
                        * 'Initial annual charges'
                        
                        And the following fields must **not** equal 999 (not applicable):
                        
                        * 'Prepayment penalty could be imposed'
                        * 'Prepayment penalty exists'"
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields=[
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
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_date,
                    id="E0320",
                    fig_link=global_data.fig_base_url + "#4.1.23",
                    name="action_taken_date.invalid_date_format",
                    description="* 'Action taken date' must be a real calendar date using YYYYMMDD format.",
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_date_in_range,
                    id="E0321",
                    fig_link=global_data.fig_base_url + "#4.1.24",
                    name="action_taken_date.invalid_date_value",
                    description=dedent(
                        """\
                        * The date indicated by 'action taken date' must occur within the 
                        current reporting period: October 1, 2024 to December 31, 2024.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    start_date_value="20241001",
                    end_date_value="20241231",
                ),
                SBLCheck(
                    is_date_after,
                    id="E2009",
                    fig_link=global_data.fig_base_url + "#4.2.8",
                    name="action_taken_date.date_value_conflict",
                    description="* The date indicated by 'action taken date' must occur on or after 'application date'.",
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="app_date",
                ),
                SBLCheck(
                    is_date_before_in_days,
                    id="W2010",
                    fig_link=global_data.fig_base_url + "#4.5.3",
                    name="action_taken_date.unreasonable_date_value",
                    description=dedent(
                        """\
                        * The date indicated by 'application date' should
                        generally be less than two years (730 days) before 
                        'action taken date'.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="multi-field",
                    related_fields="app_date",
                    days_value=730,
                ),
            ],
        },
        "denial_reasons": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0340",
                    fig_link=global_data.fig_base_url + "#4.1.25",
                    name="denial_reasons.invalid_enum_value",
                    description=dedent(
                        """\
                        * Each value in 'denial reason(s)' (separated by semicolons) 
                        must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 977, or 999.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_valid_value_count,
                    id="E0341",
                    fig_link=global_data.fig_base_url + "#4.1.26",
                    name="denial_reasons.invalid_number_of_values",
                    description=dedent(
                        """\
                        * 'Denial reason(s)' must contain at least one and 
                        at most four values, separated by semicolons.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    min_length=1,
                    max_length=4,
                ),
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2011",
                    fig_link=global_data.fig_base_url + "#4.2.9",
                    name="denial_reasons.enum_value_conflict",
                    description=dedent(
                        """\
                        * When 'action taken' equals 3, 'denial reason(s)' must **not** contain 999.
                        * When 'action taken' does **not** equal 3 (denied), 'denial reason(s)' must equal 999 (not applicable).
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="action_taken",
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
                    fig_link=global_data.fig_base_url + "#4.4.7",
                    name="denial_reasons.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'denial reason(s)' contains 999 (not applicable), 
                        'denial reason(s)' should **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"999"},
                ),
                SBLCheck(
                    is_unique_in_field,
                    id="W0341",
                    fig_link=global_data.fig_base_url + "#4.4.8",
                    name="denial_reasons.duplicates_in_field",
                    description="* 'Denial reason(s)' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
            ],
        },
        "denial_reasons_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    min_value=0,
                    max_value=300,
                    id="E0360",
                    fig_link=global_data.fig_base_url + "#4.1.27",
                    name="denial_reasons_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Free-form text field for other denial reason(s)' must 
                        **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2012",
                    fig_link=global_data.fig_base_url + "#4.2.10",
                    name="denial_reasons_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'denial reason(s)' does **not** contain 977 (other), 
                        field 'free-form text field for other denial reason(s)' must be blank.
                        * When 'denial reason(s)' contains 977, 'free-form text field for other 
                        denial reason(s)' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="denial_reasons",
                    condition_values={"977"},
                ),
                SBLCheck(
                    has_valid_multi_field_value_count,
                    id="W2013",
                    fig_link=global_data.fig_base_url + "#4.5.4",
                    name="denial_reasons_ff.multi_invalid_number_of_values",
                    description=dedent(
                        """\
                        * 'Denial reason(s)' and 'free-form text field for other 
                        denial reason(s)' combined should **not** contain more than 
                        four values. Code 977 (other), within 'Denial reason(s)', 
                        does **not** count toward the maximum number of values for 
                        the purpose of this validation check.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="multi-field",
                    related_fields="denial_reasons",
                    ignored_values={"977"},
                    max_length=4,
                ),
            ],
        },
        "pricing_interest_rate_type": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0380",
                    fig_link=global_data.fig_base_url + "#4.1.28",
                    name="pricing_interest_rate_type.invalid_enum_value",
                    description="* 'Interest rate type' must equal 1, 2, 3, 4, 5, 6, or 999.",
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [],
        },
        "pricing_init_rate_period": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0400",
                    fig_link=global_data.fig_base_url + "#4.1.29",
                    name="pricing_init_rate_period.invalid_numeric_format",
                    description=dedent(
                        """\
                        * When present, 'adjustable rate transaction: initial rate period' must be a whole number.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                    is_whole=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2016",
                    fig_link=global_data.fig_base_url + "#4.2.13",
                    name="pricing_init_rate_period.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'interest rate type' does **not** equal 3 (initial rate period > 12 months, adjustable interest),
                        4 (initial rate period > 12 months, fixed interest), 5 (initial rate period <= 12 months, adjustable interest), 
                        or 6 (initial rate period <= 12 months, fixed interest), 'initial rate period' must be blank.
                        * When 'interest rate type' equals 3, 4, 5, or 6, 'initial rate period' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="pricing_interest_rate_type",
                    condition_values={"3", "4", "5", "6"},
                ),
                SBLCheck(
                    is_greater_than,
                    id="E0401",
                    fig_link=global_data.fig_base_url + "#4.1.30",
                    name="pricing_init_rate_period.invalid_numeric_value",
                    description=dedent(
                        """\
                        * When present, 'adjustable rate transaction: initial rate period' must be greater than 0.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    min_value="0",
                    accept_blank=True,
                ),
            ],
        },
        "pricing_fixed_rate": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0420",
                    fig_link=global_data.fig_base_url + "#4.1.31",
                    name="pricing_fixed_rate.invalid_numeric_format",
                    description="* When present, 'fixed rate: interest rate' must be a numeric value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2017",
                    fig_link=global_data.fig_base_url + "#4.2.14",
                    name="pricing_fixed_rate.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'interest rate type' does **not** equal 2 (fixed interest rate, no initial rate period), 
                        4 (initial rate period > 12 months, fixed interest rate), or 6 (initial rate period <= 12 months, fixed 
                        interest rate), 'fixed rate: interest rate' must be blank.
                        * When 'interest rate type' equals 2, 4, or 6, 'fixed rate: interest rate' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="pricing_interest_rate_type",
                    condition_values={"2", "4", "6"},
                ),
                SBLCheck(
                    is_greater_than,
                    id="W0420",
                    fig_link=global_data.fig_base_url + "#4.4.9",
                    name="pricing_fixed_rate.unreasonable_numeric_value",
                    description="* When present, 'fixed rate: interest rate' should generally be greater than 0.1.",
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    min_value="0.1",
                    accept_blank=True,
                ),
            ],
        },
        "pricing_adj_margin": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0440",
                    fig_link=global_data.fig_base_url + "#4.1.32",
                    name="pricing_adj_margin.invalid_numeric_format",
                    description="* When present, 'adjustable rate transaction: margin' must be a numeric value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2018",
                    fig_link=global_data.fig_base_url + "#4.2.15",
                    name="pricing_adj_margin.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'interest rate type' does **not** equal 1 (adjustable interest rate, no initial rate period), 
                        3 (initial rate period > 12 months, adjustable interest rate), or 
                        5 (initial rate period <= 12 months, adjustable 
                        interest rate), 'adjustable rate transaction: margin' must be blank.
                        * When 'interest rate type' equals 1, 3, or 5, 'adjustable rate transaction: margin' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="pricing_interest_rate_type",
                    condition_values={"1", "3", "5"},
                ),
                SBLCheck(
                    is_greater_than,
                    id="W0441",
                    fig_link=global_data.fig_base_url + "#4.4.10",
                    name="pricing_adj_margin.unreasonable_numeric_value",
                    description=dedent(
                        """\
                        * When present, 'adjustable rate transaction: margin' should generally be greater than 0.1.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    min_value="0.1",
                    accept_blank=True,
                ),
            ],
        },
        "pricing_adj_index_name": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0460",
                    fig_link=global_data.fig_base_url + "#4.1.33",
                    name="pricing_adj_index_name.invalid_enum_value",
                    description=dedent(
                        """\
                        * 'Adjustable rate transaction: index name' must equal 
                        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 977, or 999.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2019",
                    fig_link=global_data.fig_base_url + "#4.2.16",
                    name="pricing_adj_index_name.enum_value_conflict",
                    description=dedent(
                        """\
                        * When 'interest rate type' does **not** equal 1 (adjustable interest rate, no initial rate period), 
                        3 (initial rate period > 12 months, adjustable interest rate), or 5 (initial rate period <= 12 months, 
                        adjustable interest rate), 'adjustable rate transaction: index name' must equal 999.
                        * When 'interest rate type' equals 1, 3, or 5, 'adjustable rate transaction: index name' must 
                        **not** equal 999.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="pricing_interest_rate_type",
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
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    min_value=0,
                    max_value=300,
                    id="E0480",
                    fig_link=global_data.fig_base_url + "#4.1.34",
                    name="pricing_adj_index_name_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Adjustable rate transaction: index name: other' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2020",
                    fig_link=global_data.fig_base_url + "#4.2.17",
                    name="pricing_adj_index_name_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'adjustable rate transaction: index name' does **not** equal 977 (other), 
                        'adjustable rate transaction: index name: other' must be blank.
                        * When 'adjustable rate transaction: index name' equals 977, 'adjustable rate transaction: 
                        index name: other' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="pricing_adj_index_name",
                    condition_values={"977"},
                ),
            ],
        },
        "pricing_adj_index_value": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0500",
                    fig_link=global_data.fig_base_url + "#4.1.35",
                    name="pricing_adj_index_value.invalid_numeric_format",
                    description="* When present, 'adjustable rate transaction: index value' must be a numeric value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2021",
                    fig_link=global_data.fig_base_url + "#4.2.18",
                    name="pricing_adj_index_value.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'interest rate type' does **not** equal 1 (adjustable interest rate, no initial rate period), 
                        or 3 (initial rate period > 12 months, adjustable interest rate), 'adjustable rate transaction: index value' 
                        must be blank.
                        * When 'interest rate type' equals 1 or 3, 'adjustable rate transaction: index value' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="pricing_interest_rate_type",
                    condition_values={"1", "3"},
                ),
            ],
        },
        "pricing_origination_charges": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0520",
                    fig_link=global_data.fig_base_url + "#4.1.36",
                    name="pricing_origination_charges.invalid_numeric_format",
                    description="* When present, 'total origination charges' must be a numeric value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "pricing_broker_fees": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0540",
                    fig_link=global_data.fig_base_url + "#4.1.37",
                    name="pricing_broker_fees.invalid_numeric_format",
                    description="* When present, 'amount of total broker fees' must be a numeric value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "pricing_initial_charges": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0560",
                    fig_link=global_data.fig_base_url + "#4.1.38",
                    name="pricing_initial_charges.invalid_numeric_format",
                    description="* When present, 'initial annual charges' must be a numeric value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "pricing_mca_addcost_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0580",
                    fig_link=global_data.fig_base_url + "#4.1.39",
                    name="pricing_mca_addcost_flag.invalid_enum_value",
                    description=dedent(
                        """\
                        * 'MCA/sales-based: additional cost for merchant cash advances or 
                        other sales-based financing: NA flag' must equal 900 or 999.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "900",
                        "999",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2022",
                    fig_link=global_data.fig_base_url + "#4.2.19",
                    name="pricing_mca_addcost_flag.enum_value_conflict",
                    description=dedent(
                        """\
                        * When 'credit product' does **not** equal 7 (merchant cash 
                        advance), 8 (other sales-based financing transaction) 
                        or 977 (other), 'MCA/sales-based: additional cost for 
                        merchant cash advances or other sales-based financing: 
                        NA flag' must be 999 (not applicable).
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="ct_credit_product",
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
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0600",
                    fig_link=global_data.fig_base_url + "#4.1.40",
                    name="pricing_mca_addcost.invalid_numeric_format",
                    description=dedent(
                        """\
                        * When present, 'MCA/sales-based: additional cost for merchant cash 
                        advances or other sales-based financing' must be a numeric value.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2023",
                    fig_link=global_data.fig_base_url + "#4.2.20",
                    name="pricing_mca_addcost.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'MCA/sales-based: additional cost for merchant cash advances or 
                        other sales-based financing: NA flag' does **not** equal 900 (applicable), 
                        'MCA/sales-based: additional cost for merchant cash advances or other sales-based financing' 
                        must be blank.
                        * When 'MCA/sales-based: additional cost for merchant cash advances or 
                        other sales-based financing: NA flag' equals 900, 'MCA/sales-based: additional cost for 
                        merchant cash advances or other sales-based financing' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="pricing_mca_addcost_flag",
                    condition_values={"900"},
                ),
            ],
        },
        "pricing_prepenalty_allowed": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0620",
                    fig_link=global_data.fig_base_url + "#4.1.41",
                    name="pricing_prepenalty_allowed.invalid_enum_value",
                    description="* Prepayment penalty could be imposed' must equal 1, 2, or 999.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "2",
                        "999",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "pricing_prepenalty_exists": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0640",
                    fig_link=global_data.fig_base_url + "#4.1.42",
                    name="pricing_prepenalty_exists.invalid_enum_value",
                    description="* 'Prepayment penalty exists' must equal 1, 2, or 999.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "2",
                        "999",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "census_tract_adr_type": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0660",
                    fig_link=global_data.fig_base_url + "#4.1.43",
                    name="census_tract_adr_type.invalid_enum_value",
                    description="* 'Census tract: type of address' must equal 1, 2, 3, or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "988",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "census_tract_number": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    has_correct_length,
                    id="E0680",
                    fig_link=global_data.fig_base_url + "#4.1.44",
                    name="census_tract_number.invalid_text_length",
                    description="* When present, 'census tract: tract number' must be a GEOID with exactly 11 digits.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accepted_length=11,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_valid_enum_pair,
                    id="E2024",
                    fig_link=global_data.fig_base_url + "#4.2.21",
                    name="census_tract_number.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'census tract: type of address' equals 988 (not provided by applicant 
                        and otherwise undetermined), 'census tract: tract number' must be blank. 
                        * When 'census tract: type of address' equals 1 (address or location where 
                        the loan proceeds will principally be applied), 2 (address or location of 
                        borrower's main office or headquarters), or 3 (another address or location 
                        associated with the applicant), 'census tract: tract number' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="census_tract_adr_type",
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
                    id="W0680",
                    fig_link=global_data.fig_base_url + "#4.4.11",
                    name="census_tract_number.invalid_geoid",
                    description=dedent(
                        """\
                        * When present, 'census tract: tract number' should be a valid 
                        census tract GEOID as defined by the U.S. Census Bureau.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                    codes=global_data.census_geoids,
                ),
            ],
        },
        "gross_annual_revenue_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0700",
                    fig_link=global_data.fig_base_url + "#4.1.45",
                    name="gross_annual_revenue_flag.invalid_enum_value",
                    description="* 'Gross annual revenue: NP flag' must equal 900 or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "900",
                        "988",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "gross_annual_revenue": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0720",
                    fig_link=global_data.fig_base_url + "#4.1.46",
                    name="gross_annual_revenue.invalid_numeric_format",
                    description="* When present, 'gross annual revenue' must be a numeric value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2025",
                    fig_link=global_data.fig_base_url + "#4.2.22",
                    name="gross_annual_revenue.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'gross annual revenue: NP flag' does **not** equal 900 (reported), 
                        'gross annual revenue' must be blank.
                        * When 'gross annual revenue: NP flag' equals 900, 'gross annual revenue' 
                        must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="gross_annual_revenue_flag",
                    condition_values={"900"},
                ),
            ],
        },
        "naics_code_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0740",
                    fig_link=global_data.fig_base_url + "#4.1.47",
                    name="naics_code_flag.invalid_enum_value",
                    description=dedent(
                        """\
                        * 'North American Industry Classification System (NAICS) code: NP flag' 
                        must equal 900 or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "900",
                        "988",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "naics_code": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0761",
                    fig_link=global_data.fig_base_url + "#4.1.49",
                    name="naics_code.invalid_naics_format",
                    description=dedent(
                        """\
                        * 'North American Industry Classification System (NAICS) code' 
                        may only contain numeric characters.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_correct_length,
                    id="E0760",
                    fig_link=global_data.fig_base_url + "#4.1.48",
                    name="naics_code.invalid_text_length",
                    description=dedent(
                        """\
                        * When present, 'North American Industry Classification System (NAICS) code' 
                        must be three digits in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accepted_length=3,
                    accept_blank=True,
                ),
                SBLCheck(
                    is_valid_code,
                    id="W0762",
                    fig_link=global_data.fig_base_url + "#4.4.12",
                    name="naics_code.invalid_naics_value",
                    description=dedent(
                        """\
                        * When present, 'North American Industry Classification System (NAICS) code' 
                        should be a valid NAICS code.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                    codes=global_data.naics_codes,
                ),
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2026",
                    fig_link=global_data.fig_base_url + "#4.2.23",
                    name="naics_code.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'North American Industry Classification System (NAICS) code: NP flag' 
                        does **not** equal 900 (reported), 'North American Industry Classification 
                        System (NAICS) code' must be blank.
                        * When 'North American Industry Classification System (NAICS) code: NP flag' 
                        equals 900, 'North American Industry Classification System (NAICS) code' 
                        must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="naics_code_flag",
                    condition_values={"900"},
                ),
            ],
        },
        "number_of_workers": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0780",
                    fig_link=global_data.fig_base_url + "#4.1.50",
                    name="number_of_workers.invalid_enum_value",
                    description="* 'Number of workers' must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [],
        },
        "time_in_business_type": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0800",
                    fig_link=global_data.fig_base_url + "#4.1.51",
                    name="time_in_business_type.invalid_enum_value",
                    description="* 'Time in business: type of response' must equal 1, 2, 3, or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "2",
                        "3",
                        "988",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "time_in_business": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_number,
                    id="E0820",
                    fig_link=global_data.fig_base_url + "#4.1.52",
                    name="time_in_business.invalid_numeric_format",
                    description="* When present, 'time in business' must be a whole number.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    accept_blank=True,
                    is_whole=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_greater_than_or_equal_to,
                    id="E0821",
                    fig_link=global_data.fig_base_url + "#4.1.53",
                    name="time_in_business.invalid_numeric_value",
                    description="* When present, 'time in business' must be greater than or equal to 0.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    element_wise=True,
                    min_value="0",
                    accept_blank=True,
                ),
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2027",
                    fig_link=global_data.fig_base_url + "#4.2.24",
                    name="time_in_business.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'time in business: type of response' does **not** equal 1 (the number of years an applicant has been 
                        in business is collected or obtained by the financial institution), 'time in business' must be blank.
                        * When 'time in business: type of response' equals 1, 'time in business' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="time_in_business_type",
                    condition_values={"1"},
                ),
            ],
        },
        "business_ownership_status": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0840",
                    fig_link=global_data.fig_base_url + "#4.1.54",
                    name="business_ownership_status.invalid_enum_value",
                    description=dedent(
                        """\
                        * Each value in 'business ownership status' (separated by semicolons) 
                        must equal 1, 2, 3, 955, 966, or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_valid_value_count,
                    id="E0841",
                    fig_link=global_data.fig_base_url + "#4.1.55",
                    name="business_ownership_status.invalid_number_of_values",
                    description="* 'Business ownership status' must contain at least one value.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    min_length=1,
                ),
                SBLCheck(
                    is_unique_in_field,
                    id="W0842",
                    fig_link=global_data.fig_base_url + "#4.4.13",
                    name="business_ownership_status.duplicates_in_field",
                    description="* 'Business ownership status' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0843",
                    fig_link=global_data.fig_base_url + "#4.4.14",
                    name="business_ownership_status.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'business ownership status' contains 966
                        (the applicant responded that they did not wish to 
                        provide this information) or 988 (not provided by applicant), 
                        'business ownership status' should **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "num_principal_owners_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0860",
                    fig_link=global_data.fig_base_url + "#4.1.56",
                    name="num_principal_owners_flag.invalid_enum_value",
                    description="* 'Number of principal owners: NP flag' must equal 900 or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "900",
                        "988",
                    ],
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "num_principal_owners": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0880",
                    fig_link=global_data.fig_base_url + "#4.1.57",
                    name="num_principal_owners.invalid_enum_value",
                    description="* When present, 'number of principal owners' must equal 0, 1, 2, 3, or 4.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=["0", "1", "2", "3", "4"],
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2028",
                    fig_link=global_data.fig_base_url + "#4.2.25",
                    name="num_principal_owners.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'number of principal owners: NP flag' does **not** equal 900 (reported), 
                        'number of principal owners' must be blank.
                        * When 'number of principal owners: NP flag' equals 900, 'number of principal 
                        owners' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="num_principal_owners_flag",
                    condition_values={"900"},
                ),
                SBLCheck(
                    has_valid_fieldset_pair,
                    id="W2035",
                    fig_link=global_data.fig_base_url + "#4.5.5",
                    name="po_demographics_0.conditional_fieldset_conflict",
                    description=dedent(
                        """\
                        * When 'number of principal owners' equals 0 or is blank, 
                        demographic fields for principal owners 1, 2, 3, and 4 
                        should be blank.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="multi-field",
                    related_fields=[
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
                    fig_link=global_data.fig_base_url + "#4.5.6",
                    name="po_demographics_1.conditional_fieldset_conflict",
                    description=dedent(
                        """\
                        * When 'number of principal owners' equals 1, 'ethnicity of principal owner 1', 
                        'race of principal owner 1', and 'sex/gender of principal owner 1: NP flag' 
                        should **not** be blank.
                        * Demographic fields for principal owners 2, 3, and 4 should be blank.
                    """
                    ),
                    severity=Severity.WARNING,
                    scope="multi-field",
                    related_fields=[
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
                    fig_link=global_data.fig_base_url + "#4.5.7",
                    name="po_demographics_2.conditional_fieldset_conflict",
                    description=dedent(
                        """\
                        * When 'number of principal owners' equals 2, 'ethnicity of principal owner 1 and 2', 
                        'race of principal owner 1 and 2', and 'sex/gender of principal owner 1 and 2: 
                        NP flag' should **not** be blank.
                        * Demographic fields for principal owners 3 and 4 should be blank.
                    """
                    ),
                    severity=Severity.WARNING,
                    scope="multi-field",
                    related_fields=[
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
                    fig_link=global_data.fig_base_url + "#4.5.8",
                    name="po_demographics_3.conditional_fieldset_conflict",
                    description=dedent(
                        """\
                        * When 'number of principal owners' equals 3, 'ethnicity of principal owner 1, 2, and 3', 
                        'race of principal owner 1, 2, and 3', and 'sex/gender of principal owner 1, 2, 
                        and 3: NP flag' should **not** be blank.
                        * Demographic fields for principal owner 4 should be blank.
                    """
                    ),
                    severity=Severity.WARNING,
                    scope="multi-field",
                    related_fields=[
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
                    fig_link=global_data.fig_base_url + "#4.5.9",
                    name="po_demographics_4.conditional_fieldset_conflict",
                    description=dedent(
                        """\
                        * When 'number of principal owners' equals 4, 'ethnicity of principal owner 1, 2, 3, and 4', 
                        'race of principal owner 1, 2, 3, and 4', and 'sex/gender of principal owner 1, 2, 3, and 4: NP flag' 
                        should **not** be blank.
                    """
                    ),
                    severity=Severity.WARNING,
                    scope="multi-field",
                    related_fields=[
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
        "po_1_ethnicity": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0900",
                    fig_link=global_data.fig_base_url + "#4.1.58",
                    name="po_1_ethnicity.invalid_enum_value",
                    description=dedent(
                        """\
                        * When present, each value in 'ethnicity of principal owner 1' 
                        (separated by semicolons) must equal 1, 11, 12, 13, 14, 2, 966, 977, or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_unique_in_field,
                    id="W0901",
                    fig_link=global_data.fig_base_url + "#4.4.15",
                    name="po_1_ethnicity.duplicates_in_field",
                    description="* 'Ethnicity of principal owner 1' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0902",
                    fig_link=global_data.fig_base_url + "#4.4.16",
                    name="po_1_ethnicity.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'ethnicity of principal owner 1' contains 966 
                        (the applicant responded that they did not wish to provide this information) or 
                        988 (not provided by applicant), 'ethnicity of principal owner: 1' should **not** 
                        contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_1_ethnicity_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0920",
                    fig_link=global_data.fig_base_url + "#4.1.59",
                    name="po_1_ethnicity_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Ethnicity of principal owner 1: free-form text field for 
                        other Hispanic or Latino' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2040",
                    fig_link=global_data.fig_base_url + "#4.2.26",
                    name="po_1_ethnicity_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'ethnicity of principal owner 1' does **not** contain 977 (the applicant responded in the 
                        free-form text field), 'ethnicity of principal owner 1: free-form text field for other Hispanic 
                        or Latino' must be blank.
                        * When 'ethnicity of principal owner 1' contains 977, 'ethnicity of principal owner 1: free-form 
                        text field for other Hispanic or Latino' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_1_ethnicity",
                    condition_values={"977"},
                ),
            ],
        },
        "po_1_race": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E0940",
                    fig_link=global_data.fig_base_url + "#4.1.60",
                    name="po_1_race.invalid_enum_value",
                    description=dedent(
                        """\
                        * When present, each value in 'race of principal owner 1' 
                        (separated by semicolons) must equal 1, 2, 21, 22, 23, 24, 
                        25, 26, 27, 3, 31, 32, 33, 34, 35, 36, 37, 4, 41, 42, 43, 
                        44, 5, 966, 971, 972, 973, 974, or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_unique_in_field,
                    id="W0941",
                    fig_link=global_data.fig_base_url + "#4.4.17",
                    name="po_1_race.duplicates_in_field",
                    description="* 'Race of principal owner 1' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W0942",
                    fig_link=global_data.fig_base_url + "#4.4.18",
                    name="po_1_race.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'race of principal owner 1' contains 966 (the applicant responded that 
                        they did not wish to provide this information) or 988 (not provided by applicant), 
                        'race of principal owner: 1' should **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_1_race_anai_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0960",
                    fig_link=global_data.fig_base_url + "#4.1.61",
                    name="po_1_race_anai_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 1: free-form text field for 
                        American Indian or Alaska Native Enrolled or Principal Tribe' 
                        must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2060",
                    fig_link=global_data.fig_base_url + "#4.2.30",
                    name="po_1_race_anai_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 1' does **not** contain 971 (the applicant responded in 
                        the free-form text field for American Indian or Alaska Native Enrolled or Principal Tribe), 
                        'race of principal owner 1: free-form text field for American Indian or Alaska Native 
                        Enrolled or Principal Tribe' must be blank.
                        * When 'race of principal owner 1' contains 971, 'race of principal owner 1: free-form text field 
                        for American Indian or Alaska Native Enrolled or Principal Tribe' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_1_race",
                    condition_values={"971"},
                ),
            ],
        },
        "po_1_race_asian_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E0980",
                    fig_link=global_data.fig_base_url + "#4.1.62",
                    name="po_1_race_asian_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 1: free-form text field for 
                        other Asian' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2080",
                    fig_link=global_data.fig_base_url + "#4.2.34",
                    name="po_1_race_asian_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 1' does **not** contain 972 (the applicant responded in the free-form text 
                        field for other Asian race), 'race of principal owner 1: free-form text field for other Asian' must be blank.
                        * When 'race of principal owner 1' contains 972, 'race of principal owner 1: free-form text field 
                        for other Asian' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_1_race",
                    condition_values={"972"},
                ),
            ],
        },
        "po_1_race_baa_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1000",
                    fig_link=global_data.fig_base_url + "#4.1.63",
                    name="po_1_race_baa_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 1: free-form text field for other 
                        Black or African American' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2100",
                    fig_link=global_data.fig_base_url + "#4.2.38",
                    name="po_1_race_baa_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 1' does **not** contain 973 (the applicant 
                        responded in the free-form text field for other Black or African race), 
                        'race of principal owner 1: free-form text field for other Black or African 
                        American' must be blank.
                        * When 'race of principal owner 1' contains 973, 'race of principal owner 1: 
                        free-form text field for other Black or African American' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_1_race",
                    condition_values={"973"},
                ),
            ],
        },
        "po_1_race_pi_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1020",
                    fig_link=global_data.fig_base_url + "#4.1.64",
                    name="po_1_race_pi_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 1: free-form text field for 
                        other Pacific Islander race' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2120",
                    fig_link=global_data.fig_base_url + "#4.2.42",
                    name="po_1_race_pi_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 1' does **not** contain 974 (the applicant 
                        responded in the free-form text field for other Pacific Islander race), 
                        'race of principal owner 1: free-form text field for other Pacific Islander race' 
                        must be blank.
                        * When 'race of principal owner 1' contains 974, 'Race of Principal Owner 1: 
                        Free-form Text Field for Other Pacific Islander race' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_1_race",
                    condition_values={"974"},
                ),
            ],
        },
        "po_1_gender_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1040",
                    fig_link=global_data.fig_base_url + "#4.1.65",
                    name="po_1_gender_flag.invalid_enum_value",
                    description="* When present, 'sex/gender of principal owner 1: NP flag' must equal 1, 966, or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "966",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "po_1_gender_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1060",
                    fig_link=global_data.fig_base_url + "#4.1.66",
                    name="po_1_gender_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Sex/gender of principal owner 1: free-form text field for 
                        self-identified sex/gender' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2140",
                    fig_link=global_data.fig_base_url + "#4.2.46",
                    name="po_1_gender_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'sex/gender of principal owner 1: NP flag' does **not** equal 1 (the applicant responded in the 
                        free-form text field), 'sex/gender of principal owner 1: free-form text field for self-identified 
                        sex/gender' must be blank.
                        * When 'sex/gender of principal owner 1: NP flag' equals 1, 'sex/gender of principal owner 1: free-form 
                        text field for self-identified sex/gender' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_1_gender_flag",
                    condition_values={"1"},
                ),
            ],
        },
        "po_2_ethnicity": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1080",
                    fig_link=global_data.fig_base_url + "#4.1.67",
                    name="po_2_ethnicity.invalid_enum_value",
                    description=dedent(
                        """\
                        * When present, each value in 'ethnicity of principal owner 2' 
                        (separated by semicolons) must equal 1, 11, 12, 13, 14, 2, 966, 977, or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_unique_in_field,
                    id="W1081",
                    fig_link=global_data.fig_base_url + "#4.4.19",
                    name="po_2_ethnicity.duplicates_in_field",
                    description="* 'Ethnicity of principal owner 2' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1082",
                    fig_link=global_data.fig_base_url + "#4.4.20",
                    name="po_2_ethnicity.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'ethnicity of principal owner 2' contains 966 (the applicant 
                        responded that they did not wish to provide this information) or 988 
                        (not provided by applicant), 'ethnicity of principal owner: 2' should 
                        **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_2_ethnicity_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1100",
                    fig_link=global_data.fig_base_url + "#4.1.68",
                    name="po_2_ethnicity_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Ethnicity of principal owner 2: free-form text field for 
                        other Hispanic or Latino' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2041",
                    fig_link=global_data.fig_base_url + "#4.2.27",
                    name="po_2_ethnicity_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'ethnicity of principal owner 2' does **not** contain 977 (the applicant responded in the 
                        free-form text field), 'ethnicity of principal owner 2: free-form text field for other Hispanic 
                        or Latino' must be blank.
                        * When 'ethnicity of principal owner 2' contains 977, 'ethnicity of principal owner 2: free-form 
                        text field for other Hispanic or Latino' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_2_ethnicity",
                    condition_values={"977"},
                ),
            ],
        },
        "po_2_race": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1120",
                    fig_link=global_data.fig_base_url + "#4.1.69",
                    name="po_2_race.invalid_enum_value",
                    description=dedent(
                        """\
                        * When present, each value in 'race of principal owner 2' 
                        (separated by semicolons) must equal 1, 2, 21, 22, 23, 24, 
                        25, 26, 27, 3, 31, 32, 33, 34, 35, 36, 37, 4, 41, 42, 43, 44, 
                        5, 966, 971, 972, 973, 974, or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_unique_in_field,
                    id="W1121",
                    fig_link=global_data.fig_base_url + "#4.4.21",
                    name="po_2_race.duplicates_in_field",
                    description="* 'Race of principal owner 2' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1122",
                    fig_link=global_data.fig_base_url + "#4.4.22",
                    name="po_2_race.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'race of principal owner 2' contains 966 
                        (the applicant responded that they did not wish 
                        to provide this information) or 988 (not provided 
                        by applicant), 'race of principal owner: 2' should 
                        **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_2_race_anai_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1140",
                    fig_link=global_data.fig_base_url + "#4.1.70",
                    name="po_2_race_anai_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 2: free-form text field 
                        for American Indian or Alaska Native Enrolled or Principal 
                        Tribe' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2061",
                    fig_link=global_data.fig_base_url + "#4.2.31",
                    name="po_2_race_anai_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 2' does **not** contain 971 (the applicant responded in 
                        the free-form text field for American Indian or Alaska Native Enrolled or Principal Tribe), 
                        'race of principal owner 2: free-form text field for American Indian or Alaska Native Enrolled 
                        or Principal Tribe' must be blank.
                        * When 'race of principal owner 2' contains 971, 'race of principal owner 2: free-form text field 
                        for American Indian or Alaska Native Enrolled or Principal Tribe' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_2_race",
                    condition_values={"971"},
                ),
            ],
        },
        "po_2_race_asian_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1160",
                    fig_link=global_data.fig_base_url + "#4.1.71",
                    name="po_2_race_asian_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 2: free-form text field for 
                        other Asian' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2081",
                    fig_link=global_data.fig_base_url + "#4.2.35",
                    name="po_2_race_asian_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 2' does **not** contain 972 (the applicant responded in the free-form text 
                        field for other Asian race), 'race of principal owner 2: free-form text field for other Asian' must be blank.
                        * When 'race of principal owner 2' contains 972, 'race of principal owner 2: free-form text field for other 
                        Asian' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_2_race",
                    condition_values={"972"},
                ),
            ],
        },
        "po_2_race_baa_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1180",
                    fig_link=global_data.fig_base_url + "#4.1.72",
                    name="po_2_race_baa_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 2: free-form text field for other 
                        Black or African American' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2101",
                    fig_link=global_data.fig_base_url + "#4.2.39",
                    name="po_2_race_baa_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 2' does **not** contain 973 (the applicant 
                        responded in the free-form text field for other Black or African race), 
                        'race of principal owner 2: free-form text field for other Black or African American' must be blank.
                        * When 'race of principal owner 2' contains 973, 'race of principal owner 2: 
                        free-form text field for other Black or African American' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_2_race",
                    condition_values={"973"},
                ),
            ],
        },
        "po_2_race_pi_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1200",
                    fig_link=global_data.fig_base_url + "#4.1.73",
                    name="po_2_race_pi_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 2: free-form text field for 
                        other Pacific Islander race' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2121",
                    fig_link=global_data.fig_base_url + "#4.2.43",
                    name="po_2_race_pi_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 2' does **not** contain 974 (the applicant responded in the 
                        free-form text field for other Pacific Islander race), 'race of principal owner 2: free-form 
                        text field for other Pacific Islander race' must be blank.
                        * When 'race of principal owner 2' contains 974, 'Race of Principal Owner 2: Free-form Text 
                        Field for Other Pacific Islander race' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_2_race",
                    condition_values={"974"},
                ),
            ],
        },
        "po_2_gender_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1220",
                    fig_link=global_data.fig_base_url + "#4.1.74",
                    name="po_2_gender_flag.invalid_enum_value",
                    description="* When present, 'sex/gender of principal owner 2: NP flag' must equal 1, 966, or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "966",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "po_2_gender_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1240",
                    fig_link=global_data.fig_base_url + "#4.1.75",
                    name="po_2_gender_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Sex/gender of principal owner 2: free-form text field for 
                        self-identified sex/gender' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2141",
                    fig_link=global_data.fig_base_url + "#4.2.47",
                    name="po_2_gender_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'sex/gender of principal owner 2: NP flag' does **not** 
                        equal 1 (the applicant responded in the free-form text field), 
                        'sex/gender of principal owner 2: free-form text field for 
                        self-identified sex/gender' must be blank.
                        * When 'sex/gender of principal owner 2: NP flag' equals 1, 'sex/gender 
                        of principal owner 2: free-form text field for self-identified sex/gender' 
                        must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_2_gender_flag",
                    condition_values={"1"},
                ),
            ],
        },
        "po_3_ethnicity": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1260",
                    fig_link=global_data.fig_base_url + "#4.1.76",
                    name="po_3_ethnicity.invalid_enum_value",
                    description=dedent(
                        """\
                        * When present, each value in 'ethnicity of principal 
                        owner 3' (separated by semicolons) must equal 1, 11, 12, 
                        13, 14, 2, 966, 977, or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_unique_in_field,
                    id="W1261",
                    fig_link=global_data.fig_base_url + "#4.4.23",
                    name="po_3_ethnicity.duplicates_in_field",
                    description="* 'Ethnicity of principal owner 3' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1262",
                    fig_link=global_data.fig_base_url + "#4.4.24",
                    name="po_3_ethnicity.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'ethnicity of principal owner 3' contains 966 
                        (the applicant responded that they did not wish to provide 
                        this information) or 988 (not provided by applicant), 'ethnicity 
                        of principal owner: 3' should **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_3_ethnicity_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1280",
                    fig_link=global_data.fig_base_url + "#4.1.77",
                    name="po_3_ethnicity_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Ethnicity of principal owner 3: free-form text field 
                        for other Hispanic or Latino' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2042",
                    fig_link=global_data.fig_base_url + "#4.2.28",
                    name="po_3_ethnicity_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'ethnicity of principal owner 3' does not contain 977 (the applicant responded in the 
                        free-form text field), 'ethnicity of principal owner 3: free-form text field for other Hispanic 
                        or Latino' must be blank.
                        * When 'ethnicity of principal owner 3' contains 977, 'ethnicity of principal owner 3: free-form 
                        text field for other Hispanic or Latino' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_3_ethnicity",
                    condition_values={"977"},
                ),
            ],
        },
        "po_3_race": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1300",
                    fig_link=global_data.fig_base_url + "#4.1.78",
                    name="po_3_race.invalid_enum_value",
                    description=dedent(
                        """\
                        * When present, each value in 'race of principal owner 3' 
                        (separated by semicolons) must equal 1, 2, 21, 22, 23, 24, 
                        25, 26, 27, 3, 31, 32, 33, 34, 35, 36, 37, 4, 41, 42, 43, 
                        44, 5, 966, 971, 972, 973, 974, or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_unique_in_field,
                    id="W1301",
                    fig_link=global_data.fig_base_url + "#4.4.25",
                    name="po_3_race.duplicates_in_field",
                    description="* 'Race of principal owner 3' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1302",
                    fig_link=global_data.fig_base_url + "#4.4.26",
                    name="po_3_race.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'race of principal owner 3' contains 966 
                        (the applicant responded that they did not wish to 
                        provide this information) or 988 (not provided by applicant), 
                        'race of principal owner: 3' should **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_3_race_anai_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1320",
                    fig_link=global_data.fig_base_url + "#4.1.79",
                    name="po_3_race_anai_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 3: free-form text field for 
                        American Indian or Alaska Native Enrolled or Principal Tribe' 
                        must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2062",
                    fig_link=global_data.fig_base_url + "#4.2.32",
                    name="po_3_race_anai_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 3' does **not** contain 971 (the applicant responded in 
                        the free-form text field for American Indian or Alaska Native Enrolled or Principal Tribe), 
                        'race of principal owner 3: free-form text field for American Indian or Alaska Native 
                        Enrolled or Principal Tribe' must be blank.
                        * When 'race of principal owner 3' contains 971, 'race of principal owner 3: free-form text 
                        field for American Indian or Alaska Native Enrolled or Principal Tribe' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_3_race",
                    condition_values={"971"},
                ),
            ],
        },
        "po_3_race_asian_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1340",
                    fig_link=global_data.fig_base_url + "#4.1.80",
                    name="po_3_race_asian_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 3: free-form text field for 
                        other Asian' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2082",
                    fig_link=global_data.fig_base_url + "#4.2.36",
                    name="po_3_race_asian_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 3' does **not** contain 972 (the applicant responded in the 
                        free-form text field for other Asian race), 'race of principal owner 3: free-form text field 
                        for other Asian' must be blank.
                        * When 'race of principal owner 3' contains 972, 'race of principal owner 3: free-form text 
                        field for other Asian' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_3_race",
                    condition_values={"972"},
                ),
            ],
        },
        "po_3_race_baa_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1360",
                    fig_link=global_data.fig_base_url + "#4.1.81",
                    name="po_3_race_baa_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 3: free-form text field for other 
                        Black or African American' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2102",
                    fig_link=global_data.fig_base_url + "#4.2.40",
                    name="po_3_race_baa_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 3' does **not** contain 973 (the applicant responded in 
                        the free-form text field for other Black or African race), 'race of principal owner 3: 
                        free-form text field for other Black or African American' must be blank.
                        * When 'race of principal owner 3' contains 973, 'race of principal owner 3: free-form text 
                        field for other Black or African American' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_3_race",
                    condition_values={"973"},
                ),
            ],
        },
        "po_3_race_pi_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1380",
                    fig_link=global_data.fig_base_url + "#4.1.82",
                    name="po_3_race_pi_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 3: free-form text field for other 
                        Pacific Islander race' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2122",
                    fig_link=global_data.fig_base_url + "#4.2.44",
                    name="po_3_race_pi_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 3' does **not** contain 974 (the applicant responded in 
                        the free-form text field for other Pacific Islander race), 'race of principal owner 3: 
                        free-form text field for other Pacific Islander race' must be blank.
                        * When 'race of principal owner 3' contains 974, 'Race of Principal Owner 3: Free-form Text 
                        Field for Other Pacific Islander race' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_3_race",
                    condition_values={"974"},
                ),
            ],
        },
        "po_3_gender_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1400",
                    fig_link=global_data.fig_base_url + "#4.1.83",
                    name="po_3_gender_flag.invalid_enum_value",
                    description="* When present, 'sex/gender of principal owner 3: NP flag' must equal 1, 966, or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "966",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "po_3_gender_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1420",
                    fig_link=global_data.fig_base_url + "#4.1.84",
                    name="po_3_gender_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Sex/gender of principal owner 3: free-form text field for 
                        self-identified sex/gender' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2142",
                    fig_link=global_data.fig_base_url + "#4.2.48",
                    name="po_3_gender_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'sex/gender of principal owner 3: NP flag' does **not** equal 1 
                        (the applicant responded in the free-form text field), 'sex/gender of principal 
                        owner 3: free-form text field for self-identified sex/gender' must be blank.
                        * When 'sex/gender of principal owner 3: NP flag' equals 1, 'sex/gender of principal 
                        owner 3: free-form text field for self-identified sex/gender' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_3_gender_flag",
                    condition_values={"1"},
                ),
            ],
        },
        "po_4_ethnicity": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1440",
                    fig_link=global_data.fig_base_url + "#4.1.85",
                    name="po_4_ethnicity.invalid_enum_value",
                    description=dedent(
                        """\
                        * When present, each value in 'ethnicity of principal owner 4' 
                        (separated by semicolons) must equal 1, 11, 12, 13, 14, 2, 966, 977, or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_unique_in_field,
                    id="W1441",
                    fig_link=global_data.fig_base_url + "#4.4.27",
                    name="po_4_ethnicity.duplicates_in_field",
                    description="* 'Ethnicity of principal owner 4' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1442",
                    fig_link=global_data.fig_base_url + "#4.4.28",
                    name="po_4_ethnicity.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'ethnicity of principal owner 4' contains 966 (the applicant 
                        responded that they did not wish to provide this information) or 988 
                        (not provided by applicant), 'ethnicity of principal owner: 4' should 
                        **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_4_ethnicity_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1460",
                    fig_link=global_data.fig_base_url + "#4.1.86",
                    name="po_4_ethnicity_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Ethnicity of principal owner 4: free-form text field for 
                        other Hispanic or Latino' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2043",
                    fig_link=global_data.fig_base_url + "#4.2.29",
                    name="po_4_ethnicity_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'ethnicity of principal owner 4' does **not** contain 977 (the applicant responded in the 
                        free-form text field), 'ethnicity of principal owner 4: free-form text field for other Hispanic 
                        or Latino' must be blank.
                        * When 'ethnicity of principal owner 4' contains 977, 'ethnicity of principal owner 4: free-form 
                        text field for other Hispanic or Latino' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_4_ethnicity",
                    condition_values={"977"},
                ),
            ],
        },
        "po_4_race": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1480",
                    fig_link=global_data.fig_base_url + "#4.1.87",
                    name="po_4_race.invalid_enum_value",
                    description=dedent(
                        """\
                        * When present, each value in 'race of principal owner 4' 
                        (separated by semicolons) must equal 1, 2, 21, 22, 23, 24, 
                        25, 26, 27, 3, 31, 32, 33, 34, 35, 36, 37, 4, 41, 42, 43, 
                        44, 5, 966, 971, 972, 973, 974, or 988.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
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
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    is_unique_in_field,
                    id="W1481",
                    fig_link=global_data.fig_base_url + "#4.4.29",
                    name="po_4_race.duplicates_in_field",
                    description="* 'Race of principal owner 4' should **not** contain duplicated values.",
                    severity=Severity.WARNING,
                    scope="single-field",
                ),
                SBLCheck(
                    meets_multi_value_field_restriction,
                    id="W1482",
                    fig_link=global_data.fig_base_url + "#4.4.30",
                    name="po_4_race.multi_value_field_restriction",
                    description=dedent(
                        """\
                        * When 'race of principal owner 4' contains 966 (the applicant 
                        responded that they did not wish to provide this information) or 
                        988 (not provided by applicant), 'race of principal owner: 4' 
                        should **not** contain more than one value.
                     """
                    ),
                    severity=Severity.WARNING,
                    scope="single-field",
                    element_wise=True,
                    single_values={"966", "988"},
                ),
            ],
        },
        "po_4_race_anai_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1500",
                    fig_link=global_data.fig_base_url + "#4.1.88",
                    name="po_4_race_anai_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 4: free-form text field for 
                        American Indian or Alaska Native Enrolled or Principal Tribe' 
                        must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2063",
                    fig_link=global_data.fig_base_url + "#4.2.33",
                    name="po_4_race_anai_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 4' does **not** contain 971 (the applicant responded in 
                        the free-form text field for American Indian or Alaska Native Enrolled or Principal Tribe), 
                        'race of principal owner 4: free-form text field for American Indian or Alaska Native Enrolled 
                        or Principal Tribe' must be blank.
                        * When 'race of principal owner 4' contains 971, 'race of principal owner 4: free-form text field 
                        for American Indian or Alaska Native Enrolled or Principal Tribe' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_4_race",
                    condition_values={"971"},
                ),
            ],
        },
        "po_4_race_asian_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1520",
                    fig_link=global_data.fig_base_url + "#4.1.89",
                    name="po_4_race_asian_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 4: free-form text field for other 
                        Asian' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2083",
                    fig_link=global_data.fig_base_url + "#4.2.37",
                    name="po_4_race_asian_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 4' does **not** contain 972 (the applicant 
                        responded in the free-form text field for other Asian race), 'race of principal 
                        owner 4: free-form text field for other Asian' must be blank.
                        * When 'race of principal owner 4' contains 972, 'race of principal owner 4: 
                        free-form text field for other Asian' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_4_race",
                    condition_values={"972"},
                ),
            ],
        },
        "po_4_race_baa_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1540",
                    fig_link=global_data.fig_base_url + "#4.1.90",
                    name="po_4_race_baa_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 4: free-form text field for other 
                        Black or African American' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2103",
                    fig_link=global_data.fig_base_url + "#4.2.41",
                    name="po_4_race_baa_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 4' does **not** contain 973 (the applicant 
                        responded in the free-form text field for other Black or African race), 
                        'race of principal owner 4: free-form text field for other Black or African 
                        American' must be blank.
                        * When 'race of principal owner 4' contains 973, 'race of principal owner 4: 
                        free-form text field for other Black or African American' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_4_race",
                    condition_values={"973"},
                ),
            ],
        },
        "po_4_race_pi_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1560",
                    fig_link=global_data.fig_base_url + "#4.1.91",
                    name="po_4_race_pi_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Race of principal owner 4: free-form text field for other 
                        Pacific Islander race' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2123",
                    fig_link=global_data.fig_base_url + "#4.2.45",
                    name="po_4_race_pi_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'race of principal owner 4' does **not** contain 974 (the applicant 
                        responded in the free-form text field for other Pacific Islander race), 
                        'race of principal owner 4: free-form text field for other Pacific Islander 
                        race' must be blank.
                        * When 'race of principal owner 4' contains 974, 'Race of Principal Owner 4: 
                        Free-form Text Field for Other Pacific Islander race' must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_4_race",
                    condition_values={"974"},
                ),
            ],
        },
        "po_4_gender_flag": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck(
                    is_valid_enum,
                    id="E1580",
                    fig_link=global_data.fig_base_url + "#4.1.92",
                    name="po_4_gender_flag.invalid_enum_value",
                    description="* When present, 'sex/gender of principal owner 4: NP flag' must equal 1, 966, or 988.",
                    severity=Severity.ERROR,
                    scope="single-field",
                    accepted_values=[
                        "1",
                        "966",
                        "988",
                    ],
                    accept_blank=True,
                ),
            ],
            ValidationPhase.LOGICAL: [],
        },
        "po_4_gender_ff": {
            ValidationPhase.SYNTACTICAL: [
                SBLCheck.str_length(
                    0,
                    300,
                    id="E1600",
                    fig_link=global_data.fig_base_url + "#4.1.93",
                    name="po_4_gender_ff.invalid_text_length",
                    description=dedent(
                        """\
                        * 'Sex/gender of principal owner 4: free-form text field for 
                        self-identified sex/gender' must **not** exceed 300 characters in length.
                     """
                    ),
                    severity=Severity.ERROR,
                    scope="single-field",
                ),
            ],
            ValidationPhase.LOGICAL: [
                SBLCheck(
                    has_no_conditional_field_conflict,
                    id="E2143",
                    fig_link=global_data.fig_base_url + "#4.2.49",
                    name="po_4_gender_ff.conditional_field_conflict",
                    description=dedent(
                        """\
                        * When 'sex/gender of principal owner 4: NP flag' does **not** equal 1 
                        (the applicant responded in the free-form text field), 'sex/gender of 
                        principal owner 4: free-form text field for self-identified sex/gender' 
                        must be blank.
                        * When 'sex/gender of principal owner 4: NP flag' equals 1, 'sex/gender 
                        of principal owner 4: free-form text field for self-identified sex/gender' 
                        must **not** be blank.
                    """
                    ),
                    severity=Severity.ERROR,
                    scope="multi-field",
                    related_fields="po_4_gender_flag",
                    condition_values={"1"},
                ),
            ],
        },
    }
