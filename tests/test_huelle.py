# -*- coding: utf-8 -*-
"""huelle.ordner() findet die Android-Hülle unter beiden Namen.

Bis 04.10.2026 kannten die Bauskripte nur ../zmaj-android; ein frischer
git clone heißt aber zmaj-huelle, und der Bau brach dann ab."""
import os

import pytest


def test_umgebungsvariable_geht_vor(tmp_path):
    import huelle
    assert huelle.ordner({"ZMAJ_HUELLE": str(tmp_path)}, str(tmp_path / "x")) == str(tmp_path)


def test_alter_name_vor_neuem(tmp_path):
    import huelle
    (tmp_path / "zmaj-android").mkdir()
    (tmp_path / "zmaj-huelle").mkdir()
    assert huelle.ordner({}, str(tmp_path)) == os.path.join(str(tmp_path), "zmaj-android")


def test_frischer_klon_wird_gefunden(tmp_path):
    import huelle
    (tmp_path / "zmaj-huelle").mkdir()
    assert huelle.ordner({}, str(tmp_path)) == os.path.join(str(tmp_path), "zmaj-huelle")


def test_ohne_huelle_der_gewohnte_pfad(tmp_path):
    import huelle
    assert huelle.ordner({}, str(tmp_path)) == os.path.join(str(tmp_path), "zmaj-android")


def test_alle_bauskripte_nutzen_huelle(wurzel):
    for name in ("app_bauen.py", "admob_scharf.py", "projekt_sichern.py"):
        text = open(os.path.join(wurzel, name), encoding="utf-8").read()
        assert "huelle.ordner()" in text, name


def test_testwerbung_nur_in_der_kopie(tmp_path, wurzel):
    """--testwerbung schaltet in der Paket-Kopie auf Testanzeigen; die Quelle
    muss den Anker genau einmal haben, sonst bricht der Bau ab. 10.10.2026."""
    import app_bauen
    quelle = open(os.path.join(wurzel, "web", "index.html"), encoding="utf-8").read()
    assert quelle.count(app_bauen.TESTWERBUNG_AUS) == 1
    kopie = tmp_path / "index.html"
    kopie.write_text("a\n" + app_bauen.TESTWERBUNG_AUS + "\nb\n", encoding="utf-8")
    app_bauen.testwerbung_einschalten(str(kopie))
    text = kopie.read_text(encoding="utf-8")
    assert app_bauen.TESTWERBUNG_AN in text and app_bauen.TESTWERBUNG_AUS not in text


# Pflicht-Updates (Ajdin, 10.10.2026): Die App haelt ein Update fuer Pflicht,
# wenn sein versionCode ein Vielfaches von 100 ist. --pflicht muss genau dort
# landen, ein normaler Bau nie.
@pytest.mark.parametrize("aktuell, pflicht, erwartet", [
    (98, False, 99),
    (99, False, 101),
    (100, False, 101),
    (199, False, 201),
    (0, False, 1),
    (98, True, 100),
    (99, True, 100),
    (100, True, 200),
    (101, True, 200),
    (0, True, 100),
])
def test_naechste_versionsnummer(aktuell, pflicht, erwartet):
    import app_bauen
    assert app_bauen.naechste_versionsnummer(aktuell, pflicht) == erwartet


def test_normaler_bau_landet_nie_auf_pflicht():
    import app_bauen
    for n in range(0, 1001):
        normal = app_bauen.naechste_versionsnummer(n)
        pflicht = app_bauen.naechste_versionsnummer(n, pflicht=True)
        assert normal > n and normal % 100 != 0, n
        assert n < pflicht <= n + 100 and pflicht % 100 == 0, n


def test_naechste_versionsnummer_unsinn():
    import app_bauen
    for falsch in (-1, "98", 98.0, True, None):
        with pytest.raises(ValueError):
            app_bauen.naechste_versionsnummer(falsch)
    grenze = app_bauen.HOECHSTE_VERSIONSNUMMER
    assert app_bauen.naechste_versionsnummer(grenze - 1, pflicht=True) == grenze
    with pytest.raises(ValueError):
        app_bauen.naechste_versionsnummer(grenze - 1)       # 2.100.000.000 waere Pflicht
    with pytest.raises(ValueError):
        app_bauen.naechste_versionsnummer(grenze, pflicht=True)


