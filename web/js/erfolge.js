/* ---- Wegmarken ----
   Was gefeiert wird. Ajdin hat am 18.09.2026 aus vier Möglichkeiten nur die
   Lerntage gewählt - Wörter, Level und Geschichten bleiben bewusst draußen.
   Weitere Schwellen kosten hier nur eine Zeile und einen Text.

   Die Zahl kommt aus days.size und ist rückwirkend richtig: die App schreibt
   die Lerntage seit dem ersten Tag mit. Wer die App heute aktualisiert,
   verliert also nichts. */
const MEILENSTEINE = [
  {id:'tage7',    ziel:7,    txt:'wegmarke.t7'},
  {id:'tage30',   ziel:30,   txt:'wegmarke.t30'},
  {id:'tage100',  ziel:100,  txt:'wegmarke.t100'},
  {id:'tage365',  ziel:365,  txt:'wegmarke.t365'},
  {id:'tage1000', ziel:1000, txt:'wegmarke.t1000'},
];
/* Läuft gerade eine Wegmarke? Dann keine Werbung darüber - siehe lessonEnd.
   Eine Anzeige über dem 100. Lerntag wäre die schlechteste Minute, die sich
   die App aussuchen könnte. */
let wegmarkeLaeuft = false;

/* Wird aus markToday gerufen, also genau einmal je neuem Lerntag - NIE aus
   einer Zeichenfunktion. Sonst käme die Karte bei jedem Neuzeichnen wieder,
   und das ist derselbe Fehler, vor dem oben schon bei den Münzen gewarnt
   wird. */
function pruefeMeilensteine(){
  const n = days.size;
  const faellig = MEILENSTEINE.filter(m => n >= m.ziel && !gefeiert.has(m.id));
  if(!faellig.length) return;
  /* Mehrere auf einmal kann es geben: wer die App erst jetzt aktualisiert,
     hat 7, 30 und 100 längst hinter sich. Abgehakt werden dann alle, gefeiert
     nur die größte - fünf Karten hintereinander wären kein Fest mehr,
     sondern eine Warteschlange. */
  wegmarkeLaeuft = true;
  /* SOFORT abhaken und speichern, nicht erst beim Zeigen der Karte.
     Vorher stand das unten in zeigeWegmarke - der Gedanke war, dass eine
     Wegmarke nicht verlorengeht, wenn die App in den 1,4 Sekunden bis zur
     Karte zugemacht wird. Die Kehrseite war schlimmer: dann kam sie am
     nächsten Tag wieder. Ajdin hat das an zwei Tagen gesehen.
     Abgewogen: eine verpasste Wegmarke kostet einen Glückwunsch, und die
     nächste kommt trotzdem. Eine wiederholte lässt die App kaputt aussehen. */
  faellig.forEach(m => gefeiert.add(m.id));
  saveProgress();
  /* Erst der Ergebnisschirm, dann die Karte. Die Fanfare läuft 0,7 s, der
     Ton für die Tagesaufgabe kommt bei 0,85 s - die Wegmarke ist die größte
     Sache und kommt zuletzt. */
  setTimeout(()=> zeigeWegmarke(faellig[faellig.length - 1]), 1400);
}

function zeigeWegmarke(m){
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage';
  kasten.innerHTML =
    '<div class="nachfragebox wegmarkebox">' +
      '<div class="celebrate"><div class="zmaj cheer">' + zmaj('cheer') + '</div></div>' +
      '<div class="wegzahl">' + m.ziel + '</div>' +
      '<div class="wegwort">' + esc(tp('wegmarke.tage', m.ziel)) + '</div>' +
      '<div class="txt">' + esc(t(m.txt)) + '</div>' +
      '<button class="btn know" id="wegOk"></button>' +
    '</div>';
  kasten.querySelector('#wegOk').textContent = t('task.weiter');
  // Nur bei eingeschalteter Bewegung - siehe .schnipsel im Stilblatt.
  if(animOn){
    const farben = ['var(--accent)', 'var(--primary)', 'var(--good)', '#FFFFFF'];
    for(let i=0; i<26; i++){
      const s = document.createElement('i');
      s.className = 'schnipsel';
      s.style.left = (Math.random()*100).toFixed(1) + '%';
      s.style.background = farben[i % farben.length];
      s.style.animationDelay = (Math.random()*0.6).toFixed(2) + 's';
      s.style.animationDuration = (2.2 + Math.random()*1.6).toFixed(2) + 's';
      kasten.appendChild(s);
    }
  }
  document.body.appendChild(kasten);   // der Drache hängt sich selbst ein
  sound('wegmarke');
  /* Die Karte meldet sich bei der Zurueck-Taste an - wie frage() ,
     die Vollversionswahl und der Widerruf . Ohne das lief die
     Taste durch die Karte hindurch: am 7. Lerntag drueckte der erste Druck
     darunter "Lektion abbrechen", der noch nicht gelesene Ergebnisschirm war
     weg, und die Glueckwunschkarte schwebte danach ueber dem Lernpfad.
     Gefunden am 26.09.2026. Beim Schliessen wieder abmelden, sonst blockiert
     die Karte jede spaetere Nachfrage - frage() steigt bei gesetztem
     frageSchliessen sofort aus. */
  const zu = ()=>{ kasten.remove(); wegmarkeLaeuft = false;
                   if(frageSchliessen === zu) frageSchliessen = null; };
  frageSchliessen = zu;
  kasten.querySelector('#wegOk').addEventListener('click', zu);
  kasten.addEventListener('click', e=>{ if(e.target === kasten) zu(); });
}

/* Die längste Serie, die jemals lief - über ALLE Tage, nicht von heute
   rückwärts wie streak(). Dieselbe Regel wie dort: ein Frosttag überbrückt
   die Lücke, zählt aber selbst nicht mit.

   Gerechnet wird über den Mittag ('T12:00:00'). Um Mitternacht zu rechnen
   geht bei der Zeitumstellung schief: die Nacht hat dann 23 oder 25 Stunden,
   und ein Tagesabstand in Millisekunden stimmt nicht mehr. */
