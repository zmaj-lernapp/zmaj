# -*- coding: utf-8 -*-
"""WebKit stumm im Lautstaerkemixer von Windows (21.11.2026).

Chromium bekommt --mute-audio (browser in conftest.py). WebKit von
Playwright hat kein Gegenstueck und spielt unter Windows MP3 und WAV hoerbar
ab: Ajdin hoerte waehrend der Browsertests bosnische Woerter aus den
Laptop-Lautsprechern. Ajdin: "3. ja" auf den Vorschlag, dass das
Testprogramm WebKit im Lautstaerkemixer von Windows selbst stumm schaltet.

Das tut Stummschalter: ein Hintergrund-Thread schaut alle 100 ms ueber die
Core Audio API von Windows (IMMDeviceEnumerator -> IAudioSessionManager2 ->
Audio-Sitzungen) nach und schaltet jede Sitzung stumm (ISimpleAudioVolume.
SetMute), die aus dem Ordner kommt, den man ihm gibt - in der Suite der
Ordner von WebKit unter ms-playwright (WebKitWebProcess.exe und seine
Geschwister). Andere Programme fasst er nie an, auch nicht Chrome, die
Systemklaenge oder Ajdins Musik. Alles ueber ctypes, ohne neue Pakete
(comtypes fehlt im e2e-venv).

"Aus dem Ordner" heisst seit der Pruefung vom 21.11.2026 zweierlei (siehe
_darf_stumm): die Kennung der Sitzung nennt ein Programm darin, und der
Prozess hinter ihrer Nummer laeuft von dort. Die Nummer allein taugte
nicht - die Sitzung der Systemklaenge meldet eine Nummer ohne Prozess.

Windows merkt sich die Stummschaltung je Programmpfad und Ausgabegeraet
(wie im Lautstaerkemixer von Hand; sie steht in der Registry unter
HKCU\\Software\\Microsoft\\Internet Explorer\\LowRegistry\\Audio\\PolicyConfig\\
PropertyStore): Eine neue Sitzung von WebKitWebProcess.exe ist danach von
Anfang an stumm, auch in spaeteren Laeufen. Das ist gewollt - erst dadurch
ist schon der erste Ton eines neuen Prozesses still. Zurueck geht es im
Lautstaerkemixer (Einstellungen > System > Sound > Lautstaerkemixer) oder
mit einer neuen WebKit-Fassung, die in einem neuen Ordner liegt. Damit
auch der allererste Lauf nichts hoeren laesst, spielt die webkit-Fixture
vorab Stille (vorlauf) und wartet, bis deren Sitzung stumm ist.

Gemessen am 21.11.2026 mit Probetoenen von -76 und -66 dBFS: jede neue
Sitzung war beim ersten Blick schon stumm, und am Ausgabegeraet kam nur
sein Grundrauschen an (5e-5, genauso viel wie bei digitaler Stille). Der
Spitzenpegel einer Sitzung (IAudioMeterInformation, in sitzungen) zeigt,
was WebKit liefert, vor der Stummschaltung - er beweist also, dass etwas
spielte, nicht dass es zu hoeren war.

Ausserhalb von Windows tut das alles nichts.
"""
import http.server
import io
import json
import os
import re
import sys
import threading
import time
import uuid
import wave

AN = sys.platform == "win32"

S_OK = 0
S_FALSE = 1
# GetProcessId: die Sitzung gehoert nicht genau einem Prozess. So meldet
# sich die Sitzung der Systemklaenge, mit einer Nummer, zu der es keinen
# Prozess gibt (gemessen 21.11.2026: 2292).
AUDCLNT_S_NO_SINGLE_PROCESS = 0x0889000D

