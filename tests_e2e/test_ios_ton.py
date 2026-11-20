# -*- coding: utf-8 -*-
"""iPhone: Ton im Fingertipp und keine Ueberbreite (15.11.2026).

Ajdin mit TestFlight 1.3 (Build 3) auf dem iPhone 11, iOS 16.6.1: nie Ton,
auch nicht beim ersten Wort, Lautlos-Schalter aus. Und: "die app ist etwas
zu breit fuer iphone das muss ganz leicht duenner sein". Was index.html
seitdem auf iOS tut, steht dort unter "Ton im Fingertipp" und beim Viewport
im Kopf. Hier im Browser nachgestellt, wenn es geht mit WebKit von Playwright
(dem Motor von Safari), und jede Pruefung mit Gegenprobe auf Android:

- kein AudioContext vor dem ersten Fingertipp; im Tipp: Audio-Sitzung
  'playback' (ab iOS 17), Kontext anlegen, Ein-Sample-Puffer, den spieler
  einmal stumm anspielen
- resume() auch bei 'interrupted', ein Wort dann gleich ueber den spieler
- ein Kontext, dessen Uhr trotz 'running' steht, wird geschlossen; bis zum
  naechsten Tipp sprechen die Woerter ueber den spieler
- ein abgelehntes play() steht im Ton-Protokoll, der naechste Tipp versucht
  es neu
- unter iOS 17 keine Audio-Sitzung 'playback', die Woerter ueber den spieler
- maximum-scale=1.0 und 16 px in allen Eingabefeldern, keine waagerechte
  Ueberbreite bei 375, 390 und 414 Punkten

Seit dem 15.11.2026 (Build 4, Befund mit iOS 27.2.1: nach dem Hintergrund
kein Ton mehr, und der Doppeltipp zoomt ohne Weg zurueck), siehe "Zurueck
in der App" in index.html:
- zurueck (sichtbar, 'resume', 'appStateChange'): ein ruhender Kontext wird
  fortgesetzt, ein bestelltes Wort faellt weg, der naechste Tipp spielt den
  spieler und den Ein-Sample-Puffer neu an
- bleibt er stehen oder steht seine Uhr, wird er geschlossen und im
  naechsten Tipp neu angelegt
- solange die App nur inaktiv ist, zaehlt die Uhr-Probe nicht
- eine vom System angehaltene Geschichte merkt sich die Stelle und spielt
  nicht von selbst weiter
- user-scalable=no, minimum- und maximum-scale 1, touch-action:
  manipulation an allen Elementen; Android ohne all das

Hoerbares gibt es im Browser nicht, und WebKit unter Windows hat gar keinen
AudioContext. Deshalb eine Attrappe (TON), die mitschreibt, was die App
bestellt - samt dem Ereignis, in dem es geschah (window.event). Den Zoom von
UIKit beim Antippen eines Felds kann Playwright nicht ausloesen; geprueft
wird seine Ursache, die Schrift unter 16 px.
"""
import pytest
from conftest import MitSchemaSperre, Seite
from test_ios import HUELLE

# Was WKWebView meldet: iOS 26 friert die Fassung im UA auf 18_6 ein.
UA_IOS26 = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15"
            " (KHTML, like Gecko) Mobile/15E148")
UA_IOS16 = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15"
            " (KHTML, like Gecko) Mobile/15E148")

GESTEN = ("touchend", "pointerup", "click")

# AudioContext, navigator.audioSession und HTMLMediaElement.play als
# Attrappe. Alles landet in window.__ton, mit laufender Nummer (seq) und dem
# Ereignis, in dem es geschah (ev; ':skript' = nicht vom Nutzer).
# window.__tonTot: der naechste Kontext meldet 'running', seine Uhr steht.
# window.__playNein: Name des Fehlers, mit dem play() ablehnt.
TON = r"""
(() => {
  const L = window.__ton = {neu: [], resume: [], zu: [], starts: [], osz: [], spiele: [], sitzung: []};
  let seq = 0;
  window.__tonTot = false; window.__playNein = '';
  const ev = () => window.event ? window.event.type + (window.event.isTrusted ? '' : ':skript') : null;
  class Kontext extends EventTarget {
    constructor(o){
      super();
      this.nr = L.neu.length; this.optionen = o || null; this.tot = !!window.__tonTot;
      this._z = 'suspended'; this._basis = 0; this._seit = 0;
      this.sampleRate = 48000; this.baseLatency = 0.02; this.destination = {};
      L.neu.push({nr: this.nr, ev: ev(), seq: ++seq, tot: this.tot, optionen: this.optionen});
      setTimeout(() => this.zustand('running'), 5);   // wie WebKit: rendert kurz nach dem Anlegen
    }
    get state(){ return this._z; }
    get currentTime(){
      return this._z === 'running' && !this.tot ? this._basis + (performance.now() - this._seit) / 1000 : this._basis;
    }
    zustand(z){
      if(this._z === z || this._z === 'closed') return;
      this._basis = this.currentTime; this._z = z; this._seit = performance.now();
      this.dispatchEvent(new Event('statechange'));
    }
    resume(){
      L.resume.push({nr: this.nr, von: this._z, ev: ev(), seq: ++seq});
      if(this._z === 'closed') return Promise.reject(new DOMException('zu', 'InvalidStateError'));
      this.zustand('running'); return Promise.resolve();
    }
    stirb(){ this._basis = this.currentTime; this.tot = true; }   // die Uhr bleibt ab jetzt stehen
    close(){ L.zu.push({nr: this.nr, ev: ev(), seq: ++seq}); this.zustand('closed'); return Promise.resolve(); }
    createBuffer(k, n, sr){ return {numberOfChannels: k, length: n, sampleRate: sr, duration: n / sr,
                                    getChannelData: () => new Float32Array(n)}; }
    decodeAudioData(){ return Promise.resolve(this.createBuffer(1, 24000, 24000)); }
    createBufferSource(){
      const ctx = this, q = {buffer: null, onended: null, connect(){}, stop(){},
        start(wann){ L.starts.push({nr: ctx.nr, n: q.buffer ? q.buffer.length : 0, wann: wann || 0, ev: ev(), seq: ++seq}); }};
      return q;
    }
    createOscillator(){ const ctx = this;
      return {type: 'sine', frequency: {value: 0}, connect(){}, stop(){}, start(w){ L.osz.push({nr: ctx.nr, w}); }}; }
    createGain(){
      return {gain: {value: 0, setValueAtTime(){}, linearRampToValueAtTime(){}, exponentialRampToValueAtTime(){}}, connect(){}};
    }
  }
  window.AudioContext = Kontext;
  window.webkitAudioContext = undefined;
  let typ = 'auto';
  const sitzung = {get type(){ return typ; }, set type(v){ L.sitzung.push({v, ev: ev(), seq: ++seq}); typ = v; }};
  Object.defineProperty(Navigator.prototype, 'audioSession', {configurable: true, get: () => sitzung});
  HTMLMediaElement.prototype.play = function(){
    L.spiele.push({src: this.getAttribute('src'), muted: this.muted, ev: ev(), seq: ++seq});
    return window.__playNein ? Promise.reject(new DOMException('abgelehnt', window.__playNein)) : Promise.resolve();
  };
})();
"""

