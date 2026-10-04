# Barrierefreiheit der Zmaj-App – Messbericht

Stand 04.10.2026. Automatische Prüfung mit axe-core, dazu die Reparatur als
Patch-Skript `barrierefreiheit_richten.py`. `web/index.html` ist NICHT
geändert: Die App steckt bis zum 07.10.2026 im geschlossenen Test, jede
Einreichung setzt Googles Prüfuhr zurück.

ACHTUNG: axe findet nach eigener Angabe etwa ein Drittel bis die Hälfte der
Probleme. Was hier „0 Verstöße“ heißt, heißt nicht „barrierefrei“. Ein
Durchgang mit TalkBack auf dem Telefon gehört vor die Veröffentlichung.


## Methode

- Demo gebaut mit `python3 demo_bauen.py --ziel /tmp/a11y_site` (die App ohne
  Werbung, Inhalt für alle acht Sprachen), über einen lokalen Python-Server
  ausgeliefert.
- Chromium (Playwright, `/opt/pw-browsers/chromium`), Ansicht 390 × 844
  CSS-Punkte, wie ein übliches Telefon.
- Lernstand wie bei den Store-Bildern: `testdaten/zmaj-screenshots.json`,
  auf heute verschoben (`store/bilder_machen/bilder_playwright.py`,
  `lernstand()`), Einwilligung „nein“, Sprache gesetzt.
- axe-core 4.13.0, `axe.run(document)` mit den Standardregeln (WCAG 2.0/2.1
  A und AA plus Best Practices). axe prüft nur Sichtbares, deshalb wurde
  jede Ansicht einzeln aufgerufen.
- Fünf Durchläufe: Englisch hell, Deutsch hell, Englisch dunkel, Englisch
  hell in Sektion 4 (`?sek=4`) und in Sektion 8 (`?sek=8`) – die
  Sektionsfarben ändern Grund und gedämpften Text, und gerade die
  kräftigeren Gründe der geraden Sektionen sind die schwierigen.
- Danach dieselbe Messung auf einer Kopie, die mit
  `python3 barrierefreiheit_richten.py --datei /tmp/a11y_site_nachher/index.html --schreiben`
  gerichtet war.

### Ansichten (12 je Durchlauf, 60 insgesamt)

| Name | Aufruf |
|---|---|
| start | Lernpfad, Reiter Wörter (`homeMode='words'; showHome()`) |
| geschichten-reiter | Reiter Geschichten |
| wiederholen-reiter | Reiter Wiederholen (Topf) |
| level | `openLevel(12)` |
| lektion | `startLesson()`, erste Aufgabe |
| lektion-auswahl | erste Auswahlaufgabe (`mc`) |
| lektion-richtig | dieselbe, richtige Antwort angetippt |
| lektion-falsch | nächste Auswahlaufgabe, falsche Antwort angetippt |
| test | Leveltest (`openLevel(3); startTest()`) |
| einstellungen | `showSettings()` |
| geschichte | `openStory(3)` |
| laden | `showLaden()` |


## Ergebnis vorher / nachher

Gezählt sind betroffene Elemente (axe „nodes“), summiert über alle Ansichten.
Ein Element, das in zwölf Ansichten sichtbar ist (Fußzeile), zählt zwölfmal.

| Durchlauf | kritisch vorher | ernst vorher | mäßig vorher | kritisch nachher | ernst nachher | mäßig nachher |
|---|---:|---:|---:|---:|---:|---:|
| Englisch hell | 4 | 24 | 86 | 0 | 0 | 12 |
| Deutsch hell | 4 | 24 | 85 | 0 | 0 | 12 |
| Englisch dunkel | 4 | 6 | 85 | 0 | 0 | 12 |
| Englisch hell, Sektion 4 | 4 | 24 | 86 | 0 | 0 | 12 |
| Englisch hell, Sektion 8 | 4 | 24 | 85 | 0 | 0 | 12 |
| **Summe** | **20** | **102** | **427** | **0** | **0** | **60** |

Nach Regel:

