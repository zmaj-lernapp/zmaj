# -*- coding: utf-8 -*-
"""K2 und K7 in der App (1.5, eingebaut am 27.11.2026).

Was dazukam, steht in tests/k2_einbau.py und wird in tests/test_k2.py am Inhalt
geprueft. Hier der Weg durch die App: der alte Lernstand von Hose und Geschaeft zieht
auf die neue Kennung, die neuen Woerter und das Level Ordnungszahlen sind da, beim
Tippen zaehlen radnja, trgovina und prodavnica fuereinander (nicht bei „Handel“), in
der Auswahl stehen sie nie gegeneinander, und „4.“ gilt bei četvrti, beim Tippen und
beim Sprechen.
"""
from test_kartei import _heute
from test_varianten import AUFGABE, RICHTIG

HOSE_ALT, HOSE = "hose:pantalone", "hose:pantalone / hlače"
LADEN_ALT, KLEIN = "geschäft:radnja", "geschäft (kleiner laden):radnja"
GROSS = "geschäft (großer laden):trgovina"


def _gespeichert(seite):
    return seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand'))")


def test_alter_stand_von_hose_und_geschaeft_zieht_um(seite, heute_stand):
    """Gewusst, Fehler-Topf, Stern und Lernkartei wandern beim Start auf die neue
    Kennung (UMBENANNT), Unbeteiligtes bleibt, und beim Neuladen wandert nichts doppelt."""
    h = _heute()
    seite.starten(stand=heute_stand(
        gewusst=[HOSE_ALT, LADEN_ALT, "brot:hljeb"],
        topf={"w:" + HOSE_ALT: {"typ": "type", "n": 1, "z": 123}},
        stern={"w:" + LADEN_ALT: {"z": 50, "r": 7}},
        kartei={"tag": 0, "n": 0, "w": {HOSE_ALT: [4, h + 9, h - 21], LADEN_ALT: [2, h + 3, h - 5]}}))
    jetzt = seite.js("""() => ({known: [...known].sort(), topf, stern, kartei: kartei.w,
                                umbenannt: [UMBENANNT['hose:pantalone'], UMBENANNT['geschäft:radnja']]})""")
    assert jetzt["umbenannt"] == [HOSE, KLEIN]
    assert jetzt["known"] == sorted(["brot:hljeb", HOSE, KLEIN])
    assert jetzt["topf"] == {"w:" + HOSE: {"typ": "type", "n": 1, "z": 123}}
    assert jetzt["stern"] == {"w:" + KLEIN: {"z": 50, "r": 7}}
    # brot:hljeb bekommt seinen Termin erst jetzt (karteiNachtragen), die beiden behalten ihren
    assert {k: v for k, v in jetzt["kartei"].items() if k != "brot:hljeb"} == {HOSE: [4, h + 9, h - 21],
                                                                              KLEIN: [2, h + 3, h - 5]}
    d = _gespeichert(seite)
    assert sorted(d["gewusst"]) == jetzt["known"] and d["stern"] == jetzt["stern"]
    # trgovina „Geschäft (großer Laden)“ ist neu und bleibt ungelernt
    assert GROSS not in jetzt["known"]
    seite.neu_laden()
    assert seite.js("() => [[...known].sort(), Object.keys(topf), Object.keys(stern), Object.keys(kartei.w).sort()]") == [
        sorted(["brot:hljeb", HOSE, KLEIN]), ["w:" + HOSE], ["w:" + KLEIN], sorted(["brot:hljeb", HOSE, KLEIN])]
    assert seite.fehler == []


