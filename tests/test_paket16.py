# -*- coding: utf-8 -*-
"""Wortschatz-Paket 16 (07.11.2026): Sektion 26 · Gesundheit und Sport.

165 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_16.json, b2_2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- začin (Gewürz) und začiniti (würzen) neben začini (Gewürze) aus der App: začini zaehlt
  bei začin nicht und steht nie mit ihnen in einer Auswahl (NIE_NEBENEINANDER);
- Einzahl gezeigt, Mehrzahl zaehlt mit (crijeva, obrve, bore, tegobe, namirnice, vlakna);
- eine Form allein genannt: die andere zaehlt nicht (Nachfrage 1 B, Paket 15 bis 20).

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["koerper_genauer", "augenbraue_knoechel", "krankheiten", "asthma_migraene", "aerzte_krankenhaus",
         "chirurgie_pflege", "leiden_lindern", "geburt_behandlung", "psyche_wohlbefinden",
         "stress_erschoepfung", "sport_wettkampf", "trainieren_siegen", "ernaehrung", "kalorien_gewuerze"]
SEKTION = {
    "koerper_genauer": "gesundheitsport", "augenbraue_knoechel": "gesundheitsport",
    "krankheiten": "gesundheitsport", "asthma_migraene": "gesundheitsport",
    "aerzte_krankenhaus": "gesundheitsport", "chirurgie_pflege": "gesundheitsport",
    "leiden_lindern": "gesundheitsport", "geburt_behandlung": "gesundheitsport",
    "psyche_wohlbefinden": "gesundheitsport", "stress_erschoepfung": "gesundheitsport",
    "sport_wettkampf": "gesundheitsport", "trainieren_siegen": "gesundheitsport",
    "ernaehrung": "gesundheitsport", "kalorien_gewuerze": "gesundheitsport",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "koerper_genauer": ["vid", "organizam", "ćelija", "dodir", "crijevo", "hormon", "imunitet", "šaka",
                        "disanje", "dlan", "sluh", "žila"],
    "augenbraue_knoechel": ["obrva", "bora", "znoj", "peta", "probava", "kičma", "rebro", "ožiljak", "palac",
                            "puls", "štitna žlijezda / štitnjača", "gležanj"],
    "krankheiten": ["korona", "poremećaj", "zaraziti", "bakterija", "slijep", "tumor", "hroničan", "oboljeti",
                    "obolijevati", "komplikacija", "tegoba", "krvarenje"],
    "asthma_migraene": ["grč", "akutan", "trovanje", "holesterol", "groznica", "astma", "gluh", "opekotina",
                        "gojaznost", "migrena", "prijelom", "upala pluća", "potres mozga"],
    "aerzte_krankenhaus": ["zdravstveni", "medicinski", "zdravstvo", "doza", "medicina", "prevencija",
                           "klinika", "psiholog", "rehabilitacija", "ambulanta"],
    "chirurgie_pflege": ["psihijatar", "transplantacija", "karantin", "hirurgija", "hirurg", "babica", "gips",
                         "dermatolog", "fizioterapeut", "invalidska kolica", "nosila"],
    "leiden_lindern": ["spavanje", "trpjeti", "pretrpjeti", "zaspati", "dojiti", "ublažiti", "ublažavati",
                       "ljekovit", "otrov", "pogoršati se", "pogoršavati se", "bolovati"],
    "geburt_behandlung": ["pelena", "porođaj", "vakcinisati", "poroditi se", "porađati se", "gušiti se",
                          "ugušiti se", "masaža", "operisati", "novorođenče", "namazati", "mazati", "opeći se"],
    "psyche_wohlbefinden": ["koncentracija", "ovisnost / zavisnost", "psihički", "depresija", "pamćenje",
                            "opustiti se", "opuštati se", "pušenje", "trauma", "uznemiriti", "uznemiravati",
                            "anksioznost"],
    "stress_erschoepfung": ["napet", "nervoza", "joga", "zabrinuti", "zabrinjavati", "pušač", "očaj",
                            "nesanica", "mentalno zdravlje", "terapeut", "usamljenost", "iscrpljen"],
    "sport_wettkampf": ["liga", "meč", "teren", "sportski", "prvenstvo", "takmičenje", "bod", "turnir",
                        "prvak", "finale", "stadion", "udarac"],
    "trainieren_siegen": ["poluvrijeme", "pobjednik", "medalja", "utrka / trka", "trenirati", "bazen",
                          "sportista", "igralište", "trčanje", "takmičiti se", "plivanje", "skijanje"],
    "ernaehrung": ["sastojak", "namirnica", "ishrana / prehrana", "obrok", "protein", "organski", "glad",
                   "vlakno", "prehrambeni", "konzumirati", "mineral"],
    "kalorien_gewuerze": ["kalorija", "željezo / gvožđe", "masnoća", "hranjiv", "masan", "apetit",
                          "ugljikohidrat", "žeđ", "vegetarijanac", "začin", "začiniti"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = set()

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "crijevo": ["crijeva"], "obrva": ["obrve"], "bora": ["bore"], "slijep": ["slijepa", "slijepo"],
    "hroničan": ["hronična", "hronično"], "tegoba": ["tegobe"], "akutan": ["akutna", "akutno"],
    "gluh": ["gluha", "gluho"], "zdravstveni": ["zdravstvena", "zdravstveno"],
    "medicinski": ["medicinska", "medicinsko"], "trpjeti": ["trpiti"], "pretrpjeti": ["pretrpiti"],
    "ljekovit": ["ljekovita", "ljekovito"], "porođaj": ["porod"], "psihički": ["psihička", "psihičko"],
    "napet": ["napeta", "napeto"], "iscrpljen": ["iscrpljena", "iscrpljeno"],
    "sportski": ["sportska", "sportsko"], "namirnica": ["namirnice"], "organski": ["organska", "organsko"],
    "vlakno": ["vlakna"], "prehrambeni": ["prehrambena", "prehrambeno"], "hranjiv": ["hranjiva", "hranjivo"],
    "masan": ["masna", "masno"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "probava": ["varenje"], "opekotina": ["opeklina"], "prijelom": ["prelom"], "karantin": ["karantena"],
    "vakcinisati": ["cijepiti", "vakcinirati"], "operisati": ["operirati"],
    "mentalno zdravlje": ["psihičko zdravlje"], "ugljikohidrat": ["ugljeni hidrat"], "začin": ["začini"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "oboljeti": "obolijevati", "obolijevati": "oboljeti", "trpjeti": "pretrpjeti", "pretrpjeti": "trpjeti",
    "ublažiti": "ublažavati", "ublažavati": "ublažiti", "pogoršati se": "pogoršavati se",
    "pogoršavati se": "pogoršati se", "poroditi se": "porađati se", "porađati se": "poroditi se",
    "gušiti se": "ugušiti se", "ugušiti se": "gušiti se", "namazati": "mazati", "mazati": "namazati",
    "opustiti se": "opuštati se", "opuštati se": "opustiti se", "uznemiriti": "uznemiravati",
    "uznemiravati": "uznemiriti", "zabrinuti": "zabrinjavati", "zabrinjavati": "zabrinuti",
}


def test_zacin_und_zaciniti_neben_zacini(grunddaten, index_html):
    w = {x["bs"]: x for k in grunddaten["kategorien"] for x in k["words"]}
    assert w["začini"]["de"] == "Gewürze" and w["začin"]["de"] == "Gewürz" and w["začiniti"]["de"] == "würzen"
    assert "partner" not in w["začiniti"]
    assert "['začin', 'začini']" in index_html and "['začiniti', 'začini']" in index_html
