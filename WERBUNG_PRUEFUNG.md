# Prüfung der Werbe-Einbindung

Vom **20.09.2026**, am Tag nach dem Anlegen des AdMob-Kontos und
bevor die echten Kennungen eingesetzt werden. Fünf Blickwinkel:
Kennungen, Einwilligung, Platzierung, Fehlerfall, Zielgruppe. Jeder
Befund wurde danach von einem zweiten Durchgang angegriffen, der ihn
widerlegen sollte — hier steht nur, was das überstanden hat.

**Nichts davon ist im laufenden geschlossenen Test zu ändern.** Jede
Einreichung setzt Googles Prüfuhr zurück. Das gehört alles in den
ersten Build NACH dem Test, zusammen mit dem Kennungstausch
(`admob_scharf.py`) und dem dauerhaften Premium.

Solange Testkennungen laufen, kann keiner dieser Punkte Schaden
anrichten: Google zählt Testanzeigen nicht. Gefährlich werden sie in
dem Moment, in dem `ADMOB_TEST` auf `false` steht.

| Schwere | Anzahl |
|---|---|
| Kontogefährdend | 3 |
| Schwer | 11 |
| Mittel | 5 |
| Klein | 1 |

---

## Stand am 30.09.2026

**Behoben: die Punkte 4, 6, 7, 8, 9, 11, 13, 14, 15, 16, 17, 18 und 19.**
Damit sind **alle zwanzig Punkte abgehakt** — 5, 10 und 12 am 28./29.09.,
1, 2 und 3 am 29.09., 20 war schon vorher erledigt.

Gegengeprüft mit Googles Testkennungen auf beiden Geräten — Galaxy S9
(Android 10) bis Fassung 59, danach Galaxy S21 Ultra (Android 15) bis
Fassung 62 — und dort, wo der Fehler nur ohne AdMob-Plugin auftritt, im
Browser.

**Punkt 12 war schon behoben** und stand nur noch aus Versehen in der
Liste: `werbungFuerLeben()` zeigt seit dem 29.09. `kurzMeldung(t('werbung.
keine_anzeige'))`, wenn keine Anzeige kam. Nachgesehen, nicht angenommen.

**Punkt 9 und 13 — der Doppeltipp.** Es gab keinen Riegel. Jetzt sitzt
`anzeigeLaeuft` in `zeigeWerbung()` — nicht in `zeigeWerbungJetzt()`, weil
auch der Zweitversuch über `admobStart()` durch diese Tür geht. Jeder
Ausgang läuft über `fertigEinmal()`, damit der Riegel wieder aufgeht.
Dazu wird der Knopf `lAd` beim Tippen ausgegraut: ein Knopf, der sich
nicht rührt, lädt zum zweiten Tipp ein.

Im Browser gemessen, drei Tipps unmittelbar hintereinander:

```
erster  -> Überlagerung 1, Riegel zu, Kontingent 1
zweiter -> false, keine zweite Überlagerung
dritter -> false, keine zweite Überlagerung
nach dem Schliessen: Riegel wieder auf, nächste Anzeige läuft
```

**Dabei eine neue Gefahr eingebaut und gleich wieder entschärft.** Ein
Riegel, den niemand öffnet, sperrt die Werbung bis zum Neustart der App —
vorher kostete ein hängender Aufruf nur diesen einen Versuch. Beim Messen
stand genau der Fall auf dem Schirm. Es gibt jetzt eine Sicherheitsleine:
ein Wecker über 150 Sekunden, der den Riegel notfalls selbst aufmacht.
Die Frist liegt über der längsten inneren Frist von 120 Sekunden, greift
also nur, wenn wirklich niemand mehr antwortet.

**Punkt 11 und 16 — die weggeworfene Belohnung.** Vorher entschied ein
`Promise.race` gegen 120 Sekunden darüber, ob es ein Leben gibt. Wer
während des Videos angerufen wurde, sah es zu Ende und bekam nichts; wer
abbrach, wartete zwei Minuten auf nichts. Jetzt halten zwei Zuhörer beides
getrennt fest — `onRewardedVideoAdReward` sagt, **dass** die Belohnung
fällig wurde, `onRewardedVideoAdDismissed` beendet das Warten. Das Plugin
schreibt eigens dazu, dass Dismissed über die Belohnung nichts aussagt.

Erst die Ereignisse einzeln vermessen, um nicht auf Vermutungen zu bauen:

```
prepare fertig    4193 ms
Loaded            4194 ms
Showed            4567 ms
Reward           10020 ms   show löst auf: {type:"coins", amount:10}
```

Dann der ganze Weg in der App, Leben vorher auf 0:

```
Video angesehen, danach geschlossen:
    lief: true, Rückmeldung nach 22,2 s  — nicht nach 120 s
    Leben 0 -> 1, Riegel wieder auf, Kontingent zählt
```

Die 22,2 Sekunden sind der Beleg: die Rückmeldung kam, als die Anzeige
geschlossen wurde. Vorher wäre an dieser Stelle die volle Frist gelaufen.

**Was hier nicht geprüft werden konnte:** der Abbruch **vor** dem
Belohnungspunkt. Googles Testvideo lässt sich per Zurück-Taste erst
schließen, nachdem die Belohnung gefallen ist — zwei Versuche endeten
beide mit `lief: true`. Der Zweig ist durch den Bau richtig (ohne
Reward-Ereignis bleibt `verdient` falsch, Dismissed beendet das Warten),
aber er ist **nicht am Gerät beobachtet**. Nachzuholen mit einem echten
Video von Hand.

**Punkt 14 — das späte Video riss die Lektion ab.** `showLevelHome()`
läuft jetzt nur noch, wenn der Bildschirm ohne Leben überhaupt noch steht.
Geprüft wird der Knopf **selbst**, nicht seine Kennung: nur wenn genau
dieser Knoten noch im Dokument hängt, ist es derselbe Schirm. Beide
Richtungen im Browser gemessen:

```
Schirm weg (Herz gekauft, neue Lektion):  showLevelHome 0 mal, Leben +1
Schirm steht noch:                        showLevelHome 1 mal, Leben +1
```

**Punkt 15 — das Einwilligungsfenster trotz Vollversion.** Wer zahlt, sieht
nie eine Anzeige. Ihn nach einer Einwilligung in eine Datenverarbeitung zu
fragen, die bei ihm nicht stattfindet, ist falsch. Die Prüfung gehört in
`einwilligungFragen()` und nicht in `admobStart()`: am PC gibt es das Plugin
gar nicht, und bei der versteckten Dauer-Vollversion steht `zmaj_voll` auf
`0` — in beiden Fällen griff der dortige Ausstieg nicht. Im Browser
gemessen, also genau auf dem Weg, der vorher durchrutschte:

```
ohne Vollversion, keine gespeicherte Antwort:  fragt = true   (richtig)
mit Vollversion:                               fragt = false
mit Dauer-Vollversion (zmaj_voll = "0"):       fragt = false
```

**Punkt 19 — npa=1 trotz Zustimmung.** `werbungAbgleichen()` hing an einer
einzigen Stelle: `showSettings()`. Wer die Einstellungen nie öffnet — und
das sind die meisten —, bekam dauerhaft unpersonalisierte Anzeigen, obwohl
er in Googles Fenster zugestimmt hatte. Das trifft auch Länder ohne DSGVO,
wo `ZmajEinwilligung.java` ausdrücklich `personalisiert: true` meldet — dort
ohne jeden rechtlichen Gegenwert, rein als Einnahmeverlust. Der Abgleich
läuft jetzt in `werbungVorbereiten()`, bevor die erste Anzeige kommen kann.

Auf dem S9 nach einem Kaltstart gemessen, **ohne die Einstellungen zu
öffnen**:

```
Googles Antwort:  {dsgvo:1, zweck1..4: true, google: true,
                   bekannt: true, personalisiert: true}
persWahl:                 true
werbungPersonalisiert():  true
Einstellungen je offen:   false
```

Vorher stand `persWahl` hier auf `null` und an jede Anzeige ging `npa=1`.
Dazu der Kommentar über AdMob berichtigt: er behauptete, die App setze npa
nicht mehr selbst — sie tut es an zwei Stellen, und das ist auch richtig so.

**Punkt 18 — die Diagnosedaten in der Datenschutzerklärung.** Das
Data-Safety-Formular kreuzt „App-Informationen und -Leistung / Diagnosedaten
/ Startzeit, Hänger, Energieverbrauch“ an; die Erklärung zählte nur vier
Dinge auf und nannte sie nicht. Google vergleicht beides miteinander. Jetzt
steht der Halbsatz in allen acht Sprachen, und `seite_bauen.py` hat ihn auf
die öffentliche Seite gebracht.

Die Begriffe sind nachgeschlagen statt geraten: Google Play nennt es auf
Schwedisch `starttid` und `batteriförbrukning`. Die sieben Übersetzungen
benutzen deshalb das Akku-Wort ihrer Sprache. Das Deutsche bleibt bei
„Energieverbrauch“ — so steht es im Formular, das abgeschickt wird.

Der zweite Teil des ursprünglichen Befundes — ein Widerspruch bei den
Zwecken „Analysen“ und „Betrugsprävention“ — hat der Gegenprüfung nicht
standgehalten und bleibt unangetastet: das sind Zwecke von Googles
Verarbeitung, und dafür verweist die Erklärung auf Googles eigene.

**Punkt 20 war schon behoben**, wie Punkt 12. `admob_scharf.py` tauscht
längst den ganzen Kommentarblock in `strings.xml` mit, nicht nur die
Kennung. Offen war nur der Zusatzbefund: `ANLEITUNG.md` führt dieselben
Testkennungen in einer Tabelle und wäre beim Tausch veraltet. Die Tabelle
steht jetzt mit in `admob_scharf.py` — und weil dessen Nachkontrolle jede
angefasste Datei darauf prüft, dass keine Testkennung mehr darin steht,
prüft sich die Änderung selbst. Probelauf:

```
ok   index.html     Testschalter aus
ok   index.html     Interstitial-Kennung
ok   index.html     Kennung fuer das belohnte Video
ok   ANLEITUNG.md   Kennungstabelle in der Anleitung
ok   strings.xml    App-Kennung in der Huelle
     Nachkontrollen bestanden.
```

Geschrieben wurde dort nichts: das Skript läuft erst nach der
Produktionsfreigabe.

**Punkt 17 — kein Ladehinweis, und prepare ohne Frist.** Wer auf
„Video ansehen“ tippte, bekam bis zum ersten Bild der Anzeige keine
Rückmeldung: der AdMob-Weg baut keine eigene Oberfläche, anders als der
Platzhalter am PC. Bei schwachem Netz sind das mehrere Sekunden, in denen
die App unbeteiligt aussieht — und genau das löst den zweiten Tipp aus,
also Punkt 9 und 13. Der Knopf schreibt sich jetzt auf „♥ Wird geladen …“
um und wird gesperrt; danach steht wieder „♥ Video ansehen“ da.

Zweitens hatte nur show eine Frist, prepare nicht. Das wiegt seit dem
Riegel schwerer: die Sicherheitsleine macht zwar nach 150 Sekunden wieder
auf, aber so lange soll niemand vor einem toten Knopf sitzen. Prepare
bekommt 15 Sekunden, und der Grund für einen Fehlschlag wird
mitgenommen statt verschluckt.

Auf dem S9 durchgespielt, Leben vorher auf 0:

```
vorher:   ♥ Video ansehen
während:  ♥ Wird geladen …      gesperrt: true
danach:   Leben 0 → 1, Riegel wieder auf, Schirm aufgeräumt
```

Der dritte Teil des Befundes — ein Kommentar, der eine Ladeanzeige
behauptete, die es nie gab — war schon beim Umbau für Punkt 11/16
verschwunden.

**Zur Knopfbreite:** der neue Text ist in allen acht Sprachen kürzer oder
gleich lang wie der alte („♥ Wird geladen …“ gegen „♥ Video ansehen“). Eine
eigene Messung auf 360 dp steht aus: der Schirm ohne Leben war in der
Sprachprüfung vom 29.09. nicht dabei, weil er sich nur mit leergespielten
Leben erreichen lässt.

