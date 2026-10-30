# -*- coding: utf-8 -*-
"""Die App als iPhone/iPad-App - im Browser nachgestellt (30.10.2026).

Ajdin am 30.10.2026: "ja fang mit der ios version an"; Plan und
Entscheidungen in Release\\iOS_Plan.md. Ein Mac fehlt, also wird iOS hier
so nachgestellt wie Android in den anderen Tests: window.Capacitor mit
getPlatform() = 'ios' und Attrappen der Plugins aus der iOS-Huelle
(ZmajAnmeldung mit appleAusweis und anbieter, ZmajAbo mit verwalten und
wiederherstellen, ZmajBewertung, Share, App). Jede Pruefung hat ihre
Gegenprobe mit 'android': dort bleibt alles wie vorher.

Was sich so nicht pruefen laesst (StoreKit, Apples Fenster, ATT, der
Stummschalter, die Raender am echten Geraet), steht in iOS_Plan.md 3.9.
"""
import re

import pytest

from firebase_attrappe import UID, dok_pfad, wege
from test_anmeldung import KONTO, ZUSTAND, _aufrufe, _fertig, _gelernt, _starten, _t, _warte

SPRACHEN = ("de", "en", "tr", "sv", "nl", "nb", "da", "fr")
VERBOTEN = re.compile(r"Google Play|Play Store|Play-butikk|Play Butik|Android|Google-Konto|Google account"
                      r"|Google hesab|Google-konto|compte Google|Google-account|Google Commerce")

# Die Attrappe der iOS-Huelle. %s ist die Plattform. Aufrufe landen in
# sessionStorage (probe_aufrufe), wie in test_anmeldung.py.
HUELLE = r"""
(() => {
  const ss = window.sessionStorage;
  const lies = (k, d) => { try{ return JSON.parse(ss.getItem(k) || d); }catch(e){ return JSON.parse(d); } };
  const merk = (name, daten) => { const a = lies('probe_aufrufe', '[]'); a.push([name, daten || null]); ss.setItem('probe_aufrufe', JSON.stringify(a)); };
  const horcher = async () => ({remove(){}});
  window.Capacitor = {getPlatform: () => '%s', isNativePlatform: () => true, Plugins: {
    App: {addListener: horcher},
    Share: {share: async (o) => { merk('share', o); }},
    ZmajAnmeldung: {
      anbieter: async () => { merk('anbieter'); return lies('probe_anbieter', '{"google": true, "apple": true}'); },
      googleAusweis: async (o) => { merk('googleAusweis', o); return {idToken: 'google-probe'}; },
      appleAusweis: async (o) => { merk('appleAusweis', o);
        const f = ss.getItem('probe_apple_fehler');
        if(f){ const e = new Error(f); e.code = f; throw e; }
        return {idToken: 'apple-probe', nonce: 'nonce-probe', code: 'code-probe'}; },
      sitzungMerken: async (o) => { merk('sitzungMerken', o); ss.setItem('probe_nativ', JSON.stringify(o)); return {ok: true}; },
      sitzungHolen: async () => lies('probe_nativ', '{}'),
      restoreSichern: async () => ({ok: false, grund: 'ios'}),
      restoreHolen: async () => ({}),
      abmelden: async () => { merk('abmelden'); ss.removeItem('probe_nativ'); return {ok: true}; },
    },
    ZmajAbo: {
      stand: async () => ({bekannt: true, aktiv: ss.getItem('probe_aktiv') === '1', gesperrt: false,
                           plan: ss.getItem('probe_aktiv') === '1' ? 'jahr' : null, probe: false}),
      preise: async () => ({ok: true, plaene: [
        {plan: 'monat', preis: '2,99 €', micros: 2990000, waehrung: 'EUR', zeitraum: 'P1M'},
        {plan: 'jahr', preis: '19,99 €', micros: 19990000, waehrung: 'EUR', zeitraum: 'P1Y', gratis: 'P1W'}]}),
      kaufen: async (o) => { merk('kaufen', o); return {ok: true}; },
      aufJahrWechseln: async () => { merk('aufJahrWechseln'); return {ok: true}; },
      verwalten: async () => { merk('verwalten'); return {ok: true}; },
      wiederherstellen: async () => { merk('wiederherstellen'); return {ok: true, aktiv: false}; },
      addListener: horcher,
    },
    ZmajBewertung: {
      imApp: async () => { merk('imApp'); return {ok: true, ms: 99999}; },
      storeOeffnen: async () => { merk('storeOeffnen'); },
    },
  }};
})();
"""


