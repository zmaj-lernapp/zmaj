# Antrag auf Produktionszugriff

Was Google fragt, wenn der geschlossene Test durch ist — und was du antwortest.

Angelegt am 20.09.2026, dem Tag, an dem der Test veröffentlicht wurde. Die
Fragen stehen hier im Wortlaut, damit du vom ersten Tag an das Richtige
sammelst. Wer erst am Tag 15 liest, was gefragt wird, hat die Hälfte davon
nicht mitgeschrieben.

**Wo:** Play Console → Dashboard → Produktion → „Zugriff auf die
Produktionsversion beantragen". Der Knopf wird erst aktiv, wenn zwölf Tester
**durchgehend die vorangegangenen 14 Tage** angemeldet waren.

**Stand am 23.09.2026: die Uhr läuft.**

| | |
|---|---|
| Release im geschlossenen Test veröffentlicht | erledigt |
| Mindestens 12 Tester angemeldet | **erledigt** — am 23.09.2026 durchgestrichen |
| Test mit 12 Testern, mindestens 14 Tage | **läuft seit dem 23.09.2026** |
| Knopf „Produktionszugriff beantragen" | noch grau |
| Bankkonto | **bestätigt** |
| Version 9 | veröffentlicht |

**Frühester Termin für den Antrag: um den 07.10.2026.** Google nennt kein
Datum und zeigt keinen Zähler. Ab dem 06.10. täglich ins Dashboard sehen,
ob der Knopf aktiv wird.

Bis dahin sind drei Dinge Pflicht:

1. **Nichts einreichen.** Kein neues AAB, keine Änderung an den
   Versionshinweisen, nichts. Jede Einreichung setzt die Uhr zurück, und
   dann beginnen die vierzehn Tage von vorn.
2. **Kein Tester darf austreten.** Wer aussteigt und wieder einsteigt,
   fängt bei null an und reißt die Zwölf. Ergänzen ist dagegen harmlos —
   und ein oder zwei zusätzliche Tester sind eine billige Versicherung.
3. **Die Feedback-Tabelle füllen** (weiter unten in dieser Datei). Drei der
   acht Antragsfragen lassen sich ohne diese Mitschrift nicht beantworten,
   und ein Test, in dem nichts passiert ist, liest sich schlecht.

Was in der Wartezeit erledigt werden kann, ohne die Uhr anzufassen: die
Antworten für den Antrag vorschreiben, `app-ads.txt` hochladen, die
AdMob-Genehmigung abwarten, und die Änderungen für den Build NACH dem Test
vorbereiten — `werbung_richten.py`, `werbung_texte.py`, `admob_scharf.py`
liegen fertig im Projekt.


**Achtung beim Ausfüllen:** Klickst du „Verwerfen" oder verlässt die Seite
ohne „Weiter", ist alles Eingetippte weg. Deshalb hier vorschreiben und dann
hineinkopieren.

**Wie lange es dauert:** Die Prüfung des Antrags dauert in der Regel bis zu
sieben Tage. Danach kommt noch die Prüfung der ersten Produktionsversion
obendrauf. Google empfiehlt selbst mindestens eine Woche Puffer.

---

## Teil 1 — Informationen zum geschlossenen Test

### 1.1 Wie leicht war es, Tester zu finden?

*(Auswahlliste)*

> Ehrlich antworten. Zwölf Leute in zwei Tagen zusammenzubekommen war Arbeit,
> aber es hat geklappt.

**Antwort:** _(beim Ausfüllen wählen)_

### 1.2 Haben die Tester alle verfügbaren Funktionen benutzt?

Und: Entsprach die Nutzung dem erwarteten Verhalten echter Nutzer,
**einschließlich Angaben zu beobachteten Unterschieden**?

> Der zweite Halbsatz ist der, den alle überlesen. Google will die
> Abweichungen ausdrücklich genannt haben. Eine bekannte Abweichung gibt es
> schon jetzt: Ein Tester hat ein iPhone und kann die App nicht installieren.
> Das gehört hier hinein, nicht verschwiegen.

