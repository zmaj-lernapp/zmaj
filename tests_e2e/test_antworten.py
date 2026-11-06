# -*- coding: utf-8 -*-
"""Die Antwortknoepfe der Auswahlaufgaben (Pruefbericht zu 1.3, 06.11.2026).

V1: Heisst die Frage genau wie ein Teil eines falschen Knopfs ("ziehen" neben
"ziehen / zurueckziehen"), ist der falsche Knopf in Wahrheit richtig und kostet
trotzdem ein Leben. Solche Paare stehen in NIE_NEBENEINANDER und damit nie in
derselben Auswahl, in allen Sprachen. Beim Tippen zaehlt das andere Wort weiter
nicht.

G1: Bei "Was bedeutet ...?" stand dieselbe Bedeutung zweimal da, etwa zweimal
"herstellen" bei poboljšati. Der doppelte Knopf schied sofort aus.

G2: Die falschen Antworten kamen gemischt aus Woertern und Beispielsaetzen. Wer ein
Wort sucht, strich die Saetze und musste weniger wissen, auch im Level-Test. Jetzt
kommt zuerst dieselbe Art, nur wenn davon zu wenige da sind die andere.
"""
import pytest
from test_aspektpaare import AUSWAHL

SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]

GESPERRT = [("ziehen:vući", "ziehen / zurückziehen:povlačiti"),
            ("also:dakle", "und dann / also:pa"),
            ("aus:iz", "von:od"),
            ("komm! / los!:Hajde!", "auf geht's!:Hajmo!"),
            ("suchen:tražiti", "rufen / anrufen:zvati"),
            ("dokument:dokument", "bescheinigung:potvrda"),
            ("alles gut:Sve je dobro", "was gibt's? / wie läuft's?:Šta ima?"),
            ("wesentlich / wichtig:bitan", "wichtig (der wichtige):važan"),
            ("nach (einem ereignis):nakon", "nach / pro:po")]

# Frage und falscher Knopf im selben Level: Heisst die Frage genau wie ein Teil
# des Knopfs, muss das andere Wort aus der Auswahl heraus sein. Verglichen wird
# ohne Gross/klein wie ueberall bei den Bedeutungen. Darum faellt hier auch "sie
# sind" (oni su) neben "ihr seid / Sie sind" (vi ste) auf, und auf Daenisch "de er"
# neben "I er / De er". Das bleibt: Die Grossschreibung trennt die beiden richtig,
# und genau diesen Unterschied uebt das Level Konjugation.
UNTERSCHIED_GEWOLLT = {"oni su", "vi ste"}
TEIL_DER_FRAGE = r"""
() => {
  const paare = [];
  for(const c of CATEGORIES){
    for(const w of c.words){
      const frage = _bedeutung(w.de);
      const mitTeil = c.words.filter(x => x.bs !== w.bs && _formen(x.de).length > 1 && _formen(x.de).includes(frage));
      if(!mitTeil.length) continue;
      const gesperrt = new Set(geschwister(w).map(x => x.bs));
      mitTeil.filter(x => !gesperrt.has(x.bs)).forEach(x => paare.push([c.id, w.bs, w.de, x.bs, x.de]));
    }
  }
  return paare;
}
"""


# Die Level, in denen im Pruefbericht am meisten doppelte Knoepfe auftraten.
OFT_DOPPELT = ["kaempfen_angreifen", "veraendern_herstellen", "kommen_gehen"]

# Wiederholt ziehen, wie die Aufgabe es tut: die Antwort und drei falsche.
ZIEHEN = r"""
([level, runden]) => {
  let gezogen = 0; const doppelt = [];
  for(const id of level){
    const c = CATEGORIES.find(x => x.id === id);
    if(!c) throw new Error('kein Level ' + id);
    for(let r = 0; r < runden; r++) for(const w of c.words){
      const de = [w, ...distractors(w, c.words, 3)].map(x => _bedeutung(x.de));
      gezogen++;
      if(new Set(de).size !== 4) doppelt.push([w.bs, de]);
    }
  }
  return {gezogen, doppelt: doppelt.slice(0, 5)};
}
"""

