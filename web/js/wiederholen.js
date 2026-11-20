/* =================== WIEDERHOLEN ===================
   Der Sammeltopf fuer falsch Beantwortetes - der zweite Wunsch der Tester
   vom 24.09.2026: gezielt wiederholen, ohne sich durch Gekonntes zu
   klicken. Festgelegt von Ajdin am 30.09.2026: ein eigener Reiter, Fehler
   aus Lektionen und Level-Tests, zehn Aufgaben je Runde, raus nach zweimal
   hintereinander richtig, und eine Runde zaehlt wie eine Lektion - Leben,
   Serie, Tagesaufgaben, Muenzen. Fuer alle, auch ohne Vollversion.

   Gemerkt wird nur ein Schluessel, nie die Aufgabe selbst. Die Texte sind
   je Sprache verschieden, die Schluessel nicht:
     w:<Wort-Kennung>             das Wort, wie in known
     s:<Level>|<bosnischer Satz>  ein Lueckensatz
     k:<Level>|<bosnischer Satz>  ein Satz aus Kacheln (seit 13.10.2026)
                                  Bei s: und k: immer der Satz aus vokabeln.py,
                                  auch wenn er mit einer anderen Zahl kam
                                  (task.v, 25.10.2026). Umbenannte Saetze:
                                  SAETZE_UMBENANNT.
     g:<Level>|<Nummer>           eine Grammatikaufgabe. Die Nummer statt
                                  der Loesung, weil sechs Loesungen mit
                                  uebersetzt werden ("weiblich (ona)").
   Dazu die Aufgabenart, in der es schiefging, und wie oft es seitdem
   hintereinander richtig war.

   Eine richtige Antwort direkt nach dem Fehler - die Wiederholung am Ende
   derselben Lektion - zaehlt nicht: da stand die Loesung eben noch auf dem
   Bildschirm. */
const TOPF_RUNDE = 10, TOPF_RAUS = 2, TOPF_MAX = 300;
function topfSchluessel(task){
  if(!task) return '';
  if(task.typ === 'gap' && task.s) return 's:' + task.s.kat + '|' + task.s.text;
  if(task.typ === 'kacheln' && task.s) return 'k:' + task.s.kat + '|' + task.s.bs;
  if(task.typ === 'gram' && task.g && task.g._lv) return 'g:' + task.g._lv + '|' + task.g._nr;
  /* Beim Zahnarzt: kein Schluessel heisst kein Fehler-Topf und kein Stern. */
  if(task.w && task.w.id) return istZa(task.w.id) ? '' : 'w:' + task.w.id;
  return '';
}
function topfMerken(task, ok){
  const k = topfSchluessel(task);
  if(!k) return;
  const e = topf[k];
  if(ok){
    if(!e || task.retry) return;
    e.n = (e.n || 0) + 1;
    if(e.n >= TOPF_RAUS) delete topf[k];
    return;
  }
  topf[k] = {typ: task.typ, n: 0, z: Date.now()};
  /* Deckel, damit der Lernstand nicht ohne Ende waechst. Es fallen die
     aeltesten Fehler weg. */
  const alle = Object.keys(topf);
  if(alle.length > TOPF_MAX){
    alle.sort((a, b) => (topf[a].z || 0) - (topf[b].z || 0))
        .slice(0, alle.length - TOPF_MAX).forEach(x => { delete topf[x]; });
  }
}
let _wortNachId = null;
function wortNachId(id){
  if(!_wortNachId){
    _wortNachId = new Map();
    CATEGORIES.forEach(c => c.words.forEach(w => { if(!_wortNachId.has(w.id)) _wortNachId.set(w.id, {w, c}); }));
  }
  return _wortNachId.get(id) || null;
}
/* Aus dem Schluessel wieder eine Aufgabe. null, wenn es den Inhalt nicht
   mehr gibt - dann fliegt der Eintrag raus. */
function topfAufgabe(k, e){
  const art = k.slice(0, 2), rest = k.slice(2);
  if(art === 'w:'){
    const f = wortNachId(rest);
    if(!f) return null;
    let typ = e.typ;
    if(typ === 'listen' && !canListen) typ = 'mc';
    if(typ === 'type' && !typable(f.w)) typ = 'mcrev';
    if(['mc', 'mcrev', 'type', 'listen'].indexOf(typ) < 0) typ = 'mcrev';
    return {typ, w: f.w, pool: f.c.words, rep: f.c.label};
  }
  if(art === 's:'){
    const s = SENTENCES.find(x => 's:' + x.kat + '|' + x.text === k);
    if(!s) return null;
    const c = byId(s.kat);
    return {typ:'gap', s, rep: c ? c.label : ''};
  }
  /* Ohne diesen Zweig raeumte topfAufraeumen() jeden falsch gelegten Satz
     gleich wieder weg - er fuehrte ja zu keiner Aufgabe. */
  if(art === 'k:'){
    const s = SATZBAU.find(x => 'k:' + x.kat + '|' + x.bs === k);
    if(!s) return null;
    const c = byId(s.kat);
    return {typ:'kacheln', s, rep: c ? c.label : ''};
  }
  if(art === 'g:'){
    const teile = rest.split('|');
    const g = ((GRAMMAR[teile[0]] || {}).uebungen || [])[Number(teile[1])];
    if(!g) return null;
    const c = byId(teile[0]);
    return {typ:'gram', g, rep: c ? c.label : ''};
  }
  return null;
}
/* Umbenannte Woerter im Fehler-Topf auf ihre neue Kennung ziehen, nach
   derselben Regel wie sternUmschreiben(): UMBENANNT, sonst das bosnische
   Wort, wenn genau ein Wort es traegt. Anders als dort faellt hier nichts
   weg - was zu keiner Aufgabe mehr fuehrt, raeumt wie bisher
   topfAufraeumen() ab. Treffen alter und neuer Eintrag zusammen, gilt der
   juengere Fehler: topfMerken() setzt bei jedem Fehler neu auf n = 0.
   Ueber eine Map und Object.fromEntries wie in standUebernehmen(), damit
   ein Schluessel "__proto__" aus einer Sicherung nichts verbiegt.
   Gibt zurueck, ob sich etwas geaendert hat. 22.10.2026. */
