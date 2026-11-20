/* ---------- Gesprochenes vergleichen ----------
   Die Erkennung schreibt, was sie hoert, nach den Regeln der Sprache, die
   das Geraet gerade kann - und Bosnisch kann es meist nicht. Aus "noć"
   wird dann "notch", aus "ćao" wird "chao". Buchstabe fuer Buchstabe
   verglichen waere jede zweite richtige Antwort falsch.

   Deshalb wird vorher lautlich vereinfacht: alles, was wie tsch oder sch
   klingt, faellt auf einen Buchstaben zusammen, Doppelbuchstaben werden
   einfach, Leerzeichen fallen weg (wo die Erkennung Wortgrenzen setzt,
   ist Zufall). Was dann noch abweicht, darf sich um ein paar Buchstaben
   unterscheiden - je laenger das Wort, desto mehr. */
/* ---------- Zahlen: Ziffer und Wort gelten beide ----------
   Androids Erkenner gibt Zahlen als ZIFFERN zurueck. Wer "pet" sagt, wird als
   "5" verstanden - und lautlich() strich am Ende alles ausser a-z, aus der 5
   wurde eine leere Zeichenkette, und die Antwort galt als falsch. Im Level
   "Zahlen" traf das fast jede Sprechaufgabe.
   Ajdin am 27.09.2026: "das sprechen funktioniert irgendwie bei den zahlen
   schlecht ich sage die zahl richtig der sagt irgendwie nein", dann "dann lass
   einfach beides gelten sowohl zahl als auch buchstaben".
   Zwei Wege, die sich ergaenzen:
   - zahlWert() liest einen GANZEN Ausdruck als Zahl, ob "5", "pet" oder
     "dvije". Sind beide Seiten Zahlen, wird gerechnet statt gehoert - damit
     gilt auch die weibliche Form.
   - zahlenAusschreiben() ersetzt Ziffern MITTEN in einem Satz durch das
     Zahlwort, fuer Faelle wie "Nalazimo se u 5". */
const ZAHL_EINER = ['nula','jedan','dva','tri','četiri','pet','šest','sedam','osam','devet',
                    'deset','jedanaest','dvanaest','trinaest','četrnaest','petnaest',
                    'šesnaest','sedamnaest','osamnaest','devetnaest'];
const ZAHL_ZEHNER = {2:'dvadeset', 3:'trideset', 4:'četrdeset', 5:'pedeset',
                     6:'šezdeset', 7:'sedamdeset', 8:'osamdeset', 9:'devedeset'};
const ZAHL_GROSS  = {100:'sto', 200:'dvjesto', 1000:'hiljada'};
/* Weibliche und saechliche Formen, und das kroatische tisuca fuer tausend.
   dvjesta neben dvjesto fuer zweihundert seit K2 (Ajdin K2, 20.11.2026): beide
   Schreibungen sind ueblich, dvjesto die haeufigere (spoznaja.unze.ba/article/32). */
const ZAHL_SONDER = {jedna:1, jedno:1, dvije:2, dvoje:2, tisuca:1000, dvjesta:200};

function zahlAlsWort(n){
  if(!Number.isInteger(n) || n < 0) return null;
  if(n < 20) return ZAHL_EINER[n];
  if(n < 100){
    const z = ZAHL_ZEHNER[Math.floor(n / 10)], e = n % 10;
    return z ? (e ? z + ' ' + ZAHL_EINER[e] : z) : null;
  }
  return ZAHL_GROSS[n] || null;
}

const zahlenAusschreiben = s => String(s).replace(/\d+/g, m => {
  const w = zahlAlsWort(parseInt(m, 10));
  return w === null ? m : ' ' + w + ' ';
});

function zahlWert(s){
  const roh = String(s).trim();
  if(/^\d+$/.test(roh)) return parseInt(roh, 10);
  const t = strip(roh).replace(/[^a-z ]/g, '').replace(/\s+/g, ' ').trim();
  if(!t) return null;
  const ohne = t.replace(/ /g, '');
  if(ZAHL_SONDER[ohne] !== undefined) return ZAHL_SONDER[ohne];
  const i = ZAHL_EINER.findIndex(w => strip(w) === t);
  if(i >= 0) return i;
  for(const z in ZAHL_ZEHNER) if(strip(ZAHL_ZEHNER[z]) === t) return Number(z) * 10;
  for(const n in ZAHL_GROSS)  if(strip(ZAHL_GROSS[n])  === t) return Number(n);
  /* Zusammengesetzt, z.B. "dvadeset jedan". Nur Zehner plus Einer.
     Seit dem 12.11.2026 auch mit "i" dazwischen, "dvadeset i jedan": bs-Web
     hat beides etwa gleich oft (193 / 156). So gilt es fuer jede Zahl, beim
     Tippen wie beim Sprechen. */
  const teile = t.split(' ');
  if(teile.length === 3 && teile[1] === 'i') teile.splice(1, 1);
  if(teile.length === 2){
    const a = zahlWert(teile[0]), b = zahlWert(teile[1]);
    /* Nur Zehner plus Einer: 20 bis 90, glatt, und danach eine 1 bis 9.
       Damit bleibt "sto jedan" draussen - so heisst 101 im Bosnischen nicht. */
    if(a !== null && b !== null && a >= 20 && a <= 90 && a % 10 === 0 && b >= 1 && b <= 9) return a + b;
  }
  return null;
}
/* ---- Zahlen, die wechseln (25.10.2026) ----
   Ajdin: "die sätze immer mit der gleichen zahl ist und nicht mal
   variiert". Gemeint ist die Zahl im Satz: "Sada je pet sati." kam immer
   mit fuenf. Ein Satz mit zahl (vokabeln.py) kommt jetzt je Aufgabe mit
   einer der Zahlen aus zahl.werte - welche Saetze und welche Zahlen, hat
   Ajdin in einer Tabelle freigegeben ("Ja, alle so"). Bosnisch steht die
   Zahl als Wort, in der Bedeutung als Ziffer: zahl.de ist die uebersetzte
   Vorlage mit {n} ("Jetzt ist es {n} Uhr."), auf Tuerkisch bei der Uhrzeit
   mit {lok} fuer "7'de", "3'te".
   - Gezogen wird einmal je Aufgabe, in renderTask() (task.v). Die
     Wiederholung nach einem Fehler ist eine Kopie der Aufgabe und behaelt
     die Zahl. Fehler-Topf und Stern merken sich den Grundsatz
     (topfSchluessel nimmt task.s, nicht die Fassung) - eine andere Zahl
     ist kein anderer Eintrag.
   - Eine andere als die heutige Zahl nur, wenn der fertige Satz eine
     Aufnahme hat - auf dem Handy bliebe er sonst stumm - und ihr Zahlwort
     schon gelernt ist. Gesucht wird das Wort im Level zahlen ueber seinen
     Wert und gefragt nach seiner Kennung: "dvije" zaehlt so als "zwei:dva",
     und "sto" ist hundert, nicht der Tisch ("tisch:sto" steht in einem
     anderen Level). Sonst bleibt die heutige Zahl samt der Bedeutung von
     heute - so auch in der Web-Demo, die fuer diese Saetze keine Aufnahmen
     hat (sie spricht nur Emir, siehe ton_nur_emir.json).
     Gelernt heisst: in known - oder der Level zahlen liegt schon hinter
     dem Lernenden (zahlLevelHinter()). Bis zur Pruefung am 25.10.2026 galt
     nur known, und wer per Einstufung ("etwas", "gut") hinter dem Level
     zahlen anfaengt, hat dessen Woerter nie in known: er sah die Saetze
     immer mit der gleichen Zahl, also genau das, was Ajdin bemaengelt hat.
   - Ersetzt wird das Zahlwort als ganzes Wort, mit der Grossschreibung des
     Originals, in text, answer, bs und jedem auch. Genau so baut
     zahl_fassung() in inhalt.py die Saetze, nach denen die Aufnahmen
     heissen; tests_e2e/test_zahlen.py vergleicht beide.
   - Ist die Zahl die Loesung, gilt eine getippte Ziffer weiter als richtig
     (zahlWert() in matches()). */
