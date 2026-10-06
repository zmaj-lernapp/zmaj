# -*- coding: utf-8 -*-
"""
feedback_holen.py  –  neue Mails an zmaj.lernapp@gmail.com abholen

Fuer die abendliche Feedback-Durchsicht (geplante Aufgabe "zmaj-feedback",
jeden Abend um 20 Uhr, eingerichtet am 01.10.2026). Ajdin: "koennen wir es
so machen, wenn ein Feedback kommt, dass du das direkt siehst und
bearbeitest und gegebenenfalls direkt umsetzt in die neue Version".

Liest nur, markiert nichts als gelesen (BODY.PEEK) und loescht nichts.
Zugang: mail_zugang.json, Vorlage in mail_zugang.BEISPIEL.json. Gebraucht
werden nur "benutzer" und "passwort" (das Gmail-App-Passwort). Frueher
verschickte mail.py damit auch Mails; mail.py ist seit dem 04.10.2026 weg,
die Datei bleibt fuer dieses Skript.

  python feedback_holen.py                neue Mails seit dem letzten Merken
                                          als JSON ausgeben (nichts merken)
  python feedback_holen.py --merken       dasselbe, danach den Stand merken
  python feedback_holen.py --start        nur den Stand auf "jetzt" setzen
  python feedback_holen.py --entwurf DATEI
        legt eine Antwort als ENTWURF in Gmail an - verschickt wird nichts.
        DATEI ist JSON: {"an": ..., "betreff": ..., "text": ...,
                         "antwort_auf": "<Message-ID der Mail>"}

Der Stand liegt in feedback/stand.json. Der Ordner feedback/ steht in der
.gitignore: Mails enthalten Namen und Adressen, die gehoeren nicht nach
GitHub.
"""
import email, email.header, email.utils, html, imaplib, io, json, os, re, sys, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HIER = os.path.dirname(os.path.abspath(__file__))
ORDNER = os.path.join(HIER, "feedback")
STAND = os.path.join(ORDNER, "stand.json")

# Absender, die keine Menschen sind. Google schickt Play-, AdMob- und
# Kontomeldungen, dazu Zustellfehler. Die gehoeren nicht ins Feedback.
MASCHINEN = re.compile(r"(no-?reply|noreply|mailer-daemon|postmaster|notifications?@|"
                       r"@(?:[\w.-]+\.)?(google|googlemail|youtube|github|firebase|admob)\.com$|"
                       r"@accounts\.google\.com$|@payments\.google\.com$|@bestpractices\.dev$)", re.I)


def zugang():
    with io.open(os.path.join(HIER, "mail_zugang.json"), encoding="utf-8") as f:
        z = json.load(f)
    return z["benutzer"], z["passwort"]


def verbinden():
    benutzer, passwort = zugang()
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(benutzer, passwort)
    return m


def dekodiere(wert):
    if not wert:
        return ""
    teile = []
    for stueck, zeichensatz in email.header.decode_header(wert):
        if isinstance(stueck, bytes):
            teile.append(stueck.decode(zeichensatz or "utf-8", errors="replace"))
        else:
            teile.append(stueck)
    return "".join(teile)


def text_aus(nachricht):
    """Der lesbare Text: text/plain bevorzugt, sonst HTML ohne Tags."""
    plain, htm = [], []
    for teil in nachricht.walk() if nachricht.is_multipart() else [nachricht]:
        if teil.get_content_maintype() == "multipart" or teil.get("Content-Disposition", "").startswith("attachment"):
            continue
        roh = teil.get_payload(decode=True)
        if roh is None:
            continue
        s = roh.decode(teil.get_content_charset() or "utf-8", errors="replace")
        (plain if teil.get_content_type() == "text/plain" else htm if teil.get_content_type() == "text/html" else []).append(s)
    if plain:
        s = "\n".join(plain)
    else:
        s = re.sub(r"(?is)<(script|style).*?</\1>", "", "\n".join(htm))
        s = html.unescape(re.sub(r"(?s)<[^>]+>", " ", s))
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n\s*\n+", "\n\n", s).strip()
    return s[:6000]


