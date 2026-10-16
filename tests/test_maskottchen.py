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


def _schnipsel(maskottchen):
    """{id: (Ebenen, Assets)} aller zmajz-<id>.json. Ein Schnipsel ist eine
    Liste von Ebenen oder - seit 16.10.2026, bei den gemalten Stuecken -
    ein Objekt {layers, assets} (zmajDaten() in web/index.html)."""
    alle = {}
    for name in sorted(os.listdir(maskottchen)):
        if name.startswith("zmajz-") and name.endswith(".json"):
            with io.open(os.path.join(maskottchen, name), encoding="utf-8") as f:
                teil = json.load(f)
            if isinstance(teil, dict):
                alle[name[6:-5]] = (teil["layers"], teil.get("assets", []))
            else:
                alle[name[6:-5]] = (teil, [])
    return alle


def test_zierrat_passt_zwischen_die_ebenen(grund, maskottchen):
    """Kein Schnipsel benutzt eine "ind" der Grunddatei, und jede Eltern-
    Ebene, an der er haengt, gibt es (in der Grunddatei oder im Schnipsel)."""
    vergeben = {e["ind"] for e in grund["layers"]}
    for name, (teil, _assets) in _schnipsel(maskottchen).items():
        eigene = {e["ind"] for e in teil}
        assert not eigene & vergeben, name
        for e in teil:
            assert "parent" not in e or e["parent"] in vergeben | eigene, (name, e["nm"])


def test_gemalte_kostueme_bringen_ihre_bilder_mit(grund, maskottchen):
    """Die gemalten Stuecke (16.10.2026): jede Bild-Ebene zeigt ein Asset
    ihres eigenen Schnipsels, das Bild liegt unter zierrat/<id>/ und hat die
    Groesse, die das Asset nennt - sonst bliebe das Stueck in der App leer
    oder verzerrt. Kein Asset-Name kommt zweimal vor (auch nicht in
    zmaj.json): Lottie findet die Bilder ueber den Namen."""
    _bild_drache(grund)
    gemalt = {n: v for n, v in _schnipsel(maskottchen).items() if v[1]}
    assert {"kappe", "fes", "hut", "doktorhut", "krone", "krone_gross", "nikolausmuetze", "bajramfes",
            "trikot", "weste_strick", "weste_leder", "umhang", "jelek", "schal_winter", "schal_bih",
            # seit 16.10.2026 auch die restlichen ("mal auch die restlichen")
            "brille", "sonnenbrille", "lesebrille", "monokel", "ohrenschuetzer", "kopfhoerer",
            "hexenhut", "hasenohren", "funkeln"} <= set(gemalt)
    namen = [a["id"] for a in grund["assets"]]
    for name, (ebenen, assets) in gemalt.items():
        ids = {a["id"]: a for a in assets}
        namen += list(ids)
        for e in ebenen:
            assert e["ty"] == 2 and e["refId"] in ids, (name, e["nm"])
        for a in assets:
            assert a["u"] == "zierrat/%s/" % name, a
            pfad = os.path.join(maskottchen, a["u"], a["p"])
            assert os.path.isfile(pfad), "fehlt: %s - haut_einbauen.py --zierrat laufen lassen" % pfad
            assert haut_einbauen.webp_groesse(pfad) == (a["w"], a["h"]), pfad
    assert len(namen) == len(set(namen))


def _ebenen_nach_name(grund, maskottchen):
    alle = {e["nm"]: e for e in grund["layers"]}
    for ebenen, _a in _schnipsel(maskottchen).values():
        alle.update({e["nm"]: e for e in ebenen})
    return alle


