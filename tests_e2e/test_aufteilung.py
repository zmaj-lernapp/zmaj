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


# Die Huelle liefert die aufbewahrte Meldung aboGeaendert (retainUntilConsumed),
# sobald der Horcher haengt. Geteilt kann das zwischen zwei Dateien sein, noch
# vor init(). Die Attrappe ruft den Horcher darum gleich beim Anhaengen auf -
# frueher geht es nicht. Jedes Schreiben von zmaj_voll wird mit skripteDa und
# standGeladen mitgeschrieben. stand() antwortet "unbekannt", damit
# vollAbgleichen() am Ende von init() nichts glattzieht, was die fruehe
# Meldung falsch gemacht haette. zmaj_voll steht vorher auf VORHER (oder fehlt).
FRUEHES_ABO = """(() => {
  const AKTIV = %s, VORHER = %s;
  window.__voll = [];
  const setzen = Storage.prototype.setItem;
  if(VORHER !== null && location.pathname.endsWith('/index.html')) setzen.call(localStorage, 'zmaj_voll', VORHER);
  Storage.prototype.setItem = function(k, v){
    if(k === 'zmaj_voll'){
      let da = 'unbekannt', geladen = 'unbekannt';
      try{ da = skripteDa; geladen = standGeladen; }catch(e){}
      window.__voll.push([v, da, geladen]);
    }
    return setzen.call(this, k, v);
  };
  window.__abgefragt = 0;
  window.Capacitor = {Plugins: {ZmajAbo: {
    stand: async () => { window.__abgefragt++; return {bekannt: false}; },
    preise: async () => ({ok: true, plaene: []}),
    addListener: (name, f) => {
      if(name === 'aboGeaendert') f({aktiv: AKTIV, gesperrt: false, plan: AKTIV ? 'jahr' : null});
      return {remove(){}};
    },
  }}};
})();"""


def fruehes_abo(aktiv=True, vorher=None):
    return FRUEHES_ABO % (json.dumps(aktiv), json.dumps(vorher))


# aktiv, zmaj_voll vorher, erwartete Schreibvorgaenge [Wert, skripteDa, standGeladen], premium danach.
# Der zweite Fall ist der aus der Nachpruefung: zmaj_voll steht noch auf '1',
# Google meldet "nicht aktiv". Lief die Meldung vor vollversionLaden(), war
# premium noch falsch, es wurde nichts geschrieben, und vollversionLaden()
# machte danach aus der '1' wieder die Vollversion.
FRUEHE_FAELLE = [
    (True, None, [["0", True, False], ["1", True, True]], True),
    (False, "1", [["0", True, True]], False),
    (True, "0", [["1", True, True]], True),
]


@pytest.mark.parametrize("aktiv,vorher,geschrieben,premium", FRUEHE_FAELLE,
                         ids=["neu_aktiv", "abgelaufen", "gekauft"])
def test_fruehe_abo_meldung_erst_nach_vollversion_laden(motor, basis, heute_stand,
                                                         aktiv, vorher, geschrieben, premium):
    """Kommt aboGeaendert vor skripteDa, wird es gemerkt und erst in
    nachAnmeldung() gleich nach loadProgress() verarbeitet, also nachdem
    vollversionLaden() und dauerVollLaden() premium gesetzt haben. Vorher
    schrieb vollversionMerken() zmaj_voll, noch bevor vollversionLaden()
    lief (Nachpruefung 4b); der Microtask nach init() aus d64d846 lief
    ebenfalls davor, weil init() zuerst auf sandboxPruefen() wartet
    (Nachpruefung von 4b, 20.11.2026)."""
    ctx = motor.new_context(viewport={"width": 360, "height": 640}, locale="de-DE", service_workers="block")
    try:
        ctx.add_init_script(fruehes_abo(aktiv, vorher))
        s = Seite(ctx.new_page(), basis)
        s.starten(stand=heute_stand())
        s.page.wait_for_function("() => window.__abgefragt > 0", timeout=15000)
        assert s.js("() => window.__voll") == geschrieben
        assert s.js("() => [aboFrueh, premium, localStorage.getItem('zmaj_voll')]") == [None, premium, geschrieben[-1][0]]
        assert s.fehler == [] and s.fremd == []
    finally:
        ctx.close()


def test_fruehe_abo_meldung_nicht_wenn_die_app_nicht_startet(seite, basis, heute_stand, wurzelordner):
    """Fehlt ein Teil (teileFehlen), startet die App nicht und speichert
    nichts - auch nicht die Vollversion aus einer fruehen Abo-Meldung."""
    app = os.path.join(wurzelordner, "app")
    datei = [d for d in app_quelle.dateien(app)
             if "const TEILE_ERWARTET = 34;" in io.open(os.path.join(app, d), encoding="utf-8").read()]
    assert len(datei) == 1, datei
    text = io.open(os.path.join(app, datei[0]), encoding="utf-8", newline="").read()
    text = text.replace("const TEILE_ERWARTET = 34;", "const TEILE_ERWARTET = 35;")
    art = "text/html" if datei[0].endswith(".html") else "text/javascript"
    seite.page.route("**/app/" + datei[0], lambda r: r.fulfill(
        status=200, content_type=art + "; charset=utf-8", body=text))
    seite.page.add_init_script(fruehes_abo())
    seite.page.goto(basis + "/leer")
    seite.js("""s => { localStorage.clear(); localStorage.setItem('zmaj_stand', s);
        localStorage.setItem('zmaj_sprache', 'de'); }""", json.dumps(heute_stand()))
    seite.page.goto(basis + "/app/index.html")
    seite.page.wait_for_function("() => document.getElementById('err').style.display === 'block'", timeout=15000)
    seite.page.wait_for_timeout(500)
    assert seite.js("() => [window.__voll, localStorage.getItem('zmaj_voll'), skripteDa]") == [[], None, False]
    assert any("Zmaj startet nicht: App-Teile: 34 von 35" in f for f in seite.fehler), seite.fehler


@pytest.mark.parametrize("datei", ["schriften.css", "lottie.min.js"])
def test_abgelehnte_datei_steht_in_fehler(seite, basis, datei):
    """G5 ganz: Ein Stilblatt oder Skript vom eigenen Server, das gar keine
    Antwort bekommt (abgelehnt wie beim Fehler mit der Warteschlange, G6),
    meldet kein "response" mit Status - nur "requestfailed". Auch das muss
    in fehler stehen. Geteilt gilt dasselbe fuer jede Datei unter js/ und css/."""
    seite.page.route("**/app/" + datei, lambda r: r.abort("connectionrefused"))
    seite.page.goto(basis + "/app/index.html")
    seite.page.wait_for_timeout(300)
    gescheitert = [f for f in seite.fehler if f.startswith("Anfrage gescheitert") and f.endswith("/app/" + datei)]
    assert len(gescheitert) == 1, seite.fehler
    assert "ERR_CONNECTION_REFUSED" in gescheitert[0] or "refused" in gescheitert[0].lower(), gescheitert
