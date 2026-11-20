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
            ("nach (einem ereignis):nakon", "nach / pro:po"),
            # Pruefbericht 1.4 (14.11.2026), V4: Molim ist die uebliche Antwort auf
            # Hvala; dići / dizati sind die Kurzformen von podići / podizati.
            ("bitte (höflich, allgemein):Molim", "gern geschehen:Nema na čemu"),
            ("hochheben / aufheben / abheben:podići / podignuti", "anheben / aufheben (umgangssprachlich):dići"),
            ("hochheben / aufheben / abheben:podići / podignuti", "anheben / aufheben (umgangssprachlich):dizati"),
            ("hochheben / aufheben / abheben:podizati", "anheben / aufheben (umgangssprachlich):dići"),
            ("hochheben / aufheben / abheben:podizati", "anheben / aufheben (umgangssprachlich):dizati"),
            # B8: beide "Darlehen", beide "Kumpel", im selben Level.
            ("darlehen / anleihe:zajam", "darlehen (privat):pozajmica"),
            ("kumpel (slang, vor allem sarajevo):jaran", "kumpel / kumpelin (locker):drug / drugarica")]
# B5: Ćao ist auch „Hallo“ (F16). Bis zum 14.11.2026 stand hier Zdravo / Ćao; seitdem nimmt
# Zdravo Ćao beim Tippen (Offen-Liste, Punkt 2), siehe test_cao_nie_neben_hallo_und_zaehlt_dort.

# Frage und falscher Knopf im selben Level: Heisst die Frage genau wie ein Teil
# des Knopfs, muss das andere Wort aus der Auswahl heraus sein. Verglichen wird
# ohne Gross/klein wie ueberall bei den Bedeutungen. Darum faellt hier auch "sie
# sind" (oni su) neben "ihr seid / Sie sind" (vi ste) auf, und auf Daenisch "de er"
# neben "I er / De er". Das bleibt: Die Grossschreibung trennt die beiden richtig,
# und genau diesen Unterschied uebt das Level Konjugation.
#
# Pruefbericht 1.4 (14.11.2026), V5: Die Klammer am Ende des Knopfs wird vor dem
# Vergleich abgetrennt. Auf Englisch stand bei der Frage "How are you?" (Kako si?)
# Kako ste mit "How are you? (formal)" als falscher Knopf, in 185 von 400
# Ziehungen - und "How are you?" passt auf beide. Nur die Frage ohne Klammer ist
# das Problem: hat auch sie eine ("How are you? (informal)"), trennen die beiden
# Klammern richtig. Eine Klammer mitten in der Bedeutung bleibt stehen, sie gehoert
# zur Wendung: "to wake (someone) up" (buditi) ist nicht "to wake up" (buditi se).
UNTERSCHIED_GEWOLLT = {"oni su", "vi ste"}
TEIL_DER_FRAGE = r"""
() => {
  const paare = [];
  // Je Form die Klammer(n) am Ende weg, dann wie _bedeutung:
  // "How are you? (formal)" -> "how are you", "Où (vers où) ?" -> "où".
  const ohneKlammer = s => _formen(s).map(f => _bedeutung(f.replace(/(\s*\([^)]*\))+(?=[\s.!?…]*$)/, '')));
  for(const c of CATEGORIES){
    for(const w of c.words){
      const frage = _bedeutung(w.de);
      const mitTeil = c.words.filter(x => x.bs !== w.bs && ohneKlammer(x.de).includes(frage));
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


# K2 (Ajdin K2, 20.11.2026, varianten.py): zajam und pozajmica zaehlen beim Tippen
# fureinander, beide heissen „Darlehen“. In der Auswahl bleiben sie gesperrt.
BEIM_TIPPEN_GLEICH = {frozenset(("darlehen / anleihe:zajam", "darlehen (privat):pozajmica"))}


@pytest.mark.parametrize("wort, anderes", GESPERRT)
def test_gesperrte_paare_nie_in_derselben_auswahl(seite, heute_stand, wort, anderes):
    seite.starten(stand=heute_stand())
    gleich = frozenset((wort, anderes)) in BEIM_TIPPEN_GLEICH
    for a, b in ((wort, anderes), (anderes, wort)):
        e = seite.js(AUSWAHL, [a, b, 200])
        assert e["gesehen"] == 0, (a, b, e)
        # Gesperrt heisst nicht gleichwertig: beim Tippen aendert sich nichts
        # (ausser bei BEIM_TIPPEN_GLEICH).
        assert e["geschwister"] and e["annehmbar"] == gleich, (a, b, e)
    assert seite.fehler == []


@pytest.mark.parametrize("hallo", ["hallo:Merhaba", "hallo (neutral, überall):Zdravo"])
def test_cao_nie_neben_hallo_und_zaehlt_dort(seite, heute_stand, hallo):
    """Pruefbericht 1.4, B5 (F16 ja): Ćao ist auch „Hallo“. Bei Merhaba und seit dem
    14.11.2026 auch bei Zdravo steht es im "auch": nie in derselben Auswahl, beim Tippen
    richtig. Ćao selbst ("Tschüss") nimmt Merhaba nicht, Zdravo seit K2 schon (Ajdin
    K2, 20.11.2026, Karte V1-77 „ja“, varianten.py)."""
    seite.starten(stand=heute_stand())
    hin = seite.js(AUSWAHL, [hallo, "tschüss:Ćao", 200])
    her = seite.js(AUSWAHL, ["tschüss:Ćao", hallo, 200])
    assert hin["gesehen"] == 0 and her["gesehen"] == 0, (hin, her)
    assert hin["geschwister"] and her["geschwister"], (hin, her)
    assert hin["annehmbar"] and her["annehmbar"] == (hallo == "hallo (neutral, überall):Zdravo"), (hin, her)
    assert seite.fehler == []


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_frage_ist_nie_ein_teil_eines_falschen_knopfs(seite, heute_stand, sprache):
    seite.starten(stand=heute_stand(), sprache=sprache)
    rest = [p for p in seite.js(TEIL_DER_FRAGE) if not {p[1], p[3]} == UNTERSCHIED_GEWOLLT]
    assert rest == [], rest
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
