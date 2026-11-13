# -*- coding: utf-8 -*-
"""B1-Lesetexte, Pakete 3 und 4 (Entscheidung 14a/15a/16a vom 13.11.2026).

Acht Texte für die Stufe "B1" hinter allen anderen Geschichten: je 150 bis
200 Wörter, ijekavisch, drei Fragen mit je drei Antworten. Vorlage:
Release\\Entscheidungen_2026-11-13\\lesetexte_proben.md. Dass jedes Wort im
Wörterbuch steht und alles in jeder Sprache übersetzt ist, prüfen schon
test_inhalt.py und test_inhalt_tiefe.py für alle Geschichten.
"""
import re

import ton_bauen

IDS = ["b1_doktor", "b1_selidba", "b1_rodjendan", "b1_utakmica",
       "b1_zanat", "b1_kahva", "b1_mejl", "b1_zmaj"]

# Formen, die es nur ekavisch gibt. Ijekavisch heißen sie mlijeko, lijepo,
# djeca, dijete, pjesma, rijeka, vrijeme, mjesto, snijeg, hljeb, uvijek,
# gdje, poslije, ovdje, dvije, djevojka, ljekar, mjesec, nedjelja, cijeli,
# sjedio, bijel, vidjeti, voljeti, razumjeti, vjerovati.
NUR_EKAVISCH = {
    "mleko", "lepo", "lep", "lepa", "deca", "dete", "pesma", "reka", "vreme",
    "mesto", "sneg", "hleb", "uvek", "gde", "posle", "ovde", "dve", "devojka",
    "lekar", "lek", "mesec", "nedelja", "nedelje", "ceo", "celo", "cela",
    "sedeo", "sedela", "beo", "bela", "belo", "videti", "videli", "voleti",
    "voleo", "volela", "razumem", "razumeti", "verovati", "pevali", "pevao",
}


def _geschichten(grunddaten):
    return {g["id"]: g for g in grunddaten["geschichten"]}


def test_alle_acht_hinter_den_alten_geschichten(grunddaten):
    ids = [g["id"] for g in grunddaten["geschichten"]]
    stellen = [ids.index(i) for i in IDS]
    assert stellen == sorted(stellen), "Reihenfolge der Pakete 3 und 4"
    ohne_b1 = [n for n, g in enumerate(grunddaten["geschichten"]) if g["stufe"] != "B1"]
    assert max(ohne_b1) < min(stellen), "B1 steht hinter allen anderen Stufen"


def test_stufe_b1_und_150_bis_200_woerter(grunddaten):
    g = _geschichten(grunddaten)
    for i in IDS:
        assert g[i]["stufe"] == "B1", i
        n = len(ton_bauen.textwoerter(g[i]["text"]))
        assert 150 <= n <= 200, (i, n)


def test_drei_fragen_mit_drei_antworten(grunddaten):
    g = _geschichten(grunddaten)
    for i in IDS:
        fragen = g[i]["fragen"]
        assert len(fragen) == 3, i
        for f in fragen:
            assert len(f["optionen"]) == 3 and len(set(f["optionen"])) == 3, (i, f["frage"])
            assert f["richtig"] in f["optionen"], (i, f["frage"])


def test_absaetze_wie_in_paket_1_und_2(alle_daten):
    """Absätze als Leerzeile in Text und Übersetzung, in jeder Sprache gleich
    viele (Prüfung 13.11.2026: ohne sie war jeder Text am 360-px-Bildschirm
    ein Block von zwei Bildschirmhöhen). Der Ton-Schlüssel hängt am Text, die
    Absätze müssen also vor ton_bauen.py stehen."""
    for code, daten in alle_daten.items():
        g = _geschichten(daten)
        for i in IDS:
            text, ueb = g[i]["text"], g[i]["uebersetzung"]
            absaetze = text.split("\n\n")
            assert len(absaetze) >= 4, (i, len(absaetze))
            assert len(ueb.split("\n\n")) == len(absaetze), (code, i)
            for t in (text, ueb):
                teile = t.split("\n\n")
                assert all(p and p == p.strip() and "\n" not in p for p in teile), (code, i)


