# -*- coding: utf-8 -*-
"""web/index.html in Dateien unter web/js und web/css teilen - und zurueck.

Plan: Release/Aufteilung/PLAN.md, Abschnitt 2 und die Gegenpruefung (G1, G4,
G7, G8, G9). Ajdin am 20.11.2026: "am besten ist es das du die app jetzt
aufteilst damit es effizienter wird".

    aufteilen.py                 schneiden (web/index.html -> web/js, web/css)
    aufteilen.py --pruefen       alles pruefen und die Tabelle zeigen, nichts schreiben
    aufteilen.py --karte [TSV]   dazu die Zeilenkarte "alte Zeile -> Datei:Zeile"
                                 (Standard: ../Release/Aufteilung/zeilenkarte_<commit>.tsv);
                                 geht auch mit --pruefen, die Karte liegt ausserhalb von web/
    aufteilen.py --zusammen      der Rueckweg: wieder EINE index.html (= app_quelle.lesen())
    --web ORDNER                 ein anderer web-Ordner (Probe, Tests)
    --vorwaerts JS, --typescript ORDNER   Werkzeug und Parser fuer die Vorwaerts-Pruefung

Geschnitten wird an Ankerzeilen (SCHNITTE_JS, SCHNITTE_CSS): je eine ganze
Zeile, mit Einrueckung, ohne Zeilenende. Jede muss im Block genau einmal
stehen, sonst bricht das Skript ab, ohne etwas zu schreiben. Zeilennummern
stehen bewusst nirgends: die verschieben sich mit jeder Aenderung.

Die Bloecke: der Stil zwischen der Zeile "<style>" und "</style>" (nicht
festStil) und das grosse Inline-<script>, dessen letzte Anweisung "init();"
ist. Teil 1 beginnt in der Zeile nach dem Tag, der letzte endet in der Zeile
vor dem schliessenden Tag, lueckenlos. An ihre Stelle treten die
<link>- bzw. <script src>-Zeilen, mit dem Zeilenende der Datei.

Bevor web/ angefasst wird, entsteht alles einmal in einem Zwischenordner und
wird dort geprueft:
  - app_quelle.lesen() gibt Byte fuer Byte die alte index.html zurueck (2.3),
  - die Teile hintereinander sind genau der alte Block,
  - jede js-Datei besteht fuer sich "node --check" (G4),
  - jeder Teil ausser start.js endet mit seiner Zaehlzeile, und
    TEILE_ERWARTET stimmt (G7),
  - Dateinamen: nur a-z und _, kein "vorfuehrung", nichts, was app_bauen.py
    beim Kopieren weglaesst (G8),
  - in den CSS-Teilen bekommt jede relative url( ein ../ (G1), und
    app_quelle.css_zurueck() macht das genau rueckgaengig,
  - die Vorwaerts-Pruefung (PLAN 2.4, ../werkzeuge/aufteilung/vorwaerts.js
    mit dem TypeScript-Parser der Huelle): keine Anweisung braucht beim
    Laden etwas aus einer spaeteren Datei (ausser den bekannten, siehe
    VORWAERTS_BEKANNT), und kein Name steht doppelt. Fehlen Werkzeug oder
    Parser, wird sie mit einem Hinweis uebersprungen.
Nach dem Schreiben wird die Byte-Probe an web/ wiederholt; schlaegt sie fehl,
stellt das Skript den alten Zustand wieder her.

Mit Python ab 3.10, ohne Abhaengigkeiten. Zeilenenden bleiben, wie sie sind
(Windows-Arbeitskopie CRLF, CI LF).
"""
import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

WURZEL = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WURZEL)
import app_quelle  # noqa: E402
import huelle  # noqa: E402

WEB = os.path.join(WURZEL, "web")
VORWAERTS_JS = os.path.join(os.path.dirname(WURZEL), "werkzeuge", "aufteilung", "vorwaerts.js")
# Der Parser aus der Android-Huelle (../zmaj-android, oder ZMAJ_HUELLE, siehe huelle.py)
TYPESCRIPT = os.path.join(huelle.ordner(), "node_modules", "typescript")
KARTE_ORDNER = os.path.join(os.path.dirname(WURZEL), "Release", "Aufteilung")

