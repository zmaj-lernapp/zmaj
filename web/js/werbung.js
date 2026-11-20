/* =================== WERBUNG ===================
   Hier steht nur die Logik: wann Werbung kommt und was sie bewirkt.
   Angezeigt wird bisher ein Platzhalter – sobald die App im Store ist,
   wird in zeigeWerbung() das echte SDK aufgerufen (AdMob o. ä.).

   Zwei Arten:
   1. Nach der Lektion, ganzseitig. Nicht nach jeder – das vertreibt Leute.
      Erst ab der WERBUNG_AB_LEKTION-ten Lektion, dann jede
      WERBUNG_JEDE_X-te, und höchstens WERBUNG_MAX_TAG mal am Tag.
   2. Freiwillig bei leeren Leben: Video ansehen, ein Leben zurück.
      Das mögen Leute, weil sie etwas davon haben.

   Die Vollversion schaltet beides ab und gibt unbegrenzt Leben. */
/* ACHTUNG vor dem Einbau eines echten Werbenetzwerks:
   1. Die Datenschutzerklärung (sprachen.py, set.datenschutz_text) sagt
      derzeit "keine Werbenetzwerke". Das muss dann geändert werden.
   2. In der EU verlangt Google seit Januar 2024 ein zertifiziertes
      Consent-Banner (CMP nach IAB-TCF, z. B. Googles User Messaging
      Platform). Ohne das werden keine Anzeigen ausgeliefert.
   3. Die Vollversion darf nur über die Bezahlung des jeweiligen Stores
      verkauft werden - eigene Bezahlwege sind dort nicht erlaubt. */
/* WERBUNG_AN steht im Bauwerte-Block vor diesem Skript. */
/* Ajdin am 27.09.2026: "die anzeige sollte nach jeder lektion kommen nicht
   nach 3 lektionen sonst kann ich ja garnichts verdienen". Beides auf 1.
   Die Obergrenze fuer den Tag bleibt bei WERBUNG_MAX_TAG - sie ist jetzt
   das, was den Tag begrenzt: nach sechs Lektionen kommt keine Anzeige mehr. */
const WERBUNG_AB_LEKTION  = 1;     // ab der ersten Lektion
const WERBUNG_JEDE_X      = 1;     // und dann nach jeder
/* Ajdin am 27.09.2026: "fuer herzen auffuellen wuerde ich eine taegliche
   grenze setzen aber fuer normale videos nicht also nach einer bestandenen
   oder nicht bestandenen lektion oder auch test".
   0 heisst: keine Tagesgrenze. Gezaehlt wird trotzdem weiter (werbungHeute.n),
   das ist die einzige Spur, an der man spaeter ablesen kann, wie viele
   Anzeigen ein Tag wirklich gebracht hat. Eine Zahl groesser 0 setzt die
   Grenze wieder in Kraft. */
const WERBUNG_MAX_TAG     = 0;     // 0 = keine Grenze fuer die Anzeige nach Lektion und Test
/* Eigenes Tageskontingent fuer das freiwillige Video. Ajdin am 26.09.2026:
   wer viel lernt, hatte nach sechs Pflicht-Anzeigen auf dem Schirm "Keine
   Leben mehr" keinen Knopf "Leben holen" mehr - aufgebraucht von Anzeigen,
   die er sich nicht ausgesucht hat. Der Entwurf oben deckelt ausdruecklich
   nur Art 1 (die Anzeige nach der Lektion), nicht Art 2. Sechs bleibt die
   Obergrenze, die vorher schon galt - nur eben nicht mehr geteilt. */
const WERBUNG_MAX_LOHN    = 6;     // freiwillige Videos, getrennt gezaehlt
const WERBUNG_LEBEN_LOHN  = 1;     // so viele Leben gibt ein belohntes Video

let werbungZaehler = 0;            // Lektionen seit der letzten Werbung
/* offen: eine Anzeige, die faellig war, aber nicht laufen konnte - weil
   der Nutzer weitergetippt hat oder die App in den Hintergrund ging. Sie
   steht hier und nicht nur im Arbeitsspeicher, weil sie sonst mit dem
   Schliessen der App verschwand: Lektion zu Ende, App wegwischen, neu
   oeffnen - und die Anzeige war umgangen. Ajdin am 29.09.2026. */
let werbungHeute = {tag: '', n: 0, lohn: 0, offen: false};
try{ werbungHeute = JSON.parse(localStorage.getItem('zmaj_werbung') || 'null') || werbungHeute; }catch(e){}

/* =================== EINWILLIGUNG ===================
   Werbung darf in der EU erst laufen, wenn der Nutzer gefragt wurde.
   Das Fenster kommt einmal beim ersten Start; die Antwort merkt sich
   dieses Gerät. In den Einstellungen lässt sie sich jederzeit ändern –
   das ist Pflicht, eine Einwilligung muss so leicht zurückzunehmen sein,
   wie sie gegeben wurde.

   WICHTIG beim Einbau eines echten Werbenetzwerks:
   Für AdMob in der EU reicht dieses Fenster nicht. Google verlangt ein
   zertifiziertes CMP nach IAB-TCF (z. B. Googles eigene User Messaging
   Platform). Das zeigt dann sein eigenes Fenster; hier drin wird nur noch
   dessen Ergebnis abgelegt, damit der Rest der App unverändert bleibt.
   Für die Web-Fassung ohne AdMob genügt dieses Fenster.

   WERBUNG_ECHT bleibt false, solange nur der Platzhalter läuft: Ohne
   echtes Werbenetzwerk verlässt kein einziges Datum das Gerät, und dann
   wäre die Frage schlicht gelogen. Zum Anschauen: ?einwilligung=1 an die
   Adresse hängen.

   Der Schalter selbst steht in sprachen.py unter WERBUNG_LAEUFT und kommt
   mit den Daten vom Server. So schaltet eine einzige Zeile die Werbung,
   das Einwilligungsfenster und den passenden Abschnitt in der
   Datenschutzerklärung gemeinsam um – sie können nicht widersprechen. */
