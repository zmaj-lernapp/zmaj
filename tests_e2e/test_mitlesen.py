# -*- coding: utf-8 -*-
"""Mitlesen beim Vorlesen einer Geschichte (20.10.2026, Wunsch von Kuebra).

Das Wort, das die Stimme gerade spricht, ist markiert - nur die Schrift
gelb, kein Kasten (Ajdin: "mach die buchstaben gelb nicht aussenrum"). Schon
Gesprochenes wird blasser. Die Zeiten kommen als Feld "w" aus
audio/index.json, ein Paar [start_ms, ende_ms] je Wort.

Gespielt wird die echte Aufnahme der Geschichte im echten Chrome. Die
Wortzeiten schiebt der Test aber selbst unter (WORTZEITEN in der App): ein
Wort alle 600 ms, 300 ms lang. Dann liegt zwischen je zwei Woertern eine
Luecke von 180 ms - laenger als der Nachlauf von 120 ms -, und man kann
genau sagen, was zu jedem Zeitpunkt markiert sein muss, ohne von der
Stimme in der Aufnahme abzuhaengen. Die echten Zeiten prueft
test_echte_wortzeiten_passen.

Verglichen wird immer der Zustand mit spieler.currentTime aus DEMSELBEN
Bild: der Test liest in einem requestAnimationFrame, der nach dem der App
laeuft. Bewegung ist immer ausdruecklich aus (reduced_motion), sonst stuende
waehrend des Farbwechsels (transition .12s) eine Zwischenfarbe da.

Springen: Der Dateiserver der Tests (http.server) kennt keine
Range-Anfragen. Ohne sie meldet Chrome die Aufnahme als nicht springbar
(seekable 0-0), und JEDER Sprung landet bei Sekunde null - am 20.10.2026
nachgemessen; die ersten Fassungen dieser Tests waren dadurch scheinbar
gruen, weil alles bei null stimmte. Die Aufnahmen liefert hier deshalb
_mit_bereichen() aus, mit 206 und Content-Range wie ein richtiger Server.
"""
import os
import re

import pytest
from conftest import Seite

SCHRITT, DAUER, NACHLAUF = 600, 300, 120
ANFANG = 1000

# Geschichte oeffnen und Wortzeiten unterschieben. `weniger`: so viele Paare
# fehlen am Ende (falsche Anzahl). Dazu ein Zaehler fuer jedes Bild, das die
# Mitlese-Schleife bestellt - so sieht man, ob sie nach dem Stopp weiterlaeuft.
VORBEREITEN = """([nr, schritt, dauer, anfang, weniger, kaputt]) => {
  openStory(nr);
  const s = STORIES[nr], datei = audioDatei(s.text);
  const n = document.querySelectorAll('#rBody .txt .w').length;
  const z = [];
  for(let i = 0; i < n - weniger; i++) z.push([anfang + i*schritt, anfang + i*schritt + dauer]);
  if(kaputt) z[3] = ['1', '2'];
  WORTZEITEN.set(datei, z);
  window.__takte = 0;
  if(!window.__rafOrig){
    window.__rafOrig = window.requestAnimationFrame;
    window.requestAnimationFrame = function(cb){
      if(cb === mitlesenTakt) window.__takte++;
      return window.__rafOrig.call(window, cb);
    };
  }
  return {datei: datei, n: n};
}"""

# Zustand nach zwei Bildern: die Schleife der App hat dann sicher einmal
# mit derselben currentTime gerechnet, die hier gelesen wird.
ZUSTAND = """() => new Promise(res => requestAnimationFrame(() => requestAnimationFrame(() => {
  const ws = [...document.querySelectorAll('#rBody .txt .w')];
  const idx = k => ws.map((w, i) => w.classList.contains(k) ? i : -1).filter(i => i >= 0);
  res({t: spieler.currentTime * 1000, pausiert: spieler.paused, akt: idx('mitlesen'),
       gelesen: idx('gelesen'), aktiv: mitlesen !== null, takte: window.__takte,
       ueberall: document.querySelectorAll('.mitlesen, .gelesen').length});
})))"""

