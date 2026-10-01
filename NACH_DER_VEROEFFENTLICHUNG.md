# Was nach der Veröffentlichung in die Projektmappe nachgetragen wird

Angelegt am 25.09.2026, als Kapitel 1 bis 6 standen. Die Mappe ist inhaltlich
vollständig, aber sie beschreibt einen Zustand: **App im geschlossenen Test.**
Sobald sie in der Produktion ist, stimmen einige Sätze nicht mehr.

Diese Datei sagt, welche. Ohne sie findet man in einem halben Jahr nicht
wieder, wo überall „geschlossener Test" steht.

**Reihenfolge:** erst die Befunde und der Bau (`README.md`), dann der Antrag
(`PRODUKTIONSZUGRIFF.md`), dann diese Liste.

---

## 1. Sätze, die dann falsch sind

| Wo | Was dort steht | Was daraus wird |
|---|---|---|
| **1.2** | „ist fertiggestellt und läuft im geschlossenen Test des Google Play Store" | veröffentlicht, mit Datum |
| **5.4**, letzter Satz | „Dieser Abschnitt wird nach der Freigabe der Produktionsversion abgeschlossen." | streichen, Abschnitt fertigschreiben |
| **5.4**, Tabelle | „Antrag auf Produktionszugriff — frühestens 07.10.2026" · „Freigabe der ersten Produktionsversion — offen" | beide mit Datum |
| **5.7**, letzter Satz | „Dieser Abschnitt wird nach dem 07.10.2026 abgeschlossen." | streichen, Auswertung schreiben |
| **5.6**, Termintabelle | „Oktober 2026 — Freigabe erwartet" | tatsächliches Datum |
| **6.2** | Die Screenshots zeigen unten „Zmaj v0.9" | erledigt am 01.10.2026: acht neue Bilder mit „v1.0“ in `store/screenshots` |

---

## 2. Zahlen, die dann erst entstehen

Das ist der eigentliche Gewinn der vier Monate zwischen Veröffentlichung und
Abgabe: In diesen Abschnitten stehen heute Absichten, später Messwerte.

- **5.7 Inbetriebnahme und Funktionstest** — Auswertung des geschlossenen
  Tests: Wurden alle Funktionen benutzt? Welche Abweichungen gab es? Was
  wurde aufgrund des Tests geändert? Die Antworten entstehen ohnehin für den
  Antrag, sie stehen dann in `PRODUKTIONSZUGRIFF.md`.
- **3.5 / 5.7** — Android Vitals über mehrere Monate statt über drei Tage:
  Abstürze, Blockaden, betroffene Geräte.
- **2.5** — Einnahmen aus Werbung und Abonnement. Dort steht heute „Ein
  Gewinn wird für die Laufzeit der Arbeit nicht erwartet". Wenn doch etwas
  hereinkommt, gehört die Zahl hin, auch wenn sie klein ist.
- **2.2** — die eigene Anwendung im Vergleich mit den dort erhobenen
  Mitbewerbern: Installationen, Bewertungen.
- **5.6** — die Zeiterfassung läuft weiter. `node mappe/zeiterfassung.js`
  rechnet sie neu und sagt, welche Zahl in `kapitel5.json` veraltet ist.

---

## 3. Risiken, die sich auflösen oder eintreten

Kapitel 4 bewertet zwölf Risiken. Nach der Veröffentlichung steht bei einigen
fest, ob die Einschätzung getragen hat. Das gehört in **4.6**, wo heute zwei
eingetretene Fälle stehen.

