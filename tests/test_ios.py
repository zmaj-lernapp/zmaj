# -*- coding: utf-8 -*-
"""iPhone und iPad (30.10.2026, iOS_Plan.md 3.5-3.7 und 3.9).

Die Seite ist dieselbe wie auf Android; was auf iOS anders ist, haengt an
EINER Weiche (PLATTFORM). Hier geprueft, was ohne Browser geht: die Weiche
selbst, die _ios-Texte in allen acht Sprachen (Richtlinie 2.3.10: keine
andere Plattform nennen), die Rechtstexte fuer iOS und app_bauen.py --ios.
Das Verhalten im Browser pruefen tests_e2e/test_ios.py.
"""
import io
import json
import os
import re
import shutil
import subprocess

import pytest

# Was auf iOS nirgends stehen darf - in keiner der acht Sprachen.
VERBOTEN = re.compile(r"Google Play|Play Store|Play-butikk|Play Butik|Android|Google-Konto|Google account"
                      r"|Google hesab|Google-konto|compte Google|Google-account|Google Commerce"
                      r"|Familienmediathek|Family Library")


# ------------------------------------------------------------------ Weiche ---
def test_plattform_an_einer_stelle(index_html):
    """Entschieden wird einmal, im Skript im Kopf; das grosse Skript liest es
    nur. Sonst ruft niemand getPlatform() auf."""
    assert index_html.count("window.ZMAJ_PLATTFORM = ") == 1
    assert index_html.count("const PLATTFORM = ") == 1
    kopf = index_html[:index_html.index("<style>")]
    # getPlatform nur im Kopf (Aufruf, typeof-Pruefung, Kommentare)
    assert index_html.count("getPlatform") == kopf.count("getPlatform") > 0
    assert "C.getPlatform()" in kopf
    # Capacitor ohne getPlatform (alte Huelle, die Browsertests) heisst Android.
    assert "(C.Plugins ? 'android' : 'web')" in kopf


def test_viewport_fit_nur_auf_ios(index_html):
    """viewport-fit=cover nur fuer iOS - Android bleibt, wie es war."""
    zeile = re.search(r'<meta name="viewport"[^>]*>', index_html).group(0)
    assert "viewport-fit" not in zeile
    assert "viewport-fit=cover" in index_html[:index_html.index("<style>")]
    assert 'html[data-plattform="ios"] body{' in index_html
    assert "env(safe-area-inset-top" in index_html


def test_ios_weichen_im_skript(index_html):
    """Die Stellen aus iOS_Plan.md 3.5, jede an der Weiche."""
    for stueck in (
        "const geraeteZurueck = () => PLATTFORM === 'android'",   # Zurueck-Knopf
        "const hasTTS = !IST_IOS",                                # keine iOS-Stimme statt Emir
        "const canBuzz = !IST_IOS",                               # Vibration
        "(IST_IOS && T[key + '_ios'] !== undefined)",             # Texte
        "const ADMOB_ID = IST_IOS ? ADMOB_ID_IOS : ADMOB_ID_ANDROID;",
        "const updPlugin = () => (!IST_IOS",                      # kein ZmajUpdate
        "if(!IST_IOS){\r\n    dauerVollVerdrahten();",            # versteckte Schalter
        "if(IST_IOS) appleBewertung(); else zeigeBewertung();",   # keine eigene Karte
    ):
        assert stueck.replace("\r\n", "\n") in index_html.replace("\r\n", "\n"), stueck


# ------------------------------------------------------------------ Texte ---
def _ios_schluessel():
    import sprachen
    return sorted(k for k in sprachen.TEXTE["de"] if k.endswith("_ios"))


def test_ios_texte_in_allen_sprachen(sprachcodes):
    """Jede _ios-Fassung gibt es in allen acht Sprachen selbst (nicht nur
    ueber den deutschen Rueckfall), und zu jeder die gewoehnliche."""
    import sprachen
    schluessel = _ios_schluessel()
    assert len(schluessel) >= 9
    for code in sprachcodes:
        for k in schluessel:
            assert sprachen.TEXTE[code].get(k), (code, k)
            assert k[:-4] in sprachen.TEXTE["de"], k