function laengsteSerie(){
  const alle = new Set([...days, ...frost]);
  if(!alle.size) return 0;
  let best = 0, lauf = 0, vor = null;
  for(const k of [...alle].sort()){
    if(vor !== null){
      const d = new Date(vor + 'T12:00:00'); d.setDate(d.getDate() + 1);
      if(dayKey(d) !== k) lauf = 0;          // Lücke: von vorn
    }
    if(days.has(k)) lauf++;
    if(lauf > best) best = lauf;
    vor = k;
  }
  return best;
}
function markToday(){
  const t=today();
  if(days.has(t)) return false;
  days.add(t);
  const n = streak(); if(n > rekord) rekord = n;
  pruefeMeilensteine();
  /* Wer heute geuebt hat, bekommt heute keine Erinnerung mehr. Geplant
     wird sonst beim Wechsel in den Hintergrund - ob die WebView dann noch
     lange genug laeuft, um die Plaene umzuschreiben, ist nicht sicher. */
  benPlanen();
  return true;
}

/* =================== ERFOLGE (13.11.2026) ===================
   Ajdin am 13.11.2026 zu Release\Entscheidungen_2026-11-13\erfolge.md:
   "alles wie empfohlen" (Fragen 8a, 9b, 10a). Seine Wahl vom 18.09.2026
   ("nur Lerntage") gilt weiter fuer das FEIERN: Karte und Konfetti gibt es
   nur bei den Lerntagen (MEILENSTEINE, zeigeWegmarke). SICHTBAR werden
   jetzt aber auch Flamme, Woerter, Stufen, Geschichten und "Fest im Kopf":
     - 18 Abzeichen in ERFOLGE. Jedes gehoert zu einer Kette (nur das
       naechste offene einer Kette bekommt einen Balken) und einer Gruppe
       (eine Zeile der Wand).
     - Zu sehen an drei Orten: oben im Profil die Leiste mit den drei
       neuesten und "x von 18" (renderErfolgLeiste), ein Tipp darauf zeigt
       die ganze Wand (showErfolge, renderErfolgWand), und eine ruhige Zeile
       auf dem Ergebnisschirm von Lektion, Test, Wiederholen-Runde und
       Geschichte (erfolgZeile) - ohne Ton, ohne Karte, ohne Konfetti.
       Die Leiste stand bis 14.11.2026 auf der Startseite unter
       "Weitermachen"; dort sagt jetzt nur ein roter Punkt am Profilknopf,
       dass etwas Neues da ist (profilPunkt). Ajdin am 14.11.2026: "mach
       die erfolge in dem benutzer menü rein", "ja roter punkt ist gut".
     - Rueckwirkend aus dem, was die App ohnehin speichert: Lerntage,
       laengste Serie (rekord), gewusste Woerter, bestandene Level,
       gelesene Geschichten, die Lernkartei. Wer das Update bekommt, hat
       seine Abzeichen sofort, liest einmal "Du hast schon 6 Abzeichen",
       und alle gelten als gesehen (erfolgeNachreichen).
     - Ein verdientes Abzeichen bleibt fuer immer, auch wenn die Zahl
       dahinter wieder faellt: die Stufe in der Kartei sinkt nach einem
       Fehler, eine Stufe bekommt neue Level, neue Geschichten kommen dazu.
     - Der Zahnarzt-Teil zaehlt nicht mit (ohneZa, nur CATEGORIES), wie bei
       Tagesaufgaben und Muenzen.
     - Keine Muenzen, kein Zufall, keine Uhrzeit, kein Vergleich mit
       anderen, kein "ohne Fehler" - siehe erfolge.md, "Regeln, damit kein
       Druck entsteht".
   Gespeichert wird in den VORHANDENEN Merkern, kein neues Feld (erfolge.md:
   die Cloud ist zu 91-95 % voll, siehe CLOUD_GROESSE_MAX):
     gefeiert  "e:<id>" heisst verdient. Wird beim Zusammenfuehren vereinigt
               und nie gekuerzt; auch 1.3 liest und schreibt die Eintraege
               unveraendert mit, sie fragt nur ihre "tage..."-Marken ab.
     wann      "e:<id>" -> Datum, nur wo es sich nicht jederzeit aus den
               Daten ablesen laesst: Woerter, Stufen, alle Geschichten, Fest
               im Kopf. Lerntage, Flamme und die erste Geschichte rechnet
               erfolgDatum() aus tage, frost und "gs:" nach.
   Mit allen 18 sind das rund 360 Bytes mehr im Stand (tests_e2e/
   test_erfolge.py misst es).
   Ob ein Abzeichen schon angesehen wurde (roter Punkt), merkt sich nur das
   Geraet (ERFOLG_GESEHEN) - eine Bequemlichkeit, kein Lernstand, und in
   der Cloud kostet es nichts. Auf einem neuen Geraet steht einmal der Satz
   "Du hast schon ..." statt roter Punkte. */
const ERFOLG_VORN = 'e:';
const ERFOLG_GESEHEN = 'zmaj_erfolge_gesehen';
/* Ab dieser Stufe der Lernkartei ist ein Wort "fest im Kopf": der Abstand
   von 90 Tagen (erfolge.md, "Gedaechtnis"). */
const KARTEI_FEST = KARTEI_ABSTAENDE.indexOf(90);
/* Welche Stufe ein Level hat, fuer die Abzeichen A1, A2 und B1. Bringen
   die Stufen-Reiter (1.4) das Feld stufe oder reiter an Level oder
   Sektion mit, gilt es. Seit dem Zusammenfuehren in sammeln-v112
   (13.11.2026) traegt jede Sektion in SEKTIONEN ihre stufe, also gilt
   immer das Feld - auch fuer die beiden neuen Grundwort-Level und
   "Zuhause" hinter Faelle 1. Die Tabelle darunter ist nur noch der Rueckhalt
   fuer einen Inhalt ohne das Feld: die Zuordnung aus
   Release\Entscheidungen_2026-11-13\level_reiter.csv (Variante B): "Saetze
   bauen" ist dort geteilt, seine ersten sechs Level gehoeren zu A1, der
   Rest zu A2. Alles ab B2 hat noch kein Abzeichen - erst, wenn die letzten
   B2-Pakete drin sind, sonst waere es zu frueh verdient (erfolge.md). */
