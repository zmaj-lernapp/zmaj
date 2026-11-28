# -*- coding: utf-8 -*-
"""Kein heller Antwortknopf nach einem Fingertipp (15.11.2026, Offen-Liste 5b).

Ajdin am iPhone (TestFlight 1.3): "manchmal ist wenn man 4 antwortmöglichkeiten
hat der unten rechts eine hellere farbe man würde denken das das richtig sei und
ausversehen drauf tippen".

Ursache, gemessen mit Playwright bei 360 x 640 und Touch: Nach einem Tipp bleibt
:hover an der Stelle des Fingers haengen. WebKit, die Engine des iPhones, gibt es
nach dem Neuzeichnen an das Element weiter, das jetzt dort liegt. "Weiter" unter
einem neuen Wort lag bei y 365-411, der Antwortknopf unten rechts der Frage
danach bei y 320-379: wer Weiter oben rechts antippte, hatte danach den Finger
auf diesem Knopf, und .opt:hover gab ihm denselben hellen Grund wie "richtig"
(--primary-soft) und einen blauen Rand. Chromium reicht :hover nicht weiter, laesst
es aber am angetippten Knopf selbst stehen - ein falsch angetippter Knopf bekam so
den hellen Grund von richtig.

Seitdem gilt jedes :hover nur unter @media (hover:hover) and (pointer:fine), der
Fokus der Reiterwahl (button.field) nur ueber :focus-visible. Geprueft wird mit
echten Tipps (touchscreen.tap) in Chromium und - wenn Playwright es auf dem
Rechner hat - in WebKit, hell und dunkel: Lektion (neues Wort, Auswahl, Hoeren,
Bedeutung, eine falsche Antwort), Lueckensatz und Grammatik, Level-Test,
Einstufung, Fragen zur Geschichte und Satzbau-Kacheln. Dazu: mit der Maus leuchtet ein offener Knopf weiter auf,
mit der Tastatur bleibt der Fokusring sichtbar, und axe findet in der Lektion
nach den Tipps nichts Ernstes.
"""
import os

import pytest
from conftest import Seite, frisch_abwarten

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXE = os.path.join(WURZEL, "tests_e2e", "vendor", "axe.min.js")

MOTOREN = ["chromium", "webkit"]
SCHEMATA = ["light", "dark"]

# Vier kurze Woerter aus den Grundlagen, jedes mit eigener Bedeutung. Mit genau
# diesen vier als Vorrat stehen in jeder Auswahl dieselben vier Knoepfe, jeder in
# einer Zeile - die Lage der Knoepfe haengt dann nicht vom Zufall ab.
KURZ = r"""
() => {
  const raus = /[\/()]/;
  const out = [], bed = new Set();
  for(const w of CATEGORIES[0].words){
    if(w.bs.length > 8 || w.de.length > 10 || raus.test(w.bs + w.de)) continue;
    const b = _bedeutung(w.de);
    if(bed.has(b) || out.some(x => geschwister(x).some(g => g.bs === w.bs))) continue;
    bed.add(b); out.push(w);
    if(out.length === 4) break;
  }
  window.__kurz = out;
  return out.map(w => w.bs);
}
"""

# Die richtige Antwort der laufenden Aufgabe in Lektion (Lx), Test (Tx) oder
# Einstufung (Ex) - wie DURCHSPIELEN in conftest.py.
SOLL = r"""
(art) => {
  const X = art === 'Lx' ? Lx : (art === 'Tx' ? Tx : Ex);
  const q = (X.qs || X.queue)[X.i];
  return q.typ === 'gram' ? q.g.richtig : (q.typ === 'mcrev' ? q.w.de : q.w.bs);
}
"""

# Mitte eines Knopfs, ins Bild geholt. text: genau dieser Knopf, falsch: irgendein
# anderer. Gibt auch den Text zurueck, damit man weiss, welcher getroffen wurde.
LAGE = r"""
([sel, text, falsch]) => {
  const alle = [...document.querySelectorAll(sel)];
  const b = text === null ? alle[0] : alle.find(o => falsch ? o.textContent !== text : o.textContent === text);
  if(!b) return null;
  b.scrollIntoView({block: 'nearest'});
  const r = b.getBoundingClientRect();
  return {x: r.x, y: r.y, w: r.width, h: r.height, t: b.textContent};
}
"""

