// Rechnet die Zeiterfassung für Abschnitt 5.6 aus den Sitzungsprotokollen neu
// und sagt, welche Zahlen in kapitel5.json nicht mehr stimmen.
//
//   node zeiterfassung.js
//
// Warum es das gibt: Solange am Projekt gearbeitet wird, wachsen die
// Protokolle weiter. Jede Zahl in 5.6 - Stunden, Zeitstempel, Lücken - ist
// deshalb ein Stand, kein Endwert. Von Hand nachgepflegt wäre sie nach der
// ersten Woche falsch, ohne dass es jemand merkt. Vor der Abgabe einmal
// laufen lassen und die gemeldeten Abweichungen eintragen.
//
// Die Protokolle liegen ausserhalb des Projekts, unter
// %USERPROFILE%\.claude\projects. Sie gehören niemandem sonst und werden
// hier nur gelesen.

const fs = require("fs");
const os = require("os");
const path = require("path");

const PAUSE = 30;                    // Minuten - so steht es in 5.6
const VERSATZ = 2 * 3600 * 1000;     // MESZ = UTC+2 (gilt bis 25.10.2026)

/* Liest die Zeitstempel einer Protokolldatei, ohne sie ganz in den Speicher
   zu holen. Node bricht bei Zeichenketten ueber rund 512 MB mit
   ERR_STRING_TOO_LONG ab, und eine Sitzungsdatei hier ist 670 MB gross.
   Gelesen wird deshalb in Stuecken mit kleiner Ueberlappung, damit kein
   Zeitstempel an einer Stueckgrenze zerrissen wird. latin1 statt utf8,
   weil nur ASCII gesucht wird - das spart die Mehrbyte-Behandlung. */
const STUECK = 8 * 1024 * 1024;
const RAND = 64;                     // laenger als '"timestamp":"…"'

const zeitstempelAus = (datei, hinein) => {
  const fd = fs.openSync(datei, "r");
  const puffer = Buffer.allocUnsafe(STUECK);
  let rest = "", gelesen = 0, roh = 0;
  try {
    for (;;) {
      const n = fs.readSync(fd, puffer, 0, STUECK, gelesen);
      if (n <= 0) break;
      gelesen += n;
      const text = rest + puffer.toString("latin1", 0, n);
      const re = /"timestamp":"[^"]*"/g;
      let m;
      while ((m = re.exec(text)) !== null) {
        /* Treffer, die ganz im uebernommenen Rand liegen, wurden im
           vorigen Stueck schon gezaehlt - sonst waere die Gesamtzahl
           zu hoch. Nur was in die neuen Daten hineinreicht, zaehlt. */
        if (m.index + m[0].length <= rest.length) continue;
        roh++;
        const ms = Date.parse(m[0].slice(13, -1));
        if (Number.isFinite(ms)) hinein.add(ms);
      }
      rest = text.slice(-RAND);
    }
  } finally {
    fs.closeSync(fd);
  }
  return roh;
};

/* Nur die Projekte, in denen an Zmaj gearbeitet wurde. Der Ordnername ist
   der Pfad mit Bindestrichen; "Desktop-Bosnisch-Lernapp" ist der alte Ort,
   bevor der Ordner nach "App Zeugs" verschoben wurde. */
const PROJEKTE = [
  "C--Users-Ajdin-Desktop-Bosnisch-Lernapp",
  "C--Users-Ajdin-Desktop-Bosnisch-Lernapp-web",
  "C--Users-Ajdin-Desktop-App-Zeugs",
  "C--Users-Ajdin-Desktop-App-Zeugs-Bosnisch-Lernapp",
  "C--Users-Ajdin-Desktop-App-Zeugs-Bosnisch-Lernapp-mappe",
];

/* Nur die Hauptsitzungen, nicht die Unteragenten. Ein Unteragent läuft
   innerhalb einer Hauptsitzung; seine Zeitstempel liegen also schon in
   deren Block und würden nichts hinzufügen - ausser dem falschen Eindruck,
   es sei mehr passiert. */
