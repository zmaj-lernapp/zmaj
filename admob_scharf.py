# -*- coding: utf-8 -*-
"""Schaltet die Werbung scharf: Testkennungen raus, echte Kennungen rein.

ERST NACH DEM GESCHLOSSENEN TEST LAUFEN LASSEN.
Solange Tester auf der App sind, muessen die Testkennungen drin bleiben.
Ein Tester, der aus Hilfsbereitschaft eine echte Anzeige anklickt, erzeugt
ungueltigen Traffic - und der kann das AdMob-Konto kosten, nicht nur die
paar Cent.

REIHENFOLGE (siehe auch docs/WARTUNG.md):
  1. App ist in der Produktion live
  2. In AdMob unter App-Einstellungen mit dem App-Shop verknuepft
     (de.smartdragon.zmaj) und die Pruefung ist durch
  3. app-ads.txt liegt oeffentlich auf zmaj-lernapp.github.io
  4. DANN erst dieses Skript

Danach app_bauen.py laufen lassen, sonst liegt in der Huelle weiter die
alte index.html.

Die Kennungen stammen aus dem AdMob-Konto, angelegt am 20.09.2026.
Sie sind keine Geheimnisse - sie stehen in jeder ausgelieferten App.

Probelauf:  python admob_scharf.py
Schreiben:  python admob_scharf.py --schreiben
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SCHREIBEN = "--schreiben" in sys.argv

ORDNER = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ORDNER, "web", "index.html")
XML = os.path.join(os.path.dirname(ORDNER), "zmaj-android", "android", "app",
                   "src", "main", "res", "values", "strings.xml")
# Die Anleitung fuehrt dieselben Kennungen in einer Tabelle. Ohne sie hier
# stuende dort nach dem Tausch weiter die Testkennung - beim naechsten
# Durchsehen sieht das aus wie eine offene Aufgabe.
ANL = os.path.join(ORDNER, "ANLEITUNG.md")

APP_ID = "ca-app-pub-9105747905460295~9760526209"
INTER = "ca-app-pub-9105747905460295/9764395638"
BELOHNT = "ca-app-pub-9105747905460295/8572576770"
TEST_PRAEFIX = "3940256099942544"

A = []


def t(datei, name, alt, neu):
    A.append((datei, name, alt, neu))


t(WEB, "Testschalter aus",
  """const ADMOB_TEST = true;""",
  """const ADMOB_TEST = false;""")

t(WEB, "Interstitial-Kennung",
  """  interstitial: 'ca-app-pub-3940256099942544/1033173712',   // Googles Testkennung""",
  """  interstitial: '%s',   // Zmaj, angelegt 20.09.2026""" % INTER)

t(WEB, "Kennung fuer das belohnte Video",
  """  belohnt:      'ca-app-pub-3940256099942544/5224354917',   // Googles Testkennung""",
  """  belohnt:      '%s',   // Zmaj, angelegt 20.09.2026""" % BELOHNT)

t(ANL, "Kennungstabelle in der Anleitung",
  """Zurzeit laufen **Googles öffentliche Testanzeigen**. Die brauchen kein
Konto, kosten nichts und bringen nichts ein. Testanzeigen in einer
veröffentlichten App sind ein Regelverstoß, also vor dem ersten Hochladen an
diesen drei Stellen die echten Werte aus dem AdMob-Konto eintragen:

| Was | Wo | Steht dort jetzt |
|---|---|---|
| App-ID | `zmaj-android/android/app/src/main/res/values/strings.xml`, `admob_app_id` | `ca-app-pub-3940256099942544~3347511713` |
| Anzeigen-IDs | `web/index.html`, `ADMOB_ID` (`interstitial`, `belohnt`) | Googles Testkennungen |
| Testbetrieb | `web/index.html`, `ADMOB_TEST` | `true` → auf `false` |""",
  """Die echten Kennungen aus dem AdMob-Konto sind eingetragen, gesetzt von
`admob_scharf.py`. Testanzeigen in einer veröffentlichten App wären ein
Regelverstoß; seitdem stehen an diesen drei Stellen die scharfen Werte:

| Was | Wo | Steht dort jetzt |
|---|---|---|
| App-ID | `zmaj-android/android/app/src/main/res/values/strings.xml`, `admob_app_id` | `%s` |
| Anzeigen-IDs | `web/index.html`, `ADMOB_ID` (`interstitial`, `belohnt`) | die echten Kennungen vom 20.09.2026 |
| Testbetrieb | `web/index.html`, `ADMOB_TEST` | `false` |""" % APP_ID)

