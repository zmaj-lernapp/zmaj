/* =================== UPDATES AUS GOOGLE PLAY ===================
   10.10.2026, Ajdin: "ja mach sanft mit schalter und wenn es schwere
   sicherheitslücken oder andere schwere fehler gibt dann mach pflicht".

   SANFT, der Normalfall: Google fragt in seinem eigenen Fenster, laedt im
   Hintergrund, und man lernt weiter. Liegt das Update fertig da, steht
   unten die kleine Leiste "Update bereit · Neu starten". Gefragt wird
   hoechstens einmal am Kalendertag, erst wenn Googles Einwilligungsfenster
   vom Start zu ist, und nie mitten in Lektion, Test, Einstufung oder
   Geschichte - Googles Fenster ist ein eigener Bildschirm und schoebe die
   Aufgabe weg.

   PFLICHT, nur bei schweren Fehlern und Sicherheitsluecken: Googles
   Vollbild, und die App ist erst nach dem Update wieder benutzbar.
   Pflicht ist ein Update mit Prioritaet 4 oder 5 ODER mit einer
   versionCode, die ein Vielfaches von 100 ist. Die zweite Regel setzt
   app_bauen.py --pflicht, ein normaler Bau landet nie darauf. Die
   Prioritaet gibt es nicht in der Play Console: sie geht nur ueber die
   Play Developer API beim Veroeffentlichen (inAppUpdatePriority) und
   laesst sich danach nicht mehr aendern. Google rechnet sie ueber alle
   Fassungen zwischen der installierten und der neuesten. Die
   versionCode-Regel sieht dagegen nur die neueste: kommt nach einem
   Pflicht-Bau ein normaler, gilt fuer alle, die davor stehen, nur noch
   sanft.
   Wer Googles Vollbild wegdrueckt, landet auf einer deckenden Karte mit
   genau einem Knopf. So raet es Google fuer Apps, die ohne das Update
   nicht laufen sollen: erst erklaeren, dann den Ablauf neu starten oder
   zum Schliessen auffordern
   (developer.android.com/guide/playcore/in-app-updates/kotlin-java).

   Die App selbst baut dafuer keine Verbindung auf: ZmajUpdate.java fragt
   den Play Store auf dem Geraet. Im Browser und in einer Huelle ohne das
   Plugin passiert gar nichts. Kann Google gerade nicht helfen (nicht aus
   dem Play Store installiert, kein Netz, Art des Updates nicht erlaubt),
   bleibt die App offen - eine Sperre, die sich nicht loesen laesst, waere
   schlimmer als der Fehler. Werbung, Abo und Leben fasst nichts davon an. */
/* Auf iPhone und iPad nie: Apple hat keine Updates aus der App heraus. Die
   iOS-Huelle meldet ZmajUpdate zwar an (seit Stufe A5), es antwortet dort
   aber immer nur "nicht_unterstuetzt" - damit ein Aufruf nie ins Leere
   geht. Gefragt wird es trotzdem nie, dafuer steht die Weiche hier.
   30.10.2026 */
const updPlugin = () => (!IST_IOS && window.Capacitor && window.Capacitor.Plugins
                         && window.Capacitor.Plugins.ZmajUpdate) || null;
const UPD_PFLICHT_PRIO = 4;                // Google vergibt 0 bis 5
const UPD_MERKER = 'zmaj_update_gefragt';  // Tag, an dem Google zuletzt sanft gefragt hat
/* Jede Anzeige, das Teilen-Menue und das Mailprogramm loesen beim
   Zurueckkommen visibilitychange aus. Einmal je Minute nachsehen reicht. */
const UPD_ABSTAND_MS = 60 * 1000;
let updBereit = false;        // erst nach dem Vorspann, siehe updBeimStart()
let updWerbungDurch = false;  // Googles Einwilligungsfenster vom Start ist zu, siehe init()
let updFragt = false, updZuletzt = 0, updStartAb = 0, updUhr = 0;
let updPflichtNein = 0;       // wann ein Pflicht-Start zuletzt "nicht gestartet" meldete
let updGeladen = false;       // Update liegt fertig geladen da -> Leiste bzw. Knopf der Karte
let updSanftOffen = false;    // Google soll fragen, sobald es ruhig ist
let updPflichtOffen = false;  // Pflicht-Update steht aus -> Karte
let updPflichtLos = false;    // Googles Vollbild beim naechsten ruhigen Moment von selbst oeffnen
let updGefragtAm = '';        // falls localStorage nicht geht

