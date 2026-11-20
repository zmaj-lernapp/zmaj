# -*- coding: utf-8 -*-
"""Das Werkzeug aufteilen.py (PLAN.md 2.1, 2.3, 2.4, 7 und G1, G4, G7, G8, G9).

An einer kleinen erfundenen App: schneiden, Byte-Probe, Zeilenkarte, der
Rueckweg --zusammen, und dass es bei jedem Fehler abbricht, ohne etwas
liegen zu lassen. An der echten App: alle 35 + 13 Anker stehen genau einmal,
und der Schnitt (nur in tmp_path) setzt sich Byte fuer Byte wieder zusammen.
Die Tests schreiben nie in web/.
"""
import io
import os
import shutil
import sys

import pytest

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(WURZEL, "web")
sys.path.insert(0, WURZEL)

import aufteilen  # noqa: E402
import app_quelle  # noqa: E402

NODE = shutil.which("node")
Z = aufteilen.ZAEHLER + "   // Teil fertig"

JS = [("eins", "/* eins */"), ("zwei", "/* ---- zwei"), ("drei", "/* ---- drei ---- */")]
CSS = [("a", "  /* ---------- A */"), ("b", "  /* ---------- B */")]
APP = ["<!doctype html>", "<html><head>", '<link href="schriften.css" rel="stylesheet">',
       '<script src="lottie.min.js"></script>', "<style>",
       "  /* ---------- A */", "  .a{background:url(symbole/x.webp)}",
       "  /* ---------- B */", "  .b{fill:url(#sternGold)} .c{background:url('flamme/aus.webp')}",
       "</style>", '<style id="festStil"></style>', "</head><body>", "<p>Markup</p>",
       "<script>", "/* Bauwerte (Probe) */", "const X = 1;", "</script>",
       "<script>", "/* eins */", "let skripteDa = false;", "var teileDa = 0;", "let a = X;", Z,
       "/* ---- zwei", "   ein Kommentar ueber zwei Zeilen */", "function f(){ return a; }", Z,
       "/* ---- drei ---- */", "const TEILE_ERWARTET = 2;", "skripteDa = true;", "init();", "</script>",
       "</body></html>", ""]


@pytest.fixture
def klein(monkeypatch):
    monkeypatch.setattr(aufteilen, "SCHNITTE_JS", JS)
    monkeypatch.setattr(aufteilen, "SCHNITTE_CSS", CSS)


def _web(tmp_path, zeilen=None, nl="\r\n"):
    web = tmp_path / "web"
    web.mkdir()
    (web / "index.html").write_bytes(nl.join(APP if zeilen is None else zeilen).encode("utf-8"))
    return str(web)


def _inhalt(web):
    """Alle Dateien unter web/ mit ihrem Inhalt (um "nichts geaendert" zu pruefen)."""
    aus = {}
    for w, _o, namen in os.walk(web):
        for n in namen:
            p = os.path.join(w, n)
            aus[os.path.relpath(p, web).replace(os.sep, "/")] = open(p, "rb").read()
    return aus


def _schneiden(web, **k):
    k.setdefault("mit_node", bool(NODE))
    k.setdefault("mit_vorwaerts", False)
    return aufteilen.schneiden(web, ausgabe=lambda *a: None, **k)


