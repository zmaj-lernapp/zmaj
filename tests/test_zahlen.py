# -*- coding: utf-8 -*-
"""Zahlen, die wechseln (25.10.2026).

Ajdin: „die sätze immer mit der gleichen zahl ist und nicht mal variiert“.
Gemeint ist die Zahl im Satz. Ein Satz mit "zahl" (vokabeln.py) kommt in
der App je Aufgabe mit einer der Zahlen aus "werte"; bosnisch als Wort, in
der Bedeutung als Ziffer („Jetzt ist es 7 Uhr.“). Welche Sätze und welche
Zahlen, hat Ajdin in einer Tabelle freigegeben („Ja, alle so“) - die steht
hier noch einmal, damit nichts dazukommt und nichts wegfällt.

Dazu „Dva plus dva je četiri.“ -> „su“ (Ajdin: „Auf „su“ ändern“).
Das Verhalten in der App prüft tests_e2e/test_zahlen.py.
"""
import collections
import io
import json
import os

import pytest

# (art, Level, Lückentext bzw. Satz) -> (Zahlwort heute, Zahlen, weiblich, frei)
# Ajdins Tabelle vom 25.10.2026, Zeile für Zeile.
TABELLE = {
    ("S", "zeit", "Sada je ___ sati."): ("pet", [5, 6, 7, 8, 9, 10, 11, 12], False, None),
    ("K", "zeit", "Sada je pet sati."): ("pet", [5, 6, 7, 8, 9, 10, 11, 12], False, None),
    ("S", "essen", "___ kahve, molim."): ("dvije", [2, 3, 4], True, None),
    ("K", "essen", "Dvije kahve, molim."): ("dvije", [2, 3, 4], True, None),
    ("S", "einkaufen", "Jakna košta ___ maraka."): ("pedeset", [30, 40, 50, 60, 70, 80, 90, 100], False, None),
    ("S", "saetze", "Imam ___ brata."): ("dva", [2, 3, 4], False, None),
    ("S", "mengen", "Imam dva ___."): ("dva", [2, 3, 4], False, None),
    ("K", "verben", "Imam dva brata."): ("dva", [2, 3, 4], False, None),
    ("S", "konjugation", "Ti ___ dva brata."): ("dva", [2, 3, 4], False, None),
    ("K", "fragen", "Ti imaš dva brata."): ("dva", [2, 3, 4], False, None),
    ("S", "saetze", "Jedemo u ___ sati."): ("sedam", [6, 7, 8, 9, 12], False, None),
    ("K", "verben", "Jedemo u sedam sati."): ("sedam", [6, 7, 8, 9, 12], False, None),
    ("S", "amt", "Imam ___ u ponedjeljak u deset sati."): ("deset", [8, 9, 10, 11, 12], False, None),
    ("K", "amt", "Imam termin u ponedjeljak u deset sati."): ("deset", [8, 9, 10, 11, 12], False, None),
    ("S", "amt", "___ za pasoš je trideset maraka."): ("trideset", [30, 40, 50, 60], False, None),
    ("K", "amt", "Taksa za pasoš je trideset maraka."): ("trideset", [30, 40, 50, 60], False, None),
    ("S", "arbeitsvertrag", "Imam pet godina ___."): ("pet", [5, 6, 7, 8, 10, 12, 15, 20], False, None),
    ("K", "arbeitsvertrag", "Imam pet godina iskustva."): ("pet", [5, 6, 7, 8, 10, 12, 15, 20], False, None),
    ("S", "arbeitsvertrag", "Probni ___ traje tri mjeseca."): ("tri", [2, 3, 4], False, None),
    ("K", "arbeitsvertrag", "Probni rad traje tri mjeseca."): ("tri", [2, 3, 4], False, None),
    ("S", "mehrzahl", "Imam dvije ___."): ("dvije", [2, 3, 4], True, None),
    ("K", "mehrzahl", "Imam dvije sestre."): ("dvije", [2, 3, 4], True, None),
    ("S", "reflexiv", "Nalazimo ___ u pet."): ("pet", [3, 4, 5, 6, 7, 8], False, "uhrzeit"),
    ("K", "reflexiv", "Nalazimo se u pet."): ("pet", [3, 4, 5, 6, 7, 8], False, "uhrzeit"),
    ("S", "routine", "___ u sedam sati."): ("sedam", [5, 6, 7, 8, 9], False, None),
    ("K", "routine", "Ustajem u sedam sati."): ("sedam", [5, 6, 7, 8, 9], False, None),
    ("S", "routine", "Idem ___ u jedanaest."): ("jedanaest", [9, 10, 11, 12], False, "uhrzeit"),
    ("K", "verben", "Idem spavati u jedanaest."): ("jedanaest", [9, 10, 11, 12], False, "uhrzeit"),
    ("S", "mengen", "Imam trideset ___."): ("trideset", [18, 20, 30, 40, 50, 60, 70], False, None),
    ("K", "verben", "Imam trideset godina."): ("trideset", [18, 20, 30, 40, 50, 60, 70], False, None),
    ("S", "mengen", "Ostajemo pet ___."): ("pet", [2, 3, 4, 5, 6, 7, 10, 14], False, "dana"),
    ("K", "saetze", "Mi ostajemo pet dana."): ("pet", [2, 3, 4, 5, 6, 7, 10, 14], False, "dana"),
    ("K", "saetze", "Moja sestra ima pet godina"): ("pet", [5, 6, 7, 8, 10, 12, 15, 18], False, None),
    ("K", "saetze", "Ja bih htjela tri jabuke, molim"): ("tri", [2, 3, 4], True, None),
    ("K", "saetze", "Autobus dolazi u deset"): ("deset", [7, 8, 9, 10, 11, 12], False, "uhrzeit"),
    ("K", "einkauf_orte", "Ne znam, možda pet maraka."): ("pet", [5, 6, 7, 8, 10, 15, 20], False, None),
}


