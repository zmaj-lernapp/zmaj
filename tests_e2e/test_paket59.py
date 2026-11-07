# -*- coding: utf-8 -*-
"""Wortschatz-Pakete 5 bis 9 im Browser (06.11.2026).

- doktor / ljekar, dozvoliti / dopustiti und dozvoljavati / dopuštati sind keine
  zweiten Woerter: Wer das alte Wort gelernt hat, behaelt seinen Lernstand
  (UMBENANNT, wie kahva / kafa), beim Tippen zaehlt jede Form.
- sav / cijeli, tu / ovdje, tako / ovako und vrlo / veoma / jako stehen nie zusammen
  in einer Auswahl (NIE_NEBENEINANDER), beim Tippen zaehlt das andere Wort nicht.
- Neue Paare mit einem alten Verb verhalten sich wie Paket 1 bis 4, auch povući mit
  seinen zwei Partnern.
- Was Ajdin freigegeben hat, zaehlt beim Tippen; was er ausgeschlossen hat, nicht.
- Die Sektionen 15 bis 17 stehen am Ende des Lernpfads.
"""
from test_aspektpaare import AUSWAHL, HINWEIS
from test_tippfehler import EINGEBEN, LAGE, LEGEN, STARTEN, _ist_hinweis

UMBENANNT = {"arzt:doktor": "arzt:doktor / ljekar",
             "erlauben:dozvoliti": "erlauben / zulassen:dozvoliti / dopustiti",
             "erlauben:dozvoljavati": "erlauben / zulassen:dozvoljavati / dopuštati"}


def _eingeben(seite, text, ms=250):
    seite.js(EINGEBEN, [text, ms])
    return seite.js(LAGE, "")


def test_lernstand_zieht_auf_die_neue_kennung(seite, heute_stand):
    alt = list(UMBENANNT)
    seite.starten(stand=heute_stand(gewusst=alt + ["brot:hljeb"],
                                    topf={"w:" + alt[0]: {"typ": "type", "n": 1, "z": 123}},
                                    stern={"w:" + alt[1]: {"z": 50, "r": 7}}))
    j = seite.js("""() => ({known: [...known], topf: Object.keys(topf), stern: Object.keys(stern)})""")
    for a, n in UMBENANNT.items():
        assert n in j["known"] and a not in j["known"], (a, n)
    assert "brot:hljeb" in j["known"]
    assert "w:" + UMBENANNT[alt[0]] in j["topf"] and "w:" + alt[0] not in j["topf"]
    assert "w:" + UMBENANNT[alt[1]] in j["stern"] and "w:" + alt[1] not in j["stern"]
    assert seite.fehler == []


def test_jede_form_zaehlt_beim_tippen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, getippt in (("arzt:doktor / ljekar", "doktor"), ("arzt:doktor / ljekar", "ljekar"),
                          ("erlauben / zulassen:dozvoliti / dopustiti", "dopustiti"),
                          ("erlauben / zulassen:dozvoljavati / dopuštati", "dozvoljavati"),
                          ("eigentlich:zapravo / ustvari", "ustvari"), ("eigentlich:zapravo / ustvari", "u stvari"),
                          ("wichtig (der wichtige):važan", "važna"), ("bedingung:uslov", "uvjet")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        lage = _eingeben(seite, getippt)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, getippt, lage)
    assert seite.fehler == []


def test_ausgeschlossene_formen_zaehlen_nicht(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, getippt in (("seite (buch, web):stranica", "strana"), ("zurück:nazad", "natrag"),
                          ("eigen:vlastit", "sopstven"), ("teilnehmen:učestvovati", "sudjelovati")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        lage = _eingeben(seite, getippt)
        assert lage["ergebnis"] is False and lage["leben"] == leben - 1, (ziel, getippt, lage)
    assert seite.fehler == []


def test_nie_nebeneinander_in_der_auswahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for wort, anderes in (("so:tako", "so (wie hier):ovako"), ("so (wie hier):ovako", "so:tako"),
                          ("ganz / all:sav", "ganz (der ganze):cijeli"), ("da / hier:tu", "hier:ovdje"),
                          ("sehr (vor eigenschaften):vrlo / veoma", "sehr:jako")):
        e = seite.js(AUSWAHL, [wort, anderes, 300])
        assert e["gesehen"] == 0, (wort, anderes, e)
        assert e["geschwister"] and not e["annehmbar"], (wort, anderes, e)
    assert seite.fehler == []


def test_neue_paare_nie_zusammen_in_der_auswahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for wort, partner in (("mitnehmen (sache):ponijeti", "tragen:nositi"),       # partner am alten Verb
                          ("aufnehmen / filmen:snimiti", "aufnehmen / filmen:snimati"),
                          ("ziehen / zurückziehen:povući", "ziehen:vući"),        # povući hat zwei Partner
                          ("ziehen / zurückziehen:povući", "ziehen / zurückziehen:povlačiti"),
                          ("erlauben / zulassen:dozvoliti / dopustiti", "erlauben / zulassen:dozvoljavati / dopuštati"),
                          ("betonen:naglasiti", "betonen:naglašavati")):
        e = seite.js(AUSWAHL, [wort, partner, 300])
        assert e["gesehen"] == 0, (wort, partner, e)
        assert e["geschwister"] and not e["annehmbar"], (wort, partner, e)
    assert seite.fehler == []


def test_anderes_verb_des_paares_ist_fast_richtig(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, partner, richtig in (("mitnehmen (sache):ponijeti", "nositi", "ponijeti"),
                                   ("ziehen / zurückziehen:povući", "vući", "povući"),
                                   ("ziehen / zurückziehen:povući", "povlačiti", "povući"),
                                   ("erlauben / zulassen:dozvoliti / dopustiti", "dopuštati", "dopustiti")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        _ist_hinweis(_eingeben(seite, partner), partner, leben, HINWEIS)
        lage = _eingeben(seite, richtig)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, lage)
    assert seite.fehler == []


def test_sektionen_fuenfzehn_bis_siebzehn_im_lernpfad(seite, heute_stand):
    seite.starten(stand=heute_stand())
    # Seit den Paketen 10 bis 20 (07.11.2026) folgen die Sektionen 18 bis 31 (Stufe B2),
    # tests_e2e/test_paket1020.py; hier die letzten drei von B1.
    e = seite.js("""() => ({sektionen: SECTIONS.slice(14, 17).map(s => s.id),
        farben: SECTIONS.slice(14, 17).map(s => sektionsNummer(s.id)),
        level: SECTIONS.slice(14, 17).map(s => CATEGORIES.filter(c => c.sektion === s.id).length),
        tun: CATEGORIES.filter(c => c.sektion === 'tunlassen').length,
        letzte: CATEGORIES[CATEGORIES.findIndex(c => c.id === 'grundlage_rahmen') - 1].id,
        macak: CATEGORIES.find(c => c.id === 'tiere').reihe})""")
    assert e == {"sektionen": ["grundbegriffe", "menschengesellschaft", "wiewowann"], "farben": ["6", "7", "8"],
                 "level": [12, 13, 12], "tun": 39, "letzte": "fuerwoerter",
                 "macak": ["mačak", "Naš mačak spava cijeli dan."]}
    assert seite.fehler == []
