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
  - Danach (Prüfung am selben Tag): steht die Seite ganz oben, bleiben über
    der Kopfleiste mindestens 16 Punkte wie in der App; auf 7 Zoll Bild 1
    klebte sie am Rand, am Handy auf Bild 1 und 4 stand sie zu knapp.
  - Prüfung danach: Steht die Seite nicht ganz oben (Bild 2, am Handy
    Bild 8), liegt oben ein Streifen in der Farbe des Grunds, so hoch wie der
    Rand oben der App - vorher stand das oberste Teil dort nur 6 bis 10
    Punkte unter dem Rand.
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
    (Prüfung 16.11.2026: fr Bild 2), jetzt mit der strengeren Messung und
    unter dem Streifen oben (siehe test_streifen_oben_auf_gerollten_seiten)."""
    schritte = dict(BP.SCHRITTE)
    assert "window.__randSchnitte = () =>" in BP.RAND_PRUEFUNG
    assert "if(!window.__randSchnitte().length) return 'Streifen +' + k;" in BP.RAND_PRUEFUNG
    b2 = schritte["02-amt"]
    # der Reihe nach: Reiterleiste, Leiste Lernpfad, Karte "Heute" (Handy en, nl)
    assert "const anker = [['Reiterleiste', oben]];" in b2
    assert "if(oben === leiste) anker.push(['Lernpfad', modus], ['Heute', document.getElementById('questBox')]);" in b2
    assert "for(const [name, el] of anker){" in b2
    assert "frei = await window.__bandFrei(el, 24);" in b2
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
    # bis zu 24 Punkte: 7 Zoll Bild 1 braucht 21 (siehe test_kopfleiste_nicht_am_rand)
    assert "const polster = y0 < 0.5 ? (opts.polster === undefined ? 24 : opts.polster) : 0;" in js
    quelle = inspect.getsource(BP.ein_lauf)
    zurueck = 'js("window.__polsterZurueck(); window.__bandWeg(); window.__obenStand = false; return 1")'
    assert quelle.index(zurueck) < quelle.index("ergebnis = js(code)")
    # der Rand, der da waechst, ist der der App
    assert re.search(r"^  body\{[^}]*padding:16px 16px 48px;", _app(), re.M | re.S)


def _luft_min():
    m = re.findall(r"window\.__luftMin = (\d+);", BP.RAND_PRUEFUNG)
    assert len(m) == 1, m
    return int(m[0])


def test_kopfleiste_nicht_am_rand():
    """Pruefung nach dem Feinschliff 16.11.2026: Auf 7 Zoll Bild 1 (de, en,
    tr, nl, da) rollte __randFrei die Seite 13 bis 14 Punkte hinauf, und die
    Kopfleiste stand nur 3 bis 4 Punkte unter dem Rand - gedraengt wie vorher
    die Reiterleiste auf fr Handy Bild 2. Steht die Seite ganz oben, rollt sie
    jetzt nur so weit, dass ueber der Kopfleiste __luftMin Punkte bleiben,
    und vor dem Bild bricht das Skript ab, wenn es doch weniger sind."""
    js = BP.RAND_PRUEFUNG
    assert "window.__luftMin = 16;" in js
    assert "window.__luftOben = () => window.__kopfRaum() / faktor() + 0.5;" in js
    frei = js.split("window.__randFrei = async", 1)[1]
    assert "window.__obenStand = y0 < 0.5;" in frei
    assert "(y0 < 0.5 ? Math.max(0, kopf - window.__luftMin * f) : kopf)" in frei
    # gesetzt nur, wo __randFrei selbst sucht (nicht beim blossen Nachpruefen),
    # und nur die Seite ganz oben zaehlt: Bild 2 und Bild 8 am Handy rollen selbst
    assert frei.index("if(opts.nurPruefen)") < frei.index("window.__obenStand = y0 < 0.5;")
    quelle = inspect.getsource(BP.ein_lauf)
    assert 'luft = js("return window.__luftPruefen()")' in quelle
    assert re.search(r"if luft\[0\] < luft\[1\] - 0\.5:\s+raise SystemExit\(", quelle)
    pruefen = js.split("window.__luftPruefen = () => {", 1)[1].split("};", 1)[0]
    assert "return [window.__luftOben(), window.__luftMin, !!B];" in pruefen
    # vor jedem Schritt zurueckgesetzt, und geprueft wird vor dem Bild
    assert quelle.index("window.__obenStand = false;") < quelle.index("ergebnis = js(code)")
    assert quelle.index("luft = js(") < quelle.index("seite.screenshot(")
    # die Kopfleiste, ueber der die Luft gemessen wird, steht in der App ganz oben
    app = _app()
    assert 'id="livesBar"' in app and 'id="muenzBar"' in app


def test_luft_oben_wie_in_der_app():
    """Ajdin zur Pruefung ("ja ist schon knapp"): 8 Punkte waren noch
    gedraengt. __luftMin ist der Rand oben der App (padding-top von body):
    so viel Luft hat dort die Kopfleiste und die Karte einer Lektion. Mehr
    darf es nicht sein - sonst brauchte jede Seite, die ganz oben steht, mehr
    Rand als in der App -, weniger soll es nicht sein."""
    m = re.search(r"^  body\{[^}]*padding:(\d+)px \d+px \d+px;", _app(), re.M | re.S)
    assert m, "padding von body nicht gefunden"
    assert _luft_min() == int(m.group(1)) == 16
    # Rand oben (padding) und Luft ueber der Kopfleiste in denselben Punkten:
    # hinauf rollt die Seite oben nur bis zur Luft __luftMin, der Rand waechst
    # bis 24 Punkte (7 Zoll Bild 1 braucht 21)
    frei = BP.RAND_PRUEFUNG.split("window.__randFrei = async", 1)[1]
    assert "Math.max(0, kopf - window.__luftMin * f)" in frei
    assert "opts.polster === undefined ? 24 : opts.polster" in frei


def test_luft_oben_in_der_ausgabe():
    """Die Ausgabe nennt je Bild die Luft ueber dem obersten Teil ("Luft
    oben 26", mit Streifen "Luft oben 17 (Streifen)") - nach der Pruefung,
    also nur fuer Bilder, die sie bestanden haben."""
    quelle = inspect.getsource(BP.ein_lauf)
    zeile = 'lage += " | Luft oben %.0f%s" % (luft[0], " (Streifen)" if luft[2] else "")'
    assert zeile in quelle
    assert quelle.index("raise SystemExit(\"%s %s %s: ueber dem obersten Teil") < quelle.index(zeile)
    assert quelle.index(zeile) < quelle.index('print("  %-16s %s | %s" % (name,')


def test_bild4_und_6_satz_mit_wenig_rand():
    """Bild 4 und 6 duerfen oben nicht mehr hinauf, nur tiefer (mehr Rand
    oben). Am Handy brauchte "Gdje je crvena torba?" dafuer 23 Punkte,
    "Ne znam gdje je ključ." 13: die Karte stand dann viel tiefer als auf
    Bild 3 und 5. Ein Satz mit mehr als 4 Punkten gilt erst ab dem 9. Versuch
    und nur, wenn keiner davor weniger brauchte; im letzten Versuch jeder."""
    js = BP.RAND_PRUEFUNG
    satz = js.split("window.__satzFrei = async (versuch, letzter, wahl) => {", 1)[1].split("};", 1)[0]
    assert "const frei = await window.__randFrei();" in satz
    assert "if(!frei || k <= 4 || letzter) return frei;" in satz
    assert "const gut = versuch >= 8 && k <= wahl.bester;" in satz
    assert satz.index("const gut =") < satz.index("wahl.bester = Math.min(wahl.bester, k);")
    # verworfen: Rand oben wieder wie in der App, und der naechste Satz kommt
    assert satz.index("window.__polsterZurueck();") < satz.index("return '';")
    # liest die Ausgabe von __randFrei ("frei Rand oben +13")
    assert "' Rand oben +' + k" in js and r"/Rand oben \+(\d+)/" in satz
    schritte = dict(BP.SCHRITTE)
    for name in ("04-kacheln", "06-luecke"):
        s = schritte[name]
        n = int(re.search(r"for\(let versuch = 0; versuch < (\d+) && !frei; versuch\+\+\)", s).group(1))
        assert "const wahl = {bester: Infinity};" in s, name
        assert "frei = await window.__satzFrei(versuch, versuch === %d, wahl);" % (n - 1) in s, name
        assert n > 8, name    # nach den 8 Versuchen mit wenig Rand bleibt noch Raum
        assert "window.__randFrei()" not in s, name


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
    assert "for kennung in GERAETE_IDS[kennung_ab - 1:]:" in quelle and "except Angeschnitten as e:" in quelle
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
    """Reicht die Lage nicht, kommt ein anderer Satz - das Motiv (Kacheln,
    Lueckensatz) bleibt."""
    schritte = dict(BP.SCHRITTE)
    for name in ("04-kacheln", "06-luecke"):
        assert "for(let versuch = 0; versuch < 12 && !frei; versuch++)" in schritte[name], name
        assert "frei = await window.__satzFrei(versuch, versuch === 11, wahl);" in schritte[name], name


def test_bild8_ohne_halbe_zeile():
    """Tablets ganz oben wie bisher; das Handy probiert der Reihe nach die
    Karte "Heute" oben ("Weitermachen" mit seinem Schatten unter dem
    Streifen), "Weitermachen" oben wie bis 16.11. und die Leiste Lernpfad/
    Geschichten/Wiederholen oben - mit dem Knopf oben allein gab es oft
    keinen Rand ohne halbe Zeile, und darueber hing der Drache."""
    b8 = dict(BP.SCHRITTE)["08-wiederholen"]
    tablets = "if(document.documentElement.classList.contains('gross')) frei = await window.__randFrei();"
    wege = "for(const [name, el] of [['Heute', document.getElementById('questBox')], ['Weitermachen', w], ['Leiste', leiste]]){"
    assert b8.index(tablets) < b8.index(wege)
    assert b8.count("frei = await window.__randFrei();") == 1
    assert "frei = await window.__bandFrei(el, 24);" in b8
    # der Schatten unter "Weitermachen" darf nicht unter dem Streifen hervorschauen
    js = BP.RAND_PRUEFUNG
    assert "r.bottom + (B ? schattenUnten(s) : 0) > B + px" in js
    assert '<div class="quests" id="questBox"></div>' in _app()   # die Karte "Heute"
    assert '<button class="btn know weiterknopf" id="weiterKnopf"></button>' in _app()


def test_streifen_oben_auf_gerollten_seiten():
    """Pruefung nach der Kopfleiste 16.11.2026: Auf Bild 2 (alle Geraete) und
    am Handy auf Bild 8 stand das oberste Teil 6 bis 10 Punkte unter dem
    Rand. Durch Rollen allein ging nicht mehr (zwischen den Leisten und
    Karten sind nur 9 bis 13 Punkte frei). Dort liegt jetzt oben ein Streifen
    in der Farbe des Grunds, so hoch wie der Rand oben der App, und der obere
    Rand wird an seiner Unterkante gemessen. Vor jedem Schritt ist er weg,
    und ein Bild, dessen Seite nicht ganz oben steht, braucht ihn."""
    js = BP.RAND_PRUEFUNG
    an = js.split("window.__bandAn = () => {", 1)[1].split("};", 1)[0]
    # so hoch wie der Rand oben der App (nicht der fuer ein Bild vergroesserte)
    assert an.index("window.__polsterZurueck();") < an.index("getComputedStyle(document.body).paddingTop")
    assert "position:fixed; left:0; top:0;" in an and "z-index:2147483647" in an
    assert "s.style.background = getComputedStyle(document.body).backgroundColor;" in js
    assert re.search(r"^  body\{\s*background:var\(--bg\);", _app(), re.M)   # der Grund ist eine Farbe
    # gemessen wird an der Unterkante des Streifens
    schnitte = js.split("window.__randSchnitte = () => {", 1)[1]
    assert "const raender = [['oben', B], ['unten', H]], aus = [];" in schnitte
    assert "if(oben < B && unten > B || oben < H && unten > H)" in schnitte
    assert "q.bottom > B && q.top < H" in schnitte
    # am Streifen auch keine halbe grosse Karte
    assert "r.height > (B ? H : H / 4)" in schnitte
    kopf = js.split("window.__kopfRaum = () => {", 1)[1].split("};", 1)[0]
    assert "if(el.id === BAND) continue;" in kopf and "r.top < B - 0.5" in kopf
    # Lage: Anker k Punkte unter dem Streifen, nie hoeher
    frei = js.split("window.__bandFrei = async (anker, bis) => {", 1)[1].split("    };", 1)[0]
    assert "Math.floor((anker.getBoundingClientRect().top - B - k) * f)" in frei
    assert "if(d < k - 0.01 || d >= k + 1) continue;" in frei
    assert frei.index("window.__bandWeg();") > frei.index("for(let k = 0; k <= bis; k++){")
    # nicht ganz oben und ohne Streifen: keine Luft, das Skript bricht ab
    assert "if(!window.__obenStand && !B) return [0, window.__luftMin, false];" in js
    quelle = inspect.getsource(BP.ein_lauf)
    assert quelle.index("window.__bandWeg();") < quelle.index("ergebnis = js(code)")
    assert quelle.index('luft = js("return window.__luftPruefen()")') < quelle.index("seite.screenshot(")
    # Bild 2 und am Handy Bild 8 nehmen den Streifen, die uebrigen Bilder nicht
    schritte = dict(BP.SCHRITTE)
    for name, code in schritte.items():
        assert ("window.__bandFrei(" in code) == (name in ("02-amt", "08-wiederholen")), name


def test_kennung_zum_nachmachen():
    """Wer nur einzelne Bilder eines Satzes neu macht, braucht dieselben
    Tagesaufgaben wie auf den uebrigen: --kennung waehlt, mit welcher
    Geraete-Kennung begonnen wird (Store-Bilder 1.4: nl am Handy mit 2)."""
    quelle = inspect.getsource(BP.main)
    assert 'p.add_argument("--kennung", type=int, default=1,' in quelle
    assert "a.version, a.kennung)" in quelle
    machen = inspect.getsource(BP.bilder_machen)
    assert "kennung_ab=1):" in machen
    assert "if not 1 <= kennung_ab <= len(GERAETE_IDS):" in machen


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
