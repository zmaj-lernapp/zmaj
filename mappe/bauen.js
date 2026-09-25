// Baut die Projektmappe als Word-Datei: Titelseite, Inhalt, Kapitel 1 bis 5, Anhang.
// Layout nach dem Vorbild der Smartgrow-Mappe vom 12.05.2026:
// grosse Titelseite, Fusszeile mit Datum und "Seite X von Y".
//
// Aufruf:  node bauen.js <ziel.docx>

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Footer, Header, ImageRun, PageNumber, NumberFormat, TabStopType,
  TabStopPosition, BorderStyle, LevelFormat, convertInchesToTwip,
  Table, TableRow, TableCell, WidthType, VerticalAlign,
} = require("docx");

const ZIEL = process.argv[2] || "Zmaj Projektmappe.docx";
const T = JSON.parse(fs.readFileSync(__dirname + "/kapitel1.json", "utf8"));

// ---------------------------------------------------------------- Bausteine
const leer = (n = 1) =>
  Array.from({ length: n }, () => new Paragraph({ text: "" }));

/* Zerlegt einen Text an **doppelten Sternen** in fette und normale Stuecke.
   Damit bleiben die Kapiteldateien im Rohzustand lesbar: wer kapitel2.json
   oeffnet, sieht sofort, was im Dokument hervorgehoben ist, ohne es bauen
   zu muessen. Leere Stuecke fliegen raus - sonst entstehen bei **Fett** am
   Absatzanfang unsichtbare Laeufe. */
const teileFett = (text) => {
  const stuecke = String(text).split("**");
  const raus = [];
  stuecke.forEach((s, i) => {
    if (s === "") return;
    raus.push(new TextRun({ text: s, bold: i % 2 === 1, size: 22, font: "Calibri" }));
  });
  return raus.length ? raus : [new TextRun({ text: "", size: 22, font: "Calibri" })];
};

const absatz = (text, opt = {}) =>
  new Paragraph({
    spacing: { after: 160, line: 276 },
    alignment: opt.zentriert ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
    children: teileFett(text),
  });

// Ein Absatz mit fetten Stuecken: ["normal", ["fett", true], "normal"]
const absatzMix = (stuecke) =>
  new Paragraph({
    spacing: { after: 160, line: 276 },
    alignment: AlignmentType.JUSTIFIED,
    children: stuecke.map((s) =>
      Array.isArray(s)
        ? new TextRun({ text: s[0], bold: true, size: 22, font: "Calibri" })
        : new TextRun({ text: s, size: 22, font: "Calibri" })),
  });

const punkt = (text) =>
  new Paragraph({
    numbering: { reference: "striche", level: 0 },
    spacing: { after: 80, line: 276 },
    children: [new TextRun({ text, size: 22, font: "Calibri" })],
  });

/* ------------------------------------------------------------------ TABELLE
   Ab Kapitel 4 reichen Absaetze und Striche nicht mehr: Eine Risikoanalyse
   ohne Tabelle ist eine Aufzaehlung, und eine Aufzaehlung laesst sich nicht
   nach Rang sortieren.

   Form in der Kapiteldatei:

     { "tabelle": {
         "breiten": [6, 46, 8, 8, 8, 24],     Prozent, Summe 100 (darf fehlen)
         "kopf":    ["Nr.", "Risiko", "E", "A", "R", "danach"],
         "zeilen":  [["1", "…", "2", "5", "10", "5"]] } }

   Zellen, die nur aus Ziffern bestehen, werden von selbst zentriert - sonst
   muesste jede Zahlenspalte einzeln ausgezeichnet werden. */
const LINIE = { style: BorderStyle.SINGLE, size: 2, color: "BFBFBF" };
/* Zentriert wird, was eine Zahl ist oder ein Bereich aus Zahlen -
   "3", "20", "1 bis 4", "15–25". Alles andere bleibt linksbuendig. */
