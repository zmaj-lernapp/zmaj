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

Der Text der Geschichten ist ihr Ton-Schluessel (ton_bauen.py) und bleibt
unveraendert. Die Tests im Browser stehen in
tests_e2e/test_pruefbericht14_geschichten.py.
"""
import hashlib

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

# sha256 ueber alle Geschichtentexte am 14.11.2026, vor B10 und B12
TEXTE_SHA256 = "11df97e6637dfa90a1b5e68dd94252a6dd0f7ad928aafee97bba75d4eb4f6d8f"


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
