# -*- coding: utf-8 -*-
r"""
entwurf_technik_pruefen.py  -  prüft den Entwurf gegen den Bestand

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" entwurf_technik_pruefen.py

Liest nur, schreibt nichts. Gemeldet wird:
  1. ein bosnisches Wort (oder eine seiner Formen hinter " / "), das schon
     in einem Level steht
  2. eine deutsche Zeile ohne alle sieben Übersetzungen
  3. ein deutscher Text, den uebersetzungen.py schon kennt - mit einer
     ANDEREN Übersetzung. Dort gilt der deutsche Text als Schlüssel für die
     ganze App, der Entwurf würde also den Bestand umschreiben.
  4. je Sprache eine neue Bedeutung, die wörtlich schon zu einem anderen
     bosnischen Wort gehört. Dann wäre die Auswahlaufgabe nicht entscheidbar
     (siehe geschwister() in web/index.html).
"""
import vokabeln
import uebersetzungen
import entwurf_technik as E

fehler = 0


def melde(text):
    global fehler
    fehler += 1
    print("  " + text)


def formen(bs):
    return [f.strip().lower() for f in bs.split(" / ") if f.strip()]


bestand = {}
for k in vokabeln.KATEGORIEN:
    for w in k["words"]:
        for f in formen(w["bs"]):
            bestand.setdefault(f, []).append(k["id"])

print("1. Schon vorhandene bosnische Wörter")
neu_bs = [w for L in E.LEVEL for w in L["words"]]
for w in neu_bs:
    for f in formen(w["bs"]):
        if f in bestand:
            melde("%s  steht schon in %s" % (f, ", ".join(bestand[f])))
ids = [L["id"] for L in E.LEVEL]
for i in ids:
    if any(k["id"] == i for k in vokabeln.KATEGORIEN):
        melde("Level-Kennung %s gibt es schon" % i)
alle_neu = [f for w in neu_bs for f in formen(w["bs"])]
for f in set(alle_neu):
    if alle_neu.count(f) > 1:
        melde("%s  steht im Entwurf zweimal" % f)

print("2. Fehlende Übersetzungen")
deutsch = set()
for L in E.LEVEL:
    deutsch.update([L["label"], L["tipp"]])
    deutsch.update(w["de"] for w in L["words"])
deutsch.update(s["de"] for s in E.SAETZE)
for code in E.SPRACHEN:
    fehlt = [d for d in deutsch if not E.UEBERSETZUNGEN[code].get(d)]
    for d in fehlt:
        melde("%s: %s" % (code, d))
    zuviel = [d for d in E.UEBERSETZUNGEN[code] if d not in deutsch]
    for d in zuviel:
        melde("%s: übersetzt, kommt aber nicht vor: %s" % (code, d))

print("3. Deutsche Schlüssel, die uebersetzungen.py schon anders kennt")
for code in E.SPRACHEN:
    tabelle = uebersetzungen.INHALT.get(code, {}).get("texte", {})
    for d in sorted(deutsch):
        if d in tabelle and tabelle[d] != E.UEBERSETZUNGEN[code][d]:
            melde("%s: %r  Bestand %r  Entwurf %r" % (code, d, tabelle[d], E.UEBERSETZUNGEN[code][d]))

print("4. Gleiche Bedeutung wie ein anderes Wort")


def norm(s):
    return " ".join(str(s).lower().rstrip(".!?…").split())


for code in ["de"] + E.SPRACHEN:
    if code == "de":
        t = lambda d: d
        woe = {}
    else:
        tabelle = uebersetzungen.INHALT.get(code, {}).get("texte", {})
        woe = uebersetzungen.INHALT.get(code, {}).get("woerter", {})
        t = lambda d, tabelle=tabelle: tabelle.get(d, d)
    alt = {}
    for k in vokabeln.KATEGORIEN:
        for w in k["words"]:
            alt.setdefault(norm(woe.get(w["bs"], t(w["de"]))), set()).add(w["bs"])
    neu = {}
    for w in neu_bs:
        b = norm(w["de"] if code == "de" else E.UEBERSETZUNGEN[code][w["de"]])
        if b in alt and w["bs"] not in alt[b]:
            melde("%s: %r bedeutet schon %s" % (code, b, ", ".join(sorted(alt[b]))))
        neu.setdefault(b, set()).add(w["bs"])
    for b, bs in neu.items():
        if len(bs) > 1:
            melde("%s: %r zweimal im Entwurf: %s" % (code, b, ", ".join(sorted(bs))))

print()
print("Wörter: %d in %d Level, Sätze: %d" % (len(neu_bs), len(E.LEVEL), len(E.SAETZE)))
print("Befunde: %d" % fehler if fehler else "Keine Befunde.")
