# -*- coding: utf-8 -*-
"""Doppeltipp nach einer neu gezeichneten Aufgabe (20.11.2026, Optimierung Punkt 1).

Gegenprobe vom 20.11.2026 (Release/Optimierung_2026-11-20/geprueft_bedienung.md):
Doppeltipp per Touch auf die LETZTE Wortkarte. Weiter zeichnet sofort die erste
echte Aufgabe, und der zweite Tipp traf dort eine Antwort. In 2 von 9 Laeufen
(150 und 250 ms Abstand) war das eine falsche Antwort und ein Leben weg, obwohl
die Frage nie zu sehen war.

Seitdem nimmt ein Aufgabenfeld FRISCH_MS (300 ms) nach dem Zeichnen keinen echten
Tipp an (aufgaben.js, vor renderTask). Geprueft mit echten Tipps
(touchscreen.tap), in Chromium und - wenn Playwright es hat - in WebKit:

- letzte Wortkarte -> erste Aufgabe, zweiter Tipp nach 90, 150 und 250 ms auf
  eine falsche Antwort: keine Antwort, kein Leben weg
- Wortkarte -> Wortkarte: die zweite Karte wird nicht uebersprungen
- Weiter nach einer Antwort -> naechste Aufgabe: ebenso
- danach geht ein Tipp wie immer, Klicks per Skript (Testhelfer) und die
  Tastatur sofort

Zum Gegencheck ohne die Sperre: FRISCH_MS in web/js/aufgaben.js auf 0 setzen,
dann scheitern die Doppeltipp-Tests hier.
"""
import time

import pytest
from conftest import Seite

MOTOREN = ["chromium", "webkit"]

# Vier kurze Woerter mit eigener Bedeutung (wie in test_heller_knopf.py): mit
# ihnen als Vorrat hat jede Auswahl dieselben vier Knoepfe.
KURZ = r"""
() => {
  const raus = /[\/()]/;
  const out = [], bed = new Set();
  for(const w of CATEGORIES[0].words){
    if(w.bs.length > 8 || w.de.length > 10 || raus.test(w.bs + w.de)) continue;
    const b = _bedeutung(w.de);
    if(bed.has(b) || out.some(x => geschwister(x).some(g => g.bs === w.bs))) continue;
    bed.add(b); out.push(w);
    if(out.length === 4) break;
  }
  window.__kurz = out;
  return out.map(w => w.bs);
}
"""

# Jeder echte Klick mit Zeitstempel - als Skript vor der App, damit dieser
# Horcher vor der Sperre der App laeuft und auch abgewiesene Klicks sieht.
# i: welche Aufgabe stand, als der Klick ankam.
KLICKS_MITSCHREIBEN = r"""
window.__klicks = [];
window.addEventListener('click', e => {
  if(e.isTrusted) window.__klicks.push({zeit: e.timeStamp, detail: e.detail,
                                        i: typeof Lx !== 'undefined' && Lx ? Lx.i : null});
}, true);
"""

# Die Lektion mit einer festen Reihe starten; queue: Liste von [typ, wortnummer].
LEKTION = r"""
async (reihe) => {
  const warte = ms => new Promise(r => setTimeout(r, ms));
  lives = {anzahl: LEBEN_MAX, zeit: Date.now()};     // jeder Versuch mit vollen Leben
  openLevel(0); await warte(300); startLesson(); await warte(300);
  const k = window.__kurz;
  Lx.queue = reihe.map(([typ, n]) => ({typ, w: k[n], pool: k}));
  Lx.i = 0; Lx.total = Lx.queue.filter(q => q.typ !== 'intro').length;
  showLessonTask(); await warte(400);
}
"""

# Mitte eines Knopfs: der richtigen oder einer falschen Antwort, oder von Weiter.
MITTE = r"""
([sel, text, falsch]) => {
  const alle = [...document.querySelectorAll(sel)];
  const b = text === null ? alle[0] : alle.find(o => falsch ? o.textContent !== text : o.textContent === text);
  if(!b) return null;
  const r = b.getBoundingClientRect();
  return {x: r.x + r.width / 2, y: r.y + r.height / 2, t: b.textContent};
}
"""

STAND = "() => ({i: Lx.i, leben: livesNow(), erg: Lx.results.slice(), rechts: Lx.right," \
        " weiterbox: !!document.querySelector('#lBody .weiterbox'), fb: (document.querySelector('#lBody #xFb') || {}).className || ''})"


