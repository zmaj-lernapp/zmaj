# -*- coding: utf-8 -*-
"""Wortschatz-Paket 2 (31.10.2026): vier Level in Tun und Lassen und
Sektion 11 · Wie etwas ist.

150 Eintraege, von Ajdin am 31.10.2026 durchgesehen
(Release\\Wortschatz\\paket_02.json, paket_02_entscheidungen.md). Aus Nr. 139
sind zwei Woerter geworden (okus, ukus), also 151 Woerter mit Beispielsatz.
Hier steht, was beim Einbau festgelegt wurde:

- wie in Paket 1 steht jedes Wort direkt vor seinem Beispielsatz, die Level
  tragen "reihenfolge": True (tests/test_paket1.py);
- die vier neuen Level von Tun und Lassen stehen vor passieren und notfall,
  die sieben von Sektion 11 am Ende;
- Adjektive zeigen die maennliche Form, weibliche und saechliche stehen in
  "auch" und zaehlen beim Tippen. "(m/w)" haette die deutsche Bedeutung und
  damit die Kennung veraendert;
- "partner" steht bei allen neuen Paaren an beiden Woertern, auch am Verb
  aus Paket 1 oder der App;
- gleich geschriebene Woerter (dug lang / dug Schulden, jako sehr / jak
  stark) kommen nie zusammen in eine Auswahl: dasselbe bs schliesst
  distractors() aus, eine Form in "auch" geschwister() in web/index.html.
"""
import re

import pytest

TUN = ["paare_geben", "paare_denken", "paare_alltag", "im_haushalt"]
WIE = ["lang_kurz", "voll_leer", "moeglich", "wie_jemand_ist", "benehmen", "glueck_sorgen", "sinne"]

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin
# es freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und
# damit Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "paare_geben": ["nalaziti", "primiti", "nuditi", "iskoristiti", "sačuvati", "gubiti", "ostavljati", "bacati",
                    "skidati", "krasti", "pokazivati", "pozivati", "potražiti", "naručivati"],
    "paare_denken": ["javljati se", "objašnjavati", "odlučivati", "rješavati", "razmisliti", "shvatati",
                     "zaboravljati", "poslušati", "dogovarati se", "sačekati"],
    "paare_alltag": ["postajati", "nastavljati", "dešavati se / događati se", "padati", "pripremati",
                     "buditi se", "buditi", "probuditi", "prestajati", "uspijevati", "ženiti se", "udavati se",
                     "paliti", "posjećivati", "gasiti", "popravljati"],
    "im_haushalt": ["iznijeti", "složiti", "oprati", "miješati", "pokvariti se", "obrisati", "brisati", "sušiti",
                    "rezati", "skuhati", "pržiti", "zaliti", "objesiti", "počistiti", "usisavati", "usisati"],
    "lang_kurz": ["daleko", "visok", "težak", "širok", "dug", "nizak", "kratak", "uzak", "lagan", "tanak",
                  "debeo", "mršav"],
    "voll_leer": ["isti", "jak", "pun", "bogat", "drugačiji", "slab", "prazan", "tačan", "suh", "pogrešan",
                  "siromašan", "tvrd", "mokar", "mekan"],
    "moeglich": ["potreban", "moguć", "poseban", "siguran", "sličan", "spreman", "slobodan", "jednostavan",
                 "običan", "čudan", "nemoguć", "gotov", "komplikovan", "zauzet", "pravi"],
    "wie_jemand_ist": ["drag", "ozbiljan", "vrijedan", "pametan", "iskren", "zao", "hrabar", "glup", "pošten",
                       "veseo", "oprezan"],
    "benehmen": ["ljubazan", "pristojan", "pažljiv", "lijen", "strpljiv", "sebičan", "smiren", "bezobrazan",
                 "tvrdoglav", "stidljiv", "škrt"],
    "glueck_sorgen": ["sreća", "osjećaj", "briga", "zahvalan", "Sretno!", "zabrinut", "zbunjen", "razočaran",
                      "ljubomoran", "zaljubljen", "opušten", "uzbuđen", "uplašen", "pospan"],
    "sinne": ["osjetiti", "primijetiti", "probati", "miris", "taman", "okus", "ukus", "svijetao", "mrak", "buka",
              "tišina", "tih", "dirati", "glasan", "gorak", "mirisati", "smrdjeti / smrditi", "bljutav"],}

