# -*- coding: utf-8 -*-
"""Browser-Tests: die echte App in Chromium, so wie ein Lernender sie sieht.

Getrennt von tests/, weil sie Playwright und einen Browser brauchen und
eine halbe Minute laufen statt zwei Sekunden. `python3 -m pytest` laeuft
weiter nur tests/ (testpaths in pyproject.toml); diese hier mit

    python3 -m pip install -r requirements-e2e.txt
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
import warnings

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
# Doppeltipp-Sperre (20.11.2026, Optimierung Punkt 1): eine neu gezeichnete
# Aufgabe nimmt FRISCH_MS (300 ms) lang keinen echten Tipp oder Mausklick an
# (aufgaben.js, vor renderTask). Klicks per Skript wie in DURCHSPIELEN gelten
# sofort. Wer mit Playwright klickt (locator.click, mouse, touchscreen), wartet
# vorher mit frisch_abwarten() - nur so lange wie noetig.
FRISCH_ABWARTEN = r"""() => new Promise(r => setTimeout(r,
  typeof frisch !== 'undefined' && frisch ? Math.max(0, frisch.bis - performance.now()) + 30 : 0))"""


def frisch_abwarten(page):
    """Bis die zuletzt gezeichnete Aufgabe echte Tipps annimmt."""
    page.evaluate(FRISCH_ABWARTEN)


DURCHSPIELEN = r"""
async ([feld, art]) => {
  // Sx: der Sprung-Test in einen Reiter (13.11.2026), Liste qs wie beim Test
  const X = () => art === 'Lx' ? Lx : (art === 'Sx' ? Sx : Tx);
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
    // Zahlen, die wechseln (25.10.2026): Luecke und Kacheln zeigen die
    // Fassung mit der gezogenen Zahl q.v - geantwortet wird auf sie.
    const s = q.s && typeof zahlFassung === 'function' ? zahlFassung(q.s, q.v) : q.s;
    if(q.typ === 'intro'){ body.querySelector('#xNext').click(); }
    else if(q.typ === 'speak'){ body.querySelector('#xSkip').click(); }
    else if(q.typ === 'gap' || q.typ === 'type'){
      body.querySelector('#xIn').value = (q.typ === 'gap' ? s.answer : q.w.bs).split(' / ')[0];
      body.querySelector('#xCheck').click();
    } else if(q.typ === 'kacheln'){
      // Satzbau (13.10.2026): die Kacheln in der Reihenfolge von bs antippen.
      // Ohne diesen Zweig landete die Aufgabe unten bei q.w.bs - die hat kein w.
      const rand = /^[.,!?¿¡:;"„“”«»…()]+|[.,!?¿¡:;"„“”«»…()]+$/g;
      for(const soll of s.bs.split(/\s+/).map(x => x.replace(rand, '').toLowerCase()).filter(Boolean)){
        const b = [...body.querySelectorAll('#xBank .kachel:not(.platz)')].find(o => o.textContent.toLowerCase() === soll);
        if(!b) throw new Error('keine Kachel "' + soll + '" bei ' + s.bs);
        b.click();
      }
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

# Fremde Schemata (mailto:, tel:, intent: ...) gibt das installierte Chrome
# unter Windows an das System weiter. Ohne Mailprogramm oeffnet Windows dann
# bei jedem Klick ein Fenster "App auswaehlen" (OpenWith.exe). Nach den Laeufen
# vom 14./15.11.2026 standen 32 solche Fenster in Ajdins Taskleiste, ausgeloest
# von Feedback, Widerruf und Empfehlen (index.html, location.href = 'mailto:').
# Dieses Skript laeuft in jedem Dokument vor der App und haelt solche
# Navigationen ueber die Navigation API an, bevor Chrome sie weitergibt. Die
# Adresse steht danach in window.__zmajFremdeSchemata und, bei einer Seite()
# (unten), in Seite.fremd - dort, wo Chromium sie vorher als Anfrage meldete.
# Erprobt am 16.11.2026: page.route("mailto:*") haelt nichts an, das Fenster
# kam trotzdem; mit diesem Skript kam keins (tests_e2e/test_schema_sperre.py).
SCHEMA_SPERRE = r"""(() => {
  const intern = /^(https?|about|blob|data|javascript|file):/i;
  window.__zmajFremdeSchemata = [];
  if (!window.navigation) return;
  navigation.addEventListener('navigate', e => {
    const url = e.destination && e.destination.url;
    if (!url || intern.test(url)) return;
    window.__zmajFremdeSchemata.push(url);
    if (typeof window.__zmajSchemaMelden === 'function') window.__zmajSchemaMelden(url);
    if (e.cancelable) e.preventDefault();
  });
})();"""


class MitSchemaSperre:
    """Ein Browser, dessen neue Kontexte die SCHEMA_SPERRE mitbringen, sonst
    genau wie der Browser selbst (alles andere wird durchgereicht). So gilt die
    Sperre auch fuer die rund 40 Tests, die ihren Kontext selbst anlegen."""

    def __init__(self, browser):
        self._browser = browser

    def __getattr__(self, name):
        return getattr(self._browser, name)

    def new_context(self, *args, **kwargs):
        ctx = self._browser.new_context(*args, **kwargs)
        ctx.add_init_script(SCHEMA_SPERRE)
        return ctx

    def new_page(self, *args, **kwargs):
        page = self._browser.new_page(*args, **kwargs)
        page.context.add_init_script(SCHEMA_SPERRE)
        return page


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
    # Gesucht wird in der ganzen App (app_quelle): seit 1.5 kann der Code in
    # gehaertet/js stehen, und sonst fiele die ganze Suite an dieser Stelle aus.
    import app_quelle
    if "const nurTexte = x =>" not in app_quelle.lesen(gehaertet):   # sonst schon in web/ geschrieben
        html, fehler = import_richten.anwenden(html)
        assert not fehler, fehler
        io.open(pfad, "w", encoding="utf-8", newline="").write(html)
    return str(ordner)


class Dateiserver(socketserver.ThreadingTCPServer):
    """Der Server der Browser-Tests, mit Warteschlange 128 (22.10.2026).

    ThreadingTCPServer ruft listen() mit request_queue_size = 5 auf. Die App
    holt beim Start die 32 Drachenteile auf einmal, und was ueber die fuenf
    hinaus ankommt, bevor der Server es annimmt, lehnt Windows ab. Folge:
    mal dieser, mal jener Test rot mit net::ERR_CONNECTION_REFUSED auf
    maskottchen/teile/*.webp, obwohl an der App nichts falsch war.
    Gemessen und abgesichert in test_dateiserver.py."""
    request_queue_size = 128
    daemon_threads = True


@pytest.fixture(scope="session")
def basis(wurzelordner):
    """Dateiserver auf einem freien Port, wie in bilder_playwright.py."""
    class Leise(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    srv = Dateiserver(("127.0.0.1", 0), functools.partial(Leise, directory=wurzelordner))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()
    srv.server_close()


@pytest.fixture(scope="session")
def playwright_sitzung():
    """Eine Playwright-Sitzung fuer alle Tests - zwei im selben Prozess
    vertraegt die Sync-API nicht. Chromium und WebKit kommen beide aus ihr."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def pw(playwright_sitzung):
    """Dieselbe Sitzung unter dem Namen, den test_ios_ton.py (15.11.2026)
    benutzt: Es holt sich WebKit mit pw.webkit. Seit dem 1.4-Merge
    (16.11.2026) gibt es nur noch ein sync_playwright(), playwright_sitzung."""
    return playwright_sitzung


@pytest.fixture(scope="session")
def browser(playwright_sitzung):
    chromium = os.environ.get("ZMAJ_CHROMIUM") or None
    # Stumm (20.11.2026): Ajdin hoerte waehrend der Browsertests bosnische
    # Woerter aus den Laptop-Lautsprechern. Playwright setzt --mute-audio nur
    # ohne Fenster (headless) selbst; hier ausdruecklich, damit es auch mit
    # Fenster still bleibt (headless=False, PWDEBUG). Nur die Ausgabe ist
    # stumm: spieler und WebAudio laufen weiter, ihre Zeiten stimmen.
    # WebKit hat keinen solchen Schalter, siehe webkit.
    b = playwright_sitzung.chromium.launch(executable_path=chromium, args=["--mute-audio"])
    yield MitSchemaSperre(b)
    b.close()


@pytest.fixture(scope="session")
def webkit_stumm(playwright_sitzung):
    """Schaltet WebKit im Lautstaerkemixer von Windows stumm, solange die
    Tests laufen (stumm_windows.py, 21.11.2026): jede Audio-Sitzung eines
    Prozesses aus dem Ordner von WebKit, alle 100 ms aufs Neue, sonst
    nichts. Ausserhalb von Windows tut er nichts. Mit
    ZMAJ_STUMM_PROTOKOLL=datei.json steht am Ende darin, welche Sitzungen er
    sah, ob Windows sie schon stumm hatte und ihr hoechster Spitzenpegel.

    Ohne Ordner von WebKit (Playwright meldet keinen Pfad, oder er fehlt auf
    der Platte) tut er nichts, und alles mit WebKit wird uebersprungen
    (Pruefung 21.11.2026): aus einem leeren Pfad machte os.path.abspath den
    Arbeitsordner, und der Helfer haette dessen Prozesse stumm geschaltet."""
    import stumm_windows

    try:
        programm = playwright_sitzung.webkit.executable_path or ""
    except Exception:           # Playwright weiss nichts von WebKit
        programm = ""
    ordner = os.path.dirname(programm)
    if not ordner or not os.path.isabs(ordner) or not os.path.isdir(ordner):
        pytest.skip("WebKit fehlt (Ordner: %r)" % ordner)
    st = stumm_windows.Stummschalter(ordner)
    st.start()
    yield st
    st.stop()
    if os.environ.get("ZMAJ_STUMM_PROTOKOLL"):
        st.protokoll_schreiben(os.environ["ZMAJ_STUMM_PROTOKOLL"])


@pytest.fixture(scope="session")
def webkit(playwright_sitzung, webkit_stumm):
    """WebKit, die Engine des iPhones (15.11.2026, Offen-Liste 5b). Nur wenn
    Playwright es auf dem Rechner schon hat - hier wird nichts geladen (kein
    playwright install). Fehlt es, wird der Test uebersprungen; die Chromium-
    Faelle laufen trotzdem."""
    # Ton (gemessen 21.11.2026 an den Audio-Sitzungen von Windows, Probeton
    # bei -66 dBFS): WebKit von Playwright spielt unter Windows MP3 und WAV
    # hoerbar ab, einen AudioContext hat es nicht. Ein Gegenstueck zu
    # --mute-audio gibt es nicht - keine Startoption, keine
    # Umgebungsvariable, kein Befehl im Protokoll (Playwright 1.63,
    # webkit-2359). Darum schaltet webkit_stumm es im Lautstaerkemixer von
    # Windows stumm (Ajdin: "3. ja"). Vorher spielt der vorlauf eine halbe
    # Sekunde Stille: Deren Sitzung wird stumm, und weil Windows sich das je
    # Programmpfad und Ausgabegeraet merkt, beginnt danach jede neue Sitzung
    # von WebKitWebProcess.exe schon stumm, vor ihrem ersten Ton (gemessen
    # 21.11.2026). Das bleibt so, auch nach dem Lauf - zurueck nur im
    # Lautstaerkemixer. Wechselt das Ausgabegeraet mitten im Lauf
    # (Kopfhoerer), faengt der Takt von 100 ms die neue Sitzung.
    import stumm_windows

    try:
        b = playwright_sitzung.webkit.launch()
    except Exception as e:      # jeder Startfehler heisst hier: kein WebKit da
        pytest.skip("WebKit fehlt: %s" % str(e).strip().splitlines()[0])
    try:
        gespielt, stumm = stumm_windows.vorlauf(b, webkit_stumm)
    except Exception as e:      # der Takt von 100 ms schaltet trotzdem stumm
        gespielt, stumm = "Fehler: %s" % str(e).strip().splitlines()[0], False
    if not stumm:               # z. B. kein Ausgabegeraet - dann ist auch nichts zu hoeren
        warnings.warn("WebKit im Lautstaerkemixer nicht stumm (Stille: %s, Fehler: %s)"
                      % (gespielt, webkit_stumm.fehler[:1]))
    yield MitSchemaSperre(b)
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
        # Ein Skript oder Stilblatt der App, das nicht kommt (404), wirft selbst
        # keinen pageerror: ein fehlendes Stilblatt bliebe ganz still, ein
        # fehlendes Skript zeigte nur Folgefehler. Seit die App in web/js und
        # web/css geteilt sein kann (1.5), steht so etwas darum hier in
        # fehler. Nur Skripte und Stilblaetter vom eigenen Server: /leer (siehe
        # starten) und /api/... antworten absichtlich mit 404.
        page.on("response", lambda r: self.fehler.append("HTTP %d %s" % (r.status, r.url))
                if r.status >= 400 and r.url.startswith(basis)
                and r.request.resource_type in ("script", "stylesheet") else None)
        # Und eines, das gar keine Antwort bekommt: abgelehnt
        # (net::ERR_CONNECTION_REFUSED, G6) oder abgebrochen. Das kommt nicht
        # bei "response" an, sondern nur hier. Auch net::ERR_ABORTED zaehlt:
        # page.goto wartet auf "load", also auf alle Skripte und Stilblaetter,
        # bevor ein Test weiter navigiert. Gemessen am 20.11.2026 an der
        # geteilten App (351 Tests mit den meisten Seitenwechseln, Chromium
        # und WebKit, dann die ganze Suite): kein abgebrochenes Skript oder
        # Stilblatt. Schliesst ein Test die Seite mitten im Laden, landet die
        # Meldung nach seinen Pruefungen und stoert nicht.
        page.on("requestfailed", lambda r: self.fehler.append("Anfrage gescheitert (%s) %s" % (r.failure, r.url))
                if r.url.startswith(basis) and r.resource_type in ("script", "stylesheet") else None)
        # mailto: und andere fremde Schemata haelt die SCHEMA_SPERRE an; als
        # Anfrage kommen sie dann nicht mehr an, deshalb meldet sie sie hier.
        page.expose_binding("__zmajSchemaMelden", lambda quelle, url: self.fremd.append(url))

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

    def frisch_abwarten(self):
        frisch_abwarten(self.page)


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


@pytest.fixture(scope="session")
def cloud_html(wurzelordner, tmp_path_factory):
    """Die Demo mit eingeschalteter Anmeldung und erfundenen Zugangsdaten.

    Eingesetzt mit app_bauen.cloud_einsetzen() wie beim Bauen - das schaltet
    seit 28.10.2026 (v109) auch CLOUD_AN ein. Gebraucht von test_cloud.py
    und test_anmeldung.py, Firebase beantwortet dort firebase_attrappe.py."""
    import app_bauen
    from firebase_attrappe import CLIENT, PROJEKT, SCHLUESSEL

    ordner = tmp_path_factory.mktemp("cloudprobe")
    kopie = ordner / "index.html"
    shutil.copyfile(os.path.join(wurzelordner, "app", "index.html"), str(kopie))
    assert kopie.read_bytes().decode("utf-8").count("const CLOUD_AN = false;") == 1
    zugang = ordner / "cloud_zugang.json"
    zugang.write_text(json.dumps({"projekt": PROJEKT, "schluessel": SCHLUESSEL, "client": CLIENT}),
                      encoding="utf-8")
    assert app_bauen.cloud_einsetzen(str(kopie), str(zugang)) is True
    html = kopie.read_bytes()
    assert b"const CLOUD_AN = true;" in html and b"__CLOUD_" not in html
    return html
