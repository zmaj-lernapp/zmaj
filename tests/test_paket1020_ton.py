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

w5331, der Satz zu smijeh, war bis zum 08.11.2026 frei. Ajdin hat die alte Aufnahme w4691
angehoert und genommen (paket_06_staging\\_alt_vor_smijeh_2026-11-06), sie liegt jetzt als
w5331 in der Huelle; tests/offen_p1020.json ist leer.

Zurueckgezogen am 08.11.2026: w5562 (nego i) und w8899 (nego i / već i). Ajdin: „nimm es
nur rein in einem ganzen satz nur so hört es sich sehr komisch an“. Das Wort ist aus der
App heraus, sein Satz w5563 bleibt. Die Nummern werden nicht neu vergeben, die Dateien
liegen nicht mehr in audio_emir/ (app_bauen.py warnte sonst bei jedem Bau).

Dahinter seit dem 14.11.2026: w8953 und w8954, kolegica statt koleginica (Pruefbericht 1.4,
S2/F19). Emir hat das Wort und den Satz neu gesprochen (Stimme_Emir_neu\\nachbesserung_2026-11-14,
Ajdin: „passt“). Die alten Aufnahmen w2012 und w2135 bleiben in web/audio/index.json stehen,
wie w2278 bei produžni kabl, und spielen nicht mehr.

Und w8955, nana / metvica mit beiden Formen (Pruefbericht 1.4, B6/F17 b): Emir spricht
„nana, metvica.“ wie kahva / kafa (Stimme_Emir_neu\\nachbesserung_2026-11-14\\nana_metvica,
Ajdin: „Nimm die neue fassung“). w0089 „nana“ (auch Oma) und w1717 „nana (auch: metvica)“
bleiben in web/audio/index.json stehen.

Danach seit dem 16.11.2026 w8956 bis w9048: die 93 Antworten der Grammatik-Uebungen,
die die App nach der Antwort spricht (Stimme_Emir_neu\\nachbesserung_2026-11-15_grammatik,
Ko in Fassung C2, plačem in K2). Die prueft tests/test_grammatik_ton.py.

