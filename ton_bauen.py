# -*- coding: utf-8 -*-
r"""
ton_bauen.py  –  erzeugt die Sprachaufnahmen für die App

Was es tut: Es schickt jedes bosnische Wort an einen Sprachdienst, speichert
die Antwort als MP3 in web/audio und schreibt web/audio/index.json. Die App
liest nur noch diese Datei – sie braucht dafür keinen Server.

ERST HÖREN, DANN BAUEN:

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_bauen.py --probe

Das erzeugt 30 ausgesuchte Wörter (bosnische Spezifika, ijekavische Formen,
die Laute č ć dž đ) mit allen verfügbaren Stimmen nach web/audio/_probe/.
Hör sie selbst durch – achte auf č gegen ć, dž gegen đ, die ijekavischen
Formen (mlijeko, nicht mleko) und das bosnische h (kahva, hljeb, lahko).
Erst wenn eine Stimme richtig klingt, kommt der große Lauf:

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_bauen.py --stimme bs-BA-GoranNeural

Der Lauf ist abbruchsicher und wiederholbar: Was schon in index.json steht und
als Datei vorhanden ist, wird übersprungen. Ein zweiter Aufruf kostet nichts.

ZUGANG: Lege neben diese Datei eine tts_zugang.json nach dem Muster in
tts_zugang.BEISPIEL.json. Diese Datei gehört NICHT in die App, nicht ins APK
und nicht auf GitHub – der Schlüssel wird nur hier am PC gebraucht.

WICHTIG ZUR LIZENZ: Bei Azure muss die Ressource im bezahlten Tarif S0 laufen,
nicht im kostenlosen F0. Der kostenlose Tarif trägt die Rechte zur
kommerziellen Verwendung nicht. S0 hat keine Grundgebühr; dieser Lauf kostet
ein paar Cent. Siehe LIESMICH in web/audio.
"""
import base64
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

ORDNER = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(ORDNER, "web", "audio")
INDEX = os.path.join(AUDIO, "index.json")
ZUGANG = os.path.join(ORDNER, "tts_zugang.json")

# Diese 30 Wörter entscheiden, ob die Stimme taugt. Bosnische Eigenheiten,
# ijekavische Formen und die Laute, die kroatische Stimmen zusammenwerfen.
PROBE = [
    "kahva", "hljeb", "hiljada", "tačno", "babo", "nana", "amidža", "daidža",
    "lahko", "Merhaba",
    "mlijeko", "dijete", "djeca", "lijek", "čovjek", "snijeg", "nedjelja",
    "kuća", "noć", "voće", "čaj", "čaša", "dječak", "prodavač",
    "grad", "luk", "para", "đak", "džamija", "žena",
]


# ---------------------------------------------------------------- Lerninhalt

def _modul(name):
    import importlib.util
    pfad = os.path.join(ORDNER, name + ".py")
    spec = importlib.util.spec_from_file_location(name, pfad)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def schluessel(text):
    """Genau das, wonach audioDatei() in index.html zuerst sucht:
    die erste Hälfte vor ' / ', getrimmt, kleingeschrieben – MIT Satzzeichen.
    Dadurch können 'Molim' und 'Molim?' getrennte Aufnahmen haben."""
    return text.split(" / ")[0].strip().lower()


def sprechtext(text):
    """Wie fuerStimme() in index.html: Das bosnische Alphabet kennt kein
    x, q, w, y. Die Stimme verschluckt sie, darum vorher umschreiben."""
    t = text.split(" / ")[0].strip()
    for a, b in (("x", "ks"), ("X", "Ks"), ("q", "k"), ("Q", "K"),
                 ("w", "v"), ("W", "V"), ("y", "j"), ("Y", "J")):
        t = t.replace(a, b)
    return t


_WORT_EXTRA = "'’-"


def _ist_wortzeichen(ch):
    return ch.isalpha() or unicodedata.category(ch).startswith("M") or ch in _WORT_EXTRA


