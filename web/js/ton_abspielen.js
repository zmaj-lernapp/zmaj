/* ---- Wann das Wort kommt (22.10.2026) ----
   Ajdin: "der sprecher sagt viel zu spaet die woerter oder saetze die
   muessen frueher kommen man wartet zu lange bis er anfaengt". Nach einer
   Antwort war das Wort am PC erst nach rund 0,7 s zu hoeren: 450 ms
   Wartezeit, rund 70 ms Abspielweg und rund 190 ms Stille am Anfang der
   Aufnahme (die kuerzt seitdem app_bauen.py im Paket, siehe TON_ANFANG
   dort). Mit allem zusammen sind es jetzt rund 0,29 s.
   Gewartet wird jetzt nur so lange, dass das Wort nicht in den
   Rueckmeldeton hineinredet: 'ok' ist bis etwa 0,2 s hoerbar, 'no' bis
   etwa 0,27 s (siehe sound()). Abspielweg und die kurze Reststille kommen
   noch dazu - das Wort setzt gleich nach dem Ton ein, ueberdeckt ihn aber
   nicht. Ohne Toene gibt es nichts abzuwarten.
   Beim Erscheinen einer Aufgabe (neues Wort, Hoerfrage) waren es 250 bzw.
   300 ms, damit der Bildschirm erst steht. Der steht nach ein, zwei
   Bildern - 100 ms reichen. */
const nachAntwort = ok => soundOn ? (ok ? 180 : 250) : 40;
const BEIM_ERSCHEINEN = 100;
/* ---- Wann das Wort kommt, Teil 2 (26.10.2026) ----
   Ajdin: "die sprecher stimme kommt immernoch etwas zu langsam". Auf seinem
   S21 gemessen, vom Tippen bis zum ersten hoerbaren Laut: nach einer
   richtigen Antwort 273 ms (bis 367), nach einer falschen 326 ms, beim
   Erscheinen eines neuen Worts 199 ms. Davon sind 180, 250 und 100 ms die
   Wartezeiten oben, der Rest ist der Anlauf des spielers (Datei holen,
   dekodieren, Ausgabe anwerfen) - und der schwankt, weil er erst nach dem
   Zeitgeber beginnt.
   Jetzt laufen Woerter und Saetze ueber WebAudio, und der spieler ist der
   Rueckfall:
   - Erscheint eine Aufgabe, wird ihr Wort schon geholt und dekodiert
     (pufferLaden(), 10-37 ms auf dem S21, waehrend man noch liest), ebenso
     das der naechsten Aufgabe - genau der Text, den die Aufgabe spricht
     (aufgabeText() vor renderTask()). Sechs Puffer reichen fuer die
     aktuelle, die naechste und die Wiederholungen.
   - Nach einer Antwort wird das Wort im selben Augenblick bestellt wie der
     Rueckmeldeton, auf dessen Uhr: Start bei Tonbeginn + ABSTAND_OK bzw.
     ABSTAND_NO, in der Datei ab kurz vor dem ersten Laut (Vorlauf). Kein
     Zeitgeber und kein Anlauf dazwischen. Ohne Toene sofort.
   - Neues Wort und Hoerfrage: sofort, sobald die Aufgabe steht.
   - Der Abstand ist gemessen (abstand_messen.py, Arbeitsordner
     sprecher_einbau): sound('ok') und sound('no') offline gerendert,
     Huellkurve und Welle. 'ok' ist ab 171 ms nach Tonbeginn dauerhaft
     leiser als -30 dBFS, 'no' ab 191 ms. Die Datei startet 5 ms vor ihrem
     ersten Laut (VORLAUF_RAND) - also 167 und 186 ms: setzt das Wort ein,
     ist der Ton hoechstens noch -30 dBFS laut. Je der kleinste solche Wert.
   - Der Vorlauf ist die Stille am Anfang der Datei, gemessen am Puffer
     selbst (erster Wert ueber -65 dBFS; bei den Emir-Woertern im Paket 25
     bis 41 ms, meist 30). Sie wird uebersprungen statt abgewartet.
   Am PC nachgemessen (Median vom Tippen bis zum ersten hoerbaren Laut,
   Messweg 'eingebaut' aus werkzeuge/handy_messen/mess.js, Opus-Dateien
   wie im Paket): nach richtig 339 -> 226 ms, nach falsch 420 -> 248 ms,
   neues Wort 273 -> 68 ms. Auf dem Handy misst es handy_messen.py mit den
   Gruppen eingebaut_*.
   Rueckfall auf den spieler wie bisher (Wartezeiten oben), wenn der Puffer
   noch nicht da ist, es keinen AudioContext gibt oder die Datei nicht laedt.
   Die Geschichten bleiben ganz beim spieler (sprichMitSpieler): Mitlesen,
   Pause und Weiterlesen haengen an ihm, und das Tempo auch - WebAudio kennt
   kein preservesPitch, 0,75x klaenge tiefer. Bis zum 05.11.2026 war deshalb
   auch ein Tempo ungleich 1 ein Grund fuer den Rueckfall, in jeder Lektion
   (siehe "---- Tempo ----"). */
const ABSTAND_OK = 0.167, ABSTAND_NO = 0.186;   // s ab Tonbeginn bis zum Start der Datei
const VORLAUF_SCHWELLE = Math.pow(10, -65 / 20), VORLAUF_RAND = 0.005;
const PUFFER_MAX = 6;
/* Datei -> {buf, vorlauf}; buf ist null, solange sie laedt. Die
   Reihenfolge der Map ist die der letzten Benutzung, vorn faellt heraus. */
