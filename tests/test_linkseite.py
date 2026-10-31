# -*- coding: utf-8 -*-
"""Die Linkseite links.html fuer die Profile (Ajdin am 31.10.2026, Weg B in
Release/Social_Media_Recherche_2026-10-31.md, Abschnitt 5.1).

Geprueft wird hier, ohne Browser:
  - Der Play-Link hat genau die Form aus Abschnitt 4.2 (Kanal URL-codiert
    in referrer=), fuer TikTok, Instagram, YouTube und "web".
  - Die Seite steht in acht Sprachen, ohne Skript auf Englisch, mit dem
    Link fuer "web" im HTML. Darunter Kontakt (Formular nur, wenn es gebaut
    wird), Impressum, Datenschutz, die drei Profile und der KI-Hinweis.
  - Nichts von fremden Servern, eine Content-Security-Policy ohne
    connect-src, und das Skript fasst weder Cookies noch localStorage an
    (§ 25 TDDDG).
  - Das Impressum sagt in allen acht Sprachen, dass es auch fuer die drei
    Profile gilt (Abschnitt 5.1).
Die drei ?von=-Varianten, die Seite ohne JavaScript und das Handyformat
prueft tests_e2e/test_linkseite.py im Browser.
"""
import base64
import hashlib
import json
import re
from html import escape

# Abschnitt 4.2, woertlich. Die Seite muss genau diese Links erzeugen.
RECHERCHE = {
    "tiktok": "https://play.google.com/store/apps/details?id=de.smartdragon.zmaj"
              "&referrer=utm_source%3Dtiktok%26utm_medium%3Dsocial%26utm_campaign%3Dbio",
    "instagram": "https://play.google.com/store/apps/details?id=de.smartdragon.zmaj"
                 "&referrer=utm_source%3Dinstagram%26utm_medium%3Dsocial%26utm_campaign%3Dbio",
    "youtube": "https://play.google.com/store/apps/details?id=de.smartdragon.zmaj"
               "&referrer=utm_source%3Dyoutube%26utm_medium%3Dsocial%26utm_campaign%3Dbio",
    "web": "https://play.google.com/store/apps/details?id=de.smartdragon.zmaj"
           "&referrer=utm_source%3Dweb%26utm_medium%3Dsocial%26utm_campaign%3Dbio",
}
PROFILE = ("TikTok", "Instagram", "YouTube")
ZUGANG = {"projekt": "zmaj-probe", "schluessel": "AIza" + "Probe" * 7}


def _bauen(tmp_path, monkeypatch, formular):
    import huelle
    import seite_bauen
    import sprachen
    ziel = tmp_path / "seite"
    privat = tmp_path / "huelle"
    privat.mkdir()
    if formular:
        (privat / "cloud_zugang.json").write_text(json.dumps(ZUGANG), encoding="utf-8")
    monkeypatch.setattr(seite_bauen, "ZIEL", str(ziel))
    monkeypatch.setattr(huelle, "ordner", lambda *a, **k: str(privat))
    monkeypatch.setattr(sprachen, "KONTAKT_FORMULAR", formular)
    monkeypatch.setattr(sprachen, "KONTAKT_STAND", "31.10.2026" if formular else None)
    seite_bauen.main()
    return (ziel / "links.html").read_text(encoding="utf-8")


def _abteilungen(html):
    return re.findall(r'(?s)<section data-sprache="([a-z]+)" lang="([a-z]+)"( hidden)?>(.*?)</section>', html)


def _skripte(html):
    return re.findall(r"(?is)<script[^>]*>(.*?)</script[^>]*>", html)


def _fingerabdruck(text):
    return "'sha256-%s'" % base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode("ascii")


def _csp(html):
    inhalt = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', html).group(1)
    teile = {}
    for teil in inhalt.split(";"):
        name, *werte = teil.split()
        teile[name] = werte
    return teile


def test_play_link_wie_in_der_recherche():
    import seite_bauen
    assert seite_bauen.play_link() == RECHERCHE["web"]
    for kanal in seite_bauen.KANAELE:
        assert seite_bauen.play_link(kanal) == RECHERCHE[kanal], kanal
    assert set(seite_bauen.KANAELE) == set(RECHERCHE) - {"web"}


def test_texte_in_allen_acht_sprachen(sprachcodes):
    import seite_bauen
    assert sorted(seite_bauen.LINKS) == sorted(sprachcodes)
    for code in sprachcodes:
        t = seite_bauen.LINKS[code]
        assert set(t) == {"play", "ki"}, code
        assert "Zmaj" in t["play"] and "Google Play" in t["play"] and t["play"].endswith("(Android)"), code
        assert t["ki"].strip(), code
        if code != "en":
            assert t["play"] != seite_bauen.LINKS["en"]["play"], code
            assert t["ki"] != seite_bauen.LINKS["en"]["ki"], code
    assert seite_bauen.LINKS["en"]["ki"] == "Characters & voices made with AI"


