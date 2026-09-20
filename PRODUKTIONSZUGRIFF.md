# Antrag auf Produktionszugriff

Was Google fragt, wenn der geschlossene Test durch ist — und was du antwortest.

Angelegt am 20.09.2026, dem Tag, an dem der Test veröffentlicht wurde. Die
Fragen stehen hier im Wortlaut, damit du vom ersten Tag an das Richtige
sammelst. Wer erst am Tag 15 liest, was gefragt wird, hat die Hälfte davon
nicht mitgeschrieben.

**Wo:** Play Console → Dashboard → Produktion → „Zugriff auf die
Produktionsversion beantragen". Der Knopf wird erst aktiv, wenn zwölf Tester
**durchgehend die vorangegangenen 14 Tage** angemeldet waren.

**Stand am Abend des 20.09.2026, im Dashboard abgelesen:**

| | |
|---|---|
| Release im geschlossenen Test veröffentlicht | erledigt (Haken) |
| Mindestens 12 Tester angemeldet | **„Momentan sind 5 Tester angemeldet"** |
| Test mit 12 Testern, mindestens 14 Tage | noch nicht begonnen |
| Knopf „Produktionszugriff beantragen" | grau |

**Das ist der Engpass, und er ist größer, als er aussieht.** Eingeladen sind
dreizehn, angemeldet fünf. Eine Einladung zählt nicht — der Tester muss den
Link geöffnet, „Tester werden" gedrückt und die App installiert haben. Und
die vierzehn Tage fangen erst an zu laufen, wenn die zwölf voll sind. Jeder
Tag, den die anderen acht nicht reagieren, ist ein Tag, der vorne nicht
angerechnet wird.

Version 9 ist übrigens durch: „Das App-Update wurde veröffentlicht."


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
> Sprachlern-Apps führen die Sprache nicht. Zmaj schließt diese Lücke: 43
> Level vom Alltag bis zum Arbeitsvertrag, 1108 Wörter mit bosnischer
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

**Noch offen — aus der Tabelle oben zusammenschreiben.**

### 3.2 Woran hast du festgemacht, dass die App reif für die Produktion ist?

**Antwortgerüst:**

> _(am Ende ergänzen: keine Abstürze gemeldet, alle Funktionen von mindestens
> einem Tester benutzt, gemeldete Fehler behoben, Inhalte von
> Muttersprachlern gegengelesen …)_

---

## Was währenddessen NICHT passieren darf

- **Kein neues AAB hochladen.** Googles Prüfuhr zählt ab der zuletzt
  eingereichten Änderung und startet bei jeder Einreichung neu.
- **Kein Tester darf austreten.** Wer aussteigt und wieder einsteigt, fängt
  bei null an — und reißt damit die Zwölf.
- Tester **ergänzen** ist dagegen harmlos und braucht keinen neuen Release.

## Offene Baustellen, die nichts mit dem Antrag zu tun haben

- **Dauerhaftes Premium für Ajdin und Kübra einbauen** — versteckter Weg
  in den Einstellungen (z. B. siebenmal auf die Versionszeile tippen, dann
  ein Code), der `premium` lokal dauerhaft setzt. Kein Play-Kauf, kein
  Ablauf. Das ist eine Codeänderung und geht deshalb erst in den ersten
  Build NACH dem Test. Bis dahin trägt der Lizenztest.
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
     **Noch nicht veroeffentlicht** — der Schalter in der Spalte
     „Veroeffentlichen" fehlt noch. Ohne veroeffentlichte Nachricht verlangt
     Google seit Januar 2024 fuer Besucher aus EWR, UK und Schweiz eine
     zertifizierte Einwilligungsplattform, die es dann nicht gibt.
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