let WERBUNG_ECHT = false;          // wird aus sprachen.py übernommen
const EINWILLIGUNG_STAND = 1;      // hochzählen, wenn sich die Partner ändern -> neu fragen
const EINWILLIGUNG_TEST = new URLSearchParams(location.search).get('einwilligung') === '1';

let einwilligung = null;
try{ einwilligung = JSON.parse(localStorage.getItem('zmaj_einwilligung') || 'null'); }catch(e){}

function einwilligungGueltig(){
  return !!einwilligung && einwilligung.stand === EINWILLIGUNG_STAND &&
         (einwilligung.wahl === 'ja' || einwilligung.wahl === 'nein');
}
function einwilligungFragen(){
  /* Punkt 15 aus WERBUNG_PRUEFUNG.md: wer die Vollversion hat, sieht nie
     eine Anzeige - ihn nach einer Einwilligung in eine Datenverarbeitung
     zu fragen, die bei ihm nicht stattfindet, ist falsch und unhoeflich.
     Die Pruefung gehoert hierher und nicht in admobStart(): am PC gibt es
     das Plugin gar nicht, und bei der versteckten Dauer-Vollversion steht
     zmaj_voll auf '0' - in beiden Faellen griff der dortige Ausstieg
     nicht, das Fenster kam trotzdem. */
  if(unlimited()) return false;
  if(admobDa()) return false;      // dann fragt Googles eigenes Fenster
  /* Punkt 7 aus WERBUNG_PRUEFUNG.md: kam Googles UMP nicht durch, sprang
     frueher unser eigenes Fenster ein. Das ist kein zertifiziertes CMP.
     Seine Antwort wurde trotzdem dauerhaft gespeichert, landete ueber
     werbungPersonalisiert() als npa an echten Anzeigenanfragen, und beim
     naechsten Start mit Netz fragte UMP dieselbe Sache ein zweites Mal -
     derselbe Nutzer, zweimal befragt, und die erste Antwort galt als
     Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO.
     Auf dem Geraet fragt deshalb ausschliesslich Google. Kommt UMP nicht
     durch, gibt es lieber keine Werbung; der naechste Start versucht es
     erneut, und zeigeWerbung() fasst innerhalb einer Sitzung einmal nach.
     Unser eigenes Fenster bleibt fuer die Browser-Fassung, wo es AdMob
     gar nicht gibt. */
  const P = window.Capacitor && window.Capacitor.Plugins;
  if(WERBUNG_ECHT && P && P.AdMob) return false;
  return (WERBUNG_ECHT || EINWILLIGUNG_TEST) && !einwilligungGueltig();
}
/* Diese Antwort braucht das SDK später: false heißt "nur allgemeine
   Werbung" (bei AdMob npa=1). */
/* Ein eigener Schalter, wie bei Tönen und Vibration. Ausgeschaltet
   bedeutet npa=1: Anzeigen kommen weiter, nur ohne Bezug zu dir.
   Er gilt immer - auch wenn bei Google zugestimmt wurde. Strenger als
   die Einwilligung darf man sein, lockerer nicht.
   Solange niemand geschaltet hat, zählt die Antwort aus dem
   Einwilligungsfenster; gibt es auch die nicht, bleibt es aus. */
let persWahl = null;
try{ const v = localStorage.getItem('zmaj_pers'); if(v==='an'||v==='aus') persWahl = (v==='an'); }catch(e){}
function werbungPersonalisiert(){
  if(persWahl !== null) return persWahl;
  return einwilligungGueltig() && einwilligung.wahl === 'ja';
}
function setzePersonalisiert(v){
  persWahl = !!v;
  try{ localStorage.setItem('zmaj_pers', persWahl ? 'an' : 'aus'); }catch(e){}
}
function einwilligungMerken(wahl){
  einwilligung = {wahl: wahl, stand: EINWILLIGUNG_STAND, zeit: new Date().toISOString()};
  try{ localStorage.setItem('zmaj_einwilligung', JSON.stringify(einwilligung)); }catch(e){}
}

/* Zeigt das Fenster und liefert die Wahl zurück. Es lässt sich nicht
   wegklicken - eine der beiden Antworten muss kommen. */
function zeigeEinwilligung(){
  return new Promise(fertig => {
    const kasten = document.createElement('div');
    kasten.className = 'einwilligung';
    kasten.innerHTML =
      '<div class="einwilligungbox">' +
        '<h3>' + esc(t('consent.titel')) + '</h3>' +
        '<div class="txt">' + t('consent.text') + '</div>' +
        '<details><summary>' + esc(t('set.datenschutz')) + '</summary>' +
          '<div class="inner legal">' + t('set.datenschutz_text', {anbieter: t('set.anbieter')}) + '</div>' +
        '</details>' +
        '<button class="btn know" id="einwJa"></button>' +
        '<button class="btn ghost" id="einwNein"></button>' +
        '<div class="fuss">' + esc(t('consent.fuss')) + '</div>' +
      '</div>';
    const ja = kasten.querySelector('#einwJa'), nein = kasten.querySelector('#einwNein');
    ja.textContent = t('consent.ja');
    nein.textContent = t('consent.nein');
    document.body.appendChild(kasten);
    const waehle = wahl => { einwilligungMerken(wahl); kasten.remove(); fertig(wahl); };
    ja.addEventListener('click', () => waehle('ja'));
    nein.addEventListener('click', () => waehle('nein'));
  });
}

/* `belohnt` trennt die beiden Arten. Ohne Argument ist die Pflicht-Anzeige
   gemeint, so wie vorher - der Aufruf in lessonEnd() bleibt deshalb
   unveraendert. Das `|| 0` faengt Staende ab, die noch ohne `lohn` im
   Geraetespeicher liegen; sonst waere der Vergleich NaN und der Knopf
   "Leben holen" von der ersten Sekunde an weg. */
