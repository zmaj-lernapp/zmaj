# -*- coding: utf-8 -*-
"""Die Serien-Flamme oben auf der Startseite (20.10.2026, Wunsch von Kuebra
und Ajdin, entschieden nach einer Vorschau mit drei Varianten).

Ajdin: "nimm a fuer 0 tage und den rest fuer c". Die Flamme zeigt also,
ob heute schon gelernt wurde:
  - Serie 0, heute nichts:          .aus  - grau, blass, steht still (A)
  - Serie laeuft, heute noch nichts: .glut - klein, entsaettigt, flackert (C)
  - heute gelernt:                   volle Flamme wie bisher
  - Wechsel von kalt auf an IN DER SITZUNG (erste Lektion des Tages):
    .auf - einmal kurz auflodern. Beim Start nicht.

Und: "die zahl und das feuer nicht auf einer ebene". Gemessen wird hier
nicht mit getBoundingClientRect - der Kasten eines Emojis sagt nichts darueber,
wo die Flamme sichtbar sitzt -, sondern an den Pixeln: je ein Bildschirmfoto
mit nur der Flamme und nur der Zahl, daraus die Zeilen mit Farbe. Verglichen
wird die Mitte zwischen oberster und unterster Zeile, in CSS-Pixeln.

Grosse Schrift: Android vergroessert in der WebView jede Schriftgroesse
(Einstellungen > Schriftgroesse), Kaesten in px aber nicht. Chrome hat dafuer
keinen Schalter; SCHRIFT macht dasselbe von Hand - jede berechnete
Schriftgroesse mal Faktor.

Aufbau wie test_stern.py: jeder Test mit eigenem Browserkontext im
Geraetemodus; die Bewegung (prefers-reduced-motion) ist immer ausdruecklich
gesetzt, sonst haengt das Ergebnis an der Einstellung des Rechners.

Seit dem 22.10.2026 (unten ab "Stufen"):
  - Stufen nach der laufenden Serie, Ajdin: "Mit Stufen" - unter 30 orange,
    ab 30 blau, ab 100 lila, ab 365 weissgold mit Funken. Die Glut behaelt
    die Farbe ihrer Stufe, das Auflodern ebenso. Funken nur, wenn die
    Flamme brennt und Bewegung erlaubt ist.
  - Dieselbe Flamme ueberall, Ajdin: "beachte das nicht das es 2
    verschiedene desgins sind": auch in der Statistik am Ende einer
    Lektion und einer Wiederholungsrunde, mit demselben Zustand und
    derselben Stufe (flammeKlassen/flammeHtml), dort ebenfalls an den
    Pixeln auf Hoehe der Zahl gemessen. Aufgelodert wird nur oben.
"""
import base64
import datetime
import io
import json
import os
import re

import pytest
from conftest import WURZEL, Seite

GLUT_TAKT = """() => { const f = document.getElementById('serieFlamme'), a = f.getAnimations()[0];
  a.pause(); const aus = {};
  for(const p of [0, 0.35, 0.6]){ a.currentTime = p * 2200; const s = getComputedStyle(f);
    aus[p] = [s.filter, s.opacity]; }
  a.play(); return aus; }"""

FLAMME = """() => { const f = document.getElementById('serieFlamme'), s = getComputedStyle(f);
  return {klasse: f.className, aria: f.getAttribute('aria-hidden'), text: f.textContent,
          zahl: document.getElementById('serieZahl').textContent,
          filter: s.filter, opacity: s.opacity, transform: s.transform,
          animation: s.animationName, dauer: s.animationDuration, wdh: s.animationIterationCount,
          laufend: f.getAnimations().map(a => a.animationName),
          noAnim: document.body.classList.contains('no-anim'),
          alle: document.querySelectorAll('.flamme').length}; }"""

# Die erste Lektion des Tages, kurz: markToday() wie am Ende einer Lektion,
# dann zurueck auf die Startseite. Der Test mit der echten Lektion steht
# weiter unten (test_auflodern_nach_der_ersten_lektion).
ERSTE_LEKTION = """() => { markToday(); homeMode = 'words'; showHome();
  const f = document.getElementById('serieFlamme');
  return {klasse: f.className, laufend: f.getAnimations().map(a => a.animationName)}; }"""

# Wie Android "Schriftgroesse": jede berechnete Schriftgroesse mal f. Erst alle
# lesen, dann schreiben - sonst rechnete ein Kind mit der schon vergroesserten
# Groesse seiner Eltern noch einmal.
SCHRIFT = """(f) => { const els = [...document.querySelectorAll('body *')];
  const g = els.map(e => parseFloat(getComputedStyle(e).fontSize));
  els.forEach((e, i) => e.style.fontSize = (g[i] * f) + 'px'); }"""

