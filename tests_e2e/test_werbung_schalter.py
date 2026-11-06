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
    sofort um, wie der eigene Schalter ohne AdMob. Seit dem Pruefbericht
    vom 01.11.2026 fragt nur der erste Tipp der Sitzung bei Google nach,
    die weiteren legen sofort um, auch ohne Netz.
  - Ohne Netz bleibt der Schalter, darunter steht voll.fehler.
  - Kam das Abo erst, nachdem AdMob in dieser Sitzung gefragt hatte, startet
    ein Ja in Googles Fenster das Werbe-SDK nicht (Pruefbericht 01.11.2026).
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
    # Erst wenn der Start durch ist: Nach dem Vorspann fragt werbungVorbereiten()
    # einmal ZmajEinwilligung. Das landete sonst zwischen den gezaehlten Aufrufen.
    # Hielt bisher nur, weil der Vorspann immer 4,5 s dauerte (Pruefbericht 1.3, G18).
    seite.page.wait_for_function("() => updWerbungDurch", timeout=20000)


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
    # Pruefbericht 01.11.2026: Googles "nicht verlangt" gilt fuer die Sitzung -
    # der zweite Tipp fragt nicht noch einmal und geht auch ohne Netz.
    seite.js("() => { window.probe.fehler = 'offline'; }")
    n = len(seite.js("() => window.probe.aufrufe"))
    _tippen(seite)
    assert _neu(seite, n) == []
    assert seite.js(ZEILE) == {"box": True, "an": "false", "unten": _t(seite, "set.einwilligung_nein"), "alt": False}
    assert seite.js("() => localStorage.getItem('zmaj_pers')") == "aus"
    assert "showPrivacyOptionsForm" not in seite.js("() => window.probe.aufrufe")
    assert seite.fehler == []


def test_abonnent_nach_kauf_in_der_sitzung_kein_werbe_sdk(seite, heute_stand):
    """Pruefbericht 01.11.2026: Hatte AdMob in dieser Sitzung schon gefragt
    (AdMobP gesetzt, nach einem Nein nie initialize()) und kam das Abo erst
    danach, geht der Tipp ueber den Weg der Nutzer mit Werbung und zieht mit
    einwilligungNachziehen() die Auskunft nach. Ein Ja in Googles Fenster
    darf dabei das Werbe-SDK fuer den Abonnenten nicht starten."""
    _abonnent(seite, heute_stand)
    seite.js("""() => { AdMobP = window.Capacitor.Plugins.AdMob; admobDarf = false;
                        admobOptionen = true; admobGestartet = false; showSettings(); }""")
    assert seite.js(ZEILE)["box"] is True
    seite.js("() => { window.probe.wahl = true; }")
    n = len(seite.js("() => window.probe.aufrufe"))
    _tippen(seite)
    assert _neu(seite, n) == ["showPrivacyOptionsForm", "stand", "requestConsentInfo"]
    assert seite.js(ZEILE)["an"] == "true"
    # Die Auskunft ist nachgezogen, gestartet ist nichts.
    assert seite.js("() => [admobDarf, admobGestartet]") == [True, False]
    assert "initialize" not in seite.js("() => window.probe.aufrufe")
    assert seite.fehler == []


def test_abonnent_ohne_netz_schalter_bleibt(seite, heute_stand):
    _abonnent(seite, heute_stand)
    seite.js("() => { window.probe.fehler = 'offline'; showSettings(); }")
    _tippen(seite)
    assert seite.js(ZEILE) == {"box": True, "an": "false", "unten": _t(seite, "voll.fehler"), "alt": False}
    # Auch fuer Screenreader (Pruefbericht 01.11.2026).
    seite.page.wait_for_function("t => document.getElementById('ansage').textContent === t",
                                 arg=_t(seite, "voll.fehler"))
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
