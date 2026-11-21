/* ---- Lernzeit ----
   Gezählt wird NUR, während wirklich an einer Lektion, einem Test oder einer
   Geschichte gearbeitet wird – und nur zwischen zwei beantworteten Aufgaben.
   Jede einzelne Pause ist auf PAUSE_MAX gedeckelt: Wer über einer Aufgabe
   lange nachdenkt, bekommt 90 Sekunden gutgeschrieben, wer die Lektion offen
   liegen lässt, bekommt nichts mehr. Auf zehn Minuten kommt man damit nur
   durch tatsächlich beantwortete Aufgaben, nicht durch Dasitzen.
   Gespeichert wird in Sekunden, angezeigt in Minuten. */
const PAUSE_MAX = 90;      // Sekunden je Pause, die noch als Lernen zählen
let uhrStart = 0;          // 0 = Uhr läuft nicht
let seitAntwort = 0;       // Sekunden seit der letzten beantworteten Aufgabe
function uhrAn(){ if(!uhrStart) uhrStart = Date.now(); }
function uhrNeu(){ seitAntwort = 0; uhrAn(); }   // frische Lektion, Test oder Geschichte
/* Schreibt die bisher gelaufene Zeit gut. Wird alle zehn Sekunden aufgerufen,
   damit die Zeit auch dann in der Datei landet, wenn der Browser mitten in
   der Lektion zugeht – und beim Verlassen ein letztes Mal.
   `antwort` = true kommt aus den Antwort-Rückrufen: erst dann beginnt die
   nächste Pause. Der Deckel oben im Kommentar war lange nur versprochen –
   ohne ihn füllte eine offen liegende Aufgabe die Tagesaufgabe „Minuten“
   und damit die Münzen, ohne dass jemand übt. */
function uhrTakt(antwort){
  if(!uhrStart) return;
  const weg = Date.now() - uhrStart;
  if(weg < 1000) return;      // angefangene Sekunde liegen lassen
  const sek = Math.floor(weg/1000);
  uhrStart += sek*1000;       // nur das Gutgeschriebene abziehen, Rest bleibt stehen
  const gut = Math.max(0, Math.min(sek, PAUSE_MAX - seitAntwort));
  seitAntwort += sek;
  if(gut) zaehle('zeit', gut);
  if(antwort === true) seitAntwort = 0;
}
function uhrAus(){ uhrTakt(); uhrStart = 0; }
setInterval(uhrTakt, 10000);
// Bildschirm aus, Tab gewechselt, Handy gesperrt: das zählt nicht mit –
// und der Ton hat dort erst recht nichts verloren. Sonst spricht die App
// aus der Tasche weiter, obwohl sie längst im Hintergrund liegt.
// Wieder sichtbar: nur anlaufen lassen, was vorher wirklich lief. Die
// Ergebnisschirme haben die Uhr schon aus – dort darf sie nicht neu starten,
// sonst zählt jede AdMob-Anzeige und jedes Sperren Minuten dazu.
let uhrWarAn = false;
document.addEventListener('visibilitychange', ()=>{
  if(!skripteDa) return;   // Start noch nicht fertig, siehe skripteDa
  if(document.hidden){
    /* Eine vorgelesene Geschichte merkt sich die Stelle - wie beim Antippen
       eines Wortes. stilleBitte() dreht currentTime auf null, und nach dem
       Entsperren begann sie wieder ganz von vorn. laeuftVor steht nur beim
       Vorlesen, auch in der Pause. Gefunden bei der Pruefung am 06.10.2026. */
    if(laeuftVor && spieler.src && spieler.currentTime > 0)
      geschichteStelle = {datei: spieler.src, sekunde: spieler.currentTime};
    uhrWarAn = uhrStart > 0; uhrAus(); stilleBitte(true);   // Aufgabe bleibt gueltig
    /* Den Werbewecker abraeumen. Die Anzeige ist damit nicht verloren:
       werbungSchuldig traegt sie in die naechste Lektion. */
    if(werbungWecker){ clearTimeout(werbungWecker); werbungWecker = 0; schuldigSetzen(true); }
    /* Und speichern. Eine RICHTIGE Antwort speicherte bisher gar nicht:
       known.add() und zaehle() laufen, saveProgress() nicht. Gespeichert
       wurde nur bei einer falschen Antwort (ueber loseLife) und am
       Lektionsende. Der Fehler traf also ausgerechnet den fehlerfreien
       Lauf - Anruf mitten in der Lektion, und die gelernten Woerter waren
       weg. Ajdin am 18.09.2026. */
    saveProgress();
    /* Jetzt ist der Stand des Tages fertig - wer geuebt hat, bekommt
       heute keine Erinnerung mehr. Siehe BENACHRICHTIGUNGEN. */
    benPlanen();
  }
  else {
    /* Zuerst der Tageswechsel: ueber Nacht im Hintergrund ist der
       haeufigste Fall, und er faellt sonst erst auf, wenn die Serie
       schon gerissen ist. */
    tagPruefen();
    if(uhrWarAn){ uhrWarAn = false; uhrAn(); }
    topfNachziehen();
    /* Gefunden bei der Pruefung am 06.10.2026: wer nach der Wartezeit
       zurueckkam, sah das Herz noch bei 0 und den Lektionsknopf gesperrt,
       bis zu 30 Sekunden lang - nachgezogen hat nur der Takt unten. Die
       zwei Wege nicht, solange eine Anzeige laeuft: lebenWege() baut ihre
       Knoepfe neu, und werbungFuerLeben() raeumt danach nur auf, wenn sein
       Knopf noch im Dokument haengt. */
    renderLives();
    if(!anzeigeLaeuft) lebenWege();
    ohneLebenVorbei();
  }
});

/* Frisch geschaffte Aufgaben – wird beim Zeichnen des Ergebnisschirms geleert.
   Deshalb braucht es keinen "schon gefeiert"-Merker in der Datei: nach einem
   Neuladen ist die Liste leer, also feiert nichts ein zweites Mal. */
let questFrisch = [];