function topfUmschreiben(nachWort){
  if(!CATEGORIES.length) return false;
  const neu = new Map();
  let geaendert = false;
  Object.keys(topf).forEach(k => {
    let ziel = k;
    if(k.slice(0, 2) === 'w:' && !wortNachId(k.slice(2))){
      const id = k.slice(2);
      const kand = (UMBENANNT[id] && wortNachId(UMBENANNT[id])) ? [UMBENANNT[id]]
                 : ((nachWort && nachWort.get(id.slice(id.lastIndexOf(':') + 1))) || []);
      if(kand.length === 1){ ziel = 'w:' + kand[0]; geaendert = true; }
    }
    else if(satzUmbenannt(k)){ ziel = SAETZE_UMBENANNT[k]; geaendert = true; }   // 25.10.2026
    const e = topf[k], da = neu.get(ziel);
    neu.set(ziel, (da && (da.z || 0) >= (e.z || 0)) ? da : e);
  });
  if(geaendert) topf = Object.fromEntries(neu);
  return geaendert;
}
function topfAufraeumen(){
  if(!CATEGORIES.length) return;
  let weg = false;
  Object.keys(topf).forEach(k => { if(!topfAufgabe(k, topf[k])){ delete topf[k]; weg = true; } });
  if(weg) saveProgress();
}
const topfAnzahl = () => Object.keys(topf).length;
/* Die aeltesten zuerst - was einmal richtig war, steht damit bald wieder
   an, und frisch Falsches bekommt etwas Abstand.
   Steht derselbe Satz als Luecke (s:) und als Kacheln (k:) im Topf, kommt
   in eine Runde nur die Luecke - wie in buildLesson(), sonst verraet die
   eine Aufgabe die andere. Die Kacheln bleiben im Topf und kommen in einer
   spaeteren Runde. Review vom 14.10.2026. */
function topfRunde(){
  return rundeAus(Object.keys(topf).map(k => ({k, e: topf[k]}))
    .sort((a, b) => (a.e.z || 0) - (b.e.z || 0))
    .map(x => topfAufgabe(x.k, x.e)).filter(Boolean));
}
/* Aus einer schon sortierten Liste von Aufgaben eine Runde: die ersten
   TOPF_RUNDE, ohne Luecke und Kacheln desselben Satzes, gemischt. Seit
   19.10.2026 ein eigenes Stueck, weil die Markiert-Runde (sternRunde)
   dieselbe Regel braucht. */
function rundeAus(liste){
  const runde = [], belegt = new Set();
  const doppelt = a => a.typ === 'kacheln' && [a.s.bs, ...(a.s.auch || [])].some(x => belegt.has(kachelNorm(x)));
  for(const a of liste){
    if(runde.length >= TOPF_RUNDE) break;
    if(a.typ === 'gap'){
      lueckeFertig(a.s).forEach(x => belegt.add(x));
      // Lag die Kachel-Fassung schon in der Runde (sie war aelter), muss sie raus.
      for(let i = runde.length - 1; i >= 0; i--) if(doppelt(runde[i])) runde.splice(i, 1);
    } else if(doppelt(a)) continue;
    runde.push(a);
  }
  return shuffle(runde);
}
/* Der Reiter Wiederholen entscheidet beim Zeichnen zwischen "Runde
   starten" und "keine Leben". Wachsen Leben nach, waehrend er offen ist,
   zeichnet nur das hier ihn neu - der Takt alle 30 Sekunden und die
   Rueckkehr aus dem Hintergrund rufen es auf. */
function topfNachziehen(){
  /* Nur den Kasten und den Weitermachen-Knopf neu zeichnen, nicht die
     ganze Startseite: showHome() springt an den Seitenanfang, und dieser
     Aufruf kommt nicht vom Nutzer. */
  /* Der Kasten "Markiert" (19.10.2026) hat denselben Knopf und dieselbe
     Sperre ohne Leben, ebenso "Heute faellig" (29.10.2026). */
  if(sichtbar('pfad') && homeMode === 'topf' &&
     ((topfAnzahl() && (livesNow() > 0) !== !!$('topfLos')) ||
      (sternAnzahl() && (livesNow() > 0) !== !!$('sternLos')) ||
      (karteiHeute().length && (livesNow() > 0) !== !!$('karteiLos')))){ renderHero(); showTopf(); }
}
/* Wie showLevelHome() die Lektion wegraeumen. Ohne das blieb #lesson
   sichtbar geschaltet und Lx halb durchgelaufen stehen: lektionDarfWeg()
   hielt die abgebrochene Runde weiter fuer laufend, und Laden, Muenzen und
   Zahnrad fragten auf der Startseite "Lektion abbrechen?". Gefunden in der
   Gegenpruefung am 01.10.2026. */
function topfSeite(){
  homeMode = 'topf';
  $('lesson').style.display = 'none';
  $('lBody').innerHTML = '';
  $('zmajLesson').innerHTML = '';   // wie showLevelHome (19.10.2026)
  showHome();
}
/* Nach dem Ende einer Lektion oder Runde: wohin zurueck. */
function lektionVerlassen(){ if(Lx && Lx.topf) topfSeite(); else showLevelHome(); }
/* Der Reiter Wiederholen: oben der Kasten fuer Fehler, unveraendert,
   darunter seit 19.10.2026 der Kasten "Markiert" (sternKasten) und seit
   29.10.2026 als dritter "Heute faellig" (karteiKasten). */
function showTopf(){
  topfKasten();
  sternKasten();
  karteiKasten();
}
function topfKasten(){
  const box = $('topfBox');
  if(!box) return;
  topfAufraeumen();
  const n = topfAnzahl();
  let html = '<h2>' + esc(t('topf.titel')) + '</h2><div class="desc">' + esc(t('topf.desc')) + '</div>';
  if(!n){
    box.innerHTML = html + '<div class="topfleer">' + esc(t('topf.leer')) + '</div>';
    return;
  }
  html += '<div class="topfzahl">' + n + '</div><div class="topfwort">' + esc(tp('topf.anzahl', n)) + '</div>';
  if(livesNow() > 0){
    html += '<div class="row"><button class="btn know" id="topfLos"></button></div>';
    box.innerHTML = html;
    $('topfLos').textContent = t('topf.start');
    $('topfLos').addEventListener('click', startTopf);
    return;
  }
  /* Ohne Leben dieselben zwei Wege wie in der Levelansicht. */
  const herz = VERBRAUCH.find(w => w.id === 'herz');
  const perVideo = werbungErlaubt(true);
  const perMuenzen = muenzen() >= herz.preis && herz.geht();
  html += '<div class="note">' + esc(t('level.keine_leben', {zeit: fmtMin(nextLifeIn())})) + '</div>' +
    ((perVideo || perMuenzen) ?
      '<div class="row schmal">' +
        (perVideo ? '<button class="btn ghost" id="topfAd"></button>' : '') +
        (perMuenzen ? '<button class="btn ghost" id="topfCoin"></button>' : '') +
      '</div>' : '') +
    vollZeileLeben('topfVoll');
  box.innerHTML = html;
  if($('topfAd')){ $('topfAd').innerHTML = mitSymbol('herz', esc(t('werbung.leben_holen'))); $('topfAd').addEventListener('click', werbungFuerLeben); }
  if($('topfCoin')){
    $('topfCoin').innerHTML = t('lektion.leben_muenzen', symbolTexte({n: herz.preis}));
    $('topfCoin').addEventListener('click', ()=>{ kaufe('herz'); renderLives(); showTopf(); });
  }
  vollZeileHorchen('topfVoll');
}
/* Ohne Argumente: beide haengen auch direkt als Klick-Horcher und als
   onclick des Weitermachen-Knopfs, und der Klick kaeme sonst als Quelle an. */
