# -*- coding: utf-8 -*-
"""Der Serienschutz unter der Serie, Entwurf B "zwei Plaetze" (24.10.2026).

Ajdin am 23.10.2026 ueber die alte Zeile "❄ 1 Schutz · noch 9 Tage bis zum
naechsten": sie ist "nackt". Gewaehlt hat er Entwurf B ("Nimm B sieht am
besten aus"): zwei Schilde nebeneinander (SCHUTZ_MAX), gefuellt =
vorhanden, blass = noch nicht da; der naechste leere Platz friert von unten
zu, Tag fuer Tag (SCHUTZ_TAGE = 10). Daneben kurz "1 Schutz" und "noch 9
Tage" bzw. "voll". Die Meldungen "gerettet" und "gerissen" stehen als
Sprechblase des Drachen darunter. Das Schild ist das gemalte
web/symbole/serienschutz.webp; die Schneeflocke ist aus allen acht Sprachen
heraus.

Geprueft wird:
  - 0, 1 und 2 Schutz: welche Plaetze voll, zufrierend oder leer sind,
    der Text daneben, was der Bildschirmleser liest ("1 Schutz, noch 9
    Tage"), Schilde nur als Schmuck (aria-hidden, alt="");
  - der Fortschritt Tag fuer Tag, an den Pixeln: das Eis waechst von unten,
    der blasse Platz hat keine Farbe, das volle Schild am meisten;
  - die Sprechblasen "gerettet" (ein und zwei Tage) und "gerissen", ihr
    Zipfel unter dem Drachen, der Festgruss darunter statt dazwischen;
  - hell und dunkel ohne Skriptfehler, ohne fremde Anfragen und ohne
    ernsten axe-Fund;
  - alle acht Sprachen: keine Schneeflocke, nichts ragt ueber den Rand,
    und der Drache bleibt 120 px breit - auch bei 130 % Schrift und 320 px.

Die Uhr steht fest (10.11.2026, 12 Uhr, kein Fest), damit "noch 9 Tage"
nicht an der Sekunde haengt. Gemessen wird nur an Bildern, nicht an
Schriften - so laeuft alles auch in der CI unter Linux.
"""
import base64
import datetime
import os
import re

import pytest
from conftest import Seite

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXE = os.path.join(WURZEL, "tests_e2e", "vendor", "axe.min.js")

JETZT = datetime.datetime(2026, 11, 10, 12, 0)
TAG = 86400000
BILD = "symbole/serienschutz.webp"
SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]

# Was auf der Startseite zum Serienschutz steht.
ZEILE = """() => { const z = document.getElementById('streakLine'), m = document.getElementById('schutzMeldung');
  const pl = [...z.querySelectorAll('.schutzplatz')];
  return {
    text: z.textContent, b: z.querySelector('.schutztext b').textContent,
    small: z.querySelector('.schutztext small') ? z.querySelector('.schutztext small').textContent : null,
    smallKlasse: z.querySelector('.schutztext small') ? z.querySelector('.schutztext small').className : null,
    smallFarbe: z.querySelector('.schutztext small') ? getComputedStyle(z.querySelector('.schutztext small')).color : null,
    plaetze: pl.map(p => p.className.replace('schutzplatz', '').trim()),
    tage: pl.map(p => p.dataset.tage === undefined ? null : Number(p.dataset.tage)),
    zu: pl.map(p => p.style.getPropertyValue('--zu') || null),
    ariaPlaetze: z.querySelector('.schutzplaetze').getAttribute('aria-hidden'),
    bilder: [...z.querySelectorAll('img')].map(i => ({src: i.getAttribute('src'), alt: i.getAttribute('alt'),
      klasse: i.className, geladen: i.complete && i.naturalWidth > 0,
      filter: getComputedStyle(i).filter, clip: getComputedStyle(i).clipPath})),
    leser: getComputedStyle(z.querySelector('.nurleser') || z).clipPath,
    blase: {hidden: m.hidden, anzeige: getComputedStyle(m).display, klasse: m.className, text: m.textContent,
            bild: m.querySelector('.bild img') ? m.querySelector('.bild img').getAttribute('src') : null,
            bildGeladen: m.querySelector('.bild img') ? m.querySelector('.bild img').complete && m.querySelector('.bild img').naturalWidth > 0 : null,
            bildAria: m.querySelector('.bild') ? m.querySelector('.bild').getAttribute('aria-hidden') : null,
            kohle: m.querySelector('.kohle') ? getComputedStyle(m.querySelector('.kohle')).backgroundImage : null,
            kohleAria: m.querySelector('.kohle') ? m.querySelector('.kohle').getAttribute('aria-hidden') : null},
    zahl: document.getElementById('serieZahl').textContent,
    pfad: document.getElementById('pfad').textContent};
}"""


