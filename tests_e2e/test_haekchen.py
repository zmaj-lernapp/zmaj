# -*- coding: utf-8 -*-
"""Fehlende Haekchen im Browser: "pada kisa" fuer "Pada kiša" (12.11.2026).

Die Regel selbst und die Faelle stehen in tests/test_haekchen.py. Hier der
sichtbare Ablauf in Schreibaufgabe und Lueckensatz, in Lektion, Level-Test
und Einstufung: richtig, kein Leben weg, der Ton fuer richtig, und die
Rueckmeldung "Richtig! Mit Sonderzeichen: ..." nennt die Schreibweise der
Antwort, die getippt wurde. Mit einem Tippfehler dazu kommt erst "Fast
richtig!" wie bei jedem Wort.
"""
import pytest

from test_tippfehler import EINGEBEN, LAGE, LEGEN, STARTEN, _ist_hinweis

SONDER = "Richtig! Mit Sonderzeichen: "


def _legen(seite, art, typ, ziel):
    return seite.js(LEGEN, [art, typ, ziel])


def _eingeben(seite, text, loesung=""):
    seite.js(EINGEBEN, [text, 250])
    return seite.js(LAGE, loesung)


def _sonderzeichen(lage, wort, leben):
    assert lage["ergebnis"] is True and lage["leben"] == leben, lage
    assert lage["fb"] == SONDER + wort and "almost" in lage["klasse"].split(), lage
    assert lage["toene"] == ["ok"] and not lage["offen"] and lage["loesung"], lage


@pytest.mark.parametrize("art", ["Lx", "Tx", "Ex"])
def test_pada_kisa_ueberall(seite, heute_stand, art):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN[art])
    for getippt in ("pada kisa", "PADA KISA", "Pada kisa!"):
        leben = _legen(seite, art, "type", "es regnet:Pada kiša")
        _sonderzeichen(_eingeben(seite, getippt), "Pada kiša", leben)
    leben = _legen(seite, art, "gap", "Pada ___.|kiša")
    _sonderzeichen(_eingeben(seite, "kisa"), "kiša", leben)
    assert seite.fehler == []


@pytest.mark.parametrize("ziel, getippt, wort", [
    ("ćevapi:ćevapi", "cevapi", "ćevapi"),
    ("ćevapi:ćevapi", "CEVAPI", "ćevapi"),
    ("kupferkännchen:džezva", "dzezva", "džezva"),
    ("auf wiedersehen:Doviđenja", "cao", "Ćao"),            # die weitere Antwort, nicht Doviđenja
    ("auf die gesundheit!:U zdravlje!", "zivjeli", "Živjeli!"),
    ("vier:četiri", "cetiri", "četiri"),                    # bis 12.11.2026 "Tačno!" ohne Schreibweise
    ("fünf brüder:pet braće", "5 brace", "pet braće"),       # bis 12.11.2026 falsch
])
def test_schreibaufgabe_zeigt_die_getippte_antwort(seite, heute_stand, ziel, getippt, wort):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "type", ziel)
    _sonderzeichen(_eingeben(seite, getippt), wort, leben)
    assert seite.fehler == []


def test_lueckensatz_mit_weiterer_antwort(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for satz, getippt, wort in (("Kahva je u ___.|džezvi", "dzezvi", "džezvi"),
                                ("Moj ___ je pčelar.|amidža", "adzo", "adžo"),
                                ("Moj ___ je pčelar.|amidža", "amidza", "amidža")):
        leben = _legen(seite, "Lx", "gap", satz)
        _sonderzeichen(_eingeben(seite, getippt), wort, leben)
    assert seite.fehler == []


def test_ziffer_und_richtige_haekchen_bleiben_tacno(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, getippt in (("vier:četiri", "4"), ("es regnet:Pada kiša", "pada kiša"),
                          ("es regnet:Pada kiša", "Pada kiša")):
        leben = _legen(seite, "Lx", "type", ziel)
        lage = _eingeben(seite, getippt)
        assert lage["ergebnis"] is True and lage["fb"] == "Tačno! ✓" and lage["leben"] == leben, (getippt, lage)
    assert seite.fehler == []


@pytest.mark.parametrize("art", ["Lx", "Tx", "Ex"])
def test_tippfehler_ohne_haekchen_gibt_erst_den_hinweis(seite, heute_stand, art):
    """Ein Tippfehler und dazu fehlende Haekchen: erst "Fast richtig!",
    danach gilt "pada kisa" wie immer. Auch mit Leerzeichen hinter dem "!"."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN[art])
    for vertippt in ("pada kisq", "pada kisq! "):
        leben = _legen(seite, art, "type", "es regnet:Pada kiša")
        _ist_hinweis(_eingeben(seite, vertippt, "pada kiša"), vertippt, leben)
        _sonderzeichen(_eingeben(seite, "pada kisa"), "Pada kiša", leben)
    assert seite.fehler == []
