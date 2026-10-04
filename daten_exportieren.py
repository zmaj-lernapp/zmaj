# -*- coding: utf-8 -*-
r"""
daten_exportieren.py  –  der Lerninhalt als offener Datensatz in data/

Die App liest ihren Inhalt aus vokabeln.py, grammatik.py, geschichten.py und
uebersetzungen.py. Für jeden anderen – ein Wörterbuch, eine Anki-Sammlung,
eine Forschungsarbeit zu Bosnisch – ist Python der falsche Weg. Dieses Skript
schreibt deshalb denselben Inhalt als JSON, CSV und Anki-Tabelle nach data/,
dazu als Paralleltext (TSV je Sprachpaar, JSONL, TMX) für maschinelle
Übersetzung.

    python3 daten_exportieren.py            # data/ neu schreiben
    python3 daten_exportieren.py --pruefen  # nur prüfen, ob data/ aktuell ist

WARUM ES NICHT ABWEICHEN KANN: Wie inhalt_bauen.py ruft es inhalt.lade_daten()
auf, also dieselbe Funktion, die auch die App füttert. Die Ausgabe enthält
kein Datum und keine Zufallswerte; zweimal laufen lassen ergibt Byte für Byte
dieselben Dateien. Deshalb kann die CI mit --pruefen feststellen, ob jemand
vokabeln.py geändert und vergessen hat, data/ neu zu schreiben.

Lizenz der Ausgabe: CC BY-SA 4.0 (siehe LICENSE-CONTENT und data/DATASHEET.md).
"""
import csv
import hashlib
import io
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, "data")
AUDIO = os.path.join(HIER, "web", "audio")
sys.path.insert(0, HIER)

# Version des Datensatz-Formats. Erhöhen, wenn sich Felder ändern - nicht,
# wenn nur Wörter dazukommen.
FORMAT = "1.0"
REPO = "https://github.com/zmaj-lernapp/zmaj"
LIZENZ = "CC-BY-SA-4.0"
NENNUNG = "Zmaj – Bosnian learning content, (c) 2026 Ajdin Hasic, CC BY-SA 4.0, " + REPO


# ---------------------------------------------------------------- Tonspur ---
def ton_verzeichnis():
    """web/audio/index.json als {schlüssel: dateiname}, wie die App es lädt."""
    pfad = os.path.join(AUDIO, "index.json")
    if not os.path.exists(pfad):
        return {}
    daten = json.load(io.open(pfad, encoding="utf-8"))
    return {str(e["key"]).lower(): e["datei"] for e in daten.get("toene", [])}


def ton_datei(text, toene):
    """Dieselbe Suche wie audioDatei() in web/index.html: erst alle Formen
    ("moj / moja / moje"), dann die erste Form, dann ohne Satzzeichen."""
    klein = text.strip().lower()
    if " / " in klein and klein in toene:
        return toene[klein]
    voll = text.split(" / ")[0].strip().lower()
    kurz = voll.rstrip(".!?…").strip()
    return toene.get(voll) or toene.get(kurz)


def ton_pfad(datei):
    return "web/audio/" + datei if datei else None


