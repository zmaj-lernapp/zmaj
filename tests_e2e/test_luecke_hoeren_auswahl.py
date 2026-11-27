# -*- coding: utf-8 -*-
"""Zwei Ideen von Ajdin vom 27.11.2026, beide in Update 1.5.

1  Lueckensatz ("___ je plavo."): Nach "Prüfen" steht in der Loesung ein
   Knopf "Hören", der den ganzen Satz spielt. Ajdin: "nachdem man das
   ergebnis sehen möchte gibt es den knopf zum anhören". Vor dem Pruefen gibt
   es ihn nie (er verriete die Luecke), beim Hinweis "Fast richtig!" auch
   nicht, und ohne Aufnahme des ganzen Satzes auch nicht. Der Knopf spielt
   nichts von selbst; ein Tipp darauf spielt nur und blaettert nicht weiter.
   Er kommt in Lektion, Level-Test und Einstufung.
2  Auswahl (Was heisst ...?, Hoer-Auswahl, Was bedeutet ...?): Nach einer
   falschen Wahl steht hinter der Loesung, was das Gewaehlte heisst - "Richtig
   wäre: more · jezero = See". Ajdin: "man klickt jezero an aber es ist more
   richtig dann steht die antwort ist more jezero bedeutet see oder so".
   Bosnisch ist nur das Wort, die Bedeutung kommt in der Sprache der App, in
   allen acht. Gezaehlt wird wie vorher.

Beides in Chromium und WebKit, mit echten Klicks am Handy-Format, und das
Layout bei 375 und 360 Punkten Breite.
"""
import pytest
from conftest import Seite
from test_tippfehler import LEGEN, STARTEN

MOTOREN = ["chromium", "webkit"]
SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
FELD = {"Lx": "#lBody", "Tx": "#tBody", "Ex": "#eBody"}
NBSP = " "


@pytest.fixture(params=MOTOREN)
def motor(request, browser):
    """Chromium immer, WebKit nur wenn da (siehe conftest.py, webkit)."""
    return browser if request.param == "chromium" else request.getfixturevalue("webkit")


def _handy(motor, basis, stand, breite=375, hoehe=667, sprache="de"):
    ctx = motor.new_context(viewport={"width": breite, "height": hoehe}, device_scale_factor=2,
                            has_touch=True, is_mobile=True, locale="de-DE", service_workers="block")
    s = Seite(ctx.new_page(), basis)
    s.starten(stand=stand, sprache=sprache)
    # Der Vorspann liegt sonst ueber allem und faengt echte Klicks ab.
    s.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
    s.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    return ctx, s


@pytest.fixture
def handy(motor, basis, heute_stand):
    ctx, s = _handy(motor, basis, heute_stand())
    yield s
    ctx.close()


# Hoeren mitschreiben und trotzdem wirklich spielen lassen (der Ton ist in
# beiden Browsern stumm, siehe conftest.py).
SPRECHEN_MITSCHREIBEN = r"""() => {
  if(!window.__sprechSpion){
    window.__sprechSpion = true;
    const echt = speak;
    speak = (x, f) => { window.__speak.push(x); return echt(x, f); };
  }
  window.__speak = [];
}"""

# Was nach (oder vor) dem Pruefen in der Aufgabe steht.
HOEREN_LAGE = r"""(feld) => {
  const body = document.querySelector(feld), k = body.querySelector('.satzton');
  const text_ = sel => { const e = body.querySelector(sel); return e ? e.textContent : null; };
  return {knopf: !!k, text: k ? k.textContent.trim() : null,
          inLoesung: !!(k && k.closest('.loesung')), imAntwortfeld: !!(k && k.closest('.antwortfeld')),
          hoerKnoepfe: body.querySelectorAll('.listen').length,
          weiter: !!body.querySelector('.weiterbox'), fb: text_('#xFb'), klasse: (body.querySelector('#xFb') || {}).className,
          lbs: text_('.loesung .lbs'), lde: text_('.loesung .lde'),
          speak: (window.__speak || []).slice(), gesprochen: (window.__gesprochen || []).slice(),
          hoeren: t('task.hoeren'), i: body.dataset.i};
}"""


def _luecke_legen(s, art, ziel="___ je plavo.|Nebo"):
    """Lektion, Level-Test oder Einstufung starten und den Satz hineinlegen
    (LEGEN aus test_tippfehler.py schreibt Toene und spaeterSprechen mit)."""
    s.js(STARTEN[art])
    leben = s.js(LEGEN, [art, "gap", ziel])
    s.js(SPRECHEN_MITSCHREIBEN)
    return leben


