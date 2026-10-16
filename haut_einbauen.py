# -*- coding: utf-8 -*-
"""
haut_einbauen.py  -  holt die Bildteile des Drachen als WebP in die App

Seit dem 15.10.2026 ist der Drache in der App aus Bildern zusammengesetzt
(Google Gemini, geschnitten in 32 Teile, siehe zmaj_lottie.py "Bild-Drache").
Die Teile entstehen als PNG ausserhalb des Repos, in
App Zeugs\\Profilbild\\Drache_Bildteile\\ (dort LIESMICH.txt: fertig\\teile\\ ist
der Grundsatz, fertig\\haut\\<farbe>\\ sind die Hautsaetze). Dieses Skript
wandelt sie in WebP um und legt sie dorthin, wo zmaj.json sie sucht:

    python haut_einbauen.py --teile ORDNER
        Grundsatz (der blaue Drache): ORDNER/<teil>.png
        -> web/maskottchen/teile/<teil>.webp

    python haut_einbauen.py ORDNER
        Hautfarben: ORDNER/<farbe>/<teil>.png
        -> web/maskottchen/haut/<farbe>/<teil>.webp
        Jeder Unterordner, dessen Name eine Farbe der App ist (FARBEN in
        web/index.html, siehe FARBEN unten; seit 16.10.2026 auch das
        gemalte Skelett "skelett"), wird uebernommen. --nur gruen,rosa
        schraenkt ein. Ein Teil, das kleiner ist als sein Feld (FELD
        unten, die Haende an der Wange), wird durchsichtig erweitert.

    python haut_einbauen.py --zierrat ORDNER
        gemalte Kostueme (seit 16.10.2026): ORDNER/<stueck>/<teil>.png
        -> web/maskottchen/zierrat/<stueck>/<teil>.webp
        Jeder Unterordner wird uebernommen, dessen Name ein Stueck des
        Ladens ist (es gibt web/maskottchen/zmajz-<stueck>.json). Welche
        Teile ein Stueck hat und wie gross sie sind, steht in zmaj_lottie.py
        (GEMALTE_HUETE, GEMALTE_RUMPFSTUECKE, GEMALTE_AERMEL) - danach
        zmaj_lottie.py laufen lassen, es prueft Namen und Groessen.

    python haut_einbauen.py --pruefen
        wandelt nichts, prueft nur web/maskottchen/teile, haut/ und zierrat/

Alle Saetze bekommen dieselben Einstellungen (WEBP unten): verlustbehaftet
mit Qualitaet 90, Alpha verlustfrei. Am 15.10.2026 an den Teilen gemessen:
1,6 MB PNG -> 0,33 MB WebP, kleinster Abstand 39,8 dB (Kopf), Farben und
Deckkraft unveraendert; auch dreifach vergroessert ist kein Unterschied zu
sehen. In der App erscheint der Drache hoechstens mit 1 Geraetepixel je
Leinwand-Einheit, die Bilder haben 2.

Ein Hautsatz wird nur ganz oder gar nicht uebernommen: es muessen genau die
Teile da sein, die in teile/ liegen, jedes in derselben Groesse - sonst
saesse ein Teil schief oder fehlte, und die App zeigte an seiner Stelle
nichts. Die App nimmt einen Hautsatz nur, wenn web/inhalt ihn kennt:
danach also inhalt_bauen.py laufen lassen (app_bauen.py prueft das).

Umgewandelt wird mit ffmpeg (libwebp), wie die Tonspur in app_bauen.py -
nur Standardbibliothek, keine Abhaengigkeit fuer App oder Bau. Gesucht wird
ffmpeg in ZMAJ_FFMPEG, dann in ../werkzeuge/ffmpeg/bin, dann im PATH.
"""

