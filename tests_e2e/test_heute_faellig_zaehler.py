# -*- coding: utf-8 -*-
"""Der rote Zaehler am Reiter Wiederholen und "Heute faellig" ganz oben (O10).

Ajdin am 20.11.2026: "ja mach die heute fällig ganz nach oben und mach so eine
rote mitteilung "12" das ist eine gute idee". Vorher lag der Kasten "Heute
faellig" als dritter unter "Wiederholen" und "Markiert", bei 800 px Hoehe
ausser Sicht (Release\\Optimierung_2026-11-20\\BERICHT.md, Punkt 10).

Geprueft in Chromium und - wenn Playwright es auf dem Rechner hat - in WebKit:
  - der Zaehler zeigt die Zahl aus dem Kasten "Heute faellig", nur wenn sie
    groesser als null ist, ab 100 "99+"; rot mit weisser Schrift (4,5:1),
    hell und dunkel, und ein Bildschirmleser hoert die Zahl im Namen des
    Reiters;
  - er braucht keinen Platz in der Reiterzeile, ragt nicht in die Schrift
    und nicht ueber die Leiste hinaus - in allen acht Sprachen, auf dem
    iPhone (html[data-plattform="ios"]) und auf dem Tablet (html.gross);
  - im Reiter Wiederholen steht "Heute faellig" oben;
  - nach einer Runde und beim Wechsel des Kartei-Tags um 4 Uhr zaehlt er neu.
"""
import datetime
import os
import re

import pytest
from conftest import Seite
from test_ios import HUELLE
from test_kartei import ANTWORT, WOERTER, _heute, _kartei_datum, _uhr

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXE = os.path.join(WURZEL, "tests_e2e", "vendor", "axe.min.js")
MOTOREN = ["chromium", "webkit"]

# Zaehler, Reiter, Schrift im Reiter, Leiste und die drei Reiter, dazu was der
# Bildschirmleser hoert und ob sich die Seite seitlich schieben liesse.
LAGE = r"""() => {
  const r = e => { const b = e.getBoundingClientRect(); return {l: b.left, t: b.top, r: b.right, b: b.bottom}; };
  const z = document.getElementById('faelligZahl'), reiter = document.getElementById('modeTopf');
  const leiste = document.querySelector('.mode[role="tablist"]'), s = getComputedStyle(z);
  return {zahl: z.textContent, versteckt: z.hidden, sichtbar: !!(z.offsetWidth || z.offsetHeight),
          stumm: z.getAttribute('aria-hidden'), name: reiter.getAttribute('aria-label'),
          zaehler: r(z), reiter: r(reiter), schrift: r(reiter.querySelector('[data-t]')), leiste: r(leiste),
          reiterOben: [...leiste.querySelectorAll('button')].map(b => Math.round(b.getBoundingClientRect().top)),
          ueber: [...leiste.querySelectorAll('button')].map(b => b.scrollWidth - b.clientWidth),
          grund: s.backgroundColor, farbe: s.color,
          seiteB: document.scrollingElement.scrollWidth, innenB: innerWidth,
          plattform: document.documentElement.dataset.plattform || '',
          gross: document.documentElement.classList.contains('gross')};
}"""


def _rgb(s):
    return [int(x) for x in re.findall(r"\d+", s)[:3]]


def _kontrast(a, b):
    def hell(c):
        k = [x / 255 for x in c]
        k = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in k]
        return 0.2126 * k[0] + 0.7152 * k[1] + 0.0722 * k[2]
    h1, h2 = sorted([hell(a), hell(b)], reverse=True)
    return (h1 + 0.05) / (h2 + 0.05)


def _starten(seite, heute_stand, n, gesamt=20, sprache="de", **mehr):
    """n Woerter heute faellig, gesamt gewusst (der Rest erst uebermorgen)."""
    seite.starten(stand=heute_stand(), sprache=sprache)
    ids = seite.js(WOERTER, gesamt)
    h = _heute()
    w = {x: ([2, h - (i % 5), h - 9] if i < n else [2, h + 2, h - 5]) for i, x in enumerate(ids)}
    seite.starten(stand=heute_stand(gewusst=ids, kartei={"tag": 0, "n": 0, "w": w}, **mehr), sprache=sprache)
    return ids


