# -*- coding: utf-8 -*-
r"""Barrierefreiheit: Schalter mit Namen, lesbarer grauer und farbiger Text, ein Hauptbereich.

GEFUNDEN BEI DER AXE-MESSUNG am 04.10.2026 (axe-core 4.13, Chromium,
390 x 844, Englisch und Deutsch, hell und dunkel, Sektion 1, 4 und 8).
Bericht: "Zmaj Berichte/barrierefreiheit-2026-10-04.md".

WAS AXE GEFUNDEN HAT (nur ernst und kritisch)

  1. button-name, kritisch. Die Schalter in den Einstellungen (Toene,
     Vibration, Animationen, Werbung, Vollversion, die drei Benachrichtigungen)
     sind leere <button role="switch">. Die Ueberschrift steht daneben in
     einem <div class="st">, ist aber nicht mit dem Schalter verbunden.
     TalkBack sagt nur "Schalter, an" - wofuer, erfaehrt man nicht.
  2. color-contrast, ernst. Grauer Text (--muted) steht an vielen Stellen
     nicht auf der hellen Flaeche, sondern direkt auf dem farbigen Grund:
     Lernserie, Fortschritt im Level ("16 von 19 Woertern"), Fusszeile.
     Dort 3,7:1 in Sektion 1 und nur 3,0:1 in Sektion 4 und 8 - gefordert
     sind 4,5:1. In der hellen Fassung liegt jedes --sekN-matt zu hell.
  3. color-contrast, ernst. Farbiger Text in Gruen, Rot und Gelb:
     "Richtig! ✓" nach einer Antwort 3,2:1, "Die Antwort ist: kuca" 4,1:1,
     "Jetzt dran" am Lernpfad 2,3:1, "Gelesen" 3,2:1, "KM" an den Muenzen
     1,8:1 (hell) und 3,8:1 (dunkel). Gruen, Rot und Gelb sind aber auch
     Flaechen- und Randfarben (Balken, Schalter, Knopfschatten) - dort
     gilt 3:1 und dort stimmen sie. Deshalb werden sie NICHT umgefaerbt.

WAS GEAENDERT WIRD

  zu 1: Jede Schalter-Ueberschrift bekommt eine id, der Schalter
        aria-labelledby darauf. Kein neuer Text in acht Sprachen: der
        Name ist genau die Ueberschrift, die schon sichtbar dasteht, und
        wechselt mit der Sprache mit.
  zu 2: Die neun hellen --sekN-matt und --muted werden dunkler, gleicher
        Farbton und gleiche Saettigung (HLS), nur die Helligkeit sinkt, bis
        sie auf Grund, Flaeche und sanftem Ton der eigenen Sektion
        mindestens 4,6:1 erreicht. Die dunkle Fassung erreicht das schon
        (mindestens 4,85:1) und bleibt unberuehrt.
  zu 3: Drei neue Texttoken --good-text, --bad-text, --accent-text, je in
        hell und dunkel. Sie gelten nur fuer Schrift (Rueckmeldung, Zustand
        am Lernpfad, KM, Haken). Flaechen und Raender behalten --good,
        --bad und --accent-dark. "KM" verliert dafuer opacity:.7 - die
        Abstufung macht jetzt nur noch die Schriftgroesse.

  Dazu, nur "maessig" bei axe, aber ohne Risiko: Die Ansichten stehen in
  einem <main>. Damit kann ein Bildschirmleser direkt zum Inhalt springen
  (landmark-one-main, region).

  Farbwerte, alt -> neu (Kontrast auf dem schwierigsten Grund der Sektion):
    --muted           #66698A -> #585A77   (3,70 -> 4,65)
    --sek1-matt       #66698A -> #585A77   (3,67 -> 4,62)
    --sek2-matt       #6F668A -> #564F6C   (3,22 -> 4,65)
    --sek3-matt       #7B668A -> #695776   (3,65 -> 4,65)
    --sek4-matt       #87668A -> #644C66   (2,97 -> 4,61)
    --sek5-matt       #8A6680 -> #73556B   (3,49 -> 4,62)
    --sek6-matt       #8A6674 -> #694D58   (3,06 -> 4,62)
    --sek7-matt       #597876 -> #4C6665   (3,60 -> 4,64)
    --sek8-matt       #5D767E -> #46595F   (3,05 -> 4,66)
    --sek9-matt       #647287 -> #545F71   (3,50 -> 4,63)
    --good-text   hell #188049 (statt #1E9E5A, 3,21 -> 4,63 auf jeder Flaeche)
    --bad-text    hell #D0352C (statt #D6453D, 4,09 -> 4,62)
    --accent-text hell #876A00 (statt #C99E00, 2,27 -> 4,64, auch auf --accent-soft)
    --good-text   dunkel #55CE8A (statt #4CCB84, 4,43 -> 4,60)
    --bad-text    dunkel #FF9E98 (statt #FF7A72, 3,60 -> 4,61)
    --accent-text dunkel #DFB31F (statt #D9AE1E, 4,36 -> 4,61)

WAS BEWUSST BLEIBT
  - .opt.right: gruene Schrift auf --primary-soft. Mit --good-text steigt
    sie, erreicht auf den kraeftigen Sektionsgruenden (2, 4, 6, 8) aber
    keine 4,5:1. Dafuer braeuchte es #126037 - fast schwarzgruen - oder
    einen anderen Grund fuer die richtige Antwort. Das ist eine
    Gestaltungsfrage, keine Reparatur. Die Antwort steht zusaetzlich als
    Text in der Rueckmeldung darunter, die jetzt lesbar ist.
  - .streakline .lost und .result-big.fail behalten --bad: das eine steht
    auf dem Grund (dafuer muesste Rot fast braun werden), das andere ist
    grosse Schrift, dort reichen 3:1.
  - page-has-heading-one: eine h1 pro Ansicht hiesse sichtbare neue
    Ueberschriften oder versteckte Texte in acht Sprachen.

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

Probelauf:  python barrierefreiheit_richten.py
Schreiben:  python barrierefreiheit_richten.py --schreiben
An Kopie:   python barrierefreiheit_richten.py --datei /pfad/index.html --schreiben
"""
import io
import os
import re
import sys

