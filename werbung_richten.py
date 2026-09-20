# -*- coding: utf-8 -*-
"""Behebt die Befunde aus WERBUNG_PRUEFUNG.md.

ERST NACH DEM GESCHLOSSENEN TEST LAUFEN LASSEN. Jede Einreichung setzt
Googles Pruefuhr zurueck. Gehoert in denselben Build wie admob_scharf.py.

WAS HIER PASSIERT, nach Befundnummern aus WERBUNG_PRUEFUNG.md:

 1 + 2  Die Anzeige wird unmittelbar vor dem Zeigen noch einmal gefragt,
        ob sie ueberhaupt noch darf. Zwischen der Entscheidung und dem
        Zeigen liegt ein Ladevorgang von unbekannter Dauer - in dieser
        Zeit kann der Nutzer laengst weitergegangen sein oder die App
        weggelegt haben. Beides verbietet Google ausdruecklich, und beides
        war moeglich. Dazu wird der 1,2-Sekunden-Wecker jetzt abgeraeumt,
        wenn die App in den Hintergrund geht.

 3      maxAdContentRating. Ohne die Angabe darf AdMob Anzeigen bis
        MatureAudience ausliefern - in einer App mit USK 0 / PEGI 3.

 4      testingDevices. Nach dem Kennungstausch gaebe es sonst keinen Weg
        mehr, auf dem eigenen Handy Testanzeigen zu bekommen; jeder eigene
        Tipp waere ungueltiger Traffic.

 5 + 10 Der Platzhalter-Kasten ("Hier erscheint die Werbung") wird auf dem
        Geraet nicht mehr gebaut. Er war als Attrappe fuer den PC gedacht,
        erschien aber auch auf dem Handy, sobald AdMob nicht hochkam - und
        vergab dort sogar das Leben.

 6      Nach Googles Datenschutzfenster wird der Stand neu eingelesen. Ein
        Widerruf wirkte sonst erst nach einem Neustart.

 7      Das selbstgebaute Einwilligungsfenster tritt auf dem Geraet ganz
        zurueck. Es ist kein zertifiziertes CMP, und wer es beantwortet
        hatte, wurde beim naechsten Start von Google ein zweites Mal
        gefragt.

 8      Die Zeile zur Werbe-Einwilligung bleibt erreichbar, auch mit
        Vollversion - Google verlangt den Weg zum Widerruf, solange eine
        Einwilligung gespeichert ist.

 9 + 13 Doppeltipp auf "Video ansehen" startet nicht mehr zwei Anzeigen.

11 + 16 Die Belohnung haengt jetzt am Ereignis, nicht am Rueckgabewert.
        Vorher ging ein verdientes Leben verloren, wenn die Frist zuerst
        griff - und beim Abbrechen wartete die App zwei Minuten auf eine
        Antwort, die nie kam.

12 + 17 Ein Fehlschlag ist nicht mehr stumm: Der Knopf zeigt "Video wird
        geladen", und kommt nichts, steht da ein Satz. Vorher sah ein
        nicht verfuegbares Video aus wie ein kaputter Knopf.

14      Ein spaet eintreffendes Video reisst keine laufende Lektion mehr
        ab.

15      Wer die Vollversion hat, wird nicht mehr nach einer Einwilligung
        fuer Werbung gefragt, die er nie sieht.

19      werbungAbgleichen() laeuft schon beim Start, nicht erst beim
        Oeffnen der Einstellungen. Sonst ging npa=1 hinaus, obwohl der
        Nutzer bei Google zugestimmt hatte.

NICHT hier drin: Befund 18 (Datenschutzerklaerung um die Diagnosedaten
ergaenzen) und Befund 20 (Kommentar in strings.xml). Beide stehen in
WERBUNG_PRUEFUNG.md und sind Textarbeit, keine Codeaenderung.

Probelauf:  python werbung_richten.py
Schreiben:  python werbung_richten.py --schreiben
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SCHREIBEN = "--schreiben" in sys.argv

ORDNER = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ORDNER, "web", "index.html")
SPR = os.path.join(ORDNER, "sprachen.py")

A = []


def t(datei, name, alt, neu):
    A.append((datei, name, alt, neu))


# =====================================================================
#  web/index.html
# =====================================================================

# ------------------------------------------------ 3 + 4: Einstufung, Testgeraete
t(WEB, "Einstufung und Testgeraete als Konstanten",
  """let AdMobP = null;          // das Plugin, sobald es sich gemeldet hat""",
  """/* Wie "erwachsen" eine Anzeige hoechstens sein darf. Ohne diese Angabe
   gilt allein die Voreinstellung im AdMob-Konto, und die laesst bis
   MatureAudience zu - in einer Lernapp mit Inhaltseinstufung USK 0 / PEGI 3
   waere das ein Widerspruch zu dem, was bei Google eingetragen ist.
   'General' passt zu USK 0. Wer mehr Anzeigen (und damit mehr Einnahmen)
   will, kann auf 'Teen' gehen - dann muss aber vorher die Inhaltseinstufung
   in der Play Console dazu passen, nicht umgekehrt. */
const ADMOB_EINSTUFUNG = 'General';

/* Die eigenen Handys. Solange ADMOB_TEST true ist, sieht jeder
   Testanzeigen; danach nicht mehr. Ohne diese Liste waere jeder eigene
   Tipp auf eine echte Anzeige ungueltiger Traffic - und der kostet im
   Zweifel das ganze Konto.
   Die Kennung steht beim ersten Start im Logcat: nach "Use
   RequestConfiguration.Builder().setTestDeviceIds" suchen. */
const ADMOB_TESTGERAETE = [];

let AdMobP = null;          // das Plugin, sobald es sich gemeldet hat""")