# Nur eines von beiden sichtbar, alles andere unsichtbar (auch Festschmuck,
# Drache und die Funken der Gold-Stufe). Die Flamme mit voller Deckkraft und
# ohne Filter: gemessen wird wo sie steht, nicht wie blass sie ist oder wie
# weit ihr Schein reicht. transform bleibt unberuehrt - genau darum geht es
# (Verschiebung, kleine Glut, Auflodern).
# f und z sind die ids von Flamme und Zahl. In der Statistik ist die Zahl
# kein eigenes Element, nur Text im <b> neben der Flamme: das <b> wird
# sichtbar, seine Kinder (die Flamme) bleiben es nicht, der Text erbt.
MESS_STIL = """([art, f, z]) => { let s = document.getElementById('messStil');
  if(!s){ s = document.createElement('style'); s.id = 'messStil'; document.head.appendChild(s); }
  const T = {
    flamme: 'body *{visibility:hidden!important} #' + f + '{visibility:visible!important;'
            + ' opacity:1!important; filter:none!important}',
    zahl: 'body *{visibility:hidden!important} #' + z + '{visibility:visible!important}',
    echt: ''};
  s.textContent = T[art]; }"""

# Oberste und unterste Zeile mit Farbe, im Browser ausgerechnet (der e2e-venv
# hat kein numpy/Pillow). Grund ist das Pixel oben links.
ZEILEN = """async ([bilder, dpr]) => {
  const lade = async s => { const img = new Image(); img.src = 'data:image/png;base64,' + s; await img.decode();
    const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
    const x = c.getContext('2d'); x.drawImage(img, 0, 0); return x.getImageData(0, 0, c.width, c.height); };
  const box = d => { const W = d.width, H = d.height, D = d.data; let oben = H, unten = -1;
    for(let y = 0; y < H; y++) for(let x = 0; x < W; x++){ const i = 4 * (y * W + x);
      if(Math.abs(D[i] - D[0]) + Math.abs(D[i+1] - D[1]) + Math.abs(D[i+2] - D[2]) > 40){
        if(y < oben) oben = y; if(y > unten) unten = y; } }
    return {oben: oben / dpr, unten: (unten + 1) / dpr, hoehe: (unten + 1 - oben) / dpr,
            mitte: (oben + unten + 1) / 2 / dpr}; };
  const f = box(await lade(bilder.flamme)), z = box(await lade(bilder.zahl));
  return {flamme: f, zahl: z, dy: f.mitte - z.mitte};
}"""

# Noto Color Emoji, die Emoji-Schrift von Android. Am Rechner zeichnet Chrome
# seine eigene (Windows: Segoe UI Emoji), und deren Flamme sitzt anders im
# Kasten - es zaehlt aber das Handy, dort hat Ajdin es gesehen. Android
# Studio bringt die Schrift fuer seine Vorschau mit; ZMAJ_ANDROID_EMOJI kann
# auf eine andere Kopie zeigen. Fehlt sie, misst nur der Test mit der
# Schrift des Rechners. (Pruefung vom 20.10.2026)
ANDROID_EMOJI = os.environ.get("ZMAJ_ANDROID_EMOJI") or (
    "C:/Program Files/Android/Android Studio/plugins/design-tools/resources/layoutlib/data/fonts/NotoColorEmoji.ttf")

# Als zweite Schrift der Flamme, gleich hinter Spectral: Grundlinie und Hoehe
# des Kastens bestimmt weiter Spectral, wie auf dem Handy; nur das Emoji
# kommt aus Noto statt aus dem Rueckfall des Rechners.
ANDROID_STIL = """([url, id]) => { const f = document.getElementById(id);
  const s = document.createElement('style');
  s.textContent = "@font-face{font-family:'ZmajAndroidEmoji'; src:url('" + url + "') format('truetype')}";
  document.head.appendChild(s);
  const fam = getComputedStyle(f).fontFamily.split(',');
  fam.splice(1, 0, "'ZmajAndroidEmoji'");
  f.style.fontFamily = fam.join(',');
  return document.fonts.load("30px 'ZmajAndroidEmoji'", '🔥').then(l => l.length); }"""


def _android_emoji(ctx, seite, ziel="serieFlamme"):
    ctx.route("**/__android_emoji.ttf", lambda r: r.fulfill(path=ANDROID_EMOJI, content_type="font/ttf"))
    assert seite.js(ANDROID_STIL, [seite.basis + "/__android_emoji.ttf", ziel]) >= 1
    seite.page.wait_for_timeout(100)


def _tage(zustand):
    """aus: nie gelernt; glut: die letzten sieben Tage bis gestern;
    an: dieselben und heute."""
    heute = datetime.date.today()
    erster = {"aus": None, "glut": 1, "an": 0}[zustand]
    if erster is None:
        return []
    return [(heute - datetime.timedelta(days=i)).isoformat() for i in range(erster, 8)]


def _kontext(browser, basis, bewegung="no-preference", dpr=1, hoehe=640):
    ctx = browser.new_context(viewport={"width": 360, "height": hoehe}, device_scale_factor=dpr,
                              locale="de-DE", service_workers="block", reduced_motion=bewegung)
    return ctx, Seite(ctx.new_page(), basis)


def _starten(seite, heute_stand, zustand, animationen=True):
    if not animationen:
        seite.page.goto(seite.basis + "/leer")
        seite.js("() => { localStorage.clear(); localStorage.setItem('zmaj_anim', 'aus'); }")
    seite.starten(stand=heute_stand(tage=_tage(zustand)), leeren=animationen)


