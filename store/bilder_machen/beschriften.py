# -*- coding: utf-8 -*-
"""
beschriften.py  –  Store-Bilder mit Überschrift und Feature-Grafik je Sprache

Nimmt die acht Rohbilder einer Sprache (1080 x 1920, aus bilder_playwright.py)
und setzt über jedes eine kurze Überschrift: oben ein Band in den Farben der
Feature-Grafik, darunter das Bild verkleinert mit runden Ecken. Dazu die
Feature-Grafik (1024 x 500) aus web/_feature.html in derselben Sprache, als
JPEG ohne Alphakanal, wie Google sie verlangt.

    python store/bilder_machen/beschriften.py ROH ZIEL de en tr ...

ROH/<sprache>/01-start.png ... 08-wiederholen.png  ->  ZIEL/<sprache>/<sprache>_01-start.png ...
                                                     und ZIEL/<sprache>/<sprache>_feature.jpg

Die Sprachkennung steht vorn im Dateinamen, weil die Play Console beim
Hochladen gleich benannte Dateien verwechselt (10.10.2026).

Braucht Chrome und das Python-Paket websockets, kein Playwright und kein
Pillow. Seit 11.10.2026: vorher hatten die Bilder keine Überschrift und die
Grafik stand in allen Sprachen auf Deutsch.

Tablets (seit 30.10.2026): Mit --geraet tablet7 oder tablet10 kommen die
Rohbilder aus  bilder_playwright.py --geraet ...  und stehen unter derselben
Überschrift in einem schlichten Tablet-Rahmen. Ausgabe 1080 x 1920 (7 Zoll)
bzw. 1440 x 2560 (10 Zoll), 9:16, PNG ohne Alpha; Name <sprache>_tab7_01-start.png
bzw. <sprache>_tab10_... Die Feature-Grafik gibt es je Sprache nur einmal,
darum entsteht sie nur ohne --geraet.

    python store/bilder_machen/beschriften.py --geraet tablet10 ROH10 ZIEL10 de en ...
"""

import asyncio
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import bilder_playwright as BP  # noqa: E402

CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
TOR = 9447

# Reihenfolge wie BP.SCHRITTE. Höchstens etwa 38 Zeichen, sonst wird die
# Schrift kleiner. Übersetzt und von je einem zweiten Durchgang gegengelesen
# am 11.10.2026; Deutsch hat Ajdin freigegeben.
UEBERSCHRIFTEN = {
    "de": ["Jeden Tag ein Stück Bosnisch", "65 Levels – vom Hallo bis zum Amt",
           "Jedes Wort zum Anhören", "Kurze Übungen, die hängen bleiben",
           "Grammatik, einfach erklärt", "Ganze Sätze selbst schreiben",
           "Geschichten: Wort antippen, verstehen", "Wiederholen, bevor du vergisst"],
    "en": ["A little Bosnian every day", "65 levels – from hello to paperwork",
           "Hear every word", "Short exercises that stick",
           "Grammar made simple", "Write whole sentences yourself",
           "Stories: tap a word to understand it", "Review before you forget"],
    "tr": ["Her gün biraz Boşnakça", "65 seviye – merhabadan resmî işlere",
           "Her kelimeyi dinleyebilirsin", "Akılda kalan kısa alıştırmalar",
           "Dil bilgisi, sade ve anlaşılır", "Cümleleri baştan sona kendin yaz",
           "Hikâyeler: kelimeye dokun, anla", "Unutmadan önce tekrar et"],
    "sv": ["Lite bosniska varje dag", "65 nivåer – från hej till myndigheter",
           "Lyssna på varje ord", "Korta övningar som fastnar i minnet",
           "Grammatik, enkelt förklarad", "Skriv hela meningar själv",
           "Berättelser: tryck på okända ord", "Repetera innan du glömmer"],
    "nl": ["Elke dag een stukje Bosnisch", "65 levels – van hallo tot het loket",
           "Hoor hoe elk woord klinkt", "Korte oefeningen die blijven hangen",
           "Grammatica, helder uitgelegd", "Schrijf zelf hele zinnen",
           "Verhalen: tik aan wat je niet kent", "Herhalen voordat je het vergeet"],
    "nb": ["Litt bosnisk hver dag", "65 nivåer – fra hei til byråkratiet",
           "Hør hvert eneste ord", "Korte øvelser som sitter",
           "Grammatikk, enkelt forklart", "Skriv hele setninger selv",
           "Historier: Trykk på et ord og forstå", "Repeter før du glemmer"],
    "da": ["Lidt bosnisk hver dag", "65 niveauer – fra hej til kommunen",
           "Hør hvert eneste ord", "Korte øvelser, der bliver hængende",
           "Grammatik, enkelt forklaret", "Skriv selv hele sætninger",
           "Historier: tryk på et ord, forstå det", "Gentag, før du glemmer det"],
    "fr": ["Un peu de bosnien chaque jour", "65 niveaux – du bonjour à la paperasse",
           "Écoute chaque mot", "Exercices courts qui restent en tête",
           "La grammaire, expliquée simplement", "Écris toi-même des phrases complètes",
           "Touche un mot, l’histoire s’éclaire", "Révise avant d’oublier"],
}

