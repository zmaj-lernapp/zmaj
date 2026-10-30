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

Tablets (seit 30.10.2026): --geraet tablet7 bzw. tablet10 macht dieselben
acht Bilder in Tablet-Breite. Das sind Rohbilder des Bildschirms (16:10, wie
ein echtes 7- bzw. 10-Zoll-Tablet), noch nicht im Store-Format; das Format
mit Überschrift und Tablet-Rahmen macht beschriften.py --geraet ...

    python3 store/bilder_machen/bilder_playwright.py --geraet tablet10 --aussehen dunkel --sprache de --ziel ROH10/de

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

# Bildschirm in CSS-Punkten und Pixeldichte. "handy" ist das Store-Format
# selbst (so breit wie Ajdins S21). Die Tablets haben die üblichen Android-
# Maße: 600 x 960 dp (7 Zoll, wie das Nexus 7) und 800 x 1280 dp (10 Zoll).
# Ab v110 waechst die App auf Tablets mit (GROSS in web/index.html): auf
# 10 Zoll alles 1,3-mal so gross, Lektionen fuellen den Bildschirm - so
# sieht sie dort wirklich aus.
GERAETE = {
    "handy":    {"breite": 360, "hoehe": 640,  "dsf": 3},   # 1080 x 1920
    "tablet7":  {"breite": 600, "hoehe": 960,  "dsf": 2},   # 1200 x 1920
    "tablet10": {"breite": 800, "hoehe": 1280, "dsf": 2},   # 1600 x 2560
}

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
    # Bis 11.10.2026 stand hier "05-richtig": dieselbe Aufgabe wie 04, nur
    # beantwortet. Jetzt eine Grammatikaufgabe - die zeigte bisher kein Bild.
    ("05-grammatik", """
        // Konjugation: sieht nach Grammatik aus und fragt nicht schon wieder
        // nach dem Preis wie 04.
        let ziel = -1;
        {
          const k = CATEGORIES.findIndex(c => c.id === 'konjugation');
          const lv = k >= 0 ? k : CATEGORIES.findIndex(c => ((GRAMMAR[c.id] || {}).uebungen || []).length);
          openLevel(lv); await new Promise(r=>setTimeout(r,400)); startLesson();
          await new Promise(r=>setTimeout(r,800));
          ziel = Lx.queue.findIndex(q => q.typ === 'gram');
        }
        while(Lx.i < ziel){ await window.__antworte(true, 'lBody', ()=>Lx); }
        await new Promise(r=>setTimeout(r,800)); scrollTo(0,0);
        window.__f5 = Lx.queue[Lx.i].g.frage;
        return Lx.queue[Lx.i].typ + ' ' + Lx.queue[Lx.i].g.frage"""),
    # 15.10.2026 (Store-Bilder v5, bis 30.10. nur in einem Hilfsskript außerhalb des Projekts):
    # 05 und 06 zeigten denselben Satz, weil Grammatikaufgabe und Lückensatz
    # aus derselben Konjugations-Lektion kamen. Darum nur ein Lückensatz, der
    # nicht schon in der Frage aus 05 steht, und ein ganzer Satz (Satzzeichen
    # am Ende, mindestens vier Wörter) - "Sedam, osam, ___" passt nicht zu
    # "Ganze Sätze selbst schreiben". Dafür bis zu 40 Mal neu mischen.
    ("06-luecke", """
        const wb = document.querySelector('#lBody .weiterbox .btn');
        if(wb){ wb.click(); await new Promise(r=>setTimeout(r,500)); }
        const passt = q => q.typ === 'gap' && !(window.__f5 || '').includes(q.s.text)
          && /[.?!]\\s*$/.test(q.s.text) && q.s.text.trim().split(/\\s+/).length >= 4;
        let ziel = Lx.queue.findIndex((q, i) => i >= Lx.i && passt(q));
        for(let n = 0; ziel < 0 && n < 40; n++){ startLesson(); await new Promise(r=>setTimeout(r,600)); ziel = Lx.queue.findIndex(passt); }
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


def bilder_machen(sprache, ziel, chrome=None, geraet="handy", aussehen=None):
    """aussehen: None = wie bisher (Playwright stellt hell ein), "hell" oder
    "dunkel". Die Store-Bilder sind seit v5 (15.10.2026) dunkel; die App folgt
    dem Gerät, darum wird hier das Gerät dunkel gestellt, nicht die App."""
    from playwright.sync_api import sync_playwright

    g = GERAETE[geraet]
    farbe = {"hell": {"color_scheme": "light"}, "dunkel": {"color_scheme": "dark"}}.get(aussehen, {})
    if not os.path.exists(os.path.join(WEB, "inhalt", sprache + ".json")):
        raise SystemExit("web/inhalt/%s.json fehlt - erst  python3 inhalt_bauen.py" % sprache)
    os.makedirs(ziel, exist_ok=True)
    antworte = open(os.path.join(HIER, "antworte.js"), encoding="utf-8").read()
    srv, basis = server_starten()
    pfade = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chrome) if chrome else pw.chromium.launch()
            seite = browser.new_context(viewport={"width": g["breite"], "height": g["hoehe"]},
                                        device_scale_factor=g["dsf"], locale=sprache, **farbe).new_page()
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
    """Fünf Bilder nebeneinander, für das README.

    Die Lücken sind durchsichtig (15.10.2026): Seit die Bilder dunkel sind,
    standen weiße Streifen dazwischen, auf GitHub im dunklen Modus grell.
    Die Palette bleibt MEDIANCUT - FASTOCTREE könnte zwar Alpha, verlor aber
    den weichen Schatten um den Drachen. Darum bekommen die Lücken eine
    Farbe, die in der App nicht vorkommt, und genau dieser Paletteneintrag
    wird durchsichtig. Trifft er auch nur ein Pixel der Bilder, bleiben die
    Lücken weiß wie vorher."""
    from PIL import Image
    breite, hoehe, luecke = 540, 960, 16
    loch = (255, 0, 255)
    bilder = [Image.open(pfade[i]).convert("RGB").resize((breite, hoehe), Image.LANCZOS) for i in auswahl]
    leinwand = Image.new("RGB", (breite * len(bilder) + luecke * (len(bilder) - 1), hoehe), loch)
    for i, b in enumerate(bilder):
        leinwand.paste(b, (i * (breite + luecke), 0))
    bild = leinwand.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    extra = {}
    if len(bilder) > 1:
        idx = bild.getpixel((breite + luecke // 2, hoehe // 2))
        nur_luecken = bild.histogram()[idx] == luecke * (len(bilder) - 1) * hoehe
        if nur_luecken and tuple(bild.getpalette()[idx * 3:idx * 3 + 3]) == loch:
            extra["transparency"] = idx
    if not extra:
        leinwand = Image.new("RGB", leinwand.size, (255, 255, 255))
        for i, b in enumerate(bilder):
            leinwand.paste(b, (i * (breite + luecke), 0))
        bild = leinwand.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    bild.save(ausgabe, optimize=True, **extra)
    print("Montage: %s (%.0f KB, Lücken %s)" % (ausgabe, os.path.getsize(ausgabe) / 1024.0,
                                                "durchsichtig" if extra else "weiß"))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--sprache", default="de")
    p.add_argument("--ziel", help="Ordner für die Bilder")
    p.add_argument("--chrome", help="Pfad zu Chromium, falls Playwright keinen eigenen hat")
    p.add_argument("--montage", help="zusätzlich eine Bildleiste für das README schreiben (braucht Pillow)")
    p.add_argument("--geraet", default="handy", choices=sorted(GERAETE),
                   help="handy (Standard, 1080 x 1920) oder Tablet-Rohbilder tablet7 / tablet10")
    p.add_argument("--aussehen", choices=("hell", "dunkel"),
                   help="Gerät hell oder dunkel stellen (ohne: hell, wie bisher; Store-Bilder seit v5: dunkel)")
    a = p.parse_args(argv)
    if a.geraet != "handy" and not a.ziel:
        p.error("--geraet %s braucht --ziel (Rohbilder, nicht für store/screenshots)" % a.geraet)
    ziel = a.ziel or (os.path.join(WURZEL, "store", "screenshots") if a.sprache == "de"
                      else os.path.join(WURZEL, "docs", "assets", "screenshots-" + a.sprache))
    pfade = bilder_machen(a.sprache, ziel, a.chrome, a.geraet, a.aussehen)
    if a.montage:
        montage(pfade, a.montage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
