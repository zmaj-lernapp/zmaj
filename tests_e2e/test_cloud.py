# -*- coding: utf-8 -*-
"""Cloud-Sicherung, vorbereitet und aus (19.10.2026) - im echten Browser.

Ajdin am 18.10.2026: Firebase, eingeschaltet erst nach dem
Produktionsstart. Geprueft wird hier:
  - Mit CLOUD_AN = false passiert nichts: keine einzige Anfrage ins Netz
    (mitgeschnitten), keine Oberflaeche, kein Eintrag im Geraetespeicher -
    auch nicht, wenn die App in den Hintergrund geht oder jemand die
    Funktionen direkt aufruft.
  - standZusammenfuehren(): Vereinigung, nichts geht verloren, Muenzen als
    Maximum, jedes Feld nach seiner Regel, idempotent und kommutativ.
  - Eine kaputte oder gefaelschte Gegenseite wird gefiltert wie eine
    Sicherungsdatei, der eigene Stand bleibt.
  - Buendelung mit dem Speicher-Adapter und gestellter Uhr: hoechstens ein
    Schreiben am Tag (plus beim Anmelden), nur bei Aenderungen, ohne Netz
    still spaeter.
  - Ein zweites Geraet wird eingearbeitet; was dieses Geraet selbst
    weggenommen hat, kommt nicht aus der eigenen alten Sicherung zurueck.
  - Der Firestore-Adapter gegen einen nachgestellten Server (page.route):
    Adressen, Ausweis, Dokumentform. Dafuer eine eigene Fassung der Demo mit
    CLOUD_AN = true und erfundenen Werten, eingesetzt mit
    app_bauen.cloud_einsetzen() wie beim Bauen. Kein Byte verlaesst den
    Rechner - jede Anfrage beantwortet der Test selbst.
  - Loeschen, wenn Firebase fuer das Konto eine frische Anmeldung verlangt:
    die Sicherung ist weg und die App abgemeldet, mit Google wird neu
    angemeldet und nur dasselbe Konto geloescht.
"""
import datetime
import json

# Die Attrappe steht seit 28.10.2026 in firebase_attrappe.py, die Demo mit
# eingeschalteter Anmeldung (cloud_html) in conftest.py.
from firebase_attrappe import FIREBASE, PROJEKT, UID, Attrappe

# Speicher-Adapter einrichten: window.ablage haelt den "Cloud"-Stand.
ADAPTER = """() => { window.ablage = {}; window.adapter = cloudSpeicherAdapter(window.ablage); return true; }"""


def _keine_cloud_anfrage(urls):
    return [u for u in urls if any(h in u for h in FIREBASE)]


# ---------------------------------------------------------------- aus ---

def test_aus_kein_netz_keine_oberflaeche_kein_speicher(seite, heute_stand):
    alle = []
    seite.page.on("request", lambda r: alle.append(r.url))
    seite.starten(stand=heute_stand())
    z = seite.js("""async () => {
        const r = {an: CLOUD_AN, eingerichtet: cloudEingerichtet(), adapter: cloudAdapter()};
        r.start = await cloudAbgleich('start');
        r.pause = await cloudAbgleich('pause');
        r.anonym = await cloudAnmelden('anonym');
        r.google = await cloudAnmelden('google');
        r.loeschen = await cloudLoeschen();
        // In den Hintergrund und zurueck - wie Home-Taste und wieder auf.
        Object.defineProperty(document, 'hidden', {configurable: true, get: () => true});
        document.dispatchEvent(new Event('visibilitychange'));
        await new Promise(f => setTimeout(f, 300));
        delete document.hidden;
        document.dispatchEvent(new Event('visibilitychange'));
        showSettings();
        return r;
    }""")
    assert z == {"an": False, "eingerichtet": False, "adapter": None, "start": "nichts",
                 "pause": "nichts", "anonym": False, "google": False, "loeschen": False}, z
    seite.neu_laden()
    rest = seite.js("""() => ({
        schluessel: Object.keys(localStorage).filter(k => /cloud/i.test(k)),
        oberflaeche: [...document.querySelectorAll('*')].filter(e =>
            /cloud/i.test((e.id || '') + ' ' + (typeof e.className === 'string' ? e.className : '')
                          + ' ' + ((e.dataset && e.dataset.t) || ''))).length})""")
    assert rest == {"schluessel": [], "oberflaeche": 0}, rest
    assert _keine_cloud_anfrage(alle) == [], alle
    assert seite.fremd == [], "Anfragen an fremde Server: %s" % seite.fremd
    assert seite.fehler == []


