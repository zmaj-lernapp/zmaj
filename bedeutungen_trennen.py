# -*- coding: utf-8 -*-
r"""
bedeutungen_trennen.py  –  trennt Übersetzungen, die zwei verschiedene
                           bosnische Wörter gleich aussehen lassen

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" bedeutungen_trennen.py
    ... --schreiben

WORUM ES GEHT (27.09.2026)

doppelte_bedeutung.py meldet 72 Stellen, an denen zwei bosnische Wörter in
einer Oberflächensprache dieselbe Bedeutung anzeigen. Seit dem 26.09.2026
fängt die App das ab: geschwister() in index.html kennt alle Wörter mit
derselben angezeigten Bedeutung, distractors() hält sie aus einer Auswahl
heraus, und die Schreibaufgabe nimmt jede Variante an. Es geht also nichts
kaputt – aber die Übung wird beliebig. Auf Türkisch hieß „piletina"
(Hühnerfleisch) genauso wie „kokoš" (das Huhn): „tavuk". Wer das liest, kann
nicht wissen, welches der beiden gemeint ist.

Dieses Skript trennt die Fälle, in denen die Zielsprache ein eigenes Wort
hat. Die Fälle, in denen sie keines hat, bleiben unangetastet – die stehen
unten unter BLEIBT und in bedeutung_ausnahmen.json.

GEÄNDERT WIRD NUR  INHALT[<code>]["texte"]  in uebersetzungen.py.
Der deutsche Text ist dort der Schlüssel, der Wert ist die Anzeige in der
Zielsprache. Kommt derselbe deutsche Text mehrfach im Lernstoff vor, wird er
überall ersetzt – das ist nachgesehen worden. 32 der 35 Schlüssel hängen an
genau einer Vokabel. Die drei anderen wirken zusätzlich an einer zweiten
Stelle, und zwar auf dieselben Wörter:

    „Gebühr"         auch im Wörterbuch zu den Geschichten (taksa)
    „Gebühr (Akk.)"  nur dort (taksu) – zieht mit, damit die Akkusativform
                     dasselbe Wort zeigt wie die Grundform
    „wenn / falls"   auch in der Grammatik-Tabelle zu den Nebensätzen (ako),
                     wo „hvis (betingelse)" in der Bedeutungsspalte steht

Kein Lückensatz, kein Level-Name und keine Sektion hängt daran.

NEBENBEI AUFGEFALLEN, nicht geändert: das Wörterbuch übersetzt „radnji" mit
„Laden (Lok.)", die Vokabel „radnja" aber mit „Geschäft". Dasselbe bosnische
Wort zeigt in fr deshalb einmal „magasin" und einmal „boutique (locatif)".
Das steht so in der deutschen Vorlage und müsste in vokabeln.py bzw.
geschichten.py gerichtet werden, nicht hier.

WORAN SICH DIE NEUEN TEXTE ORIENTIEREN

An den Sprachen, die dasselbe Paar längst getrennt haben. Für „Preisnachlass"
steht in sv schon „prisnedsättning (rabatt)", in nb „prisavslag", in da
„rabat (nedsat pris)", in fr „réduction (de prix)" – nur en, tr und nl
zeigten denselben Text wie für „Rabatt". Zwei neue Texte stehen sogar schon
an anderer Stelle in derselben Sprache: der tr Level-Tipp sagt „Hava durumu,
mevsimler, hayvanlar." und fr übersetzt „Laden (Lok.)" mit
„boutique (locatif)".

Unsichere Stellen sind nachgeschlagen worden, nicht geraten:
„elektrik sigortası", „kiraya veren", „vücut ateşi" und „Sağlığınıza!" für
Türkisch, „Skål for helsen" / „Skål for et godt helbred" für Norwegisch und
Dänisch, „Jeg vil gjerne be om unnskyldning" als förmliche norwegische Form,
„hen" und „prijsverlaging" für Niederländisch, „taxe" und „hors-d'œuvre" für
Französisch, und für Dänisch die Bestätigung, dass „hvis" das richtige
Fragewort für „wessen" ist und „hvems" nicht standardsprachlich ist –
deshalb wird dort die Konjunktion präzisiert und nicht das Fragewort.

Zwei geplante Texte hat die Vorabkontrolle abgefangen: „Jeg beklager" wäre
in nb neben „Žao mi je" gelandet, deshalb bleibt dort die Alltagsform stehen
und die förmliche Bitte wird höflicher – in sv genauso.

BLEIBT (38 Stellen) – nachgeschlagen und begründet, siehe
bedeutung_ausnahmen.json:

  Dasselbe Wort zweimal, jede Antwort ist richtig (22 Stellen)
      sa / sa …  und  bez / bez …  in allen sieben Sprachen und auf Deutsch,
      prodavač / prodavac (zwei Schreibweisen aus zwei Levels),
      fr prije / prije, fr Znaš ... / znaš

  Die Zielsprache hat kein zweites Wort (11 Stellen)
      pavlaka / kisela pavlaka in en, tr, nl, nb – Sauerrahm und saure Sahne
      sind dort ein Wort. da mor (majka/mama): „moder" ist die gehobene
      Vollform, kein Alltagswort für „Mama". fr gâteau (kolač/torta):
      „tarte" ist etwas anderes als eine Torte.
      so / slano in sv, nl, nb, da: Salz und salzig sind dieselbe Form.
      tr tatlı (Nachtisch/süß), tr yemek (essen/Gericht), sv fråga
      (Frage/fragen): dieselbe Form für Hauptwort und Verb bzw. Eigenschaft.
      fr sac (Tasche/Sack): „cabas" und „sac de jute" sind engere Wörter.

  Steht so in der Grundsprache (3 Stellen)
      de bis morgen, de mit, de ohne – Deutsch ist die Grundsprache und hat
      in uebersetzungen.py keine Tabelle. Für nl wird „Bis morgen!" getrennt.

WIE ES ARBEITET: Es ersetzt ganze Zeilen, jede muss im Block ihrer Sprache
genau einmal vorkommen, sonst bricht es ab. Vor dem Schreiben rechnet es
aus, wie viele Doppelungen danach übrig sind, und bricht ab, wenn ein neuer
Text eine neue Doppelung anlegen würde. Ohne --schreiben ist es ein
Probelauf. Mit --schreiben legt es uebersetzungen.py.vor_trennen an.

DANACH: texte_pruefen.py, doppelte_bedeutung.py und inhalt_bauen.py.
"""

