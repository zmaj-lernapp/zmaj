/* ---- Laden ----
   Münzen kommen aus den Tagesaufgaben. Die Vollversion gibt es hier
   ausdrücklich NICHT: `premium` darf der Browser nie setzen, der Server holt
   es immer aus der Datei zurück. Und die Abos sind die einzige Einnahme. */
/* Welcher Reiter offen ist. Gekauft wird auch ausserhalb des Ladens - vom
   Bildschirm ohne Leben aus -, deshalb steht der Wert hier draussen. */
let ladenReiter = 'vorrat', ladenOffen = false;
function renderLaden(){
  const box=$('ladenWaren'); if(!box) return;
  renderLives();                      // die Muenzzahl oben stimmt sonst nach einem Kauf nicht
  /* Fuenf Reiter nebeneinander brachen auf schmalen Geraeten in zwei Zeilen
     um und sahen zerfasert aus. Jetzt dieselbe Aufklappliste wie bei der
     Sprachwahl: eine Zeile, egal wie viele Gruppen es gibt.
     Ajdin am 18.09.2026. */
  const kopf = $('ladenKopf'), liste = $('ladenListe');
  if(kopf && liste){
    const jetzt = GRUPPEN.find(g => g.id === ladenReiter) || GRUPPEN[0];
    kopf.innerHTML = '<span>'+esc(t(jetzt.titel))+'</span><span class="pfeil" aria-hidden="true">\u25be</span>';
    kopf.setAttribute('aria-expanded', ladenOffen);
    liste.hidden = !ladenOffen;
    liste.innerHTML = GRUPPEN.map(g =>
        '<button type="button" class="sprachzeile'+(g.id===ladenReiter?' jetzt':'')+'" data-gruppe="'+g.id+'">'
      + esc(t(g.titel)) + (g.id===ladenReiter ? ' <span class="haken">\u2713</span>' : '') + '</button>').join('');
    kopf.onclick = ()=>{ ladenOffen = !ladenOffen; renderLaden(); };
    // Die Zeile, auf der der Fokus lag, gibt es nach dem Neuzeichnen nicht
    // mehr - er geht zurueck auf die Reiterwahl (17.10.2026).
    liste.querySelectorAll('.sprachzeile').forEach(b => b.onclick = ()=>{
      ladenOffen = false; ladenReiter = b.dataset.gruppe; renderLaden();
      try{ kopf.focus({preventScroll:true}); }catch(e){}
    });
  }
  /* Bei den Farben ein Tupfer neben dem Namen: sonst muesste man kaufen, um
     zu sehen, wovon die Rede ist. */
  const tupfer = w => FARBEN[w.id]
    ? '<span class="farbtupfer" style="background:#'+FARBEN[w.id][0]+'"></span>' : '';
  const zeile = (w, knopf, extra) =>
    '<div class="ware'+(extra ? ' '+extra : '')+'"><div><div class="wt">'+tupfer(w)+t(w.titel)+'</div>'+
    '<div class="wd">'+t(w.sub)+'</div></div>'+knopf+'</div>';
  /* Jeder Knopf nennt seinen Artikel (17.10.2026): "Tragen, Mütze" statt nur
     "Tragen". Wer mit Screenreader von Knopf zu Knopf geht, hoerte sonst
     fuenfmal "Tragen" und wusste nicht, wofuer. Der sichtbare Text steht
     vorn im Namen (WCAG 2.5.3). Getragen oder nicht sagt der Text selbst:
     "Abnehmen" heisst, er sitzt. aria-pressed gibt es bewusst nicht - der
     Text wechselt mit dem Zustand, und "Abnehmen, gedrueckt" hiesse das
     Gegenteil. */
  const knopfName = (w, sicht) => ' aria-label="'+esc(sicht+', '+t(w.titel))+'"';
  const preisKnopf = w => {
    const geht = muenzen() >= w.preis && w.geht();
    return '<button class="btn kauf '+(geht?'know':'ghost')+'" data-ware="'+w.id+'"'+
           knopfName(w, w.preis+' '+SYMBOL_SAGT.muenze)+(geht?'':' disabled')+'>'+mitSymbol('muenze', w.preis)+'</button>';
  };
  /* Ein Stueck der Vollversion hat keinen Preis. Laeuft sie, steht dort
     Tragen oder Abnehmen wie bei gekaufter Ware; laeuft sie nicht, ein
     grauer Knopf, der in die Einstellungen fuehrt.
     Gibt es dort nichts zu holen - kein Abo-Plugin wie im Browser am PC,
     oder Google kennt die Produkte noch nicht -, blendet showSettings()
     den ganzen Vollversions-Block aus. Dann fuehrte der Knopf ins Leere,
     und im Reiter Effekte war er der einzige. Jetzt steht er dort
     ausgegraut: nichts zu tun, aber auch kein falsches Versprechen.
     Dieselbe Bedingung benutzen vollZeileLaden() und vollZeileLeben().
     Gefunden in der Gegenpruefung am 29.09.2026. */
  const tragenKnopf = w => '<button class="btn kauf '+(traegt(w.id)?'know':'ghost')+'" data-tragen="'+w.id+'"'+
        knopfName(w, t(traegt(w.id) ? 'laden.abnehmen' : 'laden.tragen'))+'>'+
        t(traegt(w.id) ? 'laden.abnehmen' : 'laden.tragen')+'</button>';
  const vollKnopf = w => (!aboPlugin() || aboProdukteFehlen)
    ? '<button class="btn kauf ghost"'+knopfName(w, t('laden.nur_voll'))+' disabled>'+t('laden.nur_voll')+'</button>'
    : '<button class="btn kauf ghost" data-vollstueck="1"'+knopfName(w, t('laden.nur_voll'))+'>'+t('laden.nur_voll')+'</button>';
  const zierratZeile = w => w.voll
    ? zeile(w, unlimited() ? tragenKnopf(w) : vollKnopf(w))
    : (hatStueck(w.id) ? zeile(w, tragenKnopf(w)) : zeile(w, preisKnopf(w)));
  /* Beim Herz steht neben dem Preis auch das freiwillige Video - der Laden
     ist die Stelle, an der man nach "auffuellen" sucht. Eigenes
     Tageskontingent, siehe WERBUNG_MAX_LOHN.
     Der Knopf steht IMMER da und wird nur ausgegraut, genau wie der
     Preisknopf. Vorher verschwand er ganz, wenn die Leben voll waren - dann
     stand der Preis grau daneben und das Video gar nicht, und es sah aus, als
     gaebe es den Weg nicht. Ajdin am 27.09.2026: "hae im laden ist noch kein
     werbung ansehen balken" - er hatte funf von funf Leben. */
  const videoKnopf = w => {
    const geht = w.geht() && werbungErlaubt(true);
    return '<button class="btn kauf ' + (geht ? 'know' : 'ghost') + '" data-videoleben="1"'
         + (geht ? '' : ' disabled') + '>' + mitSymbol('herz', t('werbung.leben_holen')) + '</button>';
  };
  const knoepfe = w => w.id === 'herz'
    ? '<span class="kaufwege">' + preisKnopf(w) + videoKnopf(w) + '</span>'
    : preisKnopf(w);
  /* Die Vollversion ganz oben im Vorrat. Sie ist das Einzige im Laden,
     das es NICHT fuer Muenzen gibt - gekauft wird bei Google -, und
     genau deshalb sucht sie dort niemand. Der Knopf fuehrt in die
     Einstellungen, wo der Kauf steht. Ajdin am 29.09.2026: „im laden
     noch eine anzeige hinbauen dann sieht man es eindeutig“. */
  const vollZeileLaden = () => {
    if(unlimited() || !aboPlugin() || aboProdukteFehlen) return '';
    /* Die Testwoche schon hier und nicht erst im Kaufkasten - aber nur,
       wenn Google sie diesem Nutzer anbietet, und mit dem Preis danach wie
       dort. Gefunden bei der Pruefung am 07.10.2026. */
    const gratis = gratisText(aboGratisPlan);
    return '<div class="ware"><div><div class="wt">' + esc(t('voll.wahl_titel')) + '</div>'
         + '<div class="wd">' + esc(t('lektion.vollversion')) + '</div>'
         + (gratis ? '<div class="wd" style="font-weight:800; color:var(--ink)">' + esc(gratis) + '</div>' : '')
         + '</div>'
         + '<button class="btn kauf know" id="ladenVoll">' + esc(t('laden.voll_knopf'))
         + '</button></div>';
  };
  box.innerHTML = ladenReiter === 'vorrat'
    ? vollZeileLaden() + VERBRAUCH.map(w => zeile(w, knoepfe(w), w.id === 'herz' ? 'zweiwege' : '')).join('')
    : ZIERRAT.filter(w => w.gruppe === ladenReiter).map(zierratZeile).join('');
  box.querySelectorAll('button[data-ware]').forEach(b =>
    b.addEventListener('click', ()=> ladenTipp(()=> kaufe(b.dataset.ware))));
  box.querySelectorAll('button[data-tragen]').forEach(b =>
    b.addEventListener('click', ()=> ladenTipp(()=> trage(b.dataset.tragen))));
  const vk = box.querySelector('button[data-videoleben]');
  if(vk && !vk.disabled) vk.addEventListener('click', werbungFuerLeben);
  // Beide direkt zum Kaufkasten, siehe vollKaufOeffnen(). 07.10.2026
  const lv = box.querySelector('#ladenVoll');
  if(lv) lv.addEventListener('click', ()=>{ vollKaufOeffnen(); });
  box.querySelectorAll('button[data-vollstueck]').forEach(b =>
    b.addEventListener('click', ()=>{ vollKaufOeffnen(); }));
}
/* Ein Doppeltipp ist ein Tipp. Ohne Sperre kostete er beim Herz 200 statt 100
   Muenzen, und Zierrat wurde gekauft und sofort wieder abgenommen. renderLaden()
   zeichnet die Knoepfe nach jedem Tipp neu, der zweite traf also einen frischen
   Knopf; deshalb zaehlt die Zeit und nicht der Knopf. Hier und nicht in kaufe()
   und trage(): die werden auch direkt nacheinander aufgerufen.
   Gezaehlt wird ab dem Ende des ersten Tipps: der erste Kauf nach dem Start
   haelt die Seite mitunter laenger fest, als die Sperre dauert (680 ms in einem
   frischen Browser), und der zweite Tipp wartet solange in der Schlange.
   Pruefbericht 1.3, G9. */