def _geometrie_ok(m):
    """Der Zaehler im Reiter oben rechts: nicht in der Schrift, nicht ueber
    die Leiste hinaus, die drei Reiter in einer Zeile, nichts zum Schieben."""
    z, s, leiste = m["zaehler"], m["schrift"], m["leiste"]
    assert len(set(m["reiterOben"])) == 1, m["reiterOben"]
    assert z["b"] <= s["t"] + 0.5, ("Zaehler reicht in die Schrift", z, s)
    assert z["r"] <= m["reiter"]["r"] + 0.5 and z["l"] >= m["reiter"]["l"], (z, m["reiter"])
    assert z["r"] <= leiste["r"] and max(m["ueber"]) <= 0, ("breiter als der Platz", m["ueber"])
    assert z["t"] < m["reiter"]["t"] and z["b"] > m["reiter"]["t"], "oben auf der Kante des Reiters"
    assert m["seiteB"] <= m["innenB"], (m["seiteB"], m["innenB"])


@pytest.fixture(params=MOTOREN)
def motor(request, browser):
    """Chromium immer, WebKit nur wenn da (siehe conftest.py, webkit)."""
    return browser if request.param == "chromium" else request.getfixturevalue("webkit")


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_zaehler_am_reiter(motor, basis, heute_stand, schema):
    ctx = motor.new_context(viewport={"width": 360, "height": 780}, locale="de-DE",
                            color_scheme=schema, service_workers="block")
    seite = Seite(ctx.new_page(), basis)
    try:
        _starten(seite, heute_stand, 12)
        m = seite.js(LAGE)
        assert m["zahl"] == "12" and not m["versteckt"] and m["sichtbar"]
        assert m["stumm"] == "true" and m["name"] == "Wiederholen, 12 Wörter heute fällig"
        assert _rgb(m["grund"]) == [208, 53, 44] and _rgb(m["farbe"]) == [255, 255, 255]
        assert _kontrast(_rgb(m["grund"]), _rgb(m["farbe"])) >= 4.5
        _geometrie_ok(m)
        # Nur am Reiter Wiederholen, keiner an Lernpfad und Geschichten
        assert seite.js("() => document.querySelectorAll('.zaehler').length") == 1
        # axe: an Leiste und Zaehler nichts Ernstes (Kontrast, Name, Rolle)
        seite.page.add_script_tag(path=AXE)
        funde = seite.js("""async () => (await axe.run('.mode[role="tablist"]', {resultTypes: ['violations']}))
            .violations.filter(v => v.impact === 'serious' || v.impact === 'critical').map(v => v.id)""")
        assert funde == []
        # Im Reiter Wiederholen: "Heute faellig" oben, der Zaehler bleibt
        seite.page.click("#modeTopf")
        reihe = seite.js("""() => [...document.getElementById('topfHome').children]
            .map(e => [e.id, Math.round(e.getBoundingClientRect().top)])""")
        assert [x[0] for x in reihe] == ["karteiBox", "topfBox", "sternBox"]
        assert reihe[0][1] < reihe[1][1] < reihe[2][1]
        assert seite.js("() => document.querySelector('#karteiBox .topfzahl').textContent") == "12"
        m = seite.js(LAGE)
        assert m["zahl"] == "12" and m["sichtbar"]
        _geometrie_ok(m)
        # Einzahl, dann nichts faellig: kein Zaehler, der Reiter heisst wieder
        # nur, was er zeigt
        seite.js("() => { Object.keys(kartei.w).slice(1).forEach(id => { kartei.w[id][1] = karteiTag() + 2; }); showHome(); }")
        m = seite.js(LAGE)
        assert m["zahl"] == "1" and m["sichtbar"] and m["name"] == "Wiederholen, 1 Wort heute fällig"
        seite.js("() => { Object.keys(kartei.w).forEach(id => { kartei.w[id][1] = karteiTag() + 2; }); showHome(); }")
        m = seite.js(LAGE)
        assert m["versteckt"] and not m["sichtbar"] and m["name"] is None
        assert seite.js("() => document.getElementById('modeTopf').textContent.trim()") == "Wiederholen"
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


