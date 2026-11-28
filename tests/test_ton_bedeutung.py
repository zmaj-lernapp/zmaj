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


def _ist_wort(w):
    """istWort(grundBedeutung(w)) aus web/js/start.js: hoechstens zwei Woerter in der
    deutschen Bedeutung der Wort-ID. Alles andere zerlegt die Wortliste in Satzwoerter."""
    schnitt = len(w["id"]) - len(w["bs"]) - 1
    de = w["id"][:schnitt] if schnitt > 0 else w["de"]
    return len(re.sub(r"\([^)]*\)", " ", de).split(" / ")[0].split()) <= 2


def _saetze():
    return {i: w for i, w in _vokabeln().items() if not _ist_wort(dict(w, id=i))}


def test_saetze_gibt_es_und_passen(tabelle):
    """Abschnitt "saetze": jede Wort-ID ist ein Satz, das Wort steht darin, es hat ein "*"
    (von dem abgewichen wird), und der Schluessel gehoert zu diesem Wort."""
    saetze = _saetze()
    assert tabelle["saetze"]
    for i, je_wort in tabelle["saetze"].items():
        assert i in saetze, "kein Satz mit dieser Wort-ID (Tippfehler, oder ein Wort?): %s" % i
        teile = [x.lower() for x in ton_bauen.textwoerter(saetze[i]["bs"])]
        for wort, k in je_wort.items():
            assert wort in teile, (i, wort)
            assert wort in tabelle["geschichten"], (i, wort)
            assert ton_bedeutung.wort_von(k) == wort, (i, wort, k)
            assert k != tabelle["geschichten"][wort]["*"], "gleich dem \"*\", die Zeile ist ueberfluessig: %s" % i


# Woran man an der deutschen Bedeutung eines Satzes erkennt, dass ein Satzwort NICHT die
# Bedeutung aus dem WOERTERBUCH hat, und welcher Ton dann gilt (21.11.2026).
ANDERE_BEDEUTUNG = {
    "sam": (r"\b(allein|selbst|selber)\b", "sam"),                  # sȃm, nicht "bin"
    "smije": (r"\b(darf|darfst|dürfen|dürft)\b", "smije (darf)"),   # nicht "lacht"
    "jela": (r"\btanne", "jela (tanne)"),                           # nicht "gegessen"
}


def test_satzwort_mit_anderer_bedeutung_ist_entschieden(tabelle):
    """"Wörter dieses Levels" spielt fuer ein Satzwort den Ton seiner Bedeutung im
    WOERTERBUCH ("*"). In „Sam izdržava cijelu porodicu.“ ist das falsch: dort heisst
    "sam" allein. Ein neuer Satz dieser Art soll auffallen, bevor er nach Emirs
    Aufnahme "sam (bin)" spielt."""
    offen = []
    for i, w in _saetze().items():
        teile = {x.lower() for x in ton_bauen.textwoerter(w["bs"])}
        de = i[:len(i) - len(w["bs"]) - 1]                 # die deutsche Bedeutung, klein
        for wort, (muster, k) in ANDERE_BEDEUTUNG.items():
            if wort in teile and re.search(muster, de) and tabelle["saetze"].get(i, {}).get(wort) != k:
                offen.append("%s (%s: %s)" % (i, wort, k))
    assert offen == [], "in ton_bedeutung.json \"saetze\" eintragen: %s" % offen
    # Beim Zahnarzt gibt es keine Ausnahmen je Satz (zahnarzt_fuer_app() in inhalt.py).
    import zahnarzt
    za = ["%s (%s)" % (w["bs"], wort) for k in zahnarzt.KATEGORIEN for w in k["words"]
          for wort, (muster, _) in ANDERE_BEDEUTUNG.items()
          if wort in {x.lower() for x in ton_bauen.textwoerter(w["bs"])} and re.search(muster, w["de"].lower())]
    assert za == [], "Beim Zahnarzt braeuchte es satzwort_ton: %s" % za


