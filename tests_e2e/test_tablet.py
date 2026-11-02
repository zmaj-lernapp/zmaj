# -*- coding: utf-8 -*-
"""Tablets: die App waechst mit dem Bildschirm (30.10.2026).

Ajdin zu den ersten Store-Bildern fuer 7- und 10-Zoll-Tablets: "die tablet
bilder die zeigen zu viel platz kann man nicht je nach dem wie gross der
bildschirm ist das layout anpassen". Die App war ueberall eine Spalte bis
540 Punkte in Handygroesse. Auf dem 10-Zoll-Tablet hochkant (800 x 1280)
blieben links und rechts je 130 Punkte leer, und unter einer Lektion stand
der halbe Bildschirm leer.

Seitdem (siehe GROSS im Kopf von web/index.html und "Tablets" im Stil):
  - ab 600 Punkten kleinstem Seitenmass vergroessert CSS-zoom die ganze
    App; hochkant fuellt die Spalte 85 bis 90 % der Breite, quer steht sie
    in der Mitte und laesst 740 Punkte Hoehe,
  - Lektion, Level-Test und Einstufung fuellen den Bildschirm; hochkant
    stehen Drache und Aufgabe mittig, die Antworten unten, Pruefen und
    Weiter ganz unten, und nach der Antwort springt nichts,
  - am Handy aendert sich nichts.

Geprueft wird hier in den Massen echter Geraete, alle mit Touch wie im
Tablet: 7 Zoll (600 x 960), 10 Zoll (800 x 1280), iPad (768 x 1024),
iPad Pro 11 Zoll (834 x 1194) und 12,9 Zoll (1024 x 1366), jeweils auch
quer, wo es zaehlt. Den Bildvergleich vorher/nachher am Handy (360 x 640,
390 x 844, 412 x 915, 360 x 726, 844 x 390, je 16 Schirme: alle 80 Bilder
Pixel fuer Pixel gleich) hat der Lauf vom 30.10.2026 gemacht, fuer jede
Groesse mit frischem Browser. Liefen alle Groessen nacheinander im
selben Browser, zeichnete Chrome bei der neuen Fassung ab der zweiten
Groesse den Schein der gefaerbten Flamme oben minimal anders (hoechstens
43 von 255 in einem Farbkanal, rund 1400 Pixel); jede Groesse fuer sich
war gleich, auch mit leerem style am Wurzelelement. Fuer einen solchen
Vergleich also je Groesse einen eigenen Browser starten.
test_handy_bleibt_wie_es_war sichert ab, dass dort keine der neuen Regeln
greift. test_layout_test.py misst zusaetzlich bei 800 x 1280,
dass Lektion, Level-Test und Einstufung auch auf dem Tablet gleich stehen.
"""
import pytest
from conftest import Seite

# (id, Breite, Hoehe, erwarteter Massstab, .hoch?, Anteil der Spalte an der Breite oder None)
TABLETS = [
    pytest.param(600, 960, 1.0, True, (0.89, 0.91), id="7zoll_hoch"),
    pytest.param(960, 600, 1.0, False, None, id="7zoll_quer"),
    pytest.param(800, 1280, 1.304, True, (0.85, 0.90), id="10zoll_hoch"),
    pytest.param(1280, 800, 1.081, False, None, id="10zoll_quer"),
    pytest.param(768, 1024, 1.219, True, (0.85, 0.90), id="ipad_hoch"),
    pytest.param(834, 1194, 1.359, True, (0.85, 0.90), id="ipad11_hoch"),
    pytest.param(1024, 1366, 1.4, True, (0.85, 0.90), id="ipad13_hoch"),
    pytest.param(1366, 1024, 1.384, False, None, id="ipad13_quer"),
]
HANDYS = [
    pytest.param(360, 640, id="360x640"),
    pytest.param(390, 844, id="390x844"),
    pytest.param(412, 915, id="412x915"),
    pytest.param(360, 726, id="s21_360x726"),
    pytest.param(844, 390, id="quer_844x390"),
]
TYPEN = ["intro", "mc", "mcrev", "listen", "type", "gap", "gram", "kacheln"]


@pytest.fixture
def geraet(browser, basis):
    kontexte = []

    def neu(breite, hoehe, stand):
        ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, device_scale_factor=2,
                                  is_mobile=True, has_touch=True, locale="de-DE", service_workers="block")
        kontexte.append(ctx)
        s = Seite(ctx.new_page(), basis)
        s.starten(stand=stand)
        return s

    yield neu
    for ctx in kontexte:
        ctx.close()