# Was ein Knopf gerade zeigt. Dazu der Grund und Rand eines unberuehrten Knopfs
# derselben Stelle: ein frischer .opt weit links ausserhalb des Bildes im selben
# Kasten, also mit denselben Farben der Sektion, aber nie unter einem Finger.
STILE = r"""
(sel) => {
  const farben = o => { const c = getComputedStyle(o);
    return {grund: c.backgroundColor,
            rand: [c.borderTopColor, c.borderRightColor, c.borderBottomColor, c.borderLeftColor].join(' ')}; };
  const alle = [...document.querySelectorAll(sel)];
  if(!alle.length) return null;
  const probe = document.createElement('button');
  probe.className = 'opt'; probe.textContent = 'x';
  probe.style.cssText = 'position:fixed; left:-9999px; top:0; transition:none';
  alle[0].parentElement.appendChild(probe);
  const frisch = farben(probe);
  probe.remove();
  return {frisch, knoepfe: alle.map(o => Object.assign(farben(o),
    {t: o.textContent, unter: o.matches(':hover'), aus: o.disabled, ring: o.matches(':focus-visible'),
     fokus: o === document.activeElement}))};
}
"""

# Eine Farbe so, wie getComputedStyle sie schreibt (rgb(...)), im Kasten sel.
FARBE = r"""
([sel, wert]) => {
  const p = document.createElement('i');
  p.style.cssText = 'position:fixed; left:-9999px; color:' + wert;
  document.querySelector(sel).appendChild(p);
  const c = getComputedStyle(p).color;
  p.remove();
  return c;
}
"""


@pytest.fixture(params=MOTOREN)
def motor(request, browser):
    """Chromium immer, WebKit nur wenn da (siehe conftest.py, webkit)."""
    return browser if request.param == "chromium" else request.getfixturevalue("webkit")


def _oeffnen(b, basis, heute_stand, schema, touch=True):
    """Ein Handy mit 360 Punkten Breite und Touch - oder ohne Touch mit Maus."""
    ctx = b.new_context(viewport={"width": 360, "height": 640}, device_scale_factor=2,
                        has_touch=touch, is_mobile=touch, locale="de-DE",
                        color_scheme=schema, service_workers="block")
    s = Seite(ctx.new_page(), basis)
    s.starten(stand=heute_stand())
    # Den Vorspann per Skript wegtippen: ein echter Tipp setzte den Finger schon.
    s.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
    s.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    if touch:
        assert s.js("() => matchMedia('(hover:hover) and (pointer:fine)').matches") is False
    assert len(s.js(KURZ)) == 4
    return ctx, s


def _tipp(s, x, y):
    s.page.touchscreen.tap(x, y)


def _tipp_auf(s, sel, text=None, falsch=False, fx=0.5, fy=0.5):
    lage = s.js(LAGE, [sel, text, falsch])
    assert lage, "nichts gefunden: %s %r" % (sel, text)
    s.page.wait_for_timeout(80)                  # nach scrollIntoView
    lage = s.js(LAGE, [sel, lage["t"], False])
    x, y = lage["x"] + lage["w"] * fx, lage["y"] + lage["h"] * fy
    frisch_abwarten(s.page)                      # Doppeltipp-Sperre nach neuer Aufgabe
    _tipp(s, x, y)
    return x, y, lage["t"]


def _bis_weiter(s, feld):
    s.page.wait_for_function("(f) => !!document.querySelector('#' + f + ' .weiterbox .btn')", arg=feld,
                             timeout=8000)
    # WEITER_NACH (900 ms): erst dann nimmt das Feld den Tipp, und Weiter hat den Fokus.
    s.page.wait_for_timeout(1150)


def _weiter(s, feld):
    """Weiter rechts antippen, wo der Daumen der rechten Hand hinkommt."""
    return _tipp_auf(s, "#%s .weiterbox .btn" % feld, fx=0.8)


def _alle_gleich(s, sel, wo):
    """Alle Knoepfe zeigen denselben Grund und Rand - den eines unberuehrten."""
    s.page.wait_for_timeout(350)                 # .opt hat transition .12s
    st = s.js(STILE, sel)
    assert st and len(st["knoepfe"]) >= 2, (wo, st)
    falsch = [k for k in st["knoepfe"] if (k["grund"], k["rand"]) != (st["frisch"]["grund"], st["frisch"]["rand"])]
    assert not falsch, "%s: heller Knopf %s, frisch %s" % (wo, falsch, st["frisch"])
    # Nach Fingertipps zeigt kein Knopf einen Fokusring (der ist fuer die Tastatur).
    assert not [k for k in st["knoepfe"] if k["ring"]], (wo, st["knoepfe"])
    return st


