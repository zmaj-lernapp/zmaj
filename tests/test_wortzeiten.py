# -*- coding: utf-8 -*-
"""Die Wortzeiten der Geschichten (Feld "w" in web/audio/index.json).

Beim Vorlesen markiert die App das Wort, das gerade gesprochen wird. Dafuer
braucht jede Geschichte genau ein Paar [start_ms, ende_ms] je Wort, das die
App antippbar anzeigt. Ein Paar zu viel oder zu wenig, und ab dieser Stelle
leuchtet immer das falsche Wort. Seit 20.10.2026, siehe wortzeiten_holen.py.
"""
import io
import json
import os

import pytest

import offen_b1_teil2
import ton_bauen
import wortzeiten_holen as wz


@pytest.fixture(scope="module")
def index(wurzel):
    return json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8"))


def _geschichten():
    import geschichten
    return geschichten.GESCHICHTEN


# Geschichten, deren Aufnahme noch fehlt, siehe tests/offen_b1_teil2.py. Vom
# 13.11.2026 an die B1-Lesetexte der Pakete 3 und 4, seit dem 16.11.2026 liest
# Vesna alle Geschichten vor (Offen-Liste 6) und die Menge ist leer.
WARTET_AUF_TON = offen_b1_teil2.GESCHICHTEN


def test_wartet_auf_ton_ist_aktuell(index):
    ids = {s["id"] for s in _geschichten()}
    assert WARTET_AUF_TON <= ids, sorted(WARTET_AUF_TON - ids)
    keys = {e["key"] for e in index["toene"]}
    fertig = sorted(s["id"] for s in _geschichten()
                    if s["id"] in WARTET_AUF_TON and ton_bauen.schluessel(s["text"]) in keys)
    assert not fertig, "Aufnahme ist da - bitte aus tests/offen_b1_teil2.py streichen: %s" % fertig


def test_jede_geschichte_hat_passende_wortzeiten(index):
    import offen_lesetexte
    nach_key = {e["key"]: e for e in index["toene"]}
    fehler = []
    for s in _geschichten():
        k = ton_bauen.schluessel(s["text"])
        # Geschichten ohne Ton: Pakete 1 und 2 in tests/offen_lesetexte.json,
        # Pakete 3 und 4 in tests/offen_b1_teil2.py (13.11.2026, seit 16.11.2026 leer)
        if k in offen_lesetexte.GESCHICHTEN or s["id"] in WARTET_AUF_TON:
            continue
        e = nach_key[k]
        w = e.get("w")
        if not isinstance(w, list):
            fehler.append("%s: kein w" % e["datei"])
            continue
        woerter = ton_bauen.textwoerter(s["text"])
        if len(w) != len(woerter):
            fehler.append("%s: %d Paare, %d Woerter" % (e["datei"], len(w), len(woerter)))
        vorher = 0
        for i, paar in enumerate(w):
            ok = (isinstance(paar, list) and len(paar) == 2
                  and all(isinstance(x, int) and not isinstance(x, bool) for x in paar))
            if not ok:
                fehler.append("%s: Paar %d %r" % (e["datei"], i, paar))
                continue
            if paar[0] > paar[1]:
                fehler.append("%s: Paar %d start > ende" % (e["datei"], i))
            if paar[0] < vorher:
                fehler.append("%s: Paar %d nicht monoton" % (e["datei"], i))
            vorher = paar[1]
    assert not fehler, fehler[:20]


def test_wortzeiten_gehoeren_zum_text(index):
    """Die Zeiten "w" wurden genau zu diesem Text geholt (wortzeiten_passen()
    vergleicht mit Gross- und Kleinschreibung, 20.10.2026). Sonst wirft der
    naechste ton_bauen.py-Lauf sie weg. Ausgenommen ist nur, was in
    WORTZEITEN_NEU (tests/offen_b1_teil2.py) auf die naechste Vesna-Runde wartet."""
    import offen_lesetexte
    nach_key = {e["key"]: e for e in index["toene"]}
    falsch = sorted(s["id"] for s in _geschichten()
                    if ton_bauen.schluessel(s["text"]) not in offen_lesetexte.GESCHICHTEN
                    and s["id"] not in WARTET_AUF_TON
                    and s["id"] not in offen_b1_teil2.WORTZEITEN_NEU
                    and not ton_bauen.wortzeiten_passen(nach_key[ton_bauen.schluessel(s["text"])], s["text"]))
    assert falsch == []


