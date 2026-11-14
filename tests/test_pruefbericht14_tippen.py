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


# ---- B1 / F12: Wendungen mit einer gebraeuchlichen anderen Fassung ----
# F12 a bis i alle ja. Auch bei Trebam vodu (faelle1, Akkusativ) und auto oca
# (faelle2, Genitiv), obwohl die andere Fassung den geuebten Fall umgeht.
B1 = {
    "wo wohnst du?:Gdje stanuješ?": ["Gdje živiš?"],                          # a
    "das ist teuer:Ovo je skupo": ["To je skupo"],                            # b
    "das stimmt:To je tačno": ["Tačno je"],                                   # c
    "ich brauche wasser:Trebam vodu": ["Treba mi voda"],                      # d
    "ich brauche eine bescheinigung:Trebam potvrdu": ["Treba mi potvrda"],    # d
    "ich vermisse dich:Nedostaješ mi": ["Fališ mi"],                          # e
    "wie heißt du?:Kako se zoveš?": ["Kako ti je ime?"],                      # f
    "mach dir keine sorgen:Ne brini": ["Ne brini se"],                        # g
    "ich werde arbeiten:Radit ću": ["Ja ću raditi"],                          # h
    "das auto des vaters:auto oca": ["očev auto"],                            # i
}


def test_b1_andere_fassung_beim_tippen(alle_daten, grunddaten, index_html):
    _pruefe_woerter(alle_daten, grunddaten, index_html, B1, B1)


def test_b1_nur_diese_richtung(grunddaten):
    """„Das stimmt nicht“ (To nije tačno) war nicht gefragt und bleibt."""
    woerter = _woerter(grunddaten)
    assert woerter["das stimmt nicht:To nije tačno"].get("auch") is None


# ---- B2 / F13: andere Wortstellung ----
# F13 a und b ja. Beim Satzbau galt die Umstellung schon („Danas je hladno i kiša pada.“).
B2 = {
    "es regnet:Pada kiša": ["Kiša pada"],                     # a
    "es schneit:Pada snijeg": ["Snijeg pada"],                # a
    "es läuft aus / es tropft:Curi voda": ["Voda curi"],      # a
    "mir ist es egal:Svejedno mi je": ["Meni je svejedno"],   # b
    "mir ist langweilig:Dosadno mi je": ["Meni je dosadno"],  # b
}


def test_b2_umstellung_beim_tippen(alle_daten, grunddaten, index_html):
    _pruefe_woerter(alle_daten, grunddaten, index_html, B2, B2)


# ---- B3 / F14: Woerter, die die App selbst als gleichbedeutend fuehrt ----
# F14 a bis o alle ja, nur in der gefragten Richtung: das Wort der Aufgabe nimmt das
# andere App-Wort, in der Form, in der die App es fuehrt (savremen wie moderan mit
# weiblicher und saechlicher Form, nekad mit nekada wie beim Wort nekad).
B3 = {
    "sagen:reći": ["kazati"],                                             # a
    "sich fürchten:plašiti se": ["bojati se"],                            # b
    "falls:ukoliko": ["ako"],                                             # c
    "losgehen:poći": ["krenuti"],                                         # d
    "ehefrau:žena": ["supruga"],                                          # e
    "ehemann:muž": ["suprug"],                                            # e
    "stau:zastoj": ["gužva"],                                             # f
    "bald:uskoro": ["skoro"],                                             # g
    "hier:ovdje": ["tu"],                                                 # h
    "früher:prije": ["nekad", "nekada"],                                  # i
    "da (weil):budući da": ["pošto"],                                     # j
    "nachdem:nakon što": ["pošto"],                                       # j
    "vorbereiten:pripremiti": ["spremiti"],                               # k
    "verbinden:spojiti": ["povezati"],                                    # l
    "modern:moderan": ["moderna", "moderno", "savremen", "savremena", "savremeno"],   # m
    "richtung:pravac": ["smjer"],                                         # n
    "fehlen:nedostajati": ["faliti"],                                     # o
}
B3_NEU = dict(B3, **{"modern:moderan": ["savremen", "savremena", "savremeno"]})
# Das andere Wort selbst bekommt nichts dazu (nicht „auch umgekehrt“).
B3_GEGENSTUECK = {
    "sagen / mitteilen:kazati": None, "angst haben / sich fürchten:bojati se": None,
    "wenn / falls:ako": None, "losgehen / losfahren:krenuti": None,
    "ehefrau (förmlich):supruga": None, "ehemann (förmlich):suprug": None,
    "gedränge / stau:gužva": None, "fast / bald:skoro": None, "da / hier:tu": None,
    "manchmal / früher:nekad": ["nekada"], "da / nachdem:pošto": None,
    "vorbereiten / zubereiten:spremiti": None, "verbinden (in zusammenhang bringen):povezati": None,
    "zeitgenössisch / modern:savremen": ["savremena", "savremeno"],
    "richtung (fahrtrichtung):smjer": None, "fehlen (locker):faliti": None,
}