MASSE = r"""
() => {
  const d = document.documentElement, w = document.querySelector('.wrap').getBoundingClientRect();
  return {gross: d.classList.contains('gross'), hoch: d.classList.contains('hoch'), GROSS,
          zoom: getComputedStyle(d).zoom, stil: d.getAttribute('style') || '',
          links: w.left, rechts: innerWidth - w.right, breite: w.width,
          seiteB: d.scrollWidth, innenB: innerWidth, innenH: innerHeight,
          maxBreite: getComputedStyle(document.querySelector('.wrap')).maxWidth,
          minHoehe: getComputedStyle(document.body).minHeight,
          kopfEng: document.querySelector('header').classList.contains('eng'),
          zahnrad: (r => [r.width, r.height])(document.getElementById('btnSettings').getBoundingClientRect())};
}
"""


@pytest.mark.parametrize("breite, hoehe, massstab, hoch, anteil", TABLETS)
def test_massstab_und_spalte(geraet, heute_stand, breite, hoehe, massstab, hoch, anteil):
    s = geraet(breite, hoehe, heute_stand())
    for ansicht in ("homeMode = 'words'; showHome();", "openLevel(0);", "openStory(0);",
                    "document.getElementById('btnSettings').click();"):
        s.js("() => { %s }" % ansicht)
        s.page.wait_for_timeout(150)
        m = s.js(MASSE)
        assert m["gross"] and m["hoch"] is hoch, m
        assert m["GROSS"] == pytest.approx(massstab, abs=0.001), m
        assert float(m["zoom"]) == pytest.approx(massstab, abs=0.001), m
        # keine seitliche Scrollleiste, Spalte genau in der Mitte
        assert m["seiteB"] <= m["innenB"], (ansicht, m)
        assert abs(m["links"] - m["rechts"]) <= 1, (ansicht, m)
        if anteil:
            assert anteil[0] <= m["breite"] / breite <= anteil[1], (ansicht, m["breite"] / breite)
        assert not m["kopfEng"], "Kopfleiste in zwei Zeilen"
        # Knoepfe wachsen mit: das Zahnrad ist 38 Punkte am Handy
        assert m["zahnrad"][0] == pytest.approx(38 * massstab, abs=1), m["zahnrad"]
    assert s.fehler == [] and s.fremd == []


# Aufgaben wie in test_layout_test.py, dazu Satzbau mit einem laengeren Satz
HELFER = r"""
() => {
  const saat = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  window.__saatWert = null;
  if(!window.__rtOrig){
    window.__rtOrig = renderTask;
    renderTask = function(){
      if(window.__saatWert != null){ Math.random = saat(window.__saatWert); window.__saatWert = null; }
      return window.__rtOrig.apply(this, arguments);
    };
  }
  const c0 = CATEGORIES[0];
  const w = c0.words.find(x => typable(x) && x.de.length <= 14 && x.bs.length <= 10 && x.bs.length >= 4) || c0.words[0];
  const gap = SENTENCES.find(x => x.kat === c0.id && x.text.indexOf('___') >= 0) || SENTENCES.find(x => x.text.indexOf('___') >= 0);
  let gram = null;
  for(const c of CATEGORIES){ const u = (GRAMMAR[c.id] || {}).uebungen || []; const g = u.find(x => x.optionen.length >= 3); if(g){ gram = g; break; } }
  const kach = SATZBAU.slice().sort((a, b) => b.bs.length - a.bs.length)[Math.floor(SATZBAU.length / 4)];
  window.__aufgabe = typ => {
    if(typ === 'gap') return {typ, s: gap};
    if(typ === 'gram') return {typ, g: gram};
    if(typ === 'kacheln') return {typ, s: kach};
    return {typ, w, pool: c0.words};
  };
  return !!(w && gap && gram && kach);
}
"""