def test_bau_merkt_veralteten_ton(tmp_path, monkeypatch, grunddaten):
    """app_bauen.inhalt_aktuell() meldet web/inhalt als veraltet, wenn der Ton nicht zur
    Tabelle passt: nach einer Aenderung an ton_bedeutung.json (Uhrzeit), und bei einem
    Inhalt ohne "ton" (gebaut vor dem 21.11.2026) auch dann, wenn die Datei neuer ist.
    Bis zur Pruefung vom 21.11.2026 kannte INHALT_QUELLEN die Tabelle gar nicht: das
    Handy haette die alten Toene gespielt, am PC waere alles richtig gewesen."""
    import shutil
    import time

    import app_bauen
    for quelle in ("ton_bedeutung.json", "ton_bedeutung.py", "inhalt.py"):
        assert quelle in app_bauen.INHALT_QUELLEN, quelle
    ordner = tmp_path / "web" / "inhalt"
    ordner.mkdir(parents=True)
    tab = tmp_path / "ton_bedeutung.json"
    shutil.copy(os.path.join(WURZEL, "ton_bedeutung.json"), str(tab))
    monkeypatch.setattr(app_bauen, "HIER", str(tmp_path))
    jetzt = time.time()

    def bauen(daten, tabelle_alter):
        (ordner / "de.json").write_text(json.dumps(daten, ensure_ascii=False), encoding="utf-8")
        os.utime(str(ordner / "de.json"), (jetzt, jetzt))
        os.utime(str(tab), (jetzt + tabelle_alter, jetzt + tabelle_alter))

    gebaut = {k: v for k, v in grunddaten.items() if k != "maskottchen"}
    bauen(gebaut, -60)
    assert app_bauen.inhalt_aktuell() == []

    felder = ("ton", "satzwort_ton")

    def ohne(x):
        return {k: v for k, v in x.items() if k not in felder}
    alt = dict(gebaut, kategorien=[dict(k, words=[ohne(w) for w in k["words"]]) for k in gebaut["kategorien"]],
               geschichten=[ohne(g) for g in gebaut["geschichten"]],
               grammatik={lid: dict(lek, uebungen=[ohne(u) for u in lek["uebungen"]]) if "uebungen" in lek else lek
                          for lid, lek in gebaut["grammatik"].items()})
    alt.pop("woerterbuch_ton")
    bauen(alt, -60)                                     # Datei neuer, aber ohne Ton
    assert app_bauen.inhalt_aktuell() == [app_bauen.TON_VERALTET]

    neu = json.loads(tab.read_text(encoding="utf-8"))
    neu["woerter"]["lang:dug"] = "dug (kurz)"
    tab.write_text(json.dumps(neu, ensure_ascii=False), encoding="utf-8")
    bauen(gebaut, +60)                                  # Tabelle nach dem Bauen geaendert
    assert app_bauen.inhalt_aktuell() == ["ton_bedeutung.json"]
    bauen(gebaut, -60)                                  # ... und Datei trotzdem neuer
    assert app_bauen.inhalt_aktuell() == [app_bauen.TON_VERALTET]


def test_geschichte_toene_zaehlt_wie_die_app():
    """Gross und klein ist dasselbe Wort, gezaehlt ab dem ersten Vorkommen; None heisst
    wie bisher, und ein Wort ohne eigene Aufnahme kommt gar nicht hinein."""
    g = {"id": "probe", "text": "Sam je sam. Ja sam, kaže on."}
    regeln = {"sam": {"*": "sam (bin)", "probe": ["sam", "sam", "sam (bin)"]},
              "je": {"*": "je"}, "on": {"*": "on (er)"}}
    assert ton_bedeutung.geschichte_toene(g, regeln) == {"sam": [None, None, "sam (bin)"], "on": ["on (er)"]}
    assert ton_bedeutung.geschichte_toene(dict(g, id="andere"), regeln) == {
        "sam": ["sam (bin)"] * 3, "on": ["on (er)"]}


def test_jede_bedeutung_bekommt_eine_eigene_aufnahme(tabelle):
    """Seit dem Abend des 21.11.2026 bekommt jede Bedeutung eine eigene Aufnahme, statt
    dass eine die heutige Datei behaelt: sonst haette Ajdin fuer 16 Dateien heraushoeren
    muessen, zu welcher Bedeutung sie passt. Einzige Ausnahme ist sȃm (allein), dafuer
    klingt w1359 (gemessen und gehoert, Release/Ton_gleiche_Schreibung_2026-11-21/
    ursache.md). Jedes Wort der Tabelle hat mindestens zwei Bedeutungen."""
    bisherig = sorted({k for _, k in ton_bedeutung.alle_schluessel(tabelle) if not ton_bedeutung.eigen(k)})
    assert bisherig == ["sam"], bisherig
    je_wort = {}
    for _, k in ton_bedeutung.alle_schluessel(tabelle):
        je_wort.setdefault(ton_bedeutung.wort_von(k), set()).add(k)
    assert {w: ks for w, ks in je_wort.items() if len(ks) < 2} == {}
    assert len(ton_bedeutung.eigene_schluessel(tabelle)) == 35          # Emir-Liste w10059 bis w10093


