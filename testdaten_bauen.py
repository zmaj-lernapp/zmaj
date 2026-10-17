# -*- coding: utf-8 -*-
r"""
testdaten_bauen.py  –  Sicherungsdateien zum Durchtesten der ganzen App

Zum Ausprobieren braucht man einen Stand, in dem nichts mehr gesperrt ist:
alle Level offen, alle Wörter gelernt, alle Geschichten gelesen. Von Hand
zusammenzuklicken dauert Stunden.

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" testdaten_bauen.py

Die fertigen Dateien landen im Ordner `testdaten` und werden in der App
über **Einstellungen → Sicherung → Sicherung einlesen** geladen.

Es entstehen zwei, weil sich manches gegenseitig ausschließt:

  zmaj-test-vollversion.json   Alles geschafft: jedes Wort sitzt, der Drache
                               trägt Fes und Schal. Zum Anschauen: so sieht
                               die App ganz am Ende aus, und nichts ist
                               gesperrt. Die Vollversion selbst kommt nicht
                               mit (siehe unten).
  zmaj-test-alles-offen.json   Jedes Level und jede Geschichte offen, aber
                               NICHTS gelernt und nichts gekauft, und ohne
                               Vollversion. Zum Spielen: die Lektionen
                               zeigen wieder Vorstellkarten, Leben gehen
                               aus, Werbung läuft, im Laden gibt es etwas
                               zu kaufen.

Warum die zweite so: mit „jedes Wort sitzt" lässt sich ein ganzer Teil der
App nicht mehr anschauen. `buildLesson` baut die neuen Aufgaben aus den
Wörtern, die noch nicht sitzen – sind alle drin, kommt keine einzige
Vorstellkarte mehr. Und mit Vollversion ist der halbe Laden ausgegraut.

ACHTUNG: Einlesen ERSETZT den Stand auf dem Gerät, es vermischt nichts.
Wer einen echten Lernstand hat, sichert den vorher über denselben Weg.

ZWEITE ACHTUNG: Die Dateien altern. Die Lernserie wird aus dem heutigen
Datum gerechnet; liest man sie Tage später ein, verbraucht die App erst den
Serienschutz und meldet dann „Serie verloren". Deshalb am Testtag noch
einmal laufen lassen – das dauert Sekunden.

Bis auf die Lerntage ist die Ausgabe vollständig durch den Inhalt bestimmt:
zwei Läufe am selben Tag ergeben byte-gleiche Dateien. Wer sie an einem
anderen Tag genau nachbauen will, gibt den letzten Lerntag mit:

    python3 testdaten_bauen.py --bis 2026-10-03

DRITTE ACHTUNG: Die Dateien veralten auch mit dem Inhalt. Im Oktober 2026
standen noch 1108 Wörter und 43 Level drin, obwohl der Kurs längst 1728
und 65 hatte – das Skript war richtig, es war nur nicht neu gelaufen.
Seitdem prüft tests/test_testdaten.py, dass jede Kennung des Inhalts
drinsteht. Schlägt der Test an: dieses Skript laufen lassen.

VIERTE ACHTUNG (17.10.2026): Eine Sicherung bringt nur, was sich ehrlich
erreichen lässt. Seit sicherungPlausibel() in web/index.html nimmt die App
beim Einlesen höchstens 60 Münzen je Lerntag (plus einen Tag) und nur so
viel Zierrat, wie diese Münzen bezahlen. Bei 30 Lerntagen sind das 1860
Münzen - deshalb steht hier keine 999 999 mehr. Die Vollversion kommt über
eine Datei gar nicht, sie steht nicht im Lernstand. Wie man für den Laden
trotzdem viele Münzen bekommt, steht in testdaten/LIESMICH.txt.

Am PC schaltet auch `?alle=1` an der Adresse zum Ausprobieren alles frei.
(Bis zum 04.10.2026 stand hier, dass die Vollversion unter `start.py` nicht
wirkt: Der alte Kontoserver holte `premium` beim Speichern aus seiner
Profildatei zurück. Den Kontoserver gibt es nicht mehr; der Lernstand liegt
auch am PC im Browser.)
"""
import argparse
import datetime
import io
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, "testdaten")
sys.path.insert(0, HIER)

