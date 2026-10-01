# -*- coding: utf-8 -*-
r"""
ton_varianten2.py  –  Fassungen zum Vergleichen für die Beanstandungen aus der
                      Prüfliste vom 01.10.2026

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_varianten2.py
    ... --erzeugen        schickt die Anfragen wirklich ab

Ajdin hat angehört:
    nju / je        "er sagt inju, es muss nju sein, und das andere Wort ist je"
    skup / skupa    "er sagt skop und nicht skup"
    drug / drugarica "er sagt dru nicht drug"

Jedes Wort gibt es zweimal in der App: einzeln (das angetippte Wort in einer
Geschichte, die erste Form) und mit allen Formen (Lektion, seit 01.10.2026).
Für beide entstehen hier je drei neue Fassungen neben der heutigen:

    kroatisch   hr-HR-SreckoNeural mit IPA-Lautschrift - hat am 26.09.2026
                bei zehn von dreizehn Beanstandungen gewonnen (dug, zbog, sud …)
    betont      bs-BA-GoranNeural mit <emphasis level='strong'>
    vesna       bs-BA-VesnaNeural, die zweite bosnische Stimme

Alles landet in web/audio/_probe/ und wird beim Verpacken übersprungen.
Was gewinnt, setzt ton_einsetzen.py (mit erweiterter WAHL) ein.
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
import ton_bauen

# (Text wie in der App, Notiz)
WOERTER = [
    ("nju / je", "er sagt inju, es muss nju sein, und das andere Wort ist je"),
    # Seit 01.10.2026 mit drei Formen, damit klar ist: teuer, nicht Treffen.
    ("skup / skupa / skupo", "er sagt skop und nicht skup"),
    ("drug / drugarica", "er sagt dru nicht drug"),
]

GORAN = "bs-BA-GoranNeural"
VESNA = "bs-BA-VesnaNeural"
SRECKO = "hr-HR-SreckoNeural"


# Ajdin zur kroatischen Fassung von skup: "das u muss länger". Die
# Lautschrift aus ton_bauen kennt keine Längen, hier steht sie von Hand.
IPA_LANG = {"skup": "skuːp", "skupa": "skuːpa", "skupo": "skuːpo"}


def ssml(fassung, gesprochen):
    teile = gesprochen.split(", ")
    if fassung == "kroatisch_lang":
        inhalt = ", ".join("<phoneme alphabet='ipa' ph='%s'>%s</phoneme>"
                           % (IPA_LANG.get(t, ton_bauen.lautschrift(t)), ton_bauen._xml(t)) for t in teile)
        return SRECKO, "hr-HR", inhalt
    if fassung == "kroatisch":
        inhalt = ", ".join("<phoneme alphabet='ipa' ph='%s'>%s</phoneme>"
                           % (ton_bauen.lautschrift(t), ton_bauen._xml(t)) for t in teile)
        return SRECKO, "hr-HR", inhalt
    roh = ton_bauen._xml(gesprochen)
    if fassung == "betont":
        return GORAN, "bs-BA", "<emphasis level='strong'>%s</emphasis>" % roh
    if fassung == "vesna":
        return VESNA, "bs-BA", "<prosody rate='-10%%'>%s</prosody>" % roh
    raise ValueError(fassung)


FASSUNGEN = ["kroatisch", "betont", "vesna"]
EXTRA = {"skup / skupa / skupo": ["kroatisch_lang"]}


def hole(zugang, fassung, gesprochen):
    import urllib.request
    stimme, sprache, inhalt = ssml(fassung, gesprochen)
    daten = ("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
             "xml:lang='%s'><voice name='%s'>%s</voice></speak>" % (sprache, stimme, inhalt))
    anfrage = urllib.request.Request(
        "https://%s.tts.speech.microsoft.com/cognitiveservices/v1" % zugang["azure"]["region"],
        data=daten.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": zugang["azure"]["schluessel"],
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
            "User-Agent": "zmaj-lernapp",
        })
    with urllib.request.urlopen(anfrage, timeout=30) as a:
        return a.read()


def dateiname(gesprochen, fassung):
    sauber = "".join(c if c.isalnum() else "_" for c in gesprochen)
    return "v2_%s__%s.mp3" % (sauber[:24], fassung)


def main():
    index = json.load(io.open(os.path.join(AUDIO, "index.json"), encoding="utf-8"))["toene"]
    nach_key = {e["key"]: e["datei"] for e in index}
    os.makedirs(ZIEL, exist_ok=True)
    zugang = ton_bauen.lade_zugang() if ERZEUGEN else None
    liste = []
    for text, notiz in WOERTER:
        for art, gesprochen, key in (
                ("einzeln", ton_bauen.sprechtext(text), ton_bauen.schluessel(text)),
                ("alle", ton_bauen.sprechtext_alle(text), ton_bauen.schluessel_alle(text))):
            eintrag = {"text": text, "art": art, "gesprochen": gesprochen, "notiz": notiz,
                       "jetzt": nach_key.get(key), "fassungen": {}}
            for f in FASSUNGEN + EXTRA.get(text, []):
                name = dateiname(gesprochen, f)
                pfad = os.path.join(ZIEL, name)
                if ERZEUGEN and not os.path.exists(pfad):
                    ton = hole(zugang, f, gesprochen)
                    io.open(pfad, "wb").write(ton)
                    print("  %-18s %-10s %6d Bytes" % (gesprochen, f, len(ton)))
                    time.sleep(0.25)
                if os.path.exists(pfad):
                    eintrag["fassungen"][f] = name
            liste.append(eintrag)
    io.open(os.path.join(ZIEL, "liste2.json"), "w", encoding="utf-8").write(
        json.dumps(liste, ensure_ascii=False, indent=1))
    print("web/audio/_probe/liste2.json: %d Einträge" % len(liste))
    if not ERZEUGEN:
        print("(Probelauf. Mit --erzeugen wirklich abrufen.)")


if __name__ == "__main__":
    main()