const puffer = new Map();
/* Der AudioContext fuer Toene und Woerter. Seit dem 26.10.2026 auch bei
   Toenen aus - die Woerter laufen darueber.
   Seit dem 05.11.2026 entsteht er nur noch hier und mit latencyHint
   'playback'. Auf Ajdins S21 (Android 15, WebView 156) blieb an dem Tag der
   Ton stumm. Hoertest: ein AudioContext mit Standard-Latenz (baseLatency
   0,004 s) war stumm, obwohl state 'running' war und kein Fehler kam. Mit
   'playback' (baseLatency 0,021 s) und ueber den spieler war er zu hoeren.
   Danach kam der Ton von selbst zurueck, die Ursache im Geraet kennen wir
   also nicht. Aber nur der kurze Puffer war stumm, und die App merkt davon
   nichts - also nehmen wir ihn nicht mehr. Der Preis: auf dem S21 kommen
   Ton und Wort rund 17 ms spaeter aus dem Lautsprecher, beide gleich viel.
   Ihr Abstand (ABSTAND_OK, ABSTAND_NO, siehe "Wann das Wort kommt, Teil 2")
   bleibt: beide sind auf der Uhr von actx bestellt und laufen durch dieselbe
   Ausgabe. Am PC in Echtzeit nachgemessen, mit beiden Einstellungen gleich:
   das Wort setzt 171 bzw. 189 ms nach Tonbeginn ein, der Ton ist dann bei
   rund -30 dBFS (test_wort_webaudio.py). Wirft ein Geraet bei der Option,
   geht es ohne sie; geht auch das nicht, bleibt actx null, und der spieler
   spricht.
   Auf iPhone und iPad entsteht er seit dem 15.11.2026 nur noch im
   Fingertipp (tonInGeste), siehe "Ton im Fingertipp" gleich darunter.
   Ausserhalb einer Geste bleibt actx dort null, und der spieler spricht. */
function tonKontext(){
  if(actx) return actx;
  if(IST_IOS && !tonInGeste) return null;
  const Kontext = window.AudioContext || window.webkitAudioContext;
  if(!Kontext) return null;
  try{ actx = new Kontext({latencyHint: 'playback'}); }
  catch(e){ try{ actx = new Kontext(); }catch(e2){} }
  if(IST_IOS && actx) tonKontextNeu(actx);
  return actx;
}
/* ---- Ton im Fingertipp: iPhone und iPad (15.11.2026) ----
   Ajdin mit TestFlight 1.3 (Build 3) auf dem iPhone 11 mit iOS 16.6.1:
   nie Ton, kein Wort und kein Piepen, auch nicht beim ersten Wort,
   Lautstaerke normal, Lautlos-Schalter aus. Im Simulator (iOS 26.5) war
   nie etwas zu hoeren, dort wurde nur dekodiert. Am Geraet gemessen ist
   nichts. Die Diagnose vom 14./15.11.2026 fand drei Stellen, an denen ein
   stummer AudioContext unbemerkt bleibt:
   - Er entstand ohne Fingertipp rund 2,4 s nach dem Start (tonVorwaermen),
     nachdem navigator.audioSession.type schon auf 'playback' stand.
     Capacitor erlaubt Ton ohne Geste, also meldete er sofort 'running'.
     Aus WKWebView sind Faelle bekannt, in denen so ein Kontext 'running'
     meldet und stumm bleibt; geholfen hat dort der Start bzw. resume() im
     Fingertipp (bugs.webkit.org 240646, 256075).
   - sound() setzte ihn nur bei 'suspended' fort. WebKit kennt dazu
     'interrupted' (Anruf, Siri, Heimknopf, eine andere Tonquelle).
   - pufferSpielen() vertraute 'running' blind. Es gab keinen Rueckfall auf
     den spieler, und eine Computerstimme hat iOS in der App nicht.
   Deshalb auf iOS, fuer alle Fassungen ab 16.4:
   1. Der Kontext entsteht nur im Fingertipp. tonEntsperren() haengt in der
      Capture-Phase an touchend, pointerup und click, laeuft also vor jedem
      anderen Klick, und tut synchron in der Geste: anlegen oder fortsetzen,
      einen Puffer mit einem einzigen Sample abspielen, den spieler einmal
      stumm anspielen.
   2. Fortgesetzt wird bei jedem Zustand ausser 'running' und 'closed'.
   3. Die Uhr wird geprueft (tonUhrLesen): steht currentTime trotz 'running'
      gegen die Wanduhr, ist der Kontext tot. Er wird geschlossen, der
      naechste Tipp legt einen neuen an. Woerter laufen erst ueber WebAudio,
      wenn seine Uhr nachweislich laeuft, bis dahin ueber den spieler.
   4. Lehnt der spieler ab, steht das im Ton-Protokoll (TON_PROTOKOLL und
      Konsole), und der naechste Tipp spielt ihn neu an.
   5. navigator.audioSession.type = 'playback' erst im ersten Tipp und nur
      ab iOS 17, darunter laufen die Woerter ueber den spieler - siehe
      tonSitzung().
   Android und die Web-Demo bleiben, wie sie waren: dort haengt hier
   nichts (tests_e2e/test_ios_ton.py prueft beides). */
let tonInGeste = false;     // nur waehrend tonEntsperren(): dann legt tonKontext() auf iOS an
let tonFrei = null;         // der Kontext, fuer den in einer Geste der Ein-Sample-Puffer lief
let spielerFrei = false;    // der spieler hat auf iOS schon einmal gespielt
let sitzungGesetzt = false; // tonSitzung() lief schon
let tonInaktiv = false;     // die App ist nur inaktiv (Kontrollzentrum, Siri, Anruf), siehe "Zurueck in der App"
/* Die letzte Probe der Kontext-Uhr: {ctx, ct, wand, lebt}. lebt heisst: die
   Uhr ist seit dem Anlegen bzw. dem letzten Zustandswechsel nachweislich
   gelaufen. Verglichen wird erst nach UHR_WAND Sekunden Wanduhr; steht sie
   dann um weniger als UHR_MIN weiter, ist der Kontext tot. Im Hintergrund
   und bei jedem Zustandswechsel beginnt die Probe neu - iOS haelt dort
   die Ausgabe an, das ist kein Fehler. */