# ---------------------------------------------------------------------------
# Schneiden und zurueck
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("nl", ["\r\n", "\n"])
def test_schneiden_und_zusammen_byte_genau(tmp_path, klein, nl):
    web = _web(tmp_path, nl=nl)
    alt = open(os.path.join(web, "index.html"), "rb").read()
    plan = _schneiden(web)
    assert sorted(os.listdir(os.path.join(web, "js"))) == ["drei.js", "eins.js", "zwei.js"]
    assert sorted(os.listdir(os.path.join(web, "css"))) == ["a.css", "b.css"]
    assert app_quelle.lesen(web).encode("utf-8") == alt
    assert app_quelle.dateien(web) == ["index.html", "css/a.css", "css/b.css", "js/eins.js", "js/zwei.js", "js/drei.js"]
    neu = open(os.path.join(web, "index.html"), "rb").read().decode("utf-8")
    assert neu.count(nl) == neu.count("\n")                      # Zeilenende der Datei uebernommen
    assert '<link rel="stylesheet" href="css/a.css">' + nl + '<link rel="stylesheet" href="css/b.css">' + nl \
        + '<style id="festStil"></style>' in neu
    assert "</script>" + nl + '<script src="js/eins.js"></script>' + nl in neu    # direkt nach den Bauwerten
    assert neu.endswith('<script src="js/drei.js"></script>' + nl + "</body></html>" + nl)
    # G1: relative Adressen bekommen ../, Verweise in die Seite nicht
    a = io.open(os.path.join(web, "css", "a.css"), encoding="utf-8", newline="").read()
    b = io.open(os.path.join(web, "css", "b.css"), encoding="utf-8", newline="").read()
    assert "url(../symbole/x.webp)" in a
    assert "url(#sternGold)" in b and "url('../flamme/aus.webp')" in b
    # der mehrzeilige Anker-Kommentar bleibt ganz in seiner Datei
    assert io.open(os.path.join(web, "js", "zwei.js"), encoding="utf-8", newline="").read().startswith(
        "/* ---- zwei" + nl + "   ein Kommentar ueber zwei Zeilen */")
    assert len(plan.teile) == 5

    aufteilen.zusammen(web, ausgabe=lambda *a: None)
    assert open(os.path.join(web, "index.html"), "rb").read() == alt
    assert sorted(os.listdir(web)) == ["index.html"]             # js/ und css/ wieder weg


def test_pruefen_schreibt_nichts(tmp_path, klein):
    web = _web(tmp_path)
    vorher = _inhalt(web)
    _schneiden(web, pruefen=True)
    assert _inhalt(web) == vorher
    _schneiden(web)
    vorher = _inhalt(web)
    aufteilen.zusammen(web, pruefen=True, ausgabe=lambda *a: None)
    assert _inhalt(web) == vorher


def test_zeilenkarte(tmp_path, klein):
    web = _web(tmp_path)
    karte = str(tmp_path / "karte.tsv")
    _schneiden(web, pruefen=True, karte=karte)
    zeilen = io.open(karte, encoding="utf-8").read().splitlines()
    assert zeilen[0] == "alte_zeile\tdatei\tzeile"
    karte = {int(z.split("\t")[0]): (z.split("\t")[1], int(z.split("\t")[2])) for z in zeilen[1:]}
    assert len(karte) == len(APP) - 1          # APP endet mit "" = Zeilenende der letzten Zeile
    alt = APP
    assert karte[1] == ("index.html", 1)
    assert karte[alt.index("  .a{background:url(symbole/x.webp)}") + 1] == ("css/a.css", 2)
    assert karte[alt.index("function f(){ return a; }") + 1] == ("js/zwei.js", 3)
    assert karte[alt.index("init();") + 1] == ("js/drei.js", 4)
    # Markup rutscht um den Stil nach oben
    _schneiden(web)
    neu = open(os.path.join(web, "index.html"), encoding="utf-8").read().splitlines()
    datei, zeile = karte[alt.index("<p>Markup</p>") + 1]
    assert datei == "index.html" and neu[zeile - 1] == "<p>Markup</p>"
    for k, z in enumerate(alt[:-1]):
        datei, zeile = karte[k + 1]
        if datei != "index.html":
            text = open(os.path.join(web, datei), encoding="utf-8").read().splitlines()
            assert app_quelle.css_zurueck(text[zeile - 1]) == z


