import pytest

from validator.checks import SBLCheck


class TestSBLCheck:
    def test_no_id_check(self):
        with pytest.raises(Exception) as exc:
            SBLCheck(lambda: True, warning=True, name="Just a Warning")

        assert "Each check must be assigned a `name` and an `id`." in str(exc.value)
        assert exc.type == ValueError

    def test_no_name_check(self):
        with pytest.raises(Exception) as exc:
            SBLCheck(lambda: True, id="00000", warning=True)

        assert "Each check must be assigned a `name` and an `id`." in str(exc.value)
        assert exc.type == ValueError

    def test_name_and_id_check(self):
        raised = False
        try:
            SBLCheck(lambda: True, id="00000", warning=True, name="Just a Warning")
        except ValueError:
            raised = True
        assert raised is False
