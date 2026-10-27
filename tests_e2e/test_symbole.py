# -*- coding: utf-8 -*-
"""Gemalte Symbole statt Emojis (24.10.2026).

Ajdin am 23.10.2026: "die emojis die muessten mal anders gemacht werden".
Entschieden ist Symbol-Satz V1 aus web/symbole, komplett ("nimm v1
komplett"), das Profil als Figur. Ersetzt sind 📚 📖 🔁 (Reiter), 🛒 ⚙ 👤
(Kopf), 🪙 (Muenzen), ♥ (Leben), 🔊 (Hoeren, Vorlesen) und 🔒 (gesperrt).

Geprueft wird:
  - in allen Ansichten, in denen sie vorkamen, steht keines dieser Emojis
    mehr im sichtbaren Text, und jedes Symbolbild ist geladen;
  - die Bilder sind quadratisch (nie verzerrt), wachsen mit der Schrift
    und stehen mittig zum Text daneben;
  - Bildschirmleser: Schmuck ist alt="" und aria-hidden, Knoepfe ohne Text
    behalten ihren Namen, wo nur eine Zahl daneben steht, sagt das Bild,
    was gezaehlt wird;
  - die drei Reiter passen auch mit Bild in allen acht Sprachen in eine
    Zeile, bei 320 Punkten Breite;
  - der Kopf bleibt bei 360 Punkten bis 130 % Schrift in einer Zeile, und
    nichts darin ragt ueber den Rand, auch nicht in der Geschichte.

Gemessen wird an Kaesten, nicht an Pixeln einer Systemschrift - die Schrift
der App liegt in web/fonts. So laeuft alles auch in der CI unter Linux.
"""
import datetime

import pytest
from conftest import Seite

SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
WEG = ["📚", "📖", "🔁", "🛒", "🪙", "♥", "🔊", "🔒", "⚙", "👤"]


def _stand(**mehr):
    h = datetime.date.today()
    s = {"einstufung": {"tag": h.isoformat(), "wahl": "neu", "bis": ""},
         "tage": [(h - datetime.timedelta(days=i)).isoformat() for i in range(1, 6)],
         "muenzen_ges": 500, "muenzen_aus": 0}
    s.update(mehr)
    return s


def _kontext(browser, basis, schema="light", breite=390, hoehe=844):
    ctx = browser.new_context(viewport={"width": breite, "height": hoehe}, locale="de-DE",
                              service_workers="block", color_scheme=schema, reduced_motion="reduce")
    return ctx, Seite(ctx.new_page(), basis)


def _starten(seite, stand=None, sprache="de"):
    seite.starten(stand=stand or _stand(), sprache=sprache)
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)


# Alle sichtbaren Symbolbilder, mit Lage und Groesse
BILDER = """() => [...document.querySelectorAll('img.sym')].filter(i => i.getClientRects().length).map(i => {
  const r = i.getBoundingClientRect();
  return {src: i.getAttribute('src'), alt: i.getAttribute('alt'), aria: i.getAttribute('aria-hidden'),
          geladen: i.complete && i.naturalWidth > 0, b: r.width, h: r.height,
          schrift: parseFloat(getComputedStyle(i).fontSize)};
})"""

