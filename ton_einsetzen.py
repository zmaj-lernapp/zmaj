# -*- coding: utf-8 -*-
r"""
ton_einsetzen.py  –  setzt die ausgewählten Fassungen an die richtige Stelle

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_einsetzen.py
    ... --schreiben

Ajdin hat am 26.09.2026 die dreizehn Fassungssätze durchgehört und je eine
gewählt. Ergebnis: zehnmal gewinnt die kroatische Stimme mit Lautschrift,
einmal die schnellere bosnische, und zweimal bleibt die heutige Aufnahme.

  bez, dug, kad, kod, kroz, od, sud, zbog, crkva, prtljag   kroatisch
  Brz oporavak                                              schnell
  brz / brza, crna                                          bleiben

Die beiden Ausnahmen haben beide ein silbisches r. Für diesen Laut gibt es
in Microsofts kroatischer Lauttabelle kein Zeichen, die Umschrift war dort
geraten – und man hört es.

WAS DAS SKRIPT TUT

1. Kopiert die gewählten Fassungen aus web/audio/_probe über die
   bestehenden Dateien. Die Dateinamen bleiben, damit der Index stimmt.
2. Legt die alten Aufnahmen als *.vor_26-09 daneben, damit ein Rückweg
   bleibt.
3. Trägt die Stimme in index.json nach, sonst steht dort weiter
   bs-BA-GoranNeural, obwohl eine kroatische Stimme spricht.
4. Schreibt die Ausnahmen nach ton_ausnahmen.json. Ohne diese Datei würde
   ton_bauen.py die Aufnahmen beim nächsten vollständigen Lauf wieder mit
   der bosnischen Stimme überschreiben.

„Brz oporavak" ist kein Ersatz, sondern ein neues Wort – dort ändert sich
auch vokabeln.py. Das erledigt dieses Skript NICHT, siehe Hinweis am Ende.
"""

import io
import json
import os
import shutil
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HIER, "web", "audio")
PROBE = os.path.join(AUDIO, "_probe")
INDEX = os.path.join(AUDIO, "index.json")
AUSNAHMEN = os.path.join(HIER, "ton_ausnahmen.json")
SCHREIBEN = "--schreiben" in sys.argv

# Ajdins Wahl vom 26.09.2026, wörtlich aus der Vergleichsseite.
WAHL = {
    "bez":          "kroatisch",
    "brz / brza":   "jetzt",
    "dug":          "kroatisch",
    "kad":          "kroatisch",
    "kod":          "kroatisch",
    "kroz":         "kroatisch",
    "od":           "kroatisch",
    "sud":          "kroatisch",
    "zbog":         "kroatisch",
    "crkva":        "kroatisch",
    "crna":         "jetzt",
    "prtljag":      "kroatisch",
    "Brz oporavak": "schnell",
}

# Welche Stimme steckt hinter welcher Fassung
STIMME = {
    "kroatisch":          "hr-HR-SreckoNeural",
    "kroatisch_schlicht": "hr-HR-SreckoNeural",
    "schnell":            "bs-BA-GoranNeural",
    "sehr_schnell":       "bs-BA-GoranNeural",
    "langsam":            "bs-BA-GoranNeural",
    "betont":             "bs-BA-GoranNeural",
    "vesna":              "bs-BA-VesnaNeural",
    "vesna_schnell":      "bs-BA-VesnaNeural",
}

# Wie die Fassung erzeugt wurde - kommt in ton_ausnahmen.json, damit ein
# späterer Lauf sie genauso wiederherstellen kann.
REZEPT = {
    "kroatisch":    {"stimme": "hr-HR-SreckoNeural", "sprache": "hr-HR", "lautschrift": True},
    "schnell":      {"stimme": "bs-BA-GoranNeural",  "sprache": "bs-BA", "rate": "+20%"},
}


