# -*- coding: utf-8 -*-
r"""
sprechen_richten.py  –  vier Befunde an der Sprechaufgabe und der Sprachausgabe

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" sprechen_richten.py
    ... --schreiben

Alle vier am 26.09.2026 gefunden.

1. DIE ERKENNUNG LÄSST SICH NICHT ABBRECHEN
   Die Schleife über ['bs-BA','hr-HR','sr-RS', null] fängt jeden Fehler von
   H.start() in einem leeren catch ab und startet sofort die nächste Sprache.
   Der Kommentar nimmt an, dass nur „diese Stimme fehlt auf dem Gerät" einen
   Fehler wirft. Androids Erkenner meldet auf demselben Weg aber auch „kein
   Treffer", Zeitüberlauf, „Mikrofon belegt" und Abbruch.
   Folge: Wer schweigt, sitzt vier Runden vor einem roten Mikrofon. Ein
   zweiter Tipp ruft H.stop(), beendet damit nur die laufende Runde und
   startet die nächste – abbrechen geht gar nicht. Dasselbe beim
   Überspringen und beim Verlassen der Lektion: das Mikrofon läuft auf der
   Levelübersicht weiter, und solange der Erkenner den Tonkanal hält,
   bleiben die Aufnahmen der nächsten Aufgabe stumm.
   Neu: Ein Merker. Sobald der Nutzer stoppt, überspringt oder die Aufgabe
   vorbei ist, bricht die Schleife ab.

2. „ICH HABE „" VERSTANDEN"
   Liefert die Erkennung nichts, läuft bewerte([]) mit leerer Liste durch:
   erstes bleibt '', und auf dem Bildschirm steht der Satz mit einem leeren
   Wort darin, dazu der Fehlerton. Der Nutzer bekommt gesagt, er habe falsch
   gesprochen, obwohl das Mikrofon nichts gehört hat.
   Neu: Dann kommt task.mikro_fehler („Das hat nicht geklappt. Versuch es
   noch einmal.") – den Text gibt es bereits in allen acht Sprachen.

3. SPRECHAUFGABEN OHNE MIKROFONRECHT
   canSpeak kommt aus H.available(). Das sagt nur, ob ein Erkenner
   installiert ist, nicht ob die App ihn benutzen darf. Wer die Berechtigung
   ablehnt, bekommt trotzdem in jeder Lektion Sprechaufgaben, muss sie
   überspringen, und Lx.skipped ist dann nie 0 – die Tagesaufgabe „Eine
   Lektion ohne Fehler" ist für ihn dauerhaft unerreichbar.
   Neu: Wird die Berechtigung abgelehnt, fällt canSpeak auf false. Ab der
   nächsten Lektion kommen keine Sprechaufgaben mehr.

4. DEUTSCHE STIMME LIEST BOSNISCH VOR
   hoerbar() prüft mit hasTTS nur, OB es speechSynthesis gibt, nie ob eine
   bosnische, kroatische oder serbische Stimme da ist. 41 der 104
   Grammatikaufgaben haben für ihre richtige Antwort keine Aufnahme. Dann
   liest die Standardstimme des Geräts die bosnische Form vor – mit deutscher
   Aussprache, direkt nachdem der Nutzer sie gelernt hat.
   Neu: Eine eigene Prüfung nur für diese Stelle. hoerbar() selbst bleibt
   unangetastet, damit die Lautsprecher in den Wortlisten nicht verschwinden,
   falls die Stimmenliste beim ersten Aufruf noch leer ist.
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


# ------------------------------------------- 1. Abbruch wird endlich gehoert
t("Merker fuer den Abbruch anlegen",
  """    mic.addEventListener('click', async ()=>{
      if(fin) return;
      const H = hoererPlugin();
      if(H){
        // Weg über das Plugin: Androids eigene Erkennung.
        if(listening){ try{ await H.stop(); }catch(e){} return; }""",

  """    /* Sobald der Nutzer stoppt, ueberspringt oder die Aufgabe verlaesst,
       darf die Sprachschleife unten nicht die naechste Sprache anwerfen.
       Vorher lief das Mikrofon bis zu viermal weiter, auch auf der
       Levueluebersicht. Gefunden am 26.09.2026. */
    let stoppGewollt = false;
    mic.addEventListener('click', async ()=>{
      if(fin) return;
      const H = hoererPlugin();
      if(H){
        // Weg über das Plugin: Androids eigene Erkennung.
        if(listening){ stoppGewollt = true; try{ await H.stop(); }catch(e){} return; }""")

t("Schleife bricht ab, wenn der Nutzer nicht mehr will",
  """          listening = true; mic.classList.add('rec'); heard.textContent = t('task.hoert_zu');
          hoererAbbrechen = abhoeren;
          let erg = null;
          for(const sprache of ['bs-BA','hr-HR','sr-RS', null]){
            try{
              erg = await H.start(Object.assign({maxResults:5, partialResults:false, popup:false},
                                                sprache ? {language:sprache} : {}));
              break;
            }catch(e){ /* diese Stimme fehlt auf dem Geraet - naechste */ }
          }""",

  """          listening = true; stoppGewollt = false;
          mic.classList.add('rec'); heard.textContent = t('task.hoert_zu');
          hoererAbbrechen = ()=>{ stoppGewollt = true; abhoeren(); };
          let erg = null;
          for(const sprache of ['bs-BA','hr-HR','sr-RS', null]){
            try{
              erg = await H.start(Object.assign({maxResults:5, partialResults:false, popup:false},
                                                sprache ? {language:sprache} : {}));
              break;
            }catch(e){
              /* Frueher stand hier nur "diese Stimme fehlt auf dem Geraet".
                 Androids Erkenner wirft auf demselben Weg aber auch bei
                 "kein Treffer", Zeitueberlauf, belegtem Mikrofon und beim
                 Abbruch durch den Nutzer. Dann darf nicht die naechste
                 Sprache starten. */
              if(stoppGewollt || fin) break;
            }
          }""")

# --------------------------------------- 2. kein leeres Anfuehrungszeichen
t("Bei leerem Ergebnis den richtigen Satz zeigen",
  """      } else {
        heard.textContent = t('task.gehoert_no',{text:erstes}); sound('no');
      }""",

  """      } else if(!erstes){
        /* Die Erkennung hat nichts geliefert - geschwiegen, zu laut, Anruf,
           Mikrofon belegt. Vorher stand hier der Satz "Ich habe \u201a\u2018
           verstanden" mit einem leeren Wort darin, dazu der Fehlerton. Der
           Nutzer bekam gesagt, er habe falsch gesprochen. */
        heard.textContent = t('task.mikro_fehler');
      } else {
        heard.textContent = t('task.gehoert_no',{text:erstes}); sound('no');
      }""")

# ------------------------------------ 3. ohne Mikrofonrecht keine Sprechaufgaben
t("Abgelehnte Berechtigung merken",
  """          if(rechte.speechRecognition !== 'granted'){ heard.textContent = t('task.mikro_blockiert'); return; }""",

  """          if(rechte.speechRecognition !== 'granted'){
            /* canSpeak kam bisher allein aus H.available() - das sagt nur,
               dass ein Erkenner installiert ist, nicht dass die App ihn
               benutzen darf. Wer ablehnt, bekam trotzdem in jeder Lektion
               Sprechaufgaben, musste sie ueberspringen, und die Tagesaufgabe
               "ohne Fehler" verlangt Lx.skipped === 0 - sie war fuer ihn
               dauerhaft unerreichbar. Ab der naechsten Lektion faellt 'speak'
               jetzt aus dem Aufgabentopf. */
            canSpeak = false;
            heard.textContent = t('task.mikro_blockiert');
            return;
          }""")

# ------------------------------- 4. nur vorlesen, wenn es eine Stimme dafuer gibt
t("Eigene Pruefung fuers Vorlesen anlegen",
  """const hoerbar = text => !!audioDatei(text) || hasTTS;""",

  """const hoerbar = text => !!audioDatei(text) || hasTTS;
/* hoerbar() entscheidet, OB ein Lautsprecher angeboten wird, und darf grosszuegig
   sein: ist die Stimmenliste beim ersten Aufruf noch leer, soll der Knopf
   trotzdem dastehen. Beim Vorlesen einer Loesung ist das anders - dort wird
   sofort gesprochen. Ohne bosnische, kroatische oder serbische Stimme liest
   die Standardstimme des Geraets die bosnische Form mit deutscher Aussprache
   vor, direkt nachdem der Nutzer sie gelernt hat. Gefunden am 26.09.2026. */
const vorlesbar = text => !!audioDatei(text) || (hasTTS && !!pickVoice());""")

t("Die Grammatik-Loesung nur mit passender Stimme vorlesen",
  """if(hoerbar(g.richtig)) spaeterSprechen(g.richtig, 450);""",
  """if(vorlesbar(g.richtig)) spaeterSprechen(g.richtig, 450);""")


# ---------------------------------------------------------------- anwenden
text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

for baustein, wo in (("function pickVoice()", "pickVoice()"),
                     ("let canSpeak", "canSpeak"),
                     ("'task.mikro_fehler'", "der Text task.mikro_fehler"),
                     ("'task.mikro_blockiert'", "der Text task.mikro_blockiert")):
    if baustein not in text:
        print("ABBRUCH: %s fehlt in index.html" % wo)
        sys.exit(1)
print("   Bausteine vorhanden: pickVoice(), canSpeak, beide Mikrofon-Texte")

if "let stoppGewollt" in text or "const vorlesbar" in text:
    print("ABBRUCH: das Skript ist hier schon gelaufen")
    sys.exit(1)

print()
for was, alt, neu in ersetzungen:
    n = text.count(alt)
    if n != 1:
        print("ABBRUCH bei \u201e%s\u201c: %d Treffer statt 1" % (was, n))
        print("   gesucht: %s" % alt.strip().splitlines()[0][:80])
        sys.exit(1)
    text = text.replace(alt, neu)
    print("   ok   %s" % was)

# ------------------------------------------------------------ Nachkontrollen
fehler = []
# Fuenf Stellen: anlegen, beim Stop-Tipp setzen, beim Start zuruecksetzen,
# im Abbrecher setzen, in der Schleife abfragen.
if text.count("stoppGewollt") != 5:
    fehler.append("stoppGewollt kommt %d mal vor statt 5" % text.count("stoppGewollt"))
if "catch(e){ /* diese Stimme fehlt auf dem Geraet - naechste */ }" in text:
    fehler.append("das leere catch steht noch da")
if text.count("const vorlesbar") != 1:
    fehler.append("vorlesbar() steht nicht genau einmal da")
if text.count("vorlesbar(g.richtig)") != 1:
    fehler.append("die Grammatik-Stelle benutzt vorlesbar() nicht")
if "hoerbar(g.richtig)" in text:
    fehler.append("die Grammatik-Stelle haengt noch an hoerbar()")
if text.count("const hoerbar = text =>") != 1:
    fehler.append("hoerbar() wurde versehentlich veraendert")
if "canSpeak = false;\n            heard.textContent" not in text:
    fehler.append("canSpeak wird bei abgelehnter Berechtigung nicht zurueckgesetzt")
if text.count("t('task.mikro_fehler')") != 3:
    fehler.append("task.mikro_fehler kommt %d mal vor, erwartet 3"
                  % text.count("t('task.mikro_fehler')"))
if fehler:
    print("\nABBRUCH, Nachkontrolle:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")

print()
print("   Was sich aendert:")
print("     zweiter Tipp aufs Mikrofon   beendet die Erkennung wirklich")
print("     ueberspringen, Lektion weg   Mikrofon geht aus, statt weiterzulaufen")
print("     nichts gesagt                'Das hat nicht geklappt' statt")
print("                                  'Ich habe \u201a\u2018 verstanden' mit Fehlerton")
print("     Mikrofon abgelehnt           ab der naechsten Lektion keine")
print("                                  Sprechaufgaben mehr")
print("     keine bosnische Stimme       Grammatik-Loesung bleibt still, statt")
print("                                  deutsch ausgesprochen zu werden")
print()
print("     Keine neuen Texte. hoerbar() und die Lautsprecher bleiben unveraendert.")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\ngeschrieben: %s" % os.path.basename(ZIEL))
else:
    print("\n(Probelauf.)")
