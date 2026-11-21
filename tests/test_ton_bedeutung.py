# -*- coding: utf-8 -*-
"""Eigener Ton je Bedeutung (21.11.2026): ton_bedeutung.json und ton_bedeutung.py.

Die App sucht den Ton nach dem Text. "sam" hatte deshalb eine einzige Aufnahme, und
die klang wie sȃm (allein), auch wo "sam" "bin" heisst. Ajdin hat es beim Test der 1.5
gehoert. ton_bedeutung.json legt je Wort-ID, Grammatik-Uebung und Stelle in einer
Geschichte einen Ton-Schluessel fest, inhalt.lade_daten() traegt ihn als "ton" ein,
und die App spielt ihn, sobald es die Aufnahme gibt (eigenerTon() in
web/js/ton_abspielen.js). Bis dahin spielt sie wie bisher. Im Browser prueft das
tests_e2e/test_ton_bedeutung.py.

Die Wachen hier sorgen dafuer, dass fuer jedes Wort der Tabelle jede Bedeutung eine
Entscheidung hat: kommt ein neues Wort gleicher Schreibung dazu (K2: tanne:jela), oder
eine Geschichte mit eigener Bedeutung im Glossar, schlaegt ein Test an.
"""
import io
import json
import os
import re

import pytest

import ton_bauen
import ton_bedeutung

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def tabelle():
    return ton_bedeutung.lade()


@pytest.fixture(scope="module")
def haben():
    """Alle Ton-Schluessel, die es heute gibt: web/audio und ton_nur_emir.json."""
    with io.open(os.path.join(WURZEL, "web", "audio", "index.json"), encoding="utf-8") as f:
        keys = {e["key"] for e in json.load(f)["toene"]}
    return keys | set(ton_bauen.nur_emir())


def _gefunden(text, haben):
    """Unter welchem Schluessel audioDatei() den Text findet (web/js/ton_abspielen.js):
    bei " / " der ganze Text, dann die erste Form, dann ohne .!?… am Ende."""
    klein = text.strip().lower()
    if " / " in klein and klein in haben:
        return klein
    voll = text.split(" / ")[0].strip().lower()
    kurz = re.sub(r"[.!?…]+$", "", text.split(" / ")[0]).strip().lower()
    return voll if voll in haben else kurz if kurz in haben else None


def _vokabeln():
    import vokabeln
    return {"%s:%s" % (w["de"].strip().lower(), w["bs"]): w for k in vokabeln.KATEGORIEN for w in k["words"]}


def _geschichten():
    import geschichten
    return {g["id"]: g for g in geschichten.GESCHICHTEN}


def _uebung(stelle):
    import grammatik
    lektion, _, nr = stelle.partition("#")
    uebungen = grammatik.GRAMMATIK.get(lektion, {}).get("uebungen", [])
    return uebungen[int(nr)] if nr.isdigit() and int(nr) < len(uebungen) else None


def test_schluessel_sehen_aus_wie_verlangt(tabelle):
    """Jeder Schluessel ist das Wort selbst oder "wort (bedeutung)", klein geschrieben,
    ohne " / ": genau so, wie ton_pruefen.py ihn in ton_nur_emir.json verlangt
    (key == schluessel(text))."""
    alle = ton_bedeutung.alle_schluessel(tabelle)
    assert alle
    for stelle, k in alle:
        assert isinstance(k, str) and k == ton_bauen.schluessel(k) and " / " not in k, (stelle, k)
        w = ton_bedeutung.wort_von(k)
        assert k == w or re.fullmatch(re.escape(w) + r" \([^()]+\)", k), (stelle, k)
    for wort, regeln in tabelle["geschichten"].items():
        assert "*" in regeln, wort
        for wo, wert in regeln.items():
            for k in (wert if isinstance(wert, list) else [wert]):
                assert ton_bedeutung.wort_von(k) == wort, (wort, wo, k)