def test_neue_ios_texte_in_allen_sprachen(sprachcodes):
    import sprachen
    for k in ("anm.apple", "anm.spaeter", "konto.fehler_apple", "set.konto_weg_apple",
              "voll.wiederherstellen", "voll.wiederhergestellt", "voll.nichts_gefunden",
              "werbung.melden", "werbung.melden_text", "werbung.melden_wann"):
        for code in sprachcodes:
            assert sprachen.TEXTE[code].get(k), (code, k)


def test_apple_knopf_heisst_wie_bei_apple(sprachcodes):
    """Die Titel aus Apples eigenem Knopf (appleid.auth.js, je Sprache,
    abgelesen am 30.10.2026). App Review lehnt eigene Uebersetzungen ab."""
    import sprachen
    soll = {"de": "Mit Apple anmelden", "en": "Sign in with Apple", "tr": "Apple ile Giriş Yap",
            "sv": "Logga in med Apple", "nl": "Log in met Apple", "nb": "Logg på med Apple",
            "da": "Log ind med Apple", "fr": "Connexion avec Apple"}
    assert sorted(soll) == sorted(sprachcodes)
    for code, titel in soll.items():
        assert sprachen.TEXTE[code]["anm.apple"] == titel, code


def test_ios_texte_nennen_keine_andere_plattform(sprachcodes):
    """Richtlinie 2.3.10. Auch die Rechtstexte fuer iOS."""
    import sprachen
    for code in sprachcodes:
        t = sprachen.texte(code)
        for k, v in t.items():
            if k.endswith("_ios"):
                m = VERBOTEN.search(v)
                assert not m, (code, k, v[max(0, m.start() - 60):m.end() + 20])


def test_ios_platzhalter_wie_im_original(sprachcodes):
    """{preis}, {anbieter} und HTML wie in der gewoehnlichen Fassung."""
    import sprachen
    for code in sprachcodes:
        t = sprachen.texte(code)
        for k, v in t.items():
            if not k.endswith("_ios"):
                continue
            original = t[k[:-4]]
            assert sorted(re.findall(r"\{\w+\}", v)) == sorted(re.findall(r"\{\w+\}", original)), (code, k)


def test_ios_rechtstexte(sprachcodes):
    """Nutzungsbedingungen und Datenschutz fuer iOS: Apple verkauft, kein
    Google Play, und alles andere wie fuer Android."""
    import sprachen
    for code in sprachcodes:
        t = sprachen.texte(code)
        for k in ("set.agb_text_ios", "set.datenschutz_text_ios"):
            assert "Apple Distribution International" in t[k], (code, k)
            assert t[k].count("<b>") == t[k[:-4]].count("<b>"), (code, k)
        assert "reportaproblem.apple.com" in t["set.agb_text_ios"], code
        # die App-Tracking-Transparenz, weil Werbung laeuft
        assert "Apple" in t["set.datenschutz_text_ios"].split("AdMob", 1)[1], code


def test_ios_rechtstexte_brechen_ab_wenn_android_sich_aendert(monkeypatch):
    """Aendert jemand einen Satz fuer Android, steht der alte Satz fuer iOS
    nicht mehr da - texte() bricht dann ab, statt still Google Play zu
    zeigen."""
    import sprachen
    alt, _ = sprachen.IOS_RECHT["de"]["agb"][0]
    roh = dict(sprachen.TEXTE["de"])
    roh["set.agb_text"] = roh["set.agb_text"].replace(alt, alt.replace("Google", "Gugel"))
    monkeypatch.setitem(sprachen.TEXTE, "de", roh)
    with pytest.raises(ValueError):
        sprachen.texte("de")


def test_ios_keine_rechtstexte_ohne_konto(monkeypatch):
    """Die Web-Demo (ohne Pflichtkonto) hat keine iOS-Fassung."""
    import sprachen
    monkeypatch.setattr(sprachen, "KONTO_PFLICHT", False)
    assert "set.agb_text_ios" not in sprachen.texte("de")


def test_html_kennt_die_neuen_schluessel(index_html):
    for k in ("anm.apple", "anm.spaeter", "konto.fehler_apple", "voll.wiederherstellen",
              "werbung.melden", "set.konto_weg_apple"):
        assert k in index_html, k


