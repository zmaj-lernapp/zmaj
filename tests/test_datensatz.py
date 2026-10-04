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
