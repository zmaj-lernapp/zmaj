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

ANGEWENDET am 05.10.2026 (Build 91). Das Skript bleibt, weil
tests/test_richten.py den angewendeten Stand prueft.

Probelauf:  python sicherheit2_richten.py
Schreiben:  python sicherheit2_richten.py --schreiben
"""
import richten

INDEX = richten.INDEX

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
    neu, fehler = richten.ersetze_einmal(html, AENDERUNGEN)
    return neu, fehler + richten.gleichgewicht(html, neu)


def main(argv=None):
    return richten.main(argv, AENDERUNGEN, anwenden, "sicherheit2_richten.py")


if __name__ == "__main__":
    raise SystemExit(main())