def test_gemalte_huete_folgen_dem_kopfplan(grund, maskottchen):
    """Je Hut drei Bilder: vorne auf allen Frontkoepfen, links/rechts genau
    dann, wenn der abgewandte Kopf kopf_links/kopf_rechts zu sehen ist -
    beim Kopfschuetteln springt der Hut im selben Bild wie der Kopf. Und er
    nimmt die Hornspitzen heraus (zmaj_leert): wo Gemini ein Horn vor den
    Hut gemalt hat, hat das Bild ein Loch, und die Spitzen darueber legten
    am abgewandten Kopf das ferne Horn vor den Hut (16.10.2026).
    Seit 16.10.2026 sind auch Brillen, Ohrensachen, Hexenhut und Hasenohren
    gemalt - 16 Kopfstuecke. Die Brillen beruehren die Hoerner nicht und
    lassen die Hornspitzen stehen."""
    _bild_drache(grund)
    alle = _ebenen_nach_name(grund, maskottchen)
    hornspitzen = {n for n in alle if n.startswith("bild_hoerner_")}
    huete = [n[:-len("_vorne")] for n in alle if n.endswith("_vorne") and n.startswith("bild_")]
    assert len(huete) == 16, huete
    brillen = {"bild_brille", "bild_sonnenbrille", "bild_lesebrille", "bild_monokel"}
    for hut in huete:
        if hut in brillen:
            assert "zmaj_leert" not in alle[hut + "_vorne"], hut
        else:
            assert set(alle[hut + "_vorne"]["zmaj_leert"]) == hornspitzen, hut
        for bild in range(grund["op"]):
            seite = {s: _deckkraft(alle[hut + "_" + s], bild) for s in ("vorne", "links", "rechts")}
            kopf = {s: _deckkraft(alle["bild_kopf_" + s], bild) for s in ("links", "rechts")}
            erwartet = "links" if kopf["links"] == 100 else "rechts" if kopf["rechts"] == 100 else "vorne"
            assert seite == {s: (100 if s == erwartet else 0) for s in seite}, (hut, bild, seite)


def test_gemalte_funken_blitzen(grund, maskottchen):
    """Funkeln (gemalt seit 16.10.2026): sieben Sterne, jeder eine eigene
    Bild-Ebene am Rumpf, vor allem anderen. Jeder blitzt auf (Deckkraft und
    Groesse animiert, am Anfang unsichtbar) und steht auf seinem eigenen
    Platz - die Ajdin-Regel vom 29.09.2026: funkeln, nicht kreisen."""
    _bild_drache(grund)
    ebenen, assets = _schnipsel(maskottchen)["funkeln"]
    rumpf = next(e["ind"] for e in grund["layers"] if e["nm"] == "body")
    assert len(ebenen) == 7 and len(assets) == 7
    plaetze = set()
    for e in ebenen:
        assert e["ty"] == 2 and e["parent"] == rumpf, e["nm"]
        assert e["ind"] < min(g["ind"] for g in grund["layers"]), e["nm"]
        ks = e["ks"]
        assert ks["o"]["a"] == 1 and ks["s"]["a"] == 1 and ks["p"]["a"] == 0, e["nm"]
        assert _deckkraft(e, 0) == 0 and max(k["s"][0] for k in ks["o"]["k"]) == 100, e["nm"]
        plaetze.add(tuple(ks["p"]["k"][:2]))
    assert len(plaetze) == 7


def test_aermel_folgen_ihrem_arm(grund, maskottchen):
    """Ein gemalter Aermel haengt an derselben Rig-Ebene wie sein Armteil
    und ist in genau denselben Bildern zu sehen - erhoben, als Faust, an
    der Wange. Er liegt vor dem Arm (kleinere "ind").
    Seit 16.10.2026 haben die drei Oberteile fuer die Bilder, in denen die
    Arme im Jubel oben stehen, eigene Aermel (oberarm*_jubel) und ein eigenes
    Rumpfbild (rumpf_jubel) - vorher sassen die Aermel dort wie Roehren auf
    der Brust. Jubel-Aermel und alter erhobener Aermel teilen sich die Bilder
    des erhobenen Oberarms, nie beide zugleich. Das Jubel-Rumpfbild gilt nur,
    wenn auch der Jubel-Aermel zu sehen ist; seit der Nachpruefung vom
    16.10.2026 tragen die Uebergangsbilder mit waagerechten Armen schon die
    Jubel-Aermel, aber noch das alte Rumpfbild - genau ein Rumpfbild ist
    immer zu sehen."""
    _bild_drache(grund)
    alle = _ebenen_nach_name(grund, maskottchen)
    geprueft = 0
    for stueck in ("trikot", "weste_strick", "weste_leder"):
        rumpf, rumpf_jubel = alle["bild_%s_rumpf" % stueck], alle["bild_%s_rumpf_jubel" % stueck]
        for nm in [n for n in alle if n.startswith("bild_%s_" % stueck) and "arm" in n]:
            teil = nm[len("bild_%s_" % stueck):]
            arm = alle["bild_" + teil.replace("_jubel", "_hoch")]
            assert alle[nm]["parent"] == arm["parent"] and alle[nm]["ind"] < arm["ind"], nm
            if teil.endswith(("_hoch", "_jubel")):
                hoch, jubel = alle[nm.replace("_jubel", "_hoch")], alle[nm.replace("_hoch", "_jubel")]
                nur_aermel = 0
                for bild in range(grund["op"]):
                    h, j = _deckkraft(hoch, bild), _deckkraft(jubel, bild)
                    rj, r = _deckkraft(rumpf_jubel, bild), _deckkraft(rumpf, bild)
                    assert h + j == _deckkraft(arm, bild) and h * j == 0, (nm, bild)
                    assert rj in (0, j) and r == 100 - rj, (nm, bild)
                    nur_aermel += j == 100 and rj == 0
                assert nur_aermel == 6, nm      # je drei Bilder hoch und runter
            else:
                for bild in range(grund["op"]):
                    assert _deckkraft(alle[nm], bild) == _deckkraft(arm, bild), (nm, bild)
            geprueft += 1
    assert geprueft == 6 + 12 + 12


