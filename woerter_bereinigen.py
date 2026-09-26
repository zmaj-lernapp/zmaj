# -*- coding: utf-8 -*-
r"""
woerter_bereinigen.py  –  macht aus der Durchsicht eine einbaufertige Liste

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" woerter_bereinigen.py
    ... --schreiben

Ajdin hat am 26.09.2026 alle 569 vorgelegten Wörter entschieden: 568 behalten,
eines abgelehnt, sechs selbst geändert. Vor dem Einbau sind drei Dinge zu tun.

1. ZEHN DUBLETTEN AUFLÖSEN

Die Vorlage entstand in zwei Runden, und die ältere hatte keine Sonderzeichen.
Man sieht es schon an den Gruppennamen: „Suesses & Kaffeeritual" gegen „Süßes",
„Getraenke" gegen „Rakija". Neun Wörter stehen deshalb zweimal drin, einmal
richtig und einmal ohne č, ć, š, ž:

    begova čorba / begova corda        džezva / dzezva
    ćevabdžinica / cevabdzinica        kafić / kafic
    naručiti / naruciti                šampita / sampita
    slastičarna / slasticarna          šljivovica / sljivovica
    viljuška / viljuska

Beim zehnten Paar ging es schief: `krompiruša` stand als Nr. 414 und wurde
abgelehnt, `krompirusa` als Nr. 325 und wurde behalten. Aussortiert wurde also
die richtige Schreibweise. Dieses Skript dreht das um.

2. DIE SECHS ÄNDERUNGEN IN FORM BRINGEN

Vier davon stehen schon in WORTSCHATZ_BEIM_EINBAUEN.md, zwei sind neu
(Hahn → horoz, Ratte → pacov). Zwei der Notizen enthalten ein zweites Wort,
das einen eigenen Eintrag bekommt.

3. EINE FRAGE BLEIBT OFFEN

`prodavač` (neu) gegen `prodavac` (in vokabeln.py vorhanden). Beide Formen
gibt es, aber zweimal dasselbe Wort verwirrt. Das Skript meldet es und
entscheidet nichts.
"""

import io
import json
import os
import sys
import unicodedata
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, "woerter_gesichtet.json")
ZIEL = os.path.join(HIER, "woerter_fertig.json")
SCHREIBEN = "--schreiben" in sys.argv

SONDER = set("čćžšđ")

# Ajdins sechs Änderungen, in saubere Einträge übersetzt.
# Grundlage: WORTSCHATZ_BEIM_EINBAUEN.md vom 25.09.2026, ergänzt um die
# zwei neuen vom 26.09.
AENDERUNGEN = {
    "Hirsch":     {"bs": "jelen"},
    "Wespe":      {"bs": "osa",
                   "anhang": "Die maennliche Form os kommt vor, osa ist die uebliche."},
    "Floh":       {"bs": "buha"},
    "Beisst er?": {"bs": "Hoće li ujesti?"},
    "Hahn":       {"bs": "horoz"},     # bewusst das Lehnwort, nicht „pijevac"
    "Ratte":      {"bs": "pacov"},
}

# Zweitwörter, die aus Ajdins Notizen als eigene Einträge entstehen.
ZUSATZ = [
    {"de": "Flohmarkt", "bs": "buvljak", "gruppe": "Insekten & Kleintiere",
     "anmerkung": "Aus Ajdins Anmerkung zu „Floh“. Alltagswort, auch „buvlja pijaca“."},
    {"de": "Der Hund hat mich gebissen", "bs": "Pas me je ujeo",
     "gruppe": "Rund ums Tier: Verben & Saetze",
     "anmerkung": "Aus Ajdins Anmerkung zu „Beisst er?“."},
]


def ohne(s):
    s = s.lower().replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def hat_sonder(s):
    return any(c in s.lower() for c in SONDER)


