/* ---- Die Huelle: Plugin ZmajAnmeldung ----
   Google (Credential Manager), die Kopie der Sitzung und die
   Restore-Schluessel fuer den Handywechsel, siehe ZmajAnmeldung.java in
   der Huelle. Gerufen wird es nur im Cloud-Modus. Jede Frage hat eine
   Frist: eine haengende Antwort darf den Start nicht aufhalten. */
const anmPlugin = () => (window.Capacitor && window.Capacitor.Plugins
                         && window.Capacitor.Plugins.ZmajAnmeldung) || null;
async function anmAufruf(name, daten, ms){
  const P = anmPlugin();
  if(!P || typeof P[name] !== 'function') return null;
  let uhr = 0;
  try{
    return await Promise.race([P[name](daten || {}),
      new Promise(fertig => { uhr = setTimeout(() => fertig(null), ms || 5000); })]);
  }catch(e){ return null; }
  finally{ clearTimeout(uhr); }
}
let cloudNativToken = null;   // was zuletzt als Kopie in der Huelle steht
function cloudNativMerken(m){
  if(!m || !m.uid || !m.token || m.token === cloudNativToken || !anmPlugin()) return;
  cloudNativToken = m.token;
  anmAufruf('sitzungMerken', {art: m.art || '', uid: m.uid, token: m.token, email: m.email || ''});
}
/* Die uid aus einem Restore-Schluessel des alten Handys - nur auf einem
   neuen Geraet, und nur solange niemand angemeldet ist. */
let restoreUid = '';
/* Beim Start, nach loadProgress(): Merker und Kopie in der Huelle
   abgleichen und einmal nach einem Restore-Schluessel fragen.
   Kein Merker, aber eine Kopie: das ist der Handywechsel, bei dem Android
   die Daten der WebView nicht mitgebracht hat - angemeldet ist man
   trotzdem, und der Lernstand kommt beim Abgleich aus der Cloud. Ein
   Merker ohne Kopie stammt von vor der Kopie und zieht um. */
async function cloudSitzungAbgleichen(){
  if(!cloudModus() || !anmPlugin()) return;
  const k = await anmAufruf('sitzungHolen', {}, 3000);
  const kopie = k && typeof k.uid === 'string' && k.uid && typeof k.token === 'string' && k.token ? k : null;
  const m = cloudMerker();
  if(!m && kopie){
    cloudNativToken = kopie.token;
    cloudMerkerSetzen({art: kopie.art || 'google', uid: kopie.uid, token: kopie.token,
                       email: typeof kopie.email === 'string' ? kopie.email : ''});
    try{ localStorage.removeItem(ABGEMELDET); }catch(e){}
  }else if(m){
    if(kopie && kopie.uid === m.uid && kopie.token === m.token) cloudNativToken = m.token;
    else cloudNativMerken(m);
  }
  /* Nur beim ersten Start nach einer Installation fragt das Plugin wirklich
     (das zaehlt Google), danach gibt es die gemerkte Antwort. */
  const r = await anmAufruf('restoreHolen', {}, 4000);
  const jetzt = cloudMerker();
  restoreUid = (!jetzt && r && typeof r.uid === 'string' && r.uid) ? r.uid : '';
  if(jetzt) anmAufruf('restoreSichern', {uid: jetzt.uid}, 20000);   // ohne Warten
  if(IST_IOS) anbieterFragen();
}
/* Welche Anmeldewege die iOS-Huelle kann (30.10.2026). ZmajAnmeldung.anbieter()
   antwortet {google, apple}: google nur, wenn in der Huelle eine
   iOS-Client-ID steht (GIDClientID aus ios_zugang.xcconfig), apple, wenn
   "Mit Apple anmelden" auf dem Geraet geht. Ohne Antwort (aeltere Huelle,
   Frist verstrichen) entscheidet, ob es die Methoden gibt. Danach werden
   die Knoepfe neu gestellt, falls die Anmeldeseite schon steht. */
