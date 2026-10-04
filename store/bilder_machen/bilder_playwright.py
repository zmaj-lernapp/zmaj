# -*- coding: utf-8 -*-
r"""
bilder_playwright.py  –  die acht Store-Bilder in jeder Sprache, auf jedem Rechner

Dasselbe wie bilder_machen.sh, aber ohne Git Bash, ohne von Hand
gestarteten Chrome und ohne festen Thonny-Pfad: Das Skript liefert web/
selbst aus, startet Chromium über Playwright und macht die Bilder.

    python3 -m pip install playwright
    python3 -m playwright install chromium        # einmal, falls kein Chromium da ist
    python3 store/bilder_machen/bilder_playwright.py                 # Deutsch → store/screenshots
    python3 store/bilder_machen/bilder_playwright.py --sprache en    # → docs/assets/screenshots-en/
    python3 store/bilder_machen/bilder_playwright.py --sprache en --montage docs/assets/screenshots-en.png

Größe wie im Store: 360 x 640 CSS-Punkte mal 3 = 1080 x 1920.
Vorher muss web/inhalt existieren (python3 inhalt_bauen.py).

Die Abläufe in den Schritten sind aus bilder_machen.sh übernommen. Wo dort
ein deutscher Text gesucht wurde ("Zuhause", "Weitermachen"), steht hier ein
sprachunabhängiger Weg: die Position im Lernpfad bzw. t('btn.weitermachen').
"""
import argparse
import functools
import http.server
import json
import os
import socketserver
import sys
import threading
import time

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(os.path.dirname(HIER))
WEB = os.path.join(WURZEL, "web")

# (Dateiname, JavaScript). Jeder Schritt läuft im Browser als async-Funktion.
SCHRITTE = [
    ("01-start", """
        const q = questsHeute(), t = today(); tagwerk[t] = {};
        q.forEach((x,i) => { tagwerk[t][x.id] = i === 0 ? x.ziel : Math.floor(x.ziel * 0.6); });
        [...known].slice(40, 47).forEach((id, i) => { topf['w:' + id] = {typ: i % 2 ? 'mcrev' : 'mc', n: 0, z: Date.now() - i * 60000}; });
        homeMode = 'words'; showHome(); scrollTo(0,0);
        await new Promise(r=>setTimeout(r,2500)); return 'start'"""),
    ("02-lernpfad", """
        const z = [...document.querySelectorAll('.label')].filter(e => e.offsetParent)[8];
        scrollBy(0, z.getBoundingClientRect().top - 70);
        await new Promise(r=>setTimeout(r,400)); return scrollY"""),
    ("03-neues-wort", """
        openLevel(12); await new Promise(r=>setTimeout(r,400)); startLesson();
        await new Promise(r=>setTimeout(r,800)); scrollTo(0,0); return Lx.queue.length"""),
    ("04-auswahl", """
        let ziel = Lx.queue.findIndex(q => q.typ === 'mc' && q.w.de.length > 8);
        if(ziel < 0) ziel = Lx.queue.findIndex(q => q.typ === 'mc');
        while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); }
        await new Promise(r=>setTimeout(r,800)); scrollTo(0,0); return Lx.i"""),
    ("05-richtig", """
        const q = Lx.queue[Lx.i];
        [...document.querySelectorAll('#lBody .opt')].find(o => o.textContent === q.w.bs).click();
        await new Promise(r=>setTimeout(r,1000)); return q.w.bs"""),
    ("06-luecke", """
        document.querySelector('#lBody .weiterbox .btn').click(); await new Promise(r=>setTimeout(r,500));
        let ziel = Lx.queue.findIndex((q, i) => i >= Lx.i && q.typ === 'gap');
        for(let n = 0; ziel < 0 && n < 8; n++){ startLesson(); await new Promise(r=>setTimeout(r,600)); ziel = Lx.queue.findIndex(q => q.typ === 'gap'); }
        while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); }
        await new Promise(r=>setTimeout(r,800));
        const q = Lx.queue[Lx.i]; const inp = document.getElementById('xIn');
        inp.value = q.s.answer.split(' / ')[0]; inp.dispatchEvent(new Event('input', {bubbles:true})); inp.blur();
        scrollTo(0,0); await new Promise(r=>setTimeout(r,300)); return q.s.text"""),
    ("07-geschichte", """
        Lx = null; openStory(3); await new Promise(r=>setTimeout(r,600));
        const w = [...document.querySelectorAll('#rBody .w')].find(x => x.textContent === 'povrća');
        if(w) w.click(); await new Promise(r=>setTimeout(r,500)); stilleBitte(); scrollTo(0,0);
        return document.getElementById('rBubble').innerText"""),
    ("08-wiederholen", """
        homeMode = 'topf'; showHome(); await new Promise(r=>setTimeout(r,600));
        scrollTo(0,0); await new Promise(r=>setTimeout(r,200));
        const text = t('btn.weitermachen');
        const w = [...document.querySelectorAll('button')].find(b => b.offsetParent && b.textContent.includes(text));
        if(w) scrollBy(0, w.getBoundingClientRect().top - 16);
        await new Promise(r=>setTimeout(r,400)); return scrollY"""),
]