def main():
    d = json.load(io.open(QUELLE, encoding="utf-8"))
    beh = d["behalten"]
    print("%d Wörter behalten, %d entschieden von %d\n"
          % (len(beh), len(d["stand"]), d["von"]))

    strich = "=" * 66

    # ---------------------------------------------------------------- 1
    print(strich)
    print("1. Dubletten")
    print(strich)
    gruppen = defaultdict(list)
    for e in beh:
        gruppen[ohne(e["bs"])].append(e)

    raus = []
    for k, v in sorted(gruppen.items()):
        if len(v) < 2:
            continue
        mit = [e for e in v if hat_sonder(e["bs"])]
        ohne_ = [e for e in v if not hat_sonder(e["bs"])]
        if mit and ohne_:
            for e in ohne_:
                raus.append(e)
                print("   raus: %-16s  bleibt: %-16s (%s)"
                      % (e["bs"], mit[0]["bs"], mit[0].get("gruppe", "")[:24]))
        elif len(v) > 1:
            print("   PRÜFEN: %s steht %dx, keine Schreibweise ist eindeutig richtig"
                  % (v[0]["bs"], len(v)))

    fertig = [e for e in beh if e not in raus]
    print("\n   %d Dubletten entfernt, %d bleiben" % (len(raus), len(fertig)))

    # krompiruša: die richtige Fassung wurde abgelehnt, die falsche behalten
    for e in fertig:
        if ohne(e["bs"]) == "krompirusa" and not hat_sonder(e["bs"]):
            print("\n   krompirusa → krompiruša (die richtige Fassung war abgelehnt worden)")
            e["bs"] = "krompiruša"
            e["de"] = e["de"].replace("Krompirusa", "Krompiruša")
            e["anmerkung"] = (e.get("anmerkung", "") +
                              " Schreibweise am 26.09.2026 berichtigt.").strip()
    print()

    # ---------------------------------------------------------------- 2
    print(strich)
    print("2. Ajdins sechs Änderungen")
    print(strich)
    offen = dict(AENDERUNGEN)
    for e in fertig:
        if e.get("de") in AENDERUNGEN:
            neu = AENDERUNGEN[e["de"]]
            if e["bs"] != neu["bs"]:
                print("   %-14s %-44s → %s" % (e["de"], e["bs"][:43], neu["bs"]))
                e["bs"] = neu["bs"]
                if neu.get("anhang"):
                    e["anmerkung"] = (e.get("anmerkung", "") + " " + neu["anhang"]).strip()
            offen.pop(e["de"], None)
    if offen:
        print("\n   NICHT GEFUNDEN: %s" % ", ".join(offen))
        return 1
    print()

    # ---------------------------------------------------------------- 3
    print(strich)
    print("3. Zusatzwörter aus den Anmerkungen")
    print(strich)
    vorhanden = {ohne(e["bs"]) for e in fertig}
    for z in ZUSATZ:
        if ohne(z["bs"]) in vorhanden:
            print("   %-28s steht schon drin" % z["bs"])
            continue
        z = dict(z, geaendert=False)
        fertig.append(z)
        print("   %-28s %s" % (z["bs"], z["de"]))
    print()

    # ---------------------------------------------------------------- 4
    print(strich)
    print("4. Offene Frage")
    print(strich)
    sys.path.insert(0, HIER)
    import vokabeln
    alt = {}
    for k in vokabeln.KATEGORIEN:
        for w in k.get("words", []):
            if w.get("bs"):
                alt.setdefault(ohne(w["bs"]), set()).add(w["bs"])
    fragen = 0
    for e in fertig:
        k = ohne(e["bs"])
        if k in alt and e["bs"] not in alt[k]:
            fragen += 1
            print("   neu „%s“ gegen vorhanden „%s“ – beides gibt es, aber nicht beides"
                  % (e["bs"], ", ".join(alt[k])))
    if not fragen:
        print("   keine")
    print()

    print(strich)
    print("%d Wörter einbaufertig." % len(fertig))
    if SCHREIBEN:
        io.open(ZIEL, "w", encoding="utf-8").write(
            json.dumps({"woerter": fertig, "stand": "26.09.2026",
                        "aus": "woerter_gesichtet.json"},
                       ensure_ascii=False, indent=1))
        print("geschrieben: %s" % os.path.basename(ZIEL))
    else:
        print("(Probelauf. Mit --schreiben wirklich schreiben.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