t(WEB, "initialize mit Einstufung und Testgeraeten",
  """    if(admobDarf) await A.initialize({initializeForTesting: ADMOB_TEST});""",
  """    if(admobDarf){
      await A.initialize({
        initializeForTesting: ADMOB_TEST || ADMOB_TESTGERAETE.length > 0,
        testingDevices: ADMOB_TESTGERAETE,
        maxAdContentRating: ADMOB_EINSTUFUNG,
      });
      admobGestartet = true;
    }""")

# ------------------------------------------------ 7 + 15: eigenes Fenster
t(WEB, "eigenes Einwilligungsfenster nur noch am PC",
  """function einwilligungFragen(){
  if(admobDa()) return false;      // dann fragt Googles eigenes Fenster
  return (WERBUNG_ECHT || EINWILLIGUNG_TEST) && !einwilligungGueltig();
}""",
  """function einwilligungFragen(){
  if(admobDa()) return false;      // dann fragt Googles eigenes Fenster
  /* Wer die Vollversion hat, sieht nie eine Anzeige. Ihn nach einer
     Einwilligung fuer eine Datenverarbeitung zu fragen, die bei ihm gar
     nicht stattfindet, waere unsinnig - und fuer jemanden, der genau
     dafuer bezahlt hat, aergerlich. Befund 15. */
  if(unlimited() || vollversionGemerkt()) return false;
  /* Auf dem Geraet gar nicht mehr. Dieses Fenster ist selbstgebaut und
     kein zertifiziertes CMP; Google verlangt im EWR seins. Kam UMP nicht
     durch, ist die richtige Antwort "keine Werbung", nicht "dann fragen
     wir eben selbst" - sonst wird derselbe Mensch beim naechsten Start
     von Google ein zweites Mal gefragt. Befund 7. */
  if(window.Capacitor && window.Capacitor.Plugins && WERBUNG_ECHT) return false;
  return (WERBUNG_ECHT || EINWILLIGUNG_TEST) && !einwilligungGueltig();
}""")

# ------------------------------------------------ 6: Widerruf wirkt sofort
t(WEB, "nach Googles Fenster den Stand neu einlesen",
  """    werbungLaeuft = true;
    try{ await AdMobP.showPrivacyOptionsForm(); }catch(e){}
    const g = await googlesAntwort();
    if(g !== null) setzePersonalisiert(g);   // genau das, was bei Google herauskam
    werbungLaeuft = false;""",
  """    werbungLaeuft = true;
    try{ await AdMobP.showPrivacyOptionsForm(); }catch(e){}
    /* Und danach neu nachfragen. Bisher blieb admobDarf auf dem Wert vom
       Start stehen: Wer hier widerrief, bekam bis zum Neustart weiter
       Anzeigen, und wer beim Start abgelehnt und es sich hier anders
       ueberlegt hatte, bekam bis zum Neustart gar keine - initialize()
       war nie gelaufen. Befund 6. */
    try{
      const neu = await AdMobP.requestConsentInfo();
      admobDarf = !!neu.canRequestAds;
      admobOptionen = neu.privacyOptionsRequirementStatus === 'REQUIRED';
      if(admobDarf && !admobGestartet){
        await AdMobP.initialize({
          initializeForTesting: ADMOB_TEST || ADMOB_TESTGERAETE.length > 0,
          testingDevices: ADMOB_TESTGERAETE,
          maxAdContentRating: ADMOB_EINSTUFUNG,
        });
        admobGestartet = true;
      }
    }catch(e){}
    const g = await googlesAntwort();
    if(g !== null) setzePersonalisiert(g);   // genau das, was bei Google herauskam
    werbungLaeuft = false;""")