/* Zählt hoch. Münzen gibt es genau in dem Augenblick, in dem der Zähler das
   Ziel überschreitet – nie beim Zeichnen, sonst gäbe es sie doppelt. */
function zaehle(id, wieviel){
  if(imZa()) return;      // Beim Zahnarzt: zaehlt nicht fuer Tagesaufgaben und Muenzen (06.11.2026)
  const t=today();
  if(!tagwerk[t]) tagwerk[t] = {};
  const vorher = tagwerk[t][id] || 0;
  tagwerk[t][id] = vorher + (wieviel || 1);
  const q = questsHeute().find(x => x.id === id);
  if(q && vorher < q.ziel && tagwerk[t][id] >= q.ziel){
    muenzenGes += MUENZEN_PRO_QUEST;
    questFrisch.push(q);
  }
}

/* ---- Leben ---- */
/* Das Geschenk zaehlt hier mit: solange es laeuft, gibt es weder Werbung
   noch eine Grenze bei den Leben - genau wie gekauft. */
const unlimited = () => premium || ALLE_FREI || geschenkLaeuft();
const REFILL_MS = LEBEN_NACHFUELLEN_MIN*60*1000;
function syncLives(){
  if(unlimited() || lives.anzahl >= LEBEN_MAX) return;
  /* Eine Zeit aus der Zukunft kommt wirklich vor: wer die Uhr des Handys
     vorstellt und wieder zurueckstellt, hat sie im Lernstand stehen. Dann
     ist die Differenz unten fuer immer negativ, gained wird nie groesser
     als null - und es waechst nie wieder ein Herz nach. Die App sagt dann
     Dinge wie "naechstes Herz in 11 Tagen", und dagegen laesst sich von
     aussen nichts machen. Selten, aber ein Totalausfall ohne Selbsthilfe. */
  if(lives.zeit > Date.now()) lives.zeit = Date.now();
  const gained = Math.floor((Date.now() - lives.zeit) / REFILL_MS);
  if(gained > 0){
    const n = Math.min(LEBEN_MAX, lives.anzahl + gained);
    lives = n >= LEBEN_MAX ? {anzahl:LEBEN_MAX, zeit:0} : {anzahl:n, zeit:lives.zeit + gained*REFILL_MS};
    saveProgress();
  }
}
function livesNow(){ syncLives(); return unlimited() ? LEBEN_MAX : lives.anzahl; }
function loseLife(){
  if(unlimited()) return;
  syncLives();
  if(lives.anzahl >= LEBEN_MAX) lives.zeit = Date.now();
  lives.anzahl = Math.max(0, lives.anzahl - 1);
  saveProgress(); renderLives();
  if(lives.anzahl === 0) benPlanen();
}
function nextLifeIn(){ if(unlimited() || lives.anzahl >= LEBEN_MAX) return 0; return Math.max(0, lives.zeit + REFILL_MS - Date.now()); }
const fmtMin = ms => { const m=Math.ceil(ms/60000); return m>=60 ? t('zeit.stunden',{h:Math.floor(m/60), m:m%60}) : t('zeit.minuten',{m:m}); };
const fmtTage = ms => { const tg=Math.floor(ms/86400000); return tg>=1 ? tp('zeit.tage', tg) : fmtMin(ms); };
/* Ein Herz mit einer Zahl, mehr nicht. Fünf einzelne Herzen plus ein Satz
   daneben brauchten eine ganze Leiste; jetzt passt es in eine Ecke.
   Die Wartezeit kommt erst, wenn man aufs Herz tippt – außer bei null, da
   ist sie das Einzige, was gerade zählt.
   livesInfoAn steht außerhalb, weil renderLives() alle 30 Sekunden neu
   zeichnet und die aufgeklappte Zeile das überleben muss. */
let livesInfoAn = false;
function lebenText(n){
  if(unlimited()) return t(ALLE_FREI ? 'leben.testmodus' : 'leben.unbegrenzt');
  if(n >= LEBEN_MAX) return t('leben.voll');
  if(n === 0) return t('leben.keine', {zeit: fmtMin(nextLifeIn())});
  return t('leben.stand', {n:n, max:LEBEN_MAX, zeit:fmtMin(nextLifeIn())});
}
function renderLives(){
  /* Die Muenzen haengen an derselben Leiste wie die Herzen und werden hier
     mitgezeichnet - so stimmen sie nach jedem Kauf und jeder Tagesaufgabe,
     ohne dass jede Stelle daran denken muss. */
  const mb=$('muenzBar');
  if(mb){ mb.hidden = !profil; if(profil) mb.innerHTML = symbol('muenze')+' <b>'+muenzen()+'</b> <span class="km">KM</span>'; }
  const bar=$('livesBar'); if(!profil){ bar.style.display='none'; return; } bar.style.display='inline-flex';
  const n = livesNow();
  /* Das Herz im Fragenkasten. Sichtbar in der Lektion (#lHerz) und im
     Level-Test (#tHerz), der seit dem 19.10.2026 Leben kostet wie die
     Lektion. Die Einstufung kostet keine und hat deshalb keins. Ihre
     unsichtbare Pille (.kastenherz.platzhalter) wird trotzdem mitgefuellt -
     sie haelt die Hoehe der Kopfzeile frei (19.10.2026). */
  document.querySelectorAll('.kastenherz').forEach(k => {
    k.innerHTML = herzSymbol(t('stat.leben')) + ' <b>' + (unlimited() ? '∞' : n) + '</b>';
    k.classList.toggle('zero', n === 0 && !unlimited());
  });
  const zeigen = livesInfoAn || n === 0;
  document.body.classList.toggle('lebenLeer', n === 0);   // Pruefbericht 1.4, S17: siehe body.lebenLeer im Stil
  bar.className='livesbar'+(unlimited()?' premium':'')+(n===0?' zero':'');
  bar.innerHTML = '<button type="button" class="herz" id="livesKnopf" aria-expanded="'+zeigen+'">'
                + herzSymbol(t('stat.leben'))+' <b>'+(unlimited()?'∞':n)+'</b></button>'
                + (zeigen ? '<span class="info">'+esc(lebenText(n))+'</span>' : '');
  $('livesKnopf').addEventListener('click', ()=>{ livesInfoAn = !livesInfoAn; renderLives(); });
  const b=$('btnLesson'); if(b){ b.disabled = n===0; b.innerHTML = n===0 ? mitSymbol('herz', esc(t('leben.warten'))) : mitSymbol('play', esc(t('level.lektion'))); }
  testKnopf(n);
  kopfEng();
}
/* Der Level-Test kostet seit dem 19.10.2026 Leben wie die Lektion (Ajdin:
   "genau wie in der Lektion") - ohne Leben ist sein Knopf deshalb ebenso
   gesperrt. Er behaelt seine Beschriftung: "Keine Leben · warten" steht
   schon auf dem Lektionsknopf daneben, zweimal derselbe Satz waere zu viel.
   Hier und in updateProgress(), damit der Knopf auch wieder aufgeht, wenn
   ein Leben nachwaechst, waehrend die Level-Uebersicht offen steht. */
