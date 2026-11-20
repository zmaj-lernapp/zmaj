/* ---- Sprachausgabe: eigene Aufnahme (web/audio) vor Computerstimme ---- */
/* hasTTS    = das Geraet hat eine Computerstimme. In der Android-App ist das
                meist NICHT so - die System-WebView kennt speechSynthesis nicht.
   canListen = es laesst sich ueberhaupt etwas hoeren: Computerstimme ODER
               mitgelieferte Aufnahmen. Daran haengen die Hoer-Knoepfe, der
               Aufgabentyp 'listen' und die Tagesaufgabe 'hoer'.
               Wird in ladeAudio() endgueltig gesetzt. */
/* Auf iOS immer false (30.10.2026, iOS_Plan.md 3.5): WebKit hat dort eine
   Computerstimme, und mit ihr laese still die iOS-Stimme statt Emir, und an
   Woertern ohne Aufnahme stuenden Lautsprecher. Gesprochen wird auf dem
   iPhone nur, was als Aufnahme mitkommt - wie in der Android-App. */
const hasTTS = !IST_IOS && 'speechSynthesis' in window;
/* Hier stand bis zum 15.11.2026 navigator.audioSession.type = 'playback',
   gleich beim Laden des Skripts. Das geschieht jetzt erst im ersten
   Fingertipp und erst ab iOS 17 - siehe tonSitzung() bei "Ton im
   Fingertipp". */
let canListen = hasTTS;
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
/* Spracherkennung gibt es auf zwei Wegen, und der Unterschied ist nicht
   Geschmack: In der App-Huelle ist die Schnittstelle des Browsers zwar da,
   aber der Dienst dahinter fehlt - sie bricht sofort mit "nicht erlaubt"
   ab, ganz gleich welche Berechtigung gesetzt ist. Darum dort das Plugin,
   das Androids eigene Erkennung benutzt; am PC bleibt es beim Browser.
   canSpeak steht erst nach hoerenPruefen() fest, das in init() laeuft. */
function hoererPlugin(){
  const P = window.Capacitor && window.Capacitor.Plugins;
  return (P && P.SpeechRecognition) || null;
}
let canSpeak = false;
/* Hat der Nutzer das Mikrofon einmal abgelehnt, merkt sich die App das.
   Sonst galt der Ausschluss nur bis zum naechsten Start: available()
   sagt lediglich, dass ein Erkenner installiert ist, nicht dass die App
   ihn benutzen darf - und nach jedem Neustart standen wieder
   Sprechaufgaben da, die sich nur ueberspringen lassen. Gefunden bei P10
   am 28.09.2026. Der Weg zurueck bleibt offen: erteilt er die
   Berechtigung spaeter in den Geraeteeinstellungen, faellt die Merkung
   beim naechsten Start von selbst weg. */
