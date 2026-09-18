# -*- coding: utf-8 -*-
"""
konten.py  –  Anmeldung mit Name und Passwort

Diese Datei kümmert sich nur um Konten und Sitzungen. Der Fortschritt
selbst liegt weiter in fortschritt_<Name>.json, genau wie vorher.

Wie das Passwort gespeichert wird
---------------------------------
Nie im Klartext. Aus dem Passwort wird mit pbkdf2 eine lange Zahlenreihe
gerechnet, und nur die steht in der Datei. Aus ihr kann man das Passwort
nicht zurückrechnen. Jedes Konto bekommt dazu ein eigenes Zufallssalz,
damit zwei gleiche Passwörter verschieden aussehen.

    passwort  +  salz  --pbkdf2 200000 Runden-->  hash

Beim Anmelden wird dieselbe Rechnung gemacht und das Ergebnis verglichen.

Wie die Anmeldung gemerkt wird
------------------------------
Nach dem Anmelden bekommt der Browser ein zufälliges Kennwort für die
Sitzung ("Token") als Cookie. Das Cookie ist HttpOnly: JavaScript auf der
Seite kann es nicht lesen, nur der Browser schickt es mit. Die Sitzungen
stehen in sitzungen.json, damit ein Neustart des Servers niemanden
hinauswirft.

Es werden nur Bausteine benutzt, die Python schon mitbringt.
"""

import hashlib
import hmac
import json
import os
import secrets
import threading
import time

# ---------------------------------------------------------------------------
# Einstellungen
# ---------------------------------------------------------------------------
RUNDEN = 200_000          # pbkdf2-Runden. Mehr = sicherer, aber langsamer.
SALZ_LAENGE = 16          # Bytes
PASSWORT_MIN = 10         # so viele Zeichen muss ein Passwort mindestens haben
PASSWORT_MAX = 128        # länger nimmt der Server nicht an
SITZUNG_TAGE = 90         # "Angemeldet bleiben": so lange hält die Anmeldung
FEHLVERSUCHE_MAX = 10     # danach ist das Konto kurz gesperrt
SPERRE_MINUTEN = 15       # so lange

NAME_MIN = 3              # kürzere Benutzernamen nimmt der Server nicht an
NAME_MAX = 20
CODE_STUNDEN_MAIL = 48    # so lange gilt der Link aus der Bestätigungsmail
CODE_STUNDEN_PW = 2       # so lange der Link zum Zurücksetzen des Passworts

_sperre = threading.Lock()
_fehlversuche = {}        # {name: [zeitpunkt, ...]} – nur im Arbeitsspeicher


# ---------------------------------------------------------------------------
# Passwörter
# ---------------------------------------------------------------------------
def passwort_maengel(passwort):
    """Welche Regeln verletzt dieses Passwort? Liste von Kürzeln, leer = alles gut.

    Die Oberfläche zeigt dieselben Regeln beim Tippen an, damit niemand
    raten muss. Verbindlich ist trotzdem immer diese Prüfung hier.
    """
    p = passwort if isinstance(passwort, str) else ""
    maengel = []
    if len(p) > PASSWORT_MAX:
        return ["passwort_lang"]
    if any(ch.isspace() for ch in p):
        maengel.append("passwort_leerzeichen")
    if len(p) < PASSWORT_MIN:
        maengel.append("passwort_kurz")
    if not any(ch.isupper() for ch in p):
        maengel.append("passwort_gross")
    if not any(ch.islower() for ch in p):
        maengel.append("passwort_klein")
    if not any(ch.isdigit() for ch in p):
        maengel.append("passwort_zahl")
    # Sonderzeichen: alles, was weder Buchstabe noch Ziffer ist
    if not any(not ch.isalnum() for ch in p if not ch.isspace()):
        maengel.append("passwort_zeichen")
    return maengel


def pruefe_name(name):
    """Benutzername: 3 bis 20 Zeichen, keine Leerzeichen.

    Erlaubt sind Buchstaben (auch ä, ć, š …), Ziffern, Bindestrich,
    Unterstrich und Punkt. Der Name wird auch zum Dateinamen, deshalb
    fliegt alles andere raus.
    """
    n = str(name or "").strip()
    if not n:
        raise ValueError("name_fehlt")
    if any(ch.isspace() for ch in n):
        raise ValueError("name_leerzeichen")
    if len(n) < NAME_MIN:
        raise ValueError("name_kurz")
    if len(n) > NAME_MAX:
        raise ValueError("name_lang")
    if not all(ch.isalnum() or ch in "-_." for ch in n):
        raise ValueError("name_zeichen")
    if not any(ch.isalnum() for ch in n):
        raise ValueError("name_zeichen")     # z. B. "..." wäre ein übler Dateiname
    return n


