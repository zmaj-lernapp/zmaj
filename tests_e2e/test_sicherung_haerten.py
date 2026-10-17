# -*- coding: utf-8 -*-
"""Eine Sicherungsdatei verschenkt nichts mehr - am Handy-Datum festgemacht.

Die Sicherheitspruefung vom 17.10.2026 hat in Chrome gemessen: eine Datei
mit tage:["1990-01-01"] einlesen, dann 1980, dann 1970 - jedes Mal fuenf
Tage Vollversion, geschenk.jahr 36 -> 46 -> 56. Dazu Muenzen ohne Grenze
(muenzen_ges 1e999 = Infinity). Ajdin dazu: "binde es am Handy-Datum".

Seitdem gilt beim Einlesen (sicherungPlausibel in index.html): Lerntage
und Schutztage nur von APP_START bis heute, Muenzen nur so viele, wie sich
mit diesen Lerntagen verdienen lassen (60 je Tag, ein Tag Vorschuss), das
Geschenkjahr nie ueber den Jahren seit APP_START. Eine echte Sicherung
kommt vollstaendig an - das prueft der Test dazu genauso.

Fuer das Jahresgeschenk muss mehr als ein Jahr seit APP_START vergangen
sein. Das ist heute noch nicht so, deshalb stellt der Test die Uhr des
Browsers vor (page.clock.set_fixed_time - Date.now steht, Zeitgeber laufen).

Dazu zwei Kleinigkeiten vom selben Tag: die Geschlechtsfrage der Grammatik
spricht ihre deutsche Antwort nicht mehr mit bosnischer Stimme, und im
tuerkischen Menue bleibt der bosnische Antwortknopf "Sarajevo" bosnisch.
"""
import datetime
import io
import json
import os
import re

import pytest

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with io.open(os.path.join(WURZEL, "web", "index.html"), encoding="utf-8") as _f:
    APP_START = datetime.date.fromisoformat(
        re.search(r"const APP_START = '(\d{4}-\d{2}-\d{2})';", _f.read()).group(1))

# Alles, was nach dem Einlesen zaehlt, in einem Blick.
ZUSTAND = """() => ({
    notiz: document.getElementById('sichNote').textContent,
    tage: [...days].sort(), frost: [...frost].sort(), rekord,
    ges: muenzenGes, aus: muenzenAus, muenzen: muenzen(),
    endlich: Number.isFinite(muenzenGes) && Number.isFinite(muenzenAus),
    besitz: [...besitz].sort(), getragen, woerter: known.size, bestanden: [...passed].sort(),
    leben: lives.anzahl,
    jahr: geschenk.jahr || 0, bis: geschenk.bis || 0, laeuft: geschenkLaeuft(), unbegrenzt: unlimited(),
    seit: localStorage.getItem('zmaj_seit'), max: geschenkJahreMax(),
    start: APP_START, heute: today(), jetzt: Date.now()})"""

# frage() oeffnet sonst das Ja/Nein-Fenster und wartet auf einen Finger.
EINLESEN = """async (text) => {
    frage = async () => true;
    await sicherungEinlesen(new File([text], 'sicherung.json', {type: 'application/json'}));
    return (%s)();
}""" % ZUSTAND


def _datei(stand, **ersetzen):
    """Die Sicherungsdatei als Text. ersetzen setzt Zahlen ein, die json.dumps
    nicht schreiben kann - 1e999 liest JSON.parse als Infinity."""
    text = json.dumps({"app": "zmaj", "version": 1, "stand": stand})
    for platzhalter, roh in ersetzen.items():
        text = text.replace('"%s"' % platzhalter, roh)
    return text


def _tage(von, bis, ohne=()):
    n = (bis - von).days
    return [(von + datetime.timedelta(days=i)).isoformat() for i in range(n + 1)
            if (von + datetime.timedelta(days=i)) not in ohne]


def _heute(seite):
    return datetime.date.fromisoformat(seite.js("() => today()"))


