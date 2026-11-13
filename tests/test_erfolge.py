# -*- coding: utf-8 -*-
"""Erfolge (13.11.2026), ohne Browser: Liste, Texte und Lernstand.

Ajdin am 13.11.2026 (erfolge.md, 8a/9b/10a). Wie es aussieht und sich
verhaelt, pruefen tests_e2e/test_erfolge.py.
"""
import re

import pytest

KENNUNGEN = ["t7", "t30", "t100", "t365", "t1000", "f30", "f100", "f365",
             "w100", "w500", "w1000", "w2500", "a1", "a2", "b1", "g1", "ga", "k100"]


def _erfolge(index_html):
    m = re.search(r"const ERFOLGE = \[(.*?)\n\];", index_html, flags=re.S)
    assert m, "ERFOLGE fehlt in index.html"
    return re.findall(r"\{id: '([a-z0-9]+)'", m.group(1))


def test_achtzehn_abzeichen_mit_festen_kennungen(index_html):
    """Die Kennungen stehen im Lernstand ("e:w500") - sie duerfen sich nie
    aendern, und es sind genau die 18 aus erfolge.md."""
    assert _erfolge(index_html) == KENNUNGEN


def test_kein_neues_feld_im_stand(index_html):
    """Gespeichert wird in gefeiert und wann (erfolge.md: keine neuen
    Felder, die Cloud ist fast voll). STAND_FELDER bleibt, wie es war."""
    m = re.search(r"const STAND_FELDER = new Set\(\[(.*?)\]\);", index_html, flags=re.S)
    felder = re.findall(r"'([a-z_]+)'", m.group(1))
    assert felder == ["gewusst", "bestanden", "gelesen", "tage", "frost", "besitz", "leben",
                      "schutz", "tagwerk", "muenzen_ges", "muenzen_aus", "getragen", "gefeiert",
                      "rekord", "wann", "geschenk_jahr", "einstufung", "topf", "bewertung",
                      "stern", "kartei", "zahnarzt"]
    assert "const ERFOLG_VORN = 'e:';" in index_html


def test_kein_konfetti_ausserhalb_der_wegmarken(index_html):
    """Feier-Karte und Konfetti nur bei Lerntagen (Ajdin 8a): der Teil der
    Erfolge baut weder .schnipsel noch eine .nachfrage, und spielt keinen Ton."""
    start = index_html.index("/* =================== ERFOLGE (13.11.2026)")
    ende = index_html.index("/* ---- Tagesaufgaben ----", start)
    teil = re.sub(r"/\*.*?\*/", "", index_html[start:ende], flags=re.S)
    for verboten in ("schnipsel", "nachfrage", "sound(", "zeigeWegmarke"):
        assert verboten not in teil, verboten


def test_jedes_abzeichen_hat_sein_bild(wurzel, index_html):
    """Die gemalten Abzeichen (13.11.2026): jedes ausser der Flamme (die
    nimmt das Bild der Serie) hat in ERFOLG_BILDER sein eigenes Bild in
    web/erfolge, quadratisch und gross genug fuer dreifache Pixeldichte wie
    web/symbole - und kein Bild liegt dort, das die App nicht nennt."""
    import os

    from test_symbole import _webp_groesse
    m = re.search(r"const ERFOLG_BILDER = Object\.fromEntries\(\s*\[(.*?)\]", index_html, flags=re.S)
    assert m, "ERFOLG_BILDER fehlt"
    genannt = re.findall(r"'([a-z0-9]+)'", m.group(1))
    assert genannt == [k for k in KENNUNGEN if not k.startswith("f")], genannt
    ordner = os.path.join(wurzel, "web", "erfolge")
    assert sorted(os.listdir(ordner)) == sorted(k + ".webp" for k in genannt)
    for k in genannt:
        b, h = _webp_groesse(os.path.join(ordner, k + ".webp"))
        assert b == h and b >= 128, (k, b, h)


@pytest.mark.parametrize("schluessel", ["erfolg.t7", "erfolg.t30", "erfolg.t100", "erfolg.t365",
                                        "erfolg.t1000", "erfolg.blau", "erfolg.lila", "erfolg.gold",
                                        "erfolg.erste", "erfolg.alle", "erfolg.kopf"])
def test_namen_bleiben_kurz(sprachcodes, schluessel):
    """Die Namen unter den Ringen: eine Zahl und ein Wort, damit bei 360 px
    nichts umbricht (erfolge.md, Risiken). Hoechstens 16 Zeichen.

    Seit 13.11.2026 heisst erfolg.kopf "Bombengedächtnis" (Ajdin), in den
    anderen Sprachen die Redewendung vom Elefanten-Gedaechtnis. Die sind
    laenger: bis 18 Zeichen, aber jedes Wort ueber 10 Buchstaben braucht
    einen weichen Trennstrich (U+00AD), sonst bricht es bei 55 px Spalte
    mitten im Wort um ("Bombeng|edächtnis")."""
    import sprachen
    for code in sprachcodes:
        v = sprachen.texte(code)[schluessel]
        sichtbar = v.replace("­", "")
        assert sichtbar and len(sichtbar) <= (18 if schluessel == "erfolg.kopf" else 16), (code, schluessel, v)
        for wort in v.split():
            assert all(len(s) <= 10 for s in wort.split("­")), (code, schluessel, wort)


def test_texte_in_allen_sprachen(sprachcodes, index_html):
    """Jeder erfolg.*-Text, den die App nennt, steht in allen acht Sprachen,
    mit denselben Platzhaltern wie im Deutschen."""
    import sprachen
    genannt = set(re.findall(r"'(erfolg\.[a-z0-9_]+)'", index_html))
    assert len(genannt) >= 30, genannt
    de = sprachen.texte("de")
    for code in sprachcodes:
        t = sprachen.texte(code)
        for k in genannt:
            assert k in t and t[k], (code, k)
            assert sorted(re.findall(r"\{\w+\}", t[k])) == sorted(re.findall(r"\{\w+\}", de[k])), (code, k)
