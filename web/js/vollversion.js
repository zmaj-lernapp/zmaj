/* ---- Die Vollversion ----
   Sie gehoert nicht in den Lernstand. Vorher stand sie dort, und damit
   wanderte sie durch die Sicherungsdatei: wer eine fremde Sicherung einlas,
   hatte sie geschenkt. Sie liegt jetzt getrennt im Geraetespeicher.

   Spaeter, wenn es das Abo wirklich gibt, ist ohnehin Google die einzige
   Wahrheit und diese Zeile nur noch der gemerkte letzte Stand fuer die
   Zeit ohne Netz. */
const VOLL_SCHLUESSEL = 'zmaj_voll';
function vollversionMerken(an){
  /* zmaj_voll bleibt der zuletzt bekannte Stand von Google - unveraendert.
     Der Dauerschalter sticht ihn nur in premium. Wuerde er auch nach
     zmaj_voll durchschlagen, waere beim Ausschalten nicht mehr bekannt,
     was Google eigentlich gesagt hat. */
  try{ localStorage.setItem(VOLL_SCHLUESSEL, an ? '1' : '0'); }catch(e){}
  premium = !!an || dauerVoll;
}
/* Einmalige Uebernahme aus dem alten Lernstand, damit niemand verliert, was
   er schon hatte. Das laeuft NUR beim normalen Laden - sicherungEinlesen()
   ruft standUebernehmen() direkt auf und kommt hier nie vorbei. Genau darin
   liegt der Unterschied zwischen "meins" und "aus einer fremden Datei". */
function vollversionLaden(alterStand){
  dauerVollLaden();          // muss vor jeder Rechnung mit premium stehen
  let v = null;
  try{ v = localStorage.getItem(VOLL_SCHLUESSEL); }catch(e){}
  if(v === null){ vollversionMerken(!!(alterStand && alterStand.premium)); return; }
  premium = (v === '1') || dauerVoll;
}

/* ---- Die dauerhafte Vollversion ----

   Das Team soll sie haben, ohne zu kaufen. Ueber Play geht das
   nicht: Gutscheincodes schenken nur einen Zeitraum, und ein
   Dauer-Lizenztester ist das falsche Werkzeug. Also ein eigener Schalter,
   getrennt von zmaj_voll, der diesen nur in premium sticht.

   Erreichbar mit siebenmal Tippen auf die Versionszeile in den
   Einstellungen, danach das Wort. Zwischen zwei Tipps hoechstens zwei
   Sekunden, sonst faengt die Zaehlung von vorn an - damit niemand durch
   verstreutes Antippen zufaellig hineinstolpert.

   Das ist Verstecken, kein Schutz. Wer die App auseinandernimmt, findet
   das Wort hier im Klartext; bei einer Anwendung, die ohne Server
   auskommt, geht es nicht anders. Fuer den Zweck reicht es. */
/* ---- Fuenf Tage Vollversion zum Jahrestag ----

   Wer ein Jahr dabei ist, bekommt fuenf Tage ohne Werbung und mit
   unbegrenzten Leben - und danach laeuft alles weiter wie vorher. Das
   ist ein Geschenk, kein Kauf: Google weiss nichts davon, deshalb steht
   es in einem eigenen Eintrag und laesst zmaj_voll in Ruhe. Sonst
   ueberschriebe der naechste Abgleich mit Google das Geschenk, oder
   schlimmer: die App hielte einen zahlenden Nutzer fuer einen
   beschenkten.

   Der Anfang steht in zmaj_seit. Wer die App schon laenger hat, bekommt
   seinen fruehesten Lerntag als Anfang - er soll nicht von vorn
   anfangen muessen, nur weil dieser Eintrag neu ist.

   Gerechnet wird in ganzen Jahren seit diesem Tag. Wer ein halbes Jahr
   nicht hereinschaut, verliert nichts: beim naechsten Start steht das
   Geschenk bereit. Ajdin am 29.09.2026. */
