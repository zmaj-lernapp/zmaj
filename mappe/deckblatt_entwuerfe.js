// Drei Entwürfe für das Deckblatt, zum Ansehen und Aussuchen.
//
// Gebaut als SVG und mit sharp gerendert. Das ist nur die Vorschau - die
// gewählte Fassung wird danach richtig in Word gesetzt, mit echtem Text
// über einem Hintergrundbild.
//
// Farben aus der App selbst:
//   #0B1533  der tiefe Grund
//   #060C20  noch dunkler, Rand
//   #4F76E8  das kräftige Blau der Kreise
//   #F5C400  das Gelb der Akzente
//
// Aufruf:  node deckblatt_entwuerfe.js

const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const B = 1240, H = 1754;          // A4 bei 150 dpi
const HIER = __dirname;
const PROJEKT = path.join(HIER, "..");

const DUNKEL = "#0B1533";
const TIEF = "#060C20";
const BLAU = "#4F76E8";
const GELB = "#F5C400";

// Das Logo in beiden Fassungen, als Daten-URL zum Einbetten
const logoDunkel = fs.readFileSync(path.join(PROJEKT, "store", "smartdragon-logo.svg"), "utf8");
const logoHell = fs.readFileSync(path.join(HIER, "smartdragon-papier.svg"), "utf8");
const alsBild = (svg) => "data:image/svg+xml;base64," + Buffer.from(svg).toString("base64");

const schirm = fs.readFileSync(path.join(PROJEKT, "store", "screenshots", "02-lernpfad.png"));

const ANGABEN = [
  "Ajdin Hasić",
  "Klasse 02FSA · Fachrichtung Automatisierungstechnik",
  "Berufs- und Technikerschule Butzbach",
  "Betreuung: Herr Dr. Rosenschon",
  "Bearbeitungszeitraum: 10.08.2026 – 19.03.2027",
];

const SCHRIFT = "Segoe UI, Calibri, sans-serif";

