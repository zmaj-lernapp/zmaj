# -*- coding: utf-8 -*-
"""Alle Muenz-Farben fuer uns (19.10.2026): siebenmal auf die Ueberschrift
"Laden", waehrend der Reiter Farben gewaehlt ist, dann das Wort des
Dauerschalters. Siehe hautAlleVerdrahten() in index.html.

Das echte Wort steht nirgends, auch hier nicht. Die Tests bauen sich eine
eigene Fassung der Demo mit dem Pruefwert eines Testworts - eingesetzt mit
app_bauen.dauer_einsetzen(), also genau so wie beim Bauen der App - und
liefern sie statt app/index.html aus.

Was hier im echten Browser nachgeprueft wird:
  - ein falsches Wort tut nichts, auch keins der anderen Woerter der
    Versionszeile; ohne eingesetzten Pruefwert (Web-Demo) tut auch das
    Testwort nichts;
  - das richtige Wort schaltet ein und, mit Rueckfrage, wieder aus;
  - eingeschaltet sind alle fuenf Muenz-Farben tragbar, ohne dass besitz
    oder Muenzen sich aendern; die Farben der Vollversion bleiben an
    unlimited() gebunden;
  - der Schalter steht weder im Lernstand noch in der Sicherungsdatei, und
    eine Sicherung schaltet ihn weder ein noch aus;
  - der Schalter an der Versionszeile arbeitet wie vorher und unabhaengig;
  - die Ueberschrift tut sonst nichts: andere Reiter, weniger als sieben
    Tipps, mehr als zwei Sekunden Pause; Reiterwahl und Kauf wie vorher.
"""
import json
import os
import shutil

import pytest

# Nur fuer diese Tests. Mit dem echten Wort hat es nichts zu tun.
TEST_WORT = "Probewort fuer alle Farben"
MUENZ_FARBEN = ["gruen", "rosa", "rot", "lila", "nacht"]
VOLL_FARBEN = ["gold", "silber", "kupfer", "galaxie"]
AN = "() => localStorage.getItem('zmaj_hautalle')"


@pytest.fixture(scope="module")
def probe_html(wurzelordner, tmp_path_factory):
    """Die Demo-Seite mit dem Pruefwert des Testworts."""
    import app_bauen
    import dauer_wort_setzen

    ordner = tmp_path_factory.mktemp("hautprobe")
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


def _laden(seite, reiter="farbe"):
    """Laden ueber den Einkaufswagen oeffnen, Reiter ueber die Aufklappliste."""
    seite.js("() => { festHeute = () => ''; }")
    seite.page.locator("#btnShop").click()
    seite.page.locator("#ladenKopf").click()
    seite.page.locator('#ladenListe .sprachzeile[data-gruppe="%s"]' % reiter).click()
    assert seite.js("() => ladenReiter") == reiter


def _tippen(seite, n=7, ziel="#ladenTitel"):
    for _ in range(n):
        seite.page.locator(ziel).click()


def _wort(seite, wort):
    seite.page.locator("#frWort").fill(wort)
    seite.page.locator("#frOk").click()


def _ruhe(seite):
    """Wartet, bis eine laufende Wortpruefung sicher fertig ist."""
    seite.js("async () => { await dauerWortStimmt('x'); await new Promise(r => setTimeout(r, 300)); }")


def _kasten(seite):
    return seite.page.locator(".nachfrage").count()


def _knoepfe(seite):
    """Je Farbe im Reiter: 'tragen', 'preis' oder 'voll'."""
    return seite.js("""() => {
        const ids = ZIERRAT.filter(w => w.gruppe === ladenReiter).map(w => w.id);
        return Object.fromEntries([...document.querySelectorAll('#ladenWaren .ware')].map((z, i) => {
            const b = z.querySelector('button');
            return [ids[i], b.dataset.tragen ? 'tragen' : b.dataset.ware ? 'preis' : 'voll'];
        }));
    }""")


def _einschalten(seite):
    _tippen(seite)
    _wort(seite, "  " + TEST_WORT.upper() + " ")      # getrimmt und klein, wie beim Dauerschalter
    seite.page.wait_for_function("() => localStorage.getItem('zmaj_hautalle') === '1'")


