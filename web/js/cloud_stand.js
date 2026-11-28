/* =================== CLOUD-SICHERUNG UND ANMELDUNG ===================
   19.10.2026 vorbereitet, seit 28.10.2026 (v109) die Pflicht-Anmeldung.
   Ajdin am 18.10.2026: "dann machen wir firebase". Am 26./27.10.2026: die
   Anmeldung kommt schon in v109 und ist Pflicht, mit Google und mit E-Mail
   und Passwort; neue Nutzer machen erst die 1. Lektion, bestehende melden
   sich beim naechsten Start an; "anmelden soll nur einmal passieren wie
   bei duolingo"; ohne Internet wird trotzdem gelernt. Der Bauplan steht in
   Release\Firebase_Plan_v109.md.

   Eingeschaltet wird nur im Bau: In der Quelle steht CLOUD_AN auf false,
   app_bauen.py (cloud_einsetzen) setzt es in der KOPIE www/index.html auf
   true - und nur, wenn die private Huelle cloud_zugang.json hat. Ohne die
   Datei, in der Browser-Demo, mit start.py und in allen Tests mit der
   Quelle passiert hier NICHTS: keine Anfrage ins Netz, keine Oberflaeche,
   kein Eintrag im Geraetespeicher, kein Aufruf des Plugins. Ohne Adapter
   tut keine Funktion unten etwas, und einen Adapter gibt es nur mit
   CLOUD_AN und eingesetzten Zugangsdaten (cloudAdapter).

   Die Regeln aus der Recherche vom 18.10.2026:
     - Das Geraet bleibt massgeblich, die Cloud ist nur Sicherung. Gelernt
       und gerechnet wird weiter mit dem Geraetespeicher.
     - Hoechstens ein Schreibvorgang je Nutzer und Tag und nur, wenn sich
       etwas geaendert hat (Spark: 20 000 am Tag fuer alle zusammen), dazu
       einer beim Anmelden und einer beim Abmelden. Gelesen wird beim ersten
       Start des Tages und vor jedem Schreiben.
       Seit 17.11.2026 hoechstens zwei am Tag: der beim Verlassen (oder,
       wenn er nicht ankam, beim naechsten Oeffnen nachgeholt) und einer
       gleich nach dem Lernen - und hoechstens CLOUD_SCHREIBVERSUCHE
       Versuche, auch wenn keiner ankommt. Nachgesehen wird bei jedem
       Oeffnen, nur rev, hoechstens alle CLOUD_NACHSEHEN_MS. Siehe
       cloudAbgleich().
     - In der Cloud steht dasselbe JSON wie in der Sicherungsdatei
       (sicherungObjekt), als ein Text in users/{uid}. Keine
       Firebase-Sonderfunktionen: fuer einen anderen Anbieter genuegt ein
       neuer Adapter mit anmelden, registrieren, laden, speichern und
       loeschen (kennung ist freiwillig, 13.11.2026).
       Seit 13.11.2026 (1.4) darf der Stand darin gepackt stehen, siehe
       CLOUD_IMMER_PACKEN; der Text bleibt eine Sicherung.
     - Zusammenfuehren statt ueberschreiben, siehe standZusammenfuehren().
       Zusammengefuehrt wird aber nur, wenn seit dem eigenen letzten
       Abgleich jemand anderes geschrieben hat (rev passt nicht mehr). Sonst
       schreibt das Geraet seinen Stand einfach drueber - sonst kaeme ein
       hier weggenommener Stern oder ein fertig geuebter Fehler aus der
       eigenen alten Sicherung wieder zurueck.
     - Fehler oder kein Netz: still, beim naechsten Anlass noch einmal.
   Angestossen wird der Abgleich beim Start (nur lesen) und wenn die App in
   den Hintergrund geht (schreiben, hoechstens einmal am Tag) - dann ist der
   Stand des Tages am vollstaendigsten. Seit 17.11.2026 auch bei jeder
   Rueckkehr in den Vordergrund und nach dem Lernen, siehe cloudAbgleich(). */
/* CLOUD_AN steht im Bauwerte-Block vor diesem Skript. */
/* Platzhalter wie beim Dauer-Pruefwert: app_bauen.py (cloud_einsetzen)
   setzt beim Bauen die Werte aus der privaten Huelle ein
   (cloud_zugang.json). Im Repository stehen sie nie. CLOUD_CLIENT ist die
   Web-Client-ID fuer die Anmeldung mit Google (28.10.2026). */
/* CLOUD_PROJEKT, CLOUD_SCHLUESSEL und CLOUD_CLIENT stehen im Bauwerte-Block vor diesem Skript. */
/* Was dieses Geraet sich merkt, erst nach dem Anmelden:
     art, uid  das Konto ('google', 'passwort' oder 'anonym')
     token     der Erneuerungsschluessel der Anmeldung - liegt im
               App-Speicher wie der Lernstand selbst, dazu als Kopie in
               der Huelle (ZmajAnmeldung.sitzungMerken), siehe
               cloudSitzungAbgleichen()
     email     die Adresse des Kontos, nur zum Anzeigen und fuer die
               frische Anmeldung vor dem Loeschen - seit 01.11.2026 auch
               als Antwortadresse beim Feedback (feedbackUeberFormular)
     rev       Kennung des Cloud-Stands, den dieses Geraet zuletzt
               geschrieben oder eingearbeitet hat
     fp        Fingerabdruck des zuletzt hochgeladenen Stands
     fremd     die Namen der Felder einer neueren Fassung (standFremd),
               die beim letzten Lesen oder Schreiben in der Cloud standen
               - fuer standZusammenfuehren(), seit 28.10.2026
     tag       Tag des letzten Schreibens beim Verlassen, gelesen der des
               letzten Lesens, gesichert der des letzten Schreibens
               ueberhaupt (fuer "Zuletzt gesichert" in der Kontoseite).
               Seit 17.11.2026 zaehlt das Nachholen beim Oeffnen als das
               Schreiben beim Verlassen (tag), und ende ist der Tag des
               letzten Schreibens gleich nach dem Lernen (cloudNachLernen)
     versuche  {tag, n}: so oft wurde an diesem Tag zu schreiben versucht,
               ob es ankam oder nicht (CLOUD_SCHREIBVERSUCHE, 17.11.2026) */
const CLOUD_MERKER = 'zmaj_cloud';
/* Wer sich abgemeldet hat oder dessen Konto von aussen weg ist, sieht beim
   naechsten Start gleich die Anmeldung - auch mit leerem Lernstand. */
const ABGEMELDET = 'zmaj_abgemeldet';
/* Auch nach Jahren wird ein Stand nicht so gross (alle Woerter, Topf und
   Sterne voll: rund 150 000 Zeichen). Dieselbe Grenze steht in
   firestore.rules.
   28.10.2026: 900 000 statt 400 000. Luft fuer die zeitgesteuerte
   Wiederholung ab v110, die je Wort Daten mitbringt, und fuer Felder
   einer neueren Fassung, die diese hier nur weitertraegt (standFremd).
   Gemessen wird der Text in UTF-8-Bytes (utf8Laenge), nicht in Zeichen:
   Firestore erlaubt 1 MiB (1 048 576 Bytes) je Dokument, und ein 'č' ist
   dort zwei Bytes lang. So bleibt das Dokument mit rev und Feldnamen
   sicher darunter; die Regel zaehlt Zeichen und laesst es damit erst
   recht durch.
   29.10.2026: Die Lernkartei bringt je gewusstem Wort rund 40 Bytes mit
   (Kennung und drei Zahlen, die Tage als Zahl statt als Datum). Ein Stand
   mit allen 1 740 Woertern gewusst, vollem Topf und allen Sternen hat
   damit rund 151 000 Bytes, mit 7 000 Woertern waeren es grob 500 000 -
   gemessen in tests_e2e/test_kartei.py. */
