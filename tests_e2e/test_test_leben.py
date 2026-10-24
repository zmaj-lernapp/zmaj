# -*- coding: utf-8 -*-
"""Der Level-Test kostet Leben - genau wie die Lektion (19.10.2026).

Ajdin: "ich wuerde sagen das der test doch leben kosten soll". Bis dahin
kostete der Test nichts, und sein Herz war ein unsichtbarer Platzhalter, der
nur die Hoehe der Kopfzeile freihielt (test_layout_test.py). Jetzt gilt im
Test, was in der Lektion gilt:

- eine falsche Antwort kostet ein Leben, eine richtige nicht, und das Herz
  im Fragenkasten ist echt, sichtbar und zaehlt mit;
- ohne Leben startet kein Test - derselbe Hinweis, dieselben Wege zu einem
  Leben wie beim Lektionsknopf;
- bei null Leben mitten im Test kommt derselbe Schirm wie in der Lektion.
  Danach ist der Test vorbei und nicht bestanden: mit einem neuen Leben
  (Muenzen oder Video) geht es wie in der Lektion zur Level-Uebersicht, und
  der naechste Test faengt von vorn an;
- mit der Vollversion kostet nichts ein Leben;
- die Einstufung beim ersten Start kostet weiter keine Leben und zeigt
  weiter kein Herz.

Die Aufgaben legt der Test selbst fest (eine Auswahlaufgabe aus Level 1),
damit "falsch" sicher falsch ist und nicht vom Zufall der Fragen abhaengt.
Angetippt wird mit echten Klicks.
"""
import time

# Level 1 ganz gewusst, damit der Test frei ist, dann starten.
TEST_STARTEN = "() => { CATEGORIES[0].words.forEach(x => known.add(x.id)); openLevel(0); startTest(); }"
LEKTION_STARTEN = "() => { openLevel(0); startLesson(); }"

# Die laufende Aufgabe durch eine feste Auswahlaufgabe ersetzen, richtig
# oder falsch antippen und warten, bis Weiter steht. art: Lx, Tx oder Ex.
ANTWORTEN = r"""
async ([feld, art, richtig]) => {
  const X = art === 'Lx' ? Lx : (art === 'Tx' ? Tx : Ex);
  const body = document.getElementById(feld);
  const warte = ms => new Promise(r => setTimeout(r, ms));
  const bis = async (bed, was) => {
    const ende = Date.now() + 8000;
    while(!bed()){ if(Date.now() > ende) throw new Error('wartet vergeblich auf: ' + was); await warte(15); }
  };
  const i = X.i, c0 = CATEGORIES[0];
  const task = {typ: 'mc', w: c0.words[i % c0.words.length], pool: c0.words};
  if(art === 'Tx'){ Tx.qs[i] = task; showTestQ(); }
  else if(art === 'Lx'){ Lx.queue[i] = task; showLessonTask(); }
  else { Ex.qs[i] = task; einstufungFrageZeigen(); }
  await bis(() => body.dataset.i === String(i) && body.querySelector('.opt') && !body.querySelector('.weiterbox'), 'Aufgabe ' + i);
  const b = [...body.querySelectorAll('.opt')].find(o => richtig ? o.textContent === task.w.bs : o.textContent !== task.w.bs);
  if(!b) throw new Error('kein passender Knopf bei ' + task.w.bs);
  b.click();
  await bis(() => X.i > i, 'Antwort auf ' + i);
  await bis(() => !!body.querySelector('.weiterbox .btn'), 'Weiter nach ' + i);
}
"""

WEITER = r"""
async (feld) => {
  const body = document.getElementById(feld);
  body.querySelector('.weiterbox .btn').click();
  const ende = Date.now() + 5000;
  while(body.querySelector('.weiterbox')){ if(Date.now() > ende) throw new Error('Weiter tut nichts'); await new Promise(r => setTimeout(r, 15)); }
}
"""

