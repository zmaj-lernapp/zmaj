/* ---- Fundament für die Wegmarken (19.09.2026) ----
   gefeiert = schon gefeierte Wegmarken, z. B. "tage100". Ohne das feiert
              die App dieselbe Marke bei jedem Neuladen wieder.
   rekord   = die längste Serie, die jemals lief. Überlebt das Reißen.
   wann     = wann etwas geschafft wurde: "lv:<id>" und "gs:<id>" -> Datum.
              Die Kürzel davor, damit sich Level- und Geschichten-Kennungen
              nicht ins Gehege kommen. Dazu ein Schluessel ohne Doppelpunkt:
              "alleWoerter" = der Tag, an dem das letzte unbekannte Wort
              fiel (siehe neuNochMoeglich()). */
let gefeiert = new Set();
/* Einstufung und Wiederholen - erklaert weiter unten bei EINSTUFUNG und
   WIEDERHOLEN. Hier oben, weil standUebernehmen() sie setzt. */
let einstufung = null;    // null = noch nie gefragt, sonst {tag, wahl, bis}
let topf = {};            // Schluessel -> {typ, n, z}
let stern = {};           // Schluessel -> {z, r}, siehe STERN (19.10.2026)
const STERN_MAX = 300;    // so viele Sterne hoechstens; hier oben, standUebernehmen() braucht ihn
/* Die Lernkartei (zeitgesteuerte Wiederholung, v110) - erklaert weiter
   unten bei LERNKARTEI. Hier oben aus demselben Grund wie STERN_MAX. */
let kartei = {tag: 0, n: 0, w: {}};
const KARTEI_ABSTAENDE = [1, 3, 7, 14, 30, 90, 180];   // Tage bis zum naechsten Termin, je Stufe 0 bis 6
let bewertung = {gezeigt:[], nein:false, bewertet:false};   // siehe BEWERTUNG
let rekord = 0;
let wann = {};
let muenzenGes = 0, muenzenAus = 0;   // jemals verdient / jemals ausgegeben
let besitz = new Set();   // gekaufter Zierrat, z. B. "hut"
/* Alle Muenz-Stuecke ohne Kauf, nur fuer uns - siehe hautAlleVerdrahten().
   Wie der Dauerschalter nur im Geraetespeicher, nie im Lernstand und nie in
   der Sicherungsdatei: besitz bleibt, was wirklich gekauft ist. 19.10.2026 */
const HAUT_ALLE_SCHLUESSEL = 'zmaj_hautalle';
let hautAlle = false;
// Auf iOS gibt es den Schalter nicht (siehe init(), 30.10.2026).
try{ hautAlle = !IST_IOS && localStorage.getItem(HAUT_ALLE_SCHLUESSEL) === '1'; }catch(e){}
/* Zaehlt fuer Laden, Tragen und Drachen als besessen: gekauft, oder bei
   eingeschaltetem Schalter jedes Stueck mit Muenzpreis - erst nur die
   Farben, seit 20.10.2026 auch Kopf, Brille und Hals (Ajdin: "gib alle
   skins, muss die austesten"). Die Stuecke der Vollversion haengen
   weiter allein an unlimited(). */
const hatStueck = id => besitz.has(id)
  || (hautAlle && ZIERRAT.some(w => w.id === id && !w.voll));
// Aufsetzen oder abnehmen ist eine Geraeteeinstellung wie Ton und Animation.
// Der Wert kommt weiter unten aus localStorage, sobald pref() bereitsteht.
/* Getragen wird jetzt mehreres: eine durch Komma getrennte Liste, hoechstens
   ein Stueck je Gruppe. Bewusst eine Zeichenkette und kein Feld - alte
   Sicherungen enthalten dort schlicht "krone", und die laufen damit weiter. */
let getragen = '';   // z. B. "krone,brille,trikot", leer = nichts
/* Was der Drache wirklich traegt. Stuecke der Vollversion fallen hier
   heraus, sobald sie ausgelaufen ist - im Speicher bleiben sie stehen,
   also haengt alles wieder am Drachen, wenn das Abo zurueckkommt. Eine
   Stelle, und damit gilt es fuer den Laden, den Drachen und die Farbe
   gleichermassen. */
/* Die rohe Liste - alles, was gespeichert ist. GERECHNET wird mit ihr,
   ANGEZEIGT wird mit getragenListe(). Stand das Rechnen auf der
   gefilterten Liste, schrieb ein einziger Tipp im Laden bei abgelaufenem
   Abo die gekuerzte Liste zurueck - Krone, Mantel, Farbe und Funkeln waren
   damit endgueltig weg, entgegen dem Versprechen zwei Zeilen hoeher.
   Gefunden in der Gegenpruefung am 29.09.2026. */
const getragenRoh = () => String(getragen || '').split(',').filter(Boolean);
const getragenListe = () => getragenRoh()
  .filter(id => !istVollStueck(id) || unlimited());
