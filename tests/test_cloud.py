# -*- coding: utf-8 -*-
"""Cloud-Sicherung (19.10.2026), seit v109 Pflicht-Anmeldung (28.10.2026).

Was ohne Browser pruefbar ist: der Schalter steht in der Quelle auf aus,
Projekt, Schluessel und Client-ID stehen nur als Platzhalter da und kommen
allein ueber app_bauen.cloud_einsetzen() in die Kopie der App - die dort
auch erst CLOUD_AN einschaltet -, ein Freigabe-Bau ohne cloud_zugang.json
bricht ab, die Regeln erlauben nur das eigene Dokument, und nirgends im
Repository steht ein echter Wert.
Das Verhalten in der App pruefen tests_e2e/test_cloud.py und
tests_e2e/test_anmeldung.py.
"""
import io
import json
import os
import re
import subprocess

import pytest

# Wie ein Web-API-Schluessel und eine Web-Client-ID von Firebase aussehen.
# Hier nur als Muster - ein echter Wert steht nie im Repository.
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
    assert set(app_bauen.CLOUD_PLATZHALTER) == {"projekt", "schluessel", "client"}
    for platzhalter in app_bauen.CLOUD_PLATZHALTER.values():
        assert index_html.count(platzhalter) == 1, platzhalter
    assert not SCHLUESSEL_FORM.search(index_html)
    assert not CLIENT_ID_FORM.search(index_html)


def test_app_prueft_dieselben_muster_wie_der_bau(index_html):
    """cloudEingerichtet() in der App und cloud_einsetzen() im Bau muessen
    dieselbe Form verlangen - sonst setzt der Bau einen Wert ein, den die
    App verwirft, und die Anmeldung bleibt still aus."""
    import app_bauen
    zeile = re.search(r"const cloudEingerichtet = \(\) => (.*?);\r?\n", index_html, re.S).group(1)
    for muster in app_bauen.CLOUD_MUSTER.values():
        assert "/^%s$/" % muster in zeile, muster


def test_google_knopf_prueft_dasselbe_client_muster(index_html):
    import app_bauen
    zeile = re.search(r"const googleMoeglich = \(\) => (.*?);\r?\n", index_html, re.S).group(1)
    assert "/^%s$/" % app_bauen.CLOUD_MUSTER["client"] in zeile


def test_groessengrenze_wie_in_den_regeln(index_html, wurzel):
    grenze = re.search(r"const CLOUD_GROESSE_MAX = (\d+);", index_html).group(1)
    assert "d.daten.size() <= %s" % grenze in _lesen(wurzel, "firestore.rules")


def test_grenze_900000_in_bytes_unter_einem_mib(index_html):
    """28.10.2026: 900 000 statt 400 000 - Luft fuer die zeitgesteuerte
    Wiederholung ab v110. Die App misst in UTF-8-Bytes (utf8Laenge), damit
    das Dokument mit rev (bis 100 Zeichen) und den Feldnamen sicher unter
    Firestores 1 MiB je Dokument bleibt; die Regel zaehlt Zeichen."""
    grenze = int(re.search(r"const CLOUD_GROESSE_MAX = (\d+);", index_html).group(1))
    assert grenze == 900000 and grenze + 100 + 4096 < 1024 * 1024
    abgleich = re.search(r"async function cloudAbgleich\(.*?\n\}", index_html, re.S).group(0)
    assert "utf8Laenge(text) > CLOUD_GROESSE_MAX" in abgleich
    assert "text.length > CLOUD_GROESSE_MAX" not in abgleich