function startTopf(){ rundeStarten('topf'); }
function startStern(){ rundeStarten('stern'); }
/* quelle: 'topf' (Fehler), 'stern' (Markiert, seit 19.10.2026) oder
   'kartei' (Heute faellig, seit 29.10.2026). Alle Runden laufen gleich -
   Leben, Serie, Tagesaufgaben, Muenzen -, Lx.topf bleibt fuer alle
   gesetzt, Lx.quelle sagt, woher die Aufgaben kommen. */
function rundeStarten(quelle){
  if(anmeldungSperre()) return;
  const aufgaben = (livesNow() > 0) ? (quelle === 'stern' ? sternRunde() : (quelle === 'kartei' ? karteiRunde() : topfRunde())) : [];
  if(!aufgaben.length){ topfSeite(); return; }
  interstitialVorladen();   // eine Runde zaehlt wie eine Lektion, also auch hier
  showView('levelView');
  setzeZurueck(t('btn.zurueck'), topfSeite);
  $('tag').textContent = t(quelle === 'stern' ? 'stern.titel' : (quelle === 'kartei' ? 'kartei.titel' : 'topf.titel'));
  stilleBitte();
  $('levelHome').style.display = 'none'; $('test').style.display = 'none'; $('lesson').style.display = 'block';
  nurHerz(true);
  $('tBody').innerHTML = '';   // siehe showLevelHome: gleiche ids in beiden Feldern
  $('zmajTest').innerHTML = '';   // siehe startLesson
  uhrNeu();
  const zl = $('zmajLesson'); zl.style.display = 'block'; $('lHerz').style.display = ''; zl.innerHTML = zmaj('happy'); setMood(zl, 'happy');
  abbrechenZeigen('lQuit', true);   // das Ergebnis davor blendet ihn aus (S18)
  Lx = {queue: aufgaben, i:0, results:[], right:0, total: aufgaben.length, skipped:0, skipNachFehler:0,
        newWords: new Set(), retried: new Set(), topf: true, quelle: quelle};
  showLessonTask();
  window.scrollTo({top:0, behavior:'smooth'});
}
/* Das Ende einer Runde. Wie lessonEnd(), nur ohne Level: kein Fortschritt
   im Level, kein Test, der frei wird. Dafuer steht da, was noch uebrig ist -
   nach der Markiert-Runde, wie viele markiert sind. "Alles wiederholt"
   gibt es dort nicht: Sterne bleiben, bis man sie wegnimmt. Nach der
   Runde "Heute faellig" (29.10.2026), wie viele heute noch faellig sind. */
function topfEnde(){
  const mitStern = Lx.quelle === 'stern', mitKartei = Lx.quelle === 'kartei';
  stilleBitte(); uhrAus();
  const scored = Lx.results.filter(r => r !== 'intro' && r !== 'skip').length;
  zaehle('lek');
  if(Lx.right === scored && scored > 0 && ohneUebersprungen()) zaehle('per');
  const newDay = markToday();
  const erfolgLob = erfolgZeile();   // Erfolge (13.11.2026): hakt ab, also vor dem Speichern
  saveProgress(); sound('done');
  cloudNachLernen();   // 17.11.2026, siehe dort
  const questLob = questZeilen();
  if(questLob) setTimeout(()=>sound('quest'), 850);
  const rest = mitStern ? sternAnzahl() : (mitKartei ? karteiHeute().length : topfAnzahl());
  $('lBar').innerHTML = ''; $('zmajLesson').style.display = 'none'; $('zmajLesson').innerHTML = ''; $('lHerz').style.display = 'none';   // kleiner Drache abgebaut, nicht nur versteckt - siehe showLevelHome (19.10.2026)
  abbrechenZeigen('lQuit', false);   // S18, siehe abbrechenZeigen
  $('lBody').innerHTML =
    '<div class="ergebnis-titel">' + mitKonfetti(t('topf.fertig')) + '</div><div class="celebrate"><div class="zmaj cheer">' + zmaj('cheer') + '</div></div>' +
    '<div class="result-big">' + Lx.right + ' / ' + scored + '</div>' +
    '<div class="stats"><div class="stat"><b>' + rest + '</b>' + esc(tp(mitStern ? 'stern.rest' : (mitKartei ? 'kartei.rest' : 'topf.rest'), rest)) + '</div>' +
      '<div class="stat"><b>' + flammeHtml() + ' ' + streak() + '</b>' + tp('stat.tage_folge', streak()) + '</div>' +
      '<div class="stat"><b>' + herzSymbol() + ' ' + (unlimited() ? '∞' : livesNow()) + '</b>' + t('stat.leben') + '</div></div>' +
    (rest === 0 && !mitStern ? '<div class="feedback ok">' + esc(t(mitKartei ? 'kartei.alles' : 'topf.alles')) + '</div>' : '') +
    (newDay ? '<div class="feedback ok">' + t('lektion.heute_geuebt') + '</div>' : '') +
    questLob + erfolgLob +
    '<div class="row"><button class="btn ghost" id="lHome"></button>' +
      (rest ? '<button class="btn know" id="lMore"></button>' : '') + '</div>';
  $('lHome').textContent = t('topf.zurueck');
  $('lHome').addEventListener('click', topfSeite);
  if($('lMore')){ $('lMore').textContent = t('topf.noch'); $('lMore').addEventListener('click', mitStern ? startStern : (mitKartei ? startKartei : startTopf)); }
  werbungZaehler++;
  werbungNachDemErgebnis('lesson', ()=> Lx);
}