# Adjektive: weibliche und saechliche Form aus dem Paket ("formen"), sie
# zaehlen beim Tippen (auch). Angezeigt wird die maennliche.
FORMEN = {
    "visok": ("visoka", "visoko"), "težak": ("teška", "teško"), "širok": ("široka", "široko"),
    "dug": ("duga", "dugo"), "nizak": ("niska", "nisko"), "kratak": ("kratka", "kratko"),
    "uzak": ("uska", "usko"), "lagan": ("lagana", "lagano"), "tanak": ("tanka", "tanko"),
    "debeo": ("debela", "debelo"), "mršav": ("mršava", "mršavo"), "isti": ("ista", "isto"),
    "jak": ("jaka", "jako"), "pun": ("puna", "puno"), "bogat": ("bogata", "bogato"),
    "drugačiji": ("drugačija", "drugačije"), "slab": ("slaba", "slabo"), "prazan": ("prazna", "prazno"),
    "tačan": ("tačna", "tačno"), "suh": ("suha", "suho"), "pogrešan": ("pogrešna", "pogrešno"),
    "siromašan": ("siromašna", "siromašno"), "tvrd": ("tvrda", "tvrdo"), "mokar": ("mokra", "mokro"),
    "mekan": ("mekana", "mekano"), "potreban": ("potrebna", "potrebno"), "moguć": ("moguća", "moguće"),
    "poseban": ("posebna", "posebno"), "siguran": ("sigurna", "sigurno"), "sličan": ("slična", "slično"),
    "spreman": ("spremna", "spremno"), "slobodan": ("slobodna", "slobodno"),
    "jednostavan": ("jednostavna", "jednostavno"), "običan": ("obična", "obično"), "čudan": ("čudna", "čudno"),
    "nemoguć": ("nemoguća", "nemoguće"), "gotov": ("gotova", "gotovo"),
    "komplikovan": ("komplikovana", "komplikovano"), "zauzet": ("zauzeta", "zauzeto"),
    "pravi": ("prava", "pravo"), "drag": ("draga", "drago"), "ozbiljan": ("ozbiljna", "ozbiljno"),
    "vrijedan": ("vrijedna", "vrijedno"), "pametan": ("pametna", "pametno"), "iskren": ("iskrena", "iskreno"),
    "zao": ("zla", "zlo"), "hrabar": ("hrabra", "hrabro"), "glup": ("glupa", "glupo"),
    "pošten": ("poštena", "pošteno"), "veseo": ("vesela", "veselo"), "oprezan": ("oprezna", "oprezno"),
    "ljubazan": ("ljubazna", "ljubazno"), "pristojan": ("pristojna", "pristojno"),
    "pažljiv": ("pažljiva", "pažljivo"), "lijen": ("lijena", "lijeno"), "strpljiv": ("strpljiva", "strpljivo"),
    "sebičan": ("sebična", "sebično"), "smiren": ("smirena", "smireno"),
    "bezobrazan": ("bezobrazna", "bezobrazno"), "tvrdoglav": ("tvrdoglava", "tvrdoglavo"),
    "stidljiv": ("stidljiva", "stidljivo"), "škrt": ("škrta", "škrto"), "zahvalan": ("zahvalna", "zahvalno"),
    "zabrinut": ("zabrinuta", "zabrinuto"), "zbunjen": ("zbunjena", "zbunjeno"),
    "razočaran": ("razočarana", "razočarano"), "ljubomoran": ("ljubomorna", "ljubomorno"),
    "zaljubljen": ("zaljubljena", "zaljubljeno"), "opušten": ("opuštena", "opušteno"),
    "uzbuđen": ("uzbuđena", "uzbuđeno"), "uplašen": ("uplašena", "uplašeno"), "pospan": ("pospana", "pospano"),
    "taman": ("tamna", "tamno"), "svijetao": ("svijetla", "svijetlo"), "tih": ("tiha", "tiho"),
    "glasan": ("glasna", "glasno"), "gorak": ("gorka", "gorko"), "bljutav": ("bljutava", "bljutavo"),}