const nurZahl = (s) => /^[0-9]+(\s*(bis|–|-)\s*[0-9]+)?$/.test(String(s).trim());

/* Wie teileFett, aber fuer Zellen: kleiner gesetzt, und im Kopf ist alles
   fett und weiss. Eine eigene Funktion, weil teileFett die Groesse fest auf
   11 pt legt - in einer sechsspaltigen Tabelle ist das zu gross. */
const zellenText = (text, opt) => {
  const raus = [];
  String(text).split("**").forEach((s, i) => {
    if (s === "") return;
    raus.push(new TextRun({
      text: s,
      bold: opt.kopf || i % 2 === 1,
      color: opt.kopf ? "FFFFFF" : "000000",
      size: 18, font: "Calibri",
    }));
  });
  return raus.length ? raus : [new TextRun({ text: "", size: 18, font: "Calibri" })];
};

const zelle = (text, opt = {}) =>
  new TableCell({
    width: opt.breite ? { size: opt.breite, type: WidthType.PERCENTAGE } : undefined,
    shading: opt.kopf ? { fill: "1F3864" } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      spacing: { after: 0, line: 240 },
      alignment: (opt.kopf || opt.mitte || nurZahl(text)) ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: zellenText(text, opt),
    })],
  });

const tabelle = (t) => {
  const b = t.breiten || t.kopf.map(() => Math.round(100 / t.kopf.length));
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: LINIE, bottom: LINIE, left: LINIE, right: LINIE,
               insideHorizontal: LINIE, insideVertical: LINIE },
    rows: [
      new TableRow({
        tableHeader: true,          // wiederholt sich, wenn die Tabelle umbricht
        children: t.kopf.map((k, i) => zelle(k, { kopf: true, breite: b[i] })),
      }),
      ...t.zeilen.map((z) => new TableRow({
        /* Eine Zeile bleibt zusammen. Ohne das bricht eine lange Zeile am
           Seitenende mitten durch: Der Text laeuft auf der naechsten Seite
           weiter, die Zahlenspalten bleiben dort aber leer - die Zeile
           sieht aus, als fehlten ihre Werte. */
        cantSplit: true,
        // "mitte" zentriert Spalten, die keine reinen Zahlen enthalten -
        // etwa eine Kennung wie R3, die sonst allein linksbuendig staende.
        children: z.map((c, i) => zelle(c, {
          breite: b[i],
          mitte: (t.mitte || []).includes(i),
        })),
      })),
    ],
  });
};

/* --------------------------------------------------------- BILDERGITTER
   Die Mappe beschreibt zwanzig Seiten lang eine Anwendung, die der Leser
   nie gesehen hat. Die Bildstrecke im Anhang holt das nach.

   Gesetzt wird als randlose Tabelle: Word kann Bilder nicht von selbst
   nebeneinander umbrechen, eine Tabelle schon. Die letzte Reihe wird mit
   leeren Zellen aufgefuellt, sonst werden ihre Bilder breiter als die
   darueber.

     { "bilder": { "spalten": 3, "breite": 150,
                   "liste": [ { "datei": "…/01-start.png", "text": "Startseite" } ] } } */
const KEIN = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const OHNE_RAHMEN = { top: KEIN, bottom: KEIN, left: KEIN, right: KEIN,
                      insideHorizontal: KEIN, insideVertical: KEIN };

const bildZelle = (b, breite, spalten) => {
  const pfad = b && b.datei ? __dirname + "/" + b.datei : null;
  const da = pfad && fs.existsSync(pfad);
  if (b && b.datei && !da) console.error("Hinweis: " + b.datei + " fehlt - Platz bleibt leer.");
  return new TableCell({
    width: { size: Math.round(100 / spalten), type: WidthType.PERCENTAGE },
    borders: OHNE_RAHMEN,
    margins: { top: 60, bottom: 60, left: 70, right: 70 },
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
        children: da ? [new ImageRun({
          type: "png",
          data: fs.readFileSync(pfad),
          transformation: { width: breite, height: Math.round(breite * 1920 / 1080) },
        })] : [],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 0 },
        children: [new TextRun({ text: b && b.text ? b.text : "", size: 16, font: "Calibri", color: "595959" })],
      }),
    ],
  });
};

