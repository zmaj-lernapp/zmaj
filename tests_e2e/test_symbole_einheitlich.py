# -*- coding: utf-8 -*-
"""Symbole einheitlich auf Android und iPhone (Offen-Liste 5, 14.11.2026).

Ajdin im iPhone-Test: "es hat noch die iphone bilder zb das überspringen
zeichen das muss einheitlich sein", und nach dem Kauf: alles frei, "nur das
das herz nicht gold ist". Gemalt mit Gemini wie Symbol-Satz V1 und von
Ajdin abgenommen ("passt").

Geprueft wird hier im Browser:
  - das goldene Herz: mit der Vollversion in der Kopfleiste, im
    Fragenkasten und in der Statistik nach der Lektion, ohne sie das rote;
    unbegrenzt ohne Kauf (?alle=1) bleibt es rot.
  - die gemalten Bilder statt 🏁 ⭐ 💙 ✨ ✉: Level-Test, Bewertungskarte,
    "Danke!" nach dem Vorschlag, Funken an der goldenen Flamme, E-Mail im
    Profil - in allen acht Sprachen, geladen, als Schmuck (alt="").
  - die selbst gezeichneten Zeichen statt ⏭ ⏸ ⏹ ✕: Ueberspringen, Pause,
    Stopp und die drei Abbrechen-Knoepfe, in allen acht Sprachen, hell und
    dunkel, bei 360 Punkten im Knopf und in einer Zeile.
  - seit 15.11.2026 (Offen-Liste 5a) gemaltes play statt ▶ (Weitermachen,
    "Lektion starten"; "Weiterlesen" in test_mitlesen.py) und gemaltes
    Konfetti statt 🎉 (Ende von Lektion, Test, Wiederholungsrunde und
    Geschichte), in allen acht Sprachen.
"""
import datetime
import os
import re

import app_quelle
import pytest
from conftest import WURZEL, Seite

# Fuer die goldene Flamme (365 Tage) muss die Uhr spaeter stehen: eine Serie
# reicht nie vor APP_START zurueck (wie in test_flamme.py). Aus der ganzen
# App (app_quelle): seit 1.5 kann APP_START in web/js stehen.
APP_START = datetime.date.fromisoformat(re.search(
    r"const APP_START = '(\d{4}-\d{2}-\d{2})';", app_quelle.lesen(os.path.join(WURZEL, "web"))).group(1))
SPAETER = APP_START + datetime.timedelta(days=400)


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


# Das Herz an einer Stelle: welches Bild, ob geladen, was daneben steht
HERZ = """(sel) => { const e = document.querySelector(sel); if(!e) return null;
  const i = e.querySelector('img.sym');
  return {bild: i ? i.getAttribute('src') : null, alt: i ? i.getAttribute('alt') : null,
          geladen: !!i && i.complete && i.naturalWidth > 0, text: e.innerText.trim()}; }"""


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_goldenes_herz_mit_vollversion(browser, basis, schema):
    """Ohne Vollversion das rote Herz mit Zahl. Mit ihr das goldene mit ∞ -
    in der Kopfleiste, im Fragenkasten der Lektion und in der Statistik
    danach. Der Name fuer den Bildschirmleser bleibt "Leben". Endet die
    Vollversion, ist es wieder rot."""
    ctx, seite = _kontext(browser, basis, schema)
    try:
        _starten(seite)
        rot = seite.js(HERZ, "#livesKnopf")
        assert rot == {"bild": "symbole/herz.webp", "alt": "Leben", "geladen": True, "text": "5"}, rot

        seite.js("() => { vollversionMerken(true); renderLives(); }")
        seite.page.wait_for_function("() => [...document.querySelectorAll('img.sym')].every(i => i.complete)")
        gold = seite.js(HERZ, "#livesKnopf")
        assert gold == {"bild": "symbole/herzgold.webp", "alt": "Leben", "geladen": True, "text": "∞"}, gold
        assert seite.js("() => $('livesBar').classList.contains('premium')")

        seite.js("() => { openLevel(0); startLesson(); stilleBitte(); }")
        kasten = seite.js(HERZ, "#lHerz")
        assert kasten["bild"] == "symbole/herzgold.webp" and kasten["text"] == "∞" and kasten["geladen"], kasten
        seite.durchspielen("lBody", "Lx")
        seite.page.wait_for_function("() => !!document.querySelector('#lBody .stats')", timeout=8000)
        stat = seite.js("""() => { const s = [...document.querySelectorAll('#lBody .stat')].find(x => x.querySelector('img.sym'));
            const i = [...document.querySelectorAll('#lBody .stat img.sym')].find(x => /herz/.test(x.src));
            return {bild: i && i.getAttribute('src'), text: i && i.closest('.stat').innerText.replace(/\\s+/g, ' ').trim()}; }""")
        assert stat == {"bild": "symbole/herzgold.webp", "text": "∞ Leben"}, stat

        seite.js("() => { stilleBitte(); vollversionMerken(false); renderLives(); homeMode = 'words'; showHome(); }")
        wieder = seite.js(HERZ, "#livesKnopf")
        assert wieder["bild"] == "symbole/herz.webp" and wieder["text"] == "5", wieder
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


