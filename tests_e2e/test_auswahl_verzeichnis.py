# -*- coding: utf-8 -*-
"""Verzeichnis fuer die Auswahl- und Tippaufgaben (20.11.2026, Optimierung Punkt 2).

Bis dahin liefen geschwister(), annehmbar() und partnerVon() bei jeder Aufgabe ueber
alle 7.997 Eintraege (15 ms je Aufgabe am Laptop, 80-95 ms bei 4-facher Drossel,
Release/Optimierung_2026-11-20/geprueft_laufzeit.md, Befund 2). Seitdem schlagen sie
in wortIndex() nach (web/js/aufgaben.js).

- Gleichheit: Fuer JEDEN Eintrag des Vorrats, in allen acht Sprachen, mit und ohne
  Zahnarzt-Teil, liefern die neuen Funktionen genau dasselbe wie die alten Schleifen
  (unten in ALT abgeschrieben), auch in derselben Reihenfolge. Die Sprachen werden
  in derselben Seite nacheinander eingestellt (setzeSprache): ein Verzeichnis aus
  der vorigen Sprache fiele dabei auf.
- Das Verzeichnis wird nur neu gebaut, wenn sich der Vorrat aendert.
- Es ist schnell genug, dass es nicht mehr nach jedem "Weiter" ins Gewicht faellt.
"""
import pytest

SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]

# Die alten Funktionen, Wort fuer Wort wie bis zum 20.11.2026 in aufgaben.js, stehen in
# WOERTLICH. Das braucht je Eintrag etwa 4,5 ms, fuer 8.000 Eintraege in 16 Durchlaeufen
# also gut zehn Minuten. Darum ALT: dieselbe Bedingung je Paar, Teil fuer Teil, nur
# sind _bedeutung(x.de), _formen(x.bs) und _auchAlle(x).flatMap(_formen) (reine
# Funktionen des Eintrags) einmal je Eintrag vorausgerechnet, und _NIE ist nach dem
# ersten Wort zerlegt (dieselbe Menge, ohne neue Zeichenkette je Paar). Dass ALT dasselbe liefert wie WOERTLICH, prueft der Vergleich
# an jedem 40. Eintrag mit.
WOERTLICH = r"""
() => ({
  vorrat: () => CATEGORIES.concat(imZa() ? zaLevel() : []).flatMap(c=>c.words),
  partnerVon(w){
    return CATEGORIES.flatMap(c=>c.words).filter(x => istPartner(w, x));
  },
  geschwister(w){
    const b = _bedeutung(w.de);
    const meineAuch = new Set(_auchAlle(w).flatMap(_formen));
    const meineFormen = _formen(w.bs);
    return this.vorrat().filter(x => x.bs !== w.bs &&
      ((b && _bedeutung(x.de) === b) ||
       istPartner(w, x) ||
       nieNebeneinander(w.bs, x.bs) ||
       _formen(x.bs).some(f => meineAuch.has(f)) ||
       _auchAlle(x).flatMap(_formen).some(f => meineFormen.includes(f))));
  },
  annehmbar(w){
    const b = _bedeutung(w.de);
    const gleich = b ? this.vorrat().filter(x => x.bs !== w.bs && _bedeutung(x.de) === b && !istPartner(w, x)).map(x=>x.bs) : [];
    return [w.bs, ...gleich, ...(w.auch || []), ...(w.auch_var || [])];
  },
})
"""

