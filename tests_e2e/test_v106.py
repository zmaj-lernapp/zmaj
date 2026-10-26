# -*- coding: utf-8 -*-
"""Was seit v104 neu ist, im echten Browser (17.10.2026): Satzbau mit
Wortkacheln, der gemalte Bild-Drache und das App-Symbol im Browser-Tab.

Bis hierher pruefte nichts davon gezielt ein Browser. Die Kacheln liefen
nur nebenbei durch DURCHSPIELEN (conftest.py) - immer richtig, und nur, wenn
der Zufall der Lektion sie gerade zog. Der Drache kam nur in
test_sicherung_einlesen vor, und dort wird bloss geprueft, dass zmajDaten()
nicht wirft. Ob jedes der 32 Teile in jeder der zehn Hautfarben und jedes
Teil der vierundzwanzig Kostueme wirklich geladen und in Jubel und Weinen
gezeigt wird, sah kein Test.

Aufbau wie in test_app_im_browser.py: jeder Test mit eigenem, leerem
Browserkontext, Geraetemodus. Die Aufgabe wird nicht ueber den Zufall der
Lektion gesucht, sondern gezielt auf den Bildschirm gelegt (KACHEL_AUFGABE);
angetippt wird danach mit echten Klicks.

Beim Drachen heisst "Jubel" cheer und "Weinen" cry (MOOD_SEG in index.html).
Gemessen wird nicht im Lauf, sondern Bild fuer Bild: der Test setzt die
Abschnitte zurueck und springt wie playMood() bei ruhender Animation mit
goToAndStop auf einzelne Bilder. So ist die Messung unabhaengig vom Takt.
"""
import json
import os
import re
import struct

import pytest
from conftest import Seite

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASKOTTCHEN = os.path.join(WURZEL, "web", "maskottchen")
AXE = os.path.join(WURZEL, "tests_e2e", "vendor", "axe.min.js")
PNG = b"\x89PNG\r\n\x1a\n"


# ---------------------------------------------------------------------------
# Satzbau: Wortkacheln
# ---------------------------------------------------------------------------

# Beispielsaetze aus dem echten Inhalt, ausgesucht nach Eigenschaften statt nach
# Wortlaut - kommt ein Satz dazu oder faellt einer weg, laeuft der Test weiter.
#   einfach:  drei oder mehr verschiedene Kacheln; weder die Umkehrung noch das
#             erste Wort allein gilt als Satz (sonst waere "falsch" nicht falsch)
#   mehrere:  ein Satz mit "auch", dessen andere Reihenfolge nur Kacheln des
#             Satzes braucht (Ajdin: mehrere Reihenfolgen duerfen richtig sein)
SAETZE_SUCHEN = """() => {
    const klein = a => a.map(x => x.toLowerCase());
    const einzig = a => a.length === new Set(klein(a)).size;
    const gilt = s => [s.bs, ...(s.auch || [])].map(kachelNorm);
    const e = SATZBAU.find(s => {
        const t = satzKacheln(s.bs), g = gilt(s);
        return t.length >= 3 && einzig(t)
            && !g.includes(kachelNorm(t.slice().reverse().join(' '))) && !g.includes(kachelNorm(t[0]));
    });
    let m = null;
    for(const s of SATZBAU){
        const t = klein(satzKacheln(s.bs));
        if(!einzig(t)) continue;
        const alt = (s.auch || []).find(a => {
            const r = klein(kachelRoh(a));
            return r.length >= 2 && einzig(r) && r.every(x => t.includes(x)) && kachelNorm(a) !== kachelNorm(s.bs);
        });
        if(alt){ m = {bs: s.bs, alt: kachelRoh(alt)}; break; }
    }
    return {einfach: e ? {bs: e.bs, de: e.de, teile: satzKacheln(e.bs)} : null, mehrere: m};
}"""

# Genau diese eine Aufgabe in die Lektion legen. openLevel/startLesson bauen die
# Ansicht und Lx; danach wird die Warteschlange ersetzt und neu gezeichnet.
KACHEL_AUFGABE = """(bs) => {
    openLevel(0); startLesson();
    const s = SATZBAU.find(x => x.bs === bs);
    Lx.queue = [{typ: 'kacheln', s}]; Lx.i = 0; Lx.total = 1;
    showLessonTask();
    return {leben: livesNow(), kat: s.kat};
}"""

LAGE = """() => ({
    ergebnisse: Lx.results.slice(), richtig: Lx.right, laenge: Lx.queue.length, i: Lx.i,
    nochmal: !!Lx.queue[Lx.queue.length - 1].retry, leben: livesNow() })"""


def _genau(text):
    """Ganzer Text, Gross/klein egal: Kacheln stehen klein da, ein Name gross."""
    return re.compile(r"^\s*" + re.escape(text) + r"\s*$", re.IGNORECASE)


class Kacheln:
    """Die Aufgabe, wie ein Finger sie sieht: Zeile oben, Vorrat darunter."""

    def __init__(self, page):
        self.page = page
        self.vorrat_ort = page.locator("#lBody #xBank .kachel:not(.platz)")
        self.zeile_ort = page.locator("#lBody #xZeile .kachel")
        self.platz_ort = page.locator("#lBody #xBank .kachel.platz")
        self.pruefen = page.locator("#lBody #xCheck")
        self.rueckmeldung = page.locator("#lBody #xFb")

    def vorrat(self):
        return [t.strip() for t in self.vorrat_ort.all_inner_texts()]

    def gelegt(self):
        return [t.strip() for t in self.zeile_ort.all_inner_texts()]

    def platzhalter(self):
        return self.platz_ort.count()

    def tippe(self, wort):
        self.vorrat_ort.filter(has_text=_genau(wort)).click()

    def zurueck(self, wort):
        self.zeile_ort.filter(has_text=_genau(wort)).click()

    def legen(self, woerter):
        for w in woerter:
            self.tippe(w)

    def klassen(self, ort):
        return (self.page.locator(ort).get_attribute("class") or "").split()


