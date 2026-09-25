# -*- coding: utf-8 -*-
r"""Behebt den eingefrorenen Vorspann bei ausgeschalteten Animationen.

GEMELDET am 23.09.2026 von einer Testerin: "Die Animation von SmartDragon
hat sich aufgehangen, trotz Neustart ging es nicht mehr." Ihr Foto zeigt
den Drachenkopf, den fertigen Schriftzug und einen gelben Klecks vor der
Schnauze. Die App laeuft normal weiter.

DIE URSACHE
Die App hat in den Einstellungen einen Schalter "Animationen". Steht er
aus, setzt applyAnim() (Zeile 1909) die Klasse no-anim auf den Koerper,
und Zeile 50 schaltet damit JEDE Animation ab:

    .no-anim *{transition:none!important; animation:none!important}

Der Stern trifft auch den Vorspann, an den dabei niemand gedacht hat.

Fuer die Systemeinstellung "Bewegung reduzieren" gibt es seit jeher eine
Vorkehrung (Zeile 409-414): dort bekommen die Vorspann-Teile ihren
Endzustand, insbesondere #vsGlut,#vsFeuer{opacity:0}. Fuer den App-Schalter
fehlt genau das. Die Folgen:

  #vsFeuer  hat statisch opacity:0        -> richtig unsichtbar
  #vsGlut   hat KEINE statische opacity   -> die Ellipse aus dem Markup
            (fill="#F5C400" opacity=".85") bleibt stehen. Das ist der
            gelbe Klecks auf dem Foto.
  #vsText   bleibt in seiner Grundfarbe   -> sieht zufaellig richtig aus

Zusaetzlich toetet Zeile 50 die Notaus-Animation vorspannNotaus. Sie ist
der einzige Weg, der den Vorspann auch dann wegnimmt, wenn das Skript gar
nicht anlaeuft - fuer Nutzer mit abgeschalteten Animationen gab es diesen
Notausstieg nicht.

WAS HIER GEAENDERT WIRD
1. no-anim bekommt dieselben Endzustaende wie die Systemeinstellung.
2. Der Vorspann wird von der Pauschalregel ausgenommen, damit sein
   Notausstieg bestehen bleibt.
3. Ohne Bewegung wird die Standzeit von 3,9 auf 1,4 Sekunden verkuerzt.
   Ein stehendes Bild vier Sekunden anzusehen hat niemand verdient.

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

Probelauf:  python vorspann_richten.py
Schreiben:  python vorspann_richten.py --schreiben
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


# ------------------------------------------- 1. Vorspann aus der Pauschale
t("Vorspann von der Pauschalregel ausnehmen",
  '  .no-anim *{transition:none!important; animation:none!important}',
  '''  /* Der Stern trifft alles - auch den Vorspann. Dessen Notaus-Animation
     muss aber bleiben: sie ist der einzige Weg, das Logo wegzunehmen,
     wenn das Skript nicht anlaeuft. Deshalb :not(#vorspann). */
  .no-anim *:not(#vorspann){transition:none!important; animation:none!important}
  /* Wer die Bewegung abschaltet, bekommt dasselbe Endbild wie bei der
     Systemeinstellung - sonst bleibt die Glut als gelber Fleck vor der
     Schnauze stehen. Gemeldet am 23.09.2026. */
  .no-anim #vsGlut, .no-anim #vsFeuer{opacity:0}
  .no-anim #vsText{fill:#FFFFFF}''')

# ------------------------------------------------ 2. kuerzere Standzeit
t("Ohne Bewegung kuerzer stehen",
  '''const VORSPANN_ABLAUF = 2400;   // so lange dauert die Bewegung oben im Stil
const VORSPANN_HALT   = 1500;   // so lange steht das fertige Bild danach still''',
  '''const VORSPANN_ABLAUF = 2400;   // so lange dauert die Bewegung oben im Stil
const VORSPANN_HALT   = 1500;   // so lange steht das fertige Bild danach still
/* Ohne Bewegung gibt es nichts abzuwarten: dann steht sofort das Endbild
   da, und 3,9 Sekunden davor zu sitzen ist nur Wartezeit. Geprueft wird
   beides - der Schalter in der App und die Einstellung des Geraets. */
function vorspannOhneBewegung(){
  if(document.body.classList.contains('no-anim')) return true;
  try{ return matchMedia('(prefers-reduced-motion: reduce)').matches; }
  catch(e){ return false; }
}''')

t("Die kuerzere Zeit auch verwenden",
  'let vorspannMin = VORSPANN_ABLAUF + VORSPANN_HALT;',
  '''let vorspannMin = vorspannOhneBewegung() ? 1400
                                         : VORSPANN_ABLAUF + VORSPANN_HALT;''')

# ---------------------------------------------------------------- anwenden
text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

# Die Bausteine muessen da sein
for baustein, wo in (('<g id="vsGlut">', "der Glut-Knoten im SVG"),
                     ("function applyAnim(){", "applyAnim()"),
                     ("@media (prefers-reduced-motion:reduce){", "der Block fuer die Systemeinstellung"),
                     ('id="vorspann"', "der Vorspann selbst")):
    if baustein not in text:
        print("ABBRUCH: %s fehlt" % wo)
        sys.exit(1)
print("   Bausteine vorhanden.")
print()

for name, alt, neu in A:
    n = text.count(alt)
    if n != 1:
        print("ABBRUCH: %-42s %d Treffer" % (name, n))
        sys.exit(1)
    text = text.replace(alt, neu, 1)
    print("ok   %s" % name)

# ------------------------------------------------------------ Nachkontrolle
fehler = []
for muss in ('.no-anim *:not(#vorspann){',
             '.no-anim #vsGlut, .no-anim #vsFeuer{opacity:0}',
             'function vorspannOhneBewegung(){',
             'vorspannMin = vorspannOhneBewegung() ? 1400'):
    if muss not in text:
        fehler.append("%r fehlt" % muss)
# Die alte Pauschale darf nicht mehr da sein
if '.no-anim *{transition:none' in text:
    fehler.append("die alte Pauschalregel steht noch drin")
# Der Schalter selbst muss weiter wirken
if "document.body.classList.toggle('no-anim', !animOn)" not in text:
    fehler.append("applyAnim() wurde beschaedigt")
# Die Systemeinstellung bleibt unberuehrt
if "#vsGlut,#vsFeuer{opacity:0}" not in text:
    fehler.append("die Vorkehrung fuer die Systemeinstellung ist verlorengegangen")
# Der Notaus muss den Vorspann weiter treffen koennen
if "animation:vorspannNotaus" not in text:
    fehler.append("der Notausstieg des Vorspanns fehlt")

if fehler:
    print("\nABBRUCH - nichts geschrieben:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")
print()
print("   Was sich fuer wen aendert:")
print("     Animationen AN      unveraendert, 3,9 s mit voller Bewegung")
print("     Schalter AUS        Endbild ohne Glutfleck, 1,4 s")
print("     Geraet reduziert    Endbild wie bisher, jetzt ebenfalls 1,4 s")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\nGeschrieben.")
    print("Danach: app_bauen.py - aber NICHT vor dem 07.10.2026 einreichen.")
else:
    print("\n(Probelauf.)")
