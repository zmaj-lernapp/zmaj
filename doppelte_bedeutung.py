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
"""

import io
import json
import os
import sys
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]


def normal(s):
    """Wie matches() vergleicht: klein, ohne Rand, ohne Schlusszeichen."""
    return (s or "").strip().rstrip(".!?…").strip().lower()


def main():
    gesamt = 0
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
        for bedeutung, eintraege in sorted(treffer.items()):
            nach_level = defaultdict(list)
            for bs, label, kid in eintraege:
                nach_level[kid].append((bs, label))
            for kid, gruppe in nach_level.items():
                if len(gruppe) > 1:
                    gleiches_level.append((bedeutung, gruppe))
            if len(nach_level) > 1:
                andere_level.append((bedeutung, eintraege))

        print()
        print(strich)
        print("%s  –  %d Bedeutungen mit mehr als einem Wort" % (sprache, len(treffer)))
        print(strich)

        if gleiches_level:
            print("  A. Im SELBEN Level – trifft Schreiben UND Auswahl:")
            for bedeutung, gruppe in gleiches_level:
                woerter = ", ".join('„%s"' % bs for bs, _ in gruppe)
                print("     „%s"  =  %s   (%s)" % (bedeutung, woerter, gruppe[0][1]))
                gesamt += 1
        if andere_level:
            print("  B. In verschiedenen Levels – trifft nur das Schreiben:")
            for bedeutung, eintraege in andere_level:
                teile = ", ".join('„%s" (%s)' % (bs, label) for bs, label, _ in eintraege)
                print("     „%s"  =  %s" % (bedeutung, teile))
                gesamt += 1

    print()
    print(strich)
    print("%d Stellen insgesamt." % gesamt)
    print("A ist der schlimmere Fall: die Auswahlaufgabe ist dort nicht")
    print("entscheidbar, und eine richtige Antwort kostet ein Herz.")
    return 1 if gesamt else 0


if __name__ == "__main__":
    sys.exit(main())
