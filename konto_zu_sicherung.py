# -*- coding: utf-8 -*-
r"""
konto_zu_sicherung.py  –  alte Profildatei in eine Sicherung umwandeln

Bis zum 16.09.2026 lag der Lernstand in Dateien wie fortschritt_Amina.json.
Die Konten sind weg, die Dateien liegen nur noch in
sicherung_konten_2026-09-16. Dieses Skript macht daraus eine Datei, die die
App über „Einstellungen → Sicherung → Sicherung einlesen" annimmt.

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" konto_zu_sicherung.py

Ohne Angabe wandelt es alle gefundenen Profile um. Die fertigen Dateien
landen neben den alten und heißen zmaj-sicherung-<Name>.json.
"""
import io
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, "sicherung_konten_2026-09-16")

# Was die App aus einem Stand liest. Alles andere - Passwort, E-Mail,
# Bestätigungsstand - gehört nicht in eine Sicherung und bleibt draußen.
FELDER = ("gewusst", "bestanden", "gelesen", "tage", "frost", "besitz",
          "leben", "schutz", "tagwerk", "muenzen_ges", "muenzen_aus", "premium")


def wandeln(pfad):
    alt = json.load(io.open(pfad, encoding="utf-8"))
    stand = {f: alt[f] for f in FELDER if f in alt}
    name = os.path.basename(pfad)[len("fortschritt_"):-len(".json")]
    ziel = os.path.join(os.path.dirname(pfad), "zmaj-sicherung-%s.json" % name)
    io.open(ziel, "w", encoding="utf-8").write(json.dumps(
        {"app": "zmaj", "version": 1, "aus": name, "stand": stand},
        ensure_ascii=False, indent=1))
    print("  %-22s %3d Wörter, %2d Level, %2d Lerntage  ->  %s"
          % (name, len(stand.get("gewusst", [])), len(stand.get("bestanden", [])),
             len(stand.get("tage", [])), os.path.basename(ziel)))
    return ziel


def main():
    ordner = sys.argv[1] if len(sys.argv) > 1 else QUELLE
    if not os.path.isdir(ordner):
        raise SystemExit("Ordner nicht gefunden: %s" % ordner)
    dateien = sorted(f for f in os.listdir(ordner)
                     if f.startswith("fortschritt_") and f.endswith(".json"))
    if not dateien:
        raise SystemExit("Keine Profildateien in %s" % ordner)
    print("%d Profile in %s\n" % (len(dateien), ordner))
    for f in dateien:
        wandeln(os.path.join(ordner, f))
    print("\nFertig. In der App: Einstellungen → Sicherung → Sicherung einlesen.")
    print("Achtung: Das ersetzt den Stand auf dem Gerät, es wird nichts vermischt.")


if __name__ == "__main__":
    main()
