# -*- coding: utf-8 -*-
"""Zahlen, die wechseln (25.10.2026) - im echten Browser.

Ajdin: "die sätze immer mit der gleichen zahl ist und nicht mal variiert".
Ein Satz mit zahl (vokabeln.py) kommt je Aufgabe mit einer der Zahlen aus
zahl.werte: bosnisch als Wort, in der Bedeutung als Ziffer. Daten, Klassen
und Uebersetzungen prueft tests/test_zahlen.py; hier geht es darum, was der
Lernende sieht und hoert:
  - Zahl im Satz, Ziffer in der Bedeutung und die abgespielte Datei passen
    zusammen, und ueber viele Aufgaben kommen mehrere Zahlen vor;
  - zahlFassung() hier baut Zeichen fuer Zeichen dieselben Saetze wie
    inhalt.zahl_fassung() - nach denen heissen die Aufnahmen;
  - die Wiederholung nach einem Fehler behaelt die Zahl, Stern und
    Fehler-Topf haben bei jeder Zahl denselben Eintrag;
  - Englisch und Tuerkisch (7'de, 3'te) stehen richtig da;
  - jede Fassung jedes Kachelsatzes laesst sich legen;
  - nur gelernte Zahlwoerter ("sto" ist hundert, nicht der Tisch), und ohne
    Aufnahme bleibt alles wie heute - so in der Web-Demo;
  - wer per Einstufung oder Level-Test ueber den Level zahlen hinaus ist,
    sieht die Zahlen trotzdem wechseln (Pruefbefund 25.10.2026);
  - "Dva plus dva su četiri." samt umgezogenem Fehler-Topf und Stern.

Die Demo hat die Aufnahmen von Emir nicht (sie liegen nur in der Huelle).
Die Tests tragen deshalb die Eintraege aus ton_nur_emir.json selbst in AUDIO
ein und schreiben mit, welche Datei abgespielt wuerde.
"""
import io
import json
import os
import re

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _toene():
    idx = json.load(io.open(os.path.join(WURZEL, "web", "audio", "index.json"), encoding="utf-8"))["toene"]
    emir = json.load(io.open(os.path.join(WURZEL, "ton_nur_emir.json"), encoding="utf-8"))["toene"]
    return idx, emir


# Wie in der App aus dem Store: die Emir-Aufnahmen stehen in AUDIO, alle
# Zahlwoerter sind gelernt, und abgespielt wird nichts - nur mitgeschrieben.
# Seit dem 26.10.2026 auf beiden Wegen: ueber WebAudio, wenn der Puffer der
# Datei bereitliegt (pufferSpielen), sonst ueber den spieler (spieleDatei).
VORBEREITEN = """([emir, gelernt]) => {
  emir.forEach(([k, d]) => AUDIO.set(k, d));
  if(gelernt) CATEGORIES.find(x => x.id === 'zahlen').words.forEach(w => known.add(w.id));
  window.__gespielt = [];
  spieleDatei = (datei, fertig) => { window.__gespielt.push(datei); if(fertig) setTimeout(fertig, 0); return Promise.resolve(); };
  pufferSpielen = (text) => {
    const d = audioDatei(text), p = d && puffer.get(d);
    if(!p || !p.buf) return false;
    window.__gespielt.push(d); return true;
  };
}"""

# Eine Aufgabe in eine frische Lektion legen. v: null = ziehen lassen.
AUFGABE = """([typ, kat, text, v]) => {
  const s = typ === 'gap' ? SENTENCES.find(x => x.kat === kat && x.text === text)
                          : SATZBAU.find(x => x.kat === kat && x.bs === text);
  if(!s) throw new Error('kein Satz ' + text);
  openLevel(0); startLesson();
  const task = {typ, s};
  if(v !== null) task.v = v;
  Lx.queue = [task]; Lx.i = 0; Lx.total = 1; Lx.results = []; Lx.right = 0;
  showLessonTask();
  window.__gespielt = [];
  const body = document.getElementById('lBody');
  const text_ = sel => { const e = body.querySelector(sel); return e ? e.textContent : null; };
  return {v: task.v, satz: text_('.sentence'), bedeutung: text_('.translation') || text_('.prompt'),
          kacheln: [...body.querySelectorAll('#xBank .kachel')].map(b => b.textContent),
          schluessel: topfSchluessel(task)};
}"""

