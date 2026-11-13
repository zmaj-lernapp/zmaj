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
  ist er vorbei und nicht bestanden;
- wer vor dem Update schon weiter war, verliert nichts: B1 bleibt fertig, die
  zwei neuen Grundwort-Level sind „dran“, angefangene Zuhause-Level bleiben offen.

Inhalt und Quelltext prüft tests/test_reiter.py ohne Browser."""
import pytest

STUFEN = ["A1", "A2", "B1", "B2", "C1"]

LEISTE = """() => [...document.querySelectorAll('#reiterLeiste button')].map(b => ({
  st: b.dataset.stufe, art: b.className, an: b.getAttribute('aria-selected') === 'true',
  text: b.querySelector('.sz').textContent.trim()}))"""

SEKTIONEN = """() => [...document.querySelectorAll('#sections .section')].map(s => ({
  titel: s.querySelector('h2').textContent, sek: s.className.match(/sek(\\d)/)[1]}))"""

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
    assert leiste[0]["text"] == "0 von 30"
    assert seite.js("() => document.getElementById('reiterKarte').hidden")
    sek = seite.js(SEKTIONEN)
    assert [s["titel"] for s in sek] == ["Sektion 1 · Grundlagen & Alltag", "Sektion 2 · Dinge zum Anfassen",
                                         "Sektion 3 · Tiere & Natur", "Sektion 4 · Sätze bauen 1"]
    assert [s["sek"] for s in sek] == ["1", "2", "3", "4"]
    assert seite.fehler == [] and seite.fremd == []


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
    seite.page.click("#sprungLos")
    # ohne Leben startet er nicht
    seite.page.click("#sprungStart")
    assert seite.js("() => sichtbar('pfad')")
    assert "Leben" in seite.page.locator("#sprungNote").text_content()
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
    assert [b["text"] for b in seite.js(LEISTE)][:3] == ["29 von 30", "30 von 31", "✓ fertig"]
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
