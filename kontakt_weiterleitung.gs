/**
 * kontakt_weiterleitung.gs  -  bringt Nachrichten aus dem Kontaktformular ins Postfach
 *
 * Das Formular auf zmaj-lernapp.github.io/kontakt.html (seite_bauen.py) legt
 * jede Nachricht als Dokument nachrichten/{uid} in Firestore ab. Firebase
 * kann im Gratistarif Spark keine Mails schicken (dafuer braeuchte es Cloud
 * Functions und damit den Tarif Blaze). Dieses Skript laeuft deshalb als
 * Google Apps Script im Konto zmaj.lernapp@gmail.com: Alle 5 Minuten meldet
 * es sich als "Melder" bei Firebase an, holt die Nachrichten, schickt jede
 * als Mail an zmaj.lernapp@gmail.com und loescht sie erst danach aus
 * Firestore. Weg A, Ajdin am 28.10.2026. Es kostet nichts: Apps Script und
 * MailApp gehoeren zum Gratis-Gmail-Konto (100 Mails am Tag).
 *
 * EINRICHTEN (fuer Ajdin Schritt fuer Schritt in Release\Firebase_Anleitung.md)
 *   0. Vorher den Gmail-Filter der Sofortantwort um
 *      -subject:"[Zmaj-Formular]" ergaenzen (siehe WARUM SO).
 *   1. script.google.com, angemeldet mit zmaj.lernapp@gmail.com: neues
 *      Projekt "Zmaj-Formular", den ganzen Inhalt dieser Datei in Code.gs.
 *   2. Projekteinstellungen (Zahnrad) -> Skripteigenschaften, vier Eintraege:
 *        PROJEKT          die Projekt-ID von Firebase
 *        SCHLUESSEL       der Web-API-Schluessel (faengt mit AIza an)
 *        MELDER_MAIL      die Adresse des Melder-Kontos in Firebase
 *        MELDER_PASSWORT  dessen Passwort
 *      Nichts davon gehoert in den Code: Diese Datei steht oeffentlich im
 *      Repository. Die Eintraege GESENDET, FEHLVERSUCHE und STAU_GEMELDET
 *      legt das Skript selbst an.
 *   3. Oben die Funktion "einrichten" waehlen, Ausfuehren, die Berechtigungen
 *      erlauben (Mails in deinem Namen senden, externe Dienste aufrufen,
 *      Ausloeser). Sie legt den Zeitausloeser "alle 5 Minuten" fuer
 *      weiterleiten() an und laesst es einmal laufen.
 *   Scheitert spaeter ein Lauf, schickt Google von selbst eine Mail an das
 *   Konto (Ausloeser -> Fehlerbenachrichtigung, Standard: taeglich).
 *
 * WARUM SO
 *   - Die Mail geht immer an ZIEL, nie an die Adresse aus dem Formular. Die
 *     steht nur bei "Antworten an" (replyTo). Sonst koennte jeder das Skript
 *     als Mailschleuder benutzen, die in unserem Namen an fremde Adressen
 *     schreibt. Aus demselben Grund nimmt der Gmail-Filter der Sofortantwort
 *     Mails mit "[Zmaj-Formular]" im Betreff aus - und zwar BEVOR dieses
 *     Skript zum ersten Mal laeuft.
 *   - MailApp statt GmailApp: Es darf nur senden, nicht das Postfach lesen.
 *   - Geloescht wird erst nach dem Versand. Scheitert das Loeschen, merkt sich
 *     das Skript das Dokument (Skripteigenschaft GESENDET) und schickt es beim
 *     naechsten Lauf nicht noch einmal, es loescht nur.
 *   - Eine Nachricht, die sich nicht verschicken laesst, haelt die anderen
 *     nicht auf (Pruefbericht 28.10.2026: Vorher brach der ganze Lauf ab, und
 *     weil die Liste nach zeit sortiert ist, stand dieselbe Nachricht bei
 *     jedem Lauf wieder vorn - ein einziges praepariertes Dokument haette das
 *     Formular fuer immer stillgelegt). Jede Nachricht hat drei Stufen:
 *       1. normal, mit "Antworten an", wenn die Adresse ADRESSE entspricht;
 *       2. Ersatz ohne "Antworten an", fester Betreff, die Adresse nur
 *          maskiert im Text, Steuerzeichen ersetzt;
 *       3. nach FEHLER_MAX Laeufen, in denen 1 und 2 scheiterten: ein
 *          Hinweis ganz ohne Inhalt aus dem Formular. Geht der raus, wird das
 *          Dokument geloescht. Geht auch der nicht raus, ist MailApp selbst
 *          gestoert - dann bleibt alles liegen, verloren geht nichts.
 *     Danach kommt die naechste Nachricht dran.
 *   - Ist das Tageskontingent von MailApp fast aufgebraucht, bleiben die
 *     uebrigen Nachrichten in Firestore und gehen am naechsten Tag raus. Die
 *     letzte Mail des Tages (RESERVE) ist ein Hinweis auf den Stau, einmal
 *     am Tag - bei Spam ist das das Zeichen, "Anonym" in Firebase
 *     auszuschalten (Notbremse in Release\Firebase_Anleitung.md, Schritt 12).
 *   - Kein Inhalt im Protokoll: Logger bekommt nur Zahlen.
 */

