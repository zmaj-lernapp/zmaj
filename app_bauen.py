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
    for zeile in maskottchen_groessen(os.path.join(WWW, "maskottchen")):
        print("   " + zeile)
    return dateien


def _ordner_groesse(ordner):
    return sum(os.path.getsize(os.path.join(w, n)) for w, _, ns in os.walk(ordner) for n in ns)


def maskottchen_groessen(ordner):
    """Wie viel der Drache im Paket wiegt. Seit dem 15.10.2026 ist er aus
    Bildern (teile/ und je Hautfarbe haut/<farbe>/, siehe zmaj_lottie.py und
    haut_einbauen.py); das ist der groesste Brocken nach der Tonspur, darum
    steht es beim Bauen da. Beide Ordner kommen ueber kopieren() mit - sie
    fangen nicht mit "_" an und stehen in keiner Ausschlussliste."""
    if not os.path.isdir(ordner):
        return ["maskottchen/ fehlt"]
    zeilen = ["maskottchen/ %.2f MB, davon teile/ %d KB" % (_ordner_groesse(ordner) / 1048576.0,
                                                          _ordner_groesse(os.path.join(ordner, "teile")) // 1024)]
    haut = os.path.join(ordner, "haut")
    if os.path.isdir(haut):
        farben = sorted(f for f in os.listdir(haut) if os.path.isdir(os.path.join(haut, f)))
        zeilen.append("haut/ %d KB: %s" % (_ordner_groesse(haut) // 1024, ", ".join(
            "%s %d KB" % (f, _ordner_groesse(os.path.join(haut, f)) // 1024) for f in farben)))
    # Seit 16.10.2026 die gemalten Kostueme (zierrat/<stueck>/, siehe GEMALT
    # in zmaj_lottie.py). Auch sie kommen ueber kopieren() mit; die App
    # laedt sie nur, wenn das Stueck getragen wird.
    zierrat = os.path.join(ordner, "zierrat")
    if os.path.isdir(zierrat):
        stuecke = sorted(f for f in os.listdir(zierrat) if os.path.isdir(os.path.join(zierrat, f)))
        zeilen.append("zierrat/ %d KB: %d Stuecke, das groesste %s" % (
            _ordner_groesse(zierrat) // 1024, len(stuecke),
            max(("%s %d KB" % (f, _ordner_groesse(os.path.join(zierrat, f)) // 1024) for f in stuecke),
                key=lambda z: int(z.split()[-2])) if stuecke else "-"))
    return zeilen


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


DAUER_PLATZHALTER = "const DAUER_PRUEFWERT = '__DAUER_PRUEFWERT__';"
DAUER_DATEI = os.path.join(HUELLE, "dauer_pruefwert.txt")


def dauer_einsetzen(pfad=None, datei=None):
    """Setzt in der KOPIE www/index.html den Pruefwert des Dauer-Worts ein.

    Das Wort fuer die versteckte Dauer-Vollversion (Ajdin und Kuebra) stand
    bis 11.10.2026 im Klartext in web/index.html und damit im oeffentlichen
    Repository. Jetzt steht dort nur ein Platzhalter; der Pruefwert liegt in
    der privaten Huelle (dauer_wort_setzen.py legt ihn an). Fehlt er, bricht
    der Bau ab - sonst kaeme eine App heraus, in der der Schalter still
    nicht mehr geht.
    """
    pfad = pfad or os.path.join(WWW, "index.html")
    datei = datei or DAUER_DATEI
    if not os.path.exists(datei):
        raise SystemExit("ABBRUCH: %s fehlt. Erst dauer_wort_setzen.py in Thonny "
                         "laufen lassen und das Wort festlegen." % datei)
    with io.open(datei, encoding="utf-8") as f:
        wert = f.read().strip()
    if not re.fullmatch(r"[0-9a-f]{64}", wert):
        raise SystemExit("ABBRUCH: %s enthaelt keinen Pruefwert (64 Hex-Zeichen)." % datei)
    with io.open(pfad, encoding="utf-8", newline="") as f:
        text = f.read()
    if text.count(DAUER_PLATZHALTER) != 1:
        raise SystemExit("ABBRUCH: '%s' steht nicht genau einmal in %s."
                         % (DAUER_PLATZHALTER, pfad))
    with io.open(pfad, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace(DAUER_PLATZHALTER,
                             DAUER_PLATZHALTER.replace("__DAUER_PRUEFWERT__", wert)))


# Cloud-Sicherung (19.10.2026): vorbereitet, aber aus (CLOUD_AN = false in
# web/index.html), eingeschaltet wird erst nach dem Produktionsstart.
# Projekt-ID und Web-API-Schluessel von Firebase stehen nie im oeffentlichen
# Repository, sondern in der privaten Huelle (cloud_zugang.json, Aufbau in
# FIREBASE_EINRICHTEN.md), und kommen wie der Dauer-Pruefwert nur in die
# KOPIE www/index.html.
CLOUD_PLATZHALTER = {
    "projekt": "const CLOUD_PROJEKT = '__CLOUD_PROJEKT__';",
    "schluessel": "const CLOUD_SCHLUESSEL = '__CLOUD_SCHLUESSEL__';",
}
# Dieselben Muster prueft cloudEingerichtet() in der App.
CLOUD_MUSTER = {
    "projekt": r"[a-z][a-z0-9-]{4,28}[a-z0-9]",
    "schluessel": r"AIza[0-9A-Za-z_-]{35}",
}
CLOUD_SCHALTER_AN = "const CLOUD_AN = true;"
CLOUD_DATEI = os.path.join(HUELLE, "cloud_zugang.json")


def cloud_einsetzen(pfad=None, datei=None):
    """Setzt in der KOPIE www/index.html Projekt-ID und Schluessel ein.

    Fehlt cloud_zugang.json, bleiben die Platzhalter stehen; die App findet
    dann keinen Adapter, und die Cloud bleibt aus. Das ist bis zum
    Produktionsstart der Normalfall. Steht CLOUD_AN aber auf true, bricht
    der Bau ohne Datei ab - sonst kaeme eine App heraus, die still nichts
    sichert. Die Werte selbst erscheinen in keiner Meldung.
    Gibt zurueck, ob eingesetzt wurde.
    """
    pfad = pfad or os.path.join(WWW, "index.html")
    datei = datei or CLOUD_DATEI
    with io.open(pfad, encoding="utf-8", newline="") as f:
        text = f.read()
    for platzhalter in CLOUD_PLATZHALTER.values():
        if text.count(platzhalter) != 1:
            raise SystemExit("ABBRUCH: '%s' steht nicht genau einmal in %s."
                             % (platzhalter, pfad))
    if not os.path.exists(datei):
        if CLOUD_SCHALTER_AN in text:
            raise SystemExit("ABBRUCH: CLOUD_AN steht auf true, aber %s fehlt "
                             "(siehe FIREBASE_EINRICHTEN.md)." % datei)
        print("  Cloud-Sicherung: keine cloud_zugang.json - sie bleibt aus.")
        return False
    with io.open(datei, encoding="utf-8") as f:
        try:
            werte = json.load(f)
        except ValueError:
            raise SystemExit("ABBRUCH: %s ist kein gueltiges JSON." % datei)
    for name, muster in CLOUD_MUSTER.items():
        wert = werte.get(name) if isinstance(werte, dict) else None
        if not isinstance(wert, str) or not re.fullmatch(muster, wert):
            raise SystemExit("ABBRUCH: In %s fehlt '%s' oder hat nicht die "
                             "erwartete Form." % (datei, name))
        platzhalter = CLOUD_PLATZHALTER[name]
        text = text.replace(platzhalter, platzhalter.replace("__CLOUD_%s__" % name.upper(), wert))
    with io.open(pfad, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("  Cloud-Sicherung: Projekt und Schluessel eingesetzt.")
    return True


# Tonspur im Paket als Opus statt MP3 (12.10.2026). Die 2.332 MP3s mit
# 48 kbit/s machten 17,5 von 25,3 MB des AAB aus; Opus mit 24 kbit/s klingt
# bei Sprache mindestens gleich gut und ist halb so gross. Nur die Kopie in
# www/audio wird umgewandelt - web/audio bleibt MP3 fuer Web-Demo,
# Datensatz und Anki. Der Zwischenspeicher in der Huelle haelt jede
# umgewandelte Datei unter dem Hash ihrer MP3, damit nicht jeder Bau alle
# Dateien neu durch ffmpeg schickt.
FFMPEG = os.path.join(os.path.dirname(HUELLE), "werkzeuge", "ffmpeg", "bin", "ffmpeg.exe")
TON_ZWISCHENSPEICHER = os.path.join(HUELLE, ".ton_opus")
TON_BITRATE = "24k"

# Stille am Anfang kuerzen (22.10.2026). Ajdin: "der sprecher sagt viel zu
# spaet die woerter oder saetze die muessen frueher kommen man wartet zu
# lange bis er anfaengt". Gemessen lagen vor dem ersten Laut einer
# Emir-Aufnahme im Median 188 ms Stille (bis 270 ms): 36 ms bringt
# ElevenLabs mit, 150 ms setzt emir_lauf.py mit adelay davor. Die
# Azure-Aufnahmen haben rund 240 ms. Das wartet man bei jedem Wort ab,
# auch beim Antippen.
# silenceremove nimmt nur die Stille VOR dem ersten Laut (start_periods=1)
# und laesst davon 30 ms stehen (start_silence): Vorlauf fuer Handys und
# Bluetooth-Kopfhoerer, die den Anfang der Ausgabe verschlucken. Als Laut
# zaehlt schon, was in einem 1-ms-Fenster ueber -65 dB ausschlaegt (Spitze,
# nicht Mittel) - also auch der leise Hauch, mit dem ein h oder f beginnt.
# Erst stand hier -55 dB; das nahm bei 13 der 2.399 Emir-Aufnahmen etwas
# zwischen -65 und -55 dB mit, bei "hoću" 32 ms vom Anhauchen. Mit -65 dB
# geht in keiner Aufnahme etwas ueber -65 dB verloren, und gespart werden
# trotzdem im Median 151 ms (mit -55 dB: 155 ms). Nachgemessen am
# 22.10.2026 an allen Aufnahmen, Quelle gegen Ergebnis.
# Die Azure-Aufnahmen rauschen vor dem Wort bei -60 bis -66 dB. Dort greift
# die Kante also oft schon am Rauschen, und es wird weniger gekuerzt (im
# Median 112 ms) - lieber das als ein Stueck vom Laut. Das betrifft im
# Paket nur die zwei Goran-Woerter ohne Emir und wer ohne audio_emir baut.
# Das Ende bleibt unberuehrt: der Nachlauf kam am 06.10.2026 gegen
# abgeschnittene Wortenden hinein.
# Nur Woerter und Saetze (w####.mp3, wie EMIR_DATEI). Die Geschichten
# nicht: ihre Wortzeiten "w" in index.json zaehlen ab Dateianfang, das
# Mitlesen liefe sonst um den geschnittenen Betrag hinterher.
# web/audio bleibt, wie es ist (Web-Demo, Datensatz, Anki) - gekuerzt wird
# nur beim Umwandeln der Kopie. Der Filter steckt im Schluessel des
# Zwischenspeichers (ton_schluessel()): sonst kaemen aus .ton_opus die
# alten, ungekuerzten Dateien, und eine Aenderung am Filter wandelt neu um.
TON_ANFANG = ("silenceremove=start_periods=1:start_threshold=-65dB:start_silence=0.03"
              ":detection=peak:window=0.001")


def ton_filter(name):
    """Der ffmpeg-Filter fuer diese Datei: TON_ANFANG fuer Woerter und
    Saetze, None fuer die Geschichten."""
    return TON_ANFANG if EMIR_DATEI.fullmatch(name) else None


def ton_schluessel(inhalt_hash, name):
    """Name im Zwischenspeicher: Inhalt und Bitrate, bei gekuerzten Dateien
    dazu ein Kennzeichen des Filters ("-a" und 8 Zeichen seines Hashes)."""
    import hashlib
    s = inhalt_hash[:32] + "-" + TON_BITRATE
    f = ton_filter(name)
    if f:
        s += "-a" + hashlib.sha256(f.encode("ascii")).hexdigest()[:8]
    return s


def ton_index_umschreiben(index):
    """Ersetzt in index.json jede Endung .mp3 durch .ogg. Gibt die Zahl zurueck."""
    n = 0
    for e in index.get("toene", []):
        d = e.get("datei", "")
        if d.lower().endswith(".mp3"):
            e["datei"] = d[:-4] + ".ogg"
            n += 1
    return n


def ton_verkleinern(audio=None, ffmpeg=None, zwischen=None):
    """Wandelt www/audio/*.mp3 in Ogg/Opus um und passt index.json an.

    Ohne ffmpeg bleibt die Tonspur MP3 (mit Hinweis) - die App spielt beides.
    Gibt (vorher, nachher) in Bytes zurueck.
    """
    import hashlib
    from concurrent.futures import ThreadPoolExecutor
    audio = audio or os.path.join(WWW, "audio")
    ffmpeg = ffmpeg or os.environ.get("ZMAJ_FFMPEG") or FFMPEG
    zwischen = zwischen or TON_ZWISCHENSPEICHER
    if _liegt_in(audio, WEB):
        raise SystemExit("\nABBRUCH: %s liegt in web/. Umgewandelt wird nur die Kopie." % audio)
    if not os.path.isfile(ffmpeg):
        print("\nHINWEIS: ffmpeg fehlt (%s) - die Tonspur bleibt MP3." % ffmpeg)
        return (0, 0)
    os.makedirs(zwischen, exist_ok=True)
    mp3s = sorted(n for n in os.listdir(audio) if n.lower().endswith(".mp3"))

    # Erst alle Schluessel, dann jeden Inhalt genau einmal umwandeln: zwei
    # byte-gleiche MP3s schrieben sonst gleichzeitig in dieselbe Datei
    # (Review 12.10.2026; heute gibt es keine, aber eine doppelt
    # vergebene Aufnahme reicht).
    schluessel = {}
    for name in mp3s:
        with open(os.path.join(audio, name), "rb") as f:
            schluessel[name] = ton_schluessel(hashlib.sha256(f.read()).hexdigest(), name)
    quelle_je_schluessel = {}
    for name in mp3s:
        quelle_je_schluessel.setdefault(schluessel[name], name)

    def umwandeln(paar):
        s, name = paar
        fertig = os.path.join(zwischen, s + ".ogg")
        if os.path.isfile(fertig) and os.path.getsize(fertig) > 0:
            return
        tmp = fertig + ".tmp.ogg"
        # Gleicher Schluessel heisst gleicher Filter (er steckt im
        # Schluessel), also genuegt der Name der ersten Quelle.
        f = ton_filter(name)
        r = subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                            "-i", os.path.join(audio, name)]
                           + (["-af", f] if f else [])
                           + ["-ac", "1", "-c:a", "libopus",
                              "-b:a", TON_BITRATE, "-vbr", "on", "-application", "audio",
                              tmp], capture_output=True)
        if r.returncode != 0 or not os.path.isfile(tmp) or os.path.getsize(tmp) == 0:
            raise RuntimeError("%s: %s" % (name, r.stderr.decode("utf-8", "replace")[-300:]))
        os.replace(tmp, fertig)

    print("\nTonspur nach Opus (%d Dateien, %s, %d davon mit gekuerzter Stille am Anfang) ..."
          % (len(mp3s), TON_BITRATE, sum(1 for n in mp3s if ton_filter(n))))
    try:
        with ThreadPoolExecutor(max_workers=max(2, (os.cpu_count() or 4))) as pool:
            list(pool.map(umwandeln, sorted(quelle_je_schluessel.items())))
        groessen = []
        for name in mp3s:
            quelle = os.path.join(audio, name)
            ziel = os.path.join(audio, name[:-4] + ".ogg")
            shutil.copyfile(os.path.join(zwischen, schluessel[name] + ".ogg"), ziel)
            groessen.append((os.path.getsize(quelle), os.path.getsize(ziel)))
            os.remove(quelle)
    except (RuntimeError, OSError) as e:
        raise SystemExit("ABBRUCH: Umwandlung der Tonspur gescheitert: %s" % e)
    index_pfad = os.path.join(audio, "index.json")
    index = json.load(io.open(index_pfad, encoding="utf-8"))
    umgeschrieben = ton_index_umschreiben(index)
    fehlen = [e["datei"] for e in index.get("toene", [])
              if not os.path.isfile(os.path.join(audio, e["datei"]))]
    if fehlen:
        raise SystemExit("ABBRUCH: %d Toene fehlen nach der Umwandlung, z. B. %s"
                         % (len(fehlen), ", ".join(fehlen[:5])))
    io.open(index_pfad, "w", encoding="utf-8").write(
        json.dumps(index, ensure_ascii=False, indent=1))
    vorher = sum(g[0] for g in groessen)
    nachher = sum(g[1] for g in groessen)
    print("   %d Eintraege umgeschrieben, %.1f MB -> %.1f MB"
          % (umgeschrieben, vorher / 1e6, nachher / 1e6))
    return (vorher, nachher)


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
    # Die Liste der Drachen-Dateien steht ebenfalls in web/inhalt
    # ("maskottchen"). Die App laedt einen Hautsatz haut/<farbe>/ nur, wenn
    # er dort steht - kommt einer per haut_einbauen.py dazu und niemand baut
    # den Inhalt neu, bliebe die Farbe am Handy stillschweigend die alte
    # (Bild-Drache, 15.10.2026).
    import inhalt
    for d in gebaut:
        with io.open(d, encoding="utf-8") as f:
            stand = json.load(f)
        if isinstance(stand, dict) and "maskottchen" in stand:
            if stand["maskottchen"] != inhalt.maskottchen_bilder():
                veraltet.append("web/maskottchen")
            break
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
    dauer_einsetzen()
    cloud_einsetzen()
    # Nach Emir: dessen Aufnahmen sind MP3 und werden mit umgewandelt.
    ton_verkleinern()
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
