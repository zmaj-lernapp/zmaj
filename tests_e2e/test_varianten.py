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


def test_tabelle_2c_zaehlt_beim_tippen(seite, heute_stand):
    """Tabelle 2c (Ajdin, 14.11.2026, Prüfbericht 1.4, F6): die zweite Form zählt
    beim Tippen, gezeigt wird sie nie. Alle Zeilen prüft tests/test_varianten.py."""
    seite.starten(stand=heute_stand())
    for level, art, wer, eingabe in (("essen", "type", "brot:hljeb", "kruh"),
                                     ("faelle2", "type", "es gibt kein brot:Nema hljeba", "Nema kruha"),
                                     ("essen_gehen", "type", "speisekarte:jelovnik", "meni"),
                                     ("unterwegs", "type", "auto:auto", "kola"),
                                     ("familie", "type", "tochter:kćerka", "kćer"),
                                     ("basics", "type", "vielen dank:Hvala puno", "Puno hvala"),
                                     ("immobilien", "gap", "Kolika je ___ mjesečno?", "stanarina"),
                                     ("basics", "gap", "Hvala ___!", "lijepa"),
                                     ("satzbau", "gap", "Pitam se ___ li dolazi.", "je")):
        assert seite.js(AUFGABE, [level, art, wer, eingabe]) == RICHTIG, (wer, eingabe)
    assert seite.fehler == []


def test_tabelle_2c_nur_in_einer_richtung(seite, heute_stand):
    """meni heißt auch „mir“, kola und pare sind Mehrzahlwörter: sie gelten nur am
    einen Wort. In der Auswahl stehen radnja und prodavnica, ponekad und nekad
    nicht mehr als falscher Knopf nebeneinander - das Getippte zählt ja auch."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const w = id => wortNachId(id).w;
      const typ = (id, e) => matches(e, annehmbar(w(id)).join(' / '));
      const luecke = (text, e) => { const s = SENTENCES.find(x => x.text === text);
        return matches(e, [s.answer, ...(s.auch || []), ...(s.auch_var || [])].join(' / ')); };
      const geschw = (id, bs) => geschwister(w(id)).some(x => x.bs === bs);
      // „u kolima“, „Nemam para“ und „Supa je u šerpi“ zählen seit der dritten Runde,
      // „kola oca“, „uplatiti pare“ und „Putujemo kolima“ seit den Fragen vom 15.11.,
      // „očeva kola“ seit dem 16.11. (unten), „očev kola“, „uplatiti para“ und
      // „Putujemo kola“ weiter nicht.
      return {nein: [typ('mir ist es egal:Svejedno mi je', 'Jelovnik je svejedno'), typ('mir:meni / mi', 'jelovnik'),
                     typ('das auto des vaters:auto oca', 'očev kola'), typ('geld einzahlen:uplatiti novac', 'uplatiti para'),
                     typ('krankenwagen / rettung:hitna', 'auto hitne pomoći'),
                     typ('der hund hat mich gebissen:Pas me je ujeo', 'Pas me je ugrizao'),
                     luecke('Putujemo ___.', 'kola'), luecke('Koliko je ___?', 'sahata'),
                     luecke('Mislim ___ je dobro.', 'je')],
              geschw: [geschw('laden:prodavnica', 'radnja'), geschw('geschäft (kleiner laden):radnja', 'prodavnica'),
                       geschw('manchmal:ponekad', 'nekad')]};
    }""")
    assert erg == {"nein": ["no"] * 9, "geschw": [True, True, True]}
    assert seite.fehler == []


# Dritte Runde (Ajdin, 14.11.2026 abends, Offen-Liste 5a): je „Ja“, nur beim Tippen.
# Alle Fälle in node prüft tests/test_varianten.py (DRITTE_RUNDE).
DRITTE_RUNDE = [("basics", "type", "entschuldigung (sie):Izvinite", "Oprostite"),
                ("formell", "gap", "___, molim Vas.", "Oprostite"),
                ("routine", "type", "manchmal:ponekad", "nekada"),
                ("faelle1", "type", "ich habe ein auto:Imam auto", "Imam kola"),
                ("praepositionen", "type", "im auto:u autu", "u kolima"),
                ("faelle2", "type", "ich habe kein geld:Nemam novca", "Nemam para"),
                ("praepositionen", "type", "auf dem markt:na pijaci", "na pazaru"),
                ("faelle3", "type", "auf der straße:na ulici", "na sokaku"),
                ("kueche_bad", "gap", "Supa je u ___.", "šerpi")]
