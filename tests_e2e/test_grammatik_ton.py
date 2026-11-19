# -*- coding: utf-8 -*-
"""Grammatik-Antworten mit Ton (16.11.2026, Offen-Liste 6b) - im echten Browser.

Nach einer Grammatik-Uebung spricht die App die richtige Antwort, wenn sie bosnisch ist
und audioDatei() eine Aufnahme findet. 93 Antworten hatten keine und blieben auf dem
Handy still; Emir hat sie gesprochen (ton_nur_emir.json, w8956 bis w9048). Die Web-Demo
hat die Aufnahmen von Emir nicht, sie liegen nur in der Huelle. Die Tests tragen die
Eintraege aus ton_nur_emir.json deshalb selbst in AUDIO ein, wie app_bauen.emir_drueber()
es fuer die App tut, und schreiben mit, welche Datei abgespielt wuerde (wie
tests_e2e/test_zahlen.py). Daten und Nummern prueft tests/test_grammatik_ton.py.
Dahinter stehen seit dem 16.11.2026 die Woerter der B1-Lesetexte (w9049 bis w9871,
tests_e2e/test_geschichtenwoerter_ton.py).
"""
import io
import json
import os

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERSTE, LETZTE = 8956, 9048


def _emir():
    with io.open(os.path.join(WURZEL, "ton_nur_emir.json"), encoding="utf-8") as f:
        return {e["key"]: e["datei"] for e in json.load(f)["toene"]}


# Wie in der App aus dem Store: die Emir-Aufnahmen stehen in AUDIO; abgespielt wird
# nichts, nur mitgeschrieben - ueber WebAudio (pufferSpielen) oder den spieler (spieleDatei).
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

# Jede Uebung: ist die Antwort bosnisch, und welche Datei faende audioDatei()?
ALLE = """() => {
  const raus = [];
  Object.keys(GRAMMAR).forEach(id => (GRAMMAR[id].uebungen || []).forEach(u =>
    raus.push({id, richtig: u.richtig, bs: gramAntwortBosnisch(u.richtig), datei: audioDatei(u.richtig)})));
  return raus;
}"""

# Eine Grammatik-Uebung in eine frische Lektion legen und richtig beantworten:
# welche Datei kommt danach?
ANTWORTEN = """async ([lektion, richtig]) => {
  const g = GRAMMAR[lektion].uebungen.find(u => u.richtig === richtig);
  if(!g) throw new Error('keine Uebung ' + richtig);
  openLevel(0); startLesson();
  Lx.queue = [{typ: 'gram', g}]; Lx.i = 0; Lx.total = 1; Lx.results = []; Lx.right = 0;
  showLessonTask();
  window.__gespielt = [];
  const body = document.getElementById('lBody');
  const knopf = [...body.querySelectorAll('#xOpts .opt')].find(b => b.textContent === richtig);
  if(!knopf) throw new Error('kein Knopf ' + richtig);
  knopf.click();
  const ende = Date.now() + 3000;
  while(!window.__gespielt.length && Date.now() < ende) await new Promise(r => setTimeout(r, 15));
  return {ok: Lx.results[0], datei: window.__gespielt[0] || null, lang: knopf.lang};
}"""


def test_jede_bosnische_antwort_findet_ihre_aufnahme(seite, heute_stand):
    """In der Web-Demo bleiben die 93 still (index.json unveraendert), mit den Emir-
    Eintraegen wie in der App findet jede bosnische Antwort eine Datei. Die drei
    deutschen Antworten zum Geschlecht spricht die App nie."""
    emir = _emir()
    seite.starten(stand=heute_stand())
    vorher = seite.js(ALLE)
    bosnisch = [u for u in vorher if u["bs"]]
    assert len(vorher) == 175 and len(bosnisch) == 172, (len(vorher), len(bosnisch))
    assert sorted(u["richtig"] for u in vorher if not u["bs"]) == ["männlich (on)", "sächlich (ono)", "weiblich (ona)"]
    neu = {d for d in emir.values() if ERSTE <= int(d[1:5]) <= LETZTE}
    assert not [u for u in vorher if u["datei"] in neu]                 # die Demo kennt sie nicht
    assert len([u for u in bosnisch if not u["datei"]]) >= 94
    seite.js(VORBEREITEN, [[k, d] for k, d in emir.items()])
    nachher = seite.js(ALLE)
    assert [u["richtig"] for u in nachher if u["bs"] and not u["datei"]] == []
    assert len({u["datei"] for u in nachher if u["datei"] in neu}) == 93
    assert seite.fehler == []


def test_nach_der_antwort_spricht_emir(seite, heute_stand):
    """Wie beim Handytest aus EINBAU.md: „___ ideš?“ -> Kuda, die Konjugation „Ja sam
    umoran.“, der Instrumental „bratom“, dazu Ko (Fassung C2) und plačem (K2)."""
    emir = _emir()
    seite.starten(stand=heute_stand())
    seite.js(VORBEREITEN, [[k, d] for k, d in emir.items()])
    lektionen = seite.js("""(texte) => texte.map(t => Object.keys(GRAMMAR).find(id =>
        (GRAMMAR[id].uebungen || []).some(u => u.richtig === t)) || null)""",
                         ["Kuda", "Ja sam umoran.", "bratom", "Ko", "plačem"])
    assert None not in lektionen, lektionen
    for lektion, (richtig, key) in zip(lektionen, [("Kuda", "kuda"), ("Ja sam umoran.", "ja sam umoran."),
                                                    ("bratom", "bratom"), ("Ko", "ko"), ("plačem", "plačem")]):
        r = seite.js(ANTWORTEN, [lektion, richtig])
        assert r == {"ok": True, "datei": emir[key], "lang": "bs"}, (richtig, r)
        assert ERSTE <= int(emir[key][1:5]) <= LETZTE, (richtig, emir[key])
    assert seite.fehler == []
