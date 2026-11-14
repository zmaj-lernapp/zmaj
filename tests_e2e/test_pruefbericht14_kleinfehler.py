# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026), Kleinfehler der Oberflaeche im Browser
(Offen-Liste 4).

S16: "Weiter zu B1 →" auf dem Testergebnis brach bei 360 px so um, dass der
Pfeil allein in der zweiten Zeile stand, auf Tuerkisch in einer dritten.
Jetzt steht vor dem Pfeil ein geschuetztes Leerzeichen, in test.weiter_stufe
und test.weiter_level, in allen acht Sprachen.

S17: Bei 0 Leben haengt der Hinweis "Keine Leben mehr · naechstes in ..."
dauerhaft unter der Herzpille. Auf Daenisch und Niederlaendisch lag er bei
360 px 11 px ueber der Seriezahl. Jetzt rueckt die Reihe mit Serie und
Drache bei 0 Leben unter ihn, auch im engen Kopf und mit grosser Schrift.

S18: Unter dem Ergebnis von Lektion und Level-Test stand weiter
"✕ Lektion abbrechen" bzw. "✕ Test abbrechen" - es gab nichts mehr
abzubrechen. Jetzt ist der Knopf dort weg, wie nach dem Sprung-Test, auch
nach einer Wiederholen-Runde und auf dem Schirm ohne Leben. Beim naechsten
Start ist er wieder da; die Zurueck-Taste des Handys fuehrt wie bisher
hinaus.
"""
import pytest
from conftest import Seite

SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]

# So stellt Chrome die grosse Systemschrift des Handys nach (wie in test_reiter.py)
GROSSE_SCHRIFT = """document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.style.cssText += ';text-size-adjust:130%;-webkit-text-size-adjust:130%'; });"""

# Unterkante des Hinweises (mit seinen 2 px Schatten) und die Oberkanten von
# Serie und Drache auf der Startseite
LEBEN_HINWEIS = """() => { const i = document.querySelector('.livesbar .info');
  const reihe = document.querySelector('#pfad .obenreihe');
  return {hinweis: i ? i.getBoundingClientRect().bottom + 2 : null,
          oben: Math.min(...[...reihe.children].map(k => k.getBoundingClientRect().top)),
          zahl: document.getElementById('serieZahl').getBoundingClientRect().top,
          polster: getComputedStyle(reihe).paddingTop,
          eng: document.querySelector('header').classList.contains('eng'),
          breit: document.documentElement.scrollWidth}; }"""

# Steht der Pfeil im Knopf #tNext in derselben Zeile wie das Zeichen davor?
PFEIL = r"""() => { const b = document.getElementById('tNext');
  const tn = [...b.childNodes].find(n => n.nodeType === 3 && n.textContent.includes('→'));
  const s = tn.textContent, i = s.lastIndexOf('→');
  let j = i - 1; while(j >= 0 && /\s/.test(s[j])) j--;
  const r = (a, e) => { const g = document.createRange(); g.setStart(tn, a); g.setEnd(tn, e); return g.getClientRects()[0]; };
  return {text: s, pfeil: r(i, i + 1).top, davor: r(j, j + 1).top, vorPfeil: s.charCodeAt(i - 1)}; }"""


def _test_bestehen(seite, i):
    seite.js("(i) => { catIdx = i; cur().words.forEach(w => known.add(w.id)); openLevel(i); startTest(); }", i)
    seite.durchspielen("tBody", "Tx")
    assert seite.js("(i) => passed.has(levelNach(i).id)", i)


def _bestanden(seite, levels):
    """Genau diese Level (Nummern in CATEGORIES) gelten als bestanden."""
    seite.js("(l) => { passed.clear(); l.forEach(i => passed.add(CATEGORIES[i].id)); }", levels)


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_s16_pfeil_nie_allein_in_der_zeile(seite, heute_stand, sprache):
    seite.starten(sprache=sprache, stand=heute_stand())
    a1, a2 = seite.js("() => [reiterLevel('A1'), reiterLevel('A2')]")
    # Weiter zu Level 5 → (test.weiter_level)
    _bestanden(seite, a1[:3])
    _test_bestehen(seite, a1[3])
    p = seite.js(PFEIL)
    assert p["text"] == seite.js("() => t('test.weiter_level', {n: 5})"), p
    assert p["vorPfeil"] == 0xA0, p
    assert abs(p["pfeil"] - p["davor"]) < 1, (sprache, p)
    # Weiter zu B1 → (test.weiter_stufe): das letzte Level von A2 bestanden
    _bestanden(seite, a1 + a2[:-1])
    _test_bestehen(seite, a2[-1])
    p = seite.js(PFEIL)
    assert p["text"] == seite.js("() => t('test.weiter_stufe', {stufe: 'B1'})"), p
    assert p["vorPfeil"] == 0xA0, p
    assert abs(p["pfeil"] - p["davor"]) < 1, (sprache, p)
    assert seite.js("() => document.documentElement.scrollWidth") <= 360
    assert seite.fehler == []


# (Sprache, Breite, Muenzen, grosse Schrift): 360 px in jeder Sprache, dazu
# der enge Kopf (Muenzen in eigener Zeile) und die grosse Systemschrift
S17_FAELLE = [(s, 360, 0, False) for s in SPRACHEN] + [
    ("nl", 320, 12345, False), ("da", 320, 12345, False), ("da", 360, 0, True), ("nl", 360, 0, True)]


@pytest.mark.parametrize("sprache,breite,km,gross", S17_FAELLE,
                         ids=["%s-%d%s%s" % (s, b, "-eng" if k else "", "-gross" if g else "") for s, b, k, g in S17_FAELLE])
def test_s17_hinweis_ohne_leben_verdeckt_die_serie_nicht(browser, basis, heute_stand, sprache, breite, km, gross):
    import datetime
    ctx = browser.new_context(viewport={"width": breite, "height": 740}, locale="de-DE",
                              service_workers="block", reduced_motion="reduce")
    try:
        seite = Seite(ctx.new_page(), basis)
        seite.page.add_init_script("window.Capacitor = {Plugins: {App: {}}};")   # wie am Handy: keine Zurueck-Taste
        if gross:
            seite.page.add_init_script(GROSSE_SCHRIFT)
        heute = datetime.date.today()
        tage = [(heute - datetime.timedelta(days=i)).isoformat() for i in range(1, 32)]   # 31 Tage Serie
        seite.starten(sprache=sprache, stand=heute_stand(tage=tage))
        seite.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
        seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
        # Volle Leben: der Hinweis ist zu, nichts rueckt
        seite.js("(km) => { muenzenGes = km; muenzenAus = 0; homeMode = 'words'; showHome(); }", km)
        voll = seite.js(LEBEN_HINWEIS)
        assert voll["hinweis"] is None and voll["polster"] == "0px", voll
        # 0 Leben: der Hinweis steht da, Serie und Drache darunter
        seite.js("() => { lives = {anzahl: 0, zeit: Date.now()}; renderLives(); showHome(); }")
        m = seite.js(LEBEN_HINWEIS)
        if not gross:
            assert m["eng"] == (km > 0), m
        assert m["hinweis"] is not None and m["oben"] >= m["hinweis"] + 2, (sprache, m)
        assert m["zahl"] >= m["hinweis"] + 2 and m["breit"] <= breite, (sprache, m)
        # Ein Leben waechst nach: alles wieder wie vorher
        seite.js("() => { lives = {anzahl: 1, zeit: Date.now()}; livesInfoAn = false; renderLives(); }")
        assert seite.js(LEBEN_HINWEIS)["polster"] == "0px"
        assert seite.fehler == []
    finally:
        ctx.close()


# Sind "✕ Lektion abbrechen" und "✕ Test abbrechen" zu sehen?
ABBRECHEN = "() => ['lQuit', 'tQuit'].map(id => { const k = document.getElementById(id); return !!k.offsetParent; })"


def test_s18_kein_abbrechen_auf_dem_ergebnis(seite, heute_stand):
    seite.starten(stand=heute_stand())
    # Lektion: waehrend sie laeuft da, auf dem Ergebnis weg, "Noch eine" wieder da
    seite.js("() => { openLevel(0); startLesson(); }")
    assert seite.js(ABBRECHEN) == [True, False]
    seite.durchspielen("lBody", "Lx")
    assert seite.js("() => !!document.getElementById('lMore')"), "kein Ergebnisschirm"
    assert seite.js(ABBRECHEN) == [False, False]
    seite.page.click("#lMore")
    assert seite.js(ABBRECHEN) == [True, False]
    # Die Zurueck-Taste auf dem Ergebnis fuehrt weiter hinaus, ohne Nachfrage
    seite.durchspielen("lBody", "Lx")
    seite.js("() => zurueckTaste()")
    assert seite.js("() => [sichtbar('levelView'), document.getElementById('levelHome').style.display]") == [True, "block"]
    assert seite.js("() => !!document.querySelector('.nachfrage')") is False
    # Level-Test: ebenso, "Nochmal" bzw. ein neuer Test zeigt ihn wieder
    seite.js("() => { cur().words.forEach(w => known.add(w.id)); startTest(); }")
    assert seite.js(ABBRECHEN) == [False, True]
    seite.durchspielen("tBody", "Tx")
    assert seite.js("() => !!document.getElementById('tBack')"), "kein Testergebnis"
    assert seite.js(ABBRECHEN) == [False, False]
    seite.js("() => startTest()")
    assert seite.js(ABBRECHEN) == [False, True]
    # Wiederholen-Runde: dasselbe Feld wie die Lektion
    ids = seite.js("() => CATEGORIES[0].words.slice(0, 3).map(w => w.id)")
    seite.js("""(ids) => { topf = {}; ids.forEach((id, i) => { topf['w:' + id] = {typ: 'mc', n: 0, z: 1000 + i}; });
        homeMode = 'topf'; showHome(); startTopf(); }""", ids)
    assert seite.js(ABBRECHEN) == [True, False]
    seite.durchspielen("lBody", "Lx")
    assert seite.js("() => !!document.querySelector('#lBody .result-big')"), "kein Rundenende"
    assert seite.js(ABBRECHEN) == [False, False]
    # Ohne Leben: der Schirm ist das Ende der Lektion bzw. des Tests
    for start, feld in (("openLevel(0); startLesson();", "lBody"), ("openLevel(0); startTest();", "tBody")):
        seite.js("() => { lives = {anzahl: 5, zeit: Date.now()}; %s }" % start)
        seite.js("(t) => { lives = {anzahl: 0, zeit: Date.now()}; lessonOutOfLives(t); }", feld == "tBody")
        assert seite.js("(f) => !!document.querySelector('#' + f + ' .ohneleben')", feld)
        assert seite.js(ABBRECHEN) == [False, False], feld
    assert seite.fehler == []