var ZIEL = 'zmaj.lernapp@gmail.com';
var BETREFF = '[Zmaj-Formular]';
var JE_LAUF = 20;            // hoechstens so viele Nachrichten je Lauf
var RESERVE = 1;             // so viele Mails des Tages bleiben fuer den Hinweis auf einen Stau
var GESENDET = 'GESENDET';   // Skripteigenschaft: verschickt, aber noch nicht geloescht
var FEHLER = 'FEHLVERSUCHE'; // Skripteigenschaft: Dokument -> Zahl der Laeufe, in denen nichts rausging
var FEHLER_MAX = 3;          // danach nur noch der Hinweis ohne Inhalt, dann loeschen
var STAU = 'STAU_GEMELDET';  // Skripteigenschaft: Tag, an dem der Stau gemeldet wurde
var MERKEN_MAX = 50;         // Eigenschaften fassen 9 KB je Wert
// Nur was hier passt, kommt in "Antworten an". Druckbares ASCII wie bei
// type="email" im Browser, Punkte im Namen nur einzeln und nicht am Rand,
// Teile der Domain ohne Bindestrich am Rand. Etwas strenger als die Regel in
// firestore.rules: Was die Regel durchlaesst, hier aber nicht passt, kommt
// trotzdem an - die Adresse steht dann nur maskiert im Text.
var ADRESSE = /^[A-Za-z0-9!#$%&'*+\/=?^_`{|}~-]+(\.[A-Za-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?)+$/;
// Steuer- und unsichtbare Zeichen, die im Ersatz (Stufe 2) durch ? ersetzt werden.
var STEUERZEICHEN = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F\u00AD\u200B-\u200F\u2028-\u202E\u2060-\u206F\uFEFF]/g;

/** Einmal von Hand ausfuehren: Ausloeser anlegen (alte ersetzen), dann ein Lauf. */
function einrichten() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'weiterleiten') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('weiterleiten').timeBased().everyMinutes(5).create();
  weiterleiten();
}

/** Der Lauf alle 5 Minuten. Laeuft der vorige noch, faellt dieser aus. */
function weiterleiten() {
  var sperre = LockService.getScriptLock();
  if (!sperre.tryLock(1000)) return;
  try {
    var n = lauf_();
    Logger.log('weitergeleitet: ' + n);
  } finally {
    sperre.releaseLock();
  }
}

function lauf_() {
  if (MailApp.getRemainingDailyQuota() < 1) {
    Logger.log('Tageskontingent fuer Mails aufgebraucht - morgen weiter.');
    return 0;
  }
  var e = eigenschaften_();
  var ausweis = anmelden_(e);
  var liste = firestore_(e, ausweis, 'get', 'nachrichten?pageSize=' + JE_LAUF + '&orderBy=zeit');
  var doks = (liste && liste.documents) || [];
  var gesendet = gemerkt_(GESENDET, []);
  var fehler = gemerkt_(FEHLER, {});
  var n = 0;
  var liegen = 0;
  for (var i = 0; i < doks.length; i++) {
    var dok = doks[i];
    if (gesendet.indexOf(dok.name) < 0) {
      if (MailApp.getRemainingDailyQuota() <= RESERVE) {
        liegen = doks.length - i;
        break;
      }
      if (!zustellen_(dok, fehler)) continue;   // bleibt liegen, die naechste kommt dran
      gesendet.push(dok.name);
      merken_(GESENDET, gesendet);
      n++;
    }
    firestore_(e, ausweis, 'delete', dok.name);
    var j = gesendet.indexOf(dok.name);
    if (j >= 0) gesendet.splice(j, 1);
    merken_(GESENDET, gesendet);
    if (dok.name in fehler) {
      delete fehler[dok.name];
      merken_(FEHLER, fehler);
    }
  }
  // Lag die ganze Sammlung vor, vergessen, was es nicht mehr gibt (etwa nach
  // der Notbremse in der Konsole geloescht).
  if (doks.length < JE_LAUF) {
    var da = doks.map(function (d) { return d.name; });
    var weg = Object.keys(fehler).filter(function (k) { return da.indexOf(k) < 0; });
    weg.forEach(function (k) { delete fehler[k]; });
    if (weg.length) merken_(FEHLER, fehler);
  }
  var gescheitert = Object.keys(fehler).length;
  if (gescheitert) Logger.log('nicht zustellbar, warten auf den naechsten Lauf: ' + gescheitert);
  if (liegen) stau_(liegen, doks.length >= JE_LAUF);
  return n;
}

