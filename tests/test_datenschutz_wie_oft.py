# -*- coding: utf-8 -*-
"""Datenschutzerklärung, Abschnitt 3, „Wie oft“ (Offen-Liste 8, Ajdin am
17.11.2026: „ok passt“ auf den deutschen Wortlaut).

Seit 277f140/d65d320 sieht die App bei jedem Öffnen nach (gedrosselt, nur die
Revisionskennung), lädt den Stand nur nach einer Änderung von einem anderen
Gerät und schreibt höchstens zweimal am Tag (nach dem Lernen und beim
Verlassen), dazu beim An- und Abmelden. Der alte Satz („liest … höchstens
einmal am Tag beim Start und schreibt … höchstens einmal am Tag“) stimmte damit
nicht mehr. Den Satz gibt es nur in der Fassung mit Konto; die Web-Demo
(set.datenschutz_text_ohne_konto) hat keine Cloud und keinen Abschnitt dazu.
Der Stand der Erklärung bleibt, er wird vor dem Upload auf den
Veröffentlichungstag gesetzt.
"""
import os

import pytest

UEBERSCHRIFT = {
    "de": "<b>Wie oft:</b> ", "en": "<b>How often:</b> ", "tr": "<b>Ne sıklıkla:</b> ",
    "sv": "<b>Hur ofta:</b> ", "nl": "<b>Hoe vaak:</b> ", "nb": "<b>Hvor ofte:</b> ",
    "da": "<b>Hvor tit:</b> ", "fr": "<b>À quelle fréquence :</b> ",
}

NEU = {
    "de": "Die App sieht beim Öffnen kurz nach, ob in deinem Konto ein neuerer Stand liegt, etwa von einem "
          "anderen Gerät, und lädt ihn nur dann. Sie schreibt deinen Stand höchstens zweimal am Tag, nach dem "
          "Lernen und wenn du sie verlässt, dazu einmal beim Anmelden und einmal beim Abmelden.",
    "en": "When you open the app, it briefly checks whether there is more recent progress in your account, for "
          "example from another device, and loads it only then. It writes your progress at most twice a day, "
          "after learning and when you leave the app, plus once when you sign in and once when you sign out.",
    "tr": "Uygulama açılışta, hesabında, örneğin başka bir cihazdan gelmiş, daha yeni bir durum olup olmadığına "
          "kısaca bakar ve yalnızca varsa indirir. Durumu hesabına günde en fazla iki kez yazar: "
          "sen çalıştıktan sonra ve uygulamadan çıktığında; buna girişte ve çıkışta birer kez eklenir.",
    "sv": "När du öppnar appen kontrollerar den snabbt om det finns ett nyare läge i ditt konto, till exempel "
          "från en annan enhet, och hämtar det bara i så fall. Den skriver läget högst två gånger om dagen, "
          "efter att du har övat och när du lämnar den, plus en gång när du loggar in och en gång när du "
          "loggar ut.",
    "nl": "Bij het openen kijkt de app even of er in je account een nieuwere stand staat, bijvoorbeeld van een "
          "ander apparaat, en haalt die alleen dan op. Je stand wordt hoogstens twee keer per dag geschreven, "
          "na het leren en als je de app verlaat, plus één keer bij het inloggen en één keer bij het "
          "uitloggen.",
    "nb": "Når du åpner appen, sjekker den raskt om det ligger nyere framgang i kontoen din, for eksempel fra "
          "en annen enhet, og henter den bare i så fall. Den skriver framgangen din høyst to ganger om dagen, "
          "etter at du har øvd og når du forlater appen, i tillegg én gang når du logger inn og én gang når du "
          "logger ut.",
    "da": "Når du åbner appen, tjekker den kort, om der ligger nyere fremgang på din konto, for eksempel fra "
          "en anden enhed, og henter den kun i så fald. Den skriver din fremgang højst to gange om dagen, "
          "efter at du har øvet dig og når du forlader appen, plus én gang når du logger ind og én gang når du "
          "logger ud.",
    "fr": "À l'ouverture, l'application vérifie brièvement si ton compte contient une progression plus "
          "récente, par exemple provenant d'un autre appareil, et ne la récupère que dans ce cas. Elle écrit "
          "ta progression au plus deux fois par jour, après une séance d'apprentissage et quand tu quittes "
          "l'application, plus une fois à la connexion et une fois à la déconnexion.",
}

