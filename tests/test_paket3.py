# -*- coding: utf-8 -*-
"""Wortschatz-Paket 3 (01.11.2026): Kaufen und bezahlen, Paare nachholen und
Sektion 12 · Körper und Gesundheit.

150 Eintraege, von Ajdin am 31.10./01.11.2026 durchgesehen
(Release\\Wortschatz\\paket_03.json, paket_03_entscheidungen.md). Hier steht,
was beim Einbau festgelegt wurde:

- wie in Paket 1 und 2 steht jedes Wort direkt vor seinem Beispielsatz, die
  Level tragen "reihenfolge": True;
- Kaufen und bezahlen (zwei Level) und Paare nachholen (ein Level) stehen in
  Tun und Lassen vor passieren und notfall, die acht Level von Sektion 12
  hinter Sektion 11 (dritte Farbe, sektionsNummer());
- "auch" und "zaehlt_nicht" genau nach dem Paket: was Ajdin ausgeschlossen
  hat (grudi, prepisati, rentgen, odabrati, pogađati se), zaehlt beim Tippen
  nicht;
- "partner" an beiden Woertern, auch am Verb aus Paket 1 oder 2. izabrati
  („sich entscheiden / wählen“) und birati („auswählen / wählen“) behalten
  Ajdins verschiedene Bedeutungen und sind trotzdem ein Paar - wie popiti
  und piti. So stehen sie nie zusammen in einer Auswahl, in der beide
  „wählen“ zeigen;
- vratiti / vraćati (zurückgeben) und vratiti se / vraćati se (zurückkommen)
  sind verschiedene Woerter; jezik heisst Zunge und Sprache.
"""
import re

import pytest

TUN = ["kaufen_zurueckgeben", "geld_sparen", "paare_mehr"]
KOERPER = ["koerper_aussen", "koerper_innen", "krank_sein", "beschwerden", "in_der_praxis", "untersuchen_heilen",
           "apotheke", "gesund_leben"]

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin
# es freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und
# damit Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "kaufen_zurueckgeben": ["vratiti", "vraćati", "red", "izabrati", "birati", "dostaviti", "kupovina", "koštati",
                            "paket", "zamijeniti", "besplatan", "cjenkati se", "dostava", "isprobati", "narudžba"],
    "geld_sparen": ["vrijediti", "plaćanje", "isplatiti se", "potrošiti", "trošiti", "zaraditi", "zarađivati",
                    "dugovati", "naplatiti", "štedjeti", "uštedjeti", "novčanik", "novčanica", "posuditi", "kovanica",
                    "Koliko sam dužan?"],
    "paare_mehr": ["iznositi", "pomisliti", "saznavati", "poželjeti", "dozvoljavati / dopuštati", "umirati", "potpisivati",
                   "primjećivati", "spašavati", "prijavljivati se", "osušiti", "povjerovati", "kvariti se",
                   "porazgovarati", "promiješati", "zalijevati"],
    "koerper_aussen": ["lice", "jezik", "čelo", "rame", "koljeno", "prsa", "usna", "obraz", "stopalo", "nokat", "brada",
                       "kuk", "lakat"],
    "koerper_innen": ["tijelo", "koža", "kost", "mišić", "mozak", "zglob", "pluća", "grlo", "jetra", "bubreg",
                      "želudac"],
    "krank_sein": ["bolest", "virus", "rak", "trudnoća", "stres", "infekcija", "upala", "gripa", "dijabetes", "zarazan",
                   "trudna", "prehlada", "moždani udar", "srčani udar / infarkt"],
    "beschwerden": ["slomiti", "umor", "kašalj", "mučnina", "osip", "povraćati", "vrtoglavica", "modrica", "proljev",
                    "znojiti se", "oteći", "kašljati", "svrbjeti / svrbiti", "zubobolja", "Muka mi je."],
    "in_der_praxis": ["kontrola", "pacijent", "simptom", "propisati", "terapija", "nalaz", "naočale", "injekcija",
                      "ginekolog", "ordinacija", "pedijatar", "ultrazvuk", "čekaonica", "rendgen", "dom zdravlja"],
    "untersuchen_heilen": ["liječiti", "izliječiti", "pregledati", "mjeriti", "izmjeriti", "oporaviti se",
                           "oporavljati se", "gutati", "progutati", "udahnuti", "ozdraviti"],
    "apotheke": ["vitamin", "mast", "tableta", "antibiotik", "kapi", "nuspojava", "sirup", "maramica", "zavoj",
                 "flaster", "bez recepta", "apotekar / farmaceut", "toplomjer / termometar", "na prazan stomak"],
    "gesund_leben": ["zdravlje", "san", "visina", "težina", "alkohol", "cigareta", "pušiti", "dijeta", "smršati",
                     "udebljati se"],
}