def _echte_sicherung(seite, heute, **mehr):
    """Ein Lernstand, wie ihn ein fleissiger Lernender wirklich hat: jeden
    Tag von APP_START bis heute gelernt, bis auf zwei Tage, die ein
    Serienschutz gerettet hat; 28 Muenzen am Tag (30 sind das Hoechste),
    Hut und Lesebrille gekauft und getragen, drei Herzen."""
    luecken = (APP_START + datetime.timedelta(days=10), APP_START + datetime.timedelta(days=20))
    tage = _tage(APP_START, heute, ohne=luecken)
    woerter = seite.js("() => CATEGORIES[0].words.slice(0, 20).map(w => w.id)")
    stand = {
        "gewusst": woerter, "bestanden": [seite.js("() => CATEGORIES[0].id")],
        "tage": tage, "frost": [d.isoformat() for d in luecken],
        "muenzen_ges": 28 * len(tage), "muenzen_aus": 1500 + 400,
        "besitz": ["hut", "lesebrille"], "getragen": "hut,lesebrille",
        "leben": {"anzahl": 3, "zeit": seite.js("() => Date.now()")},
        "gefeiert": [], "geschenk_jahr": 0,
    }
    stand.update(mehr)
    return stand


def test_alte_lerntage_bringen_kein_geschenk(seite, heute_stand):
    """Der gemessene Angriff, nacheinander: 1990, 1980, 1970. Vorher jedes
    Mal fuenf Tage Vollversion, jetzt nie - auch nicht nach dem Neuladen."""
    seite.starten(stand=heute_stand())
    heute = _heute(seite)
    for jahr in (1990, 1980, 1970):
        z = seite.js(EINLESEN, _datei({"tage": ["%d-01-01" % jahr, heute.isoformat()],
                                       "frost": ["%d-01-02" % jahr], "geschenk_jahr": 9999}))
        assert z["tage"] == [heute.isoformat()], z["tage"]
        assert z["frost"] == []
        assert not z["laeuft"] and not z["unbegrenzt"], "Geschenk aus %d" % jahr
        assert z["jahr"] == 0, "geschenk.jahr erhoeht: %r" % z["jahr"]
        assert z["start"] <= z["seit"] <= z["heute"], z["seit"]
        assert z["notiz"].startswith("Eingelesen"), z["notiz"]
    seite.neu_laden()
    z = seite.js(ZUSTAND)
    assert not z["laeuft"] and not z["unbegrenzt"] and z["jahr"] == 0
    assert seite.fehler == []


def test_gefaelschter_stand_im_speicher_wird_zurechtgerueckt(seite, heute_stand):
    """Wer die Luecke vor dem Update genutzt hat, hat zmaj_seit = 1970 und
    geschenk.jahr = 56 schon im Geraetespeicher. Beim naechsten Start endet
    das Geschenk, zmaj_seit wird berichtigt. Das Jahr 56 bleibt bewusst
    stehen (17.10.2026): zurueckgeschrieben wird nichts, sonst gaebe es das
    Geschenk mit der Uhr beliebig oft - die 56 sperrt nur weitere Geschenke
    auf diesem Geraet."""
    seite.page.goto(seite.basis + "/leer")
    seite.js("""(stand) => {
        localStorage.clear();
        localStorage.setItem('zmaj_stand', JSON.stringify(stand));
        localStorage.setItem('zmaj_seit', '1970-01-01');
        localStorage.setItem('zmaj_geschenk', JSON.stringify({jahr: 56, bis: Date.now() + 4 * 86400000}));
        localStorage.setItem('zmaj_einwilligung', JSON.stringify({wahl:'nein', stand:1, zeit:new Date().toISOString()}));
        localStorage.setItem('zmaj_sprache', 'de');
    }""", heute_stand(tage=["1970-01-01", "1980-01-01"]))
    seite.starten(leeren=False)
    z = seite.js(ZUSTAND)
    assert not z["laeuft"] and not z["unbegrenzt"], z
    assert z["tage"] == []
    assert z["start"] <= z["seit"] <= z["heute"], z["seit"]
    # Auch ein ausdruecklicher Aufruf gibt kein neues Geschenk.
    assert seite.js("() => { geschenkPruefen(); return geschenkLaeuft() || unlimited(); }") is False
    gespeichert = seite.js("() => JSON.parse(localStorage.getItem('zmaj_geschenk'))")
    assert gespeichert["jahr"] == 56, gespeichert
    assert seite.fehler == []


