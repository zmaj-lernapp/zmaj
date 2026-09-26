# -*- coding: utf-8 -*-
r"""
app_bauen.py  –  bringt den Inhalt in die Android-Hülle

Die Android-App liegt in einem eigenen Ordner neben diesem Projekt:

    C:\Users\Ajdin\Desktop\zmaj-android

Warum getrennt? Weil dieser Ordner „Bosnisch Lernapp" heißt – mit Leerzeichen.
Android-Builds stolpern darüber. Der Nachbarordner hat keins.

Dieses Skript kopiert web/ dorthin nach www/, ruft Capacitor auf und baut
das Paket zu Ende. Android Studio brauchst du dafür nicht mehr.

    app_bauen.py                 Abgleich + Debug-Paket zum Aufspielen aufs Handy
    app_bauen.py --aab           Abgleich + signiertes Paket für Google Play
    app_bauen.py --nur-abgleich  nur abgleichen, nichts bauen

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
ANDROID = os.path.join(HUELLE, "android")
# Hier stehen Pfad und Passwoerter des Freigabeschluessels. Die Datei gehoert
# NICHT in eine Sicherung, die den Rechner verlaesst.
SIGNATUR = os.path.join(ANDROID, "keystore.properties")

# Was in der App nichts verloren hat
RAUS_ORDNER = {"_probe"}
RAUS_DATEIEN = {"liesmich.txt"}
RAUS_ENDUNGEN = (".sicherung", ".bak", ".orig", ".alt")
# Sicherungen heissen index.html.vor_audio, .vor_lokal, .vor_sicherung und so
# weiter - eine feste Liste vergisst man beim naechsten Umbau. Deshalb ein
# Muster statt Aufzaehlung.
RAUS_ENTHAELT = (".vor_",)
# Werkstattmaterial faengt mit einem Unterstrich an: web/_feature.html
# zeichnet die Bannergrafik fuer den Play-Eintrag, web/_probe und
# audio/_probe sind Probeseiten. Nichts davon gehoert in die App. Ein
# Praefix statt einer Liste - sonst wandert die naechste solche Datei
# wieder mit, so wie _feature.html es bis zum 20.09.2026 getan hat.
RAUS_PRAEFIX = "_"


def kopieren():
    if not os.path.isdir(HUELLE):
        raise SystemExit("Die Android-Hülle fehlt: %s" % HUELLE)
    shutil.rmtree(WWW, ignore_errors=True)
    dateien = 0
    for wurzel, ordner, namen in os.walk(WEB):
        ordner[:] = [o for o in ordner
                     if o not in RAUS_ORDNER and not o.startswith(RAUS_PRAEFIX)]
        ziel = os.path.join(WWW, os.path.relpath(wurzel, WEB))
        os.makedirs(ziel, exist_ok=True)
        for n in namen:
            klein = n.lower()
            if (klein in RAUS_DATEIEN or klein.endswith(RAUS_ENDUNGEN)
                    or klein.startswith(RAUS_PRAEFIX)
                    or any(s in klein for s in RAUS_ENTHAELT)):
                continue
            shutil.copy2(os.path.join(wurzel, n), os.path.join(ziel, n))
            dateien += 1
    groesse = sum(os.path.getsize(os.path.join(w, n))
                  for w, _, ns in os.walk(WWW) for n in ns)
    print("%d Dateien kopiert, %.1f MB" % (dateien, groesse / 1048576.0))
    return dateien


# Aus diesen Dateien baut inhalt_bauen.py die JSON-Dateien für das Handy.
# Ändert sich eine davon, sind die JSON-Dateien veraltet.
INHALT_QUELLEN = ["sprachen.py", "vokabeln.py", "geschichten.py",
                  "grammatik.py", "uebersetzungen.py"]


def inhalt_aktuell():
    """Sind web/inhalt/*.json neuer als die Python-Dateien, aus denen sie kommen?

    Am 26.09.2026 stand in den Einstellungen wörtlich „set.sicherung_suchen"
    statt des Satzes. Ursache: sicherung_richten.py hatte sprachen.py geändert,
    aber niemand hatte inhalt_bauen.py laufen lassen. Das Handy liest die
    Texte ausschließlich aus web/inhalt/<sprache>.json, nie aus sprachen.py.
    Am PC fällt das nie auf, weil der Server die Python-Dateien frisch liest.
    """
    ordner = os.path.join(HIER, "web", "inhalt")
    if not os.path.isdir(ordner):
        return ["web/inhalt fehlt ganz"]
    gebaut = [os.path.join(ordner, d) for d in os.listdir(ordner)
              if d.endswith(".json")]
    if not gebaut:
        return ["in web/inhalt liegt keine JSON-Datei"]
    juengste = min(os.path.getmtime(d) for d in gebaut)
    veraltet = []
    for quelle in INHALT_QUELLEN:
        pfad = os.path.join(HIER, quelle)
        if os.path.exists(pfad) and os.path.getmtime(pfad) > juengste:
            veraltet.append(quelle)
    return veraltet


def pruefen():
    """Kein halbes Paket ausliefern: Tonspur vollständig, Texte aktuell."""
    sys.path.insert(0, HIER)
    import ton_pruefen
    if ton_pruefen.main() != 0:
        raise SystemExit("\nABBRUCH: Die Tonspur ist unvollständig. Nichts kopiert.")

    veraltet = inhalt_aktuell()
    if veraltet:
        print("\nABBRUCH: web/inhalt ist älter als %s." % ", ".join(veraltet))
        print("Das Handy würde die alten Texte anzeigen, am PC sähe alles richtig aus.")
        print("\nErst das hier laufen lassen, dann noch einmal bauen:")
        print('    "%s" inhalt_bauen.py' % sys.executable)
        raise SystemExit(1)

    import texte_pruefen
    if texte_pruefen.main() != 0:
        raise SystemExit("\nABBRUCH: Es fehlen Texte. Nichts kopiert.")


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


JAVA_ORTE = [
    r"C:\Program Files\Android\Android Studio\jbr",
    r"C:\Program Files\Android\Android Studio\jre",
    r"C:\Program Files\Java",
]


def java_finden():
    """Sucht ein Java für Gradle.

    Gradle bringt keins mit und findet von sich aus keins: JAVA_HOME ist auf
    diesem Rechner nicht gesetzt, und `java` steht nicht im Pfad. Android
    Studio bringt aber eins mit, und genau das ist auch das richtige – es
    passt zur Android-Werkzeugkette.
    """
    if os.environ.get("JAVA_HOME") and os.path.isfile(
            os.path.join(os.environ["JAVA_HOME"], "bin", "java.exe")):
        return os.environ["JAVA_HOME"]
    for ort in JAVA_ORTE:
        if os.path.isfile(os.path.join(ort, "bin", "java.exe")):
            return ort
        if os.path.isdir(ort):                      # Program Files\Java: Unterordner
            for name in sorted(os.listdir(ort), reverse=True):
                tief = os.path.join(ort, name)
                if os.path.isfile(os.path.join(tief, "bin", "java.exe")):
                    return tief
    return None


def gradle(ziel, was):
    """Ruft Gradle auf und gibt zurück, ob es geklappt hat."""
    heim = java_finden()
    if not heim:
        print("\nKein Java gefunden. Gradle braucht eins – normalerweise das")
        print("von Android Studio unter:")
        print("   " + JAVA_ORTE[0])
        print("Ohne das geht der Bau nur in Android Studio selbst.")
        return None
    umgebung = dict(os.environ, JAVA_HOME=heim)
    print("\n%s ...   (Java: %s)" % (was, heim))
    e = subprocess.run(os.path.join(ANDROID, "gradlew.bat") + " " + ziel,
                       cwd=ANDROID, shell=True, env=umgebung)
    if e.returncode != 0:
        raise SystemExit("Gradle meldet einen Fehler – siehe oben.")
    return True


def zeigen(pfad, was):
    if os.path.isfile(pfad):
        print("\n%s: %s" % (was, pfad))
        print("   %.1f MB" % (os.path.getsize(pfad) / 1048576.0))
    else:
        print("\n%s wurde nicht gefunden: %s" % (was, pfad))


def debug_apk():
    if gradle("assembleDebug", "Debug-Paket bauen"):
        zeigen(os.path.join(ANDROID, "app", "build", "outputs", "apk",
                            "debug", "app-debug.apk"), "APK fürs Handy")


def freigabe_aab():
    """Baut das signierte Paket für Google Play."""
    if not os.path.isfile(SIGNATUR):
        print("\nEs fehlt die Datei mit den Zugangsdaten zum Schlüssel:")
        print("   " + SIGNATUR)
        print("Ohne sie wäre das Paket unsigniert, und Play nimmt es nicht an.")
        print("Vorlage: keystore.properties.beispiel im selben Ordner.")
        raise SystemExit(1)
    if gradle("bundleRelease", "Signiertes Paket für Play bauen"):
        zeigen(os.path.join(ANDROID, "app", "build", "outputs", "bundle",
                            "release", "app-release.aab"), "AAB für Play")
        print("\nHochladen in der Play Console unter Release > Testen oder Produktion.")
        print("Google signiert beim Hochladen noch einmal selbst (Play App Signing);")
        print("dein Schlüssel ist der Upload-Schlüssel.")


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
    aab = "--aab" in sys.argv
    nur = "--nur-abgleich" in sys.argv
    print("Tonspur prüfen ...")
    pruefen()
    print("\nInhalt kopieren ...")
    kopieren()
    print("\nVersionsnummer ...")
    versionsnummer_hochzaehlen()
    capacitor()
    # Nach dem Abgleich, nicht davor: `cap sync` kann node_modules anfassen.
    plugins_flicken()
    if nur:
        print("\nAbgeglichen. Gebaut wird nichts (--nur-abgleich).")
        print("   " + ANDROID)
        return
    if aab:
        freigabe_aab()
    else:
        debug_apk()


if __name__ == "__main__":
    main()