def test_app_bekommt_den_ton(grunddaten):
    """Was die App bekommt: "ton" dort, wo es eine eigene Aufnahme geben soll."""
    voc = {w["id"]: w for k in grunddaten["kategorien"] for w in k["words"]}
    assert voc["lang:dug"]["ton"] == "dug (lang)" and voc["lang:dug"]["bs"] == "dug"
    assert voc["schulden:dug"]["ton"] == "dug (schulden)"
    assert voc["wenig:malo"]["ton"] == "malo (wenig)" and voc["klein:malo"]["ton"] == "malo (klein)"
    assert voc["küken / hähnchen:pile"]["ton"] == "pile (küken)"
    gesch = {g["id"]: g for g in grunddaten["geschichten"]}
    # Ajdins Fund: in b1_voz ist das erste "sam" "bin", das zweite "allein" (w1359 wie bisher)
    assert gesch["b1_voz"]["ton"]["sam"] == ["sam (bin)", None]
    assert gesch["jucer"]["ton"]["sam"] == ["sam (bin)"] * 3
    assert gesch["pismo"]["ton"]["mi"] == ["mi (wir)"]          # "Mi smo dobro"
    assert gesch["jucer"]["ton"]["mi"] == ["mi (mir)"]          # "Nana mi je pokazala"
    assert gesch["b1_doktor"]["ton"]["vas"] == ["vas (betont)", "vas (unbetont)"]
    assert gesch["b1_struja"]["ton"]["te"] == ["te (diese)"] and gesch["pismo"]["ton"]["te"] == ["te (dich)"]
    assert gesch["mira"]["ton"]["smije"] == ["smije (lacht)"]
    assert gesch["b1_kahva"]["ton"]["smije"] == ["smije (darf)"]
    assert gesch["jucer"]["ton"]["pile"] == ["pile (getrunken)"]
    assert gesch["b1_pita"]["ton"]["pita"] == ["pita (gericht)"]
    u = grunddaten["grammatik"]["faelle3"]["uebungen"][4]
    assert (u["richtig"], u["ton"]) == ("mi", "mi (mir)")
    assert grunddaten["grammatik"]["vergangenheit"]["uebungen"][2]["ton"] == "radio (gemacht)"
    assert grunddaten["woerterbuch_ton"]["sam"] == "sam (bin)"
    assert grunddaten["woerterbuch_ton"]["smije"] == "smije (lacht)"
    # Satzwoerter der Wortliste, die nicht die Bedeutung aus dem Woerterbuch haben
    assert voc["er versorgt allein die ganze familie.:Sam izdržava cijelu porodicu."]["satzwort_ton"] == {
        "sam": "sam"}
    assert voc["in der kurve darf man nicht überholen.:U krivini se ne smije preticati."]["satzwort_ton"] == {
        "smije": "smije (darf)"}
    assert "satzwort_ton" not in voc["ich habe die schlüssel verloren.:Izgubio sam ključeve."]


def test_ton_ist_in_jeder_sprache_gleich(alle_daten, grunddaten):
    """Der Ton haengt an Wort-ID und Geschichte, nicht an der Sprache."""
    def toene(d):
        return ({w["id"]: w.get("ton") for k in d["kategorien"] for w in k["words"] if w.get("ton")},
                {g["id"]: g.get("ton") for g in d["geschichten"] if g.get("ton")},
                {lid: [u.get("ton") for u in lek.get("uebungen", [])] for lid, lek in d["grammatik"].items()},
                d["woerterbuch_ton"],
                {w["id"]: w["satzwort_ton"] for k in d["kategorien"] for w in k["words"] if "satzwort_ton" in w})
    soll = toene(grunddaten)
    assert soll[0] and soll[1] and soll[4]
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
    assert not [w["bs"] for k in vokabeln.KATEGORIEN for w in k["words"] if "ton" in w or "satzwort_ton" in w]


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
