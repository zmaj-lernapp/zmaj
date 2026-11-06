# -*- coding: utf-8 -*-
"""Wortschatz-Paket 6 (06.11.2026): Sektion 16 · Menschen und Gesellschaft.

147 Woerter je mit Beispielsatz, von Ajdin am 06.11.2026 durchgesehen
(Release\\Wortschatz\\paket_06.json, v111_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- ljekar ist kein zweites Wort „Arzt“, sondern die zweite Form von doktor
  (doktor / ljekar, Ajdin: „mach doktor/ ljekar“). Wer doktor gelernt hat, behaelt
  den Lernstand (UMBENANNT in web/index.html, wie kahva / kafa). Der fertige Satz
  „Moraš otići kod ljekara.“ steht als Eintrag im Level wer_ist_wer;
- izbori (Wahlen) neben izbor (Auswahl), moć (Macht) neben moći (können);
- rat, dova, mezarje und smijeh warten auf Emir (smijeh: w4690 ist ein Lachen statt des Wortes).
"""
import re

import pytest

LEVEL = ["menschen", "wer_ist_wer", "beziehungen", "stimmung_streit", "staat_politik",
         "gemeinde_gesellschaft", "krieg_recht", "wirtschaft", "technik_energie", "kultur_bildung",
         "glaube_gedenken", "alltag_information", "gruppe_netz"]
ERSTE_NUMMER, LETZTE_NUMMER = 3724, 5205      # Pakete 5 bis 9 zusammen, tests/test_paket59_ton.py

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "menschen": ["osoba", "roditelji", "supruga", "suprug", "momak", "djevojčica", "stranac", "stanovnik",
                 "građanin", "državljanin", "član"],
    "wer_ist_wer": ["partner", "ličnost", "karakter", "neprijatelj", "protivnik", "svjedok", "žrtva",
                    "korisnik", "stručnjak", "bolesnik"],
    "beziehungen": ["odnos", "veza", "brak", "razvod", "prijateljstvo", "povjerenje", "poštovanje", "radost",
                    "tuga", "mržnja", "hrabrost"],
    "stimmung_streit": ["raspoloženje", "iznenađenje", "svađa", "šala", "suza", "sjećanje", "navika",
                        "druženje", "razgovor"],
    "staat_politik": ["predsjednik", "vlada", "ministar", "izbori", "stranka", "politika", "političar",
                      "vlast", "zakon", "ustav", "kanton"],
    "gemeinde_gesellschaft": ["načelnik", "gradonačelnik", "društvo", "zajednica", "organizacija", "sloboda",
                              "pravda", "moć", "javnost", "protest", "štrajk"],
    "krieg_recht": ["mir", "vojska", "oružje", "napad", "borba", "sukob", "nasilje", "zločin", "ubistvo",
                    "zatvor", "sudija", "tužba", "presuda", "dozvola", "zabrana", "propis", "žalba",
                    "izbjeglica", "dijaspora"],
    "wirtschaft": ["rad", "kompanija", "preduzeće", "privreda", "tržište", "proizvod", "usluga", "ponuda",
                   "prodaja", "roba", "trgovina"],
    "technik_energie": ["zarada", "kriza", "direktor", "oprema", "materijal", "uređaj", "vozilo", "energija",
                        "tehnologija", "poljoprivreda"],
    "kultur_bildung": ["kultura", "umjetnost", "pisac", "izložba", "predstava", "historija", "nauka",
                       "obrazovanje", "nastava", "vježba"],
    "glaube_gedenken": ["islam", "musliman", "vjernik", "namaz", "molitva", "duša", "čudo", "sudbina",
                        "groblje", "spomenik", "zastava"],
    "alltag_information": ["hrana", "piće", "ime", "prezime", "adresa", "telefon", "priča", "informacija",
                           "podatak", "tema", "tekst", "sadržaj"],
    "gruppe_netz": ["stranica", "grupa", "klub", "projekat", "program", "sistem", "mreža", "fotografija",
                    "zgrada", "namještaj", "gužva"],
}

# Das Wort steckt im Bestand als zweite Form, nur sein Satz kommt dazu.
NUR_SATZ = {
    "Moraš otići kod ljekara.": "doktor / ljekar",
}