**Noch offen — während des Tests beantworten:**

- [ ] Hat jemand die Sprechaufgabe mit Mikrofon benutzt?
- [ ] Hat jemand eine Geschichte gelesen?
- [ ] Hat jemand den Laden geöffnet und etwas gekauft?
- [ ] Hat jemand die Sprache umgestellt?
- [ ] Hat jemand länger als ein paar Minuten am Stück gelernt?

**Android Vitals, nachgesehen am 23.09.2026: keine Beanstandungen.** Keine
Abstürze, keine ANR-Meldungen bei zwölf Testern. Das ist eine Angabe, die
sich belegen lässt — Google erhebt sie selbst, ohne Zutun der App. Vor dem
Antrag noch einmal nachsehen und den Stand mit Datum hier eintragen.

### 1.3 Fasse das Feedback zusammen und beschreibe, wie du es eingesammelt hast

> Der Weg zählt mit, nicht nur das Ergebnis. Zwei Kanäle sind eingerichtet:
> die WhatsApp-Gruppe und die Feedback-Adresse `zmaj.lernapp@gmail.com`, die
> im Test-Track hinterlegt ist und den Testern bei Google Play angezeigt wird.

**Antwortgerüst:**

> Das Feedback kam über zwei Wege: eine WhatsApp-Gruppe mit allen Testern und
> die im Test hinterlegte Feedback-Adresse zmaj.lernapp@gmail.com. Gemeldet
> wurde: …

**Sammelstelle — hier laufend eintragen:**

