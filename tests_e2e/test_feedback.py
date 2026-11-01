# -*- coding: utf-8 -*-
"""Feedback ueber das Kontaktformular (01.11.2026) - im echten Browser.

Ajdin beim Test der 1.2: "wo ist das kontaktformular ist das das mit dem
feedback" - auf die Rueckfrage, ob Feedback in den Einstellungen darueber
gehen soll statt ueber das Mailprogramm: "Übers Formular". Text eintippen,
Senden, fertig; die Nachricht landet wie die vom Webformular in seinem
Gmail (nachrichten/{uid}, kontakt_weiterleitung.gs).

Firebase beantwortet firebase_attrappe.py, und zwar nach den Regeln aus
firestore.rules: anlegen nur mit einer anonymen Anmeldung unter der eigenen
uid, nur text, antwort, sprache und die Zeit vom Server. Kein Byte verlaesst
den Rechner.

Geprueft wird:
  - Angemeldet: anonym anmelden, genau eine Nachricht mit der Adresse des
    Kontos, die anonyme Anmeldung wieder weg, das Konto unberuehrt. Das
    Feld ist danach leer, die App dankt, kein Mailprogramm.
  - Derselbe Weg fuer den Vorschlag nach der Bewertungsfrage.
  - Rueckfall aufs Mailprogramm, wenn Firestore ablehnt, ohne Netz und
    wenn die Adresse des Kontos nicht zur Regel passt - der Text bleibt.
  - Noch nicht angemeldet und ohne Cloud (Quelle, Web-Fassung): wie
    bisher das Mailprogramm, keine Anfrage an Firebase.
"""
from firebase_attrappe import COMMIT, Attrappe, wege
from test_anmeldung import _gelernt, _mail_anmelden, _starten, _t

SIGNUP = "identitytoolkit.googleapis.com/v1/accounts:signUp"
DELETE = "identitytoolkit.googleapis.com/v1/accounts:delete"
ADRESSE = "ich@probe.example"
ZMAJ_MAIL = "zmaj.lernapp@gmail.com"


