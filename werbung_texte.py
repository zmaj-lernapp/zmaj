# -*- coding: utf-8 -*-
"""Befund 18 aus WERBUNG_PRUEFUNG.md - reine Textarbeit.

BEFUND 18: Die Datenschutzerklaerung zaehlt vier Dinge auf, die Google
beim Ausspielen einer Anzeige bekommt. Im Data-Safety-Formular bei Google
sind aber vier KATEGORIEN angekreuzt, darunter "App-Informationen und
-Leistung / Diagnosedaten". Die stehen in der Erklaerung nicht, und die
Zwecke (Werbung, Reichweitenmessung, Betrugspraevention) auch nicht.
Dazu der Satz "Die App bindet keine Analyse-Dienste ein" - der stimmt so
nicht mehr, sobald ein Werbebaustein mitmisst. Eine Datenschutzerklaerung,
die weniger angibt als das Formular daneben, ist ein Verstoss gegen die
Play-Richtlinien und rechtlich angreifbar.

Geaendert wird in allen acht Sprachen:
  1. Am Ende des Werbe-Absatzes kommen die Messwerte und die Zwecke dazu.
  2. Der Satz "keine Analyse-Dienste" bekommt die Ausnahme.

BEFUND 20 ist bereits erledigt: admob_scharf.py tauscht den Kommentar
ueber der Kennung inzwischen mit, er wuerde sonst weiter behaupten, dort
stehe eine Testkennung.

Diese Datei aendert NICHTS an der Funktion der App, nur Texte. Sie kann
deshalb unabhaengig von werbung_richten.py laufen - aber ebenfalls erst
nach dem geschlossenen Test, weil jede Einreichung die Pruefuhr
zuruecksetzt.

Probelauf:  python werbung_texte.py
Schreiben:  python werbung_texte.py --schreiben
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SCHREIBEN = "--schreiben" in sys.argv

ORDNER = os.path.dirname(os.path.abspath(__file__))
SPR = os.path.join(ORDNER, "sprachen.py")

A = []


def t(datei, name, alt, neu):
    A.append((datei, name, alt, neu))


# =====================================================================
#  Acht Sprachen, je zwei Stellen
# =====================================================================

# ---- Deutsch
t(SPR, "de: Messwerte und Zwecke",
  """welche Anzeige du gesehen oder angetippt hast.""",
  """welche Anzeige du gesehen oder angetippt hast. Dazu kommen technische Messwerte des Werbebausteins selbst, etwa Startzeit, Hänger und Energieverbrauch. Google verwendet all das, um Anzeigen auszuspielen, ihre Reichweite zu messen und Betrug zu erkennen.""")
t(SPR, "de: Ausnahme beim Analyse-Satz",
  """Die App bindet keine Analyse-Dienste ein und""",
  """Außer Googles Werbebaustein bindet die App keine Analyse-Dienste ein und""")

# ---- Englisch
t(SPR, "en: Messwerte und Zwecke",
  """and which ad you saw or tapped.""",
  """and which ad you saw or tapped. On top of that come technical measurements from the ad component itself, such as start-up time, freezes and battery use. Google uses all of this to serve ads, measure their reach and detect fraud.""")
t(SPR, "en: Ausnahme beim Analyse-Satz",
  """The app includes no analytics and""",
  """Apart from Google's ad component, the app includes no analytics and""")

# ---- Tuerkisch
t(SPR, "tr: Messwerte und Zwecke",
  """hangisine dokunduğun bilgisini alır.""",
  """hangisine dokunduğun bilgisini alır. Buna ek olarak reklam bileşeninin kendi teknik ölçümleri gelir: açılış süresi, takılmalar ve enerji tüketimi. Google bunların tamamını reklam göstermek, erişimi ölçmek ve dolandırıcılığı tespit etmek için kullanır.""")
t(SPR, "tr: Ausnahme beim Analyse-Satz",
  """Uygulamada analiz hizmeti yoktur ve""",
  """Google'ın reklam bileşeni dışında uygulamada analiz hizmeti yoktur ve""")

# ---- Schwedisch
t(SPR, "sv: Messwerte und Zwecke",
  """information om vilken annons du har sett eller tryckt på.""",
  """information om vilken annons du har sett eller tryckt på. Till detta kommer tekniska mätvärden från annonsdelen själv, som starttid, hackningar och energiförbrukning. Google använder allt detta för att visa annonser, mäta deras räckvidd och upptäcka bedrägerier.""")
t(SPR, "sv: Ausnahme beim Analyse-Satz",
  """Appen använder inga analystjänster och""",
  """Utöver Googles annonsdel använder appen inga analystjänster och""")

# ---- Niederlaendisch
t(SPR, "nl: Messwerte und Zwecke",
  """de informatie over welke advertentie je hebt gezien of aangetikt.""",
  """de informatie over welke advertentie je hebt gezien of aangetikt. Daar komen technische meetwaarden van het advertentieonderdeel zelf bij, zoals opstarttijd, haperingen en energieverbruik. Google gebruikt dit alles om advertenties te tonen, hun bereik te meten en fraude op te sporen.""")