if AN:
    import ctypes
    from ctypes import wintypes

    class GUID(ctypes.Structure):
        _fields_ = [("d1", ctypes.c_uint32), ("d2", ctypes.c_uint16),
                    ("d3", ctypes.c_uint16), ("d4", ctypes.c_ubyte * 8)]

    def _guid(text):
        return GUID.from_buffer_copy(uuid.UUID(text).bytes_le)

    CLSID_MMDeviceEnumerator = _guid("BCDE0395-E52F-467C-8E3D-C4579291692E")
    IID_IMMDeviceEnumerator = _guid("A95664D2-9614-4F35-A746-DE8DB63617E6")
    IID_IAudioSessionManager2 = _guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F")
    IID_IAudioSessionControl2 = _guid("BFB7FF88-7239-4FC9-8FA2-07C950BE9C6D")
    IID_ISimpleAudioVolume = _guid("87CE5498-68D6-44E5-9215-6DA47EF883D8")
    IID_IAudioMeterInformation = _guid("C02216F6-8C67-4B5B-9D00-D008E73E0064")

    CLSCTX_ALL = 23
    E_RENDER = 0                  # Wiedergabe, nicht Aufnahme
    DEVICE_STATE_ACTIVE = 1
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    _ole32 = ctypes.WinDLL("ole32")
    _ole32.CoInitializeEx.argtypes = (ctypes.c_void_p, wintypes.DWORD)
    _ole32.CoInitializeEx.restype = ctypes.HRESULT
    _ole32.CoCreateInstance.argtypes = (ctypes.POINTER(GUID), ctypes.c_void_p, wintypes.DWORD,
                                        ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p))
    _ole32.CoCreateInstance.restype = ctypes.HRESULT
    _ole32.CoUninitialize.argtypes = ()
    _ole32.CoUninitialize.restype = None
    _ole32.CoTaskMemFree.argtypes = (ctypes.c_void_p,)
    _ole32.CoTaskMemFree.restype = None

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    _kernel32.OpenProcess.restype = wintypes.HANDLE
    _kernel32.QueryFullProcessImageNameW.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                                     ctypes.POINTER(wintypes.DWORD))
    _kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    _kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    _kernel32.CloseHandle.restype = wintypes.BOOL
    _kernel32.QueryDosDeviceW.argtypes = (wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD)
    _kernel32.QueryDosDeviceW.restype = wintypes.DWORD

    _P = ctypes.POINTER
    _VOID_PP = _P(ctypes.c_void_p)
    _ARTEN = {}

    class _Com(object):
        """Ein COM-Zeiger. rufe(nr, ...) ruft Methode nr der Tabelle
        (0-2 IUnknown); ein Fehler-HRESULT wirft OSError. los() gibt frei."""

        def __init__(self, zeiger):
            self.p = zeiger

        def rufe(self, nr, argtypes, *args):
            art = _ARTEN.get((nr, argtypes))
            if art is None:
                art = _ARTEN[(nr, argtypes)] = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, *argtypes)
            tabelle = ctypes.cast(ctypes.c_void_p(self.p), _P(_P(ctypes.c_void_p)))[0]
            return art(tabelle[nr])(self.p, *args)

        def frage(self, iid):
            """QueryInterface"""
            aus = ctypes.c_void_p()
            self.rufe(0, (_P(GUID), _VOID_PP), ctypes.byref(iid), ctypes.byref(aus))
            return _Com(aus.value)

        def los(self):
            if self.p:
                tabelle = ctypes.cast(ctypes.c_void_p(self.p), _P(_P(ctypes.c_void_p)))[0]
                ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(tabelle[2])(self.p)
                self.p = None

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.los()


def _pfad(pid):
    """Voller Pfad der Programmdatei eines Prozesses, sonst None."""
    h = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return None
    try:
        puffer = ctypes.create_unicode_buffer(1024)
        n = wintypes.DWORD(len(puffer))
        if _kernel32.QueryFullProcessImageNameW(h, 0, puffer, ctypes.byref(n)):
            return puffer.value
        return None
    finally:
        _kernel32.CloseHandle(h)


def _enumerator():
    aus = ctypes.c_void_p()
    _ole32.CoCreateInstance(ctypes.byref(CLSID_MMDeviceEnumerator), None, CLSCTX_ALL,
                            ctypes.byref(IID_IMMDeviceEnumerator), ctypes.byref(aus))
    return _Com(aus.value)


