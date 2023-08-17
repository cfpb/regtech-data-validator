import pandas as pd

from util import global_data
from validator.create_schemas import (
    get_schemas,
    validate,
    validate_data_list,
    validate_raw_csv,
)


class TestGetSchemas:
    naics_codes = global_data.read_naics_codes()
    geoids = global_data.read_geoids()
    schemas = get_schemas(naics_codes, {})

    def test_with_valid_codes(self):
        naics_phase1_checks = self.schemas[0].columns["naics_code"].checks
        naics_phase2_checks = self.schemas[1].columns["naics_code"].checks
        invalid_naics_format = naics_phase1_checks[0].name
        invalid_naics_value = naics_phase2_checks[1].name
        naics_codes = naics_phase2_checks[1]._check_kwargs["codes"]
        assert self.naics_codes == naics_codes
        assert invalid_naics_format == "naics_code.invalid_naics_format"
        assert invalid_naics_value == "naics_code.invalid_naics_value"

    def test_with_invalid_codes(self):
        geoids_phase2_checks = self.schemas[1].columns["census_tract_number"].checks
        geoids = geoids_phase2_checks[1]._check_kwargs["codes"]
        assert self.geoids != geoids


class TestUtil:
    naics_codes = global_data.read_naics_codes()
    geoids = global_data.read_geoids()
    schemas = get_schemas(naics_codes, geoids)
    valid_response = {"response": "No validations errors or warnings"}

    def get_data(self, update_data: dict[str, list[str]] = {}) -> dict[str, list[str]]:
        default = {
            "uid": ["000TESTFIUIDDONOTUSEXGXVID11XTC1"],
            "app_date": ["20241201"],
            "app_method": ["1"],
            "app_recipient": ["1"],
            "ct_credit_product": ["988"],
            "ct_credit_product_ff": [""],
            "ct_guarantee": ["999"],
            "ct_guarantee_ff": [""],
            "ct_loan_term_flag": ["999"],
            "ct_loan_term": [""],
            "credit_purpose": ["999"],
            "credit_purpose_ff": [""],
            "amount_applied_for_flag": ["999"],
            "amount_applied_for": [""],
            "amount_approved": [""],
            "action_taken": ["5"],
            "action_taken_date": ["20241231"],
            "denial_reasons": ["999"],
            "denial_reasons_ff": [""],
            "pricing_interest_rate_type": ["999"],
            "pricing_init_rate_period": [""],
            "pricing_fixed_rate": [""],
            "pricing_adj_margin": [""],
            "pricing_adj_index_name": ["999"],
            "pricing_adj_index_name_ff": [""],
            "pricing_adj_index_value": [""],
            "pricing_origination_charges": [""],
            "pricing_broker_fees": [""],
            "pricing_initial_charges": [""],
            "pricing_mca_addcost_flag": ["999"],
            "pricing_mca_addcost": [""],
            "pricing_prepenalty_allowed": ["999"],
            "pricing_prepenalty_exists": ["999"],
            "census_tract_adr_type": ["988"],
            "census_tract_number": [""],
            "gross_annual_revenue_flag": ["988"],
            "gross_annual_revenue": [""],
            "naics_code_flag": ["988"],
            "naics_code": [""],
            "number_of_workers": ["988"],
            "time_in_business_type": ["988"],
            "time_in_business": [""],
            "business_ownership_status": ["988"],
            "num_principal_owners_flag": ["988"],
            "num_principal_owners": [""],
            "po_1_ethnicity": [""],
            "po_1_ethnicity_ff": [""],
            "po_1_race": [""],
            "po_1_race_anai_ff": [""],
            "po_1_race_asian_ff": [""],
            "po_1_race_baa_ff": [""],
            "po_1_race_pi_ff": [""],
            "po_1_gender_flag": [""],
            "po_1_gender_ff": [""],
            "po_2_ethnicity": [""],
            "po_2_ethnicity_ff": [""],
            "po_2_race": [""],
            "po_2_race_anai_ff": [""],
            "po_2_race_asian_ff": [""],
            "po_2_race_baa_ff": [""],
            "po_2_race_pi_ff": [""],
            "po_2_gender_flag": [""],
            "po_2_gender_ff": [""],
            "po_3_ethnicity": [""],
            "po_3_ethnicity_ff": [""],
            "po_3_race": [""],
            "po_3_race_anai_ff": [""],
            "po_3_race_asian_ff": [""],
            "po_3_race_baa_ff": [""],
            "po_3_race_pi_ff": [""],
            "po_3_gender_flag": [""],
            "po_3_gender_ff": [""],
            "po_4_ethnicity": [""],
            "po_4_ethnicity_ff": [""],
            "po_4_race": [""],
            "po_4_race_anai_ff": [""],
            "po_4_race_asian_ff": [""],
            "po_4_race_baa_ff": [""],
            "po_4_race_pi_ff": [""],
            "po_4_gender_flag": [""],
            "po_4_gender_ff": [""],
        }
        default.update(update_data)
        return default

    def get_csv_bytes(self, *update_data: str) -> bytes:
        data = [
            (
                "uid,app_date,app_method,app_recipient,ct_credit_product,"
                "ct_credit_product_ff,ct_guarantee,ct_guarantee_ff,"
                "ct_loan_term_flag,ct_loan_term,credit_purpose,credit_purpose_ff,"
                "amount_applied_for_flag,amount_applied_for,amount_approved,"
                "action_taken,action_taken_date,denial_reasons,denial_reasons_ff,"
                "pricing_interest_rate_type,pricing_init_rate_period,"
                "pricing_fixed_rate,pricing_adj_margin,pricing_adj_index_name,"
                "pricing_adj_index_name_ff,pricing_adj_index_value,"
                "pricing_origination_charges,pricing_broker_fees,"
                "pricing_initial_charges,pricing_mca_addcost_flag,"
                "pricing_mca_addcost,pricing_prepenalty_allowed,"
                "pricing_prepenalty_exists,census_tract_adr_type,"
                "census_tract_number,gross_annual_revenue_flag,"
                "gross_annual_revenue,naics_code_flag,naics_code,number_of_workers,"
                "time_in_business_type,time_in_business,business_ownership_status,"
                "num_principal_owners_flag,num_principal_owners,po_1_ethnicity,"
                "po_1_ethnicity_ff,po_1_race,po_1_race_anai_ff,po_1_race_asian_ff,"
                "po_1_race_baa_ff,po_1_race_pi_ff,po_1_gender_flag,po_1_gender_ff,"
                "po_2_ethnicity,po_2_ethnicity_ff,po_2_race,po_2_race_anai_ff,"
                "po_2_race_asian_ff,po_2_race_baa_ff,po_2_race_pi_ff,"
                "po_2_gender_flag,po_2_gender_ff,po_3_ethnicity,po_3_ethnicity_ff,"
                "po_3_race,po_3_race_anai_ff,po_3_race_asian_ff,po_3_race_baa_ff,"
                "po_3_race_pi_ff,po_3_gender_flag,po_3_gender_ff,po_4_ethnicity,"
                "po_4_ethnicity_ff,po_4_race,po_4_race_anai_ff,po_4_race_asian_ff,"
                "po_4_race_baa_ff,po_4_race_pi_ff,po_4_gender_flag,po_4_gender_ff"
            )
        ]
        data.extend(list(update_data))
        result = "\n".join(data)
        return bytes(result, "utf-8")


