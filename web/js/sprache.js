/* ---------------- Sprache ----------------
   Alle Texte der Oberfläche kommen vom Server aus sprachen.py.
   t('schluessel')            einfacher Text
   t('schluessel', {name:…})  Text mit Platzhaltern
   tp('schluessel', n)        Einzahl/Mehrzahl, {n} wird eingesetzt
   Die gewählte Sprache merkt sich der Browser (gilt für dieses Gerät). */
let SPRACHEN = [], T = {}, UEBERSETZT = {fertig:0, gesamt:0};
let SPRACHE = 'de';
try{ SPRACHE = localStorage.getItem('zmaj_sprache') || (navigator.language||'de').slice(0,2).toLowerCase(); }catch(e){}
/* Norwegisch meldet nicht jedes Geraet als "nb": aeltere Android-Fassungen
   und manche Browser sagen "no", Nynorsk-Einstellungen "nn". Ohne das
   startete die App dort auf Englisch. 12.10.2026 */
if(SPRACHE === 'no' || SPRACHE === 'nn') SPRACHE = 'nb';
/* Die Versionsnummer der App (30.10.2026, Ajdin: "ja mach so"). Bis v108
   stand "1.0" fest in sprachen.py, in app.fuss und app.ueber_kurz aller
   acht Sprachen - und blieb dort, waehrend nur der versionCode stieg.
   Jetzt steht dort {version}, und t() setzt diesen Wert ein.
   Die Nummer selbst steht nur an einer Stelle: versionName in
   app/build.gradle der Android-Huelle. app_bauen.py (version_einsetzen)
   ueberschreibt die Zeile darunter beim Bauen in der KOPIE www/index.html
   damit, in der Test-App mit "-test". Hier steht nur der Rueckfallwert
   fuer die Web-Demo, start.py und die Tests. Die Zeile muss genau so,
   am Zeilenanfang und genau einmal dastehen, sonst bricht der Bau ab. */
/* APP_VERSION steht im Bauwerte-Block vor diesem Skript. */
const FALLBACK = {   // nur nötig, wenn der Server gar nicht antwortet
  /* Updates aus Google Play, zweisprachig wie err.server: gerade eine
     Fassung, deren Inhalte nicht laden, braucht vielleicht das Pflicht-
     Update - dann stuende sonst der nackte Schluessel auf der Karte.
     10.10.2026 */
  'upd.bereit':'Update bereit · Update ready',
  'upd.neustart':'Neu starten · Restart',
  'upd.pflicht_titel':'Wichtiges Update · Important update',
  'upd.pflicht_text':'Zmaj braucht ein Update, bevor es weitergeht. · Zmaj needs an update before you can continue.',
  'upd.pflicht_knopf':'Jetzt aktualisieren · Update now',
  'err.datei':'<b>So geht es nicht:</b> Die Datei index.html wurde direkt geöffnet. Die App braucht den Server aus <b>start.py</b>.<br><br><b>So geht es:</b> Auf dem Desktop die Verknüpfung <b>„Bosnisch lernen“</b> doppelklicken. Oder in Thonny <b>start.py</b> öffnen und auf Run (F5) drücken.<br>Der Browser öffnet dann von selbst <b>http://localhost:8000</b>. Diese Adresse benutzen, nicht die Datei.',
  /* Auf dem Handy gibt es weder Thonny noch start.py. Als Getter, damit
     window.Capacitor sicher schon da ist, und zweisprachig: welche Sprache
     der Nutzer spricht, wissen wir hier noch nicht - die Uebersetzungen
     sind ja gerade das, was nicht geladen werden konnte. */
  get 'err.server'(){ return (window.Capacitor && window.Capacitor.Plugins)
    ? 'Die Inhalte konnten nicht geladen werden. Bitte die App schließen und noch einmal öffnen.<br><br>The content could not be loaded. Please close the app and open it again.<br><br><small>{fehler}</small>'
    : 'Konnte die Vokabeln nicht laden. Läuft der Server noch? Verknüpfung „Bosnisch lernen“ anklicken oder start.py in Thonny starten, dann diese Seite neu laden. Fehler: {fehler}'; }
};
function fuelle(s, vars){
  return vars ? s.replace(/\{(\w+)\}/g, (m,k)=> vars[k]!==undefined ? vars[k] : m) : s;
}
/* Texte fuer iPhone und iPad (30.10.2026, iOS_Plan.md 3.6). Wo ein Text
   Google Play, den Play Store oder Android nennt, gibt es in sprachen.py
   eine Fassung "<schluessel>_ios" - Apple lehnt Apps ab, die andere
   Plattformen nennen (Richtlinie 2.3.10), und auf dem iPhone ist Apple der
   Verkaeufer. Auf iOS gilt zuerst diese Fassung, sonst die gewoehnliche.
   Android und Browser fragen nie nach _ios. */
