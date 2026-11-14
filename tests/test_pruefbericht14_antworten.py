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
"""

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
