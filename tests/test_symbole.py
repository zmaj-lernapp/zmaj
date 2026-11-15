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


def test_goldenes_herz_mit_vollversion(wurzel, index_html):
    """Goldenes Herz fuer die Vollversion (14.11.2026). Ajdin nach dem Kauf
    im iPhone-Test: alles frei, "nur das das herz nicht gold ist".
    herzSymbol() nimmt mit premium das goldene, sonst das rote - und jede
    Stelle, an der neben dem Herz ∞ stehen kann, baut es mit herzSymbol():
    Kopfleiste, Fragenkasten, Statistik nach Lektion und Test."""
    assert "function herzSymbol(sagt){ return symbol(premium ? 'herzgold' : 'herz', sagt); }" in index_html
    assert "herzgold" in _symbole(index_html)
    assert os.path.isfile(os.path.join(wurzel, "web", "symbole", "herzgold.webp"))
    zeilen = [z for z in _ohne_kommentare(index_html).splitlines() if "'∞'" in z]
    assert len(zeilen) == 4, zeilen
    for z in zeilen:
        assert "herzSymbol(" in z and "symbol('herz'" not in z, z


# Einheitlich auf Android und iPhone (14.11.2026): die letzten Emojis der
# Oberflaeche, gemalt wie Symbol-Satz V1. Die Benachrichtigungen (ben.*)
# zeigt das Betriebssystem, dort bleiben Emojis.
GEMALT_WEG = ["🏁", "⭐", "💙", "✨", "✉"]


def test_texte_ohne_gemalte_emojis(sprachcodes):
    """Kein Text der Oberflaeche traegt noch 🏁 ⭐ 💙 ✨ ✉ - das Bild kommt
    aus dem Code. Die drei Texte, die sie trugen, stehen in jeder Sprache
    ohne Zeichen am Rand da."""
    import sprachen
    fehler = []
    for code in sprachcodes:
        texte = sprachen.texte(code)
        for k, v in texte.items():
            if not isinstance(v, str) or k.startswith("ben."):
                continue
            fehler += [(code, k, e) for e in GEMALT_WEG if e in v]
        for k in ("level.test", "bew.bewerten", "bew.danke"):
            assert texte[k] == texte[k].strip() and texte[k], (code, k, texte[k])
    assert not fehler, fehler


def test_index_ohne_gemalte_emojis_und_mit_bild(wurzel, index_html):
    """Im Quelltext der App (ohne Kommentare) steht keines dieser Emojis
    mehr. Stattdessen: Zielflagge vor dem Level-Test, Stern vor "Zmaj
    bewerten", blaues Herz nach "Danke!", Funken an der goldenen Flamme
    (oben im Kopf und in flammeHtml), Brief vor der E-Mail im Profil."""
    code = _ohne_kommentare(index_html)
    assert not [e for e in GEMALT_WEG if e in code]
    assert "bt.innerHTML = mitSymbol('ziel', esc(t('level.test')));" in code
    assert "#bwJa').innerHTML = mitSymbol('stern', esc(t('bew.bewerten')));" in code
    assert "note.insertAdjacentHTML('afterbegin', esc(t('bew.danke')) + ' ' + symbol('herzblau') + ' ');" in code
    assert code.count("mitSymbol('brief', esc(") == 2
    assert code.count('<span class="funke f') == 6
    assert code.count('<img class="sym sym-funken" src="symbole/funken.webp" alt="" aria-hidden="true">') == 3
    assert code.count("symbol('funken')") == 3
    for n in ("ziel", "stern", "herzblau", "funken", "brief"):
        assert n in _symbole(index_html), n
        assert os.path.isfile(os.path.join(wurzel, "web", "symbole", n + ".webp")), n


GEZEICHNET_WEG = ["⏭", "⏸", "⏹", "✕", "\\u23ed", "\\u23f8", "\\u23f9", "\\u2715", "&#10005;", "&times;"]


def test_texte_ohne_gezeichnete_zeichen(sprachcodes):
    """⏭ ⏸ ⏹ ✕ stehen in keinem Text mehr; Pause, Stopp und die drei
    Abbrechen-Knoepfe haben in jeder Sprache nur ihr Wort."""
    import sprachen
    fehler = []
    for code in sprachcodes:
        texte = sprachen.texte(code)
        for k, v in texte.items():
            if isinstance(v, str) and not k.startswith("ben."):
                fehler += [(code, k, e) for e in GEZEICHNET_WEG if e in v]
        for k in ("gesch.pause", "gesch.stopp", "lektion.abbrechen", "test.abbrechen", "einst.abbrechen"):
            assert texte[k] == texte[k].strip() and texte[k][0].isalpha(), (code, k, texte[k])
    assert not fehler, fehler


