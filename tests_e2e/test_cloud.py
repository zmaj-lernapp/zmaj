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
from firebase_attrappe import FIREBASE, PROJEKT, UID, Attrappe, wege

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
        # Lernkartei (v110): Tage als Zahl seit APP_START, alle vor heute
        "kartei": {"tag": 80, "n": 5, "w": {"gleich:a": [1, 82, 79], "spaet:a": [3, 90, 80],
                                            "frueh:a": [2, 85, 70], "nur:a": [0, 81, 80]}},
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
        "kartei": {"tag": 80, "n": 7, "w": {"gleich:a": [2, 81, 79], "spaet:a": [1, 81, 75],
                                            "frueh:a": [4, 99, 78], "nur:b": [5, 120, 60]}},
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
    # Lernkartei: je Wort der zuletzt geuebte Stand, am selben Tag der fruehere
    # Termin; der Tageszaehler am selben Tag als Maximum (29.10.2026)
    assert m["kartei"] == {"tag": 80, "n": 7, "w": {
        "gleich:a": [2, 81, 79], "spaet:a": [3, 90, 80], "frueh:a": [4, 99, 78],
        "nur:a": [0, 81, 80], "nur:b": [5, 120, 60]}}
    assert seite.js(MISCHEN, [dict(a, kartei=dict(a["kartei"], tag=81, n=1)), b])["kartei"]["n"] == 1
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
    assert set(a["kartei"]["w"]) | set(b["kartei"]["w"]) == set(m["kartei"]["w"])
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
    if(window.googleNein){ const e = new Error(window.googleNein); e.code = window.googleNein; throw e; }
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


def test_loeschen_anonym_zu_alt_sicherung_weg_und_abgemeldet(seite, heute_stand, cloud_html):
    attrappe = _cloud_seite(seite, heute_stand, cloud_html)
    assert seite.js("async () => await cloudAnmelden('anonym')") is True
    assert attrappe.dok is not None

    # Die Sicherung laesst sich nicht loeschen: nichts passiert, angemeldet
    # bleiben fuer einen neuen Versuch, das Konto unberuehrt.
    attrappe.anfragen.clear()
    attrappe.dok_fehler = True
    assert seite.js("async () => await cloudLoeschen()") is False
    assert wege(attrappe) == [("DELETE", DOK)]
    assert attrappe.dok is not None and not attrappe.konto_weg
    assert seite.js("() => cloudMerker() && cloudMerker().uid") == UID

    # Sicherung geht, das Konto verlangt eine frische Anmeldung - anonym gibt
    # es keine. Die Sicherung ist weg, abgemeldet wird trotzdem.
    attrappe.anfragen.clear()
    attrappe.dok_fehler = False
    attrappe.alt = {"id-1", "id-2"}
    assert seite.js("async () => await cloudLoeschen()") == "konto bleibt"
    assert wege(attrappe) == [("DELETE", DOK), ("POST", KONTO_WEG)]
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


