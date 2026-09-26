# -*- coding: utf-8 -*-
r"""
gleiche_bedeutung_richten.py  –  macht Aufgaben lösbar, bei denen zwei
                                 Vokabeln dieselbe Übersetzung haben

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" gleiche_bedeutung_richten.py
    ... --schreiben

DAS PROBLEM (gefunden am 26.09.2026)

Zwei bosnische Wörter können in einer Oberflächensprache dieselbe
Übersetzung haben. Auf Dänisch heißen `majka` und `mama` beide „mor", auf
Französisch `kolač` und `torta` beide „gâteau". Beide Paare stehen jeweils
im SELBEN Level.

Dann geht zweierlei schief:

  Schreib-Aufgabe   Auf dem Bildschirm steht „mor". Gemeint ist genau eines
                    der beiden Wörter. matches() trennt nur bei „ / "
                    innerhalb EINES Eintrags - die andere, sachlich völlig
                    richtige Antwort gilt als falsch. Das kostet ein Herz.

  Auswahl-Aufgabe   distractors() wählt die Ablenker nach dem bosnischen
                    Wort aus (w.bs !== target.bs), nicht nach der
                    angezeigten Bedeutung. Stehen beide in derselben
                    Auswahl, ist die Frage nicht entscheidbar.

Auf Deutsch fällt das nie auf, weil dort „Mutter" und „Mama" verschieden
sind. doppelte_bedeutung.py findet über alle acht Sprachen elf solche
Stellen, zwei davon im selben Level.

DIE LÖSUNG

Nicht an den Übersetzungen drehen - das wären Eingriffe in acht Sprachen,
und für Dänisch fehlt hier die Kenntnis. Stattdessen lernt die App, gleiche
Bedeutungen zu erkennen:

  geschwister(w)   alle Wörter, die dieselbe angezeigte Bedeutung tragen

  Schreiben        die Geschwister werden an die erwartete Antwort gehängt.
                   matches() trennt ohnehin bei „ / " - „majka / mama" wird
                   damit zu einer Antwort, die beide Formen annimmt.

  Auswahl          distractors() wirft Wörter mit derselben Bedeutung aus
                   dem Topf. Die Frage bleibt eindeutig.

Das wirkt in allen acht Sprachen und auch für Paare, die erst später
dazukommen - es steht keine Liste im Programm, die gepflegt werden müsste.
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


# ------------------------------------------- 1. die Hilfsfunktion anlegen
t("geschwister() neben distractors stellen",
  """function distractors(target, words, n){
  let pool = words.filter(w=>w.bs!==target.bs);
  if(pool.length<n) pool = CATEGORIES.flatMap(c=>c.words).filter(w=>w.bs!==target.bs);
  const seen = new Set([target.bs]); const out=[];
  for(const w of shuffle(pool.slice())){ if(!seen.has(w.bs)){ seen.add(w.bs); out.push(w); if(out.length===n) break; } }
  return out;
}""",

  """/* Zwei Vokabeln koennen in einer Oberflaechensprache dieselbe Uebersetzung
   haben: auf Daenisch heissen majka und mama beide "mor", auf Franzoesisch
   kolac und torta beide "gateau". Auf Deutsch faellt das nie auf.
   Ohne diese Funktion waere die Auswahlaufgabe dort nicht entscheidbar und
   die Schreibaufgabe nicht loesbar - eine richtige Antwort kostet ein Herz.
   Gefunden am 26.09.2026, elf Stellen ueber acht Sprachen. */