def test_lerntage_in_der_zukunft_fallen_raus(seite, heute_stand):
    seite.starten(stand=heute_stand())
    heute = _heute(seite)
    morgen = (heute + datetime.timedelta(days=1)).isoformat()
    gestern = (heute - datetime.timedelta(days=1)).isoformat()
    z = seite.js(EINLESEN, _datei({"tage": [gestern, heute.isoformat(), morgen, "2099-01-01"],
                                   "frost": [morgen, "2099-01-02"]}))
    assert z["tage"] == [gestern, heute.isoformat()]
    assert z["frost"] == []
    assert not z["laeuft"]
    assert seite.fehler == []


# 1e999 liest JSON.parse als Infinity - keine endliche Zahl, also 0.
# 1e9 ist endlich und wird auf die Grenze gekuerzt: ein Lerntag, 60 je
# Lerntag und ein Tag Vorschuss = 120.
@pytest.mark.parametrize("roh, erwartet", [("1e999", 0), ("1e9", 120)])
def test_muenzen_aus_der_datei_sind_begrenzt(seite, heute_stand, roh, erwartet):
    """Ausgegeben nie mehr als verdient, nichts unter null."""
    seite.starten(stand=heute_stand())
    heute = _heute(seite).isoformat()
    z = seite.js(EINLESEN, _datei({"tage": [heute], "muenzen_ges": "GES", "muenzen_aus": "AUS"},
                                  GES=roh, AUS=roh))
    assert z["endlich"], z
    assert z["ges"] == erwartet and z["aus"] == erwartet and z["muenzen"] == 0, z
    z = seite.js(EINLESEN, _datei({"tage": [heute], "muenzen_ges": "GES", "muenzen_aus": -5}, GES=roh))
    assert z["ges"] == erwartet and z["aus"] == 0 and z["muenzen"] == erwartet, z
    # Ohne Lerntage gibt es nur den Vorschuss.
    z = seite.js(EINLESEN, _datei({"muenzen_ges": 5000, "muenzen_aus": 100}))
    assert z["ges"] == 60 and z["aus"] == 60 and z["muenzen"] == 0, z
    z = seite.js(EINLESEN, _datei({"tage": [heute], "muenzen_ges": "GES"}, GES=roh))
    seite.neu_laden()
    z = seite.js(ZUSTAND)
    assert z["endlich"] and z["ges"] == erwartet and z["muenzen"] == erwartet, z
    assert seite.fehler == []


def test_echte_sicherung_bleibt_vollstaendig_erhalten(seite, heute_stand):
    """Lerntage von APP_START bis heute, Muenzen in echter Hoehe, Gekauftes
    und Getragenes, Fortschritt, Herzen: alles kommt an, der Muenzstand ist
    derselbe - auch nach dem Neuladen."""
    seite.starten(stand=heute_stand())
    heute = _heute(seite)
    stand = _echte_sicherung(seite, heute)
    z = seite.js(EINLESEN, _datei(stand))
    for zz in (z, None):
        if zz is None:
            seite.neu_laden()
            zz = seite.js(ZUSTAND)
        assert zz["tage"] == sorted(stand["tage"])
        assert zz["frost"] == sorted(stand["frost"])
        assert zz["ges"] == stand["muenzen_ges"] and zz["aus"] == stand["muenzen_aus"]
        assert zz["muenzen"] == stand["muenzen_ges"] - stand["muenzen_aus"]
        assert zz["besitz"] == ["hut", "lesebrille"]
        assert zz["getragen"] == "hut,lesebrille"
        assert zz["woerter"] == 20 and zz["bestanden"] == stand["bestanden"]
        assert zz["leben"] == 3
        assert zz["seit"] == APP_START.isoformat()
        assert not zz["laeuft"]
    assert z["notiz"].startswith("Eingelesen"), z["notiz"]
    assert seite.fehler == []


