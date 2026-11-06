# -*- coding: utf-8 -*-
"""Wortschatz-Paket 9 (06.11.2026): Sektion 17 · Wie, wo und wann.

146 Woerter je mit Beispielsatz, von Ajdin am 06.11.2026 durchgesehen
(Release\\Wortschatz\\paket_09.json, v111_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Adjektive zeigen die maennliche Form, weibliche und saechliche zaehlen ("auch").
  Damit stehen važan und važno, čist und čisto, topao und toplo, hladan und hladno,
  opasan und opasno, rani und rana, stran und strana nie zusammen in einer Auswahl;
- sav und cijeli, tu und ovdje, tako und ovako, vrlo / veoma und jako heissen teilweise
  gleich: NIE_NEBENEINANDER in web/index.html haelt sie aus derselben Auswahl, beim
  Tippen zaehlt das andere Wort trotzdem nicht;
- zapravo / ustvari ist ein Wort, der Ton aus beiden Aufnahmen zusammengesetzt;
- mrtav, uopšte, naime / jer, poput / kao und ukupno warten auf Emir.
"""
import re

import pytest

LEVEL = ["wichtig_bekannt", "ganz_viele", "frueher_spaeter", "innen_aussen", "eigenschaften",
         "hier_dort", "wann_wie_oft", "wie_sehr", "wie_man_es_meint", "saetze_verbinden",
         "praepositionen_mehr", "fuerwoerter"]
ERSTE_NUMMER, LETZTE_NUMMER = 3724, 5205      # Pakete 5 bis 9 zusammen, tests/test_paket59_ton.py

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "wichtig_bekannt": ["važan", "bitan", "značajan", "glavni", "poznat", "nepoznat", "neophodan", "odgovoran",
                        "odličan", "sjajan", "uspješan", "koristan", "normalan", "pozitivan", "negativan",
                        "jasan"],
    "ganz_viele": ["sav", "cijeli", "mnogi", "razni", "različit", "određen", "jedini", "brojan", "ukupan",
                   "potpun", "dovoljan", "vlastit", "zajednički"],
    "frueher_spaeter": ["posljednji", "prošli", "sljedeći", "bivši", "današnji", "prethodni", "budući",
                        "sadašnji", "rani", "dnevni", "redovan", "konačan"],
    "innen_aussen": ["javni", "privatan", "lokalni", "vanjski", "unutrašnji", "gornji", "donji", "srednji",
                     "blizak", "dalek", "stran"],
    "eigenschaften": ["čist", "živ", "snažan", "moderan", "topao", "hladan", "dubok", "ogroman", "opasan",
                      "kriv", "ljudski", "prirodan", "ženski", "muški", "hitan", "čest"],
    "hier_dort": ["tu", "ovdje", "tamo", "gore", "dolje", "negdje", "nigdje", "naprijed", "nazad"],
    "wann_wie_oft": ["onda", "zatim", "nekad", "odjednom", "davno", "stalno", "trenutno", "prvo", "skoro"],
    "wie_sehr": ["tako", "ovako", "vrlo / veoma", "toliko", "sasvim", "nikako", "nekako", "pomalo", "rado",
                 "otprilike", "jedva", "baš", "čak", "bar", "ni"],
    "wie_man_es_meint": ["zaista", "ipak", "inače", "uglavnom", "vjerovatno", "zapravo / ustvari", "svakako",
                         "valjda"],
    "saetze_verbinden": ["kao", "pa", "što", "iako", "ukoliko", "dakle", "međutim", "odnosno", "čim", "pošto",
                         "neka", "evo"],
    "praepositionen_mehr": ["po", "nakon", "uz", "protiv", "preko", "tokom", "pred", "među", "osim", "umjesto",
                            "unutar", "izvan", "radi"],
    "fuerwoerter": ["sebe", "taj", "svoj", "neki", "neko", "njihov", "takav", "kakav", "ovakav", "nikakav",
                    "svako", "oba"],
}

# Das Wort steckt im Bestand als zweite Form, nur sein Satz kommt dazu.
NUR_SATZ = {}

