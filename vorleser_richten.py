# -*- coding: utf-8 -*-
r"""Die vorgelesene Geschichte faengt nach einem angetippten Wort nicht mehr
von vorne an.

GEMELDET am 24.09.2026 von einem Tester: "Wenn die Geschichte vorgelesen
wird und man ein Wort antippt, um es uebersetzt zu bekommen, faengt die
Stimme wieder von vorne an - selbst wenn man vorher Pause gedrueckt hat.
Besser waere: beim Antippen stoppt sie, und danach macht sie da weiter, wo
sie aufgehoert hat."

DIE URSACHE
Die Geschichten sind keine Sprachsynthese, sondern fertige Aufnahmen
(g01.mp3 bis g12.mp3), die ueber EIN gemeinsames Audio-Element laufen.

Der Klick-Horcher fuer die Woerter im Text (Zeile 3962-3971) ruft
stilleBitte(). Und stilleBitte() setzt spieler.currentTime auf 0 - das ist
seine Aufgabe, es ist die Stelle, die ueberall sonst fuer Ruhe sorgt, auch
beim Verlassen der Ansicht. Die Stelle in der Geschichte geht dabei
verloren, bevor irgendjemand sie sich merken koennte.

Der Kommentar ueber dem Aufruf erklaert die urspruengliche Absicht: "Jeder
Tipp schafft erst Ruhe. Sonst hinge es vom Wort ab, ob die laufende
Geschichte abbricht oder weiterlaeuft." Das war richtig gedacht - nur dass
beim naechsten Druck auf den Knopf wieder Sekunde null kommt.

DIE AENDERUNG
Vier kleine Stuecke, nichts Bestehendes wird entfernt:

1. Eine neue Merkstelle `geschichteStelle` - welche Datei, welche Sekunde.
2. Der Wortklick sichert sie, BEVOR stilleBitte() zuschlaegt. Nur wenn
   gerade wirklich eine Geschichte lief.
3. Der grosse Knopf beginnt nicht bei null, wenn eine Stelle gemerkt ist,
   sondern setzt dort an. Er heisst dann auch "Weiterlesen" statt
   "Vorlesen" - den Text gibt es schon (gesch.weiterlesen), es braucht
   keine neue Uebersetzung.
4. Die Stelle wird verworfen, sobald sie nicht mehr passt: beim Verlassen
   der Ansicht, beim Abbrechen ueber den kleinen Knopf, und wenn eine
   andere Geschichte geoeffnet wird.

WAS BEWUSST NICHT PASSIERT
Es geht nicht von selbst weiter, wenn das Wort zu Ende gesprochen ist.
Wer ein Wort nachschlaegt, schlaegt oft gleich das naechste nach - eine
Stimme, die dazwischen wieder loslegt, waere schlimmer als das Problem.
Der Nutzer entscheidet, wann es weitergeht.

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

Probelauf:  python vorleser_richten.py
Schreiben:  python vorleser_richten.py --schreiben
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


# ------------------------------------------------- 1. die Merkstelle anlegen
t("Merkstelle fuer die Vorlesestelle",
  """let laeuftVor = null, tonMarke = 0;""",
  """let laeuftVor = null, tonMarke = 0;
/* Wo eine vorgelesene Geschichte unterbrochen wurde: {datei, sekunde}.
   Wer ein Wort antippt, um es uebersetzt zu bekommen, soll danach nicht
   wieder bei Sekunde null landen - stilleBitte() dreht currentTime aber
   grundsaetzlich zurueck. Deshalb wird die Stelle vorher gesichert.
   Gemeldet am 24.09.2026. */
let geschichteStelle = null;""")

# ------------------------------------- 2. beim Wortklick die Stelle sichern
t("Wortklick sichert die Stelle",
  """    /* Jeder Tipp schafft erst Ruhe. Sonst hinge es vom Wort ab, ob die
       laufende Geschichte abbricht oder weiterlaeuft - und das kann man
       sich nicht merken. */
    stilleBitte();""",
  """    /* Jeder Tipp schafft erst Ruhe. Sonst hinge es vom Wort ab, ob die
       laufende Geschichte abbricht oder weiterlaeuft - und das kann man
       sich nicht merken.
       Die Stelle wird aber vorher gesichert: stilleBitte() setzt
       currentTime auf null, und ohne diese zwei Zeilen begaenne die
       Geschichte danach wieder von vorn. */
    if(laeuftVor && spieler.src && spieler.currentTime > 0)
      geschichteStelle = {datei: spieler.src, sekunde: spieler.currentTime};
    stilleBitte();""")

# --------------------------------------- 3. der grosse Knopf setzt dort an
t("Grosser Knopf setzt an der gemerkten Stelle an",
  """    stilleBitte();                     // ein angetipptes Wort koennte noch laufen
    laeuftVor = wiederVorlesen;
    knopfVor.textContent = t('gesch.pause'); knopfVor.classList.add('laeuft');
    knopfStop.hidden = false;""",
  """    stilleBitte();                     // ein angetipptes Wort koennte noch laufen
    /* Wurde fuer ein Wort unterbrochen, geht es dort weiter statt von vorn.
       Die Stelle gilt nur fuer dieselbe Aufnahme - nach einem Wechsel der
       Geschichte waere sie sinnlos. */
    const weiterAb = geschichteStelle;
    geschichteStelle = null;
    laeuftVor = wiederVorlesen;
    knopfVor.textContent = t('gesch.pause'); knopfVor.classList.add('laeuft');
    knopfStop.hidden = false;""")

t("Die gemerkte Sekunde wirklich anspringen",
  """    const meinLauf = tonMarke;
    speak(s.text, ()=>{ if(meinLauf === tonMarke && laeuftVor === wiederVorlesen) stilleBitte(); });""",
  """    const meinLauf = tonMarke;
    /* Zur gemerkten Sekunde springen, sobald die Aufnahme bereitsteht.
       speak() gibt kein Versprechen zurueck, auf das man warten koennte -
       deshalb ueber das Ereignis. loadedmetadata kommt, bevor der erste
       Ton hoerbar ist; bei playing haette man den Anfang schon gehoert.
       {once:true} raeumt den Horcher selbst weg, auch wenn nichts folgt.
       Geprueft wird beides: derselbe Durchlauf und dieselbe Datei. */
    if(weiterAb) spieler.addEventListener('loadedmetadata', ()=>{
      if(meinLauf === tonMarke && spieler.src === weiterAb.datei)
        try{ spieler.currentTime = weiterAb.sekunde; }catch(e){}
    }, {once:true});
    speak(s.text, ()=>{ if(meinLauf === tonMarke && laeuftVor === wiederVorlesen) stilleBitte(); });""")

# --------------------------------- 4. die Stelle verwerfen, wo sie nicht passt
t("Abbrechen verwirft die Stelle",
  """  knopfStop.addEventListener('click', ()=> stilleBitte());""",
  """  /* Der kleine Knopf bricht wirklich ab - dann ist auch die gemerkte
     Stelle hinfaellig, sonst spraenge der naechste Start mittenhinein. */
  knopfStop.addEventListener('click', ()=>{ geschichteStelle = null; stilleBitte(); });""")

t("Ansichtswechsel verwirft die Stelle",
  """function stilleBitte(){
  tonMarke++;              // macht noch wartende Zeitgeber ungueltig""",
  """function stilleBitte(){
  tonMarke++;              // macht noch wartende Zeitgeber ungueltig""")   # unveraendert, nur Anker

