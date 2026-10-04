# -*- coding: utf-8 -*-
"""Die Patch-Skripte laufen auch auf einer Windows-Kopie mit CRLF.

Git fuer Windows checkt standardmaessig mit CRLF aus; die Anker der Skripte
enthalten \\n. Ohne Normalisieren brachen sie dort mit "0-mal gefunden" ab."""
import io
import os

import pytest

SKRIPTE = ["import_richten", "sicherheit2_richten", "barrierefreiheit_richten"]


@pytest.mark.parametrize("name", SKRIPTE)
def test_crlf_kopie_wird_gerichtet_und_bleibt_crlf(tmp_path, wurzel, name):
    import importlib
    skript = importlib.import_module(name)
    text = io.open(os.path.join(wurzel, "web", "index.html"), encoding="utf-8", newline="").read()
    kopie = tmp_path / "index.html"
    kopie.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    assert skript.main(["--datei", str(kopie), "--schreiben"]) == 0
    roh = kopie.read_bytes()
    assert roh.count(b"\n") == roh.count(b"\r\n"), "Zeilenenden gemischt"
    erwartet, fehler = skript.anwenden(text)
    assert not fehler
    assert roh.decode("utf-8").replace("\r\n", "\n") == erwartet
