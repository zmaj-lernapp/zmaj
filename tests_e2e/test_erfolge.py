# -*- coding: utf-8 -*-
"""Erfolge (13.11.2026): 18 Abzeichen, still sichtbar.

Ajdin am 13.11.2026 zu Release\\Entscheidungen_2026-11-13\\erfolge.md:
"alles wie empfohlen" (8a, 9b, 10a).
  - 18 Abzeichen: Lerntage, Flamme (laengste Serie), Woerter, Stufen A1 bis
    B1, Geschichten, "Fest im Kopf".
  - Rueckwirkend aus vorhandenen Daten; einmal "Du hast schon N Abzeichen",
    und alle gelten als gesehen.
  - Ein verdientes bleibt fuer immer.
  - Wand im Profil, Leiste auf der Startseite (3 neueste + "x von 18"),
    ruhige Zeile am Lektionsende. Feier-Karte und Konfetti nur bei
    Lerntagen - hier also nie.
  - Kein neues Feld im Stand: "e:<id>" in gefeiert, Datum in wann, mit
    allen 18 hoechstens etwa 0,5 KB mehr.
  - Texte in allen acht Sprachen.
"""
import datetime
import json

import pytest

SPRACHEN = ["de", "en", "tr", "sv", "nl", "nb", "da", "fr"]
APP_START = datetime.date(2026, 8, 1)

# Woerter, Level und Geschichten aus der laufenden App. Die Woerter erst ab
# Level 6, damit eine Lektion in Level 1 neue dazubringt.
DATEN = """() => {
  const w = [...new Set(CATEGORIES.slice(5).flatMap(c => c.words.map(x => x.id)))];
  return {woerter: w.slice(0, 150),
          a1: CATEGORIES.filter(c => levelStufe(c) === 'A1').map(c => c.id),
          story: STORIES[0].id};
}"""

ZUSTAND = """() => ({
  verdient: ERFOLGE.filter(erfolgVerdient).map(e => e.id),
  e: [...gefeiert].filter(x => x.startsWith('e:')).sort(),
  wann: Object.fromEntries(Object.entries(wann).filter(([k]) => k.startsWith('e:'))),
  gespeichert: JSON.parse(localStorage.getItem('zmaj_stand') || '{}'),
  gesehen: localStorage.getItem('zmaj_erfolge_gesehen'),
  leiste: (() => { const l = document.getElementById('erfolgLeiste');
    return {sichtbar: !l.hidden && l.offsetHeight > 0, text: l.innerText,
            ringe: [...l.querySelectorAll('.abzring')].map(r => r.className)}; })(),
  karte: !!document.querySelector('.nachfrage'),
  konfetti: document.querySelectorAll('.schnipsel').length,
})"""


def _tag(n):
    return (datetime.date.today() - datetime.timedelta(days=n)).isoformat()


def _daten(seite, heute_stand):
    seite.starten(stand=heute_stand())
    return seite.js(DATEN)


def _alter_stand(d, heute_stand):
    """Ein Stand von vor den Erfolgen: 31 Lerntage am Stueck bis gestern,
    120 Woerter, alle Level von A1 (mit Datum), eine Geschichte, 100 Woerter
    auf der 90-Tage-Stufe der Kartei. Kein Feld gefeiert - so sieht ein
    Stand von vor dem 19.09.2026 aus, die Wegmarken gelten als gefeiert."""
    kt = (datetime.date.today() - APP_START).days
    wann = {"lv:" + x: _tag(10) for x in d["a1"]}
    wann["gs:" + d["story"]] = _tag(20)
    return heute_stand(
        tage=[_tag(i) for i in range(1, 32)], gewusst=d["woerter"][:120],
        bestanden=d["a1"], gelesen=[d["story"]], wann=wann,
        kartei={"tag": 0, "n": 0, "w": {w: [5, kt + 40, kt - 1] for w in d["woerter"][:100]}})


def _kurznote(seite):
    seite.page.wait_for_function("() => !!document.querySelector('.kurznote')", timeout=5000)
    return seite.js("() => document.querySelector('.kurznote').textContent")


