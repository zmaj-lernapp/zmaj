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

// Zeile im Gliederungs-Ausblick: Nummer, Titel, rechts die Quelle
const glied = (nr, titel, quelle, tief) =>
  new Paragraph({
    spacing: { after: 60 },
    indent: { left: tief ? convertInchesToTwip(0.35) : 0 },
    tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
    children: [
      new TextRun({ text: nr + "\t", bold: !tief, size: 22, font: "Calibri" }),
      new TextRun({ text: titel, bold: !tief, size: 22, font: "Calibri" }),
      new TextRun({ text: "\t" + quelle, size: 18, font: "Calibri", color: "808080", italics: true }),
    ],
  });

// ---------------------------------------------------------------- Titelseite
const titelseite = [
  ...leer(6),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 0 },
    children: [new TextRun({ text: "ZMAJ", bold: true, size: 96, font: "Calibri Light", color: "1F3864" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 240 },
    children: [new TextRun({ text: "BOSNISCH LERNEN", bold: true, size: 44, font: "Calibri Light", color: "2E5496" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 400 },
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: "2E5496", space: 12 } },
    children: [new TextRun({
      text: "Eine Android-Anwendung von der Idee bis zur Veröffentlichung",
      size: 24, font: "Calibri", color: "404040",
    })],
  }),
  /* Das Studio-Zeichen sitzt auf dem Deckblatt zwischen Titel und Namen -
     gross und mittig, nicht klein in der Ecke. Auf allen folgenden Seiten
     steht es dafuer in der Kopfzeile. */
  ...(fs.existsSync(__dirname + "/smartdragon-papier.png")
    ? [new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync(__dirname + "/smartdragon-papier.png"),
          transformation: { width: 264, height: 88 },   // ca. 7 cm breit
        })],
      })]
    : []),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 120 },
    children: [new TextRun({ text: "AJDIN HASIĆ", bold: true, size: 30, font: "Calibri" })],
  }),
  ...T.titelzeilen.map((z) => new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: z, size: 22, font: "Calibri", color: "404040" })],
  })),
  ...leer(3),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: T.stand, size: 20, font: "Calibri", color: "808080" })],
  }),
];

// ---------------------------------------------------------------- Kapitel 1
// Beginnt einen eigenen Abschnitt, siehe unten bei RAENDER.
const inhalt = [];
inhalt.push(ueber1("1. Vorstellung des Projekts und des Verfassers"));

for (const teil of T.kapitel1) {
  if (teil.ueberschrift) inhalt.push(ueber2(teil.ueberschrift));
  for (const b of teil.bloecke) {
    if (typeof b === "string") inhalt.push(absatz(b));
    else if (b.punkte) b.punkte.forEach((p) => inhalt.push(punkt(p)));
    else if (b.mix) inhalt.push(absatzMix(b.mix));
  }
}

// ------------------------------------------------------- Ausblick Gliederung
inhalt.push(new Paragraph({ children: [new (require("docx").PageBreak)()] }));
inhalt.push(ueber1("Geplanter Aufbau der Arbeit"));
inhalt.push(absatz(T.gliederung_einleitung));
inhalt.push(...leer(1));
T.gliederung.forEach((g) => inhalt.push(glied(g[0], g[1], g[2], g[0].includes("."))));
inhalt.push(...leer(1));
inhalt.push(absatz(T.gliederung_schluss));

// ---------------------------------------------------------------- Dokument
/* RAENDER. Der Textteil bekommt links mehr Platz, damit beim Heften oder
   Binden nichts im Falz verschwindet: 3 cm links, 2 cm rechts.

   Die Titelseite darf das NICHT haben. "Zentriert" heisst in Word mittig
   im Satzspiegel, nicht mittig auf dem Blatt - bei ungleichen Raendern
   sitzt der Titel deshalb um die halbe Differenz zu weit rechts, hier
   0,5 cm. Das sieht man, und Ajdin hat es gesehen. Deshalb ist die
   Titelseite ein eigener Abschnitt mit gleichen Raendern, und auch ohne
   Fusszeile - eine Seitenzahl auf dem Deckblatt gehoert dort nicht hin. */
const RAND_TEXT = { top: 1418, bottom: 1418, left: 1701, right: 1134 };
const RAND_TITEL = { top: 1418, bottom: 1418, left: 1418, right: 1418 };

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
