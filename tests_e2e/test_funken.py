# -*- coding: utf-8 -*-
"""Funkenflug an der Serien-Flamme (24.10.2026).

Ajdin nach dem Test der gemalten Flamme: "kann man das feuer animieren so
das immer so kurze funken raus kommen". Aus der Vorschau mit drei Varianten
nahm er A, den Funkenflug: "nimm A aber fuer 365 tage da ist schon eine
shiny animation das waere dann zu viel". Also:
  - vier kleine Funken (.fk) steigen staendig aus der brennenden Flamme auf
    - bei orange (unter 30), blau (ab 30) und lila (ab 100), in der Farbe
    der Stufe
  - keine bei Gold (ab 365): dort funkeln schon die drei Sterne (.funke)
  - keine bei Glut, bei kalter Kohle, waehrend des Aufbaus (erst danach),
    mit dem Schalter "Animationen" aus und mit "Bewegung reduzieren" - und
    dann auch keine im Kasten: angelegt werden sie nur, wenn sie fliegen
  - ueberall gleich: oben auf der Startseite und in der Statistik am Ende
    einer Lektion und einer Wiederholungsrunde (flammeHtml/funkenRichten)
  - sie verschieben nichts, verdecken die Ziffern nicht, fliegen nicht in
    die Kopfleiste und machen die Seite nicht breiter - auch bei 320 px und
    130 / 200 % Schrift
  - bewegt werden nur transform und opacity; neu gewuerfelt werden nur
    Startpunkt, Flugweite, Schlaengeln und Groesse, nur bei
    animationiteration, und eine neue Runde beginnt am Anfang des Flugs,
    nicht mittendrin. Dauer und Verzoegerung bleiben je Funke fest: so sind
    nach dem Laden, den Einstellungen oder einer Lektion alle vier gleich
    wieder da
  - kein Zeitgeber, der dauernd laeuft, und kein Zufall beim Zeichnen

Jeder Test hier ist gegen den Stand vor dem Funkenflug rot: auch die Tests
fuer "keine Funken" sehen erst Funken fliegen und pruefen dann, dass sie
weg sind. Hilfen und Ablauf wie in test_flamme.py (Geraetemodus, Bewegung
immer ausdruecklich gesetzt, Uhr fuer die langen Serien vorgestellt).
"""
import datetime
import json

import pytest
from test_flamme import (ERSTE_LEKTION, FERTIG, LAGE, SCHRIFT, SPAETER, TOPF_ENDE, _kontext, _serie_starten,
                         _serie_tage, _vorspann_weg)

# Die Farbe der Stufe, abzulesen am Schein (box-shadow in --sp2)
FARBE = {"": "rgb(255, 90, 10)", "blau": "rgb(30, 123, 255)", "lila": "rgb(148, 64, 255)"}
OBEN = ".seriezahl .flammenbox"
STAT = "#lBody .stat .flammenbox"

# Die Funken in einem Kasten: wie sie gesetzt sind, was laeuft, welche
# Eigenschaften die Keyframes bewegen, und die Deckkraft bei 25 % des Flugs
# (dort ist ein Funke ganz da).
FUNKEN = """(wo) => { const box = document.querySelector(wo);
  return [...box.querySelectorAll('.fk')].map(x => { const s = getComputedStyle(x), an = x.getAnimations();
    let voll = null, props = [];
    if(an.length){ const a = an[0], t = a.effect.getComputedTiming();
      props = [...new Set(a.effect.getKeyframes().flatMap(k => Object.keys(k)))]
        .filter(k => !['offset', 'computedOffset', 'easing', 'composite'].includes(k)).sort();
      let t0 = t.delay; while(t0 < 0) t0 += t.duration;
      const vorher = a.currentTime; a.pause(); a.currentTime = t0 + 0.25 * t.duration;
      voll = getComputedStyle(x).opacity; a.currentTime = vorher; a.play(); }
    return {pos: s.position, zeiger: s.pointerEvents, text: x.textContent, versteckt: x.closest('[aria-hidden="true"]') === box,
            eltern: x.parentElement === box, name: s.animationName, opacity: s.opacity, schein: s.boxShadow.split(') ')[0] + ')',
            laufend: an.map(a => a.animationName + ':' + a.playState), props, voll}; }); }"""

ANZAHL = "(wo) => { const b = document.querySelector(wo); return b ? b.querySelectorAll('.fk').length : null; }"

# Zufall mit Saat: Math.random der Seite durch mulberry32 ersetzt - die
# Funken wuerfeln dann jedes Mal gleich, und ein Fund laesst sich wiederholen.
SAAT = """(saat) => { let s = saat >>> 0;
  Math.random = () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }"""