def _antworten_und_weiter(s, art, feld, wo):
    """Echter Tipp auf die richtige Antwort, dann auf Weiter; danach die neue Frage pruefen."""
    soll = s.js(SOLL, art)
    alt = s.js("(f) => document.getElementById(f).dataset.i", feld)
    _tipp_auf(s, "#%s .opt" % feld, soll)
    _bis_weiter(s, feld)
    _weiter(s, feld)
    s.page.wait_for_function("([f, alt]) => document.getElementById(f).dataset.i !== alt"
                             " && !document.querySelector('#' + f + ' .weiterbox')", arg=[feld, alt], timeout=8000)
    st = _alle_gleich(s, "#%s .opt" % feld, wo)
    # Jede Frage wird neu gebaut (innerHTML): der Fokus von Weiter geht mit dem Knopf
    # verloren und landet auf keinem der neuen Antwortknoepfe.
    assert not [k for k in st["knoepfe"] if k["fokus"]], (wo, st["knoepfe"])
    return st


def _ohne_fehler(s):
    assert s.fehler == [], s.fehler
    assert s.fremd == [], s.fremd


@pytest.mark.parametrize("schema", SCHEMATA)
def test_lektion_kein_heller_knopf_nach_dem_tipp(motor, basis, heute_stand, schema):
    """Der Fall vom iPhone: ein neues Wort, Weiter oben rechts, danach die Frage.
    Der Finger liegt nachweislich auf ihrem Knopf unten rechts. Dann Auswahl,
    Hoeren und Bedeutung mit echten Tipps, und einmal falsch."""
    ctx, s = _oeffnen(motor, basis, heute_stand, schema)
    try:
        s.js("""async () => { const warte = ms => new Promise(r => setTimeout(r, ms));
            openLevel(0); await warte(300); startLesson(); await warte(300);
            const k = window.__kurz;
            Lx.queue = [{typ:'intro', w:k[0], pool:k}, {typ:'mc', w:k[0], pool:k}, {typ:'listen', w:k[1], pool:k},
                        {typ:'mcrev', w:k[2], pool:k}, {typ:'mc', w:k[3], pool:k}, {typ:'mc', w:k[1], pool:k}];
            Lx.i = 0; Lx.total = Lx.queue.length;
            // Erst die Frage nach dem neuen Wort zeichnen: wo steht ihr Knopf unten rechts?
            Lx.i = 1; showLessonTask(); await warte(300); }""")
        ecke = s.js("""() => { const r = [...document.querySelectorAll('#lBody .opt')].map(o => o.getBoundingClientRect())
            .sort((a, b) => (b.bottom - a.bottom) || (b.right - a.right))[0];
            return [r.left, r.top, r.right, r.bottom]; }""")
        s.js("async () => { Lx.i = 0; showLessonTask(); await new Promise(r => setTimeout(r, 400)); }")
        w = s.js("() => { const r = document.querySelector('#lBody #xNext').getBoundingClientRect();"
                 " return [r.left, r.top, r.right, r.bottom]; }")
        # Wo Weiter und der kommende Knopf uebereinander liegen, dorthin tippt der Finger.
        links, oben = max(w[0], ecke[0]), max(w[1], ecke[1])
        rechts, unten = min(w[2], ecke[2]), min(w[3], ecke[3])
        assert rechts - links >= 6 and unten - oben >= 6, (
            "Weiter unter dem neuen Wort liegt nicht mehr ueber dem Knopf unten rechts der Frage danach"
            " - der Fall vom iPhone kommt hier nicht mehr vor, Test anpassen", w, ecke)
        x, y = (links + rechts) / 2, (oben + unten) / 2
        _tipp(s, x, y)
        s.page.wait_for_function("() => document.getElementById('lBody').dataset.i === '1'", timeout=8000)
        unter = s.js("([x, y]) => { const e = document.elementFromPoint(x, y); return !!e && !!e.closest('#lBody .opt'); }",
                     [x, y])
        assert unter, "der Finger liegt nicht auf einem neuen Antwortknopf"
        st = _alle_gleich(s, "#lBody .opt", "Frage nach dem neuen Wort")
        # Den Fokus hatte Weiter; er geht mit dem Knopf verloren, auf keinen neuen.
        assert not [k for k in st["knoepfe"] if k["fokus"]], st["knoepfe"]

        for wo in ("nach der Auswahl (Hoeren)", "nach dem Hoeren (Bedeutung)", "nach der Bedeutung (Auswahl)"):
            _antworten_und_weiter(s, "Lx", "lBody", wo)

        # Einmal falsch: der falsche Knopf unter dem Finger behaelt seinen eigenen Grund
        # (den unberuehrten), nur der Rand wird rot; der richtige wird gruen mit hellem Grund.
        soll = s.js(SOLL, "Lx")
        _tipp_auf(s, "#lBody .opt", soll, falsch=True)
        _bis_weiter(s, "lBody")
        st = s.js(STILE, "#lBody .opt")
        gut = s.js(FARBE, ["#lBody", "var(--good)"])
        schlecht = s.js(FARBE, ["#lBody", "var(--bad)"])
        hell = s.js(FARBE, ["#lBody", "var(--primary-soft)"])
        richtig = [k for k in st["knoepfe"] if k["t"] == soll][0]
        daneben = [k for k in st["knoepfe"] if k["t"] != soll and k["rand"] != st["frisch"]["rand"]]
        assert len(daneben) == 1, st
        assert daneben[0]["grund"] == st["frisch"]["grund"] != hell, (daneben, st["frisch"])
        assert daneben[0]["rand"] == " ".join([schlecht] * 4), daneben
        assert richtig["grund"] == hell and richtig["rand"] == " ".join([gut] * 4), richtig
        _weiter(s, "lBody")
        s.page.wait_for_function("() => !document.querySelector('#lBody .weiterbox')", timeout=8000)
        _alle_gleich(s, "#lBody .opt", "nach der falschen Antwort")
        _ohne_fehler(s)
    finally:
        ctx.close()


