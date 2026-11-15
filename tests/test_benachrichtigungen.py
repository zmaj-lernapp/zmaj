# -*- coding: utf-8 -*-
"""Benachrichtigungen mit Persoenlichkeit (Version 1.4, Ajdin am 13.11.2026:
11a 12a 13a, Vorlage benachrichtigungen.md): was sich ohne Browser pruefen
laesst - die Texte in acht Sprachen, ihre Platzhalter und die festen Regeln.
Welche Gruppe an welchem Abend kommt und dass kein Text zweimal
hintereinander kommt, prueft tests_e2e/test_benachrichtigungen.py in der
echten App.

Am 14.11.2026 hat Ajdin die 24 Texte gelesen und sieben gestrichen: A1
("Raus"), B4 mit dem Wort im Titel ("diese Benachrichtigung ist komisch
mach weg", samt Wortliste BEN_WORTE und Platzhalter {wort}) und die ganze
Gruppe D, die Wortwitze ("Der Rest raus"). Es bleiben 17, wortgleich."""
import re

import pytest

GRUPPEN = {"a": 6, "b": 6, "c": 6, "d": 6}
# Am 14.11.2026 von Ajdin gestrichen
GESTRICHEN = ["a1", "b4", "d1", "d2", "d3", "d4", "d5", "d6"]
SCHLUESSEL = ["%s%d" % (g, i) for g, n in GRUPPEN.items() for i in range(1, n + 1)
              if "%s%d" % (g, i) not in GESTRICHEN]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐]")
PLATZHALTER = {"n", "ziel", "rekord", "woerter", "tage", "level", "farbe"}

# Die deutschen Texte, wie Ajdin sie am 13.11.2026 freigegeben hat, ohne
# die am 14.11.2026 gestrichenen. Neu dazu kam nur die Einzahl dort, wo die
# Serie 1 Tag lang sein kann.
DEUTSCH = {
    "a2": ("Pazi! 🔥 {n} Tag|Pazi! 🔥 {n} Tage", "Deine Serie wackelt. Fünf Minuten halten sie fest."),
    "a3": ("🔥 {n} Tag|🔥 {n} Tage", "Zmaj hat das Holz schon geholt. Anzünden musst du."),
    "a4": ("Inat-Zeit 🔥", "{n} Tage am Stück. Zeig der Serie, wer hier stur ist."),
    "a5": ("🔥 {n} Tag|🔥 {n} Tage", "Hajde, nur eine Lektion. Zmaj passt so lange auf die Flamme auf."),
    "a6": ("Heute wird's Tag {ziel} 🔥", "Eine Lektion fehlt. Zmaj hält das Konfetti schon bereit."),
    "b1": ("Šta ima? 🐉", "{tage} Tage Funkstille. Zmaj hat deine Wörter abgestaubt."),
    "b2": ("Bolje ikad nego nikad 🐉", "„Besser irgendwann als nie“, sagt man in Bosnien. Eine kleine Lektion?"),
    "b3": ("Polako 🐉", "Serie weg? Halb so wild. Tag 1 ist der beste Tag zum Anfangen."),
    "b5": ("Dein Platz ist noch frei 🐉", "„{level}“ wartet genau da, wo du aufgehört hast."),
    "b6": ("Ima li te? 🐉", "Deine {woerter} Wörter sind alle noch da. Zmaj wartet ohne Eile."),
    "c1": ("Svaka čast! 🔥 {n} Tage", "Zmaj erzählt es schon allen anderen Drachen. Machst du weiter?"),
    "c2": ("Schon {woerter} Wörter! 🐉", "So viele, und du sagst noch, du kannst kein Bosnisch?"),
    "c3": ("Aferim! 🐉", "Rekord: {rekord} Tage am Stück. Zmaj verbeugt sich. Ein bisschen."),
    "c4": ("Zrno po zrno 🐉", "Korn für Korn wird's ein Brot. Wort für Wort wird's Bosnisch."),
    "c5": ("{n} Tage! 🔥", "Deine Flamme ist jetzt {farbe}. Zmaj hat sich extra schick gemacht."),
    "c6": ("Hajmo dalje! 🐉", "Gestern geübt, heute die Fortsetzung? Zmaj hat schon Popcorn."),
}

