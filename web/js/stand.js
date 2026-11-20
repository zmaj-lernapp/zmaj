/* ---- Fortschritt: mit dem Python-Server abgleichen ---- */
/* Eine Zahl wie Muenzen oder Rekord: endlich, nicht negativ, ganz - sonst
   0 (17.10.2026). */
const ganzAbNull = x => { const n = Number(x); return (isFinite(n) && n > 0) ? Math.floor(n) : 0; };
/* ---- Was nur fuer eine Sicherungsdatei gilt (17.10.2026) ----
   Sie kommt von aussen und kann von Hand geschrieben sein, der eigene
   Geraetespeicher nicht. Deshalb hier und nicht in standUebernehmen().
   Gibt eine Kopie zurueck; was hier nicht steht, geht unveraendert weiter,
   und Unplausibles faellt still heraus - der Rest der Sicherung kommt
   vollstaendig an.
     tage, frost  nur Tage von APP_START bis heute (tagMoeglich). Aeltere
                  schoben zmaj_seit und damit das Jahresgeschenk beliebig
                  weit zurueck, Tage in der Zukunft zaehlten bei "Tage
                  gelernt" und den Wegmarken mit.
     rekord       hoechstens so lang, wie es Lerntage gibt: streak() und
                  laengsteSerie() zaehlen nur Tage aus days.
     Muenzen      hoechstens, was sich mit diesen Lerntagen verdienen
                  laesst. Die Rechnung: Muenzen gibt es an genau einer
                  Stelle, in zaehle() - MUENZEN_PRO_QUEST (10) je geschaffter
                  Tagesaufgabe, und zieh() waehlt drei am Tag. Das sind
                  hoechstens 30 am Tag. Wegmarken, Jahresgeschenk,
                  Werbevideos (die geben Leben) und der Laden geben keine,
                  ein Startguthaben gibt es nicht: muenzenGes beginnt bei 0.
                  Grenze grosszuegig das Doppelte, 60 je Lerntag - das deckt
                  auch einen Tag, an dem die Auswahl wechselt (q.geht()) -,
                  und ein Tag mehr: Muenzen fallen schon mitten in der
                  Lektion (zaehle('auf')), den Lerntag gibt es erst an ihrem
                  Ende (markToday). 100 Lerntage -> hoechstens 6060 Muenzen.
                  Ausgegeben nie mehr als verdient.
     besitz       (Gegenpruefung 17.10.2026) nur Zierrat, den es im Laden
                  fuer Muenzen gibt, und nur so viel, wie die verdienten
                  Muenzen hergeben - das Billigste zuerst. Vorher kam per
                  Datei der ganze Laden an, 20 Stuecke fuer zusammen 23 800
                  Muenzen bei 0 Muenzen, und die Grenze darueber war fuer
                  den Zierrat wirkungslos. Stuecke der Vollversion kauft
                  niemand (sie haengen an unlimited()), unbekannte
                  Kennungen gibt es nicht - beide fallen heraus. Was
                  bleibt, ist bezahlt: ausgegeben mindestens die Preise
                  davon. Ein echter Stand hat Preise <= ausgegeben <=
                  verdient - kaufe() bucht jeden Kauf in muenzenAus - und
                  verliert nichts, auch nicht die Reihenfolge. */
