# -*- coding: utf-8 -*-
r"""Die Sicherung wiederfinden: Dateiname in der Meldung, Suchhinweis am Knopf.

GEFUNDEN BEIM PRUEFDURCHLAUF P12 am 25.09.2026. Ajdin hat gesichert,
die App-Daten geloescht und wieder eingelesen. Das hat funktioniert -
aber: "bis ich meine datei gefunden hab war es echt schwer".

WARUM DAS PASSIERT
Auf Android schreibt sicherungSpeichern() die Datei in den Zwischenspeicher
der App und uebergibt sie dann ans Teilen-Menue:

    await P.Filesystem.writeFile({path:name, ..., directory:'CACHE', ...});
    await P.Share.share({title:..., url:ort.uri});

Wo die Datei danach liegt, entscheidet der Nutzer im Teilen-Menue: Drive,
Mail, Dateien, was auch immer. Das ist richtig so und bleibt auch so, denn
eine Sicherung, die nur auf demselben Geraet liegt, ist beim Handywechsel
wertlos - und genau dafuer ist sie da.

Falsch sind nur die zwei Stellen, an denen die App schweigt:

  1. Die Meldung nach dem Speichern nennt den Dateinamen nicht. Wer spaeter
     sucht, weiss nicht wonach. Der Name traegt das Datum und ist eindeutig:
     zmaj-sicherung-2026-09-25.json
  2. Am Einlesen-Knopf steht kein Hinweis, dass die Dateiauswahl von Android
     ein Suchfeld hat, das ueber ALLE Speicherorte sucht - Downloads, Drive,
     Dateien. Ein Wort eintippen genuegt, navigieren ist gar nicht noetig.

WAS BEWUSST NICHT GEAENDERT WIRD

Die Ablage im Zwischenspeicher. Documents und External landen bei Capacitor
ebenfalls unter /Android/data/<paket>/ und werden beim Loeschen der
App-Daten genauso mitgenommen; gewonnen waere nichts.

Der fehlende accept-Filter am Dateifeld. Siehe den Kommentar an Ort und
Stelle: Android reicht accept als Typenliste an die Dateiauswahl weiter,
und eine Sicherung, die per Kabel, Mail oder Cloud aufs Handy gekommen ist,
traegt dort oft gar keinen Typ. Sie stuende dann ausgegraut da - ausgerechnet
in dem Moment, in dem jemand seinen Lernstand zurueckholen will. Ob es
wirklich eine Zmaj-Sicherung ist, prueft sicherungEinlesen ohnehin selbst
und sagt es mit set.sicherung_keine.

GEPRUEFT UND IN ORDNUNG
Bricht der Nutzer das Teilen-Menue ab, meldet das Plugin
call.reject("Share canceled"), der catch greift, und die App behauptet
NICHT faelschlich, gespeichert zu haben.

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

Probelauf:  python sicherung_richten.py
Schreiben:  python sicherung_richten.py --schreiben
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SCHREIBEN = "--schreiben" in sys.argv
ORDNER = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ORDNER, "web", "index.html")
SPR = os.path.join(ORDNER, "sprachen.py")

A = []


def t(datei, name, alt, neu):
    A.append((datei, name, alt, neu))


# =====================================================================
#  1. Der Dateiname gehoert in die Meldung
# =====================================================================
t(WEB, "Dateiname in der Meldung",
  """    note.textContent = t('set.sicherung_ok'); sound('ok');""",
  """    /* Der Dateiname gehoert in die Meldung. Wo die Sicherung landet,
       entscheidet der Nutzer im Teilen-Menue - ohne den Namen weiss er
       hinterher nicht, wonach er in der Dateiverwaltung suchen soll.
       Aufgefallen am 25.09.2026 beim Pruefdurchlauf P12. Der Name ist
       sprachneutral, deshalb braucht es dafuer keinen neuen Text. */
    note.textContent = t('set.sicherung_ok') + ' ' + name; sound('ok');""")

# =====================================================================
#  2. Ein Suchhinweis unter den beiden Knoepfen
# =====================================================================
t(WEB, "Suchhinweis am Einlesen-Knopf",
  """      <!-- Kein accept-Filter. Android reicht ihn als Typenliste an die""",
  """      <!-- Die Dateiauswahl von Android hat ein Suchfeld, das ueber alle
           Speicherorte geht. Wer den Namen kennt, muss nicht navigieren.
           Deshalb steht er hier, und deshalb nennt die Meldung nach dem
           Speichern ihn ebenfalls. -->
      <div class="sd" id="sichSuchen" style="font-size:12px; color:var(--muted); margin-bottom:8px" data-t="set.sicherung_suchen"></div>
      <!-- Kein accept-Filter. Android reicht ihn als Typenliste an die""")

# =====================================================================
#  3. Der Hinweistext in acht Sprachen
#
#  Anker ist jeweils set.sicherung_keine, die letzte Zeile des
#  Sicherungsblocks. Die ersten vier Sprachbloecke stehen buendig, die
#  letzten vier sind um vier Leerzeichen eingerueckt - deshalb steht die
#  Einrueckung hier in jedem Anker mit drin.
# =====================================================================
HINWEIS = [
    ("de", '"set.sicherung_keine": "Das ist keine Zmaj-Sicherung.",',
     '"set.sicherung_suchen": "Zum Einlesen im Auswahlfenster nach „zmaj“ suchen – damit findest du die Datei, ohne sie zu suchen.",'),
    ("en", '"set.sicherung_keine": "That is not a Zmaj backup.",',
     '"set.sicherung_suchen": "To load one, search for “zmaj” in the file picker – no need to browse for it.",'),
    ("tr", '"set.sicherung_keine": "Bu bir Zmaj yedeği değil.",',
     '"set.sicherung_suchen": "Yüklemek için dosya seçme ekranında “zmaj” diye ara – klasörlerde gezmene gerek kalmaz.",'),
    ("sv", '"set.sicherung_keine": "Det här är ingen Zmaj-kopia.",',
     '"set.sicherung_suchen": "Sök efter ”zmaj” i filväljaren när du ska läsa in – då slipper du leta.",'),
    ("nl", '    "set.sicherung_keine": "Dit is geen Zmaj-kopie.",',
     '    "set.sicherung_suchen": "Zoek bij het inlezen in het bestandsvenster naar ‘zmaj’ – dan hoef je niet te bladeren.",'),
    ("nb", '    "set.sicherung_keine": "Dette er ingen Zmaj-kopi.",',
     '    "set.sicherung_suchen": "Søk etter «zmaj» i filvelgeren når du skal lese inn – da slipper du å lete.",'),
    ("da", '    "set.sicherung_keine": "Det er ikke en Zmaj-kopi.",',
     '    "set.sicherung_suchen": "Søg efter »zmaj« i filvælgeren, når du vil indlæse – så slipper du for at lede.",'),
    ("fr", '    "set.sicherung_keine": "Ce n\'est pas une sauvegarde Zmaj.",',
     '    "set.sicherung_suchen": "Pour la restauration, cherchez « zmaj » dans le sélecteur de fichiers – inutile de parcourir les dossiers.",'),
]
for code, anker, neu in HINWEIS:
    t(SPR, "%s: Suchhinweis" % code, anker, anker + "\n" + neu)

# =====================================================================
#  Anwenden
# =====================================================================
dateien = {}
for datei in (WEB, SPR):
    roh = io.open(datei, encoding="utf-8", newline="").read()
    dateien[datei] = {"text": roh.replace("\r\n", "\n"), "crlf": "\r\n" in roh}

for datei, name, alt, neu in A:
    d = dateien[datei]
    n = d["text"].count(alt)
    if n != 1:
        print("ABBRUCH: %-16s %-28s %d Treffer" % (os.path.basename(datei), name, n))
        sys.exit(1)
    d["text"] = d["text"].replace(alt, neu, 1)
    print("ok   %-16s %s" % (os.path.basename(datei), name))

# ------------------------------------------------------------ Nachkontrolle
fehler = []
web, spr = dateien[WEB]["text"], dateien[SPR]["text"]

for muss in ("t('set.sicherung_ok') + ' ' + name;",
             'data-t="set.sicherung_suchen"',
             "function sicherungName(){ return 'zmaj-sicherung-'"):
    if muss not in web:
        fehler.append("index.html: %r fehlt" % muss)

if "note.textContent = t('set.sicherung_ok'); sound('ok');" in web:
    fehler.append("index.html: die alte Meldezeile steht noch drin")

# Ablage, Teilen-Weg und der fehlende Filter bleiben, wie sie sind
for lebt in ("directory:'CACHE'",
             "P.Share.share({title:t('set.sicherung'), url:ort.uri})",
             "catch(e){ note.textContent = t('set.sicherung_fehler'); }",
             "Kein accept-Filter.",
             '<input type="file" id="sichDatei" hidden>'):
    if lebt not in web:
        fehler.append("index.html: %r ist verlorengegangen" % lebt)

# name muss an der Meldestelle bekannt sein
kopf = web.find("async function sicherungSpeichern(){")
stelle = web.find("t('set.sicherung_ok') + ' ' + name;")
if kopf < 0 or stelle < 0 or kopf > stelle:
    fehler.append("index.html: die Meldung steht nicht mehr in sicherungSpeichern()")
elif "const text = sicherungInhalt(), name = sicherungName();" not in web[kopf:stelle]:
    fehler.append("index.html: name wird vor der Meldung nicht mehr gesetzt")

# Acht Sprachen, acht Texte
z = spr.count('"set.sicherung_suchen"')
if z != 8:
    fehler.append("sprachen.py: set.sicherung_suchen steht %d mal da, erwartet acht" % z)
if spr.count('"set.sicherung_keine"') != 8:
    fehler.append("sprachen.py: ein Anker ist verlorengegangen")

if web.count("{") != web.count("}"):
    fehler.append("index.html: geschweifte Klammern aus dem Gleichgewicht (%d zu %d)"
                  % (web.count("{"), web.count("}")))
if web.count("<!--") != web.count("-->"):
    fehler.append("index.html: ein HTML-Kommentar ist nicht geschlossen (%d zu %d)"
                  % (web.count("<!--"), web.count("-->")))
if web.count("/*") != web.count("*/"):
    fehler.append("index.html: ein Kommentar ist nicht geschlossen (%d zu %d)"
                  % (web.count("/*"), web.count("*/")))

# sprachen.py muss weiterhin gueltiges Python sein
try:
    compile(spr, "sprachen.py", "exec")
except SyntaxError as e:
    fehler.append("sprachen.py laesst sich nicht mehr uebersetzen: Zeile %s, %s"
                  % (e.lineno, e.msg))

if fehler:
    print("\nABBRUCH - nichts geschrieben:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")
print()
print("   Was sich aendert:")
print("     nach dem Sichern   Sicherung gespeichert. zmaj-sicherung-2026-09-25.json")
print("     unter den Knoepfen Zum Einlesen im Auswahlfenster nach „zmaj“ suchen")
print("     in acht Sprachen   de en tr sv nl nb da fr")
print()
print("     Ablage, Teilen-Menue und der fehlende accept-Filter bleiben unveraendert.")

if SCHREIBEN:
    for datei, d in dateien.items():
        io.open(datei, "w", encoding="utf-8", newline="").write(
            d["text"].replace("\n", "\r\n") if d["crlf"] else d["text"])
        print("\ngeschrieben: %s" % os.path.basename(datei))
    print("\nDanach: seite_bauen.py und app_bauen.py -")
    print("aber NICHT vor dem 07.10.2026 einreichen.")
else:
    print("\n(Probelauf.)")