/* Die Regel aus dem Vertrag mit ZmajUpdate.java und app_bauen.py. */
function updIstPflicht(r){
  const vc = Number(r.versionCode);
  return Number(r.prioritaet) >= UPD_PFLICHT_PRIO ||
         (r.versionCode != null && vc > 0 && vc % 100 === 0);
}
function updHeuteGefragt(){
  if(updGefragtAm === today()) return true;
  try{ return localStorage.getItem(UPD_MERKER) === today(); }catch(e){ return false; }
}
function updHeuteMerken(){
  updGefragtAm = today();
  try{ localStorage.setItem(UPD_MERKER, updGefragtAm); }catch(e){}
}
/* Mitten im Lernen. Lektion, Test und Wiederholen-Runde setzen nurHerz,
   Einstufung und Geschichte nicht - die zaehlen hier eigens mit. (Die
   Einstufung setzt es seit 19.10.2026 auch; Ex_laeuft() bleibt trotzdem
   stehen, es schadet nicht und haengt nicht an der Kopfzeile.) */
function updLerntGerade(){
  return document.body.classList.contains('nurHerz') || Ex_laeuft() || sichtbar('storyView');
}
/* Ein ruhiger Moment fuer Googles sanftes Fenster: dieselben Bedingungen
   wie in kartenNachreichen(), dazu zehn Sekunden Abstand zu einer Anzeige
   - sonst kaeme Googles Fenster direkt nach dem Video fuer ein Leben.
   updWerbungDurch und nicht einstufungBereit: das steht nach acht
   Sekunden auch dann, wenn Googles Einwilligungsfenster noch offen ist.
   Das Fenster ist kein Element im Dokument, die Abfrage unten saehe es
   nicht, und es laegen zwei Fenster von Google uebereinander. */
function updRuhig(){
  return updWerbungDurch && !document.hidden && !updLerntGerade() &&
         !sichtbar('profileView') &&      // nie ueber der Anmeldung, 28.10.2026
         !frageSchliessen && !wegmarkeLaeuft && !anzeigeLaeuft && !werbungLaeuft &&
         Date.now() - anzeigeZuletzt >= 10000 &&
         !document.querySelector('.nachfrage, .einwilligung, .werbung');
}

/* Bei Google nachsehen. nachStart: der Blick direkt nach einem
   abgebrochenen Pflicht-Start - der darf das Vollbild nicht gleich wieder
   oeffnen, sonst kaeme man nur noch mit der Home-Taste heraus. */
async function updPruefen(nachStart){
  const P = updPlugin();
  if(!P || !updBereit || updFragt) return;
  updFragt = true; updZuletzt = Date.now();
  let r = null;
  try{ r = await P.pruefen(); }catch(e){ r = null; }
  updFragt = false;
  if(!r || !r.ok){
    if(updPflichtOffen){ updPflichtOffen = false; updPflichtLos = false; updSperreWeg(); }
    updNachreichen();
    return;
  }
  /* Auch zuruecknehmen: liegt nichts mehr bereit und laedt auch nichts,
     fuehrte "Neu starten" ins Leere. Waehrend es laedt (laeuft), bleibt
     der Wert, wie ihn "status" zuletzt gesetzt hat. */
  if(r.geladen) updGeladen = true;
  else if(!r.laeuft) updGeladen = false;
  /* Pflicht, wenn die Regel greift und Google das Vollbild erlaubt - oder
     wenn die Fassung schon fertig geladen daliegt (etwa weil Google beim
     ersten Mal nur sanft erlaubte). Dann braucht es kein Fenster von
     Google mehr, der Knopf der Karte installiert sie mit abschliessen().
     Ohne das bliebe ein Pflicht-Update, das sanft geladen wurde, bei der
     Leiste stehen, und man koennte es liegen lassen. */
  const pflicht = updIstPflicht(r) &&
                  (r.geladen || ((r.verfuegbar || r.laeuft) && r.pflichtErlaubt));
  if(pflicht){
    updPflichtOffen = true; updSanftOffen = false;
    /* Von selbst nur, solange noch keine Karte steht (einmal je Start),
       oder wenn Google ein angefangenes Update fortsetzen will (laeuft) -
       das verlangt Google ausdruecklich. Wer das Vollbild weggedrueckt
       hat, sieht die Karte und tippt selbst, statt es bei jeder Rueckkehr
       ungefragt wieder vor sich zu haben. */
    if(!nachStart && (r.laeuft || !document.querySelector('.updsperre'))) updPflichtLos = true;
  } else {
    if(updPflichtOffen){ updPflichtOffen = false; updPflichtLos = false; updSperreWeg(); }
    /* Laedt es schon (laeuft) oder liegt es bereit (geladen), wird nicht
       noch einmal gefragt - die Leiste kommt dann ueber "status". Ist
       Pflicht nicht erlaubt, sanft aber schon, wird wenigstens sanft
       gefragt. */
    if(r.verfuegbar && !r.laeuft && !r.geladen && r.sanftErlaubt && !updHeuteGefragt())
      updSanftOffen = true;
  }
  updNachreichen();
}

