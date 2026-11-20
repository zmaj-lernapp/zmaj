/* =================== GESCHICHTEN-PFAD =================== */
/* ---- Stufen wie im Lernpfad (17.11.2026, Offen-Liste 7) ----
   Ajdin: "lass sie auch in 1.4 rein machen das da steht amtssprache lass
   raus es soll einfach von kinderleicht zu schwerer sein usw also nur A1,
   A2 usw". Jede Geschichte hat ihre Stufe (geschichten.py, "stufe"), und
   STORIES steht Stufe fuer Stufe, in jeder von leicht nach schwer
   (REIHENFOLGE dort). Oben stehen dieselben Reiter wie im Lernpfad
   (reiterKnoepfe), darunter nur die Geschichten des gezeigten. Eine Stufe
   ohne Geschichten (heute B2 und C1) steht da wie C1 im Lernpfad: "bald".
   Nummern und "Geschichte 2 von 6" zaehlen je Reiter, wie die Level. */
let _gStufen = null;
function geschStufen(){
  if(_gStufen && _gStufen.von === STORIES) return _gStufen;
  const stufe = [], nr = [], je = {};
  STUFEN.forEach(st => { je[st] = []; });
  let vorige = STUFEN[0];
  STORIES.forEach((s, i) => {
    /* Ohne gueltige Stufe gehoert sie zur davor, wie eine Sektion (stufenKarte) */
    const st = STUFEN.indexOf(s.stufe) >= 0 ? s.stufe : vorige;
    vorige = st; stufe[i] = st; je[st].push(i); nr[i] = je[st].length;
  });
  _gStufen = {von: STORIES, stufe, nr, je};
  return _gStufen;
}
function geschStufe(i){ return geschStufen().stufe[i] || STUFEN[0]; }
function geschImReiter(st){ return geschStufen().je[st] || []; }
/* Die naechste: die erste ungelesene, sind alle gelesen, die letzte. Sie
   ist immer frei, denn alles davor ist gelesen. */
function geschNaechste(){ const i = STORIES.findIndex(s => !read.has(s.id)); return i < 0 ? STORIES.length - 1 : i; }
/* ---- Was frei ist ----
   Eine Geschichte ist frei, wenn sie gelesen ist, wenn die davor gelesen
   ist (die erste immer) - oder wenn sie es in der Folge bis zum 17.11.2026
   war. Dort standen die zwoelf ersten nach Thema, von "Kinderbuch" bis
   "Amtssprache", dahinter die B1-Lesetexte, und frei war jede, deren
   Vorgaengerin in dieser Folge gelesen war. Mit der neuen Folge allein
   ginge manches wieder zu: "Razgovor za posao" stand auf Platz 12 und
   steht jetzt am Ende von B1 - wer bis "Kupujemo kuću" gelesen hatte,
   saehe sie gesperrt, ebenso "Naša kuća" nach "Mira i Rex". Mit der alten
   Vorgaengerin bleibt jede Geschichte frei, die vorher frei war, fuer
   jeden gespeicherten Stand, auch aus der Cloud oder einer Sicherungsdatei.
   Bis 1.3 gab es nur die ersten zwoelf, in derselben Folge wie hier. Eine
   neue Geschichte steht nicht in der Liste und geht nur der Reihe nach
   auf. tests/test_geschichten_stufen.py haelt die Liste fest. */
const GESCH_ALTE_FOLGE = ['mira', 'kuca1', 'porodica', 'pijaca', 'dan', 'grad', 'jucer', 'put', 'pismo',
  'opcina', 'kuca', 'intervju', 'b1_ljeto', 'b1_dijaspora', 'b1_vrijeme', 'b1_voz', 'b1_rafting',
  'b1_jahorina', 'b1_pita', 'b1_struja', 'b1_svadba', 'b1_posao', 'b1_stan', 'b1_doktor', 'b1_selidba',
  'b1_telefon', 'b1_rodjendan', 'b1_utakmica', 'b1_zanat', 'b1_kahva', 'b1_mejl', 'b1_zmaj'];
function storyUnlocked(i){
  const s = STORIES[i]; if(!s) return false;
  if(allesOffen() || i === 0 || read.has(s.id) || read.has(STORIES[i-1].id)) return true;
  const k = GESCH_ALTE_FOLGE.indexOf(s.id);
  return k === 0 || (k > 0 && read.has(GESCH_ALTE_FOLGE[k-1]));
}
/* Wie weit ein Reiter ist, wie stufeStand(): bald (keine Geschichten),
   fertig (alle gelesen), offen (eine ist frei) oder zu. */
