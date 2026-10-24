# -*- coding: utf-8 -*-
"""Die Serien-Flamme oben auf der Startseite (20.10.2026, Wunsch von Kuebra
und Ajdin, entschieden nach einer Vorschau mit drei Varianten).

Ajdin: "nimm a fuer 0 tage und den rest fuer c". Die Flamme zeigt also,
ob heute schon gelernt wurde:
  - Serie 0, heute nichts:          .aus  - kalte graue Kohle, steht still (A)
  - Serie laeuft, heute noch nichts: .glut - gluehende Kohlen, flackern (C)
  - heute gelernt:                   die volle Flamme
  - Wechsel von kalt auf an IN DER SITZUNG (erste Lektion des Tages):
    .auf - die Flamme baut sich einmal aus der Glut auf. Beim Start nicht.

Seit dem 24.10.2026 gemalt statt Emoji. Das Emoji sah auf Ajdins Samsung
anders aus als am Rechner, die Glut sass zu hoch ("die kleine flamme ist zu
weit oben"). Jetzt steht in einem Rahmen 403:512, gleich gross in allen
Zustaenden, je ein Bild aus web/flamme: flamme.webp, glut.webp (kleine
gluehende Kohlen, KEINE verkleinerte Flamme), aus.webp (kalte Kohle). Der
Aufbau Glut -> Flamme ist Fassung 2 der Vorschau ("feuer ist gut geworden
wir nehmen den"): die Ebenen ebene_*.webp, gestapelt, 1,5 s, danach das eine
Bild flamme.webp - ohne Sprung.

Und: "die zahl und das feuer nicht auf einer ebene". Der Rahmen sitzt mit
seiner Mitte auf der Mitte der Ziffern. Gemessen wird die Zahl an den
Pixeln: je ein Bildschirmfoto mit nur der Flamme und nur der Zahl, daraus
die Zeilen mit Farbe, verglichen wird die Mitte zwischen oberster und
unterster Zeile, in CSS-Pixeln. Der Rahmen ist ein Bild-Kasten, seine Lage
sagt getBoundingClientRect; bei der brennenden Flamme wird zusaetzlich das
sichtbare Bild an den Pixeln gemessen. Keine Emoji-Schrift mehr im Spiel -
die Masse sind auf jedem Rechner und in der CI (Linux) dieselben.

Grosse Schrift: Android vergroessert in der WebView jede Schriftgroesse
(Einstellungen > Schriftgroesse), Kaesten in px aber nicht. Chrome hat dafuer
keinen Schalter; SCHRIFT macht dasselbe von Hand - jede berechnete
Schriftgroesse mal Faktor. Der Rahmen steht in em und waechst mit.

Aufbau wie test_stern.py: jeder Test mit eigenem Browserkontext im
Geraetemodus; die Bewegung (prefers-reduced-motion) ist immer ausdruecklich
gesetzt, sonst haengt das Ergebnis an der Einstellung des Rechners.

Seit dem 22.10.2026 (unten ab "Stufen"):
  - Stufen nach der laufenden Serie, Ajdin: "Mit Stufen" - unter 30 orange,
    ab 30 blau, ab 100 lila, ab 365 weissgold mit Funken. Die Glut behaelt
    die Farbe ihrer Stufe, der Aufbau ebenso. Funken nur, wenn die Flamme
    brennt und Bewegung erlaubt ist.
  - Dieselbe Flamme ueberall, Ajdin: "beachte das nicht das es 2
    verschiedene desgins sind": auch in der Statistik am Ende einer
    Lektion und einer Wiederholungsrunde, mit demselben Zustand, derselben
    Stufe und demselben Bild (flammeKlassen/flammeBild/flammeHtml), dort
    ebenfalls an den Pixeln auf Hoehe der Zahl gemessen. Aufgebaut wird
    nur oben.
"""
import base64
import datetime
import io
import json
import os
import re

import pytest
from conftest import WURZEL, Seite

# Alle Bilder der Flamme: die drei Zustaende und die Ebenen des Aufbaus.
BILDER = ["flamme", "glut", "aus", "kohle", "ebene_flaemmchen", "ebene_kohle_heiss",
          "ebene_rot", "ebene_orange", "ebene_gelb", "ebene_kern"]
BILD = {"an": "flamme/flamme.webp", "glut": "flamme/glut.webp", "aus": "flamme/aus.webp"}
# Rahmenhoehe oben (34 px neben Spectral 46 px) und in der Statistik
# (18 px neben Nunito 18 px), Seitenverhaeltnis 403:512
OBEN = 34
STATISTIK = 18
SEITEN = 403 / 512
# Die sichtbare Flamme reicht im Rahmen von Zeile 2 bis 190 (von 192)
FLAMME_ANTEIL = 188 / 192

GLUT_TAKT = """() => { const f = document.getElementById('serieFlamme'), a = f.getAnimations()[0];
  a.pause(); const aus = {};
  for(const p of [0, 0.35, 0.6]){ a.currentTime = p * 2200; const s = getComputedStyle(f);
    aus[p] = [s.filter, s.opacity]; }
  a.play(); return aus; }"""