def _aufgabe(seite, heute_stand, welche="einfach"):
    """Seite starten, Beispielsatz suchen, Aufgabe zeigen. Gibt (Satz, Kacheln, Leben)."""
    seite.starten(stand=heute_stand())
    saetze = seite.js(SAETZE_SUCHEN)
    satz = saetze[welche]
    assert satz, "kein passender Beispielsatz in SATZBAU (%s)" % welche
    leben = seite.js(KACHEL_AUFGABE, satz["bs"])["leben"]
    k = Kacheln(seite.page)
    k.vorrat_ort.first.wait_for()
    return satz, k, leben


def test_kacheln_antippen_legt_in_die_zeile_und_zurueck(seite, heute_stand):
    """Antippen im Vorrat legt die Kachel ans Ende der Zeile, ein Platzhalter
    haelt ihre Stelle frei; Antippen in der Zeile legt sie an genau diese
    Stelle zurueck. Ohne Platzhalter rueckten die anderen nach, und der
    naechste Tipp traefe eine andere Kachel als die, auf die man zielte."""
    satz, k, _ = _aufgabe(seite, heute_stand)
    teile = satz["teile"]
    anfang = k.vorrat()
    assert k.gelegt() == []
    assert k.pruefen.is_disabled(), "Pruefen darf bei leerer Zeile nicht gehen"
    assert k.platzhalter() == 0
    for t in teile:
        assert t in anfang, "Kachel %r fehlt im Vorrat %s" % (t, anfang)
    assert len(anfang) > len(teile), "keine falschen Kacheln (Ablenker) im Vorrat"
    # Kacheln ohne Satzzeichen am Rand, sonst verraet das Komma die Stelle
    assert not [x for x in anfang if re.search(r"^[.,!?;:]|[.,!?;:]$", x)], anfang

    k.tippe(teile[0])
    assert k.gelegt() == [teile[0]]
    assert k.platzhalter() == 1
    assert len(k.vorrat()) == len(anfang) - 1
    assert k.pruefen.is_enabled()

    k.tippe(teile[1])
    assert k.gelegt() == teile[:2]
    assert k.platzhalter() == 2

    k.zurueck(teile[0])                      # die erste wieder heraus: die zweite rueckt vor
    assert k.gelegt() == [teile[1]]
    assert k.platzhalter() == 1
    assert teile[0] in k.vorrat()
    assert k.pruefen.is_enabled()

    k.zurueck(teile[1])
    assert k.gelegt() == []
    assert k.platzhalter() == 0
    assert k.vorrat() == anfang, "Kacheln nicht an ihren Platz zurueckgekehrt"
    assert k.pruefen.is_disabled()
    assert seite.fehler == []


def test_kacheln_richtige_reihenfolge_ist_richtig(seite, heute_stand):
    satz, k, leben = _aufgabe(seite, heute_stand)
    k.legen(satz["teile"])
    assert k.gelegt() == satz["teile"]
    k.pruefen.click()

    assert "ok" in k.klassen("#lBody #xFb")
    assert "no" not in k.klassen("#lBody #xFb")
    assert "ok" in k.klassen("#lBody #xZeile")
    assert "Falsch" not in k.rueckmeldung.inner_text()
    # nach der Antwort ist die Aufgabe zu: Pruefen weg, keine Kachel mehr beweglich
    assert not k.pruefen.is_visible()
    assert k.page.locator("#lBody .kachel:not([disabled])").count() == 0
    # die Loesung steht darunter: das Bosnische und was es heisst
    assert k.page.locator("#lBody .loesung .lbs").inner_text() == satz["bs"]
    assert k.page.locator("#lBody .loesung .lde").inner_text() == satz["de"]
    lage = seite.js(LAGE)
    assert lage["ergebnisse"] == [True]
    assert lage["richtig"] == 1
    assert lage["leben"] == leben, "eine richtige Antwort darf kein Herz kosten"
    k.page.locator("#lBody .weiterbox .btn").wait_for()
    assert seite.fehler == []


@pytest.mark.parametrize("variante", ["umgekehrt", "unvollstaendig", "mit_ablenker"])
def test_kacheln_falsche_reihenfolge_ist_falsch(seite, heute_stand, variante):
    """Falsch heisst: ein Herz weg, die Loesung steht da, der Satz kommt am
    Ende der Lektion noch einmal und liegt im Fehlertopf. Dazu drei Arten,
    falsch zu liegen: Reihenfolge, zu wenig Kacheln, eine Kachel zu viel."""
    satz, k, leben = _aufgabe(seite, heute_stand)
    teile = satz["teile"]
    if variante == "umgekehrt":
        legen = teile[::-1]
    elif variante == "unvollstaendig":
        legen = teile[:1]
    else:
        ablenker = [x for x in k.vorrat() if x.lower() not in [t.lower() for t in teile]]
        assert ablenker, "kein Ablenker im Vorrat"
        legen = teile + ablenker[:1]
    k.legen(legen)
    assert k.gelegt() == legen
    k.pruefen.click()

    assert "no" in k.klassen("#lBody #xFb")
    assert "ok" not in k.klassen("#lBody #xFb")
    assert "no" in k.klassen("#lBody #xZeile")
    assert satz["bs"] in k.rueckmeldung.inner_text(), "die richtige Loesung steht nicht im Hinweis"
    assert k.page.locator("#lBody .loesung .lbs").inner_text() == satz["bs"]
    lage = seite.js(LAGE)
    assert lage["ergebnisse"] == [False]
    assert lage["richtig"] == 0
    assert lage["leben"] == leben - 1
    assert lage["laenge"] == 2 and lage["nochmal"], "falsche Aufgabe kommt nicht noch einmal"

    # Fehlertopf: ohne Zweig fuer 'k:' raeumte topfAufraeumen() den Satz sofort weg
    topf = seite.js("""(bs) => {
        const k = Object.keys(topf).find(x => x.startsWith('k:') && x.endsWith('|' + bs));
        topfAufraeumen();
        return {drin: !!k, typ: k ? topf[k].typ : null, bleibt: !!k && (k in topf),
                runde: topfRunde().some(a => a.typ === 'kacheln' && a.s.bs === bs)};
    }""", satz["bs"])
    assert topf == {"drin": True, "typ": "kacheln", "bleibt": True, "runde": True}

    # Die Wiederholung: gleiche Aufgabe, leere Zeile, alle Kacheln wieder frei
    k.page.locator("#lBody .weiterbox .btn").click()
    k.vorrat_ort.first.wait_for()
    assert k.page.locator("#lBody .kicker .rep").count() == 1, "die Wiederholung ist nicht gekennzeichnet"
    assert k.gelegt() == []
    assert k.pruefen.is_disabled()
    k.legen(teile)
    k.pruefen.click()
    assert "ok" in k.klassen("#lBody #xFb")
    lage = seite.js(LAGE)
    assert lage["ergebnisse"] == [False, True]
    assert lage["richtig"] == 1
    assert seite.fehler == []