# (Name, JavaScript): die Ansichten, in denen eines der Emojis stand
ANSICHTEN = [
    ("start", "homeMode='words'; showHome(); scrollTo(0,0);"),
    ("geschichten", "homeMode='stories'; showHome();"),
    ("wiederholen", "homeMode='topf'; showHome();"),
    ("level", "const ws = CATEGORIES[0].words; ws.slice(0, 12).forEach(w => known.add(w.id));"
              " openLevel(0); document.getElementById('wordBox').open = true;"),
    ("lektion", "openLevel(0); startLesson();"),
    ("hoeren", "openLevel(0); startLesson(); const w = CATEGORIES[0].words.find(x => hoerbar(x.bs));"
               " Lx.queue = [{typ:'listen', w, pool: CATEGORIES[0].words}]; Lx.i = 0; Lx.total = 1; showLessonTask();"),
    ("laden", "Lx = null; showLaden();"),
    ("laden-kopf", "showLaden(); ladenReiter = 'kopf'; renderLaden();"),
    ("geschichte", "openStory(0); const w = [...document.querySelectorAll('#rBody .w')].find(x => hoerbar(x.textContent));"
                   " if(w) w.click();"),
]


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_keine_emojis_mehr_alle_bilder_geladen(browser, basis, schema):
    """In keiner Ansicht steht noch eines der ersetzten Emojis im sichtbaren
    Text (innerText - der Ersatztext eines Bildes zaehlt nicht dazu). Jedes
    sichtbare Symbolbild ist geladen und quadratisch."""
    ctx, seite = _kontext(browser, basis, schema)
    try:
        _starten(seite)
        funde, bilder = {}, {}
        for name, js in ANSICHTEN:
            seite.js("async () => { stilleBitte(); " + js + " await new Promise(r => setTimeout(r, 400)); stilleBitte(); }")
            seite.page.wait_for_function("() => [...document.querySelectorAll('img.sym')].every(i => i.complete)")
            text = seite.js("() => document.body.innerText")
            funde[name] = [e for e in WEG if e in text]
            bilder[name] = seite.js(BILDER)
        assert all(not f for f in funde.values()), funde
        for name, liste in bilder.items():
            assert liste, "%s: kein einziges Symbol zu sehen" % name
            for b in liste:
                assert b["src"].startswith("symbole/") and b["geladen"], (name, b)
                assert abs(b["b"] - b["h"]) < 0.5, ("verzerrt", name, b)
        # Wo welches Symbol steht
        srcs = {name: {b["src"] for b in liste} for name, liste in bilder.items()}
        assert {"symbole/lernpfad.webp", "symbole/geschichten.webp", "symbole/wiederholen.webp",
                "symbole/herz.webp", "symbole/muenze.webp", "symbole/laden.webp",
                "symbole/einstellungen.webp", "symbole/schloss.webp"} <= srcs["start"], srcs["start"]
        assert {"symbole/lautsprecher.webp", "symbole/schloss.webp"} <= srcs["level"], srcs["level"]
        assert {"symbole/herz.webp", "symbole/lautsprecher.webp"} <= srcs["lektion"], srcs["lektion"]
        assert "symbole/lautsprecher.webp" in srcs["hoeren"] and "symbole/lautsprecher.webp" in srcs["geschichte"]
        assert {"symbole/muenze.webp", "symbole/herz.webp"} <= srcs["laden"], srcs["laden"]
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


def test_ohne_leben_und_ergebnis(browser, basis):
    """Ohne Leben: Lektionsknopf, "Leben fuer Muenzen" und das grosse Herz
    auf dem Schirm "Keine Leben mehr". Danach der Ergebnisschirm einer
    Lektion mit der Statistik und einer geschafften Tagesaufgabe (+10 und
    die Muenze)."""
    ctx, seite = _kontext(browser, basis)
    try:
        jetzt = int(datetime.datetime.now().timestamp() * 1000)
        _starten(seite, _stand(leben={"anzahl": 0, "zeit": jetzt}))
        lage = seite.js("""() => { openLevel(0); lebenWege();
            const b = $('btnLesson'), c = $('lvCoin');
            return {knopf: b.innerText, knopfBild: !!b.querySelector('img.sym-herz'),
                    coin: c ? c.innerText.replace(/\\s+/g, ' ').trim() : null,
                    coinBilder: c ? [...c.querySelectorAll('img.sym')].map(i => i.className + '|' + i.getAttribute('alt')) : null}; }""")
        assert lage["knopfBild"] and lage["knopf"].strip() == "Keine Leben · warten", lage
        assert lage["coin"] == "für 100", lage
        assert lage["coinBilder"] == ["sym sym-herz|Leben", "sym sym-muenze|🪙"], lage

        _starten(seite, _stand(leben={"anzahl": 1, "zeit": jetzt}))
        seite.js("() => { openLevel(0); startLesson(); lessonOutOfLives(false); }")
        seite.page.wait_for_function("() => !!document.querySelector('#lBody .result-big.ohneleben')", timeout=8000)
        gross = seite.js("""() => { const e = document.querySelector('#lBody .result-big.ohneleben');
            const i = e.querySelector('img.sym-herz');
            return {text: e.innerText.trim(), alt: i && i.getAttribute('alt'), aria: i && i.getAttribute('aria-hidden')}; }""")
        assert gross == {"text": "0", "alt": "Leben", "aria": None}, gross

        _starten(seite)
        seite.js("() => { openLevel(0); startLesson(); }")
        seite.durchspielen("lBody", "Lx")
        seite.page.wait_for_function("() => !!document.querySelector('#lBody .stats')", timeout=8000)
        stat = seite.js("""() => { const s = [...document.querySelectorAll('#lBody .stat')].find(x => x.querySelector('img.sym-herz'));
            questFrisch = questsHeute().slice(0, 1); const box = document.createElement('div');
            box.innerHTML = questZeilen(); $('lBody').prepend(box);
            const m = box.querySelector('img.sym-muenze');
            return {stat: s ? s.innerText.replace(/\\s+/g, ' ').trim() : null,
                    statAlt: s ? s.querySelector('img.sym-herz').getAttribute('alt') : null,
                    quest: box.innerText, questAlt: m && m.getAttribute('alt')}; }""")
        assert stat["stat"] == "5 Leben" and stat["statAlt"] == "", stat
        assert "+10" in stat["quest"] and stat["questAlt"] == "🪙", stat
        assert not [e for e in WEG if e in stat["quest"]], stat
        assert seite.fehler == []
    finally:
        ctx.close()