# Das Plugin App der Huelle, mit Gedaechtnis (15.11.2026): die Attrappe in
# test_ios.HUELLE vergisst ihre Horcher. Hier landen sie in window.__app, und
# APP_MELDET ruft sie wie die Huelle ('appStateChange', 'pause', 'resume').
APP = r"""
(() => {
  const H = window.__app = {};
  const A = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.App;
  if(A) A.addListener = (n, f) => { (H[n] = H[n] || []).push(f); return Promise.resolve({remove(){}}); };
})();
"""
APP_MELDET = "([n, d]) => { (window.__app[n] || []).forEach(f => f(d)); return (window.__app[n] || []).length; }"

# Verdecken und wieder zeigen wie in test_cloud.py: document.hidden
# ueberschreiben und visibilitychange schicken. melden=False zeigt nur, ohne
# Ereignis (dann meldet sich die Seite ueber das Plugin App).
SICHT = """([versteckt, melden]) => {
  if(versteckt) Object.defineProperty(document, 'hidden', {configurable: true, get: () => true});
  else delete document.hidden;
  if(melden) document.dispatchEvent(new Event('visibilitychange'));
}"""

# Ein Wort mit Aufnahme: der Text, den speak() bekommt, und seine Datei.
WORT = """() => { const w = CATEGORIES[0].words.find(x => audioDatei(x.bs));
                  return {bs: w.bs, datei: audioDatei(w.bs)}; }"""

# Spricht das Wort und sagt, auf welchem Weg es ging: WebAudio (ein Puffer
# mit mehr als einem Sample) oder der spieler (audio/...).
SPRECHEN = """(w) => {
  const T = window.__ton, s0 = T.starts.length, p0 = T.spiele.length;
  speak(w.bs);
  return {webaudio: T.starts.slice(s0).filter(s => s.n > 1).length,
          spieler: T.spiele.slice(p0).filter(s => (s.src || '').startsWith('audio/')).length};
}"""


@pytest.fixture(scope="module")
def webkit(pw):
    try:
        b = pw.webkit.launch()
    except Exception as e:                       # pragma: no cover - nur ohne WebKit
        pytest.skip("WebKit von Playwright fehlt: %s" % e)
    # Mit der SCHEMA_SPERRE wie jeder Kontext der Suite (conftest.py, 16.11.2026)
    yield MitSchemaSperre(b)
    b.close()


@pytest.fixture(params=["webkit", "chromium"])
def motor(request, webkit, browser):
    """Der Ton-Weg haengt nicht am Motor - geprueft wird in beiden."""
    return webkit if request.param == "webkit" else browser


def _start(b, basis, heute_stand, plattform="ios", ua=UA_IOS26, breite=414, hoehe=896, ton=True):
    opts = dict(viewport={"width": breite, "height": hoehe}, device_scale_factor=2, has_touch=True,
                locale="de-DE", service_workers="block", reduced_motion="reduce")
    if ua:
        opts["user_agent"] = ua
    ctx = b.new_context(**opts)
    ctx.add_init_script(HUELLE % plattform)
    ctx.add_init_script(APP)
    if ton:
        ctx.add_init_script(TON)
    s = Seite(ctx.new_page(), basis)
    s.starten(stand=heute_stand())
    return ctx, s


def _tippen(s):
    """Ein echter Fingertipp neben die Spalte, wo nichts ist (x = 4)."""
    s.page.touchscreen.tap(4, 450)


def _ton(s):
    return s.js("() => window.__ton")


