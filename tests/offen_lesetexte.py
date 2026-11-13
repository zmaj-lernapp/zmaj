# -*- coding: utf-8 -*-
"""Was beim Einbau der B1-Lesetexte (Paket 1 und 2, 13.11.2026) noch fehlt: der Ton.

Die zwölf Texte stehen in geschichten.py, mit Übersetzung, Fragen und jeder
Wortform im Wörterbuch. Vorgelesen werden sie erst, wenn Ajdin die fraglichen
bosnischen Stellen entschieden hat; ein geänderter Text hieße sonst eine neue
Aufnahme. Bis dahin lassen die Ton-Tests (test_ton.py, test_wortzeiten.py und
tests_e2e/test_mitlesen.py) genau die Schlüssel aus offen_lesetexte.json durch
und nichts sonst. tests/test_offen_lesetexte.py
meldet jeden Schlüssel, der inzwischen Ton hat oder in keinem Text mehr
vorkommt: dann hier streichen. Ist die Liste leer, können die drei Dateien weg.
"""
import io
import json
import os

_DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offen_lesetexte.json")
_DATEN = json.load(io.open(_DATEI, encoding="utf-8")) if os.path.exists(_DATEI) else {}

GESCHICHTEN = frozenset(_DATEN.get("geschichten", []))
TON = GESCHICHTEN | frozenset(_DATEN.get("woerter", []))