def test_kacheln_andere_reihenfolge_aus_auch_gilt(seite, heute_stand):
    """Bei 'Ja se zovem Amina.' ist auch 'Zovem se Amina.' ein richtiger Satz -
    und die App wertet ihn so, obwohl die Kachel 'ja' dabei uebrig bleibt."""
    satz, k, leben = _aufgabe(seite, heute_stand, "mehrere")
    k.legen(satz["alt"])
    k.pruefen.click()
    assert "ok" in k.klassen("#lBody #xFb"), "'%s' gilt nicht" % " ".join(satz["alt"])
    assert "ok" in k.klassen("#lBody #xZeile")
    lage = seite.js(LAGE)
    assert lage["ergebnisse"] == [True]
    assert lage["leben"] == leben
    assert seite.fehler == []


def test_lektion_mit_kacheln_ganz_durchspielen(seite, heute_stand):
    """Eine echte Lektion, in der bestimmt Kacheln dran sind (Level 1, alle
    Woerter schon gewusst, damit jeder Satz 'bereit' ist), komplett richtig:
    jede Kachelaufgabe ist gewertet, kein Herz geht verloren."""
    seite.starten(stand=heute_stand())
    vorher = seite.js("""() => {
        CATEGORIES[0].words.forEach(w => known.add(w.id));
        openLevel(0); startLesson();
        return {kacheln: Lx.queue.filter(q => q.typ === 'kacheln').length, leben: livesNow()}; }""")
    assert vorher["kacheln"] >= 1, "keine Kachelaufgabe in der Lektion"
    typen = seite.durchspielen("lBody", "Lx")
    assert typen.count("kacheln") == vorher["kacheln"]
    ergebnis = seite.js("""() => ({
        ende: !!document.getElementById('lMore'), richtig: Lx.right,
        gewertet: Lx.results.filter(r => r !== 'intro' && r !== 'skip').length, leben: livesNow() })""")
    assert ergebnis["ende"], "kein Ergebnisschirm nach der Lektion"
    assert ergebnis["richtig"] == ergebnis["gewertet"] > 0
    assert ergebnis["leben"] == vorher["leben"]
    assert seite.fehler == []


def test_leveltest_hat_keine_kacheln(seite, heute_stand):
    """Im Level-Test kommt der Satzbau bewusst nicht vor (wie die Luecken):
    zweiunddreissig frisch gebaute Tests (vier Level, je achtmal), keiner mit
    Kachelaufgabe."""
    seite.starten(stand=heute_stand())
    typen = seite.js("""() => {
        CATEGORIES.slice(0, 4).forEach(c => c.words.forEach(w => known.add(w.id)));
        const alle = new Set();
        for(let level = 0; level < 4; level++){
            openLevel(level);
            for(let n = 0; n < 8; n++){ buildTest(); Tx.qs.forEach(q => alle.add(q.typ)); }
        }
        return [...alle].sort(); }""")
    assert typen, "keine Aufgabenarten im Test"
    assert "kacheln" not in typen
    assert seite.fehler == []


# Alle Saetze des Satzbaus durch die echte Aufgabe der App: jeder laesst sich
# in seiner Reihenfolge und in jeder Variante aus "auch" legen und wird als
# richtig gewertet, und die falschen Kacheln daneben sind nie ein Wort des
# Satzes oder einer Variante und nie aus KACHEL_VERWECHSELBAR. Die Python-Tests
# (tests/test_inhalt_tiefe.py) pruefen die Daten; hier rechnet die JavaScript-
# Seite - satzKacheln, kachelNorm und kachelAblenker muessen dasselbe meinen.
# Die Aufgabe wird je Satz in ein freies Feld gezeichnet und mit click() bedient.
ALLE_SAETZE = """() => {
    const probleme = [];
    const sperre = new Set(KACHEL_VERWECHSELBAR);
    let ablenker = 0;
    for(const s of SATZBAU){
        const lege = (reihenfolge, gleich) => {
            let antwort = null;
            const feld = document.createElement('div');
            document.body.appendChild(feld);
            renderTask({typ: 'kacheln', s}, feld, res => { antwort = res; });
            const vorrat = [...feld.querySelectorAll('#xBank .kachel')].map(o => o.textContent);
            for(const w of reihenfolge){
                const b = [...feld.querySelectorAll('#xBank .kachel:not(.platz)')].find(o => gleich(o.textContent, w));
                if(!b){ feld.remove(); return {fehlt: w, vorrat}; }
                b.click();
            }
            feld.querySelector('#xCheck').click();
            feld.remove();
            return {ok: !!antwort && antwort.ok === true, vorrat};
        };
        const teile = satzKacheln(s.bs);
        const r = lege(teile, (a, b) => a === b);
        if(r.fehlt || !r.ok) probleme.push('Reihenfolge von bs wird nicht gewertet: ' + s.bs);
        const eigene = new Set([s.bs, ...(s.auch || [])].flatMap(x => kachelRoh(x).map(k => k.toLowerCase())));
        const rest = r.vorrat.slice();
        teile.forEach(w => { const i = rest.indexOf(w); if(i >= 0) rest.splice(i, 1); });
        ablenker += rest.length;
        if(rest.length < (teile.length >= 5 ? 3 : 2)) probleme.push('zu wenig falsche Kacheln bei: ' + s.bs);
        rest.forEach(w => {
            if(eigene.has(w.toLowerCase()) || sperre.has(w.toLowerCase())) probleme.push('falsche Kachel "' + w + '" ist erlaubt bei: ' + s.bs);
        });
        for(const alt of (s.auch || [])){
            const v = lege(kachelRoh(alt), (a, b) => a.toLowerCase() === b.toLowerCase());
            if(v.fehlt) probleme.push('Variante "' + alt + '" laesst sich nicht legen (keine Kachel "' + v.fehlt + '") bei: ' + s.bs);
            else if(!v.ok) probleme.push('Variante "' + alt + '" wird nicht gewertet bei: ' + s.bs);
        }
    }
    stilleBitte();
    return {saetze: SATZBAU.length, ablenker, probleme};
}"""


