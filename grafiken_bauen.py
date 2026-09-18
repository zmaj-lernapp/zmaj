# -*- coding: utf-8 -*-
"""
grafiken_bauen.py  –  die Bilder für den Play Store

Google verlangt beim Hochladen ein App-Symbol in **512 × 512**. Das Symbol
in `web/` ist nur 256 Pixel groß und hat runde Ecken eingebacken – beides
geht im Store nicht: Google rundet selbst ab, sonst sieht es doppelt
gerundet aus.

Dieses Skript zeichnet die bosnische Flagge neu, quadratisch und ohne
runde Ecken, und legt sie unter `store/icon-512.png` ab.

Gezeichnet wird mit Bordmitteln – kein Zusatzpaket nötig. Geglättet wird
durch Überabtastung: Erst wird alles dreifach so groß gerechnet, dann
gemittelt. Dadurch werden die schrägen Kanten des Dreiecks und die
Sternzacken weich.

In Thonny öffnen und auf Run (F5) drücken.

---

Die zweite Grafik, die Google verlangt, ist der breite Banner oben auf der
Store-Seite: **1024 × 500**. Die kann dieses Skript nicht allein zeichnen,
weil dort Schrift und der Drache aus der Lottie-Datei vorkommen – beides
kann nur der Browser. Der Weg dafür:

    1. Die App starten (Desktop-Verknüpfung oder start.py)
    2. Hier unten ZWEITE_GRAFIK auf True stellen und das Skript laufen
       lassen. Es wartet dann auf das Bild.
    3. Im Browser http://localhost:8000/_feature.html öffnen.
       Die Seite zeichnet die Grafik und schickt sie hierher.
    4. Fertig: store/feature-1024x500.png

Das Aussehen der Bannergrafik steht in web/_feature.html – Farben, Text
und Größen lassen sich dort ändern.
"""

import base64
import math
import os
import struct
import zlib
from http.server import BaseHTTPRequestHandler, HTTPServer

ZWEITE_GRAFIK = False      # True: auf den Banner aus dem Browser warten
PORT = 8199

ORDNER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(ORDNER, "store")

# Farben wie in der App
BLAU_OBEN = (0x0B, 0x3B, 0xB0)
BLAU_UNTEN = (0x00, 0x20, 0x74)
GELB_OBEN = (0xFF, 0xD6, 0x33)
GELB_UNTEN = (0xF0, 0xB8, 0x00)
WEISS = (255, 255, 255)

UEBER = 3            # Überabtastung: 3 × 3 Punkte je Bildpunkt


def mischen(a, b, t):
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def verlauf(x, y, x0, y0, x1, y1, farbe_a, farbe_b):
    """Linearer Verlauf wie canvas.createLinearGradient."""
    dx, dy = x1 - x0, y1 - y0
    laenge = dx * dx + dy * dy
    if laenge == 0:
        return farbe_a
    t = ((x - x0) * dx + (y - y0) * dy) / laenge
    return mischen(farbe_a, farbe_b, t)


def stern_punkte(mx, my, r, zacken=5):
    """Fünfzackiger Stern, Spitze nach oben – wie in der App."""
    punkte = []
    for i in range(zacken * 2):
        winkel = -math.pi / 2 + i * math.pi / zacken
        rr = r * 0.42 if i % 2 else r
        punkte.append((mx + rr * math.cos(winkel), my + rr * math.sin(winkel)))
    return punkte


def im_vieleck(px, py, punkte):
    """Liegt der Punkt im Vieleck? (Strahlenverfahren)"""
    drin = False
    n = len(punkte)
    j = n - 1
    for i in range(n):
        xi, yi = punkte[i]
        xj, yj = punkte[j]
        if (yi > py) != (yj > py):
            if px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                drin = not drin
        j = i
    return drin


