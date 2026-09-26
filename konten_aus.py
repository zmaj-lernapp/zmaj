# -*- coding: utf-8 -*-
r"""
konten_aus.py  –  versteckt Anmeldung und Konten auch am PC

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" konten_aus.py
    ... --schreiben

WARUM: Auf dem Handy gibt es keine Anmeldung. Dort antwortet niemand auf
/api/konto, serverDa bleibt false, und die App springt mit einem
Platzhalternamen direkt hinein. Am PC antwortet start.py – und genau dann
erscheinen Anmeldeformular, Konto löschen und Profilknopf wieder.

Ajdin am 26.09.2026: die Anmeldung soll überall weg sein, bis ein Server
gemietet ist, und nachträglich wieder einschaltbar bleiben.

WIE: Ein Schalter KONTEN_AN, an einer Stelle zu ändern. Steht er auf false,
wird /api/konto gar nicht erst gefragt und MIT_SERVER bleibt überall false.
Damit verhält sich die App am PC exakt wie auf dem Handy.

WARUM NICHT EINFACH zeigeAnmeldung() AUSKOMMENTIEREN: Weil MIT_SERVER dann
auf true stehen bliebe. saveProgress() schreibt in diesem Fall per POST an
/api/fortschritt – mit einem Profilnamen, den der Server nicht kennt. Der
Lernstand ginge verloren, ohne dass die App etwas meldet. Genau dieser
Fehler ist am 20.09.2026 schon einmal aufgetreten, der Kommentar an
holeInhalt() beschreibt ihn.

WIEDER EINSCHALTEN: In index.html KONTEN_AN auf true setzen. Sonst nichts.
Das Anmelde-HTML, zeigeAnmeldung(), die Kontoverwaltung und die /api-Wege
bleiben alle unverändert im Programm stehen.
"""

import io
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, "web", "index.html")
SCHREIBEN = "--schreiben" in sys.argv

ersetzungen = []


def t(was, alt, neu):
    ersetzungen.append((was, alt, neu))


# ------------------------------------------------------- 1. der Schalter
t("Schalter KONTEN_AN anlegen",
  """let MIT_SERVER = false;""",

  """let MIT_SERVER = false;
/* ===== Konten an oder aus? =====
   Steht dieser Schalter auf false, verhaelt sich die App ueberall so wie auf
   dem Handy: kein Anmeldeformular, kein Profilknopf, kein "Konto loeschen",
   und der Lernstand liegt im Geraetespeicher. /api/konto wird dann gar nicht
   erst gefragt.

   Ajdin am 26.09.2026: die Anmeldung soll weg bleiben, bis ein Server
   gemietet ist. Zum Wiedereinschalten genuegt true - das Anmelde-HTML,
   zeigeAnmeldung() und die Kontoverwaltung stehen alle noch im Programm.

   WICHTIG: Der Schalter muss MIT_SERVER mitsteuern, nicht nur die Anzeige.
   Bliebe MIT_SERVER auf true, schriebe saveProgress() per POST an
   /api/fortschritt mit einem Profil, das der Server nicht kennt - der
   Lernstand waere weg, ohne Meldung. Dieser Fehler ist am 20.09.2026 schon
   einmal aufgetreten. */
const KONTEN_AN = false;""")

# ------------------------------- 2. holeInhalt() setzt MIT_SERVER nicht mehr
t("holeInhalt() an den Schalter haengen",
  """    if(r.ok){ const d = await r.json(); MIT_SERVER = true; return d; }""",
  """    if(r.ok){ const d = await r.json(); if(KONTEN_AN) MIT_SERVER = true; return d; }""")

# ------------------------------------- 3. /api/konto gar nicht erst fragen
t("Kontoabfrage ueberspringen",
  """  let konto = {angemeldet:false}, serverDa = false;
  try{
    const r = await fetch('/api/konto');
    if(r.ok){ konto = await r.json(); serverDa = true; }
  }catch(e){}
  MIT_SERVER = serverDa;""",

  """  let konto = {angemeldet:false}, serverDa = false;
  if(KONTEN_AN){
    try{
      const r = await fetch('/api/konto');
      if(r.ok){ konto = await r.json(); serverDa = true; }
    }catch(e){}
  }
  MIT_SERVER = serverDa;""")


# ---------------------------------------------------------------- anwenden
text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

if "const KONTEN_AN" in text:
    print("ABBRUCH: der Schalter steht schon in index.html")
    sys.exit(1)

for baustein, wo in (("nachAnmeldung({name: t('profil.ich')})", "der Weg ohne Konto"),
                     ("$('btnProfil').style.display = MIT_SERVER", "der Profilknopf")):
    if baustein not in text:
        print("ABBRUCH: %s fehlt in index.html" % wo)
        sys.exit(1)
print("   Bausteine vorhanden: der Weg ohne Konto, der Profilknopf")

print()
for was, alt, neu in ersetzungen:
    n = text.count(alt)
    if n != 1:
        print("ABBRUCH bei \u201e%s\u201c: %d Treffer statt 1" % (was, n))
        sys.exit(1)
    text = text.replace(alt, neu)
    print("   ok   %s" % was)

# ------------------------------------------------------------ Nachkontrollen
fehler = []
if text.count("const KONTEN_AN = false;") != 1:
    fehler.append("der Schalter steht nicht genau einmal da")
if text.count("if(KONTEN_AN)") != 2:
    fehler.append("der Schalter wird nicht an genau zwei Stellen abgefragt")
# Alles andere muss unveraendert bleiben - es soll nur versteckt sein
for baustein, wo in (("function zeigeAnmeldung(", "zeigeAnmeldung()"),
                     ("'/api/konto/loeschen'", "Konto loeschen"),
                     ("async function abmelden()", "abmelden()"),
                     ("nachAnmeldung({name: t('profil.ich')})", "der Weg ohne Konto")):
    if baustein not in text:
        fehler.append("%s wurde versehentlich entfernt" % wo)
if text.count("MIT_SERVER = true") != 1:
    fehler.append("MIT_SERVER wird an unerwarteter Stelle gesetzt")
if fehler:
    print("\nABBRUCH, Nachkontrolle:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")
print("   Nichts geloescht - zeigeAnmeldung(), Kontoverwaltung und die")
print("   /api-Wege stehen unveraendert im Programm.")

print()
print("   Was sich aendert (am PC, das Handy war schon so):")
print("     Start                 kein /api/konto mehr, direkt hinein")
print("     Anmeldeformular       bleibt versteckt")
print("     Profilknopf oben      verschwindet (haengt an MIT_SERVER)")
print("     Konto loeschen        bleibt versteckt")
print("     Lernstand             liegt im Browserspeicher, wie am Handy")
print("     Rueckmeldung          geht per Mailprogramm, wie am Handy")
print()
print("   Wieder einschalten: KONTEN_AN auf true setzen. Sonst nichts.")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\ngeschrieben: %s" % os.path.basename(ZIEL))
else:
    print("\n(Probelauf.)")
