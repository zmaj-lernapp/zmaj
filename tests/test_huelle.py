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
    # anmeldung_pruefen: --aab braucht seit v109 cloud_zugang.json, die es
    # hier nicht gibt - eigene Tests in test_cloud.py. 28.10.2026
    for name in ("anmeldung_pruefen", "pruefen", "kopieren", "emir_drueber", "dauer_einsetzen", "cloud_einsetzen",
                 "ton_verkleinern", "capacitor",
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


# Dauer-Vollversion (11.10.2026): Das Wort stand im Klartext im oeffentlichen
# Repository. Jetzt steht in der Quelle nur ein Platzhalter, und app_bauen.py
# setzt den Pruefwert aus der privaten Huelle ein.
def test_dauer_quelle_hat_nur_den_platzhalter(wurzel):
    import app_bauen
    quelle = open(os.path.join(wurzel, "web", "index.html"), encoding="utf-8").read()
    assert quelle.count(app_bauen.DAUER_PLATZHALTER) == 1
    assert "DAUER_WORT" not in quelle


def test_dauer_einsetzen_nur_in_der_kopie(tmp_path):
    import app_bauen
    wert = "ab" * 32
    datei = tmp_path / "dauer_pruefwert.txt"
    datei.write_text(wert + "\n", encoding="utf-8")
    kopie = tmp_path / "index.html"
    kopie.write_text("a\n" + app_bauen.DAUER_PLATZHALTER + "\nb\n", encoding="utf-8")
    app_bauen.dauer_einsetzen(str(kopie), str(datei))
    text = kopie.read_text(encoding="utf-8")
    assert "const DAUER_PRUEFWERT = '%s';" % wert in text
    assert "__DAUER_PRUEFWERT__" not in text


@pytest.mark.parametrize("inhalt", [None, "dragon", "AB" * 32])
def test_dauer_bricht_ohne_gueltigen_wert_ab(tmp_path, inhalt):
    import app_bauen
    datei = tmp_path / "dauer_pruefwert.txt"
    if inhalt is not None:
        datei.write_text(inhalt, encoding="utf-8")
    kopie = tmp_path / "index.html"
    kopie.write_text(app_bauen.DAUER_PLATZHALTER, encoding="utf-8")
    with pytest.raises(SystemExit):
        app_bauen.dauer_einsetzen(str(kopie), str(datei))


def test_dauer_pruefwert_wie_in_der_app(wurzel):
    """dauer_wort_setzen.py und dauerWortStimmt() muessen denselben Wert
    rechnen - sonst sperrt sich Ajdin mit dem richtigen Wort aus."""
    import re
    import shutil
    import subprocess
    import dauer_wort_setzen as d
    quelle = open(os.path.join(wurzel, "web", "index.html"), encoding="utf-8").read()
    assert "const DAUER_SALZ = '%s';" % d.SALZ in quelle
    assert "const DAUER_RUNDEN = %d;" % d.RUNDEN in quelle
    assert re.search(r"const w = wort\.trim\(\)\.toLowerCase\(\);", quelle)
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    js = ("const c = globalThis.crypto.subtle, e = new TextEncoder();"
          "c.importKey('raw', e.encode(process.argv[1]), 'PBKDF2', false, ['deriveBits'])"
          ".then(k => c.deriveBits({name: 'PBKDF2', hash: 'SHA-256', salt: e.encode(process.argv[2]),"
          " iterations: Number(process.argv[3])}, k, 256))"
          ".then(b => console.log(Buffer.from(b).toString('hex')));")
    wort = "  Kahva Na Bascarsiji  "
    aus = subprocess.run(["node", "-e", js, wort.strip().lower(), d.SALZ, str(d.RUNDEN)],
                         capture_output=True, text=True, check=True).stdout.strip()
    assert aus == d.pruefwert(wort)


# Tonspur als Opus im Paket (12.10.2026): nur die Kopie in www/audio, und
# index.json muss danach auf die .ogg zeigen - die App spielt nur, was dort
# steht.
def test_ton_index_umschreiben():
    import app_bauen
    index = {"toene": [{"key": "a", "datei": "w0001.mp3"},
                       {"key": "b", "datei": "g01.MP3"},
                       {"key": "c", "datei": "schon.ogg"}]}
    assert app_bauen.ton_index_umschreiben(index) == 2
    assert [e["datei"] for e in index["toene"]] == ["w0001.ogg", "g01.ogg", "schon.ogg"]


def test_ton_verkleinern_nie_in_web(wurzel):
    import app_bauen
    with pytest.raises(SystemExit):
        app_bauen.ton_verkleinern(os.path.join(wurzel, "web", "audio"), ffmpeg="gibt-es-nicht")


def test_ton_verkleinern_mit_ffmpeg(tmp_path):
    """Echte Umwandlung zweier kurzer Toene, wenn ffmpeg da ist."""
    import json
    import shutil
    import subprocess
    import app_bauen
    ffmpeg = os.environ.get("ZMAJ_FFMPEG") or (
        app_bauen.FFMPEG if os.path.isfile(app_bauen.FFMPEG) else shutil.which("ffmpeg"))
    if not ffmpeg:
        pytest.skip("ffmpeg fehlt")
    audio = tmp_path / "audio"
    audio.mkdir()
    for name, hz in (("w0001.mp3", 440), ("w0002.mp3", 660)):
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
                        "-i", "sine=frequency=%d:duration=1" % hz, "-ar", "24000", "-ac", "1",
                        "-b:a", "48k", str(audio / name)], check=True)
    (audio / "index.json").write_text(json.dumps({"version": 1, "toene": [
        {"key": "eins", "datei": "w0001.mp3"}, {"key": "zwei", "datei": "w0002.mp3"}]}),
        encoding="utf-8")
    vorher, nachher = app_bauen.ton_verkleinern(str(audio), ffmpeg=ffmpeg,
                                                zwischen=str(tmp_path / "zwischen"))
    assert sorted(os.listdir(audio)) == ["index.json", "w0001.ogg", "w0002.ogg"]
    index = json.loads((audio / "index.json").read_text(encoding="utf-8"))
    assert [e["datei"] for e in index["toene"]] == ["w0001.ogg", "w0002.ogg"]
    assert 0 < nachher < vorher
    assert (audio / "w0001.ogg").read_bytes()[:4] == b"OggS"


