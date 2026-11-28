/* ===================== Die Vollversion als Abo =====================
   Gekauft wird bei Google, nicht bei uns. Das eigene Plugin ZmajAbo spricht
   mit der Play-Abrechnung; warum selbst geschrieben und welche Fallen darin
   umgangen sind, steht ausführlich in ZmajAbo.java.

   Wichtigste Regel hier oben: Google ist die einzige Wahrheit. Der gemerkte
   Stand im Gerätespeicher wird NUR überschrieben, wenn Google wirklich
   geantwortet hat. Sonst säße ein zahlender Nutzer im Flugzeug plötzlich
   wieder vor Werbung. */
const aboPlugin = () => (window.Capacitor && window.Capacitor.Plugins
                         && window.Capacitor.Plugins.ZmajAbo) || null;
function vollversionGemerkt(){
  try{ return localStorage.getItem(VOLL_SCHLUESSEL) === '1'; }catch(e){ return false; }
}
let aboLaeuft = false;        // gerade eine Abfrage oder ein Kauf unterwegs
let aboStoerung = false;      // Play Store hat zuletzt nicht geantwortet
/* Das Abo ist da, aber Google hat es gesperrt: Zahlung geplatzt oder
   pausiert. Zaehlt nicht als Vollversion, bekommt aber einen Hinweis und
   den Weg zu Googles Abo-Seite statt eines neuen Kaufkastens. Bis Build 96
   wurde so jemand still zum Gratisnutzer. 07.10.2026 */
let aboGesperrt = false;
/* Google hat geantwortet, kennt die Produkte aber nicht. Das ist etwas
   anderes als eine Stoerung: hier ist die Antwort eindeutig, es gibt gerade
   nichts zu kaufen. Solange die Abos in der Play Console nicht angelegt und
   freigeschaltet sind, ist das der Normalfall. */
let aboProdukteFehlen = false;
/* Der Plan, dessen Testwoche die Kauf-Einstiege nennen, siehe gratisMerken(). */
let aboGratisPlan = null;
/* Der Basisplan des laufenden Abos, wie ZmajAbo ihn sich beim Kauf gemerkt
   hat: 'monat', 'jahr' oder null (unbekannt). Google selbst verraet ihn der
   App nicht, siehe planVon() in ZmajAbo.java. Nur bei 'monat' gibt es
   "Auf jaehrlich wechseln", und der Jahrespreis dafuer kommt wie im
   Kaufkasten aus preise(). 10.10.2026 */
let aboPlan = null;
let aboJahrPreis = '';

function vollMeldung(text){
  const el = $('setVollNote'); if(!el) return;
  el.textContent = text || '';
}
function vollZeileZeigen(){
  const box = $('setVollBox'); if(!box) return;
  const an = premium;
  /* Zeigen, wenn es etwas zu kaufen gibt ODER die Vollversion schon laeuft.
     Das "kaufbar" muss hier noch einmal geprueft werden: diese Funktion
     laeuft auch am PC, wo es das Plugin gar nicht gibt - ohne die Pruefung
     wuerde der Block dort auftauchen. */
  /* Bei einem gesperrten Abo auch dann, wenn Google gerade nichts zu
     kaufen anbietet: hier stehen der Hinweis und der Weg zu Google.
     07.10.2026 */
  /* Der Block selbst bleibt mit dem Plugin immer stehen, nur die Kaufzeile
     geht: Darin steht der Widerrufsknopf, und § 356a Abs. 1 BGB verlangt ihn
     waehrend der Frist staendig verfuegbar, also auch dann, wenn Google gerade
     keine Produkte liefert (Pruefbericht 1.3, G15). */
  box.style.display = aboPlugin() ? '' : 'none';
  $('setVollKauf').style.display = (an || aboGesperrt || !aboProdukteFehlen) ? '' : 'none';
  const s = $('swVoll');
  s.setAttribute('aria-checked', an);
  /* aria-disabled statt disabled: ein disabled-Knopf nimmt keinen Tipp mehr
     an - der Tipp soll aber zu Googles Abo-Seite führen. */
  s.setAttribute('aria-disabled', an);
  $('setVollStand').textContent = an ? t('voll.aktiv')
    : aboGesperrt ? t('voll.gesperrt')
    : (geschenkLaeuft() ? t('voll.geschenk_rest', {n: geschenkRest()})
    : (aboLaeuft ? t('voll.laedt') : (aboStoerung ? t('voll.kein_store') : '')));
  const v = $('setVollVerwalten');
  /* Auch bei einer Störung zeigen: wer zahlt, aber gerade keine Antwort vom
     Play Store bekommt, fände sonst keinen Kündigungsweg - und einen in der
     App verlangt Google. Ebenso bei einem gesperrten Abo: dort repariert
     man die Zahlung (07.10.2026). */
  v.style.display = (an || aboStoerung || aboGesperrt) ? '' : 'none';
  $('aboVerwalten').textContent = t('voll.verwalten');
  /* "Kaeufe wiederherstellen" nur auf iOS, und nur ohne laufende
     Vollversion - wer sie hat, braucht nichts wiederherzustellen.
     30.10.2026 */
  const wh = $('setVollWiederherstellen');
  if(wh){
    wh.style.display = (IST_IOS && !an) ? '' : 'none';
    $('aboWiederherstellen').textContent = t('voll.wiederherstellen');
  }
  /* Wechsel aufs Jahr: nur mit einem laufenden Monatsabo laut Google, nicht
     gesperrt, ohne Stoerung und nur mit Preis. premium allein reicht nicht,
     das setzt auch der Dauerschalter. 10.10.2026 */
  const w2 = $('setVollWechsel');
  if(w2){
    const zeigen = aboPlan === 'monat' && !aboGesperrt && !aboStoerung && !!aboJahrPreis;
    w2.style.display = zeigen ? '' : 'none';
    $('aboWechsel').textContent = zeigen
      ? t('voll.wechsel') + ' · ' + t('voll.pro_jahr', {preis: aboJahrPreis}) : '';
  }
  const w = $('widerrufKnopf');
  if(w) w.textContent = t('set.widerruf_knopf');
}
/* Die zuletzt gestartete Abfrage. vollKaufOeffnen() wartet auf sie: solange
   sie laeuft, steht aboLaeuft, und vollWahlZeigen() bricht still ab.
   07.10.2026 */
