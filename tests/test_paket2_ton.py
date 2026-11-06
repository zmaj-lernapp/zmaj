# -*- coding: utf-8 -*-
"""Wortschatz-Paket 2 (31.10.2026): Emir spricht die neuen Woerter und Saetze.

Die Aufnahmen hat ElevenLabs am 31.10.2026 erzeugt (Stimme Emir, dieselben
Einstellungen wie Paket 1). Sie liegen nur in der privaten Huelle unter
audio_emir/, die Nummern stehen hier in ton_nur_emir.json: w2822 bis w3123,
in der Reihenfolge von ton_bauen.sammle(), also jedes Wort direkt vor
seinem Beispielsatz. Die Saetze sind eigene Lerneintraege und brauchen
ihren Ton genauso (Lehre aus Paket 1).

"dešavati se / događati se" und "smrdjeti / smrditi" haben zwei
Aufnahmen: alle Formen und die erste Form allein, wie strina / amidžinica
am 23.10.2026. dug und skuhati standen schon in index.json (dug =
Schulden, skuhati aus einer Geschichte) und haben ihre Emir-Datei laengst
in der Huelle.
"""
import io
import json
import os

import pytest

ERSTE = 2822
LETZTE = 3123
SCHON_DA = {"dug": "w1009.mp3", "skuhati": "w1415.mp3"}
# Die elf Level aus Paket 2 (tests/test_paket2.py): vier in Tun und
# Lassen, sieben in Sektion 11 · Wie etwas ist.
PAKET2 = ("paare_geben", "paare_denken", "paare_alltag", "im_haushalt",
          "lang_kurz", "voll_leer", "moeglich", "wie_jemand_ist", "benehmen", "glueck_sorgen", "sinne")


@pytest.fixture(scope="module")
def index(wurzel):
    return {e["key"]: e for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                    encoding="utf-8"))["toene"]}


def _level(daten):
    k = {x["id"]: x for x in daten["kategorien"]}
    return [k[i] for i in PAKET2]


def _neue_woerter(daten):
    """Die Woerter ohne ihre Beispielsaetze. Jedes Wort steht direkt vor
    seinem Satz (tests/test_paket2.py)."""
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
    web/index.html) - bei " / " zuerst ueber alle Formen."""
    import ton_bauen
    import ton_pruefen
    emir = ton_bauen.nur_emir()
    huelle = ton_pruefen._huelle_audio()
    woerter = _neue_woerter(grunddaten)
    assert len(woerter) == 151
    ohne, gesehen = [], set()
    for w in woerter:
        schluessel = [ton_bauen.schluessel(w["bs"])]
        if " / " in w["bs"]:
            schluessel.insert(0, ton_bauen.schluessel_alle(w["bs"]))
        for k in schluessel:
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
    assert len(gesehen) == 153      # 149 Woerter, 2 davon auch mit allen Formen, dazu dug und skuhati


def test_jeder_beispielsatz_hat_emirs_ton(grunddaten, index, wurzel):
    """Jeder der 151 Saetze hat seine eigene Aufnahme, Text genau wie in der
    App - auch die beiden aus Ajdins Entscheidung zu okus und ukus."""
    import ton_bauen
    import ton_pruefen
    emir = ton_bauen.nur_emir()
    huelle = ton_pruefen._huelle_audio()
    saetze = _neue_saetze(grunddaten)
    assert len(saetze) == 151
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
    for satz in ("Ovo ima čudan okus.", "Imaš dobar ukus."):
        assert ton_bauen.schluessel(satz) in emir, satz


def test_nummern_w2822_bis_w3123_gehoeren_dem_paket(grunddaten):
    """Genau die 302 neuen Aufnahmen, lueckenlos, keine fuer etwas anderes,
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
