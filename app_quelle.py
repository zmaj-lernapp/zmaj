# -*- coding: utf-8 -*-
"""Die App als EIN Text, auch wenn web/index.html in Dateien geteilt ist.

Seit 1.5 (Release/Aufteilung/PLAN.md) kann das grosse Skript in Dateien unter
web/js/ und der Stil in Dateien unter web/css/ liegen. index.html laedt sie
dann der Reihe nach mit

    <link rel="stylesheet" href="css/NAME.css">     (direkt hintereinander)
    <script src="js/NAME.js"></script>              (direkt hintereinander)

lesen(web) setzt die Teile wieder ein: die Links als EIN <style>...</style>,
die Skripte als EIN <script>...</script>, mit den alten Tag-Zeilen. Heraus
kommt Byte fuer Byte die index.html von vor dem Schnitt. Darum lesen Tests
und Werkzeuge (texte_pruefen.py, store/bilder_machen) die App ueber diese
Funktion und nicht direkt aus der Datei. Ist nichts geteilt, gibt lesen()
index.html unveraendert zurueck.

Erfasst werden nur css/... und js/... - nicht schriften.css, nicht
lottie.min.js, und nicht der Bauwerte-Block (der bleibt inline in
index.html, siehe dort).

Eine Datei unter css/ loest url(...) gegen css/ auf, nicht gegen web/. Darum
stellt der Schnitt jeder relativen Adresse im Stil ein "../" voran
(css_hin), und lesen() nimmt es wieder zurueck (css_zurueck). Adressen mit
#, data:, http(s): oder / bleiben, wie sie sind (Gegenpruefung G1).

Laeuft mit Python ab 3.10 und ohne Abhaengigkeiten.
"""
import io
import os
import re

STIL_ZEILE = re.compile(r'<link rel="stylesheet" href="(css/[a-z0-9_]+\.css)">')
SKRIPT_ZEILE = re.compile(r'<script src="(js/[a-z0-9_]+\.js)"></script>')

# Relative Adressen im Stil: nicht #..., data:, http(s):, /... und nicht
# schon ../ (dann waere der Rueckweg nicht eindeutig).
_URL_HIN = re.compile(r"""url\((['"]?)(?!#|data:|https?:|/|\.\./)""")
_URL_ZURUECK = re.compile(r"""url\((['"]?)\.\./""")


def _datei(web, name):
    with io.open(os.path.join(web, name), encoding="utf-8", newline="") as f:
        return f.read()


def _zeilen(text):
    """Die Zeilen samt ihrem Zeilenende (CRLF in der Windows-Arbeitskopie,
    LF in CI). Nicht splitlines(): das trennt auch an Zeichen wie U+2028."""
    return [z for z in re.split(r"(?<=\n)", text) if z]


def _teil(zeile):
    """("css"|"js", Pfad), wenn die Zeile einen Teil laedt, sonst None."""
    z = zeile.rstrip("\r\n")
    m = STIL_ZEILE.fullmatch(z)
    if m:
        return "css", m.group(1)
    m = SKRIPT_ZEILE.fullmatch(z)
    if m:
        return "js", m.group(1)
    return None


def css_hin(stil):
    """Fuer eine Datei unter css/: jeder relativen url( ein ../ voran."""
    return _URL_HIN.sub(lambda m: "url(" + m.group(1) + "../", stil)


def css_zurueck(stil):
    """Der Rueckweg von css_hin()."""
    return _URL_ZURUECK.sub(lambda m: "url(" + m.group(1), stil)


def lesen(web):
    """index.html mit allen Teilen an ihrer Stelle, als ein Text."""
    aus = []
    zeilen = _zeilen(_datei(web, "index.html"))
    i = 0
    while i < len(zeilen):
        art = _teil(zeilen[i])
        if art is None:
            aus.append(zeilen[i])
            i += 1
            continue
        gruppe = []
        while i < len(zeilen) and (_teil(zeilen[i]) or ("", ""))[0] == art[0]:
            gruppe.append(_teil(zeilen[i])[1])
            i += 1
        erste = zeilen[i - len(gruppe)]
        ende = erste[len(erste.rstrip("\r\n")):]
        inhalt = "".join(_datei(web, name) for name in gruppe)
        tag = "style" if art[0] == "css" else "script"
        if tag == "style":
            inhalt = css_zurueck(inhalt)
        aus.append("<%s>%s%s</%s>%s" % (tag, ende, inhalt, tag, ende))
    return "".join(aus)


BAUWERTE_ANFANG = "/* Bauwerte ("


def bauwerte(html):
    """Der Text im Bauwerte-Block von index.html (ohne die Tag-Zeilen).

    Der Block ist ein eigenes kleines <script> vor den Skripten der App, die
    erste Zeile darin beginnt mit BAUWERTE_ANFANG. Gibt es ihn nicht genau
    einmal: ValueError."""
    zeilen = _zeilen(html)
    anfaenge = [i for i in range(len(zeilen) - 1)
                if zeilen[i].rstrip("\r\n") == "<script>" and zeilen[i + 1].startswith(BAUWERTE_ANFANG)]
    if len(anfaenge) != 1:
        raise ValueError("Bauwerte-Block steht %d-mal in index.html statt einmal" % len(anfaenge))
    erste = anfaenge[0] + 1
    for j in range(erste, len(zeilen)):
        if zeilen[j].rstrip("\r\n") == "</script>":
            return "".join(zeilen[erste:j])
    raise ValueError("Bauwerte-Block ohne </script>")


def dateien(web):
    """index.html und die Teile in Ladereihenfolge, Pfade relativ zu web/."""
    liste = ["index.html"]
    for zeile in _zeilen(_datei(web, "index.html")):
        art = _teil(zeile)
        if art:
            liste.append(art[1])
    return liste
