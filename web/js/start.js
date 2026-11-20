/* ---- Init ---- */
/* =================== VORSPANN ===================
   Das Studio-Zeichen steht, bis die App wirklich bereit ist – aber
   mindestens VORSPANN_MIN lang, damit es nicht auf einem schnellen Gerät
   vorbeihuscht. Auf einem langsamen bleibt es eben länger; das ist besser
   als ein leerer Bildschirm.
   Einmal weg, bleibt es weg: zweimal aufrufen schadet nichts. */
/* Zwei Bedingungen müssen zusammenkommen, bevor der Vorspann geht:
   die Zeit ist um UND die App steht. Auf einem schnellen Gerät wartet er
   auf die Zeit, auf einem langsamen auf die App.
   Nach der Bewegung bleibt das fertige Bild noch VORSPANN_HALT stehen –
   ohne diese Pause wechselt die App in dem Moment, in dem der Name
   erscheint, und man hat ihn nicht gelesen. Das gilt beim ersten Start des
   Tages, siehe vorspannHeuteSchon().
   Antippen setzt die Wartezeit auf null – auch dann, wenn schon gewartet
   wird, und auch dann, wenn die App noch lädt. */
const VORSPANN_ABLAUF = 2400;   // so lange dauert die Bewegung oben im Stil
const VORSPANN_HALT   = 1500;   // so lange steht das fertige Bild danach still
/* Ohne Bewegung gibt es nichts abzuwarten: dann steht sofort das Endbild
   da, und 3,9 Sekunden davor zu sitzen ist nur Wartezeit. Geprueft wird
   beides - der Schalter in der App und die Einstellung des Geraets. */
function vorspannOhneBewegung(){
  if(document.body.classList.contains('no-anim')) return true;
  try{ return matchMedia('(prefers-reduced-motion: reduce)').matches; }
  catch(e){ return false; }
}
/* Die Haltezeit nur beim ersten Start des Tages (entschieden am 06.11.2026): sie
   hielt jeden Kaltstart auf ueber 4,5 s, obwohl die App nach 0,14 s bereit war, und
   wer den Namen heute schon gelesen hat, muss nicht noch einmal warten
   (Pruefbericht 1.3, G18). Der Tag steht nur im Geraet und ist kein Lernstand.
   Klappt der Speicher nicht, gibt es den vollen Vorspann. */
function vorspannHeuteSchon(){
  try{
    const heute = today();
    if(localStorage.getItem('zmaj_vorspann_tag') === heute) return true;
    localStorage.setItem('zmaj_vorspann_tag', heute);
  }catch(e){}
  return false;
}
let vorspannMin = vorspannOhneBewegung() ? 1400
                : VORSPANN_ABLAUF + (vorspannHeuteSchon() ? 0 : VORSPANN_HALT);
const vorspannAb = performance.now();
let vorspannUhr = null, appBereit = false, vorspannFort = false;

/* Aufgelöst, sobald der Vorspann wirklich weg ist. Darauf wartet die
   Werbevorbereitung, damit Googles Fenster nicht über dem Logo aufgeht.

   Mit Notbremse nach elf Sekunden: das Stilblatt blendet den Vorspann über
   die Animation vorspannNotaus nach zehn Sekunden auch dann aus, wenn das
   Skript hängt. Ohne diese Zeile bliebe das Versprechen dann für immer offen
   und es käme nie wieder eine Einwilligungsfrage. */
let vorspannFertig = null;
const vorspannVorbei = new Promise(loesen => {
  vorspannFertig = loesen;
  setTimeout(loesen, 11000);
});

function vorspannBlenden(){
  if(vorspannFort) return;
  vorspannFort = true;
  clearTimeout(vorspannUhr);
  const v = $('vorspann');
  if(!v){ vorspannFertig(); return; }
  v.classList.add('weg');
  setTimeout(()=>{ v.remove(); vorspannFertig(); }, 600);
}
function vorspannPlanen(){
  if(vorspannFort || !appBereit) return;
  clearTimeout(vorspannUhr);
  vorspannUhr = setTimeout(vorspannBlenden,
                           Math.max(0, vorspannMin - (performance.now() - vorspannAb)));
}
function vorspannWeg(){ appBereit = true; vorspannPlanen(); }