def _tage(von, bis):
    """Lerntage von JETZT aus gezaehlt: 0 = heute, 1 = gestern."""
    return [(JETZT.date() - datetime.timedelta(days=i)).isoformat() for i in range(von, bis)]


def _stand(tage, anzahl, um_tage=None):
    """um_tage: so viele Tage ist es her, dass der letzte Schutz verbraucht
    wurde bzw. der Platz zu frieren begann (zeit). None = zeit 0 (voll)."""
    ms = int(JETZT.timestamp() * 1000)
    zeit = 0 if um_tage is None else int(ms - um_tage * TAG)
    return {"einstufung": {"tag": JETZT.date().isoformat(), "wahl": "neu", "bis": ""},
            "tage": tage, "schutz": {"anzahl": anzahl, "zeit": zeit}}


# Die Lagen der Vorschau: Serie, Schutz, Fortschritt
LAGEN = {
    "null": lambda: _stand(_tage(1, 13), 0, 3.5),        # Serie 12, heute nichts, noch 6 Tage
    "eins": lambda: _stand(_tage(0, 47), 1, 0.5),        # Serie 47, heute gelernt, noch 9 Tage
    "voll": lambda: _stand(_tage(0, 23), 2),             # Serie 23, heute gelernt, voll
    "gerettet": lambda: _stand(_tage(2, 50), 1, 6),      # gestern verpasst, ein Schutz da
    "verloren": lambda: _stand(_tage(3, 20), 0, 4),      # zwei Tage verpasst, keiner da
}


def _kontext(browser, basis, schema="light", breite=360, dpr=1):
    ctx = browser.new_context(viewport={"width": breite, "height": 740}, device_scale_factor=dpr,
                              locale="de-DE", service_workers="block", color_scheme=schema,
                              reduced_motion="reduce")
    s = Seite(ctx.new_page(), basis)
    s.page.clock.set_fixed_time(JETZT)
    return ctx, s


def _starten(seite, stand, sprache="de", fest=None):
    """Wie Seite.starten, nur mit Fest-Probe (zmaj_fest_probe) - die muss vor
    dem ersten Laden stehen: beim zweiten waere "gerettet" schon verbraucht."""
    seite.page.goto(seite.basis + "/leer")
    seite.js("""([stand, sprache, fest]) => { localStorage.clear();
        localStorage.setItem('zmaj_stand', JSON.stringify(stand));
        localStorage.setItem('zmaj_einwilligung', JSON.stringify({wahl:'nein', stand:1, zeit:new Date().toISOString()}));
        localStorage.setItem('zmaj_sprache', sprache);
        if(fest) localStorage.setItem('zmaj_fest_probe', fest); }""", [stand, sprache, fest])
    seite.page.goto(seite.basis + "/app/index.html")
    seite.bereit()
    # Der Vorspann liegt sonst noch ueber allem - Fotos und axe saehen nur ihn.
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    seite.page.wait_for_function("() => [...document.querySelectorAll('#pfad .obenreihe img, #schutzMeldung img')]"
                                 ".every(i => i.complete)")


