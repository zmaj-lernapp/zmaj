/* =================== ANMELDUNG =================== */
/* Fünf Zustände in einer Maske:
     'anmelden'   E-Mail oder Benutzername + Passwort + angemeldet bleiben
     'neu'        Benutzername + E-Mail + Passwort + Wiederholung
     'warten'     Konto steht, die Bestätigungsmail ist unterwegs
     'vergessen'  E-Mail eingeben, Link anfordern
     'neupw'      neues Passwort setzen (über den Link aus der Mail)
   Das Passwort verlässt den Browser nur beim Absenden und wird nirgends
   gespeichert. Die Anmeldung merkt sich der Server über ein Cookie, an das
   dieses Skript nicht herankommt. */
let kontoModus = 'anmelden';
let kontoMail = '';      // Adresse des angemeldeten Kontos, nur zum Anzeigen
let kontoCode = '';        // Code aus dem Link, nur für 'neupw'
let kontoWartetAuf = '';   // Adresse, an die die Bestätigung ging

function zeigeAnmeldung(modus, daten){
  kontoModus = modus || 'anmelden';
  daten = daten || {};
  showView('profileView'); $('kopfLeiste').style.display='none';
  setzeZurueck('', null);
  $('btnProfil').style.display='none'; $('btnSettings').style.display='none'; $('btnShop').style.display='none';
  $('zmajProfile').innerHTML=zmaj('happy'); setMood($('zmajProfile'),'happy');
  renderLangBar();

  const m = kontoModus;
  const titel = {anmelden:'konto.anmelden_titel', neu:'konto.anlegen_titel',
                 warten:'konto.warten_titel', vergessen:'konto.vergessen_titel',
                 neupw:'konto.neupw_titel'}[m];
  const frage = {anmelden:'konto.anmelden_frage', neu:'konto.anlegen_frage',
                 warten:'konto.warten_frage', vergessen:'konto.vergessen_frage',
                 neupw:'konto.neupw_frage'}[m];
  // Auf dieser Seite steht der Titel groß in der Mitte, nicht klein im Kopf
  $('kontoTitel').textContent = t(titel);
  $('tag').textContent = '';
  // Ohne bekannte Adresse stünde da "Wir haben eine Mail an  geschickt" -
  // mit einer Lücke mitten im Satz. Dann die Fassung ohne Adresse nehmen.
  const frageJetzt = (m === 'warten' && !kontoWartetAuf) ? 'konto.warten_frage_kurz' : frage;
  $('kontoFrage').textContent = t(frageJetzt, {email: kontoWartetAuf});

  // Welche Felder gehören zu welchem Zustand
  const zeigt = {
    name:    m==='anmelden' || m==='neu' || m==='vergessen',
    nameSub: m==='neu',
    mail:    m==='neu',
    pw:      m==='anmelden' || m==='neu' || m==='neupw',
    pw2:     m==='neu' || m==='neupw',
    regeln:  m==='neu' || m==='neupw',
    bleiben: m==='anmelden' || m==='neu' || m==='neupw',
    wechsel: true,          // auch beim Warten: sonst käme man nicht zurück
    vergessen: m==='anmelden'
  };
  $('kontoName').hidden = !zeigt.name;
  $('kontoNameSub').hidden = !zeigt.nameSub;
  $('kontoMail').hidden = !zeigt.mail;
  $('kontoPw').hidden = !zeigt.pw;
  $('kontoPw2').hidden = !zeigt.pw2;
  $('kontoRegeln').hidden = !zeigt.regeln;
  pwListeBeschreibt(zeigt.regeln);
  $('kontoBleibenZeile').hidden = !zeigt.bleiben;
  $('kontoWechsel').hidden = !zeigt.wechsel;
  $('kontoVergessen').hidden = !zeigt.vergessen;
  // Der Spam-Hinweis steht beim Warten immer da. Beim Passwort-vergessen
  // erst, wenn die Mail wirklich raus ist - vorher gibt es nichts zu suchen.
  $('kontoSpam').hidden = m !== 'warten';
  $('kontoSpam').textContent = t('konto.spam_kurz');

  // Das Namensfeld heißt je nach Zustand anders
  $('kontoName').placeholder = t(m==='neu' ? 'konto.benutzername'
                                : m==='vergessen' ? 'konto.email' : 'konto.kennung');
  $('kontoName').type = m==='vergessen' ? 'email' : 'text';
  $('kontoName').setAttribute('autocomplete', m==='vergessen' ? 'email' : 'username');

  const neuesPw = m==='neu' || m==='neupw';
  $('kontoPw').placeholder = t(neuesPw ? 'konto.passwort_neu' : 'konto.passwort');
  $('kontoPw').setAttribute('autocomplete', neuesPw ? 'new-password' : 'current-password');

  $('kontoSenden').textContent = t({anmelden:'konto.anmelden', neu:'konto.neu',
    warten:'konto.warten_nochmal', vergessen:'konto.vergessen_senden',
    neupw:'konto.speichern'}[m]);
  $('kontoWechsel').textContent = t(m==='anmelden' ? 'konto.neu'
                                  : m==='warten' ? 'konto.warten_anmelden'
                                  : 'konto.zurueck_anmelden');

  $('kontoNote').textContent = daten.hinweis || '';
  $('kontoNote').className = 'note';
  $('kontoPw').value = ''; $('kontoPw2').value = '';
  if(m!=='vergessen' && !daten.behalteName) $('kontoName').value = '';
  if(m==='neu') $('kontoMail').value = '';
  if(zeigt.regeln) zeigeRegeln($('kontoRegeln'), '');
  if(zeigt.name) $('kontoName').focus(); else if(zeigt.pw) $('kontoPw').focus();
}
/* Beim Tippen die Liste neu. Die Adresse gehoert seit 29.10.2026 zu den
   Regeln (nicht deine E-Mail): wer sie nach dem Passwort aendert, sieht die
   Liste gleich richtig. Mit der Pflicht-Anmeldung geht dabei auch die rote
   Zeile unter "Konto anlegen" weg - sonst stand dort noch "Es fehlt ein
   Sonderzeichen", als die Liste es laengst abgehakt hatte (gefunden am
   Bildschirmfoto, 29.10.2026). Was dann noch fehlt, zeigt die Liste; die
   Zeile kommt beim naechsten Tipp auf den Knopf wieder. */
