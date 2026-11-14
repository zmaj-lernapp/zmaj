# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026): Geschichten.

B10: Beim Antippen zeigte das Woerterbuch der Lesetexte teils die falsche
Bedeutung. ti stand als "du", in den B1-Texten heisst es aber jedes Mal
"dir" ("Ako ti bilo šta treba"). kad stand als "als / wenn", gemeint ist
auch "wann" ("Babo, kad idemo opet?", "pita kad dolazim"). vam stand als
"Ihnen", an vier Stellen ist "euch" gemeint ("Ako vam nešto zatreba" zu den
Kindern im Zug). je stand ueberall als "ist", in vier Texten heisst es auch
"sie (Akk.)" ("Direktor je pita"); das steht wie bei smije in den vokabeln
der Geschichte, die vor dem WOERTERBUCH gelten. Acht Woerter hatten die
Bedeutung der Vokabel mit allen Geschlechtern ("zufrieden (m/w)") oder dem
falschen ("važna": "wichtig (der wichtige)"), im Text steht aber genau eine
Form. Sie haben jetzt eigene Texte nur im WOERTERBUCH. Das de der Vokabel
bleibt, sonst aenderte sich die Kennung und mit ihr der Lernstand (AGENTS.md,
Regel 1).

B12: "Passt zu Level" in der Liste und oben in der Geschichte zeigte bei
sieben B1-Geschichten auf ein B2-Level, das B1-Lernende meist noch nicht offen
haben (b1_stan auf "Wohnen und Miete"). Jetzt auf ein Level bis B1 mit
demselben Thema. Die Freischaltung haengt nicht daran.

V13 a: b1_struja sagte "Hasan je imao plinski štednjak". Der Herd heisst in
der App šporet, štednjak steht als kroatisch. Ajdin (F9 a): "stednjak/sporet
ist herd aber plinski sporet ist gasherd". Jetzt "plinski šporet", im
WOERTERBUCH šporet statt štednjak; die Uebersetzung bleibt "Gasherd".