def _sitzungen(enum, je_sitzung):
    """Ruft je_sitzung(geraet_nr, steuerung) fuer jede Audio-Sitzung auf
    jedem aktiven Wiedergabegeraet - nicht nur dem Standardgeraet, das
    waehrend eines Laufs wechseln kann (Kopfhoerer)."""
    sammlung = ctypes.c_void_p()
    enum.rufe(3, (ctypes.c_int, wintypes.DWORD, _VOID_PP), E_RENDER, DEVICE_STATE_ACTIVE,
              ctypes.byref(sammlung))                                # EnumAudioEndpoints
    with _Com(sammlung.value) as geraete:
        anzahl = wintypes.UINT()
        geraete.rufe(3, (_P(wintypes.UINT),), ctypes.byref(anzahl))  # GetCount
        for g in range(anzahl.value):
            zeiger = ctypes.c_void_p()
            geraete.rufe(4, (wintypes.UINT, _VOID_PP), g, ctypes.byref(zeiger))  # Item
            with _Com(zeiger.value) as geraet:
                zeiger = ctypes.c_void_p()
                geraet.rufe(3, (_P(GUID), wintypes.DWORD, ctypes.c_void_p, _VOID_PP),
                            ctypes.byref(IID_IAudioSessionManager2), CLSCTX_ALL, None,
                            ctypes.byref(zeiger))                    # Activate
                with _Com(zeiger.value) as verwalter:
                    zeiger = ctypes.c_void_p()
                    verwalter.rufe(5, (_VOID_PP,), ctypes.byref(zeiger))  # GetSessionEnumerator
                    with _Com(zeiger.value) as liste:
                        n = ctypes.c_int()
                        liste.rufe(3, (_P(ctypes.c_int),), ctypes.byref(n))  # GetCount
                        for i in range(n.value):
                            zeiger = ctypes.c_void_p()
                            liste.rufe(4, (ctypes.c_int, _VOID_PP), i, ctypes.byref(zeiger))  # GetSession
                            with _Com(zeiger.value) as steuerung:
                                je_sitzung(g, steuerung)


def _kennung_lesen(s2):
    text = ctypes.c_void_p()
    s2.rufe(12, (_VOID_PP,), ctypes.byref(text))                    # GetSessionIdentifier
    try:
        return ctypes.wstring_at(text.value) if text.value else None
    finally:
        _ole32.CoTaskMemFree(text)             # Windows legt den Text mit CoTaskMemAlloc an


def _werte(steuerung, mit_kennung=True):
    """Was eine Audio-Sitzung ueber sich sagt (IAudioSessionControl2): das
    HRESULT von GetProcessId und die Nummer, das HRESULT von
    IsSystemSoundsSession (S_OK heisst: die Systemklaenge) und ihre Kennung
    (GetSessionIdentifier; None ohne mit_kennung). Fehler-HRESULTs werfen
    OSError."""
    with steuerung.frage(IID_IAudioSessionControl2) as s2:
        pid = wintypes.DWORD()
        pid_hr = s2.rufe(14, (_P(wintypes.DWORD),), ctypes.byref(pid))  # GetProcessId
        system_hr = s2.rufe(15, ())                                      # IsSystemSoundsSession
        kennung = _kennung_lesen(s2) if mit_kennung else None
    return {"pid_hr": pid_hr, "pid": pid.value, "system_hr": system_hr, "kennung": kennung}


def _kennung(steuerung):
    with steuerung.frage(IID_IAudioSessionControl2) as s2:
        return _kennung_lesen(s2)


def _laufwerke():
    """Geraetename -> Laufwerk (QueryDosDevice), etwa \\device\\harddiskvolume3
    -> C:. Die Kennung einer Audio-Sitzung nennt Pfade in der Geraeteform."""
    aus = {}
    puffer = ctypes.create_unicode_buffer(1024)
    for b in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if _kernel32.QueryDosDeviceW(b + ":", puffer, len(puffer)):
            ziel = puffer.value                # der erste Eintrag der Liste
            if ziel.lower().startswith("\\device\\"):
                aus[os.path.normcase(ziel)] = b + ":"
    return aus


