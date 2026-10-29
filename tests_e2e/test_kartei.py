# -*- coding: utf-8 -*-
"""Lernkartei: alte Woerter kommen in wachsenden Abstaenden wieder (v110).

Ajdins Entscheidung vom 28.10.2026 (Release\\Wiederholung_Vorschlag.md,
Verfahren A "feste Abstaende"). Geprueft wird im echten Browser:
  - die Stufen 1, 3, 7, 14, 30, 90, 180 Tage: richtig eine weiter (wenn das
    Wort faellig war), falsch zwei zurueck, nie unter die erste; das
    Beispiel aus dem Vorschlag Tag fuer Tag; die Wiederholung am Ende der
    Lektion und die Einstufung zaehlen nicht, der Level-Test schon;
  - ein neu gelerntes Wort ist morgen faellig;
  - der Umzug: gewusste Woerter ohne Termin bekommen einen, verteilt auf die
    naechsten Wochen, die aeltesten Level zuerst, nie am ersten Tag;
  - die Lektion: bis zu 3 der 10 Wortplaetze mit "Wiederholung: <Level>",
    gleich viele neue Woerter wie ohne;
  - der dritte Kasten "Heute faellig" im Reiter Wiederholen, gebaut wie
    "Markiert", die alten Kaesten unveraendert, leer und ohne Leben;
  - die Runde: Leben, Fehler-Topf, Serie, Tagesaufgaben, Ergebnis;
  - die Tagesgrenze von 30, der Rest kommt an den naechsten Tagen; zuerst,
    was gemessen am Abstand seiner Stufe am weitesten ueber der Zeit ist;
  - der Kartei-Tag beginnt um 4 Uhr, nicht um Mitternacht;
  - Geraetespeicher, Sicherungsdatei (alte Dateien ohne das Feld, kaputte
    Eintraege), umbenannte Woerter, Cloud-Abgleich, Konto leeren, Groesse.
"""
import datetime
import json

import pytest
from conftest import Seite

ABSTAENDE = [1, 3, 7, 14, 30, 90, 180]
APP_START = datetime.date(2026, 8, 1)

# Echte, verschiedene Wort-Kennungen in Lernpfad-Reihenfolge (wie test_stern.py)
WOERTER = """(n) => [...new Map(CATEGORIES.flatMap(c => c.words).map(w => [w.id, w])).keys()].slice(0, n)"""

# Die laufende Aufgabe der Lektion oder Runde beantworten, richtig oder falsch
# (Muster aus test_stern.py: ANTWORTEN, nur Woerter).
ANTWORT = r"""async (richtig) => {
  const q = Lx.queue[Lx.i], body = document.getElementById('lBody'), i = Lx.i;
  const ende = Date.now() + 5000;
  while(body.dataset.i !== String(i) && Date.now() < ende) await new Promise(r => setTimeout(r, 15));
  if(q.typ === 'type'){
    body.querySelector('#xIn').value = richtig ? q.w.bs.split(' / ')[0] : 'qqqq';
    body.querySelector('#xCheck').click();
  } else {
    const soll = q.typ === 'mcrev' ? q.w.de : q.w.bs;
    const opts = [...body.querySelectorAll('.opt')];
    (richtig ? opts.find(o => o.textContent === soll) : opts.find(o => o.textContent !== soll)).click();
  }
  while(Lx.i === i && Date.now() < ende) await new Promise(r => setTimeout(r, 15));
  const k = body.querySelector('.weiterbox .btn');
  if(k){ k.click(); await new Promise(r => setTimeout(r, 30)); }
  return q.w.id;
}"""

KASTEN = """(id) => {
  const b = document.getElementById(id);
  const txt = s => { const e = b.querySelector(s); return e ? e.textContent.trim() : null; };
  const bau = box => [...box.children].map(e => { const s = getComputedStyle(e), r = e.getBoundingClientRect();
    return [e.tagName, e.className, +r.height.toFixed(2), s.fontSize, s.fontWeight, s.color,
            s.marginTop, s.marginBottom, s.textAlign]; });
  const los = b.querySelector('.btn.know');
  return {klasse: b.className, sichtbar: b.offsetParent !== null, titel: txt('h2'), desc: txt('.desc'),
          zahl: txt('.topfzahl'), wort: txt('.topfwort'), leer: txt('.topfleer'), note: txt('.note'),
          knopf: los && los.textContent, knopfId: los && los.id,
          beschrieben: los && los.getAttribute('aria-describedby'), bau: bau(b),
          h: +b.getBoundingClientRect().height.toFixed(2)};
}"""


def _tag(d):
    """karteiTag() in Python: Tage seit APP_START."""
    return (d - APP_START).days


def _kartei_datum():
    """Das Datum des Kartei-Tags: er beginnt um 4 Uhr (KARTEI_TAG_BEGINN)."""
    jetzt = datetime.datetime.now()
    return jetzt.date() - datetime.timedelta(days=1 if jetzt.hour < 4 else 0)


def _heute():
    return _tag(_kartei_datum())


def _uhr(seite, tag, stunde=10, minute=0):
    seite.page.clock.set_fixed_time(datetime.datetime.combine(tag, datetime.time(stunde, minute)))


def _ids(seite, heute_stand, n):
    seite.starten(stand=heute_stand())
    return seite.js(WOERTER, n)


def _gespeichert(seite):
    return seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand')).kartei")


# ---------------------------------------------------------------------------
# Die Stufen
# ---------------------------------------------------------------------------

