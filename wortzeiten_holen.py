# -*- coding: utf-8 -*-
r"""
wortzeiten_holen.py  –  Wortzeiten für die Geschichten (Feld "w" in index.json)

WOZU: Beim Vorlesen markiert die App das Wort, das gerade gesprochen wird.
Dafür steht bei jeder Geschichte in web/audio/index.json ein Feld "w": für
jedes Wort, das die App antippbar anzeigt, ein Paar [start_ms, ende_ms] in
der Aufnahme, in derselben Reihenfolge wie im Text.

WOHER: Azure meldet beim Sprechen zu jedem Wort ein WordBoundary-Ereignis
mit Startzeit, Dauer und Stelle im Text. Der REST-Aufruf in ton_bauen.py
liefert nur die MP3, ohne diese Ereignisse. Deshalb spricht dieses Skript
die Geschichte über das Speech SDK noch einmal – mit derselben Stimme und
GENAU demselben SSML wie ton_bauen.py (ssml_normal) – und ersetzt dabei die
MP3. Zeiten und Datei stammen so aus demselben Aufruf und passen sicher
zusammen; Zeiten zu einer früher erzeugten Datei gibt es nicht.
Am 20.10.2026 so für alle zwölf Geschichten gemacht, 3.805 Zeichen, rund
6 Cent. Ajdin dazu: "ja du darfst 6 cent benutzen".

ABHÄNGIGKEIT: azure-cognitiveservices-speech. Das ist keine
Standardbibliothek, deshalb wird es erst hier zur Laufzeit geladen – der Bau,
die App und die Tests brauchen es nicht (AGENTS.md: nur Standardbibliothek).
Nicht in Thonny installieren, sondern in eine eigene Umgebung außerhalb des
Projekts:

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" -m venv %TEMP%\azure_venv
    %TEMP%\azure_venv\Scripts\python.exe -m pip install azure-cognitiveservices-speech

AUFRUF (aus diesem Ordner, mit dem Python der Umgebung):

    %TEMP%\azure_venv\Scripts\python.exe wortzeiten_holen.py           zeigt nur, was fehlt
    %TEMP%\azure_venv\Scripts\python.exe wortzeiten_holen.py --holen   spricht neu - kostet Geld

--holen nimmt nur Geschichten, deren "w" fehlt oder nicht mehr passt (etwa
nachdem ton_bauen.py eine geänderte Geschichte neu erzeugt hat). --alle
nimmt alle, --nur g01.mp3,g05.mp3 nur diese. --roh ORDNER legt die rohen
Ereignisse je Geschichte als JSON dort ab (zum Nachsehen, nicht fürs Repo).
Danach: ton_pruefen.py und python -m pytest.

Den Schlüssel liest das Skript aus tts_zugang.json; er wird nie ausgegeben.
"""
import io
import json
import os
import sys
import threading
import time
import unicodedata

import ton_bauen


# Was die App zu einem Wort zählt, Zeichen für Zeichen wie in index.html:
#     s.text.split(/([^\p{L}\p{M}'’-]+)/u)   und ein Stück ist ein Wort,
#     wenn /[\p{L}\p{M}]/u darauf passt.
# Dieselbe Regel wie ton_bauen.textwoerter(), hier aber mit der Stelle im
# Text - die braucht die Zuordnung der Ereignisse.
_WORT_EXTRA = "'’-"


def _buchstabe(ch):
    return unicodedata.category(ch)[0] in "LM"


def wortbereiche(text):
    """[(anfang, ende), ...] jedes App-Worts in `text` (ende ausschließlich)."""
    raus, anfang = [], None
    for i, ch in enumerate(text):
        if _buchstabe(ch) or ch in _WORT_EXTRA:
            if anfang is None:
                anfang = i
            continue
        if anfang is not None:
            if any(_buchstabe(c) for c in text[anfang:i]):
                raus.append((anfang, i))
            anfang = None
    if anfang is not None and any(_buchstabe(c) for c in text[anfang:]):
        raus.append((anfang, len(text)))
    return raus


