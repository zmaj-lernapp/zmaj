# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026): Kleinfehler der Oberflaeche, ohne Browser
(Offen-Liste 4). Was ein Lernender davon sieht, pruefen
tests_e2e/test_pruefbericht14_kleinfehler.py und test_tablet.py.

S16: Vor dem Pfeil in "Weiter zu B1 →" und "Weiter zu Level 5 →" steht ein
geschuetztes Leerzeichen, in allen acht Sprachen - sonst stand der Pfeil bei
360 px allein in der zweiten Zeile.
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
