# -*- coding: utf-8 -*-
"""sicherheit2_richten.py passt auf den heutigen Stand von web/index.html."""
import io
import os


def test_passt_und_ist_nicht_doppelt_anwendbar(wurzel):
    import sicherheit2_richten as s
    text = io.open(os.path.join(wurzel, "web", "index.html"), encoding="utf-8", newline="").read()
    if "hasOwnProperty.call(FESTE, p)" not in text:
        text, fehler = s.anwenden(text)
        assert not fehler, fehler
    assert text.count("if(neuesPw && KONTEN_AN)") == 1
    assert text.count("if(bestaetigen && KONTEN_AN)") == 1
    _, fehler = s.anwenden(text)
    assert fehler