# ---------------------------------------------------- zusammenfuehren ---

def _staende(seite):
    """Zwei Lernstaende, die sich in jedem Feld unterscheiden."""
    p = dict(seite.js("() => ZIERRAT.filter(w => !w.voll).map(w => [w.id, w.preis])"))
    a = {
        "gewusst": ["w:a", "gemeinsam"], "bestanden": ["lv1"], "gelesen": ["g1"],
        "tage": ["2026-10-01", "2026-10-02"], "frost": ["2026-10-03"], "gefeiert": ["tage7"],
        "besitz": ["hut"], "muenzen_ges": 2000, "muenzen_aus": p["hut"],
        "rekord": 2, "geschenk_jahr": 0,
        "wann": {"lv:lv1": "2026-10-02", "gs:g1": "2026-10-05"},
        "tagwerk": {"2026-10-02": {"auf": 10, "ric": 8}},
        "topf": {"w:alt": {"typ": "mc", "n": 1, "z": 1000}, "w:gleich": {"typ": "mc", "n": 1, "z": 2000},
                 "w:nur-a": {"typ": "type", "n": 0, "z": 3000}},
        "stern": {"w:s1": {"z": 100, "r": 500}, "w:nur-a": {"z": 50, "r": 0}},
        "leben": {"anzahl": 2, "zeit": 5000}, "schutz": {"anzahl": 1, "zeit": 0},
        "einstufung": {"tag": "2026-10-01", "wahl": "neu", "bis": ""},
        "bewertung": {"gezeigt": ["2026-10-01"], "nein": False, "bewertet": False},
        "getragen": "hut",
    }
    b = {
        "gewusst": ["gemeinsam", "w:b"], "bestanden": ["lv2"], "gelesen": [],
        "tage": ["2026-10-02", "2026-10-04"], "frost": [], "gefeiert": [],
        "besitz": ["lesebrille"], "muenzen_ges": 900, "muenzen_aus": p["lesebrille"],
        "rekord": 5, "geschenk_jahr": 1,
        "wann": {"lv:lv1": "2026-10-01", "lv:lv2": "2026-10-04"},
        "tagwerk": {"2026-10-02": {"auf": 4, "ric": 9, "zeit": 30}, "2026-10-04": {"auf": 1}},
        "topf": {"w:alt": {"typ": "mcrev", "n": 0, "z": 4000}, "w:gleich": {"typ": "mc", "n": 0, "z": 2000},
                 "w:nur-b": {"typ": "gap", "n": 1, "z": 10}},
        "stern": {"w:s1": {"z": 300, "r": 200}, "w:nur-b": {"z": 70, "r": 10}},
        "leben": {"anzahl": 5, "zeit": 0}, "schutz": {"anzahl": 0, "zeit": 9000},
        "einstufung": {"tag": "2026-10-03", "wahl": "gut", "bis": "x"},
        "bewertung": {"gezeigt": ["2026-10-05"], "nein": True, "bewertet": False},
        "getragen": "lesebrille",
    }
    return a, b, p


MISCHEN = "([a, b]) => standZusammenfuehren(a, b)"