const SEIT_SCHLUESSEL = 'zmaj_seit';
const GESCHENK_SCHLUESSEL = 'zmaj_geschenk';
const GESCHENK_TAGE = 5;
let geschenk = {jahr: 0, bis: 0};
/* Faellig, aber noch nicht gezeigt. Frueher stand die Sichtbarkeitspruefung
   hinter geschenkPruefen() im selben && - das Jahr war dann abgebucht und
   die Karte fuer immer weg, wenn der Tag mitten in einer Lektion wechselte.
   Jetzt bleibt das Geschenk offen, bis die Startseite wirklich zu sehen
   ist. Gefunden in der Gegenpruefung am 29.09.2026. */
let geschenkOffen = false;
try{ geschenk = JSON.parse(localStorage.getItem(GESCHENK_SCHLUESSEL) || 'null') || geschenk; }catch(e){}
/* ---- Am Handy-Datum festgemacht (17.10.2026) ----
   Ganze Jahre zu 365 Tagen, wie bisher in geschenkPruefen(). Mehr als die
   Jahre seit APP_START kann niemand dabei sein - also kann es auch nie ein
   hoeheres Geschenkjahr geben. */
const JAHR_MS = 365 * 86400000;
const jahreSeit = tag => Math.floor((Date.now() - new Date(tag + 'T00:00:00').getTime()) / JAHR_MS);
function geschenkJahreMax(){ return Math.max(0, jahreSeit(APP_START)); }
/* Ob das gespeicherte Geschenk gerade laeuft - nach dem Handy-Datum
   gerechnet, aber nie zurueckgeschrieben. Es laeuft nur in seinen fuenf
   Tagen, also von bis - GESCHENK_TAGE bis bis, und nur, wenn sein Jahr
   nach dem Handy-Datum schon erreicht ist:
     Jahr ueber dem Hoechstwert  stammt aus einer gefaelschten Sicherung
                                 von vor dieser Pruefung (jahr 56), oder
                                 die Uhr steht gerade vor dem Tag, an dem
                                 es gegeben wurde.
     Frist weiter weg als fuenf  die Uhr wurde nach dem Geschenk zurueck-
     Tage                        gestellt; sonst liefe es bis zu dem Tag,
                                 der vorher galt.
   Die erste Fassung (geschenkBegrenzen, auch 17.10.2026) schrieb beides
   als Korrektur in den Speicher: Jahr auf den Hoechstwert, Frist gekuerzt.
   Damit gab es das Geschenk mit der Uhr beliebig oft - zurueckstellen
   schrieb jahr 0, wieder vorstellen gab Jahr 1 neu, fuenf Tage je Runde.
   In der Gegenpruefung am selben Tag gemessen. Jetzt bleibt das Jahr
   stehen, wie es gegeben wurde, und "schon gegeben" in geschenkPruefen()
   haelt in beide Richtungen; ein echter Lernender, dessen Uhr kurz falsch
   geht, verliert auch nichts mehr. Dieselbe Regel wie bei den Lerntagen
   (standUebernehmen) und bei zmaj_seit (seitWann): eine Uhr, die gerade
   falsch gehen kann, schreibt nichts fest. Eine gefaelschte 56 sperrt
   damit nur noch die eigenen Geschenke. Der Anker bleibt die Uhr: wer sie
   vorstellt, bekommt das Jahr, das sie zeigt - das ging vorher auch. */
const geschenkLaeuft = () => {
  const jahr = Number(geschenk && geschenk.jahr) || 0, bis = Number(geschenk && geschenk.bis) || 0;
  const jetzt = Date.now();
  return jahr <= geschenkJahreMax() && bis > jetzt && bis - GESCHENK_TAGE * 86400000 <= jetzt;
};
const geschenkRest = () => geschenkLaeuft() ? Math.ceil((Number(geschenk.bis) - Date.now()) / 86400000) : 0;
/* zmaj_seit liegt nie vor APP_START und nie nach heute (17.10.2026). Ein
   Eintrag von davor wird berichtigt gespeichert - er kann nur aus einer
   gefaelschten Sicherung stammen. Einer nach heute wird nur so gelesen,
   nicht gespeichert: steht die Uhr des Handys gerade falsch, soll das den
   echten Anfang nicht ueberschreiben. Kein Datum zaehlt wie kein Eintrag. */