const bilder = (g) => {
  const spalten = g.spalten || 3;
  const breite = g.breite || 150;
  const reihen = [];
  for (let i = 0; i < g.liste.length; i += spalten) {
    const r = g.liste.slice(i, i + spalten);
    while (r.length < spalten) r.push(null);      // Reihe auffuellen
    reihen.push(r);
  }
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: OHNE_RAHMEN,
    rows: reihen.map((r) => new TableRow({
      cantSplit: true,                            // Bild und Unterschrift bleiben zusammen
      children: r.map((b) => bildZelle(b, breite, spalten)),
    })),
  });
};

/* ---------------------------------------------------------- QUELLTEXT
   Feste Schriftbreite, grau hinterlegt, ohne Zeilenumbruch im Satz. Eine
   Zeile Quelltext, die umbricht, ist nicht mehr lesbar - deshalb sind die
   Auszuege im Anhang von Hand auf Breite gebracht.

     { "quelltext": { "titel": "…", "datei": "web/index.html, Zeile 3898",
                      "zeilen": ["…", "…"] } } */
const quelltext = (q) => {
  const raus = [];
  if (q.titel) raus.push(new Paragraph({
    spacing: { before: 240, after: 80 },
    keepNext: true,
    children: [new TextRun({ text: q.titel, bold: true, size: 20, font: "Calibri" })],
  }));
  q.zeilen.forEach((z, i) => raus.push(new Paragraph({
    shading: { fill: "F4F6FA" },
    spacing: { after: 0, line: 230 },
    keepNext: i < q.zeilen.length - 1,
    children: [new TextRun({ text: z === "" ? " " : z, font: "Consolas", size: 15 })],
  })));
  if (q.datei) raus.push(new Paragraph({
    spacing: { before: 80, after: 160 },
    children: [new TextRun({ text: q.datei, italics: true, size: 16, font: "Calibri", color: "808080" })],
  }));
  return raus;
};

const ueber1 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    keepNext: true,   // nie allein am Seitenende stehen lassen
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, bold: true, size: 32, font: "Calibri Light", color: "1F3864" })],
  });

const ueber2 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2,
    keepNext: true,   // nie allein am Seitenende stehen lassen
    spacing: { before: 280, after: 140 },
    children: [new TextRun({ text, bold: true, size: 26, font: "Calibri Light", color: "2E5496" })],
  });

/* ---------------------------------------------------------------- TITELSEITE
   Der Hintergrund ist ein Bild: Farbflächen, Logo, Telefon, Striche. Die
   Schrift liegt als echter Word-Text darüber - markierbar, durchsuchbar
   und korrigierbar. Ein Deckblatt, das nur ein Bild ist, kann niemand mehr
   ändern, ohne das Bauskript zu haben.

   Die Maße stammen aus deckblatt_entwuerfe.js: dort ist die Seite
   1240 x 1754 px groß, also A4 bei 150 dpi. Umrechnung in Zentimeter:
   px / 150 * 2,54. In Twips (Word rechnet darin): cm * 567.

   Der linke Textrand liegt im Entwurf bei x = 95 px = 1,61 cm. Genau
   dorthin wird der Seitenrand gesetzt, dann fluchtet der Text von selbst. */
const HG = __dirname + "/entwurf-4-hintergrund.png";
const hatHG = fs.existsSync(HG);
if (!hatHG) {
  console.error("Hinweis: " + HG + " fehlt - Titelseite ohne Hintergrund.");
  console.error("Erzeugen mit:  node deckblatt_entwuerfe.js");
}

const px2tw = (px) => Math.round(px / 150 * 2.54 * 567);
const px2pt = (px) => Math.round(px / 150 * 72 * 2);   // halbe Punkte für docx

