# -*- coding: utf-8 -*-
"""Die Wortliste auf der Level-Seite, im echten Browser.

Pruefbericht 1.3, G10. Haken und Lautsprecher standen im abgeschnittenen Feld des
bosnischen Worts: bei langen Eintraegen fehlte der Lautsprecher, oft auch der
Haken, und beide Texte endeten nach einer Zeile mit "...". Geprueft wird an
dem Punkt, der zaehlt: Trifft ein Finger an der Stelle von Haken und
Lautsprecher wirklich diese beiden?
"""
import pytest

PRUEFEN = r"""() => {
  document.getElementById('wordBox').open = true;
  const r = {zeilen: 0, ton: 0, ohneTon: [], ohneHaken: [], breit: [], zerrissen: []};
  const breite = document.documentElement.clientWidth;
  document.querySelectorAll('#wordList > div').forEach(z => {
    r.zeilen++;
    z.scrollIntoView({block: 'center'});
    const trifft = el => { if(!el) return true; const b = el.getBoundingClientRect();
      const x = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
      return !!x && (x === el || el.contains(x)); };
    const name = z.querySelector('.bs').textContent;
    const ton = z.querySelector('.wortton'), ok = z.querySelector('.ok');
    if(ton) r.ton++;
    if(!trifft(ton)) r.ohneTon.push(name);
    if(!trifft(ok)) r.ohneHaken.push(name);
    if(z.getBoundingClientRect().right > breite) r.breit.push(name);
    // Ein bosnisches Wort wird nie zerrissen: es liegt ganz auf einer Zeile
    const text = z.querySelector('.bs').firstChild, muster = /\S+/g;
    for(let m; (m = muster.exec(text.data));){
      const stueck = document.createRange();
      stueck.setStart(text, m.index); stueck.setEnd(text, m.index + m[0].length);
      if(new Set([...stueck.getClientRects()].map(k => Math.round(k.top))).size > 1) r.zerrissen.push(m[0]);
    }
  });
  return r; }"""

ABGESCHNITTEN = """() => [...document.querySelectorAll('#wordList .de, #wordList .bs')].filter(x => {
  const s = getComputedStyle(x);
  return s.webkitLineClamp !== '2' || s.whiteSpace === 'nowrap'; }).length"""


@pytest.mark.parametrize("breite,hoehe", [(320, 568), (360, 640), (390, 844), (700, 900)])
def test_haken_und_lautsprecher_stehen_in_jeder_zeile(browser, basis, heute_stand, breite, hoehe):
    from conftest import Seite
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, locale="de-DE", service_workers="block")
    seite = Seite(ctx.new_page(), basis)
    try:
        seite.starten(stand=heute_stand(zahnarzt={"an": True, "z": 1000}))
        seite.js("() => document.getElementById('vorspann').click()")
        seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
        for i in seite.js("() => [CATEGORIES.findIndex(c => c.id === 'familie'), CATEGORIES.length + 1]"):
            seite.js("(i) => { catIdx = i; cur().words.forEach(w => known.add(w.id)); openLevel(i); }", i)
            r = seite.js(PRUEFEN)
            assert r["zeilen"] > 0 and r["ton"] == r["zeilen"], r
            assert r["ohneTon"] == [] and r["ohneHaken"] == [] and r["breit"] == [], (i, r)
            assert r["zerrissen"] == [], (i, r["zerrissen"])
            assert seite.js(ABGESCHNITTEN) == 0
        assert seite.fehler == []
    finally:
        ctx.close()


def test_ungelernte_zeile_zeigt_nur_das_fragezeichen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    z = seite.js("""() => { const i = CATEGORIES.findIndex(c => c.id === 'familie'); openLevel(i);
        const zeile = document.querySelector('#wordList > div');
        return {bs: zeile.querySelector('.bs').textContent, ton: !!zeile.querySelector('.wortton'), ok: !!zeile.querySelector('.ok')}; }""")
    assert z == {"bs": "?", "ton": False, "ok": False}
    assert seite.fehler == []
