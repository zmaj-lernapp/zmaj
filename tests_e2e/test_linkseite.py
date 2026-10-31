# -*- coding: utf-8 -*-
"""Die Linkseite links.html im echten Browser (31.10.2026).

Gebaut von seite_bauen.py in einen Probeordner, ausgeliefert vom
Dateiserver der Suite, im Handyformat (360 x 640). Google Play beantwortet
der Test selbst (page.route) - kein Byte verlaesst den Rechner.

Geprueft wird:
  - ?von=tiktok, ?von=instagram, ?von=youtube: Alle acht Knoepfe zeigen auf
    den Play-Link mit genau diesem Kanal (Form wie tests/test_linkseite.py),
    ohne ?von= und bei einem unbekannten Wert auf "web". Ein Tipp auf den
    Knopf fuehrt wirklich dorthin.
  - Ohne JavaScript: englischer Text, der Link fuer "web", keine
    Sprachknoepfe (ohne Skript taeten sie nichts).
  - Die Sprache des Browsers gilt, eine fehlende wird Englisch, Norwegisch
    ("no") wird bokmaal.
  - Nichts in localStorage, keine Cookies, keine Anfrage an fremde Server,
    keine Fehler in der Konsole (auch keine Verstoesse gegen die
    Content-Security-Policy).
  - Im Handyformat steht der Knopf ohne Scrollen da, und die Seite ist nicht
    breiter als der Bildschirm - hell wie dunkel eingestellt.
"""
import functools
import http.server
import json
import re
import threading

import pytest
from conftest import Dateiserver

playwright = pytest.importorskip("playwright.sync_api")

PLAY = re.compile(r"^https://play\.google\.com/")


