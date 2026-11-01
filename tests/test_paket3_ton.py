# -*- coding: utf-8 -*-
"""Wortschatz-Paket 3 (01.11.2026): Emir spricht die neuen Woerter und Saetze.

Die Aufnahmen hat ElevenLabs am 01.11.2026 erzeugt (Stimme Emir, dieselben
Einstellungen wie Paket 1 und 2), Ajdin hat sie abgehoert. Sie liegen nur
in der privaten Huelle unter audio_emir/, die Nummern stehen hier in
ton_nur_emir.json, in der Reihenfolge von ton_bauen.sammle():

- w3124 bis w3421: die elf Level aus Paket 3, jedes Wort direkt vor seinem
  Beispielsatz. Die vier Doppelformen stehen dort mit der ersten Form
  allein.
- w3720 bis w3723: dieselben vier mit allen Formen ("srčani udar,
  infarkt"). sammle() haengt sie hinter alles andere - also hinter
  Paket 4 (w3422 bis w3719, tests/test_paket4_ton.py) -, damit die
  vergebenen Nummern gleich bleiben. Wie strina / amidžinica am 23.10.2026.

zarađivati und jezik standen schon in index.json (zarađivati aus den
Geschichten, jezik = Sprache) und haben ihre Emir-Datei laengst in der
Huelle; jezik = Zunge hat denselben bosnischen Text und damit denselben
Ton.
"""
import io
import json
import os

import pytest

BEREICHE = ((3124, 3421), (3720, 3723))
SCHON_DA = {"zarađivati": "w1475.mp3", "jezik": "w1982.mp3"}
DOPPELFORMEN = ("srčani udar / infarkt", "svrbjeti / svrbiti", "apotekar / farmaceut", "toplomjer / termometar")
# Die elf Level aus Paket 3 (tests/test_paket3.py): drei in Tun und Lassen,
# acht in Sektion 12 · Körper und Gesundheit.
PAKET3 = ("kaufen_zurueckgeben", "geld_sparen", "paare_mehr",
          "koerper_aussen", "koerper_innen", "krank_sein", "beschwerden", "in_der_praxis", "untersuchen_heilen",
          "apotheke", "gesund_leben")


@pytest.fixture(scope="module")
def index(wurzel):
    return {e["key"]: e for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                    encoding="utf-8"))["toene"]}


def _level(daten):
    k = {x["id"]: x for x in daten["kategorien"]}
    return [k[i] for i in PAKET3]


def _neue_woerter(daten):
    """Die Woerter ohne ihre Beispielsaetze. Jedes Wort steht direkt vor
    seinem Satz (tests/test_paket3.py)."""
    return [w for k in _level(daten) for w in k["words"][0::2]]


def _neue_saetze(daten):
    return [w for k in _level(daten) for w in k["words"][1::2]]


def _nummer(datei):
    return int(datei[1:5])


def _im_bereich(datei):
    return any(a <= _nummer(datei) <= b for a, b in BEREICHE)


def _pruefe_emir(e, text, wo, wurzel, huelle):
    import ton_pruefen
    assert e["text"] == text, (wo, e)
    assert _im_bereich(e["datei"]), (wo, e)
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
    assert len(woerter) == 150
    assert sorted(w["bs"] for w in woerter if " / " in w["bs"]) == sorted(DOPPELFORMEN)
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
    assert len(gesehen) == 154      # 150 Woerter, 4 davon auch mit allen Formen


def test_doppelformen_alle_formen_am_ende(grunddaten):
    """Die Aufnahme mit allen Formen hat die Nummern w3720 bis w3723, die
    erste Form allein ihre Nummer an der Stelle des Wortes."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    alle = [emir[ton_bauen.schluessel_alle(bs)]["datei"] for bs in DOPPELFORMEN]
    assert sorted(alle) == ["w%04d.mp3" % n for n in range(3720, 3724)]
    for bs in DOPPELFORMEN:
        erste = emir[ton_bauen.schluessel(bs)]
        assert erste["text"] == bs
        assert 3124 <= _nummer(erste["datei"]) <= 3421, erste


def test_jeder_beispielsatz_hat_emirs_ton(grunddaten, index, wurzel):
    """Jeder der 150 Saetze hat seine eigene Aufnahme, Text genau wie in der
    App - auch die aus Ajdins Entscheidungen (Boli me u prsima. statt grudi,
    Ne mogu izabrati ...)."""
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
    for satz in ("Boli me u prsima.", "Ne mogu izabrati, sve mi se sviđa.", "Babo se uvijek cjenka na pijaci.",
                 "On ide na fizikalnu terapiju."):
        assert ton_bauen.schluessel(satz) in emir, satz


def test_nummern_gehoeren_dem_paket(grunddaten):
    """Genau die 302 neuen Aufnahmen, lueckenlos, keine fuer etwas anderes,
    und in der Reihenfolge von ton_bauen.sammle(). Die Nummern bleiben
    vergeben (ton_bauen.grosser_lauf zaehlt sie mit), auch wenn ein Wort
    spaeter wieder geht."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    im_paket = {e["datei"]: k for k, e in emir.items() if _im_bereich(e["datei"])}
    assert sorted(im_paket) == ["w%04d.mp3" % n for a, b in BEREICHE for n in range(a, b + 1)]
    assert len(im_paket) == 302
    texte = {w["bs"] for w in _neue_woerter(grunddaten) + _neue_saetze(grunddaten)}
    assert {emir[k]["text"] for k in im_paket.values()} <= texte
    reihe = [p["key"] for p in ton_bauen.sammle() if p["key"] in set(im_paket.values())]
    assert [im_paket[d] for d in sorted(im_paket)] == reihe