def test_woerter_gibt_es_und_passen(tabelle, haben):
    """Jede Wort-ID gibt es, und ihr Ton heute ist das Wort des Schluessels."""
    voc = _vokabeln()
    for i, k in tabelle["woerter"].items():
        assert i in voc, "Wort-ID gibt es nicht (Tippfehler?): %s" % i
        assert _gefunden(voc[i]["bs"], haben) == ton_bedeutung.wort_von(k), (i, k)


def test_vorgemerkt_gibt_es_noch_nicht(tabelle):
    """vorgemerkt ist fuer Woerter, die noch kommen (K2: Tanne). Gibt es die Wort-ID,
    gehoert die Zeile nach woerter."""
    voc = _vokabeln()
    for i in tabelle["vorgemerkt"]:
        assert i not in voc, "%s gibt es jetzt: in ton_bedeutung.json nach \"woerter\" verschieben" % i
    assert not set(tabelle["vorgemerkt"]) & set(tabelle["woerter"])


def test_jede_vokabel_mit_gleichem_ton_ist_entschieden(tabelle, haben):
    """Spielt eine Vokabel heute den Ton eines Tabellenworts, steht ihre Wort-ID in
    woerter oder vorgemerkt - auch wenn sie die Aufnahme wie bisher behaelt. So faellt
    ein neues Wort gleicher Schreibung auf, bevor es den falschen Ton bekommt."""
    woerter = set(ton_bedeutung.tabellenwoerter(tabelle))
    entschieden = set(tabelle["woerter"]) | set(tabelle["vorgemerkt"])
    offen = sorted(i for i, w in _vokabeln().items()
                   if _gefunden(w["bs"], haben) in woerter and i not in entschieden)
    assert offen == [], "in ton_bedeutung.json \"woerter\" entscheiden: %s" % offen


def test_grammatik_stellen_gibt_es_und_passen(tabelle, haben):
    for stelle, k in tabelle["grammatik"].items():
        u = _uebung(stelle)
        assert u is not None, "keine Uebung %s" % stelle
        assert _gefunden(u["richtig"], haben) == ton_bedeutung.wort_von(k), (stelle, u["richtig"], k)


def test_jede_grammatik_antwort_mit_gleichem_ton_ist_entschieden(tabelle, haben):
    import grammatik
    woerter = set(ton_bedeutung.tabellenwoerter(tabelle))
    offen = sorted("%s#%d" % (lid, i) for lid, lek in grammatik.GRAMMATIK.items()
                   for i, u in enumerate(lek.get("uebungen", []))
                   if _gefunden(u.get("richtig", ""), haben) in woerter
                   and "%s#%d" % (lid, i) not in tabelle["grammatik"])
    assert offen == [], "in ton_bedeutung.json \"grammatik\" entscheiden: %s" % offen


def test_geschichten_stellen_gibt_es_und_zaehlen_richtig(tabelle):
    """Jede genannte Geschichte gibt es, das Wort steht darin, und eine Liste hat genau
    einen Eintrag je Vorkommen (gezaehlt wie die antippbaren Woerter der App)."""
    gesch = _geschichten()
    for wort, regeln in tabelle["geschichten"].items():
        for gid, wert in regeln.items():
            if gid == "*":
                continue
            assert gid in gesch, (wort, gid)
            n = [x.lower() for x in ton_bauen.textwoerter(gesch[gid]["text"])].count(wort)
            assert n, "%s kommt in %s nicht vor" % (wort, gid)
            if isinstance(wert, list):
                assert len(wert) == n, (wort, gid, len(wert), n)


def test_geschichte_mit_eigenem_glossar_ist_entschieden(tabelle):
    """Hat eine Geschichte fuer ein Tabellenwort eine eigene Bedeutung im Glossar
    (vokabeln), muss die Tabelle sie ausdruecklich nennen - "*" gehoert zum
    WOERTERBUCH und passt dann vielleicht nicht."""
    offen = sorted("%s in %s (%s)" % (w, g["id"], (g.get("vokabeln") or {})[w])
                   for g in _geschichten().values() for w in tabelle["geschichten"]
                   if w in (g.get("vokabeln") or {}) and g["id"] not in tabelle["geschichten"][w])
    assert offen == [], "in ton_bedeutung.json \"geschichten\" entscheiden: %s" % offen


