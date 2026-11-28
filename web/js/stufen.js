/* ---- Stufen-Reiter (13.11.2026) ----
   Der Lernpfad steht in Reitern je Stufe: A1, A2, B1, B2 und C1, das noch
   leer ist ("bald"). Ajdin am 08.11.2026: "wir machen am besten alle
   getrennt"; am 13.11.2026 Variante B aus Release\Entscheidungen_2026-11-13
   (reiter.md, "alles wie empfohlen"): Reiter, zwei neue Grundwort-Level,
   Zuhause hinter Faelle 1.
   Die Stufe steht an der Sektion (vokabeln.py, "stufe"). Freigeschaltet wird
   weiter in EINER Kette ueber alle Reiter (isUnlocked) - die Reiter zeigen
   sie nur aufgeteilt. Ein Reiter ist offen, sobald eins seiner Level offen
   ist; vorher geht es mit dem Sprung-Test (SPRUNG-TEST weiter unten).
   Farben, Sektions- und Levelnummern fangen in jedem Reiter neu an. So kommt
   auf einer Seite keine Farbe doppelt vor (Farben-Entscheidung vom
   27.09.2026), solange ein Reiter hoechstens neun Sektionen hat. B2 hatte
   vierzehn und ist seit Frage 6a (13.11.2026, "ja") auf neun zusammengelegt
   (vokabeln.py); tests/test_reiter.py haelt die Grenze fest.
   Gerechnet wird einmal je Inhalt (stufenKarte), nicht fuer jedes Level. */
const STUFEN = ['A1', 'A2', 'B1', 'B2', 'C1'];
let _stufen = null;
function stufenKarte(){
  if(_stufen && _stufen.kat === CATEGORIES && _stufen.sek === SECTIONS) return _stufen;
  const vonSek = {}, sektionen = {}, level = {};
  STUFEN.forEach(st => { sektionen[st] = []; level[st] = []; });
  let vorige = STUFEN[0];
  SECTIONS.forEach(s => {
    /* Ohne gueltige Stufe gehoert eine Sektion zum Reiter davor - so faellt
       keine aus dem Lernpfad heraus. */
    const st = STUFEN.indexOf(s.stufe) >= 0 ? s.stufe : vorige;
    vorige = st; vonSek[s.id] = st; sektionen[st].push(s);
  });
  const vonLevel = [], nr = [];
  CATEGORIES.forEach((c, i) => {
    const st = vonSek[c.sektion] || STUFEN[0];
    vonLevel[i] = st; level[st].push(i); nr[i] = level[st].length;
  });
  _stufen = {kat: CATEGORIES, sek: SECTIONS, vonSek, sektionen, level, vonLevel, nr};
  return _stufen;
}
/* Der Reiter eines Levels. Der Zahnarzt-Teil steht in dem, in dem gerade
   gelernt wird (reiter.md: "im Reiter, in dem man gerade lernt"). */
const stufeVon = i => i >= CATEGORIES.length ? stufeVon(firstOpen()) : (stufenKarte().vonLevel[i] || STUFEN[0]);
const reiterLevel = st => stufenKarte().level[st] || [];
const reiterSektionen = st => stufenKarte().sektionen[st] || [];
/* Die Nummer, die der Lernende sieht: je Reiter von 1 (seit 13.11.2026), im
   Zahnarzt-Teil ebenso. */
const levelNummer = i => i < CATEGORIES.length ? (stufenKarte().nr[i] || i + 1) : i - CATEGORIES.length + 1;
/* So viele Level hat der Reiter von Level i - fuer "Level 3 von 31". */
const levelAnzahl = i => i < CATEGORIES.length ? reiterLevel(stufeVon(i)).length : zaLevel().length;
/* Bis wohin man von hier aus blaettern darf: ueber das letzte Level des
   Lernpfads geht es nicht in den versteckten Teil, und umgekehrt. */
const levelEnde = () => CATEGORIES.length + (imZa() ? zaLevel().length : 0);
const levelAnfang = () => imZa() ? CATEGORIES.length : 0;
const zaHoechster = () => {
  const L = zaLevel();
  for(let k = L.length - 1; k >= 0; k--) if(passed.has(L[k].id)) return k;
  return -1;
};
/* Der Schalter aus dem Stand: was von aussen kommt, wird hier gerade gezogen.
   Kein Zeitpunkt nach jetzt, wie bei den Sternen - sonst gewoenne eine
   vorgestellte Uhr jeden spaeteren Abgleich. */