let anmAnbieter = null;
async function anbieterFragen(){
  const r = await anmAufruf('anbieter', {}, 3000);
  if(r && typeof r === 'object') anmAnbieter = {google: r.google !== false, apple: r.apple !== false};
  if(sichtbar('profileView') && !$('anmWahl').hidden) anmKnoepfeStellen();
}
/* Firebase sagt, die Anmeldung gilt nicht mehr (Konto geloescht oder
   gesperrt, Passwort anderswo geaendert). Merker, Kopie und
   Restore-Schluessel weg; der Lernstand auf dem Geraet bleibt. Die
   Anmeldung kommt gleich auf der Startseite, sonst beim naechsten Wechsel
   der Ansicht - mitten in einer Lektion nie. */
function cloudVonAussenAbgemeldet(uid){
  const m = cloudMerker();
  if(!m || m.uid !== uid) return;
  cloudAbmelden();
  cloudNativToken = null; restoreUid = '';
  try{ localStorage.setItem(ABGEMELDET, '1'); }catch(e){}
  anmAufruf('abmelden', {}, 8000);
  /* Der Profilknopf bleibt seit 14.11.2026 stehen: die Erfolge gibt es
     auch ohne Konto (siehe nachAnmeldung). Ist das Profil gerade offen,
     verschwindet dort der Kasten mit dem Konto. */
  if(sichtbar('kontoView')) $('kontoKasten').hidden = true;
  torPruefen();
}
/* Googles ID-Token aus der Huelle. Google sperrt die Anmeldung in einer
   WebView; das Plugin ZmajAnmeldung fragt nativ ueber den Credential
   Manager. Wirft mit grund GOOGLE_ABGEBROCHEN, GOOGLE_KEIN_KONTO (kein
   Google-Konto auf dem Handy) oder GOOGLE_FEHLER. */
const googleMoeglich = () => !!anmPlugin() && typeof anmPlugin().googleAusweis === 'function'
  && /^[0-9]{6,20}-[0-9a-z]{16,40}\.apps\.googleusercontent\.com$/.test(CLOUD_CLIENT)
  && !(IST_IOS && anmAnbieter && !anmAnbieter.google);
/* "Mit Apple anmelden" nur auf iPhone und iPad (Entscheidung 6b, 30.10.2026). */
const appleMoeglich = () => IST_IOS && !!anmPlugin() && typeof anmPlugin().appleAusweis === 'function'
  && !(anmAnbieter && !anmAnbieter.apple);
/* Apples Ausweis aus der Huelle: ZmajAnmeldung.appleAusweis() zeigt Apples
   Fenster (ASAuthorizationAppleIDProvider) und antwortet {idToken, nonce,
   code}. nonce ist der ROHE Zufallswert, dessen SHA-256 die Huelle Apple
   mitgegeben hat - Firebase prueft damit das Token (signInWithIdp, nonce).
   code ist Apples authorizationCode, fuenf Minuten gueltig; mit ihm
   widerruft die App beim Loeschen des Kontos Apples Token (accounts:
   revokeToken), wie Apple es verlangt. Wirft mit grund APPLE_ABGEBROCHEN
   oder APPLE_FEHLER. */