def pruefe_passwort_regeln(passwort):
    """Wirft ValueError mit dem ersten Mangel, wenn das Passwort nicht taugt."""
    if not isinstance(passwort, str):
        raise ValueError("passwort_kurz")
    maengel = passwort_maengel(passwort)
    if maengel:
        raise ValueError(maengel[0])
    return passwort


def neuer_hash(passwort):
    """{'salz': ..., 'hash': ..., 'runden': ...} – so wandert es in die Profildatei."""
    pruefe_passwort_regeln(passwort)
    salz = secrets.token_bytes(SALZ_LAENGE)
    roh = hashlib.pbkdf2_hmac("sha256", passwort.encode("utf-8"), salz, RUNDEN)
    return {"salz": salz.hex(), "hash": roh.hex(), "runden": RUNDEN}


def passt(passwort, gespeichert):
    """True, wenn das Passwort zum gespeicherten Hash gehört."""
    if not isinstance(gespeichert, dict) or not gespeichert.get("hash"):
        return False
    try:
        salz = bytes.fromhex(gespeichert["salz"])
        runden = int(gespeichert.get("runden", RUNDEN))
        soll = bytes.fromhex(gespeichert["hash"])
    except (KeyError, ValueError, TypeError):
        return False
    ist = hashlib.pbkdf2_hmac("sha256", str(passwort).encode("utf-8"), salz, runden)
    # compare_digest statt ==, damit die Rechenzeit nichts über das Passwort verrät
    return hmac.compare_digest(ist, soll)


def hat_passwort(profil):
    """Hat dieses Profil schon ein Passwort? (Die alten Profile haben keins.)"""
    p = profil.get("passwort") if isinstance(profil, dict) else None
    return isinstance(p, dict) and bool(p.get("hash"))


# ---------------------------------------------------------------------------
# Sperre gegen Passwort-Raten
# ---------------------------------------------------------------------------
def _aufraeumen(name, jetzt):
    grenze = jetzt - SPERRE_MINUTEN * 60
    _fehlversuche[name] = [t for t in _fehlversuche.get(name, []) if t > grenze]


def gesperrt_bis(name):
    """0, wenn frei. Sonst der Zeitpunkt, ab dem es wieder geht."""
    with _sperre:
        jetzt = time.time()
        _aufraeumen(name, jetzt)
        versuche = _fehlversuche.get(name, [])
        if len(versuche) >= FEHLVERSUCHE_MAX:
            return versuche[0] + SPERRE_MINUTEN * 60
        return 0


def fehlversuch(name):
    with _sperre:
        jetzt = time.time()
        _aufraeumen(name, jetzt)
        _fehlversuche.setdefault(name, []).append(jetzt)


def versuche_zuruecksetzen(name):
    with _sperre:
        _fehlversuche.pop(name, None)


# ---------------------------------------------------------------------------
# Sitzungen
# ---------------------------------------------------------------------------
class Sitzungen:
    """Merkt sich, welcher Token zu welchem Konto gehört."""

    def __init__(self, datei):
        self.datei = datei
        self.sperre = threading.Lock()
        self.daten = self._laden()

    def _laden(self):
        try:
            with open(self.datei, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict):
                jetzt = time.time()
                return {t: v for t, v in d.items()
                        if isinstance(v, dict) and v.get("bis", 0) > jetzt}
        except (OSError, ValueError):
            pass
        return {}

    def _speichern(self):
        try:
            with open(self.datei, "w", encoding="utf-8") as f:
                json.dump(self.daten, f, ensure_ascii=False, indent=2)
            if os.name != "nt":
                os.chmod(self.datei, 0o600)
        except OSError:
            pass

    def anlegen(self, name, bleiben=False):
        """bleiben=True: 90 Tage. Sonst gilt die Sitzung nur für diesen Tag
        und das Cookie verschwindet, sobald der Browser zugeht."""
        token = secrets.token_urlsafe(32)
        dauer = SITZUNG_TAGE * 86400 if bleiben else 86400
        with self.sperre:
            self.daten[token] = {"name": name, "bis": time.time() + dauer,
                                 "bleiben": bool(bleiben)}
            self._speichern()
        return token

    def name_zu(self, token):
        """Zu welchem Konto gehört dieser Token? None, wenn unbekannt oder abgelaufen."""
        if not token:
            return None
        with self.sperre:
            eintrag = self.daten.get(token)
            if not eintrag:
                return None
            if eintrag.get("bis", 0) <= time.time():
                self.daten.pop(token, None)
                self._speichern()
                return None
            return eintrag.get("name")

    def beenden(self, token):
        with self.sperre:
            if self.daten.pop(token, None) is not None:
                self._speichern()

    def alle_beenden(self, name):
        """Nach einer Passwortänderung: alle anderen Geräte abmelden."""
        with self.sperre:
            weg = [t for t, v in self.daten.items() if v.get("name") == name]
            for t in weg:
                self.daten.pop(t, None)
            if weg:
                self._speichern()
            return len(weg)

    def umbenennen(self, alt, neu):
        with self.sperre:
            geaendert = False
            for v in self.daten.values():
                if v.get("name") == alt:
                    v["name"] = neu
                    geaendert = True
            if geaendert:
                self._speichern()


