# -*- coding: utf-8 -*-
"""Barrierefreiheit der Neuerungen seit v104 (17.10.2026): was zwei
Pruefungen nach WCAG 2.2 AA bei Satzbau, Laden und Drache fanden.

1  Das Ergebnis einer Aufgabe wird angesagt (unsichtbare aria-live-Region
   #ansage), auch bei den Kacheln und bei den Fragen zu einer Geschichte.
2  Kacheln: Zeile und Vorrat sind benannte Gruppen, Legen und Zuruecklegen
   werden angesagt, der Fokus bleibt bei einer sinnvollen Kachel.
3  Das Gleiten der Kacheln folgt bei JEDEM Legen dem Schalter "Animationen"
   und der Geraeteeinstellung "Bewegung reduzieren".
4  Laden: nach Kaufen und Anziehen steht der Fokus wieder auf dem Knopf des
   Artikels, es gibt eine kurze Ansage, und jeder Knopf nennt seinen Artikel.
5  Bosnischer Text traegt lang="bs" - und nur der: die Geschlechter der
   Grammatik ("weiblich (ona)") sind in der Sprache der App.
6  Die Punktereihe ueber einer Aufgabe ist eine Fortschrittsanzeige.
7  Schnelles Umziehen endet im neuen Aufzug, nicht im alten.
8  Das Eingabefeld der Lueckenaufgabe hat einen Namen in der Sprache der App.

Aufbau wie test_v106.py: jeder Test mit eigenem, leerem Browserkontext,
Geraetemodus; die Aufgabe wird gezielt auf den Bildschirm gelegt.
"""
import os

import pytest
from conftest import Seite
from test_v106 import AXE, AXE_ERNST, KACHEL_AUFGABE, UEBERGAENGE_ABWARTEN, _aufgabe, _genau

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Eine Wortaufgabe (mc, mcrev, intro, ...) allein in die Lektion legen.
WORT_AUFGABE = """(typ) => {
    openLevel(0); startLesson();
    const pool = CATEGORIES[0].words;
    const w = pool.find(x => x.bs.length > 3 && x.bs.indexOf(' / ') < 0 && x.bs.indexOf(' ') < 0);
    Lx.queue = [{typ, w, pool}]; Lx.i = 0; Lx.total = 1;
    showLessonTask();
    return {bs: w.bs, de: w.de};
}"""

# Was gerade den Fokus hat: in welchem Behaelter, an welcher Stelle.
FOKUS = """() => {
    const a = document.activeElement, p = a && a.parentElement;
    return {ort: p ? p.id : '', index: p ? [...p.children].indexOf(a) : -1,
            text: a === document.body ? '(body)' : (a.textContent || '').trim().slice(0, 80), platz: a.classList.contains('platz'),
            tragen: a.dataset ? (a.dataset.tragen || '') : '', ware: a.dataset ? (a.dataset.ware || '') : '',
            id: a.id || '', label: a.getAttribute('aria-label') || ''};
}"""

ANSAGE = "() => { const a = document.getElementById('ansage'); return a ? a.textContent : null; }"


def _ansage_abwarten(seite, teil):
    """Bis #ansage `teil` enthaelt. Die App leert die Region vor jeder Ansage
    und fuellt sie kurz danach - nie sofort."""
    seite.page.wait_for_function(
        "(teil) => { const a = document.getElementById('ansage'); return !!a && a.textContent.indexOf(teil) >= 0; }",
        arg=teil, timeout=5000)
    return seite.js(ANSAGE)


# ---------------------------------------------------------------------------
# 1  Ergebnis ansagen
# ---------------------------------------------------------------------------

def test_ansage_region_ist_unsichtbar_und_hoeflich(seite, heute_stand):
    seite.starten(stand=heute_stand())
    r = seite.js("""() => { const a = document.getElementById('ansage'); if(!a) return null;
        const b = a.getBoundingClientRect();
        return {live: a.getAttribute('aria-live'), atomar: a.getAttribute('aria-atomic'),
                breite: b.width, hoehe: b.height, versteckt: a.hidden || a.getAttribute('aria-hidden'),
                leer: a.textContent === ''}; }""")
    assert r, "keine Ansage-Region #ansage"
    assert r["live"] == "polite" and r["atomar"] == "true"
    assert r["breite"] <= 1 and r["hoehe"] <= 1, "die Ansage-Region ist sichtbar: %s" % r
    assert not r["versteckt"], "eine versteckte Region liest kein Screenreader vor"
    assert r["leer"]
    assert seite.fehler == []


