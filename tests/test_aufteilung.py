# -*- coding: utf-8 -*-
"""Die Aufteilung von web/index.html in web/js und web/css (1.5).

Plan: Release/Aufteilung/PLAN.md (3.2 und die Gegenpruefung G1, G4, G6, G8).
Ajdin am 20.11.2026: "am besten ist es das du die app jetzt aufteilst damit
es effizienter wird". Die App laedt dann 35 klassische Skripte und 13
Stilblaetter der Reihe nach; die Bauwerte bleiben als kleiner Block in
index.html, und app_quelle.lesen() setzt fuer Tests und Werkzeuge alles
wieder zu der alten Einzeldatei zusammen.

Solange index.html noch nicht geteilt ist, laufen die Teile, die nur mit
Dateien unter web/js und web/css etwas pruefen, nicht (uebersprungen mit
"noch nicht geteilt"). Alles andere gilt schon heute.
"""
import collections
import http.server
import io
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.request

import pytest

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(WURZEL, "web")
sys.path.insert(0, WURZEL)

import app_quelle  # noqa: E402

TEILE = app_quelle.dateien(WEB)[1:]
geteilt = pytest.mark.skipif(not TEILE, reason="web/index.html ist noch nicht geteilt")
NAME = re.compile(r"[a-z0-9_]+\.(?:js|css)")
# Jeder Verweis auf einen Teil, auch einer, den app_quelle nicht erkennt
# (Grossbuchstaben, Unterordner, andere Schreibweise des Tags).
JEDER_VERWEIS = re.compile(r"""(?:src|href)\s*=\s*["']?((?:\./)?(?:js|css)/[^"'\s>]*)""", re.I)
URL = re.compile(r"""url\(\s*(['"]?)([^'")]*)\1\s*\)""")


def _lesen(pfad):
    with io.open(pfad, encoding="utf-8", newline="") as f:
        return f.read()


def _index():
    return _lesen(os.path.join(WEB, "index.html"))


def _js_teile():
    return [t for t in TEILE if t.startswith("js/")]


def _node():
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    return shutil.which("node")


