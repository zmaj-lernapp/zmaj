/* =================== LEVEL-TEST =================== */
let Tx = null;
function buildTest(){
  const c = cur();
  const eigene = shuffle(c.words.slice());
  const gram = shuffle(((GRAMMAR[c.id]||{}).uebungen||[]).slice()).slice(0,3);
  let basisIds = (c.baut_auf && c.baut_auf.length) ? c.baut_auf : (imZa() ? [] : CATEGORIES.slice(0, catIdx).map(x=>x.id));
  const basisWords = shuffle(basisIds.flatMap(id => (byId(id)||{words:[]}).words.map(w=>({w, rep:byId(id).label, pool:byId(id).words}))));
  const nRep = Math.min(TEST_WIEDERHOLUNG, basisWords.length);
  const nOwn = Math.min(TEST_FRAGEN - nRep - gram.length, eigene.length);
  const picks = [...eigene.slice(0,nOwn).map(w=>({w})), ...basisWords.slice(0,nRep)];
  while(picks.length + gram.length < TEST_FRAGEN) picks.push({w:eigene[Math.floor(Math.random()*eigene.length)]});
  const qs = picks.map((p,i)=>{ let typ = i%3===0 ? 'mcrev' : 'mc'; if(typable(p.w) && i%4===2) typ = 'type'; return {...p, typ}; });
  gram.forEach(g => qs.push({g, typ:'gram'}));
  Tx = {qs:shuffle(qs), i:0, right:0, results:[]};
}
function testBar(){ $('tBar').innerHTML = Tx.qs.map((q,i)=>'<i class="'+(i<Tx.i?(Tx.results[i]?'ok':'no'):(i===Tx.i?'cur':''))+'"></i>').join(''); punkteStand($('tBar'), Tx.i, Tx.qs.length); }
function showTestQ(){
  testBar();
  sternKnopf('tStern', Tx.i < Tx.qs.length ? Tx.qs[Tx.i] : null);   // wie in showLessonTask (19.10.2026)
  if(Tx.i >= Tx.qs.length){ showTestResult(); return; }
  $('tBody').dataset.i = Tx.i;
  renderTask(Tx.qs[Tx.i], $('tBody'), res=>{
    topfMerken(Tx.qs[Tx.i], !!res.ok);
    karteiAntwort(Tx.qs[Tx.i], !!res.ok);   // Lernkartei (29.10.2026); die Einstufung zaehlt nicht
    Tx.results.push(!!res.ok); if(res.ok) Tx.right++; Tx.i++; uhrTakt(true); zaehle('auf'); if(res.ok) zaehle('ric');
    zmajReact(!!res.ok, 'zmajTest');   // wie in der Lektion (19.10.2026)
    /* Eine falsche Antwort kostet ein Leben, genau wie in der Lektion
       (Ajdin am 19.10.2026). Bei null ist der Test vorbei und nicht
       bestanden - wie in der Lektion, die bei null nie fertig wird. Das
       gilt bei jeder Frage, nicht nur bei der letzten: wer mit 1 Leben
       anfaengt, hat keinen Fehler frei, mit 2 Leben nur einen, obwohl
       TEST_BESTANDEN_AB zwei erlaubt (9 von 10 und trotzdem verloren). Ab
       3 Leben aendert sich nichts, der dritte Fehler laesst ohnehin
       durchfallen. Bewusst so gelassen; Ajdin kennt die Folge noch nicht
       vollstaendig und entscheidet, ob es dabei bleibt. Gemessen in
       test_test_leben.py::test_wenige_leben_weniger_fehler_frei. */
    if(!res.ok){
      loseLife();
      if(livesNow()===0){ weiterBeiTipp('tBody', testOutOfLives); return; }
    }
    weiterBeiTipp('tBody', showTestQ);
  }, {noSkip:true});
}
/* Wohin "Weiter" nach einem bestandenen Test fuehrt: zum naechsten noch nicht
   bestandenen Level hinter diesem. Sind Level eingeschoben worden, ist der
   direkte Nachfolger oft laengst bestanden, und dort steht nur "Level
   bestanden" (Pruefbericht 1.3, G3: nach Level 102 ging es nach 103 statt
   nach 130). Ist alles dahinter bestanden, geht es wie bisher eins weiter.
   Im Zahnarzt-Teil bleibt es innerhalb des Teils, siehe levelEnde().
   Das Ziel ist immer offen: alles davor bis hierher ist bestanden.
   Ausnahme seit der zweiten Pruefung vom 13.11.2026: wer vor den Reitern
   eingestuft wurde und ein Grundwort-Level besteht, geht dorthin, wo
   Weitermachen steht (firstOpen) - zum anderen Grundwort-Level oder zurueck
   zum Einstieg, nicht in die Level dahinter, die er mit der Einstufung
   uebersprungen hat ("Kleine Woerter" fuehrte sonst zu "Faelle 1"). Auch
   dieses Ziel ist offen: ein Grundwort-Level vor dem Einstieg oder das
   erste nicht bestandene ab dem Einstieg. Uebersprungen wird wie dort, was
   eine alte Einstufung offen haelt (altEingestuftOffen): nach "Faelle 1"
   geht es dann zu "Faelle 2" wie in 1.3, nicht nach "Kueche & Bad". */
