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
| **P6** 🔴 | Leben aufbrauchen und zurückbekommen | Am 28.09. durchgespielt. Sperrschirm, Zurück-Taste, Schließen während der Sperre, Herz für Münzen, Herz per Video und der Ablauf der Wartezeit — alles wie vorgesehen, **kein Fehler gefunden**. Zwei Nebenbefunde festgehalten, siehe unten. |
| **P7** 🔴 | Abonnement kaufen und kündigen | Am 28.09. mit einem Test-Abo (Lizenztester) durchgespielt. Kauf, Freischaltung, Neustart, Flugmodus, Bestätigungsfrist, Kündigung und Ablauf — alles ohne Fehlermeldung, **kein Fehler gefunden**. Einzelheiten unten. |
| **P8** 🔴 | Ohne Internet | Am 28.09. im Flugmodus durchgespielt. Lernen, Ton und Speichern laufen vollständig. **Zwei Fehler gefunden und behoben:** die App zeigte auf dem Handy den Platzhalter vom PC und gab dafür sogar ein Leben; und das Sprechen ohne Netz meldete „Versuch es noch einmal" statt zu sagen, dass Internet fehlt. |
| **P12** | Wortschatz durchsehen | 569 vorgelegte Wörter entschieden, 568 behalten. Dabei 10 Dubletten mit falscher Schreibweise und 13 fehlende Sonderzeichen gefunden. |

---

## Offen, vor dem Produktionsantrag (🔴)

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

---

## P6 im Einzelnen — durchgeführt am 28.09.2026

**Aufbau.** Ausgangslage: 5 von 5 Leben, 530 Münzen, Level 1 und 2 bei 100 %.
Über Nacht waren die Leben von 3 auf 5 nachgewachsen — der Nachfüllweg über
mehrere Stunden war damit schon vor dem ersten Handgriff belegt.

**Wer was gespielt hat.** Die Lektionen hat die WebView-Fernwartung gespielt,
also echte Klicks auf die echten Bedienelemente; Sprechaufgaben waren
ausgespart (`canSpeak` vorübergehend aus), weil sie sich nicht fernbedienen
lassen. Die Zurück-Taste und das Schließen der App kamen als echte
Android-Ereignisse über `adb`, nicht als Aufruf im Programm.

**Ergebnis gegen die Kriterien.**

| Kriterium | Ergebnis |
|---|---|
| Wartezeit wird heruntergezählt | 2 h 0 min → 1 h 59 min → 1 h 58 min → … , durchgehend richtig |
| Nach Ablauf kommt ein Herz zurück | ja, auf die Millisekunde wie vorausberechnet |
| App bleibt nicht hängen | kein Hänger, kein toter Schirm, kein Doppel-Zurück |
| Schließen während der Sperre | überstanden: 0 Leben, gleicher Zeitstempel, Uhr lief weiter |
| Zurück-Taste auf dem Sperrschirm | führt in die Levelansicht, von dort ins Hauptmenü |

**Der Weg im Einzelnen.**

1. **Fünfmal falsch geantwortet**, Leben 5 → 4 → 3 → 2 → 1 → 0. Jede falsche
   Antwort kostete genau ein Leben, die Aufgabe kam als Wiederholung zurück
   in die Warteschlange. Der Zeitstempel für das Nachwachsen wurde beim
   ersten Verlust gesetzt — und beim zweiten Durchgang richtigerweise **nicht**
   neu gesetzt, weil die Leben da nicht mehr voll waren.
2. **Sperrschirm:** „Lektion abgebrochen · ♥ 0 · Keine Leben mehr. · 2 h 0 min
   bis zum nächsten Leben", darunter drei Knöpfe — „♥ Video ansehen",
   „♥ für 🪙 100" und „Zurück zum Level".
3. **Zurück-Taste:** einmal führt in die Levelansicht — ohne die Frage
   „Lektion abbrechen?", der am 26.09. behobene Fehler ist also weg. Dort
   steht der Lektionsknopf als „♥ Keine Leben · warten" und ist gesperrt, und
   beide Wege zu einem Herz stehen als eigene Zeile darunter. Noch einmal
   zurück führt ins Hauptmenü. Keine Sackgasse.
