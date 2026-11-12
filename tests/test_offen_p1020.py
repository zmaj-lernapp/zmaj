# -*- coding: utf-8 -*-
"""tests/offen_p1020.json bleibt ehrlich: nur Schluessel, die in der App gesprochen werden
und wirklich noch keinen Ton haben (Wortschatz-Pakete 10 bis 20, 07.11.2026)."""
import io
import json
import os

import offen_p1020


def test_offen_steht_in_der_app():
    import ton_bauen
    posten = {p["key"] for p in ton_bauen.sammle()}
    fremd = sorted(offen_p1020.TON - posten)
    assert not fremd, fremd[:20]


def test_offen_hat_wirklich_noch_keinen_ton(wurzel):
    import ton_bauen
    index = {e["key"] for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                 encoding="utf-8"))["toene"]}
    schon = sorted(k for k in offen_p1020.TON if k in index or k in ton_bauen.nur_emir())
    assert not schon, "hat Ton, aus tests/offen_p1020.json streichen: %s" % schon[:20]