# Wo die Funken hinfliegen. Jeder Funke wird angehalten und auf viele
# Zeitpunkte seines Flugs gestellt (Anteile in "zeiten"), mit
#   - allen Ecken der Bereiche (jede Kombination der Grenzen von x, y, dx,
#     dy und wk, groesster Funke) und
#   - "runden" Runden, wie die App sie wuerfelt (funkeWuerfeln, mit Saat).
# Gemessen wird der Kasten des Funkens (getBoundingClientRect, samt
# transform) gegen
#   - die Ziffern: oben #serieZahl, in der Statistik der Text hinter dem
#     Kasten (ein Range ab der ersten Ziffer) - ganzer Zeilenkasten, also
#     eher zu streng,
#   - die Kopfleiste: header und alles Sichtbare darin (bei 200 % ragt das
#     Herz unten aus dem header heraus),
#   - den Rand des Fensters.
# Zurueck kommen die schlimmsten Werte.
FLUGBAHN = """([wo, zeiten, runden]) => {
  const box = document.querySelector(wo), fks = [...box.querySelectorAll('.fk')], B = FUNKEN_BEREICH;
  const zr = (() => { if(box.closest('.seriezahl')) return document.getElementById('serieZahl').getBoundingClientRect();
    const tn = [...box.parentElement.childNodes].find(n => n.nodeType === 3 && /[0-9]/.test(n.textContent));
    const r = document.createRange(); r.setStart(tn, tn.textContent.search(/[0-9]/)); r.setEnd(tn, tn.textContent.trimEnd().length);
    return r.getBoundingClientRect(); })();
  const kopf = document.querySelector('header');
  const kopfUnten = Math.max(...[kopf, ...kopf.querySelectorAll('*')].map(e => e.getBoundingClientRect())
    .filter(r => r.width > 0 && r.height > 0).map(r => r.bottom));
  const breite = document.documentElement.clientWidth;
  const aus = {proben: 0, sichtbar: 0, ueberZiffern: 0, tiefsterUeberlapp: -1e9, hoechsterFunke: 1e9, links: 1e9, rechts: -1e9,
               rechtsVonZiffern: -1e9, kopfUnten, ziffern: [zr.left, zr.top, zr.right, zr.bottom], boxOben: box.getBoundingClientRect().top};
  const messen = fk => { const a = fk.getAnimations()[0]; a.pause(); getComputedStyle(fk).transform;
    const t = a.effect.getComputedTiming(); let t0 = t.delay; while(t0 < 0) t0 += t.duration;
    for(const p of zeiten){ a.currentTime = t0 + p * t.duration;
      const r = fk.getBoundingClientRect(), o = parseFloat(getComputedStyle(fk).opacity);
      aus.proben++; if(o > 0.01) aus.sichtbar++;
      aus.hoechsterFunke = Math.min(aus.hoechsterFunke, r.top);
      aus.links = Math.min(aus.links, r.left); aus.rechts = Math.max(aus.rechts, r.right);
      // Ueberlappen mit den Ziffern: wie tief der Funke von oben hineinreicht
      if(r.right > zr.left && r.left < zr.right && r.bottom > zr.top && r.top < zr.bottom){
        aus.ueberZiffern++; aus.tiefsterUeberlapp = Math.max(aus.tiefsterUeberlapp, r.bottom - zr.top); }
      aus.rechtsVonZiffern = Math.max(aus.rechtsVonZiffern, r.right - zr.left); }
    a.play(); };
  const keys = ['x', 'y', 'dx', 'dy', 'wk'];
  for(let m = 0; m < 32; m++){ const fk = fks[0];
    keys.forEach((k, i) => fk.style.setProperty('--' + k, String(B[k][(m >> i) & 1])));
    fk.style.setProperty('--g', String(B.g[1])); messen(fk); }
  for(let n = 0; n < runden; n++) for(const fk of fks){ funkeWuerfeln(fk, 0); messen(fk); }
  return aus; }"""