let aboAbgleich = null;
function vollAbgleichen(){ return (aboAbgleich = vollAbgleichenJetzt()); }
/* Fragt Google. Ändert den gemerkten Stand nur bei einer echten Antwort. */
async function vollAbgleichenJetzt(){
  const P = aboPlugin(); if(!P) return;
  aboLaeuft = true; vollZeileZeigen();
  let d = null;
  try{ d = await P.stand(); }catch(e){}
  aboLaeuft = false;
  if(d && d.bekannt){
    aboStoerung = false;
    aboGesperrt = !!d.gesperrt && !d.aktiv;
    aboPlanSetzen(d);
    /* Nicht nur die Leben: mit der Vollversion gehen auch ihre Stuecke
       an oder aus. Ohne das neue Zeichnen funkelte der Drache nach dem
       Auslaufen weiter, bis der Nutzer den Schirm wechselte. */
    if(!!d.aktiv !== premium){
      vollversionMerken(!!d.aktiv); renderLives(); drachenNeu(); renderLaden();
    }
  }else{
    aboStoerung = true;   // gemerkten Stand stehen lassen
  }
  vollZeileZeigen();
}
/* Fragt einmal nach, ob es ueberhaupt etwas zu kaufen gibt.

   Ohne diese Abfrage stuende der Block da und meldete erst beim Antippen
   einen Fehler. Sie kostet nichts Sichtbares: Play Billing beantwortet sie
   vom Geraet aus, und wenn sie schiefgeht, bleibt alles, wie es war -
   lieber ein Block zu viel als einer zu wenig. */
async function produkteNachsehen(){
  const P = aboPlugin(); if(!P || premium) return;
  let d = null;
  try{ d = await P.preise(); }catch(e){ return; }
  if(!d || !d.ok) return;                      // keine Antwort: nichts aendern
  aboProdukteFehlen = !d.plaene || !d.plaene.length;
  gratisMerken(d.plaene);
  vollZeileZeigen();
}
/* Merkt sich den Plan aus einer Antwort von ZmajAbo und holt fuer ein
   Monatsabo den Jahrespreis. produkteNachsehen() fragt bei laufendem Abo
   nicht nach Preisen, deshalb hier eigens. Das frischt zugleich die
   ProductDetails im Plugin auf, die aufJahrWechseln() braucht. 10.10.2026
   In der Gratiswoche (d.probe) bleibt der Plan unbekannt: dort gibt es
   keinen bezahlten Monat, dessen Rest der Wechsel anhaengen koennte, und
   Google buchte sofort den Jahrespreis ab. Die Zeile kommt, sobald die
   Gratiswoche vorbei ist, siehe probeLaeuft() in ZmajAbo.java. 11.10.2026 */