# Stille am Anfang (22.10.2026, Ajdin: "der sprecher sagt viel zu spaet die
# woerter oder saetze"): ton_verkleinern() kuerzt sie bei Woertern und
# Saetzen auf rund 30 ms, die Geschichten bleiben, wie sie sind.
def test_ton_filter_nur_fuer_woerter():
    import app_bauen
    assert app_bauen.ton_filter("w0001.mp3") == app_bauen.TON_ANFANG
    assert "silenceremove" in app_bauen.TON_ANFANG and "start_periods=1" in app_bauen.TON_ANFANG
    assert "stop_periods" not in app_bauen.TON_ANFANG          # das Ende bleibt dran
    for name in ("g01.mp3", "g12.mp3", "index.json", "w001.mp3"):
        assert app_bauen.ton_filter(name) is None, name


def test_ton_schluessel_kennt_den_filter(monkeypatch):
    """Ohne den Filter im Schluessel kaemen aus .ton_opus die alten,
    ungekuerzten Dateien - und eine Aenderung am Filter wuerde nie wirksam."""
    import app_bauen
    h = "ab" * 32
    wort, geschichte = app_bauen.ton_schluessel(h, "w0001.mp3"), app_bauen.ton_schluessel(h, "g01.mp3")
    assert geschichte == h[:32] + "-24k"
    assert wort.startswith(geschichte + "-a") and wort != geschichte
    monkeypatch.setattr(app_bauen, "TON_ANFANG", app_bauen.TON_ANFANG.replace("0.03", "0.06"))
    assert app_bauen.ton_schluessel(h, "w0001.mp3") != wort


def _pcm(ffmpeg, pfad):
    """Mono, 48 kHz, 16 Bit - so wie die App die Opus-Datei abspielt."""
    import array
    import subprocess
    roh = subprocess.run([ffmpeg, "-v", "error", "-i", str(pfad), "-ac", "1", "-ar", "48000",
                          "-f", "s16le", "-acodec", "pcm_s16le", "-"],
                         capture_output=True, check=True).stdout
    a = array.array("h")
    a.frombytes(roh[:len(roh) // 2 * 2])
    return a


def _einsatz_ms(proben, db=-45):
    """Erster Ausschlag ueber `db` (Spitze), in ms ab Dateianfang."""
    grenze = 32768 * 10 ** (db / 20.0)
    return next((i / 48.0 for i, x in enumerate(proben) if abs(x) > grenze), None)


def test_ton_verkleinern_kuerzt_den_anfang(tmp_path):
    """w0001 und g01 beginnen beide mit 200 ms Stille. Nach dem Umwandeln
    setzt das Wort nach 20-60 ms ein, die Geschichte weiter bei 200 ms (ihre
    Wortzeiten zaehlen ab Dateianfang). Hinten fehlt nichts: der Ton ist
    danach noch volle 1,5 s lang. Im Zwischenspeicher liegen beide unter
    verschiedenen Schluesseln."""
    import json
    import shutil
    import subprocess
    import app_bauen
    ffmpeg = os.environ.get("ZMAJ_FFMPEG") or (
        app_bauen.FFMPEG if os.path.isfile(app_bauen.FFMPEG) else shutil.which("ffmpeg"))
    if not ffmpeg:
        pytest.skip("ffmpeg fehlt")
    audio = tmp_path / "audio"
    audio.mkdir()
    for name in ("w0001.mp3", "g01.mp3"):
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
                        "-i", "sine=frequency=440:duration=1.5", "-af", "adelay=200:all=1",
                        "-ar", "24000", "-ac", "1", "-b:a", "48k", str(audio / name)], check=True)
    (audio / "index.json").write_text(json.dumps({"version": 1, "toene": [
        {"key": "eins", "datei": "w0001.mp3"}, {"key": "g1", "datei": "g01.mp3", "w": [[200, 900]]}]}),
        encoding="utf-8")
    zwischen = tmp_path / "zwischen"
    app_bauen.ton_verkleinern(str(audio), ffmpeg=ffmpeg, zwischen=str(zwischen))
    wort, geschichte = _pcm(ffmpeg, audio / "w0001.ogg"), _pcm(ffmpeg, audio / "g01.ogg")
    assert 20 <= _einsatz_ms(wort) <= 60, _einsatz_ms(wort)
    assert 180 <= _einsatz_ms(geschichte) <= 230, _einsatz_ms(geschichte)
    # Hinten: der Sinus laeuft bis zum Schluss weiter, gekuerzt wurde nur vorn.
    ende = max(i for i, x in enumerate(wort) if abs(x) > 1000) / 48.0
    assert ende - _einsatz_ms(wort) >= 1480, ende
    namen = sorted(os.listdir(zwischen))
    assert len(namen) == 2 and sum(1 for n in namen if "-24k-a" in n) == 1, namen