def test_stufen_richtig_falsch_und_nur_faellig_hoch(seite, heute_stand):
    seite.starten(stand=heute_stand())
    z = seite.js("""() => {
      const w = CATEGORIES[0].words[0], h = karteiTag(), r = {};
      known = new Set([w.id]); kartei = {tag: 0, n: 0, w: {}};
      const merk = name => { r[name] = kartei.w[w.id].slice(); };
      karteiAntwort({typ: 'mc', w}, true); merk('neu');
      karteiAntwort({typ: 'mcrev', w}, true); merk('gleicherTag');
      kartei.w[w.id] = [0, h, h - 1]; karteiAntwort({typ: 'mc', w}, true); merk('faelligRichtig');
      kartei.w[w.id] = [4, h - 3, h - 33]; karteiAntwort({typ: 'type', w}, false); merk('faelligFalsch');
      kartei.w[w.id] = [1, h + 2, h - 1]; karteiAntwort({typ: 'mc', w}, false); merk('frueherFalsch');
      kartei.w[w.id] = [0, h, h - 1]; karteiAntwort({typ: 'mc', w}, false); merk('untenFalsch');
      kartei.w[w.id] = [6, h, h - 180]; karteiAntwort({typ: 'mc', w}, true); merk('obenRichtig');
      kartei.w[w.id] = [3, h, h - 14]; karteiAntwort({typ: 'mc', w, retry: true}, true); merk('nochmal');
      // Saetze und Grammatik haben kein w, ein nicht gewusstes Wort zaehlt nicht
      const satz = SENTENCES[0], fremd = CATEGORIES[1].words[0];
      karteiAntwort({typ: 'gap', s: satz}, false); karteiAntwort({typ: 'mc', w: fremd}, true);
      return {r, h, zaehler: [kartei.tag, kartei.n], fremd: fremd.id in kartei.w, alle: Object.keys(kartei.w).length};
    }""")
    h, r = z["h"], z["r"]
    assert h == _heute()
    assert r["neu"] == [0, h + 1, h], "neu gewusst: morgen faellig"
    assert r["gleicherTag"] == [0, h + 1, h], "noch nicht faellig: keine Stufe hoeher"
    assert r["faelligRichtig"] == [1, h + 3, h]
    assert r["faelligFalsch"] == [2, h + 7, h], "zwei Stufen zurueck: nach 30 Tagen falsch, dann eine Woche"
    assert r["frueherFalsch"] == [0, h + 1, h], "falsch zaehlt immer"
    assert r["untenFalsch"] == [0, h + 1, h], "nie unter die erste Stufe"
    assert r["obenRichtig"] == [6, h + 180, h], "180 Tage bleibt die laengste Stufe"
    assert r["nochmal"] == [3, h, h - 14], "die Wiederholung am Ende der Lektion zaehlt nicht"
    # faellig beantwortet: faelligRichtig, faelligFalsch, untenFalsch, obenRichtig
    assert z["zaehler"] == [h, 4]
    assert z["fremd"] is False and z["alle"] == 1
    assert seite.js("() => KARTEI_ABSTAENDE") == ABSTAENDE
    assert seite.js("() => [KARTEI_TAG_MAX, KARTEI_IN_LEKTION]") == [30, 3]
    assert seite.fehler == []


def test_beispiel_aus_dem_vorschlag_tag_fuer_tag(seite, heute_stand):
    """Montag kuca gelernt, Dienstag wieder, dann Freitag, nach einer Woche,
    nach zwei Wochen, nach einem Monat - dann falsch, und es kommt nach
    einer Woche wieder."""
    tag = datetime.date.today()
    _uhr(seite, tag)
    seite.starten(stand=heute_stand())
    seite.js("() => { window.probeWort = CATEGORIES[0].words[0]; known = new Set([probeWort.id]); kartei = {tag: 0, n: 0, w: {}}; }")
    seite.js("() => karteiAntwort({typ: 'mc', w: probeWort}, true)")
    termine = []
    # Dienstag, Freitag, eine Woche, zwei Wochen richtig - nach dem Monat falsch
    for richtig in (True, True, True, True, False):
        f = seite.js("() => kartei.w[probeWort.id][1]")
        tag = APP_START + datetime.timedelta(days=f)
        _uhr(seite, tag)
        assert seite.js("() => karteiHeute()") == [seite.js("() => probeWort.id")]
        seite.js("(ok) => karteiAntwort({typ: 'mc', w: probeWort}, ok)", richtig)
        termine.append(seite.js("() => kartei.w[probeWort.id]"))
    abstaende = [e[1] - e[2] for e in termine]
    assert abstaende == [3, 7, 14, 30, 7], abstaende
    assert [e[0] for e in termine] == [1, 2, 3, 4, 2]
    # Und ganz oben: 90, dann 180 Tage, und dort bleibt es
    seite.js("""() => { const h = karteiTag(); kartei.w[probeWort.id] = [4, h, h - 30];
        karteiAntwort({typ: 'mc', w: probeWort}, true); }""")
    assert seite.js("() => kartei.w[probeWort.id][1] - kartei.w[probeWort.id][2]") == 90
    assert seite.fehler == []


def test_neue_woerter_der_lektion_morgen_faellig(seite, heute_stand):
    """Eine ganze Lektion in Level 1, alles richtig: jedes neu gewusste Wort
    steht mit Stufe 0 und morgen in der Kartei, auch im Geraetespeicher."""
    seite.starten(stand=heute_stand())
    seite.js("() => { openLevel(0); startLesson(); }")
    seite.durchspielen("lBody", "Lx")
    z = seite.js("() => ({neu: [...Lx.newWords], h: karteiTag()})")
    assert len(z["neu"]) >= 5
    kartei = _gespeichert(seite)
    for wid in z["neu"]:
        assert kartei["w"][wid] == [0, z["h"] + 1, z["h"]], wid
    assert seite.js("() => karteiHeute()") == []
    assert seite.fehler == []


