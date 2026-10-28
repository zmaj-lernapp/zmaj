# -*- coding: utf-8 -*-
"""Die Pflicht-Anmeldung (28.10.2026, v109) - im echten Browser.

Ajdin am 26./27.10.2026: Anmeldung mit Firebase schon in v109, Pflicht,
mit Google und mit E-Mail und Passwort; neue Nutzer machen erst die 1.
Lektion, bestehende melden sich beim naechsten Start an; "anmelden soll nur
einmal passieren wie bei duolingo"; ohne Internet wird trotzdem gelernt.
Plan: Release\\Firebase_Plan_v109.md, Abschnitt 6.2.

Firebase beantwortet firebase_attrappe.py, die Huelle (ZmajAnmeldung)
ersetzt PLUGIN unten - es zaehlt jeden Aufruf in sessionStorage, und die
"native Kopie" der Sitzung liegt dort auch, damit sie ein Leeren von
localStorage uebersteht wie die echte in den SharedPreferences. Kein Byte
verlaesst den Rechner.

Ohne Firebase-Projekt (die Quelle, CLOUD_AN = false) bleibt alles wie vor
v109: test_ohne_projekt_alles_wie_heute.
"""
import datetime
import json

from firebase_attrappe import CLIENT, FIREBASE, UID, Attrappe, dok_pfad, wege

KONTO = "identitytoolkit.googleapis.com/v1/accounts:"

# Der Ersatz fuer das Plugin der Huelle. sessionStorage ueberlebt Neuladen
# und localStorage.clear() - wie die SharedPreferences "zmaj_konto".
PLUGIN = r"""
(() => {
  const ss = window.sessionStorage;
  const lies = (k, d) => { try{ return JSON.parse(ss.getItem(k) || d); }catch(e){ return JSON.parse(d); } };
  const merk = (name, daten) => { const a = lies('probe_aufrufe', '[]'); a.push([name, daten || null]); ss.setItem('probe_aufrufe', JSON.stringify(a)); };
  window.Capacitor = {Plugins: {ZmajAnmeldung: {
    googleAusweis: async (o) => { merk('googleAusweis', o);
      const f = ss.getItem('probe_google_fehler');
      if(f){ const e = new Error(f); e.code = f; throw e; }
      return {idToken: 'google-probe'}; },
    sitzungMerken: async (o) => { merk('sitzungMerken', o); ss.setItem('probe_nativ', JSON.stringify(o)); return {ok: true}; },
    sitzungHolen: async () => { merk('sitzungHolen'); return lies('probe_nativ', '{}'); },
    restoreSichern: async (o) => { merk('restoreSichern', o); return {ok: true}; },
    restoreHolen: async () => { merk('restoreHolen'); return lies('probe_restore', '{}'); },
    abmelden: async () => { merk('abmelden'); ss.removeItem('probe_nativ'); ss.removeItem('probe_restore'); return {ok: true}; },
  }}};
})();
"""

# Fertig gestartet: wie BEREIT in conftest.py, aber die Anmeldeseite zaehlt
# auch - dort ist der Einstellungsknopf mit Absicht weg.
BEREIT = ("typeof CATEGORIES !== 'undefined' && CATEGORIES && CATEGORIES.length > 0"
          " && typeof standGeladen !== 'undefined' && standGeladen"
          " && (document.getElementById('btnSettings').style.display === 'inline-block'"
          "     || document.getElementById('profileView').style.display === 'block')")

ZUSTAND = """() => ({
  sicht: ['profileView','pfad','levelView','storyView','shopView','einstufungView','kontoView','settingsView']
           .filter(v => sichtbar(v)),
  wahl: !document.getElementById('anmWahl').hidden,
  form: !document.getElementById('kontoForm').hidden,
  titel: document.getElementById('kontoTitel').textContent,
  frage: document.getElementById('kontoFrage').textContent,
  merker: JSON.parse(localStorage.getItem('zmaj_cloud') || 'null'),
  woerter: known.size, tage: days.size,
})"""


def _aufrufe(seite, name=None):
    a = seite.js("() => JSON.parse(sessionStorage.getItem('probe_aufrufe') || '[]')")
    return [d for n, d in a if n == name] if name else [n for n, _ in a]


def _t(seite, schluessel, werte=None):
    return seite.js("([k, w]) => t(k, w || {})", [schluessel, werte])