def _bereit_lebt(s):
    """Bis die Uhr des Kontexts nachweislich laeuft (nach gut 0,9 s)."""
    s.page.wait_for_function("() => actx && tonUhr && tonUhr.ctx === actx && tonUhr.lebt", timeout=5000)


def _puffer(s, w):
    s.js("(d) => pufferLaden(d)", w["datei"])
    s.page.wait_for_function("(d) => puffer.get(d) && puffer.get(d).buf", arg=w["datei"], timeout=5000)


# ------------------------------------------------------- erster Tipp ---
def test_kein_audiokontext_vor_dem_ersten_tipp(motor, basis, heute_stand):
    """Vor dem ersten Tipp: kein AudioContext, kein Anspielen, die Sitzung
    unberuehrt - auch nachdem das Vorwaermen (auf Android rund 2,4 s nach
    dem Start) laengst dran war. Im Tipp, in dieser Reihenfolge: Sitzung
    'playback', Kontext, Ein-Sample-Puffer, spieler stumm angespielt."""
    ctx, s = _start(motor, basis, heute_stand)
    try:
        s.page.wait_for_timeout(3000)
        t = _ton(s)
        assert t["neu"] == [] and t["spiele"] == [] and t["sitzung"] == [] and t["starts"] == [], t
        assert s.js("() => [actx, navigator.audioSession.type, IOS_FASSUNG, IOS_AB_17]") == [None, "auto", 18, True]
        # Ein .click() aus dem Skript ist kein Fingertipp
        s.js("() => document.body.click()")
        assert _ton(s)["neu"] == []

        _tippen(s)
        t = _ton(s)
        assert len(t["neu"]) == 1 and t["neu"][0]["ev"] in GESTEN, t
        assert t["neu"][0]["optionen"] == {"latencyHint": "playback"}
        geste = t["neu"][0]["ev"]
        assert [(x["v"], x["ev"]) for x in t["sitzung"]] == [("playback", geste)], t
        assert t["sitzung"][0]["seq"] < t["neu"][0]["seq"], "Sitzung erst nach dem Kontext"
        eins = [x for x in t["starts"] if x["n"] == 1]
        assert eins and eins[0]["ev"] == geste and eins[0]["nr"] == 0, t
        assert t["resume"] and t["resume"][0]["ev"] == geste, t          # angelegt 'suspended' -> fortgesetzt
        assert t["spiele"] and t["spiele"][0]["muted"] is True and t["spiele"][0]["ev"] == geste, t
        assert (t["spiele"][0]["src"] or "").startswith("blob:"), t
        s.page.wait_for_function("() => spielerFrei === true && vorwaermen === null && spieler.muted === false")

        # Der zweite Tipp legt nichts neu an und spielt nichts mehr an
        _bereit_lebt(s)
        vorher = _ton(s)
        _tippen(s)
        t = _ton(s)
        assert len(t["neu"]) == 1 and len(t["starts"]) == len(vorher["starts"]), t
        assert len(t["spiele"]) == len(vorher["spiele"]) and len(t["sitzung"]) == 1, t
        assert s.fehler == []
    finally:
        ctx.close()


def test_erstes_wort_ueber_den_spieler_dann_webaudio(webkit, basis, heute_stand):
    """Ein frischer Kontext ist noch nicht bewiesen: das Wort gleich nach
    dem Tipp spricht der spieler. Laeuft seine Uhr nachweislich, kommen die
    Woerter ueber WebAudio wie auf Android."""
    ctx, s = _start(webkit, basis, heute_stand)
    try:
        w = s.js(WORT)
        _tippen(s)
        _puffer(s, w)
        if not s.js("() => tonUhr && tonUhr.lebt"):
            assert s.js(SPRECHEN, w) == {"webaudio": 0, "spieler": 1}
        _bereit_lebt(s)
        assert s.js(SPRECHEN, w) == {"webaudio": 1, "spieler": 0}
        assert s.fehler == []
    finally:
        ctx.close()


# ------------------------------------------------------ interrupted ---
def test_fortsetzen_auch_bei_interrupted(motor, basis, heute_stand):
    """WebKits 'interrupted' (Anruf, Siri, Heimknopf): sound() setzt fort -
    bis zum 15.11.2026 nur bei 'suspended'. Ein Wort kommt dann gleich ueber
    den spieler, und der naechste Tipp setzt ebenfalls fort."""
    ctx, s = _start(motor, basis, heute_stand)
    try:
        w = s.js(WORT)
        _tippen(s)
        _puffer(s, w)
        _bereit_lebt(s)
        r = s.js("""() => { actx.zustand('interrupted'); window.__ton.resume = []; window.__ton.osz = [];
                            sound('ok'); return {resume: window.__ton.resume, osz: window.__ton.osz.length}; }""")
        assert [x["von"] for x in r["resume"]] == ["interrupted"] and r["osz"] == 2, r
        s.js("() => actx.zustand('interrupted')")
        assert s.js(SPRECHEN, w) == {"webaudio": 0, "spieler": 1}
        s.js("() => { actx.zustand('interrupted'); window.__ton.resume = []; }")
        _tippen(s)
        r = _ton(s)["resume"]
        assert r and r[0]["von"] == "interrupted" and r[0]["ev"] in GESTEN, r
        assert len(_ton(s)["neu"]) == 1                       # derselbe Kontext, nur fortgesetzt
        assert s.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------------- toter Kontext ---
