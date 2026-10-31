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
# Am 26.10.2026 abends dazu, Ajdin: „und auch reihenfolge berücksichtigen
# wo es noch sinn ergibt geh durch die app durch“: konjugation und zukunft
# (je Verb ja, ti, on/ona, mi, vi, oni) und routine (aufstehen bis
# schlafen gehen). Jahreszeiten (wetter) und Tageszeiten (zeit) sind nur
# ein Teil ihres Levels: dort ordnet "reihe" nur sie, der Rest bleibt
# gemischt (TEIL_REIHEN).
# Am 27.10.2026 von Ajdin auf Rückfrage zu diesem Wunsch ausgewählt:
# vergangenheit (bio sam, bio si, bio je, bila je, bili smo), modal (je
# Verb der Infinitiv, dann die Personen) und adjektive (je Adjektiv groß,
# größer, am größten) ganz; in basics als Teil-Reihe die Grüße nach
# Tageszeit, denn der Rest von basics hat keine Reihe.
# Seit 31.10.2026 die zehn Level der Sektion Tun und Lassen (Wortschatz-Paket
# 1): dort steht jedes Wort direkt vor seinem Beispielsatz, wie in routine das
# Verb vor dem Ich-Satz. Geprueft in tests/test_paket1.py.
PAKET1 = {"kommen_gehen", "geben_nehmen", "sagen_denken", "verstehen", "anfangen", "tun_machen",
          "stellen_legen", "alltag_leben", "passieren", "notfall"}
# Ebenso die elf Level aus Wortschatz-Paket 2 (31.10.2026): vier in Tun und
# Lassen, sieben in Sektion 11 · Wie etwas ist. Geprueft in tests/test_paket2.py.
PAKET2 = {"paare_geben", "paare_denken", "paare_alltag", "im_haushalt", "lang_kurz", "voll_leer", "moeglich",
          "wie_jemand_ist", "benehmen", "glueck_sorgen", "sinne"}
GEORDNET = {"zahlen", "wochentage", "monate", "mengen", "konjugation", "zukunft", "routine",
            "vergangenheit", "modal", "adjektive"} | PAKET1 | PAKET2
TEIL_REIHEN = {"zeit": ["jutro", "podne", "večer", "noć"],
               "wetter": ["proljeće", "ljeto", "jesen", "zima"],
               "basics": ["Dobro jutro", "Dobar dan", "Dobro veče", "Laku noć / Lahku noć"]}
# Personenfolge, am deutschen Pronomen abgelesen: ja, ti, on/ona, mi, vi, oni
PERSON = {"ich": 0, "du": 1, "er": 2, "wir": 3, "ihr": 4, "sie": 5}
# vergangenheit: biti in der Folge ja, ti, on, ona, mi - am deutschen
# Pronomen abgelesen ist "sie war" hier ona, nicht oni
VERGANGENHEIT_PERSON = {"ich": 0, "du": 1, "er": 2, "sie": 3, "wir": 4}
VERGANGENHEIT_BITI = ["bio sam / bila sam", "bio si / bila si", "bio je", "bila je", "bili smo"]
# modal: je Verb der Infinitiv (falls im Level), dann die Personen
MODAL_VERBEN = [["morati", "moram", "moraš", "moramo"],
                ["može", "možemo"],
                ["hoćeš", "hoćemo"],
                ["smjeti", "smijem"]]
# Im Rest von modal steht das einzelne Wort vor seinem Satz (27.10.2026)
MODAL_WORT_VOR_SATZ = [("pitati", "Smijem li pitati?"), ("čekati", "Moramo čekati"),
                       ("nešto", "Želim nešto jesti"), ("plivati", "Ne znam plivati")]
# adjektive: je Adjektiv Grundform (m/w), Komparativ, Superlativ - soweit
# das Level die Formen hat
ADJEKTIV_REIHEN = [["velik / velika", "veći", "najveći"],
                   ["mali / mala", "manji"],
                   ["dobar / dobra", "bolji", "najbolji"],
                   ["loš / loša", "gori"],
                   ["lijep / lijepa", "ljepši"],
                   ["star / stara", "stariji"],
                   ["mlad / mlada", "mlađi"],
                   ["skup / skupa / skupo", "skuplji"]]
ADJEKTIV_REST = ["nego / od", "jako", "previše", "To je bolje nego to"]
GRUESSE_DE = ["Guten Morgen", "Guten Tag", "Guten Abend", "Gute Nacht"]
# Der Tag in Folge; die Ich-Sätze stehen jeweils hinter ihrem Verb
TAGESABLAUF = ["ustajati", "tuširati se", "prati zube", "doručkovati", "ići na posao",
               "ručati", "doći kući", "kuhati", "gledati televiziju", "ići spavati"]

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
    """Ajdin am 26.10.2026: Zahlen fangen mit jedan an, nula kommt nach
    deset. Danach weiter nach dem Wert."""
    woerter = _level(grunddaten, "zahlen")["words"]
    werte = [_zahlwert(w["bs"]) for w in woerter]
    assert None not in werte, [w["bs"] for w, n in zip(woerter, werte) if n is None]
    assert werte[:11] == list(range(1, 11)) + [0]  # jedan, dva ... deset, nula
    rest = werte[11:]
    assert rest == sorted(rest) and rest[0] > 10 and len(set(werte)) == len(werte), \
        list(zip([w["bs"] for w in woerter], werte))
    assert [w["bs"] for w in woerter[9:12]] == ["deset", "nula", "jedanaest"]
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


