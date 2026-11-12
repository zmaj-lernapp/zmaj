# -*- coding: utf-8 -*-
"""Der Vorspann: voll nur beim ersten Start des Tages, sonst kuerzer.

Pruefbericht 1.3, G18, entschieden am 06.11.2026. Vorher hielt der Vorspann jeden
Kaltstart auf ueber 4,5 s, obwohl die App nach 0,14 s bereit war. Beim ersten
Start des Tages bleibt alles wie bisher, damit man den Namen lesen kann. Danach
laeuft nur die Bewegung, ohne die Haltezeit.
"""
import datetime

import pytest

from conftest import Seite

WEG = "() => !document.getElementById('vorspann')"
ZEIT = "() => performance.now()"
MIN = "() => vorspannMin"
TAG = "() => localStorage.getItem('zmaj_vorspann_tag')"
LANG, KURZ, OHNE_BEWEGUNG = 3900, 2400, 1400


def _bis_weg(seite):
    seite.page.wait_for_function(WEG, timeout=15000)
    return seite.js(ZEIT)


def test_erster_start_des_tages_voll_danach_kuerzer(seite, heute_stand):
    seite.starten(stand=heute_stand())
    assert seite.js(MIN) == LANG
    assert seite.js(TAG) == datetime.date.today().isoformat()
    erst = _bis_weg(seite)
    assert erst >= LANG, erst

    # Zweiter Start am selben Tag: nur die Bewegung, die laeuft aber zu Ende
    seite.neu_laden()
    assert seite.js(MIN) == KURZ
    zweit = _bis_weg(seite)
    assert KURZ <= zweit < LANG, (erst, zweit)
    assert erst - zweit > 1000, (erst, zweit)

    # Und der dritte ebenso
    seite.neu_laden()
    assert seite.js(MIN) == KURZ
    assert seite.fehler == []


def test_am_naechsten_tag_wieder_voll(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.page.goto(seite.basis + "/leer")
    seite.js("() => localStorage.setItem('zmaj_vorspann_tag', '2026-01-01')")
    seite.starten(stand=heute_stand(), leeren=False)
    assert seite.js(MIN) == LANG
    assert seite.js(TAG) == datetime.date.today().isoformat()
    assert seite.fehler == []


def test_antippen_ueberspringt_auch_den_kurzen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.neu_laden()
    seite.js("() => document.getElementById('vorspann').click()")
    assert _bis_weg(seite) < KURZ
    assert seite.fehler == []


def test_ohne_bewegung_bleibt_es_bei_der_festen_zeit(browser, basis, heute_stand):
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                              service_workers="block", reduced_motion="reduce")
    seite = Seite(ctx.new_page(), basis)
    try:
        seite.starten(stand=heute_stand())
        assert seite.js(MIN) == OHNE_BEWEGUNG
        seite.neu_laden()
        assert seite.js(MIN) == OHNE_BEWEGUNG
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("wert", ["", "kaputt", "2099-12-31"])
def test_komischer_merker_gibt_den_vollen_vorspann(seite, heute_stand, wert):
    seite.page.goto(seite.basis + "/leer")
    seite.js("(w) => localStorage.setItem('zmaj_vorspann_tag', w)", wert)
    seite.starten(stand=heute_stand(), leeren=False)
    assert seite.js(MIN) == LANG
    assert seite.js(TAG) == datetime.date.today().isoformat()
    assert seite.fehler == []
