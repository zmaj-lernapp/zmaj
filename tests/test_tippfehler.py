# -*- coding: utf-8 -*-
"""Der Tippfehler-Hinweis (24.10.2026) hat seinen Text in allen Sprachen.

Ajdin: "wenn man beim schreiben ausversehen einen buchstaben falsch
geschrieben hat dann soll ein hinweis kommen das wort ist falsch geschrieben
und nicht das es direkt falsch ist". Der Hinweis darf die Loesung nicht
verraten - also kein Platzhalter wie {wort}, anders als task.fast und
task.falsch. Der Ablauf selbst steht in tests_e2e/test_tippfehler.py.
"""
import io
import os
import re

import sprachen

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_hinweis_in_allen_acht_sprachen(sprachcodes):
    assert sprachcodes == ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
    gesehen = set()
    for code in sprachcodes:
        text = sprachen.TEXTE[code].get("task.tippfehler")
        assert text and text.strip() == text, code
        assert "{" not in text and "}" not in text, "verraet die Loesung: " + code
        assert text != sprachen.TEXTE[code]["task.fast"], code
        assert text not in gesehen, "nicht uebersetzt: " + code
        gesehen.add(text)
    # Franzoesisch wie die Nachbarn: geschuetztes Leerzeichen vor "!"
    assert "\xa0!" in sprachen.TEXTE["fr"]["task.tippfehler"]
    assert " !" not in sprachen.TEXTE["fr"]["task.tippfehler"]


def test_app_fragt_genau_diesen_schluessel():
    html = io.open(os.path.join(WURZEL, "web", "index.html"), encoding="utf-8").read()
    assert re.findall(r"t\('task\.tippfehler'\)", html), "index.html zeigt den Hinweis nicht"


def test_endungs_hinweis_in_allen_acht_sprachen(sprachcodes):
    """Im Lueckensatz bekommt seit dem 27.10.2026 auch eine andere Endung
    einen Hinweis (Ajdin: "Auch bei Endung Hinweis"). Er hat einen eigenen
    Text, der die Endung nennt und nicht von einem Tippfehler spricht, und
    faengt mit demselben "Fast!" an. Auch er verraet die Loesung nicht."""
    assert sprachen.TEXTE["de"]["task.endung"] == "Fast! Achte auf die Endung."
    gesehen = set()
    for code in sprachcodes:
        texte = sprachen.TEXTE[code]
        text = texte.get("task.endung")
        assert text and text.strip() == text, code
        assert "{" not in text and "}" not in text, "verraet die Loesung: " + code
        assert text not in (texte["task.fast"], texte["task.tippfehler"]), code
        assert text.split()[0] == texte["task.tippfehler"].split()[0], code
        assert text not in gesehen, "nicht uebersetzt: " + code
        gesehen.add(text)
    assert "\xa0!" in sprachen.TEXTE["fr"]["task.endung"]
    assert " !" not in sprachen.TEXTE["fr"]["task.endung"]


def test_app_fragt_den_endungs_schluessel():
    html = io.open(os.path.join(WURZEL, "web", "index.html"), encoding="utf-8").read()
    assert re.findall(r"t\('task\.endung'\)", html), "index.html zeigt den Endungs-Hinweis nicht"
