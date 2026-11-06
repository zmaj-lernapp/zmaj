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


LINK_KONTRAST = """(text) => {
    const hell = c => { const k = c.slice(0, 3).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); });
                        return 0.2126 * k[0] + 0.7152 * k[1] + 0.0722 * k[2]; };
    const farbe = s => s.match(/[\\d.]+/g).map(Number);
    const grund = el => { for(let e = el; e; e = e.parentElement){ const c = farbe(getComputedStyle(e).backgroundColor);
                          if(c.length === 3 || c[3] > 0) return c; } return [255, 255, 255]; };
    T['set.impressum_text'] = text; applyTexts();
    showSettings();
    const s = document.querySelector('#settingsView summary[data-t="set.impressum"]');
    s.parentElement.open = true;
    const a = s.parentElement.querySelector('.legal a');
    const werte = [];
    for(let sek = 1; sek <= 9; sek++){
      document.documentElement.dataset.sek = sek;
      const x = hell(farbe(getComputedStyle(a).color)), y = hell(grund(a));
      werte.push((Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05));
    }
    return werte;
}"""


def test_kontakt_link_im_impressum_ist_lesbar(seite, heute_stand):
    """Pruefbericht 1.3, G12: der Link hatte das Blau des Browsers, im dunklen
    Modus 1,03:1 bis 1,38:1 auf seinem Grund. Gemessen in jeder der neun
    Sektionsfarben, dunkel und hell."""
    mit_formular = sprachen.TEXTE["de"]["set.impressum_text_mit_formular"]
    for aussehen in ("dunkel", "hell"):
        seite.page.goto(seite.basis + "/leer")
        seite.js("(a) => localStorage.setItem('zmaj_theme', a)", aussehen)
        seite.starten(stand=heute_stand(), leeren=False)
        werte = seite.js(LINK_KONTRAST, mit_formular)
        assert len(werte) == 9 and min(werte) >= 4.5, (aussehen, werte)
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