def sprech_abbildung(text):
    """Der Text, den ton_bauen.py wirklich an Azure schickt (sprechtext), und
    zu jedem seiner Zeichen die Stelle im Originaltext.

    Nötig, weil sprechtext() die Länge ändert: "Rex" wird "Reks" gesprochen
    (das bosnische Alphabet kennt kein x). Ohne die Abbildung rutschten in der
    ersten Geschichte ab dem ersten "Rex" alle Wörter um ein Zeichen."""
    erst = text.split(" / ")[0]
    vorne = len(erst) - len(erst.lstrip())
    ersetzt = {"x": "ks", "X": "Ks", "q": "k", "Q": "K",
               "w": "v", "W": "V", "y": "j", "Y": "J"}
    sprech, zu = [], []
    for i, ch in enumerate(erst.strip(), vorne):
        for c in ersetzt.get(ch, ch):
            sprech.append(c)
            zu.append(i)
    sprech = "".join(sprech)
    if sprech != ton_bauen.sprechtext(text):
        raise SystemExit("sprechtext() in ton_bauen.py hat sich geändert - "
                         "sprech_abbildung() hier nachziehen.")
    return sprech, zu


def ssml_abbildung(sprech, stimme):
    """Das SSML wie ton_bauen.py es schickt, die Stelle, an der der Text darin
    beginnt, und zu jedem Zeichen des maskierten Texts die Stelle im
    Sprechtext (aus "&" wird "&amp;" - heute in keiner Geschichte)."""
    ssml = ton_bauen.ssml_normal(sprech, stimme, False)
    roh, zu = [], []
    for i, ch in enumerate(sprech):
        m = ton_bauen._xml(ch)
        roh.append(m)
        zu.extend([i] * len(m))
    roh = "".join(roh)
    praefix = ssml.find(roh)
    if praefix < 0 or ssml.count(roh) != 1:
        raise SystemExit("Text im SSML nicht eindeutig gefunden.")
    return ssml, praefix, zu


def ereignisse_im_text(roh_ereignisse, text, ssml, praefix, ssml_zu, sprech_zu):
    """Wortgrenzen aus Azure -> [{"a", "b", "start", "ende", "text"}] mit
    a/b als Stelle im ORIGINALTEXT und Zeiten in Millisekunden.

    text_offset zählt laut Microsoft im SSML ("character position in the input
    text or SSML"). Stimmt der Ausschnitt dort nicht mit dem gemeldeten Wort
    überein, wird das Wort ab der letzten Stelle im SSML gesucht. Gibt auch
    zurück, wie oft das nötig war."""
    raus, gesucht, zeiger = [], 0, praefix
    for e in roh_ereignisse:
        if e.get("art", "Word") != "Word":
            continue
        pos, laenge, wort = e["pos"], e["laenge"], e.get("text") or ""
        if not (wort and ssml[pos:pos + laenge] == wort):
            gefunden = ssml.find(wort, zeiger) if wort else -1
            if gefunden < 0:
                continue
            pos, laenge, gesucht = gefunden, len(wort), gesucht + 1
        r0, r1 = pos - praefix, pos - praefix + laenge
        if r0 < 0 or r1 > len(ssml_zu) or laenge <= 0:
            continue
        zeiger = pos + laenge
        s0, s1 = ssml_zu[r0], ssml_zu[r1 - 1]
        raus.append({"a": sprech_zu[s0], "b": sprech_zu[s1] + 1,
                     "start": e["start_ms"], "ende": e["start_ms"] + e["dauer_ms"],
                     "text": text[sprech_zu[s0]:sprech_zu[s1] + 1]})
    return raus, gesucht