# Springen, sobald die Aufnahme ganz geladen ist. Der Testserver kann keine
# Range-Anfragen; gesprungen werden kann dann nur im schon Geladenen.
SPRINGEN = """async (ms) => {
  const bis = async (bed) => { const e = Date.now() + 8000;
    while(!bed()){ if(Date.now() > e) throw new Error('Aufnahme laedt nicht'); await new Promise(r => setTimeout(r, 20)); } };
  await bis(() => spieler.duration > 0 && spieler.buffered.length && spieler.buffered.end(0) >= spieler.duration - 0.05);
  await new Promise(res => { spieler.addEventListener('seeked', res, {once: true}); spieler.currentTime = ms / 1000; });
  // Nie wieder scheinbar gruen: der Sprung muss wirklich angekommen sein.
  if(Math.abs(spieler.currentTime * 1000 - ms) > 150) throw new Error('Sprung nach ' + ms + ' landete bei ' + spieler.currentTime);
}"""

LAEUFT = "() => mitlesen !== null && !spieler.paused && spieler.currentTime > 0.05"


def erwartet(t, n):
    """(aktuelles Wort oder -1, Anzahl gelesener) - dieselbe Regel wie
    mitlesenZeigen() in index.html, unabhaengig davon aufgeschrieben."""
    z = [(ANFANG + i * SCHRITT, ANFANG + i * SCHRITT + DAUER) for i in range(n)]
    begonnen = sum(1 for s, _ in z if s <= t)
    akt = -1
    if begonnen:
        i = begonnen - 1
        ende = min(z[i][1] + NACHLAUF, z[i + 1][0] if i + 1 < n else float("inf"))
        if t < ende:
            akt = i
    return akt, (akt if akt >= 0 else begonnen)


def stimmt(zustand, n):
    akt, gelesen = erwartet(zustand["t"], n)
    return zustand["akt"] == ([akt] if akt >= 0 else []) and zustand["gelesen"] == list(range(gelesen))


_AUFNAHMEN = {}


def _mit_bereichen(route):
    """MP3 mit Range-Antwort ausliefern (siehe oben, Springen)."""
    url = route.request.url
    if url not in _AUFNAHMEN:
        _AUFNAHMEN[url] = route.fetch().body()     # der Testserver schickt immer alles
    daten = _AUFNAHMEN[url]
    kopf = {"Content-Type": "audio/mpeg", "Accept-Ranges": "bytes"}
    m = re.match(r"bytes=(\d+)-(\d*)", route.request.headers.get("range") or "")
    if not m:
        route.fulfill(status=200, body=daten, headers=kopf)
        return
    a = int(m.group(1))
    e = min(int(m.group(2)) if m.group(2) else len(daten) - 1, len(daten) - 1)
    kopf["Content-Range"] = "bytes %d-%d/%d" % (a, e, len(daten))
    route.fulfill(status=206, body=daten[a:e + 1], headers=kopf)


def neue_seite(browser, basis, schema="dark", hoehe=640):
    ctx = browser.new_context(viewport={"width": 360, "height": hoehe}, locale="de-DE",
                              service_workers="block", reduced_motion="reduce", color_scheme=schema)
    ctx.route("**/audio/*.mp3", _mit_bereichen)
    seite = Seite(ctx.new_page(), basis)
    seite.konsole = []
    seite.page.on("console", lambda m: seite.konsole.append("%s @ %s" % (m.text, m.location.get("url")))
                  if m.type == "error" else None)
    return ctx, seite


def starten(seite, stand):
    """Wie seite.starten, danach zaehlt die Konsole von vorn. Beim Start gibt
    es zwei gewollte 404: /leer (dort wird der Stand gesetzt) und
    /api/daten - ohne Server laeuft die App wie auf dem Handy."""
    seite.starten(stand=stand)
    seite.konsole.clear()


def vorlesen(seite):
    """Den grossen Knopf wirklich antippen (Nutzergeste fuer play()) und
    warten, bis die Aufnahme laeuft und das Mitlesen steht."""
    seite.page.click("#rListen")
    seite.page.wait_for_function(LAEUFT, timeout=10000)


