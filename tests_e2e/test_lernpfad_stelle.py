# -*- coding: utf-8 -*-
"""Zurueck aus einem Level landet dort im Lernpfad, wo man war.

Pruefbericht 1.3, G11: showView() scrollt nach oben, wer weit unten in einer
langen Sektion lernte, musste nach jedem Zurueck neu hinunterscrollen. Oben
oeffnet der Lernpfad weiterhin, wenn man von anderswo kommt, siehe den
Kommentar bei LERNPFAD in index.html.
"""
import pytest


@pytest.fixture
def lernpfad(browser, basis, heute_stand):
    """Lernpfad auf 360 Punkten, Sektion 10 offen, ein Level weit unten im Blick."""
    from conftest import Seite
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE", service_workers="block")
    seite = Seite(ctx.new_page(), basis)
    seite.starten(stand=heute_stand())
    ids = seite.js("() => CATEGORIES.map(c => c.id)")
    seite.starten(stand=heute_stand(bestanden=ids[:129]))
    seite.js("() => document.getElementById('vorspann').click()")
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    seite.js("() => { homeMode = 'words'; showHome(); if(offeneSektion !== SECTIONS[9].id) sektionAufklappen(SECTIONS[9].id); }")
    yield seite
    ctx.close()


def _level_antippen(seite, von_unten=3):
    """Tippt ein Level weit unten an und gibt die Scrollstelle davor zurueck."""
    knoten = seite.page.locator("#sections .section:not(.zu) .node")
    k = knoten.nth(knoten.count() - von_unten)
    k.evaluate("e => e.scrollIntoView({block: 'center'})")
    vorher = seite.js("() => scrollY")
    assert vorher > 1000, vorher
    k.click()
    assert seite.js("() => [sichtbar('levelView'), scrollY]") == [True, 0]
    return vorher


def test_zurueck_aus_dem_level(lernpfad):
    vorher = _level_antippen(lernpfad)
    lernpfad.page.locator("#btnBack").click()
    assert lernpfad.js("() => [sichtbar('pfad'), scrollY]") == [True, vorher]
    assert lernpfad.fehler == []


def test_zurueck_nach_der_lektion(lernpfad):
    vorher = _level_antippen(lernpfad)
    lernpfad.page.click("#btnLesson")
    lernpfad.durchspielen("lBody", "Lx")
    lernpfad.page.click("#lPfad")
    assert lernpfad.js("() => [sichtbar('pfad'), scrollY]") == [True, vorher]
    assert lernpfad.fehler == []


def test_zurueck_nach_dem_test(lernpfad):
    vorher = _level_antippen(lernpfad)
    lernpfad.js("() => { cur().words.forEach(w => known.add(w.id)); showLevelHome(); startTest(); }")
    lernpfad.durchspielen("tBody", "Tx")
    lernpfad.page.click("#tBack")
    pfad, y = lernpfad.js("() => [sichtbar('pfad'), scrollY]")
    assert pfad and abs(y - vorher) < 40, (y, vorher)     # das Level ist jetzt bestanden: Karte etwas anders
    assert lernpfad.fehler == []


def test_blaettern_im_level_behaelt_die_stelle(lernpfad):
    vorher = _level_antippen(lernpfad)
    lernpfad.page.click("#navPrev")
    assert lernpfad.js("() => scrollY") == 0
    lernpfad.page.locator("#btnBack").click()
    assert lernpfad.js("() => scrollY") == vorher
    assert lernpfad.fehler == []


def test_von_anderswo_oeffnet_der_lernpfad_oben(lernpfad):
    # Ueber die Einstellungen zurueck
    _level_antippen(lernpfad)
    lernpfad.js("() => showSettings()")
    lernpfad.js("() => showHome()")
    assert lernpfad.js("() => [sichtbar('pfad'), scrollY]") == [True, 0]
    # Reiter wechseln, auch direkt nach einem Level
    _level_antippen(lernpfad)
    lernpfad.page.locator("#btnBack").click()
    lernpfad.page.click("#modeStories")
    assert lernpfad.js("() => scrollY") == 0
    lernpfad.page.click("#modeWords")
    assert lernpfad.js("() => [sichtbar('pfad'), scrollY]") == [True, 0]
    # Der Merker gilt nur einmal: Lernpfad neu oeffnen geht nach oben
    lernpfad.js("() => { homeMode = 'words'; showHome(); }")
    assert lernpfad.js("() => scrollY") == 0
    assert lernpfad.fehler == []
