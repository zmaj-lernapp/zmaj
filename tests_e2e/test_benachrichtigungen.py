# -*- coding: utf-8 -*-
"""Benachrichtigungen mit Persoenlichkeit (Version 1.4, Ajdin am 13.11.2026:
11a 12a 13a, Vorlage benachrichtigungen.md), in der echten App.

Am 14.11.2026 hat Ajdin A1, B4 (mit der Wortliste) und die Wortwitze D1-D6
gestrichen; sie kommen nie. benPlan() rechnet ohne Plugin, was die
naechsten Abende bringen - das pruefen die Lagen hier direkt:
  - Serie in Gefahr (20 Uhr): A2-A5, Einzahl bei 1 Tag, A4 erst ab 2,
    A6 vor einer Wegmarke, ab 7 Tagen auch C1 und (Serie = Rekord) C3;
  - gestern gelernt, keine Warnung faellig (Schutz da oder Schalter aus):
    C um 19 Uhr, C5 mit der Flammenfarbe am Tag nach 30/100/365;
  - 2 bis 6 Tage Pause: B1, B2, B3, B5, mit Tagen und Level gefuellt;
  - laenger weg (7 und mehr Tage): B1, B2, B5 und C4; nie gelernt: B2 und
    C4 im Wechsel;
  - nach 14 Tagen B6 mit den Woertern, abgerundet auf 100;
  - die Schalter wie bisher, hoechstens eine Nachricht am Abend.
Dazu die Auswahl: nie derselbe Text zwei Abende hintereinander - ueber
drei Wochen mit einem nachgebauten Plugin (Planen, Zustellen, Merken), und
reihum, sodass jeder Text einer Gruppe drankommt. Zuletzt alle acht
Sprachen: jeder Text fertig gefuellt, ohne Luecke.

Die Uhr steht fest (10.11.2026, 12 Uhr), damit alle Abende noch kommen.
"""
import datetime

import pytest

JETZT = datetime.datetime(2026, 11, 10, 12, 0)
HEUTE = JETZT.date()
SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
A = {"a2", "a3", "a4", "a5"}
C_19 = {"c2", "c3", "c4", "c6"}
B = {"b1", "b2", "b3", "b5"}
# 7 und mehr Tage Pause (bis 14.11.2026 die Wortwitze); ohne Lerntag nur B2/C4
LANGE = {"b1", "b2", "b5", "c4"}
# Am 14.11.2026 von Ajdin gestrichen: kommen nie
GESTRICHEN = {"a1", "b4", "d1", "d2", "d3", "d4", "d5", "d6"}
ALLE_WEGMARKEN = ["tage7", "tage30", "tage100", "tage365", "tage1000"]


def _tage(von, bis):
    """Lerntage von HEUTE aus gezaehlt: 0 = heute, 1 = gestern; bis exklusiv."""
    return [(HEUTE - datetime.timedelta(days=i)).isoformat() for i in range(von, bis)]


def _iso(d):
    return (HEUTE + datetime.timedelta(days=d)).isoformat()


