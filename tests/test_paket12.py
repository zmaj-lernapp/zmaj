# -*- coding: utf-8 -*-
"""Wortschatz-Paket 12 (07.11.2026): Sektion 20 · Arbeit und Wirtschaft.

153 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_12.json, b2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- zaposlenik / uposlenik ist kein zweites Wort: Die Anzeige in der App (Level
  arbeitsvertrag) hat die zweite Form bekommen, der Lernstand zieht ueber UMBENANNT mit,
  hier steht nur der Satz (NUR_SATZ);
- preduzetnik wie preduzeće (poduzetnik zaehlt nicht), sticati / stjecati mit zwei Formen.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["firma_leitung", "abteilung_mitarbeiter", "produktion_handel", "liefern_beschaffen", "geld_preise",
         "wachstum_rueckgang", "schulden_verluste", "anlegen_vermoegen", "investieren_beitragen",
         "beruf_karriere", "aufstieg_weiterbildung", "rechte_arbeit"]
SEKTION = {
    "firma_leitung": "arbeitwirtschaft", "abteilung_mitarbeiter": "arbeitwirtschaft",
    "produktion_handel": "arbeitwirtschaft", "liefern_beschaffen": "arbeitwirtschaft",
    "geld_preise": "arbeitwirtschaft", "wachstum_rueckgang": "arbeitwirtschaft",
    "schulden_verluste": "arbeitwirtschaft", "anlegen_vermoegen": "arbeitwirtschaft",
    "investieren_beitragen": "arbeitwirtschaft", "beruf_karriere": "arbeitwirtschaft",
    "aufstieg_weiterbildung": "arbeitwirtschaft", "rechte_arbeit": "arbeitwirtschaft",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "firma_leitung": ["uprava", "saradnja", "izvještaj", "sektor", "poslovni", "upravljanje", "poslovanje",
                      "strategija", "klijent", "sjedište", "zamjenik"],
    "abteilung_mitarbeiter": ["odjeljenje", "rukovodstvo", "menadžer", "osnivač", "saradnik", "upravljati",
                              "osnovati", "osnivati", "sarađivati", "nadzor"],
    "produktion_handel": ["proizvodnja", "industrija", "proizvođač", "nabavka", "kvalitet", "konkurencija",
                          "potrošnja", "pogon", "potrošač", "izvoz", "isporuka", "transport", "uvoz", "zalihe"],
    "liefern_beschaffen": ["dobavljač", "skladište", "sirovina", "distribucija", "nabaviti", "nabavljati",
                           "izgradnja", "održavanje", "obezbijediti", "obezbjeđivati", "zadovoljiti",
                           "zadovoljavati", "uvesti", "uvoditi"],
    "geld_preise": ["dolar", "budžet", "fond", "stopa", "kapital", "finansijski", "novčani", "finansiranje",
                    "finansirati", "inflacija", "naplata", "valuta", "jeftin", "povoljan", "poskupljenje",
                    "ušteda", "depozit", "izdvojiti", "izdvajati"],
    "wachstum_rueckgang": ["rast", "povećanje", "pad", "smanjenje", "porast", "propasti", "propadati",
                           "potražnja", "dobit", "prognoza", "propast"],
    "schulden_verluste": ["dobitak", "nadoknada", "dužnik", "bilans", "deficit", "stečaj", "zaduženje",
                          "zadužiti se", "zaduživati se", "odšteta", "recesija", "nestašica"],
    "anlegen_vermoegen": ["ekonomski", "imovina", "doprinos", "privredni", "ekonomija", "investicija",
                          "dionica", "ulaganje", "investitor", "bogatstvo"],
    "investieren_beitragen": ["uložiti", "ulagati", "siromaštvo", "privatizacija", "tender", "tržišni",
                              "berza", "investirati", "preduzetnik", "doprinijeti", "doprinositi"],
    "beruf_karriere": ["karijera", "sposobnost", "dužnost", "stručan", "zapošljavanje", "profesionalan",
                       "obuka", "vještina", "efikasan", "sekretar", "vrhunski"],
    "aufstieg_weiterbildung": ["savjetnik", "konkurs", "sposoban", "struka", "napredovati", "iskusan",
                               "usavršavanje", "asistent", "napredovanje", "steći", "sticati / stjecati"],
    "rechte_arbeit": ["radni", "godišnji", "sindikat", "pregovor", "obavezan", "minimalan", "službeni",
                      "kolektivni", "inspektor", "invaliditet", "inspekcija", "odsustvo", "kolektiv",
                      "nezaposlenost", "staž", "pregovarati", "otpuštanje", "otpremnina"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = {"Svaki uposlenik ima pravo na godišnji odmor."}

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "poslovni": ["poslovna", "poslovno"], "odjeljenje": ["odjel"], "kvalitet": ["kvaliteta"],
    "zalihe": ["zaliha"], "finansijski": ["finansijska", "finansijsko"], "novčani": ["novčana", "novčano"],
    "jeftin": ["jeftina", "jeftino"], "povoljan": ["povoljna", "povoljno"],
    "ekonomski": ["ekonomska", "ekonomsko"], "privredni": ["privredna", "privredno"],
    "tržišni": ["tržišna", "tržišno"], "stručan": ["stručna", "stručno"],
    "profesionalan": ["profesionalna", "profesionalno"], "efikasan": ["efikasna", "efikasno"],
    "vrhunski": ["vrhunska", "vrhunsko"], "sposoban": ["sposobna", "sposobno"],
    "iskusan": ["iskusna", "iskusno"], "radni": ["radna", "radno"], "godišnji": ["godišnja", "godišnje"],
    "pregovor": ["pregovori"], "obavezan": ["obavezna", "obavezno"], "minimalan": ["minimalna", "minimalno"],
    "službeni": ["službena", "službeno"], "kolektivni": ["kolektivna", "kolektivno"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "preduzetnik": ["poduzetnik"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "osnovati": "osnivati", "osnivati": "osnovati", "nabaviti": "nabavljati", "nabavljati": "nabaviti",
    "obezbijediti": "obezbjeđivati", "obezbjeđivati": "obezbijediti", "zadovoljiti": "zadovoljavati",
    "zadovoljavati": "zadovoljiti", "uvesti": "uvoditi", "uvoditi": "uvesti", "izdvojiti": "izdvajati",
    "izdvajati": "izdvojiti", "propasti": "propadati", "propadati": "propasti", "zadužiti se": "zaduživati se",
    "zaduživati se": "zadužiti se", "uložiti": "ulagati", "ulagati": "uložiti", "doprinijeti": "doprinositi",
    "doprinositi": "doprinijeti", "steći": "sticati / stjecati", "sticati / stjecati": "steći",
}


def test_zaposlenik_hat_die_zweite_form(grunddaten, index_html):
    """Kein zweites Wort: die Anzeige in der App bekommt uposlenik dazu, wie doktor / ljekar."""
    k = next(x for x in grunddaten["kategorien"] if x["id"] == "arbeitsvertrag")
    w = {x["bs"]: x for x in k["words"]}
    assert w["zaposlenik / uposlenik"]["de"] == "Arbeitnehmer"
    alle = [x["bs"] for k in grunddaten["kategorien"] for x in k["words"]]
    assert "zaposlenik" not in alle and "uposlenik" not in alle
    assert "'arbeitnehmer:zaposlenik': 'arbeitnehmer:zaposlenik / uposlenik'" in index_html
