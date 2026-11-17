# -*- coding: utf-8 -*-
"""Die Sprechaufgabe (Pruefbericht zu 1.3, 06.11.2026, und Sprech-Fix vom 16.11.2026).

G5: Wer nur "mogu" sagte, bekam bei "Mogu li platiti karticom?" ein Bravo, und der
Satz galt als gewusst. Enthalten zaehlt jetzt nur noch, wenn das Gehoerte den
groessten Teil des Ziels abdeckt.

G6: Nach "kein Treffer" oder Stille startete die App still die naechste Sprache, und
auf dem Bildschirm stand weiter "Hoert zu ...". Jetzt ist nach einem solchen Ergebnis
Schluss und die Meldung kommt.

Sprech-Fix 16.11.2026 (Sprech-Analyse vom 16.11.2026, Fix-Plan Schritte 1-5): Ueber
das Formular kam, dass die Sprechuebung auch einen Muttersprachler nicht immer
erkennt. Auf Android rutschte die Sprachkette innerhalb einer Aufgabe bis sr-RS
und zur Handysprache, und eine kyrillische Abschrift war immer falsch.
- Schritt 1: Android hoert nur noch bs-BA und hr-HR zu. Was ein Fehler bedeutet,
  entscheidet, wie es weitergeht; die Sprache, die etwas geliefert hat, gilt fuer die
  Sitzung; scheitert alles wiederholt, fallen Sprechaufgaben fuer die Sitzung aus; jeder
  Start hat eine Zeitgrenze.
- Schritt 2: Kyrillisch wird vor dem Vergleich in Lateinschrift umgeschrieben.
- Schritt 3 und Ajdins Entscheidung 4: Ziele mit hoechstens drei Lauten gelten nur
  noch genau gleich, dafuer mit Wiederholungen und Fuellwoertern ("Pa da", "Da da").
- Schritt 4: "brat → braća" gilt auch mit der Mehrzahl allein, nicht mit der Einzahl.
- Schritt 5: Vor dem Zuhoeren haelt der Ton an, und im Browser bleibt "Hoert zu ..."
  nicht stehen.
- Ajdins Entscheidung 3: Ueberspringen nach einem gescheiterten Versuch kostet die
  Tagesaufgabe "ohne Fehler" nicht mehr.

Nachbesserung nach der Pruefung (16.11.2026): Die Mehrzahl allein gilt nur genau
gleich ("brava" war richtig fuer "braća"), zusammengeschrieben zaehlt nicht ("nana"
war richtig fuer "na"), und hat bs-BA einmal geliefert, bleibt es bei bs-BA.

Ajdins Antworten vom 16.11.2026 (Fragen, Abschnitt 11), nur beim Sprechen: "Tko" gilt
fuer "Ko", "Što" fuer "Šta" (als Wort und im Satz), "Ćau" und "Ciao" fuer "Ćao", und
"e", "ee", "eee" sowie "Okay", "Okej", "Okey" sind Fuellwoerter wie "ok". Dazu
(17.11.2026): Faellt das Sprechen fuer die Sitzung aus, nimmt die Seite die restlichen
Sprechaufgaben aus der laufenden Lektion.

Der Erkenner ist nachgebaut: Er schreibt jeden Aufruf mit und antwortet nach Plan.
Der echte Android-Erkenner laeuft nur am Handy.
"""
import pytest

ERKENNER = r"""
window.__hoerer = {plan: [], aufrufe: [], stops: 0};
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
    if(a && !Array.isArray(a)){            // {warte: ms, matches: [...]} - eine spaete Antwort
      await new Promise(r => setTimeout(r, a.warte || 0));
      return {matches: a.matches || []};
    }
    return {matches: a || []};
  },
  stop: async () => { window.__hoerer.stops++; },
};
"""

# Ein iPhone: dieselbe Seite, aber getPlatform() sagt 'ios'.
IPHONE = r"""
window.Capacitor = window.Capacitor || {Plugins: {}};
window.Capacitor.getPlatform = () => 'ios';
"""

