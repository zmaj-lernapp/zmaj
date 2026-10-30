# -*- coding: utf-8 -*-
"""demo_bauen.py: die Web-Demo zeigt keine Werbung und kein Konto und sagt das auch."""
import io
import json
import os
import re

import pytest

# Abschnitt ohne Konto -> derselbe Abschnitt mit Konto, wortgleich bis auf
# die Nummer (und das Datum unter dem letzten Punkt). In der Datenschutz-
# erklärung steht seit v109 Abschnitt 3 (Konto) neu davor, alles Spätere
# ist eins weitergerückt.
AGB_GLEICH = {1: 1, 2: 2, 4: 4, 6: 6, 7: 7, 9: 9, 10: 10}
DATENSCHUTZ_GLEICH = {1: 1, 3: 4, 4: 5, 5: 6, 6: 7}


def _abschnitte(text):
    """{nummer: inhalt} eines Rechtstexts, ohne Nummer und ohne „Stand“."""
    teile = [t for t in re.split(r"(?=<b>\d+\. )", text) if t]
    return {int(re.match(r"<b>(\d+)\. ", t).group(1)):
            re.sub(r"<i>[^<]*</i>$", "", re.sub(r"^<b>\d+\. ", "", t)) for t in teile}


def _verweise(text):
    return {int(z) for z in re.findall(r"\d+", text)}


@pytest.fixture(scope="module")
def demo(tmp_path_factory):
    import demo_bauen
    ziel = str(tmp_path_factory.mktemp("demo") / "site")
    demo_bauen.main(["--ziel", ziel])
    return ziel


def test_keine_platzhalter_werbung(demo):
    html = io.open(os.path.join(demo, "index.html"), encoding="utf-8").read()
    import demo_bauen
    assert demo_bauen.WERBUNG_NEU in html and demo_bauen.WERBUNG_ALT not in html


def test_datenschutz_passt_zur_demo(demo, sprachcodes):
    """Ohne Werbung darf die Datenschutzerklärung keinen Werbepartner nennen."""
    for code in sprachcodes:
        daten = json.load(io.open(os.path.join(demo, "inhalt", code + ".json"), encoding="utf-8"))
        assert daten["werbung_laeuft"] is False, code
        assert "AdMob" not in daten["texte"]["set.datenschutz_text"], code


def test_rechtstexte_ohne_konto_in_der_demo(demo, sprachcodes):
    """Die Demo hat kein Konto (CLOUD_AN = false). Nutzungsbedingungen und
    Datenschutzerklärung nennen dort weder Firebase noch ein Pflichtkonto,
    in der App schon. Prüfbericht vom 28.10.2026."""
    import sprachen
    for code in sprachcodes:
        texte = json.load(io.open(os.path.join(demo, "inhalt", code + ".json"), encoding="utf-8"))["texte"]
        app = sprachen.texte(code)
        agb, ds = texte["set.agb_text"], texte["set.datenschutz_text"]
        assert "Firebase" not in agb + ds, code
        assert "Firebase" in app["set.datenschutz_text"], code
        assert agb == sprachen.TEXTE[code]["set.agb_text_ohne_konto"], code
        # Der Werbe-Abschnitt ist gefüllt, in der Fassung ohne Konto (Nr. 6)
        assert sprachen.TEXTE[code]["set.dsgvo_werbung_aus_ohne_konto"] in _abschnitte(ds)[6], code
        # Was in der App vom Konto handelt, steht in der Demo nicht
        app_agb, app_ds = _abschnitte(app["set.agb_text"]), _abschnitte(app["set.datenschutz_text"])
        for nr in (3, 5, 8):
            assert app_agb[nr] not in agb, (code, nr)
        for nr in (2, 3, 8, 9, 10):
            assert app_ds[nr] not in ds, (code, nr)
        assert not [k for k in texte if k.endswith("_ohne_konto")], code
    de = json.load(io.open(os.path.join(demo, "inhalt", "de.json"), encoding="utf-8"))["texte"]
    app = sprachen.texte("de")
    for k in ("set.agb_text", "set.datenschutz_text"):
        assert "Konto bei Zmaj" in app[k] and "Konto bei Zmaj" not in de[k], k


def test_rechtstexte_beide_fassungen_stimmig(sprachcodes):
    """Mit und ohne Konto lückenlos nummeriert, gemeinsame Abschnitte
    wortgleich, und jeder Verweis der Fassung ohne Konto zeigt auf den
    Abschnitt, auf den die App an derselben Stelle zeigt. Wer einen
    gemeinsamen Abschnitt nur in einer Fassung ändert, landet hier."""
    import sprachen
    for code in sprachcodes:
        t = sprachen.TEXTE[code]
        agb, agb_ohne = _abschnitte(t["set.agb_text"]), _abschnitte(t["set.agb_text_ohne_konto"])
        ds, ds_ohne = _abschnitte(t["set.datenschutz_text"]), _abschnitte(t["set.datenschutz_text_ohne_konto"])
        for a in (agb, agb_ohne, ds, ds_ohne):
            assert sorted(a) == list(range(1, len(a) + 1)), code
        for ohne, mit, gleich in ((agb_ohne, agb, AGB_GLEICH), (ds_ohne, ds, DATENSCHUTZ_GLEICH)):
            for o, m in gleich.items():
                assert ohne[o] == mit[m], (code, o, m)
        for ohne, mit, gleich in ((agb_ohne[8], agb[8], AGB_GLEICH),
                                  (ds_ohne[2], ds[2], DATENSCHUTZ_GLEICH),
                                  (t["set.dsgvo_werbung_aus_ohne_konto"], t["set.dsgvo_werbung_aus"],
                                   DATENSCHUTZ_GLEICH)):
            for nr in _verweise(ohne):
                assert gleich.get(nr) in _verweise(mit), (code, nr, ohne[:40])


def test_app_selbst_bleibt_unveraendert(demo, index_html):
    """Die Demo ändert nur die Kopie, nie web/."""
    import demo_bauen
    assert index_html.replace("\r\n", "\n").count(demo_bauen.WERBUNG_ALT) == 1


def test_keine_probedateien_in_der_demo(demo):
    for wurzel_, ordner, dateien in os.walk(demo):
        assert "_probe" not in ordner, wurzel_
    assert os.path.exists(os.path.join(demo, ".nojekyll"))


def test_schalter_wird_zurueckgesetzt(demo):
    import sys
    assert sys.modules["sprachen"].WERBUNG_LAEUFT is True
    assert sys.modules["sprachen"].KONTO_PFLICHT is True
