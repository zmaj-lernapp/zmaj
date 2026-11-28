/* =================== BENACHRICHTIGUNGEN ===================
   Festgelegt von Ajdin am 30.09.2026: drei Arten, jede einzeln
   abschaltbar - die taegliche Erinnerung um 19 Uhr, die Warnung um 20 Uhr,
   bevor die Serie reisst, und eine Nachricht, wenn die Leben nach dem
   Aufbrauchen wieder voll sind. Hoechstens EINE Nachricht am Abend. Um
   Erlaubnis gefragt wird nach der ersten Lektion.

   Geplant wird im Voraus, denn um 19 Uhr laeuft die App meist nicht. Die
   Plaene werden jedes Mal neu gemacht, wenn die App in den Hintergrund
   geht - dann ist der Stand des Tages fertig: wer geuebt hat, bekommt
   heute nichts mehr.

   Welcher Abend was bekommt:
     heute, noch nicht geuebt, Serie laeuft   -> Serienwarnung um 20 Uhr
     morgen, wenn heute geuebt                -> Serienwarnung um 20 Uhr
     sonst (bis sechs Tage voraus)            -> Erinnerung um 19 Uhr
   Die Serienwarnung faellt weg, solange ein Serienschutz im Vorrat liegt -
   dann reisst die Serie ja nicht. Statt ihrer kommt die Erinnerung.
   Nach sieben Tagen ohne die App hoert es auf. Wer so lange nicht kam,
   will nicht jeden Abend daran erinnert werden. Beides ist meine Wahl,
   nicht Ajdins - steht im Bericht vom 01.10.2026.

   Ganz Schluss ist danach nicht mehr (10.10.2026, Pruefung vom
   07.10.2026): Vierzehn Tage nach dem letzten Planen, also nach der
   letzten Benutzung der App, kommt genau EINE leise Rueckhol-Nachricht
   um 19 Uhr. Davor liegt eine Woche ganz ohne Nachricht, und gelernt
   wurde dann mindestens vierzehn Tage nicht. Danach kommt nichts mehr,
   auch nach dem naechsten Oeffnen nicht, bis wieder gelernt wurde -
   mehr als ein freundliches Anstupsen nach zwei Wochen waere Druck. Sie
   haengt am Schalter "Taegliche Erinnerung".
   Ausserdem haben Erinnerung, Serienwarnung und Leben-Nachricht mehrere
   Texte, die nach dem Kalendertag wechseln: Jeden Abend derselbe Satz
   wird irgendwann nicht mehr gelesen. Die Uhrzeiten bleiben fest (19 und
   20 Uhr, festgelegt am 30.09.2026). Die Pruefung schlug auch eine
   waehlbare Uhrzeit vor; die ist nicht beauftragt. Seit 1.4 haengt der
   Abendtext an der Lage, siehe TEXTE MIT PERSOENLICHKEIT; an den Regeln
   oben aendert das nichts (Ajdin am 13.11.2026: 19 und 20 Uhr bleiben
   fest, hoechstens eine Nachricht am Abend, ohne Namen).

   Die Leben-Nachricht kommt nur, wenn beim Planen alle Leben weg sind.
   Faellt sie in die Nacht (22 bis 8 Uhr), kommt sie um 8 Uhr; faellt sie
   auf einen Abend, an dem ohnehin eine Nachricht kommt, entfaellt sie. */
const BEN_SCHLUESSEL = 'zmaj_benachrichtigung';
const BEN_ERINNERUNG_UM = 19, BEN_SERIE_UM = 20, BEN_TAGE = 7;
const BEN_ID_ABEND = 100, BEN_ID_LEBEN = 200, BEN_KANAL = 'erinnerungen';
/* Rueckhol-Nachricht (10.10.2026). Die Nummer liegt zwischen den Abenden
   (100-113) und den Leben (200), also in dem Bereich, den benPlanen vor
   jedem Planen absagt. Eigener Kanal mit Wichtigkeit 2 (IMPORTANCE_LOW,
   laut developer.android.com ohne Ton), denn sie soll leise sein. Ein
   neuer Kanal statt des alten, weil Android die Wichtigkeit eines Kanals
   nach dem Anlegen nicht mehr aendern laesst. Vor Android 8 (minSdk 24
   ist Android 7) gibt es keine Kanaele, dort kommt sie wie die anderen. */