def _starten(seite, cloud_html, stand=None, attrappe=None, sprache="de", vorbereiten=None, plugin=True):
    """Wie Seite.starten(), aber mit der eingeschalteten Anmeldung und dem
    Plugin-Ersatz, und fertig ist es auch auf der Anmeldeseite."""
    attrappe = attrappe or Attrappe()
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=cloud_html))
    for host in FIREBASE:
        seite.page.route("https://%s/**" % host, attrappe)
    if plugin:
        seite.page.add_init_script(PLUGIN)
    seite.page.goto(seite.basis + "/leer")
    seite.js("""([stand, sprache]) => {
        localStorage.clear(); sessionStorage.clear();
        if(stand) localStorage.setItem('zmaj_stand', JSON.stringify(stand));
        localStorage.setItem('zmaj_einwilligung', JSON.stringify({wahl:'nein', stand:1, zeit:new Date().toISOString()}));
        localStorage.setItem('zmaj_sprache', sprache);
    }""", [stand, sprache])
    if vorbereiten:
        seite.js(vorbereiten)
    seite.page.goto(seite.basis + "/app/index.html")
    seite.page.wait_for_function(BEREIT, timeout=30000)
    return attrappe


def _neu_laden(seite):
    seite.page.reload()
    seite.page.wait_for_function(BEREIT, timeout=30000)


def _gelernt(heute_stand, seite=None, tage=1):
    heute = datetime.date.today()
    return heute_stand(gewusst=["probe:geraet"],
                       tage=[(heute - datetime.timedelta(days=i)).isoformat() for i in range(tage)])


def _fertig(seite):
    seite.page.wait_for_function("() => !anmeldungLaeuft && !cloudLaeuft")


def _warte(seite, bedingung):
    for _ in range(200):
        if bedingung():
            return
        seite.page.wait_for_timeout(25)
    raise AssertionError("wartet vergeblich")


def _mail_anmelden(seite, email, pw, neu=False):
    if seite.js("() => !document.getElementById('anmWahl').hidden"):
        seite.page.click("#anmMail")
    if neu:
        seite.page.click("#kontoWechsel")
    seite.page.fill("#kontoMail", email)
    seite.page.fill("#kontoPw", pw)
    if neu:
        seite.page.fill("#kontoPw2", pw)
    seite.page.click("#kontoSenden")
    _fertig(seite)


def _cloud_stand(attrappe, uid, woerter, tage, rev="tablet.1"):
    text = json.dumps({"app": "zmaj", "version": 1, "stand": {"gewusst": woerter, "tage": tage}})
    attrappe.doks[uid] = {"daten": {"stringValue": text}, "rev": {"stringValue": rev}}


# ------------------------------------------------------------ ohne Projekt ---

def test_ohne_projekt_alles_wie_heute(seite, heute_stand):
    """Die Quelle (CLOUD_AN = false), sogar mit dem Plugin der Huelle: nach
    Lektion 1 kein Tor, kein Aufruf des Plugins, kein Netz, kein Merker."""
    seite.page.add_init_script(PLUGIN)
    seite.starten(stand=heute_stand())
    seite.js("() => { openLevel(0); startLesson(); }")
    seite.durchspielen("lBody", "Lx")
    z = seite.js("""() => ({lHome: !!document.getElementById('lHome'), lMore: !!document.getElementById('lMore'),
                            weiter: !!document.getElementById('anmWeiter'), tage: days.size,
                            faellig: anmeldungFaellig(), modus: cloudModus()})""")
    assert z == {"lHome": True, "lMore": True, "weiter": False, "tage": 1, "faellig": False, "modus": False}, z
    seite.js("() => { showHome(); einstufungWahl(); }")
    assert seite.js("() => [sichtbar('pfad'), !!document.getElementById('eKonto')]") == [True, False]
    seite.neu_laden()
    assert seite.js("() => sichtbar('pfad') && !sichtbar('profileView')")
    assert _aufrufe(seite) == []
    rest = seite.js("() => Object.keys(localStorage).filter(k => /cloud|abgemeldet/i.test(k))")
    assert rest == []
    assert [u for u in seite.fremd if any(h in u for h in FIREBASE)] == []
    assert seite.fehler == []


# ------------------------------------------------------- neu: das Tor ---