const CLOUD_GROESSE_MAX = 900000;
const utf8Laenge = s => { try{ return new TextEncoder().encode(s).length; }catch(e){ return s.length * 3; } };
/* ---- Packen, Weg A (Ajdin am 13.11.2026: "alles wie empfohlen") ----
   Mit allen 7 998 Eintraegen von 1.3 belegt der Stand 857 000 der 900 000
   Bytes, ab etwa 8 800 Eintraegen passte er nicht mehr
   (Release\Entscheidungen_2026-11-13\cloud.md). Gepackt sind es rund
   195 000, mit 30 000 Eintraegen rund 783 000 (gemessen in
   tests_e2e/test_cloud_packen.py): jedes gewusste Wort steht nur noch
   einmal drin (vorher in gewusst UND in der Kartei, siehe karteiSpalten),
   dann gzip, dann Base64. Es bleibt ein Text in daten - firestore.rules
   bleibt, wie es ist.
   Zwei Schritte:
     1. Ab 1.4 liest die App beide Formen. Sie schreibt weiter die alte,
        solange die unter CLOUD_GROESSE_MAX passt, und packt erst, wenn
        nicht. Ein Geraet mit 1.3 merkt davon nichts.
     2. Ein bis zwei Monate spaeter, wenn kaum noch jemand 1.3 hat:
        CLOUD_IMMER_PACKEN auf true. Das spart Platz und Datenverkehr.
   Auch gepackt ist das Dokument eine gewoehnliche Sicherung,
   {app:'zmaj', version:1, datum, stand:{gepackt1:'<Base64>'}}. Darum
   verliert ein Geraet mit 1.1 bis 1.3 nichts: Es haelt gepackt1 fuer das
   Feld einer neueren Fassung, traegt es unveraendert weiter (standFremd,
   seit 28.10.2026) und schreibt den eigenen Stand daneben. Diese Fassung
   packt das wieder aus und fuehrt beides zusammen (cloudStandLesen). Was
   1.3 dabei genau tut: Release\Entscheidungen_2026-11-13\cloud_handytest.md.
   Wird so ein Geraet mit 1.3 spaeter auf 1.4 aktualisiert, steht gepackt1
   in seinem eigenen Stand. Das packt es vor dem naechsten Schreiben aus und
   arbeitet es ein (gepacktEinarbeiten, Pruefbefund 13.11.2026) - ohne das
   verloere Schritt 2 die Woerter des Geraets, das gepackt1 geschrieben hat.
   Ein Randfall bleibt, und nur 1.3 koennte ihn verhindern: Passen der
   eigene Stand von 1.3 und gepackt1 zusammen nicht unter die Grenze, laesst
   1.3 gepackt1 in der Cloud weg (standFremdAus) und behaelt es nur auf dem
   Geraet. Bis das neuere Geraet wieder abgleicht, steht dessen Stand dann
   nur dort. Mit Schritt 1 kommt das so gut wie nie vor: gepackt wird erst
   ueber der Grenze, und mit dem Wortschatz von 1.4 bleibt auch ein Stand
   mit allem gelernt darunter (857 000; nur tagwerk und tage wachsen noch,
   um einen Eintrag je Lerntag). Vor Schritt 2 und vor B2 darum erst
   nachsehen, wie viele noch 1.3 haben.
   Der Name traegt das Format. Ein spaeteres anderes bekommt einen neuen
   (gepackt2), und diese Fassung traegt es dann genauso weiter wie 1.3
   heute gepackt1. */
/* CLOUD_IMMER_PACKEN steht im Bauwerte-Block vor diesem Skript. */
const CLOUD_PACK_FELD = 'gepackt1';
/* Ausgepackt hoechstens so viel: ein kaputtes oder gefaelschtes Dokument
   fuellt nicht den Arbeitsspeicher. Der volle Stand von 1.3 hat 860 000
   Bytes, einer mit 30 000 Eintraegen gut 3 MB. */
const CLOUD_AUSGEPACKT_MAX = 32 * 1024 * 1024;
/* Firebase verlangt mindestens 6 Zeichen. Ajdin hatte die Frage offen
   gelassen; gebaut nach dem Vorschlag im Plan (Frage 3): nur die Laenge,
   mindestens 8 - einfacher als die 10 Zeichen mit vier Zeichenarten der
   alten Server-Anmeldung. 28.10.2026 */
const PW_MIN_CLOUD = 8;
/* Seit 29.10.2026 mehr als die Laenge. Ajdin nach dem Test der v109 mit
   Anmeldung: "mindestens ein Sonderzeichen, mindestens eine Zahl, Gross-
   und Kleinschreibung und was noch so wichtig ist". Entschieden: 8 Zeichen,
   je ein Gross- und ein Kleinbuchstabe, eine Ziffer, ein Sonderzeichen, und
   der Teil der Adresse vor dem @ (ab 3 Zeichen) darf nicht darin stehen.
   Verbindlich ist Firebase: Ajdin stellt in der Konsole die
   Passwort-Richtlinie auf "Require" (8 Zeichen, alle vier Zeichenarten).
   Deshalb zaehlt die App genau wie Firebases eigene Pruefung
   (validatePassword in firebase-js-sdk, password_policy_impl.ts,
   nachgesehen am 29.10.2026): Gross- und Kleinbuchstaben nur A-Z und a-z,
   Ziffern nur 0-9, die Laenge in UTF-16-Einheiten (p.length). Ein Umlaut,
   +, EUR-Zeichen oder Leerzeichen ist erlaubt, zaehlt aber fuer keine
   Regel - sonst zeigte die Liste einen Haken, und Firebase lehnte trotzdem
   ab (PASSWORD_DOES_NOT_MEET_REQUIREMENTS). "Oelbaum1!" mit einem grossen
   Oe braucht also noch einen Grossbuchstaben A-Z. Damit das niemanden
   ratlos laesst (Ş, Ö, Å, Æ stehen in tr, de, sv, nb und da oft vorn),
   nennen Liste und Fehlersatz den Bereich: "Großbuchstabe (A–Z)",
   konto.regel_gross_az und konto.fehler_gross_az (Pruefung 29.10.2026).
   PW_REGELN der alten Server-Anmeldung zaehlt jeden Buchstaben und
   behaelt deshalb konto.regel_gross.
   Sonderzeichen sind genau die, die Zmajs Firebase-Projekt selbst meldet
   (GET identitytoolkit v2/passwordPolicy, allowedNonAlphanumericCharacters,
   abgefragt am 30.10.2026). Die Anleitung von Firebase nannte - und ` nicht,
   der Server zaehlt beide; "Sommer-2026" bekam deshalb in der App ein rotes
   Sonderzeichen, obwohl Firebase es annimmt. Nie mehr Zeichen als der
   Server: lockerer hiesse ein Haken in der Liste und trotzdem eine Ablehnung.
   Die Regel mit der E-Mail kennt Firebase nicht, sie gilt nur hier.
   Nur fuer ein neues Passwort (Konto anlegen); die Anmeldung mit einem
   bestehenden Passwort prueft nichts davon. */
