# Zmaj – Bosnisch lernen

Eine Lern-App (Deutsch → Bosnisch). Sie läuft als Android-App auf dem Handy
und im Browser am PC. Ohne Server, ohne Konto: Der Lernstand bleibt auf dem
Gerät. Die Oberfläche steckt ganz in `web/index.html`; der Inhalt wird aus
den Python-Dateien daneben erzeugt.

| | |
|---|---|
| Paketname | `de.smartdragon.zmaj` |
| Stand | geschlossener Test, seit 23.09.2026 laufen die 14 Tage |
| Finanzierung | Werbung über AdMob, Vollversion als Abo |

---

## Wo ich anfange, wenn ich lange nicht hier war

| Ich will … | Datei |
|---|---|
| die App am PC starten | `start.py` in Thonny öffnen, **F5** |
| am Lerninhalt arbeiten | `vokabeln.py`, `grammatik.py`, `geschichten.py` |
| Texte der Oberfläche ändern | `sprachen.py` |
| wissen, wie alles zusammenhängt | die Abschnitte ab „Starten“ |
| den nächsten Build vorbereiten | „Liegen bereit für den Build nach dem Test“ |
| Codex-Review und -Triage einschalten | GitHub, Settings → Secrets and variables → Actions: Secret `OPENAI_API_KEY` und Variable `CODEX_AN` = `true` |

---

## Die Android-Hülle

Die Android-Hülle liegt **außerhalb** dieses Ordners, daneben unter
`zmaj-android/` (frisch geklont: `zmaj-huelle/`), in einem eigenen, privaten Repository. Alle Ordner stehen
unten unter „Ordner“.

---

## Die Skripte

Alle laufen mit dem Python aus Thonny. **`python` gibt es auf diesem Rechner
nicht** — der Interpreter steht unter
`C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe`.

### Täglich

| Skript | Was es tut |
|---|---|
| `start.py` | startet die App am PC zum Ausprobieren (nur Dateien und Inhalt, keine Konten) |
| `inhalt_bauen.py` | macht aus den Python-Dateien das JSON fürs Handy |
| `app_bauen.py` | bringt den Inhalt in die Android-Hülle und baut das Paket |

### Beim Veröffentlichen

| Skript | Was es tut |
|---|---|
| `seite_bauen.py` | erzeugt die Rechtstexte als Webseite, inklusive `app-ads.txt` |
| `grafiken_bauen.py` | Symbol und Vorstellungsgrafik für den Store |
| `logo_sichern.py` | holt das SmartDragon-Zeichen aus der App als eigene Datei |
| `projekt_sichern.py` | packt den ganzen Stand in zwei Zip-Dateien |

### Liegen bereit für den Build **nach** dem Test

Diese Skripte dürfen erst laufen, wenn die 14 Tage durch sind — jede
Einreichung setzt Googles Prüfuhr zurück. Reihenfolge wie in der Tabelle.

| Skript | Was es tut | Stand 04.10.2026 |
|---|---|---|
| `import_richten.py` | eine von Hand geschriebene Sicherung kann die App nicht mehr lahmlegen | Probelauf sauber, getestet |
| `sicherheit2_richten.py` | zwei kleine Härtungen (Konten-Links ohne Konten, Fest-Probe) | Probelauf sauber, getestet |
| `barrierefreiheit_richten.py` | Bildschirmleser und Kontrast: 0 kritische und 0 ernste axe-Befunde statt 20 und 102 | Probelauf sauber, getestet |
| `werbung_richten.py` | letzter Rest der Werbeprüfung: auch das belohnte Video wird vor dem Zeigen noch einmal geprüft (App noch vorne?) | Probelauf sauber, getestet. Am 04.10.2026 auf 2 Änderungen gekürzt, alles andere war von Hand drin oder bewusst anders gelöst (Liste im Skript) |
| `werbung_texte.py` | Datenschutzerklärung in acht Sprachen: Zwecke der Werbung und Ausnahme beim Satz „keine Analyse-Dienste“ | Probelauf sauber, getestet. Die Messwerte standen schon von Hand in allen acht Sprachen und sind herausgenommen. Danach auch `seite_bauen.py` |
| `admob_scharf.py` | tauscht die Testkennungen gegen die echten | zuletzt, nach den Werbe-Skripten |

Alle folgen demselben Muster: **erst Probelauf, dann `--schreiben`.**
Ohne den Schalter passiert nichts. Kommt ein gesuchter Textabschnitt nicht
genau einmal vor, brechen sie ab und ändern gar nichts — ein halb geändertes
Programm gibt es damit nicht. Danach `inhalt_bauen.py`, `seite_bauen.py`,
`app_bauen.py`.

Die früheren Patch-Skripte (Dialoge, Vorspann, Herz, Vorleser, Zurück,
Sicherungsmeldung und andere) sind angewendet und wurden am 04.10.2026
entfernt; sie stehen in der Git-Historie.

---

## Die Dokumentation

| Datei | Inhalt |
|---|---|
| `ANLEITUNG.md` | diese Datei: wie das Projekt gebaut und betrieben wird |
| `docs/ARCHITECTURE.md` | Überblick auf Englisch, mit Diagrammen |
| `WORTSCHATZ_KORREKTUREN.md` | was der Muttersprachler korrigiert hat – geht allem vor |
| `docs/TONBEFUNDE.md` | Prüfung der Aufnahmen |
| `docs/uebersetzungen-pruefbericht-2026-09-18.md` | Prüfung der Übersetzungen |
| `docs/barrierefreiheit-2026-10-04.md` | Prüfung der Barrierefreiheit (axe) |
| `docs/BEST_PRACTICES.md` | Antworten für das OpenSSF-Abzeichen |

Store-Texte, Prüfpläne und Arbeitsnotizen liegen nur lokal in `privat/`.

---

## Was nie in dieses Repository gehört

`.gitignore` hält es draußen, aber zur Sicherheit hier noch einmal:

- **`tts_zugang.json`** – der Azure-Schlüssel für die Sprachausgabe
- **`mail_zugang.json`** – das Passwort des Postfachs
- **Der Signierschlüssel** und `keystore.properties` – ohne ihn gibt es nie
  wieder ein Update, mit ihm kann jeder eine gefälschte Version bauen.
  `projekt_sichern.py` nimmt ihn in die Geheim-Zip auf.
- `fortschritt_*.json`, `sitzungen.json`, `codes.json` – echte Nutzerdaten aus
  der Zeit mit Kontoserver (bis 04.10.2026). Es entstehen keine neuen mehr,
  die Einträge in `.gitignore` bleiben für alte Reste stehen.
- `feedback.txt`, `start.log`, `__pycache__/`

---

## Starten

### Am PC ansehen

Es braucht nur einen nackten Dateiserver im Ordner `web`. Einen Befehl
`python` gibt es auf diesem Rechner nicht – gemeint ist immer der Python aus
Thonny. In der Eingabeaufforderung also:

    cd "C:\Users\Ajdin\Desktop\Bosnisch Lernapp\web"
    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" -m http.server 8099 --bind 127.0.0.1

Danach `http://localhost:8099` im Browser öffnen. Beenden mit Strg+C.

Das ist mit Absicht der Weg: Ein Dateiserver liefert nur Dateien aus, genau
wie die Android-Hülle. Was hier funktioniert, funktioniert auch auf dem
Handy – und es wird nichts angefasst, was einem gehört.

Der Inhalt kommt dabei aus `web/inhalt/<code>.json`. Hast du an `vokabeln.py`,
`grammatik.py`, `geschichten.py`, `sprachen.py` oder `uebersetzungen.py`
etwas geändert, muss vorher `inhalt_bauen.py` laufen – sonst siehst du den
alten Stand.

### Was mit `start.py` ist

Seit dem 04.10.2026 ist `start.py` nur noch ein schlanker Starter: In Thonny
öffnen, **F5**, der Browser geht auf `http://localhost:8000` auf. Er liefert
den Ordner `web/` aus und dazu `/api/daten` – den Inhalt, bei jedem Aufruf
frisch aus den Python-Dateien. Eine Änderung an `vokabeln.py` ist damit
nach einem Neuladen im Browser sofort zu sehen, ohne `inhalt_bauen.py`.

Konten, Anmeldung, Profildateien und Mails gibt es dort nicht mehr (der
alte Server mit `konten.py` und `mail.py` ist weg). Der Lernstand liegt
auch am PC im Speicher des Browsers, genau wie auf dem Handy. Im
Projektordner entsteht dabei nichts mehr außer `start.log`.

Außerdem:

- `start.py --fehlende <code>` schreibt die Liste der fehlenden
  Übersetzungen (siehe „Weiter übersetzen“).
- Der Inhalt selbst entsteht in `inhalt.py` (`lade_daten()`). Dieselbe
  Funktion rufen `inhalt_bauen.py`, `daten_exportieren.py`, `demo_bauen.py`
  und die Tests auf – deshalb kann die Handy-Fassung gar nicht vom PC
  abweichen. `start.lade_daten()` geht weiter, es reicht nur durch.

Die Desktop-Verknüpfung **„Zmaj Bosnisch lernen“** und
`Zmaj Bosnisch lernen.vbs` starten ebenfalls `start.py`, ohne Fenster. Ein
zweiter Doppelklick öffnet nur den Browser. Beendet wird in Thonny mit
**Stop**; über die Verknüpfung gestartet läuft er, bis der PC ausgeht (oder
`pythonw.exe` im Task-Manager beenden).

**Wichtig:** Die Datei `web/index.html` nie direkt per Doppelklick öffnen.
Über `file://` darf der Browser die Inhaltsdateien nicht nachladen, die App
zeigt dann nur einen Hinweis. Immer über eine Adresse mit `http://`.

## Aussehen und Einstellungen

Die App nutzt die Farben der bosnischen Flagge (Blau, Gelb, Weiß) und hat
ein Maskottchen: den Drachen **Zmaj**, wie die Nationalelf „Zmajevi“. Er
begrüßt auf der Startseite, jubelt nach einer Lektion und guckt traurig, wenn
die Leben aus sind.

Oben rechts öffnet ⚙ die **Einstellungen**:

- **Sprache:** die acht Oberflächensprachen.
- **Lernen:** Töne, Vibration (nur am Handy), Animationen, Stimme zum
  Vorlesen.
- **Sicherung:** Lernstand als Datei speichern und wieder einlesen (siehe
  „Kein Konto“).
- **Rückmeldung:** Ein Textfeld. „Senden“ öffnet das Mailprogramm des
  Nutzers mit fertiger Nachricht an `zmaj.lernapp@gmail.com`.
- **Über die App:** Version, Quellen, Nutzungsbedingungen, Datenschutz und –
  sobald Werbung läuft – der Knopf, mit dem sich die Einwilligung ändern
  lässt.