def _pruefen(s, art, eingabe):
    feld = FELD[art]
    s.page.locator(feld + " #xIn").fill(eingabe)
    s.frisch_abwarten()
    s.page.locator(feld + " #xCheck").click()


@pytest.mark.parametrize("art", ["Lx", "Tx", "Ex"])
def test_luecke_hoeren_erst_nach_dem_pruefen(handy, art):
    s = handy
    _luecke_legen(s, art)
    vorher = s.js(HOEREN_LAGE, FELD[art])
    assert not vorher["knopf"] and vorher["hoerKnoepfe"] == 0, vorher    # nichts verraet die Luecke
    assert s.js("(f) => document.querySelector(f).innerText.indexOf('Nebo') < 0", FELD[art])
    assert s.js("() => !!audioDatei('Nebo je plavo.')"), "der Satz hat in der Demo eine Aufnahme"

    _pruefen(s, art, "Nebo")
    s.page.wait_for_selector(FELD[art] + " .weiterbox")
    lage = s.js(HOEREN_LAGE, FELD[art])
    assert lage["knopf"] and lage["inLoesung"] and lage["imAntwortfeld"], lage
    assert lage["text"] == lage["hoeren"] == "Hören", lage
    assert lage["lbs"] == "Nebo je plavo." and lage["lde"] == "Der Himmel ist blau.", lage
    # Kein Autoplay durch den Knopf: gesprochen wird nach der Antwort wie
    # bisher einmal (spaeterSprechen), speak() ruft erst der Tipp.
    assert lage["gesprochen"] == ["Nebo je plavo."] and lage["speak"] == [], lage

    # Erst nach WEITER_NACH haengt weiterBeiTipp() seinen Horcher an das Feld.
    # Ein Tipp auf Hoeren spielt dann nur, er blaettert nicht weiter.
    s.page.wait_for_timeout(1000)
    knopf = s.page.locator(FELD[art] + " .satzton")
    knopf.click()
    s.page.wait_for_timeout(300)
    nach = s.js(HOEREN_LAGE, FELD[art])
    assert nach["speak"] == ["Nebo je plavo."], nach
    assert nach["weiter"] and nach["knopf"] and nach["i"] == lage["i"], nach
    knopf.click()
    s.page.wait_for_timeout(200)
    assert s.js(HOEREN_LAGE, FELD[art])["speak"] == ["Nebo je plavo."] * 2
    assert s.fehler == [] and s.fremd == []


def test_luecke_hoeren_auch_nach_falsch(handy):
    s = handy
    leben = _luecke_legen(s, "Lx")
    _pruefen(s, "Lx", "Sunce")
    s.page.wait_for_selector("#lBody .weiterbox")
    lage = s.js(HOEREN_LAGE, "#lBody")
    assert "no" in lage["klasse"].split() and lage["fb"] == "Richtig wäre: Nebo", lage
    assert lage["knopf"] and lage["inLoesung"], lage
    assert s.js("() => livesNow()") == leben - 1           # gezaehlt wie immer
    s.page.wait_for_timeout(1000)
    s.page.locator("#lBody .satzton").click()
    s.page.wait_for_timeout(200)
    assert s.js(HOEREN_LAGE, "#lBody")["speak"] == ["Nebo je plavo."]
    assert s.fehler == []


def test_kein_knopf_beim_hinweis_fast_richtig(handy):
    """Der Hinweis ist noch kein Ergebnis - die Luecke ist weiter offen."""
    s = handy
    _luecke_legen(s, "Lx")
    _pruefen(s, "Lx", "Neba")
    s.page.wait_for_timeout(250)
    lage = s.js(HOEREN_LAGE, "#lBody")
    assert lage["fb"] == "Fast richtig!" and not lage["knopf"] and lage["hoerKnoepfe"] == 0, lage
    assert not lage["weiter"], lage
    assert s.fehler == []


def test_ohne_satzaufnahme_kein_knopf(handy):
    """Wie beim Vorlesen der Geschichten: ohne Aufnahme kein Knopf, auch wenn
    der Browser eine Computerstimme haette."""
    s = handy
    _luecke_legen(s, "Lx")
    s.js("() => { window.__weg = AUDIO.get('nebo je plavo.'); AUDIO.delete('nebo je plavo.'); }")
    try:
        _pruefen(s, "Lx", "Nebo")
        s.page.wait_for_selector("#lBody .weiterbox")
        lage = s.js(HOEREN_LAGE, "#lBody")
        assert not lage["knopf"] and lage["lbs"] == "Nebo je plavo.", lage
    finally:
        s.js("() => AUDIO.set('nebo je plavo.', window.__weg)")
    assert s.fehler == []