def test_zusammenfuehren_jedes_feld_nach_seiner_regel(seite, heute_stand):
    seite.starten(stand=heute_stand())
    a, b, p = _staende(seite)
    m = seite.js(MISCHEN, [a, b])
    # Jedes Feld aus standAlsObjekt() ist da, nichts dazu (etwa premium).
    assert set(m) == set(seite.js("() => Object.keys(standAlsObjekt())")) == set(a)
    for k in ("gewusst", "bestanden", "gelesen", "tage", "frost", "gefeiert", "besitz"):
        assert m[k] == sorted(set(a[k]) | set(b[k])), k
    assert m["muenzen_ges"] == 2000
    # Maximum je Feld - aber bezahlt ist beides, was in besitz steht.
    assert m["muenzen_aus"] == p["hut"] + p["lesebrille"] > max(a["muenzen_aus"], b["muenzen_aus"])
    assert m["rekord"] == 5 and m["geschenk_jahr"] == 1
    assert m["wann"] == {"lv:lv1": "2026-10-01", "gs:g1": "2026-10-05", "lv:lv2": "2026-10-04"}
    assert m["tagwerk"] == {"2026-10-02": {"auf": 10, "ric": 9, "zeit": 30}, "2026-10-04": {"auf": 1}}
    assert m["topf"] == {
        "w:alt": {"typ": "mcrev", "n": 0, "z": 4000},      # der neuere Fehler
        "w:gleich": {"typ": "mc", "n": 0, "z": 2000},      # gleicher Fehler: das kleinere n
        "w:nur-a": {"typ": "type", "n": 0, "z": 3000}, "w:nur-b": {"typ": "gap", "n": 1, "z": 10}}
    assert m["stern"] == {"w:s1": {"z": 300, "r": 500}, "w:nur-a": {"z": 50, "r": 0}, "w:nur-b": {"z": 70, "r": 10}}
    assert m["leben"] == a["leben"]          # neuere Zeit
    assert m["schutz"] == b["schutz"]
    assert m["einstufung"] == b["einstufung"]
    assert m["bewertung"] == {"gezeigt": ["2026-10-01", "2026-10-05"], "nein": True, "bewertet": False}
    assert m["getragen"] == "hut"            # das Geraet gewinnt ...
    assert seite.js(MISCHEN, [dict(a, getragen=""), b])["getragen"] == "lesebrille"   # ... traegt es nichts, die Cloud
    # Gleiche Zeit: die kleinere Anzahl, in beiden Richtungen.
    for x, y in (({"anzahl": 3, "zeit": 100}, {"anzahl": 4, "zeit": 100}),
                 ({"anzahl": 4, "zeit": 100}, {"anzahl": 3, "zeit": 100})):
        assert seite.js(MISCHEN, [dict(a, leben=x), dict(b, leben=y)])["leben"] == {"anzahl": 3, "zeit": 100}
    # Die Eingaben bleiben unberuehrt.
    assert seite.js("""([a, b]) => { const sa = JSON.stringify(a), sb = JSON.stringify(b);
        standZusammenfuehren(a, b); return JSON.stringify(a) === sa && JSON.stringify(b) === sb; }""", [a, b])
    assert seite.fehler == []


def test_zusammenfuehren_idempotent_kommutativ_ohne_verluste(seite, heute_stand):
    seite.starten(stand=heute_stand())
    a, b, _ = _staende(seite)
    m = seite.js(MISCHEN, [a, b])
    assert seite.js(MISCHEN, [m, m]) == m                       # idempotent
    assert seite.js(MISCHEN, [m, a]) == m                       # schon drin: nichts aendert sich
    assert seite.js(MISCHEN, [m, b]) == m
    gleich = dict(b, getragen=a["getragen"])                    # getragen: das Geraet gewinnt
    assert seite.js(MISCHEN, [gleich, a]) == seite.js(MISCHEN, [a, gleich])   # kommutativ
    # Mit einem leeren oder fehlenden Gegenstueck geht nichts verloren.
    for leer in ({}, None, [], "kaputt"):
        assert seite.js(MISCHEN, [a, leer]) == seite.js(MISCHEN, [a, a])
    for k in ("gewusst", "bestanden", "gelesen", "tage", "frost", "besitz"):
        assert set(a[k]) <= set(m[k]) and set(b[k]) <= set(m[k]), k
    for k in ("topf", "stern", "wann"):
        assert set(a[k]) | set(b[k]) <= set(m[k]), k
    # Der echte Stand der App mit sich selbst: derselbe Stand.
    assert seite.js("""() => {
        const s = standAlsObjekt(), m = standZusammenfuehren(s, s);
        return Object.keys(s).every(k => JSON.stringify(m[k]) === JSON.stringify(s[k]));
    }""")
    assert seite.fehler == []


# ------------------------------------------------------ kaputte Gegenseite ---

def _kaputt(gestern, fremdes_wort, kaputtes_wort, laden):
    """Ein Cloud-Dokument wie von Hand gefaelscht. 1e999 liest JSON.parse
    als Infinity; json.dumps kann es nicht schreiben, deshalb Text."""
    return ('{"app":"zmaj","version":1,"stand":{'
            '"gewusst":[1,null,{"x":1},%s],"bestanden":"alles",'
            '"tage":["1970-01-01","2099-01-01","%s","kein-datum",5],"frost":["1980-01-01"],'
            '"muenzen_ges":1e999,"muenzen_aus":-5,"besitz":%s,"rekord":1e9,"geschenk_jahr":9999,'
            '"leben":{"anzahl":1e300,"zeit":"bald"},"schutz":[1,2],'
            '"stern":{%s:{"z":"x"},"boese":{"z":1},%s:{"z":5,"r":1}},'
            '"topf":[1,2,3],"wann":{"lv:x":5},"tagwerk":{"nicht-datum":{"auf":5}},'
            '"einstufung":"ja","bewertung":[],"getragen":7,"premium":true}}'
            % (json.dumps(fremdes_wort), gestern, json.dumps(laden),
               json.dumps("w:" + kaputtes_wort), json.dumps("w:" + fremdes_wort)))


