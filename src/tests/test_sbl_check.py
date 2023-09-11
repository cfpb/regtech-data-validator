import pytest

from validator.checks import SBLCheck


class TestSBLCheck:
#    def test_no_id_check(self):
#        with pytest.raises(Exception) as exc:
#            SBLCheck(lambda: True, warning=True, name="Just a Warning")

#        assert "Each check must be assigned a `name` and an `id`." in str(exc.value)
#        assert exc.type == ValueError

#    def test_no_name_check(self):
#        with pytest.raises(Exception) as exc:
#            SBLCheck(lambda: True, id="00000", warning=True)

#        assert "Each check must be assigned a `name` and an `id`." in str(exc.value)
#        assert exc.type == ValueError
    def test_no_id_check(self):
        id_check = SBLCheck(lambda: True, warning=True, name="Just a Warning")
        with pytest.raises(Exception) as exc:
            id_check

        assert "Each check must be assigned a `name` and an `id`." in str(exc.value)
        assert exc.type == ValueError

    def test_no_name_check(self):
        id_check = SBLCheck(lambda: True, id="00000", warning=True)
        with pytest.raises(Exception) as exc:
            id_check

        assert "Each check must be assigned a `name` and an `id`." in str(exc.value)
        assert exc.type == ValueError