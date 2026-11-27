# -*- coding: utf-8 -*-
"""Stufen-Reiter A1 · A2 · B1 · B2 · C1 (13.11.2026).

Ajdin am 13.11.2026 zu Release\\Entscheidungen_2026-11-13: „alles wie
empfohlen“, also Variante B (Frage 5b): Reiter je Stufe, zwei neue frühe
Level mit den 40 verspäteten Grundwörtern, „Zuhause“ hinter die Grammatik.
Der Sprung-Test in den nächsten Reiter kostet Leben wie der Level-Test (7a).
B2 ist von 14 auf 9 Sektionen zusammengelegt (6a), eine Farbe je Sektion.

Hier steht, was sich ohne Browser prüfen lässt: Inhalt, Umzug, Übersetzungen
und die Stellen im Quelltext. Das Verhalten prüft tests_e2e/test_reiter.py."""
import re

import pytest

from grundwoerter_umzug import UMZUG, kategorien_vor_umzug

A1_SAETZE = ["fragen", "genus", "konjugation", "mehrzahl", "satzbau", "kleine_woerter", "faelle1"]
ZUHAUSE = ["kueche_bad", "putzen", "technik", "auto_werkstatt", "geraete"]


def _stufe_je_level(daten):
    st = {s["id"]: s["stufe"] for s in daten["sektionen"]}
    return [st[k["sektion"]] for k in daten["kategorien"]]


def test_reiter_mit_ihren_sektionen_und_leveln(grunddaten):
    """Die Tabelle aus reiter.md: A1 30 Level, A2 31, B1 107, B2 129, C1 leer. Seit dem
    27.11.2026 hat B1 108: Ordnungszahlen (K7) hinter Zeitangaben."""
    sek = grunddaten["sektionen"]
    stufen = _stufe_je_level(grunddaten)
    assert [stufen.count(s) for s in ("A1", "A2", "B1", "B2", "C1")] == [30, 31, 108, 129, 0]
    assert [s["id"] for s in sek if s["stufe"] == "A1"] == ["alltag", "anfassen", "tiernatur", "saetze"]
    assert [s["id"] for s in sek if s["stufe"] == "A2"] == ["zuhause2", "saetze2", "einkauf", "herkunft", "kultur"]
    assert [s["id"] for s in sek if s["stufe"] == "B1"][0] == "amt", "Amt & Verträge ist Sektion 1 von B1"
    assert len([s for s in sek if s["stufe"] == "B1"]) == 9
    assert [s["id"] for s in sek if s["stufe"] == "B2"] == [
        "denkenmeinen", "arbeitwirtschaft", "medienkultur", "gesellschaftpolitik", "hauswohnung",
        "gesundheitsport", "schulewissen", "stadtreisen", "handelnveraendern"], "6a: neun Sektionen, neun Farben"
    assert all(len([s for s in sek if s["stufe"] == st]) <= 9 for st in ("A1", "A2", "B1", "B2")), \
        "keine Farbe doppelt in einem Reiter (Farben-Entscheidung vom 27.09.2026)"
    assert stufen == sorted(stufen), "die Reiter stehen im Lernpfad in ihrer Folge"


def test_sektionsnummern_je_reiter_in_jeder_sprache(alle_daten):
    import inhalt
    for code, daten in alle_daten.items():
        assert inhalt.pruefe_stufen(daten) == [], code
    de = {s["id"]: s["label"] for s in alle_daten["de"]["sektionen"]}
    assert de["saetze"] == "Sektion 4 · Sätze bauen 1"
    assert de["zuhause2"] == "Sektion 1 · Zuhause"
    assert de["saetze2"] == "Sektion 2 · Sätze bauen 2"
    assert de["amt"] == "Sektion 1 · Amt & Verträge"
    assert de["handelnveraendern"] == "Sektion 9 · Handeln und genauer sagen"
    assert de["denkenmeinen"] == "Sektion 1 · Denken, Fühlen und Beziehungen"
    en = {s["id"]: s["label"] for s in alle_daten["en"]["sektionen"]}
    assert en["saetze2"] == "Section 2 · Building sentences 2"
    assert en["stadtreisen"] == "Section 8 · Town, country and on the move"


