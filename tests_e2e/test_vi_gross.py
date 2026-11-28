# -*- coding: utf-8 -*-
"""Hoefliches Vi gross, ueberall (Offen-Liste 5a, Ajdin am 15.11.2026: "mach
doch alles groß").

Im Browser: Gross oder klein ist beim Tippen weiter egal ("hvala vam na
pomoći" ist so richtig wie "Hvala Vam na pomoći"), ohne dass ein anderes Wort
dadurch richtig wird. Beim Satzbau steht "Vam" als Kachel gross da (nur das
erste Wort ist klein) und zaehlt in der richtigen Reihenfolge. Und die
Geschichten zeigen das grosse Vi, beim Antippen kommt die Bedeutung aus dem
Woerterbuch (dort klein: "vam", "vas", "vi", "vašu").
"""
import pytest
from test_tippfehler import EINGEBEN, LAGE, LEGEN, STARTEN

TIPPEN = [
    ("vielen dank für ihre hilfe:Hvala Vam na pomoći", "Hvala Vam na pomoći"),
    ("vielen dank für ihre hilfe:Hvala Vam na pomoći", "hvala vam na pomoći"),
    ("vielen dank für ihre hilfe:Hvala Vam na pomoći", "HVALA VAM NA POMOĆI"),
    ("wo tut es ihnen weh?:Gdje Vas boli?", "gdje vas boli?"),
    ("ich danke ihnen:Zahvaljujem Vam", "zahvaljujem vam"),
    ("sie (höflich):Vi", "vi"),
    ("wir haben ihren antrag bearbeitet.:Obradili smo Vaš zahtjev.", "obradili smo vaš zahtjev"),
]


@pytest.mark.parametrize("ziel,eingabe", TIPPEN)
def test_tippen_gross_oder_klein_egal(seite, heute_stand, ziel, eingabe):
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = seite.js(LEGEN, ["Lx", "type", ziel])
    seite.js(EINGEBEN, [eingabe, 250])
    lage = seite.js(LAGE, "")
    assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, eingabe, lage)
    assert lage["fb"] == "Tačno! ✓", (ziel, eingabe, lage)
    assert seite.fehler == []


def test_gegenprobe_nichts_anderes_wird_richtig(seite, heute_stand):
    """Gross/klein egal heisst nicht: ein anderes Pronomen geht durch. "vas"
    statt "Vam", "ti" statt "Vi" und "tvoj" statt "Vaš" bleiben falsch."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const typ = (id, e) => matches(e, annehmbar(wortNachId(id).w).join(' / '));
      return [typ('vielen dank für ihre hilfe:Hvala Vam na pomoći', 'Hvala Vas na pomoći'),
              typ('sie (höflich):Vi', 'ti'),
              typ('wir haben ihren antrag bearbeitet.:Obradili smo Vaš zahtjev.', 'Obradili smo tvoj zahtjev.'),
              typ('vielen dank für ihre hilfe:Hvala Vam na pomoći', 'hvala vam na pomoći')];
    }""")
    assert erg == ["no", "no", "no", "ok"], erg
    assert seite.fehler == []


# Ein Satz des Satzbaus in ein freies Feld gezeichnet, die Kacheln in der
# Reihenfolge von bs angetippt (wie test_v106.ALLE_SAETZE).
KACHELN = """(bs) => {
  const s = SATZBAU.find(x => x.bs === bs);
  let antwort = null;
  const feld = document.createElement('div');
  document.body.appendChild(feld);
  renderTask({typ: 'kacheln', s}, feld, res => { antwort = res; });
  const vorrat = [...feld.querySelectorAll('#xBank .kachel:not(.platz)')].map(o => o.textContent);
  for(const w of satzKacheln(s.bs)){
    const b = [...feld.querySelectorAll('#xBank .kachel:not(.platz)')].find(o => o.textContent === w);
    if(!b){ feld.remove(); return {fehlt: w, vorrat}; }
    b.click();
  }
  feld.querySelector('#xCheck').click();
  feld.remove();
  return {ok: !!antwort && antwort.ok === true, teile: satzKacheln(s.bs), vorrat};
}"""


@pytest.mark.parametrize("bs,teile", [
    ("Hvala Vam na pomoći", ["hvala", "Vam", "na", "pomoći"]),
    ("Gdje Vas boli?", ["gdje", "Vas", "boli"]),
    ("Izvinite, molim Vas.", ["izvinite", "molim", "Vas"]),
])
def test_kachel_vam_zaehlt(seite, heute_stand, bs, teile):
    seite.starten(stand=heute_stand())
    r = seite.js(KACHELN, bs)
    assert r.get("fehlt") is None, r
    assert r["teile"] == teile and r["ok"] is True, r
    for t in teile:
        assert t in r["vorrat"], (t, r["vorrat"])
    assert seite.fehler == []


@pytest.mark.parametrize("i,stelle,wort,bedeutung", [
    ("opcina", "Hvala Vam na pomoći", "Vam", "Ihnen / euch"),
    ("b1_posao", "Prvo ću Vam pokazati Vašu kancelariju", "Vašu", "Ihre (Akk.)"),
    ("b1_doktor", "Šta Vas boli i od kada?", "Vas", "euch / Sie"),
    ("b1_zanat", "Jeste li Vi napravili", "Vi", "ihr / Sie"),
])
def test_geschichte_zeigt_gross_und_kennt_das_wort(seite, heute_stand, i, stelle, wort, bedeutung):
    seite.starten(stand=heute_stand())
    r = seite.js("""([id, wort]) => { const s = STORIES.find(x => x.id === id);
      return {text: s.text, bedeutung: lookup(wort, s)}; }""", [i, wort])
    assert stelle in r["text"], (i, stelle)
    assert r["bedeutung"] == bedeutung, (i, wort, r["bedeutung"])
    assert seite.fehler == []