# Der Erkenner des Browsers (Chrome am PC), nachgebaut. Ein Plan-Eintrag: eine Liste
# (Ergebnis), {fehler: 'no-speech'} oder nichts - dann endet er ohne beides.
BROWSER = r"""
window.__sr = {plan: [], starts: 0};
window.SpeechRecognition = class {
  start(){
    window.__sr.starts++;
    const a = window.__sr.plan.shift();
    setTimeout(() => {
      if(this.onstart) this.onstart();
      setTimeout(() => {
        if(a && a.fehler){ if(this.onerror) this.onerror({error: a.fehler}); }
        else if(Array.isArray(a)){ if(this.onresult) this.onresult({results: [a.map(t => ({transcript: t}))]}); }
        if(this.onend) this.onend();
      }, 20);
    }, 10);
  }
  stop(){}
  abort(){}
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
  if(window.__hoerer) window.__hoerer.aufrufe.length = 0;
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


@pytest.fixture
def mit_iphone(seite, heute_stand):
    seite.page.add_init_script(ERKENNER)
    seite.page.add_init_script(IPHONE)
    seite.starten(stand=heute_stand())
    return seite


@pytest.fixture
def mit_browser(seite, heute_stand):
    seite.page.add_init_script(BROWSER)
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
      if(!ziele.some(x => klingtWie(roh(z), x)) || !passtGesprochen(roh(z), w.bs)) r.abgelehnt.push(z);
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


# ------------------------------------- Schritt 2: Kyrillisch in Lateinschrift ---

@pytest.mark.parametrize("gehoert, ziel", [
    ("хвала", "Hvala"),
    ("Хвала", "Hvala"),
    ("добар дан", "Dobar dan"),
    ("лаку ноћ", "Laku noć"),
    ("два", "dvije"),                    # vor zahlWert() umgeschrieben, sonst bliebe das falsch
    ("да", "Da"),
    ("џезва", "džezva"),
    ("љубав", "ljubav"),
    ("коњ", "konj"),
    ("ђак", "đak"),
    ("жена", "žena"),
    ("чај", "čaj"),
    ("шума", "šuma"),
    ("цијена", "cijena"),
    ("сестра", "sestra"),
])
def test_kyrillisch_zaehlt_beim_sprechen(seite, heute_stand, gehoert, ziel):
    seite.starten(stand=heute_stand())
    assert seite.js("([g, z]) => klingtWie(g, z)", [gehoert, ziel]) is True
    assert seite.fehler == []


def test_kyrillisch_jeder_buchstabe_des_serbischen_alphabets(seite, heute_stand):
    """lautlich() macht aus ž, č, ć, š und đ ohnehin z, c, s und d - ein Tippfehler in
    der Tabelle (etwa 'ж': 'z') fiele bei klingtWie() nicht auf. Darum hier die
    Umschrift selbst, alle 30 Buchstaben, gross und klein."""
    seite.starten(stand=heute_stand())
    kyr = "АБВГДЂЕЖЗИЈКЛЉМНЊОПРСТЋУФХЦЧЏШ"
    lat = "abvgdđežzijklljmnnjoprstćufhcčdžš"
    assert seite.js("(s) => kyrillischLatein(s)", kyr) == lat
    assert seite.js("(s) => kyrillischLatein(s)", kyr.lower()) == lat
    assert seite.js("(s) => kyrillischLatein(s)", "Laku noć, 5!") == "Laku noć, 5!"   # Latein bleibt, wie es ist
    assert seite.fehler == []


def test_kyrillisch_falsches_wort_bleibt_falsch_und_tippen_bleibt_wie_es_war(seite, heute_stand):
    seite.starten(stand=heute_stand())
    e = seite.js("""() => ({falsch: [klingtWie('хвала', 'Dobar dan'), klingtWie('не', 'Da'), klingtWie('пас', 'sin')],
                            tippen: matches('хвала', 'Hvala')})""")
    assert e["falsch"] == [False, False, False], e
    assert e["tippen"] != "ok" and e["tippen"] != "almost", e     # getippt zaehlt Kyrillisch nicht
    assert seite.fehler == []


def test_kyrillische_abschrift_in_der_aufgabe(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, ["хвала"])
    assert z["ergebnisse"] == [True], z
    assert seite.fehler == []


# ------------------- Schritt 3 und Entscheidung 4: sehr kurze Ziele genau gleich ---

@pytest.mark.parametrize("gehoert, ziel, soll", [
    ("Pa da", "Da", True),              # Fuellwort davor
    ("Da da", "Da", True),              # Wiederholung
    ("da eto", "Da", True),
    ("Ćao ćao", "Ćao", True),
    ("Hmm, da.", "Da", True),
    ("dada", "Da", False),              # zusammengeschrieben: ein Wort, nicht genau gleich
    ("nana", "na", False),              # "nana" (Oma) ist selbst ein Wort der App
    ("Nana", "na", False),
    ("ko", "Ko?", True),
    ("pa", "pas", False),               # ein Buchstabe weniger: frueher richtig
    ("sir", "sin", False),
    ("na", "ne", False),
    ("dva", "Da", False),
    ("dan", "Da", False),
    ("pa", "Da", False),
    ("noć", "nož", False),
    ("on", "ona", False),
    ("Pa dva", "Da", False),            # das Wort selbst nur genau gleich
    ("Ne znam", "Ne", False),
    ("ne da", "Da", False),
    ("da ne", "Da", False),
    ("da ne", "Ne", False),
    ("Ko je", "Ko?", False),            # "je" ist kein Fuellwort
    ("kuča", "kuća", True),             # č und ć gelten weiter gleich
    ("juli", "juni", True),             # vier Laute: wie bisher
    ("vrat", "brat", True),
    ("5", "pet", True),                 # Zahlen wie bisher
    ("pa 5", "pet", True),
])
def test_sehr_kurze_ziele_nur_genau_gleich(seite, heute_stand, gehoert, ziel, soll):
    seite.starten(stand=heute_stand())
    assert seite.js("([g, z]) => klingtWie(g, z)", [gehoert, ziel]) is soll
    assert seite.fehler == []


def test_pa_da_in_der_aufgabe(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Da")
    z = _tippen(seite, ["dva", "pa"])
    assert z["ergebnisse"] == [] and "dva" in z["gehoert"], z
    z = _tippen(seite, ["Pa da"])
    assert z["ergebnisse"] == [True], z
    assert seite.fehler == []


# --------------- Fragen 11.1 bis 11.3 (17.11.2026): Schreibweise des Erkenners ---

# [gehoert, ziel, soll]. Ein Lauf, eine Seite: passtGesprochen() wie in bewerte().
NEUE_REGELN = [
    # 11.1: "Tko" fuer "Ko", "Što" fuer "Šta", als Wort und im Satz
    ["Tko", "Ko?", True],
    ["tko?", "Ko?", True],
    ["TKO", "Ko?", True],
    ["Tko je to?", "Ko je to?", True],
    ["Što", "Šta?", True],
    ["ŠTO?", "Šta?", True],
    ["Što je to?", "Šta je to?", True],
    ["Eee tko", "Ko?", True],
    ["тко", "Ko?", True],                  # erst Kyrillisch in Latein, dann die Schreibweise
    ["што", "Šta?", True],
    ["sto", "Šta?", False],                # sto (hundert) wird nie zu šta
    ["Sto", "Šta?", False],
    ["100", "Šta?", False],
    ["Šta", "sto", False],
    ["šta", "sto", False],
    ["sto", "sto", True],
    ["zašto", "Šta?", False],              # nur ganze Woerter
    ["nešto", "Šta?", False],
    ["zašto", "zašto", True],
    ["nešto", "nešto", True],
    ["Tko", "to", False],
    ["Što", "stan", False],                # nur, wo das Ziel "šta" hat
    ["Što", "staž", False],
    ["Šta", "što", False],                 # das App-Wort "što" (dass) nimmt "Šta" nicht
    ["što", "što", True],
    ["sto", "što", True],                  # Haekchen zaehlen weiter nicht
    ["Drago mi je što smo se upoznali", "Drago mi je što smo se upoznali", True],
    # 11.3: "Ćau" und "Ciao" fuer "Ćao"
    ["Ćau", "Ćao", True],
    ["ćau", "Ćao", True],
    ["čau", "Ćao", True],
    ["Cau", "Ćao", True],
    ["Ciao", "Ćao", True],
    ["CIAO", "Ćao", True],
    ["cao", "Ćao", True],
    ["Ćau ćau", "Ćao", True],
    ["Ciao ciao", "Ćao", True],
    ["Ćau", "Da", False],
    ["Ciao", "čaj", False],
    # 11.2: "e", "ee", "eee" und "Okay", "Okej", "Okey" wie "ok"
    ["Eee da", "Da", True],
    ["E da", "Da", True],
    ["eeeee, da", "Da", True],
    ["Da eee", "Da", True],
    ["Okej da", "Da", True],
    ["Okay da", "Da", True],
    ["okey, da", "Da", True],
    ["Eee ne", "Ne", True],
    ["Eee braća", "brat → braća", True],
    ["Okej psi", "pas → psi", True],
    ["e", "Da", False],                    # nur Fuellwoerter: es bleibt nichts
    ["Eee", "Da", False],
    ["e e", "Da", False],
    ["Okej", "Da", False],
    ["okej ne", "Da", False],
    ["e dva", "Da", False],                # das Wort selbst weiter nur genau gleich
    ["eh da", "Da", False],                # "eh" ist kein Fuellwort
    ["je da", "Da", False],
    ["e", "E", True],                      # ein Ziel "E": das Zoegern selbst gilt
    ["ee", "E", True],
    ["Eee", "E", True],
    ["Eee da", "E", False],
]


def test_erkenner_schreibweise_und_neue_fuellwoerter(seite, heute_stand):
    seite.starten(stand=heute_stand())
    falsch = seite.js("(liste) => liste.filter(([g, z, soll]) => passtGesprochen(g, z) !== soll)", NEUE_REGELN)
    assert falsch == [], falsch
    assert seite.fehler == []


def test_neue_regeln_gelten_nicht_beim_tippen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    e = seite.js("""() => [['Tko', 'Ko?'], ['Što', 'Šta?'], ['Ciao', 'Ćao'], ['Ćau', 'Ćao'], ['Eee da', 'Da'],
                           ['Okej da', 'Da']].map(([g, z]) => [g, z, matches(g, z)])""")
    assert all(r != "ok" for _, _, r in e), e
    assert seite.fehler == []


@pytest.mark.parametrize("ziel, falsch, richtig", [
    ("Ko?", "Ko je", "Tko"),
    ("Šta?", "sto", "Što"),
    ("Ćao", "čaj", "Ćau ćau"),
    ("Da", "e", "Eee da"),
    ("Da", "Okej", "Okej da"),
])
def test_neue_regeln_in_der_aufgabe(mit_erkenner, ziel, falsch, richtig):
    seite = mit_erkenner
    seite.js(AUFGABE, ziel)
    z = _tippen(seite, [falsch])
    assert z["ergebnisse"] == [] and z["i"] == 0, z
    z = _tippen(seite, [richtig])
    assert z["ergebnisse"] == [True], z
    assert seite.fehler == []


# ------------------------------------------ Schritt 4: Pfeil-Eintraege (Mehrzahl) ---

PFEILE = r"""
() => CATEGORIES.flatMap(c => c.words).filter(w => String(w.bs).includes(' → ')).map(w => {
  const [eins, mehr] = w.bs.split(' → ');
  return [w.bs, passtGesprochen(eins, w.bs), passtGesprochen(mehr, w.bs), passtGesprochen(eins + ' ' + mehr, w.bs)];
})
"""


def test_pfeil_eintraege_mehrzahl_allein_ja_einzahl_allein_nein(seite, heute_stand):
    seite.starten(stand=heute_stand())
    alle = seite.js(PFEILE)
    assert len(alle) == 26, alle
    falsch = [x for x in alle if x[1:] != [False, True, True]]
    assert falsch == [], falsch
    assert seite.fehler == []


@pytest.mark.parametrize("gehoert, eintrag, soll", [
    ("braća", "brat → braća", True),
    ("Pa braća", "brat → braća", True),             # Fuellwort davor
    ("braća braća", "brat → braća", True),          # Wiederholung
    ("kuče", "kuća → kuće", True),                  # č und ć gelten weiter gleich
    ("дјеца", "dijete → djeca", True),              # Kyrillisch wie ueberall beim Sprechen
    ("brat braća", "brat → braća", True),           # beide Woerter, wie bisher
    # Nur aehnlich ist nicht genau: das waren fremde Woerter der App
    ("brava", "brat → braća", False),
    ("brada", "brat → braća", False),
    ("doći", "noć → noći", False),
    ("dati", "dan → dani", False),
    ("mene", "žena → žene", False),
    ("odjeća", "dijete → djeca", False),
    ("On posjeduje tri kuće.", "kuća → kuće", False),   # ein Satz mit der Mehrzahl darin
    ("Pa brat", "brat → braća", False),             # die Einzahl allein weiter nicht
])
def test_pfeil_eintraege_mehrzahl_allein_nur_genau_gleich(seite, heute_stand, gehoert, eintrag, soll):
    seite.starten(stand=heute_stand())
    assert seite.js("([g, bs]) => passtGesprochen(g, bs)", [gehoert, eintrag]) is soll
    assert seite.fehler == []


def test_braca_in_der_aufgabe(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "brat → braća")
    z = _tippen(seite, ["brat"])
    assert z["ergebnisse"] == [], z
    z = _tippen(seite, ["brava"])
    assert z["ergebnisse"] == [] and "brava" in z["gehoert"], z
    z = _tippen(seite, ["braća"])
    assert z["ergebnisse"] == [True], z
    assert seite.fehler == []


# ---------------------------------------- Schritt 1: Android, nur bs-BA und hr-HR ---

@pytest.mark.parametrize("meldung", ["No match", "No speech input"])
def test_kein_treffer_hoert_auf_und_behaelt_die_sprache(mit_erkenner, meldung):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    fehler = _t(seite, "task.mikro_fehler")
    z = _tippen(seite, meldung, ["falsche Sprache"])       # ein zweiter Lauf taete hier so, als haette er gehoert
    assert z["aufrufe"] == ["bs-BA"] and z["gehoert"] == fehler and z["ergebnisse"] == [], z
    z = _tippen(seite, ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "bs-BA"] and z["ergebnisse"] == [True], z
    assert seite.fehler == []


@pytest.mark.parametrize("meldung", ["No match", "No speech input", "Network error"])
def test_zweimal_nichts_mit_bs_dann_hr_auch_in_der_naechsten_aufgabe(mit_erkenner, meldung):
    """Fuer Handys, die bs-BA nicht koennen und trotzdem "No match" melden. "Network
    error" zaehlt mit, solange das Handy Netz meldet."""
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    _tippen(seite, meldung)
    _tippen(seite, meldung)
    z = _tippen(seite, ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "bs-BA", "hr-HR"] and z["ergebnisse"] == [True], z
    seite.js(AUFGABE, "Hvala")
    assert _tippen(seite, ["hvala"])["aufrufe"] == ["hr-HR"]
    assert seite.fehler == []


