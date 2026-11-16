# -*- coding: utf-8 -*-
"""Die Antworten der Grammatik-Uebungen haben Ton (16.11.2026, Offen-Liste 6b).

Nach einer Grammatik-Uebung spricht die App g.richtig, wenn die Antwort bosnisch ist
(gramAntwortBosnisch in web/index.html: keine Klammer "(on)", "(ona)", "(ono)" am Ende)
und audioDatei() eine Aufnahme findet. Auf dem Handy gibt es keine Computerstimme: 94
der 175 Uebungen mit 93 verschiedenen Antworten blieben dort still. Ajdin (Fragen
15.11.2026, 8): „ja“, Emir spricht sie. Abgenommen hat er alle 93 (Hoerproben
Release\\Hoerproben_Emir_Grammatik_2026-11-15), Ko in Fassung C2, plačem in K2
(Fragen 16.11.2026, 2), bratom in A.

Die Aufnahmen liegen nur in der privaten Huelle (audio_emir/), die Nummern w8956 bis
w9048 in ton_nur_emir.json, in der Reihenfolge der Liste
(Stimme_Emir_neu\\nachbesserung_2026-11-15_grammatik\\nummern.json). web/audio/index.json
bleibt, die Web-Demo bleibt bei diesen Antworten still. ton_bauen.sammle() kennt sie
(letzter Block), damit ton_pruefen.py eine kuenftige Antwort ohne Ton meldet.
Dahinter stehen seit dem 16.11.2026 die Woerter der B1-Lesetexte (w9049 bis w9871,
tests/test_geschichtenwoerter_ton.py); hier zaehlt nur der Bereich bis w9048.
"""
import hashlib
import io
import json
import os
import re

import pytest

ERSTE, LETZTE = 8956, 9048
ANZAHL = LETZTE - ERSTE + 1
# Antworten, die sammle() schon vorher als Wort aus einem B1-Text kannte (ohne Ton).
SCHON_IN_SAMMLE = ["gdje", "ko", "ste", "doktora", "bosne", "vode", "poslu", "joj", "napisao",
                   "kuhala", "pišem", "čekam", "nemoj", "budete", "čiji"]
DEUTSCH = ["männlich (on)", "weiblich (ona)", "sächlich (ono)"]
GESCHLECHT = re.compile(r"\((on|ona|ono)\)\s*$")
EINBAU = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir,
                      "Stimme_Emir_neu", "nachbesserung_2026-11-15_grammatik")
# Ajdins Wahl (16.11.2026): diese Fassungen aus nachbesserung_3 stehen unter diesen Nummern.
GEWAEHLT = {"ko": "ko_C2.mp3", "plačem": "placem_K2.mp3", "bratom": "bratom_A.mp3"}


def _nummer(datei):
    return int(datei[1:5])


def _index(wurzel):
    with io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8") as f:
        return {e["key"]: e["datei"] for e in json.load(f)["toene"]}


def _audio_datei(text, haben):
    """Wie audioDatei() in web/index.html: bei " / " der ganze Text, dann die erste Form
    mit Satzzeichen, dann ohne .!?… am Ende (audioKey)."""
    klein = text.strip().lower()
    if " / " in klein and klein in haben:
        return haben[klein]
    voll = text.split(" / ")[0].strip().lower()
    kurz = re.sub(r"[.!?…]+$", "", text.split(" / ")[0]).strip().lower()
    return haben.get(voll) or haben.get(kurz)


def _antworten(grammatik):
    """Die bosnischen Antworten in der Reihenfolge der Lektionen, jede einmal."""
    raus = []
    for lektion in grammatik.values():
        for ue in lektion.get("uebungen", []):
            r = ue.get("richtig", "")
            if not GESCHLECHT.search(r) and r not in raus:
                raus.append(r)
    return raus


def _neu():
    import ton_bauen
    return sorted((e for e in ton_bauen.nur_emir().values() if ERSTE <= _nummer(e["datei"]) <= LETZTE),
                  key=lambda e: e["datei"])


