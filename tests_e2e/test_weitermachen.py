# -*- coding: utf-8 -*-
"""Weitermachen-Knopf: das erste nicht bestandene Level (Ajdins Regel, 01.11.2026).

Ajdin am 01.11.2026: "ich bin level 10 das heisst level 1 bis 9 hab ich
fertig und wenn ich zb auf level 8 kurz eine lektion mache soll der knopf
trotzdem bei level 10 bleiben" und "wenn ein neues level dazu kommt wegen
einen update ... bin level 10 und es kommt ein neues level 5 hinzu dann
springt der button auf level 5 und erst wenn es fertig ist springt er
wieder auf level 10". Geprueft wird im echten Browser:
  - genau seine zwei Beispiele, auch nach dem Neuladen;
  - nach der Einstufung: das erste offene ab dem Einstieg, Lektionen davor
    aendern nichts;
  - bestanden: eins weiter; ganz am Ende das letzte Level;
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


def test_neues_level_5_durch_update_erst_dorthin_dann_zurueck_zu_10(seite, heute_stand):
    """Level 5 ist nicht bestanden, als haette ein Update es eingeschoben:
    der Knopf zeigt auf Level 5, Level 10 bleibt offen. Erst wenn Level 5
    bestanden ist, zeigt er wieder auf Level 10."""
    ids = _ids(seite, heute_stand)
    luecke = [x for n, x in enumerate(ids[:9]) if n != 4]
    seite.starten(stand=heute_stand(bestanden=luecke))
    _knopf_zeigt(seite, 4)
    assert seite.js(JETZT) == ["5"]
    assert seite.js("() => isUnlocked(9)") is True
    # Eine Lektion in Level 5 macht es noch nicht fertig
    _lektion_in(seite, 4)
    _knopf_zeigt(seite, 4)
    # Bestanden (Level-Test): zurueck zu Level 10, auch nach dem Neuladen
    seite.js("async () => { passed.add(CATEGORIES[4].id); await saveProgress(); }")
    _knopf_zeigt(seite, 9)
    assert seite.js(JETZT) == ["10"]
    seite.neu_laden()
    _knopf_zeigt(seite, 9)
    assert seite.fehler == []


def test_bestanden_geht_eins_weiter(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    seite.starten(stand=heute_stand(bestanden=ids[:9]))
    seite.js("() => { passed.add(CATEGORIES[9].id); }")
    _knopf_zeigt(seite, 10)
    assert seite.fehler == []


def test_nach_der_einstufung_ab_dem_einstieg(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    eingestuft = {"einstufung": {"tag": datetime.date.today().isoformat(), "wahl": "gut", "bis": ids[10]}}
    seite.starten(stand=eingestuft)
    _knopf_zeigt(seite, 10)
    seite.starten(stand=dict(eingestuft, bestanden=[ids[10], ids[11]]))
    _knopf_zeigt(seite, 12)
    # Die uebersprungenen Level vor dem Einstieg holen den Knopf nicht zurueck
    _lektion_in(seite, 3)
    _knopf_zeigt(seite, 12)
    assert seite.fehler == []


def test_neuer_nutzer_und_ganz_am_ende(seite, heute_stand):
    ids = _ids(seite, heute_stand)
    _knopf_zeigt(seite, 0)
    # Alles bestanden: das letzte Level
    seite.starten(stand=heute_stand(bestanden=ids))
    _knopf_zeigt(seite, len(ids) - 1)
    assert seite.fehler == []