def test_geschichte_toene_zaehlt_wie_die_app():
    """Gross und klein ist dasselbe Wort, gezaehlt ab dem ersten Vorkommen; None heisst
    wie bisher, und ein Wort ohne eigene Aufnahme kommt gar nicht hinein."""
    g = {"id": "probe", "text": "Sam je sam. Ja sam, kaže on."}
    regeln = {"sam": {"*": "sam (bin)", "probe": ["sam", "sam", "sam (bin)"]},
              "je": {"*": "je"}, "on": {"*": "on (er)"}}
    assert ton_bedeutung.geschichte_toene(g, regeln) == {"sam": [None, None, "sam (bin)"], "on": ["on (er)"]}
    assert ton_bedeutung.geschichte_toene(dict(g, id="andere"), regeln) == {
        "sam": ["sam (bin)"] * 3, "on": ["on (er)"]}


def test_app_bekommt_den_ton(grunddaten):
    """Was die App bekommt: "ton" nur dort, wo es eine eigene Aufnahme geben soll."""
    voc = {w["id"]: w for k in grunddaten["kategorien"] for w in k["words"]}
    assert voc["lang:dug"]["ton"] == "dug (lang)" and voc["lang:dug"]["bs"] == "dug"
    assert "ton" not in voc["schulden:dug"]
    assert voc["wenig:malo"]["ton"] == "malo (wenig)" and "ton" not in voc["klein:malo"]
    gesch = {g["id"]: g for g in grunddaten["geschichten"]}
    # Ajdins Fund: in b1_voz ist das erste "sam" "bin", das zweite "allein"
    assert gesch["b1_voz"]["ton"]["sam"] == ["sam (bin)", None]
    assert gesch["jucer"]["ton"]["sam"] == ["sam (bin)"] * 3
    assert "mi" not in gesch["pismo"]["ton"]                  # "Mi smo dobro": wir, wie bisher
    assert gesch["b1_doktor"]["ton"]["vas"] == ["vas (betont)", None]
    assert gesch["b1_struja"]["ton"]["te"] == ["te (diese)"]
    assert "ton" not in gesch["mira"] or "smije" not in gesch["mira"]["ton"]   # lacht, wie bisher
    assert gesch["b1_kahva"]["ton"]["smije"] == ["smije (darf)"]
    u = grunddaten["grammatik"]["faelle3"]["uebungen"][4]
    assert (u["richtig"], u["ton"]) == ("mi", "mi (mir)")
    assert grunddaten["grammatik"]["vergangenheit"]["uebungen"][2]["ton"] == "radio (gemacht)"
    assert grunddaten["woerterbuch_ton"]["sam"] == "sam (bin)"
    assert "te" not in grunddaten["woerterbuch_ton"]


def test_ton_ist_in_jeder_sprache_gleich(alle_daten, grunddaten):
    """Der Ton haengt an Wort-ID und Geschichte, nicht an der Sprache."""
    def toene(d):
        return ({w["id"]: w.get("ton") for k in d["kategorien"] for w in k["words"] if w.get("ton")},
                {g["id"]: g.get("ton") for g in d["geschichten"] if g.get("ton")},
                {lid: [u.get("ton") for u in lek.get("uebungen", [])] for lid, lek in d["grammatik"].items()},
                d["woerterbuch_ton"])
    soll = toene(grunddaten)
    assert soll[0] and soll[1]
    for code, d in alle_daten.items():
        assert toene(d) == soll, code


def test_moduldaten_bleiben_unberuehrt(grunddaten):
    """anwenden() kopiert. Auf Deutsch reicht uebersetzungen.anwenden() die Listen aus
    geschichten.py und grammatik.py unveraendert durch; ein "ton" dort bliebe stehen."""
    import geschichten
    import grammatik
    import vokabeln
    assert not [g["id"] for g in geschichten.GESCHICHTEN if "ton" in g]
    assert not [lid for lid, lek in grammatik.GRAMMATIK.items() for u in lek.get("uebungen", []) if "ton" in u]
    assert not [w["bs"] for k in vokabeln.KATEGORIEN for w in k["words"] if "ton" in w]


