# -*- coding: utf-8 -*-
"""Überschriften der Store-Bilder (store/bilder_machen/beschriften.py).

Geprüft wird ohne Browser:
  - Jede Sprache hat genau eine Überschrift je Bild, in derselben Reihenfolge
    wie die Aufnahmen in bilder_playwright.py.
  - Feste Wendungen bleiben in einer Zeile: Das geschützte Leerzeichen
    (U+00A0) ist unsichtbar und geht beim Bearbeiten leicht verloren. Ohne
    brach Bild 4 auf Deutsch als „Sätze Wort für / Wort bauen“ um
    (Prüfung 13.11.2026), auf Türkisch „kelime / kelime“.
  - Store-Bilder 1.4 (16.11.2026): bilder_playwright.py markiert alle
    Abzeichen als gesehen (sonst „Du hast schon 5 Abzeichen“ auf Bild 1),
    und Bild 2 öffnet B1 nur für sich - Bild 3 stellt den Stand wieder her.
  - Nachbesserung 16.11.2026: keine halbe Schriftzeile unten auf Bild 2 und
    auf Bild 8 der Tablets, und Bild 8 zeigt die Tagesaufgaben wie Bild 1.
"""
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WURZEL, "store", "bilder_machen"))

import beschriften  # noqa: E402

BP = beschriften.BP


def _app():
    with open(os.path.join(WURZEL, "web", "index.html"), encoding="utf-8") as f:
        return f.read()

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


def test_alle_abzeichen_gelten_als_gesehen():
    """Jedes Abzeichen aus ERFOLGE, unter dem Schlüssel, den die App liest."""
    app = _app()
    ids = BP.erfolge_ids()
    liste = app.split("const ERFOLGE = [", 1)[1].split("];", 1)[0]
    assert ids and len(ids) == len(set(ids)) == liste.count("{id:")
    assert "const ERFOLG_GESEHEN = '%s';" % BP.ERFOLG_GESEHEN in app


def test_bild2_oeffnet_b1_nur_fuer_sich():
    schritte = dict(BP.SCHRITTE)
    assert "window.__bestandenVorher = new Set(passed)" in schritte["02-amt"]
    assert "passed = window.__bestandenVorher" in schritte["03-neues-wort"]
    # Was Bild 2 aus der App braucht, gibt es dort unter diesem Namen
    app = _app()
    for name in ("STUFEN", "reiterLevel", "stufeVon", "firstOpen"):
        assert re.search(r"^const %s = " % name, app, re.M), name
    for name in ("stufeWaehlen", "sektionAufklappen"):
        assert re.search(r"^function %s\(" % name, app, re.M), name
    assert re.search(r"^let [^\n]*\bpassed = new Set\(\)", app, re.M)
    assert 'id="reiterLeiste"' in app and 'id="btnProfil"' in app


def test_keine_halbe_zeile_unten():
    """Bild 2 sucht einen Abstand der Reiterleiste ohne halbe Schriftzeile am
    unteren Rand, Bild 8 bricht auf Tablets mit einer ab, und jede andere
    meldet die Ausgabe (Prüfung 16.11.2026: fr Bild 2, da tab7 Bild 8)."""
    schritte = dict(BP.SCHRITTE)
    assert "window.__untenAngeschnitten = () =>" in BP.UNTEN_ANGESCHNITTEN
    assert "if(!window.__untenAngeschnitten().length){ weg = [el, a]; break; }" in schritte["02-amt"]
    assert 'id="modeWords"' in _app()   # die Leiste Lernpfad/Geschichten/Wiederholen
    assert "throw new Error('Bild 8 unten angeschnitten: '" in schritte["08-wiederholen"]
    assert re.search(r"^function rectFaktor\(", _app(), re.M)


def test_bild8_tagesaufgaben_wie_bild1():
    """Vor Bild 8 stehen die Tagesaufgaben wieder wie auf Bild 1: Bild 4 bis 6
    erfüllten auf da tab7 alle drei, und die Zeile "Alle tre klaret!" schob
    die Seite so weit hinunter, dass unten eine Zeile halb im Bild stand."""
    schritte = dict(BP.SCHRITTE)
    assert "window.__tagwerk01 = JSON.stringify(tagwerk[t]);" in schritte["01-start"]
    assert "tagwerk[today()] = JSON.parse(window.__tagwerk01);" in schritte["08-wiederholen"]
    app = _app()
    assert re.search(r"^let tagwerk = \{\};", app, re.M)
    assert re.search(r"^const today = \(\) =>", app, re.M)