def _vorspann_weg(seite):
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)


def _matrix(transform):
    """'matrix(a, b, c, d, e, f)' -> [a, b, c, d, e, f]"""
    assert transform.startswith("matrix("), transform
    return [float(x) for x in transform[7:-1].split(",")]


def _messen(seite, dpr, kasten=".seriezahl", f="serieFlamme", z="serieZahl"):
    r = seite.js("(k) => { const r = document.querySelector(k).getBoundingClientRect();"
                 " return {x: r.left, y: r.top - 14, width: r.width, height: r.height + 28}; }", kasten)
    # Das Foto nimmt nur, was im Fenster steht - der Kasten muss ganz hinein.
    assert r["y"] >= 0 and r["y"] + r["height"] <= seite.js("() => innerHeight"), r
    bilder = {}
    for art in ("flamme", "zahl"):
        seite.js(MESS_STIL, [art, f, z])
        seite.page.wait_for_timeout(30)
        bilder[art] = base64.b64encode(seite.page.screenshot(clip=r)).decode("ascii")
    seite.js(MESS_STIL, ["echt", f, z])
    return seite.js(ZEILEN, [bilder, dpr])


# ---------------------------------------------------------------------------
# Die drei Zustaende
# ---------------------------------------------------------------------------

def test_aus_bei_serie_null(browser, basis, heute_stand):
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "aus")
        f = seite.js(FLAMME)
        assert f["zahl"] == "0"
        assert f["klasse"].split() == ["flamme", "aus"]
        assert f["filter"] == "grayscale(1)" and f["opacity"] == "0.32"
        assert f["animation"] == "none" and f["laufend"] == []     # steht still
        a, b, c, d, _, ty = _matrix(f["transform"])
        assert (a, b, c, d) == (1, 0, 0, 1) and ty < 0              # nur angehoben
        assert seite.fehler == []
    finally:
        ctx.close()


def test_glut_bei_laufender_serie_ohne_heute(browser, basis, heute_stand):
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "glut")
        f = seite.js(FLAMME)
        assert f["zahl"] == "7"
        assert f["klasse"].split() == ["flamme", "glut"]
        a, b, c, d, _, ty = _matrix(f["transform"])
        assert (round(a, 3), b, c, round(d, 3)) == (0.7, 0, 0, 0.7) and ty < 0
        assert f["animation"] == "flammeGlut" and f["dauer"] == "2.2s" and f["wdh"] == "infinite"
        assert f["laufend"] == ["flammeGlut"]
        # Die Vorlage aus der Vorschau, an drei Stellen des Takts abgelesen
        werte = seite.js(GLUT_TAKT)
        assert werte["0"] == ["grayscale(0.55) brightness(0.75)", "0.45"]
        assert werte["0.35"] == ["grayscale(0.6) brightness(0.7)", "0.4"]
        assert werte["0.6"] == ["grayscale(0.3) brightness(1)", "0.75"]
        assert seite.fehler == []
    finally:
        ctx.close()


def test_an_wenn_heute_gelernt(browser, basis, heute_stand):
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "an")
        f = seite.js(FLAMME)
        assert f["zahl"] == "8"
        assert f["klasse"].split() == ["flamme"]
        assert f["filter"] == "none" and f["opacity"] == "1"
        assert f["animation"] == "none" and f["laufend"] == []
        a, b, c, d, _, ty = _matrix(f["transform"])
        assert (a, b, c, d) == (1, 0, 0, 1) and ty < 0
        assert seite.fehler == []
    finally:
        ctx.close()