async function cloudAppleAusweis(){
  const P = anmPlugin();
  const fehler = grund => { const f = new Error('apple'); f.grund = grund; return f; };
  if(!P || !P.appleAusweis) throw fehler('APPLE_FEHLER');
  let r;
  try{ r = await P.appleAusweis({}); }
  catch(e){
    const c = String((e && (e.code || e.message)) || '');
    throw fehler(c === 'abgebrochen' ? 'APPLE_ABGEBROCHEN' : 'APPLE_FEHLER');
  }
  if(!r || typeof r.idToken !== 'string' || !r.idToken) throw fehler('APPLE_FEHLER');
  return {idToken: r.idToken, nonce: typeof r.nonce === 'string' ? r.nonce : '',
          code: typeof r.code === 'string' ? r.code : ''};
}
async function cloudGoogleAusweis(){
  const P = anmPlugin();
  const fehler = grund => { const f = new Error('google'); f.grund = grund; return f; };
  if(!P || !P.googleAusweis) throw fehler('GOOGLE_FEHLER');
  let r;
  try{ r = await P.googleAusweis({client: CLOUD_CLIENT}); }
  catch(e){
    const c = String((e && (e.code || e.message)) || '');
    throw fehler(c === 'abgebrochen' ? 'GOOGLE_ABGEBROCHEN' : c === 'kein_konto' ? 'GOOGLE_KEIN_KONTO' : 'GOOGLE_FEHLER');
  }
  if(!r || typeof r.idToken !== 'string' || !r.idToken) throw fehler('GOOGLE_FEHLER');
  return r.idToken;
}
/* ---- Adapter: Firebase Auth und Cloud Firestore ueber REST ----
   Ohne Firebase-Bibliothek, nur fetch an vier Adressen. Mit Google wird
   das ID-Token aus cloudGoogleAusweis() bei Firebase eingetauscht
   (accounts:signInWithIdp), mit E-Mail und Passwort meldet
   accounts:signInWithPassword an und accounts:signUp legt das Konto an
   (28.10.2026, statt des Firebase-JS-SDK: kein Fremdcode, dieselbe
   Sitzung im selben Merker, siehe Plan 2.2). Anonym (signUp ohne Adresse)
   bleibt fuer die Tests, angeboten wird es nicht.
   Der Ausweis fuer Firestore (ID-Token, eine Stunde gueltig) bleibt nur im
   Arbeitsspeicher; neu geholt wird er mit dem token aus dem Merker
   (securetoken). In users/{uid} stehen zwei Textfelder: daten und rev. */