# ---------------------------------------------------------------------------
# Abbrueche: es bleibt nichts liegen
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("aendern, meldung", [
    (lambda z: [x for x in z if x != "/* ---- zwei"], "0-mal"),
    (lambda z: z[:z.index("/* ---- drei ---- */")] + ["/* ---- zwei"] + z[z.index("/* ---- drei ---- */"):],
     "2-mal"),
    (lambda z: [x.replace("/* ---- drei ---- */", "/* ---- drei ----*/") for x in z], "0-mal"),
    (lambda z: [x.replace("  /* ---------- B */", "/* ---------- B */") for x in z], "0-mal"),      # G9
    (lambda z: [x for x in z if x != Z], "Zaehlzeile"),
    (lambda z: [x.replace("const TEILE_ERWARTET = 2;", "const TEILE_ERWARTET = 3;") for x in z], "TEILE_ERWARTET"),
    (lambda z: [x.replace("  .a{background:url(symbole/x.webp)}", "  .a{background:url(../x.webp)}") for x in z],
     "url"),
    (lambda z: [x for x in z if x != "init();"], "init();"),
    (lambda z: z[:5] + ["<style>"] + z[5:], "<style>"),
    (lambda z: z[:2] + ['<script src="js/alt.js"></script>'] + z[2:], "schon geteilt"),
])
def test_bricht_ab_ohne_zu_schreiben(tmp_path, klein, aendern, meldung):
    web = _web(tmp_path, aendern(list(APP)))
    vorher = _inhalt(web)
    with pytest.raises(aufteilen.Abbruch, match=meldung.replace("(", r"\(").replace(")", r"\)")):
        _schneiden(web)
    assert _inhalt(web) == vorher


def test_gemischte_zeilenenden(tmp_path, klein):
    web = _web(tmp_path)
    p = os.path.join(web, "index.html")
    roh = open(p, "rb").read()
    open(p, "wb").write(roh.replace(b"\r\n", b"\n", 1))
    with pytest.raises(aufteilen.Abbruch, match="gemischte"):
        _schneiden(web)


@pytest.mark.parametrize("name", ["_kern", "Ton", "ton2", "ton-alt", "vorfuehrung", "eins"])
def test_dateinamen(tmp_path, monkeypatch, name):
    """G8, PLAN 1.5: nur a-z und _, keine Ziffern, nichts, was app_bauen
    beim Kopieren weglaesst, kein 'vorfuehrung', kein Name zweimal."""
    monkeypatch.setattr(aufteilen, "SCHNITTE_JS", [JS[0], (name, JS[1][1]), JS[2]])
    monkeypatch.setattr(aufteilen, "SCHNITTE_CSS", CSS)
    web = _web(tmp_path)
    with pytest.raises(aufteilen.Abbruch, match="Dateiname"):
        _schneiden(web)
    assert os.listdir(web) == ["index.html"]


@pytest.mark.skipif(not NODE, reason="node fehlt")
def test_teil_der_allein_nicht_parst(tmp_path, klein):
    """G4: ein Kommentar ueber die Grenze - zusammen gueltig, die Datei allein nicht."""
    z = list(APP)
    i = z.index("/* ---- zwei")
    z[i - 1:i + 2] = ["/*", Z, "/* ---- zwei", "*/ /* ein Kommentar ueber zwei Zeilen */"]
    web = _web(tmp_path, z)
    with pytest.raises(aufteilen.Abbruch, match="node --check js/eins.js"):
        _schneiden(web)
    assert os.listdir(web) == ["index.html"]


def test_stellt_wieder_her_wenn_die_probe_in_web_scheitert(tmp_path, klein, monkeypatch):
    web = _web(tmp_path)
    vorher = _inhalt(web)
    echt = aufteilen.gleichheit_pruefen

    def nur_im_zwischenordner(ordner, plan):
        if os.path.abspath(ordner) == os.path.abspath(web):
            raise aufteilen.Abbruch("Probe")
        return echt(ordner, plan)
    monkeypatch.setattr(aufteilen, "gleichheit_pruefen", nur_im_zwischenordner)
    with pytest.raises(aufteilen.Abbruch, match="Probe"):
        _schneiden(web)
    assert _inhalt(web) == vorher
    assert sorted(os.listdir(web)) == ["index.html"]