function naechstesOffenes(){
  if(!imZa() && vorDenReiternEingestuft() && GRUNDWORT_LEVEL.indexOf(cur().id) >= 0){
    const f = firstOpen();
    if(f !== catIdx && CATEGORIES[f] && !passed.has(CATEGORIES[f].id)) return f;
  }
  const ab = imZa() ? 0 : dranAb();
  for(let k = catIdx + 1; k < levelEnde(); k++)
    if(!passed.has(levelNach(k).id) && !(ab > 0 && altEingestuftOffen(k))) return k;
  return catIdx + 1;
}
/* Der Knopf dorthin. Die Levelnummern zaehlen seit 13.11.2026 je Reiter;
   geht es in den naechsten Reiter, hiesse es sonst "Weiter zu Level 1".
   Dann steht dort der Reiter: "Weiter zu A2". */
function weiterText(ziel){
  const anderer = !imZa() && ziel < CATEGORIES.length && stufeVon(ziel) !== stufeVon(catIdx);
  return anderer ? t('test.weiter_stufe', {stufe: stufeVon(ziel)}) : t('test.weiter_level', {n: levelNummer(ziel)});
}
function showTestResult(){
  stilleBitte(); uhrAus(); testBar();   // das letzte Wort nicht ins Ergebnis reden lassen
  sternKnopf('tStern', null);
  /* Ein Test ist eine ganze Lektion wert und zaehlt deshalb auch fuer die
     Anzeige. Bis zum 27.09.2026 fehlte das ganz. */
  werbungZaehler++;
  werbungNachDemErgebnis('test', ()=> Tx);
  const c=cur(); const ok = Tx.right >= TEST_BESTANDEN_AB;
  const hasNext = catIdx+1 < levelEnde();
  // Wann ein Level bestanden wurde, lässt sich später nicht mehr herausfinden.
  const neuBestanden = ok && !passed.has(c.id);
  if(ok){ if(!passed.has(c.id)){ passed.add(c.id); wann['lv:'+c.id] = today(); } if(!imZa()) markToday(); sound('done'); }
  if(ok && bewertungFaellig()) bewertungDran = true;
  const erfolgLob = erfolgZeile();   // Erfolge (13.11.2026): hakt ab, also vor dem Speichern
  saveProgress();   // auch bei nicht bestanden: die Aufgaben sind trotzdem beantwortet
  cloudNachLernen();   // 17.11.2026, siehe dort
  /* Auch hier koennen Tagesaufgaben fertig geworden sein - siehe lessonEnd.
     Bei nicht bestandenem Test kommt der Ton frueher, weil dann keine
     Fanfare laeuft, die er abwarten muesste. */
  const questLob = questZeilen();
  if(questLob) setTimeout(()=>sound('quest'), ok ? 850 : 150);
  /* Seit der Einstufung koennen Level offen sein, ohne bestanden zu sein.
     Die Position allein sagt deshalb nicht mehr, ob eine Sektion oder
     alles geschafft ist - es muss wirklich jedes Level bestanden sein.
     Gefunden in der Gegenpruefung am 01.10.2026. */
  const sektionFertig = (imZa() ? zaLevel() : CATEGORIES).every(x => x.sektion !== c.sektion || passed.has(x.id));
  const allesFertig = !imZa() && CATEGORIES.every(x => passed.has(x.id));      // Beim Zahnarzt zaehlt nicht mit
  /* Nach einer Einstufung wird eine Sektion oft nicht an ihrem letzten
     Level fertig, sondern mittendrin, wenn das letzte uebersprungene Level
     nachgeholt ist. Zaehlt also, was DIESER Test neu abgeschlossen hat.
     Wer ein schon bestandenes Level wiederholt, bekommt die alte Regel. */
  const nextSec = sektionFertig && (neuBestanden || (hasNext && levelNach(catIdx+1).sektion !== c.sektion));
  /* Das Ergebnis hat seinen grossen Drachen, wie lessonEnd(). Der kleine
     wird dabei auch abgebaut, nicht nur versteckt: versteckt liefe er
     unsichtbar weiter (siehe showLevelHome). */
  $('zmajTest').style.display='none'; $('zmajTest').innerHTML='';
  abbrechenZeigen('tQuit', false);   // S18, siehe abbrechenZeigen
  $('tBody').innerHTML =
    '<div class="ergebnis-titel">'+t('level.titel',{i:levelNummer(catIdx), label:esc(c.label)})+'</div><div class="celebrate"><div class="zmaj '+(ok?'cheer':'sad')+'">'+zmaj(ok?'cheer':'sad')+'</div></div>'+
    '<div class="result-big'+(ok?'':' fail')+'">'+Tx.right+' / '+Tx.qs.length+'</div>'+
    '<div class="feedback '+(ok?'ok':'no')+'">'+(ok ? mitKonfetti(t(nextSec ? 'test.sektion_fertig' : 'test.bestanden')) : t('test.durchgefallen',{n:TEST_BESTANDEN_AB}))+'</div>'+
    questLob+erfolgLob+
    '<div class="row">'+
      '<button class="btn ghost" id="tBack">'+(ok?t('test.zum_pfad'):t('lektion.zurueck'))+'</button>'+
      (ok && hasNext ? '<button class="btn know" id="tNext">'+weiterText(naechstesOffenes())+'</button>' : '<button class="btn again" id="tRetry">'+t('task.nochmal')+'</button>')+
    '</div>';
  $('tBack').addEventListener('click', ()=>{ if(ok){ homeMode='words'; showHome(); } else showLevelHome(); });
  const n=$('tNext'); if(n){ const ziel = naechstesOffenes(); n.addEventListener('click', ()=> openLevel(ziel)); }
  const r=$('tRetry'); if(r) r.addEventListener('click', startTest);
  if(ok && allesFertig && (neuBestanden || !hasNext)){ $('tBody').insertAdjacentHTML('beforeend','<div class="kicker" style="margin-top:12px">'+t('test.alles_geschafft')+'</div>'); }
}
function startTest(){
  if(anmeldungSperre()) return;
  if(!testAllowed(cur())) return;
  /* Ohne Leben kein Test, wie bei startLesson() - der Knopf ist dann zwar
     gesperrt (testKnopf), aber "Nochmal" auf dem Ergebnis ruft hierher. */
  if(livesNow()===0){ showLevelHome(); $('lvNote').textContent=t('level.keine_leben',{zeit:fmtMin(nextLifeIn())}); lebenWege(); return; }
  interstitialVorladen();   // liegt am Ende des Tests bereit (siehe dort)
  stilleBitte();   // Unteransicht, laeuft nicht ueber showView() - siehe showLevelHome
  buildTest(); $('levelHome').style.display='none'; $('lesson').style.display='none'; $('test').style.display='block';
  nurHerz(true);
  $('lBody').innerHTML='';   // siehe showLevelHome: gleiche ids in beiden Feldern
  $('zmajLesson').innerHTML='';   // siehe startLesson: kein Drache laeuft unsichtbar weiter
  uhrNeu();
  /* Derselbe kleine Drache wie in der Lektion - ohne ihn standen die
     Knoepfe im Test 126 px hoeher (Testerin, 19.10.2026). */
  /* Das Herz wie in startLesson() wieder einblenden: der Schirm ohne Leben
     blendet es aus (19.10.2026). */
  const zt=$('zmajTest'); zt.style.display='block'; $('tHerz').style.display=''; zt.innerHTML=zmaj('happy'); setMood(zt,'happy');
  abbrechenZeigen('tQuit', true);   // das Ergebnis davor blendet ihn aus (S18)
  showTestQ(); window.scrollTo({top:0, behavior:'smooth'});
}
$('btnTest').addEventListener('click', startTest);
$('tQuit').addEventListener('click', async ()=>{
  if(Tx && Tx.i < Tx.qs.length &&
     !await frage(t('test.abbrechen_frage'), t('test.abbrechen_hinweis'),
                  t('btn.abbrechen'), t('btn.weitermachen'))) return;
  saveProgress(); showLevelHome();
});