ORDNER = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(ORDNER, "web", "index.html")

KOMMENTAR_TOKEN = (
    "    /* Nur fuer Schrift. --good, --bad und --accent-dark sind auch Flaechen\n"
    "       und Raender, dort reichen 3:1 und dort stimmen sie. Als Schrift auf\n"
    "       der Flaeche lagen sie bei 3,2 / 4,1 / 2,3:1 statt 4,5:1 - axe am\n"
    "       04.10.2026, barrierefreiheit_richten.py. */\n")

# Gedaempfte Toene der hellen Fassung: (Token, alt, neu)
MATT = [
    ("--muted", "#66698A", "#585A77"),
    ("--sek1-matt", "#66698A", "#585A77"),
    ("--sek2-matt", "#6F668A", "#564F6C"),
    ("--sek3-matt", "#7B668A", "#695776"),
    ("--sek4-matt", "#87668A", "#644C66"),
    ("--sek5-matt", "#8A6680", "#73556B"),
    ("--sek6-matt", "#8A6674", "#694D58"),
    ("--sek7-matt", "#597876", "#4C6665"),
    ("--sek8-matt", "#5D767E", "#46595F"),
    ("--sek9-matt", "#647287", "#545F71"),
]

# (Schalter-id, id der Ueberschrift, alter Text, neuer Text)
SCHALTER = [
    ("swVoll", "lblVoll",
     '<div><div class="st" data-t="voll.sub"></div><div class="sd" id="setVollStand"></div></div>\n'
     '        <button class="switch" id="swVoll" role="switch" aria-checked="false"></button>',
     '<div><div class="st" id="lblVoll" data-t="voll.sub"></div><div class="sd" id="setVollStand"></div></div>\n'
     '        <button class="switch" id="swVoll" role="switch" aria-checked="false" aria-labelledby="lblVoll"></button>'),
]
for sw, lbl, key in (("swSound", "lblToene", "set.toene"), ("swHaptik", "lblVibration", "set.vibration"),
                     ("swAnim", "lblAnim", "set.animationen")):
    SCHALTER.append((sw, lbl,
                     '<div class="st" data-t="%s"></div><div class="sd" data-t="%s_sub"></div></div>'
                     '<button class="switch" id="%s" role="switch" aria-checked="true"></button>' % (key, key, sw),
                     '<div class="st" id="%s" data-t="%s"></div><div class="sd" data-t="%s_sub"></div></div>'
                     '<button class="switch" id="%s" role="switch" aria-checked="true" aria-labelledby="%s"></button>'
                     % (lbl, key, key, sw, lbl)))
