# -*- coding: utf-8 -*-
"""Weitermachen-Knopf: immer das Level ganz vorn.

Ajdin am 01.11.2026: "ich bin level 10 das heisst level 1 bis 9 hab ich
fertig und wenn ich zb auf level 8 kurz eine lektion mache soll der knopf
trotzdem bei level 10 bleiben". Hier, was sich ohne Browser pruefen laesst:
firstOpen() rechnet vom hoechsten bestandenen Level aus, der Knopf fragt
firstOpen(), und das zurueckgenommene Feld letzte_lektion ist ganz weg. Das
Verhalten prueft tests_e2e/test_weitermachen.py im echten Browser."""
import re


def _html(index_html):
    return index_html.replace("\r\n", "\n")


def test_dran_ist_das_level_ganz_vorn(index_html):
    html = _html(index_html)
    rumpf = html.split("const firstOpen = () => {\n")[1].split("\n};\n")[0]
    assert "const vorn = Math.max(hoechsterBestanden() + 1, einstufungIndex());" in rumpf
    # Ganz am Ende die erste Luecke, sonst das letzte Level
    assert "CATEGORIES.findIndex(c => !passed.has(c.id))" in rumpf
    assert "CATEGORIES.length-1" in rumpf
    # Dasselbe Level, das isUnlocked() als letztes freigibt - der Knopf zeigt nie auf ein gesperrtes
    assert "i <= Math.max(hoechsterBestanden() + 1, einstufungIndex())" in html


def test_knopf_und_lernpfad_fragen_firstopen(index_html):
    html = _html(index_html)
    hero = html.split("function renderHero(){")[1].split("\n}\n")[0]
    assert "const i = firstOpen(), c = CATEGORIES[i];" in hero
    pfad = html.split("function showPath(){")[1].split("\n}\n")[0]
    assert "const next = firstOpen();" in pfad


def test_letzte_lektion_ganz_weg(index_html):
    html = _html(index_html)
    for wort in ("letzteLektion", "letzte_lektion", "weiterZiel"):
        assert wort not in html.replace("(Feld letzte_lektion)", ""), wort
    felder = re.search(r"const STAND_FELDER = new Set\(\[(.*?)\]\);", html, re.S).group(1)
    assert "letzte" not in felder