function werbungErlaubt(belohnt){
  if(!WERBUNG_AN || unlimited()) return false;   // Vollversion: nie
  if(admobDa() && !admobDarf) return false;      // Google sagt nein
  /* Punkt 7: auf dem Geraet ohne laufendes AdMob gibt es nichts zu zeigen.
     Seit das eigene Einwilligungsfenster dort nicht mehr einspringt, waere
     der Knopf „Video ansehen“ sonst zwar da, liefe aber jedes Mal ins
     Leere. Lieber gar nicht erst anbieten. */
  const Pw = window.Capacitor && window.Capacitor.Plugins;
  /* Ausnahme seit 07.10.2026: ein offener Zweitversuch nach einem Start
     ohne Netz, siehe admobNachholbar(). Sonst kam er nie an die Reihe. */
  if(!admobDa() && Pw && Pw.AdMob && !admobNachholbar()) return false;
  if(einwilligungFragen()) return false;         // erst fragen, dann werben
  /* today() ist der oertliche Tag. Vorher stand hier toISOString(), also
     UTC - der Zaehler sprang im Sommer um 2 Uhr nachts um, nicht um
     Mitternacht. Gefunden beim Abgleich der Projektmappe, 02.10.2026. */
  const heute = today();
  if(werbungHeute.tag !== heute) werbungHeute = {tag: heute, n: 0, lohn: 0,
                                                 offen: !!werbungHeute.offen};
  /* Das freiwillige Video fuer ein Herz bleibt begrenzt - es kostet Leben,
     und wer sich zwanzig Videos ansieht, spielt den Tag durch, ohne je zu
     warten. Die Anzeige nach Lektion und Test ist nicht begrenzt. */
  return belohnt ? (werbungHeute.lohn || 0) < WERBUNG_MAX_LOHN
                 : (!WERBUNG_MAX_TAG || (werbungHeute.n || 0) < WERBUNG_MAX_TAG);
}
function werbungGezaehlt(belohnt){
  const heute = today();
  if(werbungHeute.tag !== heute) werbungHeute = {tag: heute, n: 0, lohn: 0,
                                                 offen: !!werbungHeute.offen};
  if(belohnt) werbungHeute.lohn = (werbungHeute.lohn || 0) + 1;
  else werbungHeute.n    = (werbungHeute.n    || 0) + 1;
  try{ localStorage.setItem('zmaj_werbung', JSON.stringify(werbungHeute)); }catch(e){}
}

/* =================== ADMOB ===================
   Auf dem Handy zeigt Google die Anzeigen, am PC bleibt es beim Platzhalter
   von oben. Die Weiche ist das Plugin: ist es nicht da, ändert sich nichts.

   EINWILLIGUNG: Googles User Messaging Platform (UMP) bringt ihr eigenes
   Fenster mit – genau das, was oben als „zertifiziertes CMP" verlangt ist.
   Deshalb tritt unser eigenes Fenster auf dem Handy zurück. Welche Anzeigen
   jemand bekommt, entscheidet Google anhand dieser Antwort.
   Die App gibt npa trotzdem mit - an beiden Anforderungsstellen, aus dem,
   was werbungPersonalisiert() sagt. Das ist kein zweites Regelwerk,
   sondern dieselbe Antwort noch einmal: werbungAbgleichen() holt sie beim
   Start aus Googles Speicher und schreibt sie in persWahl. Frueher stand
   hier, die App setze npa nicht mehr selbst - das war schon damals nicht
   wahr. Berichtigt am 30.09.2026, Punkt 19.

   TESTBETRIEB: Solange ADMOB_TEST true ist, laufen Googles öffentliche
   Testanzeigen. Die brauchen kein Konto, kosten nichts und bringen nichts
   ein. Vor der ersten Veröffentlichung müssen hier die echten Kennungen aus
   dem AdMob-Konto stehen und ADMOB_TEST auf false – Testanzeigen in einer
   veröffentlichten App sind ein Regelverstoß. Die App-ID selbst liegt
   daneben im Android-Projekt unter res/values/strings.xml.

   Geht irgendetwas davon schief, bleibt AdMobP null und die App läuft
   einfach ohne Werbung weiter. Eine Lernapp, die wegen einer Anzeige nicht
   startet, wäre der schlechteste aller Tauschhandel. */
/* ADMOB_TEST steht im Bauwerte-Block vor diesem Skript. */
/* Punkt 4 aus WERBUNG_PRUEFUNG.md: unsere eigenen Geraete bekommen auch
   nach dem Tausch auf die echten Kennungen weiter TESTanzeigen. Ohne das
   waere jeder eigene Klick beim Nachtesten ungueltiger Traffic auf dem
   eigenen Konto - genau die Gefahr, vor der admob_scharf.py warnt. Der
   versteckte Dauer-Schalter reicht dafuer nicht: er haengt an
   localStorage und ist nach einer Neuinstallation weg.

   Eine Kennung holt man so: in den Einstellungen siebenmal auf die
   Versionszeile tippen und das Wort 'kennung' eingeben. Die App zeigt sie
   dann selbst. Der Weg ueber das Protokoll geht auch:
     adb logcat -d | grep setTestDeviceIds

   ACHTUNG, ZWEI KENNUNGEN JE GERAET. Die Kennung ist der MD5 der
   ANDROID-ID (nicht der Werbe-ID - am 30.09.2026 am Geraet nachgemessen),
   und die Android-ID haengt seit Android 8 am Signaturschluessel der App.
   Debug- und Play-Fassung sind verschieden signiert, also liefert dasselbe
   Handy zwei verschiedene Werte. Der Wert aus einer Debug-Fassung schuetzt
   die veroeffentlichte App NICHT.
   Wer also ein Geraet fuer die echte App schuetzen will, liest die Kennung
   aus der Fassung ab, die aus dem Play Store kommt.

   Bequemer und ohne diese Falle: das Geraet in der AdMob-Konsole unter
   Einstellungen -> Testgeraete eintragen. Dort zaehlt die Werbe-ID, und
   die haengt an keinem Signaturschluessel - ein Eintrag deckt beide
   Fassungen ab. Die Werbe-ID zeigt dieselbe Stelle in der App mit an.

   WICHTIG: testingDevices wirkt NUR zusammen mit initializeForTesting.
   AdMob.java:250-253 liest die Liste sonst gar nicht erst. Deshalb steht
   unten ADMOB_TEST ODER 'Liste nicht leer' - nicht nur ADMOB_TEST. Fuer
   alle anderen Geraete aendert das nichts: setTestDeviceIds
   (AdMob.java:302) betrifft genau die hier aufgezaehlten. */