def test_barrierefreiheit_unveraendert(browser, basis, heute_stand):
    """Die Flamme bleibt Schmuck fuer Bildschirmleser (aria-hidden), samt
    ihrem Kasten mit den Funken; nach dem Start gibt es sie einmal (die
    Statistik am Lektionsende kommt erst mit der Lektion), und vorgelesen
    wird weiter die Zahl."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "glut")
        f = seite.js(FLAMME)
        assert f["aria"] == "true" and f["text"] == "🔥" and f["alle"] == 1
        assert seite.js("() => document.getElementById('serieFlamme').parentElement.getAttribute('aria-hidden')") == "true"
        assert seite.js("() => document.getElementById('serieZahl').getAttribute('aria-hidden')") is None
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Auflodern: nur beim Wechsel in der Sitzung
# ---------------------------------------------------------------------------

def test_kein_auflodern_beim_start(browser, basis, heute_stand):
    """Wer heute schon gelernt hat und die App oeffnet, sieht sie einfach
    brennen - auch nach dem Neuladen und beim Reiterwechsel."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "an")
        for schritt in ("start", "neu geladen", "reiter"):
            if schritt == "neu geladen":
                seite.neu_laden()
            elif schritt == "reiter":
                _vorspann_weg(seite)
                seite.js("() => { document.getElementById('modeStories').click(); }")
                seite.js("() => { document.getElementById('modeWords').click(); }")
            f = seite.js(FLAMME)
            assert "auf" not in f["klasse"].split() and f["laufend"] == [], (schritt, f)
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("vorher", ["aus", "glut"])
def test_auflodern_nach_der_ersten_lektion(browser, basis, heute_stand, vorher):
    """Eine echte Lektion, dann "Zurueck zum Lernpfad": die Flamme lodert
    einmal auf und brennt danach normal. Ein zweiter Besuch der Startseite
    loest nichts mehr aus."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, vorher)
        assert seite.js(FLAMME)["klasse"].split() == ["flamme", vorher]
        seite.js("() => { openLevel(0); startLesson(); }")
        seite.durchspielen("lBody", "Lx")
        nachher = seite.js("""() => { document.getElementById('lPfad').click();
            const f = document.getElementById('serieFlamme');
            return {klasse: f.className, laufend: f.getAnimations().map(a => a.animationName),
                    dauer: getComputedStyle(f).animationDuration}; }""")
        assert nachher["klasse"].split() == ["flamme", "auf"], nachher
        assert nachher["laufend"] == ["flammeAuf"] and nachher["dauer"] == "0.8s"
        # animationend nimmt .auf wieder weg
        seite.page.wait_for_function("() => !document.getElementById('serieFlamme').classList.contains('auf')",
                                     timeout=3000)
        f = seite.js(FLAMME)
        assert f["klasse"].split() == ["flamme"] and f["laufend"] == [] and f["filter"] == "none"
        seite.js("() => { document.getElementById('modeStories').click(); document.getElementById('modeWords').click(); }")
        f = seite.js(FLAMME)
        assert f["klasse"].split() == ["flamme"] and f["laufend"] == []
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("weg", ["schalter", "geraet"])
def test_ohne_animationen_steht_alles_still(browser, basis, heute_stand, weg):
    """Schalter "Animationen" aus oder "Bewegung reduzieren" am Geraet: die
    Glut steht als ruhiges Bild da (klein, entsaettigt, blass), und nach der
    ersten Lektion wird nicht aufgelodert."""
    ctx, seite = _kontext(browser, basis, bewegung="reduce" if weg == "geraet" else "no-preference")
    try:
        _starten(seite, heute_stand, "glut", animationen=(weg != "schalter"))
        f = seite.js(FLAMME)
        assert f["noAnim"] is (weg == "schalter")
        assert f["klasse"].split() == ["flamme", "glut"]
        assert f["animation"] == "none" and f["laufend"] == []
        assert f["filter"] == "grayscale(0.55) brightness(0.75)" and f["opacity"] == "0.45"
        assert round(_matrix(f["transform"])[0], 3) == 0.7
        nachher = seite.js(ERSTE_LEKTION)
        assert nachher["klasse"].split() == ["flamme"] and nachher["laufend"] == [], nachher
        assert seite.fehler == []
    finally:
        ctx.close()


def test_mit_animationen_lodert_auch_der_kurzweg(browser, basis, heute_stand):
    """Gegenprobe zu oben mit demselben Kurzweg (markToday + showHome)."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "glut")
        nachher = seite.js(ERSTE_LEKTION)
        assert nachher["klasse"].split() == ["flamme", "auf"] and nachher["laufend"] == ["flammeAuf"]
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Flamme und Zahl auf einer Hoehe
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("schrift", ["rechner", "android"])
@pytest.mark.parametrize("zustand", ["aus", "glut", "an"])
def test_flamme_und_zahl_auf_einer_hoehe(browser, basis, heute_stand, zustand, schrift):
    """Sichtbare Mitte der Flamme gegen sichtbare Mitte der Ziffern, bei
    normaler Schrift, 130 % und 200 %. Vor dem 20.10.2026 stand die Flamme
    4,5 / 6,25 / 9,25 px tiefer. Bei der Glut ausserdem: sie ist wirklich
    kleiner (um 0,7), schrumpft also um ihre Mitte und nicht nach unten.
    Zweimal: mit der Emoji-Schrift des Rechners und mit der von Android
    (ANDROID_EMOJI). Deren Flamme ist etwas groesser, 33,5 statt 29,5 px
    bei 30 px Schrift."""
    if schrift == "android" and not os.path.isfile(ANDROID_EMOJI):
        pytest.skip("Noto Color Emoji nicht gefunden, siehe ANDROID_EMOJI")
    dpr = 2
    ctx, seite = _kontext(browser, basis, dpr=dpr)
    funde = {}
    try:
        _starten(seite, heute_stand, zustand)
        _vorspann_weg(seite)
        emoji = 30
        if schrift == "android":
            _android_emoji(ctx, seite)
            emoji = 33.5
        groesse = 1.0
        for faktor in (1.0, 1.3, 2.0):
            if faktor != groesse:
                seite.js(SCHRIFT, faktor / groesse)
                groesse = faktor
            m = _messen(seite, dpr)
            funde[faktor] = m
            assert abs(m["dy"]) <= 2, (zustand, faktor, m)
            # Groesse der Flamme gegen die Schrift: 30 px Emoji ~ 29,5 px hoch
            # (Android 33,5) - und zugleich der Beweis, dass die Schrift wirkt
            soll = emoji * faktor * (0.7 if zustand == "glut" else 1)
            assert abs(m["flamme"]["hoehe"] - soll) <= 0.1 * soll, (zustand, faktor, m)
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()
    print(schrift, zustand, json.dumps({k: round(v["dy"], 2) for k, v in funde.items()}))   # mit -s sichtbar


