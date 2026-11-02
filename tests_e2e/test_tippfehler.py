# -*- coding: utf-8 -*-
"""Fast richtig: erst ein Hinweis, nicht gleich falsch (24.10.2026).

Ajdin: "wenn man beim schreiben ausversehen einen buchstaben falsch
geschrieben hat dann soll ein hinweis kommen das wort ist falsch geschrieben
und nicht das es direkt falsch ist weil sowas schnell passieren kann".
Gewaehlt hat er Vorschlag B:

- genau EIN Tippfehler gegen eine richtige Antwort (ein Buchstabe ersetzt,
  einer fehlt, einer zu viel, zwei Nachbarn vertauscht) gibt einen gelben
  Hinweis, ohne die Loesung zu verraten;
- die Eingabe bleibt offen, fokussiert und behaelt ihren Text;
- der zweite Versuch zaehlt wie immer, ein zweiter Hinweis kommt nicht;
- der Hinweis kostet kein Leben und spielt keinen Ton;
- erst ab 4 Buchstaben der Antwort;
- fehlen nur Haekchen, ist es wie bisher sofort "fast richtig".

Am 27.10.2026 kam im Lueckensatz die andere Endung dazu (Ajdin: "Auch bei
Endung Hinweis"), zuerst mit eigenem Text. Noch am selben Tag: "mach doch
einfach nur fast richtig dann bezieht es sich auf alle woerter und wenn es
ein andere wort ist ist doch egal es ist doch trotzdem fast richtig". Seitdem
gibt es einen Text, "Fast richtig!", fuer jede Eingabe einen Tippfehler
neben der Antwort - auch fuer eine andere Endung und fuer ein anderes
echtes Wort ("deset" fuer "devet", "zvono" fuer "zvoni"). Die Tests zur
Endung stehen am Ende.

Die Aufgaben legt der Test selbst fest, damit nichts vom Zufall der Lektion
abhaengt. Ton und Sprechen werden nur mitgeschrieben, nicht abgespielt.
"""
import pytest

HINWEIS = "Fast richtig!"
HINWEIS_EN = "Almost right!"

# Wie Android "Schriftgroesse": jede berechnete Schriftgroesse mal f (aus
# test_flamme.py). Erst alle lesen, dann schreiben.
SCHRIFT = """(f) => { const els = [...document.querySelectorAll('body *')];
  const g = els.map(e => parseFloat(getComputedStyle(e).fontSize));
  els.forEach((e, i) => e.style.fontSize = (g[i] * f) + 'px'); }"""

# Lektion, Level-Test oder Einstufung starten. Beim Test ist das Level ganz
# gewusst, damit er frei ist.
STARTEN = {
    "Lx": "() => { openLevel(0); startLesson(); }",
    "Tx": "() => { CATEGORIES[0].words.forEach(x => known.add(x.id)); openLevel(0); startTest(); }",
    "Ex": "() => { baueEinstufung('etwas'); einstufungStarten(); }",
}

