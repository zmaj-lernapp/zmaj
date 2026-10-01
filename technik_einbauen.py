# -*- coding: utf-8 -*-
r"""
technik_einbauen.py  –  überträgt den Technik-Wortschatz aus entwurf_technik.py
                        in die App

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" technik_einbauen.py
    ... --schreiben

Ajdin hat die 60 Wörter und 10 Lückensätze am 01.10.2026 in der Prüfliste
durchgesehen (Entscheidungen im Kopf von entwurf_technik.py) und gesagt:
"kannst du ja machen, lass alles vorbereiten für den release".

WAS PASSIERT
  vokabeln.py        die zwei Level hinter "Technik & Reparatur", also am Ende
                     von Sektion 4 (Ajdins Wahl); die Lückensätze hinter
                     denen von "technik"
  uebersetzungen.py  je Sprache die Zeilen vor "# ENDE <code> texte";
                     schon vorhandene Schlüssel werden nicht doppelt
                     eingetragen

Beide Dateien haben CRLF und werden vorher als *.vor_technik gesichert.
Danach: inhalt_bauen.py, texte_pruefen.py, ton_bauen.py (Aufnahmen),
ton_pruefen.py.
"""
import io
import json
import os
import shutil
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import entwurf_technik as et

SCHREIBEN = "--schreiben" in sys.argv
SPRACHEN = {"en": "en", "tr": "tr", "sv": "sv", "nl": "nl", "nb": "nb", "da": "da", "fr": "fr"}


def lies(name):
    roh = io.open(os.path.join(HIER, name), encoding="utf-8", newline="").read()
    return roh.replace("\r\n", "\n"), "\r\n" in roh


def schreib(name, text, crlf):
    pfad = os.path.join(HIER, name)
    sicherung = pfad + ".vor_technik"
    if not os.path.exists(sicherung):
        shutil.copy2(pfad, sicherung)
    io.open(pfad, "w", encoding="utf-8", newline="").write(text.replace("\n", "\r\n") if crlf else text)


def q(s):
    return json.dumps(s, ensure_ascii=False)


def level_quelltext(l):
    zeilen = ['    {"id": %s, "label": %s, "sektion": %s, "tipp": %s,'
              % (q(l["id"]), q(l["label"]), q(l["sektion"]), q(l["tipp"])),
              '     "baut_auf": [%s],' % ", ".join(q(b) for b in l["baut_auf"]),
              '     "words": [']
    for w in l["words"]:
        links = '{"de": %s,' % q(w["de"])
        zeilen.append('        %-45s "bs": %s},' % (links, q(w["bs"])))
    zeilen.append("    ]},")
    return "\n".join(zeilen)


def main():
    # ---- vokabeln.py
    vok, crlf_v = lies("vokabeln.py")
    if '"id": "auto_werkstatt"' in vok:
        raise SystemExit("Schon eingebaut.")
    anfang = vok.index('    {"id": "technik",')
    ende = vok.index('\n    {"id": ', anfang + 10)          # das naechste Level
    # vor die Leerzeile davor einsetzen, damit der Abstand bleibt
    einsetzen = ("\n    # Technik-Wortschatz, durchgesehen von Ajdin am 01.10.2026"
                 " (entwurf_technik.py)\n"
                 + "\n\n".join(level_quelltext(l) for l in et.LEVEL) + "\n")
    vok = vok[:ende] + einsetzen + vok[ende:]

    letzte = vok.rindex('    {"kat": "technik",')
    zeilenende = vok.index("\n", letzte) + 1
    saetze = "".join('    {"kat": %s, "text": %s, "answer": %s, "de": %s},\n'
                     % (q(s["kat"]), q(s["text"]), q(s["answer"]), q(s["de"])) for s in et.SAETZE)
    vok = vok[:zeilenende] + saetze + vok[zeilenende:]

    # ---- uebersetzungen.py
    ueb, crlf_u = lies("uebersetzungen.py")
    neu_gesamt = 0
    for code in SPRACHEN:
        marke = "    # ENDE %s texte" % code
        assert ueb.count(marke) == 1, marke
        tabelle = et.UEBERSETZUNGEN[code]
        start = ueb.rindex('"%s": {' % code, 0, ueb.index(marke)) if ('"%s": {' % code) in ueb[:ueb.index(marke)] else 0
        block = ueb[start:ueb.index(marke)]
        zeilen = []
        for de, ziel in tabelle.items():
            if "\n    %s:" % q(de) in block:
                continue                      # gibt es schon
            zeilen.append("    %s: %s,\n" % (q(de), q(ziel)))
        kopf = "    # Technik-Wortschatz, 01.10.2026 (entwurf_technik.py)\n"
        ueb = ueb.replace(marke, kopf + "".join(zeilen) + marke)
        neu_gesamt += len(zeilen)
        print("%s: %d neue Zeilen" % (code, len(zeilen)))

    print("vokabeln.py: %d Level, %d Wörter, %d Sätze"
          % (len(et.LEVEL), sum(len(l["words"]) for l in et.LEVEL), len(et.SAETZE)))
    if SCHREIBEN:
        schreib("vokabeln.py", vok, crlf_v)
        schreib("uebersetzungen.py", ueb, crlf_u)
        print("geschrieben (Sicherungen *.vor_technik)")
    else:
        print("Probelauf - mit --schreiben wirklich schreiben")


if __name__ == "__main__":
    main()
