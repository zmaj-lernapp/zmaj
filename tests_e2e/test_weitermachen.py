# -*- coding: utf-8 -*-
"""Weitermachen-Knopf: immer das Level ganz vorn (01.11.2026).

Ajdin am 01.11.2026: "ich bin level 10 das heisst level 1 bis 9 hab ich
fertig und wenn ich zb auf level 8 kurz eine lektion mache soll der knopf
trotzdem bei level 10 bleiben". Geprueft wird im echten Browser:
  - genau sein Beispiel, auch nach dem Neuladen;
  - eine Luecke hinter einem (ein Update schiebt ein Level ein): der Knopf
    bleibt vorn, die Luecke bleibt offen, auch wenn man darin uebt;
  - nach der Einstufung: mindestens der Einstieg;
  - bestanden: eins weiter; ganz am Ende die Luecke, sonst das letzte Level;
  - der Lernpfad markiert dasselbe Level als "Jetzt dran".
Die Pruefungen ohne Browser stehen in tests/test_weitermachen.py.
"""
import datetime

KNOPF = """() => { homeMode = 'words'; showHome(); const k = document.getElementById('weiterKnopf');
  return k.style.display === 'none' ? null : k.textContent; }"""
LEVEL = "() => CATEGORIES.map(c => c.id)"
NAME = "(i) => '▶ ' + t('btn.weitermachen') + ' · ' + CATEGORIES[i].label"
# Die Nummern im Kreis der Level, die der Lernpfad als "Jetzt dran" markiert
JETZT = """() => { homeMode = 'words'; showHome();
  return [...document.querySelectorAll('#sections .node.current .circle')].map(n => n.textContent); }"""


def _ids(seite, heute_stand):
    seite.starten(stand=heute_stand())
    return seite.js(LEVEL)


def _knopf_zeigt(seite, i):
    assert seite.js(KNOPF) == seite.js(NAME, i), (seite.js(KNOPF), i)


def _lektion_in(seite, i):
    """Eine ganze Lektion im Level i, ueber den Lernpfad zurueck."""
    seite.js("(i) => openLevel(i)", i)
    seite.page.click("#btnLesson")
    seite.durchspielen("lBody", "Lx")
    assert seite.js("() => !!document.getElementById('lMore')"), "kein Ergebnisschirm"
    seite.page.click("#lPfad")


def test_ajdins_beispiel_level_8_ueben_knopf_bleibt_bei_10(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    seite.starten(stand=heute_stand(bestanden=ids[:9]))
    _knopf_zeigt(seite, 9)
    assert seite.js(JETZT) == ["10"]
    _lektion_in(seite, 7)
    assert seite.js("() => document.getElementById('weiterKnopf').textContent") == seite.js(NAME, 9)
    _knopf_zeigt(seite, 9)
    # Der Knopf oeffnet Level 10
    seite.page.click("#weiterKnopf")
    assert seite.js("() => [catIdx, sichtbar('levelView'), sichtbar('levelHome')]") == [9, True, True]
    seite.neu_laden()
    _knopf_zeigt(seite, 9)
    assert seite.js(JETZT) == ["10"]
    assert seite.fehler == []


def test_abgebrochene_lektion_im_alten_level_aendert_nichts(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    seite.starten(stand=heute_stand(bestanden=ids[:9]))
    seite.js("() => { openLevel(2); startLesson(); lektionVerlassen(); }")
    _knopf_zeigt(seite, 9)
    seite.neu_laden()
    _knopf_zeigt(seite, 9)
    assert seite.fehler == []


def test_luecke_hinter_einem_knopf_bleibt_vorn(seite, heute_stand):
    """Level 5 fehlt, als haette ein Update es eingeschoben: frueher schickte
    der Knopf dorthin zurueck, jetzt bleibt er bei Level 10. Level 5 bleibt
    offen und laesst sich ueben - auch das bewegt den Knopf nicht."""
    ids = _ids(seite, heute_stand)
    luecke = [x for n, x in enumerate(ids[:9]) if n != 4]
    seite.starten(stand=heute_stand(bestanden=luecke))
    _knopf_zeigt(seite, 9)
    assert seite.js(JETZT) == ["10"]
    assert seite.js("() => [isUnlocked(4), passed.has(CATEGORIES[4].id)]") == [True, False]
    _lektion_in(seite, 4)
    _knopf_zeigt(seite, 9)
    assert seite.fehler == []


def test_bestanden_geht_eins_weiter(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    seite.starten(stand=heute_stand(bestanden=ids[:9]))
    seite.js("() => { passed.add(CATEGORIES[9].id); }")
    _knopf_zeigt(seite, 10)
    # Ein weiter vorn bestandenes Level (Testmodus) zieht den Knopf mit
    seite.js("() => { passed.add(CATEGORIES[14].id); }")
    _knopf_zeigt(seite, 15)
    assert seite.fehler == []


def test_nach_der_einstufung_mindestens_der_einstieg(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    eingestuft = {"einstufung": {"tag": datetime.date.today().isoformat(), "wahl": "gut", "bis": ids[10]}}
    seite.starten(stand=eingestuft)
    _knopf_zeigt(seite, 10)
    seite.starten(stand=dict(eingestuft, bestanden=[ids[10], ids[11]]))
    _knopf_zeigt(seite, 12)
    _lektion_in(seite, 3)
    _knopf_zeigt(seite, 12)
    assert seite.fehler == []


def test_neuer_nutzer_und_ganz_am_ende(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    _knopf_zeigt(seite, 0)
    # Alles bestanden bis auf eine Luecke: dann in die Luecke
    seite.starten(stand=heute_stand(bestanden=[x for n, x in enumerate(ids) if n != 4]))
    _knopf_zeigt(seite, 4)
    # Alles bestanden: das letzte Level, wie bisher
    seite.starten(stand=heute_stand(bestanden=ids))
    _knopf_zeigt(seite, len(ids) - 1)
    assert seite.fehler == []
