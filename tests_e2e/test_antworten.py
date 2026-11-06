# -*- coding: utf-8 -*-
"""Die Antwortknoepfe der Auswahlaufgaben (Pruefbericht zu 1.3, 06.11.2026).

V1: Heisst die Frage genau wie ein Teil eines falschen Knopfs ("ziehen" neben
"ziehen / zurueckziehen"), ist der falsche Knopf in Wahrheit richtig und kostet
trotzdem ein Leben. Solche Paare stehen in NIE_NEBENEINANDER und damit nie in
derselben Auswahl, in allen Sprachen. Beim Tippen zaehlt das andere Wort weiter
nicht.
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
