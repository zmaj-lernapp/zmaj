# -*- coding: utf-8 -*-
"""Die Tonspur: jedes Wort, jeder Satz und jede Geschichte hat eine Aufnahme."""
import io
import json
import os
import re
import shutil
import subprocess

import pytest


@pytest.fixture(scope="module")
def index(wurzel):
    return json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"), encoding="utf-8"))


def test_ton_pruefen_meldet_nichts(wurzel):
    import ton_pruefen
    assert ton_pruefen.main() in (0, None)


def test_nur_erste_form_nur_fuer_echte_mehrfachformen(index):
    """ton_pruefen.NUR_ERSTE_FORM laesst eine fehlende Aufnahme mit allen
    Formen durch (22.10.2026, "so / sol" - die neue Aufnahme kostet Geld,
    Ajdin entscheidet spaeter). Das darf nur fuer ein Wort mit mehreren
    Formen gelten, dessen erste Form klingt; sonst verdeckte die Ausnahme
    ein stummes Wort."""
    import ton_bauen
    import ton_pruefen
    alle = {p["key"]: p["text"] for p in ton_bauen.sammle() if p.get("alle")}
    haben = {e["key"] for e in index["toene"]}
    for k in ton_pruefen.NUR_ERSTE_FORM:
        assert k in alle, "kein Wort mit mehreren Formen: %r" % k
        assert ton_bauen.schluessel(alle[k]) in haben, "auch die erste Form fehlt: %r" % k


def test_jede_datei_im_index_existiert_und_ist_nicht_leer(index, wurzel):
    fehlt, leer = [], []
    for e in index["toene"]:
        pfad = os.path.join(wurzel, "web", "audio", e["datei"])
        if not os.path.exists(pfad):
            fehlt.append(e["datei"])
        elif os.path.getsize(pfad) < 800:
            leer.append(e["datei"])
    assert not fehlt, fehlt[:20]
    assert not leer, leer[:20]


def test_jedes_wort_findet_seine_aufnahme(grunddaten, index):
    """In der App aus dem Store: web/audio und dazu, was es nur von Emir
    gibt (ton_nur_emir.json, 23.10.2026). Die Web-Demo bleibt fuer diese
    Woerter stumm - so entschieden."""
    import daten_exportieren as de
    import ton_bauen
    toene = {str(e["key"]).lower(): e["datei"]
             for e in index["toene"] + list(ton_bauen.nur_emir().values())}
    ohne = [w["bs"] for k in grunddaten["kategorien"] for w in k["words"]
            if not de.ton_datei(w["bs"], toene)]
    assert not ohne, ohne[:20]


def test_stimmen_sind_dokumentiert(index):
    """data/DATASHEET.md nennt die Stimmen. Kommt eine dazu, muss sie dort
    stehen - wer die Tonspur weitergibt, muss sagen können, woher sie ist."""
    stimmen = {e.get("stimme") for e in index["toene"]}
    assert stimmen <= {"bs-BA-GoranNeural", "bs-BA-VesnaNeural", "hr-HR-SreckoNeural"}, stimmen


# Der Tonweg (05.11.2026): auf Ajdins S21 blieb der AudioContext mit
# Standard-Latenz stumm, ohne Fehler; mit latencyHint 'playback' klang er.
# Die App baut ihren Kontext deshalb nur noch in tonKontext().
def test_audiocontext_entsteht_nur_in_tonkontext(index_html):
    """Bis zum 05.11.2026 gab es zwei Stellen (sound() und tonKontext()). Eine
    zweite, die den Kontext selbst baut, kaeme wieder ohne die Option."""
    assert not re.findall(r"new\s*\(?\s*(?:window\.)?(?:webkit)?AudioContext\b", index_html)
    m = re.search(r"^function tonKontext\(\)\{.*?^\}", index_html, re.S | re.M)
    assert m, "tonKontext() nicht gefunden"
    assert index_html.count("new Kontext(") == m.group(0).count("new Kontext(") == 2
    ton = index_html[index_html.index("function sound(kind){"):index_html.index("function wireSwitch(")]
    assert "tonKontext()" in ton


# Laeuft die echte Funktion aus index.html mit erfundenen Geraeten.
TONKONTEXT_PROBE = r"""
const quelle = process.argv[1];
const aufrufe = [];
const geraet = (name, wirft) => class {
  constructor(...a){ aufrufe.push([name, ...a]); if(wirft(a)) throw new TypeError('nein'); this.name = name; }
};
const fall = fenster => {
  aufrufe.length = 0;
  const t = new Function('window', 'let actx = null;\n' + quelle + '\nreturn {tonKontext, lies: () => actx};')(fenster);
  const eins = t.tonKontext(), bis_hier = aufrufe.slice(), zwei = t.tonKontext();
  return {aufrufe: bis_hier, name: eins ? eins.name : null, derselbe: eins === zwei, gemerkt: t.lies() === eins};
};
console.log(JSON.stringify({
  neu: fall({AudioContext: geraet('neu', () => false), webkitAudioContext: geraet('alt', () => false)}),
  alt: fall({webkitAudioContext: geraet('alt', () => false)}),
  wirft_bei_option: fall({AudioContext: geraet('neu', a => a.length > 0)}),
  wirft_immer: fall({AudioContext: geraet('neu', () => true)}),
  keiner: fall({}),
}));
"""


def test_tonkontext_nimmt_playback_und_faellt_zurueck(index_html):
    """Immer zuerst mit 'playback'. Wirft das Geraet dabei, ohne Option; geht
    auch das nicht oder gibt es gar keinen AudioContext, kommt null (dann
    spricht der spieler) und kein Fehler. Einmal gebaut, bleibt es derselbe:
    Ton und Wort muessen auf einer Uhr laufen."""
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    quelle = re.search(r"^function tonKontext\(\)\{.*?^\}", index_html, re.S | re.M).group(0)
    aus = subprocess.run(["node", "-e", TONKONTEXT_PROBE, quelle],
                         capture_output=True, text=True, check=True).stdout
    r = json.loads(aus)
    option = {"latencyHint": "playback"}
    assert r["neu"] == {"aufrufe": [["neu", option]], "name": "neu", "derselbe": True, "gemerkt": True}
    assert r["alt"] == {"aufrufe": [["alt", option]], "name": "alt", "derselbe": True, "gemerkt": True}
    assert r["wirft_bei_option"] == {"aufrufe": [["neu", option], ["neu"]], "name": "neu",
                                     "derselbe": True, "gemerkt": True}
    assert r["wirft_immer"]["aufrufe"] == [["neu", option], ["neu"]]
    assert r["wirft_immer"]["name"] is None
    assert r["keiner"] == {"aufrufe": [], "name": None, "derselbe": True, "gemerkt": True}