# Die laufende Aufgabe durch eine feste ersetzen. ziel ist bei 'type' die
# Kennung des Worts, bei 'gap' "Satz|Antwort". Steht von der vorigen noch
# Weiter da, wird es erst angetippt - wie beim Lernen. Ton und Sprechen
# werden mitgeschrieben statt abgespielt.
LEGEN = r"""
async ([art, typ, ziel]) => {
  const X = art === 'Lx' ? Lx : (art === 'Tx' ? Tx : Ex);
  const body = document.getElementById({Lx: 'lBody', Tx: 'tBody', Ex: 'eBody'}[art]);
  const warte = ms => new Promise(r => setTimeout(r, ms));
  const weiter = body.querySelector('.weiterbox .btn');
  if(weiter){
    weiter.click();
    const bis = Date.now() + 5000;
    while(body.querySelector('.weiterbox')){ if(Date.now() > bis) throw new Error('Weiter tut nichts'); await warte(15); }
  }
  if(!window.__spion){
    window.__spion = true;
    sound = k => { window.__toene.push(k); };
    spaeterSprechen = x => { window.__gesprochen.push(x); };
  }
  window.__toene = []; window.__gesprochen = [];
  let task;
  if(typ === 'gap'){
    const [text, antwort] = ziel.split('|');
    task = {typ: 'gap', s: SENTENCES.find(x => x.text === text && x.answer === antwort)};
    if(!task.s) throw new Error('kein Satz ' + ziel);
  } else {
    const f = wortNachId(ziel);
    if(!f) throw new Error('kein Wort ' + ziel);
    task = {typ: 'type', w: f.w, pool: f.c.words};
  }
  const i = X.i;
  window.__art = art; window.__i = i;
  if(art === 'Tx'){ Tx.qs[i] = task; showTestQ(); }
  else if(art === 'Lx'){ Lx.queue[i] = task; showLessonTask(); }
  else { Ex.qs[i] = task; einstufungFrageZeigen(); }
  const ende = Date.now() + 8000;
  while(!(body.dataset.i === String(i) && body.querySelector('#xIn') && !body.querySelector('.weiterbox'))){
    if(Date.now() > ende) throw new Error('Aufgabe kommt nicht'); await warte(15);
  }
  return livesNow();
}
"""

# Was man gerade sieht und was gezaehlt ist.
LAGE = r"""
(loesung) => {
  const art = window.__art, X = art === 'Lx' ? Lx : (art === 'Tx' ? Tx : Ex);
  const body = document.getElementById({Lx: 'lBody', Tx: 'tBody', Ex: 'eBody'}[art]);
  const fb = body.querySelector('#xFb'), inp = body.querySelector('#xIn'), pr = body.querySelector('#xCheck');
  const erg = (X.results || [])[window.__i];
  return {fb: fb.textContent, klasse: fb.className, offen: !inp.disabled,
          fokus: document.activeElement === inp, text: inp.value,
          ergebnis: erg === undefined ? null : erg, leben: livesNow(),
          toene: window.__toene.slice(), gesprochen: window.__gesprochen.length,
          loesung: !!body.querySelector('.loesung'), pruefen: !!pr && !pr.parentElement.hidden,
          weiter: !!body.querySelector('.weiterbox'),
          ansage: document.getElementById('ansage').textContent,
          verraten: !!loesung && body.innerText.toLowerCase().indexOf(loesung) >= 0,
          fehler: art === 'Ex' ? Ex.fehler : null};
}
"""

# Eingeben und Pruefen antippen, dann kurz warten (die Ansage kommt nach
# 80 ms, siehe tippHinweis()).
EINGEBEN = r"""
async ([text, ms]) => {
  const body = document.getElementById({Lx: 'lBody', Tx: 'tBody', Ex: 'eBody'}[window.__art]);
  body.querySelector('#xIn').value = text;
  body.querySelector('#xCheck').click();
  await new Promise(r => setTimeout(r, ms));
}
"""


def _legen(seite, art, typ, ziel):
    return seite.js(LEGEN, [art, typ, ziel])


def _eingeben(seite, text, loesung="", ms=250):
    seite.js(EINGEBEN, [text, ms])
    return seite.js(LAGE, loesung)


def _ist_hinweis(lage, text, leben, hinweis=HINWEIS):
    """Der Hinweis steht, und sonst ist nichts passiert."""
    assert lage["fb"] == hinweis, lage
    assert "almost" in lage["klasse"].split(), lage
    assert lage["offen"] and lage["fokus"] and lage["text"] == text, lage
    assert lage["ergebnis"] is None and lage["leben"] == leben, lage
    assert lage["toene"] == [] and lage["gesprochen"] == 0, lage
    assert not lage["loesung"] and not lage["weiter"] and lage["pruefen"], lage
    assert not lage["verraten"], lage
    assert lage["ansage"] == hinweis, lage


