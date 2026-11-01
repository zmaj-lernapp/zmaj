# -*- coding: utf-8 -*-
"""Weitermachen-Knopf: dort weiter, wo man zuletzt aufgehoert hat (01.11.2026).

Ajdin am 01.11.2026: "kann dieser weiter machen button in der app nicht da
weiter machen wo man am weitesten ist sondern da wo man als letztes
aufgehoert hat". Geprueft wird im echten Browser:
  - neuer Nutzer und alter Stand ohne das Feld letzte_lektion: wie bisher,
    das erste offene Level (firstOpen);
  - ein aelteres, noch offenes Level ueben (nach der Einstufung): der Knopf
    zeigt dieses Level, auch nach dem Neuladen und nach einer abgebrochenen
    Lektion - gespeichert schon beim Beginnen;
  - ist das Level bestanden: das naechste nicht bestandene danach, gibt es
    keins, wie bisher;
  - Level-Test, Wiederholen-Runden, Geschichten aendern nichts, die
    Einstufung loescht ein vorher gemerktes Level;
  - kaputte, fremde und gesperrte Eintraege, Sicherungsdatei, Cloud.
Die Pruefungen ohne Browser stehen in tests/test_weitermachen.py.
"""
import datetime
import json
import time

KNOPF = """() => { homeMode = 'words'; showHome(); const k = document.getElementById('weiterKnopf');
  return k.style.display === 'none' ? null : k.textContent; }"""
LEVEL = "() => CATEGORIES.map(c => c.id)"
NAME = "(i) => '▶ ' + t('btn.weitermachen') + ' · ' + CATEGORIES[i].label"
GESPEICHERT = "() => JSON.parse(localStorage.getItem('zmaj_stand')).letzte_lektion"


def _ids(seite, heute_stand):
    seite.starten(stand=heute_stand())
    return seite.js(LEVEL)


def _eingestuft(ids, ab=10, **mehr):
    """Ein Stand nach der Einstufung: Level 1 bis ab+1 offen, nicht bestanden."""
    s = {"einstufung": {"tag": datetime.date.today().isoformat(), "wahl": "gut", "bis": ids[ab]}}
    s.update(mehr)
    return s


def _knopf_zeigt(seite, i):
    assert seite.js(KNOPF) == seite.js(NAME, i), (seite.js(KNOPF), i)


def _jetzt_ms():
    return int(time.time() * 1000)


# ---------------------------------------------------------------------------
# Ohne gemerktes Level: wie bisher
# ---------------------------------------------------------------------------