const hauptsitzungen = () => {
  const wurzel = path.join(os.homedir(), ".claude", "projects");
  const raus = [];
  for (const p of PROJEKTE) {
    const ordner = path.join(wurzel, p);
    if (!fs.existsSync(ordner)) continue;
    for (const d of fs.readdirSync(ordner)) {
      if (d.endsWith(".jsonl")) raus.push(path.join(ordner, d));
    }
  }
  return raus;
};

const dateien = hauptsitzungen();
if (!dateien.length) {
  console.error("Keine Sitzungsprotokolle gefunden. Pfade in PROJEKTE prüfen.");
  process.exit(1);
}

let roh = 0;
const menge = new Set();
for (const f of dateien) roh += zeitstempelAus(f, menge);
const ms = [...menge].sort((a, b) => a - b);

// ------------------------------------------------------------ Arbeitsblöcke
const bloecke = [];
let start = ms[0], letzt = ms[0];
for (let i = 1; i < ms.length; i++) {
  if (ms[i] - letzt > PAUSE * 60000) { bloecke.push([start, letzt]); start = ms[i]; }
  letzt = ms[i];
}
bloecke.push([start, letzt]);

const tag = (t) => new Date(t + VERSATZ).toISOString().slice(0, 10);
const uhr = (t) => new Date(t + VERSATZ).toISOString().slice(11, 16);

// Ein Block über Mitternacht zählt anteilig zu beiden Tagen.
const tage = new Map();
for (const [a, b] of bloecke) {
  let von = a;
  for (;;) {
    const t = tag(von);
    const mitternacht = Date.parse(t + "T00:00:00.000Z") - VERSATZ + 86400000;
    const bis = Math.min(b, mitternacht - 1);
    tage.set(t, (tage.get(t) || 0) + (bis - von));
    if (b <= bis) break;
    von = bis + 1;
  }
}

// --------------------------------------------------- Lücken und Empfindlichkeit
const luecken = [];
for (let i = 1; i < ms.length; i++) {
  const d = (ms[i] - ms[i - 1]) / 60000;
  if (d > 5 && d <= PAUSE) luecken.push(d);       // Stille INNERHALB der Blöcke
}
const stille = luecken.reduce((a, b) => a + b, 0) / 60;

const alleLuecken = [];
for (let i = 1; i < ms.length; i++) {
  const d = (ms[i] - ms[i - 1]) / 60000;
  if (d > 5) alleLuecken.push(d);
}
const zwischen = (u, o) => alleLuecken.filter((d) => d >= u && d < o).length;

const beiSchwelle = (p) => {
  let s = 0, a = ms[0], l = ms[0];
  for (let i = 1; i < ms.length; i++) { if (ms[i] - l > p * 60000) { s += l - a; a = ms[i]; } l = ms[i]; }
  return (s + l - a) / 3600000;
};

const summe = [...tage.values()].reduce((a, b) => a + b, 0) / 3600000;

/* ---------------------------------------------- Überschneidung mit anderem
   Am 14.09.2026 lief parallel eine Sitzung zum SPS-Schulprojekt. Deren Zeit
   liegt innerhalb gezählter Zmaj-Blöcke und gehört nicht zum Projekt. Das
   fiel erst bei einer Gegenprüfung auf; ohne diese Rechnung wäre die Summe
   um anderthalb Stunden zu hoch geblieben. Deshalb prüft das Skript es nun
   bei jedem Lauf mit. */
const FREMD = "C--Users-Ajdin-AppData-Roaming-Claude-scratch-workspaces-";
const fremdZeiten = () => {
  const wurzel = path.join(os.homedir(), ".claude", "projects");
  const raus = new Set();
  if (!fs.existsSync(wurzel)) return [];
  for (const p of fs.readdirSync(wurzel)) {
    if (!p.startsWith(FREMD)) continue;
    const stapel = [path.join(wurzel, p)];
    while (stapel.length) {
      const o = stapel.pop();
      for (const d of fs.readdirSync(o, { withFileTypes: true })) {
        const voll = path.join(o, d.name);
        if (d.isDirectory()) stapel.push(voll);
        else if (d.name.endsWith(".jsonl")) zeitstempelAus(voll, raus);
      }
    }
  }
  return [...raus].sort((a, b) => a - b);
};