@pytest.mark.parametrize("daten, befund", [
    ({"sektionen": [{"id": "a", "stufe": "A2", "label": "Sektion 1 · A"},
                    {"id": "b", "stufe": "A1", "label": "Sektion 1 · B"}],
      "kategorien": [{"id": "x", "sektion": "a"}, {"id": "y", "sektion": "b"}]}, "Folge"),
    ({"sektionen": [{"id": "a", "stufe": "A1", "label": "Sektion 1 · A"},
                    {"id": "b", "stufe": "A1", "label": "Sektion 3 · B"}],
      "kategorien": [{"id": "x", "sektion": "a"}, {"id": "y", "sektion": "b"}]}, "sollte 2 sein"),
    ({"sektionen": [{"id": "a", "stufe": "A1", "label": "Sektion 1 · A"},
                    {"id": "b", "stufe": "A1", "label": "Sektion 2 · B"}],
      "kategorien": [{"id": "x", "sektion": "a"}, {"id": "y", "sektion": "b"},
                     {"id": "z", "sektion": "a"}]}, "zerrissen"),
    ({"sektionen": [{"id": "a", "stufe": "D1", "label": "Sektion 1 · A"}],
      "kategorien": [{"id": "x", "sektion": "a"}]}, "ohne gültige Stufe"),
])
def test_pruefung_meldet_falsche_reiter(daten, befund):
    import inhalt
    assert any(befund in b for b in inhalt.pruefe_stufen(daten)), inhalt.pruefe_stufen(daten)


def test_variante_b_reihenfolge(grunddaten):
    """Zuhause hinter Fälle 1, Kleine Wörter vor Fälle 1, Wörter für jeden Tag
    hinter dem Tagesablauf (level_reiter.csv)."""
    ids = [k["id"] for k in grunddaten["kategorien"]]
    sektion = {k["id"]: k["sektion"] for k in grunddaten["kategorien"]}
    assert ids[23:30] == A1_SAETZE, "A1 Level 24 bis 30"
    assert ids[30:35] == ZUHAUSE, "A2 Level 1 bis 5"
    assert ids[ids.index("routine") + 1] == "jeden_tag" and ids[ids.index("jeden_tag") + 1] == "adjektive"
    assert ids.index("jeden_tag") - 30 + 1 == 15, "A2 Level 15"
    assert all(sektion[i] == "saetze" for i in A1_SAETZE)
    assert all(sektion[i] == "zuhause2" for i in ZUHAUSE)
    a2 = [i for i, s in zip(ids, _stufe_je_level(grunddaten)) if s == "A2"]
    assert a2[5:22] == ["faelle2", "praepositionen", "faelle3", "faelle4", "vergangenheit", "zukunft", "modal",
                        "reflexiv", "routine", "jeden_tag", "adjektive", "mengen", "gefuehle", "reisen", "feiern",
                        "arbeit", "saetze"]
    assert all(sektion[i] == "saetze2" for i in a2[5:22])


def test_vierzig_grundwoerter_nur_umgezogen(grunddaten):
    """Kennung, Bedeutung und Wort bleiben; jedes Wort steht genau einmal in
    der App, nur in seinem neuen Level, und vorher kam es erst in B1."""
    nach_id = {k["id"]: k for k in grunddaten["kategorien"]}
    stufe = dict(zip([k["id"] for k in grunddaten["kategorien"]], _stufe_je_level(grunddaten)))
    alle = [(k["id"], w) for k in grunddaten["kategorien"] for w in k["words"]]
    for ziel, bs, de, alt, _ in UMZUG:
        kennung = "%s:%s" % (de.lower(), bs)
        wo = [kid for kid, w in alle if w["id"] == kennung]
        assert wo == [ziel], (bs, wo)
        assert stufe[alt] == "B1", alt
    assert stufe["kleine_woerter"] == "A1" and stufe["jeden_tag"] == "A2"
    assert [w["bs"] for w in nach_id["kleine_woerter"]["words"]] == [u[1] for u in UMZUG if u[0] == "kleine_woerter"]
    assert [w["bs"] for w in nach_id["jeden_tag"]["words"]] == [u[1] for u in UMZUG if u[0] == "jeden_tag"]
    assert len(nach_id["kleine_woerter"]["words"]) == len(nach_id["jeden_tag"]["words"]) == 20


