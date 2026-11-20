/* =================== STARTSEITE =================== */
/* Zurueck aus einem Level soll dort landen, wo man im Lernpfad war, sonst
   scrollt man in einer langen Sektion nach jedem Zurueck neu hinunter
   (Pruefbericht 1.3, G11). openLevel() merkt sich die Stelle, und sie gilt
   einmal, nur auf dem Weg aus dem Level. Von anderswo oeffnet der Pfad
   weiterhin oben, siehe LERNPFAD. */
let pfadStelle = 0;
function showHome(){
  uhrAus();
  if(anmeldungSperre()) return;     // Pflicht-Anmeldung, 28.10.2026
  const stelle = homeMode === 'words' && sichtbar('levelView') ? pfadStelle : 0;
  pfadStelle = 0;
  /* Die Mindesthoehe aus stufeWaehlen() nur behalten, wenn es gleich an die
     alte Stelle zurueckgeht - sonst oeffnet die Startseite oben, und ein
     kurzer Reiter braucht keinen leeren Bildschirm darunter. */
  if(!stelle) $('wordsHome').style.minHeight = '';
  $('storiesHome').style.minHeight = '';   // ebenso aus geschStufeWaehlen()
  showView('pfad'); setzeZurueck('', null);
  $('modeWords').setAttribute('aria-selected', homeMode==='words'); $('modeStories').setAttribute('aria-selected', homeMode==='stories');
  $('modeTopf').setAttribute('aria-selected', homeMode==='topf');
  $('wordsHome').style.display = homeMode==='words' ? 'block' : 'none';
  $('storiesHome').style.display = homeMode==='stories' ? 'block' : 'none';
  $('topfHome').style.display = homeMode==='topf' ? 'block' : 'none';
  erfolgeNachreichen();   // Erfolge (13.11.2026): still nachtragen, vor der Leiste in renderHero()
  renderHero(); renderLives();
  if(homeMode==='words') showPath(); else if(homeMode==='topf') showTopf(); else showStoryPath();
  einstufungAnbieten();
  kartenNachreichen();
  if(einstufungBereit) agbHinweis();
  if(stelle) window.scrollTo({top: stelle, behavior: 'instant'});
}
/* Der Laden ist keine Lernsache, deshalb steht er oben bei Profil und
   Einstellungen und nicht in der Reiterleiste. */
function showLaden(){
  uhrAus();
  if(anmeldungSperre()) return;
  // Im Laden bleibt die Leiste stehen: dort will man sehen, was man hat.
  showView('shopView'); $('kopfLeiste').style.display='';
  ladenOffen = false;
  setzeZurueck(t('btn.zurueck'), showHome);
  $('tag').textContent = t('laden.titel');
  renderLaden();
}
$('modeWords').addEventListener('click', ()=>{ homeMode='words'; showHome(); });
$('modeStories').addEventListener('click', ()=>{ homeMode='stories'; showHome(); });
$('modeTopf').addEventListener('click', ()=>{ homeMode='topf'; showHome(); });
$('btnShop').addEventListener('click', async ()=>{
  if(!await lektionDarfWeg()) return;
  await saveProgress(); showLaden();
});
$('btnBack').addEventListener('click', ()=>{ if(backTarget) backTarget(); });

/* =================== LERNPFAD =================== */
/* Der Pfad sprang frueher beim Oeffnen zur aktuellen Lektion. Das kam aus
   der Zeit vor dem Knopf "Weitermachen" oben, der genau dorthin fuehrt.
   Jetzt oeffnet der Pfad oben und bleibt dort - showView() setzt ohnehin
   window.scrollTo(0), gespart wird also nicht das Scrollen an sich,
   sondern der Sprung mitten in die Liste hinein.
   Ajdin am 29.09.2026: "braucht die app nicht zur aktuellsten stelle
   springen". */
/* ---- Die Reiterleiste (13.11.2026) ----
   Der Pfad oeffnet sich in dem Reiter, in dem Weitermachen steht
   (reiter.md). Tippt man einen anderen an, bleibt der stehen - bis
   Weitermachen selbst in einen anderen Reiter wandert, etwa nach dem
   letzten Level von A1: dann zeigt der Pfad wieder dorthin. Gemerkt wird
   das nur fuer diesen Start, wie die offene Sektion. */
