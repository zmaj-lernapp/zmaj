# -*- coding: utf-8 -*-
r"""
ton_auffaellig.py  –  sucht Aufnahmen, die wahrscheinlich falsch sind

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_auffaellig.py

ton_pruefen.py ist der Torwächter: es sagt, ob alle Aufnahmen DA sind. Es sagt
nicht, ob sie RICHTIG sind. Genau das versucht dieses Skript, ohne dass jemand
1502 Dateien anhören muss.

Anlass: Am 25.09.2026 fiel auf, dass die Stimme bei „sud" (Gericht) „sub" sagt
und „nju" verfremdet klingt. Beide Dateien waren vorhanden und wurden gefunden
– ton_pruefen.py hatte nichts zu beanstanden. Die Frage war: Wie viele solche
Fälle stecken noch drin?

GEPRÜFT WIRD IN VIER RICHTUNGEN:

A  Zwei verschiedene Wörter, dieselbe Aufnahme.
   Das wäre eine echte Verwechslung: Man hört ein Wort und lernt ein anderes.
   Erkannt über den SHA-256 der Dateien.

B  Aufnahmen, die für ihren Text zu kurz oder zu lang sind.
   Alle Dateien kommen von derselben Stimme mit derselben Bitrate, deshalb ist
   die Dateigröße ein brauchbares Maß für die Sprechdauer. Ein langes Wort mit
   winziger Datei ist abgeschnitten, ein kurzes mit großer enthält mehr, als
   dastehen sollte.

C  Wörter, an denen eine Sprachsynthese erfahrungsgemäß scheitert.
   Kurze Wörter mit stimmhaftem Endlaut sind die häufigste Falle – genau das
   Muster von „sud". Dazu Wörter mit Buchstaben, die es im Bosnischen nicht
   gibt, und Abkürzungen.

D  Aufnahmen, auf die kein Wort mehr zeigt (Karteileichen).

Das Ergebnis ist eine Liste zum Nachhören, keine Fehlerliste. Wer eine Datei
neu einsprechen will, schreibt einfach über die vorhandene – der Name bleibt.
"""

import hashlib
import io
import json
import os
import re
import sys
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HIER, "web", "audio")
INDEX = os.path.join(AUDIO, "index.json")

# Bosnisch kennt diese Buchstaben nicht. Kommen sie vor, ist es ein Fremdwort
# oder ein Tippfehler – beides spricht die Stimme oft daneben.
FREMD = set("qwxy")
# Stimmhafte Endlaute: im Bosnischen werden sie am Wortende härter gesprochen.
# Genau daran ist „sud" gescheitert, das als „sub" herauskam.
STIMMHAFT_ENDE = tuple("bdgzvž")
# Vokale des Bosnischen. Das r kann selbst eine Silbe tragen, wenn kein Vokal
# daneben steht: „prst", „srce", „crkva". Ajdin am 26.09.2026: „das wird
# wahrscheinlich auch bei vrt prt smrt usw auch so sein" – und er hatte recht.
# Bei „brz" stand genau das in seiner Notiz: „das r hört man zu wenig".
VOKALE = set("aeiou")


def hat_silbisches_r(wort):
    """Steht ein r zwischen zwei Konsonanten, trägt es selbst die Silbe."""
    w = wort.lower()
    for i, ch in enumerate(w):
        if ch != "r":
            continue
        davor = w[i - 1] if i > 0 else ""
        danach = w[i + 1] if i + 1 < len(w) else ""
        if davor not in VOKALE and danach not in VOKALE:
            return True
    return False


def schluessel(text):
    """Dieselbe Regel wie in index.html: nur die erste Variante zählt."""
    return text.split(" / ")[0].rstrip(".!?…").strip().lower()


