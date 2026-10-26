# -*- coding: utf-8 -*-
"""Stern: Aufgaben selbst markieren und in einer eigenen Runde ueben
(19.10.2026, Ajdins Entscheidungen; Knopf und Kasten aus dem gewaehlten
Entwurf, Variante 1 "Ring").

Was hier im echten Browser nachgeprueft wird:
  - der Knopf oben rechts in der Kopfzeile der Lernkarte, rechts neben den
    Punkten (seit dem 26.10.2026 spaet, Ajdin: "nimm A"; davor am selben
    Tag neben dem Drachen - "im moment steht es so mitten im nirgendwo" -,
    bis dahin unten rechts in der Leiste): setzen und wegnehmen (aria-pressed,
    Ansage, Goldstern), Pop nur mit Bewegung, er bleibt nach dem
    Neuladen, ein Stern je Wort ueber alle Aufgabenarten, Saetze und
    Grammatik lassen sich markieren;
  - die Lage: in .kastenkopf direkt hinter .tbar, senkrecht auf der Mitte
    der Herz-Pille, rechte Kante am Innenrand der Karte, die Zeile so hoch
    wie die Herz-Pille, Trefferflaeche 48 x 48 - und dass er nichts
    ueberdeckt (Herz, Punkte, Drache, Aufgabe), bei allen Aufgabenarten (auch Sprechen und die
    groesste Kachelbank), vor und nach der Antwort, bei 100, 130 und
    200 % Schrift, in Lektion, Markiert-Runde und Level-Test;
  - gut sichtbar in allen neun Sektionsfarben, hell und dunkel;
  - die Leiste unter der Karte hat nur noch "abbrechen", 39 px hoch;
  - versteckt haelt er seinen Platz: der Balken bleibt gleich breit, und
    der versteckte Knopf ist weder fokussierbar noch im Vorlesebaum;
  - Masse: 40 x 40 (im Entwurf 44 x 44), und der Stern sitzt per Pixelmessung
    auf weniger als 0,5 Geraetepixel in der Mitte (hell und dunkel, leer
    und markiert, 412 x 915 und 360 x 726);
  - wo er steht und wo nicht: Level-Test ja; Einstufung, Ergebnis und
    Schirm ohne Leben (Lektion und Test) nein;
  - die Obergrenze von 300 - voll heisst: nichts wird still geloescht;
  - der Reiter Wiederholen: der alte Kasten genau wie vorher, darunter
    "Markiert" im selben Aufbau und gleich hoch, leer, ohne Leben;
  - die Markiert-Runde: bis zu zehn, die am laengsten nicht geuebten
    zuerst, der Stern bleibt nach einer richtigen Antwort, r wird gesetzt,
    eine falsche Antwort kostet ein Leben und landet im Fehler-Topf;
  - der grosse Weitermachen-Knopf bleibt, wie er war;
  - Sicherungsdatei: Sterne kommen mit, kaputte werden verworfen,
    umbenannte Woerter umgeschrieben;
  - axe auf dem Reiter, auf einer Aufgabe mit Stern und im Test.

Aufbau wie test_v106.py: jeder Test mit eigenem, leerem Browserkontext im
Geraetemodus; die Aufgaben werden gezielt in die Lektion gelegt und dann
mit echten Klicks beantwortet.
"""
import base64
import json
import os

import pytest
from conftest import Seite

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AXE = os.path.join(WURZEL, "tests_e2e", "vendor", "axe.min.js")

# Aufgaben in die Lektion von Level 1 legen. Beschreibung je Aufgabe:
# {typ, wort} fuer Woerter (wort = Nummer unter den tippbaren Woertern von
# Level 1), {typ: 'gap' | 'kacheln' | 'gram'} fuer Saetze und Grammatik.
# Gibt die Kennungen zurueck (topfSchluessel).
LEGEN = """(liste) => {
  openLevel(0); startLesson();
  const c = CATEGORIES[0], ws = c.words.filter(x => typable(x));
  const s = SENTENCES.find(x => x.text.indexOf('___') >= 0);
  const fertig = new Set(lueckeFertig(s));
  const k = SATZBAU.find(x => satzKacheln(x.bs).length >= 2 && !fertig.has(kachelNorm(x.bs)));
  const lv = Object.keys(GRAMMAR).find(id => (GRAMMAR[id].uebungen || []).length);
  const bau = d => d.typ === 'gap' ? {typ: 'gap', s}
                 : d.typ === 'kacheln' ? {typ: 'kacheln', s: k}
                 : d.typ === 'gram' ? {typ: 'gram', g: GRAMMAR[lv].uebungen[0]}
                 : {typ: d.typ, w: ws[d.wort || 0], pool: c.words};
  Lx.queue = liste.map(bau); Lx.i = 0; Lx.total = Lx.queue.length; Lx.results = []; Lx.right = 0;
  showLessonTask();
  return Lx.queue.map(a => topfSchluessel(a));
}"""

# Die laufende Aufgabe (Lektion/Runde: art 'Lx', Test: 'Tx') beantworten,
# richtig oder falsch.
ANTWORTEN = r"""async ([richtig, art]) => {
  const X = art === 'Tx' ? Tx : Lx, liste = art === 'Tx' ? Tx.qs : Lx.queue;
  const q = liste[X.i], body = document.getElementById(art === 'Tx' ? 'tBody' : 'lBody'), i = X.i;
  if(q.typ === 'kacheln'){
    const rand = /^[.,!?¿¡:;"„“”«»…()]+|[.,!?¿¡:;"„“”«»…()]+$/g;
    const teile = q.s.bs.split(/\s+/).map(x => x.replace(rand, '').toLowerCase()).filter(Boolean);
    for(const soll of (richtig ? teile : teile.slice().reverse())){
      const b = [...body.querySelectorAll('#xBank .kachel:not(.platz)')].find(o => o.textContent.toLowerCase() === soll);
      b.click();
    }
    body.querySelector('#xCheck').click();
  } else if(q.typ === 'gap' || q.typ === 'type'){
    body.querySelector('#xIn').value = richtig ? (q.typ === 'gap' ? q.s.answer : q.w.bs).split(' / ')[0] : 'qqqq';
    body.querySelector('#xCheck').click();
  } else if(q.typ === 'intro'){
    body.querySelector('#xNext').click();
  } else {
    const soll = q.typ === 'gram' ? q.g.richtig : (q.typ === 'mcrev' ? q.w.de : q.w.bs);
    const opts = [...body.querySelectorAll('.opt')];
    (richtig ? opts.find(o => o.textContent === soll) : opts.find(o => o.textContent !== soll)).click();
  }
  const ende = Date.now() + 5000;
  while(X.i === i && Date.now() < ende) await new Promise(r => setTimeout(r, 15));
  return {typ: q.typ, schluessel: topfSchluessel(q)};
}"""

# Weiter antippen, sobald er da ist
WEITER = """async (feld) => {
  const ende = Date.now() + 5000;
  let k = null;
  while(!(k = document.querySelector('#' + (feld || 'lBody') + ' .weiterbox .btn')) && Date.now() < ende)
    await new Promise(r => setTimeout(r, 15));
  k.click();
  await new Promise(r => setTimeout(r, 50));
}"""

# Echte, verschiedene Wort-Kennungen in Lernpfad-Reihenfolge
WOERTER = """(n) => [...new Map(CATEGORIES.flatMap(c => c.words).map(w => [w.id, w])).keys()].slice(0, n)"""

KNOPF = """(id) => { const b = document.getElementById(id), r = b.getBoundingClientRect(), s = b.querySelector('svg');
  return {sichtbar: !b.hidden && !!b.offsetParent, gedrueckt: b.getAttribute('aria-pressed'),
          name: b.getAttribute('aria-label'), typ: b.getAttribute('type'), w: r.width, h: r.height,
          gold: !!s && s.classList.contains('an'), svg: s ? [s.getAttribute('width'), s.getAttribute('height')] : null,
          imKoerper: !!b.closest('#lBody, #tBody, #eBody')}; }"""


def _ansage(seite, text):
    seite.page.wait_for_function("(t) => document.getElementById('ansage').textContent === t", arg=text,
                                 timeout=3000)


def _stand(seite):
    return seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand')).stern")


def _vorspann_weg(seite):
    """Fuer Messungen am Bildschirm: der Vorspann liegt nach dem Start noch
    gut zwei Sekunden ueber allem (z-index 900)."""
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)


def _test_starten(seite):
    seite.js("() => { passed.add(CATEGORIES[0].id); openLevel(0); startTest(); }")
    seite.page.locator("#tBody .opt, #tBody #xIn").first.wait_for()


# ---------------------------------------------------------------------------
# Der Knopf
# ---------------------------------------------------------------------------

