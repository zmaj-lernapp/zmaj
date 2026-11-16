# -*- coding: utf-8 -*-
"""Pruefbericht 1.3, S30 (Ajdin am 14.11.2026: "ja mach"): Punkt 2 der
Nutzungsbedingungen nennt neben Unterricht, menschlicher Uebersetzung und
Rechtsberatung auch die aerztliche Aufklaerung, und bei den heiklen Leveln
steht Gesundheit dabei - in allen acht Sprachen, mit und ohne Konto. Der
versteckte Zahnarzt-Teil wird dabei nicht verraten. Das Stand-Datum beider
Fassungen ist der 14.11.2026; einen Hinweis beim Oeffnen gibt es nicht, es
ist eine Klarstellung (AGB_WESENTLICH bleibt)."""
import re

import pytest

# Je Sprache: was in Punkt 2 stehen muss
PUNKT2 = {
    "de": ("keine Rechtsberatung und keine ärztliche Aufklärung.",
           "Amt, Bank, Immobilien, Arbeitsvertrag und Gesundheit:"),
    "en": ("legal advice or medical advice.",
           "public offices, banking, property, employment contracts and health:"),
    "tr": ("hukuki ya da tıbbi danışmanlığın yerini tutmaz.",
           "resmi daireler, banka, gayrimenkul, iş sözleşmesi ve sağlık seviyeleri"),
    "sv": ("juridisk eller medicinsk rådgivning.",
           "myndigheter, bank, bostad, anställningsavtal och hälsa:"),
    "nl": ("geen juridisch advies en geen medisch advies.",
           "overheid, bank, vastgoed, arbeidsovereenkomst en gezondheid:"),
    "nb": ("juridisk eller medisinsk rådgivning.",
           "offentlige kontorer, bank, bolig, arbeidsavtale og helse:"),
    "da": ("juridisk eller lægelig rådgivning.",
           "myndigheder, bank, bolig, ansættelseskontrakt og sundhed:"),
    "fr": ("ni un conseil juridique, ni un avis médical.",
           "l'immobilier, le contrat de travail et la santé" + chr(160) + ":"),
}
STAND = {"de": "Stand: 14.11.2026", "en": "Last updated: November 14, 2026"}


@pytest.mark.parametrize("schluessel", ["set.agb_text", "set.agb_text_ohne_konto"])
def test_s30_aerztliche_aufklaerung_und_gesundheit(sprachcodes, schluessel):
    import sprachen
    assert set(PUNKT2) == set(sprachcodes)
    for code in sprachcodes:
        text = sprachen.TEXTE[code][schluessel]
        punkt2 = text.split("<b>2.")[1].split("<b>3.")[0]
        for teil in PUNKT2[code]:
            assert teil in punkt2, (code, schluessel, teil)
        # Der versteckte Teil bleibt versteckt
        assert not re.search(r"zahn|tooth|dental|diş hekim|tandarts|tandlæge|tandlege|tandläkare|dentiste",
                             punkt2, re.I), (code, punkt2)
        stand = re.findall(r"<i>([^<]*)</i>$", text)
        assert len(stand) == 1 and stand[0].endswith(("14.11.2026", "November 14, 2026")), (code, stand)
        if code in STAND:
            assert stand[0] == STAND[code], (code, stand)


def test_s30_klarstellung_ohne_hinweis(index_html):
    """Keine neue Pflicht, kein Preis, kein Recht: AGB_WESENTLICH bleibt,
    beim Oeffnen kommt kein Hinweis "Bedingungen geaendert"."""
    assert "const AGB_WESENTLICH = CLOUD_AN ? '2026-10-28' : '2026-09-19';" in index_html