(function(){
  const v = $('vorspann');
  if(!v) return;
  v.addEventListener('click', ()=>{
    vorspannMin = 0;
    if(appBereit) vorspannBlenden(); else vorspannPlanen();
  }, {once:true});
})();

/* Erst AdMob starten, dann - falls nötig - nach der Einwilligung fragen.
   Läuft absichtlich OHNE await im Aufrufer: die App soll benutzbar sein,
   während Google noch antwortet. */
async function werbungVorbereiten(){
  /* Nicht, wenn die App gar nicht laden konnte: auf einem Fehlerbildschirm
     nach Werbe-Einwilligung zu fragen waere absurd. starten() wirft dort
     nicht, sondern blendet nur den Fehlerkasten ein. */
  const err = $('err');
  if(err && err.style.display === 'block') return;
  try{
    await admobStart();
    /* Punkt 19 aus WERBUNG_PRUEFUNG.md: Googles Antwort holen, BEVOR die
       erste Anzeige laeuft. werbungAbgleichen() hing an einer einzigen
       Stelle - showSettings(). Wer dort nie hinschaut, und das sind die
       meisten, bekam dauerhaft npa=1: unpersonalisierte Anzeigen, obwohl
       er in Googles Fenster zugestimmt hatte. Das trifft auch Laender
       ohne DSGVO, wo ZmajEinwilligung.java ausdruecklich
       personalisiert:true meldet - dort ohne jeden rechtlichen
       Gegenwert, nur als Einnahmeverlust.
       Kostet nichts Sichtbares: die Antwort liegt im Geraetespeicher,
       ZmajEinwilligung liest sie ohnehin schon aus. */
    await werbungAbgleichen();
    if(einwilligungFragen()) await zeigeEinwilligung();
  }catch(e){}
}

/* Nutzungsbedingungen, Punkt 9: Aendern sie sich wesentlich, erfaehrt man es
   beim naechsten Oeffnen. AGB_WESENTLICH ist das Datum der letzten
   WESENTLICHEN Aenderung (neue Pflichten, Preise, Rechte) und wird nur dann
   hochgesetzt - nicht bei Klarstellungen wie der vom 11.10.2026. Wer noch
   nichts gemerkt hat (neu installiert oder vor diesem Build), kennt die
   heutige Fassung: bei ihm wird das Datum nur gemerkt, ohne Hinweis.
   Der Hinweis kommt nur in einem ruhigen Moment auf dem Lernpfad - nie
   mitten in einer Lektion (dort braeche "Ansehen" sie ohne Rueckfrage ab),
   nie ueber Googles Einwilligung oder einer Anzeige. Sonst probiert er es
   noch ein paar Mal und dann wieder bei der naechsten Rueckkehr auf den
   Lernpfad (showHome). Als gesehen gilt er erst, wenn jemand ihn bedient
   hat. Punkt 9 versprach den Hinweis seit September, gebaut am 12.10.2026,
   nachgebessert nach dem Review am selben Tag. */
/* 28.10.2026 (v109): Das Konto ist Pflicht - Punkte 3, 5 und 8 sind neu
   (Frage 6 im Plan, nach dem Vorschlag gebaut). Der Hinweis darauf kommt
   nur mit Anmeldung (CLOUD_AN). Ohne Firebase-Projekt bleibt es beim Stand
   von v108 - sonst hiesse es dort "Bedingungen geaendert" fuer ein Konto,
   das es gar nicht gibt (Pruefbericht vom 28.10.). */