/* =================== STERN ===================
   Aufgaben selbst zum Wiederholen markieren - festgelegt von Ajdin am
   19.10.2026. Anders als der Fehler-Topf entscheidet hier der Lernende:
   ein Stern bleibt, bis er ihn wieder wegnimmt, auch nach richtigen
   Antworten.
     - Markierbar ist jede Aufgabe mit einer Kennung aus topfSchluessel():
       Woerter (w:), Luecken (s:), Kacheln (k:) und Grammatik (g:). Ein
       Stern je Wort, egal in welcher Aufgabenart markiert. Keine Level.
     - Der Knopf (Variante 1 "Ring" aus dem Entwurf, CSS bei .kastenkopf
       .stern) steht in der Kopfzeile der Lernkarte, rechts neben den
       Fortschrittspunkten, auf einer Linie mit dem Herz - seit dem
       26.10.2026 spaet, Ajdin: "nimm A". Vorher am selben Tag neben dem
       Drachen ("im moment steht es so mitten im nirgendwo"), bis dahin
       unten rechts in der Leiste, gegenueber von "Lektion abbrechen" bzw.
       "Test abbrechen" ("weil er zu schlecht sichtbar war").
       Er steht in der Lektion, in beiden Wiederhol-Runden und im
       Level-Test - nicht in der Einstufung, nicht auf dem Ergebnis und
       nicht auf dem Schirm ohne Leben.
     - stern[kennung] = {z: wann markiert, r: wann zuletzt in der
       Markiert-Runde geuebt, 0 = nie}. Hoechstens STERN_MAX; ist es voll,
       wird nichts still geloescht - der Stern geht nicht an, und eine
       kurze Meldung sagt warum.
     - Die Runde: bis zu TOPF_RUNDE, die am laengsten nicht geuebten
       zuerst (nie geuebte vor allen), sonst die zuerst markierten,
       gemischt. Woerter bekommen ihre Aufgabenart reihum wie in
       buildLesson(), Saetze und Grammatik bleiben, was sie sind. Nach
       jeder Antwort ist die Aufgabe "jetzt geuebt"; der Stern bleibt auch
       bei richtiger Antwort. Falsch kostet ein Leben, kommt am Ende noch
       einmal und landet im Fehler-Topf - wie in jeder Lektion.
     - Der grosse Weitermachen-Knopf oben bleibt, wie er war: er startet
       nie die Markiert-Runde, nur der Knopf im Kasten "Markiert". */
const sternAnzahl = () => Object.keys(stern).length;
const STERN_ART = /^[wskg]:./;
/* Ein Stand von aussen - Geraetespeicher oder Sicherungsdatei - wird nur
   so uebernommen: Kennung ein Text mit gueltigem Anfang und hoechstens 200
   Zeichen, z und r endliche Zahlen ab 0 (r darf fehlen), hoechstens
   STERN_MAX Eintraege, bei mehr die zuletzt markierten. Kein Zeitpunkt
   nach jetzt - wie bei den Lerntagen -, sonst stuende ein Eintrag fuer
   immer hinten in der Runde; er wird auf jetzt gesetzt, nicht verworfen,
   denn eine falsch gestellte Uhr macht den Stern nicht kaputt. */
function sternPruefen(roh){
  if(!roh || typeof roh !== 'object' || Array.isArray(roh)) return {};
  const jetzt = Date.now();
  const zahl = x => (typeof x === 'number' && isFinite(x) && x >= 0) ? Math.min(x, jetzt) : null;
  const liste = [];
  Object.keys(roh).forEach(k => {
    const e = roh[k];
    if(k.length > 200 || !STERN_ART.test(k)) return;
    if(!e || typeof e !== 'object' || Array.isArray(e)) return;
    const z = zahl(e.z), r = e.r === undefined ? 0 : zahl(e.r);
    if(z === null || r === null) return;
    liste.push([k, {z, r}]);
  });
  if(liste.length > STERN_MAX) liste.sort((a, b) => b[1].z - a[1].z);
  return Object.fromEntries(liste.slice(0, STERN_MAX));
}
/* Beim Laden und Einlesen, aus altenFortschrittUmschreiben(): umbenannte
   Woerter auf ihre neue Kennung ziehen (UMBENANNT, sonst ueber das
   bosnische Wort, wenn es genau ein Wort damit gibt - bei "sto" fuer
   hundert und Tisch waere ein Stern auf beiden falsch). Was danach zu
   keiner Aufgabe mehr fuehrt, faellt still weg, wie in topfAufraeumen().
   Gibt zurueck, ob sich etwas geaendert hat. */
function sternUmschreiben(nachWort){
  if(!CATEGORIES.length) return false;
  const neu = {};
  let geaendert = false;
  Object.keys(stern).forEach(k => {
    let ziel = k;
    if(k.slice(0, 2) === 'w:' && !wortNachId(k.slice(2))){
      const id = k.slice(2);
      const kand = (UMBENANNT[id] && wortNachId(UMBENANNT[id])) ? [UMBENANNT[id]]
                 : ((nachWort && nachWort.get(id.slice(id.lastIndexOf(':') + 1))) || []);
      ziel = kand.length === 1 ? 'w:' + kand[0] : '';
    }
    else if(satzUmbenannt(k)) ziel = SAETZE_UMBENANNT[k];   // umbenannte Saetze, 25.10.2026
    if(!ziel || !topfAufgabe(ziel, {typ: 'mc'})){ geaendert = true; return; }
    if(ziel !== k) geaendert = true;
    const e = stern[k], da = neu[ziel];
    neu[ziel] = da ? {z: Math.min(da.z, e.z), r: Math.max(da.r, e.r)} : e;
  });
  if(geaendert) stern = neu;
  return geaendert;
}
/* Der Stern selbst, genau wie im Entwurf: ein regelmaessiger, verrundeter
   Fuenfzack, die viewBox um seinen Flaechenschwerpunkt. Leer ein Umriss
   (Strich 1,9), markiert gold gefuellt (Strich 1,25, Verlauf #sternGold
   unten im Dokument). px: 24 im Knopf (bis 26.10.2026 28), 22 vor dem Titel des Kastens,
   17 im Satz. bild: der Stern im Satz wird vorgelesen ("... auf Stern."),
   die anderen sind Schmuck neben einem Namen. */
const STERN_PFAD = 'M1.41 -9.701L3.403 -5.23A0.643 0.643 0 0 0 3.923 -4.853L8.791 -4.339A1.544 1.544 0 0 1 9.662 -1.657L6.026 1.62A0.643 0.643 0 0 0 5.827 2.231L6.843 7.02A1.544 1.544 0 0 1 4.561 8.677L0.321 6.232A0.643 0.643 0 0 0 -0.321 6.232L-4.561 8.677A1.544 1.544 0 0 1 -6.843 7.02L-5.827 2.231A0.643 0.643 0 0 0 -6.026 1.62L-9.662 -1.657A1.544 1.544 0 0 1 -8.791 -4.339L-3.923 -4.853A0.643 0.643 0 0 0 -3.403 -5.23L-1.41 -9.701A1.544 1.544 0 0 1 1.41 -9.701Z';
function sternSvg(an, px, bild){
  return '<svg class="sternsym' + (an ? ' an' : '') + '" viewBox="-12 -12 24 24" width="' + px + '" height="' + px + '" ' +
    (bild ? 'role="img" aria-label="' + esc(t('stern.symbol')) + '"' : 'aria-hidden="true"') +
    ' focusable="false"><path style="stroke-width:' + (an ? '1.25' : '1.9') + '" d="' + STERN_PFAD + '"/></svg>';
}
/* Den Knopf in der Kopfzeile auf diese Aufgabe stellen. Ohne Aufgabe
   oder ohne Kennung verschwindet er (hidden; sein Platz bleibt, siehe CSS
   bei .kastenkopf .stern). Der Name kommt jedes Mal neu, damit er nach
   einem Sprachwechsel stimmt. */
