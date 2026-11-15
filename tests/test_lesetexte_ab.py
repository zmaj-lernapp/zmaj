# -*- coding: utf-8 -*-
"""B1-Lesetexte: Ajdins Antworten auf die A/B-Liste (15.11.2026).

Release\\Lesetexte_Fragen_AB.md stellte zu den fraglichen Stellen der neuen
Lesetexte zwei Fassungen zur Wahl: A, wie es im Text stand, und B. Wo Ajdin
B gewählt hat, steht jetzt genau B im Text, mit Übersetzung, Fragen und
Wörterbuch in allen acht Sprachen. Wo er A gewählt hat, bleibt der Text.
Keine dieser Geschichten hat schon Ton: Ein neuer Text ist ein neuer
Ton-Schlüssel, und der steht in tests/offen_lesetexte.json (Pakete 1 und 2),
oder die Geschichte wartet mit ihrer id in tests/offen_b1_teil2.py (Pakete 3
und 4). Im Browser: tests_e2e/test_lesetexte_ab.py.
"""
import io
import json
import os
import re

SPRACHEN = ["en", "tr", "sv", "nl", "nb", "da", "fr"]

# Stelle -> (Geschichte, Satz jetzt (B), Satz vorher (A))
B = {
    "L9": ("b1_dijaspora", "Tarik je naručio deset ćevapa s lukom i jogurt.",
           "Tarik je naručio desetku s lukom i jogurt."),
    "L10": ("b1_vrijeme", "„Dobro veče, dragi slušaoci.", "„Dobro veče, poštovani slušaoci."),
    "L12": ("b1_vrijeme", "„Ako bude sunčano, možemo i roštiljati.“",
            "„Ako bude sunčano, možemo napraviti i roštilj.“"),
    "L16": ("b1_jahorina", "Prvog jutra su iznajmili skije, skijaške cipele i štapove.",
            "Prvog jutra su iznajmili skije, pancerice i štapove."),
    "L18": ("b1_pita", "Nana je stavila tijesto na veliki sto i razvijala ga oklagijom dok nije postalo tanko kao papir.",
            "razvlačila ga rukama"),
    "L19 a": ("b1_pita", "U međuvremenu su pripremile nadjev: oguljile su krompir,", "pripremile fil:"),
    "L19 b": ("b1_pita", "Na kraju su stavile nadjev na tijesto, savile ga i stavile pitu u tepsiju.",
              "stavile fil na tijesto"),
    "L21": ("b1_pita", "Tijesto je trebalo da odmori pola sata.", "Tijesto je moralo odmarati pola sata."),
    "L22": ("b1_struja", "Bilo je hladno januarsko veče.", "Bila je hladna januarska večer."),
    # L24 "ja alle": alle vier Stellen zum Kolo tanzen jetzt (plesati)
    "L24 a": ("b1_svadba", "Plesali smo kolo oko cijele sale, od najmlađih do najstarijih.", "Igrali smo kolo"),
    "L24 b": ("b1_svadba", "Moja nana je, sa svojih osamdeset godina, plesala duže od mene.", "igrala duže od mene"),
    "L24 c": ("b1_svadba", "Toliko sam se najela da više nisam mogla plesati.", "nisam mogla igrati"),
    "L24 d": ("b1_svadba", "Plesali smo i pjevali do tri ujutro.", "Igrali smo i pjevali"),
    "L26": ("b1_posao", "Haris je završio elektrotehnički fakultet i u ponedjeljak je počeo raditi",
            "završio elektrotehniku"),
    "L27": ("b1_posao", "Kolege su bili ljubazni.", "Kolege su bile ljubazne."),
    "L28": ("b1_posao", "„Hajde, kahva je obavezna!“", "„Hajde, kahva je svetinja!“"),
    "L30": ("b1_stan", "Prvu noć je spavala na madracu na podu, ali je bila presretna.", "na dušeku"),
    # T1: Vam groß wie überall, wo EINE Person höflich angeredet wird
    "T1": ("b1_doktor", "Dat ću Vam recept i otvorit ću Vam bolovanje na pet dana.",
           "Dat ću Vam recept, a pet dana ste na bolovanju."),
    "T2": ("b1_doktor", "„Uzimajte jednu tabletu tri puta dnevno, poslije jela.",
           "„Pijte jednu tabletu tri puta dnevno"),
    "T3": ("b1_doktor", "Poslije pet dana Amar je ponovo bio zdrav i vratio se na posao.",
           "Amar je opet bio zdrav"),
    "T5": ("b1_rodjendan", "„Idemo kod tvojih roditelja na večeru.“", "„Idemo kod tvojih na večeru.“"),
    "T6": ("b1_rodjendan", "Haris je ugasio sve svijeće u jednom dahu, a svi su vikali: „Bravo!“",
           "Haris ih je ugasio odjednom"),
    "T7": ("b1_utakmica", "Kenan je grlio oca i ljude koje nikad prije nije vidio.", "Kenan je grlio babu"),
    "T11": ("b1_kahva", "Džezvu vrati na vatru samo na kratko, da se digne kajmak.",
            "Džezvu vrati na vatru samo na kratko. „"),
    "T12": ("b1_mejl", "Naslov: Dolazim u augustu!", "Predmet:"),
    "T14": ("b1_zmaj", "Pustio je malo vatre iz usta, i ćevapi su u sekundi izgorjeli.", "zagorjeli"),
    # T15 genau wie in Ajdins Antwortzeile ("T15 passt")
    "T15": ("b1_zmaj", "Zmaj je bio sit, pa je rekao: „Ne, hvala.“ Nana mu je odmah stavila još tri sarme na "
                       "tanjir. „Ali nano, rekao sam ne, hvala!“ „Čula sam“, rekla je nana. „Kod nane se ne kaže ne.“",
            "Hvala znači"),
}