function kontoGetippt(){
  if($('kontoRegeln').hidden) return;
  zeigeRegeln($('kontoRegeln'), $('kontoPw').value, $('kontoMail').value);
  const note = $('kontoNote');
  if(cloudModus() && note.classList.contains('no')){ note.textContent = ''; note.className = 'note'; }
}
['kontoMail', 'kontoPw', 'kontoPw2'].forEach(id => $(id).addEventListener('input', kontoGetippt));
$('kontoVergessen').addEventListener('click', ()=>
  cloudModus() ? anmeldungZeigen(anmAnlass, 'mail_vergessen') : zeigeAnmeldung('vergessen'));

/* Dieselben Regeln wie in konten.py. Verbindlich ist immer der Server;
   hier stehen sie nur, damit man beim Tippen sieht, was noch fehlt. */
const PW_MIN = 10;
const PW_REGELN = [
  ['passwort_kurz',    'konto.regel_laenge',  p => p.length >= PW_MIN],
  ['passwort_gross',   'konto.regel_gross',   p => /\p{Lu}/u.test(p)],
  ['passwort_klein',   'konto.regel_klein',   p => /\p{Ll}/u.test(p)],
  ['passwort_zahl',    'konto.regel_zahl',    p => /\p{Nd}/u.test(p)],
  ['passwort_zeichen', 'konto.regel_zeichen', p => /[^\p{L}\p{N}\s]/u.test(p)],
  ['passwort_leerzeichen', 'konto.regel_leer', p => !/\s/.test(p)]
];

/* Mit der Pflicht-Anmeldung (28.10.2026) galt erst nur die Laenge. Seit
   29.10.2026 gelten dort die Regeln aus PW_REGELN_CLOUD, gezaehlt wie bei
   Firebase, und dazu "nicht deine E-Mail": ○ solange das Feld leer ist,
   ✓ sobald etwas darin steht, das den Teil vor dem @ nicht enthaelt, rot
   mit ✗, wenn doch. Sie steht nur da, wenn vor dem @ mindestens 3 Zeichen
   stehen - kuerzer gilt sie nicht (pwOhneEmail). Bis zur Pruefung am
   selben Tag erschien sie nur verletzt und bekam nie einen Haken; verlangt
   war aber ein Haken fuer jede erfuellte Regel. markieren (nach "Konto
   anlegen") faerbt rot, was noch fehlt. */