def test_beispielsaetze_bleiben_in_b1(grunddaten):
    """Der Beispielsatz bleibt als Wiederholung, wo er ist (reihenfolge_befunde.csv)."""
    vorher = {k["id"]: k for k in kategorien_vor_umzug(grunddaten["kategorien"])}
    jetzt = {k["id"]: k for k in grunddaten["kategorien"]}
    for _, bs, _, alt, platz in UMZUG:
        satz = vorher[alt]["words"][platz + 1]
        assert re.search(r"[.!?]$", satz["bs"]), (bs, satz)
        assert satz["id"] in {w["id"] for w in jetzt[alt]["words"]}, (bs, satz["bs"])


def test_vor_umzug_ist_der_alte_inhalt(grunddaten):
    """Die Hilfe fuer die Pakettests stellt genau den alten Stand her."""
    vorher = kategorien_vor_umzug(grunddaten["kategorien"])
    assert len(vorher) == 296       # 295 bis K7, seit 27.11.2026 mit dem Level Ordnungszahlen
    assert sum(len(k["words"]) for k in vorher) == sum(len(k["words"]) for k in grunddaten["kategorien"])
    hier = {k["id"]: [w["bs"] for w in k["words"]] for k in vorher}
    assert hier["hier_dort"][:3] == ["tu", "Ostavi torbu tu, pored vrata.", "ovdje"]


def test_umgezogene_woerter_haben_emirs_ton():
    """Die Einträge gibt es schon, mit Ton - es kostet nichts (reiter.md).

    36 der 40 gibt es nur von Emir (ton_nur_emir.json). tamo, tu, onda und
    prvo stehen seit Oktober in web/audio (Azure); in der App liegt Emirs
    Aufnahme derselben Nummer darüber (app_bauen.emir_drueber). Ist die
    private Hülle da, muss die Datei dort liegen."""
    import io
    import json
    import os

    import app_bauen
    import ton_bauen
    emir = ton_bauen.nur_emir()
    web = {e["key"]: e["datei"] for e in json.load(io.open(ton_bauen.INDEX, encoding="utf-8"))["toene"]}
    fehlt, nur_web = [], []
    for u in UMZUG:
        k = next((f(u[1]) for f in (ton_bauen.schluessel_alle, ton_bauen.schluessel)
                  if f(u[1]) in emir or f(u[1]) in web), None)
        if k is None:
            fehlt.append(u[1])
        elif k not in emir:
            nur_web.append(web[k])
    assert not fehlt, fehlt
    assert sorted(nur_web) == ["w1265.mp3", "w1273.mp3", "w1321.mp3", "w1341.mp3"], nur_web
    if os.path.isdir(app_bauen.EMIR):
        assert all(os.path.isfile(os.path.join(app_bauen.EMIR, d)) for d in nur_web), nur_web


def test_satzbau_der_zuhause_woerter_zieht_mit():
    """Sechs Satzbau-Sätze brauchten Wörter aus Zuhause und stehen jetzt im
    ersten Level, in dem jede Kachel bekannt ist: vier in Zuhause, die zwei mit
    "se zove" in Fälle 1 (zvati). Topf und Sterne ziehen über SAETZE_UMBENANNT
    mit (index.html)."""
    import vokabeln
    kat = {s["bs"]: s["kat"] for s in vokabeln.SATZBAU}
    assert kat["Ovo je moj tanjir."] == "kueche_bad"
    assert kat["Gdje je moj alat?"] == "technik"
    assert kat["Gdje je moj punjač?"] == "geraete"
    assert kat["Moja sestra se zove Amina."] == kat["Moj muž se zove Ajdin."] == "faelle1"
    assert kat["Gdje mogu parkirati svoj auto?"] == "auto_werkstatt"