const AGB_WESENTLICH = CLOUD_AN ? '2026-10-28' : '2026-09-19';
let agbHinweisFertig = false, agbHinweisOffen = false;
function agbRuhig(){
  return updWerbungDurch && sichtbar('pfad') && !updLerntGerade() && !frageSchliessen &&
         !wegmarkeLaeuft && !anzeigeLaeuft && $('err').style.display !== 'block' &&
         !document.querySelector('.nachfrage, .einwilligung, .werbung');
}
async function agbHinweis(versuch = 0){
  if(agbHinweisFertig || agbHinweisOffen) return;
  let gemerkt = null;
  try{ gemerkt = localStorage.getItem('zmaj_agb'); }catch(e){ agbHinweisFertig = true; return; }
  const merken = ()=>{ try{ localStorage.setItem('zmaj_agb', AGB_WESENTLICH); }catch(e){} };
  if(!gemerkt){ merken(); agbHinweisFertig = true; return; }
  if(gemerkt >= AGB_WESENTLICH){ agbHinweisFertig = true; return; }
  if(!agbRuhig()){
    if(versuch < 20) setTimeout(()=>agbHinweis(versuch + 1), 3000);
    return;
  }
  agbHinweisOffen = true;
  const ansehen = await frage(t('agb.neu_titel'), t('agb.neu_text'), t('agb.ansehen'), t('agb.spaeter'));
  agbHinweisOffen = false;
  agbHinweisFertig = true;
  merken();
  if(ansehen){
    showSettings();
    const s = document.querySelector('summary[data-t="set.agb"]');
    if(s){ s.parentElement.open = true; s.scrollIntoView({block: 'start'}); }
  }
}

async function init(){
  /* Die beiden versteckten Schalter (7x Tippen plus Wort) gibt es auf
     iPhone und iPad nicht: Apple verbietet versteckte Funktionen
     (Richtlinie 2.5.19; neue Funktionen muessen laut 2.3.1 in den Notizen
     fuer die Pruefung stehen), und die Vollversion ohne Kauf waere dort
     ein Verstoss gegen 3.1.1. Der iOS-Bau setzt ausserdem keinen Pruefwert
     ein (app_bauen.py --ios), dauerWortStimmt() sagt dort also immer nein.
     30.10.2026. Am selben Wort haengt seit dem 06.11.2026 auch Beim Zahnarzt
     (ZA_WORT), siehe ladeDaten(). */
  if(!IST_IOS){
    dauerVollVerdrahten();
    hautAlleVerdrahten();
  }
  einstellungenFuerPlattform();
  try{ await starten(); }
  finally{ vorspannWeg(); }
  tonVorwaermenPlanen();   // den Kaltstart der Tonausgabe vorwegnehmen (22.10.2026)
  /* Cloud-Sicherung: beim Start nur lesen, siehe CLOUD-SICHERUNG. Mit
     CLOUD_AN = false passiert hier nichts. 19.10.2026
     Seit 17.11.2026 bei jedem Start nachsehen und ein verlorenes Schreiben
     nachholen, siehe cloudAbgleich(). */
  if(CLOUD_AN) cloudAbgleich('start');
  /* Einmal selbst nachsehen, ob das Abo laeuft. Bisher verliess sich die
     App allein auf die Meldung aboGeaendert - die aber beim Kaltstart
     abgeschickt wird, bevor es einen Zuhoerer gibt, und wegen der
     Aenderungspruefung im Plugin nie wiederholt wird. Nach einer
     Neuinstallation lief ein zahlender Abonnent deshalb als Gratisnutzer
     weiter. Gefunden am 20.09.2026. */
  vollAbgleichen();
  /* Und ob es etwas zu kaufen gibt, mit oder ohne Testwoche. Bisher fragte
     das nur showSettings(); die Kauf-Einstiege im Laden und auf den
     Schirmen ohne Leben wussten es deshalb nicht und konnten die Testwoche
     nicht nennen. Dieselbe Abfrage bei Google Play, nur frueher.
     07.10.2026 */
  produkteNachsehen();
  benPlanen();
  /* Jetzt erst die Werbung. vorspannVorbei löst auf, wenn das Logo
     ausgeblendet ist - oder spätestens nach elf Sekunden. */
  await vorspannVorbei;
  /* Erst jetzt. Der Aufruf stand vorher am Ende von nachAnmeldung(), also
     noch innerhalb von starten() - die Karte (z-index 1000) legte sich
     damit ueber den laufenden Vorspann (900). */
  geschenkNachreichen();
  /* Die Einstufung erst, wenn Googles Einwilligungsfenster durch ist -
     sonst laege es ueber der Frage. Zwei Anlaeufe: sobald die Einwilligung
     erledigt ist, und nach acht Sekunden, falls Google gar nicht antwortet.
     Steht beim zweiten das Fenster noch da, verzichtet er; dann kommt der
     erste, wenn es zu ist. Mit Promise.race allein kam die Frage nie, wenn
     jemand laenger als acht Sekunden im Einwilligungsfenster las -
     gefunden in der Browser-Probe am 30.09.2026. */
  /* updNachreichen(): Googles sanftes Update-Fenster wartet ebenfalls auf
     das Ende der Startfragen, siehe updRuhig(). updWerbungDurch erst, wenn
     werbungVorbereiten() wirklich fertig ist, nicht schon nach den acht
     Sekunden - Googles Einwilligungsfenster steht nicht im Dokument.
     10.10.2026 */
  /* agbHinweis() kurz danach: zuerst kommen Einstufung und Update-Fenster
     dran, der Hinweis wartet, bis keine Nachfrage mehr offen ist. */
  const einstufungLos = ()=>{ einstufungBereit = true; einstufungAnbieten(); updNachreichen(); setTimeout(agbHinweis, 1500); };
  werbungVorbereiten().then(()=>{ updWerbungDurch = true; einstufungLos(); });
  setTimeout(einstufungLos, 8000);
  /* Updates aus Google Play: erst jetzt, nach dem Vorspann. Ein
     Pflicht-Update startet gleich, ein sanftes wartet auf einen ruhigen
     Moment. 10.10.2026 */
  updBeimStart();
}