@pytest.mark.parametrize("schema", SCHEMATA)
def test_luecke_und_grammatik(motor, basis, heute_stand, schema):
    """Lueckensatz: Wort eintippen, Pruefen und Weiter antippen - die Auswahl danach.
    Dann eine Grammatikaufgabe (drei Formen) und noch einmal eine Auswahl."""
    ctx, s = _oeffnen(motor, basis, heute_stand, schema)
    try:
        antwort = s.js("""async () => { const warte = ms => new Promise(r => setTimeout(r, ms));
            openLevel(0); await warte(300); startLesson(); await warte(300); const k = window.__kurz;
            const satz = SENTENCES.find(x => x.text.indexOf('___') >= 0 && !x.zahl);
            const g = Object.values(GRAMMAR).flatMap(x => x.uebungen || [])
                .find(x => (x.optionen || []).length >= 3 && x.optionen.every(o => o.length <= 14));
            Lx.queue = [{typ:'gap', s:satz}, {typ:'mc', w:k[0], pool:k}, {typ:'gram', g}, {typ:'mc', w:k[1], pool:k}];
            Lx.i = 0; Lx.total = Lx.queue.length; showLessonTask(); await warte(500);
            return satz.answer; }""")
        s.page.fill("#lBody #xIn", antwort)
        _tipp_auf(s, "#lBody #xCheck")
        _bis_weiter(s, "lBody")
        assert s.js("() => document.querySelector('#lBody .feedback').classList.contains('ok')")
        _weiter(s, "lBody")
        s.page.wait_for_function("() => document.getElementById('lBody').dataset.i === '1'"
                                 " && !document.querySelector('#lBody .weiterbox')", timeout=8000)
        st = _alle_gleich(s, "#lBody .opt", "Auswahl nach dem Lueckensatz")
        assert not [k for k in st["knoepfe"] if k["fokus"]], st["knoepfe"]
        _antworten_und_weiter(s, "Lx", "lBody", "nach der Auswahl (Grammatik)")
        assert s.js("() => Lx.queue[Lx.i].typ") == "gram"
        _antworten_und_weiter(s, "Lx", "lBody", "nach der Grammatik (Auswahl)")
        _ohne_fehler(s)
    finally:
        ctx.close()


