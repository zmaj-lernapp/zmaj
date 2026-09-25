# -*- coding: utf-8 -*-
r"""Die Meldung nach dem Sichern nennt jetzt den Dateinamen.

GEFUNDEN BEIM PRUEFDURCHLAUF P12 am 25.09.2026. Ajdin hat gesichert,
die App-Daten geloescht und wieder eingelesen. Das hat funktioniert -
aber: "bis ich meine datei gefunden hab war es echt schwer".

WARUM DAS PASSIERT
Auf Android schreibt sicherungSpeichern() die Datei in den Zwischenspeicher
der App und uebergibt sie dann ans Teilen-Menue:

    await P.Filesystem.writeFile({path:name, ..., directory:'CACHE', ...});
    await P.Share.share({title:..., url:ort.uri});

Wo die Datei danach liegt, entscheidet der Nutzer im Teilen-Menue: Drive,
Mail, Dateien, was auch immer. Das ist richtig so und soll auch so bleiben,
denn eine Sicherung, die nur auf demselben Geraet liegt, ist beim
Handywechsel wertlos - und genau dafuer ist sie da.

Falsch ist nur die Meldung danach. Sie lautet "Sicherung gespeichert." und
verschweigt, WIE die Datei heisst. Wer sie spaeter sucht, weiss nicht wonach.
Der Name enthaelt das Datum und ist eindeutig:

    zmaj-sicherung-2026-09-25.json

NICHT geaendert wird die Ablage im Zwischenspeicher. Documents und External
landen bei Capacitor ebenfalls unter /Android/data/<paket>/ und werden beim
Loeschen der App-Daten genauso mitgenommen; gewonnen waere nichts.

Ebenfalls geprueft und in Ordnung: Bricht der Nutzer das Teilen-Menue ab,
meldet das Plugin call.reject("Share canceled"), der catch greift, und die
App behauptet NICHT faelschlich, gespeichert zu haben.

Keine neuen Texte noetig. Der Dateiname ist sprachneutral und wird an die
vorhandene Meldung angehaengt, die es in allen acht Sprachen schon gibt.

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
ZIEL = os.path.join(ORDNER, "web", "index.html")

ALT = """    note.textContent = t('set.sicherung_ok'); sound('ok');"""

NEU = """    /* Der Dateiname gehoert in die Meldung. Wo die Sicherung landet,
       entscheidet der Nutzer im Teilen-Menue - ohne den Namen weiss er
       hinterher nicht, wonach er in der Dateiverwaltung suchen soll.
       Aufgefallen am 25.09.2026 beim Pruefdurchlauf P12. Der Name ist
       sprachneutral, deshalb braucht es dafuer keine neuen Texte. */
    note.textContent = t('set.sicherung_ok') + ' ' + name; sound('ok');"""

text = io.open(ZIEL, encoding="utf-8", newline="").read()
crlf = "\r\n" in text
text = text.replace("\r\n", "\n")

n = text.count(ALT)
if n != 1:
    print("ABBRUCH: die Meldezeile steht %d mal da, erwartet genau einmal" % n)
    sys.exit(1)
text = text.replace(ALT, NEU, 1)
print("ok   Die Meldung nennt jetzt den Dateinamen")

# ------------------------------------------------------------ Nachkontrolle
fehler = []
for muss in ("t('set.sicherung_ok') + ' ' + name;",
             "function sicherungName(){ return 'zmaj-sicherung-'"):
    if muss not in text:
        fehler.append("%r fehlt" % muss)

# Die alte Fassung darf nicht mehr da sein
if "note.textContent = t('set.sicherung_ok'); sound('ok');" in text:
    fehler.append("die alte Meldezeile steht noch drin")

# Was unveraendert bleiben muss: Ablage und Teilen-Weg
for lebt in ("directory:'CACHE'",
             "P.Share.share({title:t('set.sicherung'), url:ort.uri})",
             "catch(e){ note.textContent = t('set.sicherung_fehler'); }"):
    if lebt not in text:
        fehler.append("%r ist verlorengegangen" % lebt)

# Die Variable name muss an der Stelle ueberhaupt bekannt sein
kopf = text.find("async function sicherungSpeichern(){")
stelle = text.find("t('set.sicherung_ok') + ' ' + name;")
if kopf < 0 or stelle < 0 or not (kopf < stelle):
    fehler.append("die Meldung steht nicht mehr innerhalb von sicherungSpeichern()")
elif "const text = sicherungInhalt(), name = sicherungName();" not in text[kopf:stelle]:
    fehler.append("name wird vor der Meldung nicht mehr gesetzt")

if text.count("{") != text.count("}"):
    fehler.append("geschweifte Klammern aus dem Gleichgewicht (%d zu %d)"
                  % (text.count("{"), text.count("}")))
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
print("     vorher    Sicherung gespeichert.")
print("     nachher   Sicherung gespeichert. zmaj-sicherung-2026-09-25.json")
print()
print("     Damit laesst sie sich in der Dateiverwaltung suchen.")
print("     Ablage und Teilen-Menue bleiben unveraendert.")

if SCHREIBEN:
    io.open(ZIEL, "w", encoding="utf-8", newline="").write(
        text.replace("\n", "\r\n") if crlf else text)
    print("\nGeschrieben.")
    print("Danach: app_bauen.py - aber NICHT vor dem 07.10.2026 einreichen.")
else:
    print("\n(Probelauf.)")
