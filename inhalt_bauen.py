# -*- coding: utf-8 -*-
r"""
inhalt_bauen.py  –  macht aus den Python-Dateien JSON für die Handy-App

Ein Handy kann vokabeln.py, geschichten.py, grammatik.py, sprachen.py und
uebersetzungen.py nicht lesen – das ist Python, und in der App läuft kein
Python. Dieses Skript schreibt den fertigen Inhalt als JSON nach web/inhalt,
eine Datei je Sprache.

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" inhalt_bauen.py

WANN LAUFEN LASSEN: Immer wenn du Wörter, Sätze, Geschichten, Grammatik oder
Texte geändert hast und die Handy-App das sehen soll. Am PC brauchst du es
nicht – dort liest der Server die Python-Dateien bei jedem Aufruf frisch ein.

WARUM ES NICHT ABWEICHEN KANN: Das Skript ruft dieselbe Funktion auf wie der
Server, nämlich start.lade_daten(). Was hier herauskommt, ist Zeichen für
Zeichen das, was der Browser am PC bekommt – nur als Datei statt als Antwort.
"""
import io
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, "web", "inhalt")
sys.path.insert(0, HIER)

# Diese Felder gehören nicht in die Datei:
#   audio  – die Tonspur steht in web/audio/index.json, die App liest sie
#            selbst. Hier wären es 2153 Dateinamen je Sprache, also achtmal
#            derselbe Ballast.
OHNE = ("audio",)


def main():
    import start
    import sprachen

    os.makedirs(ZIEL, exist_ok=True)
    codes = [s["code"] for s in sprachen.SPRACHEN]
    print("%d Sprachen: %s\n" % (len(codes), " ".join(codes)))

    liste, gesamt = [], 0
    for code in codes:
        daten = start.lade_daten(code)
        for feld in OHNE:
            daten.pop(feld, None)
        pfad = os.path.join(ZIEL, code + ".json")
        text = json.dumps(daten, ensure_ascii=False, separators=(",", ":"))
        io.open(pfad, "w", encoding="utf-8").write(text)
        gross = os.path.getsize(pfad)
        gesamt += gross
        liste.append((code, gross, daten))
        print("  %-3s %6.0f KB   %d Level, %d Sätze, %d Geschichten, %d Texte"
              % (code, gross / 1024.0, len(daten["kategorien"]),
                 len(daten["saetze"]), len(daten["geschichten"]),
                 len(daten["texte"])))

    # Ein Verzeichnis, damit die App weiß, was es gibt, ohne zu raten
    verzeichnis = {
        "version": 1,
        "grundsprache": sprachen.GRUNDSPRACHE,
        "sprachen": sprachen.SPRACHEN,
        "dateien": {c: c + ".json" for c in codes},
    }
    io.open(os.path.join(ZIEL, "liste.json"), "w", encoding="utf-8").write(
        json.dumps(verzeichnis, ensure_ascii=False, indent=1))

    print("\n%.1f MB in web/inhalt, dazu liste.json" % (gesamt / 1048576.0))
    pruefen(liste)


def pruefen(liste):
    """Was nützt eine Datei, die nur halb geschrieben wurde."""
    fehler = []
    for code, _, daten in liste:
        if not daten.get("kategorien"):
            fehler.append("%s: keine Level" % code)
        if len(daten.get("texte", {})) < 300:
            fehler.append("%s: nur %d Oberflächentexte" % (code, len(daten.get("texte", {}))))
        if daten.get("sprache") != code:
            fehler.append("%s: Datei meldet sich als %r" % (code, daten.get("sprache")))
        # Der bosnische Teil darf nie übersetzt werden
        erstes = daten["kategorien"][0]["words"][0]
        if erstes.get("bs") != "Merhaba":
            fehler.append("%s: erstes Wort ist %r statt Merhaba" % (code, erstes.get("bs")))

    # Alle Sprachen müssen dieselbe Menge Lernstoff haben
    mengen = {(len(d["kategorien"]), len(d["saetze"]), len(d["geschichten"]))
              for _, _, d in liste}
    if len(mengen) != 1:
        fehler.append("Sprachen haben unterschiedlich viel Inhalt: %s" % mengen)

    if fehler:
        print("\nFEHLER:")
        for f in fehler:
            print("  " + f)
        raise SystemExit(1)
    print("Geprüft: alle Sprachen vollständig und gleich groß.")


if __name__ == "__main__":
    main()