t(WEB, "Merker, ob initialize schon lief",
  """let admobOptionen = false;  // Google verlangt einen Knopf zum Nachträglich-Ändern""",
  """let admobOptionen = false;  // Google verlangt einen Knopf zum Nachträglich-Ändern
let admobGestartet = false; // damit initialize() nicht zweimal laeuft""")

t(WEB, "admobStart setzt den Merker",
  """    admobDarf = !!info.canRequestAds;
    admobOptionen = info.privacyOptionsRequirementStatus === 'REQUIRED';""",
  """    admobDarf = !!info.canRequestAds;
    admobOptionen = info.privacyOptionsRequirementStatus === 'REQUIRED';
    admobGestartet = false;""")

# ------------------------------------------------ 8: Widerruf auch mit Vollversion
t(WEB, "Einwilligungszeile bleibt mit Vollversion erreichbar",
  """  const zeigen = !unlimited()
    && (WERBUNG_ECHT || EINWILLIGUNG_TEST || einwilligungGueltig() || admobDa());""",
  """  /* Normalerweise ist die Zeile mit Vollversion gegenstandslos - es laeuft
     ja keine Werbung. Aber wer vorher als Gratisnutzer bei Google
     zugestimmt hat, hat diese Einwilligung weiterhin liegen, und Google
     verlangt fuer den EWR einen dauerhaft erreichbaren Weg zum Widerruf.
     Deshalb: admobOptionen sticht die Vollversion. Befund 8. */
  const zeigen = (!unlimited()
    && (WERBUNG_ECHT || EINWILLIGUNG_TEST || einwilligungGueltig() || admobDa()))
    || (admobDa() && admobOptionen);""")

# ------------------------------------------------ 19: Abgleich schon beim Start
t(WEB, "Personalisierung gleich beim Start abgleichen",
  """  try{
    await admobStart();
    if(einwilligungFragen()) await zeigeEinwilligung();
  }catch(e){}""",
  """  try{
    await admobStart();
    /* Sofort abgleichen, nicht erst beim Oeffnen der Einstellungen. Sonst
       ging bei jeder Anzeige npa=1 hinaus, obwohl der Nutzer bei Google
       zugestimmt hatte - die Antwort lag im TCF-Speicher, aber niemand
       hatte sie gelesen. Befund 19. */
    await werbungAbgleichen();
    if(einwilligungFragen()) await zeigeEinwilligung();
  }catch(e){}""")

