# -*- coding: utf-8 -*-
"""Die Versionsnummer, die man sieht (30.10.2026, Ajdin: "ja mach so").

Bis v108 stand "1.0" fest in sprachen.py (app.fuss, app.ueber_kurz), und im
Play Store stand ebenfalls 1.0 - hochgezaehlt wurde nur der versionCode.
Seitdem steht die Nummer nur noch in versionName in build.gradle der Huelle,
immer als NAECHSTE Store-Version. app_bauen.py setzt sie in die Kopie
www/index.html ein (Debug-Paket und --nur-abgleich mit "-test") und hebt sie
erst nach einem fertigen --aab an: 1.1 -> 1.2, 1.9 -> 1.10. Die App zeigt
sie ueber {version}.

Hier ohne Gradle und ohne Huelle: build.gradle und www/index.html sind
Probedateien, alles, was prueft, kopiert oder baut, ist eine Attrappe. Wie
es in der App aussieht, prueft tests_e2e/test_version.py.
"""
import io
import os
import re
import types

import pytest

# So wie in der Huelle: CRLF, versionNameSuffix im debug-Block.
GRADLE = ('android {\r\n    defaultConfig {\r\n        versionCode %d\r\n'
          '        versionName "%s"\r\n    }\r\n    buildTypes {\r\n'
          '        debug {\r\n            versionNameSuffix "-test"\r\n        }\r\n'
          '    }\r\n}\r\n')
INDEX = ("<script>\r\n/* Rueckfallwert, siehe app_bauen.version_einsetzen */\r\n"
         "const APP_VERSION = '1.1';\r\nconst ADMOB_TEST = false;\r\n</script>\r\n")


def _gradle(code=111, name="1.1"):
    return (GRADLE % (code, name)).encode("utf-8")


def _index(wert):
    return INDEX.replace("'1.1'", "'%s'" % wert).encode("utf-8")


# ------------------------------------------------------------- die Regel ---
@pytest.mark.parametrize("alt, neu", [
    ("1.0", "1.1"),
    ("1.1", "1.2"),
    ("1.9", "1.10"),          # ganze Zahlen, keine Dezimalen: nicht 2.0
    ("1.10", "1.11"),
    ("1.99", "1.100"),
    ("2.0", "2.1"),
    ("10.9", "10.10"),
])
def test_naechster_versionsname(alt, neu):
    import app_bauen
    assert app_bauen.naechster_versionsname(alt) == neu


@pytest.mark.parametrize("falsch", [
    "", "1", "1.", ".1", "1.1.0", "v1.1", "1.1-test", "1.01", "01.1", "0.1",
    " 1.1", "1.1 ", "1,1", "1.1\n", "١.١", None, 1.1, 1, True,
])
def test_naechster_versionsname_unsinn(falsch):
    import app_bauen
    with pytest.raises(ValueError):
        app_bauen.naechster_versionsname(falsch)


# ------------------------------------------------- build.gradle anheben ---
def test_anheben_nur_die_zahl(tmp_path):
    """1.1 -> 1.2 und 1.9 -> 1.10; Zeilenenden (CRLF), versionCode und
    versionNameSuffix bleiben Byte fuer Byte."""
    import app_bauen
    gradle = tmp_path / "build.gradle"
    gradle.write_bytes(_gradle(111, "1.1"))
    assert app_bauen.versionsname_lesen(str(gradle)) == "1.1"
    assert app_bauen.versionsname_anheben(str(gradle)) == ("1.1", "1.2")
    assert gradle.read_bytes() == _gradle(111, "1.2")
    gradle.write_bytes(_gradle(111, "1.9"))
    assert app_bauen.versionsname_anheben(str(gradle)) == ("1.9", "1.10")
    assert gradle.read_bytes() == _gradle(111, "1.10")