import os
import shutil
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
MASKOTTCHEN = os.path.join(HIER, "web", "maskottchen")
TEILE = os.path.join(MASKOTTCHEN, "teile")
HAUT = os.path.join(MASKOTTCHEN, "haut")
ZIERRAT = os.path.join(MASKOTTCHEN, "zierrat")
# Die Hautfarben der App (FARBEN in web/index.html). Ein Ordner mit anderem
# Namen waere fuer die App unsichtbar.
# Vom 15.10. bis 16.10.2026 ohne "skelett": der damalige Bildsatz war ein
# umgefaerbter Drache mit Fleisch und Augen mit Iris - gegen die
# Fest-Entscheidung vom 01.10.2026 (nur Knochen). Seit 16.10.2026 gibt es
# ein von Gemini als Skelett GEMALTES Bildset (nur Knochen, runde schwarze
# Hoehlen mit gelbem Punkt, boeser Blick nach Ajdins Wunsch vom
# 15.10.2026); es ist der Hautsatz haut/skelett/, das Vektor-Skelett bleibt
# der Rueckfall (zmaj_lottie.py, HAUT_ERSETZT). OHNE_HAUTSATZ sind die
# Farben aus FARBEN, die bewusst keinen Bildsatz bekommen - zurzeit keine.
OHNE_HAUTSATZ = []
FARBEN = ["gruen", "rosa", "rot", "lila", "nacht", "gold", "silber", "kupfer", "galaxie", "skelett"]
# Teile, deren Feld in der App groesser ist als ihr Bild im Grundsatz
# (16.10.2026): Das Skelett haelt sich beim Weinen die Knochenhaende vor die
# Augenhoehlen, dafuer sind seine Haende an der Wange 114 x 220 statt
# 88 x 151 Pixel gross. Alle Saetze teilen sich in zmaj.json dieselbe
# Asset-Groesse, darum wird ein kleineres Bild beim Umwandeln durchsichtig
# auf das Feld erweitert - an der Stelle x, y, so dass sein Drehpunkt
# dorthin faellt, wo BILD_TEILE in zmaj_lottie.py ihn erwartet. Die PNG-
# Quellen bleiben, wie sie sind.
#   teil: (Breite, Hoehe, x, y des kleineren Bildes im Feld)
FELD = {"unterarmL_wange": (114, 220, 0, 0), "unterarmR_wange": (114, 220, 26, 0)}
# -pix_fmt bgra: libwebp rechnet selbst von RGB nach YUV. Ueber yuva420p
# rechnete ffmpeg vorher um, und die Farben verschoben sich leicht.
# -preset drawing: fuer flache Flaechen mit Umriss gedacht.
WEBP = ["-pix_fmt", "bgra", "-c:v", "libwebp", "-lossless", "0", "-quality", "90",
        "-compression_level", "6", "-preset", "drawing"]


def ffmpeg_finden():
    for kandidat in (os.environ.get("ZMAJ_FFMPEG"),
                     os.path.join(os.path.dirname(HIER), "werkzeuge", "ffmpeg", "bin", "ffmpeg.exe"),
                     shutil.which("ffmpeg")):
        if kandidat and os.path.isfile(kandidat):
            return kandidat
    return None


def png_groesse(pfad):
    """(Breite, Hoehe) aus dem IHDR-Block, oder None."""
    with open(pfad, "rb") as f:
        k = f.read(24)
    if len(k) < 24 or k[:8] != b"\x89PNG\r\n\x1a\n" or k[12:16] != b"IHDR":
        return None
    return int.from_bytes(k[16:20], "big"), int.from_bytes(k[20:24], "big")


def webp_groesse(pfad):
    """(Breite, Hoehe) einer WebP-Datei aus dem Kopf, oder None.
    VP8X: erweitertes Format (mit Alpha, so schreibt ffmpeg es),
    VP8L: verlustfrei, 'VP8 ': einfach verlustbehaftet."""
    with open(pfad, "rb") as f:
        k = f.read(30)
    if len(k) < 30 or k[:4] != b"RIFF" or k[8:12] != b"WEBP":
        return None
    art = k[12:16]
    if art == b"VP8X":
        return 1 + int.from_bytes(k[24:27], "little"), 1 + int.from_bytes(k[27:30], "little")
    if art == b"VP8L":
        b = int.from_bytes(k[21:25], "little")
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    if art == b"VP8 ":
        return int.from_bytes(k[26:28], "little") & 0x3FFF, int.from_bytes(k[28:30], "little") & 0x3FFF
    return None


def grundsatz():
    """{teil: (Breite, Hoehe)} der Teile in web/maskottchen/teile."""
    if not os.path.isdir(TEILE):
        return {}
    return {n[:-5]: webp_groesse(os.path.join(TEILE, n)) for n in sorted(os.listdir(TEILE)) if n.endswith(".webp")}


def im_feld(teil, groesse):
    """Die Groesse, die ein Teil nach dem Umwandeln hat: ein Bild, das in
    sein Feld (FELD) passt, wird auf das Feld erweitert."""
    if teil in FELD and groesse and tuple(groesse) != FELD[teil][:2]:
        b, h, x, y = FELD[teil]
        if groesse[0] + x <= b and groesse[1] + y <= h:
            return (b, h)
    return groesse


def satz_fehler(groessen, soll):
    """Was an einem Satz {teil: (b, h)} gegenueber dem Grundsatz nicht stimmt."""
    fehler = ["fehlt: %s" % t for t in sorted(set(soll) - set(groessen))]
    fehler += ["%s ist %s statt %s" % (t, groessen[t], soll[t])
               for t in sorted(set(soll) & set(groessen)) if groessen[t] != soll[t]]
    return fehler


