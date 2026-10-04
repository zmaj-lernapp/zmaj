# -*- coding: utf-8 -*-
"""Die offenen Patch-Skripte passen auf den heutigen Stand von web/index.html.

Sie liegen bereit, bis der geschlossene Test vorbei ist. Ändert sich
index.html vorher an einer ihrer Stellen, soll das hier auffallen und nicht
erst am Tag des Builds. Am 04.10.2026 brachen sieben ältere Skripte genau so
ab, ohne dass es ein Test bemerkt hätte - deshalb gilt das hier für jedes
offene Skript, das richten.py benutzt."""
import importlib

import pytest

# Skript -> (Zeichen, dass es schon angewendet ist, Spuren danach je genau einmal)
OFFEN = {
    "import_richten": ("const nurTexte = x =>",
                       ["nurTexte(d.gewusst)", "anzahlBis(d.leben.anzahl, LEBEN_MAX)",
                        "Object.prototype.hasOwnProperty.call(FARBEN, id)",
                        "const vorher = standAlsObjekt();"]),
    "sicherheit2_richten": ("hasOwnProperty.call(FESTE, p)",
                            ["if(neuesPw && KONTEN_AN)", "if(bestaetigen && KONTEN_AN)"]),
    "barrierefreiheit_richten": ("--good-text:#188049",
                                 ["<main>", "</main>", "--good-text:#188049"]),
    "werbung_richten": ("}, ()=> !document.hidden);",
                        ["}, ()=> !document.hidden);",
                         "Punkt 1, nachgezogen fuers belohnte Video."]),
}

# Dasselbe fuer Skripte, die sprachen.py richten (Stand 04.10.2026: nur
# werbung_texte.py). Spuren je genau einmal - in jeder der acht Sprachen.
OFFEN_SPRACHEN = {
    "werbung_texte": ("Google verwendet all das, um Anzeigen auszuspielen",
                      ["Google verwendet all das, um Anzeigen auszuspielen",
                       "Google uses all of this to serve ads",
                       "Google bunların tamamını reklam göstermek",
                       "Google använder allt detta för att visa annonser",
                       "Google gebruikt dit alles om advertenties te tonen",
                       "Google bruker alt dette til å vise annonser",
                       "Google bruger alt dette til at vise annoncer",
                       "Google utilise tout cela pour diffuser les annonces",
                       "Außer Googles Werbebaustein bindet die App keine Analyse-Dienste",
                       "analyse en dehors du module publicitaire de Google"]),
}


def gerichtet(name, text):
    """Text nach dem Skript - angewendet, falls es noch nicht drin ist."""
    skript = importlib.import_module(name)
    if OFFEN[name][0] in text:
        return skript, text
    neu, fehler = skript.anwenden(text)
    assert not fehler, fehler
    return skript, neu


@pytest.mark.parametrize("name", OFFEN)
def test_passt_noch_oder_ist_schon_angewendet(name, index_html):
    _, neu = gerichtet(name, index_html.replace("\r\n", "\n"))
    for spur in OFFEN[name][1]:
        assert neu.count(spur) == 1, spur


@pytest.mark.parametrize("name", OFFEN)
def test_zweimal_anwenden_bricht_ab(name, index_html):
    """Ein zweiter Lauf darf nichts doppelt einbauen."""
    skript, neu = gerichtet(name, index_html.replace("\r\n", "\n"))
    _, fehler = skript.anwenden(neu)
    assert fehler


@pytest.mark.parametrize("name", OFFEN)
def test_crlf_kopie_wird_gerichtet_und_bleibt_crlf(name, index_html, tmp_path):
    """Git für Windows checkt mit CRLF aus; die Anker enthalten \\n. Ohne
    Normalisieren brachen die Skripte dort mit "0-mal gefunden" ab."""
    skript = importlib.import_module(name)
    text = index_html.replace("\r\n", "\n")
    if OFFEN[name][0] in text:
        pytest.skip("schon angewendet")
    kopie = tmp_path / "index.html"
    kopie.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    assert skript.main(["--datei", str(kopie), "--schreiben"]) == 0
    roh = kopie.read_bytes()
    assert roh.count(b"\n") == roh.count(b"\r\n"), "Zeilenenden gemischt"
    erwartet, _ = skript.anwenden(text)
    assert roh.decode("utf-8").replace("\r\n", "\n") == erwartet


