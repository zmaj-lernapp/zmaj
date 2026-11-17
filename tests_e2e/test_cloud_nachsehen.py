# -*- coding: utf-8 -*-
"""Nachsehen bei jedem Oeffnen und Nachholen (17.11.2026) - im echten Browser.

Befund am Geraet am 17.11.2026: Die Cloud-Revision stand drei Tage still,
obwohl auf dem Handy gelernt wurde - geschrieben wurde nur beim Wechsel in den
Hintergrund, und die weggewischte App kam damit nicht mehr durch. Ein zweites
Geraet auf demselben Konto hatte am Nachmittag gelesen und las bis zum
naechsten Tag nicht mehr: "Deine Lernserie ist leider gerissen" und ein alter
Levelstand, waehrend in der Cloud laengst mehr stand. Ajdin: "ja ist gut so
... standard meine ich". Geprueft wird hier (Zahlen erfunden):
  - Zwei Geraete: B hat heute schon gelesen, A schreibt danach, B kommt in
    den Vordergrund zurueck und zeigt den Stand von A.
  - Ohne Aenderung in der Cloud genau eine kennung-Anfrage (nur rev), keine
    volle Ladung, kein Schreiben; gedrosselt auf CLOUD_NACHSEHEN_MS.
  - Nachholen: Das Schreiben beim Verlassen kommt nicht an (verloren, oder
    angekommen ohne Antwort), die App wird beendet - der naechste Start
    schreibt nach, und die Cloud hat alles.
  - Hoechstens zwei Schreibvorgaenge am Tag (Verlassen oder Nachholen, dazu
    einer gleich nach dem Lernen), keiner ohne Aenderung.
  - Adapter ohne kennung und eine abgelehnte Feldmaske: wie bisher hoechstens
    einmal am Tag der ganze Stand, kein voller Download je Oeffnen.
  - Ohne Netz, mit kaputtem Firebase oder abgemeldet: still, keine Meldung.
  - Nach einer echten Lektion geht der Lerntag gleich in die Cloud.
Nachbesserung nach dem Pruefbefund vom 17.11.2026:
  - Ein einzelner Fehler beim Nachsehen (503 von Firestore oder vom
    Ausweis) schaltet es nicht ab; erst eine Ablehnung (400) oder zwei
    Fehler hintereinander, und dann nur fuer diesen Tag.
  - Hoechstens vier Schreibversuche am Tag, auch wenn keiner ankommt.
  - Reines Einarbeiten verbraucht das Schreiben des Tages nicht.
Firebase beantwortet firebase_attrappe.py, kein Byte verlaesst den Rechner.
"""
import datetime
import json
import time

import pytest
from conftest import Seite
from firebase_attrappe import FIREBASE, Attrappe, dok_pfad, wege

DOK = dok_pfad()

# Fertig gestartet, auch wenn die Anmeldeseite steht (wie in test_anmeldung.py).
BEREIT = ("typeof CATEGORIES !== 'undefined' && CATEGORIES && CATEGORIES.length > 0"
          " && typeof standGeladen !== 'undefined' && standGeladen"
          " && (document.getElementById('btnSettings').style.display === 'inline-block'"
          "     || document.getElementById('profileView').style.display === 'block')")
# Anmelden wie die Anmeldeseite: danach steht der Lernpfad. Anonym gibt die
# Attrappe jedem Geraet dasselbe Probekonto - zwei Geraete, ein Konto.
ANMELDEN = """async () => { const ok = await cloudAnmelden('anonym'); if(ok) cloudNachAnmeldung(false); return ok; }"""
# In den Hintergrund und zurueck, wie Home-Taste und wieder auf.
WEG = """() => { Object.defineProperty(document, 'hidden', {configurable: true, get: () => true});
                 document.dispatchEvent(new Event('visibilitychange')); }"""
VORN = """() => { Object.defineProperty(document, 'hidden', {configurable: true, get: () => false});
                  document.dispatchEvent(new Event('visibilitychange')); delete document.hidden; }"""
MERKER = "() => JSON.parse(localStorage.getItem('zmaj_cloud') || 'null')"
OHNE_DROSSEL = "() => { CLOUD_NACHSEHEN_MS = 0; }"


def _starten(seite, cloud_html, attrappe, stand):
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=cloud_html))
    for host in FIREBASE:
        seite.page.route("https://%s/**" % host, attrappe)
    seite.page.goto(seite.basis + "/leer")
    seite.js("""(stand) => {
        localStorage.clear();
        localStorage.setItem('zmaj_stand', JSON.stringify(stand));
        localStorage.setItem('zmaj_einwilligung', JSON.stringify({wahl:'nein', stand:1, zeit:new Date().toISOString()}));
        localStorage.setItem('zmaj_sprache', 'de');
    }""", stand)
    seite.page.goto(seite.basis + "/app/index.html")
    seite.page.wait_for_function(BEREIT, timeout=30000)


def _fertig(seite):
    seite.page.wait_for_function("() => !cloudLaeuft")