# Eine Aufgabe als erste der Lektion, messen, richtig antworten, messen.
# Alle Masse in Bildschirmpunkten (getBoundingClientRect, Chrome >= 128).
AUFGABE = r"""
async ([typ, seed]) => {
  const warte = ms => new Promise(r => setTimeout(r, ms));
  const body = document.getElementById('lBody');
  const task = __aufgabe(typ);
  openLevel(0); startLesson();
  Lx.queue[0] = task; Lx.i = 0; Lx.results = [];
  window.__saatWert = seed; showLessonTask();
  await document.fonts.ready; await warte(300);
  const q = s => body.querySelector(s);
  const r = el => { if(!el) return null; const b = el.getBoundingClientRect(); return {l: b.left, o: b.top, r: b.right, u: b.bottom}; };
  const sichtbar = e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden';
  const knoepfe = () => [...body.querySelectorAll('button, input')].filter(sichtbar).map(r);
  const erste = () => q('.options:not(.kachelbank) .opt') || q('#xIn') || q('.kachelbank .opt') || q('#xNext');
  const karte = body.closest('.card');
  const drache = document.getElementById('zmajLesson');
  const svg = drache.querySelector('svg');
  const vor = {erste: r(erste()), knoepfe: knoepfe(), karte: r(karte), pruef: r(q('#xCheck') || q('#xNext')), skip: r(q('.skip')),
               drache: r(drache), svg: r(svg), seiteH: document.documentElement.scrollHeight,
               seiteB: document.documentElement.scrollWidth};
  if(typ === 'intro') return {vor, nach: null};
  if(typ === 'gap' || typ === 'type'){
    q('#xIn').value = (typ === 'gap' ? task.s.answer : task.w.bs).split(' / ')[0]; q('#xCheck').click();
  } else if(typ === 'kacheln'){
    const rand = /^[.,!?¿¡:;"„“”«»…()]+|[.,!?¿¡:;"„“”«»…()]+$/g;
    for(const soll of task.s.bs.split(/\s+/).map(x => x.replace(rand, '').toLowerCase()).filter(Boolean)){
      const b = [...body.querySelectorAll('#xBank .kachel:not(.platz)')].find(o => o.textContent.toLowerCase() === soll);
      if(!b) throw new Error('keine Kachel ' + soll);
      b.click();
    }
    await warte(350);
    q('#xCheck').click();
  } else {
    const soll = typ === 'gram' ? task.g.richtig : (typ === 'mcrev' ? task.w.de : task.w.bs);
    [...body.querySelectorAll('.opt')].find(o => o.textContent === soll).click();
  }
  const ende = Date.now() + 6000;
  while(!q('.weiterbox')){ if(Date.now() > ende) throw new Error('kein Weiter bei ' + typ); await warte(20); }
  await warte(1100);   // sanftes Scrollen von weiterBeiTipp abwarten
  const nach = {erste: r(erste()), weiter: r(q('.weiterbox .btn')), karte: r(karte), scrollY,
                seiteH: document.documentElement.scrollHeight};
  stilleBitte(); q('.weiterbox .btn').click(); await warte(200); stilleBitte();
  return {vor, nach};
}
"""