# "auch" genau nach dem Paket, dazu bei Adjektiven die weitere Form aus "formen".
AUCH = {
    "momak": ["dečko"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "preduzeće": ["poduzeće"], "stranica": ["strana"], "projekat": ["projekt"],
}

# Partner je Wort, wie im Paket.
PARTNER = {}

# Warten auf Emir (Release\\Wortschatz\\v111_wartet_auf_emir.md), noch nicht in der App
WARTET = ["rat", "dova", "mezarje", "smijeh"]


def _level(daten):
    k = {x["id"]: x for x in daten["kategorien"]}
    return [k[i] for i in LEVEL]


def _neu(daten):
    return [w for k in _level(daten) for w in k["words"]]


def _alle(daten):
    return [w for k in daten["kategorien"] for w in k["words"]]


def _paare(k):
    """(Wort, Satz) je Level; Saetze ohne eigenes Wort (NUR_SATZ) fallen weg."""
    liste = [w for w in k["words"] if w["bs"] not in NUR_SATZ]
    return list(zip(liste[0::2], liste[1::2]))


def test_jedes_wort_steht_vor_seinem_beispielsatz(grunddaten):
    for k in _level(grunddaten):
        assert k["reihenfolge"] is True, k["id"]
        assert 16 <= len(k["words"]) <= 40, k["id"]
        assert [w["bs"] for w, _ in _paare(k)] == WOERTER[k["id"]], k["id"]
        for wort, satz in _paare(k):
            assert re.search(r"[.!?]$", satz["bs"]) and re.search(r"[.!?]$", satz["de"]), satz
            assert satz["bs"][:1].isupper() and satz["de"][:1].isupper(), satz
            assert "partner" not in satz and "auch" not in satz, satz
            assert satz["bs"] != wort["bs"], satz


def test_auch_genau_nach_dem_paket(grunddaten):
    """Feld "auch" aus dem Paket, dazu die Formen aus "formen" (weiblich, saechlich)."""
    neu = {w["bs"]: w for w in _neu(grunddaten)}
    assert {b: w["auch"] for b, w in neu.items() if w.get("auch")} == AUCH
    for w in neu.values():
        formen = [f.strip() for f in w["bs"].split(" / ")]
        for a in w.get("auch", []):
            assert a not in formen, (w["bs"], a)


@pytest.mark.parametrize("wort, form", sorted((w, f) for w, l in ZAEHLT_NICHT.items() for f in l))
def test_was_ajdin_ausgeschlossen_hat_zaehlt_nicht(grunddaten, wort, form):
    """Beim Tippen zaehlt das Wort, sein "auch" und jedes andere Wort mit derselben
    Bedeutung (annehmbar() in web/index.html). Die Form darf in keinem davon stehen;
    als eigenes Wort mit anderer Bedeutung darf es sie geben (strana, dići)."""
    w = {x["bs"]: x for x in _neu(grunddaten)}[wort]
    assert form not in w.get("auch", []) and form not in w["bs"].split(" / ")
    assert w.get("partner") != form
    for x in _alle(grunddaten):
        if form in x["bs"].split(" / ") or form in x.get("auch", []):
            assert x["de"] != w["de"], (form, x["bs"])


def test_was_auf_emir_wartet_steht_nicht_in_der_app(grunddaten):
    """Release\\Wortschatz\\v111_wartet_auf_emir.md: ohne neue Aufnahme kein Eintrag,
    und kein Partner zeigt ins Leere."""
    bs = {w["bs"] for w in _alle(grunddaten)}
    for wort in WARTET:
        assert wort not in bs, wort
    for w in _alle(grunddaten):
        if w.get("partner"):
            assert w["partner"] in bs, w["bs"]


def test_gleiche_bedeutung_im_neuen_teil_nur_bei_paaren(alle_daten):
    for code, daten in alle_daten.items():
        alle = _alle(daten)
        paare = {frozenset((w["bs"], w["partner"])) for w in alle if w.get("partner")}
        neu = {w["bs"] for w in _neu(daten)}
        nach = {}
        for w in alle:
            nach.setdefault(w["de"].strip().lower().rstrip(".!?…  \u00a0"), []).append(w["bs"])
        for bedeutung, liste in nach.items():
            if len(liste) < 2 or not neu & set(liste):
                continue
            if set(liste) == {"Upomoć!", "pomoć"}:
                continue     # „Hilfe!“ im Notfall und „Hilfe“ (Paket 5): Ajdins Bedeutungen
            assert len(liste) == 2 and frozenset(liste) in paare, (code, bedeutung, liste)


def _teile_gleich(a, b):
    def norm(s):
        return s.strip().lower().rstrip(".!?…  \u00a0")

    def kern(teil):
        return norm(re.sub(r"\s*\([^()]*\)$", "", teil.strip()))

    ta = [norm(x) for x in a.split(" / ")]
    tb = [norm(x) for x in b.split(" / ")]
    gleich = set(ta) & set(tb)
    gleich |= {x for x in ta if not x.endswith(")")} & {kern(x) for x in tb}
    gleich |= {x for x in tb if not x.endswith(")")} & {kern(x) for x in ta}
    return gleich


def test_teilbedeutungen_im_level_nur_wie_im_deutschen(alle_daten, grunddaten):
    """Wie in tests/test_paket2.py: zwei Woerter eines Levels duerfen in einer Sprache nur
    dann teilweise gleich heissen, wenn das Deutsche es auch tut."""
    de = {(k["id"], w["bs"]): w["de"] for k in grunddaten["kategorien"] for w in k["words"]}
    gefunden = []
    for code, daten in alle_daten.items():
        alle = _alle(daten)
        paare = {frozenset((w["bs"], w["partner"])) for w in alle if w.get("partner")}
        for k in _level(daten):
            for i, a in enumerate(k["words"]):
                for b in k["words"][i + 1:]:
                    if frozenset((a["bs"], b["bs"])) in paare:
                        continue
                    gleich = _teile_gleich(a["de"], b["de"])
                    if gleich and not _teile_gleich(de[(k["id"], a["bs"])], de[(k["id"], b["bs"])]):
                        gefunden.append((code, k["id"], a["bs"], b["bs"], sorted(gleich)))
    assert not gefunden, gefunden


def test_jedes_wort_und_jeder_satz_hat_emirs_ton(grunddaten, wurzel):
    """Gegen ton_nur_emir.json und, wenn die Huelle daneben liegt, die Datei dort.
    Vorhandene Aufnahmen (index.json oder aeltere Nummern) gelten auch."""
    import io
    import json
    import os

    import ton_bauen
    import ton_pruefen
    emir = ton_bauen.nur_emir()
    index = {e["key"]: e for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                    encoding="utf-8"))["toene"]}
    huelle = ton_pruefen._huelle_audio()
    ohne = []
    for w in _neu(grunddaten):
        schluessel = [ton_bauen.schluessel(w["bs"])]
        if " / " in w["bs"]:
            schluessel.insert(0, ton_bauen.schluessel_alle(w["bs"]))
        for k in schluessel:
            e = emir.get(k) or index.get(k)
            if not e:
                ohne.append((w["id"], k))
                continue
            assert not (k in emir and k in index), k
            if k in emir and huelle:
                pfad = os.path.join(huelle, e["datei"])
                assert os.path.isfile(pfad) and os.path.getsize(pfad) >= ton_pruefen.MINDEST, (w["id"], e)
            if k in emir:
                assert not os.path.exists(os.path.join(wurzel, "web", "audio", e["datei"])), e
    assert not ohne, ohne[:20]