def test_wortzeiten_neu_ist_aktuell(index):
    """Was in WORTZEITEN_NEU steht: gleicher Schluessel, gleich viele Woerter,
    die App markiert weiter richtig. Nur der Text, zu dem die Zeiten geholt
    wurden, unterscheidet sich in Gross und klein, und wortzeiten_holen.py
    --holen nimmt die Geschichte deshalb von selbst mit (_ziele(): alles,
    wofuer wortzeiten_passen() nicht gilt). Passen die Zeiten wieder, aus
    WORTZEITEN_NEU streichen. Bis zum 15.11.2026 opcina ("Hvala vam"), seit
    "Hvala Vam" wieder dasteht, ist die Liste leer."""
    nach_key = {e["key"]: e for e in index["toene"]}
    ids = {s["id"] for s in _geschichten()}
    assert offen_b1_teil2.WORTZEITEN_NEU <= ids
    assert not offen_b1_teil2.WORTZEITEN_NEU & WARTET_AUF_TON
    for s in _geschichten():
        if s["id"] not in offen_b1_teil2.WORTZEITEN_NEU:
            continue
        e = nach_key[ton_bauen.schluessel(s["text"])]
        assert not ton_bauen.wortzeiten_passen(e, s["text"]), \
            "Wortzeiten passen wieder - aus WORTZEITEN_NEU streichen: %s" % s["id"]
        assert e["text"] != s["text"] and e["text"].lower() == s["text"].lower(), s["id"]
        assert len(e["w"]) == len(ton_bauen.textwoerter(s["text"])), s["id"]


def test_wortzeiten_liegen_in_der_aufnahme(index, wurzel):
    """ton_bauen.py und wortzeiten_holen.py erzeugen MP3 mit festen 48 kbit/s,
    die Dauer ist also Groesse * 8 / 48. Wer eine Geschichte durch eine eigene
    Aufnahme ersetzt, muss ihr "w" loeschen (LIESMICH in web/audio)."""
    for e in index["toene"]:
        if "w" not in e:
            continue
        groesse = os.path.getsize(os.path.join(wurzel, "web", "audio", e["datei"]))
        dauer_ms = groesse * 8 / 48.0
        assert e["w"][0][0] < 1000, e["datei"]
        assert e["w"][-1][1] <= dauer_ms + 100, (e["datei"], e["w"][-1], dauer_ms)


def test_wortbereiche_wie_die_app():
    """Dieselben Stuecke wie textwoerter() - und damit wie index.html."""
    texte = [s["text"] for s in _geschichten()] + [
        "Mira's pas - Rex.", "„Dobar dan“, kaže on: «da»", "é a-b -", "  x  ", ""]
    for t in texte:
        assert [t[a:b] for a, b in wz.wortbereiche(t)] == ton_bauen.textwoerter(t), t


def test_sprechtext_abbildung_rex():
    """sprechtext() macht aus "Rex" "Reks" - die Stellen muessen trotzdem stimmen."""
    t = "Pas se zove Rex. Rex je mali."
    sprech, zu = wz.sprech_abbildung(t)
    assert sprech == ton_bauen.sprechtext(t) == "Pas se zove Reks. Reks je mali."
    i = sprech.index("je")
    assert t[zu[i]:zu[i + 1] + 1] == "je"
    i = sprech.index("Reks")
    assert t[zu[i]:zu[i + 3] + 1] == "Rex"


def test_ssml_wie_bisher():
    """Die Geschichten wurden am 20.10.2026 mit genau diesem SSML neu gesprochen."""
    assert ton_bauen.ssml_normal("Dobar dan & više", "bs-BA-VesnaNeural", False) == (
        "<speak version='1.0' xml:lang='bs-BA'><voice name='bs-BA-VesnaNeural'>"
        "Dobar dan &amp; više</voice></speak>")
    assert ton_bauen.ssml_normal("kuća", "X", True) == (
        "<speak version='1.0' xml:lang='bs-BA'><voice name='X'>"
        "<prosody rate='-10%'>kuća</prosody></voice></speak>")


