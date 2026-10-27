# -*- coding: utf-8 -*-
"""Woerter und Saetze ueber WebAudio (26.10.2026).

Ajdin: "die sprecher stimme kommt immernoch etwas zu langsam". Seitdem
dekodiert die App das Wort einer Aufgabe schon beim Erscheinen (und das der
naechsten) und spielt es ueber WebAudio: nach einer Antwort auf der Uhr des
Rueckmeldetons (ABSTAND_OK/ABSTAND_NO nach Tonbeginn, ab kurz vor dem
ersten Laut der Datei), beim neuen Wort und bei der Hoerfrage sofort. Der
spieler bleibt der Rueckfall und spielt die Geschichten.

Gemessen wird nichts Hoerbares: Spione auf AudioBufferSourceNode.start/stop,
OscillatorNode.start (Rueckmeldeton) und HTMLMediaElement.play schreiben
mit, wann was bestellt wurde - in Kontextzeit, also genau so, wie es die
Ausgabe spaeter abspielt. Playwright stellt Chromium stumm (--mute-audio),
das laeuft auch unter Linux ohne Tonausgabe. Der Browser darf wie die
WebView ohne Geste abspielen (Capacitor: setMediaPlaybackRequiresUserGesture
(false)).

Nachtrag nach der Pruefung (26.10.2026): auch der Vorlauf (nur Stille
wird uebersprungen), PUFFER_MAX und die Notbremsen gegen ein verlorenes
oder doppeltes Wort haben je einen Test - siehe unten.
"""
import os

import pytest
from conftest import Seite

SPIONE = """(() => {
  window.__starts = []; window.__stops = []; window.__osz = []; window.__spiele = [];
  const start = AudioBufferSourceNode.prototype.start;
  AudioBufferSourceNode.prototype.start = function(when, offset){
    window.__starts.push({when: when || 0, offset: offset || 0, jetzt: this.context.currentTime,
                          zustand: this.context.state, quelle: this, t: performance.now()});
    return start.apply(this, arguments);
  };
  const stop = AudioBufferSourceNode.prototype.stop;
  AudioBufferSourceNode.prototype.stop = function(){
    window.__stops.push({quelle: this, jetzt: this.context.currentTime, t: performance.now()});
    return stop.apply(this, arguments);
  };
  const osz = OscillatorNode.prototype.start;
  OscillatorNode.prototype.start = function(when){
    window.__osz.push({when: when || 0, t: performance.now()});
    return osz.apply(this, arguments);
  };
  const play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function(){
    window.__spiele.push({muted: this.muted, src: this.getAttribute('src'), rate: this.playbackRate, t: performance.now()});
    return play.call(this);
  };
})()"""

# Eine Lektion aus genau diesen Aufgabenarten, je ein anderes Wort mit Aufnahme.
LEKTION = """(typen) => {
  const gesehen = new Set(), ws = [];
  CATEGORIES.forEach(c => c.words.forEach(w => {
    const d = audioDatei(w.bs);
    if(d && !gesehen.has(d)){ gesehen.add(d); ws.push(w); }
  }));
  openLevel(0); startLesson();
  Lx.queue = typen.map((typ, i) => ({typ, w: ws[i], pool: CATEGORIES[0].words}));
  Lx.i = 0; Lx.total = Lx.queue.length;
  showLessonTask();
  return Lx.queue.map(q => audioDatei(q.w.bs));
}"""

GELADEN = "(dateien) => dateien.every(d => puffer.get(d) && puffer.get(d).buf)"

# Die laufende Auswahlaufgabe beantworten. Alles, was dabei bestellt wird,
# steht danach schon in den Spionen: ohne Zeitgeber geschieht es noch im Klick.
ANTWORTEN = """(ok) => {
  window.__starts = []; window.__osz = []; window.__spiele = [];
  const w = Lx.queue[Lx.i].w, datei = audioDatei(w.bs);
  [...document.querySelectorAll('#lBody .opt')].find(o => ok ? o.textContent === w.bs : o.textContent !== w.bs).click();
  const p = puffer.get(datei);
  return {starts: window.__starts.map(s => ({when: s.when, offset: s.offset, jetzt: s.jetzt,
                                             richtig: !!p && s.quelle.buffer === p.buf})),
          osz: window.__osz.map(o => o.when), vorlauf: p && p.buf ? p.vorlauf : null,
          datei, laeuft: waQuelle !== null, abstand: [ABSTAND_OK, ABSTAND_NO]};
}"""