FLAMME = """() => { const f = document.getElementById('serieFlamme'), s = getComputedStyle(f), b = f.parentElement,
  i = f.querySelector('.flammenbild'), r = b.getBoundingClientRect();
  return {klasse: f.className, aria: f.getAttribute('aria-hidden'), boxAria: b.getAttribute('aria-hidden'),
          text: f.textContent, bild: i.getAttribute('src'), alt: i.getAttribute('alt'),
          geladen: i.complete && i.naturalWidth > 0, sichtbar: getComputedStyle(i).visibility,
          rahmen: [r.left, r.top, r.width, r.height],
          zahl: document.getElementById('serieZahl').textContent,
          filter: s.filter, opacity: s.opacity, transform: s.transform,
          animation: s.animationName, dauer: s.animationDuration, wdh: s.animationIterationCount,
          laufend: f.getAnimations().map(a => a.animationName),
          stapel: f.querySelector('.gf') ? [...f.querySelectorAll('.gf img')].map(x => x.className) : null,
          noAnim: document.body.classList.contains('no-anim'),
          alle: document.querySelectorAll('.flamme').length}; }"""

# Die Animationen des Aufbaus (im Stapel unter #serieFlamme), mit Dauer.
AUFBAU = """() => { const f = document.getElementById('serieFlamme');
  return document.getAnimations().filter(a => a.effect && a.effect.target !== f && f.contains(a.effect.target))
    .map(a => [a.animationName, a.effect.getTiming().duration]); }"""

# Den Aufbau auf t ms stellen und anhalten.
ANHALTEN = """(t) => { const f = document.getElementById('serieFlamme');
  const an = document.getAnimations().filter(a => a.effect && a.effect.target !== f && f.contains(a.effect.target));
  an.forEach(a => { a.pause(); a.currentTime = t; }); return an.length; }"""
WEITER = """() => { const f = document.getElementById('serieFlamme');
  document.getAnimations().filter(a => a.effect && f.contains(a.effect.target)).forEach(a => a.play()); }"""

# Die erste Lektion des Tages, kurz: markToday() wie am Ende einer Lektion,
# dann zurueck auf die Startseite. Der Test mit der echten Lektion steht
# weiter unten (test_aufbau_nach_der_ersten_lektion).
ERSTE_LEKTION = """() => { markToday(); homeMode = 'words'; showHome();
  const f = document.getElementById('serieFlamme');
  return {klasse: f.className, bild: f.querySelector('.flammenbild').getAttribute('src'),
          stapel: f.querySelector('.gf') ? [...f.querySelectorAll('.gf img')].map(x => x.className) : null}; }"""

FERTIG = "() => !document.getElementById('serieFlamme').classList.contains('auf')"

# Wie Android "Schriftgroesse": jede berechnete Schriftgroesse mal f. Erst alle
# lesen, dann schreiben - sonst rechnete ein Kind mit der schon vergroesserten
# Groesse seiner Eltern noch einmal.
SCHRIFT = """(f) => { const els = [...document.querySelectorAll('body *')];
  const g = els.map(e => parseFloat(getComputedStyle(e).fontSize));
  els.forEach((e, i) => e.style.fontSize = (g[i] * f) + 'px'); }"""

# Nur eines von beiden sichtbar, alles andere unsichtbar (auch Festschmuck,
# Drache und die Funken der Gold-Stufe). Die Flamme ohne Filter: gemessen
# wird, wo sie steht, nicht wie weit ihr Schein reicht.
# f und z sind die ids von Flamme und Zahl. In der Statistik ist die Zahl
# kein eigenes Element, nur Text im <b> neben der Flamme: das <b> wird
# sichtbar, sein Kind (der Kasten der Flamme) bleibt es nicht, der Text erbt.
MESS_STIL = """([art, f, z]) => { let s = document.getElementById('messStil');
  if(!s){ s = document.createElement('style'); s.id = 'messStil'; document.head.appendChild(s); }
  const T = {
    flamme: 'body *{visibility:hidden!important} #' + f + ', #' + f + ' *{visibility:visible!important}'
            + ' #' + f + '{filter:none!important}',
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
  return {flamme: box(await lade(bilder.flamme)), zahl: box(await lade(bilder.zahl))};
}"""

# Zwei Bildschirmfotos Pixel fuer Pixel: groesster Unterschied eines
# Farbkanals und wie viele Pixel um mehr als 32 abweichen.
VERGLEICH = """async ([a, b]) => {
  const lade = async s => { const img = new Image(); img.src = 'data:image/png;base64,' + s; await img.decode();
    const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
    const x = c.getContext('2d'); x.drawImage(img, 0, 0); return x.getImageData(0, 0, c.width, c.height); };
  const A = await lade(a), B = await lade(b); let max = 0, viele = 0;
  for(let i = 0; i < A.data.length; i += 4){
    const d = Math.max(Math.abs(A.data[i] - B.data[i]), Math.abs(A.data[i+1] - B.data[i+1]),
                       Math.abs(A.data[i+2] - B.data[i+2]));
    if(d > max) max = d; if(d > 32) viele++; }
  return {max, viele, pixel: A.data.length / 4}; }"""


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


