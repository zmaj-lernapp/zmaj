/* ---- Einstellungen: Töne, Vibration, Animationen ---- */
const pref = (k, def) => { try{ const v=localStorage.getItem(k); return v===null ? def : v==='an'; }catch(e){ return def; } };
let soundOn = pref('zmaj_sound', true), haptikOn = pref('zmaj_haptik', true), animOn = pref('zmaj_anim', true);
try{ getragen = localStorage.getItem('zmaj_getragen') || ''; }catch(e){}
/* Auf iOS gibt es navigator.vibrate nicht (WebKit kennt es nicht), der
   Schalter taete dort nichts - er ist dort ausgeblendet (Entscheidung 13,
   30.10.2026, siehe einstellungenFuerPlattform()). */
const canBuzz = !IST_IOS && 'vibrate' in navigator;
function buzz(p){ if(haptikOn && canBuzz){ try{ navigator.vibrate(p); }catch(e){} } }
function applyAnim(){
  document.body.classList.toggle('no-anim', !animOn);
  zmajeAnpassen();   // der Schalter gilt auch fuer den Drachen (07.10.2026)
}
let actx = null;
/* tonNull: waehrend sound() die gemeinsame Startzeit aller Toene eines
   Klangs auf der Uhr von actx. rueckTon: welcher Rueckmeldeton ('ok'/'no')
   zuletzt angestimmt wurde und wann - auf ihn setzt spaeterSprechen() das
   Wort nach einer Antwort (26.10.2026, siehe "Wann das Wort kommt, Teil 2").
   Bis dahin las jeder tone() die Uhr selbst, die Toene eines Klangs
   konnten also um einen Rechenblock (2,7 ms) auseinanderliegen. */
let tonNull = null, rueckTon = null;
/* Lautstärke: Die Vokabeln kommen als fertige Aufnahme und damit in voller
   Höhe. Dagegen waren die berechneten Töne mit 0,18 deutlich zu leise –
   man hörte das Wort, aber kaum, ob es richtig war. Jetzt 0,38. Ein
   Sägezahn trägt bei gleicher Höhe mehr Energie als ein Sinus, deshalb
   bleibt der Fehlton darunter. */