/* Die Kennungen unten sind Android-Kennungen. Auf iOS bleibt die Liste leer
   (ADMOB_TESTGERAETE_JETZT): dort gibt es noch kein eigenes Testgeraet, und
   initializeForTesting soll dort nicht nur wegen fremder Kennungen anspringen.
   Ein iPhone traegt man am einfachsten mit seiner Werbe-ID in der
   AdMob-Konsole ein. 30.10.2026 */
const ADMOB_TESTGERAETE = [
  '41C694B849758EB6384F9FED5DD5FFAC',   // Ajdin, S21 Ultra - DEBUG-Fassung
  'E305C080FC5C6BC30B53AE7A29DD4E0A',   // Galaxy S9 - DEBUG-Fassung, 30.09.2026
  /* Was hier noch fehlt, siehe oben:
       - Ajdins S21 aus der PLAY-Fassung (anderer Signaturschluessel,
         andere Kennung - der Wert oben schuetzt nur die Debug-Fassung)
       - ein weiteres Testhandy, ebenfalls aus der Play-Fassung
     Beide gehoeren hier hinein, BEVOR admob_scharf.py laeuft - oder beide
     Geraete stehen mit ihrer Werbe-ID in der AdMob-Konsole, das deckt
     jede Fassung ab. */
];
const ADMOB_TESTGERAETE_JETZT = IST_IOS ? [] : ADMOB_TESTGERAETE;
/* App-Tracking-Transparenz (30.10.2026, Entscheidung 10). Auf dem iPhone
   fragt Apple, ob die App dich ueber Apps anderer Firmen hinweg verfolgen
   darf - ohne Ja gibt es keine Werbe-ID. Gefragt wird ueber Googles
   "IDFA-Hinweis" in der AdMob-Konsole: Googles Einwilligungsfenster zeigt
   ihn nach der DSGVO-Frage und ruft dann selbst Apples Fenster
   (developers.google.com/admob/ios/privacy/idfa). Steht der Hinweis dort
   nicht (noch nicht eingeschaltet, oder ausserhalb des Gebiets, fuer das er
   gilt), ist Apples Status danach noch 'notDetermined' - dann fragt die App
   einmal selbst, sonst stuende die Werbung ohne jede Frage auf "nicht
   personalisiert". Wer schon geantwortet hat, wird nie zweimal gefragt:
   Apple zeigt das Fenster ohnehin nur einmal. */
async function attNachfragen(A){
  if(!IST_IOS || !A || typeof A.trackingAuthorizationStatus !== 'function') return;
  try{
    const s = await A.trackingAuthorizationStatus();
    if(s && s.status === 'notDetermined' && typeof A.requestTrackingAuthorization === 'function'){
      await A.requestTrackingAuthorization();
    }
  }catch(e){}
}
/* ADMOB_ID_ANDROID steht im Bauwerte-Block vor diesem Skript. */
/* iPhone und iPad (30.10.2026): eigene Anzeigenbloecke, sie gehoeren zur
   iOS-App in AdMob. Hier stehen Googles oeffentliche Test-Bloecke fuer iOS
   (developers.google.com/admob/ios/test-ads) - so zeigt auch der Bau in der
   Cloud und im Simulator Testanzeigen. Die echten setzt app_bauen.py --ios
   nur in die KOPIE www/index.html ein, aus ios_zugang.xcconfig der Huelle
   (ios_admob_einsetzen), wie die Firebase-Werte. Die Zeilen muessen genau
   so bleiben, das Bauskript sucht sie. */
/* ADMOB_ID_IOS steht im Bauwerte-Block vor diesem Skript. */
const ADMOB_ID = IST_IOS ? ADMOB_ID_IOS : ADMOB_ID_ANDROID;
let AdMobP = null;          // das Plugin, sobald es sich gemeldet hat
let admobDarf = false;      // canRequestAds – vorher darf nichts geladen werden
let admobFehler = null;     // warum der Start scheiterte, fuer den zweiten Versuch
let admobZweitversuch = false;
let admobOptionen = false;  // Google verlangt einen Knopf zum Nachträglich-Ändern
/* Punkt 6: initialize() darf nur einmal laufen. Wird die Antwort spaeter
   in Googles Fenster geaendert, holen wir den Start nach - ohne Merker
   koennte das SDK zweimal starten. */
let admobGestartet = false;

function admobDa(){ return !!AdMobP; }
/* Zweitversuch nach einem Start ohne Netz. Pruefung vom 07.10.2026: bis
   v96 sagte werbungErlaubt() nein, sobald das Plugin da und AdMobP null
   war - und weil jeder Aufrufer vorher fragt, kam der Nachfass in
   zeigeWerbung() nie dran. Wer die App im Flugmodus oder in der U-Bahn
   startete, sah die ganze Sitzung keine Anzeige und kein „Video ansehen“.
   Jetzt laesst werbungErlaubt() den naechsten Werbeanlass durch, solange
   ein Versuch offen ist, und zeigeWerbung() startet AdMob dort neu.
   Ein Versuch je Gelegenheit: zeigeWerbung() verbraucht ihn, erst das
   zurueckgekehrte Netz oder die Rueckkehr in die App oeffnet ihn wieder.
   Keine Schleife, und ohne Netz wird gar nicht erst gefragt. Gefragt wird
   dabei nur Googles Einwilligung - geladen wird weiter erst nach
   canRequestAds, wie in admobStart(). */