# Stelle -> (Geschichte, Stelle, die bleibt): hier hat Ajdin A gewählt
A = {
    "L11": ("b1_vrijeme", "Oko podne se očekuje kiša, a poslijepodne i grmljavina."),
    "L13": ("b1_rafting", "Instruktor Mirza im je dao kacige, prsluke i vesla."),
    "L14": ("b1_rafting", "Kad kažem ‚stop‘, prestanite."),
    "L15": ("b1_rafting", "Poslije raftinga su na obali jeli pastrmku."),
    "L17 a": ("b1_jahorina", "Prvog jutra su iznajmili skije,"),
    "L17 b": ("b1_jahorina", "Trećeg dana su se zajedno spustili do hotela."),
    "L17 c": ("b1_pita", "Jednog jutra je rekla nani:"),
    "L20": ("b1_pita", "savile ga i stavile pitu u tepsiju."),
    "L25": ("b1_svadba", "Njegova djevojka Sara je iz Tuzle"),
    "L29": ("b1_stan", "Izdajem jednosoban stan na Grbavici."),
    "T8": ("b1_zanat", "onda se dugo kuca čekićem"),
    "T9": ("b1_zanat", "„Neka je sa srećom!“ rekao je majstor."),
    "T10": ("b1_kahva", "Moja komšinica, teta Safija,"),
    "T13": ("b1_zmaj", "Pustio je malo vatre iz usta"),
    "T16": ("b1_utakmica", "„Babo, kad idemo opet?“ pitao je Kenan."),
}