const MIKRO_NEIN = 'zmaj_mikro_nein';
function mikroAbgelehnt(){
  try{ return localStorage.getItem(MIKRO_NEIN) === '1'; }catch(e){ return false; }
}
function mikroAbsageMerken(ja){
  try{ ja ? localStorage.setItem(MIKRO_NEIN, '1') : localStorage.removeItem(MIKRO_NEIN); }catch(e){}
}
async function hoerenPruefen(){
  const H = hoererPlugin();
  if(H){
    try{ canSpeak = !!(await H.available()).available; }
    catch(e){ canSpeak = false; }
    /* Nur nachsehen, nicht fragen: checkPermissions() oeffnet kein
       Fenster. Ein abgelehntes Mikrofon nimmt 'speak' aus dem Topf,
       ein erteiltes loescht die gemerkte Absage. */
    if(canSpeak){
      try{
        const r = await H.checkPermissions();
        const stand = r && r.speechRecognition;
        if(stand === 'granted') mikroAbsageMerken(false);
        else if(stand === 'denied' || mikroAbgelehnt()) canSpeak = false;
      }catch(e){}
    }
  } else {
    canSpeak = !!SR && window.isSecureContext;
  }
  return canSpeak;
}
/* ---- Android: in welcher Sprache zugehoert wird (16.11.2026) ----
   Rueckmeldung ueber das Formular: die Sprechuebung erkennt auch einen
   Muttersprachler nicht immer (Sprech-Analyse vom 16.11.2026, Punkte 1, 3
   und 19). Bis dahin probierte die Sprechaufgabe bs-BA, hr-HR, sr-RS und
   zuletzt die Sprache des Handys. Jedes "No match" schob den naechsten Tipp
   eine Sprache weiter - nach zwei Fehlversuchen hoerte die App serbisch zu,
   und eine kyrillische Abschrift war immer falsch. Andere Fehler liefen in
   einem Tipp still bis zur Handysprache durch, ohne Netz kam so eine
   deutsche Abschrift statt der Offline-Meldung.
   Jetzt gibt es nur noch bs-BA und hr-HR, und was ein Fehler bedeutet,
   entscheidet, wie es weitergeht (sprechFehlerArt()):
   - "No match", "No speech input": die Sprache bleibt, die Meldung kommt.
     Meist war es zu kurz, zu leise oder angeschnitten. Nur solange bs-BA in
     dieser Sitzung noch nichts geliefert hat, nimmt nach zwei solchen
     Versuchen in Folge der naechste Tipp hr-HR - fuer Handys, die bs-BA
     nicht koennen und trotzdem "No match" melden. Ebenso nach zwei
     "Network error" in Folge, obwohl das Handy Netz meldet.
   - "Didn't understand" (darunter Androids "Sprache fehlt", Fehler 12 und
     13, aber auch 10, 11 und alles Unbekannte) und "error from server":
     zuerst nach SPRECH_NOCHMAL_MS einmal dieselbe Sprache, still im selben
     Tipp - "Hoert zu ..." bleibt stehen. Erst wenn auch dieser Start
     ablehnt, kommt im selben Tipp die andere Sprache, und gibt es keine
     mehr, die Meldung. Handys ohne bs-BA duerfen nicht vom Sprechen
     abgeschnitten werden.
     Warum erst noch einmal (Geraetebefund 17.11.2026, Samsung S21 mit
     Googles Erkennungsdienst): Nach einem Start, der zugehoert hatte, lehnte
     der naechste oft sofort (0 ms) mit "Didn't understand" ab, auch nach 3
     oder 10 s Pause, und der Start direkt danach hoerte in 5 von 5 Faellen
     wieder zu. Bis dahin galt die Sprache schon nach dieser einen Ablehnung
     als fehlend - etwa jeder zweite Tipp zeigte "Das hat nicht geklappt",
     ohne zugehoert zu haben.
   - "Client side error" (bis Android 11 vielleicht "Sprache fehlt"):
     ebenso, einmal dieselbe Sprache, dann die andere.
   - "RecognitionService busy", "Audio recording error": einmal dieselbe
     Sprache nach SPRECH_NOCHMAL_MS, dann die Meldung.
   - Je Sprache und Tipp gibt es nur diese eine Wiederholung, gleich nach
     welchem Fehler ("busy", dann "Didn't understand" startet nicht ein
     drittes Mal) - hoechstens vier Starts je Tipp.
   - "Network error", "Network timeout": sofort die Offline-Meldung, auch
     im Wiederholversuch.
   Als "fehlt" fuer die Sitzung gilt eine Sprache nur, wenn BEIDE Starts im
   Tipp mit "Sprache fehlt" ("Didn't understand" oder "Client side error")
   abgelehnt haben, und zwar sofort, unter SPRECH_SOFORT_MS: Androids
   "Sprache fehlt" kommt beim Start, bevor das Mikrofon aufgeht (bs-BA am
   S21: immer 0 ms; das frueheste "No match" kam nach 5,2 s). Eine spaete
   Ablehnung kommt von einem Erkenner, der die Sprache angenommen und
   zugehoert hat. Und weil auf einen Start, der zugehoert hat, oft eine
   Sofort-Ablehnung folgt, sperrte "spaet, dann sofort" sonst eine Sprache
   aus, die funktioniert - bei bs-BA hiesse das hr-HR fuer die ganze Sitzung
   ("Tko" statt "Ko"). Geht ein Paar ohne diese Merkung aus, kommt trotzdem
   im selben Tipp die andere Sprache, wie bei "error from server".
   Die Sprache, die etwas geliefert hat, gilt fuer die ganze Sitzung, ebenso
   hr-HR, wenn bs-BA "fehlt". Hat aber bs-BA einmal geliefert, bleibt es bei
   bs-BA: liefert spaeter hr-HR, weil bs-BA einmal abgelehnt hat, war hr-HR
   nur die Ausweichsprache in diesem Tipp. Scheitern alle Sprachen
   SPRECH_DIENST_GRENZE Tipps in Folge an Sprach- oder Dienstfehlern, faellt
   das Sprechen fuer diese Sitzung aus (canSpeak), ohne mikroAbsageMerken():
   beim naechsten Start wird neu versucht. Und jeder Start hat eine Zeitgrenze
   (sprechStart()). Gilt nur fuer Android - das iPhone (ZmajSprache) und der
   Browser behalten ihren Weg, siehe sprechAufIOS(). */
