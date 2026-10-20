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
"""
import base64
import datetime
import json
import os

import pytest
from conftest import Seite

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

# Nur eines von beiden sichtbar, alles andere unsichtbar (auch Festschmuck
# und Drache). Die Flamme mit voller Deckkraft und ohne Filter: gemessen wird
# wo sie steht, nicht wie blass sie ist. transform bleibt unberuehrt - genau
# darum geht es (Verschiebung, kleine Glut, Auflodern).
MESS_STIL = """(art) => { let s = document.getElementById('messStil');
  if(!s){ s = document.createElement('style'); s.id = 'messStil'; document.head.appendChild(s); }
  const T = {
    flamme: 'body *{visibility:hidden!important} #serieFlamme{visibility:visible!important;'
            + ' opacity:1!important; filter:none!important}',
    zahl: 'body *{visibility:hidden!important} #serieZahl{visibility:visible!important}',
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
ANDROID_STIL = """(url) => { const f = document.getElementById('serieFlamme');
  const s = document.createElement('style');
  s.textContent = "@font-face{font-family:'ZmajAndroidEmoji'; src:url('" + url + "') format('truetype')}";
  document.head.appendChild(s);
  const fam = getComputedStyle(f).fontFamily.split(',');
  fam.splice(1, 0, "'ZmajAndroidEmoji'");
  f.style.fontFamily = fam.join(',');
  return document.fonts.load("30px 'ZmajAndroidEmoji'", '🔥').then(l => l.length); }"""


def _android_emoji(ctx, seite):
    ctx.route("**/__android_emoji.ttf", lambda r: r.fulfill(path=ANDROID_EMOJI, content_type="font/ttf"))
    assert seite.js(ANDROID_STIL, seite.basis + "/__android_emoji.ttf") >= 1
    seite.page.wait_for_timeout(100)


def _tage(zustand):
    """aus: nie gelernt; glut: die letzten sieben Tage bis gestern;
    an: dieselben und heute."""
    heute = datetime.date.today()
    erster = {"aus": None, "glut": 1, "an": 0}[zustand]
    if erster is None:
        return []
    return [(heute - datetime.timedelta(days=i)).isoformat() for i in range(erster, 8)]


def _kontext(browser, basis, bewegung="no-preference", dpr=1):
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, device_scale_factor=dpr,
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


def _messen(seite, dpr):
    r = seite.js("() => { const r = document.querySelector('.seriezahl').getBoundingClientRect();"
                 " return {x: r.left, y: r.top - 14, width: r.width, height: r.height + 28}; }")
    bilder = {}
    for art in ("flamme", "zahl"):
        seite.js(MESS_STIL, art)
        seite.page.wait_for_timeout(30)
        bilder[art] = base64.b64encode(seite.page.screenshot(clip=r)).decode("ascii")
    seite.js(MESS_STIL, "echt")
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
        werte = seite.js("""() => { const f = document.getElementById('serieFlamme'), a = f.getAnimations()[0];
            a.pause(); const aus = {};
            for(const p of [0, 0.35, 0.6]){ a.currentTime = p * 2200; const s = getComputedStyle(f);
                aus[p] = [s.filter, s.opacity]; }
            a.play(); return aus; }""")
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
    """Die Flamme bleibt Schmuck fuer Bildschirmleser (aria-hidden), es gibt
    sie nur oben auf der Startseite, und vorgelesen wird weiter die Zahl."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "glut")
        f = seite.js(FLAMME)
        assert f["aria"] == "true" and f["text"] == "🔥" and f["alle"] == 1
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