# Geschichte -> [(deutscher Satz jetzt, deutscher Satz vorher)], nur wo sich
# die Übersetzung ändert
DE = {
    "b1_dijaspora": [("Tarik bestellte zehn Ćevapi mit Zwiebeln und einen Joghurt.",
                      "Tarik bestellte eine Portion mit zehn Ćevapi und Zwiebeln und dazu einen Joghurt.")],
    "b1_pita": [("Oma legte den Teig auf den großen Tisch und rollte ihn mit dem Nudelholz aus, bis er dünn wie Papier war.",
                 "zog ihn mit den Händen aus")],
    "b1_posao": [("„Komm, der Kaffee ist Pflicht!“", "„Komm, der Kaffee ist heilig!“")],
    "b1_doktor": [("Ich gebe Ihnen ein Rezept und schreibe Sie für fünf Tage krank.",
                   "und Sie sind fünf Tage krankgeschrieben")],
    "b1_rodjendan": [("Haris blies alle Kerzen in einem Atemzug aus, und alle riefen: „Bravo!“",
                      "Haris blies sie auf einmal aus")],
    "b1_utakmica": [("Kenan umarmte seinen Vater und Leute, die er noch nie gesehen hatte.", "Kenan umarmte Papa")],
    "b1_kahva": [("Das Kännchen stellt sie nur kurz zurück aufs Feuer, damit der Schaum aufsteigt.",
                  "Das Kännchen stellt sie nur kurz zurück aufs Feuer. „")],
    # Den letzten Satz hat Ajdin selbst übersetzt: „Bei der Oma sagt man nicht nein.“
    "b1_zmaj": [("Zmaj war satt, also sagte er: „Nein, danke.“ Die Oma legte ihm sofort noch drei Sarma auf den "
                 "Teller. „Aber Oma, ich habe nein, danke gesagt!“ „Ich habe es gehört“, sagte die Oma. „Bei der "
                 "Oma sagt man nicht nein.“", "„Danke heißt, dass es dir schmeckt.“"),
                ("die Ćevapi waren in einer Sekunde verbrannt.", "angebrannt")],
}

# Stichprobe: so heißt es jetzt auf Englisch
EN = {
    "b1_dijaspora": "Tarik ordered ten ćevapi with onions and a yogurt.",
    "b1_pita": "Grandma put the dough on the big table and rolled it out with a rolling pin until it was as thin as paper.",
    "b1_posao": "Nedžad came back for him: “Come on, coffee is a must!”",
    "b1_doktor": "I'll give you a prescription and put you on sick leave for five days.",
    "b1_rodjendan": "Haris blew out all the candles in one breath, and everyone shouted: “Bravo!”",
    "b1_utakmica": "Kenan hugged his father and people he had never seen before.",
    "b1_kahva": "She puts the džezva back on the heat only briefly, so that the foam rises.",
    "b1_zmaj": "“But Grandma, I said no, thank you!” “I heard you”, Grandma said. “At Grandma's you don't say no.”",
}

# Neue Formen im Wörterbuch der Lesetexte und ihre Bedeutung
NEU = {
    "ćevapa": "Ćevapi (Gen.)",
    "roštiljati": "grillen",
    "skijaške": "Ski- (skijaške cipele: Skischuhe)",
    "cipele": "Schuhe",
    "razvijala": "ausgerollt (w)",
    "oklagijom": "Nudelholz (Instr.)",
    "nadjev": "Füllung",
    "odmori": "ruht (sich) aus",
    "hladno": "kalt (s)",
    "januarsko": "Januar- (s)",
    "veče": "Abend",
    "plesala": "getanzt (w)",
    "plesati": "tanzen",
    "elektrotehnički": "Elektrotechnik- (elektrotehnički fakultet: Fakultät für Elektrotechnik)",
    "fakultet": "Fakultät (Studium)",
    "ljubazni": "freundlich (Mehrz.)",
    "obavezna": "Pflicht / verpflichtend (w)",
    "madracu": "Matratze (Lok.)",
    "otvorit": "öffnen (otvorit ću bolovanje: ich schreibe krank)",
    "bolovanje": "Krankschreibung (Akk.)",
    "uzimajte": "nehmen Sie (Befehl)",
    "ponovo": "wieder / erneut",
    "tvojih": "deiner (Gen. Mehrz.)",
    "roditelja": "Eltern (Gen.)",
    "svijeće": "Kerzen",
    "dahu": "Atem (Lok.) (u jednom dahu: in einem Atemzug)",
    # in Stari zanat "od oca" (Gen.), in Utakmica "grlio oca" (Akk.)
    "oca": "Vater (Gen./Akk.)",
    "digne": "hebt (se digne: steigt auf)",
    "kajmak": "Schaum (auf dem Kaffee) / Kajmak",
    "naslov": "Betreff / Titel",
    "izgorjeli": "verbrannt (Mehrz.)",
}

# Formen, die in keinem Text mehr stehen und deshalb aus dem Wörterbuch raus sind
RAUS = ["desetku", "poštovani", "roštilj", "pancerice", "razvlačila", "rukama", "fil", "moralo",
        "januarska", "večer", "igrati", "elektrotehniku", "svetinja", "dušeku", "bolovanju", "ih", "babu",
        "predmet", "zagorjeli", "znači", "ukusno"]

