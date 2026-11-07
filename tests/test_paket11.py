# -*- coding: utf-8 -*-
"""Wortschatz-Paket 11 (07.11.2026): Sektion 19 · Menschen und Beziehungen.

149 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_11.json, b2_entscheidungen.md). Hier steht, was beim
Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- odgoj, odgojiti, odgajati statt vaspitanje (zaehlt nicht), krivica, prevara, nesretan,
  saučešće wie von Ajdin gewaehlt;
- opraštati und upoznavati sind die Gegenstuecke zu oprostiti und upoznati aus der App,
  "partner" steht jetzt an beiden;
- unuk und unuka sehen im Akkusativ gleich aus: NIE_NEBENEINANDER.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["erziehung_aufwachsen", "familie_generationen", "liebe_ehe", "streit_versoehnung",
         "reue_enttaeuschung", "gefuehle_genauer", "charakter", "trauer_beileid", "begegnen_versammeln",
         "nachbarn_miteinander"]
SEKTION = {
    "erziehung_aufwachsen": "menschenbeziehungen", "familie_generationen": "menschenbeziehungen",
    "liebe_ehe": "menschenbeziehungen", "streit_versoehnung": "menschenbeziehungen",
    "reue_enttaeuschung": "menschenbeziehungen", "gefuehle_genauer": "menschenbeziehungen",
    "charakter": "menschenbeziehungen", "trauer_beileid": "menschenbeziehungen",
    "begegnen_versammeln": "menschenbeziehungen", "nachbarn_miteinander": "menschenbeziehungen",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "erziehung_aufwachsen": ["odgoj", "odgojiti", "odgajati", "uzor", "disciplina", "omladina", "vršnjak",
                             "maloljetnik", "igračka", "odrasti", "odrastati", "nagraditi", "nagrađivati",
                             "pohvala", "školovanje"],
    "familie_generationen": ["dom", "porijeklo", "generacija", "predak", "rodbina", "domaćinstvo", "starac",
                             "unuk", "unuka", "blizanac", "trudnica", "udovica", "kum", "zet", "snaha",
                             "svekrva", "svekar", "punica", "punac"],
    "liebe_ehe": ["ljepota", "strast", "vjenčanje", "vjenčati se", "zagrljaj", "poljubac", "ljubomora",
                  "ljubavni", "bračni", "supružnik", "vjeran", "nježan", "privlačan", "zabavljati se",
                  "vjeridba"],
    "streit_versoehnung": ["ljutnja", "bijes", "uvreda", "vrijeđati", "uvrijediti", "nesporazum", "tuča",
                           "napetost", "pomirenje", "pomiriti se", "miriti se", "opraštati"],
    "reue_enttaeuschung": ["kajati se", "pokajati se", "sramota", "stidjeti se / stiditi se", "krivica",
                           "prevara", "varati", "prevariti", "nervirati", "iznervirati", "razočarati",
                           "razočaranje"],
    "gefuehle_genauer": ["zadovoljstvo", "emocija", "očekivanje", "ponos", "ponositi se", "zahvalnost",
                         "nezadovoljstvo", "panika", "samopouzdanje", "doživljaj", "uzbuđenje", "olakšanje",
                         "dosada", "oduševiti", "oduševljavati", "obradovati"],
    "charakter": ["ponašanje", "osobina", "mudrost", "slabost", "mana", "dostojanstvo", "strpljenje",
                  "skroman", "pravedan", "plemenit", "jadan", "nesretan", "mudar", "odlučan", "razuman",
                  "zreo", "zaslužiti", "zasluživati"],
    "trauer_beileid": ["preminuti", "patnja", "tragedija", "žalost", "grob", "uspomena", "stradanje",
                       "pokojni", "rahmetli", "utjeha", "utješiti", "tješiti", "komemoracija", "nišan",
                       "saučešće", "suosjećanje"],
    "begegnen_versammeln": ["susret", "naselje", "kontakt", "okupljanje", "okupiti", "okupljati", "dočekati",
                            "dočekivati", "pridružiti se", "pridruživati se", "susresti", "susretati",
                            "susjedni"],
    "nachbarn_miteinander": ["dvorište", "mještanin", "sugrađanin", "solidarnost", "zajedništvo", "ugostiti",
                             "suživot", "komšiluk", "upoznavati", "posvetiti", "posvećivati", "odvojiti",
                             "odvajati"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu.
NUR_SATZ = set()

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "ljubavni": ["ljubavna", "ljubavno"], "bračni": ["bračna", "bračno"], "vjeran": ["vjerna", "vjerno"],
    "nježan": ["nježna", "nježno"], "privlačan": ["privlačna", "privlačno"], "vjeridba": ["zaruke"],
    "razočaranje": ["razočarenje"], "skroman": ["skromna", "skromno"], "pravedan": ["pravedna", "pravedno"],
    "plemenit": ["plemenita", "plemenito"], "jadan": ["jadna", "jadno"], "nesretan": ["nesretna", "nesretno"],
    "mudar": ["mudra", "mudro"], "odlučan": ["odlučna", "odlučno"], "razuman": ["razumna", "razumno"],
    "zreo": ["zrela", "zrelo"], "pokojni": ["pokojna", "pokojno"], "suosjećanje": ["saosjećanje"],
    "susresti": ["sresti"], "susretati": ["sretati"], "susjedni": ["susjedna", "susjedno"],
    "komšiluk": ["susjedstvo"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "odgoj": ["vaspitanje"], "odgojiti": ["vaspitati"], "odgajati": ["vaspitavati"], "krivica": ["krivnja"],
    "prevara": ["prijevara"], "nesretan": ["nesrećan"], "saučešće": ["sućut"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "odgojiti": "odgajati", "odgajati": "odgojiti", "odrasti": "odrastati", "odrastati": "odrasti",
    "nagraditi": "nagrađivati", "nagrađivati": "nagraditi", "vrijeđati": "uvrijediti",
    "uvrijediti": "vrijeđati", "pomiriti se": "miriti se", "miriti se": "pomiriti se",
    "opraštati": "oprostiti", "kajati se": "pokajati se", "pokajati se": "kajati se", "varati": "prevariti",
    "prevariti": "varati", "nervirati": "iznervirati", "iznervirati": "nervirati",
    "oduševiti": "oduševljavati", "oduševljavati": "oduševiti", "zaslužiti": "zasluživati",
    "zasluživati": "zaslužiti", "utješiti": "tješiti", "tješiti": "utješiti", "okupiti": "okupljati",
    "okupljati": "okupiti", "dočekati": "dočekivati", "dočekivati": "dočekati",
    "pridružiti se": "pridruživati se", "pridruživati se": "pridružiti se", "susresti": "susretati",
    "susretati": "susresti", "upoznavati": "upoznati", "posvetiti": "posvećivati", "posvećivati": "posvetiti",
    "odvojiti": "odvajati", "odvajati": "odvojiti",
}


def test_alte_verben_haben_ihr_gegenstueck(grunddaten):
    w = {x["bs"]: x for k in grunddaten["kategorien"] for x in k["words"]}
    assert w["oprostiti"]["partner"] == "opraštati" and w["opraštati"]["partner"] == "oprostiti"
    assert w["upoznati"]["partner"] == "upoznavati" and w["upoznavati"]["partner"] == "upoznati"


def test_unuk_und_unuka_nie_nebeneinander(index_html):
    assert "['unuk', 'unuka']" in index_html
