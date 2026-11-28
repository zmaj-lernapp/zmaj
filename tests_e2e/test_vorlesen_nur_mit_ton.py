# -*- coding: utf-8 -*-
"""Vorlesen nur mit Aufnahme (Offen-Liste 6; Prüfbericht 1.4, V1; 16.11.2026).

Die App-Hülle hat keine Computerstimme. Bis zum 16.11.2026 stand "Vorlesen"
auch bei den B1-Texten, die noch keine Aufnahme hatten, und ein Tipp darauf
tat nichts. Jetzt zeigt showStory() den Knopf, den Stopp-Knopf und die
Tempo-Leiste nur, wenn es die Geschichte als Aufnahme gibt (audioDatei).
Seit diesem Tag hat jede Geschichte eine. Der zweite Test nimmt einer
Geschichte ihre Aufnahme weg, so wie bei einer neuen Geschichte vor ihrem Ton."""

OEFFNEN = """(nr) => { openStory(nr); stilleBitte();
  const da = id => !!document.getElementById(id);
  return {id: STORIES[nr].id, datei: audioDatei(STORIES[nr].text), vorlesen: da('rListen'),
          stopp: da('rStop'), tempo: da('rTempo'),
          tempoKnoepfe: document.querySelectorAll('#rTempo button').length,
          uebersetzen: da('rTrans'), woerter: document.querySelectorAll('#rBody .txt .w').length}; }"""


def test_jede_geschichte_hat_ton_und_den_knopf(seite, heute_stand):
    seite.starten(stand=heute_stand())
    n = seite.js("() => STORIES.length")
    assert n >= 32, n
    alle = [seite.js(OEFFNEN, i) for i in range(n)]
    ohne = [g["id"] for g in alle if not (g["datei"] and g["vorlesen"] and g["stopp"] and g["tempo"])]
    assert ohne == [], ohne
    assert {g["tempoKnoepfe"] for g in alle} == {4}
    assert all(g["datei"].startswith("g") for g in alle), [g["datei"] for g in alle]
    assert seite.fehler == []


def test_ohne_aufnahme_kein_vorlesen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    seite.js("() => { window.__oeffnen = " + OEFFNEN + "; }")
    r = seite.js("""() => {
      const oeffnen = window.__oeffnen;
      const nr = STORIES.findIndex(s => s.id === 'b1_selidba');
      const key = STORIES[nr].text.split(' / ')[0].trim().toLowerCase();
      const datei = AUDIO.get(key);
      AUDIO.delete(key);
      const ohne = oeffnen(nr);
      // Woerter antippen geht weiter, die Blase zeigt die Bedeutung
      const w = document.querySelector('#rBody .txt .w');
      w.click();
      const blase = document.getElementById('rBubble');
      ohne.blase = !blase.hidden && blase.textContent.includes(w.textContent);
      ohne.zeile = document.querySelector('#rBody .row').children.length;
      AUDIO.set(key, datei);
      const mit = oeffnen(nr);
      return {datei: datei, ohne: ohne, mit: mit}; }""")
    assert r["datei"] and r["datei"].startswith("g"), r
    ohne, mit = r["ohne"], r["mit"]
    assert ohne["datei"] is None
    assert not ohne["vorlesen"] and not ohne["stopp"] and not ohne["tempo"], ohne
    assert ohne["uebersetzen"] and ohne["zeile"] == 1 and ohne["woerter"] > 100, ohne
    assert ohne["blase"], ohne
    assert mit["vorlesen"] and mit["stopp"] and mit["tempo"] and mit["tempoKnoepfe"] == 4, mit
    assert seite.fehler == []


def test_vorlesen_spielt_die_aufnahme(seite, heute_stand):
    """Mit Aufnahme spielt der Knopf genau die Datei der Geschichte, hier die
    neue Geschichte "Dedo i nana se sele"."""
    seite.starten(stand=heute_stand())
    nr = seite.js("() => STORIES.findIndex(s => s.id === 'b1_selidba')")
    datei = seite.js(OEFFNEN, nr)["datei"]
    seite.js("() => document.getElementById('rListen').click()")
    seite.page.wait_for_function("() => !spieler.paused && spieler.currentTime > 0.05", timeout=10000)
    lage = seite.js("""() => ({src: spieler.src, laeuft: document.getElementById('rListen').classList.contains('laeuft'),
                               stopp: !document.getElementById('rStop').hidden})""")
    seite.js("() => document.getElementById('rStop').click()")
    assert lage["src"].endswith("audio/" + datei), (lage, datei)
    assert lage["laeuft"] and lage["stopp"], lage
    assert seite.fehler == []