def test_nie_sr_rs_oder_ohne_sprache(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    for _ in range(6):
        _tippen(seite, "No match")
    assert seite.js(LAGE)["aufrufe"] == ["bs-BA", "bs-BA", "hr-HR", "hr-HR", "hr-HR", "hr-HR"]
    seite.js(AUFGABE, "Hvala")
    for meldung in ["Didn't understand, please try again.", "error from server", "Client side error",
                    "RecognitionService busy", "Network error", "Irgendetwas Neues"]:
        _tippen(seite, meldung, meldung, meldung, meldung)
    assert set(seite.js(LAGE)["aufrufe"]) <= {"bs-BA", "hr-HR"}
    assert seite.fehler == []


def test_hat_bs_geliefert_bleibt_es_bei_bs(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    _tippen(seite, ["hvala"])
    seite.js(AUFGABE, "Hvala")
    for _ in range(3):
        _tippen(seite, "No match")
    z = _tippen(seite, ["hvala"])
    assert z["aufrufe"] == ["bs-BA"] * 4 and z["ergebnisse"] == [True], z
    assert seite.fehler == []


@pytest.mark.parametrize("meldung", ["Didn't understand, please try again.", "error from server"])
def test_andere_ablehnung_nimmt_im_selben_tipp_hr(mit_erkenner, meldung):
    """So meldet das Plugin auch "Sprache fehlt" (Android-Fehler 12 und 13 fallen in
    den Zweig mit dem ersten Text). Hier muss der Rueckfall sofort greifen - Handys ohne
    bs-BA duerfen nicht vom Sprechen abgeschnitten werden."""
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, meldung, ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "hr-HR"] and z["ergebnisse"] == [True], z
    # Die gemerkte Sprache gilt in der naechsten Aufgabe
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, ["hvala"])
    assert z["aufrufe"] == ["hr-HR"] and z["ergebnisse"] == [True], z
    assert seite.fehler == []