const PW_ZEICHEN_CLOUD = '^$*.[]{}()?"!@#%&/\\,><\':;|_~`-';
const PW_REGELN_CLOUD = [
  ['passwort_kurz',    'konto.regel_laenge',  p => p.length >= PW_MIN_CLOUD],
  ['passwort_gross',   'konto.regel_gross_az', p => /[A-Z]/.test(p)],
  ['passwort_klein',   'konto.regel_klein_az', p => /[a-z]/.test(p)],
  ['passwort_zahl',    'konto.regel_zahl',    p => /[0-9]/.test(p)],
  ['passwort_zeichen', 'konto.regel_zeichen', p => [...p].some(z => PW_ZEICHEN_CLOUD.includes(z))]
];
/* Steht der Teil der Adresse vor dem @ im Passwort? Gross und klein egal.
   Kuerzer als 3 Zeichen zaehlt er nicht - sonst verboete "ab@..." jedes
   Passwort mit "ab" -, ohne @ (noch beim Tippen) auch nicht. */
function emailVorAt(email){
  const adr = String(email || ''), at = adr.indexOf('@');
  return at < 0 ? '' : adr.slice(0, at).trim().toLowerCase();
}
function pwOhneEmail(pw, email){
  const name = emailVorAt(email);
  return name.length < 3 || !String(pw || '').toLowerCase().includes(name);
}
/* Was einem neuen Passwort noch fehlt: die erste Regel, die nicht erfuellt
   ist (wie PW_REGELN beim Server), zuletzt die E-Mail - sonst ''. */
function pwFehltCloud(pw, email){
  const r = PW_REGELN_CLOUD.find(([, , erfuellt]) => !erfuellt(pw));
  return r ? r[0] : (pwOhneEmail(pw, email) ? '' : 'passwort_email');
}
function pwFehlerCloud(fehlt){
  if(fehlt === 'passwort_kurz') return t('konto.fehler_kurz', {n: PW_MIN_CLOUD});
  if(fehlt === 'passwort_email') return t('konto.fehler_pw_email');
  if(fehlt === 'passwort_gross') return t('konto.fehler_gross_az');   // nur A-Z, siehe oben
  if(fehlt === 'passwort_klein') return t('konto.fehler_klein_az');
  return kontoFehlerText(fehlt);       // Zahl, Sonderzeichen: dieselben Saetze wie beim Server
}
let cloudLaeuft = false;   // immer nur ein Abgleich zur Zeit
let cloudFirestoreAdapter = null;
let cloudFehlerGrund = '';   // der letzte Grund, fuer die Meldung in der Oberflaeche
const cloudEingerichtet = () => /^[a-z][a-z0-9-]{4,28}[a-z0-9]$/.test(CLOUD_PROJEKT)
  && /^AIza[0-9A-Za-z_-]{35}$/.test(CLOUD_SCHLUESSEL) && /^[0-9]{6,20}-[0-9a-z]{16,40}\.apps\.googleusercontent\.com$/.test(CLOUD_CLIENT);
function cloudAdapter(){
  if(!CLOUD_AN || !cloudEingerichtet()) return null;
  if(!cloudFirestoreAdapter) cloudFirestoreAdapter = cloudFirestore(CLOUD_PROJEKT, CLOUD_SCHLUESSEL);
  return cloudFirestoreAdapter;
}
/* Die Anmeldung gilt nur mit Adapter und nicht neben dem alten Server von
   start.py (KONTEN_AN, MIT_SERVER) - dort gibt es dessen eigene. */
const cloudModus = () => !!cloudAdapter() && !MIT_SERVER;
function cloudMerker(){
  try{
    const m = JSON.parse(localStorage.getItem(CLOUD_MERKER) || 'null');
    return (m && typeof m === 'object' && !Array.isArray(m) && typeof m.uid === 'string' && m.uid) ? m : null;
  }catch(e){ return null; }
}
/* nurWennGleich: nur, wenn noch dasselbe Konto angemeldet ist. Wer sich
   waehrend eines Abgleichs abmeldet, waere sonst gleich wieder angemeldet.
   28.10.2026: Hat sich der Erneuerungsschluessel geaendert, bekommt die
   Huelle eine neue Kopie der Sitzung. */
function cloudMerkerSetzen(m, nurWennGleich){
  if(nurWennGleich){ const jetzt = cloudMerker(); if(!jetzt || jetzt.uid !== m.uid) return; }
  try{ localStorage.setItem(CLOUD_MERKER, JSON.stringify(m)); }catch(e){}
  cloudNativMerken(m);
}
/* Ob sich seit dem letzten Hochladen etwas geaendert hat. Ein kurzer
   Fingerabdruck (cyrb53, 64 Bit) statt des ganzen Texts, der sonst ein
   zweites Mal im Geraetespeicher laege. */