def main():
    if not os.path.exists(INDEX):
        print("ABBRUCH: %s fehlt. Erst ton_bauen.py laufen lassen." % INDEX)
        return 1

    index = json.load(io.open(INDEX, encoding="utf-8"))
    # Jeder Eintrag in index["toene"]: key (Suchschlüssel), datei, text
    # (was gesprochen wurde), stimme.
    toene = index["toene"]
    paare = [(e["text"], e["datei"]) for e in toene]
    stimme_von = {e["text"]: e.get("stimme", "?") for e in toene}
    print("%d Aufnahmen im Index." % len(paare))
    zaehler = {}
    for e in toene:
        s = e.get("stimme", "?")
        zaehler[s] = zaehler.get(s, 0) + 1
    for s, n in sorted(zaehler.items(), key=lambda x: -x[1]):
        print("   %-26s %5d" % (s, n))
    print()

    # Dateien einlesen
    groesse, hash_zu_texten, fehlend = {}, defaultdict(list), []
    for text, datei in paare:
        pfad = os.path.join(AUDIO, datei)
        if not os.path.exists(pfad):
            fehlend.append((text, datei))
            continue
        roh = io.open(pfad, "rb").read()
        groesse[text] = len(roh)
        hash_zu_texten[hashlib.sha256(roh).hexdigest()].append((text, datei))

    strich = "=" * 66
    befunde = 0

    # ---------------------------------------------------------------- A
    print(strich)
    print("A. Zwei verschiedene Wörter teilen sich eine Aufnahme")
    print(strich)
    doppelt = {h: v for h, v in hash_zu_texten.items() if len(v) > 1}
    if not doppelt:
        print("  nichts. Jede Aufnahme gehört zu genau einem Wort.")
    for h, gruppe in sorted(doppelt.items(), key=lambda x: -len(x[1])):
        # Gleicher Sprechtext ist in Ordnung: „Da" und „Da." klingen gleich
        sprech = {schluessel(t) for t, _ in gruppe}
        art = "in Ordnung, gleicher Sprechtext" if len(sprech) == 1 else "PRÜFEN"
        if art == "PRÜFEN":
            befunde += 1
        print("  [%s] %s" % (art, ", ".join('„%s" (%s)' % (t, d) for t, d in gruppe)))
    print()

    # ---------------------------------------------------------------- B
    print(strich)
    print("B. Aufnahme passt nicht zur Länge des Textes")
    print(strich)
    # Bytes je Zeichen taugt nicht als Maß: Jede Aufnahme trägt eine feste
    # Grundlast an Stille am Anfang und Ende. Bei „Da" sind das fast 100 %
    # der Datei, bei einer Geschichte kaum etwas. Deshalb ein lineares Modell
    #     Größe ≈ Grundlast + Bytes_je_Zeichen * Zeichen
    # das über die kleinsten Quadrate an alle Aufnahmen angepasst wird.
    punkte = [(len(schluessel(text)), g) for text, g in groesse.items()
              if len(schluessel(text)) >= 2]
    werte = []
    if punkte:
        N = len(punkte)
        sx = sum(n for n, _ in punkte)
        sy = sum(g for _, g in punkte)
        sxx = sum(n * n for n, _ in punkte)
        sxy = sum(n * g for n, g in punkte)
        nenner = N * sxx - sx * sx
        steigung = (N * sxy - sx * sy) / float(nenner) if nenner else 0.0
        grundlast = (sy - steigung * sx) / float(N)
        print("  Erwartet: %.0f Bytes Grundlast + %.0f Bytes je Zeichen"
              % (grundlast, steigung))
        print("  (%d Aufnahmen als Grundlage)" % N)
        print()
        for text, g in groesse.items():
            n = len(schluessel(text))
            if n < 2:
                continue
            soll = grundlast + steigung * n
            if soll > 0:
                werte.append((g / soll, text, g, n))
        werte.sort()
        # Ein Drittel der erwarteten Länge heißt: da fehlt der halbe Satz.
        zu_kurz = [w for w in werte if w[0] < 0.35]
        zu_lang = [w for w in werte if w[0] > 3.0]
        if zu_kurz:
            print("  Auffällig KURZ – könnte abgeschnitten sein:")
            for q, text, g, n in zu_kurz[:15]:
                print("    %-36s %7d Bytes bei %3d Zeichen  = %2.0f%% des Erwarteten"
                      % ('„%s“' % text[:32], g, n, q * 100))
                befunde += 1
            if len(zu_kurz) > 15:
                print("    ... und %d weitere" % (len(zu_kurz) - 15))
        if zu_lang:
            print("  Auffällig LANG – enthält vielleicht mehr als den Text:")
            for q, text, g, n in zu_lang[-15:]:
                print("    %-36s %7d Bytes bei %3d Zeichen  = %2.0f%% des Erwarteten"
                      % ('„%s“' % text[:32], g, n, q * 100))
                befunde += 1
            if len(zu_lang) > 15:
                print("    ... und %d weitere" % (len(zu_lang) - 15))
        if not zu_kurz and not zu_lang:
            print("  nichts. Alle Aufnahmen liegen im erwarteten Bereich.")
    print()

    # ---------------------------------------------------------------- C
    print(strich)
    print("C. Wörter, an denen eine Sprachsynthese gern scheitert")
    print(strich)
    risiko = []
    for text in groesse:
        s = schluessel(text)
        wort = s.split()[0] if s.split() else s
        gruende = []
        # Das Muster von „sud": kurz und stimmhaft am Ende. Dort hat die
        # Stimme „sub" gesagt. „sehr kurz" allein ist KEIN Verdacht - sonst
        # stehen 80 harmlose Füllwörter in der Liste und niemand hört sie an.
        if len(s) <= 4 and s.endswith(STIMMHAFT_ENDE):
            gruende.append('kurz mit stimmhaftem Endlaut, wie „sud“ → „sub“')
        if hat_silbisches_r(wort):
            gruende.append('silbisches r, bei „brz“ zu schwach gesprochen')
        if FREMD & set(s):
            # sprechtext() in ton_bauen.py schreibt x, q, w, y vor der Aufnahme
            # um (aus „Rex" wird „Reks"), genauso wie fuerStimme() beim
            # Vorlesen. Geprüft am 26.09.2026, beide Listen stimmen überein.
            # Der Hinweis bleibt als Wächter: Fällt eine der beiden Stellen
            # weg, verschluckt die Stimme den Buchstaben wieder.
            gruende.append("Buchstabe %s - wird umgeschrieben, sollte passen"
                           % "".join(sorted(FREMD & set(s))))
        if re.search(r"\b[A-ZČĆŽŠĐ]{2,}\b", text):
            gruende.append("Großbuchstaben, wird buchstabiert statt gesprochen")
        if re.search(r"\d", s):
            gruende.append("Ziffer im Text")
        if gruende:
            risiko.append((s, text, gruende))
    risiko.sort()
    if not risiko:
        print("  nichts.")
    else:
        print("  %d Aufnahmen zum Nachhören:\n" % len(risiko))
        for s, text, gruende in risiko:
            print("    %-26s %s" % ('„%s"' % text[:24], "; ".join(gruende)))
    print()

    # ---------------------------------------------------------------- D
    print(strich)
    print("D. Dateien im Ordner, auf die kein Wort zeigt")
    print(strich)
    benutzt = {d for _, d in paare}
    liegen = {d for d in os.listdir(AUDIO)
              if d.lower().endswith((".mp3", ".m4a", ".wav", ".ogg"))}
    leichen = sorted(liegen - benutzt)
    if not leichen:
        print("  nichts. Jede Datei im Ordner wird auch benutzt.")
    else:
        print("  %d Karteileichen (kosten Platz im Paket):" % len(leichen))
        for d in leichen[:20]:
            print("    " + d)
        if len(leichen) > 20:
            print("    ... und %d weitere" % (len(leichen) - 20))
    if fehlend:
        print("\n  %d Einträge zeigen auf eine Datei, die es nicht gibt:" % len(fehlend))
        for t, d in fehlend[:10]:
            print('    „%s" -> %s' % (t, d))
    print()

    print(strich)
    print("%d Stellen, die einen Blick wert sind." % befunde)
    print("Abschnitt C ist eine Liste zum Nachhören, keine Fehlerliste.")
    print("Zum Ersetzen einfach über die vorhandene Datei schreiben, der Name bleibt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
