# -*- coding: utf-8 -*-
"""Stufen-Reiter A1 · A2 · B1 · B2 · C1 im Lernpfad (13.11.2026).

Ajdin am 13.11.2026 zu Release\\Entscheidungen_2026-11-13 (reiter.md):
„alles wie empfohlen“, also Variante B mit Sprung-Test, der Leben kostet wie
der Level-Test (7a). Hier steht, was ein Lernender sieht:

- oben die Leiste mit fünf Reitern; der Pfad öffnet sich in dem Reiter, in dem
  Weitermachen steht, und zeigt nur dessen Sektionen, Farben und Nummern ab 1;
- ein Reiter, der noch zu ist, zeigt eine Karte mit dem Sprung-Test, wenn der
  Reiter davor offen ist; C1 sagt nur „kommt bald“;
- bestandener Sprung-Test: Reiter offen, übersprungene Level offen, aber nicht
  bestanden, keine Münzen, kein Lerntag;
- jede falsche Antwort kostet ein Leben, ohne Leben startet er nicht, bei null
  ist er vorbei und nicht bestanden; ohne Leben gibt es dieselben Wege zu
  einem Leben wie im Level-Test;
- wer vor dem Update schon weiter war, verliert nichts: B1 bleibt fertig, die
  zwei neuen Grundwort-Level sind „dran“ (auch nach einer alten Einstufung),
  angefangene Zuhause-Level bleiben offen;
- der Stand in der Leiste passt bei 360 und 320 px, auch mit großer
  Systemschrift, in allen acht Sprachen;
- wer in 1.3 eingestuft wurde, verliert nach dem ersten Grundwort-Level nicht
  den Einstieg, und was die alte Einstufung offen hatte, bleibt offen.

Inhalt und Quelltext prüft tests/test_reiter.py ohne Browser."""
import pytest
from conftest import Seite

STUFEN = ["A1", "A2", "B1", "B2", "C1"]

LEISTE = """() => [...document.querySelectorAll('#reiterLeiste button')].map(b => ({
  st: b.dataset.stufe, art: b.className, an: b.getAttribute('aria-selected') === 'true',
  text: b.querySelector('.sz').textContent.trim()}))"""

SEKTIONEN = """() => [...document.querySelectorAll('#sections .section')].map(s => ({
  titel: s.querySelector('h2').textContent, sek: s.className.match(/sek(\\d)/)[1]}))"""

# Die Sprachen der Oberfläche, wie in sprachen.SPRACHEN
SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]

# So stellt Chrome die große Systemschrift des Handys nach (wie in
# test_kaufkasten.py und test_marken.py)
GROSSE_SCHRIFT = """document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.style.cssText += ';text-size-adjust:130%;-webkit-text-size-adjust:130%'; });"""

# Drei Stände in einer Seite, gezeichnet ohne Neuladen: neu (A1 offen, drei zu,
# C1 bald), weit (alle offen mit den größten Zahlen, B2 dreistellig) und fertig.
STAENDE_MESSEN = """async () => {
  await document.fonts.ready;   // gemessen wird in der Schrift der App, nicht im Ersatz
  const L = st => reiterLevel(st).map(i => CATEGORIES[i].id);
  const staende = {
    neu: [],
    weit: [...L('A1').slice(0, -1), ...L('A2').slice(0, -1), ...L('B1').slice(0, -1), ...L('B2').slice(0, 112)],
    fertig: CATEGORIES.map(c => c.id),
  };
  const alt = new Set(passed), aus = {};
  for(const [name, ids] of Object.entries(staende)){
    passed.clear(); ids.forEach(id => passed.add(id));
    reiterLeisteZeichnen(angezeigteStufe());
    aus[name] = [...document.querySelectorAll('#reiterLeiste button')].map(b => {
      const sz = b.querySelector('.sz'), innen = sz.querySelector('.szi');
      // sw/cw sind auf ganze Pixel gerundet; iw/ow messen genau (45,7 px Text in 44,8 px)
      return {st: b.dataset.stufe, art: b.className, text: sz.textContent.trim(), label: b.getAttribute('aria-label'),
              sicht: sz.innerText.trim(), nur: sz.classList.contains('nurzeichen'),
              px: parseFloat(sz.style.fontSize || getComputedStyle(sz).fontSize),
              iw: innen.getBoundingClientRect().width, ow: sz.getBoundingClientRect().width,
              sw: sz.scrollWidth, cw: sz.clientWidth, bw: b.scrollWidth, bc: b.clientWidth};
    });
  }
  passed.clear(); alt.forEach(id => passed.add(id));
  reiterLeisteZeichnen(angezeigteStufe());
  return aus;
}"""