def test_loeschen_google_fragt_zuerst(seite, heute_stand, cloud_html):
    attrappe = _cloud_seite(seite, heute_stand, cloud_html)
    seite.js(GOOGLE_PLUGIN)
    assert seite.js("async () => await cloudAnmelden('google')") is True
    assert wege(attrappe) == [("POST", GOOGLE), ("GET", DOK), ("PATCH", DOK)]
    assert seite.js("() => cloudMerker().art") == "google"
    # Die Anmeldung von eben ist fuer Firebase schon zu alt zum Loeschen.
    attrappe.alt = {"id-1", "id-2", "id-g1"}

    # 28.10.2026 (Pruefbericht): Google fragt ZUERST. Auswahl abgebrochen
    # oder ein anderes Google-Konto gewaehlt: nichts ist geloescht, und
    # angemeldet bleibt man auch. Bis dahin war die Sicherung dann schon weg.
    for nein, grund in (("abgebrochen", "GOOGLE_ABGEBROCHEN"), ("", "GOOGLE_ANDERES_KONTO")):
        attrappe.anfragen.clear()
        attrappe.google_uid = UID if nein else "uidAnders"
        seite.js("(nein) => { window.googleNein = nein; }", nein)
        assert seite.js("async () => [await cloudLoeschen(), cloudFehlerGrund]") == [False, grund]
        assert wege(attrappe) == ([] if nein else [("POST", GOOGLE)])
        assert attrappe.geloescht_mit == [] and not attrappe.konto_weg
        assert attrappe.dok is not None and seite.js("() => cloudMerker() && cloudMerker().uid") == UID

    # Dasselbe Konto: frisch angemeldet, danach Sicherung und Konto weg. Der
    # Abgleich, den die Kontoauswahl dabei anstoesst, wartet.
    attrappe.google_uid = UID
    attrappe.anfragen.clear()
    seite.js("() => { known.add('neu:vor-dem-loeschen'); window.googleFragen = 0; window.beimLoeschen = true; }")
    assert seite.js("async () => await cloudLoeschen()") is True
    assert wege(attrappe) == [("POST", GOOGLE), ("DELETE", DOK), ("POST", KONTO_WEG)]
    assert attrappe.geloescht_mit == ["id-g3"] and attrappe.konto_weg
    assert seite.js("() => [window.googleFragen, window.abgleichDabei]") == [1, "nichts"]
    assert attrappe.dok is None
    assert seite.js("() => [localStorage.getItem('zmaj_cloud'), known.has('neu:vor-dem-loeschen'), cloudLaeuft]") \
        == [None, True, False]
    assert all(any(h in u for h in FIREBASE) for u in seite.fremd), seite.fremd
    assert seite.fehler == []


# ------------------------------------------- Felder einer neueren Fassung ---
# 28.10.2026, Vorarbeit fuer v110 (zeitgesteuerte Wiederholung): Was diese
# Fassung nicht kennt, bleibt unveraendert und wird wieder mitgeschrieben -
# sonst loeschte ein Handy mit v109 die Wiederholungsdaten eines Tablets mit
# v110 beim naechsten Abgleich (standFremd in index.html).

WDH_ALT = {"w:a": {"faellig": "2026-11-01", "stufe": 1}}
WDH_NEU = {"w:a": {"faellig": "2026-11-05", "stufe": 2}, "w:b": {"faellig": "2026-11-02", "stufe": 1}}


def test_zusammenfuehren_behaelt_unbekannte_felder(seite, heute_stand):
    seite.starten(stand=heute_stand())
    a, b, _ = _staende(seite)
    bekannt = set(a)
    assert set(seite.js("() => [...STAND_FELDER]")) == bekannt == set(seite.js("() => Object.keys(standAlsObjekt())"))
    a = dict(a, wdh=WDH_ALT, nur_a={"x": [1, 2]}, premium=True)
    b = dict(b, wdh=WDH_NEU, nur_b=7, premium=True)
    # Ein Fehler im Topf mit einer Angabe, die diese Fassung nicht kennt.
    a["topf"] = dict(a["topf"], **{"w:alt": {"typ": "mc", "n": 1, "z": 1000, "faellig": "alt"}})
    b["topf"] = dict(b["topf"], **{"w:alt": {"typ": "mcrev", "n": 0, "z": 4000, "faellig": "neu"}})
    m = seite.js(MISCHEN, [a, b])
    assert set(m) == bekannt | {"wdh", "nur_a", "nur_b"}          # premium nicht
    assert m["wdh"] == WDH_NEU                                    # auf beiden Seiten: die Cloud
    assert m["nur_a"] == {"x": [1, 2]} and m["nur_b"] == 7       # auf einer Seite: von dort
    assert m["topf"]["w:alt"] == {"typ": "mcrev", "n": 0, "z": 4000, "faellig": "neu"}   # beim Gewinner
    # Die bekannten Felder wie ohne die neuen.
    ohne = seite.js(MISCHEN, [_staende(seite)[0], _staende(seite)[1]])
    assert {k: m[k] for k in bekannt if k != "topf"} == {k: ohne[k] for k in bekannt if k != "topf"}
    assert seite.js(MISCHEN, [m, m]) == m                          # idempotent
    assert seite.js(MISCHEN, [m, b])["wdh"] == WDH_NEU
    for leer in ({}, None):
        assert seite.js(MISCHEN, [a, leer])["wdh"] == WDH_ALT          # nur das Geraet hat es
    assert seite.js(MISCHEN, [{}, b])["wdh"] == WDH_NEU
    # Ein "__proto__" aus einer fremden Datei wird kein Feld und kein Prototyp.
    z = seite.js("""() => { const m = standZusammenfuehren(JSON.parse('{"__proto__": {"x": 1}, "neu": 1}'), {});
                           return [Object.keys(m).includes('__proto__'), m.x === undefined, m.neu]; }""")
    assert z == [False, True, 1]
    assert seite.fehler == []