def _messen(seite, dpr, kasten=".seriezahl", f="serieFlamme", z="serieZahl"):
    """Pixel von Flamme und Zahl, dazu der Rahmen (der Kasten der Flamme) -
    alles in CSS-px ab der Oberkante des Fotos."""
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
    m = seite.js(ZEILEN, [bilder, dpr])
    oben, hoehe, breite = seite.js("(f) => { const r = document.getElementById(f).parentElement.getBoundingClientRect();"
                                   " return [r.top, r.height, r.width]; }", f)
    m["rahmen"] = {"oben": oben - r["y"], "unten": oben - r["y"] + hoehe, "hoehe": hoehe, "breite": breite,
                   "mitte": oben - r["y"] + hoehe / 2}
    return m


def _foto(seite, rand=12):
    """Bildschirmfoto rund um den Rahmen oben, ohne die Zahl daneben - und
    ohne die Funken des Funkenflugs (24.10.2026): Sie setzen gleich nach dem
    Aufbau ein, verglichen wird hier aber das Bild der Flamme. Die Funken
    prueft test_funken.py."""
    r = seite.js("""(rand) => { const r = document.querySelector('.seriezahl .flammenbox').getBoundingClientRect();
        let s = document.getElementById('ohneFunken');
        if(!s){ s = document.createElement('style'); s.id = 'ohneFunken'; document.head.appendChild(s); }
        s.textContent = '.fk{visibility:hidden!important}';
        return {x: r.left - rand, y: r.top - rand, width: r.width + rand + 4, height: r.height + 2 * rand}; }""", rand)
    bild = base64.b64encode(seite.page.screenshot(clip=r)).decode("ascii")
    seite.js("() => { document.getElementById('ohneFunken').textContent = ''; }")
    return bild


# ---------------------------------------------------------------------------
# Die drei Zustaende: je ein Bild im selben Rahmen
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("zustand,zahl", [("aus", "0"), ("glut", "7"), ("an", "8")])
def test_zustand_zeigt_sein_bild(browser, basis, heute_stand, zustand, zahl):
    """aus: kalte Kohle, grau, still. glut: gluehende Kohlen, flackern in
    der Helligkeit (2,2 s, endlos). an: die Flamme, ohne Filter. Alle drei
    in voller Deckkraft und ohne Verschiebung oder Verkleinerung."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, zustand)
        seite.page.wait_for_function("() => document.querySelector('#serieFlamme .flammenbild').complete")
        f = seite.js(FLAMME)
        assert f["zahl"] == zahl
        assert f["klasse"].split() == ["flamme"] + ([zustand] if zustand != "an" else [])
        assert f["bild"] == BILD[zustand] and f["geladen"] and f["sichtbar"] == "visible"
        assert f["opacity"] == "1" and f["transform"] == "none" and f["stapel"] is None
        if zustand == "aus":
            assert f["filter"] == "grayscale(1)" and f["laufend"] == []
        elif zustand == "glut":
            assert f["animation"] == "flammeGlut" and f["dauer"] == "2.2s" and f["wdh"] == "infinite"
            assert f["laufend"] == ["flammeGlut"]
            # an drei Stellen des Takts abgelesen
            werte = seite.js(GLUT_TAKT)
            assert werte["0"] == ["brightness(1)", "1"]
            assert werte["0.35"] == ["brightness(0.9)", "1"]
            assert werte["0.6"] == ["brightness(1.18)", "1"]
        else:
            assert f["filter"] == "none" and f["laufend"] == []
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


def test_rahmen_in_allen_zustaenden_gleich(browser, basis, heute_stand):
    """Derselbe Rahmen in allen drei Zustaenden: gleiche Lage, gleiche
    Groesse (34 px hoch, 403:512). Die drei Bilder und alle Ebenen haben
    dasselbe Format, die Kohlen liegen also an derselben Stelle im Rahmen,
    an der die Flamme ihren Fuss hat."""
    rahmen = {}
    for zustand in ("aus", "glut", "an"):
        ctx, seite = _kontext(browser, basis)
        try:
            _starten(seite, heute_stand, zustand)
            _vorspann_weg(seite)
            rahmen[zustand] = seite.js(FLAMME)["rahmen"]
            groessen = seite.js("""() => Promise.all(flammeVorrat.map(i => i.decode().then(() =>
                [i.getAttribute('src'), i.naturalWidth, i.naturalHeight])))""")
            assert all(g[1:] == [151, 192] for g in groessen), groessen
            assert seite.fehler == []
        finally:
            ctx.close()
    # Die Zahl ist ueberall einstellig (0, 7, 8): links und oben gleich
    assert rahmen["aus"] == rahmen["glut"] == rahmen["an"], rahmen
    _, _, breite, hoehe = rahmen["an"]
    assert abs(hoehe - OBEN) <= 0.05 and abs(breite / hoehe - SEITEN) <= 0.005, rahmen
    print("Rahmen", json.dumps(rahmen))


def test_barrierefreiheit_unveraendert(browser, basis, heute_stand):
    """Die Flamme bleibt Schmuck fuer Bildschirmleser: Kasten und Flamme mit
    aria-hidden, das Bild mit alt="". Nach dem Start gibt es sie einmal (die
    Statistik am Lektionsende kommt erst mit der Lektion), und vorgelesen
    wird weiter die Zahl. Kein Emoji mehr."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "glut")
        f = seite.js(FLAMME)
        assert f["aria"] == "true" and f["boxAria"] == "true" and f["alt"] == "" and f["alle"] == 1
        assert f["text"] == ""
        assert seite.js("() => document.getElementById('serieZahl').getAttribute('aria-hidden')") is None
        assert seite.fehler == []
    finally:
        ctx.close()


