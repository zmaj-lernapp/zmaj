# -*- coding: utf-8 -*-
"""Überschriften der Store-Bilder (store/bilder_machen/beschriften.py).

Geprüft wird ohne Browser:
  - Jede Sprache hat genau eine Überschrift je Bild, in derselben Reihenfolge
    wie die Aufnahmen in bilder_playwright.py.
  - Feste Wendungen bleiben in einer Zeile: Das geschützte Leerzeichen
    (U+00A0) ist unsichtbar und geht beim Bearbeiten leicht verloren. Ohne
    brach Bild 4 auf Deutsch als „Sätze Wort für / Wort bauen“ um
    (Prüfung 13.11.2026), auf Türkisch „kelime / kelime“.
"""
import os
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WURZEL, "store", "bilder_machen"))

import beschriften  # noqa: E402

NBSP = " "


def test_jede_sprache_hat_alle_ueberschriften():
    namen = [name for name, _ in beschriften.BP.SCHRITTE]
    for sprache, texte in beschriften.UEBERSCHRIFTEN.items():
        assert len(texte) == len(namen), sprache
        assert all(t.strip() for t in texte), sprache


def test_bild4_bleibt_zusammen():
    de = beschriften.UEBERSCHRIFTEN["de"][3]
    assert de == "Sätze " + NBSP.join(["Wort", "für", "Wort", "bauen"])
    assert de.replace(NBSP, " ") == "Sätze Wort für Wort bauen"   # Wortlaut unverändert
    assert "kelime" + NBSP + "kelime" in beschriften.UEBERSCHRIFTEN["tr"][3]
