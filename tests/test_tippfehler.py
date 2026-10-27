# -*- coding: utf-8 -*-
"""Der Hinweis "Fast richtig!" hat seinen Text in allen Sprachen.

Ajdin am 24.10.2026: "wenn man beim schreiben ausversehen einen buchstaben
falsch geschrieben hat dann soll ein hinweis kommen das wort ist falsch
geschrieben und nicht das es direkt falsch ist". Am 27.10.2026: "mach doch
einfach nur fast richtig dann bezieht es sich auf alle woerter" - seitdem
ein Text fuer jeden Fall (Tippfehler, andere Endung, anderes echtes Wort),
task.fast_richtig statt task.tippfehler und task.endung. Der Hinweis darf
die Loesung nicht verraten - also kein Platzhalter wie {wort}, anders als
task.fast und task.falsch. Der Ablauf selbst steht in
tests_e2e/test_tippfehler.py.
"""
import io
import os
import re

import sprachen

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _html():
    return io.open(os.path.join(WURZEL, "web", "index.html"), encoding="utf-8").read()


def test_hinweis_in_allen_acht_sprachen(sprachcodes):
    assert sprachcodes == ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
    assert sprachen.TEXTE["de"]["task.fast_richtig"] == "Fast richtig!"
    gesehen = set()
    for code in sprachcodes:
        text = sprachen.TEXTE[code].get("task.fast_richtig")
        assert text and text.strip() == text, code
        assert "{" not in text and "}" not in text, "verraet die Loesung: " + code
        assert text != sprachen.TEXTE[code]["task.fast"], code
        assert text not in gesehen, "nicht uebersetzt: " + code
        gesehen.add(text)
    # Franzoesisch wie die Nachbarn: geschuetztes Leerzeichen vor "!"
    assert "\xa0!" in sprachen.TEXTE["fr"]["task.fast_richtig"]
    assert " !" not in sprachen.TEXTE["fr"]["task.fast_richtig"]


def test_app_fragt_genau_diesen_schluessel():
    assert re.findall(r"t\('task\.fast_richtig'\)", _html()), "index.html zeigt den Hinweis nicht"


def test_die_alten_hinweise_sind_weg(sprachcodes):
    """Seit dem 27.10.2026 gibt es nur noch einen Text. Bliebe einer der
    alten Schluessel stehen, kaeme er in keiner Aufgabe mehr vor - und
    fragte die App ihn doch, sahe man den Schluessel statt eines Satzes."""
    html = _html()
    for alt in ("task.tippfehler", "task.endung"):
        assert "t('" + alt + "')" not in html, alt
        for code in sprachcodes:
            assert alt not in sprachen.TEXTE[code], (alt, code)