function zeigeRegeln(kasten, passwort, email, markieren){
  const cloud = cloudModus();
  const regeln = cloud ? PW_REGELN_CLOUD : PW_REGELN;
  const punkt = (klasse, text) => '<span class="'+klasse+'">'+esc(text)+'</span>';
  const mail = cloud && emailVorAt(email).length >= 3
    ? punkt(!pwOhneEmail(passwort, email) ? 'nein' : passwort ? 'ok' : '', t('konto.regel_email')) : '';
  kasten.innerHTML = '<b>'+esc(t('konto.regeln_titel'))+'</b>' +
    regeln.map(([, schluessel, erfuellt]) =>
      punkt(erfuellt(passwort) ? 'ok' : (markieren ? 'fehlt' : ''),
            t(schluessel, {n: cloud ? PW_MIN_CLOUD : PW_MIN}))).join('') + mail;
}
/* Die Liste beschreibt das Passwortfeld (aria-describedby), solange sie
   zu sehen ist: ein Bildschirmleser nennt die Regeln mit dem Feld. Live
   ist sie nicht, sonst kaeme sie bei jedem Tastendruck (29.10.2026).
   Dazu ein Name, derselbe Text wie der Platzhalter (die Liste steht nur
   bei einem neuen Passwort da): ein Feld, das nur der Platzhalter benennt
   und das eine Beschreibung hat, beanstandet axe als label-title-only
   (ernst) - gefunden mit tests_e2e/test_barrierefreiheit.py. Eine neue
   Sprache baut die Seite neu auf (setzeSprache), der Name folgt also. */
function pwListeBeschreibt(an){
  const feld = $('kontoPw');
  if(an){ feld.setAttribute('aria-describedby', 'kontoRegeln'); feld.setAttribute('aria-label', t('konto.passwort_neu')); }
  else { feld.removeAttribute('aria-describedby'); feld.removeAttribute('aria-label'); }
}

/* Serverfehler in einen Satz übersetzen, den man lesen kann. */
function kontoFehlerText(fehler){
  const f = String(fehler||'');
  if(f.startsWith('gesperrt:')) return t('konto.fehler_gesperrt', {zeit: fmtDauer(parseInt(f.slice(9),10)||60)});
  return ({
    falsche_daten:   t('konto.fehler_daten'),
    passwort_kurz:   t('konto.fehler_kurz', {n: PW_MIN}),
    passwort_lang:   t('konto.fehler_lang'),
    passwort_gross:  t('konto.fehler_gross'),
    passwort_klein:  t('konto.fehler_klein'),
    passwort_zahl:   t('konto.fehler_zahl'),
    passwort_zeichen:t('konto.fehler_zeichen'),
    passwort_leerzeichen: t('konto.fehler_pw_leerzeichen'),
    name_vergeben:   t('konto.fehler_vergeben'),
    name_fehlt:      t('konto.fehler_name'),
    name_kurz:       t('konto.fehler_name_kurz', {n: 3}),
    name_lang:       t('konto.fehler_name_lang', {n: 20}),
    name_zeichen:    t('konto.fehler_name_zeichen'),
    name_leerzeichen:t('konto.fehler_name_leerzeichen'),
    email_fehlt:     t('konto.fehler_email'),
    email_ungueltig: t('konto.fehler_email'),
    email_vergeben:  t('konto.fehler_email_vergeben'),
    email_offen:     t('konto.fehler_email_offen'),
    code_ungueltig:  t('konto.fehler_code'),
    altes_falsch:    t('konto.fehler_alt'),
    nicht_angemeldet: t('konto.fehler_daten')
  })[f] || t('konto.fehler_allgemein');
}

/* Sekunden als "3 Minuten" oder "40 Sekunden" */
function fmtDauer(sek){
  const m = Math.ceil(sek/60);
  return m >= 1 ? tp('zeit.min_lang', m) : tp('zeit.sekunden', Math.max(1, sek));
}

$('kontoWechsel').addEventListener('click', ()=> cloudModus()
  ? anmeldungZeigen(anmAnlass, anmModus === 'mail_an' ? 'mail_neu' : 'mail_an')
  : zeigeAnmeldung(kontoModus==='anmelden' ? 'neu' : 'anmelden'));

