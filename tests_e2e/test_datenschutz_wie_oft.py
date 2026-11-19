# -*- coding: utf-8 -*-
"""Datenschutzerklärung, Abschnitt 3, „Wie oft“ (Offen-Liste 8, 17.11.2026),
im echten Browser, Einstellungen -> Datenschutz. Die Sätze selbst stehen in
tests/test_datenschutz_wie_oft.py.

Die Browser-Tests laufen auf der Web-Demo (demo_bauen.py), und die zeigt die
Fassung ohne Konto: dort gibt es „Wie oft“ nicht, und vom alten Satz darf auch
nichts dastehen. Die Fassung mit Konto, die die Android-App bekommt, kommt aus
web/inhalt/<sprache>.json, so wie inhalt_bauen.py sie geschrieben hat: Der
Test setzt sie in die laufende Demo ein und liest, was in den Einstellungen
steht.
"""
import importlib.util
import os

import pytest

import texte_pruefen

_PFAD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "tests", "test_datenschutz_wie_oft.py")
_spec = importlib.util.spec_from_file_location("datenschutz_wie_oft_saetze", _PFAD)
SAETZE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SAETZE)

OEFFNEN = """(text) => {
    if(text !== null){ T['set.datenschutz_text'] = text; applyTexts(); }
    showSettings();
    const s = document.querySelector('#settingsView summary[data-t="set.datenschutz"]');
    const d = s.parentElement, inhalt = d.querySelector('.legal');
    if(!d.open) s.click();
    return {offen: d.open, sichtbar: inhalt.offsetParent !== null, html: inhalt.innerHTML};
}"""


def _wie_oft(html, code):
    return [a for a in html.split("<br>") if a.startswith(SAETZE.UEBERSCHRIFT[code])]


@pytest.mark.parametrize("code", sorted(SAETZE.NEU))
def test_wie_oft_in_den_einstellungen(seite, heute_stand, code):
    seite.starten(sprache=code, stand=heute_stand())
    # Demo, ohne Konto: kein „Wie oft“, nichts vom alten Satz
    demo = seite.js(OEFFNEN, None)
    assert demo["offen"] and demo["sichtbar"], code
    assert _wie_oft(demo["html"], code) == [], code
    for alt in SAETZE.ALT[code]:
        assert alt not in demo["html"], (code, alt)
    # Mit Konto, aus web/inhalt
    gebaut = texte_pruefen.texte_holen(code)["set.datenschutz_text"]
    z = seite.js(OEFFNEN, gebaut)
    assert z["offen"] and z["sichtbar"], code
    assert _wie_oft(z["html"], code) == [SAETZE.UEBERSCHRIFT[code] + SAETZE.NEU[code]], code
    for alt in SAETZE.ALT[code]:
        assert alt not in z["html"], (code, alt)
    assert seite.fremd == [], seite.fremd
    assert seite.fehler == []