ZUSTAND = """() => ({
    woerter: [...known].sort(), nurTexte: [...known].every(x => typeof x === 'string'),
    bestanden: [...passed].sort(), tage: [...days].sort(), frost: [...frost].sort(),
    ges: muenzenGes, aus: muenzenAus, endlich: Number.isFinite(muenzenGes) && Number.isFinite(muenzenAus),
    besitz: [...besitz].sort(), rekord, leben: lives, schutz, stern: Object.keys(stern).sort(),
    topf: Object.keys(topf).sort(), einstufung, getragen, premium, unbegrenzt: unlimited(),
    jahr: geschenk.jahr || 0, wann})"""


def test_kaputte_gegenseite_wird_gefiltert(seite, heute_stand):
    seite.starten(stand=heute_stand())
    vorher = seite.js("""() => {
        const ids = CATEGORIES[0].words.slice(0, 3).map(w => w.id);
        known = new Set(ids); passed = new Set([CATEGORIES[0].id]); days = new Set([today()]);
        muenzenGes = 60; muenzenAus = 0; topf = {['w:' + ids[0]]: {typ: 'mc', n: 0, z: Date.now()}};
        stern = {['w:' + ids[1]]: {z: Date.now(), r: 0}};
        return {ids, heute: today(), laden: ZIERRAT.filter(w => !w.voll).map(w => w.id)};
    }""")
    heute = datetime.date.fromisoformat(vorher["heute"])
    gestern = (heute - datetime.timedelta(days=1)).isoformat()
    fremd, kaputt = seite.js("() => CATEGORIES[1].words.slice(0, 2).map(w => w.id)")
    seite.js(ADAPTER)
    seite.js("(text) => { ablage.dok = {text, rev: 'anderes-geraet.1'}; }",
             _kaputt(gestern, fremd, kaputt, vorher["laden"]))
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    z = seite.js(ZUSTAND)
    assert z["nurTexte"] and z["woerter"] == sorted(vorher["ids"] + [fremd]), z["woerter"]
    assert z["bestanden"] == [seite.js("() => CATEGORIES[0].id")]
    assert z["tage"] == sorted([vorher["heute"], gestern]) and z["frost"] == []
    assert z["endlich"] and z["ges"] == 60 and z["aus"] == 0 and z["besitz"] == [], z
    assert z["rekord"] <= len(z["tage"])
    assert z["leben"]["anzahl"] <= 5 and isinstance(z["leben"]["zeit"], (int, float))
    assert z["stern"] == sorted(["w:" + vorher["ids"][1], "w:" + fremd])
    assert z["topf"] == ["w:" + vorher["ids"][0]]
    assert z["einstufung"]["wahl"] == "neu" and z["getragen"] == ""
    assert not z["premium"] and not z["unbegrenzt"] and z["jahr"] == 0
    assert "lv:x" not in z["wann"]
    # In der Cloud steht danach ein sauberer Stand im Format der Sicherungsdatei.
    dok = seite.js("() => ablage.dok")
    datei = json.loads(dok["text"])
    assert datei["app"] == "zmaj" and datei["version"] == 1
    assert set(datei["stand"]) == set(seite.js("() => Object.keys(standAlsObjekt())"))
    assert "premium" not in datei["stand"] and dok["rev"] != "anderes-geraet.1"

    # Kein JSON: nichts einzuarbeiten, der eigene Stand ersetzt es.
    seite.js("() => { ablage.dok = {text: '{kaputt', rev: 'anderes-geraet.2'}; known.add('neu:wort'); }")
    assert seite.js("async () => await cloudAbgleich('pause', adapter)") == "gespeichert"
    assert "neu:wort" in json.loads(seite.js("() => ablage.dok.text"))["stand"]["gewusst"]
    assert seite.js(ZUSTAND)["woerter"] == sorted(vorher["ids"] + [fremd, "neu:wort"])
    assert seite.fehler == []