def _mit_zahl():
    import vokabeln
    raus = {}
    for art, liste, feld in (("S", vokabeln.SAETZE, "text"), ("K", vokabeln.SATZBAU, "bs")):
        for s in liste:
            if "zahl" in s:
                schluessel = (art, s["kat"], s[feld])
                assert schluessel not in raus, schluessel
                raus[schluessel] = s
    return raus


def test_genau_die_freigegebene_tabelle_der_rest_bleibt_fest():
    """Nur genau diese Sätze und Zahlen - Ajdin entscheidet, was bosnisch
    dasteht (AGENTS.md, Regel 4). Nicht in der Tabelle und also fest:
    „___ kahve, molim.“ im Level mengen, Menge 1, die Reihen und Rechnungen
    im Level zahlen, die Sammelzahl (Sto za dvoje), das Stockwerk. Die
    Grammatik-Aufgaben und Geschichten haben kein Feld."""
    ist = {k: (s["zahl"]["wort"], s["zahl"]["werte"], bool(s["zahl"].get("weiblich")), s["zahl"].get("frei"))
           for k, s in _mit_zahl().items()}
    assert ist == TABELLE
    import geschichten
    import grammatik
    import vokabeln
    fest = [s for s in vokabeln.SAETZE if s["kat"] == "mengen" and s["text"] == "___ kahve, molim."]
    assert len(fest) == 1 and "zahl" not in fest[0]
    assert not any("zahl" in s for s in vokabeln.SAETZE + vokabeln.SATZBAU if s["kat"] == "zahlen")
    for bs in ("Sto za dvoje, molim", "Stan je na trećem spratu."):
        assert [s for s in vokabeln.SATZBAU if s["bs"] == bs and "zahl" not in s], bs
    assert '"zahl":' not in json.dumps(grammatik.GRAMMATIK) + json.dumps(geschichten.GESCHICHTEN)


def test_pruefung_ohne_befund_in_jeder_sprache(alle_daten):
    import inhalt
    for code, daten in alle_daten.items():
        assert inhalt.pruefe_zahlen(daten) == [], code


@pytest.mark.parametrize("aenderung, meldung", [
    ({}, None),
    ({"werte": [3, 4]}, "die heutige Zahl 2 fehlt"),
    ({"werte": [2, 3, 5]}, "verschiedenen Formen"),
    ({"werte": [2, 2, 3]}, "doppelt"),
    ({"werte": [2, 21]}, "kein Zahlwort für 21"),
    ({"wort": "Dva"}, "kein Zahlwort"),
    ({"de": "Ich habe {n} Brüder, {n}."}, "2 Platzhalter"),
    ({"de": "Ich habe zwei Brüder."}, "0 Platzhalter"),
    ({"de": "Ich habe {lok} Brüder."}, "nur im Türkischen"),
    ({"de": "Ich habe {n} Brüder und 1 Schwester."}, "Ziffer"),
    ({"frei": "uhrzeit"}, "braucht 'u'"),
    ({"frei": "dana"}, "braucht 'dana'"),
    ({"frei": "egal"}, "'frei' ist"),
    ({"farbe": "rot"}, "unbekannte Felder"),
    ({"bs": "Imam dva brata, dva."}, "2-mal"),
    ({"auch": ["Imam brata."]}, "0-mal"),
    ({"bs": "Imam dvanaest brata."}, "0-mal"),        # ganzes Wort: dva steckt nicht in dvanaest
])
def test_pruefung_findet_fehler(aenderung, meldung):
    import inhalt
    zahl = {"wort": "dva", "werte": [2, 3, 4], "de": "Ich habe {n} Brüder."}
    satz = {"kat": "basics", "bs": "Imam dva brata.", "auch": ["Dva brata imam."], "de": "Ich habe zwei Brüder."}
    for k, v in aenderung.items():
        (satz if k in ("bs", "auch") else zahl)[k] = v
    satz["zahl"] = zahl
    befunde = inhalt.pruefe_zahlen({"saetze": [], "satzbau": [satz], "sprache": "de"})
    if meldung is None:
        assert befunde == []
    else:
        assert len(befunde) >= 1 and any(meldung in b for b in befunde), befunde