let stufeGewaehlt = null;   // {st, bei}: gewaehlt, als Weitermachen in "bei" stand
function angezeigteStufe(){
  const jetzt = stufeVon(firstOpen());
  return (stufeGewaehlt && stufeGewaehlt.bei === jetzt && STUFEN.indexOf(stufeGewaehlt.st) >= 0)
    ? stufeGewaehlt.st : jetzt;
}
/* Die Sektion, die in einem Reiter beim Hineinschauen offen ist: im
   Reiter von Weitermachen dessen Sektion, sonst die mit dem ersten offenen,
   nicht bestandenen Level. Ist dort nichts zu tun (fertig oder zu), sind
   alle zugeklappt. */
function laufendeSektion(st){
  const next = firstOpen();
  if(CATEGORIES[next] && stufeVon(next) === st) return CATEGORIES[next].sektion;
  const k = reiterLevel(st).find(i => isUnlocked(i) && !passed.has(CATEGORIES[i].id));
  return k === undefined ? '' : CATEGORIES[k].sektion;
}
/* Wie weit ein Reiter ist: bald (noch keine Level), fertig, offen oder zu.
   Offen ist er, sobald die Kette sein erstes Level erreicht (inDerKette).
   Ein angefangenes Level (levelAngefangen) bleibt trotzdem offen, macht
   aber nicht den ganzen Reiter auf: wer in A1 lernt und in "Kueche & Bad"
   schon Woerter kennt, sieht A2 zu, mit Sprung-Test, und kommt in
   "Kueche & Bad" trotzdem hinein. */
function stufeStand(st){
  const L = reiterLevel(st);
  if(!L.length) return {art: 'bald', done: 0, n: 0};
  const done = L.filter(i => passed.has(CATEGORIES[i].id)).length;
  const art = done === L.length ? 'fertig' : (inDerKette(L[0]) ? 'offen' : 'zu');
  return {art, done, n: L.length};
}
/* Ein Tipp auf einen Reiter wechselt nur, was darunter steht - die Leiste
   selbst bleibt genau da, wo der Finger sie getroffen hat. Ajdin am
   14.11.2026: "wenn man auf B1 zb tippt dann springt das bild so komisch
   wieder nach oben mach das raus".
   Warum es sprang: showPath() leert erst die Sektionen. Fuer einen Augenblick
   ist die Seite kuerzer als der Bildschirm, der Browser klemmt die Stelle
   auf 0, und als die neuen Sektionen dastanden, stand man oben. In einen
   kurzen Reiter (C1 "kommt bald", ein Reiter mit allen Sektionen zu) ginge
   es auch ohne das Leeren nicht anders: die Seite reichte nicht bis dahin.
   Deshalb wie bei sektionAufklappen(): Lage der Leiste vorher merken, und
   damit die Stelle erreichbar bleibt, bekommt #wordsHome eine Mindesthoehe -
   ab der Leiste ein Bildschirm abzueglich ihrer Lage. Ganz oben (scrollY 0)
   braucht es keine, die Stelle 0 gibt es immer. Danach um den Rest
   nachscrollen, ohne Fahrt (behavior 'instant'). Alles in einem Zug vor
   dem naechsten Bild, es ruckelt nichts. Die Mindesthoehe bleibt stehen,
   bis wieder ein Reiter gewaehlt wird oder die Startseite neu aufgeht
   (showHome); vorher wegnehmen hiesse, die Seite springt doch noch. */
function stufeWaehlen(st){
  leisteStehenLassen($('reiterLeiste'), $('wordsHome'), () => {
    stufeGewaehlt = {st, bei: stufeVon(firstOpen())};
    offeneSektion = laufendeSektion(st);
    showPath();
    sektionsFarbe();
  });
}
/* Seit dem 17.11.2026 haben die Geschichten dieselbe Leiste
   (geschStufeWaehlen), darum steht das Festhalten hier fuer beide: feld
   ist der Bereich unter der Leiste, neuZeichnen() zeichnet ihn neu. */
