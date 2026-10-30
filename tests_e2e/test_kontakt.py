# -*- coding: utf-8 -*-
"""Das Kontaktformular im echten Browser (28.10.2026, Weg A).

kontakt.html kommt aus seite_bauen.py, gebaut mit Schalter an und
erfundenem Zugang, ausgeliefert vom Dateiserver der Suite. Firebase
beantwortet der Test selbst (page.route) - kein Byte verlaesst den
Rechner. Weil die Content-Security-Policy im Browser vor page.route
greift, prueft jeder Test auch sie mit: Was sie sperrte, kaeme hier nie
an und stuende als Fehler in der Konsole.

Geprueft wird:
  - Absenden: anonym anlegen, genau ein Dokument nachrichten/{uid} mit
    text, antwort, sprache und der Zeit vom Server, danach die Anmeldung
    loeschen. Die Seite dankt in ihrer Sprache und leert das Formular.
  - In einer anderen Sprache (Englisch) dasselbe mit sprache "en".
  - Fallenfeld gefuellt: keine einzige Anfrage, trotzdem "Danke".
  - Kein Netz: "Keine Verbindung". Firestore lehnt ab: "hat nicht
    geklappt", und die anonyme Anmeldung wird trotzdem geloescht. Der Text
    bleibt in beiden Faellen stehen.
  - Eine Adresse ohne Punkt im Namen haelt schon der Browser auf.
  - Gegenprobe: Ein Abruf an eine andere Adresse sperrt die Policy.

Dazu die Weiterleitung kontakt_weiterleitung.gs (Apps Script). Sie laeuft
hier in einer leeren Seite desselben Browsers, die Google-Dienste
(MailApp, UrlFetchApp, PropertiesService ...) sind nachgebaut
(WELT unten). Geprueft wird (Pruefbericht 28.10.2026):
  - Normalfall: Mail an das eigene Postfach, "Antworten an" die Adresse,
    danach ist das Dokument weg.
  - Eine Nachricht, die sich nie verschicken laesst, haelt die anderen nicht
    auf; nach drei Laeufen geht ein Hinweis ohne Inhalt raus, dann ist sie
    weg.
  - Lehnt MailApp nur "Antworten an" ab, kommt die Nachricht im selben Lauf
    als Ersatz ohne "Antworten an" an.
  - Adressen mit Steuer-, Leer- oder Nicht-ASCII-Zeichen kommen nie in
    "Antworten an".
  - Tageskontingent: die letzte Mail meldet den Stau, einmal am Tag; am
    naechsten Tag geht der Rest raus.
  - Scheitert das Loeschen, geht die Nachricht beim naechsten Lauf nicht
    ein zweites Mal raus.
"""
import functools
import http.server
import json
import re
import threading
import urllib.parse

import pytest
from conftest import Dateiserver
from firebase_attrappe import CLIENT, PROJEKT, SCHLUESSEL

playwright = pytest.importorskip("playwright.sync_api")

GOOGLE = re.compile(r"^https://[^/]*googleapis\.com/")
SIGNUP = "identitytoolkit.googleapis.com/v1/accounts:signUp"
COMMIT = "firestore.googleapis.com/v1/projects/%s/databases/(default)/documents:commit" % PROJEKT
DELETE = "identitytoolkit.googleapis.com/v1/accounts:delete"