@pytest.mark.parametrize("satz, frei, werte", [
    ({"kat": "x", "bs": "Ostajemo dva dana.", "de": "x"}, "dana", [2, 5, 14]),
    ({"kat": "x", "bs": "Nalazimo se u pet.", "auch": ["U pet se nalazimo."], "de": "x"}, "uhrzeit", [3, 5]),
    ({"kat": "x", "text": "Nalazimo ___ u pet.", "answer": "se", "de": "x"}, "uhrzeit", [3, 5]),
])
def test_frei_erlaubt_gemischte_formen(satz, frei, werte):
    import inhalt
    satz = dict(satz, zahl={"wort": "pet" if "pet" in str(satz) else "dva", "werte": werte, "frei": frei,
                            "de": "um {n}"})
    liste = "saetze" if "text" in satz else "satzbau"
    assert inhalt.pruefe_zahlen({"saetze": [], "satzbau": [], liste: [satz]}) == []
    ohne = dict(satz, zahl=dict(satz["zahl"], frei=None))
    assert any("verschiedenen Formen" in b for b in inhalt.pruefe_zahlen({"saetze": [], "satzbau": [], liste: [ohne]}))


def test_englisch_o_clock_nur_bis_zwoelf():
    import inhalt
    satz = {"kat": "x", "bs": "Jedemo u sedam sati.", "de": "x",
            "zahl": {"wort": "sedam", "werte": [7, 13], "de": "We eat at {n} o'clock."}}
    assert any("o'clock" in b for b in inhalt.pruefe_zahlen({"saetze": [], "satzbau": [satz], "sprache": "en"}))


def test_grammatik_klassen():
    import inhalt
    erwartet = {0: "5+", 1: "1", 2: "2-4", 3: "2-4", 4: "2-4", 5: "5+", 10: "5+", 11: "5+", 12: "5+",
                13: "5+", 14: "5+", 15: "5+", 20: "5+", 21: "1", 22: "2-4", 24: "2-4", 25: "5+", 100: "5+"}
    assert {n: inhalt.zahl_klasse(n) for n in erwartet} == erwartet
    # Ohne "frei" hat jede Zeile eine einzige Klasse, die von heute
    for (art, kat, satz), (wort, werte, weiblich, frei) in TABELLE.items():
        heute = inhalt.zahl_wert(wort, weiblich)
        klassen = {inhalt.zahl_klasse(n) for n in werte}
        if frei is None:
            assert klassen == {inhalt.zahl_klasse(heute)}, satz
    # „dana“ ist für 2-4 und ab 5 gleich, und nur Satz 16 mischt so
    assert {k[2] for k, v in TABELLE.items() if v[3] == "dana"} == {"Ostajemo pet ___.", "Mi ostajemo pet dana."}


def test_zahlwoerter():
    import inhalt
    assert [inhalt.zahl_wort(n) for n in (2, 3, 4, 5, 11, 14, 18, 20, 30, 40, 60, 90, 100)] == [
        "dva", "tri", "četiri", "pet", "jedanaest", "četrnaest", "osamnaest",
        "dvadeset", "trideset", "četrdeset", "šezdeset", "devedeset", "sto"]
    assert inhalt.zahl_wort(2, weiblich=True) == "dvije"
    assert inhalt.zahl_wort(3, weiblich=True) == "tri"
    assert inhalt.zahl_wort(21) is None and inhalt.zahl_wort(True) is None
    assert inhalt.zahl_wert("dvije", True) == 2 and inhalt.zahl_wert("dvije") is None
    assert inhalt.zahl_wert("sto") == 100


