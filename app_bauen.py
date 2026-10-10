# -*- coding: utf-8 -*-
r"""
app_bauen.py  –  bringt den Inhalt in die Android-Hülle

Die Android-App liegt in einem eigenen Ordner neben diesem Projekt,
`zmaj-android` oder `zmaj-huelle` (frischer Klon von zmaj-lernapp/zmaj-huelle),
siehe huelle.py. Ein anderer Ort geht über die Umgebungsvariable ZMAJ_HUELLE.

Warum getrennt? Ursprünglich, weil dieser Ordner „Bosnisch Lernapp" heißt –
mit Leerzeichen, und Android-Builds stolpern darüber. Das Ausweichen
hat sich erledigt: beide liegen inzwischen unter „App Zeugs", und das
hat ebenfalls eins. Der Pfad zu gradlew.bat gehört deshalb in
Anführungszeichen, siehe gradle().

Dieses Skript kopiert web/ dorthin nach www/, ruft Capacitor auf und baut
das Paket zu Ende. Android Studio brauchst du dafür nicht mehr.

    app_bauen.py                 Abgleich + Debug-Paket zum Aufspielen aufs Handy
    app_bauen.py --aab           Abgleich + signiertes Paket für Google Play
    app_bauen.py --aab --testwerbung
                                 dasselbe mit Googles Testanzeigen – nur für
                                 den geschlossenen Test, nie für die Produktion
    app_bauen.py --aab --pflicht signiertes Paket als PFLICHT-Update:
                                 versionCode wird das nächste Vielfache von
                                 100, und wer es aus Google Play bekommt,
                                 kann die App erst nach dem Update weiter
                                 benutzen. Nur bei schweren Sicherheitslücken
                                 oder schweren Fehlern (Ajdin, 10.10.2026).
                                 Ein normaler Bau überspringt Vielfache von
                                 100, siehe naechste_versionsnummer()
    app_bauen.py --nur-abgleich  nur abgleichen, nichts bauen

Ein unbekannter oder vertippter Schalter bricht ab, bevor etwas passiert
(seit 10.10.2026, siehe schalter_lesen()).

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" app_bauen.py

Nicht mitkopiert werden: die Probeaufnahmen, die Sicherungen von index.html
und die LIESMICH-Dateien. Die gehören nicht in die App.

Liegt in der Hülle ein Ordner audio_emir/, kommen dessen Aufnahmen danach
über die Kopie in www/audio – die Stimme Emir für die Store-App. Sie liegen
nur dort und nie hier, siehe emir_drueber(). Seit 06.10.2026.
"""
import io
import json
import re
import os
import shutil
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HIER, "web")
sys.path.insert(0, HIER)
import huelle  # noqa: E402

HUELLE = huelle.ordner()   # ../zmaj-android oder ../zmaj-huelle, siehe huelle.py
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


# ------------------------------------------------------------ Stimme Emir ---
# Seit dem 06.10.2026 sprechen in der App aus dem Play Store alle Woerter und
# Saetze mit der Stimme Emir (ElevenLabs Voice Library, Modell eleven_v4).
# Die Geschichten g01-g12 behalten die Frauenstimme von Azure.
#
# Diese Aufnahmen duerfen NIE in dieses Repo. web/audio steht ueber
# REUSE.toml unter CC BY-SA und geht von hier in die Releases, die
# Anki-Pakete, die Demo auf GitHub Pages, nach Hugging Face und nach Zenodo.
# ElevenLabs verbietet, seine Ausgabe in einen Datensatz zu geben, mit dem
# sich KI trainieren laesst, und sie unter freieren Bedingungen
# weiterzugeben, als man sie selbst bekommen hat (Prohibited Use Policy,
# Punkt 9 (k), (l), (n)).
#
# Deshalb liegen sie nur in der privaten Huelle unter audio_emir/, und erst
# hier kommen sie ueber die KOPIE in www/audio. web/audio bleibt Azure.
# Fehlt der Ordner - frischer Klon dieses Repos, die Demo, jemand anderes
# baut -, aendert sich nichts.
EMIR = os.path.join(HUELLE, "audio_emir")
EMIR_DATEI = re.compile(r"w\d{4}\.mp3")


def _liegt_in(pfad, ordner):
    """Liegt `pfad` in `ordner` (oder ist es selbst)?"""
    pfad, ordner = (os.path.normcase(os.path.realpath(p)) for p in (pfad, ordner))
    try:
        return os.path.commonpath([pfad, ordner]) == ordner
    except ValueError:                      # verschiedene Laufwerke
        return False


TESTWERBUNG_AUS = "const ADMOB_TEST = false;"
TESTWERBUNG_AN = "const ADMOB_TEST = true;"


