# -*- coding: utf-8 -*-
"""Lernkartei (v110, Ajdins Entscheidung vom 28.10.2026): was sich ohne
Browser pruefen laesst. Das Verhalten selbst - Stufen, Umzug, Lektion,
Kasten, Runde, Tagesgrenze, Sicherungsdatei, Cloud - prueft
tests_e2e/test_kartei.py im echten Browser."""
import json
import re

KARTEI_TEXTE = ["kartei.titel", "kartei.desc", "kartei.anzahl", "kartei.leer", "kartei.rest", "kartei.alles"]


def test_kartei_texte_in_allen_sprachen(sprachcodes):
    """Jede Sprache hat alle Texte, kurz, ohne Platzhalter und HTML, und die
    Zahl im Kasten hat Einzahl und Mehrzahl wie topf.anzahl."""
    import sprachen
    for code in sprachcodes:
        eigene = sprachen.TEXTE[code]
        for k in KARTEI_TEXTE:
            v = eigene.get(k)
            assert isinstance(v, str) and v.strip(), (code, k)
            assert len(v) <= 120, (code, k, v)
            assert "{" not in v and "<" not in v, (code, k, v)
        assert eigene["kartei.anzahl"].count("|") == 1, code
        # Der Titel steht auch oben in der Kopfzeile der Runde
        assert len(eigene["kartei.titel"]) <= 24, code


def test_kartei_texte_deutsch_wie_entschieden():
    import sprachen
    de = sprachen.TEXTE["de"]
    assert {k: de[k] for k in KARTEI_TEXTE} == {
        "kartei.titel": "Heute fällig",
        "kartei.desc": "Gelernte Wörter kommen wieder, bevor du sie vergisst – "
                       "erst nach einem Tag, dann immer seltener.",
        "kartei.anzahl": "Wort wartet|Wörter warten",
        "kartei.leer": "Heute ist nichts fällig.",
        "kartei.rest": "noch fällig",
        "kartei.alles": "Für heute ist alles wiederholt.",
    }


def test_kasten_ganz_oben_ueber_den_beiden_alten(index_html):
    """Im Reiter Wiederholen seit dem 20.11.2026 ganz oben, ueber
    "Wiederholen" und "Markiert" (O10, Ajdin: "ja mach die heute fällig ganz
    nach oben"); bis dahin der dritte darunter. Eine schlichte .section,
    gebaut mit denselben Klassen."""
    html = index_html.replace("\r\n", "\n")
    assert ('    <div id="topfHome" style="display:none">\n'
            '      <div class="section" id="karteiBox"></div>\n'
            '      <div class="section" id="topfBox"></div>\n'
            '      <div class="section" id="sternBox"></div>\n'
            '    </div>\n') in html
    assert html.count('id="karteiBox"') == 1
    rumpf = html.split("function karteiKasten(){")[1].split("\n}\n")[0]
    for klasse in ('<div class="desc">', '<div class="topfzahl">', '<div class="topfwort">',
                   '<div class="topfleer">', '<div class="row"><button class="btn know" id="karteiLos"',
                   '<div class="note">', '<div class="row schmal">'):
        assert klasse in rumpf, klasse
    assert "function showTopf(){\n  karteiKasten();\n  topfKasten();\n  sternKasten();\n}" in html


def test_roter_zaehler_am_reiter(index_html, sprachcodes):
    """Der rote Zaehler am Reiter Wiederholen (O10, 20.11.2026): im Reiter,
    fuer den Bildschirmleser stumm, die Zahl im Namen des Reiters. Der Text
    dafuer in jeder Sprache mit {n}, Einzahl und Mehrzahl, ohne HTML."""
    import sprachen
    html = index_html.replace("\r\n", "\n")
    reiter = html.split('<button role="tab" id="modeTopf"')[1].split("</button>")[0]
    assert '<span class="zaehler" id="faelligZahl" aria-hidden="true" hidden></span>' in reiter
    assert html.count('id="faelligZahl"') == 1
    assert "faelligZaehler();" in html.split("function renderHero(){")[1].split("\n}\n")[0]
    assert "faelligNachziehen();" in html.split("function topfNachziehen(){")[1].split("\n}\n")[0]
    for code in sprachcodes:
        v = sprachen.TEXTE[code].get("kartei.zaehler")
        assert isinstance(v, str) and v.count("|") == 1, (code, v)
        assert all(teil.count("{n}") == 1 for teil in v.split("|")), (code, v)
        assert "<" not in v and len(v) <= 80, (code, v)
    assert sprachen.TEXTE["de"]["kartei.zaehler"] == "{n} Wort heute fällig|{n} Wörter heute fällig"


