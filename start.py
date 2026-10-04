# -*- coding: utf-8 -*-
"""
start.py  –  DIESE DATEI IN THONNY ÖFFNEN UND AUF "RUN" (F5) DRÜCKEN

Was passiert dann?
  1. Die Inhaltsdateien werden geprüft (Tippfehler, doppelte Wörter).
  2. Ein kleiner Webserver startet auf deinem PC und liefert den Ordner web/ aus.
  3. Dein Browser öffnet die App automatisch.
  4. In der Thonny-Konsole steht eine zweite Adresse für das Handy
     (gleiches WLAN nötig).

Beenden: in Thonny auf "Stop" drücken (oder Strg+C in der Konsole).

Außerdem:  start.py --fehlende en   schreibt die Arbeitsliste fehlende_en.txt
mit allem, was in dieser Sprache noch nicht übersetzt ist.

Warum so schlank (04.10.2026): Hier stand bis dahin der alte Server aus der
Zeit mit Konten – Anmeldung, Passwörter, Sitzungen, Bestätigungsmails,
eine Fortschrittsdatei je Profil (dazu konten.py und mail.py). Die App läuft
seit dem 26.09.2026 ganz auf dem Gerät, die Konten sind aus (KONTEN_AN =
false in web/index.html), der Lernstand liegt im Browser. Der Kontoteil war
nur noch Ballast, der echte Dateien anlegen konnte. Übrig bleibt, was die
App am PC wirklich fragt: die Dateien aus web/ und /api/daten – der Inhalt,
bei jedem Aufruf frisch aus den Python-Dateien, damit eine Änderung an
vokabeln.py nach F5 im Browser sofort zu sehen ist. Antwortet /api/daten
nicht, nimmt die App web/inhalt/<code>.json, genau wie auf dem Handy.

Der Inhalt selbst entsteht in inhalt.py. lade_daten() und die Prüfungen
werden hier nur durchgereicht, damit ältere Aufrufe wie start.lade_daten()
weiter funktionieren.

Es werden nur Bausteine benutzt, die Python schon mitbringt.
Nichts muss installiert werden.
"""

import json
import os
import socket
import sys
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------------------
# Pfade: alles relativ zu dieser Datei, egal von wo das Skript gestartet wird
# ---------------------------------------------------------------------------
ORDNER = os.path.dirname(os.path.abspath(__file__))
WEB_ORDNER = os.path.join(ORDNER, "web")
LOG_DATEI = os.path.join(ORDNER, "start.log")
PORT_START = 8000

# Wird die App über die Desktop-Verknüpfung (pythonw, ohne Fenster) gestartet,
# gibt es keine Konsole. Dann landen alle Meldungen in start.log.
if sys.stdout is None or sys.stderr is None:
    _log = open(LOG_DATEI, "w", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = _log

sys.path.insert(0, ORDNER)
import sprachen        # noqa: E402  (nach sys.path-Änderung importieren)
import uebersetzungen  # noqa: E402
# Durchgereicht für alle, die noch start.lade_daten() usw. aufrufen.
from inhalt import (  # noqa: E402,F401
    eigene_aufnahmen, fehlende_woerter, lade_daten, maskottchen_bilder,
    mit_kennung, pruefe_vokabeln,
)


def oeffne_browser(url):
    """Bevorzugt Microsoft Edge: nur dort gibt es bosnische Stimmen (Goran, Vesna)
    für das Vorlesen. Sonst der Standard-Browser."""
    import subprocess
    for pfad in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                 r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(pfad):
            try:
                subprocess.Popen([pfad, url])
                return
            except OSError:
                break
    webbrowser.open(url)


# ---------------------------------------------------------------------------
# Der Webserver: Dateien aus web/ und der Inhalt unter /api/daten
# ---------------------------------------------------------------------------
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_ORDNER, **kwargs)

    def _json(self, objekt, status=200):
        body = json.dumps(objekt, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _sprache(self):
        """Sprachkürzel aus ?sprache=... in der Adresse, sonst Deutsch."""
        from urllib.parse import urlparse, parse_qs
        werte = parse_qs(urlparse(self.path).query).get("sprache", [])
        code = werte[0][:5] if werte else ""
        return code if sprachen.ist_sprache(code) else sprachen.GRUNDSPRACHE

    def do_GET(self):
        if self.path.startswith("/api/daten"):
            return self._json(lade_daten(self._sprache()))
        if self.path == "/":
            self.path = "/index.html"
        elif self.path.startswith("/favicon.ico"):
            self.path = "/icon.ico"       # danach fragt der Browser von selbst
        return super().do_GET()

    # Kein do_POST mehr (04.10.2026): Konten, Fortschritt und Feedback liefen
    # früher über POST an diesen Server. Mit KONTEN_AN = false schickt die
    # App nichts mehr hierher; Feedback geht per Mailprogramm des Geräts.

    def end_headers(self):
        # Browser soll index.html, Symbol und Maskottchen nicht zwischenspeichern,
        # damit Änderungen sofort sichtbar sind
        if self.path.endswith((".html", ".ico", ".json")) or self.path == "/" or "icon-256" in self.path or "flagge" in self.path:
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format, *args):
        # Nur Fehler in die Konsole, nicht jeden einzelnen Aufruf
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(format, *args)