def test_ab_hundert_99_plus(seite, heute_stand):
    """Mit der Tagesgrenze sind es hoechstens 30. Kaeme mehr, steht "99+" wie
    an einem App-Symbol, und der Zaehler bleibt in der Leiste."""
    _starten(seite, heute_stand, 3)
    erg = seite.js("""() => {
      const alt = karteiHeute, aus = {};
      try{
        for(const n of [99, 100, 150]){
          karteiHeute = () => Array(n).fill('x'); faelligZaehler();
          const z = document.getElementById('faelligZahl').getBoundingClientRect();
          const r = document.getElementById('modeTopf'), l = r.getBoundingClientRect();
          aus[n] = [document.getElementById('faelligZahl').textContent, r.getAttribute('aria-label'),
                    z.right <= l.right + 0.5 && z.left >= l.left && r.scrollWidth <= r.clientWidth];
        }
      } finally { karteiHeute = alt; faelligZaehler(); }
      return aus;
    }""")
    assert erg["99"] == ["99", "Wiederholen, 99 Wörter heute fällig", True]
    assert erg["100"] == ["99+", "Wiederholen, 100 Wörter heute fällig", True]
    assert erg["150"] == ["99+", "Wiederholen, 150 Wörter heute fällig", True]
    assert seite.js("() => document.getElementById('faelligZahl').textContent") == "3"
    assert seite.fehler == []


def test_zaehlt_nach_einer_runde_neu(seite, heute_stand):
    """Eine Runde "Heute faellig" mit zehn Woertern: zurueck im Reiter zeigt
    der Zaehler, was noch faellig ist - nach der zweiten Runde nichts mehr."""
    _starten(seite, heute_stand, 12)
    assert seite.js(LAGE)["zahl"] == "12"
    for rest in (2, 0):
        seite.js("() => { homeMode = 'topf'; showHome(); }")
        seite.js("() => document.getElementById('karteiLos').click()")
        assert seite.js("() => Lx.quelle") == "kartei"
        while seite.js("() => Lx.i < Lx.queue.length"):
            seite.js(ANTWORT, True)
        seite.page.locator("#lBody .result-big").wait_for()
        seite.js("() => document.getElementById('lHome').click()")
        m = seite.js(LAGE)
        if rest:
            assert m["zahl"] == "2" and m["sichtbar"] and m["name"] == "Wiederholen, 2 Wörter heute fällig"
            assert seite.js("() => document.querySelector('#karteiBox .topfzahl').textContent") == "2"
        else:
            assert m["versteckt"] and m["name"] is None
            assert seite.js("() => document.querySelector('#karteiBox .topfleer').textContent") == "Heute ist nichts fällig."
    assert seite.fehler == []


def test_wechsel_des_kartei_tags_um_vier(motor, basis, heute_stand):
    """Die Kartei zaehlt ab 4 Uhr den neuen Tag, today() schon ab Mitternacht.
    Liegt die App ueber Nacht auf der Startseite, kommt der Zaehler mit der
    Rueckkehr aus dem Hintergrund (und dem Takt alle 30 Sekunden, beide ueber
    topfNachziehen) - ohne dass die Seite an den Anfang springt."""
    ctx = motor.new_context(viewport={"width": 360, "height": 640}, locale="de-DE", service_workers="block")
    seite = Seite(ctx.new_page(), basis)
    try:
        tag = _kartei_datum()
        _uhr(seite, tag, 22)
        seite.starten(stand=heute_stand())
        ids = seite.js(WOERTER, 20)
        h = _heute()
        # 5 morgen faellig, der Rest erst in zwei Wochen
        w = {x: ([2, h + 1, h - 6] if i < 5 else [3, h + 14, h]) for i, x in enumerate(ids)}
        seite.starten(stand=heute_stand(gewusst=ids, kartei={"tag": 0, "n": 0, "w": w}))
        seite.js("() => { homeMode = 'topf'; showHome(); }")
        assert seite.js(LAGE)["versteckt"]
        zurueck = "() => document.dispatchEvent(new Event('visibilitychange'))"
        # Nach Mitternacht, vor 4 Uhr: noch der alte Kartei-Tag
        _uhr(seite, tag + datetime.timedelta(days=1), 3, 59)
        seite.js(zurueck)
        assert seite.js(LAGE)["versteckt"]
        assert seite.js("() => document.querySelector('#karteiBox .topfleer') !== null")
        # 4 Uhr: neuer Kartei-Tag, Zaehler und Kasten ziehen nach, die Stelle bleibt
        seite.js("() => window.scrollTo(0, 120)")
        stelle = seite.js("() => window.scrollY")
        assert stelle > 0
        _uhr(seite, tag + datetime.timedelta(days=1), 4, 1)
        seite.js(zurueck)
        m = seite.js(LAGE)
        assert m["zahl"] == "5" and m["sichtbar"] and m["name"] == "Wiederholen, 5 Wörter heute fällig"
        assert seite.js("() => document.querySelector('#karteiBox .topfzahl').textContent") == "5"
        assert seite.js("() => window.scrollY") == stelle
        # Auch im Lernpfad, aus dem Takt (topfNachziehen): am Tag darauf um 4 Uhr
        seite.js("() => { Object.keys(kartei.w).slice(5).forEach(id => { kartei.w[id][1] = karteiTag() + 1; }); "
                 "homeMode = 'words'; showHome(); }")
        assert seite.js(LAGE)["zahl"] == "5"
        _uhr(seite, tag + datetime.timedelta(days=2), 4, 1)
        seite.js("() => topfNachziehen()")
        assert seite.js(LAGE)["zahl"] == "20"
        assert seite.fehler == []
    finally:
        ctx.close()