@pytest.mark.parametrize("meldung", ["Didn't understand, please try again.", "error from server"])
def test_hat_bs_geliefert_wird_hr_nur_ausweichsprache(mit_erkenner, meldung):
    """Ein einzelnes voruebergehendes Nein von bs-BA, nachdem bs-BA schon geliefert
    hat: hr-HR hilft im selben Tipp aus, der naechste Tipp beginnt wieder mit bs-BA.
    Vorher blieb die ganze restliche Sitzung bei hr-HR ("Tko" fuer "Ko?")."""
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    assert _tippen(seite, ["hvala"])["aufrufe"] == ["bs-BA"]
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, meldung, ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "hr-HR"] and z["ergebnisse"] == [True], z
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, ["hvala"])
    assert z["aufrufe"] == ["bs-BA"] and z["ergebnisse"] == [True], z
    assert seite.js("() => sprechSprache") == "bs-BA"
    assert seite.fehler == []


def test_ohne_bs_scheitert_es_nicht_an_bs(mit_erkenner):
    """Ein Handy ohne bs-BA, das "Sprache fehlt" meldet: hr-HR in jedem Tipp, und
    bs-BA wird in dieser Sitzung nicht mehr gefragt."""
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    fehlt = "Didn't understand, please try again."
    z = _tippen(seite, fehlt, "No match")
    assert z["aufrufe"] == ["bs-BA", "hr-HR"] and z["ergebnisse"] == [], z
    z = _tippen(seite, ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "hr-HR", "hr-HR"] and z["ergebnisse"] == [True], z
    assert seite.js("() => canSpeak") is True
    assert seite.fehler == []