function seitWann(){
  let s = null;
  try{ s = localStorage.getItem(SEIT_SCHLUESSEL); }catch(e){}
  if(!istDatum(s) || s < APP_START){
    /* Noch nichts eingetragen (oder etwas von vor APP_START): der fruheste
       Lerntag, sonst heute. Die Lerntage sind schon ab APP_START gefiltert;
       liegt trotzdem heute davor, geht die Uhr falsch - dann nichts
       speichern. */
    const tage = [...days].sort();
    s = tage.length ? tage[0] : today();
    if(s >= APP_START){ try{ localStorage.setItem(SEIT_SCHLUESSEL, s); }catch(e){} }
    else s = APP_START;
  }
  return s > today() ? today() : s;
}
/* Nach dem Einlesen einer Sicherung: "seit wann dabei" auf den fruehesten
   Lerntag zurueckdatieren. Auf einem neuen Geraet steht dort sonst der Tag
   der Neuinstallation - beim allerersten Start gab es ja noch keine
   Lerntage, also nahm seitWann() heute. Wer das Handy wechselt, wartete
   damit noch einmal bis zu einem Jahr auf seine fuenf Geschenktage,
   obwohl er laengst dabei ist.
   Nur nach vorn, nie nach hinten: steht schon ein frueheres Datum da,
   bleibt es stehen. Sonst koennte eine aeltere Sicherung das Geschenk
   wieder wegschieben.
   Ajdin am 29.09.2026: "wenn man ein neues geraet hat und aber premium
   hat dann ist doch bloed fuer den nutzer". */
function seitNachEinlesen(){
  const tage = [...days].sort();
  if(!tage.length) return;
  let alt = null;
  try{ alt = localStorage.getItem(SEIT_SCHLUESSEL); }catch(e){}
  /* Als "schon frueher" zaehlt seit dem 17.10.2026 nur ein echtes Datum ab
     APP_START. Ein gefaelschtes 1970 von vor dieser Pruefung hielte sonst
     jeden echten Anfang auf. tage[0] selbst liegt schon zwischen APP_START
     und heute - die Lerntage kamen durch sicherungPlausibel(). */
  if(istDatum(alt) && alt >= APP_START && alt <= tage[0]) return;
  try{ localStorage.setItem(SEIT_SCHLUESSEL, tage[0]); }catch(e){}
}
/* Laeuft beim Start und bei jedem Tageswechsel. Gibt zurueck, ob gerade
   ein Geschenk faellig geworden ist - die Karte zeigt jemand anders. */
function geschenkPruefen(){
  if(!standGeladen) return 0;
  /* Kein neues, solange eins laeuft (17.10.2026). Faellig nur, wenn seit
     dem ersten Lerntag - ab APP_START, nach dem Handy-Datum - wirklich ein
     weiteres volles Jahr vergangen ist. Das Math.min haelt die Grenze aus
     geschenkJahreMax() auch dann, wenn zmaj_seit je anders hereinkaeme. */
  if(geschenkLaeuft()) return 0;
  const jahre = Math.min(jahreSeit(seitWann()), geschenkJahreMax());
  if(jahre < 1 || jahre <= (geschenk.jahr || 0)) return 0;
  geschenk = {jahr: jahre, bis: Date.now() + GESCHENK_TAGE * 86400000};
  try{ localStorage.setItem(GESCHENK_SCHLUESSEL, JSON.stringify(geschenk)); }catch(e){}
  geschenkOffen = true;
  renderLives();
  return jahre;
}
/* Zeigt die Karte, sobald es passt: die Startseite muss da sein und es darf
   kein anderer Kasten offen stehen. Wird von drei Stellen gerufen - nach
   dem Vorspann, beim Tageswechsel und jedes Mal, wenn der Lernpfad
   gezeichnet wird. Mehrfach rufen schadet nicht, der Merker faellt beim
   ersten Mal um. */