def test_ein_tippfehler_genau_eins(seite, heute_stand):
    """einTippfehler() misst den Abstand 1 nach Damerau (OSA) - nicht mehr,
    nicht weniger."""
    seite.starten(stand=heute_stand())
    paare = [("jabula", "jabuka", True),    # ersetzt
             ("jabka", "jabuka", True),     # fehlt
             ("abuka", "jabuka", True),     # fehlt vorn
             ("jabuk", "jabuka", True),     # fehlt hinten
             ("jabukka", "jabuka", True),   # zu viel
             ("jaubka", "jabuka", True),    # vertauscht
             ("ajbuka", "jabuka", True),    # vertauscht vorn
             ("jabuak", "jabuka", True),    # vertauscht hinten
             ("jabuka", "jabuka", False),   # gleich
             ("jebuko", "jabuka", False),   # zwei ersetzt
             ("jaubak", "jabuka", False),   # zweimal vertauscht
             ("jbka", "jabuka", False),     # zwei fehlen
             ("abc", "ca", False)]
    erg = seite.js("(p) => p.map(([a, b]) => [einTippfehler(a, b), einTippfehler(b, a)])", paare)
    for (a, b, soll), (hin, her) in zip(paare, erg):
        assert hin == soll and her == soll, (a, b)
    assert seite.fehler == []


def test_hinweis_bei_jeder_art_von_tippfehler(seite, heute_stand):
    """Ersetzt, fehlt, zu viel, vertauscht: jedes Mal der Hinweis, danach
    zaehlt die richtige Antwort als richtig."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for vertippt in ("jabula", "jabka", "jabukka", "jaubka"):
        leben = _legen(seite, "Lx", "type", "apfel:jabuka")
        _ist_hinweis(_eingeben(seite, vertippt, "jabuka"), vertippt, leben)
        lage = _eingeben(seite, "jabuka")
        assert lage["ergebnis"] is True and lage["leben"] == leben, (vertippt, lage)
        assert lage["fb"] == "Tačno! ✓" and lage["toene"] == ["ok"] and not lage["offen"], (vertippt, lage)
    assert seite.fehler == []


def test_nach_dem_hinweis_zaehlt_falsch_als_falsch(seite, heute_stand):
    """Der zweite Versuch zaehlt wie immer. Ist er wieder nur ein
    Tippfehler daneben, kommt kein zweiter Hinweis."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "type", "apfel:jabuka")
    _ist_hinweis(_eingeben(seite, "jabula", "jabuka"), "jabula", leben)
    lage = _eingeben(seite, "jabuks")
    assert lage["ergebnis"] is False and lage["leben"] == leben - 1, lage
    assert lage["fb"] == "Richtig wäre: jabuka" and "no" in lage["klasse"].split(), lage
    assert lage["toene"] == ["no"] and lage["loesung"] and not lage["offen"], lage
    assert seite.fehler == []


def test_doppelt_druecken_zaehlt_nicht_doppelt(seite, heute_stand):
    """Enter zweimal oder Enter und gleich Pruefen: der zweite Druck mit
    demselben Text ist kein zweiter Versuch. Eine Sekunde spaeter ist er
    es - wer den Fehler nicht findet, haengt nicht fest."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "type", "apfel:jabuka")
    feld = seite.page.locator("#lBody #xIn")
    feld.fill("jabula")
    feld.press("Enter")
    feld.press("Enter")
    seite.page.locator("#lBody #xCheck").dispatch_event("click")
    seite.page.wait_for_timeout(250)
    _ist_hinweis(seite.js(LAGE, "jabuka"), "jabula", leben)
    seite.page.wait_for_timeout(1000)
    feld.press("Enter")
    seite.page.wait_for_timeout(250)
    lage = seite.js(LAGE, "")
    assert lage["ergebnis"] is False and lage["leben"] == leben - 1, lage
    assert seite.js("() => [Lx.right, Lx.results.length, Lx.queue.filter(q => q.retry).length]") == [0, 1, 1]
    assert seite.fehler == []


def test_kein_hinweis_unter_vier_buchstaben(seite, heute_stand):
    """voda hat vier Buchstaben und bekommt den Hinweis, sir hat drei.
    Gezaehlt wird an der Antwort, nicht an der Eingabe: auch "vod" fuer
    "voda" bekommt ihn, "sirr" fuer "sir" nicht (Pruefer 24.10.2026 -
    vorher hatten alle Paare gleich lange Eingabe und Antwort)."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for vertippt in ("voad", "vod"):
        leben = _legen(seite, "Lx", "type", "wasser:voda")
        _ist_hinweis(_eingeben(seite, vertippt, "voda"), vertippt, leben)
    for falsch in ("sur", "sirr"):
        leben = _legen(seite, "Lx", "type", "käse:sir")
        lage = _eingeben(seite, falsch)
        assert lage["ergebnis"] is False and lage["fb"] == "Richtig wäre: sir", (falsch, lage)
        assert lage["leben"] == leben - 1, (falsch, lage)
    assert seite.fehler == []