$('kontoForm').addEventListener('submit', async e=>{
  e.preventDefault();
  // Pflicht-Anmeldung mit Firebase (28.10.2026), der Server-Zweig darunter bleibt fuer start.py
  if(cloudModus()) return cloudFormularSenden();
  const m    = kontoModus;
  const name = $('kontoName').value.trim();
  const adr  = $('kontoMail').value.trim();
  const pw   = $('kontoPw').value;
  const pw2  = $('kontoPw2').value;
  const bleiben = $('kontoBleiben').checked;
  const note = $('kontoNote');
  note.className = 'note';

  // --- vorab prüfen, was der Browser schon weiß ---
  if((m==='anmelden' || m==='neu' || m==='vergessen') && !name){
    note.textContent = t(m==='vergessen' ? 'konto.fehler_email' : 'konto.fehler_name'); return;
  }
  if(m==='neu'){
    const nf = nameFehler(name);
    if(nf){ note.textContent = kontoFehlerText(nf); return; }
    if(!/^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$/.test(adr)){
      note.textContent = t('konto.fehler_email'); return;
    }
  }
  if(m==='neu' || m==='neupw'){
    const fehlt = PW_REGELN.find(([, , erfuellt]) => !erfuellt(pw));
    if(fehlt){ note.textContent = kontoFehlerText(fehlt[0]); return; }
    if(pw !== pw2){ note.textContent = t('konto.fehler_wdh'); return; }
  }

  const knopf = $('kontoSenden');
  knopf.disabled = true; note.textContent = t('konto.laeuft');
  try{
    if(m==='neu'){
      const d = await postJSON('/api/konto/anlegen', {name, email: adr, passwort: pw});
      if(!d.ok){ note.textContent = kontoFehlerText(d.fehler); return; }
      kontoWartetAuf = adr;
      zeigeAnmeldung('warten', {behalteName: true, hinweis: d.mail_raus ? '' : t('konto.testbetrieb')});
      $('kontoName').value = name;
      return;
    }
    if(m==='anmelden'){
      const d = await postJSON('/api/konto/anmelden', {kennung: name, passwort: pw, bleiben});
      if(d.ok){ await nachAnmeldung(d); return; }
      if(d.fehler === 'email_offen'){
        kontoWartetAuf = '';
        zeigeAnmeldung('warten', {behalteName: true, hinweis: t('konto.fehler_email_offen')});
        $('kontoName').value = name;
        return;
      }
      note.textContent = kontoFehlerText(d.fehler);
      return;
    }
    if(m==='warten'){
      const d = await postJSON('/api/konto/mail_neu', {kennung: name});
      note.textContent = t('konto.warten_nochmal_raus');
      note.className = 'note feedback ok';
      return;
    }
    if(m==='vergessen'){
      await postJSON('/api/konto/vergessen', {kennung: name});
      // Immer dieselbe Antwort, auch wenn es die Adresse nicht gibt
      note.textContent = t('konto.vergessen_raus');
      note.className = 'note feedback ok';
      $('kontoSpam').hidden = false;      // jetzt gibt es etwas zu suchen
      return;
    }
    if(m==='neupw'){
      const d = await postJSON('/api/konto/neues_passwort', {code: kontoCode, neu: pw, bleiben});
      if(d.ok){ kontoCode=''; geschichteAufraeumen(); await nachAnmeldung(d); return; }
      note.textContent = kontoFehlerText(d.fehler);
      return;
    }
  }catch(err){
    note.textContent = t('konto.fehler_allgemein');
  }finally{
    knopf.disabled = false;
  }
});

/* Dieselben Regeln wie konten.pruefe_name() auf der Serverseite. */
function nameFehler(n){
  if(!n) return 'name_fehlt';
  if(/\s/.test(n)) return 'name_leerzeichen';
  if(n.length < 3) return 'name_kurz';
  if(n.length > 20) return 'name_lang';
  if(!/^[\p{L}\p{N}\-_.]+$/u.test(n) || !/[\p{L}\p{N}]/u.test(n)) return 'name_zeichen';
  return '';
}

/* Den Code aus der Adresszeile nehmen, damit er nicht im Verlauf stehen bleibt. */
function geschichteAufraeumen(){
  try{ history.replaceState(null, '', location.pathname); }catch(e){}
}