def test_zuordnen_teilt_fuellt_und_schiebt():
    t = "Ovo je Mira. Pas"
    #     0123456789012345
    ereignisse = [
        {"a": 0, "b": 6, "start": 100, "ende": 500},     # "Ovo je" in einem Ereignis
        {"a": 7, "b": 11, "start": 480, "ende": 900},    # beginnt vor dem Ende davor
    ]                                                    # "Pas" fehlt
    w, bericht = wz.zuordnen(t, ereignisse, dauer_ms=2000)
    assert len(w) == 4
    assert w[0] == [100, 340] and w[1] == [340, 500]     # nach Buchstaben 3:2
    assert w[2] == [500, 900]                            # auf 500 geschoben
    assert w[3] == [900, 2000]                           # bis zum Ende aufgefuellt
    assert bericht["interpoliert"] == ["Pas"]
    assert bericht["geteilt"] == ["Ovo", "je"]
    assert bericht["geschoben"] == 1
    assert wz.pruefe_w(w, t) == []


def test_schreibe_index_behaelt_w_in_einer_zeile(tmp_path, monkeypatch):
    monkeypatch.setattr(ton_bauen, "INDEX", str(tmp_path / "index.json"))
    bekannt = {"a": {"key": "a", "datei": "w0001.mp3", "text": "A", "stimme": "s"},
               "g": {"key": "g", "datei": "g01.mp3", "text": "G", "stimme": "s",
                     "w": [[0, 10], [12, 30]]}}
    ton_bauen._schreibe_index(bekannt)
    roh = (tmp_path / "index.json").read_text(encoding="utf-8")
    assert '   "w": [[0,10],[12,30]]' in roh.splitlines()
    zurueck = json.loads(roh)
    assert zurueck == {"version": 1, "toene": [bekannt["g"], bekannt["a"]]}


def _lauf(tmp_path, monkeypatch, eintrag, posten, **optionen):
    """grosser_lauf() ohne Netz: ein Eintrag im Index, eine Datei, feste Posten."""
    audio = tmp_path / "audio"
    audio.mkdir()
    (audio / "g01.mp3").write_bytes(b"\xff" * 900)
    monkeypatch.setattr(ton_bauen, "AUDIO", str(audio))
    monkeypatch.setattr(ton_bauen, "INDEX", str(audio / "index.json"))
    (audio / "index.json").write_text(json.dumps({"version": 1, "toene": [eintrag]}), encoding="utf-8")
    monkeypatch.setattr(ton_bauen, "sammle", lambda: posten)
    monkeypatch.setattr(ton_bauen.time, "sleep", lambda s: None)
    gerufen = []

    def dienst(zugang, text, stimme, langsam):
        gerufen.append(text)
        return b"\xff" * 900

    ton_bauen.grosser_lauf(dienst, {}, "wort-stimme", "gesch-stimme", **optionen)
    toene = json.load(io.open(str(audio / "index.json"), encoding="utf-8"))["toene"]
    return {e["datei"]: e for e in toene}, gerufen


def test_spaeterer_lauf_verliert_w_nicht(tmp_path, monkeypatch):
    text = "Rex je mali."
    eintrag = {"key": ton_bauen.schluessel(text), "datei": "g01.mp3", "text": text,
               "stimme": "gesch-stimme", "w": [[100, 300], [320, 400], [420, 700]]}
    toene, gerufen = _lauf(tmp_path, monkeypatch, dict(eintrag),
                           [{"art": "geschichte", "key": eintrag["key"], "text": text}])
    assert gerufen == []
    assert toene["g01.mp3"] == eintrag


def test_geaenderter_text_verliert_sein_w(tmp_path, monkeypatch):
    alt = "Rex je mali."
    eintrag = {"key": ton_bauen.schluessel(alt), "datei": "g01.mp3", "text": alt,
               "stimme": "gesch-stimme", "w": [[100, 300], [320, 400], [420, 700]]}
    # Nur die Schreibweise geaendert: derselbe Schluessel, dieselbe Datei,
    # aber "w" wurde fuer einen anderen Text geholt - es fliegt.
    neu = "REX je mali."
    toene, gerufen = _lauf(tmp_path, monkeypatch, dict(eintrag),
                           [{"art": "geschichte", "key": ton_bauen.schluessel(neu), "text": neu}])
    assert gerufen == [] and "w" not in toene["g01.mp3"]