def test_mantel_haengt_hinter_dem_koerper(grund, maskottchen):
    """Der gemalte Koenigsmantel haengt hinter Koerper und Schwanz, aber vor
    den Fluegeln. Die Hermelinbaender auf der Brust liegen hinter den Armen
    und vor dem Koerper - vor den Armen deckten sie beim Weinen die Unterarme
    zu. Seit 16.10.2026 mittags (Ajdin: "die Schultern gucken raus, die
    muessen im Gewand sein") liegt der Kragen mit dem Schulterumhang VOR den
    Oberarmen, aber hinter Kopf und Unterarmen: er deckt die Schultern, die
    Arme kommen unter ihm hervor.
    Seit 16.10.2026 nachmittags (Ajdin: "die Arme sind beim Mantel komisch
    abgeschnitten, und beim Jubel geht er durch den Mantel"): der Saum des
    Umhangs liegt VOR den Unterarmen, solange sie haengen - die Hand kommt
    unter der Borte hervor, statt mit geradem Ende auf ihr zu liegen. Im
    Jubel liegt der Umhang HINTER den erhobenen Armen und nur die Stola
    davor, also stossen die Arme nirgends durch den Samt."""
    _bild_drache(grund)
    alle = _ebenen_nach_name(grund, maskottchen)
    ind = {n: alle[n]["ind"] for n in ("bild_umhang_mantel", "bild_umhang_kragen", "bild_umhang_kragen_jubel",
                                       "bild_umhang_baender", "bild_umhang_baender_jubel", "bild_umhang_saum",
                                       "bild_umhang_stola_jubel", "bild_body", "bild_tail",
                                       "bild_wingL", "bild_wingR", "bild_oberarmL", "bild_oberarmR",
                                       "bild_oberarmL_hoch", "bild_oberarmR_hoch", "bild_unterarmL_offen",
                                       "bild_unterarmR_offen", "bild_unterarmL_faust", "bild_unterarmR_faust",
                                       "bild_kopf_neutral", "bild_kopf_jubel")}
    arme = [ind[n] for n in ("bild_oberarmL", "bild_oberarmR", "bild_oberarmL_hoch", "bild_oberarmR_hoch")]
    assert ind["bild_body"] < ind["bild_tail"] < ind["bild_umhang_mantel"] < min(ind["bild_wingL"], ind["bild_wingR"])
    for b in ("bild_umhang_baender", "bild_umhang_baender_jubel", "bild_umhang_kragen_jubel"):
        assert max(arme) < ind[b] < ind["bild_body"], b
    assert ind["bild_umhang_baender_jubel"] < ind["bild_umhang_kragen_jubel"]
    assert max(ind["bild_kopf_neutral"], ind["bild_unterarmL_offen"], ind["bild_unterarmR_offen"]) \
        < ind["bild_umhang_kragen"] < min(arme)
    assert max(ind["bild_kopf_jubel"], ind["bild_unterarmL_faust"], ind["bild_unterarmR_faust"]) \
        < ind["bild_umhang_stola_jubel"] < min(arme)
    assert ind["bild_umhang_saum"] < min(ind["bild_unterarmL_offen"], ind["bild_unterarmR_offen"])
    # Der Saum nur mit haengenden Armen und nur zusammen mit dem Kragen
    for b in range(grund["op"]):
        if _deckkraft(alle["bild_umhang_saum"], b):
            assert _deckkraft(alle["bild_unterarmL_offen"], b) == _deckkraft(alle["bild_unterarmR_offen"], b) == 100, b
            assert _deckkraft(alle["bild_umhang_kragen"], b) == 100, b