def test_rueckwirkend_beim_ersten_start(seite, heute_stand):
    """Wer das Update bekommt, hat seine Abzeichen sofort - einmal der Satz,
    alle gesehen, nichts gefeiert. Datum nur, wo es sich nachrechnen laesst;
    bei den Woertern und der Kartei erfindet die App keins."""
    d = _daten(seite, heute_stand)
    seite.starten(stand=_alter_stand(d, heute_stand))
    assert _kurznote(seite) == "Du hast schon 7 Abzeichen"
    z = seite.js(ZUSTAND)
    assert sorted(z["verdient"]) == sorted(["t7", "t30", "f30", "w100", "a1", "g1", "k100"]), z["verdient"]
    # Datum: Stufe = spaetestes Level, Woerter und Kartei rueckwirkend ohne
    assert z["wann"] == {"e:a1": _tag(10)}, z["wann"]
    # gespeichert, und zwar in den vorhandenen Feldern
    g = z["gespeichert"]
    assert {"e:" + x for x in z["verdient"]} <= set(g["gefeiert"])
    assert g["wann"]["e:a1"] == _tag(10)
    assert "erfolge" not in g and "abzeichen" not in g
    # alles gesehen, keine Karte, kein Konfetti
    assert sorted(json.loads(z["gesehen"])) == sorted(z["verdient"])
    assert not z["karte"] and z["konfetti"] == 0
    # Leiste: "7 von 18", die drei neuesten - Flamme und 1 Monat (vorgestern,
    # bei gleichem Datum das spaetere der Liste zuerst), dann A1 - ohne Punkt
    assert z["leiste"]["sichtbar"], z["leiste"]
    assert "Erfolge" in z["leiste"]["text"] and "7 von 18" in z["leiste"]["text"]
    ringe = z["leiste"]["ringe"]
    assert len(ringe) == 3, ringe
    assert "k-flamme" in ringe[0] and "k-tage" in ringe[1] and "k-stufen" in ringe[2], ringe
    assert not any(" neu" in r or " aus" in r for r in ringe), ringe
    # Die Daten aus tage, frost und gs:
    daten = seite.js("() => Object.fromEntries(ERFOLGE.filter(erfolgVerdient).map(e => [e.id, erfolgDatum(e)]))")
    assert daten == {"t7": _tag(25), "t30": _tag(2), "f30": _tag(2), "w100": "", "a1": _tag(10),
                     "g1": _tag(20), "k100": ""}, daten
    # Beim naechsten Start kein Satz mehr
    seite.neu_laden()
    seite.page.wait_for_timeout(400)
    assert seite.js("() => !!document.querySelector('.kurznote')") is False
    assert seite.js(ZUSTAND)["verdient"] == z["verdient"]
    assert seite.fehler == [] and seite.fremd == []


def test_frisch_installiert_dann_cloud(seite, heute_stand):
    """Neues Handy, altes Konto: vor der Anmeldung ist der Stand leer, und
    das Geraet merkt sich noch nichts. Kommt der Stand dann aus der Cloud,
    zaehlt das wie ein Update - einmal der Satz, alles gesehen, kein
    erfundenes Datum, kein roter Punkt."""
    d = _daten(seite, heute_stand)
    seite.starten(stand=heute_stand())
    z = seite.js(ZUSTAND)
    assert z["verdient"] == [] and z["gesehen"] is None, z
    assert "0 von 18" in z["leiste"]["text"]
    # Die Wand ueber die Leiste oeffnen aendert daran nichts
    seite.js("() => document.getElementById('erfolgLeiste').click()")
    seite.page.wait_for_function("() => !document.getElementById('erfolgWand').hidden", timeout=3000)
    assert seite.js(ZUSTAND)["gesehen"] is None
    # Der Stand kommt (wie nach cloudAbgleich), dann die Startseite
    seite.js("(s) => { standUebernehmen(s); showHome(); }", _alter_stand(d, heute_stand))
    assert _kurznote(seite) == "Du hast schon 7 Abzeichen"
    z = seite.js(ZUSTAND)
    assert sorted(z["verdient"]) == sorted(["t7", "t30", "f30", "w100", "a1", "g1", "k100"]), z["verdient"]
    assert z["wann"] == {"e:a1": _tag(10)}, z["wann"]
    assert sorted(json.loads(z["gesehen"])) == sorted(z["verdient"])
    assert not any(" neu" in r for r in z["leiste"]["ringe"]), z["leiste"]
    assert not z["karte"] and z["konfetti"] == 0
    assert seite.fehler == [] and seite.fremd == []