const BEN_PAUSE_TAGE = 14, BEN_ID_RUECKHOL = 150, BEN_KANAL_LEISE = 'rueckhol';
const benPlugin = () => (window.Capacitor && window.Capacitor.Plugins
                         && window.Capacitor.Plugins.LocalNotifications) || null;
let benDran = false;
function benStand(){
  let s = null;
  try{ s = JSON.parse(localStorage.getItem(BEN_SCHLUESSEL) || 'null'); }catch(e){}
  return Object.assign({gefragt:false, erinnerung:false, serie:false, leben:false}, s || {});
}
function benMerken(s){
  try{ localStorage.setItem(BEN_SCHLUESSEL, JSON.stringify(s)); }catch(e){}
}
async function benErlaubt(fragen){
  const L = benPlugin();
  if(!L) return false;
  try{
    let p = await L.checkPermissions();
    if(p.display !== 'granted' && fragen) p = await L.requestPermissions();
    return p.display === 'granted';
  }catch(e){ return false; }
}
function benZeit(tag, stunde){ const d = new Date(tag + 'T12:00:00'); d.setHours(stunde, 0, 0, 0); return d; }
/* Was die naechsten Abende bringen - ohne Plugin, damit es sich auch im
   Browser nachpruefen laesst. */
/* Die Nummer einer Abendnachricht haengt am Kalendertag, nicht am Abstand
   zu heute: 14 Nummern im Kreis (100 bis 113). Vorher war es "100 + Tage
   ab heute" - eine behaltene Nachricht von gestern trug dann dieselbe
   Nummer wie ein kommender Abend, und der fiel weg. */
function benTagNr(tag){
  const z = tag.split('-').map(Number);
  return Math.round(Date.UTC(z[0], z[1] - 1, z[2]) / 86400000);
}
function benAbendId(tag){
  return BEN_ID_ABEND + (benTagNr(tag) % 14);
}
/* Welcher Text an welchem Tag: die Tagesnummer modulo der Zahl der
   Fassungen. Kein Zufall - so bringen zwei Abende hintereinander nie
   denselben Satz, und ein zweites Planen am selben Tag waehlt denselben
   Text wie das erste. 10.10.2026 */
function benFassung(tag, fassungen){ return fassungen[benTagNr(tag) % fassungen.length]; }
/* =================== TEXTE MIT PERSOENLICHKEIT ===================
   Version 1.4, Ajdin am 13.11.2026 (11a 12a 13a, Vorlage
   Release/Entscheidungen_2026-11-13/benachrichtigungen.md): Texte mit
   Zmaj-Humor in Gruppen statt der zwoelf braven von vorher. Ohne Namen,
   ohne Uhrzeit im Text, keine Werbung. Am 14.11.2026 hat Ajdin alle 24
   gelesen und sieben gestrichen: A1 ("Raus"), B4 mit einem gelernten Wort
   im Titel ("diese Benachrichtigung ist komisch mach weg", samt Wortliste
   und Platzhalter {wort}) und die ganze Gruppe D mit den Wortwitzen ("Der
   Rest raus"). Es bleiben 17, wortgleich. Welche Gruppe ein Abend
   bekommt, haengt an der Lage an diesem Abend - gerechnet unter der
   Annahme, dass bis dahin nicht gelernt wird; wer lernt, plant ohnehin neu.
     Serienwarnung (20 Uhr)            A2-A5, ab 7 Tagen Serie auch C1 und
                                       (Serie = Rekord) C3. A6 hat Vorrang,
                                       wenn die naechste Lektion eine
                                       Wegmarke (7/30/100/365/1000 Lerntage)
                                       vollmacht.
     gestern gelernt, keine Warnung    C Lob: C2 ab 100 Woertern, C3 bei
       (Schalter aus oder Schutz da)   Rekord, C4, C6 (C1 nicht, der ist ein
                                       20-Uhr-Text). C5 hat Vorrang am Tag
                                       nach 30, 100 oder 365 Tagen.
     2 bis 6 Tage Pause                B1, B2, B3, B5. B3 nur, wenn die
                                       Serie an dem Abend gerissen ist, B5
                                       nur mit einem offenen Level.
     Rueckhol-Nachricht nach 14 Tagen  B6
     alles andere (7 und mehr Tage     B2 und C4; mit einem Lerntag auch B1
       Pause oder nie gelernt)         und B5 (B5 nur mit offenem Level).
   A4 ("{n} Tage am Stueck") kommt erst ab 2 Tagen. Jede Lage hat mindestens
   zwei Texte, die sich abwechseln.
   Gewaehlt wird der Text, der am laengsten nicht kam (s.texte: Schluessel
   -> letzter Abend, eingetragen beim Zustellen in benPlanen); bei
   Gleichstand reihum nach dem Kalendertag. Der Text vom Vorabend ist
   gesperrt - so kommt nie derselbe zweimal hintereinander -, und ein
   zweites Planen am selben Tag waehlt wieder denselben. Kein Zufall.
   Alle Platzhalter werden hier auf dem Geraet gefuellt, nichts verlaesst
   es. Hoechstens eine Zahl je Text, sonst klappt die Mehrzahl nicht. */