def test_konjugation_je_verb_in_personenfolge(grunddaten):
    """ja sam, ti si ... oni su, dann imam ... imaju, idem, ideš, idemo, idu
    und so weiter: innerhalb eines Verbs steigt die Person, jedes Verb
    beginnt bei ja."""
    woerter = _level(grunddaten, "konjugation")["words"]
    bs = [w["bs"] for w in woerter]
    assert bs[:6] == ["ja sam", "ti si", "on je / ona je", "mi smo", "vi ste", "oni su"]
    assert bs[6:12] == ["imam", "imaš", "ima", "imamo", "imate", "imaju"]
    raenge = [PERSON[w["de"].split()[0]] for w in woerter]
    for i in range(1, len(raenge)):
        assert raenge[i] > raenge[i - 1] or raenge[i] == 0, (bs[i - 1], bs[i])


def test_zukunft_erst_die_personen(grunddaten):
    woerter = _level(grunddaten, "zukunft")["words"]
    assert [w["bs"] for w in woerter[:5]] == ["ću", "ćeš", "će", "ćemo", "ćete"]
    raenge = [PERSON[w["de"].split()[0]] for w in woerter[:5]]
    assert raenge == sorted(raenge)


def test_tagesablauf_vom_aufstehen_bis_zum_schlafen(grunddaten):
    bs = [w["bs"] for w in _level(grunddaten, "routine")["words"]]
    stellen = [bs.index(x) for x in TAGESABLAUF]
    assert stellen == sorted(stellen), list(zip(TAGESABLAUF, stellen))
    assert bs[0] == "ustajati" and bs[bs.index("ići spavati") + 1] == "Idem spavati"
    # erst der Tag, dann was keinen festen Platz im Tag hat
    assert max(stellen) < bs.index("ići u kupovinu") < bs.index("rano")


def test_vergangenheit_je_verb_in_personenfolge(grunddaten):
    """bio sam, bio si, bio je, bila je, bili smo; dann die Verben, von
    denen das Level nur die Ich-Form hat (imao sam, radio sam ...); danach
    Zeitangaben und Sätze. Inhalt unverändert, nur geordnet (27.10.2026)."""
    woerter = _level(grunddaten, "vergangenheit")["words"]
    bs = [w["bs"] for w in woerter]
    assert bs[:5] == VERGANGENHEIT_BITI
    raenge = [VERGANGENHEIT_PERSON[w["de"].split()[0]] for w in woerter[:5]]
    assert raenge == [0, 1, 2, 3, 4]
    ich = [i for i, w in enumerate(woerter) if i >= 5 and w["de"].startswith("ich ")]
    assert len(ich) >= 8 and ich == list(range(5, 5 + len(ich))), ich
    assert all(" sam / " in bs[i] for i in ich), [bs[i] for i in ich]
    rest = woerter[5 + len(ich):]
    assert not [w for w in rest if w["de"].split()[0] in VERGANGENHEIT_PERSON], rest


def test_modal_je_verb_in_personenfolge(grunddaten):
    """morati, moram, moraš, moramo, može, možemo, hoćeš, hoćemo, smjeti,
    smijem: je Verb der Infinitiv vorn, dann steigt die Person. Danach der
    Rest; darin kommt das einzelne Wort vor dem Satz, der es braucht."""
    woerter = _level(grunddaten, "modal")["words"]
    bs = [w["bs"] for w in woerter]
    vorn = [x for verb in MODAL_VERBEN for x in verb]
    assert bs[:len(vorn)] == vorn
    for verb in MODAL_VERBEN:
        # -1: kein Pronomen, also der Infinitiv - nur vorn erlaubt
        raenge = [PERSON.get(woerter[bs.index(x)]["de"].split()[0], -1) for x in verb]
        assert raenge == sorted(set(raenge)) and -1 not in raenge[1:], (verb, raenge)
    for wort, satz in MODAL_WORT_VOR_SATZ:
        assert len(vorn) <= bs.index(wort) < bs.index(satz), (wort, satz)