def test_level_test_zaehlt_einstufung_nicht(seite, heute_stand):
    ids = _ids(seite, heute_stand, 20)
    h = _heute()
    w = {x: [2, h, h - 7] for x in ids}
    seite.starten(stand=heute_stand(gewusst=ids, bestanden=[], kartei={"tag": 0, "n": 0, "w": w}))
    # Level-Test: eine faellige Wortfrage, richtig beantwortet
    seite.js("""(id) => { passed.add(CATEGORIES[0].id); openLevel(0); startTest();
        const f = wortNachId(id); Tx.qs = [{typ: 'mc', w: f.w, pool: f.c.words}]; Tx.i = 0; showTestQ(); }""", ids[0])
    seite.page.locator("#tBody .opt").first.wait_for()
    seite.js("""() => { const q = Tx.qs[0]; [...document.querySelectorAll('#tBody .opt')]
        .find(o => o.textContent === q.w.bs).click(); }""")
    seite.page.wait_for_function("() => Tx.i === 1")
    assert seite.js("(id) => kartei.w[id]", ids[0]) == [3, h + 14, h]
    assert seite.js("() => [kartei.tag, kartei.n]") == [h, 1]
    # Einstufung: alle Fragen richtig, die Kartei bleibt, wie sie war
    vorher = seite.js("() => JSON.stringify(kartei)")
    seite.js("""() => { baueEinstufung('etwas');
        Ex.qs.forEach(q => { if(q.w){ known.add(q.w.id); kartei.w[q.w.id] = [2, karteiTag(), 0]; } });
        window.karteiVorEinstufung = JSON.stringify(kartei); einstufungStarten(); }""")
    seite.js(r"""async () => {
      const body = document.getElementById('eBody'), warte = ms => new Promise(r => setTimeout(r, ms));
      while(Ex && !Ex.fertig && Ex.i < Ex.qs.length){
        const i = Ex.i, q = Ex.qs[i], ende = Date.now() + 5000;
        while(body.dataset.i !== String(i) && Date.now() < ende) await warte(15);
        if(q.typ === 'gap'){
          // Zahlen, die wechseln (25.10.2026): geantwortet wird auf die gezogene Fassung, wie in DURCHSPIELEN
          const s = typeof zahlFassung === 'function' ? zahlFassung(q.s, q.v) : q.s;
          body.querySelector('#xIn').value = s.answer.split(' / ')[0]; body.querySelector('#xCheck').click(); }
        else { const soll = q.typ === 'gram' ? q.g.richtig : (q.typ === 'mcrev' ? q.w.de : q.w.bs);
               [...body.querySelectorAll('.opt')].find(o => o.textContent === soll).click(); }
        while(Ex.i === i && Date.now() < ende) await warte(15);
        const k = body.querySelector('.weiterbox .btn'); if(k){ k.click(); await warte(30); }
      }
    }""")
    assert seite.js("() => Ex.results.length === Ex.qs.length && Ex.results.every(Boolean)")
    assert seite.js("() => JSON.stringify(kartei) === karteiVorEinstufung")
    assert vorher != seite.js("() => karteiVorEinstufung"), "die Probe hatte faellige Woerter in der Einstufung"
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Der Umzug
# ---------------------------------------------------------------------------

def test_umzug_verteilt_auf_wochen_aelteste_level_zuerst(seite, heute_stand):
    ids = _ids(seite, heute_stand, 100)
    seite.starten(stand=heute_stand(gewusst=ids + ["gibt:es-nicht"]))
    h = _heute()
    z = seite.js("() => ({w: kartei.w, heute: karteiHeute(), bekannt: known.has('gibt:es-nicht')})")
    assert set(z["w"]) == set(ids), "jedes gewusste Wort, das es gibt, und nur diese"
    assert z["bekannt"], "known selbst bleibt unberuehrt"
    assert z["heute"] == [], "nie am ersten Tag faellig"
    termine = [z["w"][x][1] for x in ids]
    assert termine == sorted(termine), "die aeltesten Level zuerst"
    assert termine[0] == h + 1
    je_tag = {}
    for f in termine:
        je_tag[f] = je_tag.get(f, 0) + 1
    assert max(je_tag.values()) == 4 and len(je_tag) == 25, je_tag      # 100 / 28 -> 4 je Tag
    assert all(e[0] == 3 and e[2] == 0 for e in z["w"].values()), "Stufe 3 (Pruefung vom 29.10.2026)"
    assert _gespeichert(seite)["w"] == z["w"], "gleich gespeichert"
    # Neu laden: nichts wandert ein zweites Mal
    seite.neu_laden()
    assert seite.js("() => kartei.w") == z["w"]
    # Alle Woerter: hoechstens 10 je Tag, nie weiter als 180 Tage
    alle = seite.js("""() => { known = new Set(CATEGORIES.flatMap(c => c.words).map(w => w.id));
        kartei = {tag: 0, n: 0, w: {}}; karteiNachtragen();
        const f = Object.values(kartei.w).map(e => e[1]), je = {};
        f.forEach(x => { je[x] = (je[x] || 0) + 1; });
        return {n: f.length, max: Math.max(...f), proTag: Math.max(...Object.values(je)), woerter: known.size}; }""")
    assert alle["n"] == alle["woerter"] > 1500
    assert alle["proTag"] == 10 and alle["max"] <= h + 180, alle
    assert seite.fehler == []


def test_umbenanntes_wort_behaelt_seinen_termin(seite, heute_stand):
    h = _heute()
    seite.starten(stand=heute_stand(gewusst=["salz:so"],
                                    kartei={"tag": 0, "n": 0, "w": {"salz:so": [4, h + 9, h - 21]}}))
    assert seite.js("() => kartei.w") == {"salz:so / sol": [4, h + 9, h - 21]}
    assert _gespeichert(seite)["w"] == {"salz:so / sol": [4, h + 9, h - 21]}
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Die Lektion
# ---------------------------------------------------------------------------

def _lektion_stand(seite, heute_stand, mit_kartei=True):
    """Level 1 ganz gewusst und bestanden, in Level 2 sechs Woerter
    gewusst. Fuenf Woerter aus Level 1 sind heute faellig."""
    seite.starten(stand=heute_stand())
    lv = seite.js("() => [CATEGORIES[0].id, CATEGORIES[0].words.map(w => w.id), CATEGORIES[1].words.map(w => w.id),"
                  " CATEGORIES[0].label]")
    h = _heute()
    w = {x: [1, h - i, h - 4] for i, x in enumerate(lv[1][:5])} if mit_kartei else {}
    seite.starten(stand=heute_stand(gewusst=lv[1] + lv[2][:6], bestanden=[lv[0]],
                                    kartei={"tag": 0, "n": 0, "w": w}))
    return lv


