# -*- coding: utf-8 -*-
"""Wortschatz-Paket 14 (07.11.2026): Sektion 23 · Gesellschaft und Politik, Sektion 24 · Recht und Behörden.

159 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_14.json, b2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- poslanik (Staatsebene) und zastupnik (Föderation BiH), raj und džennet, pakao und
  džehennem sind je zwei Woerter (Ajdin);
- svećenik / sveštenik ist ein Wort, rješenje / upravni akt ein eigenes neben rješenje
  (Lösung), NIE_NEBENEINANDER haelt die beiden aus derselben Auswahl.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
import pytest

from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["staat_institutionen", "wahlen_parlament", "krieg_frieden", "buerger_rechte", "religion_gemeinschaft",
         "gericht", "polizei_anzeige", "aemter_zustaendigkeit", "bescheid_einspruch", "vertraege"]
SEKTION = {
    "staat_institutionen": "gesellschaftpolitik", "wahlen_parlament": "gesellschaftpolitik",
    "krieg_frieden": "gesellschaftpolitik", "buerger_rechte": "gesellschaftpolitik",
    "religion_gemeinschaft": "gesellschaftpolitik", "gericht": "rechtbehoerden",
    "polizei_anzeige": "rechtbehoerden", "aemter_zustaendigkeit": "rechtbehoerden",
    "bescheid_einspruch": "rechtbehoerden", "vertraege": "rechtbehoerden",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "staat_institutionen": ["politički", "republika", "međunarodni", "ministarstvo", "državni", "institucija",
                            "vijeće", "federacija", "skupština", "nacionalni", "premijer", "sjednica", "odbor",
                            "komisija"],
    "wahlen_parlament": ["sporazum", "izborni", "kandidat", "poslanik", "parlament", "reforma", "usvojiti",
                         "usvajati", "koalicija", "opozicija", "glasati", "birač", "formirati", "zastupnik"],
    "krieg_frieden": ["vojni", "ratni", "borac", "poraz", "prijetnja", "sankcija", "general", "oružani",
                      "logor", "civil", "osloboditi", "oslobađati", "bitka", "mirovni", "oslobođenje",
                      "primirje"],
    "buerger_rechte": ["predstavnik", "društveni", "udruženje", "interes", "socijalni", "stanovništvo",
                       "inicijativa", "identitet", "korupcija", "humanitarni", "građanski", "migrant", "vođa",
                       "manjina", "diskriminacija", "nepravda", "ravnopravnost"],
    "religion_gemeinschaft": ["vjerski", "muslimanski", "katolički", "religija", "pravoslavni", "grijeh",
                              "džemat", "svećenik / sveštenik", "vakuf", "medresa", "milost", "raj", "hodža",
                              "pakao", "duh", "džennet", "džehennem"],
    "gericht": ["pravni", "tužilaštvo", "krivični", "istraga", "sudski", "zakonski", "optužnica", "svjedočiti",
                "suđenje", "optužba", "pravosuđe", "pritvor", "tužilac", "kršenje", "suditi", "osuditi",
                "osuđivati", "optužiti", "optuživati"],
    "polizei_anzeige": ["policijski", "podnijeti", "podnositi", "droga", "prijetiti", "zaprijetiti", "potraga",
                        "saobraćajni", "kriminal", "počiniti", "incident", "osumnjičeni", "krađa", "hapšenje",
                        "prekršaj", "uhapsiti", "hapsiti", "pljačka", "krivična prijava"],
    "aemter_zustaendigkeit": ["agencija", "služba", "ustanova", "nadležan", "uputiti", "upućivati", "zavod",
                              "odredba", "izdati", "izdavati", "dokumentacija", "nadležnost"],
    "bescheid_einspruch": ["saglasnost", "naredba", "upozorenje", "odobriti", "odobravati", "odobrenje",
                           "rješenje / upravni akt", "prigovor", "organ", "provesti", "provoditi",
                           "uspostaviti", "uspostavljati"],
    "vertraege": ["izmjena", "dopuna", "važiti", "potpisivanje", "ukinuti", "ukidati", "produžiti",
                  "produžavati", "posjed", "obnoviti", "obnavljati", "nasljednik", "važeći", "sklopiti",
                  "sklapati", "zakup", "raskid", "posjedovati"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = set()

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "politički": ["politička", "političko"], "međunarodni": ["međunarodna", "međunarodno"],
    "državni": ["državna", "državno"], "nacionalni": ["nacionalna", "nacionalno"],
    "izborni": ["izborna", "izborno"], "vojni": ["vojna", "vojno"], "ratni": ["ratna", "ratno"],
    "oružani": ["oružana", "oružano"], "mirovni": ["mirovna", "mirovno"],
    "društveni": ["društvena", "društveno"], "socijalni": ["socijalna", "socijalno"],
    "humanitarni": ["humanitarna", "humanitarno"], "građanski": ["građanska", "građansko"],
    "vjerski": ["vjerska", "vjersko"], "muslimanski": ["muslimanska", "muslimansko"],
    "katolički": ["katolička", "katoličko"], "pravoslavni": ["pravoslavna", "pravoslavno"],
    "pravni": ["pravna", "pravno"], "tužilaštvo": ["tužiteljstvo"], "krivični": ["krivična", "krivično"],
    "sudski": ["sudska", "sudsko"], "zakonski": ["zakonska", "zakonsko"], "tužilac": ["tužitelj"],
    "policijski": ["policijska", "policijsko"], "saobraćajni": ["saobraćajna", "saobraćajno"],
    "nadležan": ["nadležna", "nadležno"], "važeći": ["važeća", "važeće"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "oružani": ["oružan"], "humanitarni": ["humanitaran"], "vođa": ["lider"], "pravoslavni": ["pravoslavan"],
    "nadležan": ["nadležni"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "usvojiti": "usvajati", "usvajati": "usvojiti", "osloboditi": "oslobađati", "oslobađati": "osloboditi",
    "osuditi": "osuđivati", "osuđivati": "osuditi", "optužiti": "optuživati", "optuživati": "optužiti",
    "podnijeti": "podnositi", "podnositi": "podnijeti", "prijetiti": "zaprijetiti", "zaprijetiti": "prijetiti",
    "uhapsiti": "hapsiti", "hapsiti": "uhapsiti", "uputiti": "upućivati", "upućivati": "uputiti",
    "izdati": "izdavati", "izdavati": "izdati", "odobriti": "odobravati", "odobravati": "odobriti",
    "provesti": "provoditi", "provoditi": "provesti", "uspostaviti": "uspostavljati",
    "uspostavljati": "uspostaviti", "ukinuti": "ukidati", "ukidati": "ukinuti", "produžiti": "produžavati",
    "produžavati": "produžiti", "obnoviti": "obnavljati", "obnavljati": "obnoviti", "sklopiti": "sklapati",
    "sklapati": "sklopiti",
}


@pytest.mark.parametrize("a, b", [("poslanik", "zastupnik"), ("raj", "džennet"), ("pakao", "džehennem")])
def test_zwei_woerter_mit_eigener_bedeutung(grunddaten, a, b):
    w = {x["bs"]: x["de"] for k in grunddaten["kategorien"] for x in k["words"]}
    assert w[a] != w[b] and w[a].split(" (")[0] == w[b].split(" (")[0], (w[a], w[b])


def test_rjesenje_bleibt_daneben(grunddaten, index_html):
    w = {x["bs"]: x["de"] for k in grunddaten["kategorien"] for x in k["words"]}
    assert w["rješenje"] == "Lösung" and w["rješenje / upravni akt"] == "Bescheid (Verwaltungsakt)"
    assert "['rješenje / upravni akt', 'rješenje']" in index_html
    assert "sveštenik" not in w and "svećenik / sveštenik" in w