/* Wird von nurHerz() bei jedem Wechsel gerufen, von Startablauf und
   Rueckkehr in die App. Die Leiste folgt sofort, alles andere erst nach
   600 ms: showView() ruft nurHerz(false), BEVOR eine Runde ihre Lektion
   aufschlaegt - ohne die Pause ging Googles Fenster genau dazwischen auf. */
function updNachreichen(){
  try{
    updLeisteZeigen();
    if(!updBereit || updUhr || (!updPflichtOffen && !updSanftOffen)) return;
    updUhr = setTimeout(updJetzt, 600);
  }catch(e){}
}
function updJetzt(){
  updUhr = 0;
  try{
    if(document.hidden) return;
    if(updPflichtOffen){
      if(updLerntGerade()) return;       // nach der Lektion kommt nurHerz(false) wieder her
      /* Nicht ueber eine laufende Anzeige oder Googles Datenschutzfenster:
         sonst ginge das Video fuer ein Leben mitten im Abschluss verloren.
         Deren Ende ruft hier nichts auf, also in zwei Sekunden noch einmal. */
      if(anzeigeLaeuft || werbungLaeuft){ updUhr = setTimeout(updJetzt, 2000); return; }
      updSperreZeigen();
      if(updPflichtLos){
        updPflichtLos = false;
        /* Liegt es fertig geladen da, genuegt der Knopf der Karte. Und nicht
           gleich wieder, wenn Google eben "nicht gestartet" gemeldet hat:
           Rueckkehr (visibilitychange) und diese Antwort kommen in beliebiger
           Reihenfolge an, und der Blick der Rueckkehr wuesste nichts davon. */
        if(!updGeladen && Date.now() - updPflichtNein > 2000) updPflichtStarten();
      }
      return;
    }
    if(updSanftOffen && updRuhig()) updSanftStarten();
  }catch(e){}
}
/* Kein Riegel bis zur Antwort: ob und wann ZmajUpdate.java bei einem
   Vollbild antwortet, haengt am Nutzer. Drei Sekunden genuegen gegen den
   doppelten Tipp und haengen nie fest. */
function updDarfStarten(){
  if(Date.now() - updStartAb < 3000) return false;
  updStartAb = Date.now();
  return true;
}
async function updSanftStarten(){
  const P = updPlugin();
  updSanftOffen = false;
  if(!P || updHeuteGefragt() || !updDarfStarten()) return;
  updHeuteMerken();         // vorher: auch wenn Google gar kein Fenster zeigt, heute nicht noch einmal
  try{ await P.starten({pflicht: false}); }catch(e){}
}
async function updPflichtStarten(){
  const P = updPlugin();
  if(!P || !updDarfStarten()) return;
  updSperreZeigen();
  try{ await saveProgress(); }catch(e){}
  let r = null;
  try{ r = await P.starten({pflicht: true}); }catch(e){ r = null; }
  /* Nicht gestartet heisst: weggedrueckt oder von Google abgelehnt. Was
     davon, sagt der naechste Blick - steht das Update noch aus, bleibt die
     Karte, sonst geht sie. */
  if(!r || !r.gestartet){ updPflichtNein = Date.now(); updPruefen(true); }
}
/* "Neu starten": Google installiert und startet die App neu. Vorher
   speichern, auch wenn visibilitychange es gleich noch einmal tut. */
async function updAbschliessen(knopf){
  const P = updPlugin();
  if(!P) return;
  if(knopf){ knopf.disabled = true; setTimeout(()=>{ knopf.disabled = false; }, 4000); }
  try{ await saveProgress(); }catch(e){}
  let r = null;
  try{ r = await P.abschliessen(); }catch(e){ r = null; }
  /* Klappt es, startet die App neu, und hier kommt nichts mehr an. Kam
     eine Absage (etwa: doch nichts fertig geladen), sagt ein frischer
     Blick, ob Leiste und Karte noch stimmen. */
  if(!r || r.ok === false) updPruefen(true);
}