# {0.0.0.00000000}.{<Geraet>}|\Device\HarddiskVolume3\...\chrome.exe%b{00000000-0000-0000-0000-000000000000}
# Die Systemklaenge haben statt des Pfads ein #, etwa |#%b{A9EF3FD9-...}
# (gemessen 21.11.2026). Nur die Kennung der Sitzung, nicht die der Instanz
# (GetSessionInstanceIdentifier, mit |1%b<Nummer> am Ende).
_KENNUNG = re.compile(r"^[^|]*\|(.+)%b\{[0-9A-Fa-f-]{36}\}$")


def _kennung_programm(kennung, laufwerke):
    """Programmpfad aus der Kennung einer Audio-Sitzung, mit Laufwerk
    statt Geraetename. None, wenn die Kennung keinen Pfad nennt (die
    Systemklaenge) oder das Geraet in laufwerke fehlt."""
    m = _KENNUNG.match(kennung or "")
    if not m:
        return None
    pfad = m.group(1)
    if re.match(r"^[A-Za-z]:\\", pfad):
        return pfad
    klein = os.path.normcase(pfad)
    for geraet, laufwerk in laufwerke.items():
        geraet = os.path.normcase(geraet).rstrip("\\")
        if klein.startswith(geraet + "\\"):   # HarddiskVolume3, nicht HarddiskVolume30
            return laufwerk + pfad[len(geraet):]
    return None


def _stumm(lautstaerke):
    wert = wintypes.BOOL()
    lautstaerke.rufe(6, (_P(wintypes.BOOL),), ctypes.byref(wert))   # GetMute
    return bool(wert.value)


def _spitze(steuerung):
    with steuerung.frage(IID_IAudioMeterInformation) as messer:
        wert = ctypes.c_float()
        messer.rufe(3, (_P(ctypes.c_float),), ctypes.byref(wert))   # GetPeakValue
        return wert.value


def _zustand(steuerung):
    wert = ctypes.c_int()
    steuerung.rufe(3, (_P(ctypes.c_int),), ctypes.byref(wert))      # GetState
    return ("ruht", "aktiv", "abgelaufen")[wert.value] if 0 <= wert.value <= 2 else wert.value


def _ordner_muster(ordner):
    """Woran man einen Prozess aus ordner erkennt, als regulaerer Ausdruck.

    Laeuft Python in einem App-Paket von Windows (MSIX, z. B. aus Claude
    heraus), leitet Windows %LOCALAPPDATA% um: Playwright meldet
    ...\\AppData\\Local\\ms-playwright\\webkit-2359, der Prozess laeuft aber aus
    ...\\AppData\\Local\\Packages\\<Paket>\\LocalCache\\Local\\ms-playwright\\
    webkit-2359 (gemessen am 21.11.2026). Beides zaehlt, sonst nichts."""
    ordner = os.path.normcase(os.path.abspath(ordner)).rstrip("\\/")
    formen = [re.escape(ordner)]
    for name, unter in (("LOCALAPPDATA", "local"), ("APPDATA", "roaming")):
        basis = os.environ.get(name)
        lokal = os.environ.get("LOCALAPPDATA")
        if not basis or not lokal:
            continue
        basis = os.path.normcase(os.path.abspath(basis)).rstrip("\\/")
        if ordner.startswith(basis + os.sep):
            rest = ordner[len(basis):]
            paket = os.path.normcase(os.path.abspath(lokal)).rstrip("\\/") + os.sep + "packages"
            formen.append(re.escape(paket) + r"\\[^\\]+\\localcache\\" + unter + re.escape(rest))
    return re.compile("^(?:%s)\\\\" % "|".join(formen))


def _darin(pfad, muster):
    return bool(muster.match(os.path.normcase(os.path.abspath(pfad))))


