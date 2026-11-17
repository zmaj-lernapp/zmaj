# -*- coding: utf-8 -*-
"""Cloud-Sicherung gepackt, Weg A (Ajdin am 13.11.2026) - im echten Browser.

Release\\Entscheidungen_2026-11-13\\cloud.md, Fragen 2a, 3a, 4a. Geprueft wird:
  - Rundreise: gepackt und wieder ausgepackt kommt jeder Stand Byte fuer
    Byte zurueck, auch mit Sonderfaellen in der Kartei; jedes gewusste Wort
    steht gepackt nur noch einmal drin.
  - alt -> neu -> alt: 1.4 schreibt die alte Form, solange sie passt, packt
    erst darueber und schreibt wieder die alte, wenn es wieder passt. Ein
    zweites Geraet mit 1.4 liest beides.
  - Erst nachsehen: ohne fremdes Schreiben nur rev, nie der ganze Stand.
  - Beschaedigte Daten: nichts wirft, der eigene Stand bleibt, und was sich
    nicht auspacken laesst, wird weitergetragen statt weggeworfen.
  - Die Probe vor dem Hochladen: stimmt das Ausgepackte nicht, oder kann das
    Geraet kein gzip, geht nichts Gepacktes hoch.
  - Ein sehr grosser Stand mit 30 000 Eintraegen passt gepackt.
  - Zwei Geraete, eins mit dem ECHTEN Code von 1.3 (git show): solange nicht
    gepackt wird, liest 1.3 wie immer; ein gepacktes Dokument traegt 1.3
    unveraendert weiter, und 1.4 fuehrt danach alles zusammen - auch im
    Randfall, in dem 1.3 das gepackte Feld aus Platzgruenden fallen laesst.
  - Die Test-App von app_bauen.py --immer-packen mit 1.3 und 1.4, wie im
    Handytest (Release\\Entscheidungen_2026-11-13\\cloud_handytest.md).
  - Ein Geraet traegt gepackt1 noch von 1.3 und wird auf 1.4 aktualisiert
    (Schritt 1 und Schritt 2): es packt gepackt1 vor dem Schreiben aus, und
    ein neues Geraet hat alles, auch wenn das schreibende weg ist
    (Pruefbefund 13.11.2026).
  - Firestore gegen die Attrappe: Feldmaske fuer rev, und das gepackte
    Dokument erfuellt firestore.rules (nur daten und rev, daten ein Text bis
    900 000 Zeichen).
"""
import base64
import datetime
import gzip
import json
import os
import shutil
import subprocess

import pytest
from conftest import WURZEL, Seite
from firebase_attrappe import FIREBASE, Attrappe

# Der Stand von 1.3 (v116, live seit 08.11.2026): "Update 1.3" auf
# sammeln-v111, auch auf origin/update-1.3. Der Cloud-Teil ist dort derselbe
# wie unmittelbar vor diesem Umbau.
FASSUNG_13 = "8bb734e"
GRENZE = 900000
# So viele erfundene Woerter dazu, und die alte Form passt nicht mehr (der
# volle Stand unten hat rund 820 000 Bytes, jedes dazu rund 23).
MEHR = 5000

# Ein Stand wie bei einem, der alles kann (wie test_kartei.py, Groesse): alle
# Woerter gewusst und in der Kartei, Topf und Sterne voll, alle Level
# bestanden. extra: so viele erfundene Woerter zusaetzlich in gewusst (die
# behaelt die App, siehe altenFortschrittUmschreiben), damit die alte Form
# ueber die Grenze kommt.
VOLL = """(extra) => {
    const ids = [...new Set(CATEGORIES.flatMap(c => c.words).map(w => w.id))];
    const heute = karteiTag(), ab = [1, 3, 7, 14, 30, 90, 180];
    known = new Set(ids.concat(Array.from({length: extra}, (_, i) => 'probe:mehr-' + i)));
    kartei = {tag: heute, n: 5, w: {}};
    ids.forEach((id, i) => { const s = i % 7, l = Math.max(0, heute - (i % 5)); kartei.w[id] = [s, l + ab[s], l]; });
    topf = {}; stern = {};
    ids.slice(0, TOPF_MAX).forEach((id, i) => { topf['w:' + id] = {typ: 'mcrev', n: 1, z: Date.now() - i}; });
    ids.slice(0, STERN_MAX).forEach((id, i) => { stern['w:' + id] = {z: Date.now() - i, r: Date.now()}; });
    passed = new Set(CATEGORIES.map(c => c.id));
    return {ids: ids.length, alt: utf8Laenge(JSON.stringify(sicherungObjekt()))};
}"""
# Anmelden mit dem Speicher-Adapter; der Test traegt das Dokument von Geraet
# zu Geraet. kennung: "erst nachsehen" wie Firestore (ablage.mitKennung).
ANMELDEN = """async ([dok, kennung]) => {
    window.ablage = {uid: 'konto-probe', mitKennung: !!kennung};
    if(dok) window.ablage.dok = dok;
    window.adapter = cloudSpeicherAdapter(window.ablage);
    return await cloudAnmelden('google', adapter);
}"""
ABGLEICH = "async (anlass) => await cloudAbgleich(anlass, adapter)"
DOK_LEGEN = "(dok) => { ablage.dok = dok; }"
DOK_HOLEN = "() => ablage.dok"
ZAEHLER = "() => Object.assign({}, ablage.zaehler)"
GELESEN = "async (text) => await cloudStandLesen(text)"
WOERTER = "() => [...known].sort()"
GEPACKT_GLEICH = """async () => {
    const text = ablage.dok.text;
    return JSON.stringify(await cloudStandLesen(text)) === JSON.stringify(standAlsObjekt());
}"""


