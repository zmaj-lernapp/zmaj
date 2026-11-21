/* =================== SPRACHE =================== */
/* Die Lerninhalte kommen je nach Sprache anders vom Server zurück, deshalb
   wird beim Umschalten alles neu geholt. Was noch nicht übersetzt ist,
   schickt der Server auf Deutsch. */
/* Die Tonspur liegt als fertige Dateien in web/audio, die Zuordnung in
   web/audio/index.json. Bewusst NICHT ueber den Server: in der Handy-App
   gibt es keinen. Einmal beim Start, der Bestand ist sprachunabhaengig. */
async function ladeAudio(){
  try{
    const r = await fetch('audio/index.json', {cache:'no-cache'});
    const idx = await r.json();
    AUDIO = new Map((idx.toene||[]).map(e=>[String(e.key).toLowerCase(), e.datei]));
    /* Mitlesen (20.10.2026): nach der Datei, nicht nach dem Text - so
       gehoeren die Zeiten sicher zu genau der Aufnahme, die speak() spielt. */
    WORTZEITEN = new Map((idx.toene||[]).filter(e=>e && e.datei && Array.isArray(e.w)).map(e=>[e.datei, e.w]));
  }catch(e){ AUDIO = new Map(); WORTZEITEN = new Map(); }
  canListen = hasTTS || AUDIO.size > 0;
}
/* Woher der Inhalt kommt, haengt davon ab, wo die App laeuft.

   Am PC liest der Server die Python-Dateien bei JEDEM Aufruf frisch ein -
   eine Aenderung an vokabeln.py ist nach F5 sofort sichtbar. Diesen Weg
   wollen wir behalten, solange es ihn gibt.

   Auf dem Handy gibt es keinen Server. Dort liegt der Inhalt als fertige
   Datei daneben, erzeugt von inhalt_bauen.py. Deshalb: erst den Server
   fragen, und wenn der nicht antwortet, die Datei nehmen. */
