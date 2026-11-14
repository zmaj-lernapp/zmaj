# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026): Ajdins Antworten zum Tippen.

Ajdin hat am 14.11.2026 die Fragen F1 bis F18 aus Release\\Pruefbericht_1.4.md
beantwortet. Hier stehen nur die, die beim Tippen eine weitere richtige Antwort
bringen: je ein "auch" am Wort oder am Lueckensatz, im vorhandenen Format. Die
Kennungen bleiben (AGENTS.md, Regel 1), gesprochen wird weiter bs bzw. answer,
eine Aufnahme braucht ein "auch" nicht.

Geprueft wird zweimal: an den Daten (Kennung da, "auch" genau so, in jeder
Sprache gleich, denn Bosnisch wird nie uebersetzt) und in node mit matches()
aus web/index.html wie in tests/test_haekchen.py - die neue Antwort ist
'ok', also "Tačno!", nicht erst "Fast richtig!" und dann falsch.
"""
import json
import shutil
import subprocess

import pytest

from test_haekchen import _bloecke

NODE = r"""
const ein = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const f = new Function(ein.bloecke + '\nreturn {matches};')();
process.stdout.write(JSON.stringify(ein.faelle.map(([antworten, eingabe]) => f.matches(eingabe, antworten))));
"""


def _woerter(daten):
    return {w["id"]: w for k in daten["kategorien"] for w in k["words"]}


def _luecken(daten, text):
    s = [x for x in daten["saetze"] if x["text"] == text]
    assert len(s) == 1, (text, s)
    return s[0]


def _matches(index_html, faelle):
    """matches() aus der App fuer [(Antworten mit " / ", Eingabe)]."""
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    ein = {"bloecke": _bloecke(index_html), "faelle": faelle}
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps(ein), capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=120)
    return json.loads(aus.stdout)


def _wort_antworten(w):
    """Wie annehmbar() ohne die gleich uebersetzten Woerter: bs, auch, auch_var."""
    return " / ".join([w["bs"], *(w.get("auch") or []), *(w.get("auch_var") or [])])


def _luecke_antworten(s):
    """Wie der Lueckensatz in renderTask(): answer, auch, auch_var."""
    return " / ".join([s["answer"], *(s.get("auch") or []), *(s.get("auch_var") or [])])


def _pruefe_woerter(alle_daten, grunddaten, index_html, erwartet, neu):
    """erwartet: Kennung -> ganzes "auch"; neu: Kennung -> die neuen Antworten."""
    woerter = _woerter(grunddaten)
    for kennung, auch in erwartet.items():
        assert kennung in woerter, kennung
        assert woerter[kennung].get("auch") == auch, (kennung, woerter[kennung].get("auch"))
    for code, daten in alle_daten.items():
        andere = _woerter(daten)
        for kennung, auch in erwartet.items():
            assert andere[kennung].get("auch") == auch, (code, kennung)
    faelle = [(_wort_antworten(woerter[k]), a) for k, liste in neu.items() for a in liste]
    assert _matches(index_html, faelle) == ["ok"] * len(faelle), faelle


def _pruefe_luecken(alle_daten, grunddaten, index_html, erwartet):
    """erwartet: Text des Lueckensatzes -> (answer, ganzes "auch", die neuen Antworten)."""
    for text, (antwort, auch, _) in erwartet.items():
        for code, daten in alle_daten.items():
            s = _luecken(daten, text)
            assert (s["answer"], s.get("auch")) == (antwort, auch), (code, text, s)
    faelle = [(_luecke_antworten(_luecken(grunddaten, t)), a) for t, (_, _, neu) in erwartet.items() for a in neu]
    assert _matches(index_html, faelle) == ["ok"] * len(faelle), faelle


# ---- V8 / F1: s und sa ----
# Ajdin: "passt". Die Grammatik dieses Levels schreibt selbst „sa bratom“, „sa
# tobom“, „sa nama“, im Level praepositionen heisst „mit“ sa.
V8 = {
    "mit meiner frau:s mojom ženom": ["sa mojom ženom"],
    "mit dem bruder:s bratom": ["sa bratom"],
    "mit den kindern:s djecom": ["sa djecom"],
    "mit dir:s tobom": ["sa tobom"],
    "mit uns:s nama": ["sa nama"],
    "mit milch:s mlijekom": ["sa mlijekom"],
    "mit freundlichen grüßen:S poštovanjem": ["Sa poštovanjem"],
}


def test_v8_sa_form_beim_tippen(alle_daten, grunddaten, index_html):
    _pruefe_woerter(alle_daten, grunddaten, index_html, V8, V8)


def test_v8_kein_paar_s_sa_fuer_ueberall():
    """Nur diese sieben. Ein Paar fuer ueberall haette auch „s mnom“ erlaubt."""
    import varianten
    for p in varianten.VARIANTEN:
        assert {str(p["a"]).lower(), str(p["b"]).lower()} & {"s", "sa"} == set(), p


# ---- V9 / F2 bis F5: Lueckensaetze und Woerter mit einer zweiten gaengigen Antwort ----
# F2 bis F5 ja. Nur an diesen Eintraegen, keine Paare fuer ueberall in varianten.py:
# nicht ueberall passt das andere Wort (der Bericht nennt „volim te jako“ und „Vidimo
# se poslije“).
V9_WOERTER = {
    "sehr:jako": ["vrlo", "veoma"],                     # F2, wie vrlo / veoma „sehr (vor Eigenschaften)“
    "nach (zeitlich):poslije": ["nakon"],               # F3
    "nach der arbeit:poslije posla": ["nakon posla"],   # F3
    "nach (einem ereignis):nakon": ["poslije"],         # F3
}
V9_LUECKEN = {
    "Kahva je ___ vruća.": ("jako", ["vrlo", "veoma"], ["vrlo", "veoma", "Vrlo"]),   # F2
    "___ posla idem kući.": ("Poslije", ["Nakon"], ["Nakon", "nakon"]),             # F3
    "___ pada kiša, ostajem kod kuće.": ("Ako", ["Kad", "Kada"], ["Kad", "kada"]),   # F4
    "Kada ___ autobus?": ("polazi", ["kreće"], ["kreće"]),                          # F5
}
# Beim Satzbau liegen die anderen Woerter nicht als falsche Kachel: sie stehen bis
# zu diesem Level im Wortschatz (vrlo / veoma in kleine_woerter, kad und „Kada?“).
V9_OHNE = {
    "Kahva je jako vruća.": ["vrlo", "veoma"],
    "Ako pada kiša, ostajem kod kuće.": ["kad", "kada"],
}


def test_v9_woerter(alle_daten, grunddaten, index_html):
    _pruefe_woerter(alle_daten, grunddaten, index_html, V9_WOERTER, V9_WOERTER)


def test_v9_lueckensaetze(alle_daten, grunddaten, index_html):
    _pruefe_luecken(alle_daten, grunddaten, index_html, V9_LUECKEN)


def test_v9_satzbau_ohne(alle_daten):
    for code, daten in alle_daten.items():
        for bs, ohne in V9_OHNE.items():
            s = [x for x in daten["satzbau"] if x["bs"] == bs]
            assert len(s) == 1, (code, bs)
            # Was varianten.py dazugibt (kafa), steht dahinter.
            assert s[0]["ohne"][:len(ohne)] == ohne, (code, s[0])


def test_v9_kein_paar_fuer_ueberall():
    import varianten
    for p in varianten.VARIANTEN:
        seiten = {str(p["a"]).lower(), str(p["b"]).lower()}
        woerter = {"jako", "vrlo", "veoma", "poslije", "nakon", "ako", "kad", "kada", "polazi", "kreće"}
        assert seiten & woerter == set(), p


def test_v9_andere_stellen_bleiben(grunddaten):
    """Die Woerter vrlo / veoma, ako und kad bleiben, wie sie waren: gefragt war nur
    die Richtung zu den genannten Eintraegen."""
    woerter = {w["bs"]: w for k in grunddaten["kategorien"] for w in k["words"]}
    assert woerter["vrlo / veoma"].get("auch") is None
    assert woerter["ako"].get("auch") is None
    assert woerter["kad"].get("auch") == ["Kada?"]
