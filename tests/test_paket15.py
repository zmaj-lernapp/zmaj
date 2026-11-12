# -*- coding: utf-8 -*-
"""Wortschatz-Paket 15 (07.11.2026): Sektion 25 · Haus und Wohnung, dazu vier Level Amt, Post und Bank in Sektion 24.

168 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_15.json, b2_2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- iznajmiti heisst in der App jetzt „vermieten“, mieten ist unajmiti (neu, Paar mit
  unajmljivati); die Kennung von iznajmiti zieht ueber UMBENANNT mit;
- produžni kabl wird produžni kabel (Nachfrage 6 B), ebenfalls ueber UMBENANNT; kabl
  zaehlt nicht;
- puniti, zamjenjivati, iznajmljivati und useljavati se sind die Gegenstuecke zu napuniti,
  zamijeniti, iznajmiti und useliti se aus der App, "partner" steht an beiden.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
import pytest

from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["auf_dem_amt", "post_abmeldung", "bank_darlehen", "versicherung_zinsen", "dinge_haushalt",
         "buerste_kamm", "raeume_moebel", "sauber_kaputt", "rohre_strom", "bauen_einbauen", "streichen_kleben",
         "wohnen_miete"]
SEKTION = {
    "auf_dem_amt": "rechtbehoerden", "post_abmeldung": "rechtbehoerden", "bank_darlehen": "rechtbehoerden",
    "versicherung_zinsen": "rechtbehoerden", "dinge_haushalt": "hauswohnung", "buerste_kamm": "hauswohnung",
    "raeume_moebel": "hauswohnung", "sauber_kaputt": "hauswohnung", "rohre_strom": "hauswohnung",
    "bauen_einbauen": "hauswohnung", "streichen_kleben": "hauswohnung", "wohnen_miete": "hauswohnung",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "auf_dem_amt": ["prijava", "boravak", "popis", "spisak", "isprava", "viza", "molba", "istek", "zapisnik",
                    "podnosilac", "ovjeriti", "ovjeravati", "pošiljka"],
    "post_abmeldung": ["priložiti", "prilagati", "koverta", "šalter", "razglednica",
                       "porezna uprava / poreska uprava", "punomoć", "primalac", "odjaviti", "odjavljivati",
                       "pošiljalac", "zavod za zapošljavanje / biro", "odjava"],
    "bank_darlehen": ["isplatiti", "isplaćivati", "transakcija", "nezgoda", "premija", "zajam", "osiguranik",
                      "otplata", "pozajmica", "bankar", "provizija", "sef"],
    "versicherung_zinsen": ["bankrot", "devize", "doznaka", "kamatna stopa", "otplatiti", "otplaćivati",
                            "uplatnica", "blagajnik", "žirant", "životno osiguranje", "osiguravajuće društvo",
                            "polisa osiguranja"],
    "dinge_haushalt": ["ploča", "lanac", "teret", "kutija", "staklo", "metal", "posuda", "krema", "konac",
                       "dim", "svijeća", "nakit"],
    "buerste_kamm": ["poklopac", "pribor", "dugme", "igla", "krpa", "šminka", "parfem", "četka", "šampon",
                     "lopata", "šibica", "češalj"],
    "raeume_moebel": ["prostorija", "prag", "hodnik", "kapija", "pločica", "garaža", "fotelja", "dimnjak",
                      "trpezarija", "stepenište", "plafon", "radijator", "madrac / dušek", "ostava", "kvaka",
                      "sudoper", "kada"],
    "sauber_kaputt": ["čišćenje", "oštećenje", "cijev", "rupa", "prašina", "žica", "kvar", "vodovod", "vlaga",
                      "higijena", "mrlja", "čistoća"],
    "rohre_strom": ["kanalizacija", "prekidač", "pukotina", "puknuti", "curiti", "procuriti", "začepiti",
                    "smrad", "brojilo", "odvod", "plijesan", "kabel"],
    "bauen_einbauen": ["gradnja", "zamjena", "sastaviti", "sastavljati", "ugraditi", "ugrađivati", "beton",
                       "puniti", "ohladiti", "hladiti", "zagrijati", "grijati", "daska", "namjestiti",
                       "namještati", "zaključati", "zaključavati"],
    "streichen_kleben": ["isprati", "ispirati", "obojiti / ofarbati", "bojiti / farbati", "renovirati",
                         "zamjenjivati", "isprazniti", "prazniti", "zalijepiti", "lijepiti", "cement", "cigla",
                         "otključati", "otključavati", "šiti", "sašiti", "pomesti", "mesti"],
    "wohnen_miete": ["stambeni", "imanje", "parcela", "stanar", "fasada", "stanovanje", "produženje",
                     "raskinuti", "raskidati", "iseliti se", "iseljavati se", "vikendica", "iznajmljivati",
                     "neboder", "centralno grijanje", "useljavati se", "unajmiti", "unajmljivati"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = set()

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "polisa osiguranja": ["polica osiguranja"], "šibica": ["šibice"], "pločica": ["pločice"],
    "plijesan": ["buđ"], "stambeni": ["stambena", "stambeno"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "podnosilac": ["podnositelj"], "koverta": ["kuverta"], "primalac": ["primatelj", "primatelji"],
    "pošiljalac": ["pošiljatelj"], "kabel": ["kabl"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "ovjeriti": "ovjeravati", "ovjeravati": "ovjeriti", "priložiti": "prilagati", "prilagati": "priložiti",
    "odjaviti": "odjavljivati", "odjavljivati": "odjaviti", "isplatiti": "isplaćivati",
    "isplaćivati": "isplatiti", "otplatiti": "otplaćivati", "otplaćivati": "otplatiti", "curiti": "procuriti",
    "procuriti": "curiti", "sastaviti": "sastavljati", "sastavljati": "sastaviti", "ugraditi": "ugrađivati",
    "ugrađivati": "ugraditi", "puniti": "napuniti", "ohladiti": "hladiti", "hladiti": "ohladiti",
    "zagrijati": "grijati", "grijati": "zagrijati", "namjestiti": "namještati", "namještati": "namjestiti",
    "zaključati": "zaključavati", "zaključavati": "zaključati", "isprati": "ispirati", "ispirati": "isprati",
    "obojiti / ofarbati": "bojiti / farbati", "bojiti / farbati": "obojiti / ofarbati",
    "zamjenjivati": "zamijeniti", "isprazniti": "prazniti", "prazniti": "isprazniti", "zalijepiti": "lijepiti",
    "lijepiti": "zalijepiti", "otključati": "otključavati", "otključavati": "otključati", "šiti": "sašiti",
    "sašiti": "šiti", "pomesti": "mesti", "mesti": "pomesti", "raskinuti": "raskidati",
    "raskidati": "raskinuti", "iseliti se": "iseljavati se", "iseljavati se": "iseliti se",
    "iznajmljivati": "iznajmiti", "useljavati se": "useliti se", "unajmiti": "unajmljivati",
    "unajmljivati": "unajmiti",
}


def test_iznajmiti_heisst_vermieten(grunddaten, index_html):
    """Ajdin, 07.11.2026 (Paket 15 Nr. 113, Alternative): iznajmiti und iznajmljivati heissen
    vermieten, unajmiti und unajmljivati mieten. Der Lernstand von iznajmiti zieht mit."""
    w = {x["bs"]: x for k in grunddaten["kategorien"] for x in k["words"]}
    assert w["iznajmiti"]["de"] == "vermieten" and w["iznajmiti"]["partner"] == "iznajmljivati"
    assert w["iznajmljivati"]["de"] == "vermieten"
    assert w["unajmiti"]["de"] == w["unajmljivati"]["de"] == "mieten"
    assert "'mieten:iznajmiti': 'vermieten:iznajmiti'" in index_html


def test_produzni_kabel(grunddaten, index_html):
    k = next(x for x in grunddaten["kategorien"] if x["id"] == "auto_werkstatt")
    assert "produžni kabel" in [w["bs"] for w in k["words"]]
    alle = [x["bs"] for k in grunddaten["kategorien"] for x in k["words"]]
    assert "produžni kabl" not in alle and "kabl" not in alle
    assert "'verlängerungskabel:produžni kabl': 'verlängerungskabel:produžni kabel'" in index_html


@pytest.mark.parametrize("alt, neu", [("napuniti", "puniti"), ("zamijeniti", "zamjenjivati"),
                                      ("iznajmiti", "iznajmljivati"), ("useliti se", "useljavati se")])
def test_alte_verben_haben_ihr_gegenstueck(grunddaten, alt, neu):
    w = {x["bs"]: x for k in grunddaten["kategorien"] for x in k["words"]}
    assert w[alt]["partner"] == neu and w[neu]["partner"] == alt


def test_amt_und_bank_in_recht_und_behoerden(grunddaten):
    sek = {k["id"]: k["sektion"] for k in grunddaten["kategorien"]}
    for i in ("auf_dem_amt", "post_abmeldung", "bank_darlehen", "versicherung_zinsen"):
        assert sek[i] == "rechtbehoerden", i
