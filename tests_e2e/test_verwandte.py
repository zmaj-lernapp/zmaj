# -*- coding: utf-8 -*-
"""Verwandte im Level Familie (23.10.2026), in der App.

Ajdin: "tetka ujna strina fuer die verschiedenen tanten und striko ujak
amidza=stric tetak daidza=ujak usw". Vier Woerter haben dabei eine neue
Kennung bekommen (Bedeutung UND Wort, inhalt.py). Ein alter Stand muss beim
Start und beim Einlesen einer Sicherung ueberall mitwandern: gewusst,
Fehler-Topf und Sterne. Die Koseformen striko, adžo, ujo und dajo zaehlen
beim Tippen; getippt wird amidža heute in der Luecke "Moj ___ je pčelar.".
"""
import json

UMBENANNT = {
    "tante:tetka": "tante (schwester von vater oder mutter):tetka",
    "onkel (vaterseite):amidža": "onkel (bruder des vaters):amidža / stric",
    "onkel (mutterseite):daidža": "onkel (bruder der mutter):daidža / ujak",
    "cousin:rođak": "cousin, verwandter (allgemein):rođak",
}
NEUE_WOERTER = [
    "onkel (mann der tante):tetak",
    "tante (frau des onkels väterlicherseits):strina / amidžinica",
    "tante (frau des onkels mütterlicherseits):ujna / daidžinica",
    "cousin (sohn des onkels väterlicherseits):amidžić / brat od amidže",
    "cousine (tochter des onkels väterlicherseits):amidžična / sestra od amidže",
    "cousin (sohn des onkels mütterlicherseits):daidžić / brat od daidže",
    "cousine (tochter des onkels mütterlicherseits):daidžična / sestra od daidže",
    "cousin (sohn der tante):tetić / brat od tetke",
    "cousine (tochter der tante):tetična / sestra od tetke",
    "cousine, verwandte (allgemein):rođaka / rođakinja",
    "neffe:nećak",
    "nichte:nećakinja",
]
AMIDZA = UMBENANNT["onkel (vaterseite):amidža"]
TETKA = UMBENANNT["tante:tetka"]


def _gespeichert(seite):
    return seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand'))")


def test_alle_neuen_kennungen_gibt_es(seite, heute_stand):
    seite.starten(stand=heute_stand())
    erg = seite.js("""([alt, neu]) => ({
        alt: alt.filter(id => !!wortNachId(id)),
        fehlt: neu.filter(id => !wortNachId(id)),
        ziel: alt.map(id => UMBENANNT[id]) })""", [list(UMBENANNT), list(UMBENANNT.values()) + NEUE_WOERTER])
    assert erg == {"alt": [], "fehlt": [], "ziel": list(UMBENANNT.values())}
    assert seite.fehler == []


def test_alter_stand_wandert_beim_start(seite, heute_stand):
    topf = {"w:onkel (vaterseite):amidža": {"typ": "type", "n": 1, "z": 123},
            "w:tante:tetka": {"typ": "type", "n": 0, "z": 124}}
    stern = {"w:cousin:rođak": {"z": 50, "r": 7}, "w:onkel (mutterseite):daidža": {"z": 51, "r": 0}}
    seite.starten(stand=heute_stand(gewusst=list(UMBENANNT) + ["brot:hljeb"], topf=topf, stern=stern))
    jetzt = seite.js("() => ({known: [...known], topf, stern})")
    for alt, neu in UMBENANNT.items():
        assert neu in jetzt["known"] and alt not in jetzt["known"], alt
    assert "brot:hljeb" in jetzt["known"], "Unbeteiligtes bleibt"
    assert jetzt["topf"] == {"w:" + AMIDZA: topf["w:onkel (vaterseite):amidža"],
                             "w:" + TETKA: topf["w:tante:tetka"]}
    assert jetzt["stern"] == {"w:" + UMBENANNT["cousin:rođak"]: {"z": 50, "r": 7},
                              "w:" + UMBENANNT["onkel (mutterseite):daidža"]: {"z": 51, "r": 0}}
    # Gleich gespeichert, nicht erst bei der naechsten Antwort
    d = _gespeichert(seite)
    assert sorted(set(d["gewusst"]) & set(UMBENANNT)) == []
    assert d["topf"] == jetzt["topf"] and d["stern"] == jetzt["stern"]
    # Wiederholen: amidža / stric kommt als Auswahl (Woerter mit " / " nie
    # als Tippaufgabe), tetka weiter zum Tippen
    nach = seite.js("""(ks) => { homeMode = 'topf'; showHome();
        return {anzahl: topfAnzahl(), aufgaben: ks.map(k => { const a = topfAufgabe(k, topf[k]); return a && [a.typ, a.w.bs]; })}; }""",
                    ["w:" + AMIDZA, "w:" + TETKA])
    assert nach == {"anzahl": 2, "aufgaben": [["mcrev", "amidža / stric"], ["type", "tetka"]]}
    # Neu laden: nichts wandert ein zweites Mal, nichts geht verloren
    seite.neu_laden()
    assert seite.js("() => [[...known].filter(k => k.indexOf('vaterseite') >= 0).length, Object.keys(topf).length, Object.keys(stern).length]") == [0, 2, 2]
    assert seite.fehler == []


