# -*- coding: utf-8 -*-
"""Wortschatz-Paket 18 (07.11.2026): Sektion 28 · Stadt, Verkehr und Reisen, Sektion 29 · Land, Tiere und Pflanzen.

169 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_18.json, b2_2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- dvorana (große Halle) und sala (kleine Halle) sind zwei Woerter (Ajdin);
- prijevoz / prevoz, prijelaz / prelaz und ihre Wendungen mit zwei Formen (Nachfrage 4 B);
- apartman: der Satz sagt unajmili, weil iznajmiti jetzt vermieten heisst.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["in_der_stadt", "strassen_bahn", "kreisverkehr_faehre", "autofahren", "unfaelle_pannen",
         "reisen_unterkunft", "ankommen_ansehen", "landschaft_boden", "ozean_schlucht", "jagen_fischen",
         "tiere_genauer", "pflanzen_anbau", "ernten_pflanzen"]
SEKTION = {
    "in_der_stadt": "stadtreisen", "strassen_bahn": "stadtreisen", "kreisverkehr_faehre": "stadtreisen",
    "autofahren": "stadtreisen", "unfaelle_pannen": "stadtreisen", "reisen_unterkunft": "stadtreisen",
    "ankommen_ansehen": "stadtreisen", "landschaft_boden": "landtiere", "ozean_schlucht": "landtiere",
    "jagen_fischen": "landtiere", "tiere_genauer": "landtiere", "pflanzen_anbau": "landtiere",
    "ernten_pflanzen": "landtiere",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "in_der_stadt": ["gradski", "lokacija", "zona", "park", "dvorana", "infrastruktura", "trg", "objekat",
                     "središte", "kontejner", "pješak", "gradić", "trotoar / pločnik", "čaršija", "predgrađe",
                     "česma", "periferija", "mahala", "pješački prijelaz / pješački prelaz", "sala"],
    "strassen_bahn": ["linija", "cesta", "traka", "kamion", "tunel", "luka", "kolovoz", "prijevoz / prevoz",
                      "pruga", "željeznica", "kombi"],
    "kreisverkehr_faehre": ["motocikl", "putokaz", "krivina", "žičara", "putarina", "kružni tok", "trajekt",
                            "trolejbus", "javni prijevoz / javni prevoz", "željeznička stanica",
                            "prijelaz / prelaz"],
    "autofahren": ["automobil", "servis", "ubrzati", "ubrzavati", "usporiti", "usporavati", "sudar", "dizel",
                   "volan", "mjenjač", "kočiti", "zakočiti"],
    "unfaelle_pannen": ["branik", "udes", "preteći", "preticati", "far", "suvozač", "sudariti se",
                        "sudarati se", "točak", "gepek / prtljažnik", "poledica", "autoškola"],
    "reisen_unterkunft": ["turistički", "turizam", "kamp", "posjetilac", "destinacija", "vodič", "pilot",
                          "obilazak", "aranžman", "otputovati", "šator", "sletjeti", "slijetati"],
    "ankommen_ansehen": ["apartman", "kupanje", "poletjeti", "polijetati", "noćenje", "doputovati",
                         "fotoaparat", "suvenir", "razgledati", "razgledavati", "recepcija",
                         "granični prijelaz / granični prelaz"],
    "landschaft_boden": ["tlo", "zlato", "val", "zora", "sjena", "daljina", "drveće", "kamenje", "blato",
                         "srebro", "njiva", "pustinja", "mraz", "kopno"],
    "ozean_schlucht": ["planinar", "okean", "rosa", "vinograd", "pejzaž", "kanjon", "zaljev / zaliv", "ušće",
                       "padina", "vulkan", "lavina", "ravnica", "močvara", "klisura"],
    "jagen_fischen": ["lav", "lov", "kornjača", "lovac", "ribolov / pecanje", "loviti", "uloviti", "ovan",
                      "košnica", "insekt", "stado", "ribar"],
    "tiere_genauer": ["majmun", "jarac", "kit", "slon", "školjka", "govedo", "ženka", "delfin", "tigar",
                      "jato", "mužjak", "deva"],
    "pflanzen_anbau": ["plod", "stablo", "kora", "uzgoj", "ruža", "sjeme", "pšenica", "duhan", "lišće",
                       "sijati", "posijati", "uzgajati", "uzgojiti"],
    "ernten_pflanzen": ["breza", "žito", "ljiljan", "sadnica", "brati", "ubrati", "bor", "saditi", "posaditi",
                        "berba", "hrast", "gnojivo / đubrivo", "žetva"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = set()

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "gradski": ["gradska", "gradsko"], "turistički": ["turistička", "turističko"], "val": ["talas"],
    "uzgajati": ["gajiti"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "objekat": ["objekt"], "putarina": ["cestarina"], "preteći": ["prestići"],
    "preticati": ["pretjecati", "prestizati"], "točak": ["kotač"], "autoškola": ["auto škola"],
    "posjetilac": ["posjetitelj"], "sjena": ["sjenka"], "okean": ["ocean"], "pejzaž": ["krajolik"],
    "duhan": ["duvan"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "ubrzati": "ubrzavati", "ubrzavati": "ubrzati", "usporiti": "usporavati", "usporavati": "usporiti",
    "kočiti": "zakočiti", "zakočiti": "kočiti", "preteći": "preticati", "preticati": "preteći",
    "sudariti se": "sudarati se", "sudarati se": "sudariti se", "sletjeti": "slijetati",
    "slijetati": "sletjeti", "poletjeti": "polijetati", "polijetati": "poletjeti",
    "razgledati": "razgledavati", "razgledavati": "razgledati", "loviti": "uloviti", "uloviti": "loviti",
    "sijati": "posijati", "posijati": "sijati", "uzgajati": "uzgojiti", "uzgojiti": "uzgajati",
    "brati": "ubrati", "ubrati": "brati", "saditi": "posaditi", "posaditi": "saditi",
}


def test_dvorana_und_sala(grunddaten):
    w = {x["bs"]: x["de"] for k in grunddaten["kategorien"] for x in k["words"]}
    assert w["dvorana"] == "große Halle" and w["sala"] == "kleine Halle"


def test_apartman_mit_unajmiti(grunddaten):
    saetze = [x["bs"] for k in grunddaten["kategorien"] for x in k["words"]]
    assert "Unajmili smo apartman blizu plaže." in saetze