def test_ansage_nach_pruefen_der_kacheln(seite, heute_stand):
    """Richtig: das Lob (Tačno, bosnisch ausgezeichnet). Falsch: die richtige
    Loesung, ebenfalls als Bosnisch."""
    satz, k, _ = _aufgabe(seite, heute_stand)
    k.legen(satz["teile"])
    k.pruefen.click()
    text = _ansage_abwarten(seite, "Tačno")
    assert satz["bs"] not in text, "bei richtig wird die Loesung nicht noch einmal vorgelesen"
    assert seite.js("() => !!document.querySelector('#ansage [lang=\"bs\"]')"), "Tačno ist nicht als Bosnisch markiert"

    seite.js(KACHEL_AUFGABE, satz["bs"])                   # dieselbe Aufgabe, jetzt falsch
    k.vorrat_ort.first.wait_for()
    assert seite.js(ANSAGE) == "", "die Ansage der vorigen Aufgabe steht noch da"
    k.legen(satz["teile"][::-1])
    k.pruefen.click()
    text = _ansage_abwarten(seite, satz["bs"])
    assert "Richtig wäre" in text
    bs = seite.js("() => [...document.querySelectorAll('#ansage [lang=\"bs\"]')].map(e => e.textContent)")
    assert satz["bs"] in bs, bs
    assert seite.fehler == []


def test_ansage_nach_falscher_auswahl_nennt_die_loesung(seite, heute_stand):
    seite.starten(stand=heute_stand())
    w = seite.js(WORT_AUFGABE, "mc")
    falsch = seite.page.locator("#lBody .opt").filter(has_not_text=w["bs"]).first
    falsch.click()
    text = _ansage_abwarten(seite, w["bs"])
    assert text.startswith("Richtig wäre"), text
    # auch das sichtbare Feld ist unveraendert, nur ausgezeichnet
    assert seite.page.locator("#lBody #xFb").inner_text().strip() == "Richtig wäre: " + w["bs"]
    assert seite.fehler == []


def test_ansage_nach_mcrev_ohne_bosnisch_markierung_der_bedeutung(seite, heute_stand):
    """Bei 'Was bedeutet ...' ist die Loesung die Bedeutung - die ist nicht bosnisch."""
    seite.starten(stand=heute_stand())
    w = seite.js(WORT_AUFGABE, "mcrev")
    seite.page.locator("#lBody .opt").filter(has_not_text=w["de"]).first.click()
    _ansage_abwarten(seite, w["de"])
    bs = seite.js("() => [...document.querySelectorAll('#ansage [lang=\"bs\"]')].map(e => e.textContent)")
    assert w["de"] not in bs, "die Bedeutung ist als Bosnisch markiert"
    assert seite.fehler == []


