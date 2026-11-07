# -*- coding: utf-8 -*-
"""Wortschatz-Paket 20 (07.11.2026): Sektion 31 · Genauer sagen.

163 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_20.json, b2_2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- posve ist gestrichen (sasvim und potpuno reichen), U pravu si. zeigt die App, Imaš pravo.
  zaehlt mit; Neka, hvala. mit Ne, hvala.;
- dosad / dosada und zasad / zasada: nur diese Formen zaehlen (Nachfrage 2 B); dosada
  (Langeweile) bleibt ein eigenes Wort, nie mit dosad / dosada in einer Auswahl.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["wie_sicher", "ganz_teilweise", "wie_man_tut", "wann_wie_lange", "immer_zukunft", "wo_wohin",
         "gut_schlecht", "fest_sichtbar", "streng_zuverlaessig", "feste_wendungen", "keine_ahnung",
         "mengen_masse"]
SEKTION = {
    "wie_sicher": "genauersagen", "ganz_teilweise": "genauersagen", "wie_man_tut": "genauersagen",
    "wann_wie_lange": "genauersagen", "immer_zukunft": "genauersagen", "wo_wohin": "genauersagen",
    "gut_schlecht": "genauersagen", "fest_sichtbar": "genauersagen", "streng_zuverlaessig": "genauersagen",
    "feste_wendungen": "genauersagen", "keine_ahnung": "genauersagen", "mengen_masse": "genauersagen",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "wie_sicher": ["očito", "makar", "definitivno", "apsolutno", "relativno", "itekako", "krajnje", "većinom",
                   "generalno", "ukratko", "izrazito", "doslovno"],
    "ganz_teilweise": ["skroz", "usput", "donekle", "približno", "totalno", "nedovoljno", "suviše", "uzalud",
                       "djelimično", "nesumnjivo", "naizgled", "pretjerano"],
    "wie_man_tut": ["direktno", "automatski", "međusobno", "pravilno", "postepeno", "namjerno", "samostalno",
                    "uporno", "naprosto", "uredno", "ručno", "dobrovoljno", "napamet", "tajno", "pismeno",
                    "usmeno"],
    "wann_wie_lange": ["početkom", "krajem", "svakodnevno", "ubrzo", "odavno", "najprije", "dosad / dosada",
                       "unaprijed", "sredinom", "povremeno", "privremeno"],
    "immer_zukunft": ["neprestano", "oduvijek", "zasad / zasada", "iznenada", "naknadno", "ubuduće", "najzad",
                      "sutradan", "nakratko", "zamalo", "danju"],
    "wo_wohin": ["van", "usred", "svugdje", "nasuprot", "duž", "ovamo", "iznutra", "nedaleko", "odatle",
                 "odavde", "drugdje", "izvana", "odozgo"],
    "gut_schlecht": ["kvalitetan", "savršen", "idealan", "strašan", "divan", "omiljen", "neobičan",
                     "adekvatan", "štetan", "izuzetan", "nevjerovatan", "čuven", "pogodan", "zabavan", "nužan",
                     "prihvatljiv", "ružan", "užasan", "nepotreban"],
    "fest_sichtbar": ["prisutan", "stalan", "miran", "jednak", "klasičan", "kompletan", "vidljiv",
                      "specifičan", "čvrst", "rijedak", "blag", "moćan"],
    "streng_zuverlaessig": ["trajan", "lud", "ravan", "sitan", "ispravan", "oštar", "pouzdan", "strog",
                            "uobičajen", "okrugao", "mračan", "gust", "inteligentan"],
    "feste_wendungen": ["bez obzira", "prije svega", "između ostalog", "u međuvremenu", "što prije",
                        "u svakom slučaju", "Nema veze.", "kako god", "sve u svemu", "iz dana u dan",
                        "na kraju krajeva", "s vremena na vrijeme"],
    "keine_ahnung": ["Svaka čast!", "Nemam pojma.", "korak po korak", "Nema šanse.", "prije ili kasnije",
                     "što se mene tiče", "malo po malo", "za svaki slučaj", "Drži se!", "U pravu si.",
                     "Poslužite se!", "Neka, hvala."],
    "mengen_masse": ["posto", "dvojica", "desetak", "prosječan", "tona", "mnoštvo", "trojica", "troje",
                     "obojica", "minimum", "centimetar", "manjak", "dvadesetak", "maksimum", "nekolicina",
                     "komadić", "kašičica", "zalogaj", "gutljaj", "dunum"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = set()

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "kvalitetan": ["kvalitetna", "kvalitetno"], "savršen": ["savršena", "savršeno"],
    "idealan": ["idealna", "idealno"], "strašan": ["strašna", "strašno"], "divan": ["divna", "divno"],
    "omiljen": ["omiljena", "omiljeno"], "neobičan": ["neobična", "neobično"],
    "adekvatan": ["adekvatna", "adekvatno"], "štetan": ["štetna", "štetno"],
    "izuzetan": ["izuzetna", "izuzetno"], "nevjerovatan": ["nevjerovatna", "nevjerovatno"],
    "čuven": ["čuvena", "čuveno"], "pogodan": ["pogodna", "pogodno"], "zabavan": ["zabavna", "zabavno"],
    "nužan": ["nužna", "nužno"], "prihvatljiv": ["prihvatljiva", "prihvatljivo"], "ružan": ["ružna", "ružno"],
    "užasan": ["užasna", "užasno"], "nepotreban": ["nepotrebna", "nepotrebno"],
    "prisutan": ["prisutna", "prisutno"], "stalan": ["stalna", "stalno"], "miran": ["mirna", "mirno"],
    "jednak": ["jednaka", "jednako"], "klasičan": ["klasična", "klasično"],
    "kompletan": ["kompletna", "kompletno"], "vidljiv": ["vidljiva", "vidljivo"],
    "specifičan": ["specifična", "specifično"], "čvrst": ["čvrsta", "čvrsto"],
    "rijedak": ["rijetka", "rijetko"], "blag": ["blaga", "blago"], "moćan": ["moćna", "moćno"],
    "trajan": ["trajna", "trajno"], "lud": ["luda", "ludo"], "ravan": ["ravna", "ravno"],
    "sitan": ["sitna", "sitno"], "ispravan": ["ispravna", "ispravno"], "oštar": ["oštra", "oštro"],
    "pouzdan": ["pouzdana", "pouzdano"], "strog": ["stroga", "strogo"],
    "uobičajen": ["uobičajena", "uobičajeno"], "okrugao": ["okrugla", "okruglo"],
    "mračan": ["mračna", "mračno"], "gust": ["gusta", "gusto"],
    "inteligentan": ["inteligentna", "inteligentno"], "U pravu si.": ["Imaš pravo."],
    "Neka, hvala.": ["Ne, hvala."], "prosječan": ["prosječna", "prosječno"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "doslovno": ["doslovce"], "djelimično": ["djelomično"], "postepeno": ["postupno"],
    "dosad / dosada": ["do sada", "do sad"], "zasad / zasada": ["za sada", "za sad"],
    "nakratko": ["na kratko"], "zamalo": ["umalo"], "svugdje": ["svuda"], "izvana": ["spolja"],
    "s vremena na vrijeme": ["sa vremena na vrijeme"], "kašičica": ["žličica"], "dunum": ["dulum"],
}

# Partner je Wort, wie im Paket.
PARTNER = {}


def test_posve_gestrichen_und_dosada_daneben(grunddaten, index_html):
    w = {x["bs"]: x["de"] for k in grunddaten["kategorien"] for x in k["words"]}
    assert "posve" not in w
    assert w["dosada"] == "Langeweile" and w["dosad / dosada"] == "bisher"
    assert "['dosad / dosada', 'dosada']" in index_html


def test_alle_sektionen(grunddaten):
    """31 Sektionen, 295 Level seit den Paketen 10 bis 20 (07.11.2026); Stufe B2 hinter B1."""
    assert len(grunddaten["sektionen"]) == 31
    assert len(grunddaten["kategorien"]) == 295
    s = [x["id"] for x in grunddaten["sektionen"]]
    assert s[16] == "wiewowann" and s[17] == "denkenmeinen" and s[-1] == "genauersagen"
    assert grunddaten["kategorien"][-1]["id"] == "mengen_masse"