def lokale_ip():
    """Adresse dieses PCs im WLAN, damit das Handy die App öffnen kann."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # es wird nichts gesendet, nur die Route ermittelt
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None


def starte_server():
    # Windows lässt zwei Server auf demselben Port zu, wenn allow_reuse_address gesetzt ist.
    # Dann antwortet die alte Instanz weiter. Deshalb aus, und den Port vorher prüfen.
    ThreadingHTTPServer.allow_reuse_address = False
    for port in range(PORT_START, PORT_START + 20):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)
        belegt = s.connect_ex(("127.0.0.1", port)) == 0
        s.close()
        if belegt:
            continue
        try:
            return ThreadingHTTPServer(("0.0.0.0", port), Handler), port
        except OSError:
            continue
    raise RuntimeError("Kein freier Port gefunden (8000–8019).")


def laeuft_schon():
    """Läuft die App bereits? Dann nur den Browser öffnen statt ein zweites Mal starten."""
    import urllib.request
    for port in range(PORT_START, PORT_START + 20):
        # Erst schnell schauen, ob überhaupt etwas auf dem Port lauscht
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.2)
        offen = s.connect_ex(("127.0.0.1", port)) == 0
        s.close()
        if not offen:
            if port == PORT_START:
                return None   # 8000 ist frei, also läuft die App nicht (sie nimmt immer den ersten freien Port)
            continue
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/daten", timeout=1) as r:
                if b'"kategorien"' in r.read(200000):
                    return port
        except Exception:
            continue
    return None


def sprachen_bericht(daten):
    """Zeigt, wie weit die einzelnen Sprachen übersetzt sind."""
    if sprachen.anbieter_fehlt():
        print("Hinweis: In sprachen.py steht bei ANBIETER noch ein Platzhalter.")
        print("  Vor einer Veröffentlichung dort Name, Anschrift und E-Mail eintragen –")
        print("  sonst sind Impressum und Datenschutzerklärung unvollständig.")
    if sprachen.ustidnr_fehlt():
        print("Hinweis: Im Impressum (ANBIETER in sprachen.py) fehlt die USt-IdNr.")
        print("  Sie kommt per Post vom Bundeszentralamt für Steuern – beantragt am")
        print("  14.09.2026 über den ELSTER-Fragebogen. Sobald der Brief da ist,")
        print("  gehört sie hinein: § 5 Abs. 1 Nr. 6 DDG verlangt sie, sobald man")
        print("  eine hat. Vorher fehlt nichts.")
    namen = ", ".join(f"{s['name']} ({s['code']})" for s in sprachen.SPRACHEN)
    print(f"Sprachen: {namen}")
    for s in sprachen.SPRACHEN:
        code = s["code"]
        if code == sprachen.GRUNDSPRACHE:
            continue
        fehlt_ui = len(sprachen.fehlende_texte(code))
        fertig, gesamt = uebersetzungen.stand(daten, code)
        prozent = round(fertig / gesamt * 100) if gesamt else 100
        hinweis = "vollständig" if not fehlt_ui else f"{fehlt_ui} Texte fehlen"
        print(f"  {code}: Oberfläche {hinweis} · Lerninhalte {fertig} von {gesamt} ({prozent} %)")
    print("  Arbeitsliste für eine Sprache schreiben:  start.py --fehlende en")


def arbeitsliste(code):
    """Schreibt fehlende_<code>.txt: alles, was in dieser Sprache noch fehlt,
    schon im Format von uebersetzungen.py. Zum Ausfüllen und Hineinkopieren."""
    daten = lade_daten(sprachen.GRUNDSPRACHE)
    f = uebersetzungen.fehlende(daten, code)
    woerter, _ = uebersetzungen.sammle(daten)
    ziel = os.path.join(ORDNER, f"fehlende_{code}.txt")
    with open(ziel, "w", encoding="utf-8") as datei:
        datei.write(f"# Noch nicht uebersetzt: {code}\n")
        datei.write("# Rechts hinter dem Doppelpunkt die Uebersetzung eintragen\n")
        datei.write("# und den Block nach uebersetzungen.py kopieren.\n\n")
        datei.write('"woerter": {\n')
        for bs in f["woerter"]:
            datei.write('    %r: "",   # deutsch: %s\n' % (bs, woerter.get(bs, "")))
        datei.write("},\n\n")
        datei.write('"texte": {\n')
        for text in f["texte"]:
            datei.write('    %r: "",\n' % text)
        datei.write("},\n")
    print(f"{len(f['woerter'])} Wörter und {len(f['texte'])} Texte fehlen.")
    print(f"Arbeitsliste geschrieben: {ziel}")


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--fehlende":
        return arbeitsliste(sys.argv[2])

    print("=" * 60)
    print("  Zmaj  –  Bosnisch lernen")
    print("=" * 60)

    port = laeuft_schon()
    if port:
        print(f"Die App läuft schon auf http://localhost:{port} – öffne nur den Browser.")
        oeffne_browser(f"http://localhost:{port}")
        return

    daten = lade_daten()
    anzahl = sum(len(k["words"]) for k in daten["kategorien"])
    print(f"Vokabeln geladen: {len(daten['kategorien'])} Levels, "
          f"{anzahl} Wörter, {len(daten['saetze'])} Lückentexte")
    sektion_namen = {s["id"]: s["label"] for s in daten.get("sektionen", [])}
    letzte = None
    for nr, kat in enumerate(daten["kategorien"], start=1):
        if kat.get("sektion") != letzte:
            letzte = kat.get("sektion")
            print(f"\n{sektion_namen.get(letzte, letzte)}")
        print(f"  Level {nr:2d}  {kat['label']:<28} {len(kat['words']):3d} Wörter")
    print()

    print(f"Grammatik-Lektionen: {len(daten['grammatik'])}, Geschichten: {len(daten['geschichten'])}")
    sprachen_bericht(daten)
    probleme = pruefe_vokabeln(daten)
    if probleme:
        print("\nHinweise zu den Inhaltsdateien:")
        for p in probleme:
            print("  -", p)
    else:
        print("Inhaltsdateien sehen gut aus.")
    fehlt = fehlende_woerter(daten)
    if fehlt:
        print("Wörter in Geschichten ohne Eintrag im WOERTERBUCH (beim Antippen fehlt die Übersetzung):")
        for gid, woerter in fehlt.items():
            print(f"  - {gid}: {', '.join(sorted(woerter))}")

    server, port = starte_server()
    url_pc = f"http://localhost:{port}"
    ip = lokale_ip()

    print()
    print(f"Am PC:     {url_pc}")
    if ip:
        print(f"Am Handy:  http://{ip}:{port}   (gleiches WLAN)")
    print()
    print("Der Lernstand liegt im Browser (wie auf dem Handy), nicht auf dem PC.")
    print("Beenden: Stop in Thonny oder Strg+C.")
    print("-" * 60)

    aufnahmen = eigene_aufnahmen()
    print(f"Eigene Aufnahmen in web/audio: {len(aufnahmen)}" + ("" if aufnahmen else "  (noch keine – Computerstimme wird benutzt)"))
    threading.Timer(0.6, lambda: oeffne_browser(url_pc)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("Server beendet.")


if __name__ == "__main__":
    main()