def test_stern_setzen_und_entfernen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    k = seite.js(LEGEN, [{"typ": "mc"}])[0]
    assert k.startswith("w:")
    knopf = seite.js(KNOPF, "lStern")
    assert knopf["sichtbar"] and knopf["gedrueckt"] == "false" and not knopf["gold"]
    assert knopf["name"] == "Markieren" and knopf["typ"] == "button"
    assert (knopf["w"], knopf["h"]) == (40, 40), knopf
    assert knopf["svg"] == ["24", "24"]
    assert not knopf["imKoerper"], "der Stern gehoert nicht ins Aufgabenfeld (weiterBeiTipp)"

    seite.page.click("#lStern")
    knopf = seite.js(KNOPF, "lStern")
    assert knopf["gedrueckt"] == "true" and knopf["gold"]
    _ansage(seite, "Markiert")
    e = seite.js("(k) => stern[k]", k)
    assert e["r"] == 0 and e["z"] > 0
    assert k in _stand(seite), "sofort gespeichert"
    # Markieren beantwortet nichts
    assert seite.js("() => ({i: Lx.i, erg: Lx.results.length})") == {"i": 0, "erg": 0}

    seite.page.click("#lStern")
    knopf = seite.js(KNOPF, "lStern")
    assert knopf["gedrueckt"] == "false" and not knopf["gold"]
    _ansage(seite, "Nicht mehr markiert")
    assert seite.js("(k) => k in stern", k) is False
    assert k not in _stand(seite)
    assert seite.fehler == []


def test_farben_wie_im_entwurf(seite, heute_stand):
    """Leer: Rand --line, Stern-Umriss --muted, Flaeche seit dem 26.10.2026
    --bg wie die Herz-Pille (vorher --surface wie "Lektion abbrechen" - auf
    der Karte waere das nur ein duenner Ring). Markiert: Goldring --accent,
    hell auf --accent-soft, Goldstern mit Rand #B07D00."""
    seite.starten(stand=heute_stand())
    seite.js(LEGEN, [{"typ": "mc"}])
    # Die Werte der Variablen genau dort, wo der Knopf steht (die Sektion
    # kann --surface, --line und --muted umfaerben)
    farben = """() => { const b = document.getElementById('lStern'), s = getComputedStyle(b),
        p = getComputedStyle(b.querySelector('path'));
      const v = name => { const i = document.createElement('i'); i.style.color = 'var(' + name + ')';
        b.parentElement.appendChild(i); const c = getComputedStyle(i).color; i.remove(); return c; };
      return {rand: s.borderTopColor, grund: s.backgroundColor, strich: p.stroke, fuell: p.fill,
              randBreite: s.borderTopWidth, rund: s.borderRadius,
              line: v('--line'), surface: v('--surface'), muted: v('--muted'), accent: v('--accent'),
              accentSoft: v('--accent-soft'), bg: v('--bg')}; }"""
    leer = seite.js(farben)
    assert leer["rand"] == leer["line"] and leer["randBreite"] == "2px" and leer["rund"] == "50%"
    assert leer["grund"] == leer["bg"] != leer["surface"]
    assert leer["strich"] == leer["muted"] and leer["fuell"] == "none"
    seite.page.click("#lStern")
    seite.page.wait_for_timeout(400)            # Farbwechsel laeuft 0,15 s
    an = seite.js(farben)
    assert an["rand"] == an["accent"] == "rgb(245, 196, 0)"
    assert an["grund"] == an["accentSoft"] == "rgb(255, 244, 194)"
    assert an["strich"] == "rgb(176, 125, 0)" and "sternGold" in an["fuell"]
    assert seite.fehler == []


def test_pop_nur_mit_bewegung(browser, basis, heute_stand):
    for bewegung, erwartet in (("no-preference", True), ("reduce", False)):
        ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                                  service_workers="block", reduced_motion=bewegung)
        seite = Seite(ctx.new_page(), basis)
        try:
            seite.starten(stand=heute_stand())
            seite.js(LEGEN, [{"typ": "mc"}])
            pop = seite.js("() => { const b = document.getElementById('lStern'); b.click(); return b.classList.contains('pop'); }")
            assert pop is erwartet, bewegung
            if erwartet:
                seite.page.wait_for_function("() => !document.getElementById('lStern').classList.contains('pop')",
                                             timeout=2000)
            assert seite.fehler == []
        finally:
            ctx.close()


def test_stern_vor_und_nach_der_antwort_und_weiter_unberuehrt(seite, heute_stand):
    """Nach der Antwort laesst sich der Stern antippen, ohne dass der Tipp
    die naechste Aufgabe holt - er liegt ausserhalb von #lBody."""
    seite.starten(stand=heute_stand())
    seite.js(LEGEN, [{"typ": "mc", "wort": 0}, {"typ": "mcrev", "wort": 1}])
    seite.js(ANTWORTEN, [True, "Lx"])
    seite.page.locator("#lBody .weiterbox .btn").wait_for()
    seite.page.wait_for_timeout(1000)          # Horcher von weiterBeiTipp haengt jetzt
    assert seite.js(KNOPF, "lStern")["sichtbar"]
    seite.page.click("#lStern")
    seite.page.wait_for_timeout(200)
    assert seite.js(KNOPF, "lStern")["gedrueckt"] == "true"
    assert seite.js("() => document.getElementById('lBody').dataset.i") == "0", "Stern hat weitergeblaettert"
    assert seite.page.locator("#lBody .weiterbox .btn").is_visible()
    assert seite.fehler == []


def test_stern_bleibt_nach_neuladen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    k = seite.js(LEGEN, [{"typ": "mc", "wort": 2}])[0]
    seite.page.click("#lStern")
    seite.neu_laden()
    assert seite.js("(k) => k in stern", k)
    assert seite.js(LEGEN, [{"typ": "mcrev", "wort": 2}])[0] == k
    knopf = seite.js(KNOPF, "lStern")
    assert knopf["gedrueckt"] == "true" and knopf["gold"]
    assert seite.fehler == []


def test_ein_stern_pro_wort_ueber_aufgabenarten(seite, heute_stand):
    seite.starten(stand=heute_stand())
    keys = seite.js(LEGEN, [{"typ": "mc", "wort": 3}, {"typ": "mcrev", "wort": 3}, {"typ": "type", "wort": 3}])
    assert len(set(keys)) == 1
    seite.page.click("#lStern")                      # in der Auswahl markiert
    seite.js(ANTWORTEN, [True, "Lx"])
    seite.js(WEITER)
    assert seite.js("() => Lx.queue[Lx.i].typ") == "mcrev"
    assert seite.js(KNOPF, "lStern")["gedrueckt"] == "true", "dasselbe Wort, andere Art: schon markiert"
    assert seite.js("() => Object.keys(stern).length") == 1
    seite.page.click("#lStern")                      # hier wieder weggenommen
    seite.js(ANTWORTEN, [True, "Lx"])
    seite.js(WEITER)
    assert seite.js("() => Lx.queue[Lx.i].typ") == "type"
    assert seite.js(KNOPF, "lStern")["gedrueckt"] == "false"
    assert seite.js("() => Object.keys(stern).length") == 0
    assert seite.fehler == []


@pytest.mark.parametrize("typ,anfang", [("gap", "s:"), ("kacheln", "k:"), ("gram", "g:"), ("intro", "w:"),
                                        ("listen", "w:")])
def test_satz_grammatik_und_andere_arten_markierbar(seite, heute_stand, typ, anfang):
    seite.starten(stand=heute_stand())
    k = seite.js(LEGEN, [{"typ": typ}])[0]
    assert k.startswith(anfang)
    assert seite.js(KNOPF, "lStern")["sichtbar"]
    seite.page.click("#lStern")
    assert seite.js("(k) => !!stern[k]", k)
    assert seite.js(KNOPF, "lStern")["gedrueckt"] == "true"
    assert seite.fehler == []