def umwandeln(ffmpeg, quelle, ziel, nur=None, feld=True):
    """PNG-Ordner -> WebP-Ordner, erst in einen Nebenordner, dann getauscht:
    bricht ffmpeg mittendrin ab, bleibt der alte Satz stehen. nur: Teile,
    die mitkommen sollen (was der Grundsatz nicht kennt, kennt zmaj.json
    nicht). feld: Teile des Drachen auf ihr Feld erweitern (FELD) - nicht
    bei den Kostuemen, deren Aermel an der Wange heisst genauso, hat aber
    ein eigenes Feld (beim ersten Lauf am 16.10.2026 passiert)."""
    namen = sorted(n for n in os.listdir(quelle) if n.lower().endswith(".png") and (nur is None or n[:-4] in nur))
    # Der Nebenordner faengt mit "_" an: app_bauen.py nimmt solche Ordner
    # nie mit, falls doch einmal einer liegen bleibt.
    neu = os.path.join(os.path.dirname(ziel), "_neu_" + os.path.basename(ziel))
    alt = os.path.join(os.path.dirname(ziel), "_alt_" + os.path.basename(ziel))
    shutil.rmtree(neu, ignore_errors=True)
    os.makedirs(neu)
    for n in namen:
        # Kleiner als sein Feld (FELD): durchsichtig erweitern. format=rgba
        # vorweg, sonst fuellt pad den Rand nicht durchsichtig.
        # 16.10.2026: Die Filterliste hiess hier auch "feld" und ueberschrieb
        # den Parameter, bevor er geprueft wurde - die Bedingung war immer
        # falsch, und die Haende an der Wange (88 x 151) kamen unerweitert
        # heraus, statt 114 x 220 wie das Asset in zmaj.json. Die WebPs im
        # Repo stimmten nur, weil sie anders entstanden waren; beim naechsten
        # --teile oder neuen Hautsatz waere die Hand verzerrt gewesen.
        teil, ist = n[:-4], png_groesse(os.path.join(quelle, n))
        filter_ = []
        if feld and ist and im_feld(teil, ist) != ist:
            b, h, x, y = FELD[teil]
            filter_ = ["-vf", "format=rgba,pad=%d:%d:%d:%d:color=0x00000000" % (b, h, x, y)]
        r = subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", os.path.join(quelle, n)]
                           + filter_ + WEBP + [os.path.join(neu, n[:-4] + ".webp")], capture_output=True, text=True)
        if r.returncode:
            shutil.rmtree(neu, ignore_errors=True)
            raise SystemExit("ffmpeg scheiterte an %s:\n%s" % (n, r.stderr.strip()))
    shutil.rmtree(alt, ignore_errors=True)
    if os.path.isdir(ziel):
        os.replace(ziel, alt)
    os.replace(neu, ziel)
    shutil.rmtree(alt, ignore_errors=True)
    return sum(os.path.getsize(os.path.join(ziel, n)) for n in os.listdir(ziel))