const STUFE_NACH_SEKTION = {alltag: 'A1', anfassen: 'A1', tiernatur: 'A1',
  zuhause2: 'A2', einkauf: 'A2', herkunft: 'A2', kultur: 'A2',
  amt: 'B1', tunlassen: 'B1', wieetwasist: 'B1', koerpergesundheit: 'B1', zeitfreizeit: 'B1',
  lernenarbeiten: 'B1', grundbegriffe: 'B1', menschengesellschaft: 'B1', wiewowann: 'B1'};
const SAETZE_A1 = ['fragen', 'genus', 'konjugation', 'mehrzahl', 'satzbau', 'faelle1'];
function levelStufe(c){
  const s = SECTIONS.find(x => x.id === c.sektion) || {};
  const feld = [c.stufe, c.reiter, s.stufe, s.reiter].find(x => typeof x === 'string' && x);
  if(feld) return feld.toUpperCase();
  if(c.sektion === 'saetze') return SAETZE_A1.includes(c.id) ? 'A1' : 'A2';
  return STUFE_NACH_SEKTION[c.sektion] || '';
}
/* Die 18 Abzeichen, in der Reihenfolge der Wand. Ein weiteres kostet eine
   Zeile hier und seine Texte (erfolg.*). Die Kennung steht im Lernstand
   ("e:w500") und darf sich deshalb nie aendern.
     ziel    die Schwelle; bei Stufen und "alle Geschichten" rechnet
             erfolgStand() sie aus dem Inhalt
     merken  das Datum kommt in wann, siehe oben
     name    der Text unter dem Ring; sonst die Stufe oder die Zahl */
const ERFOLGE = [
  {id: 't7',    kette: 'tage',    gruppe: 'tage',    ziel: 7,    name: 'erfolg.t7'},
  {id: 't30',   kette: 'tage',    gruppe: 'tage',    ziel: 30,   name: 'erfolg.t30'},
  {id: 't100',  kette: 'tage',    gruppe: 'tage',    ziel: 100,  name: 'erfolg.t100'},
  {id: 't365',  kette: 'tage',    gruppe: 'tage',    ziel: 365,  name: 'erfolg.t365'},
  {id: 't1000', kette: 'tage',    gruppe: 'tage',    ziel: 1000, name: 'erfolg.t1000'},
  {id: 'f30',   kette: 'flamme',  gruppe: 'flamme',  ziel: 30,   name: 'erfolg.blau', ton: 'blau'},
  {id: 'f100',  kette: 'flamme',  gruppe: 'flamme',  ziel: 100,  name: 'erfolg.lila', ton: 'lila'},
  {id: 'f365',  kette: 'flamme',  gruppe: 'flamme',  ziel: 365,  name: 'erfolg.gold', ton: 'gold'},
  {id: 'w100',  kette: 'woerter', gruppe: 'woerter', ziel: 100,  merken: true},
  {id: 'w500',  kette: 'woerter', gruppe: 'woerter', ziel: 500,  merken: true},
  {id: 'w1000', kette: 'woerter', gruppe: 'woerter', ziel: 1000, merken: true},
  {id: 'w2500', kette: 'woerter', gruppe: 'woerter', ziel: 2500, merken: true},
  {id: 'a1',    kette: 'stufen',  gruppe: 'stufen',  stufe: 'A1', merken: true},
  {id: 'a2',    kette: 'stufen',  gruppe: 'stufen',  stufe: 'A2', merken: true},
  {id: 'b1',    kette: 'stufen',  gruppe: 'stufen',  stufe: 'B1', merken: true},
  {id: 'g1',    kette: 'lesen',   gruppe: 'lesen',   ziel: 1,    name: 'erfolg.erste'},
  {id: 'ga',    kette: 'lesen',   gruppe: 'lesen',   name: 'erfolg.alle', merken: true},
  {id: 'k100',  kette: 'kopf',    gruppe: 'lesen',   ziel: 100,  name: 'erfolg.kopf', merken: true},
];
const ERFOLG_GRUPPEN = [
  {id: 'tage', titel: 'erfolg.gruppe_tage'}, {id: 'flamme', titel: 'erfolg.gruppe_flamme'},
  {id: 'woerter', titel: 'erfolg.gruppe_woerter'}, {id: 'stufen', titel: 'erfolg.gruppe_stufen'},
  {id: 'lesen', titel: 'erfolg.gruppe_lesen'}];
const erfolgVerdient = e => gefeiert.has(ERFOLG_VORN + e.id);
const erfolgeVerdient = () => ERFOLGE.filter(erfolgVerdient);
/* Woerter, die in der Kartei die 90-Tage-Stufe erreicht haben. */
function festImKopf(){
  let n = 0;
  Object.keys(kartei.w).forEach(id => {
    const e = kartei.w[id];
    if(!istZa(id) && Array.isArray(e) && e[0] >= KARTEI_FEST) n++;
  });
  return n;
}
const erfolgStufenLevel = stufe => CATEGORIES.filter(c => levelStufe(c) === stufe);
/* Wie weit ein Abzeichen ist: {wert, ziel}. ziel 0 heisst "gibt es hier
   nicht" (eine Stufe ohne Level, kein Inhalt geladen) - nie verdient. */
