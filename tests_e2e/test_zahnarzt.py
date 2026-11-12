# -*- coding: utf-8 -*-
"""Der versteckte Teil Beim Zahnarzt im Browser (06.11.2026).

Festgelegt: siebenmal auf die Versionszeile, dann das Wort "zahnarzt". Danach steht der
Teil als eigene Sektion im Lernpfad, der Lernstand geht mit dem Konto, und in den normalen
Zahlen taucht er nicht auf. Ohne das Wort merkt niemand etwas.

Geprueft wird:
  - ohne das Wort: keine Sektion, kein Feld gesetzt;
  - Freischalten (Gross/klein egal) und wieder ausblenden, der Lernstand bleibt;
  - ein falsches Wort verraet nichts und aendert nichts;
  - das Wort schaltet keine Vollversion frei; das Wort des Dauerschalters (hier ein
    Testwort, eingesetzt wie beim Bauen, siehe test_haut_alle.py) arbeitet unveraendert;
  - Lektion und Test im Teil enthalten nichts aus dem Lernpfad, und Level, Woerter,
    Lerntage, Wegmarken, Tagesaufgaben, Muenzen, Weitermachen, Kartei, Topf und Sterne
    bleiben, wie sie waren;
  - der Lernstand uebersteht Neuladen und Neuinstallation (ueber das Konto).
"""
import json
import os
import shutil

import pytest

TEST_WORT = "Probewort fuer die Vollversion"
SEKTION = '#sections .section[data-sid="zahnarzt"]'

# Alles, was im Lernpfad zaehlt. Darf sich durch den Teil nie aendern.
ZAHLEN = """() => ({
    sektionen: SECTIONS.length, level: CATEGORIES.length, woerter: alleWoerter(),
    gewusst: ohneZa(known), bestanden: ohneZa(passed),
    summary: document.getElementById('summary').textContent,
    weiter: document.getElementById('weiterKnopf').textContent,
    firstOpen: firstOpen(), hoechster: hoechsterBestanden(),
    tage: days.size, rekord, gefeiert: [...gefeiert].sort(), serie: streak(),
    topf: topfAnzahl(), stern: sternAnzahl(), kartei: Object.keys(kartei.w).length,
    karteiHeute: karteiHeute().length, einstufung: einstufungFaellig(),
    neu: neuNochMoeglich(), premium, dauer: dauerVoll,
    geschichten: STORIES.length, satzbau: SATZBAU.length, saetze: SENTENCES.length,
    tagwerk: JSON.stringify(tagwerk), muenzen: muenzenGes,
    wortkarte: !!wortNachId('za|vilica')})"""


@pytest.fixture(scope="module")
def probe_html(wurzelordner, tmp_path_factory):
    """Die Demo mit dem Pruefwert des Testworts, wie app_bauen.py ihn einsetzt."""
    import app_bauen
    import dauer_wort_setzen

    ordner = tmp_path_factory.mktemp("zahnarztprobe")
    kopie = ordner / "index.html"
    shutil.copyfile(os.path.join(wurzelordner, "app", "index.html"), str(kopie))
    datei = ordner / "dauer_pruefwert.txt"
    datei.write_text(dauer_wort_setzen.pruefwert(TEST_WORT) + "\n", encoding="utf-8")
    app_bauen.dauer_einsetzen(str(kopie), str(datei))
    html = kopie.read_bytes()
    assert b"__DAUER_PRUEFWERT__" not in html
    return html


@pytest.fixture
def probe(seite, probe_html):
    seite.page.route("**/app/index.html", lambda r: r.fulfill(
        status=200, content_type="text/html; charset=utf-8", body=probe_html))
    return seite


def _wort(seite, wort):
    """Einstellungen auf, siebenmal auf die Versionszeile, Wort eingeben."""
    if not seite.page.locator("#ueberZeile").is_visible():
        seite.page.locator("#btnSettings").click()
    for _ in range(7):
        seite.page.locator("#ueberZeile").click()
    seite.page.locator("#frWort").fill(wort)
    seite.page.locator("#frOk").click()


