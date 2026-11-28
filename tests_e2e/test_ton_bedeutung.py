# -*- coding: utf-8 -*-
"""Eigener Ton je Bedeutung (21.11.2026) - im echten Browser, stumm.

Ajdin beim Test der 1.5: in einer Geschichte "sam" (bin) angetippt, und es kam das lange
a von sȃm (allein). Die App suchte den Ton nur nach dem Text. Seitdem traegt der Inhalt
an solchen Stellen "ton" (ton_bedeutung.json, tests/test_ton_bedeutung.py), und
eigenerTon() in web/js/ton_abspielen.js spielt ihn, sobald es die Aufnahme gibt.

Die Aufnahmen spricht Emir erst noch (w10059 bis w10093, Release/Wortschatz/
k2_2026-11-20/final/emir_liste.md). Seit dem Abend des 21.11.2026 bekommt jede Bedeutung
eine eigene, nur sȃm (allein) behaelt w1359. Die Tests tragen sie deshalb selbst in AUDIO ein,
wie app_bauen.emir_drueber() es fuer die App tun wird, und schreiben mit, welche Datei
abgespielt wuerde (wie tests_e2e/test_geschichtenwoerter_ton.py). Abgespielt wird
nichts. Ohne diese Eintraege - heute, und immer in der Web-Demo - muss alles klingen
wie vorher.
"""
import re

NEU = {"sam (bin)": "w10059.mp3", "mi (mir)": "w10060.mp3", "dug (lang)": "w10063.mp3",
       "smije (darf)": "w10071.mp3", "mi (wir)": "w10078.mp3", "dug (schulden)": "w10081.mp3",
       "smije (lacht)": "w10089.mp3"}

MITSCHREIBEN = """(neu) => {
  (window.__neu || []).forEach(k => AUDIO.delete(k));   // was ein frueherer Aufruf eingetragen hat
  window.__neu = Object.keys(neu);
  Object.entries(neu).forEach(([k, d]) => AUDIO.set(k, d));
  window.__gespielt = [];
  spieleDatei = (datei, fertig) => { window.__gespielt.push(datei); if(fertig) setTimeout(fertig, 0); return Promise.resolve(); };
  pufferSpielen = (text) => {
    const d = audioDatei(text), p = d && puffer.get(d);
    if(!p || !p.buf) return false;
    window.__gespielt.push(d); return true;
  };
}"""

OEFFNEN = """(gid) => { const i = STORIES.findIndex(s => s.id === gid);
  openStory(i); stilleBitte(); window.__gespielt = []; return i; }"""


def _genau(text):
    return re.compile("^" + re.escape(text) + "$")


def _antippen(seite, gid, wort, nr):
    """Das nr-te (ab 0) Vorkommen von wort in der Geschichte antippen, dann den
    Lautsprecher in der Blase: was wurde gespielt, was steht in der Blase?"""
    assert seite.js(OEFFNEN, gid) >= 0, gid
    w = seite.page.locator("#rBody .txt .w", has_text=_genau(wort)).nth(nr)
    n = w.get_attribute("data-n")
    w.click()
    seite.page.wait_for_function("() => window.__gespielt.length > 0", timeout=3000)
    seite.page.locator("#rBubble .wortton").click()
    seite.page.wait_for_function("() => window.__gespielt.length > 1", timeout=3000)
    r = seite.js("""() => ({gespielt: window.__gespielt.slice(),
        wort: (document.querySelector('#rBubble b') || {}).textContent || ''})""")
    return n, r


