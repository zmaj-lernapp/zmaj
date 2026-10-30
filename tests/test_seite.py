# -*- coding: utf-8 -*-
"""Die Internetseite aus seite_bauen.py, seit v109 mit Konto (28.10.2026).

Google Play verlangt fuer Apps mit Konto einen Weg zum Loeschen in der App
UND eine oeffentliche Seite dafuer. Geprueft wird, dass konto-loeschen.html
in allen acht Sprachen beide Wege nennt, dass .nojekyll entsteht (sonst
liefert GitHub Pages .well-known nicht aus) und dass assetlinks.json nur
mit den Fingerabdruecken aus der privaten Huelle geschrieben wird - und
dann gueltig ist.
"""
import json
import os

import pytest

ABDRUCK = ":".join(["AB"] * 32)


def _bauen(tmp_path, monkeypatch, abdruecke=None):
    import huelle
    import seite_bauen
    ziel = tmp_path / "seite"
    privat = tmp_path / "huelle"
    privat.mkdir()
    if abdruecke is not None:
        (privat / "fingerabdruecke.json").write_text(json.dumps(abdruecke), encoding="utf-8")
    monkeypatch.setattr(seite_bauen, "ZIEL", str(ziel))
    monkeypatch.setattr(huelle, "ordner", lambda *a, **k: str(privat))
    seite_bauen.main()
    return ziel


def test_loeschseite_nennt_app_und_mail_in_jeder_sprache():
    import seite_bauen
    import sprachen
    codes = [s["code"] for s in sprachen.SPRACHEN]
    assert sorted(seite_bauen.LOESCHEN) == sorted(codes)
    for code in codes:
        text = seite_bauen.LOESCHEN[code]["text"]
        # Der Weg in der App heisst genau wie die Zeile in der App.
        assert "<i>%s</i>" % sprachen.texte(code)["set.konto_loeschen"] in text, code
        assert 'href="mailto:{mail}"' in text and "30" in text, code
        assert "Google Play" in text, code
        assert text.count("<p>") == text.count("</p>") == 8, code


def test_seite_mit_nojekyll_und_assetlinks(tmp_path, monkeypatch):
    import seite_bauen
    ziel = _bauen(tmp_path, monkeypatch, {"de.smartdragon.zmaj": [ABDRUCK, ABDRUCK.replace("AB", "CD", 1)],
                                          "de.smartdragon.zmaj.test": [ABDRUCK.lower()]})
    assert (ziel / ".nojekyll").read_bytes() == b""
    seite = (ziel / "konto-loeschen.html").read_text(encoding="utf-8")
    mail = seite_bauen.post_adresse()
    assert seite.count('href="mailto:%s"' % mail) >= 8 and "{mail}" not in seite
    links = json.loads((ziel / ".well-known" / "assetlinks.json").read_text(encoding="utf-8"))
    pakete = {e["target"]["package_name"]: e for e in links}
    assert set(pakete) == {"de.smartdragon.zmaj", "de.smartdragon.zmaj.test"}
    for e in links:
        assert e["target"]["namespace"] == "android_app"
        assert "delegate_permission/common.get_login_creds" in e["relation"]
        assert all(a == a.upper() and len(a) == 95 for a in e["target"]["sha256_cert_fingerprints"])
    assert len(pakete["de.smartdragon.zmaj"]["target"]["sha256_cert_fingerprints"]) == 2


def test_ohne_fingerabdruecke_keine_assetlinks(tmp_path, monkeypatch):
    ziel = _bauen(tmp_path, monkeypatch)
    assert (ziel / ".nojekyll").exists()
    assert not os.path.exists(ziel / ".well-known" / "assetlinks.json")


@pytest.mark.parametrize("werte", [
    {},
    {"de.smartdragon.zmaj": []},
    {"de.smartdragon.zmaj": ["AB:CD"]},
    {"kein paket": [ABDRUCK]},
    {"de.smartdragon.zmaj": ABDRUCK},
])
def test_kaputte_fingerabdruecke_brechen_ab(tmp_path, werte):
    import seite_bauen
    datei = tmp_path / "fingerabdruecke.json"
    datei.write_text(json.dumps(werte), encoding="utf-8")
    with pytest.raises(SystemExit):
        seite_bauen.assetlinks(str(datei))