def test_zeichen_selbst_gezeichnet(index_html):
    """zeichen() zeichnet weiter, pause, stopp und zu als Inline-SVG in der
    Schriftfarbe (currentColor), als Schmuck (aria-hidden). Benutzt am
    Ueberspringen-Knopf, beim Vorlesen (Pause, Stopp) und per data-zeichen
    an den drei Abbrechen-Knoepfen, die applyTexts() fuellt."""
    code = _ohne_kommentare(index_html)
    assert not [e for e in GEZEICHNET_WEG if e in code]
    m = re.search(r"function zeichen\(name\)\{(.*?)\n\}", index_html, re.S)
    assert m, "zeichen() fehlt"
    formen = set(re.findall(r"\n\s*(\w+): '<", m.group(1)))
    assert formen == {"weiter", "pause", "stopp", "zu"}, formen
    assert 'aria-hidden="true" focusable="false"' in m.group(1) and 'class="zei zei-' in m.group(1)
    regel = re.search(r"\n\s*\.zei\{([^}]*)\}", index_html).group(1)
    assert "fill:currentColor" in regel and "stroke:currentColor" in regel, regel
    assert "width:1em" in regel and "height:1em" in regel and "vertical-align:calc(.35em - .5em)" in regel, regel
    assert "'<button class=\"skip\" id=\"xSkip\">'+text+'\\u00a0'+zeichen('weiter')+'</button>'" in code
    assert code.count("knopfVor.innerHTML = zeichen('pause') + ' ' + esc(t('gesch.pause'));") == 2
    assert "hidden>'+zeichen('stopp')+'</button>" in code
    for k in ("lQuit", "tQuit", "eQuit"):
        assert re.search(r'<button id="%s" data-t="[a-z.]+" data-zeichen="zu"></button>' % k, code), k
    assert "(el.dataset.zeichen ? zeichen(el.dataset.zeichen) + '\\u00a0' : '') + t(el.dataset.t, vars)" in code


# 🎉 und ▶ gemalt (Offen-Liste 5a, 15.11.2026). Ajdin: "Male sie",
# abgenommen mit "Passt". Wie oben: das Bild kommt aus dem Code, die Texte
# tragen das Zeichen nicht mehr. Die Benachrichtigungen (ben.*) bleiben.
GEMALT_WEG_5A = ["🎉", "▶", "\\u25b6", "\\U0001f389", "&#9654;", "&#127881;"]
PLAY_TEXTE = ("level.lektion", "gesch.weiterlesen")
KONFETTI_TEXTE = ("lektion.geschafft", "test.bestanden", "test.sektion_fertig", "topf.fertig", "gesch.geschafft")


def test_texte_ohne_konfetti_und_play(sprachcodes):
    """Kein Text der Oberflaeche traegt noch 🎉 oder ▶. Die sieben Texte,
    die sie trugen, stehen in jeder Sprache ohne Zeichen und ohne Leerraum
    am Rand da (gesch.geschafft beginnt wie bisher mit " – ")."""
    import sprachen
    fehler = []
    for code in sprachcodes:
        texte = sprachen.texte(code)
        for k, v in texte.items():
            if isinstance(v, str) and not k.startswith("ben."):
                fehler += [(code, k, e) for e in GEMALT_WEG_5A if e in v]
        for k in PLAY_TEXTE + KONFETTI_TEXTE:
            v = texte[k]
            assert v and v == v.rstrip() and v[-1] not in " \u00a0", (code, k, v)
            assert v == v.lstrip() or k == "gesch.geschafft", (code, k, v)
            assert v[0].isalpha() or k == "gesch.geschafft", (code, k, v)
        assert texte["gesch.geschafft"].startswith(" – "), (code, texte["gesch.geschafft"])
    assert not fehler, fehler


def test_konfetti_und_play_aus_dem_code(wurzel, index_html):
    """Im Quelltext (ohne Kommentare) kein 🎉 und kein ▶ mehr. play vor
    "Lektion starten", "Weitermachen · ..." und "Weiterlesen", konfetti
    ueber mitKonfetti() nach den fuenf Erfolgssaetzen - mit dem letzten Wort
    in .amwort, das geschuetzte Leerzeichen als Fluchtfolge, nicht als
    unsichtbares Zeichen."""
    code = _ohne_kommentare(index_html)
    assert not [e for e in GEMALT_WEG_5A if e in code]
    m = re.search(r"function mitKonfetti\(html\)\{(.*?)\n\}", code, re.S)
    assert m, "mitKonfetti() fehlt"
    assert "'<span class=\"amwort\">' + html.slice(i) + '\\u00a0' + symbol('konfetti') + '</span>'" in m.group(1)
    assert "\u00a0" not in m.group(1)
    # Das letzte Wort und das Bild brechen nicht auseinander (in Chrome reicht
    # das geschuetzte Leerzeichen vor einem Bild allein nicht)
    assert ".amwort{white-space:nowrap}" in index_html
    assert ": mitSymbol('play', esc(t('level.lektion'))); }" in code
    assert "k.innerHTML = mitSymbol('play', esc(t('btn.weitermachen') + ' · ' + name));" in code
    assert "knopfVor.innerHTML = mitSymbol('play', esc(t('gesch.weiterlesen')));" in code
    assert code.count("mitSymbol('play'") == 3
    for k in KONFETTI_TEXTE:
        if k.startswith("test."):
            continue
        assert "mitKonfetti(t('%s'))" % k in code, k
    assert "mitKonfetti(t(nextSec ? 'test.sektion_fertig' : 'test.bestanden'))" in code
    assert code.count("mitKonfetti(") == 5   # die Funktion und vier Stellen (der Test mit zwei Texten)
    for n in ("konfetti", "play"):
        assert n in _symbole(index_html), n
        assert os.path.isfile(os.path.join(wurzel, "web", "symbole", n + ".webp")), n
