# -*- coding: utf-8 -*-
"""Das Wort kommt frueher (22.10.2026).

Ajdin: "der sprecher sagt viel zu spaet die woerter oder saetze die muessen
frueher kommen man wartet zu lange bis er anfaengt". In index.html sind es
zwei Dinge (die Stille am Anfang der Aufnahmen kuerzt app_bauen.py, siehe
tests/test_huelle.py):

- Nach der Antwort wartet die App nur so lange, wie der Rueckmeldeton
  hoerbar ist - nachAntwort(): 180 ms richtig, 250 ms falsch, 40 ms ohne
  Toene - statt fest 450 ms. Beim Erscheinen einer Aufgabe 100 statt 250
  bzw. 300 ms.
- Beim Start laeuft die Tonausgabe einmal stumm an, und der AudioContext
  fuer die Rueckmeldetoene entsteht schon dann (tonVorwaermen).

Zum Abspielen braucht es einen Browser, der wie die WebView ohne Geste
abspielen darf (Capacitor: setMediaPlaybackRequiresUserGesture(false)).
Der aus conftest.py darf das nicht; er reicht fuer die Wartezeiten.
"""
import os

import pytest
from conftest import Seite

# Jede bestellte Wartezeit mitschreiben, samt Aufgabenart. Gesprochen wird
# trotzdem - der Spion reicht nur durch.
SPION = """() => {
  window.__wann = [];
  const echt = spaeterSprechen;
  spaeterSprechen = (text, ms) => {
    window.__wann.push([Lx && Lx.queue[Lx.i] ? Lx.queue[Lx.i].typ : '?', ms]);
    echt(text, ms);
  };
}"""

# Eine einzelne Auswahlaufgabe zum ersten Wort mit Aufnahme.
MC = """() => {
  const w = CATEGORIES[0].words.find(x => audioDatei(x.bs));
  openLevel(0); startLesson();
  Lx.queue = [{typ: 'mc', w}]; Lx.i = 0; Lx.total = 1;
  showLessonTask();
  window.__wann = [];
  return {bs: w.bs, ziel: 'audio/' + audioDatei(w.bs)};
}"""


def test_kuerzer_warten_nach_der_antwort(seite, heute_stand):
    """Eine ganze Lektion, alles richtig: nach jeder Antwort 180 ms, beim
    Erscheinen (neues Wort, Hoerfrage) 100 ms. Falsch: 250 ms, damit das
    Wort nicht in den laengeren Fehlton hineinredet. Ohne Toene 40 ms."""
    seite.starten(stand=heute_stand())
    seite.js("() => { openLevel(0); startLesson(); }")
    seite.js(SPION)
    typen = seite.durchspielen("lBody", "Lx")
    wann = seite.js("() => window.__wann")
    assert wann, "nichts vorgelesen"
    for typ, ms in wann:
        assert ms == (100 if typ in ("intro", "listen") else 180), (typ, ms)
    assert {t for t, _ in wann} >= {"intro", "mc"}, (typen, wann)

    seite.js(MC)
    seite.js("() => [...document.querySelectorAll('#lBody .opt')].find(o => o.textContent !== Lx.queue[0].w.bs).click()")
    assert seite.js("() => window.__wann") == [["mc", 250]]

    seite.js("() => { soundOn = false; }")
    seite.js(MC)
    seite.js("() => [...document.querySelectorAll('#lBody .opt')].find(o => o.textContent === Lx.queue[0].w.bs).click()")
    assert seite.js("() => window.__wann") == [["mc", 40]]
    assert seite.fehler == []


@pytest.fixture(scope="module")
def wie_webview(browser):
    b = browser.browser_type.launch(executable_path=os.environ.get("ZMAJ_CHROMIUM") or None,
                                    args=["--autoplay-policy=no-user-gesture-required"])
    yield b
    b.close()


