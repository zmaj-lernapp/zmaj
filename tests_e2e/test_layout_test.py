# -*- coding: utf-8 -*-
"""Level-Test und Einstufung sehen aus wie die Lektion (19.10.2026).

Kuebra beim Testen: "Das Test-Layout ist anders als die normale Session -
im Test sind die Knoepfe viel hoeher als in der normalen Level-Umgebung."
Nachgemessen stimmte das: dem Level-Test fehlten Drache und Herz-Pille,
Frage und Antwortknoepfe hatten eine kleinere Schrift, und unter den
Punkten stand ein eigener Abstand. Die Antwortknoepfe sassen dadurch bei
412 x 915 rund 140 px hoeher als in der Lektion, Weiter ebenso. Die
Einstufung wich auf eigene Art ab (Kopf und Fuss der App sichtbar,
Anweisungszeile, kein .kastenkopf, kein .antwortfeld) - bis zu 65 px.

Seitdem bauen alle drei ihren Fragenkasten gleich (siehe .zmaj.mini im CSS
von index.html). Dieser Test legt DIESELBE Aufgabe mit demselben Zufall
(also auch derselben Reihenfolge der Antworten) einmal in die Lektion,
einmal in den Level-Test und einmal in die Einstufung und vergleicht, wo
Frage, erste Antwort bzw. Eingabefeld, Pruefen und - nach der richtigen
Antwort - Weiter stehen. Erlaubt sind 2 px.

Gemessen wird in Seitenkoordinaten (Oberkante plus scrollY), damit das
sanfte Scrollen zu Weiter das Ergebnis nicht verschiebt. Jeder Ort bekommt
eine eigene, frische Seite - wie im Messskript vom 19.10.2026, aus dem
dieser Test stammt.

Zwei Formate: 412 x 915 (Drache 120 px) und 360 x 726, Ajdins S21 in der
App (gemessen 01.10.2026). Dort greift max-height:820px und der Drache ist
100 px gross - auch das muss an allen drei Orten gleich sein.

Am Abend desselben Tages entschied Ajdin, dass der Level-Test Leben kostet
wie die Lektion. Seitdem ist das Herz im Test kein unsichtbarer Platzhalter
mehr, sondern echt - es muss sichtbar sein und genau dort stehen, wo es in
der Lektion steht. Nur die Einstufung behaelt den Platzhalter.

Dazu prueft test_kleine_drachen_laufen_nicht_unsichtbar, dass die kleinen
Lottie-Drachen nach Abbruch und Ergebnis nicht hinter der Level-Uebersicht
weiterlaufen.
"""
import pytest
from conftest import Seite

# Breite x Hoehe, Pixeldichte, erwartete Groesse des kleinen Drachen.
FORMATE = [
    pytest.param({"width": 412, "height": 915}, 2.625, 120, id="412x915"),
    pytest.param({"width": 360, "height": 726}, 3.0, 100, id="360x726"),
    # Seit 30.10.2026 auch das 10-Zoll-Tablet hochkant (test_tablet.py):
    # alles mal 1,304, der Drache 190 Punkte, also 248 auf dem Bildschirm.
    pytest.param({"width": 800, "height": 1280}, 2.0, 248, id="tablet_800x1280"),
]
# Im echten Test kommen mc, mcrev, type und gram vor, in der Einstufung
# mc, mcrev, gap und gram - alle fuenf laufen an allen drei Orten.
TYPEN = ["mc", "mcrev", "type", "gap", "gram"]
ORTE = ["lektion", "test", "einstufung"]
FELD = {"lektion": "lBody", "test": "tBody", "einstufung": "eBody"}
TOLERANZ = 2

# Fester Zufall direkt vor renderTask (sonst mischt jede Aufgabe ihre
# Antworten anders) und je Typ eine feste Aufgabe aus Level 1.
HELFER = r"""
() => {
  const saat = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  window.__saatWert = null;
  if(!window.__rtOrig){
    window.__rtOrig = renderTask;
    renderTask = function(){
      if(window.__saatWert != null){ Math.random = saat(window.__saatWert); window.__saatWert = null; }
      return window.__rtOrig.apply(this, arguments);
    };
  }
  const c0 = CATEGORIES[0];
  const w = c0.words.find(x => typable(x) && x.de.length <= 14 && x.bs.length <= 10 && x.bs.length >= 4) || c0.words[0];
  const gap = SENTENCES.find(x => x.kat === c0.id && x.text.indexOf('___') >= 0)
           || SENTENCES.find(x => x.text.indexOf('___') >= 0);
  let gram = null;
  for(const c of CATEGORIES){
    const u = (GRAMMAR[c.id] || {}).uebungen || [];
    const g = u.find(x => x.optionen.length >= 3);
    if(g){ gram = g; break; }
  }
  window.__aufgabe = typ => {
    if(typ === 'gap') return {typ, s: gap};
    if(typ === 'gram') return {typ, g: gram};
    return {typ, w, pool: c0.words};
  };
  return !!(w && gap && gram);
}
"""