def test_adjektive_je_adjektiv_gesteigert(grunddaten):
    """velik, veći, najveći, mali, manji, dobar, bolji, najbolji ...: je
    Adjektiv die Grundform, dann der Komparativ, dann der Superlativ, in
    einem Stück. Was nicht gesteigert wird, steht danach."""
    woerter = _level(grunddaten, "adjektive")["words"]
    bs = [w["bs"] for w in woerter]
    assert bs[:3] == ["velik / velika", "veći", "najveći"]
    stellen = []
    for reihe in ADJEKTIV_REIHEN:
        i = bs.index(reihe[0])
        assert bs[i:i + len(reihe)] == reihe, reihe
        de = [woerter[i + k]["de"] for k in range(len(reihe))]
        assert "(m/w" in de[0] and de[1].endswith("er"), de          # groß (m/w), größer
        assert all(x.startswith("am ") for x in de[2:]), de           # am größten
        stellen.append(i)
    assert stellen == sorted(stellen)
    letzte = max(bs.index(r[-1]) for r in ADJEKTIV_REIHEN)
    assert all(bs.index(x) > letzte for x in ADJEKTIV_REST)
    # Jeder Superlativ steht direkt hinter seinem Komparativ
    for i, w in enumerate(woerter):
        if w["de"].startswith("am "):
            assert bs[i - 1] in [r[1] for r in ADJEKTIV_REIHEN], (bs[i - 1], bs[i])


def test_gruesse_nach_tageszeit(grunddaten):
    """Die Grüße stehen nur in basics; ihre Teil-Reihe geht vom Morgen bis
    zur Nacht. Kein anderes Level hat sie als Wort, sonst kämen sie dort
    ungeordnet (27.10.2026)."""
    reihe = TEIL_REIHEN["basics"]
    woerter = _level(grunddaten, "basics")["words"]
    assert [next(w["de"] for w in woerter if w["bs"] == x) for x in reihe] == GRUESSE_DE
    sonst = [(k["id"], w["bs"]) for k in grunddaten["kategorien"] if k["id"] != "basics"
             for w in k["words"] if w["bs"] in reihe or w["de"] in GRUESSE_DE]
    assert not sonst, sonst


def test_teil_reihen(grunddaten):
    """Nur zeit, wetter und basics haben "reihe"; jedes Wort darin steht
    genau einmal im Level, und "reihenfolge" fehlt dort (der Rest ist
    gemischt)."""
    mit = {k["id"]: k["reihe"] for k in grunddaten["kategorien"] if "reihe" in k}
    assert mit == TEIL_REIHEN
    for kid, reihe in TEIL_REIHEN.items():
        k = _level(grunddaten, kid)
        assert "reihenfolge" not in k
        bs = [w["bs"] for w in k["words"]]
        assert all(bs.count(x) == 1 for x in reihe), (kid, reihe)
        # Auch die Liste steht in der Folge der Reihe: Anki, die Exporte und
        # die Wortliste des Levels gehen nach ihr (Prüfer 27.10.2026)
        stellen = [bs.index(x) for x in reihe]
        assert stellen == sorted(stellen), (kid, stellen)
    import inhalt
    assert not [p for p in inhalt.pruefe_vokabeln(grunddaten) if "reihe" in p]


@pytest.mark.parametrize("kid, reihe, teil", [
    ("zeit", ["jutro", "mittag"], "[zeit] reihe nennt 'mittag'"),
    ("zeit", ["jutro"], "[zeit] reihe muss eine Liste"),
    ("zeit", "jutro podne", "[zeit] reihe muss eine Liste"),
    ("zeit", ["jutro", "jutro"], "[zeit] reihe muss eine Liste"),
    ("zahlen", ["jedan", "dva"], "[zahlen] reihe und reihenfolge zugleich"),
])
def test_pruefung_meldet_falsche_reihe(grunddaten, kid, reihe, teil):
    import inhalt
    daten = copy.deepcopy(grunddaten)
    _level(daten, kid)["reihe"] = reihe
    assert any(teil in p for p in inhalt.pruefe_vokabeln(daten)), inhalt.pruefe_vokabeln(daten)


def test_feld_kommt_in_jeder_sprache_an(alle_daten, grunddaten):
    """uebersetzungen.anwenden() baut die Level neu zusammen - das Feld und
    die Reihenfolge der Wörter müssen das überstehen."""
    for code, daten in alle_daten.items():
        for kid in GEORDNET:
            k = _level(daten, kid)
            assert k.get("reihenfolge") is True, (code, kid)
            assert [w["id"] for w in k["words"]] == [w["id"] for w in _level(grunddaten, kid)["words"]], (code, kid)
        for kid, reihe in TEIL_REIHEN.items():
            assert _level(daten, kid).get("reihe") == reihe, (code, kid)


@pytest.mark.parametrize("wert", ["ja", 1, None])
def test_pruefung_meldet_falschen_wert(grunddaten, wert):
    import inhalt
    daten = copy.deepcopy(grunddaten)
    _level(daten, "zahlen")["reihenfolge"] = wert
    assert any("[zahlen] reihenfolge muss True oder False sein" in p for p in inhalt.pruefe_vokabeln(daten))