function cloudFirestore(projekt, schluessel){
  const KONTO = 'https://identitytoolkit.googleapis.com/v1/accounts:';
  const ERNEUERN = 'https://securetoken.googleapis.com/v1/token?key=';
  const DOKUMENTE = 'https://firestore.googleapis.com/v1/projects/' + encodeURIComponent(projekt)
    + '/databases/(default)/documents';
  const dokument = uid => DOKUMENTE + '/users/' + encodeURIComponent(uid);
  const post = (daten, kopf) => ({method: 'POST', headers: Object.assign({'Content-Type': 'application/json'}, kopf || {}),
                                  body: JSON.stringify(daten)});
  /* Die Mails von Firebase (Bestaetigen, Passwort zuruecksetzen) in der
     Sprache der App. Norwegisch heisst bei Firebase "no". */
  const sprachKopf = () => ({'X-Firebase-Locale': SPRACHE === 'nb' ? 'no' : SPRACHE});
  let ausweis = null;   // {uid, id, bis}
  const merken = (uid, id, sekunden) => { ausweis = {uid, id, bis: Date.now() + (Number(sekunden) || 3600) * 1000}; };
  /* Nach 20 Sekunden ohne Antwort gilt es als gescheitert - sonst hielte
     ein haengendes Netz cloudLaeuft fuer immer fest. fehltOk: 404 heisst
     beim Dokument "noch nichts gesichert" und ist kein Fehler.
     19.10.2026: Der Fehler traegt Firebases Grund (error.message, etwa
     CREDENTIAL_TOO_OLD_LOGIN_AGAIN) - loeschen() braucht ihn.
     28.10.2026: Kein Netz oder keine Antwort traegt netz - die Anmeldung
     sagt dann "Keine Verbindung" statt "hat nicht geklappt".
     17.11.2026: Dazu status, die HTTP-Antwort - kennung() erkennt daran,
     ob Firestore die Feldmaske wirklich ablehnt (400). */
  async function senden(url, optionen, fehltOk){
    const ab = new AbortController(), uhr = setTimeout(() => ab.abort(), 20000);
    try{
      let r;
      try{ r = await fetch(url, Object.assign({cache: 'no-store', signal: ab.signal}, optionen)); }
      catch(e){ const f = new Error('cloud netz'); f.netz = true; throw f; }
      if(r.status === 404 && fehltOk) return null;
      if(!r.ok){
        const f = new Error('cloud ' + r.status);
        f.status = r.status;
        try{ const d = await r.json(); f.grund = String((d && d.error && d.error.message) || ''); }catch(e){}
        throw f;
      }
      return r;
    }finally{ clearTimeout(uhr); }
  }
  async function idToken(m){
    if(ausweis && ausweis.uid === m.uid && ausweis.bis > Date.now() + 60000) return ausweis.id;
    let r;
    try{
      r = await senden(ERNEUERN + schluessel, {method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'grant_type=refresh_token&refresh_token=' + encodeURIComponent(m.token || '')});
    }catch(e){
      /* 28.10.2026: Nur diese Gruende heissen "die Anmeldung ist weg". Bei
         Netzfehlern, Zeitueberschreitung oder 5xx bleibt man angemeldet. */
      if(/^(TOKEN_EXPIRED|INVALID_REFRESH_TOKEN|USER_NOT_FOUND|USER_DISABLED)/.test((e && e.grund) || '')) e.abgemeldet = true;
      throw e;
    }
    const d = await r.json();
    if(!d || !d.id_token || d.user_id !== m.uid) throw new Error('cloud anmeldung');
    if(d.refresh_token) m.token = d.refresh_token;
    merken(m.uid, d.id_token, d.expires_in);
    return ausweis.id;
  }
  const mitAusweis = async m => ({Authorization: 'Bearer ' + await idToken(m)});
  /* Googles Ausweis aus der Huelle bei Firebase eintauschen - beim Anmelden
     und noch einmal vor dem Loeschen des Kontos. */
  async function mitGoogle(){
    const google = await cloudGoogleAusweis();
    return (await senden(KONTO + 'signInWithIdp?key=' + schluessel, post({
      postBody: 'id_token=' + encodeURIComponent(google) + '&providerId=google.com',
      requestUri: 'http://localhost', returnIdpCredential: true, returnSecureToken: true}))).json();
  }
  /* Apples Ausweis eintauschen (iOS, 30.10.2026) - wie mitGoogle, dazu der
     rohe nonce. Gibt {d, code} zurueck: code braucht loeschen() fuer den
     Widerruf. */
  async function mitApple(){
    const a = await cloudAppleAusweis();
    const d = await (await senden(KONTO + 'signInWithIdp?key=' + schluessel, post({
      postBody: 'id_token=' + encodeURIComponent(a.idToken) + '&providerId=apple.com'
        + (a.nonce ? '&nonce=' + encodeURIComponent(a.nonce) : ''),
      requestUri: 'http://localhost', returnIdpCredential: true, returnSecureToken: true}))).json();
    return {d, code: a.code};
  }
  /* Apples Token widerrufen, bevor das Konto geht (30.10.2026). Apple
     verlangt das fuer Konten mit "Mit Apple anmelden"; Firebase reicht den
     authorizationCode an Apple weiter (Identity Platform REST v2,
     accounts:revokeToken, tokenType CODE - derselbe Weg wie
     Auth.revokeToken(withAuthorizationCode:) im iOS-SDK). Ohne Netz wirft
     es, und es ist noch nichts geloescht. Lehnt Firebase ab (etwa weil der
     Apple-Schluessel in der Konsole fehlt), geht das Loeschen trotzdem
     weiter: sonst koennte so jemand sein Konto nie loeschen. */
  async function appleWiderrufen(id, code){
    if(!code) return;
    try{
      await senden('https://identitytoolkit.googleapis.com/v2/accounts:revokeToken?key=' + schluessel,
        post({idToken: id, providerId: 'apple.com', tokenType: 'CODE', token: code}));
    }catch(e){ if(e && e.netz) throw e; }
  }
  /* E-Mail und Passwort - beim Anmelden und vor dem Loeschen des Kontos.
     Mit dem Schutz vor E-Mail-Aufzaehlung (bei neuen Projekten an) meldet
     Firebase fuer unbekannte Adresse und falsches Passwort dasselbe:
     INVALID_LOGIN_CREDENTIALS. */
  async function mitPasswort(email, pw){
    return (await senden(KONTO + 'signInWithPassword?key=' + schluessel,
      post({email: String(email || ''), password: String(pw || ''), returnSecureToken: true}))).json();
  }
  /* Das Konto selbst: true geloescht oder schon weg, 'alt' verlangt eine
     frische Anmeldung, false sonst gescheitert. */
  async function kontoWeg(id){
    try{ await senden(KONTO + 'delete?key=' + schluessel, post({idToken: id})); return true; }
    catch(e){
      const g = (e && e.grund) || '';
      if(/^USER_NOT_FOUND/.test(g)) return true;
      return /^(CREDENTIAL_TOO_OLD_LOGIN_AGAIN|INVALID_ID_TOKEN)/.test(g) ? 'alt' : false;
    }
  }
  const konto = (d, email) => {
    if(!d || typeof d.localId !== 'string' || !d.idToken) return null;
    merken(d.localId, d.idToken, d.expiresIn);
    return {uid: d.localId, token: d.refreshToken || '', email: String(d.email || email || ''), idToken: d.idToken};
  };
  return {
    async anmelden(art, daten){
      let d = null;
      if(art === 'anonym'){
        d = await (await senden(KONTO + 'signUp?key=' + schluessel, post({returnSecureToken: true}))).json();
      }else if(art === 'google'){
        d = await mitGoogle();
      }else if(art === 'apple'){
        d = (await mitApple()).d;
      }else if(art === 'passwort'){
        d = await mitPasswort((daten || {}).email, (daten || {}).pw);
      }
      return konto(d, art === 'passwort' ? (daten || {}).email : '');
    },
    async registrieren(email, pw){
      return konto(await (await senden(KONTO + 'signUp?key=' + schluessel,
        post({email: String(email || ''), password: String(pw || ''), returnSecureToken: true}))).json(), email);
    },
    /* Firebase sagt nie, ob es die Adresse gibt - die Meldung in der App
       auch nicht (konto.vergessen_raus). */
    async passwortVergessen(email){
      await senden(KONTO + 'sendOobCode?key=' + schluessel,
        post({requestType: 'PASSWORD_RESET', email: String(email || '')}, sprachKopf()));
      return true;
    },
    async bestaetigungSchicken(id){
      await senden(KONTO + 'sendOobCode?key=' + schluessel, post({requestType: 'VERIFY_EMAIL', idToken: id}, sprachKopf()));
      return true;
    },
    async laden(m){
      const r = await senden(dokument(m.uid), {headers: await mitAusweis(m)}, true);
      if(!r) return null;
      const f = (await r.json()).fields || {};
      return {text: (f.daten && f.daten.stringValue) || '', rev: (f.rev && f.rev.stringValue) || ''};
    },
    /* Nur rev, fuer "erst nachsehen" (13.11.2026): Firestore schickt mit
       der Feldmaske (DocumentMask, mask.fieldPaths) nur dieses Feld. Es ist
       ein gewoehnliches get, die Regel "allow get" gilt unveraendert, und es
       zaehlt als ein Lesevorgang. null: es gibt noch kein Dokument.
       17.11.2026 (Pruefbefund): Ein Fehler traegt maske nur, wenn Firestore
       die Feldmaske selbst abweist (400) - nicht bei 5xx, 429 oder wenn
       schon der Ausweis (securetoken) scheitert; der traegt ausweis. Vorher
       galt jeder Fehler als abgelehnte Maske, und ein einziger 503 schaltete
       das Nachsehen bis zum naechsten Start ab. */
    async kennung(m){
      let kopf;
      try{ kopf = await mitAusweis(m); }
      catch(e){ if(e && typeof e === 'object') e.ausweis = true; throw e; }
      let r;
      try{ r = await senden(dokument(m.uid) + '?mask.fieldPaths=rev', {headers: kopf}, true); }
      catch(e){ if(e && typeof e === 'object' && e.status === 400) e.maske = true; throw e; }
      if(!r) return null;
      const f = (await r.json()).fields || {};
      return (f.rev && f.rev.stringValue) || '';
    },
    /* 20.11.2026 (Optimierung Punkt 4): Ohne Maske schickt Firestore auf
       das PATCH das ganze Dokument zurueck - beim Vollstand rund 0,9 MB,
       die niemand liest, die aber Datenvolumen und das Ausgangs-Kontingent
       verbrauchen. mask.fieldPaths=rev ist die Antwortmaske (laut Doku die
       Felder, die zurueckkommen): zurueck kommt nur rev. NICHT updateMask.fieldPaths - das
       hiesse "nur rev schreiben", daten bliebe alt, und die Sicherung waere
       still veraltet. Geschrieben wird weiter das ganze Dokument. */
    async speichern(m, dok){
      await senden(dokument(m.uid) + '?mask.fieldPaths=rev', {method: 'PATCH',
        headers: Object.assign({'Content-Type': 'application/json'}, await mitAusweis(m)),
        body: JSON.stringify({fields: {daten: {stringValue: dok.text}, rev: {stringValue: dok.rev}}})});
      return true;
    },
    /* 19.10.2026: Zuerst die Sicherung - scheitert das, wirft es, und es
       ist nichts passiert. Danach das Konto. Firebase loescht es nur nach
       einer frischen Anmeldung (CREDENTIAL_TOO_OLD_LOGIN_AGAIN); der Ausweis
       aus dem Erneuerungsschluessel zaehlt nicht.
       28.10.2026: Deshalb meldet die App sich ZUERST frisch an - bei
       E-Mail-Konten mit dem Passwort, bei Google ueber Googles
       Kontoauswahl, und nur dasselbe Konto (uid) gilt. Falsches Passwort,
       abgebrochene Auswahl, ein anderes Google-Konto oder kein Netz: dann
       ist noch nichts geloescht. Bis zum Pruefbericht vom 28.10. fragte
       Google erst NACH dem Loeschen der Sicherung - wer dort abbrach, hatte
       keinen Lernstand mehr, aber noch ein Konto. Anonym gibt es keine neue
       Anmeldung - dort bleibt eine leere Kennung. Gibt zurueck, ob auch das
       Konto weg ist; die Sicherung ist es dann in jedem Fall. */
    async loeschen(m, optionen){
      let id;
      /* "Mit Apple anmelden" (30.10.2026): frisch bei Apple anmelden, dasselbe
         Konto pruefen, Apples Token widerrufen - erst dann wird geloescht. */
      if(m.art === 'apple'){
        const {d, code} = await mitApple();
        if(!d || d.localId !== m.uid || !d.idToken){
          const f = new Error('cloud anderes konto'); f.grund = 'APPLE_ANDERES_KONTO'; throw f;
        }
        id = d.idToken;
        await appleWiderrufen(id, code);
      }else if(m.art === 'passwort' || m.art === 'google'){
        const d = m.art === 'google' ? await mitGoogle()
          : await mitPasswort(m.email, (optionen || {}).passwort);
        if(!d || d.localId !== m.uid || !d.idToken){
          const f = new Error('cloud anderes konto');
          f.grund = m.art === 'google' ? 'GOOGLE_ANDERES_KONTO' : 'INVALID_LOGIN_CREDENTIALS';
          throw f;
        }
        id = d.idToken;
      }else{
        id = await idToken(m);
      }
      await senden(dokument(m.uid), {method: 'DELETE', headers: {Authorization: 'Bearer ' + id}}, true);
      ausweis = null;
      return await kontoWeg(id) === true;
    },
    /* Feedback aus den Einstellungen (01.11.2026), genau wie das
       Kontaktformular der Webseite (KONTAKT_SKRIPT in seite_bauen.py):
       kurz anonym anmelden, die Nachricht als nachrichten/{uid} anlegen
       (dieselben Felder, zeit vom Server, exists: false - nur Anlegen),
       die anonyme Anmeldung wieder loeschen, auch wenn das Anlegen
       scheiterte. Als das angemeldete Konto ginge es mit den Regeln vom
       31.10.2026 nicht: firestore.rules laesst in nachrichten/{uid} nur
       anonyme Anmeldungen anlegen (istAbsender), und je uid nur einmal.
       Der Ausweis des Kontos (ausweis) bleibt dabei unberuehrt - deshalb
       nicht ueber konto(), das ihn ueberschriebe. Wirft bei Fehlern. */
    async nachricht(text, antwort, sprache){
      const d = await (await senden(KONTO + 'signUp?key=' + schluessel, post({returnSecureToken: true}))).json();
      if(!d || typeof d.localId !== 'string' || !d.localId || !d.idToken) throw new Error('cloud anmeldung');
      try{
        await senden(DOKUMENTE + ':commit', post({writes: [{
          update: {name: 'projects/' + projekt + '/databases/(default)/documents/nachrichten/' + d.localId,
                   fields: {text: {stringValue: text}, antwort: {stringValue: antwort},
                            sprache: {stringValue: sprache}}},
          updateTransforms: [{fieldPath: 'zeit', setToServerValue: 'REQUEST_TIME'}],
          currentDocument: {exists: false}}]}, {Authorization: 'Bearer ' + d.idToken}));
      }finally{
        await kontoWeg(d.idToken);   // wirft nie; bleibt sie liegen, darf sie nichts mehr
      }
      return true;
    },
  };
}
/* ---- Adapter fuer die Tests ----
   Haelt den Cloud-Stand in einem gewoehnlichen Objekt (ablage) statt bei
   einem Anbieter und zaehlt, wie oft wirklich gelesen und geschrieben
   wurde. ablage.offline = true laesst jede Anfrage scheitern wie ohne
   Netz. Nur tests_e2e/test_cloud.py reicht ihn herein; cloudAdapter()
   waehlt ihn nie. */
