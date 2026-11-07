# -*- coding: utf-8 -*-
"""Gemeinsame Pruefungen fuer die Wortschatz-Pakete 10 bis 20 (Stufe B2, 07.11.2026).

Jede Datei tests/test_paket10.py bis test_paket20.py nennt ihre Level, Woerter, "auch",
"zaehlt_nicht" und "partner" genau nach dem Paket (Release\\Wortschatz\\paket_NN.json, von
Ajdin am 07.11.2026 durchgesehen) und holt sich die Pruefungen hier mit
"from paket1020_pruefung import *". Gelesen wird ueber request.module, also immer mit den
Angaben der Datei, in der der Test laeuft. Es sind dieselben Pruefungen wie in
tests/test_paket5.py bis test_paket9.py, nur einmal geschrieben statt elfmal.

Emirs Ton kommt im eigenen Schritt: was noch keinen hat, steht in tests/offen_p1020.json.
"""
import re

import offen_p1020

__all__ = ["pytest_generate_tests", "test_jedes_wort_steht_vor_seinem_beispielsatz", "test_auch_genau_nach_dem_paket",
           "test_was_ajdin_ausgeschlossen_hat_zaehlt_nicht", "test_partner_an_beiden_woertern",
           "test_gleiche_bedeutung_im_neuen_teil_nur_bei_paaren", "test_teilbedeutungen_im_level_nur_wie_im_deutschen",
           "test_jedes_wort_und_jeder_satz_hat_emirs_ton", "test_level_in_ihrer_sektion"]

# izvršiti hat seit Paket 19 zwei Partner (vršiti, izvršavati), alle drei heissen gleich
DREI_GLEICHE = {"izvršiti", "vršiti", "izvršavati"}


def _level(m, daten):
    k = {x["id"]: x for x in daten["kategorien"]}
    return [k[i] for i in m.LEVEL]


def _neu(m, daten):
    return [w for k in _level(m, daten) for w in k["words"]]


def _alle(daten):
    return [w for k in daten["kategorien"] for w in k["words"]]


def _paare(m, k):
    """(Wort, Satz) je Level; Saetze ohne eigenes Wort (NUR_SATZ) fallen weg."""
    liste = [w for w in k["words"] if w["bs"] not in m.NUR_SATZ]
    return list(zip(liste[0::2], liste[1::2]))


def pytest_generate_tests(metafunc):
    if "zaehlt_nicht_paar" in metafunc.fixturenames:
        z = getattr(metafunc.module, "ZAEHLT_NICHT", {})
        paare = sorted((w, f) for w, l in z.items() for f in l)
        metafunc.parametrize("zaehlt_nicht_paar", paare or [None], ids=[" - ".join(p) for p in paare] or ["keins"])


def test_jedes_wort_steht_vor_seinem_beispielsatz(grunddaten, request):
    m = request.module
    for k in _level(m, grunddaten):
        assert k["reihenfolge"] is True, k["id"]
        assert 16 <= len(k["words"]) <= 40, k["id"]
        assert [w["bs"] for w, _ in _paare(m, k)] == m.WOERTER[k["id"]], k["id"]
        for wort, satz in _paare(m, k):
            assert re.search(r"[.!?]$", satz["bs"]) and re.search(r"[.!?]$", satz["de"]), satz
            assert satz["bs"][:1].isupper() and satz["de"][:1].isupper(), satz
            assert "partner" not in satz and "auch" not in satz, satz
            assert satz["bs"] != wort["bs"], satz
        for w in k["words"]:
            if w["bs"] in m.NUR_SATZ:
                assert "partner" not in w and "auch" not in w, w
    assert list(m.WOERTER) == m.LEVEL


def test_auch_genau_nach_dem_paket(grunddaten, request):
    """Feld "auch" aus dem Paket, dazu die Formen aus "formen" (weiblich, saechlich)."""
    m = request.module
    neu = {w["bs"]: w for w in _neu(m, grunddaten)}
    assert {b: w["auch"] for b, w in neu.items() if w.get("auch")} == m.AUCH
    for w in neu.values():
        formen = [f.strip() for f in w["bs"].split(" / ")]
        for a in w.get("auch", []):
            assert a not in formen, (w["bs"], a)


def test_was_ajdin_ausgeschlossen_hat_zaehlt_nicht(grunddaten, request, zaehlt_nicht_paar):
    """Beim Tippen zaehlt das Wort, sein "auch" und jedes andere Wort mit derselben
    Bedeutung (annehmbar() in web/index.html). Die Form darf in keinem davon stehen;
    als eigenes Wort mit anderer Bedeutung darf es sie geben (začini neben začin)."""
    if zaehlt_nicht_paar is None:
        return
    m = request.module
    wort, form = zaehlt_nicht_paar
    w = {x["bs"]: x for x in _neu(m, grunddaten)}[wort]
    assert form not in w.get("auch", []) and form not in w["bs"].split(" / ")
    assert w.get("partner") != form
    for x in _alle(grunddaten):
        if form in x["bs"].split(" / ") or form in x.get("auch", []):
            assert x["de"] != w["de"], (form, x["bs"])


