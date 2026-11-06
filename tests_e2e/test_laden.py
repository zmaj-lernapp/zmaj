# -*- coding: utf-8 -*-
"""Der Laden im echten Browser: ein Doppeltipp kauft nur einmal.

Pruefbericht 1.3, G9. Ein schneller Doppeltipp auf Herz kostete 200 statt 100
Muenzen und gab zwei Leben, beim Serienschutz ebenso. Beim Zierrat wurde
gekauft und mit dem zweiten Tipp sofort wieder abgenommen. Die Sperre sitzt in
den Klick-Horchern, nicht in kaufe() und trage(), denn die rufen andere Stellen
direkt und bewusst nacheinander auf (test_haut_alle.py). Geklickt wird deshalb
mit der Maus an dieselbe Stelle, wie ein Finger es taete: renderLaden() zeichnet
den Knopf nach dem ersten Tipp neu.
"""
import time

ZUSTAND = """() => ({m: muenzen(), leben: lives.anzahl, schutz: schutz.anzahl,
                    besitz: [...besitz], getragen: getragenRoh()})"""
SPERRE_VORBEI_MS = 450


def _laden(seite, heute_stand, **mehr):
    seite.starten(stand=heute_stand(muenzen_ges=2000, **mehr))
    # Der Vorspann liegt ueber allem und nimmt den ersten Mausklick sonst selbst an
    seite.js("() => document.getElementById('vorspann').click()")
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    seite.js("() => { festHeute = () => ''; showLaden(); }")
    seite.page.wait_for_selector("#ladenWaren .ware")


def _doppeltipp(seite, knopf):
    k = seite.page.locator(knopf).bounding_box()
    x, y = k["x"] + k["width"] / 2, k["y"] + k["height"] / 2
    seite.page.mouse.click(x, y)
    seite.page.mouse.click(x, y)
    seite.page.wait_for_timeout(100)


def test_doppeltipp_auf_herz_kauft_einmal(seite, heute_stand):
    _laden(seite, heute_stand, leben={"anzahl": 2, "zeit": int(time.time() * 1000)})
    vorher = seite.js(ZUSTAND)
    _doppeltipp(seite, 'button[data-ware="herz"]')
    z = seite.js(ZUSTAND)
    assert (z["m"], z["leben"]) == (vorher["m"] - 100, vorher["leben"] + 1), (vorher, z)
    # Wer danach mit Absicht noch einmal kauft, kommt durch
    seite.page.wait_for_timeout(SPERRE_VORBEI_MS)
    seite.page.locator('button[data-ware="herz"]').click()
    z = seite.js(ZUSTAND)
    assert (z["m"], z["leben"]) == (vorher["m"] - 200, vorher["leben"] + 2), (vorher, z)
    assert seite.fehler == []


def test_doppeltipp_auf_serienschutz_kauft_einmal(seite, heute_stand):
    _laden(seite, heute_stand, schutz={"anzahl": 0, "zeit": 0})
    vorher = seite.js(ZUSTAND)
    preis = seite.js("() => VERBRAUCH.find(w => w.id === 'schutz').preis")
    _doppeltipp(seite, 'button[data-ware="schutz"]')
    z = seite.js(ZUSTAND)
    assert (z["m"], z["schutz"]) == (vorher["m"] - preis, vorher["schutz"] + 1), (vorher, z)
    assert seite.fehler == []


def test_doppeltipp_auf_zierrat_kauft_und_laesst_ihn_an(seite, heute_stand):
    _laden(seite, heute_stand)
    ware = seite.js("""() => { ladenReiter = GRUPPEN.find(g => g.id !== 'vorrat').id; renderLaden();
        return document.querySelector('#ladenWaren button[data-ware]').dataset.ware; }""")
    vorher = seite.js(ZUSTAND)
    preis = seite.js("(id) => ZIERRAT.find(w => w.id === id).preis", ware)
    _doppeltipp(seite, '#ladenWaren button[data-ware="%s"]' % ware)
    z = seite.js(ZUSTAND)
    assert z["m"] == vorher["m"] - preis, (vorher, z)
    assert ware in z["besitz"] and ware in z["getragen"], z
    # Ein Tipp mit Absicht nimmt es ab
    seite.page.wait_for_timeout(SPERRE_VORBEI_MS)
    seite.page.locator('#ladenWaren button[data-tragen="%s"]' % ware).click()
    z = seite.js(ZUSTAND)
    assert ware in z["besitz"] and ware not in z["getragen"], z
    assert seite.fehler == []