def test_toter_kontext_wird_im_naechsten_tipp_ersetzt(motor, basis, heute_stand):
    """'running', aber die Uhr steht: nach gut einer halben Sekunde erkannt
    und geschlossen. Bis zum naechsten Tipp sprechen die Woerter ueber den
    spieler, und ohne Tipp entsteht kein neuer Kontext. Der naechste Tipp
    legt einen an, und sobald dessen Uhr laeuft, wieder WebAudio."""
    ctx, s = _start(motor, basis, heute_stand)
    try:
        w = s.js(WORT)
        s.js("() => { window.__tonTot = true; }")
        _tippen(s)
        _puffer(s, w)
        s.page.wait_for_function("() => actx === null", timeout=5000)
        t = _ton(s)
        assert [x["nr"] for x in t["zu"]] == [0], t
        assert any("AudioContext tot" in z for z in s.js("() => TON_PROTOKOLL"))
        assert s.js(SPRECHEN, w) == {"webaudio": 0, "spieler": 1}
        s.js("() => sound('ok')")
        assert len(_ton(s)["neu"]) == 1                       # ohne Tipp kein neuer

        s.js("() => { window.__tonTot = false; }")
        _tippen(s)
        t = _ton(s)
        assert len(t["neu"]) == 2 and t["neu"][1]["ev"] in GESTEN, t
        _bereit_lebt(s)
        assert s.js(SPRECHEN, w) == {"webaudio": 1, "spieler": 0}
        assert s.fehler == []
    finally:
        ctx.close()


def test_kontext_stirbt_spaeter_der_tipp_ersetzt_ihn_sofort(webkit, basis, heute_stand):
    """Lief der Kontext schon und bleibt seine Uhr dann stehen, merkt es der
    naechste Tipp: schliessen und in derselben Geste neu anlegen. Der
    Rueckmeldeton des alten (rueckTon) gilt danach nicht mehr - ein Wort auf
    seiner Uhr kaeme beim neuen viel zu spaet."""
    ctx, s = _start(webkit, basis, heute_stand)
    try:
        _tippen(s)
        _bereit_lebt(s)
        s.js("() => { sound('ok'); actx.stirb(); }")
        assert s.js("() => rueckTon !== null")
        s.page.wait_for_timeout(700)
        _tippen(s)
        t = _ton(s)
        assert [x["nr"] for x in t["zu"]] == [0] and t["zu"][0]["ev"] in GESTEN, t
        assert len(t["neu"]) == 2 and t["neu"][1]["ev"] == t["zu"][0]["ev"], t
        assert s.js("() => [rueckTon, actx.nr]") == [None, 1]
        assert s.fehler == []
    finally:
        ctx.close()


# --------------------------------------------------- spieler lehnt ab ---
def test_abgelehntes_play_im_protokoll_und_neu_beim_naechsten_tipp(webkit, basis, heute_stand):
    """Lehnt der spieler ab, wird das nicht verschluckt: Protokoll, spielerFrei
    zurueck, der Knopf springt zurueck (fertig), und der naechste Tipp spielt
    ihn neu an."""
    ctx, s = _start(webkit, basis, heute_stand)
    try:
        w = s.js(WORT)
        s.js("() => { window.__playNein = 'NotAllowedError'; }")
        _tippen(s)
        s.page.wait_for_function("() => TON_PROTOKOLL.some(z => z.includes('(anspielen) abgelehnt: NotAllowedError'))")
        assert s.js("() => spielerFrei") is False
        r = s.js("""async (w) => {
          let fertig = false; puffer.clear();
          speak(w.bs, () => { fertig = true; });
          await new Promise(r => setTimeout(r, 50));
          return {fertig, letzte: TON_PROTOKOLL[TON_PROTOKOLL.length - 1], frei: spielerFrei};
        }""", w)
        assert r["fertig"] is True and r["frei"] is False, r
        assert "abgelehnt: NotAllowedError" in r["letzte"] and w["datei"] in r["letzte"], r

        s.js("() => { window.__playNein = ''; window.__ton.spiele = []; }")
        _tippen(s)
        s.page.wait_for_function("() => spielerFrei === true")
        sp = _ton(s)["spiele"]
        assert sp and sp[0]["muted"] is True and sp[0]["ev"] in GESTEN, sp
        assert s.fehler == []
    finally:
        ctx.close()


# --------------------------------------------------------- iOS 16 ---
def test_ios16_ohne_playback_die_woerter_ueber_den_spieler(motor, basis, heute_stand):
    """Unter iOS 17 bleibt die Audio-Sitzung beim Standard (siehe
    tonSitzung in index.html: unter 16 kann 'playback' WebAudio stumm
    machen). Die Woerter sprechen dann ueber den spieler, der auch mit
    Lautlos-Schalter spielt; nur die Pieptoene laufen ueber WebAudio."""
    ctx, s = _start(motor, basis, heute_stand, ua=UA_IOS16)
    try:
        assert s.js("() => [IOS_FASSUNG, IOS_AB_17]") == [16, False]
        w = s.js(WORT)
        _tippen(s)
        t = _ton(s)
        assert len(t["neu"]) == 1 and t["neu"][0]["ev"] in GESTEN and t["sitzung"] == [], t
        assert s.js("() => navigator.audioSession.type") == "auto"
        assert any("bleibt auto (iOS 16)" in z for z in s.js("() => TON_PROTOKOLL"))
        s.js("(d) => pufferLaden(d)", w["datei"])
        assert s.js("(d) => puffer.has(d)", w["datei"]) is False
        _bereit_lebt(s)
        assert s.js(SPRECHEN, w) == {"webaudio": 0, "spieler": 1}
        s.js("() => { window.__ton.osz = []; sound('ok'); }")
        assert len(_ton(s)["osz"]) == 2
        assert s.fehler == []
    finally:
        ctx.close()