const SPRECH_SPRACHEN = ['bs-BA', 'hr-HR'];
/* 15 s statt 12 s seit dem 17.11.2026: am S21 kam "No match" bei Stille
   einmal erst nach 11,5 s, knapp hinter der alten Grenze. */
let SPRECH_ZEITGRENZE = 15000;    // ms je Start; die Tests setzen sie herunter
const SPRECH_NOCHMAL_MS = 400;
let SPRECH_SOFORT_MS = 1500;      // schneller abgelehnt = nicht zugehoert; die Tests setzen sie herunter
const SPRECH_DIENST_GRENZE = 2;
let sprechSprache = null;         // womit der naechste Tipp beginnt; null = bs-BA, noch nicht bestaetigt
const sprechGeliefert = new Set(); // Sprachen, die in dieser Sitzung schon etwas geliefert haben
const sprechFehlt = new Set();    // Sprachen, die in dieser Sitzung mit "Sprache fehlt" abgelehnt wurden
let sprechStill = 0;              // "No match" / "No speech input" mit bs-BA in Folge
let sprechDienstAus = 0;          // Tipps in Folge, an denen jede Sprache an Sprach- oder Dienstfehlern scheiterte
let sprechVersuch = 0;            // Nummer des letzten Starts
let sprechOffen = 0;              // Nummer des Starts, auf den die Seite gerade wartet
/* Ob die Seite in der iPhone-Huelle laeuft. Dort meldet ZmajSprache bs-BA
   sofort als unbekannt und lehnt nach dem Start nie mehr ab, und es hat
   eigene Zeitgrenzen - fuer das iPhone bleibt die Sprechaufgabe deshalb,
   wie sie war. Hier in ios-web entscheidet die Weiche im Kopf (IST_IOS);
   die Plattform fragt nur der Kopf ab (tests/test_ios.py). */
function sprechAufIOS(){ return IST_IOS; }
function sprechFehlerArt(e){
  const m = String((e && e.message) || e || '');
  if(/No match|No speech input/i.test(m)) return 'still';
  if(/Network/i.test(m)) return 'netz';
  if(/busy|Audio recording/i.test(m)) return 'belegt';
  if(/Client side error/i.test(m)) return 'client';
  return 'sprache';    // Didn't understand, error from server und alles Unbekannte
}
/* H.start() mit Zeitgrenze (Analyse Punkt 19): Ruft Androids Erkenner nach
   dem Sprechende weder ein Ergebnis noch einen Fehler auf, wartete die Seite
   bisher ewig, und ein weiterer Tipp rief nur H.stop(), das dann nichts mehr
   tut. Nach SPRECH_ZEITGRENZE kommt {zeitAus: true}. Das Community-Plugin
   hat kein cancel - ein spaetes Ergebnis dieses Starts verwirft die Seite
   ueber die Versuchsnummer. Der naechste start() baut den Erkenner ohnehin
   neu. */
function sprechStart(H, optionen){
  const nr = ++sprechVersuch;
  sprechOffen = nr;
  return new Promise((fertig, fehler) => {
    const uhr = setTimeout(() => {
      if(sprechOffen !== nr) return;
      sprechOffen = 0;
      try{ const s = H.stop(); if(s && s.catch) s.catch(() => {}); }catch(e){}   // nicht warten: stop() antwortet dann nie
      fertig({zeitAus: true});
    }, SPRECH_ZEITGRENZE);
    Promise.resolve().then(() => H.start(optionen)).then(
      r => { clearTimeout(uhr); if(sprechOffen !== nr) return; sprechOffen = 0; fertig(r); },
      e => { clearTimeout(uhr); if(sprechOffen !== nr) return; sprechOffen = 0; fehler(e); });
  });
}
let AUDIO = new Map();
/* Wortzeiten der Geschichten fuer das Mitlesen (20.10.2026): Datei ->
   [[start_ms, ende_ms], ...], ein Paar je Wort. Siehe ---- Mitlesen ----. */
