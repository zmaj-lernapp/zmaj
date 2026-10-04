# -*- coding: utf-8 -*-
"""testdaten/: die Test-Sicherungen passen zum aktuellen Inhalt.

Anlass (04.10.2026): zmaj-test-vollversion.json hatte 1108 Woerter und
43 Level, der Kurs aber 1728 und 65. Das Skript war richtig, es war nur
seit dem Wachsen des Kurses nicht mehr gelaufen - und nichts hat es gemerkt.
Wer die Datei einlas, sah 22 Level "offen, aber nie bestanden" und hielt
das fuer einen Fehler der App.

Behebung, wenn hier etwas rot wird:  python3 testdaten_bauen.py
"""
import io
import json
import os

import pytest

DATEIEN = ("zmaj-test-vollversion.json", "zmaj-test-alles-offen.json")
HINWEIS = "testdaten/ ist veraltet - python3 testdaten_bauen.py laufen lassen"


@pytest.fixture(scope="module")
def sicherungen(wurzel):
    aus = {}
    for name in DATEIEN:
        with io.open(os.path.join(wurzel, "testdaten", name), encoding="utf-8") as f:
            aus[name] = json.load(f)
    return aus


@pytest.fixture(scope="module")
def inhalt(grunddaten):
    """Kennungen so, wie die App sie von inhalt.lade_daten() bekommt."""
    woerter = {w["id"] for k in grunddaten["kategorien"] for w in k["words"]}
    level = [k["id"] for k in grunddaten["kategorien"]]
    gelesen = [g["id"] for g in grunddaten["geschichten"]]
    return woerter, level, gelesen


@pytest.mark.parametrize("name", DATEIEN)
def test_alle_level_und_geschichten(sicherungen, inhalt, name):
    _, level, gelesen = inhalt
    s = sicherungen[name]["stand"]
    assert s["bestanden"] == level, HINWEIS
    assert s["gelesen"] == gelesen, HINWEIS


def test_vollversion_kennt_jedes_wort(sicherungen, inhalt):
    woerter, _, _ = inhalt
    gewusst = sicherungen["zmaj-test-vollversion.json"]["stand"]["gewusst"]
    assert len(gewusst) == len(set(gewusst)), "doppelte Kennungen"
    fehlen = sorted(woerter - set(gewusst))
    fremd = sorted(set(gewusst) - woerter)
    assert not fehlen, "%d Woerter fehlen, z. B. %s. %s" % (len(fehlen), fehlen[:5], HINWEIS)
    assert not fremd, "%d Kennungen gibt es nicht mehr, z. B. %s. %s" % (len(fremd), fremd[:5], HINWEIS)


def test_alles_offen_hat_nichts_gelernt(sicherungen):
    # Absicht, siehe testdaten_bauen.py: sonst gibt es keine Vorstellkarten.
    s = sicherungen["zmaj-test-alles-offen.json"]["stand"]
    assert s["gewusst"] == [] and s["besitz"] == [] and s["premium"] is False
    assert sicherungen["zmaj-test-vollversion.json"]["stand"]["premium"] is True


@pytest.mark.parametrize("name", DATEIEN)
def test_genau_wie_das_skript(sicherungen, name):
    """Alles ausser den Lerntagen (die haengen am Datum des Laufs) ist
    genau das, was testdaten_bauen.py heute schreiben wuerde. Faengt auch
    Handarbeit an den Dateien und neue Felder im Skript."""
    import testdaten_bauen
    datei = sicherungen[name]
    premium = name == "zmaj-test-vollversion.json"
    erwartet = testdaten_bauen.stand(premium, alles_gewusst=premium)
    tage = datei["stand"]["tage"]
    assert len(tage) == testdaten_bauen.LERNTAGE and tage == sorted(tage)
    erwartet["tage"] = tage
    assert datei["stand"] == erwartet, HINWEIS