@pytest.fixture
def webview_seite(wie_webview, basis):
    """Ohne Bewegung: dann waermt die App gleich nach dem Start vor und nicht
    erst nach dem Vorspann. Jedes play() wird mitgeschrieben, samt muted."""
    ctx = wie_webview.new_context(viewport={"width": 360, "height": 640}, locale="de-DE",
                                  service_workers="block", reduced_motion="reduce")
    ctx.add_init_script("""(() => {
      const play = HTMLMediaElement.prototype.play;
      window.__spiele = [];
      HTMLMediaElement.prototype.play = function(){
        window.__spiele.push({muted: this.muted, src: this.getAttribute('src')});
        return play.call(this);
      };
    })()""")
    s = Seite(ctx.new_page(), basis)
    yield s
    ctx.close()


# Fertig vorgewaermt: einmal abgespielt, und der Anlauf ist vorbei.
VORGEWAERMT = "() => window.__spiele.length > 0 && vorwaermen === null"


def test_vorwaermen_beim_start(webview_seite, heute_stand):
    """Einmal stumm angespielt - Stille aus dem Speicher, keine Anfrage -,
    danach wieder laut und leer; der AudioContext laeuft schon vor der
    ersten Antwort."""
    seite = webview_seite
    seite.starten(stand=heute_stand())
    seite.page.wait_for_function(VORGEWAERMT, timeout=10000)
    z = seite.js("() => ({spiele: window.__spiele, muted: spieler.muted, paused: spieler.paused,"
                 " src: spieler.getAttribute('src'), actx: actx && actx.state})")
    assert z["spiele"] and z["spiele"][0]["muted"] is True, z
    assert z["spiele"][0]["src"].startswith("blob:"), z
    assert z["muted"] is False and z["paused"] is True and z["src"] is None, z
    assert z["actx"] == "running", z
    assert seite.fehler == []


def test_wort_waehrend_des_vorwaermens_bleibt_laut(webview_seite, heute_stand):
    """Kommt ein echtes Wort, solange der stumme Anlauf laeuft, spielt es
    laut weiter - der Abschluss des Anlaufs haelt es nicht an."""
    seite = webview_seite
    seite.starten(stand=heute_stand())
    seite.page.wait_for_function(VORGEWAERMT, timeout=10000)
    r = seite.js("""async () => {
      stilleBitte(); spieler.removeAttribute('src'); spieler.load();
      tonVorwaermen();
      const an = {muted: spieler.muted, laeuft: vorwaermen !== null};
      const w = CATEGORIES[0].words.find(x => audioDatei(x.bs));
      speak(w.bs);
      await new Promise(r => setTimeout(r, 400));
      const z = {an, muted: spieler.muted, paused: spieler.paused, vorwaermen,
                 src: spieler.getAttribute('src'), ziel: 'audio/' + audioDatei(w.bs)};
      stilleBitte();
      return z;
    }""")
    assert r["an"] == {"muted": True, "laeuft": True}, r
    assert r["muted"] is False and r["paused"] is False and r["vorwaermen"] is None, r
    assert r["src"] == r["ziel"], r
    assert seite.fehler == []


def test_wort_nach_der_antwort_frueh_und_laut(webview_seite, heute_stand):
    """Nach einer richtigen Antwort laeuft das Wort laut, und 'playing' kommt
    deutlich vor den 450 ms, die die App bis zum 22.10.2026 allein gewartet
    hat (jetzt 180 ms Wartezeit plus Abspielweg)."""
    seite = webview_seite
    seite.starten(stand=heute_stand())
    seite.page.wait_for_function(VORGEWAERMT, timeout=10000)
    aufgabe = seite.js(MC)
    r = seite.js("""async (bs) => {
      let playing = null;
      const t0 = performance.now();
      spieler.addEventListener('playing', () => { if(playing === null) playing = performance.now() - t0; });
      [...document.querySelectorAll('#lBody .opt')].find(o => o.textContent === bs).click();
      const ende = Date.now() + 3000;
      while((spieler.paused || spieler.currentTime === 0) && Date.now() < ende)
        await new Promise(r => setTimeout(r, 10));
      const z = {playing, laeuft: !spieler.paused && spieler.currentTime > 0,
                 muted: spieler.muted, src: spieler.getAttribute('src')};
      stilleBitte();
      return z;
    }""", aufgabe["bs"])
    assert r["laeuft"] and r["muted"] is False and r["src"] == aufgabe["ziel"], r
    assert r["playing"] is not None and 180 <= r["playing"] < 450, r
    assert seite.fehler == []