# Eine Antwort im laufenden Sprung-Test, richtig oder falsch, mit festgelegter
# Auswahlaufgabe aus Level 1 - so ist "falsch" sicher falsch. Wartet, bis
# Weiter steht (oder der Test vorbei ist).
ANTWORT = r"""
async (richtig) => {
  const body = document.getElementById('eBody');
  const warte = ms => new Promise(r => setTimeout(r, ms));
  const bis = async (bed, was) => {
    const ende = Date.now() + 8000;
    while(!bed()){ if(Date.now() > ende) throw new Error('wartet vergeblich auf: ' + was); await warte(15); }
  };
  const i = Sx.i, c0 = CATEGORIES[0];
  Sx.qs[i] = {typ: 'mc', w: c0.words[i % c0.words.length], pool: c0.words};
  sprungFrageZeigen();
  await bis(() => body.dataset.i === String(i) && body.querySelector('.opt') && !body.querySelector('.weiterbox'), 'Aufgabe ' + i);
  const w = Sx.qs[i].w.bs;
  const b = [...body.querySelectorAll('.opt')].find(o => richtig ? o.textContent === w : o.textContent !== w);
  b.click();
  await bis(() => Sx.i > i, 'Antwort auf ' + i);
  await bis(() => !!body.querySelector('.weiterbox .btn'), 'Weiter nach ' + i);
}
"""


def _pfad(seite, stand):
    seite.starten(stand=stand)
    seite.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    seite.js("() => { homeMode = 'words'; showHome(); }")


@pytest.fixture
def ids(seite, heute_stand):
    seite.starten(stand=heute_stand())
    return seite.js("() => CATEGORIES.map(c => c.id)")


def test_neu_offen_ist_a1(seite, heute_stand):
    _pfad(seite, heute_stand())
    leiste = seite.js(LEISTE)
    assert [b["st"] for b in leiste] == STUFEN
    assert [b["art"] for b in leiste] == ["offen", "zu", "zu", "zu", "bald"]
    assert [b["an"] for b in leiste] == [True, False, False, False, False]
    assert leiste[0]["text"] == "0/30"
    assert seite.js("() => document.getElementById('reiterKarte').hidden")
    sek = seite.js(SEKTIONEN)
    assert [s["titel"] for s in sek] == ["Sektion 1 · Grundlagen & Alltag", "Sektion 2 · Dinge zum Anfassen",
                                         "Sektion 3 · Tiere & Natur", "Sektion 4 · Sätze bauen 1"]
    assert [s["sek"] for s in sek] == ["1", "2", "3", "4"]
    assert seite.fehler == [] and seite.fremd == []


# Breite x Höhe, große Systemschrift (130 %)
GROESSEN = [(360, 640, False), (320, 640, False), (360, 780, True), (320, 640, True)]


@pytest.mark.parametrize("sprache", SPRACHEN)
@pytest.mark.parametrize("breite,hoehe,gross", GROESSEN, ids=["360", "320", "360-gross", "320-gross"])
def test_stand_passt_in_die_leiste(browser, basis, heute_stand, sprache, breite, hoehe, gross):
    """Prüfung vom 13.11.2026: Bei 360 px (Ajdins S21) schnitt die Leiste den
    Stand an beiden Seiten ab, auf Türkisch immer ('30 içinden 29' wurde
    '0 içinden 2'), auf Deutsch ab dreistelligen Zahlen in B2. Jetzt steht er
    kurz als '112/129' da; der lange Satz bleibt für den Bildschirmleser.
    Zweite Prüfung: bei 320 px und mit großer Systemschrift endete er trotzdem
    in Pünktchen ('112/1…', '🔒 lock…', 'binnenk…'). Jetzt wird er kleiner,
    höchstens bis 7 px; reicht das nicht, bleibt nur das Zeichen bzw. die Zahl
    der bestandenen Level - nie eine abgeschnittene Zahl."""
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, device_scale_factor=3,
                              is_mobile=True, has_touch=True, locale="de-DE", service_workers="block")
    if gross:
        ctx.add_init_script(GROSSE_SCHRIFT)
    seite = Seite(ctx.new_page(), basis)
    try:
        _stand_messen(seite, heute_stand, sprache, breite)
    finally:
        ctx.close()


