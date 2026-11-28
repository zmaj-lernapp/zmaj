# -*- coding: utf-8 -*-
"""Emirs Ton fuer K2 und K7, fuer jede Bedeutung und fuer die Hose (Ton-Schritt 1.5, 27.11.2026).

Emir hat am 21.11.2026 die K2-Liste gesprochen (Stimme_Emir_neu/k2_2026-11-21), am 26.11.
„Češljam se.“, „Od prašine stalno kišem.“ und „Jela ostaje zelena i u zimi.“ neu
(k2_neu_2026-11-26, Ajdins Wahl C, F, D) und dazu „pantalone, hlače.“ (Fassung A). Die
Toene je Bedeutung sind vom 21.11. (ton_bedeutung_2026-11-21), sam (bin), niz (hinunter),
pita (fragt) und pravi (macht) in Ajdins Ersatzfassung (K3, K1, K1, K2). radi (wegen) bleibt
draussen (w10085): keine Fassung passte, Ajdin: „lassen wir erstmal“, es spielt weiter w5172.

Die Aufnahmen liegen nur in den privaten Huellen (audio_emir/), die Nummern in
ton_nur_emir.json: w9872 bis w10058 in der Folge der Emir-Liste
(Release/Wortschatz/k2_2026-11-20/final/emir_liste.json), w10059 bis w10093 ohne w10085,
w10094. Elf Woerter, die englisch klangen oder schlecht ausgesprochen waren, haben unter
ihrer alten Nummer eine neue Aufnahme bekommen (GLEICHE_NUMMER); ihr Schluessel bleibt.
"""
import hashlib
import io
import json
import os

import pytest

import k2_einbau as K2

STIMME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir, "Stimme_Emir_neu")
K2_ALT = os.path.join(STIMME, "k2_2026-11-21", "gewaehlt")
K2_NEU = os.path.join(STIMME, "k2_neu_2026-11-26", "gewaehlt")
BEDEUTUNG = os.path.join(STIMME, "ton_bedeutung_2026-11-21", "gewaehlt")
ERSATZ = os.path.join(STIMME, "ton_bedeutung_2026-11-21", "ersatz_2026-11-21")
LISTE = os.path.join(STIMME, os.pardir, "Release", "Wortschatz", "k2_2026-11-20", "final", "emir_liste.json")

AUS_K2_NEU = ["w9920.mp3", "w9970.mp3", "w10058.mp3"]
BEDEUTUNG_ERSTE, BEDEUTUNG_LETZTE = 10059, 10093
RADI_WEGEN = ("radi (wegen)", "w10085.mp3")
ERSATZ_WAHL = {"w10059.mp3": "sam_K3.mp3", "w10066.mp3": "niz_K1.mp3",
               "w10070.mp3": "pita_K1.mp3", "w10072.mp3": "pravi_K2.mp3"}
# Neue Aufnahme unter der alten Nummer (Ajdins Wahl 26./27.11.2026, k2_neu_2026-11-26/LIESMICH.md)
GLEICHE_NUMMER = {"w0275.mp3": "kuća", "w0276.mp3": "grad", "w0851.mp3": "most", "w0207.mp3": "more",
                  "w0083.mp3": "sin", "w1760.mp3": "lift", "w3554.mp3": "film", "w9855.mp3": "sit",
                  "w0358.mp3": "on", "w9705.mp3": "mom", "w9477.mp3": "sale"}


def _nummer(datei):
    import ton_bauen
    return ton_bauen.dateinummer(datei)


def _k2():
    import ton_bauen
    return sorted((e for e in ton_bauen.nur_emir().values() if K2.TON_ERSTE <= _nummer(e["datei"]) <= K2.TON_LETZTE),
                  key=lambda e: _nummer(e["datei"]))


def _index(wurzel):
    with io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8") as f:
        return {e["key"]: e["datei"] for e in json.load(f)["toene"]}


def _huellen():
    import huelle
    import ton_pruefen
    raus = [ton_pruefen._huelle_audio()]
    ios = os.path.join(os.path.dirname(huelle.ordner()), "zmaj-huelle-ios", "audio_emir")
    raus.append(ios if os.path.isdir(ios) else None)
    return [h for h in raus if h]


