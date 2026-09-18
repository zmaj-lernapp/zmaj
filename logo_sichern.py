# -*- coding: utf-8 -*-
r"""
logo_sichern.py  –  holt das SmartDragon-Zeichen aus der App heraus

Das Logo lebt als SVG mitten in web/index.html. Dort ist es richtig
aufgehoben – die App braucht es da –, aber es steckt eben in einer
180-KB-Datei. Für alles außerhalb der App (Play-Konto, Briefkopf,
Rechnung, Vorstellung in der Schule) braucht man es als eigene Datei.

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" logo_sichern.py

Schreibt nach store/:

    smartdragon-logo.svg     Kopf und Schriftzug, Maul zu, ohne Feuer.
                             Das ist das Zeichen zum Weitergeben.
    smartdragon-feuer.svg    Nur der Kopf, Maul offen, Flamme voll raus –
                             wie im Vorspann auf dem Höhepunkt. Ohne
                             Schriftzug, weil der dort noch gar nicht
                             steht und sonst in der Flamme läge.

Beide ohne Bewegung: ein Standbild lässt sich überall einsetzen, eine
Animation nicht. Beide ohne eigenen Hintergrund – sie gehören auf dunklen
Grund (#060C20), so wie im Vorspann.

Nach jeder Änderung am Zeichen einfach noch einmal laufen lassen.
"""
import io
import os
import re
import xml.dom.minidom

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, "web", "index.html")
ZIEL = os.path.join(HIER, "store")


def svg_holen():
    t = io.open(QUELLE, encoding="utf-8").read()
    # Zwischen dem div und dem svg steht ein Kommentar – der darf da sein
    m = re.search(r'<div id="vorspann"[^>]*>(?:\s|<!--.*?-->)*(<svg.*?</svg>)', t, re.S)
    if not m:
        raise SystemExit("Das Zeichen steckt nicht mehr an der erwarteten Stelle in web/index.html")
    return m.group(1)


def gruppe_raus(svg, kennung):
    """Eine <g>-Gruppe samt Inhalt entfernen.

    Mit einem regulären Ausdruck geht das nicht: In der Feuergruppe
    stecken weitere <g>, und ein nicht-gieriges Muster hört beim ERSTEN
    </g> auf – also mitten drin. Deshalb die Ebenen mitzählen.
    """
    start = svg.find('<g id="%s"' % kennung)
    if start < 0:
        return svg
    i, tiefe = start, 0
    while i < len(svg):
        if svg.startswith("<g", i):
            tiefe += 1
            i += 2
        elif svg.startswith("</g>", i):
            tiefe -= 1
            i += 4
            if tiefe == 0:
                break
        else:
            i += 1
    return svg[:start].rstrip() + "\n" + svg[i:].lstrip("\n")


def block_raus(svg, auf, zu):
    a = svg.find(auf)
    if a < 0:
        return svg
    b = svg.find(zu, a) + len(zu)
    return svg[:a].rstrip() + "\n" + svg[b:].lstrip("\n")


def aufraeumen(svg, mit_feuer):
    """Ohne Bewegung, ohne Maske – und wahlweise ohne Feuer."""
    if mit_feuer:
        # Maul offen, wie auf dem Höhepunkt der Bewegung
        svg = svg.replace('<g id="vsKiefer">',
                          '<g id="vsKiefer" transform="rotate(11 150 142)">')
        # Der Schriftzug muss weg: im Vorspann erscheint er erst, wenn die
        # Flamme zurückgeht. Nebeneinander lägen beide übereinander.
        svg = gruppe_raus(svg, "vsName")
        svg = svg.replace('viewBox="11 0 600 200"', 'viewBox="8 40 590 165"')
    else:
        svg = gruppe_raus(svg, "vsFeuer")
        svg = gruppe_raus(svg, "vsGlut")
    # Die Maske legt im Vorspann den Namen nach und nach frei. Im Standbild
    # steht er einfach da.
    svg = block_raus(svg, "<defs>", "</defs>")
    svg = svg.replace(' clip-path="url(#vsFrei)"', "")
    svg = svg.replace('<g id="vsName">', "<g>")
    return svg


def schreibe(name, svg, hinweis):
    kopf = ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<!-- %s\n'
            '     Erzeugt von logo_sichern.py aus web/index.html.\n'
            '     Gehoert auf dunklen Grund (#060C20). -->\n' % hinweis)
    pfad = os.path.join(ZIEL, name)
    io.open(pfad, "w", encoding="utf-8").write(kopf + svg + "\n")
    xml.dom.minidom.parse(pfad)          # bricht ab, wenn etwas zerschnitten wurde
    print("  %-26s %6d Bytes   geprueft" % (name, os.path.getsize(pfad)))


def main():
    os.makedirs(ZIEL, exist_ok=True)
    roh = svg_holen()
    print("Zeichen aus web/index.html geholt, %d Zeichen\n" % len(roh))
    schreibe("smartdragon-logo.svg", aufraeumen(roh, False),
             "SmartDragon - Zeichen des Studios, Maul zu, ohne Feuer")
    schreibe("smartdragon-feuer.svg", aufraeumen(roh, True),
             "SmartDragon - Kopf mit Flamme, Maul offen, ohne Schriftzug")
    print("\nLiegt in: %s" % ZIEL)


if __name__ == "__main__":
    main()
