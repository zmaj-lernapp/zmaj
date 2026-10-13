# -*- coding: utf-8 -*-
"""Feinere Prüfungen am Lerninhalt, in allen acht Sprachen.

Jede Prüfung hier steht für einen Fehler, den ein Lernender sehen würde:
eine Tabelle mit verrutschter Spalte, zwei gleiche Antwortknöpfe, ein
angetipptes Wort ohne Übersetzung.
"""


def tabellen(erklaerung):
    for teil in erklaerung:
        if isinstance(teil, dict) and "tabelle" in teil:
            yield teil["tabelle"]


def test_grammatik_tabellen_sind_rechteckig(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for kid, lektion in daten["grammatik"].items():
            for tab in tabellen(lektion.get("erklaerung", [])):
                breiten = {len(zeile) for zeile in tab}
                if len(breiten) != 1:
                    fehler.append((code, kid, sorted(breiten)))
    assert not fehler, fehler[:20]


def test_grammatik_optionen_ohne_dubletten(alle_daten):
    """Zwei gleiche Knöpfe: einer ist richtig, der andere falsch - der
    Lernende kann es nicht wissen. Passiert leicht erst durch Übersetzung."""
    fehler = []
    for code, daten in alle_daten.items():
        for kid, lektion in daten["grammatik"].items():
            for ue in lektion.get("uebungen", []):
                opt = ue.get("optionen", [])
                if len(set(opt)) != len(opt):
                    fehler.append((code, kid, ue.get("frage"), opt))
    assert not fehler, fehler[:20]


def test_grammatik_uebungen_vollstaendig(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for kid, lektion in daten["grammatik"].items():
            if not lektion.get("uebungen"):
                fehler.append((code, kid, "keine Übungen"))
            for ue in lektion.get("uebungen", []):
                if not str(ue.get("frage", "")).strip() or len(ue.get("optionen", [])) < 2:
                    fehler.append((code, kid, ue))
    assert not fehler, fehler[:20]


def test_woerterbuch_ohne_leere_eintraege(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for bs, bedeutung in daten["woerterbuch"].items():
            if not bs.strip() or not str(bedeutung).strip():
                fehler.append((code, bs))
    assert not fehler, fehler[:20]


def test_geschichten_vollstaendig_uebersetzt(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for g in daten["geschichten"]:
            if not g.get("uebersetzung", "").strip():
                fehler.append((code, g["id"], "keine Übersetzung"))
            for wort, bedeutung in g.get("vokabeln", {}).items():
                if not str(bedeutung).strip():
                    fehler.append((code, g["id"], wort))
            for f in g.get("fragen", []):
                if not f.get("frage", "").strip():
                    fehler.append((code, g["id"], "leere Frage"))
    assert not fehler, fehler[:20]


def test_level_haben_bezeichnung_und_tipp_in_jeder_sprache(alle_daten):
    fehler = []
    for code, daten in alle_daten.items():
        for k in daten["kategorien"]:
            if not k.get("label", "").strip():
                fehler.append((code, k["id"], "label"))
            if not k.get("tipp", "").strip():
                fehler.append((code, k["id"], "tipp"))
        for s in daten["sektionen"]:
            if not s.get("label", "").strip() or not s.get("beschreibung", "").strip():
                fehler.append((code, s["id"], "sektion"))
    assert not fehler, fehler[:20]


def test_jede_satzluecke_gehoert_zu_einem_level_mit_woertern(grunddaten):
    """Ein Lückensatz wird in der Lektion seines Levels gezeigt. Gibt es das
    Level nicht oder hat es keine Wörter, sieht ihn nie jemand."""
    mit_woertern = {k["id"] for k in grunddaten["kategorien"] if k["words"]}
    verwaist = [s["text"] for s in grunddaten["saetze"] if s["kat"] not in mit_woertern]
    assert not verwaist, verwaist[:20]


# ---------------------------------------------------------------------------
# Satzbau aus Kacheln (13.10.2026). Kübra wollte ganze Sätze aus den Wörtern
# legen, die gerade dran waren - ein Satz mit einem Wort, das erst drei Level
# später kommt, wäre genau das Gegenteil. Geprüft wird an vokabeln.SATZBAU,
# weil nur dort "formen" steht; die App bekommt es nicht.
# ---------------------------------------------------------------------------
# Namen dürfen Kacheln sein, ohne im Wortschatz zu stehen.
NAMEN = {"amina", "ajdin", "emir", "lejla", "sarajevo", "mostar", "tuzla",
         "zenica", "bosna", "hercegovina", "njemačka"}


def _wortformen(wort):
    """Alle Kacheln, die ein Wort hergibt: bs und auch, Varianten hinter
    " / " einzeln, "..." weg."""
    import inhalt
    formen = set()
    for feld in [wort.get("bs", "")] + list(wort.get("auch", []) or []):
        for alt in str(feld).split(" / "):
            formen.update(inhalt.satz_kacheln(alt.replace("...", " ")))
    return formen


def _bekannt_bis_level():
    """Level-id -> alle Kacheln aus den Wörtern von Level 1 bis hier."""
    import vokabeln
    bis_hier, tabelle = set(), {}
    for k in vokabeln.KATEGORIEN:
        for w in k["words"]:
            bis_hier |= _wortformen(w)
        tabelle[k["id"]] = set(bis_hier)
    return tabelle


def test_satzbau_kacheln_sind_bis_zu_ihrem_level_bekannt():
    import inhalt
    import vokabeln
    tabelle = _bekannt_bis_level()
    fehler = []
    for s in vokabeln.SATZBAU:
        bekannt = tabelle.get(s["kat"])
        if bekannt is None:
            fehler.append((s["bs"], "unbekanntes Level", s["kat"]))
            continue
        formen = {a.lower(): b.lower() for a, b in (s.get("formen") or {}).items()}
        for kachel in inhalt.satz_kacheln(s["bs"]):
            if kachel in bekannt or kachel in NAMEN:
                continue
            if kachel in formen and formen[kachel] in bekannt:
                continue
            fehler.append((s["kat"], s["bs"], kachel, formen.get(kachel)))
    assert not fehler, fehler[:20]


def test_satzbau_varianten_lassen_sich_aus_den_kacheln_bauen():
    """Eine Variante braucht genau die Kacheln, die auch daliegen - darf aber
    welche übrig lassen (das weggelassene Pronomen)."""
    import collections
    import inhalt
    import vokabeln
    fehler = []
    for s in vokabeln.SATZBAU:
        vorrat = collections.Counter(inhalt.satz_kacheln(s["bs"]))
        for v in s.get("auch", []) or []:
            gebraucht = collections.Counter(inhalt.satz_kacheln(v))
            if gebraucht - vorrat:
                fehler.append((s["bs"], v, dict(gebraucht - vorrat)))
            if inhalt.satz_kacheln(v) == inhalt.satz_kacheln(s["bs"]):
                fehler.append((s["bs"], v, "gleicht dem Satz"))
    assert not fehler, fehler[:20]


def test_satzbau_gibt_es_schon_im_ersten_level(grunddaten):
    """Kübra wollte es ab Level 1."""
    erstes = grunddaten["kategorien"][0]["id"]
    assert erstes == "basics"
    assert any(s["kat"] == erstes for s in grunddaten["satzbau"])


def test_satzbau_ohne_dubletten(grunddaten):
    import inhalt
    gesehen = [" ".join(inhalt.satz_kacheln(s["bs"])) for s in grunddaten["satzbau"]]
    doppelt = sorted({x for x in gesehen if gesehen.count(x) > 1})
    assert not doppelt, doppelt


def test_satzbau_geht_ohne_arbeitsfelder_an_die_app(grunddaten):
    """formen, quelle und notiz sind nur für die Prüfung und für uns. Von
    formen geht nur die Liste der Grundformen mit (grund)."""
    erlaubt = {"kat", "bs", "de", "auch", "grund"}
    fremd = [(s["bs"], sorted(set(s) - erlaubt)) for s in grunddaten["satzbau"] if set(s) - erlaubt]
    assert not fremd, fremd[:20]


def test_uebersetzungen_ohne_doppelte_schluessel(wurzel):
    """Steht ein deutscher Text in einem Sprachblock zweimal, behält Python
    stillschweigend den letzten - eine Korrektur weiter oben wirkt dann nie.
    Mit den Satzbau-Sätzen (13.10.2026) kommen viele neue Einträge dazu,
    deshalb wird das jetzt am Quelltext geprüft."""
    import ast
    import collections
    import io
    import os
    quelle = io.open(os.path.join(wurzel, "uebersetzungen.py"), encoding="utf-8").read()
    inhalt = None
    for knoten in ast.parse(quelle).body:
        if isinstance(knoten, ast.Assign) and any(isinstance(z, ast.Name) and z.id == "INHALT" for z in knoten.targets):
            inhalt = knoten.value
    assert isinstance(inhalt, ast.Dict), "INHALT nicht gefunden"
    fehler = []
    for teil in ast.walk(inhalt):
        if not isinstance(teil, ast.Dict):
            continue
        schluessel = [k.value for k in teil.keys if isinstance(k, ast.Constant)]
        for k, n in collections.Counter(schluessel).items():
            if n > 1:
                zeilen = [s.lineno for s in teil.keys if isinstance(s, ast.Constant) and s.value == k]
                fehler.append((k, zeilen))
    assert not fehler, fehler[:20]