def test_zukunft_von_der_gegenseite_wird_gekappt(seite, heute_stand):
    """Pruefbefund 19.10.2026: ein Fehler mit z aus der Zukunft kaeme nie in
    eine Runde und wuerde nie verdraengt. Wie bei stern wird z auf jetzt
    gekappt; tagwerk-Tage und wann-Daten nach heute fallen weg."""
    seite.starten(stand=heute_stand())
    w = seite.js("() => 'w:' + CATEGORIES[0].words[0].id")
    heute = seite.js("() => today()")
    morgen = (datetime.date.fromisoformat(heute) + datetime.timedelta(days=1)).isoformat()
    a = {"topf": {w: {"typ": "mc", "n": 0, "z": 1000}},
         "tagwerk": {heute: {"auf": 3}}, "wann": {"lv:lv1": heute}}
    b = {"topf": {w: {"typ": "mc", "n": 1, "z": 1e18}},
         "tagwerk": {"2999-01-01": {"auf": 5}, morgen: {"auf": 2}},
         "wann": {"lv:lv2": "2999-01-01", "lv:lv1": morgen}}
    vorher = seite.js("() => Date.now()")
    for x, y in ((a, b), (b, a)):
        m = seite.js(MISCHEN, [x, y])
        assert vorher <= m["topf"][w]["z"] <= seite.js("() => Date.now()"), m["topf"]
        assert m["topf"][w]["n"] == 1     # der neuere Fehler gewinnt weiter
        assert m["tagwerk"] == {heute: {"auf": 3}}
        assert m["wann"] == {"lv:lv1": heute}
    # Danach ist der gekappte Fehler wieder ein gewoehnlicher: idempotent.
    assert seite.js(MISCHEN, [m, m]) == m
    assert seite.fehler == []


# ----------------------------------------------------------- Buendelung ---

def _uhr(seite, tag, stunde):
    seite.page.clock.set_fixed_time(datetime.datetime.combine(tag, datetime.time(stunde, 0)))


ABGLEICH = "async (anlass) => await cloudAbgleich(anlass, adapter)"
ZAEHLER = "() => Object.assign({}, ablage.zaehler)"


def test_hoechstens_einmal_am_tag_und_nur_bei_aenderungen(seite, heute_stand):
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 10)
    seite.starten(stand=heute_stand())
    seite.js(ADAPTER)
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    assert seite.js(ZAEHLER) == {"anmelden": 1, "laden": 1, "speichern": 1, "loeschen": 0}

    # Gleicher Tag, nichts geaendert: keine Anfrage. Das Anmelden zaehlt
    # nicht als der eine Schreibvorgang des Tages.
    assert seite.js(ABGLEICH, "pause") == "unveraendert"
    assert seite.js(ZAEHLER)["laden"] == 1
    seite.js("() => known.add('probe:qx1')")
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    seite.js("() => known.add('probe:qx2')")
    assert seite.js(ABGLEICH, "pause") == "nichts"          # heute schon geschrieben
    assert seite.js(ABGLEICH, "start") == "nichts"          # heute schon gelesen
    assert seite.js(ZAEHLER) == {"anmelden": 1, "laden": 2, "speichern": 2, "loeschen": 0}

    # Tag 2: beim Start nur lesen, geschrieben wird beim Verlassen.
    _uhr(seite, tag1 + datetime.timedelta(days=1), 9)
    assert seite.js(ABGLEICH, "start") == "gelesen"
    assert seite.js(ABGLEICH, "pause") == "gespeichert"      # probe:qx2 kommt jetzt mit
    assert "probe:qx2" in json.loads(seite.js("() => ablage.dok.text"))["stand"]["gewusst"]
    assert seite.js(ZAEHLER) == {"anmelden": 1, "laden": 4, "speichern": 3, "loeschen": 0}

    # Tag 3, nichts gelernt: gelesen ja, geschrieben nein.
    _uhr(seite, tag1 + datetime.timedelta(days=2), 20)
    assert seite.js(ABGLEICH, "pause") == "unveraendert"
    assert seite.js(ZAEHLER)["speichern"] == 3

    # Tag 4 ohne Netz: still, und der Tag ist nicht verbraucht.
    _uhr(seite, tag1 + datetime.timedelta(days=3), 18)
    seite.js("() => { known.add('probe:qx4'); ablage.offline = true; }")
    assert seite.js(ABGLEICH, "pause") == "fehler"
    assert seite.js(ABGLEICH, "pause") == "fehler"
    assert seite.js("() => cloudMerker().tag") == (tag1 + datetime.timedelta(days=1)).isoformat()
    seite.js("() => { ablage.offline = false; }")
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    assert seite.js(ZAEHLER)["speichern"] == 4
    assert seite.js(ABGLEICH, "pause") == "nichts"
    assert seite.fehler == []