# Waehrend die Funken frei fliegen: alle 40 ms alle Kaesten, ueber ms
# Millisekunden - mit dem Wuerfeln der App bei jeder Runde.
FREIFLUG = """async ([wo, ms]) => { const box = document.querySelector(wo);
  const zr = document.getElementById('serieZahl').getBoundingClientRect(), kopf = document.querySelector('header');
  const kopfUnten = Math.max(...[kopf, ...kopf.querySelectorAll('*')].map(e => e.getBoundingClientRect())
    .filter(r => r.width > 0 && r.height > 0).map(r => r.bottom));
  const aus = {bilder: 0, sichtbar: 0, ueberZiffern: 0, hoechsterFunke: 1e9, rechts: -1e9, runden: 0, kopfUnten,
               zifferLinks: zr.left, breite: document.documentElement.clientWidth, scroll: 0};
  const zaehle = e => { if(e.animationName === 'flammeFlug') aus.runden++; };
  document.addEventListener('animationiteration', zaehle);
  const ende = performance.now() + ms;
  while(performance.now() < ende){
    await new Promise(r => setTimeout(r, 40)); aus.bilder++;
    for(const fk of box.querySelectorAll('.fk')){ const r = fk.getBoundingClientRect();
      if(parseFloat(getComputedStyle(fk).opacity) > 0.01) aus.sichtbar++;
      aus.hoechsterFunke = Math.min(aus.hoechsterFunke, r.top); aus.rechts = Math.max(aus.rechts, r.right);
      if(r.right > zr.left && r.left < zr.right && r.bottom > zr.top + 1 && r.top < zr.bottom) aus.ueberZiffern++; }
    aus.scroll = Math.max(aus.scroll, document.documentElement.scrollWidth - document.documentElement.clientWidth); }
  document.removeEventListener('animationiteration', zaehle);
  return aus; }"""


def _naechster_tag(seite):
    """Die Uhr einen Tag weiter (wie nach Mitternacht), Mittag."""
    seite.page.clock.set_fixed_time(datetime.datetime.combine(SPAETER + datetime.timedelta(days=1),
                                                              datetime.time(12, 0)))


def _fliegen(seite, wo, stufe):
    """Vier Funken im Kasten wo: absolut gesetzt, ohne Zeiger, im Kasten mit
    aria-hidden, ohne Text; flammeFlug laeuft, bewegt nur transform und
    opacity, ist bei 25 % ganz da, und der Schein hat die Farbe der Stufe."""
    funken = seite.js(FUNKEN, wo)
    assert len(funken) == 4, funken
    for x in funken:
        assert x["pos"] == "absolute" and x["zeiger"] == "none" and x["text"] == "", x
        assert x["versteckt"] and x["eltern"], x
        assert x["laufend"] == ["flammeFlug:running"] and x["props"] == ["opacity", "transform"], x
        assert x["voll"] == "1" and x["schein"] == FARBE[stufe], x
    return funken


# ---------------------------------------------------------------------------
# Wo es Funken gibt
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tage,stufe", [(5, ""), (30, "blau"), (100, "lila")])
def test_funken_fliegen_oben(browser, basis, tage, stufe):
    """Startseite, brennende Flamme: vier Funken in der Farbe der Stufe,
    gleich beim Start (kein Aufbau). Ein neues Zeichnen der Startseite
    laesst sie fliegen, wie sie sind - dieselben Funken, kein Neubeginn."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, tage, "an")
        _vorspann_weg(seite)
        assert seite.js("() => document.getElementById('serieFlamme').className").split() == \
            ["flamme"] + (["stufe-" + stufe] if stufe else [])
        _fliegen(seite, OBEN, stufe)
        seite.js("() => { window._fk = [...document.querySelectorAll('.seriezahl .fk')]; showHome(); showHome(); }")
        assert seite.js("() => window._fk.every((x, i) => x === document.querySelectorAll('.seriezahl .fk')[i])")
        assert seite.js(ANZAHL, OBEN) == 4
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


def test_funken_in_der_statistik_am_lektionsende(browser, basis, heute_stand):
    """Eine echte Lektion macht aus 4 Tagen Glut 5 Tage Flamme: die
    Statistik zeigt die orange Flamme mit ihren vier Funken - dieselben wie
    oben (flammeHtml). Zurueck auf der Startseite baut sich die Flamme auf,
    waehrenddessen ohne Funken; danach fliegen sie dort auch."""
    ctx, seite = _kontext(browser, basis)
    try:
        seite.starten(stand=heute_stand(tage=_serie_tage(4, "glut")))
        assert seite.js(ANZAHL, OBEN) == 0
        seite.js("() => { openLevel(0); startLesson(); }")
        seite.durchspielen("lBody", "Lx")
        _fliegen(seite, STAT, "")
        seite.js("() => document.getElementById('lPfad').click()")
        assert seite.js("() => document.getElementById('serieFlamme').classList.contains('auf')")
        assert seite.js(ANZAHL, OBEN) == 0
        seite.page.wait_for_function(FERTIG, timeout=4000)
        _fliegen(seite, OBEN, "")
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


@pytest.mark.parametrize("tage,stufe", [(29, "blau"), (99, "lila")])
def test_funken_in_der_statistik_der_wiederholungsrunde(browser, basis, tage, stufe):
    """Das Ende einer Wiederholungsrunde macht aus der Glut die Flamme der
    naechsten Stufe (29 -> 30 blau, 99 -> 100 lila): Funken in deren Farbe,
    in der Statistik und danach oben."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, tage, "glut")
        assert seite.js(ANZAHL, OBEN) == 0
        seite.js(TOPF_ENDE)
        _fliegen(seite, STAT, stufe)
        seite.js("() => showHome()")
        seite.page.wait_for_function(FERTIG, timeout=4000)
        _fliegen(seite, OBEN, stufe)
        assert seite.fehler == []
    finally:
        ctx.close()


