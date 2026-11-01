# -*- coding: utf-8 -*-
"""Der Werbeschalter fuer Abonnenten (01.11.2026) - im echten Browser.

Ajdin beim Test der 1.2: "bei werbung statt wahl ändern soll so ein
schalter sein", auf die Rueckfrage auch fuer Abonnenten: "Ja, auch
Schalter". Bis dahin sahen Abonnenten auf dem Handy eine eigene Zeile mit
dem Knopf "Wahl ändern" (setWiderrufBox, Punkt 8 vom 30.09.2026).

Das Handy stellt hier ein nachgebautes AdMob-Plugin und ZmajEinwilligung
(window.probe zaehlt jeden Aufruf). Geprueft wird:
  - Beim Start und beim Oeffnen der Einstellungen spricht niemand mit
    Google: kein initialize, kein requestConsentInfo, AdMobP bleibt leer.
    Der Schalter zeigt den Stand auf dem Geraet.
  - Im EWR oeffnet ein Tipp Googles Fenster, danach zeigt der Schalter,
    was dort gewaehlt wurde - in beide Richtungen.
  - Ausserhalb des EWR (kein Aenderungsweg verlangt) legt der Schalter
    sofort um, wie der eigene Schalter ohne AdMob.
  - Ohne Netz bleibt der Schalter, darunter steht voll.fehler.
  - Den alten Knopf gibt es nicht mehr; am PC (ohne AdMob) sehen
    Abonnenten keine Werbezeile, alle anderen den Schalter wie bisher.
"""

# Das nachgebaute Plugin. weg: was Google zum Aendern verlangt; wahl: was
# der Nutzer in Googles Fenster antippt; fehler: requestConsentInfo wirft.
HANDY = r"""
(() => {
  window.probe = {aufrufe: [], weg: 'REQUIRED', wahl: null, tcf: null, fehler: null};
  const merk = n => window.probe.aufrufe.push(n);
  window.Capacitor = {Plugins: {
    AdMob: {
      initialize: async () => { merk('initialize'); },
      requestConsentInfo: async () => { merk('requestConsentInfo');
        if(window.probe.fehler) throw new Error(window.probe.fehler);
        return {status: 'OBTAINED', canRequestAds: true, isConsentFormAvailable: true,
                privacyOptionsRequirementStatus: window.probe.weg}; },
      showConsentForm: async () => { merk('showConsentForm'); return {}; },
      showPrivacyOptionsForm: async () => { merk('showPrivacyOptionsForm'); window.probe.tcf = window.probe.wahl; return {}; },
    },
    ZmajEinwilligung: {
      stand: async () => { merk('stand');
        return window.probe.tcf === null ? {bekannt: false} : {bekannt: true, personalisiert: window.probe.tcf}; },
    },
  }};
})();
"""

ZEILE = """() => ({
  box: document.getElementById('setWerbungBox').offsetParent !== null,
  an: document.getElementById('swWerbung').getAttribute('aria-checked'),
  unten: document.getElementById('setWerbungStand').textContent,
  alt: !!document.getElementById('setWiderrufBox') || !!document.getElementById('einwWiderruf'),
})"""


def _t(seite, k):
    return seite.js("k => t(k)", k)


def _abonnent(seite, heute_stand, handy=True):
    """Ein Abonnent (zmaj_voll = '1'), auf dem Handy mit AdMob oder am PC."""
    if handy:
        seite.page.add_init_script(HANDY)
    seite.starten(stand=heute_stand())
    seite.js("() => localStorage.setItem('zmaj_voll', '1')")
    seite.neu_laden()
    assert seite.js("() => [unlimited(), admobDa()]") == [True, False]


def _tippen(seite):
    seite.page.click("#swWerbung")
    seite.page.wait_for_function("() => !werbungLaeuft")


def _neu(seite, vorher):
    return seite.js("() => window.probe.aufrufe")[vorher:]


