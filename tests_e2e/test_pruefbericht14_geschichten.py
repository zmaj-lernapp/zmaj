# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026) im Browser: Geschichten.

B10: Beim Antippen zeigte das Woerterbuch der Lesetexte teils die falsche
Bedeutung: "Direktor je pita" hiess "ist", "Babo, kad idemo opet?" "als /
wenn", "važna utakmica" "wichtig (der wichtige)". Getippt wird hier wie mit
dem Finger, gelesen wird, was in der Blase steht. Die Regeln dahinter prueft
tests/test_pruefbericht14_geschichten.py.
"""
import pytest

# Ein Wort in einer Geschichte antippen: das erste "wort", dessen Vorgaenger
# "davor" ist (beides ohne Gross- und Kleinschreibung). Zurueck kommt die
# Bedeutung in der Blase, ohne das fett gesetzte Wort davor.
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

# (Geschichte, Wort davor, Wort) -> Bedeutung auf Deutsch und Englisch
FAELLE = {
    ("intervju", "direktor", "je"): ("ist / sie (Akk.)", "is / her (acc.)"),
    ("b1_ljeto", "kad", "je"): ("ist / sie (Akk.)", "is / her (acc.)"),
    ("b1_utakmica", "babo", "kad"): ("als / wenn / wann", "when"),
    ("b1_posao", "ako", "ti"): ("du / dir", "you / to you"),
    ("b1_voz", "ako", "vam"): ("Ihnen / euch", "to you (formal or plural)"),
    ("b1_utakmica", "je", "važna"): ("wichtig (w)", "important (f)"),
    ("b1_vrijeme", "nije", "zadovoljan"): ("zufrieden (m)", "content (m)"),
    ("b1_doktor", "red", "doktorica"): ("Ärztin", "doctor (f)"),
    ("b1_kahva", "ima", "svoja"): ("eigene (Mehrz.)", "own (pl.)"),
    # je als Hilfsverb in einer Geschichte ohne eigenen Eintrag: bleibt "ist"
    ("b1_dijaspora", "tarik", "je"): ("ist", "is"),
}


@pytest.mark.parametrize("sprache,spalte", [("de", 0), ("en", 1)])
def test_b10_bedeutung_beim_antippen(seite, heute_stand, sprache, spalte):
    seite.starten(sprache=sprache, stand=heute_stand())
    falsch = []
    for (gid, davor, wort), bedeutung in FAELLE.items():
        r = seite.js(TIPPEN, [gid, davor, wort])
        assert r is not None, (gid, davor, wort)
        if r["hidden"] or r["wort"].lower() != wort or r["bedeutung"] != bedeutung[spalte]:
            falsch.append((gid, wort, r, bedeutung[spalte]))
    assert falsch == []
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# B12: "Passt zu Level" zeigt bei B1-Geschichten auf ein Level bis B1
# ---------------------------------------------------------------------------
# Was in der Liste unter dem Titel und oben in der Geschichte steht
PASST_ZU = r"""(gid) => {
  showStoryPath();
  const i = STORIES.findIndex(s => s.id === gid);
  const knoten = [...document.querySelectorAll('#storyList .node')][i];
  const liste = knoten ? knoten.querySelector('.tipp').textContent : null;
  openStory(i); stilleBitte();
  const kicker = document.querySelector('#rBody .kicker').textContent;
  return {liste, kicker};
}"""

B12 = {
    "b1_stan": "Wohnung & Hauskauf",
    "b1_voz": "Reisen und Urlaub",
    "b1_dijaspora": "Reisen und Urlaub",
    "b1_jahorina": "Sport und Spiel",
    "b1_struja": "Miteinander umgehen",
    "b1_kahva": "Miteinander umgehen",
    "b1_ljeto": "Familie",
}


def test_b12_passt_zu_level_bis_b1(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js("() => { homeMode = 'stories'; showHome(); }")
    falsch = []
    for gid, label in B12.items():
        r = seite.js(PASST_ZU, gid)
        if r["liste"] != "Passt zu Level: " + label or "„" + label + "“" not in r["kicker"]:
            falsch.append((gid, label, r))
    assert falsch == []
    assert seite.fehler == []