let tonUhr = null;
const UHR_WAND = 0.5, UHR_MIN = 0.05;
/* Ton-Protokoll, nur iOS: die letzten 60 Ereignisse, dazu die Konsole. Am
   Geraet mit dem Web-Inspektor lesbar; es geht nirgendwohin. */
const TON_PROTOKOLL = [];
function tonMerken(was){
  TON_PROTOKOLL.push(Math.round(performance.now()) + ' ' + was);
  if(TON_PROTOKOLL.length > 60) TON_PROTOKOLL.shift();
  try{ console.info('[Zmaj Ton] ' + was); }catch(e){}
}
/* Die iOS-Fassung, 0 = unbekannt. WKWebView meldet "iPhone OS 16_6_1" bzw.
   auf dem iPad "CPU OS 16_6" (die Huelle verlangt mit preferredContentMode
   "mobile" die Handy-Kennung). Zeigt sich ein iPad doch als Mac ohne
   iOS-Fassung, entscheidet Set.prototype.union, das es erst ab Safari 17
   gibt (MDN browser-compat-data). Ab iOS 26 friert WebKit die Fassung im UA ein (18_6,
   18_6_2, spaeter 18_7; bugs.webkit.org 298473) - auch das ist ab 17. */
const IOS_FASSUNG = (()=>{
  const m = /(?:iPhone|CPU) OS (\d+)_/.exec(navigator.userAgent || '');
  return m ? +m[1] : 0;
})();
const IOS_AB_17 = IOS_FASSUNG ? IOS_FASSUNG >= 17 : typeof Set.prototype.union === 'function';
/* navigator.audioSession.type = 'playback': Ton auch mit Lautlos-Schalter,
   wie ein Musikspieler. Erst im ersten Fingertipp, vor dem Anlegen des
   Kontexts, und nur ab iOS 17. Recherche 15.11.2026:
   - Safari 16.4 brachte nur "a subset of the AudioSession Web API"
     (webkit.org/blog/13966).
   - Der WebKit-Entwickler J.-Y. Avenard, bugs.webkit.org 237322, Kommentar
     6 (25.09.2024): "Since iOS 17, you can set the audio session type to
     playback".
   - Ein Bericht aus der Praxis, nach type = 'playback' auf dem iPhone:
     "no success/failure sounds at all, ringer on or off", behoben durch
     Zuruecknehmen (github.com/juancho0202/inburgering-a2-cursus/pull/16).
   - WebKit 16.6 gleicht Unterbrechungen zwischen Web- und GPU-Prozess noch
     nicht ab, 17 schon (Quellvergleich der Tags WebKit-7615.3.12.11.3 und
     WebKit-7616.2.9.11.9, Diagnose 15.11.2026).
   Belegt ist der stumme Kontext unter 16 damit nicht, aber er kann es sein,
   und das iPhone 11 mit 16.6.1 war genau so stumm. Also bleibt die Sitzung
   unter 17 beim Standard. Dann schaltet der Lautlos-Schalter WebAudio stumm
   (bugs.webkit.org 237322), <audio> aber nicht (bugs.webkit.org 251532) -
   deshalb sprechen die Woerter unter iOS 17 ueber den spieler, und nur die
   Pieptoene haengen am Schalter. */
function tonSitzung(){
  if(sitzungGesetzt) return;
  sitzungGesetzt = true;
  const s = navigator.audioSession;
  if(!s){ tonMerken('audioSession: gibt es nicht'); return; }
  if(!IOS_AB_17){ tonMerken('audioSession: bleibt ' + s.type + ' (iOS ' + (IOS_FASSUNG || '?') + ')'); return; }
  try{ s.type = 'playback'; tonMerken('audioSession: playback'); }
  catch(e){ tonMerken('audioSession: ' + (e && e.name)); }
}
function tonKontextNeu(c){
  tonUhr = null; tonFrei = null;
  tonMerken('AudioContext neu: ' + c.state + ', ' + c.sampleRate + ' Hz, iOS ' + (IOS_FASSUNG || '?'));
  try{ c.addEventListener('statechange', ()=>{
    if(c !== actx) return;
    tonUhr = null;
    tonMerken('AudioContext: ' + c.state);
    if(c.state === 'running') tonBaldPruefen('wieder an');
  }); }catch(e){}
  tonBaldPruefen('nach dem Anlegen');
}
/* Zweimal nachsehen, damit die Woerter bald ueber WebAudio laufen und nicht
   erst nach dem naechsten Tipp: einmal, wenn er laeuft (erste Probe), und
   eine gute halbe Sekunde spaeter (der Beweis). */
function tonBaldPruefen(wo){
  setTimeout(()=>tonPruefen(wo), 150);
  setTimeout(()=>tonPruefen(wo), 150 + UHR_WAND * 1000 + 250);
}
/* 'lebt', 'unklar' oder 'tot' - nur auf iOS gerufen. Solange die App nur
   inaktiv ist (tonInaktiv, siehe "Zurueck in der App"), zaehlt die Probe
   nicht: iOS haelt die Ausgabe dort an, ohne den Zustand zu wechseln. */