def test_lektion_bringt_neues_abzeichen(seite, heute_stand):
    """99 Woerter, eine Lektion in Level 1: am Ende die ruhige Zeile
    "Neues Abzeichen: 100 Woerter sitzen", Datum heute, kein Konfetti. Auf
    der Startseite traegt es den roten Punkt, bis die Wand offen war."""
    d = _daten(seite, heute_stand)
    seite.starten(stand=heute_stand(gewusst=d["woerter"][:99]))
    z = seite.js(ZUSTAND)
    assert z["verdient"] == [] and z["gesehen"] == "[]"
    # Noch keins: grau das naechste, "0 von 18"
    assert "0 von 18" in z["leiste"]["text"] and len(z["leiste"]["ringe"]) == 1
    assert " aus" in z["leiste"]["ringe"][0] and "k-woerter" in z["leiste"]["ringe"][0]
    seite.js("() => { openLevel(0); startLesson(); }")
    seite.durchspielen("lBody", "Lx")
    ende = seite.js("""() => { const z = document.querySelector('#lBody .erfolgzeile');
      return z ? {text: z.innerText, ringe: z.querySelectorAll('.abzring').length} : null; }""")
    assert ende, "keine Zeile am Lektionsende"
    assert "Neues Abzeichen: 100 Wörter sitzen" in ende["text"] and "Im Profil" in ende["text"]
    assert ende["ringe"] == 1
    z = seite.js(ZUSTAND)
    assert z["verdient"] == ["w100"]
    assert z["wann"] == {"e:w100": datetime.date.today().isoformat()}
    assert "e:w100" in z["gespeichert"]["gefeiert"]
    assert not z["karte"] and z["konfetti"] == 0
    seite.page.wait_for_timeout(1600)          # die Wegmarke kaeme nach 1,4 s
    assert seite.js("() => !!document.querySelector('.nachfrage')") is False
    # Zurueck: der rote Punkt in der Leiste
    seite.js("() => document.getElementById('lPfad').click()")
    z = seite.js(ZUSTAND)
    assert "1 von 18" in z["leiste"]["text"]
    assert len(z["leiste"]["ringe"]) == 1 and " neu" in z["leiste"]["ringe"][0]
    # Die Wand: ueber die Leiste, ohne Konto ohne den Kontokasten
    seite.js("() => document.getElementById('erfolgLeiste').click()")
    seite.page.wait_for_function("() => document.getElementById('kontoView').style.display !== 'none'", timeout=3000)
    wand = seite.js("""() => { const w = document.getElementById('erfolgWand');
      return {sichtbar: !w.hidden, knoepfe: w.querySelectorAll('.abz').length,
              an: [...w.querySelectorAll('.abz:not(.offen)')].map(b => b.dataset.erfolg),
              neu: [...w.querySelectorAll('.abzring.neu')].length,
              balken: [...w.querySelectorAll('.abzbalken')].length,
              kopf: w.querySelector('.abzstand').textContent,
              konto: document.getElementById('kontoKasten').hidden}; }""")
    assert wand == {"sichtbar": True, "knoepfe": 18, "an": ["w100"], "neu": 1, "balken": 6,
                    "kopf": "1 von 18", "konto": True}, wand
    # Antippen: Satz und Datum, nochmal antippen: weg
    info = seite.js("""() => { const b = document.querySelector('#erfolgWand [data-erfolg="w100"]'); b.click();
      return b.closest('.abzgruppe').querySelector('.abzinfo').textContent; }""")
    heute = seite.js("() => new Date(today() + 'T12:00:00').toLocaleDateString('de')")
    assert info == "100 Wörter sitzen · geschafft am " + heute, info
    offen = seite.js("""() => { const b = document.querySelector('#erfolgWand [data-erfolg="w500"]'); b.click();
      return b.closest('.abzgruppe').querySelector('.abzinfo').textContent; }""")
    assert offen.startswith("500 Wörter sitzen · ") and offen.endswith(" / 500"), offen
    # Gesehen: zurueck auf der Startseite ohne Punkt
    seite.js("() => showHome()")
    assert not any(" neu" in r for r in seite.js(ZUSTAND)["leiste"]["ringe"])
    assert seite.fehler == [] and seite.fremd == []


def test_verdient_bleibt_fuer_immer(seite, heute_stand):
    """Faellt die Zahl dahinter - die Kartei nach Fehlern, weniger Woerter
    in einem eingelesenen Stand -, bleibt das Abzeichen."""
    d = _daten(seite, heute_stand)
    seite.starten(stand=_alter_stand(d, heute_stand))
    z = seite.js("""() => {
      Object.keys(kartei.w).forEach(id => { kartei.w[id][0] = 0; });
      standUebernehmen(Object.assign(standAlsObjekt(), {gewusst: [], bestanden: []}));
      showHome();
      return {verdient: ERFOLGE.filter(erfolgVerdient).map(e => e.id),
              kopf: festImKopf(), woerter: known.size}; }""")
    assert z["kopf"] == 0 and z["woerter"] == 0
    assert sorted(z["verdient"]) == sorted(["t7", "t30", "f30", "w100", "a1", "g1", "k100"]), z
    assert seite.fehler == []