function erfolgStand(e){
  switch(e.kette){
    case 'tage':    return {wert: days.size, ziel: e.ziel};
    case 'flamme':  return {wert: rekord, ziel: e.ziel};
    case 'woerter': return {wert: ohneZa(known), ziel: e.ziel};
    case 'stufen': {
      const lv = erfolgStufenLevel(e.stufe);
      return {wert: lv.filter(c => passed.has(c.id)).length, ziel: lv.length};
    }
    case 'lesen':   return {wert: STORIES.filter(s => read.has(s.id)).length, ziel: e.ziel || STORIES.length};
    case 'kopf':    return {wert: festImKopf(), ziel: e.ziel};
  }
  return {wert: 0, ziel: 0};
}
function erfolgErreicht(e){ const s = erfolgStand(e); return s.ziel > 0 && s.wert >= s.ziel; }
/* Der Tag, an dem eine Serie zum ersten Mal n Tage lang war. Dieselbe
   Zaehlung wie laengsteSerie(): ein Frosttag ueberbrueckt, zaehlt aber
   selbst nicht mit. */
function serieErreicht(n){
  let lauf = 0, vor = null;
  for(const k of [...new Set([...days, ...frost])].sort()){
    if(vor !== null){
      const d = new Date(vor + 'T12:00:00'); d.setDate(d.getDate() + 1);
      if(dayKey(d) !== k) lauf = 0;
    }
    if(days.has(k) && ++lauf >= n) return k;
    vor = k;
  }
  return '';
}
const wannDatum = k => istDatum(wann[k]) ? wann[k] : '';
/* Das Datum eines verdienten Abzeichens, '' wenn es keins gibt (Woerter,
   die schon vor dem Update sassen). */
function erfolgDatum(e){
  if(e.kette === 'tage') return [...days].sort()[e.ziel - 1] || '';
  if(e.kette === 'flamme') return serieErreicht(e.ziel);
  if(e.id === 'g1') return Object.keys(wann).filter(k => k.startsWith('gs:')).map(wannDatum).filter(Boolean).sort()[0] || '';
  return wannDatum(ERFOLG_VORN + e.id);
}
/* Rueckwirkend: das spaeteste Datum der Level einer Stufe bzw. aller
   Geschichten - nur, wenn jedes eins hat ("wann" gibt es erst seit dem
   19.09.2026). */
function erfolgDatumNachgerechnet(e){
  const keys = e.kette === 'stufen' ? erfolgStufenLevel(e.stufe).map(c => 'lv:' + c.id)
             : (e.id === 'ga' ? STORIES.map(s => 'gs:' + s.id) : []);
  const d = keys.map(wannDatum);
  return (d.length && d.every(Boolean)) ? d.sort()[d.length - 1] : '';
}
/* Hakt ab, was erreicht und noch nicht verdient ist, und gibt das Neue
   zurueck. Speichert NICHT - das tut der Aufrufer, auf den Ergebnisschirmen
   ohnehin gleich danach. live: das Abzeichen faellt gerade jetzt, also
   bekommt es das heutige Datum, wenn sich keins nachrechnen laesst. Beim
   ersten Start nach dem Update nicht: wann jemand seine 500 Woerter
   geschafft hat, weiss die App nicht, und erfunden wird kein Datum. */
function erfolgePruefen(live){
  if(!CATEGORIES.length) return [];
  const neu = [];
  ERFOLGE.forEach(e => {
    if(erfolgVerdient(e) || !erfolgErreicht(e)) return;
    gefeiert.add(ERFOLG_VORN + e.id);
    if(e.merken){
      const d = erfolgDatumNachgerechnet(e) || (live ? today() : '');
      if(d) wann[ERFOLG_VORN + e.id] = d;
    }
    neu.push(e);
  });
  return neu;
}
/* Was auf diesem Geraet schon angesehen wurde. null: noch nie etwas -
   der erste Start mit Erfolgen. Geht der Speicher nicht, gilt alles als
   gesehen: lieber kein roter Punkt als einer, der nie weggeht. */
function erfolgeGesehen(){
  try{
    const roh = localStorage.getItem(ERFOLG_GESEHEN);
    if(roh === null) return null;
    const l = JSON.parse(roh);
    return new Set(Array.isArray(l) ? l.filter(x => typeof x === 'string') : []);
  }catch(e){ return new Set(ERFOLGE.map(x => x.id)); }
}
function erfolgeAlsGesehen(){
  try{ localStorage.setItem(ERFOLG_GESEHEN, JSON.stringify(erfolgeVerdient().map(e => e.id))); }catch(e){}
}
/* Aus showHome(): still nachtragen, was ausserhalb der Ergebnisschirme
   erreicht wurde - rueckwirkend beim ersten Start nach dem Update, nach
   der Einstufung, nach dem Abgleich mit der Cloud. Kein Ton, keine Karte;
   Neues traegt nur den roten Punkt. Beim allerersten Mal auf diesem Geraet
   gilt alles Erreichte als gesehen, und einmal kommt der Satz "Du hast
   schon 6 Abzeichen" - wie bei den Wegmarken wird nichts nachgefeiert.
   Solange auf dem Geraet noch nichts gelernt ist (frisch installiert, vor
   der Anmeldung mit einem Konto von frueher), merkt es sich noch nichts:
   Kommt der Stand gleich danach aus der Cloud, zaehlt das wie ein Update -
   sonst truege jedes alte Abzeichen einen roten Punkt und das heutige
   Datum. Wer vor der Anmeldung schon gelernt hat, dessen Geraet merkt sich
   bereits etwas; fuer ihn erledigt das der erste Abgleich
   (erfolgeErsterAbgleich). */
function erfolgeNachreichen(){
  if(!standGeladen || !CATEGORIES.length) return;
  const gesehen = erfolgeGesehen();
  if(gesehen === null && !hatGelernt()) return;
  if(gesehen === null ? erfolgeWieUpdate() : erfolgePruefen(true).length) saveProgress();
}
/* Wie beim ersten Start nach dem Update: nachtragen ohne erfundenes Datum,
   alles gilt als gesehen, und einmal der Satz "Du hast schon 6 Abzeichen" -
   wenn eins dabei ist, das dieses Geraet noch nicht gezeigt hat. Gibt
   zurueck, ob eins dazukam; speichern muss der Aufrufer. */