def test_regeln_nur_das_eigene_dokument(wurzel):
    regeln = _lesen(wurzel, "firestore.rules")
    code = "\n".join(z.split("//")[0] for z in regeln.splitlines())
    assert "rules_version = '2';" in code
    # Zwei Pfade unterhalb der Datenbank: users/{uid} fuer die App und seit
    # dem 28.10.2026 nachrichten/{uid} fuer das Kontaktformular (geprueft in
    # tests/test_kontakt.py). Hier zaehlt nur der Teil fuer users/{uid}.
    assert re.findall(r"match\s+(\S+)\s*\{", code) == ["/databases/{database}/documents", "/users/{uid}",
                                                         "/nachrichten/{uid}"]
    code = code.split("match /nachrichten/{uid}")[0]
    assert "request.auth != null && request.auth.uid == uid" in code
    erlaubt = re.findall(r"allow ([a-z, ]+):\s*if ([^;]+);", code)
    assert {a for a, _ in erlaubt} == {"get", "create, update", "delete"}
    for _, bedingung in erlaubt:
        assert bedingung.strip().startswith("istEigenes()"), bedingung
    assert "if true" not in code and "{document=**}" not in code
    assert "hasOnly(['daten', 'rev'])" in code


def test_schreiben_mit_antwortmaske_nicht_mit_updatemask(index_html):
    """20.11.2026 (Optimierung Punkt 4): Das PATCH fragt mit der
    Antwortmaske mask.fieldPaths=rev nur rev zurueck statt des ganzen
    Dokuments. updateMask hiesse "nur rev schreiben" - daten bliebe alt.
    Das Verhalten pruefen tests_e2e/test_cloud_antwortmaske.py."""
    speichern = re.search(r"async speichern\(m, dok\)\{.*?\n    \},", index_html, re.S).group(0)
    assert "senden(dokument(m.uid) + '?mask.fieldPaths=rev', {method: 'PATCH'," in speichern
    assert "fields: {daten: {stringValue: dok.text}, rev: {stringValue: dok.rev}}" in speichern
    # Nirgends in der App eine Adresse mit updateMask (nur der Kommentar nennt es).
    assert not re.search(r"['\"`][^'\"`\n]*updateMask", index_html)


def test_rev_ohne_geraetekennung(index_html):
    """28.10.2026: In der Cloud liegt keine Geraete-ID - rev ist ein
    Zufallswert je Schreiben (cloudRev)."""
    abgleich = re.search(r"async function cloudAbgleich\(.*?\n\}", index_html, re.S).group(0)
    assert "geraetId" not in abgleich and "cloudRev()" in abgleich


def _funktion(index_html, name):
    return re.search(r"\nfunction %s\(.*?\r?\n\}" % name, index_html, re.S).group(0)


def test_nachsehen_bei_jedem_oeffnen_und_nach_dem_lernen(index_html):
    """17.11.2026: Nachgesehen wird beim Start und bei jeder Rueckkehr in
    den Vordergrund, hoechstens alle zwei Minuten, und geschrieben auch
    gleich nach jedem Ergebnisschirm, auf dem ein Lerntag entstehen kann
    (dazu der Sprung-Test). Das Verhalten pruefen
    tests_e2e/test_cloud_nachsehen.py."""
    assert index_html.count("let CLOUD_NACHSEHEN_MS = 2 * 60 * 1000;") == 1
    horcher = re.search(r"if\(CLOUD_AN\)\{\r?\n  document\.addEventListener\('visibilitychange', \(\)=>\{(.*?)\}\);",
                        index_html, re.S).group(1)
    assert "cloudAbgleich('pause')" in horcher and horcher.index("return;") < horcher.index("cloudAbgleich('vorn')")
    assert index_html.count("if(CLOUD_AN) cloudAbgleich('start');") == 1
    for name in ("lessonEnd", "topfEnde", "showTestResult", "sprungEnde"):
        assert _funktion(index_html, name).count("cloudNachLernen();") == 1, name
    story = _funktion(index_html, "showStoryQ")
    assert story.count("cloudNachLernen();") == 1 and story.index("saveProgress()") < story.index("cloudNachLernen()")
    # Ohne CLOUD_AN tut es nichts, und es wartet nicht.
    nach = _funktion(index_html, "cloudNachLernen")
    assert "if(CLOUD_AN) setTimeout(() => cloudAbgleich('ende'), 0);" in nach
    # Zwei Schreibvorgaenge am Tag hoechstens: m.tag (Verlassen oder
    # Nachholen) und m.ende (nach dem Lernen), nie beide zugleich.
    abgleich = re.search(r"async function cloudAbgleich\(.*?\n\}", index_html, re.S).group(0)
    assert "if(nachLernen) m.ende = heute;" in abgleich
    assert "else if(!erstes && !zuletzt) m.tag = heute;" in abgleich