const ZAHL_LEVEL = 'zahlen';
/* Tuerkisch "um 7": die Endung haengt am letzten gesprochenen Wort der Zahl
   (Vokalharmonie a/e, nach ç t ş k wird aus d ein t). Dieselbe Tabelle wie
   tr_lokativ() in inhalt.py. */
const TR_LOK_EINER = ['da', 'de', 'de', 'te', 'te', 'te', 'da', 'de', 'de', 'da'];
const TR_LOK_ZEHNER = ['', 'da', 'de', 'da', 'ta', 'de', 'ta', 'te', 'de', 'da'];
function trLokativ(n){
  const e = n % 10, z = Math.floor(n / 10) % 10;
  return n + "'" + (n === 0 ? 'da' : e ? TR_LOK_EINER[e] : z ? TR_LOK_ZEHNER[z] : 'de');
}
const zahlVorlage = (vorlage, n) => String(vorlage || '').split('{n}').join(String(n)).split('{lok}').join(trLokativ(n));
const zahlWortFuer = (z, n) => (z.weiblich && n === 2) ? 'dvije' : zahlAlsWort(n);
/* Ohne Lookbehind, das alte WebViews nicht kennen: das Zeichen davor wird
   mitgenommen und wieder vorangestellt. */
function zahlTausch(text, alt, neu){
  if(typeof text !== 'string' || !alt || !neu) return text;
  const muster = new RegExp('(^|[^\\p{L}\\p{M}])(' + alt.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')(?=[^\\p{L}\\p{M}]|$)', 'giu');
  return text.replace(muster, (m, vor, wort) => vor + (/^\p{Lu}/u.test(wort) ? neu.charAt(0).toUpperCase() + neu.slice(1) : neu));
}
/* Der Satz s mit der Zahl n. Ohne zahl oder ohne gezogene Zahl (null) der
   Satz selbst, unveraendert. */
function zahlFassung(s, n){
  const z = s && s.zahl;
  if(!z || typeof n !== 'number') return s;
  const neu = zahlWortFuer(z, n), tausch = x => zahlTausch(x, z.wort, neu);
  const f = Object.assign({}, s, {de: zahlVorlage(z.de, n)});
  ['text', 'answer', 'bs'].forEach(k => { if(typeof s[k] === 'string') f[k] = tausch(s[k]); });
  if(Array.isArray(s.auch)) f.auch = s.auch.map(tausch);
  return f;
}
/* Was nach der Antwort gesprochen wird: die Luecke mit Loesung, sonst bs. */
const zahlGanz = f => typeof f.text === 'string' ? f.text.replace('___', f.answer) : f.bs;
let _zahlKennung = null;
function zahlKennung(n){
  if(!_zahlKennung){
    _zahlKennung = new Map();
    const c = CATEGORIES.find(x => x.id === ZAHL_LEVEL);
    (c ? c.words : []).forEach(w => { const v = zahlWert(w.bs); if(v !== null && !_zahlKennung.has(v)) _zahlKennung.set(v, w.id); });
  }
  return _zahlKennung.get(n) || null;
}
/* Ob der Level zahlen schon hinter dem Lernenden liegt: bestanden, ein
   spaeterer Level bestanden, oder die Einstufung beginnt dahinter. Dann
   gelten seine Woerter als gelernt, wie "vorher" in kachelnFuerLektion()
   die Woerter frueherer Level als begegnet gelten. Dieselbe Grenze wie
   isUnlocked(): offen ist alles bis max(hoechsterBestanden()+1,
   einstufungIndex()) - liegt der Level danach noch darin, ist zahlen
   vorbei. Wer AM Level zahlen einsteigt, lernt die Zahlen erst noch.
   Pruefbefund 25.10.2026 (Ajdin: "die sätze immer mit der gleichen zahl
   ist und nicht mal variiert"). */