S3: Im Brief an die Nana stand "Nadam se da ćeš nam skuhati pitu!". Ajdin
(F20): "man sagt napraviti pitu nicht skuhati". Jetzt "napraviti pitu", auf
Deutsch "eine Pita machst" wie schon in den anderen sieben Sprachen ("make
us a pita"). skuhati steht in keinem Text mehr und ist aus dem WOERTERBUCH
raus, napraviti ("machen / zubereiten") stand schon drin. Der Ton von pismo
(g09) gehoert zum alten Text; die Geschichte wartet in tests/offen_b1_teil2.py
auf die naechste Vesna-Runde, die Datei bleibt liegen.

S7: Vi, Vas, Vam standen mal gross, mal klein. Ajdin (F23): gross in
Geschriebenem an eine Person, klein in Gespraechen der Erzaehlung, der
Zahnarzt-Teil bleibt gross. Klein jetzt auch in b1_posao (die Chefin zu Haris,
mit vašu) und b1_stan (Telefonat); gross bleibt die Nachricht in b1_telefon.
Der Ton-Schluessel ist kleingeschrieben und bleibt (ton_bauen.schluessel).

Der Text der Geschichten ist ihr Ton-Schluessel (ton_bauen.py). Er aendert
sich nur, wo Ajdin es entschieden hat; test_text_der_geschichten_bleibt haelt
jeden Stand fest. Die Tests im Browser stehen in
tests_e2e/test_pruefbericht14_geschichten.py.
"""
import hashlib
import re

import pytest

SPRACHEN = ["en", "tr", "sv", "nl", "nb", "da", "fr"]

KLEINE_WOERTER = {
    "ti": "du / dir",
    "kad": "als / wenn / wann",
    "vam": "Ihnen / euch",
}

# Geschichte -> Stelle, an der je "sie (Akk.)" heisst
JE_AKKUSATIV = {
    "intervju": "Direktor je pita",
    "b1_ljeto": "Kad je zagrlim",
    "b1_voz": "sama sam je pekla",
    "b1_zanat": "Nemojte je samo držati",
}
JE = "ist / sie (Akk.)"

# Wort -> (Bedeutung im WOERTERBUCH, Geschichte, Stelle im Text, Kennung der Vokabel)
GESCHLECHT = {
    "zadovoljan": ("zufrieden (m)", "b1_vrijeme", "Mali Dino nije zadovoljan",
                   "zufrieden (m/w):zadovoljan / zadovoljna"),
    "zdrav": ("gesund (m)", "b1_doktor", "Amar je opet bio zdrav", "gesund (m/w):zdrav / zdrava"),
    "tužan": ("traurig (m)", "b1_rodjendan", "Haris je bio malo tužan", "traurig (m/w):tužan / tužna"),
    "vaš": ("euer / Ihr (m)", "b1_telefon", "Vaš telefon", "euer / ihr (m/w/s):vaš / vaša / vaše"),
    "važna": ("wichtig (w)", "b1_utakmica", "važna utakmica", "wichtig (der wichtige):važan"),
    "njena": ("ihre (von ihr, w)", "b1_zmaj", "njena sarma", "ihr (von ihr) (m/w/s):njen / njena / njeno"),
    "doktorica": ("Ärztin", "b1_doktor", "doktorica ga je pitala", "arzt / ärztin:doktor / doktorica"),
    "svoja": ("eigene (Mehrz.)", "b1_kahva", "svoja pravila", "eigener (mein, dein, sein):svoj"),
}

# Stichprobe: so heissen die neuen Texte auf Englisch
ENGLISCH = {
    "ti": "you / to you",
    "kad": "when",
    "vam": "to you (formal or plural)",
    "zadovoljan": "content (m)",
    "važna": "important (f)",
    "doktorica": "doctor (f)",
    "svoja": "own (pl.)",
}

# sha256 ueber alle Geschichtentexte am 14.11.2026. B10 und B12 liessen sie
# unveraendert (11df97e6…), seit V13 a steht in b1_struja "plinski šporet"
# (526d6a03…), seit S3 in pismo "napraviti pitu" (b8c9980c…), seit S7 "vam"
# klein in den Gespraechen von b1_posao und b1_stan.
TEXTE_SHA256 = "46d9367108436a5c4032be50bd182df7c3b830096ae201e7c984015289b3f7cc"


def _geschichten(daten):
    return {g["id"]: g for g in daten["geschichten"]}


def _woerter(daten):
    return {w["id"]: w for k in daten["kategorien"] for w in k["words"]}


def test_text_der_geschichten_bleibt():
    """Jede Aenderung an Woertern oder Kommas kostet neuen Ton (ton_bauen.py)."""
    import geschichten
    texte = "\n\x00".join(g["text"] for g in geschichten.GESCHICHTEN)
    assert hashlib.sha256(texte.encode("utf-8")).hexdigest() == TEXTE_SHA256


def test_b10_ti_kad_vam(grunddaten):
    wb = grunddaten["woerterbuch"]
    for wort, bedeutung in KLEINE_WOERTER.items():
        assert wb[wort] == bedeutung, wort


@pytest.mark.parametrize("wort,stelle,gid", [
    ("ti", "Ako ti bilo šta treba", "b1_posao"),
    ("kad", "Babo, kad idemo opet?", "b1_utakmica"),
    ("vam", "Ako vam nešto zatreba", "b1_voz"),
])
def test_b10_die_stellen_aus_dem_bericht(grunddaten, wort, stelle, gid):
    """Die Geschichte hat fuer diese Woerter keine eigene Bedeutung, es gilt
    das WOERTERBUCH."""
    g = _geschichten(grunddaten)[gid]
    assert stelle in g["text"]
    assert wort not in (g.get("vokabeln") or {})


def test_b10_je_in_vier_geschichten(grunddaten):
    g = _geschichten(grunddaten)
    for gid, stelle in JE_AKKUSATIV.items():
        assert stelle in g[gid]["text"], gid
        assert g[gid]["vokabeln"]["je"] == JE, gid
    # Sonst bleibt je "ist"; in den uebrigen Texten ist es nie "sie".
    assert grunddaten["woerterbuch"]["je"] == "ist"
    andere = sorted(i for i, s in g.items() if "je" in (s.get("vokabeln") or {}) and i not in JE_AKKUSATIV)
    assert andere == []


def test_b10_vokabeln_der_geschichten_bleiben(grunddaten):
    """Was die vier Geschichten vorher in vokabeln hatten, steht weiter da."""
    g = _geschichten(grunddaten)
    assert g["b1_voz"]["vokabeln"]["sam"] == "bin / allein (m)"
    assert g["b1_zanat"]["vokabeln"]["sto"] == "hundert"
    assert g["b1_zanat"]["vokabeln"]["mladi"] == "die Jungen / junge Leute"


def test_b10_geschlecht_wie_im_text(grunddaten):
    g = _geschichten(grunddaten)
    wb = grunddaten["woerterbuch"]
    for wort, (bedeutung, gid, stelle, _) in GESCHLECHT.items():
        assert stelle in g[gid]["text"], (wort, gid)
        assert wb[wort] == bedeutung, wort
        assert wort not in (g[gid].get("vokabeln") or {}), wort


def test_b10_kennungen_der_vokabeln_bleiben(grunddaten):
    """Nur das WOERTERBUCH hat neue Texte, die Vokabeln behalten ihr de."""
    woerter = _woerter(grunddaten)
    for wort, (bedeutung, _, _, kennung) in GESCHLECHT.items():
        assert kennung in woerter, (wort, kennung)
        assert woerter[kennung]["de"] != bedeutung, wort


def test_b10_uebersetzt_in_allen_sprachen(alle_daten):
    de = alle_daten["de"]
    for code in SPRACHEN:
        daten = alle_daten[code]
        wb = daten["woerterbuch"]
        for wort in list(KLEINE_WOERTER) + list(GESCHLECHT):
            assert wb[wort].strip(), (code, wort)
            assert wb[wort] != de["woerterbuch"][wort], (code, wort, wb[wort])
        g = _geschichten(daten)
        for gid in JE_AKKUSATIV:
            je = g[gid]["vokabeln"]["je"]
            assert je.strip() and je != JE, (code, gid, je)
        # Bosnisch bleibt bosnisch (AGENTS.md, Regel 2)
        assert [s["text"] for s in daten["geschichten"]] == [s["text"] for s in de["geschichten"]], code
    en = alle_daten["en"]["woerterbuch"]
    for wort, bedeutung in ENGLISCH.items():
        assert en[wort] == bedeutung, wort
    assert _geschichten(alle_daten["en"])["intervju"]["vokabeln"]["je"] == "is / her (acc.)"


# ---------------------------------------------------------------------------
# B12: "Passt zu Level" zeigt bei B1-Geschichten auf kein B2-Level
# ---------------------------------------------------------------------------
# Geschichte -> (Level bis 14.11.2026, B2; Level jetzt)
B12 = {
    "b1_ljeto": ("familie_generationen", "familie"),
    "b1_dijaspora": ("ankommen_ansehen", "urlaub"),
    "b1_voz": ("strassen_bahn", "urlaub"),
    "b1_jahorina": ("trainieren_siegen", "sport"),
    "b1_struja": ("nachbarn_miteinander", "miteinander_umgehen"),
    "b1_stan": ("wohnen_miete", "immobilien"),
    "b1_kahva": ("nachbarn_miteinander", "miteinander_umgehen"),
}


def _stufe_der_level(daten):
    stufe = {s["id"]: s.get("stufe") for s in daten["sektionen"]}
    return {k["id"]: stufe.get(k.get("sektion")) for k in daten["kategorien"]}


def test_b12_passt_zu_laut_bericht(grunddaten):
    g = _geschichten(grunddaten)
    stufe = _stufe_der_level(grunddaten)
    for gid, (alt, neu) in B12.items():
        assert stufe[alt] == "B2", (gid, alt)
        assert g[gid]["passt_zu"] == neu, gid


def test_b12_keine_geschichte_zeigt_auf_b2(grunddaten):
    """Die Geschichten gehen bis B1. Ein Level aus B2 oder C1 haben ihre
    Leser meist noch nicht offen."""
    stufe = _stufe_der_level(grunddaten)
    falsch = [(g["id"], g["passt_zu"], stufe.get(g["passt_zu"])) for g in grunddaten["geschichten"]
              if stufe.get(g["passt_zu"]) not in ("A1", "A2", "B1")]
    assert falsch == []


# ---------------------------------------------------------------------------
# V13 a: "plinski šporet" in b1_struja (Ajdin, F9 a, 14.11.2026)
# ---------------------------------------------------------------------------
def test_v13a_plinski_sporet(grunddaten):
    g = _geschichten(grunddaten)["b1_struja"]
    assert "Hasan je imao plinski šporet, pa je pozvao komšije na čaj." in g["text"]
    assert "Hasan hatte einen Gasherd" in g["uebersetzung"]
    assert [s["id"] for s in grunddaten["geschichten"] if "štednjak" in s["text"].lower()] == []


def test_v13a_woerterbuch(alle_daten):
    """šporet steht im WOERTERBUCH, štednjak nicht mehr (kommt in keinem Text vor)."""
    de = alle_daten["de"]["woerterbuch"]
    assert de["šporet"] == "Herd" and de["plinski"] == "Gas-"
    assert "štednjak" not in de
    for code in SPRACHEN:
        wb = alle_daten[code]["woerterbuch"]
        assert wb["šporet"].strip() and wb["šporet"] != "Herd", (code, wb["šporet"])
        assert "štednjak" not in wb, code
    assert alle_daten["en"]["woerterbuch"]["šporet"] == "stove"


def test_v13a_wartet_weiter_auf_ton():
    """b1_struja hat noch keinen Ton (tests/offen_lesetexte.json), der neue
    Text steht dort; šporet hat seine Aufnahme schon (Vokabel "Herd")."""
    import geschichten
    import offen_lesetexte
    import ton_bauen
    g = next(s for s in geschichten.GESCHICHTEN if s["id"] == "b1_struja")
    assert ton_bauen.schluessel(g["text"]) in offen_lesetexte.GESCHICHTEN
    assert "štednjak" not in offen_lesetexte.TON and "šporet" not in offen_lesetexte.TON
    assert "plinski" in offen_lesetexte.TON


# ---------------------------------------------------------------------------
# S3: "napraviti pitu" im Brief an die Nana (Ajdin, F20, 14.11.2026)
# ---------------------------------------------------------------------------
PISMO_ALT = "Nadam se da ćeš nam skuhati pitu!"
PISMO_NEU = "Nadam se da ćeš nam napraviti pitu!"


def test_s3_napraviti_pitu(alle_daten):
    de = alle_daten["de"]
    g = _geschichten(de)["pismo"]
    assert PISMO_NEU in g["text"] and PISMO_ALT not in g["text"]
    assert "Ich hoffe, dass du uns eine Pita machst!" in g["uebersetzung"]
    assert [s["id"] for s in de["geschichten"] if "skuhati" in s["text"].lower()] == []
    # Die anderen Sprachen sagten schon "machen"; ihr Schluessel ist der neue deutsche Text.
    for code in SPRACHEN:
        assert _geschichten(alle_daten[code])["pismo"]["uebersetzung"] != g["uebersetzung"], code
    for code, stelle in {"en": "I hope you will make us a pita!", "tr": "Umarım bize pita yaparsın!",
                         "fr": "tu nous feras une pita"}.items():
        assert stelle in _geschichten(alle_daten[code])["pismo"]["uebersetzung"], code


def test_s3_woerterbuch(alle_daten):
    for code in ["de"] + SPRACHEN:
        wb = alle_daten[code]["woerterbuch"]
        assert "skuhati" not in wb, code
        assert wb["napraviti"].strip(), code
    assert alle_daten["de"]["woerterbuch"]["napraviti"] == "machen / zubereiten"


def test_s3_pismo_wartet_auf_ton(wurzel):
    """Die alte Aufnahme g09 bleibt liegen, passt aber nicht mehr zum Text.
    pismo wartet deshalb mit den B1-Texten auf die naechste Vesna-Runde, als
    einzige der zwoelf alten Geschichten."""
    import io
    import json
    import os

    import geschichten
    import offen_b1_teil2
    import ton_bauen
    alt = {g["id"] for g in geschichten.GESCHICHTEN if not g["id"].startswith("b1_")}
    assert offen_b1_teil2.GESCHICHTEN & alt == {"pismo"}
    toene = json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8"))["toene"]
    g09 = next(e for e in toene if e["datei"] == "g09.mp3")
    assert PISMO_ALT in g09["text"] and os.path.getsize(os.path.join(wurzel, "web", "audio", "g09.mp3")) > 800
    pismo = next(g for g in geschichten.GESCHICHTEN if g["id"] == "pismo")
    assert ton_bauen.schluessel(pismo["text"]) not in {e["key"] for e in toene}


# ---------------------------------------------------------------------------
# S7: hoefliches Vi gross nur in Geschriebenem an eine Person (Ajdin, F23)
# ---------------------------------------------------------------------------
VI_FORMEN = re.compile(r"(?<![^\W\d_])(vi|vas|vam|vama|vaš|vaša|vaše|vašu|vašeg|vašem|vašoj|vaši|vašim|vaših)"
                       r"(?![^\W\d_])", re.I)

# Geschichte -> Stellen, wie sie jetzt im Text stehen
S7 = {
    "b1_posao": ["Prvo ću vam pokazati vašu kancelariju"],                 # die Chefin zu Haris
    "b1_stan": ["ako vam odgovara", "Hvala vam, vidimo se sutra!"],         # Telefonat
    "b1_telefon": ["Ako ste ga našli, molim Vas, javite se."],             # Nachricht, geschrieben
    "b1_doktor": ["„I vas boli grlo?“", "„Šta vas boli i od kada?“", "Dat ću vam recept"],
    "b1_zanat": ["„Jeste li vi napravili", "kad vi odete u penziju"],
}


def _gross_mitten_im_satz(text):
    """Gross geschriebene Vi-Formen, die nicht am Satz- oder Redeanfang stehen."""
    raus = []
    for m in VI_FORMEN.finditer(text):
        davor = text[:m.start()].rstrip()
        if m.group()[0].isupper() and davor and davor[-1] not in "„\".!?:":
            raus.append(m.group())
    return raus


def test_s7_stellen(grunddaten):
    g = _geschichten(grunddaten)
    for gid, stellen in S7.items():
        for stelle in stellen:
            assert stelle in g[gid]["text"], (gid, stelle)


def test_s7_gross_nur_in_der_nachricht(grunddaten):
    """In den B1-Texten steht ein grosses Vi mitten im Satz nur noch in der
    Nachricht an den Finder des Handys. "„Vaš telefon …" beginnt die Rede.
    b1_mejl schreibt dem Cousin und seiner Familie (vas, vam: euch), klein."""
    gross = {g["id"]: _gross_mitten_im_satz(g["text"]) for g in grunddaten["geschichten"]
             if g["id"].startswith("b1_")}
    assert {k: v for k, v in gross.items() if v} == {"b1_telefon": ["Vas"]}


def test_s7_ton_schluessel_bleibt():
    """Gross oder klein aendert den Ton-Schluessel nicht: beide Texte warten mit
    demselben Schluessel in tests/offen_lesetexte.json auf ihren Ton."""
    import geschichten
    import offen_lesetexte
    import ton_bauen
    for gid in ("b1_posao", "b1_stan"):
        g = next(s for s in geschichten.GESCHICHTEN if s["id"] == gid)
        assert ton_bauen.schluessel(g["text"]) == g["text"].lower()
        assert ton_bauen.schluessel(g["text"]) in offen_lesetexte.GESCHICHTEN, gid
