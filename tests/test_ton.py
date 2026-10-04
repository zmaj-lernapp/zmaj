# -*- coding: utf-8 -*-
"""Die Tonspur: jedes Wort, jeder Satz und jede Geschichte hat eine Aufnahme."""
import io
import json
import os

import pytest


@pytest.fixture(scope="module")
def index(wurzel):
    return json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8"))


def test_ton_pruefen_meldet_nichts(wurzel):
    import ton_pruefen
    assert ton_pruefen.main() in (0, None)


def test_jede_datei_im_index_existiert_und_ist_nicht_leer(index, wurzel):
    fehlt, leer = [], []
    for e in index["toene"]:
        pfad = os.path.join(wurzel, "web", "audio", e["datei"])
        if not os.path.exists(pfad):
            fehlt.append(e["datei"])
        elif os.path.getsize(pfad) < 800:
            leer.append(e["datei"])
    assert not fehlt, fehlt[:20]
    assert not leer, leer[:20]


def test_jedes_wort_findet_seine_aufnahme(grunddaten, index):
    import daten_exportieren as de
    toene = {str(e["key"]).lower(): e["datei"] for e in index["toene"]}
    ohne = [w["bs"] for k in grunddaten["kategorien"] for w in k["words"]
            if not de.ton_datei(w["bs"], toene)]
    assert not ohne, ohne[:20]


def test_stimmen_sind_dokumentiert(index):
    """data/DATASHEET.md nennt die Stimmen. Kommt eine dazu, muss sie dort
    stehen - wer die Tonspur weitergibt, muss sagen können, woher sie ist."""
    stimmen = {e.get("stimme") for e in index["toene"]}
    assert stimmen <= {"bs-BA-GoranNeural", "bs-BA-VesnaNeural", "hr-HR-SreckoNeural"}, stimmen