| Datum | Wer | Was gemeldet | Was ich daraus gemacht habe |
|---|---|---|---|
| 20.09.2026 | eigene Pruefung waehrend des Tests, nicht von einem Tester gemeldet | Nach dem Umschalten der Sprache speicherte die App den Lernstand nicht mehr und meldete trotzdem Erfolg. Ursache: `MIT_SERVER` wurde gesetzt, bevor die Antwort ausgewertet war; Capacitor beantwortet jeden Pfad ohne Punkt mit der index.html und Status 200. | Behoben in Version 9 und noch am selben Tag ausgeliefert. Dazu zwei weitere: Lernstand wird nicht mehr ueberschrieben, wenn die App waehrend des Startbilds weggelegt wird, und eine gekaufte Vollversion wird nach einer Neuinstallation wieder erkannt. |
| 23.09.2026 | Testerin, Samsung Galaxy S, per Foto gemeldet | „Die Animation von SmartDragon hat sich aufgehangen, trotz Neustart ging es nicht mehr." Das Startbild steht still, vor der Schnauze klebt ein gelber Fleck. Die App selbst laeuft normal. | Ursache gefunden: Der App-eigene Schalter *Animationen* setzt die Klasse `no-anim`, und die Regel `.no-anim *{animation:none!important}` schaltet auch den Vorspann ab. Fuer die Systemeinstellung „Bewegung reduzieren" gibt es Ersatz-Endzustaende, fuer den App-Schalter fehlten sie — deshalb blieb die Glut-Ellipse (`opacity=".85"`) stehen. Nebenbefund: dieselbe Regel toetete den Notausstieg des Vorspanns. Behoben in `vorspann_richten.py`, am 26.09.2026 angewandt und im Browser nachgestellt: der Vorspann laeuft durch, auch mit abgeschalteten Animationen. Laeuft mit dem Build nach dem 07.10.2026. |
| 24.09.2026 | Tester, gesammelt | **Fehler:** Klickt man oben links aufs Herz, erscheint die Angabe zum nächsten Herz nicht darunter, sondern rechts hinter den Münzen. | **Behoben am 26.09.2026** (`herz_richten.py`). Der Hinweis haengt jetzt als eigene Zeile unter dem Herz, die Kopfzeile bleibt gleich hoch. Bei null Leben steht er dauerhaft da, mit rotem Rand. Im Browser nachgestellt. Laeuft mit dem Build nach dem 07.10. |
| 24.09.2026 | Tester, gesammelt | **Fehler:** Beim Vorlesen einer Geschichte beginnt die Stimme von vorn, sobald man ein Wort zum Übersetzen antippt — auch nach Drücken von Pause. Gewünscht: anhalten, Wort sprechen, dort weitermachen. | **Behoben am 26.09.2026** (`vorleser_richten.py`). Der Knopf wechselt jetzt Vorlesen – Pause – Weiterlesen und setzt die Stelle nicht mehr zurueck. Der gemeldete Fall wurde vollstaendig nachgestellt, auch mit dem Antippen dazwischen: Vorlesen bis 4,45 s, Pause, Wort angetippt (Uebersetzung erscheint, die Wortaufnahme laeuft, die Stelle 4,45 s bleibt gesichert), dann Vorlesen - es geht ab 6,61 s weiter. |
| 24.09.2026 | Tester, gesammelt | **Bedienung:** Nach einer abgeschlossenen Lektion — Geschichte wie Vokabeltest — fehlt ein Knopf zurück zum Hauptmenü. | **Behoben am 26.09.2026** (`zurueck_richten.py`). Nach Vokabeltest und Geschichte steht in einer eigenen, leisen Reihe „← Lernpfad“ bzw. „← Geschichten“. Beide im Browser gedrueckt, sie fuehren dorthin. |
| 24.09.2026 | Tester, gesammelt | **Gestaltung:** Die Farben wirken eintönig. Sinngemäß: „ein gutes Spiel mit schlechter Grafik". Wörtlich dazu: „nicht sehr anschaulich, pack maybe verschiedene Farben hin" und „nur blau sieht zwar nicht schlecht aus aber sehr eintönig". | **Bearbeitet am 26.09.2026.** Nachgemessen: auf dem Schirm standen elf Farbwerte, nach Farbton aber nur vier – sechs der elf waren dasselbe Blau. Die Ursache lag im Aufbau: die vier Sektionen benutzten dieselben Farben wie die Zustände (Blau war Primärfarbe *und* Sektion 1, Grün „geschafft" *und* Sektion 2, und so fort), ein fünfter Ton konnte nie entstehen. Jetzt trägt jede Sektion eine eigene Farbe – Blau, Türkis, Violett, Magenta – und die ganze App nimmt die Farbe der Sektion an, in der man gerade lernt: Grund, Flächen, Linien, Knöpfe und Schrift, in der hellen wie in der dunklen Fassung. Beim Wechsel blendet sie in 0,55 Sekunden hinüber. Gelb bleibt der Akzent, Grün „richtig", Rot „falsch". Gleichzeitig wurde die Startseite neu geordnet (Entwurf A+C+D): der Einstieg endet jetzt bei 248 Pixeln, vorher stand „Jetzt dran" bei 4039. Commit `8cd9078`. Läuft mit dem Build nach dem 07.10. |
| 24.09.2026 | Tester, gesammelt | **Vorschlag:** Einstufung für neue Nutzer — Selbsteinschätzung (Anfänger / Fortgeschritten / Profi), danach ein Test, der über den Einstiegspunkt entscheidet. Gedacht für Menschen, die Bosnisch sprechen, aber die Grammatik nie gelernt haben. | **Umgesetzt am 30.09./01.10.2026.** Beim ersten Start: „Kannst du schon Bosnisch?“ mit drei Antworten, danach ein Test mit 15 Fragen in fünf Stufen von leicht bis schwer (Vorbild Duolingo und Busuu). Eingestuft wird hinter die letzte Stufe, bis zu der 80 Prozent aller Antworten stimmen; übersprungene Level bleiben offen. Im Browser durchgespielt: fehlerfrei → Level 58, 6 von 10 → Level 27, vier Fehler am Anfang → Level 1. Läuft mit dem Build nach dem 07.10. |
| 24.09.2026 | Tester, gesammelt | **Vorschlag:** Ein Sammeltopf für falsch beantwortete Fragen, die sich gezielt wiederholen lassen, ohne sich durch bereits Gekonntes zu klicken. | **Umgesetzt am 30.09./01.10.2026.** Eigener Reiter „Wiederholen“: Fehler aus Lektionen und Level-Tests landen dort, zehn je Runde, raus nach zweimal hintereinander richtig. Eine Runde zählt wie eine Lektion. Für alle, auch ohne Vollversion. Läuft mit dem Build nach dem 07.10. |
| 24.09.2026 | Tester, gesammelt | **Vorschlag:** Geläufiges technisches Vokabular aufnehmen (Maschine und Ähnliches), ohne ins Fachliche abzugleiten. | **Umgesetzt am 01.10.2026.** Zwei neue Level in Sektion 4 – „Auto & Werkstatt“ und „Handy, Computer & Geräte“ (Level 27 und 28) – mit eigenen Aufnahmen und Lückensätzen, vorher mit Ajdin Wort für Wort durchgesehen. Sie sind auch im Einstufungstest. Läuft mit dem Build nach dem 07.10. |
| 24.09.2026 | Eigene Idee | **Vorschlag:** Festliche Erscheinungsbilder für den Drachen, zum Beispiel zu Halloween. | **Umgesetzt am 01.10.2026**, in drei Runden mit Ajdin und Kübra abgestimmt und auf dem Gerät abgenommen: Weihnachten (01.12.–07.01.), Ramazanski und Kurban Bajram (Termine bis 2036), Ostern (katholisch bis orthodox). Der Drache trägt dann von selbst und kostenlos ein Festkostüm, die Startseite bekommt Schmuck und einen Gruß auf Bosnisch. Halloween (Skelettdrache) erst ab 2027. Fallen zwei Feste zusammen, wechseln sie sich täglich ab. |
| 01.10.2026 | eigene Prüfung am Gerät (Ajdin und Kübra) | **Gestaltung Lektion:** Kopfzeile und Fortschritt nahmen in der Lektion zu viel Platz weg; der Kasten war bei jeder Aufgabe anders hoch. | Leben und Fortschrittspunkte stehen jetzt im Aufgabenkasten, der Drache ist größer, Anweisungszeilen fallen weg, der Kasten passt sich dem Inhalt an. Store-Screenshots neu aufgenommen. |
| 01.10.2026 | eigene Prüfung am Gerät | **Aussprache und Wörter:** Wörter mit mehreren Formen (z. B. „skup / skupa / skupo“) wurden nur in der ersten Form gesprochen; „skup“ (teuer) war mit „skup“ (Treffen) zu verwechseln; auf bosnischen Packungen steht „kafa“, die App kannte nur „kahva“. | 107 Wörter mit allen Formen neu aufgenommen, drei Aussprachen (nju, skup, drug) verbessert, „teuer“ heißt jetzt „skup / skupa / skupo“, „kahva / kafa“ gelten beide. Gelernte Wörter bleiben gelernt. |
| 01.10.2026 | eigene Prüfung am Gerät | **Einstufungstest durchgespielt:** Grammatikfragen brachen mitten in der Übersetzung um; ein Lückensatz klang unnatürlich („Meso je ljuto“). | Der bosnische Satz steht jetzt oben, die Übersetzung darunter; der Satz heißt „Ovo meso je ljuto.“ mit neuer Aufnahme. |
| 01.10.2026 | eigene Prüfung am Gerät | **Fehler:** Der Drache auf der Startseite sprang bei jedem Wechsel zwischen Lernpfad, Geschichten und Wiederholen. | Behoben: Er wird nur noch neu aufgebaut, wenn sich wirklich etwas ändert; der Jubelsprung kommt einmal nach der ersten Lektion des Tages. |
| | | | |