function geschenkNachreichen(){
  if(!geschenkOffen || frageSchliessen || !sichtbar('pfad')) return;
  geschenkOffen = false;
  zeigeGeschenk();
}
function zeigeGeschenk(){
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage';
  kasten.innerHTML =
    '<div class="nachfragebox">' +
      '<div class="celebrate"><div class="zmaj cheer">' + zmaj('cheer') + '</div></div>' +
      '<h3>' + esc(t('geschenk.titel', {n: GESCHENK_TAGE})) + '</h3>' +
      '<div class="txt">' + esc(t('geschenk.text')) + '</div>' +
      '<button class="btn know" id="geschenkOk"></button>' +
    '</div>';
  kasten.querySelector('#geschenkOk').textContent = t('task.weiter');
  document.body.appendChild(kasten);
  /* Nur die eigene Schliessfunktion zuruecknehmen. Stuende hier ein nacktes
     frageSchliessen = null, naehme diese Karte einem spaeter geoeffneten
     Kasten seinen Weg hinaus - Abo- und Widerrufkasten machen es deshalb
     genauso. */
  const zu = ()=>{ kasten.remove(); if(frageSchliessen === zu) frageSchliessen = null; };
  kasten.querySelector('#geschenkOk').addEventListener('click', zu);
  frageSchliessen = zu;
  sound('done');
}
/* Neuer Schluessel seit 11.10.2026: was unter 'zmaj_dauer' steht, wurde
   mit dem alten Wort eingeschaltet. Das stand im Klartext hier und damit
   im oeffentlichen Repository - es zaehlt nicht mehr. */
const DAUER_SCHLUESSEL = 'zmaj_dauer2';
/* Nicht das Wort, sondern sein Pruefwert (PBKDF2-SHA-256). Aus ihm laesst
   sich das Wort nicht zurueckrechnen, auch nicht aus der entpackten App.
   In der Quelle steht nur der Platzhalter; app_bauen.py setzt beim Bauen
   den Wert aus der privaten Huelle ein (dauer_pruefwert.txt, angelegt mit
   dauer_wort_setzen.py). Ohne eingesetzten Wert, etwa in der Web-Demo,
   schaltet kein Wort etwas frei. 11.10.2026 */
/* DAUER_PRUEFWERT steht im Bauwerte-Block vor diesem Skript. */
const DAUER_SALZ = 'zmaj-dauer-2026';
const DAUER_RUNDEN = 300000;
async function dauerWortStimmt(w){
  if(!/^[0-9a-f]{64}$/.test(DAUER_PRUEFWERT)) return false;
  try{
    const enc = new TextEncoder();
    const schluessel = await crypto.subtle.importKey('raw', enc.encode(w), 'PBKDF2', false, ['deriveBits']);
    const bits = await crypto.subtle.deriveBits(
      {name: 'PBKDF2', hash: 'SHA-256', salt: enc.encode(DAUER_SALZ), iterations: DAUER_RUNDEN},
      schluessel, 256);
    return [...new Uint8Array(bits)].map(b => b.toString(16).padStart(2, '0')).join('') === DAUER_PRUEFWERT;
  }catch(e){ return false; }
}
/* Dasselbe Versteck, anderes Wort: zeigt die Geraetekennung, statt
   etwas umzuschalten. Kein Geheimnis, nur nichts fuer die Oberflaeche. */