def test_neu_erst_lektion_dann_nur_noch_anmeldung(seite, heute_stand, cloud_html):
    attrappe = _starten(seite, cloud_html, stand=heute_stand())
    assert seite.js("() => [sichtbar('pfad'), anmeldungFaellig()]") == [True, False]
    assert _aufrufe(seite) == ["sitzungHolen", "restoreHolen"]
    seite.js("() => { openLevel(0); startLesson(); }")
    seite.durchspielen("lBody", "Lx")
    # Auf dem Ergebnisschirm nur noch "Weiter".
    z = seite.js("""() => ({lHome: !!document.getElementById('lHome'), lMore: !!document.getElementById('lMore'),
                            lPfad: !!document.getElementById('lPfad'),
                            weiter: (document.getElementById('anmWeiter') || {}).textContent})""")
    assert z == {"lHome": False, "lMore": False, "lPfad": False, "weiter": _t(seite, "anm.weiter")}, z
    seite.page.click("#anmWeiter")
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["profileView"] and z["wahl"] and not z["form"]
    assert z["titel"] == _t(seite, "anm.titel_sichern") and z["frage"] == _t(seite, "anm.text_sichern")
    # Der Google-Knopf ist da (Plugin und Client-ID), die Rechtstexte zum Aufklappen.
    assert seite.js("""() => [!document.getElementById('anmGoogle').hidden,
                              document.getElementById('anmGoogleText').textContent,
                              document.getElementById('anmDs').textContent.length > 500,
                              document.getElementById('anmAgb').textContent.length > 500,
                              document.getElementById('btnSettings').style.display]""") \
        == [True, _t(seite, "anm.google"), True, True, "none"]
    # Kein Weg daran vorbei.
    for weg in ("showHome()", "openLevel(0)", "showLaden()", "openStory(0)", "startLesson()",
                "startTest()", "rundeStarten('topf')", "einstufungStarten()", "showView('pfad')"):
        seite.js("() => { %s; }" % weg)
        assert seite.js(ZUSTAND)["sicht"] == ["profileView"], weg
    # Auch nicht nach einem Neustart.
    _neu_laden(seite)
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["profileView"] and z["tage"] == 1
    assert [a for a in attrappe.anfragen if a[0] != "OPTIONS"] == []      # gefragt wird erst beim Anmelden
    assert seite.fehler == []


def test_einstufung_danach_weiter_zur_anmeldung(seite, heute_stand, cloud_html):
    _starten(seite, cloud_html, stand=heute_stand())
    seite.js("() => { baueEinstufung('gut'); einstufungStarten(); einstufungEnde(); }")
    assert seite.js("() => [einstufung.fragen >= 0, document.getElementById('eLos').textContent]") \
        == [True, _t(seite, "anm.weiter")]
    seite.page.click("#eLos")
    assert seite.js(ZUSTAND)["sicht"] == ["profileView"]
    assert seite.fehler == []


# ------------------------------------------------------------- E-Mail ---