function leisteStehenLassen(leiste, feld, neuZeichnen){
  /* In Bildschirmpunkten, wie scrollBy und innerHeight - siehe rectFaktor() */
  const oben = () => leiste.getBoundingClientRect().top * rectFaktor();
  const vorher = (leiste && leiste.offsetParent) ? oben() : null;
  if(feld){
    feld.style.minHeight = '';
    if(vorher !== null && innerHeight > 0 && window.scrollY > 0)
      feld.style.minHeight = Math.ceil(Math.max(0, innerHeight - vorher) / GROSS) + 'px';
  }
  neuZeichnen();
  if(vorher !== null){
    const versatz = oben() - vorher;
    if(Math.abs(versatz) > 0.5) scrollBy({top: versatz, behavior: 'instant'});
  }
}
function reiterLeisteZeichnen(stufe){
  const leiste = $('reiterLeiste'); if(!leiste) return;
  reiterKnoepfe(leiste, stufe, stufeStand, stufeWaehlen);
}
/* Die Knoepfe einer Reiterleiste. stand(st) liefert {art, done, n} wie
   stufeStand(), waehlen(st) kommt beim Antippen. Seit dem 17.11.2026 auch
   fuer die Geschichten (geschStand, geschStufeWaehlen): dieselben Klassen,
   dieselben Texte, dasselbe Einpassen. */
function reiterKnoepfe(leiste, stufe, stand, waehlen){
  leiste.setAttribute('aria-label', t('reiter.leiste'));
  leiste.innerHTML = STUFEN.map(st => {
    const s = stand(st), an = st === stufe;
    /* Der Stand kurz als "11/31" (Pruefung vom 13.11.2026, siehe Stil
       .reiterleiste .sz); vorgelesen wird der ganze Satz. */
    /* Das Wort hinter dem Zeichen steht in .wort: passt die Zeile auch
       klein nicht, bleibt nur das Zeichen (reiterLeisteEinpassen). */
    const zeile = s.art === 'fertig' ? '✓<span class="wort"> ' + esc(t('reiter.fertig')) + '</span>'
                : s.art === 'offen'  ? s.done + '<span class="wort">/' + s.n + '</span>'
                : s.art === 'zu'     ? symbol('schloss') + '<span class="wort"> ' + esc(t('reiter.zu')) + '</span>'
                :                      esc(t('reiter.bald'));
    const sagt = st + ', ' + (s.art === 'fertig' ? t('reiter.fertig')
                            : s.art === 'offen'  ? t('reiter.stand', {done: s.done, n: s.n})
                            : s.art === 'zu'     ? t('reiter.zu') : t('reiter.bald'));
    const balken = s.n ? '<span class="sb"><i style="width:' + Math.round(s.done / s.n * 100) + '%"></i></span>' : '';
    return '<button type="button" role="tab" class="' + s.art + '" data-stufe="' + st + '" aria-selected="' + an + '"' +
           ' aria-label="' + esc(sagt) + '">' +
           '<span class="st">' + st + '</span><span class="sz"><span class="szi">' + zeile + '</span></span>' + balken + '</button>';
  }).join('');
  leiste.querySelectorAll('button').forEach(b => b.addEventListener('click', () => waehlen(b.dataset.stufe)));
  reiterLeisteEinpassen(leiste);
}
/* Zweite Pruefung vom 13.11.2026: bei 320 px oder grosser Systemschrift
   endete der Stand trotz der Kurzform in Puenktchen - "112/1…", "🔒 lock…",
   "binnenk…", genau die abgeschnittenen Zahlen, die die erste Pruefung
   verhindern sollte. Darum je Reiter messen, wie kaufkastenEinpassen():
   passt die Zeile nicht, wird sie in halben Pixeln kleiner, hoechstens
   bis 7 px. Reicht das nicht, zeigen "fertig" und "zu" nur ihr Zeichen
   (✓ bzw. Schloss) und "offen" nur die Zahl der bestandenen Level - der
   Balken darunter zeigt den Anteil, und der ganze Satz steht im
   aria-label. Abgeschnitten wird so nie eine Zahl. "Bald" hat kein
   Zeichen; dafuer ist das laengste Wort kurz (nl "volgt" statt
   "binnenkort", das bei 320 px und 130 % auch mit 7 px nicht passte).
   Gemessen wird am inneren .szi, nicht mit scrollWidth: das ist auf ganze
   Pixel gerundet und uebersah 45,7 px Text in 44,8 px.
   Mit grosser Systemschrift liefert getComputedStyle die schon
   vergroesserte Schrift; die Schleife sucht trotzdem die groesste, die
   passt, sie braucht nur ein paar Schritte mehr.
   Eine versteckte Leiste misst nichts; die Schrift laedt nach und das
   Handy wird gedreht, darum auch bei fonts.ready und resize. */