import io
import json
import os
import shutil
import sys
from collections import defaultdict

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, "uebersetzungen.py")
SICHERUNG = ZIEL + ".vor_trennen"
AUSNAHMEN = os.path.join(HIER, "bedeutung_ausnahmen.json")
SCHREIBEN = "--schreiben" in sys.argv

SPRACHEN = ["en", "tr", "sv", "nl", "nb", "da", "fr"]


# ---------------------------------------------------------------------------
# Was geändert wird:  (Sprache, deutscher Schlüssel, alt, neu, warum)
# „warum" nennt immer erst das Wort, das den Text behält.
# ---------------------------------------------------------------------------
AENDERUNGEN = [

    # ---- Englisch ---------------------------------------------------------
    ("en", "Stockwerk", "floor", "storey",
     "pod (Fußboden) behält floor; das Stockwerk heißt storey"),
    ("en", "Preisnachlass", "discount", "price reduction",
     "popust (Rabatt) behält discount"),

    # ---- Türkisch --------------------------------------------------------
    ("tr", "Hähnchen", "tavuk", "tavuk eti",
     "kokoš (Huhn) behält tavuk; das Fleisch ist tavuk eti"),
    ("tr", "Wetter", "hava", "hava durumu",
     "zrak (Luft) behält hava; der Level-Tipp sagt schon hava durumu"),
    ("tr", "Sicherung", "sigorta", "elektrik sigortası",
     "osiguranje (Versicherung) behält sigorta"),
    ("tr", "Fieber", "ateş", "vücut ateşi",
     "vatra (Feuer) behält ateş"),
    ("tr", "Vermieter", "ev sahibi", "kiraya veren",
     "domaćin (Gastgeber) behält ev sahibi; im Mietvertrag heißt es kiraya veren"),
    ("tr", "Preisnachlass", "indirim", "fiyat indirimi",
     "popust (Rabatt) behält indirim"),
    ("tr", "Auf die Gesundheit!", "Şerefe!", "Sağlığınıza!",
     "Živjeli! (Prost) behält Şerefe!"),
    ("tr", "Ich bitte um Entschuldigung", "Özür dilerim", "Sizden özür dilerim",
     "Izvinjavam se behält Özür dilerim; die förmliche Bitte nennt das Gegenüber"),
    ("tr", "Ich hoffe, dass ...", "Umarım ...", "Umarım ki ...",
     "nadam se (hoffentlich) behält umarım"),
    ("tr", "Noch ein bisschen?", "Biraz daha?", "Biraz daha ister misin?",
     "Malo više (Etwas mehr) behält Biraz daha"),
    ("tr", "Es ist fein", "Güzel", "Çok güzel",
     "lijepo (schön) behält güzel"),
    ("tr", "Es schmeckt gut", "Lezzetli", "Çok lezzetli",
     "ukusno (lecker) behält lezzetli"),

    # ---- Schwedisch ------------------------------------------------------
    ("sv", "Kueken / Haehnchen", "kyckling", "kycklingunge / kyckling",
     "piletina (Hähnchen) behält kyckling; nb schreibt kyllingunge / kylling"),
    ("sv", "Gesegnetes Bajram!", "Glad Bajram!", "Välsignad Bajram!",
     "Sretan Bajram! behält Glad Bajram!; nb und da schreiben Velsignet Bajram!"),
    ("sv", "Ich bitte um Entschuldigung", "Jag ber om ursäkt",
     "Jag vill gärna be om ursäkt",
     "Izvinjavam se behält Jag ber om ursäkt; die förmliche Bitte wird höflicher"),

    # ---- Niederländisch --------------------------------------------------
    ("nl", "Huhn", "kip", "hen",
     "piletina (Hähnchen) behält kip; die Henne heißt hen, wie sv höna und fr poule"),
    ("nl", "Preisnachlass", "korting", "prijsverlaging",
     "popust (Rabatt) behält korting"),
    ("nl", "Geschäft", "winkel", "zaak",
     "prodavnica (Laden) behält winkel"),
    ("nl", "Bis morgen!", "Tot morgen!", "We zien elkaar morgen!",
     "do sutra behält tot morgen; die anderen Sprachen übersetzen den Gruß wörtlich"),

    # ---- Norwegisch ------------------------------------------------------
    ("nb", "Leute", "folk", "mennesker",
     "narod (Volk) behält folk; sv schreibt människor (flera)"),
    ("nb", "das Fasten", "faste", "fasten",
     "postiti (fasten) behält faste; sv schreibt fastan"),
    ("nb", "Ich bitte um Entschuldigung", "Jeg ber om unnskyldning",
     "Jeg vil gjerne be om unnskyldning",
     "Izvinjavam se behält Jeg ber om unnskyldning; Jeg beklager ist besetzt "
     "(Žao mi je), deshalb wird die förmliche Bitte höflicher"),
    ("nb", "Noch ein bisschen?", "Litt mer?", "Litt til?",
     "Malo više (Etwas mehr) behält Litt mer; sv schreibt Lite till?"),
    ("nb", "Auf die Gesundheit!", "Skål!", "Skål for helsen!",
     "Živjeli! (Prost) behält Skål!"),

    # ---- Dänisch ---------------------------------------------------------
    ("da", "Leute", "folk", "mennesker",
     "narod (Volk) behält folk; sv schreibt människor (flera)"),
    ("da", "Kueken / Haehnchen", "kylling", "kyllingunge / kylling",
     "piletina (Hähnchen) behält kylling; nb schreibt es genauso"),
    ("da", "wenn / falls", "hvis", "hvis (betingelse)",
     "Čiji? behält Hvis? – hvis ist das richtige Fragewort, hvems nicht; "
     "sv schreibt om (villkor)"),
    ("da", "Noch ein bisschen?", "Lidt mere?", "Lidt til?",
     "Malo više (Etwas mehr) behält Lidt mere; sv schreibt Lite till?"),
    ("da", "Auf die Gesundheit!", "Skål!", "Skål for helbredet!",
     "Živjeli! (Prost) behält Skål!"),

    # ---- Französisch -----------------------------------------------------
    ("fr", "Vorspeise", "entrée", "hors-d'œuvre",
     "ulaz (Eingang) behält entrée"),
    ("fr", "Laden", "magasin", "boutique",
     "radnja (Geschäft) behält magasin; Laden (Lok.) heißt schon boutique (locatif)"),
    ("fr", "Gebühr", "frais", "taxe",
     "svježe (frisch) behält frais"),
    ("fr", "Gebühr (Akk.)", "frais (accusatif)", "taxe (accusatif)",
     "zieht mit Gebühr mit, damit taksu und taksa dasselbe Wort zeigen"),
]