# Setzt den Stand in der laufenden App und gibt benPlan() zurueck - dazu die
# Werte und die Gruppe des ersten Abends.
LAGE = """(l) => {
  days = new Set(l.tage); frost = new Set(l.frost || []);
  schutz = {anzahl: l.schutz || 0, zeit: (l.schutz || 0) >= SCHUTZ_MAX ? 0
            : Date.now() - (l.schutzNachIn !== undefined ? SCHUTZ_MS - l.schutzNachIn : 0)};
  gefeiert = new Set(l.gefeiert || []);
  passed = new Set(l.alleBestanden ? CATEGORIES.map(c => c.id) : []);
  const ids = [];
  const alle = CATEGORIES.flatMap(c => c.words);
  for(const w of alle){ if(new Set(ids).size >= (l.anzahl || 0)) break; ids.push(w.id); }
  known = new Set(ids);
  rekord = l.rekord !== undefined ? l.rekord : streak();
  localStorage.setItem('zmaj_benachrichtigung', JSON.stringify(Object.assign(
    {gefragt: true, erinnerung: true, serie: true, leben: false}, l.schalter || {}, {texte: l.texte || {}})));
  const plan = benPlan().map(p => ({key: p.key, art: p.art, tag: dayKey(p.wann), stunde: p.wann.getHours(),
                                    titel: p.titel, text: p.text}));
  let basis = ''; days.forEach(k => { if(k > basis) basis = k; });
  const w = benWerte(today(), basis);
  const g = benGruppe(days.has(today()) || !(streak() > 0) || schutzNow() > 0 ? 'erinnerung' : 'serie', w);
  const fuell = {};
  Object.keys(BEN_TEXTE).forEach(k => { fuell[k] = benTexte(k, w); });
  // Der Abend morgen um 19 Uhr, wenn bis dahin nicht gelernt wird
  const wMorgen = benWerte(tagMinus(today(), -1), basis);
  return {plan, w, g, fuell, n: streak(), woerter: ohneZa(known),
          level: (CATEGORIES[firstOpen()] || {}).label,
          wMorgen, gMorgen: benGruppe('erinnerung', wMorgen)};
}"""


@pytest.fixture
def app(seite):
    seite.page.clock.set_fixed_time(JETZT)
    seite.starten(stand={"einstufung": {"tag": HEUTE.isoformat(), "wahl": "neu", "bis": ""}})
    return seite


def _lage(app, **l):
    l.setdefault("gefeiert", ALLE_WEGMARKEN)
    return app.js(LAGE, l)


def _abende(r):
    return [p for p in r["plan"] if p["art"] in ("serie", "erinnerung")]


def _ohne_wiederholung(abende):
    keys = [p["key"] for p in abende]
    assert all(a != b for a, b in zip(keys, keys[1:])), keys
    assert not GESTRICHEN & set(keys), keys


# ---------------------------------------------------------------------------
# Serie in Gefahr
# ---------------------------------------------------------------------------

def test_serie_in_gefahr_um_20_uhr(app):
    """Serie 3, heute noch nichts, kein Schutz: heute um 20 Uhr ein Text aus
    A, mit der Zahl. Die Abende danach: 2 bis 6 Tage Pause -> B um 19 Uhr,
    am siebten (7 Tage Pause) B1, B2, B5 oder C4. Eine Nachricht je Abend,
    keine zweimal hintereinander."""
    r = _lage(app, tage=_tage(1, 4))
    abende = _abende(r)
    assert [p["tag"] for p in abende] == [_iso(d) for d in range(7)]
    erst = abende[0]
    assert erst["art"] == "serie" and erst["stunde"] == 20 and erst["key"] in A, erst
    assert "3 Tage" in erst["titel"] + erst["text"], erst
    assert all(p["stunde"] == 19 and p["art"] == "erinnerung" for p in abende[1:])
    assert all(p["key"] in B for p in abende[1:6]), abende
    assert abende[6]["key"] in LANGE, abende[6]
    _ohne_wiederholung(abende)
    assert r["fuell"]["a4"][1] == "3 Tage am Stück. Zeig der Serie, wer hier stur ist."
    assert app.fehler == []


def test_ein_tag_einzahl_und_ohne_a4(app):
    r = _lage(app, tage=_tage(1, 2))
    assert r["n"] == 1
    assert r["g"] == {"vorrang": [], "pool": ["a2", "a3", "a5"]}
    assert r["fuell"]["a2"][0] == "Pazi! 🔥 1 Tag"
    assert r["fuell"]["a3"][0] == "🔥 1 Tag"
    assert _abende(r)[0]["key"] in {"a2", "a3", "a5"}