function tone(freq, start, dur, type='sine', gain=0.38){
  const o=actx.createOscillator(), g=actx.createGain();
  o.type=type; o.frequency.value=freq; g.gain.value=0;
  o.connect(g); g.connect(actx.destination);
  const ab=(tonNull !== null ? tonNull : actx.currentTime)+start;
  g.gain.setValueAtTime(0,ab); g.gain.linearRampToValueAtTime(gain,ab+0.01); g.gain.exponentialRampToValueAtTime(0.0001,ab+dur);
  o.start(ab); o.stop(ab+dur+0.05);
}
function sound(kind){
  if(kind==='ok') buzz(15); else if(kind==='no') buzz([60,40,60]); else if(kind==='done') buzz([30,30,30,30,80]);
  else if(kind==='anziehen' || kind==='ablegen') buzz(12);
  else if(kind==='kauf') buzz([12,40,18]);
  else if(kind==='quest') buzz([20,50,20,50,70]);
  else if(kind==='wegmarke') buzz([40,60,40,60,40,60,180]);
  if(!soundOn) return;
  try{
    if(!tonKontext()) return;
    /* iPhone: ein Kontext, dessen Uhr trotz 'running' steht, wird
       geschlossen; der naechste Tipp legt einen neuen an (siehe "Ton im
       Fingertipp", 15.11.2026). */
    if(IST_IOS && tonUhrLesen() === 'tot'){ tonWeg('sound'); return; }
    /* Fortsetzen bei jedem Zustand ausser 'running' und 'closed', also auch
       bei WebKits 'interrupted' (iPhone: Anruf, Siri, Heimknopf). Bis zum
       15.11.2026 nur bei 'suspended' - nach einer Unterbrechung blieben die
       Pieptoene dann fuer immer stumm. Android kennt nur suspended, running
       und closed, dort ist es dasselbe wie vorher. Die Ablehnung wird
       gefangen statt als Fehler in der Konsole zu landen. */
    if(actx.state !== 'running' && actx.state !== 'closed'){
      const p = actx.resume(); if(p && p.catch) p.catch(()=>{});
    }
    tonNull = actx.currentTime;
    if(kind==='ok'){ tone(660,0,0.12); tone(880,0.11,0.18); }
    else if(kind==='no'){ tone(200,0,0.22,'sawtooth',0.26); tone(160,0.12,0.25,'sawtooth',0.22); }
    else if(kind==='done'){ tone(523,0,0.14); tone(659,0.13,0.14); tone(784,0.26,0.14); tone(1047,0.39,0.35); }
    /* Laden: an- und ablegen. Bewusst weich (Dreieck statt Sinus, leiser) und
       kuerzer als das Lob nach einer richtigen Antwort - im Laden wird nichts
       bewertet, es wird nur etwas umgesteckt. Anziehen geht hinauf und endet
       mit einem kleinen Funkeln, Ablegen geht hinunter und laesst es weg. */
    else if(kind==='anziehen'){ tone(330,0,0.08,'triangle',0.30); tone(494,0.05,0.11,'triangle',0.24); tone(988,0.13,0.09,'sine',0.13); }
    else if(kind==='ablegen'){ tone(494,0,0.08,'triangle',0.26); tone(330,0.05,0.13,'triangle',0.22); }
    /* Laden: gekauft. Bis zum 27.09.2026 klang ein Kauf wie eine richtige
       Antwort - es war derselbe 'ok'-Ton. Ajdin beim Durchsehen: "beim laden
       kategorie auffuellen ... hat noch den alten sound nicht den sound von
       den anderen kategorien". Beim Zierrat fiel es weniger auf, weil man
       danach auf Tragen tippt und den weichen Ladenton hoert; beim
       Auffuellen bleibt es beim Piepen.
       Der Kauf gehoert in dieselbe Familie wie Anziehen und Ablegen, darf
       aber etwas mehr sein - es kostet Muenzen. Also ein Dreiklang hinauf
       auf dem Dreieck, leiser als das Lob nach einer Lektion, und am Ende
       zwei Funkeln wie bei einer Muenze. */
    else if(kind==='kauf'){ tone(523,0,0.08,'triangle',0.28); tone(659,0.06,0.09,'triangle',0.26);
                            tone(784,0.13,0.13,'triangle',0.24);
                            tone(1568,0.19,0.10,'sine',0.11); tone(2093,0.25,0.12,'sine',0.08); }
    /* Tagesaufgabe erledigt. Musste sich vom Lektionsende ('done') deutlich
       unterscheiden - die beiden kommen oft kurz hintereinander. 'done' ist
       ein breiter Dreiklang von unten (523-1047), dieser hier liegt hoeher,
       laeuft schneller und endet mit einem Funkeln. */
    else if(kind==='quest'){ tone(784,0,0.10,'triangle',0.30); tone(1047,0.09,0.10,'triangle',0.30);
                             tone(1319,0.18,0.22,'triangle',0.26); tone(1976,0.24,0.14,'sine',0.12); }
    /* Wegmarke: die groesste Sache, die die App zu feiern hat. Sie faengt an
       wie das Lektionsende (523-1047), geht dann aber weiter hinauf und
       endet auf einem Dreiklang, der stehen bleibt. */
    else if(kind==='wegmarke'){ tone(523,0,0.13); tone(659,0.11,0.13); tone(784,0.22,0.13);
                                tone(1047,0.33,0.15); tone(1319,0.45,0.50);
                                tone(1568,0.50,0.46,'triangle',0.20);
                                tone(2093,0.56,0.40,'sine',0.11); }
    if(kind==='ok' || kind==='no') rueckTon = {art: kind, zeit: tonNull, um: performance.now()};
  }catch(e){}
  tonNull = null;
}
function wireSwitch(id, get, set){
  const b=$(id); b.setAttribute('aria-checked', get());
  b.addEventListener('click',()=>{ set(!get()); b.setAttribute('aria-checked', get()); });
}
wireSwitch('swSound', ()=>soundOn, v=>{ soundOn=v; try{localStorage.setItem('zmaj_sound', v?'an':'aus');}catch(e){} if(v) sound('ok'); });
wireSwitch('swHaptik', ()=>haptikOn, v=>{ haptikOn=v; try{localStorage.setItem('zmaj_haptik', v?'an':'aus');}catch(e){} if(v) buzz(30); });
wireSwitch('swAnim', ()=>animOn, v=>{ animOn=v; try{localStorage.setItem('zmaj_anim', v?'an':'aus');}catch(e){} applyAnim(); });