def _ruhe(seite):
    """Wartet, bis eine laufende Wortpruefung sicher fertig ist."""
    seite.js("async () => { await dauerWortStimmt('x'); await new Promise(r => setTimeout(r, 300)); }")


def _freischalten(seite):
    _wort(seite, "zahnarzt")
    seite.page.wait_for_function("() => zaAn()")


def _heim(seite):
    seite.js("() => { homeMode = 'words'; showHome(); }")


def _gespeichert(seite):
    return seite.js("async () => { await saveProgress(); return JSON.parse(localStorage.getItem('zmaj_stand')); }")


def _lektion_durch(seite, k=0):
    """Eine Lektion in Level k des Teils, alles richtig."""
    seite.js("(k) => { openLevel(CATEGORIES.length + k); startLesson(); }", k)
    return seite.durchspielen("lBody", "Lx")


def _level_bestehen(seite, k=0):
    """Das ganze Level k: Lektionen bis zum Test, dann der Test."""
    for _ in range(12):
        _lektion_durch(seite, k)
        if seite.js("() => testAllowed(cur())"):
            break
    assert seite.js("() => testAllowed(cur())")
    seite.js("() => startTest()")
    seite.durchspielen("tBody", "Tx")


# ------------------------------------------------------------- ohne Wort ---

def test_ohne_wort_ist_nichts_zu_sehen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _heim(seite)
    assert seite.page.locator(SEKTION).count() == 0
    z = seite.js(ZAHLEN)
    assert z["sektionen"] == 31 and z["level"] == 295 and z["woerter"] == 7997 and z["wortkarte"] is False
    assert seite.js("() => [zaAn(), zaSchalter.an, !!ZA, standAlsObjekt().zahnarzt.an]") == [False, False, True, False]
    assert seite.js("() => document.querySelector('#sections').textContent.includes('Beim Zahnarzt')") is False
    # Kein eigener Eintrag im Geraetespeicher, und nichts laedt nach
    schluessel = seite.js("() => Object.keys(localStorage).filter(k => /zahn|za_/i.test(k))")
    assert schluessel == []
    assert seite.fehler == [] and seite.fremd == []