function tonUhrLesen(){
  const c = actx;
  if(!c || c.state !== 'running' || document.hidden || tonInaktiv){ tonUhr = null; return 'unklar'; }
  const jetzt = performance.now(), ct = c.currentTime, u = tonUhr;
  if(!u || u.ctx !== c){ tonUhr = {ctx: c, ct, wand: jetzt, lebt: false}; return 'unklar'; }
  if(jetzt - u.wand < UHR_WAND * 1000) return u.lebt ? 'lebt' : 'unklar';
  if(ct - u.ct < UHR_MIN) return 'tot';
  tonUhr = {ctx: c, ct, wand: jetzt, lebt: true};
  return 'lebt';
}
/* true: die Uhr laeuft nachweislich. Ein toter Kontext wird geschlossen. */
function tonPruefen(wo){
  const z = tonUhrLesen();
  if(z === 'tot') tonWeg(wo);
  return z === 'lebt';
}
/* Schliessen; angelegt wird erst im naechsten Fingertipp. */
function tonWeg(wo){
  const alt = actx; if(!alt) return;
  const u = tonUhr;
  tonMerken('AudioContext tot (' + wo + '): ' + alt.state + ', Uhr ' +
            (u ? (alt.currentTime - u.ct).toFixed(3) + ' s in ' + ((performance.now() - u.wand) / 1000).toFixed(2) + ' s' : '?'));
  waStopp();
  actx = null; tonUhr = null; tonFrei = null;
  /* Beide stehen auf der Uhr des alten Kontexts. Ein Wort, das darauf
     bestellt wuerde, kaeme beim neuen erst viel spaeter. */
  rueckTon = null; tonNull = null;
  try{ const p = alt.close(); if(p && p.catch) p.catch(()=>{}); }catch(e){}
}
function tonWecken(c, wo){
  try{
    const p = c.resume();
    if(p && p.catch) p.catch(e => tonMerken('resume (' + wo + ') abgelehnt: ' + (e && e.name)));
  }catch(e){ tonMerken('resume (' + wo + '): ' + (e && e.name)); }
}
/* Darf ein Wort jetzt ueber WebAudio? Unter iOS 17 nie (siehe tonSitzung),
   sonst nur mit nachweislich laufender Uhr. Laeuft er nicht ('suspended',
   'interrupted'), wird er geweckt, und das Wort kommt gleich ueber den
   spieler - nicht erst nach WECKEN_MS. */
function tonFuerWoerter(){
  if(!IOS_AB_17) return false;
  if(actx.state !== 'running'){ tonWecken(actx, 'wort'); return false; }
  return tonPruefen('wort');
}
function tonEntsperren(e){
  if(!e || !e.isTrusted) return;     // ein .click() aus dem Skript ist kein Fingertipp
  tonInaktiv = false;                 // wer tippt, hat die App vor sich (falls 'appStateChange' fehlte)
  tonSitzung();
  if(actx && actx.state === 'closed') actx = null;
  if(actx) tonPruefen('tipp');        // tot: geschlossen und gleich neu
  if(!actx){
    tonInGeste = true;
    try{ tonKontext(); } finally { tonInGeste = false; }
  }
  const c = actx;
  if(c){
    const gesperrt = c.state !== 'running';
    if(gesperrt) tonWecken(c, 'tipp');
    if(gesperrt || tonFrei !== c){
      try{
        const q = c.createBufferSource();
        q.buffer = c.createBuffer(1, 1, c.sampleRate);
        q.connect(c.destination);
        q.start(0);
        tonFrei = c;
      }catch(err){ tonMerken('Ein-Sample-Puffer: ' + (err && err.name)); }
    }
  }
  if(!spielerFrei) spielerEntsperren();
}
/* Den spieler einmal in einer Geste anspielen, stumm mit der Stille aus
   stilleWav() wie beim Vorwaermen. Danach darf er auch aus einem Zeitgeber
   heraus spielen (spaeterSprechen), selbst wenn WebKit dafuer eine Geste
   verlangt. Laeuft gerade etwas oder ist eine Geschichte angehalten, bleibt
   er in Ruhe. Ein echtes Wort im selben Tipp bricht das Anspielen ab
   (spieleDatei) - dann ist er durch das Wort frei. */
function spielerEntsperren(){
  if(!spieler.paused || pausiert || laeuftVor || vorwaermen) return;
  stummAnspielen(err => {
    if(!err){ spielerFrei = true; return; }
    if(err.name !== 'AbortError') spielerAbgelehnt(err, 'anspielen');
  });
}
/* Eine Ablehnung nicht verschlucken (15.11.2026): ins Protokoll, und der
   naechste Tipp spielt den spieler neu an. */