function testKnopf(n){
  const bt = $('btnTest'), c = cur();
  if(bt && c) bt.disabled = !testAllowed(c) || n === 0;
}
/* Grosse Systemschrift (Android): passen Herzen, Muenzen und Knoepfe
   nicht mehr nebeneinander, bekommen die Muenzen eine eigene Zeile
   (header.eng). Gemessen wird, wie breit der Kopf in EINER Zeile waere -
   bei normaler Schrift passt das immer, dann bleibt alles wie bisher.
   Ein versteckter Kopf (Lektion) misst nichts; beim Verlassen ruft
   nurHerz(false) noch einmal hierher. Gefunden bei der Pruefung am
   06.10.2026: bei 200 % lag das Herz halb ueber den Muenzen.
   Steht die Zuruecktaste mit in der Leiste (iPhone, Browser), kommt davor
   ein Zwischenschritt (16.11.2026, Offen-Liste 9): passt es mit dem Wort
   nicht, zeigt sie nur den Pfeil (header.knapp, siehe dort im Stil). Erst
   wenn auch das nicht reicht, gilt header.eng - dann wie bisher mit dem
   ganzen Wort. Android zeigt die Taste nie, dort aendert sich nichts. */
function kopfEng(){
  const h = document.querySelector('header');
  if(!h || !h.offsetParent) return;
  h.classList.remove('eng', 'knapp');
  const passt = () => {
    h.style.gridTemplateColumns = 'auto auto auto'; h.style.width = 'max-content';
    const noetig = h.offsetWidth;
    h.style.gridTemplateColumns = ''; h.style.width = '';
    return noetig <= h.offsetWidth;
  };
  if(passt()) return;
  const zurueck = $('btnBack');
  if(zurueck && zurueck.style.display !== 'none'){
    h.classList.add('knapp');
    if(passt()) return;
    h.classList.remove('knapp');
  }
  h.classList.add('eng');
}
window.addEventListener('resize', kopfEng);
if(document.fonts) document.fonts.ready.then(kopfEng);
/* Muenzanzeige, Einkaufswagen und Zahnrad stehen auch waehrend einer
   Lektion oben, weil Lektion und Test Unteransichten von levelView sind und
   nicht ueber showView() laufen. Wer einen davon antippt, verliert sonst die
   angefangene Lektion ohne Warnung - die verbrauchten Leben bleiben
   verbraucht, und zurueck fuehrt nur auf die Startseite. Der Knopf "Lektion
   abbrechen" daneben fragt laengst nach, die Zurueck-Taste des Handys ruft
   genau diesen Knopf. Gefunden am 26.09.2026.
   Gefragt wird nur, wenn wirklich eine Lektion oder ein Test laeuft. */
async function lektionDarfWeg(){
  /* Tx heisst seine Liste "qs", nicht "queue" (siehe buildTest). Mit
     Tx.queue.length warf diese Zeile waehrend eines Tests einen Fehler, und
     der Tipp auf Muenzen, Laden oder Zahnrad tat daraufhin gar nichts.
     Gefunden am 26.09.2026. */
  if(sichtbar('einstufungView') && Sx && !Sx.fertig) return await sprungDarfWeg();   // 13.11.2026
  if(sichtbar('einstufungView') && Ex && !Ex.fertig){
    const ziel = einstufungZiel();
    if(!await frage(t('einst.abbrechen_frage'), t('einst.abbrechen_text', {stufe: stufeVon(ziel), n: levelNummer(ziel)}),
                    t('btn.abbrechen'), t('btn.weitermachen'))) return false;
    einstufungEnde();
    return true;
  }
  /* Nur in der Levelansicht: #lesson und #test liegen darin und behalten
     ihren eigenen Schalter, auch wenn die ganze Ansicht weg ist. */
  const laeuft = sichtbar('levelView') &&
                 ((sichtbar('lesson') && Lx && Lx.i < Lx.queue.length) ||
                  (sichtbar('test')   && Tx && Tx.i < Tx.qs.length));
  if(!laeuft) return true;
  return await frage(t('lektion.abbrechen_frage'), t('lektion.abbrechen_hinweis'),
                     t('btn.abbrechen'), t('btn.weitermachen'));
}
/* Bis zum 23.10.2026 fuehrte ein Tipp auf die Muenzen in den Laden. Jetzt
   nur noch der Einkaufswagen (#btnShop), siehe #muenzBar. */
/* Wer die App abends auf der Startseite liegen laesst und sie morgens
   wieder hervorholt, sah bisher den Stand von gestern: "Heute geuebt",
   die alte Serienzahl und alle drei Tagesaufgaben abgehakt. renderHero()
   und renderQuests() laufen naemlich nur aus showHome(), und der einzige
   Zeitgeber zeichnete bloss renderLives().
   Das ist nicht nur schief angezeigt: wer glaubt, er haette heute schon
   geuebt, lernt nicht - und verliert die Serie, weil days den neuen Tag
   nie bekommt. Gefunden am 26.09.2026. */
