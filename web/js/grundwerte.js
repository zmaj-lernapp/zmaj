/* Der Inhalt kommt aus vokabeln.py, grammatik.py und geschichten.py – hier muss nichts geändert werden. */
/* Alles geladen? (20.11.2026, Release/Aufteilung/PLAN.md 4 und G3, G7)
   Das Skript kann in Dateien unter js/ geteilt sein. Zwischen zwei Dateien
   kann der Browser andere Aufgaben ausfuehren (in WebKit gemessen): ein
   Horcher, der beim Laden angemeldet wird, koennte dann feuern, bevor die
   Dateien mit seinen Funktionen da sind. Die Horcher, die in spaetere
   Dateien greifen, fragen darum zuerst skripteDa. Es wird direkt vor init()
   wahr; danach ist alles wie in der ungeteilten Datei.
   teileDa zaehlt die Teile, die ganz durchgelaufen sind: am Ende jedes
   Teils steht die Zeile "var teileDa = (teileDa || 0) + 1;". Wirft ein Teil
   beim Laden, fehlt seine Zeile, und die App startet nicht mit halbem
   Zustand, sondern zeigt einen Fehler (teileFehlen, ganz unten). Ungeteilt
   zaehlt es einfach bis TEILE_ERWARTET.
   Bewusst var und nicht let/teileDa++: Tests schneiden Stuecke aus dem
   Skript und lassen sie in node laufen (test_haekchen, test_varianten, ...).
   Endet so ein Stueck an einer Teilgrenze, enthaelt es die Zeile, aber nicht
   diese hier - mit var ist das kein ReferenceError, und ueber mehrere
   Skripte hinweg darf var dieselbe Bindung wieder nennen. */
let skripteDa = false;
var teileDa = 0;
/* Wo die App laeuft: 'android', 'ios' oder 'web'. Entschieden wird es EIN
   Mal, im kleinen Skript im Kopf (ZMAJ_PLATTFORM), damit Stil und Skript
   nie verschieden antworten. Alles, was iPhone und iPad anders machen,
   haengt an dieser einen Konstante (30.10.2026, iOS_Plan.md 3.5). */
const PLATTFORM = (window.ZMAJ_PLATTFORM === 'android' || window.ZMAJ_PLATTFORM === 'ios')
  ? window.ZMAJ_PLATTFORM : 'web';
const IST_IOS = PLATTFORM === 'ios';
const LEKTION_WOERTER = 10;     // Wortaufgaben pro Lektion
const LEKTION_NEU_MAX = 5;       // davon höchstens so viele neue Wörter (wenn es schon bekannte gibt)
const LEKTION_LUECKEN = 2;       // Lückentexte pro Lektion
const LEKTION_KACHELN = 2;       // Sätze aus Kacheln pro Lektion (wenn ihre Wörter schon dran waren), seit 13.10.2026
/* Ohne Gleiten legen die Kacheln, wer am Handy "Bewegung reduzieren"
   eingestellt oder in der App den Schalter "Animationen" ausgeschaltet hat.
   Bis zum 17.10.2026 stand hier eine Konstante: sie las nur die
   Geraeteeinstellung, und die nur einmal beim Start - der Schalter in der App
   blieb ohne Wirkung, weil .no-anim nur CSS-Bewegung abschaltet und das
   Gleiten ueber k.animate() laeuft. Jetzt wird bei jedem Legen gefragt, genau
   wie zmajRuht() es fuer den Drachen tut. */
function kachelnRuhig(){
  if(document.body.classList.contains('no-anim')) return true;
  try{ return matchMedia('(prefers-reduced-motion: reduce)').matches; }
  catch(e){ return false; }
}
const LEKTION_GRAMMATIK = 2;     // Grammatik-Aufgaben pro Lektion (wenn vorhanden)
/* Ajdin am 27.09.2026: "mach die pruefung statt bei 80% auf 100% sonst lernt
   man nicht alles". Der Test geht jetzt erst auf, wenn JEDES Wort des Levels
   einmal richtig beantwortet war. Das kostet je Level ein paar Lektionen mehr -
   buildLesson() nimmt aber immer zuerst die noch unbekannten Wörter, es kann
   also keine Sackgasse geben, in der ein Wort nicht mehr dran kommt. */
const TEST_FREI_AB = 100;        // Prozent bekannter Wörter, ab denen der Level-Test frei ist
const TEST_FRAGEN = 10, TEST_WIEDERHOLUNG = 3, TEST_BESTANDEN_AB = 8;
const LEBEN_MAX = 5;               // Leben für die ganze App
const LEBEN_NACHFUELLEN_MIN = 120; // Minuten, bis ein Leben nachwächst (Vollversion: unbegrenzt)
/* Münzen: 10 je geschaffter Tagesaufgabe, also höchstens 30 am Tag.
   Die Preise im Laden sind daran gemessen. Die Vollversion gibt es
   ausdrücklich NICHT für Münzen – siehe ANLEITUNG.md. */
const MUENZEN_PRO_QUEST = 10;
/* Zwei Sorten Ware. Oben, was sich verbraucht - unten der Zierrat fuer den
   Drachen, der einmal gekauft bleibt. Es kann immer nur ein Stueck getragen
   werden. Die Preise sind an 30 Muenzen am Tag gemessen. */