def _darf_stumm(werte, muster, laufwerke):
    """Pfad des Prozesses, wenn diese Sitzung von WebKit ist und stumm
    geschaltet werden darf, sonst None. werte wie aus _werte, dazu "pfad"
    (der Prozess hinter der Nummer, jetzt). Fragt Windows nichts - so laesst
    sich die Entscheidung mit nachgestellten Werten pruefen.

    Pruefung vom 21.11.2026: Nummer und Pfad allein reichen nicht. Die
    Sitzung der Systemklaenge meldet eine Nummer ohne Prozess (2292, mit
    AUDCLNT_S_NO_SINGLE_PROCESS), und Sitzungen beendeter Programme bleiben
    in der Liste. Vergaebe Windows so eine Nummer an einen Prozess von
    WebKit, saehe die Sitzung nach WebKit aus: stumm waeren dann die
    Systemklaenge oder ein fremdes Programm, und Windows merkte es sich.
    Darum muss alles stimmen: GetProcessId S_OK, IsSystemSoundsSession
    S_FALSE (keine Systemklaenge), die Kennung nennt ein Programm aus dem
    Ordner (mit diesem Programm entstand die Sitzung) und der Prozess hinter
    der Nummer laeuft von dort."""
    if werte.get("pid_hr") != S_OK or not werte.get("pid"):
        return None
    if werte.get("system_hr") != S_FALSE:
        return None
    pfad = werte.get("pfad")
    if not pfad or not _darin(pfad, muster):
        return None
    programm = _kennung_programm(werte.get("kennung"), laufwerke)
    if not programm or not _darin(programm, muster):
        return None
    return pfad


def auflisten():
    """Alle Audio-Sitzungen, nur gelesen (zum Nachsehen): Prozess, Pfad,
    HRESULTs, Kennung, Zustand, stumm, Spitzenpegel. Aendert nichts.
    Ausserhalb von Windows []."""
    if not AN:
        return []
    aus = []

    def je(g, steuerung):
        werte = _werte(steuerung)
        with steuerung.frage(IID_ISimpleAudioVolume) as lautstaerke:
            stumm = _stumm(lautstaerke)
        werte.update({"geraet": g, "pfad": _pfad(werte["pid"]) if werte["pid"] else None,
                      "zustand": _zustand(steuerung), "stumm": stumm, "spitze": _spitze(steuerung)})
        aus.append(werte)

    def lesen():
        # In einem eigenen Thread: so bleibt COM im aufrufenden Thread unberuehrt.
        try:
            _ole32.CoInitializeEx(None, 0)
            try:
                with _enumerator() as enum:
                    _sitzungen(enum, je)
            finally:
                _ole32.CoUninitialize()
        except OSError as e:
            fehler.append(e)

    fehler = []
    t = threading.Thread(target=lesen)
    t.start()
    t.join(10)
    if fehler:
        raise fehler[0]
    return aus


