# -*- coding: utf-8 -*-
"""Wortschatz-Paket 19 (07.11.2026): Sektion 30 · Handeln und verändern.

169 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_19.json, b2_2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- zehn Gegenstuecke zu Verben aus der App (Level paare_bekannt); "partner" steht an beiden,
  auch am alten Verb. izvršiti hat damit zwei Partner, vršiti und izvršavati;
- sadržavati ist das Gegenstueck zu sadržati (bisher „zählt nicht“), sakrivati das zu
  sakriti; bei skrivati zaehlt sakrivati weiter nicht.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["bewegen_verschieben", "folgen_bewaeltigen", "durchfuehren_schaffen", "anpassen_verstaerken",
         "staerken_verbessern", "verbinden_trennen", "bestimmen_hindern", "menschen_umgehen",
         "erkennen_ausdruecken", "paare_bekannt", "entwicklung_vergleich"]
SEKTION = {
    "bewegen_verschieben": "handelnveraendern", "folgen_bewaeltigen": "handelnveraendern",
    "durchfuehren_schaffen": "handelnveraendern", "anpassen_verstaerken": "handelnveraendern",
    "staerken_verbessern": "handelnveraendern", "verbinden_trennen": "handelnveraendern",
    "bestimmen_hindern": "handelnveraendern", "menschen_umgehen": "handelnveraendern",
    "erkennen_ausdruecken": "handelnveraendern", "paare_bekannt": "handelnveraendern",
    "entwicklung_vergleich": "handelnveraendern",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "bewegen_verschieben": ["uhvatiti", "hvatati", "izvući", "izvlačiti", "prebaciti", "prebacivati",
                            "ubaciti", "ubacivati", "udaljiti", "udaljavati", "ispasti", "ispadati", "naići",
                            "nailaziti", "prići", "prilaziti", "približiti", "približavati"],
    "folgen_bewaeltigen": ["slijediti", "uslijediti", "savladati", "savladavati", "zauzeti", "zauzimati",
                           "odvijati se", "odviti se", "preživjeti", "preživljavati", "boraviti", "valjati",
                           "spadati", "izraditi", "izrađivati"],
    "durchfuehren_schaffen": ["primjenjivati", "primijeniti", "okončati", "realizovati", "izdržati",
                              "izdržavati", "namjeravati", "poništiti", "poništavati", "težiti",
                              "pobrinuti se", "priuštiti", "preduzeti", "preduzimati"],
    "anpassen_verstaerken": ["pretvoriti", "pretvarati", "prilagoditi", "prilagođavati", "svesti", "svoditi",
                             "pojačati", "pojačavati", "reagovati", "olakšati", "olakšavati", "urediti",
                             "uređivati"],
    "staerken_verbessern": ["ojačati", "jačati", "unaprijediti", "unapređivati", "oblikovati", "uskladiti",
                            "usklađivati", "obraditi", "obrađivati", "umanjiti", "umanjivati", "otežati",
                            "otežavati", "kontrolisati", "funkcionisati"],
    "verbinden_trennen": ["vezati", "vezivati", "prikupiti", "prikupljati", "ukloniti", "uklanjati",
                          "dodijeliti", "dodjeljivati", "spojiti", "spajati", "pokriti", "pokrivati",
                          "obuhvatiti", "obuhvatati"],
    "bestimmen_hindern": ["proglasiti", "proglašavati", "ograničiti", "ograničavati", "blokirati", "odbaciti",
                          "odbacivati", "nametnuti", "nametati", "narediti", "naređivati", "raspolagati",
                          "prepustiti", "prepuštati", "pridržavati se", "natjerati", "tjerati"],
    "menschen_umgehen": ["poručiti", "poručivati", "uručiti", "uručivati", "opravdati", "opravdavati",
                         "žaliti se", "požaliti se", "tretirati", "savjetovati", "posavjetovati",
                         "kontaktirati", "tužiti", "zbuniti", "zbunjivati", "kritikovati"],
    "erkennen_ausdruecken": ["nazivati", "iskazati", "iskazivati", "označiti", "označavati", "uočiti",
                             "uočavati", "ugledati", "glasiti", "tumačiti", "protumačiti", "izbiti",
                             "izbijati", "prisjetiti se", "prisjećati se", "proizlaziti", "proizaći",
                             "zvučati"],
    "paare_bekannt": ["zahvaljivati se", "upitati", "proslaviti", "ustvrditi", "izvršavati", "odmoriti se",
                      "viđati", "sadržavati", "izvinjavati se", "sakrivati"],
    "entwicklung_vergleich": ["tok", "pozicija", "pritisak", "reakcija", "stvaranje", "forma", "kretanje",
                              "potez", "kombinacija", "trend", "potencijal", "širenje", "mehanizam",
                              "ravnoteža", "alternativa", "uspon", "poređenje", "uporediti", "upoređivati"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = set()

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "realizovati": ["realizirati"], "preduzeti": ["poduzeti"], "preduzimati": ["poduzimati"],
    "reagovati": ["reagirati"], "kontrolisati": ["kontrolirati"], "funkcionisati": ["funkcionirati"],
    "kritikovati": ["kritizirati"], "poređenje": ["usporedba"], "uporediti": ["usporediti"],
    "upoređivati": ["uspoređivati"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "proizlaziti": ["proizilaziti"], "proizaći": ["proizići"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "uhvatiti": "hvatati", "hvatati": "uhvatiti", "izvući": "izvlačiti", "izvlačiti": "izvući",
    "prebaciti": "prebacivati", "prebacivati": "prebaciti", "ubaciti": "ubacivati", "ubacivati": "ubaciti",
    "udaljiti": "udaljavati", "udaljavati": "udaljiti", "ispasti": "ispadati", "ispadati": "ispasti",
    "naići": "nailaziti", "nailaziti": "naići", "prići": "prilaziti", "prilaziti": "prići",
    "približiti": "približavati", "približavati": "približiti", "slijediti": "uslijediti",
    "uslijediti": "slijediti", "savladati": "savladavati", "savladavati": "savladati", "zauzeti": "zauzimati",
    "zauzimati": "zauzeti", "odvijati se": "odviti se", "odviti se": "odvijati se",
    "preživjeti": "preživljavati", "preživljavati": "preživjeti", "izraditi": "izrađivati",
    "izrađivati": "izraditi", "primjenjivati": "primijeniti", "primijeniti": "primjenjivati",
    "izdržati": "izdržavati", "izdržavati": "izdržati", "poništiti": "poništavati", "poništavati": "poništiti",
    "preduzeti": "preduzimati", "preduzimati": "preduzeti", "pretvoriti": "pretvarati",
    "pretvarati": "pretvoriti", "prilagoditi": "prilagođavati", "prilagođavati": "prilagoditi",
    "svesti": "svoditi", "svoditi": "svesti", "pojačati": "pojačavati", "pojačavati": "pojačati",
    "olakšati": "olakšavati", "olakšavati": "olakšati", "urediti": "uređivati", "uređivati": "urediti",
    "ojačati": "jačati", "jačati": "ojačati", "unaprijediti": "unapređivati", "unapređivati": "unaprijediti",
    "uskladiti": "usklađivati", "usklađivati": "uskladiti", "obraditi": "obrađivati", "obrađivati": "obraditi",
    "umanjiti": "umanjivati", "umanjivati": "umanjiti", "otežati": "otežavati", "otežavati": "otežati",
    "vezati": "vezivati", "vezivati": "vezati", "prikupiti": "prikupljati", "prikupljati": "prikupiti",
    "ukloniti": "uklanjati", "uklanjati": "ukloniti", "dodijeliti": "dodjeljivati",
    "dodjeljivati": "dodijeliti", "spojiti": "spajati", "spajati": "spojiti", "pokriti": "pokrivati",
    "pokrivati": "pokriti", "obuhvatiti": "obuhvatati", "obuhvatati": "obuhvatiti",
    "proglasiti": "proglašavati", "proglašavati": "proglasiti", "ograničiti": "ograničavati",
    "ograničavati": "ograničiti", "odbaciti": "odbacivati", "odbacivati": "odbaciti", "nametnuti": "nametati",
    "nametati": "nametnuti", "narediti": "naređivati", "naređivati": "narediti", "prepustiti": "prepuštati",
    "prepuštati": "prepustiti", "natjerati": "tjerati", "tjerati": "natjerati", "poručiti": "poručivati",
    "poručivati": "poručiti", "uručiti": "uručivati", "uručivati": "uručiti", "opravdati": "opravdavati",
    "opravdavati": "opravdati", "žaliti se": "požaliti se", "požaliti se": "žaliti se",
    "savjetovati": "posavjetovati", "posavjetovati": "savjetovati", "zbuniti": "zbunjivati",
    "zbunjivati": "zbuniti", "iskazati": "iskazivati", "iskazivati": "iskazati", "označiti": "označavati",
    "označavati": "označiti", "uočiti": "uočavati", "uočavati": "uočiti", "tumačiti": "protumačiti",
    "protumačiti": "tumačiti", "izbiti": "izbijati", "izbijati": "izbiti", "prisjetiti se": "prisjećati se",
    "prisjećati se": "prisjetiti se", "proizlaziti": "proizaći", "proizaći": "proizlaziti",
    "zahvaljivati se": "zahvaliti se", "upitati": "pitati", "proslaviti": "slaviti", "ustvrditi": "tvrditi",
    "izvršavati": "izvršiti", "odmoriti se": "odmarati se", "viđati": "vidjeti", "sadržavati": "sadržati",
    "izvinjavati se": "izviniti se", "sakrivati": "sakriti", "uporediti": "upoređivati",
    "upoređivati": "uporediti",
}


PARTNER_ZU_ALTEN = {"zahvaljivati se": "zahvaliti se", "upitati": "pitati", "proslaviti": "slaviti",
                    "ustvrditi": "tvrditi", "izvršavati": "izvršiti", "odmoriti se": "odmarati se",
                    "viđati": "vidjeti", "sadržavati": "sadržati", "izvinjavati se": "izviniti se",
                    "sakrivati": "sakriti"}


def test_paare_bekannt_sind_gegenstuecke_zu_alten_verben(grunddaten):
    k = next(x for x in grunddaten["kategorien"] if x["id"] == "paare_bekannt")
    neu = [w["bs"] for w in k["words"]][0::2]
    assert neu == list(PARTNER_ZU_ALTEN)
    w = {x["bs"]: x for k in grunddaten["kategorien"] for x in k["words"]}
    for a, b in PARTNER_ZU_ALTEN.items():
        assert w[a]["partner"] == b
        if a != "izvršavati":
            assert w[b]["partner"] == a, b


def test_izvrsiti_hat_zwei_partner(grunddaten):
    w = {x["bs"]: x for k in grunddaten["kategorien"] for x in k["words"]}
    zu = sorted(x["bs"] for x in w.values() if x.get("partner") == "izvršiti")
    assert w["izvršiti"]["partner"] == "vršiti" and zu == ["izvršavati", "vršiti"]
