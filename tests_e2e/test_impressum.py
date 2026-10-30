# -*- coding: utf-8 -*-
"""Das Impressum in der App (Ajdin am 28.10.2026), im echten Browser.

Bis dahin stand es nur auf zmaj-lernapp.github.io/impressum.html. Geprueft
wird:
  - Einstellungen -> Ueber die App: ein Eintrag unter Nutzungsbedingungen
    und Datenschutz, aufgeklappt derselbe Text wie auf der Webseite
    (set.impressum_text aus sprachen.texte()), mit der Anschrift statt
    {anbieter}, in der Sprache der App - und ohne eine Anfrage ins Netz.
  - Mit Kontaktformular nennt das Impressum kontakt.html als Verweis.
    Angetippt oeffnet er im Browser des Geraets (window.open), die App
    bleibt auf ihrer Seite.
"""
import re
from html import unescape

import sprachen

OEFFNEN = """() => {
    showSettings();
    const s = document.querySelector('#settingsView summary[data-t="set.impressum"]');
    s.click();
    const d = s.parentElement, inhalt = d.querySelector('.legal');
    return {offen: d.open, titel: s.textContent, text: inhalt.textContent,
            sichtbar: inhalt.offsetParent !== null,
            reihe: [...document.querySelectorAll('#settingsView details > summary[data-t]')].map(x => x.dataset.t)};
}"""


def _nur_text(html):
    return unescape(re.sub(r"<[^>]+>", "", html.replace("<br>", "")))


def test_impressum_in_den_einstellungen(seite, heute_stand):
    for code in ("de", "en", "tr", "fr"):
        seite.starten(sprache=code, stand=heute_stand())
        z = seite.js(OEFFNEN)
        t = sprachen.texte(code)
        assert z["offen"] and z["sichtbar"], code
        assert z["titel"] == t["set.impressum"], code
        soll = t["set.impressum_text"].replace("{anbieter}", sprachen.ANBIETER)
        assert z["text"] == _nur_text(soll), code
        assert "{anbieter}" not in z["text"] and "USt-IdNr" in z["text"], code
        # Unter Nutzungsbedingungen und Datenschutz, als letzter Eintrag.
        assert z["reihe"][-3:] == ["set.agb", "set.datenschutz", "set.impressum"], (code, z["reihe"])
    assert seite.fremd == [], seite.fremd
    assert seite.fehler == []


def test_verweis_im_impressum_oeffnet_den_browser(seite, heute_stand):
    """Die Fassung mit Formular, wie texte() sie mit KONTAKT_FORMULAR in die
    App gibt. Ohne den Umweg verliesse die App beim Tippen ihre Seite."""
    seite.starten(stand=heute_stand())
    adresse = seite.page.url
    mit_formular = sprachen.TEXTE["de"]["set.impressum_text_mit_formular"]
    z = seite.js("""(text) => {
        T['set.impressum_text'] = text; applyTexts();
        window.geoeffnet = [];
        window.open = (u, ziel, art) => { geoeffnet.push([u, ziel, art]); return null; };
        showSettings();
        const s = document.querySelector('#settingsView summary[data-t="set.impressum"]');
        s.click();
        s.parentElement.querySelector('.legal a').click();
        return geoeffnet;
    }""", mit_formular)
    assert z == [["https://zmaj-lernapp.github.io/kontakt.html", "_blank", "noopener"]]
    seite.page.wait_for_timeout(300)
    assert seite.page.url == adresse
    assert seite.js("() => document.getElementById('settingsView').style.display") != "none"
    assert seite.fremd == [], seite.fremd
    assert seite.fehler == []