def test_erst_nach_dem_aufbau(browser, basis):
    """99 Tage Glut (blau), die erste Lektion des Tages macht 100 (lila): die
    Flamme baut sich auf, und solange sie das tut, gibt es keine Funken -
    auch nicht, wenn die Startseite mittendrin neu gezeichnet wird. Erst
    danach setzen sie ein, gleich in Lila."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, 99, "glut")
        _vorspann_weg(seite)
        assert seite.js(ANZAHL, OBEN) == 0
        nachher = seite.js(ERSTE_LEKTION)
        assert nachher["klasse"].split() == ["flamme", "stufe-lila", "auf"], nachher
        assert seite.js(ANZAHL, OBEN) == 0
        seite.page.wait_for_timeout(600)
        seite.js("() => showHome()")
        assert seite.js("() => document.getElementById('serieFlamme').classList.contains('auf')")
        assert seite.js(ANZAHL, OBEN) == 0
        seite.page.wait_for_function(FERTIG, timeout=4000)
        _fliegen(seite, OBEN, "lila")
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Wo es keine gibt - jeweils erst mit Funken, dann ohne
# ---------------------------------------------------------------------------

def test_keine_funken_bei_gold(browser, basis):
    """364 Tage brennend (lila): Funken. Am naechsten Tag macht die
    Wiederholungsrunde 365 - Gold. In der Statistik und oben (nach dem
    Aufbau) keine Funken, dafuer funkeln die drei Sterne wie bisher."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, 364, "an")
        _vorspann_weg(seite)
        _fliegen(seite, OBEN, "lila")
        _naechster_tag(seite)
        seite.js(TOPF_ENDE)
        assert seite.js("() => document.querySelector('#lBody .stat .flamme').className") == "flamme stufe-gold"
        assert seite.js(ANZAHL, STAT) == 0
        assert seite.js("() => [...document.querySelectorAll('#lBody .stat .funke')].map(x => x.getAnimations()"
                        ".map(a => a.animationName).join())") == ["flammeFunke"] * 3
        seite.js("() => showHome()")
        seite.page.wait_for_function(FERTIG, timeout=4000)
        assert seite.js("() => document.getElementById('serieFlamme').className") == "flamme stufe-gold"
        assert seite.js(ANZAHL, OBEN) == 0
        assert seite.js("() => [...document.querySelectorAll('.seriezahl .funke')].map(x => x.getAnimations()"
                        ".map(a => a.animationName).join())") == ["flammeFunke"] * 3
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("zustand", ["glut", "aus"])
def test_keine_funken_bei_glut_und_kohle(browser, basis, zustand):
    """Brennend mit Funken; dann ist der Lerntag vorbei (glut: die Uhr steht
    am naechsten Tag, die Serie laeuft noch) bzw. es gab nur heute
    (aus: heute wieder weg, Serie 0). Beim naechsten Zeichnen sind die
    Funken aus dem Kasten verschwunden, nicht nur unsichtbar."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, 30 if zustand == "glut" else 1, "an")
        _vorspann_weg(seite)
        _fliegen(seite, OBEN, "blau" if zustand == "glut" else "")
        if zustand == "glut":
            _naechster_tag(seite)
        else:
            seite.js("() => days.delete(today())")
        seite.js("() => showHome()")
        assert seite.js("() => document.getElementById('serieFlamme').className").split()[:2] == ["flamme", zustand]
        assert seite.js(ANZAHL, OBEN) == 0
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("weg", ["schalter", "geraet"])
def test_keine_funken_ohne_bewegung(browser, basis, weg):
    """30 Tage brennend: Funken. Dann der Schalter "Animationen" aus bzw.
    "Bewegung reduzieren" am Geraet: sofort laeuft keine Animation mehr und
    jeder Funke ist unsichtbar; beim naechsten Zeichnen sind sie weg, und
    auch die Statistik einer Wiederholungsrunde baut keine. Wieder an:
    beim naechsten Zeichnen fliegen sie wieder."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, 30, "an")
        _vorspann_weg(seite)
        _fliegen(seite, OBEN, "blau")
        if weg == "schalter":
            seite.js("() => document.getElementById('swAnim').click()")
            assert seite.js("() => document.body.classList.contains('no-anim')")
        else:
            seite.page.emulate_media(reduced_motion="reduce")
        funken = seite.js(FUNKEN, OBEN)
        assert len(funken) == 4 and all(x["laufend"] == [] and x["opacity"] == "0" for x in funken), funken
        seite.js("() => showHome()")
        assert seite.js(ANZAHL, OBEN) == 0
        seite.js(TOPF_ENDE)
        assert seite.js("() => document.querySelector('#lBody .stat .flamme').className") == "flamme stufe-blau"
        assert seite.js(ANZAHL, STAT) == 0
        if weg == "schalter":
            seite.js("() => document.getElementById('swAnim').click()")
        else:
            seite.page.emulate_media(reduced_motion="no-preference")
        seite.js("() => showHome()")
        _fliegen(seite, OBEN, "blau")
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Neue Runde: neu gewuerfelt, aber vom Anfang des Flugs an
# ---------------------------------------------------------------------------

