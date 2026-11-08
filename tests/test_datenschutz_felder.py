# -*- coding: utf-8 -*-
"""Die Datenschutzerklärung gegen das, was die App wirklich ablegt.

Prüfbericht 1.3, G14: Die Erklärung sagte „Mehr als ein Ja oder Nein steht dort
nicht“, ZmajAbo.java legt aber Kaufkennung, Plan und das Ende der Gratiswoche
ab (planMerken). Und die Aufzählung des Lernstands ließ Felder aus, die in der
Cloud liegen. Wer standAlsObjekt() ein Feld gibt, landet hier und muss die
Erklärung mitziehen.
"""
import re

import pytest

SPRACHEN = ("de", "en", "tr", "sv", "nl", "nb", "da", "fr")

# Jedes Feld aus standAlsObjekt() und womit die deutsche Erklärung es nennt.
FELDER = {
    "gewusst": "gelernte Wörter",
    "bestanden": "bestandene Level",
    "gelesen": "gelesene Geschichten",
    "tage": "Lerntage",
    "frost": "Serienschutz",
    "besitz": "gekaufte Gegenstände",
    "leben": "Leben",
    "schutz": "Serienschutz",
    "tagwerk": "Zähler für die Tagesaufgaben",
    "muenzen_ges": "Münzen",
    "muenzen_aus": "Münzen",
    "getragen": "was Zmaj trägt",
    "gefeiert": "gefeierte Wegmarken",
    "rekord": "längste Serie",
    "wann": "wann du etwas geschafft hast",
    "geschenk_jahr": "Jahr des letzten Geschenks",
    "einstufung": "Einstufung",
    "topf": "Aufgaben zum Wiederholen",
    "bewertung": "Bewertungsfrage",
    "stern": "markierte Wörter und Sätze",
    "zahnarzt": "freigeschaltete Zusatzteile",
    "kartei": "Aufgaben zum Wiederholen",
}

# Dieselben neu genannten Felder in den anderen Sprachen.
NEUE_FELDER = {
    "de": ("markierte", "längste Serie", "Wegmarken", "trägt", "Zusatzteile", "Geschenks", "Bewertungsfrage"),
    "en": ("marked", "longest streak", "milestones", "wearing", "extra sections", "last gift", "rating question"),
    "tr": ("işaretlediğin", "en uzun serin", "dönüm noktaları", "üzerindekiler", "ek bölümler", "son hediyenin",
           "değerlendirme sorusuna"),
    "sv": ("markerat", "längsta serie", "milstolpar", "har på sig", "extradelar", "senaste gåva", "betyg"),
    "nl": ("gemarkeerd", "langste reeks", "mijlpalen", "draagt", "extra delen", "laatste cadeau",
           "beoordelingsvraag"),
    "nb": ("merket", "lengste rekken", "milepæler", "har på seg", "ekstradeler", "siste gaven",
           "vurderingsspørsmålet"),
    "da": ("markeret", "længste række", "milepæle", "har på", "ekstradele", "seneste gave", "bedømmelse"),
    "fr": ("marqués", "plus longue série", "étapes", "porte Zmaj", "parties supplémentaires", "dernier cadeau",
           "demande d'évaluation"),
}

# Was im Abo-Absatz stehen muss: Kaufkennung, Plan, Ende der Gratiswoche.
ABO_ANGABEN = {
    "de": ("Kaufkennung", "gewählten Plan", "Gratiswoche"),
    "en": ("purchase identifier", "plan you chose", "free week"),
    "tr": ("satın alma kimliğini", "seçtiğin planı", "ücretsiz haftanın"),
    "sv": ("köpidentifierare", "planen du valde", "gratisveckan"),
    "nl": ("aankoopcode", "gekozen abonnement", "gratis week"),
    "nb": ("kjøps-ID", "planen du valgte", "gratisuken"),
    "da": ("købs-id", "plan, du valgte", "gratisugen"),
    "fr": ("identifiant d'achat", "formule choisie", "semaine gratuite"),
}

