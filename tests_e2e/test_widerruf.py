# -*- coding: utf-8 -*-
"""„Vertrag widerrufen“ im echten Browser, Google wird nachgebaut.

Pruefbericht 1.3, G15: Die Mail enthielt nur die Bedienungsanleitung aus dem
Kasten („Tippe auf ...“) und keine Angaben zum Vertrag, und liefert Google keine
Produkte, verschwand der Knopf mit dem ganzen Block. § 356a BGB, gelesen am
06.11.2026: Abs. 1 verlangt die Funktion waehrend der Frist staendig verfuegbar,
Abs. 2 Name, Angaben zum Vertrag und den Weg fuer die Bestaetigung.
"""
import datetime
import urllib.parse

import pytest

from conftest import Seite

ZMAJ_MAIL = "zmaj.lernapp@gmail.com"

PLUGIN = """window.Capacitor = {Plugins: {ZmajAbo: {
  stand: async () => ({bekannt: true, aktiv: AKTIV, gesperrt: false, plan: null, probe: false}),
  preise: async () => ({ok: true, plaene: PLAENE}),
  addListener: () => ({remove(){}}),
}}};"""
MIT_PRODUKTEN = "[{plan: 'jahr', preis: '19,99 €', micros: 19990000, waehrung: 'EUR'}]"

SICHTBAR = """id => { const e = document.getElementById(id);
  if(!e) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; }"""


def _einstellungen(browser, basis, heute_stand, sprache="de", plaene=MIT_PRODUKTEN, aktiv="false", plugin=True):
    ctx = browser.new_context(viewport={"width": 360, "height": 740}, locale="de-DE", service_workers="block")
    if plugin:
        ctx.add_init_script(PLUGIN.replace("PLAENE", plaene).replace("AKTIV", aktiv))
    seite = Seite(ctx.new_page(), basis)
    seite.starten(sprache=sprache, stand=heute_stand())
    seite.js("() => document.getElementById('vorspann').click()")
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    seite.js("() => showSettings()")
    seite.page.wait_for_function("() => !aboLaeuft")
    return ctx, seite


def _mail(seite):
    """Die mailto:-Aufrufe meldet Chromium als Anfrage, etwas spaeter als den Klick."""
    for _ in range(80):
        treffer = [u for u in seite.fremd if u.startswith("mailto:" + ZMAJ_MAIL + "?")]
        if treffer:
            teile = urllib.parse.parse_qs(treffer[0].split("?", 1)[1])
            return teile["subject"][0], teile["body"][0]
        seite.page.wait_for_timeout(25)
    raise AssertionError("kein mailto: " + repr(seite.fremd))


@pytest.mark.parametrize("sprache", ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"])
def test_mail_nennt_den_vertrag_statt_der_anleitung(browser, basis, heute_stand, sprache):
    ctx, seite = _einstellungen(browser, basis, heute_stand, sprache=sprache)
    try:
        texte = seite.js("""() => ({mail: t('set.widerruf_mail'), anleitung: t('set.widerruf_text'),
                                    knopf: t('set.widerruf_knopf'), ok: t('set.widerruf_bestaetigen')})""")
        assert texte["mail"] != "set.widerruf_mail", texte
        seite.page.click("#widerrufKnopf")
        assert seite.page.inner_text(".nachfrage .txt") == texte["anleitung"]
        assert seite.page.inner_text("#widOk") == texte["ok"]
        seite.page.click("#widOk")
        betreff, rumpf = _mail(seite)
        assert betreff == "Zmaj – " + texte["knopf"]
        assert texte["anleitung"] not in rumpf
        # Die Felder fuer Name und Vertrag stehen offen da, dahinter Sprache und Tag
        tag = datetime.date.today().isoformat()
        assert rumpf.replace("\r\n", "\n") == texte["mail"] + "\n\n--\n%s · %s" % (sprache, tag)
        assert seite.fehler == []
    finally:
        ctx.close()


def test_knopf_bleibt_wenn_google_keine_produkte_liefert(browser, basis, heute_stand):
    ctx, seite = _einstellungen(browser, basis, heute_stand, plaene="[]")
    try:
        seite.page.wait_for_function("() => aboProdukteFehlen")
        assert seite.js(SICHTBAR, "widerrufKnopf"), "der Knopf ist weg"
        assert not seite.js(SICHTBAR, "swVoll"), "ohne Produkte gibt es nichts zu kaufen"
        seite.page.click("#widerrufKnopf")
        seite.page.click("#widOk")
        assert _mail(seite)[1].startswith(seite.js("() => t('set.widerruf_mail')"))
        # Die Meldung mit der Adresse steht auch dann da, wenn die Kaufzeile fehlt
        assert seite.js(SICHTBAR, "setVollNote")
        assert seite.fehler == []
    finally:
        ctx.close()


def test_mit_produkten_steht_alles_wie_vorher(browser, basis, heute_stand):
    ctx, seite = _einstellungen(browser, basis, heute_stand)
    try:
        assert seite.js(SICHTBAR, "swVoll") and seite.js(SICHTBAR, "widerrufKnopf")
        assert seite.js("() => getComputedStyle(document.querySelector('#setVollBox .setting')).borderTopWidth") == "0px"
    finally:
        ctx.close()


def test_laufendes_abo_ohne_produkte_behaelt_die_kaufzeile(browser, basis, heute_stand):
    ctx, seite = _einstellungen(browser, basis, heute_stand, plaene="[]", aktiv="true")
    try:
        seite.page.wait_for_function("() => aboProdukteFehlen && premium")
        assert seite.js(SICHTBAR, "swVoll") and seite.js(SICHTBAR, "widerrufKnopf")
        assert seite.fehler == []
    finally:
        ctx.close()


def test_ohne_abo_plugin_gibt_es_den_block_nicht(browser, basis, heute_stand):
    """Am PC und in der Web-Demo kann man nichts kaufen, also auch nichts widerrufen."""
    ctx, seite = _einstellungen(browser, basis, heute_stand, plugin=False)
    try:
        assert not seite.js(SICHTBAR, "setVollBox")
        assert not seite.js(SICHTBAR, "widerrufKnopf")
    finally:
        ctx.close()
