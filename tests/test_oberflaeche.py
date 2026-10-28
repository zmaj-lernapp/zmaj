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


def test_serienschutz_ohne_schneeflocke(sprachcodes):
    """Seit dem 24.10.2026 steht vor dem Serienschutz das gemalte Schild
    (web/symbole/serienschutz.webp), Entwurf B "zwei Plaetze". Die
    Schneeflocke in den Texten ist deshalb in allen acht Sprachen weg -
    sonst stuende sie neben dem Bild. Neu ist die Kurzform "noch {zeit}"
    fuer die Zeile unter der Serie; sie muss kuerzer sein als die lange
    Fassung der Einstellungen."""
    import sprachen
    fehler = []
    for code in sprachcodes:
        texte = sprachen.texte(code)
        for k, v in texte.items():
            if k.startswith(("serie.", "laden.schutz", "set.serie")) and isinstance(v, str) and "❄" in v:
                fehler.append((code, k))
        kurz, lang = texte["serie.schutz_noch"], texte["serie.schutz_naechster"]
        if "{zeit}" not in kurz or len(kurz) >= len(lang):
            fehler.append((code, "serie.schutz_noch", kurz, lang))
    assert not fehler, fehler


def test_impressum_in_der_app(index_html, sprachcodes):
    """Ajdin am 28.10.2026: das Impressum auch in der App, unter
    Einstellungen -> Ueber die App nach Nutzungsbedingungen und Datenschutz,
    und auf der Anmeldung, die man ohne Konto nicht verlassen kann. Derselbe
    Text wie auf der Webseite (seite_bauen.py nimmt auch set.impressum_text
    aus texte(), mit KONTAKT_FORMULAR die Fassung mit Formular), offline aus
    web/inhalt/<sprache>.json."""
    import sprachen
    html = index_html.replace("\r\n", "\n")
    agb = ('<details><summary data-t="set.agb"></summary>'
           '<div class="inner legal" data-t="set.agb_text"></div></details>')
    ds = ('<details><summary data-t="set.datenschutz"></summary>'
          '<div class="inner legal" data-t="set.datenschutz_text"></div></details>')
    imp = ('<details><summary data-t="set.impressum"></summary>'
           '<div class="inner legal" data-t="set.impressum_text"></div></details>')
    assert html.count(imp) == 1 and html.index(agb) < html.index(ds) < html.index(imp)
    # Direkt darunter im selben Abschnitt, nur ein Kommentar dazwischen.
    zwischen = html[html.index(ds) + len(ds):html.index(imp)]
    assert re.fullmatch(r"\s*<!--.*?-->\s*", zwischen, re.S), zwischen
    assert html.count('<summary id="anmImpKopf"></summary><div class="inner legal" id="anmImp"></div>') == 1
    assert "$('anmImp').innerHTML = t('set.impressum_text', {anbieter: t('set.anbieter')});" in html
    for code in sprachcodes:
        t = sprachen.texte(code)
        assert t["set.impressum"].strip() and t["set.impressum"] != "set.impressum", code
        assert "{anbieter}" in t["set.impressum_text"], code