const fremd = fremdZeiten();
let ueberschneidung = 0;
const fenster = [];
if (fremd.length) {
  const fb = [];
  let fa = fremd[0], fl = fremd[0];
  for (let i = 1; i < fremd.length; i++) {
    if (fremd[i] - fl > PAUSE * 60000) { fb.push([fa, fl]); fa = fremd[i]; }
    fl = fremd[i];
  }
  fb.push([fa, fl]);
  for (const [s1, s2] of fb) for (const [z1, z2] of bloecke) {
    const u = Math.max(s1, z1), o = Math.min(s2, z2);
    if (o > u) { ueberschneidung += o - u; fenster.push([u, o]); }
  }
}

// ----------------------------------------------------------------- Ausgabe
console.log("Protokolldateien:  " + dateien.length);
console.log("Zeitstempel:       " + roh.toLocaleString("de-DE") + " (davon " + ms.length.toLocaleString("de-DE") + " verschiedene)");
console.log("Letzter Eintrag:   " + tag(ms[ms.length - 1]).split("-").reverse().join(".") + ", " + uhr(ms[ms.length - 1]) + " Uhr");
console.log();
console.log("Tag           Stunden");
[...tage.entries()].sort().forEach(([t, v]) => {
  const [j, m, d] = t.split("-");
  console.log(`${d}.${m}.${j}    ${(v / 3600000).toFixed(1).padStart(5)}`);
});
console.log("-".repeat(22));
console.log(`${tage.size} Tage        ${summe.toFixed(1).padStart(5)}   (Schnitt ${(summe / tage.size).toFixed(1)} h)`);
console.log();
console.log("Schwelle   Stunden");
[5, 15, 30, 60].forEach((p) => console.log(String(p).padStart(3) + " min    " + beiSchwelle(p).toFixed(1)));
console.log();
console.log("Lücken über 5 min: " + alleLuecken.length
  + "   (5-15: " + zwischen(5, 15) + ", 15-30: " + zwischen(15, 30)
  + ", 30-60: " + zwischen(30, 60) + ", über 60: " + zwischen(60, 1e9) + ")");
console.log("Stille in den Blöcken: " + stille.toFixed(1) + " h = "
  + (stille / summe * 100).toFixed(1) + " % von " + summe.toFixed(1) + " h, "
  + luecken.length + " Lücken");
console.log();
if (ueberschneidung > 0) {
  console.log("Parallel an einem anderen Projekt: " + (ueberschneidung / 3600000).toFixed(2) + " h");
  fenster.sort((a, b) => a[0] - b[0]).forEach(([u, o]) =>
    console.log("   " + tag(u).split("-").reverse().join(".") + "  " + uhr(u) + "-" + uhr(o)
      + "   " + Math.round((o - u) / 60000) + " min"));
  console.log("Auf das Projekt entfallen damit: " + (summe - ueberschneidung / 3600000).toFixed(1) + " h");
} else {
  console.log("Keine Überschneidung mit anderen Projekten gefunden.");
}

// ------------------------------------------- Abgleich mit dem, was in 5.6 steht
const K5 = path.join(__dirname, "kapitel5.json");
if (fs.existsSync(K5)) {
  const text = JSON.stringify(JSON.parse(fs.readFileSync(K5, "utf8")).kapitel5);
  const soll = [
    ["Zeitstempel", roh.toLocaleString("de-DE")],
    ["Summe Stunden", summe.toFixed(1).replace(".", ",")],
    ["Arbeitstage", String(tage.size)],
    ["Schwelle 15 min", beiSchwelle(15).toFixed(1).replace(".", ",")],
    ["Schwelle 60 min", beiSchwelle(60).toFixed(1).replace(".", ",")],
    ["Stille in Prozent", (stille / summe * 100).toFixed(1).replace(".", ",")],
    ["Lücken über 5 min", String(alleLuecken.length)],
  ];
  console.log();
  const fehlt = soll.filter(([, wert]) => !text.includes(wert));
  if (!fehlt.length) {
    console.log("kapitel5.json: alle geprüften Zahlen stimmen noch.");
  } else {
    console.log("kapitel5.json: diese Werte stehen dort NICHT mehr so drin —");
    fehlt.forEach(([was, wert]) => console.log("   " + was.padEnd(20) + "jetzt: " + wert));
  }
}
