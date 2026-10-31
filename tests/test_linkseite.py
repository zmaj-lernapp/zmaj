# -*- coding: utf-8 -*-
"""Die Linkseite links.html fuer die Profile (Ajdin am 31.10.2026, Weg B in
Release/Social_Media_Recherche_2026-10-31.md, Abschnitt 5.1; am selben Tag
umgebaut: "playstore insta tiktok und yt grosse buttons und datenschutz usw
sehr kleine buttons").

Geprueft wird hier, ohne Browser:
  - Der Play-Link hat genau die Form aus Abschnitt 4.2 (Kanal URL-codiert
    in referrer=), fuer TikTok, Instagram, YouTube und "web".
  - Die Seite steht in acht Sprachen, ohne Skript auf Englisch, mit dem
    Link fuer "web" im HTML. Der Knopf zu Google Play ist Googles Abzeichen
    in der Sprache der Abteilung, darunter Instagram, TikTok und YouTube als
    grosse Knoepfe mit ihrem Zeichen. Klein unten: Kontakt (Formular nur,
    wenn es gebaut wird), Impressum, Datenschutz, Nutzungsbedingungen, der
    KI-Hinweis und der Markenhinweis zu Google Play.
  - Abzeichen und Zeichen sind die heruntergeladenen Dateien, Byte fuer
    Byte (Pruefsummen in grafik/marken/QUELLEN.md), und REUSE.toml nennt sie.
  - Nichts von fremden Servern, eine Content-Security-Policy ohne
    connect-src, und das Skript fasst weder Cookies noch localStorage an
    (§ 25 TDDDG).
  - Das Impressum sagt in allen acht Sprachen, dass es auch fuer die drei
    Profile gilt (Abschnitt 5.1).
Die drei ?von=-Varianten, die Sprache des Handys, die Seite ohne
JavaScript und das Handyformat prueft tests_e2e/test_linkseite.py im
Browser.
"""
import base64
import hashlib
import json
import os
import re
import struct
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


def _fuesse(html):
    return re.findall(r'(?s)<div data-fuss="([a-z]+)" lang="([a-z]+)"( hidden)?>(.*?)</div>', html)


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


def _pruefsummen(wurzel):
    """Die Pruefsummen aus grafik/marken/QUELLEN.md: {pfad: sha256}."""
    text = open(os.path.join(wurzel, "grafik", "marken", "QUELLEN.md"), encoding="utf-8").read()
    return {p: s for s, p in re.findall(r"^    ([0-9a-f]{64})  (\S+)$", text, re.M)}


def test_play_link_wie_in_der_recherche():
    import seite_bauen
    assert seite_bauen.play_link() == RECHERCHE["web"]
    for kanal in seite_bauen.KANAELE:
        assert seite_bauen.play_link(kanal) == RECHERCHE[kanal], kanal
    assert set(seite_bauen.KANAELE) == set(RECHERCHE) - {"web"}


def test_texte_in_allen_acht_sprachen(sprachcodes):
    import seite_bauen
    assert sorted(seite_bauen.LINKS) == sorted(sprachcodes)
    assert sorted(seite_bauen.ABZEICHEN) == sorted(sprachcodes)
    for code in sprachcodes:
        t = seite_bauen.LINKS[code]
        assert set(t) == {"ki", "marke"}, code
        assert t["ki"].strip(), code
        # Zweimal Google Play (Deutsch durchgekoppelt: Google-Play-Logo).
        assert t["marke"].replace("-", " ").count("Google Play") == 2 and "Google LLC" in t["marke"], code
        datei, alt = seite_bauen.ABZEICHEN[code]
        # Googles Dateinamen: Sprache vorn, Norwegisch heisst "no".
        assert datei == "%s_badge_web_generic.png" % ("no" if code == "nb" else code), code
        assert "Google Play" in alt, code
        if code != "en":
            assert t["ki"] != seite_bauen.LINKS["en"]["ki"], code
            assert t["marke"] != seite_bauen.LINKS["en"]["marke"], code
            assert alt != seite_bauen.ABZEICHEN["en"][1], code
    assert seite_bauen.LINKS["en"]["ki"] == "Characters & voices made with AI"
    assert seite_bauen.LINKS["de"]["marke"] == "Google Play und das Google-Play-Logo sind Marken von Google LLC."
    assert seite_bauen.ABZEICHEN["de"][1] == "Jetzt bei Google Play"
    assert seite_bauen.ABZEICHEN["en"][1] == "Get it on Google Play"
    assert set(seite_bauen.ABZEICHEN_MIT_RAND) <= set(sprachcodes)


