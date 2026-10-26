# -*- coding: utf-8 -*-
"""Neue Wörter der Reihe nach (26.10.2026).

Ajdin: „bei der zahlen sektion am besten die zahlen in reihenfolge lernen
sowie wochentage und wo es noch passt“. Ein Level mit "reihenfolge": True
stellt seine neuen Wörter in der Reihenfolge von "words" vor (buildLesson()
in web/index.html mischt sie dann nicht). Hier: welche Level das sind, dass
ihre Wörter in vokabeln.py wirklich in der natürlichen Reihe stehen, und
dass das Feld in jeder Sprache bis in die App kommt. Was die App daraus
macht, prüft tests_e2e/test_reihenfolge.py im Browser.
"""
import copy

import pytest

# Entschieden am 26.10.2026: nur Level, deren Wörter eine eindeutige Reihe
# haben. Dazu gehört auch mengen (Zahlen im Satz): seine Liste steht in
# Gruppen, je Hauptwort erst eins, dann zwei bis vier, dann fünf - so wie
# der Tipp des Levels „Jedan brat, dva brata, pet braće“ -, danach
# nekoliko/nekoliko dana, pola/pola kilograma, prvi, drugi, treći, zadnji.
# Jahreszeiten (wetter), Tageszeiten (zeit) und die Personen der Verben
# (konjugation, zukunft) sind nur ein Teil ihres Levels - dort bleibt es
# gemischt.
GEORDNET = {"zahlen", "wochentage", "monate", "mengen"}

WOCHENTAGE = ["ponedjeljak", "utorak", "srijeda", "četvrtak", "petak", "subota", "nedjelja"]
MONATE = ["januar", "februar", "mart", "april", "maj", "juni", "juli", "august",
          "septembar", "oktobar", "novembar", "decembar"]
# mengen beginnt mit den Gruppen aus seinem Tipp: je Hauptwort die Form
# nach eins, dann nach zwei bis vier, dann nach fünf und mehr.
MENGEN_GRUPPEN = [
    ["jedan brat", "dva brata", "pet braće"],
    ["jedna sestra", "dvije sestre", "pet sestara"],
    ["jedna godina", "dvije godine", "pet godina"],
    ["jedan dan", "tri dana", "deset dana"],
    ["jedna kahva", "dvije kahve"],
]
# Was inhalt.zahl_wert() nicht kennt (es reicht bis hundert)
GROSSE_ZAHLEN = {"dvjesto": 200, "hiljada": 1000}


def _level(daten, kid):
    return next(k for k in daten["kategorien"] if k["id"] == kid)


def _zahlwert(bs):
    """Der Wert eines Zahlworts: "pet" -> 5, "dvadeset jedan" -> 21,
    "hiljada" -> 1000, sonst None."""
    import inhalt
    summe = 0
    for teil in bs.lower().split():
        n = GROSSE_ZAHLEN.get(teil, inhalt.zahl_wert(teil))
        if n is None:
            return None
        summe += n
    return summe


def test_genau_diese_level_sind_geordnet(grunddaten):
    geordnet = {k["id"] for k in grunddaten["kategorien"] if k.get("reihenfolge")}
    assert geordnet == GEORDNET
    for kid in GEORDNET:
        assert _level(grunddaten, kid)["reihenfolge"] is True


def test_zahlen_stehen_nach_dem_wert(grunddaten):
    woerter = _level(grunddaten, "zahlen")["words"]
    werte = [_zahlwert(w["bs"]) for w in woerter]
    assert None not in werte, [w["bs"] for w, n in zip(woerter, werte) if n is None]
    assert werte == sorted(werte) and len(set(werte)) == len(werte), list(zip([w["bs"] for w in woerter], werte))
    assert werte[:11] == list(range(11))          # nula, jedan, dva ... deset
    # "sto" ist hier hundert, nicht der Tisch - der steht in zuhause
    ids = [w["id"] for w in woerter]
    assert "hundert:sto" in ids and "tisch:sto" not in ids
    assert ids.index("hundert:sto") == werte.index(100)


def test_wochentage_von_montag_bis_sonntag(grunddaten):
    bs = [w["bs"] for w in _level(grunddaten, "wochentage")["words"]]
    assert bs[:7] == WOCHENTAGE
    assert not set(bs[7:]) & set(WOCHENTAGE)      # danach nur noch vikend, sedmica


def test_monate_von_januar_bis_dezember(grunddaten):
    bs = [w["bs"] for w in _level(grunddaten, "monate")["words"]]
    assert bs[:12] == MONATE
    assert not set(bs[12:]) & set(MONATE)          # danach mjesec, godina


def test_mengen_erst_eins_dann_die_mehrzahl(grunddaten):
    """Der Tipp des Levels: „Jedan brat, dva brata, pet braće: nach Zahlen
    ändert sich das Wort.“ Der Reihe nach kommt so jede Form mit eins vor
    ihrer Mehrzahl, und eine Gruppe steht in einer Lektion beisammen statt
    über drei verteilt."""
    import inhalt
    bs = [w["bs"] for w in _level(grunddaten, "mengen")["words"]]
    vorn = [x for gruppe in MENGEN_GRUPPEN for x in gruppe]
    assert bs[:len(vorn)] == vorn
    for gruppe in MENGEN_GRUPPEN:
        # Die Zahl vorn; "jedna" kennt zahl_wert() nicht, dvije nur als weiblich
        vorn_z = [x.split()[0] for x in gruppe]
        werte = [1 if z == "jedna" else inhalt.zahl_wert(z) or inhalt.zahl_wert(z, weiblich=True)
                 for z in vorn_z]
        assert [inhalt.zahl_klasse(n) for n in werte] == ["1", "2-4", "5+"][:len(gruppe)], (gruppe, werte)
    i = bs.index("prvi")
    assert bs[i:i + 4] == ["prvi", "drugi", "treći", "zadnji"]


def test_feld_kommt_in_jeder_sprache_an(alle_daten, grunddaten):
    """uebersetzungen.anwenden() baut die Level neu zusammen - das Feld und
    die Reihenfolge der Wörter müssen das überstehen."""
    for code, daten in alle_daten.items():
        for kid in GEORDNET:
            k = _level(daten, kid)
            assert k.get("reihenfolge") is True, (code, kid)
            assert [w["id"] for w in k["words"]] == [w["id"] for w in _level(grunddaten, kid)["words"]], (code, kid)


@pytest.mark.parametrize("wert", ["ja", 1, None])
def test_pruefung_meldet_falschen_wert(grunddaten, wert):
    import inhalt
    daten = copy.deepcopy(grunddaten)
    _level(daten, "zahlen")["reihenfolge"] = wert
    assert any("[zahlen] reihenfolge muss True oder False sein" in p for p in inhalt.pruefe_vokabeln(daten))