def test_sektion_und_level(grunddaten):
    s = grunddaten["sektionen"]
    assert s[15]["id"] == "menschengesellschaft" and s[15]["label"] == "Sektion 16 · Menschen und Gesellschaft"
    assert [k["id"] for k in grunddaten["kategorien"] if k["sektion"] == "menschengesellschaft"] == LEVEL
    ids = [k["id"] for k in grunddaten["kategorien"]]
    assert ids[ids.index("menschen") - 1] == "hilfe_hindernis", "direkt hinter Sektion 15"
    assert list(WOERTER) == LEVEL


def test_doktor_ljekar_ist_ein_wort(alle_daten, grunddaten, index_html):
    w = [x for x in _alle(grunddaten) if x["de"] == "Arzt"]
    assert [x["bs"] for x in w] == ["doktor / ljekar"]
    assert w[0]["id"] == "arzt:doktor / ljekar"
    assert "'arzt:doktor': 'arzt:doktor / ljekar'" in index_html
    assert not [x for x in _alle(grunddaten) if x["bs"] in ("doktor", "ljekar")]
    # Der Satz bleibt nutzbar, Ton vorhanden
    k = next(x for x in grunddaten["kategorien"] if x["id"] == "wer_ist_wer")
    assert "Moraš otići kod ljekara." in [x["bs"] for x in k["words"]]
    for code, daten in alle_daten.items():
        assert len({x["de"] for x in _alle(daten) if x["bs"] == "doktor / ljekar"}) == 1, code


def test_gebet_und_friedhof_nach_ajdins_antwort(grunddaten):
    w = {x["bs"]: x for x in _alle(grunddaten)}
    assert w["molitva"]["de"] == "Bittgebet (allgemein)"
    assert w["groblje"]["de"] == "Friedhof"
    assert w["momak"]["auch"] == ["dečko"]
