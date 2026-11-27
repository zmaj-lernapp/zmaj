# -*- coding: utf-8 -*-
"""K2 und K7 in 1.5 (eingebaut am 27.11.2026): neue Woerter, Ordnungszahlen, Tipp-Paare,
Hose und Geschaeft.

Ajdin am 20.11.2026: „mach gleich alle und lass emir direkt alle sprechen“ (97 neue
Woerter, 66 mit Beispielsatz) und zu den Ordnungszahlen O-F1 bis O-F4: alles ja. Am
25.11.2026 zu Hose und Geschaeft: „pantalone / hlače“ wie kahva / kafa, radnja „Geschäft
(kleiner Laden)“ und trgovina „Geschäft (großer Laden)“ (Variante A); radnja, trgovina und
prodavnica zaehlen beim Tippen fuereinander, bei „Laden“ bleibt alles, und bei „Handel“
(auch trgovina) zaehlt keins davon. Was genau dazukam, steht in tests/k2_einbau.py; den
Ablauf in der App prueft tests_e2e/test_k2.py.
"""
import json
import re
import shutil
import subprocess

import pytest

import k2_einbau as K2

LANGS = ("en", "tr", "sv", "nl", "nb", "da", "fr")
# Seit K2 groesser als die 40 Eintraege, die die Wortschatz-Pakete je Level vorsahen. Die
# Woerter gehoeren nach den finalen Listen in diese Level; teilen hiesse neue Level, und die
# hat niemand entschieden. Waechst eins weiter, schlaegt der Test an.
GROSS = {"routine": 41, "sport": 50, "familie_generationen": 56, "liebe_ehe": 42, "klima_energie": 44}


def _level(daten):
    return {k["id"]: k for k in daten["kategorien"]}


def _alle(daten):
    return [w for k in daten["kategorien"] for w in k["words"]]


def test_jedes_neue_wort_steht_genau_einmal_in_seinem_level(grunddaten):
    lv = _level(grunddaten)
    alle = [w["id"] for w in _alle(grunddaten)]
    for lid, liste in K2.WOERTER.items():
        ids = [w["id"] for w in lv[lid]["words"]]
        nach_id = {w["id"]: w for w in lv[lid]["words"]}
        for de, bs, auch, satz in liste:
            k = K2.kennung(de, bs)
            assert alle.count(k) == 1 and k in ids, (lid, k)
            assert (nach_id[k].get("auch") or []) == auch, k
            if satz:
                # der Satz steht direkt hinter seinem Wort
                assert ids[ids.index(k) + 1] == K2.kennung(*satz), (lid, k)
    assert sum(len(x) for x in K2.WOERTER.values()) == 97
    assert len([s for x in K2.WOERTER.values() for *_, s in x if s]) == 66


def test_alle_neuen_kennungen_und_nichts_sonst(grunddaten):
    alle = [w["id"] for w in _alle(grunddaten)]
    assert len(K2.NEU) == 194
    assert K2.NEU <= set(alle)
    assert len(alle) == 7997 + 194
    assert len(alle) == len(set(alle))


def test_in_b1_und_b2_hinten_im_level_je_wort_vor_seinem_satz(grunddaten):
    stufe = {s["id"]: s["stufe"] for s in grunddaten["sektionen"]}
    lv = _level(grunddaten)
    for lid, liste in K2.WOERTER.items():
        k = lv[lid]
        if stufe[k["sektion"]] not in ("B1", "B2"):
            continue
        assert k["reihenfolge"] is True, lid
        erwartet = []
        for de, bs, _, satz in liste:
            assert satz, (lid, bs)
            erwartet += [K2.kennung(de, bs), K2.kennung(*satz)]
        assert [w["id"] for w in k["words"][-len(erwartet):]] == erwartet, lid
        for _, _, _, (de, bs) in liste:
            assert re.search(r"[.!?]$", bs) and re.search(r"[.!?]$", de) and bs[:1].isupper(), bs


def test_tagesablauf_bleibt_in_seiner_folge(grunddaten):
    bs = [w["bs"] for w in _level(grunddaten)["routine"]["words"]]
    folge = ["ustajati", "Ustajem u sedam", "budilnik", "umivati se", "Umivam se", "tuširati se", "Tuširam se",
             "brijati se", "Brijem se", "prati zube", "češljati se", "Češljam se", "doručkovati"]
    assert bs[:len(folge)] == folge
    i = bs.index("gledati televiziju")
    assert bs[i:i + 6] == ["gledati televiziju", "kupati se", "Kupam se", "ići spavati", "Idem spavati", "pidžama"]


