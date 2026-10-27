# -*- coding: utf-8 -*-
"""Neue Wörter der Reihe nach (26.10.2026) - im echten Browser.

Ajdin: „bei der zahlen sektion am besten die zahlen in reihenfolge lernen
sowie wochentage und wo es noch passt“. Die Level zahlen, wochentage,
monate und mengen (Zahlen im Satz) tragen in vokabeln.py "reihenfolge":
True; buildLesson() stellt ihre neuen Wörter dann in der Reihenfolge der
Liste vor statt gemischt. Seit dem 26.10.2026 abends (Ajdin: „und auch
reihenfolge berücksichtigen wo es noch sinn ergibt geh durch die app
durch“) auch konjugation, zukunft und routine; zahlen beginnt mit jedan,
nula kommt nach deset; zeit und wetter ordnen mit "reihe" nur ihre
Tageszeiten und Jahreszeiten, der Rest bleibt gemischt. Hier:
  - die ersten zwei echten Lektionen "Zahlen" zeigen ihre Einführungskarten
    der Reihe nach (jedan, dva ... deset, nula);
  - Teil-Reihen: geschlossen und in Folge, an zufälliger Stelle, der Rest
    gemischt; eine angefangene Reihe geht vorn weiter;
  - über alle Lektionen kommen zahlen, wochentage, monate und mengen
    vollständig in der Reihenfolge der Liste;
  - ein Level ohne Reihe (farben) bleibt gemischt;
  - die Wiederholung gewusster Wörter bleibt auch in einem Level mit Reihe
    gemischt;
  - wer mitten im Level ist, behält seinen Stand und bekommt die noch
    fehlenden Wörter der Reihe nach - "sto" als hundert an seinem Platz,
    auch wenn der Tisch (tisch:sto, Level zuhause) schon gewusst ist;
  - ein Wort, das in einer Lektion nicht gewusst wurde, steht in der
    nächsten wieder vorn.
Dass die Daten selbst in der Reihe stehen, prüft tests/test_reihenfolge.py.
"""
import pytest

# Die Einführungskarten der laufenden Lektion anklicken und mitschreiben,
# was auf jeder Karte steht - so, wie der Lernende sie nacheinander sieht.
KARTEN = r"""async () => {
  const body = document.getElementById('lBody');
  const warte = ms => new Promise(r => setTimeout(r, ms));
  const bis = async (bed, was) => {
    const ende = Date.now() + 8000;
    while(!bed()){ if(Date.now() > ende) throw new Error('wartet vergeblich auf: ' + was); await warte(15); }
  };
  const gezeigt = [];
  while(Lx.i < Lx.queue.length && Lx.queue[Lx.i].typ === 'intro'){
    const i = Lx.i;
    await bis(() => body.dataset.i === String(i) && body.querySelector('.big'), 'Karte ' + i);
    gezeigt.push(body.querySelector('.big').textContent);
    body.querySelector('#xNext').click();
    await bis(() => Lx.i > i, 'nach Karte ' + i);
  }
  return gezeigt;
}"""

# Eine Lektion im Level kid starten. Zurück: die noch nicht gewussten Wörter
# des Levels in der Reihenfolge der Liste (vorher) und die neuen Wörter der
# Lektion (intros), beides als bs.
STARTEN = """(kid) => {
  const i = CATEGORIES.findIndex(c => c.id === kid);
  const offen = CATEGORIES[i].words.filter(w => !known.has(w.id)).map(w => w.bs);
  openLevel(i); startLesson();
  return {offen, intros: Lx.queue.filter(q => q.typ === 'intro').map(q => q.w.bs)};
}"""

# Alle Lektionen eines Levels nacheinander bauen, als würde jede Lektion
# ganz richtig beantwortet: die vorgestellten Wörter kommen nach known.
# ohne: Kennungen, die dabei NICHT gewusst werden (falsch beantwortet).
ALLE_LEKTIONEN = """([kid, ohne]) => {
  const i = CATEGORIES.findIndex(c => c.id === kid);
  const nicht = new Set(ohne || []);
  const offen = CATEGORIES[i].words.filter(w => !known.has(w.id)).map(w => w.bs);
  openLevel(i);
  const lektionen = [];
  for(let n = 0; n < 30; n++){
    buildLesson();
    const neu = Lx.queue.filter(q => q.typ === 'intro').map(q => q.w);
    if(!neu.length) break;
    lektionen.push(neu.map(w => w.bs));
    neu.forEach(w => { if(!nicht.has(w.id)) known.add(w.id); });
    nicht.clear();
  }
  return {lektionen, offen, liste: CATEGORIES[i].words.map(w => w.bs)};
}"""


def _flach(lektionen):
    return [w for lektion in lektionen for w in lektion]