# ------------------------------------------------ 1, 11, 16, 17: admobZeigen
t(WEB, "admobZeigen neu: Nachpruefung, Ladefrist, Belohnung am Ereignis",
  """/* Zeigt eine Anzeige und kommt zurück, wenn sie wieder zu ist.
   true heißt: sie lief wirklich. */
async function admobZeigen(belohnt){
  if(!AdMobP || !admobDarf) return false;
  try{
    if(belohnt){
      await AdMobP.prepareRewardVideoAd({adId: ADMOB_ID.belohnt, isTesting: ADMOB_TEST,
                                         npa: !werbungPersonalisiert()});
      /* Gegenstueck zur Frist beim Interstitial. Antwortet das SDK nie -
         bei schlechtem Netz kommt das vor -, stuende der Nutzer sonst ewig
         vor der Ladeanzeige. Nach zwei Minuten geht es ohne Belohnung
         weiter, dieselbe Frist wie unten. */
      const lohn = await Promise.race([AdMobP.showRewardVideoAd(),
                                       new Promise(f => setTimeout(()=>f(null), 120000))]);
      return !!lohn;
    }
    await AdMobP.prepareInterstitial({adId: ADMOB_ID.interstitial, isTesting: ADMOB_TEST,
                                     npa: !werbungPersonalisiert()});
    const zu = admobWarten([['interstitialAdDismissed', true],
                            ['interstitialAdFailedToShow', false]], 120000);
    await AdMobP.showInterstitial();
    return await zu;
  }catch(e){ return false; }
}""",
  """/* So lange warten wir hoechstens darauf, dass eine Anzeige geladen ist.
   Vorher hatte nur das Zeigen eine Frist, das Laden nicht - bei schwachem
   Netz stand der Nutzer beliebig lange vor einem Knopf, der nichts tat.
   Fuenfzehn Sekunden fuer ein Leben sind das Aeusserste; zwei Minuten
   wartet niemand. Befund 17. */
const ADMOB_LADEFRIST = 15000;
const ADMOB_ZEIGEFRIST = 120000;

/* Zeigt eine Anzeige und kommt zurück, wenn sie wieder zu ist.
   true heißt: sie lief wirklich.

   `darfNoch` wird unmittelbar VOR dem Zeigen noch einmal gefragt. Das ist
   der Kern von Befund 1: Zwischen der Entscheidung "jetzt eine Anzeige"
   und dem tatsaechlichen Zeigen liegt ein Ladevorgang von unbekannter
   Dauer, und in dieser Zeit kann der Nutzer laengst weitergegangen sein
   oder die App weggelegt haben. Eine Anzeige ueber einer laufenden Aufgabe
   oder beim Zurueckkommen in die App ist bei Google eine unzulaessige
   Implementierung - die Kategorie, fuer die Konten gesperrt werden.
   Faellt die Pruefung negativ aus, wird die geladene Anzeige einfach
   verworfen. Sie kostet nichts; eine Sperre schon. */
async function admobZeigen(belohnt, darfNoch){
  if(!AdMobP || !admobDarf) return false;
  const nochErlaubt = () => (typeof darfNoch !== 'function') || !!darfNoch();
  try{
    if(belohnt){
      const geladen = await Promise.race([
        AdMobP.prepareRewardVideoAd({adId: ADMOB_ID.belohnt, isTesting: ADMOB_TEST,
                                     npa: !werbungPersonalisiert()}).then(()=>true, ()=>false),
        new Promise(f => setTimeout(()=>f(false), ADMOB_LADEFRIST))]);
      if(!geladen || !nochErlaubt()) return false;
      /* Die Belohnung haengt am Ereignis, nicht am Rueckgabewert.
         showRewardVideoAd() wird im Plugin NUR aufgeloest, wenn eine
         Belohnung faellt - bricht der Nutzer ab, kommt nie eine Antwort,
         und die App wartete zwei Minuten (Befund 16). Griff umgekehrt die
         Frist, waehrend das Video noch lief, fiel eine verdiente Belohnung
         unter den Tisch (Befund 11). Beides erledigt sich, wenn man auf
         die Ereignisse hoert: 'Reward' kommt vor 'Dismissed', wer also
         zu Ende sieht, bekommt sein Leben.
         ACHTUNG, Stolperstelle im Plugin: beim belohnten Video haben die
         Ereignisnamen ein 'on' davor, beim Interstitial nicht. */
      const ausgang = admobWarten([['onRewardedVideoAdReward', true],
                                   ['onRewardedVideoAdDismissed', false],
                                   ['onRewardedVideoAdFailedToShow', false]], ADMOB_ZEIGEFRIST);
      AdMobP.showRewardVideoAd().catch(()=>{});   // bewusst ohne await
      return await ausgang;
    }
    const geladen = await Promise.race([
      AdMobP.prepareInterstitial({adId: ADMOB_ID.interstitial, isTesting: ADMOB_TEST,
                                  npa: !werbungPersonalisiert()}).then(()=>true, ()=>false),
      new Promise(f => setTimeout(()=>f(false), ADMOB_LADEFRIST))]);
    if(!geladen || !nochErlaubt()) return false;
    const zu = admobWarten([['interstitialAdDismissed', true],
                            ['interstitialAdFailedToShow', false]], ADMOB_ZEIGEFRIST);
    await AdMobP.showInterstitial();
    return await zu;
  }catch(e){ return false; }
}""")