def zuordnen(text, ereignisse, dauer_ms=None):
    """Je App-Wort [start_ms, ende_ms] aus den Ereignissen (siehe oben).

    Ein Wort bekommt alle Ereignisse, mit denen es sich im Text überschneidet:
    start = frühester Beginn, ende = spätestes Ende. Deckt ein Ereignis
    mehrere App-Wörter ab, bekommt jedes den Teil seiner Zeit, der seinem
    Anteil an den Buchstaben entspricht (Satzzeichen im Ereignis zählen
    nicht mit). Hat ein Wort gar kein Ereignis, wird zwischen den Nachbarn
    nach Buchstaben aufgeteilt.

    Gibt (w, bericht) zurück; bericht nennt interpolierte und geteilte Wörter
    und wie viele Anfänge auf das Ende des Vorgängers geschoben wurden."""
    bereiche = wortbereiche(text)
    zeiten = [[] for _ in bereiche]
    geteilt = set()
    for e in ereignisse:
        teile = [(k, min(e["b"], wb) - max(e["a"], wa))
                 for k, (wa, wb) in enumerate(bereiche) if e["a"] < wb and e["b"] > wa]
        if not teile:
            continue
        summe, vorne = float(sum(n for _, n in teile)), 0
        dauer = e["ende"] - e["start"]
        for k, n in teile:
            zeiten[k].append((e["start"] + dauer * vorne / summe,
                              e["start"] + dauer * (vorne + n) / summe))
            vorne += n
            if len(teile) > 1:
                geteilt.add(text[bereiche[k][0]:bereiche[k][1]])
    roh = [(min(z[0] for z in zs), max(z[1] for z in zs)) if zs else None for zs in zeiten]

    # Lücken füllen: zwischen dem Ende des letzten bekannten und dem Anfang
    # des nächsten bekannten Worts, nach Buchstaben verteilt.
    interpoliert = []
    i = 0
    while i < len(roh):
        if roh[i] is not None:
            i += 1
            continue
        j = i
        while j < len(roh) and roh[j] is None:
            j += 1
        von = roh[i - 1][1] if i > 0 else 0.0
        bis = roh[j][0] if j < len(roh) else (dauer_ms if dauer_ms else von + 300.0 * (j - i))
        laengen = [bereiche[k][1] - bereiche[k][0] for k in range(i, j)]
        summe, t = float(sum(laengen)), von
        for k, n in zip(range(i, j), laengen):
            schritt = (bis - von) * n / summe
            roh[k] = (t, t + schritt)
            t += schritt
            interpoliert.append(text[bereiche[k][0]:bereiche[k][1]])
        i = j

    w, geschoben, vorher = [], 0, 0
    for a, b in roh:
        a, b = int(round(a)), int(round(b))
        if dauer_ms is not None:
            a, b = min(a, int(dauer_ms)), min(b, int(dauer_ms))
        if a < vorher:
            geschoben += 1
            a = vorher
        b = max(a, b)
        w.append([a, b])
        vorher = b
    return w, {"interpoliert": interpoliert, "geteilt": sorted(geteilt),
               "geschoben": geschoben}


def pruefe_w(w, text):
    """Fehlerliste: ein Paar je App-Wort, ganze Zahlen, monoton, start <= ende."""
    fehler = []
    n = len(wortbereiche(text))
    if len(w) != n:
        fehler.append("%d Paare statt %d" % (len(w), n))
    vorher = 0
    for i, paar in enumerate(w):
        if (not isinstance(paar, list) or len(paar) != 2
                or not all(isinstance(x, int) and not isinstance(x, bool) for x in paar)):
            fehler.append("Paar %d ist kein [int, int]: %r" % (i, paar))
            continue
        if paar[0] > paar[1]:
            fehler.append("Paar %d: start > ende" % i)
        if paar[0] < vorher:
            fehler.append("Paar %d beginnt vor dem Ende des vorigen" % i)
        vorher = paar[1]
    return fehler


# ---------------------------------------------------------------- Azure-SDK

def _sdk():
    try:
        import azure.cognitiveservices.speech as sdk
    except ImportError:
        raise SystemExit(
            "Das Azure Speech SDK fehlt. Es gehört nicht in Thonny und nicht ins\n"
            "Projekt, sondern in eine eigene Umgebung:\n\n"
            "    \"C:\\Users\\Ajdin\\AppData\\Local\\Programs\\Thonny\\python.exe\" -m venv %TEMP%\\azure_venv\n"
            "    %TEMP%\\azure_venv\\Scripts\\python.exe -m pip install azure-cognitiveservices-speech\n"
            "    %TEMP%\\azure_venv\\Scripts\\python.exe wortzeiten_holen.py --holen") from None
    return sdk


