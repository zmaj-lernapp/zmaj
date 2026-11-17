# -*- coding: utf-8 -*-
"""Die Woerter der 20 B1-Lesetexte haben Ton (16.11.2026, Offen-Liste 6a).

Tippt man in einer Geschichte ein Wort an, spricht die App es, wenn audioDatei() eine
Aufnahme findet. Auf dem Handy gibt es keine Computerstimme: 823 Woerter, die nur in den
20 B1-Lesetexten stehen (Pakete 1 bis 4 vom 13.11.2026), hatten keine und blieben dort
still. Ajdin (Fragen 16.11.2026, 1): „B“, Emir spricht sie sofort. Abgenommen am
16.11.2026: „die wörter von emir passen“, bei den 74 fraglichen die Empfehlung (s in
Fassung B, tiho in Ck, das ist C, nach dem Wort gekuerzt). 15 weitere Woerter dieser
Texte hatte Emir schon als Grammatik-Antwort gesprochen (w8956 bis w9048,
tests/test_grammatik_ton.py).

Die Aufnahmen liegen nur in der privaten Huelle (audio_emir/), die Nummern w9049 bis
w9871 in ton_nur_emir.json, in der Reihenfolge von ton_bauen.sammle()
(Stimme_Emir_neu\\geschichten_838_2026-11-16\\nummern.json). ljubazni steht seit dem
16.11.2026 auch im Brief an die Nana, der in sammle() vor b1_posao kommt, und hat
deshalb die erste Nummer. web/audio/index.json bleibt, die Web-Demo bleibt bei diesen
Woertern still. tests/offen_lesetexte.json "woerter" und WOERTER in tests/offen_b1_teil2.py
sind seitdem leer. Im Browser: tests_e2e/test_geschichtenwoerter_ton.py.

Seit dem 17.11.2026 stehen die Geschichten Stufe fuer Stufe (REIHENFOLGE in
geschichten.py, Offen-Liste 7), und "Razgovor za posao" hat auch die Stufe B1. Die 20
B1-Lesetexte sind darum die mit "b1_" vorn, und sammle() bringt die Woerter in einer
anderen Folge. Die Nummern bleiben (ton_bauen.py vergibt nur neue); verglichen wird mit
sammle() in der Folge vom 16.11.2026 (ALTE_FOLGE in tests/test_geschichten_stufen.py).
"""
import hashlib
import io
import json
import os

import pytest

ERSTE, LETZTE = 9049, 9871
ANZAHL = LETZTE - ERSTE + 1
GRAMMATIK_ERSTE, GRAMMATIK_LETZTE = 8956, 9048
# Die 15 Woerter aus den B1-Texten, die Emir schon als Grammatik-Antwort spricht.
AUS_DER_GRAMMATIK = ["gdje", "ko", "ste", "doktora", "bosne", "vode", "poslu", "joj", "napisao",
                     "kuhala", "pišem", "čekam", "nemoj", "budete", "čiji"]
EINBAU = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir,
                      "Stimme_Emir_neu", "geschichten_838_2026-11-16")
# Ajdins Abnahme (16.11.2026): hier nicht Fassung A.
GEWAEHLT = {"s": "s_B.mp3", "tiho": "tiho_Ck.mp3"}


def _nummer(datei):
    return int(datei[1:5])


def _index(wurzel):
    with io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8") as f:
        return {e["key"]: e["datei"] for e in json.load(f)["toene"]}


def _neu():
    import ton_bauen
    return sorted((e for e in ton_bauen.nur_emir().values() if ERSTE <= _nummer(e["datei"]) <= LETZTE),
                  key=lambda e: e["datei"])


def _b1_woerter():
    import geschichten
    import ton_bauen
    b1 = [g for g in geschichten.GESCHICHTEN if g["id"].startswith("b1_")]
    assert len(b1) == 20 and all(g["stufe"] == "B1" for g in b1), [g["id"] for g in b1]
    return {ton_bauen.schluessel(w) for g in b1 for w in ton_bauen.textwoerter(g["text"])}


def test_a_jedes_wort_der_b1_texte_hat_ton(wurzel):
    """Der Test, der die Luecke gefunden haette: jedes Wort jeder Geschichte hat eine
    Aufnahme in index.json oder ton_nur_emir.json (so bringt app_bauen.emir_drueber()
    sie in die App). Ohne die neuen Nummern fehlten genau diese 823."""
    import geschichten
    import ton_bauen
    index = _index(wurzel)
    emir = ton_bauen.nur_emir()
    alle = {ton_bauen.schluessel(w) for g in geschichten.GESCHICHTEN for w in ton_bauen.textwoerter(g["text"])}
    assert sorted(k for k in alle if k not in index and k not in emir) == []
    vorher = set(index) | {k for k, e in emir.items() if _nummer(e["datei"]) < ERSTE}
    still = {k for k in alle if k not in vorher}
    assert len(still) == ANZAHL
    assert still == {e["key"] for e in _neu()}
    assert still <= _b1_woerter()