def test_abonnent_sieht_schalter_und_googles_fenster(seite, heute_stand):
    _abonnent(seite, heute_stand)
    # Beim Start: kein Wort mit Google.
    start = seite.js("() => window.probe.aufrufe")
    assert not {"initialize", "requestConsentInfo", "showConsentForm", "showPrivacyOptionsForm"} & set(start), start
    # Einstellungen auf: der Schalter, mit dem Stand auf dem Geraet - und
    # wieder keine Frage, nicht einmal an ZmajEinwilligung.
    seite.js("() => { showSettings(); }")
    assert seite.js(ZEILE) == {"box": True, "an": "false", "unten": _t(seite, "set.einwilligung_nein"), "alt": False}
    assert _neu(seite, len(start)) == []

    # Tipp: Googles Fenster, dort "ja" - der Schalter steht danach auf an.
    seite.js("() => { window.probe.wahl = true; }")
    n = len(seite.js("() => window.probe.aufrufe"))
    _tippen(seite)
    assert _neu(seite, n) == ["requestConsentInfo", "showPrivacyOptionsForm", "stand"]
    assert seite.js(ZEILE) == {"box": True, "an": "true", "unten": _t(seite, "set.einwilligung_ja"), "alt": False}
    assert seite.js("() => [localStorage.getItem('zmaj_pers'), admobDa()]") == ["an", False]

    # Und zurueck: dort "nein" - der Schalter folgt.
    seite.js("() => { window.probe.wahl = false; }")
    n = len(seite.js("() => window.probe.aufrufe"))
    _tippen(seite)
    assert _neu(seite, n) == ["requestConsentInfo", "showPrivacyOptionsForm", "stand"]
    assert seite.js(ZEILE)["an"] == "false"
    assert seite.js("() => localStorage.getItem('zmaj_pers')") == "aus"
    # Nie das Werbe-SDK gestartet, nie AdMobP gesetzt.
    assert "initialize" not in seite.js("() => window.probe.aufrufe") and not seite.js("() => admobDa()")
    assert seite.fehler == []


def test_abonnent_ausserhalb_des_ewr_legt_sofort_um(seite, heute_stand):
    _abonnent(seite, heute_stand)
    seite.js("() => { window.probe.weg = 'NOT_REQUIRED'; showSettings(); }")
    assert seite.js(ZEILE)["an"] == "false"
    n = len(seite.js("() => window.probe.aufrufe"))
    _tippen(seite)
    assert _neu(seite, n) == ["requestConsentInfo"]
    assert seite.js(ZEILE) == {"box": True, "an": "true", "unten": _t(seite, "set.einwilligung_ja"), "alt": False}
    _tippen(seite)
    assert seite.js(ZEILE)["an"] == "false"
    assert seite.js("() => localStorage.getItem('zmaj_pers')") == "aus"
    assert "showPrivacyOptionsForm" not in seite.js("() => window.probe.aufrufe")
    assert seite.fehler == []


def test_abonnent_ohne_netz_schalter_bleibt(seite, heute_stand):
    _abonnent(seite, heute_stand)
    seite.js("() => { window.probe.fehler = 'offline'; showSettings(); }")
    _tippen(seite)
    assert seite.js(ZEILE) == {"box": True, "an": "false", "unten": _t(seite, "voll.fehler"), "alt": False}
    assert seite.js("() => localStorage.getItem('zmaj_pers')") is None
    # Neu gezeigt steht wieder der Stand da.
    seite.js("() => { showSettings(); }")
    assert seite.js(ZEILE)["unten"] == _t(seite, "set.einwilligung_nein")
    assert seite.fehler == []


def test_am_pc_wie_bisher(seite, heute_stand):
    """Am PC gibt es Googles Fenster nicht: Abonnenten sehen keine
    Werbezeile. Ohne Vollversion bleibt der eigene Schalter, der sofort
    umlegt - und nirgends steht der alte Knopf."""
    _abonnent(seite, heute_stand, handy=False)
    seite.js("() => { showSettings(); }")
    assert seite.js(ZEILE) == {"box": False, "an": "false", "unten": "", "alt": False}
    seite.js("() => { localStorage.setItem('zmaj_voll', '0'); }")
    seite.neu_laden()
    seite.js("() => { showSettings(); }")
    assert seite.js(ZEILE)["box"] is True
    _tippen(seite)
    assert seite.js(ZEILE)["an"] == "true"
    assert seite.fehler == []