function geschStand(st){
  const L = geschImReiter(st);
  if(!L.length) return {art: 'bald', done: 0, n: 0};
  const done = L.filter(i => read.has(STORIES[i].id)).length;
  const art = done === L.length ? 'fertig' : (L.some(i => storyUnlocked(i)) ? 'offen' : 'zu');
  return {art, done, n: L.length};
}
/* Geoeffnet wird der Reiter der naechsten Geschichte. Tippt man einen
   anderen an, bleibt der stehen, bis die naechste in einen anderen Reiter
   wandert (nach der letzten von A1) - wie stufeGewaehlt im Lernpfad.
   Gemerkt nur fuer diesen Start. */
let geschGewaehlt = null;   // {st, bei}: gewaehlt, als die naechste in "bei" stand
function geschAngezeigt(){
  const jetzt = geschStufe(geschNaechste());
  return (geschGewaehlt && geschGewaehlt.bei === jetzt && STUFEN.indexOf(geschGewaehlt.st) >= 0)
    ? geschGewaehlt.st : jetzt;
}
/* Wie im Lernpfad: die Leiste bleibt, wo der Finger sie getroffen hat,
   nur darunter wechselt es (leisteStehenLassen). */
function geschStufeWaehlen(st){
  leisteStehenLassen($('geschReiter'), $('storiesHome'), () => {
    geschGewaehlt = {st, bei: geschStufe(geschNaechste())};
    showStoryPath();
  });
}
/* Die Karte ueber einem Reiter, in dem noch keine Geschichte frei ist: wie
   er aufgeht. Bei einer Stufe ohne Geschichten nur "kommt bald". Sonst leer.
   Die Texte sind die der Reiter im Lernpfad. */
