# -*- coding: utf-8 -*-
"""B1-Lesetexte im Browser: Ajdins Antworten auf die A/B-Liste (15.11.2026).

Die Geschichte zeigt die neue Fassung, die Übersetzung darunter passt dazu,
und jedes neue Wort hat beim Antippen seine Bedeutung, auf Deutsch und auf
Englisch. Die Regeln dahinter prüft tests/test_lesetexte_ab.py.
"""
import pytest

# Ein Wort in einer Geschichte antippen wie mit dem Finger: das erste "wort",
# dessen Vorgänger "davor" ist. Zurück kommt die Bedeutung in der Blase.
TIPPEN = r"""([gid, davor, wort]) => {
  const i = STORIES.findIndex(s => s.id === gid);
  openStory(i); stilleBitte();
  const ws = [...document.querySelectorAll('#rBody .txt .w')];
  const k = ws.findIndex((w, n) => n > 0 && w.textContent.toLowerCase() === wort
                                  && ws[n - 1].textContent.toLowerCase() === davor);
  if(k < 0) return null;
  ws[k].click();
  const b = document.getElementById('rBubble');
  const fett = b.querySelector('b');
  return {hidden: b.hidden, wort: fett ? fett.textContent : '',
          bedeutung: b.textContent.slice(fett ? fett.textContent.length : 0).trim()};
}"""

# Was die Geschichte zeigt: Text und Übersetzung, wie sie im Bildschirm stehen
ZEIGEN = r"""(gid) => {
  const i = STORIES.findIndex(s => s.id === gid);
  openStory(i); stilleBitte();
  return {text: document.querySelector('#rBody .txt').textContent,
          trans: document.getElementById('rTransText').textContent};
}"""

# (Geschichte, Wort davor, Wort) -> Bedeutung auf Deutsch und Englisch
FAELLE = {
    ("b1_dijaspora", "deset", "ćevapa"): ("Ćevapi (Gen.)", "ćevapi (gen.)"),
}

# Geschichte -> (bosnisch jetzt, deutsch jetzt, englisch jetzt)
ZU_SEHEN = {
    "b1_dijaspora": ("Tarik je naručio deset ćevapa s lukom i jogurt.",
                     "Tarik bestellte zehn Ćevapi mit Zwiebeln und einen Joghurt.",
                     "Tarik ordered ten ćevapi with onions and a yogurt."),
}


@pytest.mark.parametrize("sprache,spalte", [("de", 0), ("en", 1)])
def test_neue_woerter_beim_antippen(seite, heute_stand, sprache, spalte):
    seite.starten(sprache=sprache, stand=heute_stand())
    falsch = []
    for (gid, davor, wort), bedeutung in FAELLE.items():
        r = seite.js(TIPPEN, [gid, davor, wort])
        assert r is not None, (gid, davor, wort)
        if r["hidden"] or r["wort"].lower() != wort or r["bedeutung"] != bedeutung[spalte]:
            falsch.append((gid, wort, r, bedeutung[spalte]))
    assert falsch == []
    assert seite.fehler == []


@pytest.mark.parametrize("sprache,spalte", [("de", 1), ("en", 2)])
def test_neue_fassung_und_uebersetzung(seite, heute_stand, sprache, spalte):
    seite.starten(sprache=sprache, stand=heute_stand())
    falsch = []
    for gid, saetze in ZU_SEHEN.items():
        r = seite.js(ZEIGEN, gid)
        if saetze[0] not in r["text"] or saetze[spalte] not in r["trans"]:
            falsch.append((gid, saetze[0], saetze[spalte]))
    assert falsch == []
    assert seite.fehler == []
