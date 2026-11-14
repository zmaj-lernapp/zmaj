# -*- coding: utf-8 -*-
"""Offen-Liste 4 (14.11.2026): Die B1-Sektion "Körper und Gesundheit"
heisst "Arzt & Gesundheit" (Ajdin: "ok mach arzt & gesundheit").

Nur der Name der Sektion aendert sich, in allen acht Sprachen. Ihre id
(koerpergesundheit) bleibt, damit bleiben Farbe, offene Sektion und die
Zuordnung zur Stufe B1. Das A1-Level "Körper & Gesundheit" heisst weiter so.
"""
import json
import os

import pytest

NAME = {
    "de": "Sektion 4 · Arzt & Gesundheit",
    "en": "Section 4 · Doctor & health",
    "tr": "4. bölüm · Doktor ve sağlık",
    "sv": "Avsnitt 4 · Läkare & hälsa",
    "nl": "Deel 4 · Dokter & gezondheid",
    "nb": "Del 4 · Lege & helse",
    "da": "Del 4 · Læge & sundhed",
    "fr": "Partie 4 · Médecin & santé",
}


def test_alle_sprachen_bekannt(sprachcodes):
    assert sorted(NAME) == sorted(sprachcodes)


@pytest.mark.parametrize("sprache", sorted(NAME))
def test_sektion_heisst_arzt_und_gesundheit(alle_daten, sprache):
    daten = alle_daten[sprache]
    sektion = next(s for s in daten["sektionen"] if s["id"] == "koerpergesundheit")
    assert sektion["label"] == NAME[sprache]
    assert sektion["stufe"] == "B1"
    # das A1-Level bleibt, wie es war
    koerper = next(k for k in daten["kategorien"] if k["id"] == "koerper")
    assert koerper["sektion"] == "alltag"
    if sprache == "de":
        assert koerper["label"] == "Körper & Gesundheit"
    else:
        assert koerper["label"] != "Körper & Gesundheit", "A1-Level unuebersetzt"


def test_alter_name_ist_weg(wurzel):
    """Weder Inhalt noch Uebersetzung kennt den alten Namen noch - ein
    liegengebliebener Schluessel waere toter Text, und der offene Datensatz
    in data/ traegt den neuen Namen in allen acht Sprachen."""
    import uebersetzungen
    import vokabeln
    alt = "Sektion 4 · Körper und Gesundheit"
    assert all(s["label"] != alt for s in vokabeln.SEKTIONEN)
    for code, tabelle in uebersetzungen.INHALT.items():
        assert alt not in tabelle["texte"], code
        assert tabelle["texte"]["Sektion 4 · Arzt & Gesundheit"] == NAME[code]
    with open(os.path.join(wurzel, "data", "vocabulary.json"), encoding="utf-8") as f:
        sektionen = json.load(f)["sections"]
    gefunden = next(s for s in sektionen if s["id"] == "koerpergesundheit")
    assert gefunden["label"] == NAME