const KENNUNG_WORT = 'kennung';
/* Drittes Wort: oeffnet Googles Anzeigenpruef-Tool. Es zeigt, was bei
   Anzeigenanfragen wirklich passiert - welche Bloecke abgefragt werden, was
   zurueckkommt, wie lange es dauert. Laeuft nur auf Testgeraeten. */
const PRUEF_WORT = 'pruef';
let dauerVoll = false;

function dauerVollLaden(){
  if(IST_IOS){ dauerVoll = false; return; }   // auf iOS gibt es den Schalter nicht, 30.10.2026
  try{ dauerVoll = localStorage.getItem(DAUER_SCHLUESSEL) === '1'; }catch(e){}
}
function dauerVollSetzen(an){
  dauerVoll = !!an;
  try{ localStorage.setItem(DAUER_SCHLUESSEL, an ? '1' : '0'); }catch(e){}
  let v = null;
  try{ v = localStorage.getItem(VOLL_SCHLUESSEL); }catch(e){}
  premium = (v === '1') || dauerVoll;
}
/* Zeigt, womit sich dieses Geraet bei AdMob als Testgeraet eintragen
   laesst. Zwei Werte, zwei Zwecke: die Werbe-ID will die AdMob-Konsole,
   die Kennung gehoert in ADMOB_TESTGERAETE im Quelltext.
   Googles Doku kennt fuer die Kennung nur zwei Wege - logcat, oder "eine
   App, die sie anzeigt". Der erste braucht Kabel und USB-Debugging, und
   das laesst sich nicht auf jedem Geraet einschalten. Also der zweite.
   Ajdin am 30.09.2026, nachdem es auf einem Testhandy ausgegraut war. */
async function kennungZeigen(){
  const P = window.Capacitor && window.Capacitor.Plugins;
  if(!P || !P.ZmajEinwilligung){
    await frage('Geraetekennung', 'Gibt es nur in der Handy-Fassung.', 'Gut', 'Zu');
    return;
  }
  let d = null;
  try{ d = await P.ZmajEinwilligung.kennung(); }catch(e){}
  if(!d || !d.ok){
    await frage('Geraetekennung',
                'Ging nicht: ' + ((d && d.fehler) || 'unbekannt'), 'Gut', 'Zu');
    return;
  }
  /* Beide untereinander, damit man sie abschreiben oder abfotografieren
     kann. Kopieren geht in der WebView nicht immer - deshalb steht der
     Wert auch lesbar da und nicht nur hinter einem Knopf. */
  const text = 'Werbe-ID (AdMob-Konsole):' + String.fromCharCode(10) + d.werbe_id
             + String.fromCharCode(10) + String.fromCharCode(10)
             + 'Kennung (ADMOB_TESTGERAETE):' + String.fromCharCode(10) + d.kennung
             + (d.abgeschaltet ? String.fromCharCode(10) + String.fromCharCode(10)
                 + 'Achtung: Werbe-ID ist auf diesem Geraet abgeschaltet.' : '');
  if(await frage('Geraetekennung', text, 'Kopieren', 'Zu')){
    try{ await navigator.clipboard.writeText(d.werbe_id + ' / ' + d.kennung); }catch(e){}
  }
}
/* Googles Anzeigenpruef-Tool. Das Werbe-Plugin kennt es nicht, deshalb
   ueber das eigene. Es laeuft nur auf Testgeraeten - steht das Geraet
   weder in ADMOB_TESTGERAETE noch in der AdMob-Konsole, sagt Google das
   selbst, und die Meldung steht dann hier. */
