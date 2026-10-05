# -*- coding: utf-8 -*-
r"""
huelle.py  –  wo liegt die Android-Hülle?

Die Hülle (Capacitor, privates Repository zmaj-lernapp/zmaj-huelle) liegt
neben diesem Projekt. Am eigenen Rechner heißt der Ordner seit jeher
`zmaj-android`; ein frischer `git clone` legt ihn aber als `zmaj-huelle`
an. Bis zum 04.10.2026 kannten app_bauen.py, admob_scharf.py und
projekt_sichern.py nur den ersten Namen und brachen nach einem neuen
Klon mit "Die Android-Hülle fehlt" ab.

Reihenfolge: Umgebungsvariable ZMAJ_HUELLE, dann ../zmaj-android, dann
../zmaj-huelle. Gibt es keinen davon, kommt ../zmaj-android zurück, damit
die Fehlermeldung den gewohnten Pfad nennt.
"""
import os

HIER = os.path.dirname(os.path.abspath(__file__))
NAMEN = ("zmaj-android", "zmaj-huelle")


def ordner(umgebung=None, basis=None):
    """Pfad zur Android-Hülle (muss nicht existieren)."""
    umgebung = os.environ if umgebung is None else umgebung
    basis = os.path.dirname(HIER) if basis is None else basis
    if umgebung.get("ZMAJ_HUELLE"):
        return os.path.abspath(umgebung["ZMAJ_HUELLE"])
    for name in NAMEN:
        pfad = os.path.join(basis, name)
        if os.path.isdir(pfad):
            return pfad
    return os.path.join(basis, NAMEN[0])