def test_kein_hinweis_bei_zwei_fehlern(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "type", "apfel:jabuka")
    _ist_hinweis(_eingeben(seite, "jebuka", "jabuka"), "jebuka", leben)
    leben = _legen(seite, "Lx", "type", "apfel:jabuka")
    lage = _eingeben(seite, "jebuko")
    assert lage["ergebnis"] is False and lage["fb"] == "Richtig wäre: jabuka", lage
    assert seite.fehler == []


def test_hinweis_auch_bei_einem_echten_wort(seite, heute_stand):
    """deset ist zehn. Bis zum 27.10.2026 bekam es fuer neun keinen Hinweis
    (zehn und neun verwechselt, nicht vertippt). Ajdin: "wenn es ein andere
    wort ist ist doch egal es ist doch trotzdem fast richtig" - jetzt der
    Hinweis wie bei jedem Tippfehler, danach zaehlt devet richtig."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for eingabe in ("devwt", "deset"):
        leben = _legen(seite, "Lx", "type", "neun:devet")
        _ist_hinweis(_eingeben(seite, eingabe, "devet"), eingabe, leben)
        lage = _eingeben(seite, "devet")
        assert lage["ergebnis"] is True and lage["fb"] == "Tačno! ✓" and lage["leben"] == leben, (eingabe, lage)
    assert seite.js("() => [fastRichtig('deset', 'devet'), fastRichtig('Deset!', 'devet'),"
                    " fastRichtig('devwt', 'devet'), fastRichtig('dvoje', 'devet')]") == [True, True, True, False]
    assert seite.fehler == []


def test_nur_haekchen_bleibt_sofort_fast_richtig(seite, heute_stand):
    """Wie bisher: fehlen nur Haekchen, ist es gleich richtig. Haekchen
    zaehlen auch beim Tippfehler nicht mit - kruskq ist genau einer."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    _legen(seite, "Lx", "type", "birne:kruška")
    lage = _eingeben(seite, "kruska")
    assert lage["ergebnis"] is True and lage["fb"] == "Richtig! Mit Sonderzeichen: kruška", lage
    assert "almost" in lage["klasse"].split() and lage["toene"] == ["ok"], lage
    leben = _legen(seite, "Lx", "type", "birne:kruška")
    _ist_hinweis(_eingeben(seite, "kruskq", "kruška"), "kruskq", leben)
    lage = _eingeben(seite, "kruska")
    assert lage["ergebnis"] is True and lage["fb"] == "Richtig! Mit Sonderzeichen: kruška", lage
    assert seite.fehler == []