def test_alle_satzbau_saetze_sind_loesbar(seite, heute_stand):
    seite.starten(stand=heute_stand())
    r = seite.js(ALLE_SAETZE)
    assert r["saetze"] > 300, "SATZBAU ist auffaellig klein: %d" % r["saetze"]
    assert r["ablenker"] > r["saetze"], "die Saetze haben kaum falsche Kacheln"
    assert r["probleme"] == [], "\n".join(r["probleme"][:20])
    assert seite.fehler == []


# axe-core ueber die Kachelaufgabe. test_barrierefreiheit.py ist aelter als der
# Satzbau und kennt sie nicht. Wie dort zaehlen nur ernste und kritische
# Verstoesse. Vor jeder Messung warten, bis alle CSS-Uebergaenge fertig sind:
# der Pruefen-Knopf blendet beim Freiwerden von der Sperrfarbe zur Knopffarbe
# ueber, und mitten darin misst axe ein zu schwaches Kontrastverhaeltnis
# (4,03 statt 4,5, gesehen am 17.10.2026), das es im Ruhezustand nicht gibt.
UEBERGAENGE_ABWARTEN = """async () => {
    await Promise.all(document.getAnimations().filter(a => a instanceof CSSTransition)
        .map(a => a.finished.catch(() => null)));
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
}"""
AXE_ERNST = """async () => (await axe.run(document, {resultTypes: ['violations']})).violations
    .filter(v => v.impact === 'serious' || v.impact === 'critical')
    .map(v => v.id + ' (' + v.impact + '): ' + v.nodes.map(n => n.target.join(' ')).join(', '))"""


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_kacheln_ansicht_ohne_ernste_verstoesse(browser, basis, heute_stand, schema):
    """Leer, zwei Kacheln gelegt, richtig beantwortet, falsch beantwortet - hell und dunkel."""
    kontext = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                                  service_workers="block", color_scheme=schema)
    try:
        seite = Seite(kontext.new_page(), basis)
        seite.starten(stand=heute_stand())
        satz = seite.js(SAETZE_SUCHEN)["einfach"]
        assert satz
        seite.js(KACHEL_AUFGABE, satz["bs"])
        k = Kacheln(seite.page)
        k.vorrat_ort.first.wait_for()
        seite.page.add_script_tag(path=AXE)
        funde = []

        def messen(zustand):
            seite.js(UEBERGAENGE_ABWARTEN)
            funde.extend("%s/%s: %s" % (schema, zustand, v) for v in seite.js(AXE_ERNST))

        messen("leer")
        k.legen(satz["teile"][:2])
        messen("zwei gelegt")
        k.legen(satz["teile"][2:])
        k.pruefen.click()
        messen("richtig")
        seite.js(KACHEL_AUFGABE, satz["bs"])           # dieselbe Aufgabe noch einmal, jetzt falsch
        k.vorrat_ort.first.wait_for()
        k.legen(satz["teile"][::-1])
        k.pruefen.click()
        messen("falsch")
        assert funde == [], "\n".join(funde)
        assert seite.fehler == []
    finally:
        kontext.close()


# ---------------------------------------------------------------------------
# Bild-Drache: Hautfarben, Kostueme, Stimmungen
# ---------------------------------------------------------------------------

STIMMUNGEN = ["idle", "cheer", "cry"]                      # Ruhe, Jubel, Weinen
KOPF = {"idle": "kopf_neutral.webp", "cheer": "kopf_jubel.webp", "cry": "kopf_weinen.webp"}


class Netz:
    """Alles, was das Netz zu den Bildern sagt. Zwei 404 sind Absicht und
    gehoeren zum Aufbau der Tests: /leer (die leere Seite desselben Ursprungs,
    siehe Seite.starten) und /api/... (ohne Server laeuft die App im
    Geraetemodus)."""

    ERWARTET = ("/leer", "/api/")

    def __init__(self, page):
        self.antworten = []
        self.gescheitert = []
        page.on("response", lambda r: self.antworten.append((r.status, r.url)))
        page.on("requestfailed", lambda r: self.gescheitert.append(r.url))

    def kaputt(self):
        out = ["%d %s" % (s, u) for s, u in self.antworten
               if s >= 400 and not any(e in u for e in self.ERWARTET)]
        return out + ["gescheitert: %s" % u for u in self.gescheitert]

    def geholt(self, teil):
        """Die URLs, die geholt wurden und `teil` enthalten (Status 200)."""
        return [u for s, u in self.antworten if s == 200 and teil in u]