async function holeInhalt(){
  try{
    const r = await fetch('/api/daten?sprache='+encodeURIComponent(SPRACHE));
    /* Erst auswerten, DANN merken. Auf dem Handy gibt es keinen Server,
       aber Capacitor beantwortet jeden Pfad ohne Punkt im letzten Segment
       mit der index.html und Status 200 - r.ok ist also wahr. Stand das
       Merken davor, blieb MIT_SERVER auf true, obwohl r.json() gleich am
       HTML scheitert. Beim Start korrigierte das noch /api/konto weiter
       unten; beim Sprachwechsel lief ladeDaten() erneut und niemand setzte
       zurueck. Ab da schrieb saveProgress() per POST ins Leere und meldete
       Erfolg. Gefunden am 20.09.2026, waehrend der geschlossene Test lief. */
    if(r.ok){ const d = await r.json(); if(KONTEN_AN) MIT_SERVER = true; return d; }
  }catch(e){}
  // Zweiter Versuch mit der gewuenschten Sprache, dann Englisch, dann
  // Deutsch. Englisch davor, weil die App in 177 Laendern steht: ein Handy
  // in Bosnien meldet "bs", das gibt es hier nicht - und wer kein Deutsch
  // kann, kommt mit Englisch weiter. Welche Sprache es wirklich wurde,
  // traegt ladeDaten() danach in SPRACHE nach (Feld "sprache" im Inhalt).
  for(const code of [SPRACHE, 'en', 'de']){
    try{
      const r = await fetch('inhalt/'+encodeURIComponent(code)+'.json', {cache:'no-cache'});
      if(r.ok) return await r.json();
    }catch(e){}
  }
  throw new Error('Inhalt nicht gefunden');
}
async function ladeDaten(){
  const d = await holeInhalt();
  SECTIONS = d.sektionen || []; CATEGORIES = d.kategorien; SENTENCES = d.saetze;
  GRAMMAR = d.grammatik || {}; STORIES = d.geschichten || []; DICT = d.woerterbuch || {};
  DICT_TON = d.woerterbuch_ton || {};   // eigener Ton je Bedeutung, Feld seit 21.11.2026
  /* Fehlt das Feld (Inhalt von vor dem 13.10.2026), gibt es eben keine
     Satzbau-Aufgaben. Die Namensliste der Kacheln haengt am Inhalt und wird
     beim naechsten Gebrauch neu gesammelt. */
  SATZBAU = Array.isArray(d.satzbau) ? d.satzbau : [];
  /* Auf iPhone und iPad gibt es den Teil nicht (06.11.2026). Apple: "Don't
     include any hidden, dormant, or undocumented features in your app"
     (Richtlinie 2.5.19), und der Weg dorthin, das Wort hinter der Versionszeile,
     ist dort gar nicht eingehaengt (init()). Der iOS-Bau laesst auch den Inhalt
     weg (app_bauen.ios_zahnarzt_entfernen); ZA bleibt hier trotzdem leer, damit
     ein Schalter aus dem Konto den Teil auf dem iPhone nicht aufklappt: Wer ihn
     auf Android eingeschaltet hat und sich auf dem iPhone anmeldet, hat im Stand
     zahnarzt.an. Schalter und Lernstand bleiben dabei im Stand und gehen
     unveraendert ins Konto zurueck (standAlsObjekt), auf Android ist also nichts
     verloren. Ajdin entscheidet, ob das so bleibt. */
  ZA = (!IST_IOS && d.zahnarzt && d.zahnarzt.sektion && Array.isArray(d.zahnarzt.kategorien)) ? d.zahnarzt : null;
  _kachelNamen = null;
  /* Die zwei Zwischenspeicher der Wortliste haengen an DICT und CATEGORIES und
     werden nur beim ersten Gebrauch gefuellt. Ohne dieses Leeren behielten sie
     nach einem Sprachwechsel die alte Sprache: im Level Tagesablauf stand bei
     "Ustajem" weiter "ich stehe auf" statt "je me leve", in 28 von 43 Leveln,
     bis die App geschlossen und neu geoeffnet wurde. Gefunden am 26.09.2026. */
  vokabelFormen = null; dictFormen = null;
  /* Jede Grammatikaufgabe weiss, zu welchem Level sie gehoert und die
     wievielte sie ist. Daran erkennt der Wiederholen-Topf sie wieder, auch
     nach einem Sprachwechsel. Und die Wortsuche des Topfs neu aufbauen. */
  Object.keys(GRAMMAR).forEach(id => ((GRAMMAR[id] || {}).uebungen || []).forEach((g, i) => { g._lv = id; g._nr = i; }));
  _wortNachId = null;
  _zahlKennung = null;    // die Zahlwoerter fuer zahlZiehen() (25.10.2026)
  MASCOT = new Set(d.maskottchen||[]);
  SPRACHEN = d.sprachen || []; T = d.texte || {}; UEBERSETZT = d.uebersetzt || {fertig:0, gesamt:0};
  WERBUNG_ECHT = !!d.werbung_laeuft;      // Schalter aus sprachen.py
  /* Noch einmal, nur iOS (06.11.2026): "Anzeige melden" haengt an WERBUNG_ECHT, und
     das steht erst hier. Der Aufruf in init() kommt davor, die Zeile blieb sonst aus. */
  einstellungenFuerPlattform();
  if(d.sprache) SPRACHE = d.sprache;
  if(!CATEGORIES || !CATEGORIES.length) throw new Error('keine Levels');
  if(!SECTIONS.length){ SECTIONS = [{id:'_', label:'Alle Levels', beschreibung:''}]; CATEGORIES.forEach(c=>c.sektion='_'); }
  applyTexts();
}
async function setzeSprache(code){
  if(code === SPRACHE) return;
  const vorher = SPRACHE;
  const warAuf = VIEWS.find(v => $(v).style.display !== 'none');
  SPRACHE = code;
  try{ localStorage.setItem('zmaj_sprache', code); }catch(e){}
  try{ await ladeDaten(); }catch(e){ SPRACHE = vorher; return; }
  if(!STORIES.length) $('modeStories').hidden = true;
  profilPunkt();          // sein Vorlesetext ist in der Sprache (14.11.2026)
  if(warAuf === 'settingsView') showSettings();          // dort steht die Auswahlliste
  else if(warAuf === 'profileView'){      // dort stehen die Flaggen
    if(cloudModus()) anmeldungZeigen(anmAnlass, anmModus); else zeigeAnmeldung(kontoModus);
  }
  else if(profil) showHome(); else zeigeAnmeldung('anmelden');
}
function renderLangBar(){
  const box=$('langBar'); if(!box) return;
  box.innerHTML = SPRACHEN.map(s=>'<button type="button" class="'+(s.code===SPRACHE?'on':'')+'" data-code="'+esc(s.code)+'">'+s.flagge+' '+esc(s.name)+'</button>').join('');
  box.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>setzeSprache(b.dataset.code)));
}
/* Die Sprachwahl fährt an Ort und Stelle aus. Zugeklappt steht dort die
   aktuelle Sprache mit Pfeil, aufgeklappt stehen alle untereinander.
   Zu bleibt sie nach der Wahl und beim Verlassen der Einstellungen. */
