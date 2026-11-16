# -*- coding: utf-8 -*-
"""Überschriften der Store-Bilder (store/bilder_machen/beschriften.py).

Geprüft wird ohne Browser:
  - Jede Sprache hat genau eine Überschrift je Bild, in derselben Reihenfolge
    wie die Aufnahmen in bilder_playwright.py.
  - Feste Wendungen bleiben in einer Zeile: Das geschützte Leerzeichen
    (U+00A0) ist unsichtbar und geht beim Bearbeiten leicht verloren. Ohne
    brach Bild 4 auf Deutsch als „Sätze Wort für / Wort bauen“ um
    (Prüfung 13.11.2026), auf Türkisch „kelime / kelime“.
  - Store-Bilder 1.4 (16.11.2026): bilder_playwright.py markiert alle
    Abzeichen als gesehen (sonst „Du hast schon 5 Abzeichen“ auf Bild 1),
    und Bild 2 öffnet B1 nur für sich - Bild 3 stellt den Stand wieder her.
  - Nachbesserung 16.11.2026: keine halbe Schriftzeile unten auf Bild 2 und
    auf Bild 8 der Tablets, und Bild 8 zeigt die Tagesaufgaben wie Bild 1.
  - Feinschliff 16.11.2026: vor jedem Bild bricht das Skript ab, wenn der
    obere oder untere Rand eine Zeile oder einen Knopf durchschneidet, wenn
    KM oder Tagesaufgaben anders sind als auf Bild 1, und es nimmt den
    Tastaturfokus weg und wartet, bis der Drache die Augen offen hat.
"""
import inspect
import json
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WURZEL, "store", "bilder_machen"))

import beschriften  # noqa: E402

BP = beschriften.BP


def _app():
    with open(os.path.join(WURZEL, "web", "index.html"), encoding="utf-8") as f:
        return f.read()

NBSP = " "


def test_jede_sprache_hat_alle_ueberschriften():
    namen = [name for name, _ in beschriften.BP.SCHRITTE]
    for sprache, texte in beschriften.UEBERSCHRIFTEN.items():
        assert len(texte) == len(namen), sprache
        assert all(t.strip() for t in texte), sprache


def test_bild4_bleibt_zusammen():
    de = beschriften.UEBERSCHRIFTEN["de"][3]
    assert de == "Sätze " + NBSP.join(["Wort", "für", "Wort", "bauen"])
    assert de.replace(NBSP, " ") == "Sätze Wort für Wort bauen"   # Wortlaut unverändert
    assert "kelime" + NBSP + "kelime" in beschriften.UEBERSCHRIFTEN["tr"][3]


def test_alle_abzeichen_gelten_als_gesehen():
    """Jedes Abzeichen aus ERFOLGE, unter dem Schlüssel, den die App liest."""
    app = _app()
    ids = BP.erfolge_ids()
    liste = app.split("const ERFOLGE = [", 1)[1].split("];", 1)[0]
    assert ids and len(ids) == len(set(ids)) == liste.count("{id:")
    assert "const ERFOLG_GESEHEN = '%s';" % BP.ERFOLG_GESEHEN in app


def test_bild2_oeffnet_b1_nur_fuer_sich():
    schritte = dict(BP.SCHRITTE)
    assert "window.__bestandenVorher = new Set(passed)" in schritte["02-amt"]
    assert "passed = window.__bestandenVorher" in schritte["03-neues-wort"]
    # Was Bild 2 aus der App braucht, gibt es dort unter diesem Namen
    app = _app()
    for name in ("STUFEN", "reiterLevel", "stufeVon", "firstOpen"):
        assert re.search(r"^const %s = " % name, app, re.M), name
    for name in ("stufeWaehlen", "sektionAufklappen"):
        assert re.search(r"^function %s\(" % name, app, re.M), name
    assert re.search(r"^let [^\n]*\bpassed = new Set\(\)", app, re.M)
    assert 'id="reiterLeiste"' in app and 'id="btnProfil"' in app


def test_keine_halbe_zeile_unten():
    """Bild 2 sucht einen Abstand der Reiterleiste ohne angeschnittene Zeile
    (Prüfung 16.11.2026: fr Bild 2), jetzt mit der strengeren Messung."""
    schritte = dict(BP.SCHRITTE)
    assert "window.__randSchnitte = () =>" in BP.RAND_PRUEFUNG
    assert "if(!window.__randSchnitte().length){ weg = [el, a]; break; }" in schritte["02-amt"]
    assert 'id="modeWords"' in _app()   # die Leiste Lernpfad/Geschichten/Wiederholen
    assert re.search(r"^function rectFaktor\(", _app(), re.M)


