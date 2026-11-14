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

Dazu pismo ("Pismo nani", 14.11.2026): Ajdin hat "napraviti pitu" statt
"skuhati pitu" entschieden (Prüfbericht 1.4, S3, F20). Der Ton (g09, Vesna)
und seine Wortzeiten gehören zum alten Text. Die Geschichte wird in derselben
Vesna-Runde wie die B1-Texte neu gesprochen, bis dahin wartet sie hier.

WORTZEITEN_NEU (14.11.2026, Offen-Liste, Punkt 3): Geschichten, die ihren Ton
haben und behalten, deren Wortzeiten "w" aber zu einem alten Text gehören.
opcina ("Na općini") sagt jetzt "Hvala vam na pomoći" statt "Hvala Vam" (F23:
klein im Gespräch). Der Schlüssel ist kleingeschrieben, die Aufnahme g10 passt
weiter, und die Zahl der Wörter ist gleich, die App markiert also richtig.
ton_bauen.wortzeiten_passen() vergleicht den Text aber mit Groß- und
Kleinschreibung: Der nächste ton_bauen.py-Lauf wirft "w" von g10 weg, und
wortzeiten_holen.py --holen nimmt g10 von selbst mit (spricht neu, wenige
Cent). test_wortzeiten_neu_ist_aktuell in test_wortzeiten.py meldet, sobald die
Zeiten wieder passen: dann hier streichen.
"""

GESCHICHTEN = frozenset({"b1_doktor", "b1_selidba", "b1_rodjendan", "b1_utakmica",
                         "b1_zanat", "b1_kahva", "b1_mejl", "b1_zmaj",
                         "pismo"})

WORTZEITEN_NEU = frozenset({"opcina"})


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
