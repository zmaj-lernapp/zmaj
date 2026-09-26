# Der Lernpfad mit den 561 Wörtern

Vorschlag vom 26.09.2026, dritte Fassung. **Noch nichts eingebaut.**

Ajdin: „ne mach mehr aber mach es so das es sinn ergibt wenn es geht
auch von leicht zu schwer“.

## Die neuen Sektionen stehen nicht hinten

Sie stehen an ihrem Platz in der Schwierigkeit. Das geht, weil der
Lernstand **Level-Kennungen speichert und keine Nummern**: `passed` ist
eine Menge von ids, `hoechsterBestanden()` sucht die höchste Nummer
dazu. Schiebt man vorne etwas ein, bleibt jedes bestandene Level
bestanden, und alles bis zum eigenen Stand bleibt offen. Die neuen Level
tauchen mittendrin auf – freigeschaltet, nicht sperrend.

## Der Pfad

| | Sektion | | Level | Wörter | Farbe |
|---|---|---|---|---|---|
| 1 | Grundlagen & Alltag | *da* | 15 | 333 | Blau |
| 2 | **Dinge zum Anfassen** | **NEU** | 4 | 115 | Indigo |
| 3 | **Tiere & Natur** | **NEU** | 4 | 109 | Violett |
| 4 | **Zuhause** | **NEU** | 3 | 77 | Magenta |
| 5 | Sätze bauen | *da* | 22 | 613 | Petrol |
| 6 | **Einkaufen & Essen gehen** | **NEU** | 4 | 108 | Himmelblau |
| 7 | **Bosnien & Herkunft** | **NEU** | 3 | 81 | Blau |
| 8 | **Menschen & Kultur** | **NEU** | 2 | 58 | Indigo |
| 9 | Amt & Verträge | *da* | 6 | 162 | Violett |
| | **zusammen** | | **63** | **1656** | |

Aus 3 Sektionen und 43 Leveln werden **9 Sektionen und 63 Level**.

## Warum die Nomen vor die Grammatik

Obst, Gemüse und Tiere sind Wörter zum Zeigen – dafür braucht es
keinen Fall und keine Beugung. Sie **hinter** die Grammatik zu stellen
hieße, das Leichteste zuletzt zu bringen.

Das Einkaufen steht dagegen bewusst **danach**: „Können Sie mir bitte
zwei Kilo davon geben“ braucht Fälle und Verben. Und Sektion 8,
Menschen & Kultur, kommt zuletzt – Floskeln und Gastfreundschaft sind
das Idiomatische, das man am wenigsten ableiten kann.

### Dinge zum Anfassen

Nomen, die man zeigen kann. Ohne Grammatik zu verstehen.

| Level | Wörter |
|---|---|
| Obst | 24 |
| Gemüse | 27 |
| Lebensmittel | 35 |
| Vorrat & Getränke | 29 |

### Tiere & Natur

Dieselbe Stufe wie davor, anderes Feld.

| Level | Wörter |
|---|---|
| Tiere | 29 |
| Tiere draußen | 28 |
| Rund ums Tier | 22 |
| Natur & Pflanzen | 30 |

### Zuhause

Die ersten Taetigkeiten kommen dazu: putzen, waschen, reparieren.

| Level | Wörter |
|---|---|
| Küche & Bad | 24 |
| Putzen & Nachbarschaft | 26 |
| Technik & Reparatur | 27 |

### Einkaufen & Essen gehen

Bestellen, bezahlen, nachfragen. Braucht Fälle und Verben.

| Level | Wörter |
|---|---|
| Einkaufen & Orte | 28 |
| Im Restaurant: ankommen | 27 |
| Im Restaurant: essen & zahlen | 29 |
| Essen gehen & Mengen | 24 |

### Bosnien & Herkunft

Woher jemand kommt, und die Formen für männlich und weiblich.

| Level | Wörter |
|---|---|
| Bosnische Küche | 25 |
| Länder & Herkunft | 26 |
| Nationalitäten & Sprachen | 30 |

### Menschen & Kultur

Floskeln, Gastfreundschaft, Sevdah. Das Idiomatische.

| Level | Wörter |
|---|---|
| Vorstellen & Kennenlernen | 29 |
| Musik, Glaube & Gastfreundschaft | 29 |

## Was in vorhandene Level geht

| Level | hat heute | dazu | dann | Warum |
|---|---|---|---|---|
| Grundlagen | 32 | +1 | **33** | Ein Wort. |
| Wetter & Natur | 28 | +7 | **35** | Sieben Wörter, Gruppe nennt Level 10. |
| Feste & Traditionen | 31 | +5 | **36** | Fünf Wörter, Gruppe nennt Level 35. |

## Die Farben bei neun Sektionen

Sechs Farbtöne, 30 bis 33 Grad auseinander, alle mindestens 28 Grad
von Grün („richtig“), Rot („falsch“) und Gelb (Akzent) entfernt:

| Ton | Farbe | Sektionen |
|---|---|---|
| 235° | Blau | 1, 7 |
| 268° | Indigo | 2, 8 |
| 300° | Violett | 3, 9 |
| 332° | Magenta | 4 |
| 175° | Petrol | 5 |
| 205° | Himmelblau | 6 |

Ab Sektion 7 wiederholen sie sich. Das ist vertretbar: zwischen
Sektion 1 und Sektion 7 liegen fünf Sektionen und über dreißig Level,
die sieht nie jemand nebeneinander. Der Umschalter rechnet ohnehin mit
Rest, das Wiederholen ist schon eingebaut.

**Eine kleine Änderung:** Sektion 1 trägt heute den Ton 225. Mit
sechs Tönen wird daraus 235 – zehn Grad, das sieht man kaum. Bliebe
es bei 225, ginge sich nur **fünf** Töne aus, weil der sechste dann
zu nah an Grün käme.

## Was danach noch fehlt

- **561 Tonaufnahmen** über `ton_bauen.py`.
- **Übersetzungen in sieben Sprachen.**
- **20 Level-Beschreibungen und Tipps**, achtsprachig.
- **Sechs Sektionsnamen und -beschreibungen**, achtsprachig.
- **Zwei neue Farbtöne** und die Verteilung auf neun Sektionen.