def test_wegmarke_hat_vorrang(app):
    """Sechs Lerntage, Serie laeuft: die naechste Lektion macht Tag 7 voll."""
    r = _lage(app, tage=_tage(1, 7), gefeiert=[])
    erst = _abende(r)[0]
    assert erst["key"] == "a6" and erst["stunde"] == 20
    assert erst["titel"] == "Heute wird's Tag 7 🔥"
    assert erst["text"] == "Eine Lektion fehlt. Zmaj hält das Konfetti schon bereit."
    # Schon gefeiert: dann wie sonst
    r = _lage(app, tage=_tage(1, 7), gefeiert=["tage7"])
    assert _abende(r)[0]["key"] in A


def test_ab_sieben_tagen_auch_lob(app):
    r = _lage(app, tage=_tage(1, 11), rekord=10)
    assert r["g"]["pool"] == ["a2", "a3", "a4", "a5", "c1", "c3"]
    assert r["fuell"]["c1"][0] == "Svaka čast! 🔥 10 Tage"
    assert r["fuell"]["c3"][1] == "Rekord: 10 Tage am Stück. Zmaj verbeugt sich. Ein bisschen."
    r = _lage(app, tage=_tage(1, 11), rekord=25)          # Rekord liegt hoeher: kein C3
    assert r["g"]["pool"] == ["a2", "a3", "a4", "a5", "c1"]


# ---------------------------------------------------------------------------
# Gestern gelernt, keine Warnung faellig
# ---------------------------------------------------------------------------

def test_gestern_gelernt_mit_schutz_lob(app):
    """Seit 14.11.2026 ohne die Wortwitze: nur noch Lob."""
    r = _lage(app, tage=_tage(1, 13), schutz=1, rekord=12, anzahl=250)
    erst = _abende(r)[0]
    assert erst["art"] == "erinnerung" and erst["stunde"] == 19
    assert r["g"] == {"vorrang": [], "pool": ["c2", "c3", "c4", "c6"]}
    assert erst["key"] in C_19, erst
    assert r["woerter"] == 250
    assert r["fuell"]["c2"][0] == "Schon 200 Wörter! 🐉"
    # Unter 100 Woertern kein C2, Rekord hoeher: kein C3 - bleiben zwei im Wechsel
    r = _lage(app, tage=_tage(1, 13), schutz=1, rekord=40, anzahl=60)
    assert r["g"]["pool"] == ["c4", "c6"]


def test_serie_aus_dann_lob_statt_warnung(app):
    """Schalter "Serie in Gefahr" aus: die Erinnerung um 19 Uhr bleibt, mit
    Lob statt der Warnung."""
    r = _lage(app, tage=_tage(1, 5), schalter={"serie": False})
    erst = _abende(r)[0]
    assert erst["art"] == "erinnerung" and erst["stunde"] == 19 and erst["key"] in C_19


@pytest.mark.parametrize("n,farbe", [(30, "blau"), (100, "lila"), (365, "golden")])
def test_am_tag_nach_30_100_365_die_flammenfarbe(app, n, farbe):
    r = _lage(app, tage=_tage(1, n + 1), schutz=1)
    erst = _abende(r)[0]
    assert erst["key"] == "c5", erst
    assert erst["titel"] == "%d Tage! 🔥" % n
    assert erst["text"] == "Deine Flamme ist jetzt %s. Zmaj hat sich extra schick gemacht." % farbe


# ---------------------------------------------------------------------------
# Pause
# ---------------------------------------------------------------------------