let WORTZEITEN = new Map();
let voiceName = ''; try{ voiceName = localStorage.getItem('zmaj_voice') || ''; }catch(e){}
const audioKey = text => text.split(' / ')[0].replace(/[.!?…]+$/,'').trim().toLowerCase();
function bosnianVoices(){
  return speechSynthesis.getVoices().filter(v=>/^(bs|hr|sr)/i.test(v.lang))
    .sort((a,b)=>{ const s=v=>(/^bs/i.test(v.lang)?0:(/^hr/i.test(v.lang)?1:2))*10 + (/natural|online/i.test(v.name)?0:1); return s(a)-s(b); });
}
function pickVoice(){ const list = bosnianVoices(); return list.find(v=>v.name===voiceName) || list[0] || null; }
/* Das bosnische Alphabet kennt kein x, q, w und y. Die Stimme verschluckt diese
   Buchstaben (aus „Rex“ wird „Re“). Darum vor dem Vorlesen umschreiben.
   Nur für den Ton, der angezeigte Text bleibt unverändert. */
function fuerStimme(text){
  return text.split(' / ')[0]
    .replace(/x/g, 'ks').replace(/X/g, 'Ks')
    .replace(/q/g, 'k').replace(/Q/g, 'K')
    .replace(/w/g, 'v').replace(/W/g, 'V')
    .replace(/y/g, 'j').replace(/Y/g, 'J');
}
/* ---- Tempo ----
   Ajdin am 18.09.2026: man soll langsamer vorlesen lassen koennen. Bis zum
   05.11.2026 galt der Wert fuer alle Aufnahmen - ein Wort, das in der Lektion
   zu schnell kommt, sei dasselbe Problem. Das war ein Fehler: einstellen
   laesst er sich nur in den Geschichten, und wer dort einmal 0,75x waehlte,
   hoerte den Sprecher danach in allen Lektionen langsam, ohne zu wissen warum
   und ohne Knopf dafuer. Dazu fiel der schnelle Weg ueber WebAudio weg (siehe
   "Wann das Wort kommt, Teil 2"). Gefunden bei Ajdins Frau, Ajdin: "das muessen
   wir fixen das es nur auf das lesen sich beziehen muss".
   Seitdem gilt tempo nur noch beim Vorlesen einer Geschichte: showStory() gibt
   es an sprichMitSpieler() weiter, auch fuer die Computerstimme am PC. Alles
   andere laeuft immer mit 1 - Woerter, Saetze, Hoerfragen und auch ein in der
   Geschichte angetipptes Wort. Ein gemerktes zmaj_tempo bleibt gueltig. */
const TEMPI = [0.5, 0.75, 1, 1.25];
let tempo = 1;
try{ const gemerkt = parseFloat(localStorage.getItem('zmaj_tempo'));
     if(TEMPI.indexOf(gemerkt) >= 0) tempo = gemerkt; }catch(e){}
/* pausiert: angehalten, aber NICHT zurueckgesetzt. Ohne diese Unterscheidung
   wuerde das 'pause'-Ereignis den Vorlese-Knopf sofort zuruecksetzen, und die
   Stelle im Text waere verloren. */
let pausiert = false;

/* Ein einziges Audio-Element fuer alles. Fuer jedes Wort ein neues anzulegen
   laesst den vorigen Ton weiterlaufen und fuellt mit der Zeit den Speicher. */
const spieler = new Audio(); spieler.preload = 'none';
/* Der laufende stumme Anlauf aus tonVorwaermen(), sonst null (22.10.2026). */
let vorwaermen = null;
function spieleDatei(datei, fertig, rate){
  waStopp();               // nie zwei Woerter uebereinander (26.10.2026)
  pausiert = false;        // ein neuer Ton hebt eine alte Pause auf
  /* Ein echtes Wort ist nie stumm: laeuft noch das Vorwaermen, ist es
     hiermit vorbei, und sein Abschluss laesst den spieler in Ruhe. */
  vorwaermen = null; spieler.muted = false;
  spieler.pause(); spieler.currentTime = 0;
  spieler.onended = fertig || null;
  spieler.src = 'audio/' + datei;
  /* Das Tempo bei jedem Start neu setzen: die Eigenschaft ueberlebt zwar den
     Wechsel der Quelle, aber nicht jede WebView haelt sich daran. Und ohne
     rate immer auf 1, sonst bliebe das naechste Wort auf dem Tempo der
     Geschichte davor haengen (05.11.2026, siehe "---- Tempo ----").
     preservesPitch haelt die Tonhoehe - ohne das klaenge Goran bei 0,5x wie
     aus dem Keller. */
  try{ spieler.preservesPitch = true; }catch(e){}
  try{ spieler.playbackRate = rate || 1; }catch(e){}
  return spieler.play();   // Promise! Ablehnung muss gefangen werden.
}
/* ---- Ruhe ----
   Die Geschichten sind als ganze Aufnahme dabei, die laengste 52 Sekunden.
   Wer waehrenddessen zurueckgeht, hoerte sie vorher bis zum Ende weiter -
   auch auf der Startseite und in den Einstellungen. Deshalb eine einzige
   Stelle, die alles abstellt, und ein Aufruf in showView(): egal auf
   welchem Weg man eine Ansicht verlaesst, es wird still.
   `laeuftVor` ist gesetzt, solange ein Knopf mitlaufen soll - er faerbt
   sich zurueck, wenn der Ton endet oder abgebrochen wird. */