**Punkt 8 — Abonnenten konnten ihre Einwilligung nicht widerrufen.** Wer
die Vollversion hat, fährt AdMob bewusst nicht hoch: während des Abos
findet keine Werbe-Datenverarbeitung statt, und das soll so bleiben. Nur —
eine früher als Gratisnutzer erteilte Einwilligung liegt weiter in Googles
Speicher auf dem Gerät. Art. 7 Abs. 3 DSGVO verlangt, dass sie sich so
leicht zurücknehmen lässt, wie sie gegeben wurde, und die
Datenschutzerklärung verspricht in acht Sprachen „jederzeit unter
Einstellungen → Werbung“. Für Abonnenten stimmte das nicht.

**Der naheliegende Ein-Zeilen-Fix wäre schlimmer als gar nichts gewesen**
— das hat die Gegenprüfung sauber herausgearbeitet. Streicht man nur das
`!unlimited()`, steht die Zeile zwar da, aber ohne `AdMobP` fände der
Schalter weder `admobDa()` noch `admobOptionen` und legte nur den lokalen
npa-Schalter um: eine Zeile, die so aussieht, als ändere sie die
Einwilligung, Googles gespeicherte Antwort aber nicht anfässt.

Gebaut ist deshalb Weg (b) aus der Gegenprüfung: eine **eigene Zeile** mit
eigenem Knopf, die Googles Auskunft **erst auf Tipp** nachlädt — ohne
`initialize()`. Das Werbe-SDK bleibt aus, beim Start spricht weiterhin
niemand mit Google, und der Einstiegspunkt ist trotzdem dauerhaft
erreichbar. `AdMobP` wird dabei bewusst **nicht** gesetzt: das würde
`admobDa()` umschalten und damit `einwilligungFragen()` und
`werbungErlaubt()` mitreißen — liefe das Abo in derselben Sitzung aus,
käme danach keine Anzeige mehr durch.

Auf Ajdins S21 gemessen, mit eingeschalteter Dauer-Vollversion:

```
Zeile: Werbung | Deine Antwort liegt bei Google. Hier kannst du sie
       ändern. | Wahl ändern
Werbeschalter daneben: ausgeblendet   (richtig, da gibt es nichts zu drehen)

requestConsentInfo():  status OBTAINED
                       isConsentFormAvailable true
                       privacyOptionsRequirementStatus REQUIRED
AdMobP danach: false   admobDa() danach: false
```

Googles Fenster ist also vorhanden und erreichbar, und das Werbe-SDK
bleibt dabei aus.

**Was nicht geprüft werden konnte:** das Öffnen des Fensters selbst. Beim
Versuch hatte sich das S21 gesperrt, und die PIN geht mich nichts an.
Nachzuholen mit entsperrtem Gerät — ein Tipp auf „Wahl ändern“ genügt.

Nebenbei gelernt: schlägt `requestConsentInfo()` mit „Error making
request.“ fehl, liegt das nicht am Netz, sondern daran, dass die Activity
nicht im Vordergrund ist — einmal mit heruntergezogener
Benachrichtigungsleiste gemessen, einmal ohne. Der Fehlerzweig zeigt
dafür eine kurze Meldung.

**Punkt 4 — die eigenen Geräte bekommen weiter Testanzeigen.** Im ganzen
Projekt kam `testingDevices` kein einziges Mal vor. Weil `isTesting` und
`initializeForTesting` beide am selben Schalter hingen, gäbe es nach dem
Umlegen auf die echten Kennungen keine Möglichkeit mehr, auf dem eigenen
Handy noch Testanzeigen zu sehen — jeder eigene Klick beim Nachtesten wäre
ungültiger Traffic auf dem eigenen Konto.

Die Gegenprüfung hatte den entscheidenden Zusatz: `testingDevices` allein
wirkt nicht. `AdMob.java:250-253` liest die Liste nur, wenn
`initializeForTesting` wahr ist. Deshalb hängt sie jetzt an „`ADMOB_TEST`
**oder** Liste nicht leer“. Für alle anderen Geräte ändert das nichts:
`setTestDeviceIds` (`AdMob.java:302`) betrifft genau die aufgezählten.

Die Kennung wurde am Gerät abgelesen, nicht geraten. Vorher meldete AdMob:

```
I/Ads: Use RequestConfiguration.Builder().setTestDeviceIds(
       Arrays.asList("41C694B849758EB6384F9FED5DD5FFAC"))
       to get test ads on this device.
```

Nach dem Eintragen, derselbe Aufruf auf demselben Gerät:

```
I/Ads: This request is sent from a test device.
```

Das ist der Beleg: die Liste kommt im SDK an. Sie überlebt auch
`admob_scharf.py`, weil `initializeForTesting` dann über die nicht leere
Liste wahr bleibt — der Probelauf des Skripts geht weiterhin durch.

Für die Messung musste die versteckte Dauer-Vollversion auf Ajdins S21
kurz aus, weil `admobStart()` sonst gar nicht erst hochfährt. Sie ist
danach wieder an, der Lernstand unverändert (77 Wörter, 5 Leben, derselbe
Zierrat).

**Noch offen:** Kübras Handy und das Galaxy S9 fehlen in der Liste. Beide
gehören hinein, **bevor** `admob_scharf.py` läuft — wie man die Kennung
abliest, steht als Anmerkung über der Liste im Quelltext.

**Punkt 6 — eine Änderung in Googles Fenster wirkte erst nach einem
Neustart.** Danach wurde nur `persWahl` neu gelesen; `admobDarf` und
`admobOptionen` blieben auf dem Wert vom Start. Zwei Wege liefen schief:

* **Widerruf** → `canRequestAds` wird false, die App fragte aber bis zum
  Neustart weiter Anzeigen an. Kein Datenschutzverstoß — `npa` wird bei
  jeder Anfrage frisch gerechnet —, aber ein Verstoß gegen Googles eigene
  Bedingung.
* **Zustimmung nach anfänglicher Ablehnung** → `admobDarf` blieb false und
  `initialize()` war nie gelaufen. Die Zustimmung blieb bis zum Neustart
  folgenlos: keine Werbung, kein belohntes Video. Schadet nur uns.

Neu ist `einwilligungNachziehen()`: holt die Auskunft frisch, setzt beide
Werte und holt `initialize()` nach, falls es noch nicht lief. Ein Merker
verhindert den zweiten Start. Auf dem S21 gemessen — der klebende Zustand
wurde nachgestellt:

```
vorher:        admobDarf true,  gestartet true,  Werbung erlaubt true
nachgestellt:  admobDarf false, gestartet false, Werbung erlaubt false
danach:        admobDarf true,  gestartet true,  Werbung erlaubt true
               nach 545 ms, ohne Neustart
```

**Punkt 7 — das eigene Fenster sprang für Googles UMP ein.** Kam UMP nicht
durch, zeigte die App ihren eigenen Einwilligungsdialog. Der ist kein
zertifiziertes CMP. Seine Antwort wurde dauerhaft gespeichert, landete über
`werbungPersonalisiert()` als `npa` an **echten** Anzeigenanfragen, und beim
nächsten Start mit Netz fragte UMP dieselbe Sache ein zweites Mal — derselbe
Nutzer zweimal befragt, und die erste Antwort galt der App als Einwilligung
nach Art. 6 Abs. 1 lit. a DSGVO.

Auf dem Gerät fragt jetzt ausschließlich Google. Kommt UMP nicht durch,
gibt es lieber keine Werbung; der nächste Start versucht es erneut, und
`zeigeWerbung()` fasst innerhalb einer Sitzung einmal nach. Das eigene
Fenster bleibt für die Browser-Fassung, wo es AdMob gar nicht gibt.

Dazu gehört eine zweite Änderung, sonst wäre die Reparatur nach hinten
losgegangen: ohne laufendes AdMob ist auf dem Gerät jetzt **gar keine
Werbung erlaubt**. Sonst stünde der Knopf „Video ansehen“ zwar da, liefe
aber jedes Mal ins Leere.

Beide Seiten gemessen:

```
Gerät, Plugin da, AdMob nicht hochgefahren:
    einwilligungFragen()  false   (eigenes Fenster springt nicht ein)
    werbungErlaubt(true)  false   (kein toter Knopf)
    werbungErlaubt(false) false

Browser, kein Plugin:
    einwilligungFragen()  true    (eigenes Fenster bleibt)
```

Teil C des Befundes — der zahlende Abonnent bekam das Fenster trotzdem —
war schon mit Punkt 15 erledigt.

---

## Stand am 29.09.2026

**Behoben: die drei kontogefährdenden Punkte 1, 2 und 3.** Alle drei am
Gerät gegengeprüft, Fassung 38.

**Punkt 1 — zwischen Laden und Zeigen.** Die Bedingung, unter der die
Anzeige angefordert wurde, steckt jetzt in `darfNoch()` und wird ein
zweites Mal geprüft, unmittelbar bevor die Anzeige auf den Schirm geht.
Dazwischen liegt `prepareInterstitial()`, ein Netzabruf von Sekunden.
Gemessen wurde mit Gegenprobe:

```
Lektion zu Ende, bei 1,4 s auf „Noch eine Lektion“ getippt:
    neue Lektion 0/12 steht, KEINE Anzeige, n bleibt 3, schuldig bleibt true
Dieselbe Lektion, NICHT getippt:
    Anzeige kommt, n 3 -> 4, schuldig wird false
```

Die geladene Anzeige geht dabei nicht verloren: `werbungSchuldig` trägt
sie in die nächste Lektion.

**Punkt 2 — der 1,2-Sekunden-Wecker.** Er steht jetzt in `werbungWecker`
und wird abgeräumt, sobald die App in den Hintergrund geht; `document.hidden`
gehört zusätzlich in die Bedingung, weil `sichtbar()` nur das CSS fragt.
Gemessen: Wecker gestellt, Home-Taste gedrückt, zurückgekommen —

```
in den Hintergrund: wecker=false schuldig=true
wieder da:          wecker=false schuldig=true      keine Anzeige, n unverändert
```

**Punkt 3 — die Schranke für Anzeigeninhalte.** `initialize()` bekommt
jetzt `maxAdContentRating: 'Teen'` mit. „Teen“ statt „General“, weil die
Zielgruppe laut `STORE_TEXTE.md` auf 16–17 und 18+ steht — so hatte es
schon die Gegenprüfung des Befunds richtiggestellt. AdMob kommt damit
sauber hoch (`admobDa()` wahr, kein Fehler); ein falscher Wert wäre beim
Start geflogen.

**Beobachtung vom 29.09., zu Punkt 1 und 17:** Nach einem Kaltstart kam
nach zwei Lektionen keine Anzeige. Auf eine von Hand angeforderte kam sie
nach etwa 14 Sekunden, und der Tageszähler sprang dabei von 0 auf 3 — die
beiden wartenden Anfragen lösten sich zusammen mit ihr auf.
`prepareInterstitial()` hat keine Frist, und die erste Anzeige ist
innerhalb des 1,2-Sekunden-Fensters noch nicht bereit. Dem Nutzer
schadet das nicht, es kostet Einblendungen.

---

## Stand am 28.09.2026

**Behoben: Punkt 5, Punkt 10 und Punkt 12.** Alle drei hängen zusammen.
Ohne Netz kam AdMob nicht hoch, und die App fiel auf den Platzhalter
zurück, der für den PC gedacht ist. Auf dem Gerät gibt es ihn jetzt nicht
mehr: Ist das AdMob-Plugin da, fällt die Anzeige aus (`fertig(false)`) —
ohne Kontingent und ohne Leben. Damit der Knopf dabei nicht kaputt
aussieht, kommt eine kurze Meldung — „Gerade gibt es keine Anzeige.
Versuch es später noch einmal.“ —, in allen acht Sprachen.