def test_pause_drei_tage_comeback(app):
    """Zuletzt vor drei Tagen gelernt, kein Schutz: Serie gerissen. Alle
    vier B-Texte kommen in Frage und sind fertig gefuellt; B4 ist seit dem
    14.11.2026 weg, ein Wort steht nicht mehr in den Werten."""
    r = _lage(app, tage=_tage(3, 10))
    erst = _abende(r)[0]
    assert erst["art"] == "erinnerung" and erst["stunde"] == 19 and erst["key"] in B
    assert r["w"]["pause"] == 3 and r["w"]["gerissen"] is True and "wort" not in r["w"]
    assert r["g"] == {"vorrang": [], "pool": ["b1", "b2", "b3", "b5"]}
    f = r["fuell"]
    assert sorted(f) == sorted(["a2", "a3", "a4", "a5", "a6", "b1", "b2", "b3", "b5", "b6",
                                "c1", "c2", "c3", "c4", "c5", "c6"])
    assert f["b1"] == ["Šta ima? 🐉", "3 Tage Funkstille. Zmaj hat deine Wörter abgestaubt."]
    assert f["b5"] == ["Dein Platz ist noch frei 🐉", "„%s“ wartet genau da, wo du aufgehört hast." % r["level"]]
    assert r["level"]


def test_pause_ohne_level_ohne_riss(app):
    """Alles bestanden: kein B5. Zwei Tage Pause, aber der Schutz hat gestern
    gerettet und noch einer liegt bereit: kein B3 - und die Warnung
    entfaellt, der Schutz ist ja da. Bleiben B1 und B2 im Wechsel."""
    tage = _tage(2, 9)
    r = _lage(app, tage=tage, frost=[_tage(1, 2)[0]], schutz=1, alleBestanden=True, anzahl=30)
    assert r["w"]["pause"] == 2 and r["w"]["gerissen"] is False
    assert r["g"]["pool"] == ["b1", "b2"]


def test_nachwachsender_schutz_kein_b3(app):
    """Serie 5 bis gestern, kein Schutz, der naechste waechst in 12 Stunden
    nach (heute um Mitternacht). Heute um 20 Uhr kommt die Warnung, der
    Schutz kommt erst danach. Morgen rettet er die Serie beim Oeffnen -
    also am Abend kein B3 "Serie weg?". Gefunden in der Pruefung am
    13.11.2026; vorher zaehlte nur der Schutz von jetzt."""
    stunde = 3600 * 1000
    # Waechst er erst morgen nach 19 Uhr nach, ist die Serie zur Nachricht weg
    r = _lage(app, tage=_tage(1, 6), schutzNachIn=33 * stunde)
    assert r["wMorgen"]["pause"] == 2 and r["wMorgen"]["gerissen"] is True
    assert "b3" in r["gMorgen"]["pool"]
    r = _lage(app, tage=_tage(1, 6), schutzNachIn=12 * stunde)
    abende = _abende(r)
    assert abende[0]["art"] == "serie" and abende[0]["stunde"] == 20 and abende[0]["tag"] == _iso(0)
    assert r["wMorgen"]["pause"] == 2 and r["wMorgen"]["gerissen"] is False
    assert "b3" not in r["gMorgen"]["pool"]
    assert abende[1]["tag"] == _iso(1) and abende[1]["key"] in B - {"b3"}, abende[1]
    # Gegenprobe: morgen um 19 Uhr geoeffnet, rettet der Schutz die Serie
    app.page.clock.set_fixed_time(datetime.datetime.combine(HEUTE + datetime.timedelta(days=1),
                                                            datetime.time(19, 5)))
    nachher = app.js("() => { pruefeSchutz(); return {meldung: schutzMeldung, n: streak(),"
                     " frost: [...frost]}; }")
    assert nachher == {"meldung": 1, "n": 5, "frost": [_iso(0)]}
    assert app.fehler == []


