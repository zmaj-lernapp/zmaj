# -*- coding: utf-8 -*-
"""Sandbox der Test-App (08.11.2026) - im echten Browser.

Ajdin: "nein bei der test app lass sie offen das ist wie eine sandbox app",
und "ja" zu einem festen Schalter "alles offen". Geprueft wird:
  - Im Browser bleibt alles gesperrt wie bisher, auch mit der Nummer der
    Test-App ("-test") im Paket.
  - Nachgestellte Test-App (window.Capacitor mit App.getInfo() und der
    App-ID de.smartdragon.zmaj.test, Paket mit "-test" wie aus
    app_bauen.version_einsetzen): jedes Level, jede Sektion, jeder Test und
    jede Geschichte ist offen, ein spaetes Level laesst sich antippen, die
    Versionszeile sagt es - und passed, known und read bleiben leer, auch
    im gespeicherten Stand.
  - Dieselbe Nachstellung mit der App-ID der echten App, oder mit der
    Test-ID und einem Store-Paket ohne "-test": alles gesperrt.
Die Erkennung selbst prueft tests/test_sandbox.py.
"""
import os
import shutil

import pytest

TEST_ID = "de.smartdragon.zmaj.test"
ECHTE_ID = "de.smartdragon.zmaj"

# Das nachgebaute Android: nur App, wie @capacitor/app es anbietet.
HANDY = r"""
((id) => {
  window.probe = {getInfo: 0};
  window.Capacitor = {isNativePlatform: () => true, Plugins: {App: {
    getInfo: async () => { window.probe.getInfo++;
      return {name: 'Zmaj Test', id: id, build: '116', version: '1.4-test'}; },
    addListener: async () => ({remove: async () => {}}),
    exitApp: () => {},
  }}};
})(%s);
"""

LAGE = """() => ({
  sandbox: SANDBOX,
  offen: CATEGORIES.filter((c, i) => isUnlocked(i)).length,
  level: CATEGORIES.length,
  tests: CATEGORIES.filter(c => testAllowed(c)).length,
  geschichten: STORIES.filter((s, i) => storyUnlocked(i)).length,
  alleGeschichten: STORIES.length,
  sektionenZu: document.querySelectorAll('#sections .section.locked').length,
  sektionen: document.querySelectorAll('#sections .section').length,
  levelZu: document.querySelectorAll('#sections .node.locked').length,
  // Seit den Stufen-Reitern (13.11.2026) steht nur ein Reiter im Lernpfad
  levelImReiter: reiterLevel(angezeigteStufe()).length,
  reiter: [...document.querySelectorAll('#reiterLeiste button')].map(b => b.className),
  fuss: document.querySelector('footer[data-t="app.fuss"]').textContent,
  zeile: document.getElementById('ueberZeile').textContent,
  bestanden: passed.size, gewusst: known.size, gelesen: read.size,
  leben: unlimited(),
  gefragt: window.probe ? window.probe.getInfo : null,
})"""


def _paket(wurzelordner, tmp_path_factory, test):
    import app_bauen

    ordner = tmp_path_factory.mktemp("sandbox_test" if test else "sandbox_store")
    kopie = ordner / "index.html"
    shutil.copyfile(os.path.join(wurzelordner, "app", "index.html"), str(kopie))
    soll = "1.4-test" if test else "1.4"
    assert app_bauen.version_einsetzen("1.4", test=test, pfad=str(kopie)) == soll
    return kopie.read_bytes()


@pytest.fixture(scope="module")
def test_paket(wurzelordner, tmp_path_factory):
    """Die Demo, wie app_bauen.py sie fuer die Test-App einsetzt."""
    return _paket(wurzelordner, tmp_path_factory, True)


@pytest.fixture(scope="module")
def store_paket(wurzelordner, tmp_path_factory):
    """Die Demo, wie app_bauen.py --aab sie einsetzt."""
    return _paket(wurzelordner, tmp_path_factory, False)


def _ausliefern(seite, html):
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=html))


def _gesperrt(lage):
    assert lage["sandbox"] is False, lage
    assert lage["offen"] == 1 and lage["level"] > 20, lage
    assert lage["tests"] == 0, lage
    assert lage["sektionenZu"] > 0 and lage["levelZu"] == lage["levelImReiter"] - 1, lage
    assert lage["reiter"] == ["offen", "zu", "zu", "zu", "bald"], lage
    if lage["alleGeschichten"] > 1:
        assert lage["geschichten"] == 1, lage
    for text in (lage["fuss"], lage["zeile"]):
        assert "Sandbox" not in text, lage