def _sammle_wie_am_16_11(monkeypatch):
    """sammle() mit den Geschichten in der Folge vom 16.11.2026, als die Nummern
    vergeben wurden."""
    import ton_bauen
    from test_geschichten_stufen import ALTE_FOLGE
    echt = ton_bauen._modul

    def modul(name):
        m = echt(name)
        if name == "geschichten":
            m.GESCHICHTEN.sort(key=lambda g: ALTE_FOLGE.index(g["id"]))
        return m

    monkeypatch.setattr(ton_bauen, "_modul", modul)
    posten = ton_bauen.sammle()
    monkeypatch.setattr(ton_bauen, "_modul", echt)
    return posten


def test_b_nummern_lueckenlos_in_der_reihenfolge_von_sammle(monkeypatch):
    import ton_bauen
    neu = _neu()
    assert [e["datei"] for e in neu] == ["w%04d.mp3" % n for n in range(ERSTE, LETZTE + 1)]
    for e in neu:
        assert set(e) == {"key", "datei", "text"} and e["key"] == ton_bauen.schluessel(e["text"]), e
    # Die letzten Nummern ueberhaupt
    assert max(_nummer(e["datei"]) for e in ton_bauen.nur_emir().values()) == LETZTE
    # sammle() kennt alle als Wort aus einer Geschichte, mit demselben Text, und die Nummern
    # folgen seiner Reihenfolge vom 16.11.2026. Heute bringt sammle() dieselben Woerter,
    # nur steht ein Wort vielleicht zuerst gross in einer anderen Geschichte ("Boli").
    posten = [p for p in _sammle_wie_am_16_11(monkeypatch) if p["key"] in {e["key"] for e in neu}]
    assert [p["key"] for p in posten] == [e["key"] for e in neu]
    heute = [p for p in ton_bauen.sammle() if p["key"] in {e["key"] for e in neu}]
    assert (sorted((p["key"], p["text"].lower(), p["art"]) for p in heute)
            == sorted((p["key"], p["text"].lower(), p["art"]) for p in posten))
    assert all(p["art"] == "wort" for p in posten)
    assert [p["text"] for p in posten] == [e["text"] for e in neu]
    assert neu[0] == {"key": "ljubazni", "datei": "w9049.mp3", "text": "ljubazni"}


def test_b_wie_in_nummern_json():
    pfad = os.path.join(EINBAU, "nummern.json")
    if not os.path.exists(pfad):
        pytest.skip("Einbau-Ordner nicht da")
    with io.open(pfad, encoding="utf-8") as f:
        n = json.load(f)
    assert n["erste"] == "w%04d.mp3" % ERSTE and n["letzte"] == "w%04d.mp3" % LETZTE and n["anzahl"] == ANZAHL
    assert n["ton_nur_emir"] == _neu()


def test_c_die_grammatik_woerter_behalten_ihre_nummer():
    """Die 15 Woerter, die Emir schon als Grammatik-Antwort spricht, kommen nicht doppelt."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    for k in AUS_DER_GRAMMATIK:
        assert GRAMMATIK_ERSTE <= _nummer(emir[k]["datei"]) <= GRAMMATIK_LETZTE, emir[k]
    assert not set(AUS_DER_GRAMMATIK) & {e["key"] for e in _neu()}
    assert set(AUS_DER_GRAMMATIK) <= _b1_woerter()


def test_c_offen_ist_leer():
    import offen_b1_teil2
    import offen_lesetexte
    assert offen_lesetexte.TON == frozenset()
    assert offen_b1_teil2.WOERTER == frozenset() and offen_b1_teil2.ton_schluessel() == set()


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


def test_d_abgenommene_fassungen_in_der_huelle():
    """Jede Datei in der Huelle ist Byte fuer Byte die abgenommene aus fertig/, s ist
    Fassung B und tiho Ck."""
    import ton_pruefen
    huelle = ton_pruefen._huelle_audio()
    if not huelle or not os.path.isdir(os.path.join(EINBAU, "fertig")):
        pytest.skip("Huelle oder Einbau-Ordner nicht da")

    def md5(p):
        with open(p, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    for e in _neu():
        assert md5(os.path.join(huelle, e["datei"])) == md5(os.path.join(EINBAU, "fertig", e["key"] + ".mp3")), e
    neu = {e["key"]: e["datei"] for e in _neu()}
    for key, datei in GEWAEHLT.items():
        assert md5(os.path.join(huelle, neu[key])) == md5(os.path.join(EINBAU, "_app", datei)), key
