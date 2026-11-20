/* ===== Zmaj bewerten und empfehlen (Einstellungen, Ueber die App) =====
   07.10.2026. Bewerten geht hier gleich in den Play Store und nicht ueber
   Googles Fenster in der App: das hat ein Kontingent und kommt oft gar
   nicht, deshalb raet Google bei Knoepfen davon ab (ZmajBewertung.java).
   Empfehlen nutzt dasselbe Teilen-Menue wie die Sicherung - kein Netz,
   keine neue Bibliothek. referrer=utm_source app_teilen laesst die Play
   Console die Installationen ueber diesen Weg zaehlen (WERBEPLAN.md,
   Abschnitt 2). Am PC ohne Teilen-Menue geht das Mailprogramm auf. */
/* iPhone und iPad (30.10.2026): die Seite der App im App Store. Die Nummer
   (Apple-ID der App) gibt es erst mit dem Eintrag in App Store Connect
   (Stufe B). Bis dahin steht hier ein Platzhalter, und app_bauen.py --ios
   setzt sie aus ios_zugang.xcconfig der Huelle in die KOPIE ein, wie die
   Werbe-IDs. Ohne Nummer gibt es auf iOS keinen Link in einen Store - die
   beiden Zeilen "Bewerten" und "Empfehlen" sind dann ausgeblendet
   (einstellungenFuerPlattform), statt ins Leere zu fuehren. */
/* APPLE_APP_ID steht im Bauwerte-Block vor diesem Skript. */
const appStoreDa = () => /^[0-9]{6,12}$/.test(APPLE_APP_ID);
const appStoreLink = () => appStoreDa() ? 'https://apps.apple.com/app/id' + APPLE_APP_ID : '';
/* Der Weg in den Store fuer Bewerten und Empfehlen: auf iOS der App Store,
   sonst wie bisher Google Play. */
function storeLink(teilen){
  if(IST_IOS) return appStoreLink();
  return 'https://play.google.com/store/apps/details?id=' + ZMAJ_PAKET
    + (teilen ? '&referrer=utm_source%3Dapp_teilen' : '');
}
$('setBewerten').addEventListener('click', async ()=>{
  const P = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.ZmajBewertung;
  if(P){ try{ await P.storeOeffnen(); }catch(e){} return; }
  /* iOS ohne Plugin gibt es eigentlich nicht; dann wenigstens die Seite zum
     Schreiben einer Bewertung (?action=write-review, Apples Weg). */
  const u = IST_IOS ? (appStoreDa() ? appStoreLink() + '?action=write-review' : '') : storeLink(false);
  if(u) try{ window.open(u, '_blank', 'noopener'); }catch(e){}
});
$('setEmpfehlen').addEventListener('click', async ()=>{
  const P = window.Capacitor && window.Capacitor.Plugins;
  const text = t('set.empfehlen_text');
  const link = storeLink(true);
  if(!link) return;
  try{
    if(P && P.Share) await P.Share.share({title: 'Zmaj', text: text, url: link, dialogTitle: t('set.empfehlen')});
    else if(navigator.share) await navigator.share({title: 'Zmaj', text: text, url: link});
    else location.href = 'mailto:?subject=Zmaj&body=' + encodeURIComponent(text + ' ' + link);
  }catch(e){}   // Menue ohne Auswahl geschlossen: nichts zu melden
});

const ZMAJ_MAIL = 'zmaj.lernapp@gmail.com';

/* Ohne Server kann die App keine Mail verschicken - das kann nur das Geraet.
   Also oeffnen wir die Mail-App des Nutzers mit fertig ausgefuellter
   Nachricht. Kein fremder Dienst, keine zusaetzlichen Daten.
   Falls kein Mail-Programm eingerichtet ist, passiert sichtbar nichts -
   deshalb steht die Adresse danach zum Kopieren da.
   Seit 01.11.2026 ist das in der Handy-App mit Konto nur noch der
   Rueckfall: dort geht Feedback ueber das Kontaktformular
   (feedbackUeberFormular, weiter unten). Ohne Cloud bleibt es der Weg. */
