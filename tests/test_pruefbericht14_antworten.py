# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026): richtige Antworten, die ein Leben kosteten.

V3: Beim Tippen nahmen vier Stellen nur eine von zwei richtigen Antworten.
kad und kada gelten als Einzelwort beide (vokabeln.py, Wann? und kad), in den
drei Fragen mit kad/kada aber nicht. Der Lueckensatz „___, kako si?“ nahm nur
Merhaba, obwohl das Wort Merhaba Zdravo im "auch" hat. „Ich habe es
geschafft!“ nennt kein Geschlecht, „Uspio sam!“ ist genauso richtig. Bei „Was
ist passiert?“ gilt wie beim Verb desiti se / dogoditi se beides. Je ein
"auch" am Eintrag; die Kennungen bleiben, Aufnahmen braucht ein "auch" nicht.
Kein Paar kad/kada in varianten.py, weil kada auch „Badewanne“ heisst.

V4 und B8: In der Auswahl stand als falscher Knopf ein Wort, das genauso richtig
ist (Molim neben „Gern geschehen“, dići neben podići, zajam neben pozajmica).
B9: „(Antwort darauf)“ als Bedeutung von Alejkumu selam verwies ins Leere.
Die Tests im Browser stehen in tests_e2e/test_pruefbericht14_antworten.py und
tests_e2e/test_antworten.py (GESPERRT).
"""
import io
import json
import os

V3_WOERTER = {
    "wann kommst du?:Kada dolaziš?": ["Kad dolaziš?"],
    "wann wirst du kommen?:Kada ćeš doći?": ["Kad ćeš doći?"],
    "wann heiratest du?:Kad se ženiš?": ["Kada se ženiš?"],
    "ich habe es geschafft!:Uspjela sam!": ["Uspio sam!"],
    "was ist passiert?:Šta se desilo?": ["Šta se dogodilo?"],
}


def _woerter(daten):
    return {w["id"]: w for k in daten["kategorien"] for w in k["words"]}


def test_v3_auch_an_den_woertern(grunddaten):
    woerter = _woerter(grunddaten)
    for kennung, auch in V3_WOERTER.items():
        # Die Kennung ist unveraendert, der Lernstand haengt daran (AGENTS.md, Regel 1).
        assert kennung in woerter, kennung
        assert woerter[kennung].get("auch") == auch, kennung


def test_v3_zdravo_im_lueckensatz(grunddaten):
    saetze = [s for s in grunddaten["saetze"] if s["text"] == "___, kako si?"]
    assert len(saetze) == 1, saetze
    s = saetze[0]
    # Gezeigt und gesprochen wird weiter der Satz mit Merhaba.
    assert s["answer"] == "Merhaba" and s["auch"] == ["Zdravo"], s
    merhaba = [w for w in _woerter(grunddaten).values() if w["bs"] == "Merhaba"]
    assert [w.get("auch") for w in merhaba] == [["Zdravo"]]


def test_v3_auch_gilt_in_jeder_sprache(alle_daten):
    """"auch" ist bosnisch und wird nie uebersetzt (AGENTS.md, Regel 2)."""
    for code, daten in alle_daten.items():
        woerter = {w["bs"]: w for k in daten["kategorien"] for w in k["words"]}
        for kennung, auch in V3_WOERTER.items():
            bs = kennung.split(":", 1)[1]
            assert woerter[bs].get("auch") == auch, (code, bs)


def test_v3_kein_paar_kad_kada_fuer_ueberall():
    import varianten
    for p in varianten.VARIANTEN:
        assert {str(p["a"]).lower(), str(p["b"]).lower()} & {"kad", "kada"} == set(), p


# V4: Bei "Was bedeutet ...?" stand als falsche Antwort ein Wort mit derselben
# Bedeutung. Molim ("Bitte", englisch "Please / you're welcome (polite)") ist die
# uebliche Antwort auf Hvala und stand neben "Gern geschehen" (Nema na čemu), in
# 43 bis 62 von 400 Ziehungen. dići / dizati sind die Kurzformen von podići /
# podizati (v111_entscheidungen.md Nr. 53) und standen daneben, auch ueber Kreuz.
# Jetzt in NIE_NEBENEINANDER; beim Tippen aendert sich nichts.
V4_PAARE = [("Molim", "Nema na čemu"), ("podići / podignuti", "dići"), ("podići / podignuti", "dizati"),
            ("podizati", "dići"), ("podizati", "dizati")]


def _nie_nebeneinander(index_html):
    import re
    block = re.search(r"const NIE_NEBENEINANDER = \[(.*?)\]\];", index_html, re.S).group(1)
    block = re.sub(r"/\*.*?\*/", "", block, flags=re.S)
    return set(re.findall(r"\['([^']+)', '([^']+)'\]", block + "]"))


def _paare_pruefen(index_html, grunddaten, paare):
    nie = _nie_nebeneinander(index_html)
    woerter = {}
    for k in grunddaten["kategorien"]:
        for w in k["words"]:
            woerter.setdefault(w["bs"], []).append((k["id"], w))
    for a, b in paare:
        assert (a, b) in nie, (a, b)
        assert len(woerter.get(a, [])) == 1 and len(woerter.get(b, [])) == 1, (a, b)
        (level_a, wa), (level_b, wb) = woerter[a][0], woerter[b][0]
        # Im selben Level, dort zieht die Auswahl ihre falschen Knoepfe.
        assert level_a == level_b, (a, level_a, b, level_b)
        # Gesperrt heisst nicht gleichwertig: kein "auch", beim Tippen zaehlt das andere nicht.
        assert b not in wa.get("auch", []) and a not in wb.get("auch", []), (a, b)


def test_v4_molim_und_heben_nie_in_derselben_auswahl(index_html, grunddaten):
    _paare_pruefen(index_html, grunddaten, V4_PAARE)


# B8: zajam und pozajmica heissen in allen Sprachen "Darlehen" (bank_darlehen),
# jaran und drug / drugarica beide "Kumpel" (kennenlernen). Sie standen als
# falscher Knopf nebeneinander, in 106 bzw. 77 von 400 Ziehungen.
B8_PAARE = [("zajam", "pozajmica"), ("jaran", "drug / drugarica")]


def test_b8_darlehen_und_kumpel_nie_in_derselben_auswahl(index_html, grunddaten):
    _paare_pruefen(index_html, grunddaten, B8_PAARE)


# B9: Alejkumu selam hiess "(Antwort darauf)", englisch "(reply to this)". Seit dem
# alphabetischen Einsortieren steht es vor Selam alejkum, der Verweis ging ins
# Leere, als Schreibaufgabe war es nicht loesbar. Die neue Bedeutung nennt den
# Gruss; die Kennung aendert sich und zieht ueber UMBENANNT mit (AGENTS.md, Regel 1).
B9_ALT, B9_NEU = "(antwort darauf):Alejkumu selam", "antwort auf selam alejkum:Alejkumu selam"
B9_BEDEUTUNG = {"de": "Antwort auf Selam alejkum", "en": "reply to Selam alejkum",
                "tr": "Selam alejkum'a verilen cevap", "sv": "svar på Selam alejkum",
                "nl": "antwoord op Selam alejkum", "nb": "svar på Selam alejkum",
                "da": "svar på Selam alejkum", "fr": "réponse à Selam alejkum"}


def test_b9_neue_kennung_und_umbenannt(grunddaten, index_html):
    woerter = _woerter(grunddaten)
    assert B9_ALT not in woerter and B9_NEU in woerter
    assert "'%s': '%s'" % (B9_ALT, B9_NEU) in index_html
    # Der Gruss, auf den die Bedeutung verweist, steht im selben Level.
    level = [k for k in grunddaten["kategorien"] if any(w["id"] == B9_NEU for w in k["words"])]
    assert len(level) == 1 and "Selam alejkum" in [w["bs"] for w in level[0]["words"]]


def test_b9_bedeutung_in_allen_sprachen(alle_daten, wurzel):
    assert set(alle_daten) == set(B9_BEDEUTUNG)
    for code, daten in alle_daten.items():
        w = [x for k in daten["kategorien"] for x in k["words"] if x["bs"] == "Alejkumu selam"]
        assert len(w) == 1 and w[0]["de"] == B9_BEDEUTUNG[code], (code, w)
        # Die Kennung haengt an der deutschen Bedeutung, in jeder Sprache dieselbe.
        assert w[0]["id"] == B9_NEU, code
    with io.open(os.path.join(wurzel, "uebersetzungen.py"), encoding="utf-8") as f:
        assert "(Antwort darauf)" not in f.read()


def test_b9_ton_bleibt(wurzel):
    """Der Ton haengt am bosnischen Wort, nicht an der Bedeutung: dieselbe Aufnahme."""
    with io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8") as f:
        toene = json.load(f)["toene"]
    assert [t["datei"] for t in toene if t["text"] == "Alejkumu selam"] == ["w1987.mp3"]