def test_bilder_beim_start_vorgeladen(browser, basis, heute_stand):
    """Alle zehn Bilder (drei Zustaende, sieben Ebenen des Aufbaus) holt die
    App einmal beim Start, nur vom eigenen Ursprung - beim ersten Wechsel
    laedt nichts nach. Die Liste in der App deckt genau den Ordner
    web/flamme ab."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "an")
        assert sorted(seite.js("() => FLAMME_BILDER")) == sorted(BILDER)
        seite.page.wait_for_function("() => flammeVorrat.every(i => i.complete && i.naturalWidth > 0)", timeout=5000)
        geholt = seite.js("""() => performance.getEntriesByType('resource').map(e => e.name)
            .filter(n => n.includes('/flamme/'))""")
        assert sorted({n.rsplit("/", 1)[1] for n in geholt}) == sorted(b + ".webp" for b in BILDER), geholt
        assert all(n.startswith(seite.basis) for n in geholt)
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()
    im_ordner = sorted(n[:-5] for n in os.listdir(os.path.join(WURZEL, "web", "flamme")) if n.endswith(".webp"))
    assert im_ordner == sorted(BILDER)


# ---------------------------------------------------------------------------
# Der Aufbau Glut -> Flamme: nur beim Wechsel in der Sitzung
# ---------------------------------------------------------------------------

def test_kein_aufbau_beim_start(browser, basis, heute_stand):
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
            assert "auf" not in f["klasse"].split() and f["stapel"] is None, (schritt, f)
            assert f["bild"] == BILD["an"] and seite.js(AUFBAU) == [], schritt
        assert seite.fehler == []
    finally:
        ctx.close()


# Die Ebenen des Stapels, von unten nach oben. Aus kalter Kohle: kein
# Flaemmchen, dafuer die graue Kohle obenauf.
STAPEL = {"glut": ["gf-flaemmchen", "gf-kohle", "gf-heiss", "gf-rot", "gf-orange", "gf-gelb", "gf-kern"],
          "aus": ["gf-kohle", "gf-heiss", "gf-asche", "gf-rot", "gf-orange", "gf-gelb", "gf-kern"]}


@pytest.mark.parametrize("vorher", ["aus", "glut"])
def test_aufbau_nach_der_ersten_lektion(browser, basis, heute_stand, vorher):
    """Eine echte Lektion, dann "Zurueck zum Lernpfad": die Flamme baut sich
    einmal auf - der Stapel aus Ebenen, alle Teile 1,5 s, das eine Bild so
    lange versteckt (es traegt schon flamme.webp). Danach ist der Stapel weg
    und das Bild steht da. Ein zweiter Besuch der Startseite loest nichts
    mehr aus."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, vorher)
        assert seite.js(FLAMME)["klasse"].split() == ["flamme", vorher]
        seite.js("() => { openLevel(0); startLesson(); }")
        seite.durchspielen("lBody", "Lx")
        seite.js("() => document.getElementById('lPfad').click()")
        f = seite.js(FLAMME)
        assert f["klasse"].split() == ["flamme", "auf"], f
        assert f["stapel"] == STAPEL[vorher], f
        assert f["bild"] == BILD["an"] and f["sichtbar"] == "hidden"
        teile = seite.js(AUFBAU)
        assert {n for n, _ in teile} >= {"gfHeiss", "gfKern", "gfGelb", "gfOrange", "gfRot", "gfLodern", "gfGlut"}, teile
        assert ("gfAsche" in {n for n, _ in teile}) is (vorher == "aus")
        assert {d for _, d in teile} == {1500}, teile
        # animationend von gfLodern nimmt Stapel und .auf wieder weg
        seite.page.wait_for_function(FERTIG, timeout=4000)
        f = seite.js(FLAMME)
        assert f["klasse"].split() == ["flamme"] and f["stapel"] is None and f["filter"] == "none"
        assert f["bild"] == BILD["an"] and f["sichtbar"] == "visible" and seite.js(AUFBAU) == []
        seite.js("() => { document.getElementById('modeStories').click(); document.getElementById('modeWords').click(); }")
        f = seite.js(FLAMME)
        assert f["klasse"].split() == ["flamme"] and f["stapel"] is None
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