def _ms(wert):
    """duration kommt als timedelta, audio_offset in Ticks zu 100 ns."""
    if hasattr(wert, "total_seconds"):
        return wert.total_seconds() * 1000.0
    return wert / 10000.0


def sprechen(sdk, zugang, ssml):
    """Ein Aufruf: (mp3_bytes, rohe Ereignisse, Dauer in ms oder None)."""
    cfg = sdk.SpeechConfig(subscription=zugang["azure"]["schluessel"],
                           region=zugang["azure"]["region"])
    # Dasselbe Format wie ton_bauen.py (X-Microsoft-OutputFormat).
    cfg.set_speech_synthesis_output_format(
        sdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3)
    if hasattr(sdk.PropertyId, "SpeechServiceResponse_RequestWordBoundary"):
        cfg.set_property(sdk.PropertyId.SpeechServiceResponse_RequestWordBoundary, "true")
    synth = sdk.SpeechSynthesizer(speech_config=cfg, audio_config=None)   # nichts abspielen
    ereignisse, sperre = [], threading.Lock()

    def grenze(evt):
        art = str(getattr(evt, "boundary_type", "Word")).split(".")[-1]
        with sperre:
            ereignisse.append({"art": art, "start_ms": _ms(evt.audio_offset),
                               "dauer_ms": _ms(evt.duration), "pos": evt.text_offset,
                               "laenge": evt.word_length, "text": getattr(evt, "text", "")})

    synth.synthesis_word_boundary.connect(grenze)
    erg = synth.speak_ssml_async(ssml).get()
    if erg.reason != sdk.ResultReason.SynthesizingAudioCompleted:
        d = erg.cancellation_details
        meldung = "%s: %s" % (d.reason, d.error_details)
        raise RuntimeError(meldung.replace(zugang["azure"]["schluessel"], "***"))
    time.sleep(0.2)                         # letzte Ereignisse aus dem SDK-Faden
    dauer = getattr(erg, "audio_duration", None)
    dauer_ms = _ms(dauer) if dauer else None
    with sperre:
        return bytes(erg.audio_data), list(ereignisse), dauer_ms


# ------------------------------------------------------------------- Lauf

def _ziele(index, alle, nur):
    import geschichten
    nach_key = {e["key"]: e for e in index["toene"]}
    ziele = []
    for s in geschichten.GESCHICHTEN:
        text = s["text"]
        eintrag = nach_key.get(ton_bauen.schluessel(text))
        if not eintrag:
            raise SystemExit("Keine Aufnahme fuer Geschichte %r - erst ton_bauen.py." % s.get("id"))
        if nur and eintrag["datei"] not in nur:
            continue
        if alle or nur or not ton_bauen.wortzeiten_passen(eintrag, text):
            ziele.append((s, eintrag))
    return ziele