/* =================== EINSTUFUNG ===================
   Fuer alle, die schon etwas Bosnisch koennen - die zweite und dritte
   Generation, die zu Hause zuhoert, aber nie Grammatik hatte. Gewuenscht
   von den Testern am 24.09.2026 (PRODUKTIONSZUGRIFF.md, Selbsteinschaetzung
   und danach ein Test), festgelegt von Ajdin am 30.09.2026: nur beim
   ersten Start, 15 Fragen, 80 Prozent, ohne Leben. Uebersprungene Level
   sind offen, aber nicht bestanden - keine Muenzen, keine Wegmarken.

   Die Sprungweite ist abgeschaut bei Duolingo und Busuu: erst die
   Selbsteinschaetzung, dann ein Test, der leicht anfaengt, immer schwerer
   wird und von selbst aufhoert, wenn es zu schwer wird. Hier sind es fuenf
   Stufen zu je drei Fragen, jede Stufe ein Stueck weiter hinten im
   Lernpfad. Eingestuft wird hinter die letzte Stufe, bis zu der mindestens
   80 Prozent ALLER bisherigen Antworten stimmen. Beim vierten Fehler ist
   Schluss: dann schafft auch die letzte Stufe die 80 Prozent nicht mehr
   (12 von 15). Amt & Vertraege wird nie uebersprungen - das ist der Teil,
   fuer den die meisten ueberhaupt kommen.

   Die Stufen haengen an den Kennungen der Sektionen, nicht an Nummern.
   Faellt eine Sektion weg, wird die Stufe kleiner oder entfaellt; die
   Reihenfolge muss aber die des Lernpfads bleiben.
   Seit 13.11.2026 (Stufen-Reiter): Zuhause steht hinter Faelle 1, und
   "Saetze bauen" ist geteilt - die Teilung, die vorher haelfte 1 und 2
   machte, ist jetzt die Sektion selbst (saetze in A1, saetze2 in A2).
   Zuhause kommt deshalb zu Saetze bauen 2; sonst haette eine bestandene
   zweite Stufe hinter Zuhause eingestuft, ueber Saetze bauen 1 hinweg.
   Eingestuft wird weiter hoechstens bis zum Anfang von B1. */
const EINSTUFUNG_STUFEN = [
  {sek:['alltag'],                          arten:['mcrev','mc','gap']},
  {sek:['anfassen','tiernatur'],            arten:['mcrev','mc','gap']},
  {sek:['saetze'],                          arten:['gram','gram','gap']},
  {sek:['zuhause2','saetze2'],              arten:['gram','gram','gap']},
  {sek:['einkauf','herkunft','kultur'],     arten:['mcrev','mc','gap']},
];
const EINSTUFUNG_QUOTE = 0.8;
let Ex = null;
/* Erst wenn Vorspann und Googles Einwilligungsfenster durch sind. Sonst
   laegen zwei Fenster uebereinander. */
let einstufungBereit = false;

/* Ab welchem Level die Einstufung den Weg frei gemacht hat, oder -1. */
function einstufungIndex(){
  if(!einstufung || !einstufung.bis) return -1;
  return CATEGORIES.findIndex(c => c.id === einstufung.bis);
}
/* Nur beim allerersten Start: noch nie gefragt und noch gar nichts getan.
   Wer schon eine Lektion hinter sich hat - auch aus einer Sicherung -,
   wird nicht mehr gefragt. */
