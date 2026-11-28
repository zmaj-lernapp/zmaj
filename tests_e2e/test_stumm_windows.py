# -*- coding: utf-8 -*-
"""WebKit stumm im Lautstaerkemixer von Windows (21.11.2026).

Ajdin hoerte waehrend der Browsertests bosnische Woerter. Chromium hat
--mute-audio, WebKit von Playwright nicht. stumm_windows.py schaltet seine
Audio-Sitzungen deshalb im Lautstaerkemixer stumm (webkit_stumm in
conftest.py). Hier spielt nur Stille, zu hoeren ist also nie etwas:

- eine neue Sitzung von WebKit ist stumm, und zwar schon beim ersten Blick,
  bevor der Stummschalter sie anfasst: Windows hat es sich vom vorlauf der
  webkit-Fixture gemerkt (je Programmpfad und Ausgabegeraet)
- die Sitzungen anderer Programme bleiben, wie sie waren
- erkannt wird nur der Ordner von WebKit, auch umgeleitet in ein App-Paket
- Pruefung vom 21.11.2026: die Systemklaenge, Sitzungen ohne Prozess und
  Sitzungen mit fremder Kennung fasst er nie an, auch nicht, wenn WebKit
  ihre Nummer bekommt - mit nachgestellten Werten und gegen die echte
  Sitzungsliste (trocken und wirklich)
"""
import os
import sys
import time

import pytest

import stumm_windows

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="den Lautstaerkemixer gibt es nur unter Windows")

# Nachgestellt nach der Messung vom 21.11.2026 (Ajdins Laptop)
LOKAL = "C:\\Users\\Probe\\AppData\\Local"
LAUFWERKE = {"\\Device\\HarddiskVolume3": "C:"}
GERAET = "{0.0.0.00000000}.{08a31c40-1eb6-4bd8-a244-1ccae7ae1302}"
NULL = "{00000000-0000-0000-0000-000000000000}"
SYSTEMKLAENGE = GERAET + "|#%b{A9EF3FD9-4240-455E-A4D5-F2B3301887B2}"
WEBKIT = LOKAL + "\\ms-playwright\\webkit-2359\\WebKitWebProcess.exe"
UMGELEITET = (LOKAL + "\\Packages\\Claude_pzs8sxrjxfjjc\\LocalCache\\Local\\ms-playwright\\webkit-2359"
              "\\WebKitWebProcess.exe")
CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"


def kennung(pfad, geraet="\\Device\\HarddiskVolume3"):
    """Kennung einer Sitzung, wie Windows sie fuer ein Programm bildet."""
    return GERAET + "|" + geraet + pfad[2:] + "%b" + NULL


def werte(**neu):
    """Eine Sitzung von WebKit, wie sie sein soll - mit Abweichungen."""
    w = {"pid_hr": stumm_windows.S_OK, "pid": 4711, "system_hr": stumm_windows.S_FALSE,
         "kennung": kennung(WEBKIT), "pfad": WEBKIT}
    w.update(neu)
    return w