# Was man gerade sieht: Leben, die beiden Herzen im Fragenkasten, welcher
# Teil der Levelansicht offen ist.
LAGE = r"""
() => {
  // Seit dem 24.10.2026 ist das Herz ein Bild (web/symbole/herz.webp) und
  // steht nicht mehr im Text. mitHerz() schreibt es wieder als ♥ davor -
  // aber nur, wenn das gemalte Herz wirklich da ist.
  const mitHerz = e => (e.querySelector('img.sym-herz') ? '♥' : '') + e.textContent;
  const herz = id => {
    const e = document.getElementById(id);
    return {text: mitHerz(e), null_: e.classList.contains('zero'),
            sichtbar: e.getClientRects().length > 0 && getComputedStyle(e).visibility === 'visible'};
  };
  let gespeichert = null;
  try{ gespeichert = JSON.parse(localStorage.getItem('zmaj_stand')).leben.anzahl; }catch(e){}
  return {leben: livesNow(), gespeichert, tHerz: herz('tHerz'), lHerz: herz('lHerz'),
          test: sichtbar('test'), lektion: sichtbar('lesson'), uebersicht: sichtbar('levelHome'),
          tx: Tx ? {i: Tx.i, n: Tx.qs.length, results: Tx.results.slice()} : null,
          bestanden: passed.has(CATEGORIES[0].id), nachfrage: !!document.querySelector('.nachfrage')};
}
"""

# Der Schirm ohne Leben, so beschrieben, dass Lektion und Test vergleichbar
# sind. Ziffern fallen weg: die Wartezeit kann um eine Minute springen.
SCHIRM = r"""
(feld) => {
  const b = document.getElementById(feld), sec = b.closest('section');
  const txt = e => e ? e.textContent : null;
  // Das grosse Herz ist seit dem 24.10.2026 ein Bild, siehe LAGE
  const mitHerz = e => e ? (e.querySelector('img.sym-herz') ? '♥' : '') + e.textContent : null;
  return {
    titel: txt(b.querySelector('.ergebnis-titel')),
    gross: mitHerz(b.querySelector('.result-big.fail.ohneleben')),
    weinen: !!b.querySelector('.celebrate .zmaj.sad'),
    zeilen: [...b.querySelectorAll('.feedback')].filter(e => e.style.display !== 'none').map(txt),
    stats: [...b.querySelectorAll('.stat')].map(e => txt(e).replace(/[0-9]+/g, '#')),
    knoepfe: [...b.querySelectorAll('button')].map(e => e.id + ':' + txt(e)),
    punkte: sec.querySelector('.tbar').innerHTML,
    herz_weg: sec.querySelector('.kastenherz').style.display === 'none',
    drache_weg: sec.querySelector('.zmaj.mini').style.display === 'none',
  };
}
"""


def _jetzt_ms():
    return int(time.time() * 1000)