Gefunden hat das P8 am Gerät, im Flugmodus. Im Bericht standen die drei
Punkte seit dem 20.09. da, damals aus dem Quelltext hergeleitet. Die
Gegenprobe steht in `PRUEFPLAN.md` unter „P8 im Einzelnen“.

**Noch nicht abgehakt:** Die Punkte um die Anzeigenkette (11, 16, 17) sind
durch die Arbeit vom 27.09.2026 berührt — damals wurde der eigentliche
Grund behoben, dass auf `addListener` nicht gewartet wurde. Einzeln gegen
diese Liste geprüft sind sie noch nicht. Alle übrigen Punkte stehen
unverändert.

---

## 1. Zwischen dem Laden und dem Zeigen des Interstitials prueft niemand mehr, welcher Bildschirm gerade da ist

**Kontogefährdend** · Platzierung · `web/index.html:4655`

```
      if(Lx === dieseLektion && !wegmarkeLaeuft
         && sichtbar('levelView') && sichtbar('lesson')) zeigeWerbung(false, ()=>{});
```

**Was passiert:** Die Pruefung laeuft 1200 ms nach dem Ergebnisschirm. Danach geht es in admobZeigen() (Zeile 1406) zuerst in 'await AdMobP.prepareInterstitial(...)' - das ist ein Netzabruf und dauert je nach Verbindung ein bis mehrere Sekunden. Erst danach kommt showInterstitial() (Zeile 1410), und dazwischen wird nichts mehr geprueft. Konkret: Nutzer beendet die Lektion, bei 1,2 s faellt die Entscheidung 'Anzeige', bei 1,5 s tippt er auf 'Noch eine' (lMore, Zeile 4637), die neue Lektion startet, die erste Aufgabe steht da - und bei 3 s klappt das Interstitial ueber die laufende Aufgabe. Genau das, was der Kommentar in Zeile 4647 verhindern will, verhindert er nicht. Fuer Google ist das eine Anzeige mitten in einer Handlung bzw. direkt nach dem Laden eines Bildschirms - unzulaessige Implementierung, und genau die Kategorie, fuer die Konten gesperrt werden.

**Was zu tun ist:** admobZeigen() eine Pruefung mitgeben, die unmittelbar vor showInterstitial() noch einmal laeuft (z. B. ein Rueckruf 'darfNoch()' mit derselben Bedingung wie in Zeile 4655). Ist sie falsch, die geladene Anzeige verwerfen statt sie zu zeigen. Alternativ das Interstitial schon beim Lektionsstart im Voraus laden und in der setTimeout-Stelle nur noch zeigen, damit zwischen Pruefung und Anzeige keine Zeit mehr liegt.

**Einschränkung aus der Gegenprüfung:** Der Befund stimmt im Kern, ist aber an drei Stellen zu eng bzw. zu schneidig formuliert:

1. ZU ENG: Nicht nur "Noch eine" (lMore, 4637) ist betroffen. Derselbe Wettlauf gilt fuer "Zurueck" (lHome, 4636 -> showLevelHome, 4099-4101, setzt lesson auf display:none). Wer nach 1,2 s zurueckgeht, bekommt die Anzeige ueber dem Lernpfad. Genau der erste Fall, den der Kommentar in 4645-4648 nennt. Das Loch ist also breiter als beschrieben.

2. PRAEZISER: `sichtbar('levelView') && sichtbar('lesson')` (5006: `return !!e && e.style.display !== 'none'`) unterscheidet den Ergebnisschirm gar nicht von einer laufenden Aufgabe - beides liegt im selben Feld 'lesson'. Die einzige Unterscheidung leistet `Lx === dieseLektion` (Lx wird in 4470 fuer jede neue Lektion neu gesetzt), und genau diese Pruefung wird nach dem await in 1406 nicht wiederholt.

3. ZU SCHNEIDIG: Die Angabe "ein bis mehrere Sekunden" ist am Code nicht messbar. Belegbar ist nur, dass prepareInterstitial (1406) - anders als der belohnte Pfad mit seinem 120-s-Rennen in 1397 - ueberhaupt keine Frist hat und das Fenster daher unbestimmt lang ist. Es bleibt ein Wettlauf, der nicht jeden Nutzer trifft, sondern den, der in diesem Fenster tippt. Die Einstufung "kontogefaehrdend" ist vertretbar, aber sie ist der am schwaechsten belegte Teil; der Mechanismus selbst ist eindeutig belegt.

---

## 2. Der 1,2-Sekunden-Wecker laeuft weiter, wenn die App in den Hintergrund geht - die Anzeige kommt dann beim Zurueckkommen

**Kontogefährdend** · Platzierung · `web/index.html:4657`

```
    }, 1200);
```

**Was passiert:** Das setTimeout wird nirgends abgebrochen, und sichtbar() prueft nur CSS: 'function sichtbar(id){ const e = $(id); return !!e && e.style.display !== "none"; }' (Zeile 5006). Ob das Fenster ueberhaupt noch vorne ist, fragt niemand - der visibilitychange-Horcher (Zeile 2439) stoppt nur Uhr und Ton. Konkret: Nutzer beendet die Lektion und drueckt sofort Home, oder ein Anruf kommt rein. Bei 1,2 s laeuft der Wecker trotzdem los, die Anzeige wird geladen und gezeigt - der Nutzer bekommt sie beim naechsten Oeffnen der App zu sehen, ohne etwas getan zu haben. Google verbietet beides ausdruecklich: Anzeigen beim Verlassen der App und Anzeigen beim App-Start/Fortsetzen ohne Nutzerhandlung.

**Was zu tun ist:** Den Wecker in einer Variablen halten und bei 'document.hidden' in Zeile 2440 mit clearTimeout abraeumen. Zusaetzlich in die Bedingung von Zeile 4655 '&& !document.hidden' aufnehmen und dieselbe Pruefung direkt vor showInterstitial() wiederholen.

**Einschränkung aus der Gegenprüfung:** Zwei Praezisierungen, die den Befund nicht umstossen, aber sein Bild schaerfen:

(a) Der genaue sichtbare Ausgang laesst sich aus dem Code nicht beweisen. Ob die Anzeige im Hintergrund sofort ueber Home-Bildschirm/Anruf erscheint oder erst beim Zurueckkommen, entscheidet Android: seit Android 10 duerfen Apps aus dem Hintergrund keine Activity mehr starten, und die AdMob-Anzeige ist eine Activity. Moeglich sind also drei Ausgaenge - Anzeige beim Zurueckkommen (der vom Befund genannte und wahrscheinlichste Fall, weil die App Sekundenbruchteile vorher noch vorne war), stillschweigendes Scheitern, oder Anzeige ueber der fremden Oberflaeche. Die Formulierung "wird geladen und gezeigt" ist damit eine plausible, aber nicht am Code belegbare Prognose. Der Defekt selbst - ein Anzeigenaufruf ohne jede Pruefung, ob die App noch vorne ist - ist dagegen eindeutig belegt, und der wahrscheinlichste Ausgang ist zugleich der, den Google verbietet.

(b) Das Zeitfenster ist eng: es trifft nur, wer innerhalb von 1,2 Sekunden nach dem Ergebnisschirm die App verlaesst, oder wen in dieser Spanne ein Anruf erwischt. Das mindert die Haeufigkeit, nicht die Schwere - bei sechs Anzeigen taeglich ueber die ganze Nutzerschaft reicht ein Bruchteil fuer eine Beschwerde. Die Einstufung "kontogefaehrdend" bleibt richtig.

---

## 3. Es wird keine maxAdContentRating gesetzt - in einer App mit Inhaltseinstufung USK 0 / PEGI 3 darf AdMob damit Anzeigen bis MatureAudience ausliefern

**Kontogefährdend** · Zielgruppe · `C:\Users\Ajdin\Desktop\Bosnisch Lernapp\web\index.html:1371`

```
    if(admobDarf) await A.initialize({initializeForTesting: ADMOB_TEST});
```

**Was passiert:** initialize() bekommt nur initializeForTesting. Das Plugin @capacitor-community/admob 8.1.0 kennt maxAdContentRating (node_modules/@capacitor-community/admob/dist/esm/definitions.d.ts, Enum General/ParentalGuidance/Teen/MatureAudience), aber es wird nicht uebergeben, und auch nativ setzt nichts eine RequestConfiguration (kein Treffer in android/app/src/main/java/ und im AndroidManifest.xml). Damit gilt allein die Voreinstellung im AdMob-Konto, die nirgends im Projekt dokumentiert ist. STORE_TEXTE.md:1169 legt die Inhaltseinstufung aber auf USK 0 / PEGI 3 fest, mit ausdruecklich Nein bei Gluecksspiel, Drogen, Sexualitaet, Gewalt. Google Play verlangt, dass die ausgelieferten Anzeigen zur Inhaltseinstufung der App passen und dass man die Anzeigenfilter entsprechend setzt (Play Console Hilfe 9859655). Eine Wett-, Alkohol- oder Dating-Anzeige in einer mit PEGI 3 eingestuften Lern-App ist genau der Fall, den Google dort beschreibt - das trifft die App und das AdMob-Konto gleichzeitig. Weil ADMOB_TEST heute true ist, faellt es im Test nicht auf: Googles Testanzeigen sind immer harmlos. Sichtbar wird es erst mit den echten Kennungen.

**Was zu tun ist:** In admobStart() mitgeben: A.initialize({initializeForTesting: ADMOB_TEST, maxAdContentRating: 'General'}). 'General' passt zu USK 0 / PEGI 3. Soll es hoeher sein (z. B. 'Teen', weil die Zielgruppe 16+ ist), dann muss vorher die Inhaltseinstufung in der Play Console dazu passen - nicht umgekehrt. Danach app_bauen.py laufen lassen, sonst steht in android/app/src/main/assets/public/index.html weiter die alte Fassung (beide Dateien sind heute byteweise identisch).

**Einschränkung aus der Gegenprüfung:** Richtig ist: web/index.html:1371 uebergibt maxAdContentRating nicht, und nirgends im Projekt wird es nachgeholt — damit entscheidet allein die undokumentierte Kontoeinstellung. Falsch sind drei Punkte des Befunds.

1. Nativ wird sehr wohl eine RequestConfiguration gesetzt, naemlich vom Plugin selbst (AdMob.java:94 ruft setRequestConfiguration, ab Zeile 248 wird sie gebaut und per MobileAds.setRequestConfiguration angewandt) — nur eben mit MAX_AD_CONTENT_RATING_UNSPECIFIED, weil der Schluessel fehlt. Es fehlt also kein nativer Code, sondern ein Wort in Zeile 1371.

2. Die Zielgruppe ist laut STORE_TEXTE.md:64 auf 16-17 und 18+ festgelegt, nicht auf Kinder. Die passende Schranke ist deshalb "Teen", nicht "General". Die Zuspitzung "PEGI-3-Lern-App bekommt Dating-Anzeigen" traegt nicht, weil Inhaltseinstufung und Zielgruppenangabe zwei verschiedene Felder sind.

3. Schwere ist nicht "kontogefaehrdend", sondern "sollte vor dem Scharfschalten rein". Ein Verstoss ist am Code nicht nachweisbar, weil das Ergebnis von der AdMob-Kontoeinstellung abhaengt.

Konkrete Behebung, ein Zeileneingriff in web/index.html:1371:
  if(admobDarf) await A.initialize({initializeForTesting: ADMOB_TEST, maxAdContentRating: 'Teen'});
Sinnvoll waere, das zusammen mit den echten Kennungen in admob_scharf.py mitzufuehren, damit Quelle und Huelle nicht auseinanderlaufen.

---

## 4. Kein testingDevices: nach dem Tausch bekommen die eigenen Geraete echte Anzeigen

**Schwer** · Kennungen · `C:\Users\Ajdin\Desktop\Bosnisch Lernapp\web\index.html:1371`

```
    if(admobDarf) await A.initialize({initializeForTesting: ADMOB_TEST});
```