def textwoerter(text):
    """Die einzelnen Wörter eines Geschichtentextes – GENAU die Stücke, die
    index.html als antippbare `.w`-Spans anzeigt.

    Dort steht:
        s.text.split(/([^\\p{L}\\p{M}'’-]+)/u)   und behalten wird, worauf
        /[\\p{L}\\p{M}]/u passt.

    Ein Wort ist also eine zusammenhängende Folge aus Buchstaben,
    kombinierenden Zeichen, Apostroph und Bindestrich, die mindestens einen
    Buchstaben enthält. Weicht das hier auch nur um ein Zeichen ab, entstehen
    Aufnahmen, die die App nie findet – deshalb Zeichen für Zeichen dasselbe.
    """
    raus, jetzt = [], []
    for ch in text:
        if _ist_wortzeichen(ch):
            jetzt.append(ch)
            continue
        if jetzt:
            s = "".join(jetzt)
            if any(c.isalpha() or unicodedata.category(c).startswith("M") for c in s):
                raus.append(s)
            jetzt = []
    if jetzt:
        s = "".join(jetzt)
        if any(c.isalpha() or unicodedata.category(c).startswith("M") for c in s):
            raus.append(s)
    return raus


def sammle():
    """Alles, was speak() in der App je zu hören bekommt, in fester
    Reihenfolge – damit die vergebenen Nummern bei jedem Lauf gleich bleiben."""
    v = _modul("vokabeln")
    g = _modul("geschichten")

    posten, gesehen = [], set()
    for kat in v.KATEGORIEN:
        for w in kat["words"]:
            k = schluessel(w["bs"])
            if k and k not in gesehen:
                gesehen.add(k)
                posten.append({"art": "wort", "key": k, "text": w["bs"]})

    gesch = getattr(g, "GESCHICHTEN", None) or getattr(g, "STORIES", None) or []
    for s in gesch:
        txt = s.get("text") if isinstance(s, dict) else None
        if not txt:
            continue
        k = schluessel(txt)
        if k not in gesehen:
            gesehen.add(k)
            posten.append({"art": "geschichte", "key": k, "text": txt})

    # Die Lückensätze, jeweils mit eingesetzter Lösung. Der Satz MIT Lücke
    # ("Dobar ___") wäre sinnlos zu sprechen – gehört wird der fertige Satz,
    # nachdem man geantwortet hat.
    for s in getattr(v, "SAETZE", []):
        ganz = s["text"].replace("___", s["answer"])
        k = schluessel(ganz)
        if k and k not in gesehen:
            gesehen.add(k)
            posten.append({"art": "wort", "key": k, "text": ganz})

    # Die einzelnen Wörter aus den Geschichten. In der Geschichte kann man
    # jedes Wort antippen; ohne eigene Aufnahme bliebe es stumm, weil die
    # App-Hülle keine Computerstimme hat.
    for s in gesch:
        txt = s.get("text") if isinstance(s, dict) else None
        if not txt:
            continue
        for wort in textwoerter(txt):
            k = schluessel(wort)
            if k and k not in gesehen:
                gesehen.add(k)
                posten.append({"art": "wort", "key": k, "text": wort})

    # Der Probesatz aus den Einstellungen, fest in index.html verdrahtet.
    k = schluessel("Dobar dan, kako si?")
    if k not in gesehen:
        posten.append({"art": "wort", "key": k, "text": "Dobar dan, kako si?"})
    return posten


# -------------------------------------------------------------- Sprachdienst

def lade_zugang():
    if not os.path.exists(ZUGANG):
        raise SystemExit(
            "tts_zugang.json fehlt.\n"
            "Kopiere tts_zugang.BEISPIEL.json nach tts_zugang.json und trage\n"
            "deinen Schlüssel ein. Die Datei bleibt auf diesem Rechner.")
    return json.load(io.open(ZUGANG, encoding="utf-8"))


# Wörter, die anders erzeugt werden müssen als alle übrigen. Ajdin hat am
# 26.09.2026 dreizehn Fassungssätze durchgehört und je eine gewählt; bei zehn
# gewann die kroatische Stimme mit Lautschrift. Grund: <phoneme> ist für die
# bosnischen Stimmen gesperrt (Fußnote 3 in Microsofts Stimmentabelle: „Phonemes,
# custom lexicon, and visemes aren't supported"), für die kroatischen nicht.
# Ohne diese Datei würde ein vollständiger Lauf die Wahl wieder überschreiben.
_AUSNAHMEN = None