@pytest.mark.parametrize("wort", ["falsch", "kennung", ""])
def test_falsches_wort_tut_nichts(probe, heute_stand, wort):
    probe.starten(stand=heute_stand(muenzen_ges=5000))
    _laden(probe)
    vorher = _knoepfe(probe)
    _tippen(probe)
    assert probe.page.locator("#frWort").count() == 1, "nach sieben Tipps kommt die Eingabe"
    _wort(probe, wort)
    _ruhe(probe)
    assert _kasten(probe) == 0, "auch kein Kasten der Versionszeile (kennung)"
    assert probe.js(AN) is None
    assert probe.js("() => hautAlle") is False
    assert _knoepfe(probe) == vorher
    assert all(vorher[f] == "preis" for f in MUENZ_FARBEN)
    assert probe.fehler == []


def test_ohne_pruefwert_schaltet_das_wort_nichts(seite, heute_stand):
    """Web-Demo: dort steht nur der Platzhalter, kein Wort schaltet frei."""
    seite.starten(stand=heute_stand(muenzen_ges=5000))
    _laden(seite)
    _tippen(seite)
    _wort(seite, TEST_WORT)
    _ruhe(seite)
    assert seite.js(AN) is None
    assert _knoepfe(seite)["nacht"] == "preis"
    assert seite.fehler == []


def test_richtiges_wort_schaltet_ein_und_aus(probe, heute_stand):
    probe.starten(stand=heute_stand(muenzen_ges=5000, besitz=["gruen"]))
    _laden(probe)
    k = _knoepfe(probe)
    assert k["gruen"] == "tragen" and all(k[f] == "preis" for f in MUENZ_FARBEN[1:])

    _einschalten(probe)
    assert _kasten(probe) == 0, "eingeschaltet wird ohne Rueckfrage"
    k = _knoepfe(probe)
    assert all(k[f] == "tragen" for f in MUENZ_FARBEN), k
    assert all(k[f] == "voll" for f in VOLL_FARBEN), "Vollversions-Farben bleiben an unlimited()"

    # Tragen ohne Muenzabzug, besitz bleibt, was gekauft ist
    probe.page.locator('#ladenWaren button[data-tragen="nacht"]').click()
    zustand = "() => ({farbe: getrageneFarbe(), fest: festTracht().farbe, muenzen: muenzen(), besitz: [...besitz]," \
              " stand: {besitz: standAlsObjekt().besitz, aus: standAlsObjekt().muenzen_aus}})"
    erwartet = {"farbe": "nacht", "fest": "nacht", "muenzen": 5000, "besitz": ["gruen"],
                "stand": {"besitz": ["gruen"], "aus": 0}}
    assert probe.js(zustand) == erwartet
    # Kaufen geht nicht mehr, Vollversions-Farbe tragen auch nicht
    probe.js("() => { kaufe('rosa'); trage('gold'); }")
    assert probe.js(zustand) == erwartet
    assert probe.js("() => getragenRoh()") == ["nacht"]

    # Bleibt nach dem Neustart
    probe.neu_laden()
    assert probe.js("() => [hautAlle, getrageneFarbe(), muenzen()]") == [True, "nacht", 5000]

    # Ausschalten fragt nach; "Anlassen" laesst ihn an
    _laden(probe)
    _tippen(probe)
    _wort(probe, TEST_WORT)
    probe.page.locator("#frNein").wait_for()
    probe.page.locator("#frNein").click()
    _ruhe(probe)
    assert probe.js(AN) == "1"

    _tippen(probe)
    _wort(probe, TEST_WORT)
    probe.page.locator("#frJa").wait_for()
    probe.page.locator("#frJa").click()
    probe.page.wait_for_function("() => localStorage.getItem('zmaj_hautalle') === '0'")
    k = _knoepfe(probe)
    assert k["gruen"] == "tragen" and all(k[f] == "preis" for f in MUENZ_FARBEN[1:]), k
    # Die nicht gekaufte Farbe faellt vom Drachen, gespeichert bleibt sie
    assert probe.js("() => [hautAlle, getrageneFarbe(), getragenRoh(), muenzen(), [...besitz]]") == \
        [False, "", ["nacht"], 5000, ["gruen"]]
    assert probe.fehler == []