def pruefen():
    """Grundsatz und alle Hautsaetze in web/maskottchen pruefen."""
    soll = grundsatz()
    if not soll:
        print("web/maskottchen/teile fehlt oder ist leer.")
        return 1
    print("teile/: %d Teile, %d KB" % (len(soll), sum(os.path.getsize(os.path.join(TEILE, t + ".webp")) for t in soll) // 1024))
    schlecht = 0
    for farbe in sorted(os.listdir(HAUT)) if os.path.isdir(HAUT) else []:
        ordner = os.path.join(HAUT, farbe)
        if not os.path.isdir(ordner):
            continue
        ist = {n[:-5]: webp_groesse(os.path.join(ordner, n)) for n in os.listdir(ordner) if n.endswith(".webp")}
        fehler = satz_fehler(ist, soll) + ([] if farbe in FARBEN else ["%s ist keine Farbe der App" % farbe])
        groesse = sum(os.path.getsize(os.path.join(ordner, n)) for n in os.listdir(ordner)) // 1024
        print("haut/%s/: %s, %d KB" % (farbe, "in Ordnung" if not fehler else "; ".join(fehler[:4]), groesse))
        schlecht += bool(fehler)
    # Gemalte Kostueme: ob die Bilder da sind und passen, prueft
    # zmaj_lottie.py (es kennt die Teile); hier nur, was wo liegt.
    for stueck in sorted(os.listdir(ZIERRAT)) if os.path.isdir(ZIERRAT) else []:
        ordner = os.path.join(ZIERRAT, stueck)
        if os.path.isdir(ordner):
            fehler = [] if os.path.isfile(os.path.join(MASKOTTCHEN, "zmajz-%s.json" % stueck)) else ["kein Stueck der App"]
            print("zierrat/%s/: %d Bilder, %d KB%s" % (stueck, len(os.listdir(ordner)),
                                                      sum(os.path.getsize(os.path.join(ordner, n)) for n in os.listdir(ordner)) // 1024,
                                                      "; " + fehler[0] if fehler else ""))
            schlecht += bool(fehler)
    return 1 if schlecht else 0


def zierrat_einbauen(ffmpeg, quelle):
    """ORDNER/<stueck>/<teil>.png -> web/maskottchen/zierrat/<stueck>/<teil>.webp,
    je Stueck ganz oder gar nicht (umwandeln tauscht den Ordner erst am Ende)."""
    fertig = []
    for stueck in sorted(os.listdir(quelle)):
        ordner = os.path.join(quelle, stueck)
        if not os.path.isdir(ordner):
            continue
        if not os.path.isfile(os.path.join(MASKOTTCHEN, "zmajz-%s.json" % stueck)):
            print("uebersprungen: %s - kein Stueck der App (zmajz-%s.json fehlt)" % (stueck, stueck))
            continue
        os.makedirs(ZIERRAT, exist_ok=True)
        groesse = umwandeln(ffmpeg, ordner, os.path.join(ZIERRAT, stueck), feld=False)
        fertig.append(stueck)
        print("zierrat/%s/: %d KB" % (stueck, groesse // 1024))
    print("\n%d Stuecke uebernommen. Jetzt zmaj_lottie.py laufen lassen - es prueft Namen und Groessen."
          % len(fertig))
    return 0 if fertig else 1


def main(argv):
    if "--pruefen" in argv:
        return pruefen()
    nur = None
    if "--nur" in argv:
        nur = set(argv[argv.index("--nur") + 1].split(","))
        argv = argv[:argv.index("--nur")] + argv[argv.index("--nur") + 2:]
    teile = "--teile" in argv
    zierrat = "--zierrat" in argv
    rest = [a for a in argv if a not in ("--teile", "--zierrat")]
    if len(rest) != 1 or not os.path.isdir(rest[0]) or (teile and zierrat):
        print(__doc__)
        return 1
    quelle = os.path.abspath(rest[0])
    ffmpeg = ffmpeg_finden()
    if not ffmpeg:
        raise SystemExit("ffmpeg nicht gefunden (ZMAJ_FFMPEG, ../werkzeuge/ffmpeg/bin oder PATH).")
    if zierrat:
        return zierrat_einbauen(ffmpeg, quelle)

    if teile:
        n = len([x for x in os.listdir(quelle) if x.lower().endswith(".png")])
        if not n:
            raise SystemExit("In %s liegen keine PNG-Dateien." % quelle)
        groesse = umwandeln(ffmpeg, quelle, TEILE)
        print("teile/: %d Teile, %d KB" % (n, groesse // 1024))
        print("Jetzt zmaj_lottie.py laufen lassen - es prueft Namen und Groessen.")
        return 0

    soll = grundsatz()
    if not soll:
        raise SystemExit("Erst den Grundsatz einbauen: python haut_einbauen.py --teile ORDNER")
    fertig, uebersprungen = [], []
    for farbe in sorted(os.listdir(quelle)):
        ordner = os.path.join(quelle, farbe)
        if not os.path.isdir(ordner) or (nur and farbe not in nur):
            continue
        if farbe not in FARBEN:
            print("uebersprungen: %s - keine Farbe der App (%s)" % (farbe, ", ".join(FARBEN)))
            continue
        ist = {n[:-4]: im_feld(n[:-4], png_groesse(os.path.join(ordner, n)))
               for n in os.listdir(ordner) if n.lower().endswith(".png")}
        fehler = satz_fehler(ist, soll)
        if fehler:
            uebersprungen.append(farbe)
            print("uebersprungen: %s - %s" % (farbe, "; ".join(fehler[:4]) + (" ..." if len(fehler) > 4 else "")))
            continue
        os.makedirs(HAUT, exist_ok=True)
        groesse = umwandeln(ffmpeg, ordner, os.path.join(HAUT, farbe), nur=soll)
        fertig.append(farbe)
        print("haut/%s/: %d Teile, %d KB" % (farbe, len(soll), groesse // 1024))
    if fertig:
        print("\nUebernommen: %s. Jetzt inhalt_bauen.py laufen lassen, damit die App sie kennt." % ", ".join(fertig))
    if not fertig and not uebersprungen:
        print("In %s liegt kein Ordner mit einer Hautfarbe." % quelle)
    return 1 if uebersprungen else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