let letzterTag = today();
function tagPruefen(){
  const jetzt = today();
  if(jetzt === letzterTag) return false;
  letzterTag = jetzt;
  /* Der Serienschutz lief bisher nur beim Kaltstart (nachAnmeldung) und beim
     Einlesen einer Sicherung. Bleibt die App ueber einen ausgelassenen Tag
     hinweg im Speicher - Home-Taste, Handy in die Tasche, kein Neuladen -,
     kam der ausgelassene Tag nie in frost: die Serie fiel still von 40 auf 1,
     obwohl Schutztage im Vorrat lagen, und es kam weder "gerettet" noch
     "verloren". Am PC faellt das nicht auf, weil start.py jedes Mal eine
     frische Seite liefert. pruefeSchutz() zaehlt von GESTERN zurueck, muss
     also nicht punktgenau um Mitternacht laufen; der Aufruf hier deckt beide
     Wege ab - den Zeitgeber alle 30 Sekunden und das Hervorholen der App.
     Zweimal laufen schadet nicht: beim zweiten Mal stehen die Luecken schon
     in frost, luecken ist leer und die Funktion kehrt sofort zurueck.
     Gefunden am 26.09.2026. */
  pruefeSchutz();
  geschenkPruefen();
  geschenkNachreichen();
  /* Nur zeichnen, wenn die Startseite ueberhaupt sichtbar ist. Mitten in
     einer Lektion wuerde showHome() die Aufgabe wegreissen. Der Merker
     steht trotzdem schon auf heute, damit es spaeter nicht grundlos
     nachzieht - showLevelHome() zeichnet die Startseite ohnehin neu. */
  if(sichtbar('pfad')) showHome();
  return true;
}
setInterval(()=>{ tagPruefen(); renderLives(); topfNachziehen(); ohneLebenVorbei(); }, 30000);

/* ---- Lernserie ----
   days  = Tage mit einer fertigen Lektion
   frost = Tage, die ein Serienschutz gerettet hat. Sie unterbrechen die Serie
           nicht, zählen aber selbst nicht als Lerntag (wie bei Duolingo). */
const dayKey = x => x.getFullYear()+'-'+String(x.getMonth()+1).padStart(2,'0')+'-'+String(x.getDate()).padStart(2,'0');
function streak(){
  const alle = new Set([...days, ...frost]);
  const d=new Date(); let n=0;
  if(!alle.has(dayKey(d))) d.setDate(d.getDate()-1);
  while(alle.has(dayKey(d))){ if(days.has(dayKey(d))) n++; d.setDate(d.getDate()-1); }
  return n;
}

/* ---- Serienschutz ----
   Wächst von selbst nach: alle SCHUTZ_TAGE Tage einer, höchstens SCHUTZ_MAX.
   Lässt man einen Tag aus, deckt ein Schutz diesen Tag ab und die Serie bleibt. */
const SCHUTZ_MS = SCHUTZ_TAGE*24*60*60*1000;
function syncSchutz(){
  if(schutz.zeit > Date.now()) schutz.zeit = Date.now();   // siehe syncLives
  /* Voll laeuft keine Uhr. zeit bleibt trotzdem stehen, nach einem Kauf entscheidet sie
     den Abgleich, siehe kaufe(). Bis zum 06.11.2026 ging sie hier auf 0. */
  if(schutz.anzahl >= SCHUTZ_MAX) return false;
  if(!schutz.zeit){ schutz.zeit = Date.now(); return true; }
  const dazu = Math.floor((Date.now() - schutz.zeit) / SCHUTZ_MS);
  if(dazu <= 0) return false;
  const n = Math.min(SCHUTZ_MAX, schutz.anzahl + dazu);
  schutz = n >= SCHUTZ_MAX ? {anzahl:SCHUTZ_MAX, zeit:0} : {anzahl:n, zeit:schutz.zeit + dazu*SCHUTZ_MS};
  return true;
}
function schutzNow(){ if(syncSchutz()) saveProgress(); return schutz.anzahl; }
function naechsterSchutzIn(){ return (schutz.anzahl>=SCHUTZ_MAX || !schutz.zeit) ? 0 : Math.max(0, schutz.zeit + SCHUTZ_MS - Date.now()); }