def test_jubelbilder_am_rumpf_wechseln_mit_den_armen(grund, maskottchen):
    """Jelek und Koenigsmantel haben seit 16.10.2026 mittags eigene Bilder
    fuer den Jubel mit erhobenen Armen (das Jelek blieb sonst "zu niedrig",
    der Mantel liess die Schultern frei). Je Paar ist in jedem Bild genau
    eines zu sehen, und das Jubelbild genau dann, wenn auch das Trikot sein
    Jubelbild zeigt (die Arme stehen oben). Das Jubel-Jelek liegt vor den
    Oberarmen (der Rand des Armlochs deckt den Armansatz), aber hinter Kopf
    und Unterarmen.
    Seit 16.10.2026 abends gilt der Jubel-Umhang schon in den
    Uebergangsbildern (cheer_quer), solange auch der Jubel-Aermel des
    Trikots gilt: unter dem Ruhekragen kamen die waagerechten Arme dort
    seitlich aus dem Umhang wie aus einem Schlitz."""
    _bild_drache(grund)
    alle = _ebenen_nach_name(grund, maskottchen)
    oben = [_deckkraft(alle["bild_trikot_rumpf_jubel"], b) for b in range(grund["op"])]
    hoch = [_deckkraft(alle["bild_trikot_oberarmL_jubel"], b) for b in range(grund["op"])]
    assert 0 < oben.count(100) < hoch.count(100) < len(oben)
    for alt, jubel, wann in (("bild_jelek_rumpf", "bild_jelek_rumpf_jubel", oben),
                             ("bild_umhang_kragen", "bild_umhang_kragen_jubel", hoch),
                             ("bild_umhang_kragen", "bild_umhang_stola_jubel", hoch),
                             ("bild_umhang_baender", "bild_umhang_baender_jubel", hoch)):
        for b in range(grund["op"]):
            a, j = _deckkraft(alle[alt], b), _deckkraft(alle[jubel], b)
            assert a + j == 100 and a * j == 0, (alt, b)
            assert j == wann[b], (jubel, b)
    ind = {n: alle[n]["ind"] for n in ("bild_jelek_rumpf_jubel", "bild_oberarmL_hoch", "bild_oberarmR_hoch",
                                       "bild_unterarmL_faust", "bild_kopf_jubel")}
    assert max(ind["bild_kopf_jubel"], ind["bild_unterarmL_faust"]) < ind["bild_jelek_rumpf_jubel"] \
        < min(ind["bild_oberarmL_hoch"], ind["bild_oberarmR_hoch"])


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
    Knochen - kein Fleisch, keine Augen mit Iris. Seit 16.10.2026 ist es
    das von Gemini gemalte Skelett, der Hautsatz haut/skelett/ (am selben
    Rig, also dieselbe Bewegung wie der Drache). Das Vektor-Skelett weicht
    ihm ganz (zmaj_ohne_haut auf jeder seiner Ebenen) und bleibt der
    Rueckfall, wenn der Satz fehlt: dann nimmt es alle Bilder heraus und
    bringt das Vektor-Gesicht mit, ohne das Augenweiss mit Iris."""
    _bild_drache(grund)
    teil, _assets = _schnipsel(maskottchen)["skelett"]
    assert all(e.get("zmaj_ohne_haut") == "skelett" for e in teil), "das Vektor-Skelett muss dem Bildsatz weichen"
    assert "haut/skelett/" in inhalt.maskottchen_bilder(maskottchen), "der gemalte Satz ist nicht vollstaendig"
    leert = set(teil[0]["zmaj_leert"])
    bilder = {e["nm"] for e in grund["layers"] if e.get("ty") == 2}
    assert bilder <= leert, "im Rueckfall blieben Bilder unter den Knochen stehen"
    namen = {e["nm"] for e in teil}
    assert {"skelett_augen", "lids", "mouth_idle"} <= namen
    assert "eyes" not in namen


def test_feld_der_haende_an_der_wange(grund):
    """Die Knochenhaende des Skeletts vor den Augenhoehlen sind groesser als
    die Hand an der Wange; alle Saetze teilen sich ein Asset, die kleineren
    Bilder erweitert haut_einbauen.py durchsichtig (FELD, 16.10.2026)."""
    assert haut_einbauen.im_feld("unterarmR_wange", (88, 151)) == (114, 220)
    assert haut_einbauen.im_feld("unterarmR_wange", (114, 220)) == (114, 220)
    assert haut_einbauen.im_feld("unterarmR_wange", (100, 151)) == (100, 151)   # passt nicht ins Feld
    assert haut_einbauen.im_feld("body", (328, 575)) == (328, 575)
    _bild_drache(grund)
    groesse = {a["id"]: (a["w"], a["h"]) for a in grund["assets"]}
    for teil, (b, h, _x, _y) in haut_einbauen.FELD.items():
        assert groesse[teil] == (b, h), teil


def test_umwandeln_erweitert_auf_das_feld(tmp_path, monkeypatch):
    """umwandeln() gibt ffmpeg den pad-Filter mit, wenn ein Teil kleiner als
    sein Feld ist - aber nicht bei den Kostuemen (feld=False). Bis 16.10.2026
    ueberschrieb eine lokale Variable den Parameter, und der Filter kam nie
    mit; im_feld() allein hatte das nicht gezeigt."""
    quelle = tmp_path / "quelle"
    quelle.mkdir()
    for teil, (b, h) in (("unterarmL_wange", (88, 151)), ("body", (328, 575))):
        (quelle / (teil + ".png")).write_bytes(
            b"\x89PNG\r\n\x1a\n" + bytes(4) + b"IHDR" + b.to_bytes(4, "big") + h.to_bytes(4, "big"))
    aufrufe = []

    class Fertig:
        returncode = 0
        stderr = ""

    def ffmpeg(cmd, **_):
        aufrufe.append(cmd)
        return Fertig()

    monkeypatch.setattr(haut_einbauen.subprocess, "run", ffmpeg)
    haut_einbauen.umwandeln("ffmpeg", str(quelle), str(tmp_path / "ziel"))
    vf = {os.path.basename(c[c.index("-i") + 1]): c[c.index("-vf") + 1] if "-vf" in c else None for c in aufrufe}
    assert vf == {"body.png": None, "unterarmL_wange.png": "format=rgba,pad=114:220:0:0:color=0x00000000"}
    aufrufe.clear()
    haut_einbauen.umwandeln("ffmpeg", str(quelle), str(tmp_path / "ziel"), feld=False)
    assert not any("-vf" in c for c in aufrufe)


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


def test_kopfschuetteln(grund):
    """Ajdin, 15.10.2026: bei einer falschen Antwort soll der Drache "richtig
    den Kopf schuetteln" und "durchgehend boese gucken", statt den Kopf um
    den Hals zu wiegen. In no, no_l und no_r wechseln sich darum die
    abgewandten Koepfe links und rechts ab, dazwischen steht nur der finstere
    Kopf (nie der neutrale, nie das Blinzeln), no_l beginnt links, no_r
    rechts, und der Kopf kippt und rutscht dabei nicht (16.10.2026)."""
    _bild_drache(grund)
    koepfe = [e for e in grund["layers"] if e["nm"].startswith("bild_kopf_")]
    kopf = next(e for e in grund["layers"] if e["nm"] == "head")
    marken = {m["cm"]: (m["tm"], m["tm"] + m["dr"]) for m in grund["markers"]}

    def im_bild(t):
        return next(e["nm"].split("_", 2)[2] for e in koepfe if _deckkraft(e, t) == 100)

    def werte(spur, a, e):
        return [json.dumps(k["s"]) for k in spur["k"] if a <= k["t"] < e]

    for name, zuerst in (("no", "links"), ("no_l", "links"), ("no_r", "rechts")):
        a, e = marken[name]
        folge = [im_bild(t) for t in range(a, e)]
        assert set(folge) == {"finster", "links", "rechts"}, (name, folge)
        schwuenge = [k for i, k in enumerate(folge) if k != "finster" and folge[i - 1] != k]
        assert schwuenge[0] == zuerst and len(schwuenge) >= 4, (name, schwuenge)
        assert all(x != y for x, y in zip(schwuenge, schwuenge[1:])), (name, schwuenge)
        assert folge[0] == folge[-1] == "finster", name
        assert set(werte(kopf["ks"]["r"], a, e)) <= {"[0]"}, name
        assert len(set(werte(kopf["ks"]["p"], a, e))) <= 1, name


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
    steht bewusst in OHNE_HAUTSATZ (siehe haut_einbauen.py; bis 16.10.2026
    das Skelett, seitdem ist es ein gemalter Satz)."""
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


def test_app_nimmt_die_bilder_der_kostueme_mit(index_html):
    """zmajDaten() muss die neue Form {layers, assets} kennen und deren
    Bilder unabhaengig von der Hautfarbe unter maskottchen/zierrat/ suchen -
    sonst traegt der Drache leere Bild-Ebenen (16.10.2026)."""
    t = index_html.replace("\r\n", "\n")
    rumpf = t[t.index("async function zmajDaten("):t.index("function zmaj(mood")]
    assert "Array.isArray(teil.layers)" in rumpf and "zierBilder.push(...(teil.assets || []))" in rumpf
    assert re.search(r"zierBilder\.filter\(a => benutzt\.has\(a\.id\)\)", rumpf)
    assert re.search(r"\{u: 'maskottchen/' \+ \(a\.u \|\| ''\)\}", rumpf)


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