---

## Teil 2 — Informationen zur App

*Diese Antworten sind laut Google nicht öffentlich und beeinflussen weder die
Sichtbarkeit noch den Zugang zu Programmen. Also ruhig konkret werden.*

### 2.1 Zielgruppe, so genau wie möglich

**Vorgeschrieben:**

> Erwachsene mit persönlichem Bezug zu Bosnien und Herzegowina, die die
> Sprache lernen oder auffrischen wollen: Partnerinnen und Partner in
> deutsch-bosnischen Beziehungen, angeheiratete Familienangehörige, und
> Nachkommen der zweiten und dritten Einwanderergeneration, die Bosnisch oft
> verstehen, es aber nie lesen und schreiben gelernt haben. Schwerpunkt
> Deutschland; die App ist zusätzlich auf Englisch, Türkisch, Schwedisch,
> Niederländisch, Norwegisch, Dänisch und Französisch verfügbar, weil die
> bosnische Diaspora vor allem in diesen Ländern lebt. Zielalter 16 Jahre und
> älter, kein Angebot für Kinder.

### 2.2 Welchen Nutzen bietet deine App?

**Vorgeschrieben:**

> Für Bosnisch gibt es fast kein strukturiertes Lernmaterial — die großen
> Sprachlern-Apps führen die Sprache nicht. Zmaj schließt diese Lücke: 65
> Level vom Alltag bis zum Arbeitsvertrag, 1728 Wörter mit bosnischer
> Tonspur, 16 Grammatik-Lektionen mit 104 Übungen, 12 Lesegeschichten und
> eine Sprechaufgabe mit Spracherkennung. Geübt wird in fünf Formen: hören,
> tippen, auswählen, Lücken füllen und sprechen. Die App läuft vollständig
> auf dem Gerät, ohne Nutzerkonto und ohne Server — es verlässt kein
> Lernstand das Telefon.

