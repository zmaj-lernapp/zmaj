/* =================== LEVEL =================== */
function openLevel(i){
  if(anmeldungSperre()) return;
  // Beim Blaettern von Level zu Level bleibt die Stelle von vorher, siehe showHome()
  if(!sichtbar('levelView')) pfadStelle = sichtbar('pfad') && homeMode === 'words' ? window.scrollY : 0;
  catIdx=i; showView('levelView');
  setzeZurueck(t('btn.zurueck_pfad'), ()=>{ homeMode='words'; showHome(); });
  $('tag').textContent=t('level.zaehler',{i:levelNummer(i), n:levelAnzahl(i)});   // je Reiter, 13.11.2026
  showLevelHome();
  kartenNachreichen();
}
/* Lektion, Test und Level-Uebersicht sind Unteransichten INNERHALB von
   levelView und laufen nicht ueber showView(). Deshalb hier eigens
   abstellen - sonst spricht das letzte Wort der Lektion (bis zu 3,7 s)
   auf der Uebersicht zu Ende. Das war der gemeldete Fall. */
/* Lektion, Test und Wiederholen-Runde laufen in levelView, aber nicht ueber
   showView(). Darum schalten die drei Starts den Kopf selbst um, und
   showLevelHome() und showView() schalten ihn zurueck - alle Wege hinaus
   (Ergebnis, Abbrechen, Zurueck-Taste, topfSeite) gehen durch eine der
   beiden. */
/* updNachreichen(): Update-Leiste und Googles Update-Fenster warten, bis
   keine Lektion mehr laeuft. Jeder Weg hinein und hinaus fuehrt hier
   vorbei, showView() eingeschlossen - deshalb haengt es hier. 10.10.2026 */
function nurHerz(an){ document.body.classList.toggle('nurHerz', !!an); if(an) renderLives(); else kopfEng(); updNachreichen(); }
function showLevelHome(){
  stilleBitte();
  nurHerz(false);
  $('lesson').style.display='none'; $('test').style.display='none'; $('levelHome').style.display='block';
  // Beide Aufgabenfelder leeren. renderTask() sucht seine Knöpfe mit
  // getElementById, und die ids (xCheck, xIn, xOpts …) sind in Lektion und
  // Test dieselben. Bliebe die abgebrochene Lektion stehen, würde der Test
  // seine Knöpfe an die alten Felder hängen und auf nichts mehr reagieren.
  $('lBody').innerHTML=''; $('tBody').innerHTML='';
  /* Ebenso die kleinen Drachen von Lektion und Test (19.10.2026): #lesson
     und #test sind keine Ansichten im Sinne von zmajRuht(), ihre
     Lottie-Drachen liefen hinter der Uebersicht unsichtbar in Schleife
     weiter - nach Abbruch, Ergebnis und Zurueck-Taste. Leer geraeumt baut
     der Beobachter unter mountZmaj() sie ab; startLesson(), startTopf()
     und startTest() setzen sie neu ein. */
  $('zmajLesson').innerHTML=''; $('zmajTest').innerHTML='';
  uhrAus();
  const c = cur(); const s = imZa() ? ZA.sektion : SECTIONS.find(x=>x.id===c.sektion);
  /* Unter dem Titel die Sektion ohne ihren Namen, seit 13.11.2026 mit dem
     Reiter davor ("A2 · Sektion 1"): die Nummern zaehlen je Reiter. */
  $('lvTitle').innerHTML = t('level.titel',{i:levelNummer(catIdx), label:esc(c.label)})+'<small>'+esc(s ? (imZa() ? s.label.replace(/ /g, ' ') : stufeVon(catIdx) + ' · ' + s.label.replace(/ ·.*$/,'')) : '')+'</small>';
  $('lvTipp').textContent = c.tipp || '';
  const basis = $('lvBasis'); basis.innerHTML='';
  if(c.baut_auf && c.baut_auf.length){
    basis.appendChild(document.createTextNode(t('level.baut_auf')));
    c.baut_auf.forEach(id=>{ const k=byId(id); if(k){ const sp=document.createElement('span'); sp.textContent=k.label; basis.appendChild(sp); } });
  }
  updateProgress(); renderLives();
  const L = GRAMMAR[c.id];
  $('gramBox').style.display = L ? 'block' : 'none';
  if(L) $('gBody').innerHTML = renderExplain(L.erklaerung||[]);
  const zeilen = wortzeilen(c);
  $('wordBox').hidden = zeilen.length === 0;
  /* Die einzige Stelle, an der alle Wörter eines Levels ruhig nebeneinander
     stehen – und ausgerechnet dort konnte man keines anhören. Aufgedeckte
     Zeilen bekommen jetzt einen Lautsprecher, sofern es dafür etwas zu hören
     gibt. */
  $('wordList').innerHTML = zeilen.map(z=>
      '<div><span class="de">'+esc(z.de)+'</span>'
    + '<span class="bs'+(z.kann?'':' zu')+'">'+(z.kann ? esc(z.bs) : '?')+'</span>'
    + (z.kann ? '<span class="wortende"><span class="ok">✓</span>'
                + (hoerbar(eigenerTon(z.bs, z.ton)) ? '<button type="button" class="wortton" data-ton="'+esc(eigenerTon(z.bs, z.ton))+'" aria-label="'+esc(nurWort(t('task.hoeren')))+'">'+symbol('lautsprecher')+'</button>' : '')
                + '</span>'
              : '')
    + '</div>').join('');
  $('wordList').querySelectorAll('.wortton').forEach(b=>b.addEventListener('click', e=>{
    e.stopPropagation(); stilleBitte(); speak(b.dataset.ton);   // eigener Ton je Bedeutung (21.11.2026)
  }));
  $('navPrev').disabled = catIdx===levelAnfang();
  $('navNext').disabled = !(catIdx+1<levelEnde() && isUnlocked(catIdx+1));
}
function updateProgress(){
  const c=cur(); const words=c.words;
  const done = words.filter(w=>known.has(w.id)).length;
  const pct = levelPct(c);
  $('fill').style.width = pct+'%';
  $('capText').textContent = t('level.cap',{done:done, n:words.length});
  $('capPct').textContent = pct+'%';
  lebenWege();                       // ohne Leben die zwei Wege zeigen, sonst wegnehmen
  const marke = $('mark80');
  marke.hidden = TEST_FREI_AB >= 100;
  marke.style.left = TEST_FREI_AB + '%';
  marke.title = t('level.test_marke',{p:TEST_FREI_AB});
  const bt=$('btnTest'), allowed=testAllowed(c);
  testKnopf(livesNow());
  if(passed.has(c.id)){ bt.textContent=t('level.test_bestanden'); }
  else if(allowed) bt.innerHTML = mitSymbol('ziel', esc(t('level.test')));
  else bt.innerHTML = mitSymbol('schloss', esc(t('level.test_gesperrt',{p:TEST_FREI_AB})));
  $('lvNote').textContent = passed.has(c.id) ? t('level.note_bestanden') :
    (allowed ? t('level.note_frei',{a:TEST_BESTANDEN_AB, b:TEST_FRAGEN}) : t('level.note_zu',{p:TEST_FREI_AB}));
}
$('navPrev').addEventListener('click',()=>{ if(catIdx>levelAnfang()) openLevel(catIdx-1); });
$('navNext').addEventListener('click',()=>{ if(catIdx+1<levelEnde() && isUnlocked(catIdx+1)) openLevel(catIdx+1); });

