# -*- coding: utf-8 -*-
"""demo_bauen.py: die Web-Demo zeigt keine Werbung und sagt das auch."""
import io
import json
import os

import pytest


@pytest.fixture(scope="module")
def demo(tmp_path_factory):
    import demo_bauen
    ziel = str(tmp_path_factory.mktemp("demo") / "site")
    demo_bauen.main(["--ziel", ziel])
    return ziel


def test_keine_platzhalter_werbung(demo):
    html = io.open(os.path.join(demo, "index.html"), encoding="utf-8").read()
    import demo_bauen
    assert demo_bauen.WERBUNG_NEU in html and demo_bauen.WERBUNG_ALT not in html


def test_datenschutz_passt_zur_demo(demo, sprachcodes):
    """Ohne Werbung darf die Datenschutzerklärung keinen Werbepartner nennen."""
    for code in sprachcodes:
        daten = json.load(io.open(os.path.join(demo, "inhalt", code + ".json"), encoding="utf-8"))
        assert daten["werbung_laeuft"] is False, code
        assert "AdMob" not in daten["texte"]["set.datenschutz_text"], code


def test_app_selbst_bleibt_unveraendert(demo, wurzel):
    """Die Demo ändert nur die Kopie, nie web/."""
    import demo_bauen
    html = io.open(os.path.join(wurzel, "web", "index.html"), encoding="utf-8").read()
    assert html.count(demo_bauen.WERBUNG_ALT) == 1


def test_keine_probedateien_in_der_demo(demo):
    for wurzel_, ordner, dateien in os.walk(demo):
        assert "_probe" not in ordner, wurzel_
    assert os.path.exists(os.path.join(demo, ".nojekyll"))


def test_schalter_wird_zurueckgesetzt(demo):
    import sys
    assert sys.modules["sprachen"].WERBUNG_LAEUFT is True