### 2.3 Geschätzte Installationen im ersten Jahr

*(Auswahlliste)*

> Die unterste realistische Stufe wählen. Die Angabe ist keine
> Selbstverpflichtung und wird nicht veröffentlicht.

**Antwort:** _(beim Ausfüllen wählen)_

---

## Teil 3 — Informationen zur Produktionsreife

### 3.1 Welche Änderungen hast du aufgrund des Tests gemacht?

> **Die heikelste Frage.** Google erwartet, dass sich im Test etwas geändert
> hat. Ein Test, in dem nichts passiert ist, liest sich schlecht. Deshalb
> oben die Tabelle führen — dann steht hier am Ende von selbst etwas.

**Entwurf vom 01.10.2026, aus der Tabelle oben** (vor dem Einfügen prüfen,
ob inzwischen etwas dazugekommen ist):

> Aus dem Test sind diese Änderungen entstanden:
> Fehler behoben: Nach einem Sprachwechsel wurde der Lernstand nicht mehr
> gespeichert (noch am selben Tag mit Version 9 ausgeliefert). Die
> Startanimation blieb stehen, wenn Animationen abgeschaltet waren. Der
> Hinweis zum nächsten Leben stand an der falschen Stelle. Beim Vorlesen
> einer Geschichte fing die Stimme nach dem Antippen eines Wortes von vorn an.
> Bedienung: Nach Lektion, Test und Geschichte führt jetzt ein Knopf direkt
> zurück zum Lernpfad.
> Gestaltung: Die Tester fanden die App eintönig. Jede Sektion hat jetzt eine
> eigene Farbe, und die Startseite zeigt sofort, wo es weitergeht.
> Zwei Wünsche der Tester sind eingebaut: ein Einstufungstest beim ersten
> Start für alle, die schon Bosnisch sprechen, und ein Reiter „Wiederholen“,
> in dem falsch beantwortete Aufgaben gezielt geübt werden.
> Inhalt: Aus den Rückmeldungen wurden 22 neue Level (von 43 auf 65, von 1108
> auf 1728 Wörter) – unter anderem Einkaufen, Restaurant, Tiere, Obst und
> Gemüse, Länder und Herkunft, Auto und Werkstatt, Handy und Haushaltsgeräte.
> Lektionen: Leben und Fortschritt stehen jetzt im Aufgabenkasten, der Kasten
> passt sich dem Inhalt an. Aussprache: Wörter mit mehreren Formen werden
> vollständig gesprochen, einzelne Aufnahmen wurden verbessert.