def _app(seite, plattform, heute_stand, sprache="de", html=None):
    """Die Demo (ohne Anmeldung) als iOS- oder Android-App starten. html:
    eine geaenderte index.html, etwa mit eingesetzter Apple-ID."""
    if html is not None:
        seite.page.route("**/app/index.html", lambda r: r.fulfill(
            status=200, content_type="text/html; charset=utf-8", body=html))
    seite.page.add_init_script(HUELLE % plattform)
    seite.starten(sprache=sprache, stand=heute_stand())
    seite.js("() => sessionStorage.removeItem('probe_aufrufe')")


def _sichtbar(seite, sel):
    return seite.js("(s) => { const e = document.querySelector(s); return !!e && !!(e.offsetWidth || e.offsetHeight); }", sel)


# ---------------------------------------------------- Weiche und Raender ---
@pytest.mark.parametrize("plattform", ["ios", "android"])
def test_zurueck_knopf_und_raender(seite, heute_stand, plattform):
    """Auf iOS gibt es keine Zurueck-Taste - der Knopf oben steht dort wie im
    Browser. Die Seite reicht unter Notch und Home-Leiste (viewport-fit) und
    haelt mit env(safe-area-inset-*) Abstand. Android: wie vorher."""
    _app(seite, plattform, heute_stand)
    ios = plattform == "ios"
    assert seite.js("() => [PLATTFORM, document.documentElement.dataset.plattform]") == [plattform] * 2
    vp = seite.js("() => document.querySelector('meta[name=viewport]').content")
    assert ("viewport-fit=cover" in vp) is ios
    seite.js("() => showSettings()")
    assert _sichtbar(seite, "#btnBack") is ios
    if ios:
        seite.page.click("#btnBack")
        seite.page.wait_for_function("() => sichtbar('pfad')")
    # Polster oben: 16 px plus Rand (im Browser 0) - der Stil gilt nur auf iOS.
    regel = seite.js("""() => [...document.styleSheets].flatMap(s => { try{ return [...s.cssRules]; }catch(e){ return []; } })
                         .some(r => r.selectorText === 'html[data-plattform="ios"] body')""")
    assert regel is True
    assert seite.fehler == []


def test_keine_andere_plattform_auf_dem_bildschirm(seite, heute_stand):
    """Richtlinie 2.3.10: In keiner der acht Sprachen steht auf iOS "Google
    Play", "Play Store" oder "Android" - nicht auf dem Lernpfad, nicht in den
    Einstellungen, nicht im Kaufkasten."""
    for sprache in SPRACHEN:
        _app(seite, "ios", heute_stand, sprache=sprache)
        texte = [seite.js("() => document.body.innerText")]
        seite.js("() => showSettings()")
        seite.page.wait_for_function("() => document.getElementById('setVollBox').style.display === ''")
        texte.append(seite.js("() => document.body.innerText"))
        seite.page.click("#swVoll")
        seite.page.wait_for_selector(".nachfrage #aboKauf")
        texte.append(seite.js("() => document.querySelector('.nachfrage').innerText"))
        for text in texte:
            m = VERBOTEN.search(text)
            assert not m, (sprache, text[max(0, m.start() - 80):m.end() + 20])
        assert seite.fehler == [], sprache


@pytest.mark.parametrize("plattform", ["ios", "android"])
def test_einstellungen(seite, heute_stand, plattform):
    """iOS: kein Vibrations-Schalter, "Kaeufe wiederherstellen" da, ohne
    Apple-ID kein Bewerten/Empfehlen, keine Computerstimme, und siebenmal
    auf die Versionszeile tippen tut nichts. Android: alles wie vorher."""
    _app(seite, plattform, heute_stand)
    ios = plattform == "ios"
    seite.js("() => showSettings()")
    seite.page.wait_for_function("() => document.getElementById('setVollBox').style.display === ''")
    assert _sichtbar(seite, "#swHaptik") is not ios
    assert _sichtbar(seite, "#aboWiederherstellen") is ios
    assert _sichtbar(seite, "#setBewerten") is not ios
    assert _sichtbar(seite, "#setEmpfehlen") is not ios
    assert seite.js("() => [hasTTS, canBuzz].some(Boolean)") is not ios
    for _ in range(7):
        seite.page.click("#ueberZeile")
    seite.page.wait_for_timeout(300)
    wort = seite.js("() => !!document.querySelector('.nachfrage input')")
    assert wort is not ios
    assert seite.fehler == []