const MUENZEN_JE_TAG_HOECHSTENS = 2 * 3 * MUENZEN_PRO_QUEST;
function sicherungPlausibel(s){
  const p = Object.assign({}, s);
  p.tage = Array.isArray(s.tage) ? s.tage.filter(tagMoeglich) : [];
  p.frost = Array.isArray(s.frost) ? s.frost.filter(tagMoeglich) : [];
  const lerntage = new Set(p.tage).size;
  p.rekord = Math.min(ganzAbNull(s.rekord), lerntage);
  p.muenzen_ges = Math.min(ganzAbNull(s.muenzen_ges), MUENZEN_JE_TAG_HOECHSTENS * (lerntage + 1));
  const preis = id => { const w = ZIERRAT.find(x => x.id === id && !x.voll); return w ? w.preis : 0; };
  const liste = [...new Set((Array.isArray(s.besitz) ? s.besitz : [])
    .filter(id => typeof id === 'string' && preis(id) > 0))];
  const behalten = new Set();
  let summe = 0;
  for(const id of [...liste].sort((a, b) => preis(a) - preis(b))){
    if(summe + preis(id) > p.muenzen_ges) break;
    summe += preis(id); behalten.add(id);
  }
  p.besitz = liste.filter(id => behalten.has(id));
  p.muenzen_aus = Math.max(Math.min(ganzAbNull(s.muenzen_aus), p.muenzen_ges), summe);
  /* Sterne (19.10.2026): nur gueltige Kennungen und Zahlen, hoechstens
     STERN_MAX, und kein Zeitpunkt nach jetzt - siehe sternPruefen(). */
  p.stern = sternPruefen(s.stern);
  /* Lernkartei (29.10.2026): kein Uebungstag nach heute, kein Termin
     weiter weg als die laengste Stufe - siehe karteiPruefen(). */
  p.kartei = karteiPruefen(s.kartei, true);
  return p;
}
/* ---- Felder einer neueren Fassung (28.10.2026, Vorarbeit fuer v110) ----
   Mit v110 kommt die zeitgesteuerte Wiederholung, und mit ihr kommen neue
   Felder in den Lernstand. Eine Fassung, die sie nicht kennt - diese
   hier -, darf sie nicht wegwerfen: Bis dahin fiel alles weg, was
   standAlsObjekt() nicht nennt. Ein Handy mit v109 haette so beim
   naechsten Abgleich die Wiederholungsdaten geloescht, die ein Tablet mit
   v110 in die Cloud geschrieben hat, und eine Sicherungsdatei von v110
   verloere sie beim Einlesen.
   Jetzt legt standUebernehmen() solche Felder unveraendert in standFremd
   ab, standAlsObjekt() schreibt sie wieder mit - in den Geraetespeicher,
   die Sicherungsdatei und die Cloud -, und standZusammenfuehren()
   behaelt sie (siehe dort).
     STAND_FELDER  was diese Fassung selbst liest und schreibt, genau die
                   Schluessel von standAlsObjekt() (tests_e2e/test_cloud.py
                   vergleicht beides)
     STAND_ALT     was frueher im Stand stand und mit Absicht wegfaellt:
                   premium gehoert nicht mehr hinein (siehe
                   vollversionLaden) und wandert auch nicht als fremdes
                   Feld mit
   Was die App nicht kennt, prueft sie nicht - sie traegt es nur. Damit
   eine Datei damit nicht den Geraetespeicher sprengt, gilt fuer alle
   fremden Felder zusammen die Grenze der Cloud (CLOUD_GROESSE_MAX, in
   UTF-8-Bytes). Was darueber hinausgeht, faellt Feld fuer Feld weg, nie
   alle auf einmal (Pruefbefund 28.10.2026: vorher fielen bei Ueberlauf
   alle weg, auch die aktuellen aus der Cloud, und der naechste Abgleich
   loeschte sie dort). "__proto__" wird nie ein Feld.
   Fuer v110 und jede spaetere Fassung heisst das (Pruefbefund
   28.10.2026): eigene Daten - etwa die der zeitgesteuerten Wiederholung -
   gehoeren ausschliesslich in eigene, neue Felder auf oberster Ebene des
   Stands, nie in topf, stern oder ein anderes Feld aus STAND_FELDER.
   Die behandelt diese Fassung nach ihren eigenen Regeln und verliert
   dabei, was sie nicht kennt: topfMerken() schreibt einen Eintrag bei
   jedem Fehler neu und loescht ihn nach TOPF_RAUS richtigen Antworten,
   topfAufraeumen() wirft Schluessel weg, die zu keiner Aufgabe fuehren,
   sternPruefen() behaelt nur z und r.
   v110 (29.10.2026) hat sich daran gehalten: die Lernkartei steht im
   eigenen Feld kartei und gehoert damit ab hier zu STAND_FELDER. Fuer
   kartei gilt dasselbe: karteiPruefen() behaelt je Wort genau drei
   Zahlen - was eine spaetere Fassung (etwa FSRS) braucht, kommt in ein
   weiteres neues Feld, nicht an die Eintraege dort. */
const STAND_FELDER = new Set(['gewusst', 'bestanden', 'gelesen', 'tage', 'frost', 'besitz', 'leben',
  'schutz', 'tagwerk', 'muenzen_ges', 'muenzen_aus', 'getragen', 'gefeiert', 'rekord', 'wann',
  'geschenk_jahr', 'einstufung', 'topf', 'bewertung', 'stern', 'kartei', 'zahnarzt']);
const STAND_ALT = new Set(['premium']);
let standFremd = {};
/* Die fremden Felder eines Stands als tiefe Kopie - sie teilen nichts mit
   dem Stand, aus dem sie kommen. Hoechstens platz Bytes fuer alle
   zusammen, gezaehlt mit fremdGroesse(): Feld fuer Feld in der
   Reihenfolge des Stands, und passt eins nicht mehr, faellt nur dieses
   weg. Ein Feld, das sich nicht als JSON schreiben laesst, ebenso. */
const fremdGroesse = (k, text) => utf8Laenge(JSON.stringify(k)) + utf8Laenge(text) + 2;
function standFremdAus(d, platz = CLOUD_GROESSE_MAX){
  if(!d || typeof d !== 'object' || Array.isArray(d)) return {};
  const aus = [];
  let summe = 0;
  Object.keys(d).forEach(k => {
    if(STAND_FELDER.has(k) || STAND_ALT.has(k) || k === '__proto__' || d[k] === undefined) return;
    let text;
    try{ text = JSON.stringify(d[k]); }catch(e){ return; }
    if(typeof text !== 'string') return;
    const g = fremdGroesse(k, text);
    if(summe + g > platz) return;
    summe += g;
    aus.push([k, JSON.parse(text)]);
  });
  return Object.fromEntries(aus);
}
/* So viele Bytes bringen fremde Felder zu einem Stand ohne sie hoechstens
   mit (Schluessel, Doppelpunkt, Wert, Komma), gezaehlt wie in
   standFremdAus(). */
function fremdPlatz(f){
  return Object.keys(f).reduce((s, k) => s + fremdGroesse(k, JSON.stringify(f[k])), 0);
}
/* Ein Stand sieht ueberall gleich aus - egal ob er aus der Profildatei des
   Servers kommt, aus dem Gerätespeicher oder aus einer Sicherungsdatei.
   Deshalb nur eine Stelle, die ihn uebernimmt. */