def test_falsche_antwort_im_test_kostet_ein_leben(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(TEST_STARTEN)
    lage = seite.js(LAGE)
    assert lage["test"] and lage["leben"] == 5
    assert lage["tHerz"] == {"text": "♥ 5", "null_": False, "sichtbar": True}, lage["tHerz"]

    seite.js(ANTWORTEN, ["tBody", "Tx", True])
    lage = seite.js(LAGE)
    assert lage["leben"] == 5 and lage["tHerz"]["text"] == "♥ 5", "eine richtige Antwort darf kein Leben kosten"
    seite.js(WEITER, "tBody")

    seite.js(ANTWORTEN, ["tBody", "Tx", False])
    lage = seite.js(LAGE)
    assert lage["leben"] == 4 and lage["gespeichert"] == 4
    assert lage["tHerz"] == {"text": "♥ 4", "null_": False, "sichtbar": True}, lage["tHerz"]
    # Das Herz zaehlt schon waehrend der Rueckmeldung, nicht erst danach -
    # wie in der Lektion, wo loseLife() selbst renderLives() ruft.
    seite.js(WEITER, "tBody")
    lage = seite.js(LAGE)
    assert lage["test"] and lage["tx"]["i"] == 2 and lage["tx"]["results"] == [True, False]
    assert lage["tHerz"]["text"] == "♥ 4" and lage["tHerz"]["sichtbar"]
    assert seite.fehler == [], seite.fehler


def test_ohne_leben_startet_kein_test(seite, heute_stand):
    # Mit Muenzen, damit unter dem Hinweis auch ein Weg zu einem Leben steht
    seite.starten(stand=heute_stand(leben={"anzahl": 0, "zeit": _jetzt_ms()}, muenzen_ges=500, muenzen_aus=0))
    knoepfe ="() => ({lektion: $('btnLesson').disabled, test: $('btnTest').disabled})"
    gesperrt = r"""
    (start) => {
      showLevelHome();
      (start === 'test' ? startTest : startLesson)();
      return {note: $('lvNote').textContent, wege: $('lvLeben').style.display, wege_html: $('lvLeben').innerHTML,
              test: sichtbar('test'), lektion: sichtbar('lesson'), uebersicht: sichtbar('levelHome')};
    }"""
    seite.js("() => { CATEGORIES[0].words.forEach(x => known.add(x.id)); openLevel(0); }")
    assert seite.js(knoepfe) == {"lektion": True, "test": True}, "ohne Leben muss auch der Test-Knopf gesperrt sein"

    lektion = seite.js(gesperrt, "lektion")
    test = seite.js(gesperrt, "test")
    assert not test["test"] and test["uebersicht"]
    assert "Keine Leben mehr" in test["note"]
    assert test["wege"] == "flex" and 'id="lvCoin"' in test["wege_html"], test
    assert test == lektion, "ohne Leben verhaelt sich der Test anders als die Lektion"
    assert seite.js(LAGE)["leben"] == 0

    # Waechst ein Leben nach, geht der Knopf wieder auf - auch ohne neue Uebersicht.
    seite.js("() => { lives = {anzahl: 1, zeit: Date.now()}; renderLives(); }")
    assert seite.js(knoepfe) == {"lektion": False, "test": False}
    assert seite.fehler == [], seite.fehler


def _bis_null(seite, art, feld):
    """Mit einem Leben falsch antworten und Weiter tippen."""
    seite.js(ANTWORTEN, [feld, art, False])
    lage = seite.js(LAGE)
    herz = lage["tHerz" if art == "Tx" else "lHerz"]
    assert lage["leben"] == 0 and herz == {"text": "♥ 0", "null_": True, "sichtbar": True}, herz
    seite.js(WEITER, feld)
    return seite.js(SCHIRM, feld)


def test_null_leben_mitten_im_test_wie_in_der_lektion(seite, heute_stand):
    stand = heute_stand(leben={"anzahl": 1, "zeit": _jetzt_ms()}, muenzen_ges=500, muenzen_aus=0)

    # Erst die Lektion als Vorlage
    seite.starten(stand=stand)
    seite.js(LEKTION_STARTEN)
    lektion = _bis_null(seite, "Lx", "lBody")

    # Dann der Test auf einer frischen Seite (der Hinweis auf die Vollversion
    # kommt bei jedem dritten Mal - beide sollen das erste Mal sein)
    seite.starten(stand=stand)
    seite.js(TEST_STARTEN)
    werbung_vorher = seite.js("() => werbungZaehler")
    test = _bis_null(seite, "Tx", "tBody")

    assert lektion["titel"] == "Lektion abgebrochen"
    assert test["titel"].startswith("Level 1 ·"), test["titel"]
    assert test["gross"] == "♥ 0"
    assert {k: v for k, v in test.items() if k != "titel"} == {k: v for k, v in lektion.items() if k != "titel"}, \
        "der Schirm ohne Leben sieht im Test anders aus als in der Lektion:\n%s\n%s" % (test, lektion)
    assert test["herz_weg"] and test["drache_weg"] and test["punkte"] == ""
    assert any(k.startswith("lCoin:") for k in test["knoepfe"]), test["knoepfe"]

    lage = seite.js(LAGE)
    assert lage["tx"]["i"] == lage["tx"]["n"], "der Test muss hier vorbei sein"
    assert not lage["bestanden"]
    assert seite.js("() => werbungZaehler") == werbung_vorher, "nach dem Schirm ohne Leben kommt keine Anzeige"
    # Nichts mehr abzubrechen: die Zurueck-Taste fragt nicht nach.
    assert seite.js("async () => await Promise.race([lektionDarfWeg(), new Promise(r => setTimeout(() => r('fragt'), 1500))])") is True

    # Leben fuer Muenzen: zur Uebersicht, der Test ist verloren und faengt neu an
    seite.page.click("#lCoin")
    lage = seite.js(LAGE)
    assert lage["uebersicht"] and not lage["test"] and lage["leben"] == 1 and not lage["bestanden"]
    assert seite.js("() => $('btnTest').disabled") is False
    seite.page.click("#btnTest")
    lage = seite.js(LAGE)
    assert lage["test"] and lage["tx"]["i"] == 0 and lage["tx"]["results"] == []
    assert lage["tHerz"] == {"text": "♥ 1", "null_": False, "sichtbar": True}
    assert seite.fehler == [], seite.fehler


def test_schirm_ohne_leben_im_test_raeumt_sich_weg(seite, heute_stand):
    """Wie in der Lektion: Video ansehen fuehrt zur Uebersicht, ebenso ein
    Leben, das nachwaechst, waehrend der Schirm steht (ohneLebenVorbei).
    Die Demo hat keine Werbung - die Anzeige wird hier ersetzt."""
    seite.starten(stand=heute_stand(leben={"anzahl": 1, "zeit": _jetzt_ms()}))
    seite.js(TEST_STARTEN)
    seite.js("() => { werbungErlaubt = () => true; zeigeWerbung = (belohnt, fertig) => fertig(true); }")
    schirm = _bis_null(seite, "Tx", "tBody")
    assert any(k.startswith("lAd:") for k in schirm["knoepfe"]), schirm["knoepfe"]
    seite.page.click("#lAd")
    lage = seite.js(LAGE)
    assert lage["uebersicht"] and not lage["test"] and lage["leben"] == 1 and not lage["bestanden"]

    # Nachwachsen: lives von Hand zurueck auf 1, dann der 30-Sekunden-Takt
    seite.js("() => { lives = {anzahl: 1, zeit: Date.now()}; startTest(); }")
    _bis_null(seite, "Tx", "tBody")
    seite.js("() => { lives = {anzahl: 1, zeit: Date.now()}; ohneLebenVorbei(); }")
    lage = seite.js(LAGE)
    assert lage["uebersicht"] and not lage["test"]

    # Ein nicht bestandenes Testergebnis traegt auch .result-big.fail - das
    # darf der Takt nicht fuer den Schirm ohne Leben halten.
    seite.js("() => { lives = {anzahl: 5, zeit: 0}; startTest(); Tx.i = Tx.qs.length; Tx.right = 0; showTestQ(); ohneLebenVorbei(); }")
    lage = seite.js(LAGE)
    assert lage["test"] and seite.js("() => !!document.querySelector('#tBody .result-big.fail')")
    assert seite.fehler == [], seite.fehler


def test_wenige_leben_weniger_fehler_frei(seite, heute_stand):
    """Die volle Folge von "genau wie in der Lektion": der Test endet beim
    letzten Leben, egal bei welcher Frage. Mit 1 Leben ist kein Fehler frei,
    mit 2 Leben nur einer - obwohl TEST_BESTANDEN_AB zwei erlaubt. Ab
    3 Leben besteht man mit 8 von 10 wie bisher.
    Bewusst so gelassen (Pruefung am 19.10.2026). Ajdin entscheidet noch, ob
    es dabei bleibt - entscheidet er anders, sind A und B hier umzudrehen."""
    def spielen(leben, folge):
        seite.starten(stand=heute_stand(leben={"anzahl": leben, "zeit": _jetzt_ms()}))
        seite.js(TEST_STARTEN)
        for richtig in folge:
            seite.js(ANTWORTEN, ["tBody", "Tx", richtig])
            seite.js(WEITER, "tBody")
        return seite.js("""() => ({ohneleben: !!document.querySelector('#tBody .ohneleben'),
            ergebnis: (document.querySelector('#tBody .result-big:not(.ohneleben)') || {}).textContent || null,
            i: Tx.i, n: Tx.qs.length, right: Tx.right, bestanden: passed.has(CATEGORIES[0].id),
            leben: lives.anzahl, grenze: TEST_BESTANDEN_AB})""")

    # A: 2 Leben, die ersten beiden falsch - vorbei, obwohl 8 von 10 noch ging
    a = spielen(2, [False, False])
    assert a["grenze"] == 8 and a["n"] == 10
    assert a["ohneleben"] and a["i"] == a["n"] and a["right"] == 0 and not a["bestanden"], a

    # B: 1 Leben, 9 richtig, die letzte falsch - 9 von 10 und nicht bestanden
    b = spielen(1, [True] * 9 + [False])
    assert b["ohneleben"] and b["right"] == 9 and not b["bestanden"] and b["ergebnis"] is None, b

    # C: 3 Leben, zwei Fehler - bestanden mit 8 von 10, ein Leben bleibt
    c = spielen(3, [False, False] + [True] * 8)
    assert not c["ohneleben"] and c["ergebnis"] == "8 / 10" and c["bestanden"] and c["leben"] == 1, c
    assert seite.fehler == [], seite.fehler


def test_vollversion_test_kostet_nichts(seite, heute_stand):
    seite.starten(stand=heute_stand(leben={"anzahl": 1, "zeit": _jetzt_ms()}))
    seite.js("() => { vollversionMerken(true); renderLives(); }")
    seite.js(TEST_STARTEN)
    for _ in range(3):
        seite.js(ANTWORTEN, ["tBody", "Tx", False])
        seite.js(WEITER, "tBody")
    lage = seite.js(LAGE)
    assert lage["test"] and lage["tx"]["i"] == 3 and lage["tx"]["results"] == [False, False, False]
    assert lage["tHerz"] == {"text": "♥ ∞", "null_": False, "sichtbar": True}, lage["tHerz"]
    assert seite.js("() => lives.anzahl") == 1, "mit der Vollversion darf kein Leben verloren gehen"
    assert seite.fehler == [], seite.fehler


def test_einstufung_kostet_nichts_und_zeigt_kein_herz(seite, heute_stand):
    seite.starten(stand=heute_stand(leben={"anzahl": 2, "zeit": _jetzt_ms()}))
    seite.js("() => { baueEinstufung('etwas'); einstufungStarten(); }")
    for _ in range(2):
        seite.js(ANTWORTEN, ["eBody", "Ex", False])
        seite.js(WEITER, "eBody")
    info = seite.js(r"""() => {
      const h = document.querySelector('#einstufungView .kastenherz');
      return {leben: lives.anzahl, platzhalter: h.classList.contains('platzhalter'),
              unsichtbar: getComputedStyle(h).visibility, fehler: Ex.fehler,
              echte: document.querySelectorAll('#einstufungView .kastenherz:not(.platzhalter)').length};
    }""")
    assert info == {"leben": 2, "platzhalter": True, "unsichtbar": "hidden", "fehler": 2, "echte": 0}, info
    assert seite.fehler == [], seite.fehler