/* Kleiner Helfer, damit jeder Aufruf gleich aussieht. */
async function postJSON(pfad, koerper){
  const r = await fetch(pfad, {method:'POST', headers:{'Content-Type':'application/json'},
                               body: JSON.stringify(koerper||{})});
  try{ return await r.json(); }catch(e){ return {ok:false, fehler:'kaputt'}; }
}

async function nachAnmeldung(info){
  profil = info.name || '';
  premium = !!info.premium;
  kontoMail = info.email || '';
  await loadProgress(); aboFruehNachholen(); syncLives(); pruefeSchutz();   // aboFrueh: nach vollversionLaden()
  if(altenFortschrittUmschreiben() | funkelnUmzug()) saveProgress();
  /* Pflicht-Anmeldung (28.10.2026): Sitzung mit der Kopie in der Huelle
     abgleichen und einmal nach einem Restore-Schluessel fragen. Ohne
     Cloud passiert hier nichts. */
  if(cloudModus()) await cloudSitzungAbgleichen();
  /* Das Jahresgeschenk hing bisher allein an tagPruefen() - und das
     schlaegt nur an, wenn die App offen ist, waehrend der Tag wechselt.
     Wer sie abends schliesst und morgens neu oeffnet, kam nie an sein
     Geschenk: letzterTag steht beim Laden schon auf heute. Gefunden am
     29.09.2026, als es um den Geraetewechsel ging. */
  geschenkPruefen();
  /* Der Profilknopf steht seit 14.11.2026 immer da, auch ohne Konto: im
     Profil stehen jetzt die Erfolge, und die gibt es auch in der Web-Demo,
     in der ersten Lektion vor der Pflicht-Anmeldung und auf dem iPhone
     nach "Spaeter". Ohne Konto zeigt showKonto() nur Erfolge und
     Lernserie, ohne den Kasten mit Passwort, E-Mail und Abmelden. Bis dahin
     blieb der Knopf ohne Konto weg (ohne Server, und seit v109 vor der
     Anmeldung). */
  $('btnProfil').style.display = 'inline-block';
  // Kein Name mehr im Knopf, nur die Figur: eine Zeile oben (29.10.2026).
  $('btnSettings').style.display='inline-block';
  $('btnShop').style.display='inline-block';
  homeMode='words'; showHome();
}

async function abmelden(){
  if(cloudModus()) return cloudAbmeldenGanz();     // 28.10.2026
  await saveProgress();
  await postJSON('/api/konto/abmelden', {});
  profil=''; kontoMail=''; known=new Set(); passed=new Set(); read=new Set(); days=new Set(); frost=new Set();
  zeigeAnmeldung('anmelden');
}
/* Bis Version 0.9 merkte sich die App nur das bosnische Wort. Jetzt merkt sie
   sich „bedeutung:wort“, also „hundert:sto“ und „tisch:sto“ getrennt.
   Alter Fortschritt wird beim ersten Öffnen umgeschrieben und geht dabei
   nicht verloren. Erkannt werden beide früheren Schreibweisen: das nackte
   Wort und die Zwischenform „level:wort“. */
/* Woerter, bei denen sich deutsche UND bosnische Seite geaendert haben -
   die Suche unten findet sie sonst nicht wieder. "skup / skupa" war
   mehrdeutig (auch: Treffen, zusammen); mit "skupo" ist klar, dass es
   teuer heisst. Ajdin am 01.10.2026. */