/**
 * Schickt eine Nachricht, Stufe fuer Stufe (siehe WARUM SO). true, wenn eine
 * Mail rausging - dann darf das Dokument weg. false zaehlt einen Fehlversuch.
 */
function zustellen_(dok, fehler) {
  var stufen = [function () { mail_(dok, false); }, function () { mail_(dok, true); }];
  if ((fehler[dok.name] || 0) >= FEHLER_MAX) stufen.push(function () { hinweis_(dok); });
  for (var i = 0; i < stufen.length; i++) {
    try {
      stufen[i]();
      return true;
    } catch (x) {
      // Nur die Stufe, nicht die Meldung: Die kann die Adresse enthalten.
      Logger.log('Versand gescheitert, Stufe ' + (i + 1));
    }
  }
  fehler[dok.name] = (fehler[dok.name] || 0) + 1;
  merken_(FEHLER, fehler);
  return false;
}

function eigenschaften_() {
  var p = PropertiesService.getScriptProperties();
  var e = {};
  ['PROJEKT', 'SCHLUESSEL', 'MELDER_MAIL', 'MELDER_PASSWORT'].forEach(function (k) {
    e[k] = p.getProperty(k);
    if (!e[k]) throw new Error('Skripteigenschaft ' + k + ' fehlt (Projekteinstellungen -> Skripteigenschaften).');
  });
  return e;
}

/** Als Melder bei Firebase anmelden; gibt den Ausweis (ID-Token, 1 Stunde) zurueck. */
function anmelden_(e) {
  var r = UrlFetchApp.fetch(
    'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=' + encodeURIComponent(e.SCHLUESSEL), {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({email: e.MELDER_MAIL, password: e.MELDER_PASSWORT, returnSecureToken: true}),
      muteHttpExceptions: true
    });
  if (r.getResponseCode() !== 200) {
    throw new Error('Anmeldung als Melder gescheitert: ' + r.getResponseCode() + ' ' + grund_(r));
  }
  var d = JSON.parse(r.getContentText());
  if (!d.idToken) throw new Error('Anmeldung als Melder: kein Ausweis in der Antwort.');
  return d.idToken;
}

/** pfad: relativ zu .../documents/ oder ein voller Dokumentname (projects/...). */
function firestore_(e, ausweis, art, pfad) {
  var url = 'https://firestore.googleapis.com/v1/' + (pfad.indexOf('projects/') === 0 ? pfad
    : 'projects/' + encodeURIComponent(e.PROJEKT) + '/databases/(default)/documents/' + pfad);
  var r = UrlFetchApp.fetch(url, {
    method: art,
    headers: {Authorization: 'Bearer ' + ausweis},
    muteHttpExceptions: true
  });
  var code = r.getResponseCode();
  if (code < 200 || code > 299) throw new Error('Firestore ' + art + ': ' + code + ' ' + grund_(r));
  var text = r.getContentText();
  return text ? JSON.parse(text) : {};
}

/** Der Grund aus einer Fehlerantwort von Google, ohne Inhalte. */
function grund_(r) {
  try {
    var f = JSON.parse(r.getContentText()).error || {};
    return String(f.status || f.message || '');
  } catch (x) {
    return '';
  }
}

function wert_(feld) {
  return feld && typeof feld.stringValue === 'string' ? feld.stringValue : '';
}

function eingang_(dok) {
  var f = dok.fields || {};
  var zeit = f.zeit && f.zeit.timestampValue ? new Date(f.zeit.timestampValue) : new Date();
  if (isNaN(zeit.getTime())) zeit = new Date();
  return Utilities.formatDate(zeit, 'Europe/Berlin', 'dd.MM.yyyy HH:mm');
}