def test_erste_zwei_lektionen_zahlen_der_reihe_nach(seite, heute_stand):
    """Zwei echte Lektionen, alles richtig: die Karten "Neues Wort" kommen
    als jedan, dva ... und danach mit dem nächsten noch offenen Wort
    weiter. Die Aufgaben dazwischen bleiben gemischt, das ist hier egal."""
    seite.starten(stand=heute_stand())
    erste = seite.js(STARTEN, "zahlen")
    assert erste["intros"] == ["jedan", "dva", "tri", "četiri", "pet", "šest", "sedam", "osam"]
    assert seite.js(KARTEN) == erste["intros"]
    seite.durchspielen("lBody", "Lx")
    assert seite.js("() => !!document.getElementById('lMore')"), "kein Ergebnisschirm"

    # Gewusst ist ein Wort erst nach seiner richtigen Aufgabe; eine
    # übersprungene Sprechaufgabe zählt nicht. Deshalb gegen "offen" prüfen.
    zweite = seite.js(STARTEN, "zahlen")
    assert len(zweite["intros"]) >= 5
    assert zweite["intros"] == zweite["offen"][:len(zweite["intros"])]
    assert "devet" in zweite["intros"], zweite
    assert seite.js(KARTEN) == zweite["intros"]
    seite.durchspielen("lBody", "Lx")
    assert seite.fehler == []


@pytest.mark.parametrize("kid, groessen", [
    ("zahlen", [8, 5, 5, 5, 5, 4]),
    ("wochentage", [8, 1]),
    ("monate", [8, 5, 1]),
    ("mengen", [8, 5, 5, 5, 5, 3]),
    ("konjugation", [8, 5, 5, 5, 5, 1]),
    ("zukunft", [8, 5, 5, 3]),
    ("routine", [8, 5, 5, 5, 5, 3]),
])
def test_ganzes_level_der_reihe_nach(seite, heute_stand, kid, groessen):
    """Von der ersten bis zur letzten Lektion: zusammen genau die Liste aus
    vokabeln.py, in ihrer Reihenfolge. Die erste Lektion stellt acht Wörter
    vor - bei wochentage also Montag bis Sonntag samt vikend, bei mengen
    jedan brat, dva brata, pet braće und so weiter."""
    seite.starten(stand=heute_stand())
    erg = seite.js(ALLE_LEKTIONEN, [kid, []])
    assert _flach(erg["lektionen"]) == erg["liste"]
    assert [len(x) for x in erg["lektionen"]] == groessen
    if kid == "zahlen":                               # jedan zuerst, nula nach deset
        assert erg["lektionen"][0][0] == "jedan"
        assert _flach(erg["lektionen"])[9:11] == ["deset", "nula"]
    if kid == "konjugation":
        assert erg["lektionen"][0][:6] == ["ja sam", "ti si", "on je / ona je", "mi smo", "vi ste", "oni su"]
    if kid == "zukunft":
        assert erg["lektionen"][0][:5] == ["ću", "ćeš", "će", "ćemo", "ćete"]
    if kid == "routine":
        assert erg["lektionen"][0][:3] == ["ustajati", "Ustajem u sedam", "tuširati se"]
    assert seite.fehler == []


def test_jedes_mal_dieselbe_reihe(seite, heute_stand):
    """Nicht zufällig richtig: zwanzigmal dieselbe erste Lektion gebaut,
    zwanzigmal dieselben Karten."""
    seite.starten(stand=heute_stand())
    reihen = seite.js("""() => { openLevel(CATEGORIES.findIndex(c => c.id === 'monate'));
      return Array.from({length: 20}, () => { buildLesson(); return Lx.queue.filter(q => q.typ === 'intro').map(q => q.w.bs).join(' '); }); }""")
    assert set(reihen) == {"januar februar mart april maj juni juli august"}
    assert seite.fehler == []


def test_level_ohne_reihe_bleibt_gemischt(seite, heute_stand):
    """farben hat kein "reihenfolge": dort kommen die neuen Wörter weiter
    gemischt - nicht immer dieselben, nicht in der Reihenfolge der Liste."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const i = CATEGORIES.findIndex(c => c.id === 'farben');
      openLevel(i);
      const liste = CATEGORIES[i].words.map(w => w.bs);
      const reihen = Array.from({length: 15}, () => { buildLesson(); return Lx.queue.filter(q => q.typ === 'intro').map(q => q.w.bs); });
      return {liste, reihen, feld: CATEGORIES[i].reihenfolge === undefined};
    }""")
    assert erg["feld"]
    verschieden = {" ".join(r) for r in erg["reihen"]}
    assert len(verschieden) > 1, verschieden
    assert any(r != erg["liste"][:len(r)] for r in erg["reihen"])
    assert seite.fehler == []