# ---------------------------------------------------------------------------
# Einmal-Codes für die Links in den Mails
# ---------------------------------------------------------------------------
class Codes:
    """Die Links aus den Mails. Ein Code gehört zu einem Konto, hat einen
    Zweck ("mail" oder "pw") und läuft ab.

    Gespeichert wird nur der SHA-256-Abdruck des Codes, nicht der Code
    selbst – wie beim Passwort. Wer die Datei liest, kann damit nichts
    anfangen.
    """

    def __init__(self, datei):
        self.datei = datei
        self.sperre = threading.Lock()
        self.daten = self._laden()

    @staticmethod
    def _abdruck(code):
        return hashlib.sha256(str(code).encode("utf-8")).hexdigest()

    def _laden(self):
        try:
            with open(self.datei, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict):
                jetzt = time.time()
                return {k: v for k, v in d.items()
                        if isinstance(v, dict) and v.get("bis", 0) > jetzt}
        except (OSError, ValueError):
            pass
        return {}

    def _speichern(self):
        try:
            with open(self.datei, "w", encoding="utf-8") as f:
                json.dump(self.daten, f, ensure_ascii=False, indent=2)
            if os.name != "nt":
                os.chmod(self.datei, 0o600)
        except OSError:
            pass

    def neu(self, name, zweck, stunden):
        """Legt einen Code an und gibt ihn im Klartext zurück – einmalig,
        denn gespeichert wird nur der Abdruck."""
        code = secrets.token_urlsafe(24)
        with self.sperre:
            # alte Codes desselben Zwecks für dieses Konto verfallen
            for k in [k for k, v in self.daten.items()
                      if v.get("name") == name and v.get("zweck") == zweck]:
                self.daten.pop(k, None)
            self.daten[self._abdruck(code)] = {
                "name": name, "zweck": zweck, "bis": time.time() + stunden * 3600}
            self._speichern()
        return code

    def pruefe(self, code, zweck):
        """Zu welchem Konto gehört dieser Code? None, wenn ungültig."""
        if not code:
            return None
        with self.sperre:
            eintrag = self.daten.get(self._abdruck(code))
            if not eintrag or eintrag.get("zweck") != zweck:
                return None
            if eintrag.get("bis", 0) <= time.time():
                self.daten.pop(self._abdruck(code), None)
                self._speichern()
                return None
            return eintrag.get("name")

    def verbrauche(self, code, zweck):
        """Wie pruefe, aber der Code gilt danach nicht mehr."""
        name = self.pruefe(code, zweck)
        if name:
            with self.sperre:
                self.daten.pop(self._abdruck(code), None)
                self._speichern()
        return name

    def loesche_fuer(self, name):
        with self.sperre:
            weg = [k for k, v in self.daten.items() if v.get("name") == name]
            for k in weg:
                self.daten.pop(k, None)
            if weg:
                self._speichern()


# ---------------------------------------------------------------------------
# Cookie lesen und schreiben
# ---------------------------------------------------------------------------
COOKIE_NAME = "zmaj_sitzung"


def token_aus_cookie(kopfzeile):
    """Holt den Token aus der Cookie-Zeile des Browsers."""
    if not kopfzeile:
        return None
    for teil in str(kopfzeile).split(";"):
        name, _, wert = teil.strip().partition("=")
        if name == COOKIE_NAME:
            return wert.strip() or None
    return None


def cookie_setzen(token, sicher=False, bleiben=False):
    """Wert für die Set-Cookie-Kopfzeile.

    HttpOnly  – JavaScript kommt nicht heran (Schutz, falls je fremder
                Code auf der Seite landet)
    SameSite  – der Browser schickt es nicht an fremde Seiten
    Secure    – nur über HTTPS; lokal läuft http, deshalb abschaltbar
    Max-Age   – nur mit „Angemeldet bleiben“. Ohne die Zeile wirft der
                Browser das Cookie weg, sobald er geschlossen wird.
    """
    teile = ["%s=%s" % (COOKIE_NAME, token), "Path=/", "HttpOnly", "SameSite=Strict"]
    if bleiben:
        teile.insert(2, "Max-Age=%d" % (SITZUNG_TAGE * 86400))
    if sicher:
        teile.append("Secure")
    return "; ".join(teile)


def cookie_loeschen():
    return "%s=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict" % COOKIE_NAME