# Je Sprache ein Stück des alten Satzes, das im neuen nicht vorkommt.
ALT = {
    "de": ("höchstens einmal am Tag beim Start", "liest den Stand in deinem Konto"),
    "en": ("at most once a day when it starts", "reads the progress in your account"),
    "tr": ("günde en fazla bir kez okur", "günde en fazla bir kez yazar"),
    "sv": ("högst en gång om dagen vid start", "läser läget i ditt konto"),
    "nl": ("hoogstens één keer per dag bij het starten", "leest de stand in je account"),
    "nb": ("høyst én gang om dagen ved oppstart", "leser framgangen i kontoen din"),
    "da": ("højst én gang om dagen ved start", "læser din fremgang på kontoen"),
    "fr": ("au plus une fois par jour au démarrage", "lit l'état de ton compte"),
}


def test_alle_sprachen_abgedeckt(sprachcodes):
    assert set(sprachcodes) == set(NEU) == set(ALT) == set(UEBERSCHRIFT)


@pytest.mark.parametrize("code", sorted(NEU))
def test_neuer_satz_unter_wie_oft(code):
    """Der neue Satz steht genau einmal da, gleich hinter der Überschrift und
    vor dem nächsten Absatz, im Text, wie App und Webseite ihn bekommen."""
    import sprachen
    for text in (sprachen.TEXTE[code]["set.datenschutz_text"], sprachen.texte(code)["set.datenschutz_text"]):
        assert text.count(NEU[code]) == 1, code
        assert text.count(UEBERSCHRIFT[code] + NEU[code] + "<br><b>") == 1, code


@pytest.mark.parametrize("code", sorted(NEU))
def test_alter_satz_nirgends_mehr(code):
    """Weder in einem Text der Sprache noch in der Fassung ohne Konto."""
    import sprachen
    for schluessel, text in sprachen.TEXTE[code].items():
        if not isinstance(text, str):
            continue
        for alt in ALT[code]:
            assert alt not in text, (code, schluessel, alt)
        if schluessel != "set.datenschutz_text":
            assert NEU[code] not in text, (code, schluessel)


def test_alter_satz_auch_nicht_in_der_quelle_und_den_hinweisen(wurzel):
    """Auch nicht in einem Kommentar von sprachen.py, im README (englisch) und in
    FIREBASE_EINRICHTEN.md."""
    import io
    quelle = io.open(os.path.join(wurzel, "sprachen.py"), encoding="utf-8").read()
    for code, teile in ALT.items():
        for alt in teile:
            assert alt not in quelle, (code, alt)
    readme = io.open(os.path.join(wurzel, "README.md"), encoding="utf-8").read()
    assert "at most once a day" not in readme
    anleitung = io.open(os.path.join(wurzel, "FIREBASE_EINRICHTEN.md"), encoding="utf-8").read()
    assert "höchstens einmal am Tag je Nutzer" not in anleitung
    assert "höchstens 1× schreiben am Tag" not in anleitung
    # §9 Testen, Schritt 4 (Prüferbefund 17.11.2026): sonst hält, wer danach
    # testet, die zwei Schreibvorgänge am Tag für einen Fehler.
    assert "höchstens einen Schreibvorgang je Nutzer und Tag" not in anleitung
    assert "höchstens zwei Schreibvorgänge je Gerät und Tag gibt" in anleitung


def test_bezuege_eindeutig():
    """Prüferbefunde vom 17.11.2026: Im Türkischen bezog man „çalıştıktan
    sonra“ ohne Subjekt auf die App („nachdem sie gelaufen ist“), im
    Französischen konnte „la quittes“ auch „ta progression“ meinen, im
    Englischen, Norwegischen und Dänischen „it“/„den“ ebenso den Stand."""
    assert "yazar: sen çalıştıktan sonra" in NEU["tr"]
    assert "quand tu quittes l'application" in NEU["fr"]
    assert "when you leave the app" in NEU["en"]
    assert "når du forlater appen" in NEU["nb"]
    assert "når du forlader appen" in NEU["da"]
    for code, stueck in (("fr", "tu la quittes"), ("en", "leave it,"), ("nb", "forlater den,"),
                         ("da", "forlader den,")):
        assert stueck not in NEU[code], code
