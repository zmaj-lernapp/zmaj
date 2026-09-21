// Macht aus dem SmartDragon-Zeichen eine Fassung für weißes Papier.
//
// Das Original in store/smartdragon-logo.svg gehört auf dunklen Grund: Der
// Schriftzug ist weiß. Auf einem Blatt Papier steht dann nur der Drachenkopf
// da und daneben nichts. Die Zähne sind ebenfalls weiß und müssen es
// bleiben – deshalb wird nicht stumpf jedes Weiß ersetzt, sondern nur die
// Füllung des Textes, den seine Kennung vsText eindeutig macht.
//
// Aufruf:  node logo_papier.js

const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const HIER = __dirname;
const QUELLE = path.join(HIER, "..", "store", "smartdragon-logo.svg");
const SVG_HELL = path.join(HIER, "smartdragon-papier.svg");
const PNG = path.join(HIER, "smartdragon-papier.png");

const BREITE = 510;          // dreifach, damit es im Druck nicht ausfranst
const SCHRIFTFARBE = "#1E3FA8";   // dasselbe Blau wie der Kopf

let svg = fs.readFileSync(QUELLE, "utf8");

// Nur die Textfüllung. Der Block reicht von id="vsText" bis zum nächsten >.
const vorher = svg;
svg = svg.replace(
  /(<text\s+id="vsText"[\s\S]*?fill=")#FFFFFF(")/,
  `$1${SCHRIFTFARBE}$2`
);
if (svg === vorher) {
  console.error("ABBRUCH: die Textfüllung wurde nicht gefunden.");
  console.error("Hat sich logo_sichern.py geändert? Dann hier nachziehen.");
  process.exit(1);
}

// Gegenprobe: Die Zähne müssen weiß geblieben sein.
const weissDanach = (svg.match(/#FFFFFF/g) || []).length;
const weissVorher = (vorher.match(/#FFFFFF/g) || []).length;
if (weissDanach !== weissVorher - 1) {
  console.error(
    `ABBRUCH: ${weissVorher - weissDanach} Weiß-Angaben ersetzt, erwartet genau 1.`);
  process.exit(1);
}

svg = svg.replace(
  "<!-- SmartDragon - Zeichen des Studios, Maul zu, ohne Feuer",
  "<!-- SmartDragon - Fassung fuer WEISSES PAPIER, erzeugt von mappe/logo_papier.js.\n" +
  "     Nicht von Hand aendern - das Original steht in store/smartdragon-logo.svg.\n" +
  "     Einziger Unterschied: der Schriftzug ist blau statt weiss.\n" +
  "     SmartDragon - Zeichen des Studios, Maul zu, ohne Feuer");

fs.writeFileSync(SVG_HELL, svg);

sharp(Buffer.from(svg))
  .resize({ width: BREITE })
  .png()                       // Hintergrund bleibt durchsichtig
  .toFile(PNG)
  .then((i) => {
    console.log(`${path.basename(SVG_HELL)}  geschrieben`);
    console.log(`${path.basename(PNG)}  ${i.width}x${i.height}, ${(i.size / 1024).toFixed(1)} kB`);
  })
  .catch((e) => {
    console.error("Rendern ging schief:", e.message);
    process.exit(1);
  });