def test_kaufkasten_und_abo_auf_ios(seite, heute_stand):
    """Apples Pflichtangaben (3.1.2): Laufzeit und Preis auf den Karten, die
    Gratiswoche mit dem Preis danach, Verlaengerung und Kuendigung bei Apple,
    Links zu Nutzungsbedingungen und Datenschutz, Kaeufe wiederherstellen.
    "Abo verwalten" fuehrt zu Apple (ZmajAbo.verwalten), nie zu Google."""
    _app(seite, "ios", heute_stand)
    seite.js("() => showSettings()")
    seite.page.wait_for_function("() => document.getElementById('setVollBox').style.display === ''")
    seite.page.click("#swVoll")
    seite.page.wait_for_selector(".nachfrage #aboKauf")
    kasten = seite.js("() => document.querySelector('.nachfrage').innerText")
    assert "2,99 €" in kasten and "19,99 €" in kasten
    assert _t(seite, "voll.hinweis_ios") in kasten
    assert _t(seite, "voll.gratis_jahr", {"n": 7, "preis": "19,99 €"}) in kasten
    for knopf in ("#aboAgb", "#aboDs", "#aboWh"):
        assert _sichtbar(seite, knopf), knopf
    # Nutzungsbedingungen als eigene Ebene, der Kaufkasten bleibt darunter.
    seite.page.click("#aboAgb")
    seite.page.wait_for_selector(".rechtsebene .legal")
    assert len(seite.js("() => document.querySelector('.rechtsebene .legal').innerText")) > 500
    seite.page.click("#rechtZu")
    assert seite.js("() => !document.querySelector('.rechtsebene') && !!document.querySelector('#aboKauf')")
    # Wiederherstellen aus dem Kaufkasten.
    seite.page.click("#aboWh")
    _warte(seite, lambda: "wiederherstellen" in _aufrufe(seite))
    seite.page.wait_for_function("() => document.getElementById('setVollNote').textContent !== ''")
    assert seite.js("() => document.getElementById('setVollNote').textContent") == _t(seite, "voll.nichts_gefunden")
    # Mit laufendem Abo: verwalten bei Apple.
    seite.js("() => { sessionStorage.setItem('probe_aktiv', '1'); return vollAbgleichen(); }")
    seite.page.wait_for_function("() => premium")
    fenster = []
    seite.page.on("popup", lambda p: fenster.append(p.url))
    seite.page.click("#aboVerwalten")
    _warte(seite, lambda: "verwalten" in _aufrufe(seite))
    assert fenster == []
    assert not _sichtbar(seite, "#aboWiederherstellen")
    assert seite.fehler == []


def test_wechsel_aufs_jahr_text_fuer_ios(seite, heute_stand):
    """Auf iOS ist der Wechsel ein Upgrade: Apple erstattet den Rest des
    Monats (Entscheidung 9) - nicht Googles Text."""
    _app(seite, "ios", heute_stand)
    seite.js("() => { aboPlan = 'monat'; aboJahrPreis = '19,99 €'; jahrWechselZeigen(); }")
    seite.page.wait_for_selector("#wechselOk")
    text = seite.js("() => document.querySelector('.nachfrage').innerText")
    assert _t(seite, "voll.wechsel_text_ios", {"preis": "19,99 €"}) in text
    assert "Google" not in text
    assert seite.fehler == []


@pytest.mark.parametrize("plattform", ["ios", "android"])
def test_bewertung(seite, heute_stand, plattform):
    """iOS: keine eigene Karte, Apples Fenster ueber ZmajBewertung.imApp(),
    und danach nicht der Store. Android: die Karte wie bisher."""
    _app(seite, plattform, heute_stand)
    seite.js("() => { bewertungDran = true; anzeigeZuletzt = 0; kartenNachreichen(); }")
    seite.page.wait_for_timeout(1200)
    karte = seite.js("() => !!document.querySelector('.nachfrage #bwJa')")
    if plattform == "ios":
        assert not karte
        assert _aufrufe(seite) == ["imApp"]
        assert seite.js("() => bewertung.gezeigt.length") == 1
    else:
        assert karte and "imApp" not in _aufrufe(seite)
    assert seite.fehler == []