def test_alle_acht_sprachen(seite, heute_stand):
    """Name fuer den Bildschirmleser in Einzahl und Mehrzahl, und der Zaehler
    passt in jeder Sprache an den Reiter - bei 360 und 320 Punkten."""
    import sprachen
    _starten(seite, heute_stand, 12)
    for breite in (360, 320):
        seite.page.set_viewport_size({"width": breite, "height": 640})
        for code in ("de", "en", "tr", "sv", "nl", "nb", "da", "fr"):
            seite.js("async (c) => { await setzeSprache(c); homeMode = 'words'; showHome(); }", code)
            texte = sprachen.TEXTE[code]
            einzahl, mehrzahl = texte["kartei.zaehler"].split("|")
            m = seite.js(LAGE)
            assert m["zahl"] == "12", code
            assert m["name"] == texte["tab.wiederholen"] + ", " + mehrzahl.replace("{n}", "12"), code
            _geometrie_ok(m)
            seite.js("() => { const k = Object.keys(kartei.w).filter(id => kartei.w[id][1] <= karteiTag());"
                     " k.slice(1).forEach(id => { kartei.w[id][1] += 100; }); faelligZaehler(); }")
            m = seite.js(LAGE)
            assert m["zahl"] == "1" and m["name"] == texte["tab.wiederholen"] + ", " + einzahl.replace("{n}", "1"), code
            _geometrie_ok(m)
            seite.js("() => { Object.keys(kartei.w).forEach(id => { if(kartei.w[id][1] > karteiTag() + 50) kartei.w[id][1] -= 100; }); }")
    assert seite.fehler == []


@pytest.mark.parametrize("art", ["ios", "tablet"])
def test_iphone_und_tablet(motor, basis, heute_stand, art):
    """Auf dem iPhone (Raender aus env(safe-area-inset-*)) und auf dem Tablet
    (html.gross, die Seite vergroessert mit zoom) sitzt er genauso."""
    groesse = {"width": 390, "height": 844} if art == "ios" else {"width": 800, "height": 1280}
    ctx = motor.new_context(viewport=groesse, device_scale_factor=2, has_touch=True, locale="de-DE",
                            service_workers="block")
    seite = Seite(ctx.new_page(), basis)
    try:
        if art == "ios":
            seite.page.add_init_script(HUELLE % "ios")
        _starten(seite, heute_stand, 12)
        m = seite.js(LAGE)
        if art == "ios":
            assert m["plattform"] == "ios"
        else:
            assert m["gross"]
        assert m["zahl"] == "12" and m["sichtbar"] and m["name"] == "Wiederholen, 12 Wörter heute fällig"
        _geometrie_ok(m)
        seite.page.click("#modeTopf")
        assert seite.js("() => document.getElementById('topfHome').firstElementChild.id") == "karteiBox"
        _geometrie_ok(seite.js(LAGE))
        assert seite.fehler == []
    finally:
        ctx.close()
