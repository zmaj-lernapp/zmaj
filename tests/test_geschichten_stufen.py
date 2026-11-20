# -*- coding: utf-8 -*-
"""Die Geschichten nach Stufen (17.11.2026, Offen-Liste 7).

Ajdin: "lass sie auch in 1.4 rein machen das da steht amtssprache lass raus es soll
einfach von kinderleicht zu schwerer sein usw also nur A1, A2 usw". Jede Geschichte hat
die Stufe A1, A2, B1 oder B2 wie die Reiter im Lernpfad, und die Liste steht Stufe fuer
Stufe, in jeder von leicht nach schwer (REIHENFOLGE in geschichten.py; Einstufung vom
17.11.2026, Ajdin: "passt so"). Die Themen von vorher ("Kinderbuch", "Einfach",
"Mittel", "Fortgeschritten", "Amtssprache") sind weg, auch aus den Uebersetzungen.

Frei bleibt, was vorher frei war: storyUnlocked() in web/index.html kennt die Folge bis
zum 17.11.2026 (GESCH_ALTE_FOLGE). Im Browser: tests_e2e/test_geschichten_stufen.py.
"""
import copy
import io
import json
import os
import re

# Die Folge bis zum 17.11.2026 (sammeln-v112, 861eb73). Bis 1.3 gab es nur die ersten
# zwoelf, in derselben Folge. Nach ihr sind auch die Aufnahmen numeriert (g01 bis g32).
ALTE_FOLGE = [
    "mira", "kuca1", "porodica", "pijaca", "dan", "grad", "jucer", "put", "pismo", "opcina",
    "kuca", "intervju", "b1_ljeto", "b1_dijaspora", "b1_vrijeme", "b1_voz", "b1_rafting",
    "b1_jahorina", "b1_pita", "b1_struja", "b1_svadba", "b1_posao", "b1_stan", "b1_doktor",
    "b1_selidba", "b1_telefon", "b1_rodjendan", "b1_utakmica", "b1_zanat", "b1_kahva",
    "b1_mejl", "b1_zmaj",
]

# Die neue Folge, wie abgenommen
NEU = [
    ("A1", ["mira", "porodica", "kuca1", "pijaca", "dan"]),
    ("A2", ["opcina", "jucer", "grad", "kuca", "put", "pismo"]),
    ("B1", ["b1_vrijeme", "b1_voz", "b1_stan", "b1_ljeto", "b1_svadba", "b1_rafting",
            "b1_rodjendan", "b1_doktor", "b1_posao", "b1_jahorina", "b1_utakmica",
            "b1_struja", "b1_zmaj", "b1_pita", "b1_kahva", "b1_dijaspora", "b1_telefon",
            "b1_selidba", "b1_zanat", "b1_mejl", "intervju"]),
]
THEMEN = ("Kinderbuch", "Einfach", "Mittel", "Fortgeschritten", "Amtssprache")


def _html(wurzel):
    import app_quelle   # die ganze App, auch wenn sie in web/js geteilt ist
    return app_quelle.lesen(os.path.join(wurzel, "web")).replace("\r\n", "\n")


def test_stufe_fuer_stufe_von_leicht_nach_schwer(alle_daten):
    ids = [i for _, liste in NEU for i in liste]
    stufen = [st for st, liste in NEU for _ in liste]
    for code, daten in alle_daten.items():
        assert [g["id"] for g in daten["geschichten"]] == ids, code
        assert [g["stufe"] for g in daten["geschichten"]] == stufen, code


def test_reihenfolge_nennt_jede_geschichte_einmal():
    import geschichten
    assert len(geschichten.REIHENFOLGE) == len(set(geschichten.REIHENFOLGE))
    assert [g["id"] for g in geschichten.GESCHICHTEN] == geschichten.REIHENFOLGE


def test_ids_bleiben():
    """An der id haengt der Lesestand ("read"): keine weg, keine neu, keine umbenannt."""
    import geschichten
    assert sorted(g["id"] for g in geschichten.GESCHICHTEN) == sorted(ALTE_FOLGE)


def test_keine_themen_mehr(alle_daten):
    """Nur noch A1, A2 usw. - in jeder Sprache gleich, die alten Uebersetzungen der
    Themen sind raus. "Mittel" als Vokabel (sredstvo) steht in "woerter"."""
    import uebersetzungen
    for code, daten in alle_daten.items():
        assert {g["stufe"] for g in daten["geschichten"]} <= {"A1", "A2", "B1", "B2"}, code
    for code, teil in uebersetzungen.INHALT.items():
        for thema in THEMEN:
            assert thema not in teil.get("texte", {}), (code, thema)
    assert {"A1", "A2", "B1", "B2"} <= uebersetzungen.GLEICH
    en ={w["bs"]: w["de"] for k in alle_daten["en"]["kategorien"] for w in k["words"]}
    assert en["sredstvo"] == "means / agent"


def test_zusammenfassung_ohne_kinderbuch_und_amtssprache():
    """gesch.summary nannte die Themen ("von Kinderbuch bis Amtssprache")."""
    import sprachen
    for s in sprachen.SPRACHEN:
        text = sprachen.texte(s["code"])["gesch.summary"]
        assert "·" not in text and "{done}" in text and "{n}" in text, (s["code"], text)