def test_umbenannte_satzbau_schluessel_fuehren_zu_einem_satz(index_html):
    import vokabeln
    block = re.search(r"const SAETZE_UMBENANNT = \{(.*?)\};", index_html, re.S).group(1)
    paare = re.findall(r"'(k:[^']+)': '(k:[^']+)'", block)
    neu = {"k:%s|%s" % (s["kat"], s["bs"]) for s in vokabeln.SATZBAU}
    reiter = [(a, b) for a, b in paare if a.startswith(("k:genus|", "k:faelle1|"))]
    assert len(reiter) == 6
    for alt, ziel in reiter:
        assert ziel in neu and alt not in neu, (alt, ziel)
        assert alt.split("|", 1)[1] == ziel.split("|", 1)[1], "der Satz selbst bleibt"


def test_oberflaechentexte_in_acht_sprachen():
    import sprachen
    schluessel = ["reiter.leiste", "reiter.fertig", "reiter.stand", "reiter.zu", "reiter.bald", "reiter.zu_titel",
                  "reiter.zu_text", "reiter.zu_erst", "reiter.bald_titel", "sprung.starten", "sprung.regel",
                  "sprung.titel", "sprung.offen", "sprung.nicht", "sprung.zum_reiter", "sprung.abbrechen_frage",
                  "sprung.abbrechen_text", "sprung.keine_leben", "pfad.sektion_zu", "pfad.erst_stufe"]
    codes = [s["code"] for s in sprachen.SPRACHEN]
    assert len(codes) == 8
    for c in codes:
        texte = sprachen.texte(c)
        for s in schluessel:
            assert texte.get(s, "").strip(), (c, s)
        assert "{stufe}" in texte["einst.ergebnis_start"] and "{n}" in texte["einst.ergebnis_start"], c
    # kurz, keine Erklaertexte in der Oberflaeche (app-statt-werkzeug)
    de = sprachen.texte("de")
    assert all(len(de[s]) <= 80 for s in schluessel), [s for s in schluessel if len(de[s]) > 80]


def _rumpf(html, kopf):
    html = html.replace("\r\n", "\n")
    return html.split(kopf)[1].split("\n}\n")[0]


def test_freischaltung_im_quelltext(index_html):
    html = index_html.replace("\r\n", "\n")
    # eine Kette: Bestanden, Einstufung, Sprung-Test - und angefangene Level bleiben offen
    frei = html.split("const freiBis = () => {\n")[1].split("\n};\n")[0]
    assert "let n = hoechsterBestanden() + 1;" in frei
    assert "return Math.max(n, einstufungIndex(), sprungIndex());" in frei
    assert "return inDerKette(i) || levelAngefangen(i);" in html
    assert "const inDerKette = i => allesOffen() || i === 0 || i <= freiBis() || altEingestuftOffen(i);" in html
    # Ein Reiter ist offen, wenn die Kette sein erstes Level erreicht - ein
    # angefangenes Level allein macht ihn nicht auf
    assert "(inDerKette(L[0]) ? 'offen' : 'zu')" in html
    assert "c.words.some(w => known.has(w.id))" in html
    assert "return i >= 0 && i < freiBis();" in html, "Zahlen im Satz: dieselbe Grenze"