# Ajdins Entscheidungen vom 31.10.2026 und der Pruefbericht: weitere Formen,
# die beim Tippen zaehlen. Sie stehen in "auch" hinter den Formen.
AUCH_EXTRA = {"shvatati": ["shvaćati"], "sačekati": ["pričekati"], "objesiti": ["okačiti"],
              "počistiti": ["očistiti"], "mekan": ["mek", "meko"], "komplikovan": ["kompliciran"],
              "stidljiv": ["sramežljiv"]}

# Das Gegenstueck jedes neuen Verbs. Steht es in Paket 1 oder der App, hat
# es seit Paket 2 umgekehrt auch "partner".
PARTNER = {
    "nalaziti": "naći", "primiti": "primati", "nuditi": "ponuditi", "iskoristiti": "koristiti",
    "sačuvati": "čuvati", "gubiti": "izgubiti", "ostavljati": "ostaviti", "bacati": "baciti",
    "skidati": "skinuti", "krasti": "ukrasti", "pokazivati": "pokazati", "pozivati": "pozvati",
    "potražiti": "tražiti", "naručivati": "naručiti", "javljati se": "javiti se", "objašnjavati": "objasniti",
    "odlučivati": "odlučiti", "rješavati": "riješiti", "razmisliti": "razmišljati", "shvatati": "shvatiti",
    "zaboravljati": "zaboraviti", "poslušati": "slušati", "dogovarati se": "dogovoriti se", "sačekati": "čekati",
    "postajati": "postati", "nastavljati": "nastaviti", "dešavati se / događati se": "desiti se / dogoditi se",
    "padati": "pasti", "pripremati": "pripremiti", "buditi se": "probuditi se", "buditi": "probuditi",
    "probuditi": "buditi", "prestajati": "prestati", "uspijevati": "uspjeti", "ženiti se": "oženiti se",
    "udavati se": "udati se", "paliti": "upaliti", "posjećivati": "posjetiti", "gasiti": "ugasiti",
    "popravljati": "popraviti", "obrisati": "brisati", "brisati": "obrisati", "skuhati": "kuhati",
    "počistiti": "čistiti", "usisavati": "usisati", "usisati": "usisavati",
}


def _level(daten, ids):
    k = {x["id"]: x for x in daten["kategorien"]}
    return [k[i] for i in ids]


def _neu(daten):
    return [w for k in _level(daten, TUN + WIE) for w in k["words"]]


def _alle(daten):
    return [w for k in daten["kategorien"] for w in k["words"]]


def test_sektion_elf_und_vier_level_in_tun_und_lassen(grunddaten):
    sektion = grunddaten["sektionen"][10]
    assert len(grunddaten["sektionen"]) == 11
    assert sektion["id"] == "wieetwasist"
    assert sektion["label"] == "Sektion 11 · Wie etwas ist"
    ids = [k["id"] for k in grunddaten["kategorien"]]
    tun = [k["id"] for k in grunddaten["kategorien"] if k["sektion"] == "tunlassen"]
    assert tun[8:] == TUN + ["passieren", "notfall"], "vor passieren und notfall"
    assert ids[-7:] == WIE, "Sektion 11 steht am Ende"
    assert all(k["sektion"] == "wieetwasist" for k in _level(grunddaten, WIE))
    assert list(WOERTER) == TUN + WIE
    assert sum(len(k["words"]) for k in _level(grunddaten, TUN + WIE)) == 302
    assert sum(len(k["words"]) for k in _level(grunddaten, TUN)) == 112
    # Die Level davor sind unberuehrt: 65 alte und 10 aus Paket 1
    alt = [k for k in grunddaten["kategorien"] if k["id"] not in WOERTER]
    assert len(alt) == 75 and sum(len(k["words"]) for k in alt) == 2040


