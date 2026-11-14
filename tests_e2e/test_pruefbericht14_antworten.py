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
      ("gap", "___, kako si?|Merhaba", "Ćao"),
      # Seit dem 14.11.2026 auch bei Zdravo (Offen-Liste, Punkt 2).
      ("type", "hallo (neutral, überall):Zdravo", "Ćao"),
      ("type", "hallo (neutral, überall):Zdravo", "Zdravo")]


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


# B1 (F12 e): „Fališ mi“ zaehlt bei „Ich vermisse dich“. Der Lueckensatz „___ mi.“ richtet
# sich nach dem Wort (V3) und nimmt seit dem 14.11.2026 auch Fališ (Offen-Liste, Punkt 2).
B1_LUECKE = [("gap", "___ mi.|Nedostaješ", "Fališ"),
             ("gap", "___ mi.|Nedostaješ", "Nedostaješ"),
             ("type", "ich vermisse dich:Nedostaješ mi", "Fališ mi")]


def test_b1_falis_kostet_auch_in_der_luecke_kein_leben(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for ziel, eingabe, leben, lage in _antworten(seite, B1_LUECKE):
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, eingabe, lage)
        assert lage["fb"] == "Tačno! ✓" and "ok" in lage["klasse"].split(), (ziel, eingabe, lage)
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


# B6 (F17 b): "nana (auch: metvica)" heisst jetzt "nana / metvica" wie kahva / kafa. Der
# alte Lernstand wandert mit, beim Sprechen zaehlt auch metvica, und bis es die Aufnahme
# mit beiden Formen gibt, klingt die erste Form "nana".
B6_ALT, B6_NEU = "minze:nana (auch: metvica)", "minze:nana / metvica"


def test_b6_alter_lernstand_wandert_mit(seite, heute_stand):
    seite.starten(stand=heute_stand(gewusst=[B6_ALT, "brot:hljeb"],
                                    topf={"w:" + B6_ALT: {"typ": "type", "n": 1, "z": 123}},
                                    stern={"w:" + B6_ALT: {"z": 50, "r": 7}}))
    jetzt = seite.js("""([alt, neu]) => ({known: [...known], topf, stern, alt: !!wortNachId(alt),
                                          bs: wortNachId(neu).w.bs})""", [B6_ALT, B6_NEU])
    assert jetzt["alt"] is False and jetzt["bs"] == "nana / metvica"
    assert B6_NEU in jetzt["known"] and B6_ALT not in jetzt["known"] and "brot:hljeb" in jetzt["known"]
    assert jetzt["topf"] == {"w:" + B6_NEU: {"typ": "type", "n": 1, "z": 123}}
    assert jetzt["stern"] == {"w:" + B6_NEU: {"z": 50, "r": 7}}
    assert seite.fehler == []


def test_b6_beide_formen_beim_tippen_und_sprechen(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="en")
    erg = seite.js("""(id) => {
      const w = wortNachId(id).w, ziele = String(w.bs).split(' / ');
      return {bs: w.bs, tippen: ['nana', 'metvica'].map(e => matches(e, annehmbar(w).join(' / '))),
              sprechen: ['nana', 'metvica'].map(s => ziele.some(z => klingtWie(s, z))),
              ton: audioDatei(w.bs) === audioDatei('nana') && !!audioDatei('nana')};
    }""", B6_NEU)
    assert erg == {"bs": "nana / metvica", "tippen": ["ok", "ok"], "sprechen": [True, True], "ton": True}, erg
    assert seite.fehler == []


# S2 (F19): koleginica heisst kolegica, als Wort, im Lueckensatz und im Satzbau-Satz. Der
# alte Lernstand von Wort und Satz wandert mit; die Web-Demo hat fuer die neuen Texte keinen
# Ton (den spricht nur Emir, in der App aus dem Store), sie faellt auf keine alte Aufnahme
# mit "koleginica" zurueck.
S2_ALT, S2_NEU = "kollegin:koleginica", "kollegin:kolegica"
S2_SATZ_ALT, S2_SATZ_NEU = "k:kennenlernen|Ovo je moja koleginica.", "k:kennenlernen|Ovo je moja kolegica."


def test_s2_alter_lernstand_wandert_mit(seite, heute_stand):
    seite.starten(stand=heute_stand(gewusst=[S2_ALT, "brot:hljeb"],
                                    topf={"w:" + S2_ALT: {"typ": "type", "n": 1, "z": 123},
                                          S2_SATZ_ALT: {"typ": "kacheln", "n": 1, "z": 124}},
                                    stern={"w:" + S2_ALT: {"z": 50, "r": 7}, S2_SATZ_ALT: {"z": 51, "r": 7}}))
    jetzt = seite.js("""(neu) => ({known: [...known], topf, stern, bs: wortNachId(neu).w.bs})""", S2_NEU)
    assert jetzt["bs"] == "kolegica"
    assert S2_NEU in jetzt["known"] and S2_ALT not in jetzt["known"] and "brot:hljeb" in jetzt["known"]
    assert jetzt["topf"] == {"w:" + S2_NEU: {"typ": "type", "n": 1, "z": 123},
                             S2_SATZ_NEU: {"typ": "kacheln", "n": 1, "z": 124}}
    assert jetzt["stern"] == {"w:" + S2_NEU: {"z": 50, "r": 7}, S2_SATZ_NEU: {"z": 51, "r": 7}}
    assert seite.fehler == []


S2 = [("type", S2_NEU, "kolegica"), ("gap", "Ovo je moja ___.|kolegica", "kolegica")]


def test_s2_kolegica_ist_richtig(seite, heute_stand):
    seite.starten(stand=heute_stand())
    for ziel, eingabe, leben, lage in _antworten(seite, S2):
        assert lage["ergebnis"] is True and lage["leben"] == leben, (ziel, eingabe, lage)
        assert lage["fb"] == "Tačno! ✓" and "ok" in lage["klasse"].split(), (ziel, eingabe, lage)
    erg = seite.js("""() => ({satz: SATZBAU.filter(s => s.bs.startsWith('Ovo je moja kol')).map(s => s.bs),
                              wort: audioDatei('kolegica'), ganz: audioDatei('Ovo je moja kolegica.')})""")
    assert erg == {"satz": ["Ovo je moja kolegica."], "wort": None, "ganz": None}, erg
    assert seite.fehler == []


def test_b9_bedeutung_auf_englisch(seite, heute_stand):
    seite.starten(stand=heute_stand(), sprache="en")
    assert seite.js("(id) => wortNachId(id).w.de", B9_NEU) == "reply to Selam alejkum"
    assert seite.fehler == []