const LADEN_SPERRE_MS = 400;
let ladenLetzterTipp = -LADEN_SPERRE_MS;
function ladenTipp(tun){
  if(performance.now() - ladenLetzterTipp < LADEN_SPERRE_MS) return;
  tun();
  ladenLetzterTipp = performance.now();
}
/* Anziehen oder ausziehen. Aus jeder Gruppe sitzt hoechstens ein Stueck:
   eine zweite Muetze schiebt die erste herunter. Ein zweites Mal auf
   dasselbe tippen nimmt es ab. */
function trage(id){
  if(!hatStueck(id) && !(istVollStueck(id) && unlimited())) return;
  const g = gruppeVon(id);
  const runter = traegt(id);
  // Rohe Liste: siehe getragenRoh(). Sonst faellt hier heraus, was das
  // abgelaufene Abo gerade verdeckt, und kommt nie wieder.
  const rest = getragenRoh().filter(x => x !== id && gruppeVon(x) !== g);
  setzeGetragen(runter ? rest : rest.concat([id]));
  sound(runter ? 'ablegen' : 'anziehen');
  const imLaden = ladenHatFokus();
  renderLaden(); drachenNeu();
  if(imLaden) ladenFokusAuf(id);
  ansagen(esc(t(runter ? 'laden.abgenommen' : 'laden.angezogen')));
}
/* Nach Kaufen und Anziehen zeichnet renderLaden() die Warenliste neu, und
   der Knopf, auf dem der Fokus lag, ist weg - mit Tastatur oder
   Screenreader stand man danach am Seitenanfang (17.10.2026). Jetzt geht
   der Fokus auf den Knopf desselben Artikels zurueck; ist der aus (Geld
   reicht nicht mehr, Serienschutz voll), auf einen anderen Knopf derselben
   Zeile, sonst auf die Reiterwahl. Nur, wenn er vorher im Laden lag: wer
   vom Bildschirm ohne Leben aus kauft, dem wird nichts verschoben. */