BREITE, HOEHE = 1080, 1920
BAND = 340                       # Höhe des Überschriftbands, knapp 18 %

SEITE = """<!doctype html><html lang="%(lang)s"><head><meta charset="utf-8">
<link rel="stylesheet" href="/schriften.css">
<style>
  html,body{margin:0;width:%(b)dpx;height:%(h)dpx;overflow:hidden}
  body{background:linear-gradient(160deg,#0B1330 0%%,#14265E 55%%,#1E3FA8 100%%);
       font-family:Nunito,system-ui,sans-serif}
  .band{position:absolute;left:0;top:0;width:100%%;height:%(band)dpx;display:flex;
        align-items:center;justify-content:center;box-sizing:border-box;padding:24px 70px 0}
  .band h1{margin:0;color:#fff;font-weight:800;font-size:74px;line-height:1.1;
           text-align:center;letter-spacing:-0.5px;text-wrap:balance}
  .punkt{color:#FFD23F}
  .bild{position:absolute;left:50%%;top:%(band)dpx;transform:translateX(-50%%);
        height:%(bh)dpx;border-radius:46px;overflow:hidden;
        box-shadow:0 24px 70px rgba(0,0,0,.5),0 0 0 6px rgba(255,255,255,.08)}
  .bild img{display:block;height:100%%}
</style></head><body>
<div class="band"><h1 id="t"></h1></div>
<div class="bild"><img id="i"></div>
</body></html>"""

# Tablets: dieselbe Überschrift, darunter der Bildschirm (16:10 hochkant, aus
# bilder_playwright.py --geraet ...) in einem schlichten dunklen Rahmen mit
# Kamerapunkt. Gesetzt wird immer auf 1080 x 1920 CSS-Punkten; das 10-Zoll-
# Bild entsteht daraus mit Pixeldichte 4/3 (1440 x 2560), damit beide gleich
# aussehen. Schirm 900 x 1440, Rahmen 30, unten bleiben 80 Punkte Luft.
SEITE_TABLET = """<!doctype html><html lang="%(lang)s"><head><meta charset="utf-8">
<link rel="stylesheet" href="/schriften.css">
<style>
  html,body{margin:0;width:%(b)dpx;height:%(h)dpx;overflow:hidden}
  body{background:linear-gradient(160deg,#0B1330 0%%,#14265E 55%%,#1E3FA8 100%%);
       font-family:Nunito,system-ui,sans-serif}
  .band{position:absolute;left:0;top:0;width:100%%;height:%(band)dpx;display:flex;
        align-items:center;justify-content:center;box-sizing:border-box;padding:24px 70px 0}
  .band h1{margin:0;color:#fff;font-weight:800;font-size:74px;line-height:1.1;
           text-align:center;letter-spacing:-0.5px;text-wrap:balance}
  .platz{position:absolute;left:0;right:0;top:%(band)dpx;display:flex;justify-content:center}
  .tablet{position:relative;padding:%(rand)dpx;border-radius:56px;background:#070A17;
          box-shadow:0 24px 70px rgba(0,0,0,.55),0 0 0 3px rgba(255,255,255,.16),
                     inset 0 0 0 2px rgba(255,255,255,.05)}
  .tablet::before{content:"";position:absolute;left:50%%;top:%(kamera)dpx;width:10px;height:10px;
          margin-left:-5px;border-radius:50%%;background:#283258}
  .schirm{height:%(sh)dpx;border-radius:16px;overflow:hidden}
  .schirm img{display:block;height:100%%}
</style></head><body>
<div class="band"><h1 id="t"></h1></div>
<div class="platz"><div class="tablet"><div class="schirm"><img id="i"></div></div></div>
</body></html>"""

# Je Gerät: Vorsatz im Dateinamen, Pixeldichte beim Abfotografieren, Vorlage.
GERAETE = {
    "handy":    {"vorsatz": "",       "dichte": 1,     "seite": "handy"},
    "tablet7":  {"vorsatz": "tab7_",  "dichte": 1,     "seite": "tablet"},   # 1080 x 1920
    "tablet10": {"vorsatz": "tab10_", "dichte": 4 / 3, "seite": "tablet"},   # 1440 x 2560
}