# ------------------------------------------------------------- Bauskript ---
def test_schalter_ios():
    import app_bauen
    assert app_bauen.schalter_lesen(["--ios"]) == {"--ios"}
    assert app_bauen.schalter_lesen(["--ios", "--ci", "--huelle=x"]) == {"--ios", "--ci", "--huelle=x"}
    for falsch in (["--ios", "--aab"], ["--ios", "--pflicht"], ["--ci"], ["--huelle=x"],
                   ["--ios", "--huelle="], ["--ios", "--hülle=x"]):
        with pytest.raises(SystemExit):
            app_bauen.schalter_lesen(falsch)


def test_ios_huelle_standard_und_schalter(tmp_path, monkeypatch):
    import app_bauen
    monkeypatch.delenv("ZMAJ_HUELLE_IOS", raising=False)
    assert app_bauen.ios_huelle({"--ios"}) == os.path.join(os.path.dirname(app_bauen.HIER), "zmaj-huelle-ios")
    assert app_bauen.ios_huelle({"--ios", "--huelle=%s" % tmp_path}) == str(tmp_path)
    monkeypatch.setenv("ZMAJ_HUELLE_IOS", str(tmp_path / "x"))
    assert app_bauen.ios_huelle({"--ios"}) == str(tmp_path / "x")


def test_ton_schluessel_mit_codec():
    """Opus behaelt seinen alten Namen (kein Android-Bau wandelt neu um), AAC
    hat einen eigenen."""
    import app_bauen
    h = "cd" * 32
    assert app_bauen.ton_schluessel(h, "g01.mp3") == h[:32] + "-24k"
    assert app_bauen.ton_schluessel(h, "g01.mp3", "aac") == h[:32] + "-32k-aac"
    assert app_bauen.ton_schluessel(h, "w0001.mp3", "aac").startswith(h[:32] + "-32k-aac-a")
    assert app_bauen.TON_CODECS["aac"]["endung"] == ".m4a"


def test_ton_index_auf_m4a():
    import app_bauen
    index = {"toene": [{"key": "a", "datei": "w0001.mp3"}, {"key": "b", "datei": "g01.mp3"}]}
    assert app_bauen.ton_index_umschreiben(index, ".m4a") == 2
    assert [e["datei"] for e in index["toene"]] == ["w0001.m4a", "g01.m4a"]


def _ffmpeg():
    import app_bauen
    return app_bauen.ffmpeg_finden()


def test_ton_nach_aac_mit_zwischenspeicher(tmp_path):
    """Echte Umwandlung nach AAC (.m4a), mono 32 kbit/s, und beim zweiten
    Mal kommt alles aus dem Zwischenspeicher."""
    import app_bauen
    ffmpeg = _ffmpeg()
    if not ffmpeg or not os.path.isfile(ffmpeg):
        pytest.skip("ffmpeg fehlt")
    audio = tmp_path / "audio"
    audio.mkdir()
    for name, hz in (("w0001.mp3", 440), ("g01.mp3", 660)):
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
                        "-i", "sine=frequency=%d:duration=1" % hz, "-ar", "24000", "-ac", "1",
                        "-b:a", "48k", str(audio / name)], check=True)
    roh = {n: (audio / n).read_bytes() for n in ("w0001.mp3", "g01.mp3")}
    (audio / "index.json").write_text(json.dumps({"version": 1, "toene": [
        {"key": "eins", "datei": "w0001.mp3"}, {"key": "g", "datei": "g01.mp3"}]}), encoding="utf-8")
    zwischen = tmp_path / "zwischen"
    app_bauen.ton_verkleinern(str(audio), ffmpeg=ffmpeg, zwischen=str(zwischen), codec="aac")
    assert sorted(os.listdir(audio)) == ["g01.m4a", "index.json", "w0001.m4a"]
    index = json.loads((audio / "index.json").read_text(encoding="utf-8"))
    assert [e["datei"] for e in index["toene"]] == ["w0001.m4a", "g01.m4a"]
    assert (audio / "w0001.m4a").read_bytes()[4:8] == b"ftyp"
    gespeichert = sorted(os.listdir(zwischen))
    assert len(gespeichert) == 2 and all(n.endswith(".m4a") for n in gespeichert)
    zeiten = {n: os.path.getmtime(os.path.join(zwischen, n)) for n in gespeichert}
    # Zweiter Lauf mit denselben MP3s: nichts wird neu umgewandelt.
    for n in os.listdir(audio):
        os.remove(os.path.join(audio, n))
    for n, b in roh.items():
        (audio / n).write_bytes(b)
    (audio / "index.json").write_text(json.dumps({"version": 1, "toene": [
        {"key": "eins", "datei": "w0001.mp3"}, {"key": "g", "datei": "g01.mp3"}]}), encoding="utf-8")
    app_bauen.ton_verkleinern(str(audio), ffmpeg=ffmpeg, zwischen=str(zwischen), codec="aac")
    assert {n: os.path.getmtime(os.path.join(zwischen, n)) for n in os.listdir(zwischen)} == zeiten