@pytest.mark.parametrize("weg", ["schalter", "geraet"])
def test_ohne_animationen_steht_alles_still(browser, basis, heute_stand, weg):
    """Schalter "Animationen" aus oder "Bewegung reduzieren" am Geraet: die
    Glut steht als ruhiges Bild da, und nach der ersten Lektion steht sofort
    die Flamme - kein Stapel, kein Ablauf."""
    ctx, seite = _kontext(browser, basis, bewegung="reduce" if weg == "geraet" else "no-preference")
    try:
        _starten(seite, heute_stand, "glut", animationen=(weg != "schalter"))
        f = seite.js(FLAMME)
        assert f["noAnim"] is (weg == "schalter")
        assert f["klasse"].split() == ["flamme", "glut"] and f["bild"] == BILD["glut"]
        assert f["animation"] == "none" and f["laufend"] == []
        assert f["filter"] == "brightness(1)" and f["opacity"] == "1"
        nachher = seite.js(ERSTE_LEKTION)
        assert nachher == {"klasse": "flamme", "bild": BILD["an"], "stapel": None}, nachher
        assert seite.js(AUFBAU) == []
        assert seite.fehler == []
    finally:
        ctx.close()


def test_mit_animationen_baut_auch_der_kurzweg(browser, basis, heute_stand):
    """Gegenprobe zu oben mit demselben Kurzweg (markToday + showHome)."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "glut")
        nachher = seite.js(ERSTE_LEKTION)
        assert nachher["klasse"].split() == ["flamme", "auf"] and nachher["stapel"] == STAPEL["glut"], nachher
        assert "gfLodern" in [n for n, _ in seite.js(AUFBAU)]
        seite.page.wait_for_function(FERTIG, timeout=4000)
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("vorher", ["aus", "glut"])
def test_aufbau_ohne_sprung(browser, basis, heute_stand, vorher):
    """Der Aufbau beginnt genau im Bild davor (Glut bzw. kalte Kohle) und
    endet genau in flamme.webp, gegen das der Stapel dann getauscht wird:
    Pixel fuer Pixel verglichen, bei Pixeldichte 2. Kleine Abweichungen
    kommen nur vom Uebereinanderlegen der einzeln gespeicherten Ebenen:
    am 24.10.2026 hoechstens 55 in einem Farbkanal, an 10 von 9576 Pixeln
    ueber 32, alle auf dem Umriss. Ein falsches Bild oder ein Versatz um
    ein Pixel aendert Tausende."""
    ctx, seite = _kontext(browser, basis, dpr=2)
    try:
        _starten(seite, heute_stand, vorher)
        _vorspann_weg(seite)
        if vorher == "glut":   # das Flackern anhalten, wo es bei brightness(1) steht
            seite.js("() => { const a = document.getElementById('serieFlamme').getAnimations()[0];"
                     " a.pause(); a.currentTime = 0; }")
        seite.page.wait_for_timeout(50)
        davor = _foto(seite)
        seite.js(ERSTE_LEKTION)
        assert seite.js(ANHALTEN, 0) >= 10
        seite.page.wait_for_timeout(50)
        anfang = _foto(seite)
        seite.js(ANHALTEN, 1499.9)
        seite.page.wait_for_timeout(50)
        ende = _foto(seite)
        seite.js(WEITER)
        seite.page.wait_for_function(FERTIG, timeout=3000)
        seite.page.wait_for_timeout(50)
        danach = _foto(seite)
        vorn = seite.js(VERGLEICH, [davor, anfang])
        hinten = seite.js(VERGLEICH, [ende, danach])
        for v in (vorn, hinten):
            assert v["max"] <= 64 and v["viele"] <= 0.002 * v["pixel"], (vorn, hinten)
        assert seite.fehler == []
    finally:
        ctx.close()
    print("ohne Sprung", vorher, json.dumps({"anfang": vorn, "ende": hinten}))


@pytest.mark.parametrize("wie", ["startseite_weg", "animationen_aus"])
def test_unterbrochener_aufbau_wird_fertig(browser, basis, heute_stand, wie):
    """Verschwindet die Startseite mitten im Aufbau (gleich ins naechste
    Level) oder werden die Animationen mittendrin ausgeschaltet, kommt kein
    animationend. Das Sicherheitsnetz (flammeWache) raeumt den Stapel
    trotzdem weg - sonst stuende er still in seinem ersten Bild, Glut statt
    Flamme."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, heute_stand, "glut")
        assert seite.js(ERSTE_LEKTION)["stapel"] == STAPEL["glut"]
        if wie == "startseite_weg":
            seite.js("() => openLevel(0)")
        else:
            seite.js("() => document.body.classList.add('no-anim')")
        seite.page.wait_for_function("() => !document.querySelector('#serieFlamme .gf')", timeout=5000)
        seite.js("() => showHome()")
        f = seite.js(FLAMME)
        assert f["klasse"].split() == ["flamme"] and f["stapel"] is None
        assert f["bild"] == BILD["an"] and f["sichtbar"] == "visible"
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Rahmen und Zahl auf einer Hoehe
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("zustand", ["aus", "glut", "an"])
def test_rahmen_mittig_zur_zahl(browser, basis, heute_stand, zustand):
    """Die Mitte des Rahmens auf der sichtbaren Mitte der Ziffern, bei
    normaler Schrift, 130 % und 200 % (Toleranz 1,5 px). Der Rahmen waechst
    mit der Schrift (34 px mal Faktor). Die brennende Flamme fuellt ihn:
    ihre sichtbare Mitte steht ebenso auf der Mitte der Ziffern. Glut und
    kalte Kohle liegen unten im Rahmen, ihre Unterkante auf seiner."""
    dpr = 2
    ctx, seite = _kontext(browser, basis, dpr=dpr)
    funde = {}
    try:
        _starten(seite, heute_stand, zustand)
        _vorspann_weg(seite)
        groesse = 1.0
        for faktor in (1.0, 1.3, 2.0):
            if faktor != groesse:
                seite.js(SCHRIFT, faktor / groesse)
                groesse = faktor
            m = _messen(seite, dpr)
            funde[faktor] = m
            rahmen, bild, zahl = m["rahmen"], m["flamme"], m["zahl"]
            assert abs(rahmen["mitte"] - zahl["mitte"]) <= 1.5, (zustand, faktor, m)
            assert abs(rahmen["hoehe"] - OBEN * faktor) <= 0.1, (zustand, faktor, m)
            if zustand == "an":
                assert abs(bild["mitte"] - zahl["mitte"]) <= 1.5, (zustand, faktor, m)
                assert abs(bild["hoehe"] - FLAMME_ANTEIL * rahmen["hoehe"]) <= 1.5, (zustand, faktor, m)
            else:
                assert abs(bild["unten"] - rahmen["unten"]) <= 1.5, (zustand, faktor, m)
                assert bild["mitte"] > zahl["mitte"] + 0.15 * rahmen["hoehe"], (zustand, faktor, m)
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()
    print(zustand, json.dumps({k: [round(v["rahmen"]["mitte"] - v["zahl"]["mitte"], 2),
                                   round(v["flamme"]["mitte"] - v["zahl"]["mitte"], 2)] for k, v in funde.items()}))