def ausnahmen():
    global _AUSNAHMEN
    if _AUSNAHMEN is None:
        pfad = os.path.join(ORDNER, "ton_ausnahmen.json")
        try:
            _AUSNAHMEN = json.load(io.open(pfad, encoding="utf-8"))["ausnahmen"]
        except Exception:
            _AUSNAHMEN = {}
    return _AUSNAHMEN


# Kroatische IPA-Zeichen. Bosnisch wird phonetisch geschrieben, deshalb ist die
# Umschrift fast eins zu eins. Kein Längenzeichen heißt kurzer Vokal - genau das
# war bei bez, kad, kod, kroz, od und zbog die Beschwerde.
_IPA = [("lj", "ʎ"), ("nj", "ɲ"), ("dž", "dʒ"), ("č", "tʃ"), ("ć", "tɕ"),
        ("š", "ʃ"), ("ž", "ʒ"), ("c", "ts"), ("g", "ɡ"), ("v", "ʋ")]


def lautschrift(wort):
    s = wort.lower()
    for a, b in _IPA:
        s = s.replace(a, b)
    return s


def azure(zugang, text, stimme, langsam):
    gebiet = zugang["azure"]["region"]
    roh = _xml(text)

    sonder = ausnahmen().get(text)
    if sonder:
        sprache = sonder.get("sprache", "bs-BA")
        stimme = sonder.get("stimme", stimme)
        inhalt = roh
        if sonder.get("lautschrift"):
            inhalt = ("<phoneme alphabet='ipa' ph='%s'>%s</phoneme>"
                      % (lautschrift(text), roh))
        if sonder.get("rate"):
            inhalt = "<prosody rate='%s'>%s</prosody>" % (sonder["rate"], inhalt)
        ssml = ("<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
                "xml:lang='%s'><voice name='%s'>%s</voice></speak>"
                % (sprache, stimme, inhalt))
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

    tempo = "<prosody rate='-10%%'>%s</prosody>" % roh if langsam else roh
    ssml = ("<speak version='1.0' xml:lang='bs-BA'><voice name='%s'>%s</voice></speak>"
            % (stimme, tempo))
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


