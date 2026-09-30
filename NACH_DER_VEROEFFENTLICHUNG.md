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
| **6.2** | Die Screenshots zeigen unten „Zmaj v0.9" | neue Bilder aus der veröffentlichten Fassung |

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
  weil jede Einreichung die Prüffrist zurückgesetzt hätte.
- **Zwei verirrte CR-Zeichen in `sprachen.py`**, bei Zeile 212 zwischen
  `laden.rot` und `laden.gruen_sub`. Sie richten keinen Schaden an, sorgen
  aber dafür, dass die Datei je nach Werkzeug 3.476 oder 3.478 Zeilen hat.
  Aufgefallen beim Gegenprüfen der Zahlen für Abschnitt 5.1. **Nicht vor
  dem Ende des Tests anfassen**, danach beim ersten Bau mit entfernen.
- **Seitenzahlen im Inhaltsverzeichnis** stehen von Hand in `kapitel1.json`.
  Nach jeder größeren Änderung neu ermitteln, wie in `mappe/LIESMICH.txt`
  beschrieben.
- **Automatische Antwort auf die Kontaktadresse** `zmaj.lernapp@gmail.com`:
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

- **Store-Beschreibung ändern, vor dem Produktionsantrag.** Ajdin am
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
     **63 Levels**, die lange **1668 Wörter, 290 Lückentexte, 16
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