def test_besitz_nur_so_viel_wie_die_muenzen_bezahlen(seite, heute_stand):
    """Der ganze Laden plus ein Vollversions-Stueck und eine erfundene
    Kennung in der Datei, aber nur 10 Lerntage: es bleibt nur, was die
    gekappten Muenzen bezahlen, das Billigste zuerst; ausgegeben ist
    mindestens die Summe der behaltenen Preise. Der Rekord ist hoechstens
    die Zahl der Lerntage. Beides auch nach dem Neuladen (18.10.2026,
    nachgezogen aus der Code-Pruefung)."""
    seite.starten(stand=heute_stand())
    heute = _heute(seite)
    tage = [(heute - datetime.timedelta(days=i)).isoformat() for i in range(10)]
    laden = seite.js("() => ZIERRAT.filter(w => !w.voll && w.preis > 0).map(w => [w.id, w.preis])")
    preise = dict(laden)
    grenze = 60 * (len(tage) + 1)
    behalten, summe = [], 0
    for kennung, preis in sorted(laden, key=lambda x: x[1]):
        if summe + preis > grenze:
            break
        behalten.append(kennung)
        summe += preis
    assert behalten, "Testannahme: das billigste Stueck kostet hoechstens %d" % grenze
    besitz = [k for k, _ in laden] + ["krone_gross", "gibtsnicht", "HUT"]
    z = seite.js(EINLESEN, _datei({"tage": tage, "muenzen_ges": 5000, "muenzen_aus": 0,
                                   "besitz": besitz, "rekord": "REK"}, REK="1e9"))
    for zz in (z, None):
        if zz is None:
            seite.neu_laden()
            zz = seite.js(ZUSTAND)
        assert zz["ges"] == grenze, zz
        assert zz["besitz"] == sorted(behalten), zz["besitz"]
        assert zz["aus"] == sum(preise[k] for k in behalten), zz
        assert zz["muenzen"] == grenze - zz["aus"] >= 0
        assert zz["rekord"] == len(tage), zz["rekord"]
    assert seite.fehler == []

def test_geschenk_nach_einem_jahr_genau_einmal(seite, heute_stand):
    """Uhr auf APP_START + 1 Jahr + 2 Tage: eine echte Sicherung ab APP_START
    bringt genau ein Geschenk. Nochmal einlesen, die alten Angriffsdateien,
    ein Geschenkjahr 5 aus der Datei - nichts davon gibt ein zweites, und
    das laufende bleibt, wie es ist. Nach dem Ablauf im selben Jahr auch
    keins."""
    jetzt = datetime.datetime.combine(APP_START + datetime.timedelta(days=367), datetime.time(12, 0))
    seite.page.clock.set_fixed_time(jetzt)
    seite.starten(stand=heute_stand())
    heute = _heute(seite)
    assert heute == jetzt.date()
    datei = _datei(_echte_sicherung(seite, heute))
    z = seite.js(EINLESEN, datei)
    assert z["max"] == 1
    assert z["jahr"] == 1 and z["laeuft"] and z["unbegrenzt"], z
    bis = z["bis"]
    assert bis == z["jetzt"] + 5 * 86400000

    for text in (datei,
                 _datei({"tage": ["1970-01-01"]}),
                 _datei(_echte_sicherung(seite, heute, geschenk_jahr=5))):
        z = seite.js(EINLESEN, text)
        assert z["jahr"] == 1 and z["bis"] == bis and z["laeuft"], z

    seite.neu_laden()
    z = seite.js(ZUSTAND)
    assert z["jahr"] == 1 and z["bis"] == bis and z["laeuft"]

    # Zehn Tage spaeter: abgelaufen, und im selben Jahr kommt keins nach.
    seite.page.clock.set_fixed_time(jetzt + datetime.timedelta(days=10))
    assert seite.js("() => geschenkPruefen()") == 0
    z = seite.js(EINLESEN, _datei({"tage": ["1970-01-01", APP_START.isoformat()]}))
    assert z["jahr"] == 1 and not z["laeuft"] and not z["unbegrenzt"], z
    assert seite.fehler == []