let schutzMeldung = 0;   // >0: so viele Tage gerettet, -1: Serie ist gerissen
function pruefeSchutz(){
  schutzMeldung = 0;
  if(!days.size) return;
  const alle = new Set([...days, ...frost]);
  const luecken = [];
  const d = new Date(); d.setDate(d.getDate()-1);
  while(luecken.length <= SCHUTZ_MAX && !alle.has(dayKey(d))){ luecken.push(dayKey(d)); d.setDate(d.getDate()-1); }
  if(!luecken.length) return;                  // gestern gelernt, alles gut
  if(!alle.has(dayKey(d))){ schutzMeldung = -1; return; }   // Serie schon lange weg
  const vorrat = schutzNow();
  if(vorrat < luecken.length){ schutzMeldung = -1; return; }
  luecken.forEach(k=>frost.add(k));
  schutz.anzahl -= luecken.length;
  /* War der Vorrat voll, steht in zeit hoechstens der Kauf (siehe kaufe()). Die Uhr
     beginnt erst jetzt. */
  if(!schutz.zeit || vorrat >= SCHUTZ_MAX) schutz.zeit = Date.now();
  schutzMeldung = luecken.length;
  saveProgress();
}
function renderSerie(){
  const el=$('streakLine'); if(!el) return;
  if(schutzMeldung < 0 && days.has(today())) schutzMeldung = 0;   // heute gelernt: neue Serie laeuft
  const n=streak(), s=schutzNow(), rest=naechsterSchutzIn();
  /* Die Serie selbst steht seit dem 26.09.2026 gross darueber, mit ihrer
     eigenen Flamme. Stuende sie hier noch einmal, saehe man "🔥 0" und
     direkt darunter "🔥 Noch keine Lernserie" - dieselbe Flamme und
     dieselbe Zahl zweimal. Diese Zeile traegt deshalb nur noch den
     Schutz und die Meldungen dazu.
     n wird weiter gebraucht: schutzMeldung haengt daran. */
  /* Seit dem 24.10.2026 Entwurf B, "zwei Plaetze" (Stil bei
     .schutzplaetze): je Platz ein Schild, dazu kurz "1 Schutz" und
     "noch 9 Tage" bzw. "voll". Die lange Fassung "noch 9 Tage bis zum
     naechsten" (serie.schutz_naechster) bleibt den Einstellungen.
     Zwischen den zwei Zeilen ein Komma nur fuer den Bildschirmleser,
     sonst liest er "1 Schutz noch 9 Tage" in einem Zug. */
  const unten = s >= SCHUTZ_MAX ? '<small class="voll">'+t('serie.schutz_voll')+'</small>'
    : (rest ? '<small>'+t('serie.schutz_noch', {zeit: fmtTage(rest)})+'</small>' : '');
  const html =
    '<span class="schutzplaetze" aria-hidden="true">' + schutzPlaetze(s, rest) + '</span>' +
    '<span class="schutztext"><b>'+tp('serie.schutz', s)+'</b>' + (unten ? '<span class="nurleser">, </span>' + unten : '') + '</span>';
  /* renderSerie() laeuft bei jedem Reiterwechsel (ueber renderHero). Neu
     aufgebaut wird nur, was sich geaendert hat - sonst entstuenden die
     Bilder jedes Mal neu. */
  if(el._html !== html){ el.innerHTML = html; el._html = html; }
  const m = $('schutzMeldung');
  if(m){
    const blase = schutzMeldung > 0
      ? '<span class="bild" aria-hidden="true"><img src="'+SCHUTZ_BILD+'" alt=""></span><span>'+tp('serie.gerettet', schutzMeldung)+'</span>'
      : (schutzMeldung < 0 ? '<span class="kohle" aria-hidden="true"></span><span>'+t('serie.verloren')+'</span>' : '');
    if(m._html !== blase){
      m.innerHTML = blase; m._html = blase;
      m.className = 'schutzblase' + (schutzMeldung > 0 ? ' gerettet' : (schutzMeldung < 0 ? ' verloren' : ''));
    }
    m.hidden = !blase;
  }
}
/* Die Plaetze des Serienschutzes, Entwurf B (24.10.2026): so viele, wie
   hoechstens gehen. Vorhanden ist ein Schild in Farbe ('voll'). Der erste
   freie Platz friert zu ('friert'): ueber dem blassen Bild liegt das
   farbige, von unten her so weit sichtbar, wie Tage um sind. Gezaehlt
   wird wie im Text daneben (fmtTage rundet ab): bei "noch 9 Tage" ein
   Zehntel, bei "noch 1 Tag" neun Zehntel - so stand es im Entwurf. In
   den letzten Stunden bleibt es bei neun Zehnteln: ein ganzes Schild
   gibt es erst, wenn es wirklich da ist. Weitere freie Plaetze bleiben
   blass ('leer'). So stand es im Entwurf B, Ajdin am 23.10.2026: "Nimm B
   sieht am besten aus". */
const SCHUTZ_BILD = 'symbole/serienschutz.webp';
function schutzPlaetze(s, rest){
  const bild = k => '<img class="'+k+'" src="'+SCHUTZ_BILD+'" alt="">';
  const um = Math.min(SCHUTZ_TAGE - 1, Math.max(0, SCHUTZ_TAGE - Math.floor(rest / 86400000)));
  /* Das Bild reicht in seinem Quadrat von 2,3 bis 97,7 Prozent der Hoehe.
     Das Schild laeuft unten spitz zu; mit hoch 0,6 waechst die Eisflaeche
     ungefaehr so gleichmaessig wie die Tage, nicht nur die Hoehe. */
  const oben = (97.7 - Math.pow(um / SCHUTZ_TAGE, .6) * 95.4).toFixed(1);
  let html = '';
  for(let i = 0; i < SCHUTZ_MAX; i++){
    if(i < s) html += '<span class="schutzplatz voll">' + bild('ganz') + '</span>';
    else if(i === s) html += '<span class="schutzplatz friert" data-tage="'+um+'" style="--zu:'+oben+'%">' + bild('blass') + bild('eis') + '</span>';
    else html += '<span class="schutzplatz leer">' + bild('blass') + '</span>';
  }
  return html;
}
/* Bis zum 01.10.2026 baute renderHero() den Drachen bei JEDEM Aufruf neu
   auf. renderHero() laeuft aber bei jedem Reiterwechsel und bei jeder
   Rueckkehr aus Einstellungen, Laden oder Lektion - und wer heute schon
   gelernt hatte, bekam dabei jedes Mal den Jubelsprung zu sehen (Ajdin:
   "warum springt der Drache, wenn ich vom Lernpfad zur Geschichte
   wechsle"). Jetzt wird er nur neu aufgebaut, wenn sich die Stimmung
   aendert: Er jubelt also einmal nach der ersten Lektion des Tages.
   Traegt er nicht mehr den Zierrat des angemeldeten Kontos, etwa nach
   einem Kontowechsel, wird nur die Figur neu geladen, ohne Sprung.
   Der Tag gehoert mit in den Vergleich: Bleibt die App ueber Mitternacht
   in einem Level offen, galt sonst der Jubel von gestern schon als der von
   heute, und nach der ersten Lektion des neuen Tages kam keiner. */
/* Die Flamme neben der Serie (20.10.2026, siehe .flamme im Stil): aus bei
   Serie 0, Glut, solange heute noch nichts gelernt ist, sonst an.
   flammeVorher ist der Zustand beim letzten Zeichnen in dieser Sitzung.
   Aufgebaut wird nur beim Wechsel von kalt (aus oder Glut) auf an. Beim
   ersten Zeichnen nach dem Start ist flammeVorher noch null - wer heute
   schon gelernt hat und die App oeffnet, sieht sie einfach brennen.
   Ob Bewegung erlaubt ist, fragt dieselbe Funktion wie bei den Kacheln:
   Schalter "Animationen" und Geraeteeinstellung, bei jedem Aufruf neu.

   Seit dem 22.10.2026 dieselbe Flamme ueberall (Ajdin: "beachte das nicht
   das es 2 verschiedene desgins sind"): Zustand und Stufe kommen fuer
   jeden Ort aus flammeKlassen(), seit dem 24.10.2026 das Bild aus
   flammeBild(); die Statistik am Ende einer Lektion und einer
   Wiederholungsrunde baut ihre mit flammeHtml(). Nur hier oben baut sie
   sich auf. Neue Orte, an denen die laufende Serie mit Flamme steht,
   nehmen flammeHtml() - keine eigene Flamme. */