@pytest.fixture
def netz(seite):
    return Netz(seite.page)


# Einen Drachen bauen, Stimmung fuer Stimmung Bild fuer Bild durchgehen und
# messen. `vorgabe` ist das, was zmajDaten() auch im Kaufkasten bekommt
# ({ids, farbe}); ohne Vorgabe, mit Selektor, wird der Drache genommen, der
# schon auf dem Bildschirm steht.
#   alle    jede <image>-Adresse im SVG (alle Ebenen, auch gerade verborgene)
#   stimm   je Stimmung die Bilder, die in irgendeinem ihrer Bilder wirklich
#           zu sehen sind (Rechteck > 0; verborgene Ebenen haben keins)
#   kaputt  Adressen, die der Browser nicht als Bild laden konnte
DRACHE_MESSEN = """async ([vorgabe, stimmungen, selektor, abraeumen]) => {
    const warte = ms => new Promise(r => setTimeout(r, ms));
    let el = selektor ? document.querySelector(selektor) : null;
    if(!el){
        el = document.createElement('div'); el.className = 'zmaj-anim';
        el.style.cssText = 'position:fixed;left:0;top:0;width:260px;height:250px;z-index:99999';
        document.body.appendChild(el);
        mountZmaj(el, 'idle', vorgabe);
    }
    const ende = Date.now() + 20000;
    while(!(el._anim && el._anim.isLoaded)){
        if(Date.now() > ende) throw new Error('der Drache laedt nicht');
        await warte(30);
    }
    const a = el._anim;
    const href = i => i.getAttribute('href') || i.getAttributeNS('http://www.w3.org/1999/xlink', 'href') || '';
    const alle = [...new Set([...el.querySelectorAll('svg image')].map(href))];
    const stimm = {};
    for(const m of stimmungen){
        const seg = segOf(a, MOOD_SEG[m]);
        if(!seg){ stimm[m] = null; continue; }
        a.resetSegments(true);              // sonst zaehlt goToAndStop im zuletzt gespielten Abschnitt
        const sicht = new Set();
        for(let f = seg[0]; f < seg[1]; f += 5){
            a.goToAndStop(f, true);
            el.querySelectorAll('svg image').forEach(i => {
                const r = i.getBoundingClientRect();
                if(r.width > 0 && r.height > 0) sicht.add(href(i));
            });
        }
        stimm[m] = [...sicht];
    }
    const geladen = {};
    await Promise.all(alle.map(h => new Promise(fertig => {
        const b = new Image();
        b.onload = () => { geladen[h] = b.naturalWidth > 0; fertig(); };
        b.onerror = () => { geladen[h] = false; fertig(); };
        b.src = h;
    })));
    const stand = el._stand || '';
    if(abraeumen) el.remove();
    return {alle, stimm, stand, kaputt: alle.filter(h => !geladen[h])};
}"""

# Die Tracht, die die App an einem Festtag anzieht - ohne den Kalender.
# festHeute() ist eine Funktion der App; kurz ersetzt, danach zurueck.
FEST_TRACHT = """(id) => {
    const alt = festHeute; festHeute = () => id;
    try { return festTracht(); } finally { festHeute = alt; }
}"""


def _teile_dateien():
    """Die 32 Bilder des Grundsatzes (teile/), wie sie auf der Platte liegen."""
    return set(os.listdir(os.path.join(MASKOTTCHEN, "teile")))


def _schnipsel(kostuem):
    """Die Ebenen eines Kostuems (zmajz-<id>.json) und seine Bilder."""
    with open(os.path.join(MASKOTTCHEN, "zmajz-%s.json" % kostuem), encoding="utf-8") as f:
        d = json.load(f)
    if isinstance(d, dict):
        return d.get("layers", []), d.get("assets", [])
    return d, []


def _hat_bilder(kostuem):
    """Gemalte Stuecke (Bild-Ebenen) haben Bilder; Galaxie und der Rueckfall
    des Skeletts sind Vektor - sie bestehen nur aus Ebenen."""
    return any(a.get("p") for a in _schnipsel(kostuem)[1])


def _erwartete_teile(kostueme, farbe):
    """Welche der 32 Bilder des Grunddrachen am Drachen haengen muessen.
    Alle - ausser denen, die ein Kostuem mit Absicht leert: Huete und Kronen
    nehmen die Hornspitzen heraus ("zmaj_leert", siehe zmajDaten() und
    LIESMICH.txt im Maskottchen-Ordner). Das Vektor-Skelett faellt mit seinem
    Hautsatz weg (zmaj_ohne_haut) und leert dann nichts."""
    with open(os.path.join(MASKOTTCHEN, "zmaj.json"), encoding="utf-8") as f:
        z = json.load(f)
    datei = {a["id"]: a["p"] for a in z["assets"] if a.get("p")}
    je_ebene = {l["nm"]: datei[l["refId"]] for l in z["layers"] if l.get("refId") in datei}
    weg = set()
    for k in kostueme:
        for ebene in _schnipsel(k)[0]:
            if farbe and ebene.get("zmaj_ohne_haut") == farbe:
                continue
            weg.update(je_ebene[n] for n in ebene.get("zmaj_leert", []) if n in je_ebene)
    # Mit der Sonnenbrille blinzelt der Drache nicht (26.10.2026, ohneBlinzeln()
    # in index.html): Kopf- und Hornbild zum Blinzeln fallen mit Absicht weg.
    if "sonnenbrille" in kostueme:
        weg.update(je_ebene[n] for n in ("bild_kopf_blinzeln", "bild_hoerner_blinzeln") if n in je_ebene)
    return set(je_ebene.values()) - weg


