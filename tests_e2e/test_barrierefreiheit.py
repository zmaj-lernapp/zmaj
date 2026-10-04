# -*- coding: utf-8 -*-
"""axe-core über die Hauptansichten: nach barrierefreiheit_richten.py kein
ernster und kein kritischer Verstoß mehr.

Läuft NICHT mit dem normalen  python3 -m pytest  (testpaths = tests), weil
es einen Browser braucht und etwa eine Minute dauert:

    python3 -m pip install playwright
    python3 -m pytest tests_e2e -q
    ZMAJ_CHROMIUM=/pfad/zu/chrome python3 -m pytest tests_e2e -q   # eigener Chromium

Die Demo wird in ein Zeitverzeichnis gebaut, dort - falls index.html noch
nicht gerichtet ist - mit barrierefreiheit_richten.py gerichtet und über
einen lokalen Server geladen. An web/ ändert sich nichts.

axe liegt in tests_e2e/vendor/ (MPL-2.0, siehe REUSE.toml) und wird nur hier
in die Seite gespritzt. In web/ hat es nichts zu suchen: die App lädt
nichts, was sie nicht braucht.

Gemessen am 04.10.2026: vorher 4 kritische und bis zu 7 ernste Verstöße je
Ansicht, nachher keine. Bericht: Zmaj Berichte/barrierefreiheit-2026-10-04.md
"""
import functools
import http.server
import io
import json
import os
import socketserver
import sys
import threading
import time

import pytest

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WURZEL)
sys.path.insert(0, os.path.join(WURZEL, "store", "bilder_machen"))
AXE = os.path.join(WURZEL, "tests_e2e", "vendor", "axe.min.js")

playwright = pytest.importorskip("playwright.sync_api")

# (Name, JavaScript). Wie in store/bilder_machen/bilder_playwright.py.
ANSICHTEN = [
    ("start", "homeMode='words'; showHome(); scrollTo(0,0); await warte(800);"),
    ("geschichten", "homeMode='stories'; showHome(); await warte(600);"),
    ("wiederholen", "homeMode='topf'; showHome(); await warte(600);"),
    ("level", "homeMode='words'; showHome(); openLevel(12); await warte(600);"),
    ("lektion", "openLevel(12); await warte(400); startLesson(); await warte(900);"),
    ("lektion-auswahl", "const z = Lx.queue.findIndex((q,i) => i>=Lx.i && q.typ==='mc');"
     " while(z>=0 && Lx.i<z){ await window.__antworte(true,'lBody',()=>Lx); } await warte(700);"),
    ("lektion-richtig", "const q = Lx.queue[Lx.i];"
     " const o = [...document.querySelectorAll('#lBody .opt')].find(o => o.textContent === q.w.bs);"
     " if(o) o.click(); await warte(900);"),
    ("test", "Lx=null; openLevel(3); await warte(400); startTest(); await warte(900);"),
    ("einstellungen", "Lx=null; showSettings(); await warte(800);"),
    ("geschichte", "openStory(3); await warte(800); stilleBitte();"),
    ("laden", "showLaden(); await warte(800);"),
]


@pytest.fixture(scope="module")
def seite_basis(tmp_path_factory):
    import barrierefreiheit_richten
    import demo_bauen
    ziel = str(tmp_path_factory.mktemp("demo") / "site")
    demo_bauen.main(["--ziel", ziel])
    pfad = os.path.join(ziel, "index.html")
    html = io.open(pfad, encoding="utf-8", newline="").read()
    if barrierefreiheit_richten.KENNUNG not in html:
        neu, fehler = barrierefreiheit_richten.anwenden(html)
        assert not fehler, fehler
        io.open(pfad, "w", encoding="utf-8", newline="").write(neu)

    class Leise(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Leise, directory=ziel))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()


# Den Browser stellt tests_e2e/conftest.py (eine Playwright-Sitzung fuer
# alle Tests - zwei Sitzungen im selben Prozess vertraegt die Sync-API nicht).


@pytest.mark.parametrize("sprache,schema", [("en", "light"), ("de", "light"), ("en", "dark")])
def test_keine_ernsten_verstoesse(seite_basis, browser, sprache, schema):
    import bilder_playwright
    kontext = browser.new_context(viewport={"width": 390, "height": 844}, locale=sprache, color_scheme=schema)
    seite = kontext.new_page()
    js = lambda code: seite.evaluate(  # noqa: E731
        "async () => { const warte = ms => new Promise(r => setTimeout(r, ms)); " + code + " }")
    # Stand auf einer leeren Seite desselben Ursprungs setzen (siehe conftest.py,
    # Seite.starten): die laufende App wuerde ihn beim Wegnavigieren ueberschreiben.
    seite.goto(seite_basis + "/leer")
    js("localStorage.clear(); localStorage.setItem('zmaj_stand', %s); "
       "localStorage.setItem('zmaj_einwilligung', JSON.stringify({wahl:'nein',stand:1,zeit:new Date().toISOString()})); "
       "localStorage.setItem('zmaj_sprache', %s); return 1"
       % (json.dumps(bilder_playwright.lernstand()), json.dumps(sprache)))
    seite.goto(seite_basis + "/index.html?neu=%d" % time.time())
    seite.wait_for_function("typeof openLevel === 'function' && typeof Lx !== 'undefined'", timeout=30000)
    seite.wait_for_timeout(6000)       # Vorspann und Drache
    js(io.open(os.path.join(WURZEL, "store", "bilder_machen", "antworte.js"), encoding="utf-8").read())
    seite.add_script_tag(path=AXE)
    funde = []
    try:
        for name, code in ANSICHTEN:
            js(code + " return 1")
            assert seite.evaluate("document.documentElement.lang") == sprache
            verstoesse = seite.evaluate("""async () => (await axe.run(document, {resultTypes:['violations']}))
                .violations.filter(v => v.impact === 'serious' || v.impact === 'critical')
                .map(v => v.id + ' (' + v.impact + '): ' + v.nodes.map(n => n.target.join(' ')).join(', '))""")
            funde += ["%s/%s %s" % (sprache, name, v) for v in verstoesse]
    finally:
        kontext.close()
    assert not funde, "\n".join(funde)