let langOffen = false;
function renderLangSel(){
  const kopf = $('langKopf'), liste = $('langListe');
  if(!kopf || !liste) return;
  const jetzt = SPRACHEN.find(s => s.code === SPRACHE) || SPRACHEN[0];
  kopf.innerHTML = '<span>' + (jetzt ? jetzt.flagge + ' ' + esc(jetzt.name) : '') + '</span>'
                 + '<span class="pfeil" aria-hidden="true">▾</span>';
  kopf.setAttribute('aria-expanded', langOffen);
  liste.hidden = !langOffen;
  liste.innerHTML = SPRACHEN.map(s =>
      '<button type="button" class="sprachzeile'+(s.code===SPRACHE?' jetzt':'')+'" data-code="'+esc(s.code)+'">'
    + s.flagge + ' ' + esc(s.name)
    + (s.code===SPRACHE ? ' <span class="haken">✓</span>' : '') + '</button>').join('');
  kopf.onclick = ()=>{ langOffen = !langOffen; renderLangSel(); };
  liste.querySelectorAll('.sprachzeile').forEach(b => b.onclick = ()=>{
    langOffen = false;
    const code = b.dataset.code;
    if(code === SPRACHE) renderLangSel(); else setzeSprache(code);
  });
  const fehlt = Math.max(0, (UEBERSETZT.gesamt||0) - (UEBERSETZT.fertig||0));
  $('langNote').textContent = fehlt ? t('set.sprache_luecke',{n:fehlt}) : '';
}

/* =================== ANSICHTEN =================== */
const VIEWS = ['profileView','pfad','storyView','levelView','kontoView','settingsView','shopView','einstufungView'];
/* Hinter dem Tor der Pflicht-Anmeldung (28.10.2026): diese Ansichten gibt
   es erst nach dem Anmelden, siehe anmeldungSperre(). Das ist das Netz
   darunter - die Einstiege (showHome, startLesson ...) fragen selbst
   vorher, damit dort weder Ton noch Uhr anlaufen. */
const TOR_ANSICHTEN = ['pfad','levelView','storyView','shopView','einstufungView'];
function showView(id){
  if(TOR_ANSICHTEN.indexOf(id) >= 0 && anmeldungSperre()) return;
  stilleBitte();          // kein Ton laeuft in die naechste Ansicht hinein
  uhrAus();               // und keine Lernzeit: Geschichte und Lektion rufen uhrAn() selbst
  /* Beim Zahnarzt: Wer die Level-Ansicht verlaesst, ist nicht mehr im Teil. Eine
     Runde aus dem Reiter Wiederholen laeuft zwar auch dort, aber danach - mit
     diesem Merker gaelten fuer sie die Regeln des Teils. Nach uhrAus(): die
     letzten Sekunden gehoeren noch zum Teil. */
  if(id !== 'levelView' && imZa()) catIdx = 0;
  VIEWS.forEach(v=>{ $(v).style.display = v===id ? 'block' : 'none'; });
  zmajeAnpassen();        // Drachen ausgeblendeter Ansichten anhalten, die sichtbaren wecken
  $('kopfLeiste').style.display = '';     // wer sie nicht will, blendet sie danach aus
  nurHerz(false);                         // Lektion, Test und Runde setzen es selbst wieder
  // Auf der Anmeldeseite faellt die leere Kopfzeile weg - siehe CSS oben
  document.body.classList.toggle('vorAnmeldung', id === 'profileView');
  /* Hier und nicht in showHome(): so stimmt die Farbe auch in den
     Einstellungen, im Laden und bei den Geschichten. */
  sektionsFarbe();
  window.scrollTo({top:0});
}

