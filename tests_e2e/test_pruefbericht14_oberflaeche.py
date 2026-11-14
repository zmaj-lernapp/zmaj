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


# ---------------------------------------------------------------------------
# B13: Die richtige Antwort verraet sich nicht durch ihre Schrift
# ---------------------------------------------------------------------------
# Antworten ueber 14 Zeichen stehen kleiner und ohne Serifen da (.opt.long).
# Bis zum 14.11.2026 je Knopf: War nur die richtige lang, stand sie als
# einzige anders da ("ein alter Walnussbaum" in b1_ljeto), und umgekehrt -
# bei 31 B1-Fragen und 38 der alten Geschichten ueber alle Sprachen. Jetzt
# sind alle Knoepfe einer Aufgabe gleich: klein, sobald einer lang ist.
SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]

FRAGEN_ALLE = r"""() => {
  const aus = []; let lang = 0, kurz = 0, fragen = 0;
  STORIES.forEach((s, i) => {
    openStory(i); stilleBitte();
    (s.fragen || []).forEach((f, nr) => {
      showStoryQ(s, nr, 0); fragen++;
      const k = [...document.querySelectorAll('#rOpts .opt')];
      const klein = k.map(b => b.classList.contains('long'));
      const soll = k.some(b => b.textContent.length > 14);
      if(soll) lang++; else kurz++;
      if(!k.length || klein.some(x => x !== soll))
        aus.push([s.id, nr + 1, k.map(b => b.textContent), klein]);
    });
  });
  return {aus, lang, kurz, fragen};
}"""


def test_b13_alle_antworten_einer_frage_gleich_gross(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for sprache in SPRACHEN:
        seite.js("async (c) => { await setzeSprache(c); }", sprache)
        r = seite.js(FRAGEN_ALLE)
        assert r["aus"] == [], (sprache, r["aus"][:5])
        assert r["fragen"] >= 96 and r["lang"] > 0 and r["kurz"] > 0, (sprache, r)
    assert seite.fehler == []


def test_b13_walnussbaum_steht_nicht_mehr_allein_klein(seite, heute_stand):
    """Das Beispiel aus dem Bericht: "Was stand vor Omas Haus?" (b1_ljeto)."""
    seite.starten(stand=heute_stand())
    k = seite.js("""() => {
      const s = STORIES.find(x => x.id === 'b1_ljeto'), nr = s.fragen.findIndex(f => f.richtig === 'ein alter Walnussbaum');
      openStory(STORIES.indexOf(s)); stilleBitte(); showStoryQ(s, nr, 0);
      return [...document.querySelectorAll('#rOpts .opt')].map(b => [b.textContent, b.classList.contains('long')]);
    }""")
    assert len(k) == 3 and ["ein alter Walnussbaum", True] in k, k
    assert all(lang for _, lang in k), k
    assert seite.fehler == []


def test_b13_auch_in_der_lektion(seite, heute_stand):
    """renderChoice() baut auch die Auswahl in Lektion, Test und Grammatik:
    ein langer und drei kurze Knoepfe stehen alle klein da, vier kurze alle
    gross."""
    seite.starten(stand=heute_stand())
    r = seite.js("""() => {
      const box = document.createElement('div'); box.className = 'options';
      document.getElementById('rBody').appendChild(box);
      const knoepfe = liste => { renderChoice(box, liste.map(k => ({k})), liste[0], o => o.k, () => {});
                                 return [...box.querySelectorAll('.opt')].map(b => b.classList.contains('long')); };
      const aus = {gemischt: knoepfe(['Kühlschrank', 'Bedienungsanleitung', 'Tisch', 'Stuhl']),
                   kurz: knoepfe(['Kühlschrank', 'Tisch', 'Stuhl', 'Fenster'])};
      box.remove(); return aus;
    }""")
    assert r == {"gemischt": [True] * 4, "kurz": [False] * 4}, r
    assert seite.fehler == []
