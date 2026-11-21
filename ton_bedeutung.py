# -*- coding: utf-8 -*-
"""
ton_bedeutung.py  –  eigener Ton je Bedeutung (21.11.2026)

Die App sucht den Ton nach dem Text (audioDatei() in web/js/ton_abspielen.js).
Jede Schreibweise hat deshalb genau eine Aufnahme, egal welche Bedeutung
gemeint ist. Bei Wörtern, die gleich geschrieben werden und anders klingen,
ist das falsch. Gefunden an „sam“: als „bin“ ist es ein kurzes, unbetontes
Anhängsel, allein gesprochen kam aber das betonte sȃm (allein) mit langem a.
Ajdin am 21.11.2026 beim Test der 1.5: „bei dem wort bin also sam sagt er
das a lang das beudetet aber alleine bin ist das a kurz“. Die Liste aller
Fälle steht in Release/Ton_gleiche_Schreibung_2026-11-21/liste.md.

ton_bedeutung.json legt fest, welche Stelle welchen Ton-Schlüssel spielt:

  woerter      Wort-ID -> Schlüssel. Gilt überall, wo die Vokabel spricht
               (Lektion, Wiederholen, Markiert, Wortliste des Levels).
  vorgemerkt   wie woerter, für Wörter, die es noch nicht gibt (K2: Tanne).
               Sobald es das Wort gibt, gehört die Zeile nach woerter
               (tests/test_ton_bedeutung.py meldet es).
  grammatik    "<lektion>#<nr>" -> Schlüssel der Antwort, nr ab 0 gezählt
               wie g._nr in web/js/inhalt.js.
  geschichten  Wort -> {"*": Schlüssel, "<geschichte>": Schlüssel oder
               [Schlüssel je Vorkommen]}. "*" gilt in jeder Geschichte ohne
               eigene Zeile und für das Satzwort in "Wörter dieses Levels",
               dessen Bedeutung aus dem WOERTERBUCH kommt.
  saetze       Wort-ID eines Satzes -> {Wort: Schlüssel}. Ausnahme vom "*"
               für das Satzwort in "Wörter dieses Levels" (21.11.2026): in
               „Sam izdržava cijelu porodicu.“ heißt „sam“ allein, nicht
               „bin“, in „ne smije“ heißt „smije“ darf, nicht „lacht“. Die
               Liste zeigt je Level nur das erste Vorkommen eines Worts, also
               gilt der Schlüssel für das Wort in diesem Satz. Hier darf auch
               das Wort selbst stehen ("sam": die Aufnahme wie bisher, sȃm).

Ein Schlüssel gleich dem Wort ("sam") heißt: die Aufnahme wie bisher.
"<wort> (<bedeutung>)" ("sam (bin)") ist eine eigene Aufnahme. Die spricht
Emir; sie kommt mit ihrer Nummer in ton_nur_emir.json (Text gleich dem
Schlüssel). Bis dahin findet die App den Schlüssel nicht und spielt die
Aufnahme wie bisher (eigenerTon() in ton_abspielen.js), also kein
Rückschritt. ton_bauen.sammle() nimmt diese Schlüssel bewusst NICHT auf:
sonst spräche Azure beim nächsten großen Lauf den Text „sam (bin)“.

Seit dem Abend des 21.11.2026 bekommt JEDE Bedeutung eine eigene Aufnahme
("dug (schulden)" und "dug (lang)"), statt dass eine die heutige Datei
behält. Welche Bedeutung die heutige trifft, hätte Ajdin für 16 Dateien
heraushören müssen. Nur sȃm (allein) behält "sam" (w1359): gemessen und
gehört. Bis Emir spricht, klingt alles wie heute.

Bosnisch und Wort-IDs ändern sich dadurch nicht. Die App bekommt je Stelle
nur ein Feld "ton" dazu, an Sätzen "satzwort_ton" (anwenden(), aufgerufen
in inhalt.lade_daten()).

Nur Bausteine, die Python schon mitbringt.
"""
import io
import json
import os

import ton_bauen                            # textwoerter(): dieselben Woerter wie die App

