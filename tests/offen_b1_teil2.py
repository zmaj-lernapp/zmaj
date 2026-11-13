# -*- coding: utf-8 -*-
"""Was bei den B1-Lesetexten der Pakete 3 und 4 (13.11.2026) noch fehlt: der Ton.

Gesprochen wird erst, wenn Ajdin die acht Texte durchgesehen hat (Azure, Vesna,
wie die übrigen Geschichten). Danach ton_bauen.py und wortzeiten_holen.py laufen
lassen. Bis dahin lassen test_ton.py, test_wortzeiten.py und
tests_e2e/test_mitlesen.py genau diese
Geschichten durch: den Text und die Wörter, die nur in ihnen vorkommen, und
nichts sonst. test_wartet_auf_ton_ist_aktuell in test_wortzeiten.py meldet jede
Geschichte, die inzwischen ihren Ton hat: dann hier streichen. Ist die Menge
leer, kann diese Datei weg.
"""

GESCHICHTEN = frozenset({"b1_doktor", "b1_selidba", "b1_rodjendan", "b1_utakmica",
                         "b1_zanat", "b1_kahva", "b1_mejl", "b1_zmaj"})


def ton_schluessel():
    """Die Schlüssel aus ton_bauen.sammle(), die allein an diesen Geschichten
    hängen: ihr Text und jedes Wort, das sonst nirgends in der App gesprochen wird."""
    import geschichten
    import ton_bauen
    import vokabeln
    sonst = set()
    for kat in vokabeln.KATEGORIEN:
        for w in kat["words"]:
            sonst.add(ton_bauen.schluessel(w["bs"]))
    for s in vokabeln.SAETZE:
        sonst.add(ton_bauen.schluessel(s["text"].replace("___", s["answer"])))
    wartend = [g for g in geschichten.GESCHICHTEN if g["id"] in GESCHICHTEN]
    for g in geschichten.GESCHICHTEN:
        if g["id"] not in GESCHICHTEN:
            sonst.update(ton_bauen.schluessel(w) for w in ton_bauen.textwoerter(g["text"]))
    aus = {ton_bauen.schluessel(g["text"]) for g in wartend}
    for g in wartend:
        aus.update(k for k in (ton_bauen.schluessel(w) for w in ton_bauen.textwoerter(g["text"]))
                   if k not in sonst)
    return aus
