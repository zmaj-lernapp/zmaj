# -*- coding: utf-8 -*-
"""Wortschatz-Paket 1 (31.10.2026): Sektion 10 · Tun und Lassen.

140 Verben und 10 Notfall-Woerter, von Ajdin am 31.10.2026 durchgesehen
(Release\\Wortschatz\\paket_01.json, paket_01_entscheidungen.md). Hier steht,
was beim Einbau festgelegt wurde:

- jedes Wort steht direkt vor seinem Beispielsatz, die Level tragen
  "reihenfolge": True (wie routine: das Verb vor dem Ich-Satz);
- Aspektpaare (ostati / ostajati, doći / dolaziti) haben dieselbe deutsche
  Bedeutung und verschiedene Kennungen - getrennter Lernstand. Ajdin:
  „beide wörter rein die sollen separat sein wenn einer gelernt wurde dann
  ist der andere noch nicht gelernt“. "partner" nennt das Gegenstueck;
- in der Auswahl stehen die beiden nie zusammen, beim Tippen ist das
  Gegenstueck "Fast richtig!" mit dem Hinweis task.partner (das prueft
  tests_e2e/test_aspektpaare.py im Browser);
- " / "-Doppelformen zaehlen einzeln (matches() in web/index.html), "auch"
  nur dort, wo eine Form nicht schon im Wort steht.
"""
import re

import pytest

# Die Woerter je Level in der Reihenfolge des Pakets, ohne die Beispielsaetze.
# Bosnisch genau so, wie Ajdin es freigegeben hat - aendert sich hier etwas,
# aendert sich eine Kennung und damit Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "kommen_gehen": ["ostati", "ostajati", "dolaziti", "vratiti se", "vraćati se", "otići", "odlaziti",
                     "donijeti", "donositi", "proći", "prolaziti", "krenuti", "kretati", "stići", "stizati",
                     "ući", "ulaziti", "izaći", "izlaziti", "voziti", "putovati"],
    "geben_nehmen": ["dobiti", "dobivati", "nalaziti se", "izgubiti", "naći", "davati", "nositi", "uzeti",
                     "uzimati", "poslati", "slati", "pomagati", "čuvati", "ponuditi", "prodati", "prodavati",
                     "plaćati", "kupovati", "primati", "ukrasti"],
    "sagen_denken": ["željeti", "misliti", "smatrati", "značiti", "očekivati", "gledati", "pogledati",
                     "vjerovati", "čuti", "odlučiti", "nadati se", "odgovoriti", "odgovarati", "pričati",
                     "ispričati"],
    "verstehen": ["razgovarati", "shvatiti", "zaboraviti", "objasniti", "naučiti", "javiti se", "razmišljati",
                  "saznati", "slušati", "dogovoriti se", "bojati se", "sjetiti se", "sviđati se", "svidjeti se"],
    "anfangen": ["početi", "počinjati", "završiti", "završavati", "otvoriti", "otvarati", "nastaviti", "uspjeti",
                 "trajati", "promijeniti", "mijenjati", "prestati", "zatvoriti", "zatvarati",
                 "desiti se / dogoditi se"],
    "tun_machen": ["postojati", "koristiti", "postati", "živjeti", "igrati", "napraviti", "praviti", "uraditi",
                   "pročitati", "napisati", "baviti se", "pokušavati", "riješiti", "pripremiti", "popiti",
                   "pojesti"],
    "stellen_legen": ["stajati", "staviti", "stavljati", "držati", "ostaviti", "pasti", "sjediti", "baciti",
                      "ležati", "skinuti", "ustati", "obući", "leći"],
    "alltag_leben": ["izgledati", "roditi se", "potpisati", "uživati", "prijaviti se", "umrijeti", "dozvoliti",
                     "zanimati", "zavisiti", "nedostajati", "probuditi se", "smetati", "udati se", "oženiti se",
                     "zakasniti"],
    "passieren": ["izgubiti se", "spasiti", "povrijediti se", "paziti", "krvariti", "prehladiti se",
                  "onesvijestiti se", "boljeti / boliti", "disati / dihati", "razboljeti se / razboliti se",
                  "gorjeti / goriti"],
    "notfall": ["Upomoć!", "hitan slučaj", "hitna", "vatrogasci", "požar", "nesreća", "povreda", "rana", "krv",
                "lopov"],
}

# Ajdins Entscheidungen vom 31.10.2026: weitere Formen, die beim Tippen zaehlen
AUCH = {
    "izaći": ["izići"],
    "dobivati": ["dobijati"],
    "hitna": ["vozilo hitne pomoći", "sanitet", "kola hitne pomoći"],
}

# Gegenstuecke, die schon vor dem Paket in der App standen
ALTE_PARTNER = {"dolaziti": "doći", "davati": "dati", "pomagati": "pomoći", "plaćati": "platiti",
                "kupovati": "kupiti", "naučiti": "učiti", "pročitati": "čitati", "napisati": "pisati",
                "pokušavati": "pokušati", "ustati": "ustajati", "sjetiti se": "sjećati se",
                "uraditi": "raditi", "popiti": "piti", "pojesti": "jesti", "zakasniti": "kasniti"}


def _level(daten):
    return [k for k in daten["kategorien"] if k.get("sektion") == "tunlassen"]


def _alle(daten):
    return [w for k in daten["kategorien"] for w in k["words"]]