function zaSchalterPruefen(roh){
  const e = (roh && typeof roh === 'object' && !Array.isArray(roh)) ? roh : {};
  const z = (typeof e.z === 'number' && isFinite(e.z) && e.z > 0) ? Math.min(e.z, Date.now()) : 0;
  return {an: e.an === true, z};
}
/* Zwei Geraete: die zuletzt getroffene Wahl gilt, sonst liesse sich der Teil
   nie wieder ausblenden. Bei gleicher Zeit "an", nur damit beide Richtungen
   dasselbe ergeben. */
function zaMischen(a, b){
  const x = zaSchalterPruefen(a), y = zaSchalterPruefen(b);
  if(x.z !== y.z) return x.z > y.z ? x : y;
  return {an: x.an || y.an, z: x.z};
}
const cur = () => levelNach(catIdx);
const curWords = () => cur().words;
const curSentences = () => SENTENCES.filter(s => s.kat === cur().id);
const byId = id => CATEGORIES.find(c => c.id === id) || zaLevel().find(c => c.id === id);
/* Offen ist alles bis zum hoechsten bestandenen Level plus eins - nicht nur
   der direkte Nachfolger.

   Vorher stand hier passed.has(CATEGORIES[i-1].id). Damit sperrt ein Level,
   das bei einer Aktualisierung mitten in eine schon durchgespielte Sektion
   eingeschoben wird, auf einen Schlag alles dahinter zu: Level 20 ist neu
   und nicht bestanden, also sind 21 bis 43 wieder verschlossen, obwohl sie
   laengst geschafft sind. Von aussen sieht das aus, als haette das Update
   den Fortschritt gefressen.

   Das ist kein erfundener Fall: vokabeln.py schreibt woertlich vor, neue
   Level an der passenden Stelle einzuschieben. Der dokumentierte Arbeitsweg
   fuehrte also genau in diesen Fehler. Gefunden am 18.09.2026.

   Dazu gehoert eine Regel, die nirgends erzwungen werden kann: die
   Kennungen der Level duerfen sich bei einer Aktualisierung nie aendern -
   "bestanden" merkt sich die Kennung, nicht die Nummer. */
const hoechsterBestanden = () => {
  for(let k = CATEGORIES.length - 1; k >= 0; k--) if(passed.has(CATEGORIES[k].id)) return k;
  return -1;
};
/* Die Einstufung macht zusaetzlich alles bis zu ihrem Einstieg frei.
   "Dran" ist dann das erste offene Level AB dem Einstieg - sonst zeigte
   Weitermachen nach der Einstufung wieder auf Level 1. Ausnahme: wer
   trotzdem von vorn lernt, siehe firstOpen.
   Seit 13.11.2026 genauso der Sprung-Test in einen Reiter (sprungIndex):
   offen ist alles bis zum ersten Level des Reiters. Alle drei Grenzen
   rechnet freiBis(), zahlLevelHinter() nimmt dieselbe.
   Das "plus eins" springt ueber Level, die eine alte Einstufung ohnehin
   offen haelt (altEingestuftOffen, zweite Pruefung vom 13.11.2026): wer
   in 1.3 bei "Fragen stellen" eingestiegen ist und Faelle 1 besteht, hat
   danach Faelle 2 offen wie in 1.3, obwohl Zuhause jetzt dazwischen steht. */
const freiBis = () => {
  let n = hoechsterBestanden() + 1;
  while(altEingestuftOffen(n)) n++;
  return Math.max(n, einstufungIndex(), sprungIndex());
};
/* Angefangene Level bleiben offen (13.11.2026, reiter.md). Seit Zuhause
   hinter Faelle 1 steht, laege ein Level, in dem jemand gerade lernt, sonst
   ploetzlich hinter dem Schloss - wer in "Kueche & Bad" Woerter gelernt,
   "Natur" aber als letztes bestanden hat, kaeme nicht mehr hinein.
   Angefangen heisst: mindestens ein Wort des Levels ist gewusst. Woerter
   gehoeren genau einem Level (die Kennung ist eindeutig), gewusst wird ein
   Wort nur in einer Lektion dieses Levels - also war es schon einmal offen.
   Die zwei neuen Grundwort-Level sind fuer alle offen, die ihre Woerter aus
   B1 schon kennen; dort stehen sie ohnehin vor dem hoechsten bestandenen. */