@pytest.mark.parametrize("text, alt, neu, soll", [
    ("Dvije kahve, molim.", "dvije", "tri", "Tri kahve, molim."),
    ("Molim dvije kahve.", "dvije", "četiri", "Molim četiri kahve."),
    ("Imam pet godina iskustva.", "pet", "dvanaest", "Imam dvanaest godina iskustva."),
    ("Petak je pet.", "pet", "šest", "Petak je šest."),           # nur das ganze Wort
    ("Pet dana ostajemo.", "pet", "šest", "Šest dana ostajemo."),  # Großschreibung bleibt
    ("Nalazimo se u pet.", "pet", "tri", "Nalazimo se u tri."),
])
def test_zahl_ersetzen(text, alt, neu, soll):
    import inhalt
    assert inhalt.zahl_ersetzen(text, alt, neu) == soll


def test_tuerkische_endung():
    import inhalt
    erwartet = {1: "1'de", 2: "2'de", 3: "3'te", 4: "4'te", 5: "5'te", 6: "6'da", 7: "7'de", 8: "8'de",
                9: "9'da", 10: "10'da", 11: "11'de", 12: "12'de", 13: "13'te", 14: "14'te",
                18: "18'de", 20: "20'de", 30: "30'da", 40: "40'ta", 50: "50'de", 60: "60'ta",
                70: "70'te", 80: "80'de", 90: "90'da", 100: "100'de"}
    assert {n: inhalt.tr_lokativ(n) for n in erwartet} == erwartet


def _satz(daten, art, kat, text):
    liste, feld = (daten["saetze"], "text") if art == "S" else (daten["satzbau"], "bs")
    treffer = [s for s in liste if s["kat"] == kat and s[feld] == text]
    assert len(treffer) == 1, (art, kat, text)
    return treffer[0]


@pytest.mark.parametrize("code, art, kat, text, n, soll", [
    ("de", "S", "zeit", "Sada je ___ sati.", 7, "Jetzt ist es 7 Uhr."),
    ("de", "K", "essen", "Dvije kahve, molim.", 3, "3 Kaffee, bitte."),
    ("de", "S", "mengen", "Ostajemo pet ___.", 14, "Wir bleiben 14 Tage."),
    ("en", "S", "saetze", "Jedemo u ___ sati.", 12, "We eat at 12 o'clock."),
    ("en", "K", "saetze", "Ja bih htjela tri jabuke, molim", 2, "I would like 2 apples, please"),
    ("tr", "S", "saetze", "Jedemo u ___ sati.", 7, "Saat 7'de yemek yiyoruz."),
    ("tr", "S", "saetze", "Jedemo u ___ sati.", 9, "Saat 9'da yemek yiyoruz."),
    ("tr", "K", "reflexiv", "Nalazimo se u pet.", 3, "Saat 3'te buluşuyoruz."),
    ("tr", "K", "saetze", "Autobus dolazi u deset", 10, "Otobüs saat 10'da geliyor"),
    ("tr", "S", "zeit", "Sada je ___ sati.", 11, "Şimdi saat 11."),
    ("tr", "S", "mengen", "Imam trideset ___.", 40, "40 yaşındayım."),
    ("fr", "S", "amt", "Imam ___ u ponedjeljak u deset sati.", 8, "J'ai un rendez-vous lundi à 8 heures."),
    ("sv", "S", "arbeitsvertrag", "Probni ___ traje tri mjeseca.", 4, "Provanställningen varar i 4 månader."),
    ("nl", "S", "einkaufen", "Jakna košta ___ maraka.", 100, "De jas kost 100 mark."),
    ("nb", "S", "mehrzahl", "Imam dvije ___.", 3, "Jeg har 3 søstre."),
    ("da", "K", "einkauf_orte", "Ne znam, možda pet maraka.", 20, "Jeg ved det ikke, måske 20 mark."),
])
def test_bedeutung_mit_ziffer(alle_daten, code, art, kat, text, n, soll):
    import inhalt
    assert inhalt.zahl_fassung(_satz(alle_daten[code], art, kat, text), n)["de"] == soll


