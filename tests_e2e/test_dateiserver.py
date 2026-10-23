# -*- coding: utf-8 -*-
"""Der Testserver haelt den Ansturm beim Start aus (22.10.2026).

Die E2E-Suite flackerte: bei jedem Lauf ein anderer Test in
test_mitlesen.py rot, jedes Mal mit "Failed to load resource:
net::ERR_CONNECTION_REFUSED @ .../app/maskottchen/teile/oberarmR.webp".
Mit den Aenderungen an der App hatte das nichts zu tun, der Stand vorher
flackerte genauso.

Die App holt beim Start die 32 Drachenteile auf einmal. Der Dateiserver
in conftest.py war ein schlichter socketserver.ThreadingTCPServer, und der
ruft listen() mit request_queue_size = 5 auf. Kommen mehr Verbindungen an,
als der Server gerade annehmen kann, lehnt Windows den Rest ab, der
Browser schreibt das als Fehler in die Konsole, und jeder Test, der eine
leere Konsole verlangt, wird rot.

Gemessen am 22.10.2026 unter Windows 11, 80 Verbindungen auf einmal, je
fuenf Laeufe: mit 5 wurden 27 bis 47 abgelehnt, mit 128 keine. Deshalb
benutzen conftest.py und test_barrierefreiheit.py jetzt beide den
Dateiserver aus conftest.py mit 128.
"""
import http.client
import threading
import urllib.parse

# Mehr als die 32 Drachenteile, weniger als die 128 der Warteschlange.
GLEICHZEITIG = 64
TEIL = "/app/maskottchen/teile/oberarmR.webp"


def test_viele_verbindungen_auf_einmal(basis):
    """Alle Verbindungen gleichzeitig aufbauen und offen halten, wie der
    Browser beim Start. Mit der alten Warteschlange brach ein Teil davon
    nach rund zwei Sekunden mit ConnectionRefusedError ab. Danach muss
    jede das Drachenteil liefern."""
    url = urllib.parse.urlsplit(basis)
    verbindungen = [http.client.HTTPConnection(url.hostname, url.port, timeout=10)
                    for _ in range(GLEICHZEITIG)]
    los = threading.Barrier(GLEICHZEITIG)
    abgelehnt = []

    def verbinden(v):
        los.wait()
        try:
            v.connect()
        except OSError as e:
            abgelehnt.append(repr(e))

    faeden = [threading.Thread(target=verbinden, args=(v,)) for v in verbindungen]
    try:
        for f in faeden:
            f.start()
        for f in faeden:
            f.join()
        assert not abgelehnt, "%d von %d abgelehnt, z. B. %s" % (len(abgelehnt), GLEICHZEITIG, abgelehnt[0])
        for v in verbindungen:
            v.request("GET", TEIL)
            antwort = v.getresponse()
            assert antwort.status == 200 and antwort.read()
    finally:
        for v in verbindungen:
            v.close()