const BEN_TEXTE = {
  a2: ['ben.a2_titel', 'ben.a2_text'], a3: ['ben.a3_titel', 'ben.a3_text'],
  a4: ['ben.a4_titel', 'ben.a4_text'], a5: ['ben.a5_titel', 'ben.a5_text'],
  a6: ['ben.a6_titel', 'ben.a6_text'],
  b1: ['ben.b1_titel', 'ben.b1_text'], b2: ['ben.b2_titel', 'ben.b2_text'],
  b3: ['ben.b3_titel', 'ben.b3_text'], b5: ['ben.b5_titel', 'ben.b5_text'],
  b6: ['ben.b6_titel', 'ben.b6_text'],
  c1: ['ben.c1_titel', 'ben.c1_text'], c2: ['ben.c2_titel', 'ben.c2_text'],
  c3: ['ben.c3_titel', 'ben.c3_text'], c4: ['ben.c4_titel', 'ben.c4_text'],
  c5: ['ben.c5_titel', 'ben.c5_text'], c6: ['ben.c6_titel', 'ben.c6_text'],
};
const BEN_FARBTAGE = [30, 100, 365];   // C5: am Tag danach, die Flamme hat die Farbe gewechselt
/* Die Werte eines geplanten Abends. pause: Tage seit dem letzten Lerntag
   (basis, 0 ohne einen). Gerissen ist die Serie an dem Abend, wenn sie es
   jetzt schon ist oder mehr Tage dazwischen fehlen, als Schutz im Vorrat
   liegt.
   Zum Vorrat zaehlt auch ein Schutz, der bis 19 Uhr an dem Abend
   nachwaechst: beim Oeffnen rettet pruefeSchutz() die Serie mit genau dem.
   Vorher zaehlte nur der Schutz von jetzt, und B3 ("Serie weg?") kam fuer
   eine Serie, die gar nicht gerissen war - gefunden in der Pruefung am
   13.11.2026 (Serie 5, kein Schutz, der naechste in 12 Stunden). Wie
   schutzAbends in benPlan(). */
function benWerte(tag, basis){
  const n = streak(), tagNr = benTagNr(tag);
  const pause = basis ? tagNr - benTagNr(basis) : 0;
  let fehlt = 0;
  for(let k = 1; k < pause; k++) if(!frost.has(tagMinus(tag, k))) fehlt++;
  const schutzJetzt = schutzNow();   // gleicht zuerst ab, erst danach stimmt naechsterSchutzIn()
  const rest = naechsterSchutzIn(), bis = benZeit(tag, BEN_ERINNERUNG_UM).getTime() - Date.now();
  const nachwachsen = rest > 0 && rest <= bis ? 1 + Math.floor((bis - rest) / SCHUTZ_MS) : 0;
  const vorrat = Math.min(SCHUTZ_MAX, schutzJetzt + nachwachsen);
  const m = MEILENSTEINE.find(x => x.ziel === days.size + 1 && !gefeiert.has(x.id));
  const offen = CATEGORIES.some(c => !passed.has(c.id)) ? CATEGORIES[firstOpen()] : null;
  return {n, pause, rekord, ziel: m ? m.ziel : 0,
          woerter: Math.floor(ohneZa(known) / 100) * 100,   // abgerundet auf 100
          gerissen: pause >= 2 && (n === 0 || fehlt > vorrat),
          level: offen ? offen.label : ''};
}
/* Welche Texte an einem Abend in Frage kommen: vorrang vor allen anderen,
   sonst einer aus pool. */