// ---------------------------------------------------------------- Entwurf 1
// Dunkle obere Hälfte mit Logo und Titel, helle untere mit den Angaben.
function entwurf1() {
  const schnitt = 980;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${B}" height="${H}" viewBox="0 0 ${B} ${H}">
    <rect width="${B}" height="${H}" fill="#FFFFFF"/>
    <rect width="${B}" height="${schnitt}" fill="${DUNKEL}"/>
    <rect y="${schnitt - 6}" width="${B}" height="6" fill="${GELB}"/>
    <image href="${alsBild(logoDunkel)}" x="${(B - 420) / 2}" y="150" width="420" height="140"/>
    <text x="${B / 2}" y="520" text-anchor="middle" font-family="${SCHRIFT}"
          font-size="150" font-weight="300" fill="#FFFFFF" letter-spacing="14">ZMAJ</text>
    <text x="${B / 2}" y="600" text-anchor="middle" font-family="${SCHRIFT}"
          font-size="46" font-weight="600" fill="${BLAU}" letter-spacing="6">BOSNISCH LERNEN</text>
    <line x1="${B / 2 - 160}" y1="660" x2="${B / 2 + 160}" y2="660" stroke="${GELB}" stroke-width="2"/>
    <text x="${B / 2}" y="740" text-anchor="middle" font-family="${SCHRIFT}"
          font-size="30" fill="#AAB6D8">Eine Android-Anwendung</text>
    <text x="${B / 2}" y="785" text-anchor="middle" font-family="${SCHRIFT}"
          font-size="30" fill="#AAB6D8">von der Idee bis zur Veröffentlichung</text>
    <text x="${B / 2}" y="880" text-anchor="middle" font-family="${SCHRIFT}"
          font-size="26" fill="#6B7BA8">Projektarbeit zur Weiterbildung</text>
    <text x="${B / 2}" y="920" text-anchor="middle" font-family="${SCHRIFT}"
          font-size="26" fill="#6B7BA8">zum staatlich geprüften Techniker</text>
    ${ANGABEN.map((z, i) => `<text x="${B / 2}" y="${1120 + i * 52}" text-anchor="middle"
        font-family="${SCHRIFT}" font-size="${i === 0 ? 40 : 27}"
        font-weight="${i === 0 ? 700 : 400}" fill="${i === 0 ? "#1A1A1A" : "#444444"}">${z}</text>`).join("")}
    <text x="${B / 2}" y="1660" text-anchor="middle" font-family="${SCHRIFT}"
          font-size="22" fill="#999999">Stand: 21.09.2026</text>
  </svg>`;
}

// ---------------------------------------------------------------- Entwurf 2
// Ganz dunkel, Titel links, das Telefon rechts angeschnitten.
function entwurf2() {
  const tw = 430, th = Math.round(tw * 2400 / 1080);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${B}" height="${H}" viewBox="0 0 ${B} ${H}">
    <defs>
      <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#101E44"/>
        <stop offset="60%" stop-color="${DUNKEL}"/>
        <stop offset="100%" stop-color="${TIEF}"/>
      </linearGradient>
      <clipPath id="rund"><rect x="${B - tw - 60}" y="520" width="${tw}" height="${th}" rx="34"/></clipPath>
    </defs>
    <rect width="${B}" height="${H}" fill="url(#g)"/>
    <image href="${alsBild(logoDunkel)}" x="90" y="110" width="360" height="120"/>
    <text x="90" y="470" font-family="${SCHRIFT}" font-size="132" font-weight="300"
          fill="#FFFFFF" letter-spacing="10">ZMAJ</text>
    <rect x="92" y="500" width="120" height="5" fill="${GELB}"/>
    <text x="90" y="580" font-family="${SCHRIFT}" font-size="40" font-weight="600"
          fill="${BLAU}" letter-spacing="4">BOSNISCH LERNEN</text>
    <text x="90" y="660" font-family="${SCHRIFT}" font-size="27" fill="#AAB6D8">Eine Android-Anwendung von</text>
    <text x="90" y="700" font-family="${SCHRIFT}" font-size="27" fill="#AAB6D8">der Idee bis zur Veröffentlichung</text>
    <image href="data:image/png;base64,${schirm.toString("base64")}"
           x="${B - tw - 60}" y="520" width="${tw}" height="${th}" clip-path="url(#rund)" opacity="0.92"/>
    <rect x="${B - tw - 60}" y="520" width="${tw}" height="${th}" rx="34"
          fill="none" stroke="#2A3A66" stroke-width="3"/>
    <line x1="90" y1="1320" x2="560" y2="1320" stroke="#2A3A66" stroke-width="2"/>
    ${ANGABEN.map((z, i) => `<text x="90" y="${1390 + i * 50}" font-family="${SCHRIFT}"
        font-size="${i === 0 ? 38 : 25}" font-weight="${i === 0 ? 700 : 400}"
        fill="${i === 0 ? "#FFFFFF" : "#8A97BE"}">${z}</text>`).join("")}
    <text x="90" y="1680" font-family="${SCHRIFT}" font-size="21" fill="#4A5680">Stand: 21.09.2026</text>
  </svg>`;
}

// ---------------------------------------------------------------- Entwurf 3
// Heller Bogen: schmaler Farbstreifen links, ruhiger Satz, Logo oben.
function entwurf3() {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${B}" height="${H}" viewBox="0 0 ${B} ${H}">
    <rect width="${B}" height="${H}" fill="#FFFFFF"/>
    <rect width="26" height="${H}" fill="${DUNKEL}"/>
    <rect x="26" width="8" height="${H}" fill="${GELB}"/>
    <image href="${alsBild(logoHell)}" x="130" y="150" width="400" height="133"/>
    <text x="130" y="620" font-family="${SCHRIFT}" font-size="140" font-weight="300"
          fill="${DUNKEL}" letter-spacing="12">ZMAJ</text>
    <text x="138" y="700" font-family="${SCHRIFT}" font-size="42" font-weight="600"
          fill="${BLAU}" letter-spacing="5">BOSNISCH LERNEN</text>
    <rect x="138" y="740" width="110" height="5" fill="${GELB}"/>
    <text x="138" y="820" font-family="${SCHRIFT}" font-size="29" fill="#555555">Eine Android-Anwendung von der Idee</text>
    <text x="138" y="862" font-family="${SCHRIFT}" font-size="29" fill="#555555">bis zur Veröffentlichung</text>
    <text x="138" y="960" font-family="${SCHRIFT}" font-size="25" fill="#888888">Projektarbeit zur Weiterbildung zum</text>
    <text x="138" y="998" font-family="${SCHRIFT}" font-size="25" fill="#888888">staatlich geprüften Techniker</text>
    <line x1="138" y1="1240" x2="700" y2="1240" stroke="#DDDDDD" stroke-width="2"/>
    ${ANGABEN.map((z, i) => `<text x="138" y="${1310 + i * 50}" font-family="${SCHRIFT}"
        font-size="${i === 0 ? 38 : 25}" font-weight="${i === 0 ? 700 : 400}"
        fill="${i === 0 ? "#1A1A1A" : "#555555"}">${z}</text>`).join("")}
    <text x="138" y="1680" font-family="${SCHRIFT}" font-size="21" fill="#AAAAAA">Stand: 21.09.2026</text>
  </svg>`;
}

// ---------------------------------------------------------------- Entwurf 4
// Die Mischung: der ruhige Aufbau von 1, das Telefon von 2. Das Gerät ragt
// über die Kante in den hellen Teil - das hält die beiden Hälften zusammen,
// statt sie nur übereinanderzulegen.
function entwurf4() {
  const schnitt = 1130;
  const tw = 340, th = Math.round(tw * 2400 / 1080);
  const tx = B - tw - 95, ty = 300;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${B}" height="${H}" viewBox="0 0 ${B} ${H}">
    <defs>
      <linearGradient id="g4" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#101E44"/>
        <stop offset="70%" stop-color="${DUNKEL}"/>
        <stop offset="100%" stop-color="${TIEF}"/>
      </linearGradient>
      <clipPath id="rund4"><rect x="${tx}" y="${ty}" width="${tw}" height="${th}" rx="28"/></clipPath>
      <filter id="schatten" x="-30%" y="-10%" width="170%" height="130%">
        <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#000000" flood-opacity="0.45"/>
      </filter>
    </defs>
    <rect width="${B}" height="${H}" fill="#FFFFFF"/>
    <rect width="${B}" height="${schnitt}" fill="url(#g4)"/>
    <rect y="${schnitt - 5}" width="${B}" height="5" fill="${GELB}"/>

    <image href="${alsBild(logoDunkel)}" x="95" y="105" width="345" height="115"/>

    <text x="95" y="500" font-family="${SCHRIFT}" font-size="128" font-weight="300"
          fill="#FFFFFF" letter-spacing="10">ZMAJ</text>
    <rect x="97" y="533" width="115" height="5" fill="${GELB}"/>
    <text x="95" y="608" font-family="${SCHRIFT}" font-size="38" font-weight="600"
          fill="${BLAU}" letter-spacing="4">BOSNISCH LERNEN</text>
    <text x="95" y="690" font-family="${SCHRIFT}" font-size="26" fill="#AAB6D8">Eine Android-Anwendung von der</text>
    <text x="95" y="728" font-family="${SCHRIFT}" font-size="26" fill="#AAB6D8">Idee bis zur Veröffentlichung</text>
    <text x="95" y="830" font-family="${SCHRIFT}" font-size="23" fill="#6B7BA8">Projektarbeit zur Weiterbildung zum</text>
    <text x="95" y="866" font-family="${SCHRIFT}" font-size="23" fill="#6B7BA8">staatlich geprüften Techniker</text>

    <g filter="url(#schatten)">
      <image href="data:image/png;base64,${schirm.toString("base64")}"
             x="${tx}" y="${ty}" width="${tw}" height="${th}" clip-path="url(#rund4)"/>
      <rect x="${tx}" y="${ty}" width="${tw}" height="${th}" rx="28"
            fill="none" stroke="#3A4A78" stroke-width="3"/>
    </g>

    ${ANGABEN.map((z, i) => `<text x="95" y="${1330 + i * 52}" font-family="${SCHRIFT}"
        font-size="${i === 0 ? 40 : 26}" font-weight="${i === 0 ? 700 : 400}"
        fill="${i === 0 ? "#1A1A1A" : "#444444"}">${z}</text>`).join("")}
    <text x="95" y="1672" font-family="${SCHRIFT}" font-size="21" fill="#999999">Stand: 21.09.2026</text>
  </svg>`;
}

/* Entwurf 4 ein zweites Mal - aber OHNE Schrift.
   Das ist der Hintergrund für die Word-Fassung: Farbflächen, Logo, Telefon,
   Striche. Die Schrift kommt in Word obendrauf und bleibt dadurch echter
   Text - markierbar, durchsuchbar, änderbar. Ein Deckblatt, das nur ein
   Bild ist, kann niemand mehr korrigieren, ohne dieses Skript zu haben. */
function entwurf4Hintergrund() {
  const svg = entwurf4();
  // Jedes <text>-Element herausnehmen. Die Striche und Flächen bleiben.
  return svg.replace(/<text[\s\S]*?<\/text>/g, "");
}

const alle = [["entwurf-1", entwurf1()], ["entwurf-2", entwurf2()],
              ["entwurf-3", entwurf3()], ["entwurf-4", entwurf4()],
              ["entwurf-4-hintergrund", entwurf4Hintergrund()]];

(async () => {
  fs.mkdirSync(path.join(HIER, "entwuerfe"), { recursive: true });
  for (const [name, svg] of alle) {
    const ziel = path.join(HIER, "entwuerfe", name + ".png");
    await sharp(Buffer.from(svg)).png().toFile(ziel);
    fs.writeFileSync(path.join(HIER, "entwuerfe", name + ".svg"), svg);
    console.log(name + ".png geschrieben");
  }
})();