function aboPlanSetzen(d){
  aboPlan = (d && d.aktiv && !d.probe && (d.plan === 'monat' || d.plan === 'jahr')) ? d.plan : null;
  if(aboPlan === 'monat') jahrPreisHolen();
}
async function jahrPreisHolen(){
  const P = aboPlugin(); if(!P) return;
  let d = null;
  try{ d = await P.preise(); }catch(e){ return; }
  if(!d || !d.ok || !d.plaene) return;          // keine Antwort: nichts aendern
  const jahr = d.plaene.find(p => p.plan === 'jahr') || {};
  aboJahrPreis = jahr.preis || '';
  vollZeileZeigen();
}

/* Die Testwoche. Bis Build 94 kaufte ZmajAbo immer den nackten Basisplan,
   ein in der Play Console angelegtes "7 Tage kostenlos" kam nie an. Jetzt
   nimmt es das Gratisangebot, wenn Google dem Nutzer eins anbietet, und
   meldet dessen Dauer als "gratis" (ISO 8601: P7D, P1W, P8W4D ...).
   Dauer und Preis danach stehen VOR dem Kaufknopf, sonst weiss niemand,
   wann zum ersten Mal abgebucht wird. Google erlaubt drei Tage bis drei
   Jahre, der Text braucht also nur die Mehrzahl; Monate und Jahre werden
   ab heute in Tage umgerechnet. Gefunden bei der Pruefung am 06.10.2026.
   Seit 07.10.2026 stehen beide hier draussen statt in vollWahlZeigen():
   auch die Kauf-Einstiege im Laden und auf den Schirmen ohne Leben
   nennen die Testwoche - mit demselben Text, und nur, wenn Google sie
   diesem Nutzer anbietet. */
function gratisTage(iso){
  const m = /^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?$/.exec(iso || '');
  if(!m) return 0;
  const h = new Date(), heute = Date.UTC(h.getFullYear(), h.getMonth(), h.getDate());
  const zielJahr = h.getFullYear() + (+m[1] || 0), zielMonat = h.getMonth() + (+m[2] || 0);
  // 31. Januar plus ein Monat ist der 28. Februar, nicht der 3. Maerz
  const letzter = new Date(Date.UTC(zielJahr, zielMonat + 1, 0)).getUTCDate();
  const ende = Date.UTC(zielJahr, zielMonat,
                        Math.min(h.getDate(), letzter) + 7 * (+m[3] || 0) + (+m[4] || 0));
  return Math.round((ende - heute) / 86400000);
}
function gratisText(p){
  if(!p) return '';
  const n = gratisTage(p.gratis);
  if(!n || !p.preis) return '';
  return p.plan === 'jahr' ? t('voll.gratis_jahr', {n: n, preis: p.preis})
                           : t('voll.gratis_monat', {n: n, preis: p.preis});
}
/* Der Plan, den der Kaufkasten vorauswaehlt: das Jahr, sonst der Monat.
   Nur dessen Testwoche nennen die Einstiege - sonst stuende dort "gratis",
   und im Kasten waere eine Karte ohne Testwoche gewaehlt. 07.10.2026 */
function gratisMerken(plaene){
  const hol = id => (plaene || []).find(p => p.plan === id) || {};
  const jahr = hol('jahr');
  aboGratisPlan = jahr.preis ? jahr : hol('monat');
}
/* Macht den Kaufkasten nur so eng wie noetig, siehe .kaufknoepfe im Stil.
   Gemessen statt nach Bildschirmhoehe gestaffelt: wie viel Platz er braucht, haengt
   auch von der Sprache und der Systemschrift ab. Der Drache faellt zuerst kleiner
   aus und dann ganz weg - weg heisst aus dem Baum, sonst baut ihn der Beobachter
   unter mountZmaj() trotzdem auf, und er rechnet unsichtbar mit. */