def main(argv=None):
    arg = sys.argv[1:] if argv is None else argv
    holen, alle = "--holen" in arg, "--alle" in arg
    nur = set(arg[arg.index("--nur") + 1].split(",")) if "--nur" in arg else set()
    roh_ordner = arg[arg.index("--roh") + 1] if "--roh" in arg else None

    index = json.load(io.open(ton_bauen.INDEX, encoding="utf-8"))
    ziele = _ziele(index, alle, nur)
    zeichen = sum(len(ton_bauen.sprechtext(s["text"])) for s, _ in ziele)
    for s, e in ziele:
        print("  %s  %-10s %3d Woerter, %3d Zeichen%s"
              % (e["datei"], s.get("id"), len(wortbereiche(s["text"])),
                 len(ton_bauen.sprechtext(s["text"])), "" if "w" in e else ", ohne w"))
    print("%d Geschichte(n), %d Zeichen" % (len(ziele), zeichen))
    if not ziele or not holen:
        if ziele:
            print("Nichts gesprochen. Mit --holen wird neu gesprochen (kostet Geld).")
        return 0

    zugang = ton_bauen.lade_zugang()
    stimme = zugang.get("stimme_geschichten") or zugang.get("stimme")
    for s, e in ziele:
        if ton_bauen.ausnahmen().get(ton_bauen.sprechtext(s["text"])):
            raise SystemExit("%s steht in ton_ausnahmen.json - das kann dieses Skript nicht." % e["datei"])
        if e.get("stimme") != stimme:
            raise SystemExit("%s ist von %s, tts_zugang.json sagt %s - abgebrochen, sonst "
                             "wechselte die Stimme." % (e["datei"], e.get("stimme"), stimme))
    sdk = _sdk()

    # Erst alles holen und prüfen, dann schreiben: Bricht ein Aufruf ab,
    # bleibt web/audio unverändert. Höchstens drei Wiederholungen insgesamt -
    # jeder Aufruf kostet.
    budget = len(ziele) + 3
    aufrufe, fertig = 0, []
    for s, e in ziele:
        text = s["text"]
        sprech, sprech_zu = sprech_abbildung(text)
        ssml, praefix, ssml_zu = ssml_abbildung(sprech, stimme)
        while True:
            if aufrufe >= budget:
                raise SystemExit("ABBRUCH: %d Aufrufe verbraucht, nichts geschrieben." % aufrufe)
            aufrufe += 1
            try:
                ton, roh, dauer_ms = sprechen(sdk, zugang, ssml)
            except RuntimeError as fehler:
                print("   %s: %s - noch einmal" % (e["datei"], fehler))
                time.sleep(3)
                continue
            if len(ton) >= _mindest() and roh:
                break
            print("   %s: %d Byte, %d Ereignisse - noch einmal" % (e["datei"], len(ton), len(roh)))
        ereignisse, gesucht = ereignisse_im_text(roh, text, ssml, praefix, ssml_zu, sprech_zu)
        w, bericht = zuordnen(text, ereignisse, dauer_ms)
        fehler = pruefe_w(w, text)
        if fehler:
            raise SystemExit("ABBRUCH bei %s, nichts geschrieben: %s" % (e["datei"], "; ".join(fehler)))
        print("  %s  %3d Woerter, %3d Wortgrenzen, %.1f s, %d gesucht, interpoliert: %s, "
              "geteilt: %s, geschoben: %d"
              % (e["datei"], len(w), len(ereignisse), (dauer_ms or 0) / 1000.0, gesucht,
                 ", ".join(bericht["interpoliert"]) or "-", ", ".join(bericht["geteilt"]) or "-",
                 bericht["geschoben"]))
        if roh_ordner:
            os.makedirs(roh_ordner, exist_ok=True)
            io.open(os.path.join(roh_ordner, e["datei"][:-4] + ".json"), "w", encoding="utf-8").write(
                json.dumps({"datei": e["datei"], "dauer_ms": dauer_ms, "praefix": praefix,
                            "ereignisse": roh, "w": w, "bericht": bericht},
                           ensure_ascii=False, indent=1))
        fertig.append((e, ton, w))
        time.sleep(0.2)

    for e, ton, w in fertig:
        io.open(os.path.join(ton_bauen.AUDIO, e["datei"]), "wb").write(ton)
        e["w"] = w
    ton_bauen._schreibe_index({e["key"]: e for e in index["toene"]})
    print("\n%d Aufrufe, %d Zeichen. %d MP3 ersetzt, index.json geschrieben."
          % (aufrufe, zeichen, len(fertig)))
    print("Jetzt ton_pruefen.py und python -m pytest laufen lassen.")
    return 0


def _mindest():
    """Dieselbe Grenze fuer "stumm" wie ton_pruefen.py."""
    from ton_pruefen import MINDEST
    return MINDEST


if __name__ == "__main__":
    sys.exit(main())
