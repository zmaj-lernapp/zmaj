# -*- coding: utf-8 -*-
"""start.py, der Starter am PC: liefert web/ und /api/daten aus, sonst nichts.

Seit dem 04.10.2026 ist der alte Kontoserver weg. Was die App am PC noch
fragt, muss weiter antworten; alles mit Konten darf nicht wiederkommen."""
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest


@pytest.fixture(scope="module")
def basis():
    import start
    srv = ThreadingHTTPServer(("127.0.0.1", 0), start.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()
    srv.server_close()


def test_alte_aufrufe_gehen_weiter():
    import inhalt
    import start
    assert start.lade_daten is inhalt.lade_daten
    assert start.pruefe_vokabeln is inhalt.pruefe_vokabeln
    assert start.fehlende_woerter is inhalt.fehlende_woerter


def test_startseite_und_inhalt(basis):
    with urllib.request.urlopen(basis + "/") as r:
        assert b"<html" in r.read(4000).lower()
    with urllib.request.urlopen(basis + "/api/daten?sprache=en") as r:
        daten = json.loads(r.read().decode("utf-8"))
    assert daten["sprache"] == "en"
    assert daten["kategorien"]


def test_keine_konten_mehr(basis):
    for pfad in ("/api/konto", "/api/fortschritt"):
        with pytest.raises(urllib.error.HTTPError) as fehler:
            urllib.request.urlopen(basis + pfad)
        assert fehler.value.code == 404, pfad
    anfrage = urllib.request.Request(basis + "/api/fortschritt", data=b"{}", method="POST")
    with pytest.raises(urllib.error.HTTPError) as fehler:
        urllib.request.urlopen(anfrage)
    assert fehler.value.code in (404, 501)