def _stand(dok):
    return json.loads(dok["text"])["stand"]


def _uhr(seite, tag, stunde=10):
    seite.page.clock.set_fixed_time(datetime.datetime.combine(tag, datetime.time(stunde, 0)))


def _geraet(browser, basis):
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE", service_workers="block")
    return ctx, Seite(ctx.new_page(), basis)


@pytest.fixture
def zweites(browser, basis):
    ctx, s = _geraet(browser, basis)
    yield s
    ctx.close()


# ------------------------------------------------------------- Rundreise ---

RUNDREISE = """async (json) => {
    const s = JSON.parse(json);
    const text = await cloudPacken({app: 'zmaj', version: 1, datum: '2026-11-13', stand: s});
    if(!text) return {text: null};
    const zurueck = await cloudStandLesen(text);
    return {laenge: utf8Laenge(text), felder: Object.keys(JSON.parse(text).stand),
            gleich: JSON.stringify(zurueck) === JSON.stringify(s)};
}"""
KARTEI = {"tag": 3, "n": 1, "w": {"a:b": [1, 4, 3], "č:ćž": [0, 5, 4]}}
SONDERFAELLE = {
    "leer": "{}",
    "einfach": {"gewusst": ["a:b", "č:ćž"], "kartei": KARTEI},
    "andere_reihenfolge": {"gewusst": ["č:ćž", "x:y", "a:b"], "kartei": KARTEI},
    "nicht_in_gewusst_und_schief": {
        "gewusst": ["a:b", "c:d"],
        "kartei": {"tag": 0, "n": 0, "w": {
            "a:b": [1, 2, 3], "fehlt:a": [1, 2, 3], "zwei:a": [1, 2], "halb:a": [1.5, 2, 3],
            "text:a": ["1", 2, 3], "c:d": [-1, 2, 3], "vier:a": [1, 2, 3, 4], "objekt:a": {"s": 1},
            "nichts:a": None, "riesig:a": [2 ** 53, 1, 1]}, "neu": {"x": 1}}},
    "gewusst_doppelt_und_kein_text": {"gewusst": ["a:b", "a:b", 5, None, "c:d"],
                                      "kartei": {"tag": 1, "n": 1, "w": {"c:d": [2, 9, 2], "a:b": [0, 1, 0]}}},
    "proto": '{"gewusst":["__proto__","a:b"],"kartei":{"tag":0,"n":0,"w":{"__proto__":[1,2,3],"a:b":[0,1,0]}}}',
    "ganzzahl_schluessel": {"gewusst": ["a:b", "12"], "kartei": {"tag": 0, "n": 0, "w": {"a:b": [1, 2, 0], "12": [3, 4, 1]}}},
    "w_keine_tabelle": {"gewusst": ["a:b"], "kartei": {"tag": 0, "n": 0, "w": [1, 2]}},
    "ohne_kartei": {"gewusst": ["a:b"], "wdh": {"a:b": 1}},
    "gewusst_keine_liste": {"gewusst": "a:b", "kartei": KARTEI},
    "kartei_leer": {"gewusst": [], "kartei": {"tag": 0, "n": 0, "w": {}}},
    "fremd_und_umlaute": {"gewusst": ["šešir:ž"], "zukunft": {"version": 2, "text": "čćžšđ ČĆŽŠĐ ü"},
                          "kartei": {"tag": 0, "n": 0, "w": {"šešir:ž": [6, 9999, 9999]}}},
}


@pytest.mark.parametrize("name", list(SONDERFAELLE))
def test_rundreise_genau_auch_mit_sonderfaellen(seite, heute_stand, name):
    seite.starten(stand=heute_stand())
    s = SONDERFAELLE[name]
    z = seite.js(RUNDREISE, s if isinstance(s, str) else json.dumps(s, ensure_ascii=False))
    assert z.get("gleich") is True, z
    assert z["felder"] == ["gepackt1"]
    assert seite.fehler == []


def test_voller_stand_gepackt_ein_viertel_und_jedes_wort_einmal(seite, heute_stand):
    """Der volle Stand von 1.3 (alle 7 997 Kennungen) belegte 95 % der Grenze.
    Gepackt bleibt rund ein Viertel - gemessen am 13.11.2026 mit diesem
    Stand: 843 000 alt, 195 000 gepackt."""
    seite.starten(stand=heute_stand())
    v = seite.js(VOLL, 0)
    z = seite.js("""async () => {
        const sich = sicherungObjekt(), text = await cloudPacken(sich);
        const ids = [...known], id = ids[ids.length - 1];       // nicht in Topf und Sternen
        const zaehle = (t, w) => t.split(JSON.stringify(w)).length - 1;
        return {alt: utf8Laenge(JSON.stringify(sich)), neu: utf8Laenge(text), id,
                gleich: JSON.stringify(await cloudStandLesen(text)) === JSON.stringify(sich.stand),
                vorher: zaehle(JSON.stringify(sich), id), nachher: zaehle(JSON.stringify(packForm(sich)), id)};
    }""")
    print("voller Stand, %d Kennungen: alt %d Bytes, gepackt %d Bytes (%.0f %% der Grenze)"
          % (v["ids"], z["alt"], z["neu"], 100.0 * z["neu"] / GRENZE))
    assert z["gleich"] is True
    assert z["vorher"] == 2 and z["nachher"] == 1, z          # gewusst und Kartei -> nur gewusst
    assert z["neu"] < GRENZE * 0.3 and z["neu"] * 3 < z["alt"], z
    assert seite.fehler == []