def test_ansage_nach_geschichten_frage(seite, heute_stand):
    """Die Fragen zu einer Geschichte laufen nicht ueber renderTask() - ihr
    Ergebnis stand bis zum 17.10.2026 nur in #rFb und wurde nie angesagt.
    Falsch: die Loesung (in der Sprache der App, also ohne lang="bs").
    Die naechste Frage leert die Ansage, richtig sagt Tačno an."""
    seite.starten(stand=heute_stand())
    q = seite.js("""() => { openStory(0); stilleBitte();
        return STORIES[0].fragen.slice(0, 2).map(f => ({richtig: f.richtig})); }""")
    assert len(q) == 2, "die erste Geschichte hat keine zwei Fragen"
    opts = seite.page.locator("#rQ #rOpts .opt")
    opts.filter(has_not_text=_genau(q[0]["richtig"])).first.click()
    text = _ansage_abwarten(seite, q[0]["richtig"])
    assert text.startswith("Richtig wäre"), text
    assert seite.page.locator("#rFb").inner_text().strip() == "Richtig wäre: " + q[0]["richtig"]
    assert seite.js("() => document.querySelectorAll('#ansage [lang]').length") == 0, \
        "die Antwort einer Geschichten-Frage ist nicht bosnisch"
    weiter = seite.page.locator("#rQ .weiterbox .btn")
    seite.page.wait_for_function("() => document.activeElement && document.activeElement.matches('#rQ .weiterbox .btn')",
                                 timeout=5000)
    weiter.click()
    assert seite.js(ANSAGE) == "", "die Ansage der vorigen Frage steht noch da"
    assert seite.page.locator("#rFb").inner_text().strip() == ""
    opts.filter(has_text=_genau(q[1]["richtig"])).first.click()
    _ansage_abwarten(seite, "Tačno")
    assert seite.js("() => !!document.querySelector('#ansage [lang=\"bs\"]')"), "Tačno ist nicht als Bosnisch markiert"
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# 2  Kacheln: Gruppen, Ansage, Fokus
# ---------------------------------------------------------------------------

def test_kacheln_zeile_und_vorrat_sind_benannte_gruppen(seite, heute_stand):
    _aufgabe(seite, heute_stand)
    g = seite.js("""() => ['xZeile', 'xBank'].map(id => { const e = document.querySelector('#lBody #' + id);
        return {rolle: e.getAttribute('role'), name: e.getAttribute('aria-label'), lang: e.getAttribute('lang')}; })""")
    assert g[0] == {"rolle": "group", "name": "Dein Satz", "lang": None}
    assert g[1] == {"rolle": "group", "name": "Wörter", "lang": None}
    assert seite.fehler == []


def test_kacheln_fokus_und_ansage_beim_legen_und_zuruecklegen(seite, heute_stand):
    _, k, _ = _aufgabe(seite, heute_stand)
    bank = seite.page.locator("#lBody #xBank .kachel")
    zeile = seite.page.locator("#lBody #xZeile .kachel")
    n = bank.count()
    assert n >= 5, "zu wenige Kacheln fuer diesen Test: %d" % n
    texte = [t.strip() for t in bank.all_inner_texts()]

    # Legen: der Fokus geht zur naechsten Kachel im Vorrat, nicht zur ersten
    bank.nth(1).press("Enter")
    assert seite.js(FOKUS)["ort"] == "xBank" and seite.js(FOKUS)["index"] == 2, seite.js(FOKUS)
    _ansage_abwarten(seite, "Dein Satz: " + texte[1])

    # Die letzte gelegt: dahinter ist nichts mehr, also die davor
    bank.nth(n - 1).press("Enter")
    f = seite.js(FOKUS)
    assert (f["ort"], f["index"], f["platz"]) == ("xBank", n - 2, False), f
    _ansage_abwarten(seite, "Dein Satz: %s %s" % (texte[1], texte[n - 1]))

    # Zuruecklegen: der Fokus bleibt in der Zeile, an derselben Stelle
    zeile.nth(0).press("Enter")
    f = seite.js(FOKUS)
    assert (f["ort"], f["index"], f["text"]) == ("xZeile", 0, texte[n - 1]), f
    _ansage_abwarten(seite, "Dein Satz: " + texte[n - 1])

    # Die letzte aus der Zeile: dann auf die Kachel, die gerade zurueckging
    zeile.nth(0).press("Enter")
    f = seite.js(FOKUS)
    assert (f["ort"], f["index"], f["text"]) == ("xBank", n - 1, texte[n - 1]), f
    _ansage_abwarten(seite, "Tippe die Wörter")
    assert k.gelegt() == []
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# 3  Gleiten nur, wenn Bewegung erlaubt ist - bei jedem Legen neu gefragt
# ---------------------------------------------------------------------------

# Eine Kachel antippen und sofort zaehlen, wie viele Kacheln gleiten. Gezaehlt
# werden nur Web-Animationen (k.animate) - CSS-Uebergaenge haben damit nichts zu tun.
GLEITEN_ZAEHLEN = """() => {
    const b = document.querySelector('#lBody #xBank .kachel:not(.platz)');
    b.click();
    return [...document.querySelectorAll('#lBody .kachel')].flatMap(k => k.getAnimations())
        .filter(a => !(a instanceof CSSTransition) && !(a instanceof CSSAnimation)).length;
}"""