# Die echten Knoepfe der Aufgabe "Was bedeutet ...?".
KNOEPFE = r"""
([level, n]) => {
  const li = CATEGORIES.findIndex(c => c.id === level); catIdx = li; openLevel(li);
  document.getElementById('levelHome').style.display = 'none';
  document.getElementById('lesson').style.display = 'block';
  const c = CATEGORIES[li], b = document.getElementById('lBody'), falsch = [];
  for(let i = 0; i < n; i++){
    const w = c.words[i % c.words.length];
    renderTask({typ: 'mcrev', w, pool: c.words}, b, () => {});
    const opts = [...b.querySelectorAll('.opt')].map(o => o.textContent);
    if(opts.length !== 4 || new Set(opts).size !== 4 || !opts.includes(w.de)) falsch.push([w.bs, opts]);
  }
  return falsch;
}
"""

# Einmal jeder (schritt: jeder n-te) Eintrag im eigenen Level: immer drei falsche
# Antworten mit verschiedenen Bedeutungen, und von der anderen Art nur so viele, wie
# von der eigenen im Level fehlen. Dieselbe Art wie in der App: istWort() auf der
# deutschen Bedeutung, damit jede Sprache dieselben Saetze hat.
ALLE_EINTRAEGE = r"""
(schritt) => {
  const satz = w => !istWort(grundBedeutung(w));
  const r = {gezogen: 0, zuWenige: [], doppelt: [], andereArt: [], nurSaetzeNebenWort: 0, nurWoerterNebenSatz: 0};
  for(const c of CATEGORIES){
    c.words.forEach((w, i) => {
      if(i % schritt) return;
      const d = distractors(w, c.words, 3), de = [w, ...d].map(x => _bedeutung(x.de));
      r.gezogen++;
      if(d.length !== 3) r.zuWenige.push(w.bs);
      if(new Set(de).size !== 4) r.doppelt.push([w.bs, de]);
      const gesperrt = new Set(geschwister(w).map(x => x.bs));
      const eigene = new Set(c.words.filter(x => x.bs !== w.bs && !gesperrt.has(x.bs) && satz(x) === satz(w))
                                    .map(x => _bedeutung(x.de))).size;
      const andere = d.filter(x => satz(x) !== satz(w)).length;
      if(andere > Math.max(0, 3 - eigene)) r.andereArt.push([c.id, w.bs, d.map(x => x.bs)]);
      if(andere === 3){ if(satz(w)) r.nurWoerterNebenSatz++; else r.nurSaetzeNebenWort++; }
    });
  }
  return r;
}
"""


@pytest.mark.parametrize("wort, anderes", GESPERRT)
def test_gesperrte_paare_nie_in_derselben_auswahl(seite, heute_stand, wort, anderes):
    seite.starten(stand=heute_stand())
    for a, b in ((wort, anderes), (anderes, wort)):
        e = seite.js(AUSWAHL, [a, b, 200])
        assert e["gesehen"] == 0, (a, b, e)
        # Gesperrt heisst nicht gleichwertig: beim Tippen aendert sich nichts.
        assert e["geschwister"] and not e["annehmbar"], (a, b, e)
    assert seite.fehler == []


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_frage_ist_nie_ein_teil_eines_falschen_knopfs(seite, heute_stand, sprache):
    seite.starten(stand=heute_stand(), sprache=sprache)
    rest = [p for p in seite.js(TEIL_DER_FRAGE) if not {p[1], p[3]} == UNTERSCHIED_GEWOLLT]
    assert rest == []
    assert seite.fehler == []


def test_keine_zwei_gleichen_knoepfe_in_den_haeufigsten_leveln(seite, heute_stand):
    seite.starten(stand=heute_stand())
    e = seite.js(ZIEHEN, [OFT_DOPPELT, 12])
    assert e["gezogen"] > 500 and e["doppelt"] == [], e
    for level in OFT_DOPPELT:
        assert seite.js(KNOEPFE, [level, 60]) == [], level
    assert seite.fehler == []


@pytest.mark.parametrize("sprache, schritt", [("de", 1), ("da", 4)])
def test_alle_eintraege_drei_verschiedene_falsche_von_derselben_art(seite, heute_stand, sprache, schritt):
    seite.starten(stand=heute_stand(), sprache=sprache)
    e = seite.js(ALLE_EINTRAEGE, schritt)
    assert e["gezogen"] > 1000, e
    assert e["zuWenige"] == [] and e["doppelt"] == [], e
    assert e["andereArt"][:5] == [], e["andereArt"][:5]
    # Nachzaehlung aus dem Pruefbericht (vorher 191 von 2.710 und 263 von 1.711):
    # Bei einem Wort stehen nie nur Saetze daneben, bei einem Satz fast nie nur Woerter.
    assert e["nurSaetzeNebenWort"] == 0 and e["nurWoerterNebenSatz"] <= 10 * (5 - schritt), e
    assert seite.fehler == []
