# -*- coding: utf-8 -*-
"""Die Texte der Oberfläche in acht Sprachen."""
import re


def test_keine_sprache_hat_luecken(sprachcodes):
    import sprachen
    for code in sprachcodes:
        assert sprachen.fehlende_texte(code) == [], code


def test_platzhalter_gleich_in_allen_sprachen(sprachcodes):
    """{name} in einer Sprache und nicht in der anderen heißt: der Text
    erscheint, aber mit einer Lücke."""
    import sprachen
    basis = sprachen.texte(sprachen.GRUNDSPRACHE)
    fehler = []
    for code in sprachcodes:
        texte = sprachen.texte(code)
        for k, v in basis.items():
            if not isinstance(v, str) or not isinstance(texte.get(k), str):
                continue
            a = sorted(re.findall(r"\{[a-z_]+\}", v))
            b = sorted(re.findall(r"\{[a-z_]+\}", texte[k]))
            if a != b:
                fehler.append((code, k, a, b))
    assert not fehler, fehler[:20]


def test_html_tags_ausgeglichen(sprachcodes):
    """Ein vergessenes </b> macht in der App den ganzen Rest fett."""
    import sprachen
    fehler = []
    for code in sprachcodes:
        for k, v in sprachen.texte(code).items():
            if not isinstance(v, str):
                continue
            for tag in ("b", "i"):
                if v.count("<%s>" % tag) != v.count("</%s>" % tag):
                    fehler.append((code, k, tag))
    assert not fehler, fehler[:20]