def test_level_groesse(grunddaten):
    zu_gross = {k["id"]: len(k["words"]) for k in grunddaten["kategorien"]
                if k["id"] in K2.WOERTER and len(k["words"]) > 40}
    assert zu_gross == GROSS


def test_ordnungszahlen_hinter_zeitangaben(grunddaten):
    ids = [k["id"] for k in grunddaten["kategorien"]]
    i = ids.index("ordnungszahlen")
    assert ids[i - 1:i + 2] == ["zeitangaben", "ordnungszahlen", "sofort_endlich"]
    k = _level(grunddaten)["ordnungszahlen"]
    stufe = {s["id"]: s["stufe"] for s in grunddaten["sektionen"]}
    assert k["sektion"] == "zeitfreizeit" and stufe[k["sektion"]] == "B1"
    assert k["reihenfolge"] is True and k["baut_auf"] == ["zeitangaben", "mengen"]
    assert k["label"] == "Ordnungszahlen"
    erwartet = []
    for de, bs, auch, satz in K2.ORDNUNGSZAHLEN:
        erwartet += [(de, bs, auch), (satz[0], satz[1], [])]
    assert [(w["de"], w["bs"], w.get("auch") or []) for w in k["words"]] == erwartet
    assert [bs for _, bs, _, _ in K2.ORDNUNGSZAHLEN] == [
        "četvrti", "peti", "šesti", "sedmi", "osmi", "deveti", "deseti", "jedanaesti", "dvanaesti", "dvadeseti",
        "dvadeset prvi", "trideseti", "pedeseti", "stoti", "hiljaditi"]


def test_prvi_drugi_treci_mit_weiblicher_und_saechlicher_form(grunddaten):
    w = {x["bs"]: x for x in _level(grunddaten)["mengen"]["words"]}
    assert w["prvi"]["auch"] == ["prva", "prvo"]
    assert w["drugi"]["auch"] == ["druga", "drugo"]
    assert w["treći"]["auch"] == ["treća", "treće"]
    assert "auch" not in w["zadnji"], "zadnji war nicht gefragt (LIESMICH, Punkt 9)"


def test_jeder_neue_eintrag_ist_in_jeder_sprache_uebersetzt(grunddaten):
    import uebersetzungen
    neu = [w for w in _alle(grunddaten) if w["id"] in K2.NEU]
    for code in LANGS:
        texte, woerter = uebersetzungen.INHALT[code]["texte"], uebersetzungen.INHALT[code]["woerter"]
        fehlt = [w["de"] for w in neu if w["de"] not in texte and w["bs"] not in woerter]
        assert fehlt == [], (code, fehlt[:5])
    k = _level(grunddaten)["ordnungszahlen"]
    for code in LANGS:
        assert k["label"] in uebersetzungen.INHALT[code]["texte"]
        assert k["tipp"] in uebersetzungen.INHALT[code]["texte"]


def test_neue_bedeutungen_sind_in_jeder_sprache_eindeutig(alle_daten):
    """Gleich lautende Bedeutungen gelten in der App als dasselbe Wort (_bedeutung() in
    web/js/aufgaben.js): sie zaehlen beim Tippen fuereinander und fehlen sich in der
    Auswahl. Lautsprecher hiess auf Franzoesisch "enceinte" wie trudna (schwanger),
    Lineal "règle" wie pravilo, Schwamm auf Schwedisch "svamp" wie gljive (Pilze)."""
    bed = lambda s: re.sub(r"\s+", " ", re.sub(r"[.!?…]+$", "", str(s).lower())).strip()
    gefunden = []
    for code, daten in alle_daten.items():
        nach = {}
        for w in _alle(daten):
            nach.setdefault(bed(w["de"]), set()).add(w["bs"])
        for w in _alle(daten):
            if w["id"] in K2.NEU and len(nach[bed(w["de"])]) > 1:
                gefunden.append((code, w["bs"], w["de"], sorted(nach[bed(w["de"])])))
    assert gefunden == []