def an_stelle(seite, ms, n):
    """Zu ms springen und den Zustand lesen. Laeuft der Ton weiter, kann
    zwischen Sprung und Lesen ein Wortwechsel liegen - dann zaehlt der
    gelesene Zeitpunkt, und `stimmt` vergleicht mit genau dem."""
    seite.js(SPRINGEN, ms)
    z = seite.js(ZUSTAND)
    assert stimmt(z, n), (ms, z, erwartet(z["t"], n))
    return z


@pytest.fixture
def dunkel(browser, basis, heute_stand):
    ctx, seite = neue_seite(browser, basis, "dark")
    starten(seite, heute_stand())
    yield seite
    ctx.close()


def test_richtiges_wort_zur_richtigen_zeit(dunkel):
    seite = dunkel
    n = seite.js(VORBEREITEN, [0, SCHRITT, DAUER, ANFANG, 0, False])["n"]
    assert n > 20
    vorlesen(seite)
    # Mitten in Wort 3, im Nachlauf von Wort 12, in der Luecke nach Wort 12,
    # und zurueck an den Anfang vor dem ersten Wort.
    for ms in (ANFANG + 3 * SCHRITT + 100, ANFANG + 12 * SCHRITT + DAUER + 60,
               ANFANG + 12 * SCHRITT + DAUER + NACHLAUF + 40, 200):
        an_stelle(seite, ms, n)
    z = an_stelle(seite, ANFANG + 5 * SCHRITT + 50, n)
    assert z["akt"] == [5] and z["gelesen"] == [0, 1, 2, 3, 4], z

    # Laufen lassen: jedes Bild ueber gut zwei Sekunden muss stimmen, und es
    # muss dabei weitergehen (mindestens drei verschiedene Woerter).
    proben = seite.js("""() => new Promise(res => { const out = [], ende = performance.now() + 2200;
      const ws = [...document.querySelectorAll('#rBody .txt .w')];
      const idx = k => ws.map((w, i) => w.classList.contains(k) ? i : -1).filter(i => i >= 0);
      requestAnimationFrame(function f(){
        out.push({t: spieler.currentTime * 1000, akt: idx('mitlesen'), gelesen: idx('gelesen')});
        if(performance.now() < ende) requestAnimationFrame(f); else res(out); }); })""")
    assert len(proben) > 30
    falsch = [p for p in proben if not stimmt(p, n)]
    assert not falsch, falsch[:3]
    assert len({p["akt"][0] for p in proben if p["akt"]}) >= 3
    # Der Zaehler sieht die Schleife wirklich - sonst bewiesen die Pruefungen
    # "laeuft nach dem Stopp nicht weiter" nichts.
    assert seite.js("() => window.__takte") > 30

    # Tempo mitten im Lesen: die Zeiten gelten in der Aufnahme, nicht auf der Uhr.
    seite.page.click("#rTempo button[data-tempo='0.75']")
    assert seite.js("() => spieler.playbackRate") == 0.75
    an_stelle(seite, ANFANG + 20 * SCHRITT + 40, n)

    # Aussehen: Gelb nur in der Schrift, kein Kasten, keine andere Staerke.
    stil = seite.js("""() => { const ws = [...document.querySelectorAll('#rBody .txt .w')];
      const a = ws.find(w => w.classList.contains('mitlesen')), g = ws.find(w => w.classList.contains('gelesen')),
            frei = ws[ws.length - 1], s = getComputedStyle(a);
      return {farbe: s.color, grund: s.backgroundColor, staerke: s.fontWeight, rahmen: s.outlineStyle,
              schatten: s.boxShadow, freiStaerke: getComputedStyle(frei).fontWeight,
              gelesen: getComputedStyle(g).opacity, freiOpacity: getComputedStyle(frei).opacity}; }""")
    assert stil["farbe"] == "rgb(255, 210, 63)"            # --accent im Dunkeln
    assert stil["grund"] == "rgba(0, 0, 0, 0)" and stil["schatten"] == "none" and stil["rahmen"] == "none"
    assert stil["staerke"] == stil["freiStaerke"]
    assert stil["gelesen"] == "0.65" and stil["freiOpacity"] == "1"
    assert seite.fehler == [] and seite.konsole == []