| Nr. | Wird entschieden durch |
|---|---|
| **R3** Sperrung des Werbekontos | Sind die 20 Befunde eingebaut und nachgeprüft? Dann sinkt das Restrisiko von 10. Bleibt das Konto nach dem Scharfschalten unbeanstandet? |
| **R4** ungültiger Verkehr | ab dem Kennungstausch scharf |
| **R7** Rücksetzen der Prüffrist | mit dem Antrag erledigt |
| **R8** Austritt eines Testers | mit dem Antrag erledigt |
| **R9** Ablehnung des Antrags | eingetreten oder nicht |
| **R12** Veröffentlichung nach dem Abgabetermin | mit der Freigabe erledigt |
| **R5** Verlust des Lernstands beim Nutzer | bleibt; Restrisiko 8 ist der Preis des Aufbaus |

---

## 4. Die zwei offenen Produktentscheidungen

Beide stehen in der Mappe als offen und sollten bis zur Abgabe eine Antwort
haben — auch wenn die Antwort „bleibt wie es ist" lautet.

- **Die Begrenzung der Versuche** (3.4). Die Entscheidung vom 20.09.2026 gilt
  unter einer Bedingung: Sie wird überprüft, wenn Teilnehmer von sich aus
  melden, dass sie deswegen aufgehört haben. Nach dem Test steht fest, ob
  das passiert ist.
- **Die Gestaltung** (3.6). Ein Tester beanstandet das Erscheinungsbild als
  zu eintönig. Solange nichts geschieht, bleibt der Punkt offen — dann
  gehört ein Satz dazu, warum.

---

## 5. Was nicht vergessen werden darf

- **Halloween-Erscheinungsbild:** am 25.09.2026 auf 2027 verschoben, weil der
  31.10.2026 in die Woche des Livegangs fiel. Steht in
  `PRODUKTIONSZUGRIFF.md`.
- **AdMob mit dem App-Shop verknüpfen**, sobald die App in Produktion ist.
  Ohne diese Verknüpfung bleibt die Anzeigenbereitstellung dauerhaft
  eingeschränkt.
- **`app-ads.txt`** ins öffentliche Repo, nicht ins Projekt-Repo. Gecrawlt
  wird sie erst nach dem Livegang.
- **Die Versionshinweise** berichtigen: „Die Vollversion lässt sich noch
  nicht kaufen" stimmt seit dem 20.09.2026 nicht mehr und blieb nur stehen,
  weil jede Einreichung die Prüffrist zurückgesetzt hätte. Der neue Text
  liegt fertig in acht Sprachen in `STORE_TEXTE.md` unter „Versionshinweise –
  Entwurf vom 01.10.2026“.
- **Store-Screenshots in der Play Console tauschen.** **Erledigt am 01.10.2026** (als Entwurf, mit neuer Vorstellungsgrafik „65 Levels“; geht mit der Einreichung am Release-Tag raus). Die acht neuen Bilder
  liegen seit dem 01.10.2026 in `store/screenshots` (1080 × 1920, mit
  Weitermachen-Knopf, Sektionsfarben und Reiter „Wiederholen“). In der
  Console stehen noch die elf alten vom 19.09. Neu erzeugen lassen sie sich
  mit `store/bilder_machen/` – Anleitung im LIESMICH dort.
- **Erledigt am 01.10.2026:** die Zeilenenden in `sprachen.py` sind jetzt einheitlich (CRLF). Ursprünglicher Eintrag: **Zwei verirrte CR-Zeichen in `sprachen.py`**, bei Zeile 212 zwischen
  `laden.rot` und `laden.gruen_sub`. Sie richten keinen Schaden an, sorgen
  aber dafür, dass die Datei je nach Werkzeug 3.476 oder 3.478 Zeilen hat.
  Aufgefallen beim Gegenprüfen der Zahlen für Abschnitt 5.1. **Nicht vor
  dem Ende des Tests anfassen**, danach beim ersten Bau mit entfernen.
- **Seitenzahlen im Inhaltsverzeichnis** stehen von Hand in `kapitel1.json`.
  Nach jeder größeren Änderung neu ermitteln, wie in `mappe/LIESMICH.txt`
  beschrieben.