// Ein Textzug auf der Titelseite. `oben` ist der Abstand von der Oberkante
// der Seite bis zur Oberkante des Absatzes, in Pixeln des Entwurfs.
let letzteKante = 0;
function titelzeile(text, opt) {
  const vor = Math.max(0, px2tw(opt.oben - letzteKante));
  letzteKante = opt.oben + opt.groesse * 1.15;   // muss zu `line` unten passen
  return new Paragraph({
    spacing: { before: vor, after: 0, line: Math.round(opt.groesse * 1.15 / 150 * 1440), lineRule: "exact" },
    children: [new TextRun({
      text,
      size: px2pt(opt.groesse),
      bold: !!opt.fett,
      color: opt.farbe,
      font: opt.leicht ? "Segoe UI Light" : "Segoe UI",
      characterSpacing: opt.sperrung ? Math.round(opt.sperrung / 150 * 1440) : undefined,
    })],
  });
}

const titelseite = [
  /* Der Hintergrund hängt am ersten Absatz und liegt hinter allem anderen.
     Das Bild ist 1240 x 1754 px groß und wird auf exakt A4 gesetzt:
     21 x 29,7 cm, in Word-Pixeln bei 96 dpi also 794 x 1123. */
  new Paragraph({
    spacing: { after: 0, line: 20, lineRule: "exact" },
    children: hatHG ? [new ImageRun({
      type: "png",
      data: fs.readFileSync(HG),
      transformation: { width: 794, height: 1123 },
      floating: {
        horizontalPosition: { relative: "page", offset: 0 },
        verticalPosition: { relative: "page", offset: 0 },
        behindDocument: true,
        zIndex: 0,
        allowOverlap: true,
      },
    })] : [],
  }),

  // Die Zahlen sind die Oberkanten aus dem Entwurf. Im SVG steht dort die
  // Grundlinie; Word misst von oben, deshalb je 0,8 × Schriftgröße höher.
  titelzeile("ZMAJ", { oben: 386, groesse: 128, farbe: "FFFFFF", leicht: true, sperrung: 10 }),
  titelzeile("BOSNISCH LERNEN", { oben: 578, groesse: 38, farbe: "4F76E8", fett: true, sperrung: 4 }),

  titelzeile("Eine Android-Anwendung von der", { oben: 669, groesse: 26, farbe: "AAB6D8" }),
  titelzeile("Idee bis zur Veröffentlichung", { oben: 707, groesse: 26, farbe: "AAB6D8" }),

  titelzeile("Projektarbeit zur Weiterbildung zum", { oben: 812, groesse: 23, farbe: "6B7BA8" }),
  titelzeile("staatlich geprüften Techniker", { oben: 848, groesse: 23, farbe: "6B7BA8" }),

  titelzeile("Ajdin Hasić", { oben: 1298, groesse: 40, farbe: "1A1A1A", fett: true }),
  ...T.titelzeilen.map((z, i) =>
    titelzeile(z, { oben: 1361 + i * 52, groesse: 26, farbe: "444444" })),

  titelzeile(T.stand, { oben: 1655, groesse: 21, farbe: "999999" }),
];

/* ------------------------------------------------------ INHALTSVERZEICHNIS
   Von Hand gesetzt, nicht als Word-Feld. Ein automatisches Verzeichnis
   listet nur, was schon geschrieben ist - hier soll aber die ganze geplante
   Arbeit stehen, damit der Betreuer den Umfang sieht. Was fertig ist,
   bekommt eine Seitenzahl; alles andere einen Strich.

   Sobald die Mappe vollstaendig ist, kann das gegen ein echtes Feld
   getauscht werden. */
