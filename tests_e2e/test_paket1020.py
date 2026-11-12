# -*- coding: utf-8 -*-
"""Wortschatz-Pakete 10 bis 20 im Browser (07.11.2026, Stufe B2).

- iznajmiti heisst jetzt „vermieten“, produžni kabl wird produžni kabel, zaposlenik
  bekommt die zweite Form uposlenik: Wer das alte Wort gelernt hat, behaelt seinen
  Lernstand (UMBENANNT), beim Tippen zaehlt jede Form.
- Was die Pakete beim Einbau nicht zusammen in eine Auswahl stellen, steht in
  NIE_NEBENEINANDER (unuk / unuka, začin / začini, dosad / dosada neben dosada ...).
- Neue Paare mit einem alten Verb verhalten sich wie Paket 1 bis 9, auch izvršiti mit
  seinen zwei Partnern (vršiti, izvršavati).
- Was Ajdin freigegeben hat, zaehlt beim Tippen; was er ausgeschlossen hat, nicht.
- Die Sektionen 18 bis 31 (Stufe B2) stehen am Ende des Lernpfads, die Farben gehen
  reihum weiter.
"""
from test_aspektpaare import AUSWAHL, HINWEIS
from test_tippfehler import EINGEBEN, LAGE, LEGEN, STARTEN, _ist_hinweis

UMBENANNT = {"mieten:iznajmiti": "vermieten:iznajmiti",
             "verlängerungskabel:produžni kabl": "verlängerungskabel:produžni kabel",
             "arbeitnehmer:zaposlenik": "arbeitnehmer:zaposlenik / uposlenik"}


def _eingeben(seite, text, ms=250):
    seite.js(EINGEBEN, [text, ms])
    return seite.js(LAGE, "")


def test_lernstand_zieht_auf_die_neue_kennung(seite, heute_stand):
    alt = list(UMBENANNT)
    seite.starten(stand=heute_stand(gewusst=alt + ["brot:hljeb"],
                                    topf={"w:" + alt[1]: {"typ": "type", "n": 1, "z": 123}},
                                    stern={"w:" + alt[2]: {"z": 50, "r": 7}}))
    j = seite.js("""() => ({known: [...known], topf: Object.keys(topf), stern: Object.keys(stern)})""")
    for a, n in UMBENANNT.items():
        assert n in j["known"] and a not in j["known"], (a, n)
    assert "brot:hljeb" in j["known"]
    assert "w:" + UMBENANNT[alt[1]] in j["topf"] and "w:" + alt[1] not in j["topf"]
    assert "w:" + UMBENANNT[alt[2]] in j["stern"] and "w:" + alt[2] not in j["stern"]
    assert seite.fehler == []


def test_jede_form_zaehlt_beim_tippen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, getippt in (("arbeitnehmer:zaposlenik / uposlenik", "uposlenik"),
                          ("überzeugen:uvjeriti / ubijediti", "ubjediti"),
                          ("einerseits:s jedne strane", "sa jedne strane"), ("trotz:uprkos", "usprkos"),
                          ("bisher:dosad / dosada", "dosada"), ("staatsanwalt:tužilac", "tužitelj"),
                          ("streichholz:šibica", "šibice"), ("du hast recht.:U pravu si.", "Imaš pravo."),
                          ("tot:mrtav", "mrtva"), ("überhaupt:uopšte", "uopće")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        lage = _eingeben(seite, getippt)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, getippt, lage)
    assert seite.fehler == []


def test_ausgeschlossene_formen_zaehlen_nicht(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    # Nur Formen, die mehr als einen Buchstaben entfernt sind: kabl oder do sada gaeben
    # erst „Fast richtig!“ (Tippfehler), das prueft tests_e2e/test_tippfehler.py.
    for ziel, getippt in (("überall:svugdje", "svuda"), ("damit / um zu:kako bi / kako bih", "kako bismo"),
                          ("erziehung:odgoj", "vaspitanje"), ("überholen:preticati", "prestizati")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        lage = _eingeben(seite, getippt)
        assert lage["ergebnis"] is False and lage["leben"] == leben - 1, (ziel, getippt, lage)
    assert seite.fehler == []


def test_nie_nebeneinander_in_der_auswahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for wort, anderes in (("enkel:unuk", "enkelin:unuka"), ("gewürz:začin", "gewürze:začini"),
                          ("bisher:dosad / dosada", "langeweile:dosada"),
                          ("bescheid (verwaltungsakt):rješenje / upravni akt", "lösung:rješenje")):
        e = seite.js(AUSWAHL, [wort, anderes, 300])
        assert e["gesehen"] == 0, (wort, anderes, e)
        assert e["geschwister"] and not e["annehmbar"], (wort, anderes, e)
    assert seite.fehler == []


def test_neue_paare_nie_zusammen_in_der_auswahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for wort, partner in (("vermieten:iznajmljivati", "vermieten:iznajmiti"),     # partner am alten Verb
                          ("mieten:unajmiti", "mieten:unajmljivati"),
                          ("fragen:upitati", "fragen:pitati"),
                          ("durchführen / ausführen:izvršavati", "durchführen / ausführen:izvršiti"),
                          ("durchführen / ausführen:izvršiti", "durchführen / ausführen:vršiti"),
                          ("anheben / aufheben (umgangssprachlich):dići",
                           "anheben / aufheben (umgangssprachlich):dizati")):
        e = seite.js(AUSWAHL, [wort, partner, 300])
        assert e["gesehen"] == 0, (wort, partner, e)
        assert e["geschwister"] and not e["annehmbar"], (wort, partner, e)
    assert seite.fehler == []


def test_anderes_verb_des_paares_ist_fast_richtig(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, partner, richtig in (("vermieten:iznajmiti", "iznajmljivati", "iznajmiti"),
                                   ("durchführen / ausführen:izvršavati", "izvršiti", "izvršavati"),
                                   ("überzeugen:uvjeriti / ubijediti", "uvjeravati", "uvjeriti")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        _ist_hinweis(_eingeben(seite, partner), partner, leben, HINWEIS)
        lage = _eingeben(seite, richtig)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, lage)
    assert seite.fehler == []


def test_sektionen_achtzehn_bis_einunddreissig_im_lernpfad(seite, heute_stand):
    seite.starten(stand=heute_stand())
    e = seite.js("""() => ({sektionen: SECTIONS.slice(17).map(s => s.id),
        farben: SECTIONS.slice(17).map(s => sektionsNummer(s.id)),
        level: SECTIONS.slice(17).map(s => CATEGORIES.filter(c => c.sektion === s.id).length),
        tun: CATEGORIES.filter(c => c.sektion === 'tunlassen').length,
        letzte: CATEGORIES[CATEGORIES.length - 1].id})""")
    assert e == {"sektionen": ["denkenmeinen", "menschenbeziehungen", "arbeitwirtschaft", "medienkultur",
                               "umwelttechnik", "gesellschaftpolitik", "rechtbehoerden", "hauswohnung",
                               "gesundheitsport", "schulewissen", "stadtreisen", "landtiere",
                               "handelnveraendern", "genauersagen"],
                 "farben": ["9", "1", "2", "3", "4", "5", "6", "7", "8", "9", "1", "2", "3", "4"],
                 "level": [12, 10, 12, 8, 3, 5, 9, 8, 14, 12, 7, 6, 11, 12], "tun": 39, "letzte": "mengen_masse"}
    assert seite.fehler == []