### Der Vorspann

Beim Start steht für einen Moment das Zeichen des Studios: Der Drache speit
Feuer nach rechts, und aus dem Feuer tritt der Name **SmartDragon**. Das ist
nicht die App, sondern der Herausgeber – dieselbe Rolle wie die
Kinovorspänne vor einem Film.

Die Bewegung dauert 2,4 Sekunden (`VORSPANN_ABLAUF`), danach steht das
fertige Bild noch 1,5 Sekunden still (`VORSPANN_HALT`). Ohne diese Pause
wechselt die App genau in dem Moment, in dem der Name erscheint, und man hat
ihn nicht gelesen. Antippen überspringt. Weg ist der Vorspann erst, wenn
beides zutrifft: Die Zeit ist um **und** die App steht – auf einem langsamen
Gerät bleibt er also länger, statt auf einen leeren Bildschirm zu wechseln.

Alles steckt als SVG in `web/index.html` und wird mit CSS bewegt: kein Bild,
keine zusätzliche Datei, rund 3 KB. Sollte das Skript gar nicht erst
anlaufen, blendet sich der Vorspann nach zehn Sekunden von selbst weg – dann
steht niemand davor fest.

## Kein Konto

Seit dem 16.09.2026 gibt es **keine Anmeldung mehr**: kein Passwort, keine
E-Mail-Adresse, keine Bestätigungsmail, kein „Passwort vergessen“, keinen
Profilwechsel. Die App öffnet sich und ist da.

Der Grund ist der Verzicht auf einen Server. Ein Konto ohne Server ist
sinnlos – es könnte nichts, was der Gerätespeicher nicht auch kann, und es
hätte Passwörter und Adressen gekostet, die dann irgendwo liegen müssten.

**Wo der Lernstand liegt:** im Speicher dieses Browsers beziehungsweise
dieser App, unter dem Schlüssel `zmaj_stand`. Er überlebt das Schließen der
App und ein Update. Er ist weg, wenn die App gelöscht oder der Speicher der
Seite geleert wird, und er geht nicht von selbst auf ein zweites Gerät über.

### Sicherung

Deshalb **Einstellungen → Sicherung**. Zwei Knöpfe:

- **Sicherung speichern** schreibt den ganzen Stand in eine Datei
  `zmaj-sicherung-JJJJ-MM-TT.json`. Am Handy geht sie ins Teilen-Menü – von
  dort aus an sich selbst schicken oder in die Cloud legen. Am PC ist es ein
  gewöhnlicher Download. (Der Umweg übers Teilen ist nötig, weil eine
  Android-WebView nichts herunterlädt; der Knopf bliebe sonst wirkungslos.)
- **Sicherung einlesen** nimmt so eine Datei wieder an. Sie **ersetzt** den
  Stand auf dem Gerät, es wird nichts vermischt – deshalb fragt die App
  vorher nach. Danach steht da, wie viele Wörter und Lerntage angekommen
  sind.

In der Datei steht nur der Lernstand: gewusste Wörter, bestandene Levels,
gelesene Geschichten, Lerntage, Serienschutz, Leben, Tagesaufgaben, Münzen,
Besitz und `premium`. Kein Name, keine Adresse, nichts über das Gerät.

So kommt der Stand auch von einem Gerät aufs andere: am alten speichern, die
Datei hinüberschicken, am neuen einlesen.

### Die alten Profile

Die Profildateien von früher liegen nur lokal in
**`sicherung_konten_2026-09-16`** und werden von nichts mehr gelesen. Daraus
erzeugte Sicherungen (`zmaj-sicherung-<Name>.json`) liegen daneben; sie
enthalten nur den Lernstand, kein Passwort und keine E-Mail. Das
Umwandlungsskript ist erledigt und steht nur noch in der Git-Historie.

## Rückmeldung per Mail

Die App verschickt **keine Mails mehr**. Sie kann es auch nicht – dafür
bräuchte es einen Server. Stattdessen macht es das Gerät:

**Einstellungen → Rückmeldung**, Text hineinschreiben, „Senden“. Die App
öffnet damit das Mailprogramm des Nutzers – Empfänger, Betreff und Text sind
schon ausgefüllt, abgeschickt wird erst durch ihn selbst. Unten stehen
Sprachcode und Datum, sonst nichts.

Ist auf dem Gerät gar kein Mailprogramm eingerichtet, passiert sichtbar
nichts. Deshalb steht danach die Adresse `zmaj.lernapp@gmail.com` da, mit
einem Knopf zum Kopieren.

### Was aus mail.py und konten.py geworden ist

Am 04.10.2026 gelöscht, zusammen mit dem Kontoteil von `start.py`.
`konten.py` hielt Passwörter, Sitzungen und Einmal-Codes, `mail.py`
verschickte Bestätigungsmail, Passwort-Link und das Feedback. Die App rief
seit `KONTEN_AN = false` (26.09.2026) nichts davon mehr auf, in der
Android-Hülle waren beide nie dabei. Wer die Konten je zurückwill, findet
alles in der Versionsgeschichte vor diesem Datum.

`mail_zugang.json` bleibt: `feedback_holen.py` holt damit die Rückmeldungen
aus dem Postfach. Gebraucht werden nur `benutzer` und `passwort`, die
Vorlage steht in `mail_zugang.BEISPIEL.json`. Die echte Datei enthält ein
Passwort und bleibt auf diesem Rechner.

## Wo was liegt

Alles, was die App sich merkt, steht im Speicher des Browsers
beziehungsweise der App. Nichts davon verlässt das Gerät; niemand außer dem
Gerät selbst kommt daran.

| Schlüssel | Was drinsteht |
|---|---|
| `zmaj_stand` | der ganze Lernstand – Wörter, Levels, Geschichten, Lerntage, Leben, Serienschutz, Tagesaufgaben, Münzen, Besitz, `premium` |
| `zmaj_id` | eine zufällige Gerätekennung. Sie entscheidet, welche drei Tagesaufgaben gezogen werden |
| `zmaj_sprache` | die gewählte Oberflächensprache |
| `zmaj_sound`, `zmaj_haptik`, `zmaj_anim` | Töne, Vibration, Animationen |
| `zmaj_voice` | die gewählte Computerstimme |
| `zmaj_getragen` | welches Stück der Drache gerade trägt |
| `zmaj_werbung` | wie viele Anzeigen heute schon kamen |
| `zmaj_einwilligung` | die Antwort aus dem eigenen Einwilligungsfenster (am PC) |

Schlägt das Schreiben fehl – Speicher voll, privates Fenster, gesperrte
Seitendaten –, läuft die App trotzdem weiter. Jeder Zugriff steht in einem
`try`. Gemerkt wird dann eben nichts.

Sechs dieser Schlüssel hießen früher `rijec_…`, aus der Zeit, als die App
noch „riječ.“ hieß: Sprache, Ton, Vibration, Animationen, Stimme und
Werbezähler. Beim Start benennt die App sie einmalig um, damit beim Umstieg
nichts verlorengeht. Die Zeilen dafür können irgendwann raus.

**Was es nicht mehr gibt:** `fortschritt_<Name>.json`, `sitzungen.json`,
`codes.json`, `postausgang.txt` und `feedback.txt` im Projektordner. Die
Profildateien liegen als Kopie in `sicherung_konten_2026-09-16`. Seit dem
04.10.2026 legt auch `start.py` keine davon mehr an.

## Die Zurück-Taste

Android hat unten eine eigene Zurück-Taste. Ohne Zutun schließt sie die App
sofort – auch mitten in einer Lektion. Das war der Grund, den früheren Knopf
„App beenden“ ersatzlos zu streichen: Auf einem Handy beendet man Apps nicht
über einen Knopf in der Oberfläche.

Die Taste geht jetzt eine Ebene zurück:

| Wo man ist | Was passiert |
|---|---|
| eine Nachfrage steht offen | die Nachfrage wird verneint |
| Einwilligung oder Werbung | nichts, die haben eigene Knöpfe |
| Lektion oder Test | wie der Abbrechen-Knopf unten, samt Warnung |
| Unterseite | dasselbe wie der Zurück-Knopf oben |
| Startseite | „Zmaj wirklich schließen?“ – erst ja, dann zu |

In der Lektion drückt die Taste den vorhandenen Abbrechen-Knopf, statt
seine Arbeit nachzubauen. So fragt sie genauso nach und speichert genauso;
zwei Wege können nicht auseinanderlaufen. Vor dem Schließen wird der
Lernstand geschrieben.

Am PC gibt es keine solche Taste. Dort passiert schlicht nichts – die
Zurück-Taste des Browsers bleibt die des Browsers.

## Zwei Pfade: Lernpfad und Geschichten

Oben auf der Startseite steht eine Reiterleiste. **📚 Lernpfad** ist der
Hauptweg mit Lektionen, Level-Tests und Grammatik. **📖 Geschichten** ist
ein zweiter, freiwilliger Pfad zum Lesen. Wer nur Wörter lernen will, bleibt
im Lernpfad und sieht von den Geschichten nichts. Beide Pfade haben einen
eigenen Fortschritt.

Daneben liegt ein dritter Reiter, **🛒 Laden**. Der ist kein Pfad, sondern der
Münzladen – er steht weiter unten unter „Münzen und Laden“. Der Geschichten-
Reiter verschwindet, wenn es gar keine Geschichten gibt; Lernpfad und Laden
sind immer da.

## Der Lernpfad: 9 Sektionen, 65 Levels

Der Lernpfad zeigt neun Sektionen mit ihren Levels, ähnlich wie bei Duolingo.
Ein Level antippen öffnet die Übungen. Bestandene Levels und Sektionen bleiben
offen und können jederzeit wieder gespielt werden.

**Sektion 1 · Grundlagen & Alltag** (15 Levels): Grundlagen, Zahlen, Farben,
Familie, Essen & Trinken, Wochentage, Monate, Zeit, Zuhause, Wetter & Natur,
Körper & Gesundheit, Einkaufen & Kleidung, Unterwegs, Verben, Smalltalk &
Gefühle.

**Sektion 2 · Dinge zum Anfassen** (4 Levels): Obst, Gemüse, Lebensmittel,
Vorrat & Getränke.

**Sektion 3 · Tiere & Natur** (4 Levels): Tiere, Tiere draußen, Rund ums Tier,
Natur & Pflanzen.

**Sektion 4 · Zuhause** (5 Levels): Küche & Bad, Putzen & Nachbarschaft,
Technik & Reparatur, Auto & Werkstatt, Handy, Computer & Geräte.

