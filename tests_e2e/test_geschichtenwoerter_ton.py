# -*- coding: utf-8 -*-
"""Woerter der B1-Lesetexte mit Ton (16.11.2026, Offen-Liste 6a) - im echten Browser.

Tippt man in einer Geschichte ein Wort an, spricht die App es, wenn audioDatei() eine
Aufnahme findet. 823 Woerter, die nur in den 20 B1-Lesetexten stehen, hatten keine und
blieben auf dem Handy still; Emir hat sie gesprochen (ton_nur_emir.json, w9049 bis w9871).
Die Web-Demo hat die Aufnahmen von Emir nicht, sie liegen nur in der Huelle. Die Tests
tragen die Eintraege aus ton_nur_emir.json deshalb selbst in AUDIO ein, wie
app_bauen.emir_drueber() es fuer die App tut, und schreiben mit, welche Datei abgespielt
wuerde (wie tests_e2e/test_grammatik_ton.py). Daten und Nummern prueft
tests/test_geschichtenwoerter_ton.py.
"""
import io
import json
import os
import re

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERSTE, LETZTE = 9049, 9871
# Wie beim Handytest aus Stimme_Emir_neu\geschichten_838_2026-11-16\LIESMICH.md, Schritt 9
ANTIPPEN = [("b1_dijaspora", "Tarik", "tarik"), ("b1_dijaspora", "Miljacke", "miljacke"),
            ("b1_vrijeme", "prognozu", "prognozu"), ("b1_kahva", "džezvu", "džezvu")]


def _emir():
    with io.open(os.path.join(WURZEL, "ton_nur_emir.json"), encoding="utf-8") as f:
        return {e["key"]: e["datei"] for e in json.load(f)["toene"]}


def _neu(emir):
    return {d for d in emir.values() if ERSTE <= int(d[1:5]) <= LETZTE}


def _genau(text):
    return re.compile("^" + re.escape(text) + "$")


# Wie in der App aus dem Store: die Emir-Aufnahmen stehen in AUDIO; abgespielt wird
# nichts, nur mitgeschrieben - ueber den spieler (spieleDatei, so spricht ein angetipptes
# Wort) oder WebAudio (pufferSpielen).
VORBEREITEN = """(emir) => {
  emir.forEach(([k, d]) => AUDIO.set(k, d));
  window.__gespielt = [];
  spieleDatei = (datei, fertig) => { window.__gespielt.push(datei); if(fertig) setTimeout(fertig, 0); return Promise.resolve(); };
  pufferSpielen = (text) => {
    const d = audioDatei(text), p = d && puffer.get(d);
    if(!p || !p.buf) return false;
    window.__gespielt.push(d); return true;
  };
}"""

# Jedes Wort jeder B1-Geschichte, so wie es im Text steht: welche Datei faende audioDatei()?
ALLE = """() => {
  const raus = [];
  STORIES.forEach((s, i) => {
    if(!s.id.startsWith('b1_')) return;   // die 20 B1-Lesetexte; seit 17.11.2026 ist auch intervju B1
    openStory(i); stilleBitte();
    document.querySelectorAll('#rBody .txt .w').forEach(w =>
      raus.push({id: s.id, wort: w.textContent, datei: audioDatei(w.textContent)}));
  });
  return raus;
}"""

OEFFNEN = """(gid) => { const i = STORIES.findIndex(s => s.id === gid);
  openStory(i); stilleBitte(); window.__gespielt = []; return i; }"""


def test_jedes_wort_der_b1_texte_findet_seine_aufnahme(seite, heute_stand):
    """In der Web-Demo bleiben die neuen Woerter still (index.json unveraendert), mit den
    Emir-Eintraegen wie in der App findet jedes Wort der 20 B1-Texte eine Datei, und
    jede der 823 neuen Nummern gehoert zu einem Wort im Text."""
    emir = _emir()
    neu = _neu(emir)
    assert len(neu) == LETZTE - ERSTE + 1
    seite.starten(stand=heute_stand())
    vorher = seite.js(ALLE)
    assert len({u["id"] for u in vorher}) == 20
    assert not [u for u in vorher if u["datei"] in neu]                 # die Demo kennt sie nicht
    assert len({u["wort"].lower() for u in vorher if not u["datei"]}) >= 823
    seite.js(VORBEREITEN, [[k, d] for k, d in emir.items()])
    nachher = seite.js(ALLE)
    assert [u["id"] + ":" + u["wort"] for u in nachher if not u["datei"]] == []
    assert {u["datei"] for u in nachher if u["datei"] in neu} == neu
    assert seite.fehler == []


def test_antippen_spricht_emir(seite, heute_stand):
    """Tarik und Miljacke in b1_dijaspora, prognozu in b1_vrijeme, džezvu in b1_kahva:
    antippen, die Blase zeigt das Wort mit Lautsprecher, und es spielt die neue Nummer."""
    emir = _emir()
    seite.starten(stand=heute_stand())
    assert seite.js("(ws) => ws.map(w => audioDatei(w))", [w for _, w, _ in ANTIPPEN]) == [None] * len(ANTIPPEN)
    seite.js(VORBEREITEN, [[k, d] for k, d in emir.items()])
    for gid, wort, key in ANTIPPEN:
        assert ERSTE <= int(emir[key][1:5]) <= LETZTE, (wort, emir[key])
        assert seite.js(OEFFNEN, gid) >= 0, gid
        seite.page.locator("#rBody .txt .w", has_text=_genau(wort)).first.click()
        seite.page.wait_for_function("() => window.__gespielt.length > 0", timeout=3000)
        r = seite.js("""() => { const b = document.getElementById('rBubble');
          return {gespielt: window.__gespielt.slice(), hidden: b.hidden,
                  wort: (b.querySelector('b') || {}).textContent || '', knopf: !!b.querySelector('.wortton')}; }""")
        assert r == {"gespielt": [emir[key]], "hidden": False, "wort": wort, "knopf": True}, (gid, wort, r)
        # Der Lautsprecher in der Blase spricht dasselbe noch einmal
        seite.page.locator("#rBubble .wortton").click()
        seite.page.wait_for_function("() => window.__gespielt.length > 1", timeout=3000)
        assert seite.js("() => window.__gespielt.slice()") == [emir[key], emir[key]], (gid, wort)
    assert seite.fehler == []