function flammeZustand(){ return days.has(today()) ? 'an' : (streak() > 0 ? 'glut' : 'aus'); }
/* Stufen nach der laufenden Serie, Ajdin: "Mit Stufen" (20.10.2026).
   Schwellen nicht ohne ihn aendern. Farben im Stil bei .stufe-blau. */
function flammeStufe(n){ return n >= 365 ? 'gold' : (n >= 100 ? 'lila' : (n >= 30 ? 'blau' : '')); }
function flammeKlassen(){
  const z = flammeZustand(), st = flammeStufe(streak());
  return 'flamme' + (z === 'an' ? '' : ' ' + z) + (st ? ' stufe-' + st : '');
}
/* Das gemalte Bild je Zustand (24.10.2026, vorher das Emoji): an ->
   flamme.webp, glut -> glut.webp, aus -> aus.webp. Alle im selben Rahmen. */
function flammeBild(z){ return 'flamme/' + (z === 'an' ? 'flamme' : z) + '.webp'; }
/* Genau der Aufbau oben auf der Startseite (#serieFlamme im HTML), ohne id.
   Das Bild ist Schmuck: alt="" im Kasten mit aria-hidden, vorgelesen wird
   die Zahl daneben. Die Sterne (.funke) stehen immer drin; sichtbar sind
   sie nur in der Gold-Stufe, siehe .funke im Stil. Die Funken des
   Funkenflugs (.fk) kommen nur dazu, wenn sie fliegen sollen. */
function flammeHtml(){
  return '<span class="flammenbox" aria-hidden="true"><span class="' + flammeKlassen() + '" aria-hidden="true">' +
    '<img class="flammenbild" src="' + flammeBild(flammeZustand()) + '" alt=""></span>' +
    '<span class="funke f1">' + symbol('funken') + '</span><span class="funke f2">' + symbol('funken') +
    '</span><span class="funke f3">' + symbol('funken') + '</span>' +
    (funkenSoll() ? funkenHtml() : '') + '</span>';
}
/* Funkenflug (24.10.2026), siehe .fk im Stil. Ajdin: "kann man das feuer
   animieren so das immer so kurze funken raus kommen", und aus der
   Vorschau: "nimm A aber fuer 365 tage da ist schon eine shiny animation
   das waere dann zu viel". Funken also nur, wenn die Flamme brennt, nicht
   in der Gold-Stufe und nur mit Bewegung (Schalter "Animationen" und
   Geraeteeinstellung, wie bei den Kacheln). Waehrend des Aufbaus oben
   keine - das prueft funkenRichten() an .auf.
   Die Bereiche sind die der Vorschau (Variante A, ART.flug). Die erste
   Runde ist fest (FUNKEN_ERSTE, ueber den Rahmen verteilt und nacheinander
   gestartet): so baut flammeHtml() in der Statistik genau dasselbe wie
   funkenRichten() oben, und gewuerfelt wird nur bei animationiteration -
   kein Zeitgeber, kein Zufall beim Zeichnen. Dauer und Verzoegerung
   bleiben je Funke, wie sie hier stehen: 1,6 bis 2 s, aus dem Bereich der
   Vorschau (1,5 bis 2,1 s), die auch nur einmal je Funke wuerfelt.
   FUNKEN_BEREICH sind die Bereiche fuer jede neue Runde. */
const FUNKEN_BEREICH = {x: [.36, .64], y: [.08, .3], dx: [-.35, .35], dy: [-.75, -.5], wk: [-.08, .08], g: [.055, .08]};
const FUNKEN_ERSTE = [
  {dauer: 1.7, warte: 0,    x: .44, y: .14, dx: -.22, dy: -.66, wk: .05,  g: .06},
  {dauer: 1.9, warte: .45,  x: .57, y: .22, dx: .16,  dy: -.58, wk: -.04, g: .07},
  {dauer: 1.6, warte: .9,   x: .4,  y: .26, dx: -.3,  dy: -.52, wk: -.06, g: .065},
  {dauer: 2,   warte: 1.35, x: .6,  y: .1,  dx: .26,  dy: -.72, wk: .03,  g: .075}];
function funkenSoll(){ return flammeZustand() === 'an' && flammeStufe(streak()) !== 'gold' && !kachelnRuhig(); }
function funkenHtml(){
  return FUNKEN_ERSTE.map(w => '<span class="fk" style="' + Object.keys(w).map(k =>
    '--' + k + ':' + w[k] + (k === 'dauer' || k === 'warte' ? 's' : '')).join(';') + '"></span>').join('');
}
/* Oben: Funken anlegen oder wegnehmen. Liegen sie schon da und sollen
   bleiben, bleiben sie - sonst finge ihr Flug bei jedem renderHero() von
   vorn an. Die Farbe wechselt mit der Stufe von selbst (Stil). */
