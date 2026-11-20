# -*- coding: utf-8 -*-
"""Die App laedt ganz, in Chromium und WebKit (Aufteilung 1.5, PLAN G7).

Das Skript kann in Dateien unter js/ geteilt sein. Am Ende jedes Teils zaehlt
eine Zeile teileDa hoch; vor init() prueft die App, ob alle Teile ganz gelaufen sind
(TEILE_ERWARTET). Fehlt einer, startet sie nicht mit halbem Zustand, sondern
zeigt einen Fehler und speichert nichts. skripteDa wird direkt vor init()
wahr, erst dann arbeiten die Horcher, die in spaetere Dateien greifen.

Ungeteilt gilt dasselbe: dann laufen alle Zaehler in einem Skript.
"""
import io
import json
import os

import app_quelle
import pytest
from conftest import Seite

ZUSTAND = "() => [teileDa, TEILE_ERWARTET, skripteDa]"


@pytest.fixture(params=["chromium", "webkit"])
def motor(request):
    return request.getfixturevalue("browser" if request.param == "chromium" else "webkit")


def test_alle_teile_geladen(motor, basis, heute_stand):
    ctx = motor.new_context(viewport={"width": 360, "height": 640}, locale="de-DE", service_workers="block")
    try:
        s = Seite(ctx.new_page(), basis)
        s.starten(stand=heute_stand())
        teile, erwartet, da = s.js(ZUSTAND)
        assert teile == erwartet == 34 and da is True
        assert s.fehler == [] and s.fremd == []
    finally:
        ctx.close()


def test_fehlt_ein_teil_startet_die_app_nicht(seite, basis, heute_stand, wurzelordner):
    """Als waere ein Teil beim Laden ausgefallen: eine Zaehlzeile zu
    wenig (hier: einer mehr erwartet). Dann kein Start, der Fehler steht da,
    und der Lernstand bleibt, wie er war - auch beim Wechsel in den
    Hintergrund, der sonst speichert."""
    app = os.path.join(wurzelordner, "app")
    datei = [d for d in app_quelle.dateien(app)
             if "const TEILE_ERWARTET = 34;" in io.open(os.path.join(app, d), encoding="utf-8").read()]
    assert len(datei) == 1, datei
    text = io.open(os.path.join(app, datei[0]), encoding="utf-8", newline="").read()
    text = text.replace("const TEILE_ERWARTET = 34;", "const TEILE_ERWARTET = 35;")
    art = "text/html" if datei[0].endswith(".html") else "text/javascript"
    seite.page.route("**/app/" + datei[0], lambda r: r.fulfill(
        status=200, content_type=art + "; charset=utf-8", body=text))
    stand = heute_stand(muenzen=7)
    seite.page.goto(basis + "/leer")
    seite.js("""s => { localStorage.clear(); localStorage.setItem('zmaj_stand', s);
        localStorage.setItem('zmaj_sprache', 'de'); }""", json.dumps(stand))
    seite.page.goto(basis + "/app/index.html")
    seite.page.wait_for_function("() => document.getElementById('err').style.display === 'block'", timeout=15000)
    assert any("Zmaj startet nicht: App-Teile: 34 von 35" in f for f in seite.fehler), seite.fehler
    assert seite.js("() => [skripteDa, document.getElementById('btnSettings').style.display]") == [False, "none"]
    assert "34 von 35" in seite.js("() => document.getElementById('err').textContent")
    seite.js("""() => { Object.defineProperty(document, 'hidden', {value: true, configurable: true});
        document.dispatchEvent(new Event('visibilitychange')); }""")
    seite.page.wait_for_timeout(300)
    assert json.loads(seite.js("() => localStorage.getItem('zmaj_stand')")) == stand
