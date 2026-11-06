# -*- coding: utf-8 -*-
"""Wortschatz-Paket 5 (06.11.2026): Sektion 15 · Grundbegriffe, dazu mačak.

148 Hauptwoerter je mit Beispielsatz, von Ajdin am 06.11.2026 durchgesehen
(Release\\Wortschatz\\paket_05.json, v111_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 und 4 auf zwei Level verteilt;
- mačak steht im Level tiere mit "reihe" vor seinem Satz, mačka bleibt, maca
  kommt nicht (Ajdin: männlich und weiblich reicht);
- vijek / stoljeće ist ein Wort, der Ton ist aus beiden Aufnahmen zusammengesetzt;
- Beispiel, Fall, Form, Regel, Mittel und Person stehen schon als Grammatik-Begriffe
  da und bekommen als Woerter eigene Uebersetzungen ("woerter").
"""
import re

import pytest

LEVEL = ["ort_raum", "richtung_mass", "menge_teil", "reihe_wert", "anfang_ende",
         "das_leben", "grund_folge", "nutzen_schaden", "denken_entscheiden", "wahrheit_zweifel",
         "dinge_regeln", "hilfe_hindernis"]
ERSTE_NUMMER, LETZTE_NUMMER = 3724, 5205      # Pakete 5 bis 9 zusammen, tests/test_paket59_ton.py

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "ort_raum": ["mjesto", "strana", "prostor", "područje", "oblast", "centar", "sredina", "položaj", "smjer",
                 "krug", "površina", "blizina", "okolina"],
    "richtung_mass": ["zapad", "istok", "sjever", "jug", "dno", "tačka", "udaljenost", "dubina", "dužina",
                      "širina"],
    "menge_teil": ["dio", "broj", "većina", "količina", "iznos", "ostatak", "polovina", "trećina", "četvrtina",
                   "milion", "milijarda", "stotina"],
    "reihe_wert": ["niz", "vrsta", "par", "višak", "nedostatak", "prosjek", "gomila", "nivo", "vrijednost",
                   "razlika", "kilometar"],
    "anfang_ende": ["početak", "kraj", "period", "doba", "čas", "vijek / stoljeće", "decenija", "prošlost",
                    "nastavak", "završetak", "povratak", "odlazak", "godišnjica", "raspored", "sezona", "faza",
                    "korak"],
    "das_leben": ["život", "smrt", "rođenje", "djetinjstvo", "mladost", "starost", "snaga", "glas", "pogled",
                  "izgled", "pokret", "brzina"],
    "grund_folge": ["razlog", "uzrok", "posljedica", "cilj", "svrha", "namjera", "smisao", "značaj",
                    "značenje", "povod", "dokaz", "činjenica"],
    "nutzen_schaden": ["primjer", "slučaj", "uslov", "korist", "šteta", "prednost", "rizik", "uticaj",
                       "uspjeh", "gubitak"],
    "denken_entscheiden": ["odluka", "izbor", "ideja", "misao", "stav", "prijedlog", "savjet", "mogućnost",
                           "prilika", "čast", "potreba", "želja"],
    "wahrheit_zweifel": ["volja", "pažnja", "sumnja", "istina", "laž", "stvarnost", "tajna", "zaključak",
                         "pojam", "pamet"],
    "dinge_regeln": ["problem", "rješenje", "situacija", "stanje", "promjena", "razvoj", "napredak", "pokušaj",
                     "postupak", "proces", "način", "oblik", "pravilo", "znak", "trag"],
    "hilfe_hindernis": ["mjera", "sredstvo", "uloga", "obaveza", "pomoć", "podrška", "zaštita", "sigurnost",
                        "napor", "trud", "teškoća", "prepreka", "izazov", "aktivnost"],
}

# Das Wort steckt im Bestand als zweite Form, nur sein Satz kommt dazu.
NUR_SATZ = {}

# "auch" genau nach dem Paket, dazu bei Adjektiven die weitere Form aus "formen".
AUCH = {
    "uslov": ["uvjet"], "uticaj": ["utjecaj"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "okolina": ["okolica"],
}

# Partner je Wort, wie im Paket.
PARTNER = {}

# Warten auf Emir (Release\\Wortschatz\\v111_wartet_auf_emir.md), noch nicht in der App
WARTET = ["rub", "ivica", "poteškoća"]


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
    assert s[14]["id"] == "grundbegriffe" and s[14]["label"] == "Sektion 15 · Grundbegriffe"
    assert [k["id"] for k in grunddaten["kategorien"] if k["sektion"] == "grundbegriffe"] == LEVEL
    ids = [k["id"] for k in grunddaten["kategorien"]]
    assert ids[ids.index("ort_raum") - 1] == "arbeitsplatz", "direkt hinter Sektion 14"
    assert list(WOERTER) == LEVEL


def test_macak_im_level_tiere(alle_daten, grunddaten):
    k = next(x for x in grunddaten["kategorien"] if x["id"] == "tiere")
    assert k["reihe"] == ["mačak", "Naš mačak spava cijeli dan."]
    w = {x["bs"]: x for x in k["words"]}
    assert w["mačak"]["de"] == "Kater" and "partner" not in w["mačak"]
    alle = _alle(grunddaten)
    assert [x["de"] for x in alle if x["bs"] == "mačka"] == ["Katze"]
    assert not [x for x in alle if x["bs"] == "maca"]
    for code, daten in alle_daten.items():
        u = {x["bs"]: x["de"] for x in _alle(daten)}
        assert u["mačak"] != u["mačka"], code


def test_vijek_und_stoljece_sind_ein_wort(grunddaten):
    w = {x["bs"]: x for x in _alle(grunddaten)}
    assert w["vijek / stoljeće"]["de"] == "Jahrhundert / Zeitalter"
    assert "stoljeće" not in w and "vijek" not in w


@pytest.mark.parametrize("bs, soll", [("slučaj", "durum (olay)"), ("osoba", "kişi"), ("sredstvo", "araç / madde")])
def test_grammatik_begriffe_heissen_als_wort_anders(alle_daten, bs, soll):
    """tr Hâl, Şahıs und Orta gehoeren zur Grammatik."""
    assert {x["bs"]: x["de"] for x in _alle(alle_daten["tr"])}[bs] == soll


def test_teskoca_ist_die_ernste_schwierigkeit(grunddaten):
    w = {x["bs"]: x for x in _alle(grunddaten)}
    assert w["teškoća"]["de"] == "Schwierigkeit (ernst)"
    assert w["strana"]["de"] == "Seite (Richtung)"