def test_client_side_error_versucht_bs_zweimal_dann_hr(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, "Client side error", "Client side error", ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "bs-BA", "hr-HR"] and z["ergebnisse"] == [True], z
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, "Client side error", ["hvala"])     # hr-HR ist gemerkt, ein zweiter Versuch reicht
    assert z["aufrufe"] == ["hr-HR", "hr-HR"] and z["ergebnisse"] == [True], z
    assert seite.fehler == []


def test_busy_wiederholt_dieselbe_sprache_einmal(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    fehler = _t(seite, "task.mikro_fehler")
    z = _tippen(seite, "RecognitionService busy", "RecognitionService busy", ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "bs-BA"] and z["gehoert"] == fehler and z["ergebnisse"] == [], z
    z = _tippen(seite, "RecognitionService busy", ["hvala"])
    assert z["aufrufe"] == ["bs-BA", "bs-BA", "bs-BA", "bs-BA"] and z["ergebnisse"] == [True], z
    assert seite.fehler == []


@pytest.mark.parametrize("meldung", ["Network error", "Network timeout"])
def test_kein_netz_zeigt_die_offline_meldung_ohne_zweiten_aufruf(mit_erkenner, meldung):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, meldung, ["hvala"])
    assert z["aufrufe"] == ["bs-BA"] and z["gehoert"] == _t(seite, "task.mikro_offline") and z["ergebnisse"] == [], z
    assert seite.fehler == []