@pytest.fixture(params=MOTOREN)
def motor(request, browser):
    """Chromium immer, WebKit nur wenn da (siehe conftest.py, webkit)."""
    return browser if request.param == "chromium" else request.getfixturevalue("webkit")


@pytest.fixture
def handy(motor, basis, heute_stand):
    ctx = motor.new_context(viewport={"width": 360, "height": 640}, device_scale_factor=2,
                            has_touch=True, is_mobile=True, locale="de-DE", service_workers="block")
    ctx.add_init_script(KLICKS_MITSCHREIBEN)
    s = Seite(ctx.new_page(), basis)
    s.starten(stand=heute_stand())
    s.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
    s.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    assert len(s.js(KURZ)) == 4
    yield s
    ctx.close()


def _mitte(s, sel, text=None, falsch=False):
    m = s.js(MITTE, [sel, text, falsch])
    assert m, "nichts gefunden: %s %r" % (sel, text)
    return m


def _doppeltipp(s, erster, zweiter_sel, abstand_ms, text=None, falsch=False, neu_i=None):
    """Erster Tipp auf erster (x, y); sobald die neue Aufgabe steht, der zweite
    abstand_ms nach dem ersten auf die Mitte von zweiter_sel. Gibt den
    gemessenen Abstand der beiden Klicks zurueck (Zeitstempel im Browser).
    Ein Tipp braucht vom Aufruf bis zum Klick im Browser einige zehn ms; das
    wird am ersten gemessen und beim zweiten abgezogen."""
    vorher = len(s.js("() => window.__klicks"))
    start = s.js("() => performance.now()")
    s.page.touchscreen.tap(erster[0], erster[1])
    s.page.wait_for_function("(i) => document.getElementById('lBody').dataset.i === String(i)",
                             arg=neu_i, polling=5, timeout=4000)
    ziel = _mitte(s, zweiter_sel, text, falsch)
    lage = s.js("(n) => ({jetzt: performance.now(), klick: window.__klicks[n].zeit})", vorher)
    weg = time.monotonic()
    verzug = lage["klick"] - start                    # Aufruf bis Klick, samt einer Rueckfahrt
    rest = (abstand_ms - (lage["jetzt"] - lage["klick"]) - verzug) / 1000.0 - (time.monotonic() - weg)
    if rest > 0:
        time.sleep(rest)
    s.page.touchscreen.tap(ziel["x"], ziel["y"])
    s.page.wait_for_function("(n) => window.__klicks.length >= n", arg=vorher + 2, timeout=4000)
    k = s.js("() => window.__klicks")[vorher:vorher + 2]
    assert all(x["detail"] > 0 for x in k), k
    return k[1]["zeit"] - k[0]["zeit"], ziel


def _in_der_sperrzeit(versuch, mal=4):
    """Gueltig ist ein Doppeltipp nur, wenn der zweite Tipp wirklich in der
    Sperrzeit kam (unter 300 ms nach dem ersten). Ein Tipp per Playwright
    braucht mal laenger, besonders in WebKit - dann ein neuer Versuch, mit
    frisch aufgebauter Lektion."""
    gemessen = []
    for _ in range(mal):
        g, rest = versuch()
        if g is None:                                 # zweiter Tipp kam vor der neuen Aufgabe an
            gemessen.append("zu frueh")
            continue
        if g < 298:
            return rest
        gemessen.append(round(g))
    pytest.fail("zweiter Tipp nie in der Sperrzeit (%s ms) - Messung ungueltig" % gemessen)


def _ohne_fehler(s):
    assert s.fehler == [], s.fehler
    assert s.fremd == [], s.fremd