4. **App hart geschlossen und neu geöffnet:** 0 Leben, derselbe Zeitstempel,
   Uhr bei 1 h 58 min, Lektionsknopf weiter gesperrt.
5. **Herz für Münzen:** 530 → 430 Münzen, 0 → 1 Leben, Knopf wieder frei, die
   Zwei-Wege-Zeile verschwindet. Die Wartezeit läuft unverändert weiter — das
   nachwachsende Herz kommt also trotzdem zu seiner ursprünglichen Zeit. Das
   ist großzügig, aber gewollt.
6. **Herz per Video:** noch einmal ein Leben verloren, auf dem Sperrschirm
   „♥ Video ansehen" getippt. Die Anzeige lief, danach stand die App von
   selbst wieder in der Levelansicht, `lohn` 0 → 1, Leben 0 → 1. Nebenbei
   belegt: die **Tagesgrenze für Herz-Videos setzt sich zum Tageswechsel
   zurück** — gestern waren 6 von 6 aufgebraucht, heute stand der Zähler
   wieder auf 0.
7. **Ablauf der Wartezeit.** Zwei Stunden absitzen ließ sich nicht, also wurde
   der gespeicherte Zeitstempel um 250 Minuten zurückdatiert — zwei volle
   Nachfüllzeiten. Geprüft wird damit genau der Weg, den die App nach echtem
   Warten geht, `syncLives()` rechnet in beiden Fällen dasselbe. Nach dem
   Neustart standen **genau zwei Leben** da, der neue Zeitstempel stimmte auf
   die Millisekunde mit der Vorausberechnung überein, und das nächste Herz
   war für 1 h 50 min angekündigt. Zwei Leben hatte das Gerät an diesem Tag
   nie — der Wert kann also nur aus dem Nachfüllen stammen.

**Zwei Nebenbefunde.**

- **Der erste Messversuch schlug fehl**, und die Schuld lag bei der Messung,
  nicht an der App: nach `am force-stop` stand wieder der alte Stand da. Die
  WebView hält frisch geschriebenes `localStorage` einige Sekunden im
  Arbeitsspeicher, bevor sie es auf die Platte legt. Derselbe Schreibvorgang
  mit zwölf Sekunden Abstand überlebte vollständig. Gegenprobe mit dem
  lebensnahen Fall — schreiben, Home-Taste, dann von Android weggeräumt
  (`am kill`) — ging ebenfalls vollständig gut. `am force-stop` im
  Vordergrund ist ein Entwicklerbefehl, kein Weg, den ein Nutzer geht. Kein
  Mangel, aber gut zu wissen, wenn später wieder jemand misst.
- **Uhr vorgestellt.** Der Kommentar in `syncLives()` warnt vor einem
  Zeitstempel aus der Zukunft: dann wächst nie wieder ein Herz nach. Probe
  mit einem Stempel 24 Stunden voraus: die App klemmt ihn auf jetzt ab und
  meldet „nächstes in 2 h 0 min". Die Vorsorge greift.

**Aufgeräumt.** Leben wieder auf 5 und die 100 Münzen zurückgebucht — die hat
die Prüfung ausgegeben, nicht Ajdin. Die Probeschlüssel im Gerätespeicher sind
entfernt. **Nicht** zurückgesetzt wurden die Tageszähler und das eine
eingelöste Herz-Video: das waren echte Ereignisse.

---

## P7 im Einzelnen — durchgeführt am 28.09.2026

**Aufbau.** Gekauft hat Ajdin selbst am Gerät, mit seinem Google-Konto als
**Lizenztester** — bezahlt wird dabei mit Googles Testkarte, es fließt kein
Geld. Der Lizenztest rafft außerdem die Zeiträume zusammen: ein Monatsabo
verlängert sich alle 5 Minuten statt alle 30 Tage, und die Frist, in der die
App den Kauf bestätigen muss, beträgt 3 Minuten statt 3 Tage. Erst dadurch
ließ sich der ganze Ablauf in einer Viertelstunde prüfen. Gemessen wurde über
die WebView-Fernwartung, jeweils direkt am laufenden Programm.

