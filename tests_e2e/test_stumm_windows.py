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
"""
import os
import sys

import pytest

import stumm_windows

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="den Lautstaerkemixer gibt es nur unter Windows")


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