async def sitzung(ws_url, basis, roh, ziel, sprache, geraet="handy"):
    import websockets
    g = GERAETE[geraet]
    async with websockets.connect(ws_url, max_size=256 * 1024 * 1024) as ws:
        n = [0]

        async def ruf(m, p=None):
            n[0] += 1
            mid = n[0]
            await ws.send(json.dumps({"id": mid, "method": m, "params": p or {}}))
            while True:
                a = json.loads(await ws.recv())
                if a.get("id") == mid:
                    return a

        async def js(code, zeit=60):
            a = await asyncio.wait_for(ruf("Runtime.evaluate", {
                "expression": "(async()=>{ %s })()" % code,
                "returnByValue": True, "awaitPromise": True}), zeit)
            r = a.get("result", {})
            if r.get("exceptionDetails"):
                raise RuntimeError(json.dumps(r["exceptionDetails"], ensure_ascii=False)[:600])
            return r.get("result", {}).get("value")

        await ruf("Page.enable")
        await ruf("Emulation.setDeviceMetricsOverride",
                  {"width": BREITE, "height": HOEHE, "deviceScaleFactor": g["dichte"], "mobile": False})
        os.makedirs(ziel, exist_ok=True)
        namen = [name for name, _ in BP.SCHRITTE]
        texte = UEBERSCHRIFTEN[sprache]

        # Gleicher Ursprung wie web/, damit schriften.css und die Schriften laden.
        await ruf("Page.navigate", {"url": basis + "/leer"})
        await asyncio.sleep(1.0)
        if g["seite"] == "tablet":
            seite = SEITE_TABLET % {"lang": sprache, "b": BREITE, "h": HOEHE, "band": BAND,
                                    "rand": 30, "kamera": 10, "sh": 1440}
        else:
            seite = SEITE % {"lang": sprache, "b": BREITE, "h": HOEHE, "band": BAND,
                             "bh": HOEHE - BAND - 46}
        for name, text in zip(namen, texte):
            pfad = os.path.join(roh, name + ".png")
            daten = base64.b64encode(open(pfad, "rb").read()).decode("ascii")
            breite_text = await js("""
                document.open(); document.write(%s); document.close();
                const h = document.getElementById('t');
                h.textContent = %s;
                const img = document.getElementById('i');
                img.src = 'data:image/png;base64,%s';
                await img.decode(); await document.fonts.ready;
                // Zu lange Zeilen: Schrift kleiner, bis zwei Zeilen reichen.
                let px = 74;
                while(h.getBoundingClientRect().height > 2.3 * px * 1.1 && px > 48){
                  px -= 2; h.style.fontSize = px + 'px';
                }
                return px;""" % (json.dumps(seite), json.dumps(text), daten))
            a = await asyncio.wait_for(ruf("Page.captureScreenshot", {
                "format": "png", "clip": {"x": 0, "y": 0, "width": BREITE, "height": HOEHE, "scale": 1}}), 60)
            aus = os.path.join(ziel, "%s_%s%s.png" % (sprache, g["vorsatz"], name))
            open(aus, "wb").write(base64.b64decode(a["result"]["data"]))
            print("  %s %-16s %spx  %s" % (sprache, name, breite_text, text), flush=True)

        if geraet != "handy":
            return
        # Feature-Grafik in derselben Sprache
        await ruf("Page.navigate", {"url": basis + "/_feature.html?sprache=" + sprache})
        for _ in range(60):
            await asyncio.sleep(0.5)
            try:
                if await js("return !!window._fertig", 5):
                    break
            except Exception:
                pass
        jpg = await js("return document.getElementById('bild').toDataURL('image/jpeg', 0.92)")
        aus = os.path.join(ziel, "%s_feature.jpg" % sprache)
        open(aus, "wb").write(base64.b64decode(jpg.split(",", 1)[1]))
        print("  %s feature.jpg  Drache: %s" % (sprache, await js("return window._drache")), flush=True)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    geraet = "handy"
    if "--geraet" in argv:
        i = argv.index("--geraet")
        geraet = argv[i + 1] if i + 1 < len(argv) else ""
        del argv[i:i + 2]
        if geraet not in GERAETE:
            raise SystemExit("--geraet: eines von %s" % ", ".join(GERAETE))
    if len(argv) < 3:
        raise SystemExit(__doc__)
    roh, ziel, sprachen = argv[0], argv[1], argv[2:]
    fremd = [s for s in sprachen if s not in UEBERSCHRIFTEN]
    if fremd:
        raise SystemExit("Keine Überschriften für: %s" % ", ".join(fremd))
    srv, basis = BP.server_starten()
    profil = tempfile.mkdtemp(prefix="zmaj_chrome_")
    chrome = subprocess.Popen([CHROME, "--headless=new", "--remote-debugging-port=%d" % TOR,
                               "--user-data-dir=" + profil, "--no-first-run",
                               "--hide-scrollbars", "about:blank"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen("http://127.0.0.1:%d/json/version" % TOR, timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        for s in sprachen:
            neu = json.load(urllib.request.urlopen(urllib.request.Request(
                "http://127.0.0.1:%d/json/new?about:blank" % TOR, method="PUT"), timeout=5))
            asyncio.run(sitzung(neu["webSocketDebuggerUrl"], basis,
                                os.path.join(roh, s), os.path.join(ziel, s), s, geraet))
            urllib.request.urlopen("http://127.0.0.1:%d/json/close/%s" % (TOR, neu["id"]), timeout=5)
    finally:
        chrome.terminate()
        srv.shutdown()
        time.sleep(1)
        shutil.rmtree(profil, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