# ------------------------------------------------------- alt -> neu -> alt ---

def test_alt_neu_alt_und_ein_zweites_geraet_liest_beides(seite, zweites, heute_stand):
    tag = datetime.date.today()
    _uhr(seite, tag)
    seite.starten(stand=heute_stand())
    v = seite.js(VOLL, 0)
    assert v["alt"] < GRENZE
    assert seite.js(ANMELDEN, [None, True]) is True
    dok = seite.js(DOK_HOLEN)
    assert "gewusst" in _stand(dok) and "gepackt1" not in _stand(dok)     # passt: alte Form

    # Mehr gelernt, als in die alte Form passt: am naechsten Tag gepackt.
    _uhr(seite, tag + datetime.timedelta(days=1))
    seite.js("(n) => { for(let i = 0; i < n; i++) known.add('probe:mehr-' + i); }", MEHR)
    assert seite.js("() => utf8Laenge(JSON.stringify(sicherungObjekt()))") > GRENZE
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    dok = seite.js(DOK_HOLEN)
    assert list(_stand(dok)) == ["gepackt1"] and len(dok["text"].encode("utf-8")) <= GRENZE
    assert seite.js(GEPACKT_GLEICH) is True
    assert seite.js(ZAEHLER) == {"anmelden": 1, "laden": 1, "speichern": 2, "loeschen": 0, "kennung": 1}
    assert seite.js("() => cloudMerker().fremd") == []

    # Ein zweites Geraet mit 1.4 meldet sich an und bekommt alles.
    _uhr(zweites, tag + datetime.timedelta(days=1))
    zweites.starten(stand=heute_stand())
    zweites.js("() => known.add('zweites:wort')")
    assert zweites.js(ANMELDEN, [dok, True]) is True
    soll = seite.js(WOERTER)
    assert set(soll) | {"zweites:wort"} == set(zweites.js(WOERTER))
    assert zweites.js("() => kartei.w") == seite.js("() => kartei.w")
    dok = zweites.js(DOK_HOLEN)
    assert list(_stand(dok)) == ["gepackt1"]                                  # zu gross: wieder gepackt

    # Zurueck: das erste Geraet arbeitet es ein, dann schrumpft der Stand,
    # und es schreibt wieder die alte Form.
    seite.js(DOK_LEGEN, dok)
    _uhr(seite, tag + datetime.timedelta(days=2))
    assert seite.js(ABGLEICH, "start") == "zusammengefuehrt"
    assert "zweites:wort" in seite.js(WOERTER)
    seite.js("() => { [...known].filter(w => w.startsWith('probe:mehr-')).forEach(w => known.delete(w)); }")
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    stand = _stand(seite.js(DOK_HOLEN))
    assert "gepackt1" not in stand and "zweites:wort" in stand["gewusst"]
    assert not [w for w in stand["gewusst"] if w.startswith("probe:mehr-")]
    assert stand["kartei"] == seite.js("() => kartei")
    assert seite.fehler == [] and zweites.fehler == []


# ------------------------------------------------------- erst nachsehen ---

def test_erst_nachsehen_laedt_nur_bei_fremdem_schreiben(seite, heute_stand):
    tag = datetime.date.today()
    _uhr(seite, tag)
    seite.starten(stand=heute_stand())
    seite.js("() => known.add('probe:eins')")
    assert seite.js(ANMELDEN, [None, True]) is True
    assert seite.js(ZAEHLER) == {"anmelden": 1, "laden": 1, "speichern": 1, "loeschen": 0}

    # Naechster Tag, niemand sonst hat geschrieben: nur rev.
    _uhr(seite, tag + datetime.timedelta(days=1))
    assert seite.js(ABGLEICH, "start") == "gelesen"
    assert seite.js(ZAEHLER) == {"anmelden": 1, "laden": 1, "speichern": 1, "loeschen": 0, "kennung": 1}
    seite.js("() => known.add('probe:zwei')")
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    assert seite.js(ZAEHLER)["laden"] == 1 and seite.js(ZAEHLER)["kennung"] == 2

    # Ein anderes Geraet hat geschrieben: rev, dann der ganze Stand.
    _uhr(seite, tag + datetime.timedelta(days=2))
    seite.js("""() => { const s = JSON.parse(ablage.dok.text); s.stand.gewusst.push('tablet:wort');
                        ablage.dok = {text: JSON.stringify(s), rev: 'tablet.1'}; }""")
    assert seite.js(ABGLEICH, "start") == "zusammengefuehrt"
    assert seite.js(ZAEHLER)["laden"] == 2 and seite.js(ZAEHLER)["kennung"] == 3
    assert "tablet:wort" in seite.js(WOERTER)

    # Das Dokument ist weg (etwa anderswo geloescht): nichts zu laden, neu schreiben.
    _uhr(seite, tag + datetime.timedelta(days=3))
    seite.js("() => { ablage.dok = null; known.add('probe:drei'); }")
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    z = seite.js(ZAEHLER)
    assert z["laden"] == 2 and z["kennung"] == 4 and z["speichern"] == 3, z
    assert "probe:drei" in _stand(seite.js(DOK_HOLEN))["gewusst"]
    assert seite.fehler == []


# ---------------------------------------------------- beschaedigte Daten ---

def _b64(roh):
    return base64.b64encode(roh).decode("ascii")


def _gz(roh):
    return _b64(gzip.compress(roh, 6))