def befunde(r, farbe, kostueme, stimmungen=STIMMUNGEN, grundsatz=True):
    """Was an einer Messung (DRACHE_MESSEN) nicht stimmt, als Liste von Saetzen.
    farbe '' ist die Grundfarbe (teile/), sonst haut/<farbe>/. Mit grundsatz=False
    fehlt der Grunddrache absichtlich (das Vektor-Skelett ohne Hautsatz)."""
    out = []
    alle = r["alle"]
    if not alle and grundsatz:
        return ["kein <image> im SVG"]
    if r["kaputt"]:
        out.append("Bilder nicht ladbar: %s" % r["kaputt"])
    wirr = [h for h in alle if not h.startswith("maskottchen/") or "undefined" in h or "null" in h]
    if wirr:
        out.append("seltsame Bildadressen: %s" % wirr)
    grund = [h for h in alle if re.match(r"maskottchen/(teile|haut/[^/]+)/", h)]
    soll = "maskottchen/haut/%s/" % farbe if farbe else "maskottchen/teile/"
    falsche = [h for h in grund if not h.startswith(soll)]
    if falsche:
        out.append("Teile nicht aus %s: %s" % (soll, falsche[:3]))
    if grundsatz:
        namen = {os.path.basename(h) for h in grund}
        soll_namen = _erwartete_teile(kostueme, farbe)
        if namen != soll_namen:
            out.append("Teile des Drachen: fehlt %s, zuviel %s" % (sorted(soll_namen - namen), sorted(namen - soll_namen)))
    for k in kostueme:
        if not _hat_bilder(k):
            continue
        meine = [h for h in alle if h.startswith("maskottchen/zierrat/%s/" % k)]
        if not meine:
            out.append("Kostuem %s: kein Bild am Drachen" % k)
        elif not any(h.startswith("maskottchen/zierrat/%s/" % k) for m in stimmungen for h in (r["stimm"].get(m) or [])):
            out.append("Kostuem %s: in keiner Stimmung zu sehen" % k)
    for m in stimmungen:
        sicht = r["stimm"].get(m)
        if sicht is None:
            out.append("Stimmung %s: kein Abschnitt (Marker) in zmaj.json" % m)
            continue
        if grundsatz:
            if not any(h.endswith("/" + KOPF[m]) for h in sicht):
                out.append("Stimmung %s: der Kopf %s ist nie zu sehen (sichtbar: %s)"
                           % (m, KOPF[m], sorted({os.path.basename(h) for h in sicht if "/kopf_" in h})))
            if not any(h.endswith("/body.webp") for h in sicht):
                out.append("Stimmung %s: der Koerper ist nie zu sehen" % m)
    return out


def _messen(seite, vorgabe, stimmungen=STIMMUNGEN, selektor=None):
    return seite.js(DRACHE_MESSEN, [vorgabe, stimmungen, selektor, selektor is None])


def _netz_ok(seite, netz):
    assert netz.kaputt() == [], "Fehlschlaege im Netz: %s" % netz.kaputt()
    assert seite.fehler == []
    assert seite.fremd == [], "Anfragen an fremde Server: %s" % seite.fremd


def test_drache_in_grundfarbe_ohne_kaputte_bilder(seite, heute_stand, netz):
    """Der Drache, wie ihn jeder zuerst sieht: blau, ohne Kostuem."""
    seite.starten(stand=heute_stand())
    r = _messen(seite, {"ids": [], "farbe": ""})
    assert befunde(r, "", []) == []
    assert len(r["alle"]) == len(_teile_dateien())
    assert netz.geholt("/maskottchen/teile/body.webp"), "Netz-Mitschnitt leer: wurde body.webp nie geholt?"
    _netz_ok(seite, netz)


@pytest.mark.parametrize("stimmung", ["cheer", "cry"])
def test_drache_gold_mit_koenigsmantel_in_jubel_und_weinen(seite, heute_stand, netz, stimmung):
    """Haut Gold (Vollversion) und Koenigsmantel (umhang), so wie der Kaufkasten
    sie zeigt. Jubel und Weinen haben eigene Koepfe, Arme (Faust, Wange) und
    Aermel - hier fiel im Lauf der Bild-Umstellung am ehesten ein Teil aus."""
    seite.starten(stand=heute_stand())
    r = _messen(seite, {"ids": ["umhang"], "farbe": "gold"}, [stimmung])
    assert befunde(r, "gold", ["umhang"], [stimmung]) == []
    sicht = r["stimm"][stimmung]
    assert "maskottchen/haut/gold/" + KOPF[stimmung] in sicht
    assert "maskottchen/haut/gold/body.webp" in sicht
    mantel = [h for h in sicht if h.startswith("maskottchen/zierrat/umhang/")]
    assert mantel, "der Mantel ist in dieser Stimmung nicht zu sehen"
    # Jubel hebt die Faeuste, Weinen legt die Haende an die Wangen: andere Teile
    # (LIESMICH.txt im Maskottchen-Ordner), je Seite einer
    teil = "_faust.webp" if stimmung == "cheer" else "_wange.webp"
    for seitenteil in ("unterarmL", "unterarmR"):
        assert "maskottchen/haut/gold/%s%s" % (seitenteil, teil) in sicht, "%s%s nie zu sehen" % (seitenteil, teil)
    assert netz.geholt("/maskottchen/haut/gold/body.webp")
    assert netz.geholt("/maskottchen/zierrat/umhang/mantel.webp")
    _netz_ok(seite, netz)


