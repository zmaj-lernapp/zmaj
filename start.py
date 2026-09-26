# -*- coding: utf-8 -*-
"""
start.py  –  DIESE DATEI IN THONNY ÖFFNEN UND AUF "RUN" (F5) DRÜCKEN

Was passiert dann?
  1. Die Vokabeln aus vokabeln.py werden geprüft (Tippfehler, doppelte Wörter).
  2. Ein kleiner Webserver startet auf deinem PC.
  3. Dein Browser öffnet die App automatisch.
  4. In der Thonny-Konsole steht eine zweite Adresse für das Handy
     (gleiches WLAN nötig).

Beenden: in Thonny auf "Stop" drücken (oder Strg+C in der Konsole).

Es werden nur Bausteine benutzt, die Python schon mitbringt.
Nichts muss installiert werden.
"""

import importlib
import json
import os
import socket
import sys
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------------------
# Pfade: alles relativ zu dieser Datei, egal von wo das Skript gestartet wird
# ---------------------------------------------------------------------------
ORDNER = os.path.dirname(os.path.abspath(__file__))
WEB_ORDNER = os.path.join(ORDNER, "web")
AUDIO_ORDNER = os.path.join(WEB_ORDNER, "audio")   # Tonspur: w0001.mp3 usw. + index.json
LOG_DATEI = os.path.join(ORDNER, "start.log")
PORT_START = 8000