# Der laengste Lueckensatz mit Aufnahme, ohne wechselnde Zahl: Satz und
# Uebersetzung zusammen, damit die Loesung so hoch wie moeglich wird.
LAENGSTER_SATZ = r"""() => {
  const mit = SENTENCES.filter(s => !s.zahl && s.text.indexOf('___') >= 0 && s.answer.indexOf(' / ') < 0
                                     && audioDatei(s.text.replace('___', s.answer)));
  mit.sort((a, b) => (b.text.length + b.de.length) - (a.text.length + a.de.length));
  return mit[0].text + '|' + mit[0].answer;
}"""

# Liegt alles in der Karte, gibt es keine Seitwaertsbewegung, und steht
# Weiter (nach seinem scrollIntoView) im Bild?
LAYOUT = r"""(feld) => {
  const body = document.querySelector(feld), karte = body.closest('.card').getBoundingClientRect();
  const r = sel => { const e = body.querySelector(sel); if(!e) return null; const b = e.getBoundingClientRect();
                     return {l: b.left, r: b.right, o: b.top, u: b.bottom}; };
  return {breit: document.documentElement.scrollWidth, fenster: window.innerWidth, hoch: window.innerHeight,
          karte: {l: karte.left, r: karte.right}, knopf: r('.satzton'), loesung: r('.loesung'),
          fb: r('#xFb'), gewaehlt: r('#xFb .gewaehlt'), weiter: r('.weiterbox .btn')};
}"""


def _im_bild(lage, *teile):
    assert lage["breit"] <= lage["fenster"], lage                       # keine Seitwaertsbewegung
    for t in teile:
        b = lage[t]
        assert b, (t, lage)
        assert b["l"] >= lage["karte"]["l"] - 0.5 and b["r"] <= lage["karte"]["r"] + 0.5, (t, lage)
    w = lage["weiter"]
    assert w and w["o"] >= 0 and w["u"] <= lage["hoch"] + 0.5, lage      # Weiter im Bild


@pytest.mark.parametrize("breite, hoehe", [(375, 667), (360, 640)])
def test_luecke_layout_am_schmalen_handy(motor, basis, heute_stand, breite, hoehe):
    ctx, s = _handy(motor, basis, heute_stand(), breite, hoehe)
    try:
        ziel = s.js(LAENGSTER_SATZ)
        _luecke_legen(s, "Lx", ziel)
        _pruefen(s, "Lx", "xyz")                     # falsch: mit Rueckmeldung "Richtig wäre: ..."
        s.page.wait_for_selector("#lBody .weiterbox")
        s.page.wait_for_timeout(900)                 # Weiter rollt sanft ins Bild
        lage = s.js(LAYOUT, "#lBody")
        _im_bild(lage, "knopf", "loesung", "fb")
        k, l, w = lage["knopf"], lage["loesung"], lage["weiter"]
        assert l["o"] <= k["o"] and k["u"] <= l["u"], lage                 # in der Loesung
        assert k["u"] <= w["o"], lage                                        # nicht ueber Weiter
        assert s.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# 2  Falsche Wahl: was das Gewaehlte heisst
# ---------------------------------------------------------------------------

# Eine Auswahl mit festen Knoepfen: das Ziel und genau drei andere Woerter
# (distractors() nimmt aus einem Vorrat mit drei Woertern alle drei).
AUSWAHL_LEGEN = r"""([typ, ziel, vorrat]) => {
  openLevel(0); startLesson();
  const f = wortNachId(ziel);
  if(!f) throw new Error('kein Wort ' + ziel);
  const pool = vorrat.map(id => { const x = wortNachId(id); if(!x) throw new Error('kein Wort ' + id); return x.w; });
  if(!window.__spion2){
    window.__spion2 = true;
    sound = k => { window.__toene.push(k); };
    spaeterSprechen = x => { window.__gesprochen.push(x); };
  }
  window.__toene = []; window.__gesprochen = [];
  Lx.queue = [{typ, w: f.w, pool: [f.w, ...pool]}]; Lx.i = 0; Lx.total = 1;
  showLessonTask();
  const de = id => wortNachId(id).w.de;
  return {knoepfe: [...document.querySelectorAll('#lBody .opt')].map(b => b.textContent),
          leben: livesNow(), ziel: {bs: f.w.bs, de: f.w.de},
          andere: vorrat.map(id => ({bs: wortNachId(id).w.bs, de: de(id)})),
          falsch: t('task.falsch', {wort: typ === 'mcrev' ? f.w.de : f.w.bs})};
}"""