# ----------------------------------------------------------------- Sammeln ---
def sammeln():
    import inhalt
    import sprachen

    codes = [s["code"] for s in sprachen.SPRACHEN]
    grund = sprachen.GRUNDSPRACHE
    alle = {c: inhalt.lade_daten(c) for c in codes}
    basis = alle[grund]
    toene = ton_verzeichnis()

    # Level und Sektionen: Bezeichnungen in allen Sprachen
    sektionen = []
    for i, s in enumerate(basis["sektionen"]):
        sektionen.append({
            "id": s["id"],
            "position": i + 1,
            "label": {c: alle[c]["sektionen"][i]["label"] for c in codes},
            "description": {c: alle[c]["sektionen"][i].get("beschreibung", "") for c in codes},
        })

    levels, woerter = [], []
    for li, kat in enumerate(basis["kategorien"]):
        levels.append({
            "id": kat["id"],
            "position": li + 1,
            "section": kat.get("sektion"),
            "label": {c: alle[c]["kategorien"][li]["label"] for c in codes},
            "tip": {c: alle[c]["kategorien"][li].get("tipp", "") for c in codes},
            "builds_on": list(kat.get("baut_auf", [])),
            "word_count": len(kat["words"]),
        })
        for wi, w in enumerate(kat["words"]):
            woerter.append({
                "id": w["id"],
                "bs": w["bs"],
                "level": kat["id"],
                "level_position": li + 1,
                "section": kat.get("sektion"),
                "translations": {c: alle[c]["kategorien"][li]["words"][wi]["de"] for c in codes},
                "audio": ton_pfad(ton_datei(w["bs"], toene)),
            })

    saetze = []
    for si, s in enumerate(basis["saetze"]):
        voll = s["text"].replace("___", s["answer"], 1)
        saetze.append({
            "id": "s%04d" % (si + 1),
            "level": s["kat"],
            "cloze": s["text"],
            "answer": s["answer"],
            "bs": voll,
            "translations": {c: alle[c]["saetze"][si]["de"] for c in codes},
            "audio": ton_pfad(ton_datei(voll, toene)),
        })

    geschichten = []
    for gi, g in enumerate(basis["geschichten"]):
        geschichten.append({
            "id": g["id"],
            "title": g["titel"],
            "level_hint": g.get("passt_zu"),
            "stage": {c: alle[c]["geschichten"][gi].get("stufe", "") for c in codes},
            "bs": g["text"],
            "translations": {c: alle[c]["geschichten"][gi]["uebersetzung"] for c in codes},
            "glossary": {c: alle[c]["geschichten"][gi].get("vokabeln", {}) for c in codes},
            "questions": {c: alle[c]["geschichten"][gi].get("fragen", []) for c in codes},
            "audio": ton_pfad(ton_datei(g["text"], toene)),
        })

    woerterbuch = []
    for bs in sorted(basis["woerterbuch"], key=lambda x: (x.lower(), x)):
        woerterbuch.append({
            "bs": bs,
            "translations": {c: alle[c]["woerterbuch"].get(bs, "") for c in codes},
        })

    grammatik = {c: alle[c]["grammatik"] for c in codes}

    return {
        "codes": codes,
        "grund": grund,
        "sektionen": sektionen,
        "levels": levels,
        "woerter": woerter,
        "saetze": saetze,
        "geschichten": geschichten,
        "woerterbuch": woerterbuch,
        "grammatik": grammatik,
        "toene": toene,
    }


# --------------------------------------------------------------- Schreiben ---
def kopf(art, codes):
    return {
        "dataset": "zmaj-bosnian",
        "kind": art,
        "format_version": FORMAT,
        "license": LIZENZ,
        "attribution": NENNUNG,
        "source": REPO,
        "target_language": "bs",
        "translation_languages": codes,
    }


def als_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + "\n"


def als_csv(zeilen, felder):
    puffer = io.StringIO()
    schreiber = csv.writer(puffer, lineterminator="\n")
    schreiber.writerow(felder)
    for z in zeilen:
        schreiber.writerow(["" if z.get(f) is None else z.get(f) for f in felder])
    return puffer.getvalue()


def anki_tsv(woerter, code):
    """Anki: Datei → Importieren. Die Kopfzeilen mit # sind Anki-Anweisungen
    (ab Anki 2.1.54) und werden nicht als Karte gelesen. Ohne Ton: Anki
    findet die mp3 nur in seinem eigenen Medienordner, und eine Karte mit
    totem Abspielknopf ist schlechter als eine ohne."""
    zeilen = [
        "#separator:tab",
        "#html:false",
        "#notetype:Basic (and reversed card)",
        "#columns:Bosnian\t%s\tTags" % code,
        "#tags column:3",
    ]
    for w in woerter:
        uebers = w["translations"][code].replace("\t", " ")
        zeilen.append("\t".join([w["bs"], uebers,
                                 "zmaj zmaj::%02d_%s" % (w["level_position"], w["level"])]))
    return "\n".join(zeilen) + "\n"


# ---------------------------------------------------------- Paralleltexte ---
# Für maschinelle Übersetzung und Low-Resource-NLP. Die JSON-Dateien oben
# sind nach Lernstoff gegliedert (Level, Lücke, Glossar); wer ein MT-Modell
# trainieren oder bewerten will, braucht dagegen nur Paare "bs ↔ Sprache".
# Deshalb dieselben Inhalte noch einmal in den drei Formaten, die MT-Werkzeuge
# ohne Umbau lesen: TSV je Sprachpaar, JSONL und TMX.

