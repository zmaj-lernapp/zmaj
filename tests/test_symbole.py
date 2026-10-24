# -*- coding: utf-8 -*-
"""Gemalte Symbole statt Emojis (24.10.2026).

Ajdin am 23.10.2026: "die emojis die muessten mal anders gemacht werden".
Seitdem stehen statt 📚 📖 🔁 🛒 ⚙ 👤 🪙 ♥ 🔊 🔒 die Bilder aus web/symbole
in der Oberflaeche (Symbol-Satz V1, "nimm v1 komplett"). Hier ohne Browser:
die Texte aller acht Sprachen, der Quelltext der App und die Bilder selbst.
Wie es aussieht und mittig sitzt, pruefen tests_e2e/test_symbole.py.
"""
import io
import os
import re

import pytest

WEG = ["📚", "📖", "🔁", "🛒", "🪙", "♥", "🔊", "🔒", "⚙", "👤"]
ENTITAETEN = ["&#128722;", "&#128100;", "&#9881;", "&#9829;", "&hearts;"]


def _ohne_kommentare(html):
    html = re.sub(r"/\*.*?\*/", "", html, flags=re.S)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", html)


def _symbole(index_html):
    """Die Namen aus SYMBOLE = [...] in index.html."""
    m = re.search(r"const SYMBOLE = \[([^\]]*)\]", index_html)
    assert m, "SYMBOLE fehlt in index.html"
    return re.findall(r"'([a-z]+)'", m.group(1))


def test_texte_ohne_ersetzte_emojis(sprachcodes):
    """Kein Text der Oberflaeche traegt noch eines der Emojis. Ausnahme: die
    Benachrichtigungen (ben.*) - die zeigt Android selbst, ein Bild geht
    dort nicht ("Deine Leben sind wieder voll ♥")."""
    import sprachen
    fehler = []
    for code in sprachcodes:
        for k, v in sprachen.texte(code).items():
            if not isinstance(v, str) or k.startswith("ben."):
                continue
            for e in WEG:
                if e in v:
                    fehler.append((code, k, e))
    assert not fehler, fehler


@pytest.mark.parametrize("key,platzhalter", [
    ("quest.fertig", ["{muenze}"]),
    ("lektion.leben_muenzen", ["{herz}", "{muenze}"]),
    ("app.fuss", ["{einstellungen}"]),
])
def test_symbol_platzhalter_in_allen_sprachen(sprachcodes, key, platzhalter):
    """Mitten im Satz steht das Symbol als Platzhalter, den symbolTexte()
    mit dem Bild fuellt - in jeder Sprache genau einmal."""
    import sprachen
    for code in sprachcodes:
        v = sprachen.texte(code)[key]
        for p in platzhalter:
            assert v.count(p) == 1, (code, key, v)


def test_index_ohne_ersetzte_emojis(index_html):
    """Im Quelltext der App (ohne Kommentare) steht keines der Emojis mehr.
    Einzige Stelle: SYMBOL_SAGT, der Ersatztext fuer Bildschirmleser, wo kein
    Wort neben dem Bild steht."""
    code = _ohne_kommentare(index_html)
    code = re.sub(r"const SYMBOL_SAGT = \{[^}]*\};", "", code)
    funde = [e for e in WEG + ENTITAETEN if e in code]
    assert not funde, funde


def test_jedes_symbol_hat_sein_bild(wurzel, index_html):
    """Jeder Name, den die App benutzt - in SYMBOLE, in symbol('...') und
    mitSymbol('...') und als src im Kopf -, liegt als Bild in web/symbole."""
    namen = set(_symbole(index_html))
    namen |= set(re.findall(r"\b(?:symbol|mitSymbol)\('([a-z]+)'", index_html))
    namen |= set(re.findall(r'src="symbole/([a-z]+)\.webp"', index_html))
    assert {"lernpfad", "geschichten", "wiederholen", "muenze", "herz", "laden",
            "einstellungen", "profil", "lautsprecher", "schloss"} <= namen, namen
    fehlt = [n for n in sorted(namen) if not os.path.isfile(os.path.join(wurzel, "web", "symbole", n + ".webp"))]
    assert not fehlt, fehlt
    # Vorgeladen wird jedes Symbol, das symbol() bauen kann
    assert set(re.findall(r"\b(?:symbol|mitSymbol)\('([a-z]+)'", index_html)) <= set(_symbole(index_html))


def _webp_groesse(pfad):
    with io.open(pfad, "rb") as f:
        kopf = f.read(30)
    assert kopf[:4] == b"RIFF" and kopf[8:12] == b"WEBP", pfad
    art = kopf[12:16]
    if art == b"VP8X":
        return (int.from_bytes(kopf[24:27], "little") + 1, int.from_bytes(kopf[27:30], "little") + 1)
    if art == b"VP8L":
        b = int.from_bytes(kopf[21:25], "little")
        return ((b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1)
    if art == b"VP8 ":
        return (int.from_bytes(kopf[26:28], "little") & 0x3FFF, int.from_bytes(kopf[28:30], "little") & 0x3FFF)
    raise AssertionError("unbekanntes WebP: %s" % pfad)


def test_bilder_quadratisch(wurzel, index_html):
    """.sym setzt Breite gleich Hoehe. Damit nichts verzerrt, muessen die
    Bilder quadratisch sein - und gross genug fuer ein Handy mit dreifacher
    Pixeldichte (der grosse Hoerknopf zeigt rund 44 px)."""
    for n in _symbole(index_html):
        b, h = _webp_groesse(os.path.join(wurzel, "web", "symbole", n + ".webp"))
        assert b == h and b >= 128, (n, b, h)


def test_eine_klasse_in_em(index_html):
    """Eine Klasse fuer alle Symbolbilder, die Groesse in em (waechst mit der
    Schrift), Breite gleich Hoehe, mittig zur Schrift."""
    m = re.search(r"\n\s*\.sym\{([^}]*)\}", index_html)
    assert m, ".sym fehlt"
    regel = m.group(1)
    assert re.search(r"--sg:[\d.]+em", regel), regel
    assert "width:var(--sg)" in regel and "height:var(--sg)" in regel, regel
    assert "vertical-align:calc(.35em - var(--sg) / 2)" in regel, regel
    # Je Ort nur --sg, in em (in der Kopfleiste mit Deckel in px)
    for ort in re.findall(r"\n\s*([^{}\n]*\.sym)\{([^}]*)\}", index_html):
        if ort[0].strip() == ".sym":
            continue
        assert re.fullmatch(r"--sg:(?:[\d.]+em|min\([\d.]+em, \d+px\))", ort[1]), ort


def test_bilder_als_schmuck_oder_mit_ersatztext(index_html):
    """symbol(name) ohne Ersatztext ist alt="" und aria-hidden, im Kopf
    ebenso. Mit Ersatztext steht nur alt."""
    m = re.search(r"function symbol\(name, sagt\)\{(.*?)\n\}", index_html, re.S)
    assert m, "symbol() fehlt"
    assert "alt=\"\" aria-hidden=\"true\"" in m.group(1)
    for img in re.findall(r'<img class="sym"[^>]*>', index_html):
        assert 'alt=""' in img and 'aria-hidden="true"' in img, img