let laeuftVor = null, tonMarke = 0;
/* Das Wort, das gerade ueber WebAudio laeuft oder dort bestellt ist (eine
   AudioBufferSourceNode), sonst null - siehe pufferSpielen() (26.10.2026).
   Steht hier oben, weil stilleBitte() es abstellt. */
let waQuelle = null;
/* Wo eine vorgelesene Geschichte unterbrochen wurde: {datei, sekunde}.
   Wer ein Wort antippt, um es uebersetzt zu bekommen, soll danach nicht
   wieder bei Sekunde null landen - stilleBitte() dreht currentTime aber
   grundsaetzlich zurueck. Deshalb wird die Stelle vorher gesichert.
   Gemeldet am 24.09.2026. */
let geschichteStelle = null;
/* Das laufende Mitlesen einer Geschichte, sonst null (20.10.2026). Steht
   hier oben bei den anderen Zustaenden, weil stilleBitte() es abraeumt. */
let mitlesen = null;
/* aufgabeMarke: welche Aufgabe gerade steht. Die Spracherkennung antwortet
   verzoegert - wer waehrenddessen ueberspringt oder abbricht, bekaeme sonst
   das Ergebnis in die NAECHSTE Aufgabe geliefert, samt Piepton und einem
   zweiten done(). hoererAbbrechen bricht eine laufende Erkennung ab. */
let aufgabeMarke = 0, hoererAbbrechen = null;
/* Nur den Knopf zuruecksetzen - der Ton selbst ist dann schon aus. */
function knopfZurueck(){
  const zurueck = laeuftVor; laeuftVor = null;
  if(zurueck) try{ zurueck(); }catch(e){}
}
/* behalteAufgabe: den Ton abstellen, die Aufgabe aber stehen lassen.
   Gebraucht wird das genau einmal - beim Wechsel in den Hintergrund.
   Warum: aufgabeMarke sagt, welche Aufgabe gerade gilt. bewerte() in der
   Sprechaufgabe verwirft jedes Ergebnis, dessen Marke nicht mehr stimmt -
   richtig, wenn die Erkennung verspaetet in die NAECHSTE Aufgabe
   hineinredet. Nur hob visibilitychange die Marke ebenfalls an, obwohl
   dieselbe Aufgabe weiter auf dem Schirm steht. Folge: Handy sperren und
   wieder aufwecken, und das Sprechen war fuer diese Aufgabe tot - das
   Mikrofon hoerte zu, aber das Ergebnis fiel weg.
   Ajdin am 27.09.2026: "wenn ich mein handy schliesse und wieder oeffne geht
   das sprechen nicht mehr er erkennt meine stimme nicht". Am Geraet
   nachgemessen: die Marke sprang allein durch den Wechsel von 68 auf 69.
   Die laufende Erkennung wird trotzdem abgebrochen - die App darf nicht aus
   der Tasche weiter zuhoeren. Nur die Aufgabe bleibt gueltig. */
function stilleBitte(behalteAufgabe){
  tonMarke++;              // macht noch wartende Zeitgeber ungueltig
  if(!behalteAufgabe) aufgabeMarke++;   // und verspaetete Erkennungs-Ergebnisse
  pausiert = false;        // Stopp ist keine Pause: der Knopf darf zurueck
  spieler.onended = null;  // zuerst, und ausserhalb des try: das darf nie haengenbleiben
  try{ spieler.pause(); spieler.currentTime = 0; }catch(e){}
  waStopp();               // auch ein Wort ueber WebAudio, laufend oder erst bestellt (26.10.2026)
  if(hasTTS){ try{ speechSynthesis.cancel(); }catch(e){} }
  const h = hoererAbbrechen; hoererAbbrechen = null;
  if(h) try{ h(); }catch(e){}
  knopfZurueck();
  mitlesenAus();           // keine Markierung ohne Ton (20.10.2026)
}
/* Haelt das System den Ton von aussen an - Kopfhoerer abgezogen, ein Anruf,
   eine andere App holt sich den Ton -, kommt kein 'ended'. Der Knopf
   stuende dann bis zum naechsten Tippen auf "Stopp". Das 'pause'-Ereignis
   kommt aber. Nur kommt es VERZOEGERT, auch fuer das pause(), das
   spieleDatei() vor jedem Start selbst ruft - dann laeuft laengst der neue
   Ton und `paused` ist schon wieder false. Deshalb die Pruefung. */