**Was passiert:** Im ganzen Projekt und in der ganzen Huelle kommt testDeviceIds / testingDevices kein einziges Mal vor. Das Plugin kann es (node_modules/@capacitor-community/admob/dist/esm/definitions.d.ts:57 'testingDevices?: string[]'). Weil isTesting und initializeForTesting beide am selben Schalter ADMOB_TEST haengen, gibt es nach dem Umlegen auf false keine Moeglichkeit mehr, auf dem eigenen Handy noch Testanzeigen zu bekommen. Jede Anzeige, die Ajdin oder Kuebra beim Nachtesten sieht oder antippt, ist ungueltiger Traffic auf dem eigenen Konto - genau das Risiko, vor dem admob_scharf.py in seinem eigenen Vorspann warnt. Der versteckte Dauer-Schalter fuer die Vollversion schuetzt nicht zuverlaessig: er haengt an localStorage (vollversionGemerkt, web/index.html:3034) und ist nach einer Neuinstallation weg.

**Was zu tun ist:** Eine eigene Konstante ADMOB_TESTGERAETE mit den AdMob-Geraete-IDs der beiden Handys einfuehren und sie unabhaengig von ADMOB_TEST mitgeben: A.initialize({initializeForTesting: ADMOB_TEST || ADMOB_TESTGERAETE.length > 0, testingDevices: ADMOB_TESTGERAETE}). Die IDs stehen nach dem ersten Start im Logcat.

**Einschränkung aus der Gegenprüfung:** Vier Praezisierungen. (a) Die naheliegende Reparatur reicht nicht: testingDevices allein wirkt nicht, weil AdMob.java:250-252 die Liste nur liest, wenn initializeForTesting true ist (iOS ebenso, AdMobPlugin.swift:303). Noetig ist also initializeForTesting: true DAUERHAFT (entkoppelt von ADMOB_TEST) plus die eigenen Geraete-IDs, bei echten Anzeigenbloecken und isTesting: false. (b) 'Jede Anzeige, die sie sieht oder antippt, ist ungueltiger Traffic' ist zu scharf - der klare Verstoss ist der eigene Klick, eine blosse Einblendung auf dem eigenen Geraet ist riskant, aber nicht automatisch dasselbe. (c) Der Dauer-Schalter schuetzt im laufenden Betrieb besser als behauptet: werbungErlaubt() (:1302) bricht ueber unlimited() (:2473) ab, sobald premium steht, und dauerVoll sticht premium (:2110, :2151) - solange zmaj_dauer gesetzt ist, wird keine einzige Anzeige angefordert. Dafuer ist eine andere Stelle kaputt, die der Befund nicht nennt: der fruehe Ausstieg in admobStart() (:1356) prueft nur vollversionGemerkt(), und das liest ausschliesslich zmaj_voll (:3034-3036), nicht zmaj_dauer - entgegen dem Kommentar in :1351-1355 faehrt das SDK fuer Ajdin und Kuebra also trotzdem hoch, es fordert nur nichts an. (d) Schwere eher 'mittel' statt 'schwer': das Risikofenster ist die Zeit nach einer Neuinstallation bis zu den sieben Tipps auf die Versionszeile, die automatische Anzeige kommt fruehestens nach der dritten Lektion (WERBUNG_AB_LEKTION = 3, :1204) und das belohnte Video nur auf ausdrueckliches Antippen.

---

## 5. Scheitert Googles Einwilligungsabfrage (offline), zeigt die ausgelieferte App den Platzhalter-Kasten als echte Werbung

**Schwer** · Einwilligung · `web/index.html:1372`

```
}catch(e){ AdMobP = null; admobDarf = false; }
```

**Was passiert:** requestConsentInfo() braucht Netz. Ohne Netz wirft es, der catch setzt AdMobP auf null. Damit ist admobDa() false, einwilligungFragen() (Z. 1247-1250) liefert true, die App zeigt ihr eigenes Fenster, speichert die Antwort - und ab da ist werbungErlaubt() (Z. 1300-1307) wahr. In zeigeWerbung() greift dann der Zweig ab Z. 4518 nicht mehr, und die App baut ab Z. 4524 den Platzhalter-Kasten mit 'werbung.marke' und Countdown auf. Der Nutzer sieht in der veroeffentlichten App eine vorgetaeuschte Anzeige, und werbungFuerLeben() (Z. 4562) schenkt ihm dafuer ein Leben. Das Tageskontingent wird ebenfalls verbraucht.

**Was zu tun ist:** Den Platzhalter an WERBUNG_ECHT koppeln: laeuft ein echtes Netzwerk, darf zeigeWerbung() nie auf den Kasten zurueckfallen, sondern muss fertig(false) melden. Zusaetzlich admobStart() bei einem Fehler spaeter erneut versuchen (z. B. beim naechsten Vordergrund-Wechsel), statt endgueltig aufzugeben.

**Einschränkung aus der Gegenprüfung:** Zwei Punkte der Folgenbeschreibung sind ueberzogen bzw. falsch gewichtet:

a) "Vorgetaeuschte Anzeige" ist zu stark. Der Kasten zeigt laut sprachen.py:523-524 die Texte "Anzeige" und "Hier erscheint die Werbung." (englisch 952-953 "Advertisement" / "The ad appears here."). Der Nutzer sieht also keinen erfundenen Werbeinhalt, sondern einen leeren, als Platzhalter erkennbaren Rahmen. Unfertig und peinlich in einer veroeffentlichten App - aber keine gefaelschte Anzeige.

b) Der eigentliche Schaden liegt nicht beim belohnten Video, sondern beim Interstitial. werbungFuerLeben() (4562) verschenkt ein Leben, das ist fuer den Nutzer ein Gewinn, kein Nachteil. Weh tut Zeile 4656: nach jeder dritten Lektion wird zeigeWerbung(false, ...) aufgerufen, und der Nutzer muss dann fuenf Sekunden (4536-4545) vor einem leeren Kasten warten, mit einem "Werbung ohne"-Knopf zur Vollversion daneben, obwohl gar keine Werbung laeuft. Das Tageskontingent (WERBUNG_MAX_TAG = 6, Zeile 1206) wird dabei in 4523 verbraucht, bevor der Kasten ueberhaupt steht.

c) Praezisierung des Ausloesers: Es braucht nicht zwingend das eigene Einwilligungsfenster. Hat der Nutzer es einmal beantwortet, ist einwilligungGueltig() dauerhaft wahr, und jeder spaetere Start ohne Netz geht ohne jede Rueckfrage direkt in den Platzhalter.

---

## 6. Aenderung oder Widerruf in Googles Fenster wirkt erst nach einem Neustart der App

**Schwer** · Einwilligung · `web/index.html:2023`

```
    try{ await AdMobP.showPrivacyOptionsForm(); }catch(e){}
```

**Was passiert:** Nach dem Schliessen von Googles Fenster wird nur googlesAntwort() gelesen und persWahl gesetzt. admobDarf bleibt auf dem Wert vom Start (Z. 1369). Widerruft jemand so, dass canRequestAds false wird, zeigt die App bis zum Neustart weiter Anzeigen. Umgekehrt gilt dasselbe: wurde beim Start abgelehnt, ist admobDarf false und initialize() wurde nie aufgerufen (Z. 1371, 'if(admobDarf) await A.initialize(...)'). Stimmt der Nutzer danach im Datenschutzfenster zu, bleibt admobDarf false und das SDK ungestartet - die Zustimmung bleibt bis zum naechsten Start folgenlos.

**Was zu tun ist:** Nach showPrivacyOptionsForm() erneut requestConsentInfo() aufrufen, admobDarf und admobOptionen daraus neu setzen und initialize() nachholen, falls es noch nicht lief (einmaliges Flag, damit es nicht doppelt startet).

**Einschränkung aus der Gegenprüfung:** Mechanik stimmt, zwei Punkte der Folgenbeschreibung sind zu scharf:

a) "zeigt die App bis zum Neustart weiter Anzeigen" - richtig, aber es sind unpersonalisierte. `npa` wird bei JEDER Anzeige neu aus `werbungPersonalisiert()` berechnet (:1397 und :1407), und `persWahl` wird direkt nach dem Fenster aus Googles frischem TCF-Speicher nachgezogen (:2024-2025 über ZmajEinwilligung.java, das IABTCF_PurposeConsents 1/3/4 und Anbieter 755 liest). Es läuft nach einem Widerruf also kein personalisiertes Tracking weiter; es werden nur weiter Anzeigen angefragt, obwohl Googles Vertrag (canRequestAds=false) das verbietet. Das ist ein AdMob-Richtlinien-/Umsetzungsfehler, kein laufender DSGVO-Verstoß. Schwere daher eher "mittel" als "schwer".

b) Die Rückrichtung (beim Start abgelehnt, danach im Datenschutzfenster zugestimmt) stimmt exakt so wie beschrieben und ist erreichbar (:3612-3614), schadet aber nur euch selbst: bis zum Neustart keine Werbung und kein belohntes Video, also fehlende Einnahmen und ein Leben weniger zurückzuholen - kein Nutzerschaden.

c) Nebenbefund, der die Ursache erklärt: die Kommentare :1971-1975 und ZmajEinwilligung.java:16-19 behaupten, canRequestAds sei "in beiden Faellen wahr". Nach Googles Doku stimmt das nur, wenn in der AdMob-Konsole "limited ads" für Ablehner eingeschaltet ist; sonst ist der Wert nach "Nicht zustimmen" false. Auf diese Annahme darf man sich nicht verlassen.

Behebung: im Klickpfad nach Zeile 2023 `requestConsentInfo()` erneut aufrufen, `admobDarf` und `admobOptionen` neu setzen und, falls `initialize()` noch nie lief, es jetzt nachholen (mit einem Merker gegen doppelte Initialisierung).

---

## 7. Faellt AdMob aus, springt ein selbstgebautes Fenster ein, das kein zertifiziertes CMP ist - und der Nutzer wird spaeter ein zweites Mal gefragt

**Schwer** · Einwilligung · `web/index.html:1249`

```
  return (WERBUNG_ECHT || EINWILLIGUNG_TEST) && !einwilligungGueltig();
```

**Was passiert:** zeigeEinwilligung() (Z. 1273) ist ein eigener Dialog ohne TCF-Anbindung. Er erscheint immer dann, wenn admobDa() false ist, obwohl WERBUNG_ECHT true ist - also genau in den Faellen, in denen Googles UMP nicht durchkam. Die Antwort wird mit EINWILLIGUNG_STAND = 1 dauerhaft gespeichert (Z. 1266-1271) und nie wieder erfragt. Beim naechsten Start mit Netz zeigt Googles UMP sein Fenster: derselbe Nutzer wird zweimal zur selben Sache befragt, und die erste Antwort haelt die App fuer eine gueltige Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO, obwohl sie ueber kein zertifiziertes CMP eingeholt wurde.

**Was zu tun ist:** Sobald WERBUNG_ECHT true ist und das AdMob-Plugin vorhanden ist, das eigene Fenster gar nicht mehr anbieten. Kommt UMP nicht durch, lieber keine Werbung zeigen und es spaeter erneut versuchen. Das eigene Fenster nur noch fuer die Browser-Fassung ohne Plugin behalten.

**Einschränkung aus der Gegenprüfung:** Der Befund haelt stand. Drei Praezisierungen, eine davon macht ihn schlimmer:

A) Zeilenangaben leicht daneben. zeigeEinwilligung() beginnt bei Z. 1276, nicht 1273 (1273-1275 ist der Kommentar davor). einwilligungMerken() steht in Z. 1269-1272, nicht 1266-1271. Die Belegzeile 1249 stimmt woertlich.

