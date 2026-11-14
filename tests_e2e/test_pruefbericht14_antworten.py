# -*- coding: utf-8 -*-
"""Pruefbericht 1.4 (14.11.2026) im Browser: richtige Antworten, die ein Leben kosteten.

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