const ivZeile = (nr, titel, seite, tief) =>
  new Paragraph({
    spacing: { after: tief ? 52 : 78 },   // eng genug, dass 35 Zeilen und der Hinweis auf eine Seite passen
    indent: { left: tief ? convertInchesToTwip(0.4) : 0 },
    tabStops: [
      { type: TabStopType.LEFT, position: convertInchesToTwip(tief ? 0.85 : 0.45) },
      { type: TabStopType.RIGHT, position: TabStopPosition.MAX, leader: "dot" },
    ],
    children: [
      new TextRun({ text: nr + "\t", bold: !tief, size: 22, font: "Calibri", color: tief ? "444444" : "1F3864" }),
      new TextRun({ text: titel, bold: !tief, size: 22, font: "Calibri", color: tief ? "444444" : "1F3864" }),
      new TextRun({ text: "\t" + (seite || "–"), bold: !tief, size: 22, font: "Calibri", color: seite ? "1F3864" : "AAAAAA" }),
    ],
  });

const inhalt = [];
inhalt.push(new Paragraph({
  spacing: { before: 120, after: 260 },
  children: [new TextRun({ text: "Inhalt", bold: true, size: 44, font: "Calibri Light", color: "1F3864" })],
}));
/* Ein Unterkapitel erkennt man an Ziffer-Punkt-Ziffer (2.1), NICHT am
   blossen Punkt - 2. hat naemlich auch einen. Mit der falschen Pruefung
   war jedes Hauptkapitel eingerueckt und nicht fett. */
const istUnter = (nr) => /^\d+\.\d/.test(nr);
T.gliederung.forEach((g) => inhalt.push(ivZeile(g[0], g[1], g[3], istUnter(g[0]))));
inhalt.push(new Paragraph({
  spacing: { before: 260 },
  children: [new TextRun({
    text: "Die Seitenzahlen gelten für diesen Stand. "
        + "Die Abschnitte 5.4 und 5.7 werden nach der Freigabe im Play Store abgeschlossen.",
    size: 20, font: "Calibri", color: "808080", italics: true,
  })],
}));
inhalt.push(new Paragraph({ children: [new (require("docx").PageBreak)()] }));

// ---------------------------------------------------------------- Kapitel 1
inhalt.push(ueber1("1. Vorstellung des Projekts und des Verfassers"));

/* Ein Kapitel in Absaetze setzen. Frueher stand diese Schleife nur einmal
   fuer Kapitel 1 da; mit dem zweiten Kapitel lohnt die eigene Funktion. */
const kapitelSetzen = (teile) => {
  for (const teil of teile) {
    if (teil.ueberschrift) inhalt.push(ueber2(teil.ueberschrift));
    for (const b of teil.bloecke) {
      if (typeof b === "string") inhalt.push(absatz(b));
      else if (b.punkte) b.punkte.forEach((p) => inhalt.push(punkt(p)));
      else if (b.mix) inhalt.push(absatzMix(b.mix));
      else if (b.tabelle) {
        inhalt.push(tabelle(b.tabelle));
        // Ohne Leerabsatz klebt der Folgetext an der Tabellenkante.
        inhalt.push(new Paragraph({ spacing: { after: 160 }, text: "" }));
      }
      else if (b.bilder) {
        inhalt.push(bilder(b.bilder));
        inhalt.push(new Paragraph({ spacing: { after: 160 }, text: "" }));
      }
      else if (b.quelltext) quelltext(b.quelltext).forEach((p) => inhalt.push(p));
    }
  }
};

kapitelSetzen(T.kapitel1);

// ------------------------------------------------------------ Kapitel 2 bis 5
/* Jedes Kapitel steht in einer eigenen Datei, damit sich eines bearbeiten
   laesst, ohne die anderen anzufassen. Fehlt eine Datei, wird sie
   stillschweigend uebersprungen - dann entsteht das Dokument ohne dieses
   Kapitel, und die Gliederung zeigt dort weiter einen Strich.

   Frueher stand fuer jedes Kapitel derselbe Block einzeln da. Bei zweien
   ging das; bei vieren ist es eine Liste. */
