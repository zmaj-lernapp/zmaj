# -*- coding: utf-8 -*-
"""Der Bild-Drache (seit 15.10.2026): zmaj.json, die Bilder in
web/maskottchen/teile und haut/, und was die App davon erwartet.

Was hier bricht, faellt sonst erst am Handy auf: ein fehlendes Bild laesst
ein Stueck des Drachen leer, eine Bild-Ebene mit falscher "ind" legt den
Rumpf ueber den Kopf, und ein halber Hautsatz zeigt einen Drachen mit Loch."""
import io
import json
import os
import re

import pytest

import haut_einbauen
import inhalt


@pytest.fixture(scope="module")
def maskottchen(wurzel):
    return os.path.join(wurzel, "web", "maskottchen")


@pytest.fixture(scope="module")
def grund(maskottchen):
    with io.open(os.path.join(maskottchen, "zmaj.json"), encoding="utf-8") as f:
        return json.load(f)


def _bild_drache(grund):
    if not any(a.get("p") and not a.get("e") for a in grund.get("assets", [])):
        pytest.skip("zmaj.json ist der Vektor-Drache (zmaj_lottie.py --vektor)")


def test_jedes_bild_liegt_da_und_passt(grund, maskottchen):
    _bild_drache(grund)
    for a in grund["assets"]:
        pfad = os.path.join(maskottchen, a["u"], a["p"])
        assert os.path.isfile(pfad), "fehlt: %s - haut_einbauen.py --teile laufen lassen" % pfad
        assert haut_einbauen.webp_groesse(pfad) == (a["w"], a["h"]), pfad


def test_bild_ebenen_stehen_auf_der_tiefe_ihrer_rig_ebene(grund):
    """Die App sortiert nach "ind". Zwischen einer Bild-Ebene und ihrer
    Rig-Ebene darf nur stehen, was an derselben Rig-Ebene haengt - sonst
    schiebt sich ein Kostuem oder ein anderes Koerperteil dazwischen."""
    _bild_drache(grund)
    nach_ind = {e["ind"]: e for e in grund["layers"]}
    ids = {a["id"] for a in grund["assets"]}
    for e in grund["layers"]:
        if e.get("ty") != 2:
            continue
        assert e["refId"] in ids
        eltern = nach_ind[e["parent"]]
        assert e["ind"] < eltern["ind"], e["nm"]
        for i in range(e["ind"] + 1, eltern["ind"]):
            dazwischen = nach_ind.get(i)
            assert dazwischen is None or (dazwischen.get("ty") == 2 and dazwischen["parent"] == e["parent"]), \
                (e["nm"], dazwischen and dazwischen["nm"])


def test_zierrat_passt_zwischen_die_ebenen(grund, maskottchen):
    """Kein Schnipsel benutzt eine "ind" der Grunddatei, und jede Eltern-
    Ebene, an der er haengt, gibt es (in der Grunddatei oder im Schnipsel)."""
    vergeben = {e["ind"] for e in grund["layers"]}
    for name in sorted(os.listdir(maskottchen)):
        if not name.startswith("zmajz-"):
            continue
        with io.open(os.path.join(maskottchen, name), encoding="utf-8") as f:
            teil = json.load(f)
        eigene = {e["ind"] for e in teil}
        assert not eigene & vergeben, name
        for e in teil:
            assert "parent" not in e or e["parent"] in vergeben | eigene, (name, e["nm"])


def test_kostueme_faerben_nicht_mit(index_html, maskottchen):
    """faerbe() tauscht jede Farbe, die einer aus FARB_QUELLE gleicht. Beim
    Bild-Drachen mit Hautsatz wird gar nicht gefaerbt, ohne Satz aber schon -
    dann duerfen die Kostueme keine Drachenfarbe tragen. Ausnahme ist das
    Skelett: es soll knochenweiss werden (FARBEN.skelett)."""
    quelle = re.search(r"const FARB_QUELLE = \[([^\]]*)\]", index_html).group(1)
    farben = [[int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] for h in re.findall(r"[0-9A-Fa-f]{6}", quelle)]

    def treffer(x):
        if isinstance(x, list):
            return any(treffer(v) for v in x)
        if not isinstance(x, dict):
            return False
        k = x.get("k")
        if x.get("a") == 0 and isinstance(k, list) and len(k) == 4 and all(isinstance(v, (int, float)) for v in k):
            if any(all(abs(k[j] - q[j]) < 0.004 for j in range(3)) for q in farben):
                return True
        return any(treffer(v) for v in x.values())

    for name in sorted(os.listdir(maskottchen)):
        if name.startswith("zmajz-") and name != "zmajz-skelett.json":
            with io.open(os.path.join(maskottchen, name), encoding="utf-8") as f:
                assert not treffer(json.load(f)), name