# So viele Lerntage bekommt die Testdatei mit. Ab 21 steht die
# Tagesaufgaben-Stufe auf 3 - erst dann tauchen alle Aufgabenarten und die
# hoechsten Ziele ueberhaupt auf.
LERNTAGE = 30

# Muenzen: genau so viele, wie die App beim Einlesen annimmt (17.10.2026).
# Bis dahin standen hier 999999 - die Grenze des alten Kontoservers. Seit
# sicherungPlausibel() in web/index.html nimmt eine Sicherung hoechstens 60
# Muenzen je Lerntag und einen Tag Vorschuss an (MUENZEN_JE_TAG_HOECHSTENS),
# aus 999999 wurden beim Einlesen still 1860, und testdaten/LIESMICH.txt
# versprach etwas, das nicht ankam. Gerechnet statt eingetragen, damit es mit
# LERNTAGE mitgeht; tests/test_testdaten.py vergleicht mit der App.
# Viele Muenzen fuer den Laden: siehe testdaten/LIESMICH.txt.
MUENZEN_JE_TAG = 60
MUENZEN = MUENZEN_JE_TAG * (LERNTAGE + 1)

# Was die Datei mit allem schon gekauft hat, mit den Preisen aus ZIERRAT in
# web/index.html. Seit dem 17.10.2026 nimmt die App beim Einlesen nur so viel
# Zierrat an, wie die Muenzen bezahlen - der ganze Laden kostet 23 800, die
# vier Stuecke von vorher (Brille, Kopfhoerer, Hut, Krone) 6000, es gehen also
# nur 1860. Fes und bosnischer Schal: ein Stueck fuer den Kopf, eins fuer den
# Hals, beide traegt der Drache. Gekauft heisst bezahlt - sie stehen auch in
# muenzen_aus. tests/test_testdaten.py prueft Preise und Summe.
GEKAUFT = {"fes": 900, "schal_bih": 800}


def lerntage(bis=None):
    """Die letzten Tage BIS GESTERN - heute absichtlich nicht.

    Dann zeigt die Startseite erst die laufende Serie mit „heute noch nicht
    geuebt", und nach der ersten Lektion springt sie sichtbar um. Traegt man
    heute mit ein, faellt dieser zweite Zustand ersatzlos weg.

    Gerechnet, nicht fest eingetragen: eine feste Spanne altert, und ein paar
    Tage spaeter frisst der Serienschutz sich auf und es steht rot
    „Serie verloren" da. Deshalb am Testtag neu laufen lassen.
    """
    # bis = letzter Lerntag. Ohne Angabe gestern, also heute minus i ab 1.
    heute = (bis + datetime.timedelta(days=1)) if bis else datetime.date.today()
    return [(heute - datetime.timedelta(days=i)).isoformat()
            for i in range(LERNTAGE, 0, -1)]


def inhalt():
    """Alle Wort-Kennungen, Level und Geschichten - genau wie die App sie sieht.

    Die Kennung baut inhalt.mit_kennung(), dieselbe Funktion, die auch
    inhalt.lade_daten() benutzt. Früher stand die Regel hier ein zweites Mal;
    weicht sie je ab, erkennt die App die Wörter nicht wieder.
    Gezählt wird nichts von Hand: was im Inhalt steht, kommt in die Datei.
    """
    import geschichten
    import inhalt
    import vokabeln

    daten = inhalt.mit_kennung({"kategorien": vokabeln.KATEGORIEN})
    woerter, level = [], []
    for k in daten["kategorien"]:
        level.append(k["id"])
        for w in k["words"]:
            if w["id"] not in woerter:
                woerter.append(w["id"])
    gelesen = [g["id"] for g in geschichten.GESCHICHTEN]
    return woerter, level, gelesen