def test_kacheln_gleiten_folgt_schalter_und_geraet(seite, heute_stand):
    _aufgabe(seite, heute_stand)
    assert seite.js(GLEITEN_ZAEHLEN) > 0, "mit Animationen gleitet keine Kachel"
    # der Schalter "Animationen" in den Einstellungen - genau das tut er
    seite.js("() => { animOn = false; applyAnim(); }")
    assert seite.js(GLEITEN_ZAEHLEN) == 0, "Schalter Animationen aus, die Kacheln gleiten trotzdem"
    seite.js("() => { animOn = true; applyAnim(); }")
    # das Geraet stellt erst NACH dem Start auf "Bewegung reduzieren"
    seite.page.emulate_media(reduced_motion="reduce")
    assert seite.js(GLEITEN_ZAEHLEN) == 0, "Bewegung reduzieren am Geraet, die Kacheln gleiten trotzdem"
    seite.page.emulate_media(reduced_motion="no-preference")
    assert seite.js(GLEITEN_ZAEHLEN) > 0, "nach dem Zuruecksetzen gleitet nichts mehr"
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# 5  lang="bs"
# ---------------------------------------------------------------------------

LANG_VON = """(sel) => [...document.querySelectorAll(sel)].map(e => e.getAttribute('lang'))"""


def test_bosnischer_text_traegt_lang_bs(seite, heute_stand):
    satz, k, _ = _aufgabe(seite, heute_stand)
    assert set(seite.js(LANG_VON, "#lBody .kachel")) == {"bs"}
    k.legen(satz["teile"][:1])
    assert set(seite.js(LANG_VON, "#lBody .kachel")) == {"bs"}, "eine gelegte Kachel oder ein Platzhalter ohne lang"
    k.legen(satz["teile"][1:])
    k.pruefen.click()
    assert seite.js(LANG_VON, "#lBody .loesung .lbs") == ["bs"]
    assert seite.js(LANG_VON, "#lBody .loesung .lde") == [None]
    assert seite.js(LANG_VON, "#lBody #xFb") == [None], "das Feld selbst ist in der Sprache der App"

    seite.js(WORT_AUFGABE, "intro")
    assert seite.js(LANG_VON, "#lBody .big") == ["bs"]
    assert seite.js(LANG_VON, "#lBody .de") == [None]
    seite.js(WORT_AUFGABE, "mc")
    assert set(seite.js(LANG_VON, "#lBody .opt")) == {"bs"}
    assert seite.js(LANG_VON, "#lBody .prompt") == [None]
    seite.js(WORT_AUFGABE, "mcrev")
    assert seite.js(LANG_VON, "#lBody .big") == ["bs"]
    assert set(seite.js(LANG_VON, "#lBody .opt")) == {None}, "die Bedeutungen sind nicht bosnisch"
    assert seite.js("() => document.documentElement.lang") == "de"
    assert seite.fehler == []


# Eine Grammatikaufgabe allein in die Lektion legen - die erste, deren
# richtige Antwort `antwort` ist (gesucht im geladenen Inhalt, Sprache de).
GRAM_AUFGABE = """(antwort) => {
    openLevel(0); startLesson();
    const g = Object.values(GRAMMAR).flatMap(l => l.uebungen || []).find(u => u.richtig === antwort);
    if(!g) return null;
    Lx.queue = [{typ: 'gram', g}]; Lx.i = 0; Lx.total = 1;
    showLessonTask();
    return {richtig: g.richtig, optionen: g.optionen.slice()};
}"""