def test_fokus_sichtbar_mit_tastatur(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(LEGEN, [{"typ": "mc"}])
    for _ in range(40):
        seite.page.keyboard.press("Tab")
        if seite.js("() => document.activeElement && document.activeElement.id") == "lStern":
            break
    assert seite.js("() => document.activeElement.id") == "lStern", "Stern mit Tab nicht erreichbar"
    stil = seite.js("() => { const s = getComputedStyle(document.getElementById('lStern'));"
                    " return [s.outlineStyle, s.outlineWidth, s.outlineOffset]; }")
    assert stil == ["solid", "3px", "3px"], stil
    seite.page.keyboard.press("Enter")
    assert seite.js(KNOPF, "lStern")["gedrueckt"] == "true"


# ---------------------------------------------------------------------------
# Lage: in der Kopfzeile, rechts neben den Punkten (26.10.2026 spaet)
# ---------------------------------------------------------------------------

# Wo der Stern steht und was um ihn herum ist. Trefferflaeche: der Knopf
# plus 4 px (::before). Geschnitten wird mit der Herz-Pille, dem Balken, dem
# Kasten des Drachen und jedem sichtbaren Teil der Aufgabe.
LAGE = """(id) => { const b = document.getElementById(id), sec = b.closest('section'), card = sec.querySelector('.card');
  const R = e => e.getBoundingClientRect();
  if(!b.hidden){ const v = R(b); if(v.top < 0 || v.bottom > innerHeight) b.scrollIntoView({block: 'center'}); }
  const kopf = sec.querySelector('.kastenkopf'), herzEl = kopf.querySelector('.kastenherz'), barEl = kopf.querySelector('.tbar');
  const s = R(b), d = R(sec.querySelector('.zmaj.mini')), k = R(kopf), herz = R(herzEl), bar = R(barEl),
        c = R(card), cs = getComputedStyle(card);
  const innen = c.right - parseFloat(cs.borderRightWidth) - parseFloat(cs.paddingRight);
  const body = sec.querySelector('#lBody, #tBody');
  const teile = [...body.querySelectorAll('*')].filter(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')
    .map(e => [e, R(e)]).filter(([e, r]) => r.width > 0 && r.height > 0);
  const t = {left: s.left - 4, top: s.top - 4, right: s.right + 4, bottom: s.bottom + 4};
  const schneidet = r => !(t.right <= r.left || t.left >= r.right || t.bottom <= r.top || t.top >= r.bottom);
  const mitte = document.elementFromPoint(s.left + s.width / 2, s.top + s.height / 2);
  return {imKopf: b.parentElement === kopf, hinterBar: b.previousElementSibling === barEl, letzter: kopf.lastElementChild === b,
          inKarte: card.contains(b), sichtbar: !b.hidden && !!b.offsetParent,
          w: s.width, h: s.height, rechtsInnen: innen - s.right, abstandBar: s.left - bar.right,
          hoehe: (s.top + s.height / 2) - (herz.top + herz.height / 2), kopfH: k.height - herz.height,
          inKarteOben: t.top - (c.top + parseFloat(cs.borderTopWidth)), drache: d.height,
          ueberDrache: d.top - t.bottom, ueberAufgabe: Math.min(...teile.map(([e, r]) => r.top)) - t.bottom,
          schneidet: {herz: schneidet(herz), bar: schneidet(bar), drache: schneidet(d),
                      aufgabe: teile.filter(([e, r]) => schneidet(r)).map(([e]) => e.tagName + '.' + e.className)},
          oben: mitte === b || b.contains(mitte)}; }"""


def _lage_ok(m, wo):
    # in der Kopfzeile, direkt hinter dem Balken und als letztes darin
    # (26.10.2026: "nimm A")
    assert m["imKopf"] and m["hinterBar"] and m["letzter"] and m["inKarte"] and m["sichtbar"], (wo, m)
    assert (m["w"], m["h"]) == (40, 40), (wo, m)
    # auf einer Linie mit der Herz-Pille, rechte Kante am Innenrand der
    # Karte, je +-2 px; zwischen Balken und Knopf der Abstand der Zeile
    assert abs(m["hoehe"]) <= 2 and abs(m["rechtsInnen"]) <= 2, (wo, m)
    assert 8 <= m["abstandBar"] <= 12, (wo, m)
    # die Zeile bleibt so hoch wie die Herz-Pille - nichts darunter rutscht
    assert abs(m["kopfH"]) <= 0.5, (wo, m)
    # ueberdeckt nichts, auch nicht mit der Trefferflaeche, und bleibt in der Karte
    assert m["schneidet"] == {"herz": False, "bar": False, "drache": False, "aufgabe": []}, (wo, m)
    assert m["inKarteOben"] >= 0 and m["ueberDrache"] >= 0 and m["ueberAufgabe"] >= 0, (wo, m)
    assert m["oben"], (wo, "etwas liegt ueber dem Stern", m)


# Breite x Hoehe: 320 ist die engste Breite (der Balken am kuerzesten),
# 320 x 900 hat dabei den grossen Drachen (120 px, erst unter 821 px Hoehe
# 100 px).
FORMATE = [(320, 640), (320, 900), (360, 726), (390, 844), (412, 915)]


@pytest.mark.parametrize("breite,hoehe", FORMATE)
@pytest.mark.parametrize("knopf", ["lStern", "tStern"])
def test_stern_in_der_kopfzeile_rechts_neben_den_punkten(browser, basis, heute_stand, knopf, breite, hoehe):
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, locale="de-DE", service_workers="block")
    seite = Seite(ctx.new_page(), basis)
    try:
        seite.starten(stand=heute_stand())
        if knopf == "lStern":
            seite.js(LEGEN, [{"typ": "mc"}])
        else:
            _test_starten(seite)
        _vorspann_weg(seite)
        m = seite.js(LAGE, knopf)
        _lage_ok(m, (knopf, breite, hoehe))
        assert m["drache"] == (100 if hoehe <= 820 else 120), m
        # Vor der Antwort ganz im Bild, ohne zu scrollen
        assert seite.js("""(id) => { const r = document.getElementById(id).getBoundingClientRect();
                           return scrollY === 0 && r.top >= 0 && r.bottom <= innerHeight; }""", knopf)
        t = seite.js(TREFFER, knopf)
        # Das Raster zaehlt beide Randpunkte mit: 48 px Flaeche ergeben 48,75
        # (so auch im Entwurf gemessen); 40 px ohne ::before ergaeben 40,75.
        assert t["vor"] == ["48px", "48px"] and 48 <= t["w"] <= 48.75 and 48 <= t["h"] <= 48.75 and t["ecken"], t
        assert seite.fehler == []
    finally:
        ctx.close()


# Balken, Kopfzeile und Drache messen; den Knopf verstecken (wie die App
# es bei einer Aufgabe ohne Kennung tut) und wieder auf die Aufgabe stellen.
VERSTECKT = """(id) => { const b = document.getElementById(id), sec = b.closest('section');
  const R = s => sec.querySelector(s).getBoundingClientRect();
  const mass = () => ({bar: R('.kastenkopf .tbar').width, kopf: R('.kastenkopf').height, drache: R('.zmaj.mini').top,
                       platz: b.getBoundingClientRect().width});
  const aufgabe = id === 'tStern' ? Tx.qs[Tx.i] : Lx.queue[Lx.i];
  const sichtbar = mass();
  sternKnopf(id, null);
  const weg = mass();
  b.focus();
  const fokus = document.activeElement === b;
  const stil = getComputedStyle(b);
  const r = b.getBoundingClientRect(), e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  const zustand = {hidden: b.hidden, sichtbarkeit: stil.visibility, display: stil.display, fokus,
                   trifft: !!e && (e === b || b.contains(e))};
  sternKnopf(id, aufgabe);
  return {sichtbar, weg, wieder: mass(), zustand, wiederHidden: b.hidden}; }"""


@pytest.mark.parametrize("breite", [320, 360, 412])
@pytest.mark.parametrize("knopf", ["lStern", "tStern"])
def test_balken_springt_nicht_wenn_der_stern_versteckt_ist(browser, basis, heute_stand, knopf, breite):
    """Versteckt (hidden) haelt der Stern seinen Platz (visibility:hidden):
    der Balken bleibt gleich breit, die Kopfzeile gleich hoch, der Drache
    an seiner Stelle. Und er ist dann wirklich weg: nicht fokussierbar,
    nicht im Vorlesebaum, faengt keinen Tipp ab."""
    ctx = browser.new_context(viewport={"width": breite, "height": 726}, locale="de-DE", service_workers="block")
    seite = Seite(ctx.new_page(), basis)
    try:
        seite.starten(stand=heute_stand())
        if knopf == "lStern":
            seite.js(LEGEN, [{"typ": "mc"}])
        else:
            _test_starten(seite)
        _vorspann_weg(seite)
        rolle = seite.page.get_by_role("button", name="Markieren")
        assert rolle.count() == 1
        m = seite.js(VERSTECKT, knopf)
        assert m["sichtbar"] == m["weg"] == m["wieder"], m
        assert m["sichtbar"]["platz"] == 40 and m["sichtbar"]["bar"] > 0, m
        assert m["zustand"] == {"hidden": True, "sichtbarkeit": "hidden", "display": "flex", "fokus": False,
                                "trifft": False}, m
        assert m["wiederHidden"] is False
        # im Vorlesebaum: versteckt keiner, danach wieder genau einer
        seite.js("(id) => sternKnopf(id, null)", knopf)
        assert rolle.count() == 0
        assert seite.page.locator("#" + knopf).is_hidden()
        seite.js("(id) => sternKnopf(id, id === 'tStern' ? Tx.qs[Tx.i] : Lx.queue[Lx.i])", knopf)
        assert rolle.count() == 1
        assert seite.fehler == []
    finally:
        ctx.close()