def test_sektion_zehn_mit_zehn_leveln(grunddaten):
    assert grunddaten["sektionen"][-1]["id"] == "tunlassen"
    assert grunddaten["sektionen"][-1]["label"] == "Sektion 10 · Tun und Lassen"
    level = _level(grunddaten)
    assert [k["id"] for k in level] == list(WOERTER)
    assert [k["id"] for k in grunddaten["kategorien"][-10:]] == list(WOERTER), "die Sektion steht am Ende"
    assert sum(len(k["words"]) for k in level) == 300
    # Die 65 Level davor sind unberuehrt
    assert sum(len(k["words"]) for k in grunddaten["kategorien"][:65]) == 1740


def test_jedes_wort_steht_vor_seinem_beispielsatz(grunddaten):
    for k in _level(grunddaten):
        assert k["reihenfolge"] is True, k["id"]
        woerter = k["words"]
        assert [w["bs"] for w in woerter[0::2]] == WOERTER[k["id"]], k["id"]
        for wort, satz in zip(woerter[0::2], woerter[1::2]):
            assert re.search(r"[.!?]$", satz["bs"]) and re.search(r"[.!?]$", satz["de"]), satz
            assert satz["bs"][:1].isupper() and satz["de"][:1].isupper(), satz
            assert "partner" not in satz and "auch" not in satz, satz
            assert satz["bs"] != wort["bs"], satz


def test_auch_formen_und_doppelformen(grunddaten):
    for w in _alle(grunddaten):
        formen = [f.strip() for f in w["bs"].split(" / ")]
        for a in w.get("auch", []):
            assert a not in formen, (w["bs"], a)     # steht schon im Wort, matches() trennt selbst
    neu = {w["bs"]: w for k in _level(grunddaten) for w in k["words"]}
    for bs, auch in AUCH.items():
        assert neu[bs].get("auch") == auch, bs
    mit_auch = {bs for bs, w in neu.items() if w.get("auch")}
    assert mit_auch == set(AUCH)


def test_partner_stehen_in_der_app(grunddaten):
    alle = _alle(grunddaten)
    bs = [w["bs"] for w in alle]
    paare = set()
    for w in alle:
        if "partner" not in w:
            continue
        p = w["partner"]
        assert bs.count(p) == 1, (w["bs"], p)
        assert p != w["bs"]
        paare.add(frozenset((w["bs"], p)))
    neu = {w["bs"]: w for k in _level(grunddaten) for w in k["words"]}
    for wort, alt in ALTE_PARTNER.items():
        assert neu[wort].get("partner") == alt, wort
    # Jedes Wort hat hoechstens ein Gegenstueck
    zaehler = {}
    for p in paare:
        for x in p:
            zaehler[x] = zaehler.get(x, 0) + 1
    assert max(zaehler.values()) == 1, [x for x, n in zaehler.items() if n > 1]
    assert len(paare) == 39            # 24 im Paket, 15 mit einem Wort, das schon da war


def test_gleiche_bedeutung_im_neuen_teil_nur_bei_paaren(alle_daten):
    """Zwei Woerter mit derselben Bedeutung sind in der Auswahl nicht zu
    unterscheiden. Im neuen Teil darf das nur ein Aspektpaar sein - in
    jeder Sprache, und dort mit derselben Uebersetzung wie im Deutschen."""
    for code, daten in alle_daten.items():
        alle = _alle(daten)
        paare = {frozenset((w["bs"], w["partner"])) for w in alle if w.get("partner")}
        neu = {w["bs"] for k in _level(daten) for w in k["words"]}
        nach = {}
        for w in alle:
            nach.setdefault(w["de"].strip().lower().rstrip(".!?…  "), []).append(w["bs"])
        for bedeutung, liste in nach.items():
            if len(liste) < 2 or not neu & set(liste):
                continue
            if code == "tr" and bedeutung == "oturmak":
                continue     # sich setzen und sitzen, bedeutung_ausnahmen.json
            assert len(liste) == 2 and frozenset(liste) in paare, (code, bedeutung, liste)


def test_paare_heissen_in_jeder_sprache_gleich(alle_daten, grunddaten):
    de = {w["bs"]: w["de"] for w in _alle(grunddaten)}
    for code, daten in alle_daten.items():
        uebersetzt = {w["bs"]: w["de"] for w in _alle(daten)}
        for w in _alle(grunddaten):
            p = w.get("partner")
            if p and de[p] == w["de"]:
                assert uebersetzt[p] == uebersetzt[w["bs"]], (code, w["bs"], p)


@pytest.mark.parametrize("kennung", ["bleiben:ostati", "bleiben:ostajati", "kommen:doći", "kommen:dolaziti"])
def test_paare_haben_eigene_kennungen(grunddaten, kennung):
    ids = [w["id"] for w in _alle(grunddaten)]
    assert ids.count(kennung) == 1


def test_hinweis_auf_das_andere_verb_in_jeder_sprache(sprachcodes, index_html):
    import sprachen
    for code in sprachcodes:
        text = sprachen.TEXTE[code]["task.partner"]
        assert text.startswith(sprachen.TEXTE[code]["task.fast_richtig"]), code
        assert len(text) > len(sprachen.TEXTE[code]["task.fast_richtig"]) + 10, code
    assert "t('task.partner')" in index_html
    assert "t('task.fast_richtig')" in index_html