# ------------------------------------------------ 5, 9, 10, 13: zeigeWerbung
t(WEB, "zeigeWerbung: Sperre, Nachpruefung, kein Platzhalter auf dem Geraet",
  """function zeigeWerbung(belohnt, fertig){
  if(!werbungErlaubt()){ fertig(false); return; }
  stilleBitte();   // kein Wort unter der Anzeige - egal ob echte oder Platzhalter

  // Auf dem Handy die echte Anzeige. Gezählt wird erst, wenn sie auch lief –
  // eine Anzeige, die nicht kam, darf kein Tageskontingent verbrauchen.
  if(admobDa()){
    admobZeigen(belohnt).then(lief => { if(lief) werbungGezaehlt(); fertig(lief); });
    return;
  }
  werbungGezaehlt();""",
  """/* Eine Anzeige zur Zeit. Ohne diesen Riegel starteten zwei schnelle Tipps
   auf "Video ansehen" zwei Ladevorgaenge und zwei Anzeigen hintereinander -
   im Browser sogar zwei Leben fuer einen Tipp. Befunde 9 und 13. */
let werbungZeigtGerade = false;

function zeigeWerbung(belohnt, fertig, darfNoch){
  if(werbungZeigtGerade){ fertig(false); return; }
  if(!werbungErlaubt()){ fertig(false); return; }
  werbungZeigtGerade = true;
  const raus = angesehen => { werbungZeigtGerade = false; fertig(angesehen); };
  stilleBitte();   // kein Wort unter der Anzeige - egal ob echte oder Platzhalter

  // Auf dem Handy die echte Anzeige. Gezählt wird erst, wenn sie auch lief –
  // eine Anzeige, die nicht kam, darf kein Tageskontingent verbrauchen.
  if(admobDa()){
    /* Das .catch() ist kein Zierrat: bliebe der Riegel nach einem
       unerwarteten Fehler zu, kaeme fuer den Rest der Sitzung ueberhaupt
       keine Werbung mehr - und beim belohnten Video auch kein Leben. */
    admobZeigen(belohnt, darfNoch)
      .then(lief => { if(lief) werbungGezaehlt(); raus(lief); })
      .catch(()  => raus(false));
    return;
  }
  /* Der Kasten unten ist eine Attrappe fuer den PC: ein Rahmen mit dem Wort
     "Anzeige" und einem Countdown. Auf dem Geraet hat er nichts zu suchen.
     Er erschien dort trotzdem, sobald AdMob nicht hochkam - kein Netz,
     Einwilligung abgelehnt, Plugin-Fehler - und vergab sogar das Leben,
     ohne dass je ein Video lief. Befunde 5 und 10. */
  if(window.Capacitor && window.Capacitor.Plugins && WERBUNG_ECHT){ raus(false); return; }
  werbungGezaehlt();""")

t(WEB, "zeigeWerbung: Ausgaenge ueber den Riegel",
  """  const schliessen = (angesehen) => {
    clearInterval(uhr);
    kasten.remove();
    fertig(angesehen);
  };""",
  """  const schliessen = (angesehen) => {
    clearInterval(uhr);
    kasten.remove();
    raus(angesehen);
  };""")

# ------------------------------------------------ 12, 14, 17: werbungFuerLeben
t(WEB, "werbungFuerLeben: Knopf sperren, Rueckmeldung, kein Abriss",
  """/* Ein belohntes Video: freiwillig, gibt ein Leben zurück. */
function werbungFuerLeben(){
  zeigeWerbung(true, angesehen => {
    if(!angesehen) return;
    lives = {anzahl: Math.min(LEBEN_MAX, lives.anzahl + WERBUNG_LEBEN_LOHN),
             zeit: lives.zeit || Date.now()};
    saveProgress(); renderLives(); sound('ok');
    showLevelHome();
  });
}""",
  """/* Ein belohntes Video: freiwillig, gibt ein Leben zurück. */
function werbungFuerLeben(){
  /* Solange geladen wird, passiert auf dem Bildschirm nichts. Vorher sah
     das aus wie ein kaputter Knopf, und der zweite Tipp war die
     natuerliche Reaktion. Befunde 12 und 17. */
  const knopf = $('lAd');
  const vorher = knopf ? knopf.textContent : '';
  if(knopf){ knopf.disabled = true; knopf.textContent = t('werbung.laedt'); }
  const zurueck = () => {
    const k = $('lAd');
    if(k){ k.disabled = false; k.textContent = vorher || t('werbung.leben_holen'); }
  };
  zeigeWerbung(true, angesehen => {
    if(!angesehen){
      zurueck();
      /* Kein Fill, kein Netz, abgebrochen, Tageskontingent voll - fuer den
         Nutzer sah das alles gleich aus, naemlich nach nichts. Ein Satz
         reicht. Befund 12. */
      const note = $('lAdNote');
      if(note) note.textContent = t('werbung.keine');
      return;
    }
    lives = {anzahl: Math.min(LEBEN_MAX, lives.anzahl + WERBUNG_LEBEN_LOHN),
             zeit: lives.zeit || Date.now()};
    saveProgress(); renderLives(); sound('ok');
    /* Nur zurueck zum Lernpfad, wenn der Bildschirm ohne Leben ueberhaupt
       noch steht. Kam das Video spaet und der Nutzer hatte inzwischen mit
       Muenzen ein Herz gekauft und eine neue Lektion begonnen, riss
       showLevelHome() ihm diese Lektion weg - es leert lBody. Befund 14. */
    if($('lAd')) showLevelHome(); else zurueck();
  }, () => !document.hidden);
}""")