# „On ima kuče“ zählte vom 14. bis zum 21.11.2026, dann Ajdin: „es ist welpe also nein soll
# nicht zählen“ (Fragen vom 21.11.2026, 1). Seitdem unten in der Gegenprobe.
GEGEN_DRITTE_RUNDE = """() => {
  const w = id => wortNachId(id).w;
  const typ = (id, e) => matches(e, annehmbar(w(id)).join(' / '));
  const luecke = (text, e) => { const s = SENTENCES.find(x => x.text === text);
    return matches(e, [s.answer, ...(s.auch || []), ...(s.auch_var || [])].join(' / ')); };
  return [typ('entschuldigung (du):Izvini', 'Oprostite'), typ('verzeih mir:Oprosti mi', 'Oprostite mi'),
          luecke('Molim te, ___ mi.', 'oprostite'), typ('manchmal:ponekad', 'nikada'), typ('nie:nikad', 'nekada'),
          typ('ich habe ein auto:Imam auto', 'Imam kolima'), typ('im auto:u autu', 'u kola'),
          typ('er hat einen hund:On ima psa', 'On ima kučeta'), typ('auf der straße:na ulici', 'na sokak'),
          typ('er hat einen hund:On ima psa', 'On ima kuče')];
}"""


def test_dritte_runde_zaehlt_beim_tippen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for level, art, wer, eingabe in DRITTE_RUNDE:
        assert seite.js(AUFGABE, [level, art, wer, eingabe]) == RICHTIG, (wer, eingabe)
    erg = seite.js(GEGEN_DRITTE_RUNDE)
    assert erg == ["no"] * len(erg) and len(erg) >= 3, erg
    assert seite.fehler == []


# Fragen vom 15.11.2026 (Ajdin abends, 9a bis 9i, Offen-Liste 5d): die zweite Form auch
# an diesen neun Stellen, genau mit den bestätigten Formen, nur beim Tippen.
# Alle Fälle in node prüft tests/test_varianten.py (FRAGEN_15_11).
FRAGEN_15_11 = [("faelle4", "type", "mit dem auto:autom", "kolima"),
                ("faelle4", "gap", "Putujemo ___.", "kolima"),
                ("faelle2", "type", "das auto des vaters:auto oca", "kola oca"),
                ("bank", "type", "geld abheben:podići novac", "podići pare"),
                ("bank", "type", "geld einzahlen:uplatiti novac", "uplatiti pare"),
                ("faelle1", "type", "wir suchen die straße:Tražimo ulicu", "Tražimo sokak")]
# 9g „Bojim se kučadi“ und 9h „Čuvaj se kučeta!“ zählten bis zum 21.11.2026 (Ajdin: „es ist
# welpe also nein soll nicht zählen“), seitdem unten in der Gegenprobe.
# 9i „Kuče me je ujelo.“ hat Ajdin am 16.11.2026 zurückgenommen (8b), siehe FRAGEN_16_11.
GEGEN_FRAGEN_15_11 = """() => {
  const w = id => wortNachId(id).w;
  const typ = (id, e) => matches(e, annehmbar(w(id)).join(' / '));
  const luecke = (text, e) => { const s = SENTENCES.find(x => x.text === text);
    return matches(e, [s.answer, ...(s.auch || []), ...(s.auch_var || [])].join(' / ')); };
  return [typ('mit dem auto:autom', 'kola'), luecke('Putujemo ___.', 'kola'),
          typ('das auto des vaters:auto oca', 'očev kola'),
          typ('geld abheben:podići novac', 'podići para'), typ('wir suchen die straße:Tražimo ulicu', 'Tražimo sokaka'),
          typ('ich habe angst vor hunden:Bojim se pasa', 'Bojim se kučeta'),
          typ('vorsicht vor dem hund!:Čuvaj se psa!', 'Čuvaj se kuče!'),
          typ('der hund hat mich gebissen:Pas me je ujeo', 'Kuče me je ujeo'),
          typ('der hund hat mich gebissen:Pas me je ujeo', 'Pas me je ujelo'), typ('hund:pas', 'kučadi'),
          typ('ich habe angst vor hunden:Bojim se pasa', 'Bojim se kučadi'),
          typ('vorsicht vor dem hund!:Čuvaj se psa!', 'Čuvaj se kučeta!')];
}"""