function zahlLevelHinter(){
  const i = CATEGORIES.findIndex(c => c.id === ZAHL_LEVEL);
  return i >= 0 && i < freiBis();   // seit 13.11.2026 samt Sprung-Test
}
/* Die Zahl fuer eine Aufgabe, oder null fuer "wie bisher". */
function zahlZiehen(s){
  const z = s && s.zahl;
  if(!z || !Array.isArray(z.werte)) return null;
  const heute = zahlWert(z.wort);
  const hinter = zahlLevelHinter();
  const geht = z.werte.filter(n => n === heute ||
    (!!zahlKennung(n) && (hinter || known.has(zahlKennung(n))) && !!audioDatei(zahlGanz(zahlFassung(s, n)))));
  if(!geht.some(n => n !== heute)) return null;
  return geht[Math.floor(Math.random() * geht.length)];
}
function lautlich(s){
  let x = strip(zahlenAusschreiben(s));
  const regeln = [
    // erst die langen Buendel, sonst frisst eine kurze Regel sie auf
    [/tsch/g,'c'], [/tsh/g,'c'], [/tch/g,'c'], [/cz/g,'c'],
    [/sch/g,'s'], [/sh/g,'s'],
    [/ch/g,'c'], [/ck/g,'k'], [/zh/g,'z'], [/ts/g,'c'],
    [/dj/g,'d'], [/dz/g,'d'],
    [/qu/g,'kv'], [/q/g,'k'], [/x/g,'ks'],
    // "hvala" hoert eine deutsche Erkennung als "koala", "kwala", "quala".
    // Das h vor dem v ist fuer sie ein k - also beides auf k.
    [/hv/g,'kv'],
    [/y/g,'j'], [/w/g,'v'], [/ph/g,'f'], [/f/g,'v'], [/th/g,'t'],
  ];
  for(const [a,b] of regeln) x = x.replace(a,b);
  /* Hier stand bis 07.10.2026 statt des Rueckverweises auf (.) das
     Steuerzeichen 0x01 - ein Patch hatte die Fluchtfolge verschluckt.
     Der Ausdruck traf nie, Doppelbuchstaben blieben doppelt. */
  return x.replace(/[^a-z]/g,'').replace(/(.)\1+/g,'$1');
}
/* Wie viele Buchstaben muesste man aendern, um aus a b zu machen. */
function abstand(a, b){
  if(a === b) return 0;
  const m = a.length, n = b.length;
  if(!m) return n;
  if(!n) return m;
  let vorige = Array.from({length:n+1}, (_,j)=>j);
  for(let i=1;i<=m;i++){
    const jetzt = [i];
    for(let j=1;j<=n;j++){
      jetzt[j] = Math.min(vorige[j]+1, jetzt[j-1]+1,
                          vorige[j-1] + (a[i-1]===b[j-1] ? 0 : 1));
    }
    vorige = jetzt;
  }
  return vorige[n];
}
/* ---- Kyrillisch beim Sprechen (16.11.2026) ----
   Rueckmeldung ueber das Formular: die Sprechuebung erkennt auch einen
   Muttersprachler nicht immer (Sprech-Analyse vom 16.11.2026, Punkt 2).
   Schreibt ein Erkenner kyrillisch - Azure tut es bei sr-RS, Google
   vielleicht -, strich lautlich() alles ausser a-z, aus "хвала" wurde ein
   leerer Text, und jedes richtig gesprochene Wort war falsch. Im Korpus
   9.388 von 9.388 kyrillischen Faellen. Seit Android nur noch bs-BA und
   hr-HR nimmt, ist das ein Sicherheitsnetz.
   Umgeschrieben wird am Anfang von klingtWie(), fuer Gehoertes UND Ziel, vor
   zahlWert(): am Anfang von lautlich() waere zu spaet, zahlWert() entfernt
   Kyrillisch selbst, und "два" bliebe fuer "dvije" falsch. Nur beim
   Sprechen - getippt wird mit matches(), das bleibt, wie es ist.
   Die Tabelle: das serbische Alphabet, dazu die russischen Buchstaben, die
   es dort nicht gibt. Gross wird klein, das tun zahlWert() und lautlich()
   ohnehin. */
const KYRILLISCH = {'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'ђ':'đ', 'е':'e', 'ж':'ž', 'з':'z', 'и':'i',
  'ј':'j', 'к':'k', 'л':'l', 'љ':'lj', 'м':'m', 'н':'n', 'њ':'nj', 'о':'o', 'п':'p', 'р':'r', 'с':'s', 'т':'t',
  'ћ':'ć', 'у':'u', 'ф':'f', 'х':'h', 'ц':'c', 'ч':'č', 'џ':'dž', 'ш':'š',
  'й':'j', 'щ':'šč', 'ъ':'', 'ы':'i', 'ь':'', 'э':'e', 'ю':'ju', 'я':'ja', 'ё':'jo',
  'ѓ':'đ', 'ќ':'ć', 'ѕ':'dz', 'і':'i', 'ї':'ji', 'є':'je'};
const kyrillischLatein = s => String(s).replace(/[\u0400-\u04FF]/g, c => {
  const l = KYRILLISCH[c.toLowerCase()];
  return l === undefined ? c : l;
});
/* ---- Wie ein Erkenner kurze Woerter schreibt (17.11.2026) ----
   Seit sehr kurze Ziele nur noch genau gleich gelten (siehe FUELLWOERTER),
   fiel durch, was der kroatische Erkenner anders schreibt als die App: "Tko"
   fuer "Ko", "Što" fuer "Šta", dazu "Ćau" und "Ciao" fuer "Ćao". Ajdin am
   16.11.2026: beim Sprechen zaehlen sie, als Woerter und in Saetzen ("Tko je
   to?" fuer "Ko je to?"). Getippt bleibt es, wie es ist (matches()), "auch"-
   Formen gibt es dafuer nicht.
   Umgeschrieben wird nur das Gehoerte, nur ganze Woerter ("zašto", "nešto"
   bleiben), und nur dort, wo das Ziel die Form der App enthaelt: "Što" wird
   "šta", wenn im Ziel "šta" steht - und nicht selbst "što". Und zwar vor
   zahlWert() und lautlich(), solange die Haekchen noch dastehen: lautlich()
   macht aus "što" und "sto" (hundert) dasselbe, und zahlWert() liest "Što" als
   100. So wird "sto" nie zu "šta", und "sto" gilt weiter nicht fuer "Šta?",
   "Šta" nicht fuer "sto".
   Zuerst wurde auf beiden Seiten und ueberall umgeschrieben. Dann galt aber
   auch "Šta" fuer das App-Wort "što" (dass), ein einzelnes "Što" fuer "stan",
   "usta", "star", "stav" und "staž" (ueber "šta", einen Buchstaben daneben),
   und "sto", "schto" und "shto" galten nicht mehr fuer "što" (Messung vom
   17.11.2026). Dass "Što" fuer "sto" zaehlt, bleibt, wie es war: die Haekchen
   zaehlen beim Sprechen nicht.
   "čao" und "cao" braucht es hier nicht, lautlich() macht sie ohnehin zu
   "Ćao"; "cau" ist "Ćau" ohne Haekchen. */