def _im_dok(attrappe):
    return json.loads(attrappe.dok["daten"]["stringValue"])["stand"]


def _tage(von, bis):
    """Die Tage von vor `von` bis vor `bis` Tagen, aufsteigend (0 = heute)."""
    heute = datetime.date.today()
    return [(heute - datetime.timedelta(days=i)).isoformat() for i in range(von, bis - 1, -1)]


@pytest.fixture
def zweites(browser, basis):
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE", service_workers="block")
    yield Seite(ctx.new_page(), basis)
    ctx.close()


# ------------------------------------------------------ zwei Geraete ---

def test_zweites_geraet_sieht_beim_zurueckkommen_den_neuen_stand(seite, zweites, heute_stand, cloud_html):
    """Der Befund vom 17.11.2026, nachgestellt: B hat heute schon gelesen, als
    in der Cloud ein alter Stand stand, und zeigt "Serie gerissen". Danach
    schreibt A. Kommt B in den Vordergrund zurueck, zeigt es die 30 Tage und
    8 Level von A - bis dahin erst am naechsten Tag."""
    attrappe = Attrappe()
    b, a = seite, zweites
    jetzt = int(time.time() * 1000)
    # Fuenf Tage bis vor drei Tagen, ohne Serienschutz: gerissen. (Ab sieben
    # Lerntagen kaeme nach dem Anmelden ein Abzeichen dazu, und B haette
    # selbst etwas nachzuholen - hier soll B nur lesen.)
    _starten(b, cloud_html, attrappe, heute_stand(tage=_tage(7, 3), schutz={"anzahl": 0, "zeit": jetzt}))
    b.js("() => { CATEGORIES.slice(0, 2).forEach(c => passed.add(c.id)); saveProgress(); }")
    assert b.js(ANMELDEN) is True
    vorher = b.js("""() => ({serie: streak(), level: passed.size, gelesen: cloudMerker().gelesen === today(),
                            gerissen: !document.getElementById('schutzMeldung').hidden
                                      && document.getElementById('schutzMeldung').classList.contains('verloren'),
                            pfad: sichtbar('pfad')})""")
    assert vorher == {"serie": 0, "level": 2, "gelesen": True, "gerissen": True, "pfad": True}, vorher

    # A lernt seit 30 Tagen bis heute und hat 8 Level - und schreibt jetzt.
    _starten(a, cloud_html, attrappe, heute_stand(tage=_tage(29, 0)))
    a.js("() => { CATEGORIES.slice(0, 8).forEach(c => { passed.add(c.id); c.words.forEach(w => known.add(w.id)); }); saveProgress(); }")
    assert a.js(ANMELDEN) is True
    assert len(_im_dok(attrappe)["tage"]) == 30 and len(_im_dok(attrappe)["bestanden"]) == 8

    # B kommt zurueck (laenger als CLOUD_NACHSEHEN_MS spaeter).
    b.js(OHNE_DROSSEL)
    attrappe.anfragen.clear()
    masken = len(attrappe.masken)
    b.js(VORN)
    _fertig(b)
    assert wege(attrappe) == [("GET", DOK), ("GET", DOK)]          # erst rev, dann der ganze Stand
    assert attrappe.masken[masken:] == [["rev"], None]
    nachher = b.js("""() => ({serie: streak(), tage: days.size, level: passed.size, zahl: document.getElementById('serieZahl').textContent,
                             gerissen: !document.getElementById('schutzMeldung').hidden, pfad: sichtbar('pfad'),
                             rev: cloudMerker().rev})""")
    assert nachher == {"serie": 30, "tage": 30, "level": 8, "zahl": "30", "gerissen": False, "pfad": True,
                       "rev": attrappe.dok["rev"]["stringValue"]}, nachher
    assert a.fehler == [] and b.fehler == []


# ---------------------------------------- nachsehen, nur rev, gedrosselt ---