def test_skelett_ist_nur_knochen(grund, maskottchen):
    """Fest-Entscheidung vom 01.10.2026: das Halloween-Skelett ist nur
    Knochen - kein Fleisch, keine Augen mit Iris. Bis 15.10.2026 ersetzte
    ein Bildsatz haut/skelett/ die Knochen durch einen elfenbeinfarbenen
    Drachen mit blauen Augen. Jetzt nimmt das Stueck alle Bilder heraus und
    bringt das Vektor-Gesicht mit, ohne das Augenweiss mit Iris."""
    _bild_drache(grund)
    with io.open(os.path.join(maskottchen, "zmajz-skelett.json"), encoding="utf-8") as f:
        teil = json.load(f)
    assert not any("zmaj_ohne_haut" in e for e in teil), "das Skelett darf keinem Hautsatz weichen"
    assert not os.path.isdir(os.path.join(maskottchen, "haut", "skelett"))
    leert = set(teil[0]["zmaj_leert"])
    bilder = {e["nm"] for e in grund["layers"] if e.get("ty") == 2}
    assert bilder <= leert, "es blieben Bilder unter den Knochen stehen"
    namen = {e["nm"] for e in teil}
    assert {"skelett_augen", "lids", "mouth_idle"} <= namen
    assert "eyes" not in namen


def test_grunddatei_ohne_vektorgesicht(grund):
    """Das Gesicht steckt im Kopfbild. Bis 15.10.2026 lag die Vektor-Ebene
    "eyes" noch in zmaj.json, offene Augen ueber jedem Kopf: Blinzeln
    unsichtbar, traurige Augen zugedeckt, am abgewandten Kopf vier Augen."""
    _bild_drache(grund)
    gesicht = {"eyes", "lids", "eyes_happy", "eyes_cry", "brows", "mouth_idle", "mouth_open", "mouth_sad",
               "mouth_cry", "tears"}
    assert not gesicht & {e["nm"] for e in grund["layers"]}


def _deckkraft(ebene, bild):
    o = ebene["ks"]["o"]
    if not o.get("a"):
        return o["k"]
    wert = o["k"][0]["s"][0]
    for k in o["k"]:
        if k["t"] <= bild:
            wert = k["s"][0]
    return wert


def test_immer_genau_ein_kopf(grund):
    """In jedem Bild ist genau ein Kopf- und ein Hornbild ganz zu sehen und
    nichts halb. Eine Blende zwischen zwei Koepfen zeigte zwei Gesichter
    uebereinander (Pruefung 15.10.2026); der Kopf wechselt seitdem hart."""
    _bild_drache(grund)
    for vorsilbe in ("bild_kopf_", "bild_hoerner_"):
        ebenen = [e for e in grund["layers"] if e["nm"].startswith(vorsilbe)]
        assert ebenen
        for e in ebenen:
            assert all(k.get("h") == 1 for k in e["ks"]["o"]["k"]), e["nm"]
        for bild in range(grund["op"]):
            werte = [_deckkraft(e, bild) for e in ebenen]
            assert sorted(werte) == [0] * (len(werte) - 1) + [100], (vorsilbe, bild, werte)


def test_hautsaetze_sind_vollstaendig(maskottchen):
    soll = haut_einbauen.grundsatz()
    haut = os.path.join(maskottchen, "haut")
    if not os.path.isdir(haut):
        pytest.skip("keine Hautsaetze")
    for farbe in sorted(os.listdir(haut)):
        ordner = os.path.join(haut, farbe)
        if not os.path.isdir(ordner):
            continue
        assert farbe in haut_einbauen.FARBEN, farbe
        ist = {n[:-5]: haut_einbauen.webp_groesse(os.path.join(ordner, n)) for n in os.listdir(ordner)}
        assert not haut_einbauen.satz_fehler(ist, soll), farbe