@pytest.mark.parametrize("schema", SCHEMATA)
def test_level_test_und_einstufung(motor, basis, heute_stand, schema):
    ctx, s = _oeffnen(motor, basis, heute_stand, schema)
    try:
        s.js("""async () => { const warte = ms => new Promise(r => setTimeout(r, ms));
            CATEGORIES[0].words.forEach(w => known.add(w.id)); openLevel(0); await warte(300); startTest();
            await warte(300); const k = window.__kurz;
            Tx.qs = [{typ:'mc', w:k[0], pool:k}, {typ:'listen', w:k[1], pool:k}, {typ:'mcrev', w:k[2], pool:k},
                     {typ:'mc', w:k[3], pool:k}];
            Tx.i = 0; Tx.results = []; Tx.right = 0; showTestQ(); await warte(400); }""")
        _alle_gleich(s, "#tBody .opt", "Test, erste Frage")
        for n in range(3):
            _antworten_und_weiter(s, "Tx", "tBody", "Test, Frage %d" % (n + 2))

        s.js("""async () => { const warte = ms => new Promise(r => setTimeout(r, ms));
            baueEinstufung('etwas'); const k = window.__kurz;
            Ex.qs = [{typ:'mc', w:k[1], pool:k}, {typ:'mcrev', w:k[0], pool:k}, {typ:'listen', w:k[3], pool:k},
                     {typ:'mc', w:k[2], pool:k}];
            Ex.qs.forEach(q => { q.stufe = 0; }); einstufungStarten(); await warte(400); }""")
        _alle_gleich(s, "#eBody .opt", "Einstufung, erste Frage")
        for n in range(3):
            _antworten_und_weiter(s, "Ex", "eBody", "Einstufung, Frage %d" % (n + 2))
        _ohne_fehler(s)
    finally:
        ctx.close()


@pytest.mark.parametrize("schema", SCHEMATA)
def test_fragen_zur_geschichte(motor, basis, heute_stand, schema):
    ctx, s = _oeffnen(motor, basis, heute_stand, schema)
    try:
        n = s.js("async () => { openStory(0); stilleBitte(); await new Promise(r => setTimeout(r, 600));"
                 " return STORIES[0].fragen.length; }")
        assert n >= 3, n
        soll = r"""() => { const f = document.querySelector('#rQ .ex-q').textContent;
            return STORIES[0].fragen.find(q => q.frage === f).richtig; }"""
        _alle_gleich(s, "#rQ .opt", "Geschichte, erste Frage")
        for i in range(n - 1):
            alt = s.js("() => document.querySelector('#rQ .ex-q').textContent")
            _tipp_auf(s, "#rQ .opt", s.js(soll))
            _bis_weiter(s, "rQ")
            _weiter(s, "rQ")
            s.page.wait_for_function("(alt) => { const q = document.querySelector('#rQ .ex-q');"
                                     " return !!q && q.textContent !== alt; }", arg=alt, timeout=8000)
            _alle_gleich(s, "#rQ .opt", "Geschichte, Frage %d" % (i + 2))
        _ohne_fehler(s)
    finally:
        ctx.close()


KACHEL_SOLL = r"""
() => {
  const q = Lx.queue[Lx.i];
  const s = q.s && typeof zahlFassung === 'function' ? zahlFassung(q.s, q.v) : q.s;
  const rand = /^[.,!?¿¡:;"„“”«»…()]+|[.,!?¿¡:;"„“”«»…()]+$/g;
  return s.bs.split(/\s+/).map(x => x.replace(rand, '').toLowerCase()).filter(Boolean);
}
"""


