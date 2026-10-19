# -*- coding: utf-8 -*-
"""Cloud-Sicherung, vorbereitet und aus (19.10.2026).

Was ohne Browser pruefbar ist: der Schalter steht in der Quelle auf aus,
Projekt und Schluessel stehen nur als Platzhalter da und kommen allein ueber
app_bauen.cloud_einsetzen() in die Kopie der App, die Regeln erlauben nur
das eigene Dokument, und nirgends im Repository steht ein echter Wert.
Das Verhalten in der App pruefen tests_e2e/test_cloud.py.
"""
import io
import json
import os
import re
import subprocess

import pytest

# Wie ein Web-API-Schluessel von Firebase aussieht. Hier nur als Muster -
# ein echter steht nie im Repository.
SCHLUESSEL_FORM = re.compile(r"AIza[0-9A-Za-z_-]{35}")
CLIENT_ID_FORM = re.compile(r"\d{6,}-[0-9a-z]{20,}\.apps\.googleusercontent\.com")


def _lesen(wurzel, name):
    with io.open(os.path.join(wurzel, name), encoding="utf-8") as f:
        return f.read()


def test_schalter_steht_auf_aus(index_html):
    assert index_html.count("const CLOUD_AN = false;") == 1
    assert "CLOUD_AN = true" not in index_html


def test_quelle_hat_nur_platzhalter(index_html):
    import app_bauen
    for platzhalter in app_bauen.CLOUD_PLATZHALTER.values():
        assert index_html.count(platzhalter) == 1, platzhalter
    assert not SCHLUESSEL_FORM.search(index_html)
    assert not CLIENT_ID_FORM.search(index_html)


def test_app_prueft_dieselben_muster_wie_der_bau(index_html):
    """cloudEingerichtet() in der App und cloud_einsetzen() im Bau muessen
    dieselbe Form verlangen - sonst setzt der Bau einen Wert ein, den die
    App verwirft, und die Cloud bleibt still aus."""
    import app_bauen
    zeile = re.search(r"const cloudEingerichtet = \(\) => (.*?);\r?\n", index_html, re.S).group(1)
    for muster in app_bauen.CLOUD_MUSTER.values():
        assert "/^%s$/" % muster in zeile, muster


def test_groessengrenze_wie_in_den_regeln(index_html, wurzel):
    grenze = re.search(r"const CLOUD_GROESSE_MAX = (\d+);", index_html).group(1)
    assert "d.daten.size() <= %s" % grenze in _lesen(wurzel, "firestore.rules")


def test_regeln_nur_das_eigene_dokument(wurzel):
    regeln = _lesen(wurzel, "firestore.rules")
    code = "\n".join(z.split("//")[0] for z in regeln.splitlines())
    assert "rules_version = '2';" in code
    # Genau ein Pfad unterhalb der Datenbank, und das ist users/{uid}.
    assert re.findall(r"match\s+(\S+)\s*\{", code) == ["/databases/{database}/documents", "/users/{uid}"]
    assert "request.auth != null && request.auth.uid == uid" in code
    erlaubt = re.findall(r"allow ([a-z, ]+):\s*if ([^;]+);", code)
    assert {a for a, _ in erlaubt} == {"get", "create, update", "delete"}
    for _, bedingung in erlaubt:
        assert bedingung.strip().startswith("istEigenes()"), bedingung
    assert "if true" not in code and "{document=**}" not in code
    assert "hasOnly(['daten', 'rev'])" in code


def test_anleitung_ohne_echte_werte(wurzel):
    text = _lesen(wurzel, "FIREBASE_EINRICHTEN.md")
    assert not SCHLUESSEL_FORM.search(text)
    assert not CLIENT_ID_FORM.search(text)
    for pflicht in ("europe-west3", "Spark", "Identity Platform", "SHA-1", "cloud_zugang.json",
                    "firestore.rules", "Datenschutz", "Datensicherheit"):
        assert pflicht in text, pflicht


def test_keine_zugangsdatei_eingecheckt(wurzel):
    try:
        aus = subprocess.run(["git", "ls-files"], cwd=wurzel, capture_output=True,
                             text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("kein git")
    namen = {os.path.basename(d) for d in aus.splitlines()}
    assert not namen & {"cloud_zugang.json", "google-services.json"}


# ---- cloud_einsetzen(): nur in die Kopie, nie mit dem Wert in einer Meldung ----

PROJEKT = "zmaj-probe"
SCHLUESSEL = "AIza" + "Probe" * 7          # 39 Zeichen, nur fuer den Test


def _kopie(tmp_path, an=False):
    import app_bauen
    kopie = tmp_path / "index.html"
    kopie.write_text("a\r\nconst CLOUD_AN = %s;\r\n%s\r\n%s\r\nb\r\n"
                     % ("true" if an else "false", *app_bauen.CLOUD_PLATZHALTER.values()),
                     encoding="utf-8", newline="")
    return kopie


def _zugang(tmp_path, **werte):
    datei = tmp_path / "cloud_zugang.json"
    datei.write_text(json.dumps(werte), encoding="utf-8")
    return datei


def test_einsetzen_nur_in_der_kopie(tmp_path):
    import app_bauen
    kopie = _kopie(tmp_path)
    assert app_bauen.cloud_einsetzen(str(kopie), str(_zugang(tmp_path, projekt=PROJEKT, schluessel=SCHLUESSEL)))
    text = kopie.read_text(encoding="utf-8")
    assert "const CLOUD_PROJEKT = '%s';" % PROJEKT in text
    assert "const CLOUD_SCHLUESSEL = '%s';" % SCHLUESSEL in text
    assert "__CLOUD_" not in text
    assert kopie.read_bytes().count(b"\r\n") == 5      # Zeilenenden bleiben


def test_ohne_datei_bleibt_die_cloud_aus(tmp_path):
    import app_bauen
    kopie = _kopie(tmp_path)
    vorher = kopie.read_bytes()
    assert app_bauen.cloud_einsetzen(str(kopie), str(tmp_path / "gibt-es-nicht.json")) is False
    assert kopie.read_bytes() == vorher


def test_eingeschaltet_ohne_datei_bricht_ab(tmp_path):
    import app_bauen
    with pytest.raises(SystemExit):
        app_bauen.cloud_einsetzen(str(_kopie(tmp_path, an=True)), str(tmp_path / "gibt-es-nicht.json"))


@pytest.mark.parametrize("werte", [
    {"projekt": PROJEKT},
    {"projekt": "Zmaj Probe", "schluessel": SCHLUESSEL},
    {"projekt": PROJEKT, "schluessel": "geheim-aber-falsch"},
    {"projekt": PROJEKT, "schluessel": SCHLUESSEL + "x"},
])
def test_falsche_werte_brechen_ab_ohne_sie_zu_zeigen(tmp_path, werte):
    import app_bauen
    kopie = _kopie(tmp_path)
    vorher = kopie.read_bytes()
    with pytest.raises(SystemExit) as fehler:
        app_bauen.cloud_einsetzen(str(kopie), str(_zugang(tmp_path, **werte)))
    for wert in werte.values():
        assert wert not in str(fehler.value)
    assert kopie.read_bytes() == vorher


def test_platzhalter_fehlt_bricht_ab(tmp_path):
    import app_bauen
    kopie = tmp_path / "index.html"
    kopie.write_text("const CLOUD_AN = false;\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        app_bauen.cloud_einsetzen(str(kopie), str(_zugang(tmp_path, projekt=PROJEKT, schluessel=SCHLUESSEL)))