/** Die einzige Stelle, die sendet. Empfaenger ist immer ZIEL. */
function senden_(betreff, text, antwortAn) {
  var nachricht = {to: ZIEL, subject: BETREFF + ' ' + betreff, name: 'Zmaj-Formular', body: text};
  if (antwortAn) nachricht.replyTo = antwortAn;
  MailApp.sendEmail(nachricht);
}

/** Stufe 1 (ersatz false) und Stufe 2 (ersatz true). */
function mail_(dok, ersatz) {
  var f = dok.fields || {};
  var text = wert_(f.text);
  var antwort = wert_(f.antwort).trim();
  var gueltig = !ersatz && antwort.length <= 254 && ADRESSE.test(antwort);
  // JSON.stringify maskiert Anfuehrungszeichen und Steuerzeichen.
  var adresse = gueltig ? antwort : '(ungeprueft) ' + JSON.stringify(antwort.slice(0, 254));
  var betreff = ersatz ? '(Ersatz: Antwortadresse im Text pruefen)'
    : (text.replace(/\s+/g, ' ').trim().slice(0, 60) || '(ohne Text)');
  var zeilen = [
    'Antwort an: ' + adresse,
    'Sprache: ' + wert_(f.sprache).slice(0, 5),
    'Eingang: ' + eingang_(dok),
    '',
    ersatz ? text.replace(STEUERZEICHEN, '?') : text
  ];
  senden_(betreff, zeilen.join('\n'), gueltig ? antwort : null);
}

/** Stufe 3: nur Zahlen und die Dokument-ID, nichts aus dem Formular. */
function hinweis_(dok) {
  senden_('Nachricht nicht zustellbar', [
    'Eine Nachricht aus dem Kontaktformular liess sich in ' + FEHLER_MAX + ' Laeufen nicht als Mail',
    'verschicken, auch nicht ohne "Antworten an". Sie wird jetzt aus Firestore geloescht,',
    'damit sie die anderen nicht aufhaelt.',
    '',
    'Eingang: ' + eingang_(dok),
    'Dokument: nachrichten/' + String(dok.name).split('/').pop()
  ].join('\n'), null);
}

/** Hoechstens einmal am Tag: Das Kontingent reicht nicht fuer alle Nachrichten. */
function stau_(liegen, mehr) {
  var p = PropertiesService.getScriptProperties();
  var heute = Utilities.formatDate(new Date(), 'Europe/Berlin', 'yyyy-MM-dd');
  if (p.getProperty(STAU) === heute || MailApp.getRemainingDailyQuota() < 1) return;
  senden_('Stau: Mail-Kontingent fuer heute aufgebraucht', [
    'Heute sind mehr Nachrichten ueber das Formular gekommen, als Gmail an einem Tag',
    'verschicken laesst. Es warten noch ' + (mehr ? 'mindestens ' : '') + liegen + '. Sie gehen ab morgen der Reihe',
    'nach raus.',
    '',
    'Ist das Spam: Firebase -> Authentication -> Anmeldemethode -> Anonym deaktivieren.',
    'Dann nimmt das Formular nichts mehr an; Mail und App laufen weiter. Danach in',
    'Firestore die Sammlung nachrichten loeschen (Notbremse in',
    'Release\\Firebase_Anleitung.md, Schritt 12).'
  ].join('\n'), null);
  p.setProperty(STAU, heute);
}

/** Eine gemerkte Liste oder Zuordnung aus den Skripteigenschaften. */
function gemerkt_(name, leer) {
  try {
    var wert = JSON.parse(PropertiesService.getScriptProperties().getProperty(name) || 'null');
    var passt = wert !== null && typeof wert === 'object' && Array.isArray(wert) === Array.isArray(leer);
    return passt ? wert : leer;
  } catch (x) {
    return leer;
  }
}

/** Merkt sich hoechstens MERKEN_MAX Eintraege, die neuesten. */
function merken_(name, wert) {
  if (Array.isArray(wert)) {
    while (wert.length > MERKEN_MAX) wert.shift();
  } else {
    var schluessel = Object.keys(wert);
    while (schluessel.length > MERKEN_MAX) delete wert[schluessel.shift()];
  }
  PropertiesService.getScriptProperties().setProperty(name, JSON.stringify(wert));
}