B) Die Schadenskette laeuft anders, als der Befund sie beschreibt - und weiter. Solange AdMobP null ist, geht ueberhaupt keine Anzeige raus (admobZeigen bricht in Z. 1393 mit `if(!AdMobP || !admobDarf) return false;` ab). In dem Moment verlaesst also kein Datum das Geraet, "ungueltige Einwilligung" trifft es da noch nicht. Der Schaden faellt spaeter an: werbungPersonalisiert() (Z. 1261-1264) liefert `einwilligungGueltig() && einwilligung.wahl === 'ja'`, und genau das setzt den npa-Schalter auf den ECHTEN AdMob-Anfragen in Z. 1397 und Z. 1407 (`npa: !werbungPersonalisiert()`). Heisst: hat der Nutzer im Eigenbau-Fenster "ja" gedrueckt, werden ab dem naechsten Start personalisierte Anzeigen angefordert - auf Grundlage einer Antwort, die nie durch ein CMP gelaufen ist. Die Korrektur aus Googles echten TCF-Daten gibt es zwar (googlesAntwort() ueber das eigene Plugin ZmajEinwilligung), sie laeuft aber nur in werbungAbgleichen(), und das wird ausschliesslich beim Oeffnen der Einstellungen aufgerufen (Z. 3615). Wer nie in die Einstellungen geht, sendet dauerhaft npa aus der nicht-zertifizierten Quelle, im Widerspruch zum TC-String, den Googles SDK daneben fuehrt.

C) Dieselbe Zeile 1249 hat noch einen zweiten, im Befund nicht genannten Fehler: admobStart() steigt in Z. 1354 bei `if(vollversionGemerkt()) return;` vorzeitig aus. AdMobP bleibt dann null, admobDa() ist false, und weil einwilligungFragen() - anders als werbungErlaubt() in Z. 1302 - kein unlimited() prueft, bekommt ein zahlender Abonnent beim Start das Werbe-Einwilligungsfenster vorgesetzt, obwohl er nie eine Anzeige sehen wird.

Die eigentliche Ursache in einem Satz: `admobDa()` wird als "laeuft auf dem Handy, Google hat gefragt" gelesen, unterscheidet aber drei Zustaende nicht - PC-Browser ohne Plugin (Eigenbau ist dort richtig), Vollversion (gar nicht fragen), und UMP gescheitert (Eigenbau ist dort falsch, es muesste ein Wiederholungsversuch statt einer dauerhaft gespeicherten Antwort sein).

---

## 8. Abonnenten der Vollversion haben keinen Weg mehr, eine frueher erteilte Einwilligung zu widerrufen

**Schwer** · Einwilligung · `web/index.html:3612`

```
  const zeigen = !unlimited()
```

**Was passiert:** Mit aktiver Vollversion wird die Zeile 'Werbung' in den Einstellungen ausgeblendet (Z. 3614). Wer vorher als Gratisnutzer bei Google zugestimmt hat, hat diese Einwilligung weiterhin im UMP-Speicher liegen, kommt aber nicht mehr an Googles Datenschutzfenster heran. Google verlangt fuer den EWR einen dauerhaft erreichbaren Einstiegspunkt, solange privacyOptionsRequirementStatus REQUIRED ist. Ausserdem verspricht die Datenschutzerklaerung ausdruecklich 'du kannst sie jederzeit unter Einstellungen -> Werbung aendern' (sprachen.py:522, gleichlautend in github-seite/datenschutz.html:44) - das stimmt fuer Abonnenten nicht.

**Was zu tun ist:** Die Zeile auch bei aktiver Vollversion zeigen, sobald admobOptionen true ist oder eine Einwilligung gespeichert wurde - mit dem Untertext, dass gerade keine Werbung laeuft. Dafuer muss admobStart() bei Premium wenigstens requestConsentInfo() aufrufen duerfen, oder der Einstiegspunkt muss ueber ZmajEinwilligung/UMP unabhaengig vom Werbe-SDK erreichbar bleiben.

**Einschränkung aus der Gegenprüfung:** Die Ursachenkette im Befund ist unvollstaendig, und der naheliegende Ein-Zeilen-Fix wuerde nicht wirken.

web/index.html:1348-1372, admobStart():
  if(vollversionGemerkt()) return;   // Zeile 1356
Bei aktiver Vollversion faehrt AdMob gar nicht erst hoch. Damit bleibt AdMobP null, admobDa() ist false (Z. 1345) und admobOptionen false (Z. 1343, gesetzt erst in Z. 1370). Folge: Selbst wenn man das !unlimited() in Zeile 3612 streicht, waere die Zeile zwar sichtbar - der Klick-Handler (Z. 2021) faende admobDa() && admobOptionen aber false und wuerde in Z. 2029-2030 nur den lokalen npa-Schalter umlegen. Googles Datenschutzfenster kaeme nie. Der Abonnent haette dann eine Zeile, die so aussieht, als koennte sie die Einwilligung aendern, aber Googles gespeicherte TCF-Antwort nicht anfasst - das waere schlimmer als gar keine Zeile.

Ein tragfaehiger Fix braucht deshalb zwei Aenderungen: (a) fuer Abonnenten requestConsentInfo() trotzdem laufen lassen, um privacyOptionsRequirementStatus zu erfahren und AdMobP fuer showPrivacyOptionsForm() verfuegbar zu haben, ohne A.initialize() aufzurufen (Z. 1371 bleibt hinter admobDarf und muesste zusaetzlich hinter !premium), oder (b) die Zeile fuer Abonnenten auf einen reinen 'Einwilligung bei Google aendern'-Knopf umstellen, der genau dafuer die Consent-Info nachlaedt.

Kleinere Praezisierung zur Schwere: Zeile 1356 ist bewusst so gebaut ('fuer jemanden, der genau dafuer bezahlt hat, waere das verkehrt', Kommentar Z. 1351-1355) und ist datenschutzrechtlich fuer sich genommen richtig - es findet waehrend des Abos keine Werbe-Datenverarbeitung statt. Der belastbare Kern des Befunds ist daher nicht 'Google wird die App ablehnen' (die automatische Pruefung sieht diesen Fall nicht), sondern: die Einwilligung liegt weiter im UMP-Speicher des Geraets, ist ohne App-Daten-Loeschen nicht widerrufbar (Art. 7 Abs. 3 DSGVO), und die Datenschutzerklaerung behauptet in acht Sprachen und auf der Webseite das Gegenteil. Das allein reicht als Mangel aus.

---

## 9. Kein Schutz gegen Doppeltippen auf 'Video ansehen' - zwei Videos hintereinander und zwei Leben fuer eins

**Schwer** · Platzierung · `web/index.html:4605`

```
  if($('lAd')) $('lAd').addEventListener('click', werbungFuerLeben);
```

**Was passiert:** Der Knopf wird beim Antippen nicht gesperrt, und zeigeWerbung() (Zeile 4512) hat keine Wiedereintritts-Sperre. werbungFuerLeben() geht ueber admobZeigen(true) in 'await AdMobP.prepareRewardVideoAd(...)' (Zeile 1396) - waehrend dieses Ladens bleibt der Knopf sichtbar und anklickbar. Zwei schnelle Tipps starten also zwei Ladevorgaenge und zwei showRewardVideoAd()-Aufrufe. Folge 1: zwei Anzeigen unmittelbar hintereinander, was Google als Haeufung untersagt. Folge 2: jeder der beiden Rueckrufe in Zeile 4565 rechnet ein Leben dazu ('lives.anzahl + WERBUNG_LEBEN_LOHN'), also zwei Leben fuer ein angesehenes Video. Dasselbe gilt fuer das Interstitial, dort faellt es nur nicht auf, weil es keinen Knopf gibt.

**Was zu tun ist:** In zeigeWerbung() ganz oben ein Modul-Flag 'werbungLaeuft' setzen und bei gesetztem Flag sofort mit fertig(false) zurueckkehren; zurueckgesetzt wird es in jedem Ausgang (AdMob-Rueckruf, Platzhalter-schliessen, Fehlerzweig). Zusaetzlich in werbungFuerLeben() den Knopf 'lAd' beim ersten Tipp auf disabled setzen.

**Einschränkung aus der Gegenprüfung:** Drei Teile der Folgenbeschreibung sind zu streichen oder abzuschwaechen. 1) "Zwei Leben fuer EIN angesehenes Video" ist nicht belegbar: AdRewardExecutor.java (node_modules/@capacitor-community/admob/android/...) haelt preparedAds je Anzeigen-Kennung, das zweite prepare ueberschreibt den Eintrag, und RewardedAdCallbackAndListeners.kt loest jede Zusage nur ueber ihren eigenen OnUserEarnedRewardListener auf. Belegbar ist nur: zwei ueberlappende Ladevorgaenge und zwei showRewardVideoAd()-Aufrufe, und die Gutschrift ohne Einmal-Marke. Realistisch ist entweder zwei Videos -> zwei Leben (doppelt gegen das Tageskontingent gezaehlt, aber nicht erschlichen) oder der zweite show() laeuft ins Leere und die Zusage faellt erst nach dem 120-Sekunden-Rennen in web/index.html:1402 als null zurueck, also gar kein zweites Leben. 2) Das Interstitial ist nicht betroffen: web/index.html:4649-4657 loest genau einmal je Lektion aus, mit Waechter "Lx === dieseLektion", es gibt keinen Knopf und keinen zweiten Einstieg. 3) Die Richtlinienbehauptung ("Google untersagt Haeufung") laesst sich am Code nicht pruefen und traegt den Befund nicht. Das Gewicht liegt beim fehlenden Doppeltipp-Schutz und der nicht idempotenten Lebensgutschrift; angemessene Schwere eher mittel als schwer. Fix analog zu Zeile 3177: ein Modul-Flag plus disabled auf dem lAd-Knopf.

---

## 10. Auf dem Handy kann die Belohnung fuer einen Platzhalter vergeben werden, ohne dass je ein Video lief

**Schwer** · Platzierung · `web/index.html:4522`

```
  werbungGezaehlt();
```

**Was passiert:** Ist admobDa() falsch (Zeile 4518 trifft nicht zu), baut zeigeWerbung() den Attrappen-Kasten mit der Marke 'Anzeige' und dem Text 'Hier erscheint die Werbung.' (Zeilen 4524-4534) und vergibt nach fuenf Sekunden ueber schliessen(true) in Zeile 4556 das Leben. Auf dem Geraet tritt genau das in drei belegbaren Faellen ein: (a) admobStart() faellt in den Fehlerzweig 'catch(e){ AdMobP = null; admobDarf = false; }' (Zeile 1372), (b) admobStart() bricht bei aktiver Vollversion sofort ab ('if(vollversionGemerkt()) return;', Zeile 1356) und vollAbgleichen() stellt spaeter in derselben Sitzung fest, dass das Abo nicht mehr laeuft (Zeile 3082 setzt premium auf false) - AdMobP bleibt dann fuer den Rest der Sitzung null, (c) WERBUNG_ECHT ist false. In allen drei Faellen sieht ein Nutzer in einer veroeffentlichten App einen als 'Anzeige' beschrifteten Kasten, der keine ist, und bekommt Leben dafuer. Zusaetzlich verbraucht dieser Platzhalter ueber werbungGezaehlt() das Tageskontingent echter Anzeigen.

**Was zu tun ist:** Auf Capacitor (window.Capacitor?.Plugins vorhanden) den Platzhalter gar nicht mehr bauen: laeuft AdMob nicht, mit fertig(false) zurueckkehren und den Knopf 'Video ansehen' erst gar nicht anbieten. Den Platzhalter nur noch in der Browser-Fassung zulassen.