def test_lange_weg_b1_b2_b5_c4(app):
    """Ajdin am 14.11.2026: statt der Wortwitze nach 7 und mehr Tagen Pause
    B2 und C4, mit einem Lerntag auch B1 und B5 (B5 nur mit offenem Level).
    {tage} in B1 steht dort bis 13 (und darueber) in der Mehrzahl."""
    r = _lage(app, tage=_tage(7, 12))
    assert r["w"]["pause"] == 7
    assert r["g"] == {"vorrang": [], "pool": ["b1", "b2", "b5", "c4"]}
    assert r["fuell"]["b1"] == ["Šta ima? 🐉", "7 Tage Funkstille. Zmaj hat deine Wörter abgestaubt."]
    abende = _abende(r)
    assert all(p["key"] in LANGE and p["stunde"] == 19 for p in abende), r["plan"]
    _ohne_wiederholung(abende)
    assert {p["key"] for p in abende} == LANGE, abende   # reihum kommt jeder dran
    r = _lage(app, tage=_tage(13, 20))
    assert r["w"]["pause"] == 13
    assert r["fuell"]["b1"][1] == "13 Tage Funkstille. Zmaj hat deine Wörter abgestaubt."
    # Alles bestanden: kein B5
    r = _lage(app, tage=_tage(10, 20), alleBestanden=True)
    assert r["g"]["pool"] == ["b1", "b2", "c4"]
    assert all(p["key"] in {"b1", "b2", "c4"} for p in _abende(r)), r["plan"]
    _ohne_wiederholung(_abende(r))
    assert app.fehler == []


def test_nie_gelernt_b2_und_c4_im_wechsel(app):
    """Ohne einen Lerntag nur B2 und C4 - sie wechseln sich jeden Abend ab."""
    r = _lage(app, tage=[])
    assert r["g"] == {"vorrang": [], "pool": ["b2", "c4"]}
    keys = [p["key"] for p in _abende(r)]
    assert len(keys) == 7 and set(keys) == {"b2", "c4"}, keys
    _ohne_wiederholung(_abende(r))


@pytest.mark.parametrize("lage", [
    dict(tage=_tage(1, 2)), dict(tage=_tage(1, 11), rekord=10), dict(tage=_tage(1, 7), gefeiert=[]),
    dict(tage=_tage(1, 13), schutz=1, rekord=12, anzahl=250), dict(tage=_tage(1, 31), schutz=1),
    dict(tage=_tage(3, 10)), dict(tage=_tage(2, 9), schutz=1, alleBestanden=True),
    dict(tage=_tage(7, 12)), dict(tage=_tage(10, 20), alleBestanden=True), dict(tage=[]),
])
def test_gestrichene_kommen_nie(app, lage):
    """A1, B4 und D1-D6 kommen in keiner Lage, und jede Lage hat mindestens
    zwei Texte, die sich abwechseln."""
    r = _lage(app, **lage)
    assert not GESTRICHEN & set(r["g"]["pool"] + r["g"]["vorrang"]), r["g"]
    assert len(r["g"]["pool"]) >= 2, r["g"]
    assert not GESTRICHEN & {p["key"] for p in r["plan"]}, r["plan"]
    _ohne_wiederholung(_abende(r))


@pytest.mark.parametrize("anzahl,text", [
    (250, "Deine 200 Wörter sind alle noch da. Zmaj wartet ohne Eile."),
    (40, "Deine Wörter sind alle noch da. Zmaj wartet ohne Eile."),
])
def test_rueckhol_nach_14_tagen_ist_b6(app, anzahl, text):
    r = _lage(app, tage=_tage(1, 4), anzahl=anzahl)
    zurueck = [p for p in r["plan"] if p["art"] == "rueckhol"]
    assert len(zurueck) == 1
    assert zurueck[0]["key"] == "b6" and zurueck[0]["tag"] == _iso(14) and zurueck[0]["stunde"] == 19
    assert zurueck[0]["titel"] == "Ima li te? 🐉" and zurueck[0]["text"] == text