def test_store_links_mit_apple_id(seite, heute_stand, wurzelordner):
    """Mit der Apple-ID (app_bauen.py --ios setzt sie ein) fuehren Bewerten
    und Empfehlen in den App Store."""
    import io
    import os
    html = io.open(os.path.join(wurzelordner, "app", "index.html"), encoding="utf-8", newline="").read()
    assert html.count("const APPLE_APP_ID = '__APPLE_ID__';") == 1
    html = html.replace("const APPLE_APP_ID = '__APPLE_ID__';", "const APPLE_APP_ID = '1234567890';")
    _app(seite, "ios", heute_stand, html=html)
    seite.js("() => showSettings()")
    assert _sichtbar(seite, "#setBewerten") and _sichtbar(seite, "#setEmpfehlen")
    seite.page.click("#setEmpfehlen")
    _warte(seite, lambda: "share" in _aufrufe(seite))
    assert _aufrufe(seite, "share")[0]["url"] == "https://apps.apple.com/app/id1234567890"
    seite.page.click("#setBewerten")
    _warte(seite, lambda: "storeOeffnen" in _aufrufe(seite))
    assert seite.fehler == []


@pytest.mark.parametrize("plattform", ["ios", "android"])
def test_anzeige_melden(seite, heute_stand, plattform):
    """Richtlinie 2.5.18, nur iOS: nach einer Vollbildanzeige kurz "Anzeige
    melden", als Mail an uns mit Zeit und Art."""
    _app(seite, plattform, heute_stand)
    seite.js("() => { anzeigeMerken(false); anzeigeMeldenAnbieten(); }")
    knopf = seite.js("() => { const b = document.querySelector('.meldenote button'); return b ? b.textContent : null; }")
    if plattform == "ios":
        assert knopf == _t(seite, "werbung.melden")
        link = seite.js("() => anzeigeMeldenLink()")
        assert link.startswith("mailto:zmaj.lernapp@gmail.com?subject=")
        assert "interstitial" in link and "ios" in link
    else:
        assert knopf is None
    assert seite.fehler == []


# ------------------------------------------------------------- Anmeldung ---
def _ios_anmelden(seite, cloud_html, heute_stand, plattform="ios", anbieter=None):
    seite.page.add_init_script(HUELLE % plattform)
    vorbereiten = None
    if anbieter is not None:
        vorbereiten = "() => sessionStorage.setItem('probe_anbieter', %r)" % __import__("json").dumps(anbieter)
    return _starten(seite, cloud_html, stand=_gelernt(heute_stand), plugin=False, vorbereiten=vorbereiten)


def test_anmeldung_mit_apple_und_google(seite, heute_stand, cloud_html):
    """iOS: "Mit Apple anmelden" ueber "Mit Google anmelden", dazu
    "Spaeter". Apples Ausweis geht mit dem rohen nonce an Firebase."""
    attrappe = _ios_anmelden(seite, cloud_html, heute_stand)
    seite.page.wait_for_function("() => anmAnbieter !== null")
    assert _sichtbar(seite, "#anmApple") and _sichtbar(seite, "#anmGoogle") and _sichtbar(seite, "#anmSpaeter")
    assert seite.js("() => document.getElementById('anmAppleText').textContent") == "Mit Apple anmelden"
    oben = seite.js("() => [document.getElementById('anmApple').getBoundingClientRect().top,"
                    " document.getElementById('anmGoogle').getBoundingClientRect().top]")
    assert oben[0] < oben[1]
    # Abgebrochen: nichts zu sagen, nichts gefragt.
    seite.js("() => sessionStorage.setItem('probe_apple_fehler', 'abgebrochen')")
    seite.page.click("#anmApple")
    _fertig(seite)
    assert seite.js("() => document.getElementById('anmNote').textContent") == ""
    assert attrappe.anfragen == []
    seite.js("() => sessionStorage.setItem('probe_apple_fehler', 'fehler')")
    seite.page.click("#anmApple")
    _fertig(seite)
    assert seite.js("() => document.getElementById('anmNote').textContent") == _t(seite, "konto.fehler_apple")
    seite.js("() => sessionStorage.removeItem('probe_apple_fehler')")
    seite.page.click("#anmApple")
    _fertig(seite)
    z = seite.js(ZUSTAND)
    assert z["sicht"] == ["pfad"] and z["merker"]["art"] == "apple" and z["merker"]["uid"] == UID
    assert wege(attrappe)[0] == ("POST", KONTO + "signInWithIdp")
    assert seite.fehler == []


