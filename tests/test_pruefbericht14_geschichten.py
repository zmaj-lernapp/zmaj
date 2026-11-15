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

S7: Vi, Vas, Vam standen mal gross, mal klein. Ajdin (F23, 14.11.2026): gross
in Geschriebenem an eine Person, klein in Gespraechen der Erzaehlung. Am
15.11.2026 neu entschieden: "mach doch alles groß" - gross, sobald EINE Person
hoeflich angeredet wird, auch in den Gespraechen (b1_posao, b1_stan, opcina,
b1_struja, b1_doktor, b1_zanat; b1_telefon war es schon). Klein bleibt, wo
mehrere gemeint sind: b1_voz, b1_rafting, b1_mejl. Der Ton-Schluessel ist
kleingeschrieben und bleibt (ton_bauen.schluessel); die Wortzeiten von opcina
(g10) gehoeren mit "Hvala Vam" wieder genau zum Text.

B11 / F11 a: Die Lektion sagt, vor jer, da und ako steht kein Komma, wenn der
Nebensatz hinter dem Hauptsatz steht (grammatik.py, satzbau). Sieben B1-Saetze
hatten es trotzdem ("Najviše sam voljela subotu, jer je nana …"). Ajdin (F11):
a, die sieben Kommas streichen. Der Einschub in b1_selidba ("Sjeli su na pod,
jer sto još nisu kupili, i …") blieb, die Geschichte wird ersetzt. Keiner der
sieben Texte hatte Ton; der Schluessel aendert sich mit dem Komma und ist in
tests/offen_lesetexte.json nachgezogen (b1_zanat, b1_mejl und b1_zmaj warten
mit ihrer id in tests/offen_b1_teil2.py).

F10: Ajdin "mach eine neue geschichte". Statt "Selidba" (wieder eine junge
Frau, die wegen der Arbeit umzieht, wie in b1_stan) steht unter derselben id
"Dedo i nana se sele": Opa und Oma ziehen vom Dorf unter dem Vlašić in eine
kleine Wohnung in Travnik, der Opa nimmt heimlich einen Pflaumenbaum mit.
Angenommen mit "nana se teško penje uz stepenice" und "Napokon bašta koja nije
prevelika". Uebersetzung und Fragen in acht Sprachen, die richtige Antwort ist
nirgends deutlich laenger (B13). Die Formen der alten Geschichte, die kein Text
mehr braucht, sind aus dem WOERTERBUCH und aus uebersetzungen.py raus. Ton
folgt in der Vesna-Runde.

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
    # seit Ajdins A/B-Antwort T3 (15.11.2026) "ponovo" statt "opet"
    "zdrav": ("gesund (m)", "b1_doktor", "Amar je ponovo bio zdrav", "gesund (m/w):zdrav / zdrava"),
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
# klein in den Gespraechen von b1_posao und b1_stan (46d93671…), seit F11 a
# ohne die sieben Kommas vor nachgestelltem jer und ako (7ae50346…), seit der
# Offen-Liste, Punkt 3, "Hvala vam na pomoći" klein in opcina (bc6caa52…), dann
# "Dedo i nana se sele" statt "Selidba" (ccb92728…), seit 15.11.2026 das
# hoefliche Vi gross auch in den Gespraechen (Ajdin: "mach doch alles groß",
# 21871bb1…), dann Ajdins A/B-Antworten zu den B1-Lesetexten, eine Geschichte
# nach der anderen (tests/test_lesetexte_ab.py).
TEXTE_SHA256 = "118b50083893465f7f33b0b99899e848eb2d77d9108bdf8c6e452883ae4f659b"


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
# S7: hoefliches Vi gross, sobald EINE Person hoeflich angeredet wird, auch im
# Gespraech (Ajdin am 15.11.2026: "mach doch alles groß", statt F23)
# ---------------------------------------------------------------------------
VI_FORMEN = re.compile(r"(?<![^\W\d_])(vi|vas|vam|vama|vaš|vaša|vaše|vašu|vašeg|vašem|vašoj|vaši|vašim|vaših)"
                       r"(?![^\W\d_])", re.I)

# Geschichte -> Stellen, wie sie jetzt im Text stehen: EINE Person, hoeflich
S7 = {
    "opcina": ["„Hvala Vam na pomoći“, kaže Amina."],                       # Amina am Schalter
    "b1_struja": ["„Komšinice, je li i kod Vas nestalo struje?“"],           # Hasan zu Merima
    "b1_posao": ["Prvo ću Vam pokazati Vašu kancelariju"],                  # die Chefin zu Haris
    "b1_stan": ["ako Vam odgovara", "Hvala Vam, vidimo se sutra!"],         # Telefonat
    "b1_telefon": ["Ako ste ga našli, molim Vas, javite se."],             # Nachricht, geschrieben
    # seit Ajdins A/B-Antwort T1 (15.11.2026) auch "i otvorit ću Vam bolovanje"
    "b1_doktor": ["„I Vas boli grlo?“", "„Šta Vas boli i od kada?“",
                  "Dat ću Vam recept i otvorit ću Vam bolovanje na pet dana."],
    "b1_zanat": ["„Jeste li Vi napravili", "kad Vi odete u penziju"],      # Lejla zum Meister
}
# Klein, weil mehrere gemeint sind (ihr, euch)
S7_KLEIN = {
    "b1_voz": ["„Ako vam nešto zatreba, nazovite me.“"],                    # die Frau zu Lejla und Emir
    "b1_rafting": ["Prsluk će vas držati."],                                 # der Instruktor zur Gruppe
    "b1_mejl": ["kod vas ako vam to ne smeta", "Šta da vam donesem"],       # an Cousin und Familie
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
    for gid, stellen in list(S7.items()) + list(S7_KLEIN.items()):
        for stelle in stellen:
            assert stelle in g[gid]["text"], (gid, stelle)


def test_s7_klein_nur_wo_mehrere_gemeint_sind(grunddaten):
    """Ueber alle Geschichten steht ein kleines vi, vas, vam oder vaš nur noch
    dort, wo mehrere angeredet werden. Kommt eine Stelle dazu, schlaegt der
    Test an: dann lesen, wer mit wem spricht."""
    klein = {g["id"]: [m.group() for m in VI_FORMEN.finditer(g["text"]) if m.group()[0].islower()]
             for g in grunddaten["geschichten"]}
    assert {k: v for k, v in klein.items() if v} == {
        "b1_voz": ["vam"], "b1_rafting": ["vas"], "b1_mejl": ["vas", "vam", "vam"]}


def test_s7_gross_auch_im_gespraech(grunddaten):
    """Jede hoefliche Anrede einer Person steht gross, mitten im Satz wie in
    der Nachricht von b1_telefon. "„Vaš telefon …" beginnt die Rede."""
    gross = {g["id"]: _gross_mitten_im_satz(g["text"]) for g in grunddaten["geschichten"]}
    assert {k: v for k, v in gross.items() if v} == {
        "opcina": ["Vam"], "b1_struja": ["Vas"], "b1_posao": ["Vam", "Vašu"], "b1_stan": ["Vam", "Vam"],
        "b1_telefon": ["Vas"], "b1_doktor": ["Vas", "Vas", "Vam", "Vam"], "b1_zanat": ["Vi", "Vi"]}
    opcina = _geschichten(grunddaten)["opcina"]
    assert "„Danke für Ihre Hilfe“, sagt Amina." in opcina["uebersetzung"]


@pytest.mark.parametrize("gid,sie", [
    ("opcina", "Danke für Ihre Hilfe"), ("b1_struja", "ist bei Ihnen auch der Strom weg"),
    ("b1_posao", "zeige ich Ihnen Ihr Büro"), ("b1_stan", "wenn es Ihnen passt"),
    ("b1_doktor", "Tut Ihnen auch der Hals weh"), ("b1_doktor", "Was tut Ihnen weh"),
    ("b1_doktor", "Ich gebe Ihnen ein Rezept"), ("b1_zanat", "Haben Sie all diese Sachen gemacht"),
    ("b1_zanat", "wenn Sie in Rente gehen"),
])
def test_s7_uebersetzung_in_der_sie_form(grunddaten, gid, sie):
    """Wo das Bosnische siezt, siezt auch die Uebersetzung."""
    assert sie in _geschichten(grunddaten)[gid]["uebersetzung"], (gid, sie)


def test_s7_opcina_behaelt_ihren_ton(wurzel):
    """Der Ton-Schluessel ist kleingeschrieben: g10 passt. Seit dem 15.11.2026
    steht wieder "Hvala Vam" wie in der Aufnahme, die Wortzeiten gehoeren damit
    wieder genau zum Text, opcina steht nicht mehr in WORTZEITEN_NEU."""
    import io
    import json
    import os

    import geschichten
    import offen_b1_teil2
    import offen_lesetexte
    import ton_bauen
    g = next(s for s in geschichten.GESCHICHTEN if s["id"] == "opcina")
    toene = json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8"))["toene"]
    g10 = next(e for e in toene if e["datei"] == "g10.mp3")
    assert g10["key"] == ton_bauen.schluessel(g["text"])
    assert "Hvala Vam na pomoći" in g10["text"]
    assert len(g10["w"]) == len(ton_bauen.textwoerter(g["text"]))
    assert ton_bauen.wortzeiten_passen(g10, g["text"])
    assert "opcina" not in offen_b1_teil2.WORTZEITEN_NEU
    assert "opcina" not in offen_b1_teil2.GESCHICHTEN
    assert ton_bauen.schluessel(g["text"]) not in offen_lesetexte.GESCHICHTEN


def test_s7_ton_schluessel_bleibt():
    """Gross oder klein aendert den Ton-Schluessel nicht: beide Texte warten mit
    demselben Schluessel in tests/offen_lesetexte.json auf ihren Ton."""
    import geschichten
    import offen_lesetexte
    import ton_bauen
    for gid in ("b1_posao", "b1_stan", "b1_struja"):
        g = next(s for s in geschichten.GESCHICHTEN if s["id"] == gid)
        assert ton_bauen.schluessel(g["text"]) == g["text"].lower()
        assert ton_bauen.schluessel(g["text"]) in offen_lesetexte.GESCHICHTEN, gid


# ---------------------------------------------------------------------------
# B11 / F11 a: kein Komma vor nachgestelltem jer und ako (14.11.2026)
# ---------------------------------------------------------------------------
# Geschichte -> der Satz, wie er jetzt dasteht
F11 = {
    "b1_ljeto": "Najviše sam voljela subotu jer je nana tada pravila pitu.",
    "b1_dijaspora": "Tarik je bio malo nervozan jer njegov bosanski nije savršen.",
    "b1_jahorina": "Ajdin je obukao debelu jaknu, kapu i rukavice jer je vani bilo minus osam.",
    "b1_zanat": "Tu se cijeli dan čuje kucanje čekića jer u malim radnjama majstori prave stvari od bakra.",
    "b1_zmaj": "Već nekoliko mjeseci uči bosanski jer ovog ljeta ide kod nane u Mostar.",
    "b1_stan": "„Može sutra u šest ako Vam odgovara.“",
    "b1_mejl": "Prvu sedmicu bih bio kod vas ako vam to ne smeta.",
}
KOMMA_DAVOR = re.compile(r",\s+(jer|ako)(?![^\W\d_])")


def test_f11_die_sieben_saetze(grunddaten):
    g = _geschichten(grunddaten)
    for gid, satz in F11.items():
        assert satz in g[gid]["text"], (gid, satz)


def test_f11_kein_komma_vor_jer_und_ako(grunddaten):
    """Wie die Lektion es lehrt, in keiner Geschichte. Bis zur neuen
    Geschichte stand ein Komma davor nur noch im Einschub der alten
    b1_selidba ("Sjeli su na pod, jer sto još nisu kupili, i …"); "Dedo i
    nana se sele" hat weder jer noch ako."""
    import grammatik
    regel = "Vor „jer“, „da“ und „ako“ steht kein Komma, wenn der Nebensatz hinter dem Hauptsatz steht"
    assert any(regel in str(teil) for teil in grammatik.GRAMMATIK["satzbau"]["erklaerung"])
    funde = {s["id"]: [m.group() for m in KOMMA_DAVOR.finditer(s["text"])] for s in grunddaten["geschichten"]}
    assert {k: v for k, v in funde.items() if v} == {}


def test_f11_ton_schluessel_nachgezogen():
    """Keiner der sieben Texte hatte Ton. Mit dem Komma aendert sich ihr
    Schluessel: Paket 1 und 2 warten mit dem neuen Text in
    tests/offen_lesetexte.json, Paket 3 und 4 mit ihrer id in
    tests/offen_b1_teil2.py."""
    import geschichten
    import offen_b1_teil2
    import offen_lesetexte
    import ton_bauen
    for gid in F11:
        g = next(s for s in geschichten.GESCHICHTEN if s["id"] == gid)
        k = ton_bauen.schluessel(g["text"])
        assert k in offen_lesetexte.GESCHICHTEN or gid in offen_b1_teil2.GESCHICHTEN, gid
    alt = [t for t in offen_lesetexte.GESCHICHTEN if KOMMA_DAVOR.search(t)]
    assert alt == []


# ---------------------------------------------------------------------------
# F10: "Dedo i nana se sele" statt "Selidba" (Offen-Liste, Punkt 3, 14.11.2026)
# ---------------------------------------------------------------------------
# Ajdin: "mach eine neue geschichte", Entwurf Release\Selidba_neu_Entwurf.md,
# Vorschlag 1, angenommen mit "nimm penje uz stepenicama" und "nimm napokon...".
DEDO_TEXT = "\n\n".join([
    "Dedo Rasim i nana Fadila već četrdeset godina žive u kući na selu ispod Vlašića. Ali bašta im je "
    "prevelika, a nana se teško penje uz stepenice. Zato su odlučili da se presele u Travnik, u mali stan "
    "blizu kćerke Alme. Zgrada ima lift.",
    "U subotu je došao unuk Edin da pomogne. Nana je htjela sve ponijeti: ormar, šporet na drva i trideset "
    "tegli zimnice. „Nano, stan ima dvije sobe, a ne deset!“ rekao je Edin. Uzeo je papir i zapisivao šta "
    "ide, a šta ostaje.",
    "Dedo je htio samo dvije stvari: staru fotelju i radio. „U njoj trideset godina slušam radio. Bez nje "
    "ne idem!“ Ormar i šporet su ostali u kući, a ključ su dali komšiji.",
    "Edin je u punom kombiju našao kantu koje nije bilo na spisku. U kanti je bila mlada šljiva iz bašte. "
    "„Dedo, rekao si samo dvije stvari!“ „Ovo nije stvar“, rekao je dedo. „Ovo je šljiva.“",
    "Prve večeri su sjedili na novom balkonu. Nana je skuhala kahvu, a dedo je zalijevao svoju šljivu. "
    "„Napokon bašta koja nije prevelika“, rekao je. Nana se nasmijala: „Naviknut ćemo se, Rasime.“",
])
DEDO_FRAGEN = [
    ("Wohin ziehen Rasim und Fadila?",
     ["in eine kleine Wohnung in Travnik", "in ein großes Haus in Sarajevo", "in ein anderes Dorf am Vlašić"]),
    ("Welche zwei Dinge wollte der Opa mitnehmen?",
     ["den alten Sessel und das Radio", "den Schrank und den Holzherd", "den großen Tisch und das Bett"]),
    ("Was fand Edin im vollen Kleinbus?",
     ["einen Pflaumenbaum im Eimer", "einen Eimer mit Pflaumenmus", "den Schlüssel vom alten Haus"]),
]
# Aus der alten Geschichte, kommen in keinem Text mehr vor
SELIDBA_ALT_WOERTER = ["hajra", "kamenje", "kutiji", "pokucajte", "stepenicama", "petom", "pitom", "kombi"]
SELIDBA_ALT_TEXTE = ["Warum zieht Selma um?", "der Aufzug funktionierte nicht", "eine warme Pita",
                     "Hajra (Name)", "funktioniert / gearbeitet (m)", "Kisten (Akk.)"]


def test_f10_text_wie_angenommen(grunddaten):
    g = _geschichten(grunddaten)["b1_selidba"]
    assert g["titel"] == "Dedo i nana se sele"
    assert g["stufe"] == "B1" and g["passt_zu"] == "erledigen_umziehen"
    assert g["text"] == DEDO_TEXT
    assert "nana se teško penje uz stepenice" in g["text"]
    assert "„Napokon bašta koja nije prevelika“" in g["text"]
    assert not re.search(r"(?i)\b(jer|ako|vi|vas|vam)\b", g["text"])


def test_f10_id_und_platz_bleiben(grunddaten):
    """Die id bleibt b1_selidba, so bleibt der Lesestand. Auch der Platz in der
    Kette bleibt: hinter b1_doktor, vor b1_rodjendan."""
    ids = [g["id"] for g in grunddaten["geschichten"]]
    i = ids.index("b1_selidba")
    assert ids[i - 1:i + 2] == ["b1_doktor", "b1_selidba", "b1_rodjendan"]


def test_f10_uebersetzung_und_fragen(alle_daten):
    de = _geschichten(alle_daten["de"])["b1_selidba"]
    ueb = de["uebersetzung"]
    assert "Aber der Garten ist ihnen zu groß, und Oma fällt das Treppensteigen schwer." in ueb
    assert "„Endlich ein Garten, der nicht zu groß ist“, sagte er." in ueb
    assert [(f["frage"], f["optionen"]) for f in de["fragen"]] == DEDO_FRAGEN
    assert [f["richtig"] for f in de["fragen"]] == [o[0] for _, o in DEDO_FRAGEN]
    for code in SPRACHEN:
        g = _geschichten(alle_daten[code])["b1_selidba"]
        assert g["titel"] == "Dedo i nana se sele", code
        assert g["uebersetzung"] != ueb and "Rasim" in g["uebersetzung"], code
        assert len(g["uebersetzung"].split("\n\n")) == 5, code
        for f, f_de in zip(g["fragen"], de["fragen"]):
            assert f["frage"] != f_de["frage"], (code, f["frage"])
            assert all(o != o_de for o, o_de in zip(f["optionen"], f_de["optionen"])), (code, f["optionen"])
            assert f["richtig"] == f["optionen"][0], code


def test_f10_richtige_antwort_nicht_laenger(alle_daten):
    """B13: Die richtige Antwort ist in keiner Sprache deutlich laenger als die
    falschen (hoechstens das 1,25-fache der kuerzesten)."""
    zu_lang = []
    for code, daten in alle_daten.items():
        for n, f in enumerate(_geschichten(daten)["b1_selidba"]["fragen"], 1):
            falsch = [len(o) for o in f["optionen"] if o != f["richtig"]]
            if len(f["richtig"]) > 1.25 * min(falsch):
                zu_lang.append((code, n, f["richtig"], falsch))
    assert zu_lang == []


def test_f10_woerterbuch(alle_daten):
    """Jedes Wort laesst sich antippen (test_inhalt.py). radio ist hier das
    Geraet, njoj und nje meinen den Sessel; die Formen der alten Geschichte
    sind raus, ihre Uebersetzungen auch."""
    import uebersetzungen
    de = alle_daten["de"]
    g = _geschichten(de)["b1_selidba"]
    vok = g["vokabeln"]
    assert vok["radio"] == "Radio / funktioniert (m)"
    assert "Sessel" in vok["njoj"] and "Sessel" in vok["nje"]
    wb = de["woerterbuch"]
    assert "radio" not in wb
    for wort in ("rasim", "fadila", "vlašića", "travnik", "prevelika", "penje", "napokon", "tegli",
                 "zimnice", "kantu", "spisku", "šljiva", "šljivu", "zalijevao", "fotelju", "nasmijala"):
        assert wort in wb, wort
    for wort in SELIDBA_ALT_WOERTER:
        assert wort not in wb, wort
    for code in SPRACHEN:
        gv = _geschichten(alle_daten[code])["b1_selidba"]["vokabeln"]
        assert set(gv) == set(vok), code
        assert all(gv[k].strip() and gv[k] != vok[k] for k in vok), code
        texte = uebersetzungen.INHALT[code]["texte"]
        assert [t for t in SELIDBA_ALT_TEXTE if t in texte] == [], code
    assert alle_daten["en"]["woerterbuch"]["šljiva"] == "plum tree / plum"
    assert _geschichten(alle_daten["en"])["b1_selidba"]["vokabeln"]["radio"] == "radio / worked (m)"


def test_f10_wartet_auf_ton(wurzel):
    """Neuer Text, neuer Ton-Schluessel: die Geschichte wartet weiter mit ihrer
    id in tests/offen_b1_teil2.py auf die Vesna-Runde."""
    import io
    import json
    import os

    import geschichten
    import offen_b1_teil2
    import ton_bauen
    assert "b1_selidba" in offen_b1_teil2.GESCHICHTEN
    g = next(s for s in geschichten.GESCHICHTEN if s["id"] == "b1_selidba")
    toene = json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8"))["toene"]
    assert ton_bauen.schluessel(g["text"]) not in {e["key"] for e in toene}
