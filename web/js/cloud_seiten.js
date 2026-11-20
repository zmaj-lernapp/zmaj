/* ---- Das Tor: ohne Anmeldung geht es nach der 1. Lektion nicht weiter ----
   28.10.2026, Ajdin am 27.10.: "nach der 1. Lektion, wie bei Duolingo".
   Wer noch nichts gelernt hat, lernt ohne Konto. Wer etwas gelernt hat
   (oder dessen altes Handy einen Restore-Schluessel hinterlassen hat, oder
   der sich abgemeldet hat), sieht nur noch die Anmeldung - auch beim
   naechsten Start. Ohne Internet gibt es kein Tor: dann wird einfach
   weitergelernt, die Serie haengt nur am Geraet. netzWeg: die Anmeldung
   ist eben am Netz gescheitert, obwohl navigator.onLine Netz meldete, und
   der Lernende hat "Erst einmal weiterlernen" gewaehlt - bis zum naechsten
   'online' oder Start. Seit dem Pruefbericht vom 28.10. auch, wenn es an
   Firebase oder Google lag (anmFehlerZeigen) - dann bis zum naechsten
   Start. */
let netzWeg = false;
let anmeldungLaeuft = false;
let anmAnlass = 'sichern', anmModus = 'wahl';
/* Die Einstufung zaehlt, sobald darin eine Frage beantwortet ist - nicht
   bei "Ich fange neu an" und nicht bei einem Abbruch gleich bei Frage 1
   (fragen ist dann 0), wie im Plan 2.5. Gewusste Woerter zaehlen nur, wenn
   sie schon beim Laden da waren (gewusstGeladen: Stand von v108, eine
   Sicherung, die Cloud). known.add() laeuft mitten in der Lektion - wer
   Lektion 1 halb machte und verliess, stand sonst vor der Anmeldung, ohne
   eine Lektion beendet zu haben. Gegenpruefung 28.10.2026. */
const hatGelernt = () => days.size > 0 || gewusstGeladen || passed.size > 0
  || !!(einstufung && einstufung.fragen > 0);
function warAbgemeldet(){ try{ return localStorage.getItem(ABGEMELDET) === '1'; }catch(e){ return false; } }
function anmeldungFaellig(){
  return cloudModus() && standGeladen && !cloudMerker()
    && (hatGelernt() || !!restoreUid || warAbgemeldet())
    && navigator.onLine !== false && !netzWeg && !anmSpaeterHeute();
}
/* "Spaeter" auf iPhone und iPad (30.10.2026, Entscheidung 7). Apple: wer
   keine kontogebundenen Funktionen braucht, darf ohne Anmeldung lernen
   (Richtlinie 5.1.1(v)). Das Konto sichert bei Zmaj nur den Lernstand.
   Also gibt es dort neben der Anmeldung "Spaeter", und das Tor bleibt fuer
   den Rest des Tages offen; am naechsten Tag fragt es wieder, mit demselben
   Ausweg. Auf Android bleibt die Pflicht wie seit v109. */
const ANM_SPAETER = 'zmaj_anm_spaeter';
function anmSpaeterHeute(){
  if(!IST_IOS) return false;
  try{ return localStorage.getItem(ANM_SPAETER) === today(); }catch(e){ return false; }
}
/* Welcher Anmeldeweg zuletzt lief: 'google', 'apple' oder ''. Nur fuer die
   Fehlermeldung - INVALID_IDP_RESPONSE kommt bei beiden. 30.10.2026 */
let anmWeg = '';
function anmeldungAnlass(){
  if(restoreUid && !hatGelernt()) return 'zurueck';
  if(warAbgemeldet()) return 'abgemeldet';
  return days.size > 1 ? 'bestand' : 'sichern';
}
/* true: die Anmeldung steht (oder steht jetzt), der Aufrufer bricht ab. */
function anmeldungSperre(){
  if(!anmeldungFaellig()) return false;
  if(!sichtbar('profileView')) anmeldungZeigen(anmeldungAnlass());
  return true;
}
/* Nach 'online' und beim Zurueckkommen in die App: auf der Startseite gleich,
   sonst beim naechsten Wechsel der Ansicht (showView) - mitten in einer
   Lektion nie, und nicht ueber einer offenen Karte. */