def test_rueckkehr_ohne_aenderung_nur_rev(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js(ANMELDEN) is True
    seite.js(OHNE_DROSSEL)
    for _ in range(3):
        attrappe.anfragen.clear()
        masken = len(attrappe.masken)
        seite.js(VORN)
        _fertig(seite)
        assert wege(attrappe) == [("GET", DOK)]                     # genau ein Lesen ...
        assert attrappe.masken[masken:] == [["rev"]]               # ... nur rev, kein Schreiben
    assert seite.js("async () => await cloudAbgleich('vorn')") == "gelesen"
    assert seite.js("async () => await cloudAbgleich('start')") == "gelesen"
    assert seite.js(MERKER)["gelesen"] == seite.js("() => today()")
    assert seite.fehler == []


def test_drosselung_schnelles_hin_und_her(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js("() => CLOUD_NACHSEHEN_MS") == 2 * 60 * 1000
    assert seite.js(ANMELDEN) is True
    # Eben angemeldet, also eben gelesen: die Rueckkehr gleich danach fragt nicht.
    attrappe.anfragen.clear()
    seite.js(VORN)
    _fertig(seite)
    assert attrappe.anfragen == []
    # Mit einer kurzen Drossel: einmal nachsehen, dann hin und her - nichts.
    seite.js("() => { CLOUD_NACHSEHEN_MS = 3000; cloudNachgesehen = 0; }")
    seite.js(VORN)
    _fertig(seite)
    for _ in range(3):
        seite.js(WEG)
        _fertig(seite)
        seite.js(VORN)
        _fertig(seite)
    assert seite.js("async () => await cloudAbgleich('start')") == "nichts"
    assert wege(attrappe) == [("GET", DOK)]
    # Nach Ablauf der Drossel wieder eine Anfrage.
    seite.page.wait_for_timeout(3100)
    seite.js(VORN)
    _fertig(seite)
    assert wege(attrappe) == [("GET", DOK), ("GET", DOK)]
    assert attrappe.masken[-2:] == [["rev"], ["rev"]]
    assert seite.fehler == []


# --------------------------------------------------------- nachholen ---

@pytest.mark.parametrize("abbruch", ["verloren", "angekommen"])
def test_verlorenes_schreiben_holt_der_naechste_start_nach(seite, heute_stand, cloud_html, abbruch):
    attrappe = Attrappe()
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js(ANMELDEN) is True
    rev_vorher = attrappe.dok["rev"]["stringValue"]
    seite.js("() => { known.add('probe:abends'); saveProgress(); }")

    # In den Hintergrund: das Schreiben bricht ab, die App wird beendet.
    attrappe.schreib_abbruch = abbruch
    attrappe.anfragen.clear()
    seite.js(WEG)
    _fertig(seite)
    assert [art for art, _ in wege(attrappe)] == ["GET", "PATCH"]
    m = seite.js(MERKER)
    assert m.get("tag") != seite.js("() => today()") and m["rev"] == rev_vorher
    assert ("probe:abends" in _im_dok(attrappe)["gewusst"]) == (abbruch == "angekommen")
    # Die beendete App stoesst beim Verlassen nichts mehr an (cloudLaeuft).
    seite.js("() => { cloudLaeuft = true; }")
    attrappe.schreib_abbruch = None
    attrappe.anfragen.clear()
    seite.page.reload()
    seite.page.wait_for_function(BEREIT, timeout=30000)
    seite.page.wait_for_function("() => !cloudLaeuft && (cloudMerker() || {}).tag === today()")
    # Neuer Ausweis, rev nachsehen - war es doch angekommen, erst den Stand
    # aus der Cloud einarbeiten -, dann schreiben.
    soll = [("POST", "securetoken.googleapis.com/v1/token"), ("GET", DOK)]
    soll += [("GET", DOK)] if abbruch == "angekommen" else []
    assert wege(attrappe) == soll + [("PATCH", DOK)]
    assert "probe:abends" in _im_dok(attrappe)["gewusst"]
    z = seite.js("() => ({rev: cloudMerker().rev, fp: cloudMerker().fp === cloudFingerabdruck(standAlsObjekt())})")
    assert z == {"rev": attrappe.dok["rev"]["stringValue"], "fp": True}, z

    # Das war das Schreiben des Tages: beim naechsten Verlassen keins mehr.
    seite.js("() => known.add('probe:spaeter')")
    attrappe.anfragen.clear()
    seite.js(WEG)
    _fertig(seite)
    assert attrappe.anfragen == []
    assert seite.fehler == []


# ------------------------------------ hoechstens zwei am Tag, nie umsonst ---

ADAPTER = """(kennung) => { window.ablage = {mitKennung: kennung}; window.adapter = cloudSpeicherAdapter(window.ablage);
                            CLOUD_NACHSEHEN_MS = 0; }"""
ABGLEICH = "async (anlass) => await cloudAbgleich(anlass, adapter)"
ZAEHLER = "() => Object.assign({}, ablage.zaehler)"
LERNEN = "(w) => { known.add(w); }"


def _uhr(seite, tag, stunde):
    seite.page.clock.set_fixed_time(datetime.datetime.combine(tag, datetime.time(stunde, 0)))


def test_hoechstens_zwei_am_tag_und_keiner_ohne_aenderung(seite, heute_stand):
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 9)
    seite.starten(stand=heute_stand())
    seite.js(ADAPTER, True)
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    assert seite.js(ZAEHLER) == {"anmelden": 1, "laden": 1, "speichern": 1, "loeschen": 0}

    # Oeffnen und Lernende ohne Aenderung: nur rev, kein Schreiben.
    assert seite.js(ABGLEICH, "vorn") == "gelesen"
    assert seite.js(ABGLEICH, "ende") == "nichts"
    assert seite.js(ZAEHLER) == {"anmelden": 1, "laden": 1, "speichern": 1, "loeschen": 0, "kennung": 1}
    # Gleich nach dem Lernen: einmal am Tag.
    seite.js(LERNEN, "probe:eins")
    assert seite.js(ABGLEICH, "ende") == "gespeichert"
    seite.js(LERNEN, "probe:zwei")
    assert seite.js(ABGLEICH, "ende") == "nichts"
    m = seite.js("() => cloudMerker()")
    assert m["ende"] == tag1.isoformat() and "tag" not in m
    # Das Schreiben beim Verlassen kam nicht an (ohne Netz) - die Rueckkehr
    # holt es nach, und es zaehlt als das des Tages.
    seite.js("() => { ablage.offline = true; }")
    assert seite.js(ABGLEICH, "pause") == "fehler"
    seite.js("() => { ablage.offline = false; }")
    assert seite.js(ABGLEICH, "vorn") == "gespeichert"
    assert "probe:zwei" in json.loads(seite.js("() => ablage.dok.text"))["stand"]["gewusst"]
    seite.js(LERNEN, "probe:drei")
    for anlass in ("pause", "vorn", "ende", "start"):
        assert seite.js(ABGLEICH, anlass) in ("nichts", "gelesen"), anlass
    assert seite.js(ZAEHLER)["speichern"] == 3                    # Anmelden + zwei

    # Tag 2: probe:drei ist noch nicht oben - der Start holt es nach.
    _uhr(seite, tag1 + datetime.timedelta(days=1), 8)
    assert seite.js(ABGLEICH, "start") == "gespeichert"
    assert "probe:drei" in json.loads(seite.js("() => ablage.dok.text"))["stand"]["gewusst"]
    assert seite.js(ABGLEICH, "pause") == "nichts"
    assert seite.js(ABGLEICH, "ende") == "nichts"                 # nichts Neues
    seite.js(LERNEN, "probe:vier")
    assert seite.js(ABGLEICH, "ende") == "gespeichert"
    seite.js(LERNEN, "probe:fuenf")
    for anlass in ("ende", "pause", "vorn"):
        assert seite.js(ABGLEICH, anlass) in ("nichts", "gelesen"), anlass
    assert seite.js(ZAEHLER)["speichern"] == 5

    # Tag 3 holt probe:fuenf nach; Tag 4 ohne Lernen schreibt gar nichts.
    _uhr(seite, tag1 + datetime.timedelta(days=2), 8)
    assert seite.js(ABGLEICH, "start") == "gespeichert"
    _uhr(seite, tag1 + datetime.timedelta(days=3), 8)
    for anlass in ("start", "vorn", "ende", "pause", "vorn"):
        assert seite.js(ABGLEICH, anlass) in ("nichts", "gelesen", "unveraendert"), anlass
    z = seite.js(ZAEHLER)
    assert z["speichern"] == 6 and z["laden"] == 1, z              # nie wieder der ganze Stand
    assert seite.fehler == []


def test_gleichzeitige_abgleiche_ueberholen_sich_nicht(seite, heute_stand):
    """Laeuft schon ein Abgleich, tut jeder weitere nichts (cloudLaeuft) -
    auch die neuen 'vorn' und 'ende'. Was dabei liegen bleibt, holt die
    naechste Rueckkehr nach."""
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 9)
    seite.starten(stand=heute_stand())
    seite.js(ADAPTER, True)
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    seite.js(LERNEN, "probe:eins")
    # Verlassen und gleich zurueck, im selben Augenblick: nur einer schreibt.
    z = seite.js("""async () => await Promise.all(['pause', 'vorn', 'ende', 'start', 'abmelden']
                                                   .map(a => cloudAbgleich(a, adapter)))""")
    assert z == ["gespeichert", "nichts", "nichts", "nichts", "nichts"], z
    assert seite.js(ZAEHLER)["speichern"] == 2
    seite.js(LERNEN, "probe:zwei")
    z = seite.js("""async () => await Promise.all(['ende', 'pause', 'vorn'].map(a => cloudAbgleich(a, adapter)))""")
    assert z == ["gespeichert", "nichts", "nichts"], z
    assert seite.js(ZAEHLER)["speichern"] == 3
    # Liegen geblieben: probe:drei kam waehrend eines laufenden Abgleichs.
    seite.js("() => { cloudLaeuft = true; }")
    seite.js(LERNEN, "probe:drei")
    assert [seite.js(ABGLEICH, a) for a in ("vorn", "ende", "pause")] == ["nichts", "nichts", "nichts"]
    seite.js("() => { cloudLaeuft = false; }")
    _uhr(seite, tag1 + datetime.timedelta(days=1), 9)
    assert seite.js(ABGLEICH, "vorn") == "gespeichert"
    assert "probe:drei" in json.loads(seite.js("() => ablage.dok.text"))["stand"]["gewusst"]
    assert seite.fehler == []