function admobNachholbar(){
  const P = window.Capacitor && window.Capacitor.Plugins;
  return WERBUNG_ECHT && !AdMobP && !!admobFehler && !admobZweitversuch &&
         !!(P && P.AdMob) && navigator.onLine !== false;
}
function admobWiederOeffnen(){ if(!AdMobP && admobFehler) admobZweitversuch = false; }
window.addEventListener('online', admobWiederOeffnen);
document.addEventListener('visibilitychange', ()=>{ if(!document.hidden) admobWiederOeffnen(); });

/* Reihenfolge nach Googles Vorgabe: erst fragen, dann das SDK starten. */
async function admobStart(){
  const P = window.Capacitor && window.Capacitor.Plugins;
  if(!P || !P.AdMob || !WERBUNG_ECHT) return;
  /* Bei aktiver Vollversion faehrt AdMob gar nicht erst hoch. werbungErlaubt()
     verhindert zwar jede Anzeige, aber das SDK wuerde trotzdem starten und mit
     Google sprechen - fuer jemanden, der genau dafuer bezahlt hat, waere das
     verkehrt. Gelesen wird direkt aus dem Geraetespeicher, weil an dieser
     Stelle im Start noch niemand angemeldet ist.

     Der versteckte Dauerschalter gehoert hier dazu. Er schreibt zmaj_voll
     bewusst NICHT mit (siehe vollversionMerken), deshalb las diese Stelle
     ihn gar nicht: auf beiden Testhandys fuhr AdMob trotz eingeschalteter
     Dauer-Vollversion hoch, sprach mit Google und zeigte dessen
     Einwilligungsfenster - genau das, was dieser Kommentar ausschliessen
     wollte. Gefunden am 26.09.2026. */
  dauerVollLaden();   // frisch aus dem Geraetespeicher, wie eine Zeile tiefer
  if(vollversionGemerkt() || dauerVoll || geschenkLaeuft()) return;
  try{
    const A = P.AdMob;
    let info = await A.requestConsentInfo();
    if(info.isConsentFormAvailable && info.status === 'REQUIRED'){
      info = await A.showConsentForm();
    }
    // AdMobP wird gesetzt, sobald Google gefragt HAT - auch wenn die Antwort
    // nein war. Sonst hielte sich die App danach für den Browser und würde
    // ihr eigenes Einwilligungsfenster hinterherschieben: zweimal gefragt,
    // und die Ablehnung sähe aus, als hätte sie nicht gezählt.
    // Nur das Werbe-SDK selbst starten wir dann nicht.
    AdMobP = A;
    admobDarf = !!info.canRequestAds;
    admobOptionen = info.privacyOptionsRequirementStatus === 'REQUIRED';
    // Nur iOS, und nur wenn Googles Fenster Apples Frage nicht schon gestellt hat.
    if(admobDarf) await attNachfragen(A);
    /* maxAdContentRating: ohne diese Angabe entscheidet allein die
       Voreinstellung im AdMob-Konto, welche Anzeigen kommen duerfen -
       und die steht nirgends im Projekt. Punkt 3 aus WERBUNG_PRUEFUNG.md,
       behoben am 29.09.2026.
       Bis v96 stand hier „Teen“, begruendet mit der Zielgruppe 16+. Googles
       Werberichtlinie richtet sich aber nach der Inhaltseinstufung, nicht
       nach der Zielgruppe, und die ist USK 0 / PEGI 3 (STORE_TEXTE.md).
       Dazu passt „General“. Der Wert aus dem SDK geht der Einstellung in
       der AdMob-Konsole vor, aendern laesst er sich also nur mit einem
       Neubau. Hoeher darf er erst, wenn die Einstufung in der Play Console
       dazu passt, nicht umgekehrt. Pruefung vom 07.10.2026. */
    if(admobDarf){
      await A.initialize({
        /* Siehe ADMOB_TESTGERAETE: ohne initializeForTesting bleibt die
           Liste unbeachtet. */
        initializeForTesting: ADMOB_TEST || ADMOB_TESTGERAETE_JETZT.length > 0,
        testingDevices: ADMOB_TESTGERAETE_JETZT,
        maxAdContentRating: 'General'});
      admobGestartet = true;
    }
  }catch(e){
    /* Der Fehler wurde bis zum 27.09.2026 stillschweigend verschluckt. Das
       ist teuer: AdMobP steht danach auf null, damit liefert admobDa() false,
       damit kippt einwilligungFragen() auf true - und werbungErlaubt() sagt
       fuer BEIDE Werbearten nein, den ganzen Lauf lang. Eine Stoerung beim
       Start, und der Tag bringt nichts ein. Am Geraet genau so gemessen:
       admobDa false, einwilligungFragen true, beide Erlaubnisse false,
       waehrend frueher am selben Tag noch drei belohnte Videos liefen.
       Jetzt bleibt der Grund stehen, damit man ihn nachlesen kann, und
       zeigeWerbung() fasst einmal nach. */
    AdMobP = null; admobDarf = false;
    admobFehler = (e && (e.message || e.code)) ? String(e.message || e.code) : 'unbekannt';
  }
}

