# -*- coding: utf-8 -*-
r"""
entwuerfe_anwenden.py  –  wendet geprüfte Änderungsentwürfe einzeln an

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" entwuerfe_anwenden.py <entwuerfe.json>
    ... --schreiben

Die anderen Änderungsskripte in diesem Projekt behandeln ein Thema und
brechen ab, sobald etwas nicht stimmt. Das ist richtig, solange die
Änderungen zusammengehören.

Hier ist es anders: Es kommen mehrere unabhängige Entwürfe auf einmal, und
einer soll die übrigen nicht aufhalten. Deshalb prüft dieses Skript jeden
einzeln und überspringt, was nicht passt — mit Begründung.

WAS GEPRÜFT WIRD, je Entwurf

  1. Kommt der alte Text genau einmal vor? Sonst übersprungen.
  2. Ist die Datei danach noch gültiges JavaScript? Sonst wird dieser eine
     Entwurf zurückgenommen, die übrigen bleiben.
  3. Benutzt der neue Text nur Oberflächentexte, die es gibt? Ein t('...')
     mit unbekanntem Schlüssel würde dem Nutzer den rohen Schlüssel zeigen.

Die Ausgangsdatei wird vorher als *.vor_entwuerfe gesichert.

ERWARTETES FORMAT der JSON-Datei:

    {"anwendbar": [
      {"befund": "...", "alt": "...", "neu": "...", "warum": "..."},
      ...
    ]}
"""

import io
import json
import os
import re
import shutil
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, "web", "index.html")
SCHREIBEN = "--schreiben" in sys.argv

args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    print("Aufruf: entwuerfe_anwenden.py <entwuerfe.json> [--schreiben]")
    sys.exit(1)
QUELLE = args[0]


def js_pruefen(text):
    """Zieht das JavaScript heraus und lässt node die Syntax prüfen."""
    teile = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", text, re.S)
    if not teile:
        return False, "kein <script>-Block gefunden"
    probe = os.path.join(HIER, "_syntaxprobe.js")
    io.open(probe, "w", encoding="utf-8").write("\n;\n".join(teile))
    try:
        e = subprocess.run(["node", "--check", probe],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return e.returncode == 0, e.stdout.decode("utf-8", "replace").strip()[:200]
    finally:
        if os.path.exists(probe):
            os.remove(probe)


def textschluessel(neu):
    """Alle t('...') und tp('...') im neuen Text."""
    return set(re.findall(r"\bt\(\s*'([^']+)'", neu)) | \
           set(re.findall(r"\btp\(\s*'([^']+)'", neu))


def bekannte_schluessel():
    pfad = os.path.join(HIER, "web", "inhalt", "de.json")
    if not os.path.exists(pfad):
        return None
    d = json.load(io.open(pfad, encoding="utf-8"))
    texte = d.get("texte") or {}
    if not texte:
        for v in d.values():
            if isinstance(v, dict) and any(k.startswith("set.") for k in v):
                texte = v
                break
    return set(texte)


def main():
    entwuerfe = json.load(io.open(QUELLE, encoding="utf-8"))
    liste = entwuerfe.get("anwendbar", entwuerfe if isinstance(entwuerfe, list) else [])
    if not liste:
        print("Keine Entwürfe in %s" % os.path.basename(QUELLE))
        return 1

    text = io.open(ZIEL, encoding="utf-8", newline="").read()
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    bekannt = bekannte_schluessel()

    print("%d Entwürfe aus %s" % (len(liste), os.path.basename(QUELLE)))
    print("=" * 68)

    angewandt, uebersprungen = [], []
    for i, e in enumerate(liste, 1):
        name = e.get("befund", "Entwurf %d" % i)[:52]
        alt, neu = e.get("alt", ""), e.get("neu", "")

        if not alt or not neu:
            uebersprungen.append((name, "alt oder neu fehlt"))
            print("  [ ] %-54s alt/neu fehlt" % name)
            continue

        alt_n = alt.replace("\r\n", "\n")
        n = text.count(alt_n)
        if n != 1:
            uebersprungen.append((name, "%d Treffer statt 1" % n))
            print("  [ ] %-54s %d Treffer" % (name, n))
            continue

        # Unbekannte Oberflächentexte?
        if bekannt is not None:
            fehlend = textschluessel(neu) - bekannt
            if fehlend:
                uebersprungen.append((name, "unbekannte Texte: %s" % ", ".join(sorted(fehlend))))
                print("  [ ] %-54s Text fehlt: %s" % (name, ", ".join(sorted(fehlend))[:24]))
                continue

        vorher = text
        text = text.replace(alt_n, neu.replace("\r\n", "\n"))

        ok, meldung = js_pruefen(text)
        if not ok:
            text = vorher                       # nur diesen einen zurücknehmen
            uebersprungen.append((name, "danach kein gültiges JavaScript: %s" % meldung[:90]))
            print("  [ ] %-54s JS kaputt" % name)
            continue

        angewandt.append(name)
        print("  [x] %-54s ok" % name)

    print("=" * 68)
    print("%d angewandt, %d übersprungen" % (len(angewandt), len(uebersprungen)))
    if uebersprungen:
        print()
        print("Übersprungen:")
        for name, grund in uebersprungen:
            print("   %-52s %s" % (name, grund))

    if not angewandt:
        print("\nNichts anzuwenden.")
        return 0

    if SCHREIBEN:
        sicherung = ZIEL + ".vor_entwuerfe"
        if not os.path.exists(sicherung):
            shutil.copy2(ZIEL, sicherung)
            print("\nAusgangsstand gesichert: %s" % os.path.basename(sicherung))
        io.open(ZIEL, "w", encoding="utf-8", newline="").write(
            text.replace("\n", "\r\n") if crlf else text)
        print("geschrieben: %s" % os.path.basename(ZIEL))
    else:
        print("\n(Probelauf. Mit --schreiben wirklich anwenden.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