def stand(premium, alles_gewusst=True, bis=None):
    woerter, level, gelesen = inhalt()

    return {
        # Alle Woerter als gekonnt einzutragen kostet etwas: buildLesson baut
        # die neuen Aufgaben aus den Woertern, die noch NICHT sitzen. Sind
        # alle drin, gibt es keine Vorstellkarten mehr - dieser Teil der
        # Lektion laesst sich dann gar nicht mehr anschauen. Deshalb die
        # zweite Datei ohne.
        "gewusst": woerter if alles_gewusst else [],
        # Freischalten tun allein diese beiden. `gewusst` braucht es dafuer
        # nicht: testAllowed fragt zuerst passed.has(...) und hoert da auf.
        "bestanden": level,
        "gelesen": gelesen,
        # Lerntage MÜSSEN sein. Ohne sie sagt die App an drei Stellen
        # „heute noch nicht geübt" und „noch keine Lernserie" – bei lauter
        # bestandenen Leveln. Und die Tagesaufgaben blieben auf Stufe 1,
        # damit wäre ein ganzer Zweig der App gar nicht anschaubar.
        "tage": lerntage(bis),
        "frost": [],
        # Schon etwas aus dem Laden gekauft, damit man den Drachen
        # angezogen sieht, ohne erst sparen zu müssen - so viel, wie die
        # Münzen bezahlen (siehe GEKAUFT). In der zweiten Datei nicht: dort
        # soll der Laden ja gerade ausprobiert werden.
        "besitz": list(GEKAUFT) if alles_gewusst else [],
        # Und gleich aufgesetzt – sonst steht der Drache nackt da, obwohl
        # alles gekauft ist.
        "getragen": ",".join(GEKAUFT) if alles_gewusst else "",
        "leben": {"anzahl": 5, "zeit": 0},
        "schutz": {"anzahl": 2, "zeit": 0},
        # Leer lassen: Münzen gibt es nur in dem Augenblick, in dem ein
        # Zähler sein Ziel überschreitet. Vorgefüllt gäbe es beim Testen nie
        # wieder eine Münze und nie die Jubelmeldung.
        "tagwerk": {},
        "muenzen_ges": MUENZEN,
        "muenzen_aus": sum(GEKAUFT.values()) if alles_gewusst else 0,
        # Wirkt beim Einlesen nicht: die Vollversion steht seit September
        # 2026 nicht mehr im Lernstand (vollversionLaden() in web/index.html).
        # Bleibt als Merker, welche Datei welche ist.
        "premium": premium,
    }


def schreibe(name, premium, hinweis, alles_gewusst=True, bis=None):
    d = {"app": "zmaj", "version": 1, "aus": hinweis,
         "stand": stand(premium, alles_gewusst, bis)}
    pfad = os.path.join(ZIEL, name)
    io.open(pfad, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))
    s = d["stand"]
    print("  %-30s %4d Wörter, %2d Level, %2d Geschichten, %2d Lerntage, "
          "%d Münzen, Merker premium %s"
          % (name, len(s["gewusst"]), len(s["bestanden"]), len(s["gelesen"]),
             len(s["tage"]), s["muenzen_ges"], "an " if premium else "aus"))
    return pfad


def main(argv=None):
    p = argparse.ArgumentParser(description="Sicherungen zum Durchtesten bauen.")
    p.add_argument("--bis", type=datetime.date.fromisoformat, default=None,
                   help="letzter Lerntag JJJJ-MM-TT (Vorgabe: gestern)")
    bis = p.parse_args(argv).bis
    os.makedirs(ZIEL, exist_ok=True)
    print("Testdaten bauen ...\n")
    schreibe("zmaj-test-vollversion.json", True, "Test mit Vollversion", bis=bis)
    schreibe("zmaj-test-alles-offen.json", False, "Test ohne Vollversion",
             alles_gewusst=False, bis=bis)
    print("\nLiegt in: %s" % ZIEL)
    print("In der App: Einstellungen > Sicherung > Sicherung einlesen.")
    print("Achtung: Das ersetzt den Stand auf dem Gerät. Eigenen vorher sichern.")


if __name__ == "__main__":
    main()