# Aufgabe an den Anfang des Durchgangs legen, messen, richtig antworten,
# Weiter messen und antippen (sonst haengt der Horcher von weiterBeiTipp
# noch am Feld und blaettert bei der naechsten Aufgabe mit).
DURCHGANG = r"""
async ([ort, typ, seed, feld]) => {
  const warte = ms => new Promise(r => setTimeout(r, ms));
  const body = document.getElementById(feld);
  const task = __aufgabe(typ);
  if(ort === 'lektion'){
    openLevel(0); startLesson();
    Lx.queue[0] = task; Lx.i = 0; Lx.results = [];
    window.__saatWert = seed; showLessonTask();
  } else if(ort === 'test'){
    CATEGORIES[0].words.forEach(x => known.add(x.id));
    openLevel(0); startTest();
    Tx.qs[0] = task; Tx.i = 0; Tx.results = []; Tx.right = 0;
    window.__saatWert = seed; showTestQ();
  } else {
    baueEinstufung('etwas');
    Ex.qs[0] = task; Ex.i = 0;
    window.__saatWert = seed; einstufungStarten();
  }
  await document.fonts.ready;
  await warte(200);
  const y = el => {
    if(!el) return null;
    const b = el.getBoundingClientRect();
    if(b.width === 0 && b.height === 0) return null;
    return Math.round(b.top + window.scrollY);
  };
  const q = s => body.querySelector(s);
  const ersteAntwort = () => q('.options:not(.kachelbank) .opt') || q('#xIn');
  const vor = {frage: y(q('.prompt') || q('.big') || q('.sentence') || q('.ex-q')),
               antwort: y(ersteAntwort()), pruefen: y(q('#xCheck'))};
  if(typ === 'gap' || typ === 'type'){
    q('#xIn').value = (typ === 'gap' ? task.s.answer : task.w.bs).split(' / ')[0];
    q('#xCheck').click();
  } else {
    const soll = typ === 'gram' ? task.g.richtig : (typ === 'mcrev' ? task.w.de : task.w.bs);
    const b = [...body.querySelectorAll('.opt')].find(o => o.textContent === soll);
    if(!b) throw new Error('kein Knopf ' + soll);
    b.click();
  }
  const ende = Date.now() + 6000;
  while(!q('.weiterbox')){ if(Date.now() > ende) throw new Error('kein Weiter bei ' + ort + '/' + typ); await warte(20); }
  await warte(150);
  const nach = {antwort: y(ersteAntwort()), weiter: y(q('.weiterbox .btn'))};
  const sec = body.closest('section');
  const drache = sec.querySelector('.zmaj.mini');
  const herz = sec.querySelector('.kastenherz');
  const kopf = document.querySelector('header');
  const hb = herz ? herz.getBoundingClientRect() : null;
  const info = {
    drache: drache ? Math.round(drache.getBoundingClientRect().height) : 0,
    herz: herz ? getComputedStyle(herz).visibility : null,
    herz_box: hb ? [Math.round(hb.left), Math.round(hb.top + window.scrollY), Math.round(hb.width), Math.round(hb.height)] : null,
    // Das Herz ist seit dem 24.10.2026 ein Bild (web/symbole/herz.webp):
    // als ♥ mitzaehlen, wenn es da ist.
    herz_text: herz ? (herz.querySelector('img.sym-herz') ? '♥' : '') + herz.textContent : null,
    kopf_sichtbar: !!(kopf && kopf.getClientRects().length),
  };
  stilleBitte();
  q('.weiterbox .btn').click();
  await warte(250);
  stilleBitte();
  return {vor, nach, info};
}
"""


@pytest.fixture
def handy(browser, basis):
    kontexte = []

    def neu(heute_stand, viewport, dpr):
        ctx = browser.new_context(viewport=viewport, device_scale_factor=dpr, is_mobile=True, has_touch=True,
                                  locale="de-DE", service_workers="block")
        kontexte.append(ctx)
        s = Seite(ctx.new_page(), basis)
        s.starten(stand=heute_stand())
        assert s.js(HELFER), "keine passende Aufgabe in den Daten"
        return s

    yield neu
    for ctx in kontexte:
        ctx.close()


