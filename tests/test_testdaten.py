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
import re

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


def _app_grenzen(wurzel):
    """Muenzen je Lerntag und Preise des Zierrats, so wie web/index.html sie
    rechnet - nicht abgeschrieben, sonst merkt niemand, wenn sie wandern."""
    with io.open(os.path.join(wurzel, "web", "index.html"), encoding="utf-8") as f:
        html = f.read()
    konst = {"MUENZEN_PRO_QUEST": int(re.search(r"const MUENZEN_PRO_QUEST = (\d+);", html).group(1))}
    formel = re.search(r"const MUENZEN_JE_TAG_HOECHSTENS = ([^;]+);", html).group(1)
    je_tag = 1
    for faktor in formel.split("*"):
        faktor = faktor.strip()
        je_tag *= konst[faktor] if faktor in konst else int(faktor)
    preise = {m.group(1): int(m.group(2)) for m in
              re.finditer(r"\{id:'(\w+)',\s*gruppe:'\w+',\s*preis:(\d+)\}", html)}
    return je_tag, preise


@pytest.mark.parametrize("name", DATEIEN)
def test_kommt_beim_einlesen_vollstaendig_an(wurzel, sicherungen, name):
    """Gegenpruefung 17.10.2026: die Dateien versprachen 999999 Muenzen und
    vier Stuecke Zierrat fuer 6000, beim Einlesen kamen 1860 Muenzen an.
    Seitdem steht nur drin, was sicherungPlausibel() annimmt: hoechstens
    60 Muenzen je Lerntag und ein Tag dazu, nur kaufbarer Zierrat, und der
    ist bezahlt. Ob es im Browser wirklich unveraendert ankommt, prueft
    tests_e2e/test_sicherung_haerten.py."""
    import testdaten_bauen
    je_tag, preise = _app_grenzen(wurzel)
    assert testdaten_bauen.MUENZEN_JE_TAG == je_tag, "MUENZEN_JE_TAG weicht von web/index.html ab"
    s = sicherungen[name]["stand"]
    assert s["muenzen_ges"] <= je_tag * (len(set(s["tage"])) + 1), HINWEIS
    unbekannt = [w for w in s["besitz"] if w not in preise]
    assert not unbekannt, "nicht kaufbar: %s" % unbekannt
    if name == "zmaj-test-vollversion.json":
        assert testdaten_bauen.GEKAUFT == {w: preise[w] for w in testdaten_bauen.GEKAUFT}, \
            "Preise in GEKAUFT weichen von ZIERRAT ab"
    assert sum(preise[w] for w in s["besitz"]) <= s["muenzen_aus"] <= s["muenzen_ges"], HINWEIS
    assert all(w in s["besitz"] for w in s["getragen"].split(",") if w)


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
