# -*- coding: utf-8 -*-
"""Schnellerer Lektionsstart in spaeten Leveln (20.11.2026, Optimierung Punkt 9).

Im Level 277 mit vollem Stand dauerte startLesson() 520-720 ms bei 4-facher Drossel,
fast alles in zwei Stellen (Release/Optimierung_2026-11-20/geprueft_laufzeit.md,
Befund 3): lueckeGesehen() lief jede Antwort gegen alle gesehenen Formen, und
kachelnFuerLektion() baute "vorher" aus allen Woertern aller frueheren Level neu.
Seitdem (web/js/lektion.js): Formen je Wort gemerkt (lueckeFormenVon), Formen als
Menge und nur die Wortfolgen des Satzes nachgesehen (lueckeFormMenge), und zu jedem
Wort-Teil der erste Level (kachelErsterLevel), einmal je Inhalt.

- Gleichheit: Fuer jeden der 298 Level (297 bis K7, 27.11.2026), mit leerem, mittlerem (1.000 Woerter, 40
  Level) und vollem Stand, entscheiden die neuen Funktionen bei JEDEM Kandidaten-Satz
  dasselbe wie die alten (unten in ALT Wort fuer Wort abgeschrieben). Dazu wird jede
  Lektion zweimal gebaut, mit demselben Zufall, einmal mit den alten Funktionen:
  dieselben Woerter, Luecken, Kacheln und Grammatikaufgaben in derselben Reihenfolge.
- Die Verzeichnisse werden neu gebaut, wenn sich der Inhalt aendert.
- Der Start ist im spaeten Level wirklich schneller.
"""
import json

import pytest

# Die alten Funktionen, Wort fuer Wort wie bis zum 20.11.2026 in lektion.js.
ALT = r"""
(() => {
  function gesehenFormen(ids){
    const formen = [];
    CATEGORIES.forEach(c => c.words.forEach(w => {
      if(!ids.has(w.id)) return;
      [w.bs, ...(w.auch || [])].forEach(x => String(x).split(' / ').forEach(f => {
        const teile = lueckeTeile(f);
        if(teile.trim()) formen.push(teile);
      }));
    }));
    return {formen, zahlen: null};
  }
  function lueckeGesehen(s, g){
    return String(s.answer).split(' / ').some(a => {
      const z = zahlWert(a);
      if(z !== null){
        if(!g.zahlen) g.zahlen = new Set(g.formen.map(zahlDerForm));
        if(g.zahlen.has(z)) return true;
      }
      const kern = lueckeTeile(a), satz = lueckeTeile(s.text.replace('___', a));
      return !!kern.trim() && g.formen.some(f => f.includes(kern) && satz.includes(f));
    });
  }
  function lueckenFuerLektion(ids){
    if(imZa()) return [];
    const g = gesehenFormen(ids), schon = new Set(), out = [];
    const nimm = liste => shuffle(liste.filter(s => lueckeGesehen(s, g))).forEach(s => {
      const k = s.text + '|' + s.answer;
      if(out.length < LEKTION_LUECKEN && !schon.has(k)){ schon.add(k); out.push(s); }
    });
    nimm(curSentences());
    if(out.length < LEKTION_LUECKEN){
      const frueher = new Set(CATEGORIES.slice(0, catIdx).filter(x => passed.has(x.id)).map(x => x.id));
      nimm(SENTENCES.filter(s => frueher.has(s.kat)));
    }
    return out;
  }
  function kachelnFuerLektion(ids, belegt){
    if(imZa()) return [];
    const c = cur();
    const teileVon = w => kachelFormen(w).flatMap(f => lueckeTeile(f).trim().split(' ')).filter(Boolean);
    const hier = new Set(c.words.flatMap(teileVon));
    const vorher = new Set(CATEGORIES.slice(0, catIdx).flatMap(k => k.words.flatMap(teileVon)));
    const gesehen = new Set(gesehenFormen(ids).formen.flatMap(f => f.trim().split(' ')));
    const bereit = s => kachelRoh(s.bs).concat(s.grund || []).every(k => lueckeTeile(k).trim().split(' ').filter(Boolean)
      .every(x => !hier.has(x) || gesehen.has(x) || vorher.has(x)));
    const schon = new Set(), out = [];
    const nimm = liste => shuffle(liste.slice()).forEach(s => {
      const k = kachelNorm(s.bs);
      if(belegt && [s.bs, ...(s.auch || [])].some(x => belegt.has(kachelNorm(x)))) return;
      if(out.length < LEKTION_KACHELN && !schon.has(k)){ schon.add(k); out.push(s); }
    });
    nimm(SATZBAU.filter(s => s.kat === c.id && bereit(s)));
    if(out.length < LEKTION_KACHELN){
      const frueher = new Set(CATEGORIES.slice(0, catIdx).filter(x => passed.has(x.id)).map(x => x.id));
      nimm(SATZBAU.filter(s => frueher.has(s.kat)));
    }
    return out;
  }
  return {gesehenFormen, lueckeGesehen, lueckenFuerLektion, kachelnFuerLektion};
})()
"""