def test_grammatik_geschlecht_ist_nicht_bosnisch(seite, heute_stand):
    """Bei "Welches Geschlecht hat „kuća“?" sind die Antworten "männlich (on)",
    "weiblich (ona)", "sächlich (ono)" in der Sprache der App. Weder die
    Knoepfe noch die Loesung in Rueckmeldung und Ansage tragen lang="bs".
    Eine gewoehnliche Grammatikaufgabe ("___ sestra" mit "moja") behaelt es."""
    seite.starten(stand=heute_stand())
    g = seite.js(GRAM_AUFGABE, "weiblich (ona)")
    assert g, "keine Geschlechtsaufgabe im Inhalt"
    assert "männlich (on)" in g["optionen"]
    assert set(seite.js(LANG_VON, "#lBody .opt")) == {None}, "die Geschlechter sind als Bosnisch markiert"
    seite.page.locator("#lBody .opt").filter(has_not_text=_genau(g["richtig"])).first.click()
    text = _ansage_abwarten(seite, g["richtig"])
    assert text.startswith("Richtig wäre"), text
    assert seite.page.locator("#lBody #xFb").inner_text().strip() == "Richtig wäre: " + g["richtig"]
    assert seite.js("() => document.querySelectorAll('#lBody #xFb [lang], #ansage [lang]').length") == 0, \
        "die Loesung ist als Bosnisch markiert"

    g = seite.js(GRAM_AUFGABE, "moja")
    assert g, "keine Aufgabe mit der Antwort moja"
    assert set(seite.js(LANG_VON, "#lBody .opt")) == {"bs"}
    seite.page.locator("#lBody .opt").filter(has_not_text=_genau("moja")).first.click()
    _ansage_abwarten(seite, "moja")
    bs = seite.js("() => [...document.querySelectorAll('#ansage [lang=\"bs\"]')].map(e => e.textContent)")
    assert "moja" in bs, bs
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# 8  Das Lueckenfeld hat einen Namen
# ---------------------------------------------------------------------------

LUECKE_AUFGABE = """() => {
    openLevel(0); startLesson();
    const s = SENTENCES.find(x => x.text.indexOf('___') > 0 && !/___\\s*[.!?]?$/.test(x.text));
    Lx.queue = [{typ: 'gap', s}]; Lx.i = 0; Lx.total = 1;
    showLessonTask();
    return {text: s.text};
}"""


def test_lueckenfeld_hat_namen_in_der_sprache_der_app(seite, heute_stand):
    """Vorher meldete ein Screenreader nur "Eingabefeld". Der Name ist
    deutsch und liegt nicht in einem lang="bs"; bosnisch sind die Satzteile
    davor und danach. Zu sehen ist der Satz wie vorher."""
    seite.starten(stand=heute_stand())
    s = seite.js(LUECKE_AUFGABE)
    feld = seite.js("""() => { const e = document.querySelector('#lBody #xIn');
        const l = e.parentElement.closest('[lang]');
        return {name: e.getAttribute('aria-label'), lang: e.getAttribute('lang'),
                umgebung: l === document.documentElement ? 'html' : (l ? l.getAttribute('lang') : null),
                fokus: document.activeElement === e}; }""")
    assert feld == {"name": "Tippe das fehlende Wort ein", "lang": None, "umgebung": "html", "fokus": True}, feld
    teile = seite.js(LANG_VON, "#lBody .sentence > span")
    assert teile and set(teile) == {"bs"}, teile
    sicht = seite.js("""() => { const z = document.querySelector('#lBody .sentence'), e = z.querySelector('#xIn');
        return [...z.childNodes].map(n => n === e ? '___' : n.textContent).join(''); }""")
    assert sicht == s["text"], "der Satz sieht anders aus als vorher: %r" % sicht
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# 6  Punktereihe als Fortschrittsanzeige
# ---------------------------------------------------------------------------

BALKEN = """(id) => { const e = document.getElementById(id);
    return {rolle: e.getAttribute('role'), min: e.getAttribute('aria-valuemin'), max: e.getAttribute('aria-valuemax'),
            jetzt: e.getAttribute('aria-valuenow'), name: e.getAttribute('aria-label')}; }"""


