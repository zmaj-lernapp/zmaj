# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026): Grammatik-Lektionen.

V12 (F8 ja, "ja ist genitiv"): In der Lektion Praepositionen standen iznad,
ispod und između in der Zeile Instrumental. Die App benutzt danach ueberall
den Genitiv („ispod stola“, „iznad grada“, „između tebe i brata“), das
Beispiel „između kuća“ passte nur zufaellig (Genitiv Mehrzahl). Jetzt stehen
die drei beim Genitiv, mit dem Beispiel „ispod stola, između kuće i škole“.
Die Uebung „Sjedim ___ tebe i brata.“ ist Genitiv und passt jetzt zur Tabelle.

S4 (F21 ja): Die Instrumental-Regel sagte „-em nur nach j, č, š, ž“, die App
schreibt aber auch čekićem und želucem. Jetzt: nach c, č, ć, dž, đ, j, lj, nj,
š, ž + em, in allen 8 Sprachen.
"""

S4_BUCHSTABEN = "c, č, ć, dž, đ, j, lj, nj, š, ž"
S4_IN_SPRACHE = {
    "de": "nach ", "en": "after ", "sv": "efter ", "da": "efter ",
    "nb": "etter ", "nl": "na ", "fr": "après ", "tr": "",
}


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


def test_s4_instrumental_em_nach_allen_weichen_lauten(alle_daten, grunddaten):
    assert set(alle_daten) == set(S4_IN_SPRACHE), sorted(alle_daten)
    for code, daten in alle_daten.items():
        tabelle = _tabelle(daten["grammatik"]["faelle4"])
        regel = tabelle[1][3]
        assert (S4_IN_SPRACHE[code] + S4_BUCHSTABEN) in regel, (code, regel)
        assert "prijateljem" in regel and "+ om" in regel, (code, regel)
        assert "nach" not in regel or code == "de", (code, regel)
    # Die Woerter aus dem Bericht, die die Regel vorher nicht erklaerte
    # (b1_zanat „kuca čekićem“, „Imam tegobe sa želucem.“).
    import json
    alles = json.dumps(grunddaten, ensure_ascii=False)
    assert "čekićem" in alles and "želucem" in alles
