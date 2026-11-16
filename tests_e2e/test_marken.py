# -*- coding: utf-8 -*-
"""Die gelben Marken ueber der Aufgabe ueberlappen nicht (12.11.2026).

Ajdin am 11.11.2026 mit einem Bildschirmfoto von seinem S21 (360 Punkte
breit): "das bild hab ich geschickt weil sie die beiden gelben infos
ueberlappen". Im Wiederholen stand "Wiederholung: Wetter & Natur" ueber
"Noch einmal", und die zweite Marke klebte ohne jeden Abstand an der ersten.
Die Zeile mit den Marken hat font-size:0 (sie blendet den Anweisungstext
aus, siehe .kicker.aufgabe in index.html), umgebrochene Marken lagen deshalb
Kante an Kante - auf dem Handy mit seiner Pixelrundung uebereinander.

Geprueft wird hier:
  - mit dem in Pixeln laengsten Levelnamen jeder der acht Sprachen, bei
    360 x 780 und 320 x 640, normaler und grosser Systemschrift: beide
    Marken im Kasten, ohne Ueberlappung, umgebrochen mit 6 px Abstand,
    nebeneinander mit 8 px, jede Zeile mittig, nichts rollt quer;
  - mit einer Zeile Marken steht alles genau da, wo es vor dem 12.11.2026
    stand: die Marke 6 px unter dem Drachen, die Aufgabe 8 px darunter,
    ohne Marke kein Platz fuer sie;
  - im Level-Test gilt dasselbe (gleiche Regeln, gleiches kick()).
"""
import pytest
from conftest import Seite

SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]

# So stellt Chrome die grosse Systemschrift des Handys nach (wie in
# test_kaufkasten.py)
GROSSE_SCHRIFT = """document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.style.cssText += ';text-size-adjust:130%;-webkit-text-size-adjust:130%'; });"""

# Die Aufgabe mit den gewuenschten Marken an die Stelle der ersten Wortaufgabe
# der Lektion (bzw. des Level-Tests) legen, zeigen und vermessen.
# kat: Kennung eines Levels oder '' fuer den in Pixeln laengsten Levelnamen.
MESSEN = r"""async ([ort, art, kat]) => {
  let lv = null;
  if(kat) lv = CATEGORIES.find(c => c.id === kat);
  else {
    const probe = document.createElement('span');
    probe.className = 'rep';
    probe.style.cssText = 'position:absolute; visibility:hidden; white-space:nowrap; font-size:13px';
    document.body.appendChild(probe);
    let breit = 0;
    CATEGORIES.forEach(c => { probe.textContent = t('task.wiederholung', {label: c.label});
      const b = probe.getBoundingClientRect().width; if(b > breit){ breit = b; lv = c; } });
    probe.remove();
  }
  const marken = art === 'beide' ? {rep: lv.label, pool: lv.words, retry: true}
               : art === 'rep' ? {rep: lv.label, pool: lv.words}
               : art === 'nochmal' ? {retry: true} : {};
  let body;
  if(ort === 'test'){
    CATEGORIES[0].words.forEach(x => known.add(x.id));
    openLevel(0); startTest();
    const w = CATEGORIES[0].words[0];
    Tx.qs[0] = {typ: 'mc', w, pool: CATEGORIES[0].words, ...marken};
    Tx.i = 0; Tx.results = []; Tx.right = 0; showTestQ();
    body = document.getElementById('tBody');
  } else {
    openLevel(1); startLesson();
    const i = Lx.queue.findIndex(a => a.w && a.typ !== 'intro');
    const a = {typ: art === 'intro' ? 'intro' : 'mc', w: Lx.queue[i].w, pool: CATEGORIES[1].words, ...marken};
    Lx.queue[i] = a; Lx.i = i; showLessonTask();
    body = document.getElementById('lBody');
  }
  await document.fonts.ready;
  const box = e => { const r = e.getBoundingClientRect();
    return {x: r.left, y: r.top + scrollY, w: r.width, h: r.height, r: r.right, b: r.bottom + scrollY}; };
  const k = body.querySelector('.kicker.aufgabe');
  const card = body.closest('.card');
  const cs = getComputedStyle(card);
  const innen = box(card);
  innen.x += parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth);
  innen.r -= parseFloat(cs.paddingRight) + parseFloat(cs.borderRightWidth);
  return {
    label: lv.label,
    marken: [...k.querySelectorAll('.rep')].map(e => ({t: e.textContent, ...box(e)})),
    kicker: box(k), innen,
    drache: box(body.closest('section').querySelector('.zmaj.mini')),
    danach: box(k.nextElementSibling),
    quer: document.documentElement.scrollWidth > innerWidth,
  };
}"""