SPIELER_WORTE = "() => window.__spiele.filter(s => (s.src || '').startsWith('audio/')).map(s => s.src)"


@pytest.fixture(scope="module")
def wie_webview(browser):
    b = browser.browser_type.launch(executable_path=os.environ.get("ZMAJ_CHROMIUM") or None,
                                    args=["--autoplay-policy=no-user-gesture-required"])
    yield b
    b.close()


@pytest.fixture
def ws(wie_webview, basis):
    ctx = wie_webview.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                                  service_workers="block", reduced_motion="reduce")
    ctx.add_init_script(SPIONE)
    s = Seite(ctx.new_page(), basis)
    yield s
    ctx.close()


def bereit(seite, stand):
    """Gestartet und vorgewaermt: der AudioContext laeuft."""
    seite.starten(stand=stand)
    seite.page.wait_for_function("() => window.__spiele.length > 0 && vorwaermen === null"
                                 " && actx && actx.state === 'running'", timeout=10000)


def lektion(seite, typen, warten=2):
    dateien = seite.js(LEKTION, typen)
    assert all(dateien), dateien
    seite.page.wait_for_function(GELADEN, arg=dateien[:warten], timeout=10000)
    return dateien


@pytest.mark.parametrize("ok", [True, False])
def test_nach_der_antwort_auf_der_uhr_des_tons(ws, heute_stand, ok):
    """Das Wort wird im Klick bestellt, ABSTAND_OK bzw. ABSTAND_NO nach dem
    Beginn des Rueckmeldetons, ab dem Vorlauf der Datei - kein Zeitgeber,
    kein spieler."""
    bereit(ws, heute_stand())
    lektion(ws, ["mc", "mc"])
    r = ws.js(ANTWORTEN, ok)
    assert r["abstand"] == [0.167, 0.186], r
    assert len(r["starts"]) == 1 and r["starts"][0]["richtig"], r
    assert r["osz"], "kein Rueckmeldeton"
    s, ton = r["starts"][0], min(r["osz"])
    assert abs(s["when"] - ton - (0.167 if ok else 0.186)) < 1e-6, (s, ton)
    assert s["when"] > s["jetzt"], s                       # bestellt, noch nicht zu hoeren
    assert r["vorlauf"] is not None and 0 <= r["vorlauf"] < 0.5 and s["offset"] == r["vorlauf"], r
    assert r["laeuft"]
    ws.page.wait_for_timeout(500)
    assert ws.js(SPIELER_WORTE) == []                       # kein Rueckfall hinterher
    assert ws.js("() => window.__starts.length") == 1       # und nichts doppelt
    assert ws.fehler == []


def test_abstand_ist_gemessen(seite, heute_stand):
    """Beleg fuer ABSTAND_OK/ABSTAND_NO: die Toene aus sound() offline
    gerendert, als Huellkurve (ConstantSource statt Oszillator). Setzt das
    Wort ein (Start + VORLAUF_RAND), ist der Ton hoechstens -30 dBFS laut;
    5 ms frueher waere er es noch nicht - es ist der kleinste solche Wert."""
    seite.starten(stand=heute_stand())
    r = seite.js("""async () => {
      const echt = actx, an = soundOn, sr = 48000, aus = {};
      for(const art of ['ok', 'no']){
        const off = new OfflineAudioContext(1, sr * 0.6, sr);
        off.createOscillator = function(){ const c = this.createConstantSource(); c.frequency = {value: 0}; return c; };
        off.resume = () => Promise.resolve();   // sound() setzt fort, was noch nicht laeuft - offline ginge das schief
        actx = off; soundOn = true;
        try{ sound(art); } finally { actx = echt; soundOn = an; }
        const h = (await off.startRendering()).getChannelData(0);
        const db = s => 20 * Math.log10(Math.max(Math.abs(h[Math.round(s * sr)]), 1e-9));
        const ein = (art === 'ok' ? ABSTAND_OK : ABSTAND_NO) + VORLAUF_RAND;
        aus[art] = {ein: db(ein), frueher: db(ein - 0.005), spaeter: db(ein + 0.05)};
      }
      return aus;
    }""")
    for art in ("ok", "no"):
        assert r[art]["ein"] <= -30 and r[art]["spaeter"] < r[art]["ein"], r
        assert r[art]["frueher"] > -30, r
    assert seite.fehler == []