function kaufkastenEinpassen(box){
  const zuHoch = () => box.scrollHeight > box.clientHeight;
  if(zuHoch()) box.classList.add('eng1');
  if(zuHoch()){
    box.classList.add('eng2');
    const vorschau = box.querySelector('.abovorschau');
    if(vorschau) vorschau.remove();
  }
  if(zuHoch()) box.classList.add('eng3');
  box.classList.toggle('rollt', zuHoch());
}
/* Die Auswahl Monat oder Jahr. Preise und Zeiträume kommen von Google. */
async function vollWahlZeigen(){
  const P = aboPlugin(); if(!P || aboLaeuft) return;
  aboLaeuft = true; vollMeldung(''); vollZeileZeigen();
  let d = null;
  try{ d = await P.preise(); }catch(e){}
  aboLaeuft = false; vollZeileZeigen();
  if(d && d.ok && (!d.plaene || !d.plaene.length)){
    /* Eindeutige Antwort: es gibt nichts zu kaufen. Keine Fehlermeldung -
       die Kaufzeile geht einfach weg, der Widerrufsknopf bleibt. */
    aboProdukteFehlen = true; aboStoerung = false; vollZeileZeigen(); return;
  }
  if(!d || !d.ok){
    aboStoerung = true; vollZeileZeigen(); vollMeldung(t('voll.fehler')); return;
  }
  aboStoerung = false; aboProdukteFehlen = false;
  gratisMerken(d.plaene);
  /* Erst hier der Kaufkasten - und nur, wenn die Einstellungen noch offen
     sind. Google braucht fuer preise() eine bis mehrere Sekunden; wer in
     dieser Zeit mit der Zurueck-Taste weiterging, bekam "Vollversion holen"
     mit "Zahlungspflichtig abonnieren" ueber den Lernpfad gelegt, samt
     frageSchliessen: die Zurueck-Taste schloss danach erst diesen Kasten
     statt das, was er vor sich hatte. Googles Antwort ist oben trotzdem
     ausgewertet, nur gefragt wird nicht mehr. Gefunden am 26.09.2026. */
  if(!sichtbar('settingsView')) return;
  const hol = id => d.plaene.find(p => p.plan === id) || {};
  const monat = hol('monat'), jahr = hol('jahr');
  /* Die Ersparnis rechnet die App aus, damit sie in jeder Währung stimmt.
     Nur zeigen, wenn beide Preise da sind und es wirklich günstiger ist. */
  let sparen = 0;
  if(monat.micros && jahr.micros){
    sparen = Math.round(100 - (jahr.micros / 12) / monat.micros * 100);
  }
  /* Was das Jahr im Monat kostet. Google liefert nur den Jahrespreis,
     und 19,99 durch zwoelf rechnet im Laden niemand nach. Die Waehrung
     kommt aus derselben Antwort, damit es in jedem Land stimmt. */
  let proMonat = '';
  if(jahr.micros && jahr.waehrung){
    try{
      proMonat = new Intl.NumberFormat(undefined, {style: 'currency', currency: jahr.waehrung})
                   .format(jahr.micros / 12 / 1000000);
    }catch(e){ proMonat = ''; }
  }
  /* Die Testwoche: gratisTage() und gratisText() stehen seit 07.10.2026
     vor vollWahlZeigen(), die Kauf-Einstiege brauchen sie auch. */
  /* Die Karte WAEHLT nur aus. Gekauft wird mit dem Knopf darunter, und der
     heißt "Zahlungspflichtig abonnieren".

     Das ist kein Schönheitsfehler: § 312j Abs. 3 BGB verlangt für eine
     zahlungspflichtige Bestellung genau diese oder eine gleich eindeutige
     Beschriftung, und nach EuGH C-249/21 zählt allein der Text auf der
     Schaltfläche - nicht, was daneben oder darüber steht. Das OLG
     Düsseldorf hat am 08.02.2024 entschieden, dass "Abonnieren" oder
     "Weiter zur Zahlung" dafür nicht reichen. Eine Karte mit "Jährlich" und
     einem Preis erst recht nicht. */
  const karte = (p, name, abzeichen, zweite) =>
    '<button type="button" class="abokarte" role="radio" aria-checked="false"'+
      ' data-plan="'+esc(p.plan)+'"'+(p.preis?'':' disabled')+'>'+
      '<span><span class="n">'+esc(name)+'</span>'+
        (abzeichen || zweite ? '<br><span class="abospar">'+esc(abzeichen)+
          (zweite ? '<span class="promonat">'+esc(zweite)+'</span>' : '')+'</span>' : '')+'</span>'+
      '<span class="p">'+esc(p.preis || '–')+'</span>'+
    '</button>';
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage';
  kasten.innerHTML =
    '<div class="nachfragebox kaufbox">' +
      '<h3>'+esc(t('voll.wahl_titel'))+'</h3>' +
      '<div class="abovorschau">' + zmaj('cheer') +
        '<div class="wort">' + esc(t('voll.so_koenntest_du')) + '</div></div>' +
      '<div class="txt">'+esc(t('voll.wahl_text'))+'</div>' +
      '<div class="abowahl" role="radiogroup">' +
        karte(monat, t('voll.monat'), '', '') +
        karte(jahr, t('voll.jahr'),
              sparen > 0 ? tp('voll.sparen', sparen) : '',
              proMonat ? t('voll.pro_monat', {preis: proMonat}) : '') +
      '</div>' +
      '<div class="abogratis" id="aboGratis"></div>' +
      '<div class="abohinweis">'+esc(t('voll.hinweis'))+'</div>' +
      /* iOS (30.10.2026, Richtlinie 3.1.2): Links zu Nutzungsbedingungen
         und Datenschutz und "Kaeufe wiederherstellen" stehen im Kaufkasten
         selbst. Name, Laufzeit und Preis stehen schon auf den Karten, die
         Gratiszeit mit dem Preis danach darueber. Die Links rollen mit dem
         Inhalt, fest am Rand stehen nur die Knoepfe (.kaufknoepfe). */
      (IST_IOS ? '<div class="abolinks">' +
         '<button type="button" class="abolink" id="aboAgb"></button> · ' +
         '<button type="button" class="abolink" id="aboDs"></button> · ' +
         '<button type="button" class="abolink" id="aboWh"></button></div>' : '') +
      '<div class="kaufknoepfe">' +
        '<button class="btn know" id="aboKauf"></button>' +
        '<button class="btn ghost" id="aboZu"></button>' +
      '</div>' +
    '</div>';
  kasten.querySelector('#aboKauf').textContent = t('voll.kaufen');
  kasten.querySelector('#aboZu').textContent = t('btn.dialog_abbrechen');
  if(IST_IOS){
    kasten.querySelector('#aboAgb').textContent = t('set.agb');
    kasten.querySelector('#aboDs').textContent = t('set.datenschutz');
    kasten.querySelector('#aboWh').textContent = t('voll.wiederherstellen');
    kasten.querySelector('#aboAgb').addEventListener('click', ()=> rechtstextZeigen('agb'));
    kasten.querySelector('#aboDs').addEventListener('click', ()=> rechtstextZeigen('datenschutz'));
  }
  document.body.appendChild(kasten);
  const zu = ()=>{ kasten.remove(); if(frageSchliessen === zu) frageSchliessen = null; };
  frageSchliessen = zu;                       // damit die Zurück-Taste sie schließt
  kasten.querySelector('#aboZu').addEventListener('click', zu);
  if(IST_IOS) kasten.querySelector('#aboWh').addEventListener('click', ()=>{ zu(); aboWiederherstellen(); });
  kasten.addEventListener('click', e=>{ if(e.target === kasten) zu(); });
  /* Vorausgewählt ist das Jahr - das günstigere. Gibt es dafür keinen Preis,
     nimmt die Auswahl, was da ist. */
  const karten = [...kasten.querySelectorAll('.abokarte')];
  let gewaehlt = null;
  const waehle = b => {
    if(!b || b.disabled) return;
    gewaehlt = b;
    karten.forEach(x => x.setAttribute('aria-checked', x === b));
    // Die Testwoche gilt je Plan - es zaehlt die gewaehlte Karte.
    kasten.querySelector('#aboGratis').textContent = gratisText(b.dataset.plan === 'jahr' ? jahr : monat);
  };
  waehle(karten.find(b => b.dataset.plan === 'jahr' && !b.disabled) || karten.find(b => !b.disabled));
  karten.forEach(b => b.addEventListener('click', ()=> waehle(b)));
  // Erst hier: die Testwoche steht jetzt da und zaehlt mit
  kaufkastenEinpassen(kasten.querySelector('.kaufbox'));
  /* Der Drache in voller Montur - unabhaengig davon, was der Nutzer
     gerade traegt. Genau das ist ja das Angebot. */
  const schau = kasten.querySelector('.abovorschau .zmaj-anim');
  if(schau) mountZmaj(schau, 'cheer',
    {ids: ['krone_gross', 'monokel', 'umhang', 'galaxie', 'funkeln']
           .filter(id => MASCOT.has(zierratDatei(id))), farbe: 'galaxie'});
  kasten.querySelector('#aboKauf').addEventListener('click', async ()=>{
    if(aboLaeuft || !gewaehlt) return;         // Sperre gegen Doppeltipp
    aboLaeuft = true;
    kasten.querySelector('#aboKauf').disabled = true;
    let r = null;
    try{ r = await P.kaufen({plan: gewaehlt.dataset.plan}); }catch(e){}
    aboLaeuft = false;
    zu();
    /* Ob gekauft wurde, sagt nicht dieser Aufruf, sondern die Meldung aus
       dem Plugin - sonst hinge die App, wenn jemand Googles Fenster
       wegwischt, ohne zu entscheiden. */
    if(!r || !r.ok) vollMeldung(t('voll.fehler'));
    vollZeileZeigen();
  });
}
function aboMeldung(d){
  const aktiv = !!(d && d.aktiv);
  if(aktiv !== premium){ vollversionMerken(aktiv); renderLives(); }
  aboStoerung = false;
  aboGesperrt = !!(d && d.gesperrt) && !aktiv;   // siehe vollAbgleichenJetzt()
  aboPlanSetzen(d);
  vollZeileZeigen();
  if(aktiv && d && d.neu){ vollMeldung(t('voll.gekauft')); sound('wegmarke'); }
}
/* aboGeaendert vor skripteDa (20.11.2026, Aufteilung): Die Huelle liefert
   die beim Abgleich aufbewahrte Meldung (retainUntilConsumed), sobald der
   Horcher haengt. In der ungeteilten Datei lief sie fruehestens nach dem
   ganzen Skript. Geteilt kann sie zwischen zwei Dateien kommen, noch vor
   init(), und im Fehlerfall (teileFehlen) auch. Darum wird sie bis
   skripteDa nur gemerkt (die letzte zaehlt) und erst in nachAnmeldung()
   gleich nach loadProgress() nachgereicht: dann haben vollversionLaden()
   und dauerVollLaden() premium schon gesetzt, und aboMeldung() vergleicht
   mit dem echten Stand. Startet die App nicht, wird sie nie verarbeitet.
   Ungeteilt ist aboFrueh immer leer. Eine Meldung nach skripteDa laeuft
   wie bisher sofort - auch vor loadProgress(); das heilt vollAbgleichen()
   am Ende von init(). */