class TestValidate:
    util = TestUtil()
    schemas = util.schemas
    phase1_schema = schemas[0]
    phase2_schema = schemas[1]

    def test_with_valid_dataframe(self):
        df = pd.DataFrame(data=self.util.get_data())
        result = validate(self.phase1_schema, df)
        ph2_result = validate(self.phase2_schema, df)
        assert len(result) == 0
        assert len(ph2_result) == 0

    def test_with_invalid_dataframe(self):
        df = pd.DataFrame(data=self.util.get_data({"ct_credit_product": ["989"]}))
        result = validate(self.phase1_schema, df)
        ph2_result = validate(self.phase2_schema, df)
        assert len(result) == 1
        assert len(ph2_result) == 0

    def test_with_multi_invalid_dataframe(self):
        df = pd.DataFrame(
            data=self.util.get_data(
                {
                    "ct_credit_product": ["989"],
                    "num_principal_owners": ["1"],
                    "action_taken": ["2"],
                }
            )
        )
        result = validate(self.phase1_schema, df)
        assert len(result) == 1

        ph2_result = validate(self.phase2_schema, df)
        assert len(ph2_result) == 3


class TestValidateDataList:
    util = TestUtil()
    schemas = util.schemas
    phase1_schema = schemas[0]
    phase2_schema = schemas[1]

    def test_with_valid_data(self):
        result = validate_data_list(
            self.phase1_schema, self.phase2_schema, self.util.get_data()
        )

        assert len(result) == 1
        assert result[0] == self.util.valid_response

    def test_with_invalid_data(self):
        result = validate_data_list(
            self.phase1_schema,
            self.phase2_schema,
            self.util.get_data({"ct_credit_product": ["989"]}),
        )

        assert len(result) == 1
        assert result[0] != self.util.valid_response

    def test_with_multi_invalid_data_with_phase1(self):
        result = validate_data_list(
            self.phase1_schema,
            self.phase2_schema,
            self.util.get_data(
                {
                    "ct_credit_product": ["989"],
                    "num_principal_owners": ["1"],
                    "action_taken": ["2"],
                }
            ),
        )
        # should only return phase 1 validation result since phase1 failed
        assert len(result) == 1
        assert result[0] != self.util.valid_response

    def test_with_multi_invalid_data_with_phase2(self):
        result = validate_data_list(
            self.phase1_schema,
            self.phase2_schema,
            self.util.get_data(
                {
                    "num_principal_owners": ["1"],
                    "action_taken": ["2"],
                }
            ),
        )
        # since the data passed phase 1 validations
        # this should return phase 2 validations
        assert len(result) == 3
        assert result[0] != self.util.valid_response