def test_probelauf_schreibt_nichts(index_html, tmp_path):
    import import_richten
    kopie = tmp_path / "index.html"
    kopie.write_text(index_html, encoding="utf-8")
    vorher = kopie.read_bytes()
    import_richten.main(["--datei", str(kopie)])
    assert kopie.read_bytes() == vorher


def test_fehlender_anker_bricht_ab_ohne_zu_schreiben(tmp_path):
    import richten
    aenderungen = [("eins", "a", "A"), ("zwei", "fehlt", "x")]
    kopie = tmp_path / "x.html"
    kopie.write_text("a b", encoding="utf-8")

    def anwenden(html):
        neu, fehler = richten.ersetze_einmal(html, aenderungen)
        return neu, fehler + richten.gleichgewicht(html, neu)

    assert richten.main(["--datei", str(kopie), "--schreiben"], aenderungen, anwenden, "x.py") == 1
    assert kopie.read_text(encoding="utf-8") == "a b"


def test_gleichgewicht_findet_aufgerissene_klammer():
    import richten
    assert richten.gleichgewicht("f(){}", "f(){") == ["geschweifte Klammern aus dem Gleichgewicht"]
    assert richten.gleichgewicht("<!-- x -->", "<!-- x") == ["HTML-Kommentare aus dem Gleichgewicht"]
    assert richten.gleichgewicht("a", "a") == []


@pytest.fixture(scope="module")
def sprachen_py(wurzel):
    """sprachen.py, wie es im Repository liegt, Zeilenenden auf \\n."""
    import io
    import os
    roh = io.open(os.path.join(wurzel, "sprachen.py"), encoding="utf-8", newline="").read()
    return roh.replace("\r\n", "\n")


def sprachen_gerichtet(name, text):
    skript = importlib.import_module(name)
    if OFFEN_SPRACHEN[name][0] in text:
        return skript, text
    neu, fehler = skript.anwenden(text)
    assert not fehler, fehler
    return skript, neu


@pytest.mark.parametrize("name", OFFEN_SPRACHEN)
def test_sprachen_passt_noch_oder_ist_schon_angewendet(name, sprachen_py):
    _, neu = sprachen_gerichtet(name, sprachen_py)
    for spur in OFFEN_SPRACHEN[name][1]:
        assert neu.count(spur) == 1, spur
    compile(neu, "sprachen.py", "exec")


@pytest.mark.parametrize("name", OFFEN_SPRACHEN)
def test_sprachen_zweimal_anwenden_bricht_ab(name, sprachen_py):
    skript, neu = sprachen_gerichtet(name, sprachen_py)
    _, fehler = skript.anwenden(neu)
    assert fehler


@pytest.mark.parametrize("name", OFFEN_SPRACHEN)
def test_sprachen_crlf_kopie_wird_gerichtet_und_bleibt_crlf(name, sprachen_py, tmp_path):
    skript = importlib.import_module(name)
    if OFFEN_SPRACHEN[name][0] in sprachen_py:
        pytest.skip("schon angewendet")
    kopie = tmp_path / "sprachen.py"
    kopie.write_bytes(sprachen_py.replace("\n", "\r\n").encode("utf-8"))
    vorher = kopie.read_bytes()
    assert skript.main(["--datei", str(kopie)]) == 0
    assert kopie.read_bytes() == vorher, "der Probelauf hat geschrieben"
    assert skript.main(["--datei", str(kopie), "--schreiben"]) == 0
    roh = kopie.read_bytes()
    assert roh.count(b"\n") == roh.count(b"\r\n"), "Zeilenenden gemischt"
    erwartet, _ = skript.anwenden(sprachen_py)
    assert roh.decode("utf-8").replace("\r\n", "\n") == erwartet