def lernstand():
    """Wie stand.py: Vorführstand aus testdaten, auf heute verschoben."""
    sys.path.insert(0, HIER)
    import datetime
    quelle = os.path.join(WURZEL, "testdaten", "zmaj-screenshots.json")
    s = json.load(open(quelle, encoding="utf-8"))["stand"]
    heute = datetime.date.today()
    s["tage"] = sorted((heute - datetime.timedelta(days=i)).isoformat() for i in range(47))
    s["rekord"] = 47
    s["frost"] = []
    s["bewertung"] = {"gezeigt": [], "nein": True, "bewertet": False}
    s["einstufung"] = {"tag": s["tage"][0], "wahl": "neu", "bis": ""}
    return json.dumps(s, ensure_ascii=False)


def server_starten():
    """web/ auf einem freien Port, im Hintergrund, ohne Ausgabe."""
    class Leise(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Leise, directory=WEB)
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d" % srv.server_address[1]


def bilder_machen(sprache, ziel, chrome=None):
    from playwright.sync_api import sync_playwright

    if not os.path.exists(os.path.join(WEB, "inhalt", sprache + ".json")):
        raise SystemExit("web/inhalt/%s.json fehlt - erst  python3 inhalt_bauen.py" % sprache)
    os.makedirs(ziel, exist_ok=True)
    antworte = open(os.path.join(HIER, "antworte.js"), encoding="utf-8").read()
    srv, basis = server_starten()
    pfade = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chrome) if chrome else pw.chromium.launch()
            seite = browser.new_context(viewport={"width": 360, "height": 640},
                                        device_scale_factor=3, locale=sprache).new_page()
            js = lambda code: seite.evaluate("async () => {" + code + "}")  # noqa: E731
            # Den Stand auf einer leeren Seite desselben Ursprungs setzen, nicht in
            # der laufenden App: deren visibilitychange speichert beim Wegnavigieren
            # sonst den eigenen, leeren Stand darueber (wie tests_e2e/conftest.py).
            seite.goto(basis + "/leer")
            js("localStorage.clear(); localStorage.setItem('zmaj_stand', %s); "
               "localStorage.setItem('zmaj_einwilligung', JSON.stringify({wahl:'nein',stand:1,zeit:new Date().toISOString()})); "
               "localStorage.setItem('zmaj_sprache', %s); return 1"
               % (json.dumps(lernstand()), json.dumps(sprache)))
            seite.goto(basis + "/index.html?neu=%d" % time.time())
            seite.wait_for_function("typeof openLevel === 'function' && typeof Lx !== 'undefined'", timeout=30000)
            seite.wait_for_timeout(6000)   # Vorspann und Drache
            js(antworte)
            js("const st = document.createElement('style'); st.textContent = '#btnBack{display:none!important}'; "
               "document.head.append(st); return 1")
            for name, code in SCHRITTE:
                ergebnis = js(code)
                pfad = os.path.join(ziel, name + ".png")
                seite.screenshot(path=pfad)
                pfade.append(pfad)
                print("  %-16s %s" % (name, str(ergebnis)[:60].replace("\n", " ")))
            browser.close()
    finally:
        srv.shutdown()
    return pfade


def montage(pfade, ausgabe, auswahl=(0, 1, 2, 3, 6)):
    """Fünf Bilder nebeneinander, für das README."""
    from PIL import Image
    breite, hoehe, luecke = 540, 960, 16
    bilder = [Image.open(pfade[i]).convert("RGB").resize((breite, hoehe), Image.LANCZOS) for i in auswahl]
    leinwand = Image.new("RGB", (breite * len(bilder) + luecke * (len(bilder) - 1), hoehe), (255, 255, 255))
    for i, b in enumerate(bilder):
        leinwand.paste(b, (i * (breite + luecke), 0))
    leinwand.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE).save(ausgabe, optimize=True)
    print("Montage: %s (%.0f KB)" % (ausgabe, os.path.getsize(ausgabe) / 1024.0))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--sprache", default="de")
    p.add_argument("--ziel", help="Ordner für die Bilder")
    p.add_argument("--chrome", help="Pfad zu Chromium, falls Playwright keinen eigenen hat")
    p.add_argument("--montage", help="zusätzlich eine Bildleiste für das README schreiben (braucht Pillow)")
    a = p.parse_args(argv)
    ziel = a.ziel or (os.path.join(WURZEL, "store", "screenshots") if a.sprache == "de"
                      else os.path.join(WURZEL, "docs", "assets", "screenshots-" + a.sprache))
    pfade = bilder_machen(a.sprache, ziel, a.chrome)
    if a.montage:
        montage(pfade, a.montage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
