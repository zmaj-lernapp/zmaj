# -*- coding: utf-8 -*-
"""Was beim Einbau der B1-Lesetexte (Paket 1 und 2, 13.11.2026) noch fehlt: der Ton.

Die zwölf Texte stehen in geschichten.py, mit Übersetzung, Fragen und jeder
Wortform im Wörterbuch. Seit dem 16.11.2026 liest Azure (Vesna) sie vor, mit
Wortzeiten (Offen-Liste 6, nach Ajdins A/B-Antworten vom 15.11.2026);
"geschichten" in offen_lesetexte.json ist deshalb leer. Es fehlten noch die
Wörter, die nur in diesen Texten stehen: Wörter spricht Emir, nicht Azure.
Bis dahin lassen die Ton-Tests (test_ton.py, test_wortzeiten.py und
tests_e2e/test_mitlesen.py) genau die Schlüssel aus offen_lesetexte.json durch
und nichts sonst. tests/test_offen_lesetexte.py
meldet jeden Schlüssel, der inzwischen Ton hat oder in keinem Text mehr
vorkommt: dann hier streichen. Ist die Liste leer, können die drei Dateien weg.
Seit dem 16.11.2026 spricht Emir auch diese Wörter (ton_nur_emir.json, w9049
bis w9871, Offen-Liste 6a), "woerter" ist leer. Die Dateien bleiben, bis ein
neuer Text mit Wörtern ohne Ton sie wieder braucht oder Ajdin sie streicht.
"""
import io
import json
import os

_DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offen_lesetexte.json")
_DATEN = json.load(io.open(_DATEI, encoding="utf-8")) if os.path.exists(_DATEI) else {}

GESCHICHTEN = frozenset(_DATEN.get("geschichten", []))
TON = GESCHICHTEN | frozenset(_DATEN.get("woerter", []))