def test_neuer_nutzer_und_alter_stand_wie_bisher(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    assert seite.js("() => [weiterZiel(), firstOpen(), letzteLektion]") == [0, 0, None]
    _knopf_zeigt(seite, 0)
    # Gespeichert wird das Feld leer - eine alte App liest es nicht, eine neue nimmt "wie bisher"
    seite.js("async () => await saveProgress()")
    assert "letzte_lektion" in seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand'))")
    assert seite.js(GESPEICHERT) is None
    # Alter Stand ohne das Feld, fuenf Level bestanden: das sechste
    seite.starten(stand=heute_stand(bestanden=ids[:5]))
    assert seite.js("() => letzteLektion") is None
    _knopf_zeigt(seite, 5)
    # Nach der Einstufung: das erste offene ab dem Einstieg
    seite.starten(stand=_eingestuft(ids, bestanden=[ids[10], ids[11]]))
    _knopf_zeigt(seite, 12)
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Ein aelteres Level ueben
# ---------------------------------------------------------------------------

def test_altes_level_ueben_knopf_zeigt_dieses_level(seite, heute_stand):
    """Nach der Einstufung auf Level 11 und zwei bestandenen Leveln zeigt
    der Knopf auf Level 13. Wer dann Level 4 uebt, kommt mit dem Knopf
    dorthin zurueck - nicht mehr nach vorn."""
    ids = _ids(seite, heute_stand)
    seite.starten(stand=_eingestuft(ids, bestanden=[ids[10], ids[11]]))
    _knopf_zeigt(seite, 12)
    seite.js("() => openLevel(3)")
    vorher = _jetzt_ms()
    seite.page.click("#btnLesson")
    seite.durchspielen("lBody", "Lx")
    assert seite.js("() => !!document.getElementById('lMore')"), "kein Ergebnisschirm"
    g = seite.js(GESPEICHERT)
    assert g["level"] == ids[3] and vorher <= g["z"] <= _jetzt_ms()
    seite.page.click("#lPfad")
    assert seite.js("() => document.getElementById('weiterKnopf').textContent") == seite.js(NAME, 3)
    # Der Knopf oeffnet das Level
    seite.page.click("#weiterKnopf")
    assert seite.js("() => [catIdx, sichtbar('levelView'), sichtbar('levelHome')]") == [3, True, True]
    # Auch nach dem Neuladen
    seite.neu_laden()
    _knopf_zeigt(seite, 3)
    # Im Lernpfad bleibt "jetzt dran" und die Farbe beim ersten offenen Level
    assert seite.js("() => firstOpen()") == 12
    assert seite.fehler == []


def test_abgebrochene_lektion_zaehlt_schon_beim_beginnen(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    seite.starten(stand=_eingestuft(ids))
    _knopf_zeigt(seite, 10)
    seite.js("() => openLevel(4)")
    seite.page.click("#btnLesson")
    # Gespeichert, ohne dass die App in den Hintergrund ging
    assert seite.js(GESPEICHERT)["level"] == ids[4]
    # App mitten in der Lektion zu und wieder auf
    seite.neu_laden()
    _knopf_zeigt(seite, 4)
    # Eine neuere Lektion in einem anderen Level gewinnt - auch ein spaeteres
    seite.js("() => { openLevel(7); startLesson(); lektionVerlassen(); }")
    _knopf_zeigt(seite, 7)
    seite.js("() => { openLevel(2); startLesson(); lektionVerlassen(); }")
    _knopf_zeigt(seite, 2)
    assert seite.fehler == []


def test_ohne_leben_merkt_nichts(seite, heute_stand):
    """Ohne Leben startet keine Lektion - dann bleibt auch das Level, wo es war."""
    ids = _ids(seite, heute_stand)
    seite.starten(stand=_eingestuft(ids, leben={"anzahl": 0, "zeit": 4102444800000},
                                    letzte_lektion={"level": ids[2], "z": 1000}))
    seite.js("() => { openLevel(5); startLesson(); }")
    assert seite.js("() => letzteLektion") == {"level": ids[2], "z": 1000}
    _knopf_zeigt(seite, 2)
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Bestandenes Level
# ---------------------------------------------------------------------------

def test_fertiges_level_fuehrt_zum_naechsten_offenen(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    # Level 4 und 5 bestanden, zuletzt in Level 4: das naechste offene danach ist 6, nicht 13
    seite.starten(stand=_eingestuft(ids, bestanden=[ids[3], ids[4], ids[10], ids[11]],
                                    letzte_lektion={"level": ids[3], "z": _jetzt_ms() - 60000}))
    _knopf_zeigt(seite, 5)
    # Alles danach bestanden: wie bisher - das erste offene ab dem Einstieg, sonst das erste
    seite.starten(stand=_eingestuft(ids, bestanden=ids[3:],
                                    letzte_lektion={"level": ids[3], "z": _jetzt_ms() - 60000}))
    assert seite.js("() => [weiterZiel(), firstOpen()]") == [0, 0]
    _knopf_zeigt(seite, 0)
    # Das letzte Level im Lernpfad, alles bestanden: wie bisher das letzte
    seite.starten(stand=heute_stand(bestanden=ids, letzte_lektion={"level": ids[5], "z": 1}))
    assert seite.js("() => [weiterZiel(), firstOpen()]") == [len(ids) - 1] * 2
    assert seite.fehler == []


def test_lektion_dann_test_bestanden_naechstes_level(seite, heute_stand):
    """Der echte Weg: eine Lektion in Level 4 (nach der Einstufung offen),
    dann den Level-Test bestehen. Der Test aendert das gemerkte Level nicht -
    aber es ist jetzt bestanden, also zeigt der Knopf auf Level 5."""
    ids = _ids(seite, heute_stand)
    woerter = seite.js("() => CATEGORIES[3].words.map(w => w.id)")
    seite.starten(stand=_eingestuft(ids, gewusst=woerter, bestanden=[ids[10]]))
    seite.js("() => openLevel(3)")
    seite.page.click("#btnLesson")
    seite.durchspielen("lBody", "Lx")
    seite.page.click("#lHome")
    gemerkt = seite.js("() => letzteLektion")
    assert gemerkt["level"] == ids[3]
    _knopf_zeigt(seite, 3)                         # noch nicht bestanden: dorthin
    seite.js("() => openLevel(3)")
    seite.page.click("#btnTest")
    seite.durchspielen("tBody", "Tx")
    assert seite.js("(id) => passed.has(id)", ids[3])
    assert seite.js("() => letzteLektion") == gemerkt, "der Test merkt sich nichts"
    seite.page.click("#tBack")
    assert seite.js("() => document.getElementById('weiterKnopf').textContent") == seite.js(NAME, 4)
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Was nichts aendert - und die Einstufung
# ---------------------------------------------------------------------------

def test_test_runden_geschichten_aendern_nichts(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    woerter = seite.js("() => CATEGORIES[5].words.map(w => w.id)")
    gemerkt = {"level": ids[2], "z": _jetzt_ms() - 60000}
    seite.starten(stand=_eingestuft(ids, gewusst=woerter, letzte_lektion=gemerkt))
    # Level-Test begonnen und abgebrochen
    seite.js("() => { openLevel(5); startTest(); showLevelHome(); }")
    assert seite.js("() => letzteLektion") == gemerkt
    # Runde aus dem Fehler-Topf und Markiert-Runde, ganz durchgespielt
    seite.js("""(ws) => { topf = {}; stern = {};
        ws.slice(0, 3).forEach((id, i) => { topf['w:' + id] = {typ: 'mc', n: 0, z: 1000 + i}; });
        ws.slice(3, 6).forEach((id, i) => { stern['w:' + id] = {z: 2000 + i, r: 0}; });
        startTopf(); }""", woerter)
    assert seite.js("() => Lx.quelle") == "topf"
    seite.durchspielen("lBody", "Lx")
    seite.js("() => startStern()")
    assert seite.js("() => Lx.quelle") == "stern"
    seite.durchspielen("lBody", "Lx")
    assert seite.js("() => letzteLektion") == gemerkt
    # Geschichte geoeffnet
    seite.js("() => openStory(0)")
    assert seite.js("() => letzteLektion") == gemerkt
    _knopf_zeigt(seite, 2)
    assert seite.js(GESPEICHERT) == gemerkt
    assert seite.fehler == []


def test_einstufung_loescht_ein_gemerktes_level(seite, heute_stand):
    """Die Einstufung kommt nur, solange nichts gelernt ist. Eine vorher
    angefangene und abgebrochene Lektion in Level 1 soll den neuen Einstieg
    nicht ueberstimmen."""
    ids = _ids(seite, heute_stand)
    seite.js("() => { openLevel(0); startLesson(); lektionVerlassen(); }")
    assert seite.js("() => letzteLektion.level") == ids[0]
    seite.js("(bis) => einstufungMerken('gut', bis, 12, 15)", ids[20])
    assert seite.js("() => letzteLektion") is None and seite.js(GESPEICHERT) is None
    _knopf_zeigt(seite, 20)
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Kaputt, fremd, gesperrt
# ---------------------------------------------------------------------------

def test_kaputte_fremde_und_gesperrte_eintraege(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    jetzt = _jetzt_ms()
    z = seite.js("""() => [
        letzteLektionPruefen(null), letzteLektionPruefen('x'), letzteLektionPruefen([1]),
        letzteLektionPruefen({level: 5}), letzteLektionPruefen({level: ''}),
        letzteLektionPruefen({level: 'a'.repeat(201)}), letzteLektionPruefen({z: 5}),
        letzteLektionPruefen({level: 'a'.repeat(200), z: 'x'}),
        letzteLektionPruefen({level: 'b', z: -1}), letzteLektionPruefen({level: 'b', z: 1e999}),
        letzteLektionPruefen({level: 'b', z: 7, mehr: 1}),
        letzteLektionPruefen({level: 'b', z: Date.now() + 1e9}).z <= Date.now()]""")
    assert z[:7] == [None] * 7, z
    assert z[7] == {"level": "a" * 200, "z": 0}
    assert z[8] == {"level": "b", "z": 0} and z[9] == {"level": "b", "z": 0}   # 1e999 ist kein JSON
    assert z[10] == {"level": "b", "z": 7}                                     # nur die zwei Angaben
    assert z[11] is True, "nichts aus der Zukunft"
    # Ein Level, das es nicht mehr gibt: wie bisher
    seite.starten(stand=heute_stand(bestanden=ids[:2], letzte_lektion={"level": "gibt-es-nicht", "z": jetzt}))
    _knopf_zeigt(seite, 2)
    assert seite.js("() => letzteLektion.level") == "gibt-es-nicht", "der Eintrag schadet nicht und bleibt"
    # Ein gesperrtes Level (ohne Einstufung, nichts bestanden): wie bisher
    seite.starten(stand=heute_stand(letzte_lektion={"level": ids[50], "z": jetzt}))
    _knopf_zeigt(seite, 0)
    # Kaputtes im Geraetespeicher: die App startet, der Knopf wie bisher
    for kaputt in ("x", [1, 2], {"level": 7, "z": 1}, None):
        seite.starten(stand=heute_stand(bestanden=ids[:1], letzte_lektion=kaputt))
        assert seite.js("() => letzteLektion") is None
        _knopf_zeigt(seite, 1)
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Sicherungsdatei und Cloud
# ---------------------------------------------------------------------------

EINLESEN = """async (text) => {
  frage = async () => true;
  await sicherungEinlesen(new File([text], 'sicherung.json', {type: 'application/json'}));
  return letzteLektion;
}"""


def test_sicherungsdatei_nimmt_das_level_mit(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    gemerkt = {"level": ids[4], "z": _jetzt_ms() - 5000}
    seite.starten(stand=_eingestuft(ids, letzte_lektion=gemerkt))
    datei = json.loads(seite.js("() => sicherungInhalt()"))
    assert datei["version"] == 1 and datei["stand"]["letzte_lektion"] == gemerkt
    seite.js("() => standLeeren()")
    assert seite.js("() => letzteLektion") is None
    assert seite.js(EINLESEN, json.dumps(datei)) == gemerkt
    assert seite.js(GESPEICHERT) == gemerkt
    _knopf_zeigt(seite, 4)
    # Eine alte Datei ohne das Feld: wie bisher
    alt = {"app": "zmaj", "version": 1, "stand": {"bestanden": ids[:3], "tage": [datetime.date.today().isoformat()]}}
    assert seite.js(EINLESEN, json.dumps(alt)) is None
    _knopf_zeigt(seite, 3)
    # Eine kaputte: faellt still weg, der Rest kommt an
    kaputt = {"app": "zmaj", "version": 1, "stand": {"bestanden": ids[:2], "letzte_lektion": {"level": ["x"]}}}
    assert seite.js(EINLESEN, json.dumps(kaputt)) is None
    _knopf_zeigt(seite, 2)
    assert seite.fehler == []


MISCHEN = "([a, b]) => standZusammenfuehren(a, b).letzte_lektion"


def test_cloud_das_neuere_gewinnt(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    alt, neu = {"level": ids[3], "z": 1000}, {"level": ids[8], "z": 2000}
    for a, b in ((alt, neu), (neu, alt)):
        assert seite.js(MISCHEN, [{"letzte_lektion": a}, {"letzte_lektion": b}]) == neu
    # Gleicher Zeitpunkt: der kleinere Text, in beiden Richtungen gleich
    x, y = {"level": "b-level", "z": 5}, {"level": "a-level", "z": 5}
    assert seite.js(MISCHEN, [{"letzte_lektion": x}, {"letzte_lektion": y}]) == y
    assert seite.js(MISCHEN, [{"letzte_lektion": y}, {"letzte_lektion": x}]) == y
    # Auf einer Seite fehlt es oder ist kaputt: die andere
    for leer in ({}, {"letzte_lektion": None}, {"letzte_lektion": "kaputt"}):
        assert seite.js(MISCHEN, [leer, {"letzte_lektion": alt}]) == alt
        assert seite.js(MISCHEN, [{"letzte_lektion": alt}, leer]) == alt
    assert seite.js(MISCHEN, [{}, {}]) is None
    assert seite.fehler == []


def test_cloud_abgleich_mit_dem_tablet(seite, heute_stand):
    """Ueber den Speicher-Adapter, mit gestellter Uhr wie in test_kartei.py:
    gelesen wird hoechstens einmal am Tag. Am naechsten Tag hat das Tablet
    zuletzt geuebt - der Knopf zeigt dessen Level."""
    tag1 = datetime.date.today()
    seite.page.clock.set_fixed_time(datetime.datetime.combine(tag1, datetime.time(10, 0)))
    ids = _ids(seite, heute_stand)
    jetzt = seite.js("() => Date.now()")
    seite.starten(stand=_eingestuft(ids, letzte_lektion={"level": ids[3], "z": jetzt - 60000}))
    seite.js("() => { window.ablage = {}; window.adapter = cloudSpeicherAdapter(window.ablage); }")
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    oben = json.loads(seite.js("() => ablage.dok.text"))["stand"]["letzte_lektion"]
    assert oben == {"level": ids[3], "z": jetzt - 60000}
    seite.page.clock.set_fixed_time(datetime.datetime.combine(tag1 + datetime.timedelta(days=1),
                                                              datetime.time(10, 0)))
    morgen = seite.js("() => Date.now()")
    seite.js("""(neu) => { const s = JSON.parse(ablage.dok.text); s.stand.letzte_lektion = neu;
        ablage.dok = {text: JSON.stringify(s), rev: 'tablet.1'}; }""", {"level": ids[6], "z": morgen - 1000})
    assert seite.js("async () => await cloudAbgleich('start', adapter)") == "zusammengefuehrt"
    assert seite.js("() => letzteLektion") == {"level": ids[6], "z": morgen - 1000}
    _knopf_zeigt(seite, 6)
    # Danach eine Lektion hier: die ist neuer und geht beim naechsten Hochladen hinauf
    seite.js("() => { openLevel(2); startLesson(); lektionVerlassen(); }")
    assert seite.js("async () => await cloudAbgleich('pause', adapter)") == "gespeichert"
    assert json.loads(seite.js("() => ablage.dok.text"))["stand"]["letzte_lektion"]["level"] == ids[2]
    assert seite.fehler == []