def test_rand_bricht_ab():
    """Feinschliff 16.11.2026: Vor jedem Bild sucht __randFrei eine Lage ohne
    Anschnitt, und steht danach doch etwas am Rand, bricht das Skript ab -
    vorher war es nur ein Hinweis in der Ausgabe, und Bild 1, 4 und 8 gingen
    mit halben Zeilen durch."""
    quelle = inspect.getsource(BP.ein_lauf)
    assert "js(RAND_PRUEFUNG)" in quelle
    assert "window.__randFrei(%s)" in quelle and "SPIELRAUM.get(name, {})" in quelle
    assert 'schnitte = js("return window.__randSchnitte()")' in quelle
    assert re.search(r"if schnitte:\s+raise Angeschnitten\(", quelle)
    # ... und gibt es mit keiner Kennung eine Lage ohne, bricht es ab
    assert re.search(r"else:\s+raise SystemExit\(fehler\)", inspect.getsource(BP.bilder_machen))
    # die Pruefung kommt vor dem Bild
    assert quelle.index("__randSchnitte()") < quelle.index("seite.screenshot(")
    # Bild 2, 4, 6 und 8 suchen selbst, hier wird nur nachgeprueft
    for name in ("02-amt", "04-kacheln", "06-luecke", "08-wiederholen"):
        assert BP.SPIELRAUM[name] == {"nurPruefen": True}, name
    assert set(BP.SPIELRAUM) <= {name for name, _ in BP.SCHRITTE}
    assert "if(opts.nurPruefen) return window.__randSchnitte().length ? '' : 'frei';" in BP.RAND_PRUEFUNG


def test_rand_oben_nur_fuer_ein_bild():
    """Steht die Seite ganz oben, darf sie nicht weiter hinunter. Statt
    dessen waechst der Rand ueber der Kopfleiste (padding-top von body) um
    ein paar Punkte - nur fuer dieses Bild: vor jedem Schritt steht er
    wieder wie in der App (10 Zoll sv, nb Bild 1, 7 Zoll de Bild 8)."""
    js = BP.RAND_PRUEFUNG
    assert "b.style.paddingTop = (pt0 + k) + 'px';" in js
    assert "const polster = y0 < 0.5 ? (opts.polster === undefined ? 12 : opts.polster) : 0;" in js
    quelle = inspect.getsource(BP.ein_lauf)
    assert quelle.index('js("window.__polsterZurueck(); return 1")') < quelle.index("ergebnis = js(code)")
    # der Rand, der da waechst, ist der der App
    assert re.search(r"^  body\{[^}]*padding:16px 16px 48px;", _app(), re.M | re.S)


def test_rand_misst_streng():
    """Keine Spitzen der naechsten Zeile (auf 7 Zoll 1 bis 3 Pixel), Abstand
    einer Zeile im Bild zum Rand, Unterstreichung, und halbe Knoepfe."""
    js = BP.RAND_PRUEFUNG
    assert "luft = 4 * px" in js and "px = 1 / (devicePixelRatio * f)" in js
    assert "H - 1.5" not in js and "H + 0.5" not in js       # die alten Toleranzen
    assert "'unten zu knapp: '" in js and "'oben zu knapp: '" in js
    assert "/underline/.test(s.textDecorationLine)" in js
    # Zeile fuer Zeile gemessen, nicht der ganze Text eines Absatzes
    assert "cv.measureText(zeile)" in js
    knoepfe = re.search(r"const KNOEPFE = '([^']+)'", js).group(1)
    for sel in ("button", "[role=tab]", ".kachel", ".btn"):
        assert sel in knoepfe.split(", "), sel
    # Level-Zeilen und Sektionskoepfe laufen als Karten unten weiter
    assert "if(b.closest('.node, .skopf')) continue;" in js
    app = _app()
    assert "b.className='node'" in app and '<div class="skopf" role="button"' in app


def test_vor_jedem_bild_kein_fokus_und_stand_wie_bild1():
    """Bild 3 zeigte "Weiter" mit Tastaturfokus; auf 10 Zoll en und fr standen
    auf Bild 7 und 8 1250 KM statt 1240. __randFrei nimmt den Fokus weg und
    stellt KM und Tagesaufgaben wie auf Bild 1 her, und STAND_IM_BILD bricht
    ab, wenn sie trotzdem abweichen."""
    js = BP.RAND_PRUEFUNG
    assert "if(a && a !== document.body && a.blur) a.blur();" in js
    assert "window.__standZurueck();" in js.split("window.__randFrei = async")[1]
    assert "muenzenGes = window.__muenzen01[0]; muenzenAus = window.__muenzen01[1];" in js
    assert "window.__muenzen01 = [muenzenGes, muenzenAus];" in dict(BP.SCHRITTE)["01-start"]
    quelle = inspect.getsource(BP.ein_lauf)
    assert "stand = js(STAND_IM_BILD)" in quelle and "wie auf Bild 1" in quelle
    app = _app()
    assert re.search(r"^let muenzenGes = 0, muenzenAus = 0;", app, re.M)
    assert re.search(r"^function renderLives\(\)", app, re.M)
    assert 'id="muenzBar"' in app and 'id="questBox"' in app
    assert "$$('xNext').focus();" in app   # darum der Fokusrahmen auf Bild 3


