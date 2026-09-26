# -*- coding: utf-8 -*-
r"""
muenzen_richten.py  –  die drei Knöpfe oben fragen nach, bevor sie eine
                       laufende Lektion wegwerfen

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" muenzen_richten.py
    ... --schreiben

DAS PROBLEM (gefunden am 26.09.2026, selbst nachgestellt):

Münzanzeige, Einkaufswagen und Zahnrad stehen auch während einer Lektion oben
in der Kopfzeile. Lektion und Level-Test sind Unteransichten innerhalb von
levelView und laufen nicht über showView(), deshalb bleibt die Kopfzeile
stehen. Ein Tipp auf einen der drei wechselt sofort weg.

Nachgestellt im Browser:

    vorher    Lektion läuft, Aufgabe 1 von 12
    Tipp auf die Münzanzeige
    nachher   Laden offen, keine Nachfrage, Lektion weg
              Zurück-Knopf führt zur Startseite, nicht in die Lektion
              Level neu öffnen: lBody ist leer, die Lektion ist nicht zurück

Der Knopf „Lektion abbrechen" daneben fragt ausdrücklich nach, und die
Zurück-Taste des Handys ruft genau diesen Knopf. Nur der Weg über die
Kopfzeile geht daran vorbei. Die Münzanzeige speichert dabei nicht einmal.

Besonders bitter: Man tippt auf die Münzen, WEIL man ein Herz kaufen will –
also gerade dann, wenn nur noch wenig Leben übrig ist.

WAS SICH ÄNDERT: Alle drei fragen jetzt dasselbe wie der Abbrechen-Knopf.
Keine neuen Texte – lektion.abbrechen_frage und die drei anderen gibt es
bereits in allen acht Sprachen.
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


# ------------------------------------------------- 1. die gemeinsame Wache
t("Wache einbauen und die Muenzanzeige daran haengen",
  """// Ein Tipp auf die Muenzen fuehrt dorthin, wo man sie ausgibt.
$('muenzBar').addEventListener('click', showLaden);""",

  """/* Muenzanzeige, Einkaufswagen und Zahnrad stehen auch waehrend einer
   Lektion oben, weil Lektion und Test Unteransichten von levelView sind und
   nicht ueber showView() laufen. Wer einen davon antippt, verliert sonst die
   angefangene Lektion ohne Warnung - die verbrauchten Leben bleiben
   verbraucht, und zurueck fuehrt nur auf die Startseite. Der Knopf "Lektion
   abbrechen" daneben fragt laengst nach, die Zurueck-Taste des Handys ruft
   genau diesen Knopf. Gefunden am 26.09.2026.
   Gefragt wird nur, wenn wirklich eine Lektion oder ein Test laeuft. */
async function lektionDarfWeg(){
  const laeuft = (sichtbar('lesson') && Lx && Lx.i < Lx.queue.length) ||
                 (sichtbar('test')   && Tx && Tx.i < Tx.queue.length);
  if(!laeuft) return true;
  return await frage(t('lektion.abbrechen_frage'), t('lektion.abbrechen_hinweis'),
                     t('btn.abbrechen'), t('btn.weitermachen'));
}
// Ein Tipp auf die Muenzen fuehrt dorthin, wo man sie ausgibt.
$('muenzBar').addEventListener('click', async ()=>{
  if(!await lektionDarfWeg()) return;
  await saveProgress(); showLaden();
});""")

# ------------------------------------------------- 2. der Einkaufswagen
t("Einkaufswagen fragt nach",
  """$('btnShop').addEventListener('click', async ()=>{ await saveProgress(); showLaden(); });""",
  """$('btnShop').addEventListener('click', async ()=>{
  if(!await lektionDarfWeg()) return;
  await saveProgress(); showLaden();
});""")

# ------------------------------------------------- 3. das Zahnrad
t("Zahnrad fragt nach",
  """$('btnSettings').addEventListener('click', async ()=>{ await saveProgress(); showSettings(); });""",
  """$('btnSettings').addEventListener('click', async ()=>{
  if(!await lektionDarfWeg()) return;
  await saveProgress(); showSettings();
});""")


# ---------------------------------------------------------------- anwenden
text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

# Die Bausteine muessen da sein, sonst laeuft die Wache ins Leere
for baustein, wo in (("function sichtbar(id)", "sichtbar()"),
                     ("function frage(titel, text, ja, nein)", "frage()"),
                     ("lektion.abbrechen_frage", "der Abbrechen-Text"),
                     ("let Lx", "Lx"),
                     ("let Tx", "Tx")):
    if baustein not in text:
        print("ABBRUCH: %s fehlt in index.html" % wo)
        sys.exit(1)
print("   Bausteine vorhanden: sichtbar(), frage(), Lx, Tx, die Texte")

if "async function lektionDarfWeg" in text:
    print("ABBRUCH: die Wache steht schon in index.html")
    sys.exit(1)

print()
for was, alt, neu in ersetzungen:
    n = text.count(alt)
    if n != 1:
        print("ABBRUCH bei \u201e%s\u201c: %d Treffer statt 1" % (was, n))
        print("   gesucht: %s" % alt.splitlines()[0][:80])
        sys.exit(1)
    text = text.replace(alt, neu)
    print("   ok   %s" % was)

# ------------------------------------------------------------ Nachkontrollen
fehler = []
if text.count("async function lektionDarfWeg") != 1:
    fehler.append("die Wache steht nicht genau einmal da")
if text.count("await lektionDarfWeg()") != 3:
    fehler.append("die Wache wird nicht von genau drei Knoepfen gerufen")
if "$('muenzBar').addEventListener('click', showLaden)" in text:
    fehler.append("die Muenzanzeige haengt noch direkt an showLaden")
# Der Abbrechen-Knopf muss unveraendert weiter fragen
if "$('lQuit').addEventListener" not in text:
    fehler.append("der Abbrechen-Knopf ist verschwunden")
if fehler:
    print("\nABBRUCH, Nachkontrolle:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")

print()
print("   Was sich aendert:")
print("     Lektion laeuft, Tipp auf Muenzen/Wagen/Zahnrad")
print("                        -> fragt wie der Abbrechen-Knopf")
print("     nichts laeuft      -> unveraendert, keine Frage")
print("     Muenzanzeige       -> speichert jetzt auch, wie die beiden Nachbarn")
print()
print("     Keine neuen Texte. Der Abbrechen-Knopf bleibt, wie er ist.")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\ngeschrieben: %s" % os.path.basename(ZIEL))
else:
    print("\n(Probelauf.)")