/* Punkt 6 aus WERBUNG_PRUEFUNG.md: nach Googles Datenschutzfenster stand
   nur persWahl neu - admobDarf und admobOptionen blieben auf dem Wert vom
   Start. Zwei Wege liefen schief:
     Widerruf -> canRequestAds wird false, die App fragte aber bis zum
       Neustart weiter Anzeigen an. Kein Datenschutzverstoss, denn npa
       wird bei jeder Anfrage frisch gerechnet, aber ein Verstoss gegen
       Googles eigene Bedingung.
     Zustimmung nach anfaenglicher Ablehnung -> admobDarf blieb false und
       initialize() war nie gelaufen; die Zustimmung blieb bis zum
       Neustart folgenlos.
   Deshalb die Auskunft frisch holen und das SDK nachstarten, falls es
   noch nicht lief. */
/* ohneStart (01.11.2026, Pruefbericht): nur die Auskunft nachziehen, das
   SDK aber NICHT starten. Fuer Abonnenten, die erst in dieser Sitzung
   gekauft haben, als AdMob schon gefragt hatte (AdMobP gesetzt, aber nach
   einem Nein nie initialize()). Seit sie den Werbeschalter haben, liefe ihr
   Tipp sonst hierher, und ein Ja in Googles Fenster haette das Werbe-SDK
   fuer jemanden gestartet, der genau dafuer bezahlt - siehe admobStart(). */
async function einwilligungNachziehen(ohneStart){
  if(!AdMobP) return;
  try{
    const info = await AdMobP.requestConsentInfo();
    admobDarf = !!info.canRequestAds;
    admobOptionen = info.privacyOptionsRequirementStatus === 'REQUIRED';
    if(admobDarf && !admobGestartet && !ohneStart){
      await AdMobP.initialize({
        initializeForTesting: ADMOB_TEST || ADMOB_TESTGERAETE_JETZT.length > 0,
        testingDevices: ADMOB_TESTGERAETE_JETZT,
        maxAdContentRating: 'General'});
      admobGestartet = true;
    }
  }catch(e){}
}

/* Auf das Ereignis warten, mit dem das SDK sagt „fertig" oder „ging nicht".
   Ohne Frist könnte die App hängenbleiben, wenn gar nichts mehr kommt. */
/* DIE HORCHER MUESSEN STEHEN, BEVOR DIE ANZEIGE STARTET.
   addListener liefert ein Versprechen. Bis zum 27.09.2026 wurde darauf nicht
   gewartet: admobWarten meldete an, und showInterstitial() lief im selben Zug
   los. War die Anmeldung dann noch nicht durch, kamen interstitialAdShowed und
   interstitialAdDismissed bei niemandem an. Die Anzeige stand auf dem Schirm,
   die App wartete zwei Minuten in der Frist, zaehlte nichts und meldete
   "nicht gelaufen".
   Am Geraet belegt: werbungHeute stand bei n=0 und lohn=4 - der belohnte Weg
   benutzt gar keine Horcher, sondern den Rueckgabewert von
   showRewardVideoAd(), und lief deshalb immer. Nur das Interstitial hing am
   Wettlauf. Mit vorher angemeldeten Horchern feuerten alle drei Ereignisse
   sauber: Loaded 520,3 s, Showed 520,4 s, Dismissed 525,5 s.

   Deshalb ist die Funktion jetzt async und gibt einen Umschlag zurueck:
   { warten: Versprechen }. Ein nacktes Versprechen ginge nicht - await wuerde
   es mit dem inneren verketten und erst beim Ereignis zurueckkommen, also
   genau nach dem Zeigen, was wir vermeiden wollen. */
async function admobWarten(paare, frist){
  let melden = null;
  const warten = new Promise(f => { melden = f; });
  const handles = [];
  let uhr = 0;
  const schluss = w => {
    clearTimeout(uhr);
    handles.forEach(h => { try{ h.remove(); }catch(e){} });
    melden(w);
  };
  for(const [name, wert] of paare){
    try{ handles.push(await AdMobP.addListener(name, ()=>schluss(wert))); }catch(e){}
  }
  uhr = setTimeout(()=>schluss(false), frist);
  return {warten};
}

/* ---- Interstitial vorladen ----
   Bis zum 05.10.2026 wurde die Anzeige erst NACH der Lektion geladen. Das
   dauert ein bis mehrere Sekunden, und in der Zeit stand schon der
   Ergebnisschirm mit "Noch eine Lektion" da. Wer dort tippte, bekam die
   Anzeige gar nicht (zweiter Blick in admobZeigen) - sie ging verloren.
   Ajdin am 05.10.2026: "die kam aber bisschen verspaetet, man konnte
   theoretisch direkt die naechste Lektion anklicken".
   Jetzt wird sie schon beim Start einer Lektion oder eines Tests geladen,
   wie Google es empfiehlt, und liegt am Ende bereit. Eine geladene Anzeige
   ist bei AdMob eine Stunde gueltig; nach 50 Minuten wird neu geladen.
   Die Anzeige gilt nur, solange die Wahl zur Personalisierung dieselbe
   ist wie beim Laden. Wer sie abschaltet, bekommt nicht noch die Anzeige,
   die vorher personalisiert angefordert wurde - der Schalter verspricht,
   sofort zu wirken. Gefunden bei der Pruefung am 05.10.2026. */
let interVorrat = 0;          // Zeitpunkt, zu dem eine Anzeige fertig geladen war
let interLaedt = null;        // laufendes Laden, damit es nicht doppelt startet
let interNpa = null;          // npa, mit dem die bereite Anzeige angefordert wurde
let interLaedtNpa = null;     // npa des laufenden Ladens
const INTER_GUELTIG_MS = 50 * 60 * 1000;
const interstitialBereit = () => !!interVorrat && Date.now() - interVorrat < INTER_GUELTIG_MS &&
                                 interNpa === !werbungPersonalisiert();
