import requests

from regtech_data_validator.phase_validations import get_phase_1_and_2_validations_for_lei
from regtech_data_validator.global_data import fig_base_url
from bs4 import BeautifulSoup


class TestFigAnchors:

    def test_fig_anchors(self):

        html_text = requests.get(
            "https://www.consumerfinance.gov/data-research/small-business-lending/filing-instructions-guide/2024-guide/#4"
        ).text
        source_links = BeautifulSoup(html_text, 'html.parser')

        validators = get_phase_1_and_2_validations_for_lei()
        checks = []
        validator_anchors = []
        fig_anchors = []

        for k in validators.keys():
            v = validators[k]
            for p in v.keys():
                checks.extend(v[p])

        for check in checks:
            validator_anchors.append({"id": check.title, "anchor": check.fig_anchor})

        elements = source_links.find_all(lambda tag: tag.name == "a" and "Validation ID:" in tag.text)
        for e in elements:
            anchor = e.get('href')
            id = e.text.split("Validation ID:")[1].strip()
            fig_anchors.append({"id": id, "anchor": fig_base_url + anchor})

        validator_anchors = sorted(validator_anchors, key=lambda d: d['id'])
        fig_anchors = sorted(fig_anchors, key=lambda d: d['id'])
        anchors = zip(validator_anchors, fig_anchors)
        assert not any(x != y for x, y in anchors)
