# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026) im Browser: richtige Antworten, die ein Leben kosteten (V3, B5, B9, V11).

V3: „Wann kommst du?“, getippt „Kad dolaziš?“, gab erst „Fast richtig!“, dann
„Richtig wäre: Kada dolaziš?“ und ein Leben weniger. Ebenso Zdravo im
Lueckensatz „___, kako si?“, „Uspio sam!“ und „Šta se dogodilo?“. Jetzt zaehlt
die andere Antwort gleich als richtig, ohne Leben.
"""
from test_tippfehler import EINGEBEN, LAGE, LEGEN, STARTEN

V3 = [("type", "wann kommst du?:Kada dolaziš?", "Kad dolaziš?"),
      ("type", "wann wirst du kommen?:Kada ćeš doći?", "Kad ćeš doći?"),
      ("type", "wann heiratest du?:Kad se ženiš?", "Kada se ženiš?"),
      ("type", "ich habe es geschafft!:Uspjela sam!", "Uspio sam!"),
      ("type", "was ist passiert?:Šta se desilo?", "Šta se dogodilo?"),
      ("gap", "___, kako si?|Merhaba", "Zdravo"),
      # Das Bisherige bleibt richtig.
      ("type", "wann kommst du?:Kada dolaziš?", "Kada dolaziš?"),
      ("type", "ich habe es geschafft!:Uspjela sam!", "Uspjela sam!"),
      ("gap", "___, kako si?|Merhaba", "Merhaba")]


def _antworten(seite, faelle):
    seite.js(STARTEN["Lx"])
    aus = []
    for typ, ziel, eingabe in faelle:
        leben = seite.js(LEGEN, ["Lx", typ, ziel])
        seite.js(EINGEBEN, [eingabe, 250])
        aus.append((ziel, eingabe, leben, seite.js(LAGE, "")))
    return aus


def test_v3_die_andere_antwort_kostet_kein_leben(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for ziel, eingabe, leben, lage in _antworten(seite, V3):
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, eingabe, lage)
        assert lage["fb"] == "Tačno! ✓" and "ok" in lage["klasse"].split(), (ziel, eingabe, lage)
    assert seite.fehler == []


def test_v3_nur_die_genannten_formen(seite, heute_stand):
    """kad/kada gilt nur in den drei Fragen, nicht fuer jedes Wort: kada heisst
    auch „Badewanne“. Ein anderes Verb bleibt falsch."""
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const typ = (id, e) => matches(e, annehmbar(wortNachId(id).w).join(' / '));
      const s = SENTENCES.find(x => x.text === '___, kako si?');
      return [typ('wann kommst du?:Kada dolaziš?', 'Kad dolazis'),
              typ('was ist passiert?:Šta se desilo?', 'Šta se dešava?'),
              typ('ich habe es geschafft!:Uspjela sam!', 'Uspio si!'),
              matches('Doviđenja', [s.answer, ...(s.auch || []), ...(s.auch_var || [])].join(' / '))];
    }""")
    assert erg == ["almost", "no", "no", "no"], erg
    assert seite.fehler == []


# B5 (F16 ja): Ćao ist auch „Hallo“. Getippt bei „Hallo“ und im Lueckensatz
# „___, kako si?“ kostet es kein Leben mehr, beim Satzbau „Merhaba, kako si?“
# liegt ćao nie als falsche Kachel.
B5 = [("type", "hallo:Merhaba", "Ćao"),
      ("gap", "___, kako si?|Merhaba", "Ćao")]


def test_b5_cao_kostet_bei_hallo_kein_leben(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for ziel, eingabe, leben, lage in _antworten(seite, B5):
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, eingabe, lage)
        assert lage["fb"] == "Tačno! ✓" and "ok" in lage["klasse"].split(), (ziel, eingabe, lage)
    assert seite.fehler == []


