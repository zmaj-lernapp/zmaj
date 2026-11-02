# -*- coding: utf-8 -*-
"""Wortschatz-Paket 1 (31.10.2026): Emir spricht die neuen Woerter und Saetze.

Die Aufnahmen hat ElevenLabs am 31.10.2026 erzeugt (Stimme Emir, wie
emir_lauf.py). Sie liegen nur in der privaten Huelle unter audio_emir/, die
Nummern stehen hier in ton_nur_emir.json: w2521 bis w2671. Woerter mit
" / " haben zwei Aufnahmen, alle Formen ("boljeti, boliti") und die erste
Form allein - wie strina / amidžinica am 23.10.2026. ostati, voziti,
naučiti und početi standen schon in index.json (Woerter aus den
Geschichten) und haben ihre Emir-Datei laengst in der Huelle.

Seit dem 31.10.2026 spricht Emir auch die 150 Beispielsaetze (Ajdin:
"Jedes neue Wort bekommt einen Beispielsatz mit Emir-Ton"): w2672 bis
w2821, ebenfalls nur in der Huelle.
"""
import io
import json
import os

import pytest

ERSTE = 2521
LETZTE = 2671
SATZ_ERSTE = 2672
SATZ_LETZTE = 2821
SCHON_DA = {"ostati": "w1387.mp3", "voziti": "w1385.mp3", "naučiti": "w1408.mp3", "početi": "w1478.mp3"}
# Die zehn Level aus Paket 1. Seit Paket 2 (31.10.2026) hat die Sektion
# tunlassen vier Level mehr - deren Ton prueft nicht dieser Test.
PAKET1 = ("kommen_gehen", "geben_nehmen", "sagen_denken", "verstehen", "anfangen", "tun_machen",
          "stellen_legen", "alltag_leben", "passieren", "notfall")


@pytest.fixture(scope="module")
def index(wurzel):
    return {e["key"]: e for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                    encoding="utf-8"))["toene"]}


def _neue_woerter(daten):
    """Die Woerter der Sektion 10 ohne ihre Beispielsaetze. Jedes Wort steht
    direkt vor seinem Satz (tests/test_paket1.py)."""
    return [w for k in daten["kategorien"] if k["id"] in PAKET1 for w in k["words"][0::2]]


def _nummer(datei):
    return int(datei[1:5])


def test_jede_neue_wort_id_hat_emirs_ton(grunddaten, index, wurzel):
    """Jede neue Wort-ID gegen ton_nur_emir.json: die App findet ihren Ton
    ueber den Schluessel aus dem bosnischen Text (audioDatei() in
    web/index.html) - bei " / " zuerst ueber alle Formen."""
    import ton_bauen
    import ton_pruefen
    emir = ton_bauen.nur_emir()
    huelle = ton_pruefen._huelle_audio()
    woerter = _neue_woerter(grunddaten)
    assert len(woerter) == 150
    ohne, gesehen = [], set()
    for w in woerter:
        schluessel = [ton_bauen.schluessel(w["bs"])]
        if " / " in w["bs"]:
            schluessel.insert(0, ton_bauen.schluessel_alle(w["bs"]))
        for k in schluessel:
            gesehen.add(k)
            if k in SCHON_DA:
                assert index[k]["datei"] == SCHON_DA[k], (w["id"], k)
                if huelle:
                    assert os.path.isfile(os.path.join(huelle, SCHON_DA[k])), (w["id"], k)
                continue
            e = emir.get(k)
            if not e:
                ohne.append((w["id"], k))
                continue
            assert k not in index, (w["id"], k)
            assert e["text"] == w["bs"], (w["id"], e)
            assert ERSTE <= _nummer(e["datei"]) <= LETZTE, (w["id"], e)
            assert not os.path.exists(os.path.join(wurzel, "web", "audio", e["datei"])), e
            if huelle:
                pfad = os.path.join(huelle, e["datei"])
                assert os.path.isfile(pfad) and os.path.getsize(pfad) >= ton_pruefen.MINDEST, \
                    "Emir-Aufnahme fehlt in der Huelle: %s (%s)" % (e["datei"], w["id"])
    assert not ohne, ohne[:20]
    assert len(gesehen) == 155      # 145 Woerter, 5 mit allen Formen, 5 mit der ersten Form


def test_nummern_w2521_bis_w2671_gehoeren_dem_paket(grunddaten):
    """Genau die 151 neuen Aufnahmen, lueckenlos und keine fuer etwas
    anderes. Die Nummern bleiben vergeben (ton_bauen.grosser_lauf zaehlt
    sie mit), auch wenn ein Wort spaeter wieder geht."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    im_paket = {e["datei"]: k for k, e in emir.items() if ERSTE <= _nummer(e["datei"]) <= LETZTE}
    assert sorted(im_paket) == ["w%04d.mp3" % n for n in range(ERSTE, LETZTE + 1)]
    texte = {w["bs"] for w in _neue_woerter(grunddaten)}
    assert {emir[k]["text"] for k in im_paket.values()} <= texte


def _neue_saetze(daten):
    """Die Beispielsaetze der Sektion 10: jeder steht direkt hinter seinem Wort."""
    return [w for k in daten["kategorien"] if k["id"] in PAKET1 for w in k["words"][1::2]]


def test_jeder_beispielsatz_hat_emirs_ton(grunddaten, wurzel):
    """Jeder der 150 Saetze hat seine eigene Aufnahme, Text genau wie in der
    App, Nummer zwischen w2672 und w2821 - lueckenlos und nur fuer diese
    Saetze."""
    import ton_bauen
    import ton_pruefen
    emir = ton_bauen.nur_emir()
    huelle = ton_pruefen._huelle_audio()
    saetze = _neue_saetze(grunddaten)
    assert len(saetze) == 150
    ohne = []
    for s in saetze:
        k = ton_bauen.schluessel(s["bs"])
        e = emir.get(k)
        if not e:
            ohne.append((s["id"], k))
            continue
        assert e["text"] == s["bs"], (s["id"], e)
        assert SATZ_ERSTE <= _nummer(e["datei"]) <= SATZ_LETZTE, (s["id"], e)
        assert not os.path.exists(os.path.join(wurzel, "web", "audio", e["datei"])), e
        if huelle:
            pfad = os.path.join(huelle, e["datei"])
            assert os.path.isfile(pfad) and os.path.getsize(pfad) >= ton_pruefen.MINDEST, \
                "Emir-Aufnahme fehlt in der Huelle: %s (%s)" % (e["datei"], s["id"])
    assert not ohne, ohne[:20]
    im_bereich = {e["datei"]: e["text"] for e in emir.values()
                  if SATZ_ERSTE <= _nummer(e["datei"]) <= SATZ_LETZTE}
    assert sorted(im_bereich) == ["w%04d.mp3" % n for n in range(SATZ_ERSTE, SATZ_LETZTE + 1)]
    assert set(im_bereich.values()) == {s["bs"] for s in saetze}