function textSchluessel(key){
  return (IST_IOS && T[key + '_ios'] !== undefined) ? key + '_ios' : key;
}
function t(key, vars){
  key = textSchluessel(key);
  let s = T[key] !== undefined ? T[key] : FALLBACK[key];
  if(s === undefined) return key;
  if(s.indexOf('|') >= 0) s = s.split('|')[0];
  /* {version} kommt immer aus APP_VERSION (30.10.2026), ohne dass ein
     Aufrufer es mitgeben muss - so gilt es fuer die data-t-Elemente aus
     applyTexts() (Fuss, Versionszeile) wie fuer jeden t()-Aufruf. Nur wenn
     der Platzhalter dasteht: alle anderen Texte laufen wie vorher. */
  if(s.indexOf('{version}') >= 0) vars = Object.assign({version: versionText()}, vars);
  return fuelle(s, vars);
}
/* Die Nummer, wie Fuss und Versionszeile sie zeigen. In der Sandbox der
   Test-App mit einem kurzen Hinweis dahinter (08.11.2026), sonst genau
   APP_VERSION. Nur Ajdin sieht ihn, deshalb nur auf Deutsch. */
function versionText(){ return APP_VERSION + (SANDBOX ? ' · Sandbox: alles offen' : ''); }
/* Franzoesisch stellt das Substantiv nach null in die Einzahl ("0 nouveau
   mot"); Deutsch, Englisch, Schwedisch, Norwegisch, Daenisch und
   Niederlaendisch nehmen die Mehrzahl, Tuerkisch hat nur eine Form. Ohne diese
   Ausnahme stand auf dem Ergebnisschirm einer Lektion ohne neue Woerter
   "+0 nouveaux mots" und in den Einstellungen am ersten Tag "Serie : 0 jours".
   Eine Liste statt eines Vergleichs auf 'fr', damit eine spaetere Sprache mit
   derselben Regel nur hier eingetragen werden muss. Gefunden am 26.09.2026. */
const EINZAHL_BEI_NULL = ['fr'];
function tp(key, n, vars){
  key = textSchluessel(key);
  const s = T[key] !== undefined ? T[key] : key;
  const teile = s.split('|');
  const einzahl = n === 1 || (n === 0 && EINZAHL_BEI_NULL.includes(SPRACHE));
  const gewaehlt = (einzahl || teile.length < 2) ? teile[0] : teile[1];
  return fuelle(gewaehlt, Object.assign({n:n}, vars||{}));
}
function applyTexts(){
  document.documentElement.lang = SPRACHE;
  document.title = t('app.titel');
  // {anbieter} steht in den Rechtstexten und wird überall gleich gefüllt,
  // damit Name und Anschrift nur an einer Stelle gepflegt werden müssen.
  const anbieter = t('set.anbieter');
  // Dazu die gemalten Symbole fuer {herz}, {muenze} und {einstellungen}
  // (24.10.2026, siehe symbol()) - im Fuss steht das Zahnrad.
  const vars = symbolTexte({anbieter});
  // data-zeichen: ein gezeichnetes Zeichen davor (zeichen(), 14.11.2026),
  // mit geschuetztem Leerzeichen am ersten Wort
  document.querySelectorAll('[data-t]').forEach(el=>{
    el.innerHTML = (el.dataset.zeichen ? zeichen(el.dataset.zeichen) + '\u00a0' : '') + t(el.dataset.t, vars);
  });
  document.querySelectorAll('[data-t-title]').forEach(el=>{ el.title = t(el.dataset.tTitle); });
  document.querySelectorAll('[data-t-ph]').forEach(el=>{ el.placeholder = t(el.dataset.tPh); });
}
/* Verweise in den Rechtstexten (28.10.2026). Mit Kontaktformular nennt das
   Impressum zmaj-lernapp.github.io/kontakt.html als Verweis. Angetippt
   oeffnet er im Browser des Geraets, wie der Play Store und die Kanaele -
   ohne das verliesse die App ihre eigene Seite. Erst auf Tippen, nie von
   allein: kein Netz zur Laufzeit (AGENTS.md, Regel 6). */
document.addEventListener('click', e=>{
  const a = (e.target && e.target.closest) ? e.target.closest('.legal a[href^="https://"]') : null;
  if(!a) return;
  e.preventDefault();
  try{ window.open(a.href, '_blank', 'noopener'); }catch(x){}
});

let SECTIONS = [], CATEGORIES = [], SENTENCES = [], GRAMMAR = {}, STORIES = [], DICT = {};
let DICT_TON = {};         // Ton je Bedeutung der Woerterbuch-Woerter, siehe eigenerTon() (21.11.2026)
let SATZBAU = [];          // Sätze aus Kacheln (vokabeln.py SATZBAU), seit 13.10.2026
let ZA = null;             // Beim Zahnarzt: {sektion, kategorien}, siehe zaLevel() (06.11.2026)
let known = new Set(), passed = new Set(), read = new Set(), days = new Set();
/* Ob known schon beim Laden Woerter hatte - oder nach dem Einlesen einer
   Sicherung, nach dem Zusammenfuehren mit der Cloud. Nur dann zaehlen sie
   fuer das Tor, siehe hatGelernt(). Gesetzt in standUebernehmen(). */
let gewusstGeladen = false;
let frost = new Set();    // Tage, die ein Serienschutz gerettet hat
let tagwerk = {};         // Tag -> Zähler, z.B. {'2026-09-14': {auf:23, ric:18}}
var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
