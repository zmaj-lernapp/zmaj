# -*- coding: utf-8 -*-
"""Steuert die App in einem kopflosen Chrome am PC - fuer die Store-Bilder.

    pc.py js '<Rumpf mit return>'     laeuft als async Funktion in der Seite
    pc.py bild <datei.png>            Bildschirmfoto des sichtbaren Teils
    pc.py nav <adresse>               Seite laden

Die Bildschirmgroesse kommt aus BREITE, HOEHE und DSF (Punkte je CSS-Punkt).
Sie wird bei jedem Aufruf neu gesetzt: Chrome vergisst sie, sobald die
Verbindung zu ist. 360 x 640 mal 3 ergibt genau 1080 x 1920.
"""
import asyncio, base64, json, os, sys, urllib.request

TOR = "9444"
ZEIT = int(os.environ.get("ZEIT", "60"))


async def main():
    import websockets
    was, arg = sys.argv[1], sys.argv[2]
    seiten = json.load(urllib.request.urlopen("http://127.0.0.1:%s/json" % TOR, timeout=8))
    ziel = [s for s in seiten if s.get("type") == "page"]
    async with websockets.connect(ziel[0]["webSocketDebuggerUrl"], max_size=256 * 1024 * 1024) as ws:
        n = [0]

        async def ruf(methode, params):
            n[0] += 1
            await ws.send(json.dumps({"id": n[0], "method": methode, "params": params}))
            while True:
                a = json.loads(await ws.recv())
                if a.get("id") == n[0]:
                    return a

        await ruf("Emulation.setDeviceMetricsOverride", {
            "width": int(os.environ.get("BREITE", "360")),
            "height": int(os.environ.get("HOEHE", "640")),
            "deviceScaleFactor": float(os.environ.get("DSF", "3")),
            "mobile": True})
        await ruf("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})
        if was == "js":
            a = await asyncio.wait_for(ruf("Runtime.evaluate", {
                "expression": "(async()=>{ %s })()" % arg,
                "returnByValue": True, "awaitPromise": True}), ZEIT)
            r = a.get("result", {})
            if r.get("exceptionDetails"):
                print(json.dumps(r["exceptionDetails"], ensure_ascii=False)[:1200]); return 1
            w = r.get("result", {}).get("value")
            print(w if isinstance(w, str) else json.dumps(w, ensure_ascii=False, indent=1))
        elif was == "bild":
            a = await asyncio.wait_for(ruf("Page.captureScreenshot", {"format": "png"}), ZEIT)
            open(arg, "wb").write(base64.b64decode(a["result"]["data"]))
            print("gespeichert", arg)
        elif was == "nav":
            await ruf("Page.navigate", {"url": arg})
            print("geladen", arg)
    return 0


sys.exit(asyncio.run(main()))