/* ---------- Aussehen: hell, dunkel oder wie das Geraet ----------
   Der Stil konnte das schon, es fehlte nur die Wahl:
     ohne data-theme     prefers-color-scheme entscheidet, also das Handy
     data-theme="light"  hell, auch auf einem dunkel gestellten Handy
     data-theme="dark"   dunkel, auch auf einem hell gestellten
   Angewandt wird es zweimal: im kleinen Skript im Kopf der Seite, damit beim
   Start nichts aufblitzt, und hier, wenn jemand die Wahl aendert. */
let themeWahl = 'geraet';
try{
  const w = localStorage.getItem('zmaj_theme');
  if(w === 'hell' || w === 'dunkel') themeWahl = w;
}catch(e){}

function themeAnwenden(blenden){
  const wurzel = document.documentElement;
  if(themeWahl === 'hell')        wurzel.dataset.theme = 'light';
  else if(themeWahl === 'dunkel') wurzel.dataset.theme = 'dark';
  else delete wurzel.dataset.theme;
  const leiste = $('themeWahl');
  if(leiste) [].slice.call(leiste.children).forEach(b => {
    b.setAttribute('aria-checked', b.dataset.themeWahl === themeWahl ? 'true' : 'false');
  });
  /* Beim Start nicht blenden - da gibt es keine alte Fassung, aus der man
     herueberblenden koennte, und der Kopf der Seite hat die richtige schon
     gesetzt. Nur ein Tippen blendet. */
  if(blenden) weichUmblenden();
}


(function(){
  const leiste = $('themeWahl');
  if(!leiste) return;
  leiste.addEventListener('click', e => {
    const knopf = e.target.closest('button[data-theme-wahl]');
    if(!knopf || knopf.dataset.themeWahl === themeWahl) return;
    themeWahl = knopf.dataset.themeWahl;
    /* 'geraet' ist der Standard und wird nicht gespeichert, sondern
       geloescht - dann gilt wieder, was das Handy sagt, auch wenn wir die
       Schluesselnamen irgendwann aendern. */
    try{
      if(themeWahl === 'geraet') localStorage.removeItem('zmaj_theme');
      else localStorage.setItem('zmaj_theme', themeWahl);
    }catch(e){}
    themeAnwenden(true);
    sound('ok');
    buzz(20);
  });
  themeAnwenden(false);
})();
/* Der Werbeschalter ist UNSERER und wirkt sofort, in beide Richtungen.
   Er erzwingt npa=1, also unpersonalisierte Anzeigen - auch dann, wenn bei
   Google zugestimmt wurde. Strenger als die Einwilligung darf man sein,
   lockerer nicht.

   Warum er Googles Fenster NICHT spiegelt, obwohl das der Wunsch war: aus
   Googles Antwort laesst sich gar nicht ablesen, ob der Nutzer zugestimmt
   hat. Das Plugin liefert `status`, `canRequestAds` und
   `privacyOptionsRequirementStatus` - und canRequestAds ist in beiden
   Faellen wahr, denn ohne Zustimmung kommen eben unpersonalisierte
   Anzeigen. Die feine Antwort steckt in Googles TCF-Speicher, an den die
   App nicht herankommt. Ein Schalter, der Googles Fenster nachfaehrt,
   braucht also eine eigene native Erweiterung.

   Googles Fenster bleibt trotzdem erreichbar: als kleiner Verweis in der
   Zeile darunter, sobald Google einen Weg dorthin verlangt. */