# Eine Aufgabe jeder Art bauen und an die erste Stelle legen - Lektion,
# Markiert-Runde oder Level-Test. kachelnGross: die Kachelbank mit den
# meisten Kacheln, speak: das laengste Wort.
LEGEN_ART = """async ([ort, typ]) => {
  lives = {anzahl: LEBEN_MAX, zeit: Date.now()};
  const c = CATEGORIES[0], ws = c.words.filter(x => typable(x));
  const bau = typ => {
    if(typ === 'gap') return {typ, s: SENTENCES.find(x => x.text.indexOf('___') >= 0)};
    if(typ === 'kacheln' || typ === 'kachelnGross'){
      const alle = SATZBAU.filter(x => satzKacheln(x.bs).length >= 2);
      return {typ: 'kacheln', s: typ === 'kacheln' ? alle[0]
        : alle.slice().sort((a, b) => satzKacheln(b.bs).length - satzKacheln(a.bs).length || b.bs.length - a.bs.length)[0]};
    }
    if(typ === 'gram'){ const lv = Object.keys(GRAMMAR).find(id => (GRAMMAR[id].uebungen || []).length);
      return {typ, g: GRAMMAR[lv].uebungen[0]}; }
    return {typ, w: typ === 'speak' ? c.words.slice().sort((a, b) => b.bs.length - a.bs.length)[0] : ws[0], pool: c.words};
  };
  const a = bau(typ);
  if(ort === 'lektion'){ openLevel(0); startLesson(); Lx.queue = [a, bau('mc')]; Lx.i = 0; Lx.total = 2; Lx.results = []; Lx.right = 0; showLessonTask(); }
  else if(ort === 'runde'){
    stern = {}; CATEGORIES.flatMap(c => c.words).slice(0, 3).forEach((w, i) => { stern['w:' + w.id] = {z: i + 1, r: 0}; });
    homeMode = 'topf'; showHome(); startStern(); Lx.queue[0] = a; Lx.i = 0; showLessonTask();
  } else { passed.add(c.id); openLevel(0); startTest(); Tx.qs[0] = a; Tx.i = 0; Tx.results = []; Tx.right = 0; showTestQ(); }
  await document.fonts.ready; await new Promise(r => setTimeout(r, 200));
  return ort === 'runde' ? Lx.quelle : ort;
}"""

# Irgendwie antworten (falsch: dann steht auch die Loesung da, das Feld ist
# am groessten); Sprechen wird uebersprungen.
ANTWORT_ART = """async (ort) => {
  const X = ort === 'test' ? Tx : Lx, liste = ort === 'test' ? Tx.qs : Lx.queue;
  const body = document.getElementById(ort === 'test' ? 'tBody' : 'lBody'), q = liste[X.i], i = X.i;
  if(q.typ === 'speak') body.querySelector('#xSkip').click();
  else if(q.typ === 'intro') body.querySelector('#xNext').click();
  else if(q.typ === 'kacheln'){ [...body.querySelectorAll('#xBank .kachel:not(.platz)')].forEach(b => b.click()); body.querySelector('#xCheck').click(); }
  else if(q.typ === 'gap' || q.typ === 'type'){ body.querySelector('#xIn').value = 'qqqq'; body.querySelector('#xCheck').click(); }
  else body.querySelector('.opt').click();
  const ende = Date.now() + 5000;
  while(X.i === i && Date.now() < ende) await new Promise(r => setTimeout(r, 15));
  await new Promise(r => setTimeout(r, 250));
}"""

# Wie die Schrift des Handys (test_symbole.py): jede Groesse mal f. Vorher
# zuruecksetzen, damit nichts doppelt waechst.
SCHRIFT = """(f) => { document.querySelectorAll('[data-schrift]').forEach(e => { e.style.fontSize = ''; delete e.dataset.schrift; });
  if(f === 1) return;
  const els = [...document.querySelectorAll('body *')], g = els.map(e => parseFloat(getComputedStyle(e).fontSize));
  els.forEach((e, i) => { e.style.fontSize = (g[i] * f) + 'px'; e.dataset.schrift = '1'; }); }"""

ARTEN = {"lektion": ["mc", "mcrev", "type", "listen", "gap", "kacheln", "kachelnGross", "speak", "gram", "intro"],
         "runde": ["mc", "type", "gap", "kachelnGross", "gram"],
         "test": ["mc", "listen", "gap", "kachelnGross", "gram"]}


@pytest.mark.parametrize("faktor", [1, 1.3, 2])
def test_stern_ueberdeckt_nichts(browser, basis, heute_stand, faktor):
    """Bei 320 px, der engsten Breite: jede Aufgabenart in Lektion,
    Markiert-Runde und Level-Test, vor und nach der Antwort - der Stern
    bleibt an seiner Stelle in der Kopfzeile und ueberdeckt weder Herz,
    Punkte und Drache noch irgendeinen Teil der Aufgabe. Bei 130 und 200 %
    Schrift waechst die Herz-Pille und mit ihr die Zeile, der Knopf bleibt
    auf ihrer Mitte. Nach einer langen Aufgabe scrollt die App zu "Weiter";
    dann wird erst zum Stern zurueckgescrollt."""
    ctx = browser.new_context(viewport={"width": 320, "height": 640}, locale="de-DE", service_workers="block",
                              reduced_motion="reduce")
    seite = Seite(ctx.new_page(), basis)
    try:
        seite.starten(stand=heute_stand())
        _vorspann_weg(seite)
        gemessen = 0
        for ort, arten in ARTEN.items():
            knopf = "tStern" if ort == "test" else "lStern"
            for typ in arten:
                assert seite.js(LEGEN_ART, [ort, typ]) == ("stern" if ort == "runde" else ort)
                seite.js(SCHRIFT, faktor)
                _lage_ok(seite.js(LAGE, knopf), (ort, typ, faktor, "vor"))
                seite.js(ANTWORT_ART, ort)
                seite.js(SCHRIFT, faktor)
                _lage_ok(seite.js(LAGE, knopf), (ort, typ, faktor, "nach"))
                gemessen += 2
        assert gemessen == 40
        assert seite.fehler == []
    finally:
        ctx.close()


# Farben genau dort, wo der Knopf steht, ohne Uebergang (der Knopf blendet
# Farben in 0,15 s um).
KNOPF_FARBEN = """([nr, an]) => {
  let st = document.getElementById('ohneUebergang');
  if(!st){ st = document.createElement('style'); st.id = 'ohneUebergang'; st.textContent = '*{transition:none!important}'; document.head.appendChild(st); }
  document.documentElement.dataset.sek = String(nr);
  const b = document.getElementById('lStern');
  sternZeigen(b, an);
  const z = c => c.match(/[\\d.]+/g).slice(0, 3).map(Number);
  const s = getComputedStyle(b), p = getComputedStyle(b.querySelector('path'));
  return {grund: z(s.backgroundColor), strich: z(p.stroke), karte: z(getComputedStyle(document.querySelector('#lesson .card')).backgroundColor)}; }"""


def _kontrast(a, b):
    def hell(c):
        k = [x / 255.0 for x in c]
        k = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in k]
        return 0.2126 * k[0] + 0.7152 * k[1] + 0.0722 * k[2]
    h = sorted((hell(a), hell(b)), reverse=True)
    return (h[0] + 0.05) / (h[1] + 0.05)


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_stern_gut_sichtbar_in_allen_sektionen(browser, basis, heute_stand, schema):
    """Ajdin am 26.10.2026: "weil er zu schlecht sichtbar war". In allen neun
    Sektionsfarben: der leere Stern hebt sich mit mindestens 4,5:1 von
    seinem Knopf ab, der Knopf als Scheibe von der Karte (vorher dieselbe
    Farbe, 1:1), und der markierte Goldstern hat einen Rand mit mindestens
    3:1 zu seinem Grund."""
    ctx = browser.new_context(viewport={"width": 360, "height": 726}, locale="de-DE", service_workers="block",
                              color_scheme=schema)
    seite = Seite(ctx.new_page(), basis)
    try:
        seite.starten(stand=heute_stand())
        seite.js(LEGEN, [{"typ": "mc"}])
        werte = {}
        for nr in range(1, 10):
            leer = seite.js(KNOPF_FARBEN, [nr, False])
            an = seite.js(KNOPF_FARBEN, [nr, True])
            werte[nr] = (round(_kontrast(leer["strich"], leer["grund"]), 2),
                         round(_kontrast(leer["grund"], leer["karte"]), 2),
                         round(_kontrast(an["strich"], an["grund"]), 2))
        assert all(s >= 4.5 and k >= 1.25 and g >= 3 for s, k, g in werte.values()), (schema, werte)
        assert seite.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------------------------------
# Die Leiste unter der Karte
# ---------------------------------------------------------------------------

LEISTE = """(id) => { const nav = document.getElementById(id).parentElement, q = nav.firstElementChild;
  const n = nav.getBoundingClientRect(), r = q.getBoundingClientRect();
  return {kinder: [...nav.children].map(e => e.tagName + (e.id ? '#' + e.id : '')), navH: n.height, quitH: r.height,
          links: r.left - n.left, quitTop: r.top - n.top, sterne: nav.querySelectorAll('.stern').length}; }"""


@pytest.mark.parametrize("quit", ["lQuit", "tQuit"])
def test_leiste_nur_noch_abbrechen(seite, heute_stand, quit):
    """Die Leiste hat wieder nur "abbrechen" links und den leeren Platzhalter
    (wie vor dem 19.10.2026 und wie in der Einstufung) und ist so hoch wie
    der Knopf: 39 px (Windows) bzw. 38 px (Linux-CI, Noto). Mit dem Stern war
    sie genau so hoch - an ihr aendert sich nichts."""
    seite.starten(stand=heute_stand())
    if quit == "lQuit":
        seite.js(LEGEN, [{"typ": "mc"}])
    else:
        _test_starten(seite)
    _vorspann_weg(seite)
    m = seite.js(LEISTE, quit)
    assert m["kinder"] == ["BUTTON#" + quit, "SPAN"] and m["sterne"] == 0, m
    assert abs(m["navH"] - 39) <= 1 and m["navH"] == m["quitH"] and m["quitTop"] == 0 and m["links"] == 0, m
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Masse und Zentrierung aus dem Entwurf
# ---------------------------------------------------------------------------