def test_unbekannte_felder_bleiben_im_geraet_und_in_der_datei(seite, heute_stand):
    seite.starten(stand=heute_stand(wdh=WDH_ALT, zukunft={"version": 2}))
    z = seite.js("() => ({stand: standAlsObjekt(), datei: JSON.parse(sicherungInhalt()).stand})")
    for s in (z["stand"], z["datei"]):
        assert s["wdh"] == WDH_ALT and s["zukunft"] == {"version": 2}, s
    seite.js("async () => { known.add('probe:wort'); await saveProgress(); }")
    seite.neu_laden()
    gespeichert = seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand'))")
    assert gespeichert["wdh"] == WDH_ALT and gespeichert["zukunft"] == {"version": 2}
    assert "probe:wort" in gespeichert["gewusst"]
    # Wirft das Uebernehmen eines neuen Stands, kommen auch die fremden Felder
    # des alten zurueck (standErsetzen).
    z = seite.js("""() => [standErsetzen(() => ({neu: 1, get gewusst(){ throw new Error('probe'); }})),
                           standAlsObjekt()]""")
    assert z[0] is False and z[1]["wdh"] == WDH_ALT and "neu" not in z[1], z[0]
    assert seite.fehler == []


def test_cloud_behaelt_felder_eines_neueren_geraets(seite, heute_stand):
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 10)
    seite.starten(stand=heute_stand(wdh=WDH_ALT))
    seite.js(ADAPTER)
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    assert json.loads(seite.js("() => ablage.dok.text"))["stand"]["wdh"] == WDH_ALT

    # Ein Tablet mit v110 schreibt neuere Wiederholungsdaten und ein neues Feld.
    _uhr(seite, tag1 + datetime.timedelta(days=1), 10)
    seite.js("""(w) => { const s = JSON.parse(ablage.dok.text);
                         s.stand.wdh = w; s.stand.v110 = {an: true}; s.stand.gewusst.push('tablet:wort');
                         ablage.dok = {text: JSON.stringify(s), rev: 'tablet.1'}; }""", WDH_NEU)
    assert seite.js(ABGLEICH, "start") == "zusammengefuehrt"
    assert seite.js("() => [standAlsObjekt().wdh, standAlsObjekt().v110]") == [WDH_NEU, {"an": True}]
    # Dieses Geraet lernt weiter und schreibt - die Daten des Tablets bleiben,
    # die alte eigene Kopie kommt nicht zurueck.
    seite.js("() => known.add('handy:wort')")
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    stand = json.loads(seite.js("() => ablage.dok.text"))["stand"]
    assert stand["wdh"] == WDH_NEU and stand["v110"] == {"an": True}
    assert {"tablet:wort", "handy:wort"} <= set(stand["gewusst"])
    assert seite.fehler == []