def test_xcconfig_lesen(tmp_path):
    import app_bauen
    p = tmp_path / "ios_zugang.xcconfig"
    p.write_text("// Kommentar\n#include? \"x\"\nZMAJ_A = 1 // dahinter\nZMAJ_LEER =\nkaputt\n", encoding="utf-8")
    assert app_bauen.xcconfig_lesen(str(p)) == {"ZMAJ_A": "1", "ZMAJ_LEER": ""}
    assert app_bauen.xcconfig_lesen(str(tmp_path / "fehlt")) == {}


def _kopie(tmp_path, wurzel):
    kopie = tmp_path / "www" / "index.html"
    kopie.parent.mkdir()
    shutil.copyfile(os.path.join(wurzel, "web", "index.html"), str(kopie))
    return kopie


def test_ios_zugang_einsetzen(tmp_path, wurzel):
    import app_bauen
    kopie = _kopie(tmp_path, wurzel)
    zugang = tmp_path / "ios_zugang.xcconfig"
    # Erfunden, nur in der Form echt.
    inter, lohn = "ca-app-pub-1111111111111111/2222222222", "ca-app-pub-1111111111111111/3333333333"
    zugang.write_text("ZMAJ_ADMOB_INTERSTITIAL = %s\nZMAJ_ADMOB_BELOHNT = %s\nZMAJ_APPLE_APP_ID = 1234567890\n"
                      % (inter, lohn), encoding="utf-8")
    assert app_bauen.ios_zugang_einsetzen(str(kopie), str(zugang)) == [
        "ZMAJ_ADMOB_INTERSTITIAL", "ZMAJ_ADMOB_BELOHNT", "ZMAJ_APPLE_APP_ID"]
    text = kopie.read_bytes().decode("utf-8")
    assert "interstitial: '%s'" % inter in text and "belohnt:      '%s'" % lohn in text
    assert "const APPLE_APP_ID = '1234567890';" in text
    # die Android-Bloecke bleiben, wie sie sind
    assert "ca-app-pub-9105747905460295/9764395638" in text
    # Quelle unveraendert
    quelle = io.open(os.path.join(wurzel, "web", "index.html"), encoding="utf-8").read()
    assert app_bauen.IOS_APPLE_ID_ZEILE in quelle


def test_ios_zugang_ohne_datei_bleibt_test(tmp_path, wurzel):
    import app_bauen
    kopie = _kopie(tmp_path, wurzel)
    vorher = kopie.read_bytes()
    assert app_bauen.ios_zugang_einsetzen(str(kopie), str(tmp_path / "fehlt.xcconfig")) == []
    assert kopie.read_bytes() == vorher


@pytest.mark.parametrize("inhalt", [
    "ZMAJ_ADMOB_INTERSTITIAL = ca-app-pub-1111111111111111~2222222222\n"
    "ZMAJ_ADMOB_BELOHNT = ca-app-pub-1111111111111111/3333333333\n",       # App-ID statt Block
    "ZMAJ_ADMOB_INTERSTITIAL = ca-app-pub-1111111111111111/2222222222\n",   # nur einer
    "ZMAJ_APPLE_APP_ID = id123\n",
])
def test_ios_zugang_falsche_form_bricht_ab(tmp_path, wurzel, inhalt):
    import app_bauen
    kopie = _kopie(tmp_path, wurzel)
    vorher = kopie.read_bytes()
    zugang = tmp_path / "ios_zugang.xcconfig"
    zugang.write_text(inhalt, encoding="utf-8")
    with pytest.raises(SystemExit):
        app_bauen.ios_zugang_einsetzen(str(kopie), str(zugang))
    assert kopie.read_bytes() == vorher


def test_ios_zugang_nie_in_web(wurzel, tmp_path):
    import app_bauen
    with pytest.raises(SystemExit):
        app_bauen.ios_zugang_einsetzen(os.path.join(wurzel, "web", "index.html"), str(tmp_path / "x"))