let aboFrueh = null;
function aboFruehNachholen(){
  const f = aboFrueh; aboFrueh = null;
  if(f) aboMeldung(f.d);
}
/* Meldungen aus dem Plugin. Einmal beim Laden anhängen. */
(function aboHorchen(){
  const P = aboPlugin(); if(!P || !P.addListener) return;
  P.addListener('aboGeaendert', d => {
    if(!skripteDa){ aboFrueh = {d}; return; }
    aboFrueh = null;
    aboMeldung(d);
  });
  P.addListener('kaufAbgebrochen', ()=>{ vollMeldung(t('voll.abgebrochen')); vollZeileZeigen(); });
  P.addListener('kaufFehler', ()=>{ vollMeldung(t('voll.fehler')); vollZeileZeigen(); });
  /* Eine wartende Zahlung (Bargeld, Gutschein) hat noch keinen Ausgang.
     Es gibt bewusst keinen eigenen Text dafür: die Zeile bleibt auf
     "wird geladen", und sobald Google bezahlt meldet, springt sie um. */
  P.addListener('kaufWartet', ()=>{ aboLaeuft = true; vollZeileZeigen(); });
})();
/* ---- Widerruf ----
   § 356a BGB, in Kraft seit dem 19.06.2026: eine ständig verfügbare,
   hervorgehobene Schaltfläche, dahinter eine zweite zum Bestätigen. Ob
   Ajdin gegenüber dem Käufer überhaupt der Unternehmer ist oder ob das
   Google Commerce Limited ist, ist umstritten - er hat sich für die
   sichere Seite entschieden.

   Ohne Server kann die App keine Erklärung entgegennehmen. Also derselbe
   Weg wie beim Feedback: die App öffnet das Mailprogramm mit fertiger
   Nachricht, abgeschickt wird sie vom Nutzer, und Ajdins Antwortmail ist
   die Eingangsbestätigung auf einem dauerhaften Datenträger. */