def test_konto_mit_email_anlegen(seite, heute_stand, cloud_html):
    attrappe = _starten(seite, cloud_html, stand=_gelernt(heute_stand))
    attrappe.konto_anlegen("da@probe.example", "schon-da-123")
    assert seite.js(ZUSTAND)["titel"] == _t(seite, "anm.titel_sichern")
    seite.page.click("#anmMail")
    z = seite.js(ZUSTAND)
    assert z["form"] and not z["wahl"] and z["titel"] == _t(seite, "konto.anmelden_titel")
    seite.page.click("#kontoWechsel")
    assert seite.js("""() => [document.getElementById('kontoTitel').textContent,
                              document.getElementById('kontoPw2').hidden, document.getElementById('kontoRegeln').hidden,
                              document.getElementById('kontoRegeln').textContent]""") \
        == [_t(seite, "konto.anlegen_titel"), False, False,
            _t(seite, "konto.regeln_titel") + _t(seite, "konto.regel_laenge", {"n": 8})]
    note = "() => document.getElementById('kontoNote').textContent"
    # Zu kurz, ungleich, keine Adresse - die App sagt es, ohne zu fragen.
    for email, pw, pw2, soll in (("neu@probe.example", "kurz", "kurz", ("konto.fehler_kurz", {"n": 8})),
                                 ("neu@probe.example", "geheim123", "geheim124", ("konto.fehler_wdh", None)),
                                 ("keine-adresse", "geheim123", "geheim123", ("konto.fehler_email", None))):
        seite.page.fill("#kontoMail", email)
        seite.page.fill("#kontoPw", pw)
        seite.page.fill("#kontoPw2", pw2)
        seite.page.click("#kontoSenden")
        assert seite.js(note) == _t(seite, *soll)
    assert attrappe.anfragen == []
    # Die Adresse hat schon ein Konto.
    seite.page.fill("#kontoMail", "da@probe.example")
    seite.page.fill("#kontoPw", "geheim123")
    seite.page.fill("#kontoPw2", "geheim123")
    seite.page.click("#kontoSenden")
    _fertig(seite)
    assert seite.js(note) == _t(seite, "konto.fehler_email_da")
    assert seite.js(ZUSTAND)["merker"] is None
    # Jetzt richtig.
    attrappe.anfragen.clear()
    seite.page.fill("#kontoMail", "neu@probe.example")
    seite.page.fill("#kontoPw", "geheim123")
    seite.page.fill("#kontoPw2", "geheim123")
    seite.page.click("#kontoSenden")
    _fertig(seite)
    seite.page.wait_for_function("() => document.querySelector('.nachfrage #anmFertigOk')")
    uid = attrappe.konten["neu@probe.example"]["uid"]
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["pfad"]
    m = z["merker"]
    assert m["art"] == "passwort" and m["uid"] == uid and m["email"] == "neu@probe.example" and m["token"] == "r-" + uid
    assert [w for w in wege(attrappe) if w[1] != KONTO + "sendOobCode"] == [
        ("POST", KONTO + "signUp"), ("GET", dok_pfad(uid)), ("PATCH", dok_pfad(uid))]
    assert "probe:geraet" in json.loads(attrappe.doks[uid]["daten"]["stringValue"])["stand"]["gewusst"]
    for _ in range(40):
        if attrappe.mails:
            break
        seite.page.wait_for_timeout(50)
    assert [(x["art"], x["sprache"]) for x in attrappe.mails] == [("VERIFY_EMAIL", "de")]
    assert seite.js("() => document.querySelector('.nachfrage .txt').textContent") == _t(seite, "konto.bestaetigung_raus")
    seite.page.click("#anmFertigOk")
    assert _aufrufe(seite, "sitzungMerken")[-1] == {"art": "passwort", "uid": uid, "token": "r-" + uid,
                                                    "email": "neu@probe.example"}
    seite.page.wait_for_function("() => JSON.parse(sessionStorage.getItem('probe_aufrufe')).some(a => a[0] === 'restoreSichern')")
    assert _aufrufe(seite, "restoreSichern") == [{"uid": uid}]
    assert seite.js("() => [document.getElementById('btnProfil').style.display, document.getElementById('btnSettings').style.display]") \
        == ["inline-block", "inline-block"]
    assert seite.fehler == []


def test_falsches_passwort_und_passwort_vergessen(seite, heute_stand, cloud_html):
    attrappe = _starten(seite, cloud_html, stand=_gelernt(heute_stand), sprache="nb")
    attrappe.konto_anlegen("ich@probe.example", "richtig-123")
    _mail_anmelden(seite, "ich@probe.example", "falsch-123")
    assert seite.js("() => document.getElementById('kontoNote').textContent") == _t(seite, "konto.fehler_mail_pw")
    assert seite.js(ZUSTAND)["merker"] is None and attrappe.doks == {}
    # Passwort vergessen: dieselbe Antwort, ob es die Adresse gibt oder nicht.
    seite.page.click("#kontoVergessen")
    assert seite.js(ZUSTAND)["titel"] == _t(seite, "konto.vergessen_titel")
    assert seite.js("() => document.getElementById('kontoPw').hidden")
    antworten = []
    for email in ("ich@probe.example", "gibt-es-nicht@probe.example"):
        seite.page.fill("#kontoMail", email)
        seite.page.click("#kontoSenden")
        _fertig(seite)
        antworten.append(seite.js("""() => [document.getElementById('kontoNote').textContent,
                                            document.getElementById('kontoSpam').hidden]"""))
    assert antworten == [[_t(seite, "konto.vergessen_raus"), False]] * 2
    # Die Mail in der Sprache der App - Norwegisch heisst bei Firebase "no".
    assert [(x["art"], x["email"], x["sprache"]) for x in attrappe.mails] == [
        ("PASSWORD_RESET", "ich@probe.example", "no"), ("PASSWORD_RESET", "gibt-es-nicht@probe.example", "no")]
    # Zurueck: aus dem Formular zur Wahl, aus der Wahl nirgendwohin (dann
    # fragt die Zurueck-Taste wie auf der Startseite, ob Zmaj zugehen soll).
    seite.js("() => zurueckTaste()")
    assert seite.js(ZUSTAND)["wahl"] and seite.js("() => backTarget") is None
    seite.page.click("#anmMail")
    seite.page.click("#kontoWechsel")
    seite.js("() => zurueckTaste()")
    assert seite.js(ZUSTAND)["wahl"]
    # Und richtig angemeldet.
    _mail_anmelden(seite, "ich@probe.example", "richtig-123")
    assert seite.js(ZUSTAND)["merker"]["art"] == "passwort" and attrappe.mails[-1]["art"] == "PASSWORD_RESET"
    assert seite.fehler == []