const UMBENANNT = {
  /* Deutsche Bedeutungen mit Umlaut statt ae/oe/ue/ss, Pruefung am
     06.10.2026. Die Kennung haengt an der deutschen Seite; ohne diese
     Zeilen faende die Suche unten das Wort nur ueber das bosnische Wort
     und haengte den Fortschritt an jeden gleichlautenden Eintrag. */
  'hallo (neutral, ueberall):Zdravo': 'hallo (neutral, überall):Zdravo',
  'kueken / haehnchen:pile': 'küken / hähnchen:pile',
  'kraehe:vrana': 'krähe:vrana',
  'baer:medvjed': 'bär:medvjed',
  'eichhoernchen:vjeverica': 'eichhörnchen:vjeverica',
  'muecke:komarac': 'mücke:komarac',
  'fluegel:krilo': 'flügel:krilo',
  'beissen:ugristi': 'beißen:ugristi',
  'beisst er?:Hoće li ujesti?': 'beißt er?:Hoće li ujesti?',
  'fuettern:hraniti': 'füttern:hraniti',
  'gefaehrlich:opasno': 'gefährlich:opasno',
  'hoehle:pećina': 'höhle:pećina',
  'huegel:brdo': 'hügel:brdo',
  'baeckerei:pekara': 'bäckerei:pekara',
  'hurmasica (sirupgebaeck):hurmašica': 'hurmašica (sirupgebäck):hurmašica',
  'rahat lokum (geleewuerfel zum kaffee):rahat lokum': 'rahat lokum (geleewürfel zum kaffee):rahat lokum',
  'tufahija (gefuellter apfel in sirup):tufahija': 'tufahija (gefüllter apfel in sirup):tufahija',
  'burek (blaetterteigrolle mit fleisch):burek': 'burek (blätterteigrolle mit fleisch):burek',
  'dolma (gefuelltes gemuese):dolma': 'dolma (gefülltes gemüse):dolma',
  'geraeuchertes fleisch:suho meso': 'geräuchertes fleisch:suho meso',
  'sirnica (pita mit kaese):sirnica': 'sirnica (pita mit käse):sirnica',
  'zeljanica (pita mit spinat und kaese):zeljanica': 'zeljanica (pita mit spinat und käse):zeljanica',
  'saenger / saengerin:pjevač / pjevačica': 'sänger / sängerin:pjevač / pjevačica',
  'sevdah (wehmuetige sehnsucht):sevdah': 'sevdah (wehmütige sehnsucht):sevdah',
  'teferic (ausflugsfest im gruenen):teferič': 'teferič (ausflugsfest im grünen):teferič',
  'antwort auf den bajram-gruss:Allah razi olsun': 'antwort auf den bajram-gruß:Allah razi olsun',
  'masallah (wie schoen, gott schuetze es):mašallah': 'mašallah (wie schön, gott schütze es):mašallah',
  'danke fuer die einladung:Hvala na pozivu': 'danke für die einladung:Hvala na pozivu',
  'insallah (so gott will):inšallah': 'inšallah (so gott will):inšallah',
  'somun (fladenbrot zu cevapi):somun': 'somun (fladenbrot zu ćevapi):somun','teuer (m/w):skup / skupa': 'teuer (m/w/s):skup / skupa / skupo',
  /* Ajdin am 01.10.2026: "auf einer bosnischen Kaffeepackung steht kafa nicht
     kahva - mach beides rein". */
  'kaffee:kahva': 'kaffee:kahva / kafa',
  'kaffeemaschine:aparat za kahvu': 'kaffeemaschine:aparat za kahvu / aparat za kafu',
  /* Ajdin am 22.10.2026: "die vokabel salz am besten zu so/sol aendern weil
     man es so oder so sagt". Die Suche unten ueber das bosnische Wort
     faende "so" nicht mehr wieder - es heisst jetzt "so / sol". */
  'salz:so': 'salz:so / sol',
  /* Ajdin am 23.10.2026: "tetka ujna strina fuer die verschiedenen tanten
     und striko ujak amidza=stric tetak daidza=ujak usw". Tanten und Onkel
     heissen seitdem nach ihrer Seite, amidža und daidža haben eine zweite
     Form (stric, ujak). Die Suche unten faende amidža und daidža ueber das
     bosnische Wort nicht mehr wieder; tetka und rođak faende sie, aber nur
     solange kein zweites Wort so heisst. */
  'tante:tetka': 'tante (schwester von vater oder mutter):tetka',
  'onkel (vaterseite):amidža': 'onkel (bruder des vaters):amidža / stric',
  'onkel (mutterseite):daidža': 'onkel (bruder der mutter):daidža / ujak',
  'cousin:rođak': 'cousin, verwandter (allgemein):rođak',
  /* Ajdin am 06.11.2026: "mach doktor/ ljekar", "dozvoliti/dopustiti". Kein
     zweites Wort mit derselben Bedeutung, sondern eine zweite Form wie bei
     kahva / kafa; die Suche unten faende das alte bosnische Wort nicht mehr. */
  'arzt:doktor': 'arzt:doktor / ljekar',
  'erlauben:dozvoliti': 'erlauben / zulassen:dozvoliti / dopustiti',
  'erlauben:dozvoljavati': 'erlauben / zulassen:dozvoljavati / dopuštati',
  /* Ajdin am 07.11.2026 (Wortschatz-Pakete 10 bis 20): iznajmiti heisst jetzt
     "vermieten", mieten ist unajmiti (b2_2_entscheidungen.md, Paket 15 Nr. 113).
     Aus produžni kabl wird produžni kabel ("kabel", Nachfrage 6 B), zaposlenik
     bekommt die zweite Form uposlenik wie doktor / ljekar. Die Suche unten
     faende das alte bosnische Wort bei den beiden letzten nicht mehr. */
  'mieten:iznajmiti': 'vermieten:iznajmiti',
  'verlängerungskabel:produžni kabl': 'verlängerungskabel:produžni kabel',
  'arbeitnehmer:zaposlenik': 'arbeitnehmer:zaposlenik / uposlenik',
  /* Pruefbericht 1.4 (14.11.2026), B9: Alejkumu selam hiess "(Antwort darauf)" und
     stand seit dem alphabetischen Einsortieren vor Selam alejkum - die Bedeutung
     verwies ins Leere. Jetzt "Antwort auf Selam alejkum". Die Suche unten faende
     es heute auch ueber das bosnische Wort, aber nur, solange kein zweites Wort
     so heisst - hier steht es fest, fuer gewusst, Fehler-Topf und Sterne. */
  '(antwort darauf):Alejkumu selam': 'antwort auf selam alejkum:Alejkumu selam',
  /* Pruefbericht 1.4 (14.11.2026), B6: Minze hiess "nana (auch: metvica)", mit dem
     deutschen "auch" im bosnischen Knopf. Ajdin (F17 b): "nana / metvica" wie kahva /
     kafa. Die Suche unten faende das alte bosnische Wort nicht mehr. */
  'minze:nana (auch: metvica)': 'minze:nana / metvica',
  /* Pruefbericht 1.4 (14.11.2026), S2: Ajdin (F19) "kolegica ist [richtig] nicht
     koleginica", "ne sofort umstellen". Neuer Ton von Emir (w8953), die alte Aufnahme
     bleibt wie bei produžni kabl in index.json. Die Suche unten faende das alte
     bosnische Wort nicht mehr. */
  'kollegin:koleginica': 'kollegin:kolegica'};