def test_linkseite_mit_formular(tmp_path, monkeypatch, sprachcodes):
    import seite_bauen
    import sprachen
    html = _bauen(tmp_path, monkeypatch, True)
    teile = _abteilungen(html)

    # Acht Sprachen, ohne Skript sichtbar nur die englische.
    assert [c for c, _, _, _ in teile] == sprachcodes
    assert [c for c, _, h, _ in teile if not h] == ["en"]
    assert all(c == echt for c, echt, _, _ in teile)
    assert html.startswith('<!doctype html>\n<html lang="en">')
    assert '<ul class="sprachen" hidden>' in html

    # Der Knopf zeigt ohne Skript auf den Link fuer "web".
    knopf = 'href="%s"' % escape(RECHERCHE["web"], quote=True)
    assert html.count('<a class="play" %s>' % knopf) == 8
    for code, _, _, inhalt in teile:
        assert '>%s</a>' % escape(seite_bauen.LINKS[code]["play"], quote=False) in inhalt, code
        assert '<a href="kontakt.html">%s</a>' % sprachen.kontakt_texte(code)["titel"] in inhalt, code
        assert '<a href="impressum.html">%s</a>' % sprachen.texte(code)["set.impressum"] in inhalt, code
        assert '<a href="datenschutz.html">' in inhalt, code
        for name, adresse in seite_bauen.SOZIAL:
            assert '<a href="%s" rel="noopener">%s</a>' % (adresse, name) in inhalt, (code, name)
        assert '<p class="ki">%s</p>' % escape(seite_bauen.LINKS[code]["ki"], quote=False) in inhalt, code
    assert [n for n, _ in seite_bauen.SOZIAL] == list(PROFILE)

    # Impressum im Fuss: Anschrift und Verweise, ohne Skript auf Englisch.
    assert sprachen.ANBIETER.replace("<br>", " · ") in html
    fuesse = re.findall(r'<span data-fuss="([a-z]+)"( hidden)?>', html)
    assert [c for c, h in fuesse if not h] == ["en"] and len(fuesse) == 8
    assert html.count('<a href="impressum.html">') == 16
    assert 'href="links.html"' not in html

    # Nichts von fremden Servern, nur das eigene Symbol.
    assert not re.search(r"<script[^>]+src=|<link[^>]+stylesheet|@import|url\(|<iframe", html)
    assert re.findall(r'<img [^>]*src="([^"]+)"', html) == ["icon-256.png"]
    assert re.findall(r'<link [^>]*href="([^"]+)"', html) == ["favicon.ico", "icon-256.png"]
    assert "unsafe" not in html and not re.search(r"\sstyle=|\son[a-z]+=", html)

    # Ein Skript, per Fingerabdruck erlaubt; die Seite ruft nichts ab.
    skripte = _skripte(html)
    assert len(skripte) == 1
    csp = _csp(html)
    assert csp["default-src"] == ["'none'"]
    assert csp["script-src"] == [_fingerabdruck(skripte[0])]
    stil = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    assert csp["style-src"] == [_fingerabdruck(stil)]
    assert csp["img-src"] == ["'self'"] and csp["form-action"] == ["'none'"]
    assert "connect-src" not in csp

    # Kein Zaehler, keine Cookies, kein Speicher auf dem Geraet (§ 25 TDDDG).
    skript = skripte[0]
    for verboten in ("localStorage", "sessionStorage", "indexedDB", "cookie", "fetch(", "XMLHttpRequest",
                     "sendBeacon", "innerHTML", "eval(", "new Function", "http://"):
        assert verboten not in skript, verboten
    assert re.findall(r"https://[^/'\"]+", skript) == ["https://play.google.com"]
    assert json.dumps(seite_bauen.play_link("__QUELLE__")) in skript
    assert json.dumps(list(seite_bauen.KANAELE)) in skript


def test_linkseite_ohne_formular(tmp_path, monkeypatch, sprachcodes):
    """Ohne kontakt.html fuehrt Kontakt zur E-Mail-Adresse, wie auf der
    Startseite - nie zu einer Seite, die es nicht gibt."""
    import seite_bauen
    html = _bauen(tmp_path, monkeypatch, False)
    assert "kontakt.html" not in html
    mail = seite_bauen.post_adresse()
    for code, _, _, inhalt in _abteilungen(html):
        assert '<a href="mailto:%s">%s</a>' % (mail, seite_bauen.START[code][4]) in inhalt, code


def test_impressum_gilt_fuer_die_profile(tmp_path, monkeypatch, sprachcodes):
    """Abschnitt 5.1: "Dieses Impressum gilt auch fuer unsere Profile auf
    TikTok, Instagram und YouTube." - in beiden Fassungen jeder Sprache,
    als eigener Absatz vor dem Kontakt, gleich in beiden."""
    import sprachen
    satz = {}
    for code in sprachcodes:
        for k in ("set.impressum_text", "set.impressum_text_mit_formular"):
            absaetze = sprachen.TEXTE[code][k].split("<br><br>")
            treffer = [a for a in absaetze if all(p in a for p in PROFILE)]
            assert len(treffer) == 1, (code, k)
            assert "<" not in treffer[0], (code, k)
            satz.setdefault(code, set()).add(treffer[0])
            kontakt = [i for i, a in enumerate(absaetze) if a.startswith("<b>") and i > 0][0]
            assert absaetze.index(treffer[0]) == kontakt - 1, (code, k)
        assert len(satz[code]) == 1, code
    assert satz["de"] == {"Dieses Impressum gilt auch für unsere Profile auf TikTok, Instagram und YouTube."}
    _bauen(tmp_path, monkeypatch, True)
    impressum = (tmp_path / "seite" / "impressum.html").read_text(encoding="utf-8")
    for code in sprachcodes:
        assert next(iter(satz[code])) in impressum, code
