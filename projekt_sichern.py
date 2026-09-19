# -*- coding: utf-8 -*-
r"""
projekt_sichern.py  –  packt den ganzen Stand in zwei Zip-Dateien

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" projekt_sichern.py

Warum ZWEI Dateien und nicht eine?

    zmaj-projekt-JJJJ-MM-TT.zip   Alles zum Wiederaufbauen. KEINE Zugangsdaten,
                                  keine Kontodaten, keine Lernstände anderer.
                                  Diese Datei darf auf einen USB-Stick, in die
                                  Cloud und später nach GitHub.

    zmaj-geheim-JJJJ-MM-TT.zip    Nur die Handvoll geheimer und persönlicher
                                  Dateien. Winzig. Die gehört auf einen Stick
                                  in die Schublade und NIRGENDWO sonst hin.

Getrennt, weil man eine Sicherung irgendwann weitergibt oder hochlädt – und
dann soll man nicht erst nachdenken müssen, was da eigentlich drin ist. Was
in der Projektdatei steckt, kann man bedenkenlos hergeben. Punkt.

Mitgesichert wird auch die Android-Hülle nebenan, aber nur ihre echten
Bestandteile: das Verzeichnis der Symbole, der Manifest, die Gradle-Dateien.
Nicht `node_modules`, nicht die Bauergebnisse, nicht `www` – das sind 220 MB,
die `npm install` und `app_bauen.py` in zwei Minuten neu herstellen.

Die Tondateien sind dagegen DRIN. Sie sehen aus wie erzeugtes Beiwerk, aber
sie neu zu erzeugen kostet Azure-Guthaben und braucht den Schlüssel. Weg
sind sie schneller als bezahlt.
"""
import io
import os
import zipfile
from datetime import date

HIER = os.path.dirname(os.path.abspath(__file__))
NEBENAN = os.path.join(os.path.dirname(HIER), "zmaj-android")
ZIEL = os.path.join(os.path.dirname(HIER), "Zmaj Sicherungen")

# ---------------------------------------------------------------- geheim ---
# Alles hier drin kommt in die zweite Datei und NIE in die erste.
# Pfade relativ zum Projektordner, Ordner mit Schrägstrich am Ende.
GEHEIM = [
    "mail_zugang.json",                 # Postfach der App
    "tts_zugang.json",                  # Azure-Sprachausgabe
    "sicherung_konten_2026-09-16/",     # Konten, Sitzungen, fremde Lernstände
    "feedback.txt",                     # was Nutzer geschrieben haben
    "codes.json",
    "sitzungen.json",
    "keystore.properties",              # Passwoerter zum Freigabeschluessel
]
# Dateien, auf die dieses Muster passt, sind ebenfalls persönlich.
# .jks und .keystore: der Freigabeschluessel von Zmaj. Er MUSS gesichert
# werden - geht er verloren, laesst sich die App nie wieder aktualisieren -
# aber eben in die zweite Datei, die den Rechner nicht verlaesst.
GEHEIM_MUSTER = ("fortschritt_", ".jks", ".keystore")

# ------------------------------------------------------------- weglassen ---
# Weder hier noch dort – lässt sich jederzeit neu herstellen.
EGAL_ORDNER = {"__pycache__", ".pytest_cache", "_probe"}
EGAL_DATEIEN = {"start.log", "desktop.ini", "thumbs.db", ".ds_store"}

# In der Android-Hülle: was NICHT mit muss
HUELLE_WEG_ORDNER = {
    "node_modules",      # npm install
    "www",               # Kopie von web/, macht app_bauen.py
    "build",             # Bauergebnis
    ".gradle", ".idea",  # Werkzeugkram
    "assets",            # nur unter app/src/main – die Kopie der Web-App
    "capture",
}
HUELLE_WEG_DATEIEN = {"local.properties"}   # zeigt auf DIESEN Rechner


def ist_geheim(rel):
    r = rel.replace("\\", "/")
    for g in GEHEIM:
        if g.endswith("/"):
            if r == g[:-1] or r.startswith(g):
                return True
        elif r == g or r.endswith("/" + g):
            return True
    return any(m in os.path.basename(r) for m in GEHEIM_MUSTER)


def ist_egal(rel):
    teile = rel.replace("\\", "/").split("/")
    if any(t in EGAL_ORDNER for t in teile[:-1]):
        return True
    return teile[-1].lower() in EGAL_DATEIEN


def sammeln(wurzel, praefix, weg_ordner=None, weg_dateien=None):
    """Alle Dateien unterhalb von `wurzel` als (vollerpfad, nameimzip)."""
    weg_ordner = weg_ordner or set()
    weg_dateien = weg_dateien or set()
    raus = []
    for ort, ordner, namen in os.walk(wurzel):
        ordner[:] = [o for o in ordner if o not in EGAL_ORDNER and o not in weg_ordner]
        for n in namen:
            if n.lower() in weg_dateien:
                continue
            voll = os.path.join(ort, n)
            rel = os.path.relpath(voll, wurzel).replace("\\", "/")
            if ist_egal(rel):
                continue
            raus.append((voll, praefix + "/" + rel))
    return raus


def packen(pfad, stuecke):
    with zipfile.ZipFile(pfad, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for voll, name in stuecke:
            z.write(voll, name)
    return os.path.getsize(pfad)


def mb(n):
    return "%.1f MB" % (n / 1048576.0)


def main():
    if not os.path.isdir(NEBENAN):
        raise SystemExit("Die Android-Huelle fehlt: %s" % NEBENAN)
    os.makedirs(ZIEL, exist_ok=True)
    heute = date.today().isoformat()

    # --- Projektordner aufteilen ---
    alles = sammeln(HIER, "Bosnisch Lernapp")
    projekt = [(v, n) for v, n in alles
               if not ist_geheim(n.split("/", 1)[1])]
    geheim = [(v, n) for v, n in alles
              if ist_geheim(n.split("/", 1)[1])]

    # Die eigenen Sicherungen nicht mitsichern
    projekt = [(v, n) for v, n in projekt if not n.startswith("Bosnisch Lernapp/Zmaj Sicherungen")]

    # --- Android-Huelle dazu ---
    huelle = sammeln(NEBENAN, "zmaj-android", HUELLE_WEG_ORDNER, HUELLE_WEG_DATEIEN)
    projekt += huelle

    print("Sicherung vom %s\n" % heute)
    print("  Projekt      %4d Dateien" % (len(projekt) - len(huelle)))
    print("  Android      %4d Dateien" % len(huelle))
    print("  geheim       %4d Dateien" % len(geheim))

    p1 = os.path.join(ZIEL, "zmaj-projekt-%s.zip" % heute)
    g1 = os.path.join(ZIEL, "zmaj-geheim-%s.zip" % heute)
    print("\nPacken ...")
    print("  %-30s %s" % (os.path.basename(p1), mb(packen(p1, projekt))))
    print("  %-30s %s" % (os.path.basename(g1), mb(packen(g1, geheim))))

    # Was in der geheimen Datei steckt, soll man nachlesen koennen, ohne sie
    # zu oeffnen - aber nur die Namen, niemals den Inhalt.
    print("\nIn der geheimen Datei:")
    for _, n in sorted(geheim):
        print("  " + n.split("/", 1)[1])

    print("\nLiegt in: %s" % ZIEL)
    print("\nzmaj-projekt-....zip darf ueberall hin.")
    print("zmaj-geheim-....zip gehoert auf einen Stick und sonst nirgendwohin.")


if __name__ == "__main__":
    main()