@pytest.mark.parametrize("typ, knopf", [("intro", "#xListen"), ("listen", "#xPlay")])
def test_neues_wort_und_hoerfrage_sofort(ws, heute_stand, typ, knopf):
    """Liegt der Puffer bereit, spielt das Wort, sobald die Aufgabe steht
    (frueher 100 ms Wartezeit und dann der spieler). Der Hoeren-Knopf
    spielt ebenfalls sofort und stellt das laufende Wort vorher ab."""
    bereit(ws, heute_stand())
    dateien = lektion(ws, ["intro", typ])
    r = ws.js("""() => {
      window.__starts = []; window.__stops = []; window.__spiele = [];
      document.querySelector('#lBody #xNext').click();
      const p = puffer.get(audioDatei(Lx.queue[Lx.i].w.bs));
      return {i: Lx.i, starts: window.__starts.map(s => ({when: s.when, jetzt: s.jetzt, richtig: s.quelle.buffer === p.buf}))};
    }""")
    assert r["i"] == 1 and len(r["starts"]) == 1 and r["starts"][0]["richtig"], r
    assert r["starts"][0]["when"] <= r["starts"][0]["jetzt"] + 0.003, r     # sofort
    ws.page.wait_for_timeout(60)
    k = ws.js("""(knopf) => {
      const erste = window.__starts[0].quelle;
      document.querySelector('#lBody ' + knopf).click();
      const zweite = window.__starts[1];
      return {n: window.__starts.length, erste: window.__stops.some(s => s.quelle === erste),
              sofort: !!zweite && zweite.when <= zweite.jetzt + 0.003, laeuft: !!zweite && waQuelle === zweite.quelle};
    }""", knopf)
    assert k == {"n": 2, "erste": True, "sofort": True, "laeuft": True}, k
    ws.page.wait_for_timeout(400)
    assert ws.js("() => window.__starts.length") == 2           # kein verspaeteter Zeitgeber
    assert ws.js(SPIELER_WORTE) == []
    assert dateien[1] and ws.fehler == []


def test_hoeren_in_der_wartezeit_kein_zweites_mal(ws, heute_stand):
    """Ist der Puffer beim Erscheinen noch nicht da, wartet das Wort wie
    bisher 100 ms. Tippt man in der Zeit auf Hoeren und der Puffer ist
    inzwischen da, kommt das Wort einmal - der Zeitgeber faengt es danach
    nicht noch einmal von vorn an."""
    bereit(ws, heute_stand())
    dateien = lektion(ws, ["intro", "intro"])
    r = ws.js("""async (d) => {
      const p = puffer.get(d); puffer.delete(d);       // beim Erscheinen noch nicht da
      window.__starts = []; window.__spiele = [];
      document.querySelector('#lBody #xNext').click();
      puffer.set(d, p);                                 // jetzt da
      document.querySelector('#lBody #xListen').click();
      await new Promise(r => setTimeout(r, 400));
      return {starts: window.__starts.length,
              spieler: window.__spiele.filter(s => (s.src || '').startsWith('audio/')).length};
    }""", dateien[1])
    assert r == {"starts": 1, "spieler": 0}, r
    assert ws.fehler == []


@pytest.mark.parametrize("fall", ["tempo", "ohne_puffer", "ohne_kontext", "datei_laedt_nicht"])
def test_rueckfall_auf_den_spieler(ws, heute_stand, fall):
    """Ohne bereiten Puffer, bei Tempo != 1 (WebAudio kennt kein
    preservesPitch), ohne AudioContext und wenn die Datei nicht laedt: wie
    vor dem 26.10.2026 ueber den spieler, nach der Wartezeit nachAntwort()."""
    bereit(ws, heute_stand())
    if fall == "datei_laedt_nicht":
        ws.page.route("**/audio/*", lambda route: route.fulfill(status=404, body="")
                      if route.request.resource_type == "fetch" else route.continue_())
        dateien = ws.js(LEKTION, ["mc", "mc"])
        ws.page.wait_for_function("(d) => !puffer.has(d)", arg=dateien[0], timeout=10000)
    else:
        dateien = lektion(ws, ["mc", "mc"])
    if fall == "tempo":
        ws.js("() => setzeTempo(0.75)")
    elif fall == "ohne_puffer":
        ws.js("() => puffer.clear()")
    elif fall == "ohne_kontext":
        ws.js("() => { actx = null; window.AudioContext = window.webkitAudioContext = undefined; }")
    r = ws.js(ANTWORTEN, True)
    assert r["starts"] == [] and not r["laeuft"], r
    ws.page.wait_for_function("(z) => window.__spiele.some(s => s.src === z)", arg="audio/" + dateien[0], timeout=5000)
    z = ws.js("() => ({muted: spieler.muted, rate: spieler.playbackRate, starts: window.__starts.length})")
    assert z == {"muted": False, "rate": 0.75 if fall == "tempo" else 1, "starts": 0}, z
    ws.js("() => { stilleBitte(); setzeTempo(1); }")
    assert ws.fehler == []


