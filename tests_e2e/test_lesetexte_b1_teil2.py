# -*- coding: utf-8 -*-
"""Die B1-Lesetexte der Pakete 3 und 4 am 360-px-Bildschirm (Prüfung 13.11.2026).

Text und Übersetzung zeigen ihre Absätze (white-space: pre-line), und die
Antwortknöpfe verraten die richtige Antwort nicht durch ihre Größe: Lang
(Klasse "long", kleinere Schrift) ist nie nur die richtige. Auf Französisch
steht beim ersten Tor kein Wörterbuch-Hinweis mehr wie "personne (négation)"."""

FRAGE = """([id, nr]) => {
  const i = STORIES.findIndex(s => s.id === id);
  openStory(i); stilleBitte(); showStoryQ(STORIES[i], nr, 0);
  return [...document.querySelectorAll('#rOpts .opt')].map(b => ({t: b.textContent, lang: b.classList.contains('long')}));
}"""


def _richtig(seite, gid, nr):
    return seite.js("([id, nr]) => STORIES.find(s => s.id === id).fragen[nr].richtig", [gid, nr])


def test_absaetze_in_text_und_uebersetzung(seite, heute_stand):
    seite.starten(stand=heute_stand())
    r = seite.js("""() => {
      const i = STORIES.findIndex(s => s.id === 'b1_doktor');
      openStory(i); stilleBitte();
      document.getElementById('rTrans').click();
      const txt = document.querySelector('#rBody .txt'), tr = document.getElementById('rTransText');
      return {ws: getComputedStyle(txt).whiteSpace, wsTrans: getComputedStyle(tr).whiteSpace,
              absaetze: txt.textContent.split('\\n\\n').length, absaetzeTrans: tr.textContent.split('\\n\\n').length,
              breit: document.documentElement.scrollWidth <= window.innerWidth}; }""")
    assert r["ws"] == "pre-line" and r["wsTrans"] == "pre-line", r
    assert r["absaetze"] == 5 and r["absaetzeTrans"] == 5, r
    assert r["breit"], "Seite lässt sich seitlich verschieben"
    assert seite.fehler == []


def test_lange_antwort_ist_nie_nur_die_richtige(seite, heute_stand):
    seite.starten(stand=heute_stand())
    fehler, lange = [], 0
    for gid in ("b1_doktor", "b1_selidba", "b1_zanat", "b1_mejl"):
        for nr in range(3):
            knoepfe = seite.js(FRAGE, [gid, nr])
            lang = [k["t"] for k in knoepfe if k["lang"]]
            lange += len(lang)
            if lang == [_richtig(seite, gid, nr)]:
                fehler.append("%s Frage %d" % (gid, nr + 1))
    assert fehler == []
    assert lange >= 10, "die Klasse long kommt gar nicht an"
    assert seite.fehler == []


def test_erstes_tor_auf_franzoesisch(seite, heute_stand):
    seite.starten(sprache="fr", stand=heute_stand())
    knoepfe = seite.js(FRAGE, ["b1_utakmica", 1])
    texte = sorted(k["t"] for k in knoepfe)
    assert texte == ["aucune des deux équipes", "l'équipe d'Islande", "l'équipe de Bosnie"], texte
    assert _richtig(seite, "b1_utakmica", 1) == "l'équipe d'Islande"
    assert seite.fehler == []