function widerrufZeigen(){
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage';
  kasten.innerHTML =
    '<div class="nachfragebox">' +
      '<h3></h3><div class="txt"></div>' +
      '<button class="btn know" id="widOk"></button>' +
      '<button class="btn ghost" id="widZu"></button>' +
    '</div>';
  kasten.querySelector('h3').textContent = t('set.widerruf_knopf');
  kasten.querySelector('.txt').textContent = t('set.widerruf_text');
  kasten.querySelector('#widOk').textContent = t('set.widerruf_bestaetigen');
  kasten.querySelector('#widZu').textContent = t('btn.dialog_abbrechen');
  document.body.appendChild(kasten);
  const zu = ()=>{ kasten.remove(); if(frageSchliessen === zu) frageSchliessen = null; };
  frageSchliessen = zu;
  kasten.querySelector('#widZu').addEventListener('click', zu);
  kasten.addEventListener('click', e=>{ if(e.target === kasten) zu(); });
  kasten.querySelector('#widOk').addEventListener('click', ()=>{
    const betreff = 'Zmaj – ' + t('set.widerruf_knopf');
    /* Bis 06.11.2026 stand hier set.widerruf_text, also die Anleitung aus dem
       Kasten. § 356a Abs. 2 BGB verlangt Name, Angaben zum Vertrag und den Weg
       fuer die Bestaetigung; ohne sie folgte eine Rueckfrage (Pruefbericht 1.3,
       G15). Der Text nennt weder Google noch GPA: iOS nimmt denselben. */
    /* today() statt toISOString(): UTC zeigte zwischen Mitternacht und 1 Uhr
       (im Sommer 2 Uhr) noch den Vortag. Gefunden 17.11.2026 um 0:28, als
       test_widerruf.py nach Mitternacht lief. Ebenso feedbackPerMail(). */
    const rumpf = t('set.widerruf_mail') + '\n\n--\n'
                + (SPRACHE||'') + ' · ' + today();
    try{ location.href = 'mailto:' + ZMAJ_MAIL
          + '?subject=' + encodeURIComponent(betreff)
          + '&body=' + encodeURIComponent(rumpf); }catch(e){}
    zu();
    vollMeldung(t('set.feedback_mail', {mail: ZMAJ_MAIL}));
  });
}
$('widerrufKnopf').addEventListener('click', widerrufZeigen);