def test_adapter_ohne_kennung_einmal_am_tag(seite, heute_stand):
    """Ohne kennung kaeme bei jedem Oeffnen der ganze Stand - dann wie bisher
    hoechstens einmal am Tag gelesen. Nachgeholt wird trotzdem."""
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 9)
    seite.starten(stand=heute_stand())
    seite.js(ADAPTER, False)
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    for anlass in ("vorn", "start", "vorn"):
        assert seite.js(ABGLEICH, anlass) == "nichts", anlass
    assert seite.js(ZAEHLER)["laden"] == 1
    _uhr(seite, tag1 + datetime.timedelta(days=1), 9)
    assert seite.js(ABGLEICH, "vorn") == "gelesen"
    assert seite.js(ABGLEICH, "vorn") == "nichts"
    assert seite.js(ZAEHLER)["laden"] == 2
    seite.js(LERNEN, "probe:eins")
    seite.js("() => { ablage.offline = true; }")
    assert seite.js(ABGLEICH, "pause") == "fehler"
    seite.js("() => { ablage.offline = false; }")
    assert seite.js(ABGLEICH, "vorn") == "gespeichert"
    assert seite.js(ZAEHLER) == {"anmelden": 1, "laden": 3, "speichern": 2, "loeschen": 0}
    assert seite.fehler == []


