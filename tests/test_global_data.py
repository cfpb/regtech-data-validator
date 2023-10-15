import pytest

from regtech_data_validator import global_data


class TestGlobalData:
    def test_valid_naics_codes(self):
        global_data.read_naics_codes()
        assert len(global_data.naics_codes) == 96

    def test_valid_geoids(self):
        global_data.read_geoids()
        assert len(global_data.census_geoids) == 87275

    def test_invalid_naics_file(self):
        failed_fpath = "./data/naics/processed/2022_codes.csv1"
        with pytest.raises(Exception) as exc:
            global_data.read_naics_codes(failed_fpath)
        assert exc.type == FileNotFoundError

    def test_invalid_geoids_file(self):
        failed_fpath = "./data/census/processed/Census2022.processed.csv2"
        with pytest.raises(Exception) as exc:
            global_data.read_geoids(failed_fpath)
        assert exc.type == FileNotFoundError