const traegt = id => getragenListe().indexOf(id) >= 0;
function setzeGetragen(liste){
  getragen = liste.join(',');
  try{ localStorage.setItem('zmaj_getragen', getragen); }catch(e){}
}
const muenzen = () => Math.max(0, muenzenGes - muenzenAus);
let lives = {anzahl: LEBEN_MAX, zeit: 0}, premium = false;
let schutz = {anzahl: 1, zeit: 0};
let profil = '';   // Name des angemeldeten Kontos
// Der Server weiß aus dem Sitzungs-Cookie, wer fragt. Deshalb steht hier
// kein Name mehr in der Adresse - den konnte früher jeder austauschen.
const apiF = () => '/api/fortschritt';

/* ===== Mit Server oder allein? =====
   Am PC antwortet start.py, dann bleibt alles wie bisher: Konten, Anmeldung,
   Fortschritt in der Profildatei. Auf dem Handy antwortet niemand - dann
   liegt alles im Speicher des Browsers, und es gibt keine Anmeldung.
   Gesetzt wird der Schalter einmal beim Start in holeInhalt(). */
let MIT_SERVER = false;
/* ===== Konten an oder aus? =====
   Steht dieser Schalter auf false, verhaelt sich die App ueberall so wie auf
   dem Handy: kein Anmeldeformular, kein Profilknopf, kein "Konto loeschen",
   und der Lernstand liegt im Geraetespeicher. /api/konto wird dann gar nicht
   erst gefragt.

   Ajdin am 26.09.2026: die Anmeldung soll weg bleiben, bis ein Server
   gemietet ist. Zum Wiedereinschalten genuegt true - das Anmelde-HTML,
   zeigeAnmeldung() und die Kontoverwaltung stehen alle noch im Programm.

   WICHTIG: Der Schalter muss MIT_SERVER mitsteuern, nicht nur die Anzeige.
   Bliebe MIT_SERVER auf true, schriebe saveProgress() per POST an
   /api/fortschritt mit einem Profil, das der Server nicht kennt - der
   Lernstand waere weg, ohne Meldung. Dieser Fehler ist am 20.09.2026 schon
   einmal aufgetreten. */
const KONTEN_AN = false;
/* Solange der Lernstand nicht gelesen ist, darf nichts geschrieben werden.
   Der visibilitychange-Horcher haengt schon beim Einlesen des Skripts am
   Dokument, loadProgress() laeuft aber erst nach Vorspann, Toenen, Inhalt
   und Kontoabfrage. Dazwischen liegen mehrere Sekunden. */
let standGeladen = false;
const LOKAL_STAND = 'zmaj_stand';
const LOKAL_ID    = 'zmaj_id';

/* Eine zufaellige Kennung, einmal je Geraet erzeugt. Sie entscheidet, welche
   drei Tagesaufgaben gezogen werden. Der Profilname taugt dafuer nicht mehr:
   ohne Konten hiesse jeder gleich, und alle bekaemen dieselben drei. */
function geraetId(){
  let id = '';
  try{ id = localStorage.getItem(LOKAL_ID) || ''; }catch(e){}
  if(!id){
    id = 'g' + Math.random().toString(36).slice(2) + '-' + Date.now().toString(36);
    try{ localStorage.setItem(LOKAL_ID, id); }catch(e){}
  }
  return id;
}
const questSaat = () => MIT_SERVER ? profil : geraetId();

function lokalLesen(){
  try{ return JSON.parse(localStorage.getItem(LOKAL_STAND) || '{}') || {}; }
  catch(e){ return {}; }
}
function lokalSchreiben(d){
  try{ localStorage.setItem(LOKAL_STAND, JSON.stringify(d)); return true; }
  catch(e){ return false; }   // Speicher voll oder gesperrt
}
let homeMode = 'words';
/* backTarget ist der Weg eine Ebene zurück – oder null, wenn wir auf der
   Startseite stehen. Daran hängen beide Wege zurück: die Zurück-Taste des
   Handys und, falls es keine gibt, der Knopf oben rechts.

   Den Knopf gibt es nur dort, wo das Gerät keinen eigenen hat: am PC im
   Browser. Auf dem Handy ist er doppelt gemoppelt und nimmt oben Platz
   weg – Ajdin am 16.09.2026: "man kann doch selbst mit dem handy zurück
   gehen". Die Weiche ist dieselbe wie überall: ist das Capacitor-Plugin
   da, läuft die App nativ.
   Seit 30.10.2026 nur auf Android: das iPhone hat keine Zurueck-Taste,
   und ohne den Knopf kaeme man dort aus keiner Unterseite mehr heraus
   (iOS_Plan.md 3.5). Auf iOS steht er also wie im Browser oben rechts. */
const geraeteZurueck = () => PLATTFORM === 'android' && !!(window.Capacitor && window.Capacitor.Plugins
                                && window.Capacitor.Plugins.App);