AUSWAHL_LAGE = r"""() => {
  const fb = document.querySelector('#lBody #xFb'), g = fb.querySelector('.gewaehlt');
  return {text: fb.textContent, html: fb.innerHTML, klasse: fb.className, gewaehlt: !!g,
          gewaehltBs: g ? [...g.querySelectorAll('[lang]')].map(e => [e.getAttribute('lang'), e.textContent]) : [],
          gewaehltLang: g ? g.getAttribute('lang') : null,
          ergebnis: Lx.results[0], leben: livesNow(), toene: window.__toene.slice(),
          loesung: (document.querySelector('#lBody .loesung .lbs') || {}).textContent || null,
          ansage: document.getElementById('ansage').textContent};
}"""

MEER = ("meer:more", ["see:jezero", "fluss:rijeka", "berg:planina"])


def _antippen(s, text):
    s.frisch_abwarten()
    b = s.page.locator("#lBody .opt").filter(has_text=text)
    knopf = [i for i in range(b.count()) if b.nth(i).text_content() == text]
    assert len(knopf) == 1, (text, b.all_text_contents())
    b.nth(knopf[0]).click()


@pytest.mark.parametrize("typ, tippen, soll", [
    ("mc", "jezero", "Richtig wäre: more · jezero = See"),
    ("listen", "jezero", "Richtig wäre: more · jezero = See"),
    ("mcrev", "See", "Richtig wäre: Meer · jezero = See"),
])
def test_falsche_wahl_nennt_was_das_gewaehlte_heisst(handy, typ, tippen, soll):
    s = handy
    a = s.js(AUSWAHL_LEGEN, [typ, MEER[0], MEER[1]])
    erwartet = {"more", "jezero", "rijeka", "planina"} if typ != "mcrev" else {"Meer", "See", "Fluss", "Berg"}
    assert set(a["knoepfe"]) == erwartet, a
    _antippen(s, tippen)
    s.page.wait_for_selector("#lBody .weiterbox")
    lage = s.js(AUSWAHL_LAGE)
    assert lage["text"].replace(NBSP, " ") == soll, lage
    assert NBSP + "· " in lage["text"], lage               # der Punkt bricht nie allein in die naechste Zeile
    # Nur das Wort ist bosnisch, die Bedeutung ist in der Sprache der App.
    assert lage["gewaehltBs"] == [["bs", "jezero"]] and lage["gewaehltLang"] is None, lage
    # Sichtbar auch so, wie es auf dem Bildschirm steht.
    assert s.page.locator("#lBody #xFb").inner_text().replace(NBSP, " ").strip() == soll
    # Gezaehlt wie vorher: falsch, ein Leben weniger, der Fehlerton.
    assert lage["ergebnis"] is False and lage["leben"] == a["leben"] - 1 and lage["toene"] == ["no"], lage
    assert "no" in lage["klasse"].split() and lage["loesung"] == "more", lage
    # Angesagt wird das Ganze, mit dem Wort darin.
    s.page.wait_for_function("() => document.getElementById('ansage').textContent.indexOf('jezero = See') >= 0",
                             timeout=5000)
    assert s.fehler == [] and s.fremd == []


@pytest.mark.parametrize("typ, tippen", [("mc", "more"), ("listen", "more"), ("mcrev", "Meer")])
def test_richtige_wahl_ohne_zusatz(handy, typ, tippen):
    s = handy
    a = s.js(AUSWAHL_LEGEN, [typ, MEER[0], MEER[1]])
    _antippen(s, tippen)
    s.page.wait_for_selector("#lBody .weiterbox")
    lage = s.js(AUSWAHL_LAGE)
    assert lage["text"] == "Tačno! ✓" and not lage["gewaehlt"], lage
    assert lage["ergebnis"] is True and lage["leben"] == a["leben"], lage
    assert s.fehler == []