LEKTION = """() => { openLevel(1); startLesson();
  const ws = Lx.queue.filter(a => a.w && a.typ !== 'intro');
  return {neu: ws.filter(a => a.neu).length, woerter: ws.length,
          faellig: ws.filter(a => a.faellig).map(a => ({id: a.w.id, rep: a.rep, pool: a.pool === wortNachId(a.w.id).c.words})),
          ids: ws.map(a => a.w.id), heute: karteiHeute()}; }"""


def test_lektion_bis_zu_drei_faellige_mit_hinweis(seite, heute_stand):
    lv = _lektion_stand(seite, heute_stand, mit_kartei=False)
    ohne = seite.js(LEKTION)
    lv = _lektion_stand(seite, heute_stand)
    mit = seite.js(LEKTION)
    assert len(mit["heute"]) == 5
    assert ohne["faellig"] == []
    assert len(mit["faellig"]) == 3
    # die am laengsten faelligen zuerst (h-4, h-3, h-2); in der Lektion gemischt
    assert mit["heute"][:3] == list(reversed(lv[1][2:5]))
    assert {f["id"] for f in mit["faellig"]} == set(lv[1][2:5])
    assert all(f["rep"] == lv[3] and f["pool"] for f in mit["faellig"])
    assert mit["neu"] == ohne["neu"] == 5, "neue Woerter bleiben gleich viele"
    assert mit["woerter"] == ohne["woerter"] == 10
    assert len(set(mit["ids"])) == len(mit["ids"]), "kein Wort doppelt"
    # Der Hinweis auf der Karte, wie im Level-Test
    text = seite.js("""() => { const i = Lx.queue.findIndex(a => a.faellig); Lx.i = i; showLessonTask();
        return document.querySelector('#lBody .rep').textContent; }""")
    assert text == "Wiederholung: " + lv[3]
    # Weitermachen bleibt beim Level
    seite.js("() => { homeMode = 'words'; showHome(); }")
    assert seite.js("() => document.getElementById('weiterKnopf').textContent").startswith("▶ Weitermachen · ")
    assert seite.fehler == []


def test_lektion_faellige_aus_demselben_level_ohne_hinweis(seite, heute_stand):
    seite.starten(stand=heute_stand())
    ids = seite.js("() => CATEGORIES[0].words.map(w => w.id)")
    h = _heute()
    seite.starten(stand=heute_stand(gewusst=ids[:8], kartei={"tag": 0, "n": 0, "w": {ids[0]: [0, h, h - 1]}}))
    z = seite.js("""() => { openLevel(0); startLesson(); const a = Lx.queue.find(x => x.faellig);
        return a && {id: a.w.id, rep: a.rep || null, pool: a.pool || null}; }""")
    assert z == {"id": ids[0], "rep": None, "pool": None}
    assert seite.fehler == []


def test_lektion_faellige_ohne_sprechen(seite, heute_stand):
    """Sprechen laesst sich ueberspringen, und dann zaehlt die Antwort nicht:
    faellige Woerter bekommen in der Lektion nie "speak", wie in der Runde
    (Pruefung vom 29.10.2026). Die uebrigen Woerter behalten ihre Mischung."""
    _lektion_stand(seite, heute_stand)
    z = seite.js("""() => { canSpeak = true; const f = [], rest = [];
        for(let i = 0; i < 40; i++){ openLevel(1); startLesson();
          Lx.queue.filter(a => a.w && a.typ !== 'intro').forEach(a => (a.faellig ? f : rest).push(a.typ)); }
        return {f, rest}; }""")
    assert len(z["f"]) == 120 and "speak" not in z["f"], z["f"]
    assert "speak" in z["rest"]
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Der Kasten "Heute faellig"
# ---------------------------------------------------------------------------

TOPF_ALT = """() => {
  const n = Object.keys(topf).length;
  let html = '<h2>' + esc(t('topf.titel')) + '</h2><div class="desc">' + esc(t('topf.desc')) + '</div>';
  if(!n) return html + '<div class="topfleer">' + esc(t('topf.leer')) + '</div>';
  return html + '<div class="topfzahl">' + n + '</div><div class="topfwort">' + esc(tp('topf.anzahl', n)) + '</div>'
              + '<div class="row"><button class="btn know" id="topfLos">' + esc(t('topf.start')) + '</button></div>';
}"""


def _faellig_stand(seite, heute_stand, n, gesamt=None, **mehr):
    ids = _ids(seite, heute_stand, gesamt or n)
    h = _heute()
    w = {x: [2, h - (i % 5), h - 9] for i, x in enumerate(ids[:n])}
    seite.starten(stand=heute_stand(gewusst=ids, kartei={"tag": 0, "n": 0, "w": w}, **mehr))
    return ids


