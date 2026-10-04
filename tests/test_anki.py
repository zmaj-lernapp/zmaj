# -*- coding: utf-8 -*-
"""anki_bauen.py: ein Paket je Sprache, mit Ton, mit festen Kennungen."""
import io
import json
import os
import sqlite3
import zipfile

import pytest


@pytest.fixture(scope="module")
def paket(tmp_path_factory, wurzel):
    genanki = pytest.importorskip("genanki")
    import anki_bauen
    vokabeln = json.load(io.open(os.path.join(wurzel, "data", "vocabulary.json"), encoding="utf-8"))
    alt = anki_bauen.ZIEL
    anki_bauen.ZIEL = str(tmp_path_factory.mktemp("anki"))
    try:
        pfad, karten, toene = anki_bauen.paket_bauen("en", vokabeln, genanki)
    finally:
        anki_bauen.ZIEL = alt
    return pfad, karten, toene, vokabeln


def test_jede_vokabel_wird_eine_notiz_mit_zwei_karten(paket, tmp_path):
    pfad, karten, _, vokabeln = paket
    with zipfile.ZipFile(pfad) as z:
        z.extract("collection.anki2", str(tmp_path))
    db = sqlite3.connect(str(tmp_path / "collection.anki2"))
    assert db.execute("select count(*) from notes").fetchone()[0] == len(vokabeln["entries"]) == karten
    assert db.execute("select count(*) from cards").fetchone()[0] == 2 * karten


def test_toene_liegen_im_paket(paket):
    pfad, _, toene, vokabeln = paket
    erwartet = {os.path.basename(e["audio"]) for e in vokabeln["entries"] if e["audio"]}
    with zipfile.ZipFile(pfad) as z:
        medien = set(json.loads(z.read("media")).values())
    assert medien == erwartet and len(medien) == toene


def test_kennungen_sind_fest():
    """Zufällige Kennungen hießen: jeder Import legt alle Karten doppelt an."""
    import anki_bauen
    assert anki_bauen.feste_id("zmaj-modell-v1") == anki_bauen.feste_id("zmaj-modell-v1")
    assert anki_bauen.feste_id("zmaj-stapel-en") != anki_bauen.feste_id("zmaj-stapel-de")


def test_sprachen_haben_eigene_notiz_kennungen(tmp_path, wurzel):
    """Anki erkennt Notizen an der GUID. Teilten sich en und de dieselben,
    ueberschriebe das zweite importierte Paket das erste."""
    import sqlite3 as _sqlite3
    import zipfile as _zipfile
    genanki = pytest.importorskip("genanki")
    import anki_bauen
    vokabeln = json.load(io.open(os.path.join(wurzel, "data", "vocabulary.json"), encoding="utf-8"))
    alt = anki_bauen.ZIEL
    anki_bauen.ZIEL = str(tmp_path)
    try:
        guids = {}
        for code in ("en", "de"):
            pfad, _, _ = anki_bauen.paket_bauen(code, vokabeln, genanki)
            with _zipfile.ZipFile(pfad) as z:
                z.extract("collection.anki2", str(tmp_path / code))
            db = _sqlite3.connect(str(tmp_path / code / "collection.anki2"))
            guids[code] = {g for (g,) in db.execute("select guid from notes")}
    finally:
        anki_bauen.ZIEL = alt
    assert len(guids["en"]) == len(vokabeln["entries"])
    assert not guids["en"] & guids["de"]