def _zeile(seite):
    return seite.js(ZEILE)


# Wie Android "Schriftgroesse": jede berechnete Schriftgroesse mal f (wie in
# test_flamme.py und test_symbole.py). Erst alle lesen, dann schreiben.
SCHRIFT = """(f) => { const els = [...document.querySelectorAll('body *')];
  const g = els.map(e => parseFloat(getComputedStyle(e).fontSize));
  els.forEach((e, i) => e.style.fontSize = (g[i] * f) + 'px'); }"""


# ---------------------------------------------------------------------------
# 0, 1, 2 Schutz
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("lage,plaetze,tage,b,small", [
    ("null", ["friert", "leer"], [4, None], "0 Schutz", "noch 6 Tage"),
    ("eins", ["voll", "friert"], [None, 1], "1 Schutz", "noch 9 Tage"),
    ("voll", ["voll", "voll"], [None, None], "2 Schutz", "voll"),
])
def test_plaetze_und_text(browser, basis, lage, plaetze, tage, b, small):
    """Zwei Plaetze (SCHUTZ_MAX). Vorhanden = Schild in Farbe, ohne Filter.
    Der erste freie Platz friert zu: blass darunter, farbig darueber,
    von oben her abgeschnitten. Weitere freie Plaetze nur blass. Daneben
    der kurze Text; der Bildschirmleser liest "1 Schutz, noch 9 Tage" - die
    Schilde sind Schmuck, ohne Namen."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, LAGEN[lage]())
        z = _zeile(seite)
        assert z["plaetze"] == plaetze and z["tage"] == tage
        assert z["b"] == b and z["small"] == small
        assert z["text"] == b + ", " + small            # das Komma nur fuer den Bildschirmleser
        assert z["leser"] == "inset(50%)"               # .nurleser: unsichtbar
        assert z["smallKlasse"] == ("voll" if small == "voll" else "")
        assert z["ariaPlaetze"] == "true"
        erwartet = {"voll": ["ganz"], "friert": ["blass", "eis"], "leer": ["blass"]}
        assert [x["klasse"] for x in z["bilder"]] == [k for p in plaetze for k in erwartet[p]]
        for x in z["bilder"]:
            assert x["src"] == BILD and x["alt"] == "" and x["geladen"], x
            if x["klasse"] == "ganz":
                assert x["filter"] == "none" and x["clip"] == "none", x
            elif x["klasse"] == "blass":
                assert x["filter"].startswith("grayscale(1)"), x
            else:
                um = tage[plaetze.index("friert")]
                oben = 97.7 - (um / 10) ** .6 * 95.4
                assert x["clip"] == "inset(%s%% 0px 0px)" % ("%.1f" % oben).rstrip("0").rstrip("."), x
        assert "❄" not in z["pfad"]
        assert z["blase"]["hidden"] and z["blase"]["anzeige"] == "none"
        # was der Bildschirmleser bekommt: nur Text, kein Bild
        snap = seite.page.locator("#streakLine").aria_snapshot()
        assert "img" not in snap, snap
        assert re.sub(r"\s+", " ", " ".join(re.findall(r"text: (.*)", snap))).replace(" ,", ",") == b + ", " + small, snap
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Fortschritt: Tag fuer Tag friert der Platz von unten zu
# ---------------------------------------------------------------------------

# Farbige Pixel (Kanal-Spanne > 60) eines Bildschirmfotos: wie viele, und die
# oberste Zeile. Das blasse Bild ist grau, der Grund nur leicht getoent.
FARBE = """async (s) => { const img = new Image(); img.src = 'data:image/png;base64,' + s; await img.decode();
  const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
  const x = c.getContext('2d'); x.drawImage(img, 0, 0); const d = x.getImageData(0, 0, c.width, c.height).data;
  let n = 0, oben = c.height;
  for(let y = 0; y < c.height; y++) for(let i = 0; i < c.width; i++){ const k = 4 * (y * c.width + i);
    const hi = Math.max(d[k], d[k+1], d[k+2]), lo = Math.min(d[k], d[k+1], d[k+2]);
    if(hi - lo > 60){ n++; if(y < oben) oben = y; } }
  return {n, oben, hoehe: c.height}; }"""

# Den Schutz auf "seit e Tagen" stellen und neu zeichnen, ohne neu zu laden.
STELLEN = """(e) => { schutz = {anzahl: 0, zeit: Date.now() - e * 86400000}; renderSerie();
  const p = document.querySelectorAll('#streakLine .schutzplatz');
  return {tage: Number(p[0].dataset.tage), text: document.querySelector('#streakLine small').textContent}; }"""


def _platz_foto(seite, i):
    seite.page.wait_for_function("() => [...document.querySelectorAll('#streakLine img')].every(i => i.complete && i.naturalWidth)")
    r = seite.js("(i) => { const r = document.querySelectorAll('#streakLine .schutzplatz')[i].getBoundingClientRect();"
                 " return {x: r.left, y: r.top, width: r.width, height: r.height}; }", i)
    return seite.js(FARBE, base64.b64encode(seite.page.screenshot(clip=r)).decode("ascii"))


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_fortschritt_tag_fuer_tag(browser, basis, schema):
    """Gezaehlt wird wie im Text daneben: "noch 9 Tage" = 1 Tag um, "noch 1
    Tag" = 9 Tage um; in den letzten Stunden bleibt es bei 9 - ein ganzes
    Schild gibt es erst, wenn es da ist. Mit jedem Tag mehr farbige Pixel,
    und die Eiskante steigt. Der leere zweite Platz hat keine Farbe, ein
    volles Schild am meisten."""
    ctx, seite = _kontext(browser, basis, schema=schema, dpr=2)
    try:
        _starten(seite, LAGEN["null"]())
        vorher = None
        for e, um, text in [(0.2, 1, "noch 9 Tage"), (1.5, 2, "noch 8 Tage"), (4.5, 5, "noch 5 Tage"),
                            (8.5, 9, "noch 1 Tag"), (9.9, 9, None)]:
            st = seite.js(STELLEN, e)
            assert st["tage"] == um, (e, st)
            if text:
                assert st["text"] == text, (e, st)
            else:
                assert st["text"].startswith("noch ") and "Tag" not in st["text"], st   # Stunden
            seite.page.wait_for_timeout(50)
            f = _platz_foto(seite, 0)
            assert f["n"] > 0, (e, f)
            if vorher and um > vorher[0]:
                assert f["n"] > vorher[1]["n"] and f["oben"] < vorher[1]["oben"], (e, f, vorher)
            vorher = (um, f)
            assert _platz_foto(seite, 1)["n"] == 0                     # leer: blass, ohne Farbe
        # Ein Tag spaeter ist der Schutz da: der erste Platz voll, der zweite friert
        seite.js("() => { schutz = {anzahl: 0, zeit: Date.now() - 10.2 * 86400000}; renderSerie(); }")
        z = _zeile(seite)
        assert z["plaetze"] == ["voll", "friert"] and z["b"] == "1 Schutz"
        seite.page.wait_for_function("() => [...document.querySelectorAll('#streakLine img')].every(i => i.complete)")
        assert _platz_foto(seite, 0)["n"] > vorher[1]["n"]
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Meldungen als Sprechblase
# ---------------------------------------------------------------------------

ZIPFEL = """() => { const m = document.getElementById('schutzMeldung'), d = document.getElementById('zmajHome');
  const r = m.getBoundingClientRect(), s = getComputedStyle(m, '::before'), z = d.getBoundingClientRect();
  const mitte = r.right - parseFloat(s.right) - parseFloat(s.width) / 2;
  return {mitte, links: z.left, rechts: z.right, top: s.top, inhalt: s.content,
          davor: m.previousElementSibling.className, danach: m.nextElementSibling ? m.nextElementSibling.className : ''}; }"""


@pytest.mark.parametrize("fall", ["ein_tag", "zwei_tage"])
def test_gerettet_als_sprechblase(browser, basis, fall):
    """Gestern (bzw. gestern und vorgestern) verpasst, Schutz da: die Serie
    bleibt, der Schutz ist verbraucht, und der Drache sagt es in einer
    Sprechblase mit dem Schild - ohne Schneeflocke im Text. Ihr Zipfel
    zeigt nach oben, auf die Mitte des Drachen."""
    stand = LAGEN["gerettet"]() if fall == "ein_tag" else _stand(_tage(3, 50), 2)
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, stand)
        z = _zeile(seite)
        assert z["zahl"] == str(len(stand["tage"]))
        assert z["b"] == "0 Schutz" and z["plaetze"] == ["friert", "leer"]
        m = z["blase"]
        assert not m["hidden"] and m["anzeige"] == "flex" and m["klasse"] == "schutzblase gerettet"
        assert m["text"] == ("Du hast einen Tag ausgelassen. Ein Schutz hat deine Serie gerettet." if fall == "ein_tag"
                             else "Du hast 2 Tage ausgelassen. 2 Schutz haben deine Serie gerettet.")
        assert m["bild"] == BILD and m["bildGeladen"] and m["bildAria"] == "true" and m["kohle"] is None
        zp = seite.js(ZIPFEL)
        assert zp["inhalt"] == '""' and zp["top"] == "-8px"
        assert zp["links"] + 30 < zp["mitte"] < zp["rechts"] - 30, zp
        assert zp["davor"] == "obenreihe" and "weiterknopf" in zp["danach"], zp
        assert "❄" not in z["pfad"]
        assert seite.fehler == []
    finally:
        ctx.close()


def test_verloren_als_sprechblase_bis_heute_gelernt(browser, basis):
    """Zwei Tage verpasst, kein Schutz: die Serie ist 0, die Blase rot
    umrandet mit der kalten Kohle der Flamme. Nach der ersten Lektion des
    Tages laeuft eine neue Serie - die Blase ist weg."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, LAGEN["verloren"]())
        z = _zeile(seite)
        assert z["zahl"] == "0"
        m = z["blase"]
        assert not m["hidden"] and m["klasse"] == "schutzblase verloren"
        assert m["text"] == "Deine Lernserie ist leider gerissen. Heute fängt eine neue an."
        assert "flamme/aus.webp" in m["kohle"] and m["kohleAria"] == "true" and m["bild"] is None
        rand = seite.js("() => getComputedStyle(document.getElementById('schutzMeldung')).borderTopColor")
        assert rand == "rgb(241, 178, 172)"
        seite.js("() => { markToday(); homeMode = 'words'; showHome(); }")
        z = _zeile(seite)
        assert z["blase"]["hidden"] and z["blase"]["anzeige"] == "none" and z["zahl"] == "1"
        assert seite.fehler == []
    finally:
        ctx.close()