def test_aufbau_bleibt_im_rahmen(browser, basis, heute_stand):
    """Waehrend des Aufbaus (angehalten bei 0,75 s) steht der Stapel genau im
    Rahmen, und der Rahmen genau da, wo vorher die Glut stand - auch bei
    grosser Schrift."""
    ctx, seite = _kontext(browser, basis, dpr=2)
    try:
        _starten(seite, heute_stand, "glut")
        _vorspann_weg(seite)
        seite.js(SCHRIFT, 1.3)
        vorher = seite.js(FLAMME)["rahmen"]
        assert seite.js(ERSTE_LEKTION)["stapel"] == STAPEL["glut"]
        seite.js(ANHALTEN, 750)
        lage = seite.js("""() => { const f = document.getElementById('serieFlamme');
            const r = e => { const x = e.getBoundingClientRect(); return [x.left, x.top, x.width, x.height]; };
            return {rahmen: r(f.parentElement), stapel: r(f.querySelector('.gf')), kohle: r(f.querySelector('.gf-kohle'))}; }""")
        assert lage["rahmen"] == vorher == lage["stapel"] == lage["kohle"], (vorher, lage)
        seite.js(WEITER)
        seite.page.wait_for_function(FERTIG, timeout=3000)
        assert seite.js(FLAMME)["rahmen"] == vorher
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
# sie ausschreibt. Der Schein ist 0,2 (Gold 0,3) Rahmenhoehen weit.
TON = {"": "", "blau": "hue-rotate(190deg) saturate(1.35) ", "lila": "hue-rotate(245deg) saturate(1.45) ",
       "gold": "saturate(0.45) brightness(1.3) "}
SCHEIN = {"blau": "rgba(60, 150, 255, 0.55)", "lila": "rgba(170, 90, 255, 0.55)", "gold": "rgba(255, 214, 90, 0.9)"}
WEITE = {"blau": 0.2, "lila": 0.2, "gold": 0.3}
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

# Der Kasten als HTML, bei den Funken des Funkenflugs (.fk) ohne das, was
# jeder Funke bei jeder Runde neu wuerfelt (die Schluessel von
# FUNKEN_BEREICH; 24.10.2026, test_funken.py). Gleich sein muessen Aufbau,
# Klassen, Bild, die Zahl der Funken und ihre Dauer und Verzoegerung.
OHNE_WURF = """const ohneWurf = h => { const t = document.createElement('template');
  t.innerHTML = typeof h === 'string' ? h : h.outerHTML;
  t.content.querySelectorAll('.fk').forEach(x => Object.keys(FUNKEN_BEREICH).forEach(k => x.style.removeProperty('--' + k)));
  return t.innerHTML; };"""