def test_geschichte_sam_als_bin_und_als_allein(seite, heute_stand):
    """b1_voz: "sama sam je pekla" (bin) und "nikad nisi sam na putu" (allein). Ohne Emirs
    neue Aufnahme spielen beide wie bisher w1359. Mit ihr spielt "bin" die neue, "allein"
    weiter w1359 - auch der Lautsprecher in der Blase. Die Blase zeigt das Wort."""
    seite.starten(stand=heute_stand())
    seite.js(MITSCHREIBEN, {})
    assert seite.js("() => audioDatei('sam')") == "w1359.mp3"
    for nr in (0, 1):
        n, r = _antippen(seite, "b1_voz", "sam", nr)
        assert n == str(nr + 1)
        assert r == {"gespielt": ["w1359.mp3", "w1359.mp3"], "wort": "sam"}, (nr, r)

    seite.js(MITSCHREIBEN, NEU)
    assert _antippen(seite, "b1_voz", "sam", 0)[1] == {"gespielt": ["w10059.mp3"] * 2, "wort": "sam"}
    assert _antippen(seite, "b1_voz", "sam", 1)[1] == {"gespielt": ["w1359.mp3"] * 2, "wort": "sam"}
    for nr in range(3):                                   # jucer: dreimal "bin"
        assert _antippen(seite, "jucer", "sam", nr)[1]["gespielt"] == ["w10059.mp3"] * 2, nr
    # "Mi smo dobro" in pismo ist "wir", "Nana mi je pokazala" in jucer "mir"
    assert _antippen(seite, "pismo", "Mi", 0)[1]["gespielt"] == ["w10078.mp3"] * 2
    assert _antippen(seite, "jucer", "mi", 0)[1]["gespielt"] == ["w10060.mp3"] * 2
    # Fehlt die Aufnahme einer Bedeutung, spielt diese Stelle wie bisher
    seite.js(MITSCHREIBEN, {k: d for k, d in NEU.items() if k != "mi (wir)"})
    assert _antippen(seite, "pismo", "Mi", 0)[1]["gespielt"] == ["w1370.mp3"] * 2
    assert seite.fehler == []


LERNEN = """async (id) => {
  const w = CATEGORIES.flatMap(c => c.words).find(x => x.id === id);
  if(!w) throw new Error('kein Wort ' + id);
  openLevel(0); startLesson();
  Lx.queue = [{typ: 'intro', w}]; Lx.i = 0; Lx.total = 1; Lx.results = []; Lx.right = 0;
  showLessonTask();
  window.__gespielt = [];
  document.querySelector('#lBody #xListen').click();
  const ende = Date.now() + 3000;
  while(!window.__gespielt.length && Date.now() < ende) await new Promise(r => setTimeout(r, 15));
  return {ton: w.ton || null, gespielt: window.__gespielt[0] || null, vorladen: aufgabeText({typ: 'intro', w})};
}"""


def test_vokabel_dug_als_lang_und_als_schulden(seite, heute_stand):
    """lang:dug und schulden:dug haben je einen eigenen Ton. Ohne die Aufnahmen sprechen
    beide w1009 wie bisher, mit ihnen jede ihre eigene, und fehlt nur eine, bleibt diese
    bei w1009."""
    seite.starten(stand=heute_stand())
    seite.js(MITSCHREIBEN, {})
    assert seite.js(LERNEN, "lang:dug") == {"ton": "dug (lang)", "gespielt": "w1009.mp3", "vorladen": "dug"}
    assert seite.js(LERNEN, "schulden:dug") == {"ton": "dug (schulden)", "gespielt": "w1009.mp3",
                                                "vorladen": "dug"}
    seite.js(MITSCHREIBEN, NEU)
    assert seite.js(LERNEN, "lang:dug") == {"ton": "dug (lang)", "gespielt": "w10063.mp3",
                                                    "vorladen": "dug (lang)"}
    assert seite.js(LERNEN, "schulden:dug") == {"ton": "dug (schulden)", "gespielt": "w10081.mp3",
                                                "vorladen": "dug (schulden)"}
    seite.js(MITSCHREIBEN, {k: d for k, d in NEU.items() if k != "dug (schulden)"})
    assert seite.js(LERNEN, "schulden:dug") == {"ton": "dug (schulden)", "gespielt": "w1009.mp3",
                                                "vorladen": "dug"}
    assert seite.fehler == []


GRAMMATIK = """async () => {
  const g = GRAMMAR.faelle3.uebungen[4];
  openLevel(0); startLesson();
  Lx.queue = [{typ: 'gram', g}]; Lx.i = 0; Lx.total = 1; Lx.results = []; Lx.right = 0;
  showLessonTask();
  window.__gespielt = [];
  const knopf = [...document.querySelectorAll('#lBody #xOpts .opt')].find(b => b.textContent === g.richtig);
  knopf.click();
  const ende = Date.now() + 3000;
  while(!window.__gespielt.length && Date.now() < ende) await new Promise(r => setTimeout(r, 15));
  return {richtig: g.richtig, ton: g.ton, gespielt: window.__gespielt[0] || null};
}"""


