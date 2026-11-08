# -*- coding: utf-8 -*-
"""Der versteckte Teil Beim Zahnarzt (06.11.2026): der Inhalt.

Eine Zahnaerztin will mit Patienten reden koennen, die nur Bosnisch
sprechen. Bosnisch und Deutsch stehen genau so in Release\\Wortschatz\\paket_zahnarzt.json,
von Ajdin am 06.11.2026 durchgesehen. Hier steht, was beim Einbau festgelegt wurde:

- 64 Eintraege, je Wort und Satz (127 Eintraege, "Ja sam stomatologinja ..." ist
  nur einer). 8 davon warteten auf Emir (v111_wartet_auf_emir.md) und stehen seit dem
  07.11.2026 an ihrer Stelle; ihr Ton kommt im eigenen Schritt (tests/offen_p1020.json);
- aus Sicht der Aerztin, Vi, Vas und Vam gross;
- er zaehlt nirgends mit: nicht in KATEGORIEN, nicht im Datensatz;
- die Kennung ist ZA_VORN + bs, ohne Doppelpunkt, siehe zahnarzt.py;
- Emir: w5206 bis w5316, in der Reihenfolge der Datei.

Wie die App damit umgeht, prueft tests_e2e/test_zahnarzt.py.
"""
import io
import os
import re

import pytest

import offen_p1020

ERSTE, LETZTE = 5206, 5316
SPRACHEN = ("en", "tr", "sv", "nl", "nb", "da", "fr")

# Die Woerter je Level ohne die Beispielsaetze, Bosnisch genau so, wie Ajdin es
# freigegeben hat. Aendert sich hier etwas, beginnt das Wort von vorn.
WOERTER = {
    "za|zaehne": ["zubar / stomatolog", "vilica", "živac", "kutnjak", "sjekutić", "očnjak", "umnjak",
                  "mliječni zub", "korijen zuba", "zubno meso"],
    "za|befund": ["karijes", "rupa u zubu", "plomba", "privremena plomba", "zubni most", "zubna proteza",
                  "zubni implantat", "vađenje zuba"],
    "za|behandlung": ["zubni kamenac", "upala desni", "anestezija", "rendgenski snimak", "otisak zuba",
                      "izbjeljivanje zuba", "zubni konac", "navlaka", "liječenje kanala", "aparat za zube", "otok"],
    "za|anweisungen": ["Otvorite usta.", "Zatvorite usta.", "Zagrizite.", "Isperite usta.", "Naslonite glavu.",
                       "Dišite kroz nos.", "Opustite se.", "Ne bojte se.", "Podignite ruku ako Vas zaboli.",
                       "Otvorite usta malo šire.", "Neće boliti."],
    "za|fragen": ["Da li Vas boli ovdje?", "Koji zub Vas boli?", "Od kada Vas boli?", "Da li Vas boli kad zagrizete?",
                  "Da li je osjetljiv na hladno?", "Da li ste alergični na neki lijek?", "Da li ste trudni?",
                  "Kada ste zadnji put bili kod zubara?"],
    "za|erklaeren": ["Imate karijes.", "Treba Vam plomba.", "Moramo napraviti snimak.", "Dat ću Vam injekciju.",
                     "Dva sata nemojte jesti.", "Dođite na kontrolu za sedmicu dana.",
                     "Zub se mora vaditi.", "Ja sam stomatologinja, kako Vam mogu pomoći?"],
    "za|patienten": ["Boli me zub.", "Boli me kad jedem.", "Ispala mi je plomba.", "Slomio mi se zub.",
                     "Krvare mi desni.", "Otekao mi je obraz.", "Noću ne mogu spavati od bolova.", "Bojim se zubara."],
}
# Warteten auf Emir, Wort und Satz (Release\\Wortschatz\\v111_wartet_auf_emir.md), seit dem
# 07.11.2026 an ihrer Stelle. Ihr Ton fehlt bis zum Ton-Schritt (tests/offen_p1020.json).
WARTET = []
NACHGEKOMMEN = ["zubno meso", "Zubno meso Vam je malo upaljeno.", "navlaka", "Na ovaj zub ide navlaka.",
          "liječenje kanala", "Ovom zubu treba liječenje kanala.", "aparat za zube",
          "Moja kćerka nosi aparat za zube.", "otok", "Otok će proći za nekoliko dana.",
          "Otvorite usta malo šire.", "Otvorite usta malo šire, ne vidim dobro.", "Neće boliti.",
          "Neće boliti, dobit ćete injekciju.", "Zub se mora vaditi.", "Žao mi je, zub se mora vaditi."]