function ladenHatFokus(){
  const box = $('ladenWaren');
  return !!box && box.contains(document.activeElement);
}
function ladenFokusAuf(id){
  const box = $('ladenWaren'); if(!box) return;
  const knoepfe = [...box.querySelectorAll('button[data-tragen="'+id+'"], button[data-ware="'+id+'"]')];
  let ziel = knoepfe.find(b => !b.disabled);
  if(!ziel && knoepfe[0]) ziel = [...knoepfe[0].closest('.ware').querySelectorAll('button')].find(b => !b.disabled);
  if(!ziel) ziel = $('ladenKopf');
  if(ziel) try{ ziel.focus({preventScroll:true}); }catch(e){}
}
/* Nach dem Wechsel muss die Animation neu geladen werden - jedes Stueck
   steckt in einer eigenen Datei. */
function drachenNeu(){
  document.querySelectorAll('.zmaj-anim').forEach(el=>{
    if(el._anim){ try{ el._anim.destroy(); }catch(e){} el._anim = null; el._stand = null; el.innerHTML=''; }
    mountZmaj(el);
  });
}
/* Ein Kauf ist ein Ereignis und muss den Abgleich ueberstehen (Serienschutz 06.11.2026,
   Herz 07.11.2026). Bisher blieb zeit stehen und ging bei vollem Vorrat auf 0. Gegen den
   Stand von vor dem Kauf gewann dann die neuere Zeit oder bei gleicher Zeit die kleinere
   Anzahl (siehe zeitWahl): Die Ware war auf allen Geraeten weg, die Muenzen auch. Darum
   geht zeit nach oben. Bei vollem Vorrat laeuft keine Uhr, zeit ist dort der Kauf. Sonst
   laeuft die Uhr weiter, ein Kauf soll keine Wartezeit kosten, eine Millisekunde reicht.
   Ein Geraet mit 1.2 liest beides als ganz normale Zeit. Zierrat braucht das nicht:
   besitz ist eine Vereinigung, siehe standZusammenfuehren(). */