def test_neue_runde_beginnt_am_anfang(browser, basis):
    """Bei jeder Runde (animationiteration) wuerfelt der Funke Startpunkt,
    Flugweite, Schlaengeln und Groesse neu, in den Bereichen der Vorschau.
    Dauer und Verzoegerung bleiben die aus FUNKEN_ERSTE - auch die Vorschau
    wuerfelt die Dauer nur einmal je Funke. Direkt nach dem Wechsel steht
    er am Anfang seines Flugs (unter 6 % seiner Dauer), und jeder Funke
    zaehlt seine Runden ohne Doppel weiter. Dasselbe von Hand nach Runde 1,
    7, 500 und 5000 (angehalten, 5 ms nach dem Rundenwechsel): Das Wuerfeln
    laesst den Funken in seiner Runde und an seiner Stelle im Flug."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, 30, "an")
        _vorspann_weg(seite)
        assert seite.js(ANZAHL, OBEN) == 4
        runden = seite.js("""async () => { const aus = [], fks = [...document.querySelectorAll('.seriezahl .fk')];
            const merke = e => { if(e.animationName !== 'flammeFlug') return;
              const x = e.target, s = x.style, a = x.getAnimations()[0]; getComputedStyle(x).transform;
              const t = a.effect.getComputedTiming();
              aus.push({i: fks.indexOf(x), fortschritt: t.progress, runde: t.currentIteration,
                        werte: Object.fromEntries(['dauer', 'warte', 'x', 'y', 'dx', 'dy', 'wk', 'g']
                          .map(k => [k, parseFloat(s.getPropertyValue('--' + k))]))}); };
            document.addEventListener('animationiteration', merke);
            await new Promise(r => setTimeout(r, 6000));
            document.removeEventListener('animationiteration', merke); return aus; }""")
        bereich = seite.js("() => FUNKEN_BEREICH")
        erste = seite.js("() => FUNKEN_ERSTE")
        von_hand = seite.js("""() => { const fk = document.querySelector('.seriezahl .fk'), a = fk.getAnimations()[0], aus = [];
            a.pause();
            for(const k of [1, 7, 500, 5000]){ getComputedStyle(fk).transform; const t = a.effect.getComputedTiming();
              let t0 = t.delay; while(t0 + k * t.duration < 0) t0 += t.duration;
              a.currentTime = t0 + k * t.duration + 5;
              const runde = a.effect.getComputedTiming().currentIteration;
              funkeWuerfeln(fk);
              getComputedStyle(fk).transform; const u = a.effect.getComputedTiming();
              aus.push({k, runde, danach: u.currentIteration, ms: u.progress * u.duration}); }
            a.play(); return aus; }""")
    finally:
        ctx.close()
    assert sorted(bereich) == ["dx", "dy", "g", "wk", "x", "y"], bereich
    assert len(runden) >= 8 and {r["i"] for r in runden} == {0, 1, 2, 3}, runden
    for r in runden:
        assert 0 <= r["fortschritt"] < 0.06, r
        assert (r["werte"]["dauer"], r["werte"]["warte"]) == (erste[r["i"]]["dauer"], erste[r["i"]]["warte"]), r
        for k, (unten, oben) in bereich.items():
            assert unten - 0.001 <= r["werte"][k] <= oben + 0.001, (k, r)
    for i in range(4):
        folge = [r["runde"] for r in runden if r["i"] == i]
        assert all(b > a for a, b in zip(folge, folge[1:])), (i, folge)
    for h in von_hand:
        assert h["danach"] == h["runde"] and 4.99 <= h["ms"] < 6.5, von_hand
    print("Runden", len(runden), json.dumps([round(r["fortschritt"], 3) for r in runden]), json.dumps(von_hand))


# ---------------------------------------------------------------------------
# Lage: nichts verschoben, nichts verdeckt, nicht in der Kopfleiste
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("breite", [360, 320])
def test_funken_verschieben_nichts(browser, basis, breite):
    """Bei 100, 130 und 200 % Schrift: alle Kaesten oben stehen mit
    fliegenden Funken genau da, wo sie ohne stuenden, und die Seite wird
    nicht breiter."""
    ctx, seite = _kontext(browser, basis)
    seite.page.set_viewport_size({"width": breite, "height": 640})
    funde = {}
    try:
        _serie_starten(seite, 30, "an")
        _vorspann_weg(seite)
        groesse = 1.0
        for faktor in (1.0, 1.3, 2.0):
            if faktor != groesse:
                seite.js(SCHRIFT, faktor / groesse)
                groesse = faktor
            assert seite.js(ANZAHL, OBEN) == 4
            mit = seite.js(LAGE)
            seite.js("() => document.querySelectorAll('.seriezahl .fk').forEach(x => x.style.display = 'none')")
            ohne = seite.js(LAGE)
            seite.js("() => document.querySelectorAll('.seriezahl .fk').forEach(x => x.style.display = '')")
            assert mit == ohne, (faktor, mit, ohne)
            assert seite.js("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth")
            funde[faktor] = mit
        assert seite.fehler == []
    finally:
        ctx.close()
    print("Lage", breite, json.dumps({k: v[".flammenbox"] for k, v in funde.items()}))


# Zeitpunkte im Flug: Anfang, Einblenden, der Bogen bei 45 %, das Verglimmen
ZEITEN = [0, 0.04, 0.08, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92, 0.97, 0.999]


def _flugbahn_pruefen(m, mit_kopf):
    """Die Funken verdecken die Ziffern nicht (hoechstens 1 px am oberen
    Rand des Zeilenkastens), bleiben unter der Kopfleiste und im Fenster."""
    assert m["proben"] >= 32 * len(ZEITEN) and m["sichtbar"] > m["proben"] // 2, m
    assert m["ueberZiffern"] == 0 or m["tiefsterUeberlapp"] <= 1, m
    if mit_kopf:
        assert m["hoechsterFunke"] >= m["kopfUnten"], m
    assert m["links"] >= 0 and m["rechts"] <= m.get("breite", 1e9), m


@pytest.mark.parametrize("breite", [360, 320])
def test_flugbahn_oben(browser, basis, breite):
    """Oben auf der Startseite, bei 100, 130 und 200 % Schrift: Jeder Funke
    an 14 Zeitpunkten seines Flugs, mit allen Ecken der Bereiche und 25
    gewuerfelten Runden je Funke (feste Saat) - kein Kasten schneidet die
    Ziffern, keiner reicht in die Kopfleiste (Herz, Muenzen, Laden), keiner
    aus dem Fenster. Dazu 4 s freier Flug mit dem Wuerfeln der App."""
    ctx, seite = _kontext(browser, basis)
    seite.page.set_viewport_size({"width": breite, "height": 640})
    funde = {}
    try:
        _serie_starten(seite, 30, "an")
        _vorspann_weg(seite)
        seite.js(SAAT, 2410 + breite)
        groesse = 1.0
        for faktor in (1.0, 1.3, 2.0):
            if faktor != groesse:
                seite.js(SCHRIFT, faktor / groesse)
                groesse = faktor
            m = seite.js(FLUGBAHN, [OBEN, ZEITEN, 25])
            m["breite"] = breite
            _flugbahn_pruefen(m, True)
            funde[faktor] = m
        frei = seite.js(FREIFLUG, [OBEN, 4000])
        assert frei["runden"] >= 4 and frei["sichtbar"] > 0, frei
        assert frei["ueberZiffern"] == 0 and frei["hoechsterFunke"] >= frei["kopfUnten"], frei
        assert frei["rechts"] <= frei["zifferLinks"] and frei["scroll"] == 0, frei
        assert seite.fehler == []
    finally:
        ctx.close()
    print("Flugbahn oben", breite, json.dumps({k: {"Abstand zum Kopf": round(v["hoechsterFunke"] - v["kopfUnten"], 1),
                                                   "rechts bis Ziffern": round(v["rechtsVonZiffern"], 1)}
                                               for k, v in funde.items()}))


def test_flugbahn_in_der_statistik(browser, basis):
    """Dasselbe in der Statistik am Ende einer Wiederholungsrunde (blau, 30
    Tage), bei 100, 130 und 200 % Schrift: Die Ziffern stehen dort nur eine
    Leerstelle hinter dem Kasten - kein Funke schneidet sie, keiner ragt aus
    dem Fenster, und Kasten und Zahl stehen mit Funken wie ohne."""
    ctx, seite = _kontext(browser, basis, hoehe=1600)
    try:
        _serie_starten(seite, 29, "glut")
        _vorspann_weg(seite)
        seite.js(TOPF_ENDE)
        seite.js(SAAT, 30)
        lage = """() => { const b = document.querySelector('#lBody .stat .flammenbox'), z = b.parentElement;
            const r = e => { const x = e.getBoundingClientRect(); return [x.left, x.top, x.width, x.height]; };
            return {box: r(b), zahl: r(z), stat: r(z.parentElement), stats: r(z.parentElement.parentElement)}; }"""
        groesse = 1.0
        for faktor in (1.0, 1.3, 2.0):
            if faktor != groesse:
                seite.js(SCHRIFT, faktor / groesse)
                groesse = faktor
            assert seite.js(ANZAHL, STAT) == 4
            mit = seite.js(lage)
            seite.js("() => document.querySelectorAll('#lBody .stat .fk').forEach(x => x.style.display = 'none')")
            assert seite.js(lage) == mit, faktor
            seite.js("() => document.querySelectorAll('#lBody .stat .fk').forEach(x => x.style.display = '')")
            m = seite.js(FLUGBAHN, [STAT, ZEITEN, 25])
            m["breite"] = 360
            _flugbahn_pruefen(m, False)
            assert seite.js("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth")
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Nach der Rueckkehr, ohne Zeitgeber, ohne Zufall beim Zeichnen (Befunde der
# Pruefung am 24.10.2026)
# ---------------------------------------------------------------------------

# Wann jeder Funke oben zum ersten Mal zu sehen ist, in ms ab jetzt, je Bild
# nachgesehen, hoechstens ms lang. null: in der Zeit gar nicht.
SICHTBAR_AB = """async (ms) => { const fks = [...document.querySelectorAll('.seriezahl .fk')], erst = fks.map(() => null);
  const t0 = performance.now();
  while(performance.now() - t0 < ms && erst.includes(null)){ await new Promise(r => requestAnimationFrame(r));
    fks.forEach((x, i) => { if(erst[i] === null && parseFloat(getComputedStyle(x).opacity) > 0.05)
      erst[i] = Math.round(performance.now() - t0); }); }
  return erst; }"""

# Dauer und Verzoegerung jedes Funkens, wie sie in seinem style stehen
TAKT = """(wo) => [...document.querySelectorAll(wo + ' .fk')].map(x =>
  ['--dauer', '--warte'].map(k => parseFloat(x.style.getPropertyValue(k))))"""


def test_nach_der_rueckkehr_gleich_wieder_da(browser, basis):
    """Die Startseite bleibt lange offen: gut 200 s Animationszeit (die
    Zeitleiste der Seite laeuft ueber das Chrome-Protokoll 20-fach), also
    einige hundert Runden. Dann in den Laden und zurueck. Solange die
    Startseite ausgeblendet ist, laeuft keine Animation; zurueck fangen die
    Funken von vorn an - alle vier sind nacheinander wieder da wie beim
    Start, spaetestens nach 2 s, und Dauer und Verzoegerung sind noch die
    aus FUNKEN_ERSTE. Zuerst rueckte die Verzoegerung jede Runde nach, und
    nach der Rueckkehr blieb ein Funke so viele Sekunden weg, wie sie
    inzwischen gross war - nach jeder Lektion, aus dem Laden und aus den
    Einstellungen (Befund der Pruefung)."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, 30, "an")
        _vorspann_weg(seite)
        seite.js(SAAT, 2410)
        seite.js("() => { window._runden = 0; document.addEventListener('animationiteration', e => {"
                 " if(e.animationName === 'flammeFlug') window._runden++; }); }")
        cdp = ctx.new_cdp_session(seite.page)
        cdp.send("Animation.enable")
        cdp.send("Animation.setPlaybackRate", {"playbackRate": 20})
        seite.page.wait_for_timeout(10000)
        cdp.send("Animation.setPlaybackRate", {"playbackRate": 1})
        runden = seite.js("() => window._runden")
        assert runden >= 200, runden
        seite.js("() => showLaden()")
        seite.page.wait_for_timeout(300)
        seite.js("() => showHome()")
        ab = seite.js(SICHTBAR_AB, 4000)
        takt = seite.js(TAKT, OBEN)
        erste = seite.js("() => FUNKEN_ERSTE.map(w => [w.dauer, w.warte])")
        assert len(ab) == 4 and None not in ab and max(ab) <= 2000, (runden, ab, takt)
        assert takt == erste, (runden, takt)
        assert seite.fehler == []
    finally:
        ctx.close()
    print("Runden", runden, "nach der Rueckkehr sichtbar ab (ms)", ab)


