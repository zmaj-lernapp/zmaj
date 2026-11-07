# -*- coding: utf-8 -*-
"""Wortschatz-Pakete 10 bis 20 in den sieben Sprachen im Browser (07.11.2026).

- Die neuen Woerter zeigen die Uebersetzung, nicht den deutschen Text, auch die drei
  Ausnahmen unter "woerter": namirnica (der Schluessel "Lebensmittel" ist schon ein
  Level-Name), množina (Grammatik-Ueberschrift) und auf Schwedisch pitati / upitati
  (fråga heisst auch "Frage").
- mieten und vermieten heissen in jeder Sprache verschieden (iznajmiti ist seit dem
  Geruest "vermieten").
- In den Sektionen 18 bis 31 und in den aelteren Leveln mit neuen Texten ist keine
  Frage ein Teil eines falschen Knopfs (wie tests_e2e/test_antworten.py, dort fuer alle
  Level).
"""
import json

import pytest
from test_antworten import TEIL_DER_FRAGE, UNTERSCHIED_GEWOLLT

SPRACHEN = ["en", "tr", "sv", "nl", "nb", "da", "fr"]

# Aeltere Level mit neuen Texten: die Warteliste, unajmiti in immobilien und auf
# Schwedisch pitati in modal
ALTE_LEVEL = ["immobilien", "heben_ziehen", "lieben_fuerchten", "richtung_mass", "hilfe_hindernis",
              "stimmung_streit", "krieg_recht", "glaube_gedenken", "ganz_viele", "eigenschaften",
              "wie_man_es_meint", "saetze_verbinden", "praepositionen_mehr", "modal"]
TEIL_IM_NEUEN = TEIL_DER_FRAGE.replace(
    "for(const c of CATEGORIES){",
    "for(const c of CATEGORIES.filter(c => SECTIONS.slice(17).some(s => s.id === c.sektion)"
    " || %s.includes(c.id))){" % json.dumps(ALTE_LEVEL))
assert TEIL_IM_NEUEN != TEIL_DER_FRAGE

BEDEUTUNG = r"""
(ids) => ids.map(id => {
  for(const c of CATEGORIES){
    const w = c.words.find(x => x.id === id);
    if(w) return w.de;
  }
  return null;
})
"""

# (Kennung, deutscher Schluessel in "texte", bosnisches Wort)
WOERTER = [("vermieten:iznajmiti", "vermieten", "iznajmiti"),
           ("mieten:unajmiti", "mieten", "unajmiti"),
           ("lebensmittel:namirnica", "Lebensmittel", "namirnica"),
           ("mehrzahl:množina", "Mehrzahl", "množina"),
           ("fragen:upitati", "fragen", "upitati"),
           ("fragen:pitati", "fragen", "pitati")]


def _erwartet(code, de, bs):
    import uebersetzungen
    u = uebersetzungen.INHALT[code]
    return u["woerter"].get(bs) or u["texte"][de]


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_neue_woerter_in_der_sprache(seite, heute_stand, sprache):
    seite.starten(stand=heute_stand(), sprache=sprache)
    gezeigt = seite.js(BEDEUTUNG, [w[0] for w in WOERTER])
    assert gezeigt == [_erwartet(sprache, de, bs) for _, de, bs in WOERTER]
    vermieten, mieten = gezeigt[0], gezeigt[1]
    assert vermieten != mieten and vermieten not in ("vermieten", "Vermieten")
    if sprache == "sv":
        assert gezeigt[4] == gezeigt[5] == "ställa en fråga"
    assert seite.fehler == []


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_frage_ist_nie_ein_teil_eines_falschen_knopfs_in_b2(seite, heute_stand, sprache):
    seite.starten(stand=heute_stand(), sprache=sprache)
    rest = [p for p in seite.js(TEIL_IM_NEUEN) if not {p[1], p[3]} == UNTERSCHIED_GEWOLLT]
    assert rest == []
    assert seite.fehler == []