def test_zweites_geraet_wird_eingearbeitet_weggenommenes_bleibt_weg(seite, heute_stand):
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 10)
    seite.starten(stand=heute_stand())
    seite.js(ADAPTER)
    # Sterne nur auf echten Woertern - andere raeumt sternUmschreiben() weg.
    eigen, tablet = seite.js("() => CATEGORIES[0].words.slice(0, 2).map(w => 'w:' + w.id)")
    seite.js("(k) => { known.add('eigen:wort'); stern = {[k]: {z: Date.now(), r: 0}}; }", eigen)
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True

    # Hier wird der Stern weggenommen. Am naechsten Tag schreibt dieses
    # Geraet drueber - der Stern kommt nicht aus der eigenen Sicherung zurueck.
    _uhr(seite, tag1 + datetime.timedelta(days=1), 10)
    seite.js("() => { stern = {}; }")
    assert seite.js(ABGLEICH, "start") == "gelesen"
    assert seite.js("() => Object.keys(stern)") == []
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    assert json.loads(seite.js("() => ablage.dok.text"))["stand"]["stern"] == {}

    # Ein zweites Geraet hat geschrieben: dessen Woerter und Sterne kommen
    # dazu, die eigenen bleiben.
    _uhr(seite, tag1 + datetime.timedelta(days=2), 10)
    seite.js("""(k) => {
        const s = JSON.parse(ablage.dok.text);
        s.stand.gewusst = ['tablet:wort'];
        s.stand.stern = {[k]: {z: Date.now() - 1000, r: 0}};
        s.stand.muenzen_ges = 0; s.stand.besitz = [];
        ablage.dok = {text: JSON.stringify(s), rev: 'tablet.1'};
    }""", tablet)
    assert seite.js(ABGLEICH, "start") == "zusammengefuehrt"
    z = seite.js("() => ({w: [...known].sort(), s: Object.keys(stern), rev: cloudMerker().rev})")
    assert z == {"w": ["eigen:wort", "tablet:wort"], "s": [tablet], "rev": "tablet.1"}, z
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    stand = json.loads(seite.js("() => ablage.dok.text"))["stand"]
    assert stand["gewusst"] == ["eigen:wort", "tablet:wort"]
    # Und nach dem eigenen Schreiben wird nicht noch einmal zusammengefuehrt.
    _uhr(seite, tag1 + datetime.timedelta(days=3), 10)
    assert seite.js(ABGLEICH, "start") == "gelesen"
    assert seite.fehler == []


# ------------------------------------------- Firestore gegen eine Attrappe ---