def test_erhaltenes_geschenk_reist_mit(seite, heute_stand):
    """Auf einem neuen Handy: die Sicherung sagt, das Geschenk des ersten
    Jahres gab es schon. Dann kommt es nicht noch einmal."""
    jetzt = datetime.datetime.combine(APP_START + datetime.timedelta(days=367), datetime.time(12, 0))
    seite.page.clock.set_fixed_time(jetzt)
    seite.starten(stand=heute_stand())
    z = seite.js(EINLESEN, _datei(_echte_sicherung(seite, _heute(seite), geschenk_jahr=1)))
    assert z["jahr"] == 1 and not z["laeuft"] and not z["unbegrenzt"], z
    assert seite.fehler == []


# Eine Grammatikaufgabe allein in die Lektion legen - die erste, deren
# richtige Antwort `antwort` ist (gesucht im geladenen Inhalt). Danach
# wird jedes Vorlesen mitgeschrieben statt gesprochen. pickVoice() liefert
# eine bosnische Stimme, damit vorlesbar() wie auf einem Handy mit Stimme
# ja sagt - im Testbrowser gibt es keine, und dann kaeme der Fehler nie.
GRAM_AUFGABE = """(antwort) => {
    openLevel(0); startLesson();
    const g = Object.values(GRAMMAR).flatMap(l => l.uebungen || []).find(u => u.richtig === antwort);
    if(!g) return null;
    Lx.queue = [{typ: 'gram', g}]; Lx.i = 0; Lx.total = 1;
    showLessonTask();
    window.gesprochen = [];
    pickVoice = () => ({lang: 'bs-BA', name: 'Probe', voiceURI: 'Probe'});
    spaeterSprechen = text => window.gesprochen.push(text);
    speechSynthesis.speak = u => window.gesprochen.push('stimme: ' + u.text);
    return {frage: g.frage, richtig: g.richtig,
            knoepfe: [...document.querySelectorAll('#lBody .opt')].map(b => ({text: b.textContent, lang: b.getAttribute('lang')}))};
}"""


def test_geschlechtsfrage_spricht_nichts_deutsches(seite, heute_stand):
    """"weiblich (ona)" ist Deutsch mit einem bosnischen Fuerwort - die
    bosnische Stimme liest es nicht vor. Die Gegenprobe "moja" schon, sonst
    wuerde der Test auch dann nichts finden, wenn er gar nicht mithoert."""
    seite.starten(stand=heute_stand())
    g = seite.js(GRAM_AUFGABE, "weiblich (ona)")
    assert g, "keine Geschlechtsaufgabe im Inhalt"
    seite.page.locator("#lBody .opt").first.click()
    seite.page.wait_for_timeout(600)
    assert seite.js("() => window.gesprochen") == []

    g = seite.js(GRAM_AUFGABE, "moja")
    assert g, "keine Aufgabe mit der Antwort moja"
    seite.page.locator("#lBody .opt").first.click()
    assert seite.js("() => window.gesprochen") == ["moja"]
    assert seite.fehler == []


def test_tuerkisch_faelle3_zeigt_bosnische_knoepfe(seite, heute_stand):
    """"Stanujem u ___." - die Knoepfe sind bosnisch, auch "Sarajevo"; die
    Bedeutung in Klammern ist tuerkisch und sagt "Saraybosna"."""
    seite.starten(sprache="tr", stand=heute_stand())
    assert seite.js("() => document.documentElement.lang") == "tr"
    g = seite.js(GRAM_AUFGABE, "Sarajevu")
    assert g, "keine Aufgabe mit der Antwort Sarajevu"
    assert sorted(k["text"] for k in g["knoepfe"]) == ["Sarajeva", "Sarajevo", "Sarajevu"], g
    assert {k["lang"] for k in g["knoepfe"]} == {"bs"}
    assert "Saraybosna" in g["frage"], g["frage"]
    assert seite.fehler == []
