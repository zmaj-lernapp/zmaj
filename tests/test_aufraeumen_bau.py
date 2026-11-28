# -*- coding: utf-8 -*-
"""Aufraeumen im Bau (1.5, Optimierung Punkt 5, Ajdin am 20.11.2026: "und
räum auf"). Alles nur in der Kopie www/:

  - icon.ico kommt nicht mehr mit (die App laedt es nie);
  - die drei Standbilder des Drachen kommen als WebP statt PNG, bleiben aber
    der Rueckfall ohne lottie (zmaj() in drache.js);
  - audio/index.json hat nur noch die Felder, die die App liest, und das
    erst ganz am Ende des Baus - vorher braucht der Bau "stimme" und "text".
"""
import io
import json
import os
import re
import shutil

import pytest


def _app_bauen():
    import app_bauen
    return app_bauen


# ------------------------------------------------------------- icon.ico ---
def test_kopieren_laesst_icon_ico_weg(tmp_path, monkeypatch):
    app_bauen = _app_bauen()
    web = tmp_path / "web"
    (web / "maskottchen").mkdir(parents=True)
    for name in ("index.html", "icon.ico", "icon-256.png", "maskottchen/zmaj-frei.png"):
        (web / name).write_bytes(b"x")
    monkeypatch.setattr(app_bauen, "WEB", str(web))
    www = tmp_path / "huelle" / "www"
    www.parent.mkdir()
    assert app_bauen.kopieren(str(www)) == 3
    assert not (www / "icon.ico").exists()
    assert (www / "icon-256.png").is_file() and (www / "index.html").is_file()
    assert (www / "maskottchen" / "zmaj-frei.png").is_file()


def test_die_app_laedt_icon_ico_nie(wurzel):
    """Nur der PC-Server (start.py) und die Webseite (seite_bauen.py) brauchen
    es. In der App selbst steht es nirgends."""
    import app_quelle
    assert "icon.ico" not in app_quelle.lesen(os.path.join(wurzel, "web"))


# ------------------------------------------------------- Standbilder ---
def _ffmpeg():
    app_bauen = _app_bauen()
    f = app_bauen.ffmpeg_finden()
    if not f or not os.path.isfile(f):
        pytest.skip("kein ffmpeg auf diesem Rechner")
    return f


def _inhalt(code, text):
    """Eine kleine Inhaltsdatei in der Form von inhalt_bauen.py. web/inhalt/
    ist erzeugt und nicht im Git (auf GitHub laeuft pytest vor inhalt_bauen.py),
    darum legt der Test sie selbst an."""
    return json.dumps({
        "sektionen": [{"id": "a1", "titel": text}],
        "maskottchen": ["zmaj-frei.png", "zmaj-jubel.png", "zmaj-traurig.png", "zmaj.json",
                        "zmajz-fes.json", "zmajz-krone.json", "haut/gold/", "haut/skelett/"],
        "sprache": code,
        "texte": {"weiter": text},
    }, ensure_ascii=False, separators=(",", ":"))