function torPruefen(){
  if(!anmeldungFaellig() || !sichtbar('pfad') || frageSchliessen) return;
  if(document.querySelector('.nachfrage, .einwilligung, .werbung, .updsperre')) return;
  anmeldungSperre();
}
/* Statt der Knoepfe auf einem Ergebnisschirm nur "Weiter" zur Anmeldung. */
function torStattKnoepfe(ids){
  const erster = $(ids[0]);
  if(!erster || !erster.parentElement) return;
  const feld = erster.parentElement.parentElement;
  ids.forEach(id => { const b = $(id); if(b && b.parentElement) b.parentElement.remove(); });
  const reihe = document.createElement('div');
  reihe.className = 'row';
  reihe.innerHTML = '<button class="btn know" id="anmWeiter"></button>';
  const k = reihe.querySelector('button');
  k.textContent = t('anm.weiter');
  k.addEventListener('click', ()=>{ if(!anmeldungSperre()){ homeMode = 'words'; showHome(); } });
  feld.appendChild(reihe);
}
function kopfZurueck(){
  $('btnSettings').style.display = 'inline-block';
  $('btnShop').style.display = 'inline-block';
  $('btnProfil').style.display = 'inline-block';     // auch ohne Konto, siehe nachAnmeldung (14.11.2026)
}

/* ---- Die Anmeldeseite ----
   Dieselbe Seite wie die alte Server-Anmeldung (profileView, kontoForm),
   die fuer start.py unveraendert bleibt (zeigeAnmeldung). anlass bestimmt
   Titel und Text, modus die Felder:
     wahl            Mit Google / Mit E-Mail, darunter Datenschutz und
                     Nutzungsbedingungen zum Aufklappen
     mail_an         E-Mail und Passwort
     mail_neu        Konto anlegen: E-Mail, Passwort, Wiederholung
     mail_vergessen  E-Mail, Link zum Zuruecksetzen schicken
   Die Flaggen fuer die Sprache stehen oben wie bisher. */
function anmeldungZeigen(anlass, modus = 'wahl', daten = {}){
  anmAnlass = anlass || anmAnlass;
  anmModus = modus;
  showView('profileView'); $('kopfLeiste').style.display = 'none';
  $('btnProfil').style.display = 'none'; $('btnSettings').style.display = 'none'; $('btnShop').style.display = 'none';
  $('zmajProfile').innerHTML = zmaj('happy'); setMood($('zmajProfile'), 'happy');
  renderLangBar();
  $('tag').textContent = '';
  const wahl = modus === 'wahl';
  const titel = modus === 'mail_neu' ? 'konto.anlegen_titel' : modus === 'mail_vergessen' ? 'konto.vergessen_titel'
    : modus === 'mail_an' ? 'konto.anmelden_titel'
    : ({sichern: 'anm.titel_sichern', bestand: 'anm.titel_bestand', zurueck: 'anm.titel_zurueck'}[anmAnlass] || 'konto.anmelden_titel');
  const text = modus === 'mail_vergessen' ? 'konto.vergessen_frage'
    : ({sichern: 'anm.text_sichern', bestand: 'anm.text_bestand', zurueck: 'anm.text_zurueck',
        konto: 'anm.text_zurueck'}[anmAnlass] || 'anm.text_abgemeldet');
  $('kontoTitel').textContent = t(titel);
  $('kontoFrage').textContent = t(text);
  $('anmWahl').hidden = !wahl;
  $('kontoForm').hidden = wahl;
  $('anmOffline').hidden = !daten.netz;
  $('anmOffline').textContent = t('anm.weiterlernen');
  /* Wer ueber "Ich habe schon ein Konto" kam und noch gar nicht muss, kommt
     hier auch wieder heraus. Wer muss, hat in der Wahl keinen Weg zurueck -
     die Zurueck-Taste fragt dann wie auf der Startseite, ob Zmaj zugehen soll. */
  const zurueck = !wahl ? ()=> anmeldungZeigen(anmAnlass, 'wahl')
    : (anmeldungFaellig() ? null : ()=>{ kopfZurueck(); homeMode = 'words'; showHome(); });
  setzeZurueck(zurueck ? t('btn.zurueck') : '', zurueck);
  /* "Spaeter" nur auf iOS, nur in der Wahl und nur, wenn das Tor wirklich
     zu ist - wer freiwillig hier ist, hat schon die Zurueck-Taste. */
  $('anmSpaeter').hidden = !(IST_IOS && wahl && anmeldungFaellig());
  $('anmSpaeter').textContent = t('anm.spaeter');
  if(wahl){
    anmKnoepfeStellen();
    $('anmMail').textContent = t('anm.mail');
    $('anmNote').textContent = daten.hinweis || '';
    $('anmNote').className = daten.hinweis ? 'note feedback no' : 'note';
    $('anmDsKopf').textContent = t('set.datenschutz');
    $('anmDs').innerHTML = t('set.datenschutz_text', {anbieter: t('set.anbieter')});
    $('anmAgbKopf').textContent = t('set.agb');
    $('anmAgb').innerHTML = t('set.agb_text', {anbieter: t('set.anbieter')});
    $('anmImpKopf').textContent = t('set.impressum');
    $('anmImp').innerHTML = t('set.impressum_text', {anbieter: t('set.anbieter')});
    $('kontoWechsel').hidden = true; $('kontoVergessen').hidden = true;
    return;
  }
  const neu = modus === 'mail_neu', vergessen = modus === 'mail_vergessen';
  $('kontoName').hidden = true; $('kontoNameSub').hidden = true; $('kontoBleibenZeile').hidden = true;
  $('kontoMail').hidden = false;
  $('kontoPw').hidden = vergessen;
  $('kontoPw2').hidden = !neu;
  $('kontoRegeln').hidden = !neu;
  pwListeBeschreibt(neu);
  $('kontoSpam').hidden = true;
  $('kontoSpam').textContent = t('konto.spam_kurz');
  $('kontoPw').placeholder = t(neu ? 'konto.passwort_neu' : 'konto.passwort');
  $('kontoPw').setAttribute('autocomplete', neu ? 'new-password' : 'current-password');
  $('kontoSenden').textContent = t(neu ? 'konto.neu' : vergessen ? 'konto.vergessen_senden' : 'konto.anmelden');
  $('kontoWechsel').hidden = false;
  $('kontoWechsel').textContent = t(modus === 'mail_an' ? 'konto.neu' : 'konto.zurueck_anmelden');
  $('kontoVergessen').hidden = modus !== 'mail_an';
  $('kontoNote').textContent = daten.hinweis || '';
  $('kontoNote').className = daten.hinweis ? 'note feedback no' : 'note';
  $('kontoPw').value = ''; $('kontoPw2').value = '';
  if(neu) zeigeRegeln($('kontoRegeln'), '', $('kontoMail').value);
  $('kontoMail').focus();
}
/* Eine Firebase-Antwort als Satz. Firebase haengt manchmal " : ..." an,
   deshalb zaehlt nur der Anfang (wie in kontoWeg). Leer: nichts zu sagen
   (Google-Auswahl abgebrochen). */
