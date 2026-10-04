# -*- coding: utf-8 -*-
"""Die Bewerbungstexte halten die Zeichengrenzen des Formulars ein.

Das Formular schneidet bei 500 Zeichen ab, ohne es vorher zu sagen. Die
Grenze hier ist 470, damit nach dem Einsetzen echter Zahlen für [N] noch
Platz bleibt.
"""
import io
import os
import re

GRENZE = 470


def felder(wurzel):
    text = io.open(os.path.join(wurzel, "docs", "codex-for-oss", "BEWERBUNG.md"), encoding="utf-8").read()
    return dict(re.findall(r"<!-- feld: (\w+) -->\n(.*?)\n<!-- ende -->", text, re.S))


def test_alle_felder_da(wurzel):
    assert {"rolle", "qualifikation", "api", "sonstiges"} <= set(felder(wurzel))


def test_zeichengrenze(wurzel):
    zu_lang = {k: len(v) for k, v in felder(wurzel).items() if len(v) > GRENZE}
    assert not zu_lang, zu_lang


def test_zahlen_im_text_stimmen_mit_dem_inhalt(wurzel, grunddaten):
    """1,728 Wörter, 300 Sätze ... stehen in der Bewerbung. Ändert sich der
    Inhalt, muss die Bewerbung mitgehen."""
    woerter = sum(len(k["words"]) for k in grunddaten["kategorien"])
    soll = {
        "1,728 words": woerter == 1728,
        "300 sentences": len(grunddaten["saetze"]) == 300,
        "12 stories": len(grunddaten["geschichten"]) == 12,
        "16 grammar lessons": len(grunddaten["grammatik"]) == 16,
    }
    text = felder(wurzel)["qualifikation"]
    for satz, stimmt in soll.items():
        assert satz in text and stimmt, satz
