# -*- coding: utf-8 -*-
r"""Befund 18 aus WERBUNG_PRUEFUNG.md - reine Textarbeit in sprachen.py.

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

BEFUND 18: Die Datenschutzerklaerung zaehlt auf, was Google beim Ausspielen
einer Anzeige bekommt. Im Data-Safety-Formular bei Google ist zusaetzlich
"App-Informationen und -Leistung / Diagnosedaten" angekreuzt, und die
Zwecke (Werbung, Reichweitenmessung, Betrugspraevention) stehen dort auch.
Dazu der Satz "Die App bindet keine Analyse-Dienste ein" - der stimmt so
nicht, solange ein Werbebaustein mitmisst. Eine Datenschutzerklaerung, die
weniger angibt als das Formular daneben, ist ein Verstoss gegen die
Play-Richtlinien und rechtlich angreifbar.

STAND 04.10.2026 - die Haelfte ist schon von Hand drin.
Die Messwerte (Startzeit, Haenger, Energie- bzw. Akkuverbrauch) stehen in
allen acht Sprachen bereits im Werbe-Absatz von set.dsgvo_werbung_an, von
Hand und mit eigener Wortwahl ("Werbebaustein", "ad component",
"annonsmodulen" ...). Der alte Entwurf haette sie ein zweites Mal
angehaengt. Entfernt; offen sind je Sprache nur noch:
  1. der Satz mit den Zwecken, angehaengt an den vorhandenen Messwerte-Satz,
  2. die Ausnahme im Satz "keine Analyse-Dienste".
Die Ausnahme benutzt dasselbe Wort fuer den Werbebaustein wie der Satz von
Hand davor (sv annonsmodul, nb annonsemodul, da annoncemodul,
nl advertentiemodule) statt des alten Entwurfs (annonsdel, ...).

BEFUND 20 ist bereits erledigt: admob_scharf.py tauscht den Kommentar ueber
der Kennung mit.

Aendert nichts an der Funktion der App, nur Texte. Kann deshalb
unabhaengig von werbung_richten.py laufen. Danach seite_bauen.py (die
Webseite zieht dieselben Texte), inhalt_bauen.py und app_bauen.py.

Probelauf:  python werbung_texte.py
Schreiben:  python werbung_texte.py --schreiben
"""
import richten

SPRACHEN = richten.SPRACHEN

# Je Sprache: (Ende des Messwerte-Satzes von Hand, angehaengter Zweck-Satz,
#              alter Analyse-Satz, Analyse-Satz mit Ausnahme).
# Die Messwerte-Anker enden auf <br>: so findet ein zweiter Lauf sie nicht
# mehr und bricht ab, statt den Zweck-Satz doppelt anzuhaengen.
_TEXTE = [
    ("de",
     "Startzeit, Hänger und Energieverbrauch.<br>",
     " Google verwendet all das, um Anzeigen auszuspielen, ihre Reichweite zu messen und Betrug zu erkennen.",
     "Die App bindet keine Analyse-Dienste ein und",
     "Außer Googles Werbebaustein bindet die App keine Analyse-Dienste ein und"),
    ("en",
     "start-up time, freezes and battery use.<br>",
     " Google uses all of this to serve ads, measure their reach and detect fraud.",
     "The app includes no analytics and",
     "Apart from Google's ad component, the app includes no analytics and"),
    ("tr",
     "başlatma süresi, takılmalar ve pil tüketimi.<br>",
     " Google bunların tamamını reklam göstermek, erişimi ölçmek ve dolandırıcılığı tespit etmek için kullanır.",
     "Uygulamada analiz hizmeti yoktur ve",
     "Google'ın reklam bileşeni dışında uygulamada analiz hizmeti yoktur ve"),
    ("sv",
     "starttid, hängningar och batteriförbrukning.<br>",
     " Google använder allt detta för att visa annonser, mäta deras räckvidd och upptäcka bedrägerier.",
     "Appen använder inga analystjänster och",
     "Utöver Googles annonsmodul använder appen inga analystjänster och"),
    ("nl",
     "opstarttijd, haperingen en batterijverbruik.<br>",
     " Google gebruikt dit alles om advertenties te tonen, hun bereik te meten en fraude op te sporen.",
     "De app gebruikt geen analysediensten en",
     "Behalve de advertentiemodule van Google gebruikt de app geen analysediensten en"),
    ("nb",
     "oppstartstid, heng og batteriforbruk.<br>",
     " Google bruker alt dette til å vise annonser, måle rekkevidden deres og oppdage svindel.",
     "Appen bruker ingen analysetjenester og",
     "Bortsett fra Googles annonsemodul bruker appen ingen analysetjenester og"),
    ("da",
     "opstartstid, hængninger og batteriforbrug.<br>",
     " Google bruger alt dette til at vise annoncer, måle deres rækkevidde og opdage svindel.",
     "Appen bruger ingen analysetjenester og",
     "Bortset fra Googles annoncemodul bruger appen ingen analysetjenester og"),
    ("fr",
     "temps de démarrage, blocages et consommation de batterie.<br>",
     " Google utilise tout cela pour diffuser les annonces, mesurer leur portée et détecter la fraude.",
     "analyse et ne charge aucune police ou script",
     "analyse en dehors du module publicitaire de Google et ne charge aucune police ou script"),
]

AENDERUNGEN = []
for _code, _mess, _zweck, _alt, _neu in _TEXTE:
    AENDERUNGEN.append(("%s: Zwecke der Werbung" % _code,
                        _mess, _mess[:-len("<br>")] + _zweck + "<br>"))
    AENDERUNGEN.append(("%s: Ausnahme beim Analyse-Satz" % _code, _alt, _neu))


def anwenden(text):
    """(neuer Text, Fehlerliste). Ein Fehler heisst: nichts wird geschrieben."""
    neu, fehler = richten.ersetze_einmal(text, AENDERUNGEN)
    fehler += richten.gleichgewicht(text, neu)
    if not fehler:
        # sprachen.py ist Python: was hier herauskommt, muss sich laden lassen
        try:
            compile(neu, "sprachen.py", "exec")
        except SyntaxError as e:
            fehler.append("sprachen.py: Syntaxfehler danach (%s)" % e)
    return neu, fehler


def main(argv=None):
    return richten.main(argv, AENDERUNGEN, anwenden, "werbung_texte.py", ziel=SPRACHEN)


if __name__ == "__main__":
    raise SystemExit(main())