const levelAngefangen = i => { const c = CATEGORIES[i]; return !!c && c.words.some(w => known.has(w.id)); };
const isUnlocked = i => {
  /* Beim Zahnarzt: dieselbe Regel, nur innerhalb des Teils. Der Stand im
     Lernpfad und die Einstufung spielen dort keine Rolle. */
  if(i >= CATEGORIES.length && CATEGORIES.length) return allesOffen() || i - CATEGORIES.length <= zaHoechster() + 1;
  return inDerKette(i) || levelAngefangen(i);
};
/* Offen ueber die Kette allein, ohne die angefangenen Level. Danach
   richtet sich, ob ein ganzer Reiter offen ist (stufeStand).
   Dazu kommt, was eine Einstufung von vor den Reitern abgedeckt hat und
   jetzt hinter ihrem Einstieg liegt (zweite Pruefung vom 13.11.2026). In
   1.3 fragte Stufe 2 der Einstufung auch "Zuhause" ab (EINSTUFUNG_STUFEN
   damals: anfassen, tiernatur, zuhause2); wer sie bestand, stieg bei
   "Fragen stellen" ein und hatte Zuhause offen. Seit Zuhause hinter
   Faelle 1 steht, waeren die fuenf Level wieder zu und der Reiter A2 mit
   ihnen - zu oeffnen nur ueber den Sprung-Test, der Leben kostet. Die
   anderen alten Einstiege (obst, zukunft, einkauf_orte, formell) haben
   alles, was sie in 1.3 abdeckten, auch jetzt vor sich; nachgerechnet mit
   der Levelfolge von 1.3 in data/vocabulary.json. Kennungen statt
   Nummern, wie bei "bestanden". */
const ALT_EINSTUFUNG_OFFEN = {fragen: ['zuhause2']};
const altEingestuftOffen = i => {
  if(!vorDenReiternEingestuft() || !CATEGORIES[i]) return false;
  const sek = ALT_EINSTUFUNG_OFFEN[einstufung.bis];
  return !!sek && sek.indexOf(CATEGORIES[i].sektion) >= 0;
};
const inDerKette = i => allesOffen() || i === 0 || i <= freiBis() || altEingestuftOffen(i);
/* "Dran" ist das erste nicht bestandene Level ab dem Einstieg. Danach
   richten sich der Weitermachen-Knopf, die markierte Stelle im Lernpfad,
   die beim Start aufgeklappte Sektion und die Farbe der App.

   So will es Ajdin, festgelegt am 01.11.2026 nach zwei Umwegen:
     - "ich bin level 10 das heisst level 1 bis 9 hab ich fertig und wenn
       ich zb auf level 8 kurz eine lektion mache soll der knopf trotzdem
       bei level 10 bleiben" - Nachueben in bestandenen Leveln aendert
       nichts, denn bestanden bleibt bestanden.
     - "wenn ein neues level dazu kommt wegen einen update ... bin level
       10 und es kommt ein neues level 5 hinzu dann springt der button auf
       level 5 und erst wenn es fertig ist springt er wieder auf level 10" -
       ein eingeschobenes Level ist das erste nicht bestandene, also dran.
     - Der Einstieg zaehlt nur, solange man auch dort lernt. Ajdins
       Test-App war am 26.10. auf Level 65 eingestuft, er hat aber Level 1
       bis 9 bestanden - und der Knopf stand auf "Arzt & Versicherung".
       "bin aber noch bei level 10 die hab ich noch nicht fertig gemacht".
       Wer vor dem Einstieg etwas bestanden hat und ab dem Einstieg noch
       nichts, lernt von vorn: dann gilt das erste nicht bestandene Level
       ueberhaupt. Ohne etwas bestanden oder mit einem bestandenen Level ab
       dem Einstieg bleibt es beim Einstieg.
   Verworfen: der Knopf im Level der letzten Lektion (Feld letzte_lektion)
   und der Knopf immer hinter dem hoechsten bestandenen, der eingeschobene
   Level uebersprungen haette. Beide erschienen nie.
   Seit 13.11.2026 ist ein bestandener Sprung-Test ein Einstieg wie die
   Einstufung: wer danach im neuen Reiter etwas besteht, macht dort weiter;
   wer es nicht tut, lernt dort weiter, wo er war.
   Die zwei Grundwort-Level (GRUNDWORT_LEVEL) sind fuer alle "dran", die vor
   den Reitern eingestuft wurden (Pruefung vom 13.11.2026): ihre 40 Woerter
   standen damals noch vor ihnen in B1, jetzt liegen sie im uebersprungenen
   A-Teil - ohne diese Ausnahme kaemen sie nie dran, obwohl reiter.md sagt
   "Wer schon weiter ist, hat sie danach als 'dran'". Wer mit den Reitern
   eingestuft wird (einstufung.reiter), hat sie mit A1 und A2 bewusst
   uebersprungen; der Ergebnisschirm sagt ihm "Du steigst in B1 ein", und
   dabei bleibt es. Ebenso nach einem Sprung-Test, der gibt es nur mit den
   Reitern.
   Fuer diese alten Einstufungen zaehlen die Grundwort-Level nicht als
   "vor dem Einstieg bestanden" (zweite Pruefung vom 13.11.2026): sonst
   galt nach dem ersten bestandenen Grundwort-Level "lernt von vorn", und
   Weitermachen sprang von "Kleine Woerter" auf Level 1 statt zu "Woerter
   fuer jeden Tag" bzw. zum Einstieg. Sie liegen ja nur durch das Update
   vor dem Einstieg; wer sie besteht, hat nicht von vorn angefangen.
   Was eine alte Einstufung offen haelt, obwohl es jetzt hinter ihrem
   Einstieg steht (ALT_EINSTUFUNG_OFFEN, bei "fragen" Zuhause), ist
   ebenso wenig "dran", solange ab dem Einstieg gelernt wird: in 1.3 lag
   es vor dem Einstieg, Weitermachen fuehrte nie hinein. Wer von vorn
   lernt, bekommt es in der Reihe. */