const ERKENNER_SCHREIBWEISE = {'tko': 'ko', 'što': 'šta', 'ćau': 'ćao', 'čau': 'ćao', 'cau': 'ćao', 'ciao': 'ćao'};
function schreibweiseAngleichen(gehoert, ziel){
  const klein = w => w.normalize('NFC').toLowerCase();
  let zw = null;   // die Woerter des Ziels, erst wenn es sie braucht
  return String(gehoert).replace(/[\p{L}\p{M}]+/gu, w => {
    const k = klein(w), n = ERKENNER_SCHREIBWEISE[k];
    if(n === undefined) return w;
    if(!zw) zw = new Set((String(ziel).match(/[\p{L}\p{M}]+/gu) || []).map(klein));
    return zw.has(n) && !zw.has(k) ? n : w;
  });
}
/* ---- Sehr kurze Ziele (16.11.2026) ----
   Ziele mit hoechstens drei Lauten (so gezaehlt, wie lautlich() zaehlt)
   gelten nur noch GENAU gleich. Bis dahin durfte ein Buchstabe abweichen,
   und dann zaehlte "pa" fuer "pas", "sir" fuer "sin", "na" fuer "ne", "dva",
   "dan" und "pa" fuer "Da": 498 von 559 kurzen Zielen nahmen ein anderes
   Wort der App an (Analyse, Punkt 7). Ajdin am 16.11.2026: nur noch genau
   gleich. Dafuer duerfen um das Wort herum Wiederholungen und Fuellwoerter
   stehen, "Pa da", "Da da", "Ćao ćao" (Punkt 5, Fix-Plan Schritt 3) - das
   Wort selbst aber nur genau gleich, sonst ginge "Pa dva" fuer "Da" durch.
   "Ko je" fuer "Ko?" bleibt falsch, "je" ist kein Fuellwort. Ab vier
   Lauten bleibt alles wie bisher. Die Fuellwoerter stehen schon so da, wie
   lautlich() sie schreibt ("Hmm" wird "hm", "OK" wird "ok").
   Zusammengeschrieben zaehlt nicht: "dada" ist EIN gehoertes Wort, und es
   klingt nicht genau wie "da". Bis zur Nachbesserung am 16.11.2026 galt es,
   und dann waren die App-Woerter "nana" (Oma) richtig fuer "na" und "jaja"
   (Eier) fuer "Ja".
   Seit dem 17.11.2026 auch das Zoegern "e", "ee", "eee" (lautlich() macht
   jedes Wort nur aus e zu "e") und "Okay", "Okej", "Okey" wie "ok" (lautlich():
   "okaj", "okej") - Ajdin am 16.11.2026, "Eee da" und "Okej da" fuer "Da".
   "e" allein fuer "Da" bleibt falsch: ohne die Fuellwoerter bleibt nichts.
   Waere "E" (Ausruf) einmal selbst ein Ziel - heute ist es keins -, gaelte
   dort das Zoegern: ein Fuellwort im Ziel zaehlt mit (siehe unten). */
const FUELLWOERTER = new Set(['pa', 'eto', 'evo', 'ovaj', 'hm', 'aha', 'ok', 'e', 'okaj', 'okej']);
function wortGenau(gehoert, ziel){
  const woerter = s => String(s).split(/\s+/).map(x => lautlich(x)).filter(Boolean);
  const zw = woerter(ziel);
  // Ein Fuellwort, das selbst zum Ziel gehoert ("Evo"), bleibt stehen.
  const gw = woerter(gehoert).filter(x => !FUELLWOERTER.has(x) || zw.includes(x));
  if(!gw.length || !zw.length) return false;
  // Das Ziel ein- oder mehrmals, Wort fuer Wort und jedes genau gleich
  return gw.length % zw.length === 0 && gw.every((x, i) => x === zw[i % zw.length]);
}
/* Passt das Gehoerte zum Zielwort? */
function klingtWie(gehoert, ziel){
  ziel = kyrillischLatein(ziel);   // siehe KYRILLISCH (16.11.2026) und ERKENNER_SCHREIBWEISE (17.11.2026)
  gehoert = schreibweiseAngleichen(kyrillischLatein(gehoert), ziel);
  /* Sind beide Seiten eine Zahl, wird gerechnet - dann gilt "5" fuer "pet"
     und "2" auch fuer die weibliche Form "dvije". */
  const zg = zahlWert(gehoert), zz = zahlWert(ziel);
  if(zg !== null && zz !== null) return zg === zz;
  /* Ein Klammerzusatz spricht niemand mit: "nana (auch: metvica)" war "nana". Seit dem
     14.11.2026 heisst das Wort "nana / metvica" (Pruefbericht 1.4, B6), die Regel bleibt. */
  const zielOhne = String(ziel).replace(/\([^)]*\)/g, ' ');
  const g = lautlich(gehoert), z = lautlich(zielOhne);
  if(!g || !z) return false;
  if(g === z) return true;
  if(z.length <= 3) return wortGenau(gehoert, zielOhne);   // siehe FUELLWOERTER (16.11.2026)
  // Enthalten zaehlt nur bei genug Buchstaben, sonst passt "da" ueberallhin
  const kurz = Math.min(g.length, z.length);
  /* Mehr gesagt als das Ziel ist in Ordnung. Weniger nur, wenn fast alles da ist:
     Sonst reichte "mogu" fuer "Mogu li platiti karticom?", und der Satz galt als
     gewusst (Pruefbericht 1.3, 06.11.2026). */
  if(kurz >= 4 && (g.includes(z) || (z.includes(g) && g.length >= z.length * 0.7))) return true;
  return abstand(g, z) <= Math.max(1, Math.round(z.length / 5));
}
/* Passt das Gehoerte zu einem Eintrag? Das fragt die Sprechaufgabe (bewerte()).
   Jede Schreibweise gilt: "Laku noć / Lahku noć" sind zwei.
   Pfeil-Eintraege im Level "Mehrzahl" ("brat → braća", 26 Stueck, 16.11.2026,
   Analyse Punkt 8): Bis dahin zaehlten sie nur, wenn beide Woerter gesagt
   wurden, "braća" allein war falsch. Jetzt gilt auch die Mehrzahl allein, die
   Einzahl allein weiter nicht.
   Die Mehrzahl allein nur GENAU gleich, wie ein sehr kurzes Ziel (wortGenau()),
   mit Wiederholungen und Fuellwoertern: "braća", "kuče", "Pa braća". Zuerst
   lief sie durch klingtWie() mit seiner Aehnlichkeit, und dann galten fremde
   Woerter: "brava" fuer braća, "doći" fuer noći, "dati" fuer dani, "mene" fuer
   žene, dazu jeder Satz mit der Mehrzahl darin ("On posjeduje tri kuće.") -
   194 fremde Woerter und Saetze der App in 19 der 26 Eintraege (Pruefung vom
   16.11.2026).
   Bei vier Lauten widersprach das Ajdins Entscheidung (keine neue
   Aehnlichkeit). Genau gleich kann die Einzahl nie sein, ein Vergleich mit
   ihr ist nicht mehr noetig. */
