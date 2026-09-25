# -*- coding: utf-8 -*-
r"""Bringt die zwei Dialoge des versteckten Schalters ins App-Design.

Der Schalter fuer die dauerhafte Vollversion benutzt bisher confirm() und
prompt(). Beides sind Systemabfragen der WebView: sie tragen oben den
Hostnamen, sehen nach Browser aus und halten den ganzen Bildschirm an.

Die App hat dafuer laengst ein eigenes Muster. In web/index.html steht ueber
frage() sogar der Grund, warum confirm() dort vermieden wird - die zwei
Stellen im Schalter sind die letzten Ausreisser.

  confirm(...)  ->  frage(titel, text, ja, nein)      gibt es schon
  prompt(...)   ->  frageWort(titel, text)            wird hier ergaenzt

frageWort() ist Zeile fuer Zeile nach frage() gebaut: dieselbe Huelle
.nachfrage, dieselbe Box .nachfragebox, dasselbe frageSchliessen fuer die
Zuruecktaste, daneben tippen heisst abbrechen.

Die Texte bleiben deutsch. Der Schalter ist fuer zwei Personen gedacht, und
ein halb uebersetzter Dialog waere schlechter als ein ganz deutscher.

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

Probelauf:  python dialog_richten.py
Schreiben:  python dialog_richten.py --schreiben
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


# ------------------------------------------------- 1. frageWort ergaenzen
# Direkt hinter frage(), damit beide beieinanderstehen.
t("frageWort() neben frage() stellen",
  """    // Daneben tippen heißt Nein – wie überall sonst auch
    kasten.addEventListener('click', e=>{ if(e.target === kasten) schliesse(false); });
  });
}
""",
  """    // Daneben tippen heißt Nein – wie überall sonst auch
    kasten.addEventListener('click', e=>{ if(e.target === kasten) schliesse(false); });
  });
}

/* Wie frage(), aber mit einem Eingabefeld. Liefert den Text oder null.
   Gebraucht wird das einmal: für den versteckten Schalter der dauerhaften
   Vollversion. prompt() täte es auch, sieht aber nach Browser aus. */