/* Dasselbe fuer Saetze (25.10.2026): Fehler-Topf und Sterne merken sich
   einen Satz als "s:<Level>|<Lueckentext>" bzw. "k:<Level>|<Satz>"
   (topfSchluessel). Aendert sich der bosnische Text, fuehrt der alte
   Schluessel zu keiner Aufgabe mehr - topfAufraeumen() und
   sternUmschreiben() warfen ihn still weg. Hier steht, wohin er zieht.
   Ajdin am 25.10.2026 zu "Dva plus dva je četiri.": "Auf „su“ ändern" -
   bei dva, tri, četiri im Subjekt steht das Verb im Plural (Gramatika
   bosanskoga jezika, § 241). */
const SAETZE_UMBENANNT = {
  'k:zahlen|Dva plus dva je četiri.': 'k:zahlen|Dva plus dva su četiri.',
  /* 13.11.2026, Stufen-Reiter: Zuhause steht hinter Faelle 1. Sechs
     Satzbau-Saetze brauchten Woerter von dort (tanjir, alat, punjač,
     parkirati, und zvati ueber nazvati) und ziehen in das erste Level, in
     dem jede Kachel bekannt ist: vier nach Zuhause, die zwei mit "se zove"
     nach Faelle 1 (dort steht zvati). Der Satz bleibt. */
  'k:genus|Ovo je moj tanjir.': 'k:kueche_bad|Ovo je moj tanjir.',
  'k:genus|Gdje je moj alat?': 'k:technik|Gdje je moj alat?',
  'k:genus|Gdje je moj punjač?': 'k:geraete|Gdje je moj punjač?',
  'k:genus|Moja sestra se zove Amina.': 'k:faelle1|Moja sestra se zove Amina.',
  'k:genus|Moj muž se zove Ajdin.': 'k:faelle1|Moj muž se zove Ajdin.',
  'k:faelle1|Gdje mogu parkirati svoj auto?': 'k:auto_werkstatt|Gdje mogu parkirati svoj auto?',
  /* Pruefbericht 1.4 (14.11.2026), S2: koleginica heisst kolegica (Ajdin, F19). Der
     Lueckensatz "Ovo je moja ___." behaelt seinen Schluessel, nur die Antwort wechselt. */
  'k:kennenlernen|Ovo je moja koleginica.': 'k:kennenlernen|Ovo je moja kolegica.'};