spieler.addEventListener('pause', ()=>{
  if(!spieler.paused || pausiert) return;
  /* iPhone (15.11.2026): eine vorgelesene Geschichte, die das System
     anhaelt (Anruf, Siri), merkt sich die Stelle, und sie setzt nicht von
     selbst wieder ein - siehe tonVonAussenAngehalten() bei "Zurueck in der
     App". Android bleibt, wie es war. */
  if(IST_IOS && laeuftVor) tonVonAussenAngehalten();
  knopfZurueck();
});
spieler.addEventListener('error', knopfZurueck);
/* ---- Mitlesen ----
   Wunsch einer Testerin, umgesetzt am 20.10.2026: beim Vorlesen einer Geschichte
   ist das Wort markiert, das die Stimme gerade spricht - so kann man im
   Text folgen. Schon Gesprochenes wird blasser. Aussehen: .w.mitlesen und
   .w.gelesen im Stil.
   Die Zeiten liefert wortzeiten_holen.py als Feld "w" in audio/index.json:
   je Wort ein Paar [start_ms, ende_ms] ab Anfang der Aufnahme bei Tempo 1,
   in der Reihenfolge der .w in showStory(). Gelesen wird
   spieler.currentTime - das ist Zeit in der Aufnahme, nicht auf der Uhr.
   Deshalb passt es bei jedem Tempo ohne Umrechnung, auch wenn das Tempo
   mitten im Lesen wechselt, und nach einem Sprung (Weiterlesen ab der
   gemerkten Stelle) setzt die Markierung gleich am richtigen Wort ein.
   requestAnimationFrame statt 'timeupdate': das kommt nur etwa viermal in
   der Sekunde, kurze Woerter wie "i" oder "je" fielen durch.
   Die Schleife laeuft nur, solange der Ton laeuft. In der Pause steht sie,
   die Markierung bleibt stehen, 'play' weckt sie wieder. Abgeraeumt wird
   bei allem, was das Vorlesen beendet: Stopp, Ende, Wort angetippt, andere
   Geschichte, Ansicht verlassen, App verdeckt - alles laeuft ueber
   stilleBitte() oder wiederVorlesen() in showStory().
   Die Computerstimme am PC bekommt keine Markierung: sie spricht
   fuerStimme(text) ("Rex" als "Reks"), die Stellen aus onboundary passen
   also nicht Zeichen fuer Zeichen zum angezeigten Text. Auf dem Handy gibt
   es sie ohnehin nicht. */
const MITLESEN_NACHLAUF = 120;   // ms, die ein Wort nach seinem Ende noch stehen bleibt
/* Die Zeiten nur, wenn sie zur Geschichte passen: genau ein Paar je Wort,
   Zahlen, Anfaenge aufsteigend. Wurde der Text geaendert und die Aufnahme
   nicht, stimmt die Anzahl nicht mehr - dann lieber keine Markierung als
   eine, die neben der Stimme herlaeuft. Still, ohne Meldung. */
function mitlesZeiten(datei, anzahl){
  const z = datei ? WORTZEITEN.get(datei) : null;
  if(!Array.isArray(z) || !anzahl || z.length !== anzahl) return null;
  let vorher = -Infinity;
  for(let i = 0; i < z.length; i++){
    const p = z[i];
    if(!Array.isArray(p) || p.length < 2 || !Number.isFinite(p[0]) ||
       !Number.isFinite(p[1]) || p[0] < vorher) return null;
    vorher = p[0];
  }
  return z;
}
/* Nach speak() rufen: dann steht die Aufnahme schon im spieler, und die
   Marke ist die dieses Laufs. */