for sw, lbl, key in (("swBenErinnerung", "lblBenErinnerung", "set.ben_erinnerung"),
                     ("swBenSerie", "lblBenSerie", "set.ben_serie"), ("swBenLeben", "lblBenLeben", "set.ben_leben")):
    SCHALTER.append((sw, lbl,
                     '<div class="st" data-t="%s"></div><div class="sd" data-t="%s_sub"></div></div>'
                     '<button class="switch" id="%s" role="switch" aria-checked="false"></button>' % (key, key, sw),
                     '<div class="st" id="%s" data-t="%s"></div><div class="sd" data-t="%s_sub"></div></div>'
                     '<button class="switch" id="%s" role="switch" aria-checked="false" aria-labelledby="%s"></button>'
                     % (lbl, key, key, sw, lbl)))
SCHALTER.append(("swWerbung", "lblWerbung",
                 '<div class="st" data-t="set.einwilligung"></div><div class="sd" id="setWerbungStand"></div></div>\n'
                 '        <button class="switch" id="swWerbung" role="switch" aria-checked="false"></button>',
                 '<div class="st" id="lblWerbung" data-t="set.einwilligung"></div><div class="sd" id="setWerbungStand"></div></div>\n'
                 '        <button class="switch" id="swWerbung" role="switch" aria-checked="false" aria-labelledby="lblWerbung"></button>'))

AENDERUNGEN = []

# ---- 1. Schalter mit Namen
for sw, lbl, alt, neu in SCHALTER:
    AENDERUNGEN.append(("Schalter %s benannt" % sw, alt, neu))

# ---- 2. Gedaempfter Text dunkler (nur hell)
for token, alt, neu in MATT:
    AENDERUNGEN.append(("%s dunkler" % token, "%s:%s;" % (token, alt), "%s:%s;" % (token, neu)))