def test_laenge_verraet_die_antwort_nicht(alle_daten, index_html):
    """renderChoice() setzt Antworten über 14 Zeichen kleiner und ohne
    Serifen. Ist nur die richtige so lang, sieht man sie (Prüfung 13.11.2026:
    5 von 24 Fragen auf Deutsch, 31 über alle Sprachen). Also ist in keiner
    Sprache nur die richtige Antwort lang. Und keine Antwort trägt einen
    Hinweis in Klammern, wie ihn Wörterbuch-Bedeutungen haben ("personne
    (négation)" stand im französischen Quiz)."""
    grenze = re.search(r"label\.length>(\d+)\?' long'", index_html)
    assert grenze, "Schwelle in renderChoice() nicht gefunden"
    grenze = int(grenze.group(1))
    fehler = []
    for code, daten in alle_daten.items():
        g = _geschichten(daten)
        for i in IDS:
            for n, f in enumerate(g[i]["fragen"], 1):
                assert f["richtig"] in f["optionen"], (code, i, n)
                lang = [o for o in f["optionen"] if len(o) > grenze]
                if lang == [f["richtig"]]:
                    fehler.append("%s %s Frage %d: %s" % (code, i, n, f["richtig"]))
                fehler += ["%s %s Frage %d: %s" % (code, i, n, o) for o in f["optionen"] if "(" in o]
    assert fehler == [], fehler


def test_kein_titel_und_keine_kennung_doppelt(grunddaten):
    """Themen, die es schon gab, kommen nicht noch einmal (Entscheidung 15a)."""
    titel = [g["titel"].lower() for g in grunddaten["geschichten"]]
    ids = [g["id"] for g in grunddaten["geschichten"]]
    assert len(titel) == len(set(titel)), sorted(t for t in titel if titel.count(t) > 1)
    assert len(ids) == len(set(ids)), sorted(i for i in ids if ids.count(i) > 1)


def test_ijekavisch(grunddaten):
    g = _geschichten(grunddaten)
    for i in IDS:
        woerter = set(re.findall(r"[^\W\d_]+", g[i]["text"].lower()))
        assert not woerter & NUR_EKAVISCH, (i, sorted(woerter & NUR_EKAVISCH))


def test_woerterbuch_b1_2_ist_eingetragen():
    """WOERTERBUCH_B1_2 ergänzt das WOERTERBUCH nur. Steht ein Wort dort schon,
    gilt der Eintrag dort, auch nach dem Zusammenführen mit anderen Lesetexten."""
    import geschichten
    for wort, bedeutung in geschichten.WOERTERBUCH_B1_2.items():
        assert wort == wort.lower() and bedeutung.strip(), wort
        assert wort in geschichten.WOERTERBUCH, wort


def test_bedeutung_aus_dem_zusammenhang(grunddaten):
    """Diese Formen meinen im Text etwas anderes als im allgemeinen Wörterbuch
    ("sto" = hundert, nicht Tisch; "ne smije" = darf nicht, nicht lacht). Sie
    stehen deshalb in den vokabeln der Geschichte, die vor dem WOERTERBUCH gelten."""
    g = _geschichten(grunddaten)
    erwartet = {
        ("b1_zanat", "sto"): "hundert",
        ("b1_kahva", "smije"): "darf (ne smije: darf nicht)",
        ("b1_rodjendan", "smije"): "darf (ne smije: darf nicht)",
        ("b1_utakmica", "prvo"): "erste (s) / zuerst",
        ("b1_utakmica", "karte"): "Karten / Tickets",
        ("b1_zmaj", "nego"): "sondern / als",
        ("b1_doktor", "vremena"): "Wetter / Zeit (Gen.)",
        ("b1_doktor", "jela"): "Essen (Gen.)",
    }
    for (gid, wort), bedeutung in erwartet.items():
        assert g[gid]["vokabeln"][wort] == bedeutung, (gid, wort)