def test_abgelehnte_feldmaske_kein_voller_download_je_oeffnen(seite, heute_stand, cloud_html):
    """Nimmt Firestore die Feldmaske nicht an, laedt die App wie bisher den
    ganzen Stand (test_cloud_packen.py) - aber danach nicht bei jedem Oeffnen
    wieder, sondern bis zum naechsten Start hoechstens einmal am Tag."""
    attrappe = Attrappe()
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js(ANMELDEN) is True
    seite.js(OHNE_DROSSEL)
    attrappe.maske_abgelehnt = True
    attrappe.anfragen.clear()
    masken = len(attrappe.masken)
    seite.js(VORN)
    _fertig(seite)
    assert wege(attrappe) == [("GET", DOK), ("GET", DOK)] and attrappe.masken[masken:] == [["rev"], None]
    for _ in range(3):
        seite.js(VORN)
        _fertig(seite)
    assert len(attrappe.anfragen) == 2
    # Geschrieben wird weiter, mit dem ganzen Stand vorher.
    seite.js("() => known.add('probe:ohne-maske')")
    seite.js(WEG)
    _fertig(seite)
    assert wege(attrappe)[2:] == [("GET", DOK), ("PATCH", DOK)] and attrappe.masken[-1] is None
    assert "probe:ohne-maske" in _im_dok(attrappe)["gewusst"]
    assert seite.fehler == []


# ----------------------------------- ohne Netz, kaputt, abgemeldet: still ---

STILL = """() => ({fehler: document.getElementById('err').style.display === 'block',
                   karte: !!document.querySelector('.nachfrage, .einwilligung'),
                   pfad: sichtbar('pfad'), merker: !!cloudMerker()})"""