function erfolgeWieUpdate(){
  const vorher = erfolgeGesehen();
  const neu = erfolgePruefen(false).length > 0;
  erfolgeAlsGesehen();
  const alle = erfolgeVerdient();
  if(alle.some(e => !vorher || !vorher.has(e.id))) erfolgSchonMelden(alle.length);
  return neu;
}
/* Aus cloudUebernehmen(), wenn dieses Geraet zum ersten Mal mit einem Konto
   abgleicht: zaehlt wie ein Update (Pruefbefund 13.11.2026). Auf dem neuen
   Handy kommt das Tor erst nach Lektion 1 oder der Einstufung, und dabei
   speichert erfolgZeile() bzw. erfolgeNachreichen() schon die leere Liste
   des Gesehenen. Danach galten alle alten Abzeichen als frisch verdient:
   roter Punkt, kein Satz, und Woerter und Kartei bekamen das heutige
   Datum - das beim Zusammenfuehren als das fruehere fuer immer im Konto
   bliebe. Ohne Inhalt (kann nicht pruefen) vergisst das Geraet das
   Gesehene, dann nimmt erfolgeNachreichen() den Weg des Updates. */
function erfolgeErsterAbgleich(){
  if(CATEGORIES.length){ erfolgeWieUpdate(); return; }
  try{ localStorage.removeItem(ERFOLG_GESEHEN); }catch(e){}
}
/* Der Satz erst, wenn der Vorspann weg ist (Pruefbefund 13.11.2026):
   showHome() laeuft beim Start schon darunter, und nach 3,2 s war der Satz
   wieder weg, bevor die Startseite zu sehen war. vorspannVorbei steht
   weiter unten im Skript, daher das try. */
function erfolgSchonMelden(n){
  const melden = () => kurzMeldung(tp('erfolg.schon', n));
  let warten = null;
  try{ warten = vorspannVorbei; }catch(e){}
  if(warten) warten.then(melden); else melden();
}
function zahlText(n){ try{ return Number(n).toLocaleString(SPRACHE); }catch(e){ return String(n); } }
function datumText(d){ try{ return new Date(d + 'T12:00:00').toLocaleDateString(SPRACHE); }catch(e){ return d; } }
function erfolgName(e){ return e.name ? t(e.name) : (e.stufe || zahlText(e.ziel)); }
/* Der kurze Satz zum Abzeichen - beim Antippen in der Wand und in der
   Zeile am Lektionsende ("Neues Abzeichen: 500 Woerter sitzen"). */
function erfolgSatz(e){
  const n = zahlText(e.ziel);
  switch(e.kette){
    case 'tage':    return t('erfolg.satz_tage', {n});
    case 'flamme':  return t('erfolg.satz_flamme', {n});
    case 'woerter': return t('erfolg.satz_woerter', {n});
    case 'stufen':  return t('erfolg.satz_stufe', {stufe: e.stufe});
    case 'kopf':    return t('erfolg.satz_kopf', {n});
  }
  return t(e.id === 'g1' ? 'erfolg.satz_erste' : 'erfolg.satz_alle');
}
/* Die gemalten Abzeichen in web/erfolge/ (Gemini, Ajdin 10a; Bogen-Entwurf
   vom 13.11.2026 in Release\Entscheidungen_2026-11-13\erfolge_bogen_entwurf.png,
   als Richtung freigegeben). Jedes Abzeichen hat sein eigenes Bild,
   in einer Kette waechst es mit: Kalender mit Haken, Stern, Pokal, Krone,
   goldener Kalender mit Edelstein - eine Karte, drei, ein dicker Stapel, ein
   voller Karteikasten - ein, zwei, drei Stufen - ein Buch, ein Buecherstapel -
   das Gehirn. 128 x 128 wie web/symbole. Die Farbe der Kette macht weiter
   der Ring. Die Flamme bleibt das gemalte Bild der Serie, eingefaerbt wie
   dort. Kommt ein Abzeichen ohne Bild dazu (spaeter B2, C1), greift der
   Platzhalter darunter. */
const ERFOLG_BILDER = Object.fromEntries(
  ['t7', 't30', 't100', 't365', 't1000', 'w100', 'w500', 'w1000', 'w2500',
   'a1', 'a2', 'b1', 'g1', 'ga', 'k100'].map(id => [id, 'erfolge/' + id + '.webp']));
function erfolgBild(e){
  if(e.kette === 'flamme') return '<img class="ton-' + e.ton + '" src="flamme/flamme.webp" alt="">';
  if(ERFOLG_BILDER[e.id]) return '<img src="' + ERFOLG_BILDER[e.id] + '" alt="">';
  switch(e.kette){
    case 'tage':    return '<img src="symbole/lernpfad.webp" alt="">';
    case 'woerter': return 'Č';
    case 'stufen':  return esc(e.stufe);
    case 'kopf':    return '<img src="symbole/wiederholen.webp" alt="">';
  }
  return '<img src="symbole/geschichten.webp" alt="">';
}
/* Die Zahl auf dem Ring. Bei den Stufen steht dort ihr Name (A1), seit das
   gemalte Bild ihn nicht mehr traegt - nur der Platzhalter zeigt ihn selbst.
   "Alle Geschichten" haengt am Inhalt und bleibt ohne. */
const erfolgPille = e => e.kette === 'stufen' ? (ERFOLG_BILDER[e.id] ? e.stufe : '')
  : e.id === 'ga' ? '' : zahlText(e.ziel);
/* Der Ring ist Schmuck (aria-hidden): vorgelesen werden Name und Zustand
   daneben, nicht "Č 100 100". */