function standUebernehmen(d){
  d = d || {};
  /* Was diese Fassung nicht kennt, bleibt unveraendert (28.10.2026, siehe
     standFremd). Vor allem anderen: wirft unten etwas, nimmt
     standErsetzen() mit dem alten Stand auch dessen fremde Felder zurueck. */
  standFremd = standFremdAus(d);
  /* Eine Sicherung kann jeder von Hand schreiben. Eine Zahl in gewusst
     liess altenFortschrittUmschreiben() bei jedem Start werfen, bevor der
     Einstellungsknopf erschien - siehe import_richten.py, 04.10.2026. */
  const nurTexte = x => Array.isArray(x) ? x.filter(s => typeof s === 'string') : [];
  known = new Set(nurTexte(d.gewusst)); passed = new Set(nurTexte(d.bestanden)); read = new Set(nurTexte(d.gelesen));
  gewusstGeladen = known.size > 0;
  // Nur echte Datumsangaben - siehe istDatum.
  // Kein Array (etwa "tage":"x") hiess bisher: .filter wirft. Jetzt: leer.
  /* Und keine vor APP_START (17.10.2026): die kann es nicht geben, ein
     solcher Tag stammt aus einer gefaelschten Sicherung von vor dieser
     Pruefung. Die obere Grenze "nicht nach heute" gilt hier bewusst NICHT,
     nur beim Einlesen (sicherungPlausibel): springt die Uhr des Handys
     zurueck, etwa nach leerem Akku, verloere sonst schon der naechste
     Start alle Lerntage - und speicherte das gleich so. */
  const abStart = s => istDatum(s) && s >= APP_START;
  days = new Set((Array.isArray(d.tage) ? d.tage : []).filter(abStart));
  frost = new Set((Array.isArray(d.frost) ? d.frost : []).filter(abStart));
  /* Unterschied zwischen "Feld fehlt" und "Feld ist leer":
       fehlt  = der Stand kommt von VOR den Wegmarken, etwa aus einer alten
                Sicherungsdatei. Dann wird weiter unten alles schon
                Erreichte stillschweigend abgehakt - eine alte Datei
                einzulesen ist kein Grund zu feiern.
       leer   = neuer Stand, es wurde wirklich noch nichts gefeiert.
     Die Dateien in testdaten/ haben 30 Lerntage und kein Feld; ohne diese
     Unterscheidung feierte die App nach jedem Einlesen von vorn. */
  const gefeiertFehlt = (d.gefeiert === undefined);
  gefeiert = new Set(nurTexte(d.gefeiert));
  wann = (d.wann && typeof d.wann==='object' && !Array.isArray(d.wann)) ? d.wann : {};
  /* Nie laenger als es Lerntage gibt (Gegenpruefung 17.10.2026): streak()
     und laengsteSerie() zaehlen nur Tage aus days, ein Frosttag ueberbrueckt
     nur. Ein Rekord von 1e9 aus einer gefaelschten Sicherung von vor der
     Pruefung blieb sonst im Geraetespeicher stehen. Anders als die
     Lerntage selbst sicher gegen eine zurueckspringende Uhr - days.size
     haengt nicht am heutigen Datum. Ein echter Stand verliert nichts. */
  rekord = Math.min(ganzAbNull(d.rekord), days.size);
  /* Steht noch kein Rekord da, wird er aus den vorhandenen Lerntagen
     nachgerechnet. Sonst finge eine Testerin bei null an, obwohl sie die Tage
     längst hinter sich hat. Passiert genau einmal je Lernstand. */
  const gerechnet = laengsteSerie();
  if(gerechnet > rekord) rekord = gerechnet;
  /* Siehe oben: alter Stand ohne das Feld. Was schon erreicht ist, gilt als
     gefeiert - sonst kommt beim nächsten Lerntag eine Karte für etwas, das
     Wochen zurückliegt. */
  if(gefeiertFehlt && days.size){
    MEILENSTEINE.forEach(m => { if(days.size >= m.ziel) gefeiert.add(m.id); });
  }
  tagwerk = (d.tagwerk && typeof d.tagwerk==='object') ? d.tagwerk : {};
  /* Endlich und nicht negativ (17.10.2026). "1e999" liest JSON.parse als
     Infinity, und Number(...) || 0 liess das durch - unendlich viele
     Muenzen, Leben und Zierrat umsonst. Die Obergrenze fuer eine
     Sicherungsdatei steht in sicherungPlausibel(). */
  /* Beim normalen Start bewusst KEINE Obergrenze fuer Muenzen und Zierrat
     (Gegenpruefung 17.10.2026). Ein ueberhoehter Stand im Geraetespeicher
     kann nur von einer Datei stammen, die vor der Pruefung eingelesen
     wurde - also von einem Geraet aus dem geschlossenen Test. Dort liegt
     er auch wirklich, und mit Absicht: Ajdins Handy hatte am 27.09.2026
     1 000 029 Muenzen aus testdaten/ und den ganzen Laden, eine
     Handysicherung vom 07.10. 1110 Muenzen bei 7 Lerntagen (Grenze 480).
     Kuerzen hiesse, beim Update still und unwiderruflich zu nehmen; das
     Geld kauft nur Zierrat, Herzen und Serienschutz. Dazu kommen Muenzen
     auch an Tagen ohne Lerntag (abgebrochene Lektion, nicht bestandener
     Test - in jener Sicherung 2 von 9 Tagen), die Grenze ist also eine
     Schaetzung und keine Rechnung. Lerntage nach heute bleiben aus dem
     Grund, der oben bei abStart() steht. */
  muenzenGes = ganzAbNull(d.muenzen_ges); muenzenAus = ganzAbNull(d.muenzen_aus);
  besitz = new Set(nurTexte(d.besitz));
  /* Fehlt das Feld, ist es ein Stand von vorher: nie eingestuft, nichts
     im Topf. Ob gefragt wird, entscheidet einstufungFaellig() - wer schon
     Fortschritt hat, wird es nie. */
  einstufung = (d.einstufung && typeof d.einstufung==='object' && !Array.isArray(d.einstufung)) ? d.einstufung : null;
  /* Nur Eintraege, die Objekte sind: topfAufgabe() liest e.typ. Object.fromEntries
     legt auch "__proto__" als gewoehnlichen Schluessel an, nichts aendert den Prototyp. */
  topf = (d.topf && typeof d.topf==='object' && !Array.isArray(d.topf))
    ? Object.fromEntries(Object.entries(d.topf).filter(([, e]) => e && typeof e==='object' && !Array.isArray(e)))
    : {};
  /* Fehlt das Feld (Stand oder Sicherung von vor dem 19.10.2026), ist
     nichts markiert. Kaputte Eintraege fallen hier still heraus. */
  stern = sternPruefen(d.stern);
  /* Die Lernkartei (29.10.2026). Fehlt das Feld - ein Stand von vor
     v110 -, ist sie leer; die gewussten Woerter bekommen ihre Termine
     gleich danach in karteiNachtragen() (altenFortschrittUmschreiben). */
  kartei = karteiPruefen(d.kartei);
  /* Beim Zahnarzt: fehlt das Feld (Stand von vor dem 06.11.2026), ist er aus. */
  zaSchalter = zaSchalterPruefen(d.zahnarzt);
  const bw = (d.bewertung && typeof d.bewertung==='object' && !Array.isArray(d.bewertung)) ? d.bewertung : {};
  bewertung = {gezeigt: Array.isArray(bw.gezeigt) ? bw.gezeigt.filter(istDatum) : [],
               nein: !!bw.nein, bewertet: !!bw.bewertet};
  /* Endliche Zahl zwischen 0 und dem Hoechstwert. Im Spiel kommt nie mehr
     zustande - jede Stelle, die erhoeht, nimmt Math.min. 1e300 Herzen aus
     einer Datei waeren die Vollversion umsonst, ein Text als zeit liess nie
     wieder eins nachwachsen. */
  const anzahlBis = (x, max) => (typeof x==='number' && isFinite(x)) ? Math.max(0, Math.min(max, Math.floor(x))) : null;
  const zeitpunkt = x => (typeof x==='number' && isFinite(x)) ? x : 0;
  const la = (d.leben && typeof d.leben==='object') ? anzahlBis(d.leben.anzahl, LEBEN_MAX) : null;
  lives = la !== null ? {anzahl:la, zeit:zeitpunkt(d.leben.zeit)} : {anzahl:LEBEN_MAX, zeit:0};
  const sa = (d.schutz && typeof d.schutz==='object') ? anzahlBis(d.schutz.anzahl, SCHUTZ_MAX) : null;
  schutz = sa !== null ? {anzahl:sa, zeit:zeitpunkt(d.schutz.zeit)} : {anzahl:1, zeit:0};
  /* premium steht hier bewusst NICHT mehr. Der Lernstand kommt auch aus
     einer Sicherungsdatei, die jeder von Hand aufmachen kann - siehe
     vollversionLaden() weiter unten. */
  /* Das getragene Stueck lebt sonst nur im Geraetespeicher. Wer auf ein
     neues Handy umzieht, haette den Zierrat zwar gekauft, der Drache truege
     aber nichts. Nur uebernehmen, wenn es wirklich dabei ist: vom Server
     kommt der Schluessel nie, und dann soll er das Getragene nicht loeschen. */
  if(typeof d.getragen === 'string'){
    getragen = d.getragen;
    try{ localStorage.setItem('zmaj_getragen', getragen); }catch(e){}
  }
  /* Siehe standAlsObjekt: nur nach oben. Eine aeltere Sicherung darf ein
     schon gegebenes Geschenk nicht wieder aufmachen. */
  /* Und nie ueber das hinaus, was seit APP_START moeglich ist (17.10.2026) -
     siehe geschenkJahreMax(). */
  const jahrAusStand = Math.min(Number(d.geschenk_jahr) || 0, geschenkJahreMax());
  if(jahrAusStand > (geschenk.jahr || 0)){
    geschenk = {jahr: jahrAusStand, bis: geschenk.bis || 0};
    try{ localStorage.setItem(GESCHENK_SCHLUESSEL, JSON.stringify(geschenk)); }catch(e){}
  }
}
/* Einmaliger Umzug. Bis Fassung 52 funkelte jeder mit Vollversion von
   selbst - das Funkeln stand in keiner Trageliste, getrageneTeile() legte
   es jedem dazu. Seit es eine Ware ist, muss es in getragen stehen, sonst
   waere es nach dem Update ohne ein Wort verschwunden.
   Laeuft genau einmal, und nur bei dem, der die Vollversion zuletzt hatte.
   Wichtig ist die Stelle: erst NACH loadProgress(). Stand er frueher,
   beim Einlesen von zmaj_getragen, schrieb standUebernehmen() ihn gleich
   darauf wieder zu - in der Browser-Probe am 30.09.2026 aufgefallen. */