function interstitialVorladen(){
  if(!AdMobP || !admobDarf || !werbungErlaubt(false)) return Promise.resolve(false);
  if(interstitialBereit()) return Promise.resolve(true);
  const npa = !werbungPersonalisiert();
  // Laeuft noch ein Laden mit der alten Wahl: abwarten, dann neu anfordern.
  if(interLaedt) return interLaedtNpa === npa ? interLaedt : interLaedt.then(()=> interstitialVorladen());
  interLaedtNpa = npa;
  interLaedt = AdMobP.prepareInterstitial({adId: ADMOB_ID.interstitial, isTesting: ADMOB_TEST, npa})
    .then(()=>{ interVorrat = Date.now(); interNpa = npa; return true; },
          e => { interVorrat = 0;
                 admobFehler = (e && (e.message || e.code)) ? String(e.message || e.code) : 'Laden gescheitert';
                 return false; })
    .finally(()=>{ interLaedt = null; });
  return interLaedt;
}

/* Zeigt eine Anzeige und kommt zurück, wenn sie wieder zu ist.
   true heißt: sie lief wirklich. */
/* darfNoch() ist die Bedingung, unter der die Anzeige ueberhaupt
   angefordert wurde - derselbe Bildschirm, dieselbe Lektion, App noch
   vorne. Sie wird unten ein zweites Mal geprueft, unmittelbar bevor die
   Anzeige auf den Schirm geht. Dazwischen liegt prepareInterstitial(),
   und das ist ein Netzabruf von ein bis mehreren Sekunden: genug Zeit,
   um auf „Noch eine Lektion“ zu tippen und die erste Aufgabe vor sich
   zu haben. Punkt 1 aus WERBUNG_PRUEFUNG.md, behoben am 29.09.2026. */