def test_punktereihe_ist_fortschrittsanzeige(seite, heute_stand):
    seite.starten(stand=heute_stand())
    n = seite.js("() => { openLevel(0); startLesson(); return Lx.queue.length; }")
    assert seite.js(BALKEN, "lBar") == {"rolle": "progressbar", "min": "0", "max": str(n), "jetzt": "0",
                                        "name": "Frage 1 von %d" % n}
    assert seite.js("() => Lx.queue[0].typ") == "intro"
    seite.page.locator("#lBody #xNext").click()
    assert seite.js(BALKEN, "lBar")["jetzt"] == "1"
    assert seite.js(BALKEN, "lBar")["name"] == "Frage 2 von %d" % n

    seite.js("() => { CATEGORIES[0].words.forEach(w => known.add(w.id)); openLevel(0); startTest(); }")
    b = seite.js(BALKEN, "tBar")
    m = seite.js("() => Tx.qs.length")
    assert b == {"rolle": "progressbar", "min": "0", "max": str(m), "jetzt": "0", "name": "Frage 1 von %d" % m}
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# 4  Laden: Fokus, Ansage, Namen
# ---------------------------------------------------------------------------

def _laden(seite, heute_stand, reiter="kopf"):
    seite.starten(stand=heute_stand(besitz=["hut", "brille"], muenzen_ges=5000))
    seite.js("(r) => { festHeute = () => ''; showLaden(); ladenReiter = r; renderLaden(); }", reiter)


def test_laden_fokus_und_ansage_nach_anziehen_und_ablegen(seite, heute_stand):
    _laden(seite, heute_stand)
    seite.page.locator('#ladenWaren button[data-tragen="hut"]').click()
    f = seite.js(FOKUS)
    assert f["tragen"] == "hut", "der Fokus ist nach dem Anziehen weg: %s" % f
    assert f["text"] == "Abnehmen"
    assert f["label"].startswith("Abnehmen") and "Mütze" in f["label"], f["label"]
    _ansage_abwarten(seite, "Angezogen.")

    seite.page.locator('#ladenWaren button[data-tragen="hut"]').click()
    f = seite.js(FOKUS)
    assert (f["tragen"], f["text"]) == ("hut", "Tragen"), f
    _ansage_abwarten(seite, "Abgenommen.")
    assert seite.fehler == []


def test_laden_fokus_und_ansage_nach_kaufen(seite, heute_stand):
    _laden(seite, heute_stand)
    seite.page.locator('#ladenWaren button[data-ware="fes"]').click()
    f = seite.js(FOKUS)
    assert f["tragen"] == "fes", "nach dem Kauf steht der Fokus nicht auf dem gekauften Stueck: %s" % f
    _ansage_abwarten(seite, "Gekauft.")
    # Serienschutz: nach dem Kauf ist das Hoechste erreicht, der Knopf aus -
    # dann bleibt der Fokus in der Nahe, auf der Reiterwahl
    seite.js("() => { ladenReiter = 'vorrat'; renderLaden(); }")
    seite.page.locator('#ladenWaren button[data-ware="schutz"]').click()
    assert seite.page.locator('#ladenWaren button[data-ware="schutz"]').is_disabled()
    assert seite.js(FOKUS)["id"] == "ladenKopf"
    _ansage_abwarten(seite, "Gekauft.")
    assert seite.fehler == []


def test_laden_jeder_knopf_nennt_seinen_artikel(seite, heute_stand):
    """Tragen, Abnehmen, Preis und Vollversion - in jedem Reiter steht der Name
    des Artikels im Namen des Knopfes, und der sichtbare Text vorn (WCAG 2.5.3)."""
    _laden(seite, heute_stand)
    probleme = seite.js("""() => {
        const out = [];
        for(const g of GRUPPEN){
            ladenReiter = g.id; renderLaden();
            document.querySelectorAll('#ladenWaren .ware').forEach(z => {
                const titel = z.querySelector('.wt').textContent.trim();
                z.querySelectorAll('button[data-tragen], button[data-ware], button[data-vollstueck], button.kauf:not([data-videoleben]):not(#ladenVoll)').forEach(b => {
                    const name = b.getAttribute('aria-label') || '';
                    const sicht = b.textContent.trim();
                    if(!name.startsWith(sicht) || name.indexOf(titel) < 0) out.push(g.id + ': "' + sicht + '" heisst "' + name + '" (Artikel ' + titel + ')');
                });
            });
        }
        return out; }""")
    assert probleme == [], "\n".join(probleme)
    assert seite.fehler == []


