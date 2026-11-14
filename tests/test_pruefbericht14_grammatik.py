# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026): Grammatik-Lektionen.

V12 (F8 ja, "ja ist genitiv"): In der Lektion Praepositionen standen iznad,
ispod und između in der Zeile Instrumental. Die App benutzt danach ueberall
den Genitiv („ispod stola“, „iznad grada“, „između tebe i brata“), das
Beispiel „između kuća“ passte nur zufaellig (Genitiv Mehrzahl). Jetzt stehen
die drei beim Genitiv, mit dem Beispiel „ispod stola, između kuće i škole“.
Die Uebung „Sjedim ___ tebe i brata.“ ist Genitiv und passt jetzt zur Tabelle.
"""


def _tabelle(lektion):
    for teil in lektion["erklaerung"]:
        if isinstance(teil, dict) and "tabelle" in teil:
            return teil["tabelle"]
    raise AssertionError("keine Tabelle")


def _zeile(tabelle, fall):
    zeilen = [z for z in tabelle if z[0] == fall]
    assert len(zeilen) == 1, (fall, tabelle)
    return zeilen[0]


def test_v12_iznad_ispod_izmedju_beim_genitiv(grunddaten):
    tabelle = _tabelle(grunddaten["grammatik"]["praepositionen"])
    genitiv = _zeile(tabelle, "Genitiv")
    instrumental = _zeile(tabelle, "Instrumental")
    praep_gen = [p.strip() for p in genitiv[1].split(",")]
    praep_ins = [p.strip() for p in instrumental[1].split(",")]
    for p in ("iznad", "ispod", "između"):
        assert p in praep_gen, (p, genitiv)
        assert p not in praep_ins, (p, instrumental)
    assert "ispod stola, između kuće i škole" in genitiv[2], genitiv
    assert "između" not in instrumental[2], instrumental
    # Was beim Instrumental war, bleibt dort.
    assert praep_ins == ["s/sa", "pod", "pred", "za (hinter)"], instrumental
    assert instrumental[2] == "s bratom, pod stolom", instrumental


def test_v12_in_jeder_sprache(alle_daten, grunddaten):
    vorlage = _tabelle(grunddaten["grammatik"]["praepositionen"])
    for code, daten in alle_daten.items():
        tabelle = _tabelle(daten["grammatik"]["praepositionen"])
        # Genitiv-Zeile und Beispiele sind bosnisch und stehen ueberall gleich da.
        assert tabelle[1][1:] == vorlage[1][1:], code
        instrumental = tabelle[-1][1]
        for p in ("iznad", "ispod", "između"):
            assert p not in instrumental, (code, instrumental)
        if code != "de":
            # Die Zelle ist uebersetzt ("za (behind)"), kein deutscher Rest.
            assert "hinter" not in instrumental, (code, instrumental)
            assert instrumental.startswith("sa, pod, pred, za ("), (code, instrumental)


def test_v12_uebung_zwischen_passt(grunddaten):
    uebungen = [u for u in grunddaten["grammatik"]["praepositionen"]["uebungen"]
                if u["frage"].startswith("„Sjedim ___ tebe i brata.“")]
    assert len(uebungen) == 1, uebungen
    assert uebungen[0]["richtig"] == "između"