@pytest.mark.parametrize("breite", [412, 360])
def test_dritter_kasten_unter_markiert_im_selben_aufbau(browser, basis, heute_stand, breite):
    ctx = browser.new_context(viewport={"width": breite, "height": 915}, locale="de-DE", service_workers="block")
    seite = Seite(ctx.new_page(), basis)
    try:
        ids = _faellig_stand(seite, heute_stand, 12)
        seite.js("""(ids) => { topf = {}; stern = {};
            ids.slice(0, 3).forEach((id, i) => { topf['w:' + id] = {typ: 'mc', n: 0, z: 1000 + i}; });
            ids.slice(3, 5).forEach((id, i) => { stern['w:' + id] = {z: 2000 + i, r: 0}; });
            homeMode = 'topf'; showHome(); }""", ids)
        reihe = seite.js("""() => [...document.getElementById('topfHome').children].map(e => e.id)""")
        assert reihe == ["topfBox", "sternBox", "karteiBox"]
        assert seite.js("() => document.getElementById('topfBox').innerHTML") == seite.js(TOPF_ALT)
        k, s = seite.js(KASTEN, "karteiBox"), seite.js(KASTEN, "sternBox")
        assert k["klasse"] == "section" and k["sichtbar"]
        assert k["titel"] == "Heute fällig"
        assert k["desc"] == ("Gelernte Wörter kommen wieder, bevor du sie vergisst – "
                             "erst nach einem Tag, dann immer seltener.")
        assert k["zahl"] == "12" and k["wort"] == "Wörter warten"
        assert k["knopf"] == "Runde starten" and k["knopfId"] == "karteiLos"
        assert k["beschrieben"] == "karteiTitel" and s["beschrieben"] == "sternTitel"
        assert s["knopf"] == "Runde starten" and s["zahl"] == "2"
        # gleicher Aufbau wie "Markiert", Kind fuer Kind. Nur die Hoehe der
        # Beschreibung darf abweichen - ihr Text ist ein anderer und kann
        # eine Zeile mehr oder weniger brauchen.
        assert len(k["bau"]) == len(s["bau"]) == 5
        for a, b in zip(k["bau"], s["bau"]):
            if a[1] == "desc":
                a, b = a[:2] + a[3:], b[:2] + b[3:]
            assert a == b, (a, b)
        assert k["h"] - k["bau"][1][2] == s["h"] - s["bau"][1][2], (k["h"], s["h"])
        # Weitermachen bleibt, wie es war: nur der Topf, nie die Kartei
        assert seite.js("() => document.getElementById('weiterKnopf').textContent") == "▶ Weitermachen · Wiederholen"
        seite.js("() => { topf = {}; homeMode = 'topf'; showHome(); }")
        assert seite.js("() => document.getElementById('weiterKnopf').style.display") == "none"
        # Einzahl
        seite.js("""(ids) => { ids.slice(1, 12).forEach(id => { kartei.w[id][1] = karteiTag() + 3; }); showTopf(); }""", ids)
        assert seite.js(KASTEN, "karteiBox")["wort"] == "Wort wartet"
        assert seite.fehler == []
    finally:
        ctx.close()