@pytest.mark.parametrize("meldung", ["Didn't understand, please try again.", "error from server"])
def test_wiederholtes_scheitern_beider_sprachen_nimmt_das_sprechen_fuer_die_sitzung(mit_erkenner, meldung):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    _tippen(seite, meldung, meldung)
    assert seite.js("() => canSpeak") is True                 # einmal ist noch kein Muster
    z = _tippen(seite, meldung, meldung)
    assert z["gehoert"] == _t(seite, "task.mikro_fehler"), z
    e = seite.js("""() => { const vorher = canSpeak;
        catIdx = 0; openLevel(0); buildLesson();
        return {vorher, abgelehnt: mikroAbgelehnt(), gemerkt: localStorage.getItem(MIKRO_NEIN),
                sprechen: Lx.queue.filter(a => a.typ === 'speak').length,
                aufrufe: window.__hoerer.aufrufe.slice()}; }""")
    assert e["vorher"] is False and e["abgelehnt"] is False and e["gemerkt"] is None and e["sprechen"] == 0, e
    assert set(e["aufrufe"]) <= {"bs-BA", "hr-HR"}, e
    # Beim naechsten Start wird neu versucht
    seite.neu_laden()
    assert seite.js("() => canSpeak") is True
    assert seite.fehler == []


def test_ein_start_ohne_antwort_endet_nach_der_zeitgrenze(mit_erkenner):
    seite = mit_erkenner
    seite.js("() => { SPRECH_ZEITGRENZE = 300; }")
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, {"warte": 1500, "matches": ["hvala"]})
    assert z["aufrufe"] == ["bs-BA"] and z["gehoert"] == _t(seite, "task.mikro_fehler") and z["ergebnisse"] == [], z
    assert seite.js("() => window.__hoerer.stops") >= 1
    seite.page.wait_for_timeout(1700)                         # das spaete Ergebnis ist inzwischen da
    z = seite.js(LAGE)
    assert z["ergebnisse"] == [] and z["gehoert"] == _t(seite, "task.mikro_fehler") and z["i"] == 0, z
    z = _tippen(seite, ["hvala"])
    assert z["ergebnisse"] == [True], z
    assert seite.fehler == []


