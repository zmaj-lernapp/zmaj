# -*- coding: utf-8 -*-
"""Browser-Tests: die echte App in Chromium, so wie ein Lernender sie sieht.

Getrennt von tests/, weil sie Playwright und einen Browser brauchen und
eine halbe Minute laufen statt zwei Sekunden. `python3 -m pytest` laeuft
weiter nur tests/ (testpaths in pyproject.toml); diese hier mit

    python3 -m pytest tests_e2e -q
    ZMAJ_CHROMIUM=/pfad/zu/chromium python3 -m pytest tests_e2e -q

Ausgeliefert wird die Demo aus demo_bauen.py, nicht web/ selbst: sie bringt
ihren Inhalt als JSON mit (web/inhalt/ ist gitignored und fehlt in einem
frischen Checkout), und ein schlichter Dateiserver reicht. Ohne /api/daten
und /api/konto laeuft die App dann genau wie auf dem Handy - im
Geraetemodus, Stand in localStorage.

Die Muster stammen aus store/bilder_machen/bilder_playwright.py: freier
Port, Stand vorab in localStorage, App-Funktionen direkt aufrufen.
"""
import functools
import http.server
import io
import json
import os
import shutil
import socketserver
import sys
import threading

import pytest

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WURZEL)

# Fertig gestartet ist die App, wenn nachAnmeldung() durch ist: erst dort
# erscheint der Einstellungsknopf. Genau daran scheiterte der kaputte Import
# vom 04.10.2026 (siehe import_richten.py) - deshalb ist das die Bedingung.
BEREIT = ("typeof CATEGORIES !== 'undefined' && CATEGORIES && CATEGORIES.length > 0"
          " && document.getElementById('btnSettings').style.display === 'inline-block'")

# Beantwortet die laufende Lektion bzw. den Test bis zum Ende, immer richtig.
# Die Erkennung der Aufgabenarten ist aus store/bilder_machen/antworte.js
# uebernommen. Anders als dort wartet sie nicht fest 1,2 s je Aufgabe (das
# braucht der Bildschirmfoto-Lauf, damit man das Gruen sieht), sondern genau
# so lange, bis die App den naechsten Schritt gemacht hat. Sonst dauerte eine
# Lektion eine halbe Minute.
DURCHSPIELEN = r"""
async ([feld, art]) => {
  const X = () => art === 'Lx' ? Lx : Tx;
  const liste = () => X().qs || X().queue;
  const body = document.getElementById(feld);
  const warte = ms => new Promise(r => setTimeout(r, ms));
  const bis = async (bed, was) => {
    const ende = Date.now() + 8000;
    while(!bed()){ if(Date.now() > ende) throw new Error('wartet vergeblich auf: ' + was); await warte(15); }
  };
  const typen = [];
  for(let n = 0; X().i < liste().length; n++){
    if(n > 200) throw new Error('mehr als 200 Schritte');
    const i = X().i, q = liste()[i];
    await bis(() => body.dataset.i === String(i) && !body.querySelector('.weiterbox'), 'Aufgabe ' + i);
    typen.push(q.typ);
    if(q.typ === 'intro'){ body.querySelector('#xNext').click(); }
    else if(q.typ === 'speak'){ body.querySelector('#xSkip').click(); }
    else if(q.typ === 'gap' || q.typ === 'type'){
      body.querySelector('#xIn').value = (q.typ === 'gap' ? q.s.answer : q.w.bs).split(' / ')[0];
      body.querySelector('#xCheck').click();
    } else {
      const soll = q.typ === 'gram' ? q.g.richtig : (q.typ === 'mcrev' ? q.w.de : q.w.bs);
      const b = [...body.querySelectorAll('.opt')].find(o => o.textContent === soll);
      if(!b) throw new Error('kein Knopf "' + soll + '" bei ' + q.typ);
      b.click();
    }
    await bis(() => X().i > i, 'Antwort auf ' + i);
    const weiter = body.querySelector('.weiterbox .btn');
    if(weiter){ weiter.click(); await bis(() => !body.querySelector('.weiterbox'), 'Weiter nach ' + i); }
  }
  return typen;
}
"""