# Wird die App über die Desktop-Verknüpfung (pythonw, ohne Fenster) gestartet,
# gibt es keine Konsole. Dann landen alle Meldungen in start.log.
if sys.stdout is None or sys.stderr is None:
    _log = open(LOG_DATEI, "w", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = _log

sys.path.insert(0, ORDNER)
import vokabeln     # noqa: E402  (nach sys.path-Änderung importieren)
import grammatik    # noqa: E402
import geschichten  # noqa: E402
import sprachen     # noqa: E402  (Texte der Oberfläche in allen Sprachen)
import uebersetzungen  # noqa: E402  (Lerninhalte in allen Sprachen)
import konten       # noqa: E402  (Anmeldung mit Name und Passwort)
import mail         # noqa: E402  (Bestätigung und Passwort vergessen)

# Wer angemeldet ist, steht in sitzungen.json. Die Datei gehört niemandem
# sonst – wer sie lesen kann, kommt in jedes Konto. Nicht weitergeben.
SITZUNG_DATEI = os.path.join(ORDNER, "sitzungen.json")
SITZUNGEN = konten.Sitzungen(SITZUNG_DATEI)

# Die Einmal-Codes aus den Mails (Bestätigung, neues Passwort).
CODE_DATEI = os.path.join(ORDNER, "codes.json")
CODES = konten.Codes(CODE_DATEI)

# Läuft die App später über HTTPS, hier auf True stellen. Dann schickt der
# Browser das Sitzungs-Cookie nur noch über eine verschlüsselte Verbindung.
NUR_HTTPS = False

# Ein gelöschtes Konto liegt noch so viele Tage als geloescht_<Name>_<Zeit>.json
# im Ordner, danach wird es endgültig entfernt. Die Frist ist die Schonzeit für
# Fehlklicks – und die Zusage, die in der Datenschutzerklärung und auf
# zmaj-lernapp.github.io/konto-loeschen.html steht. Wer sie ändert, muss beide
# Stellen mitändern.
GELOESCHT_TAGE = 30


# ---------------------------------------------------------------------------
# Vokabeln prüfen – gibt Hinweise in der Konsole aus, bricht aber nicht ab
# ---------------------------------------------------------------------------
def pruefe_vokabeln(daten):
    probleme = []
    ids = set()
    sektionen = {s.get("id") for s in daten.get("sektionen", [])}
    reihenfolge = [k.get("id") for k in daten["kategorien"]]
    for kat in daten["kategorien"]:
        for schluessel in ("id", "label", "words"):
            if schluessel not in kat:
                probleme.append(f"Level ohne '{schluessel}': {kat}")
        kid = kat.get("id", "?")
        if kid in ids:
            probleme.append(f"Level-id doppelt: '{kid}'")
        ids.add(kid)
        if sektionen and kat.get("sektion") not in sektionen:
            probleme.append(f"[{kid}] unbekannte Sektion '{kat.get('sektion')}'")
        for basis in kat.get("baut_auf", []):
            if basis not in reihenfolge:
                probleme.append(f"[{kid}] baut_auf nennt unbekanntes Level '{basis}'")
            elif reihenfolge.index(basis) >= reihenfolge.index(kid):
                probleme.append(f"[{kid}] baut_auf '{basis}' kommt erst später in der Liste")

        gesehen = set()
        for wort in kat.get("words", []):
            if "de" not in wort or "bs" not in wort:
                probleme.append(f"[{kid}] Wort ohne 'de' oder 'bs': {wort}")
                continue
            if not wort["de"].strip() or not wort["bs"].strip():
                probleme.append(f"[{kid}] leeres Wort: {wort}")
            if wort["bs"] in gesehen:
                probleme.append(f"[{kid}] doppelt: '{wort['bs']}'")
            gesehen.add(wort["bs"])

    for satz in daten["saetze"]:
        for schluessel in ("kat", "text", "answer", "de"):
            if schluessel not in satz:
                probleme.append(f"Satz ohne '{schluessel}': {satz}")
        if "___" not in satz.get("text", ""):
            probleme.append(f"Satz ohne Lücke '___': {satz.get('text')}")
        if satz.get("kat") not in ids:
            probleme.append(f"Satz mit unbekannter Kategorie '{satz.get('kat')}': {satz.get('text')}")

    # Grammatik-Lektionen
    for kid, lektion in daten.get("grammatik", {}).items():
        if kid not in ids:
            probleme.append(f"Grammatik für unbekanntes Level '{kid}'")
        for ue in lektion.get("uebungen", []):
            if ue.get("richtig") not in ue.get("optionen", []):
                probleme.append(f"[{kid}] Übung: 'richtig' steht nicht in 'optionen': {ue.get('frage')}")

    # Geschichten
    for g in daten.get("geschichten", []):
        if g.get("passt_zu") and g.get("passt_zu") not in ids:
            probleme.append(f"Geschichte '{g.get('id')}': passt_zu nennt unbekanntes Level '{g.get('passt_zu')}'")
        for f in g.get("fragen", []):
            if f.get("richtig") not in f.get("optionen", []):
                probleme.append(f"Geschichte '{g.get('id')}': 'richtig' fehlt in 'optionen': {f.get('frage')}")

    return probleme


def fehlende_woerter(daten):
    """Wörter in Geschichten, die im WOERTERBUCH fehlen (nur ein Hinweis)."""
    import re
    wb = daten.get("woerterbuch", {})
    fehlt = {}
    for g in daten.get("geschichten", []):
        eigene = {k.lower(): v for k, v in g.get("vokabeln", {}).items()}
        for w in re.findall(r"[^\W\d_]+", g["text"]):
            k = w.lower()
            if k not in wb and k not in eigene:
                fehlt.setdefault(g["id"], set()).add(w)
    return fehlt


def lade_daten(sprache=None):
    """Liest die Inhaltsdateien bei jedem Aufruf neu ein, damit Änderungen
    sofort nach einem Browser-Neuladen sichtbar sind.

    sprache: Kürzel aus sprachen.py ("de", "en", "tr", …). Die Lerninhalte
    werden damit übersetzt, soweit uebersetzungen.py etwas dazu weiß.
    Der bosnische Teil bleibt natürlich immer bosnisch."""
    for modul in (vokabeln, grammatik, geschichten, sprachen, uebersetzungen):
        importlib.reload(modul)
    code = sprache if sprachen.ist_sprache(sprache) else sprachen.GRUNDSPRACHE
    daten = {
        "sektionen": getattr(vokabeln, "SEKTIONEN", []),
        "kategorien": vokabeln.KATEGORIEN,
        "saetze": vokabeln.SAETZE,
        "grammatik": getattr(grammatik, "GRAMMATIK", {}),
        "geschichten": getattr(geschichten, "GESCHICHTEN", []),
        "woerterbuch": getattr(geschichten, "WOERTERBUCH", {}),
    }
    daten = mit_kennung(daten)     # noch auf Deutsch, damit die Kennung gleich bleibt
    fertig, gesamt = uebersetzungen.stand(daten, code)
    daten = uebersetzungen.anwenden(daten, code)
    daten.update({
        "audio": eigene_aufnahmen(),
        "maskottchen": maskottchen_bilder(),
        "sprache": code,
        "sprachen": sprachen.SPRACHEN,
        "texte": sprachen.texte(code),
        # Ein Schalter für beides: echte Werbung und der Werbe-Abschnitt in
        # der Datenschutzerklärung. Er steht in sprachen.py, damit Text und
        # Verhalten nicht auseinanderlaufen können.
        "werbung_laeuft": bool(getattr(sprachen, "WERBUNG_LAEUFT", False)),
        "uebersetzt": {"fertig": fertig, "gesamt": gesamt},
    })
    return daten


def mit_kennung(daten):
    """Jedes Wort bekommt eine Kennung „bedeutung:wort“, also „hundert:sto“
    und „tisch:sto“.

    Die App merkt sich damit nicht nur das bosnische Wort, sondern auch, welche
    Bedeutung gemeint ist. Nötig, weil dasselbe Wort zweierlei heißen kann:
    „sto“ ist die Zahl hundert und der Tisch, „oko“ das Auge und „um herum“.
    Früher galt die zweite Bedeutung automatisch als gekonnt, sobald man die
    erste gelernt hatte.

    Die Kennung wird aus der deutschen Bedeutung gebaut, bevor übersetzt wird.
    Sie bleibt deshalb in jeder Sprache dieselbe."""
    daten["kategorien"] = [
        dict(k, words=[dict(w, id="%s:%s" % (w.get("de", "").strip().lower(), w.get("bs", "")))
                       for w in k.get("words", [])])
        for k in daten.get("kategorien", [])]
    return daten


def maskottchen_bilder():
    """Bilder in web/maskottchen: zmaj-frei.png (normal), optional zmaj-jubel.png,
    zmaj-traurig.png. Fehlen sie, zeichnet die App den Drachen als Vektor."""
    ordner = os.path.join(WEB_ORDNER, "maskottchen")
    try:
        return sorted(f for f in os.listdir(ordner) if f.lower().endswith((".png", ".webp", ".jpg", ".jpeg", ".gif", ".json", ".riv")))
    except OSError:
        return []


def eigene_aufnahmen():
    """Dateinamen im Ordner web/audio – nur noch für die Meldung beim Start.
    Welche Datei zu welchem Wort gehört, steht seit dem 15.09.2026 in
    web/audio/index.json. Die App liest diese Datei selbst und braucht
    den Server dafür nicht mehr."""
    try:
        return sorted(f for f in os.listdir(AUDIO_ORDNER)
                      if f.lower().endswith((".mp3", ".m4a", ".wav", ".ogg", ".webm")))
    except OSError:
        return []


def oeffne_browser(url):
    """Bevorzugt Microsoft Edge: nur dort gibt es bosnische Stimmen (Goran, Vesna)
    für das Vorlesen. Sonst der Standard-Browser."""
    import subprocess
    for pfad in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                 r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(pfad):
            try:
                subprocess.Popen([pfad, url])
                return
            except OSError:
                break
    webbrowser.open(url)


# ---------------------------------------------------------------------------
# Profile und Fortschritt
# Jede Person hat eine eigene Datei: fortschritt_<Name>.json (Levels, Wörter,
# Geschichten, Streak, Leben, Vollversion). Beim ersten Start werden die
# Profile aus START_PROFILE angelegt.
# ---------------------------------------------------------------------------
fortschritt_sperre = threading.Lock()
START_PROFILE = ["Ajdin", "Kübra"]
PROFIL_PRAEFIX = "fortschritt_"


def profil_name_saeubern(name):
    """Nur Buchstaben, Ziffern, Bindestrich, Unterstrich und Punkt.

    Der Name wird zum Dateinamen, deshalb fliegt alles andere raus –
    Leerzeichen inbegriffen. Dieselben Zeichen lässt konten.pruefe_name()
    durch; die beiden müssen zusammenpassen.
    """
    name = "".join(ch for ch in str(name) if ch.isalnum() or ch in "-_.").strip(". ")
    return name[:konten.NAME_MAX]


def profil_datei(name):
    return os.path.join(ORDNER, f"{PROFIL_PRAEFIX}{name}.json")


def liste_profile():
    """Alle Profilnamen, alphabetisch."""
    namen = []
    for datei in os.listdir(ORDNER):
        if datei.startswith(PROFIL_PRAEFIX) and datei.endswith(".json"):
            namen.append(datei[len(PROFIL_PRAEFIX):-5])
    return sorted(namen, key=str.lower)


def profil_anlegen(name, passwort=None, email=None):
    name = konten.pruefe_name(name)           # wirft bei Leerzeichen usw.
    if profil_name_saeubern(name) != name:
        raise ValueError("name_zeichen")
    if name.lower() in {x.lower() for x in liste_profile()}:
        raise ValueError("name_vergeben")
    neu = _saeubere({})
    if passwort is not None:
        neu["passwort"] = konten.neuer_hash(passwort)
    if email is not None:
        if profil_zu_email(email):
            raise ValueError("email_vergeben")
        neu["email"] = mail.adresse_sauber(email)
        neu["email_bestaetigt"] = False
    speichere_fortschritt(name, neu)
    return name


def profil_finden(name):
    """Sucht das Profil ohne Rücksicht auf Groß- und Kleinschreibung."""
    gesucht = str(name or "").strip().lower()
    if not gesucht:
        return None
    for vorhanden in liste_profile():
        if vorhanden.lower() == gesucht:
            return vorhanden
    return None


def profil_zu_email(email):
    """Welches Konto gehört zu dieser Adresse? None, wenn keines."""
    try:
        gesucht = mail.adresse_sauber(email)
    except ValueError:
        return None
    for name in liste_profile():
        if lade_fortschritt(name).get("email") == gesucht:
            return name
    return None


def profil_zu_kennung(kennung):
    """Beim Anmelden darf man die E-Mail oder den Benutzernamen eingeben."""
    k = str(kennung or "").strip()
    if "@" in k:
        return profil_zu_email(k)
    return profil_finden(k)


def profil_loeschen(name):
    """Löschen in zwei Schritten.

    Sofort: Die Datei wird in geloescht_<Name>_<Zeit>.json umbenannt. Damit
    ist das Konto weg – anmelden kann sich niemand mehr, der Name ist wieder
    frei, und ein Fehlklick lässt sich am selben Tag noch retten.

    Endgültig: Nach GELOESCHT_TAGE Tagen räumt aufraeumen_geloeschte() die
    Datei weg. Das ist keine Höflichkeit, sondern Pflicht – eine „Löschung“,
    die eine vollständige Kopie behält, ist nach der DSGVO keine.
    """
    if name not in liste_profile():
        raise ValueError("Profil unbekannt")
    ziel = os.path.join(ORDNER, f"geloescht_{name}_{int(time.time())}.json")
    os.replace(profil_datei(name), ziel)
    SITZUNGEN.alle_beenden(name)      # auf allen Geräten abmelden
    CODES.loesche_fuer(name)          # offene Links aus Mails entwerten


def aufraeumen_geloeschte(schweigend=True):
    """Entfernt gelöschte Konten, die älter als GELOESCHT_TAGE Tage sind.

    Läuft beim Start und danach einmal am Tag. Gibt zurück, wie viele
    Dateien weggeräumt wurden.
    """
    grenze = time.time() - GELOESCHT_TAGE * 86400
    weg = 0
    try:
        namen = os.listdir(ORDNER)
    except OSError:
        return 0
    for name in namen:
        if not (name.startswith("geloescht_") and name.endswith(".json")):
            continue
        pfad = os.path.join(ORDNER, name)
        try:
            # Der Zeitstempel steckt im Dateinamen; fehlt er, zählt das Datum
            teil = name[:-5].rsplit("_", 1)[-1]
            zeit = float(teil) if teil.isdigit() else os.path.getmtime(pfad)
            if zeit < grenze:
                os.remove(pfad)
                weg += 1
                if not schweigend:
                    print(f"Endgültig gelöscht (älter als {GELOESCHT_TAGE} Tage): {name}")
        except OSError:
            pass
    return weg


def aufraeumen_im_hintergrund():
    """Einmal am Tag nachsehen, solange der Server läuft."""
    def schleife():
        while True:
            time.sleep(24 * 3600)
            try:
                aufraeumen_geloeschte(schweigend=False)
            except Exception:
                pass
    threading.Thread(target=schleife, daemon=True).start()


def profile_vorbereiten():
    """Beim Start: ganz alte fortschritt.json übernehmen, Konten melden.

    Neue Konten legt niemand mehr automatisch an – die entstehen nur noch
    über die Anmeldeseite, mit Passwort.
    """
    alt = os.path.join(ORDNER, "fortschritt.json")
    if not liste_profile() and os.path.exists(alt):
        os.replace(alt, profil_datei(START_PROFILE[0]))
        print(f"Alter Fortschritt übernommen für Konto {START_PROFILE[0]}.")

    namen = liste_profile()
    if not namen:
        print("Noch keine Konten. Das erste legst du in der App an.")
        return
    ohne = [n for n in namen if not konten.hat_passwort(lade_fortschritt(n))]
    print("Konten:", ", ".join(namen))
    if ohne:
        print("  Noch ohne Passwort: " + ", ".join(ohne))
        print("  Beim nächsten Anmelden fragt die App danach. Der Fortschritt bleibt.")


def konto_anmelden(kennung, passwort):
    """Prüft E-Mail oder Benutzername samt Passwort.

    Wirft ValueError mit einem Kürzel, das die Oberfläche übersetzt:
      falsche_daten    – Kennung oder Passwort stimmt nicht
      gesperrt:<sek>   – zu viele Fehlversuche
      email_offen      – Konto da, aber die Adresse ist noch nicht bestätigt
    """
    echter = profil_zu_kennung(kennung)
    # Immer denselben Fehler melden, egal ob die Kennung oder das Passwort
    # falsch war. Sonst könnte man ausprobieren, welche Konten es gibt.
    if not echter:
        raise ValueError("falsche_daten")

    rest = konten.gesperrt_bis(echter)
    if rest:
        raise ValueError("gesperrt:%d" % max(1, int(rest - time.time())))

    profil = lade_fortschritt(echter)
    if not konten.hat_passwort(profil) or not konten.passt(passwort, profil["passwort"]):
        konten.fehlversuch(echter)
        raise ValueError("falsche_daten")

    konten.versuche_zuruecksetzen(echter)
    # Erst nach richtigem Passwort verraten, dass die Bestätigung fehlt.
    if profil.get("email") and not profil.get("email_bestaetigt"):
        raise ValueError("email_offen")
    return echter


def basis_adresse(handler):
    """Unter welcher Adresse erreicht der Nutzer die App? Für die Links in
    den Mails. Kommt aus der Anfrage, funktioniert also lokal wie online.

    Eine Ausnahme: „localhost“ bedeutet auf jedem Gerät *dieses* Gerät.
    Wer das Konto am PC anlegt und die Mail am Handy öffnet, landet mit so
    einem Link im Nichts – das Handy sucht die App bei sich selbst. Steht
    also localhost in der Anfrage, kommt stattdessen die WLAN-Adresse
    dieses PCs in den Link. Die funktioniert auf beiden Geräten.
    Sobald die App online läuft, steht dort ohnehin der echte Name."""
    port_hier = handler.server.server_address[1] if getattr(handler, "server", None) else PORT_START
    host = handler.headers.get("Host") or ("127.0.0.1:%d" % port_hier)

    if host.startswith("["):                    # IPv6 steht in eckigen Klammern
        name, _, rest = host.partition("]")
        name, port = name[1:], rest[1:] if rest.startswith(":") else ""
    else:
        name, _, port = host.partition(":")

    if name.lower() in ("localhost", "127.0.0.1", "::1"):
        ip = lokale_ip()
        if ip:
            host = "%s:%s" % (ip, port or port_hier)

    schema = "https" if NUR_HTTPS else "http"
    return "%s://%s" % (schema, host)


def schicke_bestaetigung(name, basis, texte):
    """Legt einen Code an und schickt die Bestätigungsmail."""
    profil = lade_fortschritt(name)
    adresse = profil.get("email")
    if not adresse or profil.get("email_bestaetigt"):
        return False
    code = CODES.neu(name, "mail", konten.CODE_STUNDEN_MAIL)
    link = "%s/?bestaetigen=%s" % (basis, code)
    return mail.sende_bestaetigung(adresse, name, link, texte)


def schicke_passwort_link(name, basis, texte):
    profil = lade_fortschritt(name)
    adresse = profil.get("email")
    if not adresse:
        return False
    code = CODES.neu(name, "pw", konten.CODE_STUNDEN_PW)
    link = "%s/?neues-passwort=%s" % (basis, code)
    return mail.sende_passwort_link(adresse, name, link, texte)


def konto_passwort_setzen(name, neues, altes=None):
    """Legt ein Passwort fest oder ändert es.

    Bei einem Profil, das noch keins hat (Ajdin und Kübra von früher),
    darf man ohne altes Passwort eins setzen. Hat es schon eins, muss das
    alte stimmen.
    """
    echter = profil_finden(name)
    if not echter:
        raise ValueError("falsche_daten")

    profil = lade_fortschritt(echter)
    if konten.hat_passwort(profil):
        rest = konten.gesperrt_bis(echter)
        if rest:
            raise ValueError("gesperrt:%d" % max(1, int(rest - time.time())))
        if not konten.passt(altes, profil["passwort"]):
            konten.fehlversuch(echter)
            raise ValueError("altes_falsch")

    profil["passwort"] = konten.neuer_hash(neues)   # prüft auch die Länge
    speichere_fortschritt(echter, profil)
    konten.versuche_zuruecksetzen(echter)
    return echter


def konto_info(name):
    """Was die Oberfläche über das angemeldete Konto wissen muss."""
    d = lade_fortschritt(name)
    return {"name": name, "levels": len(d["bestanden"]), "woerter": len(d["gewusst"]),
            "tage": len(d["tage"]), "premium": d["premium"],
            "hat_passwort": konten.hat_passwort(d),
            "email": d.get("email", ""),
            "email_bestaetigt": bool(d.get("email_bestaetigt", False))}


# gewusst = Wörter, bestanden = Level-ids, gelesen = Geschichten-ids,
# tage  = Datumsliste der Tage mit einer fertigen Lektion (für die Lernserie)
# frost = Datumsliste der Tage, die ein Serienschutz gerettet hat. Sie zählen
#         als "Serie nicht gerissen", aber nicht als Lerntag.
# besitz = im Laden gekaufter Zierrat, z. B. ["hut"]. Einmal gekauft, bleibt es.
# gefeiert = schon gefeierte Wegmarken, z. B. ["tage7", "tage30"]. Eine reine
#            Liste von Kürzeln, deshalb passt sie ohne Weiteres hier hinein.
FELDER = ("gewusst", "bestanden", "gelesen", "tage", "frost", "besitz", "gefeiert")
# rekord = die längste Lernserie, die jemals lief. Eine nackte Zahl, also
#          KEIN Feld für FELDER oben - die werden als Listen behandelt.
# wann   = {"lv:<id>": "2026-09-18"} – wann ein Level bestanden und eine
#          Geschichte gelesen wurde. Das Einzige im ganzen Lernstand, das
#          sich nachträglich nicht mehr beschaffen lässt.
REKORD_MAX = 100_000     # mehr Tage am Stück hat noch niemand gelernt
WANN_MAX = 500           # 63 Level und 12 Geschichten – reichlich Luft
# leben  = {"anzahl": 0-5, "zeit": Zeitstempel in Millisekunden, ab dem nachgefüllt wird}
# schutz = dasselbe für den Serienschutz: alle SCHUTZ_TAGE Tage wächst einer nach
# premium = True schaltet unbegrenzte Leben frei (Vollversion; Bezahlung kommt später)
LEBEN_LEER = {"anzahl": 5, "zeit": 0}
SCHUTZ_MAX = 2       # so viele Serienschutz kann man gleichzeitig haben
SCHUTZ_START = 1     # so viele bekommt ein neues Profil geschenkt
SCHUTZ_TAGE = 10     # alle so viele Tage wächst ein Schutz nach
# tagwerk = {"2026-09-14": {"auf": 23, "ric": 18}} – die Tageszähler für die
#           drei Tagesaufgaben. Die Schlüssel sind die Quest-Kürzel, was 0 ist
#           steht nicht drin. "tage" bleibt davon unberührt: das ist die Serie.
#           WELCHE drei Quests heute dran sind, steht NICHT in der Datei – das
#           rechnet der Browser aus Profilname und Datum aus, immer gleich.
#           "zeit" ist die Lernzeit in Sekunden, alle anderen sind Stückzahlen.
TAGWERK_SCHLUESSEL = ("auf", "ric", "lek", "per", "neu", "hoer", "lue", "gesch", "zeit")
TAGWERK_TAGE_MAX = 400   # so viele Tage bleiben in der Datei, ältere fallen raus
TAGWERK_MAX = 500        # mehr zählt ein einzelner Stückzähler nicht
TAGWERK_ZEIT_MAX = 6 * 3600   # Lernzeit je Tag: mehr als sechs Stunden nicht
# Münzen aus den Tagesaufgaben, zum Ausgeben im Laden.
# Gespeichert wird NICHT der Kontostand, sondern zwei Summen, die beide nur
# wachsen können: muenzen_ges (jemals verdient) und muenzen_aus (jemals
# ausgegeben). Der Stand ist die Differenz. Grund: beim Speichern gewinnt
# pro Feld der größere Wert – ein altes Browserfenster kann damit weder
# Münzen herbeizaubern noch einen Kauf rückgängig machen. Mit einem einzigen
# Kontostand ginge beides.
MUENZEN_MAX = 999_999


def _zahl(wert, ersatz=0):
    """int() ohne Absturz. Ein kaputter Wert in der Datei darf nicht dazu
       führen, dass lade_fortschritt() ein leeres Profil zurückgibt."""
    try:
        return int(wert)
    except (TypeError, ValueError):
        return ersatz


def _ist_datum(s):
    """True bei genau 'JJJJ-MM-TT' UND nur, wenn es den Tag wirklich gibt.

       Die Form wird von Hand geprüft, nicht mit re – das hier läuft bei
       jedem Speichern über hunderte Schlüssel. Erst wenn die Form stimmt,
       wird der Kalender befragt; das kostet dann nur noch bei den wenigen
       Schlüsseln etwas, die überhaupt in Frage kommen.

       Ohne die zweite Hälfte kam '2026-13-99' durch – gemessen in der
       Nacht auf den 19.09.2026. In den Lerntagen zählt so etwas bei
       days.size mit, und das ist die Zahl hinter "1000 Tage gelernt"."""
    if not (isinstance(s, str) and len(s) == 10 and s[4] == "-" and s[7] == "-"
            and s[:4].isdigit() and s[5:7].isdigit() and s[8:].isdigit()):
        return False
    try:
        time.strptime(s, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def _saeubere_tagwerk(roh):
    """Macht aus beliebigem Browser-Inhalt saubere Tageszähler."""
    if not isinstance(roh, dict):
        return {}
    # Ein Tag in der Zukunft kann nur von einer verstellten Uhr kommen. Ein
    # Tag Spielraum, weil Gerät und Server in verschiedenen Zeitzonen stehen
    # können, sobald der Server irgendwann nicht mehr auf demselben PC läuft.
    morgen = time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400))
    sauber = {}
    for tag, werte in roh.items():
        if not _ist_datum(tag) or tag > morgen or not isinstance(werte, dict):
            continue
        tageswerk = {}
        for k in TAGWERK_SCHLUESSEL:     # unbekannte Schlüssel fliegen raus
            n = _zahl(werte.get(k), 0)
            if n > 0:
                tageswerk[k] = min(n, TAGWERK_ZEIT_MAX if k == "zeit" else TAGWERK_MAX)
        if tageswerk:
            sauber[tag] = tageswerk
    if len(sauber) > TAGWERK_TAGE_MAX:   # die ältesten Tage fallen weg
        for tag in sorted(sauber)[:len(sauber) - TAGWERK_TAGE_MAX]:
            del sauber[tag]
    return sauber