function passtGesprochen(gehoert, bs){
  return String(bs).split(' / ').some(form => {
    if(klingtWie(gehoert, form)) return true;          // beide Woerter zusammen, wie bisher
    const pfeil = form.split(' → ');
    return pfeil.length === 2 && wortGenau(schreibweiseAngleichen(kyrillischLatein(gehoert), pfeil[1]), pfeil[1]);
  });
}
function esc(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
/* Fuer aria-label: alles vor dem ersten Buchstaben weg. Auf dem Bildschirm
   sagt "🔊 Hören" alles; vorgelesen wird daraus je nach Programm
   "Lautsprecher mit Schallwellen Hören" oder gar nichts. */
const nurWort = s => String(s).replace(/^[^\p{L}\p{N}]+/u, '').trim();
/* ---- Gemalte Symbole statt Emojis (24.10.2026) ----
   Ajdin: "die emojis die muessten mal anders gemacht werden". Symbol-Satz
   V1 aus web/symbole, siehe .sym im Stil. symbol(name) ist Schmuck: alt=""
   und aria-hidden, die Bedeutung traegt der Text daneben ("Hören",
   "500 KM", "Lernpfad"). Traegt sie kein Wort - neben dem Herz steht nur
   "5", neben der Muenze nur "+10" -, bekommt das Bild mit sagt einen
   Ersatztext: bei den Leben das Wort der Sprache (stat.leben), sonst das
   Emoji, das es ersetzt (SYMBOL_SAGT). Dessen Namen liest ein
   Bildschirmleser in der Sprache des Geraets vor, genau wie vorher im
   Text - ohne neue Uebersetzung.
   Steht ein Symbol mitten im Satz, heisst es in sprachen.py {herz},
   {muenze} oder {einstellungen}; symbolTexte() liefert die Bilder dazu.
   Am Anfang eines Knopfs steht es nicht im Text, sondern davor:
   mitSymbol('lautsprecher', t('task.hoeren')). */
const SYMBOL_SAGT = {muenze: '🪙', einstellungen: '⚙'};
function symbol(name, sagt){
  return '<img class="sym sym-' + name + '" src="symbole/' + name + '.webp" '
       + (sagt ? 'alt="' + esc(sagt) + '"' : 'alt="" aria-hidden="true"') + '>';
}
function mitSymbol(name, html){ return symbol(name) + ' ' + html; }
/* Goldenes Herz fuer die Vollversion (14.11.2026). Ajdin nach dem Kauf im
   iPhone-Test: alles frei, "nur das das herz nicht gold ist". Mit der
   Vollversion (premium, auch der Dauerschalter) steht ueberall, wo das Herz
   mit ∞ steht, das goldene: Kopfleiste, Fragenkasten in Lektion und Test,
   Statistik auf dem Ergebnis. Unbegrenzt ohne Kauf (?alle=1, Geschenk)
   bleibt es rot - Gold heisst gekauft. Gemalt mit Gemini wie die anderen. */
function herzSymbol(sagt){ return symbol(premium ? 'herzgold' : 'herz', sagt); }
/* Einheitlich auf Android und iPhone (14.11.2026). Ajdin im iPhone-Test:
   "es hat noch die iphone bilder ... das muss einheitlich sein". Die
   letzten Emojis der Oberflaeche sind ebenso gemalt (abgenommen: "passt")
   und stehen nicht mehr im Text, sondern kommen von hier: ziel vor
   "Level-Test" (war 🏁), stern vor "Zmaj bewerten" (⭐), herzblau nach
   "Danke!" (💙), funken an der goldenen Flamme (✨), brief vor der E-Mail
   im Profil (✉). Ueberall steht ein Wort daneben, die Bilder sind also
   Schmuck. Die Zeichen fuer Ueberspringen, Pause, Stopp und Abbrechen
   zeichnet zeichen() selbst. */
/* 🎉 und ▶ ebenso gemalt (15.11.2026, Ajdin: "Male sie", abgenommen:
   "Passt"). play steht vor "Lektion starten", "Weitermachen · ..." und
   "Weiterlesen" (war ▶), konfetti nach "Lektion geschafft", "Runde
   geschafft", "Bestanden! Bravo", "... die ganze Sektion fertig" und
   "Geschichte geschafft!" (war 🎉). Wie das Emoji am Ende des Satzes,
   aber nie allein in einer Zeile: das letzte Wort und das Bild stehen in
   .amwort zusammen (ein geschuetztes Leerzeichen allein reicht nicht,
   Chrome bricht trotzdem vor dem Bild um - so stand es auf Tuerkisch bei
   360 px allein unter "hikâye tamamlandı!"). Nur fuer reinen Text ohne
   Tags. Schmuck, der Satz sagt es schon. */
function mitKonfetti(html){
  const i = html.lastIndexOf(' ') + 1;
  return html.slice(0, i) + '<span class="amwort">' + html.slice(i) + '\u00a0' + symbol('konfetti') + '</span>';
}
/* Selbst gezeichnet (14.11.2026, siehe .zei im Stil): weiter (⏭, an den
   Ueberspringen-Knoepfen), pause (⏸) und stopp (⏹) beim Vorlesen der
   Geschichte, zu (✕) an "Lektion abbrechen", "Test abbrechen" und "Test
   beenden" - dort per data-zeichen, damit ein Sprachwechsel (applyTexts)
   es mitnimmt. Raster 24 x 24. Schmuck: aria-hidden, den Namen traegt das
   Wort daneben bzw. das aria-label des Stopp-Knopfs. Als Funktion mit den
   Formen darin, nicht als const: applyTexts darf es jederzeit rufen. */
function zeichen(name){
  const formen = {
    weiter: '<path d="M3.5 6.5 10.5 12 3.5 17.5Z M10.5 6.5 17.5 12 10.5 17.5Z"/>'
          + '<path d="M20.5 6.5v11" style="fill:none;stroke-width:2.6"/>',
    pause: '<rect x="5.5" y="5" width="4" height="14" rx=".6"/><rect x="14.5" y="5" width="4" height="14" rx=".6"/>',
    stopp: '<rect x="5.5" y="5.5" width="13" height="13" rx="1.2"/>',
    zu: '<path d="M6.5 6.5 17.5 17.5 M17.5 6.5 6.5 17.5"/>',
  };
  return '<svg class="zei zei-' + name + '" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
       + formen[name] + '</svg>';
}
function symbolTexte(vars){
  return Object.assign({herz: symbol('herz', t('stat.leben')),
                        muenze: symbol('muenze', SYMBOL_SAGT.muenze),
                        einstellungen: symbol('einstellungen', SYMBOL_SAGT.einstellungen)}, vars || {});
}
/* Alle einmal beim Start holen, wie die Flamme (FLAMME_BILDER): sonst
   stuende beim ersten Herz im Fragenkasten oder dem ersten Schloss einen
   Augenblick lang ein leerer Platz. Nur eigene Dateien. Die Liste haelt
   die Bilder fest, damit der Browser sie nicht wieder verwirft. */
const SYMBOLE = ['lernpfad', 'geschichten', 'wiederholen', 'muenze', 'herz', 'laden',
                 'einstellungen', 'profil', 'lautsprecher', 'schloss', 'herzgold',
                 'ziel', 'stern', 'herzblau', 'funken', 'brief', 'konfetti', 'play'];
const symbolVorrat = SYMBOLE.map(n => {
  const i = new Image(); i.src = 'symbole/' + n + '.webp';
  if(i.decode) i.decode().catch(() => {});
  return i;
});
/* ---- Ansagen fuer Screenreader (17.10.2026, WCAG 4.1.3) ----
   Schreibt eine kurze Meldung in die unsichtbare Region #ansage
   (aria-live="polite"). Erst leeren, dann kurz darauf fuellen: derselbe
   Text zweimal hintereinander ("Gekauft.") wuerde sonst kein zweites Mal
   vorgelesen. html ist schon maskiert - so kann ein bosnisches Wort als
   <span lang="bs"> mitkommen und klingt dann bosnisch statt deutsch.
   Nach ANSAGE_STEHT wird die Region wieder leer, damit beim Durchwischen am
   Seitenende keine alte Meldung steht. ansagen('') bricht eine wartende ab.
   WEITER_NACH: so lange wartet weiterBeiTipp(), bevor es den Fokus auf
   Weiter legt. Das Ergebnis einer Aufgabe kommt erst danach - der
   Fokuswechsel schnitte die Ansage sonst mitten im Wort ab. Weil beide
   Zeitgeber getrennt starten, setzt weiterBeiTipp() die Ansage nach dem
   Fokus noch einmal an (ansageNachFokus). */
const ANSAGE_STEHT = 6000, WEITER_NACH = 900;
let ansageUhr = 0, ansageWegUhr = 0, ansageText = '';
function ansagen(html, warte){
  const el = $('ansage'); if(!el) return;
  clearTimeout(ansageUhr); clearTimeout(ansageWegUhr);
  el.textContent = '';
  ansageText = html || '';
  if(!html) return;
  ansageUhr = setTimeout(()=>{
    el.innerHTML = html;
    ansageWegUhr = setTimeout(()=>{ el.textContent = ''; ansageText = ''; }, ANSAGE_STEHT);
  }, warte || 60);
}
/* Nach dem Fokus auf Weiter: eine noch wartende oder schon gelaufene
   Ansage des Ergebnisses einmal neu ansetzen, 80 ms nach dem Fokus. Der
   allererste Ton einer Sitzung legt den AudioContext an und braucht bis zu
   0,7 s; er laeuft zwischen der Rueckmeldung und done(). Dann kam die
   Ansage vor dem Fokuswechsel und wurde von ihm abgeschnitten (gemessen in
   der Code-Pruefung, 18.10.2026). Im Normalfall wartet sie noch und wird
   nur auf denselben Augenblick verschoben - doppelt kommt nichts. */
function ansageNachFokus(){ if(ansageText) ansagen(ansageText, 80); }
/* ABRUNDEN, nicht runden. Math.round machte aus 199 von 200 Wörtern glatte
   100 Prozent - die Anzeige stand auf 100, und mit TEST_FREI_AB=100 wäre der
   Test aufgegangen, obwohl ein Wort fehlt. Bei den heutigen Levelgrößen (bis
   40 Wörter) konnte das noch nicht passieren, bei einem größeren schon. */
const levelPct = c => { const n=c.words.length; return n ? Math.floor(c.words.filter(w=>known.has(w.id)).length/n*100) : 0; };
/* Der Vergleich läuft ueber ganze Zahlen und nicht ueber die Prozentanzeige:
   so hängt die Freigabe nicht daran, wie gerundet wird. */
const testAllowed = c => allesOffen() || passed.has(c.id) ||
  c.words.filter(w=>known.has(w.id)).length * 100 >= c.words.length * TEST_FREI_AB;
const typable = w => w.bs.length<=14 && !/[.…→]/.test(w.bs) && !w.bs.includes(' / ');
const today = () => { const d=new Date(); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); };
/* Ein Lerntag ist genau 'JJJJ-MM-TT'. Alles andere fliegt beim Einlesen raus:
   eine von Hand verbogene oder halb übertragene Sicherung würde die Serie
   sonst unbrauchbar machen, und man käme von allein nie wieder heraus.

   Die Form allein reicht nicht. '2026-13-99' hat sie auch, und so ein
   Eintrag kann zwar nie eine Serie verlängern - dayKey() liefert das nie -,
   er zählt aber bei days.size mit, und das ist die Zahl hinter "1000 Tage
   gelernt". Deshalb muss sich die Zeichenkette in ein echtes Datum
   verwandeln lassen und unverändert wieder herauskommen. Damit fällt auch
   der 29. Februar in einem Jahr ohne Schalttag heraus.

   Gerechnet wird über den Mittag: um Mitternacht verschiebt die
   Zeitumstellung das Datum. */
