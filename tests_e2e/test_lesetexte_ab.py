# -*- coding: utf-8 -*-
"""B1-Lesetexte im Browser: Ajdins Antworten auf die A/B-Liste (15.11.2026).

Die Geschichte zeigt die neue Fassung, die Übersetzung darunter passt dazu,
und jedes neue Wort hat beim Antippen seine Bedeutung, auf Deutsch und auf
Englisch. Die Regeln dahinter prüft tests/test_lesetexte_ab.py.
"""
import pytest

# Ein Wort in einer Geschichte antippen wie mit dem Finger: das erste "wort",
# dessen Vorgänger "davor" ist. Zurück kommt die Bedeutung in der Blase.
TIPPEN = r"""([gid, davor, wort]) => {
  const i = STORIES.findIndex(s => s.id === gid);
  openStory(i); stilleBitte();
  const ws = [...document.querySelectorAll('#rBody .txt .w')];
  const k = ws.findIndex((w, n) => n > 0 && w.textContent.toLowerCase() === wort
                                  && ws[n - 1].textContent.toLowerCase() === davor);
  if(k < 0) return null;
  ws[k].click();
  const b = document.getElementById('rBubble');
  const fett = b.querySelector('b');
  return {hidden: b.hidden, wort: fett ? fett.textContent : '',
          bedeutung: b.textContent.slice(fett ? fett.textContent.length : 0).trim()};
}"""

# Was die Geschichte zeigt: Text und Übersetzung, wie sie im Bildschirm stehen
ZEIGEN = r"""(gid) => {
  const i = STORIES.findIndex(s => s.id === gid);
  openStory(i); stilleBitte();
  return {text: document.querySelector('#rBody .txt').textContent,
          trans: document.getElementById('rTransText').textContent};
}"""

# (Geschichte, Wort davor, Wort) -> Bedeutung auf Deutsch und Englisch
FAELLE = {
    ("b1_dijaspora", "deset", "ćevapa"): ("Ćevapi (Gen.)", "ćevapi (gen.)"),
    ("b1_vrijeme", "veče", "dragi"): ("liebe (Mehrz.)", "dear (pl.)"),
    ("b1_vrijeme", "i", "roštiljati"): ("grillen", "to grill / to barbecue"),
    ("b1_jahorina", "skije", "skijaške"): ("Ski- (skijaške cipele: Skischuhe)", "ski (skijaške cipele: ski boots)"),
    ("b1_jahorina", "skijaške", "cipele"): ("Schuhe", "shoes"),
    ("b1_pita", "ga", "oklagijom"): ("Nudelholz (Instr.)", "rolling pin (instr.)"),
    ("b1_pita", "pripremile", "nadjev"): ("Füllung", "filling"),
    ("b1_pita", "je", "trebalo"): ("musste (s)", "had to (n)"),
    ("b1_pita", "da", "odmori"): ("ruht (sich) aus", "rests"),
    ("b1_struja", "je", "hladno"): ("kalt (s)", "cold (n)"),
    ("b1_struja", "hladno", "januarsko"): ("Januar- (s)", "January (n)"),
    ("b1_struja", "januarsko", "veče"): ("Abend", "evening"),
    ("b1_svadba", "godina", "plesala"): ("getanzt (w)", "danced (f)"),
    ("b1_svadba", "mogla", "plesati"): ("tanzen", "to dance"),
    ("b1_posao", "završio", "elektrotehnički"): ("Elektrotechnik- (elektrotehnički fakultet: Fakultät für Elektrotechnik)",
                                                 "electrical engineering (elektrotehnički fakultet: "
                                                 "faculty of electrical engineering)"),
    ("b1_posao", "elektrotehnički", "fakultet"): ("Fakultät (Studium)", "faculty (university)"),
    ("b1_posao", "bili", "ljubazni"): ("freundlich (Mehrz.)", "friendly (pl.)"),
    ("b1_posao", "je", "obavezna"): ("Pflicht / verpflichtend (w)", "a must / compulsory (f)"),
    ("b1_stan", "na", "madracu"): ("Matratze (Lok.)", "mattress (loc.)"),
    ("b1_doktor", "i", "otvorit"): ("öffnen (otvorit ću bolovanje: ich schreibe krank)",
                                    "to open (otvorit ću bolovanje: I'll put you on sick leave)"),
    ("b1_doktor", "vam", "bolovanje"): ("Krankschreibung (Akk.)", "sick leave (acc.)"),
    ("b1_doktor", "rekao", "uzimajte"): ("nehmen Sie (Befehl)", "take (formal, imperative)"),
    ("b1_doktor", "je", "ponovo"): ("wieder / erneut", "again / once more"),
    ("b1_rodjendan", "kod", "tvojih"): ("deiner (Gen. Mehrz.)", "your (gen. pl.)"),
    ("b1_rodjendan", "ugasio", "sve"): ("alle (sve svijeće: alle Kerzen)", "all (sve svijeće: all the candles)"),
    ("b1_rodjendan", "jednom", "dahu"): ("Atem (Lok.) (u jednom dahu: in einem Atemzug)",
                                        "breath (loc.) (u jednom dahu: in one breath)"),
    ("b1_utakmica", "grlio", "oca"): ("Vater (Gen./Akk.)", "father (gen./acc.)"),
    ("b1_zanat", "od", "oca"): ("Vater (Gen./Akk.)", "father (gen./acc.)"),
    ("b1_kahva", "se", "digne"): ("hebt (se digne: steigt auf)", "lifts (se digne: rises)"),
    ("b1_kahva", "digne", "kajmak"): ("Schaum (auf dem Kaffee) / Kajmak", "foam (on the coffee) / kajmak"),
    ("b1_zmaj", "sekundi", "izgorjeli"): ("verbrannt (Mehrz.)", "burnt (pl.)"),
    ("b1_zmaj", "sam", "ne"): ("nicht / nein", "not / no"),
    ("b1_zmaj", "kaže", "ne"): ("nicht / nein", "not / no"),
}

