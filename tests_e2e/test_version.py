# -*- coding: utf-8 -*-
"""Die App zeigt ihre Versionsnummer (30.10.2026, Ajdin: "ja mach so").

Bis v108 stand "Zmaj v1.0" fest im Text. Jetzt setzt t() {version} aus
APP_VERSION ein - in der Fusszeile (app.fuss) und in der Versionszeile der
Einstellungen (app.ueber_kurz), in allen acht Sprachen. Beim Bauen
ueberschreibt app_bauen.version_einsetzen() APP_VERSION in der Kopie mit
versionName aus build.gradle der Huelle; der zweite Test baut sich so eine
Kopie (wie test_haut_alle.py mit dem Pruefwert) und liefert sie statt
app/index.html aus.

Die Versionszeile ist zugleich der versteckte Schalter (siebenmal tippen,
dann ein Wort). Hier nur: sieben Tipps oeffnen die Abfrage weiterhin, und
Abbrechen schliesst sie. Das Wort selbst steht nirgends; was es schaltet,
prueft test_haut_alle.py mit einem Testwort.
"""
import os
import shutil

import pytest

import sprachen

SPRACHCODES = [s["code"] for s in sprachen.SPRACHEN]
TEXTE = """() => ({
    version: APP_VERSION,
    fuss: document.querySelector('footer[data-t="app.fuss"]').textContent,
    zeile: document.getElementById('ueberZeile').textContent
})"""


@pytest.mark.parametrize("sprache", SPRACHCODES)
def test_fuss_und_versionszeile_zeigen_app_version(seite, heute_stand, sprache):
    seite.starten(sprache=sprache, stand=heute_stand())
    t = seite.js(TEXTE)
    version = t["version"]
    assert version and version != "1.0", t
    assert t["fuss"].startswith("Zmaj v%s · " % version), t
    assert (" %s · " % version) in t["zeile"] and t["zeile"].startswith("Zmaj "), t
    for text in (t["fuss"], t["zeile"]):
        assert "{version}" not in text and "1.0" not in text, t
    # In den Einstellungen zu sehen, nicht nur im Quelltext der Seite
    seite.page.locator("#btnSettings").click()
    zeile = seite.page.locator("#ueberZeile")
    assert zeile.is_visible()
    assert version in zeile.inner_text()
    assert seite.fehler == [] and seite.fremd == []


@pytest.fixture(scope="module")
def paket_html(wurzelordner, tmp_path_factory):
    """Die Demo, wie app_bauen.py sie fuer die Test-App einsetzt."""
    import app_bauen

    ordner = tmp_path_factory.mktemp("versionprobe")
    kopie = ordner / "index.html"
    shutil.copyfile(os.path.join(wurzelordner, "app", "index.html"), str(kopie))
    assert app_bauen.version_einsetzen("7.13", test=True, pfad=str(kopie)) == "7.13-test"
    return kopie.read_bytes()


def test_eingesetzte_version_erscheint(seite, heute_stand, paket_html):
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=paket_html))
    seite.starten(stand=heute_stand())
    t = seite.js(TEXTE)
    assert t["version"] == "7.13-test"
    assert t["fuss"].startswith("Zmaj v7.13-test · Einstellungen über"), t
    assert t["zeile"].startswith("Zmaj Version 7.13-test · Bosnisch lernen"), t

    # Versteckter Schalter: sieben Tipps auf die Versionszeile oeffnen die
    # Abfrage wie vorher; Abbrechen schliesst sie, ohne etwas zu schalten.
    seite.page.locator("#btnSettings").click()
    for _ in range(7):
        seite.page.locator("#ueberZeile").click()
    seite.page.locator("#frWort").wait_for()
    seite.page.locator("#frAb").click()
    assert seite.page.locator("#frWort").count() == 0
    assert seite.js("() => localStorage.getItem('zmaj_dauer2')") is None
    assert seite.js(TEXTE)["zeile"].startswith("Zmaj Version 7.13-test")
    assert seite.fehler == [] and seite.fremd == []