**Sektion 5 · Sätze bauen** (22 Levels): Fragen stellen, Geschlecht: on, ona,
ono, Verben beugen, Mehrzahl, Nebensätze & Verneinung, Fälle 1: Nominativ &
Akkusativ, Fälle 2: Genitiv, Präpositionen, Fälle 3: Dativ & Lokativ, Fälle 4:
Instrumental & Vokativ, Vergangenheit, Zukunft & Pläne, Können, müssen,
wollen, Reflexive Verben (se), Tagesablauf, Vergleichen & Beschreiben, Zahlen
im Satz, Gefühle & Meinungen, Reisen & Verkehr, Feste & Traditionen, Arbeit &
Schule, Ganze Sätze.

**Sektion 6 · Einkaufen & Essen gehen** (4 Levels): Einkaufen & Orte, Im
Restaurant: ankommen, Im Restaurant: essen & zahlen, Essen gehen & Mengen.

**Sektion 7 · Bosnien & Herkunft** (3 Levels): Bosnische Küche, Länder &
Herkunft, Nationalitäten & Sprachen.

**Sektion 8 · Menschen & Kultur** (2 Levels): Vorstellen & Kennenlernen,
Musik, Glaube & Gastfreundschaft.

**Sektion 9 · Amt & Verträge** (6 Levels): Höflich & Formell, Amt & Behörde,
Bank & Geld, Wohnung & Hauskauf, Arbeitsvertrag & Bewerbung, Arzt &
Versicherung.

Jedes Level nennt unter „Baut auf“, welche früheren Levels es voraussetzt.
Daraus kommen die Wiederholungsfragen im Test.

Regeln:

- Nur Level 1 ist am Anfang offen. Alle anderen sind gesperrt (🔒). Eine
  Sektion geht auf, sobald das letzte Level der vorherigen bestanden ist.
- Jedes Level hat einen **Level-Test** mit 10 Fragen: bis zu 3 Grammatik-
  Aufgaben, 3 Wiederholungsfragen aus den Levels unter „Baut auf“, der Rest
  aus den Wörtern des Levels. Ab 8 richtigen Antworten ist das Level bestanden
  (✓) und das nächste geht auf.
- Der Test ist erst freigeschaltet, wenn der Balken des Levels bei mindestens
  80 % steht.
- Fragen sind gemischt: Deutsch zu Bosnisch, Bosnisch zu Deutsch, Wörter
  selbst schreiben und (wo vorhanden) Grammatik-Aufgaben. Im Test kann nichts
  übersprungen werden. Beim Schreiben zählt eine Antwort ohne Sonderzeichen
  (z. B. „noc“ statt „noć“) als richtig, mit Hinweis.
- Das Level „Ganze Sätze“ enthält keine neuen Wörter. Jeder Satz ist aus Wörtern
  der vorherigen Levels zusammengesetzt.
- Zum Ausprobieren ohne Sperre `?alle=1` an die Adresse hängen, also zum
  Beispiel `http://localhost:8099/?alle=1`. Dann sind alle Levels
  anklickbar.

Der Fortschritt (gelernte Wörter, bestandene Levels, gelesene Geschichten,
Lerntage, Leben) liegt im Speicher des Geräts unter `zmaj_stand`. Jedes Gerät
hat seinen eigenen; auf ein zweites kommt er nur über eine Sicherungsdatei.

## Grammatik

16 Levels haben eine **Grammatik-Erklärung**, die sich im Level aufklappen
lässt: eine kurze Erklärung mit Tabelle, zum Beispiel alle Endungen eines
Falls. Die dazugehörigen Übungsaufgaben kommen in der Lektion und im
Level-Test dran, mit Tipp bei Fehlern. Die Lektionen stehen in `grammatik.py`.

## Der Geschichten-Pfad: 12 Geschichten

Die Geschichten sind wie Levels aufgebaut und werden von vorn nach hinten
schwerer:

| Nr. | Titel              | Stufe           | Passt zu Level          |
|-----|--------------------|-----------------|-------------------------|
| 1   | Mira i Rex         | Kinderbuch      | Farben                  |
| 2   | Naša kuća          | Kinderbuch      | Zuhause                 |
| 3   | Moja porodica      | Einfach         | Familie                 |
| 4   | Na pijaci          | Einfach         | Einkaufen & Kleidung    |
| 5   | Moj dan            | Einfach         | Tagesablauf             |
| 6   | U gradu            | Mittel          | Präpositionen           |
| 7   | Jučer              | Mittel          | Vergangenheit           |
| 8   | Put u Bosnu        | Mittel          | Reisen & Verkehr        |
| 9   | Pismo nani         | Fortgeschritten | Zukunft & Pläne         |
| 10  | Na općini          | Amtssprache     | Amt & Behörde           |
| 11  | Kupujemo kuću      | Amtssprache     | Wohnung & Hauskauf      |
| 12  | Razgovor za posao  | Amtssprache     | Arbeitsvertrag & Bewerbung |

Regeln: Nur die erste Geschichte ist offen. Eine Geschichte gilt als gelesen,
wenn alle Fragen zum Text richtig beantwortet sind. Dann öffnet sich die
nächste. Jedes Wort im Text lässt sich antippen und zeigt die Übersetzung, die
ganze Übersetzung kann eingeblendet werden, „Vorlesen“ nutzt die
Computerstimme. Gelesene Geschichten bleiben offen. Mit `?alle=1` sind auch
hier alle Geschichten frei.

Die Geschichten und das Wörterbuch stehen in `geschichten.py`. Fehlt ein Wort
aus einem Geschichtentext im Wörterbuch, meldet das `start.py` beim Start,
und ein Test schlägt fehl. Die Prüfung selbst steht in `inhalt.py`
(`fehlende_woerter()`).

## Die Lektion (wie bei Duolingo)

In einem Level gibt es nur „Lektion starten“ und den Level-Test. Eine Lektion
mischt zufällig alle Aufgabenarten:

| Aufgabe          | Was passiert                                                        |
|------------------|---------------------------------------------------------------------|
| Neues Wort       | Wort mit Übersetzung und Ton, nur anschauen (zählt nicht).          |
| Auswahl          | Deutsch → bosnisch oder bosnisch → deutsch, vier Antworten.         |
| Schreiben        | Das bosnische Wort tippen. Ohne Sonderzeichen zählt es mit Hinweis. |
| Hören            | Wort anhören, richtige Schreibweise wählen. Überspringbar.          |
| Sprechen         | Wort ins Mikrofon sagen. Überspringbar. (Nur am PC in Chrome/Edge.) |
| Lückentext       | Satz mit Lücke ergänzen.                                            |
| Grammatik        | Aufgabe aus der Grammatik-Lektion des Levels, mit Tipp bei Fehlern. |

Regeln der Lektion:

- Etwa 10 Wortaufgaben plus 2 Lückentexte plus bis zu 2 Grammatik-Aufgaben.
  Neue Wörter werden vorher kurz vorgestellt. Ein Level braucht etwa drei
  Lektionen, das passt für ein Level pro Tag.
- Richtig beantwortet heißt: das Wort „sitzt“ und füllt den Balken. Falsch
  beantwortete Aufgaben kommen am Ende der Lektion noch einmal.
- Übersprungene Aufgaben (Hören, Sprechen) bringen keinen Fortschritt.
- Bei jeder Antwort gibt es einen Richtig- oder Falsch-Ton, abschaltbar in
  den Einstellungen (⚙).
- Ab 80 % Balken wird der Level-Test frei. Erst der bestandene Test öffnet das
  nächste Level. Die Grammatik-Erklärung und die Wortliste des Levels sind
  jederzeit aufklappbar.

## Leben

Die App hat 5 Leben, sie gelten für die ganze App. Jede falsche Antwort in
einer Lektion kostet ein Leben. Übersprungene Aufgaben und der Level-Test
kosten nichts. Bei 0 Leben wird die Lektion abgebrochen, richtig gelernte
Wörter bleiben gespeichert. Alle 120 Minuten wächst ein Leben nach, die
Anzeige oben zeigt die Wartezeit. Solange kann man Geschichten lesen und die
Grammatik-Erklärungen anschauen.

Die Wartezeit steht in `web/index.html` in der Zeile
`LEBEN_NACHFUELLEN_MIN = 120` und lässt sich dort ändern.

**Vollversion:** Sie sitzt im Lernstand als `"premium": true` und gibt
unbegrenzte Leben und keine Werbung. Einen Weg, sie zu **kaufen**, gibt es
noch nicht – dafür fehlt Google Play Billing, das steht in der Hülle nicht
drin (siehe „Werbung, Vollversion und Laden“). Zum Ausprobieren: eine
Sicherung speichern, in der Datei `"premium": false` auf `true` ändern,
wieder einlesen. Im Testmodus (`?alle=1`) sind die Leben ebenfalls
unbegrenzt.

## Werbung, Vollversion und Laden

Drei Dinge hängen hier zusammen, und sie stehen heute unterschiedlich weit:

- **Werbung** ist eingebaut und läuft. Auf dem Handy zeigt Google AdMob die
  Anzeigen, zurzeit mit Googles Testkennungen.
- **Die Vollversion** ist beschlossen und durchgerechnet, aber nicht
  gebaut – es fehlt die Bezahlung über Google Play.
- **Der Laden** läuft seit dem 15.09.2026. Er braucht keinen Store, weil
  dort nicht mit Geld bezahlt wird, sondern mit Münzen aus den
  Tagesaufgaben.

### Werbung

Zwei Arten: ganzseitig nach einer Lektion, und freiwillig bei leeren Leben
(Video ansehen, ein Leben zurück). Die Vollversion schaltet beides ab.

Wann etwas kommt, steht in `web/index.html`:

- `WERBUNG_AN = true` – Hauptschalter
- `WERBUNG_AB_LEKTION = 3` – die ersten Lektionen bleiben frei
- `WERBUNG_JEDE_X = 3` – danach jede dritte
- `WERBUNG_MAX_TAG = 6` – mehr kommt an einem Tag nicht
- `WERBUNG_LEBEN_LOHN = 1` – so viele Leben gibt ein freiwilliges Video

Gezählt wird erst, wenn eine Anzeige auch wirklich lief. Eine, die nicht
kam, darf kein Tageskontingent verbrauchen.

**Auf dem Handy** übernimmt das Plugin `@capacitor-community/admob`. Geht
dabei irgendetwas schief, bleibt es aus und die App läuft weiter – eine
Lernapp, die wegen einer Anzeige nicht startet, wäre der schlechteste aller
Tauschhandel.

**Am PC** gibt es das Plugin nicht. Dort kommt weiter der **Platzhalter**:
ein Fenster, das sich genauso verhält (fünf Sekunden Wartezeit, dann
Schließen-Knopf), aber kein einziges Datum vom Gerät schickt. So lässt sich
die Stelle prüfen, an der Werbung säße, ohne Werbung zu laden.