def test_b5_cao_nie_als_kachel_neben_merhaba(seite, heute_stand):
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => {
      const s = SATZBAU.find(x => x.bs === 'Merhaba, kako si?');
      const gesehen = new Set();
      for(let n = 0; n < 300; n++) kachelAblenker(s, 3).forEach(x => gesehen.add(x.toLowerCase()));
      return {ohne: s.ohne, cao: gesehen.has('ćao'), anzahl: gesehen.size};
    }""")
    assert erg["ohne"][:1] == ["ćao"] and erg["cao"] is False and erg["anzahl"] > 5, erg
    assert seite.fehler == []


# V11 (F7 a): Gdje gilt umgangssprachlich auch fuer „wohin“. „Wohin gehst du?“ und der
# Lueckensatz „___ ideš?“ nehmen es ohne Leben; in der Grammatik „Fragen stellen“ steht
# Gdje nicht mehr als falscher Knopf neben Kuda.
V11 = [("type", "wohin gehst du?:Kuda ideš?", "Gdje ideš?"),
       ("gap", "___ ideš?|Kuda", "Gdje"),
       ("type", "wohin gehst du?:Kuda ideš?", "Kuda ideš?"),
       ("gap", "___ ideš?|Kuda", "Kuda")]


def test_v11_gdje_kostet_bei_wohin_kein_leben(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for ziel, eingabe, leben, lage in _antworten(seite, V11):
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, eingabe, lage)
        assert lage["fb"] == "Tačno! ✓" and "ok" in lage["klasse"].split(), (ziel, eingabe, lage)
    assert seite.fehler == []


def test_v11_grammatik_gdje_kein_falscher_knopf(seite, heute_stand):
    seite.starten(stand=heute_stand())
    erg = seite.js("""() => GRAMMAR.fragen.uebungen.filter(g => g.richtig === 'Kuda')
                              .map(g => ({optionen: g.optionen, tipp: g.tipp}))""")
    assert erg == [{"optionen": ["Kuda", "Kada", "Ko"],
                    "tipp": "Bewegung in eine Richtung: Kuda. Gesprochen oft auch Gdje."}], erg
    assert seite.fehler == []


# B9: Alejkumu selam hiess "(Antwort darauf)" und stand vor Selam alejkum - der
# Verweis ging ins Leere. Die neue Bedeutung aendert die Kennung; UMBENANNT zieht
# gewusst, Fehler-Topf und Sterne mit (wie salz:so in test_umbenannt.py).
B9_ALT, B9_NEU = "(antwort darauf):Alejkumu selam", "antwort auf selam alejkum:Alejkumu selam"


def test_b9_alter_lernstand_wandert_mit(seite, heute_stand):
    seite.starten(stand=heute_stand(gewusst=[B9_ALT, "brot:hljeb"],
                                    topf={"w:" + B9_ALT: {"typ": "type", "n": 1, "z": 123}},
                                    stern={"w:" + B9_ALT: {"z": 50, "r": 7}}))
    jetzt = seite.js("""([alt, neu]) => ({known: [...known], topf, stern, alt: !!wortNachId(alt),
                                          umbenannt: UMBENANNT[alt], de: wortNachId(neu).w.de})""", [B9_ALT, B9_NEU])
    assert jetzt["alt"] is False and jetzt["umbenannt"] == B9_NEU and jetzt["de"] == "Antwort auf Selam alejkum"
    assert B9_NEU in jetzt["known"] and B9_ALT not in jetzt["known"] and "brot:hljeb" in jetzt["known"]
    assert jetzt["topf"] == {"w:" + B9_NEU: {"typ": "type", "n": 1, "z": 123}}
    assert jetzt["stern"] == {"w:" + B9_NEU: {"z": 50, "r": 7}}
    gespeichert = seite.js("() => JSON.parse(localStorage.getItem('zmaj_stand'))")
    assert B9_NEU in gespeichert["gewusst"] and B9_ALT not in gespeichert["gewusst"]
    assert seite.fehler == []


def test_b9_als_schreibaufgabe_loesbar(seite, heute_stand):
    """Die Aufgabe nennt jetzt den Gruss, auf den man antwortet."""
    seite.starten(stand=heute_stand())
    seite.js(STARTEN["Lx"])
    leben = seite.js(LEGEN, ["Lx", "type", B9_NEU])
    assert "Antwort auf Selam alejkum" in seite.js("() => document.getElementById('lBody').innerText")
    seite.js(EINGEBEN, ["Alejkumu selam", 250])
    lage = seite.js(LAGE, "")
    assert lage["ergebnis"] is True and lage["leben"] == leben and lage["fb"] == "Tačno! ✓", lage
    assert seite.fehler == []


def test_b9_bedeutung_auf_englisch(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="en")
    assert seite.js("(id) => wortNachId(id).w.de", B9_NEU) == "reply to Selam alejkum"
    assert seite.fehler == []