def test_browser_bleibt_gesperrt(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _gesperrt(seite.js(LAGE))
    assert seite.fehler == [] and seite.fremd == []


def test_browser_mit_test_paket_bleibt_gesperrt(seite, heute_stand, test_paket):
    """Die Nummer allein reicht nicht: ohne Android bleibt es zu."""
    _ausliefern(seite, test_paket)
    seite.starten(stand=heute_stand())
    lage = seite.js(LAGE)
    assert lage["fuss"].startswith("Zmaj v1.4-test · Einstellungen"), lage
    _gesperrt(lage)
    assert seite.fehler == [] and seite.fremd == []


def test_echte_app_id_bleibt_gesperrt(seite, heute_stand, test_paket):
    _ausliefern(seite, test_paket)
    seite.page.add_init_script(HANDY % ('"%s"' % ECHTE_ID))
    seite.starten(stand=heute_stand())
    lage = seite.js(LAGE)
    _gesperrt(lage)
    assert lage["gefragt"] == 1, lage
    assert seite.fehler == [] and seite.fremd == []


def test_store_paket_fragt_gar_nicht_erst(seite, heute_stand, store_paket):
    """Test-ID, aber ein Paket ohne "-test" (wie --aab): zu, und Android
    wird nicht einmal gefragt."""
    _ausliefern(seite, store_paket)
    seite.page.add_init_script(HANDY % ('"%s"' % TEST_ID))
    seite.starten(stand=heute_stand())
    lage = seite.js(LAGE)
    _gesperrt(lage)
    assert lage["gefragt"] == 0, lage
    assert seite.fehler == [] and seite.fremd == []


def test_test_app_alles_offen_ohne_lernstand(seite, heute_stand, test_paket):
    _ausliefern(seite, test_paket)
    seite.page.add_init_script(HANDY % ('"%s"' % TEST_ID))
    seite.starten(stand=heute_stand())
    lage = seite.js(LAGE)
    assert lage["sandbox"] is True and lage["gefragt"] == 1, lage
    assert lage["offen"] == lage["level"] and lage["tests"] == lage["level"], lage
    assert lage["geschichten"] == lage["alleGeschichten"], lage
    assert lage["sektionenZu"] == 0 and lage["levelZu"] == 0 and lage["sektionen"] >= 4, lage
    assert lage["reiter"] == ["offen", "offen", "offen", "offen", "bald"], lage
    assert lage["fuss"].startswith("Zmaj v1.4-test · Sandbox: alles offen · Einstellungen"), lage
    assert lage["zeile"].startswith("Zmaj Version 1.4-test · Sandbox: alles offen · "), lage
    # Nur die Sperren: Leben bleiben begrenzt wie in der echten App
    assert lage["leben"] is False, lage
    assert (lage["bestanden"], lage["gewusst"], lage["gelesen"]) == (0, 0, 0), lage

    # Im letzten Reiter die letzte Sektion aufklappen und ihr letztes Level antippen
    seite.page.click("#reiterLeiste button[data-stufe='B2']")
    letzte = seite.page.locator("#sections .section").last
    letzte.locator(".skopf").click()
    letzte.locator(".node").last.click()
    assert seite.page.locator("#levelView").is_visible()
    kopf = seite.js("""() => ({i: catIdx, n: CATEGORIES.length,
        test: document.getElementById('btnTest').disabled,
        testText: document.getElementById('btnTest').textContent.trim(), frei: t('level.test'),
        ziel: !!document.querySelector('#btnTest img.sym-ziel')})""")
    assert kopf["i"] == kopf["n"] - 1, kopf
    assert kopf["test"] is False and kopf["testText"] == kopf["frei"] and kopf["ziel"], kopf
    # Auch der versteckte Zahnarzt-Teil waere offen (nur im Arbeitsspeicher)
    za = seite.js("""() => { if(!ZA) return null; const alt = zaSchalter.an; zaSchalter.an = true;
        const offen = zaLevel().every((c, k) => isUnlocked(CATEGORIES.length + k));
        zaSchalter.an = alt; return offen; }""")
    assert za in (True, None)

    # Nichts davon steht im Lernstand, auch nicht im gespeicherten
    stand = seite.js("async () => { await saveProgress(); return JSON.parse(localStorage.getItem('zmaj_stand')); }")
    for feld in ("bestanden", "gewusst", "gelesen"):
        assert not stand.get(feld), (feld, stand.get(feld))
    assert seite.js("() => [passed.size, known.size, read.size]") == [0, 0, 0]
    assert seite.fehler == [] and seite.fremd == []