def normal(s):
    """Wie matches() und doppelte_bedeutung.py vergleichen."""
    return (s or "").strip().rstrip(".!?…").strip().lower()


# ---------------------------------------------------------------------------
# Rechnen, was die Änderung bewirkt – ohne die Datei anzufassen
# ---------------------------------------------------------------------------
def doppelte(code, tabelle, woerter, kategorien):
    """{angezeigte Bedeutung: [(bosnisch, level-id), ...]} mit mehr als einem Wort."""
    nach_bedeutung = defaultdict(list)
    for k in kategorien:
        for w in k["words"]:
            bs, de = w.get("bs"), w.get("de")
            if not bs or not de:
                continue
            anzeige = woerter.get(bs, tabelle.get(de, de))
            nach_bedeutung[normal(anzeige)].append((bs, k["id"]))
    return {b: v for b, v in sorted(nach_bedeutung.items()) if len(v) > 1}


def vorschau():
    """(vorher, nachher) je Sprache – und Abbruch, wenn etwas nicht passt."""
    sys.path.insert(0, HIER)
    import vokabeln
    import uebersetzungen

    fehler = []
    for code, schluessel, alt, neu, _ in AENDERUNGEN:
        ist = uebersetzungen.INHALT[code]["texte"].get(schluessel)
        if ist is None:
            fehler.append("%s: Schlüssel %r steht nicht in der Tabelle" % (code, schluessel))
        elif ist != alt:
            fehler.append("%s %r: Tabelle sagt %r, erwartet war %r"
                          % (code, schluessel, ist, alt))
    if fehler:
        print("ABBRUCH, die Tabelle sieht anders aus als erwartet:")
        for f in fehler:
            print("   " + f)
        sys.exit(1)

    stand = {}
    for code in SPRACHEN:
        tabelle = dict(uebersetzungen.INHALT[code]["texte"])
        woerter = uebersetzungen.INHALT[code].get("woerter", {})
        vorher = doppelte(code, tabelle, woerter, vokabeln.KATEGORIEN)
        for c, schluessel, _, neu, _ in AENDERUNGEN:
            if c == code:
                tabelle[schluessel] = neu
        nachher = doppelte(code, tabelle, woerter, vokabeln.KATEGORIEN)
        stand[code] = (vorher, nachher)
    return stand