const GRUNDWORT_LEVEL = ['kleine_woerter', 'jeden_tag'];
const vorDenReiternEingestuft = () => !!(einstufung && einstufung.bis && !einstufung.reiter);
/* Ab welchem Level "dran" gesucht wird: der Einstieg, oder 0 fuer "lernt
   von vorn". firstOpen() und naechstesOffenes() rechnen damit. */
const dranAb = () => {
  const ein = Math.max(einstufungIndex(), sprungIndex()), alt = vorDenReiternEingestuft();
  let h = -1;
  for(let k = CATEGORIES.length - 1; k >= 0; k--)
    if(passed.has(CATEGORIES[k].id) && !(alt && GRUNDWORT_LEVEL.indexOf(CATEGORIES[k].id) >= 0)){ h = k; break; }
  return (ein > 0 && (h < 0 || h >= ein)) ? ein : 0;
};
const firstOpen = () => {
  const ab = dranAb();
  if(ab > 0 && vorDenReiternEingestuft()){
    const g = CATEGORIES.findIndex((c, k) => k < ab && GRUNDWORT_LEVEL.indexOf(c.id) >= 0 && !passed.has(c.id));
    if(g >= 0) return g;
  }
  let i = CATEGORIES.findIndex((c, k) => k >= ab && !passed.has(c.id) && !(ab > 0 && altEingestuftOffen(k)));
  if(i < 0) i = CATEGORIES.findIndex(c => !passed.has(c.id));
  return i < 0 ? CATEGORIES.length-1 : i;
};
/* Welche Sektion gerade dran ist. Die Antwort faerbt die ganze App, siehe
   :root[data-sek=...] im Stil. Gerechnet wird ueber das naechste offene
   Level, nicht ueber die gerade gezeigte Seite: sonst wechselte die Farbe
   beim Blaettern durch die Einstellungen.
   Es gibt neun Sektionen und neun Farben, eine je Sektion. Bis zum
   27.09.2026 waren es sechs, und die Sektionen 7 bis 9 trugen deshalb
   wieder die Farben von 1 bis 3 - beim Durchscrollen sah man denselben
   Bogen zweimal. Der Rest bleibt trotzdem stehen: kommt irgendwann eine
   zehnte Sektion dazu, faengt sie wieder bei der ersten Farbe an statt
   ohne Farbe dazustehen. */
