# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026), Kleinfehler der Oberflaeche im Browser
(Offen-Liste 4).

S16: "Weiter zu B1 →" auf dem Testergebnis brach bei 360 px so um, dass der
Pfeil allein in der zweiten Zeile stand, auf Tuerkisch in einer dritten.
Jetzt steht vor dem Pfeil ein geschuetztes Leerzeichen, in test.weiter_stufe
und test.weiter_level, in allen acht Sprachen.
"""
import pytest

SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]

# Steht der Pfeil im Knopf #tNext in derselben Zeile wie das Zeichen davor?
PFEIL = r"""() => { const b = document.getElementById('tNext');
  const tn = [...b.childNodes].find(n => n.nodeType === 3 && n.textContent.includes('→'));
  const s = tn.textContent, i = s.lastIndexOf('→');
  let j = i - 1; while(j >= 0 && /\s/.test(s[j])) j--;
  const r = (a, e) => { const g = document.createRange(); g.setStart(tn, a); g.setEnd(tn, e); return g.getClientRects()[0]; };
  return {text: s, pfeil: r(i, i + 1).top, davor: r(j, j + 1).top, vorPfeil: s.charCodeAt(i - 1)}; }"""


def _test_bestehen(seite, i):
    seite.js("(i) => { catIdx = i; cur().words.forEach(w => known.add(w.id)); openLevel(i); startTest(); }", i)
    seite.durchspielen("tBody", "Tx")
    assert seite.js("(i) => passed.has(levelNach(i).id)", i)


def _bestanden(seite, levels):
    """Genau diese Level (Nummern in CATEGORIES) gelten als bestanden."""
    seite.js("(l) => { passed.clear(); l.forEach(i => passed.add(CATEGORIES[i].id)); }", levels)


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_s16_pfeil_nie_allein_in_der_zeile(seite, heute_stand, sprache):
    seite.starten(sprache=sprache, stand=heute_stand())
    a1, a2 = seite.js("() => [reiterLevel('A1'), reiterLevel('A2')]")
    # Weiter zu Level 5 → (test.weiter_level)
    _bestanden(seite, a1[:3])
    _test_bestehen(seite, a1[3])
    p = seite.js(PFEIL)
    assert p["text"] == seite.js("() => t('test.weiter_level', {n: 5})"), p
    assert p["vorPfeil"] == 0xA0, p
    assert abs(p["pfeil"] - p["davor"]) < 1, (sprache, p)
    # Weiter zu B1 → (test.weiter_stufe): das letzte Level von A2 bestanden
    _bestanden(seite, a1 + a2[:-1])
    _test_bestehen(seite, a2[-1])
    p = seite.js(PFEIL)
    assert p["text"] == seite.js("() => t('test.weiter_stufe', {stufe: 'B1'})"), p
    assert p["vorPfeil"] == 0xA0, p
    assert abs(p["pfeil"] - p["davor"]) < 1, (sprache, p)
    assert seite.js("() => document.documentElement.scrollWidth") <= 360
    assert seite.fehler == []
