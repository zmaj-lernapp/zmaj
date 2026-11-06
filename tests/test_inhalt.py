# -*- coding: utf-8 -*-
"""Der Lerninhalt: Level, Wörter, Sätze, Grammatik, Geschichten.

Ein Fehler hier landet beim Lernenden - ein Satz ohne Lücke, eine Testfrage
ohne richtige Antwort, ein Level, das Wörter abfragt, die noch nicht dran
waren. Die App fällt dabei nicht um; sie lehrt dann einfach etwas Falsches.
"""
import re

import pytest

# Befunde, die inhalt.pruefe_vokabeln() schon meldet und die noch auf eine
# inhaltliche Entscheidung warten. Ein NEUER Befund lässt den Test scheitern,
# ein behobener auch - dann bitte hier streichen.
# Am 06.10.2026 gestrichen: resto1 und kennenlernen bauten auf das spätere
# Level formell auf, ihr Level-Test fragte also Ungelerntes ab. Seitdem ist
# die Liste leer und jedes baut_auf auf ein späteres Level ein Fehler.
BEKANNT = set()


def test_projekteigene_pruefung(grunddaten):
    import inhalt
    befunde = set(inhalt.pruefe_vokabeln(grunddaten))
    neu = befunde - BEKANNT
    behoben = BEKANNT - befunde
    assert not neu, "Neue Befunde aus inhalt.pruefe_vokabeln():\n" + "\n".join(sorted(neu))
    assert not behoben, "Behoben - bitte aus BEKANNT streichen:\n" + "\n".join(sorted(behoben))


def test_kennzahlen_wie_im_readme(grunddaten):
    """README und Store-Text nennen diese Zahlen. Ändern sie sich,
    müssen die Texte mitgehen."""
    woerter = sum(len(k["words"]) for k in grunddaten["kategorien"])
    assert len(grunddaten["kategorien"]) == 166
    assert woerter == 4421
    assert len(grunddaten["saetze"]) == 300
    assert len(grunddaten["geschichten"]) == 12
    assert len(grunddaten["grammatik"]) == 16


def test_woerter_und_saetze_getrennt_wie_in_readme_und_store(grunddaten, wurzel):
    """Entscheidung vom 06.11.2026 (Prüfbericht 1.3, G16): Wörter und Sätze werden
    getrennt genannt, „4.421 Wörter“ stimmte nicht. Ein Satz endet auf ein
    Satzzeichen; breiter gezählt auch alles ab vier Wörtern, darunter Formen wie
    „moj / moja / moje“. Beide Zählungen müssen zu den gerundeten Zahlen passen.
    Geht das hier nicht mehr auf, müssen README und Store-Text mit."""
    import os
    ende = re.compile(r"[.!?…]$")
    eintraege = [w["bs"].strip() for k in grunddaten["kategorien"] for w in k["words"]]
    eng = sum(bool(ende.search(b)) for b in eintraege)
    breit = sum(bool(ende.search(b)) or len(b.split()) >= 4 for b in eintraege)
    for saetze in (eng, breit):
        assert abs(saetze - 1500) <= 100, saetze
        assert abs(len(eintraege) - saetze - 2900) <= 100, saetze

    def flach(name):
        with open(os.path.join(wurzel, name), encoding="utf-8") as f:
            return " ".join(f.read().split())
    readme = flach("README.md")
    assert "about 2,900 words and phrases and about 1,500 example sentences" in readme
    assert "rund 2.900 Wörter und Wendungen und rund 1.500 Beispielsätze" in readme
    assert "oko 2.900 riječi i izraza i oko 1.500 rečenica" in flach("README.bs.md")
    # Der Alt-Text des Kopfbilds beschreibt das Bild, und dort steht die Zahl noch.
    ohne_bild = re.sub(r'alt="[^"]*"', "", readme)
    assert "4,421 words" not in ohne_bild and "4421 Vokabeln" not in ohne_bild