const istDatum = s => {
  if(typeof s !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
  const d = new Date(s + 'T12:00:00');
  return !isNaN(d.getTime()) && dayKey(d) === s;
};
/* ---- Der frueheste moegliche Tag (17.10.2026) ----
   Die Form allein reichte auch sonst nicht. Lerntage kommen aus einer
   Sicherungsdatei, und die kann jeder von Hand schreiben: ein Lerntag
   "1990-01-01" kam durch, seitNachEinlesen() setzte zmaj_seit auf ihn, und
   geschenkPruefen() rechnete 36 Jahre aus - fuenf Tage Vollversion. Mit
   1980, 1970 ... gleich noch einmal, beliebig oft. So in der
   Sicherheitspruefung am 17.10.2026 in Chrome gemessen. Ajdin dazu:
   "binde es am Handy-Datum".

   Vor APP_START kann es keinen Lerntag geben. Belegt am 17.10.2026: erster
   Commit am 19.09.2026, die Technikerarbeit laeuft ab dem 10.08.2026
   (PROJEKTMAPPE.md), der frueheste Tag in irgendeiner Sicherung oder
   Testdatei ist der 04.08.2026 (testdaten/zmaj-screenshots.json), auf einem
   echten Handy der 18.08.2026. Lieber ein paar Tage zu frueh als einen
   echten Lernenden abzuschneiden - deshalb der Monatserste davor.
   Verglichen wird als Zeichenkette: 'JJJJ-MM-TT' sortiert wie das Datum. */
const APP_START = '2026-08-01';
/* Ein Tag aus einer Sicherungsdatei: echtes Datum, nicht vor APP_START und
   nicht nach heute - heute nach der Uhr des Handys, wie today(). Beim
   normalen Laden gilt nur die untere Grenze, siehe standUebernehmen(). */
const tagMoeglich = s => istDatum(s) && s >= APP_START && s <= today();

/* NFC in norm() (12.11.2026, Pruefung "Fast richtig"): ein Haekchen kann als
   eigenes Zeichen hinter dem Buchstaben kommen ("s" + U+030C statt "š", beim
   Einfuegen aus manchen Programmen). Ohne NFC war das richtig Getippte nur
   'almost', und die App sagte "Mit Sonderzeichen", obwohl sie dastanden. */
function matches(guess, answer){
  const g = guess.trim(); if(!g) return 'leer';
  const norm = s => s.normalize('NFC').toLowerCase().replace(/[.!?…]+$/,'').replace(/\s+/g,' ').trim();
  const alts = answer.split(' / ');
  if(alts.some(a => norm(a) === norm(g))) return 'ok';
  /* Getippte Zahlen zaehlen genauso: wer "5" schreibt, meint "pet".
     Erst der Zahlwert, dann der ausgeschriebene Satz - so gilt auch
     "Nalazimo se u 5".
     Fehlen dabei nur Haekchen ("sest" fuer "šest", "cetiri" fuer "četiri"),
     ist es 'almost' wie bei jedem anderen Wort. Bis zum 12.11.2026 sagte
     zahlWert(), das selbst ohne Haekchen vergleicht, hier 'ok', und die App
     zeigte "Tačno!" statt der Schreibweise. Die Ziffer "6" und "dva" fuer
     "Dvije" bleiben 'ok'. */
  const zg = zahlWert(g);
  if(zg !== null && alts.some(a => zahlWert(a) === zg)) return alts.some(a => clean(a) === clean(g)) ? 'almost' : 'ok';
  if(alts.some(a => norm(zahlenAusschreiben(a)) === norm(zahlenAusschreiben(g)))) return 'ok';
  if(alts.some(a => fastGleich(a, g))) return 'almost';
  return 'no';
}
/* Gleich bis auf Haekchen, Gross/klein, Satzzeichen am Ende, Komma und
   Bindestrich - das ist 'almost' in matches(), und gemeinteAntwort() sucht
   damit die Antwort, die gemeint war. */
function fastGleich(a, g){
  const cg = clean(g);
  return clean(a) === cg
    /* Ziffer und fehlendes Haekchen zusammen: "5 brace" fuer "pet braće",
       "7 cevapa" fuer "sedam ćevapa". Bis zum 12.11.2026 war das 'no' und
       kostete ein Leben, "5 braće" galt dagegen. */
    || clean(zahlenAusschreiben(a)) === clean(zahlenAusschreiben(g))
    // Ohne den Bindestrich auch ohne die Luecke: "sogandolma" fuer "sogan-dolma".
    || (a.includes('-') && clean(a.replace(/-/g,'')) === cg);
}
/* Welche Antwort gemeint war, wenn matches() 'almost' sagt - fuer "Richtig!
   Mit Sonderzeichen: {wort}". Bis zum 12.11.2026 stand dort immer die erste
   Antwort: wer bei "Auf Wiedersehen" "cao" tippte, las "Mit Sonderzeichen:
   Doviđenja", bei "Auf die Gesundheit!" mit "zivjeli" "U zdravlje!" - ein
   anderes Wort als das getippte.
   Betroffen waren 136 schreibbare Woerter, deren "auch" Haekchen hat (dazu
   gleich uebersetzte aus annehmbar()), und ein Lueckensatz (adžo fuer
   amidža). Die erste Antwort, die fast gleich ist, gewinnt; passt keine,
   bleibt es die erste. */
function gemeinteAntwort(guess, answer){
  const g = String(guess || '').trim(), alts = String(answer || '').split(' / ');
  return alts.find(a => fastGleich(a, g)) || alts[0];
}
/* Welche richtige Antwort einer FALSCHEN Eingabe am naechsten liegt - fuer
   "Richtig waere: {wort}" (17.11.2026, Offen-Liste 7). Ajdin beim Handytest:
   "ich wollte extra falsch machen damit ich sehe ob man auch sieht was bei
   der version die man geschrieben hat falsch ist er zeigt leider nur die
   normale form an". Wer bei "Vielen Dank" zweimal "Mnogo hvla" tippte, las
   "Richtig waere: Hvala puno" und erfuhr nicht, dass bei "Mnogo hvala" nur
   ein a fehlte. Jetzt steht dort "Mnogo hvala", und die Loesung darunter
   zeigt mit "Auch richtig:" die Hauptform (loesung() in renderTask).
   answer wie bei matches(), mit " / " getrennt - dieselben Antworten, die
   dort als richtig gelten (Hauptform, auch, auch_var, gleich uebersetzte).
   haupt ist, was bisher dastand: w.bs bzw. s.answer.
   Gemessen wird abstand() (Levenshtein) auf den Formen von clean(), wie bei
   fastGleich() und fastRichtig(): Gross/klein, Haekchen, Satzzeichen am
   Ende, Komma und Bindestrich zaehlen nicht, Ziffern auch ausgeschrieben.
   Bei gleichem Abstand gewinnt die frueher genannte Antwort, zuerst also
   die Hauptform. Es bleibt bei haupt,
   - wenn die naechste Antwort ein Teil von haupt ist ("vrlo" aus
     "vrlo / veoma" - die getippte Form steht dann schon mit da);
   - wenn die Eingabe keiner Antwort nahe ist: mehr als die Haelfte der
     Buchstaben der naechsten Antwort anders ("ne znam", ein ganz anderes
     Wort). Dann waere jede Form geraten, und es steht wie bisher die
     Hauptform da.
   Was als richtig, fast richtig oder falsch zaehlt, aendert sich dadurch
   nicht - nur, welche Form als Loesung dasteht. */
function naechsteAntwort(guess, answer, haupt){
  const g = String(guess || '').trim();
  if(!g) return haupt;
  const cg = clean(g), zg = clean(zahlenAusschreiben(g));
  let beste = null, bester = Infinity;
  String(answer || '').split(' / ').forEach(a => {
    const d = Math.min(abstand(clean(a), cg), abstand(clean(zahlenAusschreiben(a)), zg));
    if(d < bester){ bester = d; beste = a; }
  });
  if(beste === null || 2 * bester > clean(beste).length) return haupt;
  return String(haupt).split(' / ').includes(beste) ? haupt : beste;
}

/* ---------- Fast richtig: erst ein Hinweis, nicht gleich falsch ----------
   Ajdin am 24.10.2026: "wenn man beim schreiben ausversehen einen buchstaben
   falsch geschrieben hat dann soll ein hinweis kommen das wort ist falsch
   geschrieben und nicht das es direkt falsch ist weil sowas schnell
   passieren kann". Von den Vorschlaegen hat er B gewaehlt ("b"):
   - Liegt die Eingabe GENAU EINEN Tippfehler neben einer richtigen Antwort,
     kommt ein gelber Hinweis (task.fast_richtig). Die Loesung verraet er
     nicht.
   - Die Eingabe bleibt offen, der zweite Versuch zaehlt wie immer: richtig
     oder "fast richtig" ist richtig, alles andere falsch. Ein Hinweis je
     Aufgabe, er kostet kein Leben und spielt keinen Ton (tippHinweis() in
     renderTask).
   - Erst ab 4 Buchstaben der Antwort. Bei "sir" ist ein anderer Buchstabe
     schon ein Drittel des Wortes.
   Am 27.10.2026 kam im Lueckensatz die andere Endung dazu ("Auch bei Endung
   Hinweis": "nedjelji" fuer "nedjelja"), zuerst mit eigenem Text. Auf die
   Rueckfrage, ob der Hinweis auch kommen soll, wenn das Getippte ein anderes
   echtes Wort ist ("zvono" - Klingel - fuer "zvoni" - klingelt), sagte Ajdin
   am selben Tag: "mach doch einfach nur fast richtig dann bezieht es sich
   auf alle wörter und wenn es ein andere wort ist ist doch egal es ist doch
   trotzdem fast richtig". Seitdem gilt eine Regel fuer Schreibaufgabe und
   Lueckensatz: ein Tippfehler Abstand, ein Text, "Fast richtig!".
   Weggefallen sind dabei
   - die Ausnahme fuer echte Woerter (echteWoerter()): bis dahin bekam
     "deset" fuer "devet" keinen Hinweis, weil wer zehn fuer neun schreibt,
     sich nicht vertippt, sondern die Zahlen verwechselt hat;
   - der eigene Hinweis auf die Endung (nurEndung(), task.endung) und
     andereEndung(), nach der eine andere Endung im Lueckensatz kein
     Tippfehler war. Eine andere Endung ist immer auch ein Tippfehler
     Abstand - ein Buchstabe anders oder einer mehr -, die eine Regel deckt
     sie mit ab.
   Verglichen wird auf den Formen von clean(): ohne Haekchen, Gross/klein,
   Satzzeichen am Ende, Komma und Bindestrich. Fehlen nur Haekchen, hat matches() schon 'almost'
   gesagt - hierher kommt nur, was 'no' war. So vermischt sich nichts: ein
   fehlendes Haekchen ist nie "der eine Tippfehler", und bei "kruskq" fuer
   "kruška" ist es genau einer (q statt s), das Haekchen zaehlt nicht mit. */

/* Genau ein Tippfehler zwischen a und b: ein Buchstabe ersetzt, einer
   fehlt, einer zu viel, oder zwei Nachbarn vertauscht - der Abstand 1 nach
   Damerau-Levenshtein in der eingeschraenkten Form (OSA). Fuer genau 1
   braucht es keine Tabelle: bis zur ersten Abweichung ist alles gleich,
   dahinter muss der Rest passen. */
function einTippfehler(a, b){
  if(a === b || Math.abs(a.length - b.length) > 1) return false;
  let i = 0;
  while(i < a.length && i < b.length && a[i] === b[i]) i++;
  if(a.length === b.length)
    return a.slice(i + 1) === b.slice(i + 1) ||                                         // ersetzt
           (a[i] === b[i + 1] && a[i + 1] === b[i] && a.slice(i + 2) === b.slice(i + 2));  // vertauscht
  const [lang, kurz] = a.length > b.length ? [a, b] : [b, a];
  return lang.slice(i + 1) === kurz.slice(i);                                           // fehlt, zu viel
}

/* Bekommt diese Eingabe den Hinweis? antworten wie bei matches(), mit
   " / " getrennt - jede richtige Antwort wird geprueft. Die 4 Buchstaben
   zaehlen an der Antwort, nicht an der Eingabe: "voad" fuer "voda" bekommt
   den Hinweis, "sur" fuer "sir" nicht. Gezaehlt werden getippte Zeichen
   nach clean(): lj, nj und dž sind zwei Tasten, "konj" und "džem" haben
   also 4 - vertippen kann man sich auf jeder Taste. Ob sie wie im Alphabet
   als ein Buchstabe zaehlen sollen, war am 24.10.2026 noch offen; auf die
   Rueckfrage am 27.10.2026 blieb es bei zwei. */
function fastRichtig(eingabe, antworten){
  const g = clean(String(eingabe || ''));
  return !!g && String(antworten || '').split(' / ').map(clean).some(a =>
    (a.match(/[a-z]/g) || []).length >= 4 && einTippfehler(g, a));
}
/* So lange nach dem Hinweis ist derselbe Text noch kein zweiter Versuch,
   siehe tippHinweis(). */
const DOPPELT_MS = 1000;

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