def test_schalter_nicht_in_lernstand_und_sicherung(probe, heute_stand):
    probe.starten(stand=heute_stand(muenzen_ges=300))
    _laden(probe)
    _einschalten(probe)
    probe.page.locator('#ladenWaren button[data-tragen="lila"]').click()
    probe.js("() => saveProgress()")

    datei = probe.js("() => sicherungInhalt()")
    assert "hautalle" not in datei.lower()
    stand = json.loads(datei)["stand"]
    assert not [s for s in stand if "haut" in s.lower()]
    assert stand["besitz"] == [] and stand["muenzen_aus"] == 0
    assert "hautalle" not in (probe.js("() => localStorage.getItem('zmaj_stand')") or "").lower()

    # Einlesen laesst den Schalter, wie er ist - auch mit untergeschobenem Feld
    einlesen = """async (text) => {
        frage = async () => true;
        await sicherungEinlesen(new File([text], 'sicherung.json', {type: 'application/json'}));
        return [hautAlle, localStorage.getItem('zmaj_hautalle')];
    }"""
    assert probe.js(einlesen, datei) == [True, "1"]
    probe.js("() => hautAlleSetzen(false)")
    boese = json.loads(datei)
    boese["stand"].update({"hautalle": True, "zmaj_hautalle": "1", "haut_alle": 1})
    assert probe.js(einlesen, json.dumps(boese)) == [False, "0"]
    assert probe.fehler == []


def test_versionszeile_unveraendert_und_unabhaengig(probe, heute_stand):
    probe.starten(stand=heute_stand(muenzen_ges=100))
    dauer = "() => [localStorage.getItem('zmaj_dauer2'), localStorage.getItem('zmaj_hautalle'), premium]"

    # Versionszeile: dasselbe Wort schaltet die Dauer-Vollversion, nicht die Farben
    probe.page.locator("#btnSettings").click()
    _tippen(probe, ziel="#ueberZeile")
    _wort(probe, TEST_WORT)
    probe.page.wait_for_function("() => localStorage.getItem('zmaj_dauer2') === '1'")
    assert probe.js(dauer) == ["1", None, True]

    # Laden: schaltet die Farben, laesst die Dauer-Vollversion
    _laden(probe)
    _einschalten(probe)
    assert probe.js(dauer) == ["1", "1", True]

    # Versionszeile aus: die Farben bleiben
    probe.page.locator("#btnSettings").click()
    _tippen(probe, ziel="#ueberZeile")
    _wort(probe, TEST_WORT)
    probe.page.locator("#frJa").wait_for()
    probe.page.locator("#frJa").click()
    probe.page.wait_for_function("() => localStorage.getItem('zmaj_dauer2') === '0'")
    assert probe.js(dauer) == ["0", "1", False]
    assert probe.fehler == []


def test_ueberschrift_sonst_ohne_wirkung(probe, heute_stand):
    probe.starten(stand=heute_stand(muenzen_ges=5000))
    titel = probe.js("() => t('laden.titel')")
    assert probe.page.locator("#ladenTitel").count() == 1

    # Andere Reiter: beliebig oft tippen, nichts geht auf
    probe.page.locator("#btnShop").click()
    assert probe.js("() => ladenReiter") == "vorrat"
    _tippen(probe, 8)
    assert _kasten(probe) == 0
    _laden(probe, "kopf")
    _tippen(probe, 7)
    assert _kasten(probe) == 0

    # Farben: sechs reichen nicht; ein Tipp in einem anderen Reiter zaehlt von vorn
    _laden(probe)
    _tippen(probe, 6)
    assert _kasten(probe) == 0
    _laden(probe, "brille")
    _tippen(probe, 1)
    _laden(probe)
    _tippen(probe, 3)
    assert _kasten(probe) == 0

    # Mehr als zwei Sekunden Pause zaehlt von vorn
    probe.page.wait_for_timeout(2300)
    _tippen(probe, 6)
    assert _kasten(probe) == 0
    _tippen(probe, 1)
    assert probe.page.locator("#frWort").count() == 1
    probe.page.locator("#frAb").click()
    assert _kasten(probe) == 0 and probe.js(AN) is None

    # Ueberschrift, Reiterwahl und Kauf wie vorher
    assert probe.page.locator("#ladenTitel").inner_text().strip() == titel
    assert probe.js("() => { const h = document.getElementById('ladenTitel');"
                    " return [h.tagName, h.getAttribute('role'), h.getAttribute('tabindex')]; }") == ["H2", None, None]
    probe.page.locator('#ladenWaren button[data-ware="gruen"]').click()
    assert probe.js("() => [[...besitz], muenzen(), getrageneFarbe()]") == [["gruen"], 4100, "gruen"]
    assert _knoepfe(probe)["gruen"] == "tragen"
    assert probe.fehler == []