t(WEB, "Platz fuer die Rueckmeldung unter den beiden Knoepfen",
  """    ((perVideo || perMuenzen) ?
      '<div class="row schmal">'+
        (perVideo   ? '<button class="btn ghost" id="lAd">'+t('werbung.leben_holen')+'</button>' : '')+
        (perMuenzen ? '<button class="btn ghost" id="lCoin">'+t('lektion.leben_muenzen',{n:herz.preis})+'</button>' : '')+
      '</div>' : '')+""",
  """    ((perVideo || perMuenzen) ?
      '<div class="row schmal">'+
        (perVideo   ? '<button class="btn ghost" id="lAd">'+t('werbung.leben_holen')+'</button>' : '')+
        (perMuenzen ? '<button class="btn ghost" id="lCoin">'+t('lektion.leben_muenzen',{n:herz.preis})+'</button>' : '')+
      '</div>'+
      // bleibt leer, bis es etwas zu sagen gibt
      '<div class="feedback" id="lAdNote" style="color:var(--muted)"></div>' : '')+""")

# ------------------------------------------------ 2: der Wecker
t(WEB, "Merker fuer den Werbe-Wecker",
  """let werbungZaehler = 0;            // Lektionen seit der letzten Werbung""",
  """let werbungZaehler = 0;            // Lektionen seit der letzten Werbung
/* Der Wecker aus lessonEnd(). Er muss abraeumbar sein: wer die App in den
   1,2 Sekunden weglegt, bekaeme die Anzeige sonst beim Zurueckkommen
   praesentiert, ohne etwas getan zu haben. Befund 2. */
let werbeWecker = 0;""")

t(WEB, "Wecker abraeumen, wenn die App weggelegt wird",
  """  if(document.hidden){
    uhrWarAn = uhrStart > 0; uhrAus(); stilleBitte();""",
  """  if(document.hidden){
    uhrWarAn = uhrStart > 0; uhrAus(); stilleBitte();
    clearTimeout(werbeWecker); werbeWecker = 0;   // Befund 2""")

t(WEB, "Wecker merken und vor dem Zeigen noch einmal pruefen",
  """    const dieseLektion = Lx;
    setTimeout(()=>{
      // wegmarkeLaeuft: eine Anzeige über dem 100. Lerntag wäre die
      // schlechteste Minute, die sich die App aussuchen könnte. Die Lektion
      // fällt dann eben aus der Zählung - werbungZaehler steht schon höher,
      // die nächste bekommt sie.
      if(Lx === dieseLektion && !wegmarkeLaeuft
         && sichtbar('levelView') && sichtbar('lesson')) zeigeWerbung(false, ()=>{});
    }, 1200);""",
  """    const dieseLektion = Lx;
    /* Dieselbe Frage zweimal: einmal jetzt, und einmal - als darfNoch -
       unmittelbar bevor die geladene Anzeige tatsaechlich erscheint.
       Dazwischen liegt der Ladevorgang, und der dauert so lange, wie das
       Netz braucht. Befund 1. */
    const darfNoch = () => Lx === dieseLektion && !wegmarkeLaeuft
                        && !document.hidden
                        && sichtbar('levelView') && sichtbar('lesson');
    clearTimeout(werbeWecker);
    werbeWecker = setTimeout(()=>{
      werbeWecker = 0;
      // wegmarkeLaeuft: eine Anzeige über dem 100. Lerntag wäre die
      // schlechteste Minute, die sich die App aussuchen könnte. Die Lektion
      // fällt dann eben aus der Zählung - werbungZaehler steht schon höher,
      // die nächste bekommt sie.
      if(darfNoch()) zeigeWerbung(false, ()=>{}, darfNoch);
    }, 1200);""")