def _saeubere_wann(roh):
    """{"lv:<id>": "JJJJ-MM-TT"} – wann etwas geschafft wurde. Alles, was
       kein echtes Datum ist, fliegt raus; ein Datum aus der Zukunft kann
       nur von einer verstellten Uhr kommen und fliegt auch."""
    if not isinstance(roh, dict):
        return {}
    morgen = time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400))
    sauber = {}
    for schluessel, tag in roh.items():
        if not isinstance(schluessel, str) or not _ist_datum(tag) or tag > morgen:
            continue
        sauber[str(schluessel)[:80]] = tag
        if len(sauber) >= WANN_MAX:
            break
    return sauber


def _saeubere(daten):
    sauber = {feld: [str(x) for x in daten.get(feld, []) if isinstance(daten.get(feld), list)] for feld in FELDER}
    leben = daten.get("leben") if isinstance(daten.get("leben"), dict) else {}
    sauber["leben"] = {
        "anzahl": max(0, min(5, _zahl(leben.get("anzahl", 5), 5))),
        "zeit": _zahl(leben.get("zeit", 0)),
    }
    schutz = daten.get("schutz") if isinstance(daten.get("schutz"), dict) else {}
    sauber["schutz"] = {
        "anzahl": max(0, min(SCHUTZ_MAX, _zahl(schutz.get("anzahl", SCHUTZ_START), SCHUTZ_START))),
        "zeit": _zahl(schutz.get("zeit", 0)),
    }
    sauber["premium"] = bool(daten.get("premium", False))
    sauber["rekord"] = max(0, min(REKORD_MAX, _zahl(daten.get("rekord"), 0)))
    # Lerntage und Frosttage sind Datumslisten, keine beliebigen Zeichenketten.
    # Über FELDER kommen sie nur als str(x) herein - hier fliegt heraus, was
    # kein echter Kalendertag ist. Doppelte fallen dabei auch weg.
    for feld in ("tage", "frost"):
        sauber[feld] = sorted({t for t in sauber[feld] if _ist_datum(t)})
    sauber["wann"] = _saeubere_wann(daten.get("wann"))
    sauber["tagwerk"] = _saeubere_tagwerk(daten.get("tagwerk"))
    # Münzen: zwei nur wachsende Summen, der Stand ist die Differenz.
    # Eintauschbar gegen Herzen, Serienschutz und Zierrat – NICHT gegen die
    # Vollversion: "premium" darf der Browser nie setzen (siehe do_POST).
    ges = max(0, min(MUENZEN_MAX, _zahl(daten.get("muenzen_ges"), 0)))
    aus = max(0, min(MUENZEN_MAX, _zahl(daten.get("muenzen_aus"), 0)))
    sauber["muenzen_ges"] = ges
    sauber["muenzen_aus"] = min(aus, ges)   # nie mehr ausgegeben als verdient
    # Der Passwort-Hash muss jede Runde überleben. Er kommt nie aus dem
    # Browser, sondern immer aus der Datei – siehe do_POST /api/fortschritt.
    p = daten.get("passwort")
    if isinstance(p, dict) and p.get("hash") and p.get("salz"):
        sauber["passwort"] = {"salz": str(p["salz"]), "hash": str(p["hash"]),
                              "runden": int(p.get("runden", konten.RUNDEN))}
    # Ebenso die E-Mail-Adresse und ob sie bestätigt wurde
    if daten.get("email"):
        sauber["email"] = str(daten["email"]).strip().lower()[:254]
        sauber["email_bestaetigt"] = bool(daten.get("email_bestaetigt", False))
    return sauber