# Vergleicht die Level von bis bis (ausschliesslich). Je Level:
# 1. die gesehenen Formen (Reihenfolge und Inhalt),
# 2. jede Luecke, die die Lektion in Betracht zieht (Level und fruehere, bestandene),
# 3. jeden Kachelsatz des Levels einzeln (SATZBAU nur mit ihm: er kommt genau dann,
#    wenn er bereit ist),
# 4. die ganze Lektion aus buildLesson() mit demselben Zufall, einmal mit den alten
#    Funktionen eingesetzt.
VERGLEICH = r"""
([von, bis]) => {
  const ALTF = """ + ALT + r""";
  const zufall = seed => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const echtZufall = Math.random, vorherIdx = catIdx, satzbau = SATZBAU;
  const neuL = window.lueckenFuerLektion, neuK = window.kachelnFuerLektion;
  const r = {level: 0, abweichungen: [], luecken: 0, lueckenJa: 0, kacheln: 0, kachelnJa: 0,
             lektionen: 0, mitLuecke: 0, mitKacheln: 0, eingesetzt: 0, aufgaben: 0};
  const abw = (...x) => r.abweichungen.push(x);
  const gleicheAufgabe = (a, b) => a.typ === b.typ && a.w === b.w && a.s === b.s && a.g === b.g &&
    !!a.neu === !!b.neu && !!a.faellig === !!b.faellig && a.rep === b.rep && a.pool === b.pool;
  try{
    for(let i = von; i < Math.min(bis, CATEGORIES.length); i++){
      catIdx = i; r.level++;
      const c = cur();
      const ids = new Set([...known, ...c.words.filter(w => !known.has(w.id)).slice(0, LEKTION_NEU_MAX).map(w => w.id)]);
      // 1.
      const gN = gesehenFormen(ids), gA = ALTF.gesehenFormen(ids);
      if(gN.formen.length !== gA.formen.length || gN.formen.some((f, k) => f !== gA.formen[k])) abw('gesehenFormen', c.id);
      // 2.
      const frueher = new Set(CATEGORIES.slice(0, catIdx).filter(x => passed.has(x.id)).map(x => x.id));
      curSentences().concat(SENTENCES.filter(s => frueher.has(s.kat))).forEach(s => {
        const n = lueckeGesehen(s, gN), a = ALTF.lueckeGesehen(s, gA);
        r.luecken++; if(a) r.lueckenJa++;
        if(n !== a) abw('luecke', c.id, s.text, s.answer, n, a);
      });
      // 3.
      satzbau.filter(s => s.kat === c.id).forEach(s => {
        SATZBAU = [s];
        const n = kachelnFuerLektion(ids, null).length, a = ALTF.kachelnFuerLektion(ids, null).length;
        SATZBAU = satzbau;
        r.kacheln++; if(a) r.kachelnJa++;
        if(n !== a) abw('kacheln', c.id, s.bs, n, a);
      });
      // 4.
      Math.random = zufall(7919 * (i + 1));
      buildLesson();
      const neu = Lx.queue;
      let altGerufen = 0;
      window.lueckenFuerLektion = ids => { altGerufen++; return ALTF.lueckenFuerLektion(ids); };
      window.kachelnFuerLektion = (ids, belegt) => { altGerufen++; return ALTF.kachelnFuerLektion(ids, belegt); };
      Math.random = zufall(7919 * (i + 1));
      buildLesson();
      window.lueckenFuerLektion = neuL; window.kachelnFuerLektion = neuK;
      Math.random = echtZufall;
      const alt = Lx.queue;
      if(altGerufen === 2) r.eingesetzt++;
      r.lektionen++; r.aufgaben += neu.length;
      if(alt.some(q => q.typ === 'gap')) r.mitLuecke++;
      if(alt.some(q => q.typ === 'kacheln')) r.mitKacheln++;
      if(neu.length !== alt.length || neu.some((q, k) => !gleicheAufgabe(q, alt[k])))
        abw('lektion', c.id, neu.map(q => q.typ + ':' + (q.w ? q.w.id : q.s ? (q.s.bs || q.s.text) : '')).join(','),
            alt.map(q => q.typ + ':' + (q.w ? q.w.id : q.s ? (q.s.bs || q.s.text) : '')).join(','));
    }
  } finally {
    catIdx = vorherIdx; SATZBAU = satzbau; Math.random = echtZufall;
    window.lueckenFuerLektion = neuL; window.kachelnFuerLektion = neuK;
  }
  r.anzahl = r.abweichungen.length; r.abweichungen = r.abweichungen.slice(0, 5);
  return r;
}
"""


def _stand(art, heute_stand, vollversion):
    if art == "leer":
        return heute_stand()
    st = json.loads(json.dumps(vollversion["stand"]))
    st.pop("premium", None)
    if art == "mittel":      # etwa ein fleissiger Nutzer nach sieben Wochen, wie in geprueft_laufzeit.md
        st["gewusst"] = st["gewusst"][:1000]
        st["bestanden"] = st["bestanden"][:40]
    st.update(heute_stand())
    return st