def test_laden_reiterwahl_gibt_den_fokus_zurueck(seite, heute_stand):
    _laden(seite, heute_stand, "vorrat")
    seite.page.locator("#ladenKopf").click()
    seite.page.locator('#ladenListe .sprachzeile[data-gruppe="brille"]').click()
    assert seite.js(FOKUS)["id"] == "ladenKopf"
    assert seite.js("() => ladenReiter") == "brille"
    assert seite.fehler == []


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_laden_kostueme_ohne_ernste_verstoesse(browser, basis, heute_stand, schema):
    kontext = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                                  service_workers="block", color_scheme=schema)
    try:
        seite = Seite(kontext.new_page(), basis)
        _laden(seite, heute_stand)
        seite.page.add_script_tag(path=AXE)
        funde = []
        for reiter in ["kopf", "farbe", "effekt"]:
            seite.js("(r) => { ladenReiter = r; renderLaden(); }", reiter)
            seite.js(UEBERGAENGE_ABWARTEN)
            funde += ["%s/%s: %s" % (schema, reiter, v) for v in seite.js(AXE_ERNST)]
        assert funde == [], "\n".join(funde)
        assert seite.fehler == []
    finally:
        kontext.close()


# ---------------------------------------------------------------------------
# 7  Schnelles Umziehen
# ---------------------------------------------------------------------------

def test_schnelles_umziehen_endet_im_neuen_aufzug(seite, heute_stand):
    """Drei Stuecke in einem Zug anziehen, ohne aufs Laden zu warten. Vorher
    kehrte mountZmaj() beim zweiten und dritten Mal sofort zurueck, und die
    laufende Ladung setzte den Stand mit nur dem ersten Stueck. Am Ende muss
    der Drache der Startseite den neuen Aufzug tragen - und es darf nicht
    endlos nachgeladen werden."""
    seite.starten(stand=heute_stand(besitz=["hut", "brille", "gruen"]))
    fertig = """() => { const e = document.querySelector('#zmajHome .zmaj-anim');
        return !!(e && e._anim && e._anim.isLoaded); }"""
    seite.page.wait_for_function(fertig, timeout=30000)
    seite.js("""() => { festHeute = () => '';
        window.__ladungen = 0; const alt = zmajDaten;
        zmajDaten = (...a) => { window.__ladungen++; return alt(...a); };
        trage('hut'); trage('brille'); trage('gruen'); }""")
    seite.page.wait_for_function("""() => { const e = document.querySelector('#zmajHome .zmaj-anim');
        return !!(e && e._anim && e._anim.isLoaded && !e._laedt && e._stand === zierratSchluessel()); }""",
                                 timeout=30000)
    stand = seite.js("() => document.querySelector('#zmajHome .zmaj-anim')._stand")
    assert "hut" in stand and "brille" in stand and stand.endswith("|gruen"), stand
    vorher = seite.js("() => window.__ladungen")
    seite.page.wait_for_timeout(1500)
    nachher = seite.js("() => window.__ladungen")
    assert nachher == vorher, "der Drache laedt immer weiter nach (%d -> %d)" % (vorher, nachher)
    anzahl = seite.js("() => document.querySelectorAll('.zmaj-anim').length")
    assert nachher <= 3 * max(anzahl, 1), "%d Ladungen fuer %d Drachen" % (nachher, anzahl)
    bilder = seite.js("""() => [...document.querySelectorAll('#zmajHome .zmaj-anim svg image')]
        .map(i => i.getAttribute('href') || i.getAttributeNS('http://www.w3.org/1999/xlink', 'href') || '')""")
    for stueck in ("hut", "brille"):
        if os.path.isdir(os.path.join(WURZEL, "web", "maskottchen", "zierrat", stueck)):
            assert any("zierrat/%s/" % stueck in b for b in bilder), "%s fehlt am Drachen" % stueck
    if os.path.isdir(os.path.join(WURZEL, "web", "maskottchen", "haut", "gruen")):
        assert any("haut/gruen/" in b for b in bilder), "die gruene Haut fehlt"
    assert seite.fehler == []