async function pruefwerkzeugOeffnen(){
  const P = window.Capacitor && window.Capacitor.Plugins;
  if(!P || !P.ZmajEinwilligung){
    await frage('Anzeigen pruefen', 'Gibt es nur in der Handy-Fassung.', 'Gut', 'Zu');
    return;
  }
  /* Der haeufigste Grund fuer ein Nein, und er hat nichts mit dem
     Testgeraet zu tun: ohne laufendes AdMob ist die Testgeraeteliste nie
     gesetzt worden - sie geht in initialize() mit. Mit eingeschalteter
     Vollversion faehrt das SDK gar nicht erst hoch. Google meldet dann
     "device is not in test mode", was in die Irre fuehrt.
     Am 30.09.2026 genau so gemessen. */
  if(!admobDa()){
    await frage('Anzeigen pruefen',
                'AdMob laeuft gerade nicht. Mit der Vollversion faehrt es gar' +
                ' nicht erst hoch, und ohne laufendes SDK kennt Google das' +
                ' Testgeraet nicht.', 'Gut', 'Zu');
    return;
  }
  let d = null;
  try{ d = await P.ZmajEinwilligung.pruefwerkzeug(); }catch(e){ d = {ok:false, fehler:String(e)}; }
  if(d && !d.ok){
    await frage('Anzeigen pruefen',
                'Ging nicht: ' + (d.fehler || 'unbekannt') +
                String.fromCharCode(10) + String.fromCharCode(10) +
                'Das Tool laeuft nur auf Testgeraeten.', 'Gut', 'Zu');
  }
}
/* Das Wort schaltet den Teil ein, beim zweiten Mal fragt es, ob er wieder weg
   soll. Der Lernstand bleibt dabei stehen. Ohne Inhalt (etwa ein alter Stand
   von inhalt/) geschieht nichts, wie bei einem falschen Wort. */
async function zaUmschalten(){
  if(!ZA) return;
  if(zaAn()){
    if(!await frage(ZA.sektion.label, t('za.ausblenden_frage'), t('za.ausblenden'), t('btn.dialog_abbrechen'))) return;
    zaSchalter = {an: false, z: Date.now()};
    /* Auf null: showPath() klappt dann wieder die laufende Sektion auf. */
    if(offeneSektion === ZA.sektion.id) offeneSektion = null;
  } else {
    zaSchalter = {an: true, z: Date.now()};
    offeneSektion = ZA.sektion.id;      // zurueck im Lernpfad steht er offen da
    kurzMeldung('✓ ' + ZA.sektion.label);
  }
  await saveProgress();
}
function dauerVollVerdrahten(){
  const z = $('ueberZeile'); if(!z) return;
  let n = 0, uhr = 0;
  z.addEventListener('click', async ()=>{
    clearTimeout(uhr); uhr = setTimeout(()=>{ n = 0; }, 2000);
    if(++n < 7) return;
    n = 0; clearTimeout(uhr);
    /* Es entscheidet das Wort, nicht der Zustand. Vorher wurde bei
       eingeschalteter Dauer-Vollversion ohne Wort gefragt, ob sie aus
       soll - wer nur die Kennung ablesen sollte, konnte sie damit
       versehentlich ausschalten. */
    const wort = await frageWort('Wort?');
    if(wort === null) return;
    const w = wort.trim().toLowerCase();
    if(w === KENNUNG_WORT){ await kennungZeigen(); return; }
    if(w === PRUEF_WORT){ await pruefwerkzeugOeffnen(); return; }
    /* Beim Zahnarzt (06.11.2026): wie die zwei davor ein eigener Weg, der bei
       der Vollversion nicht vorbeikommt. Jedes andere Wort geht unveraendert
       durch die Pruefung darunter, und ein falsches meldet weiter nichts. */
    if(w === ZA_WORT){ await zaUmschalten(); return; }
    if(!(await dauerWortStimmt(w))) return;
    if(dauerVoll){
      if(await frage('Dauerhafte Vollversion',
                     'Sie ist eingeschaltet. Ausschalten?',
                     'Ausschalten', 'Anlassen')){
        dauerVollSetzen(false); renderLives(); vollZeileZeigen();
      }
      return;
    }
    dauerVollSetzen(true); renderLives(); vollZeileZeigen();
  });
}
/* ---- Alle Muenz-Stuecke fuer uns ----
   Ajdin am 19.10.2026: alle Farben, die es fuer Muenzen gibt, tragen, ohne
   sie zu kaufen - nur fuer sich. Am 20.10.2026 dazu auch Huete, Brillen
   und Halsstuecke ("gib alle skins"), siehe hatStueck(). Dasselbe Wort wie beim Dauerschalter
   (derselbe Pruefwert, dauerWortStimmt), aber eine andere Stelle: siebenmal
   auf die Ueberschrift "Laden", waehrend der Reiter Farben gewaehlt ist,
   hoechstens zwei Sekunden zwischen zwei Tipps. Nochmal so schaltet aus.
   Warum dort: die Ueberschrift ist kein Knopf und tut sonst nichts, der
   Zaehler stoert also keine Bedienung, und siebenmal schnell tippt dort
   niemand. Die Muenzanzeige fuehrte damals in den Laden, der Reiterkopf klappt die
   Liste auf - beide fielen deshalb weg. Und die Wirkung steht gleich
   darunter: "Tragen" statt Preis.
   Gekauft wird nichts, besitz und Muenzen bleiben, wie sie sind. Ist der
   Schalter aus, faellt ein nicht gekauftes Stueck vom Drachen wie eins
   der Vollversion nach dem Abo; gespeichert bleibt es. */
