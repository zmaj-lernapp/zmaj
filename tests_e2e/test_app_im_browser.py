# -*- coding: utf-8 -*-
"""Die App im Browser: starten, lernen, lesen, Sprache wechseln.

Jeder Test beginnt mit einem eigenen, leeren Browserkontext. Was hier
gespeichert wird, ist der Geraetemodus - genau der Weg, den die App auf dem
Handy nimmt (kein /api/konto, Stand in localStorage)."""
import pytest

# Bewusst ausgeschrieben statt aus sprachen.py: kommt eine Sprache dazu,
# soll sie hier mit Absicht dazukommen (und test_repository merkt den Rest).
SPRACHEN = ("de", "en", "tr", "sv", "nl", "nb", "da", "fr")


@pytest.mark.parametrize("sprache", SPRACHEN)
def test_startet_in_jeder_sprache(seite, sprache):
    """Startet ohne Skriptfehler, zeigt alle 65 Level und keine Werbung.
    Die Demo legt beide Werbeschalter um (demo_bauen.py); stuende einer
    noch, saehe man auf der Webseite Platzhalter-Anzeigen."""
    seite.starten(sprache=sprache)
    zustand = seite.js("""() => ({
        sprache: SPRACHE, level: CATEGORIES.length, echt: WERBUNG_ECHT, erlaubt: werbungErlaubt(),
        pfad: document.getElementById('pfad').style.display,
        texte: Object.keys(T).length })""")
    assert zustand["sprache"] == sprache
    assert zustand["level"] == 65
    assert zustand["echt"] is False
    assert zustand["erlaubt"] is False
    assert zustand["pfad"] == "block"
    assert zustand["texte"] > 100
    assert seite.fehler == []
    assert seite.fremd == [], "Anfragen an fremde Server: %s" % seite.fremd


def test_lektion_im_ersten_level(seite, heute_stand):
    """Eine ganze Lektion, alles richtig: Ergebnis erscheint, kein Herz geht
    verloren, und die neuen Woerter sind nach dem Neuladen noch da."""
    seite.starten(stand=heute_stand())
    vorher = seite.js("() => { openLevel(0); startLesson(); return {leben: livesNow(), woerter: known.size}; }")
    assert vorher["woerter"] == 0
    typen = seite.durchspielen("lBody", "Lx")
    assert "intro" in typen
    ergebnis = seite.js("""() => ({
        ende: !!document.getElementById('lMore'),
        richtig: Lx.right,
        gewertet: Lx.results.filter(r => r !== 'intro' && r !== 'skip').length,
        leben: livesNow(), woerter: known.size })""")
    assert ergebnis["ende"], "kein Ergebnisschirm nach der Lektion"
    assert ergebnis["gewertet"] > 0
    assert ergebnis["richtig"] == ergebnis["gewertet"]
    assert ergebnis["leben"] == vorher["leben"]
    assert ergebnis["woerter"] > 0

    seite.neu_laden()
    assert seite.js("() => known.size") == ergebnis["woerter"]
    assert seite.js("() => days.size") == 1        # heute gelernt
    assert seite.fehler == []


def test_leveltest_bestehen(seite, heute_stand):
    """Alle Woerter von Level 1 gekannt, Test komplett richtig: bestanden,
    und das bleibt nach dem Neuladen so."""
    seite.starten(stand=heute_stand())
    erste = seite.js("""() => {
        CATEGORIES[0].words.forEach(w => known.add(w.id));
        openLevel(0);
        if(!testAllowed(cur())) return 'Test nicht frei';
        startTest(); return CATEGORIES[0].id; }""")
    assert erste != "Test nicht frei"
    seite.durchspielen("tBody", "Tx")
    ergebnis = seite.js("""() => ({right: Tx.right, n: Tx.qs.length, bestanden: passed.has(cur().id),
                                    weiter: !!document.getElementById('tNext')})""")
    assert ergebnis["n"] == 10
    assert ergebnis["right"] == ergebnis["n"]
    assert ergebnis["bestanden"]
    assert ergebnis["weiter"], "kein Knopf zum naechsten Level"

    seite.neu_laden()
    assert seite.js("id => passed.has(id)", erste)
    assert seite.fehler == []


def test_geschichte_wort_antippen(seite, heute_stand):
    """Erste Geschichte oeffnen, ein Wort mit Eintrag antippen: die Blase
    zeigt das Wort und seine Bedeutung."""
    seite.starten(stand=heute_stand())
    wort = seite.js("""() => {
        openStory(0);
        const s = STORIES[0];
        const w = [...document.querySelectorAll('#rBody .w')].find(x => lookup(x.textContent, s));
        if(!w) return null;
        return {wort: w.textContent, bedeutung: lookup(w.textContent, s)}; }""")
    assert wort, "kein Wort mit Eintrag in der ersten Geschichte"
    assert seite.js("() => document.getElementById('rBubble').hidden") is True
    seite.page.locator("#rBody .w", has_text=wort["wort"]).first.click()
    blase = seite.page.locator("#rBubble")
    blase.wait_for(state="visible")
    text = blase.inner_text()
    assert wort["wort"] in text
    assert wort["bedeutung"] in text
    assert seite.fehler == []


def test_sprachwechsel_behaelt_fortschritt(seite, heute_stand):
    """Erst Deutsch lernen, dann auf Englisch wechseln: Woerter, bestandene
    Level und Lerntage bleiben, auch nach dem Neuladen. Die Kennung eines
    Wortes ist sprachunabhaengig (AGENTS.md, Regel 1)."""
    seite.starten(sprache="de", stand=heute_stand())
    vorher = seite.js("""() => {
        CATEGORIES[0].words.forEach(w => known.add(w.id)); passed.add(CATEGORIES[0].id);
        saveProgress(); return {woerter: known.size, level: passed.size, wort: CATEGORIES[0].words[0].de}; }""")
    assert vorher["woerter"] > 0
    seite.js("async () => { await setzeSprache('en'); }")
    nachher = seite.js("() => ({sprache: SPRACHE, woerter: known.size, level: passed.size, wort: CATEGORIES[0].words[0].de})")
    assert nachher["sprache"] == "en"
    assert nachher["woerter"] == vorher["woerter"]
    assert nachher["level"] == vorher["level"]
    assert nachher["wort"] != vorher["wort"], "Bedeutung nicht uebersetzt"

    seite.neu_laden()
    neu = seite.js("() => ({sprache: SPRACHE, woerter: known.size, level: passed.size})")
    assert neu == {"sprache": "en", "woerter": vorher["woerter"], "level": vorher["level"]}
    assert seite.fehler == []