**Einschränkung aus der Gegenprüfung:** Drei Punkte des Befunds stimmen nicht. (1) Fall (c) 'WERBUNG_ECHT ist false' tritt in der ausgelieferten App nicht ein: sprachen.py:88 WERBUNG_LAEUFT = True, start.py:180 reicht es als werbung_laeuft durch, und alle mitgelieferten Daten (zmaj-android/.../assets/public/inhalt/de.json usw.) enthalten "werbung_laeuft":true, also ist WERBUNG_ECHT (gesetzt in web/index.html:2930) auf dem Geraet true. (2) Fall (b) ist ein Wettlauf, keine Gewissheit: init() (ca. 4863-4867) ruft vollAbgleichen() VOR 'await vorspannVorbei; werbungVorbereiten();'. vollversionMerken() (2104-2110) schreibt zmaj_voll='0', meist bevor admobStart() in 1356 vollversionGemerkt() liest - dann startet AdMob normal. Nur wenn Play Billing langsamer antwortet als der Vorspann, bleibt AdMobP null, dafuer dann dauerhaft. (3) Eine Vorbedingung fehlt und 4556 ist kein Timer: bei WERBUNG_ECHT=true und AdMobP=null sperrt werbungErlaubt() (1301-1304) ueber einwilligungFragen() (1247) zunaechst jede Werbung; erst nachdem werbungVorbereiten() in 4850 das eigene Einwilligungsfenster gezeigt und der Nutzer geantwortet hat, erscheint der Platzhalter. Und das Leben faellt nicht automatisch nach fuenf Sekunden, sondern erst beim Tippen auf den ab 4544 freigegebenen Knopf.

---

## 11. Der 120-Sekunden-Ablauf wirft eine tatsaechlich verdiente Belohnung weg: Video gesehen, kein Leben

**Schwer** · Fehlerfall · `web/index.html:1403`

```
                                       new Promise(f => setTimeout(()=>f(null), 120000))]);
```

**Was passiert:** Das ist die direkte Antwort auf die Frage nach dem Zeitablauf: es laeuft NICHTS doppelt - es geht etwas verloren. Greift die Frist, loest Promise.race mit null auf, admobZeigen gibt false zurueck, werbungFuerLeben bricht in Zeile 4564 wortlos ab. Kommt die Belohnung danach doch noch (call.resolve im Plugin), ist das Rennen laengst entschieden; der Wert faellt ersatzlos unter den Tisch. Der Nutzer hat das komplette Video angesehen und steht ohne Leben da - also schlechter als ohne Werbung, denn ohne Werbung haette er die zwei Minuten nicht verschenkt. Erreichbar ist das leicht: Anruf waehrend des Videos, App im Hintergrund, langes Video mit Endkarte. Die Frist zaehlt ab dem show-Aufruf, nicht ab Videostart. Der Zeitgeber wird ausserdem nie geloescht, anders als in admobWarten (Zeile 1381 clearTimeout).

**Was zu tun ist:** Die Belohnung nicht am Ausgang des Rennens festmachen. Einen Zuhoerer auf das 'rewarded'-Ereignis setzen, der das verdiente Leben in eine Variable schreibt, und diese Variable auch dann noch auswerten, wenn die Frist schon gegriffen hat. Zusaetzlich: greift die Frist, waehrend die Anzeige noch laeuft, darf die App nicht so tun, als sei nichts gewesen.

**Einschränkung aus der Gegenprüfung:** Drei Teile der Begruendung sind falsch oder zu hoch gegriffen, der Befund selbst bleibt:

a) Das Beispiel "langes Video mit Endkarte" trifft nicht. Die Belohnung wird in onUserEarnedReward ausgeloest, also beim Erreichen der Belohnungsschwelle im Video - vor der Endkarte. Wie lange jemand danach auf der Endkarte sitzt, spielt fuer das Rennen keine Rolle mehr. Belastbar sind nur die Faelle, in denen die Belohnung selbst spaeter als 120 s nach dem show-Aufruf faellt: Unterbrechung durch Anruf, App im Hintergrund, angehaltene Anzeige. Der Zusatz "Frist zaehlt ab dem show-Aufruf, nicht ab Videostart" stimmt zwar, betraegt aber nur die Anzeigen-Startverzoegerung und traegt praktisch nichts bei.

b) "Der Zeitgeber wird nie geloescht" stimmt (kein clearTimeout, anders als Zeile 1381 in admobWarten), ist aber nicht der Schaden. Das Promise ist dann schon entschieden, das spaete f(null) ist wirkungslos; es bleibt nur bis zu zwei Minuten ein Zeitgeber haengen. Der Schaden ist allein die weggeworfene Belohnung.

c) Schwere "schwer" ist zu hoch, "mittel" trifft es. Im admobDa()-Zweig (Zeile 4517-4521) wird kein Fenster gebaut und keines entfernt, der Bildschirm lessonOutOfLives bleibt mitsamt Knopf lAd stehen (Zeile 4607), der Nutzer kann es also sofort noch einmal versuchen. Ausserdem wird werbungGezaehlt() nur bei lief === true aufgerufen, das Tageskontingent ist also nicht verbraucht. Verloren sind die zwei Minuten, nicht der Zugang zum Leben.

Wichtig fuer die Behebung, und das fehlt im Befund: die Frist darf NICHT einfach herausgenommen werden. Da das Plugin den Aufruf beim Schliessen ohne Belohnung weder aufloest noch ablehnt, waere admobZeigen sonst bei jedem Abbruch fuer immer haengen - fertig() liefe nie. Richtig ist, die spaete Belohnung trotzdem zu verwerten: entweder zusaetzlich auf AdMobP.addListener('onRewardedVideoAdReward', ...) hoeren und das Leben auch nachtraeglich gutschreiben, oder das show-Promise mit .then() weiterverfolgen und bei spaeter Aufloesung nachliefern, und als Renn-Gegner statt der starren 120 s das Ereignis 'onRewardedVideoAdDismissed' verwenden.

---

## 12. Jeder Fehlschlag der Werbung ist vollkommen stumm - der Knopf sieht kaputt aus

**Schwer** · Fehlerfall · `web/index.html:4564`

```
    if(!angesehen) return;
```

**Was passiert:** Kein Fill, kein Netz, Nutzer bricht ab, Zeitablauf, Tageskontingent voll, admobDarf false - alle Wege enden in fertig(false), und dort steht nur ein return. Keine Meldung, kein Ton, keine Zeile. Der Nutzer tippt auf '♥ Video ansehen' und die App reagiert ueberhaupt nicht. Dazu kommt Zeile 4513: bei !werbungErlaubt() bricht zeigeWerbung sofort ab, ebenfalls stumm. Fuer den Nutzer ist ein defekter Knopf nicht von einer nicht verfuegbaren Anzeige zu unterscheiden - und er sitzt auf dem Bildschirm ohne Leben, wo genau dieser Knopf der einzige schnelle Ausweg ist. Das ist der Fall, der die App schlechter macht als gar keine Werbung: ohne den Knopf wuesste er wenigstens, dass er warten muss.

**Was zu tun ist:** fertig(false) unterscheidbar machen und eine kurze Zeile anzeigen, etwa 'Gerade ist kein Video da. Versuch es spaeter noch einmal.' Ein Textschluessel in sprachen.py, eingeblendet an derselben Stelle wie lektion.bis_naechstes. Kein Entwicklertext, ein Satz.

**Einschränkung aus der Gegenprüfung:** Drei Teile des Befunds stimmen nicht:

1. FALSCH: "Tageskontingent voll, admobDarf false, Einwilligung fehlt -> stummer Knopf". Diese Faelle erzeugen keinen toten Knopf, weil der Knopf dann gar nicht gezeichnet wird: 4588 `const perVideo = werbungErlaubt();` und 4599 `(perVideo ? '<button ... id="lAd">' : '')`. werbungErlaubt() (1301-1308) prueft genau diese drei Dinge. Zwischen Zeichnen und Tippen kann sich nichts davon aendern (admobDarf wird nur in admobStart gesetzt, 1369/1372; werbungHeute.n steigt nur nach einer gelaufenen Anzeige). Damit ist Zeile 4513 `if(!werbungErlaubt()){ fertig(false); return; }` vom Leben-Knopf aus praktisch unerreichbar. Sie greift nur beim Interstitial (4644-4656), und dort ist Stille richtig: der Rueckruf ist bewusst `()=>{}`, der Nutzer hat nichts angefordert.

2. FALSCH: "Nutzer bricht ab" als Defekt. Wer die Anzeige selbst wegdrueckt, weiss, warum er kein Leben bekommt. Das ist kein fehlendes Feedback.

3. FALSCH: "ohne den Knopf wuesste er wenigstens, dass er warten muss". Die Wartezeit steht immer ueber dem Knopf: 4595 `fmtMin(nextLifeIn())` mit t('lektion.bis_naechstes'). Bei genug Muenzen steht daneben zusaetzlich der Kauf-Knopf (4589/4600). Der Nutzer sitzt also nicht orientierungslos da.

WAS WIRKLICH STIMMT, eng gefasst: Auf dem Geraet fuehren kein Fill, kein Netz, ein Ausnahmefehler oder der 120-Sekunden-Zeitablauf (1404-1405, 1414) ueber 4519 zu fertig(false) und dort in 4564 in ein nacktes return - ohne Ton, Text oder Zustandsaenderung, und ohne Schutz gegen Mehrfachtippen. Zu reparieren ist genau ein Punkt: ein else-Zweig in werbungFuerLeben (4563-4570) mit kurzer Meldung plus sound('no'), und eine Laufsperre wie bei 2018. Schwere eher mittel als schwer, weil Wartezeit und Muenzweg sichtbar bleiben und der Fall erst mit den echten Kennungen haeufig wird.

---

## 13. Doppeltipp auf 'Video ansehen' hat keinen Riegel - zwei Anzeigen gleichzeitig, im Browser zwei Leben fuer einen Tipp

**Schwer** · Fehlerfall · `web/index.html:4605`

```
  if($('lAd')) $('lAd').addEventListener('click', werbungFuerLeben);
```

**Was passiert:** Der Knopf wird beim Tippen nicht gesperrt, und weder zeigeWerbung (4512) noch admobZeigen (1392) haben eine 'laeuft gerade'-Variable. Da nach dem Tipp sichtbar nichts passiert (vorheriger Befund), ist der zweite Tipp die natuerliche Reaktion. Auf dem Handy laufen dann zwei prepareRewardVideoAd auf dieselbe Kennung; im Plugin ist preparedAds eine Map ueber die adUnitId (AdRewardExecutor.java Zeile 23), der zweite Ladevorgang ueberschreibt also den ersten Eintrag. Je nach Zeitversatz bekommt der Nutzer ein zweites, ungewolltes Video hinterhergeschoben, oder eine der beiden Zusagen haengt die vollen 120 Sekunden. Im PC-Browser ist es eindeutig: der Platzhalterzweig baut zwei Ueberlagerungen uebereinander, kasten.remove() in Zeile 4553 entfernt nur die eigene, und der Nutzer bekommt zwei Leben fuer einen Tipp - waehrend werbungGezaehlt() in Zeile 4522 zweimal vom Tageskontingent abzieht.

**Was zu tun ist:** Eine Variable werbungLaeuft am Anfang von zeigeWerbung setzen und im fertig-Zweig wieder loeschen; bei gesetzter Variable sofort zurueck. Zusaetzlich den Knopf in werbungFuerLeben per disabled sperren, damit man das Ergebnis auch sieht.

**Einschränkung aus der Gegenprüfung:** Falsch ist der Teil, den der Befund als "eindeutig" bezeichnet: der PC-Browser. .werbung ist in Zeile 248 "position:fixed; inset:0; z-index:999; background:#060C20", also eine deckende Vollbild-Ueberlagerung, und der Platzhalterzweig baut sie synchron im selben Klick-Handler auf (werbungErlaubt, stilleBitte, werbungGezaehlt 4522, createElement, appendChild 4536 - alles ohne await). Wenn der Handler zurueckkehrt, liegt die Ueberlagerung bereits ueber #lAd; der zweite Tipp wird beim Zustellen neu getroffen und landet auf der Ueberlagerung. Es gibt im Browser also weder zwei Ueberlagerungen noch zwei Leben noch einen doppelten Abzug vom Tageskontingent. Einzige Restvariante am PC: der Mausklick fokussiert den Knopf, ein danach gedruecktes Enter loest ihn erneut aus, weil Tastaturaktivierung keine Trefferpruefung macht - Randlage, auf dem Handy ohne Bedeutung. Auch "zwei Anzeigen gleichzeitig" trifft nicht: das zweite show scheitert am noch laufenden ersten. Der realistische Schaden auf dem Geraet: loest der zweite Ladevorgang erst nach dem Schliessen des ersten Videos aus, schiebt sich ein unangefordertes Vollbild-Video ueber die inzwischen per showLevelHome() (4569) geoeffnete Startseite; wird es angesehen, gibt es ein zweites Leben und einen zweiten Abzug. Schwere daher eher mittel als schwer, und die Belegzeile ist nur im AdMob-Zweig wirksam.

