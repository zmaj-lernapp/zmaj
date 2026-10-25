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
        "satzbau": satzbau_fuer_app(getattr(vokabeln, "SATZBAU", [])),
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


# Satzzeichen, die am Rand einer Kachel wegfallen. Dieselben stehen in
# web/index.html (KACHEL_RAND) - die App trennt die Sätze genauso.
SATZZEICHEN = ".,!?¿¡:;\"„“”«»…()"


def satz_kacheln(satz):
    """Die Kacheln eines Satzes, wie die App sie zeigt und vergleicht: an
    Leerzeichen getrennt, Satzzeichen am Rand weg, klein geschrieben."""
    teile = []
    for roh in str(satz or "").split():
        wort = roh.strip(SATZZEICHEN).lower()
        if wort:
            teile.append(wort)
    return teile


def satzbau_fuer_app(liste):
    """Nur kat, bs, de, auch, ohne, grund (die Grundformen aus formen) und
    zahl gehen an die App. quelle, notiz und die gebeugten Formen selbst sind
    Arbeitsfelder für die Prüfung und für uns (13.10.2026) - auf dem Handy
    wären sie bloß Ballast in acht Dateien."""
    raus = []
    for s in liste:
        neu = {"kat": s.get("kat"), "bs": s.get("bs", ""), "de": s.get("de", "")}
        if s.get("auch"):
            neu["auch"] = list(s["auch"])
        # ohne (14.10.2026): Wörter, die bei diesem Satz nie als falsche Kachel
        # kommen dürfen, weil sie ihn auch richtig machen (somun neben pogaču,
        # ćao neben Merhaba). Die App sperrt sie in kachelAblenker().
        # Keine Liste geht unverändert weiter, damit pruefe_vokabeln() es meldet.
        if s.get("ohne"):
            neu["ohne"] = list(s["ohne"]) if isinstance(s["ohne"], (list, tuple)) else s["ohne"]
        # Von formen nur die Grundformen: Steht "kahvu" im Satz, soll er erst
        # kommen, wenn "kahva" in dieser Lektion schon dran war. Die gebeugte
        # Form selbst kennt die App aus keinem Wort und könnte sie nicht prüfen.
        grund = sorted({str(g).lower() for g in (s.get("formen") or {}).values()})
        if grund:
            neu["grund"] = grund
        # zahl (25.10.2026): die Zahlen, mit denen der Satz kommen darf, siehe
        # zahl_fassung() unten. Unverändert, damit pruefe_zahlen() auch einen
        # kaputten Eintrag sieht.
        if "zahl" in s:
            neu["zahl"] = dict(s["zahl"]) if isinstance(s["zahl"], dict) else s["zahl"]
        raus.append(neu)
    return raus


# ---------------------------------------------------------------------------
# Zahlen, die wechseln (25.10.2026)
# ---------------------------------------------------------------------------
# Ajdin am 25.10.2026: „die sätze immer mit der gleichen zahl ist und nicht
# mal variiert“. Gemeint ist die Zahl im Satz: „Sada je pet sati.“ kam immer
# mit fünf. Ein Satz mit "zahl" (vokabeln.py) kommt in der App je Aufgabe mit
# einer der Zahlen aus "werte" - bosnisch als Wort, in der Bedeutung als
# Ziffer („Jetzt ist es 7 Uhr.“). Welche Sätze und welche Zahlen, hat Ajdin in
# einer Tabelle freigegeben („Ja, alle so“); mehr kommt nicht dazu.
#
# zahl_fassung() hier und zahlFassung() in web/index.html müssen Zeichen für
# Zeichen dasselbe bauen: ton_bauen.sammle() nimmt die Fassungen von hier, und
# die App sucht die Aufnahme unter dem Satz, den sie selbst gebaut hat. Weicht
# eins ab, bleibt der Satz stumm. tests_e2e/test_zahlen.py vergleicht beide.