/* ---- Der Werbeschalter ----
   Wo AdMob laeuft, gehoert die Einwilligung Google. Ein Tipp auf den
   Schalter oeffnet deshalb Googles eigenes Fenster - und DANACH stellt sich
   der Schalter auf das ein, was dort herauskam. Er springt also nicht von
   selbst um, sondern folgt der Antwort. Genau das wollte Ajdin.

   Dass das geht, liegt an ZmajEinwilligung, einem kleinen eigenen Plugin im
   Android-Teil: es liest die TCF-Angaben, die Googles UMP-SDK ablegt. Das
   AdMob-Plugin allein gibt sie nicht her - es meldet nur canRequestAds, und
   das ist auch bei Ablehnung wahr, weil dann eben unpersonalisierte
   Anzeigen kommen.

   Ohne AdMob - am PC, im Browser - bleibt es ein gewoehnlicher Schalter,
   der sofort umlegt. */
const einwPlugin = () => (window.Capacitor && window.Capacitor.Plugins
                          && window.Capacitor.Plugins.ZmajEinwilligung) || null;
/* Liefert true/false, wenn Google etwas abgelegt hat, sonst null. Bei null
   wird der eigene Schalter NICHT angefasst - lieber stehen lassen als raten. */
async function googlesAntwort(){
  const P = einwPlugin();
  if(!P) return null;
  try{
    const s = await P.stand();
    return (s && s.bekannt) ? !!s.personalisiert : null;
  }catch(e){ return null; }
}
/* Einmal beim Start abgleichen, damit der Schalter von Anfang an das zeigt,
   was bei Google steht - und nicht erst, nachdem man ihn angefasst hat. */
/* Abgeglichen wird nur, wo Googles Fenster den Schalter fuehrt. Ajdin am
   26.09.2026: verlangt Google keinen eigenen Aenderungsknopf (ausserhalb
   des EWR, oder wenn in der AdMob-Konsole kein Datenschutzfenster steht),
   dann ist admobOptionen false und der Schalter ist unser eigener - und
   trotzdem hat dieser Abgleich die Wahl beim naechsten Oeffnen der
   Einstellungen wieder auf "an" gesetzt, weil ZmajEinwilligung bei
   IABTCF_gdprApplies=0 fest "personalisiert" meldet. Eine Einwilligung,
   die sich nicht zuruecknehmen laesst, darf es nicht geben. Der Entwurf
   weiter oben sagt es selbst: solange niemand geschaltet hat, zaehlt die
   Antwort aus dem Einwilligungsfenster - danach nicht mehr. */
async function werbungAbgleichen(){
  const eigenerSchalter = !(admobDa() && admobOptionen);
  if(!eigenerSchalter || persWahl === null){
    const g = await googlesAntwort();
    if(g !== null && g !== werbungPersonalisiert()) setzePersonalisiert(g);
  }
  if($('setWerbungBox') && $('setWerbungBox').style.display !== 'none') werbungZeileZeigen();
}
function werbungZeileZeigen(){
  const an = werbungPersonalisiert();
  $('swWerbung').setAttribute('aria-checked', an);
  $('setWerbungStand').textContent = t(an ? 'set.einwilligung_ja' : 'set.einwilligung_nein');
}
let werbungLaeuft = false;      // zwei Fenster uebereinander waeren haesslich
/* Ob die Werbezeile fuer einen Abonnenten dasteht: nur auf dem Geraet, wo es
   Googles Fenster gibt (Punkt 8), seit 01.11.2026 mit Schalter. */
const aboWerbeZeile = () => unlimited() && !!(window.Capacitor && window.Capacitor.Plugins
                                              && window.Capacitor.Plugins.AdMob);
/* Punkt 8: der Widerruf fuer Abonnenten. Googles Auskunft wird ERST HIER
   geholt, auf Tipp, und ohne initialize() - das Werbe-SDK bleibt aus, beim
   Start spricht weiterhin niemand mit Google. AdMobP wird bewusst NICHT
   gesetzt: das wuerde admobDa() umschalten und damit einwilligungFragen()
   und werbungErlaubt() mitreissen, und liefe das Abo in derselben Sitzung
   aus, kaeme danach keine Anzeige mehr durch.
   Dass hier ueberhaupt mit Google gesprochen wird, hat der Nutzer selbst
   angetippt - anders ist Googles Fenster nicht zu erreichen. */
