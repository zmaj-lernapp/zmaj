# -*- coding: utf-8 -*-
r"""Zwei kleine Haertungen aus der zweiten Sicherheitspruefung (04.10.2026).

Die Pruefung ging ueber alle Eingaben ausser dem Backup-Import (der hat
import_richten.py): URL-Parameter, Werte im Geraetespeicher, Texte, die als
HTML eingesetzt werden, mailto, Ladepfade. Kein Befund ist von aussen
ausnutzbar - kein XSS, kein Weg an der Vollversion vorbei. Zwei Stellen
sind trotzdem unnoetig zerbrechlich:

  1. ?neues-passwort=... und ?bestaetigen=... werden noch ausgewertet,
     obwohl es keine Konten mehr gibt (KONTEN_AN = false). Auf der Web-Demo
     oeffnet so ein Link einen Anmeldeschirm ohne Server dahinter. Ein
     Neuladen hilft, verloren geht nichts. Auf Android nicht erreichbar.
  2. zmaj_fest_probe = "toString" im Geraetespeicher: FESTE["toString"] ist
     die eingebaute Funktion, festSchmuck() wirft bei jedem Start. Setzen
     kann das nur, wer am Geraet selbst ist (Fernwartung, Entwicklerwerkzeuge).

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

Probelauf:  python sicherheit2_richten.py
Schreiben:  python sicherheit2_richten.py --schreiben
"""
import io
import os
import sys

ORDNER = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(ORDNER, "web", "index.html")

AENDERUNGEN = [
    ("Passwort-Link nur mit Konten",
     "  if(neuesPw){\n    kontoCode = neuesPw;",
     "  if(neuesPw && KONTEN_AN){      // ohne Konten gibt es nichts zurueckzusetzen\n    kontoCode = neuesPw;"),
    ("Bestaetigungs-Link nur mit Konten",
     "  if(bestaetigen){\n    geschichteAufraeumen();",
     "  if(bestaetigen && KONTEN_AN){\n    geschichteAufraeumen();"),
    ("Fest-Probe nur eigene Feste",
     "if(p && FESTE[p]) return p;",
     "if(p && Object.prototype.hasOwnProperty.call(FESTE, p)) return p;"),
]


def anwenden(html):
    """(neuer Text, Fehlerliste). Ein Fehler heisst: nichts wird geschrieben."""
    fehler, neu = [], html
    for name, alt, ersatz in AENDERUNGEN:
        n = neu.count(alt)
        if n != 1:
            fehler.append("%s: Stelle %d-mal gefunden statt einmal" % (name, n))
            continue
        neu = neu.replace(alt, ersatz)
    for auf, zu, was in (("{", "}", "geschweifte Klammern"), ("(", ")", "runde Klammern"),
                         ("/*", "*/", "Kommentare")):
        if neu.count(auf) - neu.count(zu) != html.count(auf) - html.count(zu):
            fehler.append("%s aus dem Gleichgewicht" % was)
    return neu, fehler


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    datei = argv[argv.index("--datei") + 1] if "--datei" in argv else INDEX
    html = io.open(datei, encoding="utf-8", newline="").read()
    neu, fehler = anwenden(html)
    for name, _, _ in AENDERUNGEN:
        print("   %s %s" % ("✗" if any(f.startswith(name) for f in fehler) else "✓", name))
    if fehler:
        print("\nABBRUCH - nichts geschrieben:")
        for f in fehler:
            print("   " + f)
        return 1
    if "--schreiben" in argv:
        io.open(datei, "w", encoding="utf-8", newline="").write(neu)
        print("\ngeschrieben. Danach: app_bauen.py - aber NICHT vor dem 07.10.2026 einreichen.")
    else:
        print("\n(Probelauf. Zum Schreiben: python sicherheit2_richten.py --schreiben)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