function funkenRichten(f){
  const box = f.parentElement, da = box.querySelectorAll('.fk');
  const soll = funkenSoll() && !f.classList.contains('auf');
  if(soll && !da.length) box.insertAdjacentHTML('beforeend', funkenHtml());
  else if(!soll) da.forEach(x => x.remove());
}
/* Eine neue Runde fuer einen Funken (24.10.2026): Startpunkt, Flugweite,
   Schlaengeln und Groesse neu gewuerfelt, wie in der Vorschau. Dauer und
   Verzoegerung bleiben, wie FUNKEN_ERSTE sie angelegt hat. Vier Funken mit
   eigener Dauer laufen ohnehin nie im Gleichschritt.
   Zuerst wurde auch die Dauer je Runde neu gewuerfelt. Damit eine neue
   Dauer nicht mitten in den Flug springt, rueckte dabei die Verzoegerung
   jede Runde nach - nach ein paar Minuten stand sie bei mehreren Sekunden.
   Kam man dann aus dem Laden, den Einstellungen oder einer Lektion zurueck,
   fing die Animation neu an (die Startseite war ausgeblendet), und ein
   Funke blieb so lange weg, wie seine Verzoegerung war. Gefunden bei der
   Pruefung, nachgestellt in tests_e2e/test_funken.py. */
function funkeWuerfeln(fk){
  const s = fk.style, B = FUNKEN_BEREICH;
  for(const k in B) s.setProperty('--' + k, (B[k][0] + Math.random() * (B[k][1] - B[k][0])).toFixed(3));
}
document.addEventListener('animationiteration', e => {
  if(e.animationName === 'flammeFlug') funkeWuerfeln(e.target);
});
/* Alle Bilder der Flamme einmal beim Start holen (24.10.2026): Flamme, Glut,
   kalte Kohle und die Ebenen des Aufbaus liegen dann schon bereit, wenn sie
   zum ersten Mal gebraucht werden - sonst stuende beim ersten Wechsel einen
   Augenblick lang ein leerer Rahmen da. Nur eigene Dateien, keine Anfrage
   nach draussen. Die Liste haelt die Bilder fest, damit der Browser sie
   nicht wieder aus dem Speicher wirft. */
const FLAMME_BILDER = ['flamme', 'glut', 'aus', 'kohle', 'ebene_flaemmchen', 'ebene_kohle_heiss',
                       'ebene_rot', 'ebene_orange', 'ebene_gelb', 'ebene_kern'];
const flammeVorrat = FLAMME_BILDER.map(n => {
  const i = new Image(); i.src = 'flamme/' + n + '.webp';
  if(i.decode) i.decode().catch(() => {});
  return i;
});
/* Der Aufbau Glut -> Flamme (24.10.2026), Fassung 2 der Vorschau - siehe
   "Der Aufbau" im Stil. Die Ebenen sind dieselben Dateien wie oben im
   Vorrat. Aus kalter Kohle (Serie 0) gibt es kein Flaemmchen, dafuer liegt
   die graue Kohle obenauf und blendet aus. */
const FLAMME_DAUER = 1500;
function flammeStapel(vonAus){
  const b = (k, n) => '<img class="gf-' + k + '" src="flamme/' + n + '.webp" alt="">';
  return '<span class="gf' + (vonAus ? ' von-aus' : '') + '" aria-hidden="true"><span class="gf-schein"></span>' +
    '<span class="gf-glut">' + (vonAus ? '' : b('flaemmchen', 'ebene_flaemmchen')) + b('kohle', 'kohle') +
      b('heiss', 'ebene_kohle_heiss') + (vonAus ? b('asche', 'aus') : '') + '</span>' +
    '<span class="gf-glutkern"></span>' +
    '<span class="gf-feuer">' + b('rot', 'ebene_rot') + b('orange', 'ebene_orange') + b('gelb', 'ebene_gelb') +
      b('kern', 'ebene_kern') + '</span></span>';
}
let flammeUhr = 0;
/* Stapel weg, das eine Bild wieder sichtbar. Es traegt schon flamme.webp,
   und der Stapel endet genau in diesem Bild - deshalb springt nichts. */
function flammeFertig(f){
  clearTimeout(flammeUhr);
  const s = f.querySelector('.gf'); if(s) s.remove();
  f.classList.remove('auf');
}
/* Sicherheitsnetz zu animationend: Laeuft der Aufbau nicht mehr, weil die
   Startseite mittendrin verschwand oder die Animationen ausgeschaltet
   wurden, kaeme kein animationend - und der Stapel stuende still in
   seinem ersten Bild, Glut statt Flamme. Laeuft er noch (oder ist er
   angehalten), wird spaeter wieder nachgesehen. */
function flammeWache(f){
  clearTimeout(flammeUhr);
  flammeUhr = setTimeout(() => {
    let laeuft = false;
    try{
      const x = f.querySelector('.gf-feuer');
      laeuft = !!x && x.getAnimations().some(a => a.playState === 'running' || a.playState === 'paused');
    }catch(e){}
    if(laeuft) flammeWache(f); else { flammeFertig(f); funkenRichten(f); }
  }, FLAMME_DAUER + 300);
}
let flammeVorher = null;
function flammeZeigen(){
  const f = $('serieFlamme'); if(!f) return;
  const zustand = flammeZustand();
  /* .auf und der Stapel bleiben stehen, solange der Aufbau laeuft -
     renderHero() kommt waehrend der 1,5 s auch mal ein zweites Mal vorbei.
     Ohne Bewegung oder wenn die Flamme nicht mehr brennt (Mitternacht) ist
     er sofort fertig. */
  const baut = zustand === 'an' && f.classList.contains('auf') && !kachelnRuhig();
  if(!baut) flammeFertig(f);
  f.className = flammeKlassen() + (baut ? ' auf' : '');
  const bild = f.querySelector('.flammenbild'), soll = flammeBild(zustand);
  if(bild.getAttribute('src') !== soll) bild.setAttribute('src', soll);
  if(zustand === 'an' && flammeVorher && flammeVorher !== 'an' && !baut && !kachelnRuhig()){
    f.insertAdjacentHTML('beforeend', flammeStapel(flammeVorher === 'aus'));
    f.classList.add('auf');
    flammeWache(f);
  }
  flammeVorher = zustand;
  funkenRichten(f);
}
/* gfLodern laeuft auf .gf-feuer und endet mit allen anderen Teilen. Erst
   danach setzen die Funken ein. */