function einstufungFaellig(){
  return !einstufung && !ALLE_FREI && CATEGORIES.length > 0
    && ohneZa(passed) === 0 && ohneZa(known) === 0 && days.size === 0;
}
function stufenLevel(st){
  const nr = [];
  CATEGORIES.forEach((c, i) => { if(st.sek.indexOf(c.sektion) >= 0) nr.push(i); });
  if(!st.haelfte) return nr;
  const mitte = Math.ceil(nr.length / 2);
  return st.haelfte === 1 ? nr.slice(0, mitte) : nr.slice(mitte);
}
/* Eine Frage aus den Leveln einer Stufe. `schon` verhindert, dass dasselbe
   Wort zweimal drankommt. Fehlt etwas (keine Grammatik, keine Saetze),
   weicht die Frage auf eine Wortaufgabe aus. */
function einstufungFrage(levels, art, schon){
  const reihe = shuffle(levels.slice());
  if(art === 'gram'){
    for(const i of reihe){
      const id = CATEGORIES[i].id;
      const u = shuffle(((GRAMMAR[id] || {}).uebungen || []).filter(g => !schon.has('g:' + g._lv + '|' + g._nr)));
      if(u.length){ schon.add('g:' + u[0]._lv + '|' + u[0]._nr); return {typ:'gram', g:u[0]}; }
    }
    art = 'mcrev';
  }
  if(art === 'gap'){
    const ids = new Set(levels.map(i => CATEGORIES[i].id));
    const s = shuffle(SENTENCES.filter(x => ids.has(x.kat) && !schon.has('s:' + x.text)))[0];
    if(s){ schon.add('s:' + s.text); return {typ:'gap', s}; }
    art = 'mc';
  }
  for(const i of reihe){
    const c = CATEGORIES[i];
    const w = shuffle(c.words.filter(x => !schon.has(x.id)))[0];
    if(w){ schon.add(w.id); return {typ:art, w, pool:c.words}; }
  }
  return null;
}
function baueEinstufung(wahl){
  const stufen = [], qs = [], schon = new Set();
  EINSTUFUNG_STUFEN.forEach(st => {
    const levels = stufenLevel(st);
    if(!levels.length) return;
    const k = stufen.length;
    stufen.push(levels);
    st.arten.forEach(art => {
      const q = einstufungFrage(levels, art, schon);
      if(q){ q.stufe = k; qs.push(q); }
    });
  });
  Ex = {qs, i:0, results:[], stufen, fehler:0, fertig:false, wahl};
}
/* So viele Fehler vertraegt der ganze Test noch: bei 15 Fragen drei. */
function einstufungSpielraum(){
  const n = Ex.qs.length;
  return n - Math.ceil(n * EINSTUFUNG_QUOTE - 1e-9);
}
/* Wo es losgeht: hinter der letzten Stufe, bis zu der die Quote haelt.
   Eine Stufe zaehlt nur, wenn alle ihre Fragen beantwortet sind. */
function einstufungZiel(){
  let n = 0, r = 0, beste = -1;
  for(let k = 0; k < Ex.stufen.length; k++){
    const nr = [];
    Ex.qs.forEach((q, i) => { if(q.stufe === k) nr.push(i); });
    if(!nr.length) continue;
    if(nr.some(i => i >= Ex.results.length)) break;
    n += nr.length;
    r += nr.filter(i => Ex.results[i]).length;
    if(r >= n * EINSTUFUNG_QUOTE - 1e-9) beste = k;
  }
  if(beste < 0) return 0;
  const ziel = Math.max.apply(null, Ex.stufen[beste]) + 1;
  return Math.min(ziel, CATEGORIES.length - 1);
}

/* Einmal je Start. Ohne diesen Merker kam die Frage nach dem Wegtippen bei
   jedem Reiterwechsel wieder - showHome() ruft einstufungAnbieten() jedes
   Mal. Gefunden in der Gegenpruefung am 01.10.2026. */