/* Die Anmeldeknoepfe der Wahl: Apple (nur iOS) ueber Google, beide nur,
   wenn die Huelle sie kann - ohne Client-ID in der Huelle gibt es keinen
   Google-Knopf (anbieterFragen). 30.10.2026 */
function anmKnoepfeStellen(){
  $('anmApple').hidden = !appleMoeglich();
  $('anmAppleText').textContent = t('anm.apple');
  $('anmGoogle').hidden = !googleMoeglich();
  $('anmGoogleText').textContent = t('anm.google');
}
function kontoFirebaseFehler(g){
  g = String(g || '');
  if(g === 'netz') return t('konto.fehler_netz');
  if(/^(INVALID_LOGIN_CREDENTIALS|EMAIL_NOT_FOUND|INVALID_PASSWORD|MISSING_PASSWORD)/.test(g)) return t('konto.fehler_mail_pw');
  if(/^EMAIL_EXISTS/.test(g)) return t('konto.fehler_email_da');
  if(/^(INVALID_EMAIL|MISSING_EMAIL)/.test(g)) return t('konto.fehler_email');
  if(/^WEAK_PASSWORD/.test(g)) return t('konto.fehler_kurz', {n: PW_MIN_CLOUD});
  /* Die Passwort-Richtlinie in der Konsole (29.10.2026, siehe
     PW_REGELN_CLOUD). Beim Anlegen kommt das nur, wenn die Konsole strenger
     ist als die App, etwa mehr als 8 Zeichen. Beim Anmelden, wenn dort
     "Upgrade bei der Anmeldung erzwingen" an ist und das alte Passwort die
     Regeln nicht erfuellt - dann hilft nur ein neues, ueber "Passwort
     vergessen?". */
  if(/^PASSWORD_DOES_NOT_MEET_REQUIREMENTS/.test(g))
    return t(anmModus === 'mail_an' ? 'konto.fehler_pw_erneuern' : 'konto.fehler_pw_regeln');
  if(/^TOO_MANY_ATTEMPTS_TRY_LATER/.test(g)) return t('konto.fehler_zu_oft');
  if(/^USER_DISABLED/.test(g)) return t('konto.fehler_konto_gesperrt');
  if(g === 'GOOGLE_ABGEBROCHEN' || g === 'APPLE_ABGEBROCHEN') return '';
  if(g === 'GOOGLE_KEIN_KONTO') return t('konto.fehler_google_keins');
  /* Apple vor INVALID_IDP_RESPONSE: das kommt bei beiden Wegen, gemeint ist
     der, der zuletzt lief (anmWeg). 30.10.2026 */
  if(/^APPLE_(FEHLER|ANDERES_KONTO)/.test(g) || (anmWeg === 'apple' && /^INVALID_IDP_RESPONSE/.test(g)))
    return t('konto.fehler_apple');
  if(/^(GOOGLE_FEHLER|INVALID_IDP_RESPONSE)/.test(g)) return t('konto.fehler_google');
  return t('konto.fehler_allgemein');
}
/* 28.10.2026 (Pruefbericht): "Erst einmal weiterlernen" nicht nur ohne
   Netz, sondern bei jedem Fehler, gegen den der Lernende nichts tun kann:
   Firebase antwortet mit 5xx oder 429, ein Anmeldeweg ist in der Konsole
   aus (OPERATION_NOT_ALLOWED), der Schluessel ist falsch beschraenkt, oder
   Googles Auswahl scheitert (GOOGLE_FEHLER). Sonst saesse am Tag nach dem
   Update jeder mit Lernstand fest. Keinen Ausweg gibt es nur bei diesen
   Gruenden: Eingabefehler, abgebrochene Auswahl, kein Google-Konto auf dem
   Handy (dann E-Mail) und ein gesperrtes Konto. */