---

## 14. Ein spaet eintreffendes Video reisst eine bereits laufende Lektion ab

**Schwer** · Fehlerfall · `web/index.html:4568`

```
    showLevelHome();
```

**Was passiert:** showLevelHome wird aufgerufen, ohne zu pruefen, wo der Nutzer inzwischen steht - und es leert in Zeile 4106 $('lBody').innerHTML und $('tBody').innerHTML. Der Interstitial-Weg hat genau diese Pruefung (Zeile 4655: Lx === dieseLektion && sichtbar('levelView') && sichtbar('lesson')), der belohnte Weg hat sie nicht. Erreichbarer Weg: Leben leer, Nutzer tippt 'Video ansehen', die Anzeige laedt langsam, er wartet nicht, kauft stattdessen mit Muenzen ein Herz (Zeile 4606, kaufe('herz') setzt in Zeile 3695 lives.anzahl hoch) und startet eine Lektion. Jetzt erscheint das nachgeladene Video ueber der laufenden Lektion, und danach wirft showLevelHome die Lektion samt aller bereits gegebenen Antworten weg - lessonEnd wird nie erreicht, der Lerntag wird nicht gezaehlt.

**Was zu tun ist:** Denselben Riegel setzen wie beim Interstitial: vor showLevelHome pruefen, ob der Bildschirm ohne Leben ueberhaupt noch steht. Steht er nicht mehr, nur die Leben gutschreiben und renderLives aufrufen, aber die Ansicht in Ruhe lassen.

**Einschränkung aus der Gegenprüfung:** Zwei Angaben im Befund sind zu weit gefasst, die Kernaussage bleibt:

a) „samt aller bereits gegebenen Antworten weg" stimmt so nicht. Richtige Antworten werden schon während der Lektion verbucht (`showLessonTask`, ca. 4487-4494: `known.add(...)`, `zaehle('neu'/'ric'/'auf')`), und `document.addEventListener('visibilitychange', ...)` in Zeile 2439-2448 ruft beim Wegblenden der App `saveProgress()` auf – wenn die native Anzeige hochkommt, sind gelernte Wörter, Münzen und Tagesaufgaben-Zähler also bereits gesichert. Tatsächlich verloren geht die laufende Lektion selbst (Warteschlange, Position, Ergebnisschirm) und alles, was nur in `lessonEnd()` passiert: `zaehle('lek')` (4613), der „ohne Fehler"-Bonus (4616), `questZeilen()` (4625) und `markToday()` (4617).

b) „der Lerntag wird nicht gezaehlt" gilt nur, wenn der Tag nicht schon anderweitig markiert war – `markToday()` wird auch aus der Geschichte (4061) und aus dem bestandenen Level-Test (4741) gerufen.

c) Kleinigkeit: die zitierte Interstitial-Prüfung in 4655 enthält zusätzlich `!wegmarkeLaeuft`.

---

## 15. Nutzer mit Vollversion bekommen beim Start trotzdem das Werbe-Einwilligungsfenster

**Mittel** · Einwilligung · `web/index.html:1356`

```
  if(vollversionGemerkt()) return;
```

**Was passiert:** admobStart() steigt bei gemerkter Vollversion sofort aus, AdMobP bleibt null. einwilligungFragen() (Z. 1247-1250) prueft unlimited() aber nicht. In werbungVorbereiten() (Z. 4850, 'if(einwilligungFragen()) await zeigeEinwilligung();') wird deshalb einem zahlenden Abonnenten der Dialog 'Werbung in Zmaj - Zmaj ist kostenlos und lebt von Werbung' vorgelegt und eine Einwilligung fuer eine Datenverarbeitung abgefragt, die bei ihm nie stattfindet.

**Was zu tun ist:** In einwilligungFragen() zusaetzlich auf !unlimited() und !vollversionGemerkt() pruefen.

**Einschränkung aus der Gegenprüfung:** Drei Praezisierungen, die den Befund nicht umstossen, aber richtigstellen:

a) Der Dialog kommt nicht bei jedem Start, sondern einmal: Nach der Antwort speichert einwilligungMerken() (Zeile 1269-1272) die Wahl, einwilligungGueltig() ist danach wahr, und das Fenster bleibt weg - bis EINWILLIGUNG_STAND (Zeile 1237) hochgezaehlt wird.

b) Zeile 1356 ist nicht die eigentliche Ursache, sondern nur der Ausloeser auf dem Handy. Die Wurzel ist die fehlende unlimited()-Pruefung in einwilligungFragen() (1247-1250). Im PC-Browser steigt admobStart() schon eine Zeile frueher aus (Zeile 1350, kein Capacitor-Plugin), dort bekommt ein Nutzer mit Vollversion (dauerVoll oder gemerktem Stand) denselben Dialog, ganz ohne Zeile 1356. Die saubere Reparatur gehoert deshalb in einwilligungFragen() - eine Zeile "if(unlimited()) return false;" -, nicht in admobStart().

c) Kleine Ungenauigkeit in der Formulierung des Befundes: Der Ausstieg in 1356 liest mit vollversionGemerkt() (Zeile 3034) direkt aus dem Geraetespeicher (zmaj_voll), waehrend einwilligungFragen() gar nichts davon liest. Ein Nutzer mit der versteckten Dauer-Vollversion (dauerVoll, Zeile 2140-2152) ist sogar doppelt betroffen: zmaj_voll steht bei ihm auf '0', deshalb greift 1356 nicht, AdMob faehrt hoch - obwohl premium wahr ist.

---

## 16. Wird ein belohntes Video vorzeitig geschlossen, haengt die App zwei Minuten und zaehlt die gelaufene Anzeige nicht

**Mittel** · Platzierung · `web/index.html:1402`

```
      const lohn = await Promise.race([AdMobP.showRewardVideoAd(),
                                       new Promise(f => setTimeout(()=>f(null), 120000))]);
```

**Was passiert:** Im nativen Plugin wird der Aufruf nur im Belohnungs-Horcher aufgeloest: 'OnUserEarnedRewardListener { item -> ... call.resolve(response) }' in zmaj-android/node_modules/@capacitor-community/admob/android/src/main/java/com/getcapacitor/community/admob/rewarded/RewardedAdCallbackAndListeners.kt. Beim blossen Schliessen laeuft nur onAdDismissedFullScreenContent (FullscreenPluginCallback.kt), der PluginCall wird weder aufgeloest noch abgelehnt. Das Versprechen bleibt also volle 120 Sekunden offen. In dieser Zeit ist der Knopf 'Video ansehen' weiter da und anklickbar (siehe Doppeltipp-Befund), und werbungGezaehlt() (Zeile 4519) laeuft nicht, obwohl Google eine Impression gezaehlt hat - das Tageslimit stimmt danach nicht mehr mit dem ueberein, was der Nutzer gesehen hat.

**Was zu tun ist:** Zusaetzlich auf die Plugin-Ereignisse hoeren, so wie es der Interstitial-Zweig mit admobWarten() schon macht: 'rewardedVideoAdDismissed' bzw. 'rewardedVideoAdFailedToShow' gegen 'rewardedVideoAdReward' rennen lassen, statt allein auf das Versprechen von showRewardVideoAd() zu setzen. Die Frist von 120 s bleibt als letzte Reissleine.

**Einschränkung aus der Gegenprüfung:** Ein Punkt im Titel ist falsch: "Die App haengt zwei Minuten" trifft nicht zu. Im AdMob-Zweig wird ueberhaupt kein eigenes Fenster gebaut - das return in Zeile 4520 ueberspringt den Platzhalterkasten ab Zeile 4524, und stilleBitte() (Zeile 2738) stellt nur Ton ab, es ist keine Sperre und keine Ladeanzeige. Der Nutzer steht nach dem Schliessen sofort wieder auf dem voll bedienbaren "Keine Leben"-Schirm (lessonOutOfLives, Zeile 4577). Richtig ist: es passiert zwei Minuten lang gar nichts sichtbar - kein Leben, keine Meldung, keine Rueckmeldung -, und nach Ablauf der Frist greift in werbungFuerLeben Zeile 4564 'if(!angesehen) return;', also wieder nichts. Das Problem ist stille Wirkungslosigkeit, nicht ein Einfrieren. Nebenbei ist damit auch der Code-Kommentar in den Zeilen 1397-1400 sachlich falsch: er begruendet die Frist damit, der Nutzer stuende sonst "ewig vor der Ladeanzeige" - eine Ladeanzeige gibt es auf diesem Weg nie. Zweite kleine Ungenauigkeit: der Befund nennt FullscreenPluginCallback.kt als Ort, an dem nichts aufgeloest wird; die eigentliche Konstruktionsstelle mit dem onCompleted-Runnable steht in AdRewardExecutor.java:76-83. Am Ergebnis aendert das nichts, denn auch dieser Runnable loest nichts auf. Dritte Praezisierung: der Fehler ist kein Doppel-Leben-Risiko - tippt der Nutzer waehrend der offenen Frist erneut und sieht das Video diesmal zu Ende, wird nur der zweite PluginCall aufgeloest; der erste liefert nach 120 Sekunden null und faellt folgenlos durch.

---

## 17. Kein Ladehinweis im AdMob-Weg, obwohl der Kommentar einen behauptet - und prepare hat gar keine Frist

**Mittel** · Fehlerfall · `web/index.html:1396`

```
      await AdMobP.prepareRewardVideoAd({adId: ADMOB_ID.belohnt, isTesting: ADMOB_TEST,
```

**Was passiert:** Der Kommentar direkt darunter (Zeile 1398-1401) spricht davon, der Nutzer stuende sonst 'ewig vor der Ladeanzeige'. Es gibt keine Ladeanzeige. Die Ueberlagerung .werbung (CSS Zeile 248, gebaut in Zeile 4524) entsteht nur im Platzhalterzweig; der AdMob-Zweig in Zeile 4518-4521 baut gar keine Oberflaeche. Ausserdem ist nur show durch die Frist abgesichert, prepare nicht: dieses await hat keine Zeitgrenze. Bei schwachem Netz vergehen zwischen Tipp und erstem Bild der Anzeige mehrere Sekunden, in denen die App vollkommen unbeteiligt aussieht. Immerhin: die App haengt nicht, sie bleibt bedienbar - aber nur, weil sie gar nichts anzeigt. Genau diese fehlende Rueckmeldung loest den Doppeltipp aus (naechster Befund).

**Was zu tun ist:** Sofort nach dem Tipp den Knopf sperren und auf 'Video wird geladen ...' umschreiben, und prepare in dieselbe Promise.race-Konstruktion legen wie show, mit einer kurzen Frist von etwa 15 Sekunden - kein Mensch wartet zwei Minuten auf ein Leben.

**Einschränkung aus der Gegenprüfung:** Zwei Praezisierungen, die den Befund nicht kippen, aber seine Formulierung korrigieren:

a) Der Vorwurf "Nutzer stuende ewig vor der Ladeanzeige" als Fehlerbeschreibung ist zu stark. Scheitert das Laden, lehnt das Plugin ab, :1412 `catch(e){ return false; }` faengt das - ein unbegrenztes Warten ist nicht der reale Fall. Der belegbare Mangel ist enger und trotzdem echt: waehrend des prepare zeigt die App nichts, und der Fehlschlag danach bleibt ebenfalls wortlos, weil :4564 `if(!angesehen) return;` kommentarlos abbricht. Der Nutzer tippt "Leben holen" und bekommt weder waehrenddessen noch danach irgendeine Reaktion.

b) "gebaut in Zeile 4524" ist minimal unscharf: :4524 erzeugt das div, :4525 setzt `className='werbung'`. Sachlich richtig, nur eine Zeile daneben.