def test_stille_bitte_stoppt_auch_webaudio(ws, heute_stand):
    """Bestellt (nach der Antwort, noch nicht zu hoeren) und laufend (neues
    Wort): stilleBitte() stellt beides ab."""
    bereit(ws, heute_stand())
    lektion(ws, ["mc", "intro"])
    r = ws.js("""() => {
      window.__starts = []; window.__stops = [];
      const w = Lx.queue[Lx.i].w;
      [...document.querySelectorAll('#lBody .opt')].find(o => o.textContent === w.bs).click();
      const s = window.__starts[0];
      stilleBitte();
      const st = window.__stops.find(x => x.quelle === s.quelle);
      return {gestartet: !!s, gestoppt: !!st, vorDemStart: !!st && st.jetzt < s.when, frei: waQuelle === null};
    }""")
    assert r == {"gestartet": True, "gestoppt": True, "vorDemStart": True, "frei": True}, r
    ws.js("() => document.querySelector('#lBody .weiterbox .btn').click()")
    ws.page.wait_for_function("() => window.__starts.length === 2", timeout=5000)
    ws.page.wait_for_timeout(60)
    r = ws.js("""() => {
      const s = window.__starts[1];
      const lief = s.quelle.context.currentTime > s.when;
      stilleBitte();
      return {lief, gestoppt: window.__stops.some(x => x.quelle === s.quelle), frei: waQuelle === null};
    }""")
    assert r == {"lief": True, "gestoppt": True, "frei": True}, r
    assert ws.fehler == []


def test_schnell_weitertippen_nichts_doppelt_nichts_spaet(ws, heute_stand):
    """Antworten und gleich Weiter, ohne auf das Wort zu warten, dann die
    Lektion verlassen: jedes Wort ist abgestellt, bevor das naechste
    bestellt wird, keins kommt zweimal, und nach dem Verlassen kommt
    nichts mehr - weder ueber WebAudio noch verspaetet ueber den spieler."""
    bereit(ws, heute_stand())
    dateien = lektion(ws, ["mc", "mc", "intro", "mc", "mcrev", "mc"])
    # Alle sechs vorab dekodieren (die App holt immer nur die aktuelle und die
    # naechste) - sonst kaeme beim schnellen Tippen manches ueber den Zeitgeber.
    ws.js("(d) => d.forEach(pufferLaden)", dateien)
    ws.page.wait_for_function(GELADEN, arg=dateien, timeout=10000)
    r = ws.js("""async () => {
      window.__starts = []; window.__stops = []; window.__spiele = [];
      const body = document.getElementById('lBody');
      for(let n = 0; n < 6; n++){
        const q = Lx.queue[Lx.i];
        if(q.typ === 'intro') body.querySelector('#xNext').click();
        else {
          const soll = q.typ === 'mcrev' ? q.w.de : q.w.bs;
          [...body.querySelectorAll('.opt')].find(o => o.textContent === soll).click();
          if(n < 5) body.querySelector('.weiterbox .btn').click();
        }
        await new Promise(r => setTimeout(r, 20));
      }
      const verlassen = performance.now();
      lektionVerlassen();
      await new Promise(r => setTimeout(r, 700));
      const s = window.__starts, st = window.__stops;
      const stopVon = q => st.find(x => x.quelle === q);
      const zaehl = new Map();
      s.forEach(x => zaehl.set(x.quelle.buffer, (zaehl.get(x.quelle.buffer) || 0) + 1));
      return {n: s.length,
              ueberlappt: s.slice(0, -1).filter((x, i) => !stopVon(x.quelle) || stopVon(x.quelle).t > s[i + 1].t).length,
              nichtGestoppt: s.filter(x => !stopVon(x.quelle)).length,
              doppelt: Math.max(0, ...zaehl.values()),
              danach: s.filter(x => x.t > verlassen).length,
              spielerDanach: window.__spiele.filter(x => x.t > verlassen && (x.src || '').startsWith('audio/')).length,
              spieler: window.__spiele.filter(x => (x.src || '').startsWith('audio/')).length,
              frei: waQuelle === null};
    }""")
    assert r["n"] == 6, r          # jedes Wort ueber WebAudio
    assert r["ueberlappt"] == 0 and r["nichtGestoppt"] == 0 and r["doppelt"] == 1, r
    assert r["danach"] == 0 and r["spielerDanach"] == 0 and r["spieler"] == 0 and r["frei"], r
    assert ws.fehler == []


