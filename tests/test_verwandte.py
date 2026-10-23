# -*- coding: utf-8 -*-
"""Verwandte im Level Familie (23.10.2026).

Ajdin: "tetka ujna strina fuer die verschiedenen tanten und striko ujak
amidza=stric tetak daidza=ujak usw". Tanten und Onkel nach ihrer Seite,
Cousins, Neffe und Nichte, siehe WORTSCHATZ_KORREKTUREN.md. Emir spricht die
neuen Woerter; ihre Aufnahmen liegen nur in der Huelle, die Nummern stehen
in ton_nur_emir.json.
"""
import io
import json
import os
import re

import pytest

NEU = [
    ("Onkel (Bruder des Vaters)", "amidža / stric"),
    ("Onkel (Bruder der Mutter)", "daidža / ujak"),
    ("Onkel (Mann der Tante)", "tetak"),
    ("Tante (Schwester von Vater oder Mutter)", "tetka"),
    ("Tante (Frau des Onkels väterlicherseits)", "strina / amidžinica"),
    ("Tante (Frau des Onkels mütterlicherseits)", "ujna / daidžinica"),
    ("Cousin (Sohn des Onkels väterlicherseits)", "amidžić / brat od amidže"),
    ("Cousine (Tochter des Onkels väterlicherseits)", "amidžična / sestra od amidže"),
    ("Cousin (Sohn des Onkels mütterlicherseits)", "daidžić / brat od daidže"),
    ("Cousine (Tochter des Onkels mütterlicherseits)", "daidžična / sestra od daidže"),
    ("Cousin (Sohn der Tante)", "tetić / brat od tetke"),
    ("Cousine (Tochter der Tante)", "tetična / sestra od tetke"),
    ("Cousin, Verwandter (allgemein)", "rođak"),
    ("Cousine, Verwandte (allgemein)", "rođaka / rođakinja"),
    ("Neffe", "nećak"),
    ("Nichte", "nećakinja"),
]
KOSEFORMEN = {"amidža / stric": ["striko", "adžo"], "daidža / ujak": ["ujo", "dajo"]}
UMBENANNT = {
    "tante:tetka": "tante (schwester von vater oder mutter):tetka",
    "onkel (vaterseite):amidža": "onkel (bruder des vaters):amidža / stric",
    "onkel (mutterseite):daidža": "onkel (bruder der mutter):daidža / ujak",
    "cousin:rođak": "cousin, verwandter (allgemein):rođak",
}


def _familie(daten):
    return next(k for k in daten["kategorien"] if k["id"] == "familie")


def test_familie_hat_alle_verwandten(grunddaten):
    paare = [(w["de"], w["bs"]) for w in _familie(grunddaten)["words"]]
    for p in NEU:
        assert p in paare, p
    assert len(paare) == 34


def test_koseformen_sind_keine_lernwoerter(grunddaten):
    woerter = {w["bs"]: w for w in _familie(grunddaten)["words"]}
    for bs, formen in KOSEFORMEN.items():
        assert woerter[bs].get("auch") == formen, bs
    alle = {f for k in grunddaten["kategorien"] for w in k["words"] for f in w["bs"].split(" / ")}
    for f in sum(KOSEFORMEN.values(), []):
        assert f not in alle, f


def test_koseformen_werden_nie_gesprochen(grunddaten):
    """Frueher sprach Emir ein "(auch: ...)" mit - als deutsches "auch".
    Gesprochen wird genau das, was ton_bauen.py aus "bs" macht."""
    import ton_bauen
    verboten = set(sum(KOSEFORMEN.values(), [])) | {"auch"}
    familie = {w["bs"] for w in _familie(grunddaten)["words"]}
    texte = [ton_bauen.sprechtext_alle(p["text"]) if p.get("alle") else ton_bauen.sprechtext(p["text"])
             for p in ton_bauen.sammle() if p["text"] in familie or "pčelar" in p["text"]]
    assert len(texte) >= 34
    for t in texte:
        assert not set(re.findall(r"\w+", t.lower())) & verboten, t


def test_luecke_nimmt_stric_und_die_koseformen(grunddaten):
    s = next(x for x in grunddaten["saetze"] if x["text"] == "Moj ___ je pčelar.")
    assert s["answer"] == "amidža"
    assert s["auch"] == ["stric", "striko", "adžo"]
    assert s["de"] == "Mein Onkel (Bruder des Vaters) ist Imker."