# Die bosnischen Stellen bleiben in jeder Sprache stehen (Prueflisten-Stellen
# ohne Einwand). Tuerkisch schreibt inat mit grossem I als İnat - das Wort ist
# dort dasselbe.
BOSNISCH = {
    "a2": "Pazi", "a5": "Hajde", "b1": "Šta ima", "b2": "Bolje ikad nego nikad", "b3": "Polako",
    "b6": "Ima li te", "c1": "Svaka čast", "c3": "Aferim", "c4": "Zrno po zrno", "c6": "Hajmo dalje",
}

# Laenge nach der Vorlage: Titel bis 30 Zeichen, Text bis 80. Die
# Ausnahme fuer B4 (Titel bis 36) ist mit B4 weg.
TITEL_BIS, TEXT_BIS = 30, 80


def _laengste_werte(code, daten, index_html):
    """Die laengsten echten Werte je Sprache: der laengste Level-Name dieser
    Sprache (so, wie die App ihn bekommt), die laengste Flammenfarbe; Serie
    und Rekord 365, die Wegmarke 1000, 7000 Woerter. Die Pause ({tage} in
    B1) steht seit dem 14.11.2026 auch nach 7 und mehr Tagen - gerechnet ab
    dem letzten Lerntag, also beliebig lang; hier dreistellig."""
    import sprachen
    t = sprachen.TEXTE[code]
    return {"n": "365", "ziel": "1000", "rekord": "365", "woerter": "7000", "tage": "365",
            "level": max((k["label"] for k in daten["kategorien"]), key=len),
            "farbe": max((t["ben.farbe_" + f] for f in ("blau", "lila", "gold")), key=len)}


def _js_tabelle(index_html):
    rumpf = index_html.split("const BEN_TEXTE = {")[1].split("};")[0]
    return dict((k, (a, b)) for k, a, b in
                re.findall(r"(\w+): \['(ben\.\w+)', '(ben\.\w+)'\]", rumpf))


def test_tabelle_im_code_kennt_alle_17(index_html):
    tab = _js_tabelle(index_html)
    assert sorted(tab) == sorted(SCHLUESSEL)
    for k, (titel, text) in tab.items():
        assert (titel, text) == ("ben.%s_titel" % k, "ben.%s_text" % k)


def test_alle_texte_in_allen_sprachen(sprachcodes):
    import sprachen
    for code in sprachcodes:
        eigene = sprachen.TEXTE[code]
        for k in SCHLUESSEL:
            for teil in ("titel", "text"):
                v = eigene.get("ben.%s_%s" % (k, teil))
                assert isinstance(v, str) and v.strip(), (code, k, teil)
                assert "<" not in v and "\n" not in v, (code, k, v)
        for k in ("ben.b6_text_wenig", "ben.farbe_blau", "ben.farbe_lila", "ben.farbe_gold"):
            assert eigene.get(k, "").strip(), (code, k)
            assert "{" not in eigene[k], (code, k)


def test_deutsch_wie_freigegeben():
    import sprachen
    de = sprachen.TEXTE["de"]
    assert {k: (de["ben.%s_titel" % k], de["ben.%s_text" % k]) for k in SCHLUESSEL} == DEUTSCH
    assert de["ben.b6_text_wenig"] == "Deine Wörter sind alle noch da. Zmaj wartet ohne Eile."
    assert [de["ben.farbe_" + f] for f in ("blau", "lila", "gold")] == ["blau", "lila", "golden"]


def test_alte_texte_sind_raus(sprachcodes, index_html):
    import sprachen
    for code in sprachcodes:
        alt = [k for k in sprachen.TEXTE[code]
               if re.match(r"ben\.(erinnerung_|serie_|rueckhol_)", k)]
        assert alt == [], (code, alt)
    for k in ("ben.erinnerung_", "ben.serie_titel", "ben.serie_text", "ben.rueckhol_"):
        assert k not in index_html, k
    # Die Leben-Nachricht und die Kanaele bleiben, wie sie sind
    for k in ("ben.leben_titel", "ben.leben_text_3", "ben.kanal", "ben.kanal_leise"):
        assert "'%s'" % k in index_html, k


