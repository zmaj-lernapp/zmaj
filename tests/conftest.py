# -*- coding: utf-8 -*-
"""Gemeinsame Bausteine der Tests. Alles läuft ohne Netz und ohne Abhängigkeit
außer pytest (jsonschema ist optional)."""
import os
import sys

import pytest

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WURZEL)


@pytest.fixture(scope="session")
def wurzel():
    return WURZEL


@pytest.fixture(scope="session")
def sprachcodes():
    import sprachen
    return [s["code"] for s in sprachen.SPRACHEN]


@pytest.fixture(scope="session")
def alle_daten(sprachcodes):
    """inhalt.lade_daten() je Sprache - genau das, was die App bekommt."""
    import inhalt
    return {c: inhalt.lade_daten(c) for c in sprachcodes}


@pytest.fixture(scope="session")
def grunddaten(alle_daten):
    import sprachen
    return alle_daten[sprachen.GRUNDSPRACHE]


@pytest.fixture(scope="session")
def grunddaten_vor_umzug(grunddaten):
    """grunddaten mit den Leveln, wie die Wortschatz-Pakete sie geliefert
    haben: die 40 Grundwoerter wieder an ihrem alten Platz in B1, ohne die
    zwei neuen A-Level (Stufen-Reiter, 13.11.2026). Siehe grundwoerter_umzug.py.
    Seit dem 27.11.2026 auch ohne die neuen Woerter aus K2 und das Level
    Ordnungszahlen (K7), siehe k2_einbau.py."""
    from grundwoerter_umzug import vor_umzug
    from k2_einbau import ohne_k2
    return vor_umzug(ohne_k2(grunddaten))


@pytest.fixture(scope="session")
def index_html(wurzel):
    """web/index.html, wie sie im Repository liegt (Zeilenenden unverändert).

    Über app_quelle.lesen(): Ist die App in web/js und web/css geteilt (1.5,
    Release/Aufteilung/PLAN.md), stehen die Teile hier wieder an ihrer
    Stelle - Byte für Byte die alte Einzeldatei. Ungeteilt ist es die Datei."""
    import app_quelle
    return app_quelle.lesen(os.path.join(wurzel, "web"))