let farbUhr = 0;
let offeneSektion = null;        // welche Sektion offen ist
                                 // null = noch nie gesetzt, '' = alle zu

/* Die Nummer der Farbe zu einer Sektion. Neun Sektionen, neun Farben.
   Der Rest greift erst ab einer zehnten.
   Seit 13.11.2026 je Reiter: die erste Sektion jedes Reiters traegt die
   erste Farbe, wie im Lernpfad (showPath). Der Zahnarzt-Teil steht unten im
   Reiter, in dem gerade gelernt wird, und nimmt die Farbe danach. */
function sektionsNummer(id){
  let i;
  if(ZA && id === ZA.sektion.id) i = reiterSektionen(stufeVon(firstOpen())).length;
  else {
    const k = stufenKarte(), st = k.vonSek[id];
    i = st ? k.sektionen[st].findIndex(s => s.id === id) : -1;
  }
  return String((i < 0 ? 0 : i) % 9 + 1);
}

/* Auf- und Zuklappen. Ein Tipp auf einen anderen Kopf klappt den auf und
   den bisherigen zu. Ein Tipp auf den Kopf der offenen Sektion klappt sie
   zu - dann ist keine offen und der Lernpfad steht als reine Uebersicht
   da. Ajdin am 26.09.2026: "die sektion soll sich auch zuklappen koennen
   wenn man nochmal ganz oben drauf drueckt".
   Es wird nicht neu gezeichnet, nur umgeschaltet - das ist billiger und
   laesst die Stelle stehen, an der man gerade liest. */
function sektionAufklappen(id){
  const box = $('sections'); if(!box) return;
  /* Wo sitzt der angetippte Kopf gerade auf dem Bildschirm? Klappt gleichzeitig
     eine Sektion WEITER OBEN zu, fallen dort mehrere hundert Pixel weg, alles
     darunter rutscht nach oben, und der angetippte Kopf wandert aus dem Blick.
     Es sieht aus, als springe die Seite.
     Ajdin am 27.09.2026: "wenn man eine sektion oeffnet dann springt das so
     komisch am besten wenn man auf die sektion klickt das der bildschirm auch
     da bleibt".
     Deshalb: Stelle vorher merken, nach dem Umschalten um genau den
     Unterschied nachscrollen. Der Kopf steht danach wieder da, wo der Finger
     ihn getroffen hat. */
  const kasten = [].slice.call(box.children).find(el => el.dataset.sid === id);
  /* In Bildschirmpunkten, wie scrollBy und innerHeight - siehe rectFaktor() */
  const oben = () => kasten.getBoundingClientRect().top * rectFaktor();
  const vorher = kasten ? oben() : null;

  offeneSektion = (offeneSektion === id) ? '' : id;
  [].slice.call(box.children).forEach(el => {
    const auf = el.dataset.sid === offeneSektion;
    el.classList.toggle('zu', !auf);
    const kopf = el.querySelector('.skopf');
    if(kopf) kopf.setAttribute('aria-expanded', auf ? 'true' : 'false');
  });

  if(kasten && vorher !== null){
    /* getBoundingClientRect erzwingt hier einen neuen Umbruch - genau das ist
       gewollt, sonst stuende noch die alte Stelle da.
       Ohne behavior:'instant' wuerde ein spaeter eingefuehrtes
       scroll-behavior:smooth daraus eine sichtbare Fahrt machen; das Ziel ist
       aber, dass sich gar nichts bewegt. */
    const versatz = oben() - vorher;
    if(Math.abs(versatz) > 1) scrollBy({top: versatz, behavior: 'instant'});
    /* Klappt oberhalb eine lange Sektion zu, wird die Seite kuerzer als die
       Stelle, an der man gerade stand. Der Browser kann dann nicht so weit
       scrollen und klemmt den Wert ab - der Kopf sitzt hinterher trotzdem
       woanders. In dem Fall ist "bleiben" gar nicht moeglich, weil nicht
       genug Seite da ist.
       Dann wird der Kopf bewusst an die Bezugslinie gesetzt, an der auch die
       Farbe haengt. Das ist eine Bewegung, aber eine erklaerbare: die
       angetippte Sektion steht oben und traegt ihre Farbe. */
    const rest = oben() - vorher;
    if(Math.abs(rest) > 2){
      const linie = innerHeight > 0 ? Math.min(220, innerHeight * 0.32) : 160;
      scrollBy({top: oben() - linie, behavior: 'instant'});
    }
  }
  /* Der Umweg ueber sektionsFarbe ist Absicht: ist keine Sektion offen,
     faellt die Farbe auf die zurueck, in der gerade gelernt wird. Ohne
     Farbe dazustehen waere schlechter als eine. */
  sektionsFarbe();
}