# Das erste Wort einer Geschichte antippen (TIPPEN braucht ein Wort davor)
ERSTES = r"""(gid) => {
  const i = STORIES.findIndex(s => s.id === gid);
  openStory(i); stilleBitte();
  const w = document.querySelector('#rBody .txt .w');
  w.click();
  const b = document.getElementById('rBubble');
  const fett = b.querySelector('b');
  return {hidden: b.hidden, wort: fett ? fett.textContent : '',
          bedeutung: b.textContent.slice(fett ? fett.textContent.length : 0).trim()};
}"""

# Geschichte -> (erstes Wort, Bedeutung auf Deutsch, auf Englisch)
ERSTE_WOERTER = {
    "b1_mejl": ("Naslov", "Betreff / Titel", "subject / title"),
}

# Geschichte -> (bosnisch jetzt, deutsch jetzt, englisch jetzt)
ZU_SEHEN = {
    "b1_dijaspora": ("Tarik je naručio deset ćevapa s lukom i jogurt.",
                     "Tarik bestellte zehn Ćevapi mit Zwiebeln und einen Joghurt.",
                     "Tarik ordered ten ćevapi with onions and a yogurt."),
    "b1_vrijeme": ("Ako bude sunčano, možemo i roštiljati.",
                   "Wenn es sonnig ist, können wir auch grillen.",
                   "If it's sunny, we can have a barbecue too."),
    "b1_pita": ("razvijala ga oklagijom dok nije postalo tanko kao papir.",
                "rollte ihn mit dem Nudelholz aus, bis er dünn wie Papier war.",
                "rolled it out with a rolling pin until it was as thin as paper."),
    "b1_struja": ("Bilo je hladno januarsko veče.", "Es war ein kalter Januarabend.",
                  "It was a cold January evening."),
    "b1_svadba": ("Plesali smo kolo oko cijele sale", "Wir tanzten Kolo durch den ganzen Saal",
                  "We danced the kolo around the whole hall"),
    "b1_posao": ("„Hajde, kahva je obavezna!“", "„Komm, der Kaffee ist Pflicht!“", "“Come on, coffee is a must!”"),
    "b1_doktor": ("Dat ću Vam recept i otvorit ću Vam bolovanje na pet dana.",
                  "Ich gebe Ihnen ein Rezept und schreibe Sie für fünf Tage krank.",
                  "I'll give you a prescription and put you on sick leave for five days."),
    "b1_rodjendan": ("Haris je ugasio sve svijeće u jednom dahu",
                     "Haris blies alle Kerzen in einem Atemzug aus",
                     "Haris blew out all the candles in one breath"),
    "b1_utakmica": ("Kenan je grlio oca i ljude", "Kenan umarmte seinen Vater und Leute",
                    "Kenan hugged his father and people"),
    "b1_kahva": ("Džezvu vrati na vatru samo na kratko, da se digne kajmak.",
                 "Das Kännchen stellt sie nur kurz zurück aufs Feuer, damit der Schaum aufsteigt.",
                 "She puts the džezva back on the heat only briefly, so that the foam rises."),
    "b1_mejl": ("Naslov: Dolazim u augustu!", "Betreff: Ich komme im August!", "Subject: I'm coming in August!"),
    "b1_zmaj": ("„Čula sam“, rekla je nana. „Kod nane se ne kaže ne.“",
                "„Ich habe es gehört“, sagte die Oma. „Bei der Oma sagt man nicht nein.“",
                "“I heard you”, Grandma said. “At Grandma's you don't say no.”"),
}