def test_pruefung_meldet_falsche_stufe_und_folge(grunddaten):
    import inhalt
    assert inhalt.pruefe_geschichten_stufen(grunddaten) == []
    d = copy.deepcopy(grunddaten)
    d["geschichten"][0]["stufe"] = "Kinderbuch"
    assert any("ohne gültige Stufe: 'Kinderbuch'" in p for p in inhalt.pruefe_geschichten_stufen(d))
    d = copy.deepcopy(grunddaten)
    d["geschichten"].append(d["geschichten"].pop(0))     # eine A1 hinter alle B1
    assert any("nicht Stufe für Stufe" in p for p in inhalt.pruefe_geschichten_stufen(d))


def test_alte_folge_steht_in_der_app(wurzel):
    m = re.search(r"const GESCH_ALTE_FOLGE = \[(.*?)\];", _html(wurzel), re.S)
    assert m and re.findall(r"'([a-z0-9_]+)'", m.group(1)) == ALTE_FOLGE


def test_freischalten_mit_alter_folge(wurzel):
    html = _html(wurzel)
    rumpf = html.split("function storyUnlocked(i){\n")[1].split("\n}\n")[0]
    assert "read.has(s.id)" in rumpf and "read.has(STORIES[i-1].id)" in rumpf
    assert "GESCH_ALTE_FOLGE.indexOf(s.id)" in rumpf and "read.has(GESCH_ALTE_FOLGE[k-1])" in rumpf
    assert "const storyUnlocked" not in html


def _frei(i, gelesen, neu):
    """storyUnlocked() aus web/index.html, ohne allesOffen()."""
    s = neu[i]
    if i == 0 or s in gelesen or neu[i - 1] in gelesen:
        return True
    k = ALTE_FOLGE.index(s)
    return k == 0 or (k > 0 and ALTE_FOLGE[k - 1] in gelesen)


def test_zurueck_nur_in_eine_freie(wurzel):
    """Pruefung 17.11.2026: "Vorherige" (sPrev) oeffnete die davor ohne nachzufragen.
    Mit der alten Folge war die immer gelesen. In der neuen ist sie bei alten Staenden
    oft zu (37 Faelle, etwa "Mejl rođaku" vor "Razgovor za posao", wer bis "Kupujemo
    kuću" gelesen hat). Deshalb fragen Knopf, Horcher und Ergebnisschirm nach."""
    neu = [i for _, liste in NEU for i in liste]
    faelle = [(k, neu[i]) for k in range(len(ALTE_FOLGE) + 1)
              for i in range(1, len(neu))
              if _frei(i, set(ALTE_FOLGE[:k]), neu) and not _frei(i - 1, set(ALTE_FOLGE[:k]), neu)]
    assert len(faelle) == 37 and (11, "intervju") in faelle and (5, "grad") in faelle
    html = _html(wurzel)
    oeffnen = html.split("function openStory(i){\n")[1].split("\n}\n")[0]
    assert "$('sPrev').disabled = !(i>0 && storyUnlocked(i-1));" in oeffnen
    assert "$('sPrev').addEventListener('click',()=>{ if(rIdx>0 && storyUnlocked(rIdx-1)) openStory(rIdx-1); });" in html
    ergebnis = html.split("function showStoryQ(s, qi, right){\n")[1].split("\n}\n")[0]
    assert "$('sPrev').disabled = !(rIdx>0 && storyUnlocked(rIdx-1));" in ergebnis
    assert "$('sPrev').disabled = i===0;" not in html


def test_jede_geschichte_behaelt_ihre_aufnahme(wurzel):
    """Die Aufnahme haengt am Text, nicht am Platz: jede Geschichte findet ihre, mit
    passenden Wortzeiten (Mitlesen), numeriert in der alten Folge."""
    import geschichten
    import ton_bauen
    with io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8") as f:
        toene = {e["key"]: e for e in json.load(f)["toene"]}
    for g in geschichten.GESCHICHTEN:
        e = toene[ton_bauen.schluessel(g["text"])]
        assert e["datei"] == "g%02d.mp3" % (ALTE_FOLGE.index(g["id"]) + 1), g["id"]
        assert ton_bauen.wortzeiten_passen(e, g["text"]), g["id"]
        assert os.path.getsize(os.path.join(wurzel, "web", "audio", e["datei"])) > 800, g["id"]


def test_stories_json_in_der_neuen_folge(wurzel):
    """Der offene Datensatz (daten_exportieren.py) hat dieselbe Folge und die Stufe in
    jeder Sprache."""
    with io.open(os.path.join(wurzel, "data", "stories.json"), encoding="utf-8") as f:
        eintraege = json.load(f)["entries"]
    assert [e["id"] for e in eintraege] == [i for _, liste in NEU for i in liste]
    for e, st in zip(eintraege, [st for st, liste in NEU for _ in liste]):
        assert set(e["stage"].values()) == {st}, e["id"]