@pytest.mark.parametrize("art", ["leer", "mittel", "voll"])
def test_lektionen_gleich_wie_vorher_in_allen_leveln(seite, heute_stand, vollversion, art):
    seite.starten(stand=_stand(art, heute_stand, vollversion), sprache="de")
    n = seite.js("() => CATEGORIES.length")
    assert n == 298        # 297 bis K7 (27.11.2026)
    gewusst, bestanden = seite.js("() => [known.size, passed.size]")
    assert {"leer": (0, 0), "mittel": (1000, 40), "voll": (8191, 298)}[art] == (gewusst, bestanden)
    summe = {}
    for von in range(0, n, 50):
        e = seite.js(VERGLEICH, [von, von + 50])
        assert e["anzahl"] == 0, e
        for k, v in e.items():
            if isinstance(v, int):
                summe[k] = summe.get(k, 0) + v
    assert summe["level"] == 298 and summe["lektionen"] == 298, summe       # 297 bis K7 (27.11.2026)
    # Die alten Funktionen waren wirklich eingesetzt, und es gab etwas zu vergleichen.
    assert summe["eingesetzt"] == 298, summe
    assert summe["luecken"] >= 300 and summe["kacheln"] >= 357, summe
    assert summe["kachelnJa"] > 0 and summe["mitKacheln"] > 0, summe
    if art != "leer":
        assert summe["lueckenJa"] > 300 and summe["mitLuecke"] > 200, summe
        assert summe["luecken"] > summe["lueckenJa"], summe     # auch Saetze, die nicht kommen duerfen
    assert seite.fehler == [] and seite.fremd == []


NEU_GEBAUT = r"""
async () => {
  const r = {};
  const a = kachelErsterLevel();
  r.gleichBleibend = kachelErsterLevel() === a;
  // Jeder Teil steht beim ersten Level, in dem er vorkommt.
  r.erster = CATEGORIES.every((k, i) => k.words.every(w => kachelTeileVon(w).every(x => a.get(x) <= i)));
  const w0 = CATEGORIES[0].words[0];
  r.formenGemerkt = lueckeFormenVon(w0) === lueckeFormenVon(w0);
  // Ein Wort mehr in einem Level (wie test_varianten.py), dann wieder weg.
  const k = CATEGORIES[3];
  const neu = {id: 'probe:probe', bs: 'probeteil', de: 'Probe'};
  k.words.push(neu);
  const b = kachelErsterLevel();
  r.mitWort = b !== a && b.get('probeteil') === 3;
  k.words.pop();
  const c = kachelErsterLevel();
  r.ohneWort = c !== b && !c.has('probeteil');
  // Sprachwechsel: neue CATEGORIES, neues Verzeichnis, neue Formen.
  await setzeSprache('da');
  const d = kachelErsterLevel();
  r.sprache = d !== c && CATEGORIES[0].words[0] !== w0 && lueckeFormenVon(CATEGORIES[0].words[0]) !== lueckeFormenVon(w0);
  return r;
}
"""


def test_verzeichnisse_neu_wenn_sich_der_inhalt_aendert(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="de")
    assert seite.js(NEU_GEBAUT) == {"gleichBleibend": True, "erster": True, "formenGemerkt": True,
                                    "mitWort": True, "ohneWort": True, "sprache": True}
    # Nach dem Sprachwechsel entscheidet alles wie vorher, hier in jedem zehnten Level.
    for von in range(0, 298, 10):
        e = seite.js(VERGLEICH, [von, von + 1])
        assert e["anzahl"] == 0 and e["level"] == 1 and e["eingesetzt"] == 1, e
    assert seite.fehler == []


# Vorher am Laptop ohne Drossel im Level 277 mit vollem Stand: Luecken und Kacheln
# zusammen 77 ms (bei 4-facher Drossel rund 450 ms), jetzt 13 ms (20.11.2026).
SCHNELL = r"""
() => {
  const vorher = catIdx;
  catIdx = CATEGORIES.length - 20;
  try{
    const ids = new Set(known);
    lueckenFuerLektion(ids); kachelnFuerLektion(ids, new Set());     // Verzeichnisse einmal bauen lassen
    const t = [];
    for(let i = 0; i < 7; i++){
      const t0 = performance.now();
      lueckenFuerLektion(ids); kachelnFuerLektion(ids, new Set());
      t.push(performance.now() - t0);
    }
    t.sort((a, b) => a - b);
    return {catIdx, ms: t[3]};
  } finally { catIdx = vorher; }
}
"""


def test_spaeter_level_startet_schneller(seite, heute_stand, vollversion):
    seite.starten(stand=_stand("voll", heute_stand, vollversion), sprache="de")
    e = seite.js(SCHNELL)
    assert e["catIdx"] == 278      # 20 vor dem Ende, seit K7 (27.11.2026) ein Level mehr
    assert e["ms"] < 40, e
    assert seite.fehler == []
