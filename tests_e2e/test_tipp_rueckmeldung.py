# -*- coding: utf-8 -*-
"""Nach einer falschen Eingabe die richtige Form, die dem Getippten am nächsten liegt (17.11.2026).

Ajdin beim Handytest (Offen-Liste 7): "ich wollte extra falsch machen damit ich
sehe ob man auch sieht was bei der version die man geschrieben hat falsch ist er
zeigt leider nur die normale form an das müssten wir noch beheben".

Bei "Vielen Dank" (Hauptform Hvala puno) zählen auch Puno hvala, Hvala lijepa,
Hvala mnogo und Mnogo hvala. Wer "Mnogo hvla" tippte, bekam "Fast richtig!",
und beim zweiten Versuch mit demselben Fehler "Richtig wäre: Hvala puno" - von
seinem "Mnogo hvala" stand nirgends etwas. Jetzt sucht naechsteAntwort() unter
allen richtigen Antworten die nächste (Abstand nach clean() wie beim Vergleich),
und die Lösung darunter nennt die Hauptform mit "Auch richtig:". Ist die Eingabe
keiner Form nahe, bleibt es bei der Hauptform. Gesprochen wird weiter die
Hauptform - sie steht in der Lösung, und nur sie hat bei fast allen Formen eine
Aufnahme. Was als richtig, fast richtig oder falsch zählt, bleibt, wie es war.
"""
import pytest

from test_tippfehler import EINGEBEN, HINWEIS, HINWEIS_EN, LAGE, LEGEN, STARTEN, _ist_hinweis

# Was nach der Antwort dasteht und was gesprochen wurde (LEGEN schreibt mit).
LOESUNG = r"""
() => {
  const body = document.getElementById({Lx: 'lBody', Tx: 'tBody', Ex: 'eBody'}[window.__art]);
  const text_ = sel => { const e = body.querySelector(sel); return e ? e.textContent : null; };
  return {fb: text_('#xFb'), auch: text_('.loesung .lauch'), bs: text_('.loesung .lbs'),
          de: text_('.loesung .lde'), gesprochen: window.__gesprochen.slice()};
}
"""


def _legen(seite, art, typ, ziel):
    return seite.js(LEGEN, [art, typ, ziel])


def _eingeben(seite, text, loesung="", ms=250):
    seite.js(EINGEBEN, [text, ms])
    return seite.js(LAGE, loesung)


def _zweimal(seite, art, typ, ziel, eingabe, verraet, hinweis=HINWEIS):
    """Wie Ajdin am Handy: ein Tippfehler gibt erst "Fast richtig!", derselbe
    Text eine Sekunde später ist der zweite Versuch und falsch."""
    leben = _legen(seite, art, typ, ziel)
    _ist_hinweis(_eingeben(seite, eingabe, verraet), eingabe, leben, hinweis)
    seite.page.wait_for_timeout(1050)     # DOPPELT_MS: vorher zählt derselbe Text nicht
    return leben, _eingeben(seite, eingabe), seite.js(LOESUNG)


def _falsch_gezaehlt(lage, leben, kostet=True):
    """Gezählt wie vor dem 17.11.2026: falsch, ein Leben weniger, Fehlerton."""
    assert lage["ergebnis"] is False and "no" in lage["klasse"].split(), lage
    assert lage["leben"] == (leben - 1 if kostet else leben), lage
    assert lage["toene"] == ["no"] and lage["loesung"] and not lage["offen"], lage