---

## 18. Die Datenschutzerklaerung nennt die Diagnosedaten nicht, die im Data-Safety-Formular als erhoben und geteilt angegeben werden

**Mittel** · Zielgruppe · `C:\Users\Ajdin\Desktop\Bosnisch Lernapp\sprachen.py:522`

```
"set.dsgvo_werbung_an": "<b>Werbung:</b> ... Beim Ausspielen einer Anzeige erhält Google die Werbe-ID deines Geräts, deine IP-Adresse, grobe Angaben zu Gerät und Land sowie die Information, welche Anzeige du gesehen oder angetippt hast.<br>...<b>Sonst nichts:</b> Die App bindet keine Analyse-Dienste ein ..."
```

**Was passiert:** Die Erklaerung zaehlt vier Dinge auf: Werbe-ID, IP-Adresse, grobe Geraete- und Landangaben, Anzeigen-Interaktion. Das Data-Safety-Formular in STORE_TEXTE.md:1125-1130 kreuzt aber vier Kategorien an, darunter "App-Informationen und -Leistung | Diagnosedaten | Startzeit, Haenger, Energieverbrauch - das SDK misst sich selbst". Diagnosedaten kommen in der Datenschutzerklaerung nicht vor. Ebenso wenig die Zwecke "Analysen" und "Betrugspraevention und Sicherheit", die im Formular fuer alle vier Kategorien angegeben werden - der Text sagt an dieser Stelle sogar "Sonst nichts: Die App bindet keine Analyse-Dienste ein". Google vergleicht die verlinkte Datenschutzerklaerung mit dem Formular; STORE_TEXTE.md:1218-1221 nennt genau diesen Abgleich selbst als Pruefpunkt. Sagen beide nicht dasselbe, ist das der Anlass fuer eine Rueckfrage oder eine Beanstandung. Der Text ist in allen acht Sprachen betroffen (sprachen.py:522 de, :951 en, :1282 tr usw.) und steht so auch schon oeffentlich in github-seite/datenschutz.html.

**Was zu tun ist:** In set.dsgvo_werbung_an die Aufzaehlung um die Diagnosedaten ergaenzen (etwa "sowie technische Messwerte des Werbebausteins wie Startzeit und Haenger") und die Zwecke nennen (Werbung, Reichweitenmessung, Betrugspraevention). Den Satz "Sonst nichts: Die App bindet keine Analyse-Dienste ein" praezisieren zu "ausser Google AdMob bindet die App keine weiteren Dienste ein", sonst steht er gegen die Zweckangabe "Analysen" im Formular. Danach seite_bauen.py laufen lassen und github-seite/ neu hochladen.

**Einschränkung aus der Gegenprüfung:** Haltbar ist nur die eine Hälfte: Die Datenart "Diagnosedaten" (STORE_TEXTE.md:1129) fehlt in der Datenschutzerklärung (sprachen.py:522 und die sieben Übersetzungen, dazu github-seite\datenschutz.html). Das ist der ganze belegbare Befund.

Nicht haltbar ist der Zusatz zu den Zwecken "Analysen" und "Betrugsprävention und Sicherheit":
- Das sind Zwecke von Googles Verarbeitung, keine Datenarten. Die Erklärung verweist dafür ausdrücklich weiter: sprachen.py:522 "Was Google mit den Daten macht, steht in Googles Datenschutzerklärung: policies.google.com/privacy". Ein Verweis auf die Erklärung des Empfängers ist die übliche und zulässige Form, ein Widerspruch entsteht dadurch nicht.
- Der behauptete Selbstwiderspruch existiert so nicht. Der Satz lautet vollständig: "<b>Sonst nichts:</b> Die App bindet keine Analyse-Dienste ein und lädt keine Schriften oder Skripte von fremden Servern. Alles Übrige ... steckt in ihr selbst." Es geht erkennbar um eingebundene Fremd-SDKs und Fremdserver, nicht um die Frage, ob Google die Werbedaten auswertet. Beides kann gleichzeitig wahr sein. STORE_TEXTE.md:1158 sagt selbst "Es ist kein Absturzmelder eingebaut" - die App-Aussage ist also korrekt. Der Befund zitiert hier verkürzt und liest eine Aussage in den Text hinein, die dort nicht steht.
- Einzig die englische Fassung sprachen.py:951 ist unnötig weit formuliert ("The app includes no analytics") und die einzige Stelle, an der man den Vorwurf mit etwas gutem Willen noch anbringen könnte. Widerspruch bleibt es auch dort nicht, nur missverständlich.

Fazit: Ein fehlender Halbsatz zu Diagnosedaten, kein Widerspruch bei den Zwecken. Die Korrektur ist ein Zusatz in sprachen.py in allen acht Sprachen (etwa: das Werbe-SDK meldet Google außerdem technische Messwerte über sich selbst - Startzeit, Hänger, Energieverbrauch), danach seite_bauen.py neu laufen lassen. Alternativ die Formularzeile STORE_TEXTE.md:1129 streichen, falls Googles AdMob-Anleitung sie nicht mehr verlangt - das ist vor dem Absenden dort nachzuschlagen.

---

## 19. Auf dem Handy wird npa=1 gesendet, bis der Nutzer einmal die Einstellungen oeffnet - auch wenn er bei Google zugestimmt hat

**Mittel** · Zielgruppe · `C:\Users\Ajdin\Desktop\Bosnisch Lernapp\web\index.html:1261`

```
function werbungPersonalisiert(){
  if(persWahl !== null) return persWahl;
  return einwilligungGueltig() && einwilligung.wahl === 'ja';
}
```

**Was passiert:** Auf Android tritt das eigene Einwilligungsfenster zurueck (einwilligungFragen() bei :1248 gibt false zurueck, sobald admobDa() wahr ist), also bleibt localStorage 'zmaj_einwilligung' leer und einwilligungGueltig() ist false. persWahl ist nach einer Neuinstallation ebenfalls null. werbungPersonalisiert() liefert damit false, und :1397 und :1407 senden npa: true an jede Anzeige. Abgeglichen wird erst in werbungAbgleichen(), und das wird nur an einer einzigen Stelle gerufen: :3615 in showSettings(). Wer die Einstellungen nie oeffnet - und das sind die meisten -, bekommt dauerhaft unpersonalisierte Anzeigen, obwohl er in Googles Fenster zugestimmt hat. Das kostet Einnahmen (unpersonalisierte Anzeigen bringen deutlich weniger) und widerspricht der Datenschutzerklaerung, die in sprachen.py:522 zusagt, bei Zustimmung duerften die Anzeigen "zu deinen Interessen passen". Nebenbei: der Kommentar bei :1324 behauptet "die App setzt npa nicht mehr selbst" - sie tut es an zwei Stellen doch.

**Was zu tun ist:** werbungAbgleichen() zusaetzlich in werbungVorbereiten() (:4841) direkt nach await admobStart() aufrufen, bevor die erste Anzeige kommen kann. Dann steht persWahl von Anfang an auf dem, was in Googles TCF-Speicher liegt, den ZmajEinwilligung.java ohnehin schon ausliest. Den veralteten Kommentar bei :1324 dabei richtigstellen.

**Einschränkung aus der Gegenprüfung:** Zwei Praezisierungen, die den Kern nicht umstossen:

1. Reichweite groesser als beschrieben: Der Schaden trifft nicht nur EU-Nutzer, die zugestimmt haben. ZmajEinwilligung.java liefert bei IABTCF_gdprApplies == 0 ausdruecklich bekannt:true / personalisiert:true ("Keine DSGVO, also nichts einzuschraenken"). Diese Antwort wird beim Start ebenfalls nie gelesen, weil werbungAbgleichen() nur in showSettings() haengt. Also bekommen auch Nutzer in der Tuerkei und in englischsprachigen Nicht-EU-Laendern, fuer die gar keine Einschraenkung gilt, dauerhaft npa=1 - dort ist der Einnahmeverlust ohne jeden rechtlichen Gegenwert.

2. Die Rechtsfolge ist schwaecher als behauptet: npa=1 trotz Zustimmung ist strenger als die erteilte Einwilligung, nicht lockerer. Das ist kein Datenschutzverstoss und kein Verstoss gegen Art. 6 Abs. 1 lit. a DSGVO. Es widerspricht lediglich der Beschreibung in sprachen.py:522 ("Sagst du nein, siehst du nur allgemeine Werbung" - im Umkehrschluss also: bei Ja passende Werbung). Das ist eine Ungenauigkeit in der Datenschutzerklaerung gegenueber dem tatsaechlichen Verhalten, kein Rechtsrisiko. Das eigentliche Problem ist rein wirtschaftlich.

3. Zeitpunkt: Solange ADMOB_TEST = true (:1334) und die Testkennungen (:1336-1337) stehen, kostet es noch nichts. Wirksam wird der Verlust genau mit dem Umstellen auf die echten Kennungen - also vor dem naechsten Release zu beheben. Die einfachste Behebung waere ein Aufruf von werbungAbgleichen() in werbungVorbereiten() direkt nach await admobStart() (:4849).

---

## 20. Der Kommentar ueber admob_app_id bleibt nach dem Tausch stehen und behauptet weiter, dort stehe eine Testkennung

**Klein** · Kennungen · `C:\Users\Ajdin\Desktop\zmaj-android\android\app\src\main\res\values\strings.xml:9`

```
         Werbe-SDK dabei ist. Hier steht Googles oeffentliche TEST-Kennung.
```

**Was passiert:** admob_scharf.py ersetzt nur Zeile 14. Die Zeilen 9 bis 13 sagen danach weiterhin 'Hier steht Googles oeffentliche TEST-Kennung' und 'VOR DEM ERSTEN HOCHLADEN in den Play Store durch die echte Kennung aus dem AdMob-Konto ersetzen'. Beim naechsten Durchsehen sieht das aus wie eine offene Aufgabe, und es besteht die Gefahr, dass jemand eine bereits getauschte Kennung noch einmal anfasst.

**Was zu tun ist:** Den Kommentarblock in admob_scharf.py mittauschen: neuer Text in der Art 'Echte App-ID aus dem AdMob-Konto, eingetragen am 20.09.2026 durch admob_scharf.py. Die Anzeigen-Kennungen stehen in web/index.html unter ADMOB_ID.'

**Einschränkung aus der Gegenprüfung:** Zwei Praezisierungen gegenueber dem Befundtext:

1. Es werden nicht "die Zeilen 9 bis 13" falsch, sondern nur die Zeilen 9 (zweiter Satz) bis 11. Der Rest bleibt wahr: Zeile 8 / Anfang 9 ("Ohne diesen Eintrag stuerzt die App beim Start ab, sobald das Werbe-SDK dabei ist") gilt weiter, und Zeile 12-13 ("Die Anzeigen-Kennungen selbst stehen in web/index.html unter ADMOB_ID") ist durch web/index.html:1337 bestaetigt. Die Behebung ist also ein Umschreiben von zwei Saetzen, kein Loeschen des Blocks.

2. Die behauptete Folge "es besteht die Gefahr, dass jemand eine bereits getauschte Kennung noch einmal anfasst" ist ueberzeichnet. Zeile 14 steht unmittelbar unter dem Kommentar und wuerde dann sichtbar auf ca-app-pub-9105747905460295~ lauten, also erkennbar keine Testkennung. Ausserdem bricht ein zweiter Lauf von admob_scharf.py bei Zeile 77-80 mit "0 Treffer" und dem Hinweis "Steht die Aenderung vielleicht schon drin?" ab, bevor irgendetwas geschrieben wird. Reale Schadwirkung: keine. Es bleibt reine Verwirrung beim Durchsehen.

Zusatzbefund ausserhalb des Auftrags, aber gleicher Ursache: ANLEITUNG.md:424-426 fuehrt die Testkennungen in einer Tabelle und wird beim Tausch ebenfalls veraltet, ohne dass admob_scharf.py sie anfasst.

---
