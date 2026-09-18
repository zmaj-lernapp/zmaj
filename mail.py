# -*- coding: utf-8 -*-
"""
mail.py  –  E-Mails verschicken (Bestätigung und Passwort vergessen)

Zwei Betriebsarten
------------------
**Testbetrieb** (solange keine Zugangsdaten hinterlegt sind): Die Mail wird
nicht verschickt, sondern in die Datei `postausgang.txt` im Projektordner
geschrieben und in der Konsole angezeigt. So kann man alles ausprobieren,
ohne einen Mailserver zu haben. Den Link zum Bestätigen einfach von dort
kopieren.

**Echtbetrieb**: Sobald `mail_zugang.json` im Projektordner liegt, geht die
Mail wirklich raus. Die Datei sieht so aus:

    {
      "server":   "smtp.gmail.com",
      "port":     587,
      "benutzer": "deine.adresse@gmail.com",
      "passwort": "das-app-passwort-von-google",
      "absender": "Zmaj <deine.adresse@gmail.com>"
    }

Bei Gmail braucht es ein **App-Passwort** (Google-Konto → Sicherheit →
Bestätigung in zwei Schritten → App-Passwörter). Das normale Kontopasswort
funktioniert nicht.

`mail_zugang.json` enthält ein Passwort. Nicht weitergeben und nicht mit
in ein öffentliches Verzeichnis legen.

Es werden nur Bausteine benutzt, die Python schon mitbringt.
"""

import json
import os
import re
import smtplib
import ssl
import threading
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid, parseaddr

ORDNER = os.path.dirname(os.path.abspath(__file__))
ZUGANG_DATEI = os.path.join(ORDNER, "mail_zugang.json")
POSTAUSGANG = os.path.join(ORDNER, "postausgang.txt")

_sperre = threading.Lock()

# Grobe Prüfung: etwas@etwas.endung, keine Leerzeichen, nicht zu lang.
# Streng genug für Tippfehler, locker genug für echte Adressen.
_ADRESSE = re.compile(r"^[^@\s]{1,64}@[^@\s.]+(\.[^@\s.]+)+$")


def adresse_sauber(adresse):
    """Kleingeschrieben und ohne Rand-Leerzeichen. Wirft ValueError, wenn
    das keine E-Mail-Adresse sein kann."""
    a = str(adresse or "").strip().lower()
    if not a:
        raise ValueError("email_fehlt")
    if len(a) > 254 or not _ADRESSE.match(a):
        raise ValueError("email_ungueltig")
    return a