def test_ohne_netz_oder_abgemeldet_keine_meldung(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js(ANMELDEN) is True
    seite.js(OHNE_DROSSEL)
    seite.js("() => known.add('probe:offline')")
    # Kein Netz: Nachsehen, Nachholen und Schreiben nach dem Lernen scheitern still.
    attrappe.abbruch = True
    seite.js(VORN)
    _fertig(seite)
    assert seite.js("async () => await cloudAbgleich('ende')") == "fehler"
    assert seite.js(STILL) == {"fehler": False, "karte": False, "pfad": True, "merker": True}
    # Firestore lehnt ab (429, Tageskontingent weg): dasselbe, angemeldet bleiben.
    attrappe.abbruch = False
    attrappe.kontingent_weg = True
    seite.js(VORN)
    _fertig(seite)
    assert seite.js(STILL) == {"fehler": False, "karte": False, "pfad": True, "merker": True}
    assert "probe:offline" not in _im_dok(attrappe)["gewusst"]
    # Das Netz ist wieder da: die naechste Rueckkehr holt nach.
    attrappe.kontingent_weg = False
    seite.js(VORN)
    _fertig(seite)
    assert "probe:offline" in _im_dok(attrappe)["gewusst"]
    # Abgemeldet: keine Anfrage, und auch hier keine Meldung.
    seite.js("() => cloudAbmelden()")
    attrappe.anfragen.clear()
    seite.js(VORN)
    seite.page.wait_for_timeout(200)
    assert seite.js("async () => [await cloudAbgleich('vorn'), await cloudAbgleich('ende')]") == ["nichts", "nichts"]
    assert attrappe.anfragen == []
    assert seite.js("() => document.getElementById('err').style.display") != "block"
    assert seite.fehler == []


# -------------------------------------------- nach einer echten Lektion ---

def test_nach_der_lektion_geht_der_lerntag_gleich_in_die_cloud(seite, heute_stand, cloud_html):
    """Lernen und gleich wegwischen: Der Lerntag ist schon oben, bevor die App
    in den Hintergrund geht. Die zweite Lektion des Tages schreibt nicht noch
    einmal - das bleibt dem Verlassen."""
    attrappe = Attrappe()
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js(ANMELDEN) is True
    heute = seite.js("() => today()")
    assert heute not in _im_dok(attrappe).get("tage", [])
    attrappe.anfragen.clear()
    seite.js("() => { openLevel(0); startLesson(); }")
    seite.durchspielen("lBody", "Lx")
    seite.page.wait_for_function("() => !cloudLaeuft && (cloudMerker() || {}).ende === today()")
    assert [art for art, _ in wege(attrappe)] == ["GET", "PATCH"]
    stand = _im_dok(attrappe)
    assert heute in stand["tage"] and stand["gewusst"]
    assert "tag" not in seite.js(MERKER)              # das Schreiben beim Verlassen bleibt frei
    # Die zweite Lektion: kein weiteres Schreiben ...
    attrappe.anfragen.clear()
    seite.js("() => { openLevel(0); startLesson(); }")
    seite.durchspielen("lBody", "Lx")
    seite.page.wait_for_timeout(300)
    _fertig(seite)
    assert attrappe.anfragen == []
    # ... aber beim Verlassen kommt sie mit.
    seite.js(WEG)
    _fertig(seite)
    assert [art for art, _ in wege(attrappe)] == ["GET", "PATCH"]
    assert seite.js(MERKER)["tag"] == heute
    assert seite.fehler == []


# ------------------------------ Nachbesserung nach dem Pruefbefund 17.11. ---

TOKEN = "securetoken.googleapis.com/v1/token"
LERNEN_UND_ENDE = "async (w) => { known.add(w); saveProgress(); return await cloudAbgleich('ende'); }"


def _a_schreibt(attrappe, wort, rev):
    """Ein anderes Geraet hat geschrieben: ein Wort mehr in gewusst, neue rev."""
    datei = json.loads(attrappe.dok["daten"]["stringValue"])
    datei["stand"]["gewusst"] = sorted(set(datei["stand"]["gewusst"]) | {wort})
    attrappe.dok = {"daten": {"stringValue": json.dumps(datei)}, "rev": {"stringValue": rev}}


def _warte(seite, bedingung):
    for _ in range(400):
        if bedingung():
            return
        seite.page.wait_for_timeout(25)
    raise AssertionError("Bedingung nicht erfuellt")


@pytest.mark.parametrize("wo", ["firestore", "ausweis"])
def test_ein_fehler_beim_nachsehen_schaltet_es_nicht_ab(seite, heute_stand, cloud_html, wo):
    """Probe P9 des Pruefers: Ein einzelner 503 beim Nachsehen - von Firestore
    oder schon beim Erneuern des Ausweises - galt als abgelehnte Feldmaske,
    und bis zum naechsten Start sah das Geraet nichts Neues mehr (der Befund
    vom 17.11. waere zurueck gewesen). Jetzt wird einmal der ganze Stand
    gelesen, und die naechste Rueckkehr sieht wieder nur rev nach - und
    findet, was ein anderes Geraet geschrieben hat."""
    attrappe = Attrappe()
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js(ANMELDEN) is True
    if wo == "firestore":
        seite.js(OHNE_DROSSEL)
        attrappe.maske_fehler = [503]
        attrappe.anfragen.clear()
        masken = len(attrappe.masken)
        seite.js(VORN)
        _fertig(seite)
        assert wege(attrappe) == [("GET", DOK), ("GET", DOK)] and attrappe.masken[masken:] == [["rev"], None]
    else:
        # Neu geladen ist der Ausweis weg, und sein Erneuern scheitert einmal.
        # Heute schon geschrieben: Weder das Verlassen der alten Seite noch der
        # Start schreiben etwas, gezaehlt wird nur das Nachsehen.
        seite.js("() => { const m = cloudMerker(); m.tag = today(); localStorage.setItem('zmaj_cloud', JSON.stringify(m)); }")
        attrappe.token_fehler_folge = [503]
        attrappe.anfragen.clear()
        masken = len(attrappe.masken)
        seite.page.reload()
        seite.page.wait_for_function(BEREIT, timeout=30000)
        _warte(seite, lambda: len(attrappe.masken) > masken)
        _fertig(seite)
        assert wege(attrappe) == [("POST", TOKEN), ("POST", TOKEN), ("GET", DOK)]
        assert attrappe.masken[masken:] == [None]
        seite.js(OHNE_DROSSEL)
    assert seite.js("() => cloudBillig(cloudAdapter(), cloudMerker())") is True
    # Ein anderes Geraet schreibt; die naechste Rueckkehr sieht nach und arbeitet es ein.
    _a_schreibt(attrappe, "probe:von-a", "a.1")
    attrappe.anfragen.clear()
    masken = len(attrappe.masken)
    seite.js(VORN)
    _fertig(seite)
    assert wege(attrappe) == [("GET", DOK), ("GET", DOK)] and attrappe.masken[masken:] == [["rev"], None]
    assert seite.js("() => [known.has('probe:von-a'), cloudMerker().rev]") == [True, "a.1"]
    # Danach wieder nur rev - und nichts hochzuladen.
    attrappe.anfragen.clear()
    seite.js(VORN)
    _fertig(seite)
    assert wege(attrappe) == [("GET", DOK)] and attrappe.masken[-1] == ["rev"]
    assert seite.fehler == []


def test_maske_erst_nach_zwei_fehlern_hintereinander_aus(seite, heute_stand, cloud_html):
    """Andere Fehler als eine Ablehnung (400) schalten das Nachsehen erst aus,
    wenn es zweimal hintereinander so ging - dann fuer den Rest des Tages, wie
    ein Adapter ohne kennung. Ein gelungenes Nachsehen dazwischen faengt von
    vorn an."""
    attrappe = Attrappe()
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js(ANMELDEN) is True
    seite.js(OHNE_DROSSEL)
    billig = "() => cloudBillig(cloudAdapter(), cloudMerker())"
    attrappe.maske_fehler = [503]
    for _ in range(2):                       # Fehler, dann gelungen
        seite.js(VORN)
        _fertig(seite)
    attrappe.maske_fehler = [500]
    seite.js(VORN)
    _fertig(seite)
    assert seite.js(billig) is True
    assert attrappe.masken[1:] == [["rev"], None, ["rev"], ["rev"], None]
    attrappe.maske_fehler = [503]            # der zweite hintereinander
    seite.js(VORN)
    _fertig(seite)
    assert seite.js(billig) is False
    attrappe.anfragen.clear()
    for _ in range(3):
        seite.js(VORN)
        _fertig(seite)
    assert attrappe.anfragen == []           # heute schon gelesen: wie ohne kennung
    assert seite.fehler == []


@pytest.mark.parametrize("abbruch", ["verloren", "angekommen"])
def test_hoechstens_vier_schreibversuche_am_tag(seite, heute_stand, cloud_html, abbruch):
    """Probe P15 des Pruefers: Kommt keine Antwort aufs Schreiben, verbrauchte
    das den Tag nicht, und jeder Anlass schrieb neu - drei Lektionen, sechsmal
    weg und sechsmal zurueck ergaben 15 Schreibvorgaenge (und bei
    "angekommen" 14 volle Ladungen). Jetzt hoechstens CLOUD_SCHREIBVERSUCHE
    (4) am Tag; der naechste Tag holt den Rest nach. Anmelden und Abmelden
    sind nie gesperrt."""
    attrappe = Attrappe()
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 9)
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js("() => CLOUD_SCHREIBVERSUCHE") == 4
    assert seite.js(ANMELDEN) is True
    seite.js(OHNE_DROSSEL)
    attrappe.schreib_abbruch = abbruch
    attrappe.anfragen.clear()
    masken = len(attrappe.masken)
    for i in range(3):
        assert seite.js(LERNEN_UND_ENDE, "probe:lektion%d" % i) in ("fehler", "nichts")
        for _ in range(2):
            seite.js(WEG)
            _fertig(seite)
            seite.js(VORN)
            _fertig(seite)
    arten = [a for a, _ in wege(attrappe)]
    assert arten.count("PATCH") == 4, arten
    voll = attrappe.masken[masken:].count(None)
    assert voll == (4 if abbruch == "angekommen" else 0), attrappe.masken[masken:]
    m = seite.js(MERKER)
    assert m["versuche"] == {"tag": tag1.isoformat(), "n": 4}
    assert m.get("tag") != tag1.isoformat() and m.get("ende") != tag1.isoformat()
    assert seite.js(STILL) == {"fehler": False, "karte": False, "pfad": True, "merker": True}
    # Weiter nur nachsehen, nie mehr schreiben - auch wenn das Netz wieder geht.
    attrappe.schreib_abbruch = None
    attrappe.anfragen.clear()
    for anlass in ("ende", "pause", "vorn", "start"):
        assert seite.js("async (a) => await cloudAbgleich(a)", anlass) in ("nichts", "gelesen"), anlass
    assert [a for a, _ in wege(attrappe)] == ["GET", "GET"]

    # Naechster Tag: das erste Oeffnen holt alles nach, und es zaehlt neu.
    _uhr(seite, tag1 + datetime.timedelta(days=1), 9)
    attrappe.anfragen.clear()
    assert seite.js("async () => await cloudAbgleich('vorn')") == "gespeichert"
    assert wege(attrappe) == [("POST", TOKEN), ("GET", DOK), ("PATCH", DOK)]   # der Ausweis von gestern ist abgelaufen
    assert {"probe:lektion0", "probe:lektion1", "probe:lektion2"} <= set(_im_dok(attrappe)["gewusst"])
    m = seite.js(MERKER)
    assert m["versuche"] == {"tag": (tag1 + datetime.timedelta(days=1)).isoformat(), "n": 1}
    # Sind die Versuche des Tages aufgebraucht, schreibt das Abmelden trotzdem.
    seite.js("""() => { const m = cloudMerker(); m.versuche = {tag: today(), n: 4};
                        localStorage.setItem('zmaj_cloud', JSON.stringify(m)); }""")
    assert seite.js(LERNEN_UND_ENDE, "probe:vor-dem-abmelden") == "nichts"
    assert seite.js("async () => await cloudAbgleich('abmelden')") == "gespeichert"
    assert "probe:vor-dem-abmelden" in _im_dok(attrappe)["gewusst"]
    assert seite.js(MERKER)["versuche"]["n"] == 4
    assert seite.fehler == []