@pytest.mark.parametrize("k", SCHLUESSEL + ["b6_wenig"])
def test_platzhalter_und_mehrzahl(sprachcodes, k):
    """Nur bekannte Platzhalter, in jeder Sprache dieselben; hoechstens eine
    Zahl je Text. "|" (Einzahl|Mehrzahl) genau dort, wo das Deutsche es hat,
    und dann auf beiden Seiten mit denselben Platzhaltern."""
    import sprachen
    schl = ["ben.b6_text_wenig"] if k == "b6_wenig" else ["ben.%s_titel" % k, "ben.%s_text" % k]
    for s in schl:
        de = sprachen.TEXTE["de"][s]
        soll = set(re.findall(r"\{(\w+)\}", de))
        assert soll <= PLATZHALTER, (s, soll)
        for code in sprachcodes:
            v = sprachen.TEXTE[code][s]
            assert set(re.findall(r"\{(\w+)\}", v)) == soll, (code, s, v)
            assert v.count("|") == de.count("|"), (code, s, v)
            for seite in v.split("|"):
                assert set(re.findall(r"\{(\w+)\}", seite)) == soll, (code, s, seite)
                zahlen = set(re.findall(r"\{(\w+)\}", seite)) & {"n", "ziel", "rekord", "woerter", "tage"}
                assert len(zahlen) <= 1, (code, s, seite)
    # Nur {n} kann 1 sein - genau die Titel mit {n} brauchen die Einzahl.
    titel = sprachen.TEXTE["de"].get("ben.%s_titel" % k, "")
    if k in ("a2", "a3", "a5"):
        assert "{n}" in titel and titel.count("|") == 1
    # {tage} (B1) ist immer mindestens 2: die Mehrzahl ohne "|"
    if k == "b1":
        assert "{tage} Tage" in sprachen.TEXTE["de"]["ben.b1_text"] and "|" not in sprachen.TEXTE["de"]["ben.b1_text"]


@pytest.mark.parametrize("k", SCHLUESSEL)
def test_ton_regeln(sprachcodes, alle_daten, index_html, k):
    """Genau ein Emoji je Titel, keines im Text. Kein "Zmaj:" vorn, keine
    Uhrzeit, keine Grossbuchstaben-Rufe, hoechstens ein "!" je Teil.
    Laenge wie in der Vorlage: Titel bis 30 Zeichen, Text bis 80, mit den
    laengsten echten Werten der
    Sprache. Bis zum 13.11.2026 stand hier 36 und 100 mit ausgedachten
    Werten - so rutschte ein franzoesischer Text mit 87 Zeichen durch."""
    import sprachen
    for code in sprachcodes:
        lang = _laengste_werte(code, alle_daten[code], index_html)
        titel = sprachen.TEXTE[code]["ben.%s_titel" % k]
        text = sprachen.TEXTE[code]["ben.%s_text" % k]
        for seite in titel.split("|"):
            assert len(EMOJI.findall(seite)) == 1, (code, k, seite)
            assert not seite.startswith("Zmaj:"), (code, k, seite)
            voll = re.sub(r"\{(\w+)\}", lambda m: lang[m.group(1)], seite)
            assert len(voll) <= TITEL_BIS, (code, k, len(voll), voll)
            assert seite.count("!") <= 1, (code, k, seite)
        assert not EMOJI.findall(text), (code, k, text)
        voll = re.sub(r"\{(\w+)\}", lambda m: lang[m.group(1)], text)
        assert len(voll) <= TEXT_BIS, (code, k, len(voll), voll)
        assert text.count("!") <= 1, (code, k, text)
        for teil in (titel, text):
            assert not re.search(r"\d{1,2}[:.]\d{2}|\b(19|20) ?(Uhr|pm|h)\b", teil), (code, k, teil)
            assert not re.search(r"\b[A-ZÄÖÜ]{4,}\b", teil.replace("ZMAJ", "")), (code, k, teil)


def test_android_klappt_den_ganzen_text_auf(index_html):
    """Nur mit body setzt das Plugin keinen Stil, dann zeigt Android
    aufgeklappt hoechstens zwei Zeilen (vor Android 12 nur eine). Mit
    largeBody wird es BigTextStyle; zugeklappt bleibt body. Pruefung am
    13.11.2026."""
    rumpf = index_html.split("async function benPlanen(){")[1].split("function zeigeBenFrage(")[0]
    assert "body: p.text, largeBody: p.text," in rumpf


def test_bosnische_stellen_bleiben(sprachcodes):
    import sprachen
    for code in sprachcodes:
        for k, wort in BOSNISCH.items():
            ganz = sprachen.TEXTE[code]["ben.%s_titel" % k] + " " + sprachen.TEXTE[code]["ben.%s_text" % k]
            assert wort in ganz, (code, k, wort)
        a4 = sprachen.TEXTE[code]["ben.a4_titel"].lower()
        assert "inat" in a4.replace("i̇", "i"), (code, a4)