# ---- 3. Texttoken fuer Gruen, Rot, Gelb
AENDERUNGEN += [
    ("Texttoken hell",
     "    --line:#CBCEEB; --good:#1E9E5A; --good-dark:#157A44; --bad:#D6453D; --on-primary:#FFFFFF; --on-accent:#0F1E4D;\n",
     "    --line:#CBCEEB; --good:#1E9E5A; --good-dark:#157A44; --bad:#D6453D; --on-primary:#FFFFFF; --on-accent:#0F1E4D;\n"
     + KOMMENTAR_TOKEN +
     "    --good-text:#188049; --bad-text:#D0352C; --accent-text:#876A00;\n"),
    ("Texttoken dunkel (System)",
     '    :root:not([data-theme="light"]){\n'
     "      --bg:#151728; --surface:#2C2F4E; --ink:#F2F5FF; --muted:#ADAFCD;\n",
     '    :root:not([data-theme="light"]){\n'
     "      --bg:#151728; --surface:#2C2F4E; --ink:#F2F5FF; --muted:#ADAFCD;\n"
     "      --good-text:#55CE8A; --bad-text:#FF9E98; --accent-text:#DFB31F;   /* siehe oben, 04.10.2026 */\n"),
    ("Texttoken dunkel (gewaehlt)",
     '  :root[data-theme="dark"]{\n'
     "    --bg:#151728; --surface:#2C2F4E; --ink:#F2F5FF; --muted:#ADAFCD;\n",
     '  :root[data-theme="dark"]{\n'
     "    --bg:#151728; --surface:#2C2F4E; --ink:#F2F5FF; --muted:#ADAFCD;\n"
     "    --good-text:#55CE8A; --bad-text:#FF9E98; --accent-text:#DFB31F;   /* siehe oben, 04.10.2026 */\n"),
    ("Rueckmeldung lesbar",
     "  .feedback.ok{color:var(--good)} .feedback.no{color:var(--bad)} .feedback.almost{color:var(--accent-dark)}",
     "  .feedback.ok{color:var(--good-text)} .feedback.no{color:var(--bad-text)} .feedback.almost{color:var(--accent-text)}"),
    ("Antwortknopf Schrift",
     "  .opt.right{border-color:var(--good); background:var(--primary-soft); color:var(--good); box-shadow:0 3px 0 var(--good-dark)}\n"
     "  .opt.wrong{border-color:var(--bad); color:var(--bad); box-shadow:0 3px 0 var(--bad)}",
     "  .opt.right{border-color:var(--good); background:var(--primary-soft); color:var(--good-text); box-shadow:0 3px 0 var(--good-dark)}\n"
     "  .opt.wrong{border-color:var(--bad); color:var(--bad-text); box-shadow:0 3px 0 var(--bad)}"),
    ("Zustand am Lernpfad",
     "  .node.current .state{color:var(--accent-dark)}\n  .node.done .state{color:var(--good)}",
     "  .node.current .state{color:var(--accent-text)}\n  .node.done .state{color:var(--good-text)}"),
    ("KM lesbar",
     "  .km{font-size:.78em; opacity:.7; font-weight:800; letter-spacing:.3px}",
     "  /* Ohne opacity und in --accent-text: mit .7 auf Gelb waren es 1,8:1 (hell)\n"
     "     und 3,8:1 (dunkel). Leiser als die Zahl bleibt KM durch die Groesse. */\n"
     "  .km{font-size:.78em; font-weight:800; letter-spacing:.3px; color:var(--accent-text)}"),
    ("Quest erledigt",
     "  .qalle{margin-top:6px; font-size:12px; font-weight:800; color:var(--good)}",
     "  .qalle{margin-top:6px; font-size:12px; font-weight:800; color:var(--good-text)}"),
    ("Passwortregel erfuellt",
     "  .pwregeln span.ok{color:var(--good)}",
     "  .pwregeln span.ok{color:var(--good-text)}"),
    ("Sprache gewaehlt",
     "  .sprachzeile .haken{margin-left:auto; color:var(--good)}",
     "  .sprachzeile .haken{margin-left:auto; color:var(--good-text)}"),
    ("Wortliste gewusst",
     "  .wordlist .ok{color:var(--good); font-size:12px}",
     "  .wordlist .ok{color:var(--good-text); font-size:12px}"),
    ("Sprechen erkannt",
     "heard.innerHTML = '<span style=\"color:var(--good)\">'+t('task.gehoert_ok'",
     "heard.innerHTML = '<span style=\"color:var(--good-text)\">'+t('task.gehoert_ok'"),
]

# ---- 4. Ein Hauptbereich um die Ansichten
AENDERUNGEN += [
    ("main auf",
     '  <div class="err" id="err"></div>\n',
     '  <div class="err" id="err"></div>\n'
     "  <!-- Hauptbereich, damit ein Bildschirmleser direkt zum Inhalt springen\n"
     "       kann. Kopf und Fuss stehen bewusst draussen. axe, 04.10.2026. -->\n"
     "  <main>\n"),
    ("main zu",
     '\n  <footer data-t="app.fuss"></footer>\n',
     '\n  </main>\n  <footer data-t="app.fuss"></footer>\n'),
]

