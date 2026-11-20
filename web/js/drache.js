/* ---- Maskottchen Zmaj (Drache, wie die Nationalelf „Zmajevi“) ---- */
let MASCOT = new Set();   // Dateien in web/maskottchen
/* Reihenfolge: 1. Lottie-Animation zmaj.json (Skelett, Keyframes, echte Bewegung)
                2. Bilder zmaj-frei/-jubel/-traurig.png (Bewegung per CSS)
                3. Vektor-Ersatz */
/* Lottie-Dateien: zmaj.json (alle Zustände per Marker) oder je Zustand eine eigene Datei
   zmaj-idle.json, zmaj-cheer.json, zmaj-sad.json, zmaj-ok.json, zmaj-no.json, zmaj-cry.json
   (z. B. von LottieFiles). Fehlt eine Zustandsdatei, wird zmaj.json genommen. */
const hasLottie = () => !!window.lottie && MASCOT.has('zmaj.json');
/* ---- Zierrat aufsetzen ----
   Bis zum 18.09.2026 war jedes Schmuckstück eine eigene, vollständige
   Animationsdatei mit rund 75 KB. Deshalb konnte der Drache immer nur eines
   tragen: mehr hätte für jede Kombination eine weitere Datei bedeutet.
   Jetzt liegt neben der Grunddatei je Stück nur noch seine Ebene
   (zmajz-<id>.json, zwei bis sieben Kilobyte). Sie werden hier angehängt und
   nach `ind` sortiert – das ist genau die Reihenfolge, die zmaj_lottie.py in
   ORDER festgelegt hat, also liegt der Hut vorn und der Schal hinter dem Kopf.
   Jede Kombination kostet damit keine einzige Datei extra. */
/* ---- Die Farbe des Drachen ----
   Der Drache besteht aus fuenf Blautoenen: Koerper, Aufhellung, Dunkel,
   Fluegelhaut, Fluegelschatten. Eine andere Farbe heisst: diese fuenf gegen
   fuenf andere tauschen, in derselben Reihenfolge und mit demselben
   Helligkeitsgefaelle - sonst verliert die Figur ihre Plastik.
   Seit dem Drachen v6 (14.10.2026, neue Figur nach den Vorlagen) ist
   "Dunkel" auch der UMRISS der ganzen Figur, dazu Brauen, Mund und
   Nasenloecher - darum muss der dritte Ton jeder Farbe richtig dunkel sein.
   Gelb bleibt ueberall stehen: Bauch und Hoerner. Das ist der Gegenpol,
   an dem man den Drachen erkennt. Die Augen sind blau und faerben nie um.
   Die Zahlen sind dieselben wie in zmaj_lottie.py. Wer sie dort aendert,
   muss FARB_QUELLE hier mitaendern. */
const zuFarbe = h => [parseInt(h.slice(0, 2), 16) / 255,
                      parseInt(h.slice(2, 4), 16) / 255,
                      parseInt(h.slice(4, 6), 16) / 255];
/* Dazu seit dem 01.10.2026 die drei Gelbtoene als Nummer 6 bis 8 - seit
   v6: Bauch und Hoerner, Bauchrillen und Schatten auf Gold, Umriss der
   Hoerner. Getauscht wird nur, was eine Farbe auch angibt: die Kauffarben
   haben fuenf Toene und lassen Gelb stehen, das Skelett hat acht und macht
   auch die Hoerner zu Knochen.
   v6-Werte, abgemessen an der Vorlage pro_vorne.png (14.10.2026); bis v5
   stand hier 2448B8, 3F66DF, 17307F, 6C90FF, 3A5CD0, FFCB1F, D9A400, F2A900. */
const FARB_QUELLE = ['415EA1', '5281B3', '26366A', '7E9CDF', '6282CC', 'F6C044', 'D79536', 'A86D27'].map(zuFarbe);
/* v6 (14.10.2026): Der fuenfte Ton, der Fluegelschatten, liegt jetzt
   zwischen Koerper und Fluegelhaut (60 % zur Haut hin) wie beim blauen
   Drachen der Vorlage. Vorher war er fast so dunkel wie der Koerper - bei
   der neuen Figur verschwanden damit die Fingerknochen der Fluegel, die die
   Koerperfarbe tragen, im Schatten der Haut. Rosa und Silber haben einen
   dunkleren dritten Ton bekommen, weil der jetzt der Umriss ist. */
const FARBEN = {
  gruen:   ['1E9E52', '32C169', '136434', '62DE98', '47C47C'],
  rosa:    ['D94E8C', 'EE74A8', '7E2450', 'FF9CC4', 'F07DAE'],
  rot:     ['C0392B', 'E05A4A', '7E1C14', 'FF8878', 'E66859'],
  lila:    ['7A3FBF', '9C63DB', '4A2277', 'BE8DF0', 'A36EDC'],
  nacht:   ['3A3F4C', '575E70', '22252D', '7C8598', '62697A'],
  /* Nur mit der Vollversion. Die fuenf Toene stehen fuer dieselben fuenf
     Blautoene wie bei den anderen Farben: Grund, hell, dunkel, Fluegel,
     Fluegelschatten. */
  gold:    ['D9A520', 'F2C94C', '8A6508', 'FFDE7A', 'F0C756'],
  silber:  ['9AA3B0', 'C3CAD6', '4D5563', 'E2E7EF', 'C5CCD6'],
  kupfer:  ['B06A2C', 'D08C45', '7A4417', 'E8A867', 'D28F4F'],
  /* Die Galaxie ist mehr als eine Farbe: zu diesen fuenf dunklen Toenen
     gehoert die Ebene zmajz-galaxie.json mit den Sternen darauf. Weil
     die Kennung in beiden Listen steht - hier und im Laden -, laedt
     getrageneTeile() sie von selbst mit. */
  galaxie: ['241A4D', '3A2C73', '150F30', '4C3C93', '3A2D74'],
  /* Kein Kaufartikel: die Haut des Skelett-Drachen zu Halloween. Acht
     Toene - knochenweiss, die Fluegelhaut dunkel (sie wird ohnehin
     geleert), dazu die drei Gelbtoene. v6: der dritte und der achte Ton
     sind dunkler (8E846C, 8A7F66), denn sie sind jetzt die Umrisse von
     Schaedel und Hoernern - hell auf hell verschwand der Schaedel. */
  skelett: ['E6DFCB', 'F6F1E4', '8E846C', '4A465C', '2C2A38', 'D6CCB0', 'A99F84', '8A7F66'],
};
/* hasOwnProperty: FARBEN['constructor'] waere sonst die eingebaute Funktion
   Object, und .map darauf wirft - der Drache bliebe leer. 04.10.2026. */
const farbeVon = id => (Object.prototype.hasOwnProperty.call(FARBEN, id) ? FARBEN[id] : []).map(zuFarbe);
/* Alle Farbwerte in den Daten durchgehen und die fuenf Blautoene ersetzen.
   Farben stehen in Lottie als {a:0, k:[r,g,b,a]} - vier Zahlen. Positionen
   haben zwei oder drei, Groessen drei; ein Feld mit vier Zahlen ist also
   praktisch immer eine Farbe, und getauscht wird ohnehin nur, was genau
   einem der fuenf Toene entspricht. Die Deckkraft (k[3]) bleibt stehen,
   sonst verschwaenden die halbdurchsichtigen Aufhellungen. */
function faerbe(daten, palette){
  const nah = (a, b) => Math.abs(a - b) < 0.004;
  const geh = x => {
    if(Array.isArray(x)){ x.forEach(geh); return; }
    if(!x || typeof x !== 'object') return;
    if(x.a === 0 && Array.isArray(x.k) && x.k.length === 4){
      for(let i = 0; i < Math.min(FARB_QUELLE.length, palette.length); i++){
        const q = FARB_QUELLE[i];
        if(nah(x.k[0], q[0]) && nah(x.k[1], q[1]) && nah(x.k[2], q[2])){
          x.k = [palette[i][0], palette[i][1], palette[i][2], x.k[3]];
          return;
        }
      }
    }
    for(const s in x) geh(x[s]);
  };
  geh(daten);
  return daten;
}

let zmajBasis = null;              // Grunddatei, einmal geholt
const zmajTeile = new Map();       // id -> Ebene, einmal geholt
let zmajFertig = null, zmajFertigFuer = null;
const zierratDatei = id => 'zmajz-' + id + '.json';
/* Bildsatz einer Hautfarbe: nur, wenn web/maskottchen/haut/<farbe>/ alle
   Teile hat (maskottchen_bilder() in inhalt.py meldet ihn dann als
   "haut/<farbe>/"). Sonst '' - der Drache bleibt in der Grundfarbe. */
const hautSatz = farbe => (farbe && MASCOT.has('haut/' + farbe + '/')) ? farbe : '';
/* Auch hier die Ausnahme fuer die Stuecke der Vollversion: sie stehen in
   keinem Besitz, weil sie nicht gekauft werden. Ohne sie haengt der
   Umhang zwar in getragen, kommt aber nie an den Drachen. hatStueck statt
   besitz.has: sonst kaeme ein freigeschalteter Hut nie an den Drachen,
   und nach dem Ausschalten faellt er wieder ab (20.10.2026). */
function getrageneTeile(){
  return getragenListe()
    .filter(id => (hatStueck(id) || istVollStueck(id)) && MASCOT.has(zierratDatei(id)));
}
// Welche Farbe getragen wird. Leer heisst blau, die Grundfarbe.
/* Die Farbe der Vollversion steht in keinem Besitz - sie wird nicht
   gekauft. Ohne diese Ausnahme blieb der Drache blau, obwohl Gold
   getragen war. Beim Bauen in der Vorschau aufgefallen, 29.09.2026. */
const getrageneFarbe = () => getragenListe()
  .find(id => FARBEN[id] && (hatStueck(id) || istVollStueck(id))) || '';
/* Ohne Vorgabe zeigt der Drache, was der Nutzer wirklich traegt. Mit
   Vorgabe zeigt er etwas anderes - gebraucht wird das genau einmal, im
   Kaufkasten: dort steht er in voller Montur, damit man sieht, was man
   bekommt, statt es zu lesen. Die Vorschau wird nicht zwischengelagert,
   sonst verdraengt sie den echten Drachen aus dem Speicher. */
/* =================== FESTTAGE ===================
   Eingebaut am 01.10.2026. Ajdin: "das Weihnachtslayout bis zum 07.01
   laufen lassen und das gleiche mit Ostern, Halloween erst naechstes Jahr,
   Bajram zweimal". Und: "wenn mal der Fall kommt, dass Bajram mit einem
   anderen Feiertag kollidiert, dann soll er jeden Tag wechseln - ich denke,
   das ist fair fuer alle."

   Zeitraeume (jeweils einschliesslich):
     Weihnachten  1. Dezember bis 7. Januar - Weihnachten, Neujahr und das
                  orthodoxe Weihnachten am 7. Januar
     Ostern       je Palmsonntag bis Ostermontag, katholisch und orthodox
                  (seit 13.11.2026). Fallen beide zusammen, sind es 9 Tage,
                  liegen sie eine Woche auseinander 16, sonst zwei getrennte
                  Wochen.
     Bajram       Ramazanski drei Tage, Kurban vier Tage, ab dem ersten Tag
                  laut Islamischer Gemeinschaft in BiH. Bajram wandert jedes
                  Jahr um elf Tage nach vorn und laesst sich nicht wie
                  Ostern ausrechnen - deshalb eine Tabelle. Sie reicht bis
                  2036 und muss dann verlaengert werden.
     Halloween    24. bis 31. Oktober, erst ab 2027
   Sind zwei Feste zugleich dran, wechseln sie sich taeglich ab.

   Das Kostuem zieht der Drache von selbst an, kostenlos, und legt es nach
   dem Fest wieder ab. Getragenes bleibt gespeichert wie es ist - das
   Festteil verdeckt nur fuer die Festtage, was in seiner Gruppe sitzt.
   Im Kaufkasten der Vollversion bleibt der Drache in voller Montur. */