def parallel_eintraege(s):
    """Alle Paralleleinträge in fester Reihenfolge: Wörter nach Level (so
    stehen sie schon in s["woerter"]), dann Sätze, dann Geschichten.
    Die Geschichte steht als ganzer Text drin – sie ist nicht satzweise
    ausgerichtet, und eine geratene Satzzuordnung wäre schlechter als keine."""
    eintraege = []
    for art, liste in (("word", s["woerter"]), ("sentence", s["saetze"]),
                       ("story", s["geschichten"])):
        for e in liste:
            eintraege.append({"id": e["id"], "kind": art, "bs": e["bs"],
                              "translations": dict(e["translations"])})
    return eintraege


def tsv_feld(text):
    """Tabulator und Zeilenumbruch würden die Spalten verschieben. Heute
    kommen sie in Wörtern und Sätzen nicht vor; ein Test wacht darüber."""
    return " ".join(text.split()) if any(z in text for z in "\t\r\n") else text


def parallel_tsv(eintraege, code):
    """Ohne Anführungszeichen-Regeln (QUOTE_NONE): ein Feld enthält weder
    Tabulator noch Zeilenumbruch, also braucht es keine. Leere Übersetzungen
    fallen weg – ein Paar mit leerer Seite lehrt ein MT-Modell, nichts
    auszugeben. Geschichten nicht: mehrere Absätze passen nicht in eine Zeile."""
    zeilen = ["\t".join(["bs", code, "kind", "id"])]
    for e in eintraege:
        if e["kind"] == "story":
            continue
        ziel = e["translations"].get(code, "").strip()
        if not ziel or not e["bs"].strip():
            continue
        zeilen.append("\t".join([tsv_feld(e["bs"]), tsv_feld(ziel), e["kind"], e["id"]]))
    return "\n".join(zeilen) + "\n"


def parallel_jsonl(eintraege, codes):
    zeilen = []
    for e in eintraege:
        uebers = {c: e["translations"][c] for c in codes if e["translations"].get(c, "").strip()}
        zeilen.append(json.dumps({"id": e["id"], "kind": e["kind"], "bs": e["bs"],
                                  "translations": uebers}, ensure_ascii=False))
    return "\n".join(zeilen) + "\n"


def xml_text(text):
    from xml.sax.saxutils import escape
    return escape(text, {'"': "&quot;"})


def parallel_tmx(eintraege, codes):
    """TMX 1.4b. Bewusst ohne creationdate im Kopf: die Datei muss bei jedem
    Lauf Byte für Byte gleich sein, sonst schlägt --pruefen in der CI an.
    segtype je <tu>: Wörter sind "phrase", Geschichten "paragraph"."""
    segtyp = {"word": "phrase", "sentence": "sentence", "story": "paragraph"}
    zeilen = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE tmx SYSTEM "tmx14.dtd">',
        '<tmx version="1.4">',
        ' <header creationtool="zmaj daten_exportieren.py" creationtoolversion="%s"'
        ' segtype="sentence" o-tmf="zmaj-json" adminlang="en" srclang="bs"'
        ' datatype="plaintext">' % xml_text(FORMAT),
        '  <prop type="x-license">%s</prop>' % xml_text(LIZENZ),
        '  <prop type="x-attribution">%s</prop>' % xml_text(NENNUNG),
        ' </header>',
        ' <body>',
    ]
    for e in eintraege:
        zeilen.append('  <tu tuid="%s" segtype="%s">' % (xml_text(e["id"]), segtyp[e["kind"]]))
        zeilen.append('   <prop type="x-kind">%s</prop>' % e["kind"])
        zeilen.append('   <tuv xml:lang="bs"><seg>%s</seg></tuv>' % xml_text(e["bs"]))
        for c in codes:
            ziel = e["translations"].get(c, "")
            if ziel.strip():
                zeilen.append('   <tuv xml:lang="%s"><seg>%s</seg></tuv>' % (c, xml_text(ziel)))
        zeilen.append('  </tu>')
    zeilen += [' </body>', '</tmx>']
    return "\n".join(zeilen) + "\n"