let einstufungGefragt = false;
function einstufungAnbieten(){
  if(!einstufungBereit || einstufungGefragt || !einstufungFaellig()) return;
  /* Nur auf der Startseite und nur, wenn gerade nichts anderes offen ist.
     Klappt es jetzt nicht, kommt die Frage beim naechsten Start - sie gilt
     erst als beantwortet, wenn jemand wirklich gewaehlt hat. */
  if(!sichtbar('pfad') || frageSchliessen ||
     document.querySelector('.nachfrage, .einwilligung, .werbung')) return;
  einstufungGefragt = true;
  einstufungWahl();
}
function einstufungKarte(inhalt){
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage';
  kasten.innerHTML = '<div class="nachfragebox einstbox">' + inhalt + '</div>';
  document.body.appendChild(kasten);
  /* Zurueck-Taste und Tipp daneben schliessen nur. Gefragt wird dann beim
     naechsten Start wieder - ein versehentlicher Tipp soll den Test nicht
     fuer immer verschenken. */
  const zu = ()=>{ kasten.remove(); if(frageSchliessen === zu) frageSchliessen = null; };
  frageSchliessen = zu;
  kasten.addEventListener('click', e=>{ if(e.target === kasten) zu(); });
  return {kasten, zu};
}
function einstufungMerken(wahl, bis, richtig, fragen){
  /* reiter: eingestuft mit den Stufen-Reitern (seit 13.11.2026), siehe
     firstOpen und GRUNDWORT_LEVEL. Aeltere Einstufungen haben das Feld nicht. */
  einstufung = {tag: today(), wahl: wahl, bis: bis || '', reiter: true};
  if(fragen !== undefined){ einstufung.richtig = richtig; einstufung.fragen = fragen; }
  saveProgress();
}
function einstufungWahl(){
  const {kasten, zu} = einstufungKarte(
    '<div class="celebrate"><div class="zmaj idle">' + zmaj('happy') + '</div></div>' +
    '<h3>' + esc(t('einst.frage_titel')) + '</h3>' +
    '<div class="abowahl">' +
      /* Die Schluessel ausgeschrieben, nicht zusammengesetzt: texte_pruefen.py
         liest die t()-Aufrufe und haelt 'einst.' + w fuer einen fehlenden Text. */
      [['neu', t('einst.neu')], ['etwas', t('einst.etwas')], ['gut', t('einst.gut')]].map(([w, text]) =>
        '<button type="button" class="abokarte einstwahl" data-wahl="' + w + '"><span class="n">' +
        esc(text) + '</span></button>').join('') +
    '</div>' +
    /* Wer neu installiert hat und schon ein Konto hat, holt hier seinen
       Stand zurueck, ohne erst Lektion 1 zu machen. Nur mit der
       Pflicht-Anmeldung, 28.10.2026. */
    (cloudModus() ? '<div class="abohinweis" style="text-align:center; margin-top:10px">' +
                    '<button type="button" class="abolink" id="eKonto"></button></div>' : ''));
  if(cloudModus()){
    const k = kasten.querySelector('#eKonto');
    k.textContent = t('konto.zurueck_anmelden');
    k.addEventListener('click', ()=>{ zu(); anmeldungZeigen('konto'); });
  }
  kasten.querySelectorAll('[data-wahl]').forEach(b => b.addEventListener('click', ()=>{
    const wahl = b.dataset.wahl;
    zu();
    if(wahl === 'neu'){ einstufungMerken('neu', ''); return; }
    einstufungErklaeren(wahl);
  }));
}
function einstufungErklaeren(wahl){
  /* Die Zahl kommt aus dem gebauten Test, nicht aus dem Text: fehlt einmal
     eine Sektion, stimmt die Angabe trotzdem. */
  baueEinstufung(wahl);
  const {kasten, zu} = einstufungKarte(
    '<h3>' + esc(t('einst.test_titel')) + '</h3>' +
    '<div class="txt">' + esc(t('einst.test_text', {n: Ex.qs.length})) + '</div>' +
    '<button class="btn know" id="eStart"></button>' +
    '<button class="btn ghost" id="eNeu"></button>');
  kasten.querySelector('#eStart').textContent = t('einst.starten');
  kasten.querySelector('#eNeu').textContent = t('einst.lieber_neu');
  kasten.querySelector('#eStart').addEventListener('click', ()=>{ zu(); einstufungStarten(); });
  kasten.querySelector('#eNeu').addEventListener('click', ()=>{ zu(); Ex = null; einstufungMerken(wahl, ''); });
}
function einstufungStarten(){
  if(anmeldungSperre()) return;
  if(!Ex || !Ex.qs.length){ einstufungMerken(Ex ? Ex.wahl : 'etwas', ''); Ex = null; return; }
  showView('einstufungView');
  herzImKasten(false);   // nach einem Sprung-Test wieder der Platzhalter (13.11.2026)
  /* Die Uhr fuer die Tagesaufgabe "Minuten" laeuft bewusst nicht: der Test
     bringt keine Muenzen.
     Seit 19.10.2026 ganz ohne Kopf und Fuss, wie Lektion und Level-Test:
     sie schoben den Kasten 54 px nach unten, und bei 360 px Breite brach
     "Zurueck" oben in zwei Zeilen um. Hinaus geht es weiter ueber
     "Test beenden" und die Zurueck-Taste des Handys (backTarget unten).
     Bis dahin blendete die Einstufung hier die Leiste mit Leben und
     Muenzen aus und schrieb "Einstufung" unter das Logo - beides sitzt im
     Kopf, den nurHerz jetzt ganz verbirgt, und beim Verlassen setzen
     showView() und showPath() beides neu. setzeZurueck bleibt: der Knopf
     ist zwar unsichtbar, aber backTarget gilt fuer die Zurueck-Taste. */
  nurHerz(true);
  setzeZurueck(t('btn.zurueck'), ()=>{
    if(Ex && !Ex.fertig) $('eQuit').click(); else { homeMode = 'words'; showHome(); }
  });
  $('eQuit').style.display = '';
  $('eBody').innerHTML = '';
  const ze = $('zmajEinst'); ze.style.display = 'block'; ze.innerHTML = zmaj('happy'); setMood(ze, 'happy');
  einstufungFrageZeigen();
}
function einstufungBar(){
  $('eBar').innerHTML = Ex.qs.map((q, i) => '<i class="' +
    (i < Ex.results.length ? (Ex.results[i] ? 'ok' : 'no') : (i === Ex.i && !Ex.fertig ? 'cur' : '')) + '"></i>').join('');
  punkteStand($('eBar'), Ex.results.length, Ex.qs.length);
}
function einstufungFrageZeigen(){
  if(!Ex || Ex.fertig) return;
  einstufungBar();
  if(Ex.i >= Ex.qs.length || Ex.fehler > einstufungSpielraum()){ einstufungEnde(); return; }
  const body = $('eBody');
  body.dataset.i = Ex.i;
  const meinEx = Ex;
  renderTask(Ex.qs[Ex.i], body, res=>{
    if(Ex !== meinEx || Ex.fertig) return;
    Ex.results.push(!!res.ok);
    if(!res.ok) Ex.fehler++;
    Ex.i++;
    einstufungBar();
    zmajReact(!!res.ok, 'zmajEinst');   // wie in der Lektion (19.10.2026)
    weiterBeiTipp('eBody', einstufungFrageZeigen);
  }, {noSkip:true});
}
function einstufungEnde(){
  if(!Ex || Ex.fertig) return;
  Ex.fertig = true;
  stilleBitte();
  const ziel = einstufungZiel();
  const richtig = Ex.results.filter(Boolean).length;
  const c = CATEGORIES[ziel];
  einstufungMerken(Ex.wahl, ziel > 0 ? c.id : '', richtig, Ex.results.length);
  einstufungBar();
  $('eQuit').style.display = 'none';
  // Das Ergebnis hat seinen grossen Drachen; der kleine wird abgebaut, wie in showTestResult()
  $('zmajEinst').style.display = 'none'; $('zmajEinst').innerHTML = '';
  $('eBody').innerHTML =
    '<div class="ergebnis-titel">' + esc(t('einst.ergebnis_titel')) + '</div>' +
    '<div class="celebrate"><div class="zmaj ' + (ziel > 0 ? 'cheer' : 'idle') + '">' + zmaj(ziel > 0 ? 'cheer' : 'happy') + '</div></div>' +
    '<div class="result-big">' + richtig + ' / ' + Ex.results.length + '</div>' +
    '<div class="feedback ok">' + esc(ziel > 0 ? t('einst.ergebnis_start', {stufe: stufeVon(ziel), n: levelNummer(ziel), label: c.label})
                                              : t('einst.ergebnis_anfang')) + '</div>' +
    (ziel > 0 ? '<div class="feedback" style="color:var(--muted)">' + esc(t('einst.ergebnis_offen')) + '</div>' : '') +
    '<div class="row"><button class="btn know" id="eLos"></button></div>';
  $('eLos').textContent = t('einst.los');
  // Danach kommt die Anmeldung (28.10.2026): showHome() fuehrt hin.
  if(anmeldungFaellig()) $('eLos').textContent = t('anm.weiter');
  sound(ziel > 0 ? 'done' : 'ok');
  $('eLos').addEventListener('click', ()=>{
    homeMode = 'words';
    if(c) offeneSektion = c.sektion;
    stufeGewaehlt = null;   // der Reiter des Einstiegs (13.11.2026)
    showHome();
  });
}
$('eQuit').addEventListener('click', async ()=>{
  /* Derselbe Knopf beendet den Sprung-Test, der in dieser Ansicht laeuft */
  if(Sx && !Sx.fertig){
    if(await sprungDarfWeg()) sprungZurueck();
    return;
  }
  if(!Ex || Ex.fertig) return;
  const ziel = einstufungZiel();
  if(!await frage(t('einst.abbrechen_frage'), t('einst.abbrechen_text', {stufe: stufeVon(ziel), n: levelNummer(ziel)}),
                  t('btn.abbrechen'), t('btn.weitermachen'))) return;
  einstufungEnde();
});

