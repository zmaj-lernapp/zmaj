# -*- coding: utf-8 -*-
"""Wortschatz-Paket 2 im Browser (31.10.2026).

- Die neuen Paare (gubiti / izgubiti, sačekati / čekati) verhalten sich wie
  die aus Paket 1 - auch vom alten Verb aus, an dem "partner" jetzt ebenfalls
  steht (tests_e2e/test_aspektpaare.py).
- Gleich geschriebene Woerter kommen nie zusammen in eine Auswahl: dug (lang)
  und dug (Schulden), jak (stark) und jako (sehr), pravi und pravo
  (geradeaus), težak und teško (schwierig), dug und duga (Regenbogen).
- Adjektive zeigen die maennliche Form, die weibliche und die saechliche
  sind beim Tippen richtig; dazu Ajdins weitere Formen (mek, kompliciran,
  okačiti).
- nalaziti (finden) und nalaziti se (sich befinden) gelten nicht als gleich.
"""
from test_aspektpaare import AUSWAHL, HINWEIS
from test_tippfehler import EINGEBEN, LAGE, LEGEN, STARTEN, _ist_hinweis


def _eingeben(seite, text, ms=250):
    seite.js(EINGEBEN, [text, ms])
    return seite.js(LAGE, "")


def test_neue_paare_nie_zusammen_in_der_auswahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for wort, partner in (("verlieren:gubiti", "verlieren:izgubiti"),
                          ("verlieren:izgubiti", "verlieren:gubiti"),       # partner am Verb aus Paket 1
                          ("warten:sačekati", "warten:čekati"),
                          ("warten:čekati", "warten:sačekati"),             # partner am Verb aus der App
                          ("wecken:buditi", "wecken:probuditi")):
        e = seite.js(AUSWAHL, [wort, partner, 300])
        assert e["gesehen"] == 0, (wort, e)
        assert e["geschwister"] and not e["annehmbar"], (wort, e)
        assert e["partner"], (wort, e)
    assert seite.fehler == []


def test_gleiche_schreibung_nie_zusammen_in_der_auswahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for wort, anderes in (("lang:dug", "schulden:dug"), ("schulden:dug", "lang:dug"),
                          ("lang:dug", "regenbogen:duga"), ("regenbogen:duga", "lang:dug"),
                          ("stark:jak", "sehr:jako"), ("sehr:jako", "stark:jak"),
                          ("echt:pravi", "geradeaus:pravo"), ("geradeaus:pravo", "echt:pravi"),
                          ("schwer (gewicht):težak", "schwierig:teško"),
                          ("schwierig:teško", "schwer (gewicht):težak")):
        e = seite.js(AUSWAHL, [wort, anderes, 300])
        assert e["gesehen"] == 0, (wort, anderes, e)
    assert seite.fehler == []


def test_mit_und_ohne_se_sind_verschiedene_woerter(seite, heute_stand):
    """In der Auswahl darf nalaziti se neben nalaziti stehen - es ist ein
    anderes Wort. Beim Tippen ist es falsch."""
    seite.starten(stand=heute_stand())
    e = seite.js(AUSWAHL, ["finden:nalaziti", "sich befinden:nalaziti se", 300])
    assert e["gesehen"] > 0 and not e["geschwister"] and not e["annehmbar"] and e["partner"] == "naći", e
    seite.js(STARTEN["Lx"])
    leben = seite.js(LEGEN, ["Lx", "type", "finden:nalaziti"])
    lage = _eingeben(seite, "nalaziti se")
    assert lage["ergebnis"] is False and lage["leben"] == leben - 1, lage
    assert seite.fehler == []


def test_weibliche_und_saechliche_form_zaehlen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, getippt in (("lang:dug", "duga"), ("lang:dug", "dugo"), ("stark:jak", "jako"),
                          ("weich:mekan", "meko"), ("weich:mekan", "mek"),
                          ("kompliziert:komplikovan", "kompliciran"),
                          ("aufhängen:objesiti", "okačiti"), ("putzen:počistiti", "očistiti")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        lage = _eingeben(seite, getippt)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, getippt, lage)
        assert lage["fb"] == "Tačno! ✓", (ziel, lage)
    assert seite.fehler == []


def test_altes_verb_des_paares_beim_tippen_ist_fast_richtig(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, partner, richtig in (("verlieren:gubiti", "izgubiti", "gubiti"),
                                   ("verlieren:izgubiti", "gubiti", "izgubiti"),
                                   ("putzen:čistiti", "očistiti", "čistiti")):    # auch-Form des Partners
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        _ist_hinweis(_eingeben(seite, partner), partner, leben, HINWEIS)
        lage = _eingeben(seite, richtig)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, lage)
    assert seite.fehler == []


def test_sektion_elf_im_lernpfad(seite, heute_stand):
    seite.starten(stand=heute_stand())
    e = seite.js("""() => ({level: CATEGORIES.filter(c => c.sektion === 'wieetwasist').map(c => c.id),
        vor: CATEGORIES.slice(73, 79).map(c => c.id)})""")
    assert e == {"level": ["lang_kurz", "voll_leer", "moeglich", "wie_jemand_ist", "benehmen", "glueck_sorgen",
                           "sinne"],
                 "vor": ["paare_geben", "paare_denken", "paare_alltag", "im_haushalt", "passieren", "notfall"]}
    assert seite.fehler == []