$('serieFlamme').addEventListener('animationend', e => {
  if(e.animationName === 'gfLodern'){ flammeFertig(e.currentTarget); funkenRichten(e.currentTarget); }
});
let heroStand = null;
function renderHero(){
  festSchmuck();
  const stimmung = days.has(today()) ? 'cheer' : 'happy';
  const stand = stimmung + '|' + today();
  const box = $('zmajHome'), anim = box.querySelector('.zmaj-anim');
  if(stand !== heroStand || !box.firstChild){
    if(anim && anim._anim){ try{ anim._anim.destroy(); }catch(e){} anim._anim = null; }
    box.innerHTML = zmaj(stimmung); setMood(box, stimmung);
    heroStand = stand;
  } else if(anim && anim._anim && anim._stand !== zierratSchluessel()){
    try{ anim._anim.destroy(); }catch(e){}
    anim._anim = null; anim._stand = null; anim.innerHTML = '';
    mountZmaj(anim);
  }
  $('serieZahl').textContent = streak();
  flammeZeigen();
  /* Der Einstiegsknopf traegt den Namen dessen, was als naechstes dran ist.
     btn.weitermachen gibt es schon in allen acht Sprachen, es muss also
     kein neuer Text dazu.
     Er richtet sich nach dem Reiter: im Lernpfad auf das naechste Level,
     bei den Geschichten auf die naechste ungelesene. Bis zum 26.09.2026
     zeigte er auch bei den Geschichten auf ein Level und sprang beim
     Antippen aus dem Reiter heraus.
     Die Begruessung des Drachen (hero.heute, hero.serie, hero.start) faellt
     mit der Sprechblase weg. Die Texte bleiben in den Sprachdateien stehen,
     falls sie wiederkommen. */
  const k = $('weiterKnopf');
  if(k){
    let name = '', hin = null;
    if(homeMode === 'topf'){
      /* Im Reiter Wiederholen fuehrt der Knopf in die naechste Runde. Ist
         nichts im Topf, gibt es nichts weiterzumachen. */
      if(topfAnzahl() && livesNow() > 0){ name = t('topf.titel'); hin = startTopf; }
    } else if(homeMode === 'stories'){
      /* Die erste ungelesene. Sind alle gelesen, die letzte - dann ist der
         Knopf ein Weg zum Nachlesen statt eine tote Stelle. */
      const si = geschNaechste();
      const s = STORIES[si];
      if(s && storyUnlocked(si)){ name = s.titel; hin = () => openStory(si); }
    } else {
      const i = firstOpen(), c = CATEGORIES[i];
      if(c){ name = c.label; hin = () => openLevel(i); }
    }
    if(hin){
      k.innerHTML = mitSymbol('play', esc(t('btn.weitermachen') + ' · ' + name));
      k.onclick = hin;
      k.style.display = '';
    } else {
      k.style.display = 'none';   // nichts offen, nichts weiterzumachen
    }
  }
  renderSerie();
  profilPunkt();   // Erfolge: seit 14.11.2026 statt der Leiste nur der rote Punkt
  faelligZaehler();   // roter Zaehler am Reiter Wiederholen (O10, 20.11.2026)
  renderQuests();
}
/* Als Pfeil, nicht als Wert: showErfolge() steht weiter unten. Ist das Skript
   in Dateien geteilt, gibt es kein Heben ueber Dateigrenzen - die Zeile warf
   dann beim Laden (Release/Aufteilung/PLAN.md 2.4). 20.11.2026 */
$('erfolgLeiste').addEventListener('click', ()=>showErfolge());
/* Die drei Tagesaufgaben. Absichtlich ohne Warnung und ohne Rot, wenn eine
   nicht geschafft ist: ein ausgelassener Tag soll nichts kosten. */
function renderQuests(){
  const el=$('questBox'); if(!el) return;
  if(!profil || !CATEGORIES.length){ el.innerHTML=''; return; }
  const qs = questsHeute();
  const fertig = qs.filter(questFertig).length;
  el.innerHTML =
    // Die Muenzen stehen seit dem 18.09.2026 oben in der Kopfzeile. Hier
    // waeren sie dasselbe zweimal auf einem Bildschirm.
    // Der Zaehler rechts ist "1/3": zwei Zahlen und ein Schraegstrich
    // brauchen keine Uebersetzung.
    '<div class="qkopf"><span>'+t('quest.titel')+'</span>'+
      '<span class="muenzen">'+fertig+'/'+qs.length+'</span></div>' +
    '<div class="qringe">' +
    qs.map(q => {
      const n = Math.min(questStand(q.id), q.ziel), ok = n >= q.ziel;
      // Die Zeitaufgabe rechnet in Sekunden, angezeigt wird in Minuten
      const zZiel = q.min ? Math.round(q.ziel/60) : q.ziel;
      const zN    = q.min ? Math.floor(n/60) : n;
      /* Im Ring steht immer das Zahlenpaar, auch bei einer Aufgabe, die man
         nur einmal macht: "0/1". Dort stand bis zum 26.09.2026 ein Punkt,
         und ein Punkt sagt nichts - die beiden Nachbarringe zeigten Zahlen,
         der erste einen Fleck. */
      return '<div class="qring'+(ok?' fertig':'')+'">'+
        '<div class="kreisel">'+(ok ? '✓' : zN+'/'+zZiel)+'</div>'+
        tp(q.txt, zZiel)+'</div>';
    }).join('') + '</div>' +
    (fertig===qs.length && qs.length ? '<div class="qalle">'+t('quest.alle')+'</div>' : '');
}
/* Grüne Zeilen für den Ergebnisschirm. Leert questFrisch – deshalb feiert
   nach einem Neuladen nichts ein zweites Mal. */
function questZeilen(){
  if(!questFrisch.length) return '';
  const alle = questsHeute().every(questFertig);
  const zeilen = questFrisch.map(q =>
    '<div class="feedback ok">'+t('quest.fertig', symbolTexte({n:MUENZEN_PRO_QUEST}))+' · '+
    tp(q.txt, q.min ? Math.round(q.ziel/60) : q.ziel)+'</div>').join('');
  questFrisch = [];
  return zeilen + (alle ? '<div class="feedback ok"><b>'+t('quest.alle')+'</b></div>' : '');
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