def test_geschichten_bleiben_beim_spieler(ws, heute_stand):
    """Auch wenn ein Puffer bereitlaege: die Geschichte und ein angetipptes
    Wort darin laufen ueber den spieler (Mitlesen, Pause, Weiterlesen)."""
    bereit(ws, heute_stand())
    r = ws.js("""async () => {
      openStory(0);
      const bis = async bed => { const e = Date.now() + 8000; while(!bed()){ if(Date.now() > e) throw new Error('laedt nicht'); await new Promise(r => setTimeout(r, 20)); } };
      const d = audioDatei(STORIES[0].text);
      const w = [...document.querySelectorAll('#rBody .txt .w')].find(x => audioDatei(x.textContent));
      const wd = audioDatei(w.textContent);
      pufferLaden(d); pufferLaden(wd);
      await bis(() => puffer.get(d) && puffer.get(d).buf && puffer.get(wd) && puffer.get(wd).buf);
      window.__starts = []; window.__spiele = [];
      document.getElementById('rListen').click();
      await new Promise(r => setTimeout(r, 200));
      const geschichte = {starts: window.__starts.length, spiele: window.__spiele.map(s => s.src)};
      w.click();
      await new Promise(r => setTimeout(r, 200));
      const wort = {starts: window.__starts.length, src: spieler.getAttribute('src')};
      stilleBitte();
      return {d, wd, geschichte, wort};
    }""")
    assert r["geschichte"]["starts"] == 0 and "audio/" + r["d"] in r["geschichte"]["spiele"], r
    assert r["wort"] == {"starts": 0, "src": "audio/" + r["wd"]}, r
    assert ws.fehler == []


def test_toene_aus_sofort_und_kontext_da(ws, heute_stand):
    """Mit Toenen aus entsteht der AudioContext trotzdem (die Woerter laufen
    darueber), und nach der Antwort kommt das Wort sofort - kein Ton, auf
    den zu warten waere."""
    ws.starten(stand=heute_stand())
    ws.js("() => localStorage.setItem('zmaj_sound', 'aus')")
    ws.neu_laden()
    ws.page.wait_for_function("() => window.__spiele.length > 0 && vorwaermen === null", timeout=10000)
    assert ws.js("() => ({sound: soundOn, kontext: !!actx})") == {"sound": False, "kontext": True}
    lektion(ws, ["mc", "mc"])
    r = ws.js(ANTWORTEN, True)
    assert r["osz"] == [] and len(r["starts"]) == 1 and r["starts"][0]["richtig"], r
    assert r["starts"][0]["when"] <= r["starts"][0]["jetzt"] + 0.003, r
    assert ws.fehler == []


def test_stillgelegter_kontext_wird_geweckt(ws, heute_stand):
    """Android legt den AudioContext nach rund 30 s Stille still. Vor dem
    Start wird er fortgesetzt; das Wort bleibt bei WebAudio, ohne Rueckfall."""
    bereit(ws, heute_stand())
    lektion(ws, ["mc", "mc"])
    ws.js("""async () => {
      soundOn = false;              // sonst weckt ihn schon der Rueckmeldeton
      await actx.suspend();
      window.__weck = 0;
      const r = AudioContext.prototype.resume;
      AudioContext.prototype.resume = function(){ window.__weck++; return r.apply(this, arguments); };
    }""")
    r = ws.js(ANTWORTEN, True)
    assert len(r["starts"]) == 1 and r["starts"][0]["richtig"], r
    ws.page.wait_for_timeout(400)
    z = ws.js("() => ({weck: window.__weck, zustand: actx.state, frei: waQuelle === null})")
    assert z["weck"] >= 1 and z["zustand"] == "running", z
    assert ws.js(SPIELER_WORTE) == []
    assert ws.fehler == []