@pytest.mark.parametrize("breite, hoehe, massstab, hoch, anteil", TABLETS)
def test_lektion_fuellt_den_bildschirm(geraet, heute_stand, breite, hoehe, massstab, hoch, anteil):
    s = geraet(breite, hoehe, heute_stand())
    assert s.js(HELFER), "keine passende Aufgabe in den Daten"
    probleme = []
    for n, typ in enumerate(TYPEN):
        m = s.js(AUFGABE, [typ, 1000 + n])
        v, na = m["vor"], m["nach"]

        def fehler(text):
            probleme.append("%s: %s" % (typ, text))

        if v["seiteB"] > breite:
            fehler("seitlich scrollbar (%s)" % v["seiteB"])
        # Alles zum Antworten sichtbar, ohne zu scrollen
        unten = max(k["u"] for k in v["knoepfe"])
        if unten > hoehe + 0.5:
            fehler("Knopf unter dem Bildrand (%.0f > %d)" % (unten, hoehe))
        # Der Drache steht mittig im Kasten und ist das SVG von Lottie (scharf)
        mitte_karte = (v["karte"]["l"] + v["karte"]["r"]) / 2
        if abs((v["drache"]["l"] + v["drache"]["r"]) / 2 - mitte_karte) > 1:
            fehler("Drache nicht mittig")
        if v["svg"] is None or abs(v["svg"]["r"] - v["svg"]["l"] - (v["drache"]["r"] - v["drache"]["l"])) > 1:
            fehler("Lottie-SVG nicht so gross wie sein Platz: %s / %s" % (v["svg"], v["drache"]))
        if hoehe >= 740:
            # Der Kasten reicht bis "Lektion abbrechen" am unteren Rand: Seite genau
            # so hoch wie der Bildschirm (16 + 48 Rand, 56 fuer die Zeile darunter)
            if v["seiteH"] > hoehe + 1:
                fehler("Seite hoeher als der Bildschirm (%d)" % v["seiteH"])
            if v["karte"]["u"] < hoehe - 120 * massstab - 2:
                fehler("Kasten fuellt den Bildschirm nicht (unten bei %.0f)" % v["karte"]["u"])
        if hoch:
            # Pruefen/Weiter ganz unten im Kasten (24 Punkte Innenrand, 4 Schatten);
            # beim Satzbau steht darunter wie am Handy noch "Ueberspringen"
            unterstes = max(v["pruef"]["u"], v["skip"]["u"] if v["skip"] else 0) if v["pruef"] else None
            if unterstes and v["karte"]["u"] - unterstes > 30 * massstab:
                fehler("Pruefen/Weiter nicht unten (%.0f ueber dem Rand)" % (v["karte"]["u"] - unterstes))
            # Antworten in der unteren Haelfte, Aufgabe darueber
            if v["erste"]["o"] < hoehe * 0.33 and typ not in ("type", "gap"):
                fehler("Antworten zu weit oben (%.0f)" % v["erste"]["o"])
        if na is None:
            continue
        # Weiter sichtbar, ohne zu scrollen, und die getippten Antworten bleiben stehen
        if na["weiter"]["u"] > hoehe + 0.5 or na["scrollY"] > 0:
            fehler("Weiter nicht ohne Scrollen sichtbar (%s, scrollY %s)" % (na["weiter"], na["scrollY"]))
        if typ in ("mc", "mcrev", "listen", "gram") and abs(na["erste"]["o"] - v["erste"]["o"]) > 1:
            fehler("Antworten springen nach der Antwort um %.1f" % (na["erste"]["o"] - v["erste"]["o"]))
        if hoch and abs(na["weiter"]["u"] - (v["pruef"] or na["weiter"])["u"]) > 1 and typ in ("type", "gap", "kacheln"):
            fehler("Weiter steht nicht, wo Pruefen stand")
    assert probleme == [], "\n".join(probleme)
    assert s.fehler == [] and s.fremd == []


MITTE = r"""
async () => {
  const warte = ms => new Promise(r => setTimeout(r, ms));
  homeMode = 'words'; showHome(); await warte(100);
  window.__antwort = 'offen';
  frage('Lektion abbrechen?', 'Dein Fortschritt geht verloren.', 'Ja', 'Nein').then(x => { window.__antwort = x; });
  await warte(100);
  const k = document.querySelector('.nachfrage'), b = k.querySelector('.nachfragebox').getBoundingClientRect(),
        f = k.getBoundingClientRect();
  return {box: [b.left, b.top, b.right, b.bottom], flaeche: [f.left, f.top, f.right, f.bottom]};
}
"""


@pytest.mark.parametrize("breite, hoehe", [pytest.param(800, 1280, id="10zoll_hoch"),
                                           pytest.param(1280, 800, id="10zoll_quer"),
                                           pytest.param(1024, 1366, id="ipad13_hoch")])
def test_dialog_meldung_und_konfetti_mittig(geraet, heute_stand, breite, hoehe):
    s = geraet(breite, hoehe, heute_stand())
    m = s.js(MITTE)
    l, o, r, u = m["box"]
    assert m["flaeche"] == pytest.approx([0, 0, breite, hoehe], abs=0.5), "Abdunkelung deckt nicht den Bildschirm"
    assert abs((l + r) / 2 - breite / 2) <= 1 and abs((o + u) / 2 - hoehe / 2) <= 1, m
    assert l >= 0 and o >= 0 and r <= breite and u <= hoehe
    # Echter Tipp an der Stelle, wo "Nein" zu sehen ist: das Ziel stimmt trotz zoom
    s.page.locator("#frNein").click()
    s.page.wait_for_function("window.__antwort === false", timeout=3000)
    assert s.js("() => document.querySelectorAll('.nachfrage').length") == 0

    # Kurze Meldung: unten in der Mitte, 86 Punkte ueber dem Rand (mit zoom)
    s.js("() => kurzMeldung('Kein Internet.')")
    s.page.wait_for_timeout(300)
    k = s.js("() => { const b = document.querySelector('.kurznote').getBoundingClientRect(); return [b.left, b.right, b.bottom]; }")
    g = s.js("() => GROSS")
    assert abs((k[0] + k[1]) / 2 - breite / 2) <= 1, k
    assert k[2] == pytest.approx(hoehe - 86 * g, abs=1.5), k

    # Wegmarke mit Konfetti: Karte mittig, die Schnipsel fallen ueber die ganze Breite
    s.js("() => { animOn = true; zeigeWegmarke({id:'test', ziel:7, txt:'wegmarke.t7'}); }")
    s.page.wait_for_timeout(300)
    w = s.js("""() => { const b = document.querySelector('.wegmarkebox').getBoundingClientRect();
                        const x = [...document.querySelectorAll('.schnipsel')].map(e => e.getBoundingClientRect().left);
                        return {box: [b.left, b.top, b.right, b.bottom], min: Math.min(...x), max: Math.max(...x), n: x.length}; }""")
    l, o, r, u = w["box"]
    assert abs((l + r) / 2 - breite / 2) <= 1 and abs((o + u) / 2 - hoehe / 2) <= 1, w
    assert w["n"] > 0 and w["min"] >= -1 and w["max"] <= breite, w
    assert s.fehler == [] and s.fremd == []