def test_versionsnummer_in_build_gradle(tmp_path):
    """Nur die Zahl aendert sich, Zeilenenden (CRLF) und alles andere bleiben."""
    import app_bauen
    gradle = tmp_path / "build.gradle"
    vorher = ('android {\r\n    defaultConfig {\r\n        versionCode 98\r\n'
              '        versionName "1.0"\r\n    }\r\n}\r\n')
    gradle.write_bytes(vorher.encode("utf-8"))
    assert app_bauen.versionsnummer_hochzaehlen(pflicht=True, pfad=str(gradle)) == 100
    assert gradle.read_bytes().decode("utf-8") == vorher.replace("versionCode 98", "versionCode 100")
    assert app_bauen.versionsnummer_hochzaehlen(pfad=str(gradle)) == 101
    gradle.write_bytes(vorher.replace("98", "99").encode("utf-8"))
    assert app_bauen.versionsnummer_hochzaehlen(pfad=str(gradle)) == 101


def test_pflicht_ohne_versionscode_bricht_ab(tmp_path):
    """Ein Paket, das man fuer Pflicht haelt und das keins ist, darf nicht entstehen."""
    import app_bauen
    with pytest.raises(SystemExit):
        app_bauen.versionsnummer_hochzaehlen(pflicht=True, pfad=str(tmp_path / "fehlt.gradle"))
    leer = tmp_path / "build.gradle"
    leer.write_text("android {}\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        app_bauen.versionsnummer_hochzaehlen(pflicht=True, pfad=str(leer))
    assert app_bauen.versionsnummer_hochzaehlen(pfad=str(leer)) is None


@pytest.mark.parametrize("argv", [["--plicht"], ["--aab", "pflicht"], ["--pflicht", "--nur-abgleich"]])
def test_vertippter_schalter_bricht_ab(argv):
    """Aus einem vertippten --pflicht darf kein sanftes Update werden."""
    import app_bauen
    with pytest.raises(SystemExit):
        app_bauen.schalter_lesen(argv)


def test_bekannte_schalter():
    import app_bauen
    assert app_bauen.schalter_lesen([]) == set()
    assert app_bauen.schalter_lesen(["--aab", "--pflicht", "--testwerbung"]) == {
        "--aab", "--pflicht", "--testwerbung"}


def test_main_bricht_vor_dem_bau_ab(monkeypatch):
    """main() prueft die Schalter zuerst: Bei "--plicht" wird nichts geprueft,
    kopiert oder hochgezaehlt."""
    import app_bauen

    def verboten(*args, **kwargs):
        raise AssertionError("darf vor dem Abbruch nicht laufen")

    for name in ("pruefen", "kopieren", "versionsnummer_hochzaehlen"):
        monkeypatch.setattr(app_bauen, name, verboten)
    with pytest.raises(SystemExit):
        app_bauen.main(["--plicht"])


def test_main_reicht_pflicht_durch(monkeypatch):
    """--pflicht kommt bei versionsnummer_hochzaehlen an, ein normaler Bau nicht."""
    import app_bauen
    aufrufe = []
    for name in ("pruefen", "kopieren", "emir_drueber", "capacitor",
                 "plugins_flicken", "freigabe_aab", "debug_apk"):
        monkeypatch.setattr(app_bauen, name, lambda *args, n=name, **kwargs: aufrufe.append(n))

    def hochzaehlen(pflicht=False):
        aufrufe.append(("nummer", pflicht))
        return 200 if pflicht else 201

    monkeypatch.setattr(app_bauen, "versionsnummer_hochzaehlen", hochzaehlen)
    app_bauen.main(["--aab", "--pflicht"])
    assert ("nummer", True) in aufrufe and "freigabe_aab" in aufrufe and "debug_apk" not in aufrufe
    aufrufe.clear()
    app_bauen.main(["--aab"])
    assert ("nummer", False) in aufrufe and ("nummer", True) not in aufrufe