### Vor der Veröffentlichung: drei Kennungen tauschen

Zurzeit laufen **Googles öffentliche Testanzeigen**. Die brauchen kein
Konto, kosten nichts und bringen nichts ein. Testanzeigen in einer
veröffentlichten App sind ein Regelverstoß, also vor dem ersten Hochladen an
diesen drei Stellen die echten Werte aus dem AdMob-Konto eintragen:

| Was | Wo | Steht dort jetzt |
|---|---|---|
| App-ID | `zmaj-android/android/app/src/main/res/values/strings.xml`, `admob_app_id` | `ca-app-pub-3940256099942544~3347511713` |
| Anzeigen-IDs | `web/index.html`, `ADMOB_ID` (`interstitial`, `belohnt`) | Googles Testkennungen |
| Testbetrieb | `web/index.html`, `ADMOB_TEST` | `true` → auf `false` |

Die App-ID muss dort stehen, auch wenn man sie nicht benutzt: Ohne den
Eintrag stürzt die App beim Start ab, sobald das Werbe-SDK dabei ist.

Die echten Kennungen (seit dem 20.09.2026) stehen in `admob_scharf.py`.
Eingetragen werden sie nicht von Hand, sondern mit diesem Skript – es
tauscht alle drei, legt `ADMOB_TEST` um und prüft danach nach, dass keine
Testkennung übrig geblieben ist. Wann das dran ist und was vorher laufen
muss, steht oben unter „Liegen bereit für den Build nach dem Test“.

### Die Einwilligung holt Google

Für AdMob in der EU reicht ein selbstgebautes Fenster nicht. Google verlangt
ein zertifiziertes CMP nach IAB-TCF – in der Praxis ihre eigene *User
Messaging Platform*. Die bringt ihr eigenes Fenster mit.

Deshalb ist die Reihenfolge beim Start: erst `admobStart()`, das Google
fragt, dann der Rest. Meldet sich das Plugin, tritt das eigene Fenster
zurück. Welche Anzeigen jemand bekommt, entscheidet danach Google anhand der
Antwort; die App setzt „nicht personalisiert“ nicht mehr selbst, sonst
regelten zwei Stellen dasselbe.

Sagt Google nein (`canRequestAds` ist falsch), wird das SDK gar nicht erst
gestartet. Es kommt dann keine Anzeige, und weil sich das Plugin nie
gemeldet hat, hält die App sich für den Browser: Sie zeigt im Anschluss
**ihr eigenes Einwilligungsfenster**. Das ist eine Frage zu viel – hier
gehört noch etwas nachgezogen (`einwilligungFragen()` in `web/index.html`
erkennt nur ein Plugin, das erfolgreich gestartet ist).

Verlangt Google einen Knopf zum Nachträglich-Ändern, steht er unter
*Einstellungen → Über die App → Werbung*.

**Das eigene Fenster** gibt es weiterhin, aber nur noch dort, wo es kein
Plugin gibt: am PC. Beide Antworten sind ein Klick und gleich groß –
„Ablehnen“ darf nach der DSGVO nicht umständlicher sein als „Zustimmen“. Die
Antwort liegt unter `zmaj_einwilligung`. Zum Anschauen `?einwilligung=1` an
die Adresse hängen.

### Der eine Schalter

Werbung, Einwilligungsfenster und der passende Abschnitt in der
Datenschutzerklärung hängen an **einer einzigen Zeile**:

```python
# sprachen.py
WERBUNG_LAEUFT = True
```

- **True** (so steht es heute) – echte Werbung, die Einwilligung wird
  eingeholt, und Abschnitt 6 der Datenschutzerklärung nennt Google AdMob als
  Werbepartner, die Werbe-ID, die Einwilligung nach Art. 6 Abs. 1 lit. a
  DSGVO und den Widerruf.
- **False** – die App zeigt nur den Platzhalter, kein Datum verlässt das
  Gerät, kein Einwilligungsfenster. In der Datenschutzerklärung steht unter
  Abschnitt 6 „keine Werbenetzwerke“.

Der Schalter wird durchgereicht: `sprachen.py` → `inhalt.lade_daten()` →
`web/inhalt/<code>.json` → `web/index.html` (`WERBUNG_ECHT`). Deshalb **nur
diese eine Stelle anfassen** – so können Text und Verhalten nicht
auseinanderlaufen. Beide Fassungen von Abschnitt 6 stehen in allen acht
Sprachen unter `set.dsgvo_werbung_aus` und `set.dsgvo_werbung_an`.

Nach einer Änderung `inhalt_bauen.py` laufen lassen, sonst steht in den
fertigen Inhaltsdateien noch der alte Wert.

### Was im Play-Konto dazugehört

1. `seite_bauen.py` laufen lassen und die Dateien aus `github-seite` neu
   hochladen, damit die öffentliche Datenschutzerklärung dasselbe sagt wie
   die App.
2. Unter **Werbe-ID** die Erklärung auf **„Ja“** stellen. Das Google Mobile
   Ads SDK bringt die Berechtigung `com.google.android.gms.permission.AD_ID`
   selbst mit und führt sie automatisch mit dem Manifest zusammen – die App
   benutzt die Werbe-ID dann, ob man sie einträgt oder nicht. Ein „Nein“
   wäre eine Falschangabe.
3. Unter **Datensicherheit** „Geräte- oder andere IDs“ ergänzen und bei den
   betroffenen Punkten „geteilt“ auf Ja setzen.

### Vollversion: die Preise

Entschieden am 19.09.2026 und **eingebaut**: In der Android-Hülle steckt
`ZmajAbo.java` mit der Google Play Billing Library 9.1.0. Ein Abo
`vollversion` mit zwei Basisplänen `monat` (P1M) und `jahr` (P1Y) – ein
Produkt mit zwei Plänen, nicht zwei Produkte, sonst geht der Wechsel von
Monat auf Jahr nicht sauber.

Das Jahresabo ist deutlich günstiger als zwölf Monatszahlungen, damit es
sich für den Nutzer lohnt.

**Die Preise stehen bewusst in keiner Datei** – weder hier in der App noch
in den Store-Beschreibungen. Sie kommen zur Laufzeit von Google über
`getFormattedPrice`. Das ist keine Bequemlichkeit: Googles
Zahlungsrichtlinie verlangt, dass der Preis in der App dem im Kauffenster
entspricht, und in 177 Ländern mit eigenen Währungen und Steuersätzen kann
das keine fest eingetippte Zahl leisten. Die Tabelle oben ist nur die
Rechnung dahinter, damit sie nicht noch einmal gemacht werden muss.

Was noch fehlt, liegt allein in der Play Console: das Produkt anlegen und
**aktivieren**. Bis dahin antwortet Google auf die Preisabfrage mit OK und
einer leeren Liste, und der Vollversion-Block blendet sich still aus.

Beides sind **Abos**, keine Einmalkäufe. Angelegt werden sie in der Play
Console unter *Monetarisierung → Produkte → Abos*, und bezahlt wird
ausschließlich über Google Play – eigene Bezahlwege sind dort verboten.
Google zieht Steuer und Anteil selbst ab, es muss nichts abgeführt werden.

### Münzen und Laden

Der Laden ist fertig und läuft. Er sitzt im dritten Reiter der Startseite,
**🛒 Laden**, neben Lernpfad und Geschichten. Oben steht der Kontostand, dann
kommen zwei Gruppen Ware.

**10 Münzen pro geschaffter Tagesaufgabe.** Drei Aufgaben am Tag, also
höchstens 30 Münzen täglich, realistisch eher 15 bis 20.

Gruppe eins heißt **„Für dich“**. Was man hier kauft, ist danach verbraucht:

| Ware | Preis | bei 30 Münzen am Tag | kaufbar, wenn |
|---|---|---|---|
| Herz auffüllen | 100 | gut drei Tage | ein Leben fehlt und die Leben nicht ohnehin unbegrenzt sind |
| Serienschutz | 300 | zehn Tage | weniger als zwei Schutz vorhanden sind |

Gruppe zwei heißt seit dem 15.09.2026 **„Accessoires für Zmaj“**; vorher stand
dort „Für Zmaj – einmal gekauft, bleibt es“. Das sind vier Kleidungsstücke für
den Drachen, jedes nur einmal zu kaufen:

| Ware | Preis | bei 30 Münzen am Tag | Beschreibung in der App |
|---|---|---|---|
| Brille | 800 | knapp vier Wochen | „Eine runde Lesebrille.“ |
| Kopfhörer | 1200 | knapp sechs Wochen | „Zum Mithören beim Lernen.“ |
| Mütze | 1500 | gut sieben Wochen | „Eine rote Wintermütze mit Bommel.“ |
| Krone | 2500 | knapp drei Monate | „Gold mit roten Steinen.“ |

Gekauftes wird sofort angezogen. Danach steht statt des Preises ein Knopf
**„Tragen“** beziehungsweise **„Abnehmen“**: Ein Tipp auf ein anderes Stück
zieht dieses an, ein zweiter Tipp auf dasselbe zieht es wieder aus. Der Drache
trägt **immer nur ein Stück** – jede Kombination wäre eine eigene
Animationsdatei, und es gibt je eine Datei pro Stück (`zmaj-brille.json`,
`zmaj-hut.json`, `zmaj-kopfhoerer.json`, `zmaj-krone.json`) plus `zmaj.json`
ohne alles. Nach jedem Wechsel lädt die App die Animation neu.

Gekauft und getragen sind zwei verschiedene Dinge. **Was dir gehört**, steht
als `besitz` im Lernstand und wandert mit einer Sicherung auf ein anderes
Gerät. **Was der Drache gerade anhat**, merkt sich das Gerät für sich unter
`zmaj_getragen` und wandert nicht mit – wie Ton, Sprache und Stimme. Am PC
kann er also die Krone tragen und am Handy die Mütze.

Das Herz ist mit Absicht teuer: Leben für Kleingeld nachzukaufen würde
„unbegrenzte Leben" als Argument für die Vollversion entwerten.