def test_keine_mehrdeutigen_cousin_woerter(grunddaten):
    """bratić, sestrična und bratučed heissen je nach Gegend Cousin oder
    Neffe/Nichte - bewusst nicht im Kurs, weder als Wort noch als "auch",
    in einem Satz oder in einer Geschichte (Ajdin am 23.10.2026)."""
    verboten = {"bratić", "sestrična", "bratučed"}
    texte = []
    for k in grunddaten["kategorien"]:
        for w in k["words"]:
            texte += [w["bs"]] + list(w.get("auch", []))
    for s in grunddaten["saetze"]:
        texte += [s["text"], s["answer"]] + list(s.get("auch", []))
    for s in grunddaten.get("satzbau", []):
        texte += [s["bs"]] + list(s.get("auch", []))
    texte += [g.get("text", "") for g in grunddaten["geschichten"]]
    assert len(texte) > 2000
    for t in texte:
        woerter = set(re.findall(r"\w+", str(t).lower()))
        assert not woerter & verboten, t


def test_auch_bei_luecken_ist_sauber(grunddaten):
    """"auch" am Lueckensatz (seit 23.10.2026): weitere richtige Antworten.
    Gezeigt und gesprochen wird weiter "answer"."""
    for s in grunddaten["saetze"]:
        if "auch" not in s:
            continue
        assert isinstance(s["auch"], list) and s["auch"], s["text"]
        for a in s["auch"]:
            assert isinstance(a, str) and a and a == a.strip(), (s["text"], a)
            assert " / " not in a and "___" not in a and a != s["answer"], (s["text"], a)


def test_alte_kennungen_wandern_mit(grunddaten, index_html):
    ids = {w["id"] for k in grunddaten["kategorien"] for w in k["words"]}
    for alt, neu in UMBENANNT.items():
        assert alt not in ids and neu in ids, alt
        assert "'%s': '%s'" % (alt, neu) in index_html, alt


def test_jede_sprache_unterscheidet_die_verwandten(alle_daten, grunddaten):
    """Zwei Verwandte mit derselben Uebersetzung waeren in der Auswahl
    nicht zu unterscheiden (doppelte_bedeutung.py)."""
    neu = {de for de, _ in NEU}
    stellen = [i for i, w in enumerate(_familie(grunddaten)["words"]) if w["de"] in neu]
    for code, daten in alle_daten.items():
        woerter = _familie(daten)["words"]
        bedeutungen = [w["de"].strip().lower() for w in woerter]
        for i in stellen:
            assert bedeutungen.count(bedeutungen[i]) == 1, (code, woerter[i]["de"])


# ---------------------------------------------------- Aufnahmen nur von Emir ---
def test_ton_nur_emir_ist_stimmig(wurzel):
    import ton_bauen
    import ton_pruefen
    index = json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8"))
    emir = ton_bauen.nur_emir()
    assert ton_pruefen.nur_emir_pruefen(emir, index["toene"]) == []
    assert set(emir) <= {p["key"] for p in ton_bauen.sammle()}


def _schreibe(pfad, daten):
    io.open(str(pfad), "w", encoding="utf-8").write(json.dumps(daten))


def test_grosser_lauf_laesst_emir_aus_und_vergibt_danach(tmp_path, monkeypatch):
    """Ohne die Nummern aus ton_nur_emir.json bekaeme "tri" w0002 - unter
    der in audio_emir/ schon "dva" liegt."""
    import ton_bauen
    audio = tmp_path / "audio"
    audio.mkdir()
    (audio / "w0001.mp3").write_bytes(b"x" * 900)
    _schreibe(audio / "index.json", {"version": 1, "toene": [
        {"key": "jedan", "datei": "w0001.mp3", "text": "jedan", "stimme": "s"}]})
    _schreibe(tmp_path / "ton_nur_emir.json", {"version": 1, "toene": [
        {"key": "dva", "datei": "w0002.mp3", "text": "dva"}]})
    monkeypatch.setattr(ton_bauen, "AUDIO", str(audio))
    monkeypatch.setattr(ton_bauen, "INDEX", str(audio / "index.json"))
    monkeypatch.setattr(ton_bauen, "NUR_EMIR", str(tmp_path / "ton_nur_emir.json"))
    monkeypatch.setattr(ton_bauen, "sammle", lambda: [
        {"art": "wort", "key": k, "text": k} for k in ("jedan", "dva", "tri")])
    monkeypatch.setattr(ton_bauen.time, "sleep", lambda s: None)
    gesprochen = []
    monkeypatch.setattr(ton_bauen, "hole", lambda d, z, text, s, l: gesprochen.append(text) or b"y" * 900)
    ton_bauen.grosser_lauf(None, {}, "s", "s")
    assert gesprochen == ["tri"]
    neu = json.load(io.open(str(audio / "index.json"), encoding="utf-8"))
    assert {e["key"]: e["datei"] for e in neu["toene"]} == {"jedan": "w0001.mp3", "tri": "w0003.mp3"}
    assert not (audio / "w0002.mp3").exists()