def test_ohne_namen_und_ohne_werbung(sprachcodes):
    """12a: kein Name. Und nichts, was Apple und Google in Nachrichten
    verbieten (Vollversion, Muenzen, andere Apps) oder was Druck macht."""
    import sprachen
    verboten = re.compile(r"\{(name|email|mail)\}|premium|vollversion|full version|münze|coin|"
                          r"faul|lazy|enttäuscht|disappointed|letzte chance|last chance", re.I)
    for code in sprachcodes:
        for k in SCHLUESSEL:
            for teil in ("titel", "text"):
                v = sprachen.TEXTE[code]["ben.%s_%s" % (k, teil)]
                assert not verboten.search(v), (code, k, v)


def test_franzoesisch_mit_geschuetztem_leerzeichen():
    """Wie ueberall im Franzoesischen der App: vor ? ! : und innen in « »
    ein geschuetztes Leerzeichen, nie ein normales."""
    import sprachen
    fr = sprachen.TEXTE["fr"]
    for k in SCHLUESSEL:
        for teil in ("titel", "text"):
            v = fr["ben.%s_%s" % (k, teil)]
            assert not re.search(r" [?!:»]|« ", v), (k, v)


def test_gestrichene_texte_sind_raus(sprachcodes, index_html):
    """Ajdin am 14.11.2026: A1 raus, B4 raus ("diese Benachrichtigung ist
    komisch mach weg"), die Wortwitze D1-D6 raus ("Der Rest raus") - in
    allen Sprachen und im Code, samt der Wortliste fuer {wort}. Kein
    Abendtext kennt {wort} noch."""
    import sprachen
    for code in sprachcodes:
        rest = [k for k in sprachen.TEXTE[code]
                if any(k.startswith("ben.%s_" % g) for g in GESTRICHEN)]
        assert rest == [], (code, rest)
        for k, v in sprachen.TEXTE[code].items():
            if k.startswith("ben."):
                assert "{wort}" not in v, (code, k, v)
    for g in GESTRICHEN:
        assert "'ben.%s_" % g not in index_html, g
        assert "'%s'" % g not in index_html.split("const BEN_TEXTE = {")[1].split("let benLaeuft")[0], g
    for weg in ("BEN_WORTE", "BEN_WITZE", "benGelernt", "w.wort", "wort: w."):
        assert weg not in index_html, weg
    assert "function benWerte(tag, basis){" in index_html


def test_gruppen_wie_am_14_11_entschieden(index_html):
    """Die Wahl nach der Lage (14.11.2026): Serie A2-A5 (+C1/C3, A6 Vorrang),
    gestern gelernt C2/C3/C4/C6 (C5 Vorrang), 2-6 Tage Pause B1/B2/B3/B5,
    alles andere B2 und C4, mit einem Lerntag auch B1 und B5. Wie sie im
    Browser wirkt, pruefen die E2E-Tests."""
    rumpf = index_html.split("function benGruppe(art, w){")[1].split("\n}")[0]
    assert "const pool = ['a2', 'a3'].concat(w.n >= 2 ? ['a4'] : [], ['a5']);" in rumpf
    assert ".concat(w.n >= 7 && w.n >= w.rekord ? ['c3'] : [], ['c4', 'c6']);" in rumpf
    assert "const pool = w.pause > 0 ? ['b1', 'b2'].concat(w.level ? ['b5'] : []) : ['b2'];" in rumpf
    assert "pool.push('c4');" in rumpf


def test_regeln_wie_entschieden(index_html):
    """13a: 19 und 20 Uhr fest, hoechstens eine Nachricht am Abend (eine
    Nummer je Kalendertag), die Rueckhol-Nachricht nach 14 Tagen."""
    assert "const BEN_ERINNERUNG_UM = 19, BEN_SERIE_UM = 20, BEN_TAGE = 7;" in index_html
    assert "const BEN_PAUSE_TAGE = 14, BEN_ID_RUECKHOL = 150, BEN_KANAL_LEISE = 'rueckhol';" in index_html
    assert "const BEN_FARBTAGE = [30, 100, 365];" in index_html
    rumpf = index_html.split("function benPlan(){")[1].split("\nlet benLaeuft")[0]
    assert "plan.push({id: benAbendId(tag), art, wann, titel, text, key});" in rumpf
    assert "const key = benWahl(benGruppe(art, w), tag, zuletzt);" in rumpf
    # Kein Zufall in der Auswahl: zweimal Planen am selben Tag waehlt dasselbe
    auswahl = index_html.split("const BEN_TEXTE = {")[1].split("let benLaeuft")[0]
    assert "Math.random" not in auswahl