def _seite(browser, basis, heute_stand, breite, hoehe, gross, sprache="de"):
    optionen = {"is_mobile": True, "has_touch": True}
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, device_scale_factor=3,
                              locale="de-DE", service_workers="block", **optionen)
    if gross:
        ctx.add_init_script(GROSSE_SCHRIFT)
    seite = Seite(ctx.new_page(), basis)
    seite.starten(sprache=sprache, stand=heute_stand())
    return ctx, seite


def _pruefen(m, wo):
    """Die Marken liegen im Kasten, ueberlappen nicht und haben Abstand."""
    marken = m["marken"]
    assert len(marken) == 2, (wo, marken)
    a, b = marken
    for x in marken:
        assert x["x"] >= m["innen"]["x"] - 0.5 and x["r"] <= m["innen"]["r"] + 0.5, ("ragt aus dem Kasten", wo, x, m["innen"])
    getrennt = (a["r"] <= b["x"] or b["r"] <= a["x"] or a["b"] <= b["y"] or b["b"] <= a["y"])
    assert getrennt, ("Marken ueberlappen", wo, marken)
    if b["y"] >= a["b"] - 0.5:                      # umgebrochen: untereinander
        assert b["y"] - a["b"] == pytest.approx(6, abs=0.6), ("Abstand untereinander", wo, marken)
        mitte = (m["kicker"]["x"] + m["kicker"]["r"]) / 2
        for x in marken:
            assert (x["x"] + x["r"]) / 2 == pytest.approx(mitte, abs=1), ("nicht mittig", wo, x, mitte)
    else:                                            # nebeneinander
        assert a["y"] == pytest.approx(b["y"], abs=0.5), (wo, marken)
        assert b["x"] - a["r"] == pytest.approx(8, abs=0.6), ("Abstand nebeneinander", wo, marken)
    assert not m["quer"], ("rollt quer", wo)


@pytest.mark.parametrize("gross", [False, True], ids=["normal", "grosse_schrift"])
@pytest.mark.parametrize("breite,hoehe", [(360, 780), (320, 640)])
def test_laengster_levelname_in_jeder_sprache(browser, basis, heute_stand, breite, hoehe, gross):
    fehler = []
    for sprache in SPRACHEN:
        ctx, seite = _seite(browser, basis, heute_stand, breite, hoehe, gross, sprache)
        try:
            for kat in ("", "wetter"):   # der laengste Name und der vom Bildschirmfoto
                m = seite.js(MESSEN, ["lektion", "beide", kat])
                _pruefen(m, (sprache, breite, gross, m["label"]))
            fehler += seite.fehler
        finally:
            ctx.close()
    assert fehler == []


@pytest.mark.parametrize("gross", [False, True], ids=["normal", "grosse_schrift"])
def test_eine_zeile_marken_steht_wie_vorher(browser, basis, heute_stand, gross):
    """Die 6 px Rand je Marke heben die -6 px an der Zeile wieder auf: mit
    einer Zeile Marken (auch "Neues Wort") steht alles, wo es vorher stand."""
    ctx, seite = _seite(browser, basis, heute_stand, 360, 780, gross)
    try:
        ohne = seite.js(MESSEN, ["lektion", "keine", "wetter"])
        assert ohne["marken"] == [] and ohne["kicker"]["h"] == 0
        assert "mitmarke" not in seite.js("() => document.querySelector('#lBody .kicker').className")
        for art in ("rep", "nochmal", "intro"):
            m = seite.js(MESSEN, ["lektion", art, "wetter"])
            assert len(m["marken"]) == 1, (art, m["marken"])
            x = m["marken"][0]
            assert x["y"] - m["drache"]["b"] == pytest.approx(ohne["kicker"]["y"] - ohne["drache"]["b"], abs=0.5), art
            assert m["danach"]["y"] - x["b"] == pytest.approx(8, abs=0.5), art
            if art != "intro":       # "Neues Wort" hat darunter eine andere Zeile
                assert m["danach"]["y"] - ohne["danach"]["y"] == pytest.approx(x["h"], abs=0.5), art
            mitte = (m["kicker"]["x"] + m["kicker"]["r"]) / 2
            assert (x["x"] + x["r"]) / 2 == pytest.approx(mitte, abs=1), ("nicht mittig", art)
        # Zwei Zeilen: genau 6 px dazwischen, und darunter wieder 8
        m = seite.js(MESSEN, ["lektion", "beide", "wetter"])
        a, b = m["marken"]
        assert b["y"] - a["b"] == pytest.approx(6, abs=0.5)
        assert m["danach"]["y"] - b["b"] == pytest.approx(8, abs=0.5)
        assert seite.fehler == []
    finally:
        ctx.close()


def test_im_level_test_ebenso(browser, basis, heute_stand):
    ctx, seite = _seite(browser, basis, heute_stand, 320, 640, True)
    try:
        m = seite.js(MESSEN, ["test", "beide", ""])
        _pruefen(m, ("test", m["label"]))
        assert seite.fehler == []
    finally:
        ctx.close()