def test_wiederholung_bleibt_gemischt(seite, heute_stand):
    """Nur die neuen Wörter kommen der Reihe nach. Die Wiederholung
    gewusster Wörter bleibt auch in einem Level mit "reihenfolge" gemischt -
    sonst kämen bei 20 gewussten Zahlen in jeder Lektion nur nula, jedan,
    dva ... als Wiederholung dran und die späteren nie wieder. Zehnmal
    gebaut: die neuen Wörter jedes Mal dieselben der Reihe nach, die
    Wiederholung verschieden und nicht immer die Spitze der Liste."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const i = CATEGORIES.findIndex(c => c.id === 'zahlen');
      const woerter = CATEGORIES[i].words;
      woerter.slice(0, 20).forEach(w => known.add(w.id));
      openLevel(i);
      const runden = Array.from({length: 10}, () => {
        buildLesson();
        return {neu: Lx.queue.filter(q => q.typ === 'intro').map(q => q.w.bs),
                wdh: Lx.queue.filter(q => q.w && q.typ !== 'intro' && !q.neu).map(q => q.w.bs)};
      });
      return {runden, gewusst: woerter.slice(0, 20).map(w => w.bs), offen: woerter.slice(20).map(w => w.bs)};
    }""")
    gewusst, runden = erg["gewusst"], erg["runden"]
    for r in runden:
        assert r["neu"] and r["neu"] == erg["offen"][:len(r["neu"])], r
        assert r["wdh"] and set(r["wdh"]) <= set(gewusst), r
    n = len(runden[0]["wdh"])
    saetze = {frozenset(r["wdh"]) for r in runden}
    assert len(saetze) > 1, saetze
    assert any(set(r["wdh"]) != set(gewusst[:n]) for r in runden)
    assert len(set().union(*saetze)) > n              # auch spätere Zahlen kommen dran
    assert seite.fehler == []


def test_lernstand_mitten_im_level(seite, heute_stand):
    """Gespeicherter Stand mit jedan, pet und deset aus zahlen und dem Tisch
    (tisch:sto) aus zuhause: alles bleibt gewusst, die nächste Lektion
    stellt die fehlenden Zahlen der Reihe nach vor, die gewussten kommen nur
    als Wiederholung, und über alle weiteren Lektionen kommt der Rest
    vollständig in Reihenfolge - "sto" als hundert an seinem Platz, obwohl
    der Tisch mit demselben bs schon gewusst ist."""
    gewusst = ["eins:jedan", "fünf:pet", "zehn:deset", "tisch:sto"]
    seite.starten(stand=heute_stand(gewusst=gewusst))
    assert sorted(seite.js("() => [...known]")) == sorted(gewusst)

    lektion = seite.js(STARTEN, "zahlen")
    assert "sto" in lektion["offen"]                 # hundert:sto ist noch offen
    assert lektion["intros"][:4] == ["dva", "tri", "četiri", "šest"], lektion["intros"]
    assert lektion["intros"] == lektion["offen"][:len(lektion["intros"])]
    assert not {"jedan", "pet", "deset"} & set(lektion["intros"])
    wiederholt = seite.js("() => Lx.queue.filter(q => q.w && q.typ !== 'intro' && !q.neu).map(q => q.w.id)")
    assert wiederholt and set(wiederholt) <= {"eins:jedan", "fünf:pet", "zehn:deset"}, wiederholt
    assert seite.js(KARTEN) == lektion["intros"]
    seite.durchspielen("lBody", "Lx")
    assert set(gewusst) <= set(seite.js("() => [...known]"))

    seite.neu_laden()                                 # gespeichert und wieder gelesen
    assert set(gewusst) <= set(seite.js("() => [...known]"))
    rest = seite.js(ALLE_LEKTIONEN, ["zahlen", []])
    assert _flach(rest["lektionen"]) == rest["offen"]
    # Unabhängig davon, wie "offen" im Browser entsteht: die Stellen der
    # vorgestellten Wörter in der Liste steigen streng (bs ist in zahlen
    # eindeutig, "sto" hier nur als hundert).
    liste = rest["liste"]
    assert len(set(liste)) == len(liste)
    stellen = [liste.index(bs) for bs in _flach(rest["lektionen"])]
    assert stellen == sorted(set(stellen)), stellen
    assert rest["offen"][-4:] == ["devedeset", "sto", "dvjesto", "hiljada"], rest["offen"]
    assert seite.js("""() => CATEGORIES.find(c => c.id === 'zahlen').words.every(w => known.has(w.id))
                              && known.has('tisch:sto') && known.has('hundert:sto')""")
    assert seite.fehler == []


