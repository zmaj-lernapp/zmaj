/* ---- Passwort ändern ---- */
$('setPwAuf').addEventListener('click', ()=>{
  const f=$('pwForm'); const auf = f.style.display==='none';
  f.style.display = auf ? 'block' : 'none';
  $('pwNote').textContent=''; $('pwNote').className='note';
  $('pwAlt').value=$('pwNeu').value=$('pwNeu2').value='';
  zeigeRegeln($('pwRegeln'), '');
  if(auf) $('pwAlt').focus();
});
$('pwNeu').addEventListener('input', e=> zeigeRegeln($('pwRegeln'), e.target.value));
$('pwForm').addEventListener('submit', async e=>{
  e.preventDefault();
  const alt=$('pwAlt').value, neu=$('pwNeu').value, neu2=$('pwNeu2').value;
  const fehlt = PW_REGELN.find(([, , erfuellt]) => !erfuellt(neu));
  if(fehlt){ $('pwNote').textContent=kontoFehlerText(fehlt[0]); $('pwNote').className='note feedback no'; return; }
  if(neu!==neu2){ $('pwNote').textContent=t('konto.fehler_wdh'); $('pwNote').className='note feedback no'; return; }
  $('pwNote').textContent = t('konto.laeuft'); $('pwNote').className='note';
  const d = await postJSON('/api/konto/passwort', {alt, neu});
  if(d.ok){
    $('pwAlt').value=$('pwNeu').value=$('pwNeu2').value='';
    $('pwNote').textContent = t('set.passwort_ok');
    $('pwNote').className = 'note feedback ok';
    sound('ok');
  } else {
    $('pwNote').textContent = kontoFehlerText(d.fehler);
    $('pwNote').className = 'note feedback no';
  }
});

/* ---- Konto löschen ---- */
$('setKontoWeg').addEventListener('click', ()=>{
  if(cloudModus()) return kontoWegKlick();     // 28.10.2026
  const f=$('wegForm'); const auf = f.style.display==='none';
  f.style.display = auf ? 'block' : 'none';
  $('wegNote').textContent=''; $('wegPw').value='';
  if(auf) $('wegPw').focus();
});
$('wegForm').addEventListener('submit', async e=>{
  e.preventDefault();
  if(cloudModus()) return cloudKontoLoeschen($('wegPw').value);     // 28.10.2026
  if(!confirm(t('set.konto_loeschen_frage',{name:profil}))) return;
  const d = await postJSON('/api/konto/loeschen', {passwort: $('wegPw').value});
  if(d.ok){
    $('wegPw').value=''; $('wegForm').style.display='none';
    profil=''; known=new Set(); passed=new Set(); read=new Set(); days=new Set(); frost=new Set();
    zeigeAnmeldung('anmelden');
  } else $('wegNote').textContent = kontoFehlerText(d.fehler);
});
/* ===== Sicherung =====
   Ohne Server liegt der Lernstand nur im Speicher dieses Browsers. Geht das
   Handy kaputt oder wird die App geloescht, ist er weg. Deshalb zum
   Mitnehmen als Datei.

   Auf Android reicht ein gewoehnlicher Download NICHT - eine WebView laedt
   nichts herunter, der Knopf bliebe wirkungslos. Dort schreiben wir die
   Datei ueber Capacitor in den Zwischenspeicher und reichen sie ans
   Teilen-Menue weiter; der Nutzer schickt sie sich dann selbst zu oder legt
   sie in seine Cloud. Im Browser am PC bleibt es beim normalen Download. */
/* Die Datei als Objekt. Die Cloud-Sicherung speichert genau dieses JSON
   (ohne Einrueckung), damit ein Stand aus der Cloud auch als Datei
   eingelesen werden kann und umgekehrt. 19.10.2026 */
function sicherungObjekt(stand){
  return {app:'zmaj', version:1,
          datum:new Date().toISOString().slice(0,10),
          stand: stand || standAlsObjekt()};
}
function sicherungInhalt(){
  return JSON.stringify(sicherungObjekt(), null, 1);
}
/* Der Lernstand aus einer Sicherung, oder null, wenn es keine ist. */
function sicherungStandAus(d){
  // typeof [] ist auch 'object'. Eine Datei mit "stand": [] kaeme sonst
  // durch und wuerde den Lernstand nicht ersetzen, sondern loeschen.
  if(!d || d.app !== 'zmaj' || !d.stand || typeof d.stand !== 'object' || Array.isArray(d.stand)) return null;
  return d.stand;
}
/* Einen neuen Stand uebernehmen - mit Rueckweg. machen() liefert ihn und
   laeuft schon innerhalb der Absicherung. Gibt zurueck, ob es geklappt hat.
   Gebraucht beim Einlesen einer Datei und seit 19.10.2026 beim
   Zusammenfuehren mit der Cloud (cloudUebernehmen). */
function standErsetzen(machen){
  /* Wirft das Uebernehmen trotz der Pruefungen in standUebernehmen(), kommt
     der alte Stand zurueck - sonst speicherte das naechste saveProgress()
     einen halb uebernommenen. import_richten.py, 04.10.2026. */
  const vorher = standAlsObjekt();
  /* standUebernehmen() schreibt Geschenkjahr und getragenes Stueck sofort
     in den Geraetespeicher. Beim Zuruecknehmen muessen die mit zurueck,
     sonst verbraucht eine abgelehnte Datei das Jahresgeschenk. */
  const geschenkVorher = Object.assign({}, geschenk), getragenVorher = getragen;
  /* Ebenso gewusstGeladen: zurueck kommt hier der laufende Stand, kein
     geladener - fuers Tor zaehlte sonst ein halb gelerntes Wort. */
  const gewusstVorher = gewusstGeladen;
  try{ standUebernehmen(machen()); altenFortschrittUmschreiben(); return true; }
  catch(e){ standUebernehmen(vorher); altenFortschrittUmschreiben();
           geschenk = geschenkVorher; getragen = getragenVorher; gewusstGeladen = gewusstVorher;
           try{ localStorage.setItem(GESCHENK_SCHLUESSEL, JSON.stringify(geschenk));
                localStorage.setItem('zmaj_getragen', getragen); }catch(e2){}
           return false; }
}
function sicherungName(){ return 'zmaj-sicherung-' + new Date().toISOString().slice(0,10) + '.json'; }