function updLeisteZeigen(){
  let el = $('updLeiste');
  const soll = updGeladen && updBereit && !updLerntGerade() && !document.querySelector('.updsperre');
  document.body.classList.toggle('updDa', soll);
  if(!soll){ if(el) el.hidden = true; return; }
  if(!el){
    el = document.createElement('div');
    el.id = 'updLeiste';
    el.className = 'updleiste';
    el.setAttribute('role', 'status');
    el.innerHTML = '<span class="updtext"></span><button type="button" class="btn know"></button>';
    const knopf = el.querySelector('button');
    knopf.addEventListener('click', ()=> updAbschliessen(knopf));
    document.body.appendChild(el);
    /* Die Hoehe aendert sich auch ohne Aufruf hier: die Schrift laedt
       nach, die Sprache wechselt, das Handy wird gedreht. Einmal messen
       reichte in der Probe nicht - die Leiste lag 7 px auf dem letzten
       Kasten. */
    if(window.ResizeObserver) new ResizeObserver(updLeisteMessen).observe(el);
  }
  /* Bei jedem Aufruf beschriften: die Sprache kann inzwischen gewechselt
     haben. Aber nur, wenn sich etwas aendert - role="status" liest jede
     Aenderung vor, und nurHerz() kommt bei jedem Ansichtswechsel her. */
  const text = el.querySelector('.updtext'), knopf = el.querySelector('button');
  if(text.textContent !== t('upd.bereit')) text.textContent = t('upd.bereit');
  if(knopf.textContent !== t('upd.neustart')) knopf.textContent = t('upd.neustart');
  el.hidden = false;
  updLeisteMessen();
}
/* Fuer body.updDa im Stil: so viel Platz unter der Seite, wie die Leiste
   wirklich hoch ist. Ausgeblendet misst sie 0 - dann bleibt der alte Wert. */
function updLeisteMessen(){
  const el = $('updLeiste');
  const hoehe = el ? el.offsetHeight : 0;
  if(hoehe > 0) document.body.style.setProperty('--upd-hoehe', hoehe + 'px');
}
/* Die Karte beim Pflicht-Update. Kein Tipp daneben, keine Zurueck-Taste
   (die schliesst hier die App, siehe zurueckTaste) - nur der eine Knopf.
   Sie traegt die Klasse nachfrage, damit Bewertung, Einstufung und
   Erinnerungsfrage solange warten. */
function updSperreZeigen(){
  if(document.querySelector('.updsperre')) return;
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage updsperre';
  kasten.setAttribute('role', 'alertdialog');
  kasten.setAttribute('aria-modal', 'true');
  kasten.setAttribute('aria-labelledby', 'updTitel');
  kasten.innerHTML =
    '<div class="nachfragebox einstbox">' +
      '<div class="celebrate"><div class="zmaj idle">' + zmaj('happy') + '</div></div>' +
      '<h3 id="updTitel"></h3><div class="txt"></div>' +
      '<button type="button" class="btn know" id="updJetzt"></button>' +
    '</div>';
  kasten.querySelector('h3').textContent = t('upd.pflicht_titel');
  kasten.querySelector('.txt').textContent = t('upd.pflicht_text');
  const knopf = kasten.querySelector('#updJetzt');
  knopf.textContent = t('upd.pflicht_knopf');
  /* Liegt das Update schon fertig geladen da, ist Neustarten der kuerzere Weg. */
  knopf.addEventListener('click', ()=>{ if(updGeladen) updAbschliessen(knopf); else updPflichtStarten(); });
  document.body.appendChild(kasten);
  updLeisteZeigen();
}
function updSperreWeg(){
  const k = document.querySelector('.updsperre');
  if(k) k.remove();
  updLeisteZeigen();
}

/* Meldungen aus dem Plugin. Einmal beim Laden anhaengen, wie bei ZmajAbo.
   Kommt "geladen", waehrend noch der Vorspann laeuft, wartet die Leiste
   auf updBereit. */
(function updHorchen(){
  const P = updPlugin();
  if(!P || !P.addListener) return;
  try{
    Promise.resolve(P.addListener('status', d => {
      /* Kommt die Meldung, bevor alle Teile geladen sind: merken, die Leiste
         zeigt updBeimStart() danach (skripteDa, 20.11.2026). */
      if(d && d.geladen){ updGeladen = true; if(skripteDa) updNachreichen(); }
    })).catch(()=>{});
  }catch(e){}
})();
/* Zurueck in der App: Google will, dass dann nach einem fertig geladenen
   und nach einem angefangenen Pflicht-Update gesehen wird. Steht ein
   Pflicht-Update aus, jedes Mal, sonst einmal je Minute. */
document.addEventListener('visibilitychange', ()=>{
  if(!skripteDa || document.hidden || !updBereit) return;
  if(updPflichtOffen || Date.now() - updZuletzt >= UPD_ABSTAND_MS) updPruefen(false);
  else updNachreichen();
});
/* Aus init(), wenn der Vorspann weg ist. */
function updBeimStart(){
  if(updBereit) return;
  updBereit = true;
  updPruefen(false);
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
