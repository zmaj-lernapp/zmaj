# -*- coding: utf-8 -*-
"""
dauer_wort_setzen.py  –  legt das Wort fuer die versteckte Dauer-Vollversion fest

In Thonny oeffnen und auf Run (F5) druecken. Das Skript fragt zweimal nach
dem Wort und schreibt nur seinen Pruefwert in die private Android-Huelle
(dauer_pruefwert.txt). Das Wort selbst wird nirgends gespeichert - nicht
hier, nicht in der Huelle, nicht auf GitHub. Wer es vergisst, legt einfach
ein neues fest.

Danach neu bauen (app_bauen.py). In der App: sieben Mal auf die
Versionszeile tippen, Wort eingeben. Ein vorher eingeschalteter
Dauer-Schalter zaehlt nach dem Wechsel nicht mehr.

Warum so (11.10.2026): Das alte Wort stand im Klartext in web/index.html und
damit im oeffentlichen Repository, in seiner Geschichte und im
Zenodo-Archiv. Der Pruefwert laesst sich nicht zurueckrechnen; damit auch
Durchprobieren nichts bringt, braucht es ein langes Wort.
"""

import getpass
import hashlib
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import huelle  # noqa: E402

# Muessen zu DAUER_SALZ und DAUER_RUNDEN in web/index.html passen.
SALZ = "zmaj-dauer-2026"
RUNDEN = 300000
MINDESTLAENGE = 12


def pruefwert(wort):
    """Wie dauerWortStimmt() in web/index.html: getrimmt, klein geschrieben."""
    w = wort.strip().lower()
    return hashlib.pbkdf2_hmac("sha256", w.encode("utf-8"), SALZ.encode("utf-8"),
                               RUNDEN).hex()


def main():
    ziel = os.path.join(huelle.ordner(), "dauer_pruefwert.txt")
    print("Neues Wort fuer die Dauer-Vollversion (mindestens %d Zeichen,"
          " gern mehrere Woerter)." % MINDESTLAENGE)
    eins = getpass.getpass("Wort: ")
    zwei = getpass.getpass("Noch einmal: ")
    if eins != zwei:
        raise SystemExit("Die beiden Eingaben sind verschieden. Nichts gespeichert.")
    if len(eins.strip()) < MINDESTLAENGE:
        raise SystemExit("Zu kurz. Nichts gespeichert.")
    with open(ziel, "w", encoding="utf-8") as f:
        f.write(pruefwert(eins) + "\n")
    print("Gespeichert: %s" % ziel)
    print("Jetzt neu bauen. Das Wort steht nirgends - gut merken.")


if __name__ == "__main__":
    main()