function frageWort(titel, text){
  if(frageSchliessen) return Promise.resolve(null);
  return new Promise(fertig => {
    const kasten = document.createElement('div');
    kasten.className = 'nachfrage';
    kasten.innerHTML =
      '<div class="nachfragebox">' +
        '<h3>' + esc(titel) + '</h3>' +
        (text ? '<div class="txt">' + esc(text) + '</div>' : '') +
        '<input class="field" id="frWort" type="text" autocomplete="off" ' +
               'autocapitalize="none" autocorrect="off" spellcheck="false">' +
        '<button class="btn know" id="frOk">Weiter</button>' +
        '<button class="btn ghost" id="frAb">Abbrechen</button>' +
      '</div>';
    document.body.appendChild(kasten);
    const feld = kasten.querySelector('#frWort');
    const schliesse = w => { kasten.remove(); frageSchliessen = null; fertig(w); };
    frageSchliessen = () => schliesse(null);
    kasten.querySelector('#frOk').addEventListener('click', ()=>schliesse(feld.value));
    kasten.querySelector('#frAb').addEventListener('click', ()=>schliesse(null));
    // Eingabetaste wie Weiter – sonst sucht man auf dem Handy den Knopf
    feld.addEventListener('keydown', e=>{ if(e.key === 'Enter') schliesse(feld.value); });
    kasten.addEventListener('click', e=>{ if(e.target === kasten) schliesse(null); });
    // Erst nach dem Einhängen, sonst öffnet sich die Tastatur nicht
    setTimeout(()=>feld.focus(), 50);
  });
}
""")

# --------------------------------------------- 2. Die zwei Stellen tauschen
t("Schalter auf die App-Dialoge umstellen",
  """  z.addEventListener('click', ()=>{
    clearTimeout(uhr); uhr = setTimeout(()=>{ n = 0; }, 2000);
    if(++n < 7) return;
    n = 0; clearTimeout(uhr);
    if(dauerVoll){
      if(confirm('Dauerhafte Vollversion ist an. Ausschalten?')){
        dauerVollSetzen(false); renderLives(); vollZeileZeigen();
      }
      return;
    }
    const wort = prompt('Wort?');
    if(wort === null) return;
    if(wort.trim().toLowerCase() !== DAUER_WORT) return;
    dauerVollSetzen(true); renderLives(); vollZeileZeigen();
  });""",
  """  z.addEventListener('click', async ()=>{
    clearTimeout(uhr); uhr = setTimeout(()=>{ n = 0; }, 2000);
    if(++n < 7) return;
    n = 0; clearTimeout(uhr);
    if(dauerVoll){
      if(await frage('Dauerhafte Vollversion',
                     'Sie ist eingeschaltet. Ausschalten?',
                     'Ausschalten', 'Anlassen')){
        dauerVollSetzen(false); renderLives(); vollZeileZeigen();
      }
      return;
    }
    const wort = await frageWort('Wort?');
    if(wort === null) return;
    if(wort.trim().toLowerCase() !== DAUER_WORT) return;
    dauerVollSetzen(true); renderLives(); vollZeileZeigen();
  });""")

# ---------------------------------------------------------------- anwenden
text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

# Die Bausteine muessen da sein, sonst baut man auf Sand
for baustein, wo in (("function frage(titel, text, ja, nein){", "frage()"),
                     ("function esc(", "esc()"),
                     ("let frageSchliessen = null;", "frageSchliessen"),
                     ('class="field"', "die Eingabefeld-Klasse"),
                     (".nachfragebox{", "die Dialogbox im CSS")):
    if baustein not in text:
        print("ABBRUCH: %s fehlt in der Datei" % wo)
        sys.exit(1)
print("   Alle Bausteine vorhanden: frage(), esc(), .field, .nachfragebox")
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
if "function frageWort(titel, text){" not in text:
    fehler.append("frageWort() wurde nicht eingefuegt")
if text.count("function frageWort") != 1:
    fehler.append("frageWort() steht %d mal da" % text.count("function frageWort"))
if "await frageWort('Wort?')" not in text:
    fehler.append("der Schalter ruft frageWort() nicht")
if "await frage('Dauerhafte Vollversion'" not in text:
    fehler.append("der Schalter ruft frage() nicht")
# Ohne async kein await
stelle = text.find("const wort = await frageWort")
if stelle > 0:
    rumpf = text.rfind("addEventListener('click'", 0, stelle)
    if "async" not in text[rumpf:rumpf + 60]:
        fehler.append("die Klickbehandlung ist nicht async - await wuerde scheitern")
# Im Schalter darf kein Systemdialog mehr stehen
schalter = text[text.find("function dauerVollVerdrahten"):]
schalter = schalter[:schalter.find("\n}\n") + 3]
for rest in ("confirm(", "prompt(", "alert("):
    if rest in schalter:
        fehler.append("im Schalter steht noch %s" % rest)
# Das Wort darf nicht verlorengehen
if "DAUER_WORT" not in text:
    fehler.append("DAUER_WORT ist verschwunden")

if fehler:
    print("\nABBRUCH - nichts geschrieben:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")
print()
print("   Die uebrigen Systemabfragen:")
for zeile_nr, zeile in enumerate(text.split("\n"), 1):
    if any(d in zeile for d in ("confirm(", "prompt(", "alert(")) and "//" not in zeile[:zeile.find("confirm(") if "confirm(" in zeile else 0]:
        kurz = zeile.strip()[:64]
        print("     Zeile %-5d %s" % (zeile_nr, kurz))

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\nGeschrieben.")
    print("Danach: app_bauen.py - aber NICHT vor dem 07.10.2026 einreichen.")
else:
    print("\n(Probelauf.)")