def test_jedes_wort_steht_vor_seinem_beispielsatz(grunddaten):
    for k in _level(grunddaten, TUN + WIE):
        assert k["reihenfolge"] is True, k["id"]
        woerter = k["words"]
        assert [w["bs"] for w in woerter[0::2]] == WOERTER[k["id"]], k["id"]
        for wort, satz in zip(woerter[0::2], woerter[1::2]):
            assert re.search(r"[.!?]$", satz["bs"]) and re.search(r"[.!?]$", satz["de"]), satz
            assert satz["bs"][:1].isupper() and satz["de"][:1].isupper(), satz
            assert "partner" not in satz and "auch" not in satz, satz
            assert satz["bs"] != wort["bs"], satz


def test_okus_und_ukus_sind_zwei_woerter(grunddaten):
    """Ajdin: okus ist der Geschmack von Essen, ukus z. B. der Modegeschmack."""
    sinne = _level(grunddaten, ["sinne"])[0]["words"]
    i = [w["bs"] for w in sinne].index("okus")
    assert [(w["de"], w["bs"]) for w in sinne[i:i + 4]] == [
        ("Geschmack (Essen)", "okus"),
        ("Das schmeckt komisch.", "Ovo ima čudan okus."),
        ("Geschmack (Stil)", "ukus"),
        ("Du hast einen guten Geschmack.", "Imaš dobar ukus."),
    ]
    ids = [w["id"] for w in _alle(grunddaten)]
    assert ids.count("geschmack (essen):okus") == ids.count("geschmack (stil):ukus") == 1


def test_adjektive_maennlich_die_anderen_formen_zaehlen(grunddaten):
    neu = {w["bs"]: w for w in _neu(grunddaten)}
    for bs, (weiblich, saechlich) in FORMEN.items():
        w = neu[bs]
        assert " / " not in w["bs"] and "(m/w" not in w["de"], bs
        assert w["auch"] == [weiblich, saechlich] + AUCH_EXTRA.get(bs, []), bs
    for bs, extra in AUCH_EXTRA.items():
        assert neu[bs]["auch"][-len(extra):] == extra, bs
    mit_auch = {bs for bs, w in neu.items() if w.get("auch")}
    assert mit_auch == set(FORMEN) | set(AUCH_EXTRA)
    for w in neu.values():
        formen = [f.strip() for f in w["bs"].split(" / ")]
        for a in w.get("auch", []):
            assert a not in formen, (w["bs"], a)


@pytest.mark.parametrize("wort, form, anderes", [
    ("jak", "jako", "sehr:jako"),
    ("pravi", "pravo", "geradeaus:pravo"),
    ("težak", "teško", "schwierig:teško"),
    ("dug", "duga", "regenbogen:duga"),
])
def test_gleiche_schreibung_nie_zusammen_in_der_auswahl(grunddaten, wort, form, anderes):
    """Die Form steht in "auch" des neuen Wortes - geschwister() in
    web/index.html laesst die beiden dann nie zusammen in eine Auswahl."""
    neu = {w["bs"]: w for w in _neu(grunddaten)}
    assert form in neu[wort]["auch"]
    andere = [w for w in _alle(grunddaten) if w["id"] == anderes]
    assert len(andere) == 1 and andere[0]["bs"] == form


def test_dug_hat_zwei_bedeutungen(grunddaten):
    """Gleiches bs, verschiedene Kennung: distractors() schliesst dasselbe bs aus."""
    dug = sorted(w["id"] for w in _alle(grunddaten) if w["bs"] == "dug")
    assert dug == ["lang:dug", "schulden:dug"]