/* =================== SPRUNG-TEST (13.11.2026) ===================
   Ein Reiter geht auf, wenn der vorige fertig ist - oder vorher mit dem
   Sprung-Test (reiter.md, Variante B, Ajdin: "alles wie empfohlen"):
   15 Fragen aus dem vorigen Reiter, ab 12 richtigen ist der Reiter offen,
   dieselbe Schwelle wie bei der Einstufung (80 Prozent). Gefragt wird wie
   dort von leicht nach schwer: der vorige Reiter in fuenf Stuecken zu je
   drei Fragen (Wort, Grammatik, Luecke - fehlt eins, weicht
   einstufungFrage() aus). Ist die Schwelle nicht mehr zu schaffen, ist
   Schluss.
   Wie bei der Einstufung sind die uebersprungenen Level offen, aber nicht
   bestanden: keine Muenzen, keine Wegmarken, kein Lerntag, nichts in
   Topf und Kartei. Anders als dort kostet jede falsche Antwort ein Leben,
   wie im Level-Test (Frage 7a am 13.11.2026; Level-Test seit 19.10.2026),
   mit Vollversion unbegrenzt. Bei null Leben ist er vorbei und nicht
   bestanden.
   Gemerkt wird in wann unter "sp:<Reiter>" der Tag des Bestehens. wann
   geht mit Sicherung und Cloud und wird beim Abgleich je Schluessel
   vereinigt - ein bestandener Sprung geht also auf keinem Geraet wieder
   verloren, und der Stand braucht kein neues Feld. Offen ist dann alles
   bis zum ersten Level des Reiters (sprungIndex, freiBis).
   Er laeuft in der Ansicht der Einstufung (eBar, eBody, eQuit), mit Sx
   statt Ex. */
