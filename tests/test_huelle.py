# -*- coding: utf-8 -*-
"""huelle.ordner() findet die Android-Hülle unter beiden Namen.

Bis 04.10.2026 kannten die Bauskripte nur ../zmaj-android; ein frischer
git clone heißt aber zmaj-huelle, und der Bau brach dann ab."""
import os


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