let backTarget = null;
function setzeZurueck(text, ziel){
  backTarget = ziel;
  const k = $('btnBack');
  if(!k) return;
  const vorher = k.style.display + '|' + k.textContent;
  if(!ziel || geraeteZurueck()) k.style.display = 'none';
  /* aria-label: Im knappen Kopf (header.knapp, siehe kopfEng) zeigt die
     Taste nur den Pfeil, das Wort hat dort die Schriftgroesse 0. Damit
     Bildschirmleser es trotzdem sicher vorlesen, steht derselbe Text auch
     hier (16.11.2026). */
  else { k.style.display = 'inline-block'; k.textContent = text; k.setAttribute('aria-label', text); }
  /* Die Taste macht den Kopf breiter (oder schmaler): neu messen, ob er
     noch in eine Zeile passt. Pruefbefund vom 24.10.2026: bei 360 px und
     130 % Schrift ragte "← Geschichten" 52 px ueber den Rand, die Seite
     liess sich seitlich schieben - kopfEng() lief nur, wenn die Leben neu
     gezeichnet wurden. Auf dem Handy bleibt die Taste immer versteckt,
     dort aendert sich nichts und es wird nichts gemessen. */
  if(k.style.display + '|' + k.textContent !== vorher) kopfEng();
}
let catIdx = 0;

const $ = id => document.getElementById(id);
/* getBoundingClientRect und der zoom der Tablets (30.10.2026, siehe GROSS
   oben im Kopf). Chrome ab 128 (genormtes zoom) liefert die Masse in
   Bildschirmpunkten, mit dem zoom darin. Aeltere WebViews (die App laeuft
   ab Android 7, dort endet Chrome bei 119) und Safari bis zur Korrektur
   von WebKit-Fehler 77998 (im WebKit-Quelltext am 07.11.2025) teilen sie
   durch den zoom.
   Welche Art das Geraet hat, misst ein unsichtbarer Kasten von 100 Punkten
   einmal aus. rectFaktor() ist dann der Faktor von getBoundingClientRect
   zu Bildschirmpunkten (fuer innerHeight und scrollBy), rectFaktor()/GROSS
   der zu Punkten der Seite (fuer translate und scrollWidth).
   Ohne zoom (Handy) ist beides genau 1, dort rechnet alles wie vorher. */
let rectMitZoom = null;
function rectFaktor(){
  if(GROSS === 1) return 1;
  if(rectMitZoom === null){
    const p = document.createElement('div');
    p.style.cssText = 'position:absolute; left:0; top:0; width:100px; height:1px; visibility:hidden; pointer-events:none';
    document.body.appendChild(p);
    rectMitZoom = p.getBoundingClientRect().width > 50 * (1 + GROSS);   // mit zoom 100*GROSS, ohne 100
    p.remove();
  }
  return rectMitZoom ? 1 : GROSS;
}
/* ---- Beim Zahnarzt (06.11.2026) ----
   Gedacht fuer Praxisteams, die mit Patienten reden wollen, die nur
   Bosnisch sprechen. Ajdin: "das interssiert 1% der menschen", also versteckt:
   siebenmal auf die Versionszeile, dann das Wort ZA_WORT (dauerVollVerdrahten).
   Es schaltet nichts Bezahltes frei und darf deshalb hier stehen.
   Der Teil steht mit Absicht NICHT in CATEGORIES und SECTIONS. Alles, was
   zaehlt - Level, Woerter, Fortschritt, Weitermachen, Einstufung, Kartei,
   Wiederholen -, rechnet ueber diese beiden Listen und sieht ihn damit nie,
   auch nicht bei dem, der ihn freigeschaltet hat. Nur der Lernpfad (showPath)
   und die Wege durch ein Level kennen ihn: seine Level haben die Nummern ab
   CATEGORIES.length (levelNach), und imZa() sagt, ob gerade eins offen ist.
   Der Lernstand steht in known und passed wie jeder andere. So geht er ohne
   eigene Regel mit dem Konto, durch die Sicherung und durchs Zusammenfuehren.
   Seine Kennungen fangen mit ZA_VORN an (zahnarzt.py); gezaehlt wird mit
   ohneZa(). Der Schalter steht im Stand (Feld zahnarzt), damit der Teil nach
   einer Neuinstallation von selbst wieder da ist. Eine Lektion hier ist kein
   Lerntag (also auch keine Wegmarke und kein anderes Bild auf der Startseite),
   zaehlt nicht fuer Tagesaufgaben und Muenzen und landet nicht in Kartei,
   Fehler-Topf und Sternen. */
const ZA_WORT = 'zahnarzt', ZA_VORN = 'za|';
let zaSchalter = {an: false, z: 0};
const zaLevel = () => ZA ? ZA.kategorien : [];
const zaAn = () => !!(ZA && zaSchalter.an);
const istZa = x => typeof x === 'string' && x.startsWith(ZA_VORN);
const ohneZa = menge => { let n = 0; menge.forEach(x => { if(!istZa(x)) n++; }); return n; };
const imZa = () => CATEGORIES.length > 0 && catIdx >= CATEGORIES.length;
const levelNach = i => i < CATEGORIES.length ? CATEGORIES[i] : zaLevel()[i - CATEGORIES.length];
var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