def test_ohne_ios_client_id_kein_google_knopf(seite, heute_stand, cloud_html):
    """Steht in der Huelle keine iOS-Client-ID, sagt anbieter() google:false -
    dann gibt es den Google-Knopf nicht, Apple und E-Mail bleiben."""
    _ios_anmelden(seite, cloud_html, heute_stand, anbieter={"google": False, "apple": True})
    seite.page.wait_for_function("() => anmAnbieter !== null")
    assert not _sichtbar(seite, "#anmGoogle")
    assert _sichtbar(seite, "#anmApple") and _sichtbar(seite, "#anmMail")
    assert seite.fehler == []


def test_spaeter_einmal_am_tag(seite, heute_stand, cloud_html):
    """Richtlinie 5.1.1(v): auf iOS darf man ohne Konto weiterlernen. Nach
    "Spaeter" bleibt das Tor fuer heute offen, auch nach einem Neustart."""
    _ios_anmelden(seite, cloud_html, heute_stand)
    seite.page.click("#anmSpaeter")
    seite.page.wait_for_function("() => sichtbar('pfad')")
    seite.js("() => startLesson()")
    assert seite.js("() => !sichtbar('profileView')")
    seite.page.reload()
    seite.page.wait_for_function("() => typeof standGeladen !== 'undefined' && standGeladen && sichtbar('pfad')")
    assert seite.js("() => !sichtbar('profileView') && anmeldungFaellig() === false")
    # Morgen fragt es wieder.
    seite.js("() => localStorage.setItem('zmaj_anm_spaeter', '2000-01-01')")
    assert seite.js("() => anmeldungFaellig()") is True
    assert seite.fehler == []


def test_android_ohne_apple_und_ohne_spaeter(seite, heute_stand, cloud_html):
    """Gegenprobe: Android bleibt bei Google und E-Mail, Pflicht wie seit v109."""
    _ios_anmelden(seite, cloud_html, heute_stand, plattform="android")
    seite.page.wait_for_timeout(300)
    assert not _sichtbar(seite, "#anmApple") and not _sichtbar(seite, "#anmSpaeter")
    assert _sichtbar(seite, "#anmGoogle")
    assert "anbieter" not in _aufrufe(seite)
    assert seite.fehler == []


def test_konto_loeschen_mit_apple_widerruft(seite, heute_stand, cloud_html):
    """Vor dem Loeschen frisch bei Apple anmelden und Apples Token widerrufen
    (accounts:revokeToken, tokenType CODE) - dann Sicherung und Konto weg."""
    attrappe = _ios_anmelden(seite, cloud_html, heute_stand)
    seite.page.wait_for_function("() => anmAnbieter !== null")
    seite.page.click("#anmApple")
    _fertig(seite)
    assert seite.js(ZUSTAND)["merker"]["art"] == "apple"
    seite.js("() => showKonto()")
    attrappe.anfragen.clear()
    seite.page.click("#setKontoWeg")
    frage = seite.js("() => document.querySelector('.nachfrage').innerText")
    assert _t(seite, "set.konto_weg_apple") in frage
    seite.page.click("#frJa")
    seite.page.wait_for_function("() => sichtbar('profileView')")
    assert len(_aufrufe(seite, "appleAusweis")) == 2
    assert wege(attrappe) == [("POST", KONTO + "signInWithIdp"),
                              ("POST", "identitytoolkit.googleapis.com/v2/accounts:revokeToken"),
                              ("DELETE", dok_pfad()), ("POST", KONTO + "delete")]
    w = attrappe.widerrufen[0]
    assert (w["providerId"], w["tokenType"], w["token"]) == ("apple.com", "CODE", "code-probe")
    assert attrappe.konto_weg and seite.js(ZUSTAND)["merker"] is None
    assert seite.fehler == []