def _kaputt(name, gut):
    """gut: ein echtes gepackt1 aus der App."""
    roh = bytearray(base64.b64decode(gut))
    if name == "gekippt":
        roh[len(roh) // 2] ^= 0xFF
        return _b64(bytes(roh))
    if name == "abgeschnitten":
        return _b64(bytes(roh[: len(roh) // 2]))
    form = {"f": 1, "s": {"app": "zmaj", "version": 1, "stand": {"gewusst": ["a:b"],
                                                                 "kartei": {"tag": 0, "n": 0, "w": None}}}}
    return {
        "kein_base64": "das ist kein Base64!",
        "leer": "",
        "zahl": 12345,
        "tabelle": {"x": 1},
        "kein_gzip": _b64(os.urandom(300)),
        "kein_json": _gz(b"{kaputt"),
        "kein_utf8": _gz(b"\xff\xfe{}"),
        "falsches_format": _gz(json.dumps(dict(form, f=2)).encode()),
        "kartei_zu_lang": _gz(json.dumps(dict(form, k={"i": [1, 1], "s": [0, 0], "a": [1, 1], "l": [0, 0],
                                                         "x": []})).encode()),
        "kartei_spalten_ungleich": _gz(json.dumps(dict(form, k={"i": [1], "s": [], "a": [1], "l": [0],
                                                                  "x": []})).encode()),
        "kartei_text": _gz(json.dumps(dict(form, k={"i": [1], "s": ["0"], "a": [1], "l": [0], "x": []})).encode()),
        "bombe": _gz(b"0" * (33 * 1024 * 1024)),
    }[name]


KAPUTT = ["gekippt", "abgeschnitten", "kein_base64", "leer", "zahl", "tabelle", "kein_gzip", "kein_json",
          "kein_utf8", "falsches_format", "kartei_zu_lang", "kartei_spalten_ungleich", "kartei_text", "bombe"]


@pytest.mark.parametrize("name", KAPUTT)
def test_beschaedigt_nichts_wirft_eigenes_bleibt_nichts_weggeworfen(seite, heute_stand, name):
    tag = datetime.date.today()
    _uhr(seite, tag)
    seite.starten(stand=heute_stand())
    gut = seite.js("""async () => JSON.parse(await cloudPacken(sicherungObjekt({gewusst: ['a:b'],
                         kartei: {tag: 0, n: 0, w: {'a:b': [1, 2, 1]}}}))).stand.gepackt1""")
    wert = _kaputt(name, gut)
    text = json.dumps({"app": "zmaj", "version": 1, "datum": "2026-11-13", "stand": {"gepackt1": wert}})
    # cloudStandLesen gibt den Stand mit dem unlesbaren Feld zurueck, unveraendert.
    assert seite.js(GELESEN, text) == {"gepackt1": wert}

    seite.js("() => { known.add('eigen:wort'); passed.add(CATEGORIES[0].id); }")
    assert seite.js(ANMELDEN, [{"text": text, "rev": "kaputt.1"}, True]) is True
    assert {"eigen:wort"} <= set(seite.js(WOERTER))
    assert seite.js("() => standFremd.gepackt1") == wert                  # weitergetragen, wie 1.3
    stand = _stand(seite.js(DOK_HOLEN))
    assert stand["gepackt1"] == wert and "eigen:wort" in stand["gewusst"]

    # Packt dieses Geraet spaeter selbst, ersetzt es das kaputte Feld.
    _uhr(seite, tag + datetime.timedelta(days=1))
    seite.js(VOLL, MEHR)
    seite.js("() => known.add('eigen:wort')")
    assert seite.js(ABGLEICH, "pause") == "gespeichert"
    dok = seite.js(DOK_HOLEN)
    assert list(_stand(dok)) == ["gepackt1"] and _stand(dok)["gepackt1"] != wert
    innen = seite.js(GELESEN, dok["text"])
    assert "gepackt1" not in innen and "eigen:wort" in innen["gewusst"]
    assert seite.fehler == []


# ------------------------------------------------ Probe vor dem Hochladen ---

def test_probe_falsch_oder_kein_gzip_dann_nichts_gepacktes(seite, heute_stand):
    tag = datetime.date.today()
    _uhr(seite, tag)
    seite.starten(stand=heute_stand())
    seite.js(VOLL, MEHR)
    assert seite.js(ANMELDEN, [None, True]) is True
    vorher = seite.js(DOK_HOLEN)
    assert list(_stand(vorher)) == ["gepackt1"]

    # Kaeme beim Auspacken etwas anderes heraus: kein Hochladen, die Cloud bleibt.
    seite.js("""() => { window.auspackenEcht = cloudAuspacken;
                        cloudAuspacken = async z => { const s = await window.auspackenEcht(z);
                                                      s.stand.gewusst.pop(); return s; }; }""")
    seite.js("() => known.add('probe:neu')")
    assert seite.js(ABGLEICH, "abmelden") == "zu gross"
    assert seite.js(DOK_HOLEN) == vorher
    seite.js("() => { cloudAuspacken = window.auspackenEcht; }")

    # Ohne gzip im Geraet (sehr alte WebView): die alte Form oder nichts.
    seite.js("() => { window.packenEcht = CompressionStream; window.CompressionStream = undefined; }")
    assert seite.js("() => packenMoeglich()") is False
    assert seite.js(ABGLEICH, "abmelden") == "zu gross"
    assert seite.js(DOK_HOLEN) == vorher
    seite.js("() => { window.CompressionStream = window.packenEcht; }")
    assert seite.js(ABGLEICH, "abmelden") == "gespeichert"
    assert "probe:neu" in seite.js(GELESEN, seite.js(DOK_HOLEN)["text"])["gewusst"]
    assert seite.fehler == []


# ------------------------------------------------ sehr grosser Stand ---

GROSS = """async () => {
    const echt = [...new Set(CATEGORIES.flatMap(c => c.words).map(w => w.id))];
    // Weitere Eintraege wie die echten, mit einer Zahl hinten dran - sonst
    // schriebe altenFortschrittUmschreiben() sie ueber den bosnischen Teil auf
    // die echten Woerter um.
    const ids = [];
    for(let r = 0; ids.length < 30000; r++){
      for(const id of echt){
        if(ids.length >= 30000) break;
        ids.push(r ? id + ' ' + r : id);
      }
    }
    // Zufaellige, aber feste Kartei: Stufe 0 bis 6, geuebt in den letzten 180 Tagen.
    let x = 12345;
    const zufall = () => { x = (Math.imul(x, 1103515245) + 12345) & 0x7fffffff; return x / 0x7fffffff; };
    const heute = karteiTag(), ab = [1, 3, 7, 14, 30, 90, 180];
    known = new Set(ids);
    kartei = {tag: heute, n: 12, w: {}};
    ids.forEach(id => { const s = Math.floor(zufall() * 7), l = heute - Math.floor(zufall() * Math.min(heute, 180));
                        kartei.w[id] = [s, l + ab[s], l]; });
    topf = {}; stern = {};
    ids.slice(0, TOPF_MAX).forEach((id, i) => { topf['w:' + id] = {typ: 'mcrev', n: 1, z: Date.now() - i}; });
    ids.slice(0, STERN_MAX).forEach((id, i) => { stern['w:' + id] = {z: Date.now() - i, r: Date.now()}; });
    passed = new Set(CATEGORIES.map(c => c.id));
    const sich = sicherungObjekt(), text = await cloudPacken(sich);
    return {n: known.size, alt: utf8Laenge(JSON.stringify(sich)), neu: text ? utf8Laenge(text) : null,
            gleich: !!text && JSON.stringify(await cloudStandLesen(text)) === JSON.stringify(sich.stand)};
}"""


def test_sehr_grosser_stand_30000_eintraege(seite, zweites, heute_stand):
    """Weg A sollte bis etwa 30 000 Eintraege reichen (cloud.md). Gerechnet mit
    zufaelligen Kartei-Zahlen statt lauter gleichen - die packen sich
    schlechter, das ist der ehrlichere Fall."""
    seite.starten(stand=heute_stand())
    z = seite.js(GROSS)
    print("30 000 Eintraege: alt %d Bytes, gepackt %s Bytes (%.0f %% der Grenze)"
          % (z["alt"], z["neu"], 100.0 * (z["neu"] or 0) / GRENZE))
    assert z["n"] == 30000 and z["alt"] > 3 * GRENZE
    assert z["gleich"] is True and z["neu"] <= GRENZE, z

    assert seite.js(ANMELDEN, [None, True]) is True
    dok = seite.js(DOK_HOLEN)
    assert list(_stand(dok)) == ["gepackt1"] and len(dok["text"].encode("utf-8")) <= GRENZE
    # Ein neues Geraet bekommt alle 30 000.
    zweites.starten(stand=heute_stand())
    assert zweites.js(ANMELDEN, [dok, True]) is True
    assert zweites.js(WOERTER) == seite.js(WOERTER)
    assert seite.fehler == [] and zweites.fehler == []


# ------------------------------------------ zwei Geraete, eins mit 1.3 ---

@pytest.fixture(scope="session")
def html_13():
    """web/index.html von 1.3 aus dem Git-Verlauf, mit WERBUNG_AN aus wie in der
    Demo (demo_bauen.py). Fehlt der Verlauf (flacher Klon im CI), wird
    uebersprungen."""
    import demo_bauen
    try:
        roh = subprocess.run(["git", "-C", WURZEL, "show", FASSUNG_13 + ":web/index.html"],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("1.3 (%s) ist nicht im Git-Verlauf" % FASSUNG_13)
    text = roh.decode("utf-8")
    assert text.count(demo_bauen.WERBUNG_ALT) == 1
    return text.replace(demo_bauen.WERBUNG_ALT, demo_bauen.WERBUNG_NEU).encode("utf-8")


@pytest.fixture
def geraet_13(browser, basis, html_13):
    ctx, s = _geraet(browser, basis)
    s.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=html_13))
    yield s
    ctx.close()


def _13_starten(s, heute_stand, **stand):
    s.starten(stand=heute_stand(**stand))
    assert s.js("() => [typeof cloudStandLesen, typeof cloudSpeicherAdapter]") == ["undefined", "function"]


def test_13_liest_wie_immer_solange_nicht_gepackt_wird(seite, geraet_13, heute_stand):
    neu, alt = seite, geraet_13
    neu.starten(stand=heute_stand())
    neu.js("() => { CATEGORIES[0].words.slice(0, 5).forEach(w => known.add(w.id)); passed.add(CATEGORIES[0].id); }")
    assert neu.js(ANMELDEN, [None, True]) is True
    assert "gepackt1" not in _stand(neu.js(DOK_HOLEN))

    _13_starten(alt, heute_stand)
    alt.js("() => known.add(CATEGORIES[1].words[0].id)")
    assert alt.js(ANMELDEN, [neu.js(DOK_HOLEN), False]) is True
    assert set(neu.js(WOERTER)) < set(alt.js(WOERTER))                    # 1.3 hat alles von 1.4
    neu.js(DOK_LEGEN, alt.js(DOK_HOLEN))
    assert neu.js(ABGLEICH, "anmelden") == "gespeichert"
    assert set(neu.js(WOERTER)) == set(alt.js(WOERTER))
    assert neu.fehler == [] and alt.fehler == []


def test_13_traegt_gepacktes_weiter_und_14_fuehrt_alles_zusammen(seite, geraet_13, heute_stand):
    """Was 1.3 mit einem gepackten Dokument tut (cloud_handytest.md): Es
    meldet sich an, zeigt nur seinen eigenen Stand, haelt gepackt1 fuer das
    Feld einer neueren Fassung und schreibt es unveraendert neben seinen
    Stand. Verloren geht nichts: 1.4 packt aus und fuehrt beides zusammen."""
    neu, alt = seite, geraet_13
    neu.starten(stand=heute_stand())
    neu.js(VOLL, MEHR)
    assert neu.js(ANMELDEN, [None, True]) is True
    dok = neu.js(DOK_HOLEN)
    blob = _stand(dok)["gepackt1"]
    neu_vorher = set(neu.js(WOERTER))

    _13_starten(alt, heute_stand)
    eigen = alt.js("() => CATEGORIES[2].words.slice(0, 3).map(w => w.id).concat(['nur13:wort'])")
    alt.js("(w) => w.forEach(x => known.add(x))", eigen)
    assert alt.js(ANMELDEN, [dok, False]) is True
    assert set(alt.js(WOERTER)) == set(eigen)                             # 1.3 sieht nur seins
    assert alt.js("() => standFremd.gepackt1") == blob
    assert alt.js("() => cloudMerker().fremd") == ["gepackt1"]
    stand13 = _stand(alt.js(DOK_HOLEN))
    assert stand13["gepackt1"] == blob and set(stand13["gewusst"]) == set(eigen)

    # 1.4 liest, was 1.3 geschrieben hat: alles zusammen, wieder gepackt.
    neu.js(DOK_LEGEN, alt.js(DOK_HOLEN))
    assert neu.js(ABGLEICH, "anmelden") == "gespeichert"
    assert set(neu.js(WOERTER)) == neu_vorher | set(eigen)
    assert "gepackt1" not in neu.js("() => standFremd")
    dok = neu.js(DOK_HOLEN)
    assert list(_stand(dok)) == ["gepackt1"] and _stand(dok)["gepackt1"] != blob
    innen = neu.js(GELESEN, dok["text"])
    assert set(innen["gewusst"]) == neu_vorher | set(eigen) and "gepackt1" not in innen

    # Und 1.3 nimmt das neue gepackt1 statt des alten.
    alt.js(DOK_LEGEN, dok)
    assert alt.js(ABGLEICH, "anmelden") == "gespeichert"
    assert alt.js("() => standFremd.gepackt1") == _stand(dok)["gepackt1"]
    assert set(alt.js(WOERTER)) == set(eigen)
    assert neu.fehler == [] and alt.fehler == []


def test_randfall_13_laesst_gepacktes_fallen_und_14_bringt_alles_zurueck(seite, geraet_13, heute_stand):
    """cloud.md, Risiken: Ist auch der Stand auf dem Geraet mit 1.3 schon gross,
    passen beide nicht mehr in ein Dokument. 1.3 laesst dann das fremde Feld
    gepackt1 in der Cloud weg (wie seit 28.10.2026 vorgesehen). Fuer kurze
    Zeit fehlt der Stand von 1.4 in der Cloud - auf dem Geraet mit 1.4 ist er
    aber, und beim naechsten Abgleich kommt alles wieder hinein."""
    neu, alt = seite, geraet_13
    neu.starten(stand=heute_stand())
    neu.js(VOLL, MEHR)
    assert neu.js(ANMELDEN, [None, True]) is True
    neu_vorher = set(neu.js(WOERTER))

    _13_starten(alt, heute_stand)
    alt.js(VOLL, 0)
    alt.js("() => known.add('nur13:wort')")
    alt_vorher = set(alt.js(WOERTER))
    assert alt.js(ANMELDEN, [neu.js(DOK_HOLEN), False]) is True
    stand13 = _stand(alt.js(DOK_HOLEN))
    assert "gepackt1" not in stand13 and set(stand13["gewusst"]) == alt_vorher

    neu.js(DOK_LEGEN, alt.js(DOK_HOLEN))
    assert neu.js(ABGLEICH, "anmelden") == "gespeichert"
    alles = neu_vorher | alt_vorher
    assert set(neu.js(WOERTER)) == alles
    dok = neu.js(DOK_HOLEN)
    assert list(_stand(dok)) == ["gepackt1"]
    assert set(neu.js(GELESEN, dok["text"])["gewusst"]) == alles
    assert neu.fehler == [] and alt.fehler == []


# --------------------------- Test-App "immer packen" (Handytest) ---

@pytest.fixture(scope="session")
def html_immer(wurzelordner, tmp_path_factory):
    """Die Test-App aus app_bauen.py --immer-packen: CLOUD_IMMER_PACKEN an,
    eingesetzt mit immer_packen_einschalten() wie beim Bauen."""
    import app_bauen
    kopie = tmp_path_factory.mktemp("immerpacken") / "index.html"
    shutil.copyfile(os.path.join(wurzelordner, "app", "index.html"), str(kopie))
    app_bauen.immer_packen_einschalten(str(kopie))
    html = kopie.read_bytes()
    assert html.count(app_bauen.PACKEN_AN.encode("utf-8")) == 1
    return html


@pytest.fixture
def geraet_immer(browser, basis, html_immer):
    ctx, s = _geraet(browser, basis)
    s.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=html_immer))
    yield s
    ctx.close()


def test_handytest_immer_packen_mit_13_und_14(geraet_immer, geraet_13, seite, heute_stand):
    """Der Ablauf aus cloud_handytest.md, mit drei Browsern statt Handys:
    Die Test-App packt auch einen kleinen Stand. 1.3 zeigt dann nur seinen
    eigenen und traegt gepackt1 weiter, die Test-App fuehrt beides zusammen.
    Eine 1.4 aus dem Store (Schritt 1) liest das gepackte Dokument und
    schreibt wieder die alte Form - danach sieht auch 1.3 alles."""
    immer, alt, neu = geraet_immer, geraet_13, seite
    immer.starten(stand=heute_stand())
    w_immer = immer.js("() => CATEGORIES[0].words.slice(0, 4).map(w => w.id)")
    immer.js("(w) => w.forEach(x => known.add(x))", w_immer)
    assert immer.js(ANMELDEN, [None, True]) is True
    dok = immer.js(DOK_HOLEN)
    assert list(_stand(dok)) == ["gepackt1"] and len(dok["text"]) < 20000      # klein, trotzdem gepackt

    _13_starten(alt, heute_stand)
    w_alt = alt.js("() => CATEGORIES[1].words.slice(0, 3).map(w => w.id)")
    alt.js("(w) => w.forEach(x => known.add(x))", w_alt)
    assert alt.js(ANMELDEN, [dok, False]) is True
    assert set(alt.js(WOERTER)) == set(w_alt)                               # 1.3 sieht nur seins
    stand13 = _stand(alt.js(DOK_HOLEN))
    assert stand13["gepackt1"] == _stand(dok)["gepackt1"] and set(stand13["gewusst"]) == set(w_alt)

    immer.js(DOK_LEGEN, alt.js(DOK_HOLEN))
    assert immer.js(ABGLEICH, "anmelden") == "gespeichert"
    alles = set(w_immer) | set(w_alt)
    assert set(immer.js(WOERTER)) == alles
    dok = immer.js(DOK_HOLEN)
    assert list(_stand(dok)) == ["gepackt1"]

    neu.starten(stand=heute_stand())
    assert neu.js(ANMELDEN, [dok, True]) is True
    assert set(neu.js(WOERTER)) == alles
    dok = neu.js(DOK_HOLEN)
    assert "gepackt1" not in _stand(dok) and set(_stand(dok)["gewusst"]) == alles   # passt: alte Form

    alt.js(DOK_LEGEN, dok)
    assert alt.js(ABGLEICH, "anmelden") == "gespeichert"
    assert set(alt.js(WOERTER)) == alles
    assert "gepackt1" not in alt.js("() => standFremd")                    # das alte Feld ist weg
    assert "gepackt1" not in _stand(alt.js(DOK_HOLEN))
    assert immer.fehler == [] and alt.fehler == [] and neu.fehler == []


# Nach dem Update: dieselbe Ablage wie vorher, ein frischer Adapter. Mit
# "erst nachsehen" wie Firestore - kennt das Geraet das rev, laedt es nichts.
ADAPTER_NACH_UPDATE = """(dok) => {
    window.ablage = {uid: 'konto-probe', mitKennung: true, dok};
    window.adapter = cloudSpeicherAdapter(window.ablage);
}"""


@pytest.mark.parametrize("schritt", [1, 2])
def test_update_13_auf_14_mit_mitgetragenem_gepackt1(geraet_immer, geraet_13, seite, heute_stand,
                                                     html_immer, schritt):
    """Pruefbefund 13.11.2026: X (Test-App "immer packen") schreibt gepackt1.
    Y mit 1.3 traegt es als fremdes Feld weiter und wird dann auf 1.4
    aktualisiert - Schritt 1 (die App aus dem Store) oder Schritt 2 (nur
    CLOUD_IMMER_PACKEN umgeschaltet). Danach hat niemand sonst geschrieben,
    Y laedt die Cloud also nicht (nur rev). X ist weg, ein neues Geraet Z
    meldet sich an. Vorher fehlten mit Schritt 2 die Woerter von X in der
    Cloud: Y packte ohne das mitgetragene gepackt1. Jetzt packt Y es vor dem
    Schreiben aus und arbeitet es ein - Z bekommt alles, und Y zeigt es."""
    x, y, z = geraet_immer, geraet_13, seite
    x.starten(stand=heute_stand())
    w_x = x.js("() => CATEGORIES[0].words.slice(0, 4).map(w => w.id).concat(['nurx:wort'])")
    x.js("(w) => { w.forEach(v => known.add(v)); stern['w:' + w[0]] = {z: Date.now(), r: Date.now()}; }", w_x)
    assert x.js(ANMELDEN, [None, True]) is True
    dok = x.js(DOK_HOLEN)
    assert list(_stand(dok)) == ["gepackt1"]
    blob = _stand(dok)["gepackt1"]

    _13_starten(y, heute_stand)
    w_y = y.js("() => CATEGORIES[1].words.slice(0, 3).map(w => w.id)")
    y.js("(w) => w.forEach(v => known.add(v))", w_y)
    assert y.js(ANMELDEN, [dok, False]) is True
    assert set(y.js(WOERTER)) == set(w_y)                                   # 1.3 sieht nur seins
    assert y.js("() => standFremd.gepackt1") == blob
    dok = y.js(DOK_HOLEN)
    assert _stand(dok)["gepackt1"] == blob

    # Update auf 1.4: Geraetespeicher wie vorher, neuer Code.
    y.page.unroute("**/app/index.html")
    if schritt == 2:
        y.page.route("**/app/index.html", lambda r: r.fulfill(
            status=200, content_type="text/html; charset=utf-8", body=html_immer))
    y.neu_laden()
    assert y.js("() => [typeof cloudStandLesen, CLOUD_IMMER_PACKEN]") == ["function", schritt == 2]
    assert y.js("() => standFremd.gepackt1") == blob                       # noch mitgetragen
    y.js(ADAPTER_NACH_UPDATE, dok)
    y.js("() => known.add('y:nach-update')")
    assert y.js(ABGLEICH, "pause") == "gespeichert"
    zaehler = y.js(ZAEHLER)
    assert zaehler.get("laden", 0) == 0 and zaehler["kennung"] == 1, zaehler  # die Cloud nicht gelesen

    alles = set(w_x) | set(w_y) | {"y:nach-update"}
    assert set(y.js(WOERTER)) == alles                                      # Y zeigt jetzt auch X
    assert "gepackt1" not in y.js("() => standFremd")                      # eingearbeitet
    assert "w:" + w_x[0] in y.js("() => stern")
    dok = y.js(DOK_HOLEN)
    if schritt == 1:
        assert "gepackt1" not in _stand(dok) and set(_stand(dok)["gewusst"]) == alles   # passt: alte Form
    else:
        assert list(_stand(dok)) == ["gepackt1"] and _stand(dok)["gepackt1"] != blob
        assert set(y.js(GELESEN, dok["text"])["gewusst"]) == alles

    # X ist weg. Ein neues Geraet meldet sich an und hat trotzdem alles.
    z.starten(stand=heute_stand())
    assert z.js(ANMELDEN, [dok, True]) is True
    assert set(z.js(WOERTER)) == alles
    assert "w:" + w_x[0] in z.js("() => stern")
    assert x.fehler == [] and y.fehler == [] and z.fehler == []


def test_mitgetragenes_gepackt1_kaputt_bleibt_in_der_alten_form(seite, heute_stand):
    """Laesst sich ein mitgetragenes gepackt1 nicht auspacken, bleibt es auf
    dem Geraet und in der alten Form auch in der Cloud. Weggelassen wird es
    erst, wenn das Geraet selbst packt (siehe test_beschaedigt_...)."""
    seite.starten(stand=heute_stand(gepackt1="das ist kein Base64!", gewusst=["eigen:wort"]))
    assert seite.js("() => standFremd.gepackt1") == "das ist kein Base64!"
    assert seite.js(ANMELDEN, [None, True]) is True
    stand = _stand(seite.js(DOK_HOLEN))
    assert stand["gepackt1"] == "das ist kein Base64!" and "eigen:wort" in stand["gewusst"]
    assert seite.js("() => standFremd.gepackt1") == "das ist kein Base64!"
    assert seite.fehler == []


# ------------------------------------------------ Firestore, Attrappe ---

def test_firestore_gepackt_nach_den_regeln_und_mit_feldmaske(seite, heute_stand, cloud_html):
    attrappe = Attrappe()
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=cloud_html))
    for host in FIREBASE:
        seite.page.route("https://%s/**" % host, attrappe)
    tag = datetime.date.today()
    _uhr(seite, tag)
    seite.starten(stand=heute_stand())
    seite.js(VOLL, MEHR)
    assert seite.js("async () => await cloudAnmelden('anonym')") is True
    # firestore.rules, gueltig(): genau daten und rev, daten ein Text bis 900 000 Zeichen.
    assert set(attrappe.dok) == {"daten", "rev"}
    daten, rev = attrappe.dok["daten"]["stringValue"], attrappe.dok["rev"]["stringValue"]
    assert len(daten) <= GRENZE and len(daten.encode("utf-8")) <= GRENZE and len(rev) <= 100
    assert list(json.loads(daten)["stand"]) == ["gepackt1"]
    assert attrappe.masken == [None]

    # Naechster Tag: zuerst nur rev; ein anderes Geraet hat geschrieben, also
    # danach das ganze Dokument.
    _uhr(seite, tag + datetime.timedelta(days=1))
    attrappe.dok = dict(attrappe.dok, rev={"stringValue": "anderes.1"})
    seite.js("() => { const m = cloudMerker(); m.gelesen = ''; localStorage.setItem('zmaj_cloud', JSON.stringify(m)); }")
    assert seite.js("async () => await cloudAbgleich('start')") == "zusammengefuehrt"
    assert attrappe.masken[-2:] == [["rev"], None]

    # Nimmt Firestore die Feldmaske nicht an, laedt die App wie bisher alles,
    # statt jeden Abgleich daran scheitern zu lassen. Das Zusammenfuehren von
    # gestern hat den Stand hier veraendert (sortiert), und heute wurde noch
    # nicht geschrieben: Seit 17.11.2026 schreibt der Start ihn gleich mit.
    _uhr(seite, tag + datetime.timedelta(days=2))
    attrappe.maske_abgelehnt = True
    attrappe.dok = dict(attrappe.dok, rev={"stringValue": "anderes.2"})
    n = len(attrappe.masken)
    assert seite.js("async () => await cloudAbgleich('start')") == "gespeichert"
    assert attrappe.masken[n:] == [["rev"], None]
    assert attrappe.dok["rev"]["stringValue"] == seite.js("() => cloudMerker().rev") != "anderes.2"
    # Am naechsten Tag beim Verlassen: gleich der ganze Stand, ohne die
    # abgelehnte Feldmaske noch einmal zu versuchen (cloudMaskeKaputt).
    _uhr(seite, tag + datetime.timedelta(days=3))
    seite.js("() => known.add('probe:nach-maske')")
    assert seite.js("async () => await cloudAbgleich('pause')") == "gespeichert"
    assert attrappe.masken[n + 2:] == [None]
    assert "probe:nach-maske" in seite.js(GELESEN, attrappe.dok["daten"]["stringValue"])["gewusst"]
    assert seite.fehler == []