def test_teilbedeutungen_im_level_nur_wie_im_deutschen(alle_daten, grunddaten):
    """Wie bei den Wortschatz-Paketen (tests/paket1020_pruefung.py): zwei Woerter eines
    Levels heissen in einer Sprache nur dann teilweise gleich, wenn das Deutsche es auch tut."""
    from paket1020_pruefung import _teile_gleich
    de = {(k["id"], w["bs"]): w["de"] for k in grunddaten["kategorien"] for w in k["words"]}
    gefunden = []
    for code, daten in alle_daten.items():
        paare = {frozenset((w["bs"], w["partner"])) for w in _alle(daten) if w.get("partner")}
        for k in daten["kategorien"]:
            for i, a in enumerate(k["words"]):
                for b in k["words"][i + 1:]:
                    if (a["id"] not in K2.NEU and b["id"] not in K2.NEU) or frozenset((a["bs"], b["bs"])) in paare:
                        continue
                    if _teile_gleich(a["de"], b["de"]) and not _teile_gleich(de[(k["id"], a["bs"])],
                                                                             de[(k["id"], b["bs"])]):
                        gefunden.append((code, k["id"], a["bs"], b["bs"]))
    assert gefunden == []


# --- Hose und Geschaeft (Ajdin am 25.11.2026, Variante A) ---

def test_hose_und_geschaeft_mit_neuer_kennung(grunddaten, index_html):
    ids = {w["id"]: w for w in _level(grunddaten)["einkaufen"]["words"]}
    alle = {w["id"] for w in _alle(grunddaten)}
    for alt, neu in K2.UMBENANNT.items():
        assert alt not in alle and neu in ids, (alt, neu)
        assert "'%s': '%s'" % (alt, neu) in index_html, "UMBENANNT in web/js/anmeldung_server.js"
    assert ids["hose:pantalone / hlače"]["bs"] == "pantalone / hlače"
    gross = K2.kennung(*K2.GESCHAEFT_GROSS)
    namen = list(ids)
    assert namen.index(gross) == namen.index("geschäft (kleiner laden):radnja") + 1
    # trgovina heisst weiter auch „Handel“, im Level Wirtschaft
    assert "handel:trgovina" in alle


def test_klammern_der_geschaefte_in_jeder_sprache(alle_daten):
    gesehen = set()
    for code, daten in alle_daten.items():
        w = {x["id"]: x["de"] for x in _level(daten)["einkaufen"]["words"]}
        klein, gross = w["geschäft (kleiner laden):radnja"], w["geschäft (großer laden):trgovina"]
        assert klein != gross and klein.endswith(")") and gross.endswith(")"), code
        gesehen.add(code)
    assert gesehen == {"de", *LANGS}


def test_handel_und_die_geschaefte_zaehlen_richtig(grunddaten):
    """Schreibaufgabe: Wort, auch und auch_var (annehmbar() in web/js/aufgaben.js)."""
    w = {x["id"]: x for x in _alle(grunddaten)}

    def antworten(kennung):
        x = w[kennung]
        return {x["bs"], *(x.get("auch") or []), *(x.get("auch_var") or [])}

    assert antworten("geschäft (kleiner laden):radnja") >= {"radnja", "trgovina", "prodavnica"}
    assert antworten("geschäft (großer laden):trgovina") == {"trgovina", "radnja", "prodavnica"}
    assert antworten("laden:prodavnica") == {"prodavnica", "radnja", "trgovina", "dućan"}, "bei Laden bleibt alles"
    assert antworten("handel:trgovina") == {"trgovina"}


def test_tipp_paare_der_neuen_woerter(grunddaten):
    w = {x["id"]: x for x in _alle(grunddaten)}
    assert sum(len(x) for x in K2.TIPPEN.values()) == 34
    for kennung, formen in K2.TIPPEN.items():
        assert [f.lower().rstrip("?") for f in w[kennung]["auch_var"]] == formen, kennung
        # gezeigt wird keine davon
        assert not set(formen) & set((w[kennung].get("auch") or [])), kennung


# --- Ordnungszahl als Ziffer mit Punkt (O-F3) in matches() ---

def _stueck(html, anfang, ende):
    assert html.count(anfang) == 1, anfang
    a = html.index(anfang)
    return html[a:html.index(ende, a)]


NODE = r"""
const ein = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const f = new Function(ein.bloecke + '\nreturn {matches};')();
process.stdout.write(JSON.stringify(ein.faelle.map(([e, a]) => f.matches(e, a))));
"""

