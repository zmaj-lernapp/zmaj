# -*- coding: utf-8 -*-
"""tests/offen_lesetexte.json bleibt ehrlich: nur Schlüssel, die in der App gesprochen
werden und wirklich noch keinen Ton haben (B1-Lesetexte, 13.11.2026). Seit dem
16.11.2026 haben alle Geschichten ihren Ton, es warten nur noch Wörter, auch die
aus tests/offen_b1_teil2.py."""
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


def test_keine_geschichte_wartet_mehr(wurzel):
    """Seit dem 16.11.2026 liest Vesna alle Geschichten vor (Offen-Liste 6):
    keine wartet mehr in einer der beiden Listen, jede hat ihre Aufnahme. Es
    warten nur noch Wörter."""
    import geschichten
    import offen_b1_teil2
    import ton_bauen
    index = {e["key"] for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                 encoding="utf-8"))["toene"]}
    assert offen_lesetexte.GESCHICHTEN == frozenset() and offen_b1_teil2.GESCHICHTEN == frozenset()
    assert [g["id"] for g in geschichten.GESCHICHTEN if ton_bauen.schluessel(g["text"]) not in index] == []
    texte = {ton_bauen.schluessel(g["text"]) for g in geschichten.GESCHICHTEN}
    assert not (offen_lesetexte.TON | offen_b1_teil2.ton_schluessel()) & texte


def test_woerter_aus_teil2_haben_wirklich_noch_keinen_ton(wurzel):
    """Dasselbe für die Wörter aus tests/offen_b1_teil2.py (Pakete 3 und 4):
    jedes wird in der App gesprochen und hat noch keine Aufnahme."""
    import offen_b1_teil2
    import ton_bauen
    index = {e["key"] for e in json.load(io.open(os.path.join(wurzel, "web", "audio", "index.json"),
                                                 encoding="utf-8"))["toene"]}
    posten = {p["key"]: p["art"] for p in ton_bauen.sammle()}
    aus = offen_b1_teil2.ton_schluessel()
    assert sorted(aus - set(posten)) == []
    assert sorted(k for k in aus if posten[k] != "wort") == []
    schon = sorted(k for k in aus if k in index or k in ton_bauen.nur_emir())
    assert not schon, "hat Ton, aus WOERTER in tests/offen_b1_teil2.py nehmen: %s" % schon[:20]