def test_regeln_wie_entschieden(index_html):
    assert "const KARTEI_ABSTAENDE = [1, 3, 7, 14, 30, 90, 180];" in index_html
    assert "const KARTEI_TAG_MAX = 30, KARTEI_IN_LEKTION = 3;" in index_html
    # richtig eine Stufe weiter, falsch zwei zurueck, nie unter die erste
    assert ("const s = ok ? Math.min(e[0] + 1, KARTEI_LETZTE) : Math.max(e[0] - 2, 0);") in index_html


def test_nachbesserung_nach_der_pruefung(index_html):
    """Pruefung vom 29.10.2026: Reihenfolge nach relativer Verspaetung, der
    Umzug auf Stufe 3 mit hoechstens 10 je Tag, der Kartei-Tag ab 4 Uhr,
    faellige Woerter in der Lektion ohne Sprechen, der Hinweis ohne Leben
    nur einmal. Das Verhalten prueft tests_e2e/test_kartei.py."""
    html = index_html.replace("\r\n", "\n")
    assert "const KARTEI_UMZUG_STUFE = 3, KARTEI_UMZUG_TAGE = 28, KARTEI_UMZUG_MIN = 3, KARTEI_UMZUG_MAX = 10;" in html
    assert "const KARTEI_TAG_BEGINN = 4;" in html
    heute = html.split("function karteiHeute(){")[1].split("\n}\n")[0]
    assert "(heute - kartei.w[id][1] + 1) / KARTEI_ABSTAENDE[kartei.w[id][0]]" in heute
    tag = html.split("function karteiTag(){")[1].split("\n}\n")[0]
    assert "if(d.getHours() < KARTEI_TAG_BEGINN) d.setDate(d.getDate() - 1);" in tag
    lektion = html.split("function buildLesson(){")[1].split("\n}\n")[0]
    assert "const pickF = artenReihum(types.filter(x => x !== 'speak'));" in lektion
    assert "faellig.forEach(f => tasks.push(Object.assign({typ:pickF(f.w)," in lektion
    # Der Hinweis ohne Leben nur einmal: seit "Heute faellig" ganz oben steht
    # (O10, 20.11.2026), zeigt er ihn, und die zwei darunter lassen ihn weg.
    kasten = html.split("function karteiKasten(){")[1].split("\n}\n")[0]
    assert "if(topfAnzahl() || sternAnzahl())" not in kasten
    for name in ("topfKasten", "sternKasten"):
        rumpf = html.split("function %s(){" % name)[1].split("\n}\n")[0]
        assert "if(karteiHeute().length){ box.innerHTML = html; return; }" in rumpf, name


def test_eigenes_feld_ueberall_dabei(index_html):
    """Nur im neuen Feld kartei (Regel bei STAND_FELDER), und das ueberall:
    Geraetespeicher und Sicherungsdatei (standAlsObjekt), Einlesen
    (standUebernehmen, sicherungPlausibel), Cloud (standZusammenfuehren)."""
    felder = re.search(r"const STAND_FELDER = new Set\(\[(.*?)\]\);", index_html, re.S).group(1)
    assert "'kartei'" in felder
    html = index_html.replace("\r\n", "\n")
    assert "          kartei: kartei};\n" in html
    assert "  kartei = karteiPruefen(d.kartei);\n" in html
    assert "  p.kartei = karteiPruefen(s.kartei, true);\n" in html
    assert "  m.kartei = karteiMischen(a.kartei, b.kartei);\n" in html
    # topf und stern bleiben, wie sie waren: keine Kartei-Daten darin
    for zeile in html.split("\n"):
        if re.search(r"\b(topf|stern)\[[^\]]+\]\s*=", zeile):
            assert "kartei" not in zeile, zeile


def test_einstufung_zaehlt_nicht(index_html):
    """Jede Antwort auf ein Wort zaehlt - in Lektion, Runden und Level-Test,
    nur nicht in der Einstufung."""
    html = index_html.replace("\r\n", "\n")
    einst = html.split("function einstufungFrageZeigen(){")[1].split("function einstufungEnde(){")[0]
    assert "karteiAntwort" not in einst
    lektion = html.split("function showLessonTask(){")[1].split("\n}\n")[0]
    assert lektion.count("karteiAntwort(task,") == 2
    test = html.split("function showTestQ(){")[1].split("\n}\n")[0]
    assert "karteiAntwort(Tx.qs[Tx.i], !!res.ok);" in test
    assert html.count("karteiAntwort(") == 4      # die Funktion und drei Aufrufe