def test_auflodern_bleibt_auf_einer_hoehe(browser, basis, heute_stand):
    """Auf dem Hoehepunkt des Aufloderns (45 %, scale 1,28) waechst die
    Flamme um ihre Mitte - auch bei grosser Schrift."""
    dpr = 2
    ctx, seite = _kontext(browser, basis, dpr=dpr)
    try:
        _starten(seite, heute_stand, "glut")
        _vorspann_weg(seite)
        seite.js(SCHRIFT, 1.3)
        assert seite.js(ERSTE_LEKTION)["laufend"] == ["flammeAuf"]
        seite.js("""() => { const a = document.getElementById('serieFlamme').getAnimations()[0];
            a.pause(); a.currentTime = 0.45 * 800; }""")
        m = _messen(seite, dpr)
        assert abs(m["dy"]) <= 2, m
        soll = 30 * 1.3 * 1.28
        assert abs(m["flamme"]["hoehe"] - soll) <= 0.1 * soll, m
        seite.js("() => document.getElementById('serieFlamme').getAnimations()[0].finish()")
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Stufen nach der laufenden Serie (22.10.2026, Ajdin: "Mit Stufen")
# ---------------------------------------------------------------------------
# Lerntage vor APP_START wirft die App beim Laden weg (standUebernehmen,
# 17.10.2026) - eine Serie von 365 Tagen gibt es also erst ab APP_START +
# 364. Fuer die Stufen wird die Uhr des Browsers deshalb vorgestellt, wie in
# test_sicherung_haerten.py (Date.now steht, Zeitgeber laufen). Eine echte
# Lektion laeuft damit nicht: DURCHSPIELEN wartet mit Date.now - die Tests
# mit Lektion bleiben bei der Uhr des Rechners und der Schwelle 30.

with io.open(os.path.join(WURZEL, "web", "index.html"), encoding="utf-8") as _f:
    APP_START = datetime.date.fromisoformat(
        re.search(r"const APP_START = '(\d{4}-\d{2}-\d{2})';", _f.read()).group(1))
SPAETER = APP_START + datetime.timedelta(days=400)

# Der Farbfilter je Stufe und die Farbe ihres stillen Scheins, so wie Chrome
# sie ausschreibt.
TON = {"": "", "blau": "hue-rotate(190deg) saturate(1.35) ", "lila": "hue-rotate(245deg) saturate(1.45) ",
       "gold": "saturate(0.45) brightness(1.3) "}
SCHEIN = {"blau": "rgba(60, 150, 255, 0.55)", "lila": "rgba(170, 90, 255, 0.55)", "gold": "rgba(255, 214, 90, 0.9)"}
GLANZ = {"": "rgba(255, 140, 0, 0.9)", "blau": "rgba(60, 150, 255, 0.9)", "lila": "rgba(170, 90, 255, 0.9)",
         "gold": "rgb(255, 214, 90)"}
STUFEN = [(29, ""), (30, "blau"), (99, "blau"), (100, "lila"), (364, "lila"), (365, "gold")]

FUNKEN = """(wo) => [...document.querySelectorAll(wo + ' .funke')].map(x => { const s = getComputedStyle(x);
  return {text: x.textContent, pos: s.position, name: s.animationName, opacity: s.opacity, verz: s.animationDelay,
          laufend: x.getAnimations().map(a => a.animationName), aria: x.parentElement.getAttribute('aria-hidden')}; })"""

# Jede Funke angehalten bei 40 % ihres Takts (nach ihrer Verzoegerung): dort
# ist sie ganz da.
FUNKEN_HOEHEPUNKT = """(wo) => [...document.querySelectorAll(wo + ' .funke')].map(x => {
  const a = x.getAnimations()[0]; a.pause(); a.currentTime = a.effect.getTiming().delay + 0.4 * 2400;
  const o = getComputedStyle(x).opacity; a.play(); return o; })"""

# Wo steht was: die Kaesten oben auf der Startseite.
LAGE = """() => Object.fromEntries(['.obenreihe', '.seriezahl', '.flammenbox', '#serieFlamme', '#serieZahl', '#streakLine']
  .map(k => { const r = document.querySelector(k).getBoundingClientRect(); return [k, [r.left, r.top, r.width, r.height]]; }))"""

# Die Flamme in der Statistik am Ende (Lektion oder Wiederholungsrunde), und
# was flammeKlassen() gerade sagt.
STAT_FLAMME = """() => { const f = document.querySelector('#lBody .stat .flamme'), s = getComputedStyle(f), b = f.parentElement;
  return {klasse: f.className, soll: flammeKlassen(), filter: s.filter, laufend: f.getAnimations().map(a => a.animationName),
          box: b.className, aria: b.getAttribute('aria-hidden'), text: f.textContent, zahl: f.closest('b').textContent,
          gleich: b.outerHTML === flammeHtml(), funken: b.querySelectorAll('.funke').length}; }"""