AUCH = {"zubar / stomatolog": ["stomatologinja", "zubarka"], "plomba": ["ispun"],
        "zubno meso": ["desni"], "navlaka": ["krunica", "zubna krunica"],
        "liječenje kanala": ["liječenje korijenskih kanala"], "otok": ["oteklina"], "Neće boliti.": ["Neće boljeti."]}
NUR_EIN_EINTRAG = "Ja sam stomatologinja, kako Vam mogu pomoći?"


@pytest.fixture(scope="module")
def teil():
    import zahnarzt
    return zahnarzt


def _alle(teil):
    return [w for k in teil.KATEGORIEN for w in k["words"]]


def test_level_und_woerter_genau_wie_freigegeben(teil):
    assert [k["id"] for k in teil.KATEGORIEN] == list(WOERTER)
    for k in teil.KATEGORIEN:
        woerter = [w["bs"] for w in k["words"]]
        # Jedes Wort direkt vor seinem Beispielsatz, deshalb jedes zweite.
        assert woerter[::2] == WOERTER[k["id"]], k["id"]
        assert k["sektion"] == teil.SEKTION["id"] and k["reihenfolge"] is True, k["id"]
        # Mit den Nachzueglern vom 07.11.2026 an ihrer Stelle haben zwei Level 22 Eintraege
        assert 2 <= len(k["words"]) <= 22, (k["id"], len(k["words"]))
    erklaeren = [w["bs"] for k in teil.KATEGORIEN if k["id"] == "za|erklaeren" for w in k["words"]]
    assert erklaeren[-1] == NUR_EIN_EINTRAG and erklaeren.count(NUR_EIN_EINTRAG) == 1
    assert len(_alle(teil)) == 127


def test_was_auf_emir_wartet_steht_nicht_drin(teil):
    bs = {w["bs"] for w in _alle(teil)}
    assert not bs & set(WARTET), bs & set(WARTET)


def test_kennung_eindeutig_und_ohne_doppelpunkt(teil):
    bs = [w["bs"] for w in _alle(teil)]
    assert len(set(bs)) == len(bs)
    assert not [b for b in bs if ":" in b]
    assert teil.ZA_VORN == "za|"


def test_anrede_mit_vi_gross(teil):
    klein = [w["bs"] for w in _alle(teil) if re.search(r"(?<![^\W\d_])(vi|vas|vam)(?![^\W\d_])", w["bs"])]
    assert not klein, klein
    gross = [w["bs"] for w in _alle(teil) if re.search(r"\b(Vas|Vam)\b", w["bs"])]
    assert len(gross) >= 10, gross


def test_auch_nur_wie_freigegeben(teil):
    assert {w["bs"]: w["auch"] for w in _alle(teil) if w.get("auch")} == AUCH


def test_fuer_die_app_eigenes_feld_und_keine_zaehlung(grunddaten):
    assert len(grunddaten["sektionen"]) == 31
    assert len(grunddaten["kategorien"]) == 295
    z = grunddaten["zahnarzt"]
    assert z["sektion"]["id"] == "zahnarzt" and len(z["kategorien"]) == 7
    assert all(k["id"].startswith("za|") for k in z["kategorien"])
    normal = {w["id"] for k in grunddaten["kategorien"] for w in k["words"]}
    versteckt = [w["id"] for k in z["kategorien"] for w in k["words"]]
    assert all(i.startswith("za|") and ":" not in i for i in versteckt)
    assert not normal & set(versteckt)
    assert not [k for k in grunddaten["kategorien"] if k.get("sektion") == "zahnarzt"]


