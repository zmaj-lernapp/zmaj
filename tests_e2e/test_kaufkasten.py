# -*- coding: utf-8 -*-
"""Der Kaufkasten auf kleinen Handys, im echten Browser.

Pruefbericht 1.3, G13: auf 320x568 begann "Zahlungspflichtig abonnieren" bei 680,
der Kasten endete bei 545; auf 360x640 bei 641 und 614. Man sah Drache und
Preise, aber keinen Knopf. Geprueft wird ohne zu scrollen: Treffen ein Finger
auf Kauf- und Abbrechen-Knopf wirklich diese Knoepfe, und steht das, was man vor
der Bestellung wissen muss (gewaehlter Preis, Verlaengerung), dabei im Bild?
Die Preise sind erfunden, Google wird nachgebaut.
"""
import pytest

from conftest import Seite

PLUGIN = """window.__kaeufe = [];
window.Capacitor = {Plugins: {ZmajAbo: {
  stand: async () => ({bekannt: true, aktiv: false, gesperrt: false, plan: null, probe: false}),
  preise: async () => ({ok: true, plaene: [
    {plan: 'monat', preis: '2,99 €', micros: 2990000, waehrung: 'EUR'},
    {plan: 'jahr', preis: '19,99 €', micros: 19990000, waehrung: 'EUR', gratis: GRATIS}]}),
  addListener: () => ({remove(){}}),
  kaufen: async (a) => { __kaeufe.push(a.plan); return {ok: true}; },
}}};"""

# So stellt Chrome die grosse Systemschrift des Handys nach, wie die WebView
GROSSE_SCHRIFT = """document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.style.cssText += ';text-size-adjust:130%;-webkit-text-size-adjust:130%'; });"""

LAGE = """() => {
  const box = document.querySelector('.nachfrage .nachfragebox');
  const b = box.getBoundingClientRect();
  const trifft = el => { const r = el.getBoundingClientRect();
    const x = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    return !!x && (x === el || el.contains(x)); };
  const ganz = el => { const r = el.getBoundingClientRect();
    return r.top >= b.top - 0.5 && r.bottom <= Math.min(b.bottom, innerHeight) + 0.5 && trifft(el); };
  const anim = document.querySelector('.abovorschau .zmaj-anim');
  return {
    kauf: ganz(document.getElementById('aboKauf')),
    zu: ganz(document.getElementById('aboZu')),
    hinweis: ganz(document.querySelector('.nachfragebox .abohinweis')),
    gratis: document.getElementById('aboGratis').textContent,
    gratisDa: ganz(document.getElementById('aboGratis')),
    preis: ganz(document.querySelector('.abokarte[data-plan="jahr"] .p')),
    drache: anim ? Math.round(anim.getBoundingClientRect().height) : 0,
    gemalt: !!(anim && (anim._laedt || anim._anim)),
    breit: box.scrollWidth > box.clientWidth,
    rollt: box.scrollHeight > box.clientHeight,
  };
}"""


def _kasten(browser, basis, heute_stand, breite, hoehe, gratis="'P7D'", sprache="de", gross=False):
    optionen = {"is_mobile": True, "has_touch": True} if gross else {}
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, locale="de-DE",
                              service_workers="block", **optionen)
    ctx.add_init_script(PLUGIN.replace("GRATIS", gratis) + (GROSSE_SCHRIFT if gross else ""))
    seite = Seite(ctx.new_page(), basis)
    seite.starten(sprache=sprache, stand=heute_stand())
    seite.js("() => document.getElementById('vorspann').click()")
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    seite.js("() => vollKaufOeffnen()")
    seite.page.wait_for_selector("#aboKauf")
    return ctx, seite


