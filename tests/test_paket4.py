# -*- coding: utf-8 -*-
"""Wortschatz-Paket 4 (01.11.2026): Sektion 13 · Zeit und Freizeit und
Sektion 14 · Lernen und Arbeiten.

150 Eintraege, von Ajdin am 01.11.2026 durchgesehen
(Release\\Wortschatz\\paket_04.json, paket_04_entscheidungen.md). Hier steht,
was beim Einbau festgelegt wurde:

- wie in den Paketen 1 bis 3 steht jedes Wort direkt vor seinem
  Beispielsatz, die Level tragen "reihenfolge": True;
- die sechs Level von Sektion 13 und die vier von Sektion 14 stehen am Ende,
  hinter Sektion 12 (vierte und fuenfte Farbe, sektionsNummer());
- "auch" genau nach dem Paket: bei allen 16 Fragen zaehlt die zweite Form
  mit, nur ranac (Ajdin: serbisch) und seljak NICHT;
- Paare im Paket: ponoviti / ponavljati, zapamtiti / pamtiti. Kommt das
  Gegenstueck erst spaeter (pobijediti, snimiti ...), steht kein "partner";
- vrijeme heisst Zeit und Wetter, radio ist das Radio neben radio sam.
"""
import re

import pytest

ZEIT = ["zeitangaben", "sofort_endlich", "sport", "hobbys", "medien", "urlaub"]
LERNEN = ["schule", "lernen_studieren", "berufe", "arbeitsplatz"]

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin
# es freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und
# damit Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "zeitangaben": ["vrijeme", "sekunda", "trenutak", "ponoć", "prijepodne", "jutros", "večeras", "sinoć", "noćas",
                    "prekjučer", "datum", "dnevno", "mjesečno", "budućnost", "praznik"],
    "sofort_endlich": ["odmah", "upravo", "maloprije", "nedavno", "ranije", "konačno", "dok", "tek", "još", "opet",
                       "zauvijek", "na vrijeme"],
    "sport": ["sport", "fudbal", "košarka", "rukomet", "trčati", "utakmica", "ekipa", "reprezentacija", "igrač",
              "trener", "gol", "lopta", "pobijediti", "pobjeda", "rezultat", "navijati", "navijač", "teretana",
              "trening", "vježbati"],
    "hobbys": ["hobi", "slobodno vrijeme", "crtati", "pecati", "gitara", "plesti", "slika", "izlet", "kino",
               "pozorište", "koncert", "muzej", "žurka", "igra"],
    "medien": ["novine", "vijesti", "emisija", "kanal", "reklama", "radio", "film", "serija", "televizija",
               "društvene mreže", "video", "snimiti", "pratiti", "objaviti", "glumac"],
    "urlaub": ["tramvaj", "brod", "ljetovanje", "plaža", "spakovati", "ruksak", "smještaj", "turista", "putnik",
               "propustiti", "otkazati", "rezervisati", "red vožnje"],
    "schule": ["vrtić", "osnovna škola", "srednja škola", "razred", "ocjena", "predmet", "matematika", "greška",
               "rječnik", "sveska", "raspust", "užina", "položiti", "ponoviti", "ponavljati"],
    "lernen_studieren": ["zapamtiti", "pamtiti", "računati", "brojati", "znanje", "slovo", "rečenica", "prevesti",
                         "fakultet", "studirati", "profesor", "diplomirati", "upisati se"],
    "berufe": ["kuhar", "frizer", "mehaničar", "zidar", "stolar", "vodoinstalater", "pekar", "čistačica",
               "njegovateljica", "policajac", "vojnik", "vatrogasac", "poljoprivrednik", "programer", "novinar",
               "službenik", "radnik", "poštar"],
    "arbeitsplatz": ["smjena", "gradilište", "sastanak", "zadatak", "nezaposlen", "zaposliti se", "zaposlen",
                     "otpustiti", "penzioner", "pauza", "povišica", "oglas", "zanat", "praksa", "radni dan"],
}

