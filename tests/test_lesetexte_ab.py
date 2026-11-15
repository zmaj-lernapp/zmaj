# -*- coding: utf-8 -*-
"""B1-Lesetexte: Ajdins Antworten auf die A/B-Liste (15.11.2026).

Release\\Lesetexte_Fragen_AB.md stellte zu den fraglichen Stellen der neuen
Lesetexte zwei Fassungen zur Wahl: A, wie es im Text stand, und B. Wo Ajdin
B gewählt hat, steht jetzt genau B im Text, mit Übersetzung, Fragen und
Wörterbuch in allen acht Sprachen. Wo er A gewählt hat, bleibt der Text.
Keine dieser Geschichten hat schon Ton: Ein neuer Text ist ein neuer
Ton-Schlüssel, und der steht in tests/offen_lesetexte.json (Pakete 1 und 2),
oder die Geschichte wartet mit ihrer id in tests/offen_b1_teil2.py (Pakete 3
und 4). Im Browser: tests_e2e/test_lesetexte_ab.py.
"""
import io
import json
import os
import re

SPRACHEN = ["en", "tr", "sv", "nl", "nb", "da", "fr"]

# Stelle -> (Geschichte, Satz jetzt (B), Satz vorher (A))
B = {
    "L9": ("b1_dijaspora", "Tarik je naručio deset ćevapa s lukom i jogurt.",
           "Tarik je naručio desetku s lukom i jogurt."),
    "L10": ("b1_vrijeme", "„Dobro veče, dragi slušaoci.", "„Dobro veče, poštovani slušaoci."),
    "L12": ("b1_vrijeme", "„Ako bude sunčano, možemo i roštiljati.“",
            "„Ako bude sunčano, možemo napraviti i roštilj.“"),
}

# Stelle -> (Geschichte, Stelle, die bleibt): hier hat Ajdin A gewählt
A = {
    "L11": ("b1_vrijeme", "Oko podne se očekuje kiša, a poslijepodne i grmljavina."),
    "L13": ("b1_rafting", "Instruktor Mirza im je dao kacige, prsluke i vesla."),
    "L14": ("b1_rafting", "Kad kažem ‚stop‘, prestanite."),
    "L15": ("b1_rafting", "Poslije raftinga su na obali jeli pastrmku."),
    "L17 a": ("b1_jahorina", "Prvog jutra su iznajmili skije,"),
    "L17 b": ("b1_jahorina", "Trećeg dana su se zajedno spustili do hotela."),
    "L17 c": ("b1_pita", "Jednog jutra je rekla nani:"),
    "L20": ("b1_pita", "savile ga i stavile pitu u tepsiju."),
    "L25": ("b1_svadba", "Njegova djevojka Sara je iz Tuzle"),
    "L29": ("b1_stan", "Izdajem jednosoban stan na Grbavici."),
    "T8": ("b1_zanat", "onda se dugo kuca čekićem"),
    "T9": ("b1_zanat", "„Neka je sa srećom!“ rekao je majstor."),
    "T10": ("b1_kahva", "Moja komšinica, teta Safija,"),
    "T13": ("b1_zmaj", "Pustio je malo vatre iz usta"),
    "T16": ("b1_utakmica", "„Babo, kad idemo opet?“ pitao je Kenan."),
}

# Geschichte -> [(deutscher Satz jetzt, deutscher Satz vorher)], nur wo sich
# die Übersetzung ändert
DE = {
    "b1_dijaspora": [("Tarik bestellte zehn Ćevapi mit Zwiebeln und einen Joghurt.",
                      "Tarik bestellte eine Portion mit zehn Ćevapi und Zwiebeln und dazu einen Joghurt.")],
}

# Stichprobe: so heißt es jetzt auf Englisch
EN = {
    "b1_dijaspora": "Tarik ordered ten ćevapi with onions and a yogurt.",
}

# Neue Formen im Wörterbuch der Lesetexte und ihre Bedeutung
NEU = {
    "ćevapa": "Ćevapi (Gen.)",
    "roštiljati": "grillen",
}

# Formen, die in keinem Text mehr stehen und deshalb aus dem Wörterbuch raus sind
RAUS = ["desetku", "poštovani", "roštilj"]

# Deutsche Texte, die mit ihnen aus uebersetzungen.py gegangen sind
RAUS_TEXTE = ["zehn Ćevapi (Portion, Akk.)", "sehr geehrte"]

# (Geschichte, Wort) -> Bedeutung in den vokabeln der Geschichte. "dragi
# slušaoci" ist Mehrzahl, im WOERTERBUCH bleibt "lieber" ("Dragi Adnane").
VOKABELN = {
    ("b1_vrijeme", "dragi"): "liebe (Mehrz.)",
}


