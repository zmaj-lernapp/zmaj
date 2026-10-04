# -*- coding: utf-8 -*-
"""
inhalt.py  –  macht aus den Inhaltsdateien das, was die App bekommt

lade_daten(sprache) ist die EINE Stelle, an der vokabeln.py, grammatik.py,
geschichten.py, sprachen.py und uebersetzungen.py zusammenkommen. Alles
andere ruft sie auf: start.py (live am PC), inhalt_bauen.py (JSON für die
Handy-App), daten_exportieren.py (offener Datensatz), demo_bauen.py (Demo
auf GitHub Pages) und die Tests. Deshalb können Handy, Datensatz und Demo
nie voneinander abweichen.

Warum eine eigene Datei (04.10.2026): Bis dahin stand das alles in start.py,
zwischen rund 800 Zeilen Kontoverwaltung, Passwörtern, Sitzungen und
Bestätigungsmails aus der Zeit mit Server. Die App läuft längst ganz auf dem
Gerät, die Konten sind aus (KONTEN_AN = false in web/index.html). Wer den
Inhalt brauchte, musste trotzdem den ganzen alten Server importieren. Jetzt
steht hier nur noch der Inhalt; start.py ist ein schlanker Starter und
reicht lade_daten() für ältere Aufrufer einfach durch.

Nur Bausteine, die Python schon mitbringt.
"""

import importlib
import os
import re
import sys

ORDNER = os.path.dirname(os.path.abspath(__file__))
WEB_ORDNER = os.path.join(ORDNER, "web")
AUDIO_ORDNER = os.path.join(WEB_ORDNER, "audio")   # Tonspur: w0001.mp3 usw. + index.json

if ORDNER not in sys.path:
    sys.path.insert(0, ORDNER)
import vokabeln        # noqa: E402  (nach sys.path-Änderung importieren)
import grammatik       # noqa: E402
import geschichten     # noqa: E402
import sprachen        # noqa: E402  (Texte der Oberfläche in allen Sprachen)
import uebersetzungen  # noqa: E402  (Lerninhalte in allen Sprachen)


def lade_daten(sprache=None):
    """Liest die Inhaltsdateien bei jedem Aufruf neu ein, damit Änderungen
    sofort nach einem Browser-Neuladen sichtbar sind.

    sprache: Kürzel aus sprachen.py ("de", "en", "tr", …). Die Lerninhalte
    werden damit übersetzt, soweit uebersetzungen.py etwas dazu weiß.
    Der bosnische Teil bleibt natürlich immer bosnisch."""
    for modul in (vokabeln, grammatik, geschichten, sprachen, uebersetzungen):
        importlib.reload(modul)
    code = sprache if sprachen.ist_sprache(sprache) else sprachen.GRUNDSPRACHE
    daten = {
        "sektionen": getattr(vokabeln, "SEKTIONEN", []),
        "kategorien": vokabeln.KATEGORIEN,
        "saetze": vokabeln.SAETZE,
        "grammatik": getattr(grammatik, "GRAMMATIK", {}),
        "geschichten": getattr(geschichten, "GESCHICHTEN", []),
        "woerterbuch": getattr(geschichten, "WOERTERBUCH", {}),
    }
    daten = mit_kennung(daten)     # noch auf Deutsch, damit die Kennung gleich bleibt
    fertig, gesamt = uebersetzungen.stand(daten, code)
    daten = uebersetzungen.anwenden(daten, code)
    daten.update({
        "audio": eigene_aufnahmen(),
        "maskottchen": maskottchen_bilder(),
        "sprache": code,
        "sprachen": sprachen.SPRACHEN,
        "texte": sprachen.texte(code),
        # Ein Schalter für beides: echte Werbung und der Werbe-Abschnitt in
        # der Datenschutzerklärung. Er steht in sprachen.py, damit Text und
        # Verhalten nicht auseinanderlaufen können.
        "werbung_laeuft": bool(getattr(sprachen, "WERBUNG_LAEUFT", False)),
        "uebersetzt": {"fertig": fertig, "gesamt": gesamt},
    })
    return daten


def mit_kennung(daten):
    """Jedes Wort bekommt eine Kennung „bedeutung:wort“, also „hundert:sto“
    und „tisch:sto“.

    Die App merkt sich damit nicht nur das bosnische Wort, sondern auch, welche
    Bedeutung gemeint ist. Nötig, weil dasselbe Wort zweierlei heißen kann:
    „sto“ ist die Zahl hundert und der Tisch, „oko“ das Auge und „um herum“.
    Früher galt die zweite Bedeutung automatisch als gekonnt, sobald man die
    erste gelernt hatte.

    Die Kennung wird aus der deutschen Bedeutung gebaut, bevor übersetzt wird.
    Sie bleibt deshalb in jeder Sprache dieselbe."""
    daten["kategorien"] = [
        dict(k, words=[dict(w, id="%s:%s" % (w.get("de", "").strip().lower(), w.get("bs", "")))
                       for w in k.get("words", [])])
        for k in daten.get("kategorien", [])]
    return daten


