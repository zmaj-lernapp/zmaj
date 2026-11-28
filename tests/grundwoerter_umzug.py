# -*- coding: utf-8 -*-
"""Die 40 Grundwoerter, die am 13.11.2026 aus B1 in zwei neue A-Level gezogen
sind (Stufen-Reiter, Variante B, Ajdin: „alles wie empfohlen“).

Die Tests der Wortschatz-Pakete 1 bis 9 pruefen, was damals geliefert wurde:
je Level Wort, Beispielsatz, Wort, Beispielsatz, die Zahl der Eintraege und die
Nummern der Aufnahmen. Mit vor_umzug() sehen sie die Level so, wie sie
geliefert wurden - die Wortkarten an ihrem alten Platz, die zwei neuen Level
weg. Was der Umzug selbst verspricht (Kennung bleibt, Beispielsatz bleibt in
B1, nichts doppelt), prueft tests/test_reiter.py am echten Inhalt.

UMZUG: (neues Level, bs, de, altes Level, alter Platz in "words")."""
import copy

UMZUG = [
    ("kleine_woerter", "ovdje", "hier", "hier_dort", 2),
    ("kleine_woerter", "tamo", "dort", "hier_dort", 4),
    ("kleine_woerter", "tu", "da / hier", "hier_dort", 0),
    ("kleine_woerter", "gore", "oben", "hier_dort", 6),
    ("kleine_woerter", "dolje", "unten", "hier_dort", 8),
    ("kleine_woerter", "onda", "dann", "wann_wie_oft", 0),
    ("kleine_woerter", "zatim", "danach", "wann_wie_oft", 2),
    ("kleine_woerter", "prvo", "zuerst", "wann_wie_oft", 14),
    ("kleine_woerter", "opet", "wieder", "sofort_endlich", 18),
    ("kleine_woerter", "odmah", "sofort", "sofort_endlich", 0),
    ("kleine_woerter", "stalno", "ständig", "wann_wie_oft", 10),
    ("kleine_woerter", "tako", "so", "wie_sehr", 0),
    ("kleine_woerter", "vrlo / veoma", "sehr (vor Eigenschaften)", "wie_sehr", 4),
    ("kleine_woerter", "rado", "gern", "wie_sehr", 16),
    ("kleine_woerter", "kao", "wie / als", "saetze_verbinden", 0),
    ("kleine_woerter", "pa", "und dann / also", "saetze_verbinden", 2),
    ("kleine_woerter", "evo", "hier ist / da ist", "saetze_verbinden", 24),
    ("kleine_woerter", "taj", "dieser (da)", "fuerwoerter", 2),
    ("kleine_woerter", "sav", "ganz / all", "ganz_viele", 0),
    ("kleine_woerter", "cijeli", "ganz (der ganze)", "ganz_viele", 2),
    ("jeden_tag", "ime", "Name", "alltag_information", 4),
    ("jeden_tag", "prezime", "Nachname", "alltag_information", 6),
    ("jeden_tag", "adresa", "Adresse", "alltag_information", 8),
    ("jeden_tag", "telefon", "Telefon", "alltag_information", 10),
    ("jeden_tag", "roditelji", "Eltern", "menschen", 2),
    ("jeden_tag", "osoba", "Person", "menschen", 0),
    ("jeden_tag", "hrana", "Essen / Nahrung", "alltag_information", 0),
    ("jeden_tag", "piće", "Getränk", "alltag_information", 2),
    ("jeden_tag", "lice", "Gesicht", "koerper_aussen", 0),
    ("jeden_tag", "život", "das Leben", "das_leben", 0),
    ("jeden_tag", "mjesto", "Ort / Platz", "ort_raum", 0),
    ("jeden_tag", "dio", "Teil", "menge_teil", 0),
    ("jeden_tag", "početak", "Anfang", "anfang_ende", 0),
    ("jeden_tag", "kraj", "Ende", "anfang_ende", 2),
    ("jeden_tag", "problem", "Problem", "dinge_regeln", 0),
    ("jeden_tag", "slika", "Bild / Foto", "hobbys", 12),
    ("jeden_tag", "priča", "Geschichte (Erzählung)", "alltag_information", 12),
    ("jeden_tag", "igra", "Spiel (zum Spielen)", "hobbys", 26),
    ("jeden_tag", "film", "Film", "medien", 12),
    ("jeden_tag", "broj", "Zahl / Nummer", "menge_teil", 2),
]
NEUE_LEVEL = ("kleine_woerter", "jeden_tag")


def kategorien_vor_umzug(kategorien):
    """Kopie der Level-Liste mit den 40 Wortkarten an ihrem alten Platz und
    ohne die zwei neuen Level. Geht mit vokabeln.KATEGORIEN wie mit den Daten
    aus inhalt.lade_daten() (dann mit Kennung)."""
    kat = copy.deepcopy(list(kategorien))
    nach_id = {k["id"]: k for k in kat}
    for ziel, bs, de, alt, platz in sorted(UMZUG, key=lambda u: (u[3], u[4])):
        neu = nach_id[ziel]["words"]
        wort = next(w for w in neu if w["bs"] == bs and w["de"] == de)
        nach_id[alt]["words"].insert(platz, wort)
    return [k for k in kat if k["id"] not in NEUE_LEVEL]


def vor_umzug(daten):
    """Die Daten aus inhalt.lade_daten(), Level wie vor dem 13.11.2026."""
    d = dict(daten)
    d["kategorien"] = kategorien_vor_umzug(daten["kategorien"])
    return d