const BAJRAM = [
  /* Erster Tag und Dauer. Recherchiert am 01.10.2026 aus zwei getrennten
     Quellen - Diyanet (dieselbe Rechnung wie die Islamische Gemeinschaft
     in BiH, Istanbuler Kriterium 2016) und bosnische Seiten - und
     gegeneinander geprueft. 2033 faellt Ramazanski zweimal ins Jahr. */
  ['2027-03-09', 3],   // Ramazanski
  ['2027-05-16', 4],   // Kurban
  ['2028-02-26', 3],   // Ramazanski
  ['2028-05-05', 4],   // Kurban
  ['2029-02-14', 3],   // Ramazanski
  ['2029-04-24', 4],   // Kurban
  ['2030-02-04', 3],   // Ramazanski
  ['2030-04-13', 4],   // Kurban
  ['2031-01-24', 3],   // Ramazanski
  ['2031-04-02', 4],   // Kurban
  ['2032-01-14', 3],   // Ramazanski
  ['2032-03-22', 4],   // Kurban
  ['2033-01-02', 3],   // Ramazanski
  ['2033-03-11', 4],   // Kurban
  ['2033-12-23', 3],   // Ramazanski
  ['2034-03-01', 4],   // Kurban
  ['2034-12-12', 3],   // Ramazanski
  ['2035-02-18', 4],   // Kurban
  ['2035-12-01', 3],   // Ramazanski
  ['2036-02-07', 4],   // Kurban   // unsicher: 07. oder 08.02., Diyanet hat 2036 noch nicht veroeffentlicht
  ['2036-11-19', 3],   // Ramazanski
];
const FEST_GRUPPE = {hexenhut: 'kopf', nikolausmuetze: 'kopf', bajramfes: 'kopf', hasenohren: 'kopf',
                     jelek: 'hals', skelett: 'farbe'};
const tagNr = (j, m, d) => Math.round(Date.UTC(j, m - 1, d) / 864e5);
const heuteNr = () => { const d = new Date(); return tagNr(d.getFullYear(), d.getMonth() + 1, d.getDate()); };
/* Ostersonntag nach dem gregorianischen Kalender (Gauss, in der Form von
   Meeus). Geprueft gegen 2026 bis 2036. */
function osternWest(j){
  const a = j % 19, b = Math.floor(j / 100), c = j % 100, d = Math.floor(b / 4), e = b % 4;
  const f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451);
  const n = h + l - 7 * m + 114;
  return tagNr(j, Math.floor(n / 31), n % 31 + 1);
}
/* Orthodoxes Ostern: julianisch gerechnet, dann 13 Tage auf den heutigen
   Kalender - das stimmt von 1900 bis 2099. */
function osternOst(j){
  const a = j % 4, b = j % 7, c = j % 19, d = (19 * c + 15) % 30, e = (2 * a + 4 * b - d + 34) % 7;
  const n = d + e + 114;
  return tagNr(j, Math.floor(n / 31), n % 31 + 1) + 13;
}
function festZeiten(j){
  const z = [{id: 'weihnachten', von: tagNr(j, 12, 1), bis: tagNr(j + 1, 1, 7)}];
  /* Ostern: je eine Woche um jedes Ostern, Palmsonntag bis Ostermontag,
     katholisch und orthodox. Ajdin, 13.11.2026: "mach kuerzen ostern" -
     vorher lief es vom katholischen Palmsonntag bis zum orthodoxen
     Ostermontag am Stueck, 2027 waeren das 44 Tage gewesen. Liegen beide
     Wochen aneinander oder ueberlappen sie, wird ein Zeitraum daraus
     (2026: 29.03.-13.04.); sonst sind es zwei (2027: 21.-29.03. und
     25.04.-03.05.), dazwischen gibt es kein Osterkostuem. */
  const ow = osternWest(j), oo = osternOst(j);
  if(oo - 7 <= ow + 2) z.push({id: 'ostern', von: ow - 7, bis: oo + 1});
  else z.push({id: 'ostern', von: ow - 7, bis: ow + 1}, {id: 'ostern', von: oo - 7, bis: oo + 1});
  if(j >= 2027) z.push({id: 'halloween', von: tagNr(j, 10, 24), bis: tagNr(j, 10, 31)});
  BAJRAM.forEach(([tag, dauer]) => {
    const [y, m, d] = tag.split('-').map(Number);
    if(y === j) z.push({id: 'bajram', von: tagNr(y, m, d), bis: tagNr(y, m, d) + dauer - 1});
  });
  return z;
}
/* Welches Fest heute dran ist, oder ''. zmaj_fest_probe setzt niemand in
   der App - nur wer am Geraet nachsehen will, wie ein Fest aussieht, ueber
   die Fernwartung. */
function festHeute(){
  try{ const p = localStorage.getItem('zmaj_fest_probe'); if(p && Object.prototype.hasOwnProperty.call(FESTE, p)) return p; }catch(e){}
  const n = heuteNr(), j = new Date().getFullYear();
  /* Zwei zugleich: taeglich abwechselnd, und zwar ab dem Tag, an dem das
     zweite dazukommt - mit diesem zuerst. Laeuft Weihnachten schon seit
     Wochen und kommt Bajram fuer drei Tage dazu, ist es dann Bajram,
     Weihnachten, Bajram und nicht umgekehrt. */
  const aktiv = festZeiten(j - 1).concat(festZeiten(j)).filter(z => z.von <= n && n <= z.bis)
    .sort((a, b) => b.von - a.von || a.bis - b.bis);   // gleicher Beginn: das kuerzere zuerst
  return aktiv.length ? aktiv[(n - aktiv[0].von) % aktiv.length].id : '';
}
/* Was der Drache heute wirklich anhat: das Getragene, ueber das sich zu
   einem Fest das Festkostuem legt. Ein Festteil ersetzt das Stueck aus
   derselben Gruppe. Das Skelett hat keinen Koerper mehr, darauf saesse
   keine Weste - deshalb faellt dann auch die Halsgruppe weg. */
function festTracht(){
  const ids = getrageneTeile(), farbe = getrageneFarbe();
  const f = FESTE[festHeute()];
  const neu = f ? f.teile.filter(id => MASCOT.has(zierratDatei(id))) : [];
  if(!neu.length) return {ids, farbe};
  const weg = new Set(neu.map(id => FEST_GRUPPE[id]));
  if(f.farbe) weg.add('hals');
  return {ids: ids.filter(id => !weg.has(gruppeVon(id))).concat(neu), farbe: f.farbe || farbe};
}

/* ---- Schmuck auf der Startseite ----
   Oben eine Girlande (an Bajram die Baščaršija bei Nacht), unter Serie und
   Drache ein Gruss: oben bosnisch, darunter in der Sprache der App. Dazu
   fallende Blaetter oder Flocken. Gezeichnet auf 330 Punkte Breite; die
   Bilder skalieren mit, ohne sich zu verziehen.
   Entworfen in drei Runden mit Ajdin, 01.10.2026: Schneehauben auf den
   Knoepfen und Eiszapfen sind wieder raus, die Haeuser an Bajram sind
   bosnische Altstadthaeuser, die Tulpen zu Ostern haben oben Luft. */
const festSvgUrl = s => "url('data:image/svg+xml," + encodeURIComponent(s).replace(/'/g, '%27') + "')";
const FW = 330;
const festSchnur = d => '<path d="M0,6 Q' + (FW / 2) + ',' + d + ' ' + FW + ',6" stroke="#9AA0C8" stroke-width="2" fill="none"/>';
function festHaenger(n, fn){
  let s = '';
  for(let i = 0; i < n; i++){
    const x = 16 + i * (FW - 32) / (n - 1);
    const y = 6 + 26 * (1 - Math.pow((x - FW / 2) / (FW / 2), 2)) * 0.55;
    s += '<line x1="' + x + '" y1="' + y + '" x2="' + x + '" y2="' + (y + 8) + '" stroke="#9AA0C8" stroke-width="1.4"/>' + fn(x, y + 8, i);
  }
  return s;
}
const festBild = (h, innen) => '<svg class="festgirlande festteil" aria-hidden="true" viewBox="0 0 ' + FW + ' ' + h + '" width="100%">' + innen + '</svg>';
const festBlatt = (c, r) => '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 24 24"><g transform="rotate(' + r + ')"><path d="M0,-11 L3,-5 L9,-7 L6,-1 L11,2 L5,4 L6,10 L0,6 L-6,10 L-5,4 L-11,2 L-6,-1 L-9,-7 L-3,-5Z" fill="' + c + '"/><path d="M0,-8 V11" stroke="#7A3B14" stroke-width="1.2"/></g></svg>';

function festHalloween(){
  const oben = festBild(70, festSchnur(34) + festHaenger(7, (x, y, i) => i % 2
    ? '<g transform="translate(' + x + ',' + (y + 9) + ')"><path d="M-16,-2 Q-8,-12 0,-3 Q8,-12 16,-2 Q9,0 7,7 Q3,2 0,7 Q-3,2 -7,7 Q-9,0 -16,-2Z" fill="#6E5B9A"/><circle cx="-3.5" cy="-1" r="1.6" fill="#FFB347"/><circle cx="3.5" cy="-1" r="1.6" fill="#FFB347"/></g>'
    : '<g transform="translate(' + x + ',' + (y + 12) + ')"><ellipse rx="14" ry="12" fill="#F28C28"/><ellipse rx="5.5" ry="12" fill="#E07A12"/><rect x="-2" y="-16" width="4" height="6" rx="2" fill="#4E7A2E"/><path d="M-7,-3 l3.5,-4 l3.5,4Z M0.5,-3 l3.5,-4 l3.5,4Z M-7,4 l2,2 l2,-2 l2,2 l2,-2 l2,2 l2,-2" fill="#3B1F0A" stroke="#3B1F0A" stroke-width="1"/></g>'));
  const farben = ['#E8742A', '#C8452B', '#E9A23B', '#B5651D', '#D9532B'];
  let fall = '';
  /* Sechs Blaetter. Zehn waren einer Testerin zu viele ("bisschen zu viele
     Blaetter, aber sonst top"), 01.10.2026. */
  for(let i = 0; i < 6; i++){
    const x = (i * 53 + 11) % 100, d = 9 + (i % 4) * 2.5, verz = -(i * 2.6), g = 16 + (i % 3) * 6;
    fall += '<i style="left:' + x + '%;width:' + g + 'px;height:' + g + 'px;background-image:' + festSvgUrl(festBlatt(farben[i % 5], i * 40))
      + ';animation-name:festFallen,festWiegen;animation-timing-function:linear,ease-in-out;animation-duration:' + d + 's,' + (d / 3) + 's;animation-delay:' + verz + 's,' + verz + 's"></i>';
  }
  return {oben, fall, css: `.festgruss{background-image:${festSvgUrl(festBlatt('#E8742A', 20))},${festSvgUrl(festBlatt('#C8452B', -30))}; background-repeat:no-repeat; background-size:26px,20px; background-position:right 10px top 8px, right 34px bottom 8px}`};
}

function festWeihnachten(){
  const lichter = ['#E8474B', '#F5C518', '#4CCB84', '#6C90FF'];
  const oben = festBild(62, festSchnur(30) + festHaenger(11, (x, y, i) =>
    '<g transform="translate(' + x + ',' + (y - 2) + ')"><rect x="-3" y="-4" width="6" height="5" rx="1" fill="#9AA0C8"/><ellipse cy="8" rx="6" ry="8.5" fill="' + lichter[i % 4] + '"/><ellipse cy="8" rx="12" ry="14" fill="' + lichter[i % 4] + '" opacity=".22"/></g>'));
  let fall = '';
  for(let i = 0; i < 26; i++){
    const x = (i * 29 + 7) % 100, d = 7 + (i % 5) * 1.6, verz = -(i * 0.9), g = 3 + (i % 3) * 2;
    fall += '<i class="flocke" style="left:' + x + '%;width:' + g + 'px;height:' + g + 'px;animation-name:festFallen;animation-timing-function:linear;animation-duration:' + d + 's;animation-delay:' + verz + 's"></i>';
  }
  return {oben, fall, css: ''};
}