function benGruppe(art, w){
  if(art === 'serie'){
    const pool = ['a2', 'a3'].concat(w.n >= 2 ? ['a4'] : [], ['a5']);
    if(w.n >= 7){ pool.push('c1'); if(w.n >= w.rekord) pool.push('c3'); }
    return {vorrang: w.ziel ? ['a6'] : [], pool};
  }
  if(w.pause === 1){
    const pool = (w.woerter >= 100 ? ['c2'] : [])
      .concat(w.n >= 7 && w.n >= w.rekord ? ['c3'] : [], ['c4', 'c6']);
    return {vorrang: BEN_FARBTAGE.includes(w.n) ? ['c5'] : [], pool};
  }
  if(w.pause >= 2 && w.pause <= 6){
    const pool = ['b1', 'b2'];
    if(w.gerissen) pool.push('b3');
    if(w.level) pool.push('b5');
    return {vorrang: [], pool};
  }
  /* Alles andere: 7 und mehr Tage Pause oder noch nie gelernt - bis zum
     14.11.2026 kamen hier die Wortwitze. Mit einem Lerntag (pause > 0)
     B1, B2 und mit offenem Level B5, ohne einen nur B2; dazu immer C4. */
  const pool = w.pause > 0 ? ['b1', 'b2'].concat(w.level ? ['b5'] : []) : ['b2'];
  pool.push('c4');
  return {vorrang: [], pool};
}
/* zuletzt: Schluessel -> Tag, an dem er zuletzt kam (auch die Abende davor
   in diesem Plan). */
function benWahl(gruppe, tag, zuletzt){
  const gestern = tagMinus(tag, 1);
  const v = gruppe.vorrang.find(k => zuletzt[k] !== gestern);
  if(v) return v;
  let liste = gruppe.pool.filter(k => zuletzt[k] !== gestern);
  if(!liste.length) liste = gruppe.pool;
  const start = benTagNr(tag) % liste.length;
  let beste = null;
  for(let i = 0; i < liste.length; i++){
    const k = liste[(start + i) % liste.length];
    if(beste === null || (zuletzt[k] || '') < (zuletzt[beste] || '')) beste = k;
  }
  return beste;
}
/* Titel und Text, fertig gefuellt. Die Mehrzahl richtet sich nach der Zahl,
   die im Text steht; nur {n} kann 1 sein, die anderen sind immer groesser
   (Pause ab 2, Woerter ab 100, Rekord ab 7, Wegmarke ab 7). */