# "auch" genau nach dem Paket (Ajdins Entscheidungen; prije podne und malo
# prije getrennt geschrieben), dazu bei Adjektiven die weibliche und die
# saechliche Form aus "formen".
AUCH = {
    "sekunda": ["sekund"], "trenutak": ["momenat"], "prijepodne": ["prije podne"], "maloprije": ["malo prije"],
    "konačno": ["napokon"], "opet": ["ponovo"], "fudbal": ["nogomet"], "ekipa": ["tim"], "plesti": ["štrikati"],
    "pozorište": ["teatar"], "žurka": ["zabava"], "spakovati": ["spakirati"], "turista": ["turist"],
    "čistačica": ["spremačica"], "poljoprivrednik": ["farmer"], "smjena": ["šihta"], "gradilište": ["bauštela"],
    "nezaposlen": ["nezaposlena", "nezaposleno"], "zaposlen": ["zaposlena", "zaposleno"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {"ruksak": "ranac", "poljoprivrednik": "seljak"}

PAARE = {"ponoviti": "ponavljati", "zapamtiti": "pamtiti"}
# Das Gegenstueck ist seit Paket 8 (06.11.2026) da, "partner" steht an beiden Woertern
SEIT_PAKET8 = {"pobijediti": "pobjeđivati", "crtati": "nacrtati", "snimiti": "snimati", "objaviti": "objavljivati",
               "spakovati": "pakovati", "otkazati": "otkazivati", "položiti": "polagati", "računati": "izračunati",
               "prevesti": "prevoditi", "upisati se": "upisivati se", "zaposliti se": "zapošljavati se"}
# Das Gegenstueck kommt erst in einem spaeteren Paket - bis dahin ohne "partner"
SPAETER = ["plesti", "propustiti", "brojati", "otpustiti"]


def _level(daten, ids):
    k = {x["id"]: x for x in daten["kategorien"]}
    return [k[i] for i in ids]


def _neu(daten):
    return [w for k in _level(daten, ZEIT + LERNEN) for w in k["words"]]


def _alle(daten):
    return [w for k in daten["kategorien"] for w in k["words"]]


def test_sektionen_dreizehn_und_vierzehn_am_ende(grunddaten):
    sektionen = grunddaten["sektionen"]
    assert [s["id"] for s in sektionen][12:14] == ["zeitfreizeit", "lernenarbeiten"]
    assert sektionen[12]["label"] == "Sektion 13 · Zeit und Freizeit"
    assert sektionen[13]["label"] == "Sektion 14 · Lernen und Arbeiten"
    ids = [k["id"] for k in grunddaten["kategorien"]]
    i = ids.index("zeitangaben")
    assert ids[i:i + 10] == ZEIT + LERNEN, "hinter Sektion 12, seit 06.11.2026 folgen die Sektionen 15 bis 17"
    assert ids[i - 1] == "gesund_leben"
    assert [k["id"] for k in grunddaten["kategorien"] if k["sektion"] == "zeitfreizeit"] == ZEIT
    assert [k["id"] for k in grunddaten["kategorien"] if k["sektion"] == "lernenarbeiten"] == LERNEN
    assert list(WOERTER) == ZEIT + LERNEN
    assert sum(len(k["words"]) for k in _level(grunddaten, ZEIT + LERNEN)) == 300
    assert sum(len(k["words"]) for k in _level(grunddaten, ZEIT)) == 178


def test_jedes_wort_steht_vor_seinem_beispielsatz(grunddaten):
    for k in _level(grunddaten, ZEIT + LERNEN):
        assert k["reihenfolge"] is True, k["id"]
        assert 20 <= len(k["words"]) <= 40, k["id"]
        woerter = k["words"]
        assert [w["bs"] for w in woerter[0::2]] == WOERTER[k["id"]], k["id"]
        for wort, satz in zip(woerter[0::2], woerter[1::2]):
            assert re.search(r"[.!?]$", satz["bs"]) and re.search(r"[.!?]$", satz["de"]), satz
            assert satz["bs"][:1].isupper() and satz["de"][:1].isupper(), satz
            assert "partner" not in satz and "auch" not in satz, satz
            assert satz["bs"] != wort["bs"], satz


def test_auch_genau_nach_dem_paket(grunddaten):
    neu = {w["bs"]: w for w in _neu(grunddaten)}
    assert {bs: w["auch"] for bs, w in neu.items() if w.get("auch")} == AUCH
    for w in neu.values():
        assert " / " not in w["bs"], w["bs"]     # Paket 4 hat keine Doppelform
        for a in w.get("auch", []):
            assert a != w["bs"], w["bs"]


@pytest.mark.parametrize("wort, form", sorted(ZAEHLT_NICHT.items()))
def test_was_ajdin_ausgeschlossen_hat_zaehlt_nicht(grunddaten, wort, form):
    """ranac ist nach Ajdin serbisch, seljak ist nicht der Landwirt."""
    w = {x["bs"]: x for x in _neu(grunddaten)}[wort]
    assert form not in w.get("auch", [])
    assert not [x for x in _alle(grunddaten) if form in x["bs"].split(" / ") or form in x.get("auch", [])], form


def test_paare_und_spaetere_gegenstuecke(grunddaten):
    alle = _alle(grunddaten)
    neu = {w["bs"]: w for w in _neu(grunddaten)}
    soll = dict(SEIT_PAKET8)
    for a, b in PAARE.items():
        soll[a], soll[b] = b, a
    assert {b: w["partner"] for b, w in neu.items() if w.get("partner")} == soll
    for wort in SPAETER:
        assert "partner" not in neu[wort], wort
        assert not [x for x in alle if x.get("partner") == wort], wort


@pytest.mark.parametrize("bs, kennungen", [
    ("vrijeme", ["wetter:vrijeme", "zeit:vrijeme"]),
    ("jezik", ["sprache:jezik", "zunge:jezik"]),
])
def test_gleiche_schreibung_zwei_kennungen(alle_daten, grunddaten, bs, kennungen):
    """Gleiches bs, verschiedene Kennung: distractors() schliesst dasselbe bs
    aus, und in keiner Sprache stehen die beiden Bedeutungen gleich da."""
    assert sorted(w["id"] for w in _alle(grunddaten) if w["bs"] == bs) == kennungen
    for code, daten in alle_daten.items():
        bed = [w["de"].lower() for w in _alle(daten) if w["bs"] == bs]
        assert len(set(bed)) == 2, (code, bed)


@pytest.mark.parametrize("a, b", [
    ("radio:radio", "ich habe gearbeitet (m/w):radio sam / radila sam"),
    ("spiel (match):utakmica", "spiel (zum spielen):igra"),
    ("feuerwehrmann:vatrogasac", "feuerwehr:vatrogasci"),
    ("eher / vorher:ranije", "früher:prije"),
    ("das fernsehen:televizija", "fernseher:televizor"),
    ("das wissen:znanje", "wissen:znati"),
    ("schauspieler:glumac", "spieler:igrač"),
])
def test_aehnliche_woerter_heissen_ueberall_verschieden(alle_daten, a, b):
    """Pruefbericht, „Nur für den Einbau“: in der Auswahl nicht als gleich
    werten - in keiner Sprache dieselbe Bedeutung."""
    for code, daten in alle_daten.items():
        w = {x["id"]: x["de"] for x in _alle(daten)}
        assert w[a].strip().lower() != w[b].strip().lower(), (code, w[a], w[b])


def test_zukunft_als_wort_nicht_als_zeitform(alle_daten):
    """„Zukunft“ ist auch der Titel der Grammatik zur Zeitform (tr Gelecek
    zaman, nl Toekomende tijd, fr Futur). budućnost bekommt eigene
    Uebersetzungen ueber "woerter" in uebersetzungen.py."""
    soll = {"de": "Zukunft", "en": "future", "tr": "gelecek", "sv": "framtid", "nl": "toekomst", "nb": "framtid",
            "da": "fremtid", "fr": "avenir"}
    for code, daten in alle_daten.items():
        w = {x["bs"]: x["de"] for x in _alle(daten)}
        assert w["budućnost"] == soll[code], code


def test_upravo_und_maloprije_im_tuerkischen_klar_getrennt(alle_daten):
    """Gegenpruefung 01.11.2026: tr hiess upravo „az önce“ und maloprije
    „biraz önce“ - in einer Auswahl nur um „bir“ verschieden. upravo heisst
    jetzt „yeni (az önce)“ wie in „Eve yeni geldim.“"""
    w = {x["bs"]: x["de"] for x in _alle(alle_daten["tr"])}
    assert w["upravo"] == "yeni (az önce)"
    assert w["maloprije"] == "biraz önce"
    assert "Eve yeni geldim." in w.values()


def test_franzoesischer_tipp_arbeitsplatz_passt_zu_smjena(alle_daten):
    """Gegenpruefung 01.11.2026: der Tipp begann mit „L'équipe“, smjena
    heisst aber „poste (de travail)“; „équipe“ ist ekipa im Level Sport."""
    k = next(k for k in alle_daten["fr"]["kategorien"] if k["id"] == "arbeitsplatz")
    assert k["tipp"].startswith("Le poste, le chantier"), k["tipp"]
    assert "équipe" not in k["tipp"].lower()
    assert any(w["bs"] == "smjena" and w["de"] == "poste (de travail)" for w in k["words"])


def test_gleiche_bedeutung_im_neuen_teil_nur_bei_paaren(alle_daten):
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
    """Wie in tests/test_paket2.py, fuer die Sektionen 13 und 14. Beispiele:
    sinoć „gestern Abend“ und noćas „heute Nacht“ (en yesterday evening /
    tonight / last night), računati „rechnen“ und brojati „zählen“ (sv
    räkna (matte) / räkna (antal)), navijati und navijač (fr encourager /
    soutenir, supporteur)."""
    de = {(k["id"], w["bs"]): w["de"] for k in grunddaten["kategorien"] for w in k["words"]}
    gefunden = []
    for code, daten in alle_daten.items():
        alle = _alle(daten)
        paare = {frozenset((w["bs"], w["partner"])) for w in alle if w.get("partner")}
        for k in daten["kategorien"]:
            if k["sektion"] not in ("zeitfreizeit", "lernenarbeiten"):
                continue
            for i, a in enumerate(k["words"]):
                for b in k["words"][i + 1:]:
                    if frozenset((a["bs"], b["bs"])) in paare:
                        continue
                    gleich = _teile_gleich(a["de"], b["de"])
                    if gleich and not _teile_gleich(de[(k["id"], a["bs"])], de[(k["id"], b["bs"])]):
                        gefunden.append((code, k["id"], a["bs"], b["bs"], sorted(gleich)))
    assert not gefunden, gefunden