def test_firestore_adapter_gegen_attrappe(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=cloud_html))
    for host in FIREBASE:
        seite.page.route("https://%s/**" % host, attrappe)
    seite.starten(stand=heute_stand())
    assert seite.js("() => [CLOUD_AN, cloudEingerichtet(), !!cloudAdapter()]") == [True, True, True]
    assert attrappe.anfragen == []                  # ohne Anmeldung: kein Start-Abgleich

    # Google geht nur mit dem Plugin der Huelle - im Browser gibt es keins.
    assert seite.js("async () => await cloudAnmelden('google')") is False
    assert attrappe.anfragen == []

    assert seite.js("async () => await cloudAnmelden('anonym')") is True
    dok_pfad = "firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/users/%s" % (PROJEKT, UID)
    assert attrappe.anfragen == [
        ("POST", "identitytoolkit.googleapis.com/v1/accounts:signUp", ""),
        ("GET", dok_pfad, "Bearer id-1"),
        ("PATCH", dok_pfad, "Bearer id-1")]
    assert set(attrappe.dok) == {"daten", "rev"}
    datei = json.loads(attrappe.dok["daten"]["stringValue"])
    assert datei["app"] == "zmaj" and "stand" in datei
    merker = seite.js("() => JSON.parse(localStorage.getItem('zmaj_cloud'))")
    assert merker["uid"] == UID and merker["art"] == "anonym" and merker["rev"] == attrappe.dok["rev"]["stringValue"]

    # In den Hintergrund mit etwas Neuem: einmal lesen, einmal schreiben.
    attrappe.anfragen.clear()
    seite.js("""async () => {
        known.add('neu:im-hintergrund');
        Object.defineProperty(document, 'hidden', {configurable: true, get: () => true});
        document.dispatchEvent(new Event('visibilitychange'));
    }""")
    seite.page.wait_for_function("() => !cloudLaeuft && JSON.parse(localStorage.getItem('zmaj_cloud')).tag === today()")
    assert [a for a, _, _ in attrappe.anfragen] == ["GET", "PATCH"]
    assert "neu:im-hintergrund" in json.loads(attrappe.dok["daten"]["stringValue"])["stand"]["gewusst"]

    # Neu geladen ist der Ausweis weg: der Start holt mit dem gemerkten
    # Erneuerungsschluessel einen neuen und liest - heute schon gelesen,
    # also gar nichts. Am naechsten Tag dagegen genau eine Leseanfrage.
    attrappe.anfragen.clear()
    seite.js("() => { delete document.hidden; }")
    seite.page.reload()
    seite.bereit()
    seite.page.wait_for_timeout(500)
    assert attrappe.anfragen == []
    # cloudLaeuft haelt den Abgleich auf, den das Verlassen der alten Seite
    # (visibilitychange) sonst noch anstiesse - gezaehlt wird nur der Start.
    seite.js("""() => { const m = JSON.parse(localStorage.getItem('zmaj_cloud'));
                        m.gelesen = '2026-01-01'; localStorage.setItem('zmaj_cloud', JSON.stringify(m));
                        cloudLaeuft = true; }""")
    seite.page.reload()
    seite.bereit()
    seite.page.wait_for_function("() => !cloudLaeuft && JSON.parse(localStorage.getItem('zmaj_cloud')).gelesen === today()")
    assert attrappe.anfragen == [
        ("POST", "securetoken.googleapis.com/v1/token", ""),
        ("GET", dok_pfad, "Bearer id-2")]

    # Konto loeschen: Dokument und Konto weg, der Lernstand bleibt.
    attrappe.anfragen.clear()
    assert seite.js("async () => await cloudLoeschen()") is True
    assert [(a, p) for a, p, _ in attrappe.anfragen] == [
        ("DELETE", dok_pfad), ("POST", "identitytoolkit.googleapis.com/v1/accounts:delete")]
    assert attrappe.dok is None
    assert seite.js("() => [localStorage.getItem('zmaj_cloud'), known.has('neu:im-hintergrund')]") == [None, True]
    # Jede Anfrage ging an Firebase - und keine davon wirklich hinaus.
    assert all(any(h in u for h in FIREBASE) for u in seite.fremd), seite.fremd
    assert seite.fehler == []


# ------------------------------------- Loeschen mit zu alter Anmeldung ---
# 19.10.2026: Firebase loescht ein Konto nur nach einer frischen Anmeldung.
# Vorher blieb dann der Merker, und das naechste 'pause' lud die eben
# geloeschte Sicherung wieder hoch.

DOK = "firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/users/%s" % (PROJEKT, UID)
KONTO_WEG = "identitytoolkit.googleapis.com/v1/accounts:delete"
GOOGLE = "identitytoolkit.googleapis.com/v1/accounts:signInWithIdp"

# Das Plugin der Huelle, nachgestellt. Waehrend des Loeschens stoesst es
# einen Abgleich an - wie die Kontoauswahl, die die App verdeckt.
GOOGLE_PLUGIN = """() => { window.Capacitor = {Plugins: {ZmajAnmeldung: {googleAusweis: async () => {
    window.googleFragen = (window.googleFragen || 0) + 1;
    if(window.beimLoeschen) window.abgleichDabei = await cloudAbgleich('pause');
    return {idToken: 'google-probe'};
}}}}; return true; }"""


def _cloud_seite(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=cloud_html))
    for host in FIREBASE:
        seite.page.route("https://%s/**" % host, attrappe)
    seite.starten(stand=heute_stand())
    return attrappe


def _wege(attrappe):
    return [(a, p) for a, p, _ in attrappe.anfragen]