def maskottchen_bilder():
    """Bilder in web/maskottchen: zmaj-frei.png (normal), optional zmaj-jubel.png,
    zmaj-traurig.png. Fehlen sie, zeichnet die App den Drachen als Vektor."""
    ordner = os.path.join(WEB_ORDNER, "maskottchen")
    try:
        return sorted(f for f in os.listdir(ordner) if f.lower().endswith((".png", ".webp", ".jpg", ".jpeg", ".gif", ".json", ".riv")))
    except OSError:
        return []


def eigene_aufnahmen():
    """Dateinamen im Ordner web/audio – nur noch für die Meldung beim Start.
    Welche Datei zu welchem Wort gehört, steht seit dem 15.09.2026 in
    web/audio/index.json. Die App liest diese Datei selbst und braucht
    den Server dafür nicht mehr."""
    try:
        return sorted(f for f in os.listdir(AUDIO_ORDNER)
                      if f.lower().endswith((".mp3", ".m4a", ".wav", ".ogg", ".webm")))
    except OSError:
        return []


# ---------------------------------------------------------------------------
# Inhalt prüfen – gibt Hinweise zurück, bricht aber nicht ab
# ---------------------------------------------------------------------------
def pruefe_vokabeln(daten):
    probleme = []
    ids = set()
    sektionen = {s.get("id") for s in daten.get("sektionen", [])}
    reihenfolge = [k.get("id") for k in daten["kategorien"]]
    for kat in daten["kategorien"]:
        for schluessel in ("id", "label", "words"):
            if schluessel not in kat:
                probleme.append(f"Level ohne '{schluessel}': {kat}")
        kid = kat.get("id", "?")
        if kid in ids:
            probleme.append(f"Level-id doppelt: '{kid}'")
        ids.add(kid)
        if sektionen and kat.get("sektion") not in sektionen:
            probleme.append(f"[{kid}] unbekannte Sektion '{kat.get('sektion')}'")
        for basis in kat.get("baut_auf", []):
            if basis not in reihenfolge:
                probleme.append(f"[{kid}] baut_auf nennt unbekanntes Level '{basis}'")
            elif reihenfolge.index(basis) >= reihenfolge.index(kid):
                probleme.append(f"[{kid}] baut_auf '{basis}' kommt erst später in der Liste")

        gesehen = set()
        for wort in kat.get("words", []):
            if "de" not in wort or "bs" not in wort:
                probleme.append(f"[{kid}] Wort ohne 'de' oder 'bs': {wort}")
                continue
            if not wort["de"].strip() or not wort["bs"].strip():
                probleme.append(f"[{kid}] leeres Wort: {wort}")
            if wort["bs"] in gesehen:
                probleme.append(f"[{kid}] doppelt: '{wort['bs']}'")
            gesehen.add(wort["bs"])

    for satz in daten["saetze"]:
        for schluessel in ("kat", "text", "answer", "de"):
            if schluessel not in satz:
                probleme.append(f"Satz ohne '{schluessel}': {satz}")
        if "___" not in satz.get("text", ""):
            probleme.append(f"Satz ohne Lücke '___': {satz.get('text')}")
        if satz.get("kat") not in ids:
            probleme.append(f"Satz mit unbekannter Kategorie '{satz.get('kat')}': {satz.get('text')}")

    # Grammatik-Lektionen
    for kid, lektion in daten.get("grammatik", {}).items():
        if kid not in ids:
            probleme.append(f"Grammatik für unbekanntes Level '{kid}'")
        for ue in lektion.get("uebungen", []):
            if ue.get("richtig") not in ue.get("optionen", []):
                probleme.append(f"[{kid}] Übung: 'richtig' steht nicht in 'optionen': {ue.get('frage')}")

    # Geschichten
    for g in daten.get("geschichten", []):
        if g.get("passt_zu") and g.get("passt_zu") not in ids:
            probleme.append(f"Geschichte '{g.get('id')}': passt_zu nennt unbekanntes Level '{g.get('passt_zu')}'")
        for f in g.get("fragen", []):
            if f.get("richtig") not in f.get("optionen", []):
                probleme.append(f"Geschichte '{g.get('id')}': 'richtig' fehlt in 'optionen': {f.get('frage')}")

    return probleme


def fehlende_woerter(daten):
    """Wörter in Geschichten, die im WOERTERBUCH fehlen (nur ein Hinweis)."""
    wb = daten.get("woerterbuch", {})
    fehlt = {}
    for g in daten.get("geschichten", []):
        eigene = {k.lower(): v for k, v in g.get("vokabeln", {}).items()}
        for w in re.findall(r"[^\W\d_]+", g["text"]):
            k = w.lower()
            if k not in wb and k not in eigene:
                fehlt.setdefault(g["id"], set()).add(w)
    return fehlt