function spielerAbgelehnt(e, wo){
  spielerFrei = false;
  tonMerken('spieler.play (' + wo + ') abgelehnt: ' + ((e && (e.name || e.message)) || e));
}
/* ---- Zurueck in der App: iPhone und iPad (15.11.2026, Build 4) ----
   Ajdin am iPhone 11 nach dem Update auf iOS 27.2.1, TestFlight 1.3 Build 3
   (noch ohne "Ton im Fingertipp"): nach einem frischen Start Ton, nach dem
   Schliessen ohne Beenden und Wiederoeffnen keiner mehr, "ka mal
   funktioniert es mal nicht". Eine Sprechuebung brachte ihn zurueck.
   iOS schaltet die Audio-Sitzung einer App ab, die im Hintergrund
   angehalten wird, und beim Zurueckkommen schaltete sie niemand wieder ein
   - ausser der Spracherkennung (setActive in ZmajSprache.swift). Das tut
   seit Build 4 die Huelle bei jeder Rueckkehr (ZmajTon.swift). Die Seite
   tut ihren Teil:
   1. Zurueck heisst: sichtbar (visibilitychange), 'resume' oder
      'appStateChange' mit isActive vom Plugin App. Alle rufen tonZurueck(),
      oft kurz nacheinander; es zaehlt nur die letzte Probe (tonRueckkehr).
   2. Laeuft der AudioContext nicht ('suspended', 'interrupted'), wird er
      fortgesetzt. Ein Wort, das auf seiner stehenden Uhr noch bestellt
      war, faellt vorher weg (waStopp) - es kaeme sonst verspaetet ueber das,
      was als Naechstes klingt.
   3. Laeuft er nach RUECKKEHR_MS immer noch nicht, wird er geschlossen, und
      der naechste Tipp legt einen neuen an. Laeuft er, beweist die
      Wanduhr-Probe wie nach dem Anlegen, dass seine Uhr geht (tonBaldPruefen,
      bei einem Zustandswechsel ueber 'statechange'); steht sie, ebenso
      schliessen. Bis dahin sprechen die Woerter ueber den spieler.
   4. Der naechste Tipp spielt den Ein-Sample-Puffer und den spieler neu an
      (tonFrei, spielerFrei) - in der Zeit draussen kann iOS die Sitzung
      gewechselt haben. Laeuft gerade etwas oder ist eine Geschichte
      angehalten, bleibt der spieler in Ruhe (spielerEntsperren).
   5. Ist die App nur inaktiv (Kontrollzentrum, Siri, Anruf), bleibt die
      Seite sichtbar. Dann zaehlt die Uhr-Probe nicht (tonInaktiv): iOS haelt
      die Ausgabe an, ohne den Zustand zu wechseln, das ist kein toter
      Kontext.
   6. Haelt das System eine vorgelesene Geschichte an, merkt sie sich die
      Stelle wie beim Wechsel in den Hintergrund, und "Vorlesen" macht dort
      weiter (tonVonAussenAngehalten). Noch einmal pause() dazu: WebKit setzt
      eine Wiedergabe, die vor einer Unterbrechung lief, danach sonst von
      selbst fort (mayResumePlayback). Dann liefe die Geschichte weiter,
      waehrend der Knopf schon wieder "Vorlesen" zeigt, und ein Tipp darauf
      begaenne sie von vorn.
   Android und die Web-Demo: nichts davon (IST_IOS, tests_e2e/test_ios_ton.py). */
let tonRueckkehr = 0;          // zaehlt die Rueckkehr-Proben; nur die letzte gilt
const RUECKKEHR_MS = 1000;     // so lange darf resume() nach der Rueckkehr brauchen
function tonWirdInaktiv(wo){
  tonInaktiv = true; tonUhr = null;
  tonMerken('App ' + wo);
}
function tonZurueck(wo){
  tonInaktiv = false; tonUhr = null;
  tonFrei = null; spielerFrei = false;       // der naechste Tipp spielt beides neu an
  const nr = ++tonRueckkehr, c = actx;
  if(!c){ tonMerken('zurueck (' + wo + '), noch ohne AudioContext'); return; }
  tonMerken('zurueck (' + wo + '): AudioContext ' + c.state);
  if(c.state === 'closed'){ actx = null; return; }
  if(c.state === 'running'){ tonBaldPruefen('zurueck'); return; }
  waStopp();
  tonWecken(c, 'zurueck');
  setTimeout(()=>{
    if(nr !== tonRueckkehr || c !== actx || document.hidden || tonInaktiv) return;
    if(c.state !== 'running') tonWeg('zurueck, ' + c.state);
  }, RUECKKEHR_MS);
}
function tonVonAussenAngehalten(){
  const t = +spieler.currentTime || 0, d = +spieler.duration || 0;
  if(spieler.ended || (d && t >= d - 0.25)) return;     // das Ende der Aufnahme, kein Anhalten
  if(spieler.src && t > 0) geschichteStelle = {datei: spieler.src, sekunde: t};
  tonMerken('Geschichte von aussen angehalten bei ' + t.toFixed(1) + ' s');
  try{ spieler.pause(); }catch(e){}
}
if(IST_IOS){
  ['touchend', 'pointerup', 'click'].forEach(n =>
    document.addEventListener(n, tonEntsperren, {capture: true, passive: true}));
  spieler.addEventListener('playing', ()=>{ spielerFrei = true; });
  document.addEventListener('visibilitychange', ()=>{
    tonUhr = null;
    if(!document.hidden) tonZurueck('sichtbar');
  });
  /* Das Plugin App der Huelle (AppPlugin.swift in @capacitor/app 8.1.1):
     'appStateChange' kommt auch, wenn die App nur inaktiv wird - die Seite
     bleibt dann sichtbar, und visibilitychange schweigt. 'pause' und
     'resume' kommen beim Wechsel in den Hinter- und Vordergrund. */
  const appP = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.App;
  const appHoeren = (name, f) => {
    try{ const h = appP.addListener(name, f); if(h && h.catch) h.catch(()=>{}); }catch(e){}
  };
  if(appP && typeof appP.addListener === 'function'){
    appHoeren('appStateChange', d => {
      if(d && d.isActive === false) tonWirdInaktiv('inaktiv');
      else if(d && d.isActive === true) tonZurueck('aktiv');
    });
    appHoeren('pause', () => tonWirdInaktiv('im Hintergrund'));
    appHoeren('resume', () => tonZurueck('im Vordergrund'));
  }
}
/* Sekunden bis kurz vor dem ersten Laut im Puffer. */
function vorlaufMessen(buf){
  let erst = Infinity;
  try{
    for(let k = 0; k < buf.numberOfChannels; k++){
      const d = buf.getChannelData(k), n = Math.min(d.length, erst);
      for(let i = 0; i < n; i++) if(d[i] > VORLAUF_SCHWELLE || d[i] < -VORLAUF_SCHWELLE){ erst = i; break; }
    }
  }catch(e){ return 0; }
  return erst === Infinity ? 0 : Math.max(0, erst / buf.sampleRate - VORLAUF_RAND);
}
/* Holt und dekodiert eine Datei in den Zwischenspeicher. Schlaegt es
   fehl, bleibt nichts liegen - dann spielt der spieler. */
