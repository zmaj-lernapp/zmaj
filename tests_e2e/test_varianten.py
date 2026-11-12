# -*- coding: utf-8 -*-
"""Andere bosnische Wörter, die beim Tippen genauso gelten (varianten.py, 12.11.2026), in der App.

Bis dahin nahm „Voda je u ___.“ nur flaši, und boci kostete ein Leben. Jetzt
hängen annehmbar() und der Lückensatz in renderTask() "auch_var" an, beim
Satzbau liegt die andere Form nicht als falsche Kachel da, in der Auswahl
nicht als falscher Knopf. Welche Antworten genau dazukommen, hält
tests/test_varianten.py fest.
"""

# Eine Aufgabe in der Lektion des Levels, so wie sie ein Lernender sieht:
# eintippen, Prüfen. Ergebnis: gezählt richtig oder nicht.
AUFGABE = """async ([level, art, wer, eingabe]) => {
  const warte = ms => new Promise(r => setTimeout(r, ms));
  const i = CATEGORIES.findIndex(c => c.id === level);
  openLevel(i); startLesson();
  const task = art === 'gap'
    ? {typ: 'gap', s: SENTENCES.find(x => x.text === wer)}
    : {typ: 'type', w: wortNachId(wer).w, pool: CATEGORIES[i].words};
  Lx.queue = [task]; Lx.i = 0; Lx.total = 1; Lx.right = 0; Lx.results = [];
  showLessonTask();
  await warte(250);
  const body = document.getElementById('lBody');
  body.querySelector('#xIn').value = eingabe;
  body.querySelector('#xCheck').click();
  await warte(150);
  return {richtig: Lx.right, ergebnis: Lx.results[0], rueckmeldung: body.querySelector('#xFb').className};
}"""

RICHTIG = {"richtig": 1, "ergebnis": True, "rueckmeldung": "feedback ok"}


def test_schreibaufgabe_nimmt_das_andere_wort(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for level, wort, eingabe in (("kueche_bad", "flasche:flaša", "boca"),
                                 ("faelle1", "ich trinke kaffee:Pijem kahvu", "Pijem kafu"),
                                 ("kennenlernen", "nachbarn (mehrzahl):komšije", "susjedi"),
                                 ("mengen", "zweimal:dva puta", "dvaput"),
                                 ("zahlen", "einundzwanzig:dvadeset jedan", "dvadeset i jedan")):
        assert seite.js(AUFGABE, [level, "type", wort, eingabe]) == RICHTIG, (wort, eingabe)
    assert seite.fehler == []


def test_lueckensatz_nimmt_das_andere_wort(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for level, text, eingabe in (("kueche_bad", "Voda je u ___.", "boci"),
                                 ("faelle1", "Pijem ___.", "kafu"),
                                 ("zuhause", "Moj ___ je dobar čovjek.", "susjed"),
                                 ("laender", "Švicarska je mala ___.", "zemlja"),
                                 ("kueche_bad", "Voda je u ___.", "flaši")):
        assert seite.js(AUFGABE, [level, "gap", text, eingabe]) == RICHTIG, (text, eingabe)
    assert seite.fehler == []


def test_nichts_anderes_wird_richtig(seite, heute_stand):
    """Andere Fälle des anderen Wortes bleiben falsch, ebenso das andere Wort,
    wo es nicht steht (kafu bei „jedna kahva“, boca in der Lücke mit flaši)."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const w = id => wortNachId(id).w;
      const typ = (id, e) => matches(e, annehmbar(w(id)).join(' / '));
      const luecke = (text, e) => { const s = SENTENCES.find(x => x.text === text);
        return matches(e, [s.answer, ...(s.auch || []), ...(s.auch_var || [])].join(' / ')); };
      return [typ('flasche:flaša', 'bocu'), typ('flasche:flaša', 'boce'), typ('nachbar:komšija', 'susjeda'),
              typ('ein kaffee:jedna kahva', 'jedna kafu'), typ('ich trinke kaffee:Pijem kahvu', 'Pijem kafa'),
              luecke('Voda je u ___.', 'boca'), luecke('Pijem ___.', 'kafa'), luecke('Volim svoju ___.', 'mama'),
              typ('flasche:flaša', 'boca'), luecke('Voda je u ___.', 'boci')];
    }""")
    assert erg == ["no"] * 8 + ["ok", "ok"]
    assert seite.fehler == []


def test_kachel_puno_liegt_nie_neben_mnogo(seite, heute_stand):
    """„Ima mnogo djece“: „Ima puno djece“ ist genauso richtig - puno (aus pun
    mit auch puno) darf keine falsche Kachel sein."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const s = SATZBAU.find(x => x.bs === 'Ima mnogo djece');
      const gesehen = new Set();
      for(let n = 0; n < 300; n++) kachelAblenker(s, 3).forEach(x => gesehen.add(x.toLowerCase()));
      return {ohne: s.ohne, puno: gesehen.has('puno'), anzahl: gesehen.size};
    }""")
    assert erg["ohne"] == ["puno"] and erg["puno"] is False and erg["anzahl"] > 5, erg
    assert seite.fehler == []


def test_auswahl_haelt_die_variante_fern(seite, heute_stand):
    """Stünde boca einmal als eigenes Wort in der App, läge es nie als falscher
    Knopf neben flaša - wie ein Wort aus "auch"."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const flasa = wortNachId('flasche:flaša').w;
      const k = CATEGORIES.find(c => c.id === 'kueche_bad');
      const boca = {id: 'ball:boca', bs: 'boca', de: 'Ball'};
      k.words.push(boca);
      try{
        const geschw = geschwister(flasa).map(x => x.bs);
        let neben = false;
        for(let n = 0; n < 200; n++) if(distractors(flasa, k.words, 3).some(x => x.bs === 'boca')) neben = true;
        return {geschw: geschw.includes('boca'), neben, umgekehrt: geschwister(boca).map(x => x.bs).includes('flaša')};
      } finally { k.words.pop(); }
    }""")
    assert erg == {"geschw": True, "neben": False, "umgekehrt": True}
    assert seite.fehler == []