# "auch" genau nach dem Paket, dazu bei Adjektiven die weitere Form aus "formen".
AUCH = {
    "važan": ["važna", "važno"], "bitan": ["bitna", "bitno"], "značajan": ["značajna", "značajno"],
    "glavni": ["glavna", "glavno"], "poznat": ["poznata", "poznato"], "nepoznat": ["nepoznata", "nepoznato"],
    "neophodan": ["neophodna", "neophodno"], "odgovoran": ["odgovorna", "odgovorno"],
    "odličan": ["odlična", "odlično"], "sjajan": ["sjajna", "sjajno"], "uspješan": ["uspješna", "uspješno"],
    "koristan": ["korisna", "korisno"], "normalan": ["normalna", "normalno"],
    "pozitivan": ["pozitivna", "pozitivno"], "negativan": ["negativna", "negativno"],
    "jasan": ["jasna", "jasno"], "sav": ["sva", "sve"], "cijeli": ["cijela", "cijelo"],
    "mnogi": ["mnoge", "mnoga"], "razni": ["razne", "razna"], "različit": ["različita", "različito"],
    "određen": ["određena", "određeno"], "jedini": ["jedina", "jedino"], "brojan": ["brojni"],
    "ukupan": ["ukupna", "ukupno"], "potpun": ["potpuna", "potpuno"], "dovoljan": ["dovoljna", "dovoljno"],
    "vlastit": ["vlastiti", "vlastita", "vlastito"], "zajednički": ["zajednička", "zajedničko"],
    "posljednji": ["posljednja", "posljednje"], "prošli": ["prošla", "prošlo"],
    "sljedeći": ["sljedeća", "sljedeće"], "bivši": ["bivša", "bivše"], "današnji": ["današnja", "današnje"],
    "prethodni": ["prethodna", "prethodno"], "budući": ["buduća", "buduće"],
    "sadašnji": ["sadašnja", "sadašnje"], "rani": ["rana", "rano"], "dnevni": ["dnevna", "dnevno"],
    "redovan": ["redovna", "redovno"], "konačan": ["konačna", "konačno"], "javni": ["javna", "javno"],
    "privatan": ["privatna", "privatno"], "lokalni": ["lokalna", "lokalno"], "vanjski": ["vanjska", "vanjsko"],
    "unutrašnji": ["unutrašnja", "unutrašnje"], "gornji": ["gornja", "gornje"], "donji": ["donja", "donje"],
    "srednji": ["srednja", "srednje"], "blizak": ["bliska", "blisko"], "dalek": ["daleka", "daleko"],
    "stran": ["strana", "strano"], "čist": ["čista", "čisto"], "živ": ["živa", "živo"],
    "snažan": ["snažna", "snažno"], "moderan": ["moderna", "moderno"], "topao": ["topla", "toplo"],
    "hladan": ["hladna", "hladno"], "dubok": ["duboka", "duboko"], "ogroman": ["ogromna", "ogromno"],
    "opasan": ["opasna", "opasno"], "kriv": ["kriva", "krivo"], "ljudski": ["ljudska", "ljudsko"],
    "prirodan": ["prirodna", "prirodno"], "ženski": ["ženska", "žensko"], "muški": ["muška", "muško"],
    "hitan": ["hitna", "hitno"], "čest": ["česta", "često"], "nekad": ["nekada"], "bar": ["barem"],
    "zapravo / ustvari": ["u stvari"], "taj": ["ta", "to"], "svoj": ["svoja", "svoje"],
    "neki": ["neka", "neko"], "njihov": ["njihova", "njihovo"], "takav": ["takva", "takvo"],
    "kakav": ["kakva", "kakvo"], "ovakav": ["ovakva", "ovakvo"], "nikakav": ["nikakva", "nikakvo"],
    "oba": ["obje"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "određen": ["određeni"], "ukupan": ["ukupni"], "potpun": ["potpuni"], "vlastit": ["sopstven"],
    "konačan": ["konačni"], "privatan": ["privatni"], "stran": ["strani"], "nazad": ["natrag"],
}

# Partner je Wort, wie im Paket.
PARTNER = {}

# Warten auf Emir (Release\\Wortschatz\\v111_wartet_auf_emir.md), noch nicht in der App
WARTET = ["mrtav", "uopšte", "naime / jer", "poput / kao", "ukupno"]


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
    assert s[16]["id"] == "wiewowann" and s[16]["label"] == "Sektion 17 · Wie, wo und wann"
    assert [k["id"] for k in grunddaten["kategorien"] if k["sektion"] == "wiewowann"] == LEVEL
    assert [k["id"] for k in grunddaten["kategorien"]][-len(LEVEL):] == LEVEL, "am Ende des Lernpfads"
    assert list(WOERTER) == LEVEL


def test_alle_sektionen(grunddaten):
    assert len(grunddaten["sektionen"]) == 17
    assert len(grunddaten["kategorien"]) == 166


@pytest.mark.parametrize("a, b", [("sav", "cijeli"), ("tu", "ovdje"), ("tako", "ovako"), ("vrlo / veoma", "jako")])
def test_nie_nebeneinander_in_der_auswahl(index_html, grunddaten, a, b):
    bs = {w["bs"] for w in _alle(grunddaten)}
    assert a in bs and b in bs
    assert "['%s', '%s']" % (a, b) in index_html
    w = {x["bs"]: x for x in _alle(grunddaten)}
    assert b not in w[a].get("auch", []) and a not in w[b].get("auch", []), "kein auch: das saehe beim Tippen mit"


@pytest.mark.parametrize("wort, form", [("važan", "važno"), ("čist", "čisto"), ("topao", "toplo"), ("hladan", "hladno"),
                                         ("opasan", "opasno"), ("rani", "rana"), ("rani", "rano"), ("stran", "strana"),
                                         ("hitan", "hitna"), ("neki", "neka"), ("neki", "neko"), ("čest", "često")])
def test_form_steht_im_auch_und_damit_nie_in_derselben_auswahl(grunddaten, wort, form):
    assert form in {x["bs"]: x for x in _alle(grunddaten)}[wort]["auch"]


def test_bedeutungen_getrennt_von_der_kurzform(alle_daten):
    for code, daten in alle_daten.items():
        u = {x["bs"]: x["de"] for x in _alle(daten)}
        for a, b in (("važan", "važno"), ("čist", "čisto"), ("topao", "toplo"), ("hladan", "hladno"),
                     ("opasan", "opasno")):
            assert u[a].strip().lower() != u[b].strip().lower(), (code, a, b)