# Deutsche Texte, die mit ihnen aus uebersetzungen.py gegangen sind
RAUS_TEXTE = ["zehn Ćevapi (Portion, Akk.)", "sehr geehrte", "Skischuhe", "gezogen / gedehnt (w)", "Hände (Instr.)",
              "Januar- (w)", "tanzen / spielen", "Elektrotechnik (Akk.)", "Heiligtum", "Krankschreibung (Lok.)",
              "auf einmal", "deinen (kod tvojih: bei deinen Eltern)", "sie (Akk. Mehrz.)", "Papa (Akk.)",
              "Vater (Gen.)", "Betreff", "angebrannt (Mehrz.)", "es bedeutet", "Was bedeutet „Hvala“ für die Oma?",
              "dass es ihm schmeckt", "dass er satt ist", "dass er schlafen will", "sie brennen an"]

# (Geschichte, Wort) -> Bedeutung in den vokabeln der Geschichte. "dragi
# slušaoci" ist Mehrzahl, im WOERTERBUCH bleibt "lieber" ("Dragi Adnane").
VOKABELN = {
    ("b1_vrijeme", "dragi"): "liebe (Mehrz.)",
    # "Tijesto je trebalo da odmori": musste; im WOERTERBUCH "gebraucht (s)" aus b1_posao
    ("b1_pita", "trebalo"): "musste (s)",
    # "ugasio sve svijeće": alle; im WOERTERBUCH "alles"
    ("b1_rodjendan", "sve"): "alle (sve svijeće: alle Kerzen)",
    # „Ne, hvala.“, „Kod nane se ne kaže ne.“: nein; im WOERTERBUCH "nicht"
    ("b1_zmaj", "ne"): "nicht / nein",
}


def _geschichten(daten):
    return {g["id"]: g for g in daten["geschichten"]}


def _geaendert():
    return sorted({gid for gid, _, _ in B.values()})


def test_b_steht_genau_so_im_text(grunddaten):
    g = _geschichten(grunddaten)
    for stelle, (gid, jetzt, vorher) in B.items():
        assert jetzt in g[gid]["text"], (stelle, jetzt)
        assert vorher not in g[gid]["text"], (stelle, vorher)


def test_a_bleibt(grunddaten):
    g = _geschichten(grunddaten)
    for stelle, (gid, satz) in A.items():
        assert satz in g[gid]["text"], (stelle, satz)


def test_deutsche_uebersetzung(grunddaten):
    g = _geschichten(grunddaten)
    for gid, paare in DE.items():
        for jetzt, vorher in paare:
            assert jetzt in g[gid]["uebersetzung"], (gid, jetzt)
            assert vorher not in g[gid]["uebersetzung"], (gid, vorher)


def test_uebersetzt_in_allen_sprachen(alle_daten):
    """Jede Sprache hat die neue Übersetzung (sonst stünde dort der deutsche
    Text), Bosnisch bleibt bosnisch (AGENTS.md, Regel 2)."""
    de = _geschichten(alle_daten["de"])
    for code in SPRACHEN:
        g = _geschichten(alle_daten[code])
        for gid in _geaendert():
            assert g[gid]["text"] == de[gid]["text"], (code, gid)
            assert g[gid]["uebersetzung"] != de[gid]["uebersetzung"], (code, gid)
            assert len(g[gid]["uebersetzung"].split("\n\n")) == len(de[gid]["text"].split("\n\n")), (code, gid)
            for f, f_de in zip(g[gid]["fragen"], de[gid]["fragen"]):
                assert f["frage"] != f_de["frage"] and f["richtig"] in f["optionen"], (code, gid)
    en = _geschichten(alle_daten["en"])
    for gid, satz in EN.items():
        assert satz in en[gid]["uebersetzung"], (gid, satz)