def stand_lesen():
    try:
        with io.open(STAND, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def stand_schreiben(uidvalidity, letzte):
    os.makedirs(ORDNER, exist_ok=True)
    with io.open(STAND, "w", encoding="utf-8") as f:
        json.dump({"uidvalidity": uidvalidity, "letzte_uid": letzte,
                   "gemerkt": time.strftime("%Y-%m-%d %H:%M")}, f, ensure_ascii=False, indent=1)


def posteingang(m):
    typ, daten = m.select("INBOX", readonly=True)
    if typ != "OK":
        raise SystemExit("INBOX nicht lesbar")
    typ, d = m.response("UIDVALIDITY")
    uidvalidity = int(d[0]) if d and d[0] else 0
    typ, d = m.uid("search", None, "ALL")
    uids = [int(x) for x in (d[0] or b"").split()]
    return uidvalidity, uids


def abholen(merken):
    m = verbinden()
    try:
        uidvalidity, uids = posteingang(m)
        st = stand_lesen()
        if st.get("uidvalidity") != uidvalidity:
            # Erster Lauf oder Gmail hat neu nummeriert: nichts Altes
            # aufrollen, nur den Stand setzen.
            stand_schreiben(uidvalidity, max(uids or [0]))
            print(json.dumps({"hinweis": "Stand neu gesetzt, keine alten Mails", "neu": []}, ensure_ascii=False))
            return
        letzte = st.get("letzte_uid", 0)
        neu, maschinen = [], 0
        for uid in [u for u in uids if u > letzte]:
            typ, d = m.uid("fetch", str(uid), "(BODY.PEEK[])")
            if typ != "OK" or not d or not isinstance(d[0], tuple):
                continue
            n = email.message_from_bytes(d[0][1])
            name, adresse = email.utils.parseaddr(dekodiere(n.get("From")))
            if MASCHINEN.search(adresse or ""):
                maschinen += 1
                continue
            neu.append({"uid": uid, "von_name": name, "von": adresse,
                        "betreff": dekodiere(n.get("Subject")), "datum": n.get("Date", ""),
                        "message_id": n.get("Message-ID", ""), "text": text_aus(n)})
        print(json.dumps({"neu": neu, "maschinen_uebersprungen": maschinen}, ensure_ascii=False, indent=1))
        if merken and uids:
            stand_schreiben(uidvalidity, max(uids))
    finally:
        try:
            m.logout()
        except Exception:
            pass


def entwurfsordner(m):
    typ, liste = m.list()
    for zeile in liste or []:
        z = zeile.decode("utf-8", errors="replace")
        if "\\Drafts" in z:
            return z.rsplit(' "/" ', 1)[-1].strip()
    return '"[Gmail]/Drafts"'


def entwurf(datei):
    from email.mime.text import MIMEText
    with io.open(datei, encoding="utf-8") as f:
        e = json.load(f)
    benutzer, _ = zugang()
    msg = MIMEText(e["text"], "plain", "utf-8")
    msg["From"] = "Zmaj <%s>" % benutzer
    msg["To"] = e["an"]
    msg["Subject"] = e["betreff"]
    msg["Date"] = email.utils.formatdate(localtime=True)
    if e.get("antwort_auf"):
        msg["In-Reply-To"] = e["antwort_auf"]
        msg["References"] = e["antwort_auf"]
    m = verbinden()
    try:
        ordner = entwurfsordner(m)
        typ, d = m.append(ordner, "(\\Draft)", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        print("Entwurf angelegt in %s: %s" % (ordner, typ))
    finally:
        m.logout()


if __name__ == "__main__":
    if "--entwurf" in sys.argv:
        entwurf(sys.argv[sys.argv.index("--entwurf") + 1])
    elif "--start" in sys.argv:
        m = verbinden()
        uidvalidity, uids = posteingang(m)
        m.logout()
        stand_schreiben(uidvalidity, max(uids or [0]))
        print("Stand gesetzt: %d Mails im Posteingang, ab jetzt zaehlt nur Neues." % len(uids))
    else:
        abholen("--merken" in sys.argv)
