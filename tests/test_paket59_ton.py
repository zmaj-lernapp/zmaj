# -*- coding: utf-8 -*-
"""Wortschatz-Pakete 5 bis 9 (06.11.2026): Emir spricht die neuen Woerter und Saetze.

Die Aufnahmen hat ElevenLabs am 05.11.2026 erzeugt (Stimme Emir, dieselben
Einstellungen wie Paket 1 bis 4), sechs kurze Woerter am 06.11.2026 nachgeholt.
Sie liegen nur in der privaten Huelle unter audio_emir/, die Nummern stehen hier
in ton_nur_emir.json: w3724 bis w5205, in der Reihenfolge von ton_bauen.sammle().
w4690 (smijeh, ein Lachen statt des Wortes) und sein Satz w4691 sind seit dem
06.11.2026 zurueckgezogen; ihre Nummern bleiben frei. Ebenso w4114 (plakati, zweites a
zu lang) und sein Satz w4115 (e bei beba zu kurz).

doktor / ljekar, dozvoliti / dopustiti, dozvoljavati / dopuštati, vijek / stoljeće,
podići / podignuti und zapravo / ustvari sind aus fertigen Einzelaufnahmen
zusammengesetzt (keine neue Aufnahme); šutjeti / šutiti und vrlo / veoma hat Emir
mit beiden Formen gesprochen.

Was auf Emir wartet (Release\\Wortschatz\\v111_wartet_auf_emir.md), hat noch keine Nummer.
"""
ERSTE, LETZTE = 3724, 5205
ZURUECKGEZOGEN = {4114, 4115, 4690, 4691}
ZUSAMMENGESETZT = ["doktor / ljekar", "dozvoliti / dopustiti", "dozvoljavati / dopuštati", "podići / podignuti",
                   "vijek / stoljeće", "zapravo / ustvari"]
WARTET = ["ivica", "poteškoća", "dova", "mezarje", "dići", "dizati", "uopšte", "ukupno", "smijeh", "plakati",
          "živimo na rubu grada.", "moj dedo je bio u ratu.", "našli smo mrtvu pticu u bašti.",
          "kasnim na posao. naime, autobus se pokvario.", "želim biti poput svog babe.",
          "smijeh je najbolji lijek.", "zašto beba stalno plače?"]


def _nummer(datei):
    return int(datei[1:5])


def _im_bereich(emir):
    return {e["datei"]: k for k, e in emir.items() if ERSTE <= _nummer(e["datei"]) <= LETZTE}


def test_nummern_lueckenlos_und_in_der_reihenfolge_der_app():
    import ton_bauen
    emir = ton_bauen.nur_emir()
    neu = _im_bereich(emir)
    assert sorted(neu) == ["w%04d.mp3" % n for n in range(ERSTE, LETZTE + 1) if n not in ZURUECKGEZOGEN]
    # Dahinter steht nur noch der Teil Beim Zahnarzt (w5206 bis w5316, tests/test_zahnarzt.py).
    assert max(_nummer(e["datei"]) for e in emir.values()) == 5316
    reihe = [p["key"] for p in ton_bauen.sammle() if p["key"] in set(neu.values())]
    assert [neu[d] for d in sorted(neu)] == reihe


def test_zusammengesetzte_anzeigen_haben_eigene_nummer():
    import ton_bauen
    emir = ton_bauen.nur_emir()
    for bs in ZUSAMMENGESETZT + ["šutjeti / šutiti", "vrlo / veoma"]:
        e = emir[ton_bauen.schluessel_alle(bs)]
        assert e["text"] == bs and ERSTE <= _nummer(e["datei"]) <= LETZTE, e


def test_erste_form_behaelt_ihre_aufnahme():
    """doktor, dozvoliti und dozvoljavati spielen weiter, wenn eine Geschichte oder
    ein Wort nur die erste Form braucht."""
    import ton_bauen
    emir = ton_bauen.nur_emir()
    assert emir["dozvoliti"]["text"] == "dozvoliti / dopustiti" and _nummer(emir["dozvoliti"]["datei"]) < ERSTE
    assert emir["dozvoljavati"]["text"] == "dozvoljavati / dopuštati"
    assert _nummer(emir["dozvoljavati"]["datei"]) < ERSTE


def test_was_wartet_hat_keine_nummer():
    import ton_bauen
    emir = ton_bauen.nur_emir()
    for k in WARTET:
        assert k not in emir, k


def test_keine_emir_datei_im_oeffentlichen_ordner(wurzel):
    import os

    import ton_bauen
    for e in ton_bauen.nur_emir().values():
        assert not os.path.exists(os.path.join(wurzel, "web", "audio", e["datei"])), e
