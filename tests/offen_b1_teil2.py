# -*- coding: utf-8 -*-
"""Was bei den B1-Lesetexten der Pakete 3 und 4 (13.11.2026) noch fehlt.

Seit dem 16.11.2026 liest Azure (Vesna) alle Geschichten vor, auch die acht
Texte von b1_doktor bis b1_zmaj und pismo mit "napraviti pitu" (Offen-Liste 6,
nach Ajdins A/B-Antworten vom 15.11.2026). GESCHICHTEN ist deshalb leer: hier
stünde eine Geschichte, deren Text samt Wörtern noch auf Vesna wartet. Die
Ton-Tests (test_ton.py, test_wortzeiten.py und tests_e2e/test_mitlesen.py)
lassen sie dann durch, test_wartet_auf_ton_ist_aktuell in test_wortzeiten.py
meldet jede, die inzwischen ihren Ton hat.

WOERTER: Geschichten, deren Text Ton hat, deren Wörter aber noch nicht. Ein
Wort, das nur in diesen Texten steht, hat noch keine Aufnahme: Wörter spricht
Emir, nicht Azure (seit 23.10.2026), und wann, entscheidet Ajdin. Bis dahin
lassen die Ton-Tests genau diese Wörter durch, tests/test_offen_lesetexte.py
meldet jedes, das inzwischen Ton hat. Die Wörter der Pakete 1 und 2 stehen in
tests/offen_lesetexte.json. Sind beide Mengen leer, kann diese Datei weg.

WORTZEITEN_NEU (14.11.2026, Offen-Liste, Punkt 3): Geschichten, die ihren Ton
haben und behalten, deren Wortzeiten "w" aber zu einem alten Text gehören.
ton_bauen.wortzeiten_passen() vergleicht den Text mit Groß- und
Kleinschreibung; wortzeiten_holen.py --holen nimmt so eine Geschichte von
selbst mit. test_wortzeiten_neu_ist_aktuell in test_wortzeiten.py meldet,
sobald die Zeiten wieder passen: dann hier streichen.
Bis zum 15.11.2026 stand hier opcina ("Hvala vam" statt "Hvala Vam", F23).
Seit Ajdins "mach doch alles groß" steht dort wieder "Hvala Vam na pomoći" wie
in der Aufnahme g10, die Wortzeiten passen wieder. Die Liste ist leer.
"""

GESCHICHTEN = frozenset()

WOERTER = frozenset({"b1_doktor", "b1_selidba", "b1_rodjendan", "b1_utakmica",
                     "b1_zanat", "b1_kahva", "b1_mejl", "b1_zmaj"})

WORTZEITEN_NEU = frozenset()


def ton_schluessel():
    """Die Schlüssel aus ton_bauen.sammle(), die allein an diesen Geschichten
    hängen: der Text der Geschichten aus GESCHICHTEN und jedes Wort aus
    GESCHICHTEN und WOERTER, das sonst nirgends in der App gesprochen wird."""
    import geschichten
    import ton_bauen
    import vokabeln
    ids = GESCHICHTEN | WOERTER
    sonst = set()
    for kat in vokabeln.KATEGORIEN:
        for w in kat["words"]:
            sonst.add(ton_bauen.schluessel(w["bs"]))
    for s in vokabeln.SAETZE:
        sonst.add(ton_bauen.schluessel(s["text"].replace("___", s["answer"])))
    for g in geschichten.GESCHICHTEN:
        if g["id"] not in ids:
            sonst.update(ton_bauen.schluessel(w) for w in ton_bauen.textwoerter(g["text"]))
    aus = {ton_bauen.schluessel(g["text"]) for g in geschichten.GESCHICHTEN if g["id"] in GESCHICHTEN}
    for g in geschichten.GESCHICHTEN:
        if g["id"] in ids:
            aus.update(k for k in (ton_bauen.schluessel(w) for w in ton_bauen.textwoerter(g["text"]))
                       if k not in sonst)
    return aus