# Ladereihenfolge = Reihenfolge im Text. Anker = die erste Zeile der Datei.
SCHNITTE_JS = [
    ("grundwerte", "/* Der Inhalt kommt aus vokabeln.py, grammatik.py und geschichten.py \u2013 hier muss nichts "
                   "ge\u00e4ndert werden. */"),
    ("werbung", "/* =================== WERBUNG ==================="),
    ("sprache", "/* ---------------- Sprache ----------------"),
    ("zustand", "/* ---- Fundament f\u00fcr die Wegmarken (19.09.2026) ----"),
    ("stufen", "/* ---- Stufen-Reiter (13.11.2026) ----"),
    ("pruefen", "/* ---------- Gesprochenes vergleichen ----------"),
    ("drache", "/* ---- Maskottchen Zmaj (Drache, wie die Nationalelf \u201eZmajevi\u201c) ---- */"),
    ("geraet", "/* ---- Einstellungen: T\u00f6ne, Vibration, Animationen ---- */"),
    ("stand", "/* ---- Fortschritt: mit dem Python-Server abgleichen ---- */"),
    ("vollversion", "/* ---- Die Vollversion ----"),
    ("erfolge", "/* ---- Wegmarken ----"),
    ("tag", "/* ---- Lernzeit ----"),
    ("ton", "/* ---- Sprachausgabe: eigene Aufnahme (web/audio) vor Computerstimme ---- */"),
    ("ton_abspielen", "/* ---- Wann das Wort kommt (22.10.2026) ----"),
    ("inhalt", "/* =================== SPRACHE =================== */"),
    ("abo", "/* ===================== Die Vollversion als Abo ====================="),
    ("anmeldung_server", "/* =================== ANMELDUNG =================== */"),
    ("einstellungen", "/* =================== EINSTELLUNGEN =================== */"),
    ("laden", "/* ---- Laden ----"),
    ("konto_sicherung", "/* ---- Passwort \u00e4ndern ---- */"),
    ("cloud_stand", "/* =================== CLOUD-SICHERUNG UND ANMELDUNG ==================="),
    ("cloud_adapter", "/* ---- Die Huelle: Plugin ZmajAnmeldung ----"),
    ("cloud_seiten", "/* ---- Das Tor: ohne Anmeldung geht es nach der 1. Lektion nicht weiter ----"),
    ("feedback", "/* ===== Zmaj bewerten und empfehlen (Einstellungen, Ueber die App) ====="),
    ("startseite", "/* =================== STARTSEITE =================== */"),
    ("geschichten", "/* =================== GESCHICHTEN-PFAD =================== */"),
    ("level", "/* =================== LEVEL =================== */"),
    ("aufgaben", "/* =================== AUFGABEN-BAUSTEINE =================== */"),
    ("lektion", "/* =================== LEKTION =================== */"),
    ("pruefungen", "/* =================== LEVEL-TEST =================== */"),
    ("wiederholen", "/* =================== WIEDERHOLEN ==================="),
    ("bewertung", "/* =================== BEWERTUNG ==================="),
    ("benachrichtigung", "/* =================== BENACHRICHTIGUNGEN ==================="),
    ("updates", "/* =================== UPDATES AUS GOOGLE PLAY ==================="),
    ("start", "/* ---- Init ---- */"),
]
# Die Reihenfolge ist Pflicht (Kaskade), tablet.css zuletzt. Die Anker sind
# mit zwei Leerzeichen eingerueckt (G9).
SCHNITTE_CSS = [
    ("grund", "  /* ---------- Farben: bosnische Flagge (Blau, Gelb, Wei\u00df) ---------- */"),
    ("kopf", "  /* ---------- Kopf ---------- */"),
    ("maskottchen", "  /* ---------- Maskottchen ---------- */"),
    ("startseite", "  /* ---------- Startseite ---------- */"),
    ("aufgaben_erfolge", "  /* ---------- Tagesaufgaben ---------- */"),
    ("laden", "  /* ---------- Laden ---------- */"),
    ("sektion", "  /* ---- Die ganze App traegt die Farbe der laufenden Sektion ----"),
    ("vollversion", "  /* ---- Update aus Google Play (10.10.2026) ----"),
    ("wiederholen", "  /* ---- Einstufung und Wiederholen ----"),
    ("wegmarke_leben", "  /* ---- Wegmarke ----"),
    ("level", "  /* ---------- Level ---------- */"),
    ("einstellungen", "  /* ---------- Einstellungen ---------- */"),
    ("tablet", "  /* ---------- Tablets (30.10.2026) ----------"),
]

