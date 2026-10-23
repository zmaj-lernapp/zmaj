# -*- coding: utf-8 -*-
"""Umbenannte Woerter behalten ihren Lernstand (AGENTS.md, Regel 1).

Anlass (22.10.2026), Ajdin: "die vokabel salz am besten zu so/sol aendern
weil man es so oder so sagt". Die Kennung eines Wortes haengt an Bedeutung
UND Wort (inhalt.py) und heisst seitdem "salz:so / sol" statt "salz:so".
Ein alter Stand muss beim Start und beim Einlesen einer Sicherung ueberall
auf die neue Kennung wandern: gewusst, Fehler-Topf und Sterne.

Der Fehler-Topf zog bis dahin gar nicht mit: topfAufraeumen() warf
"w:salz:so" beim naechsten Oeffnen von Wiederholen still weg. Seit
22.10.2026 schreibt topfUmschreiben() ihn um.
"""
import json

ALT, NEU = "salz:so", "salz:so / sol"


def _gespeichert(seite):
    return seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand'))")


def _alter_stand(heute_stand):
    return heute_stand(gewusst=[ALT, "brot:hljeb"],
                       topf={"w:" + ALT: {"typ": "type", "n": 1, "z": 123}},
                       stern={"w:" + ALT: {"z": 50, "r": 7}})


def test_salz_hat_die_neue_kennung(seite, heute_stand):
    seite.starten(stand=heute_stand())
    w = seite.js("""([alt, neu]) => ({alt: !!wortNachId(alt), neu: wortNachId(neu) && wortNachId(neu).w.bs,
                                      umbenannt: UMBENANNT[alt]})""", [ALT, NEU])
    assert w == {"alt": False, "neu": "so / sol", "umbenannt": NEU}
    assert seite.fehler == []


def test_alter_stand_wandert_beim_start(seite, heute_stand):
    seite.starten(stand=_alter_stand(heute_stand))
    jetzt = seite.js("""() => ({known: [...known], topf, stern})""")
    assert NEU in jetzt["known"] and ALT not in jetzt["known"]
    assert "brot:hljeb" in jetzt["known"], "Unbeteiligtes bleibt"
    assert jetzt["topf"] == {"w:" + NEU: {"typ": "type", "n": 1, "z": 123}}
    assert jetzt["stern"] == {"w:" + NEU: {"z": 50, "r": 7}}
    # Gleich gespeichert, nicht erst bei der naechsten Antwort
    d = _gespeichert(seite)
    assert NEU in d["gewusst"] and ALT not in d["gewusst"]
    assert d["topf"] == jetzt["topf"] and d["stern"] == jetzt["stern"]
    # Der Reiter Wiederholen raeumt den Eintrag nicht mehr weg, und aus
    # "type" wird die Auswahl - Woerter mit " / " sind nie Tippaufgaben.
    nach = seite.js("""(k) => { homeMode = 'topf'; showHome();
        const a = topfAufgabe(k, topf[k]);
        return {anzahl: topfAnzahl(), typ: a && a.typ, bs: a && a.w.bs}; }""", "w:" + NEU)
    assert nach == {"anzahl": 1, "typ": "mcrev", "bs": "so / sol"}
    # Neu laden: nichts wandert ein zweites Mal, nichts geht verloren
    seite.neu_laden()
    assert seite.js("() => [known.has('salz:so / sol'), Object.keys(topf), Object.keys(stern)]") == [
        True, ["w:" + NEU], ["w:" + NEU]]
    assert seite.fehler == []


def test_topf_alt_und_neu_zugleich_der_juengere_fehler_gilt(seite, heute_stand):
    for alt_z, neu_z, sieger in ((100, 200, "neu"), (300, 200, "alt")):
        e_alt = {"typ": "mc", "n": 1, "z": alt_z}
        e_neu = {"typ": "listen", "n": 0, "z": neu_z}
        seite.starten(stand=heute_stand(topf={"w:" + ALT: e_alt, "w:" + NEU: e_neu}))
        assert seite.js("() => topf") == {"w:" + NEU: e_alt if sieger == "alt" else e_neu}
    assert seite.fehler == []


def test_alte_sicherung_wandert_beim_einlesen(seite, heute_stand):
    seite.starten(stand=heute_stand())
    datei = json.loads(seite.js("() => sicherungInhalt()"))
    datei["stand"].update({"gewusst": [ALT], "topf": {"w:" + ALT: {"typ": "mc", "n": 0, "z": 77}},
                           "stern": {"w:" + ALT: {"z": 60, "r": 0}}})
    erg = seite.js("""async (text) => {
      frage = async () => true;
      await sicherungEinlesen(new File([text], 'sicherung.json', {type: 'application/json'}));
      return {known: [...known], topf, stern};
    }""", json.dumps(datei))
    assert erg["known"] == [NEU]
    assert erg["topf"] == {"w:" + NEU: {"typ": "mc", "n": 0, "z": 77}}
    assert erg["stern"] == {"w:" + NEU: {"z": 60, "r": 0}}
    assert seite.fehler == []


def test_beide_formen_gelten_und_der_ton_faellt_auf_so_zurueck(seite, heute_stand):
    """Nichts Neues gebaut: matches() trennt bei " / ", audioDatei() nimmt ohne
    Aufnahme "so / sol" die erste Form - bis Ajdin die neue Aufnahme bestellt."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const w = wortNachId('salz:so / sol').w;
      const vorher = AUDIO;
      AUDIO = new Map([['so', 'w0119.mp3']]);
      const ton = audioDatei(w.bs);
      AUDIO = vorher;
      return {so: matches('so', w.bs), sol: matches('Sol', w.bs), falsch: matches('sok', w.bs),
              tippen: typable(w), ton};
    }""")
    assert erg == {"so": "ok", "sol": "ok", "falsch": "no", "tippen": False, "ton": "w0119.mp3"}
    assert seite.fehler == []
