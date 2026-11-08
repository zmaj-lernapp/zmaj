# -*- coding: utf-8 -*-
"""Wortschatz-Paket 7 (06.11.2026): 148 Verben fuer Sektion 10 · Tun und Lassen.

Von Ajdin am 06.11.2026 durchgesehen (Release\\Wortschatz\\paket_07.json,
v111_entscheidungen.md). Hier steht, was beim Einbau festgelegt wurde:

- zehn Level vor den Leveln aus Paket 8, hinter paare_mehr und vor passieren;
- dopustiti und dopuštati sind keine zweiten Woerter „erlauben“, sondern die zweite
  Form von dozvoliti und dozvoljavati (Bedeutung jetzt „erlauben / zulassen“). Der
  Lernstand zieht mit (UMBENANNT). Ihre fertigen Saetze stehen als Eintraege im
  Level entscheiden_annehmen;
- nositi bekommt am alten Wort partner ponijeti, povući hat zwei Partner;
- dići und dizati warten auf Emir, podići / podignuti ist ein Wort.
"""
import re

import pytest

import offen_p1020

LEVEL = ["sagen_betonen", "mitteilen_bitten", "fuehren_bringen", "heben_ziehen", "schaffen_erreichen",
         "starten_planen", "veraendern_herstellen", "ermoeglichen_entdecken", "entscheiden_annehmen", "aufhoeren_vermeiden"]
ERSTE_NUMMER, LETZTE_NUMMER = 3724, 5205      # Pakete 5 bis 9 zusammen, tests/test_paket59_ton.py

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "sagen_betonen": ["kazati", "tvrditi", "naglasiti", "naglašavati", "najaviti", "najavljivati", "spomenuti",
                      "spominjati", "potvrditi", "potvrđivati", "priznati", "priznavati", "izraziti",
                      "izražavati", "opisati", "opisivati"],
    "mitteilen_bitten": ["podsjetiti", "podsjećati", "upozoriti", "upozoravati", "obavijestiti",
                         "obavještavati", "predložiti", "predlagati", "preporučiti", "preporučivati",
                         "obećati", "obećavati", "pozdraviti", "pozdravljati", "moliti", "zamoliti",
                         "zatražiti", "zahtijevati"],
    "fuehren_bringen": ["voditi", "povesti", "dovesti", "dovoditi", "odvesti", "odvoditi", "odnijeti",
                        "odnositi", "prenijeti", "prenositi", "ponijeti", "predati", "predavati", "preuzeti",
                        "preuzimati"],
    "heben_ziehen": ["vući", "povući", "povlačiti", "podići / podignuti", "podizati", "spustiti", "spuštati",
                     "gurnuti", "gurati", "dodati", "dodavati", "izbaciti", "izbacivati", "izvaditi", "vaditi",
                     "oduzeti", "oduzimati", "pružiti", "pružati", "dići", "dizati"],
    "schaffen_erreichen": ["činiti", "učiniti", "stvoriti", "stvarati", "postići", "postizati", "ostvariti",
                           "ostvarivati", "izvršiti", "vršiti", "obaviti", "obavljati"],
    "starten_planen": ["pokrenuti", "pokretati", "započeti", "započinjati", "postaviti", "postavljati",
                       "održati", "održavati", "organizovati", "planirati"],
    "veraendern_herstellen": ["razviti", "razvijati", "povećati", "povećavati", "smanjiti", "smanjivati",
                              "poboljšati", "poboljšavati", "izgraditi", "graditi", "proizvesti",
                              "proizvoditi"],
    "ermoeglichen_entdecken": ["omogućiti", "omogućavati", "osigurati", "osiguravati", "uništiti",
                               "uništavati", "otkriti", "otkrivati", "pronaći", "pronalaziti"],
    "entscheiden_annehmen": ["prihvatiti", "prihvatati", "odbiti", "odbijati", "odabrati", "odabirati",
                             "odrediti", "određivati", "zaključiti", "zaključivati", "utvrditi", "utvrđivati",
                             "podržati", "podržavati", "pristati", "pristajati", "zabraniti", "zabranjivati"],
    "aufhoeren_vermeiden": ["prekinuti", "prekidati", "odustati", "odustajati", "napustiti", "napuštati",
                            "ispuniti", "ispunjavati", "izbjeći", "izbjegavati", "spriječiti", "sprječavati",
                            "zaustaviti", "zaustavljati", "provjeriti", "provjeravati", "dokazati",
                            "dokazivati"],
}

# Das Wort steckt im Bestand als zweite Form, nur sein Satz kommt dazu.
NUR_SATZ = {
    "Neću ti dopustiti da to uradiš.": "dozvoliti / dopustiti",
    "Roditelji mu ne dopuštaju da izlazi.": "dozvoljavati / dopuštati",
}

