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

Was auf Emir wartete (Release\\Wortschatz\\v111_wartet_auf_emir.md), hat seit dem
07.11.2026 eine Nummer ab w5317 (tests/test_paket1020_ton.py).
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
    # Dahinter stehen der Teil Beim Zahnarzt (w5206 bis w5316, tests/test_zahnarzt.py) und
    # seit dem 07.11.2026 die Pakete 10 bis 20 mit der Warteliste (w5317 bis w8952,
    # tests/test_paket1020_ton.py).
    assert max(_nummer(e["datei"]) for e in emir.values()) == 8952
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


def test_was_wartete_hat_jetzt_eine_nummer_hinter_dem_zahnarzt():
    """Seit dem 07.11.2026 hat Emir gesprochen, was wartete (Ton-Schritt der Pakete 10
    bis 20). Der Satz zu smijeh kam als letzter am 08.11.2026: Ajdin nimmt die alte
    Aufnahme w4691, jetzt w5331. tests/offen_p1020.json ist seitdem leer."""
    import offen_p1020
    import ton_bauen
    emir = ton_bauen.nur_emir()
    for k in WARTET:
        if k in offen_p1020.TON:
            assert k not in emir, k
        else:
            assert _nummer(emir[k]["datei"]) >= 5317, (k, emir[k])
    assert offen_p1020.TON == frozenset()
    assert emir["smijeh je najbolji lijek."]["datei"] == "w5331.mp3"


def test_keine_emir_datei_im_oeffentlichen_ordner(wurzel):
    import os

    import ton_bauen
    for e in ton_bauen.nur_emir().values():
        assert not os.path.exists(os.path.join(wurzel, "web", "audio", e["datei"])), e
