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


def test_ton_pruefen_meldet_nichts(wurzel, monkeypatch):
    """Seit dem 07.11.2026 ohne die Schluessel aus tests/offen_p1020.json: Emirs Ton fuer
    die Pakete 10 bis 20 kommt im eigenen Schritt. Alles andere muss vollstaendig sein."""
    import offen_p1020
    import ton_bauen
    import ton_pruefen
    echt = ton_bauen.sammle
    monkeypatch.setattr(ton_bauen, "sammle", lambda: [p for p in echt() if p["key"] not in offen_p1020.TON])
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
    import offen_p1020
    ohne = [w["bs"] for k in grunddaten["kategorien"] for w in k["words"]
            if not de.ton_datei(w["bs"], toene)
            and ton_bauen.schluessel(w["bs"]) not in offen_p1020.TON]      # Ton-Schritt, 07.11.2026
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


# Das Tempo (05.11.2026): bei Ajdins Frau stand es aus einer Geschichte auf
# 0,75x, und der Sprecher war dadurch in allen Lektionen langsam. Es gilt jetzt
# nur noch beim Vorlesen einer Geschichte.
def test_tempo_liest_nur_das_vorlesen_der_geschichte(index_html):
    """Bis zum 05.11.2026 las spieleDatei() den Wert selbst, und pufferLaden(),
    pufferSpielen() und woerterVorladen() schalteten bei tempo !== 1 den
    schnellen Weg ab. Jede neue Stelle, die ihn liest, braechte das zurueck."""
    skript = re.sub(r"/\*.*?\*/", "", index_html, flags=re.S)
    zeilen = [z.strip() for z in skript.splitlines()
              if re.search(r"(?<![\w.\-'\"])tempo\b(?![\w'\"-])", z.split("//")[0])]
    verwaltung = ("let tempo = 1;", "tempo = gemerkt;", "tempo = v;", "(v===tempo)")
    rest = [z for z in zeilen if not any(x in z for x in verwaltung)]
    assert len(zeilen) == len(verwaltung) + 1, zeilen
    assert len(rest) == 1 and rest[0].startswith("sprichMitSpieler(s.text,") and rest[0].endswith(", tempo);"), rest


# Laeuft die echten Funktionen aus index.html mit erfundenem spieler und
# erfundener Computerstimme. Im Skript steht tempo auf 0,75 wie bei dem Fund.
TEMPO_PROBE = r"""
const quelle = process.argv[1];
const bau = (datei, spielt) => new Function('datei', 'spielt', `
  let tempo = 0.75, pausiert = false, vorwaermen = null, tonMarke = 0, laeuftVor = null;
  const hasTTS = true, raten = [];
  const spieler = {playbackRate: 1, muted: false, currentTime: 0, pause(){}, play(){ return spielt(); }};
  const waStopp = () => {}, fuerStimme = t => t, pickVoice = () => null, audioDatei = () => datei;
  class SpeechSynthesisUtterance { constructor(t){ this.text = t; } }
  const speechSynthesis = {cancel(){}, speak(u){ raten.push(u.rate); }};
  const localStorage = {setItem(){}};
  const document = {querySelectorAll: () => []};
  ${quelle}
  return {spieler, raten, sprichMitSpieler, setzeTempo, liest: v => { laeuftVor = v; }};
`)(datei, spielt);
const ruhe = () => new Promise(r => setTimeout(r));
(async () => {
  const a = bau('x.mp3', () => Promise.resolve()), rate = () => a.spieler.playbackRate, aus = {};
  a.sprichMitSpieler('wort');                   aus.wort = rate();
  a.sprichMitSpieler('geschichte', null, 0.75); aus.geschichte = rate();
  a.sprichMitSpieler('wort');                   aus.danach = rate();
  a.setzeTempo(0.5);                            aus.wort_bleibt = rate();
  a.liest(() => {});
  a.sprichMitSpieler('geschichte', null, 0.5);  aus.neu = rate();
  a.setzeTempo(1.25);                           aus.mitten = rate();
  const b = bau(null, () => Promise.resolve());
  b.sprichMitSpieler('wort'); b.sprichMitSpieler('geschichte', null, 0.75);
  aus.ohne_aufnahme = b.raten;
  const c = bau('x.mp3', () => Promise.reject(new Error('kaputt')));
  c.sprichMitSpieler('wort'); c.sprichMitSpieler('geschichte', null, 0.75);
  await ruhe();
  aus.datei_faellt_aus = c.raten;
  console.log(JSON.stringify(aus));
})();
"""


def test_tempo_nur_wenn_es_mitgegeben_wird(index_html):
    """Ohne mitgegebenes Tempo immer 1, im spieler wie in der Computerstimme
    (Grundgeschwindigkeit 0,85), auch wenn die Datei ausfaellt. Der spieler
    bleibt nicht auf dem Tempo der Geschichte haengen. setzeTempo() aendert
    einen laufenden Ton nur, wenn gerade vorgelesen wird."""
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    quelle = "\n".join(re.search(r"^function %s\(.*?^\}" % name, index_html, re.S | re.M).group(0)
                       for name in ("spieleDatei", "setzeTempo", "sprichMitStimme", "sprichMitSpieler"))
    aus = subprocess.run(["node", "-e", TEMPO_PROBE, quelle], capture_output=True, text=True, check=True).stdout
    r = json.loads(aus)
    assert r.pop("ohne_aufnahme") == pytest.approx([0.85, 0.6375])
    assert r.pop("datei_faellt_aus") == pytest.approx([0.85, 0.6375])
    assert r == {"wort": 1, "geschichte": 0.75, "danach": 1, "wort_bleibt": 1, "neu": 0.5, "mitten": 1.25}