def test_nachbesserung_nach_dem_pruefbefund(index_html):
    """Pruefbefund 17.11.2026 zum Nachsehen bei jedem Oeffnen, das Verhalten
    pruefen tests_e2e/test_cloud_nachsehen.py und test_cloud_packen.py:
      - hoechstens vier Schreibversuche am Tag, gezaehlt VOR dem Schreiben,
        Anmelden und Abmelden ausgenommen;
      - reines Einarbeiten gilt als hochgeladen (m.fp), nur wenn die Cloud
        schon alles hatte, was das Geraet hat (cloudHatAlles);
      - nur eine Ablehnung der Feldmaske (400) schaltet das Nachsehen sofort
        ab, und dann nur fuer diesen Tag; Fehler des Ausweises nie."""
    assert index_html.count("const CLOUD_SCHREIBVERSUCHE = 4;") == 1
    assert index_html.count("const CLOUD_MASKE_FEHLER = 2;") == 1
    assert "cloudMaskeKaputt" not in index_html
    abgleich = re.search(r"async function cloudAbgleich\(.*?\n\}", index_html, re.S).group(0)
    merken = "if(!erstes && !zuletzt){ m.versuche = {tag: heute, n: versucht() + 1}; cloudMerkerSetzen(m, true); }"
    assert abgleich.count(merken) == 1
    assert abgleich.index(merken) < abgleich.index("await adapter.speichern(m, {text, rev});")
    assert "schreiben = frei && m.tag !== heute && geaendert();" in abgleich
    assert "if(!frei || m.ende === heute || !geaendert()) return 'nichts';" in abgleich
    assert "(anlass === 'pause' && m.tag !== heute && frei)" in abgleich
    # Geprueft vor dem Einarbeiten, m.fp nur ohne Schreiben danach
    pruefen = "if(s && !schreiben && m.rev) schonOben = cloudHatAlles(s, m.fremd);"
    assert abgleich.count(pruefen) == 1
    assert abgleich.index(pruefen) < abgleich.index("cloudUebernehmen(s, m.fremd, !m.rev)")
    assert "if(schonOben) m.fp = cloudFingerabdruck(standAlsObjekt());" in abgleich
    hat = _funktion(index_html, "cloudHatAlles")
    assert "sicherungPlausibel(s)" in hat and "mit.getragen = nur.getragen;" in hat
    maske = _funktion(index_html, "cloudMaskeAus")
    assert "x.tag === today()" in maske
    assert "if(e && typeof e === 'object' && e.status === 400) e.maske = true;" in index_html
    assert "if(e && typeof e === 'object') e.ausweis = true;" in index_html
    assert "f.status = r.status;" in index_html


def test_anleitung_ohne_echte_werte(wurzel):
    text = _lesen(wurzel, "FIREBASE_EINRICHTEN.md")
    assert not SCHLUESSEL_FORM.search(text)
    assert not CLIENT_ID_FORM.search(text)
    for pflicht in ("europe-west3", "Spark", "Identity Platform", "SHA-1", "SHA-256", "cloud_zugang.json",
                    "firestore.rules", "Datenschutz", "Datensicherheit", "client", "E-Mail/Passwort",
                    "fingerabdruecke.json", "--ohne-anmeldung", "App-Zugriff"):
        assert pflicht in text, pflicht