def test_lueckensatz_genauso(seite, heute_stand):
    """Im Lueckensatz derselbe Ablauf und derselbe Text - auch fuer ein
    echtes Wort ("deset" fuer "devet"). Unter 4 Buchstaben ist es weiter
    gleich falsch."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for satz, eingabe, richtig in (("Ne ___.|razumijem", "razumijen", "razumijem"),
                                   ("Sedam, osam, ___|devet", "deset", "devet"),       # echtes Wort
                                   ("Subota i ___ su vikend.|nedjelja", "nedjeljw", "nedjelja")):
        leben = _legen(seite, "Lx", "gap", satz)
        _ist_hinweis(_eingeben(seite, eingabe, richtig), eingabe, leben)
        lage = _eingeben(seite, richtig)
        assert lage["ergebnis"] is True and lage["fb"] == "Tačno! ✓" and lage["leben"] == leben, (satz, lage)
    leben = _legen(seite, "Lx", "gap", "Kako ___?|ste")                               # unter 4
    lage = _eingeben(seite, "stw")
    assert lage["ergebnis"] is False and lage["fb"] == "Richtig wäre: ste", lage
    assert lage["leben"] == leben - 1, lage
    # Gegenprobe: in der Schreibaufgabe bekommt die andere Endung denselben Hinweis.
    leben = _legen(seite, "Lx", "type", "sonntag:nedjelja")
    _ist_hinweis(_eingeben(seite, "nedjelji", "nedjelja"), "nedjelji", leben)
    assert seite.fehler == []


@pytest.mark.parametrize("art", ["Tx", "Ex"])
def test_level_test_und_einstufung_genauso(seite, heute_stand, art):
    """Level-Test und Einstufung gehen durch dieselbe Aufgabe: Hinweis ohne
    Leben und ohne Fehler, dann richtig."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN[art])
    leben = _legen(seite, art, "type", "apfel:jabuka")
    lage = _eingeben(seite, "jabula", "jabuka")
    _ist_hinweis(lage, "jabula", leben)
    if art == "Ex":
        assert lage["fehler"] == 0
    lage = _eingeben(seite, "jabuka")
    assert lage["ergebnis"] is True and lage["leben"] == leben, lage
    assert seite.fehler == []


def test_bildschirmleser_bekommt_den_hinweis_in_seiner_sprache(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="en")
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "type", "apfel:jabuka")
    lage = _eingeben(seite, "jabula", "jabuka")
    _ist_hinweis(lage, "jabula", leben, HINWEIS_EN)
    live = seite.js("() => { const a = document.getElementById('ansage');"
                    " return [a.getAttribute('aria-live'), a.getAttribute('aria-atomic')]; }")
    assert live == ["polite", "true"]
    assert seite.fehler == []


# ---- Nach den Pruefern am 24.10.2026 ----

def test_luecke_doppelter_letzter_buchstabe_ist_ein_tippfehler(seite, heute_stand):
    """"sutraa" fuer "sutra": die Taste zweimal getroffen - keine Form,
    sondern der typische Tippfehler. andereEndung() hielt das fuer eine
    angehaengte Endung wie "brat" - "brata", und es kostete ein Leben,
    waehrend die Schreibaufgabe den Hinweis gab."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "gap", "Vidimo se ___!|sutra")
    _ist_hinweis(_eingeben(seite, "sutraa", "sutra"), "sutraa", leben)
    lage = _eingeben(seite, "sutra")
    assert lage["ergebnis"] is True and lage["leben"] == leben, lage
    leben = _legen(seite, "Lx", "gap", "Subota i ___ su vikend.|nedjelja")
    _ist_hinweis(_eingeben(seite, "nedjeljaa", "nedjelja"), "nedjeljaa", leben)
    assert seite.fehler == []


def test_hinweis_auch_bei_weiteren_richtigen_antworten(seite, heute_stand):
    """Jede richtige Antwort zaehlt, nicht nur die erste: im Lueckensatz die
    aus "auch" (stric, striko, adžo neben amidža), in der Schreibaufgabe die
    aus annehmbar() (Zdravo neben Merhaba)."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "gap", "Moj ___ je pčelar.|amidža")
    _ist_hinweis(_eingeben(seite, "strko", "amidža"), "strko", leben)
    lage = _eingeben(seite, "striko")
    assert lage["ergebnis"] is True and lage["leben"] == leben, lage
    leben = _legen(seite, "Lx", "type", "hallo:Merhaba")
    _ist_hinweis(_eingeben(seite, "Zdrsvo", "merhaba"), "Zdrsvo", leben)
    lage = _eingeben(seite, "Zdravo")
    assert lage["ergebnis"] is True and lage["leben"] == leben, lage
    assert seite.fehler == []