function erfolgRing(e, an, neu, mitZahl){
  const pille = mitZahl ? erfolgPille(e) : '';
  return '<span class="abzring k-' + e.kette + (e.ton ? ' t-' + e.ton : '') + (an ? '' : ' aus') + (neu ? ' neu' : '') + '" aria-hidden="true">' +
    '<span class="abzbild">' + erfolgBild(e) + '</span>' +
    (pille ? '<span class="abzzahl">' + esc(pille) + '</span>' : '') + '</span>';
}
/* Was beim Antippen unter der Gruppe steht: der Satz, dazu das Datum -
   oder bei einem offenen, wie weit es ist. */
function erfolgInfo(e){
  if(erfolgVerdient(e)){
    const d = erfolgDatum(e);
    return erfolgSatz(e) + ' · ' + (d ? t('erfolg.am', {datum: datumText(d)}) : t('erfolg.geschafft'));
  }
  const s = erfolgStand(e);
  return erfolgSatz(e) + ' · ' + zahlText(Math.min(s.wert, s.ziel)) + ' / ' + zahlText(s.ziel);
}
/* Was ein Bildschirmleser zu einem Abzeichen der Wand sagt (Pruefbericht
   1.4, S15). Vorher nur der Name unter dem Ring und der Zustand: "100,
   geschafft" - ohne die Gruppe darueber versteht das niemand, den ganzen
   Satz gab es erst nach dem Antippen. Jetzt der Satz selbst ("100 Woerter
   sitzen, geschafft"). Steht der sichtbare Name nicht schon darin, kommt
   er davor ("1 Woche, 7 Tage gelernt, geschafft"): der Name, den man
   sieht, soll auch im vorgelesenen stecken (WCAG 2.5.3). Der weiche
   Trennstrich in "Bomben-gedaechtnis" gehoert nicht in den Vergleich. */
function erfolgVorlesen(e, an, neu){
  const name = erfolgName(e).replace(/\u00ad/g, ''), satz = erfolgSatz(e);
  const teile = satz.toLowerCase().includes(name.toLowerCase()) ? [satz] : [name, satz];
  teile.push(t(an ? 'erfolg.geschafft' : 'erfolg.offen'));
  if(neu) teile.push(t('erfolg.neu_kurz'));
  return teile.join(', ');
}
/* Die Wand, hinter der Leiste oben im Profil (showErfolge). Je Kette
   bekommt nur das erste offene einen Balken; offene sind grau, noch nicht
   angesehene tragen den roten Punkt. Danach gilt alles als gesehen - beim
   naechsten Oeffnen ist der Punkt weg, auch der am Profilknopf. */
function renderErfolgWand(){
  const box = $('erfolgWand');
  if(!box) return;
  if(!CATEGORIES.length || !standGeladen){ box.hidden = true; box.innerHTML = ''; return; }
  const gesehen = erfolgeGesehen() || new Set();
  const naechste = new Set(), ketten = new Set();
  ERFOLGE.forEach(e => {
    if(erfolgVerdient(e) || ketten.has(e.kette)) return;
    ketten.add(e.kette); naechste.add(e.id);
  });
  const abzeichen = e => {
    const an = erfolgVerdient(e), neu = an && !gesehen.has(e.id), s = erfolgStand(e);
    const balken = !an && naechste.has(e.id) && s.ziel > 0;
    const wert = Math.min(s.wert, s.ziel);
    return '<button type="button" class="abz' + (an ? '' : ' offen') + '" data-erfolg="' + e.id + '">' +
      erfolgRing(e, an, neu, true) +
      '<span class="abzname" aria-hidden="true">' + esc(erfolgName(e)) + '</span>' +
      '<span class="nurleser">' + esc(erfolgVorlesen(e, an, neu)) + '</span>' +
      (balken ? '<span class="abzbalken" aria-hidden="true"><i style="width:' + Math.round(wert / s.ziel * 100) + '%"></i></span>' +
                '<span class="abzweit">' + esc(zahlText(wert) + ' / ' + zahlText(s.ziel)) + '</span>' : '') +
      '</button>';
  };
  box.innerHTML =
    '<div class="abzkopf"><h2>' + esc(t('erfolg.titel')) + '</h2><span class="abzstand">' +
      esc(t('erfolg.stand', {n: erfolgeVerdient().length, gesamt: ERFOLGE.length})) + '</span></div>' +
    ERFOLG_GRUPPEN.map(g => '<div class="abzgruppe"><h3>' + esc(t(g.titel)) + '</h3>' +
      '<div class="abzwand">' + ERFOLGE.filter(e => e.gruppe === g.id).map(abzeichen).join('') + '</div>' +
      '<div class="abzinfo" aria-live="polite"></div></div>').join('');
  box.hidden = false;
  box.querySelectorAll('.abz').forEach(b => b.addEventListener('click', () => {
    const e = ERFOLGE.find(x => x.id === b.dataset.erfolg), info = b.closest('.abzgruppe').querySelector('.abzinfo');
    if(!e || !info) return;
    const war = info.dataset.erfolg === e.id;
    info.dataset.erfolg = war ? '' : e.id;
    info.textContent = war ? '' : erfolgInfo(e);
  }));
  if(erfolgeGesehen() !== null || hatGelernt()) erfolgeAlsGesehen();   // siehe erfolgeNachreichen
  profilPunkt();
}
/* Die Leiste oben im Profil (bis 14.11.2026 auf der Startseite): die drei
   zuletzt verdienten (ohne Datum zuletzt, bei gleichem Datum das spaetere
   der Liste zuerst) und "7 von 18". Ist noch keins verdient, steht grau
   das, dem man am naechsten ist - eine leere Leiste saehe kaputt aus.
   Noch nicht angesehene tragen den roten Punkt, bis die Wand offen war. */