# Vor allen Skripten der Seite: jeder Rueckruf von setTimeout, setInterval
# und requestAnimationFrame wird mitgeschrieben, mit der Stelle, die ihn
# angelegt hat (die Zeile des Aufrufers im Stack).
ZEITGEBER = """(() => { const z = window.__zeitgeber = [];
  const wo = () => ((new Error().stack || '').split('\\n')[3] || '').trim();
  const huelle = (art, f, w) => typeof f !== 'function' ? f : function(){
    z.push(art + ' ' + w); return f.apply(this, arguments); };
  for(const art of ['setTimeout', 'setInterval', 'requestAnimationFrame']){ const o = window[art];
    window[art] = function(f, ...r){ return o.call(this, huelle(art, f, wo()), ...r); }; }
})();"""

# ms Millisekunden Ruhe, ab 13 s nach dem Laden: Dann sind die einmaligen
# Zeitgeber des Starts durch (Vorspann, Einstufung, Hinweise; der spaeteste
# ist die Notbremse des Vorspanns nach 11 s). Zurueck kommt, wie oft die
# Rueckrufe je Stelle liefen und wie viele Runden die Funken flogen. Das
# Fenster schliesst fensterZu, ein Zeitgeber des Tests: die Gegenprobe.
RUHE = """async (ms) => { await new Promise(r => setTimeout(r, Math.max(0, 13000 - performance.now())));
  const z = window.__zeitgeber, ab = z.length; let runden = 0;
  const zaehle = e => { if(e.animationName === 'flammeFlug') runden++; };
  const fensterZu = r => setTimeout(r, ms);
  document.addEventListener('animationiteration', zaehle);
  await new Promise(fensterZu);
  document.removeEventListener('animationiteration', zaehle);
  const je = {}; z.slice(ab).forEach(k => { je[k] = (je[k] || 0) + 1; });
  return {je, runden}; }"""