def test_reines_einarbeiten_kostet_kein_schreiben(seite, heute_stand, cloud_html):
    """Probe P12 des Pruefers: Nach reinem Einarbeiten (hier nichts Neues)
    hielt das naechste Oeffnen den zusammengefuehrten Stand fuer neu und lud
    ihn hoch - mit dem Schreiben des Tages. Zwei Lektionen danach: die zweite
    kam erst am naechsten Tag in die Cloud. Jetzt gilt reines Einarbeiten als
    hochgeladen; war vorher etwas offen, bleibt es offen."""
    attrappe = Attrappe()
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 9)
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js(ANMELDEN) is True
    seite.js(OHNE_DROSSEL)
    gleich = "() => cloudMerker().fp === cloudFingerabdruck(standAlsObjekt())"
    _a_schreibt(attrappe, "probe:von-a", "a.1")
    attrappe.anfragen.clear()
    assert seite.js("async () => await cloudAbgleich('vorn')") == "zusammengefuehrt"
    assert wege(attrappe) == [("GET", DOK), ("GET", DOK)]
    assert seite.js(gleich) is True and seite.js("() => known.has('probe:von-a')") is True
    # Wieder zurueck und wieder weg, ohne zu lernen: nur nachsehen.
    attrappe.anfragen.clear()
    assert seite.js("async () => await cloudAbgleich('vorn')") == "gelesen"
    assert seite.js("async () => await cloudAbgleich('pause')") == "unveraendert"
    assert wege(attrappe) == [("GET", DOK)]
    # Zwei Lektionen danach: beide noch heute oben.
    assert seite.js(LERNEN_UND_ENDE, "probe:b1") == "gespeichert"
    seite.js("() => { known.add('probe:b2'); saveProgress(); }")
    assert seite.js("async () => await cloudAbgleich('pause')") == "gespeichert"
    assert {"probe:von-a", "probe:b1", "probe:b2"} <= set(_im_dok(attrappe)["gewusst"])
    m = seite.js(MERKER)
    assert m["tag"] == m["ende"] == tag1.isoformat()
    # War vor dem Einarbeiten etwas offen, bleibt es offen ...
    _a_schreibt(attrappe, "probe:von-a2", "a.2")
    seite.js("() => { known.add('probe:b3'); saveProgress(); }")
    attrappe.anfragen.clear()
    assert seite.js("async () => await cloudAbgleich('vorn')") == "zusammengefuehrt"   # heute schon zweimal
    assert wege(attrappe) == [("GET", DOK), ("GET", DOK)]
    assert seite.js(gleich) is False
    # ... und der naechste Tag holt es nach, mit allem von beiden.
    _uhr(seite, tag1 + datetime.timedelta(days=1), 9)
    assert seite.js("async () => await cloudAbgleich('start')") == "gespeichert"
    assert {"probe:von-a", "probe:von-a2", "probe:b1", "probe:b2", "probe:b3"} <= set(_im_dok(attrappe)["gewusst"])
    assert seite.fehler == []