function geschKarteZeichnen(stufe){
  const k = $('geschKarte'); if(!k) return;
  const s = geschStand(stufe);
  if(s.art === 'bald'){
    k.hidden = false;
    k.innerHTML = '<div class="section reiterzu"><h2>' + esc(t('reiter.bald_titel', {stufe})) + '</h2></div>';
    return;
  }
  if(s.art !== 'zu'){ k.hidden = true; k.innerHTML = ''; return; }
  const vorher = STUFEN.slice(0, STUFEN.indexOf(stufe)).filter(st => geschImReiter(st).length).pop();
  k.hidden = false;
  k.innerHTML = '<div class="section reiterzu">' +
    '<div class="schloss" aria-hidden="true">' + symbol('schloss') + '</div>' +
    '<h2>' + esc(t('reiter.zu_titel', {stufe})) + '</h2>' +
    (vorher ? '<div class="txt">' + esc(t('reiter.zu_erst', {vorher})) + '</div>' : '') +
    '</div>';
}
function showStoryPath(){
  $('tag').textContent=t('gesch.titel');
  const done = STORIES.filter(s=>read.has(s.id)).length;
  $('sSummary').textContent = t('gesch.summary',{done:done, n:STORIES.length});
  /* Weg, wie die Zeile im Lernpfad. Ajdin am 26.09.2026: "das braucht
     keiner ist platzverschwendung". Wie weit man ist, steht an jeder
     Geschichte selbst: gelesen, jetzt dran oder gesperrt.
     Anders als im Lernpfad haengt hier kein Hinweis zum Testmodus dran,
     deshalb faellt sie ganz weg. Der Text bleibt gefuellt, falls die
     Zeile wiederkommt. */
  $('sSummary').style.display = 'none';
  /* Die Stufen-Reiter (17.11.2026): oben die Leiste, darunter nur die
     Geschichten des gezeigten Reiters, die Nummern je Reiter von 1. */
  const next = geschNaechste(), stufe = geschAngezeigt(), G = geschStufen();
  const leiste = $('geschReiter');
  if(leiste) reiterKnoepfe(leiste, stufe, geschStand, geschStufeWaehlen);
  geschKarteZeichnen(stufe);
  const hier = geschImReiter(stufe);
  const box=$('storyList'); box.innerHTML='<h2>'+t('gesch.titel')+'</h2><div class="desc">'+t('gesch.desc')+'</div>';
  box.style.display = hier.length ? '' : 'none';   // "bald": nur die Karte
  hier.forEach(i=>{
    const s = STORIES[i];
    const b=document.createElement('button');
    const d=read.has(s.id), o=storyUnlocked(i), isCur=(i===next && !d);
    b.className='node'+(d?' done':'')+(isCur?' current':'')+(o?'':' locked');
    const lvl = byId(s.passt_zu);
    b.innerHTML = '<div class="circle">'+(d?'✓':(o?G.nr[i]:symbol('schloss')))+'</div>'+
      /* Kein Stufen-Schildchen mehr hinter dem Titel (Ajdin 18.11.2026: "ja weg"):
         die Stufe steht schon im Reiter, unter A1 stand sonst fuenfmal "A1". */
      '<div class="txt"><div class="label"><span class="titel">'+esc(s.titel)+'</span></div><div class="tipp">'+(lvl?t('gesch.passt_zu',{label:esc(lvl.label)}):'')+'</div></div>'+
      '<div class="state">'+(d?t('gesch.gelesen'):(isCur?t('zustand.jetzt'):(o?t('zustand.offen'):t('zustand.gesperrt'))))+'</div>';
    b.addEventListener('click',()=>{
      if(!storyUnlocked(i)){
        /* Die erste eines Reiters hat davor keine im selben Reiter - dann
           wie beim ersten Level eines Reiters (pfad.erst_stufe). */
        b.querySelector('.state').textContent = geschStufe(i - 1) === stufe
          ? t('gesch.erst', {n: G.nr[i - 1]}) : t('pfad.erst_stufe', {stufe: geschStufe(i - 1)});
        return;
      }
      openStory(i);
    });
    box.appendChild(b);
  });
}
let rIdx = 0;
function openStory(i){
  if(anmeldungSperre()) return;
  rIdx=i; showView('storyView'); uhrNeu();
  setzeZurueck(t('btn.zurueck_geschichten'), ()=>{ homeMode='stories'; showHome(); });
  /* Je Reiter, wie "Level 3 von 31" (17.11.2026) */
  $('tag').textContent=t('gesch.zaehler',{i:geschStufen().nr[i] || i+1, n:geschImReiter(geschStufe(i)).length || STORIES.length});
  showStory();
  /* Zurueck nur in eine freie (17.11.2026). In der neuen Folge kann die
     davor noch zu sein: wer bis "Kupujemo kuću" gelesen hat, darf "Razgovor
     za posao" lesen (alte Folge), die davor ist "Mejl rođaku" und gesperrt.
     Vorher war die davor immer gelesen, und der Knopf fragte nicht nach. */
  $('sPrev').disabled = !(i>0 && storyUnlocked(i-1));
  $('sNext2').disabled = !(i+1<STORIES.length && storyUnlocked(i+1));
}
$('sPrev').addEventListener('click',()=>{ if(rIdx>0 && storyUnlocked(rIdx-1)) openStory(rIdx-1); });
$('sNext2').addEventListener('click',()=>{ if(rIdx+1<STORIES.length && storyUnlocked(rIdx+1)) openStory(rIdx+1); });

/* ---- Bildschirm an beim Vorlesen ----
   Eine Geschichte ist eine einzige Aufnahme, 23 bis 36 Sekunden, bei 0,5x
   doppelt so lang. Wer zuhoert, tippt nichts an - nach rund 30 Sekunden
   ging der Bildschirm aus, die App lag im Hintergrund, der
   visibilitychange-Horcher stellte den Ton ab, und die Geschichte begann
   danach von vorn. Gefunden bei der Pruefung am 06.10.2026.
   Deshalb bleibt der Bildschirm an, solange vorgelesen wird - in der Pause
   nicht, und sonst nirgends in der App. Fehlt die Schnittstelle (WebView
   vor Fassung 84) oder lehnt das Geraet ab (Stromsparmodus), bleibt alles
   wie vorher, ohne Meldung. */
