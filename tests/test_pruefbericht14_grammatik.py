# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026): Grammatik-Lektionen.

V12 (F8 ja, "ja ist genitiv"): In der Lektion Praepositionen standen iznad,
ispod und između in der Zeile Instrumental. Die App benutzt danach ueberall
den Genitiv („ispod stola“, „iznad grada“, „između tebe i brata“), das
Beispiel „između kuća“ passte nur zufaellig (Genitiv Mehrzahl). Jetzt stehen
die drei beim Genitiv, mit dem Beispiel „ispod stola, između kuće i škole“.
Die Uebung „Sjedim ___ tebe i brata.“ ist Genitiv und passt jetzt zur Tabelle.

S4 (F21 ja): Die Instrumental-Regel sagte „-em nur nach j, č, š, ž“, die App
schreibt aber auch čekićem und želucem. Jetzt: nach c, č, ć, dž, đ, j, lj, nj,
š, ž + em, in allen 8 Sprachen.

S6 (Offen-Liste, Punkt 3): „Svoj“ hiess in der Lektion Faelle 1 nur „mein
eigener“, im Woerterbuch der Lesetexte „eigener (mein, dein, sein)“, obwohl in
b1_voz und b1_telefon eine Frau „svoj broj“ hat. Jetzt „der eigene (mein, dein,
sein, ihr …), wenn der Besitzer das Subjekt ist“, in 8 Sprachen. Die Vokabel
behaelt ihr de, das ist ihre Kennung.