@pytest.mark.parametrize("breite,hoehe", [(320, 568), (360, 640), (360, 740), (390, 844)])
@pytest.mark.parametrize("gratis", ["'P7D'", "''"])
def test_kaufknopf_steht_ohne_scrollen_im_bild(browser, basis, heute_stand, breite, hoehe, gratis):
    ctx, seite = _kasten(browser, basis, heute_stand, breite, hoehe, gratis)
    try:
        m = seite.js(LAGE)
        assert m["kauf"] and m["zu"] and m["preis"] and m["hinweis"], m
        assert not m["breit"] and not m["rollt"], m
        if gratis == "''":
            assert m["gratis"] == "", m
        else:
            assert "19,99" in m["gratis"] and m["gratisDa"], m
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("sprache", ["en", "tr", "sv", "nl", "nb", "da", "fr"])
def test_kaufknopf_in_jeder_sprache(browser, basis, heute_stand, sprache):
    for breite, hoehe in ((320, 568), (360, 640), (360, 740)):
        ctx, seite = _kasten(browser, basis, heute_stand, breite, hoehe, sprache=sprache)
        try:
            m = seite.js(LAGE)
            assert m["kauf"] and m["zu"] and m["preis"] and m["gratisDa"], (breite, hoehe, m)
            assert seite.fehler == []
        finally:
            ctx.close()


@pytest.mark.parametrize("breite,hoehe", [(360, 740), (390, 844)])
def test_kaufknopf_bei_grosser_systemschrift(browser, basis, heute_stand, breite, hoehe):
    """Der Preis darf nicht hinter dem festen Knopf verschwinden: wer kauft, muss
    ihn sehen, auch bei grosser Schrift."""
    ctx, seite = _kasten(browser, basis, heute_stand, breite, hoehe, gratis="''", gross=True)
    try:
        assert seite.js("() => getComputedStyle(document.getElementById('aboKauf')).fontSize") == "19.5px"
        m = seite.js(LAGE)
        assert m["kauf"] and m["zu"] and m["preis"], m
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("breite,hoehe,drache", [(360, 640, 0), (360, 740, 90), (390, 844, 150)])
def test_der_drache_wird_nur_so_klein_wie_noetig(browser, basis, heute_stand, breite, hoehe, drache):
    ctx, seite = _kasten(browser, basis, heute_stand, breite, hoehe)
    try:
        m = seite.js(LAGE)
        assert m["drache"] == drache, m
        # Ein weggenommener Drache rechnet nicht unsichtbar mit
        assert m["gemalt"] is (drache > 0), m
    finally:
        ctx.close()


def test_auf_dem_kleinsten_handy_laesst_sich_alles_erreichen(browser, basis, heute_stand):
    # Franzoesisch braucht hier am meisten Platz und ist die einzige Sprache, die deutlich rollt
    ctx, seite = _kasten(browser, basis, heute_stand, 320, 568, sprache="fr")
    try:
        assert seite.js(LAGE)["rollt"] is True
        seite.js("() => { const b = document.querySelector('.nachfrage .nachfragebox'); b.scrollTop = b.scrollHeight; }")
        m = seite.js(LAGE)
        assert m["hinweis"] and m["preis"] and m["kauf"] and m["zu"], m
        # Ganz oben steht wieder der Titel, und unter den Knoepfen schaut nichts durch
        z = seite.js("""() => { const b = document.querySelector('.nachfrage .nachfragebox'); b.scrollTop = 0;
            const h = document.querySelector('.nachfragebox h3').getBoundingClientRect();
            const f = document.querySelector('.kaufknoepfe').getBoundingClientRect();
            const r = b.getBoundingClientRect();
            return {titel: h.top >= r.top, ende: Math.round(f.bottom - r.bottom)}; }""")
        assert z["titel"] is True and abs(z["ende"]) <= 1, z
    finally:
        ctx.close()


def test_kaufen_und_abbrechen_gehen_weiter(browser, basis, heute_stand):
    ctx, seite = _kasten(browser, basis, heute_stand, 320, 568)
    try:
        seite.page.locator("#aboZu").click()
        assert seite.js("() => !document.querySelector('.nachfrage')") is True
        seite.js("() => vollKaufOeffnen()")
        seite.page.wait_for_selector("#aboKauf")
        seite.page.locator('.abokarte[data-plan="monat"]').click()
        seite.page.locator("#aboKauf").click()
        seite.page.wait_for_function("() => !document.querySelector('.nachfrage')")
        assert seite.js("() => __kaeufe") == ["monat"]
        assert seite.fehler == []
    finally:
        ctx.close()