def _git_dateien(wurzel):
    try:
        return subprocess.run(["git", "ls-files"], cwd=wurzel, capture_output=True,
                              text=True, check=True).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("kein git")


def test_keine_zugangsdatei_eingecheckt(wurzel):
    namen = {os.path.basename(d) for d in _git_dateien(wurzel)}
    assert not namen & {"cloud_zugang.json", "google-services.json", "fingerabdruecke.json"}


def test_kein_echter_wert_im_repository(wurzel):
    """Kein Web-API-Schluessel und keine Client-ID in irgendeiner Datei -
    die Tests bauen ihre erfundenen Werte aus Stuecken zusammen."""
    funde = []
    for name in _git_dateien(wurzel):
        if not name.endswith((".py", ".html", ".md", ".js", ".json", ".txt", ".toml", ".rules", ".yml", ".cff")):
            continue
        pfad = os.path.join(wurzel, name)
        if not os.path.isfile(pfad) or os.path.getsize(pfad) > 5_000_000:
            continue
        with io.open(pfad, encoding="utf-8", errors="replace") as f:
            text = f.read()
        if SCHLUESSEL_FORM.search(text) or CLIENT_ID_FORM.search(text):
            funde.append(name)
    assert funde == []


# ---- cloud_einsetzen(): nur in die Kopie, nie mit dem Wert in einer Meldung ----

PROJEKT = "zmaj-probe"
SCHLUESSEL = "AIza" + "Probe" * 7          # 39 Zeichen, nur fuer den Test
CLIENT = "1234567" + "89012-" + "probe" * 6 + ".apps." + "googleusercontent.com"


def _kopie(tmp_path, an=False):
    import app_bauen
    kopie = tmp_path / "index.html"
    kopie.write_text("a\r\nconst CLOUD_AN = %s;\r\n%s\r\n%s\r\n%s\r\nb\r\n"
                     % ("true" if an else "false", *app_bauen.CLOUD_PLATZHALTER.values()),
                     encoding="utf-8", newline="")
    return kopie


def _zugang(tmp_path, **werte):
    datei = tmp_path / "cloud_zugang.json"
    datei.write_text(json.dumps(werte), encoding="utf-8")
    return datei


def _alle(tmp_path):
    return _zugang(tmp_path, projekt=PROJEKT, schluessel=SCHLUESSEL, client=CLIENT)


def test_einsetzen_nur_in_der_kopie_und_schaltet_ein(tmp_path):
    import app_bauen
    kopie = _kopie(tmp_path)
    assert app_bauen.cloud_einsetzen(str(kopie), str(_alle(tmp_path)))
    text = kopie.read_text(encoding="utf-8")
    assert "const CLOUD_PROJEKT = '%s';" % PROJEKT in text
    assert "const CLOUD_SCHLUESSEL = '%s';" % SCHLUESSEL in text
    assert "const CLOUD_CLIENT = '%s';" % CLIENT in text
    assert "const CLOUD_AN = true;" in text and "CLOUD_AN = false" not in text
    assert "__CLOUD_" not in text
    assert kopie.read_bytes().count(b"\r\n") == 6      # Zeilenenden bleiben


def test_einsetzen_in_einer_schon_eingeschalteten_kopie(tmp_path):
    """Die Browsertests schalten ihre Kopie mitunter selbst ein."""
    import app_bauen
    kopie = _kopie(tmp_path, an=True)
    assert app_bauen.cloud_einsetzen(str(kopie), str(_alle(tmp_path)))
    assert kopie.read_text(encoding="utf-8").count("const CLOUD_AN = true;") == 1


def test_ohne_datei_bleibt_alles_wie_vorher(tmp_path):
    import app_bauen
    kopie = _kopie(tmp_path)
    vorher = kopie.read_bytes()
    assert app_bauen.cloud_einsetzen(str(kopie), str(tmp_path / "gibt-es-nicht.json")) is False
    assert kopie.read_bytes() == vorher


