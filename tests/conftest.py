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
    """start.lade_daten() je Sprache - genau das, was die App bekommt."""
    import start
    return {c: start.lade_daten(c) for c in sprachcodes}


@pytest.fixture(scope="session")
def grunddaten(alle_daten):
    import sprachen
    return alle_daten[sprachen.GRUNDSPRACHE]
