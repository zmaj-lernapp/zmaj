# -*- coding: utf-8 -*-
r"""Ein Weg zurueck ins Hauptmenue nach jeder abgeschlossenen Lektion.

GEMELDET am 24.09.2026 von einem Tester: "Nachdem man eine Lektion geschafft
hat - egal ob Geschichte oder Vokabeltest - sollte es einen Knopf zurueck
zum Hauptmenue geben."

DIE LAGE
Der Vokabeltest endet mit zwei Knoepfen: "Zurueck zum Level" und "Noch eine
Lektion". Der erste fuehrt zu showLevelHome() - also in die Uebersicht DES
LEVELS, nicht ins Hauptmenue. Die Geschichte endet mit "Fragen nochmal" und
"Naechste Geschichte" und hat gar keinen Ausgang.

Am PC faellt das nicht auf, weil oben ein Zurueck-Knopf steht. Auf dem Handy
blendet setzeZurueck() ihn grundsaetzlich aus, sobald das Capacitor-Plugin
da ist - dort verlaesst sich die App auf die Geraetetaste. Wer die nicht
benutzt (oder eine Gestensteuerung hat, bei der sie nicht offensichtlich
ist), sitzt nach jeder Lektion fest. Gemeldet wurde es vom Handy.

DIE AENDERUNG
Unter die vorhandene Knopfreihe kommt eine zweite, schmale mit EINEM leisen
Knopf. Nicht ein dritter Knopf in dieselbe Reihe: .btn hat flex:1, drei
nebeneinander werden auf einem Handy zu schmal.

Die schmale Reihe gibt es schon - .row.schmal (Zeile 567) macht den Knopf
kleiner und leiser. Genau dafuer ist sie da: "Nebenangebote - kleiner und
leiser als der Hauptknopf darueber."

KEINE NEUEN TEXTE
Beide Beschriftungen stehen bereits in sprachen.py, in allen acht Sprachen:
    btn.zurueck_pfad          "← Lernpfad"
    btn.zurueck_geschichten   "← Geschichten"
Und das Muster fuer den Sprung ist ebenfalls vorhanden (Zeile 3937, 4057):
    homeMode='words'; showHome();

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

Probelauf:  python zurueck_richten.py
Schreiben:  python zurueck_richten.py --schreiben
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

A = []


def t(name, alt, neu):
    A.append((name, alt, neu))


# ------------------------------------------------- 1. nach dem Vokabeltest
t("Vokabeltest: Weg in den Lernpfad",
  """    '<div class="row"><button class="btn ghost" id="lHome">'+t('lektion.zurueck')+'</button><button class="btn know" id="lMore">'+t('lektion.noch_eine')+'</button></div>';
  $('lHome').addEventListener('click', showLevelHome);
  $('lMore').addEventListener('click', startLesson);""",
  """    '<div class="row"><button class="btn ghost" id="lHome">'+t('lektion.zurueck')+'</button><button class="btn know" id="lMore">'+t('lektion.noch_eine')+'</button></div>'+
    /* Zweite, leise Reihe: der Weg ganz heraus. "Zurueck zum Level" fuehrt
       nur in die Uebersicht DIESES Levels - auf dem Handy ist der
       Zurueck-Knopf oben ausgeblendet, und ohne diesen Knopf sitzt man
       nach jeder Lektion fest. Gemeldet am 24.09.2026. */
    '<div class="row schmal"><button class="btn ghost" id="lPfad">'+t('btn.zurueck_pfad')+'</button></div>';
  $('lHome').addEventListener('click', showLevelHome);
  $('lMore').addEventListener('click', startLesson);
  $('lPfad').addEventListener('click', ()=>{ homeMode='words'; showHome(); });""")

# ------------------------------------------------- 2. nach der Geschichte
t("Geschichte: Weg zurueck zu den Geschichten",
  """      '<div class="row"><button class="btn ghost" id="rAgain">'+t('gesch.fragen_nochmal')+'</button>'+(all && hasNext ? '<button class="btn know" id="rGoNext">'+t('gesch.naechste')+'</button>' : '')+'</div>';
    $('rAgain').addEventListener('click',()=>showStoryQ(s,0,0));
    const n=$('rGoNext'); if(n) n.addEventListener('click',()=>openStory(rIdx+1));""",
  """      '<div class="row"><button class="btn ghost" id="rAgain">'+t('gesch.fragen_nochmal')+'</button>'+(all && hasNext ? '<button class="btn know" id="rGoNext">'+t('gesch.naechste')+'</button>' : '')+'</div>'+
      /* Wie beim Vokabeltest: eine leise Reihe mit dem Weg heraus. Hier
         gab es bisher gar keinen - nur "nochmal" und "naechste". */
      '<div class="row schmal"><button class="btn ghost" id="rHome">'+t('btn.zurueck_geschichten')+'</button></div>';
    $('rAgain').addEventListener('click',()=>showStoryQ(s,0,0));
    $('rHome').addEventListener('click',()=>{ homeMode='stories'; showHome(); });
    const n=$('rGoNext'); if(n) n.addEventListener('click',()=>openStory(rIdx+1));""")

# ---------------------------------------------------------------- anwenden
text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

# Die Bausteine muessen da sein
for baustein, wo in (("  .row.schmal{margin-top:14px}", "die schmale Knopfreihe im Stil"),
                     ("let homeMode = 'words';", "homeMode"),
                     ("function showHome(", "showHome()")):
    if baustein not in text:
        print("ABBRUCH: %s fehlt" % wo)
        sys.exit(1)
print("   Bausteine vorhanden: .row.schmal, homeMode, showHome()")

# Und die Texte muessen in allen acht Sprachen stehen
import subprocess
pruef = subprocess.run(
    [r"C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe", "-c",
     "import sprachen;"
     "fehlt=[s['code'] for s in sprachen.SPRACHEN"
     " if not sprachen.texte(s['code']).get('btn.zurueck_pfad')"
     " or not sprachen.texte(s['code']).get('btn.zurueck_geschichten')];"
     "print(','.join(fehlt))"],
    cwd=r"C:\Users\Ajdin\Desktop\App Zeugs\Bosnisch Lernapp",
    capture_output=True, text=True)
fehlende = (pruef.stdout or "").strip()
if fehlende:
    print("ABBRUCH: die Knopftexte fehlen in: %s" % fehlende)
    sys.exit(1)
print("   Beide Knopftexte stehen in allen acht Sprachen.")
print()

for name, alt, neu in A:
    n = text.count(alt)
    if n != 1:
        print("ABBRUCH: %-42s %d Treffer" % (name, n))
        sys.exit(1)
    text = text.replace(alt, neu, 1)
    print("  ok   %s" % name)

# ------------------------------------------------------------ Nachkontrolle
fehler = []
for muss in ('id="lPfad">\'+t(\'btn.zurueck_pfad\')',
             'id="rHome">\'+t(\'btn.zurueck_geschichten\')',
             "$('lPfad').addEventListener('click', ()=>{ homeMode='words'; showHome(); });",
             "$('rHome').addEventListener('click',()=>{ homeMode='stories'; showHome(); });"):
    if muss not in text:
        fehler.append("%r fehlt" % muss)
# Jede Kennung nur einmal - doppelte ids brechen $()
for kennung in ('id="lPfad"', 'id="rHome"'):
    if text.count(kennung) != 1:
        fehler.append("%s steht %d mal da" % (kennung, text.count(kennung)))
# Die vorhandenen Knoepfe bleiben
for lebt in ("$('lHome').addEventListener('click', showLevelHome);",
             "$('lMore').addEventListener('click', startLesson);",
             "$('rAgain').addEventListener('click',()=>showStoryQ(s,0,0));"):
    if lebt not in text:
        fehler.append("%r ist verlorengegangen" % lebt)
if text.count("{") != text.count("}"):
    fehler.append("geschweifte Klammern aus dem Gleichgewicht (%d zu %d)"
                  % (text.count("{"), text.count("}")))

if fehler:
    print("\nABBRUCH - nichts geschrieben:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")
print()
print("   Was sich aendert:")
print("     nach dem Vokabeltest   zusaetzlich '← Lernpfad'")
print("     nach der Geschichte    zusaetzlich '← Geschichten'")
print("     Beide in einer eigenen, leiseren Reihe darunter.")
print("     Keine neuen Texte - beide Beschriftungen gab es schon.")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\nGeschrieben.")
    print("Danach: app_bauen.py - aber NICHT vor dem 07.10.2026 einreichen.")
else:
    print("\n(Probelauf.)")