$('swVoll').addEventListener('click', ()=>{
  if(premium){ aboSeiteOeffnen(); return; }   // aus geht nur bei Google
  /* Gesperrt: kein zweites Abo anbieten, das alte ist ja noch da. Google
     will solche Nutzer im Abo-Center, wo sie die Zahlung reparieren.
     07.10.2026 */
  if(aboGesperrt){ aboSeiteOeffnen(); return; }
  vollWahlZeigen();
});
/* Alle Kauf-Einstiege ausserhalb der Einstellungen: die Zeile im Laden,
   die Vollversions-Stuecke, "Nie wieder warten" auf den Schirmen ohne
   Leben und "Werbung abschalten" auf dem Ersatz-Werbeschirm. Bis Build 96
   oeffneten sie nur die Einstellungen, und wer kaufen wollte, musste dort
   erst noch den Schalter antippen. Jetzt kommt gleich der Kaufkasten.
   Vorher abwarten, was Google zum Abo sagt: showSettings() startet
   vollAbgleichen(), und solange das laeuft, bricht vollWahlZeigen() an
   aboLaeuft still ab. Laeuft das Abo schon oder ist es gesperrt, bleibt es
   bei den Einstellungen - dort stehen der Stand und der Weg zu Google.
   Gefunden bei der Pruefung am 07.10.2026. */
async function vollKaufOeffnen(){
  showSettings();
  if(!aboPlugin() || unlimited() || aboGesperrt) return;
  try{ await aboAbgleich; }catch(e){}
  if(unlimited() || aboGesperrt || aboProdukteFehlen || !sichtbar('settingsView')) return;
  vollWahlZeigen();
}
/* Auch die Standzeile ist antippbar: antwortet der Play Store gerade nicht,
   soll man es noch einmal versuchen können. Google empfiehlt das ausdrücklich. */
$('setVollStand').addEventListener('click', ()=>{ if(!premium) vollAbgleichen(); });
$('aboVerwalten').addEventListener('click', aboSeiteOeffnen);
/* "Auf jaehrlich wechseln". Wie im Kaufkasten startet nicht die Zeile
   selbst den Kauf, sondern ein Knopf "Zahlungspflichtig abonnieren"
   (§ 312j Abs. 3 BGB, siehe vollWahlZeigen()): der Wechsel ist ein neues
   Jahresabo, und Google bucht sofort ab. Was dabei genau passiert, steht
   bei aufJahrWechseln() in ZmajAbo.java. 10.10.2026 */