let wachSperre = null, wachGewollt = false, wachAnfrage = false;
function wachHalten(an){
  wachGewollt = !!an;
  if(!an){
    const w = wachSperre; wachSperre = null;
    if(w) try{ w.release().catch(()=>{}); }catch(e){}
    return;
  }
  if(wachSperre || wachAnfrage || document.hidden) return;
  try{
    if(!navigator.wakeLock || !navigator.wakeLock.request) return;
    wachAnfrage = true;
    navigator.wakeLock.request('screen').then(w=>{
      wachAnfrage = false;
      // Waehrend der Anfrage abgestellt (Stopp, Ende, Zurueck): gleich wieder hergeben
      if(!wachGewollt){ w.release().catch(()=>{}); return; }
      wachSperre = w;
      w.addEventListener('release', ()=>{ if(wachSperre === w) wachSperre = null; });
    }).catch(()=>{ wachAnfrage = false; });
  }catch(e){ wachAnfrage = false; }
}
/* Beim Verdecken gibt das System die Sperre von selbst frei. Heute stellt
   der Horcher oben dabei auch den Ton ab, dann ist wachGewollt schon aus.
   Laeuft das Vorlesen einmal weiter, wird sie bei der Rueckkehr neu geholt. */
document.addEventListener('visibilitychange', ()=>{ if(!document.hidden && wachGewollt) wachHalten(true); });
function lookup(word, story){ const k=word.toLowerCase(); return (story.vokabeln||{})[k] || DICT[k] || null; }
function showStory(){
  const s = STORIES[rIdx]; if(!s) return;
  stilleBitte();          // beim Blättern zur nächsten Geschichte
  const lvl = byId(s.passt_zu);
  let html = '<div class="kicker" style="text-align:center">'+esc(s.stufe||'')+(lvl?t('gesch.kicker_passt',{label:esc(lvl.label)}):'')+(read.has(s.id)?t('gesch.kicker_gelesen'):'')+'</div>';
  const tokens = s.text.split(/([^\p{L}\p{M}'’-]+)/u);
  html += '<h3>'+esc(s.titel)+'</h3><div class="txt">'+tokens.map(x=> /[\p{L}\p{M}]/u.test(x) ? '<span class="w">'+esc(x)+'</span>' : esc(x)).join('')+'</div>';
  html += '<div class="bubble empty" id="rBubble" hidden></div>';
  /* "Vorlesen", Stopp und die Tempo-Leiste nur, wenn es die Geschichte als
     Aufnahme gibt (Pruefbericht 1.4, V1; Offen-Liste 6, 16.11.2026). Die
     App-Huelle hat keine Computerstimme: bei den B1-Texten ohne Aufnahme
     stand der Knopf da, und ein Tipp darauf tat nichts. Seit dem 16.11.2026
     hat jede Geschichte ihre Aufnahme; das hier faengt die naechste ab, die
     vor ihrem Ton in die App kommt. Am PC gilt dasselbe, auch mit Stimme. */
  const mitTon = !!audioDatei(s.text);
  html += '<div class="row"><button class="btn ghost" id="rTrans">'+t('gesch.zeigen')+'</button>'+
          (mitTon ? '<button class="btn again" id="rListen">'+mitSymbol('lautsprecher', t('gesch.vorlesen'))+'</button>'+
          '<button class="btn ghost" id="rStop" style="flex:0 0 54px" aria-label="'+esc(nurWort(t('gesch.stopp')))+'" hidden>'+zeichen('stopp')+'</button>' : '')+'</div>';
  if(mitTon) html += '<div class="tempo" id="rTempo"></div>';
  html += '<div class="trans" id="rTransText" hidden>'+esc(s.uebersetzung||'')+'</div>';
  html += '<div class="fragenblock" id="rQ"></div>';
  $('rBody').innerHTML = html;
  $('rBody').querySelectorAll('.w').forEach(w=>w.addEventListener('click',()=>{
    $('rBody').querySelectorAll('.w.on').forEach(x=>x.classList.remove('on')); w.classList.add('on');
    const wort = w.textContent;
    const bed = lookup(wort, s); const b=$('rBubble');
    b.hidden = false;
    b.className='bubble'; b.innerHTML = '<b>'+esc(wort)+'</b> '+(bed?esc(bed):'<span style="color:var(--muted)">'+t('gesch.kein_eintrag')+'</span>');
    /* Jeder Tipp schafft erst Ruhe. Sonst hinge es vom Wort ab, ob die
       laufende Geschichte abbricht oder weiterlaeuft - und das kann man
       sich nicht merken.
       Die Stelle wird aber vorher gesichert: stilleBitte() setzt
       currentTime auf null, und ohne diese zwei Zeilen begaenne die
       Geschichte danach wieder von vorn. */
    if(laeuftVor && spieler.src && spieler.currentTime > 0)
      geschichteStelle = {datei: spieler.src, sekunde: spieler.currentTime};
    stilleBitte();
    /* Das angetippte Wort gleich einzeln vorsprechen. Nur wenn es dafuer
       wirklich etwas gibt: fuer rund vier von zehn Woertern im Text liegt
       eine Aufnahme bereit, und eine Computerstimme hat die App-Huelle
       nicht. Sonst bliebe es stumm, und das Antippen fuehlte sich kaputt an
       - deshalb steht der Lautsprecher auch nur dann dabei. Er ist ein
       echter Knopf: nochmal hoeren, ohne das Wort im Text neu zu treffen. */
    if(hoerbar(wort)){
      /* task.hoeren, NICHT gesch.vorlesen: dieser Knopf spricht ein einzelnes
         Wort. Sobald eine Sprache aus dem Vorlese-Knopf "Hör die Geschichte"
         macht, stünde hier sonst etwas Falsches. */
      b.insertAdjacentHTML('beforeend', '<button type="button" class="wortton" aria-label="'+esc(nurWort(t('task.hoeren')))+'">'+symbol('lautsprecher')+'</button>');
      // Ueber den spieler wie die ganze Geschichte, nie ueber WebAudio (26.10.2026),
      // aber mit normalem Tempo: das gemerkte gilt nur beim Vorlesen (05.11.2026)
      b.querySelector('.wortton').addEventListener('click', ()=>{ stilleBitte(); sprichMitSpieler(wort); });
      sprichMitSpieler(wort);
    }
    /* Die Blase sitzt unten im Bild fest (V2, 14.11.2026, CSS bei
       .bubble). Wer ein Wort ganz unten antippt, haette es sonst unter ihr.
       Dann die Seite gerade so weit schieben, dass es darueber steht - sonst
       bleibt sie stehen. Erst hier, wenn der Lautsprecher schon drin ist:
       er kann die Blase hoeher machen. */
    try{
      const wr = w.getBoundingClientRect(), br = b.getBoundingClientRect();
      if(wr.bottom > br.top - 6 && wr.top < br.bottom)
        scrollBy({top: (wr.bottom - br.top + 12) * rectFaktor(), behavior: kachelnRuhig() ? 'auto' : 'smooth'});
    }catch(e){}
  }));
  $('rTrans').addEventListener('click',()=>{ const box=$('rTransText'); box.hidden=!box.hidden; $('rTrans').textContent = box.hidden?t('gesch.zeigen'):t('gesch.verbergen'); });
  /* Der grosse Knopf macht drei Dinge nacheinander: vorlesen, anhalten,
     weiterlesen. Angehalten wird nicht zurueckgesetzt - es geht da weiter,
     wo es aufgehoert hat. Ajdin am 18.09.2026.
     Ganz abbrechen kann man mit dem kleinen Knopf daneben; der erscheint
     erst, wenn es etwas abzubrechen gibt. */
  geschichteStelle = null;   // neue Geschichte, alte Stelle gilt nicht mehr
  const knopfVor = $('rListen'), knopfStop = $('rStop');
  const wiederVorlesen = ()=>{
    knopfVor.innerHTML = mitSymbol('lautsprecher', esc(t('gesch.vorlesen')));
    knopfVor.classList.remove('laeuft');
    knopfStop.hidden = true;
    wachHalten(false);   // Stopp, Ende, Wort angetippt, Ansicht verlassen, verdeckt
    /* Auch wenn das System den Ton von aussen anhaelt (Anruf, Kopfhoerer):
       dann kommt kein stilleBitte(), nur dieser Rueckruf. (20.10.2026) */
    mitlesenAus();
  };
  // Ohne Aufnahme gibt es beide Knoepfe nicht (mitTon oben, 16.11.2026)
  if(mitTon) knopfVor.addEventListener('click',()=>{
    if(pausiert){                      // angehalten -> an derselben Stelle weiter
      if(tonWeiter()){ knopfVor.innerHTML = zeichen('pause') + ' ' + esc(t('gesch.pause')); knopfVor.classList.add('laeuft'); wachHalten(true); }
      return;
    }
    if(laeuftVor){                     // laeuft -> anhalten, Stelle merken
      if(tonPause()){ knopfVor.innerHTML = mitSymbol('play', esc(t('gesch.weiterlesen'))); knopfVor.classList.remove('laeuft'); wachHalten(false); }
      else stilleBitte();              // nichts zum Anhalten da: sauber abstellen
      return;
    }
    stilleBitte();                     // ein angetipptes Wort koennte noch laufen
    /* Wurde fuer ein Wort unterbrochen, geht es dort weiter statt von vorn.
       Die Stelle gilt nur fuer dieselbe Aufnahme - nach einem Wechsel der
       Geschichte waere sie sinnlos. */
    const weiterAb = geschichteStelle;
    geschichteStelle = null;
    laeuftVor = wiederVorlesen;
    knopfVor.innerHTML = zeichen('pause') + ' ' + esc(t('gesch.pause')); knopfVor.classList.add('laeuft');
    knopfStop.hidden = false;
    /* Die Marke unterscheidet Durchlaeufe: ein verspaeteter Rueckruf aus
       einem laengst abgestellten Lauf darf den naechsten nicht abwuergen. */
    const meinLauf = tonMarke;
    /* Zur gemerkten Sekunde springen, sobald die Aufnahme bereitsteht.
       speak() gibt kein Versprechen zurueck, auf das man warten koennte -
       deshalb ueber das Ereignis. loadedmetadata kommt, bevor der erste
       Ton hoerbar ist; bei playing haette man den Anfang schon gehoert.
       {once:true} raeumt den Horcher selbst weg, auch wenn nichts folgt.
       Geprueft wird beides: derselbe Durchlauf und dieselbe Datei. */
    if(weiterAb) spieler.addEventListener('loadedmetadata', ()=>{
      if(meinLauf === tonMarke && spieler.src === weiterAb.datei)
        try{ spieler.currentTime = weiterAb.sekunde; }catch(e){}
    }, {once:true});
    /* Vor speak(): endet der Ton sofort (keine Aufnahme, keine Stimme),
       gibt wiederVorlesen() die Sperre gleich wieder frei. */
    wachHalten(true);
    // nie ueber WebAudio: das Mitlesen liest spieler.currentTime (26.10.2026).
    // Die einzige Stelle, die das gemerkte Tempo mitgibt (05.11.2026).
    sprichMitSpieler(s.text, ()=>{ if(meinLauf === tonMarke && laeuftVor === wiederVorlesen) stilleBitte(); }, tempo);
    /* Mitlesen (20.10.2026). Ohne passende Wortzeiten oder ohne Aufnahme
       (Computerstimme) bleibt der Text einfach ohne Markierung. */
    mitlesenStart(audioDatei(s.text), $('rBody').querySelectorAll('.txt .w'));
  });
  /* Der kleine Knopf bricht wirklich ab - dann ist auch die gemerkte
     Stelle hinfaellig, sonst spraenge der naechste Start mittenhinein. */
  if(mitTon) knopfStop.addEventListener('click', ()=>{ geschichteStelle = null; stilleBitte(); });
  tempoLeiste('rTempo', true);   // ohne Aufnahme gibt es #rTempo nicht, dann tut sie nichts
  showStoryQ(s, 0, 0);
}
function showStoryQ(s, qi, right){
  ansagen('');   // die Ansage der vorigen Frage nicht in diese hineinlaufen lassen (17.10.2026)
  const box=$('rQ'); const fragen=s.fragen||[];
  if(!fragen.length){ box.innerHTML=''; return; }
  if(qi>=fragen.length){
    const all = right===fragen.length;
    if(all){ if(!read.has(s.id)){ read.add(s.id); wann['gs:'+s.id] = today(); } markToday(); zaehle('gesch'); sound('done'); }
    const erfolgLob = erfolgZeile();   // Erfolge (13.11.2026): hakt ab, also vor dem Speichern
    saveProgress();   // auch bei einem Fehler: die Fragen sind beantwortet
    cloudNachLernen();   // 17.11.2026, siehe dort
    /* Die gruenen Zeilen fuer erledigte Tagesaufgaben - derselbe Fehler, der
       am 18.09.2026 fuer die Lektion und danach fuer den Vokabeltest behoben
       wurde, hier aber nicht: Wer beim Lesen 'gesch', 'auf', 'ric' oder ueber
       die Uhr 'zeit' fertig machte, bekam die Muenzen ohne ein Wort - und die
       Muenzleiste ist ausserhalb der Startseite gar nicht zu sehen. Schlimmer:
       questZeilen() LEERT questFrisch, und weil es hier nie lief, blieb der
       Eintrag liegen und wurde auf dem Ergebnisschirm der NAECHSTEN Lektion
       als frisch geschafft gefeiert, obwohl er zur Geschichte davor gehoerte.
       questZeilen() darf nur einmal je Ergebnisschirm laufen - deshalb hier in
       eine Variable und unten nur noch eingesetzt. Gefunden am 26.09.2026. */
    const questLob = questZeilen();
    if(questLob) setTimeout(()=>sound('quest'), 850);   // nach der Fanfare, nicht darueber
    const hasNext = rIdx+1 < STORIES.length;
    box.innerHTML='<div class="ergebnis-titel">'+t('gesch.fragen')+'</div>'+(all?'<div class="celebrate"><div class="zmaj cheer">'+zmaj('cheer')+'</div></div>':'')+
      '<div class="feedback '+(all?'ok':'no')+'" style="text-align:center">'+t('gesch.ergebnis',{r:right, n:fragen.length})+(all?mitKonfetti(t('gesch.geschafft')):t('gesch.nochmal_lesen'))+'</div>'+erfolgLob+
      '<div class="row"><button class="btn ghost" id="rAgain">'+t('gesch.fragen_nochmal')+'</button>'+(all && hasNext ? '<button class="btn know" id="rGoNext">'+t('gesch.naechste')+'</button>' : '')+'</div>'+
      /* Wie beim Vokabeltest: eine leise Reihe mit dem Weg heraus. Hier
         gab es bisher gar keinen - nur "nochmal" und "naechste". */
      '<div class="row schmal"><button class="btn ghost" id="rHome">'+t('btn.zurueck_geschichten')+'</button></div>';
    $('rAgain').addEventListener('click',()=>showStoryQ(s,0,0));
    $('rHome').addEventListener('click',()=>{ homeMode='stories'; showHome(); });
    const n=$('rGoNext'); if(n) n.addEventListener('click',()=>openStory(rIdx+1));
    $('sNext2').disabled = !(hasNext && storyUnlocked(rIdx+1));
    /* Gelesen kann auch die davor aufgehen: nach "Moj dan" ist "U gradu"
       frei (alte Folge), "Jučer" davor erst, wenn "U gradu" gelesen ist. */
    $('sPrev').disabled = !(rIdx>0 && storyUnlocked(rIdx-1));
    return;
  }
  const q=fragen[qi];
  box.innerHTML='<div class="kicker" style="text-align:center">'+t('gesch.frage_n',{i:qi+1, n:fragen.length})+'</div><div class="ex-q" style="text-align:center">'+esc(q.frage)+'</div>'+
    '<div class="options '+(q.optionen.every(o=>o.length<=14) ? 'waagrecht' : 'one')+'" id="rOpts"></div>'+
    '<div class="feedback" id="rFb" style="text-align:center"></div>';
  // Kein eigener Weiter-Knopf mehr: nach der Antwort bringt ein Tippen
  // irgendwo im Fragenfeld die nächste Frage – genau wie in der Lektion.
  // Der Horcher sitzt nur auf dem Fragenfeld, damit das Nachschlagen eines
  // Wortes im Text darüber nicht versehentlich weiterblättert.
  /* Die Rueckmeldung wie in der Lektion: sichtbar in #rFb und angesagt.
     Bis zum 17.10.2026 stand sie nur da - wer mit Screenreader antwortete,
     hoerte nach 900 ms nur "Weiter" und erfuhr nie, ob es richtig war. Die
     Antworten sind in der Sprache der App, also nicht als Bosnisch markiert. */
  renderChoice($('rOpts'), shuffle(q.optionen.map(o=>({k:o}))), q.richtig, o=>o.k, r=>{
    rueckmeldungZeigen($('rFb'), r?'ok':'no', r?'task.richtig':'task.falsch', q.richtig, false);
    uhrTakt(true); zaehle('auf'); if(r) zaehle('ric');
    weiterBeiTipp('rQ', ()=> showStoryQ(s, qi+1, right+(r?1:0)));
  });
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