async function admobZeigen(belohnt, darfNoch){
  if(!AdMobP || !admobDarf) return false;
  try{
    if(belohnt){
      /* Punkt 17: prepare hatte keine Frist - nur show war abgesichert.
         Seit der Riegel aus Punkt 9/13 drin ist, waere ein haengendes
         prepare besonders unangenehm: die Sicherheitsleine macht zwar
         nach 150 Sekunden wieder auf, aber so lange soll niemand vor
         einem toten Knopf sitzen. Fuenfzehn Sekunden reichen - kein
         Mensch wartet zwei Minuten auf ein Leben.
         Der Grund fuer den Fehlschlag wird mitgenommen statt verschluckt,
         sonst sucht man beim naechsten Mal wieder von vorn. */
      let ladeFehler = null;
      const geladen = await Promise.race([
        AdMobP.prepareRewardVideoAd({adId: ADMOB_ID.belohnt, isTesting: ADMOB_TEST,
                                     npa: !werbungPersonalisiert()})
          .then(()=> true, e => { ladeFehler = e; return false; }),
        new Promise(f => setTimeout(()=> f(null), 15000))]);
      if(!geladen){
        admobFehler = ladeFehler ? String(ladeFehler.message || ladeFehler.code || ladeFehler)
                                 : 'Ladefrist von 15 s abgelaufen';
        return false;
      }
      /* Der zweite Blick, wie beim Interstitial unten: bis hierher
         konnten 15 Sekunden vergehen, und wer die App inzwischen
         weggelegt hat, bekaeme das Video sonst beim Zurueckkommen.
         Punkt 1, nachgezogen fuers belohnte Video. */
      if(darfNoch && !darfNoch()) return false;
      /* Punkt 11 und 16 aus WERBUNG_PRUEFUNG.md.
         Vorher entschied hier ein Rennen gegen zwei Minuten darueber, ob
         es ein Leben gibt. Zwei Wege liefen schief: wer waehrend des
         Videos angerufen wurde, sah es zu Ende und bekam trotzdem nichts
         - die Belohnung kam nach dem Rennen und fiel unter den Tisch.
         Und wer abbrach, wartete zwei volle Minuten auf nichts, weil das
         Plugin den Aufruf beim Schliessen ohne Belohnung weder aufloest
         noch ablehnt.
         Jetzt halten zwei Zuhoerer die beiden Dinge getrennt fest:
         onRewardedVideoAdReward sagt, DASS die Belohnung faellig wurde -
         das Plugin schreibt eigens dazu, dass Dismissed darueber nichts
         aussagt -, und Dismissed beendet das Warten, sobald der Nutzer
         die Anzeige wegdrueckt. Dieselbe Bauweise wie beim Interstitial
         ein Stueck weiter unten.
         Die Frist bleibt als letzter Ausweg stehen: ohne sie haengt der
         Aufruf bei einem Abbruch fuer immer. */
      let verdient = false;
      let lohnHorcher = null;
      try{ lohnHorcher = await AdMobP.addListener('onRewardedVideoAdReward',
                                                  ()=>{ verdient = true; }); }catch(e){}
      const fertigLohn = await admobWarten([['onRewardedVideoAdDismissed', true],
                                            ['onRewardedVideoAdFailedToShow', false]], 120000);
      /* Nicht awaiten: das Versprechen loest nur auf, wenn es eine
         Belohnung gibt. Kommt sie, wird sie hier trotzdem noch
         mitgenommen - doppelt haelt besser als der Zuhoerer allein. */
      AdMobP.showRewardVideoAd().then(lohn => { if(lohn) verdient = true; }, ()=>{});
      /* true heisst: das Video stand und wurde geschlossen. Ohne Belohnung
         hat der Nutzer es also vorher weggedrueckt. 07.10.2026. */
      const geschlossen = await fertigLohn.warten;
      if(lohnHorcher) try{ lohnHorcher.remove(); }catch(e){}
      lohnAbgebrochen = geschlossen === true && !verdient;
      return verdient;
    }
    /* Vorgeladen ist die Anzeige meist schon (siehe interstitialVorladen).
       Nur wenn nicht, wird wie frueher hier geladen. Liegt keine bereit
       und das Laden scheitert, wirft prepare - das faengt der catch
       unten ab wie bisher. */
    if(!interstitialBereit()){
      const geladen = await interstitialVorladen();
      if(!geladen) throw new Error(admobFehler || 'Interstitial nicht geladen');
    }
    /* Hier der zweite Blick. Passt es nicht mehr, wird die geladene
       Anzeige einfach nicht gezeigt - sie bleibt im Plugin liegen und
       kommt am Ende der naechsten Lektion. Lieber eine Einblendung
       weniger als eine ueber einer laufenden Aufgabe.
       Erst danach gilt sie als verbraucht. Stand das vorher, war sie nach
       einem Tipp auf "Noch eine Lektion" waehrend des Ladens als weg
       markiert, obwohl sie bereitlag, und wer immer schnell weitertippte,
       sah die ganze Sitzung keine. Gefunden bei der Pruefung am 05.10.2026. */
    if(darfNoch && !darfNoch()) return false;
    interVorrat = 0;               // wird jetzt gezeigt - beim naechsten Mal neu laden
    /* GEZAEHLT wird, sobald die Anzeige wirklich auf dem Schirm stand, und
       GEWARTET wird, bis der Nutzer sie geschlossen hat. Das sind zwei
       verschiedene Dinge, und bis zum 27.09.2026 hingen beide am
       Schliess-Ereignis: kam es nicht, lief admobZeigen nach zwei Minuten in
       die Frist, gab false zurueck, und die Anzeige galt als nicht gelaufen -
       obwohl sie da war. Gemessen: werbungHeute.n stand nach elf Lektionen
       auf 0, waehrend prepareInterstitial und showInterstitial einzeln
       aufgerufen beide sauber durchliefen.
       Ajdin am 27.09.2026: "also es kommt nicht immer werbung nach der
       lektion und nach dem test auch nicht". */
    let gezeigt = false;
    /* Auch hier auf die Anmeldung warten - aus demselben Grund wie in
       admobWarten. */
    let gesehen = null;
    try{ gesehen = await AdMobP.addListener('interstitialAdShowed', ()=>{ gezeigt = true; }); }
    catch(e){}
    const zu = await admobWarten([['interstitialAdDismissed', true],
                                  ['interstitialAdFailedToShow', false]], 120000);
    await AdMobP.showInterstitial();
    await zu.warten;
    if(gesehen) try{ gesehen.remove(); }catch(e){}
    interstitialVorladen();        // fuer die naechste Lektion schon bereitlegen
    return gezeigt;
  }catch(e){
    /* Auch hier den Grund stehen lassen statt ihn zu verschlucken - sonst
       sucht man beim naechsten Mal wieder von vorne. */
    admobFehler = (e && (e.message || e.code)) ? String(e.message || e.code) : 'unbekannt';
    return false;
  }
}
const SCHUTZ_MAX = 2;              // so viele Serienschutz gleichzeitig  (muss zu start.py passen)
const SCHUTZ_TAGE = 10;            // alle so viele Tage wächst ein Schutz nach
const ALLE_FREI = new URLSearchParams(location.search).get('alle') === '1';
/* Sandbox in der Test-App (08.11.2026, Ajdin: "nein bei der test app lass
   sie offen das ist wie eine sandbox app", und "ja" zu einem festen
   Schalter "alles offen"). In "Zmaj Test" ist jedes Level und jede Sektion
   offen, auch der Zahnarzt-Teil, jeder Level-Test und jede Geschichte - wie
   mit ?alle=1, aber NUR die Sperren: Leben, Werbung, Einstufung und die
   Frage nach der Bewertung laufen wie in der echten App. Freigeschaltet
   wird nur im Kopf der App, in passed, known oder read wird dafuer nichts
   geschrieben. Wer dort lernt, lernt wie immer: Lernstand, Speichern und
   Cloud-Abgleich bleiben genau wie bisher.
   An ist sie nur, wenn BEIDES stimmt:
     - Android selbst meldet ueber App.getInfo() die App-ID
       de.smartdragon.zmaj.test. Die hat nur der debug-Bau der Huelle
       (applicationIdSuffix ".test" in app/build.gradle), Google Play kennt
       sie nicht. Die echte App meldet de.smartdragon.zmaj.
     - APP_VERSION endet auf "-test". Das setzt app_bauen.py
       (version_einsetzen) nur fuer das Debug-Paket und --nur-abgleich,
       nie fuer --aab.
   Im Zweifel aus: im Browser gibt es kein window.Capacitor, und fehlt
   etwas, wirft getInfo() oder antwortet es nicht binnen SANDBOX_WARTEN,
   bleibt alles gesperrt wie bisher. Gefragt wird einmal in starten(), vor
   dem ersten Zeichnen. Zu sehen ist sie nur in der Versionszeile, siehe
   versionText(). */
const SANDBOX_APP_ID = 'de.smartdragon.zmaj.test';
const SANDBOX_WARTEN = 2000;
let SANDBOX = false;
function sandboxErkannt(appId, version){
  return appId === SANDBOX_APP_ID && typeof version === 'string' && /-test$/.test(version);
}
async function sandboxPruefen(){
  SANDBOX = false;
  try{
    const C = window.Capacitor;
    const A = C && C.Plugins && C.Plugins.App;
    if(!A || typeof A.getInfo !== 'function') return false;
    if(typeof C.isNativePlatform !== 'function' || C.isNativePlatform() !== true) return false;
    if(!sandboxErkannt(SANDBOX_APP_ID, APP_VERSION)) return false;   // Store-Bau: gar nicht erst fragen
    const info = await Promise.race([A.getInfo(),
                                     new Promise(r => setTimeout(() => r(null), SANDBOX_WARTEN))]);
    SANDBOX = sandboxErkannt(info && info.id, APP_VERSION);
  }catch(e){ SANDBOX = false; }
  return SANDBOX;
}
/* Ob die Sperren gerade ausgesetzt sind: ?alle=1 oder die Sandbox. */
const allesOffen = () => ALLE_FREI || SANDBOX;

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