const VERBRAUCH = [
  {id:'herz',   preis:100, titel:'laden.herz',   sub:'laden.herz_sub',
   geht:()=> !unlimited() && lives.anzahl < LEBEN_MAX},
  {id:'schutz', preis:300, titel:'laden.schutz', sub:'laden.schutz_sub',
   geht:()=> schutzNow() < SCHUTZ_MAX}
];
/* Zierrat in fuenf Gruppen - Kopf, Brille, Hals, Farbe, Effekt. Das sind
   zugleich die Reiter im Laden. Aus jeder Gruppe kann ein Stueck getragen
   werden, alle fuenf zusammen. Die Reihenfolge
   hier ist die Reihenfolge im Laden: das Guenstigste zuerst.
   Die Kennungen muessen zu den Dateien web/maskottchen/zmajz-<id>.json
   passen, die zmaj_lottie.py erzeugt. */
const ZIERRAT = [
  {id:'ohrenschuetzer', gruppe:'kopf',   preis:600},
  {id:'kappe',          gruppe:'kopf',   preis:700},
  {id:'fes',            gruppe:'kopf',   preis:900},
  {id:'kopfhoerer',     gruppe:'kopf',   preis:1200},
  {id:'hut',            gruppe:'kopf',   preis:1500},
  {id:'doktorhut',      gruppe:'kopf',   preis:1800},
  {id:'krone',          gruppe:'kopf',   preis:2500},

  {id:'lesebrille',     gruppe:'brille', preis:400},
  {id:'sonnenbrille',   gruppe:'brille', preis:600},
  {id:'brille',         gruppe:'brille', preis:800},

  {id:'schal_winter',   gruppe:'hals',   preis:500},
  {id:'schal_bih',      gruppe:'hals',   preis:800},
  {id:'weste_strick',   gruppe:'hals',   preis:1000},
  {id:'weste_leder',    gruppe:'hals',   preis:1400},
  {id:'trikot',         gruppe:'hals',   preis:2000},

  /* Die Farbe des Drachen. Sie ist kein Kleidungsstueck, wird aber genauso
     gekauft und getragen - deshalb steht sie hier mit drin und laeuft durch
     dieselbe Mechanik. Blau braucht keinen Eintrag: nichts getragen heisst
     blau, so wie kein Hut getragen "ohne Hut" heisst. */
  {id:'gruen',          gruppe:'farbe',  preis:900},
  {id:'rosa',           gruppe:'farbe',  preis:1100},
  {id:'rot',            gruppe:'farbe',  preis:1300},
  {id:'lila',           gruppe:'farbe',  preis:1600},
  {id:'nacht',          gruppe:'farbe',  preis:2200},

  /* Nur mit der Vollversion. Kein Preis: sie lassen sich nicht kaufen,
     weder fuer Muenzen noch sonstwie. Sie sind da, solange das Abo
     laeuft - auch in der Probezeit und in den fuenf Geschenktagen - und
     der Drache legt sie ab, wenn es ausgelaufen ist.
     Kein Vorteil im Spiel: ein Hut beantwortet keine Aufgabe. */
  {id:'krone_gross',    gruppe:'kopf',   voll:true},
  {id:'monokel',        gruppe:'brille', voll:true},
  {id:'umhang',         gruppe:'hals',   voll:true},
  {id:'gold',           gruppe:'farbe',  voll:true},
  {id:'silber',         gruppe:'farbe',  voll:true},
  {id:'kupfer',         gruppe:'farbe',  voll:true},
  {id:'galaxie',        gruppe:'farbe',  voll:true},

  /* Eigene Gruppe, damit es sich mit Farbe und Kleidung vertraegt: aus
     jeder Gruppe sitzt nur ein Stueck, im Farbreiter wuerde das Funkeln
     die Galaxie herunterschieben. Vorher lief es an der Warenliste
     vorbei und liess sich deshalb nicht abnehmen. */
  {id:'funkeln',        gruppe:'effekt', voll:true},
].map(w => Object.assign(w, {
  titel: 'laden.' + w.id, sub: 'laden.' + w.id + '_sub',
  geht: w.voll ? (() => unlimited()) : (() => !hatStueck(w.id)),
}));
const VOLL_STUECKE = new Set(ZIERRAT.filter(w => w.voll).map(w => w.id));
const istVollStueck = id => VOLL_STUECKE.has(id);
const GRUPPEN = [
  {id:'vorrat', titel:'laden.verbrauch'},
  {id:'kopf',   titel:'laden.reiter_kopf'},
  {id:'hals',   titel:'laden.reiter_hals'},
  {id:'brille', titel:'laden.reiter_brille'},
  {id:'farbe',  titel:'laden.reiter_farbe'},
  {id:'effekt', titel:'laden.reiter_effekt'},
];
const gruppeVon = id => { const w = ZIERRAT.find(x => x.id === id); return w ? w.gruppe : ''; };

/* Die Einstellungen dieses Geräts hießen früher rijec_… – aus der Zeit,
   als die App noch „riječ.“ hieß. Einmal umbenennen, damit Sprache, Ton
   und Stimme beim Umstieg nicht verlorengehen. Kann irgendwann raus. */
try{
  ['sprache','sound','haptik','anim','voice','werbung'].forEach(k => {
    const alt = localStorage.getItem('rijec_' + k);
    if(alt === null) return;
    if(localStorage.getItem('zmaj_' + k) === null) localStorage.setItem('zmaj_' + k, alt);
    localStorage.removeItem('rijec_' + k);
  });
}catch(e){}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