# Die laufende Aufgabe beantworten: richtig (true), falsch (false) oder mit
# diesem Text. auch: die Kacheln in der Reihenfolge des ersten "auch".
LOESEN = r"""async ([antwort, auch]) => {
  const q = Lx.queue[Lx.i], body = document.getElementById('lBody'), i = Lx.i;
  const s = zahlFassung(q.s, q.v);
  if(q.typ === 'kacheln'){
    const rand = /^[.,!?¿¡:;"„“”«»…()]+|[.,!?¿¡:;"„“”«»…()]+$/g;
    const satz = auch && s.auch && s.auch.length ? s.auch[0] : s.bs;
    const teile = satz.split(/\s+/).map(x => x.replace(rand, '').toLowerCase()).filter(Boolean);
    for(const soll of (antwort === false ? teile.slice().reverse() : teile)){
      const b = [...body.querySelectorAll('#xBank .kachel:not(.platz)')].find(o => o.textContent.toLowerCase() === soll);
      if(!b) throw new Error('keine Kachel "' + soll + '" bei ' + satz);
      b.click();
    }
  } else {
    body.querySelector('#xIn').value = antwort === true ? s.answer : antwort === false ? 'qqqq' : antwort;
  }
  const vorher = window.__gespielt.length;
  body.querySelector('#xCheck').click();
  const warte = async (bed) => { const ende = Date.now() + 3000; while(!bed() && Date.now() < ende) await new Promise(r => setTimeout(r, 15)); };
  await warte(() => Lx.i > i);
  await warte(() => window.__gespielt.length > vorher);
  const text_ = sel => { const e = body.querySelector(sel); return e ? e.textContent : null; };
  return {v: q.v, ok: Lx.results[i], loesung: text_('.loesung .lbs'), bedeutung: text_('.loesung .lde'),
          datei: window.__gespielt[vorher] || null, schluessel: topfSchluessel(q)};
}"""

WEITER = """async () => {
  const ende = Date.now() + 5000;
  let k = null;
  while(!(k = document.querySelector('#lBody .weiterbox .btn')) && Date.now() < ende)
    await new Promise(r => setTimeout(r, 15));
  k.click();
  await new Promise(r => setTimeout(r, 50));
}"""


def _vorbereiten(seite, gelernt=True):
    _, emir = _toene()
    seite.js(VORBEREITEN, [[[e["key"], e["datei"]] for e in emir], gelernt])


def _zahlen_im_satz(satz):
    """Die Zahlwoerter im bosnischen Satz als Werte."""
    import inhalt
    raus = []
    for w in re.findall(r"[^\W\d_]+", satz.lower()):
        n = inhalt.zahl_wert(w)
        n = inhalt.zahl_wert(w, True) if n is None else n
        if n is not None:
            raus.append(n)
    return raus


def _passt(erg, datei_text):
    """Zahl im Satz = Ziffer in der Bedeutung = Zahl der abgespielten Aufnahme."""
    assert erg["ok"] is True, erg
    assert _zahlen_im_satz(erg["loesung"]) == [erg["v"]], erg
    assert re.findall(r"\d+", erg["bedeutung"]) == [str(erg["v"])], erg
    assert erg["datei"], erg
    assert datei_text[erg["datei"]].rstrip(".") == erg["loesung"].rstrip("."), (erg, datei_text[erg["datei"]])


# Feste Faelle fuer den Tausch als ganzes Wort (Pruefbefund 25.10.2026): in
# den 36 echten Saetzen steckt kein Zahlwort in einem anderen Wort, ein
# zahlTausch() ohne Wortgrenze blieb dort also gruen. Dieselben Faelle
# laufen durch inhalt.zahl_ersetzen().
TAUSCH_FAELLE = [
    ("Dvije kahve, molim.", "dvije", "tri", "Tri kahve, molim."),
    ("Petak je pet.", "pet", "šest", "Petak je šest."),                    # nicht am Wortanfang
    ("Imam dvanaest brata, dva.", "dva", "tri", "Imam dvanaest brata, tri."),
    ("Dvadeset i deset.", "deset", "osam", "Dvadeset i osam."),            # nicht am Wortende
    ("Šesti je šest.", "šest", "pet", "Šesti je pet."),                    # mit Haekchen
    ("Pet dana ostajemo.", "pet", "šest", "Šest dana ostajemo."),          # Grossschreibung bleibt
]