class Stummschalter(object):
    """Schaltet alle Audio-Sitzungen stumm, die aus ordner kommen (siehe
    _darf_stumm), solange er laeuft - alle takt Sekunden aufs Neue, damit
    auch neue Sitzungen sofort stumm sind. Mit start()/stop() oder als
    with-Block. ordner muss ein voller Pfad sein: aus einem leeren machte
    os.path.abspath den Arbeitsordner.

    sitzungen: je Sitzung (pid, Geraet) ein Eintrag mit Programm (laut
    Prozess und laut Kennung), ob sie beim ersten Blick schon stumm war
    (Windows hat sich das gemerkt) oder ob er sie stumm geschaltet hat, ob
    sie zuletzt stumm war, und dem hoechsten Spitzenpegel
    (IAudioMeterInformation, 0..1)."""

    def __init__(self, ordner, takt=0.1):
        if not ordner or not os.path.isabs(ordner):
            raise ValueError("Stummschalter braucht einen vollen Pfad, nicht %r" % (ordner,))
        self.ordner = ordner
        self._muster = _ordner_muster(ordner)
        self._laufwerke = {}
        self.takt = takt
        self.sitzungen = {}
        self.fehler = []
        self.runden = 0
        self._sperre = threading.Lock()
        self._halt = threading.Event()
        self._erste = threading.Event()
        self._thread = None
        self._beginn = time.monotonic()

    # --------------------------------------------------------------- Ablauf
    def start(self):
        if not AN or self._thread:
            return self
        self._halt.clear()
        self._thread = threading.Thread(target=self._lauf, name="stumm_windows", daemon=True)
        self._thread.start()
        self._erste.wait(5)          # die erste Runde ist durch (oder gescheitert)
        return self

    def stop(self):
        if self._thread:
            self._halt.set()
            self._thread.join(5)
            self._thread = None

    def __enter__(self):
        return self.start()

    def __exit__(self, *_):
        self.stop()

    def _lauf(self):
        try:
            _ole32.CoInitializeEx(None, 0)       # COINIT_MULTITHREADED
        except OSError as e:
            self._fehler(e)
            self._erste.set()
            return
        try:
            with _enumerator() as enum:
                laufwerke_um = 0.0
                while True:
                    try:
                        if time.monotonic() >= laufwerke_um:   # ein Laufwerk kann dazukommen
                            self._laufwerke = _laufwerke()
                            laufwerke_um = time.monotonic() + 10
                        _sitzungen(enum, self._je_sitzung_sicher)
                        self.runden += 1
                    except Exception as e:        # z. B. Geraet gerade weg; weiter im Takt
                        self._fehler(e)
                    self._erste.set()
                    if self._halt.wait(self.takt):
                        break
        except OSError as e:
            self._fehler(e)
        finally:
            self._erste.set()
            _ole32.CoUninitialize()

    def _fehler(self, e):
        with self._sperre:
            if len(self.fehler) < 20:
                self.fehler.append(str(e))

    def _prozess_pfad(self, pid):
        """Pfad des Prozesses mit dieser Nummer. Jedes Mal neu gefragt und
        nicht je pid gemerkt: Windows vergibt die Nummer eines beendeten
        Prozesses wieder, und dann waere es ein fremdes Programm. (Eigene
        Methode, damit ein Test hier nachstellen kann, WebKit habe jede
        Nummer.)"""
        return _pfad(pid)

    def _schalten(self, lautstaerke):
        """Stumm. (Eigene Methode, damit ein Test trocken laufen kann.)"""
        lautstaerke.rufe(5, (wintypes.BOOL, ctypes.c_void_p), True, None)   # SetMute

    def _je_sitzung_sicher(self, g, steuerung):
        # Ein Fehler bei einer Sitzung (Prozess gerade beendet) haelt die
        # anderen nicht auf.
        try:
            self._je_sitzung(g, steuerung)
        except Exception as e:
            self._fehler(e)

    def _je_sitzung(self, g, steuerung):
        # Erst das Billige, die Kennung nur fuer Sitzungen, deren Prozess aus
        # ordner kommt: Rechnet der Hauptthread, wartet jeder Aufruf ueber
        # ctypes auf das GIL, und alles fuer jede Sitzung zu lesen halbierte
        # fast den Takt (gemessen 21.11.2026: 6 statt 10 Runden in 4 s).
        # Entschieden wird trotzdem nur in _darf_stumm, mit allen Werten.
        werte = _werte(steuerung, mit_kennung=False)
        pid = werte["pid"]
        if werte["pid_hr"] != S_OK or not pid or werte["system_hr"] != S_FALSE:
            return
        werte["pfad"] = self._prozess_pfad(pid)
        if not werte["pfad"] or not _darin(werte["pfad"], self._muster):
            return
        werte["kennung"] = _kennung(steuerung)
        pfad = _darf_stumm(werte, self._muster, self._laufwerke)
        if not pfad:
            return
        with steuerung.frage(IID_ISimpleAudioVolume) as lautstaerke:
            vorher = _stumm(lautstaerke)
            if not vorher:
                self._schalten(lautstaerke)
            jetzt = _stumm(lautstaerke)
        spitze = _spitze(steuerung)
        with self._sperre:
            s = self.sitzungen.get((pid, g))
            if s is None:
                s = self.sitzungen[(pid, g)] = {
                    "pid": pid, "geraet": g, "programm": os.path.basename(pfad),
                    "kennung": _kennung_programm(werte["kennung"], self._laufwerke),
                    "gesehen_ms": int((time.monotonic() - self._beginn) * 1000),
                    "zuerst_stumm": vorher, "von_uns_stumm": False, "stumm": jetzt,
                    "spitze": 0.0, "aktiv_proben": 0}
            if not vorher:
                s["von_uns_stumm"] = True
            s["stumm"] = jetzt
            s["spitze"] = max(s["spitze"], spitze)
            if _zustand(steuerung) == "aktiv":
                s["aktiv_proben"] += 1

    # ------------------------------------------------------------ Auskunft
    def bericht(self):
        with self._sperre:
            return [dict(s) for s in self.sitzungen.values()]

    def warten_bis_stumm(self, sekunden=5.0, neu_ab=0):
        """Bis mehr als neu_ab Sitzungen bekannt und alle stumm sind. True,
        wenn es geklappt hat (ausserhalb von Windows immer)."""
        if not AN:
            return True
        ende = time.monotonic() + sekunden
        while time.monotonic() < ende:
            with self._sperre:
                if len(self.sitzungen) > neu_ab and all(s["stumm"] for s in self.sitzungen.values()):
                    return True
            time.sleep(0.02)
        return False

    def protokoll_schreiben(self, pfad):
        with io.open(pfad, "w", encoding="utf-8") as f:
            json.dump({"ordner": self.ordner, "runden": self.runden, "fehler": self.fehler,
                       "sitzungen": self.bericht()}, f, ensure_ascii=False, indent=1)