def test_alte_sicherung_wandert_beim_einlesen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    datei = json.loads(seite.js("() => sicherungInhalt()"))
    datei["stand"].update({"gewusst": list(UMBENANNT),
                           "topf": {"w:tante:tetka": {"typ": "mc", "n": 0, "z": 77}},
                           "stern": {"w:onkel (vaterseite):amidža": {"z": 60, "r": 0}}})
    erg = seite.js("""async (text) => {
      frage = async () => true;
      await sicherungEinlesen(new File([text], 'sicherung.json', {type: 'application/json'}));
      return {known: [...known], topf, stern};
    }""", json.dumps(datei))
    assert sorted(erg["known"]) == sorted(UMBENANNT.values())
    assert erg["topf"] == {"w:" + TETKA: {"typ": "mc", "n": 0, "z": 77}}
    assert erg["stern"] == {"w:" + AMIDZA: {"z": 60, "r": 0}}
    assert seite.fehler == []


def test_koseformen_zaehlen_beim_tippen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const a = wortNachId('onkel (bruder des vaters):amidža / stric').w;
      const d = wortNachId('onkel (bruder der mutter):daidža / ujak').w;
      const m = (eingabe, w) => matches(eingabe, annehmbar(w).join(' / '));
      return {striko: m('striko', a), adzo: m('Adžo', a), stric: m('stric', a), amidza: m('amidža', a),
              ujo: m('ujo', d), dajo: m('dajo', d), ujak: m('ujak', d),
              quer: m('ujo', a), falsch: m('tetak', a), tippen: typable(a)};
    }""")
    assert erg == {"striko": "ok", "adzo": "ok", "stric": "ok", "amidza": "ok", "ujo": "ok", "dajo": "ok",
                   "ujak": "ok", "quer": "no", "falsch": "no", "tippen": False}
    assert seite.fehler == []


AUFGABE = """async ([art, eingabe]) => {
  const warte = ms => new Promise(r => setTimeout(r, ms));
  const i = CATEGORIES.findIndex(c => c.id === 'familie');
  openLevel(i); startLesson();
  const task = art === 'gap'
    ? {typ: 'gap', s: SENTENCES.find(x => x.text === 'Moj ___ je pčelar.')}
    : {typ: 'type', w: wortNachId('onkel (bruder des vaters):amidža / stric').w, pool: CATEGORIES[i].words};
  Lx.queue = [task]; Lx.i = 0; Lx.total = 1; Lx.right = 0; Lx.results = [];
  showLessonTask();
  await warte(250);
  const body = document.getElementById('lBody');
  body.querySelector('#xIn').value = eingabe;
  body.querySelector('#xCheck').click();
  await warte(150);
  return {richtig: Lx.right, ergebnis: Lx.results[0]};
}"""


def test_luecke_moj_striko_je_pcelar(seite, heute_stand):
    """Die Luecke ist die Stelle, an der amidža getippt wird."""
    seite.starten(stand=heute_stand())
    for eingabe, ok in (("striko", True), ("adžo", True), ("stric", True), ("amidža", True),
                        ("ujo", False)):
        erg = seite.js(AUFGABE, ["gap", eingabe])
        assert erg == {"richtig": 1 if ok else 0, "ergebnis": ok}, eingabe
    assert seite.fehler == []


def test_schreibaufgabe_mit_striko(seite, heute_stand):
    """Als Schreibaufgabe kommt amidža / stric nie (typable()) - gaebe es
    sie, zaehlte die Koseform auch dort."""
    seite.starten(stand=heute_stand())
    assert seite.js(AUFGABE, ["type", "striko"]) == {"richtig": 1, "ergebnis": True}
    assert seite.js(AUFGABE, ["type", "dajo"]) == {"richtig": 0, "ergebnis": False}
    assert seite.fehler == []


def test_neue_woerter_kommen_in_der_lektion(seite, heute_stand):
    """Alles andere im Level gewusst: die Lektion stellt neue Verwandte vor,
    fragt sie ab, und danach sind sie gelernt."""
    seite.starten(stand=heute_stand())
    vorher = seite.js("""(neu) => {
      const i = CATEGORIES.findIndex(c => c.id === 'familie');
      const offen = new Set(neu);
      CATEGORIES[i].words.forEach(w => { if(!offen.has(w.id)) known.add(w.id); });
      openLevel(i); startLesson();
      return Lx.queue.filter(q => q.typ === 'intro').map(q => q.w.id);
    }""", NEUE_WOERTER)
    assert vorher and set(vorher) <= set(NEUE_WOERTER), vorher
    seite.durchspielen("lBody", "Lx")
    # Gewusst ist ein neues Wort nach seiner richtig beantworteten Aufgabe -
    # eine uebersprungene Sprechaufgabe zaehlt nicht (DURCHSPIELEN ueberspringt sie).
    erg = seite.js("""() => ({ende: !!document.getElementById('lMore'), richtig: Lx.right,
        gewertet: Lx.results.filter(r => r !== 'intro' && r !== 'skip').length, known: [...known],
        beantwortet: Lx.queue.filter((q, i) => q.w && q.typ !== 'intro' && Lx.results[i] === true).map(q => q.w.id)})""")
    assert erg["ende"], "kein Ergebnisschirm"
    assert erg["gewertet"] > 0 and erg["richtig"] == erg["gewertet"]
    neu_beantwortet = [w for w in erg["beantwortet"] if w in NEUE_WOERTER]
    assert neu_beantwortet, erg["beantwortet"]
    for wid in neu_beantwortet:
        assert wid in erg["known"], wid
    assert seite.fehler == []