function renderErfolgLeiste(){
  const el = $('erfolgLeiste');
  if(!el) return;
  if(!profil || !CATEGORIES.length || !standGeladen){ el.hidden = true; el.innerHTML = ''; return; }
  const gesehen = erfolgeGesehen() || new Set();
  const da = ERFOLGE.map((e, i) => ({e, i, d: erfolgDatum(e)})).filter(x => erfolgVerdient(x.e));
  da.sort((a, b) => (a.d === b.d ? b.i - a.i : (a.d < b.d ? 1 : -1)));
  let ringe = da.slice(0, 3).map(x => erfolgRing(x.e, true, !gesehen.has(x.e.id), false));
  if(!ringe.length){
    const anteil = e => { const s = erfolgStand(e); return s.ziel > 0 ? s.wert / s.ziel : -1; };
    const naechstes = ERFOLGE.reduce((best, e) => anteil(e) > anteil(best) ? e : best, ERFOLGE[0]);
    ringe = [erfolgRing(naechstes, false, false, false)];
  }
  el.innerHTML =
    '<span class="eltext"><span class="elkopf">' + esc(t('erfolg.titel')) + '</span>' +
      '<span class="elstand">' + esc(t('erfolg.stand', {n: da.length, gesamt: ERFOLGE.length})) + '</span></span>' +
    '<span class="elbilder" aria-hidden="true">' + ringe.join('') + '</span>' +
    '<span class="elpfeil" aria-hidden="true">›</span>';
  el.hidden = false;
}
/* Der rote Punkt am Profilknopf oben (14.11.2026): ein verdientes
   Abzeichen, das auf diesem Geraet noch nicht in der Wand zu sehen war -
   dieselbe Merkung wie die Punkte in Leiste und Wand (erfolgeGesehen). Er
   geht weg, sobald die Wand offen war, nicht schon beim Blick ins Profil:
   dort steht er weiter auf dem Ring in der Leiste. Ein Bildschirmleser
   hoert ihn mit, "Profil, Neues Abzeichen: 100 Woerter sitzen". */
function profilPunkt(){
  const b = $('btnProfil');
  if(!b) return;
  const gesehen = erfolgeGesehen() || new Set();
  const neu = (standGeladen && CATEGORIES.length) ? erfolgeVerdient().filter(e => !gesehen.has(e.id)) : [];
  b.classList.toggle('neu', neu.length > 0);
  if(neu.length) b.setAttribute('aria-label', t('set.profil') + ', ' +
    (neu.length === 1 ? t('erfolg.neu', {name: erfolgSatz(neu[0])}) : t('erfolg.neu_mehr', {n: neu.length})));
  else b.removeAttribute('aria-label');
}
/* Die ruhige Zeile fuer den Ergebnisschirm (Ajdin 13.11.2026, 9b): neu
   verdiente Abzeichen, gruen wie die Tagesaufgaben, ohne Ton und ohne
   Konfetti. Prueft und hakt ab - also genau einmal je Ergebnisschirm rufen,
   VOR dessen saveProgress(). '' wenn nichts neu ist. Die Lerntage bekommen
   ihre grosse Karte weiter von pruefeMeilensteine(); diese Zeile steht
   dann still darunter. */
function erfolgZeile(){
  if(!standGeladen) return '';
  /* Die erste Lektion ueberhaupt: was bis eben verdient war, gilt als
     gesehen, das Neue bekommt seinen roten Punkt (siehe
     erfolgeNachreichen - vorher merkt sich das Geraet nichts). */
  if(erfolgeGesehen() === null) erfolgeAlsGesehen();
  const neu = erfolgePruefen(true);
  if(!neu.length) return '';
  profilPunkt();   // nach einer Geschichte steht der Kopf mit dem Profilknopf darueber
  const titel = neu.length === 1 ? t('erfolg.neu', {name: erfolgSatz(neu[0])}) : t('erfolg.neu_mehr', {n: neu.length});
  return '<div class="erfolgzeile"><span class="ezbilder" aria-hidden="true">' +
    neu.slice(-3).reverse().map(e => erfolgRing(e, true, false, false)).join('') + '</span>' +
    '<span class="ezt">' + esc(titel) + '<span class="ezs">' + esc(t('erfolg.im_profil')) + '</span></span></div>';
}

/* ---- Tagesaufgaben ----
   Drei Stück am Tag, ausgelost aus Profilname und Datum. WELCHE drei es sind,
   wird nirgends gespeichert, sondern jedes Mal neu ausgerechnet – deshalb
   kommen beim Neuladen, im zweiten Tab und auf dem Handy zwingend dieselben
   drei heraus. Man kann sich also keine leichten erwürfeln.

   Wichtige Regel: In die Auslosung darf nur eingehen, was sich im Lauf des
   Tages NICHT mehr ändert. Also nicht `passed`, nicht `read`, nicht `catIdx` –
   sonst stünden nach der ersten Lektion drei andere Aufgaben da und der
   Fortschritt in den alten wäre weg. Erlaubt: profil, today(), Lerntage vor
   heute, canListen, known.size.

   Gespeichert wird nur `tagwerk`: die Zähler je Tag. */
const alleWoerter = () => CATEGORIES.reduce((n,c)=>n+c.words.length, 0);

/* known.size darf laut der Regel darueber in die Auslosung - die Bedingung
   "es gibt noch unbekannte Woerter" kippt aber doch mitten am Tag, naemlich
   in der Lektion, in der das letzte unbekannte Wort richtig beantwortet wird.
   Ab diesem Augenblick fiel 'neu' aus questTopf(), zieh() mischte aus acht
   statt neun Arten und lieferte fuer denselben Tag drei ANDERE Aufgaben: der
   Fortschritt der angefangenen war weg, und die neu gezogenen standen wegen
   tagwerk sofort mit Haken da, ohne dass Muenzen geflossen waeren - zaehle()
   zahlt nur im Augenblick des Ueberschreitens. Deshalb bleibt die Aufgabe an
   dem Tag, an dem das letzte Wort fiel, noch im Topf. Der Tag liegt in wann,
   damit es nach einem Neustart und im zweiten Tab genauso ausgeht - eine
   Sitzungsvariable waere hier zu wenig. Gefunden am 26.09.2026. */