S8 (Offen-Liste, Punkt 3): In der Lektion Zukunft stand „ću + Infinitiv“ in
uebersetzungen.GLEICH und blieb in jeder Sprache deutsch. Jetzt uebersetzt
(infinitive, mastar, infinitif, infinitief, infinitiv).
"""

S4_BUCHSTABEN = "c, č, ć, dž, đ, j, lj, nj, š, ž"
S4_IN_SPRACHE = {
    "de": "nach ", "en": "after ", "sv": "efter ", "da": "efter ",
    "nb": "etter ", "nl": "na ", "fr": "après ", "tr": "",
}


def _tabelle(lektion):
    for teil in lektion["erklaerung"]:
        if isinstance(teil, dict) and "tabelle" in teil:
            return teil["tabelle"]
    raise AssertionError("keine Tabelle")


def _zeile(tabelle, fall):
    zeilen = [z for z in tabelle if z[0] == fall]
    assert len(zeilen) == 1, (fall, tabelle)
    return zeilen[0]


def test_v12_iznad_ispod_izmedju_beim_genitiv(grunddaten):
    tabelle = _tabelle(grunddaten["grammatik"]["praepositionen"])
    genitiv = _zeile(tabelle, "Genitiv")
    instrumental = _zeile(tabelle, "Instrumental")
    praep_gen = [p.strip() for p in genitiv[1].split(",")]
    praep_ins = [p.strip() for p in instrumental[1].split(",")]
    for p in ("iznad", "ispod", "između"):
        assert p in praep_gen, (p, genitiv)
        assert p not in praep_ins, (p, instrumental)
    assert "ispod stola, između kuće i škole" in genitiv[2], genitiv
    assert "između" not in instrumental[2], instrumental
    # Was beim Instrumental war, bleibt dort; nad und među kamen am 15.11.2026 dazu (unten).
    assert praep_ins == ["s/sa", "pod", "nad", "pred", "za (hinter)", "među"], instrumental
    assert instrumental[2] == "s bratom, pod stolom", instrumental


def test_v12_in_jeder_sprache(alle_daten, grunddaten):
    vorlage = _tabelle(grunddaten["grammatik"]["praepositionen"])
    for code, daten in alle_daten.items():
        tabelle = _tabelle(daten["grammatik"]["praepositionen"])
        # Genitiv-Zeile und Beispiele sind bosnisch und stehen ueberall gleich da.
        assert tabelle[1][1:] == vorlage[1][1:], code
        instrumental = tabelle[-1][1]
        for p in ("iznad", "ispod", "između"):
            assert p not in instrumental, (code, instrumental)
        if code != "de":
            # Die Zelle ist uebersetzt ("za (behind)"), kein deutscher Rest.
            assert "hinter" not in instrumental, (code, instrumental)
            assert instrumental.startswith("sa, pod, nad, pred, za ("), (code, instrumental)


# ---------------------------------------------------------------------------
# Frage 10 (Release\Fragen_Ajdin_2026-11-15.md, Ajdin 15.11.2026 abends, „10 ja“)
# ---------------------------------------------------------------------------
# Beim Instrumental standen nur „s/sa, pod, pred, za (hinter)“. nad (über) und među
# (zwischen) kommen dazu, das Beispiel „s bratom, pod stolom“ bleibt.
FRAGE10_HINTER = {"de": "hinter", "en": "behind", "tr": "arkasında", "sv": "bakom", "nl": "achter",
                  "nb": "bak", "da": "bag", "fr": "derrière"}


def test_frage10_nad_und_medju_beim_instrumental(alle_daten):
    assert set(alle_daten) == set(FRAGE10_HINTER), sorted(alle_daten)
    for code, daten in alle_daten.items():
        tabelle = _tabelle(daten["grammatik"]["praepositionen"])
        instrumental = tabelle[-1]
        anfang = "s/sa" if code == "de" else "sa"           # die Übersetzungen schreiben seit jeher „sa“
        assert instrumental[1] == "%s, pod, nad, pred, za (%s), među" % (anfang, FRAGE10_HINTER[code]), code
        assert instrumental[2] == "s bratom, pod stolom", code
        # Genitiv behält iznad und između, die Zeile Instrumental steht nur einmal da.
        assert "iznad" in tabelle[1][1] and "između" in tabelle[1][1], code
        assert [z for z in tabelle if "među" in z[1] and "između" not in z[1]] == [instrumental], code


def test_v12_uebung_zwischen_passt(grunddaten):
    uebungen = [u for u in grunddaten["grammatik"]["praepositionen"]["uebungen"]
                if u["frage"].startswith("„Sjedim ___ tebe i brata.“")]
    assert len(uebungen) == 1, uebungen
    assert uebungen[0]["richtig"] == "između"


def test_s4_instrumental_em_nach_allen_weichen_lauten(alle_daten, grunddaten):
    assert set(alle_daten) == set(S4_IN_SPRACHE), sorted(alle_daten)
    for code, daten in alle_daten.items():
        tabelle = _tabelle(daten["grammatik"]["faelle4"])
        regel = tabelle[1][3]
        assert (S4_IN_SPRACHE[code] + S4_BUCHSTABEN) in regel, (code, regel)
        assert "prijateljem" in regel and "+ om" in regel, (code, regel)
        assert "nach" not in regel or code == "de", (code, regel)
    # Die Woerter aus dem Bericht, die die Regel vorher nicht erklaerte
    # (b1_zanat „kuca čekićem“, „Imam tegobe sa želucem.“).
    import json
    alles = json.dumps(grunddaten, ensure_ascii=False)
    assert "čekićem" in alles and "želucem" in alles


# ---------------------------------------------------------------------------
# Vokativ: + u nach allen weichen Lauten (dritte Runde, 14.11.2026 abends)
# ---------------------------------------------------------------------------
# Die Regel nannte nur „nach j, č, š, ž + u (prijatelju!)“. Ajdin: ć, lj, nj, đ, dž
# dazuschreiben, „Ja“ - so wie im Clip 41 Zmajevi (Release\Clips_2026-11-13\41_Zmajevi\
# storyboard.md): mladić → mladiću, prijatelj → prijatelju.
VOKATIV_BUCHSTABEN = "ć, č, j, lj, nj, š, ž, đ, dž"
VOKATIV_IN_SPRACHE = {
    "de": "nach {} + u", "en": "after {} it adds -u", "tr": "{} harflerinden sonra + u gelir",
    "sv": "efter {} blir det + u", "nl": "na {} wordt het + u", "nb": "etter {} blir det + u",
    "da": "efter {} bliver det + u", "fr": "après {} + u",
}


def _vokativ(daten):
    saetze = [t for t in daten["grammatik"]["faelle4"]["erklaerung"]
              if isinstance(t, str) and "(brate!, gospodine!, sine!)" in t]
    assert len(saetze) == 1, saetze
    return saetze[0]


def test_vokativ_u_nach_allen_weichen_lauten(alle_daten):
    assert set(alle_daten) == set(VOKATIV_IN_SPRACHE), sorted(alle_daten)
    for code, daten in alle_daten.items():
        regel = _vokativ(daten)
        assert VOKATIV_IN_SPRACHE[code].format(VOKATIV_BUCHSTABEN) in regel, (code, regel)
        assert "(mladiću!, prijatelju!)" in regel, (code, regel)
        assert "j, č, š, ž" not in regel, (code, regel)
        assert "nach" not in regel or code == "de", (code, regel)       # kein deutscher Rest
    # Die Uebung dazu bleibt: prijatelju! ist richtig, prijatelje! falsch.
    for code, daten in alle_daten.items():
        freund = [u for u in daten["grammatik"]["faelle4"]["uebungen"] if u["richtig"] == "prijatelju!"]
        assert len(freund) == 1 and freund[0]["optionen"] == ["prijatelje!", "prijatelju!", "prijatelja!"], code


# ---------------------------------------------------------------------------
# S6: svoj ist nicht nur "mein eigener" (Offen-Liste, Punkt 3, 14.11.2026)
# ---------------------------------------------------------------------------
# Die Lektion Faelle 1 und das Woerterbuch der Lesetexte sagten "mein eigener"
# bzw. "eigener (mein, dein, sein)". In b1_voz gibt die Frau "svoj broj" (ihre
# Nummer), in b1_telefon schreibt Amina "na svoj broj" (an ihre eigene).
S6_LEKTION = "„Svoj“ heißt „der eigene“ (mein, dein, sein, ihr …) und wird benutzt, wenn der Besitzer das Subjekt ist."
S6_WB = "eigener (mein, dein, sein, ihr …)"
S6_KENNUNG = "eigener (mein, dein, sein):svoj"
S6_ENGLISCH = ("“Svoj” means “one's own” (my, your, his, her …) and is used when the owner is the subject",
               "one's own (my, your, his, her …)")


def _faelle1_svoj(daten):
    saetze = [t for t in daten["grammatik"]["faelle1"]["erklaerung"]
              if isinstance(t, str) and "Volim svoju majku" in t]
    assert len(saetze) == 1, saetze
    return saetze[0]


def test_s6_lektion_der_eigene(alle_daten):
    de = _faelle1_svoj(alle_daten["de"])
    assert S6_LEKTION in de and "mein eigener" not in de
    for code, daten in alle_daten.items():
        if code == "de":
            continue
        satz = _faelle1_svoj(daten)
        assert satz != de and "Svoj" in satz and "…" in satz, (code, satz)
        assert "eigen" not in satz or code == "nl", (code, satz)      # kein deutscher Rest
    assert S6_ENGLISCH[0] in _faelle1_svoj(alle_daten["en"])


def test_s6_woerterbuch_nicht_nur_mein(alle_daten):
    de = alle_daten["de"]
    assert de["woerterbuch"]["svoj"] == S6_WB
    texte = {g["id"]: g["text"] for g in de["geschichten"]}
    assert "Žena im daje svoj broj telefona." in texte["b1_voz"]
    assert "napisala poruku na svoj broj" in texte["b1_telefon"]
    for code, daten in alle_daten.items():
        if code != "de":
            assert daten["woerterbuch"]["svoj"] not in (S6_WB, ""), code
    assert alle_daten["en"]["woerterbuch"]["svoj"] == S6_ENGLISCH[1]


def test_s6_kennung_der_vokabel_bleibt(alle_daten):
    """Das de der Vokabel svoj ist ihre Kennung (AGENTS.md, Regel 1), es bleibt."""
    woerter = {w["id"]: w for k in alle_daten["de"]["kategorien"] for w in k["words"]}
    assert woerter[S6_KENNUNG]["de"] == "eigener (mein, dein, sein)"
    en = {w["id"]: w for k in alle_daten["en"]["kategorien"] for w in k["words"]}
    assert en[S6_KENNUNG]["de"] == "one's own (my, your, his)"


# ---------------------------------------------------------------------------
# S8: "ću + Infinitiv" in der Lektion Zukunft (Offen-Liste, Punkt 3)
# ---------------------------------------------------------------------------
# Die Zelle stand in uebersetzungen.GLEICH und blieb in jeder Sprache deutsch.
S8 = {"de": "ću + Infinitiv", "en": "ću + infinitive", "tr": "ću + mastar", "fr": "ću + infinitif",
      "nl": "ću + infinitief", "sv": "ću + infinitiv", "nb": "ću + infinitiv", "da": "ću + infinitiv"}


def test_s8_cu_infinitiv_uebersetzt(alle_daten, grunddaten):
    import uebersetzungen
    assert "ću + Infinitiv" not in uebersetzungen.GLEICH
    vorlage = _tabelle(grunddaten["grammatik"]["zukunft"])
    assert vorlage[1][:2] == ["ich", "ću + Infinitiv"]
    assert set(alle_daten) == set(S8)
    for code, daten in alle_daten.items():
        tabelle = _tabelle(daten["grammatik"]["zukunft"])
        assert tabelle[1][1] == S8[code], (code, tabelle[1])
        # Die anderen Formen und die Beispiele sind bosnisch und bleiben.
        assert [z[1] for z in tabelle[2:]] == [z[1] for z in vorlage[2:]], code
        assert [z[2] for z in tabelle[1:]] == [z[2] for z in vorlage[1:]], code
