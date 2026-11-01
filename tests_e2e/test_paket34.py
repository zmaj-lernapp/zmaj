# -*- coding: utf-8 -*-
"""Wortschatz-Pakete 3 und 4 im Browser (01.11.2026).

- izabrati („sich entscheiden / wählen“) und birati („auswählen / wählen“)
  haben verschiedene Bedeutungen und sind trotzdem ein Paar: nie zusammen
  in einer Auswahl, das andere Verb beim Tippen ist "Fast richtig!".
- Die neuen Paare mit einem Verb aus Paket 1 oder 2 verhalten sich wie
  dort, auch vom alten Verb aus (misliti / pomisliti, sušiti / osušiti).
- Gleich geschriebene Woerter kommen nie zusammen in eine Auswahl: jezik
  (Zunge / Sprache), vrijeme (Zeit / Wetter).
- vratiti (zurueckgeben) und vratiti se (zurueckkommen) sind verschiedene
  Woerter: in der Auswahl erlaubt, beim Tippen falsch.
- Was Ajdin freigegeben hat, zaehlt beim Tippen (nogomet, naočare, prije
  podne, zarazna); was er ausgeschlossen hat, nicht (ranac, grudi,
  rentgen, odabrati).
- Die Sektionen 12 bis 14 stehen am Ende des Lernpfads.
"""
from test_aspektpaare import AUSWAHL, HINWEIS
from test_tippfehler import EINGEBEN, LAGE, LEGEN, STARTEN, _ist_hinweis


def _eingeben(seite, text, ms=250):
    seite.js(EINGEBEN, [text, ms])
    return seite.js(LAGE, "")


def test_neue_paare_nie_zusammen_in_der_auswahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for wort, partner in (("sich entscheiden / wählen:izabrati", "auswählen / wählen:birati"),
                          ("auswählen / wählen:birati", "sich entscheiden / wählen:izabrati"),
                          ("denken / meinen:misliti", "denken / meinen:pomisliti"),    # partner am Verb aus Paket 1
                          ("trocknen:sušiti", "trocknen:osušiti"),                     # partner am Verb aus Paket 2
                          ("schlucken:gutati", "schlucken:progutati"),
                          ("wiederholen:ponoviti", "wiederholen:ponavljati")):
        e = seite.js(AUSWAHL, [wort, partner, 300])
        assert e["gesehen"] == 0, (wort, e)
        assert e["geschwister"] and not e["annehmbar"], (wort, e)
        assert e["partner"], (wort, e)
    assert seite.fehler == []


def test_anderes_verb_des_paares_ist_fast_richtig(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, partner, richtig in (("sich entscheiden / wählen:izabrati", "birati", "izabrati"),
                                   ("auswählen / wählen:birati", "izabrati", "birati"),
                                   ("sparen:štedjeti", "uštediti", "štedjeti"),      # auch-Form des Partners
                                   ("erfahren:saznati", "saznavati", "saznati")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        _ist_hinweis(_eingeben(seite, partner), partner, leben, HINWEIS)
        lage = _eingeben(seite, richtig)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, lage)
    assert seite.fehler == []


def test_gleiche_schreibung_nie_zusammen_in_der_auswahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for wort, anderes in (("zunge:jezik", "sprache:jezik"), ("sprache:jezik", "zunge:jezik"),
                          ("zeit:vrijeme", "wetter:vrijeme"), ("wetter:vrijeme", "zeit:vrijeme")):
        e = seite.js(AUSWAHL, [wort, anderes, 300])
        assert e["gesehen"] == 0, (wort, anderes, e)
    assert seite.fehler == []


def test_mit_und_ohne_se_sind_verschiedene_woerter(seite, heute_stand):
    """vratiti se darf in der Auswahl neben vratiti stehen - es ist ein
    anderes Wort. Beim Tippen ist es falsch."""
    seite.starten(stand=heute_stand())
    e = seite.js(AUSWAHL, ["zurückgeben:vratiti", "zurückkommen:vratiti se", 300])
    assert e["gesehen"] > 0 and not e["geschwister"] and not e["annehmbar"] and e["partner"] == "vraćati", e
    seite.js(STARTEN["Lx"])
    leben = seite.js(LEGEN, ["Lx", "type", "zurückgeben:vratiti"])
    lage = _eingeben(seite, "vratiti se")
    assert lage["ergebnis"] is False and lage["leben"] == leben - 1, lage
    assert seite.fehler == []


def test_freigegebene_formen_zaehlen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, getippt in (("fußball:fudbal", "nogomet"), ("brille:naočale", "naočare"),
                          ("vormittag:prijepodne", "prije podne"), ("ansteckend:zarazan", "zarazna"),
                          ("herzinfarkt:srčani udar / infarkt", "infarkt"), ("mannschaft:ekipa", "tim"),
                          ("arbeitslos:nezaposlen", "nezaposleno")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        lage = _eingeben(seite, getippt)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, getippt, lage)
        assert lage["fb"] == "Tačno! ✓", (ziel, lage)
    assert seite.fehler == []


def test_ausgeschlossene_formen_zaehlen_nicht(seite, heute_stand):
    """Ajdin: ranac ist serbisch, grudi die weibliche Brust, seljak nicht der
    Landwirt, odabrati kommt spaeter als eigenes Wort."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, getippt in (("rucksack:ruksak", "ranac"), ("brust:prsa", "grudi"),
                          ("landwirt:poljoprivrednik", "seljak"),
                          ("sich entscheiden / wählen:izabrati", "odabrati")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        lage = _eingeben(seite, getippt)
        assert lage["ergebnis"] is False and lage["leben"] == leben - 1, (ziel, getippt, lage)
    assert seite.fehler == []


def test_ausgeschlossen_und_einen_buchstaben_daneben(seite, heute_stand):
    """prepisati (abschreiben) und rentgen liegen einen Buchstaben neben
    propisati und rendgen: wie jeder Tippfehler erst "Fast richtig!" ohne
    Leben (Ajdin, 24./27.10.2026), beim zweiten Mal falsch - richtig sind
    sie nie."""
    from test_tippfehler import HINWEIS as TIPPFEHLER
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, getippt in (("verschreiben:propisati", "prepisati"), ("röntgen:rendgen", "rentgen")):
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        _ist_hinweis(_eingeben(seite, getippt), getippt, leben, TIPPFEHLER)
        seite.page.wait_for_timeout(1100)          # nach DOPPELT_MS ist es ein zweiter Versuch
        lage = _eingeben(seite, getippt)
        assert lage["ergebnis"] is False and lage["leben"] == leben - 1, (ziel, getippt, lage)
    assert seite.fehler == []


def test_sektionen_zwoelf_bis_vierzehn_im_lernpfad(seite, heute_stand):
    seite.starten(stand=heute_stand())
    e = seite.js("""() => ({sektionen: SECTIONS.slice(11).map(s => s.id),
        farben: SECTIONS.slice(11).map(s => sektionsNummer(s.id)),
        level: SECTIONS.slice(11).map(s => CATEGORIES.filter(c => c.sektion === s.id).length),
        letzte: CATEGORIES[CATEGORIES.length - 1].id})""")
    assert e == {"sektionen": ["koerpergesundheit", "zeitfreizeit", "lernenarbeiten"], "farben": ["3", "4", "5"],
                 "level": [8, 6, 4], "letzte": "arbeitsplatz"}
    assert seite.fehler == []