function festBajram(){
  /* Baščaršija bei Nacht: Altstadthaeuser mit ueberstehendem Obergeschoss,
     Walmdach, Erker (doksat) und Gitterfenstern; die Laeden der Čaršija;
     Gazi Husrev-begova džamija mit Minarett, Sebilj und Sahat-kula. */
  const g = '#E9B949', gd = '#A87E26', gl = '#F3CF6E', licht = '#FFE9A3';
  const fenster = (x, y, b = 6, hh = 8) => '<rect x="' + x + '" y="' + y + '" width="' + b + '" height="' + hh + '" rx="1" fill="' + licht + '"/>'
    + '<path d="M' + (x + b / 2) + ',' + y + ' v' + hh + ' M' + x + ',' + (y + hh / 2) + ' h' + b + '" stroke="' + gd + '" stroke-width=".9"/>';
  const haus = (x, b, eg, og, dach, erker) => {
    const ogU = 96 - eg, ogO = ogU - og, ue = 4;
    let s = '<rect x="' + x + '" y="' + ogU + '" width="' + b + '" height="' + eg + '" fill="' + gd + '"/>'
      + '<rect x="' + (x - ue) + '" y="' + ogO + '" width="' + (b + 2 * ue) + '" height="' + og + '" fill="' + g + '"/>'
      + '<path d="M' + (x - ue - 1) + ',' + ogU + ' h' + (b + 2 * ue + 2) + ' l-3,3 h' + (-(b + 2 * ue - 4)) + 'Z" fill="' + gd + '" opacity=".7"/>'
      + '<path d="M' + (x - ue - 7) + ',' + (ogO + 1) + ' L' + (x + b * 0.22) + ',' + (ogO - dach) + ' L' + (x + b * 0.78) + ',' + (ogO - dach) + ' L' + (x + b + ue + 7) + ',' + (ogO + 1) + 'Z" fill="' + gl + '"/>'
      + '<rect x="' + (x + b * 0.7) + '" y="' + (ogO - dach - 5) + '" width="4" height="9" fill="' + gl + '"/>';
    const n = Math.max(2, Math.round(b / 12));
    for(let i = 0; i < n; i++) s += fenster(x - ue + 5 + i * ((b + 2 * ue - 16) / (n - 1)), ogO + 4, 6, og - 8);
    s += '<path d="M' + (x + b / 2 - 4) + ',96 v-10 a4,4 0 0 1 8,0 v10Z" fill="#6E4F14"/>';
    if(erker){
      const ex = x + b / 2 - 9;
      s += '<rect x="' + ex + '" y="' + (ogO - 2) + '" width="18" height="' + (og + 4) + '" fill="' + gl + '"/>'
        + '<path d="M' + ex + ',' + (ogO + og + 2) + ' l9,6 l9,-6Z" fill="' + gd + '"/>' + fenster(ex + 3, ogO + 2, 12, og - 4);
    }
    return s;
  };
  const kuppel = (cx, y, r) => '<path d="M' + (cx - r) + ',' + y + ' A' + r + ',' + (r * 0.95) + ' 0 0 1 ' + (cx + r) + ',' + y + 'Z" fill="' + g + '"/>';
  /* Mondsicheln werden ausgeschnitten (Maske), nicht mit Nachtblau
     uebermalt: im hellen Design laeuft der Himmel nach unten ins
     Durchsichtige aus, und die blaue Scheibe stand dort sichtbar auf
     hellem Grund. Jede Maske braucht eine eigene Kennung. */
  let masken = '', mn = 0;
  const sichel = (cx, cy, r, dx, dy, ri) => {
    const id = 'festMond' + (mn++);
    masken += '<mask id="' + id + '"><rect x="' + (cx - r - 1) + '" y="' + (cy - r - 1) + '" width="' + (2 * r + 2) + '" height="' + (2 * r + 2) + '" fill="#fff"/>'
      + '<circle cx="' + (cx + dx) + '" cy="' + (cy + dy) + '" r="' + ri + '" fill="#000"/></mask>';
    return '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="' + g + '" mask="url(#' + id + ')"/>';
  };
  const halbmond = (cx, y) => '<rect x="' + (cx - 0.8) + '" y="' + (y - 7) + '" width="1.6" height="7" fill="' + g + '"/>' + sichel(cx, y - 9, 2.6, 1.2, -0.6, 2.2);
  const oben = '<svg class="festgirlande festteil festnacht" aria-hidden="true" viewBox="0 0 328 96" width="100%">'
    + '<defs><linearGradient id="festNacht" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1C2350"/><stop offset="1" stop-color="#151728" stop-opacity="0"/></linearGradient></defs>'
    + '<rect width="328" height="96" rx="16" fill="url(#festNacht)"/>'
    + sichel(300, 22, 12, 5.5, -3.5, 10)
    + [[24, 14], [70, 24], [104, 10], [146, 30], [196, 12], [246, 22], [276, 40], [318, 46]].map(([x, y], i) => '<circle class="festStern" cx="' + x + '" cy="' + y + '" r="' + (i % 2 ? 1.5 : 2.1) + '" fill="#FFF3C4" style="animation-delay:' + (i * 0.4) + 's"/>').join('')
    + haus(12, 38, 18, 16, 16, true)
    + '<rect x="62" y="82" width="34" height="14" fill="' + gd + '"/><path d="M58,83 L64,72 H94 L100,83Z" fill="' + gl + '"/>'
    + '<rect x="65" y="85" width="12" height="11" fill="' + licht + '" opacity=".85"/><rect x="81" y="85" width="12" height="11" fill="' + licht + '" opacity=".85"/>'
    + '<path d="M65,88 h12 M81,88 h12" stroke="' + gd + '" stroke-width="1"/>'
    + '<rect x="104" y="66" width="46" height="30" fill="' + g + '"/><rect x="110" y="60" width="34" height="7" fill="' + g + '"/>'
    + kuppel(127, 61, 17) + halbmond(127, 45)
    + '<rect x="100" y="80" width="54" height="16" fill="' + gd + '"/>'
    + kuppel(109, 81, 6) + kuppel(127, 81, 6) + kuppel(145, 81, 6)
    + [104, 116, 128, 140].map(x => '<path d="M' + (x + 1) + ',96 v-8 a4,4 0 0 1 8,0 v8Z" fill="' + licht + '" opacity=".8"/>').join('')
    + '<rect x="157" y="28" width="7" height="68" fill="' + g + '"/>'
    + '<rect x="154" y="44" width="13" height="3" fill="' + gl + '"/><path d="M154,47 h13 l-2,3 h-9Z" fill="' + gd + '"/>'
    + '<path d="M156,29 L160.5,14 L165,29Z" fill="' + gl + '"/>' + halbmond(160.5, 14) + fenster(158.5, 56, 4, 6)
    + '<rect x="174" y="91" width="40" height="5" fill="' + gd + '"/><rect x="178" y="87" width="32" height="4" fill="' + g + '"/>'
    + '<rect x="181" y="68" width="26" height="19" fill="' + g + '"/>'
    + [183, 191, 199].map(x => '<path d="M' + x + ',86 v-10 a3,3 0 0 1 6,0 v10Z" fill="' + licht + '" opacity=".85"/>').join('')
    + '<path d="M172,69 L180,61 H208 L216,69Z" fill="' + gl + '"/>' + kuppel(194, 62, 12) + halbmond(194, 50)
    + '<rect x="224" y="30" width="15" height="66" fill="' + g + '"/><path d="M222,31 L231.5,14 L241,31Z" fill="' + gl + '"/>'
    + '<circle cx="231.5" cy="40" r="5" fill="' + licht + '"/><path d="M231.5,40 v-3.5 M231.5,40 h2.6" stroke="' + gd + '" stroke-width="1.1"/>'
    + fenster(229, 54, 5, 8) + fenster(229, 70, 5, 8)
    + haus(289, 24, 16, 14, 13, false) + haus(252, 34, 18, 17, 17, true)
    + '<defs>' + masken + '</defs></svg>';
  /* Im Grusskasten Mondsichel und fuenfzackiger Stern. Vorher standen dort
     zwei verschraenkte Quadrate - klein gezeichnet sahen sie aus wie ein
     Davidstern (Ajdin: "die Sterne sehen ein bisschen aus wie Judensterne,
     aender das"). */
  const zacken = Array.from({length: 10}, (_, k) => {
    const w = (-90 + k * 36) * Math.PI / 180, r = k % 2 ? 1.5 : 3.6;
    return (5.2 + r * Math.cos(w)).toFixed(2) + ',' + (-2.2 + r * Math.sin(w)).toFixed(2);
  }).join(' ');
  const mond = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 24 24"><defs><mask id="m"><rect x="-12" y="-12" width="24" height="24" fill="#fff"/><circle cx="4.2" cy="-2.6" r="7.4" fill="#000"/></mask></defs>'
    + '<circle r="9.5" fill="#E9B949" mask="url(#m)"/><polygon points="' + zacken + '" fill="#E9B949"/></svg>';
  return {oben, fall: '', css: `.festgruss{border-style:double; border-width:4px; background-image:${festSvgUrl(mond)}; background-repeat:no-repeat; background-size:32px; background-position:right 12px center}`};
}

function festOstern(){
  const wimpel = ['#F6A8C4', '#8FD6B4', '#FFE08A', '#B9C8FF'];
  const eier = [['#F6A8C4', '#FFFFFF'], ['#8FD6B4', '#F5C518'], ['#9BB8FF', '#FFFFFF'], ['#F5C518', '#E8474B']];
  const oben = festBild(66, festSchnur(30) + festHaenger(9, (x, y, i) => i % 2
    ? '<path transform="translate(' + x + ',' + (y - 8) + ')" d="M-11,0 H11 L0,22Z" fill="' + wimpel[i % 4] + '"/>'
    : '<g transform="translate(' + x + ',' + (y + 12) + ')"><ellipse rx="10" ry="13" fill="' + eier[i % 4][0] + '"/><path d="M-10,0 l5,-4 5,4 5,-4 5,4" stroke="' + eier[i % 4][1] + '" stroke-width="2" fill="none"/><circle cy="7" r="2" fill="' + eier[i % 4][1] + '"/><circle cx="-5" cy="6" r="1.6" fill="' + eier[i % 4][1] + '"/><circle cx="5" cy="6" r="1.6" fill="' + eier[i % 4][1] + '"/></g>'));
  const tulpe = (x, c, h) => '<g transform="translate(' + x + ',62)"><path d="M0,0 V-' + h + '" stroke="#5DAA6E" stroke-width="2.5"/><path d="M0,-' + (h - 8) + ' q-9,-4 -9,-14 q0,-4 9,-8 q9,4 9,8 q0,10 -9,14Z" fill="' + c + '"/><path d="M0,-' + (h * 0.45) + ' q-8,-2 -10,-10 q8,0 10,6Z" fill="#5DAA6E"/></g>';
  const bluemchen = (x, y) => '<g transform="translate(' + x + ',' + y + ')">' + [0, 72, 144, 216, 288].map(r => '<ellipse rx="3" ry="5.5" cy="-5" transform="rotate(' + r + ')" fill="#FFFFFF"/>').join('') + '<circle r="3" fill="#F5C518"/></g>';
  let wiese = '<svg class="festwiese festteil" aria-hidden="true" viewBox="0 0 ' + FW + ' 64" width="100%"><path d="M0,64 V52 Q' + (FW * 0.25) + ',44 ' + (FW / 2) + ',52 T' + FW + ',50 V64Z" fill="#3E7C55" opacity=".55"/>';
  [[18, '#F6A8C4', 30], [52, '#FFE08A', 24], [FW - 70, '#B9C8FF', 28], [FW - 30, '#F6A8C4', 34]].forEach(([x, c, hh]) => { wiese += tulpe(x, c, hh); });
  [[90, 54], [130, 58], [FW / 2, 53], [FW / 2 + 40, 57], [FW - 110, 55]].forEach(([x, y]) => { wiese += bluemchen(x, y); });
  wiese += '<g transform="translate(' + (FW / 2 - 18) + ',44) scale(.62)"><ellipse cy="6" rx="15" ry="13" fill="#FFD84D"/><circle cy="-10" r="10" fill="#FFD84D"/><circle cx="3" cy="-12" r="1.8" fill="#2B2B2B"/><path d="M9,-10 l6,2 -6,2Z" fill="#F28C28"/><path d="M-8,4 q-6,-4 -10,2 q5,2 10,1Z" fill="#F2C230"/><path d="M-12,4 q2,-14 12,-16 q-4,10 12,14 q-6,10 -24,2Z" fill="#FFFFFF" opacity=".95"/><path d="M-12,4 l3,-4 3,4 3,-4 3,4 3,-4 3,4 3,-4 3,4" stroke="#C9B9A0" stroke-width="1" fill="none"/></g>';
  wiese += '</svg>';
  const bluete = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 24 24">' + [0, 72, 144, 216, 288].map(r => '<ellipse rx="4" ry="7" cy="-6" transform="rotate(' + r + ')" fill="#F6A8C4"/>').join('') + '<circle r="4" fill="#F5C518"/></svg>';
  return {oben, wiese, fall: '', css: `.festgruss{background-image:${festSvgUrl(bluete)}; background-repeat:no-repeat; background-size:26px; background-position:right 12px center}`};
}