function benTexte(k, w){
  const farbe = {blau: t('ben.farbe_blau'), lila: t('ben.farbe_lila'), gold: t('ben.farbe_gold')}[flammeStufe(w.n)] || '';
  const vars = {n: w.n, ziel: w.ziel, rekord: w.rekord, woerter: w.woerter, tage: w.pause,
                level: w.level, farbe};
  const zahl = {a6: w.ziel, b1: w.pause, b6: w.woerter, c2: w.woerter, c3: w.rekord}[k] || w.n;
  const text = (k === 'b6' && w.woerter < 100) ? 'ben.b6_text_wenig' : BEN_TEXTE[k][1];
  return [tp(BEN_TEXTE[k][0], zahl, vars), tp(text, zahl, vars)];
}
function benPlan(){
  const s = benStand(), jetzt = Date.now(), heute = today(), plan = [];
  const heuteGeuebt = days.has(heute);
  /* Der letzte Lerntag ('' ohne einen). Kam fuer ihn die
     Rueckhol-Nachricht schon (s.rueckholFuer, gesetzt in benPlanen), bleibt
     es still - keine Abendnachricht, keine zweite Rueckhol-Nachricht -,
     bis wieder gelernt wird. Siehe BENACHRICHTIGUNGEN. 10.10.2026 */
  let basis = '';
  days.forEach(k => { if(k > basis) basis = k; });
  const ruhe = s.rueckholFuer === basis;
  const schutzDa = schutzNow() > 0;
  const schutzRest = naechsterSchutzIn();
  const gesendet = new Set(s.gesendet || []);
  const abende = new Set();
  /* Welcher Text wann zuletzt kam, dazu die Abende dieses Plans - siehe
     TEXTE MIT PERSOENLICHKEIT. */
  const zuletzt = Object.assign({}, s.texte || {});
  for(let d = 0; d < BEN_TAGE && !ruhe; d++){
    const tag = tagMinus(heute, -d);
    if(d === 0 && heuteGeuebt) continue;
    /* Kam heute schon eine Abendnachricht, kommt keine zweite - auch dann
       nicht, wenn die Art inzwischen wechselt (etwa weil beim Oeffnen der
       letzte Serienschutz verbraucht wurde und jetzt die Warnung um 20 Uhr
       faellig waere). Gefunden in der Gegenpruefung am 01.10.2026. */
    if(d === 0 && gesendet.has(tag)){ abende.add(tag); continue; }
    const serieLebt = (d === 0 && streak() > 0) || (d === 1 && heuteGeuebt);
    /* Ein Schutz, der bis 20 Uhr nachwaechst, rettet die Serie genauso. */
    const schutzAbends = schutzDa ||
      (schutzRest > 0 && jetzt + schutzRest <= benZeit(tag, BEN_SERIE_UM).getTime());
    let art = null, um = 0;
    if(s.serie && serieLebt && !schutzAbends){ art = 'serie'; um = BEN_SERIE_UM; }
    else if(s.erinnerung){ art = 'erinnerung'; um = BEN_ERINNERUNG_UM; }
    if(!art) continue;
    const wann = benZeit(tag, um);
    if(wann.getTime() <= jetzt + 60000) continue;
    abende.add(tag);
    /* Der Text nach der Lage an diesem Abend (1.4, 13.11.2026). */
    const w = benWerte(tag, basis);
    const key = benWahl(benGruppe(art, w), tag, zuletzt);
    zuletzt[key] = tag;
    const [titel, text] = benTexte(key, w);
    plan.push({id: benAbendId(tag), art, wann, titel, text, key});
  }
  /* Die Rueckhol-Nachricht: vierzehn Tage ab heute. Die Abende oben
     reichen bis heute + 6, dazwischen liegt eine Woche ohne Nachricht.
     Jedes neue Planen schiebt sie nach hinten - sie kommt nur, wenn die
     App so lange zu blieb. basis sagt, zu welchem Lerntag sie gehoert;
     benPlanen traegt das nach dem Zustellen in s.rueckholFuer ein.
     10.10.2026
     Nur mit einem Lerntag (Pruefbericht 1.4, V6, 14.11.2026): Ohne ihn -
     frisch, nach dem Abmelden oder nach "Konto loeschen" - gibt es nichts
     zurueckzuholen, und "Deine Woerter sind alle noch da" stimmte nicht. */
  if(s.erinnerung && !ruhe && basis){
    /* Seit 1.4 der Text B6, mit der Zahl der Woerter (13.11.2026). */
    const zurueck = tagMinus(heute, -BEN_PAUSE_TAGE);
    const [titel, text] = benTexte('b6', benWerte(zurueck, basis));
    plan.push({id: BEN_ID_RUECKHOL, art: 'rueckhol', basis, key: 'b6',
               wann: benZeit(zurueck, BEN_ERINNERUNG_UM), titel, text});
  }
  if(s.leben && !unlimited()){
    syncLives();
    if(lives.anzahl === 0 && lives.zeit){
      const wann = new Date(lives.zeit + LEBEN_MAX * REFILL_MS);
      const h = wann.getHours();
      if(h >= 22 || h < 8){
        if(h >= 22) wann.setDate(wann.getDate() + 1);
        wann.setHours(8, 0, 0, 0);
      }
      const abend = h >= 18 && h < 22 && abende.has(dayKey(wann));
      if(!abend && wann.getTime() > jetzt + 60000)
        plan.push({id: BEN_ID_LEBEN, art: 'leben', wann, titel: t('ben.leben_titel'),
                   text: benFassung(dayKey(wann), [t('ben.leben_text'), t('ben.leben_text_2'), t('ben.leben_text_3')])});
    }
  }
  return plan;
}
let benLaeuft = null;
/* Nach "Konto loeschen" (Pruefbericht 1.4, V6, 14.11.2026). Bis dahin
   blieben die geplanten Nachrichten stehen, und der naechste Start plante
   auf dem leeren Stand neu: sieben Abende und "Ima li te? Deine 200 Woerter
   sind alle noch da." - obwohl die Datenschutzerklaerung (Abschnitt 10)
   sagt, dass der Lernstand sofort geloescht ist. Jetzt sind alle drei
   Schalter aus und alles in unserem Nummernbereich ist abgesagt, auch was
   benPlanen() fuer heute behalten wuerde (s.geplant leer). Danach plant
   benPlanen() wie immer - mit den Schaltern aus also nichts. Wer wieder
   Nachrichten will, schaltet sie in den Einstellungen ein.
   Nur hier, nicht beim Abmelden: dort bleiben die Erinnerungen mit Absicht,
   sie holen zur Anmeldung zurueck. Erst einen laufenden Plan abwarten,
   sonst schriebe er die alten Schalter mit seinem Stand zurueck. */
