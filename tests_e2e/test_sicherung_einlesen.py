# -*- coding: utf-8 -*-
"""Eine Sicherungsdatei darf die App nicht lahmlegen - import_richten.py
im echten Browser.

Die vier boesen Dateien stehen im Kopf von import_richten.py. Gefaehrlich
ist vor allem die erste: ohne die Haertung warf danach jeder Start, bevor
der Einstellungsknopf erschien, und an "Sicherung einlesen" kam man nie
wieder heran. Deshalb wird hier nach dem Einlesen NEU GELADEN und erst dann
geprueft - der Fehler zeigte sich ja erst beim naechsten Start.

Geprueft wird die Kopie gehaertet/ (siehe conftest.py), solange
import_richten.py noch nicht in web/index.html geschrieben ist. Gegenprobe
am 04.10.2026: gegen die ungehaertete Kopie app/ schlagen alle vier Faelle
fehl - die Tests sehen den Fehler also wirklich.
"""
import json

import pytest

BOESE = {
    "gewusst_zahl": {"app": "zmaj", "stand": {"gewusst": [1], "tage": ["2026-10-01"]}},
    "herzen_1e300": {"app": "zmaj", "stand": {"gewusst": [], "leben": {"anzahl": 1e300, "zeit": "morgen"}}},
    # WORT wird durch die Kennung eines echten Wortes ersetzt: zu einer
    # unbekannten Kennung baut topfAufgabe() gar keine Aufgabe und liest
    # den Eintrag nie - dann gaebe es auch nichts zu pruefen.
    "topf_null": {"app": "zmaj", "stand": {"topf": {"w:WORT": None}}},
    "besitz_constructor": {"app": "zmaj", "stand": {"besitz": ["constructor"], "getragen": "constructor"}},
    # Lerntage als Text: (d.tage||[]).filter warf. Jetzt werden sie ignoriert.
    "tage_text": {"app": "zmaj", "stand": {"tage": "x", "frost": "y", "geschenk_jahr": 9999}},
}

# frage() oeffnet sonst das Ja/Nein-Fenster und wartet auf einen Finger.
EINLESEN = """async (text) => {
    frage = async () => true;
    await sicherungEinlesen(new File([text], 'sicherung.json', {type: 'application/json'}));
    return {notiz: document.getElementById('sichNote').textContent, woerter: known.size, herzen: lives.anzahl};
}"""

NACH_START = """async () => {
    const knopf = document.getElementById('btnSettings');
    homeMode = 'topf'; showHome();           // Wiederholen-Reiter: warf bei topf null
    homeMode = 'words'; showHome();
    /* mountZmaj() faengt Fehler beim Bauen des Drachen still ab - er bliebe
       nur leer, ein Seitenfehler kaeme nie. Deshalb hier direkt fragen. */
    const drache = await zmajDaten().then(() => 'ok', e => String(e));
    return {einstellungen: knopf.style.display === 'inline-block' && knopf.offsetParent !== null,
            herzen: lives.anzahl, max: LEBEN_MAX, woerter: known.size, drache};
}"""


@pytest.mark.parametrize("name", sorted(BOESE))
def test_boese_sicherung_legt_app_nicht_lahm(seite, heute_stand, name):
    seite.starten(app="gehaertet", stand=heute_stand())
    wort = seite.js("() => CATEGORIES[0].words[0].id")
    seite.js(EINLESEN, json.dumps(BOESE[name]).replace("WORT", json.dumps(wort)[1:-1]))
    seite.neu_laden()
    nach = seite.js(NACH_START)
    assert nach["einstellungen"], "Einstellungsknopf fehlt nach dem Neustart"
    assert 0 <= nach["herzen"] <= nach["max"] == 5
    assert nach["drache"] == "ok"
    assert seite.fehler == []


def test_echte_sicherung_bleibt_vollstaendig(seite, heute_stand, vollversion):
    """Die Haertung nimmt einer echten Sicherung nichts: gleich viele Woerter
    wie in der ungehaerteten App, auch nach dem Neuladen."""
    text = json.dumps(vollversion)
    seite.starten(app="app", stand=heute_stand())
    ohne = seite.js(EINLESEN, text)

    seite.starten(app="gehaertet", stand=heute_stand())
    mit = seite.js(EINLESEN, text)
    assert ohne["woerter"] > 1000
    assert mit["woerter"] == ohne["woerter"]
    assert mit["notiz"] == ohne["notiz"]          # "... Woerter eingelesen", keine Fehlermeldung

    seite.neu_laden()
    nach = seite.js(NACH_START)
    assert nach["woerter"] == ohne["woerter"]
    assert nach["einstellungen"]
    assert nach["drache"] == "ok"
    assert seite.fehler == []