# "auch" genau nach dem Paket (Feld auch, Ajdins Entscheidungen), dazu bei
# Adjektiven die weibliche und die saechliche Form aus "formen".
AUCH = {
    "besplatan": ["besplatna", "besplatno"], "zarazan": ["zarazna", "zarazno"],
    "štedjeti": ["štediti"], "uštedjeti": ["uštediti"], "posuditi": ["pozajmiti"], "kovanica": ["novčić"],
    "zalijevati": ["zalivati", "zaljevati"], "proljev": ["proliv", "dijareja"], "oteći": ["nateći"],
    "naočale": ["naočare"], "na prazan stomak": ["na prazan želudac", "natašte"], "smršati": ["smršaviti"],
    "udebljati se": ["ugojiti se"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {"prsa": "grudi", "propisati": "prepisati", "rendgen": "rentgen", "izabrati": "odabrati",
                "cjenkati se": "pogađati se"}

# Paare im Paket (beide Woerter neu)
PAARE_IM_PAKET = {"vratiti": "vraćati", "izabrati": "birati", "potrošiti": "trošiti", "zaraditi": "zarađivati",
                  "štedjeti": "uštedjeti", "liječiti": "izliječiti", "mjeriti": "izmjeriti",
                  "oporaviti se": "oporavljati se", "gutati": "progutati"}
# Gegenstuecke aus Paket 1 und 2: seit Paket 3 hat auch das alte Verb "partner"
ALTE_PARTNER = {"iznositi": "iznijeti", "pomisliti": "misliti", "saznavati": "saznati", "poželjeti": "željeti",
                "dozvoljavati / dopuštati": "dozvoliti / dopustiti", "umirati": "umrijeti", "potpisivati": "potpisati",
                "primjećivati": "primijetiti", "spašavati": "spasiti", "prijavljivati se": "prijaviti se",
                "osušiti": "sušiti", "povjerovati": "vjerovati", "kvariti se": "pokvariti se",
                "porazgovarati": "razgovarati", "promiješati": "miješati", "zalijevati": "zaliti"}
# Seit Paket 8 (06.11.2026) haben slomiti und propisati ihr Gegenstueck
SEIT_PAKET8 = {"slomiti": "lomiti", "propisati": "propisivati"}
# Seit den Paketen 7 und 8 eigene Woerter mit eigener Bedeutung: odabrati
# „aussuchen“ neben izabrati, pogađati se „verhandeln (Preis)“ neben cjenkati se.
# Beim Tippen zaehlen sie dort weiter nicht (keine auch-Form, kein Partner, andere
# Bedeutung).
EIGENES_WORT = {"odabrati": "aussuchen", "pogađati se": "verhandeln (Preis)"}


def _level(daten, ids):
    k = {x["id"]: x for x in daten["kategorien"]}
    return [k[i] for i in ids]


def _neu(daten):
    return [w for k in _level(daten, TUN + KOERPER) for w in k["words"]]


def _alle(daten):
    return [w for k in daten["kategorien"] for w in k["words"]]


def test_sektion_zwoelf_und_drei_level_in_tun_und_lassen(grunddaten):
    sektionen = [s["id"] for s in grunddaten["sektionen"]]
    assert sektionen[11] == "koerpergesundheit"
    assert grunddaten["sektionen"][11]["label"] == "Sektion 12 · Körper und Gesundheit"
    tun = [k["id"] for k in grunddaten["kategorien"] if k["sektion"] == "tunlassen"]
    assert tun[12:15] == TUN, "nach im_haushalt"
    assert tun[-2:] == ["passieren", "notfall"], "seit 06.11.2026 stehen dazwischen die Level aus Paket 7 und 8"
    ids = [k["id"] for k in grunddaten["kategorien"]]
    i = ids.index("koerper_aussen")
    assert ids[i - 1] == "sinne" and ids[i:i + 8] == KOERPER, "hinter Sektion 11"
    assert [k["id"] for k in grunddaten["kategorien"] if k["sektion"] == "koerpergesundheit"] == KOERPER
    assert list(WOERTER) == TUN + KOERPER
    assert sum(len(k["words"]) for k in _level(grunddaten, TUN + KOERPER)) == 300
    assert sum(len(k["words"]) for k in _level(grunddaten, KOERPER)) == 206


def test_jedes_wort_steht_vor_seinem_beispielsatz(grunddaten):
    for k in _level(grunddaten, TUN + KOERPER):
        assert k["reihenfolge"] is True, k["id"]
        assert 20 <= len(k["words"]) <= 40, k["id"]
        woerter = k["words"]
        assert [w["bs"] for w in woerter[0::2]] == WOERTER[k["id"]], k["id"]
        for wort, satz in zip(woerter[0::2], woerter[1::2]):
            assert re.search(r"[.!?]$", satz["bs"]) and re.search(r"[.!?]$", satz["de"]), satz
            assert satz["bs"][:1].isupper() and satz["de"][:1].isupper(), satz
            assert "partner" not in satz and "auch" not in satz, satz
            assert satz["bs"] != wort["bs"], satz


@pytest.mark.parametrize("wort, de, satz", [
    ("prsa", "Brust", "Boli me u prsima."),
    ("terapija", "Therapie", "On ide na fizikalnu terapiju."),
    ("izabrati", "sich entscheiden / wählen", "Ne mogu izabrati, sve mi se sviđa."),
    ("birati", "auswählen / wählen", "Ti biraš film večeras."),
    ("cjenkati se", "feilschen", "Babo se uvijek cjenka na pijaci."),
    ("isprobati", "ausprobieren / testen", "Moram isprobati ovaj recept."),
])
def test_ajdins_entscheidungen(grunddaten, wort, de, satz):
    """paket_03_entscheidungen.md: fuenf Eintraege waren falsch und sind
    ersetzt, izabrati und birati behalten verschiedene Bedeutungen."""
    woerter = _neu(grunddaten)
    i = [w["bs"] for w in woerter].index(wort)
    assert woerter[i]["de"] == de and woerter[i + 1]["bs"] == satz


def test_auch_und_doppelformen(grunddaten):
    neu = {w["bs"]: w for w in _neu(grunddaten)}
    assert {bs: w["auch"] for bs, w in neu.items() if w.get("auch")} == AUCH
    for w in neu.values():
        formen = [f.strip() for f in w["bs"].split(" / ")]
        for a in w.get("auch", []):
            assert a not in formen, (w["bs"], a)
    # trudna gibt es nur weiblich
    assert "auch" not in neu["trudna"]
    for doppel in ("srčani udar / infarkt", "svrbjeti / svrbiti", "apotekar / farmaceut", "toplomjer / termometar"):
        assert doppel in neu, doppel


@pytest.mark.parametrize("wort, form", sorted(ZAEHLT_NICHT.items()))
def test_was_ajdin_ausgeschlossen_hat_zaehlt_nicht(grunddaten, wort, form):
    """Beim Tippen zaehlt das Wort, sein "auch" und jedes andere Wort mit
    derselben Bedeutung (annehmbar() in web/index.html). Die Form darf in
    keinem davon stehen - und auch kein Paar-Partner sein."""
    w = {x["bs"]: x for x in _neu(grunddaten)}[wort]
    assert form not in w.get("auch", []) and form not in w["bs"].split(" / ")
    alle = _alle(grunddaten)
    treffer = [x for x in alle if form in x["bs"].split(" / ") or form in x.get("auch", [])]
    if form in EIGENES_WORT:
        assert [x["de"] for x in treffer] == [EIGENES_WORT[form]], form
        assert w["de"] != EIGENES_WORT[form]
    else:
        assert not treffer, form
    assert w.get("partner") != form


def test_partner_in_beide_richtungen(grunddaten):
    alle = _alle(grunddaten)
    bs = [w["bs"] for w in alle]
    nach_bs = {w["bs"]: w for w in alle}
    neu = {w["bs"]: w for w in _neu(grunddaten)}
    soll = dict(ALTE_PARTNER)
    soll.update(SEIT_PAKET8)
    for a, b in PAARE_IM_PAKET.items():
        soll[a], soll[b] = b, a
    assert {b: w["partner"] for b, w in neu.items() if w.get("partner")} == soll
    for wort, gegen in soll.items():
        assert bs.count(gegen) == 1, gegen
        assert nach_bs[gegen].get("partner") == wort, (gegen, wort)
    assert len({frozenset(p) for p in soll.items()}) == 27
    # Jedes Wort hat hoechstens ein Gegenstueck
    zaehler = {}
    for w in alle:
        if w.get("partner"):
            for x in (w["bs"], w["partner"]):
                zaehler.setdefault(x, set()).add(frozenset((w["bs"], w["partner"])))
    # Ausnahme seit Paket 7: povući hat zwei Gegenstuecke (povlačiti, vući)
    assert len(zaehler.pop("povući")) == 2
    assert max(len(v) for v in zaehler.values()) == 1


def test_izabrati_und_birati_paar_mit_verschiedener_bedeutung(alle_daten, grunddaten):
    """Ajdin: izabrati = sich (fuer etwas) entscheiden, birati = auswaehlen.
    Die Bedeutungen bleiben, wie er sie freigegeben hat. Als Paar stehen sie
    nie zusammen in einer Auswahl (geschwister()); tippt man das andere Verb,
    kommt "Fast richtig!" mit dem Hinweis auf das Paar."""
    w = {x["bs"]: x for x in _alle(grunddaten)}
    assert w["izabrati"]["partner"] == "birati" and w["birati"]["partner"] == "izabrati"
    assert w["izabrati"]["de"] != w["birati"]["de"]
    for code, daten in alle_daten.items():
        u = {x["bs"]: x["de"] for x in _alle(daten)}
        assert u["izabrati"] != u["birati"], code


@pytest.mark.parametrize("ohne, mit", [("vratiti", "vratiti se"), ("vraćati", "vraćati se")])
def test_zurueckgeben_und_zurueckkommen_sind_nicht_gleich(alle_daten, ohne, mit):
    """Pruefbericht: in der Auswahl duerfen zurueckgeben und zurueckkommen
    nicht als gleich gelten - kein Paar, kein "auch", in keiner Sprache
    dieselbe Bedeutung und kein gemeinsamer Teil zwischen " / "."""
    for code, daten in alle_daten.items():
        w = {x["bs"]: x for x in _alle(daten)}
        a, b = w[ohne], w[mit]
        assert a.get("partner") != mit and b.get("partner") != ohne
        assert mit not in a.get("auch", []) and ohne not in b.get("auch", [])
        teile_a = {t.strip().lower() for t in a["de"].split(" / ")}
        teile_b = {t.strip().lower() for t in b["de"].split(" / ")}
        assert not teile_a & teile_b, (code, a["de"], b["de"])


def test_jezik_heisst_zunge_und_sprache(alle_daten, grunddaten):
    """Gleiches bs, zwei Kennungen. distractors() schliesst dasselbe bs aus;
    in jeder Sprache stehen die Bedeutungen verschieden da."""
    ids = sorted(w["id"] for w in _alle(grunddaten) if w["bs"] == "jezik")
    assert ids == ["sprache:jezik", "zunge:jezik"]
    for code, daten in alle_daten.items():
        bed = [w["de"] for w in _alle(daten) if w["bs"] == "jezik"]
        assert len(set(bed)) == 2, (code, bed)


def test_gleiche_bedeutung_im_neuen_teil_nur_bei_paaren(alle_daten):
    """Wie in Paket 1 und 2: zwei Woerter mit derselben Bedeutung sind in
    der Auswahl nicht zu unterscheiden. Im neuen Teil darf das nur ein
    Aspektpaar sein - in jeder Sprache."""
    for code, daten in alle_daten.items():
        alle = _alle(daten)
        paare = {frozenset((w["bs"], w["partner"])) for w in alle if w.get("partner")}
        neu = {w["bs"] for w in _neu(daten)}
        nach = {}
        for w in alle:
            nach.setdefault(w["de"].strip().lower().rstrip(".!?…  "), []).append(w["bs"])
        for bedeutung, liste in nach.items():
            if len(liste) < 2 or not neu & set(liste):
                continue
            assert len(liste) == 2 and frozenset(liste) in paare, (code, bedeutung, liste)


def _teile_gleich(a, b):
    """Wie in tests/test_paket2.py: gleiche Teilbedeutung zwischen " / ",
    ein Teil ohne Klammer gilt auch gegen einen Teil mit Klammer am Ende."""
    def norm(s):
        return s.strip().lower().rstrip(".!?…  ")

    def kern(teil):
        return norm(re.sub(r"\s*\([^()]*\)$", "", teil.strip()))

    ta = [norm(x) for x in a.split(" / ")]
    tb = [norm(x) for x in b.split(" / ")]
    gleich = set(ta) & set(tb)
    gleich |= {x for x in ta if not x.endswith(")")} & {kern(x) for x in tb}
    gleich |= {x for x in tb if not x.endswith(")")} & {kern(x) for x in ta}
    return gleich


def test_teilbedeutungen_im_level_nur_wie_im_deutschen(alle_daten, grunddaten):
    """Wie in tests/test_paket2.py, fuer Sektion 12: zwei Woerter eines Levels
    duerfen in einer Sprache nur dann teilweise gleich heissen, wenn das
    Deutsche es auch tut (Sektion 10 prueft schon test_paket2.py).
    Beispiele: kašalj „der Husten“ und kašljati „husten“ (sv hostan / hosta),
    oporaviti se „sich erholen“ und ozdraviti „gesund werden“ (tr toparlanmak
    / iyileşmek)."""
    de = {(k["id"], w["bs"]): w["de"] for k in grunddaten["kategorien"] for w in k["words"]}
    gefunden = []
    for code, daten in alle_daten.items():
        alle = _alle(daten)
        paare = {frozenset((w["bs"], w["partner"])) for w in alle if w.get("partner")}
        for k in daten["kategorien"]:
            if k["sektion"] != "koerpergesundheit":
                continue
            for i, a in enumerate(k["words"]):
                for b in k["words"][i + 1:]:
                    if frozenset((a["bs"], b["bs"])) in paare:
                        continue
                    gleich = _teile_gleich(a["de"], b["de"])
                    if gleich and not _teile_gleich(de[(k["id"], a["bs"])], de[(k["id"], b["bs"])]):
                        gefunden.append((code, k["id"], a["bs"], b["bs"], sorted(gleich)))
    assert not gefunden, gefunden


@pytest.mark.parametrize("code, bs, bedeutung", [
    ("en", "želudac", "stomach (organ)"),      # stomak (Bauch) ist "stomach"
    ("en", "pacijent", "patient (at the doctor's)"),    # strpljiv (geduldig) ist "patient"
    ("fr", "pacijent", "patient (chez le médecin)"),
    ("tr", "jezik", "dil (ağızdaki)"),         # jezik (Sprache) ist "dil"
    ("fr", "rendgen", "radiographie"),        # radio ist das Radio (Paket 4)
    ("en", "prehlada", "cold (illness)"),       # hladno (kalt) ist "cold"
])
def test_bedeutungen_die_sonst_zusammenfielen(alle_daten, bs, code, bedeutung):
    """Woerter, die in einer Sprache sonst wie ein anderes Wort hiessen,
    tragen eine Klammer."""
    w = {x["id"]: x["de"] for x in _alle(alle_daten[code]) if x["bs"] == bs}
    assert bedeutung in w.values(), (code, bs, w)