def test_echte_woerter_bekommen_den_hinweis_ueberall(seite, heute_stand):
    """Bis zum 27.10.2026 hing es an der Aufgabe, was als echtes Wort galt
    und keinen Hinweis bekam (echteWoerter()). Jetzt bekommt jedes Wort einen
    Tippfehler neben der Antwort "Fast richtig!": "crveno" fuer "crvena" in
    der Schreibaufgabe, "mosta" fuer "košta" und "zvono" (Klingel) fuer
    "zvoni" (klingelt) im Lueckensatz - das Beispiel aus Ajdins Rueckfrage.
    Die alten Pruefungen gibt es nicht mehr."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    assert seite.js("() => [typeof echteWoerter, typeof nurVertippt, typeof nurEndung, typeof andereEndung]") == \
        ["undefined"] * 4
    for typ, ziel, eingabe, richtig in (("type", "rot:crvena", "crveno", "crvena"),
                                        ("gap", "Koliko ___?|košta", "mosta", "košta"),
                                        ("gap", "Komšinica ___ na vrata.|zvoni", "zvono", "zvoni")):
        leben = _legen(seite, "Lx", typ, ziel)
        _ist_hinweis(_eingeben(seite, eingabe, richtig), eingabe, leben)
        lage = _eingeben(seite, richtig)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, lage)
    assert seite.fehler == []


def test_fokus_kommt_nach_echtem_tipp_auf_pruefen_zurueck(seite, heute_stand):
    """Wer Pruefen mit dem Finger antippt, nimmt dem Feld den Fokus - auf dem
    Handy klappt die Tastatur zu. Der Hinweis gibt ihn zurueck. Ein Klick
    per JS verschiebt den Fokus nie, deshalb hier ein echter Klick."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for typ, ziel, vertippt, loesung in (("type", "apfel:jabuka", "jabula", "jabuka"),
                                         ("gap", "Ne ___.|razumijem", "razumijen", "razumijem")):
        leben = _legen(seite, "Lx", typ, ziel)
        seite.page.locator("#lBody #xIn").fill(vertippt)
        seite.page.locator("#lBody #xCheck").click()
        seite.page.wait_for_timeout(250)
        _ist_hinweis(seite.js(LAGE, loesung), vertippt, leben)
        assert seite.js("() => document.activeElement.id") == "xIn", typ
    assert seite.fehler == []