function cloudFingerabdruck(stand){
  const s = JSON.stringify(stand);
  let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
  for(let i = 0; i < s.length; i++){
    const c = s.charCodeAt(i);
    h1 = Math.imul(h1 ^ c, 2654435761); h2 = Math.imul(h2 ^ c, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return (h2 >>> 0).toString(16).padStart(8, '0') + (h1 >>> 0).toString(16).padStart(8, '0');
}
/* Die Kennung eines Cloud-Stands. Bis zum 28.10.2026 stand hier
   geraetId() + Zeit - dann laege in der Cloud eine Geraete-ID, und das
   Datensicherheits-Formular muesste sie nennen. Fuer "jemand anderes hat
   geschrieben" genuegt ein Zufallswert je Schreiben. */
function cloudRev(){
  let z = '';
  try{ z = Array.from(crypto.getRandomValues(new Uint32Array(2)), x => x.toString(36)).join(''); }
  catch(e){ z = Math.random().toString(36).slice(2); }
  return z + '.' + Date.now().toString(36);
}
function cloudStandAus(text){
  try{ return typeof text === 'string' ? sicherungStandAus(JSON.parse(text)) : null; }
  catch(e){ return null; }
}
/* ---- Packen und Auspacken (13.11.2026), siehe CLOUD_IMMER_PACKEN ----
   gzip ist im Browser eingebaut (CompressionStream: Android-WebView ab
   Chrome 80, iOS ab 16.4). Ohne bleibt es bei der alten Form, und ein
   gepacktes Dokument traegt das Geraet nur weiter wie 1.3. */
const packenMoeglich = () => typeof CompressionStream === 'function' && typeof DecompressionStream === 'function'
  && typeof Blob === 'function' && typeof Response === 'function'
  && typeof TextEncoder === 'function' && typeof TextDecoder === 'function';
/* Bytes durch einen Strom (packen oder auspacken), hoechstens max heraus. */
async function packStrom(bytes, strom, max){
  const leser = new Blob([bytes]).stream().pipeThrough(strom).getReader();
  const teile = [];
  let n = 0;
  for(;;){
    const {done, value} = await leser.read();
    if(done) break;
    n += value.length;
    if(n > max){ try{ await leser.cancel(); }catch(e){} throw new Error('ausgepackt zu gross'); }
    teile.push(value);
  }
  const aus = new Uint8Array(n);
  let i = 0;
  teile.forEach(t => { aus.set(t, i); i += t.length; });
  return aus;
}
function base64Aus(bytes){
  let s = '';
  for(let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(s);
}
/* Streng: atob nimmt auch Leerzeichen und fehlende Fuellzeichen hin. */
function base64Zurueck(text){
  if(typeof text !== 'string' || !text || text.length % 4 || !/^[A-Za-z0-9+/]+={0,2}$/.test(text)) throw new Error('kein Base64');
  const s = atob(text), b = new Uint8Array(s.length);
  for(let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i);
  return b;
}
/* Jedes Wort nur einmal (Ajdin, 13.11.2026). Ein gewusstes Wort stand
   zweimal im Stand, in gewusst und als Schluessel der Kartei - zusammen
   819 000 der 857 000 Bytes. Gepackt behaelt die Kartei ihre Eintraege
   in Spalten, ohne Kennung:
     i  wie weit der Platz in gewusst hinter dem des vorigen Eintrags liegt
        (stehen beide gleich sortiert, ueberall 1)
     s  die Stufe
     a  Termin minus Uebungstag (meist einer der Abstaende 1 bis 180)
     l  der Uebungstag
   gzip packt Spalten mit aehnlichen Zahlen viel dichter als Paare. Was
   nicht passt - die Kennung steht nicht in gewusst, oder es sind nicht
   genau drei ganze Zahlen -, steht unveraendert in x, mit seinem Platz in
   der Kartei. So kommt alles in derselben Reihenfolge zurueck, und der
   Vergleich vor dem Hochladen (cloudPacken) findet jede Abweichung. */
function karteiSpalten(gewusst, w){
  const platz = new Map();
  gewusst.forEach((id, i) => { if(typeof id === 'string' && !platz.has(id)) platz.set(id, i); });
  const ganz = x => Number.isSafeInteger(x) && Math.abs(x) < 2 ** 40;
  const k = {i: [], s: [], a: [], l: [], x: []};
  let vorher = -1;
  Object.entries(w).forEach(([id, e], n) => {
    const p = platz.get(id);
    if(p !== undefined && Array.isArray(e) && e.length === 3 && ganz(e[0]) && ganz(e[1]) && ganz(e[2])){
      k.i.push(p - vorher); vorher = p;
      k.s.push(e[0]); k.a.push(e[1] - e[2]); k.l.push(e[2]);
    }else k.x.push([n, id, e]);
  });
  return k;
}
function karteiAusSpalten(gewusst, k){
  const liste = x => Array.isArray(x) ? x : null;
  const i = liste(k && k.i), s = liste(k && k.s), a = liste(k && k.a), l = liste(k && k.l), x = liste(k && k.x);
  if(!i || !s || !a || !l || !x || s.length !== i.length || a.length !== i.length || l.length !== i.length) throw new Error('kartei');
  const ganz = Number.isSafeInteger, paare = [];
  let p = -1, j = 0, xi = 0;
  for(let pos = 0, n = i.length + x.length; pos < n; pos++){
    const ausnahme = x[xi];
    if(Array.isArray(ausnahme) && ausnahme[0] === pos){
      if(typeof ausnahme[1] !== 'string') throw new Error('kartei');
      paare.push([ausnahme[1], ausnahme[2]]); xi++;
      continue;
    }
    if(j >= i.length || !ganz(i[j]) || !ganz(s[j]) || !ganz(a[j]) || !ganz(l[j])) throw new Error('kartei');
    p += i[j];
    if(p < 0 || p >= gewusst.length || typeof gewusst[p] !== 'string') throw new Error('kartei');
    paare.push([gewusst[p], [s[j], a[j] + l[j], l[j]]]); j++;
  }
  if(j !== i.length || xi !== x.length) throw new Error('kartei');
  return Object.fromEntries(paare);
}
/* Die Sicherung, wie sie gepackt wird: {f: 1, s: die Sicherung, k: die
   Kartei in Spalten}; in s steht kartei.w dann auf null, damit die
   Schluessel ihre Reihenfolge behalten. Ohne Kartei oder gewusst ohne k. */
function packForm(sicherung){
  const st = sicherung.stand, k = st && st.kartei;
  const objekt = x => !!x && typeof x === 'object' && !Array.isArray(x);
  if(!objekt(st) || !Array.isArray(st.gewusst) || !objekt(k) || !objekt(k.w)) return {f: 1, s: sicherung};
  return {f: 1, s: {...sicherung, stand: {...st, kartei: {...k, w: null}}}, k: karteiSpalten(st.gewusst, k.w)};
}
/* gepackt1 -> die Sicherung. Wirft, wenn es nicht geht. */
async function cloudAuspacken(z){
  const roh = await packStrom(base64Zurueck(z), new DecompressionStream('gzip'), CLOUD_AUSGEPACKT_MAX);
  const form = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(roh));
  const objekt = x => !!x && typeof x === 'object' && !Array.isArray(x);
  if(!objekt(form) || form.f !== 1 || !objekt(form.s)) throw new Error('form');
  if(form.k !== undefined){
    const st = form.s.stand, k = objekt(st) ? st.kartei : null;
    if(!objekt(st) || !Array.isArray(st.gewusst) || !objekt(k) || k.w !== null) throw new Error('form');
    k.w = karteiAusSpalten(st.gewusst, form.k);
  }
  return form.s;
}
/* Eine Sicherung gepackt, als Text fuer daten - oder null, wenn es nicht
   geht. Vor dem Hochladen wird sie mit demselben Weg wieder ausgepackt,
   den das andere Geraet nimmt (cloudStandLesen), und mit dem Stand
   verglichen (Empfehlung, Punkt 4). Weicht etwas ab, gibt es null, und
   cloudAbgleich() nimmt die alte Form oder schreibt gar nichts. Der
   Vergleichstext entsteht vor dem ersten await: Was waehrenddessen gelernt
   wird, gehoert schon zum naechsten Abgleich. */
async function cloudPacken(sicherung){
  if(!packenMoeglich()) return null;
  try{
    const soll = JSON.stringify(sicherung.stand);
    const roh = new TextEncoder().encode(JSON.stringify(packForm(sicherung)));
    const z = base64Aus(await packStrom(roh, new CompressionStream('gzip'), Infinity));
    const text = JSON.stringify({app: 'zmaj', version: 1, datum: sicherung.datum, stand: {[CLOUD_PACK_FELD]: z}});
    return JSON.stringify(await cloudStandLesen(text)) === soll ? text : null;
  }catch(e){ return null; }
}
/* Der Stand aus daten, alt oder gepackt - null, wenn es keine Sicherung
   ist (wie cloudStandAus).
     - alte Form ohne gepackt1: wie bisher.
     - nur gepackt1 (von 1.4 geschrieben): der ausgepackte Stand.
     - gepackt1 und daneben ein eigener Stand: das hat ein Geraet mit 1.1
       bis 1.3 geschrieben, das gepackt1 nur weitertrug. Beides wird
       zusammengefuehrt wie zwei Geraete (standZusammenfuehren, der
       ausgepackte als b, die Cloud).
     - gepackt1 laesst sich nicht auspacken (kaputt, oder das Geraet kann
       kein gzip): der Stand mit gepackt1, unveraendert. Dann traegt diese
       Fassung es weiter wie 1.3 ein fremdes Feld - weggeworfen wird nichts,
       was sich nicht lesen laesst. Vor jedem Schreiben versucht es das
       Auspacken noch einmal (gepacktEinarbeiten); erst wenn dieses Geraet
       selbst packt, ersetzt es gepackt1 (siehe cloudAbgleich). */
async function cloudStandLesen(text){
  const s = cloudStandAus(text);
  if(!s || !Object.prototype.hasOwnProperty.call(s, CLOUD_PACK_FELD) || !packenMoeglich()) return s;
  let innen = null;
  try{ innen = sicherungStandAus(await cloudAuspacken(s[CLOUD_PACK_FELD])); }catch(e){ innen = null; }
  if(!innen) return s;
  const aussen = {...s};
  delete aussen[CLOUD_PACK_FELD];
  return Object.keys(aussen).length ? standZusammenfuehren(aussen, innen, [], false) : innen;
}
/* Die Namen der Felder einer neueren Fassung in einem Stand, fuer m.fremd.
   Gekappt, damit ein gefaelschtes Dokument den Merker nicht aufblaeht;
   ein Name, der fehlt, laesst hoechstens ein geloeschtes Feld wieder
   zurueckkommen (siehe standZusammenfuehren). */
const fremdNamen = s => (s && typeof s === 'object' && !Array.isArray(s))
  ? Object.keys(s).filter(k => !STAND_FELDER.has(k) && !STAND_ALT.has(k) && k !== '__proto__' && k.length <= 200).slice(0, 100)
  : [];
/* Den Stand aus der Cloud einarbeiten. Er kommt von aussen wie eine
   Sicherungsdatei, also zuerst durch sicherungPlausibel(); das Ergebnis
   geht in standErsetzen() durch standUebernehmen(). Danach dasselbe wie
   nach dem Einlesen einer Datei (sicherungEinlesen). cloudVorher: siehe
   standZusammenfuehren(), ebenso erstesMal. */
function cloudUebernehmen(fremd, cloudVorher, erstesMal){
  if(!standErsetzen(() => standZusammenfuehren(standAlsObjekt(), sicherungPlausibel(fremd), cloudVorher, erstesMal))) return false;
  seitNachEinlesen();
  geschenkPruefen();
  syncLives(); pruefeSchutz();
  if(erstesMal) erfolgeErsterAbgleich();   // Erfolge: wie ein Update, vor dem Speichern
  saveProgress();
  renderLives();
  /* Auf der Startseite gleich zeigen, was dazugekommen ist. Mitten in einer
     Lektion nicht - dort gilt der neue Stand ab der naechsten. */
  if(sichtbar('pfad') && !frageSchliessen) showHome();
  return true;
}
/* Ein gepackt1 im eigenen Stand (Pruefbefund 13.11.2026). Das traegt ein
   Geraet, das bis zum Update noch 1.3 hatte: 1.3 hat gepackt1 aus der Cloud
   als Feld einer neueren Fassung abgelegt (standFremd) und weitergetragen.
   Nach dem Update auf 1.4 liest das Geraet die Cloud nur, wenn ein anderes
   geschrieben hat (cloudStandLesen) - sonst blieb gepackt1 hier fuer immer
   gepackt. Packte das Geraet dann selbst, kam es nicht mit in die Cloud:
   Die Woerter des Geraets, das gepackt1 geschrieben hatte, waren dort weg,
   und hier gingen sie beim Abmelden verloren. Mit Schritt 1 ging das noch
   gut (die alte Form traegt gepackt1 weiter), mit Schritt 2 nicht mehr.
   Darum wird es vor jedem Schreiben ausgepackt und eingearbeitet wie ein
   Stand aus der Cloud (cloudUebernehmen: erst sicherungPlausibel, dann
   standZusammenfuehren). gepackt1 selbst steht dabei in cloudVorher und
   faellt so aus dem eigenen Stand - sein Inhalt steht danach in den
   eigenen Feldern. Gibt zurueck:
     'nichts'         kein gepackt1, oder das Geraet kann kein gzip - dann
                      traegt es gepackt1 weiter wie 1.3
     'kaputt'         es laesst sich nicht auspacken. Es bleibt hier und in
                      der alten Form auch in der Cloud; erst wenn das Geraet
                      packt, ersetzt es das neue gepackt1 (siehe cloudAbgleich)
     'eingearbeitet'  ausgepackt und eingearbeitet
     'fehler'         das Einarbeiten warf; der Stand ist wie vorher */
async function gepacktEinarbeiten(){
  const z = standFremd[CLOUD_PACK_FELD];
  if(z === undefined || !packenMoeglich()) return 'nichts';
  let innen = null;
  try{ innen = sicherungStandAus(await cloudAuspacken(z)); }catch(e){ innen = null; }
  if(!innen) return 'kaputt';
  /* Waehrenddessen eine Sicherungsdatei eingelesen: dann deren gepackt1
     (oder keins). Sonst liesse cloudAbgleich ein ungeprueftes weg. */
  if(standFremd[CLOUD_PACK_FELD] !== z) return gepacktEinarbeiten();
  return cloudUebernehmen(innen, [CLOUD_PACK_FELD], false) ? 'eingearbeitet' : 'fehler';
}
/* Nachsehen bei jedem Oeffnen (17.11.2026, Ajdin: "ja ist gut so ...
   standard meine ich"). Befund am Geraet am selben Tag: Ein zweites Geraet
   hatte am Nachmittag gelesen, als in der Cloud noch ein Stand von vor drei
   Tagen stand, und las bis zum naechsten Tag nicht mehr. Es zeigte "Deine
   Lernserie ist leider gerissen" und einen alten Levelstand, obwohl in der
   Cloud laengst mehr stand. Jetzt sieht die App beim Start und bei
   jeder Rueckkehr in den Vordergrund nach - nur rev, ein Lesevorgang mit ein
   paar hundert Bytes; den ganzen Stand gibt es nur, wenn ein anderes Geraet
   geschrieben hat. Hoechstens alle CLOUD_NACHSEHEN_MS, sonst kostete
   schnelles Hin- und Herwechseln jedesmal eine Anfrage. cloudNachgesehen
   steht nur im Arbeitsspeicher: ein neuer Start sieht immer nach. Gezaehlt
   wird jede Anfrage an die Cloud, auch die vor dem Schreiben. */
let CLOUD_NACHSEHEN_MS = 2 * 60 * 1000;   // die Tests setzen sie herunter
let cloudNachgesehen = 0;                  // Date.now() der letzten Anfrage
/* Ob sich nur rev holen laesst (kennung, 13.11.2026): nicht bei einem
   Adapter ohne kennung, nicht ohne gemerktes rev und nicht, wenn Firestore
   die Feldmaske heute nicht annimmt (cloudMaskeAus).
   Pruefbefund 17.11.2026: Bis dahin galt jeder Fehler beim Nachsehen als
   abgelehnte Maske, auch ein einzelner 503 von Firestore oder vom
   Ausweis, und das Nachsehen blieb bis zum naechsten Start aus - ein
   zweites Geraet sah dann wieder tagelang nichts Neues, genau der Befund
   vom 17.11. Jetzt: Weist Firestore die Maske selbst ab (400, e.maske),
   gilt sie fuer heute als abgelehnt; andere Fehler erst, wenn es
   CLOUD_MASKE_FEHLER Mal hintereinander so ging und das ganze Lesen danach
   klappte. Fehler des Ausweises (e.ausweis) zaehlen nie. Ein gelungenes
   Nachsehen faengt von vorn an, und am naechsten Tag wird die Maske wieder
   versucht. Nur im Arbeitsspeicher, je Adapter {tag, n}. */
const CLOUD_MASKE_FEHLER = 2;
const cloudMaskeFehler = new WeakMap();
function cloudMaskeAus(adapter){
  const x = cloudMaskeFehler.get(adapter);
  return !!x && x.tag === today() && x.n >= CLOUD_MASKE_FEHLER;
}
const cloudBillig = (adapter, m) => !!m.rev && typeof adapter.kennung === 'function' && !cloudMaskeAus(adapter);
/* Schreibversuche am Tag (Pruefbefund 17.11.2026). "Hoechstens zwei am Tag"
   (m.tag, m.ende) zaehlt nur, was ankam. Blieb die Antwort aufs Schreiben
   aus - langsames Netz, die 20 Sekunden in senden() laufen ab, obwohl
   Firestore den Stand schon hat -, schrieb jeder weitere Anlass neu: in
   der Probe 15 Schreibvorgaenge und 14 volle Ladungen an einem Tag. Darum
   zaehlt m.versuche ({tag, n}) jeden Schreibversuch von 'pause', 'start',
   'vorn' und 'ende', gemerkt VOR dem Schreiben, damit auch eine dabei
   beendete App ihn verbraucht hat. Sind es CLOUD_SCHREIBVERSUCHE, wird bis
   zum naechsten Tag nur noch nachgesehen; was liegen blieb, holt das erste
   Oeffnen am naechsten Tag nach. Anmelden und Abmelden zaehlen nicht und
   sind nie gesperrt. Vier: die zwei, die ankommen sollen, und Luft fuer
   zwei, die nicht ankamen - etwa das Schreiben beim Verlassen, das Android
   beim Wegwischen abwuergt. */
const CLOUD_SCHREIBVERSUCHE = 4;
/* Steht in der Cloud (s, wie cloudStandLesen ihn liefert) schon alles,
   was dieses Geraet hat? Rein, vor dem Einarbeiten: Der eigene Stand mit
   der Cloud zusammengefuehrt ergibt dasselbe wie die Cloud mit sich selbst
   - mit denselben Schritten wie cloudUebernehmen() (sicherungPlausibel,
   standZusammenfuehren, cloudVorher). getragen zaehlt nicht mit: das ist
   die Wahl des Geraets, dort gewinnt ohnehin das eigene. Pruefbefund
   17.11.2026, siehe cloudAbgleich() bei !schreiben. Bewusst nicht nur "seit
   dem letzten Hochladen nichts Neues" (m.fp): Schreiben zwei Geraete im
   selben Augenblick, fehlt dem spaeteren Stand in der Cloud, was das
   fruehere hochgeladen hatte - das muss wieder hoch. Laeuft nur, wenn ein
   anderes Geraet geschrieben hat; wirft etwas, gilt es als nein. */
function cloudHatAlles(s, cloudVorher){
  try{
    const b = sicherungPlausibel(s);
    const mit = standZusammenfuehren(standAlsObjekt(), b, cloudVorher, false);
    const nur = standZusammenfuehren(b, b, cloudVorher, false);
    mit.getragen = nur.getragen;
    return JSON.stringify(mit) === JSON.stringify(nur);
  }catch(e){ return false; }
}
/* Der Abgleich. anlass:
     'start'     die App startet, und seit 17.11.2026
     'vorn'      sie kommt zurueck in den Vordergrund: beide nachsehen und,
                 wenn noetig, das Schreiben des Tages nachholen (unten)
     'pause'     sie geht in den Hintergrund: schreiben, hoechstens einmal am
                 Tag (m.tag)
     'ende'      seit 17.11.2026 gleich nach dem Lernen (cloudNachLernen):
                 schreiben, hoechstens einmal am Tag (m.ende)
     'anmelden'  lesen und schreiben, zaehlt nicht als der eine am Tag
     'abmelden'  seit 28.10.2026 dasselbe, ein letztes Mal vor dem Abmelden
   Gibt zurueck, was passiert ist - fuer die Tests und fuers Abmelden.
   Nachholen (17.11.2026): Geschrieben wurde bis dahin nur beim Wechsel in
   den Hintergrund. Wischt man die App danach weg, beendet Android sie, bevor
   die Anfragen fertig sind - im Befund kam drei Tage lang nichts in der
   Cloud an, obwohl auf dem Handy gelernt wurde. Hat sich der Stand seit
   dem letzten Hochladen geaendert (m.fp) und ist das Schreiben beim
   Verlassen heute noch nicht gelungen (m.tag), holt das Oeffnen es nach,
   genau wie 'pause', und es zaehlt dann als dieses eine. Weil das Oeffnen
   oft erst am naechsten Tag kommt, schreibt die App ausserdem einmal am Tag
   gleich nach dem Lernen ('ende'), solange sie noch vorn ist: Ein zweites
   Geraet kennt den Lerntag dann noch am selben Tag. Zusammen hoechstens zwei
   Schreibvorgaenge je Nutzer und Tag (dazu An- und Abmelden), jeder nur,
   wenn sich etwas geaendert hat - bei Spark (20 000 am Tag fuer alle) reicht
   das fuer rund 10 000 Lernende am Tag. Enger wird jetzt das Lesen (50 000
   am Tag): rund ein Lesevorgang je Oeffnen und einer je Schreiben.
   Nachbesserung nach dem Pruefbefund vom 17.11.2026: hoechstens
   CLOUD_SCHREIBVERSUCHE Versuche am Tag, auch wenn keiner ankommt; reines
   Einarbeiten gilt als hochgeladen (m.fp, unten); und ein einzelner Fehler
   beim Nachsehen schaltet es nicht mehr ab (cloudMaskeAus). */
async function cloudAbgleich(anlass, adapter = cloudAdapter()){
  const m = cloudMerker();
  if(!adapter || !m || cloudLaeuft || !standGeladen || MIT_SERVER) return 'nichts';
  const heute = today(), erstes = anlass === 'anmelden', zuletzt = anlass === 'abmelden';
  const oeffnen = anlass === 'start' || anlass === 'vorn', nachLernen = anlass === 'ende';
  const geaendert = () => m.fp !== cloudFingerabdruck(standAlsObjekt());
  // Heute schon so oft zu schreiben versucht, siehe CLOUD_SCHREIBVERSUCHE.
  const versucht = () => (m.versuche && m.versuche.tag === heute && Number(m.versuche.n)) || 0;
  const frei = versucht() < CLOUD_SCHREIBVERSUCHE;
  let schreiben = erstes || zuletzt || (anlass === 'pause' && m.tag !== heute && frei);
  if(oeffnen){
    // Gedrosselt; geht die Uhr des Geraets zurueck, wird nachgesehen.
    const seit = Date.now() - cloudNachgesehen;
    if(cloudNachgesehen && seit >= 0 && seit < CLOUD_NACHSEHEN_MS) return 'nichts';
    schreiben = frei && m.tag !== heute && geaendert();
    /* Billig ist nur rev. Ohne (cloudBillig) kaeme bei jedem Oeffnen der
       ganze Stand - dann wie bisher hoechstens einmal am Tag. */
    if(!schreiben && m.gelesen === heute && !cloudBillig(adapter, m)) return 'nichts';
  }else if(nachLernen){
    if(!frei || m.ende === heute || !geaendert()) return 'nichts';
    schreiben = true;
  }else{
    if(!schreiben && m.gelesen === heute) return 'nichts';
    /* Heute schon gelesen und seit dem letzten Hochladen nichts Neues: dann
       auch keine Anfrage. */
    if(schreiben && !erstes && !zuletzt && m.gelesen === heute && !geaendert()) return 'unveraendert';
  }
  cloudLaeuft = true;
  cloudNachgesehen = Date.now();
  try{
    /* Erst nachsehen (13.11.2026, Empfehlung Punkt 3): zuerst nur rev.
       Den ganzen Stand gibt es nur, wenn ein anderes Geraet geschrieben hat
       oder dieses noch keinen kennt (m.rev leer). Sonst kaeme er Tag fuer
       Tag umsonst - bis zu 900 000 Bytes, und der Datenverkehr ist die
       engste Grenze des Gratis-Tarifs (cloud.md, Kosten). Ein Adapter ohne
       kennung laedt wie bisher alles. Scheitert das Nachsehen aus einem
       anderen Grund als Netz oder Anmeldung - etwa weil Firestore die
       Feldmaske einmal nicht annimmt -, wird wie bisher alles geladen.
       Sonst bliebe jeder Abgleich an dieser einen Anfrage haengen. */
    let dok, kennung, maske = '';
    if(cloudBillig(adapter, m)){
      try{ kennung = await adapter.kennung(m); }
      catch(e){
        if(!e || e.netz || e.abgemeldet || e.name === 'AbortError') throw e;
        kennung = undefined;
        maske = e.ausweis ? 'ausweis' : (e.maske ? 'abgelehnt' : 'fehler');
      }
    }
    if(kennung === undefined) dok = await adapter.laden(m);
    else dok = kennung === null ? null : (kennung === m.rev ? {rev: kennung, text: null} : await adapter.laden(m));
    /* Ging das Nachsehen nicht, das ganze Lesen aber schon: mitzaehlen,
       ob Firestore die Feldmaske nicht annimmt - sonst kaeme mit dem
       Nachsehen bei jedem Oeffnen (17.11.2026) jedesmal der ganze Stand.
       Ging es, von vorn. Siehe cloudMaskeAus(). */
    if(maske === 'abgelehnt' || maske === 'fehler'){
      const x = cloudMaskeFehler.get(adapter), vorher = (x && x.tag === heute) ? x.n : 0;
      cloudMaskeFehler.set(adapter, {tag: heute, n: maske === 'abgelehnt' ? CLOUD_MASKE_FEHLER : vorher + 1});
    }else if(kennung !== undefined) cloudMaskeFehler.delete(adapter);
    m.gelesen = heute;
    const fremd = !!dok && dok.rev !== m.rev;
    let schonOben = false;
    if(fremd){
      /* Ist der Text dort kaputt, gibt es nichts einzuarbeiten - dann
         ersetzt ihn unten der eigene Stand. Wirft das Einarbeiten, wird
         lieber nicht geschrieben: dort koennte ein anderes Geraet stehen.
         Seit 13.11.2026 alt oder gepackt, siehe cloudStandLesen(). */
      const s = await cloudStandLesen(dok.text);
      if(s && !schreiben && m.rev) schonOben = cloudHatAlles(s, m.fremd);
      if(s && !cloudUebernehmen(s, m.fremd, !m.rev)) return 'fehler';
      m.rev = dok.rev;
      m.fremd = fremdNamen(s);
    }
    if(!dok) m.fremd = [];
    if(!schreiben){
      /* Pruefbefund 17.11.2026: Hatte die Cloud schon alles, was dieses
         Geraet hat (cloudHatAlles), gilt der zusammengefuehrte Stand als
         hochgeladen (m.fp). Bis dahin hielt das naechste Oeffnen ihn fuer
         neu (sortierte Listen genuegten) und lud ihn noch einmal hoch, mit
         dem Schreiben des Tages (m.tag): Gerade im Zwei-Geraete-Fall des
         Befunds kostete jedes Einarbeiten so den zweiten Schreibvorgang, und
         was danach gelernt wurde, kam erst am naechsten Tag hoch. Was
         cloudUebernehmen() dabei selbst nachtraegt (Serienschutz, Abzeichen),
         kommt mit der naechsten eigenen Aenderung mit; das andere Geraet
         rechnet es ohnehin selbst. Fehlt der Cloud etwas von hier - eigenes
         Neues, oder ein anderes Geraet hat im selben Augenblick darueber
         geschrieben -, bleibt m.fp, und das Nachholen bringt es hoch. */
      if(schonOben) m.fp = cloudFingerabdruck(standAlsObjekt());
      cloudMerkerSetzen(m, true);
      return fremd ? 'zusammengefuehrt' : 'gelesen';
    }
    /* Traegt der eigene Stand noch gepackt1 (Update von 1.3), erst
       auspacken und einarbeiten, siehe gepacktEinarbeiten(). Wirft das
       Einarbeiten, wird lieber nicht geschrieben - wie oben. */
    if(await gepacktEinarbeiten() === 'fehler'){ cloudMerkerSetzen(m, true); return 'fehler'; }
    const stand = standAlsObjekt(), fp = cloudFingerabdruck(stand);
    if(!erstes && dok && !fremd && fp === m.fp){ cloudMerkerSetzen(m, true); return 'unveraendert'; }
    /* Passt der Stand nicht in die Cloud, bleiben dort Felder einer
       neueren Fassung weg, Feld fuer Feld, bis er passt (Pruefbefund
       28.10.2026). Auf dem Geraet bleiben sie, und die neuere Fassung hat
       ihre eigene Kopie. Vorher scheiterte dann jedes Hochladen still mit
       'zu gross': der Lernfortschritt dieses Geraets kam nie mehr in die
       Cloud, und Abmelden ging nicht mehr. 'zu gross' heisst jetzt, schon
       der eigene Stand ist groesser als CLOUD_GROESSE_MAX - mit echtem
       Lernen unerreichbar, siehe dort.
       13.11.2026: Davor wird gepackt, wenn die alte Form nicht passt (nach
       Schritt 2 immer, CLOUD_IMMER_PACKEN). Erst wenn auch das nicht geht
       oder nicht passt, bleiben fremde Felder weg. Ein gepackt1, das hier
       jetzt noch im Stand steht, liess sich oben nicht auspacken
       (gepacktEinarbeiten, 'kaputt'): Nur dann kommt es nicht mit in das
       Gepackte, das neue gepackt1 ersetzt es. In der alten Form bleibt es
       stehen, und auf dem Geraet auch. (Bis zum Pruefbefund vom 13.11.2026
       hiess es hier, ein mitgetragenes gepackt1 sei immer kaputt. Ein
       Geraet, das es noch unter 1.3 bekommen hat, hat es aber nie
       auszupacken versucht.) */
    let oben = stand, text = JSON.stringify(sicherungObjekt(stand)), gepackt = false;
    if(CLOUD_IMMER_PACKEN || utf8Laenge(text) > CLOUD_GROESSE_MAX){
      const innen = Object.fromEntries(Object.entries(stand).filter(([k]) => k !== CLOUD_PACK_FELD));
      const p = await cloudPacken(sicherungObjekt(innen));
      if(p && utf8Laenge(p) <= CLOUD_GROESSE_MAX){ oben = innen; text = p; gepackt = true; }
    }
    if(!gepackt && utf8Laenge(text) > CLOUD_GROESSE_MAX){
      const eigen = Object.fromEntries(Object.entries(stand).filter(([k]) => STAND_FELDER.has(k)));
      const platz = CLOUD_GROESSE_MAX - utf8Laenge(JSON.stringify(sicherungObjekt(eigen)));
      oben = Object.assign(eigen, standFremdAus(stand, platz));
      text = JSON.stringify(sicherungObjekt(oben));
    }
    if(utf8Laenge(text) > CLOUD_GROESSE_MAX){ cloudMerkerSetzen(m, true); return 'zu gross'; }
    const rev = cloudRev();
    // Den Versuch merken, bevor er losgeht - siehe CLOUD_SCHREIBVERSUCHE.
    if(!erstes && !zuletzt){ m.versuche = {tag: heute, n: versucht() + 1}; cloudMerkerSetzen(m, true); }
    await adapter.speichern(m, {text, rev});
    m.rev = rev; m.fp = fp; m.gesichert = heute; m.fremd = fremdNamen(oben);
    if(nachLernen) m.ende = heute;
    else if(!erstes && !zuletzt) m.tag = heute;     // 'pause', oder nachgeholt beim Oeffnen
    cloudMerkerSetzen(m, true);
    return 'gespeichert';
  }catch(e){
    // Kein Netz oder abgelehnt: der Tag ist nicht verbraucht.
    cloudMerkerSetzen(m, true);
    cloudFehlerGrund = cloudGrund(e);   // fuers Abmelden: Netz oder Firebase?
    /* Die Anmeldung ist bei Firebase ungueltig geworden (Konto geloescht,
       gesperrt, Passwort anderswo geaendert) - nicht bei Netzfehlern. */
    if(e && e.abgemeldet) cloudVonAussenAbgemeldet(m.uid);
    return 'fehler';
  }finally{ cloudLaeuft = false; }
}
/* Gleich nach dem Lernen (17.11.2026, siehe cloudAbgleich): nach dem
   Ergebnis einer Lektion, einer Runde, eines Tests, einer Geschichte und
   eines Sprung-Tests, solange die App noch vorn ist. Einen Takt spaeter,
   damit der Fingerabdruck den Ergebnisschirm nicht aufhaelt, und ohne
   Warten: Was nicht ankommt, holt das naechste Oeffnen nach. Ohne Cloud
   (CLOUD_AN = false) passiert nichts. */
function cloudNachLernen(){
  if(CLOUD_AN) setTimeout(() => cloudAbgleich('ende'), 0);
}
/* Der Grund eines Fehlers, wie ihn kontoFirebaseFehler() versteht: Firebases
   error.message, 'netz' oder einer der Gruende aus cloudGoogleAusweis(). */
function cloudGrund(e){
  if(!e) return 'fehler';
  if(e.grund) return String(e.grund);
  if(e.netz || e.name === 'AbortError' || e instanceof TypeError) return 'netz';
  return 'fehler';
}
/* art: 'google', 'passwort' (daten: email, pw), 'neu' (Konto mit E-Mail
   anlegen, daten wie bei 'passwort') oder 'anonym'. Gibt zurueck, ob die
   Anmeldung geklappt hat; den Grund fuer ein Nein legt sie in
   cloudFehlerGrund. Ob der erste Abgleich gleich durchkam, ist egal -
   sonst eben beim naechsten Anlass. */
async function cloudAnmelden(art, adapter = cloudAdapter(), daten){
  cloudFehlerGrund = '';
  if(!adapter || !standGeladen || MIT_SERVER || cloudLaeuft) return false;
  let konto = null;
  try{
    konto = art === 'neu' ? await adapter.registrieren((daten || {}).email, (daten || {}).pw)
                          : await adapter.anmelden(art, daten);
  }catch(e){ cloudFehlerGrund = cloudGrund(e); }
  if(!konto || typeof konto.uid !== 'string' || !konto.uid){
    cloudFehlerGrund = cloudFehlerGrund || 'fehler';
    return false;
  }
  /* Dasselbe Konto noch einmal: rev und fp bleiben. Ein anderes faengt von
     vorn an - sein Stand wird beim Abgleich zusammengefuehrt. */
  const alt = cloudMerker();
  const neu = {art: art === 'neu' ? 'passwort' : art, token: konto.token || ''};
  if(konto.email) neu.email = konto.email;
  cloudMerkerSetzen(alt && alt.uid === konto.uid ? Object.assign(alt, neu) : Object.assign({uid: konto.uid}, neu));
  try{ localStorage.removeItem(ABGEMELDET); }catch(e){}
  restoreUid = '';
  /* Die Bestaetigungsmail einmal nach dem Anlegen (Frage 4 im Plan, nach
     dem Vorschlag gebaut). Bestaetigen muss niemand - Ajdin am 27.10.2026:
     keine Bestaetigungspflicht. Nicht warten, Fehler sind egal. */
  if(art === 'neu' && konto.idToken && adapter.bestaetigungSchicken){
    adapter.bestaetigungSchicken(konto.idToken).catch(()=>{});
  }
  await cloudAbgleich('anmelden', adapter);
  anmAufruf('restoreSichern', {uid: konto.uid}, 20000);
  return true;
}
/* Abmelden ist nur Vergessen auf diesem Geraet - ohne Netz. Die Oberflaeche
   (cloudAbmeldenGanz) schreibt vorher ein letztes Mal. */
function cloudAbmelden(){ try{ localStorage.removeItem(CLOUD_MERKER); }catch(e){} }
/* Konto und Sicherung in der Cloud loeschen. Google Play verlangt das fuer
   jede App, in der man ein Konto anlegen kann. Gibt zurueck: true (beides
   weg), 'konto bleibt' (die Sicherung ist weg, das Konto nicht - siehe
   loeschen im Adapter) oder false (nichts geloescht, angemeldet bleiben
   fuer einen neuen Versuch). optionen.passwort: bei E-Mail-Konten, fuer
   die frische Anmeldung davor (28.10.2026).
   19.10.2026: Ist die Sicherung weg, wird immer abgemeldet - sonst laedt
   das naechste 'pause' den Stand wieder hoch, und die Loeschung haette
   nicht gewirkt. cloudLaeuft haelt so lange jeden Abgleich auf, auch den,
   den Googles Kontoauswahl beim Verdecken der App anstossen koennte. */
async function cloudLoeschen(adapter = cloudAdapter(), optionen){
  cloudFehlerGrund = '';
  const m = cloudMerker();
  if(!adapter || !m || cloudLaeuft) return false;
  cloudLaeuft = true;
  try{
    let ganz;
    try{ ganz = await adapter.loeschen(m, optionen || {}); }
    catch(e){ cloudFehlerGrund = cloudGrund(e); return false; }
    cloudAbmelden();
    return ganz === false ? 'konto bleibt' : true;
  }finally{ cloudLaeuft = false; }
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