# Das Ende einer Wiederholungsrunde, ohne die Runde: topfEnde() mit einer
# leeren Runde. Es setzt den Lerntag wie das Ende einer Lektion.
TOPF_ENDE = """() => { showView('levelView');
  for(const [id, an] of [['levelHome', 'none'], ['test', 'none'], ['lesson', 'block']]) document.getElementById(id).style.display = an;
  Lx = {queue: [], i: 0, results: [], right: 0, total: 0, skipped: 0, newWords: new Set(), retried: new Set(),
        topf: true, quelle: 'topf'};
  topfEnde(); }"""

# Die Flamme oben auf dem Hoehepunkt des Aufloderns (45 %), angehalten.
AUF_HOEHEPUNKT = """() => { const f = document.getElementById('serieFlamme'), a = f.getAnimations()[0];
  a.pause(); a.currentTime = 0.45 * 800; const w = getComputedStyle(f).filter; a.play(); return w; }"""


def _lodert_in_stufenfarbe(filter_, stufe):
    """Auf dem Hoehepunkt: erst der Farbfilter der Stufe, dann der volle
    Glanz in ihrer Farbe. grayscale steht dort bei fast 0 - Chrome schreibt
    wegen der Kurve z. B. 6.1e-17, deshalb nur der Anfang."""
    return (filter_.startswith(TON[stufe] + "grayscale(")
            and ("brightness(1.15) drop-shadow(" + GLANZ[stufe]) in filter_)


def _serie_starten(seite, n, zustand, animationen=True):
    """Eine Serie von n Tagen am Tag SPAETER: glut bis gestern, an bis heute."""
    seite.page.clock.set_fixed_time(datetime.datetime.combine(SPAETER, datetime.time(12, 0)))
    erster = {"glut": 1, "an": 0}[zustand]
    tage = [(SPAETER - datetime.timedelta(days=i)).isoformat() for i in range(erster, erster + n)]
    stand = {"einstufung": {"tag": SPAETER.isoformat(), "wahl": "neu", "bis": ""}, "tage": tage}
    if not animationen:
        seite.page.goto(seite.basis + "/leer")
        seite.js("() => { localStorage.clear(); localStorage.setItem('zmaj_anim', 'aus'); }")
    seite.starten(stand=stand, leeren=animationen)


def _serie_tage(n, zustand):
    """Wie _tage, nur n Tage lang - mit der Uhr des Rechners."""
    heute = datetime.date.today()
    erster = {"glut": 1, "an": 0}[zustand]
    return [(heute - datetime.timedelta(days=i)).isoformat() for i in range(erster, erster + n)]


