# -*- coding: utf-8 -*-
"""Wortschatz-Paket 8 (06.11.2026): 148 Verben fuer Sektion 10 · Tun und Lassen.

Von Ajdin am 06.11.2026 durchgesehen (Release\\Wortschatz\\paket_08.json,
v111_entscheidungen.md). Hier steht, was beim Einbau festgelegt wurde:

- zwoelf Level hinter denen aus Paket 7, vor passieren und notfall;
- die Gegenstuecke zu Verben aus Paket 3 und 4 stehen im Level paare_nachholen,
  "partner" dann an beiden Woertern (snimiti - snimati, crtati - nacrtati);
- stati gehoert zu stajati (stehen), mit verschiedener Bedeutung wie izabrati / birati;
- naviknuti se hat den Nachtrag vom 06.11.2026, navići se zaehlt nicht;
- plakati wartet auf Emir (w4114: zweites a zu lang, w4115: e bei beba zu kurz).
"""
import re

import pytest

import offen_p1020

LEVEL = ["sein_wirken", "erscheinen_verschwinden", "miteinander_umgehen", "lieben_fuerchten", "wundern_beruhigen",
         "sich_bewegen", "losgehen_abbiegen", "kaempfen_angreifen", "schuetzen_strafen", "im_alltag_tun",
         "erledigen_umziehen", "paare_nachholen"]
ERSTE_NUMMER, LETZTE_NUMMER = 3724, 5205      # Pakete 5 bis 9 zusammen, tests/test_paket59_ton.py

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "sein_wirken": ["nemati", "ticati se", "pripadati", "sadržati", "sastojati se", "služiti", "poslužiti",
                    "djelovati", "uticati", "nastati", "nastajati"],
    "erscheinen_verschwinden": ["pojaviti se", "pojavljivati se", "nestati", "nestajati", "rasti", "porasti",
                                "doživjeti", "doživljavati", "učestvovati", "poznavati", "razlikovati"],
    "miteinander_umgehen": ["podijeliti", "dijeliti", "pustiti", "puštati", "zadržati", "zadržavati",
                            "obratiti se", "obraćati se", "družiti se", "ponašati se", "poštovati", "cijeniti",
                            "pohvaliti", "hvaliti", "lagati", "slagati", "truditi se", "potruditi se",
                            "pogađati se"],
    "lieben_fuerchten": ["ljubiti", "poljubiti", "zagrliti", "grliti", "plakati", "sanjati", "mrziti",
                         "ljutiti se", "naljutiti se", "plašiti se", "uplašiti se"],
    "wundern_beruhigen": ["čuditi se", "vikati", "šutjeti / šutiti", "sumnjati", "patiti", "žaliti", "faliti",
                          "ličiti", "smiriti", "smirivati", "iznenaditi", "iznenađivati"],
    "sich_bewegen": ["hodati", "stati", "okrenuti", "okretati", "skočiti", "skakati", "popeti se",
                     "penjati se", "sići", "silaziti", "prijeći", "prelaziti"],
    "losgehen_abbiegen": ["poći", "polaziti", "obići", "obilaziti", "pobjeći", "bježati", "letjeti",
                          "skrenuti", "skretati", "sastati se", "sastajati se"],
    "kaempfen_angreifen": ["boriti se", "braniti", "odbraniti", "ubiti", "ubijati", "poginuti", "udariti",
                           "udarati", "pucati", "napasti", "napadati"],
    "schuetzen_strafen": ["osvojiti", "osvajati", "zaštititi", "štititi", "izazvati", "izazivati", "kazniti",
                          "kažnjavati", "razbiti", "razbijati"],
    "im_alltag_tun": ["peći", "ispeći", "sipati", "srediti", "sređivati", "spremiti", "spremati", "sakriti",
                      "skrivati", "uključiti", "uključivati", "isključiti", "isključivati"],
    "erledigen_umziehen": ["popuniti", "popunjavati", "zapisati", "zapisivati", "zakazati", "zakazivati",
                           "uplatiti", "uplaćivati", "preseliti se", "seliti se", "pogriješiti", "griješiti",
                           "naviknuti se", "navikavati se", "sjeći"],
    "paare_nachholen": ["snimati", "objavljivati", "polagati", "otkazivati", "pobjeđivati", "pakovati",
                        "prevoditi", "upisivati se", "zapošljavati se", "lomiti", "propisivati", "nacrtati",
                        "izračunati"],
}

# Das Wort steckt im Bestand als zweite Form, nur sein Satz kommt dazu.
NUR_SATZ = {}

