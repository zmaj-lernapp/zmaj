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

# Woerter mit mehreren Formen, bei denen die Aufnahme mit ALLEN Formen
# bewusst noch fehlt. audioDatei() in web/index.html spielt dann die erste
# Form - der Rueckfall, den es seit dem 01.10.2026 gibt. Eine neue Aufnahme
# kostet Geld (Azure), ob und wann, entscheidet Ajdin. Gilt nur fuer die
# Texte hier (Schluessel wie schluessel_alle() in ton_bauen.py), jeder andere
# fehlende Ton bleibt ein Fehler, und die erste Form muss ihre Aufnahme
# haben. Hat ton_bauen.py die Aufnahme erzeugt, meldet die Pruefung den
# Eintrag als ueberfluessig - dann hier loeschen.
#
# Leer seit dem 23.10.2026: "so / sol" (Ajdin am 22.10.2026: "die vokabel
# salz am besten zu so/sol aendern weil man es so oder so sagt") hat seine
# Aufnahme mit beiden Formen - von Emir, siehe ton_nur_emir.json.
NUR_ERSTE_FORM = set()


def _huelle_audio():
    """audio_emir/ der Huelle, wenn es den Ordner gibt, sonst None."""
    try:
        import huelle
    except ImportError:
        return None
    pfad = os.path.join(huelle.ordner(), "audio_emir")
    return pfad if os.path.isdir(pfad) else None


def nur_emir_pruefen(emir, toene, audio=None, huelle_audio=None):
    """ton_nur_emir.json (seit 23.10.2026): Aufnahmen, die es nur von Emir
    gibt. Gibt die Fehler als Liste zurueck.

    Ihre Dateien liegen nie in web/audio, nur in der Huelle unter
    audio_emir/ (ElevenLabs verbietet die Weitergabe, siehe EMIR in
    app_bauen.py). Die Nummer darf kein Eintrag in index.json tragen -
    app_bauen.emir_drueber() legte sonst das falsche Wort darueber. Der
    Schluessel folgt denselben Regeln wie in index.json.
    huelle_audio: audio_emir/ der Huelle; None heisst nicht nachsehen
    (kein Ordner da, etwa in der CI oder in einem frischen Klon)."""
    import re
    import ton_bauen
    audio = AUDIO if audio is None else audio
    fehler = []
    im_index = {e["key"] for e in toene}
    belegt = {e["datei"] for e in toene}
    gesehen = set()
    for k, e in sorted(emir.items(), key=lambda x: str(x[1].get("datei"))):
        datei, text = str(e.get("datei", "")), str(e.get("text", ""))
        if not re.fullmatch(r"w\d{4}\.mp3", datei):
            fehler.append("ton_nur_emir.json: kein Name wie w0001.mp3: %r (%s)" % (datei, k))
            continue
        if datei in gesehen or datei in belegt:
            fehler.append("ton_nur_emir.json: Nummer schon vergeben: %s (%s)" % (datei, k))
        gesehen.add(datei)
        if k in im_index:
            fehler.append("steht in index.json und in ton_nur_emir.json: %s" % k)
        soll = ton_bauen.schluessel_alle(text) if " / " in k else ton_bauen.schluessel(text)
        if k != soll:
            fehler.append("ton_nur_emir.json: Schlüssel passt nicht zum Text: %r statt %r"
                          % (k, soll))
        if os.path.exists(os.path.join(audio, datei)):
            fehler.append("%s liegt in web/audio - Emir gehört nie ins öffentliche Repo (%s)"
                          % (datei, k))
        if huelle_audio:
            pfad = os.path.join(huelle_audio, datei)
            if not os.path.isfile(pfad):
                fehler.append("Emir-Aufnahme fehlt in der Hülle: %s  (%s)" % (datei, text[:40]))
            elif os.path.getsize(pfad) < MINDEST:
                fehler.append("Emir-Aufnahme nur %d Byte, vermutlich stumm: %s"
                              % (os.path.getsize(pfad), datei))
    return fehler


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

    # 3) Jedes Wort aus dem Lerninhalt steht im Index - oder in
    #    ton_nur_emir.json (seit 23.10.2026): Aufnahmen, die es nur von Emir
    #    gibt. Die Web-Demo hat fuer sie keinen Ton, die App aus dem Store
    #    bekommt sie in app_bauen.emir_drueber(). Liegt die Huelle daneben,
    #    muss jede dieser Dateien dort in audio_emir/ stehen.
    haben = {e["key"] for e in toene}
    emir = ton_bauen.nur_emir()
    huelle_audio = _huelle_audio()
    fehler += nur_emir_pruefen(emir, toene, huelle_audio=huelle_audio)
    haben |= set(emir)
    posten = ton_bauen.sammle()
    for p in posten:
        if p["key"] in haben:
            if p.get("alle") and p["key"] in NUR_ERSTE_FORM:
                warnung.append("Aufnahme ist da, aus NUR_ERSTE_FORM loeschen: %s" % p["text"][:60])
            continue
        if (p.get("alle") and p["key"] in NUR_ERSTE_FORM
                and ton_bauen.schluessel(p["text"]) in haben):
            warnung.append("nur die erste Form klingt, Aufnahme mit allen Formen fehlt: %s"
                           % p["text"][:60])
            continue
        fehler.append("kein Ton für: %s" % p["text"][:60])
    for k in sorted(set(emir) - {p["key"] for p in posten}):
        warnung.append("in ton_nur_emir.json, aber in keinem Inhalt mehr: %s" % k)

    # 4) Keine verwaisten Dateien im Ordner
    if os.path.isdir(AUDIO):
        for f in sorted(os.listdir(AUDIO)):
            if f.lower().endswith(TONARTEN) and f not in benutzt:
                warnung.append("liegt herum, steht in keinem Index: %s" % f)

    # 5) Der Schlüssel muss wirklich das sein, wonach die App sucht
    # Aufnahmen mit allen Formen (Schluessel mit " / ") sucht die App ueber
    # den ganzen Text - siehe schluessel_alle() in ton_bauen.py.
    for e in toene:
        if " / " in e["key"]:
            soll = ton_bauen.schluessel_alle(e["text"])
        else:
            soll = ton_bauen.schluessel(e["text"])
        if e["key"] != soll:
            fehler.append("Schlüssel passt nicht zum Text: %r statt %r"
                          % (e["key"], soll))

    groesse = sum(os.path.getsize(os.path.join(AUDIO, e["datei"]))
                  for e in toene
                  if os.path.exists(os.path.join(AUDIO, e["datei"])))

    print("Töne im Index      : %d" % len(toene))
    print("Erwartet aus Inhalt: %d" % len(posten))
    if emir:
        print("Nur von Emir       : %d  (%s)" % (len(emir), "in der Hülle nachgesehen"
              if huelle_audio else "keine Hülle da, nicht nachgesehen"))
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