function cloudSpeicherAdapter(ablage){
  ablage.zaehler = ablage.zaehler || {anmelden: 0, laden: 0, speichern: 0, loeschen: 0};
  const netz = was => {
    if(ablage.offline){ const f = new Error('offline'); f.netz = true; throw f; }
    ablage.zaehler[was] = (ablage.zaehler[was] || 0) + 1;
  };
  return {
    async anmelden(art, daten){
      netz('anmelden');
      return {uid: ablage.uid || 'probe-' + art, token: 'probe', email: (daten && daten.email) || ''};
    },
    async registrieren(email){ netz('registrieren'); return {uid: ablage.uid || 'probe-neu', token: 'probe', email, idToken: 'probe-id'}; },
    async passwortVergessen(){ netz('vergessen'); return true; },
    async bestaetigungSchicken(){ netz('bestaetigen'); return true; },
    async laden(){ netz('laden'); return ablage.dok ? {text: ablage.dok.text, rev: ablage.dok.rev} : null; },
    async speichern(m, dok){ netz('speichern'); ablage.dok = {text: dok.text, rev: dok.rev}; return true; },
    async loeschen(){ netz('loeschen'); ablage.dok = null; return true; },
    /* "Erst nachsehen" wie Firestore (13.11.2026), aber nur mit
       ablage.mitKennung - ohne laedt er alles wie vorher, und die
       Zaehler der Tests vom 19.10. stimmen weiter. */
    ...(ablage.mitKennung ? {async kennung(){ netz('kennung'); return ablage.dok ? ablage.dok.rev : null; }} : {}),
  };
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
