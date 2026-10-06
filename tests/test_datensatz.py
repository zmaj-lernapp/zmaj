# -*- coding: utf-8 -*-
"""data/ ist der offene Datensatz. Er muss zu den Quelldateien passen."""
import hashlib
import io
import json
import os

import pytest


def lies(wurzel, name):
    return io.open(os.path.join(wurzel, "data", name), encoding="utf-8", newline="").read()


def test_datensatz_ist_aktuell():
    import daten_exportieren
    assert daten_exportieren.main(["--pruefen"]) == 0, \
        "data/ ist veraltet: python3 daten_exportieren.py laufen lassen"


def test_manifest_pruefsummen_stimmen(wurzel):
    manifest = json.loads(lies(wurzel, "manifest.json"))
    for name, info in manifest["files"].items():
        inhalt = lies(wurzel, name).encode("utf-8")
        assert hashlib.sha256(inhalt).hexdigest() == info["sha256"], name


def test_tonpfade_im_datensatz_existieren(wurzel):
    vokabeln = json.loads(lies(wurzel, "vocabulary.json"))
    for e in vokabeln["entries"]:
        if e["audio"]:
            assert os.path.exists(os.path.join(wurzel, *e["audio"].split("/"))), e["audio"]


@pytest.mark.parametrize("name", ["vocabulary", "sentences", "stories"])
def test_json_schema(wurzel, name):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(lies(wurzel, "schema/%s.schema.json" % name))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(json.loads(lies(wurzel, name + ".json")), schema)


def test_satz_ergibt_sich_aus_luecke_und_antwort(wurzel):
    saetze = json.loads(lies(wurzel, "sentences.json"))
    for s in saetze["entries"]:
        assert s["cloze"].replace("___", s["answer"], 1) == s["bs"], s["id"]


def test_datenkarte_passt_zum_manifest(wurzel):
    """data/README.md ist die Datenkarte für Hugging Face. Ihr YAML-Kopf und
    die Zahlen im Text müssen zum Datensatz passen."""
    import re
    karte = lies(wurzel, "README.md")
    kopf = karte.split("---")[1]
    manifest = json.loads(lies(wurzel, "manifest.json"))
    n = manifest["counts"]

    assert "license: cc-by-sa-4.0" in kopf
    sprachen = set(re.findall(r"^  - ([a-z]{2})$", kopf, re.M))
    assert sprachen == {"bs"} | set(manifest["translation_languages"])
    groesse = "1K<n<10K" if 1000 <= n["words"] < 10000 else None
    assert groesse and groesse in kopf, n["words"]
    for datei in re.findall(r"data_files: (\S+)", kopf):
        assert datei in manifest["files"], datei

    for zahl, schluessel in [("1,728 words", "words"), ("300 cloze", "sentences"),
                             ("12 graded", "stories"), ("406", "glossary_entries"),
                             ("16 grammar", "grammar_lessons")]:
        assert zahl in karte, zahl
        assert int(zahl.split()[0].replace(",", "")) == n[schluessel], schluessel


def test_datensatz_wirbt_nicht_fuer_sprachsynthese(wurzel):
    """06.10.2026: Die Tonspur ist Ausgabe von Azure TTS, und Microsofts
    Bedingungen verbieten, sie zum Bauen oder Trainieren von Sprachsynthese
    zu nutzen. Datenkarte, Datenblatt und Archivangaben dürfen deshalb
    text-to-speech weder als Aufgabe noch als Zweck nennen, und überall, wo
    die Tonspur weitergeht, muss der Hinweis darauf stehen. Die Store-App
    spricht mit anderen Aufnahmen, die nie in dieses Repository gehören."""
    import re

    def text(*teile):
        return io.open(os.path.join(wurzel, *teile), encoding="utf-8").read()

    def flach(s):
        # Kommentare raus, Zeilenumbrüche weg: der Hinweis ist umbrochen.
        return " ".join(re.sub(r"<!--.*?-->", "", s, flags=re.S).split())

    karte = text("data", "README.md")
    kopf = karte.split("---")[1]
    assert not re.search(r"^\s*- text-to-speech\s*$", kopf, re.M)
    zenodo = json.loads(text(".zenodo.json"))
    assert "text-to-speech" not in zenodo["keywords"]
    assert not re.search(r"^\s*- text-to-speech\s*$", text("CITATION.cff"), re.M)
    assert not re.search(r'^keywords = .*"tts"', text("pyproject.toml"), re.M)
    blatt = text("data", "DATASHEET.md")
    zwecke = flach(blatt.split("## Intended uses")[1].split("\n## ")[0])
    assert not re.search(r"\bTTS\b|text-to-speech|speech synthesis", zwecke, re.I), zwecke

    hinweis = "must not be used to train speech synthesis"
    for name, inhalt in [("data/README.md", karte), ("data/DATASHEET.md", blatt),
                         (".zenodo.json", zenodo["description"]),
                         ("README.md", text("README.md")),
                         ("paket/README.md", text("paket", "README.md"))]:
        assert hinweis in flach(inhalt), name
