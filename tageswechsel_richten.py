# -*- coding: utf-8 -*-
r"""
tageswechsel_richten.py  –  die Startseite merkt, wenn ein neuer Tag begonnen hat

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" tageswechsel_richten.py
    ... --schreiben

DAS PROBLEM (gefunden am 26.09.2026)

Wer abends lernt, die App auf der Startseite liegen lässt und sie am
nächsten Morgen aus dem Hintergrund hervorholt, sieht den Stand von
gestern: den jubelnden Drachen, „Heute geübt" mit der Serienzahl von
gestern, alle drei Tagesaufgaben abgehakt und „Alle drei geschafft".

Der Grund: renderHero() und renderQuests() laufen nur aus showHome().
Der visibilitychange-Horcher startet beim Zurückkommen bloß die Lernuhr,
und der einzige Zeitgeber zeichnet ausschließlich renderLives().

Das ist nicht nur ein Anzeigefehler. Wer glaubt, er habe heute schon
geübt, lernt an diesem Tag nicht — und verliert die Lernserie, weil `days`
den neuen Tag nie bekommt.

DIE LÖSUNG

Ein Merker mit dem zuletzt gezeichneten Tag. Er wird an zwei Stellen
geprüft, die es ohnehin schon gibt:

  visibilitychange   beim Zurückholen aus dem Hintergrund
  setInterval        alle 30 Sekunden, für die App, die offen liegenbleibt

Hat sich der Tag geändert und der Nutzer steht auf der Startseite, wird
sie neu gezeichnet. Steht er woanders — mitten in einer Lektion —, merkt
sich der Merker den neuen Tag trotzdem, damit nicht später grundlos neu
gezeichnet wird.
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


# ------------------------------------------- 1. Merker und Prüffunktion
t("Tageswaechter anlegen und an den Zeitgeber haengen",
  """setInterval(renderLives, 30000);""",

  """/* Wer die App abends auf der Startseite liegen laesst und sie morgens
   wieder hervorholt, sah bisher den Stand von gestern: "Heute geuebt",
   die alte Serienzahl und alle drei Tagesaufgaben abgehakt. renderHero()
   und renderQuests() laufen naemlich nur aus showHome(), und der einzige
   Zeitgeber zeichnete bloss renderLives().
   Das ist nicht nur schief angezeigt: wer glaubt, er haette heute schon
   geuebt, lernt nicht - und verliert die Serie, weil days den neuen Tag
   nie bekommt. Gefunden am 26.09.2026. */
let letzterTag = today();
function tagPruefen(){
  const jetzt = today();
  if(jetzt === letzterTag) return false;
  letzterTag = jetzt;
  /* Nur zeichnen, wenn die Startseite ueberhaupt sichtbar ist. Mitten in
     einer Lektion wuerde showHome() die Aufgabe wegreissen. Der Merker
     steht trotzdem schon auf heute, damit es spaeter nicht grundlos
     nachzieht - showLevelHome() zeichnet die Startseite ohnehin neu. */
  if(sichtbar('pfad')) showHome();
  return true;
}
setInterval(()=>{ tagPruefen(); renderLives(); }, 30000);""")

# ------------------------------------------- 2. beim Zurueckholen pruefen
t("Beim Zurueckholen aus dem Hintergrund pruefen",
  """  else if(uhrWarAn){ uhrWarAn = false; uhrAn(); }
});""",

  """  else {
    /* Zuerst der Tageswechsel: ueber Nacht im Hintergrund ist der
       haeufigste Fall, und er faellt sonst erst auf, wenn die Serie
       schon gerissen ist. */
    tagPruefen();
    if(uhrWarAn){ uhrWarAn = false; uhrAn(); }
  }
});""")


# ---------------------------------------------------------------- anwenden
text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

for baustein, wo in (("const today = ()", "today()"),
                     ("function showHome(", "showHome()"),
                     ("function sichtbar(id)", "sichtbar()"),
                     ("function renderLives(", "renderLives()")):
    if baustein not in text:
        print("ABBRUCH: %s fehlt in index.html" % wo)
        sys.exit(1)
print("   Bausteine vorhanden: today(), showHome(), sichtbar(), renderLives()")

if "function tagPruefen" in text:
    print("ABBRUCH: der Tageswaechter steht schon in index.html")
    sys.exit(1)

print()
for was, alt, neu in ersetzungen:
    n = text.count(alt)
    if n != 1:
        print("ABBRUCH bei \u201e%s\u201c: %d Treffer statt 1" % (was, n))
        print("   gesucht: %s" % alt.strip().splitlines()[0][:78])
        sys.exit(1)
    text = text.replace(alt, neu)
    print("   ok   %s" % was)

# ------------------------------------------------------------ Nachkontrollen
fehler = []
if text.count("function tagPruefen") != 1:
    fehler.append("tagPruefen() steht nicht genau einmal da")
# Definition plus zwei Aufrufe
if text.count("tagPruefen(") != 3:
    fehler.append("tagPruefen kommt %d mal vor, erwartet 3" % text.count("tagPruefen("))
if text.count("let letzterTag") != 1:
    fehler.append("der Merker steht nicht genau einmal da")
if "setInterval(renderLives, 30000)" in text:
    fehler.append("der alte Zeitgeber steht noch da")
if text.count("setInterval(()=>{ tagPruefen(); renderLives(); }, 30000)") != 1:
    fehler.append("der neue Zeitgeber fehlt")
if fehler:
    print("\nABBRUCH, Nachkontrolle:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")

print()
print("   Was sich aendert:")
print("     App liegt ueber Nacht offen  -> morgens steht der neue Tag da")
print("     App kommt aus dem Hintergrund -> Tageswechsel wird sofort geprueft")
print("     mitten in einer Lektion      -> nichts wird weggerissen, der")
print("                                     Merker zieht still nach")
print()
print("     Keine neuen Texte. Der Zeitgeber laeuft weiter alle 30 Sekunden.")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\ngeschrieben: %s" % os.path.basename(ZIEL))
else:
    print("\n(Probelauf.)")