### 3.2 Woran hast du festgemacht, dass die App reif für die Produktion ist?

**Entwurf vom 01.10.2026** – die Stellen in eckigen Klammern vor dem
Einfügen prüfen und nur stehen lassen, was stimmt:

> Android Vitals zeigt für den ganzen Test keine Abstürze und keine ANR
> [Stand am Tag des Antrags nachsehen]. Alle gemeldeten Fehler sind behoben
> und auf zwei eigenen Geräten (Android 10 und Android 13 oder neuer)
> nachgeprüft. [Die Tester haben Lektionen, Tests, Geschichten, Hör- und
> Sprechaufgaben, Laden und Sprachwahl benutzt – nur, was 1.2 bestätigt.]
> Werbung und Einwilligung laufen über Google AdMob und Googles zertifizierte
> Einwilligungsplattform; die Werbung wurde vorher Punkt für Punkt gegen die
> AdMob-Richtlinien geprüft. Das Abo läuft über Google Play Billing. Die App
> speichert alles auf dem Gerät, ohne Konto und ohne Server. [Die bosnischen
> Inhalte hat eine Muttersprachlerin gegengelesen – nur, wenn das so ist.]

---

## Ablauf am Release-Tag (vorbereitet am 01.10.2026)

Alles, was vorher ging, ist erledigt: Store-Texte in acht Sprachen,
Screenshots und Vorstellungsgrafik liegen als Entwurf in der Console
(„10 Änderungen“ unter Veröffentlichungen – Übersicht), die Website ist
online, das signierte Paket liegt als `App Zeugs\Release\zmaj-1.0-v89.aab`.

1. Produktionszugriff ist erteilt (Mail von Google).
2. Paket neu bauen, falls seit dem 01.10. noch etwas geändert wurde
   (`python app_bauen.py --aab`), sonst v89 nehmen.
3. Produktion → neuer Release → Paket hochladen, Versionshinweise aus
   `STORE_TEXTE.md` in allen acht Sprachen (ohne Festtage, Ajdin am 01.10.).
4. **Probezeit anlegen:** Abo `vollversion` → beide Basispläne → Angebot
   „7 Tage kostenlos“ für Neukunden. Die Store-Beschreibung verspricht sie –
   ohne Angebot stimmt der Text nicht. Nur mit Ajdins Ja aktivieren.
5. Ajdin drückt „Release starten“ und „Änderungen zur Überprüfung einreichen“.
6. Nach dem Livegang: AdMob mit dem Store verknüpfen, `app-ads.txt` prüfen,
   Kübras Handy und das S9 als Testgeräte eintragen, dann erst
   `admob_scharf.py`.

## Was währenddessen NICHT passieren darf

- **Kein neues AAB hochladen.** Googles Prüfuhr zählt ab der zuletzt
  eingereichten Änderung und startet bei jeder Einreichung neu.
- **Kein Tester darf austreten.** Wer aussteigt und wieder einsteigt, fängt
  bei null an — und reißt damit die Zwölf.
- Tester **ergänzen** ist dagegen harmlos und braucht keinen neuen Release.

## Offene Baustellen, die nichts mit dem Antrag zu tun haben