def test_hautfarben_gibt_es_in_der_app(index_html):
    """Jede Farbe der App hat entweder einen Platz fuer einen Hautsatz oder
    steht bewusst in OHNE_HAUTSATZ (das Skelett, siehe haut_einbauen.py)."""
    block = re.search(r"const FARBEN = \{([\s\S]*?)\n\};", index_html.replace("\r\n", "\n")).group(1)
    block = re.sub(r"/\*[\s\S]*?\*/", "", block)
    assert not set(haut_einbauen.FARBEN) & set(haut_einbauen.OHNE_HAUTSATZ)
    assert set(re.findall(r"(\w+)\s*:\s*\[", block)) == set(haut_einbauen.FARBEN) | set(haut_einbauen.OHNE_HAUTSATZ)


def test_vektor_drache_nimmt_keinen_hautsatz(index_html):
    """Mit zmaj_lottie.py --vektor hat zmaj.json keine Bilder; ein Hautsatz,
    der noch in haut/ liegt, darf dann faerbe() nicht abschalten."""
    t = index_html.replace("\r\n", "\n")
    rumpf = t[t.index("async function zmajDaten("):t.index("function zmaj(mood")]
    assert re.search(r"const haut = bilder \? hautSatz\(farbe\) : ''", rumpf)
    assert re.search(r"const bilder = \(zmajBasis\.assets \|\| \[\]\)\.some\(", rumpf)


def test_maskottchen_bilder_meldet_nur_ganze_hautsaetze(tmp_path):
    (tmp_path / "zmaj.json").write_text("{}")
    (tmp_path / "zmaj-frei.png").write_bytes(b"")
    for ordner, namen in {"teile": "ab", "haut/gruen": "ab", "haut/rosa": "a", "haut/_neu_rot": "ab"}.items():
        (tmp_path / ordner).mkdir(parents=True)
        for n in namen:
            (tmp_path / ordner / (n + ".webp")).write_bytes(b"")
    assert inhalt.maskottchen_bilder(str(tmp_path)) == ["zmaj-frei.png", "zmaj.json", "haut/gruen/"]


def test_maskottchen_bilder_ohne_teile(tmp_path):
    (tmp_path / "zmaj.json").write_text("{}")
    assert inhalt.maskottchen_bilder(str(tmp_path)) == ["zmaj.json"]


def _riff(art, nutz):
    daten = art + len(nutz).to_bytes(4, "little") + nutz
    return b"RIFF" + (4 + len(daten)).to_bytes(4, "little") + b"WEBP" + daten


def test_webp_groesse_liest_alle_drei_arten(tmp_path):
    vp8x = _riff(b"VP8X", bytes([0x10, 0, 0, 0]) + (327).to_bytes(3, "little") + (574).to_bytes(3, "little"))
    bits = (91 & 0x3FFF) | ((166 & 0x3FFF) << 14)
    vp8l = _riff(b"VP8L", bytes([0x2F]) + bits.to_bytes(4, "little") + bytes(8))
    vp8 = _riff(b"VP8 ", bytes([0, 0, 0, 0x9D, 0x01, 0x2A]) + (245).to_bytes(2, "little") + (307).to_bytes(2, "little"))
    for daten, erwartet in ((vp8x, (328, 575)), (vp8l, (92, 167)), (vp8, (245, 307)), (b"kein bild" * 4, None)):
        p = tmp_path / "x.webp"
        p.write_bytes(daten)
        assert haut_einbauen.webp_groesse(str(p)) == erwartet


def test_satz_fehler():
    soll = {"a": (1, 2), "b": (3, 4)}
    assert haut_einbauen.satz_fehler({"a": (1, 2), "b": (3, 4), "c": (5, 5)}, soll) == []
    assert haut_einbauen.satz_fehler({"a": (1, 2)}, soll) == ["fehlt: b"]
    assert haut_einbauen.satz_fehler({"a": (1, 2), "b": (3, 5)}, soll) == ["b ist (3, 5) statt (3, 4)"]