def test_drache_traegt_in_der_vollversion_gold_und_umhang(seite, heute_stand, vollversion, netz):
    """Der Weg, den ein zahlender Nutzer geht: Sicherung mit Vollversion, im
    Laden Gold und Umhang anziehen (trage), der Drache auf der Startseite
    baut sich neu. Der Kalender ist festgenagelt (kein Fest), sonst legte
    etwa Halloween das Skelett ueber Gold."""
    seite.starten(stand=heute_stand(**vollversion["stand"]))
    fertig = """() => { const e = document.querySelector('#zmajHome .zmaj-anim');
        return !!(e && e._anim && e._anim.isLoaded); }"""
    # Jedes Anziehen erst abwarten, bevor das naechste kommt - so prueft
    # dieser Test nur das Anziehen. Dass schnelles Umziehen waehrend des
    # Ladens im neuen Aufzug endet (bis 17.10.2026 blieb der alte stehen),
    # prueft test_barrierefreiheit_v106.py.
    seite.page.wait_for_function(fertig, timeout=30000)
    seite.js("() => { festHeute = () => ''; trage('gold'); }")
    seite.page.wait_for_function(fertig, timeout=30000)
    seite.js("() => trage('umhang')")
    seite.page.wait_for_function(fertig, timeout=30000)
    tracht = seite.js("() => festTracht()")
    assert tracht["farbe"] == "gold"
    assert "umhang" in tracht["ids"]
    r = _messen(seite, None, STIMMUNGEN, "#zmajHome .zmaj-anim")
    assert "gold" in r["stand"] and "umhang" in r["stand"], "die Startseite zeigt den alten Drachen: %s" % r["stand"]
    assert befunde(r, "gold", tracht["ids"]) == []
    _netz_ok(seite, netz)


def test_kaufkasten_drache_in_voller_montur(seite, heute_stand, netz):
    """Der Drache im Kaufkasten der Vollversion: Krone, Monokel, Umhang, Galaxie
    und Funkeln auf einmal, in Jubel. Der Kasten braucht Googles Preise und
    laesst sich im Browser nicht oeffnen; die Vorgabe wird deshalb so gebildet
    wie in vollWahlZeigen() (index.html: mountZmaj(schau, 'cheer', ...))."""
    seite.starten(stand=heute_stand())
    vorgabe = seite.js("""() => ({ids: ['krone_gross', 'monokel', 'umhang', 'galaxie', 'funkeln']
        .filter(id => MASCOT.has(zierratDatei(id))), farbe: 'galaxie'})""")
    assert len(vorgabe["ids"]) == 5, vorgabe
    r = _messen(seite, vorgabe, ["cheer"])
    assert befunde(r, "galaxie", vorgabe["ids"], ["cheer"]) == []
    _netz_ok(seite, netz)


# Wie playMood() bei ruhender Animation (Schalter "Animationen" aus oder
# Geraete-Einstellung "weniger Bewegung"): kein Lauf, sondern ein Standbild aus
# der Mitte der Stimmung. Gemessen wird gleich nach dem Laden, vor dem
# Zeitgeber, der kurze Stimmungen in die Ruhepose zurueckholt.
STANDBILD = """async ([vorgabe, stimmung]) => {
    document.body.classList.add('no-anim');
    const el = document.createElement('div'); el.className = 'zmaj-anim';
    el.style.cssText = 'position:fixed;left:0;top:0;width:260px;height:250px;z-index:99999';
    document.body.appendChild(el);
    mountZmaj(el, stimmung, vorgabe);
    const ende = Date.now() + 20000;
    while(!(el._anim && el._anim.isLoaded)){
        if(Date.now() > ende) throw new Error('der Drache laedt nicht');
        await new Promise(r => setTimeout(r, 10));
    }
    const href = i => i.getAttribute('href') || i.getAttributeNS('http://www.w3.org/1999/xlink', 'href') || '';
    const sicht = [...el.querySelectorAll('svg image')].filter(i => {
        const r = i.getBoundingClientRect(); return r.width > 0 && r.height > 0; }).map(href);
    return {sicht, pausiert: el._anim.isPaused, stimmung: el.dataset.mood};
}"""


@pytest.mark.parametrize("stimmung,kopf", [("cheer", "kopf_jubel"), ("cry", "kopf_weinen"), ("sad", "kopf_traurig")])
def test_drache_ohne_animation_zeigt_standbild_der_stimmung(seite, heute_stand, stimmung, kopf):
    """Mit ausgeschalteten Animationen steht der Drache still und zeigt trotzdem
    die Stimmung - nicht die Ruhepose und nicht ein Blinzeln dazwischen."""
    seite.starten(stand=heute_stand())
    r = seite.js(STANDBILD, [{"ids": ["umhang"], "farbe": "gold"}, stimmung])
    assert r["pausiert"] is True, "der Drache laeuft trotz 'Animationen aus'"
    koepfe = sorted({os.path.basename(h) for h in r["sicht"] if "/kopf_" in h})
    assert koepfe == [kopf + ".webp"], koepfe
    assert "maskottchen/haut/gold/body.webp" in r["sicht"]
    assert seite.fehler == []


def test_alle_hautfarben_laden_ohne_kaputte_bilder(seite, heute_stand, netz):
    """Jeder Hautsatz in haut/ (zehn) am Drachen, in Ruhe, Jubel und Weinen.
    Gesammelt statt einzeln, damit die App nur einmal startet; die Meldung
    nennt jede kaputte Farbe."""
    farben = sorted(d for d in os.listdir(os.path.join(MASKOTTCHEN, "haut"))
                    if os.path.isdir(os.path.join(MASKOTTCHEN, "haut", d)))
    assert len(farben) >= 9, farben
    seite.starten(stand=heute_stand())
    probleme = []
    for farbe in farben:
        r = _messen(seite, {"ids": [], "farbe": farbe})
        probleme += ["Haut %s: %s" % (farbe, b) for b in befunde(r, farbe, [])]
    assert probleme == [], "\n".join(probleme)
    _netz_ok(seite, netz)


def test_alle_kostueme_laden_ohne_kaputte_bilder(seite, heute_stand, netz):
    """Jedes Kostuem aus dem Laden (zmajz-*.json) einzeln am blauen Drachen.
    Das Vektor-Skelett ist ohne Hautsatz ein Rueckfall ohne Grunddrachen
    (zmaj_leert) - dort fehlt der Grundsatz mit Absicht."""
    kostueme = sorted(re.match(r"zmajz-(.+)\.json$", f).group(1)
                      for f in os.listdir(MASKOTTCHEN) if re.match(r"zmajz-.+\.json$", f))
    assert len(kostueme) >= 24, kostueme
    seite.starten(stand=heute_stand())
    probleme = []
    for k in kostueme:
        r = _messen(seite, {"ids": [k], "farbe": ""})
        probleme += ["Kostuem %s: %s" % (k, b) for b in befunde(r, "", [k], grundsatz=(k != "skelett"))]
    assert probleme == [], "\n".join(probleme)
    _netz_ok(seite, netz)