@pytest.mark.parametrize("inhalt", [
    _gradle(111, "1.1.0"),
    _gradle(111, "v1.1"),
    _gradle(111, "1.1-test"),
    _gradle(111, ""),
    _gradle(111, "1"),
    _gradle(111, "1.1").replace(b'versionName "1.1"', b"versionName = '1.1'"),
    _gradle(111, "1.1").replace(b'versionName "1.1"', b""),
    _gradle(111, "1.1").replace(b'versionName "1.1"', b'versionName "1.1"\r\n        versionName "1.2"'),
])
def test_unbekannte_form_bricht_ab_ohne_zu_schreiben(tmp_path, inhalt):
    import app_bauen
    gradle = tmp_path / "build.gradle"
    gradle.write_bytes(inhalt)
    with pytest.raises(SystemExit):
        app_bauen.versionsname_lesen(str(gradle))
    with pytest.raises(SystemExit):
        app_bauen.versionsname_anheben(str(gradle))
    assert gradle.read_bytes() == inhalt


def test_ohne_build_gradle_bricht_ab(tmp_path):
    import app_bauen
    for f in (app_bauen.versionsname_lesen, app_bauen.versionsname_anheben):
        with pytest.raises(SystemExit):
            f(str(tmp_path / "fehlt.gradle"))


# ------------------------------------------------- Einsetzen in die Kopie ---
def test_einsetzen_store_und_debug(tmp_path):
    """Store-Bau: die Nummer, wie sie in build.gradle steht. Debug-Paket und
    --nur-abgleich: mit "-test". Sonst aendert sich kein Byte."""
    import app_bauen
    kopie = tmp_path / "index.html"
    kopie.write_bytes(_index("1.1"))
    assert app_bauen.version_einsetzen("1.4", pfad=str(kopie)) == "1.4"
    assert kopie.read_bytes() == _index("1.4")
    # Die Kopie wird bei jedem Bau neu aus web/ gezogen; hier geht es auch
    # ueber einen schon eingesetzten Wert hinweg.
    assert app_bauen.version_einsetzen("1.10", test=True, pfad=str(kopie)) == "1.10-test"
    assert kopie.read_bytes() == _index("1.10-test")


@pytest.mark.parametrize("inhalt", [
    "<script>\r\nconst ADMOB_TEST = false;\r\n</script>\r\n",                      # fehlt
    INDEX + "const APP_VERSION = '1.1';\r\n",                                     # doppelt
    INDEX.replace("const APP_VERSION", "  const APP_VERSION"),                    # eingerueckt
    INDEX.replace("const APP_VERSION = '1.1';", "// const APP_VERSION = '1.1';"),  # nur im Kommentar
    INDEX.replace("const APP_VERSION", "let APP_VERSION"),
])
def test_einsetzen_ohne_anker_bricht_ab(tmp_path, inhalt):
    import app_bauen
    kopie = tmp_path / "index.html"
    kopie.write_bytes(inhalt.encode("utf-8"))
    with pytest.raises(SystemExit):
        app_bauen.version_einsetzen("1.1", pfad=str(kopie))
    assert kopie.read_bytes() == inhalt.encode("utf-8")


@pytest.mark.parametrize("name", ["1.1-test", "1.1.0", "1.1'; alert(1); '", "", None])
def test_einsetzen_nur_gepruefte_nummern(tmp_path, name):
    """Was eingesetzt wird, steht in einem JavaScript-Text - nur die Form
    Hauptzahl.Nebenzahl kommt hinein, "-test" haengt version_einsetzen
    selbst an."""
    import app_bauen
    kopie = tmp_path / "index.html"
    kopie.write_bytes(_index("1.1"))
    with pytest.raises(SystemExit):
        app_bauen.version_einsetzen(name, pfad=str(kopie))
    assert kopie.read_bytes() == _index("1.1")


def test_einsetzen_nie_in_web(wurzel):
    import app_bauen
    quelle = os.path.join(wurzel, "web", "index.html")
    vorher = io.open(quelle, "rb").read()
    with pytest.raises(SystemExit):
        app_bauen.version_einsetzen("9.9", pfad=quelle)
    assert io.open(quelle, "rb").read() == vorher


def test_quelle_hat_den_rueckfallwert_genau_einmal(index_html):
    import app_bauen
    treffer = app_bauen.APP_VERSION_ZEILE.findall(index_html)
    assert len(treffer) == 1, treffer
    wert = re.search(r"'([^']*)'", treffer[0]).group(1)
    assert app_bauen.VERSIONSNAME_FORM.fullmatch(wert), wert