async function starten(){
  /* Vor allem anderen: ladeDaten() setzt die Texte (Versionszeile), und
     nachAnmeldung() zeichnet den Lernpfad. Siehe SANDBOX. 08.11.2026 */
  await sandboxPruefen();
  try{
    await ladeAudio();
    await ladeDaten();
  }catch(e){
    const err=$('err'); err.style.display='block';
    err.innerHTML = location.protocol==='file:' ? t('err.datei') : t('err.server',{fehler:esc(e.message)});
    $('pfad').style.display='none';
    return;
  }
  /* Die Stimmen einmal anstossen: manche Browser liefern sie erst danach.
     Die Auswahlliste dazu gab es bis September 2026; ihr Element steht
     nicht mehr im HTML, deshalb ist sie entfallen. */
  if(hasTTS) speechSynthesis.getVoices();
  if(!STORIES.length) $('modeStories').hidden = true;
  await hoerenPruefen();
  /* Werbung und Einwilligung stehen hier NICHT mehr. Sie laufen erst, wenn
     der Vorspann durch ist - siehe werbungVorbereiten() am Ende von init().
     Vorher sprang Googles Fenster über das Logo, während es noch lief.
     Ajdin am 19.09.2026. */
  // Kommt der Nutzer über einen Link aus einer Mail?
  const adresse = new URLSearchParams(location.search);
  const bestaetigen = adresse.get('bestaetigen');
  const neuesPw = adresse.get('neues-passwort');

  if(neuesPw && KONTEN_AN){      // ohne Konten gibt es nichts zurueckzusetzen
    kontoCode = neuesPw;
    geschichteAufraeumen();
    zeigeAnmeldung('neupw');
    return;
  }
  if(bestaetigen && KONTEN_AN){
    geschichteAufraeumen();
    const d = await postJSON('/api/konto/bestaetigen', {code: bestaetigen, bleiben: true});
    if(d.ok){
      await nachAnmeldung(d);
      // kurze Rückmeldung, dass es geklappt hat
      const balken = $('livesBar');
      if(balken){ const alt = balken.innerHTML;
        balken.innerHTML = '<span class="feedback ok">'+esc(t('konto.bestaetigt_titel'))+' ✓</span>';
        setTimeout(()=>{ renderLives(); }, 3500); }
      return;
    }
    zeigeAnmeldung('anmelden', {hinweis: kontoFehlerText(d.fehler)});
    return;
  }

  // Gilt die Anmeldung von letztem Mal noch? Das weiß nur der Server.
  /* Hier faellt die Entscheidung: Server oder allein.

     Massgeblich ist diese Anfrage, nicht die vorherige an /api/daten. Denn
     wenn dort einmal etwas hakt, darf die App NICHT stillschweigend in den
     Gerätemodus rutschen - sie wuerde sonst in den Browserspeicher schreiben
     statt in die Profildatei, und der Lernstand saehe aus wie verloren.
     Antwortet /api/konto, gibt es einen Server. Punkt. */
  let konto = {angemeldet:false}, serverDa = false;
  if(KONTEN_AN){
    try{
      const r = await fetch('/api/konto');
      if(r.ok){ konto = await r.json(); serverDa = true; }
    }catch(e){}
  }
  MIT_SERVER = serverDa;

  if(!serverDa){
    // Keine Konten, keine Anmeldung - direkt hinein.
    /* Kein "premium" mehr mitgeben: ohne Server holt es vollversionLaden()
       aus dem eigenen Schluessel, gleich hier unten in loadProgress(). */
    await nachAnmeldung({name: t('profil.ich')});
    return;
  }
  if(konto.angemeldet) await nachAnmeldung(konto);
  else zeigeAnmeldung('anmelden');
}