def test_woerterbuch(alle_daten):
    """Jede neue Form lässt sich antippen, in jeder Sprache mit eigener
    Bedeutung; die alten sind raus, ihre Übersetzungen auch."""
    import uebersetzungen
    wb = alle_daten["de"]["woerterbuch"]
    for wort, bedeutung in NEU.items():
        assert wb.get(wort) == bedeutung, wort
    for code in SPRACHEN:
        wbc = alle_daten[code]["woerterbuch"]
        for wort in NEU:
            assert wbc[wort].strip() and wbc[wort] != wb[wort], (code, wort, wbc[wort])
        texte = uebersetzungen.INHALT[code]["texte"]
        assert [t for t in RAUS_TEXTE if t in texte] == [], code
    for code, daten in alle_daten.items():
        assert [w for w in RAUS if w in daten["woerterbuch"]] == [], code


def test_l24_kolo_wird_ueberall_getanzt(grunddaten):
    """Ajdin zu L24: "ja alle". In Svadba i kolo wird nur noch getanzt
    (plesati); igrati steht in keiner Form mehr dort, in Utakmica und
    Komšiluk bez struje spielen sie weiter (igrali, igrala)."""
    g = _geschichten(grunddaten)
    svadba = {w.lower() for w in re.findall(r"[^\W\d_]+", g["b1_svadba"]["text"])}
    assert not {w for w in svadba if w.startswith("igr")}
    assert {"plesali", "plesala", "plesati"} <= svadba
    assert "naši su igrali mnogo bolje" in g["b1_utakmica"]["text"]
    assert "Djeca su se igrala u hodniku" in g["b1_struja"]["text"]


def test_t6_odjednom_nur_noch_ploetzlich(grunddaten):
    """odjednom steht nur noch in Komšiluk bez struje ("plötzlich");
    Rođendansko iznenađenje braucht seinen Eintrag "auf einmal" nicht mehr."""
    g = _geschichten(grunddaten)
    assert "odjednom" not in g["b1_rodjendan"]["vokabeln"]
    assert "odjednom" not in g["b1_rodjendan"]["text"]
    assert "kad je odjednom nestalo struje" in g["b1_struja"]["text"]
    assert grunddaten["woerterbuch"]["odjednom"] == "plötzlich"


def test_t12_betreff_bleibt_auf_deutsch(alle_daten):
    """Naslov statt Predmet; die Übersetzung bleibt "Betreff" (Subject, Konu ...)."""
    g = _geschichten(alle_daten["de"])["b1_mejl"]
    assert g["text"].startswith("Naslov: Dolazim u augustu!\n\n")
    assert g["uebersetzung"].startswith("Betreff: Ich komme im August!\n\n")
    assert _geschichten(alle_daten["en"])["b1_mejl"]["uebersetzung"].startswith("Subject: I'm coming in August!")


# S7: "lass doktor vorher" - Izgubljeni telefon hinter Kod doktora und Dedo i
# nana se sele, wie in Ajdins Themenliste
B1_REIHE = ["b1_ljeto", "b1_dijaspora", "b1_vrijeme", "b1_voz", "b1_rafting", "b1_jahorina", "b1_pita",
            "b1_struja", "b1_svadba", "b1_posao", "b1_stan", "b1_doktor", "b1_selidba", "b1_telefon",
            "b1_rodjendan", "b1_utakmica", "b1_zanat", "b1_kahva", "b1_mejl", "b1_zmaj"]


def test_s7_telefon_hinter_doktor_und_selidba(alle_daten):
    """Nur die Reihenfolge ändert sich: Text, id, Stufe und passt_zu bleiben,
    in jeder Sprache dieselbe Kette. Frei wird eine Geschichte, wenn die davor
    gelesen ist (storyUnlocked in web/index.html); der Lesestand hängt an der id."""
    for code, daten in alle_daten.items():
        ids = [g["id"] for g in daten["geschichten"]]
        assert [i for i in ids if i.startswith("b1_")] == B1_REIHE, code
        assert ids[-len(B1_REIHE):] == B1_REIHE, code
    g = _geschichten(alle_daten["de"])["b1_telefon"]
    assert g["titel"] == "Izgubljeni telefon" and g["stufe"] == "B1" and g["passt_zu"] == "geraete"