def test_a_jede_bosnische_antwort_hat_ton(wurzel, alle_daten):
    """Der Test, der die Luecke gefunden haette: in jeder Sprache findet jede bosnische
    Antwort nach der Regel von audioDatei() eine Aufnahme in index.json oder
    ton_nur_emir.json (so wie app_bauen.emir_drueber() sie in die App bringt)."""
    import ton_bauen
    haben = dict(_index(wurzel))
    haben.update({k: e["datei"] for k, e in ton_bauen.nur_emir().items()})
    for code, daten in alle_daten.items():
        ohne = [r for r in _antworten(daten["grammatik"]) if not _audio_datei(r, haben)]
        assert ohne == [], (code, ohne[:20])
    # Ohne die neuen Nummern blieben genau diese 93 still (vorher: index.json und die
    # aelteren Emir-Aufnahmen). index.json selbst ist unveraendert.
    vorher = dict(_index(wurzel))
    vorher.update({k: e["datei"] for k, e in ton_bauen.nur_emir().items() if _nummer(e["datei"]) < ERSTE})
    still = [r for r in _antworten(alle_daten["de"]["grammatik"]) if not _audio_datei(r, vorher)]
    assert len(still) == ANZAHL, len(still)
    assert sorted(ton_bauen.schluessel(r) for r in still) == sorted(e["key"] for e in _neu())


def test_b_nummern_lueckenlos_in_der_reihenfolge_der_lektionen():
    import grammatik
    import ton_bauen
    neu = _neu()
    assert [e["datei"] for e in neu] == ["w%04d.mp3" % n for n in range(ERSTE, LETZTE + 1)]
    for e in neu:
        assert set(e) == {"key", "datei", "text"} and e["key"] == ton_bauen.schluessel(e["text"]), e
    # Die Reihenfolge der Antworten in grammatik.GRAMMATIK, nur die ohne Ton davor.
    reihe = [r for r in _antworten(grammatik.GRAMMATIK)]
    assert [e["text"] for e in neu] == [r for r in reihe if r in {x["text"] for x in neu}]
    # sammle() kennt alle 93: 15 schon als Wort aus einem B1-Text, 78 aus dem letzten Block,
    # dort in derselben Reihenfolge wie die Nummern.
    keys = [p["key"] for p in ton_bauen.sammle()]
    assert {e["key"] for e in neu} <= set(keys)
    start = min(keys.index(e["key"]) for e in neu if e["key"] not in SCHON_IN_SAMMLE)
    block = keys[start:]
    assert len(block) == ANZAHL - len(SCHON_IN_SAMMLE)
    assert block == [e["key"] for e in neu if e["key"] not in SCHON_IN_SAMMLE]
    assert all(keys.index(k) < start for k in SCHON_IN_SAMMLE)


def test_b_wie_in_nummern_json():
    pfad = os.path.join(EINBAU, "nummern.json")
    if not os.path.exists(pfad):
        pytest.skip("Einbau-Ordner nicht da")
    with io.open(pfad, encoding="utf-8") as f:
        n = json.load(f)
    assert n["erste"] == "w%04d.mp3" % ERSTE and n["letzte"] == "w%04d.mp3" % LETZTE and n["anzahl"] == ANZAHL
    assert n["ton_nur_emir"] == _neu()


def test_c_deutsche_antworten_nicht_gesprochen():
    import grammatik
    import ton_bauen
    deutsch = sorted({ue["richtig"] for lek in grammatik.GRAMMATIK.values() for ue in lek.get("uebungen", [])
                      if GESCHLECHT.search(ue.get("richtig", ""))})
    assert deutsch == sorted(DEUTSCH)
    texte = {p["text"] for p in ton_bauen.sammle()}
    assert not texte & set(DEUTSCH)
    assert not {ton_bauen.schluessel(d) for d in DEUTSCH} & set(ton_bauen.nur_emir())


def test_d_nur_in_der_huelle(wurzel):
    import ton_pruefen
    for e in _neu():
        assert not os.path.exists(os.path.join(wurzel, "web", "audio", e["datei"])), e
    assert not {e["key"] for e in _neu()} & set(_index(wurzel))
    huelle = ton_pruefen._huelle_audio()
    if not huelle:
        pytest.skip("Huelle nicht da")
    for e in _neu():
        pfad = os.path.join(huelle, e["datei"])
        assert os.path.isfile(pfad) and os.path.getsize(pfad) >= ton_pruefen.MINDEST, e


def test_d_ajdins_fassungen_in_der_huelle():
    """Ko C2, plačem K2 und bratom A (nachbesserung_3) liegen unter ihren Nummern."""
    import ton_bauen
    import ton_pruefen
    huelle = ton_pruefen._huelle_audio()
    quelle = os.path.join(EINBAU, "nachbesserung_3")
    if not huelle or not os.path.isdir(quelle):
        pytest.skip("Huelle oder Einbau-Ordner nicht da")
    emir = ton_bauen.nur_emir()

    def md5(p):
        with open(p, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    for key, datei in GEWAEHLT.items():
        assert md5(os.path.join(huelle, emir[key]["datei"])) == md5(os.path.join(quelle, datei)), key