def test_partner_an_beiden_woertern(grunddaten, request):
    """"partner" genau nach dem Paket, auch beim Gegenstueck - bei einem Verb, das schon in
    der App stand, auch dort. Ausnahme izvršavati: es zeigt auf izvršiti, izvršiti aber auf
    vršiti (zwei Partner, die App liest in beide Richtungen)."""
    m = request.module
    neu = {w["bs"]: w for w in _neu(m, grunddaten)}
    alle = {w["bs"]: w for w in _alle(grunddaten)}
    assert {b: w["partner"] for b, w in neu.items() if w.get("partner")} == m.PARTNER
    for wort, gegen in m.PARTNER.items():
        assert gegen in alle, (wort, gegen)
        if wort == "izvršavati":
            assert alle["izvršiti"]["partner"] == "vršiti"
            continue
        assert alle[gegen].get("partner") == wort, (gegen, wort)


def test_gleiche_bedeutung_im_neuen_teil_nur_bei_paaren(alle_daten, request):
    """Zwei Woerter mit derselben Bedeutung sind in der Auswahl nicht zu unterscheiden.
    Im neuen Teil darf das nur ein Paar sein (in jeder Sprache)."""
    m = request.module
    for code, daten in alle_daten.items():
        alle = _alle(daten)
        paare = {frozenset((w["bs"], w["partner"])) for w in alle if w.get("partner")}
        neu = {w["bs"] for w in _neu(m, daten)}
        nach = {}
        for w in alle:
            nach.setdefault(w["de"].strip().lower().rstrip(".!?…   "), []).append(w["bs"])
        for bedeutung, liste in nach.items():
            if len(liste) < 2 or not neu & set(liste):
                continue
            if set(liste) == DREI_GLEICHE or set(liste) == {"Upomoć!", "pomoć"}:
                continue
            assert len(liste) == 2 and frozenset(liste) in paare, (code, bedeutung, liste)


def _teile_gleich(a, b):
    def norm(s):
        return s.strip().lower().rstrip(".!?…   ")

    def kern(teil):
        return norm(re.sub(r"\s*\([^()]*\)$", "", teil.strip()))

    ta = [norm(x) for x in a.split(" / ")]
    tb = [norm(x) for x in b.split(" / ")]
    gleich = set(ta) & set(tb)
    gleich |= {x for x in ta if not x.endswith(")")} & {kern(x) for x in tb}
    gleich |= {x for x in tb if not x.endswith(")")} & {kern(x) for x in ta}
    return gleich


def test_teilbedeutungen_im_level_nur_wie_im_deutschen(alle_daten, grunddaten, request):
    """Wie in tests/test_paket2.py: zwei Woerter eines Levels duerfen in einer Sprache nur
    dann teilweise gleich heissen, wenn das Deutsche es auch tut."""
    m = request.module
    de = {(k["id"], w["bs"]): w["de"] for k in grunddaten["kategorien"] for w in k["words"]}
    gefunden = []
    for code, daten in alle_daten.items():
        alle = _alle(daten)
        paare = {frozenset((w["bs"], w["partner"])) for w in alle if w.get("partner")}
        for k in _level(m, daten):
            for i, a in enumerate(k["words"]):
                for b in k["words"][i + 1:]:
                    if frozenset((a["bs"], b["bs"])) in paare:
                        continue
                    gleich = _teile_gleich(a["de"], b["de"])
                    if gleich and not _teile_gleich(de[(k["id"], a["bs"])], de[(k["id"], b["bs"])]):
                        gefunden.append((code, k["id"], a["bs"], b["bs"], sorted(gleich)))
    assert not gefunden, gefunden


def test_jedes_wort_und_jeder_satz_hat_emirs_ton(grunddaten, wurzel, request):
    """Gegen ton_nur_emir.json und, wenn die Huelle daneben liegt, die Datei dort.
    Vorhandene Aufnahmen (index.json oder aeltere Nummern) gelten auch. Bis zum
    Ton-Schritt fehlt er genau fuer die Schluessel in tests/offen_p1020.json."""
    import io
    import json
    import os

    import ton_bauen
    import ton_pruefen
    m = request.module
    emir = ton_bauen.nur_emir()
    index = {e["key"]: e for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                    encoding="utf-8"))["toene"]}
    huelle = ton_pruefen._huelle_audio()
    ohne = []
    for w in _neu(m, grunddaten):
        schluessel = [ton_bauen.schluessel(w["bs"])]
        if " / " in w["bs"]:
            schluessel.insert(0, ton_bauen.schluessel_alle(w["bs"]))
        for k in schluessel:
            e = emir.get(k) or index.get(k)
            if not e:
                if k not in offen_p1020.TON:
                    ohne.append((w["id"], k))
                continue
            assert not (k in emir and k in index), k
            if k in emir and huelle:
                pfad = os.path.join(huelle, e["datei"])
                assert os.path.isfile(pfad) and os.path.getsize(pfad) >= ton_pruefen.MINDEST, (w["id"], e)
            if k in emir:
                assert not os.path.exists(os.path.join(wurzel, "web", "audio", e["datei"])), e
    assert not ohne, ohne[:20]


def test_level_in_ihrer_sektion(grunddaten, request):
    """Die Level stehen in der Reihenfolge des Pakets in ihrer Sektion (18 bis 31, Stufe B2)."""
    m = request.module
    ids = [k["id"] for k in grunddaten["kategorien"]]
    sek = {k["id"]: k["sektion"] for k in grunddaten["kategorien"]}
    assert [i for i in ids if i in set(m.LEVEL)] == m.LEVEL
    assert {i: sek[i] for i in m.LEVEL} == m.SEKTION
    b2 = [s["id"] for s in grunddaten["sektionen"]][17:]
    for i in m.LEVEL:
        assert sek[i] in b2, i