def test_pause_haelt_weiter_laeuft(dunkel):
    seite = dunkel
    n = seite.js(VORBEREITEN, [0, SCHRITT, DAUER, ANFANG, 0, False])["n"]
    vorlesen(seite)
    seite.js(SPRINGEN, ANFANG + 5 * SCHRITT + 20)
    seite.page.click("#rListen")                            # Pause
    seite.page.wait_for_function("() => spieler.paused && pausiert")
    vorher = seite.js(ZUSTAND)
    assert stimmt(vorher, n) and len(vorher["gelesen"]) >= 5, vorher
    takte = vorher["takte"]
    seite.page.wait_for_timeout(700)
    nachher = seite.js(ZUSTAND)
    assert nachher["akt"] == vorher["akt"] and nachher["gelesen"] == vorher["gelesen"]
    assert nachher["t"] == vorher["t"]
    # In der Pause bestellt die Schleife keine Bilder.
    assert nachher["takte"] == takte, "Mitlese-Schleife laeuft in der Pause weiter"

    seite.page.click("#rListen")                            # Weiter
    seite.page.wait_for_function(LAEUFT)
    seite.page.wait_for_function("(g) => document.querySelectorAll('#rBody .txt .w.gelesen').length > g",
                                 arg=len(vorher["gelesen"]), timeout=4000)
    assert stimmt(seite.js(ZUSTAND), n)
    assert seite.fehler == [] and seite.konsole == []


def _aufgeraeumt(seite):
    """Keine Markierung mehr, Schleife aus, und sie bestellt auch spaeter
    kein Bild mehr."""
    z = seite.js(ZUSTAND)
    assert z["ueberall"] == 0 and not z["aktiv"], z
    vorher = z["takte"]
    seite.page.wait_for_timeout(400)
    assert seite.js("() => window.__takte") == vorher, "Mitlese-Schleife laeuft nach dem Ende weiter"


def test_stopp_raeumt_auf(dunkel):
    seite = dunkel
    n = seite.js(VORBEREITEN, [0, SCHRITT, DAUER, ANFANG, 0, False])["n"]
    vorlesen(seite)
    an_stelle(seite, ANFANG + 4 * SCHRITT + 50, n)
    seite.page.click("#rStop")
    _aufgeraeumt(seite)
    assert seite.fehler == [] and seite.konsole == []


def test_ende_der_aufnahme_raeumt_auf(dunkel):
    seite = dunkel
    seite.js(VORBEREITEN, [0, SCHRITT, DAUER, ANFANG, 0, False])
    vorlesen(seite)
    seite.page.wait_for_function("() => document.querySelector('#rBody .txt .w.mitlesen, #rBody .txt .w.gelesen')",
                                 timeout=4000)
    seite.js("async () => { const d = spieler.duration; await (%s)((d - 0.3) * 1000); }" % SPRINGEN)
    seite.page.wait_for_function("() => laeuftVor === null && !document.getElementById('rListen').classList.contains('laeuft')",
                                 timeout=5000)
    _aufgeraeumt(seite)
    assert seite.fehler == [] and seite.konsole == []


def test_antippen_raeumt_auf_und_weiterlesen_setzt_richtig_ein(dunkel):
    seite = dunkel
    n = seite.js(VORBEREITEN, [0, SCHRITT, DAUER, ANFANG, 0, False])["n"]
    vorlesen(seite)
    seite.js(SPRINGEN, ANFANG + 8 * SCHRITT + 30)
    # Ein Wort weiter vorn antippen: Blase auf, Vorlesen unterbrochen.
    seite.page.locator("#rBody .txt .w").nth(2).click()
    seite.page.wait_for_function("() => !document.getElementById('rBubble').hidden")
    z = seite.js(ZUSTAND)
    assert z["akt"] == [] and z["gelesen"] == [] and not z["aktiv"]
    assert seite.js("() => document.querySelectorAll('#rBody .txt .w.on').length") == 1   # .on bleibt wie bisher
    stelle = seite.js("() => geschichteStelle && geschichteStelle.sekunde * 1000")
    assert stelle and stelle >= ANFANG + 8 * SCHRITT + 30
    # Weiterlesen: setzt an der gemerkten Stelle ein, nicht bei null.
    seite.page.click("#rListen")
    seite.page.wait_for_function("() => mitlesen !== null && spieler.currentTime * 1000 >= %d" % int(stelle - 1),
                                 timeout=8000)
    z = seite.js(ZUSTAND)
    assert stimmt(z, n), z
    assert len(z["gelesen"]) >= 8, z
    assert seite.fehler == [] and seite.konsole == []