function zeitNachKauf(zeit, voll){ return voll ? Math.max(Date.now(), zeit + 1) : zeit + 1; }
function kaufe(id){
  const w = [...VERBRAUCH, ...ZIERRAT].find(x => x.id === id);
  if(!w || muenzen() < w.preis || !w.geht()) return;
  if(id==='herz'){
    syncLives();
    lives.anzahl = Math.min(LEBEN_MAX, lives.anzahl + 1);
    lives.zeit = zeitNachKauf(lives.zeit, lives.anzahl >= LEBEN_MAX);
  } else if(id==='schutz'){
    const vorrat = schutzNow();
    schutz.anzahl = Math.min(SCHUTZ_MAX, vorrat + 1);
    schutz.zeit = zeitNachKauf(schutz.zeit, schutz.anzahl >= SCHUTZ_MAX);
  } else {
    // Gekauftes wird gleich getragen - und schiebt das alte Stueck derselben
    // Gruppe herunter, nicht den ganzen uebrigen Zierrat.
    besitz.add(id);
    const g = gruppeVon(id);
    setzeGetragen(getragenRoh().filter(x => gruppeVon(x) !== g).concat([id]));
  }
  muenzenAus += w.preis;
  saveProgress(); sound('kauf');
  // Gekauft wird auch außerhalb des Ladens - vom Bildschirm ohne Leben aus.
  // Dort gibt es weder Notizzeile noch Warenliste, deshalb überall prüfen.
  const imLaden = ladenHatFokus();
  if($('ladenNote')) $('ladenNote').textContent = t('laden.gekauft');
  if($('ladenWaren')) renderLaden();
  if(imLaden) ladenFokusAuf(id);
  ansagen(esc(t('laden.gekauft')));   // die Notizzeile oben liest kein Screenreader von selbst vor
  renderLives();
  if(ZIERRAT.some(x => x.id === id)) drachenNeu();
  if($('setSchutz')) $('setSchutz').textContent = tp('serie.schutz', schutzNow());
}
/* Auswahl ändern: dasselbe Fenster noch einmal, mit der Antwort von
   vorhin gelöscht - sonst käme es gar nicht erst hoch. */
$('btnSettings').addEventListener('click', async ()=>{
  if(!await lektionDarfWeg()) return;
  await saveProgress(); showSettings();
});
$('setLogout').addEventListener('click', abmelden);

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