def test_kein_dauer_pruefwert_auf_ios(tmp_path, wurzel):
    import app_bauen
    kopie = _kopie(tmp_path, wurzel)
    app_bauen.dauer_platzhalter_pruefen(str(kopie))          # Platzhalter: in Ordnung
    text = kopie.read_bytes().decode("utf-8").replace("__DAUER_PRUEFWERT__", "a" * 64)
    kopie.write_bytes(text.encode("utf-8"))
    with pytest.raises(SystemExit):
        app_bauen.dauer_platzhalter_pruefen(str(kopie))


def _ios_huelle(tmp_path):
    h = tmp_path / "zmaj-huelle-ios"
    (h / "ios" / "App" / "App.xcodeproj").mkdir(parents=True)
    (h / "ios" / "App" / "App.xcodeproj" / "project.pbxproj").write_text(
        "MARKETING_VERSION = 1.1;\nMARKETING_VERSION = 1.1;\n", encoding="utf-8")
    return h


def _ablauf(monkeypatch, wurzel):
    """ios_bauen() mit aufgezeichneten Schritten statt echter Arbeit."""
    import app_bauen
    aufrufe = []

    def merke(name):
        def f(*args, **kwargs):
            aufrufe.append((name, args, kwargs))
        return f

    for name in ("pruefen", "emir_drueber", "cloud_einsetzen", "ios_zugang_einsetzen", "ton_verkleinern",
                 "capacitor", "testwerbung_einschalten",
                 # Android-Schritte, die auf iOS nie laufen duerfen
                 "dauer_einsetzen", "versionsnummer_hochzaehlen", "plugins_flicken", "debug_apk",
                 "freigabe_aab", "versionsname_lesen", "versionsname_anheben", "anmeldung_pruefen"):
        monkeypatch.setattr(app_bauen, name, merke(name))

    def kopieren(www=None):
        aufrufe.append(("kopieren", (www,), {}))
        os.makedirs(www, exist_ok=True)
        shutil.copyfile(os.path.join(wurzel, "web", "index.html"), os.path.join(www, "index.html"))

    monkeypatch.setattr(app_bauen, "kopieren", kopieren)
    return aufrufe


def test_ios_bauen_ablauf(tmp_path, monkeypatch, wurzel):
    import app_bauen
    h = _ios_huelle(tmp_path)
    aufrufe = _ablauf(monkeypatch, wurzel)
    www = app_bauen.main(["--ios", "--huelle=%s" % h])
    namen = [a[0] for a in aufrufe]
    assert www == os.path.join(str(h), "www")
    assert namen == ["pruefen", "kopieren", "emir_drueber", "cloud_einsetzen", "ios_zugang_einsetzen",
                     "ton_verkleinern", "capacitor"]
    ton = aufrufe[namen.index("ton_verkleinern")]
    assert ton[2] == {"zwischen": os.path.join(str(h), ".ton_aac"), "codec": "aac"}
    assert aufrufe[namen.index("capacitor")][1] == ("ios", str(h))
    assert aufrufe[namen.index("emir_drueber")][1] == (www, os.path.join(str(h), "audio_emir"))
    text = io.open(os.path.join(www, "index.html"), encoding="utf-8").read()
    assert "const APP_VERSION = '1.1';" in text


def test_ios_bauen_ci_ohne_geheimes(tmp_path, monkeypatch, wurzel):
    import app_bauen
    h = _ios_huelle(tmp_path)
    aufrufe = _ablauf(monkeypatch, wurzel)
    app_bauen.main(["--ios", "--ci", "--huelle=%s" % h])
    namen = [a[0] for a in aufrufe]
    assert namen == ["pruefen", "kopieren", "ton_verkleinern"]
    text = io.open(os.path.join(str(h), "www", "index.html"), encoding="utf-8").read()
    assert "const CLOUD_AN = false;" in text and "const APP_VERSION = '1.1-test';" in text


def test_ios_bauen_ohne_huelle(tmp_path, monkeypatch, wurzel):
    import app_bauen
    _ablauf(monkeypatch, wurzel)
    with pytest.raises(SystemExit):
        app_bauen.main(["--ios", "--huelle=%s" % (tmp_path / "gibt-es-nicht")])