class TestValidateRawCsv:
    util = TestUtil()
    schemas = util.schemas
    phase1_schema = schemas[0]
    phase2_schema = schemas[1]

    def test_with_valid_data(self):
        data = (
            "000TESTFIUIDDONOTUSEXGXVID11XTC1,20241201,1,1,988,,999,,999,,999,"
            ",999,,,5,20241231,999,,999,,,,999,,,,,,999,,999,999,988,,988,,988,"
            ",988,988,,988,988,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        csv_bytes = self.util.get_csv_bytes(data)
        result = validate_raw_csv(self.phase1_schema, self.phase2_schema, csv_bytes)
        assert len(result) == 1
        assert result[0] == self.util.valid_response

    def test_with_multi_valid_data(self):
        data = (
            "000TESTFIUIDDONOTUSEXGXVID11XTC1,20241201,1,1,988,,999,,999,"
            ",999,,999,,,5,20241231,999,,999,,,,999,,,,,,999,,999,999,988,"
            ",988,,988,,988,988,,988,988,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        data2 = (
            "000TESTFIUIDDONOTUSEXGXVID13XTC1,20241201,1,1,988,,999,,999,"
            ",999,,999,,,5,20241231,999,,999,,,,999,,,,,,999,,999,999,988,"
            ",988,,988,,988,988,,988,988,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        csv_bytes = self.util.get_csv_bytes(data, data2)
        result = validate_raw_csv(self.phase1_schema, self.phase2_schema, csv_bytes)
        assert len(result) == 1
        assert result[0] == self.util.valid_response

    def test_with_invalid_data(self):
        data = (
            "000TESTFIUIDDONOTUSEXGXVID11XTC1,20241201,1,1,989,,999,,999,"
            ",999,,999,,,5,20241231,999,,999,,,,999,,,,,,999,,999,999,988,"
            ",988,,988,,988,988,,988,988,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        data2 = (
            "000TESTFIUIDDONOTUSEXGXVID13XTC1,20241201,1,1,988,,990,,999,"
            ",999,,999,,,5,20241231,999,,999,,,,999,,,,,,999,,999,999,988,"
            ",988,,988,,988,988,,988,988,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        csv_bytes = self.util.get_csv_bytes(data, data2)
        result = validate_raw_csv(self.phase1_schema, self.phase2_schema, csv_bytes)
        assert len(result) == 2
        assert result[0] != self.util.valid_response

    def test_with_multi_invalid_data_with_phase1(self):
        data = (
            "000TESTFIUIDDONOTUSEXGXVID11XTC1,20241201,1,1,988,,999,,999,,999,"
            ",999,,,2,20241231,999,,999,,,,999,,,,,,999,,999,999,988,,988,,988,"
            ",988,988,,988,988,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        data2 = (
            "000TESTFIUIDDONOTUSEXGXVID11XTC1,20241201,1,1,988,,999,,999,,999,"
            ",999,,,5,20241231,999,,999,,,,999,,,,,,999,,999,999,988,,988,,988,"
            ",988,988,,988,988,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        csv_bytes = self.util.get_csv_bytes(data, data2)
        result = validate_raw_csv(self.phase1_schema, self.phase2_schema, csv_bytes)
        assert len(result) == 1
        assert result[0] != self.util.valid_response

    def test_with_multi_invalid_data_with_phase2(self):
        data = (
            "000TESTFIUIDDONOTUSEXGXVID11XTC1,20241201,1,1,988,,999,,999,,999,"
            ",999,,,2,20241231,999,,999,,,,999,,,,,,999,,999,999,988,,988,,988,"
            ",988,988,,988,988,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        data2 = (
            "000TESTFIUIDDONOTUSEXGXVID12XTC1,20241201,1,1,988,,999,,999,,999,"
            ",999,,,1,20241231,999,,999,,,,999,,,,,,999,,999,999,988,,988,,988,"
            ",988,988,,988,988,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        )
        csv_bytes = self.util.get_csv_bytes(data, data2)
        result = validate_raw_csv(self.phase1_schema, self.phase2_schema, csv_bytes)
        assert len(result) == 2
        assert result[0] != self.util.valid_response
