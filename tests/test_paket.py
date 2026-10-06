# -*- coding: utf-8 -*-
"""Das PyPI-Paket zmaj-bosnian liefert genau den Datensatz aus data/."""
import io
import json
import os
import subprocess
import sys

import pytest


def _paket_cli(wurzel, *argumente):
    import paket_bauen
    paket_bauen.main(["--nur-kopieren"])
    umgebung = dict(os.environ, PYTHONPATH=os.path.join(wurzel, "paket", "src"),
                    PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, "-m", "zmaj_bosnian", *argumente],
                          cwd=wurzel, env=umgebung, capture_output=True,
                          text=True, encoding="utf-8", timeout=10)


def test_paket_cli_zufaelliges_wort(wurzel):
    ergebnis = _paket_cli(wurzel, "word")
    daten = json.load(io.open(os.path.join(wurzel, "data", "vocabulary.json"), encoding="utf-8"))
    zeilen = {f"{wort['bs']} → {wort['translations']['en']}" for wort in daten["entries"]}
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert ergebnis.stdout.strip() in zeilen


@pytest.mark.parametrize("suche,sprache", [("KUĆA", "en"), ("house", "en"), ("Haus", "de")])
def test_paket_cli_sucht_wort_und_bedeutung(wurzel, suche, sprache):
    ergebnis = _paket_cli(wurzel, "search", suche, "--lang", sprache)
    daten = json.load(io.open(os.path.join(wurzel, "data", "vocabulary.json"), encoding="utf-8"))
    erwartet = [f"{wort['bs']} → {wort['translations'][sprache]}" for wort in daten["entries"]
                if suche.casefold() in wort["bs"].casefold()
                or suche.casefold() in wort["translations"][sprache].casefold()]
    assert erwartet
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert ergebnis.stdout.splitlines() == erwartet


def test_paket_cli_statistik(wurzel):
    ergebnis = _paket_cli(wurzel, "stats")
    daten = json.load(io.open(os.path.join(wurzel, "data", "manifest.json"), encoding="utf-8"))
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert ergebnis.stdout.splitlines() == [f"{name}: {zahl}" for name, zahl
                                           in sorted(daten["counts"].items())]


def test_paket_cli_ohne_treffer(wurzel):
    ergebnis = _paket_cli(wurzel, "search", "kein-treffer-9fd42d")
    assert ergebnis.returncode == 0, ergebnis.stderr
    assert ergebnis.stdout.strip() == "No matching words."


@pytest.mark.parametrize("argumente", [("word", "--lang", "xx"), ("search",), ("search", "  ")])
def test_paket_cli_ungueltige_argumente(wurzel, argumente):
    ergebnis = _paket_cli(wurzel, *argumente)
    assert ergebnis.returncode == 2
    assert "error:" in ergebnis.stderr
    assert "Traceback" not in ergebnis.stderr


def test_paket_liefert_den_datensatz(wurzel):
    import paket_bauen
    paket_bauen.main(["--nur-kopieren"])
    sys.path.insert(0, os.path.join(wurzel, "paket", "src"))
    try:
        import zmaj_bosnian as z
        n = json.load(io.open(os.path.join(wurzel, "data", "manifest.json"), encoding="utf-8"))["counts"]
        assert len(z.vocabulary()) == n["words"]
        assert len(z.sentences()) == n["sentences"]
        assert len(z.stories()) == n["stories"]
        assert len(z.glossary()) == n["glossary_entries"]
        assert len(z.levels()) == n["levels"] and len(z.sections()) == n["sections"]
        for code in z.LANGUAGES:
            assert len(z.grammar(code)) == n["grammar_lessons"], code
        assert z.vocabulary()[0]["bs"] == "Merhaba"
    finally:
        sys.path.remove(os.path.join(wurzel, "paket", "src"))


def test_version_gleich_wie_im_repo(wurzel):
    """Paket, pyproject und CITATION nennen dieselbe Version."""
    import re
    paket = io.open(os.path.join(wurzel, "paket", "pyproject.toml"), encoding="utf-8").read()
    haupt = io.open(os.path.join(wurzel, "pyproject.toml"), encoding="utf-8").read()
    v = re.search(r'^version = "([^"]+)"', paket, re.M).group(1)
    assert re.search(r'^version = "%s"' % re.escape(v), haupt, re.M)