def test_ueberschriebenes_kommt_wieder_hoch(seite, heute_stand, cloud_html):
    """Schreiben zwei Geraete im selben Augenblick, fehlt dem spaeteren Stand
    in der Cloud, was das fruehere hochgeladen hatte (Firestore schreibt ohne
    Vorbedingung). Dann gilt das Einarbeiten nicht als hochgeladen, und das
    Nachholen bringt es wieder hoch - darum prueft cloudHatAlles() den
    Inhalt und nicht nur, ob hier seit dem letzten Hochladen etwas dazukam."""
    attrappe = Attrappe()
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 9)
    _starten(seite, cloud_html, attrappe, heute_stand())
    assert seite.js(ANMELDEN) is True
    seite.js(OHNE_DROSSEL)
    vorher = attrappe.dok                    # den hat das andere Geraet gelesen
    assert seite.js(LERNEN_UND_ENDE, "probe:b-oben") == "gespeichert"
    attrappe.dok = vorher
    _a_schreibt(attrappe, "probe:von-a", "a.1")         # ohne probe:b-oben
    assert seite.js("async () => await cloudAbgleich('vorn')") == "zusammengefuehrt"
    assert seite.js("() => cloudMerker().fp !== cloudFingerabdruck(standAlsObjekt())") is True
    attrappe.anfragen.clear()
    assert seite.js("async () => await cloudAbgleich('vorn')") == "gespeichert"
    assert wege(attrappe) == [("GET", DOK), ("PATCH", DOK)]
    assert {"probe:von-a", "probe:b-oben"} <= set(_im_dok(attrappe)["gewusst"])
    # getragen ist die Wahl des Geraets und zaehlt dabei nicht mit; ein
    # fehlendes Wort schon.
    probe = "(was) => { const s = standAlsObjekt(); if(was) s.getragen = 'anders'; else s.gewusst = s.gewusst.slice(1);" \
            " return cloudHatAlles(s, cloudMerker().fremd); }"
    assert seite.js(probe, True) is True
    assert seite.js(probe, False) is False
    assert seite.fehler == []
