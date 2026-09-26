# -*- coding: utf-8 -*-
r"""
texte_pruefen.py  –  findet Textschlüssel, die die App anzeigen will,
                     die es in web/inhalt aber nicht gibt

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" texte_pruefen.py

WARUM ES DAS GIBT: Am 26.09.2026 stand in den Einstellungen wörtlich
„set.sicherung_suchen" statt des Satzes, den der Nutzer lesen sollte. Ein
Änderungsskript hatte den Text in `sprachen.py` eingetragen, aber niemand
hatte `inhalt_bauen.py` laufen lassen. Das Handy liest die Texte
ausschließlich aus `web/inhalt/<sprache>.json`, nie aus `sprachen.py`.

Am PC fällt so etwas nie auf, weil der Server die Python-Dateien bei jedem
Aufruf frisch einliest. Auf dem Handy sieht der Nutzer den nackten Schlüssel.

WANN LAUFEN LASSEN: nach jeder Änderung an den Texten, und in jedem Fall
vor `app_bauen.py`. Der Rückgabewert ist 0, wenn alles stimmt, sonst 1.

GEPRÜFT WIRD IN DREI RICHTUNGEN:
  A  Das Programm will einen Text anzeigen, den keine Sprache hat.
  B  Eine Sprache führt einen Schlüssel, eine andere nicht.
  C  Ein Platzhalter wie {name} steht in einer Sprache, in einer anderen nicht.
     Das ist heimtückisch: der Text erscheint, aber mit einer Lücke.
"""
import io
import json
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]


def texte_holen(sprache):
    """Die Textliste einer Sprache aus web/inhalt/<sprache>.json."""
    pfad = os.path.join(HIER, "web", "inhalt", "%s.json" % sprache)
    d = json.load(io.open(pfad, encoding="utf-8"))
    texte = d.get("texte") or d.get("t") or {}
    if not texte:
        for wert in d.values():
            if isinstance(wert, dict) and any(
                    k.startswith("set.") or k.startswith("app.") for k in wert):
                texte = wert
                break
    return texte


def main():
    html = io.open(os.path.join(HIER, "web", "index.html"), encoding="utf-8").read()

    # Kommentare weg, bevor gesucht wird. Über t() steht ein Kommentar, der
    # die Benutzung erklärt und dabei wörtlich t('schluessel') schreibt.
    # Ohne diesen Schritt meldet das Skript dieses Beispiel als fehlenden Text.
    html = re.sub(r"/\*.*?\*/", "", html, flags=re.S)
    html = re.sub(r"^\s*//.*$", "", html, flags=re.M)

    verlangt = {}

    def merke(schluessel, wie):
        verlangt.setdefault(schluessel, set()).add(wie)

    for m in re.finditer(r'data-t(?:-title|-ph)?="([^"]+)"', html):
        merke(m.group(1), "data-t")
    for m in re.finditer(r"\bt\(\s*'([^']+)'", html):
        merke(m.group(1), "t()")
    for m in re.finditer(r'\bt\(\s*"([^"]+)"', html):
        merke(m.group(1), "t()")
    for m in re.finditer(r"\btp\(\s*'([^']+)'", html):
        merke(m.group(1), "tp()")

    # Schlüssel, die erst zur Laufzeit zusammengesetzt werden, lassen sich
    # von außen nicht auflösen. Sie werden gezählt, aber nicht bemängelt.
    gebaut = {k for k in verlangt if "+" in k or "$" in k or "{" in k}
    fest = sorted(set(verlangt) - gebaut)

    print("Das Programm verlangt %d feste Textschlüssel" % len(fest))
    if gebaut:
        print("(%d weitere entstehen zur Laufzeit und werden übersprungen)"
              % len(gebaut))
    print()

    texte = {s: texte_holen(s) for s in SPRACHEN}
    vorhanden = {s: set(texte[s]) for s in SPRACHEN}

    print("Vorhanden je Sprache:  " +
          "  ".join("%s %d" % (s, len(vorhanden[s])) for s in SPRACHEN))
    print()

    fehler = 0
    strich = "=" * 62

    print(strich)
    print("A. Das Programm will anzeigen, was die Sprache nicht hat")
    print(strich)
    treffer = False
    for schluessel in fest:
        fehlt_in = [s for s in SPRACHEN if schluessel not in vorhanden[s]]
        if fehlt_in:
            treffer = True
            fehler += 1
            print("  %-38s fehlt in: %s" % (schluessel, " ".join(fehlt_in)))
            print("      steht im Programm als %s" % ", ".join(sorted(verlangt[schluessel])))
    if not treffer:
        print("  nichts. Jeder verlangte Schlüssel liegt in allen acht Sprachen vor.")
    print()

    print(strich)
    print("B. Eine Sprache hat einen Schlüssel, eine andere nicht")
    print(strich)
    alle = set()
    for s in SPRACHEN:
        alle |= vorhanden[s]
    treffer = False
    for schluessel in sorted(alle):
        fehlt_in = [s for s in SPRACHEN if schluessel not in vorhanden[s]]
        if fehlt_in and len(fehlt_in) < len(SPRACHEN):
            treffer = True
            fehler += 1
            print("  %-38s fehlt in: %s" % (schluessel, " ".join(fehlt_in)))
    if not treffer:
        print("  nichts. Alle acht Sprachen führen dieselben Schlüssel.")
    print()

    print(strich)
    print("C. Platzhalter, die zwischen den Sprachen abweichen")
    print(strich)
    treffer = False
    for schluessel in sorted(vorhanden["de"]):
        if not isinstance(texte["de"].get(schluessel), str):
            continue
        soll = set(re.findall(r"\{(\w+)\}", texte["de"][schluessel]))
        for s in SPRACHEN[1:]:
            wert = texte[s].get(schluessel)
            if not isinstance(wert, str):
                continue
            ist = set(re.findall(r"\{(\w+)\}", wert))
            if ist != soll:
                treffer = True
                fehler += 1
                print("  %s" % schluessel)
                print("      de hat %s, %s hat %s"
                      % (sorted(soll) or "keinen", s, sorted(ist) or "keinen"))
    if not treffer:
        print("  nichts. Die Platzhalter stimmen in allen Sprachen überein.")
    print()

    print(strich)
    if fehler:
        print("%d Stellen gefunden, die einem Nutzer auffallen können." % fehler)
        print("Meistens hilft: inhalt_bauen.py laufen lassen.")
        return 1
    print("Keine fehlenden Texte. Die App kann alles anzeigen, was sie anzeigen will.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
