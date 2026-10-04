# -*- coding: utf-8 -*-
"""Die Mermaid-Diagramme in der Dokumentation.

GitHub zeichnet sie direkt im Markdown. Zwei Dinge können still kaputtgehen:
ein Diagrammtyp, den GitHub nicht kennt (dann steht dort nur der Quelltext),
und Zahlen, die nicht mehr zum Datensatz passen."""
import io
import json
import os
import re

from test_links import markdown_dateien

ZAUN = "`" * 3
BLOCK = re.compile(ZAUN + r"mermaid\n(.*?)\n" + ZAUN, re.S)
TYPEN = ("flowchart", "graph", "sequenceDiagram", "gantt", "erDiagram",
         "stateDiagram-v2", "pie", "classDiagram", "journey", "timeline", "mindmap")


def bloecke(wurzel):
    for datei in markdown_dateien(wurzel):
        text = io.open(os.path.join(wurzel, datei), encoding="utf-8").read()
        for treffer in BLOCK.finditer(text):
            yield datei, treffer.group(1)


def test_es_gibt_diagramme(wurzel):
    assert len(list(bloecke(wurzel))) >= 10


def test_nur_bekannte_diagrammtypen(wurzel):
    schlecht = [(d, b.splitlines()[0]) for d, b in bloecke(wurzel)
                if b.strip().split()[0] not in TYPEN]
    assert not schlecht, schlecht


def test_keine_tabulatoren_und_klammern_ausgeglichen(wurzel):
    for datei, b in bloecke(wurzel):
        assert "\t" not in b, datei
        if b.startswith("erDiagram"):
            continue           # Krähenfüße wie }o--o{ sind gewollt unausgeglichen
        for auf, zu in ("[]", "{}", "()"):
            assert b.count(auf) == b.count(zu), (datei, auf, b.splitlines()[0])


def test_kuchen_woerter_je_sektion_stimmt(wurzel):
    """Das Kuchendiagramm im Datenblatt nennt die Wörter je Sektion."""
    vokabeln = json.load(io.open(os.path.join(wurzel, "data", "vocabulary.json"), encoding="utf-8"))
    soll = [sum(lv["word_count"] for lv in vokabeln["levels"] if lv["section"] == s["id"])
            for s in vokabeln["sections"]]
    kuchen = [b for d, b in bloecke(wurzel) if d == "data/DATASHEET.md" and b.startswith("pie")]
    assert kuchen, "kein Kuchendiagramm im Datenblatt"
    ist = [int(x) for x in re.findall(r":\s*(\d+)\s*$", kuchen[0], re.M)]
    assert ist == soll
    assert "(%s)" % format(sum(soll), ",") in kuchen[0].splitlines()[0]


def test_zahlen_in_den_diagrammen_passen_zum_manifest(wurzel):
    n = json.load(io.open(os.path.join(wurzel, "data", "manifest.json"), encoding="utf-8"))["counts"]
    erwartet = {"1,728": n["words"], "300": n["sentences"], "406": n["glossary_entries"],
                "2,332": n["audio_files"], "16": n["grammar_lessons"], "65": n["levels"]}
    alles = "\n".join(b for _, b in bloecke(wurzel))
    for text, wert in erwartet.items():
        if text in alles:
            assert int(text.replace(",", "")) == wert, text