@pytest.fixture(scope="module")
def links_basis(tmp_path_factory):
    """Die Seiten wie online: mit Formular (erfundener Zugang)."""
    import huelle
    import seite_bauen
    import sprachen

    ordner = tmp_path_factory.mktemp("linkseite")
    privat = ordner / "huelle"
    privat.mkdir()
    (privat / "cloud_zugang.json").write_text(
        json.dumps({"projekt": "zmaj-probe", "schluessel": "AIza" + "Probe" * 7}), encoding="utf-8")
    ziel = ordner / "seite"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(seite_bauen, "ZIEL", str(ziel))
        mp.setattr(huelle, "ordner", lambda *a, **k: str(privat))
        mp.setattr(sprachen, "KONTAKT_FORMULAR", True)
        mp.setattr(sprachen, "KONTAKT_STAND", "31.10.2026")
        seite_bauen.main()
    assert (ziel / "links.html").exists()

    class Leise(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    srv = Dateiserver(("127.0.0.1", 0), functools.partial(Leise, directory=str(ziel)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()
    srv.server_close()


class Linkseite:
    def __init__(self, browser, basis, locale="en-US", skript=True, farben="dark"):
        self.ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale=locale,
                                       java_script_enabled=skript, color_scheme=farben,
                                       service_workers="block")
        self.page = self.ctx.new_page()
        self.basis = basis
        self.fehler, self.konsole, self.fremd, self.play = [], [], [], []
        self.page.on("pageerror", lambda e: self.fehler.append(str(e)))
        self.page.on("console", lambda m: self.konsole.append(m.text) if m.type == "error" else None)
        self.page.on("request", lambda r: None if r.url.startswith(basis) or PLAY.match(r.url)
                     else self.fremd.append(r.url))
        self.page.route(PLAY, self._play)

    def _play(self, route, request):
        self.play.append(request.url)
        route.fulfill(status=200, content_type="text/html", body="<!doctype html><title>Play</title>")

    def oeffnen(self, von=None):
        self.page.goto(self.basis + "/links.html" + ("?von=" + von if von is not None else ""))

    def knoepfe(self):
        return self.page.eval_on_selector_all("a.play", "l => l.map(a => a.href)")

    def sichtbar(self):
        return self.page.eval_on_selector_all(
            "section[data-sprache]", "l => l.filter(s => !s.hidden).map(s => s.dataset.sprache)")

    def sauber(self):
        assert self.fehler == [], self.fehler
        assert self.konsole == [], self.konsole
        assert self.fremd == [], self.fremd

    def zu(self):
        self.ctx.close()


@pytest.fixture
def linkseite(browser, links_basis):
    seiten = []

    def oeffnen(**k):
        s = Linkseite(browser, links_basis, **k)
        seiten.append(s)
        return s
    yield oeffnen
    for s in seiten:
        s.zu()


@pytest.mark.parametrize("von,quelle", [("tiktok", "tiktok"), ("instagram", "instagram"),
                                        ("youtube", "youtube"), ("TikTok", "tiktok"),
                                        (None, "web"), ("", "web"), ("facebook", "web"),
                                        ("tiktok2", "web")])
def test_kanal_aus_von(linkseite, von, quelle):
    import seite_bauen
    s = linkseite()
    s.oeffnen(von)
    assert s.knoepfe() == [seite_bauen.play_link(quelle)] * 8
    assert s.sichtbar() == ["en"]
    s.sauber()


def test_tipp_fuehrt_zu_google_play(linkseite):
    import seite_bauen
    s = linkseite()
    s.oeffnen("tiktok")
    s.page.click('section[data-sprache="en"] a.play')
    s.page.wait_for_url(PLAY)
    assert s.play == [seite_bauen.play_link("tiktok")]
    assert s.page.url == seite_bauen.play_link("tiktok")


def test_ohne_javascript(linkseite):
    import seite_bauen
    s = linkseite(skript=False, locale="de-DE")
    s.oeffnen("instagram")
    assert s.knoepfe() == [seite_bauen.play_link("web")] * 8
    assert s.page.is_visible('section[data-sprache="en"] a.play')
    assert not s.page.is_visible('section[data-sprache="de"]')
    assert not s.page.is_visible(".sprachen")
    assert s.page.is_visible('[data-fuss="en"] a[href="impressum.html"]')
    s.page.click('section[data-sprache="en"] a.play')
    s.page.wait_for_url(PLAY)
    assert s.play == [seite_bauen.play_link("web")]


@pytest.mark.parametrize("locale,soll", [("de-DE", "de"), ("tr-TR", "tr"), ("hr-HR", "en"),
                                         ("no-NO", "nb"), ("fr-FR", "fr")])
def test_sprache_des_browsers(linkseite, locale, soll):
    s = linkseite(locale=locale)
    s.oeffnen("youtube")
    assert s.sichtbar() == [soll]
    assert s.page.evaluate("document.documentElement.lang") == soll
    assert s.page.is_visible('[data-fuss="%s"]' % soll)
    assert s.page.is_visible(".sprachen")
    s.page.click('.sprachen button[data-sprache="sv"]')
    assert s.sichtbar() == ["sv"]
    s.sauber()


@pytest.mark.parametrize("farben", ["light", "dark"])
def test_handyformat_ohne_speicher(linkseite, farben):
    s = linkseite(farben=farben)
    s.oeffnen("tiktok")
    knopf = s.page.locator('section[data-sprache="en"] a.play').bounding_box()
    assert knopf["y"] >= 0 and knopf["y"] + knopf["height"] <= 640, knopf
    assert knopf["width"] >= 300, knopf
    assert s.page.evaluate("document.documentElement.scrollWidth") <= 360
    # Dunkel wie alle Seiten, auch wenn das Handy hell eingestellt ist.
    hinten = s.page.evaluate("getComputedStyle(document.body).backgroundColor")
    assert hinten == "rgb(11, 21, 51)", hinten
    assert s.page.evaluate("localStorage.length") == 0
    assert s.page.evaluate("document.cookie") == ""
    assert s.ctx.cookies() == []
    s.sauber()