def test_zusammenfuehren_und_platz(seite, heute_stand):
    """Zwei Geraete: verdient ist, was eines verdient hat; das Datum ist das
    fruehere. Und alle 18 zusammen kosten im Stand hoechstens 0,5 KB."""
    seite.starten(stand=heute_stand())
    m = seite.js("""() => standZusammenfuehren(
        {gefeiert: ['tage7', 'e:w100'], wann: {'e:w100': '2026-11-01'}},
        {gefeiert: ['e:t7'], wann: {'e:w100': '2026-10-30', 'e:a1': '2026-10-02'}})""")
    assert m["gefeiert"] == ["e:t7", "e:w100", "tage7"]
    assert m["wann"] == {"e:a1": "2026-10-02", "e:w100": "2026-10-30"}
    platz = seite.js("""() => {
      const vorher = utf8Laenge(JSON.stringify(standAlsObjekt()));
      ERFOLGE.forEach(e => { gefeiert.add(ERFOLG_VORN + e.id); if(e.merken) wann[ERFOLG_VORN + e.id] = '2026-11-13'; });
      return utf8Laenge(JSON.stringify(standAlsObjekt())) - vorher; }""")
    assert 0 < platz <= 512, platz
    assert seite.fehler == []


def test_zahnarzt_und_stufen(seite, heute_stand):
    """Woerter beim Zahnarzt zaehlen nicht. Jede Sektion bis "Wie, wo und
    wann" hat eine der Stufen A1, A2, B1, ab B2 keine davon; Saetze bauen
    ist geteilt (heute ueber SAETZE_A1, mit den Stufen-Reitern als zwei
    Sektionen "saetze" und "saetze2" mit eigenem Feld stufe)."""
    seite.starten(stand=heute_stand())
    z = seite.js("""() => {
      known = new Set(Array.from({length: 120}, (_, i) => 'za|wort' + i));
      const w100 = ERFOLGE.find(e => e.id === 'w100');
      const bisB1 = SECTIONS.slice(0, SECTIONS.findIndex(s => s.id === 'wiewowann') + 1).map(s => s.id);
      const mitAbz = st => ['A1', 'A2', 'B1'].includes(st);
      const lv = CATEGORIES.map(c => [c.sektion, levelStufe(c)]);
      return {wert: erfolgStand(w100).wert, erreicht: erfolgErreicht(w100),
              ohne: lv.filter(([s, st]) => bisB1.includes(s) && !mitAbz(st)).length,
              danach: lv.filter(([s, st]) => !bisB1.includes(s) && mitAbz(st)).length,
              saetze: [...new Set(lv.filter(([s]) => s.startsWith('saetze')).map(([, st]) => st))].sort(),
              stufen: ['A1', 'A2', 'B1'].map(s => erfolgStufenLevel(s).length)}; }""")
    assert z["wert"] == 0 and z["erreicht"] is False
    assert z["ohne"] == 0 and z["danach"] == 0
    assert z["saetze"] == ["A1", "A2"]
    assert all(n > 0 for n in z["stufen"]), z["stufen"]
    assert seite.fehler == []


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_alle_sprachen(seite, heute_stand, sprache):
    """In jeder Sprache: kein nackter Schluessel, kein offener Platzhalter,
    nichts ragt bei 360 px ueber den Rand."""
    d = _daten(seite, heute_stand)
    seite.starten(sprache=sprache, stand=_alter_stand(d, heute_stand))
    note = _kurznote(seite)
    leiste = seite.js("() => document.getElementById('erfolgLeiste').innerText")
    seite.js("() => document.getElementById('erfolgLeiste').click()")
    seite.page.wait_for_function("() => !document.getElementById('erfolgWand').hidden", timeout=3000)
    wand = seite.js("""() => { const w = document.getElementById('erfolgWand');
      w.querySelectorAll('.abz').forEach(b => b.click());   // jede Gruppe zeigt ihren letzten Satz
      return {text: w.innerText, breit: document.documentElement.scrollWidth,
              raus: [...w.querySelectorAll('.abz, .abzinfo')].filter(e => e.getBoundingClientRect().right > 361).length}; }""")
    zeile = seite.js("""() => { known = new Set(); ERFOLGE.forEach(e => gefeiert.delete(ERFOLG_VORN + e.id));
      return erfolgZeile(); }""")
    for text in (note, leiste, wand["text"], zeile):
        assert "erfolg." not in text and "{" not in text, (sprache, text)
    assert "7" in note and "18" in leiste
    assert wand["breit"] <= 360 and wand["raus"] == 0, (sprache, wand)
    assert seite.fehler == [] and seite.fremd == []