def test_keine_dauernden_zeitgeber(browser, basis, heute_stand):
    """Die Funken fliegen ohne Zeitgeber: Die Bewegung macht CSS, gewuerfelt
    wird bei animationiteration. In 4 s Ruhe auf der Startseite, waehrend
    die Funken mehrere Runden fliegen, laeuft deshalb kein Rueckruf von
    setTimeout, setInterval oder requestAnimationFrame mehr als einmal von
    derselben Stelle aus - ausser beim Drachen (lottie.min.js zeichnet jedes
    Bild). Die beiden Uhren der App (alle 10 s und alle 30 s) laufen darin
    hoechstens einmal. Gegenprobe: Der Zeitgeber des Tests wird gesehen."""
    ctx, seite = _kontext(browser, basis)
    ctx.add_init_script(ZEITGEBER)
    try:
        seite.starten(stand=heute_stand(tage=_serie_tage(30, "an")))
        _vorspann_weg(seite)
        _fliegen(seite, OBEN, "blau")
        m = seite.js(RUHE, 4000)
        assert seite.js(ANZAHL, OBEN) == 4
        assert seite.fehler == []
    finally:
        ctx.close()
    drache = {k: n for k, n in m["je"].items() if "/lottie.min.js" in k}
    sonst = {k: n for k, n in m["je"].items() if k not in drache}
    assert m["runden"] >= 4, m
    assert [n for k, n in sonst.items() if "fensterZu" in k] == [1], sonst
    assert all(n <= 1 for n in sonst.values()), sonst
    print("Ruhe", m["runden"], "Runden;", json.dumps(sonst), "; Drache", sum(drache.values()))