# Trefferflaeche wie im Entwurf nachgemessen: elementFromPoint im
# 0,25-px-Raster durch die Mitte, waagrecht und senkrecht, dazu die Ecken.
TREFFER = """(id) => { const b = document.getElementById(id), r = b.getBoundingClientRect();
  const mx = r.left + r.width / 2, my = r.top + r.height / 2;
  const trifft = (x, y) => { const e = document.elementFromPoint(x, y); return !!e && (e === b || b.contains(e)); };
  const spanne = (fn) => { let a = 1e9, z = -1e9; for(let d = -32; d <= 32; d += 0.25){ if(fn(d)){ a = Math.min(a, d); z = Math.max(z, d); } }
    return z - a + 0.25; };
  const v = getComputedStyle(b, '::before');
  return {w: spanne(d => trifft(mx + d, my)), h: spanne(d => trifft(mx, my + d)), vor: [v.width, v.height],
          ecken: [[-23, -23], [23, -23], [-23, 23], [23, 23]].every(([dx, dy]) => trifft(mx + dx, my + dy))}; }"""


MESS_STIL = """(art) => {
  let st = document.getElementById('messStil');
  if(!st){ st = document.createElement('style'); st.id = 'messStil'; document.head.appendChild(st); }
  const ruhig = '.kastenkopf .stern, .kastenkopf .stern *{transition:none!important; animation:none!important}';
  const T = {
    echt: '',
    ohneStern: '.kastenkopf .stern svg{visibility:hidden!important}',
    maskeStern: '.kastenkopf .stern{background:transparent!important; border-color:transparent!important}' +
                ' .kastenkopf .stern .sternsym path{stroke:#000!important} .kastenkopf .stern .sternsym.an path{fill:#000!important}',
    maskeLeer: '.kastenkopf .stern{background:transparent!important; border-color:transparent!important}' +
               ' .kastenkopf .stern svg{visibility:hidden!important}',
    maskeKreis: '.kastenkopf .stern{background:#000!important; border-color:#000!important} .kastenkopf .stern svg{visibility:hidden!important}',
  };
  st.textContent = ruhig + T[art];
}"""

# Schwerpunkte aus den Bildschirmfotos, im Browser ausgerechnet (der e2e-venv
# hat kein numpy). geo: Stern- gegen Kreismaske, nach Deckung gewichtet.
# echt: |echt - ohneStern| ueber 20 % des Hoechstwerts, ungewichtet.
SCHWERPUNKT = """async (bilder) => {
  const lade = async s => { const img = new Image(); img.src = 'data:image/png;base64,' + s; await img.decode();
    const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight;
    const x = c.getContext('2d'); x.drawImage(img, 0, 0); return x.getImageData(0, 0, c.width, c.height); };
  const d = {}; for(const k of Object.keys(bilder)) d[k] = await lade(bilder[k]);
  const diff = (a, b) => { const out = new Float64Array(a.width * a.height);
    for(let i = 0; i < out.length; i++) out[i] = Math.abs(a.data[4*i] - b.data[4*i]) + Math.abs(a.data[4*i+1] - b.data[4*i+1]) + Math.abs(a.data[4*i+2] - b.data[4*i+2]);
    return out; };
  const mitte = (w, breite) => { let s = 0, sx = 0, sy = 0;
    for(let i = 0; i < w.length; i++){ if(!w[i]) continue; const x = i % breite, y = Math.floor(i / breite); s += w[i]; sx += w[i] * x; sy += w[i] * y; }
    return [sx / s, sy / s]; };
  const B = d.echt.width;
  const ws = diff(d.maskeStern, d.maskeLeer), wk = diff(d.maskeKreis, d.maskeLeer), we = diff(d.echt, d.ohneStern);
  let max = 0; for(const v of we) max = Math.max(max, v);
  const we2 = we.map(v => v > 0.2 * max ? 1 : 0);
  const [sx, sy] = mitte(ws, B), [kx, ky] = mitte(wk, B), [ex, ey] = mitte(we2, B);
  return {dx_geo: sx - kx, dy_geo: sy - ky, dx_echt: ex - kx, dy_echt: ey - ky, breite: B};
}"""

DREHPUNKT = """(id) => { const b = document.getElementById(id), r = b.getBoundingClientRect(), s = b.querySelector('svg');
  const p = new DOMPoint(0, 0).matrixTransform(s.getScreenCTM());
  return {dx: p.x - (r.left + r.width / 2), dy: p.y - (r.top + r.height / 2)}; }"""


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_stern_sitzt_in_der_mitte(browser, basis, heute_stand, schema):
    """Wie im Entwurf nachgemessen: Flaechenschwerpunkt des Sterns gegen die
    Mitte des Kreises, in Geraetepixeln, unter 0,5 - leer und markiert, bei
    412 x 915 (dpr 2,625) und Ajdins S21 (360 x 726, dpr 3)."""
    funde = {}
    for (breite, hoehe, dpr) in ((412, 915, 2.625), (360, 726, 3)):
        ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, device_scale_factor=dpr,
                                  locale="de-DE", service_workers="block", color_scheme=schema,
                                  reduced_motion="reduce")
        seite = Seite(ctx.new_page(), basis)
        try:
            seite.starten(stand=heute_stand())
            seite.js(LEGEN, [{"typ": "mc"}])
            _vorspann_weg(seite)
            seite.page.mouse.move(0, 0)
            for an in (False, True):
                seite.js("(an) => sternZeigen(document.getElementById('lStern'), an)", an)
                r = seite.js("() => { const r = document.getElementById('lStern').getBoundingClientRect();"
                             " return {x: r.left - 8, y: r.top - 8, width: r.width + 16, height: r.height + 16}; }")
                bilder = {}
                for art in ("echt", "ohneStern", "maskeStern", "maskeLeer", "maskeKreis"):
                    seite.js(MESS_STIL, art)
                    seite.page.wait_for_timeout(30)
                    bilder[art] = base64.b64encode(seite.page.screenshot(clip=r)).decode("ascii")
                seite.js(MESS_STIL, "echt")
                m = seite.js(SCHWERPUNKT, bilder)
                lay = seite.js(DREHPUNKT, "lStern")
                fall = "%d_%s" % (breite, "an" if an else "leer")
                funde[fall] = m
                assert abs(m["breite"] - (40 + 16) * dpr) <= 1, m
                for k in ("dx_geo", "dy_geo", "dx_echt", "dy_echt"):
                    assert abs(m[k]) < 0.5, (schema, fall, k, m)
                assert abs(lay["dx"]) < 0.01 and abs(lay["dy"]) < 0.01, (schema, fall, lay)
            assert seite.fehler == []
        finally:
            ctx.close()
    print(schema, json.dumps(funde))   # mit -s sichtbar
    assert len(funde) == 4


# ---------------------------------------------------------------------------
# Wo der Stern nicht steht
# ---------------------------------------------------------------------------

