"""Create a Pandera SBLAR DataFrameSchema object.

Refer to the Pandera documentation for details. 
https://pandera.readthedocs.io/en/stable/dataframe_schemas.html

The only major modification from native Pandera is the use of custom
Check classes to differentiate between warnings and errors. """


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
            checks=[],
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
            checks=[],
        ),
        "ct_guarantee_ff": Column(
            str,
            title="Field 8: Free-form text field for other guarantee",
            checks=[],
        ),
        "ct_loan_term_flag": Column(
            str,
            title="Field 9: Loan term: NA/NP flag",
            checks=[],
        ),
        "ct_loan_term": Column(
            str,
            title="Field 10: Loan term",
            checks=[],
        ),
        "credit_purpose": Column(
            str,
            title="Field 11: Credit purpose",
            checks=[],
        ),
        "credit_purpose_ff": Column(
            str,
            title="Field 12: Free-form text field for other credit purpose",
            checks=[],
        ),
        "amount_applied_for_flag": Column(
            str,
            title="Field 13: Amount applied for: NA/NP flag",
            checks=[],
        ),
        "amount_applied_for": Column(
            str,
            title="Field 14: Amount applied for",
            checks=[],
        ),
        "amount_approved": Column(
            str,
            title="Field 15: Amount approved or originated",
            checks=[],
        ),
        "action_taken": Column(
            str,
            title="Field 16: Action taken",
            checks=[],
        ),
        "action_taken_date": Column(
            str,
            title="Field 17: Action taken date",
            checks=[],
        ),
        "denial_reasons": Column(
            str,
            title="Field 18: Denial reason(s)",
            checks=[],
        ),
        "denial_reasons_ff": Column(
            str,
            title="Field 19: Free-form text field for other denial reason(s)",
            checks=[],
        ),
        "pricing_interest_rate_type": Column(
            str,
            title="Field 20: Interest rate type",
            checks=[],
        ),
    }
)