/* =================== ZURUECK-TASTE ===================
   Android hat unten eine eigene Zurueck-Taste. Ohne Zutun schliesst sie die
   App sofort - auch mitten in einer Lektion. Stattdessen geht sie hier eine
   Ebene zurueck, und erst auf der Startseite fragt sie nach:

     offene Nachfrage        -> die Nachfrage verneinen
     Einwilligung / Werbung  -> nichts, die haben eigene Knoepfe
     Lektion oder Test       -> wie der Abbrechen-Knopf unten, mit Nachfrage
     Unterseite              -> derselbe Weg wie der Zurueck-Knopf oben
     Startseite              -> einmal nachfragen, dann schliessen

   In der Lektion druecken wir den vorhandenen Knopf, statt seine Arbeit
   nachzubauen - so fragt die Taste genauso nach und speichert genauso.

   Das ersetzt den frueheren Beenden-Knopf vollstaendig. Am PC gibt es keine
   solche Taste; dort passiert schlicht nichts. */
/* Nach einer Antwort lief bisher ein Zeitgeber und schob die naechste
   Aufgabe hoch. Ajdin am 17.09.2026: man will in Ruhe sehen, was richtig
   und was falsch war. Jetzt wartet die App auf ein Tippen.
   Der Horcher haengt am Aufgabenfeld, nicht am ganzen Bildschirm - sonst
   wuerde der Abbrechen-Knopf darunter gleich zweierlei ausloesen.
   Die Viertelsekunde Verzoegerung verhindert, dass derselbe Klick, der die
   Antwort gegeben hat, sofort weiterblaettert. */