function reiterLeisteEinpassen(el){
  /* Ohne Leiste (resize und fonts.ready geben ein Ereignis oder nichts mit)
     beide, Lernpfad und Geschichten - gemessen wird nur die sichtbare. */
  const leisten = (el && el.nodeType === 1) ? [el] : [$('reiterLeiste'), $('geschReiter')];
  leisten.forEach(leiste => { if(leiste && leiste.offsetParent) leisteEinpassen(leiste); });
}
function leisteEinpassen(leiste){
  leiste.querySelectorAll('.sz').forEach(sz => {
    const innen = sz.querySelector('.szi'); if(!innen) return;
    sz.style.fontSize = ''; sz.classList.remove('nurzeichen');
    const zuBreit = () => innen.getBoundingClientRect().width > sz.getBoundingClientRect().width + 0.01;
    const kleiner = () => {
      let px = parseFloat(getComputedStyle(sz).fontSize) || 11;
      while(zuBreit() && px > 7){ px = Math.max(7, px - 0.5); sz.style.fontSize = px + 'px'; }
    };
    kleiner();
    if(zuBreit() && sz.querySelector('.wort')){ sz.style.fontSize = ''; sz.classList.add('nurzeichen'); kleiner(); }
  });
}
window.addEventListener('resize', reiterLeisteEinpassen);
if(document.fonts) document.fonts.ready.then(reiterLeisteEinpassen);
/* Die Karte ueber den Sektionen eines Reiters, der noch zu ist: wie er
   aufgeht, und der Sprung-Test, wenn der Reiter davor offen ist. Bei C1
   nur "kommt bald". Sonst leer. */