const ANM_OHNE_AUSWEG = /^(INVALID_LOGIN_CREDENTIALS|EMAIL_NOT_FOUND|INVALID_PASSWORD|MISSING_PASSWORD|EMAIL_EXISTS|INVALID_EMAIL|MISSING_EMAIL|WEAK_PASSWORD|PASSWORD_DOES_NOT_MEET_REQUIREMENTS|USER_DISABLED|GOOGLE_ABGEBROCHEN|GOOGLE_KEIN_KONTO|APPLE_ABGEBROCHEN)/;
function anmFehlerZeigen(grund, note){
  const text = kontoFirebaseFehler(grund);
  note.textContent = text;
  note.className = text ? 'note feedback no' : 'note';
  if(!ANM_OHNE_AUSWEG.test(String(grund || ''))) $('anmOffline').hidden = false;
}
/* Angemeldet: hinein. Nach dem Anlegen eines Kontos sagt eine Karte, dass
   die Bestaetigungsmail unterwegs ist. Sonst nichts mehr: bis 29.10.2026
   stand dann 3,5 Sekunden "Du bist angemeldet. ✓" an der Stelle der
   Herzpille oben links. Ajdin am 29.10.2026: "mach das komplett raus, ist
   unnoetig" - dass man drin ist, sieht man an der Startseite. Der Satz war
   auch die Ueberschrift der Karte; die Karte sagt ihr Eigentliches jetzt
   ohne. Darunter seit 29.10.2026 der kurze Hinweis auf den Spam-Ordner -
   dort lag bei Ajdin die Bestaetigungsmail. */
