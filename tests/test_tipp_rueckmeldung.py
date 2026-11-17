# -*- coding: utf-8 -*-
"""Nach einer falschen Eingabe die richtige Form, die dem Getippten am nächsten liegt (17.11.2026).

Ajdin beim Handytest (Offen-Liste 7): Wer bei „Vielen Dank“ „Mnogo hvla“ tippte,
las „Richtig wäre: Hvala puno“ - von seinem „Mnogo hvala“, das genauso zählt,
stand nirgends etwas. Jetzt wählt naechsteAntwort() in web/index.html die nächste
richtige Antwort, und die Lösung darunter nennt die Hauptform mit „Auch richtig:“
(task.auch_richtig). Hier: dieselbe Wahl in node auf genau den Funktionen aus
web/index.html und dem echten Inhalt, die beiden Tippstellen und der Text in allen
acht Sprachen. Den Ablauf in der App prüft tests_e2e/test_tipp_rueckmeldung.py.
"""
import json
import shutil
import subprocess

import pytest

import sprachen


def _html(index_html):
    return index_html.replace("\r\n", "\n")


def _stueck(html, anfang, ende):
    assert html.count(anfang) == 1, anfang
    a = html.index(anfang)
    return html[a:html.index(ende, a)]


def _zweig(html, typ):
    """Der Zweig von renderTask() für eine Aufgabenart."""
    a = html.index("\n  if(task.typ==='" + typ + "'){")
    return html[a:html.index("\n  if(task.typ==='", a + 1)]


def test_beide_tippstellen_zeigen_die_naechste_form(index_html):
    html = _html(index_html)
    for typ, antworten, haupt in (("type", "auchOk", "w.bs"), ("gap", "antworten", "s.answer")):
        zweig = _zweig(html, typ)
        assert ("const gezeigt = r==='ok' ? " + haupt + " : r==='almost' ? gemeinteAntwort(inp.value, " + antworten
                + ") : naechsteAntwort(inp.value, " + antworten + ", " + haupt + ");") in zweig, typ
        assert "r==='almost' ? 'task.fast' : 'task.falsch', gezeigt);" in zweig, typ
        assert ", andereForm(gezeigt, " + haupt + "));" in zweig, typ
    # Gesprochen wird weiter die Hauptform (es gibt fast nur ihre Aufnahme).
    assert "spaeterSprechen(w.bs, nachAntwort(ok), ok); done({ok});" in _zweig(html, "type")
    assert "const gesagt = lueckeText(s);" in _zweig(html, "gap")
    assert html.count("naechsteAntwort(inp.value, ") == 2 and html.count("function naechsteAntwort(") == 1
    assert html.count("t('task.auch_richtig')") == 1


def test_text_in_allen_acht_sprachen(sprachcodes):
    assert sprachcodes == ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
    assert sprachen.TEXTE["de"]["task.auch_richtig"] == "Auch richtig:"
    gesehen = set()
    for code in sprachcodes:
        text = sprachen.TEXTE[code].get("task.auch_richtig")
        assert text and text.strip() == text and text.endswith(":"), code
        assert "{" not in text, code
        assert text not in gesehen, "nicht übersetzt: " + code
        gesehen.add(text)
    # Französisch wie task.falsch: geschütztes Leerzeichen vor dem Doppelpunkt
    assert sprachen.TEXTE["fr"]["task.auch_richtig"].endswith("\xa0:")


NODE = r"""
const ein = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const f = new Function(ein.bloecke + '\nreturn {matches, naechsteAntwort};')();
process.stdout.write(JSON.stringify(ein.faelle.map(([eingabe, antworten, haupt]) =>
  [f.matches(eingabe, antworten), f.naechsteAntwort(eingabe, antworten, haupt)])));
"""


def _woerter(daten):
    for kat in daten["kategorien"]:
        yield from kat["words"]


# (Kennung oder Lückensatz, Eingabe, erwartete Lösung)
FAELLE = [
    ("vielen dank:Hvala puno", "Mnogo hvla", "Mnogo hvala"),
    ("vielen dank:Hvala puno", "mnogo hvla!", "Mnogo hvala"),
    ("vielen dank:Hvala puno", "Hvala pno", "Hvala puno"),
    ("vielen dank:Hvala puno", "Puno hvla", "Puno hvala"),
    ("vielen dank:Hvala puno", "Hvala lijeoa", "Hvala lijepa"),
    ("vielen dank:Hvala puno", "ne znam", "Hvala puno"),
    ("vielen dank:Hvala puno", "Mnogo", "Hvala puno"),
    ("vielen dank:Hvala puno", "  ", "Hvala puno"),
    ("das auto des vaters:auto oca", "očeva kla", "očeva kola"),
    ("das auto des vaters:auto oca", "ocev auti", "očev auto"),
    ("das auto des vaters:auto oca", "kola oci", "kola oca"),
    ("der hund hat mich gebissen:Pas me je ujeo", "Kuče me je ujelo", "Pas me je ujeo"),
    ("der hund hat mich gebissen:Pas me je ujeo", "Ujeo me je kuče", "Ujeo me je pas"),
    ("flasche:flaša", "bocq", "boca"),
    ("flasche:flaša", "flasq", "flaša"),
    ("Hvala ___!", "mnogp", "mnogo"),
    ("Hvala ___!", "pnuo", "puno"),
    ("Voda je u ___.", "bocii", "boci"),
    ("Moj ___ je pčelar.", "strco", "stric"),
]


@pytest.fixture(scope="module")
def node_ergebnis(index_html, grunddaten):
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    html = _html(index_html)
    bloecke = "\n".join([
        _stueck(html, "const strip = s =>", "\n/* ---------- Gesprochenes vergleichen"),
        _stueck(html, "const ZAHL_EINER = ", "\n/* ---- Zahlen, die wechseln"),
        _stueck(html, "function abstand(a, b){", "\n/* ---- Kyrillisch beim Sprechen"),
        _stueck(html, "function matches(guess, answer){", "\n/* ---------- Fast richtig: erst ein Hinweis"),
    ])
    woerter = {w["id"]: w for w in _woerter(grunddaten)}
    faelle = []
    for wer, eingabe, _ in FAELLE:
        if "___" in wer:
            s = next(x for x in grunddaten["saetze"] if x["text"] == wer)
            antworten, haupt = [s["answer"]] + (s.get("auch") or []) + (s.get("auch_var") or []), s["answer"]
        else:
            w = woerter[wer]
            antworten, haupt = [w["bs"]] + (w.get("auch") or []) + (w.get("auch_var") or []), w["bs"]
        faelle.append([eingabe, " / ".join(antworten), haupt])
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps({"bloecke": bloecke, "faelle": faelle}),
                         capture_output=True, text=True, encoding="utf-8", check=True, timeout=120)
    return json.loads(aus.stdout)


def test_naechste_form(node_ergebnis):
    falsch = [(f, e) for f, e in zip(FAELLE, node_ergebnis) if e[1] != f[2]]
    assert falsch == []


def test_was_zaehlt_bleibt(node_ergebnis):
    """Alle Fälle oben waren und bleiben falsch (oder leer) - matches() ist unverändert."""
    assert [e[0] for e in node_ergebnis] == ["no"] * 7 + ["leer"] + ["no"] * 11