def _www_mit_standbildern(tmp_path, wurzel):
    """Eine kleine Kopie: die drei echten Standbilder, zwei Inhaltsdateien und
    liste.json, wie kopieren() sie nach www/ legt."""
    www = tmp_path / "www"
    (www / "maskottchen").mkdir(parents=True)
    (www / "inhalt").mkdir()
    for n in ("zmaj-frei", "zmaj-jubel", "zmaj-traurig"):
        shutil.copyfile(os.path.join(wurzel, "web", "maskottchen", n + ".png"),
                        str(www / "maskottchen" / (n + ".png")))
    for code, text in (("de", "Weiter – Übung"), ("tr", "Devam – Alıştırma")):
        (www / "inhalt" / (code + ".json")).write_text(_inhalt(code, text), encoding="utf-8")
    (www / "inhalt" / "liste.json").write_text(json.dumps({
        "version": 1, "grundsprache": "de",
        "sprachen": [{"code": "de", "name": "Deutsch"}, {"code": "tr", "name": "Türkçe"}],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    return www


def test_standbilder_test_braucht_kein_erzeugtes_web_inhalt(tmp_path, wurzel, monkeypatch):
    """Auf GitHub gibt es web/inhalt/ beim Testlauf noch nicht. Die Kopie darf
    nichts daraus lesen."""
    import builtins
    offen, kopie = builtins.open, shutil.copyfile
    gesperrt = os.path.normcase(os.path.join(wurzel, "web", "inhalt"))

    def pruefen(pfad):
        if os.path.normcase(os.path.abspath(str(pfad))).startswith(gesperrt):
            raise FileNotFoundError(pfad)

    monkeypatch.setattr(builtins, "open", lambda p, *a, **k: (pruefen(p), offen(p, *a, **k))[1])
    monkeypatch.setattr(shutil, "copyfile", lambda q, z, *a, **k: (pruefen(q), kopie(q, z, *a, **k))[1])
    www = _www_mit_standbildern(tmp_path, wurzel)
    monkeypatch.undo()
    for code in ("de", "tr"):
        daten = json.load(io.open(str(www / "inhalt" / (code + ".json")), encoding="utf-8"))
        assert daten["maskottchen"][:3] == ["zmaj-frei.png", "zmaj-jubel.png", "zmaj-traurig.png"]
    assert "maskottchen" not in json.load(io.open(str(www / "inhalt" / "liste.json"), encoding="utf-8"))


def test_standbilder_werden_webp(tmp_path, wurzel):
    app_bauen = _app_bauen()
    _ffmpeg()
    www = _www_mit_standbildern(tmp_path, wurzel)
    vorher = {c: json.load(io.open(str(www / "inhalt" / (c + ".json")), encoding="utf-8")) for c in ("de", "tr")}
    liste = (www / "inhalt" / "liste.json").read_bytes()
    png = sum((www / "maskottchen" / (n + ".png")).stat().st_size for n in app_bauen.STANDBILDER)

    assert app_bauen.standbilder_als_webp(str(www)) == 3

    m = www / "maskottchen"
    assert sorted(os.listdir(str(m))) == ["zmaj-frei.webp", "zmaj-jubel.webp", "zmaj-traurig.webp"]
    webp = 0
    for n in app_bauen.STANDBILDER:
        daten = (m / (n + ".webp")).read_bytes()
        assert daten[:4] == b"RIFF" and daten[8:12] == b"WEBP", n
        # VP8X mit Alpha-Bit: der Drache bleibt freigestellt
        assert daten[12:16] == b"VP8X" and daten[20] & 0x10, n
        webp += len(daten)
    assert webp < png / 2, (webp, png)
    # In der Liste stehen die neuen Namen an derselben Stelle, sonst ist alles gleich.
    for code, alt in vorher.items():
        pfad = www / "inhalt" / (code + ".json")
        neu = json.load(io.open(str(pfad), encoding="utf-8"))
        assert neu["maskottchen"] == [re.sub(r"^(zmaj-(frei|jubel|traurig))\.png$", r"\1.webp", d)
                                      for d in alt["maskottchen"]]
        assert "zmaj-frei.webp" in neu["maskottchen"] and "zmaj-frei.png" not in neu["maskottchen"]
        assert {k: v for k, v in neu.items() if k != "maskottchen"} == \
               {k: v for k, v in alt.items() if k != "maskottchen"}
        # dieselbe Form wie inhalt_bauen.py
        assert pfad.read_text(encoding="utf-8") == json.dumps(neu, ensure_ascii=False, separators=(",", ":"))
    assert (www / "inhalt" / "liste.json").read_bytes() == liste


def test_standbilder_ohne_ffmpeg_bleiben_png(tmp_path, wurzel, monkeypatch):
    app_bauen = _app_bauen()
    www = _www_mit_standbildern(tmp_path, wurzel)
    vorher = {p: p.read_bytes() for p in www.rglob("*") if p.is_file()}
    monkeypatch.setattr(app_bauen, "ffmpeg_finden", lambda: None)
    assert app_bauen.standbilder_als_webp(str(www)) == 0
    assert {p: p.read_bytes() for p in www.rglob("*") if p.is_file()} == vorher


def test_standbilder_scheitert_eins_bleiben_alle_png(tmp_path, wurzel):
    """Kann ffmpeg kein WebP (etwa ohne libwebp), bleibt der ganze Satz PNG
    und die Liste unveraendert - nie ein halb umgestellter Satz."""
    app_bauen = _app_bauen()
    _ffmpeg()
    www = _www_mit_standbildern(tmp_path, wurzel)
    (www / "maskottchen" / "zmaj-traurig.png").write_bytes(b"kein Bild")
    vorher = {p: p.read_bytes() for p in www.rglob("*") if p.is_file()}
    assert app_bauen.standbilder_als_webp(str(www)) == 0
    assert {p: p.read_bytes() for p in www.rglob("*") if p.is_file()} == vorher


def test_standbilder_nie_in_web(wurzel):
    app_bauen = _app_bauen()
    with pytest.raises(SystemExit):
        app_bauen.standbilder_als_webp(os.path.join(wurzel, "web"))
    for n in app_bauen.STANDBILDER:
        assert os.path.isfile(os.path.join(wurzel, "web", "maskottchen", n + ".png"))
        assert not os.path.exists(os.path.join(wurzel, "web", "maskottchen", n + ".webp"))


def test_standbilder_mit_den_schaltern_der_drachenbilder():
    import haut_einbauen
    assert _app_bauen().STANDBILD_WEBP == haut_einbauen.WEBP


def test_drache_nimmt_erst_webp_dann_png(wurzel):
    """zmaj() in drache.js: je Standbild erst .webp (App), dann .png (web/)."""
    with io.open(os.path.join(wurzel, "web", "js", "drache.js"), encoding="utf-8") as f:
        js = f.read()
    rumpf = js[js.index("function zmaj(mood='happy'){"):]
    rumpf = rumpf[:rumpf.index("\n}")]
    assert "[...want, 'zmaj-frei', 'zmaj'].flatMap(n => [n + '.webp', n + '.png'])" in rumpf
    assert ".png'" not in rumpf.replace("n + '.png'", "")


# --------------------------------------------------- audio/index.json ---
def _wie_die_app(index):
    """ladeAudio() in inhalt.js: AUDIO und WORTZEITEN."""
    toene = index.get("toene") or []
    audio = {str(e["key"]).lower(): e["datei"] for e in toene}
    zeiten = {e["datei"]: e["w"] for e in toene if e and e.get("datei") and isinstance(e.get("w"), list)}
    return audio, zeiten


def test_die_app_liest_nur_key_datei_und_w(wurzel):
    """Steht hier eines Tages ein weiteres Feld, muss es in TON_FELDER."""
    with io.open(os.path.join(wurzel, "web", "js", "inhalt.js"), encoding="utf-8") as f:
        js = f.read()
    rumpf = js[js.index("async function ladeAudio(){"):]
    rumpf = rumpf[:rumpf.index("\n}")]
    assert set(re.findall(r"\be\.(\w+)", rumpf)) == set(_app_bauen().TON_FELDER)
    # und sonst laedt niemand in der App die Datei
    import app_quelle
    app = app_quelle.lesen(os.path.join(wurzel, "web"))
    assert len(re.findall(r"""fetch\(\s*['"`][^'"`]*index\.json""", app)) == 1
    assert "fetch('audio/index.json'" in rumpf


def test_index_verschlanken_mit_dem_echten_index(tmp_path, wurzel):
    """Mit dem echten web/audio/index.json: die App findet danach jeden Ton
    und jede Wortzeit genau wie vorher, die Datei ist kleiner."""
    app_bauen = _app_bauen()
    audio = tmp_path / "www" / "audio"
    audio.mkdir(parents=True)
    shutil.copyfile(os.path.join(wurzel, "web", "audio", "index.json"), str(audio / "index.json"))
    voll = json.load(io.open(str(audio / "index.json"), encoding="utf-8"))
    assert any("w" in e for e in voll["toene"]) and all("stimme" in e for e in voll["toene"])

    vorher, nachher = app_bauen.ton_index_verschlanken(str(audio))

    roh = (audio / "index.json").read_text(encoding="utf-8")
    schlank = json.loads(roh)
    assert _wie_die_app(schlank) == _wie_die_app(voll)
    assert schlank["version"] == voll["version"] and len(schlank["toene"]) == len(voll["toene"])
    assert {k for e in schlank["toene"] for k in e} == {"key", "datei", "w"}
    assert nachher == len(roh.encode("utf-8")) and nachher < vorher / 2, (vorher, nachher)
    assert "\n" not in roh


def test_index_verschlanken_auf_ios_behaelt_stimme(tmp_path):
    """ios/store_helfer.py der iOS-Huelle zaehlt im fertigen Paket die
    Eintraege mit "stimme": "emir"."""
    app_bauen = _app_bauen()
    audio = tmp_path / "audio"
    audio.mkdir()
    toene = [{"key": "Jedan", "datei": "w0001.m4a", "text": "Jedan", "stimme": "emir"},
             {"key": "g01", "datei": "g01.m4a", "text": "G", "stimme": "bs-BA-VesnaNeural", "w": [[1, 2]]}]
    (audio / "index.json").write_text(json.dumps({"version": 1, "toene": toene}), encoding="utf-8")
    app_bauen.ton_index_verschlanken(str(audio), app_bauen.TON_FELDER_IOS)
    assert json.loads((audio / "index.json").read_text(encoding="utf-8")) == {"version": 1, "toene": [
        {"key": "Jedan", "datei": "w0001.m4a", "stimme": "emir"},
        {"key": "g01", "datei": "g01.m4a", "w": [[1, 2]], "stimme": "bs-BA-VesnaNeural"}]}


@pytest.mark.parametrize("kaputt", [{"datei": "w0001.ogg"}, {"key": "a"}, "w0001.ogg"])
def test_index_verschlanken_bricht_bei_kaputtem_eintrag_ab(tmp_path, kaputt):
    app_bauen = _app_bauen()
    audio = tmp_path / "audio"
    audio.mkdir()
    roh = json.dumps({"version": 1, "toene": [{"key": "b", "datei": "w0002.ogg", "text": "b"}, kaputt]})
    (audio / "index.json").write_text(roh, encoding="utf-8")
    with pytest.raises(SystemExit):
        app_bauen.ton_index_verschlanken(str(audio))
    assert (audio / "index.json").read_text(encoding="utf-8") == roh


def test_index_verschlanken_nie_in_web(wurzel):
    app_bauen = _app_bauen()
    pfad = os.path.join(wurzel, "web", "audio", "index.json")
    vorher = os.path.getsize(pfad)
    with pytest.raises(SystemExit):
        app_bauen.ton_index_verschlanken(os.path.join(wurzel, "web", "audio"))
    assert os.path.getsize(pfad) == vorher


# ------------------------------------------------------- Reihenfolge ---
ANDROID_SCHRITTE = ("anmeldung_pruefen", "versionsname_lesen", "pruefen", "kopieren", "emir_drueber",
                    "dauer_einsetzen", "cloud_einsetzen", "version_einsetzen", "ton_verkleinern",
                    "testwerbung_einschalten", "immer_packen_einschalten", "standbilder_als_webp",
                    "ton_index_verschlanken", "versionsnummer_hochzaehlen", "capacitor", "plugins_flicken",
                    "debug_apk", "freigabe_aab", "versionsname_anheben")


@pytest.mark.parametrize("argv", [[], ["--nur-abgleich", "--testwerbung"], ["--aab", "--testwerbung"],
                                  ["--immer-packen"]])
def test_verschlanken_ist_der_letzte_schritt_an_www(monkeypatch, argv):
    """Nach allem, was www/ anfasst (emir_drueber setzt "stimme" und zaehlt
    damit, ton_verkleinern schreibt die Endungen um) und vor capacitor(), das
    www/ ins Paket traegt."""
    app_bauen = _app_bauen()
    aufrufe = []
    for name in ANDROID_SCHRITTE:
        monkeypatch.setattr(app_bauen, name, lambda *a, n=name, **k: aufrufe.append((n, a, k)))
    app_bauen.main(argv)
    namen = [a[0] for a in aufrufe]
    an_www = ["kopieren", "emir_drueber", "dauer_einsetzen", "cloud_einsetzen", "version_einsetzen",
              "ton_verkleinern", "testwerbung_einschalten", "immer_packen_einschalten"]
    letzter = max(namen.index(n) for n in an_www if n in namen)
    assert letzter < namen.index("standbilder_als_webp") < namen.index("ton_index_verschlanken") \
        < namen.index("capacitor")
    # Android: Standard-www und nur key, datei, w
    assert aufrufe[namen.index("ton_index_verschlanken")][1:] == ((), {})
    assert app_bauen.TON_FELDER == ("key", "datei", "w")
