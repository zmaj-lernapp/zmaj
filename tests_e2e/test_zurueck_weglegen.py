# -*- coding: utf-8 -*-
"""Zurueck-Taste auf der Startseite legt die App weg (20.11.2026, Optimierung Punkt 7).

Ajdin am 20.11.2026: "7. ja machen wir". Bis 1.4 fragte
die App auf der Startseite "Beenden?" und rief dann App.exitApp(); beim
naechsten Oeffnen kam ein Kaltstart mit Vorspann. Jetzt ruft sie auf Android
App.minimizeApp() (moveTaskToBack in @capacitor/app), ohne Rueckfrage - wie
die Home-Taste. Release/Optimierung_2026-11-20/BERICHT.md, Punkt 7.

Geprueft mit einem nachgebauten Plugin App, das jeden Aufruf mitschreibt.
Gedrueckt wird ueber den Horcher, den die App fuer 'backButton' anmeldet:
  - Android, Startseite: minimizeApp einmal, exitApp nie, keine Rueckfrage,
    der Stand ist vorher gespeichert
  - Android, Pflicht-Update-Karte: exitApp wie bisher, minimizeApp nie
  - Android, Levelseite: eine Ebene zurueck, weder weglegen noch beenden
  - iPhone (getPlatform 'ios', keine Zurueck-Taste): weiter die Rueckfrage,
    nichts wird weggelegt

Zum Gegencheck ohne die Aenderung: in web/js/start.js (zurueckTaste) den
Block mit minimizeApp entfernen, dann scheitert der Test zur Startseite.
"""
from conftest import Seite

# Das Plugin App wie @capacitor/app es anbietet, mit Mitschrift.
PLUGIN = r"""
((plattform) => {
  window.__app = {aufrufe: [], horcher: {}};
  window.Capacitor = {
    getPlatform: () => plattform,
    isNativePlatform: () => true,
    Plugins: {App: {
      addListener: (name, f) => { window.__app.horcher[name] = f;
                                  return Promise.resolve({remove: async () => {}}); },
      minimizeApp: () => { window.__app.aufrufe.push('minimizeApp'); return Promise.resolve(); },
      exitApp: () => { window.__app.aufrufe.push('exitApp'); return Promise.resolve(); },
    }},
  };
})(%s);
"""

# Die Zurueck-Taste druecken, wie die Huelle es tut, und warten, bis sie fertig
# ist. Wartet sie nach 5 s noch (eine Rueckfrage steht offen), heisst das
# 'wartet' - der Test scheitert dann, statt haengen zu bleiben.
DRUECKEN = """async () => {
  const f = window.__app.horcher.backButton;
  if(!f) return 'kein Horcher';
  return await Promise.race([Promise.resolve(f({canGoBack: false})).then(() => 'ok'),
                             new Promise(r => setTimeout(() => r('wartet'), 5000))]);
}"""

LAGE = """() => ({aufrufe: window.__app.aufrufe.slice(),
  rueckfrage: !!document.querySelector('.nachfrage:not(.updsperre)'),
  level: sichtbar('levelView')})"""


def _seite(browser, basis, plattform):
    ctx = browser.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                              service_workers="block", reduced_motion="reduce")
    seite = Seite(ctx.new_page(), basis)
    seite.page.add_init_script(PLUGIN % ('"%s"' % plattform))
    return ctx, seite


def _startseite(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
    seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
    seite.js("() => { homeMode = 'words'; showHome(); }")
    assert seite.js("() => PLATTFORM") in ("android", "ios")
    assert seite.js("() => backTarget") is None


def test_startseite_android_legt_weg(browser, basis, heute_stand):
    ctx, seite = _seite(browser, basis, "android")
    try:
        _startseite(seite, heute_stand)
        # saveProgress mitzaehlen: vor dem Weglegen wird gespeichert
        seite.js("""() => { const alt = saveProgress; window.__gespeichert = 0;
            saveProgress = async () => { window.__gespeichert++;
                                         window.__app.aufrufe.push('saveProgress'); return alt(); }; }""")
        assert seite.js(DRUECKEN) == "ok"
        lage = seite.js(LAGE)
        assert lage["aufrufe"] == ["saveProgress", "minimizeApp"], lage
        assert lage["rueckfrage"] is False, lage
        # Noch einmal (App wieder vorn): wieder nur weglegen
        assert seite.js(DRUECKEN) == "ok"
        assert seite.js(LAGE)["aufrufe"].count("minimizeApp") == 2
        assert "exitApp" not in seite.js(LAGE)["aufrufe"]
        assert seite.fehler == []
    finally:
        ctx.close()


def test_pflicht_update_beendet_weiter(browser, basis, heute_stand):
    ctx, seite = _seite(browser, basis, "android")
    try:
        _startseite(seite, heute_stand)
        seite.js("() => updSperreZeigen()")
        assert seite.js("() => !!document.querySelector('.updsperre')")
        assert seite.js(DRUECKEN) == "ok"
        lage = seite.js(LAGE)
        assert lage["aufrufe"] == ["exitApp"], lage
        assert seite.fehler == []
    finally:
        ctx.close()


def test_levelseite_geht_zurueck(browser, basis, heute_stand):
    ctx, seite = _seite(browser, basis, "android")
    try:
        _startseite(seite, heute_stand)
        seite.js("() => openLevel(0)")
        assert seite.js("() => sichtbar('levelView')")
        assert seite.js(DRUECKEN) == "ok"
        lage = seite.js(LAGE)
        assert lage["aufrufe"] == [] and lage["level"] is False, lage
        assert seite.js("() => backTarget") is None      # wieder auf der Startseite
        assert seite.fehler == []
    finally:
        ctx.close()


def test_iphone_fragt_weiter(browser, basis, heute_stand):
    """iOS hat keine Zurueck-Taste; kaeme das Ereignis doch, bleibt es beim
    alten Weg mit Rueckfrage - weggelegt wird nur auf Android."""
    ctx, seite = _seite(browser, basis, "ios")
    try:
        _startseite(seite, heute_stand)
        seite.js("() => { window.__fertig = false; zurueckTaste().then(() => { window.__fertig = true; }); }")
        seite.page.wait_for_selector(".nachfrage", timeout=5000)
        lage = seite.js(LAGE)
        assert lage["aufrufe"] == [] and lage["rueckfrage"] is True, lage
        assert seite.fehler == []
    finally:
        ctx.close()