def test_grammatik_mi_als_mir(seite, heute_stand):
    """„Hladno ___ je.“ (Mir ist kalt.): nach der Antwort "mi" als "mir"."""
    seite.starten(stand=heute_stand())
    seite.js(MITSCHREIBEN, {})
    assert seite.js(GRAMMATIK) == {"richtig": "mi", "ton": "mi (mir)", "gespielt": "w1370.mp3"}
    seite.js(MITSCHREIBEN, NEU)
    assert seite.js(GRAMMATIK) == {"richtig": "mi", "ton": "mi (mir)", "gespielt": "w10060.mp3"}
    assert seite.fehler == []


WORTLISTE = """([level, bs]) => {
  const i = CATEGORIES.findIndex(c => c.id === level);
  catIdx = i; cur().words.forEach(w => known.add(w.id)); openLevel(i);
  window.__gespielt = [];
  const zeile = [...document.querySelectorAll('#wordList > div')].find(z => z.querySelector('.bs').textContent === bs);
  if(!zeile) return null;
  zeile.querySelector('.wortton').click();
  return window.__gespielt.slice();
}"""


def test_wortliste_satzwort_und_vokabel(seite, heute_stand):
    """"Wörter dieses Levels": "sam" aus „Izgubio sam ključeve.“ hat die Bedeutung aus dem
    Woerterbuch ("bin") und damit auch dessen Ton; die Vokabel dug im Level lang_kurz
    ihren eigenen. Ohne die neuen Aufnahmen wie bisher."""
    seite.starten(stand=heute_stand())
    seite.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
    seite.js(MITSCHREIBEN, {})
    assert seite.js(WORTLISTE, ["geben_nehmen", "sam"]) == ["w1359.mp3"]
    assert seite.js(WORTLISTE, ["lang_kurz", "dug"]) == ["w1009.mp3"]
    seite.js(MITSCHREIBEN, NEU)
    assert seite.js(WORTLISTE, ["geben_nehmen", "sam"]) == ["w10059.mp3"]
    assert seite.js(WORTLISTE, ["lang_kurz", "dug"]) == ["w10063.mp3"]
    assert seite.js(WORTLISTE, ["bank", "dug"]) == ["w10081.mp3"]
    assert seite.fehler == []


def test_wortliste_satzwort_mit_anderer_bedeutung(seite, heute_stand):
    """"Wörter dieses Levels": In „Sam izdržava cijelu porodicu.“ (allein) und „Babo je sam
    sastavio ormar.“ (selbst) bleibt "sam" bei w1359, auch wenn es "sam (bin)" gibt; in
    „Nana ima dijabetes, ne smije jesti slatko.“ spielt "smije" darf, nicht lacht
    (satzwort_ton, ton_bedeutung.json "saetze"). Ohne die neuen Aufnahmen wie bisher."""
    seite.starten(stand=heute_stand())
    seite.js("() => { const v = document.getElementById('vorspann'); if(v) v.click(); }")
    seite.js(MITSCHREIBEN, {})
    assert seite.js(WORTLISTE, ["durchfuehren_schaffen", "Sam"]) == ["w1359.mp3"]
    assert seite.js(WORTLISTE, ["krank_sein", "smije"]) == ["w1264.mp3"]
    seite.js(MITSCHREIBEN, NEU)
    assert seite.js(WORTLISTE, ["durchfuehren_schaffen", "Sam"]) == ["w1359.mp3"]
    assert seite.js(WORTLISTE, ["bauen_einbauen", "sam"]) == ["w1359.mp3"]
    assert seite.js(WORTLISTE, ["krank_sein", "smije"]) == ["w10071.mp3"]
    assert seite.js(WORTLISTE, ["unfaelle_pannen", "smije"]) == ["w10071.mp3"]
    seite.js(MITSCHREIBEN, {k: d for k, d in NEU.items() if k != "smije (darf)"})
    assert seite.js(WORTLISTE, ["krank_sein", "smije"]) == ["w1264.mp3"]
    assert seite.fehler == []