def test_nicht_im_datensatz(wurzel):
    with io.open(os.path.join(wurzel, "data", "parallel.jsonl"), encoding="utf-8") as f:
        text = f.read()
    for bs in ("Imate upalu živca u ovom zubu.", "Dišite kroz nos, samo polako.", "stomatologinja"):
        assert bs not in text, bs


@pytest.mark.parametrize("code", SPRACHEN)
def test_uebersetzt_und_bosnisch_bleibt(code, teil):
    import inhalt
    fertig = inhalt.zahnarzt_fuer_app(code)
    deutsch = inhalt.zahnarzt_fuer_app("de")
    assert fertig["sektion"]["label"] != deutsch["sektion"]["label"]
    assert fertig["sektion"]["beschreibung"] != deutsch["sektion"]["beschreibung"]
    fehlt = []
    for k, d in zip(fertig["kategorien"], deutsch["kategorien"]):
        if k["label"] == d["label"] or k["tipp"] == d["tipp"]:
            fehlt.append(d["label"])
        for w, x in zip(k["words"], d["words"]):
            assert w["bs"] == x["bs"] and w["id"] == x["id"], w
            if w["de"] == x["de"]:
                fehlt.append(x["de"])
    assert not fehlt, fehlt


def test_ton_lueckenlos_in_der_reihenfolge_der_datei(teil):
    import ton_bauen
    emir = ton_bauen.nur_emir()
    neu = sorted((e["datei"], k, e["text"]) for k, e in emir.items() if ERSTE <= int(e["datei"][1:5]) <= LETZTE)
    assert [n[0] for n in neu] == ["w%04d.mp3" % n for n in range(ERSTE, LETZTE + 1)]
    nach = set(NACHGEKOMMEN)
    assert [n[2] for n in neu] == [w["bs"] for w in _alle(teil) if w["bs"] not in nach]
    for _, k, text in neu:
        assert k == (ton_bauen.schluessel_alle(text) if " / " in text else ton_bauen.schluessel(text))
    # Dahinter seit dem 07.11.2026 die Pakete 10 bis 20 und die Nachzuegler; was davon noch
    # keinen Ton hat, steht in tests/offen_p1020.json
    for w in _alle(teil):
        if w["bs"] in nach:
            k = ton_bauen.schluessel(w["bs"])
            assert k in offen_p1020.TON or int(emir[k]["datei"][1:5]) > LETZTE, w["bs"]
    # zubar / stomatolog: dazu die erste Form aus der App, sie hat ihre eigene Aufnahme
    posten = {p["key"] for p in ton_bauen.sammle()}
    assert "zubar / stomatolog" in posten and "zubar" in posten


def test_codewort_vor_der_vollversion_und_pruefung_unveraendert(index_html):
    html = index_html.replace("\r\n", "\n")
    assert "const ZA_WORT = 'zahnarzt'" in html
    # Das Wort zweigt ab, bevor dauerWortStimmt() es sieht - und die Pruefung bleibt, wie sie war.
    assert ("    if(w === ZA_WORT){ await zaUmschalten(); return; }\n"
            "    if(!(await dauerWortStimmt(w))) return;\n") in html
    assert "const DAUER_PRUEFWERT = '__DAUER_PRUEFWERT__';\n" in html
    assert "if(!/^[0-9a-f]{64}$/.test(DAUER_PRUEFWERT)) return false;\n" in html
    start = html.index("async function zaUmschalten(){")
    koerper = html[start:html.index("function dauerVollVerdrahten(){")]
    for wort in ("dauerVoll", "premium", "DAUER_", "zmaj_voll", "hautAlle"):
        assert wort not in koerper, wort
