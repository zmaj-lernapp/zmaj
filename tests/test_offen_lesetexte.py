# -*- coding: utf-8 -*-
"""tests/offen_lesetexte.json bleibt ehrlich: nur Schlüssel, die in der App gesprochen
werden und wirklich noch keinen Ton haben (B1-Lesetexte, 13.11.2026)."""
import io
import json
import os

import offen_lesetexte


def test_offen_steht_in_der_app():
    import ton_bauen
    posten = {p["key"]: p["art"] for p in ton_bauen.sammle()}
    fremd = sorted(offen_lesetexte.TON - set(posten))
    assert not fremd, fremd[:20]
    falsch = sorted(k for k in offen_lesetexte.GESCHICHTEN if posten[k] != "geschichte")
    assert not falsch, falsch


def test_offen_hat_wirklich_noch_keinen_ton(wurzel):
    import ton_bauen
    index = {e["key"] for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                 encoding="utf-8"))["toene"]}
    schon = sorted(k for k in offen_lesetexte.TON if k in index or k in ton_bauen.nur_emir())
    assert not schon, "hat Ton, aus tests/offen_lesetexte.json streichen: %s" % schon[:20]


def test_nur_die_b1_texte_warten():
    """Die alten zwölf Geschichten haben ihren Ton. Wartet einer von ihnen, ist
    etwas an seinem Text verrutscht."""
    import geschichten
    import ton_bauen
    alt = {ton_bauen.schluessel(g["text"]) for g in geschichten.GESCHICHTEN if not g["id"].startswith("b1_")}
    assert not alt & offen_lesetexte.GESCHICHTEN