def testwerbung_einschalten(pfad=None):
    """Schaltet in der KOPIE www/index.html auf Googles Testanzeigen um.

    Fuer Pakete, die in den geschlossenen Test gehen. Seit admob_scharf.py
    stehen in web/index.html die echten Kennungen, und ein Tester, der aus
    Hilfsbereitschaft eine echte Anzeige antippt, erzeugt ungueltigen
    Traffic auf dem AdMob-Konto. Mit ADMOB_TEST = true nimmt das Plugin
    Googles Test-Anzeigenbloecke. Die Quelle bleibt unberuehrt; ein Paket
    fuer die Produktion entsteht ohne --testwerbung. Google hat den ersten
    Antrag auf Produktionszugriff am 09.10.2026 abgelehnt, auch weil
    waehrend des Tests kein Update kam - fuer diese Updates ist der
    Schalter da.
    """
    pfad = pfad or os.path.join(WWW, "index.html")
    with io.open(pfad, encoding="utf-8", newline="") as f:
        text = f.read()
    if text.count(TESTWERBUNG_AUS) != 1:
        raise SystemExit("ABBRUCH: '%s' steht nicht genau einmal in %s - "
                         "Testwerbung laesst sich nicht sicher einschalten."
                         % (TESTWERBUNG_AUS, pfad))
    with io.open(pfad, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace(TESTWERBUNG_AUS, TESTWERBUNG_AN))
    print("\nTESTWERBUNG: ADMOB_TEST = true im Paket. Nur fuer den "
          "geschlossenen Test hochladen, NICHT in die Produktion.")