def test_eingeschaltet_ohne_datei_bricht_ab(tmp_path):
    import app_bauen
    with pytest.raises(SystemExit):
        app_bauen.cloud_einsetzen(str(_kopie(tmp_path, an=True)), str(tmp_path / "gibt-es-nicht.json"))


def test_pflicht_ohne_datei_bricht_ab_und_nennt_den_ausweg(tmp_path):
    import app_bauen
    kopie = _kopie(tmp_path)
    vorher = kopie.read_bytes()
    with pytest.raises(SystemExit) as fehler:
        app_bauen.cloud_einsetzen(str(kopie), str(tmp_path / "gibt-es-nicht.json"), pflicht=True)
    assert "--ohne-anmeldung" in str(fehler.value)
    assert kopie.read_bytes() == vorher


@pytest.mark.parametrize("werte", [
    {"projekt": PROJEKT, "schluessel": SCHLUESSEL},
    {"projekt": "Zmaj Probe", "schluessel": SCHLUESSEL, "client": CLIENT},
    {"projekt": PROJEKT, "schluessel": "geheim-aber-falsch", "client": CLIENT},
    {"projekt": PROJEKT, "schluessel": SCHLUESSEL + "x", "client": CLIENT},
    {"projekt": PROJEKT, "schluessel": SCHLUESSEL, "client": "probe.apps.googleusercontent.com"},
    {"projekt": PROJEKT, "schluessel": SCHLUESSEL, "client": CLIENT + ".boese.example"},
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
        app_bauen.cloud_einsetzen(str(kopie), str(_alle(tmp_path)))


def test_schalter_fehlt_oder_doppelt_bricht_ab(tmp_path):
    import app_bauen
    for schalter in ("", "const CLOUD_AN = false;\r\nconst CLOUD_AN = false;\r\n"):
        kopie = tmp_path / "index.html"
        kopie.write_text("a\r\n%s%s\r\n" % (schalter, "\r\n".join(app_bauen.CLOUD_PLATZHALTER.values())),
                         encoding="utf-8", newline="")
        vorher = kopie.read_bytes()
        with pytest.raises(SystemExit):
            app_bauen.cloud_einsetzen(str(kopie), str(_alle(tmp_path)))
        assert kopie.read_bytes() == vorher


# ---- Freigabe-Bau nur mit Anmeldung (anmeldung_pruefen) ----

def test_freigabe_ohne_zugang_bricht_ab(tmp_path):
    import app_bauen
    fehlt = str(tmp_path / "gibt-es-nicht.json")
    with pytest.raises(SystemExit) as fehler:
        app_bauen.anmeldung_pruefen({"--aab"}, fehlt)
    assert "--ohne-anmeldung" in str(fehler.value)
    with pytest.raises(SystemExit):
        app_bauen.anmeldung_pruefen({"--aab", "--testwerbung", "--pflicht"}, fehlt)


def test_freigabe_mit_zugang_oder_absichtlich_ohne(tmp_path):
    import app_bauen
    fehlt = str(tmp_path / "gibt-es-nicht.json")
    assert app_bauen.anmeldung_pruefen({"--aab"}, str(_alle(tmp_path))) is None
    assert app_bauen.anmeldung_pruefen({"--aab", "--ohne-anmeldung"}, fehlt) is None
    # Debug-Bau und Abgleich fuer die Test-App gehen immer.
    assert app_bauen.anmeldung_pruefen(set(), fehlt) is None
    assert app_bauen.anmeldung_pruefen({"--nur-abgleich", "--testwerbung"}, fehlt) is None
    assert app_bauen.schalter_lesen(["--aab", "--ohne-anmeldung"]) == {"--aab", "--ohne-anmeldung"}


def test_main_ohne_zugang_bricht_vor_dem_bau_ab(monkeypatch, tmp_path):
    """--aab ohne cloud_zugang.json: nichts wird geprueft, kopiert oder
    hochgezaehlt."""
    import app_bauen

    def verboten(*args, **kwargs):
        raise AssertionError("darf vor dem Abbruch nicht laufen")

    for name in ("pruefen", "kopieren", "versionsnummer_hochzaehlen"):
        monkeypatch.setattr(app_bauen, name, verboten)
    monkeypatch.setattr(app_bauen, "CLOUD_DATEI", str(tmp_path / "gibt-es-nicht.json"))
    with pytest.raises(SystemExit):
        app_bauen.main(["--aab"])


# ---- Gepackt sichern, Weg A (Ajdin am 13.11.2026) ----
# Schritt 1 (1.4): packen nur, wenn die alte Form nicht mehr passt. Schritt 2
# ("immer packen", ein bis zwei Monate spaeter) kommt ueber die Quelle. Fuer
# den Handytest mit einem Geraet mit 1.3 gibt es die Test-App mit
# --immer-packen. Das Verhalten pruefen tests_e2e/test_cloud_packen.py.

def test_packen_in_der_quelle_noch_schritt_1(index_html):
    import app_bauen
    assert index_html.count(app_bauen.PACKEN_AUS) == 1
    assert app_bauen.PACKEN_AN not in index_html
    assert index_html.count("const CLOUD_PACK_FELD = 'gepackt1';") == 1


def test_immer_packen_nur_in_der_kopie(tmp_path):
    import app_bauen
    kopie = tmp_path / "index.html"
    kopie.write_bytes(("a\r\n" + app_bauen.PACKEN_AUS + "\r\nb\n").encode("utf-8"))
    app_bauen.immer_packen_einschalten(str(kopie))
    assert kopie.read_bytes() == ("a\r\n" + app_bauen.PACKEN_AN + "\r\nb\n").encode("utf-8")
    # Steht der Anker nicht genau einmal da, bricht der Bau ab, und die
    # Datei bleibt, wie sie war.
    for roh in (b"a\n", (app_bauen.PACKEN_AUS * 2).encode("utf-8")):
        kopie.write_bytes(roh)
        with pytest.raises(SystemExit):
            app_bauen.immer_packen_einschalten(str(kopie))
        assert kopie.read_bytes() == roh


def test_immer_packen_nie_fuer_den_store():
    import app_bauen
    assert app_bauen.schalter_lesen(["--immer-packen"]) == {"--immer-packen"}
    assert app_bauen.schalter_lesen(["--nur-abgleich", "--immer-packen"]) == {"--nur-abgleich", "--immer-packen"}
    with pytest.raises(SystemExit) as fehler:
        app_bauen.schalter_lesen(["--aab", "--immer-packen"])
    assert "CLOUD_IMMER_PACKEN" in str(fehler.value)


def test_immer_packen_im_bau_nach_dem_kopieren(monkeypatch):
    """In die Kopie www/index.html, also nach kopieren() und vor capacitor() -
    nur, was dann in www/ liegt, kommt ins Paket. Ohne den Schalter nie."""
    import app_bauen
    aufrufe = []
    for name in ("anmeldung_pruefen", "versionsname_lesen", "pruefen", "kopieren", "emir_drueber",
                 "dauer_einsetzen", "cloud_einsetzen", "version_einsetzen", "ton_verkleinern",
                 "testwerbung_einschalten", "immer_packen_einschalten", "versionsnummer_hochzaehlen",
                 "capacitor", "plugins_flicken", "debug_apk", "freigabe_aab", "versionsname_anheben"):
        monkeypatch.setattr(app_bauen, name, lambda *a, n=name, **k: aufrufe.append(n))
    app_bauen.main(["--immer-packen"])
    assert aufrufe.index("kopieren") < aufrufe.index("immer_packen_einschalten") < aufrufe.index("capacitor")
    assert "debug_apk" in aufrufe and "freigabe_aab" not in aufrufe
    aufrufe.clear()
    app_bauen.main([])
    assert "immer_packen_einschalten" not in aufrufe and "debug_apk" in aufrufe