function weiterBeiTipp(feldId, weiter){
  const feld = $(feldId);
  if(!feld){ weiter(); return; }
  /* Egal ob Knopf oder Tipp daneben: weitergehen darf es nur einmal. Der
     Knopf hat einen eigenen Horcher, und der Horcher auf dem Feld sieht
     denselben Klick im Einfangen zuerst. */
  let schon = false;
  /* Wer eine Lektion oder einen Test abbricht, tippt dabei ausserhalb des
     Aufgabenfeldes - einmal() laeuft also nie, und der Horcher bleibt auf
     #lBody bzw. #tBody haengen; diese Felder werden nie neu gebaut, nur
     geleert. Im naechsten Test zeichnete der alte Horcher Frage 1 noch
     einmal, waehrend die Antwort schon Frage 2 zugeschrieben wurde: eine
     Frage wurde still uebersprungen, eine andere zweimal gestellt und dabei
     mit ihrer Loesung im Rueckmeldefeld angezeigt, und die Fortschrittsleiste
     zeigte einen Punkt fuer eine Frage, die nie auf dem Schirm war.
     buildLesson() und buildTest() legen bei jedem Start ein neues Lx bzw. Tx
     an - daran erkennt der Horcher, dass er aus einem alten Durchgang stammt.
     Gefunden am 26.09.2026. */
  const meinLx = Lx, meinTx = Tx;
  /* Tablet hochkant (30.10.2026): dort ist das Aufgabenfeld
     display:contents (siehe html.hoch im Stil), und der freie Platz
     zwischen Aufgabe und Antworten gehoert zum Kasten, nicht zum Feld. Ein
     Tipp genau dorthin zaehlt wie einer ins Feld. Nur auf den Kasten
     selbst - Stern und Herz in der Kopfzeile bleiben, was sie sind. Am
     Handy gibt es das nicht.
     Nur fuer die drei Felder, die dort wirklich aufgeloest sind. Bei einer
     Geschichte ist #rQ ein normales Feld, und sein Kasten ist der ganze
     Geschichtenkasten mit dem Text: ein Tipp auf dessen Rand blaetterte
     schon zur naechsten Frage, obwohl der Horcher dort bewusst nur am
     Fragenfeld sitzt (showStoryQ). Gefunden in der Pruefung am 30.10.2026. */
  const aufgeloest = (feldId === 'lBody' || feldId === 'tBody' || feldId === 'eBody') &&
    document.documentElement.classList.contains('hoch');
  const karte = aufgeloest ? feld.closest('.card') : null;
  const frei = e => { if(e.target === karte) los(e); };
  const ab = ()=>{
    feld.removeEventListener('click', los, true);
    if(karte) karte.removeEventListener('click', frei);
  };
  const einmal = ()=>{
    if(schon) return;
    schon = true;
    ab();
    weiter();
  };
  /* Ein Tipp auf einen Hörknopf oder auf die Tempoleiste soll NUR das tun -
     sonst wären sie nach der Antwort unbenutzbar, weil derselbe Tipp sofort
     die nächste Aufgabe holt. */
  const los = (e)=>{
    /* Der Merker war seit dem 26.09.2026 da, wurde aber nie gelesen. Ein
       Horcher aus einem alten Durchgang haengt sich jetzt beim ersten Tipp
       selbst ab und laesst den Klick durch. Gefunden in der Gegenpruefung
       am 01.10.2026. */
    if(Lx !== meinLx || Tx !== meinTx){ ab(); return; }
    if(e && e.target && e.target.closest && e.target.closest('.listen, .wortton, .tempo')) return;
    einmal();
  };
  /* Ajdin am 18.09.2026: ein eigener Knopf mit Kasten drum. Der Hinweis
     "Tippen für die nächste Aufgabe" war leicht zu übersehen, und man wusste
     nicht, wohin man tippen soll. Tippen geht weiterhin überall. */
  if(!feld.querySelector('.weiterbox')){
    const kasten = document.createElement('div');
    kasten.className = 'row weiterbox';
    kasten.innerHTML = '<button type="button" class="btn know">'+esc(t('task.weiter'))+'</button>';
    if(feldId === 'lBody' || feldId === 'tBody' || feldId === 'eBody'){
      /* Rueckmeldung, Loesung und Weiter zusammen unter die Aufgabe - bei
         Schreib- und Lueckenaufgaben stand sonst der leere Pruefen-Platz
         dazwischen. Es sind dieselben Knoten (#xFb), spaetere Aenderungen
         daran kommen also an. Die Einstufung (eBody) seit 19.10.2026: ihr
         Weiter stand bis zu 43 px anders als in der Lektion. */
      const unten = document.createElement('div');
      unten.className = 'antwortfeld';
      feld.querySelectorAll(':scope > .feedback, :scope > .loesung').forEach(e => unten.appendChild(e));
      unten.appendChild(kasten);
      feld.appendChild(unten);
    } else {
      feld.appendChild(kasten);
    }
    kasten.querySelector('button').addEventListener('click', einmal);
    /* Ist eine Aufgabe laenger als der Schirm - kleines Handy, lange
       Grammatikantworten -, laege Weiter sonst unter dem Rand. 'nearest'
       bewegt nichts, solange er sichtbar ist. */
    try{ kasten.scrollIntoView({block:'nearest', behavior:'smooth'}); }catch(e){}
  }
  // 900 ms statt 250: nach der Antwort läuft jetzt das Wort. Wer gleich
  // tippt, soll es wenigstens angehört haben können. Der Knopf selbst
  // bekommt seinen Rahmen erst dann - vorher könnte ihn derselbe Klick
  // treffen, der gerade geantwortet hat.
  // WEITER_NACH steht bei ansagen(): die Ansage des Ergebnisses wartet
  // darauf, dass der Fokus hier auf Weiter liegt (17.10.2026).
  setTimeout(()=>{
    if(schon) return;
    feld.addEventListener('click', los, true);
    if(karte) karte.addEventListener('click', frei);
    const k = feld.querySelector('.weiterbox .btn');
    if(k) try{ k.focus({preventScroll:true}); }catch(e){ k.focus(); }
    ansageNachFokus();
  }, WEITER_NACH);
}