def test_mnogo_hvla_zeigt_mnogo_hvala_und_die_hauptform(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben, lage, lsg = _zweimal(seite, "Lx", "type", "vielen dank:Hvala puno", "Mnogo hvla", "mnogo hvala")
    _falsch_gezaehlt(lage, leben)
    assert lsg["fb"] == "Richtig wäre: Mnogo hvala", lsg
    assert lsg["auch"] == "Auch richtig:" and lsg["bs"] == "Hvala puno" and lsg["de"] == "Vielen Dank", lsg
    assert lsg["gesprochen"] == ["Hvala puno"], lsg           # die Aufnahme der Hauptform, wie bisher
    # Gezählt wird wie vorher: die Wiederholung kommt ans Ende, nichts doppelt.
    assert seite.js("() => [Lx.right, Lx.results.length, Lx.queue.filter(q => q.retry).length]") == [0, 1, 1]
    assert seite.fehler == []


def test_hvala_pno_zeigt_nur_die_hauptform(seite, heute_stand):
    """Der Tippfehler liegt an der Hauptform selbst - keine zweite Zeile."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben, lage, lsg = _zweimal(seite, "Lx", "type", "vielen dank:Hvala puno", "Hvala pno", "hvala puno")
    _falsch_gezaehlt(lage, leben)
    assert lsg["fb"] == "Richtig wäre: Hvala puno" and lsg["auch"] is None and lsg["bs"] == "Hvala puno", lsg
    assert seite.fehler == []


def test_oceva_kla_zeigt_oceva_kola(seite, heute_stand):
    """„očeva kola“ zählt seit dem 16.11.2026 bei „das Auto des Vaters“ (auto oca)."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben, lage, lsg = _zweimal(seite, "Lx", "type", "das auto des vaters:auto oca", "očeva kla", "očeva kola")
    _falsch_gezaehlt(lage, leben)
    assert lsg["fb"] == "Richtig wäre: očeva kola", lsg
    assert lsg["auch"] == "Auch richtig:" and lsg["bs"] == "auto oca", lsg
    assert lsg["gesprochen"] == ["auto oca"], lsg
    assert seite.fehler == []


def test_kuce_me_je_ujelo_zeigt_pas_me_je_ujeo(seite, heute_stand):
    """„Kuče me je ujelo“ zählt seit dem 16.11.2026 nicht mehr (Ajdin: „nimm nur
    pas aber beide“). Richtig sind „Pas me je ujeo“ und „Ujeo me je pas“. Gezeigt
    wird „Pas me je ujeo“: nach clean() 5 Zeichen anders (kuce/pas, ujelo/ujeo),
    die gleiche Wortstellung; bis „Ujeo me je pas“ sind es 8. Kein Tippfehler,
    also gleich falsch und ohne "Fast richtig!"."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    ziel = "der hund hat mich gebissen:Pas me je ujeo"
    abst = seite.js("""(id) => { const w = wortNachId(id).w, e = clean('Kuče me je ujelo');
        return annehmbar(w).map(a => [a, abstand(clean(a), e)]); }""", ziel)
    assert abst == [["Pas me je ujeo", 5], ["Ujeo me je pas", 8]], abst
    leben = _legen(seite, "Lx", "type", ziel)
    lage = _eingeben(seite, "Kuče me je ujelo")
    _falsch_gezaehlt(lage, leben)
    lsg = seite.js(LOESUNG)
    assert lsg["fb"] == "Richtig wäre: Pas me je ujeo" and lsg["auch"] is None, lsg
    assert seite.fehler == []


@pytest.mark.parametrize("eingabe", ["ne znam", "xyz", "Mnogo", "Hvala"])
def test_ganz_falsch_zeigt_die_hauptform(seite, heute_stand, eingabe):
    """Keiner Form nahe (mehr als die Hälfte anders): wie bisher die Hauptform.
    „Mnogo“ liegt 6 Zeichen von „Mnogo hvala“ (11) entfernt, „Hvala“ 5 von
    „Hvala puno“ (10) - die Hauptform gewinnt bei Gleichstand ohnehin."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "type", "vielen dank:Hvala puno")
    lage = _eingeben(seite, eingabe)
    _falsch_gezaehlt(lage, leben)
    lsg = seite.js(LOESUNG)
    assert lsg["fb"] == "Richtig wäre: Hvala puno" and lsg["auch"] is None and lsg["bs"] == "Hvala puno", lsg
    assert seite.fehler == []


@pytest.mark.parametrize("satz, eingabe, soll, ganz, spricht", [
    ("Hvala ___!|puno", "mnogp", "mnogo", "Hvala puno!", "Hvala puno!"),             # auch
    ("Voda je u ___.|flaši", "bocii", "boci", "Voda je u flaši.", "Voda je u flaši."),  # auch_var
])
def test_lueckensatz_zeigt_die_naechste_form(seite, heute_stand, satz, eingabe, soll, ganz, spricht):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben, lage, lsg = _zweimal(seite, "Lx", "gap", satz, eingabe, soll)
    _falsch_gezaehlt(lage, leben)
    assert lsg["fb"] == "Richtig wäre: " + soll, lsg
    assert lsg["auch"] == "Auch richtig:" and lsg["bs"] == ganz, lsg
    assert lsg["gesprochen"] == [spricht], lsg
    assert seite.fehler == []


def test_lueckensatz_tippfehler_an_der_hauptform(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben, lage, lsg = _zweimal(seite, "Lx", "gap", "Hvala ___!|puno", "pnuo", "puno")
    _falsch_gezaehlt(lage, leben)
    assert lsg["fb"] == "Richtig wäre: puno" and lsg["auch"] is None and lsg["bs"] == "Hvala puno!", lsg
    assert seite.fehler == []


def test_fehlende_haekchen_an_der_anderen_form(seite, heute_stand):
    """'almost' wie bisher: gilt sofort, ohne Leben, und nennt die getippte Form
    (gemeinteAntwort()). Neu ist nur "Auch richtig:" über der Hauptform."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "type", "das auto des vaters:auto oca")
    lage = _eingeben(seite, "Ocev auto")
    assert lage["ergebnis"] is True and lage["leben"] == leben and lage["toene"] == ["ok"], lage
    assert "almost" in lage["klasse"].split(), lage
    lsg = seite.js(LOESUNG)
    assert lsg["fb"] == "Richtig! Mit Sonderzeichen: očev auto", lsg
    assert lsg["auch"] == "Auch richtig:" and lsg["bs"] == "auto oca", lsg
    # An der Hauptform selbst bleibt es ohne die Zeile.
    leben = _legen(seite, "Lx", "type", "birne:kruška")
    _eingeben(seite, "kruska")
    lsg = seite.js(LOESUNG)
    assert lsg["fb"] == "Richtig! Mit Sonderzeichen: kruška" and lsg["auch"] is None, lsg
    assert seite.fehler == []


def test_richtig_getippte_andere_form_bleibt_wie_sie_war(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = _legen(seite, "Lx", "type", "vielen dank:Hvala puno")
    lage = _eingeben(seite, "Mnogo hvala")
    assert lage["ergebnis"] is True and lage["leben"] == leben and lage["fb"] == "Tačno! ✓", lage
    assert seite.js(LOESUNG)["auch"] is None
    assert seite.fehler == []


@pytest.mark.parametrize("art", ["Tx", "Ex"])
def test_level_test_und_einstufung_genauso(seite, heute_stand, art):
    """Beide gehen durch renderTask(). Die Einstufung kostet keine Leben und
    zählt den Fehler wie bisher."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN[art])
    leben, lage, lsg = _zweimal(seite, art, "type", "vielen dank:Hvala puno", "Mnogo hvla", "mnogo hvala")
    _falsch_gezaehlt(lage, leben, kostet=art == "Tx")
    if art == "Ex":
        assert lage["fehler"] == 1, lage
    assert lsg["fb"] == "Richtig wäre: Mnogo hvala" and lsg["auch"] == "Auch richtig:", lsg
    assert lsg["bs"] == "Hvala puno", lsg
    assert seite.fehler == []


def test_auf_englisch(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="en")
    seite.js(STARTEN["Lx"])
    leben, lage, lsg = _zweimal(seite, "Lx", "type", "vielen dank:Hvala puno", "Mnogo hvla", "mnogo hvala",
                                HINWEIS_EN)
    _falsch_gezaehlt(lage, leben)
    assert lsg["fb"] == "The answer is: Mnogo hvala" and lsg["auch"] == "Also correct:", lsg
    assert lsg["bs"] == "Hvala puno", lsg
    assert seite.fehler == []


def test_jede_andere_form_mit_einem_tippfehler(seite, heute_stand):
    """Über den ganzen Inhalt: jede andere richtige Form (auch, auch_var), mit
    verdoppeltem ersten Buchstaben getippt, wird als Lösung gezeigt. Ausnahme ist
    nur der Gleichstand mit der Hauptform (sskoro: skoro und uskoro je 1 entfernt,
    pprodavac: prodavac und prodavač nach clean() gleich) - dann die Hauptform.
    Im Lückensatz ebenso, dort gibt es keinen Gleichstand.
    Seit K2 (21.11.2026, gut 1.150 weitere Formen) auch der Gleichstand mit
    einer anderen richtigen Form (iistorijska: istorijska und historijska je 1
    entfernt - dann die, die vorne steht) und eine Form aus einem Buchstaben
    (aa für a bei ali): dort greift die Grenze in naechsteAntwort() (2 x
    Abstand > Länge), es bleibt bei der Hauptform. Beides ist keine falsche
    Lösung, denn gezeigt wird eine richtige Form, die genauso nah liegt."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const aus = {woerter: 0, saetze: 0, anders: [], gleichstand: 0, zuKurz: 0};
      const prueft = (antworten, haupt, alts, zaehler) => {
        const teile = String(haupt).split(' / ');
        for(const alt of alts){
          if(teile.includes(alt)) continue;
          const e = alt[0] + alt;
          if(matches(e, antworten) !== 'no') continue;
          aus[zaehler]++;
          const z = naechsteAntwort(e, antworten, haupt);
          if(z === alt) continue;
          const dAlt = abstand(clean(alt), clean(e));
          const dZ = Math.min(...String(z).split(' / ').map(h => abstand(clean(h), clean(e))));
          if(z === haupt && 2 * dAlt > clean(alt).length) aus.zuKurz++;
          else if(dZ === dAlt) aus.gleichstand++;
          else aus.anders.push([haupt, alt, e, z]);
        }
      };
      for(const w of CATEGORIES.flatMap(c => c.words)){
        const alts = [...(w.auch || []), ...(w.auch_var || [])].flatMap(x => String(x).split(' / '));
        if(alts.length) prueft(annehmbar(w).join(' / '), w.bs, alts, 'woerter');
      }
      for(const s of SENTENCES){
        const alts = [...(s.auch || []), ...(s.auch_var || [])];
        if(alts.length) prueft([s.answer, ...alts].join(' / '), s.answer, alts, 'saetze');
      }
      return aus;
    }""")
    assert erg["woerter"] > 900 and erg["saetze"] > 30, erg
    # 15 Gleichstände und 2 zu kurze Formen (s, a) am 21.11.2026 (vor K2: höchstens 10)
    assert erg["anders"] == [] and erg["gleichstand"] <= 20 and erg["zuKurz"] <= 3, erg
    assert seite.fehler == []
