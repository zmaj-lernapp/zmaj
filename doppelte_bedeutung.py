# -*- coding: utf-8 -*-
r"""
doppelte_bedeutung.py  –  findet Aufgaben, die nicht lösbar sind

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" doppelte_bedeutung.py

DAS PROBLEM: Zwei bosnische Wörter können in einer Oberflächensprache
dieselbe Übersetzung haben. Auf Dänisch heißen „majka" und „mama" beide
„mor".

Dann geht Folgendes schief:

  Schreib-Aufgabe   Auf dem Bildschirm steht „mor". Gemeint ist genau eines
                    der beiden Wörter. matches() trennt nur bei „ / " INNERHALB
                    eines Eintrags, die andere – sachlich völlig richtige –
                    Antwort gilt als falsch. Das kostet ein Herz.

  Auswahl-Aufgabe   distractors() wählt die Ablenker nach dem bosnischen Wort
                    aus, nicht nach der angezeigten Bedeutung. Stehen beide in
                    derselben Auswahl, ist die Frage nicht entscheidbar.

Auf Deutsch fällt das nie auf, weil dort „Mutter" und „Mama" verschieden sind.

GEPRÜFT WIRD in allen acht Oberflächensprachen, getrennt nach:
  A  Beide Wörter im selben Level  – trifft auch die Auswahl-Aufgabe
  B  Wörter in verschiedenen Levels – trifft nur die Schreib-Aufgabe
  C  Angesehen und so gewollt – steht mit Begründung in
     bedeutung_ausnahmen.json und zählt nicht mehr als offen

Am 27.09.2026 waren es 72 Stellen, nachdem je Sprache 557 Vokabeln
dazugekommen waren. bedeutungen_trennen.py hat die getrennt, für die die
Oberflächensprache ein eigenes Wort hat („tavuk eti" statt „tavuk" für
Hühnerfleisch, „storey" statt „floor" für das Stockwerk). Übrig blieb, was
sich nicht trennen lässt, ohne die Übersetzung zu verbiegen – das steht in
bedeutung_ausnahmen.json und erscheint hier unter C.
"""

import io
import json
import os
import sys
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
AUSNAHMEN = os.path.join(HIER, "bedeutung_ausnahmen.json")


def normal(s):
    """Wie matches() vergleicht: klein, ohne Rand, ohne Schlusszeichen."""
    return (s or "").strip().rstrip(".!?…").strip().lower()


def vermerkt():
    """{(sprache, bedeutung): warum} aus bedeutung_ausnahmen.json.

    Am 27.09.2026 hat bedeutungen_trennen.py die Doppelungen getrennt, für die
    die Oberflächensprache ein eigenes Wort hat. Was übrig blieb, steht dort
    mit Begründung – dasselbe Wort zweimal, oder eine Sprache, die für beide
    Bedeutungen nur ein Wort hat. Diese Fälle stehen unten unter C und nicht
    mehr zwischen den ungeprüften."""
    if not os.path.exists(AUSNAHMEN):
        return {}
    daten = json.load(io.open(AUSNAHMEN, encoding="utf-8"))
    gruende = daten.get("gruende", {})
    aus = {}
    for fall in daten.get("bleiben", []):
        schluessel = (fall["sprache"], normal(fall["bedeutung"]))
        aus[schluessel] = (fall.get("grund", "?"), fall.get("warum", ""),
                           gruende.get(fall.get("grund"), ""))
    return aus


def main():
    gesamt = 0
    aus = vermerkt()
    geprueft = 0
    unbekannt = []
    strich = "=" * 70

    for sprache in SPRACHEN:
        pfad = os.path.join(HIER, "web", "inhalt", "%s.json" % sprache)
        if not os.path.exists(pfad):
            print("%s: Datei fehlt" % sprache)
            continue
        d = json.load(io.open(pfad, encoding="utf-8"))

        # Bedeutung -> Liste von (bosnisch, level)
        nach_bedeutung = defaultdict(list)
        for k in d.get("kategorien", []):
            for w in k.get("words", []):
                bs, de = w.get("bs"), w.get("de")
                if not bs or not de:
                    continue
                # Ein Eintrag wie „schnell (m/w)" zählt als eine Bedeutung.
                # Mehrfachformen mit „ / " trennt matches() selbst auf.
                nach_bedeutung[normal(de)].append((bs, k.get("label", "?"), k.get("id")))

        treffer = {b: v for b, v in nach_bedeutung.items() if len(v) > 1}
        if not treffer:
            print("%s  nichts" % sprache)
            continue

        gleiches_level = []
        andere_level = []
        vermerkte = []
        for bedeutung, eintraege in sorted(treffer.items()):
            if (sprache, bedeutung) in aus:
                vermerkte.append((bedeutung, eintraege))
                geprueft += 1
                continue
            nach_level = defaultdict(list)
            for bs, label, kid in eintraege:
                nach_level[kid].append((bs, label))
            for kid, gruppe in nach_level.items():
                if len(gruppe) > 1:
                    gleiches_level.append((bedeutung, gruppe))
            if len(nach_level) > 1:
                andere_level.append((bedeutung, eintraege))
            unbekannt.append((sprache, bedeutung))

        print()
        print(strich)
        print("%s  –  %d Bedeutungen mit mehr als einem Wort" % (sprache, len(treffer)))
        print(strich)

        if gleiches_level:
            print("  A. Im SELBEN Level – trifft Schreiben UND Auswahl:")
            for bedeutung, gruppe in gleiches_level:
                woerter = ", ".join('%s' % bs for bs, _ in gruppe)
                print("     %s  =  %s   (%s)" % (bedeutung, woerter, gruppe[0][1]))
                gesamt += 1
        if andere_level:
            print("  B. In verschiedenen Levels – trifft nur das Schreiben:")
            for bedeutung, eintraege in andere_level:
                teile = ", ".join('%s (%s)' % (bs, label) for bs, label, _ in eintraege)
                print("     %s  =  %s" % (bedeutung, teile))
                gesamt += 1
        if vermerkte:
            print("  C. Angesehen und so gewollt – siehe bedeutung_ausnahmen.json:")
            for bedeutung, eintraege in vermerkte:
                grund, warum, _ = aus[(sprache, bedeutung)]
                teile = ", ".join('%s' % bs for bs, _, _ in eintraege)
                print("     %s  =  %s   [%s]" % (bedeutung, teile, grund))
                print("        %s" % warum)
        if not (gleiches_level or andere_level):
            print("  Nichts Offenes.")

    print()
    print(strich)
    print("%d offene Stellen, %d angesehen und begruendet." % (gesamt, geprueft))
    print()
    if unbekannt:
        print("OFFEN heisst: noch nicht angesehen. Entweder trennen - dafuer ist")
        print("bedeutungen_trennen.py da - oder in bedeutung_ausnahmen.json")
        print("eintragen, warum es so bleiben soll.")
        print()
    print("SEIT DEM 26.09.2026 FAENGT DIE APP DAS AB.")
    print("geschwister() in index.html liefert alle Woerter mit derselben")
    print("angezeigten Bedeutung. distractors() wirft sie aus dem")
    print("Ablenkertopf, und die Schreibaufgabe nimmt jede davon an.")
    print("Diese Liste ist deshalb keine Fehlerliste mehr, sondern zeigt,")
    print("wo die Uebersetzungen doppelt sind - das kann man beheben, muss")
    print("man aber nicht. Rueckgabewert bleibt 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
