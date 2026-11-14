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
B5: Ćao ist auch „Hallo“ (F16) und stand neben Zdravo als falscher Knopf.
B9: „(Antwort darauf)“ als Bedeutung von Alejkumu selam verwies ins Leere.
B6: „nana (auch: metvica)“ trug das deutsche „auch“ im bosnischen Knopf.
S2: koleginica heisst kolegica (F19), als Wort, im Lueckensatz und im Satzbau.
V5: Hatte nur eines von zwei Woertern im selben Level eine Klammer („How are
you?“ neben „How are you? (formal)“), passte die Frage auf beide Knoepfe.
B7: Englische Lueckensaetze verlangten die Du-Form, „you“ passt aber auch auf
die Sie- und Ihr-Form.
S11 (Offen-Liste, Punkt 3): Der Lueckensatz „Gdje je moj ___?“ sagte
„Wechselgeld“, der Satzbau-Satz „Gdje je moj kusur?“ „Rückgeld“, und
WORTSCHATZ_KORREKTUREN.md (Richtiggestellt) nimmt Rückgeld. Jetzt auch der
Lueckensatz; er haengt an text und answer, die Kennung der Vokabel bleibt.
Die Tests im Browser stehen in tests_e2e/test_pruefbericht14_antworten.py und
tests_e2e/test_antworten.py (GESPERRT, TEIL_DER_FRAGE).
"""
import io
import json
import os
import re

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
    # Gezeigt und gesprochen wird weiter der Satz mit Merhaba. Ćao seit B5/F16
    # (tests/test_pruefbericht14_tippen.py), am Wort wie im Lueckensatz.
    assert s["answer"] == "Merhaba" and s["auch"] == ["Zdravo", "Ćao"], s
    merhaba = [w for w in _woerter(grunddaten).values() if w["bs"] == "Merhaba"]
    assert [w.get("auch") for w in merhaba] == [["Zdravo", "Ćao"]]


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


# B5: Ćao ist auch „Hallo“ (Ajdin, F16 ja) und stand als falscher Knopf neben
# „Hallo“, in 46 bis 57 von 400 Ziehungen. Bei Merhaba und seit dem 14.11.2026 auch bei
# Zdravo („Hallo (neutral, überall)“, Offen-Liste Punkt 2) zaehlt es beim Tippen ("auch",
# test_pruefbericht14_tippen.py); das haelt es auch aus der Auswahl (geschwister()). Ein
# Paar in NIE_NEBENEINANDER waere doppelt und sagte das Gegenteil - das fuer Zdravo, das
# bis dahin dort stand, ist darum raus.
def test_b5_cao_nie_neben_zdravo(index_html, grunddaten):
    nie = _nie_nebeneinander(index_html)
    assert ("Zdravo", "Ćao") not in nie and ("Merhaba", "Ćao") not in nie
    woerter = {w["bs"]: w for k in grunddaten["kategorien"] for w in k["words"]}
    # Im selben Level wie Ćao, dort zieht die Auswahl ihre falschen Knoepfe; das "auch"
    # des Worts haelt Ćao heraus.
    level = {w["bs"]: k["id"] for k in grunddaten["kategorien"] for w in k["words"]}
    assert level["Zdravo"] == level["Ćao"], level["Zdravo"]
    assert woerter["Zdravo"].get("auch") == ["Ćao"]


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


# B6 (F17 b, "ok"): Minze hiess "nana (auch: metvica)", mit dem deutschen "auch" im
# bosnischen Knopf, auch auf Englisch, Tuerkisch und Franzoesisch. Jetzt "nana / metvica"
# wie kahva / kafa. Die Kennung aendert sich und zieht ueber UMBENANNT mit.
B6_ALT, B6_NEU = "minze:nana (auch: metvica)", "minze:nana / metvica"


def test_b6_neue_kennung_und_umbenannt(alle_daten, index_html):
    assert "'%s': '%s'" % (B6_ALT, B6_NEU) in index_html
    for code, daten in alle_daten.items():
        woerter = _woerter(daten)
        assert B6_ALT not in woerter and woerter[B6_NEU]["bs"] == "nana / metvica", code
        # Kein bosnisches Wort traegt mehr einen Zusatz in Klammern.
        assert [w["bs"] for w in woerter.values() if "(" in w["bs"]] == [], code


def test_b6_ton_wie_kahva_kafa(wurzel):
    """Wie kahva / kafa gehoert zum Wort eine Aufnahme mit beiden Formen ("nana,
    metvica"). Die gibt es noch nicht, erzeugt wird sie nicht ohne Ajdin: bis dahin
    spielt audioDatei() die erste Form "nana" (w0089). ton_pruefen.py laesst die Luecke
    nur ueber NUR_ERSTE_FORM durch."""
    import ton_bauen
    import ton_pruefen
    with io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8") as f:
        toene = {t["key"]: t["datei"] for t in json.load(f)["toene"]}
    assert toene["kahva / kafa"] != toene["kahva"]
    assert toene["nana"] == "w0089.mp3"
    assert "nana / metvica" not in toene and "nana / metvica" not in ton_bauen.nur_emir()
    assert ton_pruefen.NUR_ERSTE_FORM == {"nana / metvica"}
    posten = [p for p in ton_bauen.sammle() if p["text"] == "nana / metvica"]
    assert [(p["key"], p.get("alle")) for p in posten] == [("nana / metvica", True)], posten


# S2 (F19): Ajdin „kolegica ist [richtig] nicht koleginica“, „ne sofort umstellen“. An
# allen drei Stellen kolegica: das Wort, der Lueckensatz und der Satzbau-Satz. Die Kennung
# des Worts und der Schluessel des Satzbau-Satzes ziehen ueber UMBENANNT und
# SAETZE_UMBENANNT mit; der Lueckensatz behaelt seinen Schluessel. Den Ton spricht Emir
# (tests/test_paket1020_ton.py). Die beiden anderen Saetze aus S2 bleiben, wie sie waren.
S2_ALT, S2_NEU = "kollegin:koleginica", "kollegin:kolegica"


def test_s2_kolegica_an_allen_stellen(alle_daten, index_html, wurzel):
    assert "'%s': '%s'" % (S2_ALT, S2_NEU) in index_html
    assert "'k:kennenlernen|Ovo je moja koleginica.': 'k:kennenlernen|Ovo je moja kolegica.'" in index_html
    for code, daten in alle_daten.items():
        woerter = _woerter(daten)
        assert S2_ALT not in woerter and woerter[S2_NEU]["bs"] == "kolegica", code
        luecke = [s for s in daten["saetze"] if s["kat"] == "kennenlernen" and s["text"] == "Ovo je moja ___."]
        assert [(s["answer"], s.get("auch")) for s in luecke] == [("kolegica", None)], (code, luecke)
        satz = [s for s in daten["satzbau"] if s["kat"] == "kennenlernen" and s["bs"].startswith("Ovo je moja kol")]
        assert [(s["bs"], s.get("auch")) for s in satz] == [("Ovo je moja kolegica.", None)], (code, satz)
    with io.open(os.path.join(wurzel, "vokabeln.py"), encoding="utf-8") as f:
        # Nur noch in Kommentaren (bis wann es so hiess), in keinem Eintrag.
        rest = [z for z in f if "koleginica" in z.split("#")[0]]
    assert rest == [], rest


def test_s2_die_anderen_saetze_bleiben(grunddaten):
    """F19 b und c gelten nicht: keine Umstellung „Plava je voda u jezeru“ oder „Pet godina
    ima moja sestra“."""
    satz = {s["bs"]: s for s in grunddaten["satzbau"]}
    assert satz["Voda u jezeru je plava"].get("auch") is None
    auch = satz["Moja sestra ima pet godina"].get("auch") or []
    assert not [a for a in auch if a.lower().startswith("pet godina ima")], auch


# V5: Bei vielen Paaren hatte nur eines der beiden Woerter eine Klammer. Die Frage
# ohne Klammer passte dann auf beide Knoepfe: auf Englisch stand bei „How are you?“
# (Kako si?) Kako ste mit „How are you? (formal)“ als falscher Knopf, in 185 von 400
# Ziehungen. Jetzt hat auch die andere Seite eine Klammer, nur in uebersetzungen.py;
# keine Kennung aendert sich, das Deutsche bleibt (AGENTS.md, Regel 1).
V5_NEU = {
    "en": {"Kako si?": "How are you? (informal)", "tebi / ti": "to you (singular)",
           "ćeš": "you will (singular)"},
    "tr": {"iznad": "üstünde (yukarıda)", "moram": "zorundayım", "prodavač": "satıcı (erkek)"},
    "sv": {"dijete": "barn (ett)"},
    "nl": {"ili": "of (keuze)", "za": "voor (ten behoeve van)"},
    "nb": {"dijete": "barn (ett)", "onda": "så (i tid)"},
    "da": {"otac": "far (formelt)", "onda": "så (i tid)"},
    "fr": {"Merhaba": "Salut (en arrivant)", "Dobar dan": "Bonjour (la journée)",
           "Gdje?": "Où (sans mouvement) ?"},
}


def _bed(s):
    """Wie _bedeutung in web/index.html: klein, Satzzeichen am Ende weg."""
    return re.sub(r"\s+", " ", re.sub(r"[.!?…]+$", "", str(s or "").lower())).strip()


def _ohne_klammer(s):
    """Je Form die Klammer(n) am Ende weg, wie TEIL_DER_FRAGE in tests_e2e/test_antworten.py."""
    return [_bed(re.sub(r"(\s*\([^)]*\))+(?=[\s.!?…]*$)", "", _bed(f))) for f in str(s).split(" / ")]


def _gesperrt(w, x, nie):
    """Was die App in der Auswahl ohnehin nie nebeneinander stellt (geschwister())."""
    formen = lambda s: [_bed(f) for f in str(s).split(" / ")]
    auch = lambda y: [f for a in (y.get("auch") or []) + (y.get("auch_var") or []) for f in formen(a)]
    return (_bed(w["de"]) == _bed(x["de"]) or (w["bs"], x["bs"]) in nie or (x["bs"], w["bs"]) in nie
            or x.get("partner") == w["bs"] or w.get("partner") == x["bs"]
            or set(formen(x["bs"])) & set(auch(w)) or set(formen(w["bs"])) & set(auch(x)))


def test_v5_neue_bedeutungen(alle_daten):
    for code, neu in V5_NEU.items():
        woerter = {}
        for k in alle_daten[code]["kategorien"]:
            for w in k["words"]:
                woerter.setdefault(w["bs"], []).append(w)
        for bs, de in neu.items():
            assert [w["de"] for w in woerter[bs] if w["id"].split(":")[0] in {
                "wie geht's dir?", "dir", "du wirst", "über / oberhalb", "ich muss", "verkäufer",
                "kind", "oder", "für", "dann", "vater", "hallo", "guten tag", "wo?"}] == [de], (code, bs)


def test_v5_kennungen_bleiben(grunddaten):
    kennungen = {w["id"] for k in grunddaten["kategorien"] for w in k["words"]}
    for kennung in ("wie geht's dir?:Kako si?", "dir:tebi / ti", "du wirst:ćeš", "über / oberhalb:iznad",
                    "ich muss:moram", "verkäufer:prodavač", "kind:dijete", "oder:ili", "für:za",
                    "dann:onda", "vater:otac", "hallo:Merhaba", "guten tag:Dobar dan", "wo?:Gdje?"):
        assert kennung in kennungen, kennung


def test_v5_woerterbuch_der_geschichten_bleibt(alle_daten):
    """za und onda bekommen ihre Klammer nur als Wort (woerter): in den Geschichten
    heisst za auch „pro“, „in“ und „an“ (za kilogram, za deset minuta, za stolom)."""
    assert alle_daten["nl"]["woerterbuch"]["za"] == "voor"
    assert alle_daten["nb"]["woerterbuch"]["onda"] == "så"
    assert alle_daten["da"]["woerterbuch"]["onda"] == "så"


def test_v5_keine_einseitige_klammer_im_selben_level(alle_daten, index_html):
    """Heisst die Frage ohne Klammer genau wie ein anderes Wort desselben Levels ohne
    seine Klammer am Ende, passt sie auf beide Knoepfe. Vorher 17 Paare in sieben
    Sprachen, jetzt keins. "sie sind" (oni su) neben "Sie sind" (vi ste) bleibt: die
    Grossschreibung trennt sie, genau das uebt das Level Konjugation."""
    nie = _nie_nebeneinander(index_html)
    rest = []
    for code, daten in alle_daten.items():
        for k in daten["kategorien"]:
            for w in k["words"]:
                frage = _bed(w["de"])
                for x in k["words"]:
                    if x["bs"] == w["bs"] or frage not in _ohne_klammer(x["de"]) or _gesperrt(w, x, nie):
                        continue
                    if {w["bs"], x["bs"]} != {"oni su", "vi ste"}:
                        rest.append((code, k["id"], w["bs"], w["de"], x["bs"], x["de"]))
    assert rest == []


# B7: "How are you?" bei „Kako ___?“ nahm nur si, ste war falsch, obwohl "you" beides
# sein kann. Ebenso bei radiš, imaš, Imaš, Možeš, te und Nedostaješ. Die en-Texte
# sagen jetzt "(informal)", wie „Kada ___ doći?“ schon "(singular, informal)". Die
# anderen Sprachen unterscheiden du und Sie selbst. Gleicher Text, gleiche
# Uebersetzung: auch das Wort und der Satzbau-Satz mit demselben Text bekommen es.
B7_LUECKEN = [("Kako ___?", "si"), ("Volim ___.", "te"), ("___ mi.", "Nedostaješ"),
              ("Šta ___?", "radiš"), ("Koliko ___ godina?", "imaš"), ("___ li vremena?", "Imaš"),
              ("___ li mi pomoći?", "Možeš"), ("Kada ___ doći?", "ćeš")]


def test_b7_englische_luecken_mit_du_form_sagen_informal(alle_daten):
    en = alle_daten["en"]
    for text, antwort in B7_LUECKEN:
        s = [x for x in en["saetze"] if x["text"] == text and x["answer"] == antwort]
        assert len(s) == 1, (text, antwort)
        assert re.search(r"\((singular, )?informal\)$", s[0]["de"]), s[0]
    # Die Sie-Form hat ihr "(formal)" schon, die beiden stehen nie gleich da.
    ste = [x for x in en["saetze"] if x["text"] == "Kako ___?" and x["answer"] == "ste"]
    assert [x["de"] for x in ste] == ["How are you? (formal)"]


def test_b7_andere_sprachen_unveraendert(alle_daten):
    for code in ("tr", "sv", "nl", "nb", "da", "fr"):
        for text, antwort in B7_LUECKEN:
            s = [x for x in alle_daten[code]["saetze"] if x["text"] == text and x["answer"] == antwort]
            assert len(s) == 1 and "informal" not in s[0]["de"], (code, s)


# ---------------------------------------------------------------------------
# S11: kusur heisst im Lueckensatz Rueckgeld, wie im Satzbau
# ---------------------------------------------------------------------------
# So steht der Satz in jeder Sprache da; Lueckensatz und Satzbau sagen dasselbe.
S11 = {"de": "Wo ist mein Rückgeld?", "en": "Where is my change?", "tr": "Para üstüm nerede?",
       "sv": "Var är min växel?", "nl": "Waar is mijn wisselgeld?", "nb": "Hvor er vekslepengene mine?",
       "da": "Hvor er mine byttepenge?", "fr": "Où est ma monnaie ?"}


def test_s11_kusur_ist_rueckgeld(alle_daten, wurzel):
    import uebersetzungen
    assert set(alle_daten) == set(S11)
    for code, daten in alle_daten.items():
        luecke = [s for s in daten["saetze"] if s["text"] == "Gdje je moj ___?" and s["answer"] == "kusur"]
        satzbau = [s for s in daten["satzbau"] if s["bs"] == "Gdje je moj kusur?"]
        assert len(luecke) == 1 and len(satzbau) == 1, code
        assert luecke[0]["de"] == satzbau[0]["de"] == S11[code], (code, luecke[0]["de"], satzbau[0]["de"])
    # Der alte deutsche Schluessel ist in keiner Sprache mehr uebrig.
    for code, tabelle in uebersetzungen.INHALT.items():
        assert "Wo ist mein Wechselgeld?" not in tabelle["texte"], code
    with io.open(os.path.join(wurzel, "WORTSCHATZ_KORREKTUREN.md"), encoding="utf-8") as f:
        assert "| *kusur* | „Wechselgeld\" | **Rückgeld.**" in f.read()


def test_s11_kennung_der_vokabel_bleibt(grunddaten):
    """Nur die Anzeige des Satzes aendert sich. Die Vokabel kusur behaelt ihr
    de "Wechselgeld / Rückgeld" und damit ihre Kennung."""
    woerter = [w for k in grunddaten["kategorien"] for w in k["words"] if w["bs"] == "kusur"]
    assert [w["id"] for w in woerter] == ["wechselgeld / rückgeld:kusur"]