def test_ipad_ohne_ios_fassung_im_ua(webkit, basis, heute_stand):
    """Meldet sich ein iPad als Mac (Desktop-Modus), fehlt die iOS-Fassung.
    Dann entscheidet Set.prototype.union (ab Safari 17): hier da, also
    'playback'. Die Huelle verlangt zwar die Handy-Kennung
    (preferredContentMode "mobile"), aber darauf verlaesst sich das nicht."""
    ua = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
          " (KHTML, like Gecko)")
    ctx, s = _start(webkit, basis, heute_stand, ua=ua, breite=820, hoehe=1180)
    try:
        assert s.js("() => [IOS_FASSUNG, IOS_AB_17]") == [0, True]
        _tippen(s)
        assert [x["v"] for x in _ton(s)["sitzung"]] == ["playback"]
        assert s.fehler == []
    finally:
        ctx.close()


# ---------------------------------------------- Android wie vorher ---
def test_android_wie_vorher(motor, basis, heute_stand):
    """Gegenprobe: auf Android entsteht der Kontext beim Vorwaermen ohne
    Tipp, der spieler wird ohne Tipp stumm angespielt, die Sitzung bleibt
    unberuehrt, ein Tipp tut nichts, Woerter laufen gleich ueber WebAudio,
    und es gibt kein Ton-Protokoll."""
    ctx, s = _start(motor, basis, heute_stand, plattform="android", ua=None)
    try:
        s.page.wait_for_function("() => window.__ton.neu.length === 1 && vorwaermen === null", timeout=10000)
        t = _ton(s)
        assert t["neu"][0]["ev"] is None and t["sitzung"] == [], t
        assert t["spiele"] and t["spiele"][0]["muted"] is True and t["spiele"][0]["ev"] is None, t
        w = s.js(WORT)
        _puffer(s, w)
        assert s.js(SPRECHEN, w) == {"webaudio": 1, "spieler": 0}
        vorher = _ton(s)
        _tippen(s)
        t = _ton(s)
        assert len(t["neu"]) == 1 and len(t["starts"]) == len(vorher["starts"]), t
        assert len(t["spiele"]) == len(vorher["spiele"]) and t["sitzung"] == [], t
        # sound() setzt fort wie bisher, wenn der Kontext ruht
        r = s.js("() => { actx.zustand('suspended'); window.__ton.resume = []; sound('ok'); return window.__ton.resume; }")
        assert [x["von"] for x in r] == ["suspended"], r
        assert s.js("() => TON_PROTOKOLL") == []
        assert s.fehler == []
    finally:
        ctx.close()


# ------------------------------------------------------------ Breite ---
FELDER = """() => [...document.querySelectorAll('input, textarea, select')]
  .filter(e => !['checkbox', 'radio', 'file', 'hidden', 'range', 'button', 'submit'].includes((e.type || '').toLowerCase()))
  .map(e => ({id: e.id, cls: e.className, px: parseFloat(getComputedStyle(e).fontSize)}))"""

# Waagerecht: laesst sich die Seite seitlich schieben, oder ragt etwas
# Sichtbares ueber den rechten Rand? Ausgenommen ist, was in einem Kasten
# mit eigenem waagerechten Ueberlauf (scroll/hidden/clip) steckt.
BREITE = """() => {
  const d = document.documentElement, w = window.innerWidth;
  const eigenerRand = e => { for(let a = e.parentElement; a && a !== document.body; a = a.parentElement){
      const o = getComputedStyle(a).overflowX; if(o !== 'visible') return true; } return false; };
  const ueber = [];
  for(const e of document.querySelectorAll('body *')){
    const r = e.getBoundingClientRect();
    if(!r.width || !r.height || r.right <= w + 0.5) continue;
    const st = getComputedStyle(e);
    if(st.visibility === 'hidden' || st.position === 'fixed' || eigenerRand(e)) continue;
    ueber.push((e.id ? '#' + e.id : e.tagName.toLowerCase()) + '.' + String(e.className).slice(0, 30) + ' ' + Math.round(r.right));
  }
  return {sw: d.scrollWidth, cw: d.clientWidth, bsw: document.body.scrollWidth, w, ueber: ueber.slice(0, 8)};
}"""

SCHIRME = {
    "start": "() => { homeMode = 'words'; showHome(); }",
    "lektion": "() => { showHome(); openLevel(0); startLesson(); }",
    "tippen": """() => { showHome(); openLevel(0); startLesson();
                  const w = CATEGORIES[0].words.find(x => typable(x));
                  Lx.queue = [{typ: 'type', w}]; Lx.i = 0; Lx.total = 1; showLessonTask(); }""",
    "einstellungen": "() => showSettings()",
    "profil": "() => showKonto()",
    "anmeldung": "() => zeigeAnmeldung('neu')",
    "kaufkasten": "() => { showHome(); vollKaufOeffnen(); }",
}