def test_rueckhol_nur_mit_einem_lerntag(app):
    """Pruefbericht 1.4, V6: Ohne einen Lerntag (frisch, nach dem Abmelden oder
    dem Loeschen des Kontos) gibt es nichts zurueckzuholen - "Deine Woerter
    sind alle noch da" stimmte dann nicht. Die Abende bleiben."""
    r = _lage(app, tage=[], anzahl=250)
    assert [p for p in r["plan"] if p["art"] == "rueckhol"] == [], r["plan"]
    assert len(_abende(r)) == 7
    r = _lage(app, tage=_tage(20, 21))
    assert [p["key"] for p in r["plan"] if p["art"] == "rueckhol"] == ["b6"]


def test_schalter_wie_bisher(app):
    r = _lage(app, tage=_tage(1, 4), schalter={"erinnerung": False, "serie": False})
    assert r["plan"] == []
    r = _lage(app, tage=_tage(1, 4), schalter={"erinnerung": False})
    assert [(p["art"], p["tag"]) for p in r["plan"]] == [("serie", _iso(0))]


def test_zweimal_planen_derselbe_text(app):
    a = _lage(app, tage=_tage(3, 10))
    b = _lage(app, tage=_tage(3, 10))
    assert [p["key"] for p in a["plan"]] == [p["key"] for p in b["plan"]]


def test_vorabend_ist_gesperrt(app):
    """Kam gestern B1, kommt heute ein anderer - auch wenn B1 reihum dran
    waere. Und der Text, der am laengsten nicht kam, gewinnt."""
    gestern = _tage(1, 2)[0]
    for k in sorted(B):
        texte = {x: "2026-10-01" for x in B}
        texte[k] = gestern
        r = _lage(app, tage=_tage(3, 10), texte=texte)
        assert _abende(r)[0]["key"] != k
    texte = {"b1": "2026-11-01", "b2": "2026-10-20", "b3": "2026-11-05", "b5": "2026-11-08"}
    r = _lage(app, tage=_tage(3, 10), texte=texte)
    assert _abende(r)[0]["key"] == "b2"


# ---------------------------------------------------------------------------
# Nie zweimal hintereinander: drei Wochen mit nachgebautem Plugin
# ---------------------------------------------------------------------------

PLUGIN = """() => { window.__ben = {pending: []};
  window.Capacitor = {Plugins: {LocalNotifications: {
    checkPermissions: async () => ({display: 'granted'}),
    requestPermissions: async () => ({display: 'granted'}),
    getPending: async () => ({notifications: __ben.pending.map(n => ({id: n.id}))}),
    cancel: async (o) => { const weg = new Set(o.notifications.map(n => n.id));
                           __ben.pending = __ben.pending.filter(n => !weg.has(n.id)); },
    createChannel: async () => {},
    checkExactNotificationSetting: async () => ({exact_alarm: 'denied'}),
    schedule: async (o) => { __ben.pending = __ben.pending.concat(o.notifications); },
  }}}; }"""

# Ein Schritt: Stand setzen (gelernt bis bis), planen, und was dann fuer
# morgen um 20 Uhr wartet, samt den gemerkten Texten.
SCHRITT = """async ([tage, gelernt]) => {
  days = new Set(tage); frost = new Set(); gefeiert = new Set(%s);
  schutz = {anzahl: 0, zeit: Date.now()};
  if(gelernt) rekord = streak();
  await benPlanen();
  const s = JSON.parse(localStorage.getItem('zmaj_benachrichtigung'));
  return {texte: s.texte || {}, geplant: s.geplant, pending: __ben.pending.map(n => ({id: n.id, at: +new Date(n.schedule.at),
          title: n.title, art: n.extra.art, aufklappbar: !!n.body && n.largeBody === n.body}))};
}""" % ALLE_WEGMARKEN