def test_cloud_grenze_in_bytes(seite, heute_stand):
    """500 000 mal 'č' sind 500 000 Zeichen, aber 1 000 000 Bytes - mehr, als
    Firestore in einem Dokument nimmt. Die App schreibt das nicht in die
    Cloud. Seit dem Pruefbefund vom 28.10.2026 scheitert daran aber nicht
    mehr das ganze Hochladen: nur das zu grosse fremde Feld bleibt in der
    Cloud weg, auf dem Geraet bleibt es, und der Lernfortschritt kommt an.
    'zu gross' gibt es nur noch, wenn schon der eigene Stand nicht passt."""
    seite.starten(stand=heute_stand())
    seite.js(ADAPTER)
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    seite.js("() => { standFremd = {probe: 'č'.repeat(500000), klein: {a: 1}}; known.add('probe:wort'); }")
    assert seite.js("() => JSON.stringify(sicherungObjekt()).length < CLOUD_GROESSE_MAX")
    # "abmelden" schreibt wie "pause", aber ohne die Grenze von einmal am Tag.
    assert seite.js(ABGLEICH, "abmelden") == "gespeichert"
    text = seite.js("() => ablage.dok.text")
    assert len(text.encode("utf-8")) <= 900000
    stand = json.loads(text)["stand"]
    assert "probe" not in stand and stand["klein"] == {"a": 1} and "probe:wort" in stand["gewusst"]
    assert seite.js("() => [Object.keys(standFremd), cloudMerker().fremd]") == [["probe", "klein"], ["klein"]]
    seite.js("() => { standFremd = {probe: 'c'.repeat(500000)}; }")
    assert seite.js(ABGLEICH, "abmelden") == "gespeichert"
    assert len(json.loads(seite.js("() => ablage.dok.text"))["stand"]["probe"]) == 500000
    # Erst wenn schon die eigenen Felder nicht passen.
    seite.js("() => { standFremd = {}; wann = {probe: 'č'.repeat(460000)}; }")
    assert seite.js(ABGLEICH, "abmelden") == "zu gross"
    assert len(json.loads(seite.js("() => ablage.dok.text"))["stand"]["probe"]) == 500000
    assert seite.fehler == []


def test_grosse_fremde_felder_nie_alle_auf_einmal(seite, heute_stand):
    """Pruefbefund 28.10.2026: Die Grenze fuer fremde Felder galt ganz oder
    gar nicht. Lag die Summe beider Seiten darueber, fielen beim
    Zusammenfuehren alle weg, auch die aktuellen aus der Cloud. Jetzt Feld
    fuer Feld, und die Cloud (b) geht vor."""
    seite.starten(stand=heute_stand())
    n = 450000
    assert seite.js("""(n) => Object.keys(standFremdAus({x: 'x'.repeat(n), y: 'y'.repeat(n), z: 1,
                                                       gewusst: [], premium: true}))""", n) == ["x", "z"]
    a, b, _ = _staende(seite)
    a = dict(a, nur_a="a" * n, klein_a=1)
    b = dict(b, nur_b="b" * n, klein_b=2)
    fremd = """([a, b]) => Object.keys(standZusammenfuehren(a, b)).filter(k => !STAND_FELDER.has(k))"""
    assert seite.js(fremd, [a, b]) == ["nur_b", "klein_b", "klein_a"]
    assert seite.js(fremd, [a, {}]) == ["nur_a", "klein_a"]
    # Uebernommen wird das Ergebnis ohne weiteren Verlust.
    assert seite.js("""([a, b]) => { standUebernehmen(standZusammenfuehren(a, b));
                                      return Object.keys(standFremd); }""", [a, b]) == ["nur_b", "klein_b", "klein_a"]
    assert seite.fehler == []