@pytest.mark.parametrize("breite", [375, 390, 414])
def test_iphone_keine_ueberbreite_und_16px_felder(webkit, basis, heute_stand, breite):
    """iPhone SE/mini (375), 12-16 (390), iPhone 11 (414): auf keinem der
    Schirme laesst sich die Seite seitlich schieben, und jedes Eingabefeld
    hat mindestens 16 px - darunter zoomt WKWebView beim Antippen. Der
    Viewport sperrt den Zoom zusaetzlich (maximum-scale=1.0)."""
    ctx, s = _start(webkit, basis, heute_stand, breite=breite, hoehe=844)
    try:
        vp = s.js("() => document.querySelector('meta[name=viewport]').content")
        assert "maximum-scale=1.0" in vp and "viewport-fit=cover" in vp, vp
        s.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
        s.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
        for name, js in SCHIRME.items():
            s.js(js)
            s.page.wait_for_timeout(250)
            m = s.js(BREITE)
            assert m["sw"] == m["cw"] == breite and m["bsw"] <= breite, (name, m)
            assert m["ueber"] == [], (name, m)
            klein = [f for f in s.js(FELDER) if f["px"] < 16]
            assert klein == [], (name, klein)
            if name == "kaufkasten":
                s.js("() => { const z = document.querySelector('.nachfrage'); if(z) z.remove(); }")
        assert s.fehler == []
    finally:
        ctx.close()


def test_android_felder_und_viewport_wie_vorher(browser, basis, heute_stand):
    """Gegenprobe: Android behaelt 15 px in den .field-Feldern und den
    Viewport ohne maximum-scale und viewport-fit."""
    ctx, s = _start(browser, basis, heute_stand, plattform="android", ua=None, breite=360, hoehe=640)
    try:
        vp = s.js("() => document.querySelector('meta[name=viewport]').content")
        assert vp == "width=device-width, initial-scale=1.0", vp
        s.js("() => showSettings()")
        felder = {f["id"]: f["px"] for f in s.js(FELDER)}
        assert felder["fbText"] == 15 and felder["kontoMail"] == 15, felder
        assert s.fehler == []
    finally:
        ctx.close()


# ----------------------------------------- zurueck in der App (Build 4) ---
def _protokoll(s, stueck):
    return any(stueck in z for z in s.js("() => TON_PROTOKOLL"))


def test_zurueck_setzt_fort_verwirft_das_bestellte_wort_und_entsperrt_neu(motor, basis, heute_stand):
    """Nur inaktiv (Siri, Anruf): der Kontext ist 'interrupted', die Seite
    bleibt sichtbar. Bei 'appStateChange' mit isActive: das auf der alten Uhr
    bestellte Wort faellt weg, resume() ohne Tipp, und erst wenn die Uhr
    wieder nachweislich laeuft, kommen die Woerter ueber WebAudio. Der
    naechste Tipp spielt spieler und Ein-Sample-Puffer neu an - ohne neuen
    Kontext."""
    ctx, s = _start(motor, basis, heute_stand)
    try:
        w = s.js(WORT)
        _tippen(s)
        _puffer(s, w)
        _bereit_lebt(s)
        s.page.wait_for_function("() => spielerFrei === true && vorwaermen === null")
        assert s.js(APP_MELDET, ["appStateChange", {"isActive": False}]) == 1
        s.js("""() => { actx.zustand('interrupted'); window.__ton.resume = []; window.__gestoppt = 0;
                        waQuelle = {onended: null, stop(){ window.__gestoppt++; }}; }""")
        assert s.js("() => [tonInaktiv, tonUhrLesen()]") == [True, "unklar"]

        s.js(APP_MELDET, ["appStateChange", {"isActive": True}])
        r = s.js("""() => ({resume: window.__ton.resume, gestoppt: window.__gestoppt, wa: waQuelle === null,
                            frei: spielerFrei, tonFrei: tonFrei === null, inaktiv: tonInaktiv, z: actx.state})""")
        assert [x["von"] for x in r["resume"]] == ["interrupted"] and r["resume"][0]["ev"] is None, r
        assert r["gestoppt"] == 1 and r["wa"] and r["frei"] is False and r["tonFrei"], r
        assert r["inaktiv"] is False and r["z"] == "running", r
        assert _protokoll(s, "zurueck (aktiv): AudioContext interrupted") and _protokoll(s, "App inaktiv")
        # Bis die Uhr bewiesen ist, der spieler; dann WebAudio wie vorher
        if not s.js("() => tonUhr && tonUhr.lebt"):
            assert s.js(SPRECHEN, w) == {"webaudio": 0, "spieler": 1}
        _bereit_lebt(s)
        _puffer(s, w)
        assert s.js(SPRECHEN, w) == {"webaudio": 1, "spieler": 0}

        # Der naechste Tipp: Ein-Sample-Puffer und spieler neu, Kontext derselbe
        s.page.wait_for_timeout(200)
        assert s.js("() => spielerFrei") is False             # die Woerter dazwischen machen ihn nicht frei
        s.js("() => { window.__ton.spiele = []; window.__ton.starts = []; }")
        _tippen(s)
        t = _ton(s)
        assert len(t["neu"]) == 1 and t["zu"] == [], t
        eins = [x for x in t["starts"] if x["n"] == 1]
        assert eins and eins[0]["ev"] in GESTEN, t
        assert t["spiele"] and t["spiele"][0]["muted"] is True and t["spiele"][0]["ev"] in GESTEN, t
        assert s.fehler == []
    finally:
        ctx.close()