t(SPR, "nl: Ausnahme beim Analyse-Satz",
  """De app gebruikt geen analysediensten en""",
  """Behalve het advertentieonderdeel van Google gebruikt de app geen analysediensten en""")

# ---- Norwegisch
t(SPR, "nb: Messwerte und Zwecke",
  """informasjon om hvilken annonse du har sett eller trykket på.""",
  """informasjon om hvilken annonse du har sett eller trykket på. I tillegg kommer tekniske måleverdier fra annonsedelen selv, som oppstartstid, hakking og strømforbruk. Google bruker alt dette til å vise annonser, måle rekkevidden deres og oppdage svindel.""")
t(SPR, "nb: Ausnahme beim Analyse-Satz",
  """Appen bruker ingen analysetjenester og""",
  """Bortsett fra Googles annonsedel bruker appen ingen analysetjenester og""")

# ---- Daenisch
t(SPR, "da: Messwerte und Zwecke",
  """oplysning om, hvilken annonce du har set eller trykket på.""",
  """oplysning om, hvilken annonce du har set eller trykket på. Dertil kommer tekniske måleværdier fra annoncedelen selv, som starttid, hak og strømforbrug. Google bruger alt dette til at vise annoncer, måle deres rækkevidde og opdage svindel.""")
t(SPR, "da: Ausnahme beim Analyse-Satz",
  """Appen bruger ingen analysetjenester og""",
  """Bortset fra Googles annoncedel bruger appen ingen analysetjenester og""")

# ---- Franzoesisch
t(SPR, "fr: Messwerte und Zwecke",
  """quelle annonce tu as vue ou sur laquelle tu as appuyé.""",
  """quelle annonce tu as vue ou sur laquelle tu as appuyé. S'y ajoutent des mesures techniques du module publicitaire lui-même : temps de démarrage, blocages et consommation d'énergie. Google utilise tout cela pour diffuser les annonces, mesurer leur portée et détecter la fraude.""")
t(SPR, "fr: Ausnahme beim Analyse-Satz",
  """analyse et ne charge aucune police ou script""",
  """analyse en dehors du module publicitaire de Google et ne charge aucune police ou script""")

# ---------------------------------------------------------------- anwenden
stand = {}
for datei, name, alt, neu in A:
    if datei not in stand:
        roh = io.open(datei, encoding="utf-8", newline="").read()
        stand[datei] = [roh.replace("\r\n", "\n"), "\r\n" in roh]
    n = stand[datei][0].count(alt)
    if n != 1:
        print("ABBRUCH: %-16s %-34s %d Treffer" % (os.path.basename(datei), name, n))
        if n == 0:
            print("         Ist die Aenderung vielleicht schon drin?")
        sys.exit(1)
    stand[datei][0] = stand[datei][0].replace(alt, neu, 1)
    print("ok   %-16s %s" % (os.path.basename(datei), name))

# ------------------------------------------------------------ Nachkontrolle
fehler = []
s = stand[SPR][0]

# In jeder der acht Sprachen muss der Zweck-Satz jetzt stehen. Gesucht wird
# nach einem Wort, das in der jeweiligen Sprache nur dort vorkommt.
for code, wort in (("de", "Energieverbrauch. Google verwendet all das"),
                   ("en", "battery use. Google uses all of this"),
                   ("tr", "enerji tüketimi. Google bunların tamamını"),
                   ("sv", "energiförbrukning. Google använder allt detta"),
                   ("nl", "energieverbruik. Google gebruikt dit alles"),
                   ("nb", "strømforbruk. Google bruker alt dette"),
                   ("da", "strømforbrug. Google bruger alt dette"),
                   ("fr", "consommation d'énergie. Google utilise tout cela")):
    if s.count(wort) != 1:
        fehler.append("%s: der Zweck-Satz steht %d mal da, erwartet 1" % (code, s.count(wort)))

# Und der alte, zu weit gefasste Satz darf nirgends mehr allein stehen
for code, alt_satz in (("de", "Sonst nichts:</b> Die App bindet keine Analyse-Dienste"),
                       ("en", "Nothing else:</b> The app includes no analytics"),
                       ("tr", "yok:</b> Uygulamada analiz hizmeti yoktur"),
                       ("sv", "Inget annat:</b> Appen använder inga analystjänster"),
                       ("nl", "Verder niets:</b> De app gebruikt geen analysediensten"),
                       ("nb", "Ellers ingenting:</b> Appen bruker ingen analysetjenester"),
                       ("da", "Ellers ingenting:</b> Appen bruger ingen analysetjenester"),
                       ("fr", "aucun service d'analyse et ne charge")):
    if alt_satz in s:
        fehler.append("%s: der alte Analyse-Satz steht noch unveraendert da" % code)

if fehler:
    print("\nABBRUCH - nichts geschrieben:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")

if SCHREIBEN:
    for datei, (text, crlf) in stand.items():
        io.open(datei, "w", encoding="utf-8", newline="").write(
            text.replace("\n", "\r\n") if crlf else text)
        print("geschrieben: %s" % os.path.basename(datei))
    print("\nJETZT NOCH: seite_bauen.py (die Webseite zieht dieselben Texte)")
    print("und app_bauen.py.")
else:
    print("(Probelauf. Zum Schreiben: python werbung_texte.py --schreiben)")