def test_cloud_ersetzt_grosses_feld_ohne_alles_zu_verlieren(seite, heute_stand):
    """Die Probe aus dem Pruefbefund: Das Handy hat ein grosses fremdes Feld
    in der Cloud, ein Tablet mit neuerer Fassung ersetzt es durch ein
    anderes, ebenso grosses. Bis dahin fielen beim Abgleich beide weg, und
    das naechste Hochladen loeschte die Daten des Tablets in der Cloud."""
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 10)
    seite.starten(stand=heute_stand(wdh_alt="a" * 450000))
    seite.js(ADAPTER)
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    assert seite.js("() => cloudMerker().fremd") == ["wdh_alt"]
    _uhr(seite, tag1 + datetime.timedelta(days=1), 10)
    seite.js("""() => { const s = JSON.parse(ablage.dok.text);
                        delete s.stand.wdh_alt; s.stand.wdh_neu = 'b'.repeat(450000);
                        ablage.dok = {text: JSON.stringify(s), rev: 'tablet.2'}; }""")
    assert seite.js(ABGLEICH, "start") == "zusammengefuehrt"
    assert seite.js("() => Object.keys(standFremd)") == ["wdh_neu"]
    seite.js("() => known.add('handy:wort')")
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    stand = json.loads(seite.js("() => ablage.dok.text"))["stand"]
    assert stand["wdh_neu"] == "b" * 450000 and "wdh_alt" not in stand
    assert "handy:wort" in stand["gewusst"]
    assert seite.fehler == []


def test_geloeschtes_fremdes_feld_kommt_nicht_zurueck(seite, heute_stand):
    """Pruefbefund 28.10.2026: Loeschte oder benannte die neuere Fassung ein
    eigenes Feld um, schrieb ein Geraet mit dieser Fassung die alte Kopie
    zurueck in die Cloud. Jetzt merkt es sich, welche fremden Felder dort
    standen (m.fremd): Was dort stand und jetzt fehlt, bleibt weg. Was hier
    neu ist (etwa aus einer Sicherungsdatei), kommt mit."""
    tag1 = datetime.date.today()
    _uhr(seite, tag1, 10)
    seite.starten(stand=heute_stand(wdh_v1={"a": 1}))
    seite.js(ADAPTER)
    bekannt = set(seite.js("() => [...STAND_FELDER]"))
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    # Ein Feld aus einer Sicherungsdatei, noch nicht hochgeladen.
    seite.js("() => { standFremd = Object.assign({}, standFremd, {aus_datei: {d: 1}}); }")
    _uhr(seite, tag1 + datetime.timedelta(days=1), 10)
    seite.js("""() => { const s = JSON.parse(ablage.dok.text);
                        delete s.stand.wdh_v1; s.stand.wdh_v2 = {a: 2};
                        ablage.dok = {text: JSON.stringify(s), rev: 'tablet.3'}; }""")
    assert seite.js(ABGLEICH, "start") == "zusammengefuehrt"
    assert seite.js("() => cloudMerker().fremd") == ["wdh_v2"]
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    stand = json.loads(seite.js("() => ablage.dok.text"))["stand"]
    assert {k: v for k, v in stand.items() if k not in bekannt} == {"wdh_v2": {"a": 2}, "aus_datei": {"d": 1}}
    assert sorted(seite.js("() => cloudMerker().fremd")) == ["aus_datei", "wdh_v2"]
    # Rein: ohne cloudVorher (erste Anmeldung) kommt alles von a mit, mit
    # nur das, was die Cloud nie hatte.
    mischen = "([a, b, v]) => Object.keys(standZusammenfuehren(a, b, v)).filter(k => !STAND_FELDER.has(k))"
    assert seite.js(mischen, [{"alt": 1, "neu": 1}, {"b": 1}, None]) == ["b", "alt", "neu"]
    assert seite.js(mischen, [{"alt": 1, "neu": 1}, {"b": 1}, ["alt", "b"]]) == ["b", "neu"]
    assert seite.fehler == []