function feedbackPerMail(text, notiz){
  const betreff = 'Zmaj – ' + t('set.feedback');
  const fuss = '\n\n--\n' + (SPRACHE||'') + ' · ' + today();   // oertlicher Tag, siehe Widerruf
  try{ location.href = 'mailto:' + ZMAJ_MAIL
        + '?subject=' + encodeURIComponent(betreff)
        + '&body=' + encodeURIComponent(text + fuss); }catch(e){}
  const kasten = notiz || $('fbNote');
  kasten.textContent = t('set.feedback_mail', {mail: ZMAJ_MAIL}) + ' ';
  const knopf = document.createElement('button');
  knopf.className = 'back'; knopf.type = 'button';
  knopf.textContent = t('set.feedback_kopieren');
  knopf.addEventListener('click', async ()=>{
    try{ await navigator.clipboard.writeText(ZMAJ_MAIL); knopf.textContent = t('set.feedback_kopiert'); }
    catch(e){ knopf.textContent = ZMAJ_MAIL; }
  });
  kasten.appendChild(knopf);
}
/* Feedback ueber das Kontaktformular statt ueber das Mailprogramm
   (01.11.2026). Ajdin beim Test der 1.2: "wo ist das kontaktformular ist
   das das mit dem feedback" - auf die Rueckfrage, ob Feedback darueber
   gehen soll: "Uebers Formular". Text eintippen, Senden, fertig, kein
   Mailprogramm; die Nachricht landet wie die vom Webformular in seinem
   Gmail (nachrichten/{uid}, kontakt_weiterleitung.gs).
   Nur in der Handy-App (cloudModus) und nur angemeldet: geantwortet wird
   an die Adresse des Kontos (cloudMerker().email). Sie muss zur Regel in
   firestore.rules passen (antwort.matches, hoechstens 254 Zeichen) -
   FEEDBACK_ADRESSE ist dasselbe Muster, tests/test_kontakt.py vergleicht
   beide. Ohne Konto, ohne Netz, wenn Firebase ablehnt oder die Adresse
   nicht passt: wie bisher das Mailprogramm (feedbackPerMail), verloren
   geht also nichts. Ohne Cloud (Web-Fassung, start.py) bleibt alles wie
   vorher. */
const FEEDBACK_ADRESSE = /^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?([.][A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?)+$/;
function feedbackAdresse(){
  const m = cloudMerker(), a = String((m && m.email) || '').trim();
  return (a.length <= 254 && FEEDBACK_ADRESSE.test(a)) ? a : '';
}
/* true, wenn die Nachricht in Firebase liegt - sonst false, nie ein Wurf. */
async function feedbackUeberFormular(text, adresse){
  const a = cloudAdapter();
  if(!a || !a.nachricht || !adresse) return false;
  try{ return await a.nachricht(text, adresse, SPRACHE) === true; }
  catch(e){ return false; }
}
let feedbackLaeuft = false;     // zweimal Senden hiesse zwei Mails
/* Schickt ein Feedback ab - aus den Einstellungen und aus dem Vorschlag
   nach der Bewertungsfrage (zeigeVorschlag), die schon immer denselben
   Weg nahmen. notiz bekommt die Meldung, knopf ist waehrenddessen aus.
   true: ueber das Formular angekommen; false: das Mailprogramm ist
   aufgegangen; null: es laeuft schon eins, nichts getan. */
async function feedbackSenden(text, notiz, knopf){
  const adresse = cloudModus() ? feedbackAdresse() : '';
  if(adresse){
    if(feedbackLaeuft) return null;
    feedbackLaeuft = true;
    const fokus = document.activeElement === knopf;
    knopf.disabled = true;
    notiz.textContent = t('set.feedback_sendet');
    const geklappt = await feedbackUeberFormular(text, adresse);
    feedbackLaeuft = false;
    knopf.disabled = false;
    /* Pruefbericht 01.11.2026: Ein abgeschalteter Knopf verliert den Fokus,
       ein Screenreader stand danach irgendwo am Seitenanfang. Zurueck auf
       den Knopf, wenn der Fokus nicht schon woanders hin gewandert ist. Die
       Meldungen selbst sagt role="status" an (fbNote, bwNote). */
    if(fokus && knopf.isConnected && (!document.activeElement || document.activeElement === document.body)) knopf.focus();
    if(geklappt){ notiz.textContent = t('set.feedback_danke'); return true; }
  }
  feedbackPerMail(text, notiz);
  return false;
}
$('fbSend').addEventListener('click', async ()=>{
  const text=$('fbText').value.trim(); if(!text){ $('fbNote').textContent=t('set.feedback_leer'); return; }
  if(!MIT_SERVER){
    const r = await feedbackSenden(text, $('fbNote'), $('fbSend'));
    if(r === null) return;
    if(r) $('fbText').value = '';
    sound('ok');
    return;
  }
  try{
    const r=await fetch('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({profil, text})});
    const d=await r.json();
    if(d.ok){ $('fbText').value=''; $('fbNote').textContent=t('set.feedback_danke'); sound('ok'); }
    else $('fbNote').textContent = t('set.feedback_fehler');
  }catch(e){ feedbackPerMail(text); }
});

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