# Die Sätze, die nicht mehr stimmten.
FALSCH = {
    "de": ("Mehr als ein Ja oder Nein", "merkt sie sich nur"),
    "en": ("Nothing more than a yes or a no", "only remembers whether"),
    "tr": ("evet ya da hayırdan fazlası", "yalnızca etkin olup olmadığını"),
    "sv": ("Mer än ett ja eller nej", "kommer appen bara ihåg"),
    "nl": ("Meer dan een ja of nee", "onthoudt hij alleen"),
    "nb": ("Mer enn et ja eller nei", "husker den bare"),
    "da": ("ikke mere end et ja eller nej", "husker den kun"),
    "fr": ("rien de plus qu'un oui ou un non", "retient seulement"),
}


def _felder_aus_der_app(index_html):
    block = re.search(r"function standAlsObjekt\(\)\{\s*const s = \{(.*?)\};", index_html, re.S).group(1)
    return set(re.findall(r"(?:^|[{,\s])([a-z_]+)\s*:", re.sub(r"/\*.*?\*/", "", block, flags=re.S)))


def test_jedes_feld_des_lernstands_steht_in_der_erklaerung(index_html):
    """Gilt für beide Fassungen: Die Web-Demo legt denselben Stand ab."""
    import sprachen
    assert _felder_aus_der_app(index_html) == set(FELDER)
    t = sprachen.TEXTE["de"]
    for schluessel in ("set.datenschutz_text", "set.datenschutz_text_ohne_konto"):
        aufzaehlung = next(a for a in t[schluessel].split("<br>") if a.startswith("<b>Dein Lernfortschritt"))
        for feld, wort in FELDER.items():
            assert wort in aufzaehlung, (schluessel, feld)


@pytest.mark.parametrize("code", SPRACHEN)
def test_neue_felder_in_jeder_sprache(code):
    import sprachen
    t = sprachen.TEXTE[code]
    for schluessel in ("set.datenschutz_text", "set.datenschutz_text_ohne_konto"):
        for wort in NEUE_FELDER[code]:
            assert wort in t[schluessel], (code, schluessel, wort)


@pytest.mark.parametrize("code", SPRACHEN)
def test_abo_angaben_stehen_da_und_der_alte_satz_nicht(code):
    import sprachen
    t = sprachen.texte(code)
    for wort in ABO_ANGABEN[code]:
        assert wort in t["set.datenschutz_text"], (code, wort)
    roh = sprachen.TEXTE[code]
    for falsch in FALSCH[code]:
        for schluessel in ("set.datenschutz_text", "set.datenschutz_text_ohne_konto", "set.dsgvo_abo"):
            assert falsch not in roh[schluessel], (code, schluessel, falsch)


@pytest.mark.parametrize("code", SPRACHEN)
def test_verweis_auf_den_abschnitt_mit_dem_abo(code):
    """Abschnitt 2 verweist auf den Abschnitt, in dem der Abo-Absatz steht. In
    der iOS-Fassung tauscht IOS_RECHT nur diesen Absatz: Was Android zusätzlich
    ablegt, gehört deshalb dorthin und nicht in Abschnitt 2."""
    import sprachen
    roh = sprachen.TEXTE[code]
    for schluessel, nummer in (("set.datenschutz_text", 7), ("set.datenschutz_text_ohne_konto", 6)):
        zweiter = re.split(r"(?=<b>\d+\. )", roh[schluessel])[2]
        absaetze = zweiter.split("<br>")
        android = next(i for i, a in enumerate(absaetze) if a.startswith("<b>") and "Android" in a[:40])
        assert re.search(r"\b%d\b" % nummer, absaetze[android - 1]), (code, schluessel, absaetze[android - 1])
        for wort in ABO_ANGABEN[code]:
            assert wort not in zweiter, (code, schluessel, wort)


@pytest.mark.parametrize("code", SPRACHEN)
def test_stand_der_erklaerung_ist_neu(code):
    """stand_setzen() ändert nur, wenn das genannte Datum später ist als das im
    Text. Ändert es bei einem Tag vor der Änderung nichts, ist der Text neuer."""
    import sprachen
    roh = sprachen.TEXTE[code]
    for schluessel in ("set.datenschutz_text", "set.datenschutz_text_ohne_konto"):
        assert sprachen.stand_setzen(roh[schluessel], "05.11.2026") == roh[schluessel], (code, schluessel)