ORDNER = os.path.dirname(os.path.abspath(__file__))
TABELLE = os.path.join(ORDNER, "ton_bedeutung.json")
ABSCHNITTE = ("woerter", "vorgemerkt", "grammatik", "geschichten", "saetze")


def lade(pfad=None):
    """Die Tabelle, bei jedem Aufruf frisch gelesen (wie lade_daten() die
    Inhaltsdateien). Fehlt die Datei, sind alle Abschnitte leer."""
    pfad = pfad or TABELLE
    if not os.path.exists(pfad):
        return {k: {} for k in ABSCHNITTE}
    with io.open(pfad, encoding="utf-8") as f:
        daten = json.load(f)
    return {k: dict(daten.get(k) or {}) for k in ABSCHNITTE}


def wort_von(schluessel):
    """Das Wort eines Schlüssels: 'sam (bin)' -> 'sam', 'sam' -> 'sam'."""
    return str(schluessel).split(" (", 1)[0]


def eigen(schluessel):
    """Steht der Schlüssel für eine eigene Aufnahme (nicht die bisherige)?"""
    return bool(schluessel) and schluessel != wort_von(schluessel)


def _werte(wert):
    return list(wert) if isinstance(wert, list) else [wert]


def alle_schluessel(tabelle=None):
    """Jeder Schlüssel der Tabelle mit seiner Stelle, als Liste (stelle, schluessel)."""
    t = tabelle or lade()
    raus = []
    for abschnitt in ("woerter", "vorgemerkt", "grammatik"):
        raus += [("%s:%s" % (abschnitt, k), v) for k, v in t[abschnitt].items()]
    for wort, regeln in t["geschichten"].items():
        for wo, wert in regeln.items():
            raus += [("geschichten:%s:%s" % (wort, wo), k) for k in _werte(wert)]
    for satz, je_wort in t["saetze"].items():
        raus += [("saetze:%s:%s" % (satz, wort), k) for wort, k in je_wort.items()]
    return raus


def eigene_schluessel(tabelle=None):
    """Alle Schlüssel für eigene Aufnahmen, sortiert."""
    return sorted({k for _, k in alle_schluessel(tabelle) if eigen(k)})


def tabellenwoerter(tabelle=None):
    """Die Wörter, über deren Ton die Tabelle entscheidet."""
    t = tabelle or lade()
    return sorted({wort_von(k) for _, k in alle_schluessel(t)} | set(t["geschichten"]))


def geschichte_toene(g, regeln):
    """{wort: [schluessel oder None je Vorkommen]} für eine Geschichte, nur
    Wörter mit mindestens einer eigenen Aufnahme. None: wie bisher.

    Gezählt wird mit ton_bauen.textwoerter(), Zeichen für Zeichen dieselben
    Stücke wie die antippbaren Wörter in showStory() (geschichten.js), und
    klein geschrieben wie dort."""
    woerter = [w.lower() for w in ton_bauen.textwoerter(g.get("text") or "")]
    raus = {}
    for wort, regel in regeln.items():
        n = woerter.count(wort)
        if not n:
            continue
        wert = regel.get(g.get("id"), regel.get("*", wort))
        liste = _werte(wert) if isinstance(wert, list) else [wert] * n
        liste = [k if eigen(k) else None for k in liste]
        if any(liste):
            raus[wort] = liste
    return raus


def woerterbuch_ton(tabelle=None):
    """Der Ton der Satzwörter in "Wörter dieses Levels", deren Bedeutung aus dem
    WOERTERBUCH kommt: das "*" jedes Worts, wenn es eine eigene Aufnahme ist."""
    t = tabelle or lade()
    return {w: r["*"] for w, r in t["geschichten"].items() if eigen(r.get("*"))}


def _wort_mit_ton(w, je_id, je_satz):
    """Eine Vokabel oder ein Satz mit seinem Ton, als Kopie; ohne Ton das Original."""
    zusatz = {}
    if w.get("id") in je_id:
        zusatz["ton"] = je_id[w["id"]]
    if w.get("id") in je_satz:
        zusatz["satzwort_ton"] = dict(je_satz[w["id"]])
    return dict(w, **zusatz) if zusatz else w


