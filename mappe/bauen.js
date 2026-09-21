// Baut Kapitel 1 der Projektmappe als Word-Datei.
// Layout nach dem Vorbild der Smartgrow-Mappe vom 12.05.2026:
// grosse Titelseite, Fusszeile mit Datum und "Seite X von Y".
//
// Aufruf:  node bauen.js <ziel.docx>

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Footer, Header, ImageRun, PageNumber, NumberFormat, TabStopType,
  TabStopPosition, BorderStyle, LevelFormat, convertInchesToTwip,
} = require("docx");

const ZIEL = process.argv[2] || "Kapitel1.docx";
const T = JSON.parse(fs.readFileSync(__dirname + "/kapitel1.json", "utf8"));

// ---------------------------------------------------------------- Bausteine
const leer = (n = 1) =>
  Array.from({ length: n }, () => new Paragraph({ text: "" }));

const absatz = (text, opt = {}) =>
  new Paragraph({
    spacing: { after: 160, line: 276 },
    alignment: opt.zentriert ? AlignmentType.CENTER : AlignmentType.JUSTIFIED,
    children: [new TextRun({ text, size: 22, font: "Calibri" })],
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

const ueber1 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, bold: true, size: 32, font: "Calibri Light", color: "1F3864" })],
  });

const ueber2 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2,
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
    spacing: { after: tief ? 90 : 130 },
    indent: { left: tief ? convertInchesToTwip(0.4) : 0 },
    tabStops: [
      { type: TabStopType.LEFT, position: convertInchesToTwip(tief ? 0.85 : 0.45) },
      { type: TabStopType.RIGHT, position: TabStopPosition.MAX, leader: "dot" },
    ],
    children: [
      new TextRun({ text: nr + "\t", bold: !tief, size: 24, font: "Calibri", color: tief ? "444444" : "1F3864" }),
      new TextRun({ text: titel, bold: !tief, size: 24, font: "Calibri", color: tief ? "444444" : "1F3864" }),
      new TextRun({ text: "\t" + (seite || "–"), bold: !tief, size: 24, font: "Calibri", color: seite ? "1F3864" : "AAAAAA" }),
    ],
  });

const inhalt = [];
inhalt.push(new Paragraph({
  spacing: { before: 200, after: 320 },
  children: [new TextRun({ text: "Inhalt", bold: true, size: 44, font: "Calibri Light", color: "1F3864" })],
}));
/* Ein Unterkapitel erkennt man an Ziffer-Punkt-Ziffer (2.1), NICHT am
   blossen Punkt - 2. hat naemlich auch einen. Mit der falschen Pruefung
   war jedes Hauptkapitel eingerueckt und nicht fett. */
const istUnter = (nr) => /^\d+\.\d/.test(nr);
T.gliederung.forEach((g) => inhalt.push(ivZeile(g[0], g[1], g[3], istUnter(g[0]))));
inhalt.push(new Paragraph({
  spacing: { before: 400 },
  children: [new TextRun({
    text: "Ein Strich steht für ein Kapitel, das noch entsteht. "
        + "Die Seitenzahlen ergänzen sich, sobald die Kapitel geschrieben sind.",
    size: 20, font: "Calibri", color: "808080", italics: true,
  })],
}));
inhalt.push(new Paragraph({ children: [new (require("docx").PageBreak)()] }));

// ---------------------------------------------------------------- Kapitel 1
inhalt.push(ueber1("1. Vorstellung des Projekts und des Verfassers"));

for (const teil of T.kapitel1) {
  if (teil.ueberschrift) inhalt.push(ueber2(teil.ueberschrift));
  for (const b of teil.bloecke) {
    if (typeof b === "string") inhalt.push(absatz(b));
    else if (b.punkte) b.punkte.forEach((p) => inhalt.push(punkt(p)));
    else if (b.mix) inhalt.push(absatzMix(b.mix));
  }
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
  description: "Technikerarbeit, Kapitel 1",
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
