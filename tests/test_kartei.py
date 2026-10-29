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


def test_dritter_kasten_unter_den_beiden_alten(index_html):
    """Im Reiter Wiederholen unter "Wiederholen" und "Markiert", eine
    schlichte .section, gebaut mit denselben Klassen."""
    html = index_html.replace("\r\n", "\n")
    assert ('      <div class="section" id="topfBox"></div>\n'
            '      <div class="section" id="sternBox"></div>\n'
            '      <div class="section" id="karteiBox"></div>\n'
            '    </div>\n') in html
    assert html.count('id="karteiBox"') == 1
    rumpf = html.split("function karteiKasten(){")[1].split("\n}\n")[0]
    for klasse in ('<div class="desc">', '<div class="topfzahl">', '<div class="topfwort">',
                   '<div class="topfleer">', '<div class="row"><button class="btn know" id="karteiLos"',
                   '<div class="note">', '<div class="row schmal">'):
        assert klasse in rumpf, klasse
    assert "function showTopf(){\n  topfKasten();\n  sternKasten();\n  karteiKasten();\n}" in html


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
    kasten = html.split("function karteiKasten(){")[1].split("\n}\n")[0]
    assert "if(topfAnzahl() || sternAnzahl()){ box.innerHTML = html; return; }" in kasten


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
    den Rest."""
    grenze = int(re.search(r"const CLOUD_GROESSE_MAX = (\d+);", index_html).group(1))
    ids = list(dict.fromkeys(w["id"] for k in grunddaten["kategorien"] for w in k["words"]))
    kompakt = dict(ensure_ascii=False, separators=(",", ":"))
    kartei = len(json.dumps({"tag": 9999, "n": 30, "w": {i: [6, 9999, 9999] for i in ids}}, **kompakt).encode("utf-8"))
    gewusst = len(json.dumps(ids, **kompakt).encode("utf-8"))
    assert kartei / len(ids) < 45, kartei / len(ids)
    assert (kartei + gewusst) * 7000 / len(ids) < grenze * 0.6