def _node_check(text, tmp_path, name="probe.js"):
    probe = tmp_path / name
    probe.write_bytes(text.encode("utf-8"))
    r = subprocess.run([_node(), "--check", str(probe)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.returncode, r.stdout.decode("utf-8", "replace")[:600]


def _stil(html):
    """Der grosse Stil zwischen dem ersten <style> und </style> (nicht festStil)."""
    a = html.index("<style>")
    a = html.index("\n", a) + 1
    return html[a:html.index("</style>", a)]


# ---------------------------------------------------------------------------
# 1. Was index.html laedt, liegt da - und nichts anderes (dazu G8)
# ---------------------------------------------------------------------------
def test_jeder_teil_geladen_und_keiner_uebrig():
    """Exakt mit os.listdir verglichen, nicht mit os.path.exists: Windows,
    start.py und die Browser-Tests verzeihen js/Ton.js statt js/ton.js, die
    Assets von Android und iOS nicht (G8)."""
    html = _index()
    verweise = [m.group(1) for m in JEDER_VERWEIS.finditer(html)]
    assert verweise == TEILE, "Verweise, die app_quelle nicht als Teil erkennt: %s" % (
        sorted(set(verweise) - set(TEILE)))
    assert len(TEILE) == len(set(TEILE)), [t for t, n in collections.Counter(TEILE).items() if n > 1]
    for ordner in ("js", "css"):
        geladen = sorted(t.split("/", 1)[1] for t in TEILE if t.startswith(ordner + "/"))
        pfad = os.path.join(WEB, ordner)
        da = sorted(os.listdir(pfad)) if os.path.isdir(pfad) else []
        assert da == geladen, "%s/: liegt da %s, geladen %s" % (ordner, da, geladen)


@geteilt
def test_dateinamen_nur_klein_und_ohne_vorfuehrung():
    """Nur ASCII-Kleinbuchstaben, Ziffern und _. Kein Name mit "vorfuehrung":
    keine_vorfuehrung() (app_bauen.py --ios) sucht das Wort irgendwo in
    index.html und braeche jeden Store-Bau ab (G8)."""
    for teil in TEILE:
        name = teil.split("/", 1)[1]
        assert NAME.fullmatch(name), teil
        assert "vorfuehrung" not in name, teil


@geteilt
def test_alle_teile_kommen_ins_paket(tmp_path, monkeypatch):
    """Mit app_bauen.kopieren() selbst, nicht nachgebaut: ein Teil, den
    RAUS_* weglaesst (_kern.js, ton.js.alt, ...), fehlte auf dem Handy."""
    import app_bauen
    web = tmp_path / "web"
    for name in ["index.html"] + TEILE:
        ziel = web / name
        ziel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(os.path.join(WEB, name), str(ziel))
    monkeypatch.setattr(app_bauen, "WEB", str(web))
    www = tmp_path / "huelle" / "www"
    www.parent.mkdir()
    app_bauen.kopieren(str(www))
    for name in ["index.html"] + TEILE:
        assert (www / name).is_file(), name
        assert (www / name).read_bytes() == (web / name).read_bytes(), name


# ---------------------------------------------------------------------------
# 2. Die Bauwerte stehen genau einmal im Block in index.html (PLAN 1.2, G2)
# ---------------------------------------------------------------------------
def _bauwert_zeilen():
    import app_bauen
    import demo_bauen
    return ([app_bauen.TESTWERBUNG_AUS, app_bauen.PACKEN_AUS, app_bauen.DAUER_PLATZHALTER,
             app_bauen.CLOUD_SCHALTER_AUS, demo_bauen.WERBUNG_ALT, app_bauen.IOS_APPLE_ID_ZEILE]
            + list(app_bauen.CLOUD_PLATZHALTER.values()) + list(app_bauen.IOS_ADMOB_ZEILEN.values())
            # G2: die Android-Bloecke (tests/test_ios.py prueft sie in der Kopie)
            + ["const ADMOB_ID_ANDROID = {", "const ADMOB_ID_IOS = {",
               "  interstitial: 'ca-app-pub-9105747905460295/9764395638',",
               "  belohnt:      'ca-app-pub-9105747905460295/8572576770',"])


def test_bauwerte_genau_einmal_im_block():
    import app_bauen
    html = _index()
    block = app_quelle.bauwerte(html)
    ganz = app_quelle.lesen(WEB)
    for zeile in _bauwert_zeilen():
        assert html.count(zeile) == 1, zeile
        assert block.count(zeile) == 1, zeile
        assert ganz.count(zeile) == 1, zeile
        for teil in _js_teile():
            assert zeile not in _lesen(os.path.join(WEB, teil)), (zeile, teil)
    assert len(app_bauen.APP_VERSION_ZEILE.findall(html)) == 1
    assert len(app_bauen.APP_VERSION_ZEILE.findall(block)) == 1
    assert len(app_bauen.APP_VERSION_ZEILE.findall(ganz)) == 1


def test_bauwerte_vor_den_skripten_und_kopfanker_im_kopf():
    """Der Block steht nach dem Markup und direkt vor den Skripten der App.
    vorfuehrung_einsetzen() haengt sich an lottie.min.js im Kopf - davor,
    also auch vor den Bauwerten."""
    import app_bauen
    html = _index()
    block = app_quelle.bauwerte(html)
    anfang = html.index(block)
    ende = html.index("</script>", anfang) + len("</script>")
    danach = html[ende:].lstrip("\r\n")
    assert danach.startswith("<script>") or danach.startswith('<script src="js/'), danach[:60]
    assert anfang > html.index("<body")
    assert html.count(app_bauen.VORFUEHRUNG_ANKER) == 1
    assert html.index(app_bauen.VORFUEHRUNG_ANKER) < html.index("</head>")
    ganz = app_quelle.lesen(WEB)
    assert app_bauen.VORFUEHRUNG_DATEI not in ganz and app_bauen.VORFUEHRUNG_CLOUD["projekt"] not in ganz


def test_bauwerte_brauchen_nichts(tmp_path):
    """Nur reine Werte: der Block laeuft vor allem anderen und darf nichts
    aus der App brauchen (sonst ReferenceError beim Start)."""
    node = _node()
    probe = tmp_path / "bauwerte.js"
    probe.write_bytes(app_quelle.bauwerte(_index()).encode("utf-8"))
    r = subprocess.run([node, str(probe)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert r.returncode == 0, r.stdout.decode("utf-8", "replace")[:600]
    namen = re.findall(r"^const ([A-Z_]+) +=", app_quelle.bauwerte(_index()), re.M)
    assert len(namen) == len(set(namen)) >= 12, namen


# ---------------------------------------------------------------------------
# 3. Reihenfolge der Skripte und Stilblaetter (PLAN 1.1)
# ---------------------------------------------------------------------------
def test_init_ist_die_letzte_anweisung():
    ganz = app_quelle.lesen(WEB)
    ende = ganz.rindex("</script>")
    davor = ganz[:ende].rstrip("\r\n")
    assert davor.endswith("\ninit();"), davor[-80:]


@geteilt
def test_teile_direkt_hintereinander_start_zuletzt():
    zeilen = _index().splitlines()
    for art, letzte, danach in (("js", "js/start.js", None), ("css", "css/tablet.css", '<style id="festStil"></style>')):
        stellen = [i for i, z in enumerate(zeilen) if app_quelle._teil(z) and app_quelle._teil(z)[0] == art]
        assert stellen == list(range(stellen[0], stellen[0] + len(stellen))), art
        assert app_quelle._teil(zeilen[stellen[-1]])[1] == letzte
        if danach:
            assert zeilen[stellen[-1] + 1] == danach
    start = _lesen(os.path.join(WEB, "js", "start.js")).rstrip("\r\n")
    assert start.endswith("\ninit();")
    erstes_js = [i for i, z in enumerate(zeilen) if z.startswith('<script src="js/')][0]
    assert zeilen[erstes_js - 1] == "</script>"     # der Bauwerte-Block


# ---------------------------------------------------------------------------
# 4. Syntax: zusammen und jede Datei fuer sich (G4)
# ---------------------------------------------------------------------------
def test_zusammen_ohne_syntaxfehler(tmp_path):
    """Alle Inline-Skripte zusammen, in Ladereihenfolge. Fangt doppelte
    let/const ueber Skripte hinweg ab: in der App liesse so eine Dopplung
    das ganze zweite Skript still ausfallen."""
    ganz = app_quelle.lesen(WEB)
    skripte = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", ganz, re.S)
    assert len(skripte) >= 3
    code, ausgabe = _node_check("\n;\n".join(skripte), tmp_path)
    assert code == 0, ausgabe


@geteilt
def test_jede_datei_fuer_sich_ohne_syntaxfehler(tmp_path):
    """Ein Teil, der allein nicht parst (offene Klammer, Kommentar ueber die
    Grenze), faellt im zusammengesetzten Text nicht auf - im Browser aber
    ganz aus (G4)."""
    for teil in _js_teile():
        code, ausgabe = _node_check(_lesen(os.path.join(WEB, teil)), tmp_path, teil.replace("/", "_"))
        assert code == 0, (teil, ausgabe)


def test_keine_funktion_doppelt():
    """Eine zweite function gleichen Namens ist kein Syntaxfehler: sie
    ueberschreibt die erste still - ueber zwei Skripte hinweg genauso."""
    funktion = re.compile(r"^(?:async )?function\s*\*?\s*([A-Za-z_$][\w$]*)", re.M)
    wo = collections.defaultdict(list)
    for teil in ["index.html"] + _js_teile():
        for name in funktion.findall(_lesen(os.path.join(WEB, teil))):
            wo[name].append(teil)
    doppelt = {n: w for n, w in wo.items() if len(w) > 1}
    assert not doppelt, doppelt
    assert len(wo) > 500     # heute rund 600; nicht still leer


# ---------------------------------------------------------------------------
# 5. Werkzeuge sehen die ganze App (texte_pruefen, Zeilenenden)
# ---------------------------------------------------------------------------
def test_texte_pruefen_sieht_alle_teile():
    """texte_pruefen.py laeuft in jedem Bau. Liest es nur index.html, findet
    es nach der Aufteilung still 84 statt 443 Schluessel und meldet trotzdem
    "keine fehlenden Texte" (Aufgabe B, 20.11.2026)."""
    import texte_pruefen
    alle = texte_pruefen.verlangte_schluessel(texte_pruefen.app_text())
    je_datei = set()
    for teil in app_quelle.dateien(WEB):
        je_datei |= set(texte_pruefen.verlangte_schluessel(_lesen(os.path.join(WEB, teil))))
    assert set(alle) == je_datei
    assert len(alle) > 400, len(alle)     # heute rund 450 (data-t, t(), tp())


def test_zeilenenden_einheitlich():
    """Alle Dateien der App mit denselben Zeilenenden wie index.html - CRLF
    in der Windows-Arbeitskopie, LF in CI. Gemischt hiesse: ein Werkzeug hat
    eine Datei mit anderen Zeilenenden geschrieben."""
    def art(text):
        crlf, lf = text.count("\r\n"), text.count("\n")
        assert crlf in (0, lf), "gemischte Zeilenenden"
        return "crlf" if crlf else "lf"
    soll = art(_index())
    for teil in app_quelle.dateien(WEB):
        assert art(_lesen(os.path.join(WEB, teil))) == soll, teil


# ---------------------------------------------------------------------------
# 6. Adressen im Stil (G1)
# ---------------------------------------------------------------------------
def _relativ(adresse):
    return adresse and not adresse.startswith(("#", "data:", "http:", "https:", "/"))


def test_stil_adressen_hin_und_zurueck():
    """In einer Datei unter css/ loest url(symbole/x.webp) gegen css/ auf
    (404, gemessen in Chrome und WebKit). Der Schnitt setzt darum ../ davor,
    app_quelle.lesen() nimmt es zurueck; das muss genau umkehrbar sein."""
    stil = _stil(app_quelle.lesen(WEB))
    assert "url(../" not in stil and "url('../" not in stil and 'url("../' not in stil
    assert app_quelle.css_zurueck(app_quelle.css_hin(stil)) == stil
    hin = app_quelle.css_hin(stil)
    for m in URL.finditer(stil):
        if _relativ(m.group(2)):
            assert os.path.isfile(os.path.join(WEB, m.group(2))), m.group(0)
    for m in URL.finditer(hin):
        if _relativ(m.group(2)):
            assert m.group(2).startswith("../"), m.group(0)
    assert "url(#sternGold)" in hin


@geteilt
def test_stil_adressen_aus_css_gesehen():
    for teil in [t for t in TEILE if t.startswith("css/")]:
        for m in URL.finditer(_lesen(os.path.join(WEB, teil))):
            if _relativ(m.group(2)):
                ziel = os.path.normpath(os.path.join(WEB, "css", m.group(2)))
                assert os.path.isfile(ziel), (teil, m.group(0))


# ---------------------------------------------------------------------------
# 7. app_quelle selbst, an einer kleinen geteilten Probe
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("nl", ["\r\n", "\n"])
def test_app_quelle_setzt_byte_genau_zusammen(tmp_path, nl):
    zeilen = ["<!doctype html>", "<html><head>", '<link href="schriften.css" rel="stylesheet">',
              '<script src="lottie.min.js"></script>', "<style>",
              "  /* ---------- A */", "  .a{background:url(symbole/x.webp)}",
              "  /* ---------- B */", "  .b{fill:url(#sternGold)} .c{background:url('flamme/aus.webp')}",
              "</style>", '<style id="festStil"></style>', "</head><body>", "<p>Markup</p>",
              "<script>", "/* Bauwerte (Probe) */", "const X = 1;", "</script>",
              "<script>", "/* eins */", "let a = X;", "/* ---- zwei */", "function f(){ return a; }",
              "init();", "</script>", "</body></html>", ""]
    alt = nl.join(zeilen)
    web = tmp_path / "web"
    (web / "css").mkdir(parents=True)
    (web / "js").mkdir()

    def schreiben(name, text):
        (web / name).write_bytes(text.encode("utf-8"))

    schreiben("index.html", alt)
    assert app_quelle.lesen(str(web)) == alt                    # ungeteilt: unveraendert
    assert app_quelle.dateien(str(web)) == ["index.html"]
    schreiben("css/a.css", app_quelle.css_hin(nl.join(zeilen[5:7]) + nl))
    schreiben("css/b.css", app_quelle.css_hin(nl.join(zeilen[7:9]) + nl))
    schreiben("js/eins.js", nl.join(zeilen[18:20]) + nl)
    schreiben("js/zwei.js", nl.join(zeilen[20:23]) + nl)
    neu = (zeilen[:4] + ['<link rel="stylesheet" href="css/a.css">', '<link rel="stylesheet" href="css/b.css">']
           + zeilen[10:17] + ['<script src="js/eins.js"></script>', '<script src="js/zwei.js"></script>']
           + zeilen[24:])
    schreiben("index.html", nl.join(neu))
    assert "url(../symbole/x.webp)" in (web / "css" / "a.css").read_text(encoding="utf-8")
    assert app_quelle.lesen(str(web)).encode("utf-8") == alt.encode("utf-8")
    assert app_quelle.dateien(str(web)) == ["index.html", "css/a.css", "css/b.css", "js/eins.js", "js/zwei.js"]
    assert app_quelle.bauwerte(app_quelle.lesen(str(web))) == "/* Bauwerte (Probe) */" + nl + "const X = 1;" + nl


# ---------------------------------------------------------------------------
# 8. Die Server am PC (G6, PLAN 3.1)
# ---------------------------------------------------------------------------
def test_server_mit_langer_warteschlange():
    """Beim Start holt die App alle Teile fast gleichzeitig. Mit der
    Warteschlange 5 lehnte Windows Verbindungen ab (test_dateiserver.py vom
    22.10.2026), und ein abgelehntes Skript macht die App kaputt (G6)."""
    import start
    sys.path.insert(0, os.path.join(WURZEL, "store", "bilder_machen"))
    import bilder_playwright
    assert start.Server.request_queue_size >= 128
    assert bilder_playwright.Dateiserver.request_queue_size >= 128


def test_start_py_speichert_skripte_und_stil_nicht_zwischen():
    """Sonst saehe man am PC nach einer Aenderung in web/js den alten Code."""
    import start
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), start.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        basis = "http://127.0.0.1:%d" % srv.server_address[1]
        for pfad in ("/lottie.min.js", "/schriften.css"):
            with urllib.request.urlopen(basis + pfad) as r:
                assert r.headers.get("Cache-Control") == "no-store", pfad
    finally:
        srv.shutdown()
        srv.server_close()