# "auch" genau nach dem Paket, dazu bei Adjektiven die weitere Form aus "formen".
AUCH = {
    "uticati": ["utjecati"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    # sadržavati ist seit Paket 19 (07.11.2026) das Gegenstueck zu sadržati (Ajdin, 06.11.2026)
    "učestvovati": ["sudjelovati"], "prijeći": ["preći"],
    "skrivati": ["sakrivati"], "naviknuti se": ["navići se"], "pakovati": ["pakirati"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "služiti": "poslužiti", "poslužiti": "služiti", "nastati": "nastajati", "nastajati": "nastati",
    "pojaviti se": "pojavljivati se", "pojavljivati se": "pojaviti se", "nestati": "nestajati",
    "nestajati": "nestati", "rasti": "porasti", "porasti": "rasti", "doživjeti": "doživljavati",
    "doživljavati": "doživjeti", "podijeliti": "dijeliti", "dijeliti": "podijeliti", "pustiti": "puštati",
    "puštati": "pustiti", "zadržati": "zadržavati", "zadržavati": "zadržati", "obratiti se": "obraćati se",
    "obraćati se": "obratiti se", "pohvaliti": "hvaliti", "hvaliti": "pohvaliti", "lagati": "slagati",
    "slagati": "lagati", "truditi se": "potruditi se", "potruditi se": "truditi se", "ljubiti": "poljubiti",
    "poljubiti": "ljubiti", "zagrliti": "grliti", "grliti": "zagrliti", "ljutiti se": "naljutiti se",
    "naljutiti se": "ljutiti se", "plašiti se": "uplašiti se", "uplašiti se": "plašiti se",
    "smiriti": "smirivati", "smirivati": "smiriti", "iznenaditi": "iznenađivati", "iznenađivati": "iznenaditi",
    "stati": "stajati", "okrenuti": "okretati", "okretati": "okrenuti", "skočiti": "skakati",
    "skakati": "skočiti", "popeti se": "penjati se", "penjati se": "popeti se", "sići": "silaziti",
    "silaziti": "sići", "prijeći": "prelaziti", "prelaziti": "prijeći", "poći": "polaziti", "polaziti": "poći",
    "obići": "obilaziti", "obilaziti": "obići", "pobjeći": "bježati", "bježati": "pobjeći",
    "skrenuti": "skretati", "skretati": "skrenuti", "sastati se": "sastajati se", "sastajati se": "sastati se",
    "braniti": "odbraniti", "odbraniti": "braniti", "ubiti": "ubijati", "ubijati": "ubiti",
    "udariti": "udarati", "udarati": "udariti", "napasti": "napadati", "napadati": "napasti",
    "osvojiti": "osvajati", "osvajati": "osvojiti", "zaštititi": "štititi", "štititi": "zaštititi",
    "izazvati": "izazivati", "izazivati": "izazvati", "kazniti": "kažnjavati", "kažnjavati": "kazniti",
    "razbiti": "razbijati", "razbijati": "razbiti", "peći": "ispeći", "ispeći": "peći", "srediti": "sređivati",
    "sređivati": "srediti", "spremiti": "spremati", "spremati": "spremiti", "uključiti": "uključivati",
    "uključivati": "uključiti", "isključiti": "isključivati", "isključivati": "isključiti",
    "popuniti": "popunjavati", "popunjavati": "popuniti", "zapisati": "zapisivati", "zapisivati": "zapisati",
    "zakazati": "zakazivati", "zakazivati": "zakazati", "uplatiti": "uplaćivati", "uplaćivati": "uplatiti",
    "preseliti se": "seliti se", "seliti se": "preseliti se", "pogriješiti": "griješiti",
    "griješiti": "pogriješiti", "naviknuti se": "navikavati se", "navikavati se": "naviknuti se",
    "snimati": "snimiti", "objavljivati": "objaviti", "polagati": "položiti", "otkazivati": "otkazati",
    "pobjeđivati": "pobijediti", "pakovati": "spakovati", "prevoditi": "prevesti",
    "upisivati se": "upisati se", "zapošljavati se": "zaposliti se", "lomiti": "slomiti",
    "propisivati": "propisati", "nacrtati": "crtati", "izračunati": "računati",
}

# Wartete auf Emir (Release\\Wortschatz\\v111_wartet_auf_emir.md), seit dem 07.11.2026 an
# seiner Stelle in WOERTER; der Ton kommt im eigenen Schritt (tests/offen_p1020.json).
WARTET = []
NACHGEKOMMEN = ["plakati"]
# Seit Paket 19 (07.11.2026) haben sadržati und sakriti ihr Gegenstueck
SEIT_P1020 = {"sadržati": "sadržavati", "sakriti": "sakrivati"}


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
    assert tun[-14:-2] == LEVEL
    assert tun[-2:] == ["passieren", "notfall"]
    assert list(WOERTER) == LEVEL


@pytest.mark.parametrize("wort, gegen", [
    ("snimiti", "snimati"), ("objaviti", "objavljivati"), ("položiti", "polagati"), ("otkazati", "otkazivati"),
    ("pobijediti", "pobjeđivati"), ("spakovati", "pakovati"), ("prevesti", "prevoditi"),
    ("upisati se", "upisivati se"), ("zaposliti se", "zapošljavati se"), ("slomiti", "lomiti"),
    ("propisati", "propisivati"), ("crtati", "nacrtati"), ("računati", "izračunati"), ("stajati", "stati"),
])
def test_altes_verb_hat_partner(grunddaten, wort, gegen):
    w = {x["bs"]: x for x in _alle(grunddaten)}
    assert w[wort]["partner"] == gegen and w[gegen]["partner"] == wort


def test_gleiche_schreibung_nicht_zusammengelegt(grunddaten):
    w = {x["bs"]: x for x in _alle(grunddaten)}
    assert w["slagati"]["de"] == "lügen" and w["slagati"]["partner"] == "lagati"
    assert w["šutjeti / šutiti"]["de"] == "schweigen"