# Die Flamme in der Statistik am Ende (Lektion oder Wiederholungsrunde), und
# was flammeKlassen() gerade sagt.
STAT_FLAMME = """() => { """ + OHNE_WURF + """
  const f = document.querySelector('#lBody .stat .flamme'), s = getComputedStyle(f), b = f.parentElement,
  i = f.querySelector('.flammenbild'), r = b.getBoundingClientRect();
  return {klasse: f.className, soll: flammeKlassen(), filter: s.filter, laufend: f.getAnimations().map(a => a.animationName),
          box: b.className, aria: b.getAttribute('aria-hidden'), text: f.textContent, zahl: f.closest('b').textContent,
          bild: i.getAttribute('src'), alt: i.getAttribute('alt'), hoehe: r.height, breite: r.width,
          gleich: ohneWurf(b) === ohneWurf(flammeHtml()), funken: b.querySelectorAll('.funke').length,
          stapel: !!f.querySelector('.gf')}; }"""

# Der Kasten oben ohne seine id - so muss ihn flammeHtml() bauen. Dazu der
# Kasten in der Statistik, beide ohne das Gewuerfelte der Funken.
OBEN_HTML = ("""() => { """ + OHNE_WURF + """
  return ohneWurf(document.getElementById('serieFlamme').parentElement.outerHTML.replace(' id="serieFlamme"', '')); }""")
STAT_HTML = """() => { """ + OHNE_WURF + """ return ohneWurf(document.querySelector('#lBody .stat .flammenbox')); }"""

# Das Ende einer Wiederholungsrunde, ohne die Runde: topfEnde() mit einer
# leeren Runde. Es setzt den Lerntag wie das Ende einer Lektion.
TOPF_ENDE = """() => { showView('levelView');
  for(const [id, an] of [['levelHome', 'none'], ['test', 'none'], ['lesson', 'block']]) document.getElementById(id).style.display = an;
  Lx = {queue: [], i: 0, results: [], right: 0, total: 0, skipped: 0, newWords: new Set(), retried: new Set(),
        topf: true, quelle: 'topf'};
  topfEnde(); }"""


def _schein(filter_, stufe, hoehe):
    """Der stille Schein der Stufe: erst ihr Farbfilter, dann drop-shadow in
    ihrer Farbe, so weit wie WEITE Rahmenhoehen."""
    m = re.fullmatch(re.escape(TON[stufe] + "drop-shadow(" + SCHEIN[stufe]) + r" 0px 0px ([0-9.]+)px\)", filter_)
    return bool(m) and abs(float(m.group(1)) - WEITE[stufe] * hoehe) <= 0.05


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
    gemalt), als Glut in der Farbe der Stufe: ihr Farbfilter steht vor dem
    der Glut, in jedem Schritt des Flackerns. Das Bild ist je Zustand
    dasselbe, nur gefaerbt. Die Zahl ist die Serie."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, tage, zustand)
        f = seite.js(FLAMME)
        assert f["zahl"] == str(tage)
        soll = ["flamme"] + (["glut"] if zustand == "glut" else []) + (["stufe-" + stufe] if stufe else [])
        assert f["klasse"].split() == soll
        assert f["bild"] == BILD[zustand] and f["opacity"] == "1"
        ton = TON[stufe]
        if zustand == "an":
            assert f["laufend"] == []
            if stufe:
                assert _schein(f["filter"], stufe, f["rahmen"][3]), f["filter"]
            else:
                assert f["filter"] == "none"
        else:
            assert f["laufend"] == ["flammeGlut"]
            werte = seite.js(GLUT_TAKT)
            assert werte["0"] == [ton + "brightness(1)", "1"]
            assert werte["0.35"] == [ton + "brightness(0.9)", "1"]
            assert werte["0.6"] == [ton + "brightness(1.18)", "1"]
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
        assert f["filter"] == TON["lila"] + "brightness(1)" and f["opacity"] == "1"
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
            assert abs(m["rahmen"]["mitte"] - m["zahl"]["mitte"]) <= 1.5, (faktor, m)
            assert abs(m["flamme"]["mitte"] - m["zahl"]["mitte"]) <= 1.5, (faktor, m)
            assert abs(m["rahmen"]["hoehe"] - OBEN * faktor) <= 0.1, (faktor, m)
        assert seite.fehler == []
    finally:
        ctx.close()
    print("gold", json.dumps({k: round(v["flamme"]["mitte"] - v["zahl"]["mitte"], 2) for k, v in funde.items()}))


# ---------------------------------------------------------------------------
# Dieselbe Flamme ueberall (22.10.2026)
# ---------------------------------------------------------------------------

