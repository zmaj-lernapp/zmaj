# -*- coding: utf-8 -*-
r"""
app_bauen.py  –  bringt den Inhalt in die Android-Hülle

Die Android-App liegt in einem eigenen Ordner neben diesem Projekt:

    C:\Users\Ajdin\Desktop\zmaj-android

Warum getrennt? Weil dieser Ordner „Bosnisch Lernapp" heißt – mit Leerzeichen.
Android-Builds stolpern darüber. Der Nachbarordner hat keins.

Dieses Skript kopiert web/ dorthin nach www/ und ruft Capacitor auf, damit
die Dateien im Android-Projekt landen. Danach in Android Studio bauen.

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" app_bauen.py

Nicht mitkopiert werden: die Probeaufnahmen, die Sicherungen von index.html
und die LIESMICH-Dateien. Die gehören nicht in die App.
"""
import io
import re
import os
import shutil
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HIER, "web")
HUELLE = os.path.join(os.path.dirname(HIER), "zmaj-android")
WWW = os.path.join(HUELLE, "www")

# Was in der App nichts verloren hat
RAUS_ORDNER = {"_probe"}
RAUS_DATEIEN = {"liesmich.txt"}
RAUS_ENDUNGEN = (".sicherung", ".bak", ".orig", ".alt")
# Sicherungen heissen index.html.vor_audio, .vor_lokal, .vor_sicherung und so
# weiter - eine feste Liste vergisst man beim naechsten Umbau. Deshalb ein
# Muster statt Aufzaehlung.
RAUS_ENTHAELT = (".vor_",)


def kopieren():
    if not os.path.isdir(HUELLE):
        raise SystemExit("Die Android-Hülle fehlt: %s" % HUELLE)
    shutil.rmtree(WWW, ignore_errors=True)
    dateien = 0
    for wurzel, ordner, namen in os.walk(WEB):
        ordner[:] = [o for o in ordner if o not in RAUS_ORDNER]
        ziel = os.path.join(WWW, os.path.relpath(wurzel, WEB))
        os.makedirs(ziel, exist_ok=True)
        for n in namen:
            klein = n.lower()
            if (klein in RAUS_DATEIEN or klein.endswith(RAUS_ENDUNGEN)
                    or any(s in klein for s in RAUS_ENTHAELT)):
                continue
            shutil.copy2(os.path.join(wurzel, n), os.path.join(ziel, n))
            dateien += 1
    groesse = sum(os.path.getsize(os.path.join(w, n))
                  for w, _, ns in os.walk(WWW) for n in ns)
    print("%d Dateien kopiert, %.1f MB" % (dateien, groesse / 1048576.0))
    return dateien


def pruefen():
    """Kein halbes Paket ausliefern: Tonspur muss vollständig sein."""
    sys.path.insert(0, HIER)
    import ton_pruefen
    if ton_pruefen.main() != 0:
        raise SystemExit("\nABBRUCH: Die Tonspur ist unvollständig. Nichts kopiert.")


# Die von AGP 9 abgelehnte Zeile. Sie steckt noch in zwei Plugins, die aus
# der Gemeinschaft kommen; die offiziellen @capacitor/... haben sie laengst
# umgestellt. Stand 18.09.2026 gibt es dort keine neuere Fassung - admob ist
# bei 8.1.0, speech-recognition bei 7.0.1, beide die jeweils neuesten.
PROGUARD_ALT = "getDefaultProguardFile('proguard-android.txt')"
PROGUARD_NEU = "getDefaultProguardFile('proguard-android-optimize.txt')"


def plugins_flicken():
    """Macht die Capacitor-Plugins vertraeglich mit dem Gradle-Plugin 9.

    AGP 9 nimmt `proguard-android.txt` nicht mehr an, weil darin
    `-dontoptimize` steht. Wer die Zeile noch benutzt, laesst den ganzen Bau
    scheitern - und zwar beim Auswerten des Plugins, also bevor irgendetwas
    anderes passiert. Das eigene app/build.gradle ist umgestellt, aber zwei
    Plugins liegen in node_modules und werden von jedem `npm install`
    ueberschrieben. Deshalb wird hier bei jedem Bau nachgesehen.

    Sobald die beiden Projekte nachgezogen haben, findet diese Funktion
    nichts mehr und kann weg.
    """
    import glob
    muster = [os.path.join(HUELLE, "node_modules", "*", "android", "build.gradle"),
              os.path.join(HUELLE, "node_modules", "*", "*", "android", "build.gradle")]
    geflickt = []
    for m in muster:
        for pfad in glob.glob(m):
            t = io.open(pfad, encoding="utf-8", newline="").read()
            if PROGUARD_ALT not in t:
                continue
            io.open(pfad, "w", encoding="utf-8", newline="").write(
                t.replace(PROGUARD_ALT, PROGUARD_NEU))
            geflickt.append(os.path.relpath(pfad, HUELLE))
    if geflickt:
        print("\nFuer das Gradle-Plugin 9 geflickt:")
        for g in geflickt:
            print("   " + g)
    return geflickt


def capacitor():
    print("\nCapacitor abgleichen ...")
    e = subprocess.run("npx cap sync android", cwd=HUELLE, shell=True)
    if e.returncode != 0:
        raise SystemExit("Capacitor meldet einen Fehler – siehe oben.")
    print("\nFertig. Jetzt in Android Studio öffnen:")
    print("   " + os.path.join(HUELLE, "android"))


def versionsnummer_hochzaehlen():
    """Zählt versionCode in app/build.gradle um eins hoch.

    Google Play nimmt jede Nummer nur EINMAL an – auch eine, die zu einem
    zurückgezogenen Paket gehörte. Wer das vergisst, merkt es erst beim
    Hochladen, und dann ist die Fassung schon gebaut.

    Hochgezählt wird bei jedem Bau, nicht nur vor dem Hochladen. Das lässt
    die Zahl schnell wachsen, aber das ist egal: Play verlangt nur, dass sie
    steigt, und bis 2.100.000.000 ist Platz. versionName bleibt von Hand –
    das ist die Nummer, die der Nutzer sieht.
    """
    pfad = os.path.join(HUELLE, "android", "app", "build.gradle")
    if not os.path.isfile(pfad):
        print("  build.gradle nicht gefunden – versionCode bleibt, wie er ist.")
        return
    text = io.open(pfad, encoding="utf-8", newline="").read()
    treffer = re.search(r"(versionCode\s+)(\d+)", text)
    if not treffer:
        print("  Kein versionCode in build.gradle gefunden.")
        return
    alt = int(treffer.group(2))
    neu = alt + 1
    text = text[:treffer.start()] + treffer.group(1) + str(neu) + text[treffer.end():]
    io.open(pfad, "w", encoding="utf-8", newline="").write(text)
    name = re.search(r'versionName\s+"([^"]+)"', text)
    print("  versionCode %d -> %d   (versionName %s, die bleibt von Hand)"
          % (alt, neu, name.group(1) if name else "?"))


def main():
    print("Tonspur prüfen ...")
    pruefen()
    print("\nInhalt kopieren ...")
    kopieren()
    print("\nVersionsnummer ...")
    versionsnummer_hochzaehlen()
    capacitor()
    # Nach dem Abgleich, nicht davor: `cap sync` kann node_modules anfassen.
    plugins_flicken()


if __name__ == "__main__":
    main()