async function benAllesAus(){
  if(benLaeuft) try{ await benLaeuft; }catch(e){}
  const s = benStand();
  s.erinnerung = false; s.serie = false; s.leben = false; s.geplant = [];
  benMerken(s);
  const L = benPlugin();
  if(L){
    const weg = [];
    for(let id = BEN_ID_ABEND; id < BEN_ID_LEBEN + 100; id++) weg.push({id});
    try{ await L.cancel({notifications: weg}); }catch(e){}
  }
  await benPlanen();
}
async function benPlanen(){
  const L = benPlugin();
  if(!L || !standGeladen) return;
  /* Nicht zweimal gleichzeitig: sonst loescht der zweite Lauf, was der
     erste gerade angelegt hat, und plant danach doppelt. */
  if(benLaeuft) return benLaeuft;
  benLaeuft = (async ()=>{
    /* Was beim letzten Planen fuer HEUTE schon faellig war, ist gekommen
       oder kommt gleich - Android stellt ungenau zu, eine 19-Uhr-Nachricht
       kann um 19:40 noch ausstehen. Die wird nicht abgesagt, und der Abend
       gilt als belegt. Ausnahme: heute schon geuebt. Dann darf sie weg,
       "du hast heute noch nicht geuebt" nach dem Ueben waere falsch.
       Aeltere Eintraege sind laengst zugestellt; sie zu behalten liesse
       ihre Nummer mit einem kommenden Abend zusammenstossen. Die
       Leben-Nachricht wird immer neu geplant. Zweite Gegenpruefung am
       01.10.2026. */
    const jetzt = Date.now(), s = benStand(), heute = today();
    const heuteGeuebt = days.has(heute);
    const gesendet = new Set(s.gesendet || []);
    const behalten = new Set();
    (s.geplant || []).forEach(p => {
      if(!p.abend || p.at > jetzt) return;
      gesendet.add(p.tag);
      /* Die Rueckhol-Nachricht ist gekommen: Fuer diesen Lerntag ist
         Schluss, bis wieder gelernt wird. 10.10.2026 */
      if(p.art === 'rueckhol') s.rueckholFuer = p.basis || '';
      /* Welcher Text an dem Abend kam, fuer benWahl() (1.4, 13.11.2026).
         Aeltere Plaene ohne key zaehlen nicht mit. */
      else if(p.key && BEN_TEXTE[p.key]){
        s.texte = s.texte || {};
        if((s.texte[p.key] || '') < p.tag) s.texte[p.key] = p.tag;
      }
      if(p.tag === heute && !heuteGeuebt) behalten.add(p.id);
    });
    s.gesendet = [...gesendet].sort().slice(-10);
    try{
      const alt = await L.getPending();
      const weg = ((alt && alt.notifications) || [])
        .filter(n => n.id >= BEN_ID_ABEND && n.id < BEN_ID_LEBEN + 100 && !behalten.has(n.id))
        .map(n => ({id: n.id}));
      if(weg.length) await L.cancel({notifications: weg});
    }catch(e){}
    /* In s.geplant steht danach nur, was wirklich noch aussteht. Was gerade
       abgesagt wurde, darf spaeter nicht als zugestellt zaehlen - auch dann
       nicht, wenn gleich die Erlaubnis fehlt oder schedule() scheitert. */
    s.geplant = (s.geplant || []).filter(p => behalten.has(p.id));
    benMerken(s);
    if(!await benErlaubt(false)) return;
    const plan = benPlan().filter(p => !behalten.has(p.id));
    if(!plan.length) return;
    try{ await L.createChannel({id: BEN_KANAL, name: t('ben.kanal'), importance: 3, visibility: 1}); }catch(e){}
    if(plan.some(p => p.art === 'rueckhol')){
      try{ await L.createChannel({id: BEN_KANAL_LEISE, name: t('ben.kanal_leise'), importance: 2, visibility: 1}); }catch(e){}
    }
    /* Genau, wo es ohne Rueckfrage geht, sonst ungenau. Unter Android 12
       meldet das Plugin immer "granted" - dort kommen die Nachrichten
       punktgenau wie vorher; ungenau darf ein Wecker dort bis zu 75 % der
       Vorlaufzeit spaeter kommen, die Serienwarnung also nach Mitternacht.
       Ab Android 12 fehlt die Erlaubnis (im Manifest entfernt), dann
       "denied" und ungenau, hoechstens etwa eine Stunde spaeter. Mit
       isExactNotification:true und fehlender Erlaubnis oeffnete das Plugin
       ab Fassung 8.3 selbst Androids Seite "Wecker und Erinnerungen" -
       am S21 so passiert am 01.10.2026. */
    let genau = false;
    try{ const r = await L.checkExactNotificationSetting(); genau = !!r && r.exact_alarm === 'granted'; }catch(e){}
    /* largeBody: derselbe Text noch einmal, damit Android ihn aufgeklappt
       ganz zeigt. Nur mit body setzt das Plugin (8.3.1) keinen Stil, dann
       zeigt Android aufgeklappt hoechstens zwei Zeilen und vor Android 12
       laesst sich die Nachricht gar nicht aufklappen - die Texte von 1.4
       sind bis 80 Zeichen lang. Mit largeBody wird es BigTextStyle,
       zugeklappt bleibt body. iOS kennt largeBody nicht und zeigt body.
       Pruefung am 13.11.2026. */
    try{
      await L.schedule({notifications: plan.map(p => ({
        id: p.id, title: p.titel, body: p.text, largeBody: p.text,
        channelId: p.art === 'rueckhol' ? BEN_KANAL_LEISE : BEN_KANAL,
        isExactNotification: genau,
        schedule: {at: p.wann, allowWhileIdle: true}, extra: {art: p.art}}))});
      s.geplant = s.geplant.concat(plan.map(p => ({id: p.id, at: p.wann.getTime(), tag: dayKey(p.wann), abend: p.art !== 'leben',
                                                   art: p.art, basis: p.basis, key: p.key})));
      benMerken(s);
    }catch(e){}
  })();
  try{ await benLaeuft; } finally { benLaeuft = null; }
}
/* Die Frage nach der ersten Lektion. Erst unsere eigene Karte, dann
   Androids Abfrage - wer bei Android einmal Nein sagt, bekommt die Abfrage
   nie wieder zu sehen, deshalb nur, wenn jemand vorher Ja gesagt hat. */
