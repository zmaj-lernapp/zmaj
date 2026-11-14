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
"""
import datetime

import pytest
from conftest import Seite


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