def _stand_messen(seite, heute_stand, sprache, breite):
    seite.starten(sprache=sprache, stand=heute_stand())
    seite.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    seite.js("() => { homeMode = 'words'; showHome(); }")
    assert seite.js("() => window.innerWidth") == breite
    aus = seite.js(STAENDE_MESSEN)
    zu_eng = [(name, b) for name, knoepfe in aus.items() for b in knoepfe
              if b["sw"] > b["cw"] or b["bw"] > b["bc"] or b["iw"] > b["ow"] + 0.01]
    assert zu_eng == [], zu_eng
    assert all(b["px"] >= 7 for knoepfe in aus.values() for b in knoepfe), aus
    # Sichtbar ist der ganze Stand oder die Zahl davor, nie ein Stück davon
    for b in aus["weit"][:4]:
        assert b["sicht"] == (b["text"].split("/")[0] if b["nur"] else b["text"]), b
    assert [b["art"] for b in aus["neu"]] == ["offen", "zu", "zu", "zu", "bald"]
    assert [b["art"] for b in aus["weit"]] == ["offen", "offen", "offen", "offen", "bald"]
    assert [b["art"] for b in aus["fertig"]] == ["fertig", "fertig", "fertig", "fertig", "bald"]
    assert [b["text"] for b in aus["weit"]][:4] == ["29/30", "30/31", "106/107", "112/129"]
    # Der Bildschirmleser hört den ganzen Satz in der Sprache, nicht "112 Schrägstrich 129"
    assert all(b["label"].startswith(b["st"]) for b in aus["weit"])
    assert "129" in aus["weit"][3]["label"] and "112" in aus["weit"][3]["label"]
    if sprache == "de":
        assert aus["weit"][3]["label"] == "B2, 112 von 129"
    assert seite.fehler == []


def test_reiter_antippen(seite, heute_stand):
    _pfad(seite, heute_stand())
    # A2: noch zu, aber A1 ist offen - also mit Sprung-Test
    seite.page.click("#reiterLeiste button[data-stufe='A2']")
    karte = seite.page.locator("#reiterKarte")
    assert karte.is_visible()
    assert karte.locator("h2").text_content() == "A2 ist noch zu"
    assert karte.locator("#sprungStart").text_content() == "Sprung-Test starten"
    assert "15 Fragen aus A1 · ab 12 richtig ist A2 offen" in karte.text_content()
    sek = seite.js(SEKTIONEN)
    assert [s["titel"] for s in sek][:2] == ["Sektion 1 · Zuhause", "Sektion 2 · Sätze bauen 2"]
    assert sek[0]["sek"] == "1", "Farben fangen in jedem Reiter neu an"
    # das erste Level von A2 sagt, was davor kommt
    erstes = seite.page.locator("#sections .section").first
    if "zu" in erstes.get_attribute("class").split():      # zugeklappt
        erstes.locator(".skopf").click()
        erstes = seite.page.locator("#sections .section").first
    erstes.locator(".node").first.click()
    assert erstes.locator(".node .state").first.text_content() == "Zuerst A1 abschließen"
    assert seite.js("() => sichtbar('pfad')")
    # B1: A2 ist selbst noch zu, also kein Sprung-Test
    seite.page.click("#reiterLeiste button[data-stufe='B1']")
    assert karte.locator("#sprungStart").count() == 0
    assert "Schließ erst A2 ab." in karte.text_content()
    # C1: leer
    seite.page.click("#reiterLeiste button[data-stufe='C1']")
    assert karte.locator("h2").text_content() == "C1 kommt bald"
    assert seite.page.locator("#sections .section").count() == 0
    # Die Wahl bleibt nach dem Neuzeichnen stehen
    seite.js("() => showHome()")
    assert [b["an"] for b in seite.js(LEISTE)] == [False, False, False, False, True]
    assert seite.fehler == []


# Wo die Leiste auf dem Bildschirm steht, und welcher Reiter gewaehlt ist
LAGE = """() => ({oben: document.getElementById('reiterLeiste').getBoundingClientRect().top,
  an: (document.querySelector('#reiterLeiste button[aria-selected="true"]') || {}).dataset.stufe})"""