def anwenden(daten, tabelle=None):
    """Trägt "ton" an Vokabeln, Grammatik-Übungen und Geschichten ein,
    "satzwort_ton" an die Sätze mit einer Ausnahme (Abschnitt "saetze"), und
    legt daten["woerterbuch_ton"] an (Satzwörter der Wortliste).

    Nur eigene Aufnahmen kommen hinein; wo die bisherige gilt, bleibt alles,
    wie es war. Ausnahme "satzwort_ton": dort steht auch das Wort selbst
    ("sam" für sȃm = allein), denn es weicht vom "*" ab. Geändertes wird
    kopiert, nie in die Moduldaten geschrieben: auf Deutsch gibt
    uebersetzungen.anwenden() die Listen aus geschichten.py und grammatik.py
    unverändert durch, und ein Eintrag dort bliebe bis zum nächsten reload
    stehen."""
    t = tabelle or lade()
    je_id = dict(t["woerter"])
    je_id.update(t["vorgemerkt"])
    je_id = {i: k for i, k in je_id.items() if eigen(k)}
    je_satz = {i: w for i, w in t["saetze"].items() if w}
    neu = dict(daten)

    kategorien = []
    for kat in daten.get("kategorien", []):
        if any(w.get("id") in je_id or w.get("id") in je_satz for w in kat.get("words", [])):
            kat = dict(kat, words=[_wort_mit_ton(w, je_id, je_satz) for w in kat["words"]])
        kategorien.append(kat)
    neu["kategorien"] = kategorien

    grammatik = dict(daten.get("grammatik") or {})
    for stelle, k in t["grammatik"].items():
        lektion, _, nr = stelle.partition("#")
        if not eigen(k) or lektion not in grammatik or not nr.isdigit():
            continue
        uebungen = list(grammatik[lektion].get("uebungen", []))
        if int(nr) < len(uebungen):
            uebungen[int(nr)] = dict(uebungen[int(nr)], ton=k)
            grammatik[lektion] = dict(grammatik[lektion], uebungen=uebungen)
    neu["grammatik"] = grammatik

    geschichten = []
    for g in daten.get("geschichten", []):
        toene = geschichte_toene(g, t["geschichten"])
        geschichten.append(dict(g, ton=toene) if toene else g)
    neu["geschichten"] = geschichten

    neu["woerterbuch_ton"] = woerterbuch_ton(t)
    return neu


FELDER = ("ton", "satzwort_ton")             # was anwenden() an einzelne Stellen schreibt


def stimmt(daten, tabelle=None):
    """Traegt ein gebauter Inhalt (web/inhalt/<sprache>.json) den Ton so, wie
    anwenden() ihn heute eintragen wuerde? Fuer app_bauen.inhalt_aktuell().

    Dazu werden "ton" und "satzwort_ton" entfernt und neu eingetragen. Ein
    Inhalt von vor dem 21.11.2026 hat sie gar nicht, einer von einer aelteren
    Tabelle andere: beide sind veraltet, auch wenn die Datei neuer ist als
    ton_bedeutung.json."""
    def ohne(x):
        return {k: v for k, v in x.items() if k not in FELDER} if isinstance(x, dict) else x
    grammatik = {lid: dict(lek, uebungen=[ohne(u) for u in lek["uebungen"]])
                 if isinstance(lek, dict) and "uebungen" in lek else lek
                 for lid, lek in (daten.get("grammatik") or {}).items()}
    roh = dict(daten,
               kategorien=[dict(k, words=[ohne(w) for w in k["words"]]) if "words" in k else k
                           for k in daten.get("kategorien", [])],
               grammatik=grammatik,
               geschichten=[ohne(g) for g in daten.get("geschichten", [])])
    roh.pop("woerterbuch_ton", None)
    soll = anwenden(roh, tabelle)
    return all(soll.get(f) == daten.get(f) for f in ("kategorien", "grammatik", "geschichten", "woerterbuch_ton"))