def test_vorgeladen_ist_was_gesprochen_wird(ws, heute_stand):
    """Jede Aufgabenart dekodiert vorab genau den Text, den sie spricht -
    auch Lueckensatz (fertiger Satz), Kacheln und Grammatik. Mit wechselnder
    Zahl die gezogene Fassung."""
    bereit(ws, heute_stand())
    r = ws.js("""() => {
      window.__geladen = []; window.__gesagt = [];
      const pl = pufferLaden;
      pufferLaden = d => { window.__geladen.push(d); return pl(d); };
      const sp = spaeterSprechen;
      spaeterSprechen = (text, ms, ok) => { window.__gesagt.push({datei: audioDatei(text), vorher: window.__geladen.slice()}); return sp(text, ms, ok); };
      const ws = CATEGORIES[0].words.filter(w => audioDatei(w.bs));
      const gap = SENTENCES.find(s => !s.zahl && s.text.indexOf('___') >= 0 && audioDatei(s.text.replace('___', s.answer)));
      const kac = SATZBAU.find(s => !s.zahl && satzKacheln(s.bs).length >= 2 && audioDatei(s.bs));
      const lv = Object.keys(GRAMMAR).find(id => (GRAMMAR[id].uebungen || []).some(u => gramAntwortBosnisch(u.richtig) && audioDatei(u.richtig)));
      const gram = lv && GRAMMAR[lv].uebungen.find(u => gramAntwortBosnisch(u.richtig) && audioDatei(u.richtig));
      const q = [{typ: 'intro', w: ws[0]}, {typ: 'mc', w: ws[1]}, {typ: 'type', w: ws[2]}, {typ: 'listen', w: ws[3]}];
      if(gap) q.push({typ: 'gap', s: gap});
      if(kac) q.push({typ: 'kacheln', s: kac});
      if(gram) q.push({typ: 'gram', g: gram});
      openLevel(0); startLesson();
      Lx.queue = q; Lx.i = 0; Lx.total = q.length;
      showLessonTask();
      const z = SENTENCES.find(s => s.zahl && Array.isArray(s.zahl.werte) && s.zahl.werte.length > 1);
      const v = z && z.zahl.werte.find(n => n !== zahlWert(z.zahl.wort));
      return {typen: q.map(x => x.typ),
              zahl: z ? {ohne: aufgabeText({typ: 'gap', s: z}), mit: aufgabeText({typ: 'gap', s: z, v}),
                         soll: lueckeText(zahlFassung(z, v)), heute: lueckeText(z)} : null};
    }""")
    assert {"gap", "kacheln", "gram"} <= set(r["typen"]), r
    if r["zahl"]:
        assert r["zahl"]["ohne"] is None and r["zahl"]["mit"] == r["zahl"]["soll"] != r["zahl"]["heute"], r
    ws.durchspielen("lBody", "Lx")
    gesagt = ws.js("() => window.__gesagt")
    mit_datei = [g for g in gesagt if g["datei"]]
    assert len(mit_datei) >= 6, gesagt
    for g in mit_datei:
        assert g["datei"] in g["vorher"], g
    ws.js("() => stilleBitte()")
    assert ws.fehler == []


# ---- Nachtrag nach der Pruefung (26.10.2026) ----
# Die Teile, die man erst merkt, wenn sie fehlen. Jeder dieser Tests faellt
# durch, wenn man die Stelle in index.html entfernt oder verstellt (geprueft
# mit kaputten Kopien, Arbeitsordner sprecher_einbau/befunde).