# ------------------------------------------------------------- Google ---

def test_google(seite, heute_stand, cloud_html):
    attrappe = _starten(seite, cloud_html, stand=_gelernt(heute_stand))
    # Abgebrochen: keine Meldung, keine Anfrage.
    seite.js("() => sessionStorage.setItem('probe_google_fehler', 'abgebrochen')")
    seite.page.click("#anmGoogle")
    _fertig(seite)
    assert seite.js("() => document.getElementById('anmNote').textContent") == ""
    seite.js("() => sessionStorage.setItem('probe_google_fehler', 'kein_konto')")
    seite.page.click("#anmGoogle")
    _fertig(seite)
    assert seite.js("() => document.getElementById('anmNote').textContent") == _t(seite, "konto.fehler_google_keins")
    assert attrappe.anfragen == []
    assert _aufrufe(seite, "googleAusweis") == [{"client": CLIENT}] * 2
    # Geklappt.
    seite.js("() => sessionStorage.removeItem('probe_google_fehler')")
    seite.page.click("#anmGoogle")
    _fertig(seite)
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["pfad"] and z["merker"]["art"] == "google" and z["merker"]["uid"] == UID
    assert wege(attrappe) == [("POST", KONTO + "signInWithIdp"), ("GET", dok_pfad()), ("PATCH", dok_pfad())]
    assert attrappe.mails == []                     # keine Bestaetigungsmail bei Google
    assert seite.fehler == []


# ---------------------------------------------- bestehende Nutzer, dauerhaft ---

def test_bestand_wird_vereinigt_und_bleibt_angemeldet(seite, heute_stand, cloud_html):
    heute = datetime.date.today()
    gestern = (heute - datetime.timedelta(days=1)).isoformat()
    attrappe = Attrappe()
    uid = attrappe.konto_anlegen("alt@probe.example", "geheim-123")
    _starten(seite, cloud_html, stand=_gelernt(heute_stand, tage=2), attrappe=attrappe)
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["profileView"] and z["titel"] == _t(seite, "anm.titel_bestand")
    serie = seite.js("() => streak()")
    _cloud_stand(attrappe, uid, ["probe:tablet"], [gestern])
    _mail_anmelden(seite, "alt@probe.example", "geheim-123")
    z = seite.js("() => ({w: [...known].sort(), t: [...days].sort(), s: streak(), sicht: sichtbar('pfad')})")
    assert z["w"] == ["probe:geraet", "probe:tablet"] and z["s"] == serie and z["sicht"]
    assert gestern in z["t"] and heute.isoformat() in z["t"]
    assert json.loads(attrappe.doks[uid]["daten"]["stringValue"])["stand"]["gewusst"] == ["probe:geraet", "probe:tablet"]

    # Neu laden, auch mit einer veraenderten Seite als "Update": angemeldet,
    # ohne Anmeldeseite, und ohne eine einzige Anmeldung bei Firebase.
    attrappe.anfragen.clear()
    seite.page.unroute("**/app/index.html")
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=cloud_html + b"\n<!-- update -->\n"))
    _neu_laden(seite)
    assert seite.js(ZUSTAND)["sicht"] == ["pfad"]
    assert [w for w in wege(attrappe) if "accounts:" in w[1]] == []
    # In den Hintergrund mit etwas Neuem: hoechstens ein Schreiben am Tag.
    for _ in range(3):
        seite.js("""() => { known.add('probe:neu' + Math.random());
            Object.defineProperty(document, 'hidden', {configurable: true, get: () => true});
            document.dispatchEvent(new Event('visibilitychange')); delete document.hidden; }""")
        _fertig(seite)
    assert [w for w in wege(attrappe) if w[0] == "PATCH"] == [("PATCH", dok_pfad(uid))]

    # Der Schluessel landet nirgends: nicht in der Sicherungsdatei, nicht in
    # der Cloud, auch nicht die Adresse; rev ohne Geraetekennung.
    dok = attrappe.doks[uid]
    for text in (seite.js("() => sicherungInhalt()"), dok["daten"]["stringValue"]):
        assert "r-" + uid not in text and "zmaj_cloud" not in text and "alt@probe.example" not in text
    assert seite.js("(rev) => rev.indexOf(geraetId()) < 0", dok["rev"]["stringValue"])
    assert seite.fehler == []