const KAPITEL = [
  ["kapitel2.json", "kapitel2", "2. Lastenheft"],
  ["kapitel3.json", "kapitel3", "3. Konzeptfindung"],
  ["kapitel4.json", "kapitel4", "4. Risikoanalyse"],
  ["kapitel5.json", "kapitel5", "5. Projektdurchführung"],
];
for (const [datei, schluessel, titel] of KAPITEL) {
  const pfad = __dirname + "/" + datei;
  if (!fs.existsSync(pfad)) continue;
  inhalt.push(new Paragraph({ children: [new (require("docx").PageBreak)()] }));
  inhalt.push(ueber1(titel));
  kapitelSetzen(JSON.parse(fs.readFileSync(pfad, "utf8"))[schluessel]);
}

// ----------------------------------------------------------------- Anhang
/* Die Belegstellen zu Abschnitt 2.2. Der Anhang steht am Ende der Arbeit,
   nicht hinter dem Kapitel - deshalb kommt er hier zuletzt, auch wenn die
   uebrigen Kapitel noch fehlen. Sobald 4 und 5 dazukommen, wandert dieser
   Block hinter sie. */
/* Der Anhang kommt aus zwei Dateien: anhang_quellen.json wird von einem
   Skript erzeugt (die Belegstellen zu 2.2) und darf nicht von Hand
   angefasst werden, kapitel6.json ist geschrieben. Die Ueberschrift
   "6. Anhang" steht nur einmal davor. */
const ANHANG = [
  ["anhang_quellen.json", "anhang_quellen"],
  ["kapitel6.json", "kapitel6"],
];
const anhangTeile = ANHANG
  .filter(([d]) => fs.existsSync(__dirname + "/" + d))
  .map(([d, k]) => JSON.parse(fs.readFileSync(__dirname + "/" + d, "utf8"))[k]);

if (anhangTeile.length) {
  inhalt.push(new Paragraph({ children: [new (require("docx").PageBreak)()] }));
  inhalt.push(ueber1("6. Anhang"));
  anhangTeile.forEach(kapitelSetzen);
}

/* ------------------------------------------------- EIGENSTAENDIGKEITSERKLAERUNG
   Steht als letzte Seite, ohne Nummer und nicht im Inhaltsverzeichnis - sie
   ist kein Kapitel der Arbeit, sondern eine Erklaerung ueber sie.

   Die Unterschriftzeile ist eine randlose Tabelle mit zwei Zellen, die oben
   eine Linie tragen. Eine Reihe Unterstriche waere einfacher, bricht aber
   je nach Schriftgroesse an anderer Stelle um. */
const EPFAD = __dirname + "/erklaerung.json";
if (fs.existsSync(EPFAD)) {
  const E = JSON.parse(fs.readFileSync(EPFAD, "utf8"));
  inhalt.push(new Paragraph({ children: [new (require("docx").PageBreak)()] }));
  inhalt.push(ueber1("Eigenständigkeitserklärung"));
  kapitelSetzen(E.erklaerung);
  inhalt.push(...leer(3));

  const LINIE_OBEN = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
  const unterschriftZelle = (text) => new TableCell({
    width: { size: 50, type: WidthType.PERCENTAGE },
    borders: { top: LINIE_OBEN, bottom: KEIN, left: KEIN, right: KEIN },
    margins: { top: 80, left: 0, right: 200 },
    children: [new Paragraph({
      spacing: { after: 0 },
      children: [new TextRun({ text, size: 20, font: "Calibri", color: "595959" })],
    })],
  });
  inhalt.push(new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: OHNE_RAHMEN,
    rows: [new TableRow({
      cantSplit: true,
      children: [
        unterschriftZelle(E.ort + ", den"),
        unterschriftZelle(E.name),
      ],
    })],
  }));
}