// Jede Sprache setzt ihre eigenen Anführungszeichen: auf, zu.
const ZITAT = {
  de:['„','“'], en:['“','”'], tr:['“','”'], sv:['”','”'],
  nl:['‘','’'], nb:['«','»'], da:['»','«'], fr:['«','»']
};
// Setzt Text in die Anführungszeichen der aktuellen Sprache.
// Französisch bekommt dabei sein Leerzeichen innen.
function inZitat(text){
  const [auf, zu] = ZITAT[SPRACHE] || ZITAT.de;
  const luft = SPRACHE==='fr' ? ' ' : '';
  return auf+luft+text+luft+zu;
}

// Was zwischen den Anführungszeichen der aktuellen Sprache steht, wird fett.
function fettZitate(text){
  const [auf, zu] = ZITAT[SPRACHE] || ZITAT.de;
  const e = s => s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  // Leerzeichen direkt hinter « und vor » bleiben außerhalb der Fettschrift
  const re = new RegExp(e(auf)+'(\\s*)([^'+e(zu)+']*?)(\\s*)'+e(zu),'g');
  return text.replace(re, auf+'$1<b>$2</b>$3'+zu);
}

function renderExplain(parts){
  return parts.map(p=>{
    if(typeof p==='string') return '<p>'+fettZitate(esc(p))+'</p>';
    if(p.tabelle){
      const [head, ...rows] = p.tabelle;
      return '<div class="tablewrap"><table><tr>'+head.map(h=>'<th>'+esc(h)+'</th>').join('')+'</tr>'+
        rows.map(r=>'<tr>'+r.map(c=>'<td>'+esc(c)+'</td>').join('')+'</tr>').join('')+'</table></div>';
    }
    return '';
  }).join('');
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
