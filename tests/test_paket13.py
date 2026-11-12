# -*- coding: utf-8 -*-
"""Wortschatz-Paket 13 (07.11.2026): Sektion 21 · Medien und Kultur, Sektion 22 · Umwelt und Technik.

155 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_13.json, b2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- arhiv (Institution, Gebaeude) und arhiva (Dokumentensammlung) sind zwei Woerter (Ajdin);
- odigrati ist das Gegenstueck zu igrati aus der App, "partner" steht an beiden;
- gas / plin, okoliš / životna sredina, planet / planeta, saopćenje / saopštenje mit zwei
  Formen; nuklearni und digitalni in der langen Form.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["zeitung_fernsehen", "berichten_verbreiten", "werbung", "theater_musik", "regie_premiere",
         "buecher_kunst", "literatur_malerei", "geschichte_frueher", "klima_energie", "naturkatastrophen",
         "computer_dateien"]
SEKTION = {
    "zeitung_fernsehen": "medienkultur", "berichten_verbreiten": "medienkultur", "werbung": "medienkultur",
    "theater_musik": "medienkultur", "regie_premiere": "medienkultur", "buecher_kunst": "medienkultur",
    "literatur_malerei": "medienkultur", "geschichte_frueher": "medienkultur",
    "klima_energie": "umwelttechnik", "naturkatastrophen": "umwelttechnik",
    "computer_dateien": "umwelttechnik",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "zeitung_fernsehen": ["medij", "članak", "portal", "naslov", "medijski", "izdanje", "intervju", "objava",
                          "kamera", "časopis", "saopćenje / saopštenje", "novost"],
    "berichten_verbreiten": ["saopćiti / saopštiti", "saopćavati / saopštavati", "urednik", "izvijestiti",
                             "izvještavati", "snimak", "anketa", "epizoda", "događaj", "izraz", "zabilježiti",
                             "bilježiti", "širiti", "proširiti"],
    "werbung": ["publika", "kampanja", "popularan", "promocija", "brend", "uzorak", "marketing", "atraktivan",
                "ugled", "oglašavanje", "slogan", "privući", "privlačiti"],
    "theater_musik": ["festival", "scena", "nastup", "odigrati", "manifestacija", "prisustvovati", "muzički",
                      "nastupiti", "nastupati", "drama", "glumica"],
    "regie_premiere": ["bend", "svečanost", "režija", "glumiti", "ulaznica", "režiser / reditelj", "premijera",
                       "izvesti", "izvoditi", "obilježiti", "obilježavati"],
    "buecher_kunst": ["predstavljati", "djelo", "nagrada", "autor", "kulturni", "predstaviti", "tradicionalan",
                      "stil", "savremen", "roman"],
    "literatur_malerei": ["književnost", "umjetnički", "biblioteka", "umjetnik", "prikazivati", "prikazati",
                          "poezija", "galerija", "pjesnik", "baština", "slikar"],
    "geschichte_frueher": ["kralj", "historijski", "carstvo", "revolucija", "legenda", "arhiv", "kraljica",
                           "civilizacija", "vladar", "osmanski", "tvrđava", "srednjovjekovni", "ustanak",
                           "stećak", "dvorac", "historičar", "arhiva"],
    "klima_energie": ["energetski", "atmosfera", "resurs", "otpad", "gas / plin", "nafta",
                      "okoliš / životna sredina", "očuvanje", "nuklearni", "rudnik", "ekološki",
                      "planet / planeta", "klimatski", "svemir", "solarni", "zagađenje", "elektrana",
                      "obnovljiv", "zagrijavanje", "biće"],
    "naturkatastrophen": ["pandemija", "poplava", "stradati", "katastrofa", "srušiti", "rušiti", "spašavanje",
                          "epidemija", "zaraza", "ugroziti", "ugrožavati", "zemljotres", "klizište",
                          "nevrijeme", "evakuacija", "sklonište", "suša"],
    "computer_dateien": ["baza", "platforma", "digitalni", "profil", "verzija", "link", "elektronski",
                         "kreirati", "instalacija", "pretraga", "inovacija", "softver", "testirati",
                         "memorija", "izbrisati", "kliknuti", "datoteka", "instalirati", "pretraživač"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = set()

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "medijski": ["medijska", "medijsko"], "popularan": ["popularna", "popularno"],
    "atraktivan": ["atraktivna", "atraktivno"], "muzički": ["muzička", "muzičko"],
    "kulturni": ["kulturna", "kulturno"], "tradicionalan": ["tradicionalna", "tradicionalno"],
    "savremen": ["savremena", "savremeno"], "umjetnički": ["umjetnička", "umjetničko"],
    "historijski": ["historijska", "historijsko"], "osmanski": ["osmanska", "osmansko"],
    "srednjovjekovni": ["srednjovjekovna", "srednjovjekovno"], "energetski": ["energetska", "energetsko"],
    "nuklearni": ["nuklearna", "nuklearno"], "ekološki": ["ekološka", "ekološko"],
    "klimatski": ["klimatska", "klimatsko"], "solarni": ["solarna", "solarno"],
    "obnovljiv": ["obnovljiva", "obnovljivo"], "zemljotres": ["potres"],
    "digitalni": ["digitalna", "digitalno"], "elektronski": ["elektronska", "elektronsko"],
    "datoteka": ["fajl"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "nuklearni": ["nuklearan"], "digitalni": ["digitalan"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "saopćiti / saopštiti": "saopćavati / saopštavati", "saopćavati / saopštavati": "saopćiti / saopštiti",
    "izvijestiti": "izvještavati", "izvještavati": "izvijestiti", "zabilježiti": "bilježiti",
    "bilježiti": "zabilježiti", "širiti": "proširiti", "proširiti": "širiti", "privući": "privlačiti",
    "privlačiti": "privući", "odigrati": "igrati", "nastupiti": "nastupati", "nastupati": "nastupiti",
    "izvesti": "izvoditi", "izvoditi": "izvesti", "obilježiti": "obilježavati", "obilježavati": "obilježiti",
    "predstavljati": "predstaviti", "predstaviti": "predstavljati", "prikazivati": "prikazati",
    "prikazati": "prikazivati", "srušiti": "rušiti", "rušiti": "srušiti", "ugroziti": "ugrožavati",
    "ugrožavati": "ugroziti",
}


def test_arhiv_und_arhiva_sind_zwei_woerter(grunddaten):
    w = {x["bs"]: x["de"] for k in grunddaten["kategorien"] for x in k["words"]}
    assert w["arhiv"] == "Archiv (Institution, Gebäude)" and w["arhiva"] == "Archiv (Dokumentensammlung)"


def test_igrati_hat_sein_gegenstueck(grunddaten):
    w = {x["bs"]: x for k in grunddaten["kategorien"] for x in k["words"]}
    assert w["igrati"]["partner"] == "odigrati" and w["odigrati"]["partner"] == "igrati"
