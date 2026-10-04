# -*- coding: utf-8 -*-
r"""Eine Sicherungsdatei darf die App nicht lahmlegen.

GEFUNDEN BEI DER SICHERHEITSPRUEFUNG am 04.10.2026 (Vorbereitung Codex for
Open Source). Eine Sicherung ist eine JSON-Datei, die jeder von Hand
schreiben und weitergeben kann ("hier mein Stand, alles freigeschaltet").
sicherungEinlesen() prueft nur, dass "stand" ein Objekt ist. Was darin
steht, uebernimmt standUebernehmen() fast ungeprueft.

WAS PASSIEREN KANN

  1. Totalausfall ohne Selbsthilfe. {"app":"zmaj","stand":{"gewusst":[1]}}
     Eine Zahl statt einer Kennung in "gewusst". altenFortschrittUmschreiben()
     ruft x.slice() auf und wirft. Der Stand ist da schon ersetzt und wird
     beim naechsten saveProgress() gespeichert. Ab dann wirft
     nachAnmeldung() bei JEDEM Start, bevor der Einstellungsknopf erscheint -
     an "Sicherung einlesen" kommt man nie wieder heran. Hilft nur noch
     "App-Daten loeschen", und damit ist alles weg.
  2. Herzen: "leben":{"anzahl":1e300} gibt unbegrenzte Leben ohne
     Vollversion; ein Text als "zeit" laesst nie wieder ein Herz nachwachsen.
  3. "topf":{"w:...":null} - der Wiederholen-Reiter wirft bei jedem Oeffnen.
  4. "besitz":["constructor"] - FARBEN["constructor"] ist die eingebaute
     Funktion Object, farbeVon() ruft .map darauf auf, der Drache bleibt leer.

WAS GEAENDERT WIRD

  standUebernehmen(): Listen nur mit Texten, Herzen und Serienschutz als
  endliche Zahl zwischen 0 und dem Hoechstwert, im Topf nur Objekte.
  Das wirkt auch beim normalen Start - loadProgress() geht durch dieselbe
  Funktion -, ein schon kaputter Stand heilt sich also selbst.
  farbeVon(): nur eigene Eintraege von FARBEN, nichts aus dem Prototyp.
  sicherungEinlesen(): wirft das Uebernehmen trotzdem, kommt der alte Stand
  zurueck und die Meldung sagt "keine gueltige Sicherung".

WAS BEWUSST BLEIBT
Echte Sicherungen aendern sich nicht: die drei Dateien in testdaten/ haben
nur Texte in den Listen, 5 Herzen, hoechstens 2 Serienschutz und im Topf
nur Objekte (geprueft). Herzen und Serienschutz koennen im Spiel nie ueber
LEBEN_MAX bzw. SCHUTZ_MAX steigen - jede Stelle, die sie erhoeht, nimmt
schon Math.min. Das Kappen beim Einlesen nimmt also niemandem etwas.

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck.

Probelauf:  python import_richten.py
Schreiben:  python import_richten.py --schreiben
"""
import richten

INDEX = richten.INDEX

