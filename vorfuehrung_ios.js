/* Vorfuehrung fuer den iOS-Pruefbau in der Cloud (30.10.2026, Stufe A8).

   NUR IM CLOUD-BAU. app_bauen.py --ios --ci --vorfuehrung legt diese Datei
   als www/vorfuehrung.js neben die Seite und haengt sie als ERSTES Skript in
   den Kopf der KOPIE www/index.html. web/ kennt sie nicht, der Store-Bau
   (app_bauen.py --ios ohne --ci) nimmt sie nie mit und bricht ab, wenn sie
   doch in der Kopie steht. Der Schalter geht nur zusammen mit --ci.

   WARUM: In der Cloud gibt es keinen Finger. xcrun simctl kann eine App
   starten und ein Bildschirmfoto machen, aber nicht tippen. Damit Ajdin vor
   dem Apple-Konto (99 USD) sieht, wie Startseite, Lektion, Einstellungen,
   Kaufkasten und Anmeldung auf iPhone und iPad aussehen, oeffnet die Seite
   diese Schirme hier selbst nacheinander und sagt auf der Konsole, wann
   einer steht. Der Ablauf (ios-pruefung.yml) liest das aus dem Protokoll
   (Capacitor reicht console.log als "[log] - ..." an stdout weiter) und
   macht dann das Foto. Zeitgesteuert, weil nichts zurueckmelden kann.

   ZWEI RUNDEN, damit auch der echte erste Start zu sehen ist:
     Runde 1 (erster Start nach der Installation): nichts anfassen. Googles
       Einwilligungsfenster kommt wie im Store - das erste Foto.
     Runde 2 (der Ablauf startet die App neu): Stand vorgeben, Werbung aus,
       dann die Schirme der Reihe nach.
   Die Runde zaehlt localStorage. Gelesen wird synchron hier oben, BEVOR
   das grosse Skript seinen Stand laedt - wie in den Browsertests, die den
   Stand auch vor dem Laden setzen (tests_e2e/conftest.py, starten).

   WAS IN RUNDE 2 NICHT ECHT IST, und warum:
   - Googles Einwilligungsfenster bleibt weg (Capacitor.Plugins.AdMob wird
     der Seite entzogen). Es laege als eigenes Fenster ueber jedem Schirm,
     und ohne Finger geht es nicht zu. Runde 1 zeigt es.
   - ZmajAbo.preise: StoreKit antwortet im Simulator ohne Xcode mit einer
     leeren Liste (die Datei Zmaj.storekit gilt nur beim Start aus Xcode),
     und dann blendet die Seite den Kaufkasten aus. Nur DANN setzt diese
     Datei die Preise aus Zmaj.storekit ein. Kaufen geht weiter an StoreKit.
   - Die Firebase-Werte (Projekt, Schluessel, Client-ID) sind Platzhalter
     aus app_bauen.py, damit die Anmeldeseite wie im Store-Bau aussieht.
     Angetippt wird dort nichts; beim Start spricht die Seite ohne
     Anmeldung nicht mit Firebase.
   Nichts hier spricht mit dem Netz (AGENTS.md, Regel 6). */