def test_feste_geraete_kennung_fuer_die_tagesaufgaben():
    """Mit fester Kennung zeigen an einem Tag alle Laeufe dieselben drei
    Tagesaufgaben - vorher zog jeder Lauf neue. Geht ein Lauf am Rand nicht
    auf, kommt er noch einmal mit der naechsten Kennung (andere Aufgaben),
    und alle Bilder dieses Laufs zeigen dieselben."""
    app = _app()
    assert re.search(r"^const LOKAL_ID\s*=\s*'%s';" % re.escape(BP.GERAETE_ID_SCHLUESSEL), app, re.M)
    assert "const questSaat = () => MIT_SERVER ? profil : geraetId();" in app
    assert "wuerfel(saatAus(questSaat()+'|'+tag))" in app
    ids = BP.GERAETE_IDS
    assert ids[0] == "zmaj-store-bilder" and len(ids) == len(set(ids)) >= 4
    assert "json.dumps(GERAETE_ID_SCHLUESSEL), json.dumps(kennung)" in inspect.getsource(BP.ein_lauf)
    quelle = inspect.getsource(BP.bilder_machen)
    assert "for kennung in GERAETE_IDS:" in quelle and "except Angeschnitten as e:" in quelle
    # nur der Rand fuehrt zum neuen Versuch, alles andere bricht ab
    assert "raise Angeschnitten(" in inspect.getsource(BP.ein_lauf)


def test_drache_mit_offenen_augen():
    """Bild 5 zeigte den Drachen blinzelnd. Das Skript wartet auf den Kopf
    mit offenen Augen und haelt die Animation dort an. Die Ebenen, nach
    denen es schaut, gibt es in der Zeichnung, und in der Ruheschleife gibt
    es Bilder mit offenen und mit geschlossenen Augen."""
    js = BP.DRACHE_ANHALTEN
    assert "l.nm === 'bild_kopf_neutral'" in js and "l.nm === 'bild_kopf_blinzeln'" in js
    quelle = inspect.getsource(BP.ein_lauf)
    assert quelle.index("__drachePausieren()") < quelle.index("seite.screenshot(") < quelle.index("__dracheWeiter()")
    with open(os.path.join(WURZEL, "web", "maskottchen", "zmaj.json"), encoding="utf-8") as f:
        d = json.load(f)
    ebenen = {e.get("nm"): e for e in d["layers"]}
    ruhe = next(m for m in d["markers"] if m["cm"] == "idle")

    def deckkraft(name, fr):
        o = ebenen[name]["ks"]["o"]
        if not o.get("a"):
            return o["k"]
        v = 0
        for k in o["k"]:
            if k["t"] <= fr:
                v = k["s"][0] if isinstance(k.get("s"), list) else k.get("s", v)
        return v

    bilder = range(int(ruhe["tm"]), int(ruhe["tm"] + ruhe["dr"]))
    offen = [fr for fr in bilder if deckkraft("bild_kopf_neutral", fr) > 0 and deckkraft("bild_kopf_blinzeln", fr) == 0]
    zu = [fr for fr in bilder if deckkraft("bild_kopf_blinzeln", fr) > 0]
    assert offen and zu and len(offen) > len(zu)


def test_bild4_und_6_mischen_neu_statt_anschnitt():
    """Reicht das Hinaufruecken nicht, kommt ein anderer Satz - das Motiv
    (Kacheln, Lueckensatz) bleibt."""
    schritte = dict(BP.SCHRITTE)
    for name in ("04-kacheln", "06-luecke"):
        assert "for(let versuch = 0; versuch < 12 && !frei; versuch++)" in schritte[name], name
        assert "frei = await window.__randFrei();" in schritte[name], name


def test_bild8_ohne_halbe_zeile():
    """Tablets ganz oben wie bisher; das Handy probiert der Reihe nach die
    Karte "Heute" oben ("Weitermachen" mit seinem Schatten ganz aus dem
    Bild), "Weitermachen" oben wie bis 16.11. und die Leiste Lernpfad/
    Geschichten/Wiederholen oben - mit dem Knopf oben allein gab es oft
    keinen Rand ohne halbe Zeile, und darueber hing der Drache."""
    b8 = dict(BP.SCHRITTE)["08-wiederholen"]
    wege = [b8.index(s) for s in ("if(document.documentElement.classList.contains('gross')) frei = await window.__randFrei();",
                                  "wie = 'Heute oben';", "wie = 'Weitermachen oben';", "wie = 'Leiste oben';")]
    assert wege == sorted(wege)
    assert b8.count("frei = await window.__randFrei();") == 4
    assert "getComputedStyle(w).boxShadow" in b8


def test_bild8_tagesaufgaben_wie_bild1():
    """Vor Bild 8 stehen die Tagesaufgaben wieder wie auf Bild 1: Bild 4 bis 6
    erfüllten auf da tab7 alle drei, und die Zeile "Alle tre klaret!" schob
    die Seite so weit hinunter, dass unten eine Zeile halb im Bild stand."""
    schritte = dict(BP.SCHRITTE)
    assert "window.__tagwerk01 = JSON.stringify(tagwerk[t]);" in schritte["01-start"]
    assert "tagwerk[today()] = JSON.parse(window.__tagwerk01);" in schritte["08-wiederholen"]
    app = _app()
    assert re.search(r"^let tagwerk = \{\};", app, re.M)
    assert re.search(r"^const today = \(\) =>", app, re.M)