def test_festgehaltenes_enter_ist_kein_zweiter_versuch(seite, heute_stand):
    """Festgehaltenes Enter schickt nach einer Weile Wiederholungen
    (repeat). Die sind kein zweiter Versuch - auch nicht nach DOPPELT_MS,
    sonst kostete langes Druecken ein Leben."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "type", "apfel:jabuka")
    seite.js("() => { window.__enter = []; document.getElementById('lBody').addEventListener('keydown',"
             " e => { if(e.key === 'Enter') window.__enter.push(e.repeat); }, true); }")
    seite.page.locator("#lBody #xIn").fill("jabula")
    seite.page.keyboard.down("Enter")
    seite.page.wait_for_timeout(seite.js("() => DOPPELT_MS") + 100)
    seite.page.keyboard.down("Enter")      # noch gedrueckt: repeat
    seite.page.keyboard.up("Enter")
    seite.page.wait_for_timeout(250)
    assert seite.js("() => window.__enter") == [False, True]
    _ist_hinweis(seite.js(LAGE, "jabuka"), "jabula", leben)
    assert seite.fehler == []


@pytest.mark.parametrize("typ", ["type", "gap"])
def test_hinweis_wird_ins_bild_geholt(browser, basis, heute_stand, typ):
    """Grosse Schrift und offene Tastatur: der Hinweis steht unter dem Feld
    und damit leicht unter dem Rand. Er hat keinen Ton - wer ihn nicht
    sieht, merkt gar nichts und verliert beim naechsten Pruefen ein Leben.
    tippHinweis() holt ihn deshalb ins Bild wie weiterBeiTipp() den
    Weiter-Knopf; das Feld behaelt den Fokus. Die Tastatur ist hier eine
    kleinere Sichtflaeche, nachdem das Feld den Fokus hat."""
    from conftest import Seite
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                              service_workers="block", reduced_motion="no-preference")
    try:
        seite = Seite(ctx.new_page(), basis)
        seite.starten(stand=heute_stand())
        seite.js(STARTEN["Lx"])
        if typ == "type":
            ziel, vertippt, loesung = "apfel:jabuka", "jabula", "jabuka"
        else:
            ziel, vertippt, loesung = "Subota i ___ su vikend.|nedjelja", "nedjeljw", "nedjelja"
        leben = _legen(seite, "Lx", typ, ziel)
        seite.js(SCHRIFT, 2.0)
        # Die Tastatur geht auf: weniger Platz, und das Feld mit dem Fokus
        # rueckt ins Bild, wie Android es dann tut.
        assert seite.js("() => document.activeElement.id") == "xIn"
        seite.page.set_viewport_size({"width": 360, "height": 400})
        seite.js("() => document.activeElement.scrollIntoView({block: 'nearest'})")
        seite.page.wait_for_timeout(250)
        seite.page.keyboard.type(vertippt)
        seite.page.keyboard.press("Enter")
        lage = seite.js("""async () => {
          const fb = document.querySelector('#lBody #xFb'), ende = Date.now() + 2000;
          let r = fb.getBoundingClientRect();
          while(!(fb.textContent && r.top >= -1 && r.bottom <= innerHeight + 1) && Date.now() < ende){
            await new Promise(w => setTimeout(w, 30)); r = fb.getBoundingClientRect(); }
          return {oben: r.top, unten: r.bottom, hoehe: innerHeight}; }""")
        # Ein Pixel Spiel: gescrollt wird in ganzen, gemessen in Bruchteilen.
        assert -1 <= lage["oben"] and lage["unten"] <= lage["hoehe"] + 1, lage
        seite.page.wait_for_timeout(250)      # die Ansage kommt nach 80 ms
        _ist_hinweis(seite.js(LAGE, loesung), vertippt, leben)
        assert seite.fehler == []
    finally:
        ctx.close()


# ---- Andere Endung im Lueckensatz (27.10.2026) ----
# Ajdin auf die Rueckfrage, ob eine andere Endung im Lueckensatz weiter
# sofort falsch sein soll: "Auch bei Endung Hinweis". Zuerst mit eigenem Text
# ("Fast! Achte auf die Endung."), noch am selben Tag "einfach nur fast
# richtig": derselbe Hinweis wie bei jedem Tippfehler. Eine andere Endung
# ist ja immer einer - ein Buchstabe anders oder einer mehr.

def test_endung_im_lueckensatz_bekommt_den_hinweis(seite, heute_stand):
    """Ein anderer Selbstlaut am Ende ("nedjelji" fuer "nedjelja"), die
    Grundform statt der gebeugten ("kahva" fuer "kahvu") oder einer
    angehaengt ("razumijemo" fuer "razumijem"): jedes Mal "Fast richtig!" -
    ohne Leben, Ton und Loesung. Der zweite Versuch zaehlt richtig."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for satz, eingabe, loesung in (("Subota i ___ su vikend.|nedjelja", "nedjelji", "nedjelja"),
                                   ("Pijem ___.|kahvu", "kahva", "kahvu"),
                                   ("Ne ___.|razumijem", "razumijemo", "razumijem")):
        leben = _legen(seite, "Lx", "gap", satz)
        _ist_hinweis(_eingeben(seite, eingabe, loesung), eingabe, leben)
        lage = _eingeben(seite, loesung)
        assert lage["ergebnis"] is True and lage["leben"] == leben, (satz, lage)
        assert lage["fb"] == "Tačno! ✓" and lage["toene"] == ["ok"] and not lage["offen"], (satz, lage)
    assert seite.js("() => [Lx.right, Lx.results.length, Lx.queue.filter(q => q.retry).length]") == [3, 3, 0]
    assert seite.fehler == []