def test_ueberall_dieselben_funken(browser, basis):
    """Gezeichnet wird ohne Zufall: funkenHtml() baut jedes Mal dieselben
    vier Funken, die aus FUNKEN_ERSTE. Die Statistik am Ende einer
    Wiederholungsrunde traegt genau sie, bevor die erste Runde vorbei ist,
    und oben nach dem Aufbau stehen dieselben - Startseite und Statistik
    fangen gleich an (Ajdin: "beachte das nicht das es 2 verschiedene
    desgins sind"). Gewuerfelt wird erst bei animationiteration."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, 29, "glut")
        _vorspann_weg(seite)
        r = seite.js("() => { const a = funkenHtml(), b = funkenHtml(); (" + TOPF_ENDE + ")();"
                     " const fks = [...document.querySelectorAll('#lBody .stat .fk')];"
                     " return {a, b, stat: fks.map(x => x.outerHTML).join(''), erste: FUNKEN_ERSTE,"
                     " werte: fks.map(x => Object.fromEntries(Object.keys(FUNKEN_ERSTE[0])"
                     ".map(k => [k, parseFloat(x.style.getPropertyValue('--' + k))])))}; }")
        assert r["a"] == r["b"] and r["stat"] == r["a"], r
        assert r["werte"] == r["erste"], r
        seite.js("() => showHome()")
        seite.page.wait_for_function(FERTIG, timeout=4000)
        oben = seite.js("() => [...document.querySelectorAll('.seriezahl .fk')].map(x => x.outerHTML).join('')")
        assert oben == r["a"], (oben, r["a"])
        assert seite.fehler == []
    finally:
        ctx.close()
