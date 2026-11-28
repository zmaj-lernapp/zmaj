# -*- coding: utf-8 -*-
"""mailto: und andere fremde Schemata gehen im Test nicht an Windows.

Offen-Liste, Eingang 15.11.2026: Nach den E2E-Laeufen standen 32 Fenster
„App auswählen“ (OpenWith.exe) in Ajdins Taskleiste. Das installierte Chrome
gibt mailto: an das System weiter, und ohne Mailprogramm fragt Windows bei
jedem Klick nach. Die SCHEMA_SPERRE in conftest.py haelt das an. Geprueft wird
hier, dass sie in jedem Kontext steckt, dass die Adresse weiter in Seite.fremd
ankommt (test_feedback und test_widerruf lesen sie dort) und dass unter
Windows kein Fenster aufgeht.
"""
import subprocess
import sys

import pytest

from conftest import Seite

ZMAJ_MAIL = "zmaj.lernapp@gmail.com"

# Ein Knopf, der wie die App per location.href ein fremdes Schema oeffnet.
KNOPF = """schema => { const b = document.createElement('button'); b.id = 'probe';
  b.textContent = 'Probe'; b.onclick = () => { location.href = schema; };
  document.body.append(b); }"""


def _fenster():
    """Wie viele Fenster „App auswählen“ gerade offen sind. Nur unter Windows."""
    aus = subprocess.run(["tasklist", "/FI", "IMAGENAME eq OpenWith.exe", "/NH"],
                         capture_output=True, text=True, encoding="cp850", errors="replace").stdout or ""
    return aus.lower().count("openwith.exe")


def _warten_auf(seite, bedingung):
    for _ in range(80):
        if bedingung():
            return True
        seite.page.wait_for_timeout(25)
    return bedingung()


def test_feedback_per_mail_geht_nicht_an_windows(seite, heute_stand):
    """Der echte Weg aus der App: Feedback ohne Cloud oeffnet mailto:."""
    vorher = _fenster() if sys.platform == "win32" else 0
    seite.starten(stand=heute_stand())
    seite.js("() => { showSettings(); }")
    adresse = seite.page.url
    seite.page.fill("#fbText", "Hallo")
    seite.page.click("#fbSend")
    mails = lambda: [u for u in seite.fremd if u.startswith("mailto:" + ZMAJ_MAIL + "?")]  # noqa: E731
    assert _warten_auf(seite, lambda: len(mails()) == 1), seite.fremd
    gesperrt = seite.js("() => window.__zmajFremdeSchemata")
    assert gesperrt == mails(), gesperrt
    assert seite.page.url == adresse
    if sys.platform == "win32":
        seite.page.wait_for_timeout(2500)   # Windows braucht etwas, bis das Fenster steht
        assert _fenster() <= vorher, "es ging ein Fenster „App auswählen“ auf"
    assert seite.fehler == []


@pytest.mark.parametrize("schema", ["mailto:test@example.org?subject=Probe", "tel:+491701234567",
                                    "intent://zmaj#Intent;scheme=zmaj;end"])
def test_jeder_neue_kontext_hat_die_sperre(browser, basis, schema):
    """Auch ein Kontext, den ein Test selbst anlegt (rund 40 Stellen), und
    ohne Seite(): Die Adresse steht dann nur in window.__zmajFremdeSchemata."""
    ctx = browser.new_context(service_workers="block")
    try:
        page = ctx.new_page()
        page.goto(basis + "/leer")          # 404, aber eine Seite mit body
        page.evaluate(KNOPF, schema)
        page.click("#probe")
        page.wait_for_function("() => window.__zmajFremdeSchemata.length > 0", timeout=5000)
        assert page.evaluate("() => window.__zmajFremdeSchemata") == [schema]
        assert page.url == basis + "/leer"
    finally:
        ctx.close()


def test_eigene_seiten_und_links_bleiben_frei(browser, basis):
    """Die Sperre haelt nur fremde Schemata an: http(s), about: und data:
    laufen wie vorher, Seite() bekommt nichts gemeldet."""
    ctx = browser.new_context(service_workers="block")
    try:
        seite = Seite(ctx.new_page(), basis)
        seite.page.goto(basis + "/leer")
        seite.page.evaluate(KNOPF, basis + "/noch-eine")
        with seite.page.expect_navigation():
            seite.page.click("#probe")
        assert seite.page.url == basis + "/noch-eine"
        assert seite.js("() => window.__zmajFremdeSchemata") == []
        seite.page.goto("about:blank")
        assert seite.page.url == "about:blank"
        assert seite.fremd == []
    finally:
        ctx.close()