(function(){
  'use strict';
  var MARKE = 'ZMAJ-VORFUEHRUNG';
  var RUNDE = 'zmaj_vorfuehrung_runde';
  var w = window;
  var C = w.Capacitor;
  function sag(text){ try{ console.log(MARKE + ' ' + text); }catch(e){} }
  var fehler = 0;
  /* Jeder Skriptfehler steht mit Marke im Protokoll und zaehlt am Ende mit -
     "Protokoll ohne JS-Fehler" ist damit eine Zahl, kein Suchen. */
  w.addEventListener('error', function(e){
    fehler++;
    sag('js-fehler ' + (e && e.message) + ' @' + (e && e.filename ? String(e.filename).split('/').pop() : '?')
        + ':' + (e && e.lineno));
  });
  w.addEventListener('unhandledrejection', function(e){
    var r = e && e.reason;
    fehler++;
    sag('js-fehler (Promise) ' + (r && (r.message || r.code) || String(r)));
  });

  if(!C || typeof C.getPlatform !== 'function' || C.getPlatform() !== 'ios'){
    sag('aus (keine iOS-Huelle)');
    return;
  }
  var runde = 0;
  try{ runde = parseInt(localStorage.getItem(RUNDE) || '0', 10) || 0; }catch(e){}
  runde += 1;
  try{ localStorage.setItem(RUNDE, String(runde)); }catch(e){}
  sag('runde=' + runde);
  if(runde < 2) return;   // Runde 1: der erste Start, wie ihn jeder sieht

  // ------------------------------------------------- Stand vor dem Laden ---
  function tag(d){
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-'
         + String(d.getDate()).padStart(2, '0');
  }
  var heute = new Date(), tage = [];
  for(var i = 3; i >= 0; i--){ var d = new Date(heute); d.setDate(d.getDate() - i); tage.push(tag(d)); }
  try{
    // Alles von Runde 1 weg, die Runde selbst bleibt.
    localStorage.clear();
    localStorage.setItem(RUNDE, String(runde));
    localStorage.setItem('zmaj_sprache', 'de');
    // Vier Lerntage bis heute und die Einstufung beantwortet: sonst kaeme
    // nach acht Sekunden die Frage "Kannst du schon etwas Bosnisch?".
    localStorage.setItem('zmaj_stand', JSON.stringify({tage: tage, muenzen_ges: 60,
      einstufung: {tag: tag(heute), wahl: 'neu', bis: ''}}));
    // Die eigene Einwilligung der Browser-Fassung gilt als beantwortet - ohne
    // AdMob zeigte die Seite sonst ihr eigenes Fenster.
    localStorage.setItem('zmaj_einwilligung', JSON.stringify({wahl: 'nein', stand: 1, zeit: heute.toISOString()}));
    // Heute "Spaeter" gesagt: die Anmeldung kommt erst, wenn sie dran ist.
    localStorage.setItem('zmaj_anm_spaeter', tag(heute));
    // Kein Sprechen in der Lektion: sonst fragte iOS mitten in der Lektion
    // nach Mikrofon und Spracherkennung, und das Fenster bliebe offen. Die
    // Frage kommt als letztes Bild (berechtigung).
    localStorage.setItem('zmaj_mikro_nein', '1');
  }catch(e){ sag('stand nicht gesetzt: ' + e.message); }

  // ------------------------------------------- Werbung aus, Preise da ---
  var admob = null, preiseGeflickt = false;
  function pluginsRichten(){
    var P = C.Plugins || {};
    if(P.AdMob){ admob = P.AdMob; try{ delete P.AdMob; }catch(e){ P.AdMob = undefined; } sag('werbung aus (AdMob der Seite entzogen)'); }
    var abo = P.ZmajAbo;
    if(abo && !preiseGeflickt && typeof abo.preise === 'function'){
      preiseGeflickt = true;
      var echt = abo.preise;
      abo.preise = function(o){
        return Promise.resolve(echt.call(abo, o)).then(function(r){
          if(r && r.ok && (!r.plaene || !r.plaene.length)){
            sag('preise aus Zmaj.storekit (StoreKit im Simulator leer)');
            // Wie in ios/App/App/Zmaj.storekit: beide mit einer Woche gratis.
            return {ok: true, plaene: [
              {plan: 'monat', preis: '2,99 €', micros: 2990000, waehrung: 'EUR', zeitraum: 'P1M', gratis: 'P1W'},
              {plan: 'jahr', preis: '19,99 €', micros: 19990000, waehrung: 'EUR', zeitraum: 'P1Y', gratis: 'P1W'}]};
          }
          return r;
        });
      };
    }
    return !!admob || preiseGeflickt;
  }
  pluginsRichten();
  var versuche = 0;
  var uhr = setInterval(function(){
    pluginsRichten();
    if((admob && preiseGeflickt) || ++versuche > 300) clearInterval(uhr);
  }, 10);

  // -------------------------------------------------- Die Schirme ---------
  var TAKT = w.ZMAJ_VORFUEHRUNG_TAKT || 4000;   // so lange steht jeder Schirm
  function warte(ms){ return new Promise(function(f){ setTimeout(f, ms); }); }
  function bis(pruefung, ms){
    var ende = Date.now() + (ms || 10000);
    return new Promise(function(fertig){
      (function nochmal(){
        var ok = false;
        try{ ok = !!pruefung(); }catch(e){}
        if(ok || Date.now() > ende) return fertig(ok);
        setTimeout(nochmal, 100);
      })();
    });
  }
  function nachOben(){ try{ w.scrollTo(0, 0); }catch(e){} }
  function karteZu(){
    try{ if(typeof frageSchliessen === 'function' && frageSchliessen) frageSchliessen(); }catch(e){}
    document.querySelectorAll('.nachfrage').forEach(function(k){ k.remove(); });
  }
  var nr = 0;
  async function bild(name, vorher){
    try{ if(vorher) await vorher(); }catch(e){ sag('schritt ' + name + ' gescheitert: ' + e.message); }
    await warte(700);
    nr++;
    sag('bild=' + name + ' nr=' + nr);
    await warte(TAKT);
  }
  /* Ein Ton, wie die App ihn spielt: aus der Datei holen und mit WebAudio
     dekodieren (die meisten Woerter laufen so). Dazu, wenn der Ablauf eine
     gelegt hat, eine AAC-Probe (.m4a) - das Format des Store-Baus
     (Entscheidung 5). Ohne Ton-Ausgabe, nur Dekodieren. */
  async function tonProbe(){
    var Ctx = w.AudioContext || w.webkitAudioContext;
    if(!Ctx){ sag('ton: kein AudioContext'); return; }
    var ctx = new Ctx();
    var dateien = [];
    try{
      // Ein Wort (w....), keine Geschichte - so wie pufferLaden() sie holt.
      var wort = [].concat(Array.from(AUDIO.values())).filter(function(d){ return /^w\d/.test(d); })[0];
      if(wort) dateien.push('audio/' + wort);
    }catch(e){}
    dateien.push('vorfuehrung_probe.m4a');
    for(var j = 0; j < dateien.length; j++){
      var pfad = dateien[j];
      try{
        var r = await fetch(pfad);
        // Status 0 ist auf iOS bei Tondateien normal (siehe pufferLaden()).
        sag('ton ' + pfad + ': status ' + r.status);
        if(!r.ok && r.status !== 0){ sag('ton ' + pfad + ': fehlt'); continue; }
        var puffer = await new Promise(function(ja, nein){
          r.arrayBuffer().then(function(b){ ctx.decodeAudioData(b, ja, nein); }, nein);
        });
        sag('ton ' + pfad + ': ok ' + puffer.duration.toFixed(2) + ' s');
      }catch(e){ sag('ton ' + pfad + ': NICHT dekodiert (' + (e && (e.message || e.name)) + ')'); }
    }
    try{ ctx.close(); }catch(e){}
  }

  async function ablauf(){
    // Bereit heisst auch: der Vorspann (Logo) ist weg - er bleibt nach dem
    // Laden noch gut fuenf Sekunden stehen (VORSPANN_ABLAUF + _HALT).
    var bereit = await bis(function(){
      return typeof appBereit !== 'undefined' && appBereit && standGeladen && sichtbar('pfad')
        && !document.getElementById('vorspann');
    }, 30000);
    if(!bereit){ sag('app nicht bereit nach 30 s'); }
    await warte(1500);   // Flamme und Drache einmal ankommen lassen
    karteZu();
    sag('geraet ' + w.innerWidth + 'x' + w.innerHeight + ' plattform=' + (typeof PLATTFORM !== 'undefined' ? PLATTFORM : '?')
        + ' cloud=' + (typeof cloudModus === 'function' && cloudModus()));
    await tonProbe();

    await bild('startseite', function(){ homeMode = 'words'; showHome(); nachOben(); });
    await bild('lektion', async function(){
      openLevel(0); startLesson(); await warte(1500);
      // Hat die Lektion ihr Wort schon fuer WebAudio dekodiert (pufferLaden)?
      try{
        var fertigDekodiert = Array.from(puffer.values()).filter(function(p){ return p && p.buf; }).length;
        sag('lektion: webaudio-puffer ' + fertigDekodiert + ' von ' + puffer.size + ' dekodiert');
      }catch(e){ sag('lektion: puffer nicht lesbar'); }
    });
    try{ lektionVerlassen(); }catch(e){}
    await bild('einstellungen', async function(){
      homeMode = 'words'; showHome(); showSettings();
      await bis(function(){ return document.getElementById('setVollBox').style.display === ''; }, 8000);
      nachOben();
    });
    await bild('einstellungen_unten', function(){
      w.scrollTo(0, document.documentElement.scrollHeight);
    });
    await bild('kaufkasten', async function(){
      nachOben(); vollWahlZeigen();
      var da = await bis(function(){ return document.querySelector('.nachfrage #aboKauf'); }, 8000);
      if(!da) sag('kaufkasten kam nicht (Vollversion ' + document.getElementById('setVollBox').style.display + ')');
    });
    karteZu();
    await bild('anmeldung', async function(){
      try{ localStorage.removeItem('zmaj_anm_spaeter'); }catch(e){}
      if(anmAnbieter === null && typeof anbieterFragen === 'function') await anbieterFragen();
      homeMode = 'words'; showHome();
      anmeldungZeigen('sichern');
      await bis(function(){ return anmAnbieter !== null; }, 5000);
      anmKnoepfeStellen();
      nachOben();
      sag('anmeldung: apple=' + !document.getElementById('anmApple').hidden
          + ' google=' + !document.getElementById('anmGoogle').hidden
          + ' spaeter=' + !document.getElementById('anmSpaeter').hidden
          + ' anbieter=' + JSON.stringify(anmAnbieter));
    });
    /* Zuletzt eine Frage von Apple, denn sie bleibt offen: auf dem iPhone
       die Tracking-Frage (ATT, NSUserTrackingUsageDescription), auf dem
       iPad die Spracherkennung (NSSpeechRecognitionUsageDescription). */
    var ipad = Math.min(w.innerWidth, w.innerHeight) >= 700;
    await bild(ipad ? 'frage_sprache' : 'frage_tracking', async function(){
      var P = C.Plugins || {};
      if(ipad){
        if(P.SpeechRecognition) P.SpeechRecognition.requestPermissions().then(
          function(r){ sag('spracherkennung: ' + JSON.stringify(r)); },
          function(e){ sag('spracherkennung: fehler ' + (e && e.message)); });
      }else if(admob && typeof admob.requestTrackingAuthorization === 'function'){
        admob.requestTrackingAuthorization().then(
          function(){ sag('tracking: beantwortet'); },
          function(e){ sag('tracking: fehler ' + (e && e.message)); });
      }
      await warte(2000);
    });
    sag('fertig bilder=' + nr + ' fehler=' + fehler);
  }
  w.addEventListener('load', function(){ ablauf().catch(function(e){ sag('abbruch ' + e.message + ' fehler=' + fehler); }); });
})();