@pytest.fixture(scope="module")
def kontakt_basis(tmp_path_factory):
    """Die Seiten mit Formular in einen Probeordner, wie tests/test_kontakt.py."""
    import huelle
    import seite_bauen
    import sprachen

    ordner = tmp_path_factory.mktemp("kontaktseite")
    privat = ordner / "huelle"
    privat.mkdir()
    (privat / "cloud_zugang.json").write_text(
        json.dumps({"projekt": PROJEKT, "schluessel": SCHLUESSEL, "client": CLIENT}), encoding="utf-8")
    ziel = ordner / "seite"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(seite_bauen, "ZIEL", str(ziel))
        mp.setattr(huelle, "ordner", lambda *a, **k: str(privat))
        mp.setattr(sprachen, "KONTAKT_FORMULAR", True)
        mp.setattr(sprachen, "KONTAKT_STAND", "28.10.2026")
        seite_bauen.main()
    assert (ziel / "kontakt.html").exists()

    class Leise(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    srv = Dateiserver(("127.0.0.1", 0), functools.partial(Leise, directory=str(ziel)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()
    srv.server_close()


class Formular:
    """Firebase fuer das Formular: anonym anlegen, ein Dokument anlegen,
    Konto loeschen. abbruch: wie ohne Netz. commit_status: was Firestore
    auf das Anlegen antwortet (403 = von den Regeln abgelehnt)."""

    def __init__(self):
        self.anfragen = []
        self.doks = {}
        self.konten = set()
        self.abbruch = False
        self.commit_status = 200
        self.n = 0

    def __call__(self, route, request):
        kopf = {"Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "authorization, content-type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"}
        if request.method == "OPTIONS":
            return route.fulfill(status=204, headers=kopf)
        teile = urllib.parse.urlsplit(request.url)
        pfad = teile.netloc + urllib.parse.unquote(teile.path)
        if self.abbruch:
            self.anfragen.append(("ABBRUCH", pfad, None, None))
            return route.abort()
        daten = json.loads(request.post_data or "{}")
        schluessel = urllib.parse.parse_qs(teile.query).get("key", [""])[0]
        self.anfragen.append((pfad, request.headers.get("authorization", ""), daten, schluessel))

        def antwort(status, inhalt):
            route.fulfill(status=status, headers=kopf, content_type="application/json", body=json.dumps(inhalt))

        if pfad == SIGNUP:
            self.n += 1
            uid = "anonym%d" % self.n
            self.konten.add(uid)
            return antwort(200, {"localId": uid, "idToken": "id-" + uid, "refreshToken": "r-" + uid,
                                 "expiresIn": "3600"})
        if pfad == COMMIT:
            if self.commit_status != 200:
                return antwort(self.commit_status, {"error": {"code": self.commit_status,
                                                              "status": "PERMISSION_DENIED"}})
            schreiben = daten["writes"][0]
            self.doks[schreiben["update"]["name"]] = schreiben
            return antwort(200, {"writeResults": [{"updateTime": "2026-10-28T12:00:00Z"}],
                                 "commitTime": "2026-10-28T12:00:00Z"})
        if pfad == DELETE:
            self.konten.discard(daten.get("idToken", "")[len("id-"):])
            return antwort(200, {"kind": "identitytoolkit#DeleteAccountResponse"})
        return antwort(404, {"error": {"code": 404, "status": "NOT_FOUND"}})


class Kontaktseite:
    def __init__(self, browser, basis, locale="de-DE"):
        self.ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale=locale,
                                       service_workers="block")
        self.page = self.ctx.new_page()
        self.basis = basis
        self.fehler, self.konsole, self.fremd = [], [], []
        self.firebase = Formular()
        self.page.on("pageerror", lambda e: self.fehler.append(str(e)))
        self.page.on("console", lambda m: self.konsole.append(m.text) if m.type == "error" else None)
        self.page.on("request", lambda r: None if r.url.startswith(basis) or GOOGLE.match(r.url)
                     else self.fremd.append(r.url))
        self.page.route(GOOGLE, self.firebase)
        self.page.goto(basis + "/kontakt.html")
        self.page.wait_for_function("!document.querySelector('form.kontakt button').disabled")

    def sprache(self, code):
        self.page.click('.sprachen button[data-sprache="%s"]' % code)

    def ausfuellen(self, code, text, adresse):
        self.page.fill("#nachricht-%s" % code, text)
        self.page.fill("#antwort-%s" % code, adresse)

    def absenden(self, code):
        self.page.click('form[data-sprache="%s"] button[type="submit"]' % code)

    def meldung(self, code, soll):
        """Wartet, bis die Meldung soll dasteht, und gibt sie zurueck."""
        sel = 'form[data-sprache="%s"] .meldung' % code
        self.page.wait_for_function("([s, t]) => document.querySelector(s).textContent === t", arg=[sel, soll])
        return self.page.text_content(sel)

    def wert(self, sel):
        return self.page.eval_on_selector(sel, "e => e.value")

    def sauber(self):
        assert self.fehler == [], self.fehler
        assert self.konsole == [], self.konsole
        assert self.fremd == [], self.fremd

    def zu(self):
        self.ctx.close()


@pytest.fixture
def kontakt(browser, kontakt_basis):
    seiten = []

    def oeffnen(**k):
        s = Kontaktseite(browser, kontakt_basis, **k)
        seiten.append(s)
        return s
    yield oeffnen
    for s in seiten:
        s.zu()


def _texte(code):
    import sprachen
    return sprachen.kontakt_texte(code)


def test_absenden_legt_genau_eine_nachricht_an(kontakt):
    s = kontakt()
    assert s.page.evaluate("document.documentElement.lang") == "de"
    s.ausfuellen("de", "  Hallo, eine Frage zu Zmaj.\nZweite Zeile.  ", "lerner@example.org")
    s.absenden("de")
    assert s.meldung("de", _texte("de")["danke"])
    pfade = [a[0] for a in s.firebase.anfragen]
    assert pfade == [SIGNUP, COMMIT, DELETE], pfade
    anlegen, schreiben, loeschen = s.firebase.anfragen
    assert anlegen[2] == {"returnSecureToken": True} and anlegen[3] == SCHLUESSEL
    assert schreiben[1] == "Bearer id-anonym1"
    assert schreiben[2] == {"writes": [{
        "update": {"name": "projects/%s/databases/(default)/documents/nachrichten/anonym1" % PROJEKT,
                   "fields": {"text": {"stringValue": "Hallo, eine Frage zu Zmaj.\nZweite Zeile."},
                              "antwort": {"stringValue": "lerner@example.org"},
                              "sprache": {"stringValue": "de"}}},
        "updateTransforms": [{"fieldPath": "zeit", "setToServerValue": "REQUEST_TIME"}],
        "currentDocument": {"exists": False}}]}
    assert loeschen[2] == {"idToken": "id-anonym1"} and loeschen[3] == SCHLUESSEL
    assert s.firebase.konten == set() and len(s.firebase.doks) == 1
    # Formular leer, Knopf wieder an.
    assert s.wert("#nachricht-de") == "" and s.wert("#antwort-de") == ""
    assert s.page.is_enabled('form[data-sprache="de"] button[type="submit"]')
    s.sauber()


def test_andere_sprache_schickt_ihre_sprache(kontakt):
    s = kontakt()
    s.ausfuellen("de", "Merhaba", "a@example.org")
    s.sprache("en")
    assert s.page.evaluate("document.documentElement.lang") == "en"
    assert s.page.is_visible("#nachricht-en") and not s.page.is_visible("#nachricht-de")
    # Was schon dastand, steht auch in der anderen Sprache.
    assert s.wert("#nachricht-en") == "Merhaba" and s.wert("#antwort-en") == "a@example.org"
    assert s.page.text_content('section[data-sprache="en"] h1') == _texte("en")["titel"]
    s.absenden("en")
    assert s.meldung("en", _texte("en")["danke"])
    schreiben = s.firebase.anfragen[1][2]["writes"][0]["update"]["fields"]
    assert schreiben["sprache"] == {"stringValue": "en"} and schreiben["text"] == {"stringValue": "Merhaba"}
    s.sauber()


def test_fallenfeld_schickt_nichts(kontakt):
    s = kontakt()
    s.ausfuellen("de", "Kaufen Sie jetzt!", "bot@example.org")
    s.page.eval_on_selector("#website-de", "e => { e.value = 'https://spam.example'; }")
    s.absenden("de")
    assert s.meldung("de", _texte("de")["danke"])
    assert s.firebase.anfragen == []
    s.sauber()


def test_ohne_netz_keine_verbindung(kontakt):
    s = kontakt()
    s.firebase.abbruch = True
    s.ausfuellen("de", "Geht das?", "lerner@example.org")
    s.absenden("de")
    assert s.meldung("de", _texte("de")["kein_netz"])
    assert [a[0] for a in s.firebase.anfragen] == ["ABBRUCH"]
    assert s.wert("#nachricht-de") == "Geht das?"
    assert s.page.is_enabled('form[data-sprache="de"] button[type="submit"]')
    # Der abgebrochene Abruf steht als Netzfehler in der Konsole - das ist
    # hier gewollt, Skriptfehler gibt es keine.
    assert s.fehler == [] and s.fremd == []


def test_abgelehnt_fehler_und_anmeldung_trotzdem_weg(kontakt):
    s = kontakt()
    s.firebase.commit_status = 403
    s.ausfuellen("de", "Hallo", "lerner@example.org")
    s.absenden("de")
    assert s.meldung("de", _texte("de")["fehler"])
    assert [a[0] for a in s.firebase.anfragen] == [SIGNUP, COMMIT, DELETE]
    assert s.firebase.konten == set() and s.firebase.doks == {}
    assert s.wert("#nachricht-de") == "Hallo"
    assert s.fehler == [] and s.fremd == []


def test_csp_sperrt_jede_andere_adresse(kontakt):
    """Gegenprobe: Die Policy greift wirklich. Ein Abruf an eine fremde
    Adresse scheitert im Browser, bevor er das Netz erreicht."""
    s = kontakt()
    ergebnis = s.page.evaluate("""async () => {
        try{ await fetch('https://example.org/'); return 'durch'; }catch(e){ return 'gesperrt'; }
    }""")
    assert ergebnis == "gesperrt"
    assert any("Content Security Policy" in k for k in s.konsole), s.konsole
    assert s.fremd == [] and s.firebase.anfragen == []


def test_ungueltige_adresse_haelt_der_browser_auf(kontakt):
    s = kontakt()
    s.ausfuellen("de", "Hallo", "lerner@example")
    s.absenden("de")
    s.page.wait_for_timeout(300)
    assert s.page.eval_on_selector("#antwort-de", "e => e.validity.valid") is False
    assert s.firebase.anfragen == []
    assert s.page.text_content('form[data-sprache="de"] .meldung') == ""
    s.sauber()


# ------------------------------------------------ Weiterleitung (.gs) ---

ZIEL = "zmaj.lernapp@gmail.com"
DOK = "projects/zmaj-probe/databases/(default)/documents/nachrichten/%s"

# Die Google-Dienste, die kontakt_weiterleitung.gs benutzt, so weit nachgebaut,
# wie das Skript sie braucht. WELT haelt alles fest: Skripteigenschaften,
# Dokumente in Firestore, verschickte Mails, Protokoll, Kontingent.
WELT = r"""
var WELT = {eig: {PROJEKT: 'zmaj-probe', SCHLUESSEL: 'AIza-probe', MELDER_MAIL: 'melder@example.org',
                  MELDER_PASSWORT: 'probe'},
            doks: [], mails: [], log: [], quote: 100, heute: '2026-10-28', loeschen: 200, wirf: null, takt: 0};
var Logger = {log: function (m) { WELT.log.push(String(m)); }};
var PropertiesService = {getScriptProperties: function () { return {
  getProperty: function (k) { return Object.prototype.hasOwnProperty.call(WELT.eig, k) ? WELT.eig[k] : null; },
  setProperty: function (k, v) { WELT.eig[k] = String(v); }
}; }};
var LockService = {getScriptLock: function () {
  return {tryLock: function () { return true; }, releaseLock: function () {}}; }};
var Utilities = {formatDate: function (d, zone, muster) { return muster === 'yyyy-MM-dd' ? WELT.heute : d.toISOString(); }};
var MailApp = {
  getRemainingDailyQuota: function () { return WELT.quote; },
  sendEmail: function (n) {
    if (WELT.wirf && WELT.wirf(n)) throw new Error('Invalid argument');
    if (WELT.quote < 1) throw new Error('Service invoked too many times for one day: email.');
    WELT.quote--;
    WELT.mails.push(JSON.parse(JSON.stringify(n)));
  }
};
var ScriptApp = {getProjectTriggers: function () { return []; }, deleteTrigger: function () {},
  newTrigger: function () {
    var b = {timeBased: function () { return b; }, everyMinutes: function (m) { WELT.takt = m; return b; },
             create: function () {}};
    return b;
  }};
function antwort_(code, inhalt) {
  var text = inhalt === undefined ? '' : JSON.stringify(inhalt);
  return {getResponseCode: function () { return code; }, getContentText: function () { return text; }};
}
var UrlFetchApp = {fetch: function (url, opt) {
  if (url.indexOf('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIza-probe') === 0) {
    return JSON.parse(opt.payload).password === WELT.eig.MELDER_PASSWORT
      ? antwort_(200, {idToken: 'melder-ausweis'}) : antwort_(400, {error: {message: 'INVALID_PASSWORD'}});
  }
  if (!opt.headers || opt.headers.Authorization !== 'Bearer melder-ausweis') {
    return antwort_(403, {error: {status: 'PERMISSION_DENIED'}});
  }
  var v1 = 'https://firestore.googleapis.com/v1/';
  if (opt.method === 'get' && url.indexOf(v1 + 'projects/zmaj-probe/databases/(default)/documents/nachrichten?') === 0) {
    var n = +/pageSize=(\d+)/.exec(url)[1];
    var liste = WELT.doks.slice().sort(function (a, b) {
      return a.fields.zeit.timestampValue < b.fields.zeit.timestampValue ? -1 : 1; }).slice(0, n);
    return antwort_(200, liste.length ? {documents: liste} : {});
  }
  if (opt.method === 'delete' && url.indexOf(v1 + 'projects/') === 0) {
    if (WELT.loeschen !== 200) return antwort_(WELT.loeschen, {error: {status: 'UNAVAILABLE'}});
    var name = url.slice(v1.length);
    WELT.doks = WELT.doks.filter(function (d) { return d.name !== name; });
    return antwort_(200, {});
  }
  return antwort_(404, {error: {status: 'NOT_FOUND'}});
}};
function dok_(id, text, antwort, minute) {
  return {name: 'projects/zmaj-probe/databases/(default)/documents/nachrichten/' + id,
          fields: {text: {stringValue: text}, antwort: {stringValue: antwort}, sprache: {stringValue: 'de'},
                   zeit: {timestampValue: '2026-10-28T12:' + ('0' + minute).slice(-2) + ':00Z'}}};
}
function lauf() { try { weiterleiten(); return null; } catch (x) { return String(x.message); } }
"""


class Weiterleitung:
    def __init__(self, browser):
        import os
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "kontakt_weiterleitung.gs"), encoding="utf-8") as f:
            gs = f.read()
        self.ctx = browser.new_context()
        self.page = self.ctx.new_page()
        self.fehler = []
        self.page.on("pageerror", lambda e: self.fehler.append(str(e)))
        self.page.set_content("<!doctype html><meta charset=utf-8><title>gs</title>")
        self.page.add_script_tag(content=WELT)
        self.page.add_script_tag(content=gs)

    def doks(self, *liste):
        """liste: (id, text, antwort, minute)."""
        self.page.evaluate("l => l.forEach(d => WELT.doks.push(dok_(d[0], d[1], d[2], d[3])))",
                           [list(d) for d in liste])

    def lauf(self):
        """None, oder die Meldung, mit der der Lauf abbrach."""
        return self.page.evaluate("lauf()")

    def setze(self, js):
        # Als Funktion: Ergibt ein Ausdruck selbst eine Funktion (WELT.wirf =
        # n => ...), ruft Playwright sie sonst gleich auf.
        self.page.evaluate("() => { %s; }" % js)

    def welt(self, name):
        return self.page.evaluate("n => WELT[n]", name)

    def eig(self, name):
        return self.page.evaluate("k => Object.prototype.hasOwnProperty.call(WELT.eig, k) ? WELT.eig[k] : null",
                                  name)

    def ids(self):
        return sorted(d["name"].rsplit("/", 1)[1] for d in self.welt("doks"))

    def mails(self):
        mails = self.welt("mails")
        assert all(m["to"] == ZIEL for m in mails), mails       # nie an die Adresse aus dem Formular
        return mails


@pytest.fixture
def weiterleitung(browser):
    offen = []

    def oeffnen():
        w = Weiterleitung(browser)
        offen.append(w)
        return w
    yield oeffnen
    for w in offen:
        assert w.fehler == [], w.fehler
        w.ctx.close()


def test_weiterleitung_normalfall(weiterleitung):
    w = weiterleitung()
    w.doks(("a", "Hallo Zmaj,\n\neine Frage.", "lerner@example.org", 1))
    w.page.evaluate("einrichten()")                 # Ausloeser anlegen, dann ein Lauf
    assert w.welt("takt") == 5
    (m,) = w.mails()
    assert m["replyTo"] == "lerner@example.org" and m["name"] == "Zmaj-Formular"
    assert m["subject"] == "[Zmaj-Formular] Hallo Zmaj, eine Frage."
    assert m["body"].startswith("Antwort an: lerner@example.org\nSprache: de\nEingang: ")
    assert m["body"].endswith("\n\nHallo Zmaj,\n\neine Frage.")
    assert w.ids() == [] and w.eig("GESENDET") == "[]" and w.eig("FEHLVERSUCHE") is None
    assert w.welt("log") == ["weitergeleitet: 1"]
    assert w.lauf() is None and len(w.mails()) == 1  # leer: nichts mehr
    # Ein Zaehler fuer ein Dokument, das es nicht mehr gibt (Notbremse), verschwindet.
    w.setze("WELT.eig.FEHLVERSUCHE = JSON.stringify({'projects/x/nachrichten/alt': 2})")
    assert w.lauf() is None and w.eig("FEHLVERSUCHE") == "{}"


def test_weiterleitung_eine_kaputte_nachricht_haelt_nichts_auf(weiterleitung):
    """Vorher brach der ganze Lauf ab, und weil die Liste nach zeit sortiert
    ist, blockierte dieselbe Nachricht jeden weiteren Lauf."""
    w = weiterleitung()
    w.doks(("a", "GIFT", "x\u0001y@example.org", 1), ("b", "Echte Frage", "lerner@example.org", 2))
    w.setze("WELT.wirf = n => n.body.indexOf('GIFT') >= 0")
    for n in (1, 2, 3):
        assert w.lauf() is None
        assert w.ids() == ["a"]
        assert json.loads(w.eig("FEHLVERSUCHE")) == {DOK % "a": n}
    (b,) = w.mails()
    assert b["subject"] == "[Zmaj-Formular] Echte Frage" and b["replyTo"] == "lerner@example.org"
    # Vierter Lauf: nur ein Hinweis ohne Inhalt aus dem Formular, dann ist sie weg.
    assert w.lauf() is None
    _, hinweis = w.mails()
    assert hinweis["subject"] == "[Zmaj-Formular] Nachricht nicht zustellbar" and "replyTo" not in hinweis
    assert "nachrichten/a" in hinweis["body"] and "GIFT" not in hinweis["body"]
    assert "example.org" not in hinweis["body"] and "\u0001" not in hinweis["body"]
    assert w.ids() == [] and json.loads(w.eig("FEHLVERSUCHE")) == {}
    # Kein Inhalt im Protokoll, nur Zahlen und Stufen.
    assert not [z for z in w.welt("log") if "GIFT" in z or "@" in z or "Frage" in z]


def test_weiterleitung_ersatz_ohne_antworten_an(weiterleitung):
    """Lehnt MailApp nur "Antworten an" ab, kommt die Nachricht trotzdem im
    selben Lauf an - die Adresse steht dann maskiert im Text."""
    w = weiterleitung()
    w.doks(("a", "Frage", "o'brien@example.ie", 1))
    w.setze("WELT.wirf = n => 'replyTo' in n")
    assert w.lauf() is None
    (m,) = w.mails()
    assert "replyTo" not in m
    assert m["subject"] == "[Zmaj-Formular] (Ersatz: Antwortadresse im Text pruefen)"
    assert m["body"].split("\n")[0] == 'Antwort an: (ungeprueft) "o\'brien@example.ie"'
    assert m["body"].endswith("\n\nFrage")
    assert w.ids() == [] and w.eig("FEHLVERSUCHE") is None


def test_weiterleitung_fremde_zeichen_nie_in_antworten_an(weiterleitung):
    """Firestore laesst solche Adressen seit dem 28.10.2026 nicht mehr zu -
    das Skript verlaesst sich darauf aber nicht."""
    w = weiterleitung()
    schlecht = ["x\u0001y@example.org", "a@b.c\u200b", "ä@b.c", "a@b..c", "a@b.de\nBcc: c@d.de",
                ".a@example.org", "<a@b.de>"]
    w.doks(*[(str(i), "Text %d" % i, a, i) for i, a in enumerate(schlecht)])
    assert w.lauf() is None
    mails = w.mails()
    assert len(mails) == len(schlecht) and w.ids() == []
    for m, a in zip(mails, schlecht):
        assert "replyTo" not in m, a
        assert m["body"].split("\n")[0] == "Antwort an: (ungeprueft) " + json.dumps(a, ensure_ascii=False), a


def test_weiterleitung_stau_einmal_am_tag(weiterleitung):
    w = weiterleitung()
    w.doks(*[(c, "Nachricht " + c, "lerner@example.org", i) for i, c in enumerate("abcde")])
    w.setze("WELT.quote = 3")
    assert w.lauf() is None
    mails = w.mails()
    assert [m["subject"] for m in mails[:2]] == ["[Zmaj-Formular] Nachricht a", "[Zmaj-Formular] Nachricht b"]
    stau = mails[2]
    assert stau["subject"].startswith("[Zmaj-Formular] Stau") and "replyTo" not in stau
    assert "Es warten noch 3." in stau["body"] and "Anonym deaktivieren" in stau["body"]
    assert w.ids() == ["c", "d", "e"] and w.welt("quote") == 0
    # Kontingent leer: nichts. Wieder etwas frei am selben Tag: kein zweiter Stau.
    assert w.lauf() is None and len(w.mails()) == 3
    w.setze("WELT.quote = 2")
    assert w.lauf() is None
    assert [m["subject"] for m in w.mails()[3:]] == ["[Zmaj-Formular] Nachricht c"] and w.ids() == ["d", "e"]
    # Am naechsten Tag geht der Rest raus.
    w.setze("WELT.heute = '2026-10-29'; WELT.quote = 100")
    assert w.lauf() is None
    assert [m["subject"] for m in w.mails()[4:]] == ["[Zmaj-Formular] Nachricht d", "[Zmaj-Formular] Nachricht e"]
    assert w.ids() == []


def test_weiterleitung_loeschen_scheitert_kein_zweiter_versand(weiterleitung):
    w = weiterleitung()
    w.doks(("a", "Hallo", "lerner@example.org", 1))
    w.setze("WELT.loeschen = 503")
    assert "Firestore delete: 503" in (w.lauf() or "")
    assert len(w.mails()) == 1 and w.ids() == ["a"] and json.loads(w.eig("GESENDET")) == [DOK % "a"]
    w.setze("WELT.loeschen = 200")
    assert w.lauf() is None
    assert len(w.mails()) == 1 and w.ids() == [] and json.loads(w.eig("GESENDET")) == []