def test_s7_testdaten_in_der_neuen_reihenfolge(wurzel):
    """Die Sicherungen zum Durchtesten führen die gelesenen Geschichten in der
    Reihenfolge der App (testdaten_bauen.py)."""
    for name in ("zmaj-test-alles-offen.json", "zmaj-test-vollversion.json"):
        stand = json.load(io.open(os.path.join(wurzel, "testdaten", name), encoding="utf-8"))["stand"]
        gelesen = [i for i in stand["gelesen"] if i.startswith("b1_")]
        assert gelesen == B1_REIHE, name


ZMAJ_FRAGEN = [
    ("Welchen Fehler macht Zmaj, als er ankommt?",
     ["er sagt am Abend „Dobro jutro“", "er vergisst den Namen der Oma", "er kommt zu spät"]),
    ("Warum bekommt Zmaj trotzdem noch mehr Sarma?",
     ["bei der Oma sagt man nicht nein", "die Oma hat ihn nicht gehört", "er hat um mehr Sarma gebeten"]),
    ("Was passiert mit den Ćevapi?", ["sie verbrennen", "sie werden kalt", "der Hund frisst sie"]),
]


def test_t15_die_fragen_folgen_dem_neuen_witz(alle_daten):
    """Die zweite Frage fragte, was "Hvala" für die Oma bedeutet; das gibt
    es nicht mehr. Jetzt: warum Zmaj trotzdem mehr Sarma bekommt. Die dritte
    sagt "verbrennen" wie T14. Die richtige Antwort steht vorn und ist in
    keiner Sprache die einzige lange."""
    de = _geschichten(alle_daten["de"])["b1_zmaj"]
    assert [(f["frage"], f["optionen"]) for f in de["fragen"]] == ZMAJ_FRAGEN
    assert [f["richtig"] for f in de["fragen"]] == [o[0] for _, o in ZMAJ_FRAGEN]
    for code in SPRACHEN:
        g = _geschichten(alle_daten[code])["b1_zmaj"]
        for f, f_de in zip(g["fragen"], de["fragen"]):
            assert f["richtig"] == f["optionen"][0], code
            assert all(o != o_de for o, o_de in zip(f["optionen"], f_de["optionen"])), (code, f["optionen"])
            falsch = [o for o in f["optionen"] if o != f["richtig"]]
            assert len(f["richtig"]) <= 14 or any(len(o) > 14 for o in falsch), (code, f["optionen"])
    en = _geschichten(alle_daten["en"])["b1_zmaj"]["fragen"][1]
    assert en["frage"] == "Why does Zmaj still get more sarma?"
    assert en["richtig"] == "at Grandma's you don't say no"


def test_alte_formen_stehen_in_keinem_text(grunddaten):
    woerter = {w.lower() for g in grunddaten["geschichten"] for w in re.findall(r"[^\W\d_]+", g["text"])}
    assert sorted(set(RAUS) & woerter) == []
    assert sorted(set(NEU) - woerter) == []


def test_vokabeln_der_geschichten(alle_daten):
    de = _geschichten(alle_daten["de"])
    for (gid, wort), bedeutung in VOKABELN.items():
        assert de[gid]["vokabeln"][wort] == bedeutung, (gid, wort)
        for code in SPRACHEN:
            v = _geschichten(alle_daten[code])[gid]["vokabeln"][wort]
            assert v.strip() and v != bedeutung, (code, gid, wort)


def test_wartet_auf_ton(wurzel):
    """Neuer Text, neuer Schlüssel: Die Geschichte wartet weiter auf Vesna,
    und jedes neue Wort ohne Aufnahme steht in einer der beiden Listen."""
    import geschichten
    import offen_b1_teil2
    import offen_lesetexte
    import ton_bauen
    index = {e["key"] for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                 encoding="utf-8"))["toene"]}
    g = {s["id"]: s for s in geschichten.GESCHICHTEN}
    teil2 = offen_b1_teil2.ton_schluessel()
    for gid in _geaendert():
        k = ton_bauen.schluessel(g[gid]["text"])
        assert k not in index, gid
        assert k in offen_lesetexte.GESCHICHTEN or gid in offen_b1_teil2.GESCHICHTEN, gid
    for wort in NEU:
        k = ton_bauen.schluessel(wort)
        if k not in index and k not in ton_bauen.nur_emir():
            assert k in offen_lesetexte.TON or k in teil2, wort
    assert not set(RAUS) & offen_lesetexte.TON