def test_festgruss_unter_der_sprechblase(browser, basis):
    """Zu einem Fest kommt der Gruss unter die Sprechblase - stuende er
    dazwischen, zeigte ihr Zipfel auf den Gruss statt auf den Drachen."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, LAGEN["gerettet"](), fest="weihnachten")
        # getAttribute statt className: Girlande und Wiese sind SVG
        folge = seite.js("""() => [...document.getElementById('pfad').children].map(e => e.id || e.getAttribute('class'))""")
        i = folge.index("schutzMeldung")
        assert folge[i - 1] in ("obenreihe", "festwiese festteil") and "festgruss festteil" in folge[i + 1:], folge
        assert folge.index("festgruss festteil") == i + 1, folge
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Hell und dunkel
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("schema", ["light", "dark"])
@pytest.mark.parametrize("lage", list(LAGEN))
def test_hell_und_dunkel_ohne_fehler(browser, basis, schema, lage):
    """Jede Lage in beiden Fassungen: kein Skriptfehler, keine fremde
    Anfrage, alle Bilder geladen, kein ernster axe-Fund (auch Kontrast) in
    der Reihe oben und in der Sprechblase. "voll" in der Eisschrift der
    Fassung."""
    ctx, seite = _kontext(browser, basis, schema=schema)
    try:
        _starten(seite, LAGEN[lage]())
        z = _zeile(seite)
        assert all(x["geladen"] for x in z["bilder"])
        if lage == "voll":
            assert z["smallFarbe"] == ("rgb(18, 80, 127)" if schema == "light" else "rgb(147, 207, 255)")
        seite.page.add_script_tag(path=AXE)
        funde = seite.js("""async () => (await axe.run({include: [['#pfad .obenreihe'], ['#schutzMeldung']]},
                {resultTypes: ['violations']})).violations
            .filter(v => v.impact === 'serious' || v.impact === 'critical')
            .map(v => v.id + ': ' + v.nodes.map(n => n.target.join(' ')).join(', '))""")
        assert funde == []
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Alle acht Sprachen
# ---------------------------------------------------------------------------

# Seitenrand, Zeile, Sprechblase und die Breite des Drachen
MASS = """() => { const s = document.querySelector('.serieblock').getBoundingClientRect(),
    l = document.getElementById('streakLine'), m = document.getElementById('schutzMeldung').getBoundingClientRect();
    return {seite: document.documentElement.scrollWidth, breit: innerWidth,
            zeile: l.scrollWidth - l.clientWidth, rechts: l.getBoundingClientRect().right, block: s.right,
            blase: m.right, drache: document.getElementById('zmajHome').getBoundingClientRect().width}; }"""


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_alle_sprachen_ohne_schneeflocke_und_ohne_ueberstand(browser, basis, sprache):
    """In jeder Sprache: keine Schneeflocke mehr (das Schild ist das Bild),
    Schutz und Rest stehen kurz da, und nichts ragt ueber den Rand - weder
    die Zeile noch die Sprechblase, auch nicht bei 360 px.

    Der Drache bleibt dabei 120 px breit, auch bei 130 % Schrift und bei
    320 px. Pruefbefund vom 24.10.2026: "reeksbeschermingen" (nl) ist ein
    Wort ohne Bruchstelle und setzte die Mindestbreite der Spalte; den
    fehlenden Platz gab der Drache ab, bei 360 px und 130 % bis auf 59 px,
    in da und nb bis 76 bzw. 82 px. Der Seitenrand blieb dabei frei, darum
    fiel es hier nicht auf."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, _stand(_tage(3, 30), 2), sprache=sprache)   # zwei Tage gerettet: die laengste Meldung
        z = _zeile(seite)
        t = seite.js("() => ({schutz: T['serie.schutz'], noch: T['serie.schutz_noch'], gerettet: T['serie.gerettet']})")
        assert "❄" not in z["pfad"] and not any("❄" in v for v in t.values()), t
        assert "{zeit}" in t["noch"] and len(t["noch"]) <= 16, t
        assert z["small"] and z["text"] == z["b"] + ", " + z["small"]
        assert not z["blase"]["hidden"] and z["blase"]["text"]
        for faktor, breite in ((1, 360), (1.3, 360), (1.3, 320)):
            if faktor != 1 and breite == 360:
                seite.js(SCHRIFT, faktor)
            seite.page.set_viewport_size({"width": breite, "height": 740})
            mass = seite.js(MASS)
            lage = (sprache, faktor, breite, z["b"], mass)
            assert mass["seite"] <= mass["breit"] and mass["zeile"] <= 0, lage
            assert mass["rechts"] <= mass["block"] + 0.5 and mass["blase"] <= mass["breit"], lage
            assert abs(mass["drache"] - 120) < 0.5, lage
        assert seite.fehler == []
    finally:
        ctx.close()