@pytest.mark.parametrize("weg", ["andere_geschichte", "ansicht_verlassen", "wort_einzeln"])
def test_wechsel_raeumt_auf(dunkel, weg):
    seite = dunkel
    n = seite.js(VORBEREITEN, [0, SCHRITT, DAUER, ANFANG, 0, False])["n"]
    vorlesen(seite)
    an_stelle(seite, ANFANG + 6 * SCHRITT + 50, n)
    alte = seite.js("() => { window.__alt = [...document.querySelectorAll('#rBody .txt .w')]; return window.__alt.length; }")
    assert alte == n
    if weg == "andere_geschichte":
        seite.js("() => openStory(1)")
    elif weg == "ansicht_verlassen":
        seite.js("() => { homeMode = 'stories'; showHome(); }")
    else:   # ein anderer Ton ueber speak() - etwa der Lautsprecher in der Blase
        seite.js("() => { stilleBitte(); speak(STORIES[0].text.split(' ')[0]); }")
    _aufgeraeumt(seite)
    # Auch die abgehaengten Knoten der alten Geschichte tragen nichts mehr.
    assert seite.js("() => window.__alt.filter(w => w.classList.contains('mitlesen') || w.classList.contains('gelesen')).length") == 0
    assert seite.fehler == [] and seite.konsole == []


@pytest.mark.parametrize("weniger, kaputt", [(1, False), (-1, False), (0, True)])
def test_unpassende_zeiten_keine_markierung(dunkel, weniger, kaputt):
    """Ein Paar zu wenig, eins zu viel, oder Unsinn darin: lieber keine
    Markierung als eine falsche - still, ohne Fehler."""
    seite = dunkel
    seite.js(VORBEREITEN, [0, SCHRITT, DAUER, ANFANG, weniger, kaputt])
    seite.page.click("#rListen")
    seite.page.wait_for_function("() => !spieler.paused && spieler.currentTime > 0.05", timeout=10000)
    seite.js(SPRINGEN, ANFANG + 3 * SCHRITT + 50)
    z = seite.js(ZUSTAND)
    assert z["ueberall"] == 0 and not z["aktiv"] and z["takte"] == 0, z
    assert seite.js("() => document.getElementById('rListen').classList.contains('laeuft')")   # vorgelesen wird trotzdem
    assert seite.fehler == [] and seite.konsole == []


def test_echte_wortzeiten_passen(dunkel):
    """Die Zeiten aus audio/index.json (wortzeiten_holen.py) passen zu jeder
    Geschichte, so wie die App sie in Woerter zerlegt. Schlaegt das fehl,
    wurde ein Text geaendert und die Zeiten nicht neu geholt - dann bleibt
    diese Geschichte ohne Markierung."""
    seite = dunkel
    ergebnis = seite.js("""() => STORIES.map((s, i) => { openStory(i);
      const datei = audioDatei(s.text), n = document.querySelectorAll('#rBody .txt .w').length;
      return {nr: i, datei: datei, n: n, paare: (WORTZEITEN.get(datei) || []).length,
              passt: !!mitlesZeiten(datei, n)}; })""")
    assert len(ergebnis) >= 12
    assert [e for e in ergebnis if not e["passt"]] == []
    assert seite.fehler == []