def _md5(pfad):
    with open(pfad, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def test_k2_lueckenlos_mit_dem_text_der_app():
    import ton_bauen
    k2 = _k2()
    assert [e["datei"] for e in k2] == ["w%04d.mp3" % n for n in range(K2.TON_ERSTE, K2.TON_LETZTE + 1)]
    texte = {}
    for p in ton_bauen.sammle():
        texte.setdefault(p["key"], p["text"])
    for e in k2:
        assert set(e) == {"key", "datei", "text"} and e["key"] == ton_bauen.schluessel(e["text"]), e
        assert texte.get(e["key"]) == e["text"], e
    # genau das, was bis zum Ton-Schritt in TON_OFFEN stand
    assert {e["key"] for e in k2} | {K2.TON_HOSE["key"]} == K2.TON_EINGEBAUT
    assert len(K2.TON_EINGEBAUT) == 188 and K2.TON_OFFEN == frozenset()


def test_hose_mit_beiden_formen(wurzel):
    """Wie nana / metvica (w8955): gesprochen „pantalone, hlače.“, Schluessel mit allen Formen.
    Die erste Form allein (etwa fuer ein angetipptes Wort) behaelt ihre Aufnahme."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    assert emir[K2.TON_HOSE["key"]] == K2.TON_HOSE
    assert K2.TON_HOSE["key"] == ton_bauen.schluessel_alle(K2.TON_HOSE["text"])
    alle = [p for p in ton_bauen.sammle() if p["key"] == K2.TON_HOSE["key"]]
    assert alle == [{"art": "wort", "key": "pantalone / hlače", "text": "pantalone / hlače", "alle": True}]
    assert "pantalone" in set(emir) | set(_index(wurzel))


def test_k2_kommt_nicht_doppelt(wurzel):
    """Kein neuer Schluessel hatte schon eine Aufnahme (web/audio oder aelter bei Emir)."""
    import ton_bauen
    neu = {e["key"] for e in _k2()} | {K2.TON_HOSE["key"]}
    aelter = {k for k, e in ton_bauen.nur_emir().items() if _nummer(e["datei"]) < K2.TON_ERSTE}
    assert not neu & set(_index(wurzel)) and not neu & aelter


def test_ton_je_bedeutung_34_von_35():
    import ton_bauen
    import ton_bedeutung
    emir = ton_bauen.nur_emir()
    eigene = ton_bedeutung.eigene_schluessel()
    assert len(eigene) == 35
    assert sorted(set(eigene) - set(emir)) == [RADI_WEGEN[0]]
    da = [emir[k] for k in eigene if k in emir]
    for e in da:
        assert e == {"key": e["key"], "datei": e["datei"], "text": e["key"]}, e
    assert sorted(_nummer(e["datei"]) for e in da) == [n for n in range(BEDEUTUNG_ERSTE, BEDEUTUNG_LETZTE + 1)
                                                       if n != _nummer(RADI_WEGEN[1])]
    assert RADI_WEGEN[1] not in {e["datei"] for e in emir.values()}


def test_wie_in_der_emir_liste():
    pfad = os.path.normpath(LISTE)
    if not os.path.exists(pfad):
        pytest.skip("Release-Ordner nicht da")
    import ton_bauen
    with io.open(pfad, encoding="utf-8") as f:
        liste = json.load(f)
    nach_datei = {e["datei"]: e for e in ton_bauen.nur_emir().values()}
    for a in liste["aufnahmen"] + liste["zusatz_beide_bedeutungen"]["aufnahmen"]:
        if a["datei"] == RADI_WEGEN[1]:
            assert a["datei"] not in nach_datei
            continue
        soll = a.get("schluessel") or ton_bauen.schluessel(a["text"])
        assert nach_datei[a["datei"]]["key"] == soll, a["datei"]


def test_neue_nummer_bleibt_beim_wort(wurzel):
    """Die elf neuen Aufnahmen tragen die Nummer des Worts von frueher, der Schluessel bleibt."""
    import ton_bauen
    haben = {d: k for k, d in _index(wurzel).items()}
    haben.update({e["datei"]: k for k, e in ton_bauen.nur_emir().items()})
    assert {d: haben.get(d) for d in GLEICHE_NUMMER} == GLEICHE_NUMMER


def test_nur_in_der_huelle(wurzel):
    import ton_pruefen
    neu = _k2() + [K2.TON_HOSE]
    for e in neu:
        assert not os.path.exists(os.path.join(wurzel, "web", "audio", e["datei"])), e
    huellen = _huellen()
    if not huellen:
        pytest.skip("Huelle nicht da")
    import ton_bauen
    import ton_bedeutung
    emir = ton_bauen.nur_emir()
    dateien = [e["datei"] for e in neu] + [emir[k]["datei"] for k in ton_bedeutung.eigene_schluessel() if k in emir]
    for h in huellen:
        for d in dateien + list(GLEICHE_NUMMER):
            pfad = os.path.join(h, d)
            assert os.path.isfile(pfad) and os.path.getsize(pfad) >= ton_pruefen.MINDEST, pfad
        assert not os.path.exists(os.path.join(h, RADI_WEGEN[1])), h


def test_ajdins_fassungen_in_der_huelle():
    """Jede Datei in beiden Huellen ist Byte fuer Byte die gewaehlte aus Stimme_Emir_neu."""
    huellen = _huellen()
    if not huellen or not all(os.path.isdir(p) for p in (K2_ALT, K2_NEU, BEDEUTUNG, ERSATZ)):
        pytest.skip("Huelle oder Einbau-Ordner nicht da")
    import ton_bauen
    import ton_bedeutung
    emir = ton_bauen.nur_emir()
    quelle = {}
    for e in _k2():
        quelle[e["datei"]] = os.path.join(K2_NEU if e["datei"] in AUS_K2_NEU else K2_ALT, e["datei"])
    quelle[K2.TON_HOSE["datei"]] = os.path.join(K2_NEU, K2.TON_HOSE["datei"])
    for k in ton_bedeutung.eigene_schluessel():
        if k in emir:
            d = emir[k]["datei"]
            quelle[d] = os.path.join(ERSATZ, ERSATZ_WAHL[d]) if d in ERSATZ_WAHL else os.path.join(BEDEUTUNG, d)
    for d in GLEICHE_NUMMER:
        quelle[d] = os.path.join(K2_NEU, d)
    assert len(quelle) == 187 + 1 + 34 + 11
    for d, ers in ERSATZ_WAHL.items():          # in gewaehlt eingesetzt, die alte liegt in _alt
        assert _md5(os.path.join(BEDEUTUNG, d)) == _md5(os.path.join(ERSATZ, ers)), d
    for h in huellen:
        for d, q in quelle.items():
            assert _md5(os.path.join(h, d)) == _md5(q), (h, d)