function hautAlleSetzen(an){
  hautAlle = !!an;
  try{ localStorage.setItem(HAUT_ALLE_SCHLUESSEL, an ? '1' : '0'); }catch(e){}
}
function hautAlleVerdrahten(){
  const z = $('ladenTitel'); if(!z) return;
  let n = 0, uhr = 0;
  z.addEventListener('click', async ()=>{
    if(ladenReiter !== 'farbe'){ n = 0; return; }
    clearTimeout(uhr); uhr = setTimeout(()=>{ n = 0; }, 2000);
    if(++n < 7) return;
    n = 0; clearTimeout(uhr);
    const wort = await frageWort('Wort?');
    if(wort === null) return;
    if(!(await dauerWortStimmt(wort.trim().toLowerCase()))) return;
    if(hautAlle && !(await frage(t('laden.titel'),
                                 'Sie sind eingeschaltet. Ausschalten?',
                                 'Ausschalten', 'Anlassen'))) return;
    hautAlleSetzen(!hautAlle);
    renderLaden(); drachenNeu();
  });
}
async function loadProgress(){
  if(!MIT_SERVER){ const roh = lokalLesen(); standUebernehmen(roh); vollversionLaden(roh); standGeladen = true; return; }
  try{
    const r = await fetch(apiF()); const d = await r.json();
    if(!r.ok) throw new Error(d.fehler||'Profil unbekannt');
    standUebernehmen(d);
  }catch(e){ standUebernehmen({}); known = new Set(); passed = new Set(); read = new Set(); days = new Set(); frost = new Set(); tagwerk = {}; muenzenGes = 0; muenzenAus = 0; besitz = new Set(); }
  standGeladen = true;
}
/* Gibt zurueck, ob der Stand wirklich weggeschrieben wurde. Fast alle
   Aufrufer interessiert das nicht - aber beim Einlesen einer Sicherung
   schon: sonst meldet die App Erfolg, und beim naechsten Start ist alles
   wieder weg, weil der Geraetespeicher voll oder gesperrt war. */
async function saveProgress(){
  /* Nichts wegschreiben, bevor gelesen wurde. Sonst ueberschreibt ein
     visibilitychange waehrend des Vorspanns - Home-Taste, Anruf,
     Bildschirmsperre - den ganzen Lernstand mit den leeren Startwerten.
     Gefunden am 20.09.2026. */
  if(!standGeladen) return false;
  if(!MIT_SERVER) return lokalSchreiben(standAlsObjekt());
  if(!profil) return false;
  try{
    const r = await fetch(apiF(), {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(standAlsObjekt())});
    return r.ok;
  }catch(e){ return false; }
}
var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
