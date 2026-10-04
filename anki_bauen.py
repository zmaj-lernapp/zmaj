# -*- coding: utf-8 -*-
r"""
anki_bauen.py  –  Anki-Pakete (.apkg) mit Ton, eines je Sprache

data/anki/*.tsv sind Textlisten ohne Ton: Anki findet eine mp3 nur in seinem
eigenen Medienordner. Ein .apkg bringt die Aufnahmen mit. Weil das je Sprache
rund 30 MB sind, liegen die Pakete nicht im Repository, sondern werden beim
Release gebaut und angehängt (.github/workflows/release.yml).

    python3 -m pip install genanki
    python3 anki_bauen.py              # alle Sprachen nach dist/anki/
    python3 anki_bauen.py en de        # nur diese

Jede Karte hat zwei Richtungen: Bosnisch hören und lesen → Bedeutung, und
Bedeutung → Bosnisch. Die Kennungen von Modell, Stapel und Notizen sind aus
festen Texten abgeleitet, nicht zufällig. Wer ein neueres Paket importiert,
bekommt deshalb korrigierte Karten statt doppelter, und sein Lernstand in
Anki bleibt erhalten.

Lizenz der Pakete: CC BY-SA 4.0 (Inhalt und Ton).
"""
import hashlib
import io
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
DATEN = os.path.join(HIER, "data")
ZIEL = os.path.join(HIER, "dist", "anki")

SPRACHNAME = {"de": "Deutsch", "en": "English", "tr": "Türkçe", "sv": "Svenska",
              "nl": "Nederlands", "nb": "Norsk", "da": "Dansk", "fr": "Français"}

STIL = """
.card { font-family: system-ui, sans-serif; font-size: 26px; text-align: center;
        color: #1b1f3b; background: #f6f5ff; }
.bs   { font-family: Georgia, serif; font-size: 34px; color: #2448b8; }
.hint { font-size: 14px; color: #6a6f8f; margin-top: 18px; }
.nightMode .card { color: #e8e9ff; background: #1b1f3b; }
.nightMode .bs   { color: #9fb4ff; }
"""

QUELLE = ('<div class="hint">Zmaj · CC BY-SA 4.0 · '
          '<a href="https://github.com/zmaj-lernapp/zmaj">github.com/zmaj-lernapp/zmaj</a></div>')


def feste_id(text):
    """Eine stabile Zahl im Bereich, den Anki für Kennungen erwartet."""
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16) % (1 << 30) + (1 << 30)


def modell(genanki):
    return genanki.Model(
        feste_id("zmaj-modell-v1"),
        "Zmaj Bosnian (2 directions)",
        fields=[{"name": "Bosnian"}, {"name": "Meaning"}, {"name": "Audio"}, {"name": "Level"}],
        templates=[
            {"name": "Bosnian → meaning",
             "qfmt": '<div class="bs">{{Bosnian}}</div>{{Audio}}',
             "afmt": '{{FrontSide}}<hr id="answer">{{Meaning}}<div class="hint">{{Level}}</div>' + QUELLE},
            {"name": "Meaning → Bosnian",
             "qfmt": "{{Meaning}}",
             "afmt": '{{FrontSide}}<hr id="answer"><div class="bs">{{Bosnian}}</div>{{Audio}}'
                     '<div class="hint">{{Level}}</div>' + QUELLE},
        ],
        css=STIL,
    )


def paket_bauen(code, vokabeln, genanki):
    """Baut ein Paket für eine Sprache und gibt (pfad, karten, töne) zurück."""
    levels = {lv["id"]: lv for lv in vokabeln["levels"]}
    m = modell(genanki)
    stapel = genanki.Deck(feste_id("zmaj-stapel-" + code),
                          "Zmaj – Bosnian (%s)" % SPRACHNAME.get(code, code))
    stapel.description = ("1,728 Bosnian words in 65 levels with audio, from the open course "
                          "Zmaj. CC BY-SA 4.0. https://github.com/zmaj-lernapp/zmaj")
    medien = []
    for e in vokabeln["entries"]:
        lv = levels[e["level"]]
        ton = ""
        if e["audio"]:
            pfad = os.path.join(HIER, *e["audio"].split("/"))
            if os.path.exists(pfad):
                medien.append(pfad)
                ton = "[sound:%s]" % os.path.basename(pfad)
        stufe = "Level %d · %s" % (lv["position"], lv["label"].get(code, lv["id"]))
        stapel.add_note(genanki.Note(
            model=m,
            fields=[e["bs"], e["translations"][code], ton, stufe],
            guid=genanki.guid_for("zmaj", e["id"]),
            tags=["zmaj", "zmaj::%02d_%s" % (lv["position"], lv["id"])],
        ))
    os.makedirs(ZIEL, exist_ok=True)
    pfad = os.path.join(ZIEL, "zmaj-bosnian-%s.apkg" % code)
    paket = genanki.Package(stapel)
    paket.media_files = sorted(set(medien))
    paket.write_to_file(pfad)
    return pfad, len(vokabeln["entries"]), len(set(medien))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        import genanki
    except ImportError:
        print("Bitte zuerst:  python3 -m pip install genanki")
        return 1
    vokabeln = json.load(io.open(os.path.join(DATEN, "vocabulary.json"), encoding="utf-8"))
    codes = argv or vokabeln["translation_languages"]
    for code in codes:
        if code not in vokabeln["translation_languages"]:
            print("Unbekannte Sprache: %s" % code)
            return 1
        pfad, karten, toene = paket_bauen(code, vokabeln, genanki)
        print("  %s  %d Wörter, %d Töne, %.1f MB" % (
            os.path.relpath(pfad, HIER), karten, toene, os.path.getsize(pfad) / 1048576.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