function mitlesenStart(datei, woerter){
  mitlesenAus();
  const liste = Array.prototype.slice.call(woerter || []);
  const zeiten = mitlesZeiten(datei, liste.length);
  if(!zeiten) return;
  mitlesen = {woerter: liste, zeiten: zeiten, quelle: spieler.src, marke: tonMarke,
              akt: -1, gelesen: 0, bild: 0};
  mitlesen.bild = requestAnimationFrame(mitlesenTakt);
}
function mitlesenAus(){
  const m = mitlesen; mitlesen = null;
  if(!m) return;
  if(m.bild) try{ cancelAnimationFrame(m.bild); }catch(e){}
  m.woerter.forEach(w => w.classList.remove('mitlesen', 'gelesen'));
}
function mitlesenTakt(){
  const m = mitlesen; if(!m) return;
  m.bild = 0;
  /* Ein anderer Ton oder ein Stopp dazwischen: aus. stilleBitte() raeumt
     schon selbst ab - das hier ist die zweite Sicherung. */
  if(m.marke !== tonMarke || spieler.src !== m.quelle){ mitlesenAus(); return; }
  mitlesenZeigen(m, spieler.currentTime * 1000);
  if(!spieler.paused) m.bild = requestAnimationFrame(mitlesenTakt);
}
spieler.addEventListener('play', ()=>{
  const m = mitlesen;
  if(m && !m.bild) m.bild = requestAnimationFrame(mitlesenTakt);
});
/* Wort i ist dran ab seinem Anfang bis kurz nach seinem Ende, laengstens
   bis das naechste beginnt. In der Pause nach einem Satz bleibt es also
   einen Augenblick stehen, dann ist keins markiert. Gelesen ist alles
   davor - in so einer Pause auch das zuletzt gesprochene. Angefasst wird
   das DOM nur, wenn sich etwas aendert, nicht in jedem Bild. */
function mitlesenZeigen(m, t){
  const z = m.zeiten, n = z.length;
  let begonnen = 0;
  while(begonnen < n && z[begonnen][0] <= t) begonnen++;
  let akt = -1;
  if(begonnen > 0){
    const i = begonnen - 1;
    const ende = Math.min(z[i][1] + MITLESEN_NACHLAUF, i + 1 < n ? z[i + 1][0] : Infinity);
    if(t < ende) akt = i;
  }
  const gelesen = akt >= 0 ? akt : begonnen;
  if(akt === m.akt && gelesen === m.gelesen) return;
  m.woerter.forEach((w, j) => {
    w.classList.toggle('mitlesen', j === akt);
    w.classList.toggle('gelesen', j < gelesen);
  });
  const neu = akt >= 0 && akt !== m.akt;
  m.akt = akt; m.gelesen = gelesen;
  if(neu) mitlesenImBlick(m.woerter[akt], akt > 0 ? m.woerter[akt - 1] : null);
}
/* Ist die Geschichte laenger als der Bildschirm (die laengste hat 85
   Woerter), bleibt das aktuelle Wort im Blick. Gescrollt wird erst, wenn es
   den sichtbaren Bereich verlaesst, und dann gleich in die Mitte - so
   rueckt die Seite einmal je halbem Bildschirm nach, nicht bei jeder
   Zeile. Und nur, wenn das Wort davor noch zu sehen war: wer beim Zuhoeren
   zu den Fragen hinuntergescrollt ist, wird nicht zurueckgerissen. Sanft
   nur mit Animationen (Schalter und Geraeteeinstellung, wie bei den
   Kacheln). */
function mitlesenImBlick(el, davor){
  try{
    /* h in den Einheiten von getBoundingClientRect, siehe rectFaktor() */
    let h = (window.innerHeight || document.documentElement.clientHeight) / rectFaktor();
    /* Steht die Blase eines angetippten Wortes unten im Bild (V2,
       14.11.2026), endet der freie Bereich an ihrer Oberkante. Steht sie an
       ihrem Platz unter dem Text, liegt ohnehin jedes Wort darueber. */
    const blase = $('rBubble');
    if(blase && !blase.hidden){
      const o = blase.getBoundingClientRect().top;
      if(o > 0 && o < h) h = o;
    }
    const r = el.getBoundingClientRect();
    if(r.top >= 0 && r.bottom <= h) return;
    if(davor){
      const d = davor.getBoundingClientRect();
      if(d.bottom <= 0 || d.top >= h) return;
    }
    el.scrollIntoView({block: 'center', behavior: kachelnRuhig() ? 'auto' : 'smooth'});
  }catch(e){}
}
/* ---- Anhalten, weitermachen, Tempo ----
   Stopp setzt an den Anfang zurueck, Pause nicht: `currentTime` bleibt
   stehen, und weil `pausiert` gesetzt ist, faellt der Knopf nicht auf
   "Vorlesen" zurueck. Die Computerstimme am PC kann beides von Haus aus;
   auf dem Handy gibt es sie nicht, dort laeuft alles ueber die Aufnahmen. */
