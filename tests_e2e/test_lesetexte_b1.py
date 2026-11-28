# -*- coding: utf-8 -*-
"""Die B1-Lesetexte (13.11.2026, Paket 1 und 2): zwölf längere Geschichten mit Absätzen.

Sie stehen hinter den Geschichten von A1 und A2 in derselben Kette (seit dem
17.11.2026 von leicht nach schwer, tests_e2e/test_geschichten_stufen.py), tragen die
Stufe "B1" und zeigen ihre Absätze (white-space: pre-line in .story .txt und
.trans). Jede Wortform hat im Wörterbuch eine Bedeutung, auch in den anderen
Sprachen. Seit dem 16.11.2026 liest Vesna sie vor (Offen-Liste 6); die Wörter,
die nur in ihnen stehen, haben noch keinen Ton (tests/offen_lesetexte.json)."""
import re


def _genau(text):
    return re.compile("^" + re.escape(text) + "$")


def test_hinter_a1_und_a2_in_einer_kette(seite, heute_stand):
    """Bis zum 17.11.2026 kam b1_ljeto als erste B1 hinter "Razgovor za posao". Seitdem
    beginnt B1 mit b1_vrijeme hinter "Pismo nani", der letzten von A2."""
    seite.starten(stand=heute_stand())
    lage = seite.js("""() => {
      const i = STORIES.findIndex(s => s.id === 'b1_vrijeme');
      return {i: i, n: STORIES.length, davor: STORIES[i - 1].id,
              stufen: [...new Set(STORIES.slice(i).map(s => s.stufe))],
              vorher: [...new Set(STORIES.slice(0, i).map(s => s.stufe))], offen: storyUnlocked(i)}; }""")
    assert lage["i"] == 11 and lage["n"] >= 32, lage
    assert lage["davor"] == "pismo"
    assert lage["stufen"] == ["B1"] and lage["vorher"] == ["A1", "A2"]
    assert lage["offen"] is False, "erst nach der letzten von A2 frei"
    assert seite.js("() => { read.add('pismo'); return storyUnlocked(11); }") is True
    assert seite.fehler == []


def test_absaetze_und_jedes_wort_mit_bedeutung(seite, heute_stand):
    seite.starten(stand=heute_stand())
    r = seite.js("""() => {
      const i = STORIES.findIndex(s => s.id === 'b1_stan');
      openStory(i); stilleBitte();
      const txt = document.querySelector('#rBody .txt');
      const ohne = STORIES.flatMap((s, k) => {
        if(s.stufe !== 'B1') return [];
        openStory(k); stilleBitte();
        return [...document.querySelectorAll('#rBody .txt .w')]
          .filter(w => !lookup(w.textContent, s)).map(w => s.id + ':' + w.textContent); });
      openStory(i); stilleBitte();
      const t2 = document.querySelector('#rBody .txt'), tr = document.getElementById('rTransText');
      return {ws: getComputedStyle(t2).whiteSpace, wsTrans: getComputedStyle(tr).whiteSpace,
              zeilen: t2.textContent.split('\\n').length, hoch: t2.getBoundingClientRect().height,
              ohne: ohne, titel: document.querySelector('#rBody h3').textContent,
              kicker: document.querySelector('#rBody .kicker').textContent}; }""")
    assert r["ws"] == "pre-line" and r["wsTrans"] == "pre-line", r
    assert r["zeilen"] >= 14, r["zeilen"]           # Anzeige, zehn Gesprächszeilen, Schluss
    assert r["ohne"] == [], r["ohne"][:20]
    assert r["titel"] == "Izdajem stan"
    assert r["kicker"].startswith("B1"), r["kicker"]
    assert seite.fehler == []


def test_auf_englisch_uebersetzt(seite, heute_stand):
    seite.starten(sprache="en", stand=heute_stand())
    r = seite.js("""() => {
      const s = STORIES.find(x => x.id === 'b1_rafting');
      return {trans: s.uebersetzung.slice(0, 20), frage: s.fragen[0].frage, richtig: s.fragen[0].richtig,
              slap: lookup('slap', s), stufe: s.stufe}; }""")
    assert r == {"trans": "Emir and his friends", "frage": "Where do they go rafting?",
                 "richtig": "on the Una", "slap": "waterfall", "stufe": "B1"}
    assert seite.fehler == []


def test_alle_fragen_richtig_schaltet_die_naechste_frei(seite, heute_stand):
    seite.starten(stand=heute_stand())
    fragen = seite.js("""() => { const i = STORIES.findIndex(s => s.id === 'b1_ljeto');
      openStory(i); stilleBitte(); return STORIES[i].fragen.map(f => f.richtig); }""")
    assert len(fragen) == 3
    opts = seite.page.locator("#rQ #rOpts .opt")
    for k, richtig in enumerate(fragen):
        opts.filter(has_text=_genau(richtig)).first.click()
        weiter = seite.page.locator("#rQ .weiterbox .btn")
        weiter.wait_for(state="visible")
        weiter.click()
        if k < len(fragen) - 1:
            seite.page.locator("#rQ #rOpts .opt").first.wait_for(state="visible")
    seite.page.locator("#rQ .ergebnis-titel").wait_for(state="visible")
    # Frei wird die naechste in der Folge seit dem 17.11.2026 (b1_svadba) und die
    # naechste in der alten (b1_dijaspora), siehe storyUnlocked()
    lage = seite.js("() => ({gelesen: read.has('b1_ljeto'), weiter: !!document.getElementById('rGoNext'), "
                    "naechste: STORIES[rIdx + 1].id, frei: storyUnlocked(rIdx + 1), "
                    "alt: storyUnlocked(STORIES.findIndex(s => s.id === 'b1_dijaspora'))})")
    assert lage == {"gelesen": True, "weiter": True, "naechste": "b1_svadba", "frei": True, "alt": True}, lage
    assert seite.fehler == []
