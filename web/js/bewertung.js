/* =================== BEWERTUNG ===================
   Festgelegt von Ajdin am 30.09.2026: eine Karte mit zwei Wegen - bei
   Google Play bewerten oder eine Verbesserung vorschlagen -, und leise
   darunter "Nein danke". Sie kommt nach einem bestandenen Level-Test, fruehestens
   am dritten Lerntag, hoechstens zweimal im Jahr, und nach "Nein danke" nie
   wieder. Wer auf Bewerten getippt hat, wird auch nicht mehr gefragt.

   Bewusst KEINE Frage wie "Gefaellt dir Zmaj?" davor. Google verbietet
   genau das: erst die Stimmung abfragen und nur die Zufriedenen zur
   Bewertung schicken. Beide Wege stehen deshalb gleichberechtigt da.
   https://developer.android.com/guide/playcore/in-app-review

   Zwischen zwei Karten liegen mindestens 90 Tage - "zweimal im Jahr" soll
   nicht heissen: zweimal in derselben Woche. Die Zahl ist meine Wahl, nicht
   Ajdins; sie steht im Bericht vom 01.10.2026.

   Die Karte kommt nicht auf dem Ergebnisschirm selbst - dort laeuft nach
   1,2 Sekunden die Anzeige. Sie wartet, bis man ihn verlaesst. */
const BEWERTUNG_AB_TAG = 3, BEWERTUNG_PRO_JAHR = 2, BEWERTUNG_ABSTAND = 90;
/* true: erst Googles Fenster in der App, und wenn es nicht kommt, der Play
   Store. false: gleich der Play Store. Siehe ZmajBewertung.java.
   Seit 14.11.2026 false (Pruefbericht 1.4, S21): Google raet davon ab, das
   Fenster ueber einen Knopf zu starten - es kommt nur, wenn Googles
   Kontingent es zulaesst, und ein Knopf, der manchmal nichts tut, sieht
   kaputt aus. "Zmaj bewerten" auf der Karte oeffnet deshalb gleich den
   Store. */
const BEWERTUNG_IM_APP = false;
const ZMAJ_PAKET = 'de.smartdragon.zmaj';
let bewertungDran = false;
function bewertungFaellig(){
  if(ALLE_FREI || bewertung.nein || bewertung.bewertet) return false;
  if(days.size < BEWERTUNG_AB_TAG) return false;
  const heute = today(), jahr = tagMinus(heute, 365);
  const imJahr = (bewertung.gezeigt || []).filter(d => d > jahr).sort();
  if(imJahr.length >= BEWERTUNG_PRO_JAHR) return false;
  const letzte = imJahr[imJahr.length - 1];
  return !(letzte && letzte > tagMinus(heute, BEWERTUNG_ABSTAND));
}
async function bewertungOeffnen(){
  const P = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.ZmajBewertung;
  if(!P){
    const u = storeLink(false);
    if(u) try{ window.open(u, '_blank', 'noopener'); }catch(e){}
    return;
  }
  if(BEWERTUNG_IM_APP){
    /* Google sagt nicht, ob das Fenster kam. Kommt die Antwort in unter
       anderthalb Sekunden, kann niemand bewertet haben - dann war das
       Kontingent verbraucht, und der Store faengt es auf. */
    try{ const r = await P.imApp(); if(r && r.ok && r.ms >= 1500) return; }catch(e){}
  }
  try{ await P.storeOeffnen(); }catch(e){}
}
/* iPhone und iPad (30.10.2026, Entscheidung 11): keine eigene Karte.
   Apple verbietet eigene Bewertungsfragen (Richtlinie 5.6.1) und hat ein
   eigenes Fenster, das es hoechstens dreimal in 365 Tagen zeigt und das
   nicht auf ein Antippen folgen soll. Es kommt also von selbst an derselben
   ruhigen Stelle wie auf Android die Karte: zurueck auf dem Lernpfad nach
   einem bestandenen Level-Test, nie ueber einer Anzeige, nach denselben
   Grenzen (bewertungFaellig). Ob Apple es wirklich zeigt, erfaehrt die App
   nicht - deshalb kein Weg in den Store danach; ZmajBewertung.imApp()
   antwortet auf iOS ohnehin mit ms 99999. Der Knopf "Zmaj bewerten" in den
   Einstellungen fuehrt weiter in den App Store. */