def test_sieben_tipps_reichen_und_sechs_nicht(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.page.locator("#btnSettings").click()
    for _ in range(6):
        seite.page.locator("#ueberZeile").click()
    assert seite.page.locator("#frWort").count() == 0
    seite.page.locator("#ueberZeile").click()
    assert seite.page.locator("#frWort").count() == 1
    seite.page.locator("#frAb").click()
    assert seite.js("() => zaAn()") is False
    assert seite.fehler == []


# ---------------------------------------------------------- Freischalten ---

@pytest.mark.parametrize("wort", ["zahnarzt", "  Zahnarzt ", "ZAHNARZT"])
def test_freischalten(seite, heute_stand, wort):
    seite.starten(stand=heute_stand())
    _wort(seite, wort)
    seite.page.wait_for_function("() => zaAn()")
    # Eine kurze Meldung statt eines Erklaertexts, und kein Kasten bleibt stehen
    assert seite.page.locator(".kurznote").inner_text() == "✓ Beim Zahnarzt"
    assert seite.page.locator(".nachfrage").count() == 0
    stand = _gespeichert(seite)
    assert stand["zahnarzt"]["an"] is True and stand["zahnarzt"]["z"] > 0
    _heim(seite)
    # Am Ende des Lernpfads, aufgeklappt, mit sieben Leveln und eigener Farbe
    e = seite.js("""() => {
        const alle = [...document.querySelectorAll('#sections .section')];
        const s = alle[alle.length - 1];
        return {id: s.dataset.sid, anzahl: alle.length, zu: s.classList.contains('zu'),
                titel: s.querySelector('h2').textContent, level: s.querySelectorAll('.node').length,
                gesperrt: s.querySelectorAll('.node.locked').length, jetzt: s.querySelectorAll('.node.current').length,
                nummer: s.querySelector('.node .circle').textContent, farbe: sektionsNummer(s.dataset.sid),
                offen: !s.classList.contains('locked')};
    }""")
    # Seit den Paketen 10 bis 20 (07.11.2026) die 32. Sektion: 31 im Lernpfad, die Farbe reihum
    assert e == {"id": "zahnarzt", "anzahl": 32, "zu": False, "titel": "Beim Zahnarzt", "level": 7,
                 "gesperrt": 6, "jetzt": 1, "nummer": "1", "farbe": "5", "offen": True}
    assert seite.fehler == [] and seite.fremd == []


def test_level_oeffnen_und_blaettern(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _freischalten(seite)
    _heim(seite)
    seite.page.locator(SEKTION + " .node").first.click()
    assert seite.page.locator("#levelView").is_visible()
    kopf = seite.js("""() => ({tag: document.getElementById('tag').textContent,
        titel: document.getElementById('lvTitle').textContent,
        zurueck: document.getElementById('navPrev').disabled, weiter: document.getElementById('navNext').disabled,
        imZa: imZa(), woerter: cur().words.length})""")
    assert kopf["tag"] == "Level 1 von 7" and kopf["titel"].startswith("Level 1 · Zähne und Mund"), kopf
    # Ohne Umbruch im Namen der Sektion: er stand sonst halb in der Zeile, halb darunter.
    # 20 Eintraege seit dem 07.11.2026: zubno meso kam mit Wort und Satz von der Warteliste.
    assert "Beim Zahnarzt" in kopf["titel"] and kopf["imZa"] is True and kopf["woerter"] == 20, kopf
    # Vor dem ersten Level kommt nichts aus dem Lernpfad, das zweite ist noch zu
    assert kopf["zurueck"] is True and kopf["weiter"] is True, kopf
    assert seite.js("() => [isUnlocked(CATEGORIES.length), isUnlocked(CATEGORIES.length + 1)]") == [True, False]
    # Wer die Ansicht verlaesst, ist nicht mehr im Teil
    _heim(seite)
    assert seite.js("() => imZa()") is False
    # Vom letzten Level des Lernpfads geht es nicht in den versteckten Teil
    seite.js("() => { passed.add(CATEGORIES[CATEGORIES.length - 2].id); openLevel(CATEGORIES.length - 1); }")
    assert seite.js("() => document.getElementById('navNext').disabled") is True
    assert seite.fehler == []


def test_ausblenden_und_lernstand_bleibt(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _freischalten(seite)
    seite.js("() => { known.add('za|vilica'); passed.add('za|zaehne'); }")
    # Abbrechen laesst ihn an
    _wort(seite, "zahnarzt")
    seite.page.locator("#frNein").click()
    _ruhe(seite)
    assert seite.js("() => zaAn()") is True
    # Ausblenden: weg aus dem Lernpfad, der Lernstand steht noch da
    _wort(seite, "zahnarzt")
    seite.page.locator("#frJa").click()
    seite.page.wait_for_function("() => !zaAn()")
    _heim(seite)
    assert seite.page.locator(SEKTION).count() == 0
    assert seite.js("() => offeneSektion !== 'zahnarzt'") is True
    stand = _gespeichert(seite)
    assert stand["zahnarzt"]["an"] is False and "za|vilica" in stand["gewusst"] and "za|zaehne" in stand["bestanden"]
    # Wieder an: alles noch da
    _freischalten(seite)
    _heim(seite)
    assert seite.page.locator(SEKTION + " .node.done").count() == 1
    assert seite.fehler == []


# --------------------------------------------------------- falsches Wort ---

@pytest.mark.parametrize("wort", ["zahnaerztin", "zahn", "zubar", "dragon", "", "za|"])
def test_falsches_wort_verraet_nichts(probe, heute_stand, wort):
    probe.starten(stand=heute_stand())
    vorher = probe.js(ZAHLEN)
    stand_vorher = _gespeichert(probe)
    _wort(probe, wort)
    _ruhe(probe)
    # Kein Kasten, keine Meldung, kein Wort darueber, ob es fast gepasst haette
    assert probe.page.locator(".nachfrage").count() == 0
    assert probe.page.locator(".kurznote").count() == 0
    assert probe.js("() => [zaAn(), premium, dauerVoll, localStorage.getItem('zmaj_dauer2')]") == [False, False, False, None]
    assert probe.js(ZAHLEN) == vorher
    assert _gespeichert(probe) == stand_vorher
    assert probe.fehler == []


# ----------------------------------------------------------- kein Premium ---

def test_codewort_schaltet_keine_vollversion_frei(probe, heute_stand):
    probe.starten(stand=heute_stand())
    aus = "() => [premium, dauerVoll, unlimited(), localStorage.getItem('zmaj_dauer2'), localStorage.getItem('zmaj_voll')]"
    leer = probe.js(aus)
    assert leer[:3] == [False, False, False]
    _freischalten(probe)
    assert probe.js(aus) == leer
    # Auch ueber die Pruefung des geheimen Worts nicht, und am Laden auch nicht
    assert probe.js("async () => await dauerWortStimmt('zahnarzt')") is False
    probe.js("() => { festHeute = () => ''; }")
    _heim(probe)
    probe.page.locator("#btnShop").click()
    probe.page.locator("#ladenKopf").click()
    probe.page.locator('#ladenListe .sprachzeile[data-gruppe="farbe"]').click()
    for _ in range(7):
        probe.page.locator("#ladenTitel").click()
    probe.page.locator("#frWort").fill("zahnarzt")
    probe.page.locator("#frOk").click()
    _ruhe(probe)
    assert probe.js(aus) == leer
    assert probe.js("() => [hautAlle, localStorage.getItem('zmaj_hautalle')]") == [False, None]
    # Das Feld im Stand schaltet nichts: ein Stand mit "an" allein bleibt ohne Vollversion
    assert "premium" not in _gespeichert(probe)
    assert probe.fehler == []


def test_wort_des_dauerschalters_arbeitet_unveraendert(probe, heute_stand):
    probe.starten(stand=heute_stand())
    _freischalten(probe)
    # Ein: nur die Vollversion, der Teil bleibt, wie er ist
    _wort(probe, TEST_WORT)
    probe.page.wait_for_function("() => localStorage.getItem('zmaj_dauer2') === '1'")
    assert probe.js("() => [premium, dauerVoll, zaAn()]") == [True, True, True]
    # Aus: mit Rueckfrage wie bisher, der Teil bleibt
    _wort(probe, TEST_WORT)
    probe.page.locator("#frJa").click()
    probe.page.wait_for_function("() => localStorage.getItem('zmaj_dauer2') === '0'")
    assert probe.js("() => [premium, dauerVoll, zaAn()]") == [False, False, True]
    # Das Codewort schaltet den Dauerschalter nicht um, auch wenn er an ist
    _wort(probe, TEST_WORT)
    probe.page.wait_for_function("() => localStorage.getItem('zmaj_dauer2') === '1'")
    _wort(probe, "zahnarzt")
    probe.page.locator("#frNein").click()
    _ruhe(probe)
    assert probe.js("() => [premium, dauerVoll, zaAn()]") == [True, True, True]
    assert probe.fehler == []


def test_sicherung_und_cloud_bringen_keine_vollversion(seite, heute_stand):
    """Das Feld kommt von aussen wie jeder Stand: es schaltet den Teil, sonst nichts."""
    seite.starten(stand=heute_stand(zahnarzt={"an": True, "z": 1000}))
    assert seite.js("() => [zaAn(), premium, dauerVoll, unlimited()]") == [True, False, False, False]
    assert seite.js("() => standZusammenfuehren({}, {zahnarzt: {an: true, z: 5}, premium: true}).premium") is None
    assert "premium" not in _gespeichert(seite)
    assert seite.fehler == []


@pytest.mark.parametrize("roh", ["ja", 1, True, ["an"], {"an": "ja", "z": 5}, {"an": 1}, {"z": "x"}, {}])
def test_kaputtes_feld_heisst_aus(seite, heute_stand, roh):
    seite.starten(stand=heute_stand(zahnarzt=roh))
    assert seite.js("() => zaAn()") is False
    assert seite.fehler == []


# -------------------------------------------- Lektion und Test im Teil ---

def test_lektion_enthaelt_nur_den_teil(seite, heute_stand):
    """Auch nicht die Saetze aus bestandenen Leveln und die faelligen Woerter der Kartei,
    die sonst in jede Lektion kommen."""
    seite.starten(stand=heute_stand())
    ids = seite.js("() => CATEGORIES.slice(0, 40).map(c => c.id)")
    woerter = seite.js("() => CATEGORIES.slice(0, 5).flatMap(c => c.words.map(w => w.id))")
    tag = seite.js("() => karteiTag()")
    seite.starten(stand=heute_stand(bestanden=ids, gewusst=woerter, zahnarzt={"an": True, "z": 1000},
                                    kartei={"tag": tag, "n": 0, "w": {i: [1, tag - 1, tag - 2] for i in woerter[:30]}}))
    assert seite.js("() => karteiHeute().length") > 0
    for k in range(7):
        seite.js("(k) => { openLevel(CATEGORIES.length + k); buildLesson(); }", k)
        e = seite.js("""() => ({arten: [...new Set(Lx.queue.map(a => a.typ))],
            fremd: Lx.queue.filter(a => !a.w || !a.w.id.startsWith('za|')).length,
            hier: Lx.queue.every(a => cur().words.includes(a.w)),
            faellig: Lx.queue.filter(a => a.faellig).length})""")
        assert e["fremd"] == 0 and e["faellig"] == 0 and e["hier"] is True, (k, e)
        assert not {"gap", "kacheln", "gram"} & set(e["arten"]), (k, e)
    # Die Auswahl zeigt nur Antworten aus dem Teil, solange er genug hat
    falsch = seite.js("""() => { const c = cur();
        return c.words.flatMap(w => distractors(w, c.words, 3)).filter(x => !x.id.startsWith('za|')).length; }""")
    assert falsch == 0
    assert seite.fehler == []


def test_lektion_zaehlt_im_teil_und_sonst_nirgends(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _freischalten(seite)
    _heim(seite)
    vorher = seite.js(ZAHLEN)
    typen = _lektion_durch(seite)
    assert typen and "gap" not in typen and "kacheln" not in typen
    im_teil = seite.js("""() => ({pct: levelPct(cur()), neu: Lx.newWords.size,
        gewusst: [...known].filter(istZa).length, stern: document.getElementById('lStern').hidden})""")
    assert im_teil["neu"] > 0 and im_teil["gewusst"] == im_teil["neu"] and im_teil["pct"] > 0
    assert im_teil["stern"] is True
    # Das Ergebnis meldet keinen Lerntag
    assert seite.js("() => t('lektion.heute_geuebt')") not in seite.page.locator("#lBody").inner_text()
    # Ein Fehler im Teil: kein Stern, kein Fehler-Topf, keine Kartei
    falsch = seite.js("""() => { const task = {typ: 'mc', w: zaLevel()[0].words[0]};
        topfMerken(task, false); karteiAntwort(task, false);
        return [topfSchluessel(task), topfAnzahl(), Object.keys(kartei.w).length]; }""")
    assert falsch == ["", vorher["topf"], vorher["kartei"]]
    _heim(seite)
    assert seite.js(ZAHLEN) == vorher
    assert seite.fehler == [] and seite.fremd == []


def test_level_bestehen_oeffnet_das_naechste_im_teil(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _freischalten(seite)
    _heim(seite)
    vorher = seite.js(ZAHLEN)
    _level_bestehen(seite)
    ergebnis = seite.page.locator("#tBody").inner_text()
    assert "Level 1 · Zähne und Mund" in ergebnis and "alles" not in ergebnis.lower()
    assert seite.page.locator("#tNext").inner_text() == seite.js("() => t('test.weiter_level', {n: 2})")
    # Kein Rueckblick auf Woerter aus dem Lernpfad in den Testfragen
    assert seite.js("() => Tx.qs.every(q => q.w.id.startsWith('za|'))") is True
    seite.page.locator("#tNext").click()
    assert seite.js("() => [imZa(), cur().id, document.getElementById('tag').textContent]") == [
        True, "za|befund", "Level 2 von 7"]
    # Der Test des zweiten Levels fragt auch das erste ab, nie den Lernpfad
    seite.js("() => { buildTest(); }")
    assert seite.js("() => Tx.qs.every(q => q.w.id.startsWith('za|'))") is True
    _heim(seite)
    assert seite.page.locator(SEKTION + " .node.done").count() == 1
    assert seite.page.locator(SEKTION + " .node.locked").count() == 5
    # In den normalen Zahlen: nichts
    jetzt = seite.js(ZAHLEN)
    assert jetzt == vorher
    assert "za|zaehne" in seite.js("() => [...passed]")
    assert seite.fehler == [] and seite.fremd == []


def test_ganz_fertig_feiert_nichts_aus_dem_lernpfad(seite, heute_stand):
    """Wer alles im Lernpfad bestanden hat, bekommt beim Teil kein "alles geschafft"."""
    seite.starten(stand=heute_stand())
    alle = seite.js("() => CATEGORIES.map(c => c.id)")
    seite.starten(stand=heute_stand(bestanden=alle, zahnarzt={"an": True, "z": 1000}))
    vorher = seite.js(ZAHLEN)
    assert vorher["firstOpen"] == 294      # das letzte der 295 Level (seit 07.11.2026)
    # Bis auf das letzte Level des Teils
    seite.js("() => { zaLevel().slice(0, -1).forEach(c => passed.add(c.id)); }")
    seite.js("() => { openLevel(CATEGORIES.length + 6); cur().words.forEach(w => known.add(w.id)); showLevelHome(); startTest(); }")
    seite.durchspielen("tBody", "Tx")
    e = seite.js("""() => ({text: document.getElementById('tBody').textContent,
        weiter: !!document.getElementById('tNext'), kicker: !!document.querySelector('#tBody .kicker')})""")
    assert e["weiter"] is False and e["kicker"] is False, e
    assert seite.js("() => t('test.sektion_fertig')") in e["text"]
    assert seite.js(ZAHLEN)["firstOpen"] == 294
    assert seite.fehler == []


def test_lernstand_im_teil_zaehlt_nicht_als_gelernt(seite, heute_stand):
    """Wer nur den Teil gelernt hat, ist fuer den Lernpfad noch am Anfang: die Einstufung
    und die Zahlen sehen nichts davon."""
    gewusst = ["za|vilica", "za|živac"]
    seite.starten(stand={"gewusst": gewusst, "bestanden": ["za|zaehne"], "zahnarzt": {"an": True, "z": 1000}})
    z = seite.js("() => ({gewusst: ohneZa(known), bestanden: ohneZa(passed), einstufung: einstufungFaellig(), roh: known.size})")
    assert z == {"gewusst": 0, "bestanden": 0, "einstufung": True, "roh": 2}
    _heim(seite)
    assert seite.js("() => document.getElementById('summary').textContent") == (
        "0 von 295 Levels geschafft · 0 von 7997 Wörtern sitzen")
    assert seite.fehler == []


def test_kennungen_werden_nie_auf_ein_wort_des_lernpfads_umgeschrieben(seite, heute_stand):
    """zubar steht im Lernpfad und im Teil. Die Regel fuers Umbenennen darf das nicht verwechseln."""
    teil = ["za|zubar / stomatolog", "za|vilica", "za|plomba", "za|karijes"]
    seite.starten(stand=heute_stand(gewusst=teil + ["zahnarzt:zubar"], zahnarzt={"an": True, "z": 1000}))
    j = seite.js("() => ({known: [...known].sort(), kartei: Object.keys(kartei.w), geaendert: altenFortschrittUmschreiben()})")
    assert j["known"] == sorted(teil + ["zahnarzt:zubar"]) and j["geaendert"] is False
    assert j["kartei"] == ["zahnarzt:zubar"], "der Teil kommt nicht in die Kartei"
    assert seite.js("() => zaLevel()[0].words[0].id") == "za|zubar / stomatolog"
    assert seite.fehler == []


# ------------------------------------------------------------ Lernstand ---

def test_lernstand_uebersteht_neuladen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    _freischalten(seite)
    _lektion_durch(seite)
    gewusst = seite.js("() => [...known].filter(istZa).sort()")
    assert gewusst
    seite.js("async () => { await saveProgress(); }")
    seite.neu_laden()
    assert seite.js("() => [...known].filter(istZa).sort()") == gewusst
    assert seite.js("() => zaAn()") is True
    _heim(seite)
    assert seite.page.locator(SEKTION).count() == 1
    assert seite.fehler == []


ADAPTER = """(dok) => { window.ablage = dok ? {dok} : {}; window.adapter = cloudSpeicherAdapter(window.ablage); return true; }"""
ANMELDEN = "async () => await cloudAnmelden('anonym', adapter)"


def test_lernstand_geht_mit_dem_konto_und_uebersteht_neuinstallation(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js(ADAPTER, None)
    assert seite.js(ANMELDEN) is True
    _freischalten(seite)
    _level_bestehen(seite)
    gewusst = seite.js("() => [...known].filter(istZa).sort()")
    assert gewusst and seite.js("() => passed.has('za|zaehne')") is True
    assert seite.js("async () => await cloudAbgleich('anmelden', adapter)") == "gespeichert"
    dok = seite.js("() => ablage.dok")
    im_konto = json.loads(dok["text"])["stand"]
    assert im_konto["zahnarzt"]["an"] is True and set(gewusst) <= set(im_konto["gewusst"])
    assert "za|zaehne" in im_konto["bestanden"]

    # Neu installiert: leerer Geraetespeicher, kein Teil, dann anmelden
    seite.starten(stand=heute_stand())
    assert seite.js("() => zaAn()") is False
    seite.js(ADAPTER, dok)
    assert seite.js(ANMELDEN) is True
    assert seite.js("() => zaAn()") is True
    assert seite.js("() => [...known].filter(istZa).sort()") == gewusst
    assert seite.js("() => passed.has('za|zaehne')") is True
    _heim(seite)
    assert seite.page.locator(SEKTION + " .node.done").count() == 1
    # Und bleibt nach dem Neuladen
    seite.js("async () => { await saveProgress(); }")
    seite.neu_laden()
    assert seite.js("() => [zaAn(), [...known].filter(istZa).length]") == [True, len(gewusst)]
    assert seite.fehler == []


def test_zwei_geraete_die_letzte_wahl_gilt(seite, heute_stand):
    seite.starten(stand=heute_stand())
    mischen = "([a, b]) => standZusammenfuehren({zahnarzt: a}, {zahnarzt: b}).zahnarzt"
    an, aus = {"an": True, "z": 1000}, {"an": False, "z": 2000}
    assert seite.js(mischen, [an, aus]) == aus and seite.js(mischen, [aus, an]) == aus
    # Gleiche Zeit: "an", damit beide Richtungen dasselbe ergeben
    gleich = {"an": False, "z": 1000}
    assert seite.js(mischen, [an, gleich]) == an and seite.js(mischen, [gleich, an]) == an
    # Fehlt das Feld (Stand von vorher), bleibt es aus; kaputt ebenso
    assert seite.js("() => standZusammenfuehren({}, {}).zahnarzt") == {"an": False, "z": 0}
    assert seite.js(mischen, [None, an]) == an
    # Aus der Zukunft: gekappt, gewinnt also keinen spaeteren Abgleich
    z = seite.js(mischen, [{"an": True, "z": 1e18}, {"an": False, "z": 5}])
    assert z["an"] is True and z["z"] <= seite.js("() => Date.now()")
    assert seite.fehler == []


# -------------------------------------------------------------- Sprachen ---

def test_uebersetzt_und_bosnisch_bleibt(seite, heute_stand):
    seite.starten(stand=heute_stand(zahnarzt={"an": True, "z": 1000}), sprache="en")
    seite.js("() => { offeneSektion = 'zahnarzt'; homeMode = 'words'; showHome(); }")
    assert seite.page.locator(SEKTION + " h2").inner_text() == "At the dentist"
    e = seite.js("() => zaLevel()[0].words[2]")
    assert e == {"de": "jaw", "bs": "vilica", "id": "za|vilica"}
    # Sprache wechseln, ohne dass der Teil verschwindet
    seite.js("async () => { await setzeSprache('de'); }")
    assert seite.js("() => zaLevel()[0].words[2].de") == "Kiefer"
    assert seite.js("() => zaAn()") is True
    assert seite.fehler == []