@pytest.fixture
def muster(monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", LOKAL)
    monkeypatch.setenv("APPDATA", "C:\\Users\\Probe\\AppData\\Roaming")
    return stumm_windows._ordner_muster(LOKAL + "\\ms-playwright\\webkit-2359")


@pytest.fixture
def webkit_ordner(playwright_sitzung):
    ordner = os.path.dirname(playwright_sitzung.webkit.executable_path or "")
    if not ordner or not os.path.isdir(ordner):
        pytest.skip("WebKit fehlt")
    return ordner


def _runden(st, n, sekunden=10.0):
    ende = time.monotonic() + sekunden
    while st.runden < n and time.monotonic() < ende:
        time.sleep(0.02)
    assert st.runden >= n, st.fehler


def _von_webkit(kennung_text, muster, laufwerke):
    programm = stumm_windows._kennung_programm(kennung_text, laufwerke)
    return bool(programm and stumm_windows._darin(programm, muster))


def _systemklaenge(liste):
    return sorted((s["geraet"], s["stumm"]) for s in liste if s["system_hr"] == stumm_windows.S_OK)


def _unveraendert(vorher, nachher, muster, laufwerke):
    """Jede Sitzung, die nicht von WebKit ist, ist stumm oder nicht wie vorher."""
    alt = {}
    for s in vorher:
        alt.setdefault((s["geraet"], s["pid"], s["kennung"]), set()).add(s["stumm"])
    for s in nachher:
        schluessel = (s["geraet"], s["pid"], s["kennung"])
        if schluessel in alt and not _von_webkit(s["kennung"], muster, laufwerke):
            assert s["stumm"] in alt[schluessel], s


def test_neue_webkit_sitzung_ist_von_anfang_an_stumm(webkit, webkit_stumm):
    vorher = {(s["pid"], s["geraet"]): s for s in stumm_windows.auflisten()}
    bekannt = {(s["pid"], s["geraet"]) for s in webkit_stumm.bericht()}
    gespielt, stumm = stumm_windows.vorlauf(webkit, webkit_stumm)
    assert gespielt == "spielt" and stumm, (gespielt, webkit_stumm.bericht(), webkit_stumm.fehler)
    neu = [s for s in webkit_stumm.bericht() if (s["pid"], s["geraet"]) not in bekannt]
    assert neu and all(s["zuerst_stumm"] and s["stumm"] for s in neu), neu
    assert {s["programm"] for s in neu} <= {"WebKitWebProcess.exe", "WebKitGPUProcess.exe", "Playwright.exe"}, neu
    assert webkit_stumm.fehler == []
    # Fremde Programme: stumm oder nicht wie vorher (Ajdins Musik, Chrome, ...)
    for s in stumm_windows.auflisten():
        alt = vorher.get((s["pid"], s["geraet"]))
        if alt and alt["pfad"] == s["pfad"] and (s["pid"], s["geraet"]) not in bekannt:
            assert s["stumm"] == alt["stumm"], (s, alt)


def test_nur_der_ordner_von_webkit():
    lokal = os.environ["LOCALAPPDATA"]
    muster = stumm_windows._ordner_muster(os.path.join(lokal, "ms-playwright", "webkit-2359"))

    def darin(*teile):
        return stumm_windows._darin(os.path.join(*teile), muster)

    assert darin(lokal, "ms-playwright", "webkit-2359", "WebKitWebProcess.exe")
    assert darin(lokal, "MS-PLAYWRIGHT", "webkit-2359", "WebKitGPUProcess.exe")
    # Python in einem App-Paket (MSIX): der Prozess laeuft aus der Umleitung
    assert darin(lokal, "Packages", "Ein.Paket_abc123", "LocalCache", "Local", "ms-playwright", "webkit-2359",
                 "WebKitWebProcess.exe")
    assert not darin(lokal, "ms-playwright", "webkit-23590", "WebKitWebProcess.exe")
    assert not darin(lokal, "ms-playwright", "ffmpeg-1011", "ffmpeg.exe")
    assert not darin(lokal, "ms-playwright", "webkit-2359.exe")
    assert not darin(lokal, "Packages", "Ein.Paket", "Tiefer", "LocalCache", "Local", "ms-playwright", "webkit-2359",
                     "WebKitWebProcess.exe")
    assert not darin("C:\\", "Program Files", "Google", "Chrome", "Application", "chrome.exe")


def test_stummschalter_braucht_vollen_pfad():
    # conftest.py, Pruefung 21.11.2026: aus "" machte os.path.abspath den Arbeitsordner
    for falsch in ("", None, "ms-playwright\\webkit-2359"):
        with pytest.raises(ValueError):
            stumm_windows.Stummschalter(falsch)


def test_kennung_nennt_das_programm():
    k = stumm_windows._kennung_programm
    assert k(kennung(WEBKIT), LAUFWERKE) == WEBKIT
    assert k(kennung(UMGELEITET), LAUFWERKE) == UMGELEITET
    assert k(kennung(WEBKIT), {"\\device\\harddiskvolume3\\": "C:"}) == WEBKIT
    assert k(GERAET + "|" + CHROME + "%b" + NULL, LAUFWERKE) == CHROME      # schon mit Laufwerk
    assert k(SYSTEMKLAENGE, LAUFWERKE) is None                              # statt des Pfads ein #
    assert k(SYSTEMKLAENGE + "|1%b#", LAUFWERKE) is None
    assert k(kennung(WEBKIT) + "|1%b4711", LAUFWERKE) is None               # Kennung der Instanz
    assert k(kennung(WEBKIT, "\\Device\\HarddiskVolume30"), LAUFWERKE) is None
    assert k(kennung(WEBKIT, "\\Device\\HarddiskVolume9"), LAUFWERKE) is None
    assert k(None, LAUFWERKE) is None
    assert k("", LAUFWERKE) is None
    assert k("Unsinn", LAUFWERKE) is None


def test_laufwerke_von_windows():
    laufwerke = stumm_windows._laufwerke()
    lw = os.path.splitdrive(os.environ["LOCALAPPDATA"])[0].upper()
    assert lw in laufwerke.values(), laufwerke
    assert all(g.startswith("\\device\\") for g in laufwerke), laufwerke


def test_stumm_nur_wenn_kennung_und_prozess_von_webkit_sind(muster):
    def darf(**neu):
        return stumm_windows._darf_stumm(werte(**neu), muster, LAUFWERKE)

    assert darf() == WEBKIT
    assert darf(kennung=kennung(UMGELEITET), pfad=UMGELEITET) == UMGELEITET       # App-Paket (MSIX)
    assert darf(kennung=GERAET + "|" + WEBKIT + "%b" + NULL) == WEBKIT
    # Die Systemklaenge, genau wie gemessen - und WebKit hat ihre Nummer bekommen
    assert darf(pid_hr=stumm_windows.AUDCLNT_S_NO_SINGLE_PROCESS, pid=2292,
                system_hr=stumm_windows.S_OK, kennung=SYSTEMKLAENGE) is None
    assert darf(system_hr=stumm_windows.S_OK) is None              # schon die Systemklaenge allein
    assert darf(system_hr=None) is None
    assert darf(kennung=SYSTEMKLAENGE) is None                     # schon die Kennung allein
    assert darf(pid_hr=stumm_windows.AUDCLNT_S_NO_SINGLE_PROCESS) is None
    assert darf(pid_hr=None) is None
    assert darf(pid=0) is None
    # Sitzung ohne Prozess (beendet oder nie einer)
    assert darf(pfad=None) is None
    # Sitzung eines beendeten fremden Programms, ihre Nummer hat jetzt WebKit
    assert darf(kennung=kennung(CHROME)) is None
    # Sitzung eines beendeten WebKit-Prozesses, ihre Nummer hat jetzt Chrome
    assert darf(pfad=CHROME) is None
    assert darf(kennung=None) is None
    assert darf(kennung="Unsinn") is None
    assert darf(kennung=kennung(WEBKIT, "\\Device\\HarddiskVolume30")) is None
    assert darf(kennung=kennung(WEBKIT.replace("webkit-2359", "webkit-23590"))) is None


def test_echte_sitzungen_trocken_als_haette_webkit_jede_nummer(webkit_ordner):
    """Gegen die echte Sitzungsliste, aber trocken (schaltet nichts): Hinter
    jeder Nummer laufe WebKit, der schlimmste Fall wiedervergebener Nummern.
    Gewaehlt werden trotzdem nur Sitzungen, deren Kennung WebKit nennt - nie
    die Systemklaenge, nie Chrome, Steam oder Claude, nie eine ohne Prozess."""
    muster = stumm_windows._ordner_muster(webkit_ordner)
    laufwerke = stumm_windows._laufwerke()
    programm = os.path.join(webkit_ordner, "WebKitWebProcess.exe")
    vorher = stumm_windows.auflisten()
    if not _systemklaenge(vorher):
        pytest.skip("keine Sitzung der Systemklaenge")
    geschaltet = []

    class Trocken(stumm_windows.Stummschalter):
        def _prozess_pfad(self, pid):
            return programm

        def _schalten(self, lautstaerke):
            geschaltet.append(lautstaerke)

    with Trocken(webkit_ordner) as st:
        _runden(st, 5)
    assert st.fehler == []
    for s in st.bericht():
        assert s["kennung"] and stumm_windows._darin(s["kennung"], muster), s
    nummern = {s["pid"] for s in vorher if s["system_hr"] == stumm_windows.S_OK}
    assert not nummern & {s["pid"] for s in st.bericht()}
    for s in vorher:          # dieselbe Entscheidung je echter Sitzung, ohne Thread
        if not _von_webkit(s["kennung"], muster, laufwerke):
            assert stumm_windows._darf_stumm(dict(s, pfad=programm), muster, laufwerke) is None, s
    nachher = stumm_windows.auflisten()
    assert _systemklaenge(nachher) == _systemklaenge(vorher)
    _unveraendert(vorher, nachher, muster, laufwerke)


def test_echte_sitzungen_systemklaenge_bleiben_wie_sie_sind(webkit_ordner):
    """Der echte Stummschalter zehn Runden gegen die echte Sitzungsliste: die
    Systemklaenge werden nicht stumm, keine fremde Sitzung aendert sich, und
    er fasst nur Sitzungen an, deren Kennung WebKit nennt."""
    muster = stumm_windows._ordner_muster(webkit_ordner)
    laufwerke = stumm_windows._laufwerke()
    vorher = stumm_windows.auflisten()
    if not _systemklaenge(vorher):
        pytest.skip("keine Sitzung der Systemklaenge")
    with stumm_windows.Stummschalter(webkit_ordner) as st:
        _runden(st, 10)
    nachher = stumm_windows.auflisten()
    assert st.fehler == []
    for s in st.bericht():
        assert s["kennung"] and stumm_windows._darin(s["kennung"], muster), s
    # je Geraet stumm oder nicht wie vorher: waren sie laut, sind sie es noch
    assert _systemklaenge(nachher) == _systemklaenge(vorher)
    _unveraendert(vorher, nachher, muster, laufwerke)