@pytest.mark.parametrize("breite, hoehe", HANDYS)
def test_handy_bleibt_wie_es_war(geraet, heute_stand, breite, hoehe):
    """Unter 600 Punkten kleinstem Mass: keine Klasse, kein zoom, keine
    Variable, die alten Masse. Auch quer (844 x 390) bleibt es das Handy."""
    s = geraet(breite, hoehe, heute_stand())
    for ansicht in ("homeMode = 'words'; showHome();", "openLevel(0); startLesson();"):
        s.js("() => { %s }" % ansicht)
        s.page.wait_for_timeout(150)
        m = s.js(MASSE)
        assert not m["gross"] and not m["hoch"], m
        assert m["GROSS"] == 1 and m["zoom"] in ("1", "normal") and m["stil"] == "", m
        assert m["maxBreite"] == "540px", m
        assert m["minHoehe"] == "%dpx" % hoehe, m          # 100vh wie bisher
        assert s.js("() => rectFaktor()") == 1
        assert s.js("() => getComputedStyle(document.getElementById('lBody')).display") == "block"
    assert s.fehler == [] and s.fremd == []


def test_tastatur_und_drehen(geraet, heute_stand):
    """Die Tastatur macht die Ansicht niedriger - der Massstab bleibt, nur
    --hoehe zieht nach. Drehen ohne Tastatur rechnet alles neu."""
    s = geraet(800, 1280, heute_stand())
    assert s.js(HELFER)
    s.js("""() => { openLevel(0); startLesson(); Lx.queue[0] = __aufgabe('type'); Lx.i = 0; Lx.results = [];
                    showLessonTask(); document.getElementById('xIn').focus(); }""")
    zustand = "() => [GROSS, document.documentElement.className, getComputedStyle(document.documentElement).getPropertyValue('--hoehe')]"
    z0, k0, _ = s.js(zustand)
    assert z0 == pytest.approx(1.304, abs=0.001) and "hoch" in k0
    s.page.set_viewport_size({"width": 800, "height": 700})      # Tastatur auf
    s.page.wait_for_timeout(200)
    z1, k1, h1 = s.js(zustand)
    assert z1 == z0 and k1 == k0, "Massstab sprang beim Tippen"
    assert float(h1.replace("px", "")) == pytest.approx(700 / z0, abs=0.02)
    assert s.js("() => document.activeElement && document.activeElement.id") == "xIn"
    s.page.set_viewport_size({"width": 800, "height": 1280})     # Tastatur zu
    s.page.wait_for_timeout(200)
    assert s.js(zustand)[0] == z0
    s.js("() => document.activeElement.blur()")
    s.page.set_viewport_size({"width": 1280, "height": 800})     # gedreht
    s.page.wait_for_timeout(200)
    z2, k2, h2 = s.js(zustand)
    assert z2 == pytest.approx(1.081, abs=0.001) and "gross" in k2 and "hoch" not in k2
    assert float(h2.replace("px", "")) == pytest.approx(800 / z2, abs=0.02)
    assert s.js("() => document.documentElement.scrollWidth") <= 1280
    s.page.set_viewport_size({"width": 400, "height": 800})      # geteilter Bildschirm: Handy
    s.page.wait_for_timeout(200)
    assert s.js(zustand)[:2] == [1, ""]
    assert s.fehler == []