def dateien_erzeugen(s):
    """Alle Dateien als {relativer Pfad: Inhalt}. Nichts wird hier geschrieben."""
    codes = s["codes"]
    aus = {}

    aus["vocabulary.json"] = als_json(dict(kopf("vocabulary", codes),
                                           sections=s["sektionen"], levels=s["levels"],
                                           entries=s["woerter"]))
    aus["sentences.json"] = als_json(dict(kopf("sentences", codes), entries=s["saetze"]))
    aus["stories.json"] = als_json(dict(kopf("stories", codes), entries=s["geschichten"]))
    aus["glossary.json"] = als_json(dict(kopf("glossary", codes), entries=s["woerterbuch"]))
    aus["grammar.json"] = als_json(dict(kopf("grammar", codes), lessons=s["grammatik"]))

    flach = []
    for w in s["woerter"]:
        z = {"id": w["id"], "level_position": w["level_position"], "level": w["level"],
             "section": w["section"], "bs": w["bs"], "audio": w["audio"]}
        z.update(w["translations"])
        flach.append(z)
    aus["vocabulary.csv"] = als_csv(
        flach, ["id", "level_position", "level", "section", "bs"] + codes + ["audio"])

    flach = []
    for t in s["saetze"]:
        z = {"id": t["id"], "level": t["level"], "bs": t["bs"], "cloze": t["cloze"],
             "answer": t["answer"], "audio": t["audio"]}
        z.update(t["translations"])
        flach.append(z)
    aus["sentences.csv"] = als_csv(
        flach, ["id", "level", "bs", "cloze", "answer"] + codes + ["audio"])

    for code in codes:
        aus["anki/zmaj-bs-%s.tsv" % code] = anki_tsv(s["woerter"], code)

    parallel = parallel_eintraege(s)
    for code in codes:
        aus["parallel/bs-%s.tsv" % code] = parallel_tsv(parallel, code)
    aus["parallel.jsonl"] = parallel_jsonl(parallel, codes)
    aus["parallel.tmx"] = parallel_tmx(parallel, codes)

    # Zuletzt das Verzeichnis: Mengen und Prüfsummen aller anderen Dateien
    mit_ton = sum(1 for w in s["woerter"] if w["audio"])
    manifest = dict(kopf("manifest", codes))
    manifest["counts"] = {
        "sections": len(s["sektionen"]),
        "levels": len(s["levels"]),
        "words": len(s["woerter"]),
        "words_with_audio": mit_ton,
        "sentences": len(s["saetze"]),
        "sentences_with_audio": sum(1 for t in s["saetze"] if t["audio"]),
        "stories": len(s["geschichten"]),
        "glossary_entries": len(s["woerterbuch"]),
        "grammar_lessons": len(s["grammatik"][s["grund"]]),
        "audio_files": len(set(s["toene"].values())),
    }
    manifest["files"] = {
        name: {"sha256": hashlib.sha256(inhalt.encode("utf-8")).hexdigest(),
               "bytes": len(inhalt.encode("utf-8"))}
        for name, inhalt in sorted(aus.items())
    }
    aus["manifest.json"] = als_json(manifest)
    return aus


# ------------------------------------------------------------------- Ablauf ---
def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    nur_pruefen = "--pruefen" in argv or "--check" in argv
    aus = dateien_erzeugen(sammeln())

    veraltet = []
    for name, inhalt in sorted(aus.items()):
        pfad = os.path.join(ZIEL, *name.split("/"))
        alt = io.open(pfad, encoding="utf-8", newline="").read() if os.path.exists(pfad) else None
        if alt == inhalt:
            continue
        veraltet.append(name)
        if not nur_pruefen:
            os.makedirs(os.path.dirname(pfad), exist_ok=True)
            io.open(pfad, "w", encoding="utf-8", newline="").write(inhalt)

    zahlen = json.loads(aus["manifest.json"])["counts"]
    print("Datensatz: %(words)d Wörter (%(words_with_audio)d mit Ton), "
          "%(sentences)d Sätze, %(stories)d Geschichten, %(glossary_entries)d "
          "Wörterbucheinträge, %(grammar_lessons)d Grammatikeinheiten" % zahlen)
    if nur_pruefen:
        if veraltet:
            print("VERALTET – bitte  python3 daten_exportieren.py  laufen lassen:")
            for name in veraltet:
                print("  data/" + name)
            return 1
        print("data/ ist aktuell.")
        return 0
    print("%d Datei(en) neu geschrieben." % len(veraltet) if veraltet else "Nichts geändert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