def test_bildschirmleser(browser, basis):
    """Schmuck ist alt="" und aria-hidden. Knoepfe, die nur ein Bild
    tragen, behalten ihren Namen (title bzw. aria-label). Neben dem Herz
    steht nur eine Zahl - dort sagt das Bild "Leben"."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite)
        a = seite.js("""() => {
          const bild = e => { const i = e.querySelector('img.sym'); return i ? [i.getAttribute('alt'), i.getAttribute('aria-hidden')] : null; };
          return {
            laden: [$('btnShop').title, bild($('btnShop')), $('btnShop').innerText.trim()],
            zahnrad: [$('btnSettings').title, bild($('btnSettings')), $('btnSettings').innerText.trim()],
            reiter: [...document.querySelectorAll('#pfad .mode button')].map(b => [b.innerText.trim(), bild(b)]),
            muenzen: [bild($('muenzBar')), $('muenzBar').innerText.replace(/\\s+/g, ' ').trim()],
            leben: [bild($('livesKnopf')), $('livesKnopf').innerText.trim()],
            fuss: [...document.querySelectorAll('footer img.sym')].map(i => i.getAttribute('alt')),
            vorrat: symbolVorrat.length + ':' + symbolVorrat.every(i => i.complete && i.naturalWidth > 0),
          }; }""")
        assert a["laden"] == ["Laden", ["", "true"], ""], a
        assert a["zahnrad"] == ["Einstellungen", ["", "true"], ""], a
        assert a["reiter"] == [["Lernpfad", ["", "true"]], ["Geschichten", ["", "true"]],
                               ["Wiederholen", ["", "true"]]], a
        assert a["muenzen"] == [["", "true"], "500 KM"], a
        assert a["leben"] == [["Leben", None], "5"], a
        assert a["fuss"] == ["⚙"], a
        assert a["vorrat"] == "10:true", a
        # Laden: der Preisknopf zeigt "100" und heisst "100 🪙, Herz auffuellen"
        preise = seite.js("""() => { showLaden(); return [...document.querySelectorAll('#ladenWaren button[data-ware]')]
            .map(b => [b.innerText.trim(), b.getAttribute('aria-label')]); }""")
        assert preise and all(n.startswith(s + " 🪙, ") for s, n in preise), preise
        # Wort-Lautsprecher und grosser Hoerknopf: nur Bild, Name per aria-label
        seite.js("() => { openLevel(0); startLesson(); const w = CATEGORIES[0].words.find(x => hoerbar(x.bs));"
                 " Lx.queue = [{typ:'listen', w, pool: CATEGORIES[0].words}]; Lx.i = 0; Lx.total = 1; showLessonTask(); stilleBitte(); }")
        hoer = seite.js("() => { const b = document.querySelector('#lBody .bigplay'); return [b.getAttribute('aria-label'), b.innerText.trim()]; }")
        assert hoer[0] and hoer[1] == "", hoer
        assert seite.fehler == []
    finally:
        ctx.close()


# Mitte des Bildes gegen die Mitte der Schrift daneben. Im Text: .35 em ueber
# der Grundlinie (die Grundlinie zeigt ein Strich ohne Hoehe, der danach
# eingesetzt wird). In Flex-Zeilen: die Mitte des Textkastens daneben.
MITTE = """() => {
  const aus = {};
  const imText = (name, img) => {
    if(!img) return;
    const s = document.createElement('span');
    s.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
    img.after(s);
    const grund = s.getBoundingClientRect().bottom, em = parseFloat(getComputedStyle(img).fontSize);
    s.remove();
    const r = img.getBoundingClientRect();
    aus[name] = Math.round(((r.top + r.bottom) / 2 - (grund - .35 * em)) * 10) / 10;
  };
  const imFlex = (name, img, text) => {
    if(!img || !text) return;
    const a = img.getBoundingClientRect(), b = text.getBoundingClientRect();
    aus[name] = Math.round(((a.top + a.bottom) / 2 - (b.top + b.bottom) / 2) * 10) / 10;
  };
  const inKasten = (name, img, kasten) => imFlex(name, img, kasten);
  imText('reiter', document.querySelector('#modeWords img.sym'));
  imText('fuss', document.querySelector('footer img.sym'));
  imFlex('muenzen', document.querySelector('#muenzBar img.sym'), document.querySelector('#muenzBar b'));
  imFlex('leben', document.querySelector('#livesKnopf img.sym'), document.querySelector('#livesKnopf b'));
  inKasten('laden', document.querySelector('#btnShop img.sym'), $('btnShop'));
  inKasten('zahnrad', document.querySelector('#btnSettings img.sym'), $('btnSettings'));
  const schloss = document.querySelector('.node.locked .circle');
  if(schloss) inKasten('schloss', schloss.querySelector('img.sym'), schloss);
  return aus;
}"""

SCHRIFT = """(f) => { const els = [...document.querySelectorAll('body *')];
  const g = els.map(e => parseFloat(getComputedStyle(e).fontSize));
  els.forEach((e, i) => e.style.fontSize = (g[i] * f) + 'px'); }"""


@pytest.mark.parametrize("faktor", [1, 1.3, 2])
def test_mittig_und_waechst_mit_der_schrift(browser, basis, faktor):
    """Die Symbole stehen mittig zur Schrift (hoechstens 1,5 Punkte daneben),
    auch bei grosser Systemschrift, und wachsen mit ihr. In der Kopfleiste
    nur bis 30 px: deren Pillen sind fest 38 px hoch, das Bild bleibt darin."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite)
        vorher = {b["src"]: b["h"] for b in seite.js(BILDER)}
        if faktor != 1:
            # Wie die Schrift des Handys: jede Groesse mal faktor. Neu gebaut wird
            # nichts - .livesbar .herz hat feste 17 px, die das Handy selbst skaliert.
            seite.js(SCHRIFT, faktor)
        mitte = seite.js(MITTE)
        assert set(mitte) >= {"reiter", "fuss", "muenzen", "leben", "laden", "zahnrad", "schloss"}, mitte
        assert all(abs(v) <= 1.5 for v in mitte.values()), mitte
        nachher = {b["src"]: b["h"] for b in seite.js(BILDER)}
        deckel = {"symbole/muenze.webp": 30, "symbole/herz.webp": 30, "symbole/laden.webp": 30}
        for src in ("symbole/lernpfad.webp", "symbole/muenze.webp", "symbole/herz.webp", "symbole/laden.webp"):
            soll = min(vorher[src] * faktor, deckel.get(src, 1000))
            assert abs(nachher[src] - soll) < 0.6, (src, vorher[src], nachher[src], soll)
        drin = seite.js("""() => ['btnShop', 'btnSettings', 'muenzBar', 'livesBar'].map(id => {
            const k = $(id).getBoundingClientRect(), i = $(id).querySelector('img.sym').getBoundingClientRect();
            return [id, i.top >= k.top && i.bottom <= k.bottom]; })""")
        assert all(ok for _, ok in drin), drin
    finally:
        ctx.close()


