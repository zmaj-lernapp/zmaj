# -*- coding: utf-8 -*-
r"""
richten.py  –  gemeinsames Gerüst der Patch-Skripte (*_richten.py)

Jedes Patch-Skript folgt derselben Regel (AGENTS.md, Regel 7): Probelauf ist
Standard, geschrieben wird nur mit --schreiben, und kommt ein Anker nicht
genau einmal vor, wird gar nichts geschrieben. Bis zum 04.10.2026 hatte jedes
Skript diese Regel als eigene Kopie von main(), Ersetzungsschleife,
Klammerprüfung und CRLF-Behandlung. Die Kopien liefen auseinander (eines
prüfte HTML-Kommentare, eines nicht). Hier steht es einmal.

Ein Skript braucht nur:

    AENDERUNGEN = [(name, alt, neu), ...]

    def anwenden(html):
        neu, fehler = richten.ersetze_einmal(html, AENDERUNGEN)
        fehler += richten.gleichgewicht(html, neu)
        return neu, fehler

    if __name__ == "__main__":
        raise SystemExit(richten.main(None, AENDERUNGEN, anwenden, "x_richten.py"))
"""
import io
import os
import sys

ORDNER = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(ORDNER, "web", "index.html")

# Paare, deren Bilanz eine Ersetzung nicht verändern darf
PAARE = (("{", "}", "geschweifte Klammern"), ("(", ")", "runde Klammern"),
         ("/*", "*/", "Kommentare"), ("<!--", "-->", "HTML-Kommentare"))


def ersetze_einmal(html, aenderungen):
    """Ersetzt jeden Anker, der genau einmal vorkommt. (neuer Text, Fehlerliste)."""
    fehler, neu = [], html
    for name, alt, ersatz in aenderungen:
        n = neu.count(alt)
        if n != 1:
            fehler.append("%s: Stelle %d-mal gefunden statt einmal" % (name, n))
            continue
        neu = neu.replace(alt, ersatz)
    return neu, fehler


def gleichgewicht(alt, neu, paare=PAARE):
    """Fehlerliste, falls eine Ersetzung ein Klammer- oder Kommentarpaar aufreißt."""
    return ["%s aus dem Gleichgewicht" % was for auf, zu, was in paare
            if neu.count(auf) - neu.count(zu) != alt.count(auf) - alt.count(zu)]


def lies(datei):
    """(Text mit \\n, war_crlf). Git für Windows checkt mit CRLF aus, die Anker
    kennen nur \\n - also normalisieren und beim Schreiben zurückwandeln."""
    roh = io.open(datei, encoding="utf-8", newline="").read()
    return roh.replace("\r\n", "\n"), "\r\n" in roh


def schreibe(datei, text, crlf):
    with io.open(datei, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n") if crlf else text)


def main(argv, aenderungen, anwenden, skript):
    """Probelauf oder --schreiben, mit --datei für eine andere Kopie.
    Rückgabe 0 bei Erfolg, 1 bei Abbruch (nichts geschrieben)."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    argv = sys.argv[1:] if argv is None else argv
    datei = argv[argv.index("--datei") + 1] if "--datei" in argv else INDEX
    html, crlf = lies(datei)
    neu, fehler = anwenden(html)
    for name, _, _ in aenderungen:
        print("   %s %s" % ("✗" if any(f.startswith(name + ":") for f in fehler) else "✓", name))
    if fehler:
        print("\nABBRUCH - nichts geschrieben:")
        for f in fehler:
            print("   " + f)
        return 1
    if "--schreiben" in argv:
        schreibe(datei, neu, crlf)
        print("\ngeschrieben: %s" % os.path.relpath(datei, ORDNER))
        print("Danach: app_bauen.py - aber NICHT vor dem 07.10.2026 einreichen.")
    else:
        print("\n(Probelauf. Zum Schreiben: python %s --schreiben)" % skript)
    return 0
