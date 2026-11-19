# -*- coding: utf-8 -*-
"""Pruefbericht 1.4, S23 (Ajdin am 15.11.2026 abends, Fragenliste Nr. 20: "ja"):
Die Datenschutzerklaerung nennt bei der Werbung neben der Werbe-ID auch die
App-Set-ID, die Googles Werbebaustein laut Google erhebt
(developers.google.com/admob/android/privacy/play-data-disclosure, abgerufen am
15.11.2026). Wortlaut nach Release\\Datenschutz_S23_Entwurf.md, in beiden
Fassungen (mit Konto und ohne, Web-Demo) und allen acht Sprachen. Der Stand der
Erklaerung ist der 19.11.2026. Ohne Werbung (set.dsgvo_werbung_aus) kommt die
Kennung nicht vor.
"""
import re

import pytest

# Je Sprache: was vorher dastand, und der eingefuegte Halbsatz dazwischen
HALBSATZ = {
    "de": ("die Werbe-ID deines Geräts, ",
           "die App-Set-ID (eine Kennung, die nur für die Apps eines Anbieters gilt), ",
           "deine IP-Adresse,"),
    "en": ("your device's advertising ID, ",
           "the app set ID (an identifier that only applies to the apps of one developer), ",
           "your IP address,"),
    "tr": ("cihazının reklam kimliğini, ",
           "uygulama seti kimliğini (yalnızca aynı geliştiricinin uygulamalarında geçerli bir kimlik), ",
           "IP adresini,"),
    "sv": ("din enhets annons-id, ",
           "app set-id:t (en identifierare som bara gäller för appar från samma utvecklare), ",
           "din IP-adress,"),
    "nl": ("de advertentie-ID van je apparaat, ",
           "de app set-ID (een ID die alleen geldt voor de apps van één ontwikkelaar), ",
           "je IP-adres,"),
    "nb": ("enhetens annonse-ID, ",
           "app set-ID-en (en ID som bare gjelder for appene fra én utvikler), ",
           "IP-adressen din,"),
    "da": ("din enheds annoncerings-id, ",
           "app set-id'et (et id, der kun gælder for apps fra samme udvikler), ",
           "din IP-adresse,"),
    "fr": ("l'identifiant publicitaire de ton appareil, ",
           "l'identifiant App Set (un identifiant valable uniquement pour les applis d'un même développeur), ",
           "ton adresse IP,"),
}
STAND = {"de": "Stand: 19.11.2026", "en": "Last updated: November 19, 2026",
         "tr": "Son güncelleme: 19.11.2026", "sv": "Senast uppdaterad: 19.11.2026",
         "nl": "Laatst bijgewerkt: 19 november 2026", "nb": "Sist oppdatert: 19.11.2026",
         "da": "Senest opdateret: 19.11.2026", "fr": "Dernière mise à jour : 19.11.2026"}
# Der Name der Kennung je Sprache
NAME = {"de": "App-Set-ID", "en": "app set ID", "tr": "uygulama seti kimliğ", "sv": "app set-id",
        "nl": "app set-ID", "nb": "app set-ID", "da": "app set-id", "fr": "identifiant App Set"}


def _satz(text, teil):
    """Der Satz, in dem teil steht."""
    i = text.index(teil)
    return text[text.rfind(". ", 0, i) + 2:text.index(".", i + len(teil)) + 1]


@pytest.mark.parametrize("schluessel", ["set.dsgvo_werbung_an", "set.dsgvo_werbung_an_ohne_konto"])
def test_s23_app_set_id_im_werbe_absatz(sprachcodes, schluessel):
    import sprachen
    assert set(HALBSATZ) == set(sprachcodes) == set(NAME)
    for code in sprachcodes:
        text = sprachen.TEXTE[code][schluessel]
        vorher, neu, nachher = HALBSATZ[code]
        assert text.count(vorher + neu + nachher) == 1, (code, schluessel)
        assert text.lower().count(NAME[code].lower()) == 1, (code, schluessel)     # nur dort genannt
        assert "Google" in text and "AdMob" in text, (code, schluessel)


def test_s23_beide_fassungen_derselbe_satz(sprachcodes):
    """Mit und ohne Konto steht derselbe Satz da (der Absatz selbst ist ohne Konto
    kürzer, dort fehlt Firebase)."""
    import sprachen
    for code in sprachcodes:
        t, neu = sprachen.TEXTE[code], HALBSATZ[code][1]
        assert _satz(t["set.dsgvo_werbung_an"], neu) == _satz(t["set.dsgvo_werbung_an_ohne_konto"], neu), code


def test_s23_ohne_werbung_keine_kennung(sprachcodes):
    import sprachen
    for code in sprachcodes:
        for k in ("set.dsgvo_werbung_aus", "set.dsgvo_werbung_aus_ohne_konto"):
            assert NAME[code].lower() not in sprachen.TEXTE[code][k].lower(), (code, k)


@pytest.mark.parametrize("schluessel", ["set.datenschutz_text", "set.datenschutz_text_ohne_konto"])
def test_s23_stand(sprachcodes, schluessel):
    import sprachen
    assert set(STAND) == set(sprachcodes)
    for code in sprachcodes:
        stand = re.findall(r"<i>([^<]*)</i>$", sprachen.TEXTE[code][schluessel])
        # Im französischen Text ohne Konto steht vor dem Doppelpunkt ein geschütztes Leerzeichen.
        assert [s.replace(chr(160), " ") for s in stand] == [STAND[code]], (code, schluessel, stand)


def test_s23_in_der_fertigen_erklaerung(sprachcodes):
    """So, wie App und Webseite (seite_bauen.py) die Erklärung bekommen: der
    Platzhalter ist gefüllt, der Halbsatz steht genau einmal da, der Stand bleibt
    (KONTAKT_STAND ist früher und ändert ihn nicht)."""
    import sprachen
    assert sprachen.WERBUNG_LAEUFT and sprachen.KONTO_PFLICHT
    for code in sprachcodes:
        text = sprachen.texte(code)["set.datenschutz_text"]
        vorher, neu, nachher = HALBSATZ[code]
        assert "{werbung_abschnitt}" not in text, code
        assert text.count(vorher + neu + nachher) == 1, code
        assert text.endswith("<i>%s</i>" % STAND[code]), (code, text[-60:])