def flagge_zeichnen(S):
    """Gibt eine Liste von Zeilen zurück, jede Zeile eine Liste von (r,g,b)."""
    gross = S * UEBER
    ax, bx = gross * 0.22, gross * 0.88          # Dreieck: (ax,0) (bx,0) (bx,unten)
    dreieck = [(ax, 0), (bx, 0), (bx, gross)]

    # Sterne entlang der langen Dreieckskante
    dx, dy = bx - ax, float(gross)
    laenge = math.hypot(dx, dy)
    ux, uy = dx / laenge, dy / laenge
    nx, ny = -uy, ux
    abstand, radius = gross * 0.085, gross * 0.052
    sterne = []
    for i in range(11):
        t = (i - 0.5) / 10.0
        mx = ax + ux * laenge * t + nx * abstand
        my = uy * laenge * t + ny * abstand
        if my < -radius or my > gross + radius:
            continue
        punkte = stern_punkte(mx, my, radius)
        xs = [p[0] for p in punkte]
        ys = [p[1] for p in punkte]
        sterne.append((punkte, min(xs), max(xs), min(ys), max(ys)))

    zeilen = []
    for y in range(gross):
        yc = y + 0.5
        zeile = []
        # welche Sterne können diese Zeile überhaupt treffen?
        aktiv = [s for s in sterne if s[3] <= yc <= s[4]]
        for x in range(gross):
            xc = x + 0.5
            if xc >= ax and im_vieleck(xc, yc, dreieck):
                farbe = verlauf(xc, yc, ax, 0, bx, gross, GELB_OBEN, GELB_UNTEN)
            else:
                farbe = verlauf(xc, yc, 0, 0, gross * 0.35, gross, BLAU_OBEN, BLAU_UNTEN)
            for punkte, x0, x1, y0, y1 in aktiv:
                if x0 <= xc <= x1 and im_vieleck(xc, yc, punkte):
                    farbe = WEISS
                    break
            zeile.append(farbe)
        zeilen.append(zeile)
    return zeilen


def verkleinern(zeilen, S):
    """UEBER × UEBER Punkte zu einem mitteln – das glättet die Kanten."""
    fertig = []
    teiler = UEBER * UEBER
    for y in range(S):
        zeile = bytearray()
        for x in range(S):
            r = g = b = 0
            for dy in range(UEBER):
                quelle = zeilen[y * UEBER + dy]
                for dx in range(UEBER):
                    p = quelle[x * UEBER + dx]
                    r += p[0]; g += p[1]; b += p[2]
            zeile += bytes((r // teiler, g // teiler, b // teiler))
        fertig.append(bytes(zeile))
    return fertig


def png_schreiben(pfad, zeilen, breite, hoehe):
    """Schreibt ein PNG ohne Durchsichtigkeit (Google will das so)."""
    roh = b"".join(b"\x00" + z for z in zeilen)     # Filterbyte 0 je Zeile

    def block(kennung, daten):
        teil = kennung + daten
        return struct.pack(">I", len(daten)) + teil + struct.pack(">I", zlib.crc32(teil) & 0xFFFFFFFF)

    kopf = struct.pack(">IIBBBBB", breite, hoehe, 8, 2, 0, 0, 0)   # 8 Bit, Farbtyp 2 = RGB
    datei = (b"\x89PNG\r\n\x1a\n" + block(b"IHDR", kopf)
             + block(b"IDAT", zlib.compress(roh, 9)) + block(b"IEND", b""))
    with open(pfad, "wb") as f:
        f.write(datei)
    return len(datei)


class Empfang(BaseHTTPRequestHandler):
    """Nimmt den Banner entgegen, den web/_feature.html im Browser zeichnet."""

    def _kopf(self, status=200):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

    def do_OPTIONS(self):
        self._kopf()

    def do_POST(self):
        laenge = int(self.headers.get("Content-Length", 0))
        daten = self.rfile.read(laenge).decode("utf-8")
        if "," in daten:
            daten = daten.split(",", 1)[1]
        roh = base64.b64decode(daten)
        os.makedirs(ZIEL, exist_ok=True)
        pfad = os.path.join(ZIEL, "feature-1024x500.png")
        with open(pfad, "wb") as f:
            f.write(roh)
        print("Fertig: store/feature-1024x500.png  %d Bytes" % len(roh))
        self._kopf()
        self.wfile.write(b"ok")
        raise SystemExit(0)

    def log_message(self, *a):
        pass


def auf_banner_warten():
    print("Warte auf den Banner aus dem Browser …")
    print("Jetzt http://localhost:8000/_feature.html öffnen.")
    print("(Die App muss dafür laufen.)")
    try:
        HTTPServer(("127.0.0.1", PORT), Empfang).serve_forever()
    except SystemExit:
        pass
    except OSError as e:
        print("Port %d ist belegt (%s). Läuft das Skript schon?" % (PORT, e))


if __name__ == "__main__":
    if ZWEITE_GRAFIK:
        auf_banner_warten()
        raise SystemExit(0)

    os.makedirs(ZIEL, exist_ok=True)
    S = 512
    print("Zeichne das App-Symbol %d × %d (mit %d-facher Überabtastung) …" % (S, S, UEBER))
    gross = flagge_zeichnen(S)
    zeilen = verkleinern(gross, S)
    pfad = os.path.join(ZIEL, "icon-512.png")
    groesse = png_schreiben(pfad, zeilen, S, S)
    print("Fertig: store/icon-512.png  %d Bytes" % groesse)
    print()
    print("Das Bild ist quadratisch und ohne runde Ecken – die setzt Google")
    print("selbst. Beim Hochladen als „App-Symbol“ verwenden.")