Der Schutz kostet dreimal so viel wie ein Herz, weil er ungleich mehr rettet.
Er wächst weiterhin alle zehn Tage von selbst nach – gekauft wird also nicht
statt, sondern zusätzlich, bis höchstens `SCHUTZ_MAX`. Deshalb bleibt die
Lernserie ehrlich: Ein geschenkter Schutz pro Lerntag hätte sie zur Lüge
gemacht (die Anzeige zeigte „30 Tage" bei 15 Lerntagen), ein gekaufter alle
zehn bis zwanzig Tage tut das nicht.

**Die Vollversion gibt es nicht für Münzen**, und das ist keine Preisfrage.
Sie soll das Abo sein, sonst hätte das Abo kein Argument mehr. 

Im Lernstand stehen nicht Münzen, sondern zwei Summen, die beide nur wachsen:
`muenzen_ges` (jemals verdient) und `muenzen_aus` (jemals ausgegeben). Der
Kontostand ist die Differenz. Das stammt aus der Zeit mit Server, wo beim
Speichern pro Feld der grössere Wert gewann – so konnte ein altes
Browserfenster weder Münzen erfinden noch einen Kauf rückgängig machen. Ohne
Server bleibt davon nur die Buchführung: Eine eingelesene Sicherung setzt
beide Summen auf ihren Stand zurück, wie alles andere auch.

## App-Icon

Überall dasselbe Symbol: die bosnische Flagge in einem abgerundeten Quadrat.
Im Browser-Tab, in der Kopfzeile und auf der Desktop-Verknüpfung.

Die Dateien liegen fertig im Ordner: `web/icon.ico` (Verknüpfung, sieben
Größen von 16 bis 256 Pixel), `web/icon-256.png` und `web/flagge.png`. Wer
ein anderes Symbol will, tauscht diese drei Dateien aus.

Für den Play Store braucht es andere Maße. `grafiken_bauen.py` zeichnet die
Flagge dafür neu: quadratisch, 512 × 512 und **ohne** runde Ecken, weil
Google selbst abrundet – sonst wäre es doppelt gerundet. Das Ergebnis liegt
in `store/icon-512.png`, daneben der breite Banner `feature-1024x500.png`.

Windows merkt sich Symbole. Zeigt der Desktop noch das alte, hilft ein
Rechtsklick auf den Desktop und „Aktualisieren“, sonst einmal ab- und anmelden.

## Lernserie und Serienschutz

Jeder Tag mit einer fertigen Lektion, einem bestandenen Test oder einer
gelesenen Geschichte zählt. Oben auf der Startseite steht, wie viele Tage in
Folge gelernt wurde und ob heute schon etwas gemacht ist.

**Serienschutz (❄)** rettet die Serie, wenn ein Tag ausfällt – wie der
Streak Freeze bei Duolingo, nur dass man ihn nicht kaufen muss:

- Man startet mit **1 Schutz**, höchstens **2** hat man gleichzeitig.
- Alle **10 Tage** wächst einer nach. Die Startseite zeigt, wie lange es noch dauert.
- Beim nächsten Öffnen der App schaut sie nach, ob Tage fehlen. Fehlt einer,
  wird er automatisch mit einem Schutz abgedeckt und die Serie läuft weiter.
  Fehlen zwei Tage, kostet das zwei Schutz.
- Reicht der Vorrat nicht, wird **nichts** verbraucht – die Serie ist dann weg,
  der Schutz bleibt für das nächste Mal liegen.
- Ein geschützter Tag zählt nicht als Lerntag. Die Serie reißt nicht ab,
  die Zahl steigt an diesem Tag aber auch nicht.

Die Zahlen stehen in `web/index.html` (`SCHUTZ_MAX = 2`, `SCHUTZ_TAGE = 10`),
nur dort. (Bis zum 04.10.2026 standen sie noch einmal im Kontoteil von
`start.py`; den gibt es nicht mehr.) Im Lernstand stehen die geretteten Tage unter `frost`
und der Vorrat unter `schutz`.

Lektion abgebrochen, weil die Leben alle waren? Der Tag zählt trotzdem als
Lerntag. Wer übt, hat geübt – auch wenn die Lektion nicht fertig wurde.

## Tagesaufgaben

Die App stellt **drei Aufgaben pro Tag**, jeden Tag neue. Fuer jede geschaffte
gibt es 10 Muenzen, also hoechstens 30 am Tag.

Es gibt neun moegliche Aufgaben: Aufgaben beantworten, Antworten richtig,
Lueckensaetze, Hoeruebungen, neue Woerter, Lektionen abschliessen, eine Lektion
ohne Fehler, eine Geschichte fehlerfrei, und Minuten lernen. Welche drei dran
sind, entscheidet `zieh()` in `web/index.html`.

**Nichts davon wird gespeichert.** Welche drei Aufgaben heute gelten, rechnet
die App jedes Mal neu aus der Gerätekennung und dem Datum aus. Deshalb kommen
beim Neuladen und im zweiten Browserfenster zwingend dieselben drei heraus -
man kann sich also keine leichten erwuerfeln.

Die Gerätekennung (`zmaj_id`) ist eine Zufallszahl, die beim ersten Start
einmal angelegt wird. Vorher stand an dieser Stelle der Profilname; ohne
Konten hiesse jeder gleich, und alle bekaemen jeden Tag dieselben drei.
Zwei Geraete ziehen deshalb verschiedene Aufgaben, auch nach einer Sicherung
- die Kennung wandert nicht mit.

Damit das aufgeht, darf in die Auslosung nur eingehen, was sich im Lauf des
Tages **nicht mehr aendert**: die Gerätekennung, das Datum, die Lerntage
*vor* heute, ob das Geraet etwas vorlesen kann, und wie viele Woerter man
kennt. Nicht `passed`, nicht `read`, nicht das aktuelle Level - sonst
staenden nach der ersten Lektion drei andere Aufgaben da und der Fortschritt
waere weg.

Es gibt drei Schwierigkeitsstufen, die sich nach den bisherigen Lerntagen
richten (ab 5 Tagen Stufe 2, ab 21 Stufe 3). Eine Aufgabe wird nicht
ausgelost, wenn sie an dem Tag unmoeglich waere: Hoeruebungen nur, wenn sich
ueberhaupt etwas hoeren laesst (Aufnahmen oder Computerstimme - seit es die
Tonspur gibt, ist das immer der Fall), neue Woerter nur solange es welche
gibt, "ohne Fehler" erst ab Stufe 2. Ausserdem ist immer mindestens eine
Aufgabe dabei, die auch mit null Herzen geht.

Gezaehlt wird in `tagwerk`, einer Zuordnung Tag -> Zaehler:

```json
"tagwerk": { "2026-09-14": { "auf": 23, "ric": 18, "zeit": 640 } },
"muenzen_ges": 120,
"muenzen_aus": 100,
"besitz": ["hut"]
```

Tage ohne Uebung stehen gar nicht erst drin. `zeit` ist die Lernzeit in
Sekunden, alles andere sind Stueckzahlen.

Obergrenzen gibt es keine: Die standen nur im alten Kontoserver in
`start.py` (400 Tage, 500 je Stueckzaehler, sechs Stunden) und sind mit ihm
am 04.10.2026 verschwunden. `tagwerk` waechst ungebremst. Bei einer kurzen Zeile je Lerntag faellt das
auf Jahre hinaus nicht ins Gewicht.

### Lernzeit

Die Uhr laeuft nur, solange wirklich eine Lektion, ein Test oder eine
Geschichte offen ist - und nur, solange der Bildschirm an ist. Wird der Tab
gewechselt oder das Handy gesperrt, haelt sie an (`visibilitychange`).
Alle zehn Sekunden wird gutgeschrieben, damit die Zeit auch dann gespeichert
ist, wenn die App mittendrin zugeht.

Ehrlich dazu: Wer eine Lektion offen liegen laesst und den Bildschirm anhat,
sammelt Zeit, ohne zu lernen. Das ist bewusst so entschieden - die App ist
fuer die eigene Familie gebaut, nicht gegen Betrueger.

### Ohne Strafe

Wird eine Aufgabe nicht geschafft, passiert **nichts**: keine Meldung, keine
rote Farbe, kein trauriger Drache. Die Stimmungen `cry`, `sad` und `no` sind
fuer Tagesaufgaben tabu.

## Sprachen

Gelernt wird immer Bosnisch. Die App kann aber in acht Sprachen mit dem Nutzer
reden: Deutsch, Englisch, Türkisch, Schwedisch, Niederländisch, Norwegisch,
Dänisch und Französisch. Umschalten geht in den Einstellungen ganz oben. Das
Gerät merkt sich die Wahl unter `zmaj_sprache`.

Zwei Dateien gehören dazu:

- **`sprachen.py`** – alle Texte der Oberfläche (Knöpfe, Hinweise, Meldungen,
  Rechtstexte), 335 Stück je Sprache.
- **`uebersetzungen.py`** – die Lerninhalte: Sektionen, Level-Namen, Tipps,
  die 1664 Wörter, die Lückentexte (290 Sätze in `vokabeln.py`, davon 285
  verschiedene deutsche Texte), die Grammatik-Erklärungen samt Tabellen,
  Übungen und Tipps, die 12 Geschichten mit ihren Fragen und das
  Wörterbuch. 2975 Einträge je Sprache (1664 Wörter + 1311 Texte).

**Alle sieben Übersetzungen sind vollständig.** `start.py` meldet beim
Start – und `inhalt_bauen.py` prüft dasselbe noch einmal, bevor es die
Dateien für die App schreibt:

```
Sprachen: Deutsch (de), English (en), Türkçe (tr), Svenska (sv),
          Nederlands (nl), Norsk bokmål (nb), Dansk (da), Français (fr)
  en: Oberfläche vollständig · Lerninhalte 2975 von 2975 (100 %)
  tr: Oberfläche vollständig · Lerninhalte 2975 von 2975 (100 %)
  sv: Oberfläche vollständig · Lerninhalte 2975 von 2975 (100 %)
  nl: Oberfläche vollständig · Lerninhalte 2975 von 2975 (100 %)
  nb: Oberfläche vollständig · Lerninhalte 2975 von 2975 (100 %)
  da: Oberfläche vollständig · Lerninhalte 2975 von 2975 (100 %)
  fr: Oberfläche vollständig · Lerninhalte 2975 von 2975 (100 %)
```

Ganz oben in `uebersetzungen.py` steht außerdem die Liste **`GLEICH`**: 414
Texte, die in jeder Sprache gleich bleiben – bosnische Beispiele aus den
Grammatik-Tabellen, Antwortmöglichkeiten wie „Gdje / Kuda / Kada“, Namen und
Zahlen. Die müssen nie übersetzt werden und tauchen in keiner Arbeitsliste auf.

**Was fehlt, bleibt auf Deutsch stehen.** Nichts geht kaputt, wenn eine
Sprache nur halb fertig ist.

### Weiter übersetzen

Einen Befehl `python` gibt es auf diesem Rechner nicht – gemeint ist immer der
Python aus Thonny. In der Eingabeaufforderung also mit vollem Pfad:

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" start.py --fehlende en

schreibt `fehlende_en.txt` mit allem, was in dieser Sprache noch fehlt – schon
im richtigen Format. Ausfüllen und den Block nach `uebersetzungen.py` kopieren.
Die Wörter stehen unter `"woerter"` (Schlüssel ist das **bosnische** Wort),
alles andere unter `"texte"` (Schlüssel ist der **deutsche** Text). Ein Wort
darf auch unter `"texte"` stehen: Zuerst wird unter `"woerter"` nachgesehen,
und erst wenn dort nichts steht, unter der deutschen Bedeutung. Heute liegen
alle Übersetzungen unter `"texte"`, `"woerter"` ist überall leer.

Danach **`inhalt_bauen.py`** laufen lassen, sonst sieht die App die neuen
Texte nicht.

### Eine neue Sprache dazunehmen

1. In `sprachen.py` eine Zeile in `SPRACHEN` ergänzen, zum Beispiel
   `{"code": "sv", "name": "Svenska", "flagge": "…"}`.
2. Im selben File einen Block `"sv": { ... }` in `TEXTE` anlegen.
3. In `uebersetzungen.py` einen Block `"sv": {"woerter": {}, "texte": {}}`.
4. In `web/index.html` in der Tabelle `ZITAT` das Anführungszeichen-Paar der
   neuen Sprache eintragen (siehe unten).

Kroatisch und Serbisch braucht es nicht – wer die spricht, versteht Bosnisch
ohnehin. Slowenisch wäre die kleinste Diaspora und lohnt sich nicht.

### Worauf beim Übersetzen zu achten ist

- **Keine zwei Wörter dürfen dieselbe Übersetzung bekommen.** Sonst hat eine
  Auswahlaufgabe zwei richtige Antworten. Im Türkischen musste deshalb
  „Markt“ zu `pazar yeri` werden (weil `Pazar` schon Sonntag heißt) und
  „Herd“ zu `mutfak ocağı` (weil `Ocak` schon Januar heißt). Im Schwedischen
  musste „Ehefrau“ zu `hustru` werden (weil `fru` schon die Anrede Frau ist)
  und das Verb „fragen“ zu `att fråga` (weil `fråga` auch die Frage ist). Im
  Französischen musste „neu“ zu `nouveau` werden (weil `neuf` schon neun
  heißt) und „zu Mittag essen“ zu `prendre le déjeuner` (weil `déjeuner` schon
  das Mittagessen ist).
- **Jede Sprache hat ihre eigenen Anführungszeichen.** In den Grammatik-
  Erklärungen setzt die App fett, was dazwischen steht. Welches Paar eine
  Sprache benutzt, steht in `web/index.html` in der Tabelle `ZITAT`:

  | Sprache | Paar | Beispiel |
  |---------|------|----------|
  | Deutsch | „ … “ | „Gdje stanuješ?“ |
  | Englisch, Türkisch | “ … ” | “Gdje stanuješ?” |
  | Schwedisch | ” … ” | ”Gdje stanuješ?” |
  | Niederländisch | ‘ … ’ | ‘Gdje stanuješ?’ |
  | Norwegisch, Französisch | « … » | « Gdje stanuješ? » |
  | Dänisch | » … « | »Gdje stanuješ?« |

  Wer eine neue Sprache anlegt, trägt das Paar dort ein – sonst bleibt die
  Fettschrift in den Erklärungen aus.
- **Französisch braucht ein geschütztes Leerzeichen** vor `?`, `!`, `:`, `;`
  und `»` sowie nach `«`. Sonst rutscht das Zeichen beim Umbruch in die
  nächste Zeile. In den Dateien steht dafür das unsichtbare Zeichen U+00A0
  statt eines normalen Leerzeichens. Die bosnischen Beispielsätze behalten ihre eigene
  Zeichensetzung: `« Gdje stanuješ? »`, nicht `« Gdje stanuješ ? »`.
- **Bei Übungen gehören Frage, alle Antwortmöglichkeiten und die richtige
  Antwort zusammen.** Weil alle über dieselbe Tabelle laufen, bleibt das von
  selbst stimmig – aber nur, wenn man eine Antwortmöglichkeit nicht einzeln
  anders übersetzt.
- **Vergleiche mit dem Deutschen anpassen.** Wo die deutsche Erklärung sagt
  „anders als im Deutschen“, steht in der englischen Fassung der Vergleich mit
  dem Englischen und in der türkischen der mit dem Türkischen.
- **Amtsbegriffe im Internet nachschlagen.** Jedes Land hat seine eigenen
  Wörter, und die kann man nicht raten. Grundbuch heißt in Schweden
  `fastighetsregistret`, in Norwegen `grunnboka`, in Dänemark `tingbogen`, in
  den Niederlanden `kadaster (openbare registers)` und im französischen
  Sprachraum `registre foncier`. Die Überweisung zum Facharzt heißt auf
  Französisch `lettre d'adressage`, auf Schwedisch `remiss`, auf Norwegisch
  und Dänisch `henvisning`, auf Niederländisch `verwijsbrief`.

**Wichtig:** Diese Übersetzungen sind nicht von Muttersprachlern. Vor der
Veröffentlichung sollte jede Sprache jemand durchsehen, der sie wirklich
spricht – so wie du das Bosnische prüfst. Dafür werden noch
Muttersprachler gesucht (Issues mit dem Label `translation`).

### Was die Prüfskripte abdecken

Zwei Dinge werden bei jeder Änderung automatisch geprüft und waren zuletzt
sauber:

- Jedes der 1728 Wörter hat eine eigene Fortschritts-Kennung.
- In keiner Sprache hat ein Level zwei Wörter mit derselben Bedeutung, und
  keine Übungsfrage hat zwei gleiche Antwortmöglichkeiten.

Was im Wörterbuch zusammenfällt (`posao` und `rad` heißen beide „Arbeit“,
`se` und `sebi` beide „sich“), fällt schon im Deutschen zusammen und ist kein
Fehler – das Wörterbuch zeigt nur an, es fragt nichts ab.

## Wie der Fortschritt gespeichert wird

Im Lernstand steht unter `gewusst` nicht das bosnische Wort allein, sondern
**`bedeutung:wort`**:

```json
"gewusst": ["hundert:sto", "tisch:sto", "danke:Hvala"]
```

Der Grund: dasselbe bosnische Wort kann zwei Bedeutungen haben. `sto` ist die
Zahl hundert und der Tisch, `oko` das Auge und „um herum“. Vorher merkte sich
die App nur `sto` – wer die Zahl konnte, bei dem galt auch das Möbelstück als
gelernt, und Level 9 startete bei 4 % statt bei 0 %. Dasselbe galt für `malo`,
`oko`, `prije`, `more` und `Htio bih`. Jetzt startet jedes der 65 Levels bei
0 %, und man sieht in einer Sicherung auf einen Blick, welche Bedeutung
gemeint ist.

Die Kennung wird immer aus der **deutschen** Bedeutung gebaut, bevor übersetzt
wird. Sie ist deshalb in jeder Sprache dieselbe – der Fortschritt bleibt beim
Sprachwechsel erhalten.

Änderst du später die **deutsche** Bedeutung eines Wortes, ändert sich seine
Kennung, und es gilt wieder als ungelernt. Bei einzelnen Wörtern ist das
egal; bei einer größeren Umbenennung sag Bescheid.

## Wörter ändern oder hinzufügen

Alles steht in `vokabeln.py`. In Thonny öffnen, ändern, speichern – und dann
**`inhalt_bauen.py`** laufen lassen, sonst liest die App weiter den alten
Stand aus `web/inhalt`. Danach im Browser neu laden (F5).

Ein Wort sieht so aus:

```python
{"de": "Kaffee", "bs": "kahva"},
```

Links Deutsch, rechts Bosnisch, am Ende ein Komma. Eine neue Zeile nach diesem
Muster in den passenden Block einfügen, fertig.

Ein Lückentext sieht so aus:

```python
{"kat": "essen", "text": "Jedna ___, molim.", "answer": "kahva", "de": "Einen Kaffee, bitte."},
```

`___` ist die Lücke, `answer` das fehlende Wort, `kat` die Kategorie.

Ein neues Level ist ein ganzer Block:

```python
{"id": "tiere", "label": "Tiere", "sektion": "alltag", "tipp": "Haustiere und Bauernhof.",
 "baut_auf": ["farben", "zuhause"],
 "words": [
    {"de": "Pferd", "bs": "konj"},
    {"de": "Kuh",   "bs": "krava"},
]},
```

`id` ist ein kurzer Name ohne Leerzeichen und Umlaute. Die Stelle in der Liste
bestimmt die Levelnummer. `sektion` ist `alltag`, `saetze` oder `amt` (siehe
`SEKTIONEN` oben in der Datei). `baut_auf` nennt die Levels, aus denen der
Test seine Wiederholungsfragen zieht. Das Level erscheint automatisch im
Lernpfad.

Die Prüfung auf doppelte Wörter, fehlende Felder und Sätze ohne Lücke steckt
in `inhalt.py` (`pruefe_vokabeln()`). `start.py` meldet sie beim Start, und
die Tests laufen sie bei jedem `pytest`. `inhalt_bauen.py` prüft
etwas anderes: dass jede Sprache Inhalt hat, dass alle acht gleich viel
enthalten und dass der bosnische Teil nirgends mitübersetzt wurde.

## Der Weg zur Android-App

Aus derselben `web/index.html`, die am PC im Browser läuft, wird die App im
Play Store. Dazwischen steht **Capacitor**: eine Hülle, die die Seite in ein
Android-Projekt packt und ihr ein paar Geräte-Funktionen dazugibt (Teilen,
Dateien, Zurück-Taste, AdMob).

### Wo was liegt

Die Hülle liegt **nicht** in diesem Projekt, sondern daneben, als eigenes
privates Repository `zmaj-lernapp/zmaj-huelle`. Der Ordner heißt
`zmaj-android` (so am eigenen Rechner) oder `zmaj-huelle` (frischer
`git clone`); `huelle.py` findet beide, ein anderer Ort geht über die
Umgebungsvariable `ZMAJ_HUELLE`.

Darin:

- `capacitor.config.json` – Name, appId und wie die Seite geladen wird
- `package.json` – die Plugins
- `www/` – hierhin wird `web/` kopiert, jedes Mal frisch
- `android/` – **das Gradle-Projekt. Dieser Ordner wird in Android Studio
  geöffnet, nicht der darüber.**

### Bauen

Ein Skript, ein Befehl:

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" app_bauen.py

`app_bauen.py` macht drei Dinge, in dieser Reihenfolge:

1. **Tonspur prüfen.** Es ruft `ton_pruefen.py` auf. Fehlt auch nur eine
   Aufnahme, bricht es ab und kopiert nichts. Ein halbes Paket soll niemand
   in die Hand bekommen.
2. **Kopieren.** `web/` nach `www/` der Hülle, vorher wird `www` geleert.
   Nicht mitkopiert werden die Probeaufnahmen (`_probe`), die Sicherungen
   von `index.html` (alles mit `.vor_` im Namen) und die LIESMICH-Dateien.
3. **`npx cap sync android`.** Damit landen die Dateien und die Plugins im
   Android-Projekt.

Am Ende steht der Pfad da, der in Android Studio zu öffnen ist. Dort dann
*Build → Generate Signed App Bundle*.

Vor dem Bauen daran denken: Hat sich am Inhalt etwas geändert, muss erst
`inhalt_bauen.py` laufen. `app_bauen.py` kopiert nur, es baut nichts neu.

### Zwei Werte, die nie wieder geändert werden dürfen

Beide stehen in `zmaj-android/capacitor.config.json`:

- **`appId` = `de.smartdragon.zmaj`.** Das ist die Kennung der App im Play
  Store. SmartDragon ist der Herausgebername – geprüft und frei. Künftige
  Apps bekommen `de.smartdragon.<app>`. Eine Änderung nach dem ersten
  Hochladen wäre im Store eine **komplett neue App**, ohne Bewertungen und
  ohne Installationen.
- **`androidScheme` = `https` mit `hostname` = `localhost`.** Daran hängt
  der Ursprung, unter dem der Browserspeicher liegt. Wird das geändert, ist
  der Lernstand **bei allen Nutzern** weg – er läge dann unter einer anderen
  Adresse, und niemand käme mehr heran.

Alles andere lässt sich später noch drehen.

### Die Plugins

| Plugin | Wofür |
|---|---|
| `@capacitor/app` | die Zurück-Taste und das Schließen der App |
| `@capacitor/filesystem` | die Sicherungsdatei schreiben |
| `@capacitor/share` | sie ans Teilen-Menü übergeben |
| `@capacitor/local-notifications` | die Lern-Erinnerung |
| `@capacitor-community/admob` | Werbung und Googles Einwilligungsfenster |
| `@capacitor-community/speech-recognition` | die Sprechaufgabe |
| `ZmajAbo` (eigenes, Java) | das Abo über Google Play Billing |
| `ZmajEinwilligung` (eigenes, Java) | liest Googles Einwilligung (IAB TCF) für die Werbung |
| `ZmajBewertung` (eigenes, Java) | Googles Bewertungsfenster |

Stand 04.10.2026, nachgesehen in `package.json` und
`android/app/src/main/java/de/smartdragon/zmaj/` der Hülle. Alle sind so eingebaut, dass ihr Fehlen nichts kaputt macht: Die App
fragt jedes Mal `window.Capacitor && window.Capacitor.Plugins`, und wo
nichts antwortet, nimmt sie den Weg für den Browser. Deshalb läuft dieselbe
Datei am PC weiter.

### Vor dem ersten Produktions-Build (nach dem 07.10.2026)

- Die Patch-Skripte in der Reihenfolge aus „Liegen bereit für den Build
  nach dem Test“, zuletzt `admob_scharf.py`.
- Die eigenen Geräte vorher in AdMob unter *Einstellungen → Testgeräte*
  eintragen (per Werbe-ID), sonst zählen eigene Klicks als ungültig.
- Zielgruppe in der Play Console bei **16+** lassen: Die Werbung läuft mit
  `maxAdContentRating: 'Teen'` und ohne Kennzeichnung als Kinder-App.
- `versionCode` in `android/app/build.gradle` erhöhen (Stand 02.10.2026: 89).

## Die öffentliche Seite

Google Play verlangt eine **öffentliche Adresse**, unter der die
Datenschutzerklärung ohne Anmeldung lesbar ist. In der App allein reicht
nicht.

`seite_bauen.py` macht aus den Rechtstexten in `sprachen.py` vier fertige
Dateien im Ordner `github-seite`:

| Datei | Was drinsteht |
|---|---|
| `index.html` | Startseite mit den Links |
| `datenschutz.html` | Datenschutzerklärung, alle acht Sprachen |
| `nutzungsbedingungen.html` | Nutzungsbedingungen, alle acht Sprachen |
| `konto-loeschen.html` | „Daten löschen“ – erklärt, dass es kein Konto gibt und wie man seinen Lernstand loswird. Google fragt im Data-Safety-Formular danach |

Die Seiten laden nichts von fremden Servern: keine Schriften, keine
Skripte. Ein Doppelklick öffnet sie auch ohne Internet zum Anschauen.

Hochgeladen werden sie zu GitHub Pages, geplante Adresse
`https://zmaj-lernapp.github.io/`. Schritt für Schritt steht das in
`github-seite/LIESMICH.txt`.

**Nach jeder Änderung an den Rechtstexten:** `seite_bauen.py` laufen lassen
und die Dateien neu hochladen. Sonst sagt die öffentliche Erklärung etwas
anderes als die App. Von Hand in den HTML-Dateien zu ändern lohnt nicht –
beim nächsten Lauf ist es weg.

## Bekannte Grenzen

- **Sprechen:** Die Aufgabenart erscheint nur, wenn der Browser
  Spracherkennung mitbringt **und** die Seite als sicher gilt. Am PC über
  `http://localhost:…` ist beides erfüllt, in Chrome und Edge. Die
  Android-WebView kennt die Spracherkennung nicht – in der App fehlt die
  Aufgabenart deshalb ganz. Sie fehlt still: Es gibt keine leere Stelle und
  keine Fehlermeldung, die Lektion zieht einfach andere Aufgaben.
- **Vorlesen in der App:** Die Android-WebView kennt auch die
  Computerstimme (`speechSynthesis`) meist nicht. Dass trotzdem alles
  vorgelesen wird, liegt allein an den 2153 Aufnahmen in `web/audio`.
- **Fremde Buchstaben:** Das bosnische Alphabet hat kein x, q, w und y. Die
  Computerstimme verschluckt sie sonst (aus „Rex“ wurde „Re“). Die App
  schreibt sie vor dem Vorlesen um: x wird ks, q wird k, w wird v, y wird j.
  Der angezeigte Text bleibt unverändert. `ton_bauen.py` macht beim Erzeugen
  der Aufnahmen genau dasselbe, damit beide Wege gleich klingen.
- **Aussprache:** Die Computerstimme des Browsers kann meist kein Bosnisch.
  Sie kommt nur noch zum Zug, wenn zu einem Text keine Aufnahme vorliegt;
  dann nimmt die App die beste verfügbare (bosnisch vor kroatisch vor
  serbisch) und zeigt in den Einstellungen eine Auswahl. **Microsoft Edge**
  hat echte bosnische Stimmen (Goran und Vesna), deshalb öffnet `start.py`
  die App in Edge, wenn es installiert ist.
- **Inhalte:** Die Vokabeln hat Claude vorgeschlagen, kein Muttersprachler.
  Bitte alles gegenprüfen.

## Die Tonspur

Alles, was die App vorlesen kann, liegt als fertige Tondatei in `web/audio`.
Welche Datei zu welchem Wort gehört, steht in **`web/audio/index.json`**. Die
App liest nur diese eine Datei; in den Ordner schaut sie nie hinein.

### Warum die Dateien nummeriert sind

Der naheliegende Weg wäre, die Datei genau so zu nennen wie das bosnische
Wort – `kahva.mp3`, `Dobar dan.mp3`. So stand es früher auch hier. Es
funktioniert nicht, und zwar aus drei Gründen:

- Windows erlaubt weder `?` noch `/` im Dateinamen. `Kako se zoveš?` und
  `Gladan sam / Gladna sam` lassen sich gar nicht erst anlegen.
- Die App schneidet Satzzeichen ab, bevor sie sucht. Eine Datei mit
  Fragezeichen im Namen fände sie also selbst dann nicht, wenn es sie gäbe.
- Die Geschichten werden am Stück vorgelesen. Ihr „Dateiname“ wäre der ganze
  Text – der längste hat über 500 Zeichen.

Deshalb heißen die Dateien **`w0001.mp3`, `w0002.mp3` …** für Wörter und
**`g01.mp3`, `g02.mp3` …** für Geschichten. Kurz, rein ASCII, auf jedem
Dateisystem erlaubt. Die Zuordnung macht `index.json`:

```json
{ "version": 1,
  "toene": [
    {"key": "kahva", "datei": "w0042.mp3",
     "text": "kahva", "stimme": "bs-BA-GoranNeural"}
  ] }
```

`key` ist genau das, wonach die App sucht: der Teil vor einem `" / "`,
getrimmt und kleingeschrieben – Satzzeichen bleiben stehen. Deshalb können
`Molim` („Bitte“) und `Molim?` („Wie bitte?“) getrennte Aufnahmen haben; die
App sucht erst den vollen Text und erst danach den um das Satzzeichen
gekürzten. Zwei Aufnahmen sind also möglich, aber nicht nötig.

Eine Nummer wird **einmal vergeben und nie wieder geändert**. Kommt ein Wort dazu, bekommt es die nächste freie; ein
gestrichenes hinterlässt eine Lücke, die nichts kostet. Dadurch bleiben
eingesprochene Dateien gültig, auch wenn sich `vokabeln.py` ändert.

### Was die App damit macht

Beim Start holt sie `audio/index.json` wie eine ganz normale Datei neben der
Seite – **nicht** über die Schnittstelle des Servers. Klappt das, kennt sie
die Tonspur; klappt es nicht, bleibt die Liste leer und nichts geht kaputt.

`speak()` nimmt zuerst die Aufnahme. Gibt es keine, oder lässt der Browser sie
nicht abspielen, fällt die App still auf die Computerstimme zurück. Davon
merkt der Nutzer nichts.

Der Hörknopf und die Aufgabenart „Hören“ hängen seit dem Umbau nicht mehr
allein an der Computerstimme: Es reicht, wenn Aufnahmen da sind. Das war der
eigentliche Grund für den Umbau – Dateien brauchen weder einen Server noch
eine Sprachausgabe im Gerät und funktionieren auch dort, wo es beides nicht
gibt.

### Die Töne erzeugen

Dafür gibt es zwei Skripte im Hauptordner. Einen Befehl `python` gibt es auf
diesem Rechner nicht – gemeint ist immer der Python aus Thonny. Ohne Zusatz
reicht es, die Datei in Thonny zu öffnen und F5 zu drücken; für `--probe` und
`--stimme` braucht es Thonnys Feld für Programmargumente oder die
Eingabeaufforderung mit dem vollen Pfad zu Thonnys `python.exe`.

    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_bauen.py --probe
    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_bauen.py --stimme bs-BA-GoranNeural
    "C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe" ton_pruefen.py

`--stimme` kann man sich sparen, sobald die gewählte Stimme in
`tts_zugang.json` unter `"stimme"` eingetragen ist; steht dort nichts und
fehlt der Zusatz, bricht das Skript mit einem Hinweis ab, statt irgendetwas zu
erzeugen.

**`ton_bauen.py`** schickt jedes Wort an einen Sprachdienst – Azure oder
Google, die Auswahl steht in der Zugangsdatei – und speichert die Antwort als
MP3. Mit `--probe` erzeugt es vorher **30 ausgesuchte Wörter** mit allen
Probestimmen nach `web/audio/_probe`: bosnische Eigenheiten wie `kahva`,
`hljeb`, `babo`, `amidža`, ijekavische Formen wie `mlijeko`, `dijete` und
`čovjek`, dazu die Laute č, ć, dž und đ. Genau daran hört man, ob eine Stimme
wirklich Bosnisch kann oder nur Kroatisch mit anderem Etikett. Erst hören,
dann der große Lauf – am besten vorspielen, ohne zu sagen, welche Stimme
welche ist.

Der große Lauf ist **abbruchsicher**: Was in `index.json` steht und als Datei
vorliegt, wird übersprungen. Ein zweiter Aufruf kostet also nichts, und ein
abgebrochener Lauf lässt sich einfach noch einmal starten. Insgesamt sind es
**2153 Aufnahmen** – 2141 Wörter und Lückensätze samt dem Probesatz aus den
Einstellungen und 12 Geschichten. Wörter werden etwas
langsamer gesprochen als die Geschichten.

**`ton_pruefen.py`** ist der Torwächter. Es benutzt dieselbe Sammel-Logik wie
`ton_bauen.py`, keine Kopie, und prüft fünf Dinge: ob jede Datei aus dem Index
wirklich da und groß genug ist (unter 800 Byte ist sie vermutlich stumm), ob
kein Dateiname doppelt vergeben wurde, ob zu jedem Wort aus `vokabeln.py` und
jeder Geschichte ein Ton existiert, ob Tondateien herumliegen, die in keinem
Index stehen, und ob jeder `key` noch zu seinem Text passt. Rückgabe 0 heißt:
vollständig. Vor jeder Weitergabe laufen lassen – am PC fällt ein fehlender
Ton nicht auf, am Handy schon.

**Zugang:** `ton_bauen.py` braucht `tts_zugang.json` neben sich, nach dem
Muster in `tts_zugang.BEISPIEL.json`. Diese Datei enthält einen Schlüssel und
bleibt auf diesem Rechner – sie gehört nicht in die App und nicht auf GitHub.
Bei Azure muss die Ressource im bezahlten Tarif **S0** laufen, nicht im
kostenlosen F0: Der kostenlose Tarif trägt die Rechte zur kommerziellen
Verwendung nicht.

### Eine eigene Aufnahme einschieben

Du bist Muttersprachler, deine Stimme sticht jede erzeugte aus. Und du musst
nicht alles auf einmal machen – jede Datei lässt sich einzeln ersetzen,
zwischendurch ist nie etwas kaputt:

1. In `web/audio/index.json` das Wort suchen und nachsehen, wie die Datei
   heißt, zum Beispiel `w0042.mp3`.
2. Das Wort aufnehmen. Die Sprachmemo-App des Handys reicht.
3. Die Datei nach `w0042.mp3` umbenennen und die alte überschreiben.
4. Im Browser F5.

Am Eintrag selbst ändert sich nichts. Nur `"stimme"` darfst du von Hand auf
deinen Namen setzen, damit später nachvollziehbar bleibt, was von wem kommt.
Andere Endungen gehen auch (`.m4a`, `.wav`, `.ogg`, `.webm`) – dann muss aber
der Dateiname in `index.json` mitgeändert werden, sonst sucht die App weiter
nach der `.mp3`.

Sinnvolle Reihenfolge: erst die Wörter der ersten Level, danach immer ein
Level voraus. Was noch nicht eingesprochen ist, kommt so lange von der
erzeugten Stimme, und niemand merkt die Naht.

Die Schritt-für-Schritt-Anleitung steht auch in `web/audio/LIESMICH.txt`.
Hier steht das Warum, dort das Wie.

### Stand heute

**Die Tonspur steht.** In `web/audio` liegen **2153 Aufnahmen**, zusammen
27.6 MB, dazu `index.json`. Erzeugt am 15.09.2026 über Azure im Tarif S0 für
unter drei Dollar:

- 2141 Wörter und Lückensätze mit `bs-BA-GoranNeural`
- die 12 Geschichten mit `bs-BA-VesnaNeural`

Dazu kommt der Ordner `_probe` mit den Probeaufnahmen aus `--probe`. Der
gehört nicht in die App und wird von `app_bauen.py` nicht mitkopiert.

Eingesprochen ist noch nichts von dir. Jede Datei, die du selbst aufnimmst
und darüberschreibst, sticht die erzeugte sofort aus – siehe „Eine eigene
Aufnahme einschieben“.

Beim Start zählt `start.py` weiterhin die Dateien im Ordner und meldet sie in
der Konsole. Das ist nur eine Anzeige für dich – die App selbst richtet sich
ausschließlich nach `index.json`.

## Ordner

```
Bosnisch Lernapp/
├── vokabeln.py       Sektionen, Levels, Wörter, Lückentexte  ← Inhalt
├── grammatik.py      Grammatik-Erklärungen und Übungen        ← Inhalt
├── geschichten.py    Geschichten-Pfad und Wörterbuch          ← Inhalt
├── sprachen.py       Oberfläche und Rechtstexte in 8 Sprachen ← Inhalt
├── uebersetzungen.py Lerninhalte in allen Sprachen            ← Inhalt
│
├── inhalt_bauen.py   Macht aus den fünf Dateien web/inhalt/<code>.json
├── app_bauen.py      Kopiert web/ in die Android-Hülle und ruft Capacitor
├── seite_bauen.py    Erzeugt die vier Seiten in github-seite
├── grafiken_bauen.py Zeichnet store/icon-512.png für den Play Store
├── zmaj_lottie.py    Erzeugt die Drachen-Animationen in web/maskottchen
├── ton_bauen.py      Erzeugt die Aufnahmen und web/audio/index.json
├── ton_pruefen.py    Prüft, ob die Tonspur vollständig ist
│
├── inhalt.py         lade_daten(): aus den fünf Dateien wird der Inhalt
├── start.py          Startet die App am PC (web/ + /api/daten) und
│                     --fehlende; keine Konten mehr
├── Zmaj Bosnisch lernen.vbs  Startet start.py ohne Fenster (Verknüpfung)
├── start.log         Meldungen, wenn über die Verknüpfung gestartet
│
├── tts_zugang.json   Schlüssel für den Sprachdienst – nicht weitergeben
├── mail_zugang.json  Postfach für feedback_holen.py – nicht weitergeben
├── *.BEISPIEL.json   Vorlagen für die beiden Zugangsdateien
│
├── ANLEITUNG.md      Diese Datei
├── sicherung_konten_2026-09-16/  Die Profildateien von früher, dazu die
│                     daraus erzeugten zmaj-sicherung-<Name>.json
├── store/            icon-512.png und feature-1024x500.png für Google
├── github-seite/     Die vier öffentlichen HTML-Seiten, siehe LIESMICH.txt
└── web/              ← das ist die App. Nur dieser Ordner wandert ins Handy
    ├── index.html    Die Oberfläche: Aussehen, Bedienung, alle Regeln
    ├── index.html.vor_*  Sicherungen früherer Fassungen (nicht in der App)
    ├── inhalt/       de.json … fr.json, erzeugt von inhalt_bauen.py,
    │                 dazu liste.json als Verzeichnis
    ├── audio/        index.json (Zuordnung Text → Datei) und 2153 Töne
    │                 w0001.mp3 …, g01.mp3 …, siehe LIESMICH.txt dort;
    │                 _probe/ mit den Probeaufnahmen bleibt draußen
    ├── maskottchen/  zmaj.json = Drache als Lottie-Animation, dazu je eine
    │                 Datei mit Brille, Kopfhörer, Mütze, Krone
    ├── fonts/        Die Schriftdateien (Nunito, Spectral)
    ├── schriften.css Bindet sie ein – kein fremder Server
    ├── lottie.min.js Spielt die Drachen-Animation ab (liegt mit im Ordner)
    ├── LIZENZEN.txt  Lizenzen der Schriften und von lottie (SIL OFL, MIT)
    ├── icon.ico      Symbol der Desktop-Verknüpfung (Flagge, 16 bis 256 px)
    ├── icon-256.png  Dasselbe Symbol als PNG
    ├── flagge.png    Dasselbe Symbol für Browser-Tab und Kopfzeile
    └── _feature.html Vorlage für den Store-Banner, siehe grafiken_bauen.py
```

Daneben, außerhalb dieses Ordners:

```
zmaj-android/         Die Android-Hülle (Capacitor), siehe „Der Weg zur
                      Android-App“. Der Unterordner android/ ist das
                      Gradle-Projekt für Android Studio.
```

## Neue Grammatik-Lektion oder Geschichte

Eine Lektion in `grammatik.py` hängt an einer Level-id:

```python
"mehrzahl": {
    "erklaerung": [
        "Ein Absatz Text.",
        {"tabelle": [["Überschrift 1", "Überschrift 2"], ["Zeile", "Zeile"]]},
    ],
    "uebungen": [
        {"frage": "Mehrzahl von „kuća“?", "optionen": ["kuće", "kući"], "richtig": "kuće", "tipp": "weiblich → -e"},
    ],
},
```

Eine Geschichte in `geschichten.py` braucht `id`, `titel`, `stufe`, `text`,
`uebersetzung` und `fragen`, optional `passt_zu` (Level-id als Hinweis). Die
Stelle in der Liste bestimmt die Reihenfolge im Geschichten-Pfad. Neue Wörter
aus dem Text kommen ins `WOERTERBUCH` (klein geschrieben, genau in der Form,
wie sie im Text stehen).

## Was als Nächstes ansteht

Was für den ersten Build nach dem geschlossenen Test der Reihe nach laufen
muss, steht oben unter „Liegen bereit für den Build nach dem Test“.

Danach, ohne Eile:

- Die Wörter Level für Level mit deiner eigenen Stimme neu einsprechen (die
  Technik dafür steht, siehe „Die Tonspur“)
- Wiederholungssystem: schwierige Wörter kommen öfter dran
- Jede der acht Sprachen von einem Muttersprachler prüfen lassen

Zurückgestellt, nicht abgesagt:

- Ein Server im Internet. Er würde erst Sinn ergeben, wenn zwei Geräte
  zusammengeführt werden können statt sich zu überschreiben – daran hakte
  es schon beim alten Server.