function zeigeBenFrage(){
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage';
  kasten.innerHTML =
    '<div class="nachfragebox einstbox">' +
      '<div class="celebrate"><div class="zmaj idle">' + zmaj('happy') + '</div></div>' +
      '<h3></h3><div class="txt"></div>' +
      '<button class="btn know" id="bnJa"></button>' +
      '<button class="btn ghost" id="bnNein"></button>' +
    '</div>';
  kasten.querySelector('h3').textContent = t('ben.frage_titel');
  kasten.querySelector('.txt').textContent = t('ben.frage_text');
  kasten.querySelector('#bnJa').textContent = t('ben.ja');
  kasten.querySelector('#bnNein').textContent = t('bew.nein');
  document.body.appendChild(kasten);
  const zu = ()=>{ kasten.remove(); if(frageSchliessen === zu) frageSchliessen = null; };
  frageSchliessen = zu;
  kasten.addEventListener('click', e=>{ if(e.target === kasten) zu(); });
  kasten.querySelector('#bnJa').addEventListener('click', async ()=>{
    zu();
    const ja = await benErlaubt(true);
    benMerken({gefragt:true, erinnerung:ja, serie:ja, leben:ja});
    if(ja) benPlanen();
  });
  kasten.querySelector('#bnNein').addEventListener('click', ()=>{
    zu(); benMerken(Object.assign(benStand(), {gefragt:true}));
  });
}
/* Die drei Schalter in den Einstellungen. Einschalten fragt Android, wenn
   die Erlaubnis noch fehlt. Sagt Android Nein, bleibt der Schalter aus und
   darunter steht, wo man es aendert. */
