# -*- coding: utf-8 -*-
"""Was beim Einbau der Wortschatz-Pakete 10 bis 20 (07.11.2026) noch fehlt: Emirs Ton.

Der Einbau kam in Schritten: zuerst das Geruest (Deutsch und Bosnisch, Sektionen,
Level, Partner, Kennungen), danach die sieben Sprachen und Emirs Ton. Die Nummern der
Aufnahmen sind schon vergeben, sie stehen mit der Herkunft jeder Datei in
Release\\Wortschatz\\_uebersetzung_p10_20\\nummern.json. In ton_nur_emir.json stehen sie
erst, wenn der Ton-Schritt die Dateien in die Huelle kopiert hat.

Bis dahin lassen die Ton-Tests genau die Schluessel aus offen_p1020.json durch und
nichts sonst. tests/test_offen_p1020.py meldet jeden Schluessel, der inzwischen Ton
hat: dann hier streichen. Ist die Liste leer, koennen beide Dateien weg.
"""
import io
import json
import os

_DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offen_p1020.json")

TON = frozenset(json.load(io.open(_DATEI, encoding="utf-8"))["ton"]) if os.path.exists(_DATEI) else frozenset()