def _kontrast(a, b):
    def lum(rgb):
        def kanal(c):
            c = c / 255
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b_ = (kanal(x) for x in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b_
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _rgb(text):
    return tuple(int(float(x)) for x in text[text.index("(") + 1:text.index(")")].split(",")[:3])


@pytest.mark.parametrize("schema, wahl, gelb", [
    ("dark", None, True), ("light", None, False),
    ("light", "dunkel", True), ("dark", "hell", False)])
def test_farbe_gelb_im_dunkeln_lesbar_im_hellen(browser, basis, heute_stand, schema, wahl, gelb):
    """Im Dunkeln das Gelb der App. Im Hellen waere es unlesbar (1,5:1) -
    dort das Gold, das die App fuer gelbe Schrift hat (--accent-text, wie
    "Jetzt dran"), mit mindestens 4,5:1 gegen die Karte und auch auf dem
    Hellgelb eines angetippten Worts: die Schrift ist 20px und nicht fett,
    also kein grosser Text (WCAG AA). Bis zur Pruefung am 20.10.2026 waren
    es #A07D00 mit 3,6:1. Die eigene Wahl in den Einstellungen (hell/dunkel)
    geht vor der des Geraets. Alle neun Sektionen: test_axe_beim_mitlesen."""
    ctx, seite = neue_seite(browser, basis, schema)
    try:
        seite.starten(stand=heute_stand())
        if wahl:
            seite.js("(w) => { localStorage.setItem('zmaj_theme', w); }", wahl)
            seite.neu_laden()
        f = seite.js("""() => { openStory(0); const ws = document.querySelectorAll('#rBody .txt .w');
          ws[1].classList.add('mitlesen'); ws[2].classList.add('mitlesen', 'on');
          return {farbe: getComputedStyle(ws[1]).color, karte: getComputedStyle(document.getElementById('rBody')).backgroundColor,
                  aufOn: getComputedStyle(ws[2]).color, onGrund: getComputedStyle(ws[2]).backgroundColor,
                  schrift: getComputedStyle(ws[0]).color}; }""")
        farbe, karte = _rgb(f["farbe"]), _rgb(f["karte"])
        assert f["aufOn"] == f["farbe"]                       # auch ein angetipptes Wort wird gelb
        if gelb:
            assert farbe == (255, 210, 63)
        else:
            assert farbe == (135, 106, 0)                        # --accent-text #876A00
            r, g, b = farbe                                      # wirkt golden: Rot und Gruen hoch, kein Blau
            assert b == 0 and 0.7 < g / r < 0.85
        assert _kontrast(farbe, karte) >= 4.5, (f, _kontrast(farbe, karte))
        assert _kontrast(farbe, _rgb(f["onGrund"])) >= 4.5
        assert farbe != _rgb(f["schrift"])
        assert seite.fehler == []
    finally:
        ctx.close()


AXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "axe.min.js")

# Fuenf Woerter gelesen, eins wird gesprochen, und eins wird gesprochen, das
# vorher angetippt war (Hellgelb dahinter) - in der Sektionsfarbe `sek`.
# axe nur mit der Regel color-contrast und nur ueber den Text. elementRef,
# damit man sieht, ob die markierten Woerter wirklich geprueft wurden: kann
# axe den Grund eines Worts nicht sicher bestimmen, legt es das Wort unter
# "incomplete" ab, und ein leeres Ergebnis bewiese nichts.
AXE_MITLESEN = """async (sek) => {
  document.documentElement.setAttribute('data-sek', String(sek));
  window.scrollTo(0, 0);
  const ws = document.querySelectorAll('#rBody .txt .w');
  ws.forEach(w => w.classList.remove('gelesen', 'mitlesen', 'on'));
  for(let i = 0; i < 5; i++) ws[i].classList.add('gelesen');
  ws[5].classList.add('mitlesen'); ws[6].classList.add('mitlesen', 'on');
  await new Promise(r => setTimeout(r, 250));
  const e = await axe.run(document.querySelector('#rBody .txt'), {runOnly: ['color-contrast'], elementRef: true});
  const art = n => n.element.classList.contains('gelesen') ? 'gelesen'
                 : n.element.classList.contains('mitlesen') ? 'mitlesen' : 'frei';
  const liste = typ => e[typ].flatMap(r => r.nodes.map(n => art(n) + ': ' + ((n.any[0] || {}).message || '')));
  return {verstoesse: liste('violations'),
          unklar: liste('incomplete').filter(x => !x.startsWith('frei')),
          geprueft: e.passes.concat(e.violations).flatMap(r => r.nodes.map(art)),
          karte: getComputedStyle(document.getElementById('rBody')).backgroundColor};
}"""