# ------------------------------------------------------ main(): wann was ---
@pytest.fixture
def bau(tmp_path, monkeypatch):
    """build.gradle und www/index.html als Probedateien; versionCode und
    versionName laufen echt, alles andere ist eine Attrappe."""
    import app_bauen
    gradle = tmp_path / "build.gradle"
    gradle.write_bytes(_gradle(111, "1.1"))
    www = tmp_path / "www"
    www.mkdir()
    index = www / "index.html"
    index.write_bytes(_index("1.1"))
    monkeypatch.setattr(app_bauen, "BUILD_GRADLE", str(gradle))
    monkeypatch.setattr(app_bauen, "WWW", str(www))
    aufrufe = []
    for name in ("anmeldung_pruefen", "pruefen", "kopieren", "emir_drueber", "dauer_einsetzen",
                 "cloud_einsetzen", "ton_verkleinern", "testwerbung_einschalten", "capacitor",
                 "plugins_flicken", "debug_apk"):
        monkeypatch.setattr(app_bauen, name, lambda *a, n=name, **k: aufrufe.append(n))

    def neue_kopie(*a, **k):
        # kopieren() zieht www/ jedes Mal frisch aus web/ - mit dem Rueckfallwert
        aufrufe.append("kopieren")
        index.write_bytes(_index("1.1"))

    monkeypatch.setattr(app_bauen, "kopieren", neue_kopie)
    ergebnis = {"aab": True}

    def freigabe():
        aufrufe.append("freigabe_aab")
        if isinstance(ergebnis["aab"], BaseException):
            raise ergebnis["aab"]
        return ergebnis["aab"]

    monkeypatch.setattr(app_bauen, "freigabe_aab", freigabe)
    return types.SimpleNamespace(gradle=gradle, index=index, aufrufe=aufrufe, ergebnis=ergebnis)


def test_store_bau_hebt_erst_danach_an(bau):
    """Das Paket traegt 1.1, danach steht in build.gradle 1.2. Ein zweiter
    Bau (etwa fuer denselben Upload) baut 1.2 und stellt auf 1.3 - eine
    Nummer uebersprungen, das ist erlaubt."""
    import app_bauen
    app_bauen.main(["--aab"])
    assert bau.index.read_bytes() == _index("1.1")
    assert bau.gradle.read_bytes() == _gradle(112, "1.2")
    assert bau.aufrufe.index("freigabe_aab") > bau.aufrufe.index("capacitor")
    app_bauen.main(["--aab", "--testwerbung"])
    assert bau.index.read_bytes() == _index("1.2")
    assert bau.gradle.read_bytes() == _gradle(113, "1.3")


def test_debug_bau_hebt_nicht_an(bau):
    import app_bauen
    app_bauen.main([])
    assert "debug_apk" in bau.aufrufe and "freigabe_aab" not in bau.aufrufe
    assert bau.index.read_bytes() == _index("1.1-test")
    assert bau.gradle.read_bytes() == _gradle(112, "1.1")      # nur versionCode


@pytest.mark.parametrize("argv", [["--nur-abgleich"], ["--nur-abgleich", "--testwerbung"]])
def test_nur_abgleich_hebt_nicht_an(bau, argv):
    """Daraus baut gradlew assembleDebug die Test-App: "-test", und
    build.gradle bleibt ganz, wie sie ist."""
    import app_bauen
    app_bauen.main(argv)
    assert "debug_apk" not in bau.aufrufe and "freigabe_aab" not in bau.aufrufe
    assert bau.index.read_bytes() == _index("1.1-test")
    assert bau.gradle.read_bytes() == _gradle(111, "1.1")


@pytest.mark.parametrize("ausgang", [SystemExit("Gradle meldet einen Fehler"), False, None])
def test_abgebrochener_bau_hebt_nicht_an(bau, ausgang):
    """Gradle bricht ab (SystemExit), oder es entsteht kein Paket (kein Java,
    kein AAB): versionName bleibt, der naechste Versuch baut dieselbe Nummer."""
    import app_bauen
    bau.ergebnis["aab"] = ausgang
    if isinstance(ausgang, BaseException):
        with pytest.raises(SystemExit):
            app_bauen.main(["--aab"])
    else:
        app_bauen.main(["--aab"])
    assert bau.gradle.read_bytes() == _gradle(112, "1.1")