async function sicherungSpeichern(){
  const note = $('sichNote'); note.textContent = '';
  const text = sicherungInhalt(), name = sicherungName();
  const P = window.Capacitor && window.Capacitor.Plugins;
  try{
    if(P && P.Filesystem && P.Share){
      await P.Filesystem.writeFile({path:name, data:text, directory:'CACHE', encoding:'utf8'});
      const ort = await P.Filesystem.getUri({path:name, directory:'CACHE'});
      /* Teilen-Menue ohne Auswahl geschlossen: das Plugin lehnt mit
         "Share canceled" ab. Bis zum 07.10.2026 stand dann "Das hat nicht
         geklappt." da, und man hielt die Sicherung fuer kaputt. Gespeichert
         ist trotzdem nichts - die Datei liegt nur im Zwischenspeicher der
         App -, also ein ruhiger Hinweis statt der Fehlermeldung.
         Grenze des Plugins: Geht das gewaehlte Ziel nur als Fenster
         ueber der App auf, wird die App nicht gestoppt, und es meldet
         ebenfalls "Share canceled". Das laesst sich hier nicht
         unterscheiden. */
      try{ await P.Share.share({title:t('set.sicherung'), url:ort.uri}); }
      catch(e){
        if(/cancel/i.test(String((e && e.message) || e))){ note.textContent = t('set.sicherung_abgebrochen'); return; }
        throw e;
      }
    } else {
      const a = document.createElement('a');
      const adresse = URL.createObjectURL(new Blob([text], {type:'application/json'}));
      a.href = adresse; a.download = name; a.click();
      setTimeout(()=>URL.revokeObjectURL(adresse), 4000);
    }
    /* Der Dateiname gehoert in die Meldung. Wo die Sicherung landet,
       entscheidet der Nutzer im Teilen-Menue - ohne den Namen weiss er
       hinterher nicht, wonach er in der Dateiverwaltung suchen soll.
       Aufgefallen am 25.09.2026 beim Pruefdurchlauf P12. Der Name ist
       sprachneutral, deshalb braucht es dafuer keinen neuen Text. */
    note.textContent = t('set.sicherung_ok') + ' ' + name; sound('ok');
  }catch(e){ note.textContent = t('set.sicherung_fehler'); }
}
async function sicherungEinlesen(datei){
  const note = $('sichNote'); note.textContent = '';
  let d;
  try{ d = JSON.parse(await datei.text()); }
  catch(e){ note.textContent = t('set.sicherung_keine'); return; }
  // Die Pruefung der Form steht in sicherungStandAus() (19.10.2026).
  if(!sicherungStandAus(d)){
    note.textContent = t('set.sicherung_keine'); return;
  }
  if(!await frage(t('set.sicherung'), t('set.sicherung_frage'),
                  t('btn.ersetzen'), t('btn.dialog_abbrechen'))) return;
  /* Der Rueckweg, falls das Uebernehmen wirft, steht seit 19.10.2026 in
     standErsetzen() - die Cloud-Sicherung braucht ihn genauso.
     sicherungPlausibel(): Lerntage nur von APP_START bis heute, Muenzen nur
     so viele, wie sich damit verdienen lassen, Zierrat nur so viel, wie
     diese Muenzen bezahlen (17.10.2026). */
  if(!standErsetzen(() => sicherungPlausibel(d.stand))){
    note.textContent = t('set.sicherung_keine'); return;
  }
  /* Dieselbe Umschreibung wie beim normalen Start (nachAnmeldung). Die
     Kennung eines Wortes ist "bedeutung:wort"; wird eine deutsche Bedeutung
     berichtigt, aendert sich die Kennung mit. Eine Sicherung von vor der
     Berichtigung brachte darum Kennungen mit, die es nicht mehr gibt: die
     Woerter hatten keinen Lautsprecher mehr, die Levelbalken fielen zurueck,
     die naechste Lektion bot sie als neu an - und die Meldung darunter
     zaehlte sie ueber known.size trotzdem mit. Erst ein Neustart richtete es.
     Fall: hitna pomoc, "Notarzt" -> "Rettungsdienst". Gefunden am 26.09.2026. */
  seitNachEinlesen();
  /* Gleich nachsehen statt erst beim naechsten Kaltstart: die Sicherung
     kann einen viel frueheren Anfang mitbringen, und dann ist das Geschenk
     in diesem Augenblick faellig. */
  geschenkPruefen();
  syncLives(); pruefeSchutz();
  const gesichert = await saveProgress();
  renderLives();
  note.textContent = gesichert
    ? t('set.sicherung_geladen', {woerter: ohneZa(known), tage: days.size})
    : t('set.sicherung_fehler');
  sound(gesichert ? 'ok' : 'no');
}
$('sichSpeichern').addEventListener('click', sicherungSpeichern);
$('sichLaden').addEventListener('click', ()=> $('sichDatei').click());
$('sichDatei').addEventListener('change', async e=>{
  const datei = e.target.files && e.target.files[0];
  e.target.value = '';          // damit dieselbe Datei nochmal gewaehlt werden kann
  if(datei) await sicherungEinlesen(datei);
});

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