function funkelnUmzug(){
  try{
    if(localStorage.getItem('zmaj_funkeln_umzug')) return false;
    localStorage.setItem('zmaj_funkeln_umzug', '1');
  }catch(e){ return false; }
  if(!(vollversionGemerkt() || dauerVoll)) return false;
  if(getragenRoh().indexOf('funkeln') >= 0) return false;
  setzeGetragen(getragenRoh().concat(['funkeln']));
  return true;
}
function standAlsObjekt(){
  const s = {gewusst:[...known], bestanden:[...passed], gelesen:[...read], tage:[...days],
          frost:[...frost], besitz:[...besitz], leben:lives, schutz:schutz, tagwerk:tagwerk,
          muenzen_ges:muenzenGes, muenzen_aus:muenzenAus,
          getragen:getragen,
          /* Muss in BEIDE Richtungen stehen - hier und in standUebernehmen.
             Steht es nur hier, fällt es beim Handywechsel durch dasselbe
             Loch, das "getragen" schon einmal hatte. */
          gefeiert:[...gefeiert], rekord:rekord, wann:wann,
          /* Nur das Jahr des letzten Geschenks, nie die laufende Frist.
             Das Jahr sagt "dieses Geschenk wurde schon gegeben" und gehoert
             damit zum Lernenden, nicht zum Geraet: lag es nur im
             Geraetespeicher, holte man sich die fuenf Tage beliebig oft -
             App-Daten loeschen, Sicherung einlesen, wieder faellig. Die
             Frist bleibt draussen, sonst waeren laufende Geschenktage
             verschenkbar. Gefunden in der Gegenpruefung am 29.09.2026.
             Das hilft nur bei einer ehrlichen Datei von nach dem
             Geschenk. Eine von davor, oder eine mit 0 von Hand, holt es
             nach "App-Daten loeschen" wieder - alle fuenf Tage einmal
             loeschen und einlesen (Gegenpruefung 17.10.2026). Bewusst
             hingenommen: dagegen hilft nur ein Merker, der das Loeschen
             der App-Daten uebersteht, und den gibt es ohne Server nicht. */
          geschenk_jahr: (geschenk.jahr || 0),
          /* Beide gehoeren zum Lernenden und muessen mit auf ein neues
             Handy - die Einstufung haelt die uebersprungenen Level offen. */
          einstufung: einstufung, topf: topf, bewertung: bewertung,
          /* Die Sterne gehoeren wie der Topf zum Lernenden (19.10.2026). Die
             Sicherungsdatei bleibt version 1: eine alte App liest das Feld
             nicht, eine neue nimmt ein fehlendes als "nichts markiert". */
          stern: stern,
          /* Die Lernkartei (v110, 29.10.2026), siehe LERNKARTEI. Auch sie
             laesst die Sicherungsdatei bei version 1: eine alte App traegt
             das Feld nur weiter (standFremd), eine neue nimmt ein fehlendes
             als leer und traegt die Termine nach. */
          /* Beim Zahnarzt (06.11.2026): nur der Schalter, der Lernstand steht
             in gewusst und bestanden. */
          zahnarzt: zaSchalter,
          kartei: kartei};
  /* Dahinter, unveraendert, was eine neuere Fassung in den Stand gelegt
     hat (28.10.2026, siehe standFremd). Eigene Felder gehen vor -
     standFremdAus() laesst ohnehin keins davon durch. */
  Object.keys(standFremd).forEach(k => {
    if(!Object.prototype.hasOwnProperty.call(s, k)) s[k] = standFremd[k];
  });
  return s;
}
/* ---- Zwei Lernstaende zusammenfuehren (19.10.2026) ----
   Fuer die Cloud-Sicherung (siehe CLOUD-SICHERUNG weiter unten): a ist der
   Stand dieses Geraets, b der aus der Cloud - von einem zweiten Geraet oder
   einer frueheren Installation. Zusammenfuehren statt ueberschreiben: das
   alte start.py ersetzte die Listen, und das zweite Geraet loeschte, was
   das erste gelernt hatte.
   Rein: liest a und b, aendert weder sie noch die App und gibt einen neuen
   Stand im Format von standAlsObjekt() zurueck. Idempotent (m mit m ergibt
   m) und kommutativ (a mit b gleich b mit a) - bis auf "getragen" und die
   Felder einer neueren Fassung, siehe dort. Listen kommen sortiert
   heraus, damit beide Richtungen dasselbe ergeben; in der App sind es
   ohnehin Mengen.
   Jedes Feld aus standAlsObjekt() ist hier bewusst behandelt (der Test
   tests_e2e/test_cloud.py vergleicht die Schluessel):
     gewusst, bestanden,   Vereinigung. Gelernt ist gelernt, egal auf
     gelesen               welchem Geraet.
     tage, frost           Vereinigung. Ein Lerntag auf dem Tablet zaehlt
                           fuer die Serie wie einer auf dem Handy.
     gefeiert              Vereinigung. Was ein Geraet gefeiert hat, feiert
                           das andere nicht noch einmal.
     besitz                Vereinigung. Gekauft ist gekauft; bezahlt wird es
                           ueber muenzen_aus.
     muenzen_ges,          je das Maximum. Beides sind Zaehler, die nur
     muenzen_aus           wachsen ("jemals verdient / ausgegeben"); die
                           Summe zaehlte die gemeinsame Vorgeschichte doppelt,
                           und jeder weitere Abgleich noch einmal. Was zwei
                           Geraete getrennt verdient haben, zaehlt so nur
                           einmal - lieber zu wenig als erfundene Muenzen.
                           Ausgegeben aber mindestens die Preise von allem in
                           besitz (dieselbe Regel wie in sicherungPlausibel):
                           wer auf zwei Geraeten getrennt je fuer 100 gekauft
                           hat, hat 200 ausgegeben.
     rekord                Maximum. standUebernehmen() kappt ihn danach an
                           den Lerntagen und rechnet aus den vereinigten
                           Tagen nach.
     geschenk_jahr         Maximum - ein gegebenes Geschenk geht nie wieder
                           auf, wie in standUebernehmen().
     wann                  je Schluessel das fruehere Datum: "wann zuerst
                           geschafft".
     tagwerk               je Tag und Zaehler das Maximum. Die Summe waere bei
                           zwei Geraeten am selben Tag genauer, aber nicht
                           idempotent - jeder Abgleich zaehlte den Tag noch
                           einmal dazu, und die Tagesaufgaben gaeben neue
                           Muenzen.
     topf                  Vereinigung der Schluessel. Steht ein Fehler auf
                           beiden Seiten, gewinnt der neuere Fehler (groesseres
                           z): seine Zaehlung n beginnt bei ihm, die andere
                           gehoert zu einem frueheren. Bei gleichem z das
                           kleinere n - lieber einmal mehr ueben als einen
                           Fehler verlieren, der nur auf einem Geraet geuebt
                           wurde. Hoechstens TOPF_MAX, es bleiben die
                           neuesten, wie in topfMerken(). Weitere Angaben
                           eines Eintrags bleiben beim Gewinner stehen; bei
                           sonst Gleichem gewinnt b (28.10.2026). Verlassen
                           darf sich darauf keine neuere Fassung -
                           topfMerken() schreibt Eintraege neu und loescht
                           sie, siehe STAND_FELDER.
     stern                 Vereinigung. Auf beiden Seiten markiert: das
                           neuere z (zuletzt markiert) und das groessere r
                           (zuletzt geuebt). Danach sternPruefen().
     zahnarzt              der Schalter mit dem neueren Zeitstempel z, siehe
                           zaMischen() (06.11.2026). Der Lernstand des Teils
                           steckt in gewusst und bestanden.
     kartei                je Wort der Stand, der zuletzt geuebt wurde
                           (Ajdin am 28.10.2026). Am selben Tag der fruehere
                           Termin, dann die kleinere Stufe: lieber einmal zu
                           frueh wiederholen als zu spaet. Der Zaehler fuer
                           heute: der neuere Tag, am selben Tag die groessere
                           Zahl, wie bei tagwerk. Nichts aus der Zukunft, wie
                           bei topf - siehe karteiMischen() (29.10.2026).
     leben, schutz         die Seite mit dem neueren Zeitstempel zeit - dort
                           ist zuletzt etwas passiert (Herz verloren, Schutz
                           verbraucht, beides gekauft, siehe zeitNachKauf()).
                           Bei gleicher Zeit die kleinere Anzahl: ein Abgleich
                           verschenkt keine Herzen.
     einstufung            die neuere (tag); fehlt sie auf einer Seite, die
                           andere. Bei gleichem Tag entscheidet der Text -
                           nur damit beide Richtungen dasselbe ergeben.
     bewertung             gezeigt vereinigt, nein und bewertet je "oder":
                           wer auf einem Geraet abgelehnt oder bewertet hat,
                           wird auf keinem mehr gefragt. Einen Zeitstempel
                           hat sie nicht; beide Merker gehen nur von false
                           nach true, das "oder" ist also der neuere Stand.
     getragen              eine Wahl, kein Fortschritt: das Geraet (a)
                           gewinnt, traegt es nichts, die Cloud. Bis zum
                           28.10.2026 die einzige Stelle, die nicht
                           kommutativ ist - mit Absicht, das Geraet bleibt
                           massgeblich. Seitdem auch die Felder einer
                           neueren Fassung, siehe unten.
   premium aus einer alten Datei faellt weg (STAND_ALT). Seit 28.10.2026
   bleibt alles andere, was diese Fassung nicht kennt, unveraendert stehen
   (standFremd). Diese Fassung aendert solche Felder nie, sie traegt nur
   weiter, was sie gelesen hat; zusammengefuehrt wird nur, wenn seit dem
   eigenen letzten Abgleich jemand anderes geschrieben hat, und dessen
   Fassung ist dann die neuere. Darum (Pruefbefund 28.10.2026):
     - Was b, die Cloud, hat, gilt - ganz und zuerst. So ueberschreibt ein
       Handy mit v109 die Wiederholungsdaten eines Tablets mit v110 nicht
       mit einer alten Kopie.
     - Ein Feld nur in a kommt mit, wenn es auf diesem Geraet neu ist,
       etwa aus einer Sicherungsdatei. Stand es beim letzten Abgleich
       schon in der Cloud (cloudVorher: die Namen aus m.fremd, siehe
       cloudAbgleich), hat die neuere Fassung es seitdem geloescht oder
       umbenannt, und es bleibt weg - vorher kam es von hier aus wieder
       in die Cloud. Ohne cloudVorher (erste Anmeldung, Tests) kommt
       alles aus a mit.
     - Die Felder aus a nur, soweit neben denen aus b Platz ist
       (CLOUD_GROESSE_MAX). Fuer sie faellt nie eins aus b weg - vorher
       konnte die Summe beider Seiten beim Uebernehmen alle verwerfen.
   Nicht kommutativ, mit Absicht - wie "getragen".
   Nicht hier, sondern drumherum geprueft wird, ob etwas plausibel ist: b
   kommt von aussen wie eine Sicherungsdatei und geht vorher durch
   sicherungPlausibel(), das Ergebnis durch standUebernehmen() - siehe
   cloudUebernehmen(). sicherungPlausibel() auf das Ergebnis hiesse, die
   eigenen Muenzen und Lerntage dieses Geraets zu kappen; genau das schliesst
   der Kommentar in standUebernehmen() fuer den eigenen Stand aus.
   erstesMal: b ist der Stand eines Kontos, und dieses Geraet gleicht zum ersten
   Mal mit ihm ab, siehe bei m.schutz. */