def dateiname(text, fassung):
    sauber = "".join(c if c.isalnum() else "_" for c in text.split(" / ")[0])
    return "%s__%s.mp3" % (sauber[:20], fassung)


def main():
    index = json.load(io.open(INDEX, encoding="utf-8"))
    nach_text = {e["text"]: e for e in index["toene"]}

    tausch, bleibt, neu, fehler = [], [], [], []
    for text, fassung in WAHL.items():
        if fassung == "jetzt":
            bleibt.append(text)
            continue
        quelle = os.path.join(PROBE, dateiname(text, fassung))
        if not os.path.exists(quelle):
            fehler.append("%s: %s fehlt" % (text, os.path.basename(quelle)))
            continue
        eintrag = nach_text.get(text)
        if eintrag is None:
            neu.append((text, fassung, quelle))       # noch keine Aufnahme
            continue
        tausch.append((text, fassung, quelle, eintrag))

    if fehler:
        print("ABBRUCH:")
        for f in fehler:
            print("   " + f)
        return 1

    strich = "=" * 64
    print(strich)
    print("Ersetzen (%d)" % len(tausch))
    print(strich)
    for text, fassung, quelle, e in tausch:
        alt = os.path.getsize(os.path.join(AUDIO, e["datei"]))
        print("   %-14s %-12s %-14s %6d -> %6d Bytes"
              % (text[:13], e["datei"], fassung, alt, os.path.getsize(quelle)))

    print()
    print(strich)
    print("Bleibt, wie es ist (%d)" % len(bleibt))
    print(strich)
    for text in bleibt:
        print("   %-14s silbisches r, die Lautschrift half nicht" % text[:13])

    if neu:
        print()
        print(strich)
        print("Noch keine Aufnahme (%d)" % len(neu))
        print(strich)
        for text, fassung, quelle in neu:
            print("   %-14s %s" % (text[:13], fassung))
            print("      Dieses Wort kommt erst mit vokabeln.py in die App.")

    if not SCHREIBEN:
        print("\n(Probelauf. Mit --schreiben wirklich einsetzen.)")
        return 0

    # ------------------------------------------------------------ schreiben
    print()
    for text, fassung, quelle, e in tausch:
        ziel = os.path.join(AUDIO, e["datei"])
        sicherung = ziel + ".vor_26-09"
        if not os.path.exists(sicherung):
            shutil.copy2(ziel, sicherung)
        shutil.copy2(quelle, ziel)
        e["stimme"] = STIMME[fassung]
        print("   ersetzt: %-12s (%s)" % (e["datei"], fassung))

    io.open(INDEX, "w", encoding="utf-8").write(
        json.dumps(index, ensure_ascii=False, indent=1))
    print("\n   index.json nachgezogen: %d Einträge tragen jetzt ihre echte Stimme"
          % len(tausch))

    # Ausnahmen festhalten, sonst überschreibt der nächste Lauf alles wieder
    liste = {}
    for text, fassung, quelle, e in tausch:
        liste[text] = dict(REZEPT[fassung], datei=e["datei"], fassung=fassung,
                           gewaehlt_am="26.09.2026")
    io.open(AUSNAHMEN, "w", encoding="utf-8").write(
        json.dumps({"ausnahmen": liste,
                    "warum": "Von Ajdin am 26.09.2026 ausgewaehlt. Ohne diese "
                             "Datei erzeugt ton_bauen.py sie wieder mit der "
                             "bosnischen Standardstimme."},
                   ensure_ascii=False, indent=1))
    print("   ton_ausnahmen.json geschrieben: %d Wörter" % len(liste))

    print()
    print("NOCH ZU TUN, von Hand:")
    print("   vokabeln.py:335  \u201eBrzo ozdravi!\u201c -> \u201eBrz oporavak\u201c")
    print("   danach inhalt_bauen.py, dann ton_bauen.py fuer die neue Aufnahme")
    print("   ton_bauen.py muss ton_ausnahmen.json lesen, sonst ist die Wahl weg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