def test_nicht_gewusstes_wort_steht_wieder_vorn(seite, heute_stand):
    """In der ersten Lektion "tri" falsch beantwortet: es ist noch nicht
    gewusst und kommt in der zweiten Lektion als erstes neues Wort, danach
    geht es mit devet weiter."""
    seite.starten(stand=heute_stand())
    erg = seite.js(ALLE_LEKTIONEN, ["zahlen", ["drei:tri"]])
    assert erg["lektionen"][0][:4] == ["jedan", "dva", "tri", "četiri"]
    assert erg["lektionen"][1][:3] == ["tri", "devet", "deset"], erg["lektionen"][1]
    assert _flach(erg["lektionen"]).count("tri") == 2
    assert seite.fehler == []


# ---------------------------------------------------------------------------
# Teil-Reihen in sonst gemischten Leveln (26.10.2026)
# ---------------------------------------------------------------------------

# Ein Level mit "reihe" n-mal von vorn bis zum Ende durchbauen, jedes Mal
# vom selben Stand aus, alles richtig beantwortet.
REIHE_RUNDEN = """([kid, n]) => {
  const i = CATEGORIES.findIndex(c => c.id === kid), c = CATEGORIES[i];
  const vorher = [...known];
  const zurueck = () => { known.clear(); vorher.forEach(x => known.add(x)); };
  openLevel(i);
  const runden = [];
  for(let r = 0; r < n; r++){
    zurueck();
    const lektionen = [];
    for(let k = 0; k < 30; k++){
      buildLesson();
      const neu = Lx.queue.filter(q => q.typ === 'intro').map(q => q.w);
      if(!neu.length) break;
      lektionen.push(neu.map(w => w.bs));
      neu.forEach(w => known.add(w.id));
    }
    runden.push(lektionen);
  }
  zurueck();
  return {runden, reihe: c.reihe, liste: c.words.map(w => w.bs), ohneFeld: c.reihenfolge === undefined};
}"""


@pytest.mark.parametrize("kid, reihe", [
    ("zeit", ["jutro", "podne", "večer", "noć"]),
    ("wetter", ["proljeće", "ljeto", "jesen", "zima"]),
])
def test_teil_reihe_in_folge_rest_gemischt(seite, heute_stand, kid, reihe):
    """Fünfzehnmal das ganze Level: die Reihe kommt jedes Mal geschlossen
    und in ihrer Folge (auch über eine Lektionsgrenze hinweg), an
    wechselnder Stelle; die übrigen Wörter kommen gemischt."""
    seite.starten(stand=heute_stand())
    erg = seite.js(REIHE_RUNDEN, [kid, 15])
    assert erg["reihe"] == reihe and erg["ohneFeld"]
    for lektionen in erg["runden"]:
        flach = _flach(lektionen)
        assert sorted(flach) == sorted(erg["liste"])
        stellen = [flach.index(x) for x in reihe]
        assert stellen == list(range(stellen[0], stellen[0] + len(reihe))), (flach, stellen)
    ohne = [x for x in erg["liste"] if x not in reihe]
    rest = {" ".join(x for x in _flach(lek) if x not in reihe) for lek in erg["runden"]}
    assert len(rest) > 1, rest                                  # der Rest gemischt
    assert rest != {" ".join(ohne)}
    beginn = {_flach(lek).index(reihe[0]) for lek in erg["runden"]}
    assert len(beginn) > 1, beginn                              # Stelle zufällig
    assert seite.fehler == []


def test_angefangene_reihe_geht_vorn_weiter(seite, heute_stand):
    """jutro ist schon gewusst: podne, večer, noć kommen in der nächsten
    Lektion als erste neue Wörter, dahinter der Rest gemischt."""
    seite.starten(stand=heute_stand(gewusst=["morgen (tageszeit):jutro"]))
    reihen = seite.js("""() => { openLevel(CATEGORIES.findIndex(c => c.id === 'zeit'));
      return Array.from({length: 12}, () => { buildLesson(); return Lx.queue.filter(q => q.typ === 'intro').map(q => q.w.bs); }); }""")
    for r in reihen:
        assert r[:3] == ["podne", "večer", "noć"] and "jutro" not in r, r
    assert len({" ".join(r[3:]) for r in reihen}) > 1
    assert seite.fehler == []


def test_wiederholung_in_teil_reihe_bleibt_gemischt(seite, heute_stand):
    """Die Wiederholung gewusster Wörter mischt auch in zeit."""
    seite.starten(stand=heute_stand())
    runden = seite.js("""() => {
      const i = CATEGORIES.findIndex(c => c.id === 'zeit');
      CATEGORIES[i].words.slice(0, 10).forEach(w => known.add(w.id));
      openLevel(i);
      return Array.from({length: 10}, () => { buildLesson();
        return Lx.queue.filter(q => q.w && q.typ !== 'intro' && !q.neu).map(q => q.w.bs).sort().join(' '); });
    }""")
    assert len(set(runden)) > 1, runden
    assert seite.fehler == []