- **Erledigt am 01.10.2026:** Vorlage „Zmaj: Deine Nachricht ist angekommen / Your message has arrived“ (Deutsch und Englisch) und ein Gmail-Filter, der sie an jede Mail außer von Google und noreply-Adressen schickt. Dazu jeden Abend gegen 20 Uhr die geplante Aufgabe „zmaj-feedback“ (`feedback_holen.py`). Ursprünglicher Eintrag: **Automatische Antwort auf die Kontaktadresse** `zmaj.lernapp@gmail.com`:
  Wer schreibt, soll sofort eine Bestätigung bekommen — dass die Nachricht
  angekommen ist, dass ein Mensch sie liest, und in welcher Zeit. In Gmail
  geht das mit einer Vorlage und einem Filter, der sie an alle eingehenden
  Mails schickt. Die Abwesenheitsnotiz kann das nicht ersetzen: sie antwortet
  derselben Person nur alle vier Tage. Text auf Deutsch und Englisch, weil
  die App in acht Sprachen läuft. Einzurichten, sobald die App öffentlich ist
  — im geschlossenen Test schreibt niemand außer uns.
- **Benachrichtigungen einbauen**, vor allem die Erinnerung, bevor die
  Lernserie abläuft. Wichtig dabei: Das müssen **örtliche** Benachrichtigungen
  sein, die das Gerät selbst stellt (`@capacitor/local-notifications`) — kein
  Versand von außen, sonst bräuchte die App doch einen Server. Zu bedenken:
  Ab Android 13 muss die App die Erlaubnis dafür erfragen; sie gehört nicht in
  den ersten Start, sondern an eine Stelle, an der der Nutzer versteht, wofür.
  Ein Schalter in den Einstellungen zum Abschalten ist Pflicht. Inhalte, die
  sich anbieten: Serie läuft heute ab, tägliche Erinnerung zur selbst
  gewählten Zeit, Leben wieder voll. Der Serienschutz muss dabei
  mitgedacht werden — wer einen hat, soll nicht gemahnt werden, als stünde er
  vor dem Verlust.

- **Erledigt am 01.10.2026** (Entwurf in allen acht Sprachen, geprüft nach dem Neuladen): **Store-Beschreibung ändern, vor dem Produktionsantrag.** Ajdin am
  30.09.2026. Drei Dinge stimmen dort nicht mehr:

  1. **„WAS ES KOSTET“** sagt noch „Zmaj ist kostenlos und finanziert sich
     über Werbung“. Der Ersatzabsatz liegt in `STORE_TEXTE.md` schon
     fertig daneben und muss nur getauscht werden — in **allen acht
     Sprachen**, die Datei führt jede einzeln.

  2. Der Ersatzabsatz ist inzwischen selbst unvollständig. Seit dem
     29./30.09.2026 bringt die Vollversion mehr als „keine Werbung und
     unbegrenzte Leben“: **große Krone, Monokel, Königsmantel, vier
     Drachenfarben (Gold, Silber, Kupfer, Galaxie) und das Funkeln**. Dazu
     **7 Tage kostenlos** (sobald in der Play Console angelegt) und **5
     Geschenktage im Jahr**. Das sind die Verkaufsargumente — sie gehören
     in die Beschreibung, nicht nur in den Kaufkasten.

  3. Zu prüfen, ob die Zahlen noch stimmen: die Kurzbeschreibung nennt
     **65 Levels**, die lange **1728 Wörter, 300 Lückentexte, 16
     Grammatik-Lektionen mit 104 Übungen, 12 Geschichten**. Nach jedem
     Inhaltszuwachs neu abgleichen — `inhalt_bauen.py` gibt die Zahlen
     beim Bauen aus.

  Wichtig: **Pay-to-win-Eindruck vermeiden.** Die Vollversion nimmt
  Werbung weg und gibt Schmuck — sie löst keine Aufgabe. Die Beschreibung
  muss das so sagen, sonst liest es sich wie ein Vorteil beim Lernen.