KENNUNG = "--good-text:#188049"


def anwenden(html):
    """(neuer Text, Fehlerliste). Ein Fehler heisst: nichts wird geschrieben."""
    fehler = []
    neu = html
    if KENNUNG in html:
        fehler.append("schon angewendet: %s steht bereits in der Datei" % KENNUNG)
    for name, alt, ersatz in AENDERUNGEN:
        n = neu.count(alt)
        if n != 1:
            fehler.append("%s: Stelle %d-mal gefunden statt einmal" % (name, n))
            continue
        neu = neu.replace(alt, ersatz)
    if fehler:
        return neu, fehler

    # Nachkontrollen wie in den anderen *_richten.py
    for auf, zu, was in (("{", "}", "geschweifte Klammern"), ("(", ")", "runde Klammern"),
                         ("/*", "*/", "Kommentare"), ("<!--", "-->", "HTML-Kommentare"),
                         ("<main>", "</main>", "main")):
        if neu.count(auf) - neu.count(zu) != html.count(auf) - html.count(zu):
            fehler.append("%s aus dem Gleichgewicht" % was)
    # Jeder Schalter hat einen Namen, und der zeigt auf genau ein Element
    for knopf in re.findall(r'<button class="switch"[^>]*>', neu):
        m = re.search(r'aria-labelledby="([^"]+)"', knopf)
        if not m:
            fehler.append("Schalter ohne Namen: %s" % knopf)
        elif neu.count('id="%s"' % m.group(1)) != 1:
            fehler.append("aria-labelledby=%s zeigt nicht auf genau ein Element" % m.group(1))
    # Die drei Texttoken stehen in allen drei Farbbloecken
    for token in ("--good-text", "--bad-text", "--accent-text"):
        n = len(re.findall(token + r":#[0-9A-F]{6};", neu))
        if n != 3:
            fehler.append("%s steht %d-mal da statt dreimal (hell, dunkel System, dunkel gewaehlt)" % (token, n))
    # Die dunklen gedaempften Toene bleiben, wie sie sind
    if neu.count("--muted:#ADAFCD;") != html.count("--muted:#ADAFCD;"):
        fehler.append("die dunkle Fassung von --muted wurde angefasst")
    # Flaechen und Raender bleiben bei --good, --bad, --accent-dark
    for lebt in (".switch[aria-checked=\"true\"]{background:var(--good)}",
                 ".tbar i.ok{background:var(--good)}", "border-color:var(--good);"):
        if lebt not in neu:
            fehler.append("%r ist verlorengegangen" % lebt)
    return neu, fehler


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    schreiben = "--schreiben" in argv
    datei = INDEX
    if "--datei" in argv:
        datei = argv[argv.index("--datei") + 1]
    roh = io.open(datei, encoding="utf-8", newline="").read()
    # Git fuer Windows checkt mit CRLF aus. Die Anker kennen nur \n -
    # also wie in sicherung_richten.py: normalisieren, beim Schreiben zurueck.
    crlf = "\r\n" in roh
    html = roh.replace("\r\n", "\n")
    neu, fehler = anwenden(html)
    for name, _, _ in AENDERUNGEN:
        print("   %s %s" % ("✗" if any(f.startswith(name + ":") for f in fehler) else "✓", name))
    if fehler:
        print("\nABBRUCH - nichts geschrieben:")
        for f in fehler:
            print("   " + f)
        return 1
    if schreiben:
        io.open(datei, "w", encoding="utf-8", newline="").write(
            neu.replace("\n", "\r\n") if crlf else neu)
        print("\ngeschrieben: %s" % datei)
        print("Danach: app_bauen.py - aber NICHT vor dem 07.10.2026 einreichen.")
    else:
        print("\n(Probelauf. Zum Schreiben: python barrierefreiheit_richten.py --schreiben)")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