def test_drei_wochen_nie_derselbe_text_zweimal(app):
    """Jeden Abend kommt um 20 Uhr die Serienwarnung, um 21 Uhr wird
    gelernt. benPlanen() merkt sich beim naechsten Mal, was kam, und plant
    fuer morgen einen anderen Text - den, der am laengsten nicht kam. Bei
    sechs Texten in der Gruppe (Serie ab 7 = Rekord: A2-A5, C1, C3; A1 ist
    seit dem 14.11.2026 weg) kommt also jeder einmal, bevor sich einer
    wiederholt."""
    app.js(PLUGIN)
    app.js("() => { localStorage.setItem('zmaj_benachrichtigung', JSON.stringify("
           "{gefragt: true, erinnerung: true, serie: true, leben: false})); }")
    start = HEUTE
    tage = [(start - datetime.timedelta(days=i)).isoformat() for i in range(1, 10)]
    # Tag 0, 21:05: gelernt -> plant morgen
    app.page.clock.set_fixed_time(datetime.datetime.combine(start, datetime.time(21, 5)))
    tage.append(start.isoformat())
    app.js(SCHRITT, [tage, True])
    gekommen = []
    for i in range(1, 22):
        tag = start + datetime.timedelta(days=i)
        # 21:00: die 20-Uhr-Nachricht ist gekommen, noch nicht gelernt
        app.page.clock.set_fixed_time(datetime.datetime.combine(tag, datetime.time(21, 0)))
        r = app.js(SCHRITT, [tage, False])
        heute = [k for k, v in r["texte"].items() if v == tag.isoformat()]
        assert len(heute) == 1, (i, r["texte"])
        gekommen.append(heute[0])
        # 21:05: gelernt -> plant morgen, nie den von heute
        app.page.clock.set_fixed_time(datetime.datetime.combine(tag, datetime.time(21, 5)))
        tage.append(tag.isoformat())
        r = app.js(SCHRITT, [tage, True])
        morgen = (tag + datetime.timedelta(days=1)).isoformat()
        plan = [p for p in r["geplant"] if p["tag"] == morgen]
        assert len(plan) == 1 and plan[0]["art"] == "serie", r["geplant"]
        assert plan[0]["key"] != heute[0]
        # hoechstens eine Nachricht je Abend
        abende = [p for p in r["geplant"] if p["abend"]]
        assert len({p["tag"] for p in abende}) == len(abende)
        # Android klappt jede ganz auf (largeBody = body)
        assert r["pending"] and all(p["aufklappbar"] for p in r["pending"]), r["pending"]
    assert all(a != b for a, b in zip(gekommen, gekommen[1:])), gekommen
    assert sorted(gekommen[:6]) == ["a2", "a3", "a4", "a5", "c1", "c3"], gekommen
    assert sorted(gekommen[6:12]) == sorted(gekommen[:6]), gekommen
    assert sorted(gekommen[12:18]) == sorted(gekommen[:6]), gekommen
    assert not GESTRICHEN & set(gekommen), gekommen
    assert app.fehler == []


AUSWAHL = """() => {
  // Ein fester Zufall (LCG), damit der Lauf immer gleich ist.
  let z = 7; const zufall = n => { z = (z * 1103515245 + 12345) % 2147483648; return z % n; };
  const alle = Object.keys(BEN_TEXTE);
  const zuletzt = {}, folge = [];
  let tag = '2026-11-10';
  for(let i = 0; i < 400; i++){
    const pool = alle.filter(() => zufall(3) > 0);
    if(pool.length < 2) pool.push('b1', 'b2');
    const vorrang = zufall(5) === 0 ? [alle[zufall(alle.length)]] : [];
    const k = benWahl({vorrang, pool}, tag, zuletzt);
    folge.push(k); zuletzt[k] = tag; tag = tagMinus(tag, -1);
  }
  // Fest stehende Gruppe: jeder kommt einmal, bevor einer wiederkommt
  const fest = ['b1', 'b2', 'b3', 'b5', 'c4'], z2 = {}, reihe = [];
  tag = '2026-11-10';
  for(let i = 0; i < 15; i++){ const k = benWahl({vorrang: [], pool: fest}, tag, z2); reihe.push(k); z2[k] = tag; tag = tagMinus(tag, -1); }
  return {folge, reihe};
}"""