def test_wort_kennungen_eindeutig_und_stabil(grunddaten):
    """Unter der Kennung speichert die App den Lernstand. Doppelt heißt: zwei
    Wörter teilen sich einen Fortschritt."""
    kennungen = [w["id"] for k in grunddaten["kategorien"] for w in k["words"]]
    doppelt = sorted({k for k in kennungen if kennungen.count(k) > 1})
    assert not doppelt, doppelt
    for k in kennungen:
        assert re.match(r"^[^:]+:.+$", k), k


@pytest.mark.parametrize("feld", ["bs", "de"])
def test_keine_unsichtbaren_leerzeichen(grunddaten, feld):
    schlecht = [w[feld] for k in grunddaten["kategorien"] for w in k["words"]
                if w[feld] != w[feld].strip() or "  " in w[feld]]
    assert not schlecht, schlecht[:20]


def test_jeder_satz_hat_genau_eine_luecke(grunddaten):
    schlecht = [s["text"] for s in grunddaten["saetze"] if s["text"].count("___") != 1]
    assert not schlecht, schlecht


def test_satz_antwort_ist_nicht_leer(grunddaten):
    schlecht = [s["text"] for s in grunddaten["saetze"] if not s["answer"].strip()]
    assert not schlecht, schlecht


def test_bosnisch_bleibt_in_jeder_sprache_bosnisch(alle_daten, grunddaten):
    """uebersetzungen.py übersetzt die Bedeutung, nie das bosnische Wort."""
    basis = [w["bs"] for k in grunddaten["kategorien"] for w in k["words"]]
    for code, daten in alle_daten.items():
        hier = [w["bs"] for k in daten["kategorien"] for w in k["words"]]
        assert hier == basis, code
        assert [s["text"] for s in daten["saetze"]] == [s["text"] for s in grunddaten["saetze"]], code
        assert [g["text"] for g in daten["geschichten"]] == [g["text"] for g in grunddaten["geschichten"]], code
        # Satzbau (13.10.2026): die Kacheln und jede erlaubte Reihenfolge
        # sind der Lernstoff, übersetzt wird nur "de".
        assert [(s["bs"], s.get("auch")) for s in daten["satzbau"]] == \
            [(s["bs"], s.get("auch")) for s in grunddaten["satzbau"]], code


def test_jede_sprache_ist_vollstaendig_uebersetzt(alle_daten):
    for code, daten in alle_daten.items():
        u = daten["uebersetzt"]
        assert u["fertig"] == u["gesamt"], "%s: %d von %d übersetzt" % (code, u["fertig"], u["gesamt"])
        leer = [w["id"] for k in daten["kategorien"] for w in k["words"] if not w["de"].strip()]
        assert not leer, (code, leer[:10])


def test_uebungen_haben_ihre_richtige_antwort_in_jeder_sprache(alle_daten):
    """Steht die richtige Antwort nicht unter den Optionen, ist die Aufgabe
    unlösbar. Das kann auch erst durch eine Übersetzung passieren."""
    fehler = []
    for code, daten in alle_daten.items():
        for kid, lektion in daten["grammatik"].items():
            for ue in lektion.get("uebungen", []):
                if ue.get("richtig") not in ue.get("optionen", []):
                    fehler.append((code, "grammatik", kid, ue.get("frage")))
        for g in daten["geschichten"]:
            for f in g.get("fragen", []):
                if f.get("richtig") not in f.get("optionen", []):
                    fehler.append((code, "geschichte", g["id"], f.get("frage")))
                if len(set(f.get("optionen", []))) != len(f.get("optionen", [])):
                    fehler.append((code, "doppelte Option", g["id"], f.get("frage")))
    assert not fehler, fehler[:20]


def test_geschichten_woerter_stehen_im_woerterbuch(grunddaten):
    """In den Geschichten lässt sich jedes Wort antippen. Fehlt es im
    Wörterbuch, kommt "Kein Eintrag"."""
    import inhalt
    fehlt = inhalt.fehlende_woerter(grunddaten)
    assert not fehlt, {k: sorted(v)[:10] for k, v in fehlt.items()}