/* Nachfrage mit Ja und Nein, liefert true für Ja.
   Warum nicht confirm(): Die Systemabfrage einer WebView trägt oben den
   Hostnamen und sieht nach Browser aus, nicht nach App. Außerdem hält
   confirm() den ganzen Bildschirm an.
   Solange eine Nachfrage offen ist, verneint frageSchliessen() sie – das
   braucht die Zurück-Taste, damit sich keine zwei Fenster stapeln. */
let frageSchliessen = null;
function frage(titel, text, ja, nein){
  if(frageSchliessen) return Promise.resolve(false);
  return new Promise(fertig => {
    const kasten = document.createElement('div');
    kasten.className = 'nachfrage';
    kasten.innerHTML =
      '<div class="nachfragebox">' +
        '<h3>' + esc(titel) + '</h3>' +
        (text ? '<div class="txt">' + esc(text) + '</div>' : '') +
        '<button class="btn know" id="frJa"></button>' +
        '<button class="btn ghost" id="frNein"></button>' +
      '</div>';
    kasten.querySelector('#frJa').textContent = ja;
    kasten.querySelector('#frNein').textContent = nein;
    document.body.appendChild(kasten);
    const schliesse = w => { kasten.remove(); frageSchliessen = null; fertig(w); };
    frageSchliessen = () => schliesse(false);
    kasten.querySelector('#frJa').addEventListener('click', ()=>schliesse(true));
    kasten.querySelector('#frNein').addEventListener('click', ()=>schliesse(false));
    // Daneben tippen heißt Nein – wie überall sonst auch
    kasten.addEventListener('click', e=>{ if(e.target === kasten) schliesse(false); });
  });
}

/* Wie frage(), aber mit einem Eingabefeld. Liefert den Text oder null.
   Gebraucht wird das für den versteckten Schalter der dauerhaften
   Vollversion und seit 19.10.2026 für den der Farben (hautAlleVerdrahten).
   prompt() täte es auch, sieht aber nach Browser aus. */
function frageWort(titel, text){
  if(frageSchliessen) return Promise.resolve(null);
  return new Promise(fertig => {
    const kasten = document.createElement('div');
    kasten.className = 'nachfrage';
    kasten.innerHTML =
      '<div class="nachfragebox">' +
        '<h3>' + esc(titel) + '</h3>' +
        (text ? '<div class="txt">' + esc(text) + '</div>' : '') +
        '<input class="field" id="frWort" type="text" autocomplete="off" ' +
               'autocapitalize="none" autocorrect="off" spellcheck="false">' +
        '<button class="btn know" id="frOk">Weiter</button>' +
        '<button class="btn ghost" id="frAb">Abbrechen</button>' +
      '</div>';
    document.body.appendChild(kasten);
    const feld = kasten.querySelector('#frWort');
    const schliesse = w => { kasten.remove(); frageSchliessen = null; fertig(w); };
    frageSchliessen = () => schliesse(null);
    kasten.querySelector('#frOk').addEventListener('click', ()=>schliesse(feld.value));
    kasten.querySelector('#frAb').addEventListener('click', ()=>schliesse(null));
    // Eingabetaste wie Weiter – sonst sucht man auf dem Handy den Knopf
    feld.addEventListener('keydown', e=>{ if(e.key === 'Enter') schliesse(feld.value); });
    kasten.addEventListener('click', e=>{ if(e.target === kasten) schliesse(null); });
    // Erst nach dem Einhängen, sonst öffnet sich die Tastatur nicht
    setTimeout(()=>feld.focus(), 50);
  });
}


var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
