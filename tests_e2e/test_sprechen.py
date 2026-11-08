# -*- coding: utf-8 -*-
"""Die Sprechaufgabe (Pruefbericht zu 1.3, 06.11.2026).

G5: Wer nur "mogu" sagte, bekam bei "Mogu li platiti karticom?" ein Bravo, und der
Satz galt als gewusst. Enthalten zaehlt jetzt nur noch, wenn das Gehoerte den
groessten Teil des Ziels abdeckt.

G6: Nach "kein Treffer" oder Stille startete die App still die naechste Sprache, und
auf dem Bildschirm stand weiter "Hoert zu ...". Jetzt ist nach einem solchen Ergebnis
Schluss und die Meldung kommt. Der Rueckfall bleibt erhalten: Der naechste Tipp nimmt
die naechste Sprache, denn ein Geraet ohne bs-BA kann ebenfalls so antworten. Das
laesst sich hier nicht pruefen, der echte Android-Erkenner laeuft nur am Handy.
Andere Ablehnungen wandern wie bisher in einem Zug weiter.

Der Erkenner ist nachgebaut: Er schreibt jeden Aufruf mit und antwortet nach Plan.
"""
import pytest

ERKENNER = r"""
window.__hoerer = {plan: [], aufrufe: []};
window.Capacitor = window.Capacitor || {Plugins: {}};
window.Capacitor.Plugins = window.Capacitor.Plugins || {};
window.Capacitor.Plugins.SpeechRecognition = {
  available: async () => ({available: true}),
  checkPermissions: async () => ({speechRecognition: 'granted'}),
  requestPermissions: async () => ({speechRecognition: 'granted'}),
  start: async (o) => {
    window.__hoerer.aufrufe.push(o.language || null);
    await new Promise(r => setTimeout(r, 15));
    const a = window.__hoerer.plan.shift();
    if(typeof a === 'string') throw new Error(a);
    return {matches: a || []};
  },
  stop: async () => {},
};
"""

# Eine Lektion, deren naechste Aufgabe genau dieses Wort sprechen will.
AUFGABE = r"""
(bs) => {
  const f = CATEGORIES.flatMap(c => c.words.map(w => ({w, c}))).find(x => x.w.bs === bs);
  if(!f) throw new Error('kein Wort ' + bs);
  catIdx = CATEGORIES.indexOf(f.c); openLevel(catIdx); buildLesson();
  Lx.queue = [{typ: 'speak', w: f.w}, {typ: 'mc', w: f.w}]; Lx.i = 0; Lx.results = [];
  document.getElementById('levelHome').style.display = 'none';
  document.getElementById('lesson').style.display = 'block';
  nurHerz(true); showLessonTask();
  window.__hoerer.aufrufe.length = 0;
}
"""

MIKRO_FERTIG = "() => !document.querySelector('#lBody #xMic').classList.contains('rec')"
LAGE = """() => ({gehoert: document.querySelector('#lBody #xHeard').textContent, aufrufe: window.__hoerer.aufrufe.slice(),
                 ergebnisse: Lx.results.slice(), i: Lx.i, leben: livesNow()})"""


def _tippen(seite, *plan):
    """Das Mikrofon antippen und warten, bis es wieder aus ist."""
    seite.js("(p) => { window.__hoerer.plan = p; }", list(plan))
    seite.page.locator("#lBody #xMic").click()
    seite.page.wait_for_timeout(30)
    seite.page.wait_for_function(MIKRO_FERTIG)
    seite.page.wait_for_timeout(30)
    return seite.js(LAGE)


@pytest.fixture
def mit_erkenner(seite, heute_stand):
    seite.page.add_init_script(ERKENNER)
    seite.starten(stand=heute_stand())
    return seite


def _t(seite, schluessel):
    return seite.js("(k) => t(k)", schluessel)


# ------------------------------------------------- G5: ein Wort reicht nicht ---

@pytest.mark.parametrize("gehoert, ziel, soll", [
    ("mogu", "Mogu li platiti karticom?", False),
    ("platiti", "Mogu li platiti karticom?", False),
    ("mogu li platiti", "Mogu li platiti karticom?", False),       # ein gutes Drittel fehlt
    ("mogu li platiti karticom", "Mogu li platiti karticom?", True),
    ("mogu li platit karticom", "Mogu li platiti karticom?", True),    # ein Buchstabe anders
    ("Hvala lijepo", "Hvala lijepo", True),
    ("kako se zoves", "Kako se zoveš?", True),
    ("kako", "Kako se zoveš?", False),
    ("mogu li", "Mogu li?", True),
    ("jabuka", "jabuka", True),
    ("to je jabuka", "jabuka", True),                              # mehr gesagt: zaehlt weiter
    ("ja volim hvala", "hvala", True),
    ("da", "Da li govoriš bosanski?", False),
    ("koala", "hvala", True),                                      # die lautliche Vereinfachung bleibt
])
def test_gehoertes_gegen_ziel(seite, heute_stand, gehoert, ziel, soll):
    seite.starten(stand=heute_stand())
    assert seite.js("([g, z]) => klingtWie(g, z)", [gehoert, ziel]) is soll
    assert seite.fehler == []