/* Je Fest: Kostuem, bosnischer Gruss, Farben des Grusskastens - Kante,
   Schrift hell und dunkel, Grund - und der Schmuck. */
const FESTE = {
  weihnachten: {teile: ['nikolausmuetze'], gruss: "Sretni praznici!", kante: '#E8474B', hell: '#B3261E', dunkel: '#FF6B6E', grund: 'rgba(232,71,75,.14)', schmuck: festWeihnachten},
  bajram:      {teile: ['bajramfes', 'jelek'], gruss: "Bajram šerif mubarek olsun!", kante: '#E9B949', hell: '#8A6508', dunkel: '#F2C94C', grund: 'rgba(233,185,73,.14)', schmuck: festBajram},
  ostern:      {teile: ['hasenohren'], gruss: "Sretan Uskrs!", kante: '#5DBB8E', hell: '#1E7A52', dunkel: '#8FD6B4', grund: 'rgba(143,214,180,.16)', schmuck: festOstern},
  halloween:   {teile: ['hexenhut', 'skelett'], farbe: 'skelett', gruss: "Sretna Noć vještica!", kante: '#F28C28', hell: '#B45309', dunkel: '#F6A04D', grund: 'rgba(242,140,40,.15)', schmuck: festHalloween},
};

/* Baut den Schmuck nur, wenn sich das Fest geaendert hat. Bei jedem
   Reiterwechsel neu gebaut, fingen die Flocken jedes Mal oben wieder an -
   derselbe Fehler wie beim springenden Drachen. */
let festSchmuckFuer = null;
function festSchmuck(){
  const id = festHeute();
  if(id === festSchmuckFuer) return;
  festSchmuckFuer = id;
  document.querySelectorAll('#pfad .festteil').forEach(e => e.remove());
  const stil = $('festStil');
  const f = FESTE[id];
  if(!f){ stil.textContent = ''; return; }
  const s = f.schmuck(), ober = document.querySelector('#pfad .obenreihe');
  stil.textContent = `#pfad{--fest-kante:${f.kante}; --fest-schrift:${f.hell}; --fest-grund:${f.grund}}
  @media (prefers-color-scheme: dark){ :root:not([data-theme="light"]) #pfad{--fest-schrift:${f.dunkel}} }
  :root[data-theme="dark"] #pfad{--fest-schrift:${f.dunkel}}
  ` + s.css;
  ober.insertAdjacentHTML('beforebegin', s.oben);
  /* Der Gruss kommt unter die Sprechblase des Serienschutzes. Stuende er
     zwischen ihr und dem Drachen, zeigte ihr Zipfel auf den Gruss
     (24.10.2026). Die Wiese bleibt direkt unter der Reihe, sie liegt dem
     Drachen zu Fuessen. */
  ($('schutzMeldung') || ober).insertAdjacentHTML('afterend', '<div class="festgruss festteil"><div><b lang="bs"></b><span></span></div></div>');
  const gruss = document.querySelector('#pfad .festgruss'), zeile = gruss.querySelector('span');
  gruss.querySelector('b').textContent = f.gruss;
  const schluessel = 'fest.' + id;        // fest.weihnachten, fest.bajram, fest.ostern, fest.halloween
  zeile.dataset.t = schluessel;            // so uebersetzt ein Sprachwechsel sie mit
  zeile.textContent = t(schluessel);
  if(s.wiese) ober.insertAdjacentHTML('afterend', s.wiese);
  if(s.fall) $('pfad').insertAdjacentHTML('beforeend', '<div class="festfall festteil" aria-hidden="true">' + s.fall + '</div>');
}

function zierratSchluessel(ids, farbe){
  if(ids === undefined){ const tr = festTracht(); ids = tr.ids; farbe = tr.farbe; }
  return ids.join(',') + '|' + farbe;
}
/* Sonnenbrille ohne Blinzeln (26.10.2026). Ajdin nach einem Bildschirm-
   video: "nur bei der sonnenbrille weil man die augen nicht sieht sieht es
   so aus das sein gesicht bugged aber er macht einfach nur die augen zu und
   wieder auf" - und dazu "ja mach das so". Die Sonnenbrille ist ganz
   deckend (zmaj_lottie.py, GEMALTE_HUETE); beim Blinzeln wechselt darunter
   das Kopf- und das Hornbild, und am Rand der Brille sieht das wie ein
   Zucken aus. Mit ihr bleibt das offene Bild stehen: in den Bildern, in
   denen der Kopfplan das Blinzelbild zeigt, zeigt jetzt das neutrale, und
   die Blinzel-Ebene faellt weg - weiter genau ein Kopf je Bild. Die
   anderen Brillen sind durchsichtig, dort sieht man das Blinzeln, es
   bleibt. Gearbeitet wird auf Kopien der Ebenen; zmajBasis bleibt, wie es
   ist. Die Deckkraft steht als Halte-Keyframes (h:1) da, wie
   kopf_deckkraft() in zmaj_lottie.py sie schreibt. */
function ohneBlinzeln(ebenen, op){
  const werte = o => {
    const w = [];
    for(let t = 0; t < op; t++){
      let v = (o && !o.a) ? o.k : 0;
      if(o && o.a) for(const f of o.k){ if(f.t <= t) v = f.s[0]; else break; }
      w.push(+v || 0);
    }
    return w;
  };
  const halten = w => ({a: 1, k: w.map((v, t) => (t === 0 || v !== w[t - 1]) ? {t: t, s: [v], h: 1} : null)
    .filter(Boolean).concat([{t: op, s: [w[0]], h: 1}])});
  for(const teil of ['kopf', 'hoerner']){
    const zu = ebenen.findIndex(l => l.nm === 'bild_' + teil + '_blinzeln');
    const offen = ebenen.findIndex(l => l.nm === 'bild_' + teil + '_neutral');
    if(zu < 0 || offen < 0) continue;
    const z = werte(ebenen[zu].ks.o), n = werte(ebenen[offen].ks.o);
    const o = halten(n.map((v, t) => Math.max(v, z[t])));
    ebenen[offen] = Object.assign({}, ebenen[offen], {ks: Object.assign({}, ebenen[offen].ks, {o: o})});
    ebenen.splice(zu, 1);
  }
}
async function zmajDaten(vorgabe){
  const tracht = vorgabe || festTracht();
  const ids = tracht.ids, farbe = tracht.farbe;
  const schluessel = zierratSchluessel(ids, farbe);
  if(!vorgabe && zmajFertig && zmajFertigFuer === schluessel) return zmajFertig;
  if(!zmajBasis) zmajBasis = await (await fetch('maskottchen/zmaj.json', {cache:'no-cache'})).json();
  for(const id of ids){
    if(zmajTeile.has(id)) continue;
    try{ zmajTeile.set(id, await (await fetch('maskottchen/' + zierratDatei(id), {cache:'no-cache'})).json()); }
    catch(e){ zmajTeile.set(id, null); }   // fehlt sie, bleibt der Drache eben ohne
  }
  /* Ein Schnipsel ist eine Liste von Ebenen - meist eine, beim Fanschal
     zwei, weil der Schriftzug eine eigene Textebene braucht. Aeltere
     Schnipsel waren ein einzelnes Objekt; beides wird vertragen.
     Seit 16.10.2026 sind 24 Stuecke von Gemini gemalt (alle bis auf
     Galaxie und Skelett - siehe GEMALT in zmaj_lottie.py). Ihr Schnipsel ist ein Objekt {layers, assets}: Bild-
     Ebenen am Rig und die Bilder dazu in maskottchen/zierrat/<id>/. Die
     Bilder stehen im Schnipsel und nicht in zmaj.json, damit nur geladen
     wird, was der Drache traegt. */
  const ebenen = zmajBasis.layers.slice(), zierBilder = [];
  ids.forEach(id => { const teil = zmajTeile.get(id);
    if(Array.isArray(teil)) ebenen.push(...teil);
    else if(teil && Array.isArray(teil.layers)){ ebenen.push(...teil.layers); zierBilder.push(...(teil.assets || [])); }
    else if(teil) ebenen.push(teil); });
  ebenen.sort((a, b) => a.ind - b.ind);
  if(ids.includes('sonnenbrille')) ohneBlinzeln(ebenen, zmajBasis.op || 0);   // siehe ohneBlinzeln()
  /* Bild-Drache (15.10.2026): Seit Ajdins Entscheidung nach den Vorschauen
     ist der Drache aus Bildern zusammengesetzt (Google Gemini, 32 Teile in
     maskottchen/teile/, Bild-Ebenen am Rig in zmaj.json - siehe
     zmaj_lottie.py). Eine Hautfarbe ist dann kein Farbtausch mehr, sondern
     ein eigener Bildsatz in maskottchen/haut/<farbe>/ mit denselben Namen.
     Nur der Satz der getragenen Farbe wird geladen. Fehlt er (MASCOT kennt
     "haut/<farbe>/" nicht), bleibt der Drache in der Grundfarbe.
     Nur, wenn zmaj.json ueberhaupt Bilder hat: mit dem Vergleichs-Schalter
     (zmaj_lottie.py --vektor) ist sie wieder der gezeichnete Drache, und
     ein liegengebliebener Hautsatz schaltete sonst faerbe() ab - der
     gruene Drache blieb blau, das Skelett behielt einen blauen Schaedel
     (Pruefung 15.10.2026). */
  const bilder = (zmajBasis.assets || []).some(a => a.p && !a.e);
  const haut = bilder ? hautSatz(farbe) : '';
  /* Ein Stueck, das ein Hautsatz ueberfluessig macht ("zmaj_ohne_haut"),
     faellt mit ihm weg: das Vektor-Skelett, wenn es haut/skelett/ gibt.
     Der Satz vom 15.10.2026 zeigte Fleisch und Augen mit Iris statt
     Knochen (gegen die Fest-Entscheidung vom 01.10.2026) und flog wieder
     raus. Seit 16.10.2026 ist haut/skelett/ ein von Gemini als Skelett
     gemaltes Bildset - nur Knochen, runde schwarze Hoehlen mit gelbem
     Punkt, boeser Blick -, am selben Rig wie der Drache, also mit genau
     seiner Bewegung. Fehlt der Satz, bleibt das Vektor-Skelett. */
  let liste = haut ? ebenen.filter(l => l.zmaj_ohne_haut !== haut) : ebenen;
  /* Ein Stueck kann Ebenen des Grunddrachens leeren - das Skelett hat kein
     Fleisch, also weg mit Koerper, Kopf, Armen, Beinen, Fluegeln und
     Schwanz (zmaj_leert in zmajz-skelett.json). Die Ebene bleibt stehen,
     nur ohne Formen: an ihr haengt die Bewegung, und die Knochen haengen
     an ihr. Bild-Ebenen (ty 2) haben keine Formen; sie fallen ganz weg -
     an ihnen haengt nichts. */
  const leer = new Set(liste.flatMap(l => l.zmaj_leert || []));
  if(leer.size) liste = liste.filter(l => !(l.ty === 2 && leer.has(l.nm)))
    .map(l => leer.has(l.nm) ? Object.assign({}, l, {shapes: []}) : l);
  /* Nur Bilder, die eine Ebene noch zeigt - lottie laedt sonst alle. Der
     Pfad steht in zmaj.json relativ zur Datei (teile/); die App laedt mit
     animationData, also setzt sie ihn hier relativ zu index.html. So liegen
     die Bilder auch in der Android-App als Dateien im Paket: kein Netz.
     Die Bilder der gemalten Kostueme haengen nicht an der Hautfarbe: ihr
     Pfad bleibt zierrat/<id>/ (16.10.2026). */
  const benutzt = new Set(liste.map(l => l.refId).filter(Boolean));
  const assets = (zmajBasis.assets || []).filter(a => !a.p || a.e || benutzt.has(a.id))
    .map(a => (a.p && !a.e) ? Object.assign({}, a, {u: 'maskottchen/' + (haut ? 'haut/' + haut + '/' : (a.u || ''))}) : a)
    .concat(zierBilder.filter(a => benutzt.has(a.id))
      .map(a => (a.p && !a.e) ? Object.assign({}, a, {u: 'maskottchen/' + (a.u || '')}) : a));
  const roh = Object.assign({}, zmajBasis, {layers: liste, assets});
  /* Beim Faerben MUSS auf einer Kopie gearbeitet werden: zmajBasis und die
     Schnipsel bleiben im Speicher stehen, und ein Farbwechsel wuerde sonst
     auf dem Ergebnis des vorigen aufsetzen. Mit Hautsatz wird nicht
     gefaerbt - die Farbe steckt in den Bildern, und die Kostueme haben
     ihre eigenen Farben (keine davon steht in FARB_QUELLE, geprueft
     15.10.2026). Ohne Hautsatz trifft faerbe() beim Bild-Drachen nur noch
     Vektor-Ebenen: das Skelett wird so knochenweiss. */
  const fertig = (farbe && !haut) ? faerbe(JSON.parse(JSON.stringify(roh)), farbeVon(farbe)) : roh;
  if(vorgabe) return fertig;
  zmajFertig = fertig; zmajFertigFuer = schluessel;
  return zmajFertig;
}
function zmaj(mood='happy'){
  if(hasLottie()) return '<div class="zmaj-anim" data-mood="'+esc(mood)+'"></div>';
  /* cry: das traurige Standbild (15.10.2026, Standbilder des Bild-Drachen) */
  const want = mood==='cheer' ? ['zmaj-jubel.png'] : ((mood==='sad' || mood==='cry') ? ['zmaj-traurig.png'] : []);
  const file = [...want, 'zmaj-frei.png', 'zmaj.png'].find(f=>MASCOT.has(f));
  if(file) return '<img src="maskottchen/'+file+'" alt="Zmaj, der Lerndrache">';
  return zmajSvg(mood);
}
/* no_l und no_r: zwei Fassungen für eine falsche Antwort – der Drache
   wendet den Kopf ab, einmal nach links, einmal nach rechts. Die App
   wechselt ab, damit mehrere Fehler hintereinander nicht gleich aussehen.
   Seit 16.10.2026 schüttelt der Bild-Drache dabei finster den Kopf: no_l
   beginnt links, no_r rechts (SCHUETTELN in zmaj_lottie.py). */