def _geschichten(daten):
    return {g["id"]: g for g in daten["geschichten"]}


def _geaendert():
    return sorted({gid for gid, _, _ in B.values()})


def test_b_steht_genau_so_im_text(grunddaten):
    g = _geschichten(grunddaten)
    for stelle, (gid, jetzt, vorher) in B.items():
        assert jetzt in g[gid]["text"], (stelle, jetzt)
        assert vorher not in g[gid]["text"], (stelle, vorher)


def test_a_bleibt(grunddaten):
    g = _geschichten(grunddaten)
    for stelle, (gid, satz) in A.items():
        assert satz in g[gid]["text"], (stelle, satz)


def test_deutsche_uebersetzung(grunddaten):
    g = _geschichten(grunddaten)
    for gid, paare in DE.items():
        for jetzt, vorher in paare:
            assert jetzt in g[gid]["uebersetzung"], (gid, jetzt)
            assert vorher not in g[gid]["uebersetzung"], (gid, vorher)


def test_uebersetzt_in_allen_sprachen(alle_daten):
    """Jede Sprache hat die neue Übersetzung (sonst stünde dort der deutsche
    Text), Bosnisch bleibt bosnisch (AGENTS.md, Regel 2)."""
    de = _geschichten(alle_daten["de"])
    for code in SPRACHEN:
        g = _geschichten(alle_daten[code])
        for gid in _geaendert():
            assert g[gid]["text"] == de[gid]["text"], (code, gid)
            assert g[gid]["uebersetzung"] != de[gid]["uebersetzung"], (code, gid)
            assert len(g[gid]["uebersetzung"].split("\n\n")) == len(de[gid]["text"].split("\n\n")), (code, gid)
            for f, f_de in zip(g[gid]["fragen"], de[gid]["fragen"]):
                assert f["frage"] != f_de["frage"] and f["richtig"] in f["optionen"], (code, gid)
    en = _geschichten(alle_daten["en"])
    for gid, satz in EN.items():
        assert satz in en[gid]["uebersetzung"], (gid, satz)


def test_woerterbuch(alle_daten):
    """Jede neue Form lässt sich antippen, in jeder Sprache mit eigener
    Bedeutung; die alten sind raus, ihre Übersetzungen auch."""
    import uebersetzungen
    wb = alle_daten["de"]["woerterbuch"]
    for wort, bedeutung in NEU.items():
        assert wb.get(wort) == bedeutung, wort
    for code in SPRACHEN:
        wbc = alle_daten[code]["woerterbuch"]
        for wort in NEU:
            assert wbc[wort].strip() and wbc[wort] != wb[wort], (code, wort, wbc[wort])
        texte = uebersetzungen.INHALT[code]["texte"]
        assert [t for t in RAUS_TEXTE if t in texte] == [], code
    for code, daten in alle_daten.items():
        assert [w for w in RAUS if w in daten["woerterbuch"]] == [], code


def test_alte_formen_stehen_in_keinem_text(grunddaten):
    woerter = {w.lower() for g in grunddaten["geschichten"] for w in re.findall(r"[^\W\d_]+", g["text"])}
    assert sorted(set(RAUS) & woerter) == []
    assert sorted(set(NEU) - woerter) == []


def test_vokabeln_der_geschichten(alle_daten):
    de = _geschichten(alle_daten["de"])
    for (gid, wort), bedeutung in VOKABELN.items():
        assert de[gid]["vokabeln"][wort] == bedeutung, (gid, wort)
        for code in SPRACHEN:
            v = _geschichten(alle_daten[code])[gid]["vokabeln"][wort]
            assert v.strip() and v != bedeutung, (code, gid, wort)


def test_wartet_auf_ton(wurzel):
    """Neuer Text, neuer Schlüssel: Die Geschichte wartet weiter auf Vesna,
    und jedes neue Wort ohne Aufnahme steht in einer der beiden Listen."""
    import geschichten
    import offen_b1_teil2
    import offen_lesetexte
    import ton_bauen
    index = {e["key"] for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                 encoding="utf-8"))["toene"]}
    g = {s["id"]: s for s in geschichten.GESCHICHTEN}
    teil2 = offen_b1_teil2.ton_schluessel()
    for gid in _geaendert():
        k = ton_bauen.schluessel(g[gid]["text"])
        assert k not in index, gid
        assert k in offen_lesetexte.GESCHICHTEN or gid in offen_b1_teil2.GESCHICHTEN, gid
    for wort in NEU:
        k = ton_bauen.schluessel(wort)
        if k not in index and k not in ton_bauen.nur_emir():
            assert k in offen_lesetexte.TON or k in teil2, wort
    assert not set(RAUS) & offen_lesetexte.TON