@pytest.mark.parametrize("ohne, mit", [("nalaziti", "nalaziti se"), ("buditi", "buditi se")])
def test_mit_und_ohne_se_sind_nicht_gleich(alle_daten, ohne, mit):
    """Pruefbericht: in der Auswahl duerfen finden / sich befinden und
    wecken / aufwachen nicht als gleich gelten - also kein Paar, kein
    gemeinsames "auch" und in keiner Sprache dieselbe Bedeutung."""
    for code, daten in alle_daten.items():
        w = {x["bs"]: x for x in _alle(daten)}
        a, b = w[ohne], w[mit]
        assert a.get("partner") != mit and b.get("partner") != ohne
        assert mit not in a.get("auch", []) and ohne not in b.get("auch", [])
        assert a["de"].strip().lower() != b["de"].strip().lower(), (code, a["de"])


def test_partner_in_beide_richtungen(grunddaten):
    alle = _alle(grunddaten)
    bs = [w["bs"] for w in alle]
    nach_bs = {w["bs"]: w for w in alle}
    neu = {w["bs"]: w for w in _neu(grunddaten)}
    assert {b: w["partner"] for b, w in neu.items() if w.get("partner")} == PARTNER
    paare = set()
    for wort, gegen in PARTNER.items():
        assert bs.count(gegen) == 1, gegen
        assert nach_bs[gegen].get("partner") == wort, (gegen, wort)
        paare.add(frozenset((wort, gegen)))
    assert len(paare) == 43
    # Jedes Wort hat hoechstens ein Gegenstueck, und jedes steht in der App
    zaehler = {}
    for w in alle:
        if w.get("partner"):
            assert bs.count(w["partner"]) == 1, (w["bs"], w["partner"])
            for x in (w["bs"], w["partner"]):
                zaehler.setdefault(x, set()).add(frozenset((w["bs"], w["partner"])))
    assert max(len(v) for v in zaehler.values()) == 1


def test_gleiche_bedeutung_im_neuen_teil_nur_bei_paaren(alle_daten):
    """Wie in Paket 1: zwei Woerter mit derselben Bedeutung sind in der
    Auswahl nicht zu unterscheiden. Im neuen Teil darf das nur ein
    Aspektpaar sein - in jeder Sprache."""
    for code, daten in alle_daten.items():
        alle = _alle(daten)
        paare = {frozenset((w["bs"], w["partner"])) for w in alle if w.get("partner")}
        neu = {w["bs"] for w in _neu(daten)}
        nach = {}
        for w in alle:
            nach.setdefault(w["de"].strip().lower().rstrip(".!?…  "), []).append(w["bs"])
        for bedeutung, liste in nach.items():
            if len(liste) < 2 or not neu & set(liste):
                continue
            assert len(liste) == 2 and frozenset(liste) in paare, (code, bedeutung, liste)


def test_gotov_und_spreman_in_jeder_sprache_verschieden(alle_daten):
    """"fertig" steht schon im Woerterbuch der Geschichten (gotova: ready,
    fr prête). Fuer gotov steht deshalb eine Ausnahme unter "woerter" in
    uebersetzungen.py - sonst hiesse es wie spreman (bereit)."""
    for code, daten in alle_daten.items():
        w = {x["bs"]: x["de"] for x in _alle(daten)}
        assert w["gotov"] != w["spreman"], code
    assert {x["bs"]: x["de"] for x in _alle(alle_daten["fr"])}["gotov"] == "fini"


def test_norwegisch_putzen_und_waschen(alle_daten):
    """nb putzen hiess "vaske" - so heisst jetzt oprati (waschen) im selben Level."""
    w = {x["bs"]: x["de"] for x in _alle(alle_daten["nb"])}
    assert w["oprati"] == "vaske"
    assert w["počistiti"] == w["čistiti"] == "gjøre rent"