const MOOD_SEG = {happy:'idle', idle:'idle', cheer:'cheer', sad:'sad', ok:'ok',
                  no:'no', no_l:'no_l', no_r:'no_r', cry:'cry'};
function segOf(a, name){
  const m = (a.markers||[]).find(x => (x.payload && x.payload.name===name) || x.payload===name);
  return m ? [m.time, m.time + m.duration] : null;
}
/* Ruhen soll der Drache, wenn Bewegung aus ist - per Schalter
   "Animationen" (Klasse no-anim) oder per Geraeteeinstellung - und wenn
   seine Ansicht ausgeblendet ist. Bis zum 07.10.2026 lief er in allen drei
   Faellen in Schleife weiter: der Schalter traf nur CSS-Animationen, und
   der Drache der Startseite rechnete hinter der Lektion unsichtbar mit. */
function zmajRuht(el){
  if(document.body.classList.contains('no-anim')) return true;
  try{ if(matchMedia('(prefers-reduced-motion: reduce)').matches) return true; }catch(e){}
  /* VIEWS steht weiter unten; bis dahin gilt alles als sichtbar */
  try{ return VIEWS.some(v => { const w = $(v); return !!w && w.style.display === 'none' && w.contains(el); }); }
  catch(e){ return false; }
}
/* Haelt jeden geladenen Drachen an, der ruhen soll, und weckt jeden, der
   wieder darf. Laeuft beim Ansichtswechsel, beim Schalter "Animationen" und
   wenn das Geraet die Bewegung umstellt. Geweckt wird ohne Jubel- oder
   Kopfschuettel-Sprung: der war laengst vorbei. 07.10.2026. */