@pytest.mark.parametrize("zustand", ["glut", "an"])
@pytest.mark.parametrize("tage,stufe", STUFEN)
def test_stufe_nach_der_serie(browser, basis, tage, stufe, zustand):
    """29 Tage orange, 30 und 99 blau, 100 und 364 lila, 365 weissgold.
    Brennend mit dem stillen Schein der Stufe (orange: kein Filter, wie
    bisher), als Glut in der Farbe der Stufe: ihr Farbfilter steht vor dem
    der Glut, in jedem Schritt des Flackerns. Die Zahl ist die Serie."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, tage, zustand)
        f = seite.js(FLAMME)
        assert f["zahl"] == str(tage)
        soll = ["flamme"] + (["glut"] if zustand == "glut" else []) + (["stufe-" + stufe] if stufe else [])
        assert f["klasse"].split() == soll
        ton = TON[stufe]
        if zustand == "an":
            assert f["laufend"] == [] and f["opacity"] == "1"
            if stufe:
                assert f["filter"].startswith(ton + "drop-shadow(" + SCHEIN[stufe]), f["filter"]
            else:
                assert f["filter"] == "none"
        else:
            assert f["laufend"] == ["flammeGlut"]
            a, b, c, d, _, ty = _matrix(f["transform"])
            assert (round(a, 3), round(d, 3)) == (0.7, 0.7) and ty < 0
            werte = seite.js(GLUT_TAKT)
            assert werte["0"] == [ton + "grayscale(0.55) brightness(0.75)", "0.45"]
            assert werte["0.35"] == [ton + "grayscale(0.6) brightness(0.7)", "0.4"]
            assert werte["0.6"] == [ton + "grayscale(0.3) brightness(1)", "0.75"]
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("weg", ["schalter", "geraet"])
def test_glut_ohne_animationen_in_stufenfarbe(browser, basis, weg):
    """Ohne Bewegung steht die Glut still - und behaelt trotzdem die Farbe
    ihrer Stufe (hier lila, 100 Tage bis gestern)."""
    ctx, seite = _kontext(browser, basis, bewegung="reduce" if weg == "geraet" else "no-preference")
    try:
        _serie_starten(seite, 100, "glut", animationen=(weg != "schalter"))
        f = seite.js(FLAMME)
        assert f["noAnim"] is (weg == "schalter")
        assert f["klasse"].split() == ["flamme", "glut", "stufe-lila"]
        assert f["animation"] == "none" and f["laufend"] == []
        assert f["filter"] == TON["lila"] + "grayscale(0.55) brightness(0.75)" and f["opacity"] == "0.45"
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("fall", ["gold_an", "gold_glut", "gold_schalter", "gold_geraet", "lila_an"])
def test_funken_nur_brennend_mit_animationen(browser, basis, fall):
    """Die drei Funken stehen immer im Kasten der Flamme (aria-hidden,
    absolut gesetzt), funkeln aber nur in der Gold-Stufe, nur wenn die
    Flamme brennt und nur mit Bewegung. Sonst laeuft keine Animation, und
    sie bleiben unsichtbar (opacity 0)."""
    tage = 364 if fall == "lila_an" else 365
    zustand = "glut" if fall == "gold_glut" else "an"
    ctx, seite = _kontext(browser, basis, bewegung="reduce" if fall == "gold_geraet" else "no-preference")
    try:
        _serie_starten(seite, tage, zustand, animationen=(fall != "gold_schalter"))
        funken = seite.js(FUNKEN, ".seriezahl")
        assert [x["text"] for x in funken] == ["✨"] * 3
        assert all(x["pos"] == "absolute" and x["aria"] == "true" for x in funken), funken
        if fall == "gold_an":
            assert [x["laufend"] for x in funken] == [["flammeFunke"]] * 3, funken
            assert [x["verz"] for x in funken] == ["0s", "0.8s", "1.6s"]
            assert seite.js(FUNKEN_HOEHEPUNKT, ".seriezahl") == ["1"] * 3
        else:
            assert all(x["laufend"] == [] and x["name"] == "none" and x["opacity"] == "0" for x in funken), funken
        assert seite.fehler == []
    finally:
        ctx.close()


def test_funken_verschieben_nichts(browser, basis):
    """Gold, brennend, Funken laufen: alle Kaesten oben stehen genau da, wo
    sie ohne Funken stuenden, und nichts ragt seitlich aus der Seite."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, 365, "an")
        _vorspann_weg(seite)
        assert [x["laufend"] for x in seite.js(FUNKEN, ".seriezahl")] == [["flammeFunke"]] * 3
        mit = seite.js(LAGE)
        seite.js("() => document.querySelectorAll('.seriezahl .funke').forEach(x => x.style.display = 'none')")
        ohne = seite.js(LAGE)
        assert mit == ohne
        assert seite.js("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth")
        assert seite.fehler == []
    finally:
        ctx.close()
    print("Lage gold", json.dumps(mit))   # mit -s sichtbar


def test_gold_flamme_auf_einer_hoehe(browser, basis):
    """Die Stufe aendert nur Farbe und Schein, nicht die Lage: auch die
    Gold-Flamme mit ihren Funken steht mit der Zahl auf einer Hoehe, bei
    normaler und doppelter Schrift."""
    dpr = 2
    ctx, seite = _kontext(browser, basis, dpr=dpr)
    funde = {}
    try:
        _serie_starten(seite, 365, "an")
        _vorspann_weg(seite)
        groesse = 1.0
        for faktor in (1.0, 2.0):
            if faktor != groesse:
                seite.js(SCHRIFT, faktor / groesse)
                groesse = faktor
            m = _messen(seite, dpr)
            funde[faktor] = m
            assert abs(m["dy"]) <= 2, (faktor, m)
            soll = 30 * faktor
            assert abs(m["flamme"]["hoehe"] - soll) <= 0.1 * soll, (faktor, m)
        assert seite.fehler == []
    finally:
        ctx.close()
    print("gold", json.dumps({k: round(v["dy"], 2) for k, v in funde.items()}))


# ---------------------------------------------------------------------------
# Dieselbe Flamme ueberall (22.10.2026)
# ---------------------------------------------------------------------------

