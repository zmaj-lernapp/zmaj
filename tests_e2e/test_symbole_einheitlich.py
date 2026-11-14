# -*- coding: utf-8 -*-
"""Symbole einheitlich auf Android und iPhone (Offen-Liste 5, 14.11.2026).

Ajdin im iPhone-Test: "es hat noch die iphone bilder zb das überspringen
zeichen das muss einheitlich sein", und nach dem Kauf: alles frei, "nur das
das herz nicht gold ist". Gemalt mit Gemini wie Symbol-Satz V1 und von
Ajdin abgenommen ("passt").

Geprueft wird hier im Browser:
  - das goldene Herz: mit der Vollversion in der Kopfleiste, im
    Fragenkasten und in der Statistik nach der Lektion, ohne sie das rote;
    unbegrenzt ohne Kauf (?alle=1) bleibt es rot.
  - die gemalten Bilder statt 🏁 ⭐ 💙 ✨ ✉: Level-Test, Bewertungskarte,
    "Danke!" nach dem Vorschlag, Funken an der goldenen Flamme, E-Mail im
    Profil - in allen acht Sprachen, geladen, als Schmuck (alt="").
"""
import datetime
import io
import os
import re

import pytest
from conftest import WURZEL, Seite

# Fuer die goldene Flamme (365 Tage) muss die Uhr spaeter stehen: eine Serie
# reicht nie vor APP_START zurueck (wie in test_flamme.py).
with io.open(os.path.join(WURZEL, "web", "index.html"), encoding="utf-8") as _f:
    APP_START = datetime.date.fromisoformat(
        re.search(r"const APP_START = '(\d{4}-\d{2}-\d{2})';", _f.read()).group(1))
SPAETER = APP_START + datetime.timedelta(days=400)


def _stand(**mehr):
    h = datetime.date.today()
    s = {"einstufung": {"tag": h.isoformat(), "wahl": "neu", "bis": ""},
         "tage": [(h - datetime.timedelta(days=i)).isoformat() for i in range(1, 6)],
         "muenzen_ges": 500, "muenzen_aus": 0}
    s.update(mehr)
    return s


def _kontext(browser, basis, schema="light", breite=390, hoehe=844):
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, locale="de-DE",
                              service_workers="block", color_scheme=schema, reduced_motion="reduce")
    return ctx, Seite(ctx.new_page(), basis)


def _starten(seite, stand=None, sprache="de"):
    seite.starten(stand=stand or _stand(), sprache=sprache)
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)


# Das Herz an einer Stelle: welches Bild, ob geladen, was daneben steht
HERZ = """(sel) => { const e = document.querySelector(sel); if(!e) return null;
  const i = e.querySelector('img.sym');
  return {bild: i ? i.getAttribute('src') : null, alt: i ? i.getAttribute('alt') : null,
          geladen: !!i && i.complete && i.naturalWidth > 0, text: e.innerText.trim()}; }"""


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_goldenes_herz_mit_vollversion(browser, basis, schema):
    """Ohne Vollversion das rote Herz mit Zahl. Mit ihr das goldene mit ∞ -
    in der Kopfleiste, im Fragenkasten der Lektion und in der Statistik
    danach. Der Name fuer den Bildschirmleser bleibt "Leben". Endet die
    Vollversion, ist es wieder rot."""
    ctx, seite = _kontext(browser, basis, schema)
    try:
        _starten(seite)
        rot = seite.js(HERZ, "#livesKnopf")
        assert rot == {"bild": "symbole/herz.webp", "alt": "Leben", "geladen": True, "text": "5"}, rot

        seite.js("() => { vollversionMerken(true); renderLives(); }")
        seite.page.wait_for_function("() => [...document.querySelectorAll('img.sym')].every(i => i.complete)")
        gold = seite.js(HERZ, "#livesKnopf")
        assert gold == {"bild": "symbole/herzgold.webp", "alt": "Leben", "geladen": True, "text": "∞"}, gold
        assert seite.js("() => $('livesBar').classList.contains('premium')")

        seite.js("() => { openLevel(0); startLesson(); stilleBitte(); }")
        kasten = seite.js(HERZ, "#lHerz")
        assert kasten["bild"] == "symbole/herzgold.webp" and kasten["text"] == "∞" and kasten["geladen"], kasten
        seite.durchspielen("lBody", "Lx")
        seite.page.wait_for_function("() => !!document.querySelector('#lBody .stats')", timeout=8000)
        stat = seite.js("""() => { const s = [...document.querySelectorAll('#lBody .stat')].find(x => x.querySelector('img.sym'));
            const i = [...document.querySelectorAll('#lBody .stat img.sym')].find(x => /herz/.test(x.src));
            return {bild: i && i.getAttribute('src'), text: i && i.closest('.stat').innerText.replace(/\\s+/g, ' ').trim()}; }""")
        assert stat == {"bild": "symbole/herzgold.webp", "text": "∞ Leben"}, stat

        seite.js("() => { stilleBitte(); vollversionMerken(false); renderLives(); homeMode = 'words'; showHome(); }")
        wieder = seite.js(HERZ, "#livesKnopf")
        assert wieder["bild"] == "symbole/herz.webp" and wieder["text"] == "5", wieder
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