def test_auswahl_vierhundert_abende(app):
    """Mit wechselnden Gruppen und Vorrang-Texten: nie derselbe Text zwei
    Abende hintereinander. Bei fester Gruppe streng reihum."""
    r = app.js(AUSWAHL)
    f = r["folge"]
    assert all(a != b for a, b in zip(f, f[1:]))
    reihe = r["reihe"]
    for i in range(0, 15, 5):
        assert sorted(reihe[i:i + 5]) == ["b1", "b2", "b3", "b5", "c4"], reihe
    assert reihe[5:10] == reihe[:5] and reihe[10:] == reihe[:5]


# ---------------------------------------------------------------------------
# Alle acht Sprachen
# ---------------------------------------------------------------------------

SPRACHE = """async (code) => {
  await setzeSprache(code);
  const aus = {};
  const w = (n, extra) => Object.assign({n, pause: 4, rekord: n, ziel: 30, woerter: 1200, gerissen: true,
                                         level: CATEGORIES[0].label}, extra || {});
  Object.keys(BEN_TEXTE).forEach(k => {
    aus[k] = {eins: benTexte(k, w(1)), fuenf: benTexte(k, w(5)), dreissig: benTexte(k, w(30)),
              wenig: benTexte(k, w(5, {woerter: 0})), lange: benTexte(k, w(5, {pause: 13}))};
  });
  const roh = {}; Object.values(BEN_TEXTE).flat().concat(['ben.b6_text_wenig', 'ben.farbe_blau']).forEach(s => { roh[s] = T[s]; });
  return {aus, roh, level: CATEGORIES[0].label, sprache: SPRACHE};
}"""


def test_alle_sprachen_fertig_gefuellt(app):
    for code in SPRACHEN:
        r = app.js(SPRACHE, code)
        assert r["sprache"] == code
        for k, fassungen in r["aus"].items():
            for name, (titel, text) in fassungen.items():
                for teil in (titel, text):
                    assert teil and "{" not in teil and "|" not in teil and "ben." not in teil, (code, k, name, teil)
                    # "null" nicht: "null Tränen" ist gewollt
                    assert not any(x in teil for x in ("undefined", "NaN", "[object")), (code, k, name, teil)
        # Einzahl und Mehrzahl: genau die Seite vor bzw. hinter dem Strich
        assert sorted(r["aus"]) == sorted(["a2", "a3", "a4", "a5", "a6", "b1", "b2", "b3", "b5", "b6",
                                           "c1", "c2", "c3", "c4", "c5", "c6"]), code
        for k in ("a2", "a3", "a5"):
            roh = r["roh"]["ben.%s_titel" % k].split("|")
            assert r["aus"][k]["eins"][0] == roh[0].replace("{n}", "1"), (code, k)
            assert r["aus"][k]["fuenf"][0] == roh[1].replace("{n}", "5"), (code, k)
        assert r["level"] in r["aus"]["b5"]["eins"][1], code
        assert "4" in r["aus"]["b1"]["eins"][1] and "1200" in r["aus"]["b6"]["eins"][1], code
        # 13 Tage Pause (seit 14.11.2026 kommt B1 auch nach 7 und mehr Tagen):
        # dieselbe Mehrzahl wie bei 4, nur die Zahl anders
        assert r["aus"]["b1"]["lange"][1] == r["roh"]["ben.b1_text"].replace("{tage}", "13"), code
        assert r["aus"]["b1"]["eins"][1] == r["roh"]["ben.b1_text"].replace("{tage}", "4"), code
        assert r["aus"]["b6"]["wenig"][1] == r["roh"]["ben.b6_text_wenig"], code
        assert r["roh"]["ben.farbe_blau"] in r["aus"]["c5"]["dreissig"][1], code
    assert app.fehler == [] and app.fremd == []