def test_abgebrochen_startet_keine_weitere_sprache(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    seite.js("""() => { window.__hoerer.plan = ['Client side error']; const H = window.Capacitor.Plugins.SpeechRecognition;
        const alt = H.start;
        H.start = async (o) => { document.querySelector('#lBody #xMic').click(); return await alt(o); }; }""")
    seite.page.locator("#lBody #xMic").click()
    seite.page.wait_for_timeout(700)
    assert seite.js(LAGE)["aufrufe"] == ["bs-BA"]
    assert seite.fehler == []


def test_iphone_behaelt_seinen_weg(mit_iphone):
    """ZmajSprache lehnt bs-BA sofort ab und nach dem Start nie mehr - die Kette von
    vorher endet dort bei hr-HR. Keine Zeitgrenze der Seite: das iPhone hat eigene."""
    seite = mit_iphone
    seite.js("() => { SPRECH_ZEITGRENZE = 200; }")
    seite.js(AUFGABE, "Hvala")
    z = _tippen(seite, "Language not supported", {"warte": 600, "matches": ["хвала"]})
    assert z["aufrufe"] == ["bs-BA", "hr-HR"] and z["ergebnisse"] == [True], z
    assert seite.fehler == []


# ------------------------------------- Schritt 5: Ton aus, Browser ohne Antwort ---

TON_SPION = """() => { window.__ton = {wa: 0, pause: 0, marke: aufgabeMarke};
  const alt = window.waStopp; window.waStopp = () => { window.__ton.wa++; return alt(); };
  const p = spieler.pause.bind(spieler); spieler.pause = () => { window.__ton.pause++; return p(); }; }"""


def test_vorsprechen_dann_sofort_mikrofon_wird_noch_bewertet(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    assert seite.page.locator("#lBody #xListen").count() == 1
    seite.page.locator("#lBody #xListen").click()
    seite.js(TON_SPION)
    z = _tippen(seite, ["hvala"])
    ton = seite.js("() => window.__ton")
    assert ton["wa"] >= 1 and z["ergebnisse"] == [True], (ton, z)
    assert seite.fehler == []


def test_browser_ohne_ergebnis_und_ohne_fehler_zeigt_die_meldung(mit_browser):
    seite = mit_browser
    seite.js(AUFGABE, "Hvala")
    seite.js(TON_SPION)
    seite.js("() => { window.__sr.plan = [undefined]; }")
    seite.page.locator("#lBody #xMic").click()
    seite.page.wait_for_timeout(200)
    e = seite.js("() => ({gehoert: document.querySelector('#lBody #xHeard').textContent, starts: window.__sr.starts, "
                 "rec: document.querySelector('#lBody #xMic').classList.contains('rec'), ton: window.__ton})")
    assert e["starts"] == 1 and e["rec"] is False and e["gehoert"] == _t(seite, "task.mikro_fehler"), e
    assert e["ton"]["wa"] >= 1, e
    seite.js("() => { window.__sr.plan = [['hvala']]; }")
    seite.page.locator("#lBody #xMic").click()
    seite.page.wait_for_timeout(200)
    assert seite.js("() => Lx.results.slice()") == [True]
    assert seite.fehler == []


# ------------------ Entscheidung 3: Ueberspringen nach Fehlversuch, Tagesaufgabe ---

UEBERSPRINGEN_UND_ENDE = r"""
() => {
  document.querySelector('#lBody #xSkip').click();
  const richtig = [...document.querySelectorAll('#lBody .opt')].find(b => b.textContent === 'Hvala');
  richtig.click();
  lessonEnd();
  return {per: (tagwerk[today()] || {}).per || 0, skipped: Lx.skipped, ergebnisse: Lx.results.slice()};
}
"""


@pytest.mark.parametrize("plan", [["No match"], ["Network error"], [["kruh"]],
                                  ["Didn't understand, please try again.", "No match"]])
def test_ueberspringen_nach_gescheitertem_versuch_kostet_ohne_fehler_nicht(mit_erkenner, plan):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    _tippen(seite, *plan)
    e = seite.js(UEBERSPRINGEN_UND_ENDE)
    assert e == {"per": 1, "skipped": 1, "ergebnisse": ["skip", True]}, e
    assert seite.fehler == []


def test_ueberspringen_nach_zeitgrenze_kostet_ohne_fehler_nicht(mit_erkenner):
    seite = mit_erkenner
    seite.js("() => { SPRECH_ZEITGRENZE = 200; }")
    seite.js(AUFGABE, "Hvala")
    _tippen(seite, {"warte": 400, "matches": ["kruh"]})
    e = seite.js(UEBERSPRINGEN_UND_ENDE)
    assert e["per"] == 1 and e["skipped"] == 1, e
    assert seite.fehler == []


def test_ueberspringen_ohne_versuch_kostet_ohne_fehler_wie_bisher(mit_erkenner):
    seite = mit_erkenner
    seite.js(AUFGABE, "Hvala")
    e = seite.js(UEBERSPRINGEN_UND_ENDE)
    assert e == {"per": 0, "skipped": 1, "ergebnisse": ["skip", True]}, e
    assert seite.fehler == []


def test_ueberspringen_im_browser_nach_fehlversuch(mit_browser):
    seite = mit_browser
    seite.js(AUFGABE, "Hvala")
    seite.js("() => { window.__sr.plan = [{fehler: 'no-speech'}]; }")
    seite.page.locator("#lBody #xMic").click()
    seite.page.wait_for_timeout(200)
    e = seite.js(UEBERSPRINGEN_UND_ENDE)
    assert e["per"] == 1 and e["skipped"] == 1, e
    assert seite.fehler == []


# Eine Wiederholen-Runde (rundeStarten, Lx.topf), deren erste Aufgabe dieses Wort
# sprechen will. Echte Runden haben keine Sprechaufgaben - topfAufgabe() macht aus
# 'speak' 'mcrev' -, hier wird eine eingesetzt, damit topfEnde() und das Lx aus
# rundeStarten() mitgeprueft sind, falls sie einmal dazukommen.
RUNDE = r"""
(bs) => {
  const f = CATEGORIES.flatMap(c => c.words.map(w => ({w, c}))).find(x => x.w.bs === bs);
  if(!f) throw new Error('kein Wort ' + bs);
  topf = {}; topf['w:' + f.w.id] = {typ: 'mc', n: 0, z: 1000};
  homeMode = 'topf'; showHome(); startTopf();
  const mc = Lx.queue.find(a => a.typ === 'mc');
  if(!Lx.topf || !mc) throw new Error('keine Runde');
  Lx.queue = [{typ: 'speak', w: f.w}, mc]; Lx.i = 0; Lx.results = []; Lx.total = 2;
  showLessonTask();
  if(window.__hoerer) window.__hoerer.aufrufe.length = 0;
  return {topf: Lx.topf, skipNachFehler: Lx.skipNachFehler};
}
"""


@pytest.mark.parametrize("plan, per", [(["No match"], 1), ([["kruh"]], 1), (None, 0)])
def test_ueberspringen_in_der_runde_wie_in_der_lektion(mit_erkenner, plan, per):
    seite = mit_erkenner
    assert seite.js(RUNDE, "Hvala") == {"topf": True, "skipNachFehler": 0}
    if plan is not None:
        _tippen(seite, *plan)
    e = seite.js(UEBERSPRINGEN_UND_ENDE)
    assert e == {"per": per, "skipped": 1, "ergebnisse": ["skip", True]}, e
    assert seite.js("() => !!document.querySelector('#lBody .result-big') && Lx.topf") is True
    assert seite.fehler == []


# ----------- 17.11.2026: Sprechen faellt fuer die Sitzung aus, laufende Lektion ---

# Eine Lektion mit diesen Sprechaufgaben und danach einer Auswahl zum ersten Wort. ab:
# so viele Aufgaben sind schon richtig beantwortet, die naechste ist dran.
AUFGABEN = r"""
([liste, ab]) => {
  const finde = bs => {
    const f = CATEGORIES.flatMap(c => c.words.map(w => ({w, c}))).find(x => x.w.bs === bs);
    if(!f) throw new Error('kein Wort ' + bs);
    return f;
  };
  const erstes = finde(liste[0]);
  catIdx = CATEGORIES.indexOf(erstes.c); openLevel(catIdx); buildLesson();
  Lx.queue = [...liste.map(bs => ({typ: 'speak', w: finde(bs).w})), {typ: 'mc', w: erstes.w}];
  Lx.i = ab; Lx.results = Array(ab).fill(true); Lx.right = ab;
  document.getElementById('levelHome').style.display = 'none';
  document.getElementById('lesson').style.display = 'block';
  nurHerz(true); showLessonTask();
  if(window.__hoerer) window.__hoerer.aufrufe.length = 0;
}
"""

# n Sprechaufgaben ueberspringen, die Auswahl richtig beantworten, Lektion beenden.
UEBERSPRINGEN_N_UND_ENDE = r"""
(n) => {
  for(let k = 0; k < n; k++) document.querySelector('#lBody #xSkip').click();
  const richtig = [...document.querySelectorAll('#lBody .opt')].find(b => b.textContent === 'Hvala');
  richtig.click();
  lessonEnd();
  return {per: (tagwerk[today()] || {}).per || 0, skipped: Lx.skipped, ergebnisse: Lx.results.slice()};
}
"""

STAND_LEKTION = """() => ({an: canSpeak, typen: Lx.queue.map(a => a.typ), woerter: Lx.queue.map(a => a.w.bs), i: Lx.i,
                           punkte: document.querySelectorAll('#lBar i').length, gemerkt: localStorage.getItem(MIKRO_NEIN)})"""


@pytest.mark.parametrize("meldung", ["Didn't understand, please try again.", "error from server"])
def test_sprechen_aus_nimmt_die_restlichen_sprechaufgaben_aus_der_lektion(mit_erkenner, meldung):
    """Bis zum 17.11.2026 standen sie weiter da und liessen sich nur ueberspringen, und
    Ueberspringen ohne eigenen Versuch kostete "ohne Fehler". Die Aufgabe davor und die,
    an der es gerade gescheitert ist, bleiben."""
    seite = mit_erkenner
    seite.js(AUFGABEN, [["Hvala", "Da", "Ne"], 1])
    _tippen(seite, meldung, meldung)
    e = seite.js(STAND_LEKTION)
    assert e["an"] is True and e["typen"] == ["speak", "speak", "speak", "mc"], e   # einmal ist noch kein Muster
    _tippen(seite, meldung, meldung)
    e = seite.js(STAND_LEKTION)
    assert e == {"an": False, "typen": ["speak", "speak", "mc"], "woerter": ["Hvala", "Da", "Hvala"], "i": 1,
                 "punkte": 3, "gemerkt": None}, e
    e = seite.js(UEBERSPRINGEN_N_UND_ENDE, 1)
    assert e == {"per": 1, "skipped": 1, "ergebnisse": [True, "skip", True]}, e
    assert seite.fehler == []


def test_abgelehntes_mikrofon_laesst_die_sprechaufgaben_stehen(mit_erkenner):
    """Beim abgelehnten Mikrofon bleibt es, wie es war: Sprechaufgaben fallen erst ab der
    naechsten Lektion weg, und Ueberspringen ohne Versuch kostet "ohne Fehler"."""
    seite = mit_erkenner
    seite.js(AUFGABEN, [["Hvala", "Da"], 0])
    seite.js("""() => { const H = window.Capacitor.Plugins.SpeechRecognition;
        H.checkPermissions = async () => ({speechRecognition: 'denied'});
        H.requestPermissions = async () => ({speechRecognition: 'denied'}); }""")
    z = _tippen(seite)
    assert z["gehoert"] == _t(seite, "task.mikro_blockiert") and z["aufrufe"] == [], z
    e = seite.js(STAND_LEKTION)
    assert e["an"] is False and e["typen"] == ["speak", "speak", "mc"] and e["gemerkt"] == "1", e
    e = seite.js(UEBERSPRINGEN_N_UND_ENDE, 2)
    assert e == {"per": 0, "skipped": 2, "ergebnisse": ["skip", "skip", True]}, e
    assert seite.fehler == []