ALT = r"""
() => {
  const vorrat = CATEGORIES.concat(imZa() ? zaLevel() : []).flatMap(c=>c.words);
  const pfad = CATEGORIES.flatMap(c=>c.words);
  const bed = vorrat.map(x => _bedeutung(x.de)), form = vorrat.map(x => _formen(x.bs)),
        auchForm = vorrat.map(x => _auchAlle(x).flatMap(_formen));
  // _NIE.has(a + '\u0000' + b), zerlegt: zu jedem a die Menge der b.
  const nieZu = new Map();
  _NIE.forEach(k => { const [a, b] = k.split('\u0000'); if(!nieZu.has(a)) nieZu.set(a, new Set()); nieZu.get(a).add(b); });
  const irgendein = (liste, ok) => { for(const f of liste) if(ok(f)) return true; return false; };
  return {
    vorrat: () => vorrat,
    partnerVon(w){
      return pfad.filter(x => istPartner(w, x));
    },
    partnerAntworten(w){
      return this.partnerVon(w).flatMap(x => [x.bs, ...(x.auch || [])]).join(' / ');
    },
    geschwister(w){
      const b = _bedeutung(w.de);
      const meineAuch = new Set(_auchAlle(w).flatMap(_formen));
      const meineFormen = _formen(w.bs);
      const nie = nieZu.get(w.bs) || new Set();
      const inAuch = f => meineAuch.has(f), inFormen = f => meineFormen.includes(f);
      const out = [];
      for(let i = 0; i < vorrat.length; i++){
        const x = vorrat[i];
        if(x.bs !== w.bs &&
           ((b && bed[i] === b) ||
            istPartner(w, x) ||
            nie.has(x.bs) ||
            (meineAuch.size && irgendein(form[i], inAuch)) ||
            (auchForm[i].length && irgendein(auchForm[i], inFormen)))) out.push(x);
      }
      return out;
    },
    annehmbar(w){
      const b = _bedeutung(w.de);
      const gleich = b ? vorrat.filter((x, i) => x.bs !== w.bs && bed[i] === b && !istPartner(w, x)).map(x=>x.bs) : [];
      return [w.bs, ...gleich, ...(w.auch || []), ...(w.auch_var || [])];
    },
  };
}
"""

VERGLEICH = r"""
(za) => {
  const vorher = catIdx;
  if(za) catIdx = CATEGORIES.length;
  try{
    const alt = (""" + ALT + r""")(), woertlich = (""" + WOERTLICH + r""")();
    if(imZa() !== za) throw new Error('imZa() nicht wie verlangt');
    const vorrat = alt.vorrat();
    const vorratAlt = woertlich.vorrat();
    if(vorrat.length !== vorratAlt.length || !vorrat.every((x, i) => x === vorratAlt[i]))
      throw new Error('Vorrat anders als wortVorrat()');
    const gleich = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
    const r = {sprache: SPRACHE, za, eintraege: vorrat.length, abweichungen: [],
               mitGeschwistern: 0, mitGleichen: 0, mitPartner: 0, woertlich: 0};
    vorrat.forEach((w, nr) => {
      const g = geschwister(w), ga = alt.geschwister(w);
      if(!gleich(g, ga)) r.abweichungen.push(['geschwister', w.id, g.map(x => x.bs), ga.map(x => x.bs)]);
      const a = annehmbar(w), aa = alt.annehmbar(w);
      if(!gleich(a, aa)) r.abweichungen.push(['annehmbar', w.id, a, aa]);
      const p = partnerVon(w), pa = alt.partnerVon(w);
      if(!gleich(p, pa)) r.abweichungen.push(['partnerVon', w.id, p.map(x => x.bs), pa.map(x => x.bs)]);
      if(partnerAntworten(w) !== alt.partnerAntworten(w)) r.abweichungen.push(['partnerAntworten', w.id]);
      if(ga.length) r.mitGeschwistern++;
      if(aa.length > 1 + (w.auch || []).length + (w.auch_var || []).length) r.mitGleichen++;
      if(pa.length) r.mitPartner++;
      if(nr % 40 === 0){
        r.woertlich++;
        if(!gleich(ga, woertlich.geschwister(w)) || !gleich(aa, woertlich.annehmbar(w)) || !gleich(pa, woertlich.partnerVon(w)))
          r.abweichungen.push(['ALT anders als WOERTLICH', w.id]);
      }
    });
    r.anzahl = r.abweichungen.length; r.abweichungen = r.abweichungen.slice(0, 10);
    return r;
  } finally { catIdx = vorher; }
}
"""


