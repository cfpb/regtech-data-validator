from regtech_data_validator import global_data


class TestGlobalData:
    def test_valid_naics_codes(self):
        assert len(global_data.naics_codes) == 96

    def test_valid_geoids(self):
        assert len(global_data.census_geoids) == 87276