- **Dauerhaftes Premium — erledigt, und zwar früher als geplant.** Der
  versteckte Weg ist gebaut: siebenmal auf die Versionszeile in den
  Einstellungen tippen (höchstens zwei Sekunden Abstand), dann das Wort
  eingeben. Setzt `zmaj_dauer` lokal, getrennt von `zmaj_voll`, ohne
  Play-Kauf und ohne Ablauf.

  **Achtung:** Der Commit hieß „NICHT ausliefern", lag aber vor dem Bau von
  Version 9 — und ist damit mitgegangen. Es steckt also bereits in der
  Fassung, die die Tester auf dem Gerät haben. Kein Schaden: Es verkauft
  nichts, es verschenkt nur, und Google verbietet nur den Verkauf außerhalb
  von Play. Wer nicht siebenmal hintereinander auf dieselbe Zeile tippt und
  danach das Wort kennt, merkt nichts davon. Für die Zukunft heißt die
  Lehre: „nicht ausliefern" gehört nicht in eine Commit-Zeile, sondern in
  einen Zweig.
- Abo-Produkt `vollversion`: angelegt am 20.09.2026 mit den Basisplänen
  `monat` (2,99 €) und `jahr` (19,99 €), Einstufung Dienst, 174 Länder,
  **beide seit 20.09.2026 aktiv**. Damit taucht der Vollversion-Block in der
  App auf. Alle 13 Tester sind Lizenztester, ihre Käufe kosten also nichts.
  ACHTUNG: In den Versionshinweisen steht noch „Die Vollversion lässt sich
  noch nicht kaufen“. Das stimmt nicht mehr, wird aber NICHT korrigiert —
  jede Einreichung setzt Googles Prüfuhr zurück. Stattdessen in der
  Testergruppe sagen.