def test_neue_woerter_und_das_level_ordnungszahlen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const ids = CATEGORIES.map(c => c.id), i = ids.indexOf('ordnungszahlen');
      const w = id => { const x = wortNachId(id); return x ? x.w.bs : null; };
      return {nachbarn: [ids[i - 1], ids[i + 1]], woerter: CATEGORIES[i].words.length,
              erste: CATEGORIES[i].words.slice(0, 2).map(x => x.bs),
              neu: [w('turnschuhe:patike'), w('der vierte:četvrti'), w('tanne:jela'), w('""" + GROSS + """'),
                    w('""" + HOSE + """'), w('schwager (bruder der ehefrau):šurjak')],
              hoseTippen: typable(wortNachId('""" + HOSE + """').w)};
    }""")
    assert erg == {"nachbarn": ["zeitangaben", "sofort_endlich"], "woerter": 30,
                   "erste": ["četvrti", "Živimo na četvrtom spratu, a lift ne radi."],
                   "neu": ["patike", "četvrti", "jela", "trgovina", "pantalone / hlače", "šurjak"],
                   "hoseTippen": False}
    assert seite.fehler == []


def test_geschaefte_zaehlen_beim_tippen_fuereinander(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for level, wort, eingabe in (("einkaufen", KLEIN, "trgovina"), ("einkaufen", KLEIN, "prodavnica"),
                                 ("einkaufen", GROSS, "radnja"), ("einkaufen", GROSS, "prodavnica"),
                                 ("unterwegs", "laden:prodavnica", "trgovina"),
                                 ("einkaufen", "jeans:farmerke", "traperice"),
                                 ("ordnungszahlen", "der vierte:četvrti", "4."),
                                 ("ordnungszahlen", "der vierte:četvrti", "četvrta"),
                                 ("ordnungszahlen", "der tausendste:hiljaditi", "tisućiti")):
        assert seite.js(AUFGABE, [level, "type", wort, eingabe]) == RICHTIG, (wort, eingabe)
    nein = seite.js("""() => {
      const typ = (id, e) => matches(e, annehmbar(wortNachId(id).w).join(' / '));
      return [typ('handel:trgovina', 'radnja'), typ('handel:trgovina', 'prodavnica'),
              typ('der vierte:četvrti', '4'), typ('zuerst:prvo', '1.'), typ('ferse:peta', '5.')];
    }""")
    assert nein == ["no"] * 5
    assert seite.fehler == []


def test_in_der_auswahl_nie_gegeneinander(seite, heute_stand):
    """trgovina heisst auch „Handel“: neben radnja oder prodavnica stuende sonst ein
    zweiter richtiger Knopf. geschwister() haelt sie auseinander, in beide Richtungen."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const w = id => wortNachId(id).w;
      const g = (id, bs) => geschwister(w(id)).some(x => x.bs === bs);
      const pool = CATEGORIES.find(c => c.id === 'einkaufen').words.concat(
        CATEGORIES.find(c => c.id === 'unterwegs').words);
      let neben = false;
      for(let n = 0; n < 200; n++){
        for(const [id, fremd] of [['""" + KLEIN + """', 'trgovina'], ['""" + GROSS + """', 'radnja'],
                                  ['""" + GROSS + """', 'prodavnica'], ['laden:prodavnica', 'trgovina']])
          if(distractors(w(id), pool, 3).some(x => x.bs === fremd)) neben = true;
      }
      return {geschw: [g('handel:trgovina', 'radnja'), g('handel:trgovina', 'prodavnica'),
                       g('""" + KLEIN + """', 'trgovina'), g('""" + GROSS + """', 'radnja'),
                       g('""" + GROSS + """', 'prodavnica'), g('laden:prodavnica', 'trgovina')],
              neben};
    }""")
    assert erg == {"geschw": [True] * 6, "neben": False}
    assert seite.fehler == []


def test_ziffer_mit_punkt_auch_beim_sprechen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => [klingtWie('4.', 'četvrti'), klingtWie('21.', 'dvadeset prvi'),
                             klingtWie('1000.', 'hiljaditi'), klingtWie('četvrti', 'četvrti'),
                             klingtWie('4', 'četvrti'), klingtWie('5.', 'četvrti'), klingtWie('1.', 'prvo'),
                             passtGesprochen('hlače', 'pantalone / hlače')]""")
    assert erg == [True, True, True, True, False, False, False, True]
    assert seite.fehler == []