ZIFFERN = [
    ("4.", "četvrti / četvrta / četvrto", "ok"),
    (" 4. ", "četvrti / četvrta / četvrto", "ok"),
    ("4", "četvrti / četvrta / četvrto", "no"),        # ohne Punkt ist es četiri
    ("4..", "četvrti / četvrta / četvrto", "no"),
    # Bei der Grundzahl gilt "4." schon vor K7: matches() streicht den Punkt am Ende wie bei
    # einem Satz, und "4" ist četiri. Die Liste (O-F3, „regel“) nahm an, das sei falsch.
    ("4.", "četiri", "ok"),
    ("5.", "četvrti / četvrta / četvrto", "no"),
    ("21.", "dvadeset prvi / dvadeset prva / dvadeset prvo / dvadeset i prvi", "ok"),
    ("1000.", "hiljaditi / hiljadita / hiljadito / tisućiti", "ok"),
    ("100.", "stoti / stota / stoto", "ok"),
    ("1.", "prvi / prva / prvo", "ok"),
    ("3.", "treći / treća / treće", "ok"),
    ("1.", "prvo", "no"),                               # prvo heisst in der App auch „zuerst“
    ("5.", "peta", "no"),                               # peta ist auch die Ferse
    ("četvrta", "četvrti / četvrta / četvrto", "ok"),
    ("cetvrti", "četvrti / četvrta / četvrto", "almost"),
]


@pytest.fixture(scope="module")
def node_ziffern(index_html):
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    html = index_html.replace("\r\n", "\n")
    bloecke = "\n".join([
        _stueck(html, "const strip = s =>", "\n/* ---------- Gesprochenes vergleichen"),
        _stueck(html, "const ZAHL_EINER = ", "\n/* ---- Zahlen, die wechseln"),
        _stueck(html, "function matches(guess, answer){", "\n/* ---------- Fast richtig: erst ein Hinweis"),
    ])
    ein = {"bloecke": bloecke, "faelle": [z[:2] for z in ZIFFERN]}
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps(ein), capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=120)
    return json.loads(aus.stdout)


def test_ziffer_mit_punkt_bei_ordnungszahlen(node_ziffern):
    assert [(e, a, r) for (e, a, _), r in zip(ZIFFERN, node_ziffern)] == ZIFFERN


def test_ziffer_mit_punkt_auch_beim_sprechen(index_html):
    html = index_html.replace("\r\n", "\n")
    assert "  if(ordnungsZiffer(gehoert, ziel)) return true;" in html
    assert "  if(ordnungsZiffer(g, alts[0])) return 'ok';" in html


def test_ordnungszahlen_der_app_stehen_in_der_tabelle(grunddaten, index_html):
    """Jede Ordnungszahl der App (maennlich, wie sie dasteht) hat ihre Zahl, sonst nichts."""
    block = re.search(r"const ORDNUNGSZAHL = \{(.*?)\};", index_html).group(1)
    tab = {k.strip(): v for k, v in re.findall(r"'?([a-z ]+)'?:(\d+)", block)}
    import unicodedata

    def ohne(s):
        s = s.lower().replace("đ", "d")
        return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
    erwartet = {ohne(bs): str(n) for n, (_, bs, _, _) in zip(
        (4, 5, 6, 7, 8, 9, 10, 11, 12, 20, 21, 30, 50, 100, 1000), K2.ORDNUNGSZAHLEN)}
    erwartet.update({"prvi": "1", "drugi": "2", "treci": "3"})
    assert tab == erwartet


# --- Ton ---

def test_ton_offen_nur_was_noch_fehlt(grunddaten, wurzel):
    """Bis zum Ton-Schritt still: genau die neuen Schluessel ohne Aufnahme. Kommt eine
    Aufnahme nach ton_nur_emir.json, muss der Schluessel hier raus. Seit dem Ton-Schritt
    am 27.11.2026 ist TON_OFFEN leer (tests/test_k2_ton.py)."""
    import io
    import os

    import ton_bauen
    emir = ton_bauen.nur_emir()
    index = {e["key"] for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                 encoding="utf-8"))["toene"]}
    assert not K2.TON_OFFEN & (set(emir) | index), sorted(K2.TON_OFFEN & (set(emir) | index))
    neu = [w["bs"] for w in _alle(grunddaten) if w["id"] in K2.NEU]
    ohne = [b for b in neu if ton_bauen.schluessel(b) not in emir and ton_bauen.schluessel(b) not in index
            and ton_bauen.schluessel(b) not in K2.TON_OFFEN]
    assert ohne == []
    assert K2.TON_OFFEN == frozenset()
    assert emir["pantalone / hlače"] == K2.TON_HOSE      # Emir w10094 „pantalone, hlače“
    assert K2.FRUEHER_IN_SAMMLE <= set(emir)


def test_tanne_hat_ihren_eigenen_ton(grunddaten):
    import ton_bedeutung
    t = ton_bedeutung.lade()
    assert t["woerter"]["tanne:jela"] == "jela (tanne)" and t["vorgemerkt"] == {}
    w = {x["id"]: x for x in _alle(grunddaten)}
    assert w["tanne:jela"]["ton"] == "jela (tanne)"