@pytest.mark.parametrize("breite,hoehe", [(360, 740), (412, 915)], ids=["360", "412"])
def test_reiter_antippen_springt_nicht(browser, basis, heute_stand, breite, hoehe):
    """Ajdin am 14.11.2026: "wenn man auf B1 zb tippt dann springt das bild
    so komisch wieder nach oben mach das raus". Die Leiste bleibt beim
    Tippen auf einen Reiter, wo sie war (hoechstens 2 px), nur der Inhalt
    darunter wechselt - ob sie oben, in der Mitte oder unten im Bild steht,
    in einen langen Reiter, in einen zugeklappten und in C1, das fast leer
    ist. Getippt wird echt, mit der Maus auf den Knopf. Vorher stand man
    nach dem Tippen auf B1 oder C1 wieder ganz oben."""
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, locale="de-DE",
                              service_workers="block", reduced_motion="reduce")
    try:
        seite = Seite(ctx.new_page(), basis)
        _pfad(seite, heute_stand())
        lage = seite.js("""() => { const r = document.getElementById('reiterLeiste').getBoundingClientRect();
          return {oben: r.top + scrollY, hoch: r.height}; }""")
        gesprungen = []
        # die Leiste knapp unter dem Rand oben, in der Mitte, unten im Bild
        for ziel in (4, hoehe // 2, hoehe - lage["hoch"] - 4):
            for st in ["B1", "C1", "A2", "B2", "A1", "C1", "B1"]:
                seite.js("(y) => window.scrollTo({top: y, behavior: 'instant'})", max(0, lage["oben"] - ziel))
                vorher = seite.js(LAGE)
                seite.page.click("#reiterLeiste button[data-stufe='%s']" % st)
                nachher = seite.js(LAGE)
                assert nachher["an"] == st, (ziel, st, nachher)
                if abs(nachher["oben"] - vorher["oben"]) > 2:
                    gesprungen.append((ziel, vorher["an"], st, round(vorher["oben"]), round(nachher["oben"])))
        assert gesprungen == [], gesprungen
        # Die Startseite neu: oben, ohne leeren Bildschirm unter C1
        seite.page.click("#reiterLeiste button[data-stufe='C1']")
        seite.js("() => showHome()")
        assert seite.js("() => [scrollY, document.getElementById('wordsHome').style.minHeight]") == [0, ""]
        assert seite.js("() => document.documentElement.scrollWidth") <= breite
        assert seite.fehler == []
    finally:
        ctx.close()


def test_sprungtest_bestanden_oeffnet_den_reiter(seite, heute_stand):
    _pfad(seite, heute_stand())
    vorher = seite.js("() => ({muenzen: muenzen(), tage: days.size, bestanden: passed.size, leben: livesNow()})")
    seite.page.click("#reiterLeiste button[data-stufe='A2']")
    seite.page.click("#sprungStart")
    assert seite.js("() => [sichtbar('einstufungView'), Sx.qs.length, Sx.vorher, Sx.ziel]") == [True, 15, "A1", "A2"]
    # Gefragt wird nur aus A1, im Kasten steht das echte Herz
    assert seite.js("""() => Sx.qs.map(q => q.w ? CATEGORIES.find(c => c.words.includes(q.w)).id : (q.g ? q.g._lv : q.s.kat))
        .map(id => stufeVon(CATEGORIES.findIndex(c => c.id === id)))""") == ["A1"] * 15
    assert seite.js("() => document.getElementById('eHerz').classList.contains('platzhalter')") is False
    seite.durchspielen("eBody", "Sx")
    assert seite.js("() => Sx.fertig")
    assert seite.page.locator("#eBody .result-big").text_content() == "15 / 15"
    assert seite.page.locator("#eBody .feedback.ok").first.text_content() == "A2 ist offen!"
    nachher = seite.js("""() => ({muenzen: muenzen(), tage: days.size, bestanden: passed.size, leben: livesNow(),
        sprung: !!wann['sp:A2'], erstesA2: isUnlocked(reiterLevel('A2')[0]), zweitesA2: isUnlocked(reiterLevel('A2')[1]),
        letztesA1: isUnlocked(reiterLevel('A1').slice(-1)[0])})""")
    assert nachher == {**vorher, "sprung": True, "erstesA2": True, "zweitesA2": False, "letztesA1": True}
    # gespeichert, auch nach dem Neuladen
    seite.page.click("#sprungLos")
    assert [b["art"] for b in seite.js(LEISTE)] == ["offen", "offen", "zu", "zu", "bald"]
    assert [b["an"] for b in seite.js(LEISTE)][1], "zurueck im Reiter des Tests"
    assert seite.js("() => document.getElementById('reiterKarte').hidden")
    assert seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand')).wann['sp:A2']")
    # Ein Einstieg wie die Einstufung: wer noch nichts bestanden hat, macht in
    # A2 weiter; wer in A1 schon etwas bestanden hat, bleibt dort, bis er in
    # A2 etwas besteht.
    assert seite.js("() => firstOpen()") == seite.js("() => reiterLevel('A2')[0]")
    assert seite.js("() => { passed.add(CATEGORIES[0].id); passed.add(CATEGORIES[1].id); return firstOpen(); }") == 2
    assert seite.js("() => { passed.add(CATEGORIES[reiterLevel('A2')[0]].id); return firstOpen(); }") \
        == seite.js("() => reiterLevel('A2')[1]")
    assert seite.fehler == []


def test_sprungtest_kostet_leben(seite, heute_stand):
    _pfad(seite, heute_stand())
    seite.page.click("#reiterLeiste button[data-stufe='A2']")
    seite.page.click("#sprungStart")
    assert seite.js("() => livesNow()") == 5
    seite.js(ANTWORT, True)
    assert seite.js("() => livesNow()") == 5, "richtig kostet nichts"
    seite.js("() => document.querySelector('#eBody .weiterbox .btn').click()")
    seite.js(ANTWORT, False)
    assert seite.js("() => [livesNow(), document.getElementById('eHerz').textContent.trim()]") == [4, "4"]
    # bei null mitten im Test ist er vorbei und nicht bestanden
    seite.js("() => { lives = {anzahl: 1, zeit: Date.now()}; document.querySelector('#eBody .weiterbox .btn').click(); }")
    seite.js(ANTWORT, False)
    seite.js("() => document.querySelector('#eBody .weiterbox .btn').click()")
    assert seite.js("() => [Sx.fertig, Sx.ohneLeben, !!wann['sp:A2'], livesNow()]") == [True, True, False, 0]
    assert seite.page.locator("#eBody .feedback.no").text_content() == "Keine Leben mehr."
    # Prüfung vom 13.11.2026: derselbe Schirm wie im Level-Test, mit der Wartezeit
    assert seite.page.locator("#eBody .result-big.ohneleben").count() == 1
    assert "bis zum nächsten Leben" in seite.page.locator("#eBody .stats").text_content()
    seite.page.click("#sprungLos")
    # ohne Leben startet er nicht
    seite.page.click("#sprungStart")
    assert seite.js("() => sichtbar('pfad')")
    assert seite.page.locator("#sprungNote").text_content().startswith("Keine Leben mehr. Das nächste kommt in ")
    assert seite.fehler == []


def test_sprungtest_ohne_leben_zeigt_die_wege(seite, heute_stand):
    """Prüfung vom 13.11.2026 (7a „wie der Level-Test“): ohne Leben gab es keinen
    Weg zu einem neuen, der Hinweis sprach von der Grammatik-Erklärung und lag
    bei 360 x 740 unter dem Bildrand. Jetzt: eigener kurzer Satz, Münzen (und
    Video, wo erlaubt), sichtbar; mit einem Leben geht der Test wieder."""
    seite.page.set_viewport_size({"width": 360, "height": 740})
    _pfad(seite, heute_stand())
    seite.page.click("#reiterLeiste button[data-stufe='A2']")
    seite.js("() => { lives = {anzahl: 0, zeit: Date.now()}; muenzenGes = 500; muenzenAus = 0; renderLives(); }")
    seite.page.click("#sprungStart")
    seite.page.wait_for_timeout(600)          # sanftes Scrollen
    z = seite.js("""() => { const n = document.getElementById('sprungNote').getBoundingClientRect();
        const w = document.getElementById('sprungKCoin');
        const r = w && w.getBoundingClientRect();
        return {text: document.getElementById('sprungNote').textContent, sichtbar: n.top >= 0 && n.bottom <= innerHeight,
                knopf: !!w, knopfSichtbar: !!r && r.top >= 0 && r.bottom <= innerHeight, pfad: sichtbar('pfad')}; }""")
    assert z["pfad"] and z["knopf"], z
    assert z["sichtbar"] and z["knopfSichtbar"], z
    assert "Grammatik" not in z["text"] and z["text"].startswith("Keine Leben mehr."), z
    # Ein Herz für Münzen: zurück auf der Karte ohne Hinweis, der Test startet
    seite.page.click("#sprungKCoin")
    assert seite.js("() => [livesNow(), muenzen(), document.getElementById('sprungNote').textContent]") == [1, 400, ""]
    seite.page.click("#sprungStart")
    assert seite.js("() => sichtbar('einstufungView') && !Sx.fertig")
    # Mitten im Test bei null: dieselben Wege; mit Münzen zurück zur Karte
    seite.js(ANTWORT, False)
    seite.js("() => document.querySelector('#eBody .weiterbox .btn').click()")
    assert seite.js("() => [Sx.ohneLeben, livesNow(), !!document.getElementById('sprungECoin')]") == [True, 0, True]
    seite.page.click("#sprungECoin")
    assert seite.js("() => [sichtbar('pfad'), livesNow(), angezeigteStufe()]") == [True, 1, "A2"]
    assert seite.page.locator("#sprungStart").count() == 1
    # Wachsen die Leben nach, verschwindet ein alter Hinweis von selbst
    seite.js("() => { lives = {anzahl: 0, zeit: Date.now()}; renderLives(); }")
    seite.page.click("#sprungStart")
    assert seite.page.locator("#sprungNote").text_content() != ""
    seite.js("() => { lives = {anzahl: 1, zeit: Date.now()}; ohneLebenVorbei(); }")
    assert seite.page.locator("#sprungNote").text_content() == ""
    assert seite.fehler == []


def test_sprungtest_abbrechen(seite, heute_stand):
    _pfad(seite, heute_stand())
    seite.page.click("#reiterLeiste button[data-stufe='A2']")
    seite.page.click("#sprungStart")
    seite.page.click("#eQuit")
    assert seite.page.locator(".nachfrage h3").text_content() == "Sprung-Test abbrechen?"
    seite.page.click("#frJa")
    seite.page.wait_for_function("() => sichtbar('pfad')", timeout=5000)
    assert seite.js("() => [Sx.fertig, !!wann['sp:A2']]") == [True, False]
    assert [b["an"] for b in seite.js(LEISTE)][1]
    assert seite.fehler == []


def test_fortgeschrittene_verlieren_nichts(seite, heute_stand, ids):
    """Stand von vor dem Update: alles bis zum Ende von B1 bestanden, die 40
    Grundwörter aus B1 gewusst. Danach ist B1 fertig, B2 offen, und die zwei
    neuen Level sind offen und „dran“ (Weitermachen springt zurück, gewollt)."""
    neu = ["kleine_woerter", "jeden_tag"]
    bis_b1 = [i for i in ids[:ids.index("fuerwoerter") + 1] if i not in neu]
    seite.starten(stand=heute_stand())
    woerter = seite.js("() => CATEGORIES.filter(c => c.id !== 'kleine_woerter' && c.id !== 'jeden_tag')"
                       ".slice(0, 166).flatMap(c => c.words.map(w => w.id))"
                       ".concat(CATEGORIES.filter(c => c.id === 'kleine_woerter' || c.id === 'jeden_tag').flatMap(c => c.words.map(w => w.id)))")
    _pfad(seite, heute_stand(bestanden=bis_b1, gewusst=woerter))
    z = seite.js("""() => ({dran: CATEGORIES[firstOpen()].id, stufe: angezeigteStufe(),
        neu: ['kleine_woerter', 'jeden_tag'].map(id => isUnlocked(CATEGORIES.findIndex(c => c.id === id))),
        bestanden: passed.size, b2: isUnlocked(reiterLevel('B2')[0])})""")
    assert z == {"dran": "kleine_woerter", "stufe": "A1", "neu": [True, True], "bestanden": len(bis_b1), "b2": True}
    assert [b["art"] for b in seite.js(LEISTE)] == ["offen", "offen", "fertig", "offen", "bald"]
    assert [b["text"] for b in seite.js(LEISTE)][:3] == ["29/30", "30/31", "✓ fertig"]
    assert seite.fehler == []


def test_angefangenes_zuhause_bleibt_offen(seite, heute_stand, ids):
    """Bis Natur bestanden, in Küche & Bad schon Wörter gelernt: Küche & Bad
    stand vorher direkt dahinter und bleibt offen, obwohl es jetzt in A2 steht.
    Weitermachen geht zu Fragen stellen (Sätze bauen 1)."""
    seite.starten(stand=heute_stand())
    woerter = seite.js("() => CATEGORIES.find(c => c.id === 'kueche_bad').words.slice(0, 4).map(w => w.id)")
    _pfad(seite, heute_stand(bestanden=ids[:23], gewusst=woerter))
    z = seite.js("""() => { const k = id => CATEGORIES.findIndex(c => c.id === id);
        return {dran: CATEGORIES[firstOpen()].id, kueche: isUnlocked(k('kueche_bad')), putzen: isUnlocked(k('putzen')),
                stufe: angezeigteStufe()}; }""")
    assert z == {"dran": "fragen", "kueche": True, "putzen": False, "stufe": "A1"}
    # A2 selbst bleibt zu (sein erstes Level ist zu), mit Sprung-Test - Küche & Bad
    # ist darin trotzdem offen und lässt sich antippen
    seite.page.click("#reiterLeiste button[data-stufe='A2']")
    assert seite.js("() => stufeStand('A2').art") == "zu"
    assert seite.page.locator("#sprungStart").count() == 1
    kueche = seite.page.locator("#sections .node").first
    assert "locked" not in kueche.get_attribute("class").split()
    assert seite.js("() => offeneSektion") == "zuhause2", "dort ist in A2 etwas zu tun"
    seite.page.locator("#sections .section").first.locator(".node").first.click()
    assert seite.js("() => [sichtbar('levelView'), cur().id]") == [True, "kueche_bad"]
    assert seite.fehler == []


def test_weiter_in_den_naechsten_reiter(seite, heute_stand, ids):
    """Nach dem letzten Level von A1 heisst der Knopf nicht "Weiter zu Level 1",
    sondern "Weiter zu A2"; danach öffnet der Lernpfad in A2."""
    _pfad(seite, heute_stand(bestanden=ids[:29]))
    seite.js("() => { catIdx = 29; cur().words.forEach(w => known.add(w.id)); openLevel(29); startTest(); }")
    seite.durchspielen("tBody", "Tx")
    assert seite.js("() => document.getElementById('tNext').textContent") == "Weiter zu A2 →"
    seite.page.click("#tNext")
    assert seite.js("() => [catIdx, document.getElementById('tag').textContent]") == [30, "Level 1 von 31"]
    seite.page.click("#btnBack")
    assert [b["an"] for b in seite.js(LEISTE)] == [False, True, False, False, False]
    assert [b["art"] for b in seite.js(LEISTE)][:2] == ["fertig", "offen"]
    assert seite.fehler == []


def test_levelnummer_je_reiter(seite, heute_stand, ids):
    _pfad(seite, heute_stand(bestanden=ids[:40]))
    seite.js("() => openLevel(CATEGORIES.findIndex(c => c.id === 'kueche_bad'))")
    assert seite.page.locator("#tag").text_content() == "Level 1 von 31"
    assert seite.page.locator("#lvTitle small").text_content() == "A2 · Sektion 1"
    seite.js("() => openLevel(CATEGORIES.findIndex(c => c.id === 'kleine_woerter'))")
    assert seite.page.locator("#tag").text_content() == "Level 29 von 30"
    assert seite.fehler == []


DRAN = """() => ({dran: CATEGORIES[firstOpen()].id, stufe: angezeigteStufe(),
    neu: ['kleine_woerter', 'jeden_tag'].map(id => isUnlocked(CATEGORIES.findIndex(c => c.id === id)))})"""


def test_vor_den_reitern_eingestuft_bekommt_die_grundwoerter(seite, heute_stand, ids):
    """Prüfung vom 13.11.2026: Wer vor dem Update bis zum Anfang von B1
    eingestuft war, hatte die 40 Grundwörter noch vor sich in B1. Jetzt liegen
    sie im übersprungenen A-Teil; ohne Ausnahme kämen sie nie dran
    (firstOpen suchte nur ab dem Einstieg). Die alte Einstufung hat kein Feld
    "reiter"."""
    import datetime
    tag = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    alt = {"tag": tag, "wahl": "gut", "bis": "formell", "richtig": 13, "fragen": 15}
    b1 = ids[ids.index("formell"):ids.index("formell") + 3]
    _pfad(seite, heute_stand(einstufung=alt, bestanden=b1))
    assert seite.js(DRAN) == {"dran": "kleine_woerter", "stufe": "A1", "neu": [True, True]}
    seite.js("() => { passed.add('kleine_woerter'); showHome(); }")
    assert seite.js(DRAN)["dran"] == "jeden_tag"
    seite.js("() => { passed.add('jeden_tag'); showHome(); }")
    assert seite.js(DRAN) == {"dran": ids[ids.index("formell") + 3], "stufe": "B1", "neu": [True, True]}
    # Eingestuft in A2 (bei "zukunft"): Kleine Wörter steht davor, Wörter für jeden Tag
    # kommt ohnehin in der Reihe
    _pfad(seite, heute_stand(einstufung=dict(alt, bis="zukunft"), bestanden=["zukunft"]))
    assert seite.js(DRAN)["dran"] == "kleine_woerter"
    seite.js("() => { passed.add('kleine_woerter'); showHome(); }")
    assert seite.js(DRAN)["dran"] == "modal"
    assert ids.index("jeden_tag") > ids.index("zukunft")
    assert seite.fehler == []


WEITER = """() => { const z = naechstesOffenes();
    return {ziel: CATEGORIES[z].id, offen: isUnlocked(z), knopf: weiterText(z)}; }"""


def test_alte_einstufung_ohne_bestandenes_bleibt_beim_einstieg(seite, heute_stand, ids):
    """Zweite Prüfung vom 13.11.2026: Wer in 1.3 eingestuft wurde und ab dem
    Einstieg noch nichts bestanden hat, bekam "Kleine Wörter" als dran - nach
    dem Bestehen sprang Weitermachen aber auf Level 1 ("basics"), denn
    hoechsterBestanden() lag jetzt vor dem Einstieg und hieß "lernt von
    vorn". Der Weiter-Knopf nach dem Test führte zu "Fälle 1". Jetzt zählen
    die Grundwort-Level dabei nicht mit."""
    import datetime
    tag = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    alt = {"tag": tag, "wahl": "gut", "bis": "formell", "richtig": 13, "fragen": 15}
    for bis in ("formell", "einkauf_orte"):
        _pfad(seite, heute_stand(einstufung=dict(alt, bis=bis)))
        assert seite.js(DRAN) == {"dran": "kleine_woerter", "stufe": "A1", "neu": [True, True]}, bis
        seite.js("() => { passed.add('kleine_woerter'); showHome(); }")
        assert seite.js(DRAN) == {"dran": "jeden_tag", "stufe": "A2", "neu": [True, True]}, bis
        seite.js("() => { passed.add('jeden_tag'); showHome(); }")
        assert seite.js(DRAN)["dran"] == bis
    # Der Weiter-Knopf nach dem Test geht denselben Weg: Kleine Wörter ->
    # Wörter für jeden Tag -> Einstieg, nicht in die übersprungenen Level
    _pfad(seite, heute_stand(einstufung=alt))
    seite.js("() => { catIdx = CATEGORIES.findIndex(c => c.id === 'kleine_woerter'); passed.add('kleine_woerter'); }")
    assert seite.js(WEITER) == {"ziel": "jeden_tag", "offen": True, "knopf": "Weiter zu A2 →"}
    seite.js("() => { catIdx = CATEGORIES.findIndex(c => c.id === 'jeden_tag'); passed.add('jeden_tag'); }")
    assert seite.js(WEITER) == {"ziel": "formell", "offen": True, "knopf": "Weiter zu B1 →"}
    # Im echten Test: Kleine Wörter bestehen, Weiter führt zu Wörter für jeden Tag
    _pfad(seite, heute_stand(einstufung=alt))
    seite.js("""() => { catIdx = CATEGORIES.findIndex(c => c.id === 'kleine_woerter');
        cur().words.forEach(w => known.add(w.id)); openLevel(catIdx); startTest(); }""")
    seite.durchspielen("tBody", "Tx")
    assert seite.js("() => document.getElementById('tNext').textContent") == "Weiter zu A2 →"
    seite.page.click("#tNext")
    assert seite.js("() => cur().id") == "jeden_tag"
    assert seite.js(DRAN)["dran"] == "jeden_tag"
    # In A2 eingestuft (bei "zukunft"): Kleine Wörter, dann der Einstieg
    _pfad(seite, heute_stand(einstufung=dict(alt, bis="zukunft")))
    assert seite.js(DRAN)["dran"] == "kleine_woerter"
    seite.js("() => { passed.add('kleine_woerter'); showHome(); }")
    # Wörter für jeden Tag steht hinter "zukunft" und kommt in der Reihe
    assert seite.js(DRAN) == {"dran": "zukunft", "stufe": "A2", "neu": [True, False]}
    assert seite.fehler == []


ZUHAUSE = ["kueche_bad", "putzen", "technik", "auto_werkstatt", "geraete"]


def test_alte_einstufung_bei_fragen_haelt_zuhause_offen(seite, heute_stand, ids):
    """Zweite Prüfung vom 13.11.2026: In 1.3 fragte Stufe 2 der Einstufung auch
    "Zuhause" ab; wer sie bestand, stieg bei "Fragen stellen" ein und hatte
    die fünf Zuhause-Level offen. Seit Zuhause hinter Fälle 1 steht, waren
    sie nach dem Update wieder zu und A2 mit ihnen. Jetzt bleiben sie offen,
    Weitermachen führt wie in 1.3 nicht hinein, und nach Fälle 1 geht es zu
    Fälle 2."""
    import datetime
    tag = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    alt = {"tag": tag, "wahl": "etwas", "bis": "fragen", "richtig": 7, "fragen": 9}
    offen = """() => { const k = id => CATEGORIES.findIndex(c => c.id === id);
        return {zuhause: %s.map(id => isUnlocked(k(id))), a2: stufeStand('A2').art,
                faelle1: isUnlocked(k('faelle1')), faelle2: isUnlocked(k('faelle2'))}; }""" % ZUHAUSE
    _pfad(seite, heute_stand(einstufung=alt))
    assert seite.js(offen) == {"zuhause": [True] * 5, "a2": "offen", "faelle1": False, "faelle2": False}
    assert seite.js(DRAN)["dran"] == "fragen"
    assert [b["art"] for b in seite.js(LEISTE)] == ["offen", "offen", "zu", "zu", "bald"]
    # Fragen stellen bis Fälle 1 bestanden: Fälle 2 ist offen und dran, Zuhause bleibt offen
    _pfad(seite, heute_stand(einstufung=alt, bestanden=ids[ids.index("fragen"):ids.index("faelle1") + 1]))
    assert seite.js(offen) == {"zuhause": [True] * 5, "a2": "offen", "faelle1": True, "faelle2": True}
    assert seite.js(DRAN)["dran"] == "faelle2"
    seite.js("() => { catIdx = CATEGORIES.findIndex(c => c.id === 'faelle1'); }")
    assert seite.js(WEITER)["ziel"] == "faelle2"
    # Eingestuft mit den Reitern bleibt es bei der Kette: Zuhause ist dort zu
    _pfad(seite, heute_stand(einstufung=dict(alt, reiter=True)))
    assert seite.js(offen) == {"zuhause": [False] * 5, "a2": "zu", "faelle1": False, "faelle2": False}
    # Andere alte Einstiege halten nichts zusaetzlich offen
    _pfad(seite, heute_stand(einstufung=dict(alt, bis="zukunft")))
    assert seite.js("() => isUnlocked(CATEGORIES.findIndex(c => c.id === 'modal'))") is False
    assert seite.fehler == []


def test_mit_den_reitern_eingestuft_bleibt_beim_einstieg(seite, heute_stand, ids):
    """Wer mit den Reitern eingestuft wird, hat A1 und A2 samt Grundwörtern
    übersprungen; der Ergebnisschirm sagt "Du steigst in B1 ein", und dabei
    bleibt Weitermachen. Die Level davor sind offen."""
    _pfad(seite, heute_stand())
    seite.js("() => { einstufungMerken('gut', 'formell', 13, 15); showHome(); }")
    assert seite.js("() => einstufung.reiter") is True
    assert seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand')).einstufung.reiter") is True
    assert seite.js(DRAN) == {"dran": "formell", "stufe": "B1", "neu": [True, True]}
    # Ein Sprung-Test ist auch ein Einstieg mit den Reitern
    _pfad(seite, heute_stand(wann={"sp:A2": "2026-11-13"}))
    assert seite.js(DRAN)["dran"] == ids[30]
    assert seite.fehler == []