# ---------------------------------------------------------------------------
# Die Datei
# ---------------------------------------------------------------------------
def bloecke(text):
    """{sprachcode: (anfang, ende)} – die Grenzen von INHALT[<code>]."""
    marken = []
    for code in SPRACHEN:
        marke = '\n"%s": {' % code
        if text.count(marke) != 1:
            print("ABBRUCH: %r steht %d mal in der Datei" % (marke.strip(), text.count(marke)))
            sys.exit(1)
        marken.append((text.index(marke), code))
    marken.sort()
    grenzen = {}
    for i, (pos, code) in enumerate(marken):
        ende = marken[i + 1][0] if i + 1 < len(marken) else len(text)
        grenzen[code] = (pos, ende)
    return grenzen


def main():
    stand = vorschau()

    text = io.open(ZIEL, encoding="utf-8", newline="").read()
    if "\r\n" not in text:
        print("ABBRUCH: uebersetzungen.py hat keine CRLF-Zeilenenden mehr.")
        return 1
    grenzen = bloecke(text)

    print("=" * 72)
    print("Was geändert wird")
    print("=" * 72)
    letzte = None
    for code, schluessel, alt, neu, grund in AENDERUNGEN:
        if code != letzte:
            print()
            letzte = code
        alt_zeile = '    "%s": "%s",' % (schluessel, alt)
        neu_zeile = '    "%s": "%s",' % (schluessel, neu)
        anfang, ende = grenzen[code]
        block = text[anfang:ende]
        n = block.count(alt_zeile)
        if n != 1:
            print("ABBRUCH bei %s %r: %d Treffer statt 1" % (code, schluessel, n))
            print("   gesucht: %s" % alt_zeile)
            return 1
        text = text[:anfang] + block.replace(alt_zeile, neu_zeile) + text[ende:]
        grenzen = bloecke(text)
        print("   %-3s %-28s %r -> %r" % (code, schluessel, alt, neu))
        print("       %s" % grund)

    # ---------------------------------------------------------- Nachkontrolle
    print()
    print("=" * 72)
    print("Was das für die Doppelungen heißt")
    print("=" * 72)
    ausnahmen = set()
    if os.path.exists(AUSNAHMEN):
        daten = json.load(io.open(AUSNAHMEN, encoding="utf-8"))
        for fall in daten.get("bleiben", []):
            ausnahmen.add((fall["sprache"], normal(fall["bedeutung"])))

    summe_vor = summe_nach = 0
    neu_entstanden = []
    offen = []
    for code in SPRACHEN:
        vorher, nachher = stand[code]
        summe_vor += len(vorher)
        summe_nach += len(nachher)
        for bedeutung in nachher:
            if bedeutung not in vorher:
                neu_entstanden.append((code, bedeutung, nachher[bedeutung]))
            elif (code, bedeutung) not in ausnahmen:
                offen.append((code, bedeutung, nachher[bedeutung]))
        print("   %-3s  %2d Bedeutungen mit mehr als einem Wort  ->  %2d"
              % (code, len(vorher), len(nachher)))
    print("   %-3s  %2d                                       ->  %2d"
          % ("", summe_vor, summe_nach))
    print()
    print("   (Deutsch fehlt in dieser Aufstellung: es ist die Grundsprache")
    print("    und hat keine Tabelle. doppelte_bedeutung.py zählt es mit und")
    print("    kommt deshalb auf drei mehr.)")

    if neu_entstanden:
        print()
        print("ABBRUCH: die neuen Texte legen neue Doppelungen an:")
        for code, bedeutung, eintraege in neu_entstanden:
            print("   %s  %r  =  %s" % (code, bedeutung,
                                        ", ".join(bs for bs, _ in eintraege)))
        return 1

    if ausnahmen:
        if offen:
            print()
            print("   Noch nicht in bedeutung_ausnahmen.json vermerkt:")
            for code, bedeutung, eintraege in offen:
                print("      %s  %r  =  %s" % (code, bedeutung,
                                               ", ".join(bs for bs, _ in eintraege)))
        else:
            print()
            print("   Jede übrige Doppelung steht mit Begründung in")
            print("   bedeutung_ausnahmen.json.")
    else:
        print()
        print("   Hinweis: bedeutung_ausnahmen.json fehlt, die übrigen")
        print("   Doppelungen sind also nirgends begründet.")

    print()
    print("   An den Lückensätzen, Level-Namen und Sektionen ändert sich")
    print("   nichts. Über die Vokabelkarte hinaus wirken nur „Gebühr\" und")
    print("   „Gebühr (Akk.)\" im Wörterbuch (taksa, taksu) und „wenn / falls\"")
    print("   in der Grammatik-Tabelle zu den Nebensätzen – jeweils auf")
    print("   dasselbe Wort.")

    if SCHREIBEN:
        shutil.copyfile(ZIEL, SICHERUNG)
        io.open(ZIEL, "w", encoding="utf-8", newline="").write(text)
        print()
        print("Sicherung: %s" % os.path.basename(SICHERUNG))
        print("geschrieben: %s (%d Zeilen geändert)"
              % (os.path.basename(ZIEL), len(AENDERUNGEN)))
        print()
        print("Jetzt: texte_pruefen.py, doppelte_bedeutung.py, inhalt_bauen.py")
    else:
        print()
        print("(Probelauf. Mit --schreiben wird es eingetragen.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