def test_zurueck_bleibt_er_stehen_wird_er_verworfen(motor, basis, heute_stand):
    """Im Hintergrund 'suspended', und resume() hilft nicht: RUECKKEHR_MS
    spaeter geschlossen. Bis zum naechsten Tipp sprechen die Woerter ueber den
    spieler, ohne Tipp entsteht kein neuer Kontext. Zurueck kommt die Seite
    hier ueber 'resume' vom Plugin App, ohne visibilitychange."""
    ctx, s = _start(motor, basis, heute_stand)
    try:
        w = s.js(WORT)
        _tippen(s)
        _puffer(s, w)
        _bereit_lebt(s)
        s.js(SICHT, [True, True])
        s.js(APP_MELDET, ["pause", None])
        s.js("""() => { actx.zustand('suspended'); window.__ton.resume = [];
                        actx.resume = function(){ window.__ton.resume.push({nr: this.nr, von: this._z, ev: null});
                                                  return Promise.resolve(); }; }""")
        assert s.js("() => tonInaktiv") is True
        s.js(SICHT, [False, False])
        assert s.js(APP_MELDET, ["resume", None]) == 1
        assert [x["von"] for x in _ton(s)["resume"]] == ["suspended"]
        assert s.js("() => actx !== null && spielerFrei === false")
        s.page.wait_for_function("() => actx === null", timeout=3000)
        t = _ton(s)
        assert [x["nr"] for x in t["zu"]] == [0], t
        assert _protokoll(s, "AudioContext tot (zurueck, suspended)")
        assert s.js(SPRECHEN, w) == {"webaudio": 0, "spieler": 1}
        s.js("() => sound('ok')")
        assert len(_ton(s)["neu"]) == 1                       # ohne Tipp kein neuer

        _tippen(s)
        t = _ton(s)
        assert len(t["neu"]) == 2 and t["neu"][1]["ev"] in GESTEN, t
        _bereit_lebt(s)
        assert s.js(SPRECHEN, w) == {"webaudio": 1, "spieler": 0}
        assert s.fehler == []
    finally:
        ctx.close()


def test_zurueck_uhr_steht_trotz_running(webkit, basis, heute_stand):
    """Wieder sichtbar, der Kontext meldet 'running', aber seine Uhr steht:
    die Wanduhr-Probe nach der Rueckkehr schliesst ihn, der naechste Tipp
    legt einen neuen an."""
    ctx, s = _start(webkit, basis, heute_stand)
    try:
        _tippen(s)
        _bereit_lebt(s)
        s.js(SICHT, [True, True])
        s.js("() => actx.stirb()")
        s.js(SICHT, [False, True])
        assert s.js("() => actx !== null && actx.state") == "running"
        s.page.wait_for_function("() => actx === null", timeout=3000)
        assert _protokoll(s, "AudioContext tot (zurueck)") and _protokoll(s, "zurueck (sichtbar): AudioContext running")
        _tippen(s)
        t = _ton(s)
        assert len(t["neu"]) == 2 and t["neu"][1]["ev"] in GESTEN, t
        assert s.fehler == []
    finally:
        ctx.close()


def test_inaktiv_zaehlt_die_uhr_nicht(motor, basis, heute_stand):
    """Kontrollzentrum, Siri, Anruf: die App ist inaktiv, die Seite sichtbar.
    Steht die Uhr dann, ist das kein toter Kontext - kein Schliessen, die
    Woerter ueber den spieler. Erst zurueck in der App zaehlt die Probe
    wieder. Ein Fingertipp hebt das Inaktiv auf, falls 'appStateChange' mit
    isActive einmal fehlt."""
    ctx, s = _start(motor, basis, heute_stand)
    try:
        w = s.js(WORT)
        _tippen(s)
        _puffer(s, w)
        _bereit_lebt(s)
        s.js(APP_MELDET, ["appStateChange", {"isActive": False}])
        s.js("() => { actx.stirb(); sound('ok'); }")          # die erste Probe der Uhr
        s.page.wait_for_timeout(700)                          # mehr als UHR_WAND: jetzt waere sie 'tot'
        s.js("() => sound('no')")
        assert s.js(SPRECHEN, w) == {"webaudio": 0, "spieler": 1}
        assert s.js("() => actx !== null") and _ton(s)["zu"] == []
        s.js(APP_MELDET, ["appStateChange", {"isActive": True}])
        s.page.wait_for_function("() => actx === null", timeout=3000)
        assert [x["nr"] for x in _ton(s)["zu"]] == [0]

        s.js(APP_MELDET, ["appStateChange", {"isActive": False}])
        assert s.js("() => tonInaktiv") is True
        _tippen(s)
        assert s.js("() => tonInaktiv") is False
        assert len(_ton(s)["neu"]) == 2
        assert s.fehler == []
    finally:
        ctx.close()


def test_android_rueckkehr_wie_vorher(motor, basis, heute_stand):
    """Gegenprobe: auf Android haengt die Seite am Plugin App nur 'backButton'
    wie vorher, keine Horcher fuer 'appStateChange', 'pause' und 'resume'.
    Verdecken und wieder Zeigen setzen den Kontext weder fort noch schliessen
    sie ihn, und es gibt kein Ton-Protokoll. Auf iOS haengen alle vier."""
    ctx, s = _start(motor, basis, heute_stand, plattform="android", ua=None)
    try:
        s.page.wait_for_function("() => window.__ton.neu.length === 1 && vorwaermen === null", timeout=10000)
        assert sorted(s.js("() => Object.keys(window.__app)")) == ["backButton"]
        s.js("() => { actx.zustand('suspended'); window.__ton.resume = []; }")
        s.js(SICHT, [True, True])
        s.js(SICHT, [False, True])
        s.page.wait_for_timeout(1300)                         # laenger als RUECKKEHR_MS
        t = _ton(s)
        assert t["resume"] == [] and t["zu"] == [] and len(t["neu"]) == 1, t
        assert s.js("() => actx.state") == "suspended"
        assert s.js("() => [tonInaktiv, tonRueckkehr]") == [False, 0]
        assert s.js("() => TON_PROTOKOLL") == []
        assert s.fehler == []
    finally:
        ctx.close()
    ctx, s = _start(motor, basis, heute_stand)
    try:
        assert sorted(s.js("() => Object.keys(window.__app)")) == ["appStateChange", "backButton", "pause", "resume"]
        assert s.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("plattform", ["ios", "android"])