def _angemeldet(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    attrappe.anonym_neu = True
    attrappe.konto_anlegen(ADRESSE, "geheim-123")
    _starten(seite, cloud_html, stand=_gelernt(heute_stand), attrappe=attrappe)
    _mail_anmelden(seite, ADRESSE, "geheim-123")
    assert seite.js("() => cloudMerker().email") == ADRESSE
    seite.js("() => { showSettings(); }")
    attrappe.anfragen.clear()
    return attrappe


def _senden(seite, text):
    seite.page.fill("#fbText", text)
    seite.page.click("#fbSend")
    seite.page.wait_for_function("() => !feedbackLaeuft && document.getElementById('fbNote').textContent !== ''"
                                 " && document.getElementById('fbNote').textContent !== t('set.feedback_sendet')")


def _mails(seite):
    """Die mailto:-Aufrufe bisher - Chromium meldet sie als Anfrage."""
    return [u for u in seite.fremd if u.startswith("mailto:" + ZMAJ_MAIL + "?")]


def _per_mail(seite, n=1, notiz="fbNote"):
    """Ob das Mailprogramm aufging, zum n-ten Mal: feedbackPerMail() ruft
    mailto: auf, schreibt die Adresse in die Meldung und haengt den Knopf
    zum Kopieren an. Die Anfrage meldet Chromium etwas spaeter als die
    Meldung dasteht - deshalb kurz warten."""
    for _ in range(80):
        if len(_mails(seite)) >= n:
            break
        seite.page.wait_for_timeout(25)
    return len(_mails(seite)) == n and seite.js("""([id, soll]) => { const n = document.getElementById(id);
        return n.textContent.startsWith(soll) && !!n.querySelector('button'); }""",
                                            [notiz, _t(seite, "set.feedback_mail", {"mail": ZMAJ_MAIL})])


def test_feedback_geht_ueber_das_formular(seite, heute_stand, cloud_html):
    attrappe = _angemeldet(seite, heute_stand, cloud_html)
    vorher = seite.js("() => cloudMerker()")
    _senden(seite, "  Im Level Familie fehlt ein Wort.  ")
    assert seite.js("() => [document.getElementById('fbNote').textContent,"
                    " document.getElementById('fbText').value, document.getElementById('fbSend').disabled]") \
        == [_t(seite, "set.feedback_danke"), "", False]
    # Pruefbericht 01.11.2026: Die Meldung sagt ein Screenreader an, und der
    # Fokus steht nach dem Senden wieder auf dem Knopf.
    assert seite.js("() => [document.getElementById('fbNote').getAttribute('role'),"
                    " document.activeElement && document.activeElement.id]") == ["status", "fbSend"]
    seite.page.wait_for_timeout(300)
    assert _mails(seite) == [] and not seite.js("() => !!document.querySelector('#fbNote button')")
    # Genau eine Nachricht, mit der Adresse des Kontos und der Sprache der App.
    assert list(attrappe.nachrichten.values()) == [
        {"text": "Im Level Familie fehlt ein Wort.", "antwort": ADRESSE, "sprache": "de"}]
    anonym = next(iter(attrappe.nachrichten))
    assert wege(attrappe) == [("POST", SIGNUP), ("POST", COMMIT), ("POST", DELETE)]
    assert attrappe.anfragen[1][2] == "Bearer " + attrappe.anonym_ausweis[anonym]
    # Die anonyme Anmeldung ist wieder weg, das Konto und die Anmeldung bleiben.
    assert attrappe.anonyme == set()
    assert not attrappe.konto_weg and ADRESSE in attrappe.konten
    assert seite.js("() => cloudMerker()") == vorher
    # Danach schreibt der Abgleich weiter mit dem Ausweis des Kontos - die
    # anonyme Anmeldung hat ihn nicht ueberschrieben.
    uid = attrappe.konten[ADRESSE]["uid"]
    attrappe.anfragen.clear()
    assert seite.js("async () => { known.add('probe:nach-feedback'); return await cloudAbgleich('abmelden'); }") \
        == "gespeichert"
    assert [w[0] for w in wege(attrappe)] == ["GET", "PATCH"]
    assert "probe:nach-feedback" in attrappe.doks[uid]["daten"]["stringValue"]
    assert seite.fehler == []


def test_vorschlag_nach_der_bewertungsfrage_ebenso(seite, heute_stand, cloud_html):
    attrappe = _angemeldet(seite, heute_stand, cloud_html)
    seite.js("() => { showHome(); zeigeVorschlag(); }")
    seite.page.fill("#bwText", "Mehr Saetze zum Hoeren, bitte.")
    seite.page.click("#bwSenden")
    seite.page.wait_for_function("t => document.getElementById('bwNote').textContent === t",
                                 arg=_t(seite, "set.feedback_danke"))
    assert seite.js("() => [document.getElementById('bwText').value, document.getElementById('bwZu').textContent,"
                    " document.getElementById('bwNote').getAttribute('role')]") \
        == ["", _t(seite, "task.weiter"), "status"]
    assert [n["text"] for n in attrappe.nachrichten.values()] == ["Mehr Saetze zum Hoeren, bitte."]
    assert attrappe.anonyme == set()
    assert seite.fehler == []


def test_rueckfall_aufs_mailprogramm(seite, heute_stand, cloud_html):
    attrappe = _angemeldet(seite, heute_stand, cloud_html)
    text = "Das Wort fuer Tante stimmt nicht."

    # Firestore lehnt ab (wie eine Regel, die nicht passt): Mailprogramm,
    # der Text bleibt stehen, die anonyme Anmeldung ist trotzdem weg.
    attrappe.nachricht_fehler = 403
    _senden(seite, text)
    assert _per_mail(seite, 1)
    assert seite.js("() => document.getElementById('fbText').value") == text
    assert wege(attrappe) == [("POST", SIGNUP), ("POST", COMMIT), ("POST", DELETE)]
    assert attrappe.nachrichten == {} and attrappe.anonyme == set()


    # Kein Netz: dasselbe.
    attrappe.nachricht_fehler = None
    attrappe.abbruch = True
    attrappe.anfragen.clear()
    seite.js("() => { document.getElementById('fbNote').textContent = ''; }")
    _senden(seite, text)
    assert _per_mail(seite, 2)
    assert [a for a, _, _ in attrappe.anfragen] == ["ABBRUCH"]

    # Eine Adresse, die die Regel nicht annaehme (Umlaut): gar nicht erst
    # versuchen, gleich das Mailprogramm.
    attrappe.abbruch = False
    attrappe.anfragen.clear()
    seite.js("""() => { const m = cloudMerker(); m.email = 'jürgen@probe.example';
                        localStorage.setItem('zmaj_cloud', JSON.stringify(m));
                        document.getElementById('fbNote').textContent = ''; }""")
    _senden(seite, text)
    assert _per_mail(seite, 3)
    assert attrappe.anfragen == [] and attrappe.nachrichten == {}
    assert seite.fehler == []


def test_ohne_anmeldung_wie_bisher(seite, heute_stand, cloud_html):
    """Handy-App, aber noch nicht angemeldet: keine Adresse fuer die
    Antwort, also das Mailprogramm - und keine Anfrage an Firebase."""
    attrappe = _starten(seite, cloud_html, stand=heute_stand())
    seite.js("() => { showSettings(); }")
    assert seite.js("() => cloudModus() && !cloudMerker()")
    _senden(seite, "Hallo")
    assert _per_mail(seite)
    assert attrappe.anfragen == []
    assert seite.fehler == []


def test_ohne_cloud_wie_bisher(seite, heute_stand):
    """Die Quelle (CLOUD_AN = false), wie die Web-Fassung: Mailprogramm."""
    seite.starten(stand=heute_stand())
    seite.js("() => { showSettings(); }")
    _senden(seite, "Hallo")
    assert _per_mail(seite)
    assert len(_mails(seite)) == 1 and len(seite.fremd) == 1 and seite.fehler == []