# =====================================================================
#  sprachen.py - zwei neue Texte in acht Sprachen
# =====================================================================
TEXTE = [
    ("♥ Leben abholen",       "Video wird geladen …",       "Gerade ist kein Video da. Versuch es später noch einmal."),
    ("♥ Collect heart",       "Loading video …",            "No video right now. Please try again later."),
    ("♥ Canı al",             "Video yükleniyor …",         "Şu anda video yok. Lütfen daha sonra tekrar dene."),
    ("♥ Hämta hjärta",        "Videon laddas …",            "Ingen video just nu. Försök igen senare."),
    ("♥ Leven ophalen",       "Video wordt geladen …",      "Nu even geen video. Probeer het later nog eens."),
    ("♥ Hent liv",            "Videoen lastes …",           "Ingen video akkurat nå. Prøv igjen senere."),
    ("♥ Hent liv",            "Videoen indlæses …",         "Ingen video lige nu. Prøv igen senere."),
    ("♥ Récupérer la vie",    "Chargement de la vidéo …",   "Pas de vidéo pour le moment. Réessaie plus tard."),
]
# Norwegisch und Daenisch haben denselben Abholtext - deshalb wird unten
# nicht ueber den Text gesucht, sondern der Reihe nach vorgegangen.


def sprachen_ergaenzen(text):
    """Haengt die zwei neuen Schluessel in jedem der acht Bloecke an."""
    marke = '"werbung.lohn_abholen": '
    stellen = []
    i = 0
    while True:
        i = text.find(marke, i)
        if i < 0:
            break
        stellen.append(i)
        i += len(marke)
    if len(stellen) != 8:
        return None, "werbung.lohn_abholen steht %d mal da, erwartet 8" % len(stellen)
    # von hinten nach vorn, damit die Fundstellen nicht verrutschen
    for nr in range(7, -1, -1):
        i = stellen[nr]
        ende = text.find("\n", i)
        if ende < 0:
            return None, "Block %d hat kein Zeilenende" % nr
        abhol, laedt, keine = TEXTE[nr]
        if abhol not in text[i:ende]:
            return None, "Block %d passt nicht: erwartet %r in %r" % (nr, abhol, text[i:ende])
        neu = ('\n"werbung.laedt": "%s",'
               '\n"werbung.keine": "%s",') % (laedt, keine)
        text = text[:ende] + neu + text[ende:]
    return text, None


# ---------------------------------------------------------------- anwenden
stand = {}
for datei, name, alt, neu in A:
    if datei not in stand:
        roh = io.open(datei, encoding="utf-8", newline="").read()
        stand[datei] = [roh.replace("\r\n", "\n"), "\r\n" in roh]
    n = stand[datei][0].count(alt)
    if n != 1:
        print("ABBRUCH: %-12s %-52s %d Treffer" % (os.path.basename(datei), name, n))
        if n == 0:
            print("         Ist der Patch vielleicht schon drin?")
        sys.exit(1)
    stand[datei][0] = stand[datei][0].replace(alt, neu, 1)
    print("ok   %-12s %s" % (os.path.basename(datei), name))

roh = io.open(SPR, encoding="utf-8", newline="").read()
spr_crlf = "\r\n" in roh
spr, fehlt = sprachen_ergaenzen(roh.replace("\r\n", "\n"))
if fehlt:
    print("ABBRUCH: sprachen.py - %s" % fehlt)
    sys.exit(1)
print("ok   %-12s zwei neue Texte in acht Sprachen" % "sprachen.py")

# ------------------------------------------------------------ Nachkontrolle
fehler = []
w = stand[WEB][0]