def fortschritt_fuer_browser(name):
    """Wie lade_fortschritt(), aber ohne den Passwort-Hash. Der Browser
       braucht ihn nie – und solange kein HTTPS läuft, liest ihn sonst
       jeder im selben WLAN mit und kann ihn in Ruhe durchprobieren."""
    daten = lade_fortschritt(name)
    daten.pop("passwort", None)
    return daten


def lade_fortschritt(name):
    try:
        with open(profil_datei(name), "r", encoding="utf-8") as f:
            daten = json.load(f)
        if isinstance(daten, dict):
            return _saeubere(daten)
    except (OSError, ValueError):
        pass
    return _saeubere({})


def speichere_fortschritt(name, daten):
    with fortschritt_sperre:
        with open(profil_datei(name), "w", encoding="utf-8") as f:
            json.dump(daten, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Der Webserver
# ---------------------------------------------------------------------------
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_ORDNER, **kwargs)

    _extra_cookie = None      # wird von _anmelden und _abmelden gesetzt

    def _json(self, objekt, status=200):
        body = json.dumps(objekt, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if self._extra_cookie:
            self.send_header("Set-Cookie", self._extra_cookie)
            self._extra_cookie = None
        self.end_headers()
        self.wfile.write(body)

    def _sprache(self):
        """Sprachkürzel aus ?sprache=... in der Adresse, sonst Deutsch."""
        from urllib.parse import urlparse, parse_qs
        werte = parse_qs(urlparse(self.path).query).get("sprache", [])
        code = werte[0][:5] if werte else ""
        return code if sprachen.ist_sprache(code) else sprachen.GRUNDSPRACHE

    def _profil(self):
        """Wer ist angemeldet? Kommt aus dem Sitzungs-Cookie, nie aus der Adresse.

        Früher stand der Name in ?profil=... – damit konnte jeder im WLAN
        den Fortschritt jedes anderen lesen und überschreiben.
        """
        token = konten.token_aus_cookie(self.headers.get("Cookie"))
        name = SITZUNGEN.name_zu(token)
        return name if name and name in liste_profile() else None

    def _anmelden(self, name, bleiben=False):
        """Sitzung anlegen und das Cookie mitschicken."""
        token = SITZUNGEN.anlegen(name, bleiben=bleiben)
        self._extra_cookie = konten.cookie_setzen(token, sicher=NUR_HTTPS, bleiben=bleiben)

    def _abmelden(self):
        token = konten.token_aus_cookie(self.headers.get("Cookie"))
        if token:
            SITZUNGEN.beenden(token)
        self._extra_cookie = konten.cookie_loeschen()

    def _vom_eigenen_pc(self):
        """Sitzt der Anfragende an diesem PC?

        Zwei Sachen darf nur er: den Server beenden und das App-Symbol neu
        schreiben. Beides fasst den Rechner an und hat im Netz nichts
        verloren – auch nicht im heimischen WLAN.
        """
        return self.client_address[0] in ("127.0.0.1", "::1", "localhost")

    BODY_MAX = 1_000_000   # ein volles Profil ist keine 100 KB groß

    def _body(self):
        laenge = _zahl(self.headers.get("Content-Length", 0))
        if laenge > self.BODY_MAX:
            raise ValueError("Anfrage zu groß")
        daten = json.loads(self.rfile.read(laenge).decode("utf-8")) if laenge else {}
        if not isinstance(daten, dict):
            raise ValueError("Erwartet ein Objekt")
        return daten

    def do_GET(self):
        if self.path.startswith("/api/daten"):
            return self._json(lade_daten(self._sprache()))
        if self.path.startswith("/api/konto"):
            # Beim Laden der Seite: bin ich noch angemeldet?
            name = self._profil()
            if not name:
                return self._json({"angemeldet": False})
            return self._json({"angemeldet": True, **konto_info(name)})
        if self.path.startswith("/api/fortschritt"):
            name = self._profil()
            if not name:
                return self._json({"ok": False, "fehler": "nicht_angemeldet"}, status=401)
            return self._json(fortschritt_fuer_browser(name))
        if self.path == "/":
            self.path = "/index.html"
        elif self.path.startswith("/favicon.ico"):
            self.path = "/icon.ico"       # danach fragt der Browser von selbst
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/beenden"):
            # Knopf "Beenden" in der App: Server sauber herunterfahren.
            # Nur vom eigenen PC aus, sonst könnte jeder im WLAN die App
            # der anderen abschalten.
            if not self._vom_eigenen_pc():
                return self._json({"ok": False, "fehler": "nur_lokal"}, status=403)
            self._json({"ok": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        try:
            if self.path.startswith("/api/feedback"):
                # Rückmeldung aus der App: geht per Mail an das Postfach der
                # App und wird zusätzlich in feedback.txt mitgeschrieben –
                # falls der Versand einmal scheitert, ist sie nicht weg.
                # Nur für Angemeldete, sonst kann jeder die Datei vollschreiben.
                if not self._profil():
                    return self._json({"ok": False, "fehler": "nicht_angemeldet"}, status=401)
                import datetime
                d = self._body()
                text = str(d.get("text", "")).strip()[:2000]
                if not text:
                    raise ValueError("Text fehlt")
                wer = self._profil()
                adresse = lade_fortschritt(wer).get("email") or ""
                sprache = self._sprache()
                with fortschritt_sperre:
                    with open(os.path.join(ORDNER, "feedback.txt"), "a", encoding="utf-8") as f:
                        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {wer} <{adresse}> [{sprache}]\n{text}\n---\n")
                # Im Hintergrund verschicken: Der Nutzer soll nicht warten,
                # bis der Mailserver geantwortet hat.
                threading.Thread(target=mail.sende_feedback,
                                 args=(wer, adresse, sprache, text),
                                 daemon=True).start()
                return self._json({"ok": True})
            if self.path.startswith("/api/konto/anlegen"):
                # Konto anlegen, aber noch nicht anmelden: erst muss die
                # E-Mail bestätigt werden.
                d = self._body()
                konten.pruefe_passwort_regeln(d.get("passwort"))
                name = profil_anlegen(d.get("name", ""), d.get("passwort"), d.get("email", ""))
                raus = schicke_bestaetigung(name, basis_adresse(self), sprachen.texte(self._sprache()))
                return self._json({"ok": True, "name": name, "email_offen": True,
                                   "mail_raus": raus})
            if self.path.startswith("/api/konto/anmelden"):
                d = self._body()
                name = konto_anmelden(d.get("kennung", d.get("name", "")), d.get("passwort", ""))
                self._anmelden(name, bleiben=bool(d.get("bleiben")))
                return self._json({"ok": True, **konto_info(name)})
            if self.path.startswith("/api/konto/bestaetigen"):
                # Der Nutzer hat auf den Link in der Mail geklickt
                d = self._body()
                name = CODES.verbrauche(d.get("code", ""), "mail")
                if not name or name not in liste_profile():
                    return self._json({"ok": False, "fehler": "code_ungueltig"}, status=400)
                profil = lade_fortschritt(name)
                profil["email_bestaetigt"] = True
                speichere_fortschritt(name, profil)
                self._anmelden(name, bleiben=bool(d.get("bleiben")))
                return self._json({"ok": True, **konto_info(name)})
            if self.path.startswith("/api/konto/mail_neu"):
                # Bestätigungsmail noch einmal schicken
                d = self._body()
                name = profil_zu_kennung(d.get("kennung", ""))
                if name:
                    schicke_bestaetigung(name, basis_adresse(self), sprachen.texte(self._sprache()))
                # Auch wenn es das Konto nicht gibt: dasselbe melden,
                # sonst kann man Adressen durchprobieren.
                return self._json({"ok": True})
            if self.path.startswith("/api/konto/vergessen"):
                d = self._body()
                name = profil_zu_kennung(d.get("kennung", ""))
                if name:
                    schicke_passwort_link(name, basis_adresse(self), sprachen.texte(self._sprache()))
                return self._json({"ok": True})
            if self.path.startswith("/api/konto/neues_passwort"):
                # Neues Passwort über den Link aus der Mail
                d = self._body()
                name = CODES.pruefe(d.get("code", ""), "pw")
                if not name or name not in liste_profile():
                    return self._json({"ok": False, "fehler": "code_ungueltig"}, status=400)
                konten.pruefe_passwort_regeln(d.get("neu"))
                profil = lade_fortschritt(name)
                profil["passwort"] = konten.neuer_hash(d.get("neu"))
                # Wer per Mail ein Passwort setzen kann, hat die Adresse
                profil["email_bestaetigt"] = True
                speichere_fortschritt(name, profil)
                CODES.verbrauche(d.get("code", ""), "pw")
                SITZUNGEN.alle_beenden(name)
                konten.versuche_zuruecksetzen(name)
                self._anmelden(name, bleiben=bool(d.get("bleiben")))
                return self._json({"ok": True, **konto_info(name)})
            if self.path.startswith("/api/konto/passwort"):
                # Eigenes Passwort ändern – nur angemeldet und nur mit dem
                # alten Passwort. Wer seins vergessen hat, geht über die Mail.
                name = self._profil()
                if not name:
                    return self._json({"ok": False, "fehler": "nicht_angemeldet"}, status=401)
                d = self._body()
                name = konto_passwort_setzen(name, d.get("neu", ""), d.get("alt"))
                SITZUNGEN.alle_beenden(name)      # andere Geräte fliegen raus
                self._anmelden(name, bleiben=True)   # dieses hier bleibt drin
                return self._json({"ok": True, **konto_info(name)})
            if self.path.startswith("/api/konto/abmelden"):
                self._abmelden()
                return self._json({"ok": True})
            if self.path.startswith("/api/konto/loeschen"):
                # Nur das eigene Konto, und nur mit Passwort
                name = self._profil()
                if not name:
                    return self._json({"ok": False, "fehler": "nicht_angemeldet"}, status=401)
                konto_anmelden(name, self._body().get("passwort", ""))
                SITZUNGEN.alle_beenden(name)
                profil_loeschen(name)
                self._abmelden()
                return self._json({"ok": True})
            if self.path.startswith("/api/fortschritt"):
                name = self._profil()
                if not name:
                    return self._json({"ok": False, "fehler": "nicht_angemeldet"}, status=401)
                daten = self._body()
                for feld in FELDER:
                    if not isinstance(daten.get(feld, []), list):
                        raise ValueError(f"{feld} muss eine Liste sein")
                alt = lade_fortschritt(name)
                neu = _saeubere(daten)
                # Das hier kommt nie aus dem Browser, immer aus der Datei –
                # sonst wäre es nach der ersten gespeicherten Lektion weg:
                neu["premium"] = alt["premium"]          # Vollversion
                for feld in ("passwort", "email", "email_bestaetigt"):
                    if alt.get(feld) is not None:
                        neu[feld] = alt[feld]
                    else:
                        neu.pop(feld, None)
                # Tageszähler zusammenführen statt ersetzen: pro Tag gewinnt
                # der größere Wert. Ein altes Browser-Tab kann damit keine
                # bereits gezählten Aufgaben mehr wegnehmen.
                zusammen = dict(alt.get("tagwerk", {}))
                for tag, werte in neu["tagwerk"].items():
                    z = dict(zusammen.get(tag, {}))
                    for k, n in werte.items():
                        z[k] = max(z.get(k, 0), n)
                    zusammen[tag] = z
                neu["tagwerk"] = _saeubere_tagwerk(zusammen)
                # Beide Münzsummen wachsen nur. Ein altes Browserfenster kann
                # damit keinen Kauf rückgängig machen und keine Münzen erfinden.
                # Gekauftes bleibt gekauft: vereinigen statt ersetzen, sonst
                # nimmt ein altes Browserfenster einen Kauf wieder weg.
                neu["besitz"] = sorted(set(neu.get("besitz", [])) | set(alt.get("besitz", [])))
                for feld in ("muenzen_ges", "muenzen_aus"):
                    neu[feld] = max(neu.get(feld, 0), alt.get(feld, 0))
                neu["muenzen_aus"] = min(neu["muenzen_aus"], neu["muenzen_ges"])
                speichere_fortschritt(name, neu)
                return self._json({"ok": True})
        except (ValueError, UnicodeDecodeError, OSError, AssertionError, KeyError) as e:
            return self._json({"ok": False, "fehler": str(e)}, status=400)
        self.send_error(404)

    def end_headers(self):
        # Browser soll index.html, Symbol und Maskottchen nicht zwischenspeichern,
        # damit Änderungen sofort sichtbar sind
        if self.path.endswith((".html", ".ico", ".json")) or self.path == "/" or "icon-256" in self.path or "flagge" in self.path:
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format, *args):
        # Nur Fehler in die Konsole, nicht jeden einzelnen Aufruf
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(format, *args)


def lokale_ip():
    """Adresse dieses PCs im WLAN, damit das Handy die App öffnen kann."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # es wird nichts gesendet, nur die Route ermittelt
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None


def starte_server():
    # Windows lässt zwei Server auf demselben Port zu, wenn allow_reuse_address gesetzt ist.
    # Dann antwortet die alte Instanz weiter. Deshalb aus, und den Port vorher prüfen.
    ThreadingHTTPServer.allow_reuse_address = False
    for port in range(PORT_START, PORT_START + 20):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)
        belegt = s.connect_ex(("127.0.0.1", port)) == 0
        s.close()
        if belegt:
            continue
        try:
            return ThreadingHTTPServer(("0.0.0.0", port), Handler), port
        except OSError:
            continue
    raise RuntimeError("Kein freier Port gefunden (8000–8019).")


def laeuft_schon():
    """Läuft die App bereits? Dann nur den Browser öffnen statt ein zweites Mal starten."""
    import urllib.request
    for port in range(PORT_START, PORT_START + 20):
        # Erst schnell schauen, ob überhaupt etwas auf dem Port lauscht
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)
        offen = s.connect_ex(("127.0.0.1", port)) == 0
        s.close()
        if not offen:
            if port == PORT_START:
                return None   # 8000 ist frei, also läuft die App nicht (sie nimmt immer den ersten freien Port)
            continue
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/daten", timeout=1) as r:
                if b'"kategorien"' in r.read(200000):
                    return port
        except Exception:
            continue
    return None


def sprachen_bericht(daten):
    """Zeigt, wie weit die einzelnen Sprachen übersetzt sind."""
    if sprachen.anbieter_fehlt():
        print("Hinweis: In sprachen.py steht bei ANBIETER noch ein Platzhalter.")
        print("  Vor einer Veröffentlichung dort Name, Anschrift und E-Mail eintragen –")
        print("  sonst sind Impressum und Datenschutzerklärung unvollständig.")
    if sprachen.ustidnr_fehlt():
        print("Hinweis: Im Impressum (ANBIETER in sprachen.py) fehlt die USt-IdNr.")
        print("  Sie kommt per Post vom Bundeszentralamt für Steuern – beantragt am")
        print("  14.09.2026 über den ELSTER-Fragebogen. Sobald der Brief da ist,")
        print("  gehört sie hinein: § 5 Abs. 1 Nr. 6 DDG verlangt sie, sobald man")
        print("  eine hat. Vorher fehlt nichts.")
    namen = ", ".join(f"{s['name']} ({s['code']})" for s in sprachen.SPRACHEN)
    print(f"Sprachen: {namen}")
    for s in sprachen.SPRACHEN:
        code = s["code"]
        if code == sprachen.GRUNDSPRACHE:
            continue
        fehlt_ui = len(sprachen.fehlende_texte(code))
        fertig, gesamt = uebersetzungen.stand(daten, code)
        prozent = round(fertig / gesamt * 100) if gesamt else 100
        hinweis = "vollständig" if not fehlt_ui else f"{fehlt_ui} Texte fehlen"
        print(f"  {code}: Oberfläche {hinweis} · Lerninhalte {fertig} von {gesamt} ({prozent} %)")
    print("  Arbeitsliste für eine Sprache schreiben:  start.py --fehlende en")


def arbeitsliste(code):
    """Schreibt fehlende_<code>.txt: alles, was in dieser Sprache noch fehlt,
    schon im Format von uebersetzungen.py. Zum Ausfüllen und Hineinkopieren."""
    daten = lade_daten(sprachen.GRUNDSPRACHE)
    f = uebersetzungen.fehlende(daten, code)
    woerter, _ = uebersetzungen.sammle(daten)
    ziel = os.path.join(ORDNER, f"fehlende_{code}.txt")
    with open(ziel, "w", encoding="utf-8") as datei:
        datei.write(f"# Noch nicht uebersetzt: {code}\n")
        datei.write("# Rechts hinter dem Doppelpunkt die Uebersetzung eintragen\n")
        datei.write("# und den Block nach uebersetzungen.py kopieren.\n\n")
        datei.write('"woerter": {\n')
        for bs in f["woerter"]:
            datei.write('    %r: "",   # deutsch: %s\n' % (bs, woerter.get(bs, "")))
        datei.write("},\n\n")
        datei.write('"texte": {\n')
        for text in f["texte"]:
            datei.write('    %r: "",\n' % text)
        datei.write("},\n")
    print(f"{len(f['woerter'])} Wörter und {len(f['texte'])} Texte fehlen.")
    print(f"Arbeitsliste geschrieben: {ziel}")


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--fehlende":
        return arbeitsliste(sys.argv[2])

    print("=" * 60)
    print("  Zmaj  –  Bosnisch lernen")
    print("=" * 60)

    port = laeuft_schon()
    if port:
        print(f"Die App läuft schon auf http://localhost:{port} – öffne nur den Browser.")
        oeffne_browser(f"http://localhost:{port}")
        return
    os.makedirs(AUDIO_ORDNER, exist_ok=True)
    profile_vorbereiten()

    # Gelöschte Konten, deren Schonfrist abgelaufen ist, endgültig entfernen
    weg = aufraeumen_geloeschte(schweigend=False)
    if weg:
        print(f"{weg} gelöschte Konten endgültig entfernt (Frist: {GELOESCHT_TAGE} Tage).")
    aufraeumen_im_hintergrund()

    daten = lade_daten()
    anzahl = sum(len(k["words"]) for k in daten["kategorien"])
    print(f"Vokabeln geladen: {len(daten['kategorien'])} Levels, "
          f"{anzahl} Wörter, {len(daten['saetze'])} Lückentexte")
    sektion_namen = {s["id"]: s["label"] for s in daten.get("sektionen", [])}
    letzte = None
    for nr, kat in enumerate(daten["kategorien"], start=1):
        if kat.get("sektion") != letzte:
            letzte = kat.get("sektion")
            print(f"\n{sektion_namen.get(letzte, letzte)}")
        print(f"  Level {nr:2d}  {kat['label']:<28} {len(kat['words']):3d} Wörter")
    print()

    print(f"Grammatik-Lektionen: {len(daten['grammatik'])}, Geschichten: {len(daten['geschichten'])}")
    sprachen_bericht(daten)
    probleme = pruefe_vokabeln(daten)
    if probleme:
        print("\nHinweise zu den Inhaltsdateien:")
        for p in probleme:
            print("  -", p)
    else:
        print("Inhaltsdateien sehen gut aus.")
    fehlt = fehlende_woerter(daten)
    if fehlt:
        print("Wörter in Geschichten ohne Eintrag im WOERTERBUCH (beim Antippen fehlt die Übersetzung):")
        for gid, woerter in fehlt.items():
            print(f"  - {gid}: {', '.join(sorted(woerter))}")

    server, port = starte_server()
    url_pc = f"http://localhost:{port}"
    ip = lokale_ip()

    print()
    print(f"Am PC:     {url_pc}")
    if ip:
        print(f"Am Handy:  http://{ip}:{port}   (gleiches WLAN)")
    print()
    print("Beenden: Knopf „Beenden“ unten in der App, Stop in Thonny oder Strg+C.")
    print("-" * 60)

    aufnahmen = eigene_aufnahmen()
    print(f"Eigene Aufnahmen in web/audio: {len(aufnahmen)}" + ("" if aufnahmen else "  (noch keine – Computerstimme wird benutzt)"))
    threading.Timer(0.6, lambda: oeffne_browser(url_pc)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("Server beendet.")


if __name__ == "__main__":
    main()