const SPRUNG_FRAGEN = 15;
let Sx = null;
function herzImKasten(echt){
  const h = $('eHerz'); if(!h) return;
  h.classList.toggle('platzhalter', !echt);
  if(echt) h.removeAttribute('aria-hidden'); else h.setAttribute('aria-hidden', 'true');
  renderLives();
}
function sprungIndex(){
  let bis = -1;
  STUFEN.forEach(st => {
    if(!wann['sp:' + st]) return;
    const L = reiterLevel(st);
    if(L.length) bis = Math.max(bis, L[0]);
  });
  return bis;
}
const sprungVorher = st => STUFEN[STUFEN.indexOf(st) - 1] || '';
const sprungNoetig = n => Math.ceil(n * EINSTUFUNG_QUOTE - 1e-9);
function sprungBauen(ziel){
  const vorher = sprungVorher(ziel), levels = reiterLevel(vorher);
  const qs = [], schon = new Set(), teile = 5;
  for(let k = 0; k < teile; k++){
    const stueck = levels.slice(Math.floor(k * levels.length / teile), Math.floor((k + 1) * levels.length / teile));
    if(!stueck.length) continue;
    ['mc', 'gram', 'gap'].forEach(art => { const q = einstufungFrage(stueck, art, schon); if(q) qs.push(q); });
  }
  Sx = {ziel, vorher, qs: qs.slice(0, SPRUNG_FRAGEN), i: 0, results: [], fehler: 0, fertig: false, ohneLeben: false};
}
/* Ohne Leben dieselben Wege wie beim Level-Test (lebenWege, lessonOutOfLives):
   ein Video oder Muenzen fuer ein Leben, darunter die Zeile zur Vollversion.
   Pruefung vom 13.11.2026: vorher stand auf der Karte nur ein Satz, der auf
   die Grammatik-Erklaerung verwies (die es dort nicht gibt), und bei 360 x 740
   lag er unter dem Bildrand - der Knopf schien nichts zu tun. Mitten im Test
   gab es nur "Keine Leben mehr." und "Zurueck".
   vorn: Anfang der Kennungen ("sprungK" auf der Karte, "sprungE" auf dem
   Schirm am Ende), damit die Knoepfe nie doppelt im Dokument stehen;
   werbungFuerLeben() kennt beide Video-Knoepfe. */
function istSprungAd(k){ return !!k && (k.id === 'sprungKAd' || k.id === 'sprungEAd'); }
function sprungLebenWege(kasten, vorn){
  if(!kasten) return;
  const herz = VERBRAUCH.find(w => w.id === 'herz');
  const perVideo = werbungErlaubt(true);
  const perMuenzen = muenzen() >= herz.preis && herz.geht();
  kasten.innerHTML =
    ((perVideo || perMuenzen) ?
      '<div class="row schmal">' +
        (perVideo   ? '<button class="btn ghost" id="' + vorn + 'Ad">' + mitSymbol('herz', esc(t('werbung.leben_holen'))) + '</button>' : '') +
        (perMuenzen ? '<button class="btn ghost" id="' + vorn + 'Coin">' + t('lektion.leben_muenzen', symbolTexte({n: herz.preis})) + '</button>' : '') +
      '</div>' : '') +
    vollZeileLeben(vorn + 'Voll');
  const ad = $(vorn + 'Ad'), coin = $(vorn + 'Coin');
  if(ad) ad.addEventListener('click', werbungFuerLeben);
  /* Wie beim Level-Test nur kaufen, wenn wirklich noch keins da ist */
  if(coin) coin.addEventListener('click', ()=>{ if(livesNow() === 0) kaufe('herz'); renderLives(); sprungLebenDa(); });
  vollZeileHorchen(vorn + 'Voll');
}
/* Ein Leben ist da (Video, Muenzen oder nachgewachsen): zurueck zur Karte
   des Reiters, wo der Test von vorn beginnt - wie der Level-Test, der dann
   auf der Level-Uebersicht steht. */