def google(zugang, text, stimme, langsam):
    sprache = "-".join(stimme.split("-")[:2])
    rumpf = json.dumps({
        "input": {"text": text},
        "voice": {"languageCode": sprache, "name": stimme},
        "audioConfig": {"audioEncoding": "MP3",
                        "speakingRate": 0.9 if langsam else 1.0},
    }).encode("utf-8")
    anfrage = urllib.request.Request(
        "https://texttospeech.googleapis.com/v1/text:synthesize?key=" + zugang["google"]["schluessel"],
        data=rumpf, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(anfrage, timeout=30) as a:
        return base64.b64decode(json.load(a)["audioContent"])


def _xml(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def hole(dienst, zugang, text, stimme, langsam):
    """Mit Wiederholung: 429 heißt 'zu schnell', dann doppelt so lange warten."""
    warte = 2
    for versuch in range(5):
        try:
            return dienst(zugang, text, stimme, langsam)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and versuch < 4:
                print("   ... %d, warte %ds" % (e.code, warte))
                time.sleep(warte)
                warte *= 2
                continue
            raise SystemExit("ABBRUCH bei '%s': HTTP %d %s\n%s"
                             % (text[:40], e.code, e.reason,
                                e.read()[:400].decode("utf-8", "replace")))
        except urllib.error.URLError as e:
            if versuch < 4:
                time.sleep(warte); warte *= 2; continue
            raise SystemExit("ABBRUCH: keine Verbindung (%s)" % e.reason)


# -------------------------------------------------------------------- Läufe

def probe(dienst, zugang, stimmen):
    ziel = os.path.join(AUDIO, "_probe")
    os.makedirs(ziel, exist_ok=True)
    print("30 Probewörter mit %d Stimme(n) nach web/audio/_probe\n" % len(stimmen))
    for stimme in stimmen:
        kurz = stimme.split("-")[-1].replace("Neural", "")
        for i, wort in enumerate(PROBE, 1):
            datei = os.path.join(ziel, "%s_%02d_%s.mp3"
                                 % (kurz, i, re.sub(r"[^a-z]", "", wort.lower()) or "x"))
            if os.path.exists(datei):
                continue
            ton = hole(dienst, zugang, sprechtext(wort), stimme, True)
            io.open(datei, "wb").write(ton)
            print("  %-14s %-12s %5d Byte" % (kurz, wort, len(ton)))
            time.sleep(0.1)
    print("\nFertig. Anhören: web\\audio\\_probe")
    print("Wenn eine Stimme überzeugt: ton_bauen.py mit  --stimme <name>  starten.")


def grosser_lauf(dienst, zugang, stimme, stimme_gesch):
    os.makedirs(AUDIO, exist_ok=True)
    alt = {"version": 1, "toene": []}
    if os.path.exists(INDEX):
        alt = json.load(io.open(INDEX, encoding="utf-8"))
    bekannt = {e["key"]: e for e in alt.get("toene", [])}

    posten = sammle()
    woerter = [p for p in posten if p["art"] == "wort"]
    print("%d Wörter, %d Geschichten, %d schon vorhanden\n"
          % (len(woerter), len(posten) - len(woerter), len(bekannt)))

    nr_w = max([int(e["datei"][1:5]) for e in bekannt.values()
                if e["datei"].startswith("w")] or [0])
    nr_g = max([int(e["datei"][1:3]) for e in bekannt.values()
                if e["datei"].startswith("g")] or [0])

    neu = fehlt = 0
    for p in posten:
        vorhanden = bekannt.get(p["key"])
        if vorhanden and os.path.exists(os.path.join(AUDIO, vorhanden["datei"])):
            continue
        if vorhanden:
            datei = vorhanden["datei"]          # Datei verschwunden, Nummer bleibt
        elif p["art"] == "wort":
            nr_w += 1; datei = "w%04d.mp3" % nr_w
        else:
            nr_g += 1; datei = "g%02d.mp3" % nr_g

        lang = p["art"] == "geschichte"
        ton = hole(dienst, zugang, sprechtext(p["text"]),
                   stimme_gesch if lang else stimme, not lang)
        if len(ton) < 800:
            print("  WARNUNG: %s ist nur %d Byte groß – vermutlich stumm"
                  % (datei, len(ton)))
            fehlt += 1
        io.open(os.path.join(AUDIO, datei), "wb").write(ton)
        bekannt[p["key"]] = {"key": p["key"], "datei": datei,
                             "text": p["text"], "stimme": stimme_gesch if lang else stimme}
        neu += 1
        if neu % 25 == 0:
            _schreibe_index(bekannt)        # Zwischenstand sichern
            print("  %4d/%d ..." % (neu, len(posten)))
        time.sleep(0.1)

    _schreibe_index(bekannt)
    gesamt = sum(os.path.getsize(os.path.join(AUDIO, e["datei"]))
                 for e in bekannt.values()
                 if os.path.exists(os.path.join(AUDIO, e["datei"])))
    print("\n%d neu erzeugt, %d Töne insgesamt, %.1f MB"
          % (neu, len(bekannt), gesamt / 1048576.0))
    if fehlt:
        print("%d Dateien sind verdächtig klein – bitte anhören." % fehlt)
    print("index.json geschrieben. Jetzt ton_pruefen.py laufen lassen.")


def _schreibe_index(bekannt):
    raus = {"version": 1,
            "toene": sorted(bekannt.values(), key=lambda e: e["datei"])}
    io.open(INDEX, "w", encoding="utf-8").write(
        json.dumps(raus, ensure_ascii=False, indent=1))


# --------------------------------------------------------------------- Start

def main():
    arg = sys.argv[1:]
    zugang = lade_zugang()
    name = zugang.get("dienst", "azure")
    dienst = {"azure": azure, "google": google}.get(name)
    if not dienst:
        raise SystemExit("Unbekannter Dienst in tts_zugang.json: %s" % name)

    if "--probe" in arg:
        stimmen = zugang.get("probestimmen") or [zugang.get("stimme")]
        return probe(dienst, zugang, [s for s in stimmen if s])

    stimme = zugang.get("stimme")
    if "--stimme" in arg:
        stimme = arg[arg.index("--stimme") + 1]
    if not stimme:
        raise SystemExit("Keine Stimme gewählt. Erst  --probe  laufen lassen,\n"
                         "dann  --stimme <name>  angeben.")
    grosser_lauf(dienst, zugang, stimme,
                 zugang.get("stimme_geschichten") or stimme)


if __name__ == "__main__":
    main()
