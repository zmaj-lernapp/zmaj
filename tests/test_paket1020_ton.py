# -*- coding: utf-8 -*-
"""Wortschatz-Pakete 10 bis 20 und die Warteliste (07.11.2026): Emir spricht.

Die Aufnahmen hat ElevenLabs am 07.11.2026 erzeugt (Stimme Emir, dieselben
Einstellungen wie Paket 4; Stimme_Emir_neu\\monat_vorbereitung). Sie liegen nur in der
privaten Huelle unter audio_emir/ (Zweig sammeln-v111), die Nummern stehen in
ton_nur_emir.json: w5317 bis w8952, in der Reihenfolge von ton_bauen.sammle(), vergeben
beim Geruest (Release\\Wortschatz\\_uebersetzung_p10_20\\nummern.json).

Zugeordnet wurde nur, was eindeutig passt: der gesprochene Text gleich dem Bosnischen
der Kennung, ohne Unterschied bei Satzzeichen. rub, rat, mrtav, naime und poput
stammen aus der Aufnahme vom 05.11.2026 (nur ihr Satz wartete), naime / jer und
poput / kao sind aus fertigen Einzelaufnahmen zusammengesetzt, keine neue Aufnahme.

Frei bleibt w5331, der Satz zu smijeh: Die alte Aufnahme w4691 ist aufbewahrt, aber
nicht angehoert (tests/offen_p1020.json).
"""
import io
import json
import os

ERSTE, LETZTE = 5317, 8952
FREI = {5331}
ZUSAMMENGESETZT = ["naime / jer", "poput / kao"]
VOM_05_11 = ["rub", "rat", "mrtav", "naime", "poput"]


def _nummer(datei):
    return int(datei[1:5])


def _im_bereich(emir):
    return {e["datei"]: k for k, e in emir.items() if ERSTE <= _nummer(e["datei"]) <= LETZTE}


def test_nummern_lueckenlos_und_in_der_reihenfolge_der_app():
    import ton_bauen
    emir = ton_bauen.nur_emir()
    neu = _im_bereich(emir)
    assert sorted(neu) == ["w%04d.mp3" % n for n in range(ERSTE, LETZTE + 1) if n not in FREI]
    assert max(_nummer(e["datei"]) for e in emir.values()) == LETZTE
    reihe = [p["key"] for p in ton_bauen.sammle() if p["key"] in set(neu.values())]
    assert [neu[d] for d in sorted(neu)] == reihe


def test_nummern_wie_beim_geruest_vergeben(wurzel):
    """Gegen nummern.json, wenn der Release-Ordner neben dem Repository liegt."""
    import pytest

    import ton_bauen
    pfad = os.path.join(os.path.dirname(wurzel), "Release", "Wortschatz", "_uebersetzung_p10_20", "nummern.json")
    if not os.path.exists(pfad):
        pytest.skip("Release-Ordner nicht da")
    vergeben = json.load(io.open(pfad, encoding="utf-8"))["eintraege"]
    assert len(vergeben) == LETZTE - ERSTE + 1
    emir = ton_bauen.nur_emir()
    for v in vergeben:
        if _nummer(v["datei"]) in FREI:
            assert v["key"] not in emir, v
            continue
        assert emir[v["key"]] == {"key": v["key"], "datei": v["datei"], "text": v["text"]}, v


def test_was_frei_bleibt_steht_in_offen():
    import offen_p1020
    import ton_bauen
    emir = ton_bauen.nur_emir()
    assert offen_p1020.TON == {"smijeh je najbolji lijek."}
    assert "smijeh je najbolji lijek." not in emir
    # Das Wort selbst hat Emir neu gesprochen (Fassung A, wahl.json vom 07.11.2026)
    assert ERSTE <= _nummer(emir["smijeh"]["datei"]) <= LETZTE


def test_zusammengesetzte_anzeigen_haben_eigene_nummer():
    import ton_bauen
    emir = ton_bauen.nur_emir()
    for bs in ZUSAMMENGESETZT:
        e = emir[ton_bauen.schluessel_alle(bs)]
        assert e["text"] == bs and ERSTE <= _nummer(e["datei"]) <= LETZTE, e
    for k in VOM_05_11:
        assert ERSTE <= _nummer(emir[k]["datei"]) <= LETZTE, emir[k]


def test_produzni_kabel_spricht_emir():
    """Aus produžni kabl wurde produžni kabel (b2_2_entscheidungen.md): neue Aufnahme,
    die alte von Goran (w2278) spielt fuer das Wort nicht mehr."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    assert emir["produžni kabel"] == {"key": "produžni kabel", "datei": "w5317.mp3", "text": "produžni kabel"}
    assert "produžni kabl" not in {p["key"] for p in ton_bauen.sammle()}


def test_huelle_hat_jede_datei():
    import pytest

    import ton_bauen
    import ton_pruefen
    huelle = ton_pruefen._huelle_audio()
    if not huelle:
        pytest.skip("Huelle nicht da")
    for datei in _im_bereich(ton_bauen.nur_emir()):
        pfad = os.path.join(huelle, datei)
        assert os.path.isfile(pfad) and os.path.getsize(pfad) >= ton_pruefen.MINDEST, datei
    for n in FREI:
        assert not os.path.exists(os.path.join(huelle, "w%04d.mp3" % n)), n


def test_keine_emir_datei_im_oeffentlichen_ordner(wurzel):
    import ton_bauen
    for datei in _im_bereich(ton_bauen.nur_emir()):
        assert not os.path.exists(os.path.join(wurzel, "web", "audio", datei)), datei