function cloudNachAnmeldung(neu){
  netzWeg = false;
  kopfZurueck();
  homeMode = 'words';
  showHome();
  if(!neu) return;
  const {kasten, zu} = einstufungKarte(
    '<div class="celebrate"><div class="zmaj cheer">' + zmaj('cheer') + '</div></div>' +
    '<div class="txt"></div><div class="spamhinweis"></div><button class="btn know" id="anmFertigOk"></button>');
  kasten.querySelector('.txt').textContent = t('konto.bestaetigung_raus');
  kasten.querySelector('.spamhinweis').textContent = t('konto.spam_kurz');
  kasten.querySelector('#anmFertigOk').textContent = t('task.weiter');
  kasten.querySelector('#anmFertigOk').addEventListener('click', zu);
}
async function cloudFormularSenden(){
  if(anmeldungLaeuft) return;
  const m = anmModus, note = $('kontoNote'), knopf = $('kontoSenden');
  const adr = $('kontoMail').value.trim(), pw = $('kontoPw').value, pw2 = $('kontoPw2').value;
  note.className = 'note';
  /* Rot wie die Antworten von Firebase - grau las sich ein Fehler wie ein
     Hinweis (29.10.2026). */
  const nein = text => { note.textContent = text; note.className = 'note feedback no'; };
  if(!/^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$/.test(adr)) return nein(t('konto.fehler_email'));
  if(m === 'mail_an' && !pw) return nein(t('konto.fehler_mail_pw'));
  if(m === 'mail_neu'){
    /* Die Zeile sagt, was als Erstes fehlt, die Liste darueber faerbt alles
       rot, was noch fehlt (29.10.2026, PW_REGELN_CLOUD). */
    const fehlt = pwFehltCloud(pw, adr);
    if(fehlt){ zeigeRegeln($('kontoRegeln'), pw, adr, true); return nein(pwFehlerCloud(fehlt)); }
    if(pw !== pw2) return nein(t('konto.fehler_wdh'));
  }
  anmeldungLaeuft = true;
  knopf.disabled = true; note.textContent = t('konto.laeuft');
  try{
    if(m === 'mail_vergessen'){
      try{ await cloudAdapter().passwortVergessen(adr); }
      catch(e){
        const g = cloudGrund(e);
        if(g === 'netz' || /^(INVALID_EMAIL|MISSING_EMAIL|TOO_MANY_ATTEMPTS_TRY_LATER)/.test(g)){ anmFehlerZeigen(g, note); return; }
        // sonst dieselbe Antwort wie bei Erfolg - verraten wird nichts
      }
      note.textContent = t('konto.vergessen_raus');
      note.className = 'note feedback ok';
      $('kontoSpam').hidden = false;      // jetzt gibt es etwas zu suchen
      return;
    }
    const art = m === 'mail_neu' ? 'neu' : 'passwort';
    if(await cloudAnmelden(art, cloudAdapter(), {email: adr, pw})){
      $('kontoPw').value = ''; $('kontoPw2').value = '';
      note.textContent = '';
      cloudNachAnmeldung(art === 'neu');
      return;
    }
    anmFehlerZeigen(cloudFehlerGrund, note);
  }finally{
    anmeldungLaeuft = false;
    knopf.disabled = false;
  }
}
$('anmGoogle').addEventListener('click', async ()=>{
  if(anmeldungLaeuft || !cloudModus()) return;
  const note = $('anmNote');
  anmeldungLaeuft = true;
  anmWeg = 'google';
  $('anmGoogle').disabled = true;
  note.className = 'note'; note.textContent = t('konto.laeuft');
  try{
    if(await cloudAnmelden('google')){ note.textContent = ''; cloudNachAnmeldung(false); return; }
    anmFehlerZeigen(cloudFehlerGrund, note);
  }finally{
    anmeldungLaeuft = false;
    $('anmGoogle').disabled = false;
  }
});
/* "Mit Apple anmelden" (iOS, 30.10.2026) - derselbe Ablauf wie Google. */
$('anmApple').addEventListener('click', async ()=>{
  if(anmeldungLaeuft || !cloudModus()) return;
  const note = $('anmNote');
  anmeldungLaeuft = true;
  anmWeg = 'apple';
  $('anmApple').disabled = true;
  note.className = 'note'; note.textContent = t('konto.laeuft');
  try{
    if(await cloudAnmelden('apple')){ note.textContent = ''; cloudNachAnmeldung(false); return; }
    anmFehlerZeigen(cloudFehlerGrund, note);
  }finally{
    anmeldungLaeuft = false;
    $('anmApple').disabled = false;
  }
});
$('anmSpaeter').addEventListener('click', ()=>{
  try{ localStorage.setItem(ANM_SPAETER, today()); }catch(e){}
  kopfZurueck();
  homeMode = 'words';
  showHome();
});
$('anmMail').addEventListener('click', ()=> anmeldungZeigen(anmAnlass, 'mail_an'));
$('anmOffline').addEventListener('click', ()=>{
  netzWeg = true;
  kopfZurueck();
  homeMode = 'words';
  showHome();
});