def test_jede_fassung_jede_sprache_genau_eine_ziffer(alle_daten, grunddaten):
    import re

    import inhalt

    def bosnisch(daten):
        return [(s.get("zahl") or {}).get("wort") for s in daten["saetze"] + daten["satzbau"]] + \
               [(s.get("zahl") or {}).get("werte") for s in daten["saetze"] + daten["satzbau"]]

    for code, daten in alle_daten.items():
        # Bosnisch bleibt bosnisch: Zahlwort und Zahlen sind in jeder Sprache dieselben
        assert bosnisch(daten) == bosnisch(grunddaten), code
        for s in daten["saetze"] + daten["satzbau"]:
            for n, f in inhalt.zahl_fassungen(s):
                assert "{" not in f["de"], (code, f["de"])
                assert re.findall(r"\d+", f["de"]) == [str(n)], (code, f["de"])


def test_bosnisch_steht_als_wort(grunddaten):
    import inhalt
    for s in grunddaten["saetze"] + grunddaten["satzbau"]:
        for n, f in inhalt.zahl_fassungen(s):
            ganz = inhalt.fertiger_satz(f)
            wort = inhalt.zahl_wort(n, s["zahl"].get("weiblich"))
            assert inhalt.zahl_zaehlen(ganz, wort) == 1, (ganz, wort)
            assert not any(ch.isdigit() for ch in ganz), ganz
    # Die heutige Zahl gibt den heutigen Satz
    for s in grunddaten["saetze"] + grunddaten["satzbau"]:
        if "zahl" in s:
            heute = inhalt.zahl_wert(s["zahl"]["wort"], s["zahl"].get("weiblich"))
            f = inhalt.zahl_fassung(s, heute)
            assert inhalt.fertiger_satz(f) == inhalt.fertiger_satz(s)
            assert f.get("auch") == s.get("auch")


def test_jede_fassung_hat_ton(wurzel, grunddaten):
    """In der App aus dem Store: web/audio und dazu, was es nur von Emir gibt.
    Die neuen Fassungen spricht Emir; ihre Dateien liegen nur in der Hülle."""
    import ton_bauen
    import ton_pruefen
    index = json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8"))
    emir = ton_bauen.nur_emir()
    haben = {e["key"] for e in index["toene"]} | set(emir)
    gesammelt = {p["key"] for p in ton_bauen.sammle()}
    import inhalt
    huelle = ton_pruefen._huelle_audio()
    fehlt, neu = [], 0
    for s in grunddaten["saetze"] + grunddaten["satzbau"]:
        for n, f in inhalt.zahl_fassungen(s):
            k = ton_bauen.schluessel(inhalt.fertiger_satz(f))
            if k not in haben or k not in gesammelt:
                fehlt.append(k)
            if k in emir:
                neu += 1
                assert not os.path.exists(os.path.join(wurzel, "web", "audio", emir[k]["datei"])), k
                if huelle:
                    assert os.path.isfile(os.path.join(huelle, emir[k]["datei"])), k
    assert not fehlt, fehlt[:20]
    assert neu >= 94


def test_kacheln_gehen_mit_jeder_zahl_auf(grunddaten):
    import inhalt
    for s in grunddaten["satzbau"]:
        for n, f in inhalt.zahl_fassungen(s):
            kacheln = inhalt.satz_kacheln(f["bs"])
            assert len(kacheln) == len(inhalt.satz_kacheln(s["bs"])), f["bs"]
            vorrat = collections.Counter(kacheln)
            for v in f.get("auch", []):
                assert not collections.Counter(inhalt.satz_kacheln(v)) - vorrat, (f["bs"], v)


def test_zahl_geht_an_die_app(alle_daten):
    for code, daten in alle_daten.items():
        k = [s for s in daten["satzbau"] if s["bs"] == "Sada je pet sati."][0]
        assert k["zahl"]["werte"] == [5, 6, 7, 8, 9, 10, 11, 12], code
        assert k["zahl"]["wort"] == "pet", code
    assert [s for s in alle_daten["en"]["satzbau"] if s["bs"] == "Sada je pet sati."][0]["zahl"]["de"] == \
        "It is {n} o'clock now."


def test_dva_plus_dva_su_cetiri(index_html):
    """„Auf „su“ ändern“ (Ajdin, 25.10.2026). Fortschritt in Fehler-Topf und
    Stern zieht über SAETZE_UMBENANNT mit; die Aufnahme ist von Emir."""
    import ton_bauen
    import vokabeln
    bs = [s["bs"] for s in vokabeln.SATZBAU if s["kat"] == "zahlen" and "plus dva" in s["bs"]]
    assert bs == ["Dva plus dva su četiri."]
    assert "'k:zahlen|Dva plus dva je četiri.': 'k:zahlen|Dva plus dva su četiri.'" in index_html
    assert ton_bauen.nur_emir()["dva plus dva su četiri."]["datei"] == "w2520.mp3"