def test_grammatik_und_kacheln_bleiben_wie_sie_sind(seite, heute_stand):
    """Bei der Grammatik sind die Knoepfe Formen ohne eigene Bedeutung, bei
    den Kacheln gibt es keinen einen gewaehlten Knopf: dort kommt nichts dazu."""
    seite.starten(stand=heute_stand())
    r = seite.js("""() => {
      openLevel(0); startLesson();
      sound = () => {}; spaeterSprechen = () => {};
      const g = Object.values(GRAMMAR).flatMap(l => (l || {}).uebungen || [])
                  .find(u => u.optionen && u.optionen.length > 1 && u.frage);
      Lx.queue = [{typ: 'gram', g}]; Lx.i = 0; Lx.total = 1;
      showLessonTask();
      const falsch = [...document.querySelectorAll('#lBody .opt')].find(b => b.textContent !== g.richtig);
      falsch.click();
      const fb = document.querySelector('#lBody #xFb');
      return {text: fb.textContent, gewaehlt: !!fb.querySelector('.gewaehlt'), richtig: g.richtig,
              soll: t('task.falsch', {wort: g.richtig})};
    }""")
    assert not r["gewaehlt"] and r["text"] == r["soll"], r
    assert seite.fehler == []


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_falsche_wahl_in_allen_sprachen(browser, basis, heute_stand, sprache):
    """In jeder Sprache: der Satz der App fuer die Loesung, dahinter das Wort
    und seine Bedeutung in dieser Sprache - nie die deutsche, ausser auf
    Deutsch. Am Handy mit 375 Punkten passt alles in die Karte."""
    ctx, s = _handy(browser, basis, heute_stand(), 375, 667, sprache)
    try:
        assert s.js("() => document.documentElement.lang") == sprache
        for typ in ("mc", "mcrev"):
            a = s.js(AUSWAHL_LEGEN, [typ, MEER[0], MEER[1]])
            jezero = a["andere"][0]
            assert jezero["bs"] == "jezero", a
            if sprache != "de":
                assert jezero["de"] != "See" and a["ziel"]["de"] != "Meer", a     # uebersetzt
            _antippen(s, "jezero" if typ == "mc" else jezero["de"])
            s.page.wait_for_selector("#lBody .weiterbox")
            lage = s.js(AUSWAHL_LAGE)
            soll = a["falsch"] + NBSP + "· jezero = " + jezero["de"]
            assert lage["text"] == soll, (typ, lage, soll)
            assert lage["gewaehltBs"] == [["bs", "jezero"]], lage
            s.page.wait_for_timeout(900)
            _im_bild(s.js(LAYOUT, "#lBody"), "fb", "gewaehlt")
        assert s.fehler == []
    finally:
        ctx.close()


# Die laengsten Saetze eines Levels als Knoepfe: das Ziel und drei andere
# mit verschiedener Bedeutung. Saetze, damit distractors() sie zuerst nimmt.
LANGE_SAETZE = r"""() => {
  const alle = CATEGORIES.flatMap(c => c.words).filter(w => !istWort(grundBedeutung(w)));
  alle.sort((a, b) => (b.bs.length + b.de.length) - (a.bs.length + a.de.length));
  const out = [], bed = new Set();
  for(const w of alle){
    if(out.length === 4) break;
    if(bed.has(w.de) || out.some(x => geschwister(x).some(g => g.bs === w.bs))) continue;
    bed.add(w.de); out.push(w.id);
  }
  return out;
}"""


@pytest.mark.parametrize("breite, hoehe", [(375, 667), (360, 640)])
@pytest.mark.parametrize("sprache", ["de", "fr"])
def test_falsche_wahl_layout_mit_langen_saetzen(motor, basis, heute_stand, breite, hoehe, sprache):
    ctx, s = _handy(motor, basis, heute_stand(), breite, hoehe, sprache)
    try:
        ids = s.js(LANGE_SAETZE)
        assert len(ids) == 4, ids
        for typ in ("mc", "mcrev"):
            a = s.js(AUSWAHL_LEGEN, [typ, ids[0], ids[1:]])
            ziel = a["ziel"]["de"] if typ == "mcrev" else a["ziel"]["bs"]
            falsch = next(k for k in a["knoepfe"] if k != ziel)
            _antippen(s, falsch)
            s.page.wait_for_selector("#lBody .weiterbox")
            s.page.wait_for_timeout(900)
            lage = s.js(LAYOUT, "#lBody")
            _im_bild(lage, "fb", "gewaehlt")
            assert s.js(AUSWAHL_LAGE)["gewaehlt"]
        assert s.fehler == []
    finally:
        ctx.close()
