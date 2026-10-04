# -*- coding: utf-8 -*-
r"""
demo_bauen.py  –  die App als Webseite zum Ausprobieren, ohne Werbung

    python3 demo_bauen.py              # nach _site/
    python3 demo_bauen.py --ziel pfad

Das Ergebnis ist ein Ordner, den jeder Dateiserver ausliefern kann; der
Workflow .github/workflows/demo.yml stellt ihn auf GitHub Pages. Wer das
README liest, kann Zmaj so in zwanzig Sekunden im Browser ausprobieren,
ohne etwas zu installieren.

WAS ANDERS IST ALS IN DER APP: keine Werbung. Auf einer Webseite gibt es
kein AdMob, die App würde Platzhalter zeigen. Deshalb werden hier zwei
Schalter gemeinsam umgelegt, so wie sprachen.py es für die App vorsieht:

  1. WERBUNG_LAEUFT aus  ->  der Inhalt sagt werbung_laeuft = false, und die
     Datenschutzerklärung bekommt den Abschnitt ohne Werbepartner
     (set.dsgvo_werbung_aus). Text und Verhalten passen zusammen.
  2. WERBUNG_AN in index.html auf false  ->  keine Platzhalter-Anzeigen.

Der zweite Schritt folgt dem Muster der *_richten.py-Skripte: Der gesuchte
Text muss genau einmal vorkommen, sonst bricht das Skript ab. An web/ selbst
wird nichts geändert, nur an der Kopie.
"""
import argparse
import io
import os
import shutil
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HIER, "web")
sys.path.insert(0, HIER)

# Nicht in die Demo: Probedateien und der vom Server erzeugte Inhalt
WEG = ("_probe", "inhalt", "_feature.html")
WERBUNG_ALT = "const WERBUNG_AN          = true;"
WERBUNG_NEU = "const WERBUNG_AN          = false;"


def kopieren(ziel):
    if os.path.exists(ziel):
        shutil.rmtree(ziel)
    shutil.copytree(WEB, ziel, ignore=lambda ordner, namen: [n for n in namen if n in WEG])


def werbung_aus_in_html(ziel):
    pfad = os.path.join(ziel, "index.html")
    html = io.open(pfad, encoding="utf-8", newline="").read()
    if html.count(WERBUNG_ALT) != 1:
        raise SystemExit("Abbruch: '%s' steht %d-mal in index.html statt einmal."
                         % (WERBUNG_ALT, html.count(WERBUNG_ALT)))
    io.open(pfad, "w", encoding="utf-8", newline="").write(html.replace(WERBUNG_ALT, WERBUNG_NEU))


def ohne_werbung(code, daten):
    """Für inhalt_bauen.schreiben(): Texte ohne Werbehinweise."""
    sprachen_neu = sys.modules["sprachen"]   # lade_daten() hat sprachen.py neu geladen ...
    vorher = sprachen_neu.WERBUNG_LAEUFT
    sprachen_neu.WERBUNG_LAEUFT = False      # ... deshalb erst danach umlegen
    try:
        daten["texte"] = sprachen_neu.texte(code)
    finally:
        sprachen_neu.WERBUNG_LAEUFT = vorher  # wer sprachen danach liest, sieht die App
    daten["werbung_laeuft"] = False


def inhalt_ohne_werbung(ziel):
    import inhalt_bauen
    liste = inhalt_bauen.schreiben(os.path.join(ziel, "inhalt"), anpassen=ohne_werbung)
    inhalt_bauen.pruefen(liste)
    return liste


def main(argv=None):
    p = argparse.ArgumentParser(description="Zmaj als Webseite ohne Werbung")
    p.add_argument("--ziel", default=os.path.join(HIER, "_site"))
    a = p.parse_args(argv)
    kopieren(a.ziel)
    werbung_aus_in_html(a.ziel)
    inhalt_ohne_werbung(a.ziel)
    # GitHub Pages soll die Dateien unverändert ausliefern, ohne Jekyll
    io.open(os.path.join(a.ziel, ".nojekyll"), "w").close()
    groesse = sum(os.path.getsize(os.path.join(w, f)) for w, _, fs in os.walk(a.ziel) for f in fs)
    print("Demo in %s, %.1f MB" % (os.path.relpath(a.ziel, HIER), groesse / 1048576.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