/* ---- Kontoseite, Abmelden, Konto loeschen ---- */
/* Den Lernstand auf diesem Geraet auf den Anfang setzen - nach dem
   Abmelden und nach dem Loeschen des Kontos. Ajdins Antwort auf die Fragen
   1 und 2 im Plan stand aus; gebaut nach dem Vorschlag "wie bei Duolingo":
   nach dem Abmelden liegt der Stand im Konto, nach dem Loeschen landete
   der alte sonst im naechsten Konto. Sprache, Toene, Erinnerungen,
   Einwilligung, Vollversion, Nutzungsbedingungen und die Zufallskennung
   bleiben. 28.10.2026
   Die Erinnerungen seit dem 14.11.2026 nur noch nach dem Abmelden: nach
   dem Loeschen schaltet benAllesAus() sie ab (Pruefbericht 1.4, V6). */
function standLeeren(){
  standErsetzen(() => ({}));
  setzeGetragen([]);
  try{ localStorage.removeItem(SEIT_SCHLUESSEL); }catch(e){}
  syncLives();
  saveProgress();
  renderLives();
}
function kontoSeiteCloud(){
  const m = cloudMerker() || {};
  $('setProfilMail').innerHTML = m.email ? mitSymbol('brief', esc(m.email)) : '';
  $('setProfilSub').hidden = true;
  const g = $('setGesichert');
  g.hidden = false;
  g.textContent = m.gesichert ? t('set.gesichert', {datum: new Date(m.gesichert + 'T12:00:00').toLocaleDateString(SPRACHE)})
                              : t('set.gesichert_nie');
  $('setPwZeile').hidden = true; $('pwForm').style.display = 'none';
  $('setWegSub').textContent = t('set.konto_weg_sub');
  $('wegForm').style.display = 'none';
  $('setLogoutNote').textContent = ''; $('setLogoutNote').className = 'note';
}
async function cloudAbmeldenGanz(){
  const note = $('setLogoutNote');
  note.className = 'note'; note.textContent = '';
  if(navigator.onLine === false){ note.textContent = t('set.abmelden_netz'); note.className = 'note feedback no'; return; }
  if(!await frage(t('set.abmelden'), t('set.abmelden_frage'), t('set.abmelden'), t('btn.dialog_abbrechen'))) return;
  note.textContent = t('konto.laeuft');
  await saveProgress();
  // Laeuft gerade ein Abgleich (etwa vom Start), auf ihn warten.
  for(let i = 0; cloudLaeuft && i < 60; i++) await new Promise(f => setTimeout(f, 500));
  cloudFehlerGrund = '';
  const r = await cloudAbgleich('abmelden');
  /* Hat Firebase die Anmeldung eben selbst fuer ungueltig erklaert
     (cloudVonAussenAbgemeldet), ist der Merker schon weg und abgemeldet
     ist man schon. Hochladen ging dann nicht mehr, der Lernstand auf dem
     Geraet ist die einzige aktuelle Kopie. Er bleibt stehen, und die
     naechste Anmeldung fuehrt ihn mit dem Konto zusammen - wie beim Start.
     Gegenpruefung 28.10.2026: bis dahin leerte abmeldenFertig() ihn hier,
     und alles seit dem letzten Hochladen war weg. */
  if(!cloudMerker()){ note.textContent = ''; anmeldungZeigen('abgemeldet'); return; }
  /* "Brauchst du Internet" nur, wenn es am Netz lag - nicht, wenn Firebase
     ablehnt, etwa mit 429, weil das Tageskontingent aufgebraucht ist
     (Gegenpruefung 28.10.2026). */
  if(r !== 'gespeichert' && r !== 'unveraendert'){
    note.textContent = t(cloudFehlerGrund === 'netz' ? 'set.abmelden_netz' : 'konto.fehler_allgemein');
    note.className = 'note feedback no';
    return;
  }
  note.textContent = '';
  cloudAbmelden();
  await abmeldenFertig();
  anmeldungZeigen('abgemeldet');
}
async function abmeldenFertig(){
  cloudNativToken = null; restoreUid = '';
  try{ localStorage.setItem(ABGEMELDET, '1'); }catch(e){}
  await anmAufruf('abmelden', {}, 8000);
  standLeeren();
}
async function kontoWegKlick(){
  const m = cloudMerker();
  if(!m) return;
  $('wegNote').textContent = ''; $('wegNote').className = 'note';
  if(m.art === 'passwort'){
    const f = $('wegForm'), auf = f.style.display === 'none';
    f.style.display = auf ? 'block' : 'none';
    $('wegPw').value = '';
    if(auf) $('wegPw').focus();
    return;
  }
  await cloudKontoLoeschen('');
}
async function cloudKontoLoeschen(passwort){
  const m = cloudMerker(), note = $('wegNote');
  if(!m || anmeldungLaeuft) return;
  /* konto.fehler_alt, nicht konto.fehler_mail_pw: das verweist auf "Mit
     Google anmelden", und den Knopf gibt es hier nicht (Gegenpruefung
     28.10.2026). Ebenso unten bei einem falschen Passwort. */
  if(m.art === 'passwort' && !passwort){ note.textContent = t('konto.fehler_alt'); note.className = 'note feedback no'; return; }
  const frageText = t('set.konto_weg_frage') + (m.art === 'google' ? ' ' + t('set.konto_weg_google')
                                               : m.art === 'apple' ? ' ' + t('set.konto_weg_apple') : '');
  if(!await frage(t('set.konto_loeschen'), frageText, t('set.konto_loeschen_knopf'), t('btn.dialog_abbrechen'))) return;
  anmeldungLaeuft = true;
  note.className = 'note'; note.textContent = t('konto.laeuft');
  let r;
  /* Laeuft gerade ein Abgleich, auf ihn warten wie beim Abmelden - seit
     17.11.2026 sieht die App bei jeder Rueckkehr nach, und cloudLoeschen()
     gaebe sonst "Hat nicht geklappt". */
  for(let i = 0; cloudLaeuft && i < 60; i++) await new Promise(f => setTimeout(f, 500));
  try{ r = await cloudLoeschen(cloudAdapter(), {passwort}); }
  finally{ anmeldungLaeuft = false; }
  if(r === false){
    /* 28.10.2026: Googles Auswahl abgebrochen - nichts ist geloescht, und
       zu sagen gibt es auch nichts (wie beim Anmelden). */
    const g = cloudFehlerGrund;
    note.textContent = (g === 'GOOGLE_ABGEBROCHEN' || g === 'APPLE_ABGEBROCHEN') ? ''
      : /^APPLE_(FEHLER|ANDERES_KONTO)/.test(g) ? t('konto.fehler_apple')
      : /^(INVALID_LOGIN_CREDENTIALS|EMAIL_NOT_FOUND|INVALID_PASSWORD|MISSING_PASSWORD)/.test(g)
      ? t('konto.fehler_alt') : t(g === 'netz' ? 'konto.fehler_netz' : 'konto.fehler_allgemein');
    note.className = note.textContent ? 'note feedback no' : 'note';
    return;
  }
  note.textContent = '';
  $('wegPw').value = ''; $('wegForm').style.display = 'none';
  await abmeldenFertig();
  await benAllesAus();     // keine Nachrichten mehr fuer ein geloeschtes Konto (V6, 14.11.2026)
  anmeldungZeigen('abgemeldet', 'wahl', {hinweis: ''});
  const n = $('anmNote');
  n.textContent = t(r === true ? 'set.konto_weg_fertig' : 'set.konto_weg_teil');
  n.className = r === true ? 'note feedback ok' : 'note feedback no';
}