| Regel | Schwere | vorher | nachher |
|---|---|---:|---:|
| button-name | kritisch | 20 | 0 |
| color-contrast | ernst | 102 | 0 |
| region | mäßig | 307 | 12 |
| landmark-one-main | mäßig | 60 | 0 |
| page-has-heading-one | mäßig | 60 | 48 |

Deutsch und Englisch verhalten sich gleich; `<html lang>` stimmte in jeder
Ansicht mit der gewählten Sprache überein (`document.documentElement.lang = SPRACHE`
in der App), axe meldet dazu nichts.


## Die Verstöße im Einzelnen

### 1. button-name – kritisch – 4 je Durchlauf (sichtbar), 8 im Code

Beispiel: `#swSound` – `<button class="switch" id="swSound" role="switch" aria-checked="true"></button>`

Alle Schalter in den Einstellungen sind leere Knöpfe. Die Überschrift
(„Töne“, „Vibration“, „Animationen“, „Werbung“, „Vollversion“, die drei
Benachrichtigungen) steht daneben in einem `<div class="st">`, ist aber
nicht mit dem Schalter verbunden. Sichtbar waren in der Demo vier
(Töne, Vibration, Animationen, Werbung); die vier anderen sind nur in der
App oder mit Abo zu sehen und haben denselben Fehler.

Warum es Lernenden schadet: TalkBack sagt „Schalter, an“ – wofür, erfährt
niemand. Wer die Töne abschalten will, weil er in der Bahn lernt, oder die
Animationen, weil sie ihn ablenken, muss raten und ausprobieren.

**Behoben.** Jede Überschrift bekommt eine `id` (`lblToene`, `lblVibration`, …),
der Schalter `aria-labelledby` darauf. Kein neuer Text: Der Name ist die
sichtbare Überschrift und wechselt mit der Sprache mit.

### 2. color-contrast – ernst – gedämpfter Text auf dem farbigen Grund

Beispiele: `footer` („Zmaj v1.0 · Settings: tap ⚙ at the top right“),
`#streakLine > span` („❄ 1 streak freeze · 9 days until the next one“),
`#capText` / `#capPct` („16 of 19 words learned“, „84%“).

`--muted` ist auf der hellen Karte (Fläche) ausreichend, steht aber an
vielen Stellen direkt auf dem Grund der Sektion: 3,67 : 1 in Sektion 1,
2,96 : 1 in Sektion 4, 3,05 : 1 in Sektion 8. Gefordert sind 4,5 : 1 für
diese Schriftgröße (12–13 px). Die dunkle Fassung liegt überall über
4,8 : 1 und ist nicht betroffen.

Warum es Lernenden schadet: Genau dort steht der Fortschritt – wie viele
Wörter gelernt, wie lange die Serie hält. Bei Sonne auf dem Display, mit
Brille oder schwächeren Augen ist das grau-auf-farbig kaum zu lesen.

**Behoben.** Die neun hellen `--sekN-matt` und `--muted` werden dunkler –
gleicher Farbton, gleiche Sättigung (HLS), nur die Helligkeit sinkt, bis
der Ton auf Grund, Fläche und sanftem Ton seiner Sektion mindestens 4,6 : 1
erreicht:

| Token | alt | neu | Kontrast auf dem Grund vorher → nachher |
|---|---|---|---|
| `--muted` | #66698A | #585A77 | 3,70 → 4,65 |
| `--sek1-matt` | #66698A | #585A77 | 3,67 → 4,62 |
| `--sek2-matt` | #6F668A | #564F6C | 3,22 → 4,65 |
| `--sek3-matt` | #7B668A | #695776 | 3,65 → 4,65 |
| `--sek4-matt` | #87668A | #644C66 | 2,97 → 4,61 |
| `--sek5-matt` | #8A6680 | #73556B | 3,49 → 4,62 |
| `--sek6-matt` | #8A6674 | #694D58 | 3,06 → 4,62 |
| `--sek7-matt` | #597876 | #4C6665 | 3,60 → 4,64 |
| `--sek8-matt` | #5D767E | #46595F | 3,05 → 4,66 |
| `--sek9-matt` | #647287 | #545F71 | 3,50 → 4,63 |

