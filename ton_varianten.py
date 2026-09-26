# -*- coding: utf-8 -*-
r"""
ton_varianten.py  –  erzeugt für die beanstandeten Wörter mehrere Fassungen
                     zum Vergleichen

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_varianten.py
    ... --erzeugen        schickt die Anfragen wirklich ab

WARUM: Am 26.09.2026 hat Ajdin 45 Aufnahmen durchgehört und zwölf
beanstandet. Seine Notizen verlangen Gegenläufiges:

    bez, kad, kod, kroz, od, zbog   der Vokal wird ZU LANG gezogen
    crkva, crna                     das Wort wird ZU SCHNELL gesprochen

Eine einzige Einstellung kann nicht beides. Deshalb erzeugt dieses Skript
für jedes Wort mehrere Fassungen nach web/audio/_probe/ und eine Seite zum
Gegenhören. Was gewinnt, wird danach mit ton_einsetzen.py an die richtige
Stelle kopiert.

DIE FASSUNGEN

    schnell        rate +20 %   gegen gedehnte Vokale
    sehr_schnell   rate +35 %   wenn +20 % nicht reicht
    langsam        rate -15 %   gibt dem silbischen r Zeit
    betont         <emphasis level='strong'>, gegen verschluckte Endlaute
    vesna          die zweite Stimme, unverändert
    vesna_schnell  zweite Stimme mit rate +20 %

Die heutige Fassung steht in der Vergleichsseite als „jetzt" daneben und
wird NICHT neu abgerufen.

NICHTS WIRD ÜBERSCHRIEBEN. Alles landet in web/audio/_probe/, und dieser
Ordner wird von app_bauen.py beim Verpacken übersprungen.
"""

import io
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HIER, "web", "audio")
ZIEL = os.path.join(AUDIO, "_probe")
ERZEUGEN = "--erzeugen" in sys.argv

sys.path.insert(0, HIER)
import ton_bauen                      # wiederverwendet: lade_zugang(), _xml()


# Die zwölf Beanstandungen vom 26.09.2026, dazu die neue Vokabel.
WOERTER = [
    # (Text wie in der App, heutige Datei, was Ajdin notiert hat)
    ("bez",            "w0533.mp3", "das e wird zu lang gezogen"),
    ("brz / brza",     "w0758.mp3", "das r hört man zu wenig"),
    ("dug",            "w1009.mp3", "das g wird verschluckt"),
    ("kad",            "w0453.mp3", "das a wird zu lang gezogen"),
    ("kod",            "w0532.mp3", "das o ist zu lang"),
    ("kroz",           "w0543.mp3", "o muss kurz, nicht lang"),
    ("od",             "w0528.mp3", "das o muss kurz"),
    ("sud",            "w0984.mp3", "sagt „sub“ statt „sud“"),
    ("zbog",           "w0524.mp3", "o zu lang und g verschluckt"),
    ("crkva",          "w0854.mp3", "zu schnell, es heißt cr – Pause – kva"),
    ("crna",           "w0070.mp3", "wird zu schnell gesprochen"),
    ("prtljag",        "w0832.mp3", "das g wird verschluckt"),
    # Keine Aussprachefrage, sondern die neue Vokabel für „Gute Besserung".
    ("Brz oporavak",   None,        "neue Vokabel statt „Brzo ozdravi!“"),
]

GORAN = "bs-BA-GoranNeural"
VESNA = "bs-BA-VesnaNeural"

# name -> (Stimme, SSML-Rumpf mit %s für den Text)
FASSUNGEN = [
    ("schnell",       GORAN, "<prosody rate='+20%%'>%s</prosody>"),
    ("sehr_schnell",  GORAN, "<prosody rate='+35%%'>%s</prosody>"),
    ("langsam",       GORAN, "<prosody rate='-15%%'>%s</prosody>"),
    ("betont",        GORAN, "<emphasis level='strong'>%s</emphasis>"),
    ("vesna",         VESNA, "%s"),
    ("vesna_schnell", VESNA, "<prosody rate='+20%%'>%s</prosody>"),
]


def sprich(zugang, text, stimme, rumpf):
    """Wie azure() in ton_bauen.py, aber mit frei wählbarem SSML-Rumpf."""
    import urllib.request
    gebiet = zugang["azure"]["region"]
    inhalt = rumpf % ton_bauen._xml(text)
    ssml = ("<speak version='1.0' xml:lang='bs-BA'><voice name='%s'>%s</voice></speak>"
            % (stimme, inhalt))
    anfrage = urllib.request.Request(
        "https://%s.tts.speech.microsoft.com/cognitiveservices/v1" % gebiet,
        data=ssml.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": zugang["azure"]["schluessel"],
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "zmaj-lernapp",
        })
    with urllib.request.urlopen(anfrage, timeout=30) as a:
        return a.read()


def dateiname(text, fassung):
    sauber = "".join(c if c.isalnum() else "_" for c in text.split(" / ")[0])
    return "%s__%s.mp3" % (sauber[:20], fassung)


def main():
    if not os.path.isdir(ZIEL):
        os.makedirs(ZIEL)

    print("%d Wörter × %d Fassungen = %d Abrufe"
          % (len(WOERTER), len(FASSUNGEN), len(WOERTER) * len(FASSUNGEN)))
    print("Ziel: web/audio/_probe/  (wird beim Verpacken übersprungen)")
    if not ERZEUGEN:
        print("\n(Probelauf. Mit --erzeugen wirklich abrufen.)")
        for text, jetzt, notiz in WOERTER:
            print("   %-16s %-12s %s" % (text[:15], jetzt or "neu", notiz))
        return 0

    zugang = ton_bauen.lade_zugang()
    gebaut, uebersprungen, fehler = 0, 0, []
    for text, jetzt, notiz in WOERTER:
        print("\n%s" % text)
        for fassung, stimme, rumpf in FASSUNGEN:
            name = dateiname(text, fassung)
            pfad = os.path.join(ZIEL, name)
            if os.path.exists(pfad):
                uebersprungen += 1
                print("   %-14s schon da" % fassung)
                continue
            try:
                ton = sprich(zugang, ton_bauen.sprechtext(text), stimme, rumpf)
                io.open(pfad, "wb").write(ton)
                gebaut += 1
                print("   %-14s %6d Bytes" % (fassung, len(ton)))
                time.sleep(0.25)          # dem Dienst Luft lassen
            except Exception as e:
                fehler.append((text, fassung, str(e)[:120]))
                print("   %-14s FEHLER: %s" % (fassung, str(e)[:80]))

    print("\n%d erzeugt, %d schon vorhanden, %d Fehler"
          % (gebaut, uebersprungen, len(fehler)))
    for t, f, e in fehler:
        print("   %s / %s: %s" % (t, f, e))

    # Die Vergleichsseite braucht die Zuordnung als JSON.
    liste = []
    for text, jetzt, notiz in WOERTER:
        eintrag = {"text": text, "notiz": notiz, "jetzt": jetzt, "fassungen": {}}
        for fassung, _, _ in FASSUNGEN:
            name = dateiname(text, fassung)
            if os.path.exists(os.path.join(ZIEL, name)):
                eintrag["fassungen"][fassung] = name
        liste.append(eintrag)
    io.open(os.path.join(ZIEL, "liste.json"), "w", encoding="utf-8").write(
        json.dumps(liste, ensure_ascii=False, indent=1))
    print("\nweb/audio/_probe/liste.json geschrieben")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