# ----------------------------------------------------------- Vorfuehrung ---
def test_vorfuehrung_des_cloud_baus(seite, heute_stand, wurzelordner, tmp_path):
    """vorfuehrung_ios.js, wie app_bauen.py --ios --ci --vorfuehrung sie in
    den Cloud-Pruefbau haengt (Stufe A8, 30.10.2026). Runde 1 laesst den
    ersten Start, wie er ist; Runde 2 entzieht der Seite AdMob, setzt die
    Preise aus Zmaj.storekit ein, wenn StoreKit leer antwortet, und meldet
    die Schirme in fester Reihenfolge - ohne Skriptfehler und ohne Netz.
    Hier mit iPhone-Breite: zuletzt die Tracking-Frage ueber AdMob."""
    import io
    import os
    import shutil
    import app_bauen
    www = tmp_path / "www"
    www.mkdir()
    shutil.copyfile(os.path.join(wurzelordner, "app", "index.html"), str(www / "index.html"))
    app_bauen.vorfuehrung_einsetzen(str(www))
    html = io.open(str(www / "index.html"), encoding="utf-8", newline="").read()
    skript = io.open(str(www / "vorfuehrung.js"), encoding="utf-8").read()
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=html))
    seite.page.route("**/app/vorfuehrung.js", lambda r: r.fulfill(
        status=200, content_type="text/javascript; charset=utf-8", body=skript))
    seite.page.set_viewport_size({"width": 440, "height": 956})
    meldungen = []
    seite.page.on("console", lambda m: meldungen.append(m.text) if m.text.startswith("ZMAJ-VORFUEHRUNG") else None)
    seite.page.add_init_script(HUELLE % "ios")
    # StoreKit im Simulator: leere Liste. Dazu AdMob mit Einwilligung und ATT.
    seite.page.add_init_script(r"""
      window.ZMAJ_VORFUEHRUNG_TAKT = 150;
      const ss = window.sessionStorage;
      const merk = (n) => { const a = JSON.parse(ss.getItem('probe_aufrufe') || '[]'); a.push([n, null]); ss.setItem('probe_aufrufe', JSON.stringify(a)); };
      window.Capacitor.Plugins.ZmajAbo.preise = async () => ({ok: true, plaene: []});
      window.Capacitor.Plugins.AdMob = {
        requestConsentInfo: async () => { merk('requestConsentInfo'); return {status: 'REQUIRED', isConsentFormAvailable: true}; },
        showConsentForm: async () => { merk('showConsentForm'); return {}; },
        requestTrackingAuthorization: async () => { merk('requestTrackingAuthorization'); },
      };
    """)
    seite.starten(stand=heute_stand())
    assert meldungen[:1] == ["ZMAJ-VORFUEHRUNG runde=1"]
    seite.page.reload()
    for _ in range(600):
        if any(m.startswith("ZMAJ-VORFUEHRUNG fertig") or m.startswith("ZMAJ-VORFUEHRUNG abbruch") for m in meldungen):
            break
        seite.page.wait_for_timeout(100)
    bilder = [m.split("bild=")[1].split()[0] for m in meldungen if "bild=" in m]
    assert bilder == ["startseite", "lektion", "einstellungen", "einstellungen_unten", "kaufkasten",
                      "anmeldung", "frage_tracking"], meldungen
    assert "ZMAJ-VORFUEHRUNG runde=2" in meldungen
    assert "ZMAJ-VORFUEHRUNG werbung aus (AdMob der Seite entzogen)" in meldungen
    assert "ZMAJ-VORFUEHRUNG preise aus Zmaj.storekit (StoreKit im Simulator leer)" in meldungen
    assert any(m.startswith("ZMAJ-VORFUEHRUNG anmeldung: apple=true google=true spaeter=true") for m in meldungen), meldungen
    assert not any("kaufkasten kam nicht" in m or "gescheitert" in m or "js-fehler" in m for m in meldungen), meldungen
    assert meldungen[-1] == "ZMAJ-VORFUEHRUNG fertig bilder=7 fehler=0", meldungen
    # Googles Fenster nie gefragt, Apples Tracking-Frage zuletzt schon.
    aufrufe = _aufrufe(seite)
    assert "requestConsentInfo" not in aufrufe and aufrufe[-1:] == ["requestTrackingAuthorization"]
    assert seite.fehler == [] and seite.fremd == []