function zmajeAnpassen(){
  document.querySelectorAll('.zmaj-anim').forEach(el => {
    const a = el._anim;
    if(!a || !a.isLoaded) return;
    const m = el.dataset.mood || 'idle';
    if(zmajRuht(el)){ if(!a.isPaused) playMood(el, m); }
    else if(a.isPaused) playMood(el, /^(ok|cheer|no)/.test(m) ? 'idle' : m);
  });
}
/* Vor skripteDa nichts: zmajRuht() fragt VIEWS (inhalt.js, spaeter). */
try{ matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', ()=>{ if(skripteDa) zmajeAnpassen(); }); }catch(e){}
function playMood(el, mood){
  const name = MOOD_SEG[mood] || 'idle';
  /* Alle Stimmungen stecken als Marker in derselben Datei, es wird also nie
     nachgeladen. Steht der Zierrat nicht mehr auf dem Stand, baut mountZmaj
     die Anzeige neu auf - das ruft drachenNeu() nach jedem Anziehen. */
  const a = el._anim; if(!a || !a.isLoaded){ el.dataset.mood = mood; return; }
  el.dataset.mood = mood;
  if(el._back){ a.removeEventListener('complete', el._back); el._back = null; }
  if(el._timer){ clearTimeout(el._timer); el._timer = null; }
  // 'cheer' gehoert dazu: einmal springen reicht. Lief es in Schleife,
  // huepfte der Drache die ganze Zeit vor sich hin.
  const once = (name==='ok' || name==='cheer' || name.slice(0,2)==='no');
  // Ältere zmaj.json kennt no_l und no_r noch nicht - dann das alte 'no'
  const s = segOf(a, name) || (name.slice(0,3)==='no_' ? segOf(a, 'no') : null);
  /* Der Zeitgeber kann ablaufen, wenn diese Animation schon abgebaut ist
     (17.10.2026): die Ansicht wurde kurz nach einer Antwort neu gezeichnet und
     der Beobachter unter mountZmaj() hat sie zerstoert, oder mountZmaj() hat
     eine neue aufgebaut. Dann gibt es hier nichts mehr zurueckzustellen -
     removeEventListener an der zerstoerten Animation warf bis dahin einen
     Skriptfehler. */
  const toIdle = ()=>{ if(el._anim !== a || !el.isConnected) return; if(el._back){ a.removeEventListener('complete', el._back); el._back=null; } if(el._timer){ clearTimeout(el._timer); el._timer=null; } if(el.dataset.mood===mood) playMood(el, 'idle'); };
  const frames = s ? (s[1]-s[0]) : (a.totalFrames || 30);
  if(zmajRuht(el)){
    /* Standbild statt Schleife (07.10.2026): fuer die Ruhepose ihr erstes
       Bild, sonst die Mitte der Stimmung - dort lacht, schmollt oder weint
       er deutlich. resetSegments, weil goToAndStop sonst im zuletzt
       gespielten Abschnitt zaehlt und an dessen Ende abschneidet. Kurze
       Stimmungen kehren ueber den Zeitgeber unten zur Ruhepose zurueck. */
    a.loop = false;
    a.resetSegments(true);
    a.goToAndStop(!s ? 0 : (name === 'idle' ? s[0] : Math.floor((s[0] + s[1]) / 2)), true);
  }
  else if(s){ a.loop = !once; a.playSegments(s, true); }
  else { a.loop = !once; a.goToAndPlay(0, true); }   // Datei ohne Marker: ganze Animation
  if(once){
    el._back = toIdle; a.addEventListener('complete', el._back);
    el._timer = setTimeout(toIdle, frames / (a.frameRate || 30) * 1000 + 80);   // Sicherheitsnetz, falls kein complete-Ereignis kommt
  }
}
/* Umziehen waehrend des Ladens (17.10.2026): drachenNeu() nach jedem Tragen
   ruft mountZmaj(); laedt der Drache da noch, kehrt es sofort zurueck, und
   die laufende Ladung baute danach den ALTEN Aufzug auf - nach schnellem
   Umziehen trug er das erste Stueck statt des letzten, bis die Startseite
   sich das naechste Mal zeichnete. Jetzt merkt sich die Ladung, fuer welchen
   Stand sie laeuft (fuer); ist der am Ende nicht mehr der gewuenschte, wird
   ihr Ergebnis verworfen und einmal neu geladen. Die Tracht haengt nur am
   Gespeicherten und am Kalender, ein neuer Durchgang trifft also den
   aktuellen Stand; NACHLADEN_MAX ist nur die Sicherung gegen eine Schleife. */
const NACHLADEN_MAX = 3;
function mountZmaj(el, mood, vorgabe){
  if(!hasLottie() || el._laedt) return;
  if(mood) el.dataset.mood = mood;
  el._laedt = true;
  const fuer = vorgabe ? zierratSchluessel(vorgabe.ids, vorgabe.farbe) : zierratSchluessel();
  zmajDaten(vorgabe).then(daten => {
    el._laedt = false;
    if(!daten || !el.isConnected) return;
    if(!vorgabe && fuer !== zierratSchluessel() && (el._nachgeladen || 0) < NACHLADEN_MAX){
      el._nachgeladen = (el._nachgeladen || 0) + 1;
      mountZmaj(el);
      return;
    }
    el._nachgeladen = 0;
    if(el._anim){ try{ el._anim.destroy(); }catch(e){} el._anim = null; el.innerHTML = ''; }
    /* lottie schreibt beim Aufbauen in die Daten hinein. Jede Anzeige
       bekommt deshalb ihre eigene Kopie – sonst stören sich der große
       Drache auf der Startseite und der kleine in der Lektion. */
    const a = lottie.loadAnimation({container: el, renderer: 'svg', loop: true, autoplay: false,
      animationData: JSON.parse(JSON.stringify(daten)),
      rendererSettings: {preserveAspectRatio: 'xMidYMid meet', progressiveLoad: false}});
    el._anim = a; el._stand = fuer;   // nicht zmajFertigFuer: das kann inzwischen eine andere Ladung gesetzt haben
    a.addEventListener('DOMLoaded', ()=>{ a.isLoaded = true; playMood(el, el.dataset.mood || 'happy'); });
  }).catch(()=>{ el._laedt = false; });
}
new MutationObserver(()=>{
  /* Laeuft nach jeder geladenen Datei, nicht erst nach init(). Vor dem Start
     gibt es nichts einzuhaengen; was dabei entsteht, haengt der naechste Lauf
     ein (alle .zmaj-anim ohne _anim). 20.11.2026 */
  if(!skripteDa) return;
  if(window.lottie && lottie.getRegisteredAnimations) lottie.getRegisteredAnimations().forEach(a => {
    if(a.wrapper && !a.wrapper.isConnected){ try{ a.destroy(); }catch(e){} }
  });
  document.querySelectorAll('.zmaj-anim').forEach(el=>{ if(!el._anim) mountZmaj(el); });
})
  .observe(document.documentElement, {childList:true, subtree:true});
function setMood(el, mood){ // Bewegung passend zur Stimmung
  if(!el) return;
  const la = el.querySelector('.zmaj-anim');
  if(la){ playMood(la, mood); return; }
  el.classList.remove('idle','cheer','sad','ok','no'); el.classList.add(mood==='cheer'?'cheer':((mood==='sad'||mood==='cry')?'sad':'idle'));
}
let falschSeite = 0;   // wechselt zwischen "Kopf nach links" und "nach rechts"
/* Kleiner Drache im Fragenkasten reagiert auf die Antwort. Seit 19.10.2026
   haben auch Level-Test (zmajTest) und Einstufung (zmajEinst) einen. */
function zmajReact(ok, id){
  const el=$(id || 'zmajLesson'); if(!el) return;
  const la = el.querySelector('.zmaj-anim');
  if(la){ playMood(la, ok ? 'ok' : (falschSeite++ % 2 ? 'no_r' : 'no_l')); return; }
  el.classList.remove('ok','no','idle'); void el.offsetWidth; el.classList.add(ok?'ok':'no');
  el.innerHTML = zmaj(ok?'happy':'sad');
  setTimeout(()=>{ el.classList.remove('ok','no'); el.classList.add('idle'); el.innerHTML=zmaj('happy'); }, ok?700:1500);
}
/* ---- Ersatz-Drache ohne Lottie ----
   Nur in Gebrauch, wenn lottie.min.js fehlt und kein Bild in web/maskottchen
   liegt. v6, 15.10.2026: statt des alten runden Drachen eine vereinfachte,
   stehende Fassung der neuen Figur (Variante A, Kopf 1.2) - die Punkte sind
   aus zmaj_lottie.py abgeleitet und ausgeduennt, Farben wie FARB_QUELLE.
   Die Stimmung zeigt nur das Gesicht: happy (Ruhe), cheer (Augen zu, Maul
   offen), sad (Blick und Brauen), cry (Augen zu, Traenen). Alles andere
   gilt als happy. %b, %d ... stehen fuer die Farben des Drachen, damit die
   Zeichenketten kurz bleiben. Ein Stueck mit ~ vorn ist die linke Haelfte
   eines Paares (Fluegel, Bein, Arm, Horn, Flosse, Auge mit Braue); die
   rechte ist dasselbe gespiegelt. Alles steht IN der Funktion: so kann
   sie auch aufgerufen werden, bevor das Skript bis hierher gelaufen ist. */
function zmajSvg(mood='happy'){
  const FARBE = {b:'#415EA1', h:'#5281B3', d:'#26366A', w:'#7E9CDF', v:'#6282CC', y:'#F6C044', g:'#D79536', a:'#A86D27'};
  const FIGUR = [
    '<ellipse cx="60" cy="111.4" rx="25.9" ry="2.2" fill="#0B1533" opacity=".13"/>',
    '~<path d="M39.4,27.9C39.1,26.8 41.5,25.9 38.3,26.9C35.1,27.9 32.5,28.2 26.7,31.9C20.9,35.6 19.7,36.4 15.1,41.8C10.5,47.2 10.8,46.8 8.1,53.4C5.5,59.9 4.7,68.2 4.7,68.2C4.7,68.2 7.5,63.5 9.4,61.5C11.3,59.5 10.8,59.8 12.2,60.2C13.6,60.5 14,60.7 15,62.9C15.9,65 16,68.8 16,68.8C16,68.8 17.6,65.9 20,64.7C22.4,63.5 23.4,63.4 25.7,63.9C27.9,64.4 27.4,64.5 29.1,66.7C30.9,68.9 32.6,72.7 32.6,72.7C32.6,72.7 34.3,69 37.7,67.3C41.2,65.5 43.4,66.7 46.4,65.8C49.5,64.8 48.5,65.1 49.9,63.6C51.3,62 51.5,61.2 51.9,59.5C52.4,57.8 53,58.2 51.6,56.6C50.3,55 49,55.4 46.5,53C44.1,50.7 43.7,50.7 42,47.2C40.3,43.8 40.5,43.2 39.8,39.2C39.1,35.2 39.5,33.9 39.4,31.1C39.2,28.3 39.6,28.9 39.4,27.9Z" fill="%w" stroke="%d" stroke-width=".8"/><path d="M33.6,32.2C30.5,40.9 18.3,66.6 16.2,68.5C14,70.5 21,49.4 24,40.8C27.1,32.1 27.6,32.1 29.8,30.2C31.9,28.3 36.6,23.6 33.6,32.2Z" fill="%v"/><path d="M35.8,33.7C36.1,42.6 34,66.9 32.7,72.5C31.4,78.1 30.3,67.6 30,58.7C29.6,49.9 30,38.7 31.3,33.1C32.6,27.5 35.4,24.8 35.8,33.7Z" fill="%v"/><path d="M39.4,28.1C40.1,30.8 38.6,35.7 39,39.8C39.4,43.9 39,42.8 41.2,46.2C43.4,49.6 47.6,52.3 48.7,54.9C49.9,57.4 48.2,57.6 46.5,57.5C44.7,57.4 43.3,56.6 41,54.6C38.7,52.6 37.9,51.7 36.2,48.6C34.5,45.5 34.1,44.3 33.5,40.9C33,37.4 33.3,36.2 33.8,33.3C34.3,30.3 34.6,28.8 35.9,27.6C37.2,26.4 38.7,25.3 39.4,28.1Z" fill="%v"/><path d="M38.6,28.3C35.9,28.8 32.3,29.8 27.3,32.8C22.3,35.8 19.7,38.4 16.3,41.5C12.9,44.7 14.4,42.6 12.2,46.7C10.1,50.9 5.2,60.7 6.7,60.1C8.2,59.5 11.6,50.6 18.9,44C26.2,37.3 34.8,34.1 39.2,30.5C43.6,27 41.3,27.8 38.6,28.3Z" fill="%v"/><path d="M38.1,26.6C36.5,26.2 35.4,27.1 32.5,28.3C29.6,29.5 29.5,29.7 26.5,31.5C23.5,33.4 23.4,33.4 20.6,35.7C17.8,38 17.7,38 15.3,40.7C13,43.3 13,43.1 11.2,46.1C9.4,49.1 9.4,49.3 8.1,52.7C6.8,56.2 6.8,56.3 6,59.9C5.1,63.5 4.8,65.3 4.7,67.2C4.5,69.1 4,70.8 5.4,67.4C6.7,63.9 8,58.5 9.9,53.5C11.9,48.5 11.4,50.1 13.2,47.4C15,44.6 14.9,44.8 17.2,42.4C19.5,40 19.6,39.9 22.4,37.9C25.1,35.8 25.2,35.7 28.1,34.1C30.9,32.5 30.9,32.3 33.7,31.3C36.4,30.3 37.9,31.1 39.1,30C40.2,28.8 39.8,27 38.1,26.6Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M32.5,31.7C30.6,34 31.1,33 27,42.2C22.8,51.4 18.6,61.9 15.9,68.5C13.3,75.1 13.2,75 16.4,68.6C19.6,62.3 24.2,52.1 28.8,43.1C33.3,34.2 33.7,35.7 34.6,32.8C35.6,30 34.4,29.3 32.5,31.7Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M34.5,33.5C33.6,36.6 33.7,36.3 33.2,46.1C32.6,55.8 32.5,65.9 32.5,72.5C32.4,79.1 32.2,79.1 32.9,72.5C33.6,65.9 34.1,55.9 35.1,46.3C36.1,36.6 37.1,37 37,33.8C36.8,30.7 35.5,30.5 34.5,33.5Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M37.6,27.8C36.5,29.1 37,30.3 37,33.3C36.9,36.4 36.7,36.7 37.4,40.1C38.1,43.5 38.2,43.8 39.7,46.9C41.3,50 40.6,49.5 43.4,52.5C46.3,55.4 48.7,57.9 51.1,58.7C53.5,59.5 54.4,57.8 53.1,55.7C51.8,53.6 48.6,52.8 46,50.3C43.3,47.7 44,48.1 42.7,45.4C41.3,42.7 41.2,42.5 40.6,39.5C40,36.5 40.2,36.2 40.3,33.4C40.5,30.7 41.8,29.7 41.1,28.3C40.4,26.9 38.6,26.6 37.6,27.8Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M36.9,27.9C37.1,27.3 37,26.7 38.7,26.7C40.3,26.7 44.1,27.9 44.1,27.9C44.1,27.9 39.3,29.3 37.7,29.3C36.1,29.3 36.7,28.5 36.9,27.9Z" fill="%w" stroke="%d" stroke-width=".8"/>',
    '<path d="M76.9,94C75.9,93 76.5,90.6 77.2,89.4C77.9,88.1 79.2,88.6 80.1,88.6C81,88.5 80.8,87.9 81.2,89.1C81.6,90.3 82.9,92.9 81.9,94C81,95.1 78,95.1 76.9,94Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M82.6,94.6C82,93.7 84.2,90.6 85.4,90.6C86.6,90.7 88.6,93.8 88,94.6C87.3,95.5 83.2,95.5 82.6,94.6Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M88.4,94.6C87.9,93.9 89.6,90.5 90.7,90.3C91.8,90.1 93.7,92.7 93.2,93.7C92.7,94.7 89,95.4 88.4,94.6Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M93.2,92.9C92.4,92.7 93.4,89.7 93.8,88.4C94.1,87.1 94,87.3 94.7,87C95.3,86.7 96,86.3 96.6,86.9C97.2,87.4 98,88 97.2,89.4C96.5,90.7 94,93.1 93.2,92.9Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M66.7,94.4C69.9,92.7 73.8,93.3 79.5,93.1C85.1,93 85.7,94.3 89.3,93.8C93,93.4 91.9,93.9 94.1,91.3C96.3,88.7 98,83.4 98,83.4C98,83.4 94.5,84.1 94.5,84.1C94.5,84.1 96.2,79.4 96.3,76.4C96.5,73.4 95,72.1 95,72.1C95,72.1 98.9,74.4 100.9,77.5C103,80.5 103.2,84.3 103.2,84.3C103.2,84.3 100.1,83.5 100.1,83.5C100.1,83.5 101.2,84 101.2,86.3C101.2,88.6 101.3,89.8 100,92.8C98.7,95.9 97.8,96.4 96,98.4C94.2,100.3 96.7,99.2 92.8,100.7C89,102.2 85.7,103.7 80.6,104.4C75.6,105.1 76,104.5 72.5,103.4C69,102.3 68.2,102.3 66.7,100.1C65.3,97.9 63.5,96.2 66.7,94.4Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M67,100.1C68.2,101.3 69.1,102.2 72.5,103.2C75.9,104.3 76.5,104.4 80.6,104.2C84.8,104 84.9,104.3 89.1,102.4C93.2,100.5 96.5,97.3 97.1,96.6C97.7,96 94.8,98.5 91.4,99.8C88,101 87.6,101.3 83.5,101.6C79.5,101.9 79.3,101.8 75.4,101C71.5,100.3 70,98.8 67.9,98.6C65.8,98.4 65.9,98.9 67,100.1Z" fill="%y" stroke="%g" stroke-width=".5"/>',
    '~<path d="M48.7,97.2C47,98.4 49.5,100.5 47.9,102.4C46.3,104.4 43.4,104.6 41.7,105.9C39.9,107.2 40.3,107.4 40.3,108.3C40.2,109.2 39.6,109.4 41.5,110C43.4,110.5 46.1,111.3 48.7,110.9C51.4,110.5 51.8,110.3 53.3,108.2C54.8,106.1 55,104 55.5,101.5C56,99.1 57.1,98.2 55.6,97.2C54.1,96.2 50.5,96 48.7,97.2Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M42.6,109.7C42.9,108.9 43.6,107.3 43.9,106.5M46.2,110.3C46.5,109.4 47.1,107.6 47.4,106.7" fill="none" stroke="%d" stroke-width=".6"/>',
    '<path d="M60,46.7C57.3,47 55.2,45.9 53.4,47.9C51.6,49.9 53.8,51.7 52.8,54.6C51.7,57.5 50.7,52.9 49.2,59.5C47.7,66.1 48.2,73.3 46.9,81C45.6,88.6 44.7,86.2 43.9,90.2C43.2,94.2 43.7,94.8 44,97C44.3,99.2 44.3,98.2 45,99.1C45.7,99.9 44.7,99.8 46.7,100.4C48.7,101 50.9,101.3 53.1,101.4C55.3,101.4 54.4,102.1 55.4,100.7C56.4,99.3 56.4,97.2 57.2,95.7C58,94.3 57.2,94.9 58.6,94.9C60,94.9 61.3,94.3 62.8,95.7C64.3,97.2 63.6,99.3 64.6,100.7C65.6,102.1 64.7,101.4 66.9,101.4C69.1,101.3 71,101.5 73.3,100.4C75.6,99.3 75.3,99.5 76,97C76.7,94.4 76.8,94.2 76.1,90.2C75.3,86.2 74.4,88.6 73.1,81C71.8,73.3 72.3,66.1 70.8,59.5C69.3,52.9 68.3,57.5 67.2,54.6C66.2,51.7 67.4,49.8 66.6,47.9C65.8,46 65.7,47.3 64,47C62.3,46.7 62.7,46.5 60,46.7Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M64.4,48.5C65.7,49.3 68.2,52.8 70.2,61.2C72.2,69.6 71,74.6 72.4,82.1C73.8,89.7 75.3,87 75.9,91.4C76.5,95.7 75.9,97.1 74.7,99.5C73.6,101.9 73.1,100.8 71.4,100.9C69.7,101.1 68.4,106.7 67.9,100.1C67.4,93.5 70.1,85.2 69.4,74.6C68.7,64 66.4,64.3 65.1,57.8C63.9,51.2 63.1,47.6 64.4,48.5Z" fill="%d" opacity=".23"/><path d="M49.4,86.3C50,86.9 50.6,87.2 51.8,88.6C52.9,90 53.1,90.2 54.1,91.9C55.1,93.5 55.3,94.4 55.7,95.2M70.6,86.3C70,86.9 69.4,87.2 68.2,88.6C67.1,90 66.9,90.2 65.9,91.9C64.9,93.5 64.7,94.4 64.3,95.2" fill="none" stroke="%d" stroke-width=".7"/><path d="M60,47.9C57.7,47.9 56.8,45.1 55.5,48.2C54.1,51.3 55.5,54.9 54.5,60.4C53.6,65.8 52.6,65.5 51.7,69.9C50.8,74.4 50.7,73.4 50.8,78.1C50.9,82.7 50.9,84.3 52.1,88.6C53.4,93 53.9,92.9 55.8,95.5C57.8,98 57.9,98.8 60,98.8C62.1,98.8 62.2,98 64.2,95.5C66.1,92.9 66.7,91.5 67.9,88.6C69.1,85.7 68.6,87.2 68.9,83.9C69.2,80.5 69.9,81 69,75.2C68.2,69.3 66.6,67.1 65.5,60.4C64.3,53.6 65.9,51.3 64.5,48.2C63.2,45.1 62.3,47.9 60,47.9Z" fill="%y" stroke="%g" stroke-width=".5"/><path d="M55.8,51.7C59.6,53.2 60.4,53.2 64.2,51.7M55.5,57.8C59.5,59.2 60.5,59.2 64.5,57.8M54,63.7C59.4,65.4 60.6,65.4 66,63.7M52.1,70.5C59.2,72.7 60.8,72.7 67.9,70.5M51.4,78.4C59.1,80.6 60.9,80.6 68.6,78.4M51.9,86C59.2,88.2 60.8,88.2 68.1,86M55,92.7C59.5,94.4 60.5,94.4 65,92.7" fill="none" stroke="%g" stroke-width=".6" opacity=".9"/>',
    '~<path d="M47.9,72.4C45.6,75.8 46,74.7 44.2,74.4C42.4,74.1 41,75.4 41.4,71.3C41.9,67.1 43.9,63.1 45.8,59.2C47.7,55.3 47.1,57.7 48.2,57.1C49.3,56.5 48.7,56.5 49.9,57C51,57.5 51.7,57.5 52.5,58.9C53.2,60.3 53.9,58.4 52.6,62.1C51.4,65.8 50.2,69 47.9,72.4Z" fill="%b"/><path d="M51.6,57.8C50.8,57.6 50.1,56.7 48.6,57C47,57.3 48,54.9 46,58.8C44,62.7 42.4,67 41.4,71.1C40.5,75.1 41.1,72.6 42.4,73.5C43.7,74.3 43.8,76.1 46.1,74.2C48.3,72.4 49.3,68.8 50.5,66.7" fill="none" stroke="%d" stroke-width=".8"/><path d="M41.4,71.1C40.4,74.3 38.5,77.9 37.7,82.1C36.9,86.3 37.8,86.4 38.3,87.8C38.8,89.3 39.3,88.4 39.6,87.9C40,87.4 39.9,85.7 39.9,85.7C39.9,85.7 40.7,88.9 41.2,89C41.7,89 41.7,85.8 41.7,85.8C41.7,85.8 42.6,88.6 43.1,88.4C43.5,88.3 43.5,85.1 43.5,85.1C43.5,85.1 44.1,87.1 44.5,87.6C44.9,88.1 44.6,90 45.1,87.2C45.6,84.3 45.7,80.3 46.4,76.3C47.2,72.3 48.2,73.2 48.2,71.1C48.2,69 47.7,68.8 46.4,68C45.2,67.3 44.3,67.7 43.2,68C42,68.3 42.3,68.5 41.8,69.2C41.4,70 42.5,67.9 41.4,71.1Z" fill="%b"/><path d="M41.4,71.1C40.5,73.9 38.5,77.9 37.7,82.1C36.9,86.3 37.8,86.4 38.3,87.8C38.8,89.3 39.3,88.4 39.6,87.9C40,87.4 39.9,85.7 39.9,85.7C39.9,85.7 40.7,88.9 41.2,89C41.7,89 41.7,85.8 41.7,85.8C41.7,85.8 42.6,88.6 43.1,88.4C43.5,88.3 43.5,85.1 43.5,85.1C43.5,85.1 44.1,87.1 44.5,87.6C44.9,88.1 44.6,90 45.1,87.2C45.6,84.3 45.7,80.3 46.4,76.3C47.2,72.3 47.7,72.4 48.2,71.1" fill="none" stroke="%d" stroke-width=".8"/><path d="M39.9,85.7C39.8,85.3 39.8,84.4 39.8,84M41.7,85.8C41.7,85.4 41.7,84.4 41.7,84M43.5,85.1C43.5,84.7 43.6,83.9 43.7,83.5" fill="none" stroke="%d" stroke-width=".6"/>',
    '~<path d="M45.7,6C45.7,6 44.1,7.7 43.4,10C42.6,12.3 41.7,11.2 42.8,15.2C43.9,19.2 45.5,23.5 47.6,26C49.8,28.5 49.5,26.3 51.4,25.3C53.3,24.2 54.9,24.1 55.2,21.8C55.5,19.5 54.4,18.7 52.4,16.2C50.4,13.8 48.8,14.4 47.2,12.1C45.6,9.7 46.5,8.3 46.1,6.8C45.8,5.3 45.7,6 45.7,6Z" fill="%y" stroke="%a" stroke-width=".7"/><path d="M45.2,6.8C44.6,7.5 43.7,8.9 43.1,11C42.5,13.1 41.7,11.4 42.8,15.2C43.9,18.9 46,23.5 47.6,26C49.3,28.5 50.2,27.7 49.4,25.3C48.7,22.8 45.7,20.4 44.6,16.2C43.6,12 45.1,10.8 45.2,8.4C45.4,6.1 45.7,6.2 45.2,6.8Z" fill="%g" opacity=".45"/><path d="M46.2,7.5C46.7,8.5 46.1,10.3 47.6,12.4C49.1,14.5 50.5,14.2 52.2,16.1C53.9,18 55.8,20.7 54.5,20.1C53.2,19.4 49.4,16.3 47.2,13.4C45,10.6 46.1,10.2 45.9,8.7C45.6,7.2 45.8,6.6 46.2,7.5Z" fill="#fff" opacity=".35"/><path d="M43.7,10.4C44.8,9.8 45.1,9.5 46.1,10.2M43.3,13.4C45.4,12.3 45.9,12.3 48,13.4M43.6,16.4C47.3,14.9 48.1,14.8 51.7,16.3M45.4,19.4C49.1,17.9 49.9,18 53.7,19.6" fill="none" stroke="%g" stroke-width=".5" opacity=".9"/>',
    '~<path d="M47.9,26.8C46.9,24.9 42.7,23.6 42.7,23.6C42.7,23.6 43,27.9 43.6,29.8C44.2,31.7 44.5,31.6 45.3,32.2C46.2,32.7 46.8,33.4 47.3,32.2C47.9,31 48.9,28.8 47.9,26.8Z" fill="%b" stroke="%d" stroke-width="1"/><path d="M47.2,32C46.3,31.5 42.5,34.3 42.5,34.3C42.5,34.3 45.6,36.8 46.6,36.3C47.7,35.7 48.1,32.4 47.2,32Z" fill="%b" stroke="%d" stroke-width="1"/>',
    '<path d="M60,20.3C58,20.4 57.7,19.7 54.8,20.8C52,21.8 51.1,19.7 48.7,24.3C46.4,28.9 46.1,34.7 45.5,39.2C44.9,43.7 45.3,40.6 46.2,42.1C47.1,43.7 45.7,43.2 49.1,45.3C52.6,47.4 54.6,50.5 60,50.5C65.4,50.5 67.4,47.4 70.9,45.3C74.3,43.2 72.9,43.7 73.8,42.1C74.7,40.6 75.1,43.7 74.5,39.2C73.9,34.7 73,28.7 71.3,24.3C69.6,19.9 69.7,22.6 67.6,21.7C65.4,20.7 64.6,20.8 62.7,20.4C60.8,20.1 62,20.2 60,20.3Z" fill="%b" stroke="%d" stroke-width="1"/><ellipse cx="60" cy="41.1" rx="8.7" ry="4.1" fill="%h" opacity=".32"/><ellipse cx="52.2" cy="31.7" rx="4.4" ry="4.5" fill="%h" opacity=".3"/><ellipse cx="67.8" cy="31.7" rx="4.4" ry="4.5" fill="%h" opacity=".3"/><path d="M59.9,15.3C59.9,15.3 61.8,19.4 61.9,22.1C61.9,24.9 60,26.4 60,26.4C60,26.4 58.4,24.5 58.1,22.1C57.8,19.7 58.5,18.5 58.9,16.8C59.3,15.1 59.9,15.3 59.9,15.3Z" fill="%b" stroke="%d" stroke-width=".8"/><path d="M55,41.3C55.1,40.7 54.1,39.8 55.3,38.8C56.6,37.8 57.7,37.4 60,37.4C62.3,37.4 63.4,37.8 64.7,38.8C65.9,39.8 64.9,40.7 65,41.3" fill="none" stroke="%d" stroke-width=".6"/><path d="M55.7,39.9C56,39.5 56.3,39.4 56.8,39.5C57.3,39.6 57.5,39.8 57.6,40.3C57.8,40.8 57.7,41.1 57.4,41.4C57,41.8 56.7,41.9 56.3,41.8C55.9,41.7 55.8,41.5 55.7,41C55.5,40.5 55.4,40.3 55.7,39.9ZM64.3,39.9C64,39.5 63.7,39.4 63.2,39.5C62.7,39.6 62.5,39.8 62.4,40.3C62.2,40.8 62.3,41.1 62.6,41.4C63,41.8 63.3,41.9 63.7,41.8C64.1,41.7 64.2,41.5 64.3,41C64.5,40.5 64.6,40.3 64.3,39.9Z" fill="%d"/>',
  ];
  const GESICHT = {
    happy: [
      '~<ellipse cx="52.6" cy="33.2" rx="3.2" ry="3.5" fill="#fff" stroke="%d" stroke-width=".6"/><ellipse cx="53.3" cy="34" rx="2.2" ry="2.5" fill="#3C6BB3" stroke="#2A4F8F" stroke-width=".3"/><ellipse cx="53.5" cy="34.3" rx="1.1" ry="1.5" fill="#112649"/><ellipse cx="52.3" cy="32.4" rx=".8" ry=".8" fill="#fff"/><ellipse cx="54.4" cy="35.7" rx=".3" ry=".3" fill="#fff" opacity=".85"/><path d="M49.4,33.2C49.5,33 49.5,32.5 49.6,32C49.8,31.5 49.9,31.3 50.2,30.9C50.5,30.6 50.6,30.4 51,30.1C51.4,29.9 51.6,29.8 52.1,29.7C52.5,29.6 52.7,29.6 53.2,29.7C53.6,29.8 53.8,29.9 54.2,30.1C54.6,30.4 54.8,30.6 55.1,30.9C55.4,31.3 55.5,31.5 55.6,32C55.8,32.5 55.8,33 55.8,33.2" fill="none" stroke="%d" stroke-width=".8"/><path d="M49.4,27.9C49.7,27.5 50,26.9 50.7,26.3C51.4,25.6 51.4,25.5 52.3,25.3C53.1,25.2 53.7,25.7 54.2,25.8" fill="none" stroke="%d" stroke-width=".9"/>',
      '<path d="M50,39.3C50.2,39.7 49.7,39.5 50.9,40.6C52.1,41.7 52.6,42.5 54.8,43.6C57.1,44.7 57.4,44.9 60,44.9C62.6,44.9 62.9,44.7 65.2,43.6C67.4,42.5 67.9,41.7 69.1,40.6C70.3,39.5 69.8,39.7 70,39.3" fill="none" stroke="%d" stroke-width=".7"/>',
    ],
    cheer: [
      '~<path d="M49.8,34.5C50.2,34.1 50.5,33.4 51.2,32.9C51.9,32.3 51.9,32.3 52.6,32.3C53.4,32.3 53.4,32.3 54.1,32.9C54.8,33.4 55.1,34.1 55.4,34.5" fill="none" stroke="%d" stroke-width=".8"/><path d="M49.6,27.3C49.9,26.8 50,26.2 50.7,25.5C51.3,24.7 51.3,24.6 52.2,24.4C53,24.2 53.6,24.6 54.1,24.6" fill="none" stroke="%d" stroke-width=".9"/>',
      '<path d="M51.2,41.3C51.2,41.3 53.4,42.3 55.5,42.8C57.7,43.3 57.8,43.2 60,43.2C62.2,43.2 62.3,43.3 64.5,42.8C66.6,42.3 68.8,41.3 68.8,41.3C68.8,41.3 68.5,42.7 67.5,44.1C66.6,45.4 66.2,45.7 64.9,46.7C63.7,47.7 63.7,47.7 62.5,48.1C61.3,48.5 61.3,48.5 60,48.5C58.7,48.5 58.7,48.5 57.5,48.1C56.3,47.7 56.3,47.7 55.1,46.7C53.8,45.7 53.4,45.4 52.5,44.1C51.5,42.7 51.2,41.3 51.2,41.3Z" fill="#7A1F2B"/><path d="M55.7,47.7C55.7,47.2 56.6,46.7 57.6,46.3C58.7,45.9 58.8,46 60,46C61.2,46 61.3,45.9 62.4,46.3C63.4,46.7 64.3,47.2 64.3,47.7C64.4,48.2 63.6,48.1 62.5,48.2C61.4,48.4 61.3,48.5 60,48.5C58.7,48.5 58.6,48.4 57.5,48.2C56.4,48.1 55.7,48.2 55.7,47.7Z" fill="#FF7B8E"/><path d="M53.3,42.1L54.4,44.3L55.4,42.6Z" fill="#fff"/><path d="M64.6,42.6L65.6,44.3L66.7,42.1Z" fill="#fff"/><path d="M51.2,41.3C51.2,41.3 53.4,42.3 55.5,42.8C57.7,43.3 57.8,43.2 60,43.2C62.2,43.2 62.3,43.3 64.5,42.8C66.6,42.3 68.8,41.3 68.8,41.3C68.8,41.3 68.5,42.7 67.5,44.1C66.6,45.4 66.2,45.7 64.9,46.7C63.7,47.7 63.7,47.7 62.5,48.1C61.3,48.5 61.3,48.5 60,48.5C58.7,48.5 58.7,48.5 57.5,48.1C56.3,47.7 56.3,47.7 55.1,46.7C53.8,45.7 53.4,45.4 52.5,44.1C51.5,42.7 51.2,41.3 51.2,41.3Z" fill="none" stroke="%d" stroke-width=".6"/><path d="M50.3,40.3C50.5,40.6 51,41 51.2,41.3M69.7,40.3C69.5,40.6 69,41 68.8,41.3" fill="none" stroke="%d" stroke-width=".6"/>',
    ],
    sad: [
      '~<ellipse cx="52.6" cy="33.2" rx="3.2" ry="3.5" fill="#fff" stroke="%d" stroke-width=".6"/><ellipse cx="53.3" cy="34.8" rx="2.2" ry="2.5" fill="#3C6BB3" stroke="#2A4F8F" stroke-width=".3"/><ellipse cx="53.5" cy="35.1" rx="1.1" ry="1.5" fill="#112649"/><ellipse cx="52.3" cy="33.1" rx=".8" ry=".8" fill="#fff"/><ellipse cx="54.4" cy="36.5" rx=".3" ry=".3" fill="#fff" opacity=".85"/><path d="M50.5,30.5A3.2,3.5 0 0 1 54.7,30.5Z" fill="%b" stroke="%d" stroke-width=".6"/><path d="M49.4,33.2C49.5,33 49.5,32.5 49.6,32C49.8,31.5 49.9,31.3 50.2,30.9C50.5,30.6 50.6,30.4 51,30.1C51.4,29.9 51.6,29.8 52.1,29.7C52.5,29.6 52.7,29.6 53.2,29.7C53.6,29.8 53.8,29.9 54.2,30.1C54.6,30.4 54.8,30.6 55.1,30.9C55.4,31.3 55.5,31.5 55.6,32C55.8,32.5 55.8,33 55.8,33.2" fill="none" stroke="%d" stroke-width=".8"/><path d="M50.2,28C50.3,27.5 50.3,26.8 50.7,26C51.1,25.1 51.1,25 51.8,24.5C52.6,24.1 53.3,24.3 53.7,24.2" fill="none" stroke="%d" stroke-width=".9"/>',
      '<path d="M55,45.6C55.6,45.3 56.2,44.7 57.5,44.2C58.7,43.8 58.7,43.8 60,43.8C61.3,43.8 61.3,43.8 62.5,44.2C63.8,44.7 64.4,45.3 65,45.6" fill="none" stroke="%d" stroke-width=".7"/>',
    ],
    cry: [
      '~<path d="M49.8,34.5C50.2,34.1 50.5,33.4 51.2,32.9C51.9,32.3 51.9,32.3 52.6,32.3C53.4,32.3 53.4,32.3 54.1,32.9C54.8,33.4 55.1,34.1 55.4,34.5" fill="none" stroke="%d" stroke-width=".8"/><path d="M50.3,34.7C50.8,34.6 51.4,34.2 52.6,34.2C53.8,34.2 54.4,34.6 55,34.7" fill="none" stroke="%d" stroke-width=".5"/><ellipse cx="52.6" cy="35.4" rx="2.2" ry=".6" fill="#8FD3FF" opacity=".85"/><path d="M50.1,28.5C50.2,28 50.2,27.3 50.7,26.5C51.1,25.6 51.1,25.5 51.9,25.1C52.7,24.7 53.3,24.9 53.8,24.8" fill="none" stroke="%d" stroke-width=".9"/>',
      '<path d="M53.5,44.2C53.5,44.2 55,43.4 56.6,43.2C58.2,43.1 58.3,43.7 60,43.7C61.7,43.7 61.8,43.1 63.4,43.2C65,43.4 66.5,44.2 66.5,44.2C66.5,44.2 66.3,45.4 65.3,46.3C64.3,47.2 64,47.3 62.6,47.7C61.3,48.1 61.3,48 60,48C58.7,48 58.7,48.1 57.4,47.7C56,47.3 55.7,47.2 54.7,46.3C53.7,45.4 53.5,44.2 53.5,44.2Z" fill="#7A1F2B"/><ellipse cx="60" cy="47.1" rx="2.4" ry=".8" fill="#FF7B8E"/><path d="M54.6,43.9L55.3,45.5L56.1,43.6Z" fill="#fff"/><path d="M63.9,43.6L64.7,45.5L65.4,43.9Z" fill="#fff"/><path d="M53.5,44.2C53.5,44.2 55,43.4 56.6,43.2C58.2,43.1 58.3,43.7 60,43.7C61.7,43.7 61.8,43.1 63.4,43.2C65,43.4 66.5,44.2 66.5,44.2C66.5,44.2 66.3,45.4 65.3,46.3C64.3,47.2 64,47.3 62.6,47.7C61.3,48.1 61.3,48 60,48C58.7,48 58.7,48.1 57.4,47.7C56,47.3 55.7,47.2 54.7,46.3C53.7,45.4 53.5,44.2 53.5,44.2Z" fill="none" stroke="%d" stroke-width=".6"/><path d="M49,37.1c1.2,1.6 1.6,2.6 1.6,3.4a1.6,1.6 0 0 1-3.2,0c0-.8.4-1.8 1.6-3.4Z" fill="#8FD3FF" opacity=".9"/><path d="M71,37.5c1.2,1.6 1.6,2.6 1.6,3.4a1.6,1.6 0 0 1-3.2,0c0-.8.4-1.8 1.6-3.4Z" fill="#8FD3FF" opacity=".9"/><path d="M49.4,42.1c1.2,1.6 1.6,2.6 1.6,3.4a1.6,1.6 0 0 1-3.2,0c0-.8.4-1.8 1.6-3.4Z" fill="#8FD3FF" opacity=".9"/>',
    ],
  };
  const teile = liste => liste.map(s => s[0] === '~'
    ? s.slice(1) + '<g transform="matrix(-1 0 0 1 120 0)">' + s.slice(1) + '</g>' : s).join('');
  const gesicht = Object.prototype.hasOwnProperty.call(GESICHT, mood) ? GESICHT[mood] : GESICHT.happy;
  return ('<svg viewBox="0 0 120 120" aria-hidden="true" stroke-linejoin="round" stroke-linecap="round">'
    + teile(FIGUR) + teile(gesicht) + '</svg>').replace(/%([a-z])/g, (m, c) => FARBE[c] || m);
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