def _stille_wav(sekunden=0.5, rate=44100):
    """Stille als WAV: Mono, 16 Bit, alle Samples 0."""
    puffer = io.BytesIO()
    w = wave.open(puffer, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(rate)
    w.writeframes(b"\0\0" * int(rate * sekunden))
    w.close()
    return puffer.getvalue()


# Spielt die Stille in Schleife ab. WebKit von Playwright darf das ohne
# Fingertipp; ein blob:- oder data:-WAV lehnt es unter Windows ab
# (NotSupportedError, auch ueber page.route), von einem echten Server nicht.
STILLE_SPIELEN = """async (src) => { const a = new Audio(src); a.loop = true; window.__stille = a;
  try { await a.play(); return 'spielt'; } catch (e) { return 'nein: ' + e.name; } }"""


def vorlauf(browser, stummschalter, sekunden=5.0):
    """Spielt in browser kurz Stille, bis ihre Audio-Sitzung stumm ist.
    So entsteht eine Sitzung von WebKit, ohne dass etwas zu hoeren waere,
    und Windows weiss danach, dass dieses Programm stumm ist (siehe oben):
    jede neue Sitzung beginnt stumm, schon vor dem ersten echten Ton.
    Die Stille kommt von einem eigenen kleinen Server auf 127.0.0.1.
    Gibt zurueck, was play() meldete, und ob die Sitzung stumm ist."""
    if not AN:
        return "aus", True
    daten = _stille_wav()

    class Stille(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            wav = self.path.endswith(".wav")
            inhalt = daten if wav else b"<!doctype html><meta charset=utf-8><body></body>"
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav" if wav else "text/html")
            self.send_header("Content-Length", str(len(inhalt)))
            self.end_headers()
            self.wfile.write(inhalt)

        def log_message(self, *args):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Stille)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    ctx = browser.new_context()
    try:
        adresse = "http://127.0.0.1:%d" % srv.server_address[1]
        page = ctx.new_page()
        page.goto(adresse + "/")
        bekannt = len(stummschalter.bericht())
        gespielt = page.evaluate(STILLE_SPIELEN, adresse + "/stille.wav")
        stumm = stummschalter.warten_bis_stumm(sekunden, bekannt) if gespielt == "spielt" else False
        return gespielt, stumm
    finally:
        ctx.close()
        srv.shutdown()
        srv.server_close()