@pytest.mark.parametrize("abstand", [90, 150, 250])
def test_doppeltipp_nach_letzter_wortkarte_kostet_kein_leben(handy, abstand):
    """Der Fall aus der Gegenprobe: Doppeltipp auf Weiter der letzten Wortkarte.
    Der zweite Tipp trifft eine FALSCHE Antwort der ersten Aufgabe - ohne Sperre
    ist das eine Antwort und ein Leben weg."""
    s = handy

    def versuch():
        s.js(LEKTION, [["intro", 0], ["intro", 1], ["mc", 0], ["mc", 1]])
        s.js("() => document.querySelector('#lBody #xNext').click()")        # erste Karte per Skript
        s.page.wait_for_function("() => document.getElementById('lBody').dataset.i === '1'", timeout=4000)
        s.page.wait_for_timeout(400)
        vor = s.js(STAND)
        assert vor["i"] == 1 and vor["leben"] == 5, vor
        weiter = _mitte(s, "#lBody #xNext")
        soll = s.js("() => Lx.queue[2].w.bs")
        gemessen, ziel = _doppeltipp(s, (weiter["x"], weiter["y"]), "#lBody .opt", abstand,
                                     text=soll, falsch=True, neu_i=2)
        assert ziel["t"] != soll
        return gemessen, soll

    soll = _in_der_sperrzeit(versuch)
    s.page.wait_for_timeout(500)
    nach = s.js(STAND)
    assert nach["i"] == 2, nach                       # erste Aufgabe steht noch, unbeantwortet
    assert nach["leben"] == 5, nach                   # kein Leben weg
    assert nach["erg"] == ["intro", "intro"], nach    # nichts beantwortet
    assert not nach["weiterbox"] and "no" not in nach["fb"].split(), nach
    assert s.js("() => [...document.querySelectorAll('#lBody .opt')].every(o => !o.disabled)")
    # Danach zaehlt ein Tipp wieder wie immer: die richtige Antwort.
    richtig = _mitte(s, "#lBody .opt", soll)
    s.page.touchscreen.tap(richtig["x"], richtig["y"])
    s.page.wait_for_function("() => !!document.querySelector('#lBody .weiterbox')", timeout=4000)
    fertig = s.js(STAND)
    assert fertig["erg"] == ["intro", "intro", True] and fertig["rechts"] == 1 and fertig["leben"] == 5, fertig
    _ohne_fehler(s)


def test_doppeltipp_ueberspringt_keine_wortkarte(handy):
    """Wortkarte -> Wortkarte: Weiter liegt an derselben Stelle. Ohne Sperre zog
    der zweite Tipp die zweite Karte ungesehen vorbei (16 von 16 in der Suche).
    Weil Weiter an derselben Stelle bleibt, kommen beide Tipps direkt
    hintereinander, ohne Warten und Nachmessen dazwischen. Ueber _doppeltipp
    lag der zweite Tipp in WebKit immer 360-480 ms nach dem ersten und damit
    hinter der Sperre (Pruefung vom 20.11.2026)."""
    s = handy

    def versuch():
        s.js(LEKTION, [["intro", 0], ["intro", 1], ["intro", 2], ["mc", 0]])
        weiter = _mitte(s, "#lBody #xNext")
        vorher = len(s.js("() => window.__klicks"))
        s.page.touchscreen.tap(weiter["x"], weiter["y"])
        s.page.touchscreen.tap(weiter["x"], weiter["y"])
        s.page.wait_for_function("(n) => window.__klicks.length >= n", arg=vorher + 2, timeout=4000)
        k = s.js("() => window.__klicks")[vorher:vorher + 2]
        assert all(x["detail"] > 0 for x in k), k
        assert k[0]["i"] == 0, k
        if k[1]["i"] != 1:                            # zweite Karte stand noch nicht
            return None, None
        return k[1]["zeit"] - k[0]["zeit"], None

    _in_der_sperrzeit(versuch)
    s.page.wait_for_timeout(500)
    nach = s.js(STAND)
    assert nach["i"] == 1 and nach["erg"] == ["intro"], nach
    assert s.js("() => document.querySelector('#lBody .big').textContent") == s.js("() => window.__kurz[1].bs")
    _ohne_fehler(s)


def test_doppeltipp_auf_weiter_nach_einer_antwort(handy):
    """Jede neu gezeichnete Aufgabe, nicht nur nach Wortkarten: richtig antworten,
    nach der 900-ms-Sperre Weiter antippen und gleich noch einmal - der zweite
    Tipp auf eine falsche Antwort der naechsten Aufgabe zaehlt nicht."""
    s = handy

    def versuch():
        s.js(LEKTION, [["mc", 0], ["mc", 1], ["mc", 2]])
        soll = s.js("() => Lx.queue[0].w.bs")
        r = _mitte(s, "#lBody .opt", soll)
        s.page.touchscreen.tap(r["x"], r["y"])
        s.page.wait_for_function("() => !!document.querySelector('#lBody .weiterbox .btn')", timeout=4000)
        s.page.wait_for_timeout(1150)                 # WEITER_NACH (900 ms) bleibt, wie es war
        weiter = _mitte(s, "#lBody .weiterbox .btn")
        soll2 = s.js("() => Lx.queue[1].w.bs")
        return _doppeltipp(s, (weiter["x"], weiter["y"]), "#lBody .opt", 150, text=soll2, falsch=True, neu_i=1)

    _in_der_sperrzeit(versuch)
    s.page.wait_for_timeout(500)
    nach = s.js(STAND)
    assert nach["i"] == 1 and nach["erg"] == [True] and nach["leben"] == 5, nach
    assert not nach["weiterbox"], nach
    _ohne_fehler(s)


