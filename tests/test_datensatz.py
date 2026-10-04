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