def test_geschichte_vom_system_angehalten(browser, basis, heute_stand, plattform):
    """Haelt das System eine vorgelesene Geschichte an (Anruf, Siri), merkt
    sie sich auf iOS die Stelle wie beim Wechsel in den Hintergrund, und ein
    zweites pause() haelt WebKit davon ab, sie nach der Unterbrechung von
    selbst weiterzuspielen. "Vorlesen" macht dann dort weiter. Das Ende der
    Aufnahme zaehlt nicht. Android: wie vorher, nur der Knopf springt zurueck.
    (Chromium: die Attrappe spielt nichts ab, das Anhalten wird als
    'pause'-Ereignis nachgestellt.)"""
    ios = plattform == "ios"
    ctx, s = _start(browser, basis, heute_stand, plattform=plattform, ua=UA_IOS26 if ios else None)
    try:
        s.js("() => openStory(0)")
        s.page.click("#rListen")
        s.page.wait_for_function("() => laeuftVor !== null && spieler.src.includes('/audio/')")
        anhalten = """(ende) => {
          if(!window.__pausen){
            window.__pausen = {n: 0};
            const orig = HTMLMediaElement.prototype.pause;
            spieler.pause = function(){ window.__pausen.n++; return orig.call(this); };
          }
          Object.defineProperty(spieler, 'currentTime', {configurable: true, get: () => ende ? 30 : 12.5, set(){}});
          Object.defineProperty(spieler, 'duration', {configurable: true, get: () => 30});
          Object.defineProperty(spieler, 'ended', {configurable: true, get: () => !!ende});
          const vorher = window.__pausen.n;
          spieler.dispatchEvent(new Event('pause'));
          return {stelle: geschichteStelle, pausen: window.__pausen.n - vorher, laeuft: laeuftVor !== null,
                  knopf: document.getElementById('rListen').classList.contains('laeuft'), src: spieler.src};
        }"""
        r = s.js(anhalten, False)
        assert r["laeuft"] is False and r["knopf"] is False, r
        if ios:
            assert r["stelle"] == {"datei": r["src"], "sekunde": 12.5} and r["pausen"] == 1, r
            assert _protokoll(s, "Geschichte von aussen angehalten bei 12.5 s")
        else:
            assert r["stelle"] is None and r["pausen"] == 0, r
            assert s.js("() => TON_PROTOKOLL") == []

        # Vorlesen nimmt die Stelle mit, und das Ende der Aufnahme merkt nichts
        s.page.click("#rListen")
        s.page.wait_for_function("() => laeuftVor !== null")
        assert s.js("() => geschichteStelle") is None
        r = s.js(anhalten, True)
        assert r["stelle"] is None and r["pausen"] == 0 and r["laeuft"] is False, r
        assert s.fehler == []
    finally:
        ctx.close()


@pytest.mark.parametrize("plattform", ["ios", "android"])
def test_kein_doppeltipp_zoom_nur_auf_ios(motor, basis, heute_stand, plattform):
    """iOS: der Viewport ist nicht zoombar (min = max = 1, user-scalable=no),
    und jedes Element hat touch-action: manipulation - auch in einem Kasten
    mit eigenem Bildlauf, wo WebKit die touch-action neu beginnt. Android:
    der Viewport wie vorher, touch-action ueberall auto."""
    ios = plattform == "ios"
    ctx, s = _start(motor, basis, heute_stand, plattform=plattform, ua=UA_IOS26 if ios else None)
    try:
        vp = s.js("() => document.querySelector('meta[name=viewport]').content")
        if ios:
            assert vp == ("width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0,"
                          " user-scalable=no, viewport-fit=cover"), vp
        else:
            assert vp == "width=device-width, initial-scale=1.0", vp
        for js in ("() => { homeMode = 'words'; showHome(); }", "() => showSettings()",
                   "() => { showHome(); openLevel(0); startLesson(); }"):
            s.js(js)
            r = s.js("""() => {
              const k = document.createElement('div'); k.style.cssText = 'overflow:auto; height:40px';
              const b = document.createElement('button'); b.textContent = 'x'; k.appendChild(b);
              document.body.appendChild(k);
              const alle = [document.documentElement, document.body, ...document.querySelectorAll('body *')];
              const werte = [...new Set(alle.map(e => getComputedStyle(e).touchAction))];
              const knopf = getComputedStyle(b).touchAction;
              k.remove();
              return {werte, knopf, n: alle.length};
            }""")
            assert r["n"] > 50, r
            soll = "manipulation" if ios else "auto"
            assert r["werte"] == [soll] and r["knopf"] == soll, (js, r)
        assert s.fehler == []
    finally:
        ctx.close()