def test_b3_gleichbedeutende_woerter(alle_daten, grunddaten, index_html):
    _pruefe_woerter(alle_daten, grunddaten, index_html, B3, B3_NEU)


def test_b3_nur_in_der_gefragten_richtung(grunddaten):
    woerter = _woerter(grunddaten)
    for kennung, auch in B3_GEGENSTUECK.items():
        assert kennung in woerter, kennung
        assert woerter[kennung].get("auch") == auch, (kennung, woerter[kennung].get("auch"))
    # „vor (zeitlich)“ heisst auch prije, nekad passt dort nicht und war nicht gefragt.
    assert woerter["vor (zeitlich):prije"].get("auch") is None


def test_b3_partner_bleiben(grunddaten):
    """Das Aspekt-Gegenstueck bleibt, wie es war: pripremati, uplašiti se, polaziti, spajati."""
    woerter = _woerter(grunddaten)
    for kennung, partner in (("vorbereiten:pripremiti", "pripremati"), ("sich fürchten:plašiti se", "uplašiti se"),
                             ("losgehen:poći", "polaziti"), ("verbinden:spojiti", "spajati")):
        assert woerter[kennung].get("partner") == partner, kennung


# ---- B4 / F15: „Dobrodošli“ zusammengeschrieben ----
# F15 ja. Vorher erst „Fast richtig!“ (das fehlende Leerzeichen), dann „Richtig waere:
# Dobro došli“ und ein Leben weniger. Gezeigt wird weiter „Dobro došli“.
B4 = {"willkommen:Dobro došli": ["Dobrodošli"]}


def test_b4_dobrodosli_zusammen(alle_daten, grunddaten, index_html):
    _pruefe_woerter(alle_daten, grunddaten, index_html, B4, B4)
    # Ohne Haekchen ist es wie sonst "Richtig! Mit Sonderzeichen" - kein Leben.
    w = _woerter(grunddaten)["willkommen:Dobro došli"]
    assert _matches(index_html, [(_wort_antworten(w), "Dobrodosli")]) == ["almost"]


# ---- S1 / F18: Lueckensaetze mit weiteren gebraeuchlichen Antworten ----
# F18 a, b, c, d und f ja; e nein: Ajde ohne h, Ajdin: „das ist schon nicht mehr
# bosnisch“. Beim Satzbau liegen die neuen Woerter bis zu diesen Leveln nie als
# Kachel, ein "ohne" braucht es nicht.
S1 = {
    "Šta si po ___?": ("zanimanju", ["struci"], ["struci"]),                              # a
    "Možemo li platiti ___?": ("odvojeno", ["posebno"], ["posebno"]),                     # b
    "Moram sipati ___.": ("gorivo", ["benzin"], ["benzin"]),                              # c
    "Ovo je jako ___.": ("ukusno", ["fino"], ["fino"]),                                   # d
    "Poslije posla ___ večeru.": ("kuham", ["spremam", "pravim"], ["spremam", "pravim"]),  # f
}


def test_s1_weitere_antworten_im_lueckensatz(alle_daten, grunddaten, index_html):
    _pruefe_luecken(alle_daten, grunddaten, index_html, S1)


def test_s1_ajde_bleibt_falsch(grunddaten, index_html):
    """F18 e nein: „___, idemo!“ nimmt nur Hajde. Ajde ist ein Buchstabe weniger und
    bekommt wie bisher „Fast richtig!“, beim zweiten Mal ist es falsch."""
    s = _luecken(grunddaten, "___, idemo!")
    assert s["answer"] == "Hajde" and "auch" not in s, s
    assert _matches(index_html, [(_luecke_antworten(s), "Ajde")]) == ["no"]