for muss, wie_oft, warum in (
        ("const ADMOB_EINSTUFUNG", 1, "die Einstufung fehlt"),
        ("const ADMOB_TESTGERAETE", 1, "die Testgeraete fehlen"),
        ("maxAdContentRating: ADMOB_EINSTUFUNG", 2, "die Einstufung wird nicht uebergeben"),
        ("let admobGestartet = false;", 1, "der Startmerker fehlt"),
        ("let werbungZeigtGerade = false;", 1, "der Riegel fehlt"),
        ("let werbeWecker = 0;", 1, "der Weckermerker fehlt"),
        ("clearTimeout(werbeWecker)", 2, "der Wecker wird nicht abgeraeumt"),
        ("onRewardedVideoAdReward", 1, "das Belohnungs-Ereignis fehlt"),
        ("const ADMOB_LADEFRIST", 1, "die Ladefrist fehlt"),
        ("async function admobZeigen(belohnt, darfNoch)", 1, "admobZeigen nimmt darfNoch nicht"),
        ("function zeigeWerbung(belohnt, fertig, darfNoch)", 1, "zeigeWerbung nimmt darfNoch nicht"),
        ("id=\"lAdNote\"", 1, "der Platz fuer die Rueckmeldung fehlt"),
        ("t('werbung.laedt')", 1, "der Ladetext wird nicht benutzt"),
        ("t('werbung.keine')", 1, "der Fehltext wird nicht benutzt"),
):
    if w.count(muss) != wie_oft:
        fehler.append("%s (%r steht %d mal da, erwartet %d)" % (warum, muss, w.count(muss), wie_oft))

# Der alte Weg darf nirgends mehr stehen
for darf_nicht, warum in (
        ("await AdMobP.showRewardVideoAd()", "das Video wird noch mit await gezeigt - haengt beim Abbruch"),
        ("fertig(angesehen);\n  };", "ein Ausgang laeuft am Riegel vorbei"),
        ("admobZeigen(belohnt).then", "admobZeigen wird noch ohne Nachpruefung gerufen"),
):
    if darf_nicht in w:
        fehler.append(warum)

# Der Riegel darf unter keinen Umstaenden haengen bleiben
if ".catch(()  => raus(false));" not in w:
    fehler.append("admobZeigen wird ohne .catch gerufen - der Riegel koennte haengen bleiben")

for darf_nicht, warum in (
        ("admobZeigen(belohnt, darfNoch).then(lief => { if(lief) werbungGezaehlt(); raus(lief); });\n    return;",
         "der Aufruf hat kein .catch"),
):
    if darf_nicht in w:
        fehler.append(warum)

# Jeder Ausgang von zeigeWerbung muss den Riegel loesen
i0 = w.find("function zeigeWerbung(belohnt, fertig, darfNoch)")
i1 = w.find("/* Ein belohntes Video", i0)
block = w[i0:i1]
# Genau vier: AdMob-Zweig, sein .catch, der Geraete-Abbruch und schliessen().
# Die zwei fertig(false) davor sind Absicht - sie liegen VOR dem Riegel.
if block.count("raus(") != 4:
    fehler.append("zeigeWerbung hat %d Ausgaenge ueber raus(), erwartet 4" % block.count("raus("))
if "const raus = angesehen" not in block:
    fehler.append("die Definition von raus() fehlt")
if "fertig(" in block.replace("fertig(false); return; }", "").replace("const raus = angesehen => { werbungZeigtGerade = false; fertig(angesehen); };", ""):
    fehler.append("in zeigeWerbung wird fertig() noch direkt gerufen")

# sprachen.py
for laedt, keine in ((x[1], x[2]) for x in TEXTE):
    if spr.count('"werbung.laedt": "%s",' % laedt) < 1:
        fehler.append("sprachen.py: %r fehlt" % laedt)
    if spr.count('"werbung.keine": "%s",' % keine) < 1:
        fehler.append("sprachen.py: %r fehlt" % keine)
if spr.count('"werbung.laedt"') != 8:
    fehler.append("werbung.laedt steht %d mal da, erwartet 8" % spr.count('"werbung.laedt"'))
if spr.count('"werbung.keine"') != 8:
    fehler.append("werbung.keine steht %d mal da, erwartet 8" % spr.count('"werbung.keine"'))

if fehler:
    print("\nABBRUCH - nichts geschrieben:")
    for f in fehler:
        print("   " + f)
    sys.exit(1)
print("\n   Nachkontrollen bestanden.")

if SCHREIBEN:
    for datei, (text, crlf) in stand.items():
        io.open(datei, "w", encoding="utf-8", newline="").write(
            text.replace("\n", "\r\n") if crlf else text)
        print("geschrieben: %s" % os.path.basename(datei))
    io.open(SPR, "w", encoding="utf-8", newline="").write(
        spr.replace("\n", "\r\n") if spr_crlf else spr)
    print("geschrieben: sprachen.py")
    print("\nJETZT NOCH: app_bauen.py laufen lassen.")
else:
    print("(Probelauf. Zum Schreiben: python werbung_richten.py --schreiben)")