def test_lektionsende_und_startseite_zeigen_dieselbe_flamme(browser, basis, heute_stand):
    """29 Tage bis gestern: oben eine orange Glut. Eine echte Lektion macht
    daraus 30 - die Statistik am Lektionsende zeigt die blaue Flamme,
    brennend, ohne Aufbau, gebaut von flammeHtml(). Zurueck auf der
    Startseite baut sie sich auf, schon in Blau (der Filter liegt auf dem
    Stapel), und brennt danach mit genau denselben Klassen, demselben Bild
    und demselben Aufbau des Kastens wie in der Statistik."""
    ctx, seite = _kontext(browser, basis)
    try:
        seite.starten(stand=heute_stand(tage=_serie_tage(29, "glut")))
        assert seite.js(FLAMME)["klasse"].split() == ["flamme", "glut"]
        seite.js("() => { openLevel(0); startLesson(); }")
        seite.durchspielen("lBody", "Lx")
        st = seite.js(STAT_FLAMME)
        assert st["klasse"] == st["soll"] == "flamme stufe-blau", st
        assert st["laufend"] == [] and _schein(st["filter"], "blau", st["hoehe"]), st
        assert st["box"] == "flammenbox" and st["aria"] == "true" and st["text"] == "" and st["funken"] == 3
        assert st["bild"] == BILD["an"] and st["alt"] == "" and not st["stapel"]
        assert abs(st["hoehe"] - STATISTIK) <= 0.05 and abs(st["breite"] / st["hoehe"] - SEITEN) <= 0.005, st
        assert st["gleich"] and st["zahl"].strip().endswith(" 30"), st
        stat_html = seite.js(STAT_HTML)
        seite.js("() => document.getElementById('lPfad').click()")
        f = seite.js(FLAMME)
        assert f["klasse"].split() == ["flamme", "stufe-blau", "auf"] and f["stapel"] == STAPEL["glut"], f
        assert _schein(f["filter"], "blau", f["rahmen"][3]), f["filter"]
        seite.page.wait_for_function(FERTIG, timeout=4000)
        f = seite.js(FLAMME)
        assert f["klasse"] == st["klasse"] and f["zahl"] == "30" and f["bild"] == st["bild"]
        assert _schein(f["filter"], "blau", f["rahmen"][3]), f["filter"]
        assert seite.js(OBEN_HTML) == stat_html
        # Die Statistik hat sich nicht aufgebaut und tut es auch jetzt nicht
        assert seite.js("() => document.querySelector('#lBody .stat .flamme').getAnimations().length") == 0
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("tage,stufe", [(29, "blau"), (364, "gold")])
def test_wiederholungsrunde_zeigt_dieselbe_flamme(browser, basis, tage, stufe):
    """Das Ende einer Wiederholungsrunde (topfEnde) setzt den Lerntag wie eine
    Lektion: 29 -> 30 blau, 364 -> 365 gold. Die Statistik zeigt dieselbe
    Flamme wie danach die Startseite, ohne Aufbau; in Gold funkeln die
    Funken dort ebenso."""
    ctx, seite = _kontext(browser, basis)
    try:
        _serie_starten(seite, tage, "glut")
        seite.js(TOPF_ENDE)
        st = seite.js(STAT_FLAMME)
        assert st["klasse"] == st["soll"] == "flamme stufe-" + stufe, st
        assert st["laufend"] == [] and st["gleich"] and st["zahl"].strip().endswith(" " + str(tage + 1)), st
        assert st["bild"] == BILD["an"] and not st["stapel"]
        funken = seite.js(FUNKEN, "#lBody .stat")
        laeuft = [["flammeFunke"]] * 3 if stufe == "gold" else [[]] * 3
        assert [x["laufend"] for x in funken] == laeuft, funken
        stat_html = seite.js(STAT_HTML)
        oben = seite.js("() => { showHome(); return document.getElementById('serieFlamme').className; }")
        assert oben.split() == ["flamme", "stufe-" + stufe, "auf"]
        f = seite.js(FLAMME)
        assert f["stapel"] == STAPEL["glut"] and _schein(f["filter"], stufe, f["rahmen"][3]), f
        seite.page.wait_for_function(FERTIG, timeout=4000)
        assert seite.js("() => document.getElementById('serieFlamme').className") == st["klasse"]
        assert seite.js(OBEN_HTML) == stat_html
        assert seite.fehler == []
    finally:
        ctx.close()


def test_statistik_flamme_und_zahl_auf_einer_hoehe(browser, basis, heute_stand):
    """Die Flamme in der Statistik am Lektionsende neben ihrer Zahl (Nunito
    18 px): die Mitte des Rahmens und die sichtbare Mitte der Flamme auf der
    sichtbaren Mitte der Ziffern, bei 100, 130 und 200 % Schrift (Toleranz
    1,5 px). Das Fenster ist hoch genug, dass die Statistik auch bei
    doppelter Schrift ganz darin steht."""
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
        groesse = 1.0
        for faktor in (1.0, 1.3, 2.0):
            if faktor != groesse:
                seite.js(SCHRIFT, faktor / groesse)
                groesse = faktor
            seite.page.wait_for_timeout(50)
            m = _messen(seite, dpr, "#messZahl", "messFlamme", "messZahl")
            funde[faktor] = m
            assert abs(m["rahmen"]["mitte"] - m["zahl"]["mitte"]) <= 1.5, (faktor, m)
            assert abs(m["flamme"]["mitte"] - m["zahl"]["mitte"]) <= 1.5, (faktor, m)
            assert abs(m["rahmen"]["hoehe"] - STATISTIK * faktor) <= 0.1, (faktor, m)
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()
    print("statistik", json.dumps({k: [round(v["rahmen"]["mitte"] - v["zahl"]["mitte"], 2),
                                       round(v["flamme"]["mitte"] - v["zahl"]["mitte"], 2),
                                       round(v["zahl"]["hoehe"], 2)] for k, v in funde.items()}))