@pytest.mark.parametrize("sprache,spalte", [("de", 0), ("en", 1)])
def test_neue_woerter_beim_antippen(seite, heute_stand, sprache, spalte):
    seite.starten(sprache=sprache, stand=heute_stand())
    falsch = []
    for (gid, davor, wort), bedeutung in FAELLE.items():
        r = seite.js(TIPPEN, [gid, davor, wort])
        assert r is not None, (gid, davor, wort)
        if r["hidden"] or r["wort"].lower() != wort or r["bedeutung"] != bedeutung[spalte]:
            falsch.append((gid, wort, r, bedeutung[spalte]))
    assert falsch == []
    assert seite.fehler == []


@pytest.mark.parametrize("sprache,spalte", [("de", 1), ("en", 2)])
def test_neue_fassung_und_uebersetzung(seite, heute_stand, sprache, spalte):
    seite.starten(sprache=sprache, stand=heute_stand())
    falsch = []
    for gid, saetze in ZU_SEHEN.items():
        r = seite.js(ZEIGEN, gid)
        if saetze[0] not in r["text"] or saetze[spalte] not in r["trans"]:
            falsch.append((gid, saetze[0], saetze[spalte]))
    assert falsch == []
    assert seite.fehler == []


def test_s7_telefon_kommt_nach_doktor(seite, heute_stand):
    """"Izgubljeni telefon" steht hinter "Kod doktora" (S7). Bis zum 17.11.2026 auch
    hinter "Dedo i nana se sele"; seitdem stehen die B1-Texte von leicht nach schwer,
    und das Telefon kommt nach "Dijaspora prvi put u Sarajevu", vor "Dedo i nana se
    sele". Frei wird es, sobald die davor gelesen ist - oder, wie vorher, "Dedo i
    nana se sele" (GESCH_ALTE_FOLGE in storyUnlocked)."""
    seite.starten(stand=heute_stand())
    r = seite.js("""() => {
      const ids = STORIES.map(s => s.id), i = ids.indexOf('b1_telefon');
      const vorher = storyUnlocked(i);
      read.add('b1_dijaspora');
      const neu = [storyUnlocked(i), storyUnlocked(i + 1)];
      read.clear(); read.add('b1_selidba');
      return {nachbarn: ids.slice(i - 3, i + 2), doktor: ids.indexOf('b1_doktor') < i, vorher: vorher,
              neu: neu, alt: storyUnlocked(i)}; }""")
    assert r["nachbarn"] == ["b1_pita", "b1_kahva", "b1_dijaspora", "b1_telefon", "b1_selidba"], r
    assert r["doktor"] and r["vorher"] is False and r["neu"] == [True, False] and r["alt"] is True, r
    assert seite.fehler == []


@pytest.mark.parametrize("sprache,spalte", [("de", 1), ("en", 2)])
def test_erstes_wort_beim_antippen(seite, heute_stand, sprache, spalte):
    seite.starten(sprache=sprache, stand=heute_stand())
    for gid, (wort, *bedeutung) in ERSTE_WOERTER.items():
        r = seite.js(ERSTES, gid)
        assert not r["hidden"] and r["wort"] == wort, (gid, r)
        assert r["bedeutung"] == bedeutung[spalte - 1], (gid, r)
    assert seite.fehler == []