def test_marken_dateien_unveraendert(wurzel):
    """Abzeichen und Zeichen sind die heruntergeladenen Dateien, Byte fuer
    Byte - jede Datei in grafik/marken hat ihre Pruefsumme in QUELLEN.md."""
    import seite_bauen
    summen = _pruefsummen(wurzel)
    marken = os.path.join(wurzel, "grafik", "marken")
    da = sorted("%s/%s" % (o, d) for o in ("google-play", "simple-icons")
                for d in os.listdir(os.path.join(marken, o)))
    assert sorted(summen) == da
    for pfad, summe in summen.items():
        with open(os.path.join(marken, pfad), "rb") as f:
            assert hashlib.sha256(f.read()).hexdigest() == summe, pfad
    for datei, _ in seite_bauen.ABZEICHEN.values():
        assert "google-play/" + datei in summen, datei
        with open(os.path.join(seite_bauen.ABZEICHEN_ORDNER, datei), "rb") as f:
            kopf = f.read(24)
        # 646 x 250 - darauf beruhen die Masse in LINKS_STIL.
        assert kopf[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", kopf[16:24]) == (646, 250), datei
    for name in seite_bauen.PROFIL_REIHE:
        assert "simple-icons/%s.svg" % name.lower() in summen, name
        box, pfad = seite_bauen.marken_zeichen(name)
        assert box == "0 0 24 24" and len(pfad) > 100, name


def test_reuse_nennt_die_marken(wurzel):
    """REUSE.toml: die Abzeichen als Marke von Google, die Zeichen von Simple
    Icons unter CC0 - jeweils als eigener Eintrag mit Vorrang."""
    text = open(os.path.join(wurzel, "REUSE.toml"), encoding="utf-8").read()
    eintraege = text.split("[[annotations]]")
    google = [e for e in eintraege if 'path = "grafik/marken/google-play/*.png"' in e]
    simple = [e for e in eintraege if 'path = "grafik/marken/simple-icons/*.svg"' in e]
    assert len(google) == 1 and 'SPDX-License-Identifier = "LicenseRef-Google-Brand"' in google[0]
    assert len(simple) == 1 and 'SPDX-License-Identifier = "CC0-1.0"' in simple[0]
    for e in google + simple:
        assert 'precedence = "override"' in e
    for name in ("LicenseRef-Google-Brand.txt", "CC0-1.0.txt"):
        assert os.path.exists(os.path.join(wurzel, "LICENSES", name)), name
    assert "grafik/marken/google-play" in open(os.path.join(wurzel, "LICENSES", "LicenseRef-Google-Brand.txt"),
                                               encoding="utf-8").read()


def test_linkseite_mit_formular(tmp_path, monkeypatch, sprachcodes, wurzel):
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

    # Der Knopf ist das Abzeichen der Sprache und zeigt ohne Skript auf den
    # Link fuer "web". Nur die englische Abteilung laedt ihr Bild sofort.
    knopf = '<a class="play" href="%s">' % escape(RECHERCHE["web"], quote=True)
    assert html.count(knopf) == 8
    for code, _, _, inhalt in teile:
        rand = ' class="rand"' if code in seite_bauen.ABZEICHEN_MIT_RAND else ""
        laden = "" if code == "en" else ' loading="lazy"'
        bild = '<img%s src="google-play-%s.png" width="646" height="250" alt="%s"%s>' % (
            rand, code, escape(seite_bauen.ABZEICHEN[code][1], quote=True), laden)
        assert knopf + bild + "</a>" in inhalt, code
        assert "<h1>%s</h1>" % escape(seite_bauen.START[code][0], quote=False) in inhalt, code

    # Die Abzeichen liegen neben der Seite, unveraendert.
    summen = _pruefsummen(wurzel)
    for code in sprachcodes:
        neben = tmp_path / "seite" / ("google-play-%s.png" % code)
        quelle = "google-play/" + seite_bauen.ABZEICHEN[code][0]
        assert hashlib.sha256(neben.read_bytes()).hexdigest() == summen[quelle], code

    # Instagram, TikTok, YouTube: einmal, in dieser Reihenfolge, mit dem
    # unveraenderten Zeichen und dem Profilnamen.
    assert seite_bauen.PROFIL_REIHE == ("Instagram", "TikTok", "YouTube")
    adressen = dict(seite_bauen.SOZIAL)
    profile = re.findall(r'<li><a class="([a-z]+)" href="([^"]+)" rel="noopener"><span class="symbol">'
                         r'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="([^"]+)"/></svg>'
                         r'</span><span class="name">([A-Za-z]+) <small>(@[a-z.]+)</small></span></a></li>', html)
    assert [p[3] for p in profile] == list(seite_bauen.PROFIL_REIHE)
    for klasse, adresse, pfad, name, profil in profile:
        assert klasse == name.lower() and adresse == adressen[name], name
        assert pfad == seite_bauen.marken_zeichen(name)[1], name
        assert profil == "@zmaj.learnbosnian" and "zmaj.learnbosnian" in adresse, name
    assert html.count("<svg") == 3
    assert [n for n, _ in seite_bauen.SOZIAL] == list(PROFILE)

    # Unten klein, je Sprache: vier Verweise, KI- und Markenhinweis.
    fuesse = _fuesse(html)
    assert [c for c, _, _, _ in fuesse] == sprachcodes
    assert [c for c, _, h, _ in fuesse if not h] == ["en"]
    for code, _, _, inhalt in fuesse:
        verweise = re.findall(r'<a href="([^"]+)">([^<]+)</a>', inhalt)
        assert verweise == [("kontakt.html", escape(sprachen.kontakt_texte(code)["titel"], quote=False)),
                            ("impressum.html", escape(sprachen.texte(code)["set.impressum"], quote=False)),
                            ("datenschutz.html", escape(seite_bauen.START[code][2], quote=False)),
                            ("nutzungsbedingungen.html", escape(seite_bauen.START[code][3], quote=False))], code
        l = seite_bauen.LINKS[code]
        assert '<p class="ki">%s</p>' % escape(l["ki"], quote=False) in inhalt, code
        marke = escape(l["marke"], quote=False).replace("Google LLC", "Google LLC")
        assert '<p class="zeichen">%s</p>' % marke in inhalt, code
    assert html.count('<a href="impressum.html">') == 8
    assert 'href="links.html"' not in html

    # Klein, aber lesbar: 13 px im Fuss (aus STIL), kein kleinerer Wert fuer
    # die Verweise; nur der Markenhinweis hat 12 px.
    assert re.search(r"(?m)^footer\{[^}]*font-size:13px", seite_bauen.STIL)
    stil = seite_bauen.LINKS_STIL
    assert re.findall(r"footer[^{]*\{[^}]*font-size:(\d+)px", stil) == ["12"]
    assert re.search(r"\.wrap>footer \.zeichen\{font-size:12px\}", stil)

    # Nichts von fremden Servern, nur eigene Bilder.
    assert not re.search(r"<script[^>]+src=|<link[^>]+stylesheet|@import|url\(|<iframe|xlink:|<use", html)
    assert re.findall(r'<img [^>]*src="([^"]+)"', html) == (
        ["icon-256.png"] + ["google-play-%s.png" % c for c in sprachcodes])
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
    # Die Sprache aus der ganzen Liste des Handys, nicht nur der ersten.
    assert "navigator.languages" in skript


def test_linkseite_ohne_formular(tmp_path, monkeypatch, sprachcodes):
    """Ohne kontakt.html fuehrt Kontakt zur E-Mail-Adresse, wie auf der
    Startseite - nie zu einer Seite, die es nicht gibt."""
    import seite_bauen
    html = _bauen(tmp_path, monkeypatch, False)
    assert "kontakt.html" not in html
    mail = seite_bauen.post_adresse()
    for code, _, _, inhalt in _fuesse(html):
        assert '<a href="mailto:%s">%s</a>' % (mail, seite_bauen.START[code][4]) in inhalt, code


def test_falsches_zeichen_bricht_ab(tmp_path, monkeypatch):
    """Ein Zeichen, das nicht mehr die Form von Simple Icons hat, wird nicht
    eingebaut - lieber Abbruch als ein veraendertes Logo."""
    import pytest
    import seite_bauen
    (tmp_path / "instagram.svg").write_text('<svg viewBox="0 0 24 24"><path d="M0 0h24v24H0z"/></svg>',
                                            encoding="utf-8")
    monkeypatch.setattr(seite_bauen, "MARKEN_ORDNER", str(tmp_path))
    with pytest.raises(SystemExit):
        seite_bauen.marken_zeichen("Instagram")


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