async function appleBewertung(){
  bewertung.gezeigt = (bewertung.gezeigt || []).concat([today()]).slice(-6);
  saveProgress();
  const P = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.ZmajBewertung;
  if(P && typeof P.imApp === 'function'){ try{ await P.imApp(); }catch(e){} }
}
function zeigeBewertung(){
  bewertung.gezeigt = (bewertung.gezeigt || []).concat([today()]).slice(-6);
  saveProgress();
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage';
  kasten.innerHTML =
    '<div class="nachfragebox einstbox">' +
      '<div class="celebrate"><div class="zmaj cheer">' + zmaj('cheer') + '</div></div>' +
      '<h3></h3><div class="txt"></div>' +
      '<button class="btn know" id="bwJa"></button>' +
      '<button class="btn ghost" id="bwVor"></button>' +
      '<div style="margin-top:12px"><button type="button" class="abolink" id="bwNein"></button></div>' +
    '</div>';
  kasten.querySelector('h3').textContent = t('bew.titel');
  kasten.querySelector('.txt').textContent = t('bew.text');
  kasten.querySelector('#bwJa').innerHTML = mitSymbol('stern', esc(t('bew.bewerten')));
  kasten.querySelector('#bwVor').textContent = t('bew.vorschlag');
  kasten.querySelector('#bwNein').textContent = t('bew.nein');
  document.body.appendChild(kasten);
  const zu = ()=>{ kasten.remove(); if(frageSchliessen === zu) frageSchliessen = null; };
  frageSchliessen = zu;
  kasten.addEventListener('click', e=>{ if(e.target === kasten) zu(); });
  kasten.querySelector('#bwJa').addEventListener('click', ()=>{
    zu(); bewertung.bewertet = true; saveProgress(); bewertungOeffnen();
  });
  kasten.querySelector('#bwVor').addEventListener('click', ()=>{ zu(); zeigeVorschlag(); });
  kasten.querySelector('#bwNein').addEventListener('click', ()=>{ zu(); bewertung.nein = true; saveProgress(); });
}
/* Das Feld fuer den Vorschlag. Verschickt wird wie in den Einstellungen:
   das Mailprogramm des Geraets geht mit fertiger Nachricht auf.
   Seit 01.11.2026 heisst "wie in den Einstellungen": in der Handy-App mit
   Konto ueber das Kontaktformular, sonst und als Rueckfall das
   Mailprogramm (feedbackSenden). Ajdin: "Uebers Formular". */
function zeigeVorschlag(){
  const kasten = document.createElement('div');
  kasten.className = 'nachfrage';
  kasten.innerHTML =
    '<div class="nachfragebox">' +
      '<h3></h3>' +
      '<textarea class="field" id="bwText" rows="4" maxlength="2000"></textarea>' +
      '<button class="btn know" id="bwSenden"></button>' +
      '<button class="btn ghost" id="bwZu"></button>' +
      '<div class="note" id="bwNote" role="status" style="margin-top:8px"></div>' +   // wie #fbNote (01.11.2026)
    '</div>';
  kasten.querySelector('h3').textContent = t('bew.fb_titel');
  kasten.querySelector('#bwText').placeholder = t('set.feedback_platzhalter');
  kasten.querySelector('#bwSenden').textContent = t('set.feedback_senden');
  kasten.querySelector('#bwZu').textContent = t('btn.abbrechen');
  document.body.appendChild(kasten);
  const zu = ()=>{ kasten.remove(); if(frageSchliessen === zu) frageSchliessen = null; };
  frageSchliessen = zu;
  kasten.querySelector('#bwZu').addEventListener('click', zu);
  kasten.querySelector('#bwSenden').addEventListener('click', async ()=>{
    const feld = kasten.querySelector('#bwText'), text = feld.value.trim();
    const note = kasten.querySelector('#bwNote');
    if(!text){ note.textContent = t('set.feedback_leer'); return; }
    const r = await feedbackSenden(text, note, kasten.querySelector('#bwSenden'));
    if(r === null) return;
    // Ueber das Formular dankt set.feedback_danke schon selbst.
    if(r) feld.value = '';
    else note.insertAdjacentHTML('afterbegin', esc(t('bew.danke')) + ' ' + symbol('herzblau') + ' ');
    sound('ok');
    kasten.querySelector('#bwZu').textContent = t('task.weiter');
  });
  setTimeout(()=>{ const f = kasten.querySelector('#bwText'); if(f) f.focus(); }, 50);
}

var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