function jahrWechselZeigen(){
  const P = aboPlugin();
  if(!P || aboLaeuft || aboPlan !== 'monat' || !aboJahrPreis) return;
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage';
  kasten.innerHTML =
    '<div class="nachfragebox">' +
      '<h3></h3><div class="txt"></div>' +
      '<div class="abogratis"></div>' +
      '<div class="abohinweis"></div>' +
      '<button class="btn know" id="wechselOk"></button>' +
      '<button class="btn ghost" id="wechselZu"></button>' +
    '</div>';
  kasten.querySelector('h3').textContent = t('voll.wechsel');
  kasten.querySelector('.txt').textContent = t('voll.wechsel_text', {preis: aboJahrPreis});
  /* Preis und Zeitraum fett direkt ueber dem Knopf, wie die Testwoche im
     Kaufkasten: wer bestellt, muss sehen, was wie oft abgebucht wird. */
  kasten.querySelector('.abogratis').textContent = t('voll.pro_jahr', {preis: aboJahrPreis});
  kasten.querySelector('.abohinweis').textContent = t('voll.hinweis');
  kasten.querySelector('#wechselOk').textContent = t('voll.kaufen');
  kasten.querySelector('#wechselZu').textContent = t('btn.dialog_abbrechen');
  document.body.appendChild(kasten);
  const zu = ()=>{ kasten.remove(); if(frageSchliessen === zu) frageSchliessen = null; };
  frageSchliessen = zu;                       // damit die Zurueck-Taste sie schliesst
  kasten.querySelector('#wechselZu').addEventListener('click', zu);
  kasten.addEventListener('click', e=>{ if(e.target === kasten) zu(); });
  kasten.querySelector('#wechselOk').addEventListener('click', async ()=>{
    if(aboLaeuft) return;                      // Sperre gegen Doppeltipp
    aboLaeuft = true;
    kasten.querySelector('#wechselOk').disabled = true;
    vollMeldung('');
    let r = null;
    try{ r = await P.aufJahrWechseln(); }catch(e){}
    aboLaeuft = false;
    zu();
    /* Ob gewechselt wurde, sagt wie beim Kauf erst die Meldung aboGeaendert
       (dann "Vollversion aktiv"), kaufAbgebrochen oder kaufFehler. */
    if(!r || !r.ok) vollMeldung(t('voll.fehler'));
    vollZeileZeigen();
  });
}
$('aboWechsel').addEventListener('click', jahrWechselZeigen);
function aboSeiteOeffnen(){
  /* iPhone und iPad (30.10.2026): Apples eigene Abo-Verwaltung, als Blatt
     in der App (ZmajAbo.verwalten, AppStore.showManageSubscriptions). Geht
     das nicht, die Abo-Seite des App Stores. */
  if(IST_IOS){
    const P = aboPlugin();
    const notweg = ()=>{ try{ window.open('https://apps.apple.com/account/subscriptions', '_blank'); }catch(e){} };
    if(P && typeof P.verwalten === 'function'){
      P.verwalten().then(r => { if(!r || r.ok === false) notweg(); }, notweg);
    }else notweg();
    return;
  }
  const u = 'https://play.google.com/store/account/subscriptions'
          + '?sku=vollversion&package=de.smartdragon.zmaj';
  try{ window.open(u, '_blank'); }catch(e){ location.href = u; }
}
/* "Kaeufe wiederherstellen" (nur iOS, Richtlinie 3.1.1, 30.10.2026).
   ZmajAbo.wiederherstellen() gleicht mit Apple ab (AppStore.sync - Apple
   fragt dabei eventuell nach dem Passwort des Apple-Accounts) und antwortet
   {ok, aktiv, plan}. Hat sich etwas geaendert, kommt ausserdem wie nach
   einem Kauf aboGeaendert. */
async function aboWiederherstellen(){
  const P = aboPlugin();
  if(!P || typeof P.wiederherstellen !== 'function' || aboLaeuft) return;
  aboLaeuft = true; vollMeldung(''); vollZeileZeigen();
  let r = null;
  try{ r = await P.wiederherstellen(); }catch(e){}
  aboLaeuft = false;
  if(r && r.ok){
    if(!!r.aktiv !== premium){ vollversionMerken(!!r.aktiv); renderLives(); drachenNeu(); renderLaden(); }
    aboPlanSetzen(r);
    vollMeldung(t(r.aktiv ? 'voll.wiederhergestellt' : 'voll.nichts_gefunden'));
  }else{
    vollMeldung(t('voll.fehler'));
  }
  vollZeileZeigen();
}
$('aboWiederherstellen').addEventListener('click', aboWiederherstellen);
/* Nutzungsbedingungen und Datenschutzerklaerung als eigene Ebene ueber dem
   Kaufkasten. Apple verlangt im Kaufkasten funktionierende Links zu beiden
   (Richtlinie 3.1.2); in der App heisst das: lesen, ohne den Kasten zu
   verlieren, und ohne Netz. Gezeigt wird die Fassung der Plattform (t(),
   auf iOS die _ios-Texte). 30.10.2026 */
function rechtstextZeigen(art){
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage rechtsebene';
  kasten.innerHTML = '<div class="nachfragebox einwilligungbox" style="text-align:left">' +
      '<h3></h3><div class="inner legal"></div>' +
      '<button class="btn know" id="rechtZu"></button></div>';
  kasten.querySelector('h3').textContent = t(art === 'agb' ? 'set.agb' : 'set.datenschutz');
  kasten.querySelector('.legal').innerHTML = t(art === 'agb' ? 'set.agb_text' : 'set.datenschutz_text',
                                               {anbieter: t('set.anbieter')});
  kasten.querySelector('#rechtZu').textContent = t('btn.zurueck');
  document.body.appendChild(kasten);
  const vorher = frageSchliessen;
  const zu = ()=>{ kasten.remove(); if(frageSchliessen === zu) frageSchliessen = vorher; };
  frageSchliessen = zu;
  kasten.querySelector('#rechtZu').addEventListener('click', zu);
  kasten.addEventListener('click', e=>{ if(e.target === kasten) zu(); });
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