def test_vorlauf_ueberspringt_nur_stille(ws, heute_stand):
    """Der Vorlauf an echten dekodierten Aufnahmen: uebersprungen wird nur,
    was leiser ist als -65 dBFS, und die Datei startet genau VORLAUF_RAND
    vor ihrem ersten lauteren Wert (auf ein Sample genau) - die Stille wird
    uebersprungen statt abgewartet. Mit -20 dBFS gingen 61 bis 174 ms
    Sprache verloren, die Tests merkten es nicht (Pruefung 26.10.2026). Die
    Aufnahmen in web/audio haben rund 130 ms Stille am Anfang, im Paket
    kuerzt app_bauen.py sie."""
    bereit(ws, heute_stand())
    dateien = lektion(ws, ["mc"] * 6)
    ws.js("(d) => d.forEach(pufferLaden)", dateien)
    ws.page.wait_for_function(GELADEN, arg=dateien, timeout=10000)
    r = ws.js("""(dateien) => dateien.map(d => {
      const p = puffer.get(d), b = p.buf, sr = b.sampleRate, still = Math.pow(10, -65 / 20), kanaele = [];
      for(let k = 0; k < b.numberOfChannels; k++) kanaele.push(b.getChannelData(k));
      let erst = Infinity;
      kanaele.forEach(x => { for(let i = 0; i < x.length && i < erst; i++) if(Math.abs(x[i]) > still){ erst = i; break; } });
      const bis = Math.round(p.vorlauf * sr);          // alles davor wird uebersprungen
      let spitze = 0;
      kanaele.forEach(x => { for(let i = 0; i < Math.min(bis, x.length); i++) spitze = Math.max(spitze, Math.abs(x[i])); });
      return {d, vorlauf: p.vorlauf, soll: Math.max(0, erst / sr - VORLAUF_RAND), sr,
              uebersprungen_db: 20 * Math.log10(Math.max(spitze, 1e-12))};
    })""", dateien)
    for x in r:
        assert x["uebersprungen_db"] <= -65, x                   # nichts Hoerbares abgeschnitten
        assert abs(x["vorlauf"] - x["soll"]) <= 1 / x["sr"], x   # und bis kurz vor den ersten Laut
        assert x["vorlauf"] > 0.05, x                            # die Stille wird wirklich uebersprungen
    assert ws.fehler == []


def test_puffer_bleibt_klein(ws, heute_stand):
    """Zwoelf Aufgaben mit je einem anderen Wort nacheinander: der
    Zwischenspeicher haelt nie mehr als PUFFER_MAX dekodierte Aufnahmen -
    sonst laege auf dem Handy jedes Wort der Sitzung im Speicher. Die
    aktuelle und die naechste bleiben darin und werden fertig geladen."""
    bereit(ws, heute_stand())
    dateien = lektion(ws, ["mc"] * 12, warten=0)
    r = ws.js("""async () => {
      const groessen = [];
      for(let i = 1; i < Lx.queue.length - 1; i++){
        Lx.i = i; showLessonTask();
        groessen.push(puffer.size);
        await new Promise(r => setTimeout(r, 30));
      }
      return {groessen, max: PUFFER_MAX};
    }""")
    assert max(r["groessen"]) == r["max"] == 6, r              # voll, aber nie darueber
    ws.page.wait_for_function(GELADEN, arg=dateien[-2:], timeout=10000)
    assert ws.js("() => puffer.size") <= 6
    ws.js("() => stilleBitte()")
    assert ws.fehler == []


def test_kontext_wacht_nicht_auf_spieler_springt_ein(ws, heute_stand):
    """Laeuft der stillgelegte AudioContext nicht wieder an (resume() kommt
    nie an), spielt nach WECKEN_MS der spieler das Wort - sonst bliebe es
    nach Android-Stille stumm. Die bestellte WebAudio-Quelle ist dann
    gestoppt und redet auch nicht hinein, wenn der Context spaeter doch
    anlaeuft."""
    bereit(ws, heute_stand())
    dateien = lektion(ws, ["mc", "mc"])
    ws.js("""async () => {
      await actx.suspend();
      window.__resume = AudioContext.prototype.resume;
      AudioContext.prototype.resume = function(){ return new Promise(() => {}); };
    }""")
    r = ws.js(ANTWORTEN, True)
    assert len(r["starts"]) == 1 and r["starts"][0]["richtig"], r
    ws.page.wait_for_function("(z) => window.__spiele.some(s => s.src === z)", arg="audio/" + dateien[0], timeout=5000)
    z = ws.js("""async () => {
      const q = window.__starts[0].quelle;
      const gestoppt = window.__stops.some(x => x.quelle === q), frei = waQuelle === null;
      await window.__resume.call(actx);
      await new Promise(r => setTimeout(r, 400));
      return {gestoppt, frei, starts: window.__starts.length, zustand: actx.state};
    }""")
    assert z == {"gestoppt": True, "frei": True, "starts": 1, "zustand": "running"}, z
    ws.js("() => stilleBitte()")
    assert ws.fehler == []


