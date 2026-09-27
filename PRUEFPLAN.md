# Prüfplan vor der Veröffentlichung

Angelegt am 26.09.2026. **Warum erst jetzt:** Der ursprüngliche Plan P1 bis
P15 stand nur im Gesprächsverlauf. Als Ajdin fragte, was P5 sei, ließ er
sich nicht mehr sicher rekonstruieren — nur P1 bis P4 und P12 waren
eindeutig zuzuordnen. Deshalb hier neu und schriftlich.

Jede Prüfung nennt, **wer** sie macht und **woran** man das Bestehen
erkennt. Prüfungen mit 🔴 braucht es vor dem Produktionsantrag, die
übrigen können danach folgen.

---

## Erledigt

| | Was | Ergebnis |
|---|---|---|
| **P1** 🔴 | Sicherung speichern, löschen, einlesen | Läuft. Zwei Mängel gefunden: die Datei war schwer zu finden, und die Vollversion ging beim Einlesen verloren. Behoben durch `sicherung_richten.py` (Dateiname in der Meldung, Suchhinweis „zmaj" in acht Sprachen). |
| **P2** 🔴 | Gerät und Fassung festhalten | Android 15, App-Fassung 15.7.54.2. |
| **P3** 🔴 | Tonspur durchhören | 45 Aufnahmen aus zwei Risikogruppen geprüft, 13 beanstandet. Zehn davon auf die kroatische Stimme mit Lautschrift umgestellt, eine Vokabel geändert (`Brz oporavak`), zwei bleiben. |
| **P4** 🔴 | Eine Lektion vollständig durchspielen | Durchgespielt am 26.09., 6 von 6 richtig. Alle sechs Übungsformen kamen vor: Sprechen, Hören, Auswählen in beide Richtungen, Lückentext, Schreiben. |
| **P5** 🔴 | Ein Level von null auf bestanden | Am 27.09. mit geleertem App-Speicher durchgespielt. Level 1 „Grundlagen“ 33 von 33 Wörtern, 100 %, bestanden; Level 2 „Zahlen“ aufgegangen. Lernstand hat Neustart und Neuinstallation überlebt. Münzen, Serie und Tagesaufgaben zählten mit. **Drei Fehler gefunden** – siehe unten. |
| **P12** | Wortschatz durchsehen | 569 vorgelegte Wörter entschieden, 568 behalten. Dabei 10 Dubletten mit falscher Schreibweise und 13 fehlende Sonderzeichen gefunden. |

---

## Offen, vor dem Produktionsantrag (🔴)

### P6 — Leben aufbrauchen und zurückbekommen

Fünfmal falsch antworten, bis keine Leben mehr da sind. Sperrbildschirm
ansehen. Dann entweder zwei Stunden warten oder ein Herz im Laden kaufen.

**Bestanden, wenn:** Die Wartezeit richtig heruntergezählt wird, nach Ablauf
ein Herz zurückkommt, und die App dabei nicht hängenbleibt.

**Achten auf:** Was passiert, wenn man die App während der Sperre schließt
und neu öffnet. Und was die Zurück-Taste auf dem Sperrbildschirm tut.

### P7 — Abonnement kaufen und kündigen

Im Testkonto die Vollversion kaufen, prüfen dass Werbung verschwindet und
die Leben unbegrenzt sind. Dann kündigen und prüfen, dass die Vollversion
bis zum Ende des Zeitraums bleibt.

**Bestanden, wenn:** Kauf, Freischaltung und Kündigung ohne Fehlermeldung
durchlaufen und der Zustand nach einem Neustart stimmt.

**Achten auf:** Ob die App ohne Internet weiterhin die Vollversion kennt.

### P8 — Ohne Internet

Flugmodus einschalten, App starten, eine Lektion spielen, Wörter anhören.

**Bestanden, wenn:** Lernen, Tonwiedergabe und Speichern funktionieren.
Werbung und Abo-Prüfung dürfen ausfallen, aber nichts blockieren.

**Achten auf:** Ob eine Fehlermeldung kommt, die den Nutzer ratlos lässt.

### P9 — Einwilligung ablehnen

App-Speicher leeren, neu starten, im Einwilligungsfenster **ablehnen**.

**Bestanden, wenn:** Die App normal weiterläuft und keine personalisierte
Werbung zeigt. Die Entscheidung muss sich in den Einstellungen ändern
lassen.

### P10 — Mikrofon verweigern

Bei der ersten Sprechaufgabe die Berechtigung ablehnen.

**Bestanden, wenn:** Die Aufgabe sich überspringen lässt und ab der
nächsten Lektion keine Sprechaufgaben mehr kommen.

*Hinweis: Der zweite Teil wurde am 26.09. erst eingebaut
(`sprechen_richten.py`) und ist noch nicht auf dem Gerät geprüft.*

---

## Offen, kann nach dem Antrag folgen

### P11 — Alle acht Oberflächensprachen

Sprache umstellen, je einen Bildschirm ansehen: Startseite, Lektion,
Einstellungen, Laden.

**Bestanden, wenn:** Nirgends ein roher Textschlüssel wie
`set.sicherung_suchen` steht und kein Text den Knopf sprengt.

*`texte_pruefen.py` prüft das automatisch und meldet derzeit nichts.*

### P13 — Ein Level mit allen Sonderfällen

Ein Level mit Grammatikaufgaben spielen, eine Geschichte lesen und ihre
Fragen beantworten.

**Bestanden, wenn:** Die Zurück-Wege aus jedem Bildschirm herausführen.

### P14 — Zwei Geräte

Sicherung auf Gerät A erstellen, auf Gerät B einlesen.

**Bestanden, wenn:** Der Lernstand vollständig ankommt. Die Vollversion
kommt nicht mit — sie hängt am Google-Konto.

### P15 — Ein Tag vergeht

App abends benutzen, am nächsten Morgen wieder öffnen.

**Bestanden, wenn:** Die Lernserie stimmt, neue Tagesaufgaben da sind und
die Startseite nicht mehr „heute schon geübt" behauptet.

*Achtung: Hier ist ein Fehler bekannt — nach Mitternacht zeigt die
Startseite ohne Neustart weiter den Stand von gestern.*

---

## Was nicht geprüft werden muss

**Nicht vor dem 07.10.2026 hochladen.** Jede Einreichung setzt Googles
Prüfuhr zurück. Die 13 Tester müssen bis dahin durchgehend angemeldet
bleiben; wer austritt und wieder eintritt, fängt bei null an.

---

## P5 im Einzelnen — durchgeführt am 27.09.2026

**Aufbau.** App-Speicher über `pm clear` geleert, also ein echtes neues Profil.
In der Geräteversion gibt es keine Anmeldung; das Leeren *ist* das neue Profil.
Danach war alles auf null: 0 Wörter, 0 Level, 0 Lerntage, 0 Münzen, 5 Leben.

**Wer was gespielt hat.** Die ersten fünf Lektionen und den Level-Test von
Level 1 hat Ajdin selbst am Gerät gespielt — dabei sind die drei Fehler unten
aufgefallen. Die restlichen Lektionen bis 100 % wurden über die
WebView-Fernwartung gespielt, also durch echte Klicks auf die echten
Bedienelemente, nicht durch Setzen von Werten. Sprechaufgaben waren dabei
ausgespart (`canSpeak` vorübergehend aus), weil sie sich nicht fernbedienen
lassen; sie hat Ajdin selbst geprüft.

**Ergebnis gegen die Kriterien.**

| Kriterium | Ergebnis |
|---|---|
| Fortschrittsbalken 100 % | Level 1 „Grundlagen": 33 von 33 Wörtern, 100 % |
| Level 2 geht auf | „Zahlen" aufgegangen, inzwischen selbst bei 100 % und bestanden |
| Lernstand nach Neustart da | ja — hat mehrere App-Neustarts UND mehrere Neuinstallationen überlebt |
| Münzen zählen | 530 Münzen, sauber mitgewachsen |
| Lernserie zählt | 1 Tag, Rekord 1, heute als Lerntag erfasst |
| Tagesaufgaben übernehmen den Fortschritt | 201 Aufgaben, 189 richtig, 66 neue Wörter, 33 Hörübungen, 29 Lückentexte, 15 Lektionen, 8 fehlerfreie, 22 Minuten |

**Was P5 gefunden hat.** Drei Fehler, die ohne das Durchspielen niemand
gesehen hätte — alle am selben Tag behoben und einzeln nachgemessen:

1. **Sprechen war nach dem Sperren des Handys tot.** `aufgabeMarke` diente
   dazu, verspätete Erkennungsergebnisse der VORIGEN Aufgabe zu verwerfen.
   Der Wechsel in den Hintergrund hob die Marke aber ebenfalls an, obwohl
   dieselbe Aufgabe weiter auf dem Schirm stand. Das Mikrofon hörte zu, das
   Ergebnis fiel stillschweigend weg. Gemessen: die Marke sprang allein durch
   den Wechsel von 68 auf 69.

2. **Zahlen wurden nie erkannt.** Androids Erkenner gibt Zahlen als Ziffern
   zurück — wer „pet" sagt, wird als „5" verstanden. Die lautliche
   Normalisierung strich alles außer a–z, aus der 5 wurde eine leere
   Zeichenkette, und der Vergleich scheiterte zwangsläufig. Im Level „Zahlen"
   traf das praktisch jede Sprechaufgabe. Jetzt gelten Ziffer und Wort, beim
   Sprechen wie beim Tippen.

3. **Ohne Leben gab es keinen Weg zu einem Leben.** Der Knopf für das
   freiwillige Video existierte nur auf dem Schirm, der kommt, wenn die Leben
   MITTEN in der Lektion ausgehen. Wer die App geschlossen hatte und mit 0
   Leben zurückkam, tippte auf ein Level und las „warte zwei Stunden" — ohne
   einen einzigen Knopf.

**Änderungen, die aus P5 heraus entstanden sind** (auf Ajdins Entscheidung,
keine Fehler): Tagesziele auf etwa zwei Lektionen statt einer, Werbung nach
jeder Lektion statt jeder dritten und auch nach dem Test, Level-Test erst bei
100 % bekannter Wörter statt 80 %.