function standZusammenfuehren(a, b, cloudVorher, erstesMal){
  const objekt = x => (x && typeof x === 'object' && !Array.isArray(x)) ? x : null;
  a = objekt(a) || {}; b = objekt(b) || {};
  const texte = x => Array.isArray(x) ? x.filter(s => typeof s === 'string') : [];
  const vereint = (x, y) => [...new Set(texte(x).concat(texte(y)))].sort();
  const zahl = x => (typeof x === 'number' && isFinite(x) && x >= 0) ? x : 0;
  const schluessel = (x, y) => [...new Set(Object.keys(x).concat(Object.keys(y)))].sort();
  const textVergleich = (x, y) => x < y ? -1 : (x > y ? 1 : 0);
  const m = {};
  ['gewusst', 'bestanden', 'gelesen', 'tage', 'frost', 'gefeiert', 'besitz']
    .forEach(k => { m[k] = vereint(a[k], b[k]); });
  const preis = id => { const w = ZIERRAT.find(x => x.id === id && !x.voll); return w ? w.preis : 0; };
  m.muenzen_ges = Math.max(ganzAbNull(a.muenzen_ges), ganzAbNull(b.muenzen_ges));
  m.muenzen_aus = Math.max(ganzAbNull(a.muenzen_aus), ganzAbNull(b.muenzen_aus),
                           m.besitz.reduce((s, id) => s + preis(id), 0));
  m.rekord = Math.max(ganzAbNull(a.rekord), ganzAbNull(b.rekord));
  m.geschenk_jahr = Math.max(ganzAbNull(a.geschenk_jahr), ganzAbNull(b.geschenk_jahr));
  /* Nichts aus der Zukunft (Pruefbefund 19.10.2026): eine vorgestellte
     Handy-Uhr oder ein gefaelschtes Cloud-Dokument brachte sonst einen
     Fehler mit z weit voraus mit. topfRunde() nimmt das kleinste z zuerst,
     topfMerken() verdraengt das kleinste - so ein Fehler kaeme nie mehr
     dran und ginge nie mehr weg, und die Cloud truege ihn auf jedes
     Geraet. z wird darum wie in sternPruefen() auf jetzt gekappt; Tage
     und Daten nach heute fallen weg. */
  const jetzt = Date.now(), heute = today();
  const bisHeute = d => istDatum(d) && d <= heute;
  /* Object.fromEntries statt Zuweisung: ein Schluessel "__proto__" aus einer
     fremden Datei wird so ein gewoehnlicher Eintrag, wie bei topf. */
  const wa = objekt(a.wann) || {}, wb = objekt(b.wann) || {};
  m.wann = Object.fromEntries(schluessel(wa, wb).map(k => {
    const x = bisHeute(wa[k]) ? wa[k] : '', y = bisHeute(wb[k]) ? wb[k] : '';
    return [k, (x && y) ? (x < y ? x : y) : (x || y)];
  }).filter(([, d]) => d));
  const ta = objekt(a.tagwerk) || {}, tb = objekt(b.tagwerk) || {};
  m.tagwerk = Object.fromEntries(schluessel(ta, tb).filter(bisHeute).map(tag => {
    const x = objekt(ta[tag]) || {}, y = objekt(tb[tag]) || {};
    return [tag, Object.fromEntries(schluessel(x, y).map(id => [id, Math.max(zahl(x[id]), zahl(y[id]))]))];
  }));
  const eintrag = e => { e = objekt(e); return (e && typeof e.typ === 'string') ? {...e, typ: e.typ, n: ganzAbNull(e.n), z: Math.min(zahl(e.z), jetzt)} : null; };
  const pa = objekt(a.topf) || {}, pb = objekt(b.topf) || {};
  const topfListe = schluessel(pa, pb).filter(k => k.length <= 200 && STERN_ART.test(k)).map(k => {
    const x = eintrag(pa[k]), y = eintrag(pb[k]);
    if(!x || !y) return [k, x || y];
    if(x.z !== y.z) return [k, x.z > y.z ? x : y];
    if(x.n !== y.n) return [k, x.n < y.n ? x : y];
    return [k, x.typ < y.typ ? x : y];
  }).filter(([, e]) => e);
  topfListe.sort((p, q) => (q[1].z - p[1].z) || textVergleich(p[0], q[0]));
  m.topf = Object.fromEntries(topfListe.slice(0, TOPF_MAX));
  const sa = objekt(a.stern) || {}, sb = objekt(b.stern) || {};
  m.stern = sternPruefen(Object.fromEntries(schluessel(sa, sb).map(k => {
    const x = objekt(sa[k]), y = objekt(sb[k]);
    return [k, (x && y) ? {z: Math.max(zahl(x.z), zahl(y.z)), r: Math.max(zahl(x.r), zahl(y.r))} : (x || y)];
  })));
  m.kartei = karteiMischen(a.kartei, b.kartei);
  m.zahnarzt = zaMischen(a.zahnarzt, b.zahnarzt);
  const zeitWahl = (x, y, max, leer) => {
    const gut = e => {
      e = objekt(e);
      if(!e || typeof e.anzahl !== 'number' || !isFinite(e.anzahl)) return null;
      return {anzahl: Math.max(0, Math.min(max, Math.floor(e.anzahl))),
              zeit: (typeof e.zeit === 'number' && isFinite(e.zeit)) ? e.zeit : 0};
    };
    x = gut(x); y = gut(y);
    if(!x || !y) return x || y || leer;
    if(x.zeit !== y.zeit) return x.zeit > y.zeit ? x : y;
    return x.anzahl <= y.anzahl ? x : y;
  };
  m.leben = zeitWahl(a.leben, b.leben, LEBEN_MAX, {anzahl: LEBEN_MAX, zeit: 0});
  /* Pruefbericht 1.3 (06.11.2026): Eine frische App stempelt auf der Startseite
     {1, jetzt} (syncSchutz). Das ist kein Ereignis, gewann beim ersten Abgleich
     aber ueber die neuere Zeit: Aus zwei Schutz im Konto wurde einer, auch auf dem
     alten Geraet, die 10 Tage begannen neu, und wer keinen hatte, bekam einen
     geschenkt. Beim ersten Abgleich zaehlt darum der Schutz des Kontos, wenn dort
     ein brauchbarer steht. Danach gilt wieder die neuere Zeit. */
  const vomKonto = erstesMal ? zeitWahl(b.schutz, null, SCHUTZ_MAX, null) : null;
  m.schutz = vomKonto || zeitWahl(a.schutz, b.schutz, SCHUTZ_MAX, {anzahl: 1, zeit: 0});
  /* Ein Einstieg (bis) schlaegt eine Einstufung ohne, egal wie alt, sonst nahm
     "Nein, ich fange neu an" auf einem neuen Geraet dem Konto den Einstieg, auf
     allen Geraeten und ohne Rueckweg (Pruefbericht 1.3). Wer wirklich von vorn
     lernt, stoert das nicht, siehe firstOpen(). */
  const ea = objekt(a.einstufung), eb = objekt(b.einstufung);
  const tagVon = e => istDatum(e.tag) ? e.tag : '';
  m.einstufung = (!ea || !eb) ? (ea || eb || null)
    : (!!ea.bis !== !!eb.bis) ? (ea.bis ? ea : eb)
    : (tagVon(ea) !== tagVon(eb)) ? (tagVon(ea) > tagVon(eb) ? ea : eb)
    : (JSON.stringify(ea) >= JSON.stringify(eb) ? ea : eb);
  const ba = objekt(a.bewertung) || {}, bb = objekt(b.bewertung) || {};
  m.bewertung = {gezeigt: vereint(ba.gezeigt, bb.gezeigt).filter(istDatum),
                 nein: !!(ba.nein || bb.nein), bewertet: !!(ba.bewertet || bb.bewertet)};
  const ga = typeof a.getragen === 'string' ? a.getragen : '';
  m.getragen = ga || (typeof b.getragen === 'string' ? b.getragen : '');
  /* Felder einer neueren Fassung: zuerst alle von b, dann, was nur a hat
     und dort neu ist, soweit Platz bleibt - siehe oben und standFremd. */
  const fb = standFremdAus(b), weg = new Set(Array.isArray(cloudVorher) ? cloudVorher : []);
  const nurA = Object.fromEntries(Object.entries(standFremdAus(a))
    .filter(([k]) => !Object.prototype.hasOwnProperty.call(fb, k) && !weg.has(k)));
  Object.assign(m, fb, standFremdAus(nurA, CLOUD_GROESSE_MAX - fremdPlatz(fb)));
  /* Eine tiefe Kopie: das Ergebnis teilt nichts mit a oder b. Sonst haengte
     standUebernehmen() etwa die einstufung des alten Stands wieder ein. */
  return JSON.parse(JSON.stringify(m));
}
var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