@pytest.mark.parametrize("viewport, dpr, drache", FORMATE)
def test_test_und_einstufung_wie_lektion(handy, heute_stand, viewport, dpr, drache):
    messung, fehler = {}, []
    for ort in ORTE:
        seite = handy(heute_stand, viewport, dpr)
        for n, typ in enumerate(TYPEN):
            messung[(ort, typ)] = seite.js(DURCHGANG, [ort, typ, 1000 + n, FELD[ort]])
        fehler += ["%s: %s" % (ort, f) for f in seite.fehler]
    assert fehler == [], "Skriptfehler: %s" % fehler

    abweichungen = []
    for typ in TYPEN:
        lektion = messung[("lektion", typ)]
        for ort in ("test", "einstufung"):
            m = messung[(ort, typ)]
            for phase in ("vor", "nach"):
                for teil, soll in lektion[phase].items():
                    ist = m[phase].get(teil)
                    if soll is None and ist is None:
                        continue
                    if soll is None or ist is None or abs(ist - soll) > TOLERANZ:
                        abweichungen.append("%s %s %s %s: Lektion y=%s, hier y=%s" % (ort, typ, phase, teil, soll, ist))
    assert abweichungen == [], "nicht an derselben Stelle wie in der Lektion:\n" + "\n".join(abweichungen)

    # Gemessen wurde wirklich etwas: jede Aufgabe hat eine Antwort und Weiter.
    for (ort, typ), m in messung.items():
        assert m["vor"]["antwort"] is not None, (ort, typ)
        assert m["nach"]["weiter"] is not None, (ort, typ)

    for ort in ORTE:
        info = messung[(ort, "mc")]["info"]
        assert info["drache"] == drache, "%s: kleiner Drache %s px statt %s px" % (ort, info["drache"], drache)
        assert not info["kopf_sichtbar"], "%s: Kopfzeile der App sichtbar" % ort
    # Der Level-Test kostet seit dem 19.10.2026 Leben wie die Lektion und
    # zeigt dasselbe echte Herz. Die Einstufung kostet keine - ihr Herz
    # haelt nur den Platz. Die Positionen oben sind trotzdem dieselben.
    assert messung[("lektion", "mc")]["info"]["herz"] == "visible"
    assert messung[("test", "mc")]["info"]["herz"] == "visible"
    assert messung[("einstufung", "mc")]["info"]["herz"] == "hidden"
    herz_l, herz_t = messung[("lektion", "mc")]["info"], messung[("test", "mc")]["info"]
    assert herz_t["herz_text"] == herz_l["herz_text"] == "♥ 5", (herz_l["herz_text"], herz_t["herz_text"])
    assert all(abs(a - b) <= TOLERANZ for a, b in zip(herz_l["herz_box"], herz_t["herz_box"])), \
        "Herz im Test %s, in der Lektion %s" % (herz_t["herz_box"], herz_l["herz_box"])


# Jeder Lottie-Drache, der laeuft, ohne dass man ihn sieht - als Kennung des
# naechsten Vorfahren mit id. Pausierte (Standbild) stoeren nicht.
UNSICHTBAR = r"""
() => lottie.getRegisteredAnimations()
  .filter(a => !a.isPaused && !(a.wrapper && a.wrapper.getClientRects().length))
  .map(a => { const e = a.wrapper && a.wrapper.closest('[id]'); return e ? e.id : '?'; })
"""
GELADEN = "id => { const e = document.querySelector('#' + id + ' .zmaj-anim'); return !!(e && e._anim && e._anim.isLoaded); }"
RESTE = "() => document.querySelectorAll('#zmajLesson .zmaj-anim, #zmajTest .zmaj-anim, #zmajEinst .zmaj-anim').length"


def test_kleine_drachen_laufen_nicht_unsichtbar(seite, heute_stand):
    """Bis zum 19.10.2026 lief der kleine Drache des Level-Tests (und schon
    vorher der der Lektion) nach Abbruch und Ergebnis unsichtbar in Schleife
    weiter: #lesson und #test sind keine Ansichten im Sinne von zmajRuht().
    Jetzt baut showLevelHome() beide ab, die Ergebnisschirme ihren eigenen."""
    seite.starten(stand=heute_stand())
    if not seite.js("() => hasLottie()"):
        pytest.skip("ohne lottie laeuft kein Drache")

    def starten(js, drache):
        seite.js(js)
        seite.page.wait_for_function(GELADEN, arg=drache, timeout=15000)
        assert seite.js(UNSICHTBAR) == [], "schon beim Start: " + drache

    def pruefen(wann, reste=0):
        seite.page.wait_for_timeout(150)
        assert seite.js(UNSICHTBAR) == [], "laeuft unsichtbar weiter nach: " + wann
        assert seite.js(RESTE) == reste, "kleiner Drache nicht abgebaut nach: " + wann

    # Lektion und Test abbrechen (tQuit und lQuit fuehren ohne Nachfrage
    # genau hierher)
    starten("() => { openLevel(0); startLesson(); }", "zmajLesson")
    seite.js("() => showLevelHome()")
    pruefen("Lektion abgebrochen")
    starten("() => { CATEGORIES[0].words.forEach(x => known.add(x.id)); startTest(); }", "zmajTest")
    seite.js("() => showLevelHome()")
    pruefen("Test abgebrochen")

    # Test bis zum Ergebnis, dann zur Uebersicht
    starten("() => startTest()", "zmajTest")
    seite.durchspielen("tBody", "Tx")
    seite.page.wait_for_function("() => !!document.querySelector('#tBody .result-big')")
    pruefen("Testergebnis")
    seite.js("() => showLevelHome()")
    pruefen("Testergebnis und Uebersicht")

    # Einstufung bis zum Ergebnis
    starten("() => { baueEinstufung('etwas'); einstufungStarten(); }", "zmajEinst")
    seite.js("() => einstufungEnde()")
    pruefen("Einstufungsergebnis")
    assert seite.fehler == [], seite.fehler
