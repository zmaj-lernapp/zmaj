/* =================== EINSTELLUNGEN =================== */
/* Konto und Einstellungen sind zwei getrennte Seiten: hinter dem
   Benutzerknopf steht alles zur Person, hinter dem Zahnrad alles zum Gerät. */
function showKonto(){
  showView('kontoView'); $('kopfLeiste').style.display='none';
  setzeZurueck(t('btn.zurueck'), showHome);
  $('tag').textContent=t('set.profil');
  /* Erfolge ganz oben (13.11.2026), seit 14.11.2026 als kompakte Leiste;
     die Wand zeigt showErfolge(). Das Profil gibt es auch ohne Konto (Web-
     Demo, Handy vor der Pflicht-Anmeldung, iPhone nach "Spaeter"): dann
     stehen nur Erfolge und Lernserie da, der Kasten mit Konto und Abmelden
     bleibt weg. */
  $('erfolgWand').hidden = true; $('erfolgWand').innerHTML = '';
  $('serieKasten').hidden = false;
  $('kontoKasten').hidden = !(MIT_SERVER || (cloudModus() && !!cloudMerker()));
  renderErfolgLeiste();
  $('setProfilName').innerHTML = mitSymbol('profil', esc(profil+(premium?' · '+t('profil.vollversion'):'')));
  $('setProfilMail').innerHTML = kontoMail ? mitSymbol('brief', esc(kontoMail)) : '';
  $('setSerie').textContent = tp('set.serie_stand', streak());
  const s=schutzNow(), rest=naechsterSchutzIn();
  $('setSchutz').textContent = tp('serie.schutz', s) +
    (s>=SCHUTZ_MAX ? ' · '+t('serie.schutz_voll') : (rest ? ' · '+t('serie.schutz_naechster',{zeit:fmtTage(rest)}) : ''));
  $('setSchutzInfo').textContent = t('set.serie_schutz_sub',{tage:SCHUTZ_TAGE, max:SCHUTZ_MAX});
  if(cloudModus()) kontoSeiteCloud();     // Pflicht-Anmeldung, 28.10.2026
}
/* Die ganze Wand der Erfolge, nach einem Tipp auf die Leiste im Profil
   (14.11.2026). Eine eigene Seite in derselben Ansicht: oben nur die Wand,
   Konto und Lernserie sind weg, und Zurueck - die Taste oben wie die des
   Handys - fuehrt ins Profil, nicht auf die Startseite. */
function showErfolge(){
  showView('kontoView'); $('kopfLeiste').style.display='none';
  setzeZurueck(t('btn.zurueck'), showKonto);
  $('tag').textContent = t('erfolg.titel');
  $('erfolgLeiste').hidden = true; $('kontoKasten').hidden = true; $('serieKasten').hidden = true;
  renderErfolgWand();
}
function showSettings(){
  showView('settingsView'); $('kopfLeiste').style.display='none';
  setzeZurueck(t('btn.zurueck'), showHome);
  $('tag').textContent=t('btn.einstellungen');
  /* 28.10.2026 (Pruefbericht): Angemeldet liegt eine Kopie im Konto -
     "nur auf diesem Geraet" stimmt dann nicht mehr. Ohne Konto (und ohne
     Firebase-Projekt) bleibt der Satz von v108. */
  /* 01.11.2026: Mit Konto gibt es die Sicherung als Datei gar nicht mehr.
     Ajdin: "Sicherung speichern kann raus weil wir ja jetzt einen server
     haben" - "Ganz raus", Speichern und Einlesen. In der Handy-App
     (cloudModus(), also CLOUD_AN mit Zugangsdaten) ist der ganze Block
     weg, angemeldet oder nicht: das Konto sichert alles. Damit gibt es
     auch den Satz fuer Angemeldete (set.sicherung_sub_konto) nicht mehr.
     Ohne Cloud - Quelle, Web-Demo, start.py - bleibt alles wie vorher,
     mit dem Satz von v108 (data-t in setSichSub). */
  $('setSichBox').style.display = cloudModus() ? 'none' : '';
  // Werbung: Die Zeile erscheint erst, wenn wirklich geworben wird oder
  // schon einmal gefragt wurde. Vorher gäbe es nichts zu ändern.
  // Mit AdMob verwaltet Google die Antwort, und Google sagt auch, ob ein
  // Knopf zum Ändern verlangt ist - außerhalb der EU ist er das nicht.
  /* Nur EIN Bedienelement fuer die Werbung. Ajdin am 18.09.2026: vorher
     standen zwei untereinander und man wusste nicht, welches nun gilt.
     Wo AdMob laeuft und Google einen eigenen Knopf verlangt, gehoert die
     Einwilligung Google - unser Schalter duerfte sie dort gar nicht selbst
     umstellen. Dann steht Googles Zeile da, und sonst nichts. Ueberall sonst,
     am PC und ohne AdMob, steht unser Schalter, und der wirkt sofort. */
  /* Die Vollversion nur dort, wo man sie auch kaufen kann - also nur mit
     dem Abo-Plugin, nicht im Browser am PC. */
  const kaufbar = !!aboPlugin();
  $('setVollBox').style.display = kaufbar ? '' : 'none';
  if(kaufbar){ vollMeldung(''); vollZeileZeigen(); vollAbgleichen(); produkteNachsehen(); }
  /* Wer die Vollversion hat, sieht gar keine Werbung mehr - dann ist auch
     der Schalter zur Werbe-Einwilligung gegenstandslos. (So bis
     01.11.2026: seitdem haben Abonnenten auf dem Geraet wieder den
     Schalter, siehe die beiden Kommentare darunter.) */
  /* Punkt 8 aus WERBUNG_PRUEFUNG.md: gegenstandslos ist der SCHALTER, nicht
     der Widerruf. Eine frueher als Gratisnutzer erteilte Einwilligung liegt
     weiter in Googles Speicher, und sie muss sich so leicht zuruecknehmen
     lassen, wie sie gegeben wurde - die Datenschutzerklaerung verspricht das
     in acht Sprachen. Deshalb eine eigene Zeile, nur auf dem Geraet: am PC
     gibt es Googles Fenster gar nicht. */
  /* 01.11.2026: Die eigene Zeile ist jetzt dieselbe wie fuer alle - mit
     Schalter statt "Wahl aendern" (Ajdin: "bei werbung statt wahl aendern
     soll so ein schalter sein", fuer Abonnenten "Ja, auch Schalter").
     Abonnenten sehen sie weiter nur auf dem Geraet (aboWerbeZeile). Beim
     Oeffnen zeigt sie den Stand auf dem Geraet und fragt NICHT bei Google
     nach (kein werbungAbgleichen) - das kommt erst mit einem Tipp, siehe
     einwilligungWiderrufen(). */
  const abo = aboWerbeZeile();
  const zeigen = abo || (!unlimited()
    && (WERBUNG_ECHT || EINWILLIGUNG_TEST || einwilligungGueltig() || admobDa()));
  $('setWerbungBox').style.display = zeigen ? '' : 'none';
  if(zeigen){ werbungZeileZeigen(); if(!abo) werbungAbgleichen(); }
  benSchalterZeigen();
  renderLangSel();
}
var teileDa = (teileDa || 0) + 1;   // dieser Teil ist ganz gelaufen, siehe teileDa oben