def test_lektionsende_und_startseite_zeigen_dieselbe_flamme(browser, basis, heute_stand):
    """29 Tage bis gestern: oben eine orange Glut. Eine echte Lektion macht
    daraus 30 - die Statistik am Lektionsende zeigt die blaue Flamme,
    brennend, ohne Auflodern, gebaut von flammeHtml(). Zurueck auf der
    Startseite lodert sie auf, schon in Blau (auch auf dem Hoehepunkt), und
    brennt danach mit genau denselben Klassen wie in der Statistik."""
    ctx, seite = _kontext(browser, basis)
    try:
        seite.starten(stand=heute_stand(tage=_serie_tage(29, "glut")))
        assert seite.js(FLAMME)["klasse"].split() == ["flamme", "glut"]
        seite.js("() => { openLevel(0); startLesson(); }")
        seite.durchspielen("lBody", "Lx")
        st = seite.js(STAT_FLAMME)
        assert st["klasse"] == st["soll"] == "flamme stufe-blau", st
        assert st["laufend"] == [] and st["filter"].startswith(TON["blau"] + "drop-shadow(" + SCHEIN["blau"]), st
        assert st["box"] == "flammenbox" and st["aria"] == "true" and st["text"] == "🔥" and st["funken"] == 3
        assert st["gleich"] and st["zahl"].strip().endswith(" 30"), st
        oben = seite.js("""() => { document.getElementById('lPfad').click();
            const f = document.getElementById('serieFlamme');
            return {klasse: f.className, laufend: f.getAnimations().map(a => a.animationName)}; }""")
        assert oben["klasse"].split() == ["flamme", "stufe-blau", "auf"] and oben["laufend"] == ["flammeAuf"], oben
        assert _lodert_in_stufenfarbe(seite.js(AUF_HOEHEPUNKT), "blau")
        seite.page.wait_for_function("() => !document.getElementById('serieFlamme').classList.contains('auf')",
                                     timeout=3000)
        f = seite.js(FLAMME)
        assert f["klasse"] == st["klasse"] and f["zahl"] == "30"
        # Derselbe Filter; nur die Weite des Scheins steht in em und ist an
        # der kleineren Flamme der Statistik kleiner (6 px an 30 px, 3,6 px
        # an 18 px).
        ohne_weite = re.compile(r" [0-9.]+px\)$")
        assert ohne_weite.sub("", f["filter"]) == ohne_weite.sub("", st["filter"]), (f["filter"], st["filter"])
        assert f["filter"].endswith(" 6px)") and st["filter"].endswith(" 3.6px)")
        # Die Statistik hat nicht aufgelodert und tut es auch jetzt nicht
        assert seite.js("() => document.querySelector('#lBody .stat .flamme').getAnimations().length") == 0
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("tage,stufe", [(29, "blau"), (364, "gold")])
def test_wiederholungsrunde_zeigt_dieselbe_flamme(browser, basis, tage, stufe):
    """Das Ende einer Wiederholungsrunde (topfEnde) setzt den Lerntag wie eine
    Lektion: 29 -> 30 blau, 364 -> 365 gold. Die Statistik zeigt dieselbe
    Flamme wie danach die Startseite, ohne Auflodern; in Gold funkeln die
    Funken dort ebenso."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, tage, "glut")
        seite.js(TOPF_ENDE)
        st = seite.js(STAT_FLAMME)
        assert st["klasse"] == st["soll"] == "flamme stufe-" + stufe, st
        assert st["laufend"] == [] and st["gleich"] and st["zahl"].strip().endswith(" " + str(tage + 1)), st
        funken = seite.js(FUNKEN, "#lBody .stat")
        laeuft = [["flammeFunke"]] * 3 if stufe == "gold" else [[]] * 3
        assert [x["laufend"] for x in funken] == laeuft, funken
        oben = seite.js("() => { showHome(); return document.getElementById('serieFlamme').className; }")
        assert oben.split() == ["flamme", "stufe-" + stufe, "auf"]
        assert _lodert_in_stufenfarbe(seite.js(AUF_HOEHEPUNKT), stufe)
        seite.page.wait_for_function("() => !document.getElementById('serieFlamme').classList.contains('auf')",
                                     timeout=3000)
        assert seite.js("() => document.getElementById('serieFlamme').className") == st["klasse"]
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("schrift", ["rechner", "android"])
def test_statistik_flamme_und_zahl_auf_einer_hoehe(browser, basis, heute_stand, schrift):
    """Die Flamme in der Statistik am Lektionsende neben ihrer Zahl (Nunito
    18 px): sichtbare Mitte gegen sichtbare Mitte, bei 100, 130 und 200 %
    Schrift, mit beiden Emoji-Schriften. Gemessen wie oben; das Fenster ist
    hoch genug, dass die Statistik auch bei doppelter Schrift ganz darin
    steht."""
    if schrift == "android" and not os.path.isfile(ANDROID_EMOJI):
        pytest.skip("Noto Color Emoji nicht gefunden, siehe ANDROID_EMOJI")
    dpr = 2
    ctx, seite = _kontext(browser, basis, dpr=dpr, hoehe=1600)
    funde = {}
    try:
        _starten(seite, heute_stand, "glut")
        _vorspann_weg(seite)
        seite.js("() => { openLevel(0); startLesson(); }")
        seite.durchspielen("lBody", "Lx")
        seite.js("""() => { const f = document.querySelector('#lBody .stat .flamme');
            f.id = 'messFlamme'; f.closest('b').id = 'messZahl'; window.scrollTo(0, 0); }""")
        emoji = 18
        if schrift == "android":
            _android_emoji(ctx, seite, "messFlamme")
            emoji = 18 * 33.5 / 30
        groesse = 1.0
        for faktor in (1.0, 1.3, 2.0):
            if faktor != groesse:
                seite.js(SCHRIFT, faktor / groesse)
                groesse = faktor
            seite.page.wait_for_timeout(50)
            m = _messen(seite, dpr, "#messZahl", "messFlamme", "messZahl")
            funde[faktor] = m
            assert abs(m["dy"]) <= 1.5, (faktor, m)
            soll = emoji * faktor
            assert abs(m["flamme"]["hoehe"] - soll) <= 0.1 * soll, (faktor, m)
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()
    print("statistik", schrift, json.dumps({k: [round(v["dy"], 2), round(v["flamme"]["hoehe"], 2),
                                                round(v["zahl"]["hoehe"], 2)] for k, v in funde.items()}))