def test_weitermachen_unveraendert(index_html):
    """Der grosse Weitermachen-Knopf startet im Reiter Wiederholen weiter nur
    die Runde fuer Fehler."""
    html = index_html.replace("\r\n", "\n")
    hero = html.split("function renderHero(){")[1].split("\n}\n")[0]
    assert "if(topfAnzahl() && livesNow() > 0){ name = t('topf.titel'); hin = startTopf; }" in hero
    assert "kartei" not in hero.lower()


def test_groesse_unter_der_cloud_grenze(grunddaten, index_html):
    """Je Wort Kennung und drei Zahlen. Gerechnet mit vierstelligen Tagen
    (27 Jahre nach APP_START): bei allen Woertern von heute und, skaliert,
    bei 7 000 Woertern (Ziel C1/C2) brauchen Kartei und gewusst zusammen
    gut die Haelfte der Cloud-Grenze (rund 457 000 von 900 000 Bytes) - wie
    im Vorschlag geschaetzt. Daneben bleibt Platz fuer Topf, Sterne und
    den Rest.

    Seit den Wortschatz-Paketen (31.10./01.11.2026) hat jedes neue Wort
    einen Beispielsatz als eigenen Eintrag mit langer Kennung - die 600
    Eintraege der Pakete 3 und 4 brauchen im Mittel 61 Byte. Damit sind es
    47 Byte je Eintrag (bis Paket 2: 44), auf 7 000 Eintraege gerechnet
    rund 567 000 Byte, gut 60 % der Grenze (bis Paket 2: 519 000). Kartei
    und gewusst allein erreichen sie bei etwa 11 000 Eintraegen - fuer das
    Ziel C1/C2 mit einem Satz zu jedem Wort braucht die Sicherung vorher
    kuerzere Kennungen fuer Saetze oder ein zweites Dokument.

    Mit den Paketen 5 bis 9 (06.11.2026, 4 425 Eintraege) sind es 52 Byte je
    Eintrag, auf 7 000 Eintraege gerechnet rund 634 000 Byte, gut 70 % der
    Grenze; Kartei und gewusst allein erreichen sie jetzt bei etwa 9 900
    Eintraegen. Bei allen 4 425 Woertern heute: rund 401 000 Byte (45 %).

    Mit den Paketen 10 bis 20 (07.11.2026, 7 998 Eintraege, Stufe B2) sind es 58 Byte
    je Eintrag in der Kartei und 102 mit gewusst. Wer alle 7 998 kann, braucht dafuer
    rund 819 000 Byte, 91 % der Grenze; dazu kommen Topf, Sterne und der Rest.
    Bei etwa 8 800 Eintraegen ist die Grenze allein damit erreicht, dann meldet
    cloudSpeichern() 'zu gross' und sichert nichts mehr. Vor dem naechsten Paket
    brauchen Saetze kuerzere Kennungen in der Sicherung oder der Stand ein zweites
    Dokument - darum die Grenze hier bei 92 %: das naechste Paket schlaegt an.

    Entschieden am 13.11.2026 (Weg A, in 1.4): Ueber CLOUD_GROESSE_MAX packt die App den
    Stand (cloud_stand.js, gepackt rund ein Viertel, tests_e2e/test_cloud_packen.py).
    Mit K2 und K7 (27.11.2026, 8 191 Eintraege) hat die 92 %-Marke wie gedacht
    angeschlagen: 840 062 Byte, 93 %. Wer alles kann, sichert also gepackt; nur ein
    Geraet mit 1.3 daneben kann dann gepackt1 weglassen (standFremdAus, Randfall in
    cloud_stand.js). Die Marke steht jetzt bei der Grenze selbst: B2 Teil 2 (rund 900
    Eintraege) schlaegt an - vorher K14 „immer packen“ und nachsehen, wer noch 1.3 hat."""
    grenze = int(re.search(r"const CLOUD_GROESSE_MAX = (\d+);", index_html).group(1))
    ids = list(dict.fromkeys(w["id"] for k in grunddaten["kategorien"] for w in k["words"]))
    kompakt = dict(ensure_ascii=False, separators=(",", ":"))
    kartei = len(json.dumps({"tag": 9999, "n": 30, "w": {i: [6, 9999, 9999] for i in ids}}, **kompakt).encode("utf-8"))
    gewusst = len(json.dumps(ids, **kompakt).encode("utf-8"))
    assert kartei / len(ids) < 60, kartei / len(ids)
    assert kartei + gewusst < grenze, (kartei + gewusst, grenze)
