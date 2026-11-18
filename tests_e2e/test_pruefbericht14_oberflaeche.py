# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026) im Browser: Lesetexte, Antwortknoepfe und
die Geschichtenliste.

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


# ---------------------------------------------------------------------------
# B14 / E3: Geschichtentitel ganz lesbar, das Schildchen weicht aus
# ---------------------------------------------------------------------------
# Bis zum 14.11.2026 kuerzte der Titel in der Geschichtenliste ab, damit das
# Schildchen daneben stehen blieb - in Franzoesisch bei 360 px bei 14 von 32
# Geschichten ("Na op...", "Razgo..."). Ajdin hat entschieden (E3, Weg a):
# der Titel ist immer ganz zu lesen, das Schildchen rutscht in die Zeile
# darunter, wenn es daneben keinen Platz hat.
#
# Gemessen wird jede Geschichte in jedem Zustand (gelesen, jetzt dran,
# gesperrt, offen): einmal mit den ersten k gelesen fuer jedes k, einmal mit
# jeder zweiten. Der Zustand rechts nimmt dem Titel Platz, "À faire
# maintenant" am meisten. Abgeschnitten heisst: der Kasten des Titels ist
# schmaler als sein Text, oder der Text (Range, also auch der verdeckte Teil)
# ragt aus dem Titel, der Zeile oder dem Knopf.
# Seit dem 17.11.2026 stehen die Geschichten in Stufen-Reitern: gemessen wird in
# jedem Zustand jeder Reiter, so kommt weiter jede Geschichte dran. Das
# Schildchen zeigt seitdem nur noch die Stufe (A1, A2, B1).
TITEL_MESSEN = r"""async () => {
  await document.fonts.ready;
  const aus = [], vorher = [...read];
  const faelle = [];
  for(let k = 0; k <= STORIES.length; k++) faelle.push(STORIES.slice(0, k).map(s => s.id));
  faelle.push(STORIES.filter((s, i) => i % 2 === 0).map(s => s.id));
  let knoten = 0, zweizeilig = 0, darunter = 0, daneben = 0, hoechstens = 0;
  const innen = (q, r) => q.left >= r.left - 0.5 && q.right <= r.right + 0.5;
  for(const ids of faelle){
    read.clear(); ids.forEach(id => read.add(id));
    for(const reiter of STUFEN){
     if(!geschImReiter(reiter).length) continue;
     geschGewaehlt = {st: reiter, bei: geschStufe(geschNaechste())}; showStoryPath();
     [...document.querySelectorAll('#storyList .node')].forEach((n, k) => {
      const i = geschImReiter(reiter)[k];
      knoten++;
      const t = n.querySelector('.titel'), st = n.querySelector('.stufe'), z = n.querySelector('.state');
      const nr = n.getBoundingClientRect(), lr = n.querySelector('.label').getBoundingClientRect(),
            tr = t.getBoundingClientRect(), zr = z.getBoundingClientRect();
      const rg = document.createRange(); rg.selectNodeContents(t);
      const zeilen = [...rg.getClientRects()].filter(q => q.width > 0);
      const tops = [...new Set(zeilen.map(q => Math.round(q.top)))];
      const fehler = [];
      if(t.clientWidth > 0 && t.scrollWidth > t.clientWidth) fehler.push('Titel gekuerzt');
      if(!zeilen.every(q => innen(q, tr) && innen(q, lr) && innen(q, nr))) fehler.push('Titel ragt hinaus');
      if(tops.length > 2) fehler.push(tops.length + ' Zeilen');
      if(!innen(lr, nr) || !innen(zr, nr) || lr.right > zr.left + 0.5) fehler.push('Zeile ragt hinaus');
      hoechstens = Math.max(hoechstens, tops.length);
      if(tops.length > 1) zweizeilig++;
      if(st){
        const sr = st.getBoundingClientRect(), letzte = zeilen[zeilen.length - 1];
        if(st.scrollWidth > st.clientWidth) fehler.push('Schildchen gekuerzt');
        if(!innen(sr, lr) || !innen(sr, nr)) fehler.push('Schildchen ragt hinaus');
        const mitte = q => (q.top + q.bottom) / 2;
        const gleicheZeile = Math.abs(mitte(sr) - mitte(letzte)) < 6;
        if(gleicheZeile) daneben++; else darunter++;
        if(!gleicheZeile && sr.top < letzte.bottom - 1) fehler.push('Schildchen ueberlappt den Titel');
        // daneben, wenn es hinter dem letzten Wort Platz hat (8 Punkte Abstand)
        if(!gleicheZeile && letzte.right + 8 + sr.width <= lr.right - 1) fehler.push('Schildchen ohne Grund darunter');
        if(gleicheZeile && sr.left < letzte.right + 6) fehler.push('Schildchen klebt am Titel');
      }
      if(fehler.length) aus.push([i, STORIES[i].titel, z.textContent, fehler.join(', ')]);
     });
    }
  }
  geschGewaehlt = null;
  read.clear(); vorher.forEach(id => read.add(id)); showStoryPath();
  const breit = document.documentElement.scrollWidth > document.documentElement.clientWidth;
  return {aus, knoten, zweizeilig, darunter, daneben, hoechstens, breit};
}"""


