# -*- coding: utf-8 -*-
r"""
testdaten_bauen.py  –  Sicherungsdateien zum Durchtesten der ganzen App

Zum Ausprobieren braucht man einen Stand, in dem nichts mehr gesperrt ist:
alle Level offen, alle Wörter gelernt, alle Geschichten gelesen, Münzen
genug. Von Hand zusammenzuklicken dauert Stunden.

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" testdaten_bauen.py

Die fertigen Dateien landen im Ordner `testdaten` und werden in der App
über **Einstellungen → Sicherung → Sicherung einlesen** geladen.

Es entstehen zwei, weil sich manches gegenseitig ausschließt:

  zmaj-test-vollversion.json   Alles geschafft. Vollversion an, keine
                               Werbung, unbegrenzte Leben, 999 999 Münzen,
                               jedes Wort sitzt, der Drache trägt die Krone.
                               Zum Anschauen: so sieht die App ganz am Ende
                               aus, und nichts ist gesperrt.
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

Und: die Vollversion wirkt nur in der Geräteversion. Läuft `start.py`, holt
der Server `premium` beim ersten Speichern aus der Profildatei zurück
(start.py:875) – dann ist sie wieder aus. Am PC stattdessen `?alle=1` an
die Adresse hängen, das schaltet zum Ausprobieren alles frei.
"""
import datetime
import io
import json
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, "testdaten")
sys.path.insert(0, HIER)

# Der Server kappt den Muenzstand still bei dieser Grenze (start.py:554).
# Ein groesserer Wert waere nach dem ersten Speichern lautlos wieder weg
# und der Test saehe aus, als haette etwas nicht funktioniert.
MUENZEN = 999999

# So viele Lerntage bekommt die Testdatei mit. Ab 21 steht die
# Tagesaufgaben-Stufe auf 3 - erst dann tauchen alle Aufgabenarten und die
# hoechsten Ziele ueberhaupt auf.
LERNTAGE = 30


def lerntage():
    """Die letzten Tage BIS GESTERN - heute absichtlich nicht.

    Dann zeigt die Startseite erst die laufende Serie mit „heute noch nicht
    geuebt", und nach der ersten Lektion springt sie sichtbar um. Traegt man
    heute mit ein, faellt dieser zweite Zustand ersatzlos weg.

    Gerechnet, nicht fest eingetragen: eine feste Spanne altert, und ein paar
    Tage spaeter frisst der Serienschutz sich auf und es steht rot
    „Serie verloren" da. Deshalb am Testtag neu laufen lassen.
    """
    heute = datetime.date.today()
    return [(heute - datetime.timedelta(days=i)).isoformat()
            for i in range(LERNTAGE, 0, -1)]


def stand(premium, alles_gewusst=True):
    import vokabeln
    import geschichten

    # Die Wort-Kennung entsteht erst beim Ausliefern, aus deutschem und
    # bosnischem Wort - genauso wie in start.lade_daten(). Steht sie hier
    # anders, erkennt die App die Woerter nicht wieder.
    woerter, level = [], []
    for k in vokabeln.KATEGORIEN:
        level.append(k["id"])
        for w in k["words"]:
            woerter.append("%s:%s" % (w.get("de", "").strip().lower(), w.get("bs", "")))
    gelesen = [g["id"] for g in geschichten.GESCHICHTEN]

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
        # „heute noch nicht geübt" und „noch keine Lernserie" – bei 43
        # bestandenen Leveln. Und die Tagesaufgaben blieben auf Stufe 1,
        # damit wäre ein ganzer Zweig der App gar nicht anschaubar.
        "tage": lerntage(),
        "frost": [],
        # Alles aus dem Laden schon gekauft, damit man den Drachen
        # anziehen kann, ohne erst sparen zu müssen. In der zweiten Datei
        # nicht: dort soll der Laden ja gerade ausprobiert werden.
        "besitz": ["brille", "kopfhoerer", "hut", "krone"] if alles_gewusst else [],
        # Und eines davon gleich aufgesetzt – sonst steht der Drache nackt
        # da, obwohl alles gekauft ist.
        "getragen": "krone" if alles_gewusst else "",
        "leben": {"anzahl": 5, "zeit": 0},
        "schutz": {"anzahl": 2, "zeit": 0},
        # Leer lassen: Münzen gibt es nur in dem Augenblick, in dem ein
        # Zähler sein Ziel überschreitet. Vorgefüllt gäbe es beim Testen nie
        # wieder eine Münze und nie die Jubelmeldung.
        "tagwerk": {},
        "muenzen_ges": MUENZEN,
        "muenzen_aus": 0,
        "premium": premium,
    }


def schreibe(name, premium, hinweis, alles_gewusst=True):
    d = {"app": "zmaj", "version": 1, "aus": hinweis,
         "stand": stand(premium, alles_gewusst)}
    pfad = os.path.join(ZIEL, name)
    io.open(pfad, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=1))
    s = d["stand"]
    print("  %-30s %4d Wörter, %2d Level, %2d Geschichten, %2d Lerntage, "
          "%d Münzen, Vollversion %s"
          % (name, len(s["gewusst"]), len(s["bestanden"]), len(s["gelesen"]),
             len(s["tage"]), s["muenzen_ges"], "an " if premium else "aus"))
    return pfad


def main():
    os.makedirs(ZIEL, exist_ok=True)
    print("Testdaten bauen ...\n")
    schreibe("zmaj-test-vollversion.json", True, "Test mit Vollversion")
    schreibe("zmaj-test-alles-offen.json", False, "Test ohne Vollversion",
             alles_gewusst=False)
    print("\nLiegt in: %s" % ZIEL)
    print("In der App: Einstellungen > Sicherung > Sicherung einlesen.")
    print("Achtung: Das ersetzt den Stand auf dem Gerät. Eigenen vorher sichern.")


if __name__ == "__main__":
    main()