@pytest.mark.parametrize("name", ["1.1.0", "v1.1", "1.1-test", "", "1"])
@pytest.mark.parametrize("argv", [["--aab"], [], ["--nur-abgleich"]])
def test_unbekannte_form_bricht_vor_allem_ab(bau, name, argv):
    """Nichts geprueft, kopiert oder hochgezaehlt - weder versionCode noch
    www/ aendern sich."""
    import app_bauen
    bau.gradle.write_bytes(_gradle(111, name))
    with pytest.raises(SystemExit):
        app_bauen.main(argv)
    assert bau.aufrufe == ["anmeldung_pruefen"]
    assert bau.gradle.read_bytes() == _gradle(111, name)
    assert bau.index.read_bytes() == _index("1.1")


def test_freigabe_aab_meldet_ob_gebaut(tmp_path, monkeypatch):
    """Ohne Java gibt gradle() None zurueck; dann, oder ohne AAB am Ende,
    darf main() versionName nicht anheben."""
    import app_bauen
    signatur = tmp_path / "keystore.properties"
    signatur.write_text("x", encoding="utf-8")
    monkeypatch.setattr(app_bauen, "SIGNATUR", str(signatur))
    monkeypatch.setattr(app_bauen, "ANDROID", str(tmp_path))
    monkeypatch.setattr(app_bauen, "gradle", lambda *a: None)
    assert app_bauen.freigabe_aab() is False
    monkeypatch.setattr(app_bauen, "gradle", lambda *a: True)
    assert app_bauen.freigabe_aab() is False
    aab = tmp_path / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
    aab.parent.mkdir(parents=True)
    aab.write_bytes(b"PK")
    assert app_bauen.freigabe_aab() is True


def test_echte_huelle_hat_die_form():
    """Die build.gradle der Huelle, wenn sie auf diesem Rechner liegt."""
    import app_bauen
    if not os.path.isfile(app_bauen.BUILD_GRADLE):
        pytest.skip("keine Huelle")
    assert app_bauen.VERSIONSNAME_FORM.fullmatch(app_bauen.versionsname_lesen())


# ---------------------------------------------------- Texte und die App ---
@pytest.mark.parametrize("key, anfang", [
    ("app.fuss", r"Zmaj v\{version\} · "),
    ("app.ueber_kurz", r"Zmaj \w+ \{version\} · "),       # Version, Sürüm, versie, versjon ...
])
def test_sprachen_mit_platzhalter(sprachcodes, key, anfang):
    """Jede Sprache hat {version} genau einmal, an der Stelle der alten
    Nummer, und "1.0" steht dort nicht mehr."""
    import sprachen
    assert len(sprachcodes) == 8
    for code in sprachcodes:
        v = sprachen.texte(code)[key]
        assert v.count("{version}") == 1, (code, key, v)
        assert "1.0" not in v, (code, key, v)
        assert re.match(anfang, v), (code, key, v)


def test_t_setzt_version_aus_app_version(index_html):
    """{version} fuellt t() selbst, fuer jeden Aufruf - nicht nur applyTexts().
    APP_VERSION steht vor t(), sonst gaebe es beim ersten Text einen Fehler."""
    m = re.search(r"\nfunction t\(key, vars\)\{(.*?)\n\}", index_html, re.S)
    assert m, "t() fehlt"
    assert "{version: APP_VERSION}" in m.group(1)
    assert index_html.index("\nconst APP_VERSION = ") < m.start()


def test_versionszeile_traegt_weiter_den_schalter(index_html):
    """Die Versionszeile in den Einstellungen ist auch der versteckte
    Schalter (siebenmal tippen). Element und Ereignis muessen bleiben."""
    assert len(re.findall(r'<div [^>]*id="ueberZeile"[^>]*data-t="app\.ueber_kurz"', index_html)) == 1
    m = re.search(r"function dauerVollVerdrahten\(\)\{(.*?)\n\}", index_html, re.S)
    assert m, "dauerVollVerdrahten() fehlt"
    assert "$('ueberZeile')" in m.group(1) and "addEventListener('click'" in m.group(1)
    assert "if(++n < 7) return;" in m.group(1)
    assert '<footer data-t="app.fuss"></footer>' in index_html