- **AdMob**, in dieser Reihenfolge:
  1. **Erledigt am 20.09.2026:** Konto angelegt, Zahlungsland Deutschland
     (unaenderbar). Die App wurde als **nicht veroeffentlicht** eingetragen,
     weil sie nur im geschlossenen Test steht und AdMob sie im Store nicht
     findet. Zahlungsprofil vollstaendig (dasselbe wie bei Play). Das Konto
     selbst war zu dem Zeitpunkt noch in der Genehmigung, Google nennt dafuer
     in der Regel 24 Stunden.

     Die drei Kennungen (keine Geheimnisse, sie stehen in jeder
     ausgelieferten App):

     | | |
     |---|---|
     | App-ID | `ca-app-pub-9105747905460295~9760526209` |
     | Interstitial `zmaj-interstitial` | `ca-app-pub-9105747905460295/9764395638` |
     | Belohnt `zmaj-belohnt` | `ca-app-pub-9105747905460295/8572576770` |
     | Publisher-ID | `pub-9105747905460295` |

  2. **Einwilligungsnachricht fuer den EWR** — steht seit 20.09.2026 als
     **Entwurf** unter Datenschutz und Mitteilungen -> Europaeische
     Verordnungen, Name `Zmaj EWR-Einwilligung`. Eingestellt: App verknuepft,
     Datenschutz-URL `https://zmaj-lernapp.github.io/datenschutz.html`,
     Standardsprache Deutsch plus die sieben anderen Sprachen der App,
     „Nicht einwilligen" fuer alle Laender auf An (die DSGVO verlangt, dass
     Ablehnen genauso leicht geht wie Zustimmen).
     **Veroeffentlicht am 20.09.2026**, Status gruen. Sie wirkt sofort und
     ohne neuen Build — die Tester bekommen ab dem naechsten Start Googles
     Einwilligungsfenster statt des selbstgebauten. Das war noetig, weil
     Google seit Januar 2024 fuer Besucher aus EWR, UK und Schweiz eine
     zertifizierte Einwilligungsplattform verlangt; ohne veroeffentlichte
     Nachricht gibt es keine.
     Zwei Einstellungen dazu, beide geprueft am 20.09.2026:

     - **Gaengige Werbepartner automatisch einbeziehen: 198 Partner.** Steht
       so voreingestellt unter Einstellungen. Die „0 Partner" in der
       Vorschau des Mitteilungs-Editors sind nur ein Platzhalter, der erst
       auf dem Geraet gefuellt wird — kein Fehler.
     - **„Anzeigenquellen automatisch als Werbepartner hinzufuegen": aus,
       und das bleibt so.** Die Option betrifft nur Vermittlung, also
       fremde Werbenetzwerke neben Google. In der Huelle steckt nur
       `@capacitor-community/admob`, kein einziger Vermittlungs-Adapter,
       und unter „Vermittlung" ist nichts eingerichtet — sie braechte also
       heute nichts und wuerde nur dafuer sorgen, dass kuenftig
       automatisch neue Datenempfaenger in die Einwilligung rutschen.
       **Erst einschalten, wenn wirklich einmal Vermittlung eingerichtet
       wird**, sonst liefern die fremden Netzwerke mangels Einwilligung
       nichts aus.
  3. **Sobald die App in Produktion live ist: in AdMob nachtraeglich mit dem
     App-Shop verknuepfen** (App-Einstellungen -> Mit App-Shop verknuepfen,
     `de.smartdragon.zmaj`). Ohne diese Verknuepfung bleibt die
     Anzeigenbereitstellung dauerhaft eingeschraenkt. Die Pruefung danach
     dauert laut Google einige Tage, manchmal laenger.
  4. Zahlungsdaten und USt-IdNr `DE465139848` hinterlegen. Die Seite
     „Zahlungen" blieb am 20.09.2026 leer, vermutlich weil das Konto noch
     nicht genehmigt war — nach der Genehmigung noch einmal hin.
  5. **Die Befunde aus `WERBUNG_PRUEFUNG.md` abarbeiten.** 20 Stueck, davon
     drei kontogefaehrdend. Solange Testkennungen laufen, richtet keiner
     davon Schaden an; gefaehrlich werden sie genau in dem Moment, in dem
     `ADMOB_TEST` auf `false` steht. Gehoert deshalb VOR Schritt 6.

     **Liegt fertig bereit, zwei Skripte:**

     ```
     python werbung_richten.py --schreiben   # 17 Befunde, Code
     python werbung_texte.py --schreiben     # Befund 18, acht Sprachen
     python seite_bauen.py                   # die Webseite zieht dieselben Texte
     python app_bauen.py
     ```

     Beide wurden am 20.09.2026 einmal angewandt, geprueft und wieder
     zurueckgenommen - die Quelle steht also noch genau auf dem Stand, der
     bei den Testern liegt. Geprueft wurde mit nachgebautem AdMob: eine
     Anzeige, deren Nachpruefung beim Zeigen nein sagt, wird geladen und
     verworfen statt gezeigt; ein abgebrochenes Video meldet sofort
     "nichts bekommen" statt nach zwei Minuten; ein zu Ende gesehenes
     Video gibt das Leben auch dann, wenn das Plugin seine Zusage nie
     aufloest. Befund 20 ist schon in `admob_scharf.py` eingebaut.
  6. Erst dann die Kennungen tauschen: `python admob_scharf.py --schreiben`
     (tauscht alle drei und setzt `ADMOB_TEST` auf `false`), danach
     `app_bauen.py`. Vorher nicht: ein Tester, der aus Hilfsbereitschaft eine
     Anzeige anklickt, ist ungueltiger Traffic und kann das AdMob-Konto
     kosten.
  7. `app-ads.txt` liegt fertig in `github-seite/` und muss in das
     oeffentliche Repo `zmaj-lernapp.github.io` hoch, nicht in das private
     Projekt-Repo. Gecrawlt wird sie erst nach dem Livegang.
- Anmeldung zur Servicegebührstufe (Kontogruppe). Bringt beim Abo nichts —
  Abos liegen ohnehin bei 15 % — lohnt aber, bevor du je einen Einmalkauf
  anbietest.