**Vorher.** `premium: false`, Google meldet `bekannt: true, aktiv: false`,
5 von 5 Leben, Werbung erlaubt, 530 Münzen. Beide Basispläne kommen von
Google: `monat` 2,99 € (P1M), `jahr` 19,99 € (P1Y) — die Preise stehen
nirgends im Programm.

**Ergebnis gegen die Kriterien.**

| Kriterium | Ergebnis |
|---|---|
| Kauf ohne Fehlermeldung | ja, Monatsplan über den Block „Vollversion" |
| Freischaltung | sofort: Schalter an, Stand „Aktiv", „Abo verwalten" erscheint |
| Werbung verschwindet | ja — `werbungErlaubt()` liefert `false`, für Anzeige und Video |
| Leben unbegrenzt | ja, ♥ ∞ und „Vollversion: unbegrenzte Leben" |
| Zustand nach Neustart | unverändert aktiv |
| Kündigung ohne Fehlermeldung | ja, über „Abo verwalten" in der App zu Googles Abo-Seite |
| Vollversion bleibt bis Zeitraumende | ja, noch rund vier Minuten, dann sauber weg |
| Ohne Internet („Achten auf") | Vollversion bleibt bekannt — siehe unten |

**Zeitverlauf der Messung** (UTC):

```
17:04  gekauft (Monat, Testkarte)
17:06  premium=true, aktiv=true, Werbung aus, Leben unbegrenzt
17:06  App hart neu gestartet -> weiterhin aktiv
17:07  Flugmodus an, App neu gestartet -> weiterhin aktiv
17:10  Flugmodus aus, 5,5 Minuten nach dem Kauf -> weiterhin aktiv
17:11  gekuendigt -> weiterhin aktiv, wie vorgesehen
17:15  Zeitraum zu Ende -> premium=false, Werbung wieder erlaubt, Leben 5 von 5
17:16  App neu gestartet -> Vollversion weg, beide Plaene wieder kaufbar
```

**Was die einzelnen Messungen belegen.**

- **Ohne Internet.** Im Flugmodus antwortet die Play-Abrechnung aus ihrem
  eigenen Zwischenspeicher: `bekannt: true, aktiv: true`. Die App musste
  nicht einmal auf den gemerkten Wert zurückfallen. Der Fall, vor dem der
  Kommentar über `vollAbgleichen()` warnt — ein zahlender Nutzer sitzt im
  Flugzeug plötzlich wieder vor Werbung — tritt also nicht ein, und zwar aus
  zwei Gründen hintereinander.
- **Die Bestätigungsfrist.** Dass die Vollversion 5,5 Minuten nach dem Kauf
  noch stand, ist der Nachweis für `acknowledgePurchase`. Ohne Bestätigung
  hätte Google den Testkauf binnen 3 Minuten von selbst erstattet und die
  Vollversion wieder abgeschaltet. Das ist der teuerste stille Fehler, den
  ein Abo haben kann, und er ist damit ausgeschlossen.
- **Die Kündigung.** Der Weg dorthin führt aus der App heraus, weil Google
  ihn vorschreibt: Der Schalter kann nur einschalten, darunter steht bei
  aktivem Abo „Abo verwalten". Dieser Weg wurde mitgeprüft und führte auf
  Googles Abo-Seite für Zmaj.
- **Nach dem Ablauf.** `premium: false`, Werbung wieder erlaubt, Leben wieder
  5 von 5 mit sauberem Zeitstempel, „Abo verwalten" verschwunden, beide Pläne
  wieder kaufbar. Die 530 Münzen sind unverändert.

**Für P8 vorweggenommen.** Der Punkt „kennt die App ohne Internet die
Vollversion?" ist damit erledigt. Was in P8 offenbleibt, ist der Rest der App
im Flugmodus: Lektion, Ton, Sicherung.

---

## P8 im Einzelnen — durchgeführt am 28.09.2026

**Aufbau.** Flugmodus über `adb` geschaltet, App jedes Mal hart geschlossen
und neu geöffnet, damit sie wirklich ohne Netz startet und nicht nur ohne Netz
weiterläuft. Die Lektion hat die Fernwartung gespielt, die Sprechaufgabe hat
Ajdin selbst am Gerät versucht — die geht nicht fernzusteuern.

**Ergebnis gegen die Kriterien.**

| Kriterium | Ergebnis |
|---|---|
| Lernen | ganze Lektion, 11 von 11 richtig, +8 neue Wörter, Ergebnisschirm vollständig |
| Tonwiedergabe | 2153 Aufnahmen liegen in der App, `w0001.mp3` spielte ab |
| Speichern | 74 gewusste Wörter im Gerätespeicher, Tagesaufgaben mitgezählt |
| Werbung fällt aus, blockiert aber nicht | **erst nach der Behebung** — siehe Befund 1 |
| Abo-Prüfung | fällt nicht einmal aus: Play Billing antwortet aus dem Zwischenspeicher (P7) |
| Keine ratlose Fehlermeldung | **erst nach der Behebung** — siehe Befund 2 |

**Befund 1 — auf dem Handy erschien der Platzhalter vom PC.**

Ohne Netz kommt AdMob beim Start nicht hoch (`admobFehler: "Error making
request."`). Danach griff in `zeigeWerbungJetzt()` der Zweig, der nur für den
Browser am PC gedacht ist, und auf dem Handy stand nach der Lektion wirklich:

```
ANZEIGE
Hier erscheint die Werbung.
[Weiter]   [Werbung abschalten]
```

Dazu zählte `werbungGezaehlt()` ohne Bedingung mit (`n` ging 0 → 1), und beim
Knopf „♥ Video ansehen" meldete der Platzhalter am Ende `fertig(true)` — es
gab also **ein echtes Leben für eine Anzeige, die es nie gab.**

Neu ist der Befund nicht: In `WERBUNG_PRUEFUNG.md` steht er seit dem
20.09.2026 als Punkt 5 und Punkt 10, dort aus dem Quelltext hergeleitet. P8
hat ihn zum ersten Mal auf dem Gerät gesehen — und er ist jetzt behoben.

**Die Behebung.** Ist das AdMob-Plugin da, gibt es keinen Platzhalter mehr:
die Anzeige fällt aus, `fertig(false)`, kein Kontingent, kein Leben. Der
Platzhalter bleibt für den PC, wo es AdMob gar nicht gibt. Damit der Knopf
nicht kaputt aussieht — das ist Punkt 12 desselben Berichts —, kommt jetzt
eine kurze Meldung: „Gerade gibt es keine Anzeige. Versuch es später noch
einmal.", in allen acht Sprachen.

**Befund 2 — das Sprechen geht ohne Netz nicht, und die App sagte das nicht.**

Androids Erkennung braucht für Bosnisch, Kroatisch und Serbisch das Netz; auf
dem Gerät liegt kein Sprachpaket dafür. Der Versuch lieferte deshalb nichts,
und die App zeigte „Das hat nicht geklappt. Versuch es noch einmal." — der
Nutzer bekam gesagt, er habe falsch gesprochen, dabei fehlte nur das Internet.
Genau der Fall, auf den P8 achten sollte.

Gut daran: **ein Leben kostet es nicht.** `bewerte([])` beantwortet die
Aufgabe gar nicht, der Nutzer kann es erneut versuchen oder überspringen.

**Die Behebung.** Kommt nichts zurück und `navigator.onLine` ist falsch,
steht jetzt „Das Sprechen braucht Internet. Überspring die Aufgabe." — in
allen acht Sprachen, an allen drei Stellen (Plugin-Weg, Fehlerzweig,
Browser-Weg).

**Gegenprobe nach der Behebung**, Fassung 34 auf dem Gerät:

| Lage | Ergebnis |
|---|---|
| Flugmodus, Lektion zu Ende | kein Platzhalter, `n` blieb bei 2 |
| Flugmodus, „♥ Video ansehen" getippt | Meldung erscheint, `lohn` bleibt 1, Leben bleibt 0 |
| Wieder online, Anzeige angefordert | echte Anzeige lief, `n` 2 → 3, keine Meldung |

Die Behebung nimmt also nur dort etwas weg, wo ohnehin nichts war.

**Offen geblieben.** Die übrigen Punkte aus `WERBUNG_PRUEFUNG.md` bleiben
stehen. Die um die Anzeigenkette herum (11, 16, 17) sind durch die Arbeit vom
27.09.2026 berührt, aber noch nicht einzeln gegen diese Liste abgehakt.
