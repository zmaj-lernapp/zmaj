# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026) im Browser: Lesetexte und Antwortknoepfe.

V2: Die Blase mit der Bedeutung eines angetippten Wortes stand hinter dem
ganzen Text, und die Seite scrollte nicht. Wer oben ein Wort antippte, sah
nur die gelbe Markierung - bei 360 und 412 px in allen 20 B1-Texten, bei
360 px auch in "intervju" (Wort bei 463 px, Blase bei 1544 px). Jetzt sitzt
sie unten im Bild fest, und das angetippte Wort bleibt darueber zu sehen.
"""
import pytest
from conftest import Seite

# Jede Geschichte oeffnen, ganz oben, und zwei Woerter des ersten
# Bildschirms antippen: eines aus der Mitte und das unterste ganz sichtbare
# (das liegt am ehesten unter der Blase). Gemessen wird nach dem Antippen.
BLASE = r"""async (i) => {
  const warte = ms => new Promise(r => setTimeout(r, ms));
  openStory(i); stilleBitte(); window.scrollTo(0, 0); await warte(30);
  const vh = innerHeight, aus = [];
  const ganz = w => { const q = w.getBoundingClientRect(); return q.top >= 0 && q.bottom <= vh; };
  const sichtbar = [...document.querySelectorAll('#rBody .txt .w')].filter(ganz);
  const wahl = [sichtbar[Math.floor(sichtbar.length / 2)], sichtbar[sichtbar.length - 1]];
  for(const w of wahl){
    window.scrollTo(0, 0); await warte(30);
    w.click(); await warte(80);
    const b = document.getElementById('rBubble'), q = b.getBoundingClientRect(), r = w.getBoundingClientRect();
    aus.push({id: STORIES[i].id, wort: w.textContent, vh, hidden: b.hidden,
              blaseOben: Math.round(q.top), blaseUnten: Math.round(q.bottom),
              wortOben: Math.round(r.top), wortUnten: Math.round(r.bottom),
              inhalt: b.querySelector('b') ? b.querySelector('b').textContent : ''});
  }
  return aus;
}"""


@pytest.mark.parametrize("breite,hoehe", [(360, 740), (412, 915)])
def test_v2_blase_im_bild_bei_jedem_lesetext(browser, basis, heute_stand, breite, hoehe):
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, locale="de-DE",
                              service_workers="block", reduced_motion="reduce")
    try:
        s = Seite(ctx.new_page(), basis)
        s.starten(stand=heute_stand())
        s.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
        s.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
        n = s.js("() => STORIES.length")
        assert n >= 32
        fehler = []
        for i in range(n):
            for m in s.js(BLASE, i):
                if m["hidden"] or m["inhalt"] != m["wort"]:
                    fehler.append(("keine Blase", m))
                elif m["blaseOben"] < 0 or m["blaseUnten"] > m["vh"]:
                    fehler.append(("Blase nicht im Bild", m))
                elif m["wortOben"] < 0 or m["wortUnten"] > m["blaseOben"]:
                    fehler.append(("Wort verdeckt oder weg", m))
        assert fehler == [], fehler[:6]
        assert s.fehler == []
    finally:
        ctx.close()


def test_v2_mitlesen_scrollt_vor_der_blase(seite, heute_stand):
    """Beim Vorlesen rueckt die Seite nach, sobald das aktuelle Wort hinter
    die festsitzende Blase geraet - nicht erst am Bildschirmrand."""
    seite.page.emulate_media(reduced_motion="reduce")      # ohne Animation: scrollt sofort
    seite.starten(stand=heute_stand())
    r = seite.js("""() => {
      const i = STORIES.findIndex(s => s.id === 'b1_ljeto');
      openStory(i); stilleBitte(); window.scrollTo(0, 0);
      const ws = [...document.querySelectorAll('#rBody .txt .w')];
      ws[0].click();
      const b = document.getElementById('rBubble').getBoundingClientRect();
      // das erste Wort, das hinter der Blase liegt, aber noch im Bildschirm
      const dahinter = ws.find(w => { const q = w.getBoundingClientRect(); return q.bottom > b.top && q.top < innerHeight; });
      if(!dahinter) return {kein: true, blase: b.top, vh: innerHeight};
      const vorher = scrollY, davor = ws[ws.indexOf(dahinter) - 1];
      mitlesenImBlick(dahinter, davor);
      return {kein: false, gescrollt: scrollY > vorher};
    }""")
    assert r["kein"] is False, r
    assert r["gescrollt"], r
    assert seite.fehler == []
