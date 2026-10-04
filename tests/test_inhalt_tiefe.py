# -*- coding: utf-8 -*-
"""Feinere Prüfungen am Lerninhalt, in allen acht Sprachen.

Jede Prüfung hier steht für einen Fehler, den ein Lernender sehen würde:
eine Tabelle mit verrutschter Spalte, zwei gleiche Antwortknöpfe, ein
angetipptes Wort ohne Übersetzung.
"""


def tabellen(erklaerung):
    for teil in erklaerung:
        if isinstance(teil, dict) and "tabelle" in teil:
            yield teil["tabelle"]


def test_grammatik_tabellen_sind_rechteckig(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for kid, lektion in daten["grammatik"].items():
            for tab in tabellen(lektion.get("erklaerung", [])):
                breiten = {len(zeile) for zeile in tab}
                if len(breiten) != 1:
                    fehler.append((code, kid, sorted(breiten)))
    assert not fehler, fehler[:20]


def test_grammatik_optionen_ohne_dubletten(alle_daten):
    """Zwei gleiche Knöpfe: einer ist richtig, der andere falsch - der
    Lernende kann es nicht wissen. Passiert leicht erst durch Übersetzung."""
    fehler = []
    for code, daten in alle_daten.items():
        for kid, lektion in daten["grammatik"].items():
            for ue in lektion.get("uebungen", []):
                opt = ue.get("optionen", [])
                if len(set(opt)) != len(opt):
                    fehler.append((code, kid, ue.get("frage"), opt))
    assert not fehler, fehler[:20]


def test_grammatik_uebungen_vollstaendig(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for kid, lektion in daten["grammatik"].items():
            if not lektion.get("uebungen"):
                fehler.append((code, kid, "keine Übungen"))
            for ue in lektion.get("uebungen", []):
                if not str(ue.get("frage", "")).strip() or len(ue.get("optionen", [])) < 2:
                    fehler.append((code, kid, ue))
    assert not fehler, fehler[:20]


def test_woerterbuch_ohne_leere_eintraege(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for bs, bedeutung in daten["woerterbuch"].items():
            if not bs.strip() or not str(bedeutung).strip():
                fehler.append((code, bs))
    assert not fehler, fehler[:20]


def test_geschichten_vollstaendig_uebersetzt(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for g in daten["geschichten"]:
            if not g.get("uebersetzung", "").strip():
                fehler.append((code, g["id"], "keine Übersetzung"))
            for wort, bedeutung in g.get("vokabeln", {}).items():
                if not str(bedeutung).strip():
                    fehler.append((code, g["id"], wort))
            for f in g.get("fragen", []):
                if not f.get("frage", "").strip():
                    fehler.append((code, g["id"], "leere Frage"))
    assert not fehler, fehler[:20]


def test_level_haben_bezeichnung_und_tipp_in_jeder_sprache(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for k in daten["kategorien"]:
            if not k.get("label", "").strip():
                fehler.append((code, k["id"], "label"))
            if not k.get("tipp", "").strip():
                fehler.append((code, k["id"], "tipp"))
        for s in daten["sektionen"]:
            if not s.get("label", "").strip() or not s.get("beschreibung", "").strip():
                fehler.append((code, s["id"], "sektion"))
    assert not fehler, fehler[:20]


def test_jede_satzluecke_gehoert_zu_einem_level_mit_woertern(grunddaten):
    """Ein Lückensatz wird in der Lektion seines Levels gezeigt. Gibt es das
    Level nicht oder hat es keine Wörter, sieht ihn nie jemand."""
    mit_woertern = {k["id"] for k in grunddaten["kategorien"] if k["words"]}
    verwaist = [s["text"] for s in grunddaten["saetze"] if s["kat"] not in mit_woertern]
    assert not verwaist, verwaist[:20]