@pytest.mark.parametrize("schema", SCHEMATA)
def test_satzbau_kacheln(motor, basis, heute_stand, schema):
    """Eine gelegte Kachel zuruecklegen: die naechste rutscht unter den Finger.
    Danach Satz fertig legen, Pruefen, Weiter - und die Auswahl danach."""
    ctx, s = _oeffnen(motor, basis, heute_stand, schema)
    try:
        s.js("""async () => { const warte = ms => new Promise(r => setTimeout(r, ms));
            openLevel(0); await warte(300); startLesson(); await warte(300);
            const satz = SATZBAU.find(x => satzKacheln(x.bs).length >= 4 && !x.zahl);
            const k = window.__kurz;
            Lx.queue = [{typ:'kacheln', s:satz}, {typ:'mc', w:k[0], pool:k}];
            Lx.i = 0; Lx.total = 2; showLessonTask(); await warte(500); }""")
        kachel = "#lBody .kachel:not(.platz)"
        _alle_gleich(s, kachel, "Kacheln am Anfang")
        _tipp_auf(s, "#lBody #xBank .kachel:not(.platz)")
        s.page.wait_for_timeout(400)
        _tipp_auf(s, "#lBody #xBank .kachel:not(.platz)")
        s.page.wait_for_timeout(400)
        _tipp_auf(s, "#lBody #xZeile .kachel")             # die erste zurueck, die zweite rutscht nach
        s.page.wait_for_timeout(500)                       # Gleiten 200-260 ms
        _alle_gleich(s, kachel, "Kacheln nach dem Zuruecklegen")
        # Zurueck auf Anfang und richtig legen
        while s.js("() => document.querySelectorAll('#lBody #xZeile .kachel').length"):
            _tipp_auf(s, "#lBody #xZeile .kachel")
            s.page.wait_for_timeout(350)
        for wort in s.js(KACHEL_SOLL):
            lage = s.js("""(w) => { const b = [...document.querySelectorAll('#lBody #xBank .kachel:not(.platz)')]
                .find(o => o.textContent.toLowerCase() === w); return b ? b.textContent : null; }""", wort)
            assert lage, wort
            _tipp_auf(s, "#lBody #xBank .kachel:not(.platz)", lage)
            s.page.wait_for_timeout(350)
            _alle_gleich(s, kachel, "Kacheln beim Legen")
        _tipp_auf(s, "#lBody #xCheck")
        _bis_weiter(s, "lBody")
        assert s.js("() => document.querySelector('#lBody #xZeile').classList.contains('ok')")
        _weiter(s, "lBody")
        s.page.wait_for_function("() => document.getElementById('lBody').dataset.i === '1'"
                                 " && !document.querySelector('#lBody .weiterbox')", timeout=8000)
        _alle_gleich(s, "#lBody .opt", "Auswahl nach den Kacheln")
        _ohne_fehler(s)
    finally:
        ctx.close()


def test_maus_leuchtet_weiter_finger_nicht(motor, basis, heute_stand):
    """Mit Maus (hover:hover, pointer:fine) wird ein offener Knopf unter dem Zeiger
    hell wie bisher, ein beantworteter nicht mehr. Am Handy aendert ein Zeiger ueber
    dem Knopf nichts, obwohl :hover dort greift."""
    for touch in (False, True):
        ctx, s = _oeffnen(motor, basis, heute_stand, "light", touch=touch)
        try:
            assert s.js("() => matchMedia('(hover:hover) and (pointer:fine)').matches") is (not touch)
            s.js("""async () => { const warte = ms => new Promise(r => setTimeout(r, ms));
                openLevel(0); await warte(300); startLesson(); await warte(300); const k = window.__kurz;
                Lx.queue = [{typ:'mc', w:k[0], pool:k}, {typ:'mc', w:k[1], pool:k}]; Lx.i = 0; Lx.total = 2;
                showLessonTask(); await warte(400); }""")
            lage = s.js(LAGE, ["#lBody .opt", s.js(SOLL, "Lx"), True])
            s.page.mouse.move(lage["x"] + lage["w"] / 2, lage["y"] + lage["h"] / 2)
            s.page.wait_for_timeout(350)
            st = s.js(STILE, "#lBody .opt")
            ziel = [k for k in st["knoepfe"] if k["t"] == lage["t"]][0]
            assert ziel["unter"], ziel
            hell = s.js(FARBE, ["#lBody", "var(--primary-soft)"])
            blau = s.js(FARBE, ["#lBody", "var(--primary)"])
            if touch:
                assert (ziel["grund"], ziel["rand"]) == (st["frisch"]["grund"], st["frisch"]["rand"]), (ziel, st)
            else:
                assert ziel["grund"] == hell and ziel["rand"] == " ".join([blau] * 4), (ziel, hell, blau)
                # Mit der Maus falsch geantwortet, der Zeiger bleibt drauf: kein heller Grund
                s.page.mouse.down()
                s.page.mouse.up()
                _bis_weiter(s, "lBody")
                st = s.js(STILE, "#lBody .opt")
                ziel = [k for k in st["knoepfe"] if k["t"] == lage["t"]][0]
                assert ziel["aus"] and ziel["unter"] and ziel["grund"] == st["frisch"]["grund"] != hell, (ziel, st)
            _ohne_fehler(s)
        finally:
            ctx.close()