# Wie zahlAlsWort() in index.html, aber nur einzelne Wörter: 0 bis 19, die
# glatten Zehner und 100. Mehr brauchen die Sätze nicht, und ein Zahlwort aus
# zwei Wörtern ("dvadeset jedan") gäbe im Satzbau eine Kachel mehr.
ZAHL_EINER = ("nula", "jedan", "dva", "tri", "četiri", "pet", "šest", "sedam", "osam", "devet",
              "deset", "jedanaest", "dvanaest", "trinaest", "četrnaest", "petnaest",
              "šesnaest", "sedamnaest", "osamnaest", "devetnaest")
ZAHL_ZEHNER = {2: "dvadeset", 3: "trideset", 4: "četrdeset", 5: "pedeset",
               6: "šezdeset", 7: "sedamdeset", 8: "osamdeset", 9: "devedeset"}
# "frei": Hier dürfen 2-4 und ab 5 gemischt sein. "uhrzeit": die Uhrzeit ohne
# Nomen („u pet“, „u tri“). "dana": dva dana wie pet dana - die Form ist gleich.
ZAHL_FREI = ("uhrzeit", "dana")
ZAHL_FELDER = {"wort", "werte", "de", "weiblich", "frei"}


def zahl_wort(n, weiblich=False):
    """Das bosnische Zahlwort für n, sonst None. weiblich: 2 heißt dvije
    (dvije kahve, dvije sestre, dvije jabuke)."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        return None
    if weiblich and n == 2:
        return "dvije"
    if n < 20:
        return ZAHL_EINER[n]
    if n < 100 and n % 10 == 0:
        return ZAHL_ZEHNER[n // 10]
    return "sto" if n == 100 else None


def zahl_wert(wort, weiblich=False):
    """Umkehrung von zahl_wort(): "pet" -> 5, "dvije" -> 2 (nur weiblich)."""
    w = str(wort or "").strip().lower()
    for n in range(101):
        if zahl_wort(n, weiblich) == w:
            return n
    return None


def zahl_klasse(n):
    """Welche Form das Nomen nach n braucht: "1" (jedan brat), "2-4" (dva
    brata, tri sestre) oder "5+" (pet godina, deset sati). 11 bis 14 gehen
    wie ab 5, 21 und 22 wieder wie 1 und 2."""
    if n % 10 == 1 and n % 100 != 11:
        return "1"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return "2-4"
    return "5+"


def _zahl_muster(wort):
    """Das Wort als ganzes Wort: davor und danach kein Buchstabe. Dieselbe
    Regel wie zahlTausch() in index.html."""
    return re.compile(r"(^|[\W\d_])(%s)(?=[\W\d_]|$)" % re.escape(wort), re.IGNORECASE)


def zahl_zaehlen(text, wort):
    """Wie oft wort als ganzes Wort in text steht, Groß/klein egal."""
    return len(_zahl_muster(wort).findall(str(text or "")))


def zahl_ersetzen(text, alt, neu):
    """Das Zahlwort alt als ganzes Wort durch neu ersetzen, mit der
    Großschreibung des Originals: "Dvije kahve" -> "Tri kahve"."""
    def tausch(m):
        gross = m.group(2)[:1].isupper()
        return m.group(1) + (neu[:1].upper() + neu[1:] if gross else neu)
    return _zahl_muster(alt).sub(tausch, text)


# Türkisch „um 7“: 7'de, 3'te, 10'da. Die Endung hängt am letzten gesprochenen
# Wort der Zahl (bir, iki, üç, dört, beş, altı, yedi, sekiz, dokuz; on, yirmi,
# otuz, kırk, elli, altmış, yetmiş, seksen, doksan; yüz): a oder e nach der
# Vokalharmonie, und nach ç, t, ş, k wird aus d ein t (üçte, dörtte, beşte,
# kırkta, altmışta, yetmişte). Ohne Einer gilt der Zehner, bei 100 yüzde.
# Gebraucht wird es nur bei der Uhrzeit bis 12; die Zehner stehen für den
# Fall, dass einmal mehr dazukommt. Dieselbe Tabelle steht in index.html.
TR_LOK_EINER = ("da", "de", "de", "te", "te", "te", "da", "de", "de", "da")
TR_LOK_ZEHNER = ("", "da", "de", "da", "ta", "de", "ta", "te", "de", "da")


def tr_lokativ(n):
    e, z = n % 10, (n // 10) % 10
    endung = "da" if n == 0 else TR_LOK_EINER[e] if e else TR_LOK_ZEHNER[z] if z else "de"
    return "%d'%s" % (n, endung)


def zahl_vorlage(vorlage, n):
    """Die Bedeutung mit Ziffer: {n} -> "7", {lok} -> "7'de"."""
    return str(vorlage or "").replace("{n}", str(n)).replace("{lok}", tr_lokativ(n))


def zahl_fassung(satz, n):
    """Der Satz mit der Zahl n: text, answer, bs und jedes auch mit dem neuen
    Zahlwort, de aus der Vorlage mit der Ziffer. Alles andere bleibt."""
    z = satz["zahl"]
    alt, neu = z["wort"], zahl_wort(n, z.get("weiblich"))
    f = dict(satz, de=zahl_vorlage(z.get("de"), n))
    for feld in ("text", "answer", "bs"):
        if isinstance(satz.get(feld), str):
            f[feld] = zahl_ersetzen(satz[feld], alt, neu)
    if satz.get("auch"):
        f["auch"] = [zahl_ersetzen(a, alt, neu) for a in satz["auch"]]
    return f


def zahl_fassungen(satz):
    """[(n, Fassung), ...] für jede Zahl aus werte, die heutige eingeschlossen.
    Ohne "zahl" eine leere Liste."""
    z = satz.get("zahl") if isinstance(satz, dict) else None
    if not isinstance(z, dict):
        return []
    return [(n, zahl_fassung(satz, n)) for n in z.get("werte", [])
            if zahl_wort(n, z.get("weiblich"))]


def fertiger_satz(satz):
    """Was die App nach der Antwort spricht: den Lückensatz mit eingesetzter
    Lösung, den Satzbau-Satz, wie er ist."""
    if "text" in satz:
        return satz["text"].replace("___", satz.get("answer", ""))
    return satz.get("bs", "")


def _zahl_formen(satz):
    """Jede Form, in der das Zahlwort stehen muss: beim Lückensatz der
    fertige Satz mit answer und mit jeder Antwort aus auch, beim Satzbau bs
    und jede Reihenfolge aus auch."""
    auch = [a for a in (satz.get("auch") or []) if isinstance(a, str)]
    if "text" in satz:
        return [str(satz.get("text", "")).replace("___", a) for a in [str(satz.get("answer", ""))] + auch]
    return [str(satz.get("bs", ""))] + auch


def pruefe_zahlen(daten):
    """Die Sätze mit "zahl" (25.10.2026). Befunde wie in pruefe_vokabeln(),
    das sie mit aufnimmt. Die Vorlage "de" wird in der Sprache der Daten
    geprüft - nach uebersetzungen.anwenden() ist sie dort schon übersetzt."""
    probleme = []
    sprache = daten.get("sprache") or "de"
    for art, liste in (("Lückensatz", daten.get("saetze", [])), ("Satzbau", daten.get("satzbau", []))):
        for satz in liste:
            if "zahl" not in satz:
                continue
            z = satz["zahl"]
            kennung = "Zahl im %s [%s] '%s'" % (art, satz.get("kat"), satz.get("text", satz.get("bs")))
            if not isinstance(z, dict):
                probleme.append(f"{kennung}: 'zahl' ist kein dict")
                continue
            fremd = sorted(set(z) - ZAHL_FELDER)
            if fremd:
                probleme.append(f"{kennung}: unbekannte Felder {fremd}")
            wort, werte, frei = z.get("wort"), z.get("werte"), z.get("frei")
            weiblich = bool(z.get("weiblich"))
            if not isinstance(wort, str) or not isinstance(werte, list) or not werte:
                probleme.append(f"{kennung}: 'wort' oder 'werte' fehlt")
                continue
            heute = zahl_wert(wort, weiblich)
            if heute is None or zahl_wort(heute, weiblich) != wort:
                probleme.append(f"{kennung}: '{wort}' ist kein Zahlwort (klein, wie zahl_wort())")
            elif heute not in werte:
                probleme.append(f"{kennung}: die heutige Zahl {heute} fehlt in 'werte'")
            if len(set(map(repr, werte))) != len(werte):
                probleme.append(f"{kennung}: Zahl doppelt in 'werte'")
            gut = [n for n in werte if zahl_wort(n, weiblich)]
            for n in werte:
                if n not in gut:
                    probleme.append(f"{kennung}: kein Zahlwort für {n!r}")
            for form in _zahl_formen(satz):
                anzahl = zahl_zaehlen(form, wort)
                if anzahl != 1:
                    probleme.append(f"{kennung}: '{wort}' steht {anzahl}-mal in '{form}', erlaubt ist genau einmal")
            if frei is None:
                klassen = sorted({zahl_klasse(n) for n in gut + ([heute] if heute is not None else [])})
                if len(klassen) > 1:
                    probleme.append(f"{kennung}: Zahlen mit verschiedenen Formen des Nomens {klassen}"
                                    " - geht nur mit 'frei'")
            elif frei not in ZAHL_FREI:
                probleme.append(f"{kennung}: 'frei' ist {frei!r}, erlaubt sind {list(ZAHL_FREI)}")
            else:
                for form in _zahl_formen(satz):
                    woerter = re.findall(r"[^\W\d_]+", form.lower())
                    i = woerter.index(wort) if wort in woerter else -1
                    if frei == "uhrzeit" and (i < 1 or woerter[i - 1] != "u"):
                        probleme.append(f"{kennung}: 'frei: uhrzeit' braucht 'u' vor der Zahl: '{form}'")
                    if frei == "dana" and (i < 0 or woerter[i + 1:i + 2] != ["dana"]):
                        probleme.append(f"{kennung}: 'frei: dana' braucht 'dana' nach der Zahl: '{form}'")
            de = z.get("de")
            if not isinstance(de, str) or not de.strip():
                probleme.append(f"{kennung}: 'de' fehlt")
                continue
            platz = de.count("{n}") + de.count("{lok}")
            if platz != 1:
                probleme.append(f"{kennung} ({sprache}): {platz} Platzhalter in '{de}', erlaubt ist genau ein {{n}}")
            if "{lok}" in de and sprache != "tr":
                probleme.append(f"{kennung} ({sprache}): {{lok}} gibt es nur im Türkischen: '{de}'")
            rest = de.replace("{n}", "").replace("{lok}", "")
            if "{" in rest or "}" in rest or re.search(r"\d", rest):
                probleme.append(f"{kennung} ({sprache}): Ziffer oder fremder Platzhalter in '{de}'")
            # „at 14 o'clock“ sagt man nicht - o'clock nur bis 12.
            if sprache == "en" and "o'clock" in de and gut and max(gut) > 12:
                probleme.append(f"{kennung} (en): o'clock nur bis 12: '{de}'")
    return probleme


def maskottchen_bilder(ordner=None):
    """Bilder in web/maskottchen: zmaj-frei.png (normal), optional zmaj-jubel.png,
    zmaj-traurig.png. Fehlen sie, zeichnet die App den Drachen als Vektor.

    Seit dem 15.10.2026 (Bild-Drache) dazu je vollstaendigem Hautsatz ein
    Eintrag "haut/<farbe>/": die App laedt die Bilder einer Hautfarbe nur,
    wenn er in der Liste steht. Vollstaendig heisst: jedes Teil aus teile/
    liegt auch in haut/<farbe>/ - ein halber Satz liesse Teile des Drachen
    leer, dann lieber die Grundfarbe."""
    ordner = ordner or os.path.join(WEB_ORDNER, "maskottchen")
    try:
        dateien = sorted(f for f in os.listdir(ordner) if f.lower().endswith((".png", ".webp", ".jpg", ".jpeg", ".gif", ".json", ".riv")))
    except OSError:
        return []
    try:
        teile = {f for f in os.listdir(os.path.join(ordner, "teile")) if f.endswith(".webp")}
        haut = os.path.join(ordner, "haut")
        farben = sorted(f for f in os.listdir(haut) if os.path.isdir(os.path.join(haut, f)) and not f.startswith("_"))
    except OSError:
        return dateien
    return dateien + ["haut/%s/" % f for f in farben
                      if teile and teile <= set(os.listdir(os.path.join(haut, f)))]


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

    # Sätze zum Bauen aus Kacheln (13.10.2026). Was hier durchrutscht, sieht
    # der Lernende als Aufgabe, die er nicht lösen kann: eine Variante mit
    # einem Wort, für das es keine Kachel gibt, oder "..." als Kachel.
    satzbau_gesehen = set()
    for satz in daten.get("satzbau", []):
        bs = str(satz.get("bs", "") or "")
        kennung = f"Satzbau [{satz.get('kat')}] '{bs}'"
        if satz.get("kat") not in ids:
            probleme.append(f"{kennung}: unbekanntes Level")
        if not bs.strip():
            probleme.append(f"Satzbau ohne 'bs': {satz}")
            continue
        if not str(satz.get("de", "") or "").strip():
            probleme.append(f"{kennung}: 'de' fehlt")
        if "..." in bs or "…" in bs or " / " in bs:
            probleme.append(f"{kennung}: enthält '...' oder ' / '")
        kacheln = satz_kacheln(bs)
        if not 2 <= len(kacheln) <= 8:
            probleme.append(f"{kennung}: {len(kacheln)} Kacheln, erlaubt sind 2 bis 8")
        for variante in satz.get("auch", []) or []:
            rest = list(kacheln)
            fehlt = []
            for wort in satz_kacheln(variante):
                if wort in rest:
                    rest.remove(wort)
                else:
                    fehlt.append(wort)
            if fehlt:
                probleme.append(f"{kennung}: Variante '{variante}' braucht Kacheln, die es nicht gibt: {fehlt}")
            if satz_kacheln(variante) == kacheln:
                probleme.append(f"{kennung}: Variante '{variante}' ist derselbe Satz")
        # ohne (14.10.2026): je ein Wort, das nie als falsche Kachel kommt.
        # Steht es selbst im Satz, ist der Eintrag ein Irrtum - die Kacheln des
        # Satzes sind ohnehin nie Ablenker. Mehr als ein Wort sperrt nichts,
        # denn Ablenker sind immer einzelne Wörter.
        ohne = satz.get("ohne", [])
        if not isinstance(ohne, list):
            probleme.append(f"{kennung}: 'ohne' ist keine Liste")
            ohne = []
        for wort in ohne:
            teile = satz_kacheln(wort) if isinstance(wort, str) else []
            if len(teile) != 1:
                probleme.append(f"{kennung}: 'ohne' braucht einzelne Wörter, nicht {wort!r}")
            elif teile[0] in kacheln:
                probleme.append(f"{kennung}: 'ohne' nennt '{wort}', das im Satz steht")
        schluessel = " ".join(kacheln)
        if schluessel in satzbau_gesehen:
            probleme.append(f"{kennung}: doppelt")
        satzbau_gesehen.add(schluessel)

    # Sätze, deren Zahl wechselt (25.10.2026)
    probleme += pruefe_zahlen(daten)

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