- **Bewertungsabfrage einbauen.** Ajdins Entwurf am 30.09.2026: ein
  Fenster „Gefällt dir das Spiel?“ — bei **Ja** direkt zur
  Google-Play-Seite der App, bei **Nein** ein zweites Fenster, in das man
  schreiben kann, was besser werden soll. Wann es erscheint und wie oft,
  ist noch zu klären.

  **Vorher zu wissen, sonst kostet es Ajdin die App:** genau dieses Muster
  — erst fragen, ob es gefällt, und nur die Zufriedenen zur Bewertung
  schicken — verbietet Google ausdrücklich. Die Anleitung zur In-App
  Review API sagt wörtlich, die App dürfe **vor oder während** der
  Bewertung **keine Frage** stellen, weder nach der Meinung („Gefällt dir
  die App?“) noch vorhersagend („Würdest du fünf Sterne geben?“). Der
  Grund: das Muster filtert die Unzufriedenen heraus und hebt den
  Sternedurchschnitt künstlich. Google gibt die Antwort deshalb auch gar
  nicht zurück — man erfährt nie, ob jemand bewertet hat.
  Nachgeschlagen am 30.09.2026:
  https://developer.android.com/guide/playcore/in-app-review

  Das Ziel dahinter ist trotzdem richtig, und es gibt zwei saubere Wege:

  **A — beide Wege gleichberechtigt anbieten.** Ein Fenster, zwei Knöpfe
  nebeneinander: „App bewerten“ und „Verbesserung vorschlagen“. Niemand
  wird gefiltert, jeder sieht beides, und wer unzufrieden ist, hat einen
  Weg, der nicht im Store endet. Das ist Ajdins Idee, nur ohne die
  Vorsortierung.

  **B — Googles eigener Weg.** Die In-App Review API ohne jede Frage nach
  einem guten Moment aufrufen, etwa nach einem bestandenen Level. Der
  Feedback-Weg bleibt davon getrennt: den Eintrag „Feedback“ gibt es in
  den Einstellungen schon.

  Zum „wann und wie oft“, wenn entschieden ist: nicht vor dem dritten
  Lerntag, nicht mitten in einer Lektion, höchstens zweimal im Jahr, und
  nie wieder, wenn jemand einmal abgelehnt hat. Google deckelt die
  In-App-Review-Anzeige ohnehin selbst.

