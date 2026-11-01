# -*- coding: utf-8 -*-
"""Wortschatz-Paket 4 (01.11.2026): Emir spricht die neuen Woerter und Saetze.

Die Aufnahmen hat ElevenLabs am 01.11.2026 erzeugt (Stimme Emir, dieselben
Einstellungen wie Paket 1 bis 3), Ajdin hat sie abgehoert und bei sport und
pekar unter mehreren Fassungen gewaehlt. Sie liegen nur in der privaten
Huelle unter audio_emir/, die Nummern stehen hier in ton_nur_emir.json:
w3422 bis w3719, in der Reihenfolge von ton_bauen.sammle(), also jedes
Wort direkt vor seinem Beispielsatz. Paket 4 hat keine Doppelformen.

vrijeme und još standen schon in index.json (vrijeme = Wetter, još aus den
Geschichten) und haben ihre Emir-Datei laengst in der Huelle; vrijeme =
Zeit hat denselben bosnischen Text und damit denselben Ton.

Zusammen mit Paket 3 (tests/test_paket3_ton.py) belegen die beiden Pakete
w3124 bis w3723 lueckenlos.
"""
import io
import json
import os

import pytest

ERSTE = 3422
LETZTE = 3719
SCHON_DA = {"vrijeme": "w0190.mp3", "još": "w1405.mp3"}
# Die zehn Level aus Paket 4 (tests/test_paket4.py): sechs in Sektion 13 ·
# Zeit und Freizeit, vier in Sektion 14 · Lernen und Arbeiten.
PAKET4 = ("zeitangaben", "sofort_endlich", "sport", "hobbys", "medien", "urlaub",
          "schule", "lernen_studieren", "berufe", "arbeitsplatz")


@pytest.fixture(scope="module")
def index(wurzel):
    return {e["key"]: e for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                    encoding="utf-8"))["toene"]}


def _level(daten):
    k = {x["id"]: x for x in daten["kategorien"]}
    return [k[i] for i in PAKET4]


def _neue_woerter(daten):
    """Die Woerter ohne ihre Beispielsaetze. Jedes Wort steht direkt vor
    seinem Satz (tests/test_paket4.py)."""
    return [w for k in _level(daten) for w in k["words"][0::2]]


def _neue_saetze(daten):
    return [w for k in _level(daten) for w in k["words"][1::2]]


def _nummer(datei):
    return int(datei[1:5])


def _pruefe_emir(e, text, wo, wurzel, huelle):
    import ton_pruefen
    assert e["text"] == text, (wo, e)
    assert ERSTE <= _nummer(e["datei"]) <= LETZTE, (wo, e)
    assert not os.path.exists(os.path.join(wurzel, "web", "audio", e["datei"])), e
    if huelle:
        pfad = os.path.join(huelle, e["datei"])
        assert os.path.isfile(pfad) and os.path.getsize(pfad) >= ton_pruefen.MINDEST, \
            "Emir-Aufnahme fehlt in der Huelle: %s (%s)" % (e["datei"], wo)


def test_jede_neue_wort_id_hat_emirs_ton(grunddaten, index, wurzel):
    """Jede neue Wort-ID gegen ton_nur_emir.json: die App findet ihren Ton
    ueber den Schluessel aus dem bosnischen Text (audioDatei() in
    web/index.html)."""
    import ton_bauen
    import ton_pruefen
    emir = ton_bauen.nur_emir()
    huelle = ton_pruefen._huelle_audio()
    woerter = _neue_woerter(grunddaten)
    assert len(woerter) == 150
    assert not [w["bs"] for w in woerter if " / " in w["bs"]]
    ohne, gesehen = [], set()
    for w in woerter:
        k = ton_bauen.schluessel(w["bs"])
        gesehen.add(k)
        if k in SCHON_DA:
            assert index[k]["datei"] == SCHON_DA[k], (w["id"], k)
            assert k not in emir, (w["id"], k)
            if huelle:
                assert os.path.isfile(os.path.join(huelle, SCHON_DA[k])), (w["id"], k)
            continue
        e = emir.get(k)
        if not e:
            ohne.append((w["id"], k))
            continue
        assert k not in index, (w["id"], k)
        _pruefe_emir(e, w["bs"], w["id"], wurzel, huelle)
    assert not ohne, ohne[:20]
    assert len(gesehen) == 150


def test_jeder_beispielsatz_hat_emirs_ton(grunddaten, index, wurzel):
    """Jeder der 150 Saetze hat seine eigene Aufnahme, Text genau wie in der
    App."""
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
        assert k not in index, (s["id"], k)
        _pruefe_emir(e, s["bs"], s["id"], wurzel, huelle)
    assert not ohne, ohne[:20]


def test_nummern_w3422_bis_w3719_gehoeren_dem_paket(grunddaten):
    """Genau die 298 neuen Aufnahmen, lueckenlos, keine fuer etwas anderes,
    und in der Reihenfolge von ton_bauen.sammle(). Die Nummern bleiben
    vergeben (ton_bauen.grosser_lauf zaehlt sie mit), auch wenn ein Wort
    spaeter wieder geht."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    im_paket = {e["datei"]: k for k, e in emir.items() if ERSTE <= _nummer(e["datei"]) <= LETZTE}
    assert sorted(im_paket) == ["w%04d.mp3" % n for n in range(ERSTE, LETZTE + 1)]
    texte = {w["bs"] for w in _neue_woerter(grunddaten) + _neue_saetze(grunddaten)}
    assert {emir[k]["text"] for k in im_paket.values()} <= texte
    reihe = [p["key"] for p in ton_bauen.sammle() if p["key"] in set(im_paket.values())]
    assert [im_paket[d] for d in sorted(im_paket)] == reihe


def test_pakete_3_und_4_belegen_w3124_bis_w3723(grunddaten):
    """Paket 3 (w3124-w3421, w3720-w3723) und Paket 4 (w3422-w3719) belegen
    zusammen w3124 bis w3723 lueckenlos, in der Reihenfolge von sammle():
    erst alle Woerter und Saetze, dann die Doppelformen mit allen Formen."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    neu = {e["datei"]: k for k, e in emir.items() if 3124 <= _nummer(e["datei"]) <= 3723}
    assert sorted(neu) == ["w%04d.mp3" % n for n in range(3124, 3724)]
    reihe = [p["key"] for p in ton_bauen.sammle() if p["key"] in set(neu.values())]
    assert [neu[d] for d in sorted(neu)] == reihe