function sichtbar(id){ const e = $(id); return !!e && e.style.display !== 'none'; }

/* Wort oder Satz? Klammerzusätze und Varianten hinter „ / " zählen nicht
   mit, sonst wäre „morgen (der nächste Tag)" ein Satz. Ab drei Wörtern ist
   es einer. Das Fragezeichen entscheidet nichts – „Wer?" bleibt ein Wort. */
function istWort(de){
  const kern = String(de || '').replace(/\([^)]*\)/g, ' ').split(' / ')[0];
  return kern.split(/\s+/).filter(Boolean).length <= 2;
}
/* Gezaehlt wird die DEUTSCHE Bedeutung, nicht die uebersetzte. w.de ist nach
   uebersetzungen.anwenden() die Bedeutung der Oberflaechensprache, und die hat
   je Sprache eine andere Wortzahl. Auf Franzoesisch galt "bankomat"
   ("distributeur de billets", drei Woerter) als Satz, wurde in seine bosnischen
   Teile zerlegt, fand keinen Woerterbucheintrag und fiel ganz aus der Liste:
   im Level Bank standen 15 statt 23 Zeilen, acht Vokabeln fehlten, auf
   Daenisch fehlten im Level Tagesablauf zehn. Die Kennung w.id baut start.py
   als "bedeutung:wort" VOR dem Uebersetzen, sie ist in allen acht Sprachen
   dieselbe. Damit zeigt die Liste ueberall dieselben Zeilen wie auf Deutsch.
   Gefunden am 26.09.2026. Eingehaengt erst am 07.10.2026: bis dahin stand
   die Funktion hier, aber schonVokabel() und wortzeilen() fragten weiter
   istWort(w.de), und in sieben Sprachen fehlten weiter Vokabeln. */
function grundBedeutung(w){
  const id = String(w.id || ''), bs = String(w.bs || '');
  const schnitt = id.length - bs.length - 1;
  return schnitt > 0 ? id.slice(0, schnitt) : String(w.de || '');
}

/* ---------- Die Liste „Wörter dieses Levels" ----------
   Sätze werden in ihre Wörter zerlegt: aus „Imam dva brata" wird
   ich habe / zwei / Bruder. Die Bedeutungen kommen aus dem Wörterbuch
   der App.
   Was anderswo schon eine eigene Vokabel ist, kommt nicht noch einmal –
   „dva" steht bei den Zahlen, da muss es nicht bei jedem Satz wieder
   auftauchen. Ajdin am 17.09.2026.
   Feste Wendungen wie „Guten Tag" bleiben ganz, denn sie sind schon
   Wörter im Sinne von istWort(). */
const wortform = s => strip(s).replace(/[^a-z]/g, '');
let vokabelFormen = null, dictFormen = null;