/* Nur mit CLOUD_AN haengt sich die Cloud ueberhaupt irgendwo ein. Der
   Start steht in init(). saveProgress() hat beim Verstecken schon lokal
   gespeichert (Horcher weiter oben), dieser Horcher kommt danach.
   28.10.2026: Beim Zurueckkommen und wenn das Netz wiederkommt, wird das
   Tor neu geprueft; ohne Netz zeigt die Anmeldeseite "Erst einmal
   weiterlernen".
   17.11.2026: Beim Zurueckkommen sieht die App ausserdem in der Cloud nach
   und holt ein verlorenes Schreiben nach ('vorn', siehe cloudAbgleich). */
if(CLOUD_AN){
  document.addEventListener('visibilitychange', ()=>{
    if(!skripteDa) return;   // Start noch nicht fertig, siehe skripteDa
    if(document.hidden){ cloudAbgleich('pause'); return; }
    torPruefen();
    cloudAbgleich('vorn');
  });
  window.addEventListener('online', ()=>{ netzWeg = false; if(skripteDa) torPruefen(); });
  window.addEventListener('offline', ()=>{
    if(!skripteDa) return;   // Start noch nicht fertig, siehe skripteDa
    if(cloudModus() && sichtbar('profileView') && !cloudMerker()) $('anmOffline').hidden = false;
  });
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