function sternKnopf(id, task){
  const b = $(id);
  if(!b) return;
  const k = task ? topfSchluessel(task) : '';
  b.dataset.k = k;
  b.hidden = !k;
  b.classList.remove('pop');
  if(!k) return;
  b.setAttribute('aria-label', t('stern.knopf'));
  sternZeigen(b, !!stern[k]);
}
function sternZeigen(b, an){
  b.setAttribute('aria-pressed', an ? 'true' : 'false');
  b.innerHTML = sternSvg(an, 24);
}
function sternUmschalten(e){
  const b = e.currentTarget, k = b.dataset.k;
  if(!k || b.hidden) return;
  if(stern[k]){
    delete stern[k];
    sternZeigen(b, false);
    ansagen(esc(t('stern.weg')));
  } else {
    if(sternAnzahl() >= STERN_MAX){ kurzMeldung(t('stern.voll', {n: STERN_MAX})); return; }
    stern[k] = {z: Date.now(), r: 0};
    sternZeigen(b, true);
    ansagen(esc(t('stern.titel')));
  }
  /* Kurz aufploppen - nur mit Bewegung (Schalter "Animationen" und
     Geraeteeinstellung, wie beim Legen der Kacheln). Ohne Bewegung kaeme
     kein animationend, und .pop bliebe stehen. */
  if(!kachelnRuhig()){ b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop'); }
  buzz(12);
  saveProgress();
}
['lStern', 'tStern'].forEach(id => {
  $(id).addEventListener('click', sternUmschalten);
  $(id).addEventListener('animationend', e => e.currentTarget.classList.remove('pop'));
});
/* Nach jeder beantworteten Aufgabe der Markiert-Runde: jetzt geuebt. Nur,
   solange sie noch markiert ist - wer den Stern unterwegs wegnimmt, will
   sie nicht mehr sehen. */
function sternGeuebt(task){
  const e = stern[topfSchluessel(task)];
  if(e) e.r = Date.now();
}
function sternRunde(){
  const runde = rundeAus(Object.keys(stern).map(k => ({k, e: stern[k]}))
    .sort((a, b) => (a.e.r - b.e.r) || (a.e.z - b.e.z))
    .map(x => topfAufgabe(x.k, {typ: 'mc'})).filter(Boolean));
  /* Wie in buildLesson(), nur ohne Sprechen: das laesst sich ueberspringen,
     und dann zaehlte es nicht als geuebt. Schreiben nur bei tippbaren
     Woertern (artenReihum), Hoeren nur, wenn das Geraet vorlesen kann. */
  const types = ['mc', 'mcrev', 'type']; if(canListen) types.push('listen');
  const pick = artenReihum(types);
  runde.forEach(a => { if(a.w) a.typ = pick(a.w); });
  return runde;
}
/* Der Kasten "Markiert" im Reiter Wiederholen, gebaut genau wie der Kasten
   darueber (topfKasten): dieselben Klassen, dieselbe Zahl, derselbe Knopf.
   Neu ist nur der Stern vor dem Titel - gold, sobald etwas markiert ist.
   Ohne Leben wie der Kasten darueber: kein "Runde starten", dafuer der
   Hinweis und dieselben zwei Wege zu einem Leben. */
function sternKasten(){
  const box = $('sternBox');
  if(!box) return;
  const n = sternAnzahl();
  let html = '<h2 id="sternTitel">' + sternSvg(n > 0, 22) + esc(t('stern.titel')) + '</h2><div class="desc">' + esc(t('stern.desc')) + '</div>';
  if(!n){
    /* {stern} im Text ist der Stern selbst, als Bild mit Namen */
    const teile = t('stern.leer').split('{stern}');
    box.innerHTML = html + '<div class="topfleer">' + esc(teile[0]) +
      (teile.length > 1 ? sternSvg(false, 17, true) + esc(teile.slice(1).join('')) : '') + '</div>';
    return;
  }
  html += '<div class="topfzahl">' + n + '</div><div class="topfwort">' + esc(tp('stern.anzahl', n)) + '</div>';
  if(livesNow() > 0){
    /* aria-describedby: zwei Knoepfe "Runde starten" auf einer Seite - der
       Screenreader sagt dazu, zu welchem Kasten dieser gehoert. */
    html += '<div class="row"><button class="btn know" id="sternLos" aria-describedby="sternTitel"></button></div>';
    box.innerHTML = html;
    $('sternLos').textContent = t('topf.start');
    $('sternLos').addEventListener('click', startStern);
    return;
  }
  const herz = VERBRAUCH.find(w => w.id === 'herz');
  const perVideo = werbungErlaubt(true);
  const perMuenzen = muenzen() >= herz.preis && herz.geht();
  html += '<div class="note">' + esc(t('level.keine_leben', {zeit: fmtMin(nextLifeIn())})) + '</div>' +
    ((perVideo || perMuenzen) ?
      '<div class="row schmal">' +
        (perVideo ? '<button class="btn ghost" id="sternAd"></button>' : '') +
        (perMuenzen ? '<button class="btn ghost" id="sternCoin"></button>' : '') +
      '</div>' : '') +
    vollZeileLeben('sternVoll');
  box.innerHTML = html;
  if($('sternAd')){ $('sternAd').innerHTML = mitSymbol('herz', esc(t('werbung.leben_holen'))); $('sternAd').addEventListener('click', werbungFuerLeben); }
  if($('sternCoin')){
    $('sternCoin').innerHTML = t('lektion.leben_muenzen', symbolTexte({n: herz.preis}));
    $('sternCoin').addEventListener('click', ()=>{ kaufe('herz'); renderLives(); showTopf(); });
  }
  vollZeileHorchen('sternVoll');
}

/* =================== LERNKARTEI ===================
   Zeitgesteuerte Wiederholung alter Woerter - festgelegt von Ajdin am
   28.10.2026: Verfahren A "feste Abstaende", die Lernkartei nach Leitner,
   spaeter vielleicht FSRS (Hintergrund in Release\Wiederholung_Vorschlag.md).
   Bis dahin kam ein gewusstes Wort nur ueber den Fehler-Topf, einen Stern
   oder zufaellig im Level-Test wieder.
     - Jedes gewusste Wort hat eine Stufe 0 bis 6 mit dem Abstand
       KARTEI_ABSTAENDE[stufe]: 1, 3, 7, 14, 30, 90, 180 Tage. Richtig: eine
       Stufe weiter, falsch: zwei zurueck, nie unter die erste. Der naechste
       Termin ist der Uebungstag plus der Abstand der neuen Stufe.
     - Gemerkt wird nur kartei = {tag, n, w}, ein eigenes Feld auf oberster
       Ebene (siehe STAND_FELDER): w[Wort-Kennung] = [stufe, faellig,
       zuletzt geuebt], die Tage als Zahl seit APP_START (karteiTag) statt
       als Datum - so klein wie moeglich, rund 40 Bytes je Wort. zuletzt ist
       0 fuer "noch nie in der Kartei geuebt" (der Umzug, siehe unten).
       tag und n: wie viele faellige Woerter an diesem Tag schon geuebt
       wurden, fuer die Tagesgrenze.
     - Jede Antwort auf ein Wort zaehlt: in der Lektion, im Level-Test und
       in allen drei Runden des Reiters Wiederholen. Nicht in der
       Einstufung, und nicht die Wiederholung einer falschen Antwort am Ende
       derselben Lektion - da stand die Loesung eben noch da (wie beim
       Fehler-Topf). Eine falsche Antwort setzt immer zwei Stufen zurueck.
       Eine richtige hebt die Stufe um eins, auch vor dem Termin - aber
       hoechstens einmal am Tag: Wurde das Wort heute schon geuebt, merkt
       sie sich nur den Uebungstag. Ajdin am 29.10.2026: "wenn man das Wort
       oefter richtig gemacht hat, dann kann man es" - an verschiedenen
       Tagen ja; dreimal am selben Tag ist Pauken und schickte das Wort an
       einem Tag auf zwei Wochen. Eine richtige Antwort holt einen Termin
       nie naeher heran (wichtig fuer die verteilten Umzugswoerter).
     - Ein Wort bekommt seinen Eintrag, sobald es gewusst ist: Stufe 0,
       morgen faellig. Gewusste Woerter ohne Eintrag - beim ersten Start mit
       v110 alle, spaeter die aus einer alten Sicherungsdatei oder von einem
       Geraet mit v109 - bekommen in karteiNachtragen() einen Termin,
       verteilt auf die naechsten Wochen, die aeltesten Level zuerst, nie
       alle am ersten Tag.
     - Hoechstens KARTEI_TAG_MAX faellige Woerter am Tag. Gezaehlt wird jede
       Antwort auf ein faelliges Wort, egal wo. Der Rest bleibt faellig und
       kommt an den naechsten Tagen. Zuerst kommt, was gemessen an seinem
       Abstand am weitesten ueber der Zeit ist (karteiHeute): ein gestern
       gelerntes Wort vor einem, das nach 90 Tagen ein paar Tage zu spaet
       dran ist.
     - Der Kartei-Tag beginnt um KARTEI_TAG_BEGINN Uhr morgens, nicht um
       Mitternacht (karteiTag).
     - Wo sie drankommen: in jeder Lektion auf bis zu KARTEI_IN_LEKTION der
       zehn Wortplaetze (buildLesson), und im Reiter Wiederholen im dritten
       Kasten "Heute faellig" mit eigener Runde (karteiKasten, karteiRunde).
       Leben, Serie, Muenzen und Tagesaufgaben wie in den anderen Runden:
       falsch kostet ein Leben, und das Wort kommt in den Fehler-Topf.
       Weitermachen bleibt, wie es ist. Erst einmal nur Woerter - Saetze und
       Grammatik bleiben, wie sie sind. */
const KARTEI_TAG_MAX = 30, KARTEI_IN_LEKTION = 3;
const KARTEI_LETZTE = KARTEI_ABSTAENDE.length - 1;
/* Der Umzug (karteiNachtragen): Stufe 3 - die Woerter sind schon eine Weile
   gewusst, und bis zum ersten Termin vergehen ohnehin Tage bis Wochen; eine
   richtige Antwort schickt sie damit einen Monat weg, eine falsche auf
   Stufe 1. Verteilt auf etwa KARTEI_UMZUG_TAGE Tage, aber mindestens
   KARTEI_UMZUG_MIN und hoechstens KARTEI_UMZUG_MAX je Tag. Mehr als die
   laengste Stufe weit wird nichts verteilt.
   29.10.2026, Pruefung: zuerst waren es Stufe 2 und bis zu 15 je Tag. Mit
   den Rueckkehrern nach zwei Wochen und nach einem Monat brauchte der
   Umzug allein bald mehr als KARTEI_TAG_MAX Plaetze am Tag. Mit Stufe 3
   kommt ein Umzugswort einmal weniger wieder, mit hoechstens 10 je Tag
   waechst der Rest langsamer. Tagessimulation dieses Codes, alle 1 740
   Woerter gewusst, 85 % richtig, jeden Tag bis zur Grenze geuebt: nach
   vier Monaten rund 90 faellige im Rueckstand statt rund 1 000. Der Umzug
   dauert dabei knapp sechs Monate. */
const KARTEI_UMZUG_STUFE = 3, KARTEI_UMZUG_TAGE = 28, KARTEI_UMZUG_MIN = 3, KARTEI_UMZUG_MAX = 10;
/* Der heutige Kartei-Tag als Zahl: Tage seit APP_START. Ueber den Mittag
   gerechnet wie laengsteSerie(), so stoert die Zeitumstellung nicht. Nie
   unter 0 - auch nicht bei einer Uhr, die vor APP_START steht.
   Er beginnt erst um KARTEI_TAG_BEGINN Uhr (29.10.2026, Pruefung): ab
   Mitternacht gerechnet war ein Wort, das um 23:55 gelernt wurde, um 00:05
   schon faellig, und eine richtige Antwort schickte es zehn Minuten nach
   dem Lernen auf drei Tage. Die erste Wiederholung soll aber gerade nicht
   gleich kommen. Wie "Naechster Tag beginnt um" in Anki, dort ebenfalls
   4 Uhr. Nur fuer die Kartei - Serie, Tagwerk und today() zaehlen weiter
   ab Mitternacht. */
const KARTEI_TAG_BEGINN = 4;
function karteiTag(){
  const d = new Date();
  if(d.getHours() < KARTEI_TAG_BEGINN) d.setDate(d.getDate() - 1);
  const n = Math.round((new Date(dayKey(d) + 'T12:00:00') - new Date(APP_START + 'T12:00:00')) / 86400000);
  return (isFinite(n) && n > 0) ? n : 0;
}
/* Ein Eintrag nur, wenn er wirklich da ist - w.constructor ist keiner. */
const karteiEintrag = (w, id) => Object.prototype.hasOwnProperty.call(w, id) ? w[id] : null;
/* Eine Kartei von aussen - Geraetespeicher, Sicherungsdatei, Cloud - wird
   nur so uebernommen: Kennung ein Text mit hoechstens 200 Zeichen und nie
   "__proto__", je Wort drei ganze Zahlen ab 0 (mehr wird nicht behalten,
   siehe STAND_FELDER), die Stufe hoechstens KARTEI_LETZTE. streng fuer
   alles, was von aussen kommt (sicherungPlausibel, karteiMischen): kein
   Uebungstag und kein Zaehlertag nach heute, kein Termin weiter weg als
   die laengste Stufe - sonst kaeme ein Wort nie wieder dran oder gewaenne
   jeden Abgleich. Im eigenen Geraetespeicher nicht: springt die Uhr zurueck,
   etwa nach leerem Akku, ginge sonst die Kartei verloren (wie die Lerntage
   in standUebernehmen). Kaputtes faellt still heraus. */
function karteiPruefen(roh, streng){
  const objekt = x => (x && typeof x === 'object' && !Array.isArray(x)) ? x : null;
  const ganz = x => (typeof x === 'number' && isFinite(x) && x >= 0) ? Math.floor(x) : null;
  const k = objekt(roh) || {}, rw = objekt(k.w) || {}, heute = karteiTag();
  const w = [];
  Object.keys(rw).forEach(id => {
    const e = rw[id];
    if(id.length > 200 || id === '__proto__' || !Array.isArray(e) || e.length < 3) return;
    let [s, f, l] = e.slice(0, 3).map(ganz);
    if(s === null || f === null || l === null) return;
    s = Math.min(s, KARTEI_LETZTE);
    if(streng){ l = Math.min(l, heute); f = Math.min(f, heute + KARTEI_ABSTAENDE[KARTEI_LETZTE]); }
    w.push([id, [s, f, l]]);
  });
  let tag = ganz(k.tag), n = ganz(k.n);
  if(tag === null || n === null || (streng && tag > heute)){ tag = 0; n = 0; }
  return {tag, n, w: Object.fromEntries(w)};
}
/* Zwei Karteien zusammenfuehren, fuer standZusammenfuehren(): je Wort, was
   zuletzt geuebt wurde, am selben Tag der fruehere Termin, dann die
   kleinere Stufe. Kommutativ und idempotent wie der Rest dort. */
function karteiMischen(a, b){
  const x = karteiPruefen(a, true), y = karteiPruefen(b, true);
  const ids = [...new Set(Object.keys(x.w).concat(Object.keys(y.w)))].sort();
  const w = Object.fromEntries(ids.map(id => {
    const p = karteiEintrag(x.w, id), q = karteiEintrag(y.w, id);
    if(!p || !q) return [id, p || q];
    if(p[2] !== q[2]) return [id, p[2] > q[2] ? p : q];
    if(p[1] !== q[1]) return [id, p[1] < q[1] ? p : q];
    return [id, p[0] <= q[0] ? p : q];
  }));
  const z = x.tag !== y.tag ? (x.tag > y.tag ? x : y) : (x.n >= y.n ? x : y);
  return {tag: z.tag, n: z.n, w};
}
/* Nach jeder beantworteten Wortaufgabe (Lektion, Runden, Level-Test), mit
   dem Ergebnis. Saetze und Grammatik haben kein task.w und zaehlen nicht. */
function karteiAntwort(task, ok){
  const w = task && task.w;
  if(!w || typeof w.id !== 'string' || !known.has(w.id) || !wortNachId(w.id)) return;
  const heute = karteiTag(), e = karteiEintrag(kartei.w, w.id);
  /* Gerade gewusst - auch ueber die Wiederholung am Ende der Lektion,
     wenn die erste Antwort falsch war. */
  if(!e){ kartei.w[w.id] = [0, heute + KARTEI_ABSTAENDE[0], heute]; return; }
  if(task.retry) return;
  const faellig = e[1] <= heute;
  if(faellig){
    if(kartei.tag !== heute){ kartei.tag = heute; kartei.n = 0; }
    kartei.n++;
  }
  if(ok && !faellig && e[2] >= heute){ kartei.w[w.id] = [e[0], e[1], heute]; return; }
  const s = ok ? Math.min(e[0] + 1, KARTEI_LETZTE) : Math.max(e[0] - 2, 0);
  const termin = heute + KARTEI_ABSTAENDE[s];
  kartei.w[w.id] = [s, ok ? Math.max(termin, e[1]) : termin, heute];
}
/* Umbenannte Woerter auf ihre neue Kennung ziehen, nach derselben Regel
   wie topfUmschreiben(): UMBENANNT, sonst das bosnische Wort, wenn genau
   ein Wort es traegt. Treffen alter und neuer Eintrag zusammen, gilt der
   zuletzt geuebte. Was keine neue Kennung findet, bleibt stehen und faellt
   in karteiNachtragen() weg. Gibt zurueck, ob sich etwas geaendert hat. */
function karteiUmschreiben(nachWort){
  if(!CATEGORIES.length) return false;
  const neu = new Map();
  let geaendert = false;
  Object.keys(kartei.w).forEach(id => {
    let ziel = id;
    if(!wortNachId(id)){
      const kand = (UMBENANNT[id] && wortNachId(UMBENANNT[id])) ? [UMBENANNT[id]]
                 : ((nachWort && nachWort.get(id.slice(id.lastIndexOf(':') + 1))) || []);
      if(kand.length === 1){ ziel = kand[0]; geaendert = true; }
    }
    const e = kartei.w[id], da = neu.get(ziel);
    neu.set(ziel, (da && da[2] >= e[2]) ? da : e);
  });
  if(geaendert) kartei.w = Object.fromEntries(neu);
  return geaendert;
}
/* Die Kartei an known angleichen: Eintraege fuer Woerter, die es nicht mehr
   gibt oder die nicht gewusst sind, fallen weg - so ist die Kartei nie
   groesser als der Wortschatz. Gewusste Woerter ohne Eintrag bekommen
   einen (der Umzug), in Lernpfad-Reihenfolge ab morgen verteilt, siehe
   KARTEI_UMZUG_STUFE. Gibt zurueck, ob sich etwas geaendert hat. */
function karteiNachtragen(){
  if(!CATEGORIES.length) return false;
  let geaendert = false;
  Object.keys(kartei.w).forEach(id => {
    if(!known.has(id) || !wortNachId(id)){ delete kartei.w[id]; geaendert = true; }
  });
  const fehlen = [], gesehen = new Set();
  CATEGORIES.forEach(c => c.words.forEach(w => {
    if(gesehen.has(w.id)) return;
    gesehen.add(w.id);
    if(known.has(w.id) && !karteiEintrag(kartei.w, w.id)) fehlen.push(w.id);
  }));
  if(!fehlen.length) return geaendert;
  const n = fehlen.length, heute = karteiTag();
  const jeTag = Math.max(Math.min(KARTEI_UMZUG_MAX, Math.max(KARTEI_UMZUG_MIN, Math.ceil(n / KARTEI_UMZUG_TAGE))),
                         Math.ceil(n / KARTEI_ABSTAENDE[KARTEI_LETZTE]));
  fehlen.forEach((id, i) => { kartei.w[id] = [KARTEI_UMZUG_STUFE, heute + 1 + Math.floor(i / jeTag), 0]; });
  return true;
}
/* Die Kennungen der Woerter, die heute drankommen: faellig, gewusst und
   noch im Inhalt. Hoechstens so viele, wie bis KARTEI_TAG_MAX heute noch
   fehlen. Aendert nichts.
   Reihenfolge (29.10.2026, Pruefung): nach der Verspaetung im Verhaeltnis
   zum Abstand der Stufe, (heute - faellig + 1) / KARTEI_ABSTAENDE[stufe],
   die groesste zuerst - die Sortierung "relative overdueness" in Anki. Bei
   gleichem Wert die aus aelteren Leveln. Vorher kam einfach der aelteste
   Termin zuerst. Sobald mehr als KARTEI_TAG_MAX faellig sind - mit dem
   Umzug schon in den ersten Wochen, mit einer Lektion am Tag nach etwa
   drei Monaten (Release\Wiederholung_Vorschlag.md) -, stand damit jeder
   Rueckstand vor den frisch gelernten Woertern: ihre Wiederholung nach
   einem Tag kam in der Simulation im Mittel fast eine Woche zu spaet, jedes
   fuenfte bekam sie in zwei Monaten gar nicht. Einen Tag zu spaet wiegt
   nach einem Tag Abstand schwer, nach 90 Tagen kaum. Bleibt ein Berg,
   warten die Woerter mit langem Abstand entsprechend laenger. */
function karteiHeute(){
  const heute = karteiTag();
  const platz = KARTEI_TAG_MAX - (kartei.tag === heute ? kartei.n : 0);
  if(platz <= 0) return [];
  const rang = new Map();
  CATEGORIES.forEach((c, i) => c.words.forEach((w, j) => { if(!rang.has(w.id)) rang.set(w.id, i * 100000 + j); }));
  const spaet = id => (heute - kartei.w[id][1] + 1) / KARTEI_ABSTAENDE[kartei.w[id][0]];
  return Object.keys(kartei.w)
    .filter(id => kartei.w[id][1] <= heute && rang.has(id) && known.has(id))
    .map(id => [id, spaet(id)])
    .sort((x, y) => (y[1] - x[1]) || (rang.get(x[0]) - rang.get(y[0])))
    .slice(0, platz).map(x => x[0]);
}
/* Die Runde "Heute faellig": bis zu TOPF_RUNDE der Woerter von heute, mit
   dem Hinweis auf ihr Level (topfAufgabe), gemischt. Die Aufgabenart reihum
   wie in der Markiert-Runde (sternRunde), ohne Sprechen. */
function karteiRunde(){
  const runde = rundeAus(karteiHeute().map(id => topfAufgabe('w:' + id, {typ: 'mc'})).filter(Boolean));
  const types = ['mc', 'mcrev', 'type']; if(canListen) types.push('listen');
  const pick = artenReihum(types);
  runde.forEach(a => { a.typ = pick(a.w); });
  return runde;
}
function startKartei(){ rundeStarten('kartei'); }
/* Der dritte Kasten im Reiter Wiederholen, "Heute faellig: n" (Ajdin am
   28.10.2026), gebaut wie die zwei darueber: dieselben Klassen, dieselbe
   Zahl, derselbe Knopf, ohne Leben derselbe Hinweis und dieselben Wege zu
   einem Leben. Die zwei alten Kaesten bleiben, wie sie sind.
   Den Hinweis ohne Leben zeigt er nur, wenn keiner der Kaesten darueber
   ihn schon zeigt (29.10.2026, Pruefung): sonst stand derselbe lange Text
   mit denselben Knoepfen bis zu dreimal untereinander. Dann bleiben hier
   Zahl und Wort. */
function karteiKasten(){
  const box = $('karteiBox');
  if(!box) return;
  const n = karteiHeute().length;
  let html = '<h2 id="karteiTitel">' + esc(t('kartei.titel')) + '</h2><div class="desc">' + esc(t('kartei.desc')) + '</div>';
  if(!n){
    box.innerHTML = html + '<div class="topfleer">' + esc(t('kartei.leer')) + '</div>';
    return;
  }
  html += '<div class="topfzahl">' + n + '</div><div class="topfwort">' + esc(tp('kartei.anzahl', n)) + '</div>';
  if(livesNow() > 0){
    /* aria-describedby wie bei "Markiert": drei Knoepfe "Runde starten". */
    html += '<div class="row"><button class="btn know" id="karteiLos" aria-describedby="karteiTitel"></button></div>';
    box.innerHTML = html;
    $('karteiLos').textContent = t('topf.start');
    $('karteiLos').addEventListener('click', startKartei);
    return;
  }
  if(topfAnzahl() || sternAnzahl()){ box.innerHTML = html; return; }
  const herz = VERBRAUCH.find(w => w.id === 'herz');
  const perVideo = werbungErlaubt(true);
  const perMuenzen = muenzen() >= herz.preis && herz.geht();
  html += '<div class="note">' + esc(t('level.keine_leben', {zeit: fmtMin(nextLifeIn())})) + '</div>' +
    ((perVideo || perMuenzen) ?
      '<div class="row schmal">' +
        (perVideo ? '<button class="btn ghost" id="karteiAd"></button>' : '') +
        (perMuenzen ? '<button class="btn ghost" id="karteiCoin"></button>' : '') +
      '</div>' : '') +
    vollZeileLeben('karteiVoll');
  box.innerHTML = html;
  if($('karteiAd')){ $('karteiAd').innerHTML = mitSymbol('herz', esc(t('werbung.leben_holen'))); $('karteiAd').addEventListener('click', werbungFuerLeben); }
  if($('karteiCoin')){
    $('karteiCoin').innerHTML = t('lektion.leben_muenzen', symbolTexte({n: herz.preis}));
    $('karteiCoin').addEventListener('click', ()=>{ kaufe('herz'); renderLives(); showTopf(); });
  }
  vollZeileHorchen('karteiVoll');
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