def test_unbegrenzt_ohne_kauf_bleibt_rot(browser, basis):
    """?alle=1 (Testmodus) macht die Leben unbegrenzt, gekauft ist aber
    nichts: das Herz bleibt rot, mit ∞."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite)
        seite.page.goto(basis + "/app/index.html?alle=1")
        seite.bereit()
        seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
        assert seite.js("() => ALLE_FREI && !premium && unlimited()")
        herz = seite.js(HERZ, "#livesKnopf")
        assert herz["bild"] == "symbole/herz.webp" and herz["text"] == "∞", herz
        assert seite.fehler == []
    finally:
        ctx.close()


SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
GEMALT_WEG = ["🏁", "⭐", "💙", "✨", "✉"]

# Ein Knopf oder Kasten: seine Symbolbilder (Name, alt, aria-hidden, geladen)
# und sein Text
BILDER_IN = """(sel) => { const e = document.querySelector(sel); if(!e) return null;
  return {bilder: [...e.querySelectorAll('img.sym')].map(i => [i.getAttribute('src'), i.getAttribute('alt'),
                    i.getAttribute('aria-hidden'), i.complete && i.naturalWidth > 0]),
          text: e.innerText.replace(/\\s+/g, ' ').trim()}; }"""


def _bild(name):
    return ["symbole/%s.webp" % name, "", "true", True]


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_gemalt_statt_emoji(browser, basis, sprache):
    """Level-Test, "Zmaj bewerten", "Danke!" und die E-Mail im Profil tragen
    das gemalte Bild, der Text daneben kein Emoji mehr - in jeder Sprache."""
    ctx, seite = _kontext(browser, basis)
    try:
        _starten(seite, sprache=sprache)
        # wie innerText mit zusammengefassten Leerraeumen (fr: "Merci" und "!"
        # mit geschuetztem Leerzeichen dazwischen)
        t = lambda k: " ".join(seite.js("k => t(k)", k).split())  # noqa: E731
        # Level-Test (frei, weil alle Woerter des Levels gewusst sind)
        seite.js("() => { CATEGORIES[0].words.forEach(w => known.add(w.id)); openLevel(0); }")
        seite.page.wait_for_function("() => [...document.querySelectorAll('#btnTest img.sym')].every(i => i.complete)")
        test = seite.js(BILDER_IN, "#btnTest")
        assert test == {"bilder": [_bild("ziel")], "text": t("level.test")}, test

        # Die Bewertungskarte
        seite.js("() => { homeMode = 'words'; showHome(); zeigeBewertung(); }")
        seite.page.wait_for_function("() => [...document.querySelectorAll('#bwJa img.sym')].every(i => i.complete)")
        ja = seite.js(BILDER_IN, "#bwJa")
        assert ja == {"bilder": [_bild("stern")], "text": t("bew.bewerten")}, ja
        seite.page.click("#bwVor")

        # Vorschlag ohne Formular: das Mailprogramm (hier nachgestellt), davor "Danke!"
        seite.js("() => { feedbackPerMail = (text, notiz) => { notiz.textContent = 'MAIL'; }; }")
        seite.page.fill("#bwText", "Probe")
        seite.page.click("#bwSenden")
        seite.page.wait_for_function("() => !!document.querySelector('#bwNote img.sym-herzblau')")
        seite.page.wait_for_function("() => document.querySelector('#bwNote img.sym-herzblau').complete")
        note = seite.js(BILDER_IN, "#bwNote")
        assert note == {"bilder": [_bild("herzblau")], "text": t("bew.danke") + " MAIL"}, note
        seite.page.click("#bwZu")

        # Profil mit Konto: der Brief vor der Adresse
        seite.js("() => { kontoMail = 'ich@probe.example'; showKonto(); }")
        seite.page.wait_for_function("() => [...document.querySelectorAll('#setProfilMail img.sym')].every(i => i.complete)")
        mail = seite.js(BILDER_IN, "#setProfilMail")
        assert mail == {"bilder": [_bild("brief")], "text": "ich@probe.example"}, mail

        for k in ("level.test", "bew.bewerten", "bew.danke"):
            assert not [e for e in GEMALT_WEG if e in t(k)], (k, t(k))
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()


def test_funken_an_der_goldenen_flamme(browser, basis):
    """Ab 365 Tagen funkeln drei gemalte Funken um die Flamme, oben und in
    der Statistik - geladen, so gross wie die Schrift des Funkens (vorher
    das Zeichen ✨), innerhalb des Kastens mit aria-hidden."""
    ctx, seite = _kontext(browser, basis)
    try:
        seite.page.clock.set_fixed_time(datetime.datetime.combine(SPAETER, datetime.time(12, 0)))
        _starten(seite, {"einstufung": {"tag": SPAETER.isoformat(), "wahl": "neu", "bis": ""},
                         "tage": [(SPAETER - datetime.timedelta(days=i)).isoformat() for i in range(0, 365)]})
        seite.page.wait_for_function("() => [...document.querySelectorAll('.funke img')].every(i => i.complete)")
        f = seite.js("""() => [...document.querySelectorAll('.seriezahl .funke')].map(x => {
            const i = x.querySelector('img.sym'), r = i.getBoundingClientRect();
            return {bild: i.getAttribute('src'), geladen: i.naturalWidth > 0, alt: i.getAttribute('alt'),
                    text: x.textContent, b: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10,
                    schrift: parseFloat(getComputedStyle(x).fontSize),
                    versteckt: !!x.closest('[aria-hidden="true"]')}; })""")
        assert len(f) == 3, f
        for x in f:
            assert x["bild"] == "symbole/funken.webp" and x["geladen"] and x["alt"] == "" and x["text"] == "", x
            assert abs(x["b"] - x["schrift"]) < 0.6 and x["b"] == x["h"] and x["versteckt"], x
        assert seite.js("() => document.getElementById('serieFlamme').classList.contains('stufe-gold')")
        statistik = seite.js("() => { const d = document.createElement('div'); d.innerHTML = flammeHtml();"
                             " return [...d.querySelectorAll('.funke img.sym')].map(i => i.getAttribute('src')); }")
        assert statistik == ["symbole/funken.webp"] * 3, statistik
        assert seite.fehler == []
    finally:
        ctx.close()



GEZEICHNET_WEG = ["⏭", "⏸", "⏹", "✕"]

# Ein Knopf: seine gezeichneten Zeichen, sein Name, sein Text, und ob alles
# in ihm liegt und in einer Zeile steht. Farbe: das Zeichen nimmt die Schrift-
# farbe des Knopfs (currentColor).
KNOPF = """(sel) => { const k = document.querySelector(sel); if(!k) return null;
  const r = k.getBoundingClientRect(), s = getComputedStyle(k);
  const zeichen = [...k.querySelectorAll('svg.zei')].map(z => { const q = z.getBoundingClientRect(), f = getComputedStyle(z);
    return {name: [...z.classList].find(c => c.startsWith('zei-')), aria: z.getAttribute('aria-hidden'),
            b: Math.round(q.width * 10) / 10, h: Math.round(q.height * 10) / 10,
            schrift: parseFloat(f.fontSize), farbe: f.fill === s.color || f.stroke === s.color,
            drin: q.left >= r.left - 0.5 && q.right <= r.right + 0.5 && q.top >= r.top - 0.5 && q.bottom <= r.bottom + 0.5}; });
  // Zeilen nur aus dem Text, und wie weit das Zeichen neben der Mitte der
  // Textzeile sitzt, in der es steht (null: es steht in keiner, allein)
  const rects = [...k.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim()).flatMap(n => {
    const g = document.createRange(); g.selectNodeContents(n); return [...g.getClientRects()].filter(q => q.width > 0); });
  const zeilen = new Set(rects.map(q => Math.round(q.top))).size;
  zeichen.forEach((x, j) => { const q = k.querySelectorAll('svg.zei')[j].getBoundingClientRect(), m = (q.top + q.bottom) / 2;
    const z = rects.find(r => m >= r.top && m <= r.bottom);
    x.mitte = z ? Math.round(Math.abs(m - (z.top + z.bottom) / 2) * 10) / 10 : null; });
  return {zeichen, text: k.innerText.replace(/\\s+/g, ' ').trim(), label: k.getAttribute('aria-label'),
          zeilen, ueber: k.scrollWidth - k.clientWidth, sichtbar: !!k.getClientRects().length}; }"""


def _zeichen(k, name, mit_wort=True):
    """Genau ein Zeichen, Schmuck, so gross wie die Schrift, im Knopf, in seiner
    Farbe - und (mit_wort) in der Zeile eines Wortes, mittig dazu, nie allein."""
    assert len(k["zeichen"]) == 1, k
    z = k["zeichen"][0]
    assert z["name"] == "zei-" + name and z["aria"] == "true", k
    assert abs(z["b"] - z["schrift"]) < 0.6 and z["b"] == z["h"] and z["drin"] and z["farbe"], k
    if mit_wort:
        assert z["mitte"] is not None and z["mitte"] <= 1.5, k


@pytest.mark.parametrize("schema", ["light", "dark"])
@pytest.mark.parametrize("sprache", SPRACHEN)
def test_gezeichnete_zeichen(browser, basis, sprache, schema):
    """Ueberspringen, Pause, Stopp und Abbrechen tragen das gezeichnete
    Zeichen in der Schriftfarbe statt ⏭ ⏸ ⏹ ✕. Der Text daneben (bzw. das
    aria-label des Stopp-Knopfs) nennt den Knopf. Bei 360 Punkten passt alles
    in den Knopf, die Abbrechen-Knoepfe in eine Zeile; das Zeichen steht nie
    allein in einer Zeile (geschuetztes Leerzeichen), nur am schmalen
    Pause-Knopf neben Stopp darf es wie vorher das Emoji ueber dem Wort stehen."""
    ctx, seite = _kontext(browser, basis, schema, breite=360, hoehe=740)
    try:
        _starten(seite, sprache=sprache)
        t = lambda k: " ".join(seite.js("k => t(k)", k).split())  # noqa: E731

        # Lektion: "Lektion abbrechen" und Ueberspringen (Hoeraufgabe)
        seite.js("() => { openLevel(0); startLesson(); const w = CATEGORIES[0].words.find(x => hoerbar(x.bs));"
                 " Lx.queue = [{typ:'listen', w, pool: CATEGORIES[0].words}]; Lx.i = 0; Lx.total = 1; showLessonTask(); stilleBitte(); }")
        quit_ = seite.js(KNOPF, "#lQuit")
        _zeichen(quit_, "zu")
        assert quit_["text"] == t("lektion.abbrechen") and quit_["zeilen"] == 1 and quit_["ueber"] <= 0, quit_
        skip = seite.js(KNOPF, "#xSkip")
        _zeichen(skip, "weiter")
        assert skip["text"] == t("task.hoeren_skip") and skip["ueber"] <= 0, skip

        # Level-Test und Einstufung: "Test abbrechen", "Test beenden"
        seite.js("() => { stilleBitte(); CATEGORIES[0].words.forEach(w => known.add(w.id)); openLevel(0); startTest(); stilleBitte(); }")
        quit_ = seite.js(KNOPF, "#tQuit")
        _zeichen(quit_, "zu")
        assert quit_["text"] == t("test.abbrechen") and quit_["zeilen"] == 1 and quit_["ueber"] <= 0, quit_
        seite.js("() => { stilleBitte(); baueEinstufung('etwas'); einstufungStarten(); stilleBitte(); }")
        quit_ = seite.js(KNOPF, "#eQuit")
        _zeichen(quit_, "zu")
        assert quit_["text"] == t("einst.abbrechen") and quit_["zeilen"] == 1 and quit_["ueber"] <= 0, quit_

        # Geschichte: Vorlesen -> Pause, daneben Stopp nur mit Zeichen
        seite.js("() => { stilleBitte(); Ex = null; homeMode = 'stories'; openStory(0); }")
        seite.js("() => { const k = document.getElementById('rListen'); k.innerHTML = zeichen('pause') + ' ' + esc(t('gesch.pause'));"
                 " document.getElementById('rStop').hidden = false; }")
        pause = seite.js(KNOPF, "#rListen")
        # Neben Stopp ist der Knopf bei 360 Punkten schmal: das Zeichen darf wie
        # vorher das Emoji ueber dem Wort stehen, nichts ragt heraus
        _zeichen(pause, "pause", mit_wort=False)
        assert pause["text"] == t("gesch.pause") and pause["zeilen"] == 1 and pause["ueber"] <= 0, pause
        stopp = seite.js(KNOPF, "#rStop")
        _zeichen(stopp, "stopp", mit_wort=False)
        assert stopp["text"] == "" and stopp["label"] == t("gesch.stopp") and stopp["ueber"] <= 0, stopp

        for k in ("gesch.pause", "gesch.stopp", "lektion.abbrechen", "test.abbrechen", "einst.abbrechen",
                  "task.hoeren_skip", "task.sprechen_skip", "task.kacheln_skip"):
            assert not [e for e in GEZEICHNET_WEG if e in t(k)], (k, t(k))
        text = seite.js("() => document.body.innerText")
        assert not [e for e in GEZEICHNET_WEG if e in text]
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()



# 🎉 und ▶ gemalt (Offen-Liste 5a, 15.11.2026). Ajdin: "Male sie", abgenommen
# mit "Passt". play steht vor dem Wort, konfetti nach dem Satz (wie vorher das
# Emoji), mit geschuetztem Leerzeichen am letzten Wort.
GEMALT_WEG_5A = ["🎉", "▶"]

# Wie BILDER_IN, dazu: steht jedes Bild in der Zeile eines Wortes (seine Mitte
# innerhalb der Hoehe einer Textzeile), oder allein in einer eigenen Zeile?
BILDER_ZEILE = """(sel) => { const e = document.querySelector(sel); if(!e) return null;
  const rects = []; const w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
  for(let n = w.nextNode(); n; n = w.nextNode()){ if(!n.textContent.trim()) continue;
    const g = document.createRange(); g.selectNodeContents(n); rects.push(...[...g.getClientRects()].filter(q => q.width > 0)); }
  return {bilder: [...e.querySelectorAll('img.sym')].map(i => [i.getAttribute('src'), i.getAttribute('alt'),
                    i.getAttribute('aria-hidden'), i.complete && i.naturalWidth > 0]),
          inZeile: [...e.querySelectorAll('img.sym')].every(i => { const q = i.getBoundingClientRect(), m = (q.top + q.bottom) / 2;
                    return rects.some(r => m >= r.top && m <= r.bottom); }),
          text: e.innerText.replace(/\\s+/g, ' ').trim()}; }"""


def _geladen(seite, sel):
    seite.page.wait_for_function(
        "(s) => { const i = [...document.querySelectorAll(s + ' img.sym')]; return i.length > 0 && i.every(x => x.complete); }",
        arg=sel, timeout=8000)
    return seite.js(BILDER_ZEILE, sel)


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_konfetti_und_play_gemalt(browser, basis, sprache):
    """Weitermachen, "Lektion starten" und "Weiterlesen" tragen das gemalte
    play vor dem Wort (war ▶), die Erfolgssaetze nach Lektion, Test,
    Wiederholungsrunde und Geschichte das gemalte Konfetti danach (war 🎉) -
    in jeder Sprache, geladen, als Schmuck, bei 360 Punkten in der Zeile des
    Wortes. Die Texte selbst tragen keines der Zeichen mehr."""
    ctx, seite = _kontext(browser, basis, breite=360, hoehe=740)
    try:
        _starten(seite, sprache=sprache)
        t = lambda k, v=None: " ".join(seite.js("([k, v]) => t(k, v || undefined)", [k, v]).split())  # noqa: E731

        # Startseite: Weitermachen
        seite.js("() => { homeMode = 'words'; showHome(); }")
        k = _geladen(seite, "#weiterKnopf")
        name = " ".join(seite.js("() => CATEGORIES[firstOpen()].label").split())
        assert k == {"bilder": [_bild("play")], "inZeile": True, "text": t("btn.weitermachen") + " · " + name}, k

        # Level: Lektion starten
        seite.js("() => openLevel(0)")
        k = _geladen(seite, "#btnLesson")
        assert k == {"bilder": [_bild("play")], "inZeile": True, "text": t("level.lektion")}, k

        # Ende der Lektion
        seite.js("() => { startLesson(); stilleBitte(); }")
        seite.durchspielen("lBody", "Lx")
        k = _geladen(seite, "#lBody .ergebnis-titel")
        assert k == {"bilder": [_bild("konfetti")], "inZeile": True, "text": t("lektion.geschafft")}, k

        # Bestandener Level-Test
        seite.js("() => { stilleBitte(); CATEGORIES[0].words.forEach(w => known.add(w.id)); openLevel(0); startTest();"
                 " stilleBitte(); Tx.i = Tx.qs.length; Tx.right = Tx.qs.length; showTestResult(); }")
        k = _geladen(seite, "#tBody .feedback.ok")
        assert k["bilder"] == [_bild("konfetti")] and k["inZeile"], k
        assert k["text"] in (t("test.bestanden"), t("test.sektion_fertig")), k

        # Ende einer Wiederholungsrunde (wie TOPF_ENDE in test_flamme.py)
        seite.js("""() => { stilleBitte(); showView('levelView');
          for(const [id, an] of [['levelHome', 'none'], ['test', 'none'], ['lesson', 'block']]) document.getElementById(id).style.display = an;
          Lx = {queue: [], i: 0, results: [], right: 0, total: 0, skipped: 0, newWords: new Set(), retried: new Set(),
                topf: true, quelle: 'topf'};
          topfEnde(); }""")
        k = _geladen(seite, "#lBody .ergebnis-titel")
        assert k == {"bilder": [_bild("konfetti")], "inZeile": True, "text": t("topf.fertig")}, k

        # Alle Fragen einer Geschichte richtig
        seite.js("() => { stilleBitte(); homeMode = 'stories'; openStory(0); stilleBitte();"
                 " const s = STORIES[0]; showStoryQ(s, s.fragen.length, s.fragen.length); }")
        k = _geladen(seite, "#rQ .feedback.ok")
        n = seite.js("() => STORIES[0].fragen.length")
        erwartet = " ".join((seite.js("(n) => t('gesch.ergebnis', {r: n, n})", n) + seite.js("() => t('gesch.geschafft')")).split())
        assert k == {"bilder": [_bild("konfetti")], "inZeile": True, "text": erwartet}, k

        for key in ("btn.weitermachen", "level.lektion", "gesch.weiterlesen", "lektion.geschafft", "test.bestanden",
                    "test.sektion_fertig", "topf.fertig", "gesch.geschafft"):
            assert not [e for e in GEMALT_WEG_5A if e in t(key)], (key, t(key))
        assert seite.fehler == [] and seite.fremd == []
    finally:
        ctx.close()