def test_loeschen_anonym_zu_alt_sicherung_weg_und_abgemeldet(seite, heute_stand, cloud_html):
    attrappe = _cloud_seite(seite, heute_stand, cloud_html)
    assert seite.js("async () => await cloudAnmelden('anonym')") is True
    assert attrappe.dok is not None

    # Die Sicherung laesst sich nicht loeschen: nichts passiert, angemeldet
    # bleiben fuer einen neuen Versuch, das Konto unberuehrt.
    attrappe.anfragen.clear()
    attrappe.dok_fehler = True
    assert seite.js("async () => await cloudLoeschen()") is False
    assert _wege(attrappe) == [("DELETE", DOK)]
    assert attrappe.dok is not None and not attrappe.konto_weg
    assert seite.js("() => cloudMerker() && cloudMerker().uid") == UID

    # Sicherung geht, das Konto verlangt eine frische Anmeldung - anonym gibt
    # es keine. Die Sicherung ist weg, abgemeldet wird trotzdem.
    attrappe.anfragen.clear()
    attrappe.dok_fehler = False
    attrappe.alt = {"id-1", "id-2"}
    assert seite.js("async () => await cloudLoeschen()") == "konto bleibt"
    assert _wege(attrappe) == [("DELETE", DOK), ("POST", KONTO_WEG)]
    assert attrappe.dok is None and not attrappe.konto_weg
    assert seite.js("() => localStorage.getItem('zmaj_cloud')") is None

    # Und nichts laedt die Sicherung wieder hoch - weder direkt noch beim
    # Verlassen der App.
    attrappe.anfragen.clear()
    assert seite.js("""async () => {
        known.add('neu:nach-dem-loeschen');
        const r = await cloudAbgleich('pause');
        Object.defineProperty(document, 'hidden', {configurable: true, get: () => true});
        document.dispatchEvent(new Event('visibilitychange'));
        await new Promise(f => setTimeout(f, 300));
        delete document.hidden;
        return r;
    }""") == "nichts"
    assert attrappe.anfragen == [] and attrappe.dok is None

    # Ist das Konto schon weg (USER_NOT_FOUND), gilt das als geloescht.
    assert seite.js("async () => await cloudAnmelden('anonym')") is True
    attrappe.alt = set()
    attrappe.konto_weg = True
    assert seite.js("async () => await cloudLoeschen()") is True
    assert attrappe.dok is None and seite.js("() => localStorage.getItem('zmaj_cloud')") is None
    assert seite.fehler == []


def test_loeschen_google_zu_alt_meldet_neu_an(seite, heute_stand, cloud_html):
    attrappe = _cloud_seite(seite, heute_stand, cloud_html)
    seite.js(GOOGLE_PLUGIN)
    assert seite.js("async () => await cloudAnmelden('google')") is True
    assert _wege(attrappe) == [("POST", GOOGLE), ("GET", DOK), ("PATCH", DOK)]
    assert seite.js("() => cloudMerker().art") == "google"

    # In der Kontoauswahl ein anderes Google-Konto: das wird nicht
    # geloescht. Die Sicherung ist weg, abgemeldet wird.
    attrappe.anfragen.clear()
    attrappe.alt = {"id-1", "id-2", "id-g1"}
    attrappe.google_uid = "uidAnders"
    assert seite.js("async () => await cloudLoeschen()") == "konto bleibt"
    assert _wege(attrappe) == [("DELETE", DOK), ("POST", KONTO_WEG), ("POST", GOOGLE)]
    assert attrappe.geloescht_mit == ["id-g1"] and not attrappe.konto_weg
    assert attrappe.dok is None and seite.js("() => localStorage.getItem('zmaj_cloud')") is None

    # Neu angemeldet und spaeter geloescht: Firebase verlangt eine frische
    # Anmeldung, die App fragt Google noch einmal und loescht danach. Der
    # Abgleich, den die Kontoauswahl dabei anstoesst, wartet.
    attrappe.google_uid = UID
    assert seite.js("async () => await cloudAnmelden('google')") is True
    attrappe.alt.add("id-g3")
    attrappe.anfragen.clear()
    attrappe.geloescht_mit.clear()
    seite.js("() => { known.add('neu:vor-dem-loeschen'); window.googleFragen = 0; window.beimLoeschen = true; }")
    assert seite.js("async () => await cloudLoeschen()") is True
    assert _wege(attrappe) == [("DELETE", DOK), ("POST", KONTO_WEG), ("POST", GOOGLE), ("POST", KONTO_WEG)]
    assert attrappe.geloescht_mit == ["id-g3", "id-g4"] and attrappe.konto_weg
    assert seite.js("() => [window.googleFragen, window.abgleichDabei]") == [1, "nichts"]
    assert attrappe.dok is None
    assert seite.js("() => [localStorage.getItem('zmaj_cloud'), known.has('neu:vor-dem-loeschen'), cloudLaeuft]") \
        == [None, True, False]
    assert all(any(h in u for h in FIREBASE) for u in seite.fremd), seite.fremd
    assert seite.fehler == []