def test_azure_spricht_die_schluessel_nie(tabelle):
    """ton_bauen.sammle() nimmt die eigenen Schluessel nicht auf: sonst erzeugte der
    naechste grosse Lauf mit Azure eine Aufnahme, die "sam (bin)" vorliest. Und kein
    Schluessel ist zugleich ein echter Text im Inhalt."""
    eigene = set(ton_bedeutung.eigene_schluessel(tabelle))
    assert eigene
    assert not eigene & {p["key"] for p in ton_bauen.sammle()}


def test_ton_pruefen_meldet_fehlende_nur_als_hinweis(tabelle):
    """Fehlt Emirs Aufnahme, ist das kein Fehler (die App spielt wie bisher). Ein
    Schluessel in web/audio oder einer, der ein echter Text ist, schon."""
    import ton_pruefen
    eigene = ton_bedeutung.eigene_schluessel(tabelle)
    assert ton_pruefen.bedeutung_pruefen(set(), set(), set(), tabelle) == ([], eigene)
    fehler, fehlt = ton_pruefen.bedeutung_pruefen({"sam (bin)"}, set(), set(), tabelle)
    assert fehler == [] and "sam (bin)" not in fehlt and len(fehlt) == len(eigene) - 1
    fehler, _ = ton_pruefen.bedeutung_pruefen(set(), {"sam (bin)"}, set(), tabelle)
    assert len(fehler) == 1 and "web/audio" in fehler[0]
    fehler, _ = ton_pruefen.bedeutung_pruefen(set(), set(), {"sam (bin)"}, tabelle)
    assert len(fehler) == 1 and "Text im Inhalt" in fehler[0]


def test_ohne_tabelle_bleibt_alles_wie_vorher(tmp_path, grunddaten):
    leer = ton_bedeutung.lade(str(tmp_path / "gibt_es_nicht.json"))
    assert leer == {k: {} for k in ton_bedeutung.ABSCHNITTE}
    d = ton_bedeutung.anwenden({"kategorien": [{"id": "k", "words": [{"id": "lang:dug", "bs": "dug"}]}],
                                "grammatik": {}, "geschichten": [{"id": "x", "text": "Ja sam."}]}, leer)
    assert d["woerterbuch_ton"] == {}
    assert d["kategorien"] == [{"id": "k", "words": [{"id": "lang:dug", "bs": "dug"}]}]
    assert d["geschichten"] == [{"id": "x", "text": "Ja sam."}]


def test_fuenfstellige_nummern_laufen_durch(tmp_path):
    """Die neuen Aufnahmen bekommen w10059 und hoeher, nach der K2-Liste (w9872 bis w10058).
    Bis zum 21.11.2026 kannten app_bauen.py und ton_pruefen.py nur vier Ziffern, und
    ton_bauen.py las aus w10059.mp3 die Zahl 1005 - das naechste neue Wort haette eine
    schon vergebene Nummer bekommen."""
    import app_bauen
    import ton_pruefen
    for name in ("w0384.mp3", "w9871.mp3", "w10059.mp3"):
        assert app_bauen.EMIR_DATEI.fullmatch(name), name
        assert app_bauen.ton_filter(name) == app_bauen.ton_filter("w0384.mp3") is not None, name
    for name in ("w123.mp3", "w123456.mp3", "g01.mp3", "w10059.ogg"):
        assert not app_bauen.EMIR_DATEI.fullmatch(name), name
    assert [ton_bauen.dateinummer(d) for d in ("w0384.mp3", "w10059.mp3", "g07.mp3")] == [384, 10059, 7]
    emir = {"sam (bin)": {"key": "sam (bin)", "datei": "w10059.mp3", "text": "sam (bin)"}}
    assert ton_pruefen.nur_emir_pruefen(emir, [], audio=str(tmp_path)) == []
    falsch = {"x": {"key": "x", "datei": "w123456.mp3", "text": "x"}}
    assert "kein Name wie" in ton_pruefen.nur_emir_pruefen(falsch, [], audio=str(tmp_path))[0]
