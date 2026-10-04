# -*- coding: utf-8 -*-
"""Die Paralleltexte in data/ (TSV, JSONL, TMX) für maschinelle Übersetzung.

Sie werden von MT-Werkzeugen gelesen, die keine Fehler verzeihen: ein
Tabulator im Feld verschiebt eine Spalte, ein ungeschütztes & macht das TMX
unlesbar. Beides fällt beim Ansehen nicht auf, deshalb hier."""
import io
import json
import os
import xml.etree.ElementTree as ET

import pytest

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def lies(wurzel, name):
    return io.open(os.path.join(wurzel, "data", name), encoding="utf-8", newline="").read()


@pytest.fixture(scope="module")
def manifest(wurzel):
    return json.loads(lies(wurzel, "manifest.json"))


@pytest.fixture(scope="module")
def quellen(wurzel):
    return {art: json.loads(lies(wurzel, name + ".json"))["entries"]
            for art, name in (("word", "vocabulary"), ("sentence", "sentences"),
                              ("story", "stories"))}


def test_parallel_dateien_stehen_im_manifest(manifest):
    erwartet = ["parallel.jsonl", "parallel.tmx"] + \
        ["parallel/bs-%s.tsv" % c for c in manifest["translation_languages"]]
    for name in erwartet:
        assert name in manifest["files"], name


def test_tmx_ist_gueltig_und_vollstaendig(wurzel, manifest):
    wurzel_el = ET.fromstring(lies(wurzel, "parallel.tmx").encode("utf-8"))
    assert wurzel_el.tag == "tmx" and wurzel_el.get("version") == "1.4"
    kopf = wurzel_el.find("header")
    assert kopf.get("srclang") == "bs"
    for pflicht in ("creationtool", "creationtoolversion", "segtype", "o-tmf",
                    "adminlang", "datatype"):
        assert kopf.get(pflicht), pflicht

    n = manifest["counts"]
    tus = wurzel_el.findall("body/tu")
    assert len(tus) == n["words"] + n["sentences"] + n["stories"]
    erlaubt = {"bs"} | set(manifest["translation_languages"])
    for tu in tus:
        sprachen = [tuv.get(XML_LANG) for tuv in tu.findall("tuv")]
        assert sprachen[0] == "bs", tu.get("tuid")
        assert len(sprachen) >= 2 and set(sprachen) <= erlaubt, tu.get("tuid")
        assert len(sprachen) == len(set(sprachen)), tu.get("tuid")
        for tuv in tu.findall("tuv"):
            assert (tuv.findtext("seg") or "").strip(), tu.get("tuid")


def test_tmx_text_stimmt_mit_quelle(wurzel, quellen):
    """Escaping hin und zurück: was im TMX steht, ist genau der Quelltext."""
    wurzel_el = ET.fromstring(lies(wurzel, "parallel.tmx").encode("utf-8"))
    alle = [e for art in ("word", "sentence", "story") for e in quellen[art]]
    for tu, e in zip(wurzel_el.findall("body/tu"), alle):
        assert tu.get("tuid") == e["id"]
        segs = {tuv.get(XML_LANG): tuv.findtext("seg") for tuv in tu.findall("tuv")}
        assert segs["bs"] == e["bs"]
        for code, text in e["translations"].items():
            if text.strip():
                assert segs[code] == text, (e["id"], code)


def test_jsonl_zeilen_passen_zum_schema(wurzel, manifest):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(lies(wurzel, "schema/parallel.schema.json"))
    jsonschema.Draft202012Validator.check_schema(schema)
    pruefer = jsonschema.Draft202012Validator(schema)

    zeilen = lies(wurzel, "parallel.jsonl").splitlines()
    n = manifest["counts"]
    assert len(zeilen) == n["words"] + n["sentences"] + n["stories"]
    arten = {}
    schluessel = set()
    for z in zeilen:
        obj = json.loads(z)
        fehler = sorted(pruefer.iter_errors(obj), key=str)
        assert not fehler, (obj["id"], fehler[0].message)
        arten[obj["kind"]] = arten.get(obj["kind"], 0) + 1
        schluessel.add((obj["kind"], obj["id"]))
    assert arten == {"word": n["words"], "sentence": n["sentences"], "story": n["stories"]}
    assert len(schluessel) == len(zeilen), "doppelte (kind, id)"


def test_tsv_zeilen_je_sprache(wurzel, manifest, quellen):
    for code in manifest["translation_languages"]:
        zeilen = lies(wurzel, "parallel/bs-%s.tsv" % code).split("\n")
        assert zeilen[-1] == "", "Datei endet nicht mit Zeilenumbruch"
        zeilen = zeilen[:-1]
        assert zeilen[0] == "bs\t%s\tkind\tid" % code

        soll = sum(1 for art in ("word", "sentence") for e in quellen[art]
                   if e["translations"].get(code, "").strip())
        assert len(zeilen) - 1 == soll, code
        for z in zeilen[1:]:
            felder = z.split("\t")
            assert len(felder) == 4, (code, z)
            assert all(f.strip() for f in felder), (code, z)
            assert "\r" not in z, (code, z)
            assert felder[2] in ("word", "sentence"), (code, z)


def test_quelltexte_enthalten_keine_tabulatoren_oder_umbrueche(quellen):
    """tsv_feld() würde sie zu Leerzeichen machen und damit den Text ändern.
    Lieber hier auffallen, als still einen anderen Satz exportieren."""
    for art in ("word", "sentence"):
        for e in quellen[art]:
            for text in [e["bs"]] + list(e["translations"].values()):
                assert not any(z in text for z in "\t\r\n"), (art, e["id"])


def test_reihenfolge_woerter_nach_level_dann_saetze(wurzel):
    zeilen = lies(wurzel, "parallel.jsonl").splitlines()
    arten = [json.loads(z)["kind"] for z in zeilen]
    assert arten == sorted(arten, key=["word", "sentence", "story"].index)
    vokabeln = json.loads(lies(wurzel, "vocabulary.json"))["entries"]
    stufen = [e["level_position"] for e in vokabeln]
    assert stufen == sorted(stufen)


def test_zahlen_im_datenblatt_stimmen():
    """Das Datenblatt nennt die Anzahl der Paare und Zeilen von Hand. Ändert
    sich der Inhalt, muss es mitgehen."""
    import io as _io
    import json as _json
    import os as _os
    wurzel = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    blatt = _io.open(_os.path.join(wurzel, "data", "DATASHEET.md"), encoding="utf-8").read()
    n = _json.load(_io.open(_os.path.join(wurzel, "data", "manifest.json"), encoding="utf-8"))["counts"]
    paare = n["words"] + n["sentences"]
    zeilen = paare + n["stories"]
    assert format(paare, ",") in blatt, paare
    assert format(zeilen, ",") in blatt, zeilen