def test_endung_nach_dem_hinweis_zaehlt_falsch_als_falsch(seite, heute_stand):
    """Es gibt nur einen zweiten Versuch. Ist er wieder eine andere Endung
    oder ein Tippfehler, ist er falsch - kein zweiter Hinweis."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    for erst, dann in (("nedjelji", "nedjelju"), ("nedjelji", "nedjeljw"), ("nedjeljw", "nedjelji")):
        leben = _legen(seite, "Lx", "gap", "Subota i ___ su vikend.|nedjelja")
        _ist_hinweis(_eingeben(seite, erst, "nedjelja"), erst, leben)
        lage = _eingeben(seite, dann)
        assert lage["ergebnis"] is False and lage["leben"] == leben - 1, (erst, dann, lage)
        assert lage["fb"] == "Richtig wäre: nedjelja" and "no" in lage["klasse"].split(), (erst, dann, lage)
        assert lage["toene"] == ["no"] and lage["loesung"] and not lage["offen"], (erst, dann, lage)
    assert seite.fehler == []


def test_endung_zaehlt_wie_jeder_tippfehler(seite, heute_stand):
    """Gezaehlt wird wie beim Tippfehler - ab 4 getippten Zeichen der
    Antwort, nj ist zwei: "sti" fuer "ste" ist sofort falsch, "konji" fuer
    "konj" bekommt den Hinweis. Zwei Buchstaben anders ("medjelji") ist
    falsch. "strico" bei „Moj ___ je pčelar.“ ist stric mit angehaengtem
    Selbstlaut und zugleich striko vertippt - beides "Fast richtig!"."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "gap", "Kako ___?|ste")
    lage = _eingeben(seite, "sti")
    assert lage["ergebnis"] is False and lage["fb"] == "Richtig wäre: ste" and lage["leben"] == leben - 1, lage
    leben = _legen(seite, "Lx", "gap", "Moj ___ je pčelar.|amidža")
    _ist_hinweis(_eingeben(seite, "strico", "amidža"), "strico", leben)
    lage = _eingeben(seite, "stric")
    assert lage["ergebnis"] is True and lage["fb"] == "Tačno! ✓" and lage["leben"] == leben, lage
    assert seite.js("() => [fastRichtig('nedjelji', 'nedjelja'), fastRichtig('Nedjelji!', 'nedjelja'),"
                    " fastRichtig('kahva', 'kahvu'), fastRichtig('striku', 'amidža / stric / striko / adžo'),"
                    " fastRichtig('konji', 'konj'), fastRichtig('sti', 'ste'), fastRichtig('sutraa', 'sutra'),"
                    " fastRichtig('nedjeljw', 'nedjelja'), fastRichtig('medjelja', 'nedjelja'),"
                    " fastRichtig('medjelji', 'nedjelja'), fastRichtig('', 'nedjelja')]") == \
        [True, True, True, True, True, False, True, True, True, False, False]
    assert seite.fehler == []


@pytest.mark.parametrize("art", ["Tx", "Ex"])
def test_endung_in_level_test_und_einstufung(seite, heute_stand, art):
    """Level-Test und Einstufung gehen durch dieselbe Aufgabe: auch hier
    kostet der Hinweis kein Leben und zaehlt keinen Fehler."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN[art])
    leben = _legen(seite, art, "gap", "Subota i ___ su vikend.|nedjelja")
    lage = _eingeben(seite, "nedjelji", "nedjelja")
    _ist_hinweis(lage, "nedjelji", leben)
    if art == "Ex":
        assert lage["fehler"] == 0
    lage = _eingeben(seite, "nedjelja")
    assert lage["ergebnis"] is True and lage["leben"] == leben, lage
    assert seite.fehler == []


def test_bildschirmleser_bekommt_den_hinweis_auch_im_lueckensatz(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="en")
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "gap", "Subota i ___ su vikend.|nedjelja")
    _ist_hinweis(_eingeben(seite, "nedjelji", "nedjelja"), "nedjelji", leben, HINWEIS_EN)
    assert seite.fehler == []