/* 01.11.2026: Angetippt wird jetzt der Schalter swWerbung, nicht mehr der
   Knopf "Wahl aendern" (Ajdin: "bei werbung statt wahl aendern soll so ein
   schalter sein" - "Ja, auch Schalter"). Er verhaelt sich wie bei Nutzern
   mit Werbung: Verlangt Google einen Weg zum Aendern (EWR), oeffnet der
   Tipp Googles Fenster, und danach zeigt der Schalter, was dort gewaehlt
   wurde (googlesAntwort). Verlangt Google keinen (ausserhalb des EWR), ist
   es der eigene Schalter und legt sofort um - wie ohne AdMob. Bis dahin
   stand dort nur "Bei Google liegt gerade keine Antwort" und es passierte
   nichts. Klappt die Frage an Google nicht (kein Netz), bleibt der
   Schalter, wie er war, und darunter steht voll.fehler, bis die Zeile neu
   gezeigt wird. Die Regeln oben zu initialize() und AdMobP gelten weiter. */
/* Pruefbericht 01.11.2026: Hat Google in dieser Sitzung einmal gesagt, dass
   es keinen Weg zum Aendern verlangt (ausserhalb des EWR), gilt das bis zum
   Neustart - jeder weitere Tipp legt sofort um, auch ohne Netz. So geht es
   auch bei Nutzern mit Werbung, dort steht admobOptionen seit dem Start
   fest. Vorher fragte jeder Tipp erneut bei Google, und ohne Netz stand nur
   voll.fehler da, obwohl die Wahl ohnehin nur auf dem Geraet liegt. */
let googleOhneFenster = false;
async function einwilligungWiderrufen(){
  const P = window.Capacitor && window.Capacitor.Plugins;
  if(!P || !P.AdMob || werbungLaeuft) return;
  if(googleOhneFenster){
    setzePersonalisiert(!werbungPersonalisiert());
    werbungZeileZeigen();
    return;
  }
  werbungLaeuft = true;
  let fehler = false;
  try{
    const A = P.AdMob;
    const info = await A.requestConsentInfo();
    if(info && info.privacyOptionsRequirementStatus === 'REQUIRED'){
      await A.showPrivacyOptionsForm();
      /* Die neue Antwort gleich uebernehmen, damit der lokale Schalter
         stimmt, falls das Abo spaeter auslaeuft. */
      const g = await googlesAntwort();
      if(g !== null) setzePersonalisiert(g);
    }else{
      /* Ausserhalb des EWR verlangt Google keinen Einstiegspunkt - dann
         gehoert die Wahl uns, wie beim eigenen Schalter. */
      googleOhneFenster = true;
      setzePersonalisiert(!werbungPersonalisiert());
    }
  }catch(e){ fehler = true; }
  werbungLaeuft = false;
  werbungZeileZeigen();
  if(fehler){
    $('setWerbungStand').textContent = t('voll.fehler');
    // Die Zeile darunter liest kein Screenreader von selbst vor (Pruefbericht 01.11.2026).
    ansagen(esc(t('voll.fehler')));
  }
}
$('swWerbung').addEventListener('click', async ()=>{
  if(werbungLaeuft) return;
  /* Abonnenten (01.11.2026): ihr eigener Weg, ohne AdMobP - siehe
     einwilligungWiderrufen(). Lief AdMob in dieser Sitzung schon (das Abo
     kam erst danach), gilt der Zweig darunter, mit demselben Ergebnis -
     nur startet das Werbe-SDK dabei fuer sie nicht (Pruefbericht
     01.11.2026, einwilligungNachziehen mit ohneStart). */
  if(aboWerbeZeile() && !admobDa()){ await einwilligungWiderrufen(); return; }
  if(admobDa() && admobOptionen){
    werbungLaeuft = true;
    try{ await AdMobP.showPrivacyOptionsForm(); }catch(e){}
    const g = await googlesAntwort();
    if(g !== null) setzePersonalisiert(g);   // genau das, was bei Google herauskam
    // Punkt 6: auch admobDarf und admobOptionen gehoeren nachgezogen.
    await einwilligungNachziehen(unlimited());
    werbungLaeuft = false;
    werbungZeileZeigen();
    return;
  }
  setzePersonalisiert(!werbungPersonalisiert());
  werbungZeileZeigen();
});
applyAnim();

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
