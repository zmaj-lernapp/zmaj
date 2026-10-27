# -*- coding: utf-8 -*-
"""Sonnenbrille ohne Blinzeln (26.10.2026).

Ajdin: "nur bei der sonnenbrille weil man die augen nicht sieht sieht es so
aus das sein gesicht bugged aber er macht einfach nur die augen zu und wieder
auf" - "ja mach das so". Mit der ganz deckenden Sonnenbrille bleibt das
offene Kopf- und Hornbild stehen, ohne sie blinzelt der Drache wie bisher.
"""

DATEN = """async (ids) => {
  const d = await zmajDaten({ids: ids, farbe: ''});
  const op = d.op;
  const sicht = l => { const w = []; const o = l.ks.o;
    for(let t = 0; t < op; t++){ let v = o.a ? 0 : o.k; if(o.a) for(const f of o.k){ if(f.t <= t) v = f.s[0]; else break; } w.push(v); }
    return w; };
  const namen = d.layers.map(l => l.nm);
  const koepfe = d.layers.filter(l => /^bild_kopf_/.test(l.nm)).map(sicht);
  const hoerner = d.layers.filter(l => /^bild_hoerner_/.test(l.nm)).map(sicht);
  const jeBild = ws => Array.from({length: op}, (_, t) => ws.filter(w => w[t] > 0).length);
  const neutral = d.layers.find(l => l.nm === 'bild_kopf_neutral');
  return {blinzeln: namen.includes('bild_kopf_blinzeln'), hornBlinzeln: namen.includes('bild_hoerner_blinzeln'),
          koepfe: [...new Set(jeBild(koepfe))], hoerner: [...new Set(jeBild(hoerner))],
          neutralBei31: sicht(neutral)[31], neutralBei65: sicht(neutral)[65]};
}"""


def test_mit_sonnenbrille_blinzelt_er_nicht(seite):
    seite.starten()
    r = seite.js(DATEN, ["sonnenbrille"])
    assert not r["blinzeln"] and not r["hornBlinzeln"], r
    assert r["koepfe"] == [1] and r["hoerner"] == [1], r      # immer genau ein Kopf
    assert r["neutralBei31"] == 100 and r["neutralBei65"] == 100, r


def test_ohne_sonnenbrille_blinzelt_er_wie_bisher(seite):
    seite.starten()
    for ids in ([], ["brille"], ["krone"]):
        r = seite.js(DATEN, ids)
        assert r["blinzeln"], (ids, r)
        # Die Krone nimmt die Hornbilder ganz heraus (zmaj_leert), also nur ohne sie.
        assert r["hornBlinzeln"] or ids == ["krone"], (ids, r)
        assert r["koepfe"] == [1], (ids, r)
        assert r["neutralBei31"] == 0, (ids, r)