Sichtbar: Grauer Text wird etwas dunkler, in den geraden Sektionen
deutlicher als in Sektion 1. Er bleibt klar leiser als die Hauptschrift
(`--ink` #0F1E4D).

### 3. color-contrast – ernst – farbige Schrift (Grün, Rot, Gelb)

| Element | Beispiel | vorher | Grund |
|---|---|---:|---|
| `#xFb.feedback.ok` | „Tačno! ✓“ nach richtiger Antwort | 3,2 : 1 | `--good` #1E9E5A auf Fläche |
| `#xFb.feedback.no` | „The answer is: kuća“ | 4,08 : 1 | `--bad` #D6453D auf Fläche |
| `.node.current .state` | „Up next“ am Geschichtenpfad | 2,33 : 1 | `--accent-dark` #C99E00 |
| `.node.done .state` | „Read“ | 3,2 : 1 | `--good` |
| `.km` | „KM“ an den Münzen | 1,8 : 1 hell, 3,79 : 1 dunkel | `--accent-dark` mit `opacity:.7` |

Warum es Lernenden schadet: Die Rückmeldung nach der Antwort ist die
wichtigste Zeile der ganzen Lektion – bei einer falschen Antwort steht dort
die richtige. Wer sie nicht lesen kann, lernt den Fehler mit.

**Behoben.** Grün, Rot und Gelb sind auch Flächen- und Randfarben (Balken,
Schalter, Knopfschatten, Rahmen der Antwort); dort gilt 3 : 1 und dort
stimmen sie. Deshalb drei neue Token nur für Schrift, Flächen bleiben:

| Token | hell | dunkel | ersetzt als Schriftfarbe |
|---|---|---|---|
| `--good-text` | #188049 (3,21 → 4,63) | #55CE8A (4,43 → 4,60) | `--good` #1E9E5A / #4CCB84 |
| `--bad-text` | #D0352C (4,09 → 4,62) | #FF9E98 (3,60 → 4,61) | `--bad` #D6453D / #FF7A72 |
| `--accent-text` | #876A00 (2,27 → 4,64) | #DFB31F (4,36 → 4,61) | `--accent-dark` #C99E00 / #D9AE1E |

(Kontrast jeweils gegen die ungünstigste Fläche aller neun Sektionen, beim
Gelb auch gegen `--accent-soft`.)

Umgestellt: `.feedback.ok/.no/.almost`, `.opt.right`/`.opt.wrong` (nur
Schrift), `.node.current/.done .state`, `.km` (dazu ohne `opacity:.7` – leiser
als die Zahl bleibt KM durch die kleinere Schrift), `.qalle`,
`.pwregeln span.ok`, `.sprachzeile .haken`, `.wordlist .ok` und die
Rückmeldung beim Sprechen (`task.gehoert_ok`). Sichtbar: Das Grün der
Rückmeldung wird eine Stufe satter, „Jetzt dran“ ein dunkleres Gold, im
Dunkeln das Rot etwas heller.

### 4. landmark-one-main und region – mäßig

Beispiel: `html` (kein `<main>`), `#streakLine`, `#questBox`,
`div[role="tablist"]`, alle Abschnitte der Einstellungen.

Die Ansichten stehen in einem `<div class="wrap">` ohne Orientierungspunkt.
Bildschirmleser bieten „zum Hauptinhalt springen“ an – hier gibt es keinen.
Wer mit TalkBack durch die App wischt, muss jedes Mal an Herzen, Münzen und
Knöpfen vorbei.

**Behoben** (ohne Risiko, deshalb mitgenommen): Alle Ansichten stehen in
einem `<main>`, Kopf und Fußzeile bewusst draußen. Kein CSS hängt an
`.wrap > div`, geprüft.

Übrig: 12 `region`-Funde im dunklen Durchlauf. Dort war die Einstufungsfrage
(„Do you already know some Bosnian?“) offen, ein Overlay außerhalb von
`<main>` ohne `role="dialog"`. Siehe unten.

### 5. page-has-heading-one – mäßig – 1 je Ansicht

Keine Ansicht hat eine `<h1>`. Für Bildschirmleser ist die Gliederung
dadurch flach. **Nicht behoben**: Eine `h1` je Ansicht hieße sichtbare neue
Überschriften (Gestaltung) oder versteckte Texte in acht Sprachen.


## Was das Skript bewusst nicht ändert

- **`.opt.right`** – grüne Schrift auf `--primary-soft`. Mit `--good-text`
  steigt der Kontrast, erreicht auf den kräftigen Sektionsgründen (2, 4, 6,
  8) aber keine 4,5 : 1; dafür bräuchte es #126037, fast schwarzgrün, oder
  einen anderen Grund für die richtige Antwort. axe meldete es nicht als
  Verstoß (während der Überblendung kann axe den Grund nicht sicher
  bestimmen). Gestaltungsfrage, nicht Reparatur. Die Antwort steht
  zusätzlich in der Rückmeldung darunter, die jetzt lesbar ist.
- **`.streakline .lost`** (Serie verloren, Rot auf dem Grund) und
  **`.result-big.fail`** (große Schrift, dort reichen 3 : 1) behalten
  `--bad`. Ersteres war in keiner Messung sichtbar; Rot auf dem Grund müsste
  fast braun werden.
- **Overlays ohne `role="dialog"`** (Einstufungsfrage, `frage()`,
  Einwilligung, Bewertung): mäßig, erfordert Fokusführung beim Öffnen und
  Schließen – das gehört getestet, nicht blind gepatcht.
- **Bosnischer Text ohne `lang="bs"`**: In der englischen Oberfläche liest
  TalkBack „kuća“ mit englischer Stimme. axe prüft das nicht. Lohnend für
  Lernende (Antwortknöpfe, Geschichten, Wortlisten), aber über viele
  JavaScript-Stellen verteilt – eigener Schritt.
- **Nicht-Text-Kontrast** (WCAG 1.4.11) der Schalter und Fortschrittsbalken
  prüft axe nicht; nicht gemessen.


## Dateien

- `barrierefreiheit_richten.py` – Patch-Skript nach dem `*_richten.py`-Muster:
  Probelauf ohne Schalter, `--schreiben` schreibt, `--datei PFAD` richtet eine
  Kopie. 32 Stellen, jede muss genau einmal vorkommen, sonst wird nichts
  geschrieben. Nachkontrollen: Klammern, Kommentare, `<main>`-Paar, jeder
  Schalter mit `aria-labelledby` auf genau ein Element, die drei Texttoken in
  allen drei Farbblöcken, dunkles `--muted` unberührt, Flächenfarben
  unverändert.
- `tests/test_barrierefreiheit_richten.py` – ohne Browser: passt auf das
  heutige `web/index.html`, zweiter Lauf bricht ab, fehlender Anker bricht
  ab, jede neue Farbe erreicht rechnerisch 4,5 : 1.
- `tests_e2e/test_barrierefreiheit.py` – mit Browser, nicht im normalen
  `pytest`-Lauf: baut die Demo, richtet sie, prüft 11 Ansichten in en hell,
  de hell, en dunkel auf 0 ernste und kritische Verstöße (ca. 80 s).
  `ZMAJ_CHROMIUM=/pfad python3 -m pytest tests_e2e -q`.
- `tests_e2e/vendor/axe.min.js` (axe-core 4.13.0, MPL-2.0, enthält
  MIT-Teile) mit `axe-core-LICENSE-3RD-PARTY.txt`; `LICENSES/MPL-2.0.txt`,
  Eintrag in `REUSE.toml`. Nur Testwerkzeug – nicht in `web/`.

Anwenden nach dem 07.10.2026:

    python3 barrierefreiheit_richten.py              # Probelauf
    python3 barrierefreiheit_richten.py --schreiben
    python3 -m pytest -q && python3 -m pytest tests_e2e -q