function benSchalterZeigen(){
  const box = $('setBenBox');
  if(!box) return;
  box.style.display = benPlugin() ? '' : 'none';
  const s = benStand();
  $('swBenErinnerung').setAttribute('aria-checked', s.erinnerung);
  $('swBenSerie').setAttribute('aria-checked', s.serie);
  $('swBenLeben').setAttribute('aria-checked', s.leben);
  $('benNote').textContent = '';
}
[['swBenErinnerung', 'erinnerung'], ['swBenSerie', 'serie'], ['swBenLeben', 'leben']].forEach(([id, feld]) => {
  const k = $(id);
  if(!k) return;
  k.addEventListener('click', async ()=>{
    const s = benStand();
    const an = !s[feld];
    if(an && !await benErlaubt(true)){
      $('benNote').textContent = t('set.ben_gesperrt');
      k.setAttribute('aria-checked', 'false');
      return;
    }
    s[feld] = an; s.gefragt = true;
    /* Wer die Erinnerung selbst wieder einschaltet, will sie - auch wenn
       die Rueckhol-Nachricht schon kam. 10.10.2026 */
    if(an && feld === 'erinnerung'){
      delete s.rueckholFuer;
      s.geplant = (s.geplant || []).filter(p => p.art !== 'rueckhol');
    }
    benMerken(s);
    k.setAttribute('aria-checked', an);
    $('benNote').textContent = '';
    benPlanen();
  });
});

/* Abstand der Bewertungskarte zur letzten Anzeige. Pruefung vom
   07.10.2026: der Ergebnisschirm des Level-Tests loest auch die Anzeige
   aus, und die Karte kam 600 ms nach dem Verlassen - bei Gratisnutzern
   fast immer direkt nach einer weggedrueckten Anzeige, und „Nein danke“
   sperrt sie fuer immer. Ging die letzte Anzeige vor weniger als dieser
   Frist zu Ende, bleibt die Karte vorgemerkt und kommt bei der naechsten
   Rueckkehr zum Lernpfad. bewertungDran lebt nur im Arbeitsspeicher:
   wer die App vorher schliesst, bekommt sie erst nach dem naechsten
   bestandenen Level-Test. Die Regel „nach bestandenem Level-Test“ und
   die Grenzen in bewertungFaellig() bleiben, wie sie sind. */
const BEWERTUNG_NACH_ANZEIGE_MS = 60 * 1000;
/* Karten, die auf das Verlassen eines Ergebnisschirms warten. Eine nach
   der anderen, nie zwei uebereinander, und nie ueber der Einwilligung,
   einer Anzeige oder einer Wegmarke. Was jetzt nicht passt, bleibt dran. */
function kartenNachreichen(){
  if(!benDran && !bewertungDran) return;
  /* anzeigeLaeuft seit dem 06.10.2026: die Karte kommt jetzt auch auf dem
     Schirm ohne Leben, und dort steht der Knopf fuer das Video. Eine
     AdMob-Anzeige hat kein Element im Dokument, das unten auffiele. */
  const frei = ()=> !frageSchliessen && !wegmarkeLaeuft && !Ex_laeuft() && !anzeigeLaeuft &&
                    !sichtbar('profileView') &&      // nie ueber der Anmeldung, 28.10.2026
                    !document.querySelector('.nachfrage, .einwilligung, .werbung');
  if(!frei()) return;
  setTimeout(()=>{
    if(!frei()) return;
    if(benDran){ benDran = false; zeigeBenFrage(); return; }
    if(bewertungDran && Date.now() - anzeigeZuletzt >= BEWERTUNG_NACH_ANZEIGE_MS){
      bewertungDran = false;
      if(IST_IOS) appleBewertung(); else zeigeBewertung();
    }
  }, 600);
}
/* Seit 13.11.2026 auch der Sprung-Test, der in derselben Ansicht laeuft */
const Ex_laeuft = () => !!(((Ex && !Ex.fertig) || (Sx && !Sx.fertig)) && sichtbar('einstufungView'));

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