def test_gleich_wie_vorher_alle_eintraege_alle_sprachen(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="de")
    assert seite.js("() => zaLevel().length") > 0, "die Demo braucht den Zahnarzt-Teil"
    gesehen = []
    for sprache in SPRACHEN:
        seite.js("async c => { await setzeSprache(c); }", sprache)
        for za in (False, True):
            e = seite.js(VERGLEICH, za)
            assert e["sprache"] == sprache, e
            assert e["anzahl"] == 0, e
            # Sonst bewiese der Vergleich nichts: alle drei Wege kommen wirklich vor.
            assert e["eintraege"] > 7900 and e["mitGeschwistern"] > 500, e
            assert e["mitGleichen"] > 0 and e["mitPartner"] > 50 and e["woertlich"] >= 199, e
            gesehen.append((sprache, za, e["eintraege"]))
    # Mit dem Zahnarzt-Teil sind es mehr Eintraege, in jeder Sprache.
    for sprache in SPRACHEN:
        ohne, mit = [n for s, z, n in gesehen if s == sprache]
        assert mit > ohne, (sprache, ohne, mit)
    assert seite.fehler == [] and seite.fremd == []


NEU_GEBAUT = r"""
async () => {
  const r = {};
  const a = wortIndex();
  r.gleichBleibend = wortIndex() === a && (geschwister(CATEGORIES[0].words[0]), wortIndex() === a);
  r.vorratGleich = a.vorrat.length === wortVorrat().length && a.vorrat.every((x, i) => x === wortVorrat()[i]);
  // Ein Wort mehr in einem Level (wie test_varianten.py), dann wieder weg.
  const k = CATEGORIES[0];
  const neu = {id: 'probe:probe', bs: 'probe', de: 'Probe'};
  k.words.push(neu);
  const b = wortIndex();
  r.mitWort = b !== a && b.vorrat.includes(neu);
  k.words.pop();
  const c = wortIndex();
  r.ohneWort = c !== b && !c.vorrat.includes(neu);
  // Zahnarzt-Teil offen und wieder zu.
  const vorher = catIdx;
  catIdx = CATEGORIES.length;
  const d = wortIndex();
  r.za = d !== c && d.vorrat.length === c.vorrat.length + zaLevel().reduce((s, x) => s + x.words.length, 0);
  catIdx = vorher;
  r.zaZu = wortIndex().vorrat.length === c.vorrat.length;
  // Sprachwechsel: neue CATEGORIES, neues Verzeichnis.
  const e = wortIndex();
  await setzeSprache('da');
  const f = wortIndex();
  r.sprache = f !== e && f.kat === CATEGORIES && f.vorrat[0] === CATEGORIES[0].words[0];
  return r;
}
"""


def test_verzeichnis_nur_neu_wenn_sich_der_vorrat_aendert(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="de")
    assert seite.js(NEU_GEBAUT) == {"gleichBleibend": True, "vorratGleich": True, "mitWort": True,
                                    "ohneWort": True, "za": True, "zaZu": True, "sprache": True}
    assert seite.fehler == []


# Vorher kosteten 300 Runden je etwa 15 + 2,5 + 1 ms am Laptop, zusammen gut 5 s.
SCHNELL = r"""
() => {
  const vorrat = wortVorrat();
  geschwister(vorrat[0]);      // das Verzeichnis einmal bauen lassen
  const t0 = performance.now();
  for(let i = 0; i < 300; i++){
    const w = vorrat[(i * 26) % vorrat.length];
    geschwister(w); annehmbar(w); partnerVon(w);
  }
  return performance.now() - t0;
}
"""


@pytest.mark.parametrize("sprache", ["de", "da"])
def test_auswahl_schlaegt_nach_statt_alles_abzulaufen(seite, heute_stand, sprache):
    seite.starten(stand=heute_stand(), sprache=sprache)
    ms = seite.js(SCHNELL)
    assert ms < 500, ms
    assert seite.fehler == []