def test_sprung_test_kostet_leben_und_merkt_sich_den_reiter(index_html):
    html = index_html.replace("\r\n", "\n")
    assert "const SPRUNG_FRAGEN = 15;" in html
    assert "const sprungNoetig = n => Math.ceil(n * EINSTUFUNG_QUOTE - 1e-9);" in html
    frage = _rumpf(html, "function sprungFrageZeigen(){")
    assert "loseLife();" in frage and "livesNow() === 0" in frage
    assert "topfMerken" not in frage and "karteiAntwort" not in frage and "zaehle(" not in frage, \
        "wie die Einstufung: kein Topf, keine Kartei, keine Tagesaufgaben"
    ende = _rumpf(html, "function sprungEnde(){")
    assert "wann['sp:' + ziel] = today()" in ende
    assert "passed.add" not in ende and "markToday" not in ende and "muenzen" not in ende
    start = _rumpf(html, "function sprungStarten(ziel){")
    assert "livesNow() === 0" in start, "ohne Leben kein Sprung-Test"
    # Pruefung vom 13.11.2026: ohne Leben dieselben Wege wie beim Level-Test, mit
    # eigenem Satz (nicht level.keine_leben mit der Grammatik-Erklaerung)
    assert "sprungLebenWege(" in start and "sprung.keine_leben" in start and "level.keine_leben" not in start
    assert "scrollIntoView" in start, "der Hinweis steht im Bild"
    wege = _rumpf(html, "function sprungLebenWege(kasten, vorn){")
    assert "werbungErlaubt(true)" in wege and "kaufe('herz')" in wege and "vollZeileLeben(" in wege
    ohne = _rumpf(html, "function sprungOhneLeben(){")
    assert "ohneleben" in ohne and "sprungLebenWege(" in ohne and "lektion.bis_naechstes" in ohne
    assert "istSprungAd(quelle)" in html and "else if(istSprungAd(knopf)) sprungLebenDa();" in html


def test_einstufung_mit_geteilten_saetzen(index_html):
    html = index_html.replace("\r\n", "\n")
    block = re.search(r"const EINSTUFUNG_STUFEN = \[(.*?)\];", html, re.S).group(1)
    sek = re.findall(r"sek:\[([^\]]*)\]", block)
    assert [re.findall(r"'(\w+)'", s) for s in sek] == [
        ["alltag"], ["anfassen", "tiernatur"], ["saetze"], ["zuhause2", "saetze2"], ["einkauf", "herkunft", "kultur"]]
    assert "haelfte" not in block


def test_grundwoerter_fuer_alte_einstufungen(index_html):
    """Pruefung vom 13.11.2026: Wer vor den Reitern eingestuft wurde, hatte die
    40 Grundwoerter noch in B1 vor sich; jetzt liegen sie davor. firstOpen()
    nimmt die zwei Grundwort-Level dann zuerst. Eine Einstufung mit den Reitern
    traegt das Feld "reiter" und bleibt beim Einstieg. Verhalten:
    tests_e2e/test_reiter.py."""
    html = index_html.replace("\r\n", "\n")
    assert "const GRUNDWORT_LEVEL = ['kleine_woerter', 'jeden_tag'];" in html
    assert "const vorDenReiternEingestuft = () => !!(einstufung && einstufung.bis && !einstufung.reiter);" in html
    erst = html.split("const firstOpen = () => {")[1].split("\n};\n")[0]
    assert "vorDenReiternEingestuft()" in erst and "k < ab && GRUNDWORT_LEVEL" in erst
    merken = _rumpf(html, "function einstufungMerken(wahl, bis, richtig, fragen){")
    assert "reiter: true" in merken
    # Zweite Pruefung vom 13.11.2026: bestandene Grundwort-Level zaehlen bei
    # alten Einstufungen nicht als "vor dem Einstieg bestanden", sonst sprang
    # Weitermachen danach auf Level 1. Der Weiter-Knopf nach dem Test geht
    # denselben Weg.
    ab = html.split("const dranAb = () => {")[1].split("\n};\n")[0]
    assert "!(alt && GRUNDWORT_LEVEL.indexOf(CATEGORIES[k].id) >= 0)" in ab
    assert "const ab = dranAb();" in erst
    weiter = _rumpf(html, "function naechstesOffenes(){")
    assert "vorDenReiternEingestuft() && GRUNDWORT_LEVEL.indexOf(cur().id) >= 0" in weiter
    assert "const f = firstOpen();" in weiter