# Zaehlzeile am Ende jedes Teils ausser dem letzten (G7, Commit c).
ZAEHLER = "var teileDa = (teileDa || 0) + 1;"
TEILE_ERWARTET = re.compile(r"^const TEILE_ERWARTET = (\d+);\r?$", re.M)
# Nur Kleinbuchstaben und _ dazwischen: keine Ziffern (PLAN 1.5), kein _ am
# Anfang (app_bauen RAUS_PRAEFIX), keine Grossbuchstaben (G8). Die Regel steht
# in app_quelle.NAME, damit Werkzeug, Leser und Tests dieselbe haben.
NAME = re.compile(app_quelle.NAME)

# Was die Vorwaerts-Pruefung heute findet und warum es bleibt (PLAN 2.4):
# (Datei, Anfang der Anweisung, gebrauchter Name).
VORWAERTS_BEKANNT = {
    # applyAnim() greift auf VIEWS (inhalt.js) nur in einem try zu.
    ("geraet", "applyAnim();", "VIEWS"),
}


class Abbruch(Exception):
    """Etwas stimmt nicht; es wurde nichts (mehr) geschrieben."""


# ---------------------------------------------------------------------------
# Lesen und Planen (schreibt nichts)
# ---------------------------------------------------------------------------
def _lesen(pfad):
    with io.open(pfad, encoding="utf-8", newline="") as f:
        return f.read()