# Hoehe des Kopfes, enger Modus, und wie weit er und die Seite reichen
KOPF = """() => { const h = document.querySelector('header'), r = h.getBoundingClientRect(),
    z = document.getElementById('btnBack');
  const zeilen = x => { const g = document.createRange(); g.selectNodeContents(x);
    return new Set([...g.getClientRects()].map(q => Math.round(q.top))).size; };
  return {hoehe: r.height, eng: h.classList.contains('eng'), rechts: r.right,
          zurueck: z.offsetParent ? z.getBoundingClientRect().right : null,
          zurueckZeilen: z.offsetParent ? zeilen(z) : null,
          inhalt: Math.max(...[...h.querySelectorAll('.livesbar, .muenzbar, .hbtns .back')]
                            .filter(e => e.offsetParent).map(e => e.getBoundingClientRect().right)),
          seite: document.documentElement.scrollWidth, breit: innerWidth}; }"""


@pytest.mark.parametrize("faktor", [1, 1.15, 1.3])
def test_kopf_bei_360_und_grosser_schrift(browser, basis, faktor):
    """Pruefbefund vom 24.10.2026. Die gemalten Symbole sind breiter als
    die Emojis waren (vor allem das Herz), der Kopf braucht deshalb 11 bis
    17 Punkte mehr, bevor die Muenzen in die zweite Zeile rutschen
    (header.eng, kopfEng). Bei 360 Punkten (Samsung S21) und einer
    dreistelligen Muenzzahl reicht es bis 130 % Schrift fuer eine Zeile -
    das haelt dieser Test fest.

    In der Geschichte kommt die Zuruecktaste dazu (nur im Browser, das
    Handy hat seine eigene). kopfEng() lief bis dahin nur, wenn die Leben
    neu gezeichnet wurden, nicht wenn die Taste erschien: bei 130 % ragte
    sie 52 Punkte ueber den Rand, und die Seite liess sich seitlich
    schieben (vor den Symbolen 45). Jetzt misst setzeZurueck() neu; im
    engen Kopf bleibt "← Geschichten" dabei in einer Zeile."""
    ctx, seite = _kontext(browser, basis, breite=360, hoehe=740)
    try:
        _starten(seite)
        if faktor != 1:
            seite.js(SCHRIFT, faktor)
        # Das Handy kennt die Schrift schon beim Start; hier kommt sie danach,
        # also wie bei einer Drehung des Geraets neu messen.
        seite.js("() => window.dispatchEvent(new Event('resize'))")
        k = seite.js(KOPF)
        assert not k["eng"] and k["hoehe"] <= 40, k
        assert k["inhalt"] <= k["rechts"] + 0.5 and k["seite"] <= k["breit"], k
        seite.js("() => openStory(0)")
        k = seite.js(KOPF)
        assert k["zurueck"] is not None and k["zurueckZeilen"] == 1, k
        assert k["zurueck"] <= k["rechts"] + 0.5 and k["inhalt"] <= k["rechts"] + 0.5, k
        assert k["seite"] <= k["breit"], k
        assert seite.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_reiter_in_einer_zeile(browser, basis, sprache):
    """Mit Bild statt Emoji passen die drei Reiter auch bei 320 Punkten in
    eine Zeile, in jeder Sprache. Nichts ragt ueber den Rand."""
    ctx, seite = _kontext(browser, basis, breite=320, hoehe=640)
    try:
        _starten(seite, sprache=sprache)
        r = seite.js("""() => { const bs = [...document.querySelectorAll('#pfad .mode button')].filter(b => !b.hidden);
            return {zeilen: new Set(bs.map(b => Math.round(b.getBoundingClientRect().top))).size,
                    ueber: bs.map(b => b.scrollWidth - b.clientWidth), breit: document.documentElement.scrollWidth,
                    text: bs.map(b => b.innerText.trim())}; }""")
        assert r["zeilen"] == 1 and max(r["ueber"]) <= 0 and r["breit"] <= 320, r
        assert not [e for e in WEG if e in "".join(r["text"])], r
        assert seite.fehler == []
    finally:
        ctx.close()
