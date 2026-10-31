# -*- coding: utf-8 -*-
"""Wortschatz-Paket 1 (31.10.2026): Emir spricht die neuen Woerter.

Die Aufnahmen hat ElevenLabs am 31.10.2026 erzeugt (Stimme Emir, wie
emir_lauf.py). Sie liegen nur in der privaten Huelle unter audio_emir/, die
Nummern stehen hier in ton_nur_emir.json: w2521 bis w2671. Woerter mit
" / " haben zwei Aufnahmen, alle Formen ("boljeti, boliti") und die erste
Form allein - wie strina / amidžinica am 23.10.2026. ostati, voziti,
naučiti und početi standen schon in index.json (Woerter aus den
Geschichten) und haben ihre Emir-Datei laengst in der Huelle.

Die Beispielsaetze des Pakets haben noch keine Aufnahme; das melden
ton_pruefen.py und tests/test_ton.py, nicht dieser Test.
"""
import io
import json
import os

import pytest

ERSTE = 2521
LETZTE = 2671
SCHON_DA = {"ostati": "w1387.mp3", "voziti": "w1385.mp3", "naučiti": "w1408.mp3", "početi": "w1478.mp3"}


@pytest.fixture(scope="module")
def index(wurzel):
    return {e["key"]: e for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                    encoding="utf-8"))["toene"]}


def _neue_woerter(daten):
    """Die Woerter der Sektion 10 ohne ihre Beispielsaetze. Jedes Wort steht
    direkt vor seinem Satz (tests/test_paket1.py)."""
    return [w for k in daten["kategorien"] if k.get("sektion") == "tunlassen" for w in k["words"][0::2]]


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