function neuNochMoeglich(){
  const alle = alleWoerter();
  if(!alle || ohneZa(known) < alle) return true;   // !alle: Inhalt noch nicht geladen
  /* Eingehaengt in QUESTS erst am 07.10.2026 - bis dahin stand dort
     weiter known.size < alleWoerter(). Wer schon VOR diesem Update alle
     Woerter konnte, hat noch keinen Tag in wann; der heutige waere
     falsch und braechte 'neu' heute zurueck in den Topf - die Aufgaben
     wechselten beim Update einmal mitten am Tag, und 'neu' waere nicht
     zu schaffen. Faellt das letzte Wort wirklich heute, hat zaehle('neu')
     schon gezaehlt, bevor die Auslosung hierher fragt. */
  if(!wann.alleWoerter){ wann.alleWoerter = questStand('neu') > 0 ? today() : tagMinus(today(), 1); saveProgress(); }
  return wann.alleWoerter === today();
}

/* Die Ziele waren auf GENAU EINE Lektion kalibriert, und zwar systematisch:
   eine Lektion bringt 10 Wortaufgaben, 2 Lückentexte, bis zu 2
   Grammatikaufgaben und - bei fünf Aufgabenarten im Wechsel - etwa 2
   Hörübungen. Stufe 1 verlangte 8 richtige, 2 Hörübungen, 2 Lückentexte,
   3 neue Wörter: alles mit einer Lektion erledigt.
   Ajdin am 27.09.2026: "ich hab doch gesagt das die ziele nicht bei lektion
   geschafft sein sollen das ist zu viel". Die Mengenziele liegen jetzt bei
   etwa zwei Lektionen.
   NICHT angehoben sind 'gesch' (eine Geschichte lesen ist eine eigene
   Handlung, kein Nebenprodukt der Lektion) und 'per' (fehlerfrei ist ein
   Güte-, kein Mengenziel). */
const QUESTS = [
  {id:'auf',   art:'menge',   dick:1, ohneLeben:true, ziele:[20,30,40], txt:'quest.aufgaben'},
  {id:'ric',   art:'menge',   dick:1, ohneLeben:true, ziele:[18,26,34], txt:'quest.richtig'},
  {id:'gesch', art:'lesen',   dick:2, ohneLeben:true, ziele:[1,1,1],    txt:'quest.geschichte'},
  {id:'lue',   art:'typ',     dick:1, ziele:[4,6,8],  txt:'quest.luecken'},
  {id:'hoer',  art:'typ',     dick:1, ziele:[4,6,8],  txt:'quest.hoeren',     geht:()=>canListen},
  {id:'neu',   art:'woerter', dick:2, ziele:[10,14,18], txt:'quest.woerter',  geht:neuNochMoeglich},
  {id:'lek',   art:'lektion', dick:2, ziele:[2,3,4],  txt:'quest.lektionen'},
  {id:'per',   art:'lektion', dick:3, ziele:[1,1,1],  txt:'quest.fehlerfrei', abStufe:2},
  // Zeit in Sekunden gespeichert, in Minuten angezeigt – siehe uhrTakt()
  {id:'zeit',  art:'zeit',    dick:2, ohneLeben:true, ziele:[600,900,1200], txt:'quest.minuten', min:true}
];

/* Die Stufe zählt nur Tage VOR heute, damit sie sich tagsüber nicht ändert
   und die drei Aufgaben nicht mitten am Tag wechseln. */
function questStufe(){
  const t=today(); let n=0;
  days.forEach(d => { if(d < t) n++; });
  return n >= 21 ? 3 : (n >= 5 ? 2 : 1);
}
/* Zahl aus Text (FNV-1a) und Würfel mit festem Startwert (mulberry32):
   gleicher Startwert, gleiche Reihe. Ohne Fremdcode, die App lädt nichts nach. */
function saatAus(text){
  let h = 2166136261;
  for(let i=0;i<text.length;i++){ h ^= text.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function wuerfel(saat){
  let a = saat >>> 0;
  return function(){
    a = (a + 0x6D2B79F5) >>> 0;
    let x = Math.imul(a ^ (a >>> 15), 1 | a);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}
function mischeFest(liste, rnd){
  const a = liste.slice();
  for(let i=a.length-1;i>0;i--){ const j=Math.floor(rnd()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; }
  return a;
}
const tagMinus = (tag, d) => { const x=new Date(tag+'T12:00:00'); x.setDate(x.getDate()-d); return dayKey(x); };

function questTopf(stufe){
  return QUESTS.filter(q => (q.abStufe||1) <= stufe && (!q.geht || q.geht()));
}
/* Zieht drei Aufgaben für einen Tag. `meide` sind die von gestern – die
   rutschen nach hinten, damit nicht tagelang dasselbe kommt. */
function zieh(tag, stufe, meide){
  const liste = mischeFest(questTopf(stufe), wuerfel(saatAus(questSaat()+'|'+tag)))
    .sort((x,y) => (meide.indexOf(x.id)>=0?1:0) - (meide.indexOf(y.id)>=0?1:0));
  const raus=[], arten=new Set(); let dick=0;
  for(const q of liste){
    if(arten.has(q.art)) continue;      // nicht zweimal fast dasselbe
    if(q.dick === 3 && dick) continue;  // höchstens eine schwere am Tag
    arten.add(q.art); if(q.dick === 3) dick++;
    raus.push(q);
    if(raus.length === 3) break;
  }
  // Mindestens eine Aufgabe, die auch mit null Herzen geht
  if(raus.length && !raus.some(q => q.ohneLeben)){
    const ersatz = liste.find(q => q.ohneLeben);
    if(ersatz) raus[raus.length-1] = ersatz;
  }
  return raus;
}
function questsHeute(){
  const tag=today(), stufe=questStufe();
  const gestern = zieh(tagMinus(tag,1), stufe, []).map(q=>q.id);
  return zieh(tag, stufe, gestern).map(q => ({...q, ziel: q.ziele[stufe-1]}));
}
const questStand = id => (tagwerk[today()] || {})[id] || 0;
const questFertig = q => questStand(q.id) >= q.ziel;

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