function pufferLaden(datei){
  if(!datei) return;
  const da = puffer.get(datei);
  if(da){ puffer.delete(datei); puffer.set(datei, da); return; }
  if(IST_IOS && !IOS_AB_17) return;   // unter iOS 17 sprechen die Woerter ueber den spieler (tonSitzung)
  const ctx = tonKontext();           // iOS: nur, wenn ein Tipp ihn schon angelegt hat
  if(!ctx || typeof fetch !== 'function') return;
  const p = {buf: null, vorlauf: 0};
  puffer.set(datei, p);
  while(puffer.size > PUFFER_MAX) puffer.delete(puffer.keys().next().value);
  /* iPhone und iPad (30.10.2026, Cloud-Lauf 8): Capacitor iOS liefert
     Tondateien (.mp3, .m4a ...) ohne HTTP-Status aus - fetch() meldet dann
     status 0 und ok false, obwohl die Datei ganz da ist
     (WebViewAssetHandler.swift: fuer isMediaExtension eine blosse
     URLResponse statt HTTPURLResponse 200). Ohne diese Ausnahme lief auf
     iOS kein einziges Wort ueber WebAudio, alles fiel auf den spieler
     zurueck. Fehlt die Datei wirklich, scheitert decodeAudioData an den
     leeren Daten und es kommt derselbe Weg. Android und Browser bleiben
     bei ok. */
  fetch('audio/' + datei)
    .then(a => { if(!a.ok && !(IST_IOS && a.status === 0)) throw new Error('HTTP ' + a.status); return a.arrayBuffer(); })
    .then(daten => ctx.decodeAudioData(daten))
    .then(buf => { p.vorlauf = vorlaufMessen(buf); p.buf = buf; })
    .catch(() => { if(puffer.get(datei) === p) puffer.delete(datei); });
}
function pufferNehmen(datei){
  const p = puffer.get(datei);
  if(!p || !p.buf) return null;
  puffer.delete(datei); puffer.set(datei, p);
  return p;
}
/* Der Rueckmeldeton dieser Antwort - nur einmal, und nur frisch. */
function rueckTonNehmen(){
  const t = rueckTon; rueckTon = null;
  return t && performance.now() - t.um < 1000 ? t : null;
}
function waStopp(){
  const q = waQuelle; waQuelle = null;
  if(q){ q.onended = null; try{ q.stop(); }catch(e){} }
}
/* Spielt die Aufnahme zu text ueber WebAudio, wenn ihr Puffer bereitliegt.
   wann: Startzeit auf der Uhr von actx, 0 = sofort. false heisst: geht
   nicht, der Aufrufer nimmt den spieler. Es laeuft immer nur ein Wort:
   ein laufendes oder bestelltes wird abgestellt, der spieler angehalten
   (nicht waehrend des stummen Vorwaermens, das endet von selbst). */
function pufferSpielen(text, fertig, wann){
  if(!actx || actx.state === 'closed') return false;
  const datei = audioDatei(text);
  const p = datei ? pufferNehmen(datei) : null;
  if(!p) return false;
  /* iPhone: nur mit nachweislich laufender Uhr, sonst gleich der spieler
     (15.11.2026, "Ton im Fingertipp"). */
  if(IST_IOS && !tonFuerWoerter()) return false;
  let q;
  try{
    q = actx.createBufferSource();
    q.buffer = p.buf;
    q.connect(actx.destination);
  }catch(e){ return false; }
  waStopp();
  pausiert = false;
  if(!spieler.paused && !vorwaermen) try{ spieler.pause(); }catch(e){}
  q.onended = ()=>{ if(waQuelle === q){ waQuelle = null; if(fertig) try{ fertig(); }catch(e){} } };
  waQuelle = q;
  try{ q.start(Math.max(wann || 0, actx.currentTime), p.vorlauf); }
  catch(e){ waQuelle = null; return false; }
  if(actx.state !== 'running') kontextWecken(q, text, fertig);
  return true;
}
/* Android legt den AudioContext nach rund 30 s Stille still. Dann vor dem
   Start fortsetzen - das Wort ist schon bestellt und kommt, sobald er
   laeuft. Laeuft er nach WECKEN_MS noch immer nicht (ein Browser ohne
   Geste), kommt das Wort ueber den spieler, und die Quelle wird
   abgestellt, damit sie nicht spaeter doch noch hineinredet. */
const WECKEN_MS = 250;
function kontextWecken(q, text, fertig){
  const marke = tonMarke, ctx = actx;
  try{ const p = ctx.resume(); if(p && p.catch) p.catch(()=>{}); }catch(e){}
  setTimeout(()=>{
    if(waQuelle !== q || marke !== tonMarke || ctx.state === 'running') return;
    waStopp(); sprichMitSpieler(text, fertig);
  }, WECKEN_MS);
}
/* Das Wort fuer nach der Antwort schon beim Erscheinen der Aufgabe in den
   spieler zu legen (Vorladen), war ebenfalls gebaut und gemessen: 0-3 ms
   frueher, auch mit vierfach gedrosselter CPU. Der Rest des Abspielwegs
   ist der Anlauf der Ausgabe, nicht das Laden. Deshalb wieder heraus - es
   haette den einen spieler mit Geschichten, Pause und Weiterlesen teilen
   muessen. 22.10.2026 */
