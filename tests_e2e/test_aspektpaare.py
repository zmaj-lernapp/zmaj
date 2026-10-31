# -*- coding: utf-8 -*-
"""Aspektpaare im Browser (Wortschatz-Paket 1, 31.10.2026).

ostati und ostajati heissen beide "bleiben", doći und dolaziti beide
"kommen". Ajdin: „beide wörter rein die sollen separat sein wenn einer
gelernt wurde dann ist der andere noch nicht gelernt“; vollendet/unvollendet
zeigt die App nicht an. Deshalb:

- in der Auswahl stehen die beiden nie zusammen - auch wenn ihre
  Bedeutungen verschieden dastehen (popiti "trinken / austrinken", piti
  "trinken");
- beim Tippen ist das Gegenstueck nicht richtig, sondern bekommt einmal
  "Fast richtig! Gemeint ist das andere Verb des Paares." - ohne Leben, ohne
  Ton, die Eingabe bleibt offen (derselbe Ablauf wie beim Tippfehler,
  tests_e2e/test_tippfehler.py);
- jedes der beiden hat seinen eigenen Lernstand.
"""
from test_tippfehler import EINGEBEN, LAGE, LEGEN, STARTEN, _ist_hinweis

HINWEIS = "Fast richtig! Gemeint ist das andere Verb des Paares."
HINWEIS_EN = "Almost right! It's the other verb of the pair."

# Je Wort viele Auswahl-Runden: das Gegenstueck darf in keiner auftauchen.
# pool: die Woerter, aus denen die Ablenker kommen - mit dem Gegenstueck
# darin, sonst bewiese das Ergebnis nichts.
AUSWAHL = r"""
([id, partner, n]) => {
  const f = wortNachId(id), p = wortNachId(partner);
  if(!f || !p) throw new Error('fehlt: ' + id + ' / ' + partner);
  const pool = f.c.words.concat(p.c.words);
  let gesehen = 0;
  for(let i = 0; i < n; i++){
    const opts = distractors(f.w, pool, 3);
    if(opts.some(o => o.bs === p.w.bs)) gesehen++;
  }
  return {gesehen, geschwister: geschwister(f.w).some(x => x.bs === p.w.bs),
          annehmbar: annehmbar(f.w).indexOf(p.w.bs) >= 0, partner: partnerAntworten(f.w)};
}
"""


def test_gegenstueck_nie_in_der_auswahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for wort, partner in (("bleiben:ostati", "bleiben:ostajati"),
                          ("bleiben:ostajati", "bleiben:ostati"),
                          ("kommen:dolaziti", "kommen:doći"),          # Partner aus einem alten Level
                          ("kommen:doći", "kommen:dolaziti"),          # partner steht nur am neuen Wort
                          ("trinken / austrinken:popiti", "trinken:piti"),   # verschiedene Bedeutung
                          ("trinken:piti", "trinken / austrinken:popiti")):
        e = seite.js(AUSWAHL, [wort, partner, 300])
        assert e["gesehen"] == 0, (wort, e)
        assert e["geschwister"] and not e["annehmbar"], (wort, e)
        assert e["partner"], (wort, e)
    assert seite.fehler == []


def test_gegenstueck_beim_tippen_ist_fast_richtig(seite, heute_stand):
    """ostajati statt ostati: der Paar-Hinweis, kein Leben weg, die Eingabe
    bleibt. Danach zaehlt ostati als richtig."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for ziel, partner, richtig in (("bleiben:ostati", "ostajati", "ostati"),
                                   ("kommen:doći", "dolaziti", "doći"),
                                   ("kommen:dolaziti", "Doci", "dolaziti"),        # ohne Haekchen, gross
                                   ("trinken / austrinken:popiti", "piti", "popiti"),
                                   ("hinausgehen / ausgehen:izlaziti", "izići", "izlaziti")):   # auch-Form
        leben = seite.js(LEGEN, ["Lx", "type", ziel])
        _ist_hinweis(_eingeben(seite, partner), partner, leben, HINWEIS)
        lage = _eingeben(seite, richtig)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, lage)
        assert lage["fb"] == "Tačno! ✓", (ziel, lage)
    assert seite.fehler == []


def test_gegenstueck_zweimal_ist_falsch(seite, heute_stand):
    """Ein Hinweis je Aufgabe: wer danach wieder das andere Verb tippt, hat
    es falsch - mit der Loesung und einem Leben weniger."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = seite.js(LEGEN, ["Lx", "type", "bleiben:ostati"])
    _ist_hinweis(_eingeben(seite, "ostajati"), "ostajati", leben, HINWEIS)
    seite.page.wait_for_timeout(1100)          # nach DOPPELT_MS ist es ein zweiter Versuch
    lage = _eingeben(seite, "ostajati")
    assert lage["ergebnis"] is False and lage["leben"] == leben - 1, lage
    assert lage["fb"] == "Richtig wäre: ostati", lage
    assert seite.fehler == []


def test_tippfehler_bleibt_wie_er_war(seite, heute_stand):
    """Ein Tippfehler am gemeinten Wort bekommt weiter das schlichte
    "Fast richtig!", ein fremdes Wort bleibt falsch."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = seite.js(LEGEN, ["Lx", "type", "bleiben:ostajati"])
    _ist_hinweis(_eingeben(seite, "ostajaty"), "ostajaty", leben, "Fast richtig!")
    leben = seite.js(LEGEN, ["Lx", "type", "bleiben:ostajati"])
    lage = _eingeben(seite, "doći")
    assert lage["ergebnis"] is False and lage["leben"] == leben - 1, lage
    assert seite.fehler == []


def test_hinweis_in_der_sprache_der_app(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="en")
    seite.js(STARTEN["Lx"])
    leben = seite.js(LEGEN, ["Lx", "type", "bleiben:ostati"])
    _ist_hinweis(_eingeben(seite, "ostajati"), "ostajati", leben, HINWEIS_EN)
    assert seite.fehler == []


def test_getrennter_lernstand(seite, heute_stand):
    """ostati richtig getippt: nur ostati ist gewusst, ostajati nicht."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    seite.js(LEGEN, ["Lx", "type", "bleiben:ostati"])
    lage = _eingeben(seite, "ostati")
    assert lage["ergebnis"] is True, lage
    gewusst = seite.js("() => [known.has('bleiben:ostati'), known.has('bleiben:ostajati')]")
    assert gewusst == [True, False]
    assert seite.fehler == []


def test_sektion_zehn_im_lernpfad(seite, heute_stand):
    """Sektion 10 traegt wieder die erste Farbe. Seit Paket 2 (31.10.2026)
    hat sie 14 Level, dahinter steht Sektion 11 mit der zweiten Farbe, und
    "partner" steht bei den neuen Paaren an beiden Woertern (63 + 2 x 43)."""
    seite.starten(stand=heute_stand())
    e = seite.js("""() => ({n: SECTIONS.length, letzte: SECTIONS[SECTIONS.length - 1].id,
        farbe: sektionsNummer('tunlassen'), level: CATEGORIES.filter(c => c.sektion === 'tunlassen').length,
        farbe11: sektionsNummer('wieetwasist'),
        partnerFeld: CATEGORIES.flatMap(c => c.words).filter(w => w.partner).length})""")
    assert e == {"n": 11, "letzte": "wieetwasist", "farbe": "1", "level": 14, "farbe11": "2",
                 "partnerFeld": 149}
    assert seite.fehler == []


def _eingeben(seite, text, ms=250):
    seite.js(EINGEBEN, [text, ms])
    return seite.js(LAGE, "")
