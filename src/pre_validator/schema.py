"""This module is responsible for creating a schema object for phase 
1 validation.

This is accomplished by loading the `schema_template` dictionary from
schema_template.py and populating the `checks` list of each column
with the appropriate pre-validation function. Some of the pre-validaiton
functions are wrapped using `functools.partial`. This is done when the
pre-validation contains a key word argument that needs to be overridden.
For example, the `uid` field is a text field but it differs from the 
others in that it cannot be blank. It must be between 21 and 45
characters."""

from functools import partial

from check_functions import (is_date, is_multiple_response, is_numeric,
                             is_single_response, is_special, is_text)
from pandera import DataFrameSchema
from sbl_check import SBLCheck
from schema_template import get_template

# this is a mapping of sblar field to check function used for phase 1
# validation of the field. 
pre_validation_mapping = {
    "uid": partial(is_text, nullable=False),
    "app_date": is_date,
    "app_method": is_single_response,
    "app_recipient": is_single_response,
    "ct_credit_product": is_single_response,
    "ct_credit_product_ff": is_text,
    "ct_guarantee": is_multiple_response,
    "ct_guarantee_ff": is_text,
    "ct_loan_term_flag": is_single_response,
    "ct_loan_term": partial(is_numeric, int_only=True),
    "credit_purpose": is_multiple_response,
    "credit_purpose_ff": is_text,
    "amount_applied_for_flag": is_single_response,
    "amount_applied_for": is_numeric,
    "amount_approved": is_numeric,
    "action_taken": is_single_response,
    "action_taken_date": is_date,
    "denial_reasons": is_multiple_response,
    "denial_reasons_ff": is_text,
    "pricing_interest_rate_type": is_single_response,
    "pricing_init_rate_period": partial(is_numeric, int_only=True),
    "pricing_fixed_rate": is_numeric,
    "pricing_adj_margin": is_numeric,
    "pricing_adj_index_name": is_single_response,
    "pricing_adj_index_name_ff": is_text,
    "pricing_adj_index_value": is_numeric,
    "pricing_origination_charges": is_numeric,
    "pricing_broker_fees": is_numeric,
    "pricing_initial_charges": is_numeric,
    "pricing_mca_addcost_flag": is_single_response,
    "pricing_mca_addcost": is_numeric,
    "pricing_prepenalty_allowed": is_single_response,
    "pricing_prepenalty_exists": is_single_response,
    "census_tract_adr_type": is_single_response,
    "census_tract_number": partial(is_special, width=11),
    "gross_annual_revenue_flag": is_single_response,
    "gross_annual_revenue": is_numeric,
    "naics_code_flag": is_single_response,
    "naics_code": partial(is_special, width=3),
    "number_of_workers": is_single_response,
    "time_in_business_type": is_single_response,
    "time_in_business": partial(is_numeric, int_only=True),
    "business_ownership_status": is_multiple_response,
    "num_principal_owners_flag": is_single_response,
    "num_principal_owners": is_single_response,
    "po_1_ethnicity": is_multiple_response,
    "po_1_ethnicity_ff": is_text,
    "po_1_race": is_multiple_response,
    "po_1_race_anai_ff": is_text,
    "po_1_race_asian_ff": is_text,
    "po_1_race_baa_ff": is_text,
    "po_1_race_pi_ff": is_text,
    "po_1_gender_flag": is_single_response,
    "po_1_gender_ff": is_text,
    "po_2_ethnicity": is_multiple_response,
    "po_2_ethnicity_ff": is_text,
    "po_2_race": is_multiple_response,
    "po_2_race_anai_ff": is_text,
    "po_2_race_asian_ff": is_text,
    "po_2_race_baa_ff": is_text,
    "po_2_race_pi_ff": is_text,
    "po_2_gender_flag": is_single_response,
    "po_2_gender_ff": is_text,
    "po_3_ethnicity": is_multiple_response,
    "po_3_ethnicity_ff": is_text,
    "po_3_race": is_multiple_response,
    "po_3_race_anai_ff": is_text,
    "po_3_race_asian_ff": is_text,
    "po_3_race_baa_ff": is_text,
    "po_3_race_pi_ff": is_text,
    "po_3_gender_flag": is_single_response,
    "po_3_gender_ff": is_text,
    "po_4_ethnicity": is_multiple_response,
    "po_4_ethnicity_ff": is_text,
    "po_4_race": is_multiple_response,
    "po_4_race_anai_ff": is_text,
    "po_4_race_asian_ff": is_text,
    "po_4_race_baa_ff": is_text,
    "po_4_race_pi_ff": is_text,
    "po_4_gender_flag": is_single_response,
    "po_4_gender_ff": is_text,
}

# populate the schema_template object with the appropriate checks
# We're creating a deep copy of the schema_template object defined in
# schema_template.py so there is no risk associated with appending.
phase_1_schema_template = get_template()

for field, phase_1_validation_func in pre_validation_mapping.items():
    phase_1_schema_template[field].checks.append(
        SBLCheck(
            phase_1_validation_func,
            name=f"Phase 1 validaiton for field {field}.",
            description=phase_1_validation_func.__doc__,
            element_wise=True,
        )
    )
    
# Create a schema from the template and we're all done :)
pre_validation_schema = DataFrameSchema()