def test_tipp_in_den_freien_platz(geraet, heute_stand):
    """Hochkant ist das Aufgabenfeld display:contents. Ein Tipp in den
    freien Platz des Kastens bringt wie am Handy die naechste Aufgabe, der
    Stern in der Kopfzeile nicht."""
    s = geraet(800, 1280, heute_stand())
    assert s.js(HELFER)
    s.js("""() => { openLevel(0); startLesson(); Lx.queue[0] = __aufgabe('mc'); Lx.i = 0; Lx.results = [];
                    showLessonTask(); }""")
    s.page.wait_for_timeout(300)
    s.js("""() => { const w = __aufgabe('mc').w; [...document.querySelectorAll('#lBody .opt')].find(o => o.textContent === w.bs).click(); }""")
    s.page.wait_for_function("document.querySelector('#lBody .weiterbox')")
    s.page.wait_for_timeout(1100)          # WEITER_NACH: erst dann horcht das Feld
    stern = s.page.locator("#lStern")
    if stern.is_visible():
        stern.click()
        s.page.wait_for_timeout(150)
        assert s.js("() => Lx.i") == 1 and s.js("() => !!document.querySelector('#lBody .weiterbox')"), \
            "der Stern hat weitergeblaettert"
    # freie Stelle: zwischen Aufgabe und Antworten, mitten im Kasten
    x, y = s.js("""() => { const p = document.querySelector('#lBody .prompt').getBoundingClientRect(),
                                  a = document.querySelector('#lBody .options').getBoundingClientRect();
                           return [p.left + p.width / 2, (p.bottom + a.top) / 2]; }""")
    assert s.js("([x, y]) => document.elementFromPoint(x, y).classList.contains('card')", [x, y])
    s.page.mouse.click(x, y)
    s.page.wait_for_function("!document.querySelector('#lBody .weiterbox')", timeout=3000)
    assert s.fehler == []


def test_geschichte_rand_blaettert_nicht(geraet, heute_stand):
    """Bei einer Geschichte horcht nur das Fragenfeld #rQ - wer im Text
    darueber liest oder nachschlaegt, soll nicht weiterblaettern. Der
    Horcher fuer den freien Platz (oben) gilt nur fuer die aufgeloesten
    Felder der Lektion; bis zur Pruefung am 30.10.2026 hing er auch am
    ganzen Geschichtenkasten, und ein Tipp auf dessen Rand holte die
    naechste Frage."""
    s = geraet(800, 1280, heute_stand())
    assert s.js("() => { openStory(0); stilleBitte(); return document.documentElement.classList.contains('hoch'); }")
    s.page.locator("#rQ #rOpts .opt").first.click()
    s.page.wait_for_function("document.querySelector('#rQ .weiterbox')")
    s.page.wait_for_timeout(1300)          # WEITER_NACH und sanftes Scrollen
    frage = "() => document.querySelector('#rQ .kicker').textContent"
    vorher = s.js(frage)
    x, y = s.js("""() => { const k = document.getElementById('rBody').getBoundingClientRect(),
                                  q = document.getElementById('rQ').getBoundingClientRect();
                           return [k.left + 6, Math.min(Math.max(q.top + 10, 10), innerHeight - 10)]; }""")
    assert s.js("([x, y]) => document.elementFromPoint(x, y).id", [x, y]) == "rBody"
    s.page.mouse.click(x, y)
    s.page.wait_for_timeout(400)
    assert s.js(frage) == vorher, "ein Tipp auf den Rand des Geschichtenkastens hat weitergeblaettert"
    assert s.js("() => !!document.querySelector('#rQ .weiterbox')")
    # Im Fragenfeld selbst geht es weiter wie bisher
    s.page.locator("#rQ .weiterbox .btn").click()
    s.page.wait_for_function("!document.querySelector('#rQ .weiterbox')", timeout=3000)
    assert s.js(frage) != vorher
    assert s.fehler == []


def test_rect_faktor_alte_webview(geraet, heute_stand):
    """Aeltere WebViews teilen getBoundingClientRect durch den zoom. Das
    wird hier nachgestellt: rectFaktor() muss es erkennen."""
    s = geraet(800, 1280, heute_stand())
    assert s.js("() => rectFaktor()") == 1          # Chrome >= 128
    alt = s.js("""() => {
      const echt = Element.prototype.getBoundingClientRect;
      Element.prototype.getBoundingClientRect = function(){
        const b = echt.call(this); return new DOMRect(b.x / GROSS, b.y / GROSS, b.width / GROSS, b.height / GROSS); };
      rectMitZoom = null; const f = rectFaktor();
      Element.prototype.getBoundingClientRect = echt; rectMitZoom = null;
      return f; }""")
    assert alt == pytest.approx(1.304, abs=0.001)
