# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026): Kleinfehler der Oberflaeche, ohne Browser
(Offen-Liste 4). Was ein Lernender davon sieht, pruefen
tests_e2e/test_pruefbericht14_kleinfehler.py und test_tablet.py.

S16: Vor dem Pfeil in "Weiter zu B1 →" und "Weiter zu Level 5 →" steht ein
geschuetztes Leerzeichen, in allen acht Sprachen - sonst stand der Pfeil bei
360 px allein in der zweiten Zeile.

S21: "Zmaj bewerten" oeffnet gleich den Play Store statt Googles Fenster in
der App (BEWERTUNG_IM_APP = false).
"""
import pytest

NBSP_PFEIL = " →"


@pytest.mark.parametrize("schluessel", ["test.weiter_level", "test.weiter_stufe"])
def test_s16_geschuetztes_leerzeichen_vor_dem_pfeil(sprachcodes, schluessel):
    import sprachen
    for code in sprachcodes:
        text = sprachen.TEXTE[code][schluessel]
        assert text.endswith(NBSP_PFEIL), (code, text)
        assert text.count("→") == 1 and " →" not in text, (code, text)


def test_s21_bewerten_ohne_fenster_in_der_app(index_html):
    """S21: Google raet davon ab, das Bewertungsfenster ueber einen Knopf zu
    starten. "Zmaj bewerten" oeffnet gleich den Play Store."""
    assert index_html.count("const BEWERTUNG_IM_APP = ") == 1
    assert "const BEWERTUNG_IM_APP = false;" in index_html