def test_native_kopie_ohne_webview_daten(seite, heute_stand, cloud_html):
    """Handywechsel, bei dem Android die WebView-Daten nicht mitbringt: die
    Kopie in der Huelle meldet an, der Lernstand kommt aus der Cloud."""
    attrappe = Attrappe()
    uid = attrappe.konto_anlegen("weg@probe.example", "geheim-123")
    _cloud_stand(attrappe, uid, ["probe:cloud"], [datetime.date.today().isoformat()])
    kopie = json.dumps({"art": "passwort", "uid": uid, "token": "r-" + uid, "email": "weg@probe.example"})
    _starten(seite, cloud_html, stand=heute_stand(), attrappe=attrappe,
             vorbereiten="() => sessionStorage.setItem('probe_nativ', %s)" % json.dumps(kopie))
    seite.page.wait_for_function("() => known.has('probe:cloud')")
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["pfad"] and z["merker"]["uid"] == uid and z["merker"]["email"] == "weg@probe.example"
    assert [w for w in wege(attrappe) if "accounts:" in w[1]] == []
    assert seite.fehler == []


def test_restore_schluessel_zeigt_willkommen_zurueck(seite, heute_stand, cloud_html):
    _starten(seite, cloud_html, stand=heute_stand(),
             vorbereiten="() => sessionStorage.setItem('probe_restore', JSON.stringify({uid: 'uidAlt'}))")
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["profileView"] and z["titel"] == _t(seite, "anm.titel_zurueck")
    assert z["woerter"] == 0
    assert seite.fehler == []


# -------------------------------------------------------------- ohne Netz ---

OFFLINE = "() => { Object.defineProperty(navigator, 'onLine', {configurable: true, get: () => false}); }"
ONLINE = "() => { delete navigator.onLine; window.dispatchEvent(new Event('online')); }"


def test_offline_lernen_dann_anmeldung_aber_nie_mitten_in_der_lektion(seite, heute_stand, cloud_html):
    attrappe = _starten(seite, cloud_html, stand=heute_stand())
    attrappe.abbruch = True
    seite.js(OFFLINE)
    seite.js("() => { openLevel(0); startLesson(); }")
    seite.durchspielen("lBody", "Lx")
    assert seite.js("() => [!!document.getElementById('lHome'), !!document.getElementById('anmWeiter'), days.size]") \
        == [True, False, 1]
    seite.js("() => { openLevel(0); startLesson(); }")
    assert seite.js("() => sichtbar('lesson')")
    # Das Netz kommt zurueck - mitten in der Lektion passiert nichts.
    attrappe.abbruch = False
    seite.js(ONLINE)
    assert seite.js("() => [sichtbar('lesson'), sichtbar('profileView')]") == [True, False]
    # Auf der Startseite kommt die Anmeldung.
    seite.js("() => showHome()")
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["profileView"] and z["tage"] == 1
    assert seite.fehler == []