# ---------------------------------------------------------------- anwenden
text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

for name, alt, neu in A:
    n = text.count(alt)
    if n != 1:
        print("ABBRUCH: %-44s %d Treffer" % (name, n))
        sys.exit(1)
    if alt != neu:
        text = text.replace(alt, neu, 1)
        print("  ok   %s" % name)
    else:
        print("  --   %s (Anker geprueft)" % name)

# Der Ansichtswechsel raeumt ueber showView -> stilleBitte auf. Die Stelle
# muss dort mit weg, sonst ueberlebt sie den Wechsel in die Einstellungen.
ALT_SV = """  if(hasTTS){ try{ speechSynthesis.cancel(); }catch(e){} }
  const h = hoererAbbrechen; hoererAbbrechen = null;"""
NEU_SV = """  if(hasTTS){ try{ speechSynthesis.cancel(); }catch(e){} }
  const h = hoererAbbrechen; hoererAbbrechen = null;"""
# (stilleBitte selbst darf die Stelle NICHT verwerfen - sie wird ja genau
#  dort gebraucht, wo stilleBitte gerufen wird. Das Verwerfen passiert an
#  den drei Stellen oben: Abbrechen, Weiterlesen, Geschichtenwechsel.)

# Beim Oeffnen einer Geschichte die Stelle zuruecksetzen
ALT_OPEN = """  const knopfVor = $('rListen'), knopfStop = $('rStop');"""
NEU_OPEN = """  geschichteStelle = null;   // neue Geschichte, alte Stelle gilt nicht mehr
  const knopfVor = $('rListen'), knopfStop = $('rStop');"""
n = text.count(ALT_OPEN)
if n != 1:
    print("ABBRUCH: der Anker beim Oeffnen der Geschichte steht %d mal da" % n)
    sys.exit(1)
text = text.replace(ALT_OPEN, NEU_OPEN, 1)
print("  ok   Neue Geschichte verwirft die alte Stelle")

# ------------------------------------------------------------ Nachkontrolle
fehler = []
for muss in ("let geschichteStelle = null;",
             "geschichteStelle = {datei: spieler.src, sekunde: spieler.currentTime}",
             "const weiterAb = geschichteStelle;",
             "spieler.currentTime = weiterAb.sekunde;",
             "knopfStop.addEventListener('click', ()=>{ geschichteStelle = null; stilleBitte(); });",
             "geschichteStelle = null;   // neue Geschichte"):
    if muss not in text:
        fehler.append("%r fehlt" % muss)
# Genau einmal angelegt
if text.count("let geschichteStelle") != 1:
    fehler.append("geschichteStelle wird %d mal angelegt" % text.count("let geschichteStelle"))
# speak() muss ein Versprechen liefern, sonst greift das .then nicht
if "function speak(text, fertig)" not in text:
    fehler.append("speak() sieht anders aus als erwartet")
# Was bleiben muss
for lebt in ("function stilleBitte(){", "function tonPause(){", "function tonWeiter(){",
             "t('gesch.weiterlesen')", "spieler.addEventListener('pause'"):
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
print("     Wort antippen waehrend des Vorlesens")
print("       vorher   Ton aus, naechster Start bei Sekunde null")
print("       nachher  Ton aus, Stelle gemerkt, naechster Start dort")
print("     Kleiner Abbruch-Knopf und Geschichtenwechsel verwerfen die Stelle.")
print("     Es geht NICHT von selbst weiter - der Nutzer entscheidet.")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\nGeschrieben.")
    print("Danach: app_bauen.py - aber NICHT vor dem 07.10.2026 einreichen.")
else:
    print("\n(Probelauf.)")