def test_festtrachten_laden_ohne_kaputte_bilder(seite, heute_stand, netz):
    """Was die App an Weihnachten, Bajram, Ostern und Halloween anzieht, mit
    der Rechnung der App (festTracht): Halloween ist Skelett-Haut mit Hexenhut."""
    seite.starten(stand=heute_stand())
    feste = seite.js("() => Object.keys(FESTE)")
    assert sorted(feste) == ["bajram", "halloween", "ostern", "weihnachten"]
    probleme = []
    for fest in feste:
        tracht = seite.js(FEST_TRACHT, fest)
        assert tracht["ids"], "%s: keine Kostueme" % fest
        r = _messen(seite, tracht)
        probleme += ["%s: %s" % (fest, b) for b in befunde(r, tracht["farbe"], tracht["ids"])]
    assert probleme == [], "\n".join(probleme)
    _netz_ok(seite, netz)


def test_standbilder_des_drachen_laden(seite, heute_stand):
    """Ohne lottie zeigt die App die drei Standbilder (zmaj() in index.html).
    Hier lottie kurz ausblenden und nachsehen, dass sie da sind und der
    Browser sie zeichnen kann."""
    seite.starten(stand=heute_stand())
    r = seite.js("""async () => {
        const l = window.lottie; window.lottie = undefined;
        const aus = {};
        try { for(const m of ['happy', 'cheer', 'sad', 'cry']) aus[m] = zmaj(m); } finally { window.lottie = l; }
        const ergebnis = {};
        for(const m in aus){
            const treffer = /<img src="([^"]+)"/.exec(aus[m]);
            if(!treffer){ ergebnis[m] = {src: null, breite: 0}; continue; }
            const breite = await new Promise(res => { const b = new Image();
                b.onload = () => res(b.naturalWidth); b.onerror = () => res(0); b.src = treffer[1]; });
            ergebnis[m] = {src: treffer[1], breite};
        }
        return ergebnis; }""")
    assert {m: v["src"] for m, v in r.items()} == {
        "happy": "maskottchen/zmaj-frei.png", "cheer": "maskottchen/zmaj-jubel.png",
        "sad": "maskottchen/zmaj-traurig.png", "cry": "maskottchen/zmaj-traurig.png"}
    assert all(v["breite"] > 0 for v in r.values()), r
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# App-Symbol und Tab-Symbol
# ---------------------------------------------------------------------------

def test_symbol_links_zeigen_auf_vorhandene_dateien(seite, heute_stand):
    """Browser-Tab und Startbildschirm-Symbol (link rel=icon und
    apple-touch-icon): die Datei antwortet mit 200, ist ein 256-Pixel-PNG, der
    Browser kann sie zeichnen, und sie liegt in web/. Die Kopfzeile behaelt
    die Flagge (flagge.png) und sie laedt."""
    seite.starten(stand=heute_stand())
    links = seite.js("""() => [...document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]')]
        .map(l => ({rel: l.rel, href: l.href, roh: l.getAttribute('href'), type: l.type}))""")
    assert {l["rel"] for l in links} == {"icon", "apple-touch-icon"}, links
    for l in links:
        antwort = seite.page.request.get(l["href"])
        assert antwort.status == 200, "%s: %d" % (l["roh"], antwort.status)
        assert antwort.headers["content-type"].startswith("image/png"), antwort.headers["content-type"]
        if l["type"]:
            assert l["type"] == "image/png"
        daten = antwort.body()
        assert daten[:8] == PNG, "%s ist kein PNG" % l["roh"]
        assert struct.unpack(">II", daten[16:24]) == (256, 256), "%s ist nicht 256 x 256" % l["roh"]
        breite = seite.js("""(url) => new Promise(res => { const b = new Image();
            b.onload = () => res(b.naturalWidth); b.onerror = () => res(0); b.src = url; })""", l["href"])
        assert breite == 256, "der Browser zeichnet %s nicht" % l["roh"]
        assert os.path.isfile(os.path.join(WURZEL, "web", l["roh"].split("?")[0])), "%s fehlt in web/" % l["roh"]
    flagge = seite.js("""() => { const i = document.querySelector('img.flag');
        return i ? {geladen: i.complete && i.naturalWidth > 0, src: i.getAttribute('src')} : null; }""")
    assert flagge and flagge["geladen"], "die Flagge in der Kopfzeile laedt nicht: %s" % flagge
    assert os.path.isfile(os.path.join(WURZEL, "web", flagge["src"].split("?")[0]))
    assert seite.fehler == []


def test_icon_ico_ist_gueltig():
    """web/icon.ico (Windows-Verknuepfung, nicht im HTML verlinkt): eine
    gueltige ICO-Datei mit einem 256er-Bild, dessen Verzeichnis zur Dateigroesse passt."""
    with open(os.path.join(WURZEL, "web", "icon.ico"), "rb") as f:
        daten = f.read()
    reserviert, art, anzahl = struct.unpack("<HHH", daten[:6])
    assert (reserviert, art) == (0, 1), "keine ICO-Datei"
    assert anzahl >= 1
    groessen = []
    for n in range(anzahl):
        breite, hoehe, _, _, _, _, laenge, ab = struct.unpack("<BBBBHHII", daten[6 + 16 * n:22 + 16 * n])
        assert ab + laenge <= len(daten), "Eintrag %d reicht ueber das Dateiende" % n
        groessen.append((breite or 256, hoehe or 256))
    assert (256, 256) in groessen, groessen