- **Die eigenen Geräte als Testgeräte eintragen — bevor**
  `admob_scharf.py` **läuft.** Ajdins S21 steht seit dem 30.09.2026 in
  `ADMOB_TESTGERAETE` (`web/index.html`). Es fehlen **Kübras Handy** und
  **das Galaxy S9**.

  Warum das keine Kleinigkeit ist: die Liste gilt pro Gerät, der Eintrag
  ist der MD5 der Werbe-ID. Nach dem Tausch auf die echten Kennungen
  bekommt jedes Gerät, das nicht darin steht, **echte** Anzeigen. Der
  Verstoß ist der eigene Klick, nicht die bloße Einblendung — aber genau
  darauf läuft es beim Nachtesten hinaus.

  Das S9 hat gar keinen Schutz, dort ist die Dauer-Vollversion nie
  eingeschaltet worden. Kübras Handy ist im Normalbetrieb geschützt —
  `admobStart()` steigt bei `dauerVoll` sofort aus —, aber der Schalter
  hängt an `localStorage`. Nach einer Neuinstallation oder einem
  „App-Daten löschen“ ist er weg, und bis zu den sieben Tipps auf die
  Versionszeile läuft das Gerät als ganz normaler Gratisnutzer.

  **Die App sagt ihre Kennung seit Fassung 64 selbst.** Sieben Tipps auf
  die Versionszeile, dann das Wort `kennung` eintippen. Es erscheinen
  beide Werte: oben die **Werbe-ID** für die AdMob-Konsole, unten die
  **Kennung** für `ADMOB_TESTGERAETE`. Kein Kabel, kein USB-Debugging,
  keine Menüsuche — gebaut genau deshalb, weil sich USB-Debugging auf
  Kübras Handy nicht einschalten lässt.

  **Die Reihenfolge löst das Problem von selbst.** Kübra hat die App aus
  dem Play-Test, also eine Store-Fassung; die lässt sich weder
  fernsteuern noch mit einer Debug-Fassung überschreiben, ohne ihren
  Lernstand zu löschen. Sie bekommt die Kennungsanzeige beim nächsten
  Hochladen — und das ist ohnehin der Produktionsantrag:

  1. ab 07.10. hochladen → Kübra bekommt Fassung 64 oder neuer
  2. Produktion live → AdMob mit dem App-Shop verknüpfen
  3. sie tippt 7× auf die Versionszeile, tippt `kennung`, schickt die Werte
  4. eintragen: Kennung in `ADMOB_TESTGERAETE`, Werbe-ID in der
     AdMob-Konsole unter Einstellungen → Testgeräte
  5. **erst dann** `admob_scharf.py`

  Vor Schritt 5 kann nichts passieren, weil bis dahin Googles
  Testkennungen laufen. Das S9 geht genauso, nur schneller — dort liegt
  eine Debug-Fassung, da reicht Anstecken.

  **Wichtig, sonst ist die ganze Mühe umsonst: jedes Handy hat ZWEI
  Kennungen.** Die Kennung ist der MD5 der **Android-ID** — nicht der
  Werbe-ID; das ist am 30.09.2026 am Gerät nachgemessen worden, die
  Quellen im Netz widersprechen sich. Und die Android-ID hängt seit
  Android 8 am **Signaturschlüssel** der App. Debug- und Play-Fassung
  sind verschieden signiert, also liefert dasselbe Handy zwei
  verschiedene Werte.

  Der Wert, der heute in `ADMOB_TESTGERAETE` steht
  (`41C694B8…`, Ajdins S21), stammt aus der **Debug**-Fassung. Er
  schützt die veröffentlichte App **nicht**. Für die echte App muss der
  Wert aus der **Play**-Fassung dazu — auch für Ajdins eigenes Handy.

  **Deshalb ist die AdMob-Konsole der bessere Weg:** dort zählt die
  **Werbe-ID**, und die hängt an keinem Signaturschlüssel. Ein Eintrag
  deckt beide Fassungen ab. Die App zeigt beide Werte nebeneinander an —
  oben die Werbe-ID für die Konsole, unten die Kennung für den Quelltext.

- **TikTok, Instagram und Facebook** — als **letzter** Schritt, wenn die
  App öffentlich ist. Die Konten legt Ajdin selbst an; erst danach lassen
  sich Reels und kurze Videos planen. Vorher bringt es nichts: ein Profil,
  das auf eine App zeigt, die es im Store noch nicht gibt, verliert seine
  Besucher sofort. Stoff ist genug da — der Drache, die acht
  Oberflächensprachen, die Geschichten, und die Frage „heisst es bosnisch,
  kroatisch oder serbisch?“, die ohnehin ständig gestellt wird.

- **Probezeit beim Abo anlegen**, sobald die App in Produktion ist: in der
  Play Console beim Basisplan ein Angebot mit **Gratiszeitraum von 7 Tagen**.
  Google zeigt beim Kauf dann von selbst „7 Tage kostenlos, danach 2,99 €",
  die App bekommt ganz normal `aktiv: true` und merkt nichts davon — **kein
  neuer Build nötig**, auch später änderbar. Duolingo gibt 14 Tage, Pimsleur
  7, Rosetta Stone 3; wenn nach ein paar Wochen kaum jemand umwandelt, auf 14
  hochstellen. Im geschlossenen Test bringt es nichts: dort kauft niemand
  außer uns, und wir sind Lizenztester.