function reiterKarteZeichnen(stufe){
  const k = $('reiterKarte'); if(!k) return;
  const s = stufeStand(stufe);
  if(s.art === 'bald'){
    k.hidden = false;
    k.innerHTML = '<div class="section reiterzu"><h2>' + esc(t('reiter.bald_titel', {stufe})) + '</h2></div>';
    return;
  }
  if(s.art !== 'zu'){ k.hidden = true; k.innerHTML = ''; return; }
  const vorher = sprungVorher(stufe);
  const geht = !!vorher && stufeStand(vorher).art !== 'zu';
  k.hidden = false;
  k.innerHTML = '<div class="section reiterzu">' +
    '<div class="schloss" aria-hidden="true">' + symbol('schloss') + '</div>' +
    '<h2>' + esc(t('reiter.zu_titel', {stufe})) + '</h2>' +
    '<div class="txt">' + esc(geht ? t('reiter.zu_text', {vorher}) : t('reiter.zu_erst', {vorher})) + '</div>' +
    (geht ? '<button type="button" class="btn know" id="sprungStart"></button>' +
            '<div class="regel">' + esc(t('sprung.regel', {n: SPRUNG_FRAGEN, vorher, ab: sprungNoetig(SPRUNG_FRAGEN), stufe})) + '</div>' +
            /* Ohne Leben: der Hinweis und die Wege zu einem Leben (sprungStarten) */
            '<div id="sprungOhne"><div class="regel" id="sprungNote" role="status"></div><div id="sprungLeben"></div></div>' : '') +
    '</div>';
  const knopf = k.querySelector('#sprungStart');
  if(knopf){
    knopf.textContent = t('sprung.starten');
    knopf.addEventListener('click', () => sprungStarten(stufe));
  }
}
function showPath(){
  $('tag').textContent=t('app.tag');
  const done = CATEGORIES.filter(c=>passed.has(c.id)).length;
  const nWords = CATEGORIES.reduce((n,c)=>n+c.words.length,0);
  $('summary').textContent = t('pfad.summary',{done:done, total:CATEGORIES.length, k:ohneZa(known), n:nWords})+(ALLE_FREI?t('pfad.testmodus'):'');
  /* Ajdin am 26.09.2026: "das braucht keiner ist platzverschwendung".
     Stimmt fuer den Alltag - wie weit die laufende Sektion ist, steht
     eine Handbreit tiefer in ihrer Karte. Im Testmodus bleibt die Zeile
     stehen, denn dort haengt der Hinweis "alles freigeschaltet" daran. */
  $('summary').style.display = ALLE_FREI ? '' : 'none';
  const box=$('sections'); box.innerHTML='';
  const next = firstOpen();
  /* Die Stufen-Reiter (13.11.2026): oben die Leiste, darunter nur die
     Sektionen des gezeigten Reiters. Ist er noch zu, steht ueber ihnen die
     Karte mit dem Sprung-Test. */
  const stufe = angezeigteStufe();
  reiterLeisteZeichnen(stufe);
  reiterKarteZeichnen(stufe);
  /* Beim Zahnarzt: eine eigene Sektion am Ende, nur wenn freigeschaltet. Ihre
     Level zaehlen ab CATEGORIES.length (levelNach); firstOpen() kennt sie nicht.
     Seit 13.11.2026 im Reiter, in dem gerade gelernt wird. */
  const zaDa = zaAn() && stufe === stufeVon(next);
  const imReiter = reiterSektionen(stufe);
  const sektionenHier = zaDa ? imReiter.concat([ZA.sektion]) : imReiter;
  const zaNext = CATEGORIES.length + zaLevel().findIndex(c => !passed.has(c.id));
  /* Beim ersten Zeichnen ist die Sektion offen, in der gerade gelernt wird.
     Danach bleibt die stehen, die der Nutzer gewaehlt hat - auch nach einer
     Lektion. Erst wenn es sie nicht mehr gibt, faellt es zurueck - seit den
     Reitern auch, wenn sie in einem anderen Reiter steht. */
  const laufende = laufendeSektion(stufe);
  /* Nur beim allerersten Zeichnen vorbelegen und dann, wenn die gewaehlte
     Sektion verschwunden ist. Ein leerer Merker heisst "alle zugeklappt" -
     das ist eine Wahl des Nutzers und wird nicht ueberschrieben. */
  if(offeneSektion === null || (offeneSektion && !sektionenHier.some(s => s.id === offeneSektion)))
    offeneSektion = laufende;
  sektionenHier.forEach((s, si)=>{
    const levels = (zaDa && s === ZA.sektion)
      ? zaLevel().map((c, k) => ({c, i: CATEGORIES.length + k}))
      : CATEGORIES.map((c,i)=>({c,i})).filter(x=>x.c.sektion===s.id);
    if(!levels.length) return;
    const sdone = levels.filter(x=>passed.has(x.c.id)).length;
    const sopen = levels.some(x=>isUnlocked(x.i));
    const sec=document.createElement('div');
    /* sek1 bis sek9 geben die Farbe, eine je Sektion. Mit Rest
       gerechnet, damit eine zehnte wieder bei der ersten anfinge statt
       ohne Farbe dazustehen. */
    const auf = s.id === offeneSektion;
    sec.className='section sek'+(si % 9 + 1)+(sopen?'':' locked')+(auf?'':' zu');
    sec.dataset.sid = s.id;
    /* Der Kopf ist ein Knopf: anklickbar, mit der Tastatur erreichbar, und
       aria-expanded sagt an, was offen ist. Die Level stehen in einem
       eigenen Kasten, damit sich genau der ausblenden laesst. */
    sec.innerHTML =
      '<div class="skopf" role="button" tabindex="0" aria-expanded="'+(auf?'true':'false')+'">'+
        '<h2>'+esc(s.label)+'</h2><div class="desc">'+esc(s.beschreibung||'')+'</div>'+
        '<div class="sbar"><i style="width:'+Math.round(sdone/levels.length*100)+'%"></i></div>'+
        /* Gesperrt "bis Sektion n fertig ist": n ist die Sektion davor im
           selben Reiter. Fuer die erste eines Reiters gibt es keine davor,
           dort sagt die Karte oben, wie der Reiter aufgeht. */
        '<div class="scap">'+t('pfad.sektion_stand',{done:sdone, n:levels.length})+(sopen?'':(si > 0 ? t('pfad.sektion_gesperrt',{n:si}) : t('pfad.sektion_zu')))+'</div>'+
      '</div><div class="levels"></div>';
    const kopf = sec.querySelector('.skopf');
    kopf.addEventListener('click', ()=> sektionAufklappen(s.id));
    kopf.addEventListener('keydown', e => {
      if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); sektionAufklappen(s.id); }
    });
    const levelKasten = sec.querySelector('.levels');
    levels.forEach(({c,i})=>{
      const b=document.createElement('button');
      const d=passed.has(c.id), o=isUnlocked(i), isCur=(i===(i < CATEGORIES.length ? next : zaNext) && !d), pct=levelPct(c);
      b.className='node'+(d?' done':'')+(isCur?' current':'')+(o?'':' locked');
      const extras = GRAMMAR[c.id]?t('pfad.grammatik'):'';
      b.innerHTML = '<div class="circle">'+(d?'✓':(o?levelNummer(i):symbol('schloss')))+'</div>'+
        '<div class="txt"><div class="label">'+esc(c.label)+'<span style="font-weight:600;font-size:12px;color:var(--muted)">'+esc(extras)+'</span></div><div class="tipp">'+esc(c.tipp||'')+'</div>'+
        (o && !d ? '<div class="mini"><i style="width:'+pct+'%"></i></div>' : '')+'</div>'+
        '<div class="state">'+(d?t('zustand.bestanden'):(isCur?t('zustand.jetzt'):(o?(pct>0?pct+' %':t('zustand.offen')):t('zustand.gesperrt'))))+'</div>';
      b.addEventListener('click',()=>{
        if(!isUnlocked(i)){
          /* Das erste Level eines Reiters hat davor keins im selben Reiter -
             "Zuerst Level 0 bestehen" stand dort sonst (13.11.2026). */
          const erstes = i < CATEGORIES.length && i > 0 && reiterLevel(stufeVon(i))[0] === i;
          b.querySelector('.state').textContent = erstes ? t('pfad.erst_stufe', {stufe: stufeVon(i - 1)})
                                                         : t('pfad.erst_level', {n: levelNummer(i - 1)});
          return;
        }
        openLevel(i);
      });
      levelKasten.appendChild(b);
    });
    box.appendChild(sec);
  });
  /* Erst jetzt steht fest, welche Sektion auf welche folgt: leere werden
     oben uebersprungen. Die letzte zeigt auf sich selbst, ihr Streifen
     bleibt damit einfarbig.
     Weitergegeben wird "var(--sekN)", nicht der fertige Farbwert. Ein
     Blick mit getComputedStyle taete es nicht: der Browser loest --sek
     dort schon auf, und der Verlauf behielte beim Wechsel zwischen heller
     und dunkler Fassung unten die alte Farbe. */
  const mitFarbe = [].slice.call(box.querySelectorAll('.section'));
  const farbNr = el => (el.className.match(/sek(\d)/) || [0, '1'])[1];
  mitFarbe.forEach((el, i) => {
    const naechste = mitFarbe[i + 1] || el;
    el.style.setProperty('--sek-next', 'var(--sek' + farbNr(naechste) + ')');
  });
  geschenkNachreichen();
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