def test_nach_der_sperre_geht_ein_tipp(handy):
    """Wer nach gut 300 ms antippt, kommt durch: die Sperre ist kurz."""
    s = handy
    s.js(LEKTION, [["intro", 0], ["mc", 0], ["mc", 1]])
    weiter = _mitte(s, "#lBody #xNext")
    s.page.touchscreen.tap(weiter["x"], weiter["y"])
    s.page.wait_for_function("() => document.getElementById('lBody').dataset.i === '1'", timeout=4000)
    s.page.wait_for_timeout(380)
    soll = s.js("() => Lx.queue[1].w.bs")
    falsch = _mitte(s, "#lBody .opt", soll, falsch=True)
    s.page.touchscreen.tap(falsch["x"], falsch["y"])
    s.page.wait_for_function("() => !!document.querySelector('#lBody .weiterbox')", timeout=4000)
    nach = s.js(STAND)
    assert nach["erg"] == ["intro", False] and nach["leben"] == 4, nach
    _ohne_fehler(s)


def test_skript_und_tastatur_bleiben_sofort(handy):
    """Klicks per Skript (wie DURCHSPIELEN in conftest.py) und Enter auf Weiter
    gelten sofort - die Sperre gilt nur fuer Tipps und Mausklicks."""
    s = handy
    s.js(LEKTION, [["intro", 0], ["intro", 1], ["intro", 2], ["intro", 3], ["mc", 0]])
    # Per Skript: zweimal Weiter ohne Pause.
    s.js("""() => { document.querySelector('#lBody #xNext').click();
                    document.querySelector('#lBody #xNext').click(); }""")
    assert s.js("() => Lx.i") == 2
    # Tastatur: Weiter hat den Fokus, zweimal Enter kurz hintereinander.
    assert s.js("() => document.activeElement === document.querySelector('#lBody #xNext')")
    s.page.keyboard.press("Enter")
    s.page.keyboard.press("Enter")
    s.page.wait_for_timeout(300)
    nach = s.js(STAND)
    assert nach["i"] == 4 and nach["erg"] == ["intro"] * 4, nach
    _ohne_fehler(s)


def test_ergebnis_gleich_nach_dem_ueberspringen_nimmt_den_tipp(handy):
    """Gesperrt ist nur, was die Aufgabe gezeichnet hat. Ueberspringen auf der
    letzten Aufgabe zeigt sofort das Ergebnis im selben Feld - ein Tipp dort
    gilt gleich, auch noch in den 300 ms nach dem Zeichnen der Aufgabe."""
    s = handy
    s.js(LEKTION, [["mc", 0], ["listen", 1]])
    soll = s.js("() => Lx.queue[0].w.bs")
    s.js("(soll) => [...document.querySelectorAll('#lBody .opt')].find(o => o.textContent === soll).click()", soll)
    s.page.wait_for_function("() => !!document.querySelector('#lBody .weiterbox .btn')", timeout=4000)
    s.page.wait_for_timeout(1150)
    # Weiter, die Hoeraufgabe kommt, und gleich ueberspringen - alles per Skript, ohne Pause.
    k = s.js("""() => { document.querySelector('#lBody .weiterbox .btn').click();
                        document.querySelector('#lBody #xSkip').click();
                        window.__gezaehlt = 0;
                        const k = document.querySelector('#lBody #lHome, #lBody #lMore');
                        k.addEventListener('click', () => { window.__gezaehlt++; }, true);
                        const r = k.getBoundingClientRect(), x = r.x + r.width / 2, y = r.y + r.height / 2;
                        return {x, y, bis: frisch.bis, unter: !!document.elementFromPoint(x, y).closest('#lHome, #lMore'),
                                klicks: window.__klicks.length}; }""")
    assert k["unter"], k
    s.page.touchscreen.tap(k["x"], k["y"])
    s.page.wait_for_function("(n) => window.__klicks.length > n", arg=k["klicks"], timeout=4000)
    assert s.js("() => window.__klicks[window.__klicks.length - 1].zeit") < k["bis"],         "der Tipp kam erst nach der Sperrzeit - Messung ungueltig"
    s.page.wait_for_timeout(200)
    assert s.js("() => window.__gezaehlt") == 1
    _ohne_fehler(s)
