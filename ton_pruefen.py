# -*- coding: utf-8 -*-
r"""
ton_pruefen.py  –  Torwächter vor dem Verpacken

Läuft in einer Sekunde und sagt dir, ob die Tonspur vollständig ist. Vor jedem
Build laufen lassen – am PC fällt ein fehlender Ton nicht auf, auf dem Handy
schon.

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_pruefen.py

Rückgabewert 0 = alles gut, 1 = etwas stimmt nicht.
"""
import io
import json
import os
import sys

ORDNER = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(ORDNER, "web", "audio")
INDEX = os.path.join(AUDIO, "index.json")
MINDEST = 800          # kleiner heißt: abgebrochen oder stumm
TONARTEN = (".mp3", ".m4a", ".wav", ".ogg", ".webm")


def main():
    import ton_bauen                       # dieselbe Sammel-Logik, keine Kopie

    fehler, warnung = [], []

    if not os.path.exists(INDEX):
        print("index.json fehlt – erst ton_bauen.py laufen lassen.")
        return 1
    index = json.load(io.open(INDEX, encoding="utf-8"))
    toene = index.get("toene", [])

    # 1) Jeder Ton im Index hat eine Datei, die groß genug ist
    benutzt = set()
    for e in toene:
        pfad = os.path.join(AUDIO, e["datei"])
        benutzt.add(e["datei"])
        if not os.path.exists(pfad):
            fehler.append("Datei fehlt: %s  (%s)" % (e["datei"], e["text"][:40]))
        elif os.path.getsize(pfad) < MINDEST:
            warnung.append("nur %d Byte, vermutlich stumm: %s  (%s)"
                           % (os.path.getsize(pfad), e["datei"], e["text"][:40]))

    # 2) Keine Nummer doppelt, alle Namen reines ASCII
    gesehen = set()
    for e in toene:
        if e["datei"] in gesehen:
            fehler.append("Dateiname doppelt vergeben: %s" % e["datei"])
        gesehen.add(e["datei"])
        try:
            e["datei"].encode("ascii")
        except UnicodeEncodeError:
            fehler.append("Dateiname nicht rein ASCII: %s" % e["datei"])

    # 3) Jedes Wort aus dem Lerninhalt steht im Index
    haben = {e["key"] for e in toene}
    posten = ton_bauen.sammle()
    for p in posten:
        if p["key"] not in haben:
            fehler.append("kein Ton für: %s" % p["text"][:60])

    # 4) Keine verwaisten Dateien im Ordner
    if os.path.isdir(AUDIO):
        for f in sorted(os.listdir(AUDIO)):
            if f.lower().endswith(TONARTEN) and f not in benutzt:
                warnung.append("liegt herum, steht in keinem Index: %s" % f)

    # 5) Der Schlüssel muss wirklich das sein, wonach die App sucht
    for e in toene:
        soll = ton_bauen.schluessel(e["text"])
        if e["key"] != soll:
            fehler.append("Schlüssel passt nicht zum Text: %r statt %r"
                          % (e["key"], soll))

    groesse = sum(os.path.getsize(os.path.join(AUDIO, e["datei"]))
                  for e in toene
                  if os.path.exists(os.path.join(AUDIO, e["datei"])))

    print("Töne im Index      : %d" % len(toene))
    print("Erwartet aus Inhalt: %d" % len(posten))
    print("Größe gesamt       : %.1f MB" % (groesse / 1048576.0))
    print()
    for w in warnung[:20]:
        print("  Warnung: %s" % w)
    if len(warnung) > 20:
        print("  ... und %d weitere Warnungen" % (len(warnung) - 20))
    for f in fehler[:30]:
        print("  FEHLER : %s" % f)
    if len(fehler) > 30:
        print("  ... und %d weitere Fehler" % (len(fehler) - 30))

    if fehler:
        print("\nNICHT verpacken. %d Fehler." % len(fehler))
        return 1
    print("\nAlles vollständig." + ("  (%d Warnungen)" % len(warnung) if warnung else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