/* ---- Vorwaermen (22.10.2026) ----
   Zwei Verzoegerungen gab es nur einmal je Sitzung, dafuer grosse. Das
   erste Wort nach dem Start war am PC erst rund 1,1 s nach dem Erscheinen
   der Aufgabe zu hoeren, jedes weitere nach 0,5 s: beim ersten play()
   lief die ganze Tonausgabe kalt an. Und den AudioContext fuer die
   Rueckmeldetoene legte erst die erste Antwort an - lief vorher noch kein
   Wort, hielt das die Seite bis zu 0,6 s fest, und das Wort danach kam um
   so viel spaeter. Beides passiert jetzt einmal beim Start: den AudioContext
   anlegen (bis 26.10.2026 nur mit Toenen an, seitdem immer) und eine Zehntelsekunde Stille STUMM
   abspielen. Stumm, weil ein lautes Abspielen auf dem Handy die Musik
   anderer Apps anhalten kann. Die Stille entsteht als WAV im Speicher
   (stilleWav): eine echte Aufnahme dafuer abzurufen brachte das erste Wort
   nur 0,02 s frueher, kostete aber beim Start eine Anfrage mehr, genau
   wenn der Drache seine Bilder laedt. Im Paket geht das ohne Antippen (Capacitor
   laesst Abspielen ohne Geste zu), stummes Abspielen erlaubt auch jeder
   Browser; der AudioContext wartet dort bis zur ersten Antwort (resume()
   in sound()). Laeuft schon etwas, ist etwas angehalten oder lag schon
   eine Aufnahme im spieler, bleibt es aus. spieleDatei() bricht den Anlauf
   ab und stellt den Ton wieder an - ein echtes Wort bleibt nie stumm. */
function stilleWav(){
  const n = 4800, puffer = new ArrayBuffer(44 + n * 2), d = new DataView(puffer);   // 0,1 s, 48 kHz, 16 Bit, mono
  const text = (o, s) => { for(let i = 0; i < s.length; i++) d.setUint8(o + i, s.charCodeAt(i)); };
  text(0, 'RIFF'); d.setUint32(4, 36 + n * 2, true); text(8, 'WAVEfmt ');
  d.setUint32(16, 16, true); d.setUint16(20, 1, true); d.setUint16(22, 1, true);
  d.setUint32(24, 48000, true); d.setUint32(28, 96000, true); d.setUint16(32, 2, true); d.setUint16(34, 16, true);
  text(36, 'data'); d.setUint32(40, n * 2, true);
  return URL.createObjectURL(new Blob([puffer], {type: 'audio/wav'}));
}
function tonVorwaermen(){
  if(!AUDIO.size) return;              // keine Aufnahmen, also auch keine Lektion
  /* iPhone und iPad: weder Kontext noch Anspielen ohne Fingertipp - beides
     macht dort tonEntsperren() im ersten Tipp (15.11.2026). */
  if(IST_IOS) return;
  tonKontext();                        // seit dem 26.10.2026 auch bei Toenen aus: die Woerter laufen ueber ihn
  if(!spieler.paused || pausiert || laeuftVor || spieler.getAttribute('src')) return;
  stummAnspielen();
}
/* Die Zehntelsekunde Stille stumm im spieler. dann(fehler) erfaehrt, ob
   play() angenommen (null) oder abgelehnt wurde - gebraucht von
   spielerEntsperren() auf iOS (15.11.2026). */
function stummAnspielen(dann){
  let adresse = null;
  try{ adresse = stilleWav(); }catch(e){ if(dann) dann(e); return; }
  const lauf = vorwaermen = {};
  const ende = ()=>{
    if(vorwaermen === lauf){           // sonst spielt inzwischen ein echtes Wort
      vorwaermen = null;
      try{ spieler.pause(); spieler.removeAttribute('src'); spieler.load(); }catch(e){}
      spieler.muted = false;           // erst nach pause(): laut ohne Geste haelt Chrome sonst an
    }
    try{ URL.revokeObjectURL(adresse); }catch(e){}
  };
  spieler.muted = true;
  spieler.src = adresse;
  let p = null, fehler = null;
  try{ p = spieler.play(); }catch(e){ fehler = e; }
  if(p && p.then) p.then(()=>{ if(dann) dann(null); setTimeout(ende, 120); },
                         e=>{ if(dann) dann(e || new Error('play')); ende(); });
  else { if(dann) dann(fehler); setTimeout(ende, 120); }
}
/* Der ruhige Moment: die App steht, und der Vorspann bewegt sich nicht mehr
   (beim ersten Start des Tages steht er danach noch VORSPANN_HALT still da,
   sonst blendet er aus; das laeuft auch bei belegter Seite). Das Anlegen des
   AudioContext haelt die Seite kurz fest - mitten in der Bewegung saehe
   man das als Ruckeln. Ohne Bewegung (Schalter, Geraeteeinstellung) gleich. */
function tonVorwaermenPlanen(){
  const warten = vorspannOhneBewegung() ? 0
               : Math.max(0, VORSPANN_ABLAUF - (performance.now() - vorspannAb));
  setTimeout(tonVorwaermen, warten);
}
/* Erst den vollen Text suchen, dann den gekuerzten Schluessel. Dadurch koennen
   "Molim" und "Molim?" eigene Aufnahmen haben, muessen aber nicht. */
function audioDatei(text){
  /* Mehrere Formen ("moj / moja / moje") haben seit dem 01.10.2026 eine
     eigene Aufnahme mit allen Formen - Ajdin: "alle Formen sprechen". Ihr
     Schluessel ist der ganze Text, siehe schluessel_alle() in ton_bauen.py.
     Fehlt sie, gilt wie bisher die erste Form. */
  const klein = text.trim().toLowerCase();
  if(klein.includes(' / ')){ const alle = AUDIO.get(klein); if(alle) return alle; }
  const voll = text.split(' / ')[0].trim().toLowerCase();
  return AUDIO.get(voll) || AUDIO.get(audioKey(text)) || null;
}
/* ---- Eigener Ton je Bedeutung (21.11.2026) ----
   Gleich geschrieben, anders gesprochen: "sam" heisst "bin" (kurz und
   unbetont) und "allein" (langes a). audioDatei() kennt nur den Text, also
   hatte jede Schreibweise genau eine Aufnahme. Ajdin beim Test der 1.5:
   in einer Geschichte "sam" (bin) angetippt, und es kam das lange a von
   "allein".
   Seitdem traegt der Inhalt an solchen Stellen ein Feld "ton" mit einem
   eigenen Schluessel wie "sam (bin)" (ton_bedeutung.py, ton_bedeutung.json):
   Vokabeln w.ton, Grammatik g.ton, Geschichten s.ton je Vorkommen, die
   Satzwoerter der Wortliste DICT_TON. Die Aufnahme dazu spricht Emir.
   Solange es sie nicht gibt - und immer in der Web-Demo, die Emir nicht
   hat - spielt der Text wie bisher: nie Stille statt des alten Tons. */