/* Ob ein Satz-Schluessel umgezogen ist: nur wenn der alte zu keiner Aufgabe
   mehr fuehrt und der neue zu einer. hasOwnProperty, damit "constructor"
   aus einer Sicherung nichts findet. */
const satzUmbenannt = k => Object.prototype.hasOwnProperty.call(SAETZE_UMBENANNT, k)
  && !topfAufgabe(k, {typ: 'mc'}) && !!topfAufgabe(SAETZE_UMBENANNT[k], {typ: 'mc'});
function altenFortschrittUmschreiben(){
  const gueltig = new Set(), nachWort = new Map(), nachLevel = new Map();
  CATEGORIES.forEach(c => c.words.forEach(w => {
    gueltig.add(w.id);
    if(!nachWort.has(w.bs)) nachWort.set(w.bs, []);
    nachWort.get(w.bs).push(w.id);
    nachLevel.set(c.id + ':' + w.bs, w.id);
  }));
  const neu = new Set(); let geaendert = false;
  known.forEach(x => {
    if(istZa(x)){ neu.add(x); return; }     // Beim Zahnarzt: nie auf ein Wort des Lernpfads umschreiben
    if(UMBENANNT[x] && gueltig.has(UMBENANNT[x])){ neu.add(UMBENANNT[x]); geaendert = true; }
    else if(gueltig.has(x)) neu.add(x);
    else if(nachLevel.has(x)){ neu.add(nachLevel.get(x)); geaendert = true; }
    else if(nachWort.has(x)){ nachWort.get(x).forEach(id => neu.add(id)); geaendert = true; }
    else if(nachWort.has(x.slice(x.lastIndexOf(':') + 1))){
      /* Die Kennung eines Wortes ist "deutsch:bosnisch" (start.py). Wird die
         deutsche Seite berichtigt - "Notarzt" war für "hitna pomoć" falsch,
         das ist der Rettungsdienst -, ändert sich damit die Kennung, und ein
         gelerntes Wort gälte plötzlich wieder als ungelernt. Der bosnische
         Teil bleibt. Also am LETZTEN Doppelpunkt trennen: zehn deutsche
         Einträge enthalten selbst einen ("Anrede: Bruder!"), kein einziger
         bosnischer. Geprüft über alle 1108 Wörter. */
      nachWort.get(x.slice(x.lastIndexOf(':') + 1)).forEach(id => neu.add(id));
      geaendert = true;
    }
    else neu.add(x);          // unbekannt, zum Beispiel ein gelöschtes Wort
  });
  if(geaendert) known = neu;
  /* Die Sterne haengen an denselben Kennungen (19.10.2026). Erst
     ausrechnen, dann verknuepfen - mit || liefe es nach einer
     Wort-Umschreibung gar nicht mehr. */
  const sternNeu = sternUmschreiben(nachWort);
  /* Der Fehler-Topf ebenso (22.10.2026). Bis dahin zog hier nur known um,
     und topfAufraeumen() warf "w:salz:so" beim naechsten Oeffnen von
     Wiederholen still weg - ein offener Fehler waere ohne Wiederholung
     verschwunden. Gefunden beim Umbenennen von Salz auf "so / sol". */
  const topfNeu = topfUmschreiben(nachWort);
  /* Die Lernkartei ebenso (29.10.2026). Danach bekommt jedes gewusste
     Wort ohne Termin einen: beim ersten Start mit v110 alle, spaeter die
     aus einer alten Sicherungsdatei oder von einem Geraet mit v109. */
  const karteiNeu = karteiUmschreiben(nachWort);
  const karteiDazu = karteiNachtragen();
  return geaendert || sternNeu || topfNeu || karteiNeu || karteiDazu;
}

// Der Knopf mit der Figur oben rechts führt in die Kontoseite -
// dort steht auch das Abmelden. (Bis 29.10.2026 stand der Name darin.)
$('btnProfil').addEventListener('click', async ()=>{ await saveProgress(); showKonto(); });

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