const _bedeutung = s => String(s||'').toLowerCase().replace(/[.!?\\u2026]+$/,'').replace(/\\s+/g,' ').trim();
function geschwister(w){
  const b = _bedeutung(w.de);
  if(!b) return [];
  return CATEGORIES.flatMap(c=>c.words).filter(x => x.bs !== w.bs && _bedeutung(x.de) === b);
}
function distractors(target, words, n){
  /* Auch die Bedeutung vergleichen, nicht nur das bosnische Wort. Sonst
     landen "majka" und "mama" in derselben Auswahl, beide zeigen "mor". */
  const gleich = new Set(geschwister(target).map(x=>x.bs));
  const raus = w => w.bs===target.bs || gleich.has(w.bs);
  let pool = words.filter(w=>!raus(w));
  if(pool.length<n) pool = CATEGORIES.flatMap(c=>c.words).filter(w=>!raus(w));
  const seen = new Set([target.bs]); const out=[];
  for(const w of shuffle(pool.slice())){ if(!seen.has(w.bs)){ seen.add(w.bs); out.push(w); if(out.length===n) break; } }
  return out;
}""")

# ------------------------------------------- 2. die Schreibaufgabe
t("Schreibaufgabe nimmt auch das Geschwisterwort an",
  """      if(fin) return; const r=matches(inp.value, w.bs);
      if(r==='leer'){ $$('xFb').textContent=t('task.tippe_wort'); $$('xFb').className='feedback no'; return; }""",

  """      /* Traegt ein anderes Wort dieselbe Uebersetzung, ist es genauso
         richtig - der Bildschirm zeigt ja nur die Bedeutung. matches()
         trennt ohnehin bei " / ", deshalb genuegt es, die Geschwister
         anzuhaengen. */
      if(fin) return;
      const auchOk = [w.bs, ...geschwister(w).map(x=>x.bs)].join(' / ');
      const r=matches(inp.value, auchOk);
      if(r==='leer'){ $$('xFb').textContent=t('task.tippe_wort'); $$('xFb').className='feedback no'; return; }""")


# ---------------------------------------------------------------- anwenden
text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

for baustein, wo in (("CATEGORIES.flatMap", "CATEGORIES"),
                     ("function matches(guess, answer)", "matches()"),
                     ("const shuffle = a =>", "shuffle()")):
    if baustein not in text:
        print("ABBRUCH: %s fehlt in index.html" % wo)
        sys.exit(1)
print("   Bausteine vorhanden: CATEGORIES, matches(), shuffle()")

if "function geschwister" in text:
    print("ABBRUCH: geschwister() steht schon in index.html")
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
if text.count("function geschwister") != 1:
    fehler.append("geschwister() steht nicht genau einmal da")
# Drei Stellen: die Definition selbst, der Aufruf in distractors und der
# in der Schreibaufgabe.
if text.count("geschwister(") != 3:
    fehler.append("geschwister() kommt %d mal vor, erwartet 3" % text.count("geschwister("))
if "matches(inp.value, w.bs)" in text:
    fehler.append("die Schreibaufgabe vergleicht noch gegen w.bs allein")
# Die Satzaufgabe (Zeile 4564) bleibt absichtlich unveraendert: dort ist die
# Antwort ein Lueckenwort, kein Vokabeleintrag mit eigener Bedeutung.
if "matches(inp.value, s.answer)" not in text:
    fehler.append("die Satzaufgabe wurde versehentlich mitgeaendert")
if fehler:
    print("\nABBRUCH, Nachkontrolle:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")
print("   Die Lueckensatz-Aufgabe bleibt unveraendert - dort ist die Antwort")
print("   ein einzelnes Wort im Satz, keine Vokabel mit eigener Bedeutung.")

print()
print("   Was sich aendert:")
print("     Auswahlaufgabe   zwei Woerter mit derselben Uebersetzung stehen")
print("                      nicht mehr zusammen in einer Auswahl")
print("     Schreibaufgabe   beide Schreibweisen gelten als richtig")
print("     betroffen        11 Stellen ueber acht Sprachen, zwei davon im")
print("                      selben Level (da: mor, fr: gateau)")
print()
print("     Keine neuen Texte, keine Aenderung an den Uebersetzungen.")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\ngeschrieben: %s" % os.path.basename(ZIEL))
else:
    print("\n(Probelauf.)")