def emir_drueber():
    """Legt die Emir-Aufnahmen ueber die kopierte Tonspur in www/audio.

    Getauscht wird nur, was gleich heisst und in index.json steht - eine
    Datei ohne Eintrag spielte die App nie ab. In der KOPIE von index.json
    steht danach bei diesen Eintraegen "stimme": "emir". Die App selbst
    liest das Feld nicht (sie nimmt nur key und datei); es steht dort fuer
    den, der das Paket aufmacht und wissen will, welche Stimme drin ist.

    Gibt die Zahl der getauschten Dateien zurueck.
    """
    if not os.path.isdir(EMIR):
        print("\nKein audio_emir/ in der Huelle - die Tonspur bleibt Azure.")
        return 0
    audio = os.path.join(WWW, "audio")
    # Nie ins oeffentliche web/ schreiben - auch dann nicht, wenn ZMAJ_HUELLE
    # aus Versehen auf dieses Projekt zeigt. Dann lieber gar kein Paket.
    if _liegt_in(audio, WEB):
        raise SystemExit("\nABBRUCH: %s liegt in web/. Emir darf nie dorthin." % audio)
    from ton_pruefen import MINDEST         # dieselbe Grenze fuer "stumm"
    index_pfad = os.path.join(audio, "index.json")
    index = json.load(io.open(index_pfad, encoding="utf-8"))
    eintraege = {e["datei"]: e for e in index.get("toene", [])}

    getauscht, fremd, stumm = 0, [], []
    for name in sorted(os.listdir(EMIR)):
        if not EMIR_DATEI.fullmatch(name):
            continue                        # LIESMICH.txt und was sonst dort liegt
        quelle = os.path.join(EMIR, name)
        if name not in eintraege or not os.path.isfile(os.path.join(audio, name)):
            fremd.append(name)
            continue
        if os.path.getsize(quelle) < MINDEST:
            stumm.append(name)
            continue
        shutil.copyfile(quelle, os.path.join(audio, name))
        eintraege[name]["stimme"] = "emir"
        getauscht += 1
    io.open(index_pfad, "w", encoding="utf-8").write(
        json.dumps(index, ensure_ascii=False, indent=1))

    def liste(namen):
        return ", ".join(namen[:10]) + (" ..." if len(namen) > 10 else "")

    azure = sorted(d for d, e in eintraege.items()
                   if EMIR_DATEI.fullmatch(d) and e.get("stimme") != "emir")
    geschichten = sum(1 for d in eintraege if not EMIR_DATEI.fullmatch(d))
    print("\nStimme Emir: %d Aufnahmen aus audio_emir/ ueber www/audio gelegt."
          % getauscht)
    print("   Geschichten bleiben bei Azure: %d" % geschichten)
    if azure:
        print("   Woerter ohne Emir, bleiben Azure: %d  (%s)" % (len(azure), liste(azure)))
    if fremd:
        print("   WARNUNG: steht in keinem Index, nicht kopiert: %s" % liste(fremd))
    if stumm:
        print("   WARNUNG: kleiner als %d Byte, nicht kopiert: %s" % (MINDEST, liste(stumm)))
    if not getauscht:
        print("   WARNUNG: audio_emir/ ist da, aber nichts passte - das Paket spricht Azure.")
    return getauscht


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
    # Der Pfad MUSS in Anfuehrungszeichen stehen. Er enthaelt ein
    # Leerzeichen ("App Zeugs"), und ohne sie bricht cmd.exe ihn dort
    # auseinander und sucht ein Programm namens ...\Desktop\App.
    # Am 26.09.2026 genau daran gescheitert: Gradle meldete einen Fehler,
    # ohne eine einzige Zeile auszugeben.
    e = subprocess.run('"%s" %s' % (os.path.join(ANDROID, "gradlew.bat"), ziel),
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


# ------------------------------------------------------- Pflicht-Updates ---
# Seit dem 10.10.2026 holt die App Updates selbst ueber Google Play (Plugin
# ZmajUpdate in der Huelle). Normal kommen sie SANFT: Google fragt, laedt im
# Hintergrund, man lernt weiter. PFLICHT - die App geht erst nach dem Update
# weiter - ist ein Update, wenn Google die Prioritaet 4 oder 5 meldet ODER
# sein versionCode ein Vielfaches von 100 ist. Die Prioritaet laesst sich nur
# ueber die Play Developer API setzen, nicht in der Play Console; die Nummer
# setzt dieses Skript mit --pflicht. Pflicht nur bei schweren
# Sicherheitsluecken oder schweren Fehlern (Ajdin, 10.10.2026).
#
# Daraus folgt die andere Haelfte der Regel: Ein NORMALER Bau darf nie auf
# einem Vielfachen von 100 landen. Weil jeder Bau hochzaehlt, kaeme der
# Zaehler sonst alle hundert Bauten von allein dort an, und ein ganz
# gewoehnliches Update waere fuer alle Pflicht.
PFLICHT_SCHRITT = 100
# Der hoechste versionCode, den Google Play annimmt.
HOECHSTE_VERSIONSNUMMER = 2100000000
SCHALTER = ("--aab", "--testwerbung", "--pflicht", "--nur-abgleich")


def schalter_lesen(argv):
    """Gibt die Schalter als Menge zurück und bricht bei einem unbekannten ab.

    Bis zum 10.10.2026 ging ein vertippter Schalter stillschweigend unter.
    Bei --pflicht wäre das gefährlich: Aus "--plicht" würde ein sanftes
    Update, obwohl eine schwere Lücke sofort geschlossen werden soll. Dann
    lieber gar kein Paket.
    """
    unbekannt = [a for a in argv if a not in SCHALTER]
    if unbekannt:
        raise SystemExit("ABBRUCH: unbekannter Schalter %s - erlaubt sind %s. "
                         "Nichts gebaut." % (", ".join(unbekannt), " ".join(SCHALTER)))
    schalter = set(argv)
    if "--pflicht" in schalter and "--nur-abgleich" in schalter:
        raise SystemExit("ABBRUCH: --pflicht setzt den versionCode, --nur-abgleich "
                         "zählt ihn nicht hoch. Zusammen gäbe das kein Pflicht-Update.")
    return schalter


def naechste_versionsnummer(aktuell, pflicht=False):
    """Der versionCode nach `aktuell`, nach der Regel oben.

    Normal: eins weiter, aber nie ein Vielfaches von 100 - dann noch eins
    (99 -> 101). Pflicht: das nächste Vielfache von 100, das größer ist als
    `aktuell`, auch wenn `aktuell` selbst schon eins ist (100 -> 200), denn
    Play nimmt jede Nummer nur einmal.

    Ohne Datei, damit die Regel für sich getestet ist (tests/test_huelle.py).
    """
    if isinstance(aktuell, bool) or not isinstance(aktuell, int) or aktuell < 0:
        raise ValueError("versionCode muss eine ganze Zahl ab 0 sein, nicht %r" % (aktuell,))
    if pflicht:
        neu = (aktuell // PFLICHT_SCHRITT + 1) * PFLICHT_SCHRITT
    else:
        neu = aktuell + 1
        if neu % PFLICHT_SCHRITT == 0:
            neu += 1
    if neu > HOECHSTE_VERSIONSNUMMER:
        raise ValueError("versionCode %d liegt über Googles Grenze %d"
                         % (neu, HOECHSTE_VERSIONSNUMMER))
    return neu


def pflicht_melden(nummer):
    """Unübersehbar - beim Hochzählen und noch einmal ganz am Ende."""
    print("\n" + "!" * 64)
    print("  PFLICHT-UPDATE: versionCode %d" % nummer)
    print("  Wer es aus Google Play bekommt, kann die App erst nach dem")
    print("  Update weiter benutzen. Nur bei schweren Sicherheitslücken")
    print("  oder schweren Fehlern hochladen.")
    print("!" * 64)


def versionsnummer_hochzaehlen(pflicht=False, pfad=None):
    """Zählt versionCode in app/build.gradle hoch, nach naechste_versionsnummer().

    Google Play nimmt jede Nummer nur EINMAL an – auch eine, die zu einem
    zurückgezogenen Paket gehörte. Wer das vergisst, merkt es erst beim
    Hochladen, und dann ist die Fassung schon gebaut.

    Hochgezählt wird bei jedem Bau, nicht nur vor dem Hochladen. Das lässt
    die Zahl schnell wachsen, aber das ist egal: Play verlangt nur, dass sie
    steigt, und bis 2.100.000.000 ist Platz. versionName bleibt von Hand –
    das ist die Nummer, die der Nutzer sieht.

    Mit pflicht=True (--pflicht) springt die Nummer auf das nächste
    Vielfache von 100 – daran erkennt die App das Pflicht-Update. Fehlt dann
    build.gradle oder der versionCode darin, bricht der Bau ab: Ein Paket,
    das man für Pflicht hält und das keins ist, wäre schlimmer als gar
    keins. 10.10.2026.

    Gibt die neue Nummer zurück, None wenn nichts geändert wurde. `pfad` ist
    für die Tests, sonst die build.gradle der Hülle.
    """
    pfad = pfad or os.path.join(HUELLE, "android", "app", "build.gradle")
    if not os.path.isfile(pfad):
        if pflicht:
            raise SystemExit("ABBRUCH: build.gradle nicht gefunden (%s) - ohne "
                             "versionCode gibt es kein Pflicht-Update." % pfad)
        print("  build.gradle nicht gefunden – versionCode bleibt, wie er ist.")
        return None
    text = io.open(pfad, encoding="utf-8", newline="").read()
    treffer = re.search(r"(versionCode\s+)(\d+)", text)
    if not treffer:
        if pflicht:
            raise SystemExit("ABBRUCH: Kein versionCode in %s - ohne ihn gibt es "
                             "kein Pflicht-Update." % pfad)
        print("  Kein versionCode in build.gradle gefunden.")
        return None
    alt = int(treffer.group(2))
    try:
        neu = naechste_versionsnummer(alt, pflicht)
    except ValueError as fehler:
        raise SystemExit("ABBRUCH: %s" % fehler)
    text = text[:treffer.start()] + treffer.group(1) + str(neu) + text[treffer.end():]
    io.open(pfad, "w", encoding="utf-8", newline="").write(text)
    name = re.search(r'versionName\s+"([^"]+)"', text)
    print("  versionCode %d -> %d   (versionName %s, die bleibt von Hand)"
          % (alt, neu, name.group(1) if name else "?"))
    if pflicht:
        pflicht_melden(neu)
    elif neu != alt + 1:
        print("  %d übersprungen: Vielfache von %d sind Pflicht-Updates."
              % (alt + 1, PFLICHT_SCHRITT))
    return neu


def main(argv=None):
    # Erst die Schalter, dann alles andere: Ein vertippter Schalter oder
    # --pflicht mit --nur-abgleich bricht ab, bevor irgendetwas kopiert oder
    # hochgezaehlt ist. 10.10.2026.
    schalter = schalter_lesen(sys.argv[1:] if argv is None else argv)
    aab = "--aab" in schalter
    nur = "--nur-abgleich" in schalter
    pflicht = "--pflicht" in schalter
    if pflicht:
        print("PFLICHT-UPDATE (--pflicht): versionCode wird das nächste "
              "Vielfache von %d.\n" % PFLICHT_SCHRITT)
    print("Tonspur prüfen ...")
    pruefen()
    print("\nInhalt kopieren ...")
    kopieren()
    # Gleich nach dem Kopieren und VOR capacitor(): `cap sync` traegt www/
    # nach android/app/src/main/assets/public, und nur was dann in www/
    # liegt, kommt ins Paket. Hier, vor der Weiche, gilt es fuer das
    # Debug-Paket, fuer --aab und fuer --nur-abgleich gleich. 06.10.2026.
    emir_drueber()
    if "--testwerbung" in schalter:
        testwerbung_einschalten()
    # Nur hochzaehlen, wenn auch gebaut wird. --nur-abgleich hat sonst
    # Nummern verbrannt, ohne dass ein Paket entstand.
    nummer = None
    if not nur:
        print("\nVersionsnummer ...")
        nummer = versionsnummer_hochzaehlen(pflicht)
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
    if pflicht:
        # Noch einmal ganz unten: Gradle schreibt Hunderte Zeilen, und die
        # Meldung vom Hochzaehlen steht dann weit oben. 10.10.2026.
        pflicht_melden(nummer)
        if not aab:
            print("  Das ist das Debug-Paket. In-App-Updates gibt es nur, wenn die")
            print("  App aus Google Play kommt; für den Store: --aab --pflicht.")


if __name__ == "__main__":
    main()