function eigenerTon(text, ton){ return ton && audioDatei(ton) ? ton : text; }
/* Was eine Vokabel spricht: ihr eigener Ton, sonst w.bs wie bisher. */
function wortTon(w){ return eigenerTon(w.bs, w.ton); }
function sprichMitStimme(text, fertig, rate){
  if(!hasTTS){ if(fertig) fertig(); return; }
  pausiert = false;
  // Sonst laegen am PC eine noch laufende Aufnahme und die Stimme uebereinander
  try{ spieler.pause(); spieler.currentTime = 0; }catch(e){}
  waStopp();                 // ebenso ein Wort ueber WebAudio (26.10.2026)
  const u = new SpeechSynthesisUtterance(fuerStimme(text));
  const v = pickVoice();
  if(v){ u.lang=v.lang; u.voice=v; } else { u.lang='hr-HR'; }
  // 0,85 ist die Grundgeschwindigkeit der Computerstimme, das Tempo der
  // Geschichte verrechnet sich damit. Unter 0,1 nimmt kein Browser den Wert an.
  u.rate = Math.max(0.1, Math.min(10, 0.85 * (rate || 1)));
  if(fertig){ u.onend = fertig; u.onerror = fertig; }
  speechSynthesis.cancel(); speechSynthesis.speak(u);
}
/* `fertig` wird gerufen, wenn der Ton von selbst zu Ende ist - daran haengt
   der Knopf, der dann von "Stopp" wieder auf "Vorlesen" springt. */
function speak(text, fertig){
  /* Liegt die Aufnahme dekodiert bereit, sofort ueber WebAudio (26.10.2026)
     - auch fuer den Hoeren-Knopf und die Lautsprecher. Sonst wie bisher. */
  /* Ein noch wartendes spaeterSprechen() kommt nicht hinterher: wer in den
     100 ms nach dem Erscheinen auf Hoeren tippt, hoerte das Wort sonst ein
     zweites Mal von vorn (26.10.2026). */
  tonMarke++;
  if(pufferSpielen(text, fertig, 0)) return;
  sprichMitSpieler(text, fertig);
}
/* Der Weg ueber den spieler - bis zum 26.10.2026 war das speak() selbst.
   Die Geschichten nehmen immer ihn: Mitlesen, Pause, Weiterlesen und der
   Sprung zur gemerkten Stelle lesen spieler.currentTime. rate gibt nur das
   Vorlesen einer Geschichte mit, ohne sie laeuft der Ton mit 1 (05.11.2026). */
function sprichMitSpieler(text, fertig, rate){
  const datei = audioDatei(text);
  if(!datei){ sprichMitStimme(text, fertig, rate); return; }
  /* Faellt die Datei aus (fehlt, Autoplay gesperrt), springt die Stimme ein.
     Aber NICHT, wenn der Start absichtlich abgebrochen wurde: stilleBitte()
     ruft pause(), und ein pause() vor dem Anlaufen laesst play() mit
     AbortError ablehnen. Ohne diese Pruefung laese am PC die Computerstimme
     genau das weiter, was man gerade abgestellt hat - in der naechsten
     Ansicht, ohne Stopp-Knopf. */
  const marke = tonMarke;
  spieleDatei(datei, fertig, rate).catch(e=>{
    /* iPhone (15.11.2026): dort gibt es keine Computerstimme, eine
       verschluckte Ablehnung hiesse Stille ohne Spur. Also ins Protokoll,
       und der naechste Tipp spielt den spieler neu an (tonEntsperren).
       sprichMitStimme() ruft danach fertig, der Knopf springt zurueck. */
    if(IST_IOS && !(e && e.name === 'AbortError')) spielerAbgelehnt(e, datei);
    if(marke !== tonMarke || (e && e.name === 'AbortError')) return;
    sprichMitStimme(text, fertig, rate);
  });
}
/* Gibt es fuer dieses Wort ueberhaupt etwas zu hoeren? Auf dem Handy kennt
   die WebView keine Computerstimme - dort gibt es nur die Aufnahmen. */
const hoerbar = text => !!audioDatei(text) || hasTTS;
/* hoerbar() entscheidet, OB ein Lautsprecher angeboten wird, und darf grosszuegig
   sein: ist die Stimmenliste beim ersten Aufruf noch leer, soll der Knopf
   trotzdem dastehen. Beim Vorlesen einer Loesung ist das anders - dort wird
   sofort gesprochen. Ohne bosnische, kroatische oder serbische Stimme liest
   die Standardstimme des Geraets die bosnische Form mit deutscher Aussprache
   vor, direkt nachdem der Nutzer sie gelernt hat. Gefunden am 26.09.2026. */
const vorlesbar = text => !!audioDatei(text) || (hasTTS && !!pickVoice());
/* Die Stimmenauswahl steht seit dem 18.09.2026 nicht mehr in den
   Einstellungen. Die Funktion bleibt samt Aufruf beim Stimmenwechsel
   stehen, falls die Zeile je zurueckkommt - sie muss das Fehlen des
   Kastens nur vertragen. */

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