Und ebenfalls seit dem 16.11.2026 als letzte w9049 bis w9871: die 823 Woerter, die nur in den
20 B1-Lesetexten stehen und beim Antippen still blieben (Stimme_Emir_neu\\geschichten_838_2026-11-16,
Offen-Liste 6a). Die prueft tests/test_geschichtenwoerter_ton.py.
"""
import io
import json
import os

ERSTE, LETZTE = 5317, 8952
ZURUECKGEZOGEN = {5562, 8899}
ZUSAMMENGESETZT = ["naime / jer", "poput / kao"]
VOM_05_11 = ["rub", "rat", "mrtav", "naime", "poput"]
KOLEGICA = {"kolegica": ("w8953.mp3", "kolegica"),
            "ovo je moja kolegica.": ("w8954.mp3", "Ovo je moja kolegica.")}
NANA_METVICA = {"nana / metvica": ("w8955.mp3", "nana / metvica")}
DAHINTER = dict(KOLEGICA, **NANA_METVICA)
GRAMMATIK_ERSTE, GRAMMATIK_LETZTE = 8956, 9048       # tests/test_grammatik_ton.py
GESCHICHTEN_LETZTE = 9871                            # tests/test_geschichtenwoerter_ton.py


def _nummer(datei):
    import ton_bauen
    return ton_bauen.dateinummer(datei)       # auch fuenfstellig (w10059), 21.11.2026


def _im_bereich(emir):
    return {e["datei"]: k for k, e in emir.items() if ERSTE <= _nummer(e["datei"]) <= LETZTE}


def test_nummern_lueckenlos_und_in_der_reihenfolge_der_app():
    import ton_bauen
    emir = ton_bauen.nur_emir()
    neu = _im_bereich(emir)
    assert sorted(neu) == ["w%04d.mp3" % n for n in range(ERSTE, LETZTE + 1) if n not in ZURUECKGEZOGEN]
    # Dahinter die drei Aufnahmen vom 14.11.2026 (kolegica, test_kolegica_spricht_emir,
    # und nana / metvica, tests/test_pruefbericht14_antworten.py), danach nur noch die
    # Grammatik-Antworten (16.11.2026, tests/test_grammatik_ton.py) und die Woerter der
    # B1-Lesetexte (16.11.2026, tests/test_geschichtenwoerter_ton.py), seit dem 27.11.2026
    # K2 und K7 und als letzte die Hose (w9872 bis w10058, w10094, tests/test_k2_ton.py).
    # ohne die eigenen Toene je Bedeutung (w10059 ff., tests/test_ton_bedeutung.py, 21.11.2026)
    import ton_bedeutung
    from k2_einbau import TON_ERSTE, TON_HOSE
    eigene = set(ton_bedeutung.eigene_schluessel())
    assert TON_ERSTE == GESCHICHTEN_LETZTE + 1
    assert max(_nummer(e["datei"]) for k, e in emir.items() if k not in eigene) == _nummer(TON_HOSE["datei"])
    nach = sorted(e["datei"] for e in emir.values() if LETZTE < _nummer(e["datei"]) < GRAMMATIK_ERSTE)
    assert nach == sorted(d for d, _ in DAHINTER.values()), nach
    for key, (datei, text) in DAHINTER.items():
        assert emir[key] == {"key": key, "datei": datei, "text": text}
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
        if _nummer(v["datei"]) in ZURUECKGEZOGEN:
            assert v["key"] not in emir, v
            continue
        assert emir[v["key"]] == {"key": v["key"], "datei": v["datei"], "text": v["text"]}, v


def test_smijeh_satz_hat_die_alte_aufnahme_und_offen_ist_leer():
    """Ajdin, 08.11.2026: Der Satz zu smijeh nimmt die alte Aufnahme w4691, als w5331."""
    import offen_p1020
    import ton_bauen
    emir = ton_bauen.nur_emir()
    assert offen_p1020.TON == frozenset()
    assert emir["smijeh je najbolji lijek."] == {"key": "smijeh je najbolji lijek.", "datei": "w5331.mp3",
                                                 "text": "Smijeh je najbolji lijek."}
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


def test_kolegica_spricht_emir(wurzel):
    """Aus koleginica wurde kolegica (Ajdin, Pruefbericht 1.4, S2/F19): Wort und Satzbau-Satz
    mit neuer Aufnahme von Emir, wie bei produžni kabel. Der Lueckensatz „Ovo je moja ___.“
    spricht denselben fertigen Satz. web/audio/index.json bleibt, wie es war."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    for key, (datei, text) in KOLEGICA.items():
        assert emir[key] == {"key": key, "datei": datei, "text": text}
    keys = {p["key"] for p in ton_bauen.sammle()}
    assert set(KOLEGICA) <= keys
    assert "koleginica" not in keys and "ovo je moja koleginica." not in keys
    with io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8") as f:
        index = {e["key"]: e["datei"] for e in json.load(f)["toene"]}
    assert index["koleginica"] == "w2012.mp3" and index["ovo je moja koleginica."] == "w2135.mp3"
    assert not set(KOLEGICA) & set(index)


def test_huelle_hat_jede_datei():
    import pytest

    import ton_bauen
    import ton_pruefen
    huelle = ton_pruefen._huelle_audio()
    if not huelle:
        pytest.skip("Huelle nicht da")
    for datei in list(_im_bereich(ton_bauen.nur_emir())) + [d for d, _ in DAHINTER.values()]:
        pfad = os.path.join(huelle, datei)
        assert os.path.isfile(pfad) and os.path.getsize(pfad) >= ton_pruefen.MINDEST, datei
    for n in ZURUECKGEZOGEN:
        assert not os.path.exists(os.path.join(huelle, "w%04d.mp3" % n)), n


def test_keine_emir_datei_im_oeffentlichen_ordner(wurzel):
    import ton_bauen
    for datei in list(_im_bereich(ton_bauen.nur_emir())) + [d for d, _ in DAHINTER.values()]:
        assert not os.path.exists(os.path.join(wurzel, "web", "audio", datei)), datei