def test_js_baut_dieselben_saetze_wie_python(seite, heute_stand):
    """Die Aufnahmen heissen nach inhalt.zahl_fassung(); die App sucht sie
    unter dem, was zahlFassung() baut. Ein Zeichen Unterschied, und der Satz
    bliebe stumm."""
    import inhalt
    soll = [f[3] for f in TAUSCH_FAELLE]
    assert [inhalt.zahl_ersetzen(*f[:3]) for f in TAUSCH_FAELLE] == soll
    for code in ("de", "tr"):
        seite.starten(stand=heute_stand(), sprache=code)
        js = seite.js("""() => [...SENTENCES, ...SATZBAU].filter(s => s.zahl).flatMap(s => s.zahl.werte.map(n => {
            const f = zahlFassung(s, n);
            return [f.text || null, f.answer || null, f.bs || null, f.auch || null, f.de, zahlGanz(f)]; }))""")
        daten = inhalt.lade_daten(code)
        py = [[f.get("text"), f.get("answer"), f.get("bs"), f.get("auch"), f["de"], inhalt.fertiger_satz(f)]
              for s in daten["saetze"] + daten["satzbau"] for _, f in inhalt.zahl_fassungen(s)]
        assert len(js) == len(py) >= 115
        assert js == py, code
        assert seite.js("(faelle) => faelle.map(([t, a, n]) => zahlTausch(t, a, n))",
                        [list(f[:3]) for f in TAUSCH_FAELLE]) == soll, code
    assert seite.fehler == []


def test_zahl_ziffer_und_ton_passen_zusammen(seite, heute_stand):
    idx, emir = _toene()
    datei_text = {e["datei"]: e["text"] for e in idx + emir}
    seite.starten(stand=heute_stand())
    _vorbereiten(seite)
    gesehen = {}
    for typ, kat, text in (("gap", "zeit", "Sada je ___ sati."),            # die Zahl ist die Loesung
                           ("gap", "amt", "___ za pasoš je trideset maraka."),
                           ("gap", "essen", "___ kahve, molim."),           # Dvije, gross am Anfang
                           ("gap", "mengen", "Ostajemo pet ___."),
                           ("kacheln", "essen", "Dvije kahve, molim."),
                           ("kacheln", "saetze", "Ja bih htjela tri jabuke, molim"),
                           ("kacheln", "saetze", "Autobus dolazi u deset")):
        for _ in range(8):
            vorher = seite.js(AUFGABE, [typ, kat, text, None])
            assert isinstance(vorher["v"], int), vorher
            erg = seite.js(LOESEN, [True, False])
            _passt(erg, datei_text)
            gesehen.setdefault(text, set()).add(erg["v"])
            if typ == "kacheln":
                # Die Kacheln liegen klein da, das Zahlwort mit der gezogenen Zahl
                assert _zahlen_im_satz(" ".join(vorher["kacheln"])).count(erg["v"]) >= 1, vorher
    # Ueber viele Aufgaben kommen mehrere Zahlen vor
    assert all(len(v) >= 2 for v in gesehen.values()), gesehen
    assert len(set().union(*gesehen.values())) >= 6, gesehen
    assert seite.fehler == []


