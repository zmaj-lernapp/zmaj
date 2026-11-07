# -*- coding: utf-8 -*-
"""Wortschatz-Paket 17 (07.11.2026): Sektion 27 · Schule und Wissen.

170 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_17.json, b2_2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- magistar (altes System) und master, tabela (Tabelle) und tablica (Schild), izum
  (Erfindung) und pronalazak (Fund) sind je zwei Woerter (Ajdin);
- prepisati (abschreiben) und propisati (verschreiben) zaehlen nicht fuereinander;
- prijevod / prevod und naglasak / akcenat mit zwei Formen.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
import pytest

from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["schule_klasse", "abitur_klassenfahrt", "an_der_uni", "abschluss_titel", "faecher_wissen",
         "forschen_messen", "entdecken_erfinden", "lesen_aussprechen", "sprache_grammatik",
         "reden_verstaendigen", "beschreiben_erklaeren", "begruenden_zusammenfassen"]
SEKTION = {
    "schule_klasse": "schulewissen", "abitur_klassenfahrt": "schulewissen", "an_der_uni": "schulewissen",
    "abschluss_titel": "schulewissen", "faecher_wissen": "schulewissen", "forschen_messen": "schulewissen",
    "entdecken_erfinden": "schulewissen", "lesen_aussprechen": "schulewissen",
    "sprache_grammatik": "schulewissen", "reden_verstaendigen": "schulewissen",
    "beschreiben_erklaeren": "schulewissen", "begruenden_zusammenfassen": "schulewissen",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "schule_klasse": ["školski", "test", "pisanje", "čitanje", "klupa", "gimnazija", "kalendar", "udžbenik",
                      "pohađati", "tabla", "opravdanje", "srednjoškolac"],
    "abitur_klassenfahrt": ["učionica", "izostanak", "maturant", "prepisati", "prepisivati", "matura",
                            "podučavati", "ekskurzija", "lektira", "kreda", "školarina", "gumica"],
    "an_der_uni": ["institut", "studij", "akademija", "predavanje", "poglavlje", "akademski", "prezentacija",
                   "zbirka", "literatura", "upis", "seminar", "citirati"],
    "abschluss_titel": ["stipendija", "predavač", "priručnik", "citat", "rektor", "esej", "magistar",
                        "knjižara", "sažetak", "semestar", "doktorat", "diplomski rad", "master"],
    "faecher_wissen": ["filozofija", "arhitektura", "psihologija", "filozof", "fizika", "matematički",
                       "sociologija", "hemija", "biologija", "informatika", "geografija", "gramatika",
                       "geometrija", "astronomija"],
    "forschen_messen": ["metoda", "naučni", "svojstvo", "ispitivanje", "tabela", "kiselina", "naučnik",
                        "materija", "provjera", "mjerenje", "istraživač", "istraživati", "istražiti",
                        "statistika", "teza", "definisati"],
    "entdecken_erfinden": ["fenomen", "definicija", "formula", "otkriće", "laboratorij", "ispitati",
                           "ispitivati", "proučiti", "proučavati", "eksperiment", "gen", "izmisliti",
                           "izmišljati", "izum", "atom", "jednačina", "pronalazak"],
    "lesen_aussprechen": ["lik", "sastav", "književni", "tumačenje", "stih", "dnevnik", "prijevod / prevod",
                          "mit", "izgovoriti", "izgovarati", "naglasak / akcenat", "slog", "izgovor", "mašta",
                          "bajka"],
    "sprache_grammatik": ["govornik", "glagol", "imenica", "zamjenica", "ćirilica", "poslovica", "pravopis",
                          "prevodilac", "skraćenica", "množina", "dijalekt", "pridjev", "latinica", "jednina",
                          "padež"],
    "reden_verstaendigen": ["komunikacija", "govor", "zvuk", "razmjena", "obraćanje", "čestitka", "napomena",
                            "upit", "natpis", "sagovornik", "komunicirati", "primjedba", "debata", "gest",
                            "bilješka", "kompliment", "pozivnica", "tablica"],
    "beschreiben_erklaeren": ["naziv", "simbol", "opis", "praktičan", "kriterij", "cjelina", "prikaz",
                              "detaljan", "logika", "složen", "obrazloženje", "primjerak", "nijansa"],
    "begruenden_zusammenfassen": ["suprotnost", "crtež", "teorijski", "ilustracija", "razumljiv", "sličnost",
                                  "nejasan", "obrazložiti", "obrazlagati", "razjasniti", "pojašnjenje",
                                  "skica", "sažeti"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = set()

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "školski": ["školska", "školsko"], "studij": ["studije"], "akademski": ["akademska", "akademsko"],
    "matematički": ["matematička", "matematičko"], "naučni": ["naučna", "naučno"],
    "laboratorij": ["laboratorija"], "književni": ["književna", "književno"], "dijalekt": ["dijalekat"],
    "praktičan": ["praktična", "praktično"], "detaljan": ["detaljna", "detaljno"],
    "složen": ["složena", "složeno"], "teorijski": ["teorijska", "teorijsko"],
    "razumljiv": ["razumljiva", "razumljivo"], "nejasan": ["nejasna", "nejasno"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "prepisati": ["propisati"], "diplomski rad": ["diplomski"], "hemija": ["kemija"], "metoda": ["metod"],
    "naučni": ["znanstveni", "znanstvena", "znanstveno"], "naučnik": ["znanstvenik"],
    "definisati": ["definirati"], "jednačina": ["jednadžba"], "prevodilac": ["prevoditelj"],
    "sagovornik": ["sugovornik"], "gest": ["gesta"], "bilješka": ["zabilješka"], "kriterij": ["kriterijum"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "prepisati": "prepisivati", "prepisivati": "prepisati", "istraživati": "istražiti",
    "istražiti": "istraživati", "ispitati": "ispitivati", "ispitivati": "ispitati", "proučiti": "proučavati",
    "proučavati": "proučiti", "izmisliti": "izmišljati", "izmišljati": "izmisliti", "izgovoriti": "izgovarati",
    "izgovarati": "izgovoriti", "obrazložiti": "obrazlagati", "obrazlagati": "obrazložiti",
}


@pytest.mark.parametrize("a, b", [("magistar", "master"), ("tabela", "tablica"), ("izum", "pronalazak")])
def test_zwei_woerter_mit_eigener_bedeutung(grunddaten, a, b):
    w = {x["bs"]: x["de"] for k in grunddaten["kategorien"] for x in k["words"]}
    assert w[a] != w[b], (a, b)


def test_prepisati_und_propisati(grunddaten):
    w = {x["bs"]: x for k in grunddaten["kategorien"] for x in k["words"]}
    assert w["prepisati"]["de"] == "abschreiben" and w["propisati"]["de"] != "abschreiben"
    assert "propisati" not in w["prepisati"].get("auch", []) and "prepisati" not in w["propisati"].get("auch", [])