// ---------------------------------------------------------------- Dokument
/* RAENDER. Links und rechts gleich - 2,5 cm.

   Vorher stand hier ein Bindungsrand von 3 cm links gegen 2 cm rechts. Das
   ist bei gebundenen Arbeiten ueblich, aber es verschiebt den Satzspiegel
   sichtbar nach rechts, und Ajdin hat genau das bemaengelt. In der
   Smartgrow-Mappe nachgemessen: dort sind die Raender gleich. Also auch
   hier.

   Die Titelseite darf das NICHT haben. "Zentriert" heisst in Word mittig
   im Satzspiegel, nicht mittig auf dem Blatt - bei ungleichen Raendern
   sitzt der Titel deshalb um die halbe Differenz zu weit rechts, hier
   0,5 cm. Das sieht man, und Ajdin hat es gesehen. Deshalb ist die
   Titelseite ein eigener Abschnitt mit gleichen Raendern, und auch ohne
   Fusszeile - eine Seitenzahl auf dem Deckblatt gehoert dort nicht hin. */
const RAND_TEXT = { top: 1418, bottom: 1418, left: 1418, right: 1418 };
const RAND_TITEL = { top: 0, bottom: 0, left: px2tw(95), right: px2tw(95) };

/* KOPFZEILE mit dem Studio-Zeichen, links, auf jeder Seite - so wie in der
   Smartgrow-Mappe.

   Das Bild ist die Papierfassung aus logo_papier.js: Im Original ist der
   Schriftzug weiss, weil das Zeichen auf dunklem Grund lebt. Auf einem
   Blatt Papier stuende dort sonst nur der Kopf und daneben nichts.

   Gerendert wird mit 510 px Breite und im Dokument auf 151 px gesetzt -
   dreifache Aufloesung, damit der Druck nicht ausfranst. Das
   Seitenverhaeltnis 3:1 stammt aus dem SVG und darf nicht verrutschen. */
const LOGO = __dirname + "/smartdragon-papier.png";
const LOGO_BREITE = 151;     // ca. 4 cm
const LOGO_HOEHE = 50;

const kopfzeile = fs.existsSync(LOGO)
  ? new Header({
      children: [new Paragraph({
        alignment: AlignmentType.LEFT,
        spacing: { after: 120 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync(LOGO),
          transformation: { width: LOGO_BREITE, height: LOGO_HOEHE },
        })],
      })],
    })
  : null;

if (!kopfzeile) {
  console.error("Hinweis: " + LOGO + " fehlt - das Dokument entsteht ohne Logo.");
  console.error("Erzeugen mit:  node logo_papier.js");
}

const fusszeile = new Footer({
  children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
    border: { top: { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF", space: 8 } },
    children: [
      new TextRun({ text: T.stand, size: 18, font: "Calibri", color: "808080" }),
      new TextRun({ text: "\tSeite ", size: 18, font: "Calibri", color: "808080" }),
      new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Calibri", color: "808080" }),
      new TextRun({ text: " von ", size: 18, font: "Calibri", color: "808080" }),
      new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, font: "Calibri", color: "808080" }),
    ],
  })],
});

const doc = new Document({
  creator: "Ajdin Hasić",
  title: "Zmaj – Bosnisch lernen",
  description: "Technikerarbeit, Kapitel 1 bis 3",
  numbering: {
    config: [{
      reference: "striche",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "–",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: convertInchesToTwip(0.35), hanging: convertInchesToTwip(0.2) } } },
      }],
    }],
  },
  sections: [
    // 1) Titelseite: gleiche Raender, keine Fuss- und keine Kopfzeile.
    //    Das Logo steht hier mitten im Titelblock, nicht oben in der Ecke.
    {
      properties: { page: { margin: RAND_TITEL } },
      children: titelseite,
    },
    // 2) Der Textteil mit Bindungsrand, Logo oben und Fusszeile unten
    {
      properties: { page: { margin: RAND_TEXT } },
      children: inhalt,
      ...(kopfzeile ? { headers: { default: kopfzeile } } : {}),
      footers: { default: fusszeile },
    },
  ],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(ZIEL, b);
  console.log("geschrieben: " + ZIEL + "  (" + (b.length / 1024).toFixed(1) + " kB)");
});