def test_nicht_in_volle_ordner(tmp_path, klein):
    web = _web(tmp_path)
    os.makedirs(os.path.join(web, "js"))
    open(os.path.join(web, "js", "fremd.js"), "w").close()
    with pytest.raises(aufteilen.Abbruch, match="nicht leer"):
        _schneiden(web)
    assert os.listdir(os.path.join(web, "js")) == ["fremd.js"]


def test_zusammen_nur_mit_genau_den_geladenen_dateien(tmp_path, klein):
    web = _web(tmp_path)
    _schneiden(web)
    open(os.path.join(web, "js", "uebrig.js"), "w").close()
    vorher = _inhalt(web)
    with pytest.raises(aufteilen.Abbruch, match="uebrig.js"):
        aufteilen.zusammen(web, ausgabe=lambda *a: None)
    assert _inhalt(web) == vorher
    os.remove(os.path.join(web, "js", "uebrig.js"))
    os.remove(os.path.join(web, "css", "b.css"))
    with pytest.raises(aufteilen.Abbruch, match="b.css"):
        aufteilen.zusammen(web, ausgabe=lambda *a: None)


def test_zusammen_ungeteilt(tmp_path, klein):
    with pytest.raises(aufteilen.Abbruch, match="nicht geteilt"):
        aufteilen.zusammen(_web(tmp_path), ausgabe=lambda *a: None)


def test_main_meldet_abbruch(tmp_path, klein, capsys):
    web = _web(tmp_path, [x for x in APP if x != "/* ---- zwei"])
    assert aufteilen.main(["--web", web, "--pruefen"]) == 1
    assert "ABBRUCH" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Die echte App (nur in tmp_path)
# ---------------------------------------------------------------------------
def test_tabellen_wie_im_plan():
    js = [n for n, _ in aufteilen.SCHNITTE_JS]
    css = [n for n, _ in aufteilen.SCHNITTE_CSS]
    assert len(js) == 35 and js[0] == "grundwerte" and js[-1] == "start"
    assert len(css) == 13 and css[0] == "grund" and css[-1] == "tablet"
    for name in js + css:
        assert aufteilen.NAME.fullmatch(name) and "vorfuehrung" not in name, name
    assert all(a.startswith("  /* ") for _, a in aufteilen.SCHNITTE_CSS)          # G9
    assert all(a == a.rstrip("\r\n") and a.strip() for _, a in aufteilen.SCHNITTE_JS + aufteilen.SCHNITTE_CSS)


def test_echte_app_schneiden_und_zusammensetzen(tmp_path):
    """Jeder Anker steht genau einmal, alle Proben bestehen (mit node und
    der Vorwaerts-Pruefung, wenn sie da sind), und der Schnitt einer Kopie
    setzt sich Byte fuer Byte wieder zusammen. Ist web/ schon geteilt, wird
    die zusammengesetzte Fassung geschnitten - das muss dieselben Teile geben."""
    alt = app_quelle.lesen(WEB)
    plan = aufteilen.planen(alt)
    aufteilen.proben(plan, mit_node=bool(NODE))
    web = str(tmp_path / "web")
    os.makedirs(web)
    with io.open(os.path.join(web, "index.html"), "w", encoding="utf-8", newline="") as f:
        f.write(alt)
    _schneiden(web, mit_node=False)
    assert app_quelle.lesen(web).encode("utf-8") == alt.encode("utf-8")
    assert len(plan.teile) == 48
    groesse = os.path.getsize(os.path.join(web, "index.html"))
    assert groesse < 100 * 1024, groesse                 # vorher ueber 1 MB
    if app_quelle.dateien(WEB)[1:]:
        for t in plan.teile:
            assert open(os.path.join(web, t.pfad), "rb").read() == open(os.path.join(WEB, t.pfad), "rb").read(), t.pfad
    aufteilen.zusammen(web, ausgabe=lambda *a: None)
    with io.open(os.path.join(web, "index.html"), encoding="utf-8", newline="") as f:
        assert f.read() == alt