def _schreiben(pfad, text):
    with io.open(pfad, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def _roh(zeile):
    return zeile.rstrip("\r\n")


def _ende(zeile):
    return zeile[len(_roh(zeile)):]


class Teil:
    def __init__(self, art, name, an, ab, text):
        self.art = art            # "css" oder "js"
        self.name = name
        self.an = an              # erste Zeile (Index in den alten Zeilen)
        self.ab = ab              # erste Zeile danach
        self.text = text          # Inhalt der Datei (CSS schon mit ../)

    @property
    def pfad(self):
        return "%s/%s.%s" % (self.art, self.name, self.art)

    @property
    def zeile(self):
        if self.art == "css":
            return '<link rel="stylesheet" href="%s">' % self.pfad
        return '<script src="%s"></script>' % self.pfad


class Plan:
    def __init__(self, alt, zeilen, stil, skript, teile, neu, herkunft):
        self.alt = alt            # index.html vorher (ganzer Text)
        self.zeilen = zeilen      # die alten Zeilen, mit Zeilenende
        self.stil = stil          # (Index "<style>", Index "</style>")
        self.skript = skript      # (Index "<script>", Index "</script>")
        self.teile = teile        # [Teil], erst CSS, dann JS
        self.neu = neu            # index.html danach
        self.herkunft = herkunft  # je alte Zeile: (Datei, Zeile ab 1)

    def dateien(self):
        return ["index.html"] + [t.pfad for t in self.teile]


def zeilenende_pruefen(text):
    crlf, lf = text.count("\r\n"), text.count("\n")
    if crlf not in (0, lf):
        raise Abbruch("index.html hat gemischte Zeilenenden (%d CRLF, %d LF)" % (crlf, lf - crlf))
    if "\r" in text.replace("\r\n", ""):
        raise Abbruch("index.html hat einzelne CR")


def namen_pruefen(schnitte, art):
    """G8 und PLAN 1.5. Dazu der Filter von app_bauen.kopieren(): was er
    weglaesst, fehlte auf dem Handy."""
    gesehen = set()
    raus = _raus_filter()
    for name, _anker in schnitte:
        datei = "%s.%s" % (name, art)
        if not NAME.fullmatch(name):
            raise Abbruch("Dateiname %s: nur a-z und _ dazwischen" % datei)
        if "vorfuehrung" in name:
            raise Abbruch("Dateiname %s: kein 'vorfuehrung' (keine_vorfuehrung() in app_bauen.py)" % datei)
        if name in gesehen:
            raise Abbruch("Dateiname %s steht zweimal" % datei)
        if raus and raus(datei):
            raise Abbruch("Dateiname %s: app_bauen.kopieren() liesse die Datei weg" % datei)
        gesehen.add(name)


def _raus_filter():
    """Die Bedingung aus app_bauen.kopieren() mit dessen RAUS_*-Werten."""
    try:
        import app_bauen
    except Exception:   # z. B. ohne Huelle in einer fremden Kopie; der Test prueft es mit kopieren()
        return None

    def raus(n):
        klein = n.lower()
        return (klein in app_bauen.RAUS_DATEIEN or klein.endswith(app_bauen.RAUS_ENDUNGEN)
                or klein.startswith(app_bauen.RAUS_PRAEFIX)
                or any(s in klein for s in app_bauen.RAUS_ENTHAELT))
    return raus


def bloecke(zeilen):
    """(Stil-Anfang, Stil-Ende), (Skript-Anfang, Skript-Ende) als Indizes der Tag-Zeilen."""
    roh = [_roh(z) for z in zeilen]
    stil = [i for i, z in enumerate(roh) if z == "<style>"]
    if len(stil) != 1:
        raise Abbruch("die Zeile <style> steht %d-mal in index.html statt einmal" % len(stil))
    try:
        stil_ab = roh.index("</style>", stil[0] + 1)
    except ValueError:
        raise Abbruch("<style> ohne </style>") from None
    kandidaten = []
    for i, z in enumerate(roh):
        if z != "<script>":
            continue
        try:
            ab = roh.index("</script>", i + 1)
        except ValueError:
            raise Abbruch("<script> in Zeile %d ohne </script>" % (i + 1)) from None
        letzte = [k for k in range(i + 1, ab) if roh[k].strip()]
        if letzte and roh[letzte[-1]] == "init();":
            kandidaten.append((i, ab))
    if len(kandidaten) != 1:
        raise Abbruch("das Inline-<script> mit init(); am Ende steht %d-mal statt einmal" % len(kandidaten))
    if not stil_ab < kandidaten[0][0]:
        raise Abbruch("der Stil steht nicht vor dem Skript")
    return (stil[0], stil_ab), kandidaten[0]


def _grenzen(zeilen, an, ab, schnitte, block):
    roh = [_roh(z) for z in zeilen]
    starts = []
    for name, anker in schnitte:
        treffer = [i for i in range(an + 1, ab) if roh[i] == anker]
        if len(treffer) != 1:
            raise Abbruch("Anker fuer %s steht %d-mal im %s statt einmal: %r" % (name, len(treffer), block, anker))
        starts.append(treffer[0])
    if starts[0] != an + 1:
        raise Abbruch("der erste Anker (%s) ist nicht die erste Zeile im %s" % (schnitte[0][0], block))
    if starts != sorted(starts) or len(set(starts)) != len(starts):
        raise Abbruch("die Anker im %s stehen nicht in der Reihenfolge der Tabelle" % block)
    return [(schnitte[k][0], starts[k], starts[k + 1] if k + 1 < len(starts) else ab) for k in range(len(starts))]


def planen(alt, schnitte_js=None, schnitte_css=None):
    """Den Schnitt ausrechnen, ohne etwas zu schreiben. alt: index.html vorher."""
    schnitte_js = SCHNITTE_JS if schnitte_js is None else schnitte_js
    schnitte_css = SCHNITTE_CSS if schnitte_css is None else schnitte_css
    zeilenende_pruefen(alt)
    zeilen = app_quelle._zeilen(alt)
    for z in zeilen:
        if app_quelle._teil(z):
            raise Abbruch("index.html ist schon geteilt (%s)" % _roh(z))
    namen_pruefen(schnitte_css, "css")
    namen_pruefen(schnitte_js, "js")
    stil, skript = bloecke(zeilen)

    teile = []
    for name, an, ab in _grenzen(zeilen, stil[0], stil[1], schnitte_css, "Stil"):
        roh = "".join(zeilen[an:ab])
        text = app_quelle.css_hin(roh)
        if app_quelle.css_zurueck(text) != roh:
            raise Abbruch("css/%s.css: url(...) laesst sich nicht eindeutig umschreiben (steht schon ../ darin?)" % name)
        teile.append(Teil("css", name, an, ab, text))
    js = []
    for name, an, ab in _grenzen(zeilen, skript[0], skript[1], schnitte_js, "Skript"):
        js.append(Teil("js", name, an, ab, "".join(zeilen[an:ab])))
    _zaehler_pruefen(js)
    teile += js

    if "".join(zeilen[stil[0] + 1:stil[1]]) != app_quelle.css_zurueck("".join(t.text for t in teile if t.art == "css")):
        raise Abbruch("die CSS-Teile ergeben nicht den alten Stil")
    if "".join(zeilen[skript[0] + 1:skript[1]]) != "".join(t.text for t in js):
        raise Abbruch("die JS-Teile ergeben nicht das alte Skript")

    # Neue index.html und woher jede alte Zeile kommt (fuer die Karte)
    neu, herkunft = [], [None] * len(zeilen)

    def gruppe(tag_an, tag_ab, art):
        ende = _ende(zeilen[tag_an])
        erste = len(neu) + 1
        for t in teile:
            if t.art == art:
                for k in range(t.an, t.ab):
                    herkunft[k] = (t.pfad, k - t.an + 1)
                neu.append(t.zeile + ende)
        herkunft[tag_an] = ("index.html", erste)
        herkunft[tag_ab] = ("index.html", len(neu))

    def uebernehmen(von, bis):
        for k in range(von, bis):
            neu.append(zeilen[k])
            herkunft[k] = ("index.html", len(neu))

    uebernehmen(0, stil[0])
    gruppe(stil[0], stil[1], "css")
    uebernehmen(stil[1] + 1, skript[0])
    gruppe(skript[0], skript[1], "js")
    uebernehmen(skript[1] + 1, len(zeilen))
    return Plan(alt, zeilen, stil, skript, teile, "".join(neu), herkunft)


def _zaehler_pruefen(js):
    """G7: jeder Teil vor start.js endet mit der Zaehlzeile, start.js zaehlt
    sie gegen TEILE_ERWARTET und endet mit init();."""
    for t in js[:-1]:
        letzte = [z for z in t.text.splitlines() if z.strip()]
        if not letzte or not letzte[-1].startswith(ZAEHLER):
            raise Abbruch("js/%s.js endet nicht mit der Zaehlzeile %r (G7)" % (t.name, ZAEHLER))
    start = js[-1].text
    if ZAEHLER in start:
        raise Abbruch("js/%s.js (der letzte Teil) hat eine Zaehlzeile" % js[-1].name)
    m = TEILE_ERWARTET.findall(start)
    if len(m) != 1 or int(m[0]) != len(js) - 1:
        raise Abbruch("TEILE_ERWARTET in js/%s.js ist %s, es gibt aber %d Teile davor"
                      % (js[-1].name, m or "nicht da", len(js) - 1))


# ---------------------------------------------------------------------------
# Proben an einem Ordner
# ---------------------------------------------------------------------------
def _teile_schreiben(web, plan):
    for art in ("css", "js"):
        os.makedirs(os.path.join(web, art), exist_ok=True)
    for t in plan.teile:
        _schreiben(os.path.join(web, t.art, t.name + "." + t.art), t.text)


def gleichheit_pruefen(web, plan):
    """PLAN 2.3: lesen() == alte index.html, Byte fuer Byte; die Liste der Dateien stimmt."""
    if app_quelle.lesen(web).encode("utf-8") != plan.alt.encode("utf-8"):
        raise Abbruch("app_quelle.lesen() gibt nicht die alte index.html zurueck")
    if app_quelle.dateien(web) != plan.dateien():
        raise Abbruch("app_quelle.dateien() liefert eine andere Liste: %s" % app_quelle.dateien(web))


def node_finden():
    return shutil.which("node")


def node_pruefen(web, plan, node):
    """G4: jede js-Datei fuer sich. Eine, die allein nicht parst, fiele im Browser ganz aus."""
    for t in plan.teile:
        if t.art != "js":
            continue
        r = subprocess.run([node, "--check", os.path.join(web, t.art, t.name + ".js")],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode:
            raise Abbruch("node --check %s:\n%s" % (t.pfad, r.stdout.decode("utf-8", "replace")[:800]))


def vorwaerts_pruefen(web, plan, node, werkzeug=VORWAERTS_JS, typescript=TYPESCRIPT):
    """PLAN 2.4. Gibt (Meldungen, Hinweise) zurueck; bricht bei neuen Stellen ab."""
    fehlt = [p for p in (werkzeug, typescript) if not os.path.exists(p)]
    if not node or fehlt:
        return [], ["Vorwaerts-Pruefung uebersprungen: fehlt %s" % (", ".join(fehlt) or "node")]
    dateien = [os.path.join(web, t.art, t.name + ".js") for t in plan.teile if t.art == "js"]
    r = subprocess.run([node, werkzeug, typescript] + dateien, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        raise Abbruch("vorwaerts.js: %s" % r.stderr.decode("utf-8", "replace")[:800])
    erg = json.loads(r.stdout.decode("utf-8"))
    if erg.get("fehler"):
        raise Abbruch("vorwaerts.js: %s" % erg["fehler"])
    if erg["doppelt"]:
        raise Abbruch("doppelte Namen auf oberster Ebene: %s" % erg["doppelt"][:10])
    neu, bekannt = [], []
    for v in erg["vorwaerts"]:
        for wer in v["braucht"]:
            name = wer.split("@")[0]
            if any(v["datei"] == d and v["text"].startswith(a) and name == n for d, a, n in VORWAERTS_BEKANNT):
                bekannt.append("bekannt: js/%s.js:%d %s braucht %s" % (v["datei"], v["zeile"], v["text"][:40], name))
            else:
                neu.append("js/%s.js:%d %s  ->  %s" % (v["datei"], v["zeile"], v["text"], wer))
    if neu:
        raise Abbruch("Vorwaerts-Verweise beim Laden (PLAN 2.4):\n  " + "\n  ".join(neu))
    hinweise = bekannt + ["%d Namen; %d beim Laden angemeldete Horcher/Zeitgeber erreichen spaeter Code aus "
                          "spaeteren Dateien (zur Info: sie laufen erst nach einer Aufgabe; die frueh feuernden "
                          "warten auf skripteDa, PLAN 4/G3)" % (erg["deklarationen"], len(erg["angestossen"]))]
    return erg["angestossen"], hinweise


def proben(plan, mit_node=True, mit_vorwaerts=True, werkzeug=VORWAERTS_JS, typescript=TYPESCRIPT):
    """Alles in einem Zwischenordner aufbauen und pruefen. Gibt die Hinweise zurueck."""
    hinweise = []
    tmp = tempfile.mkdtemp(prefix="aufteilen_")
    try:
        _schreiben(os.path.join(tmp, "index.html"), plan.neu)
        _teile_schreiben(tmp, plan)
        gleichheit_pruefen(tmp, plan)
        node = node_finden()
        if mit_node:
            if not node:
                raise Abbruch("node fehlt: jede js-Datei muss 'node --check' bestehen (G4)")
            node_pruefen(tmp, plan, node)
        if mit_vorwaerts:
            hinweise += vorwaerts_pruefen(tmp, plan, node, werkzeug, typescript)[1]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return hinweise


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------
def tabelle(plan):
    aus = ["  #  Datei                       Zeilen (alt)      KB"]
    nr = {"css": 0, "js": 0}
    for t in plan.teile:
        nr[t.art] += 1
        aus.append("%3d  %-26s %6d-%-6d %7.1f" % (nr[t.art], t.pfad, t.an + 1, t.ab, len(t.text.encode("utf-8")) / 1024.0))
    groessen = sorted(len(t.text.encode("utf-8")) for t in plan.teile if t.art == "js")
    aus.append("%d CSS, %d JS; index.html %.1f KB -> %.1f KB; JS Median %.1f KB, groesste %.1f KB" % (
        nr["css"], nr["js"], len(plan.alt.encode("utf-8")) / 1024.0, len(plan.neu.encode("utf-8")) / 1024.0,
        groessen[len(groessen) // 2] / 1024.0, groessen[-1] / 1024.0))
    return "\n".join(aus)


def karte_text(plan):
    """TSV: alte Zeile (ab 1), Datei (relativ zu web/), Zeile darin (ab 1).
    Die Tag-Zeilen <style>/</style>/<script>/</script> zeigen auf die erste
    bzw. letzte Link-/Script-Zeile in der neuen index.html."""
    aus = ["alte_zeile\tdatei\tzeile"]
    for k, (datei, zeile) in enumerate(plan.herkunft):
        aus.append("%d\t%s\t%d" % (k + 1, datei, zeile))
    return "\n".join(aus) + "\n"


def _commit(web):
    try:
        kurz = subprocess.run(["git", "-C", web, "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL).stdout.decode().strip()
        offen = subprocess.run(["git", "-C", web, "status", "--porcelain", "--", "index.html"],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode().strip()
    except OSError:
        return "ohne_git"
    return (kurz or "ohne_git") + ("_geaendert" if offen else "")


# ---------------------------------------------------------------------------
# Schneiden und Zusammensetzen
# ---------------------------------------------------------------------------
def _ordner_leer_oder_neu(web):
    for art in ("css", "js"):
        pfad = os.path.join(web, art)
        if os.path.exists(pfad) and os.listdir(pfad):
            raise Abbruch("web/%s/ gibt es schon und ist nicht leer: %s" % (art, sorted(os.listdir(pfad))[:5]))


def _aufraeumen(web, plan):
    for t in plan.teile:
        pfad = os.path.join(web, t.art, t.name + "." + t.art)
        if os.path.exists(pfad):
            os.remove(pfad)
    for art in ("css", "js"):
        pfad = os.path.join(web, art)
        if os.path.isdir(pfad) and not os.listdir(pfad):
            os.rmdir(pfad)


def schneiden(web=WEB, pruefen=False, karte=None, mit_node=True, mit_vorwaerts=True, ausgabe=print,
              werkzeug=VORWAERTS_JS, typescript=TYPESCRIPT):
    pfad = os.path.join(web, "index.html")
    alt = _lesen(pfad)
    plan = planen(alt)
    _ordner_leer_oder_neu(web)
    for h in proben(plan, mit_node, mit_vorwaerts, werkzeug, typescript):
        ausgabe(h)
    ausgabe(tabelle(plan))
    if karte:
        os.makedirs(os.path.dirname(os.path.abspath(karte)), exist_ok=True)
        with io.open(karte, "w", encoding="utf-8", newline="") as f:
            f.write(karte_text(plan))
        ausgabe("Zeilenkarte: %s" % karte)
    if pruefen:
        ausgabe("nur geprueft, nichts geschrieben (Byte-Probe im Zwischenordner: gleich)")
        return plan
    try:
        _teile_schreiben(web, plan)
        _schreiben(pfad, plan.neu)
        gleichheit_pruefen(web, plan)
    except BaseException:
        _schreiben(pfad, alt)
        _aufraeumen(web, plan)
        raise
    ausgabe("geteilt: %d Dateien, app_quelle.lesen() == alte index.html (Byte fuer Byte)" % len(plan.teile))
    return plan


def zusammen(web=WEB, pruefen=False, ausgabe=print):
    """Der Rueckweg (PLAN 7): aus den Teilen wieder genau eine index.html."""
    pfad = os.path.join(web, "index.html")
    teile = app_quelle.dateien(web)[1:]
    if not teile:
        raise Abbruch("index.html ist nicht geteilt")
    for art in ("css", "js"):
        ordner = os.path.join(web, art)
        da = sorted(os.listdir(ordner)) if os.path.isdir(ordner) else []
        geladen = sorted(t.split("/", 1)[1] for t in teile if t.startswith(art + "/"))
        if da != geladen:
            raise Abbruch("web/%s/ enthaelt andere Dateien, als index.html laedt: %s"
                          % (art, sorted(set(da) ^ set(geladen))))
    ganz = app_quelle.lesen(web)
    zeilenende_pruefen(ganz)
    if any(app_quelle._teil(z) for z in app_quelle._zeilen(ganz)):
        raise Abbruch("zusammengesetzt laedt index.html immer noch Teile")
    ausgabe("%d Teile -> eine index.html mit %.1f KB" % (len(teile), len(ganz.encode("utf-8")) / 1024.0))
    if pruefen:
        ausgabe("nur geprueft, nichts geschrieben")
        return ganz
    alt = _lesen(pfad)
    _schreiben(pfad, ganz)
    if _lesen(pfad) != ganz:
        _schreiben(pfad, alt)
        raise Abbruch("index.html liess sich nicht schreiben, alter Zustand wiederhergestellt")
    for t in teile:
        os.remove(os.path.join(web, t))
    for art in ("css", "js"):
        ordner = os.path.join(web, art)
        if os.path.isdir(ordner) and not os.listdir(ordner):
            os.rmdir(ordner)
    ausgabe("zusammengesetzt, js/ und css/ entfernt")
    return ganz


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    p = argparse.ArgumentParser(description="web/index.html in web/js und web/css teilen (PLAN.md 2.1)")
    p.add_argument("--web", default=WEB, help="der web-Ordner (Standard: web/ neben diesem Skript)")
    p.add_argument("--pruefen", action="store_true", help="nur pruefen und zeigen, nichts in web/ schreiben")
    p.add_argument("--karte", nargs="?", const="", default=None,
                   help="Zeilenkarte als TSV schreiben (Standard: ../Release/Aufteilung/zeilenkarte_<commit>.tsv)")
    p.add_argument("--zusammen", action="store_true", help="der Rueckweg: wieder eine index.html")
    p.add_argument("--vorwaerts", default=VORWAERTS_JS, help="vorwaerts.js (Standard: %(default)s)")
    p.add_argument("--typescript", default=TYPESCRIPT, help="TypeScript-Modulordner (Standard: %(default)s)")
    a = p.parse_args(argv)
    web = os.path.abspath(a.web)
    try:
        if a.zusammen:
            if a.karte is not None:
                raise Abbruch("--karte geht nur beim Schneiden")
            zusammen(web, a.pruefen)
            return 0
        karte = a.karte
        if karte == "":
            if not os.path.isdir(KARTE_ORDNER):
                raise Abbruch("%s fehlt; --karte PFAD angeben" % KARTE_ORDNER)
            karte = os.path.join(KARTE_ORDNER, "zeilenkarte_%s.tsv" % _commit(web))
        schneiden(web, a.pruefen, karte, werkzeug=a.vorwaerts, typescript=a.typescript)
    except Abbruch as e:
        print("ABBRUCH: %s" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