# "auch" genau nach dem Paket, dazu bei Adjektiven die weitere Form aus "formen".
AUCH = {
    "organizovati": ["organizirati"], "prihvatati": ["prihvaćati"], "sprječavati": ["sprečavati"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "spomenuti": ["pomenuti"], "spominjati": ["pominjati"], "podići / podignuti": ["dići"],
    "podizati": ["dizati"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "naglasiti": "naglašavati", "naglašavati": "naglasiti", "najaviti": "najavljivati",
    "najavljivati": "najaviti", "spomenuti": "spominjati", "spominjati": "spomenuti",
    "potvrditi": "potvrđivati", "potvrđivati": "potvrditi", "priznati": "priznavati", "priznavati": "priznati",
    "izraziti": "izražavati", "izražavati": "izraziti", "opisati": "opisivati", "opisivati": "opisati",
    "podsjetiti": "podsjećati", "podsjećati": "podsjetiti", "upozoriti": "upozoravati",
    "upozoravati": "upozoriti", "obavijestiti": "obavještavati", "obavještavati": "obavijestiti",
    "predložiti": "predlagati", "predlagati": "predložiti", "preporučiti": "preporučivati",
    "preporučivati": "preporučiti", "obećati": "obećavati", "obećavati": "obećati",
    "pozdraviti": "pozdravljati", "pozdravljati": "pozdraviti", "moliti": "zamoliti", "zamoliti": "moliti",
    "voditi": "povesti", "povesti": "voditi", "dovesti": "dovoditi", "dovoditi": "dovesti",
    "odvesti": "odvoditi", "odvoditi": "odvesti", "odnijeti": "odnositi", "odnositi": "odnijeti",
    "prenijeti": "prenositi", "prenositi": "prenijeti", "ponijeti": "nositi", "predati": "predavati",
    "predavati": "predati", "preuzeti": "preuzimati", "preuzimati": "preuzeti", "vući": "povući",
    "povući": "povlačiti", "povlačiti": "povući", "podići / podignuti": "podizati",
    "podizati": "podići / podignuti", "spustiti": "spuštati", "spuštati": "spustiti", "gurnuti": "gurati",
    "gurati": "gurnuti", "dodati": "dodavati", "dodavati": "dodati", "izbaciti": "izbacivati",
    "izbacivati": "izbaciti", "izvaditi": "vaditi", "vaditi": "izvaditi", "oduzeti": "oduzimati",
    "oduzimati": "oduzeti", "pružiti": "pružati", "pružati": "pružiti", "činiti": "učiniti",
    "učiniti": "činiti", "stvoriti": "stvarati", "stvarati": "stvoriti", "postići": "postizati",
    "postizati": "postići", "ostvariti": "ostvarivati", "ostvarivati": "ostvariti", "izvršiti": "vršiti",
    "vršiti": "izvršiti", "obaviti": "obavljati", "obavljati": "obaviti", "pokrenuti": "pokretati",
    "pokretati": "pokrenuti", "započeti": "započinjati", "započinjati": "započeti", "postaviti": "postavljati",
    "postavljati": "postaviti", "održati": "održavati", "održavati": "održati", "razviti": "razvijati",
    "razvijati": "razviti", "povećati": "povećavati", "povećavati": "povećati", "smanjiti": "smanjivati",
    "smanjivati": "smanjiti", "poboljšati": "poboljšavati", "poboljšavati": "poboljšati",
    "izgraditi": "graditi", "graditi": "izgraditi", "proizvesti": "proizvoditi", "proizvoditi": "proizvesti",
    "omogućiti": "omogućavati", "omogućavati": "omogućiti", "osigurati": "osiguravati",
    "osiguravati": "osigurati", "uništiti": "uništavati", "uništavati": "uništiti", "otkriti": "otkrivati",
    "otkrivati": "otkriti", "pronaći": "pronalaziti", "pronalaziti": "pronaći", "prihvatiti": "prihvatati",
    "prihvatati": "prihvatiti", "odbiti": "odbijati", "odbijati": "odbiti", "odabrati": "odabirati",
    "odabirati": "odabrati", "odrediti": "određivati", "određivati": "odrediti", "zaključiti": "zaključivati",
    "zaključivati": "zaključiti", "utvrditi": "utvrđivati", "utvrđivati": "utvrditi", "podržati": "podržavati",
    "podržavati": "podržati", "pristati": "pristajati", "pristajati": "pristati", "zabraniti": "zabranjivati",
    "zabranjivati": "zabraniti", "prekinuti": "prekidati", "prekidati": "prekinuti", "odustati": "odustajati",
    "odustajati": "odustati", "napustiti": "napuštati", "napuštati": "napustiti", "ispuniti": "ispunjavati",
    "ispunjavati": "ispuniti", "izbjeći": "izbjegavati", "izbjegavati": "izbjeći", "spriječiti": "sprječavati",
    "sprječavati": "spriječiti", "zaustaviti": "zaustavljati", "zaustavljati": "zaustaviti",
    "provjeriti": "provjeravati", "provjeravati": "provjeriti", "dokazati": "dokazivati",
    "dokazivati": "dokazati",
}

# Wartete auf Emir (Release\\Wortschatz\\v111_wartet_auf_emir.md), seit dem 07.11.2026 an
# seiner Stelle in WOERTER; der Ton kommt im eigenen Schritt (tests/offen_p1020.json).
WARTET = []
NACHGEKOMMEN = ["dići", "dizati"]
# Seit dem 07.11.2026: dići und dizati sind ein Paar, tvrditi hat sein Gegenstueck ustvrditi (Paket 19)
SEIT_P1020 = {"dići": "dizati", "dizati": "dići", "tvrditi": "ustvrditi"}


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
        # heben_ziehen hat seit dem 07.11.2026 mit dići und dizati 42 Eintraege (Warteliste,
        # an ihrer Stelle wie im Paket)
        assert 16 <= len(k["words"]) <= (42 if k["id"] == "heben_ziehen" else 40), k["id"]
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
            if set(liste) == {"izvršiti", "vršiti", "izvršavati"}:
                continue     # seit Paket 19 (07.11.2026): izvršiti hat zwei Partner, vršiti und izvršavati
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
    # Seit dem 07.11.2026: was von der Warteliste kam, hat Emirs Ton erst nach dem Ton-Schritt
    ohne = [o for o in ohne if o[1] not in offen_p1020.TON]
    assert not ohne, ohne[:20]


def test_partner_an_beiden_woertern(grunddaten):
    """"partner" genau nach dem Paket, auch beim Gegenstueck. Ausnahme vući: es zeigt auf
    povući, povući aber auf povlačiti (zwei Partner, die App liest in beide Richtungen)."""
    neu = {w["bs"]: w for w in _neu(grunddaten)}
    alle = {w["bs"]: w for w in _alle(grunddaten)}
    assert {b: w["partner"] for b, w in neu.items() if w.get("partner")} == dict(PARTNER, **SEIT_P1020)
    for wort, gegen in PARTNER.items():
        if wort == "vući":
            assert alle["povući"]["partner"] == "povlačiti"
            continue
        assert alle[gegen].get("partner") == wort, (gegen, wort)


def test_level_in_tun_und_lassen(grunddaten):
    tun = [k["id"] for k in grunddaten["kategorien"] if k["sektion"] == "tunlassen"]
    i = tun.index("paare_mehr")
    assert tun[i + 1:i + 11] == LEVEL, "hinter paare_mehr"
    assert list(WOERTER) == LEVEL


def test_dozvoliti_dopustiti_sind_ein_wort(alle_daten, grunddaten, index_html):
    w = {x["bs"]: x for x in _alle(grunddaten)}
    assert w["dozvoliti / dopustiti"]["id"] == "erlauben / zulassen:dozvoliti / dopustiti"
    assert w["dozvoljavati / dopuštati"]["id"] == "erlauben / zulassen:dozvoljavati / dopuštati"
    assert w["dozvoliti / dopustiti"]["partner"] == "dozvoljavati / dopuštati"
    assert w["dozvoljavati / dopuštati"]["partner"] == "dozvoliti / dopustiti"
    for bs in ("dozvoliti", "dozvoljavati", "dopustiti", "dopuštati"):
        assert bs not in w, bs
    assert "'erlauben:dozvoliti': 'erlauben / zulassen:dozvoliti / dopustiti'" in index_html
    assert "'erlauben:dozvoljavati': 'erlauben / zulassen:dozvoljavati / dopuštati'" in index_html
    k = next(x for x in grunddaten["kategorien"] if x["id"] == "entscheiden_annehmen")
    saetze = [x["bs"] for x in k["words"]]
    assert "Neću ti dopustiti da to uradiš." in saetze and "Roditelji mu ne dopuštaju da izlazi." in saetze
    for code, daten in alle_daten.items():
        u = {x["bs"]: x["de"] for x in _alle(daten)}
        assert u["dozvoliti / dopustiti"] == u["dozvoljavati / dopuštati"], code


def test_alte_verben_bekommen_ihren_partner(grunddaten):
    w = {x["bs"]: x for x in _alle(grunddaten)}
    assert w["nositi"]["partner"] == "ponijeti" and w["ponijeti"]["partner"] == "nositi"
    assert w["vući"]["partner"] == "povući" and w["povući"]["partner"] == "povlačiti"


def test_podici_mit_beiden_formen(grunddaten):
    w = {x["bs"]: x for x in _alle(grunddaten)}["podići / podignuti"]
    assert w["partner"] == "podizati" and "auch" not in w, "beide Formen stehen im Wort selbst"


@pytest.mark.parametrize("wort, de", [("činiti", "tun (Wirkung: Gutes tun, gut tun)"), ("učiniti", "tun"),
                                       ("odabirati", "aussuchen"), ("predavati", "abgeben / unterrichten")])
def test_ajdins_entscheidungen(grunddaten, wort, de):
    assert {x["bs"]: x for x in _alle(grunddaten)}[wort]["de"] == de