function sprungLebenDa(){
  if(sichtbar('einstufungView') && Sx && Sx.fertig){ sprungZurueck(); return; }
  const n = $('sprungNote'), w = $('sprungLeben');
  if(n) n.textContent = '';
  if(w) w.innerHTML = '';
  renderLives();
}
function sprungStarten(ziel){
  if(anmeldungSperre()) return;
  if(!sprungVorher(ziel)) return;
  /* Ohne Leben kein Test, wie beim Level-Test (startTest) - aber mit den
     Wegen zu einem Leben, sichtbar gleich unter dem Knopf. */
  if(livesNow() === 0){
    const n = $('sprungNote');
    if(n) n.textContent = t('sprung.keine_leben', {zeit: fmtMin(nextLifeIn())});
    sprungLebenWege($('sprungLeben'), 'sprungK');
    const ohne = $('sprungOhne');
    try{ if(ohne) ohne.scrollIntoView({block: 'nearest', behavior: kachelnRuhig() ? 'auto' : 'smooth'}); }catch(e){}
    return;
  }
  if($('sprungNote')) $('sprungNote').textContent = '';   // ein alter Hinweis von vorhin verschwindet
  if($('sprungLeben')) $('sprungLeben').innerHTML = '';
  sprungBauen(ziel);
  if(!Sx.qs.length){ Sx = null; return; }
  showView('einstufungView');
  /* Das Herz im Kasten ist bei der Einstufung ein unsichtbarer Platzhalter
     (sie kostet keine Leben); hier ist es echt wie im Level-Test. */
  herzImKasten(true);
  nurHerz(true);
  setzeZurueck(t('btn.zurueck'), ()=>{ if(Sx && !Sx.fertig) $('eQuit').click(); else sprungZurueck(); });
  $('eQuit').style.display = '';
  $('eBody').innerHTML = '';
  const ze = $('zmajEinst'); ze.style.display = 'block'; ze.innerHTML = zmaj('happy'); setMood(ze, 'happy');
  sprungFrageZeigen();
}
function sprungBar(){
  $('eBar').innerHTML = Sx.qs.map((q, i) => '<i class="' +
    (i < Sx.results.length ? (Sx.results[i] ? 'ok' : 'no') : (i === Sx.i && !Sx.fertig ? 'cur' : '')) + '"></i>').join('');
  punkteStand($('eBar'), Sx.results.length, Sx.qs.length);
}
function sprungFrageZeigen(){
  if(!Sx || Sx.fertig) return;
  sprungBar();
  if(Sx.i >= Sx.qs.length || Sx.fehler > Sx.qs.length - sprungNoetig(Sx.qs.length)){ sprungEnde(); return; }
  const body = $('eBody');
  body.dataset.i = Sx.i;
  const meinSx = Sx;
  renderTask(Sx.qs[Sx.i], body, res=>{
    if(Sx !== meinSx || Sx.fertig) return;
    Sx.results.push(!!res.ok);
    if(!res.ok) Sx.fehler++;
    Sx.i++;
    sprungBar();
    zmajReact(!!res.ok, 'zmajEinst');
    if(!res.ok){
      loseLife();
      if(livesNow() === 0){ Sx.ohneLeben = true; weiterBeiTipp('eBody', sprungEnde); return; }
    }
    weiterBeiTipp('eBody', sprungFrageZeigen);
  }, {noSkip:true});
}
function sprungEnde(){
  if(!Sx || Sx.fertig) return;
  Sx.fertig = true;
  stilleBitte();
  const ziel = Sx.ziel, n = Sx.qs.length, ab = sprungNoetig(n);
  const richtig = Sx.results.filter(Boolean).length;
  const ok = !Sx.ohneLeben && richtig >= ab;
  if(ok && !wann['sp:' + ziel]) wann['sp:' + ziel] = today();
  saveProgress();
  cloudNachLernen();   // 17.11.2026, siehe dort
  $('eQuit').style.display = 'none';
  // Das Ergebnis hat seinen grossen Drachen, wie einstufungEnde()
  $('zmajEinst').style.display = 'none'; $('zmajEinst').innerHTML = '';
  if(Sx.ohneLeben){ sprungOhneLeben(); return; }
  sprungBar();
  $('eBody').innerHTML =
    '<div class="ergebnis-titel">' + esc(t('sprung.titel', {stufe: ziel})) + '</div>' +
    '<div class="celebrate"><div class="zmaj ' + (ok ? 'cheer' : 'sad') + '">' + zmaj(ok ? 'cheer' : 'sad') + '</div></div>' +
    '<div class="result-big' + (ok ? '' : ' fail') + '">' + richtig + ' / ' + n + '</div>' +
    '<div class="feedback ' + (ok ? 'ok' : 'no') + '">' +
      esc(ok ? t('sprung.offen', {stufe: ziel}) : t('sprung.nicht', {ab, stufe: ziel})) + '</div>' +
    (ok ? '<div class="feedback" style="color:var(--muted)">' + esc(t('einst.ergebnis_offen')) + '</div>' : '') +
    '<div class="row"><button class="btn know" id="sprungLos"></button></div>';
  $('sprungLos').textContent = ok ? t('sprung.zum_reiter', {stufe: ziel}) : t('btn.zurueck');
  $('sprungLos').addEventListener('click', sprungZurueck);
  sound(ok ? 'done' : 'no');
}
/* Bei null Leben mitten im Test derselbe Schirm wie im Level-Test
   (lessonOutOfLives): die Null, die Wartezeit und die Wege zu einem Leben.
   Mit einem Leben geht es zurueck zur Karte (sprungLebenDa), dort beginnt
   der Test von vorn. .ohneleben: daran erkennt ohneLebenVorbei() ihn. */
function sprungOhneLeben(){
  $('eBar').innerHTML = '';
  herzImKasten(false);
  $('eBody').innerHTML =
    '<div class="ergebnis-titel">' + esc(t('sprung.titel', {stufe: Sx.ziel})) + '</div>' +
    '<div class="celebrate"><div class="zmaj sad">' + zmaj('cry') + '</div></div>' +
    '<div class="result-big fail ohneleben">' + symbol('herz', t('stat.leben')) + ' 0</div>' +
    '<div class="feedback no">' + esc(t('lektion.keine_leben')) + '</div>' +
    '<div class="stats"><div class="stat"><b>' + fmtMin(nextLifeIn()) + '</b>' + esc(t('lektion.bis_naechstes')) + '</div></div>' +
    '<div id="sprungEWege"></div>' +
    '<div class="row"><button class="btn know" id="sprungLos"></button></div>';
  sprungLebenWege($('sprungEWege'), 'sprungE');
  $('sprungLos').textContent = t('btn.zurueck');
  $('sprungLos').addEventListener('click', sprungZurueck);
  sound('no');
  renderLives();
}
/* Abbrechen mit Nachfrage, wie beim Level-Test. Verbrauchte Leben bleiben
   verbraucht. true, wenn abgebrochen ist. */
async function sprungDarfWeg(){
  if(!Sx || Sx.fertig) return true;
  if(!await frage(t('sprung.abbrechen_frage'), t('sprung.abbrechen_text', {stufe: Sx.ziel}),
                  t('btn.abbrechen'), t('btn.weitermachen'))) return false;
  Sx.fertig = true;
  stilleBitte();
  saveProgress();
  return true;
}
/* Zurueck in den Lernpfad, in den Reiter des Tests: bestanden steht er
   offen da, sonst wieder mit seiner Karte. */
function sprungZurueck(){
  const ziel = Sx ? Sx.ziel : '';
  herzImKasten(false);
  homeMode = 'words';
  if(ziel){
    stufeGewaehlt = {st: ziel, bei: stufeVon(firstOpen())};
    offeneSektion = laufendeSektion(ziel);
  }
  showHome();
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