def test_alte_einstufung_haelt_offen_was_sie_in_13_abdeckte(index_html):
    """Zweite Pruefung vom 13.11.2026: Stufe 2 der Einstufung von 1.3 fragte
    anfassen, tiernatur und zuhause2 ab; der Einstieg danach war "fragen".
    Seit Zuhause hinter Faelle 1 steht, haelt ALT_EINSTUFUNG_OFFEN es fuer
    diese alten Einstufungen offen. Nachgerechnet mit der Levelfolge von 1.3:
    nur dieser Einstieg hat etwas hinter sich verloren. Verhalten:
    tests_e2e/test_reiter.py."""
    html = index_html.replace("\r\n", "\n")
    assert "const ALT_EINSTUFUNG_OFFEN = {fragen: ['zuhause2']};" in html
    alt = html.split("const altEingestuftOffen = i => {")[1].split("\n};\n")[0]
    assert "vorDenReiternEingestuft()" in alt and "einstufung.bis" in alt
    frei = html.split("const freiBis = () => {\n")[1].split("\n};\n")[0]
    assert "while(altEingestuftOffen(n)) n++;" in frei, "nach Faelle 1 ist Faelle 2 offen"
    erst = html.split("const firstOpen = () => {")[1].split("\n};\n")[0]
    assert "!(ab > 0 && altEingestuftOffen(k))" in erst, "Weitermachen fuehrt nicht hinein"


def _levelfolge_13():
    """Die Levelfolge von 1.3 (v116), wie sie in data/vocabulary.json stand."""
    return ["basics", "zahlen", "farben", "familie", "essen", "wochentage", "monate", "zeit", "zuhause",
            "wetter", "koerper", "einkaufen", "unterwegs", "verben", "smalltalk", "obst", "gemuese",
            "lebensmittel", "vorrat", "tiere", "tiere_wild", "tiere_umgang", "natur", "kueche_bad", "putzen",
            "technik", "auto_werkstatt", "geraete", "fragen", "genus", "konjugation", "mehrzahl", "satzbau",
            "faelle1", "faelle2", "praepositionen", "faelle3", "faelle4", "vergangenheit", "zukunft", "modal",
            "reflexiv", "routine", "adjektive", "mengen", "gefuehle", "reisen", "feiern", "arbeit", "saetze",
            "einkauf_orte", "resto1", "resto2", "essen_gehen", "bosnisch_essen", "laender", "nationalitaeten",
            "kennenlernen", "kulturlevel", "formell"]


def test_alte_einstiege_gegen_die_levelfolge_von_13(grunddaten, index_html):
    """Fuer jeden Einstieg, den die Einstufung von 1.3 setzen konnte (obst,
    fragen, zukunft, einkauf_orte, formell): was damals davor lag und jetzt
    dahinter steht, muss in ALT_EINSTUFUNG_OFFEN stehen - sonst waere es
    nach dem Update wieder zu."""
    jetzt = [k["id"] for k in grunddaten["kategorien"]]
    sektion = {k["id"]: k["sektion"] for k in grunddaten["kategorien"]}
    alt = _levelfolge_13()
    tabelle = re.search(r"const ALT_EINSTUFUNG_OFFEN = \{(.*?)\};", index_html).group(1)
    assert tabelle == "fragen: ['zuhause2']"
    offen = {"fragen": {"zuhause2"}}
    for bis in ("obst", "fragen", "zukunft", "einkauf_orte", "formell"):
        davor = alt[:alt.index(bis)]
        verloren = {sektion[i] for i in davor if jetzt.index(i) > jetzt.index(bis)}
        assert verloren == offen.get(bis, set()), (bis, verloren)