def test_ton_verkleinern_neue_aufnahme_unter_altem_namen(tmp_path):
    """23.10.2026: audio_emir/w0119.mp3 ("so") wurde neu gesprochen, der Name
    blieb. Der Zwischenspeicher muss das als neue Datei erkennen - hinge sein
    Schluessel am Namen, kaeme aus .ton_opus die alte Opus-Datei ins Paket.
    Er haengt am Inhalt (sha256 der MP3, ton_schluessel())."""
    import hashlib
    import json
    import shutil
    import subprocess
    import app_bauen
    ffmpeg = os.environ.get("ZMAJ_FFMPEG") or (
        app_bauen.FFMPEG if os.path.isfile(app_bauen.FFMPEG) else shutil.which("ffmpeg"))
    if not ffmpeg:
        pytest.skip("ffmpeg fehlt")
    zwischen = tmp_path / "zwischen"
    ergebnis = []
    for lauf, hz in enumerate((440, 880)):
        audio = tmp_path / ("audio%d" % lauf)       # jeder Bau kopiert www/ frisch
        audio.mkdir()
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
                        "-i", "sine=frequency=%d:duration=1" % hz, "-ar", "24000", "-ac", "1",
                        "-b:a", "48k", str(audio / "w0119.mp3")], check=True)
        (audio / "index.json").write_text(json.dumps({"version": 1, "toene": [
            {"key": "so", "datei": "w0119.mp3"}]}), encoding="utf-8")
        s = app_bauen.ton_schluessel(hashlib.sha256((audio / "w0119.mp3").read_bytes()).hexdigest(),
                                     "w0119.mp3")
        app_bauen.ton_verkleinern(str(audio), ffmpeg=ffmpeg, zwischen=str(zwischen))
        ogg = (audio / "w0119.ogg").read_bytes()
        assert ogg == (zwischen / (s + ".ogg")).read_bytes()
        ergebnis.append((s, ogg))
    (s_alt, ogg_alt), (s_neu, ogg_neu) = ergebnis
    assert s_alt != s_neu and ogg_alt != ogg_neu
    assert sorted(os.listdir(zwischen)) == sorted([s_alt + ".ogg", s_neu + ".ogg"])


def test_projekt_zip_ohne_emir_und_pruefwert(tmp_path):
    """Die Projekt-Zip "darf ueberall hin". Emirs Aufnahmen stecken in der
    Huelle an drei Stellen (audio_emir, Opus-Zwischenspeicher, Git-Objekte)
    und duerfen in keiner davon mit; der Dauer-Pruefwert auch nicht.
    Review 12.10.2026."""
    import projekt_sichern as ps
    huelle = tmp_path / "zmaj-android"
    for rel in ("audio_emir/w0001.mp3", ".ton_opus/abc-24k.ogg", ".git/objects/ab/cdef",
                "dauer_pruefwert.txt", "cloud_zugang.json", "android/app/src/main/java/X.java"):
        p = huelle / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
    namen = [n for _, n in ps.sammeln(str(huelle), "zmaj-android",
                                      ps.HUELLE_WEG_ORDNER, ps.HUELLE_WEG_DATEIEN)]
    assert namen == ["zmaj-android/android/app/src/main/java/X.java"]