def zugang():
    """Die Zugangsdaten aus mail_zugang.json, oder None im Testbetrieb."""
    try:
        with open(ZUGANG_DATEI, "r", encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or not d.get("server") or not d.get("benutzer"):
        return None

    # Noch die Platzhalter aus der Beispieldatei drin? Dann lieber weiter
    # im Testbetrieb, statt bei jedem Versand in einen Fehler zu laufen.
    alles = " ".join(str(d.get(k, "")) for k in ("server", "benutzer", "passwort"))
    if "DEINE" in alles.upper() or "HIER" in alles.upper() or "@beispiel" in alles.lower():
        print("mail_zugang.json enthält noch die Platzhalter – weiter im Testbetrieb.")
        return None

    # Google zeigt das App-Passwort als "abcd efgh ijkl mnop". Die
    # Leerzeichen gehören nicht dazu, also raus damit.
    d = dict(d)
    d["passwort"] = str(d.get("passwort", "")).replace(" ", "")
    return d


def echt_betrieb():
    return zugang() is not None


def _in_postausgang(an, betreff, text):
    """Testbetrieb: Mail in eine Datei schreiben statt zu verschicken."""
    strich = "=" * 68
    block = "%s\nAn:      %s\nBetreff: %s\n%s\n%s\n\n" % (strich, an, betreff, strich, text)
    with _sperre:
        try:
            with open(POSTAUSGANG, "a", encoding="utf-8") as f:
                f.write(block)
        except OSError:
            pass
    print("\n[Mail nicht verschickt - Testbetrieb. Steht in postausgang.txt]")
    print(block)


def sende(an, betreff, text, antwort_an=None):
    """Verschickt eine Mail. Gibt True zurück, wenn sie wirklich rausging.

    antwort_an: Adresse für "Antworten an". Beim Feedback steht dort die
    Adresse des Nutzers – dann genügt ein Klick auf Antworten.

    Wirft nie. Wenn der Versand scheitert, landet die Mail im Postausgang
    und in der Konsole – dann kann man den Link von Hand weitergeben,
    statt dass die Anmeldung ganz stehen bleibt.
    """
    an = adresse_sauber(an)
    daten = zugang()
    if not daten:
        _in_postausgang(an, betreff, text)
        return False

    absender = daten.get("absender") or daten["benutzer"]
    if not parseaddr(absender)[1]:
        absender = formataddr(("Zmaj", daten["benutzer"]))

    nachricht = EmailMessage()
    nachricht["From"] = absender
    nachricht["To"] = an
    nachricht["Subject"] = betreff
    # Datum und Message-ID gehören zu jeder ordentlichen Mail. Fehlen sie,
    # werten manche Filter das als Zeichen für Werbemüll. Die meisten
    # Mailserver setzen sie zwar selbst ein, aber verlassen wir uns nicht
    # darauf. Der Name hinter dem @ kommt aus der Absenderadresse.
    nachricht["Date"] = formatdate(localtime=True)
    bereich = parseaddr(absender)[1].partition("@")[2] or None
    nachricht["Message-ID"] = make_msgid(domain=bereich)
    if antwort_an and parseaddr(antwort_an)[1]:
        nachricht["Reply-To"] = antwort_an
    nachricht.set_content(text)

    try:
        port = int(daten.get("port", 587))
        if port == 465:
            with smtplib.SMTP_SSL(daten["server"], port, timeout=20,
                                  context=ssl.create_default_context()) as s:
                s.login(daten["benutzer"], daten.get("passwort", ""))
                s.send_message(nachricht)
        else:
            with smtplib.SMTP(daten["server"], port, timeout=20) as s:
                s.starttls(context=ssl.create_default_context())
                s.login(daten["benutzer"], daten.get("passwort", ""))
                s.send_message(nachricht)
        print("Mail an %s verschickt: %s" % (an, betreff))
        return True
    except (smtplib.SMTPException, OSError, ssl.SSLError) as e:
        print("Mail an %s ging nicht raus (%s). Sie steht in postausgang.txt." % (an, e))
        _in_postausgang(an, betreff, text)
        return False


# ---------------------------------------------------------------------------
# Die beiden Mails, die die App verschickt
# ---------------------------------------------------------------------------
def sende_bestaetigung(an, name, link, texte):
    """texte: die Oberflächentexte der Sprache, die der Nutzer gewählt hat."""
    betreff = texte.get("mail.bestaetigen_betreff", "Zmaj – E-Mail bestätigen")
    vorlage = texte.get("mail.bestaetigen_text", "")
    return sende(an, betreff, vorlage.format(name=name, link=link))


def sende_passwort_link(an, name, link, texte):
    betreff = texte.get("mail.vergessen_betreff", "Zmaj – neues Passwort")
    vorlage = texte.get("mail.vergessen_text", "")
    return sende(an, betreff, vorlage.format(name=name, link=link))


def betreiber_adresse():
    """An diese Adresse geht das Feedback: das Postfach der App selbst.
    Im Testbetrieb gibt es keine – dann landet alles im Postausgang."""
    daten = zugang()
    return daten.get("benutzer") if daten else None


def sende_feedback(name, adresse, sprache, text):
    """Schickt eine Rückmeldung aus der App an das Postfach der App.

    `adresse` ist die E-Mail des Nutzers. Sie steht als "Antworten an" in
    der Mail, damit eine Antwort direkt bei ihm landet.
    """
    an = betreiber_adresse() or "postausgang@zmaj"
    betreff = "Zmaj Feedback von %s" % (name or "unbekannt")
    körper = (
        "Neue Rückmeldung aus der App.\n\n"
        "Von:     %s\n"
        "E-Mail:  %s\n"
        "Sprache: %s\n"
        "%s\n\n"
        "%s\n"
    ) % (name or "-", adresse or "-", sprache or "-", "-" * 60, text)
    try:
        return sende(an, betreff, körper, antwort_an=adresse)
    except ValueError:
        # Testbetrieb ohne gültige Adresse: nur in den Postausgang legen
        _in_postausgang(an, betreff, körper)
        return False