def test_unbegrenzt_ohne_kauf_bleibt_rot(browser, basis):
    """?alle=1 (Testmodus) macht die Leben unbegrenzt, gekauft ist aber
    nichts: das Herz bleibt rot, mit ∞."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite)
        seite.page.goto(basis + "/app/index.html?alle=1")
        seite.bereit()
        seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
        assert seite.js("() => ALLE_FREI && !premium && unlimited()")
        herz = seite.js(HERZ, "#livesKnopf")
        assert herz["bild"] == "symbole/herz.webp" and herz["text"] == "∞", herz
        assert seite.fehler == []
    finally:
        ctx.close()


SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
GEMALT_WEG = ["🏁", "⭐", "💙", "✨", "✉"]

# Ein Knopf oder Kasten: seine Symbolbilder (Name, alt, aria-hidden, geladen)
# und sein Text
BILDER_IN = """(sel) => { const e = document.querySelector(sel); if(!e) return null;
  return {bilder: [...e.querySelectorAll('img.sym')].map(i => [i.getAttribute('src'), i.getAttribute('alt'),
                    i.getAttribute('aria-hidden'), i.complete && i.naturalWidth > 0]),
          text: e.innerText.replace(/\\s+/g, ' ').trim()}; }"""


def _bild(name):
    return ["symbole/%s.webp" % name, "", "true", True]


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_gemalt_statt_emoji(browser, basis, sprache):
    """Level-Test, "Zmaj bewerten", "Danke!" und die E-Mail im Profil tragen
    das gemalte Bild, der Text daneben kein Emoji mehr - in jeder Sprache."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, sprache=sprache)
        # wie innerText mit zusammengefassten Leerraeumen (fr: "Merci" und "!"
        # mit geschuetztem Leerzeichen dazwischen)
        t = lambda k: " ".join(seite.js("k => t(k)", k).split())  # noqa: E731
        # Level-Test (frei, weil alle Woerter des Levels gewusst sind)
        seite.js("() => { CATEGORIES[0].words.forEach(w => known.add(w.id)); openLevel(0); }")
        seite.page.wait_for_function("() => [...document.querySelectorAll('#btnTest img.sym')].every(i => i.complete)")
        test = seite.js(BILDER_IN, "#btnTest")
        assert test == {"bilder": [_bild("ziel")], "text": t("level.test")}, test

        # Die Bewertungskarte
        seite.js("() => { homeMode = 'words'; showHome(); zeigeBewertung(); }")
        seite.page.wait_for_function("() => [...document.querySelectorAll('#bwJa img.sym')].every(i => i.complete)")
        ja = seite.js(BILDER_IN, "#bwJa")
        assert ja == {"bilder": [_bild("stern")], "text": t("bew.bewerten")}, ja
        seite.page.click("#bwVor")

        # Vorschlag ohne Formular: das Mailprogramm (hier nachgestellt), davor "Danke!"
        seite.js("() => { feedbackPerMail = (text, notiz) => { notiz.textContent = 'MAIL'; }; }")
        seite.page.fill("#bwText", "Probe")
        seite.page.click("#bwSenden")
        seite.page.wait_for_function("() => !!document.querySelector('#bwNote img.sym-herzblau')")
        seite.page.wait_for_function("() => document.querySelector('#bwNote img.sym-herzblau').complete")
        note = seite.js(BILDER_IN, "#bwNote")
        assert note == {"bilder": [_bild("herzblau")], "text": t("bew.danke") + " MAIL"}, note
        seite.page.click("#bwZu")

        # Profil mit Konto: der Brief vor der Adresse
        seite.js("() => { kontoMail = 'ich@probe.example'; showKonto(); }")
        seite.page.wait_for_function("() => [...document.querySelectorAll('#setProfilMail img.sym')].every(i => i.complete)")
        mail = seite.js(BILDER_IN, "#setProfilMail")
        assert mail == {"bilder": [_bild("brief")], "text": "ich@probe.example"}, mail

        for k in ("level.test", "bew.bewerten", "bew.danke"):
            assert not [e for e in GEMALT_WEG if e in t(k)], (k, t(k))
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


def test_funken_an_der_goldenen_flamme(browser, basis):
    """Ab 365 Tagen funkeln drei gemalte Funken um die Flamme, oben und in
    der Statistik - geladen, so gross wie die Schrift des Funkens (vorher
    das Zeichen ✨), innerhalb des Kastens mit aria-hidden."""
    ctx, seite = _kontext(browser, basis)
    try:
        seite.page.clock.set_fixed_time(datetime.datetime.combine(SPAETER, datetime.time(12, 0)))
        _starten(seite, {"einstufung": {"tag": SPAETER.isoformat(), "wahl": "neu", "bis": ""},
                         "tage": [(SPAETER - datetime.timedelta(days=i)).isoformat() for i in range(0, 365)]})
        seite.page.wait_for_function("() => [...document.querySelectorAll('.funke img')].every(i => i.complete)")
        f = seite.js("""() => [...document.querySelectorAll('.seriezahl .funke')].map(x => {
            const i = x.querySelector('img.sym'), r = i.getBoundingClientRect();
            return {bild: i.getAttribute('src'), geladen: i.naturalWidth > 0, alt: i.getAttribute('alt'),
                    text: x.textContent, b: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10,
                    schrift: parseFloat(getComputedStyle(x).fontSize),
                    versteckt: !!x.closest('[aria-hidden="true"]')}; })""")
        assert len(f) == 3, f
        for x in f:
            assert x["bild"] == "symbole/funken.webp" and x["geladen"] and x["alt"] == "" and x["text"] == "", x
            assert abs(x["b"] - x["schrift"]) < 0.6 and x["b"] == x["h"] and x["versteckt"], x
        assert seite.js("() => document.getElementById('serieFlamme').classList.contains('stufe-gold')")
        statistik = seite.js("() => { const d = document.createElement('div'); d.innerHTML = flammeHtml();"
                             " return [...d.querySelectorAll('.funke img.sym')].map(i => i.getAttribute('src')); }")
        assert statistik == ["symbole/funken.webp"] * 3, statistik
        assert seite.fehler == []
    finally:
        ctx.close()
