# -*- coding: utf-8 -*-
"""Weitermachen-Knopf: dort weiter, wo man zuletzt aufgehoert hat.

Ajdin am 01.11.2026: "kann dieser weiter machen button in der app nicht da
weiter machen wo man am weitesten ist sondern da wo man als letztes
aufgehoert hat". Hier, was sich ohne Browser pruefen laesst: das neue Feld
letzte_lektion steht ueberall, wo ein Feld des Lernstands stehen muss,
gemerkt wird nur in echten Lektionen, und der Knopf fragt weiterZiel()
statt firstOpen(). Das Verhalten selbst - altes Level, fertiges Level,
neuer Nutzer, Cloud - prueft tests_e2e/test_weitermachen.py im echten
Browser."""
import re


def _html(index_html):
    return index_html.replace("\r\n", "\n")


def _rumpf(html, kopf):
    """Der Rumpf einer Funktion auf oberster Ebene, bis zur ersten Zeile "}"."""
    assert html.count(kopf) == 1, kopf
    return html.split(kopf)[1].split("\n}\n")[0]


def test_eigenes_feld_ueberall_dabei(index_html):
    """Ein eigenes Feld auf oberster Ebene (Regel bei STAND_FELDER), und das
    ueberall: Geraetespeicher und Sicherungsdatei (standAlsObjekt), Einlesen
    (standUebernehmen, sicherungPlausibel), Cloud (standZusammenfuehren)."""
    html = _html(index_html)
    felder = re.search(r"const STAND_FELDER = new Set\(\[(.*?)\]\);", html, re.S).group(1)
    # Die alten Felder unveraendert davor, das neue hinten angehaengt
    assert felder.replace("\n", " ").endswith("'stern', 'kartei', 'letzte_lektion'")
    assert "          letzte_lektion: letzteLektion};\n" in html
    assert "  letzteLektion = letzteLektionPruefen(d.letzte_lektion);\n" in html
    assert "  p.letzte_lektion = letzteLektionPruefen(s.letzte_lektion);\n" in html
    mischen = _rumpf(html, "function standZusammenfuehren(a, b, cloudVorher){")
    assert ("const la = letzteLektionPruefen(a.letzte_lektion), "
            "lb = letzteLektionPruefen(b.letzte_lektion);") in mischen
    assert "m.letzte_lektion = " in mischen
    # Startwert: nichts gemerkt - dann wie bisher
    assert "\nlet letzteLektion = null;" in html


def test_nur_echte_lektionen_merken(index_html):
    """Gemerkt wird beim Beginnen (startLesson) und Beenden (lessonEnd) einer
    Lektion - nicht im Level-Test, in den Runden, in der Einstufung oder bei
    den Geschichten."""
    html = _html(index_html)
    assert html.count("letzteLektionMerken(") == 3          # die Funktion und zwei Aufrufe
    start = _rumpf(html, "function startLesson(){")
    # erst nach den Waechtern (Anmeldung, keine Leben): dann laeuft sie wirklich
    assert start.index("letzteLektionMerken(); saveProgress();") > start.index("buildLesson();")
    assert start.index("buildLesson();") > start.index("if(livesNow()===0)")
    ende = _rumpf(html, "function lessonEnd(){")
    # eine Runde (Lx.topf) geht vorher nach topfEnde() und merkt nichts
    assert ende.index("letzteLektionMerken();") > ende.index("if(Lx && Lx.topf){ topfEnde(); return; }")
    for kopf in ("function startTest(){", "function showTestQ(){", "function showTestResult(){",
                 "function rundeStarten(quelle){", "function topfEnde(){", "function einstufungStarten(){",
                 "function einstufungEnde(){", "function openStory(i){", "function openLevel(i){"):
        assert "letzteLektion" not in _rumpf(html, kopf), kopf
    # Gesetzt wird letzteLektion nur hier: Startwert, Merken, Uebernehmen, Einstufung
    zuweisungen = re.findall(r"(?<![.\w])letzteLektion = ([^;]*);", html)
    assert sorted(zuweisungen) == sorted(["null", "{level: c.id, z: Date.now()}",
                                          "letzteLektionPruefen(d.letzte_lektion)", "null"]), zuweisungen
    einstufung = _rumpf(html, "function einstufungMerken(wahl, bis, richtig, fragen){")
    assert "  letzteLektion = null;\n  saveProgress();" in einstufung


def test_knopf_fragt_weiterziel(index_html):
    """Nur der Knopf im Lernpfad aendert sich. Die Markierung "jetzt dran" im
    Pfad und die Farbe der Sektion bleiben beim ersten offenen Level."""
    html = _html(index_html)
    hero = _rumpf(html, "function renderHero(){")
    assert "const i = weiterZiel(), c = CATEGORIES[i];" in hero
    assert "firstOpen()" not in hero
    # Wiederholen und Geschichten wie bisher
    assert "if(topfAnzahl() && livesNow() > 0){ name = t('topf.titel'); hin = startTopf; }" in hero
    assert "let si = STORIES.findIndex(s => !read.has(s.id));" in hero
    assert "const next = firstOpen();" in _rumpf(html, "function showPath(){")
    assert "(CATEGORIES[firstOpen()] || {}).sektion" in _rumpf(html, "function sektionsFarbe(){")


def test_regel_wie_entschieden(index_html):
    html = _html(index_html)
    assert _rumpf(html, "function weiterZiel(){") == (
        "\n  const i = letzteLektion ? CATEGORIES.findIndex(c => c.id === letzteLektion.level) : -1;"
        "\n  if(i < 0 || !isUnlocked(i)) return firstOpen();"
        "\n  if(!passed.has(CATEGORIES[i].id)) return i;"
        "\n  const k = CATEGORIES.findIndex((c, n) => n > i && !passed.has(c.id) && isUnlocked(n));"
        "\n  return k < 0 ? firstOpen() : k;")
    pruefen = _rumpf(html, "function letzteLektionPruefen(roh){")
    assert "roh.level.length > 200" in pruefen
    assert "Math.min(roh.z, Date.now())" in pruefen          # nichts aus der Zukunft


def test_kein_neuer_text(index_html):
    """Der Knopf traegt weiter btn.weitermachen und den Namen des Levels."""
    hero = _rumpf(_html(index_html), "function renderHero(){")
    assert "k.textContent = '▶ ' + t('btn.weitermachen') + ' · ' + name;" in hero