def test_emir_drueber_legt_die_emir_woerter_dazu(tmp_path, monkeypatch):
    import app_bauen
    import ton_bauen
    audio = tmp_path / "www" / "audio"
    audio.mkdir(parents=True)
    emir = tmp_path / "audio_emir"
    emir.mkdir()
    (audio / "w0001.mp3").write_bytes(b"a" * 900)
    _schreibe(audio / "index.json", {"version": 1, "toene": [
        {"key": "jedan", "datei": "w0001.mp3", "text": "jedan", "stimme": "bs-BA-GoranNeural"}]})
    (emir / "w0001.mp3").write_bytes(b"e" * 900)
    (emir / "w0002.mp3").write_bytes(b"f" * 900)
    nur = tmp_path / "ton_nur_emir.json"
    _schreibe(nur, {"version": 1, "toene": [{"key": "dva", "datei": "w0002.mp3", "text": "dva"}]})
    monkeypatch.setattr(app_bauen, "WWW", str(tmp_path / "www"))
    monkeypatch.setattr(app_bauen, "EMIR", str(emir))
    monkeypatch.setattr(ton_bauen, "NUR_EMIR", str(nur))
    assert app_bauen.emir_drueber() == 2
    idx = json.load(io.open(str(audio / "index.json"), encoding="utf-8"))
    assert {e["key"]: (e["datei"], e.get("stimme")) for e in idx["toene"]} == {
        "jedan": ("w0001.mp3", "emir"), "dva": ("w0002.mp3", "emir")}
    assert (audio / "w0002.mp3").read_bytes() == b"f" * 900
    # Nummer schon vergeben: lieber kein Paket als das falsche Wort
    _schreibe(nur, {"version": 1, "toene": [{"key": "tri", "datei": "w0001.mp3", "text": "tri"}]})
    with pytest.raises(SystemExit):
        app_bauen.emir_drueber()
    # Datei fehlt in audio_emir/: ebenso
    _schreibe(nur, {"version": 1, "toene": [{"key": "tri", "datei": "w0009.mp3", "text": "tri"}]})
    with pytest.raises(SystemExit):
        app_bauen.emir_drueber()


def test_ton_pruefen_kennt_die_emir_regeln(tmp_path):
    import ton_pruefen
    web = tmp_path / "web_audio"
    web.mkdir()
    huelle = tmp_path / "audio_emir"
    huelle.mkdir()
    emir = {"dva": {"key": "dva", "datei": "w0002.mp3", "text": "dva"}}
    f = ton_pruefen.nur_emir_pruefen(emir, [], audio=str(web), huelle_audio=str(huelle))
    assert len(f) == 1 and "fehlt in der Hülle" in f[0], f
    (huelle / "w0002.mp3").write_bytes(b"x" * 900)
    assert ton_pruefen.nur_emir_pruefen(emir, [], audio=str(web), huelle_audio=str(huelle)) == []
    assert ton_pruefen.nur_emir_pruefen(emir, [], audio=str(web)) == []     # ohne Huelle
    (web / "w0002.mp3").write_bytes(b"x" * 900)
    f = ton_pruefen.nur_emir_pruefen(emir, [{"key": "dva", "datei": "w0002.mp3"}], audio=str(web))
    assert any("öffentliche" in x for x in f) and any("vergeben" in x for x in f), f
    assert any("index.json und" in x for x in f), f
    f = ton_pruefen.nur_emir_pruefen({"Dva": {"key": "Dva", "datei": "w0003.mp3", "text": "dva"}}, [],
                                     audio=str(web))
    assert any("Schlüssel" in x for x in f), f
    f = ton_pruefen.nur_emir_pruefen({"x": {"key": "x", "datei": "x.mp3", "text": "x"}}, [], audio=str(web))
    assert any("w0001.mp3" in x for x in f), f