t(XML, "App-Kennung in der Huelle",
  """    <!-- AdMob: Ohne diesen Eintrag stuerzt die App beim Start ab, sobald das
         Werbe-SDK dabei ist. Hier steht Googles oeffentliche TEST-Kennung.
         VOR DEM ERSTEN HOCHLADEN in den Play Store durch die echte Kennung
         aus dem AdMob-Konto ersetzen (Einstellungen -> App-ID, beginnt mit
         ca-app-pub- und hat eine Tilde). Die Anzeigen-Kennungen selbst
         stehen in web/index.html unter ADMOB_ID. -->
    <string name="admob_app_id">ca-app-pub-3940256099942544~3347511713</string>""",
  """    <!-- AdMob: Ohne diesen Eintrag stuerzt die App beim Start ab, sobald
         das Werbe-SDK dabei ist. Das hier ist die echte App-Kennung aus dem
         AdMob-Konto, eingetragen am 20.09.2026 von admob_scharf.py. Die
         Anzeigen-Kennungen selbst stehen in web/index.html unter ADMOB_ID.
         Nicht von Hand aendern - das Skript prueft beide Stellen zusammen. -->
    <string name="admob_app_id">%s</string>""" % APP_ID)

# ---------------------------------------------------------------- anwenden
if not os.path.exists(XML):
    print("ABBRUCH: strings.xml nicht gefunden unter\n   %s" % XML)
    sys.exit(1)

stand = {}
for datei, name, alt, neu in A:
    if datei not in stand:
        stand[datei] = io.open(datei, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    n = stand[datei].count(alt)
    if n != 1:
        print("ABBRUCH: %-14s %-34s %d Treffer" % (os.path.basename(datei), name, n))
        if n == 0:
            print("         Steht die Aenderung vielleicht schon drin?")
        sys.exit(1)
    stand[datei] = stand[datei].replace(alt, neu, 1)
    print("ok   %-14s %s" % (os.path.basename(datei), name))

# ------------------------------------------------------------ Nachkontrolle
fehler = []
for datei, text in stand.items():
    if TEST_PRAEFIX in text:
        fehler.append("in %s steht noch eine Testkennung" % os.path.basename(datei))

w = stand[WEB]
if "const ADMOB_TEST = false;" not in w:
    fehler.append("ADMOB_TEST steht nicht auf false")
if w.count(INTER) != 1:
    fehler.append("die Interstitial-Kennung steht %d mal da" % w.count(INTER))
if w.count(BELOHNT) != 1:
    fehler.append("die Belohnt-Kennung steht %d mal da" % w.count(BELOHNT))
if INTER == BELOHNT:
    fehler.append("beide Kennungen sind gleich - da ist beim Kopieren etwas schiefgegangen")

x = stand[XML]
if x.count(APP_ID) != 1:
    fehler.append("die App-Kennung steht %d mal in strings.xml" % x.count(APP_ID))
# Die App-Kennung hat eine Tilde, die Bloecke einen Schraegstrich. Wer das
# vertauscht, bekommt zur Laufzeit nur eine nichtssagende Fehlermeldung.
if "~" not in APP_ID:
    fehler.append("die App-Kennung hat keine Tilde")
for k in (INTER, BELOHNT):
    if "/" not in k:
        fehler.append("%s ist keine Anzeigenblock-Kennung (kein Schraegstrich)" % k)

if fehler:
    print("\nABBRUCH - nichts geschrieben:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")

if SCHREIBEN:
    for datei, text in stand.items():
        io.open(datei, "w", encoding="utf-8", newline="").write(text.replace("\n", "\r\n"))
        print("geschrieben: %s" % os.path.basename(datei))
    print("\nJETZT NOCH: app_bauen.py laufen lassen, sonst liegt in der Huelle")
    print("weiter die alte index.html mit den Testkennungen.")
else:
    print("(Probelauf. Zum Schreiben: python admob_scharf.py --schreiben)")