function tonPause(){
  if(pausiert) return false;
  if(hasTTS && speechSynthesis.speaking && !speechSynthesis.paused){
    pausiert = true; try{ speechSynthesis.pause(); }catch(e){} return true;
  }
  if(spieler.src && !spieler.paused){
    pausiert = true; try{ spieler.pause(); }catch(e){} return true;
  }
  return false;            // es lief gar nichts - der Aufrufer stellt ab
}
function tonWeiter(){
  if(!pausiert) return false;
  pausiert = false;
  if(hasTTS && speechSynthesis.paused){ try{ speechSynthesis.resume(); }catch(e){} return true; }
  const p = spieler.play();
  /* Laesst das Geraet nicht weiterspielen, lieber sauber abstellen als den
     Knopf auf "Pause" stehenlassen - sonst reagiert er scheinbar nicht mehr.
     Auf dem iPhone steht die Ablehnung im Ton-Protokoll (15.11.2026). */
  if(p && p.catch) p.catch(e=>{ if(IST_IOS) spielerAbgelehnt(e, 'weiter'); stilleBitte(); });
  return true;
}
function setzeTempo(v){
  tempo = v;
  try{ localStorage.setItem('zmaj_tempo', String(v)); }catch(e){}
  /* Ein laufendes Vorlesen aendert sich sofort mit, ohne Neustart, ein
     angehaltenes geht im neuen Tempo weiter. laeuftVor steht nur beim
     Vorlesen: ein angetipptes Wort bleibt normal (05.11.2026). */
  if(laeuftVor) try{ spieler.playbackRate = v; }catch(e){}
  // Beide Leisten - die in der Geschichte und die in den Einstellungen.
  document.querySelectorAll('.tempo button').forEach(b =>
    b.setAttribute('aria-pressed', String(parseFloat(b.dataset.tempo) === v)));
}
function tempoLeiste(id, mitWort){
  const box = $(id); if(!box) return;
  // 0,5 im Deutschen, 0.5 im Englischen - sonst liest es sich wie ein Fehler.
  const komma = SPRACHE === 'en' ? '.' : ',';
  // In den Einstellungen steht "Tempo" schon als Ueberschrift der Zeile.
  box.innerHTML = (mitWort ? '<span class="tlabel">'+esc(t('set.tempo'))+'</span>' : '')+
    TEMPI.map(v => '<button type="button" data-tempo="'+v+'" aria-pressed="'+(v===tempo)+'">'+
      String(v).replace('.', komma)+'\u00d7</button>').join('');
  box.querySelectorAll('button').forEach(b => b.addEventListener('click', e=>{
    // Nicht durchreichen: in der Geschichte haengt darueber der Horcher,
    // der zur naechsten Frage blaettert.
    e.stopPropagation(); setzeTempo(parseFloat(b.dataset.tempo));
  }));
}
/* Die Hoer-Aufgaben spielen das Wort kurz verzoegert von selbst ab, damit
   der Bildschirm erst steht. Verlaesst man die Lektion in genau dieser
   Viertelsekunde, kaeme der Ton NACH dem Abstellen - und liefe wieder in
   die naechste Ansicht hinein. Deshalb eine Marke: was vor dem letzten
   stilleBitte() bestellt wurde, wird nicht mehr ausgeliefert. */
/* Seit dem 26.10.2026: ok (true/false) heisst "nach einer Antwort". Liegt
   der Puffer bereit, kommt das Wort dann auf der Uhr des Rueckmeldetons
   (rueckTon), ohne ok (neues Wort, Hoerfrage) sofort - siehe "Wann das
   Wort kommt, Teil 2" gleich darunter. Sonst wie bisher: ms warten, dann
   speak(). Die Marke gilt fuer beide Wege: ein bestelltes Wort ueber
   WebAudio stellt stilleBitte() ab (waStopp), bevor es zu hoeren ist. */
function spaeterSprechen(text, ms, ok){
  const marke = ++tonMarke;
  const ton = ok === undefined ? null : rueckTonNehmen();
  const wann = ton && soundOn ? ton.zeit + (ton.art === 'no' ? ABSTAND_NO : ABSTAND_OK) : 0;
  if(pufferSpielen(text, null, wann)) return;
  setTimeout(()=>{ if(marke === tonMarke) speak(text); }, ms);
}
var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