def test_fragen_15_11_zaehlen_beim_tippen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for level, art, wer, eingabe in FRAGEN_15_11:
        assert seite.js(AUFGABE, [level, art, wer, eingabe]) == RICHTIG, (wer, eingabe)
    erg = seite.js(GEGEN_FRAGEN_15_11)
    assert erg == ["no"] * 12, erg
    assert seite.fehler == []


# Fragen vom 16.11.2026 (Ajdin, 8a und 8b, Offen-Liste 6): „očeva kola“ zählt bei „Das Auto
# des Vaters“ auch. Bei „Der Hund hat mich gebissen“ nur „Pas me je ujeo“ und „Ujeo me je
# pas“ („nimm nur pas aber beide“), die kuče-Form vom 15.11. (9i) ist wieder falsch.
# Alle Fälle in node prüft tests/test_varianten.py (FRAGEN_16_11).
FRAGEN_16_11 = [("faelle2", "type", "das auto des vaters:auto oca", "očeva kola"),
                ("faelle2", "type", "das auto des vaters:auto oca", "kola oca"),
                ("faelle2", "type", "das auto des vaters:auto oca", "očev auto"),
                ("tiere_umgang", "type", "der hund hat mich gebissen:Pas me je ujeo", "Pas me je ujeo"),
                ("tiere_umgang", "type", "der hund hat mich gebissen:Pas me je ujeo", "Ujeo me je pas")]
GEGEN_FRAGEN_16_11 = """() => {
  const w = id => wortNachId(id).w;
  const typ = (id, e) => matches(e, annehmbar(w(id)).join(' / '));
  const hund = w('der hund hat mich gebissen:Pas me je ujeo');
  return {nein: [typ('das auto des vaters:auto oca', 'očev kola'), typ('das auto des vaters:auto oca', 'očeva auto'),
                 typ('der hund hat mich gebissen:Pas me je ujeo', 'Kuče me je ujelo.'),
                 typ('der hund hat mich gebissen:Pas me je ujeo', 'Kuče me je ujelo'),
                 typ('der hund hat mich gebissen:Pas me je ujeo', 'Ujelo me je kuče'),
                 typ('er hat einen hund:On ima psa', 'Kuče me je ujelo'),
                 // Die anderen kuče-Formen blieben bis zum 21.11.2026 (Ajdin: „es ist welpe
                 // also nein soll nicht zählen“), seitdem zählt kuče beim Hund nirgends.
                 typ('er hat einen hund:On ima psa', 'On ima kuče'),
                 typ('ich habe angst vor hunden:Bojim se pasa', 'Bojim se kučadi'),
                 typ('vorsicht vor dem hund!:Čuvaj se psa!', 'Čuvaj se kučeta!'),
                 typ('hund:pas', 'kuče')],
          hund: annehmbar(hund), auch_var: hund.auch_var || null,
          // kuče nur noch beim Welpen (štene, V1-104)
          ja: [typ('welpe:štene', 'kuče')]};
}"""


def test_fragen_16_11_zaehlen_beim_tippen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for level, art, wer, eingabe in FRAGEN_16_11:
        assert seite.js(AUFGABE, [level, art, wer, eingabe]) == RICHTIG, (wer, eingabe)
    erg = seite.js(GEGEN_FRAGEN_16_11)
    assert erg["nein"] == ["no"] * 10, erg
    assert erg["hund"] == ["Pas me je ujeo", "Ujeo me je pas"] and erg["auch_var"] is None, erg
    assert erg["ja"] == ["ok"], erg
    assert seite.fehler == []