@pytest.mark.parametrize("schema", ["light", "dark"])
def test_axe_beim_mitlesen(browser, basis, heute_stand, schema):
    """axe (color-contrast) ueber eine Geschichte im Vorlesezustand, in jeder
    der neun Sektionsfarben: das gesprochene Wort, auch auf dem Hellgelb
    eines angetippten Worts, und die blasseren gelesenen erreichen 4,5:1.
    Die uebrigen axe-Tests sehen das nicht - sie zeigen keine Geschichte
    beim Vorlesen. Gegenprobe im Hellen mit den Werten der ersten Fassung
    (#A07D00, .55): dann meldet axe jedes markierte Wort, der Test kann es
    also sehen. Befund der Pruefung vom 20.10.2026."""
    ctx, seite = neue_seite(browser, basis, schema)
    try:
        starten(seite, heute_stand())
        seite.page.wait_for_function("() => !document.getElementById('vorspann')", timeout=15000)
        seite.js("() => { openStory(0); }")
        seite.page.add_script_tag(path=AXE)
        karten = set()
        for sek in range(1, 10):
            e = seite.js(AXE_MITLESEN, sek)
            karten.add(e["karte"])
            assert e["verstoesse"] == [], (schema, sek, e["verstoesse"])
            assert e["unklar"] == [], (schema, sek, e["unklar"])
            assert e["geprueft"].count("gelesen") == 5 and e["geprueft"].count("mitlesen") == 2, (schema, sek, e)
        assert len(karten) == 9                     # jede Sektion hat wirklich ihre eigene Flaeche
        if schema == "light":
            seite.js("""() => { const s = document.createElement('style');
              s.textContent = '.story{--mitlesen:#A07D00} .story .w.gelesen{opacity:.55}';
              document.head.appendChild(s); }""")
            e = seite.js(AXE_MITLESEN, 1)
            assert sorted(x.split(":")[0] for x in e["verstoesse"]) == ["gelesen"] * 5 + ["mitlesen"] * 2, e
        assert seite.fehler == [] and seite.konsole == []
    finally:
        ctx.close()


def test_folgt_dem_wort_ohne_zu_reissen(browser, basis, heute_stand):
    """Die laengste Geschichte ist laenger als der Bildschirm. Verlaesst das
    aktuelle Wort den sichtbaren Bereich, rueckt die Seite nach. Wer aber
    weggescrollt hat (das Wort davor ist nicht zu sehen), bleibt, wo er ist."""
    ctx, seite = neue_seite(browser, basis, "dark", hoehe=560)
    try:
        starten(seite, heute_stand())
        nr = seite.js("() => STORIES.reduce((m, s, i, a) => s.text.length > a[m].text.length ? i : m, 0)")
        n = seite.js(VORBEREITEN, [nr, SCHRITT, DAUER, ANFANG, 0, False])["n"]
        vorlesen(seite)
        seite.js("() => window.scrollTo(0, 0)")
        k = seite.js("""() => [...document.querySelectorAll('#rBody .txt .w')]
          .findIndex(w => w.getBoundingClientRect().bottom > innerHeight)""")
        if k < 1:
            pytest.skip("Geschichte passt ganz auf den Bildschirm")
        an_stelle(seite, ANFANG + (k - 1) * SCHRITT + 50, n)
        assert seite.js("() => scrollY") == 0                   # Wort davor sichtbar: nichts tun
        an_stelle(seite, ANFANG + k * SCHRITT + 50, n)
        lage = seite.js("""(k) => { const r = document.querySelectorAll('#rBody .txt .w')[k].getBoundingClientRect();
          return {y: scrollY, oben: r.top, unten: r.bottom, h: innerHeight}; }""", k)
        assert lage["y"] > 0 and lage["oben"] >= 0 and lage["unten"] <= lage["h"], lage

        # Ganz nach unten zu den Fragen: der Anfang des Textes ist weg.
        seite.js("() => window.scrollTo(0, document.documentElement.scrollHeight)")
        unten = seite.js("() => scrollY")
        weg = seite.js("() => document.querySelectorAll('#rBody .txt .w')[4].getBoundingClientRect().bottom <= 0")
        if not weg:
            pytest.skip("Seite zu kurz, um den Textanfang wegzuscrollen")
        an_stelle(seite, ANFANG + 5 * SCHRITT + 50, n)
        assert seite.js("() => scrollY") == unten
        assert seite.fehler == [] and seite.konsole == []
    finally:
        ctx.close()