def test_nie_spieler_und_webaudio_zugleich(ws, heute_stand):
    """Es spricht immer nur einer. Laedt der spieler noch das Wort (beim
    ersten Tippen lag kein Puffer bereit) und man tippt erneut auf Hoeren,
    haelt pufferSpielen() ihn an: ein Wort, ein Start, und der spieler
    kommt auch spaeter nicht nach. Laeuft umgekehrt ein Wort ueber WebAudio
    und das naechste hat keinen Puffer, stellt spieleDatei() das erste ab."""
    bereit(ws, heute_stand())
    dateien = lektion(ws, ["intro", "intro"])
    r = ws.js("""async ([a, b]) => {
      const textA = Lx.queue[0].w.bs, textB = Lx.queue[1].w.bs, knopf = document.querySelector('#lBody #xListen');
      const spielerWoerter = () => window.__spiele.filter(s => (s.src || '').startsWith('audio/')).map(s => s.src);
      stilleBitte();
      window.__starts = []; window.__stops = []; window.__spiele = [];
      const pa = puffer.get(a); puffer.delete(a);
      knopf.click();                                   // ohne Puffer: der spieler laedt
      const spielerLief = !spieler.paused;
      puffer.set(a, pa);
      knopf.click();                                   // jetzt mit Puffer
      await new Promise(r => setTimeout(r, 300));
      const eins = {spielerLief, spielerAus: spieler.paused, starts: window.__starts.length, spieler: spielerWoerter()};
      stilleBitte();
      window.__starts = []; window.__stops = []; window.__spiele = [];
      speak(textA);                                    // ueber WebAudio
      const q = (window.__starts[0] || {}).quelle;
      const pb = puffer.get(b); puffer.delete(b);
      speak(textB);                                    // ohne Puffer ueber den spieler
      const zwei = {webaudio: !!q, gestoppt: window.__stops.some(x => x.quelle === q), frei: waQuelle === null,
                    spieler: spielerWoerter()};
      puffer.set(b, pb);
      stilleBitte();
      return {eins, zwei};
    }""", dateien)
    assert r["eins"] == {"spielerLief": True, "spielerAus": True, "starts": 1,
                         "spieler": ["audio/" + dateien[0]]}, r
    assert r["zwei"] == {"webaudio": True, "gestoppt": True, "frei": True,
                         "spieler": ["audio/" + dateien[1]]}, r
    assert ws.fehler == []


def test_alter_rueckton_verschiebt_das_wort_nicht(ws, heute_stand):
    """Das Wort nach einer Antwort richtet sich nur nach einem frischen
    Rueckmeldeton (rueckTonNehmen: hoechstens 1 s alt). Ein liegen
    gebliebener alter - etwa von der Uhr eines frueheren AudioContext -
    schiebt es nicht in die Zukunft, es kommt sofort. Gegenprobe: derselbe
    Ton frisch gilt, Start bei Tonbeginn + ABSTAND_OK."""
    bereit(ws, heute_stand())
    lektion(ws, ["mc", "mc"])
    r = ws.js("""() => {
      const text = Lx.queue[Lx.i].w.bs, zeit = actx.currentTime + 5;
      const versuch = um => {
        stilleBitte(); window.__starts = [];
        rueckTon = {art: 'ok', zeit, um};
        spaeterSprechen(text, nachAntwort(true), true);
        const s = window.__starts[0];
        return s ? {ms: Math.round((s.when - s.jetzt) * 1000), ab_ton: Math.round((s.when - zeit) * 1000)} : null;
      };
      const alt = versuch(performance.now() - 1500), frisch = versuch(performance.now());
      stilleBitte();
      return {alt, frisch, uebrig: rueckTon};
    }""")
    assert r["alt"] is not None and r["alt"]["ms"] <= 3, r            # sofort
    assert r["frisch"] is not None and r["frisch"]["ab_ton"] == 167, r
    assert r["uebrig"] is None, r                                     # nur einmal
    assert ws.fehler == []
