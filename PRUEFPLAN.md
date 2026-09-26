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
| **P12** | Wortschatz durchsehen | 569 vorgelegte Wörter entschieden, 568 behalten. Dabei 10 Dubletten mit falscher Schreibweise und 13 fehlende Sonderzeichen gefunden. |

---

## Offen, vor dem Produktionsantrag (🔴)

### P5 — Ein Level von null auf bestanden

Neues Profil anlegen (App-Speicher leeren), Level 1 spielen, bis der
Level-Test freigeschaltet ist, Test bestehen.

**Bestanden, wenn:** Der Fortschrittsbalken 100 % zeigt, Level 2 aufgeht,
und der Lernstand nach dem Schließen und Neustarten der App noch da ist.

**Achten auf:** Ob Münzen und Lernserie richtig mitzählen, ob die
Tagesaufgabe den Fortschritt übernimmt.

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