def test_kein_stern_in_einstufung(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js("() => { baueEinstufung('etwas'); einstufungStarten(); }")
    seite.page.locator("#eBody .opt, #eBody #xIn").first.wait_for()
    assert seite.js("() => document.querySelectorAll('#einstufungView .stern').length") == 0
    assert seite.page.locator(".stern.v1:visible").count() == 0
    assert seite.fehler == []


def test_kein_stern_auf_dem_ergebnis(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(LEGEN, [{"typ": "mc"}])
    assert seite.js(KNOPF, "lStern")["sichtbar"]
    seite.js(ANTWORTEN, [True, "Lx"])
    seite.js(WEITER)
    seite.page.locator("#lBody .result-big").wait_for()
    assert not seite.js(KNOPF, "lStern")["sichtbar"]
    assert seite.fehler == []


def test_kein_stern_ohne_leben_in_der_lektion(seite, heute_stand):
    seite.starten(stand=heute_stand(leben={"anzahl": 1, "zeit": 4102444800000}))
    seite.js(LEGEN, [{"typ": "mc"}, {"typ": "mcrev", "wort": 1}])
    seite.js(ANTWORTEN, [False, "Lx"])
    assert seite.js(KNOPF, "lStern")["sichtbar"], "nach der falschen Antwort steht er noch"
    seite.js(WEITER)
    seite.page.locator("#lBody .result-big.fail.ohneleben").wait_for()
    assert not seite.js(KNOPF, "lStern")["sichtbar"]
    assert seite.fehler == []


def test_kein_stern_ohne_leben_im_test(seite, heute_stand):
    """Seit 76b2d45 kostet der Level-Test Leben; sein Schirm ohne Leben hat
    wie der der Lektion keinen Stern."""
    seite.starten(stand=heute_stand(leben={"anzahl": 1, "zeit": 4102444800000}))
    _test_starten(seite)
    assert seite.js(KNOPF, "tStern")["sichtbar"]
    seite.js(ANTWORTEN, [False, "Tx"])
    assert seite.js(KNOPF, "tStern")["sichtbar"], "nach der falschen Antwort steht er noch"
    seite.js(WEITER, "tBody")
    seite.page.locator("#tBody .result-big.fail.ohneleben").wait_for()
    assert not seite.js(KNOPF, "tStern")["sichtbar"]
    assert seite.page.locator(".stern.v1:visible").count() == 0
    assert seite.fehler == []


def test_level_test_stern_und_ergebnis(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _test_starten(seite)
    knopf = seite.js(KNOPF, "tStern")
    assert knopf["sichtbar"] and knopf["gedrueckt"] == "false" and not knopf["imKoerper"]
    assert knopf["name"] == "Markieren" and (knopf["w"], knopf["h"]) == (40, 40)
    k = seite.js("() => topfSchluessel(Tx.qs[Tx.i])")
    seite.page.click("#tStern")
    assert seite.js("(k) => !!stern[k]", k)
    assert seite.js(KNOPF, "tStern")["gold"]
    _ansage(seite, "Markiert")
    seite.durchspielen("tBody", "Tx")
    seite.page.locator("#tBody .result-big").wait_for()
    assert not seite.js(KNOPF, "tStern")["sichtbar"]
    assert seite.js("(k) => !!stern[k]", k), "der Stern bleibt nach dem Test"
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Obergrenze
# ---------------------------------------------------------------------------

def test_obergrenze_300(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js("""(ids) => { stern = {}; ids.slice(1, 301).forEach((id, i) => { stern['w:' + id] = {z: i + 1, r: 0}; });
                           saveProgress(); }""", seite.js(WOERTER, 301))
    assert seite.js("() => STERN_MAX") == 300
    # ein Wort, das noch nicht markiert ist (das erste von allen)
    seite.js("""() => { openLevel(0); startLesson(); const w = [...new Map(CATEGORIES.flatMap(c => c.words).map(w => [w.id, w])).values()][0];
                        Lx.queue = [{typ: 'mc', w, pool: CATEGORIES[0].words}]; Lx.i = 0; showLessonTask(); }""")
    assert seite.js(KNOPF, "lStern")["gedrueckt"] == "false"
    seite.page.click("#lStern")
    assert seite.js(KNOPF, "lStern")["gedrueckt"] == "false", "voll: der Stern geht nicht an"
    assert seite.js("() => Object.keys(stern).length") == 300, "nichts still geloescht, nichts dazu"
    seite.page.wait_for_function("() => { const k = document.querySelector('.kurznote'); return k && k.textContent === 'Schon 300 markiert'; }",
                                 timeout=3000)
    assert seite.js("() => document.querySelector('.kurznote').getAttribute('role')") == "status"
    assert len(_stand(seite)) == 300
    assert seite.fehler == []


def test_obergrenze_beim_laden(seite, heute_stand):
    """Ein Stand mit 301 Sternen (etwa von Hand) behaelt die 300 zuletzt markierten."""
    seite.starten(stand=heute_stand())
    ids = seite.js(WOERTER, 301)
    stern = {"w:" + x: {"z": 1000 + i, "r": 0} for i, x in enumerate(ids)}
    seite.starten(stand=heute_stand(stern=stern))
    drin = seite.js("() => Object.keys(stern)")
    assert len(drin) == 300
    assert "w:" + ids[0] not in drin, "der am fruehesten markierte faellt weg"
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Reiter Wiederholen
# ---------------------------------------------------------------------------

# Der alte Kasten, wie showTopf() ihn bis zum 19.10.2026 baute - Zeichen fuer Zeichen.
TOPF_ALT = """() => {
  const n = Object.keys(topf).length;
  let html = '<h2>' + esc(t('topf.titel')) + '</h2><div class="desc">' + esc(t('topf.desc')) + '</div>';
  if(!n) return html + '<div class="topfleer">' + esc(t('topf.leer')) + '</div>';
  return html + '<div class="topfzahl">' + n + '</div><div class="topfwort">' + esc(tp('topf.anzahl', n)) + '</div>'
              + '<div class="row"><button class="btn know" id="topfLos">' + esc(t('topf.start')) + '</button></div>';
}"""

FUELLEN = """([nTopf, nStern]) => {
  const ids = [...new Map(CATEGORIES.flatMap(c => c.words).map(w => [w.id, w])).keys()];
  topf = {}; stern = {};
  ids.slice(0, nTopf).forEach((id, i) => { topf['w:' + id] = {typ: 'mc', n: 0, z: 1000 + i}; });
  ids.slice(50, 50 + nStern).forEach((id, i) => { stern['w:' + id] = {z: 2000 + i, r: 0}; });
  saveProgress(); homeMode = 'topf'; showHome();
}"""

KAESTEN = """() => {
  const tb = document.getElementById('topfBox'), sb = document.getElementById('sternBox');
  const txt = s => { const e = sb.querySelector(s); return e ? e.textContent.trim() : null; };
  // der Aufbau: je Kind Tag, Klasse, Hoehe, Schrift und Abstaende
  const bau = box => [...box.children].map(e => { const s = getComputedStyle(e), r = e.getBoundingClientRect();
    return [e.tagName, e.className, +r.height.toFixed(2), s.fontSize, s.fontWeight, s.fontFamily, s.color,
            s.marginTop, s.marginBottom, s.textAlign]; });
  const leer = sb.querySelector('.topfleer');
  const titelStern = sb.querySelector('h2 > svg.sternsym');
  const w = document.getElementById('weiterKnopf');
  return {topfHtml: tb.innerHTML, topfKlasse: tb.className,
          reihenfolge: tb.nextElementSibling === sb,
          sternKlasse: sb.className, sichtbar: sb.offsetParent !== null,
          topfBau: bau(tb), sternBau: bau(sb),
          topfH: +tb.getBoundingClientRect().height.toFixed(2), sternH: +sb.getBoundingClientRect().height.toFixed(2),
          titel: txt('h2'), desc: txt('.desc'), zahl: txt('.topfzahl'), wort: txt('.topfwort'),
          knopf: txt('#sternLos'), knopfKlasse: sb.querySelector('#sternLos') && sb.querySelector('#sternLos').className,
          titelStern: titelStern && {gold: titelStern.classList.contains('an'), w: titelStern.getAttribute('width'),
                                      versteckt: titelStern.getAttribute('aria-hidden')},
          leer: leer && [...leer.childNodes].map(n => n.nodeType === 3 ? n.textContent : '[' + n.getAttribute('aria-label') + ']').join(''),
          leerStern: leer && leer.querySelector('svg') && {rolle: leer.querySelector('svg').getAttribute('role'),
                                                          w: leer.querySelector('svg').getAttribute('width')},
          notizen: document.querySelectorAll('#topfHome .note').length,
          weiter: w.style.display, weiterText: w.textContent};
}"""


@pytest.mark.parametrize("breite", [412, 360])
def test_reiter_wiederholen_zeigt_beide_kaesten_im_selben_aufbau(browser, basis, heute_stand, breite):
    ctx = browser.new_context(viewport={"width": breite, "height": 915}, locale="de-DE", service_workers="block")
    seite = Seite(ctx.new_page(), basis)
    try:
        seite.starten(stand=heute_stand())
        seite.js(FUELLEN, [3, 8])
        k = seite.js(KAESTEN)
        assert k["topfHtml"] == seite.js(TOPF_ALT), "der Kasten fuer Fehler hat sich veraendert"
        assert k["topfKlasse"] == "section"
        assert k["reihenfolge"], "Markiert gehoert direkt unter den alten Kasten"
        assert k["sichtbar"] and k["sternKlasse"] == "section"
        assert k["titel"] == "Markiert"
        assert k["desc"] == ("Hier landen Aufgaben, die du mit dem Stern markierst. "
                             "Sie bleiben, bis du den Stern wieder wegnimmst.")
        assert k["zahl"] == "8" and k["wort"] == "Aufgaben markiert"
        assert k["knopf"] == "Runde starten" and k["knopfKlasse"] == "btn know"
        assert k["titelStern"] == {"gold": True, "w": "22", "versteckt": "true"}
        assert k["leer"] is None
        # gleicher Aufbau, gleiche Masse - Kind fuer Kind und als Ganzes
        assert len(k["topfBau"]) == len(k["sternBau"]) == 5
        for a, b in zip(k["topfBau"], k["sternBau"]):
            assert a[1:] == b[1:] and a[0] == b[0], (a, b)
        assert k["topfH"] == k["sternH"], (k["topfH"], k["sternH"])
        # Einzahl
        seite.js(FUELLEN, [3, 1])
        assert seite.js(KAESTEN)["wort"] == "Aufgabe markiert"
        assert seite.fehler == []
    finally:
        ctx.close()


def test_reiter_wiederholen_leer(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(FUELLEN, [0, 0])
    k = seite.js(KAESTEN)
    assert k["topfHtml"] == seite.js(TOPF_ALT)
    assert k["sternKlasse"] == "section"
    assert k["leer"] == "Noch nichts markiert. Tippe in einer Aufgabe oben rechts auf [Stern]."
    assert k["leerStern"] == {"rolle": "img", "w": "17"}
    assert k["titelStern"] == {"gold": False, "w": "22", "versteckt": "true"}
    assert k["knopf"] is None and k["zahl"] is None
    # Aufbau wie der leere alte Kasten: h2, .desc, .topfleer
    assert [x[:2] for x in k["sternBau"]] == [x[:2] for x in k["topfBau"]] == \
        [["H2", ""], ["DIV", "desc"], ["DIV", "topfleer"]]
    assert seite.fehler == []


def test_reiter_wiederholen_ohne_leben(seite, heute_stand):
    """Ohne Leben keine Runde, auch nicht aus "Markiert": der Kasten zeigt
    dann wie der darueber den Hinweis und die Wege zu einem Leben. Wachsen
    Leben nach, kommt "Runde starten" in beiden zurueck."""
    seite.starten(stand=heute_stand(leben={"anzahl": 0, "zeit": 4102444800000}))
    seite.js(FUELLEN, [3, 2])
    k = seite.js(KAESTEN)
    assert k["knopf"] is None and seite.js("() => !document.getElementById('topfLos')")
    assert k["zahl"] == "2"
    assert k["notizen"] == 2
    assert seite.js("() => document.querySelector('#sternBox .note').textContent === "
                    "document.querySelector('#topfBox .note').textContent")
    seite.js(FUELLEN, [0, 2])
    k = seite.js(KAESTEN)
    assert k["knopf"] is None
    assert k["notizen"] == 1 and seite.js("() => !!document.querySelector('#sternBox .note')")
    seite.js("() => startStern()")
    assert seite.js("() => !Lx || Lx.quelle !== 'stern'"), "ohne Leben darf keine Runde starten"
    seite.js(FUELLEN, [3, 2])
    seite.js("() => { lives = {anzahl: 3, zeit: Date.now()}; topfNachziehen(); }")
    assert seite.js("() => !!document.getElementById('sternLos') && !!document.getElementById('topfLos')")
    assert seite.fehler == []


def test_weitermachen_knopf_unveraendert(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(FUELLEN, [0, 4])
    assert seite.js(KAESTEN)["weiter"] == "none", "nur Sterne: Weitermachen startet keine Markiert-Runde"
    seite.js(FUELLEN, [3, 4])
    k = seite.js(KAESTEN)
    assert k["weiter"] == "" and k["weiterText"] == "▶ Weitermachen · Wiederholen"
    seite.page.click("#weiterKnopf")
    lage = seite.js("() => ({quelle: Lx.quelle, alleImTopf: Lx.queue.every(a => topfSchluessel(a) in topf)})")
    assert lage == {"quelle": "topf", "alleImTopf": True}
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Markiert-Runde
# ---------------------------------------------------------------------------

def test_markiert_runde_auswahl_und_reihenfolge(seite, heute_stand):
    seite.starten(stand=heute_stand())
    ids = seite.js(WOERTER, 12)
    # vier nie geuebt, acht mit r; die zwei mit dem groessten r fallen heraus
    stern = {}
    for i, x in enumerate(ids):
        stern["w:" + x] = {"z": 1000 + i, "r": 0 if i < 4 else 5000 + (12 - i)}
    seite.starten(stand=heute_stand(stern=stern))
    seite.js("() => { homeMode = 'topf'; showHome(); }")
    seite.page.click("#sternLos")
    lage = seite.js("() => ({quelle: Lx.quelle, topf: Lx.topf, n: Lx.queue.length, tag: document.getElementById('tag').textContent,"
                    " keys: Lx.queue.map(a => topfSchluessel(a)), typen: Lx.queue.map(a => a.typ)})")
    assert lage["quelle"] == "stern" and lage["topf"] is True and lage["tag"] == "Markiert"
    assert lage["n"] == 10
    erwartet = {"w:" + x for i, x in enumerate(ids) if i not in (4, 5)}
    assert set(lage["keys"]) == erwartet
    assert set(lage["typen"]) <= {"mc", "mcrev", "type", "listen"}, lage["typen"]
    assert seite.js(KNOPF, "lStern")["gedrueckt"] == "true"
    # Die Reihenfolge selbst: nie geuebt zuerst (nach z), dann nach r
    reihe = seite.js("""() => Object.keys(stern).map(k => ({k, e: stern[k]}))
        .sort((a, b) => (a.e.r - b.e.r) || (a.e.z - b.e.z)).map(x => x.k)""")
    assert reihe[:4] == ["w:" + x for x in ids[:4]]
    assert reihe[4] == "w:" + ids[11]
    # gemischt: ueber mehrere Runden nicht immer dieselbe Reihenfolge
    folgen = {tuple(seite.js("() => sternRunde().map(a => topfSchluessel(a))")) for _ in range(8)}
    assert len(folgen) > 1
    assert seite.fehler == []


def test_markiert_runde_woerter_reihum_saetze_behalten_ihre_art(seite, heute_stand):
    seite.starten(stand=heute_stand())
    keys = seite.js(LEGEN, [{"typ": "gap"}, {"typ": "kacheln"}, {"typ": "gram"}, {"typ": "mc"}])
    seite.js("(keys) => { stern = {}; keys.forEach((k, i) => { stern[k] = {z: 100 + i, r: 0}; }); }", keys)
    typen = seite.js("() => { const r = sternRunde(); const m = {}; r.forEach(a => { m[topfSchluessel(a)] = a.typ; }); return m; }")
    assert typen[keys[0]] == "gap" and typen[keys[1]] == "kacheln" and typen[keys[2]] == "gram"
    assert typen[keys[3]] in ("mc", "mcrev", "type", "listen")
    # Woerter reihum: bei zehn tippbaren Woertern kommen mindestens drei Arten vor,
    # Schreiben nie bei nicht tippbaren, Hoeren nur mit canListen
    arten = seite.js("""() => { const ws = CATEGORIES.flatMap(c => c.words).filter(w => typable(w)).slice(0, 10);
        stern = {}; ws.forEach((w, i) => { stern['w:' + w.id] = {z: i + 1, r: 0}; });
        const r = sternRunde(); return {typen: r.map(a => a.typ), hoeren: canListen}; }""")
    assert len(set(arten["typen"])) >= 3, arten
    assert ("listen" in arten["typen"]) <= arten["hoeren"]
    nicht_tippbar = seite.js("""() => { const ws = CATEGORIES.flatMap(c => c.words).filter(w => !typable(w)).slice(0, 10);
        stern = {}; ws.forEach((w, i) => { stern['w:' + w.id] = {z: i + 1, r: 0}; });
        return ws.length ? sternRunde().map(a => a.typ) : []; }""")
    assert "type" not in nicht_tippbar
    assert seite.fehler == []


def test_markiert_runde_richtig_falsch(seite, heute_stand):
    seite.starten(stand=heute_stand())
    ids = seite.js(WOERTER, 3)
    stern = {"w:" + x: {"z": 1000 + i, "r": 0} for i, x in enumerate(ids)}
    seite.starten(stand=heute_stand(stern=stern))
    seite.js("() => { homeMode = 'topf'; showHome(); }")
    seite.page.click("#sternLos")
    vorher = seite.js("() => ({leben: livesNow(), jetzt: Date.now(), n: Lx.queue.length})")
    assert vorher["n"] == 3

    a = seite.js(ANTWORTEN, [True, "Lx"])
    e = seite.js("(k) => stern[k]", a["schluessel"])
    assert e is not None, "der Stern bleibt nach einer richtigen Antwort"
    assert e["r"] >= vorher["jetzt"], "r = jetzt geuebt"
    assert seite.js(KNOPF, "lStern")["gedrueckt"] == "true"
    assert seite.js("(k) => !(k in topf)", a["schluessel"])
    seite.js(WEITER)

    b = seite.js(ANTWORTEN, [False, "Lx"])
    lage = seite.js("""(k) => ({leben: livesNow(), imTopf: k in topf, stern: !!stern[k], r: stern[k].r,
                               n: Lx.queue.length, nochmal: !!Lx.queue[Lx.queue.length - 1].retry})""", b["schluessel"])
    assert lage["leben"] == vorher["leben"] - 1, "falsch kostet ein Leben"
    assert lage["imTopf"], "falsch landet im Fehler-Topf"
    assert lage["stern"] and lage["r"] >= vorher["jetzt"]
    assert lage["n"] == 4 and lage["nochmal"], "falsch kommt am Ende noch einmal"
    seite.js(WEITER)

    # zu Ende spielen: Ergebnis zaehlt wie eine Runde, ohne Stern-Knopf
    while seite.js("() => Lx.i < Lx.queue.length"):
        seite.js(ANTWORTEN, [True, "Lx"])
        seite.js(WEITER)
    seite.page.locator("#lBody .result-big").wait_for()
    ende = seite.js("""() => ({markiert: document.querySelector('#lBody .stat').textContent,
        alles: document.querySelector('#lBody').textContent.indexOf(t('topf.alles')) >= 0,
        tag: days.has(today()), noch: document.getElementById('lMore') && document.getElementById('lMore').textContent})""")
    assert ende["markiert"] == "3markiert"
    assert not ende["alles"]
    assert ende["tag"], "eine Runde zaehlt fuer die Serie"
    assert ende["noch"] == "Noch eine Runde"
    assert not seite.js(KNOPF, "lStern")["sichtbar"]
    assert len(_stand(seite)) == 3
    assert all(v["r"] >= vorher["jetzt"] for v in _stand(seite).values())
    # "Noch eine Runde" startet wieder die Markiert-Runde
    seite.js("() => document.getElementById('lMore').click()")
    assert seite.js("() => Lx.quelle") == "stern"
    assert seite.fehler == []


def test_markiert_runde_stern_unterwegs_wegnehmen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    ids = seite.js(WOERTER, 2)
    seite.starten(stand=heute_stand(stern={"w:" + x: {"z": 10 + i, "r": 0} for i, x in enumerate(ids)}))
    seite.js("() => { homeMode = 'topf'; showHome(); }")
    seite.page.click("#sternLos")
    k = seite.js("() => topfSchluessel(Lx.queue[Lx.i])")
    seite.page.click("#lStern")
    seite.js(ANTWORTEN, [True, "Lx"])
    assert seite.js("(k) => k in stern", k) is False, "weggenommen bleibt weggenommen"
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Sicherungsdatei
# ---------------------------------------------------------------------------

EINLESEN = """async (text) => {
  frage = async () => true;
  await sicherungEinlesen(new File([text], 'sicherung.json', {type: 'application/json'}));
  return {stern, notiz: document.getElementById('sichNote').textContent};
}"""


def test_sicherung_behaelt_sterne(seite, heute_stand):
    seite.starten(stand=heute_stand())
    keys = seite.js(LEGEN, [{"typ": "mc", "wort": 4}, {"typ": "gap"}, {"typ": "kacheln"}, {"typ": "gram"}])
    seite.js("(keys) => { stern = {}; keys.forEach((k, i) => { stern[k] = {z: 1000 + i, r: i * 7}; }); saveProgress(); }",
             keys)
    vorher = seite.js("() => stern")
    datei = json.loads(seite.js("() => sicherungInhalt()"))
    assert datei["version"] == 1
    assert datei["stand"]["stern"] == vorher
    seite.js("() => { stern = {}; saveProgress(); }")
    erg = seite.js(EINLESEN, json.dumps(datei))
    assert erg["stern"] == vorher
    assert _stand(seite) == vorher
    # Eine Sicherung von vorher, ohne das Feld: nichts markiert
    del datei["stand"]["stern"]
    assert seite.js(EINLESEN, json.dumps(datei))["stern"] == {}
    assert seite.fehler == []


def test_kaputte_sterne_werden_verworfen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    ids = seite.js(WOERTER, 8)
    datei = json.loads(seite.js("() => sicherungInhalt()"))
    jetzt = seite.js("() => Date.now()")
    st = {
        "w:" + ids[0]: {"z": 1000, "r": 0},                  # gut
        "w:" + ids[1]: {"z": jetzt + 10 ** 10, "r": jetzt + 10 ** 10},   # Zukunft -> auf jetzt
        "w:" + ids[2]: {"z": 5},                              # r fehlt -> 0
        "x:" + ids[3]: {"z": 1, "r": 0},                      # falscher Anfang
        "w:" + ids[4]: {"z": "1", "r": 0},                    # Text statt Zahl
        "w:" + ids[5]: {"z": -5, "r": 0},                     # negativ
        "w:" + ids[6]: [1, 2],                                # kein Objekt
        "w:" + ids[7]: {"z": "UNENDLICH", "r": 0},            # 1e999 = Infinity
        "w:" + "a" * 300: {"z": 1, "r": 0},                   # zu lang
        "w:gibt es nicht:xyzq": {"z": 1, "r": 0},             # keine Aufgabe dazu
        "__proto__": {"z": 1, "r": 0},
    }
    datei["stand"]["stern"] = st
    text = json.dumps(datei).replace('"UNENDLICH"', "1e999")
    erg = seite.js(EINLESEN, text)["stern"]
    assert set(erg) == {"w:" + ids[0], "w:" + ids[1], "w:" + ids[2]}, sorted(erg)
    assert erg["w:" + ids[0]] == {"z": 1000, "r": 0}
    assert erg["w:" + ids[1]]["z"] <= seite.js("() => Date.now()")
    assert erg["w:" + ids[1]]["r"] <= seite.js("() => Date.now()")
    assert erg["w:" + ids[2]] == {"z": 5, "r": 0}
    assert seite.js("() => Object.getPrototypeOf(stern) === Object.prototype")
    for kaputt in ([], "kaputt", 7, None):
        datei["stand"]["stern"] = kaputt
        assert seite.js(EINLESEN, json.dumps(datei))["stern"] == {}, kaputt
    # Ueber 300: die zuletzt markierten bleiben
    viele = seite.js(WOERTER, 320)
    datei["stand"]["stern"] = {"w:" + x: {"z": 1 + i, "r": 0} for i, x in enumerate(viele)}
    erg = seite.js(EINLESEN, json.dumps(datei))["stern"]
    assert len(erg) == 300 and "w:" + viele[0] not in erg and "w:" + viele[-1] in erg
    assert seite.fehler == []


def test_kaputte_sterne_im_geraetespeicher(seite, heute_stand):
    """Dieselbe Pruefung beim Start aus dem Geraetespeicher (standUebernehmen):
    nichts wirft, Kaputtes faellt still weg, die Zukunft wird auf jetzt gesetzt."""
    seite.starten(stand=heute_stand())
    ids = seite.js(WOERTER, 3)
    jetzt = seite.js("() => Date.now()")
    st = {"w:" + ids[0]: {"z": 7, "r": 3}, "w:" + ids[1]: {"z": jetzt + 10 ** 9, "r": 0},
          "w:" + ids[2]: {"z": None, "r": 0}, "q:x": {"z": 1, "r": 0}, "w:verwaist:nirgends": {"z": 1, "r": 0}}
    seite.starten(stand=heute_stand(stern=st))
    drin = seite.js("() => stern")
    assert set(drin) == {"w:" + ids[0], "w:" + ids[1]}
    assert drin["w:" + ids[0]] == {"z": 7, "r": 3}
    assert drin["w:" + ids[1]]["z"] <= seite.js("() => Date.now()")
    assert _stand(seite) == drin, "bereinigt gespeichert"
    for kaputt in ([], "x", 3):
        seite.starten(stand=heute_stand(stern=kaputt))
        assert seite.js("() => stern") == {}
    assert seite.fehler == []


def test_umbenannte_woerter_behalten_ihren_stern(seite, heute_stand):
    seite.starten(stand=heute_stand())
    probe = seite.js("""() => {
      const zaehl = new Map();
      CATEGORIES.forEach(c => c.words.forEach(w => zaehl.set(w.bs, (zaehl.get(w.bs) || new Set()).add(w.id))));
      const w = CATEGORIES.flatMap(c => c.words).find(w => zaehl.get(w.bs).size === 1 && w.id.indexOf('kaffee') < 0);
      return {einzig: w.id, alt: 'eine alte bedeutung:' + w.bs,
              kaffee: wortNachId('kaffee:kahva / kafa') ? 'kaffee:kahva / kafa' : null};
    }""")
    st = {"w:" + probe["alt"]: {"z": 50, "r": 7}}
    if probe["kaffee"]:
        st["w:kaffee:kahva"] = {"z": 60, "r": 0}
    seite.starten(stand=heute_stand(stern=st))
    drin = seite.js("() => stern")
    assert drin.get("w:" + probe["einzig"]) == {"z": 50, "r": 7}
    assert "w:" + probe["alt"] not in drin
    if probe["kaffee"]:
        assert "w:" + probe["kaffee"] in drin and "w:kaffee:kahva" not in drin
    assert _stand(seite) == drin, "umgeschrieben und gleich gespeichert"
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# axe
# ---------------------------------------------------------------------------

AXE_LAUF = """async () => (await axe.run(document, {resultTypes: ['violations']}))
    .violations.filter(v => v.impact === 'serious' || v.impact === 'critical')
    .map(v => v.id + ' (' + v.impact + '): ' + v.nodes.map(n => n.target.join(' ')).join(', '))"""


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_axe_wiederholen_und_aufgabe_mit_stern(browser, basis, heute_stand, schema):
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                              service_workers="block", color_scheme=schema)
    seite = Seite(ctx.new_page(), basis)
    try:
        seite.starten(stand=heute_stand())
        seite.page.add_script_tag(path=AXE)
        funde = []
        seite.js(FUELLEN, [3, 2])
        funde += ["wiederholen: " + v for v in seite.js(AXE_LAUF)]
        seite.js(FUELLEN, [3, 0])
        funde += ["wiederholen-leer: " + v for v in seite.js(AXE_LAUF)]
        seite.js(LEGEN, [{"typ": "mc"}])
        funde += ["aufgabe: " + v for v in seite.js(AXE_LAUF)]
        seite.page.click("#lStern")
        seite.js(ANTWORTEN, [True, "Lx"])
        seite.page.locator("#lBody .weiterbox .btn").wait_for()
        funde += ["aufgabe-markiert: " + v for v in seite.js(AXE_LAUF)]
        _test_starten(seite)
        funde += ["test: " + v for v in seite.js(AXE_LAUF)]
        assert not funde, "\n".join(funde)
        assert seite.fehler == []
    finally:
        ctx.close()
