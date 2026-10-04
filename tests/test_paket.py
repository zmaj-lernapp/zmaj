# -*- coding: utf-8 -*-
"""Das PyPI-Paket zmaj-bosnian liefert genau den Datensatz aus data/."""
import io
import json
import os
import sys


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