def test_getippte_ziffer_gilt(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _vorbereiten(seite)
    seite.js(AUFGABE, ["gap", "zeit", "Sada je ___ sati.", 9])
    erg = seite.js(LOESEN, ["9", False])
    assert erg["ok"] is True and erg["loesung"] == "Sada je devet sati.", erg
    seite.js(AUFGABE, ["gap", "zeit", "Sada je ___ sati.", 9])
    assert seite.js(LOESEN, ["5", False])["ok"] is False      # die heutige Zahl ist jetzt falsch
    seite.js(AUFGABE, ["gap", "essen", "___ kahve, molim.", 3])
    assert seite.js(LOESEN, ["3", False])["loesung"] == "Tri kahve, molim."
    assert seite.fehler == []


def test_wiederholung_behaelt_die_zahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _vorbereiten(seite)
    for typ, kat, text in (("gap", "zeit", "Sada je ___ sati."), ("kacheln", "verben", "Imam trideset godina.")):
        vorher = seite.js(AUFGABE, [typ, kat, text, None])
        erg = seite.js(LOESEN, [False, False])
        assert erg["ok"] is False
        nochmal = seite.js("() => Lx.queue.map(a => [a.retry || false, a.v])")
        assert nochmal == [[False, vorher["v"]], [True, vorher["v"]]], nochmal
        seite.js(WEITER)
        jetzt = seite.js("""() => ({i: Lx.i, v: Lx.queue[Lx.i].v,
            bedeutung: (document.querySelector('#lBody .translation') || document.querySelector('#lBody .prompt')).textContent})""")
        assert jetzt["i"] == 1 and jetzt["v"] == vorher["v"], jetzt
        assert jetzt["bedeutung"] == vorher["bedeutung"], (jetzt, vorher)
        # Der Fehler steht unter dem Grundsatz im Topf, nicht unter der Fassung
        assert seite.js("() => Object.keys(topf)").count(vorher["schluessel"]) == 1
        richtig = seite.js(LOESEN, [True, False])
        assert richtig["ok"] is True and richtig["v"] == vorher["v"]
    assert seite.js("() => Object.keys(topf).sort()") == ["k:verben|Imam trideset godina.", "s:zeit|Sada je ___ sati."]
    assert seite.fehler == []


def test_stern_und_topf_gleich_bei_jeder_zahl(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _vorbereiten(seite)
    a = seite.js(AUFGABE, ["gap", "zeit", "Sada je ___ sati.", 7])
    seite.js("() => document.getElementById('lStern').click()")
    assert seite.js("() => Object.keys(stern)") == ["s:zeit|Sada je ___ sati."]
    b = seite.js(AUFGABE, ["gap", "zeit", "Sada je ___ sati.", 11])
    assert a["schluessel"] == b["schluessel"] == "s:zeit|Sada je ___ sati."
    assert seite.js("() => document.getElementById('lStern').getAttribute('aria-pressed')") == "true"
    assert "11" in b["bedeutung"] and "7" in a["bedeutung"]
    seite.js(LOESEN, [False, False])
    assert list(seite.js("() => topf")) == ["s:zeit|Sada je ___ sati."]
    # Kacheln ebenso
    k1 = seite.js(AUFGABE, ["kacheln", "zeit", "Sada je pet sati.", 6])
    k2 = seite.js(AUFGABE, ["kacheln", "zeit", "Sada je pet sati.", 12])
    assert k1["schluessel"] == k2["schluessel"] == "k:zeit|Sada je pet sati."
    # Aus Topf und Stern kommt der Satz ohne Zahl zurueck und zieht neu
    neu = seite.js("""() => { const a = topfAufgabe('s:zeit|Sada je ___ sati.', topf['s:zeit|Sada je ___ sati.']);
        return [a.typ, a.v === undefined, a.s.text]; }""")
    assert neu == ["gap", True, "Sada je ___ sati."]
    assert seite.fehler == []


def test_englisch_und_tuerkisch(seite, heute_stand):
    for code, typ, kat, text, v, soll in (
            ("en", "gap", "saetze", "Jedemo u ___ sati.", 8, "We eat at 8 o'clock."),
            ("en", "kacheln", "saetze", "Ja bih htjela tri jabuke, molim", 2, "I would like 2 apples, please"),
            ("tr", "gap", "saetze", "Jedemo u ___ sati.", 9, "Saat 9'da yemek yiyoruz."),
            ("tr", "kacheln", "reflexiv", "Nalazimo se u pet.", 3, "Saat 3'te buluşuyoruz."),
            ("tr", "gap", "routine", "Idem ___ u jedanaest.", 10, "Saat 10'da yatıyorum."),
            ("tr", "gap", "zeit", "Sada je ___ sati.", 7, "Şimdi saat 7.")):
        seite.starten(stand=heute_stand(), sprache=code)
        _vorbereiten(seite)
        vorher = seite.js(AUFGABE, [typ, kat, text, v])
        assert soll in vorher["bedeutung"], (code, vorher)
        erg = seite.js(LOESEN, [True, False])
        assert erg["ok"] is True and erg["bedeutung"] == soll, (code, erg)
    assert seite.fehler == []


def test_kacheln_gehen_mit_jeder_zahl_auf(seite, heute_stand):
    """Jede Fassung jedes Kachelsatzes, in der Reihenfolge von bs und von
    "auch": richtig, und die Bank hat genau die Kacheln der Fassung - jede
    so oft, wie sie im Satz steht - und dazu nur Ablenker, die nicht in der
    Fassung stehen, ohne Doppelte.
    Pruefbefund 25.10.2026: vorher stand hier nur bank.includes(), und ein
    kachelAblenker(task.s, ...) statt der Fassung blieb gruen - der Zufall
    legt das gezogene Zahlwort nur in etwa 29 von 4.800 Zuegen ein zweites
    Mal als Ablenker hin ("Tri kahve, molim." mit "tri" daneben). Deshalb
    schreibt der Test zusaetzlich mit, fuer welchen Satz die Ablenker
    gesucht werden: das muss jedes Mal die Fassung sein."""
    seite.starten(stand=heute_stand())
    _vorbereiten(seite)
    erg = seite.js(r"""async () => {
      const fehler = [];
      let anzahl = 0;
      const echt = kachelAblenker, gefragt = [];
      kachelAblenker = (satz, n) => { gefragt.push(satz.bs); return echt(satz, n); };
      try{
      for(const s of SATZBAU.filter(x => x.zahl)){
        for(const n of s.zahl.werte){
          for(const auch of [false, true]){
            const f = zahlFassung(s, n);
            if(auch && !(f.auch && f.auch.length)) continue;
            const feld = document.createElement('div');
            document.body.appendChild(feld);
            let ergebnis = null;
            gefragt.length = 0;
            renderTask({typ: 'kacheln', s, v: n}, feld, r => { ergebnis = r; });
            if(gefragt.length !== 1 || gefragt[0] !== f.bs) fehler.push(['ablenker_fuer', f.bs, gefragt.slice()]);
            const bank = [...feld.querySelectorAll('#xBank .kachel')].map(b => b.textContent.toLowerCase());
            const rest = bank.slice();
            for(const x of satzKacheln(f.bs).map(x => x.toLowerCase())){
              const i = rest.indexOf(x);
              if(i < 0) fehler.push(['fehlt', f.bs, x, bank]); else rest.splice(i, 1);
            }
            const eigene = new Set([f.bs, ...(f.auch || [])].flatMap(x => kachelRoh(x).map(k => k.toLowerCase())));
            if(rest.length > 3 || new Set(rest).size !== rest.length || rest.some(x => eigene.has(x)))
              fehler.push(['ablenker', f.bs, rest]);
            const satz = auch ? f.auch[0] : f.bs;
            for(const k of kachelRoh(satz).map(x => x.toLowerCase())){
              const b = [...feld.querySelectorAll('#xBank .kachel:not(.platz)')].find(o => o.textContent.toLowerCase() === k);
              if(!b){ fehler.push(['kachel', satz, k]); break; }
              b.click();
            }
            feld.querySelector('#xCheck').click();
            if(!ergebnis || ergebnis.ok !== true) fehler.push(['falsch', satz]);
            feld.remove();
            anzahl++;
          }
        }
      }
      } finally { kachelAblenker = echt; }
      stilleBitte();
      return {fehler, anzahl};
    }""")
    assert erg["fehler"] == [], erg["fehler"][:10]
    assert erg["anzahl"] == 182       # 19 Saetze, jede Zahl, mit und ohne "auch"
    assert seite.fehler == []


def test_nur_gelernte_zahlwoerter_und_sto_ist_nicht_der_tisch(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _vorbereiten(seite, gelernt=False)
    erg = seite.js("""() => {
      const s = SENTENCES.find(x => x.text === 'Jakna košta ___ maraka.');
      const z = SENTENCES.find(x => x.text === 'Sada je ___ sati.');
      const ziehen = (satz, mal) => [...new Set(Array.from({length: mal}, () => zahlZiehen(satz)))].sort((a, b) => a - b);
      const ohne = [ziehen(s, 50), ziehen(z, 50)];
      // gelernt: alles aus dem Level zahlen ausser acht und hundert - dafuer der Tisch
      const c = CATEGORIES.find(x => x.id === 'zahlen');
      c.words.filter(w => w.id !== 'acht:osam' && w.id !== 'hundert:sto').forEach(w => known.add(w.id));
      known.add('tisch:sto');
      return {ohne, mit: [ziehen(s, 400), ziehen(z, 400)], kennung: [zahlKennung(100), zahlKennung(2)]};
    }""")
    assert erg["ohne"] == [[None], [None]]
    assert erg["kennung"] == ["hundert:sto", "zwei:dva"]
    assert erg["mit"][0] == [30, 40, 50, 60, 70, 80, 90]      # kein 100: gelernt ist nur der Tisch
    assert erg["mit"][1] == [5, 6, 7, 9, 10, 11, 12]          # kein 8
    assert seite.fehler == []


def test_eingestufte_und_bestandene_sehen_wechselnde_zahlen(seite, heute_stand):
    """Pruefbefund 25.10.2026: Wer per Einstufung ueber den Level zahlen
    hinaus startet, hat dessen Woerter nie in known und sah deshalb immer nur
    die heutige Zahl - genau das, was Ajdin bemaengelt hat. Ein Zahlwort
    gilt jetzt auch als gelernt, wenn der Level zahlen hinter dem Lernenden
    liegt: bestanden, ein spaeterer Level bestanden, oder die Einstufung
    beginnt dahinter. Wie "vorher" in kachelnFuerLektion()."""
    import datetime
    tag = datetime.date.today().isoformat()
    alle = [[5, 6, 7, 8, 9, 10, 11, 12], [30, 40, 50, 60, 70, 80, 90, 100]]
    keine = [[None], [None]]
    ziehen = """() => {
      const satz = t => SENTENCES.find(x => x.text === t);
      const alle = s => [...new Set(Array.from({length: 300}, () => zahlZiehen(s)))].sort((a, b) => a - b);
      return [alle(satz('Sada je ___ sati.')), alle(satz('Jakna košta ___ maraka.'))];
    }"""
    for mehr, soll in (({"einstufung": {"tag": tag, "wahl": "gut", "bis": "arbeitsvertrag"}}, alle),
                       ({"einstufung": {"tag": tag, "wahl": "etwas", "bis": "farben"}}, alle),
                       ({"bestanden": ["basics", "zahlen"]}, alle),
                       ({"bestanden": ["farben"]}, alle),               # spaeterer Level bestanden
                       ({"einstufung": {"tag": tag, "wahl": "etwas", "bis": "zahlen"}}, keine),   # beginnt AM Level zahlen
                       ({"bestanden": ["basics"]}, keine)):
        seite.starten(stand=heute_stand(**mehr))
        _vorbereiten(seite, gelernt=False)
        assert seite.js("() => known.size") == 0
        assert seite.js(ziehen) == soll, mehr
    # Und in der Aufgabe selbst, eingestuft ohne ein einziges gelerntes Wort
    seite.starten(stand=heute_stand(einstufung={"tag": tag, "wahl": "gut", "bis": "arbeitsvertrag"}))
    _vorbereiten(seite, gelernt=False)
    gezogen = {seite.js(AUFGABE, ["kacheln", "zeit", "Sada je pet sati.", None])["v"] for _ in range(25)}
    assert None not in gezogen and len(gezogen) >= 3, gezogen
    assert seite.fehler == []


def test_ohne_aufnahme_bleibt_die_heutige_zahl(seite, heute_stand):
    """Die Web-Demo hat die Emir-Aufnahmen nicht: dort steht alles wie vor
    dem 25.10.2026 da, auch mit gelernten Zahlwoertern."""
    seite.starten(stand=heute_stand())
    seite.js("() => CATEGORIES.find(x => x.id === 'zahlen').words.forEach(w => known.add(w.id))")
    assert seite.js("() => [...SENTENCES, ...SATZBAU].filter(s => s.zahl).map(s => zahlZiehen(s))") == [None] * 36
    seite.js("() => { window.__gespielt = []; }")
    vorher = seite.js(AUFGABE, ["gap", "zeit", "Sada je ___ sati.", None])
    assert vorher["v"] is None and "Jetzt ist es fünf Uhr." in vorher["bedeutung"], vorher
    seite.js("""() => { const b = document.getElementById('lBody'); b.querySelector('#xIn').value = 'pet'; b.querySelector('#xCheck').click(); }""")
    seite.page.wait_for_function("() => !!document.querySelector('#lBody .loesung')")
    assert seite.js("() => document.querySelector('#lBody .loesung .lbs').textContent") == "Sada je pet sati."
    assert seite.fehler == []


def test_dva_plus_dva_su_cetiri_und_der_fortschritt_zieht_um(seite, heute_stand):
    alt, neu = "k:zahlen|Dva plus dva je četiri.", "k:zahlen|Dva plus dva su četiri."
    seite.starten(stand=heute_stand(topf={alt: {"typ": "kacheln", "n": 1, "z": 123}},
                                    stern={alt: {"z": 50, "r": 7}}))
    jetzt = seite.js("() => ({topf, stern, gespeichert: JSON.parse(localStorage.getItem('zmaj_stand'))})")
    assert jetzt["topf"] == {neu: {"typ": "kacheln", "n": 1, "z": 123}}
    assert jetzt["stern"] == {neu: {"z": 50, "r": 7}}
    assert jetzt["gespeichert"]["topf"] == jetzt["topf"] and jetzt["gespeichert"]["stern"] == jetzt["stern"]
    # Nach dem Neuladen: nichts wandert ein zweites Mal, nichts geht verloren
    seite.neu_laden()
    assert seite.js("() => [Object.keys(topf), Object.keys(stern)]") == [[neu], [neu]]
    # Die Aufgabe aus dem Topf: legen und richtig. Es war das zweite Mal
    # richtig (n war 1) - damit ist sie aus dem Topf, der Stern bleibt.
    _vorbereiten(seite)
    seite.js("""(k) => { openLevel(0); startLesson(); Lx.queue = [topfAufgabe(k, topf[k])]; Lx.i = 0; Lx.total = 1;
                 Lx.results = []; showLessonTask(); }""", neu)
    erg = seite.js(LOESEN, [True, False])
    assert erg["ok"] is True and erg["loesung"] == "Dva plus dva su četiri."
    assert erg["datei"] == "w2520.mp3" and erg["schluessel"] == neu
    assert seite.js("() => [Object.keys(topf), Object.keys(stern)]") == [[], [neu]]
    # Beide zugleich: wie bei den Woertern gilt der juengere Fehler, die Sterne verschmelzen
    seite.starten(stand=heute_stand(topf={alt: {"typ": "kacheln", "n": 0, "z": 300},
                                          neu: {"typ": "kacheln", "n": 1, "z": 200}},
                                    stern={alt: {"z": 40, "r": 9}, neu: {"z": 60, "r": 2}}))
    assert seite.js("() => [topf, stern]") == [{neu: {"typ": "kacheln", "n": 0, "z": 300}},
                                               {neu: {"z": 40, "r": 9}}]
    # Aus einer alten Sicherung ebenso
    datei = json.loads(seite.js("() => sicherungInhalt()"))
    datei["stand"].update({"topf": {alt: {"typ": "kacheln", "n": 0, "z": 77}}, "stern": {alt: {"z": 60, "r": 0}}})
    erg = seite.js("""async (text) => {
      frage = async () => true;
      await sicherungEinlesen(new File([text], 'sicherung.json', {type: 'application/json'}));
      return [topf, stern];
    }""", json.dumps(datei))
    assert erg == [{neu: {"typ": "kacheln", "n": 0, "z": 77}}, {neu: {"z": 60, "r": 0}}]
    assert seite.fehler == []