def test_klammerzusatz_zaehlt_nicht_zum_ziel(seite, heute_stand):
    seite.starten(stand=heute_stand())
    assert seite.js("() => [klingtWie('nana', 'nana (auch: metvica)'), klingtWie('metvica', 'nana (auch: metvica)')]") \
        == [True, False]
    assert seite.fehler == []


# Jeder Eintrag: ganz gesprochen besteht er. Ein einzelnes Wort aus einem Satz mit
# mindestens drei Woertern besteht fast nie (vorher 4.788 von 4.802).
ALLE = r"""
() => {
  const roh = s => s.replace(/\([^)]*\)/g, ' ').replace(/[.,!?…;:„“”"]/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
  const r = {formen: 0, abgelehnt: [], einzeln: 0, durch: []};
  for(const w of CATEGORIES.concat(zaLevel()).flatMap(c => c.words)){
    const ziele = String(w.bs).split(' / ');
    for(const z of ziele){
      r.formen++;
      if(!ziele.some(x => klingtWie(roh(z), x))) r.abgelehnt.push(z);
    }
    const woerter = roh(ziele[0]).split(' ');
    if(woerter.length < 3) continue;
    for(const x of woerter.filter(y => y.length >= 4)){
      r.einzeln++;
      if(ziele.some(z => klingtWie(x, z))) r.durch.push([ziele[0], x]);
    }
  }
  return r;
}
"""


def test_alle_eintraege_ganz_gesprochen_ja_einzelnes_wort_nein(seite, heute_stand):
    seite.starten(stand=heute_stand())
    e = seite.js(ALLE)
    assert e["formen"] > 4000 and e["abgelehnt"] == [], e["abgelehnt"][:20]
    assert e["einzeln"] > 4000 and len(e["durch"]) <= 5, e["durch"][:20]
    assert seite.fehler == []


def test_ein_wort_aus_dem_satz_gibt_kein_bravo(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Mogu li platiti karticom?")
    leben = seite.js("() => livesNow()")
    z = _tippen(seite, ["mogu"])
    assert "mogu" in z["gehoert"] and z["ergebnisse"] == [] and z["i"] == 0 and z["leben"] == leben, z
    z = _tippen(seite, ["mogu li platiti karticom"])
    assert z["ergebnisse"] == [True], z
    assert seite.fehler == []


# ---------------------------------------------- G6: nicht still weiterlauschen ---

@pytest.mark.parametrize("meldung", ["No match", "No speech input"])
def test_kein_treffer_hoert_auf_und_der_naechste_tipp_nimmt_die_naechste_sprache(mit_erkenner, meldung):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    fehler = _t(seite, "task.mikro_fehler")
    z = _tippen(seite, meldung, ["falsche Sprache"])       # ein zweiter Lauf taete hier so, als haette er gehoert
    assert z["aufrufe"] == ["bs-BA"] and z["gehoert"] == fehler and z["ergebnisse"] == [], z
    # Der Rueckfall fuer Geraete ohne bs-BA: mit dem naechsten Tipp, nicht mehr still.
    z = _tippen(seite, ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "hr-HR"] and z["ergebnisse"] == [True], z
    assert seite.fehler == []


def test_jeder_tipp_eine_sprache_und_wieder_von_vorn(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    for _ in range(5):
        _tippen(seite, "No match")
    assert seite.js(LAGE)["aufrufe"] == ["bs-BA", "hr-HR", "sr-RS", None, "bs-BA"]
    assert seite.fehler == []


def test_die_naechste_aufgabe_beginnt_wieder_bei_bs(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    _tippen(seite, "No match")
    seite.js(AUFGABE, "Hvala")
    assert _tippen(seite, ["hvala"])["aufrufe"] == ["bs-BA"]
    assert seite.fehler == []


@pytest.mark.parametrize("meldung", ["Didn't understand, please try again.", "Client side error", "error from server"])
def test_andere_ablehnung_wandert_wie_bisher_in_einem_zug_weiter(mit_erkenner, meldung):
    """So meldet das Plugin auch "Sprache fehlt" (Android-Fehler 12 und 13 fallen in
    den Zweig mit dem ersten Text). Hier muss der Rueckfall sofort greifen."""
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, meldung, ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "hr-HR"] and z["ergebnisse"] == [True], z
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, meldung, meldung, meldung, meldung)
    assert z["aufrufe"] == ["bs-BA", "hr-HR", "sr-RS", None] and z["ergebnisse"] == [], z
    assert seite.fehler == []


def test_abgebrochen_startet_keine_weitere_sprache(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    seite.js("""() => { window.__hoerer.plan = ['Client side error']; const H = window.Capacitor.Plugins.SpeechRecognition;
        const alt = H.start;
        H.start = async (o) => { document.querySelector('#lBody #xMic').click(); return await alt(o); }; }""")
    seite.page.locator("#lBody #xMic").click()
    seite.page.wait_for_timeout(120)
    assert seite.js(LAGE)["aufrufe"] == ["bs-BA"]
    assert seite.fehler == []