AENDERUNGEN = [
    ("Listen nur mit Texten",
     "  known = new Set(d.gewusst||[]); passed = new Set(d.bestanden||[]); read = new Set(d.gelesen||[]);",
     "  /* Eine Sicherung kann jeder von Hand schreiben. Eine Zahl in gewusst\n"
     "     liess altenFortschrittUmschreiben() bei jedem Start werfen, bevor der\n"
     "     Einstellungsknopf erschien - siehe import_richten.py, 04.10.2026. */\n"
     "  const nurTexte = x => Array.isArray(x) ? x.filter(s => typeof s === 'string') : [];\n"
     "  known = new Set(nurTexte(d.gewusst)); passed = new Set(nurTexte(d.bestanden)); read = new Set(nurTexte(d.gelesen));"),
    ("gefeiert nur Texte",
     "  gefeiert = new Set(d.gefeiert||[]);",
     "  gefeiert = new Set(nurTexte(d.gefeiert));"),
    ("Lerntage nur als Liste",
     "  days = new Set((d.tage||[]).filter(istDatum));\n  frost = new Set((d.frost||[]).filter(istDatum));",
     "  // Kein Array (etwa \"tage\":\"x\") hiess bisher: .filter wirft. Jetzt: leer.\n"
     "  days = new Set((Array.isArray(d.tage) ? d.tage : []).filter(istDatum));\n"
     "  frost = new Set((Array.isArray(d.frost) ? d.frost : []).filter(istDatum));"),
    ("besitz nur Texte",
     "  besitz = new Set(d.besitz||[]);",
     "  besitz = new Set(nurTexte(d.besitz));"),
    ("im Topf nur Objekte",
     "  topf = (d.topf && typeof d.topf==='object' && !Array.isArray(d.topf)) ? d.topf : {};",
     "  /* Nur Eintraege, die Objekte sind: topfAufgabe() liest e.typ. Object.fromEntries\n"
     "     legt auch \"__proto__\" als gewoehnlichen Schluessel an, nichts aendert den Prototyp. */\n"
     "  topf = (d.topf && typeof d.topf==='object' && !Array.isArray(d.topf))\n"
     "    ? Object.fromEntries(Object.entries(d.topf).filter(([, e]) => e && typeof e==='object' && !Array.isArray(e)))\n"
     "    : {};"),
    ("Herzen und Serienschutz begrenzt",
     "  lives = (d.leben && typeof d.leben.anzahl==='number') ? {anzahl:d.leben.anzahl, zeit:d.leben.zeit||0} : {anzahl:LEBEN_MAX, zeit:0};\n"
     "  schutz = (d.schutz && typeof d.schutz.anzahl==='number') ? {anzahl:d.schutz.anzahl, zeit:d.schutz.zeit||0} : {anzahl:1, zeit:0};",
     "  /* Endliche Zahl zwischen 0 und dem Hoechstwert. Im Spiel kommt nie mehr\n"
     "     zustande - jede Stelle, die erhoeht, nimmt Math.min. 1e300 Herzen aus\n"
     "     einer Datei waeren die Vollversion umsonst, ein Text als zeit liess nie\n"
     "     wieder eins nachwachsen. */\n"
     "  const anzahlBis = (x, max) => (typeof x==='number' && isFinite(x)) ? Math.max(0, Math.min(max, Math.floor(x))) : null;\n"
     "  const zeitpunkt = x => (typeof x==='number' && isFinite(x)) ? x : 0;\n"
     "  const la = (d.leben && typeof d.leben==='object') ? anzahlBis(d.leben.anzahl, LEBEN_MAX) : null;\n"
     "  lives = la !== null ? {anzahl:la, zeit:zeitpunkt(d.leben.zeit)} : {anzahl:LEBEN_MAX, zeit:0};\n"
     "  const sa = (d.schutz && typeof d.schutz==='object') ? anzahlBis(d.schutz.anzahl, SCHUTZ_MAX) : null;\n"
     "  schutz = sa !== null ? {anzahl:sa, zeit:zeitpunkt(d.schutz.zeit)} : {anzahl:1, zeit:0};"),
    ("farbeVon nur eigene Eintraege",
     "const farbeVon = id => (FARBEN[id] || []).map(zuFarbe);",
     "/* hasOwnProperty: FARBEN['constructor'] waere sonst die eingebaute Funktion\n"
     "   Object, und .map darauf wirft - der Drache bliebe leer. 04.10.2026. */\n"
     "const farbeVon = id => (Object.prototype.hasOwnProperty.call(FARBEN, id) ? FARBEN[id] : []).map(zuFarbe);"),
    ("Einlesen mit Rueckweg",
     "  standUebernehmen(d.stand);\n",
     "  /* Wirft das Uebernehmen trotz der Pruefungen in standUebernehmen(), kommt\n"
     "     der alte Stand zurueck - sonst speicherte das naechste saveProgress()\n"
     "     einen halb uebernommenen. import_richten.py, 04.10.2026. */\n"
     "  const vorher = standAlsObjekt();\n"
     "  /* standUebernehmen() schreibt Geschenkjahr und getragenes Stueck sofort\n"
     "     in den Geraetespeicher. Beim Zuruecknehmen muessen die mit zurueck,\n"
     "     sonst verbraucht eine abgelehnte Datei das Jahresgeschenk. */\n"
     "  const geschenkVorher = Object.assign({}, geschenk), getragenVorher = getragen;\n"
     "  try{ standUebernehmen(d.stand); altenFortschrittUmschreiben(); }\n"
     "  catch(e){ standUebernehmen(vorher); altenFortschrittUmschreiben();\n"
     "           geschenk = geschenkVorher; getragen = getragenVorher;\n"
     "           try{ localStorage.setItem(GESCHENK_SCHLUESSEL, JSON.stringify(geschenk));\n"
     "                localStorage.setItem('zmaj_getragen', getragen); }catch(e2){}\n"
     "           note.textContent = t('set.sicherung_keine'); return; }\n"),
    ("Umschreiben nicht doppelt",
     "  altenFortschrittUmschreiben();\n  seitNachEinlesen();",
     "  seitNachEinlesen();"),
]


def anwenden(html):
    """(neuer Text, Fehlerliste). Ein Fehler heisst: nichts wird geschrieben."""
    neu, fehler = richten.ersetze_einmal(html, AENDERUNGEN)
    return neu, fehler + richten.gleichgewicht(html, neu)


def main(argv=None):
    return richten.main(argv, AENDERUNGEN, anwenden, "import_richten.py")


if __name__ == "__main__":
    raise SystemExit(main())