@pytest.mark.parametrize("breite,hoehe", [(360, 740), (412, 915)])
def test_b14_geschichtentitel_nie_abgeschnitten(seite, heute_stand, breite, hoehe):
    seite.page.set_viewport_size({"width": breite, "height": hoehe})
    seite.starten(stand=heute_stand())
    darunter = {}
    for sprache in SPRACHEN:
        seite.js("async (c) => { await setzeSprache(c); homeMode = 'stories'; showHome(); }", sprache)
        r = seite.js(TITEL_MESSEN)
        assert r["aus"] == [], (sprache, breite, len(r["aus"]), r["aus"][:6])
        assert r["breit"] is False, (sprache, breite)
        # Seit dem 18.11.2026 gibt es kein Schildchen mehr (Ajdin: "ja weg").
        assert r["knoten"] >= 33 * 32 and r["daneben"] == 0 and r["darunter"] == 0, (sprache, r)
        darunter[sprache] = r["darunter"]
    assert seite.fehler == []


def test_b14_kurze_titel_wie_vorher(seite, heute_stand):
    """Wo alles in eine Zeile passt, bleibt es dabei: Titel und Schildchen
    nebeneinander, mittig zueinander, 8 Punkte Abstand, eine Zeile hoch.
    Der Stand wie im Bild aus dem Bericht (fr, 360 px): 12 gelesen, die
    13. dran - dort standen die ersten neun schon vorher so da. Seit dem
    17.11.2026 in den Reitern A1 und A2 (alle elf gelesen), das Schildchen
    nur noch mit der Stufe: dort passen jetzt alle elf daneben."""
    seite.starten(stand=heute_stand())
    r = seite.js("""async () => {
      await setzeSprache('fr'); await document.fonts.ready;
      read.clear(); STORIES.slice(0, 12).forEach(s => read.add(s.id));
      homeMode = 'stories'; showHome();
      const aus = [];
      for(const st of ['A1', 'A2']){
        geschStufeWaehlen(st);
        [...document.querySelectorAll('#storyList .node')].forEach(n => {
          const t = n.querySelector('.titel').getBoundingClientRect();
          aus.push({titel: n.querySelector('.titel').textContent, schild: !!n.querySelector('.stufe'), reiter: st,
                    hoehe: n.querySelector('.label').getBoundingClientRect().height, titelHoehe: t.height});
        });
      }
      return aus;
    }""")
    assert [x["titel"] for x in r[:3]] == ["Mira i Rex", "Moja porodica", "Naša kuća"], r
    assert [x["reiter"] for x in r] == ["A1"] * 5 + ["A2"] * 6, r
    # Seit dem 18.11.2026 ohne Schildchen: die Stufe steht nur noch im Reiter.
    for x in r:
        assert x["schild"] is False, x
        assert x["hoehe"] <= x["titelHoehe"] + 0.5, x
    assert seite.fehler == []