function schonVokabel(){        // alle bosnischen Einzelwörter der ganzen App
  if(vokabelFormen) return vokabelFormen;
  vokabelFormen = new Set();
  CATEGORIES.forEach(k => k.words.forEach(w => {
    if(!istWort(grundBedeutung(w))) return;
    String(w.bs).split(' / ').forEach(v => {
      const t = v.trim();
      if(t && !t.includes(' ')) vokabelFormen.add(wortform(t));
    });
  }));
  return vokabelFormen;
}
function dictBedeutung(wort){
  if(!dictFormen){
    dictFormen = new Map();
    for(const k in DICT) dictFormen.set(wortform(k), DICT[k]);
  }
  return dictFormen.get(wortform(wort)) || null;
}
function wortzeilen(c){
  const zeilen = [], gesehen = new Set(), schon = schonVokabel();
  c.words.forEach(w => {
    const kann = known.has(w.id);
    if(istWort(grundBedeutung(w))){
      const f = wortform(String(w.bs).split(' / ')[0]);
      if(gesehen.has(f)) return;
      gesehen.add(f);
      zeilen.push({de: w.de, bs: w.bs, kann});
      return;
    }
    (String(w.bs).match(/[\p{L}\p{M}'’-]+/gu) || []).forEach(teil => {
      const f = wortform(teil);
      if(!f || gesehen.has(f) || schon.has(f)) return;
      const bed = dictBedeutung(teil);
      if(!bed) return;              // ohne Bedeutung wäre die Zeile leer
      gesehen.add(f);
      zeilen.push({de: bed, bs: teil, kann});
    });
  });
  return zeilen;
}

async function zurueckTaste(){
  /* Pflicht-Update (10.10.2026): hinter der Karte ist nichts zu bedienen,
     also schliesst die Taste die App. Google raet fuer diesen Fall, zu
     erklaeren und dann den Ablauf neu zu starten oder zum Schliessen
     aufzufordern. Vor allem anderen, denn die Karte liegt ueber allem.
     Speichern darf das Schliessen nicht verhindern, daher try. */
  if(document.querySelector('.updsperre')){
    const P = window.Capacitor && window.Capacitor.Plugins;
    if(P && P.App){ try{ await saveProgress(); }catch(e){} P.App.exitApp(); }
    return;
  }
  if(frageSchliessen){ frageSchliessen(); return; }
  if(document.querySelector('.einwilligung, .werbung')) return;
  if(sichtbar('levelView') && sichtbar('lesson')){ $('lQuit').click(); return; }
  if(sichtbar('levelView') && sichtbar('test')){   $('tQuit').click(); return; }
  if(backTarget){ backTarget(); return; }
  const P = window.Capacitor && window.Capacitor.Plugins;
  if(!P || !P.App) return;                       // am PC nichts zu schliessen
  /* Startseite auf Android (1.5, Optimierung Punkt 7, Ajdin 20.11.2026):
     die Taste legt die App weg wie die Home-Taste, ohne Rueckfrage. Beim
     naechsten Oeffnen ist sie sofort da, solange Android sie im Speicher
     haelt. Das macht Android seit Fassung 12 auch bei anderen Apps so.
     Gesichert wird vorher wie beim Beenden; der Wechsel in den Hintergrund
     sichert ausserdem ueber visibilitychange (cloud_seiten.js). Speichern
     darf das Weglegen nicht verhindern, daher try. Die Karte zum
     Pflicht-Update oben beendet weiter. */
  if(PLATTFORM === 'android' && typeof P.App.minimizeApp === 'function'){
    try{ await saveProgress(); }catch(e){}
    P.App.minimizeApp();
    return;
  }
  if(await frage(t('beenden.frage'), t('beenden.text'),
                 t('beenden.ja'), t('beenden.nein'))){
    await saveProgress();
    P.App.exitApp();
  }
}

(function(){
  const P = window.Capacitor && window.Capacitor.Plugins;
  if(P && P.App && P.App.addListener) P.App.addListener('backButton', zurueckTaste);
})();

/* Alle Teile da (G7)? TEILE_ERWARTET = Zahl der Zaehlzeilen (var teileDa = ...) - eine je
   Teil vor diesem. Fehlt eine, ist ein Teil beim Laden ausgefallen: dann
   nicht starten (kein halber Zustand, nichts speichern), sondern den
   Fehler zeigen und laut werfen. t() nur in try, ohne $ und vorspannWeg():
   die koennen gerade die sein, die fehlen. 20.11.2026 */
const TEILE_ERWARTET = 34;
function teileFehlen(){
  const fehler = 'App-Teile: ' + teileDa + ' von ' + TEILE_ERWARTET;
  try{
    const v = document.getElementById('vorspann');
    if(v) v.style.display = 'none';
    const p = document.getElementById('pfad');
    if(p) p.style.display = 'none';
    const e = document.getElementById('err');
    e.style.display = 'block';
    try{ e.innerHTML = t('err.server', {fehler}); }
    catch(x){ e.textContent = 'Zmaj konnte nicht starten. Bitte die App schließen und neu öffnen. '
                              + '/ Zmaj could not start. Please close the app and open it again. (' + fehler + ')'; }
  }catch(x){}
  throw new Error('Zmaj startet nicht: ' + fehler);
}
if(teileDa !== TEILE_ERWARTET) teileFehlen();
skripteDa = true;
init();
