# -*- coding: utf-8 -*-
"""Weitermachen-Knopf: das erste nicht bestandene Level ab dem Einstieg.

Ajdins Regel vom 01.11.2026 (Wortlaut bei firstOpen in web/index.html):
Nachueben in bestandenen Leveln aendert nichts, ein per Update
eingeschobenes Level ist dran, bis es bestanden ist. Hier, was sich ohne
Browser pruefen laesst: firstOpen() sucht das erste nicht bestandene Level,
Knopf und Lernpfad fragen firstOpen(), und die verworfene Regel mit dem
Feld letzte_lektion ist ganz weg. Das Verhalten prueft
tests_e2e/test_weitermachen.py im echten Browser."""
import re


def _html(index_html):
    return index_html.replace("\r\n", "\n")


def test_dran_ist_das_erste_nicht_bestandene(index_html):
    html = _html(index_html)
    rumpf = html.split("const firstOpen = () => {\n")[1].split("\n};\n")[0]
    # Der Einstieg gilt nur, solange davor nichts oder ab ihm schon etwas bestanden ist
    assert "const ein = einstufungIndex(), h = hoechsterBestanden();" in rumpf
    assert "const ab = (ein > 0 && (h < 0 || h >= ein)) ? ein : 0;" in rumpf
    # Vom Startpunkt aus das erste nicht bestandene - nicht h + 1, sonst
    # uebersprang der Knopf eingeschobene Level
    assert "CATEGORIES.findIndex((c, k) => k >= ab && !passed.has(c.id))" in rumpf
    assert "h + 1" not in rumpf


def test_knopf_und_lernpfad_fragen_firstopen(index_html):
    html = _html(index_html)
    hero = html.split("function renderHero(){")[1].split("\n}\n")[0]
    assert "const i = firstOpen(), c = CATEGORIES[i];" in hero
    pfad = html.split("function showPath(){")[1].split("\n}\n")[0]
    assert "const next = firstOpen();" in pfad


def test_letzte_lektion_ganz_weg(index_html):
    html = _html(index_html)
    for wort in ("letzteLektion", "weiterZiel"):
        assert wort not in html, wort
    assert html.count("letzte_lektion") == 1          # nur im Kommentar bei firstOpen
    felder = re.search(r"const STAND_FELDER = new Set\(\[(.*?)\]\);", html, re.S).group(1)
    assert "letzte" not in felder