def test_neue_geschichte_kommt_ohne_w(tmp_path, monkeypatch):
    alt = "Rex je mali."
    eintrag = {"key": ton_bauen.schluessel(alt), "datei": "g01.mp3", "text": alt,
               "stimme": "gesch-stimme", "w": [[100, 300], [320, 400], [420, 700]]}
    neu = "Rex je veliki."
    toene, gerufen = _lauf(tmp_path, monkeypatch, dict(eintrag),
                           [{"art": "geschichte", "key": ton_bauen.schluessel(neu), "text": neu}])
    assert gerufen == [ton_bauen.sprechtext(neu)]          # "Reks je veliki."
    assert "w" not in toene["g02.mp3"] and toene["g02.mp3"]["text"] == neu
    assert toene["g01.mp3"] == eintrag          # die alte Aufnahme behaelt ihre eigenen Zeiten


def test_nur_geschichten_spricht_keine_woerter(tmp_path, monkeypatch):
    """ton_bauen.py --nur-geschichten (16.11.2026): Woerter und Saetze spricht
    Emir, Azure nur die Geschichten. Die neue Geschichte bekommt ihre Aufnahme
    mit der Geschichtenstimme, das neue Wort keine und auch keine Nummer."""
    alt = "Rex je mali."
    eintrag = {"key": ton_bauen.schluessel(alt), "datei": "g01.mp3", "text": alt,
               "stimme": "gesch-stimme", "w": [[100, 300], [320, 400], [420, 700]]}
    neu = "Rex je veliki."
    posten = [{"art": "geschichte", "key": ton_bauen.schluessel(alt), "text": alt},
              {"art": "geschichte", "key": ton_bauen.schluessel(neu), "text": neu},
              {"art": "wort", "key": "veliki", "text": "veliki"}]
    # Ohne das echte ton_nur_emir.json: dort steht veliki seit dem 16.11.2026 (Emir,
    # Woerter der B1-Lesetexte), und grosser_lauf() liesse es dann zu Recht aus.
    monkeypatch.setattr(ton_bauen, "NUR_EMIR", str(tmp_path / "ton_nur_emir.json"))
    toene, gerufen = _lauf(tmp_path, monkeypatch, dict(eintrag), posten, nur_geschichten=True)
    assert gerufen == [ton_bauen.sprechtext(neu)]
    assert sorted(toene) == ["g01.mp3", "g02.mp3"]
    assert toene["g02.mp3"]["stimme"] == "gesch-stimme" and toene["g01.mp3"] == eintrag
    assert list((tmp_path / "audio").glob("w*.mp3")) == []
    # ohne die Option spricht derselbe Lauf auch das Wort, mit der Wortstimme
    zwei = tmp_path / "zwei"
    zwei.mkdir()
    toene, gerufen = _lauf(zwei, monkeypatch, dict(eintrag), posten)
    assert gerufen == [ton_bauen.sprechtext(neu), "veliki"]
    assert [e["stimme"] for e in toene.values() if e["key"] == "veliki"] == ["wort-stimme"]


def test_zugang_auch_ausserhalb_des_projekts(wurzel, tmp_path):
    """ZMAJ_TTS_ZUGANG (16.11.2026) nennt die Zugangsdatei, wenn sie nicht neben
    ton_bauen.py liegt - so muss der Schluessel nie ins Projekt kopiert werden.
    Ohne die Variable bleibt es tts_zugang.json neben dem Skript."""
    import subprocess
    import sys
    pfad = str(tmp_path / "zugang.json")
    befehl = [sys.executable, "-c", "import ton_bauen; print(ton_bauen.ZUGANG)"]
    umgebung = {k: v for k, v in os.environ.items() if k != "ZMAJ_TTS_ZUGANG"}
    ohne = subprocess.run(befehl, cwd=wurzel, env=umgebung, capture_output=True, text=True, check=True)
    assert ohne.stdout.strip() == os.path.join(wurzel, "tts_zugang.json")
    mit = subprocess.run(befehl, cwd=wurzel, env=dict(umgebung, ZMAJ_TTS_ZUGANG=pfad),
                         capture_output=True, text=True, check=True)
    assert mit.stdout.strip() == pfad