@pytest.mark.parametrize("schema", SCHEMATA)
def test_tastatur_zeigt_den_fokus(browser, basis, heute_stand, schema):
    """Mit Tastatur (Tab) bleibt der Fokusring der Antwortknoepfe sichtbar, und die
    Reiterwahl in den Einstellungen bekommt ihren blauen Rand - nach einem Fingertipp
    aber nicht."""
    ctx, s = _oeffnen(browser, basis, heute_stand, schema)
    try:
        s.js("""async () => { const warte = ms => new Promise(r => setTimeout(r, ms));
            openLevel(0); await warte(300); startLesson(); await warte(300); const k = window.__kurz;
            Lx.queue = [{typ:'mc', w:k[0], pool:k}]; Lx.i = 0; Lx.total = 1; showLessonTask(); await warte(400);
            document.activeElement && document.activeElement.blur(); }""")
        gesehen = []
        for _ in range(40):
            s.page.keyboard.press("Tab")
            f = s.js("""() => { const a = document.activeElement; if(!a || !a.matches('#lBody .opt')) return null;
                const c = getComputedStyle(a);
                return {t: a.textContent, sichtbar: a.matches(':focus-visible'), stil: c.outlineStyle,
                        breite: parseFloat(c.outlineWidth)}; }""")
            if f:
                gesehen.append(f)
                if len(gesehen) == 4:
                    break
        assert len(gesehen) == 4, gesehen
        for f in gesehen:
            assert f["sichtbar"] and f["stil"] != "none" and f["breite"] > 0, f

        s.js("async () => { Lx = null; showSettings(); await new Promise(r => setTimeout(r, 600)); }")
        blau = s.js(FARBE, ["#langKopf", "var(--primary)"])
        rand = "() => getComputedStyle(document.getElementById('langKopf')).borderTopColor"
        _tipp_auf(s, "#langKopf")
        s.page.wait_for_timeout(300)
        assert s.js(rand) != blau, "Reiterwahl nach dem Tipp blau umrandet"
        _tipp_auf(s, "#langKopf")                  # wieder zu
        s.page.wait_for_timeout(300)
        s.js("() => { document.activeElement && document.activeElement.blur(); }")
        for _ in range(80):
            s.page.keyboard.press("Tab")
            if s.js("() => document.activeElement && document.activeElement.id === 'langKopf'"):
                break
        assert s.js("() => document.activeElement.id") == "langKopf"
        assert s.js("() => document.activeElement.matches(':focus-visible')")
        assert s.js(rand) == blau
        _ohne_fehler(s)
    finally:
        ctx.close()


@pytest.mark.parametrize("schema", SCHEMATA)
def test_axe_nach_den_tipps(browser, basis, heute_stand, schema):
    """axe in der Lektion nach echten Tipps: kein ernster oder kritischer Verstoss."""
    ctx, s = _oeffnen(browser, basis, heute_stand, schema)
    try:
        s.js("""async () => { const warte = ms => new Promise(r => setTimeout(r, ms));
            openLevel(0); await warte(300); startLesson(); await warte(300); const k = window.__kurz;
            Lx.queue = [{typ:'intro', w:k[0], pool:k}, {typ:'mc', w:k[0], pool:k}, {typ:'mc', w:k[1], pool:k}];
            Lx.i = 0; Lx.total = 3; showLessonTask(); await warte(400); }""")
        _tipp_auf(s, "#lBody #xNext", fx=0.8, fy=0.2)
        s.page.wait_for_function("() => document.getElementById('lBody').dataset.i === '1'", timeout=8000)
        _antworten_und_weiter(s, "Lx", "lBody", "axe")
        s.page.add_script_tag(path=AXE)
        funde = s.page.evaluate("""async () => (await axe.run(document, {resultTypes:['violations']}))
            .violations.filter(v => v.impact === 'serious' || v.impact === 'critical')
            .map(v => v.id + ' (' + v.impact + '): ' + v.nodes.map(n => n.target.join(' ')).join(', '))""")
        assert funde == [], funde
        _ohne_fehler(s)
    finally:
        ctx.close()
