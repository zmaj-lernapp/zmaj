# -*- coding: utf-8 -*-
"""Kein heller Antwortknopf nach einem Fingertipp (15.11.2026, Offen-Liste 5b):
was sich ohne Browser pruefen laesst. Den Fehler selbst - nach "Weiter" unter
einem neuen Wort hatte der Antwortknopf unten rechts den hellen Grund von
"richtig" - prueft tests_e2e/test_heller_knopf.py mit echten Tipps in Chromium
und WebKit.

Am Handy bleibt :hover nach einem Tipp an der Stelle des Fingers haengen.
Deshalb steht jedes :hover der App in @media (hover:hover) and (pointer:fine),
und der Knopf der Reiterwahl zeigt den Fokus nur ueber :focus-visible."""
import re

MAUS = "@media (hover:hover) and (pointer:fine){ "

# Jede Hervorhebung unter dem Zeiger, die es am 15.11.2026 gab - unveraendert,
# nur in die Abfrage gesetzt. .opt dazu nur, solange der Knopf offen ist.
HOVER = [
    ".back:hover{border-color:var(--primary); color:var(--primary)}",
    ".langbar button:hover{border-color:var(--primary)}",
    ".node:hover .circle{transform:scale(1.06)}",
    ".livesbar .herz:hover{background:var(--primary-soft)}",
    ".sprachzeile:hover{background:var(--primary-soft)}",
    ".listen:hover{border-color:var(--primary); color:var(--primary)}",
    ".skip:hover{color:var(--primary)}",
    ".opt:not(:disabled):hover{border-color:var(--primary); background:var(--primary-soft)}",
    ".story .w:hover{background:var(--accent-soft); color:var(--primary); border-bottom-color:var(--accent)}",
]

# Die Farben nach dem Antworten bleiben, wie sie waren.
UNVERAENDERT = [
    ".opt.right{border-color:var(--good); background:var(--primary-soft); color:var(--good-text); "
    "box-shadow:0 3px 0 var(--good-dark)}",
    ".opt.wrong{border-color:var(--bad); color:var(--bad-text); box-shadow:0 3px 0 var(--bad)}",
    ".opt:active{transform:translateY(2px); box-shadow:none}",
    ".story .w.on{background:var(--accent-soft); color:var(--primary); border-bottom-color:var(--accent)}",
    "input.field:focus,textarea.field:focus,select.field:focus{outline:none; border-color:var(--primary)}",
]


def _css(index_html):
    """Alle Stilbloecke ohne Kommentare, Zeilen ohne Einrueckung."""
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", index_html, re.S))
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [z.strip() for z in css.replace("\r\n", "\n").split("\n") if z.strip()]


def test_jedes_hover_nur_mit_maus(index_html):
    zeilen = _css(index_html)
    mit = [z for z in zeilen if ":hover" in z]
    assert len(mit) >= len(HOVER)
    for z in mit:
        # eine Regel je Zeile, ganz in der Abfrage - sonst gilt sie auch am Handy
        assert z.startswith(MAUS) and z.endswith("} }") and z.count("{") == 2, z
    for regel in HOVER:
        assert MAUS + regel + " }" in zeilen, regel


def test_hover_nur_auf_offenen_knoepfen(index_html):
    """Ein beantworteter Knopf ist disabled und leuchtet auch mit Maus nicht auf."""
    assert not any(re.search(r"\.opt:hover\b", z) for z in _css(index_html))


def test_farben_nach_dem_antworten_unveraendert(index_html):
    zeilen = _css(index_html)
    for regel in UNVERAENDERT:
        assert regel in zeilen, regel


def test_fokus_der_knoepfe_nur_sichtbar_mit_tastatur(index_html):
    zeilen = _css(index_html)
    # Kein Knopf mit :focus (ohne -visible); Eingabefelder duerfen, dort steht der Cursor.
    for z in zeilen:
        for teil in z.split("{")[0].split(","):
            if re.search(r":focus(?![-\w])", teil):
                assert re.match(r"(input|textarea|select)\.|\.(blank|type)-input:", teil.strip()), z
    # Eigene Regel: eine alte WebView verwirft sonst mit :focus-visible die ganze Liste.
    assert "button.field:focus-visible{outline:none; border-color:var(--primary)}" in zeilen
    for z in zeilen:
        if ":focus-visible" in z:
            assert "," not in z.split("{")[0], z