def test_kasten_leer_und_ohne_leben(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js("() => { homeMode = 'topf'; showHome(); }")
    k = seite.js(KASTEN, "karteiBox")
    assert k["leer"] == "Heute ist nichts fällig." and k["knopf"] is None and k["zahl"] is None
    assert [x[:2] for x in k["bau"]] == [["H2", ""], ["DIV", "desc"], ["DIV", "topfleer"]]
    # Ohne Leben: Hinweis wie in den Kaesten darueber, kein "Runde starten"
    _faellig_stand(seite, heute_stand, 4, leben={"anzahl": 0, "zeit": 4102444800000})
    seite.js("() => { homeMode = 'topf'; showHome(); }")
    k = seite.js(KASTEN, "karteiBox")
    assert k["zahl"] == "4" and k["knopf"] is None
    assert k["note"] == seite.js("() => t('level.keine_leben', {zeit: fmtMin(nextLifeIn())})")
    seite.js("() => startKartei()")
    assert seite.js("() => !Lx || Lx.quelle !== 'kartei'"), "ohne Leben keine Runde"
    # Zeigt ein Kasten darueber den Hinweis schon, bleiben hier nur Zahl und
    # Wort - sonst stand derselbe lange Text dreimal da (Pruefung vom
    # 29.10.2026). Die zwei alten Kaesten zeigen ihn weiter.
    note = k["note"]
    for mit_topf, mit_stern in ((True, False), (False, True), (True, True)):
        seite.js("""([t, s]) => { topf = {}; stern = {}; const ids = Object.keys(kartei.w);
            if(t) topf['w:' + ids[0]] = {typ: 'mc', n: 0, z: 1000};
            if(s) stern['w:' + ids[1]] = {z: 2000, r: 0};
            showTopf(); }""", [mit_topf, mit_stern])
        k = seite.js(KASTEN, "karteiBox")
        assert k["zahl"] == "4" and k["wort"] == "Wörter warten" and k["note"] is None and k["knopf"] is None
        assert [x[:2] for x in k["bau"]] == [["H2", ""], ["DIV", "desc"], ["DIV", "topfzahl"], ["DIV", "topfwort"]]
        assert seite.js("() => !document.querySelector('#karteiBox button')")
        assert seite.js(KASTEN, "topfBox")["note"] == (note if mit_topf else None)
        assert seite.js(KASTEN, "sternBox")["note"] == (note if mit_stern else None)
        assert seite.js("(n) => document.getElementById('topfHome').textContent.split(n).length - 1",
                        note) == mit_topf + mit_stern
    seite.js("() => { lives = {anzahl: 3, zeit: Date.now()}; topfNachziehen(); }")
    assert seite.js("() => !!document.getElementById('karteiLos')")
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Die Runde
# ---------------------------------------------------------------------------

def test_runde_zaehlt_wie_eine_lektion(seite, heute_stand):
    ids = _faellig_stand(seite, heute_stand, 12)
    h = _heute()
    seite.js("() => { homeMode = 'topf'; showHome(); }")
    seite.page.click("#karteiLos")
    lage = seite.js("""() => ({quelle: Lx.quelle, topf: Lx.topf, n: Lx.queue.length, tag: document.getElementById('tag').textContent,
        ids: Lx.queue.map(a => a.w.id), typen: Lx.queue.map(a => a.typ), rep: Lx.queue.every(a => a.rep),
        heute: karteiHeute(), leben: livesNow()})""")
    assert lage["quelle"] == "kartei" and lage["topf"] is True and lage["tag"] == "Heute fällig"
    assert lage["n"] == 10 and set(lage["ids"]) == set(lage["heute"][:10]), "die am laengsten faelligen zehn"
    assert set(lage["typen"]) <= {"mc", "mcrev", "type", "listen"} and lage["rep"]

    richtig = seite.js(ANTWORT, True)
    assert seite.js("(id) => kartei.w[id]", richtig) == [3, h + 14, h]
    falsch = seite.js(ANTWORT, False)
    z = seite.js("""(id) => ({e: kartei.w[id], leben: livesNow(), imTopf: ('w:' + id) in topf,
                             nochmal: !!Lx.queue[Lx.queue.length - 1].retry, n: kartei.n})""", falsch)
    assert z["e"] == [0, h + 1, h] and z["leben"] == lage["leben"] - 1 and z["imTopf"] and z["nochmal"]
    assert z["n"] == 2
    vorher = seite.js("() => ({lek: questStand('lek'), auf: questStand('auf')})")
    while seite.js("() => Lx.i < Lx.queue.length"):
        seite.js(ANTWORT, True)
    seite.page.locator("#lBody .result-big").wait_for()
    ende = seite.js("""() => ({stat: document.querySelector('#lBody .stat').textContent, tag: days.has(today()),
        lek: questStand('lek'), auf: questStand('auf'), noch: document.getElementById('lMore') && document.getElementById('lMore').textContent,
        zurueck: document.getElementById('lHome').textContent, n: kartei.n, heute: karteiHeute().length,
        nochmalGezaehlt: kartei.w[Lx.queue[Lx.queue.length - 1].w.id]})""")
    assert ende["n"] == 10, "die Wiederholung am Ende zaehlt nicht"
    assert ende["heute"] == 2 and ende["stat"] == "2noch fällig"
    assert ende["tag"], "eine Runde zaehlt fuer die Serie"
    assert ende["lek"] == vorher["lek"] + 1 and ende["auf"] > vorher["auf"]
    assert ende["noch"] == "Noch eine Runde" and ende["zurueck"] == "Zurück zum Wiederholen"
    assert ende["nochmalGezaehlt"] == [0, h + 1, h]
    # Gespeichert
    assert _gespeichert(seite)["n"] == 10
    seite.js("() => document.getElementById('lMore').click()")
    assert seite.js("() => [Lx.quelle, Lx.queue.length]") == ["kartei", 2]
    # Alles fuer heute erledigt
    while seite.js("() => Lx.i < Lx.queue.length"):
        seite.js(ANTWORT, True)
    seite.page.locator("#lBody .result-big").wait_for()
    assert "Für heute ist alles wiederholt." in seite.js("() => document.getElementById('lBody').textContent")
    assert seite.js("() => document.getElementById('lMore')") is None
    assert len(ids) == 12
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Die Tagesgrenze
# ---------------------------------------------------------------------------

def test_hoechstens_30_am_tag_rest_an_den_naechsten_tagen(seite, heute_stand):
    tag = _kartei_datum()
    _uhr(seite, tag)
    ids = _faellig_stand(seite, heute_stand, 50)
    seite.js("() => { homeMode = 'topf'; showHome(); }")
    assert seite.js(KASTEN, "karteiBox")["zahl"] == "30"
    heute = seite.js("() => karteiHeute()")
    f = seite.js("() => kartei.w")
    termine = [f[x][1] for x in heute]
    # alle auf Stufe 2: die relative Verspaetung folgt dem Termin
    assert termine == sorted(termine), "die am laengsten faelligen zuerst"
    # 25 faellige geuebt (egal wo): noch 5 fuer heute
    seite.js("""(ids) => ids.forEach(id => karteiAntwort({typ: 'mc', w: wortNachId(id).w}, true))""", heute[:25])
    seite.js("() => showTopf()")
    assert seite.js(KASTEN, "karteiBox")["zahl"] == "5"
    seite.js("""(ids) => ids.forEach(id => karteiAntwort({typ: 'mc', w: wortNachId(id).w}, true))""", heute[25:])
    seite.js("() => showTopf()")
    assert seite.js(KASTEN, "karteiBox")["leer"] == "Heute ist nichts fällig."
    rest = seite.js("() => Object.keys(kartei.w).filter(id => kartei.w[id][1] <= karteiTag())")
    assert len(rest) == 20, "der Rest bleibt faellig"
    # Am naechsten Tag kommt der Rest zuerst, wieder hoechstens 30
    _uhr(seite, tag + datetime.timedelta(days=1))
    morgen = seite.js("() => karteiHeute()")
    assert set(morgen) == set(rest) and len(morgen) == 20
    assert set(heute).isdisjoint(morgen)
    assert len(ids) == 50
    assert seite.fehler == []


def test_reihenfolge_nach_relativer_verspaetung(seite, heute_stand):
    """Zuerst kommt, was gemessen am Abstand seiner Stufe am weitesten ueber
    der Zeit ist (Pruefung vom 29.10.2026, wie "relative overdueness" in
    Anki): das gestern gelernte Wort vor dem, das nach 90 Tagen zehn Tage zu
    spaet ist. Bei gleichem Wert das aus dem aelteren Level. Vorher kam der
    aelteste Termin zuerst, und ein Rueckstand verdraengte die frisch
    gelernten Woerter."""
    ids = _ids(seite, heute_stand, 6)
    h = _heute()
    w = {
        ids[0]: [5, h - 10, h - 80],    # 90 Tage, 10 zu spaet: 11/90
        ids[1]: [0, h, h - 1],          # gestern gelernt: 1/1
        ids[2]: [2, h - 6, h - 13],     # 7 Tage, 6 zu spaet: 7/7
        ids[3]: [1, h - 5, h - 8],      # 3 Tage, 5 zu spaet: 6/3
        ids[4]: [3, h, h - 14],         # 14 Tage, heute faellig: 1/14
        ids[5]: [4, h - 29, h - 59],    # 30 Tage, 29 zu spaet: 30/30
    }
    seite.starten(stand=heute_stand(gewusst=ids, kartei={"tag": 0, "n": 0, "w": w}))
    assert seite.js("() => kartei.w") == w
    assert seite.js("() => karteiHeute()") == [ids[3], ids[1], ids[2], ids[5], ids[0], ids[4]]
    # Mit nur noch drei Plaetzen fuer heute: die ersten drei, auch in der Lektion
    seite.js("(h) => { kartei.tag = h; kartei.n = 27; }", h)
    assert seite.js("() => karteiHeute()") == [ids[3], ids[1], ids[2]]
    assert seite.fehler == []


def test_kartei_tag_beginnt_um_vier(seite, heute_stand):
    """Um 23:55 gelernt ist um 00:05 noch nicht faellig, erst ab 4 Uhr
    (Pruefung vom 29.10.2026, wie "Naechster Tag beginnt um" in Anki).
    today() - Serie und Tagwerk - wechselt weiter um Mitternacht."""
    tag = _kartei_datum()
    morgen = tag + datetime.timedelta(days=1)
    h = _tag(tag)
    _uhr(seite, tag, 23, 55)
    seite.starten(stand=heute_stand())
    z = seite.js("""() => { window.probeWort = CATEGORIES[0].words[0]; known = new Set([probeWort.id]);
        kartei = {tag: 0, n: 0, w: {}}; karteiAntwort({typ: 'mc', w: probeWort}, true);
        return {e: kartei.w[probeWort.id], h: karteiTag()}; }""")
    assert z == {"e": [0, h + 1, h], "h": h}
    for stunde, minute in ((0, 5), (3, 59)):
        _uhr(seite, morgen, stunde, minute)
        assert seite.js("() => [karteiTag(), karteiHeute(), today()]") == [h, [], morgen.isoformat()], (stunde, minute)
    _uhr(seite, morgen, 4, 0)
    assert seite.js("() => [karteiTag(), karteiHeute()]") == [h + 1, [seite.js("() => probeWort.id")]]
    # Um 01:00 geuebt zaehlt noch fuer den Vortag, auch beim Tageszaehler
    _uhr(seite, morgen + datetime.timedelta(days=1), 1, 0)
    seite.js("() => karteiAntwort({typ: 'mc', w: probeWort}, true)")
    assert seite.js("() => [kartei.w[probeWort.id], kartei.tag, kartei.n]") == [[1, h + 1 + 3, h + 1], h + 1, 1]
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Sicherungsdatei, Cloud, Konto
# ---------------------------------------------------------------------------

EINLESEN = """async (text) => {
  frage = async () => true;
  await sicherungEinlesen(new File([text], 'sicherung.json', {type: 'application/json'}));
  return {kartei, notiz: document.getElementById('sichNote').textContent};
}"""


def test_sicherungsdatei_nimmt_die_kartei_mit(seite, heute_stand):
    ids = _ids(seite, heute_stand, 6)
    h = _heute()
    kartei = {"tag": h, "n": 4, "w": {ids[0]: [3, h + 5, h - 9], ids[1]: [0, h, h - 1]}}
    seite.starten(stand=heute_stand(gewusst=ids[:2], kartei=kartei))
    datei = json.loads(seite.js("() => sicherungInhalt()"))
    assert datei["version"] == 1 and datei["stand"]["kartei"] == kartei
    # Leeren und wieder einlesen: dieselbe Kartei
    seite.js("() => standLeeren()")
    assert seite.js("() => kartei") == {"tag": 0, "n": 0, "w": {}}
    z = seite.js(EINLESEN, json.dumps(datei))
    assert z["kartei"] == kartei, z
    assert _gespeichert(seite) == kartei
    assert seite.fehler == []


def test_alte_sicherung_ohne_kartei_bekommt_termine(seite, heute_stand):
    ids = _ids(seite, heute_stand, 10)
    h = _heute()
    datei = {"app": "zmaj", "version": 1, "stand": {"gewusst": ids, "tage": [datetime.date.today().isoformat()]}}
    z = seite.js(EINLESEN, json.dumps(datei))
    assert set(z["kartei"]["w"]) == set(ids)
    assert all(e[0] == 3 and e[1] > h and e[2] == 0 for e in z["kartei"]["w"].values())
    assert "10" in z["notiz"]
    assert seite.fehler == []


def test_kaputte_kartei_wird_gefiltert(seite, heute_stand):
    ids = _ids(seite, heute_stand, 8)
    h = _heute()
    w = {
        ids[0]: [9, h + 1000, h + 50],        # Stufe zu gross, Termin und Uebungstag in der Zukunft
        ids[1]: [1.7, h + 2.5, h - 3.2, 99],  # Kommazahlen, eine Zahl zu viel
        ids[2]: [-1, h, h],                   # negativ
        ids[3]: ["2", h, h],                  # Text
        ids[4]: [1, h],                       # zu kurz
        ids[5]: {"s": 1},                     # kein Feld
        ids[6]: None,
        ids[7]: [2, h + 3, h - 4],            # in Ordnung
    }
    text = json.dumps({"app": "zmaj", "version": 1, "stand": {
        "gewusst": ids, "kartei": {"tag": h + 9, "n": 3, "w": w}}})
    text = text.replace('{"tag"', '{"__proto__": {"x": 1}, "w2": 1, "tag"', 1)
    text = text.replace('"w": {', '"w": {"__proto__": [1, 1, 1], ', 1)
    z = seite.js(EINLESEN, text)["kartei"]
    assert z["tag"] == 0 and z["n"] == 0, "Zaehlertag aus der Zukunft gilt nicht"
    assert z["w"][ids[0]] == [6, h + 180, h]
    assert z["w"][ids[1]] == [1, h + 2, h - 4]
    assert z["w"][ids[7]] == [2, h + 3, h - 4]
    # die kaputten fallen weg und bekommen als gewusste Woerter einen neuen Termin
    for i in (2, 3, 4, 5, 6):
        assert z["w"][ids[i]][0] == 3 and z["w"][ids[i]][2] == 0, (i, z["w"][ids[i]])
    assert "__proto__" not in z["w"] and set(z) == {"tag", "n", "w"}
    assert seite.js("() => Object.getPrototypeOf(kartei.w) === Object.prototype")
    # Kaputtes im Geraetespeicher: die App startet, die Kartei ist sauber
    seite.starten(stand=heute_stand(gewusst=ids[:1], kartei={"tag": "x", "n": -1, "w": [1, 2]}))
    assert seite.js("() => kartei") == {"tag": 0, "n": 0, "w": {ids[0]: [3, h + 1, 0]}}
    seite.starten(stand=heute_stand(gewusst=ids[:1], kartei="kaputt"))
    assert seite.js("() => kartei.w")[ids[0]][0] == 3
    assert seite.fehler == []


def test_cloud_je_wort_der_zuletzt_geuebte(seite, heute_stand):
    tag1 = datetime.date.today()
    _uhr(seite, tag1)
    ids = _ids(seite, heute_stand, 4)
    h = _tag(tag1)
    seite.starten(stand=heute_stand(gewusst=ids, kartei={"tag": h, "n": 2, "w": {
        ids[0]: [2, h + 7, h], ids[1]: [3, h + 10, h - 4], ids[2]: [1, h + 2, h - 1], ids[3]: [0, h + 1, h]}}))
    seite.js("() => { window.ablage = {}; window.adapter = cloudSpeicherAdapter(window.ablage); }")
    assert seite.js("async () => await cloudAnmelden('anonym', adapter)") is True
    assert json.loads(seite.js("() => ablage.dok.text"))["stand"]["kartei"]["w"][ids[0]] == [2, h + 7, h]
    # Am naechsten Tag hat ein Tablet geuebt: ids[1] spaeter, ids[2] am selben Tag mit frueherem Termin
    _uhr(seite, tag1 + datetime.timedelta(days=1))
    seite.js("""([ids, h]) => { const s = JSON.parse(ablage.dok.text);
        s.stand.kartei = {tag: h + 1, n: 5, w: {[ids[1]]: [1, h + 4, h + 1], [ids[2]]: [0, h + 1, h - 1],
                                              [ids[0]]: [1, h + 3, h - 2]}};
        ablage.dok = {text: JSON.stringify(s), rev: 'tablet.1'}; }""", [ids, h])
    assert seite.js("async () => await cloudAbgleich('start', adapter)") == "zusammengefuehrt"
    k = seite.js("() => kartei")
    assert k["w"][ids[0]] == [2, h + 7, h], "hier zuletzt geuebt"
    assert k["w"][ids[1]] == [1, h + 4, h + 1], "auf dem Tablet zuletzt geuebt"
    assert k["w"][ids[2]] == [0, h + 1, h - 1], "selber Tag: der fruehere Termin"
    assert k["w"][ids[3]] == [0, h + 1, h], "nur hier"
    assert [k["tag"], k["n"]] == [h + 1, 5]
    seite.js("(id) => karteiAntwort({typ: 'mc', w: wortNachId(id).w}, true)", ids[3])
    assert seite.js("async () => await cloudAbgleich('pause', adapter)") == "gespeichert"
    oben = json.loads(seite.js("() => ablage.dok.text"))["stand"]["kartei"]
    assert oben == seite.js("() => kartei") and oben["w"][ids[3]] == [1, h + 4, h + 1]
    assert seite.fehler == []


def test_konto_leeren_leert_die_kartei(seite, heute_stand):
    ids = _faellig_stand(seite, heute_stand, 3)
    assert len(seite.js("() => Object.keys(kartei.w)")) == 3
    seite.js("() => standLeeren()")
    assert seite.js("() => kartei") == {"tag": 0, "n": 0, "w": {}}
    assert _gespeichert(seite) == {"tag": 0, "n": 0, "w": {}}
    seite.neu_laden()
    assert seite.js("() => kartei") == {"tag": 0, "n": 0, "w": {}}
    assert len(ids) == 3
    assert seite.fehler == []


def test_groesse_bleibt_weit_unter_der_cloud_grenze(seite, heute_stand):
    """Alle Woerter gewusst und in der Kartei mit grossen Zahlen, Topf und
    Sterne voll: der Stand passt mehrfach in die Cloud. Dazu die Rechnung
    fuer 7 000 Woerter (Ziel C1/C2) mit derselben Laenge je Wort."""
    seite.starten(stand=heute_stand())
    z = seite.js("""() => {
        const ids = [...new Set(CATEGORIES.flatMap(c => c.words).map(w => w.id))];
        known = new Set(ids); kartei = {tag: 9999, n: 30, w: {}};
        // 9999 ist der Tag 27 Jahre nach APP_START - vierstellig auf lange Sicht
        ids.forEach(id => { kartei.w[id] = [6, 9999, 9999]; });
        topf = {}; stern = {};
        ids.slice(0, TOPF_MAX).forEach((id, i) => { topf['w:' + id] = {typ: 'mcrev', n: 1, z: Date.now() - i}; });
        ids.slice(0, STERN_MAX).forEach((id, i) => { stern['w:' + id] = {z: Date.now() - i, r: Date.now()}; });
        const ganz = utf8Laenge(JSON.stringify(sicherungObjekt()));
        const nurKartei = utf8Laenge(JSON.stringify(kartei));
        return {ganz, nurKartei, n: ids.length, max: CLOUD_GROESSE_MAX}; }""")
    je_wort = z["nurKartei"] / z["n"]
    assert je_wort < 45, je_wort
    assert z["ganz"] < z["max"] / 3, z
    # 7 000 Woerter, Kartei und gewusst skaliert: weiter unter der Grenze
    assert z["ganz"] * 7000 / z["n"] < z["max"], z
    print("Stand mit allen %d Woertern: %d Bytes, Kartei %.1f Bytes je Wort" % (z["n"], z["ganz"], je_wort))
    assert seite.fehler == []