def test_netzfehler_beim_anmelden_erst_einmal_weiterlernen(seite, heute_stand, cloud_html):
    attrappe = _starten(seite, cloud_html, stand=_gelernt(heute_stand))
    attrappe.abbruch = True
    _mail_anmelden(seite, "ich@probe.example", "geheim-123")
    assert seite.js("""() => [document.getElementById('kontoNote').textContent,
                              document.getElementById('anmOffline').hidden,
                              document.getElementById('anmOffline').textContent]""") \
        == [_t(seite, "konto.fehler_netz"), False, _t(seite, "anm.weiterlernen")]
    seite.page.click("#anmOffline")
    assert seite.js(ZUSTAND)["sicht"] == ["pfad"]
    seite.js("() => { openLevel(0); showHome(); }")
    assert seite.js(ZUSTAND)["sicht"] == ["pfad"]      # bis zum naechsten 'online'
    attrappe.abbruch = False
    seite.js("() => window.dispatchEvent(new Event('online'))")
    assert seite.js(ZUSTAND)["sicht"] == ["profileView"]
    assert seite.fehler == []


def test_anmeldung_von_aussen_ungueltig(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    uid = attrappe.konto_anlegen("ich@probe.example", "geheim-123")
    _starten(seite, cloud_html, stand=_gelernt(heute_stand), attrappe=attrappe)
    _mail_anmelden(seite, "ich@probe.example", "geheim-123")
    alt = "() => { const m = JSON.parse(localStorage.getItem('zmaj_cloud')); m.gelesen = '2026-01-01'; localStorage.setItem('zmaj_cloud', JSON.stringify(m)); }"
    # Netzfehler oder 503: angemeldet bleiben.
    for fehler in (503, None):
        seite.js(alt)
        attrappe.token_fehler = fehler
        attrappe.abbruch = fehler is None
        attrappe.anfragen.clear()
        _neu_laden(seite)
        _warte(seite, lambda: any("securetoken" in a[1] for a in attrappe.anfragen))
        _fertig(seite)
        z = seite.js(ZUSTAND)
        assert z["sicht"] == ["pfad"] and z["merker"]["uid"] == uid, fehler
    attrappe.abbruch = False
    # Firebase sagt: die Anmeldung gilt nicht mehr.
    seite.js(alt)
    attrappe.token_fehler = "TOKEN_EXPIRED"
    _neu_laden(seite)
    seite.page.wait_for_function("() => sichtbar('profileView')")
    z = seite.js(ZUSTAND)
    assert z["merker"] is None and z["woerter"] == 1 and z["titel"] == _t(seite, "konto.anmelden_titel")
    assert "abmelden" in _aufrufe(seite)
    assert seite.js("() => sessionStorage.getItem('probe_nativ')") is None
    assert seite.fehler == []


# --------------------------------------------------- abmelden, loeschen ---

def test_abmelden(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    uid = attrappe.konto_anlegen("ich@probe.example", "geheim-123")
    _starten(seite, cloud_html, stand=_gelernt(heute_stand), attrappe=attrappe)
    _mail_anmelden(seite, "ich@probe.example", "geheim-123")
    seite.js("() => showKonto()")
    assert seite.js("""() => [document.getElementById('setProfilMail').textContent,
                              document.getElementById('setGesichert').textContent,
                              document.getElementById('setPwZeile').hidden,
                              document.getElementById('setProfilSub').hidden,
                              document.getElementById('setWegSub').textContent]""") == [
        "✉ ich@probe.example",
        _t(seite, "set.gesichert", {"datum": seite.js("() => new Date().toLocaleDateString(SPRACHE)")}),
        True, True, _t(seite, "set.konto_weg_sub")]
    # Ohne Netz: nein.
    seite.js(OFFLINE)
    seite.page.click("#setLogout")
    assert seite.js("() => document.getElementById('setLogoutNote').textContent") == _t(seite, "set.abmelden_netz")
    assert seite.js(ZUSTAND)["merker"] is not None
    seite.js("() => { delete navigator.onLine; }")
    # Mit Netz: Rueckfrage, ein letztes Schreiben, dann leer und abgemeldet.
    seite.js("() => known.add('probe:zuletzt')")
    attrappe.anfragen.clear()
    seite.page.click("#setLogout")
    seite.page.click("#frJa")
    seite.page.wait_for_function("() => sichtbar('profileView')")
    assert [w for w in wege(attrappe)] == [("GET", dok_pfad(uid)), ("PATCH", dok_pfad(uid))]
    assert "probe:zuletzt" in json.loads(attrappe.doks[uid]["daten"]["stringValue"])["stand"]["gewusst"]
    z = seite.js(ZUSTAND)
    assert z["merker"] is None and z["woerter"] == 0 and z["tage"] == 0
    assert z["titel"] == _t(seite, "konto.anmelden_titel") and z["frage"] == _t(seite, "anm.text_abgemeldet")
    assert "abmelden" in _aufrufe(seite)
    # Auch nach einem Neustart steht die Anmeldung da, obwohl nichts gelernt ist.
    _neu_laden(seite)
    assert seite.js(ZUSTAND)["sicht"] == ["profileView"]
    # Wieder angemeldet: der Stand kommt aus dem Konto zurueck.
    _mail_anmelden(seite, "ich@probe.example", "geheim-123")
    assert seite.js("() => known.has('probe:zuletzt') && known.has('probe:geraet')")
    assert seite.js("() => localStorage.getItem('zmaj_abgemeldet')") is None
    assert seite.fehler == []


def test_konto_loeschen_mit_passwort(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    uid = attrappe.konto_anlegen("ich@probe.example", "geheim-123")
    _starten(seite, cloud_html, stand=_gelernt(heute_stand), attrappe=attrappe)
    _mail_anmelden(seite, "ich@probe.example", "geheim-123")
    seite.js("() => showKonto()")
    seite.page.click("#setKontoWeg")
    assert seite.js("() => document.getElementById('wegForm').style.display") == "block"
    # Falsches Passwort: nichts ist geloescht.
    attrappe.anfragen.clear()
    seite.page.fill("#wegPw", "falsch-123")
    seite.page.click("#wegKnopf")
    seite.page.click("#frJa")
    seite.page.wait_for_function("() => document.getElementById('wegNote').textContent === t('konto.fehler_mail_pw')")
    assert seite.js("() => document.getElementById('wegNote').textContent") == _t(seite, "konto.fehler_mail_pw")
    assert wege(attrappe) == [("POST", KONTO + "signInWithPassword")]
    assert uid in attrappe.doks and "ich@probe.example" in attrappe.konten
    assert seite.js(ZUSTAND)["merker"]["uid"] == uid
    # Richtig: frisch anmelden, Dokument weg, Konto weg, Stand leer.
    attrappe.anfragen.clear()
    seite.page.fill("#wegPw", "geheim-123")
    seite.page.click("#wegKnopf")
    seite.page.click("#frJa")
    seite.page.wait_for_function("() => sichtbar('profileView')")
    assert wege(attrappe) == [("POST", KONTO + "signInWithPassword"), ("DELETE", dok_pfad(uid)),
                              ("POST", KONTO + "delete")]
    assert uid not in attrappe.doks and attrappe.konten == {}
    z = seite.js(ZUSTAND)
    assert z["merker"] is None and z["woerter"] == 0
    assert seite.js("() => document.getElementById('anmNote').textContent") == _t(seite, "set.konto_weg_fertig")
    assert "abmelden" in _aufrufe(seite)
    assert seite.fehler == []


# ------------------------------------------------ Einstufung, keine Karten ---

def test_ich_habe_schon_ein_konto_und_keine_karten_ueber_der_anmeldung(seite, heute_stand, cloud_html):
    _starten(seite, cloud_html, stand=heute_stand())
    seite.js("() => einstufungWahl()")
    assert seite.js("() => document.getElementById('eKonto').textContent") == _t(seite, "konto.zurueck_anmelden")
    seite.page.click("#eKonto")
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["profileView"] and z["frage"] == _t(seite, "anm.text_zurueck")
    # Wer noch nicht muss, kommt hier wieder heraus.
    seite.js("() => zurueckTaste()")
    assert seite.js(ZUSTAND)["sicht"] == ["pfad"]
    assert seite.js("() => document.getElementById('btnSettings').style.display") == "inline-block"
    # Mit dem Tor: keine Karte ueber der Anmeldeseite.
    seite.js("() => { known.add('probe:x'); showHome(); }")
    assert seite.js(ZUSTAND)["sicht"] == ["profileView"]
    seite.js("""() => { geschenkOffen = true; geschenkNachreichen(); einstufungGefragt = false; einstufungBereit = true;
                       einstufungAnbieten(); bewertungDran = true; kartenNachreichen(); }""")
    seite.page.wait_for_timeout(900)
    assert seite.js("() => document.querySelectorAll('.nachfrage').length") == 0
    assert seite.fehler == []