/* Kurz ueberblenden statt umzuspringen. Die Klasse farbwechsel schaltet die
   Uebergaenge im Stil ein und darf nicht stehen bleiben: sonst zoege auch das
   Gruen fuer eine richtige Antwort traege hinterher.
   Zwei Stellen brauchen das - der Sektionswechsel und der Wechsel zwischen
   hell und dunkel. Deshalb steht es hier einmal. */
function weichUmblenden(){
  const wurzel = document.documentElement;
  wurzel.classList.add('farbwechsel');
  clearTimeout(farbUhr);
  farbUhr = setTimeout(() => wurzel.classList.remove('farbwechsel'), 750);
}

/* Die Farbe umschalten und dabei weich hinueberblenden. */
function farbeSetzen(nr){
  const wurzel = document.documentElement;
  if(wurzel.dataset.sek === nr) return;        // schon die richtige Farbe
  /* Beim ersten Aufbau nicht ueberblenden: da gibt es keine alte Farbe,
     und ein Aufblitzen zum Start will niemand. */
  const ersteMal = !wurzel.dataset.sek;
  wurzel.dataset.sek = nr;
  if(ersteMal) return;
  weichUmblenden();
}

function sektionsFarbe(){
  /* Zum Ansehen am Telefon: index.html?sek=2 zeigt die App in der Farbe
     von Sektion 2, ohne dass man erst fuenfzehn Level spielen muss. Ohne
     den Zusatz rechnet die App wie immer selbst. */
  const gewuenscht = new URLSearchParams(location.search).get('sek');
  if(gewuenscht && /^[1-9]$/.test(gewuenscht)) return farbeSetzen(gewuenscht);
  if(!CATEGORIES.length || !SECTIONS.length) return;
  /* Die aufgeklappte Sektion gibt die Farbe vor, nicht die, in der gerade
     gelernt wird. Wer sich Sektion 3 ansieht, soll sie auch sehen. */
  /* Ist keine aufgeklappt: die Sektion von Weitermachen - seit den
     Stufen-Reitern (13.11.2026) nur, wenn ihr Reiter gezeigt wird. Sonst
     die erste des gezeigten Reiters, damit die Farbe zu dem passt, was man
     sieht. */
  const next = firstOpen(), st = angezeigteStufe();
  const id = offeneSektion || (stufeVon(next) === st ? (CATEGORIES[next] || {}).sektion
                                                     : (reiterSektionen(st)[0] || {}).id);
  farbeSetzen(sektionsNummer(id));
}
const shuffle = a => { for(let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; } return a; };
const strip = s => s.toLowerCase().replace(/đ/g,'d').normalize('NFD').replace(/[̀-ͯ]/g,'');
/* Komma und Bindestrich im Inneren zaehlen wie ein fehlendes Haekchen: "Racun molim"
   fuer "Račun, molim", "sogan dolma" fuer "sogan-dolma". Vorher kosteten sie bei zwei
   gleichen Versuchen ein Leben (Pruefbericht 1.3, 06.11.2026). Nur matches(),
   fastGleich() und fastRichtig() benutzen clean().
   Erst trim(), dann das Satzzeichen am Ende (12.11.2026): fastRichtig() bekommt
   die Eingabe ungekuerzt, und bei "pada kisq! " - ein Leerzeichen hinter dem
   Ausrufezeichen, wie es manche Tastatur anhaengt - blieb das "!" stehen und
   war ein zweiter Fehler. Der Hinweis kam dann nicht. */
const clean = s => strip(s).trim().replace(/[.!?…]+$/,'').replace(/[,-]/g,' ').replace(/\s+/g,' ').trim();

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
