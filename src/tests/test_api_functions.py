import os

import pytest
from fastapi.testclient import TestClient
from test_schema_functions import TestUtil

from api.main import app


class TestApiSchemas:
    client = TestClient(app)
    util = TestUtil()
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))

    def test_valid_json_data(self):
        res = self.client.post("/v1/validate", json=self.util.get_data())
        assert res.json()[0] == self.util.valid_response
        assert res.status_code == 200

    def test_invalid_json_data(self):
        res = self.client.post(
            "/v1/validate", json=self.util.get_data({"ct_credit_product": ["989"]})
        )
        assert (
            res.json()[0]["validation"]["id"] == "ct_credit_product.invalid_enum_value"
        )
        assert res.status_code == 200

    def test_multi_invalid_json_data(self):
        res = self.client.post(
            "/v1/validate",
            json=self.util.get_data(
                {
                    "ct_credit_product": ["989"],
                    "num_principal_owners": ["1"],
                    "action_taken": ["2"],
                }
            ),
        )
        assert len(res.json()) == 1
        assert (
            res.json()[0]["validation"]["id"] == "ct_credit_product.invalid_enum_value"
        )
        assert res.status_code == 200

    def test_multi_invalid_twophase_json_data(self):
        res = self.client.post(
            "/v1/validate",
            json=self.util.get_data(
                {
                    "num_principal_owners": ["1"],
                    "action_taken": ["2"],
                }
            ),
        )
        assert len(res.json()) == 3
        assert (
            res.json()[0]["validation"]["id"]
            == "amount_approved.conditional_field_conflict"
        )
        assert (
            res.json()[1]["validation"]["id"]
            == "pricing_charges.conditional_fieldset_conflict"
        )
        assert (
            res.json()[2]["validation"]["id"]
            == "num_principal_owners.conditional_field_conflict"
        )
        assert res.status_code == 200

    def test_upload_valid_file(self):
        print("CURR_DIR:", self.CURR_DIR)
        valid_file_path = os.path.join(
            self.CURR_DIR, "sample_csv_files/valid_sample_data.csv"
        )
        # valid_file_path = "./sample_csv_files/valid_sample_data.csv"
        if os.path.isfile(valid_file_path):
            files = {"file": open(valid_file_path, "rb")}
            res = self.client.post("/v1/upload", files=files)
            assert res.json()[0] == self.util.valid_response
            assert res.status_code == 200
        else:
            pytest.fail(f"{valid_file_path} does not exist.")

    def test_upload_invalid_phase1_file(self):
        invalid_file_path = os.path.join(
            self.CURR_DIR, "sample_csv_files/invalid_phase1_sample_data.csv"
        )
        # invalid_file_path = "./sample_csv_files/invalid_phase1_sample_data.csv"
        if os.path.isfile(invalid_file_path):
            files = {"file": open(invalid_file_path, "rb")}
            res = self.client.post("/v1/upload", files=files)
            assert len(res.json()) == 1
            assert res.json()[0]["validation"]["id"] == "uid.duplicates_in_dataset"
            assert res.status_code == 200
        else:
            pytest.fail(f"{invalid_file_path} does not exist.")

    def test_upload_invalid_phase2_file(self):
        invalid_file_path = os.path.join(
            self.CURR_DIR, "sample_csv_files/invalid_phase2_sample_data.csv"
        )
        if os.path.isfile(invalid_file_path):
            files = {"file": open(invalid_file_path, "rb")}
            res = self.client.post("/v1/upload", files=files)
            assert len(res.json()) == 3
            assert (
                res.json()[0]["validation"]["id"]
                == "amount_approved.conditional_field_conflict"
            )
            assert (
                res.json()[1]["validation"]["id"]
                == "pricing_charges.conditional_fieldset_conflict"
            )
            assert (
                res.json()[2]["validation"]["id"]
                == "num_principal_owners.conditional_field_conflict"
            )
            assert res.status_code == 200
        else:
            pytest.fail(f"{invalid_file_path} does not exist.")
