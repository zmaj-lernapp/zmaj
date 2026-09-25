# -*- coding: utf-8 -*-
r"""Setzt den Lebens-Hinweis unter das Herz statt hinter die Muenzen.

GEMELDET am 24.09.2026 von einem Tester: "Wenn man oben links aufs Herz
klickt, erscheint die Angabe zum naechsten Herz nicht darunter, sondern
rechts daneben - hinter den Muenzen."

DIE URSACHE
Der Kopfbereich ist ein Raster mit drei Spalten (1fr auto 1fr). Die
Herzleiste sitzt in Spalte 1, die Muenzen in Spalte 2, die Knoepfe in
Spalte 3. Die beiden 1fr-Spalten sind gleich breit und werden von der
Muenzpille in der Mitte festgehalten - Spalte 1 kann nicht wachsen.

Die Leiste selbst ist inline-flex, also eine Zeile: der Hinweistext stellt
sich rechts neben das Herz. Beim Aufklappen waechst die Pille damit weit
ueber ihre Spalte hinaus. Weggeschoben wird nichts, weil das Raster fest
ist - stattdessen werden Muenzen und Knoepfe UEBER den Text gemalt, denn
sie stehen spaeter im Quelltext. Sichtbar bleiben nur Fetzen in den Luecken.

Die bisherigen Regeln (overflow:hidden, ellipsis, nowrap) sind der alte
Notbehelf: der Text darf abschneiden, statt die Knoepfe hinauszudraengen.
Das Ueberdecken beheben sie nicht.

DIE AENDERUNG
Reines CSS, kein JavaScript, kein neuer Knoten, keine neuen Texte.
Der Hinweis wird aus der Zeile genommen (position:absolute) und als eigene
kleine Pille unter das Herz gehaengt. Ein absolut gesetztes Kind zaehlt
nicht zur Flex-Zeile: die Herzpille bleibt beim Aufklappen genau so breit
wie zugeklappt, das Raster ruehrt sich nicht, und nichts darunter rutscht.

ZWEI DINGE, DIE DABEI BEDACHT SIND
1. Bei null Leben steht der Hinweis DAUERHAFT da - renderLives() setzt
   "const zeigen = livesInfoAn || n === 0" (Zeile 2504). Die schwebende
   Pille liegt dann staendig ueber dem Inhalt. Das ist hinnehmbar, weil
   bei null Leben ohnehin nicht gelernt werden kann (der Lektionsknopf ist
   gesperrt) und die Wartezeit genau die Angabe ist, die man dann sucht.
   pointer-events:none sorgt dafuer, dass sie keinen Tipp abfaengt.
2. Der Block wird als Ganzes ersetzt, weil ".livesbar .info" darin ZWEIMAL
   vorkommt (Zeile 470 und 477). Wer nur die erste Regel aendert, bekommt
   die Polsterung der zweiten zurueck.

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

Probelauf:  python herz_richten.py
Schreiben:  python herz_richten.py --schreiben
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SCHREIBEN = "--schreiben" in sys.argv
# Der Pfad wird aus dem Ort dieses Skripts abgeleitet, nicht fest eingetragen.
# Vorher stand hier der volle Pfad. Der Projektordner ist am 21.09.2026 schon
# einmal umgezogen; beim naechsten Umzug haette das Skript ins Leere gegriffen
# oder - schlimmer - in eine alte Kopie geschrieben.
ORDNER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(ORDNER, "web", "index.html")

ALT = """  .livesbar{
    display:inline-flex; align-items:center; gap:8px; background:var(--surface); border:2px solid var(--line);
    border-radius:99px; padding:3px 8px 3px 4px; font-size:13px; color:var(--muted); font-weight:700;
    width:auto; min-width:0;
  }
  /* In der Kopfzeile ist kein Platz fuer die ausgeklappte Wartezeit neben
     allem anderen - sie darf abschneiden statt die Knoepfe hinauszudraengen. */
  .livesbar .info{overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
  .livesbar .herz{
    display:inline-flex; align-items:center; gap:5px; background:none; border:0; cursor:pointer;
    font:inherit; font-size:17px; color:var(--bad); padding:3px 8px; border-radius:99px;
  }
  .livesbar .herz b{font-size:15px; color:var(--ink)}
  .livesbar .herz:hover{background:var(--primary-soft)}
  .livesbar .info{padding-right:4px}
  .livesbar.premium .herz{color:var(--accent-dark)}
  .livesbar.zero{border-color:var(--bad)}"""

NEU = """  .livesbar{
    display:inline-flex; align-items:center; gap:8px; background:var(--surface); border:2px solid var(--line);
    border-radius:99px; padding:3px 8px 3px 4px; font-size:13px; color:var(--muted); font-weight:700;
    width:auto; min-width:0;
    position:relative;          /* Bezugspunkt fuer den Hinweis darunter */
  }
  /* Die Wartezeit haengt UNTER der Herzpille, nicht daneben.
     Vorher stand sie in derselben Zeile; der Kopf ist aber ein Raster mit
     drei festen Spalten, und die Pille wuchs damit unter die Muenzen und
     Knoepfe, die spaeter im Quelltext stehen und darueber gemalt werden.
     Gemeldet am 24.09.2026.
     position:absolute nimmt sie aus der Zeile: die Herzpille bleibt
     aufgeklappt genauso breit wie zugeklappt, das Raster ruehrt sich
     nicht, und der Inhalt darunter rutscht nicht weg.
     pointer-events:none, weil sie ueber der Karte darunter schwebt und
     dort keinen Tipp abfangen soll. */
  .livesbar .info{
    position:absolute; top:calc(100% + 4px); left:0; z-index:5;
    background:var(--surface); border:2px solid var(--line); border-radius:99px;
    box-shadow:0 2px 0 var(--line); padding:2px 10px;
    font-size:11.5px; line-height:16px; font-weight:700;
    max-width:calc(100vw - 40px);
    overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
    pointer-events:none;
  }
  .livesbar .herz{
    display:inline-flex; align-items:center; gap:5px; background:none; border:0; cursor:pointer;
    font:inherit; font-size:17px; color:var(--bad); padding:3px 8px; border-radius:99px;
  }
  .livesbar .herz b{font-size:15px; color:var(--ink)}
  .livesbar .herz:hover{background:var(--primary-soft)}
  .livesbar.premium .herz{color:var(--accent-dark)}
  .livesbar.zero{border-color:var(--bad)}
  /* Bei null Leben steht der Hinweis dauerhaft (renderLives: zeigen =
     livesInfoAn || n === 0). Dann traegt er denselben roten Rand wie die
     Pille darueber, damit beide als ein Stueck zu lesen sind. */
  .livesbar.zero .info{border-color:var(--bad)}"""

text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

n = text.count(ALT)
if n != 1:
    print("ABBRUCH: der Stilblock steht %d mal da, erwartet genau einmal" % n)
    sys.exit(1)
text = text.replace(ALT, NEU, 1)
print("ok   Lebens-Hinweis haengt jetzt unter dem Herz")

# ------------------------------------------------------------ Nachkontrolle
fehler = []
for muss in ("position:relative;          /* Bezugspunkt",
             "position:absolute; top:calc(100% + 4px); left:0; z-index:5;",
             "pointer-events:none;",
             ".livesbar.zero .info{border-color:var(--bad)}"):
    if muss not in text:
        fehler.append("%r fehlt" % muss)
# Die doppelte Regel darf es nicht mehr geben
if text.count(".livesbar .info{") != 1:
    fehler.append(".livesbar .info steht %d mal da, erwartet einmal"
                  % text.count(".livesbar .info{"))
if ".livesbar .info{padding-right:4px}" in text:
    fehler.append("die alte zweite Regel steht noch drin")
# Was bleiben muss
for lebt in (".livesbar .herz{", ".livesbar.premium .herz", ".livesbar.zero{border-color",
             "const zeigen = livesInfoAn || n === 0;"):
    if lebt not in text:
        fehler.append("%r ist verlorengegangen" % lebt)
# Klammern im Gleichgewicht
if text.count("{") != text.count("}"):
    fehler.append("geschweifte Klammern aus dem Gleichgewicht (%d zu %d)"
                  % (text.count("{"), text.count("}")))
# Kein offener Kommentar
if text.count("/*") != text.count("*/"):
    fehler.append("ein Kommentar ist nicht geschlossen (%d zu %d)"
                  % (text.count("/*"), text.count("*/")))

if fehler:
    print("\nABBRUCH - nichts geschrieben:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")
print()
print("   Was sich aendert:")
print("     zugeklappt      unveraendert")
print("     aufgeklappt     Hinweis als eigene Pille unter dem Herz,")
print("                     Kopfzeile bleibt gleich hoch")
print("     null Leben      Hinweis dauerhaft, mit rotem Rand")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\nGeschrieben.")
    print("Danach: app_bauen.py - aber NICHT vor dem 07.10.2026 einreichen.")
else:
    print("\n(Probelauf.)")