@pytest.fixture(scope="session")
def heute_stand():
    return _heute_stand


def _heute_stand(**mehr):
    """Ein Stand ohne Einstufungsfrage. Die kommt sonst bei leerem Stand nach
    acht Sekunden als Karte ueber alles - siehe init() in index.html."""
    import datetime
    s = {"einstufung": {"tag": datetime.date.today().isoformat(), "wahl": "neu", "bis": ""}}
    s.update(mehr)
    return s


@pytest.fixture(scope="session")
def wurzelordner(tmp_path_factory):
    """Zwei Kopien der Demo nebeneinander: app/ wie ausgeliefert, gehaertet/
    mit import_richten.py angewandt. So prueft der Import-Test das Skript,
    bevor es web/index.html wirklich anfasst."""
    import demo_bauen
    import import_richten

    ordner = tmp_path_factory.mktemp("zmaj_e2e")
    app = os.path.join(str(ordner), "app")
    assert demo_bauen.main(["--ziel", app]) == 0
    gehaertet = os.path.join(str(ordner), "gehaertet")
    shutil.copytree(app, gehaertet)
    pfad = os.path.join(gehaertet, "index.html")
    html = io.open(pfad, encoding="utf-8", newline="").read()
    if "const nurTexte = x =>" not in html:          # sonst schon in web/ geschrieben
        html, fehler = import_richten.anwenden(html)
        assert not fehler, fehler
        io.open(pfad, "w", encoding="utf-8", newline="").write(html)
    return str(ordner)


@pytest.fixture(scope="session")
def basis(wurzelordner):
    """Dateiserver auf einem freien Port, wie in bilder_playwright.py."""
    class Leise(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Leise, directory=wurzelordner))
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()
    srv.server_close()


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    chromium = os.environ.get("ZMAJ_CHROMIUM") or None
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=chromium)
        yield b
        b.close()


class Seite:
    """Eine Seite samt allem, was dabei schiefging: Skriptfehler und
    Anfragen an fremde Server (AGENTS.md, Regel 6: kein Netz zur Laufzeit)."""

    def __init__(self, page, basis):
        self.page = page
        self.basis = basis
        self.fehler = []
        self.fremd = []
        page.on("pageerror", lambda e: self.fehler.append(str(e)))
        page.on("request", lambda r: None if r.url.startswith((basis, "data:", "blob:"))
                else self.fremd.append(r.url))

    def js(self, code, arg=None):
        return self.page.evaluate(code, arg)

    def starten(self, app="app", sprache="de", stand=None, leeren=True):
        """Stand und Sprache setzen, dann die App laden. Gesetzt wird auf
        einer leeren Seite desselben Ursprungs - nicht in der laufenden App,
        deren pagehide/visibilitychange sonst beim Neuladen den eigenen,
        leeren Stand darueberschreiben koennte."""
        if leeren or stand is not None:
            self.page.goto(self.basis + "/leer")      # 404, aber gleicher Ursprung
            self.js("""([stand, sprache, leeren]) => {
                if(leeren) localStorage.clear();
                if(stand) localStorage.setItem('zmaj_stand', JSON.stringify(stand));
                localStorage.setItem('zmaj_einwilligung',
                    JSON.stringify({wahl:'nein', stand:1, zeit:new Date().toISOString()}));
                localStorage.setItem('zmaj_sprache', sprache);
            }""", [stand, sprache, leeren])
        self.page.goto("%s/%s/index.html" % (self.basis, app))
        self.bereit()

    def bereit(self):
        self.page.wait_for_function(BEREIT, timeout=30000)

    def neu_laden(self):
        self.page.reload()
        self.bereit()

    def durchspielen(self, feld, art):
        return self.js(DURCHSPIELEN, [feld, art])


@pytest.fixture
def seite(browser, basis):
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                              service_workers="block")
    s = Seite(ctx.new_page(), basis)
    yield s
    ctx.close()


@pytest.fixture(scope="session")
def vollversion():
    with io.open(os.path.join(WURZEL, "testdaten", "zmaj-test-vollversion.json"), encoding="utf-8") as f:
        return json.load(f)
