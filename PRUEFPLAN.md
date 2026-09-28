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
| **P9** 🔴 | Einwilligung ablehnen | Am 28.09. mit geleertem App-Speicher durchgespielt. Ablehnen bringt die App nicht aus dem Tritt, `npa=1` geht an jede Anfrage, und Werbung läuft trotzdem — nur unpersonalisiert. Die Entscheidung lässt sich in den Einstellungen in beide Richtungen ändern. **Kein Fehler gefunden.** |
| **P10** 🔴 | Mikrofon verweigern | Am 28.09. durchgespielt. Ablehnen kostet kein Leben, die Aufgabe lässt sich überspringen, und ab der nächsten Lektion kommen keine Sprechaufgaben mehr. **Ein Fehler gefunden und behoben:** der Ausschluss hielt nur bis zum nächsten Start der App. |
| **P11** | Alle acht Oberflächensprachen | Am 28.09. gemessen: acht Sprachen, je fünf Bildschirme. Kein roher Textschlüssel. **Ein gesprengter Knopf im französischen Laden**, behoben durch einen kürzeren Text. Dazu die elf Texte sprachlich geprüft, die seit dem Bericht vom 18.09. neu sind — **21 Befunde, alle eingearbeitet**. |
| **P12** | Wortschatz durchsehen | 569 vorgelegte Wörter entschieden, 568 behalten. Dabei 10 Dubletten mit falscher Schreibweise und 13 fehlende Sonderzeichen gefunden. |
| **P13** | Ein Level mit allen Sonderfällen | Am 28.09. durchgespielt: Level 27 „Fragen stellen“ mit beiden Grammatikaufgaben richtig (10 von 10), Geschichte „Mira i Rex“ gelesen und alle drei Fragen beantwortet. **Alle zehn Zurück-Wege führen heraus**, keine Sackgasse. Kein Fehler gefunden. |

---

## Offen, vor dem Produktionsantrag (🔴)

Nichts mehr. **P1 bis P10 sind seit dem 28.09.2026 alle abgehakt**,
die letzten fünf davon an diesem einen Tag. P6, P7 und P9 liefen ohne
Befund; P8 brachte zwei Fehler und P10 einen, alle drei noch am selben
Tag behoben und gegengeprüft.

---

## Offen, kann nach dem Antrag folgen

### P14 — Zwei Geräte

Sicherung auf Gerät A erstellen, auf Gerät B einlesen.

**Bestanden, wenn:** Der Lernstand vollständig ankommt. Die Vollversion
kommt nicht mit — sie hängt am Google-Konto.

### P15 — Ein Tag vergeht

App abends benutzen, am nächsten Morgen wieder öffnen.

**Bestanden, wenn:** Die Lernserie stimmt, neue Tagesaufgaben da sind und
die Startseite nicht mehr „heute schon geübt" behauptet.

**Zum bekannten Fehler:** Er ist am 26.09.2026 behoben worden. `tagPruefen()`
läuft seitdem im Zeitgeber alle 30 Sekunden, merkt den Datumswechsel, ruft
`pruefeSchutz()` und zeichnet die Startseite neu, wenn sie sichtbar ist.
Bestätigt ist das bisher nur im Quelltext — **über einen echten Tageswechsel
am Gerät noch nie.** Genau das ist P15.

**Ausgangswerte vom Abend des 28.09.2026** (am Gerät abgelesen), damit sich
morgen vergleichen lässt:

```
Lerntage   2026-09-27, 2026-09-28     Serie 2, Rekord 2, heute gelernt: ja
Serienschutz   1 im Vorrat, kein Tag in frost
Tagesaufgaben  2 von 3 geschafft:
               „10 Minuten lernen" ✓ · „10 neue Wörter lernen" ✓
               „20 Aufgaben beantworten" offen
Tageszähler    45 Aufgaben, 34 richtig, 6 Hörübungen, 6 Lückentexte,
               11 neue Wörter, 2 Lektionen, 1 fehlerfrei, 283 Minuten
Leben          5 von 5, Zeitstempel 0
Werbung        n = 6, lohn = 1 (Tag 2026-09-28)
Lernstand      77 Wörter, Level „basics" und „zahlen", 550 Münzen
```

**Worauf morgen zu achten ist:**

1. Die App **ohne Neustart** aufwecken — nur so wird der Zeitgeber geprüft.
   Erst danach einmal hart neu starten und beides vergleichen.
2. Serie muss auf 3 stehen, wenn morgen gelernt wird — und vorher auf 2
   bleiben, nicht auf 0 fallen.
3. Drei **neue** Tagesaufgaben, Zähler wieder bei null.
4. Die Startseite darf nicht mehr „Heute geübt ✓" zeigen.
5. Der Werbezähler muss sich zurücksetzen (`tag` auf den neuen Tag, `n` und
   `lohn` auf 0) — das ist am 28.09. schon einmal beobachtet worden.
6. Der Serienschutz darf **nicht** verbraucht werden: Es wird kein Tag
   ausgelassen.

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

---

## P9 im Einzelnen — durchgeführt am 28.09.2026

**Vorher gesichert.** Zwei Dateien in `sicherung_handy/`: der ganze
App-Speicher und der Lernstand allein. Das war nötig, weil P9 mit
`pm clear` anfängt — ohne Sicherung wäre alles weg gewesen. Die große
Sicherung vom 27.09. mit 1108 Wörtern, 43 Level und 35 Lerntagen liegt
unverändert daneben; sie gehört zu dem Stand vor dem Leeren für P5.

**Aufbau.** `pm clear de.smartdragon.zmaj`, dann App starten — ein echter
Erststart. Googles Einwilligungsfenster (UMP) kam von selbst. „Do not
consent" wurde als echter Tipp über `adb` gesetzt, nicht im Programm.

**Ergebnis gegen die Kriterien.**

| Kriterium | Ergebnis |
|---|---|
| App läuft normal weiter | ja — frisches Profil, Lernpfad, 5 Leben, kein Absturz, keine Fehlermeldung |
| Keine personalisierte Werbung | `personalisiert: false`, also `npa=1` an jeder Anfrage |
| Werbung läuft trotzdem | echte Anzeige lief, Zähler 0 → 1, kein Platzhalter |
| Entscheidung in den Einstellungen änderbar | ja, in beide Richtungen |

**Was in Googles Speicher stand**, direkt nach dem Ablehnen, gelesen über das
eigene Plugin `ZmajEinwilligung`:

```
dsgvo: 1 · zweck1: false · zweck3: false · zweck4: false
google: false · bekannt: true · personalisiert: false
```

Genau darauf hört `werbungPersonalisiert()`, und daraus wird das `npa` der
Anzeigenanfrage. Die App rät also nicht, sie liest Googles Antwort.

**Die Entscheidung ändern.** In den Einstellungen stand der Werbeschalter auf
aus, darunter „Nur zufällige Anzeigen, nicht auf dich zugeschnitten." Ein Tipp
darauf öffnet Googles eigenes Fenster — der Schalter legt nicht selbst um,
sondern folgt der Antwort. Nach „Consent" sprang er auf an, der Text wurde zu
„Anzeigen dürfen zu deinen Interessen passen.", und `zmaj_pers` stand auf
`an`. Der Weg zurück wurde genauso geprüft: noch einmal tippen, „Do not
consent", Schalter wieder aus. **Beide Richtungen, nicht nur eine.**

**Nebenbefund — das Fenster kam auf Englisch.** Es begrüßte mit „Welcome to
Publisher Test Ads". Das ist Googles Testformular, das zu den Testkennungen
gehört; ein eigener Text steht darin nicht. Ob das veröffentlichte Formular
auf Deutsch erscheint, hängt daran, welche Sprachen in der AdMob-Konsole für
die Datenschutzmeldung hinterlegt sind. **Beim Kennungstausch
(`admob_scharf.py`) mit ansehen.**

**Nebenbefund — eine Falle beim Zurückspielen.** Der Lernstand ließ sich
zuerst nicht wiederherstellen: nach dem Zurückschreiben und einem
`location.reload()` stand wieder alles auf null. Grund ist nicht die App,
sondern die Reihenfolge — beim Entladen schreibt die App ihren
Arbeitsspeicher weg, und der war noch leer. Richtig ist, die App den
zurückgespielten Stand mit `loadProgress()` lesen zu lassen, statt neu zu
laden. **Der Weg in der App selbst ist davon nicht betroffen:** dort ruft das
Einlesen einer Sicherung `standUebernehmen()` direkt auf (P1).

**Wiederhergestellt und gegengeprüft.** Nach hartem Neustart: 77 Wörter,
Level „basics" und „zahlen" bestanden, 550 Münzen, 5 Leben, 2 Lerntage,
Rekord 2, Einwilligung wieder auf „ja" — also der Stand von vor P9.

---

## P10 im Einzelnen — durchgeführt am 28.09.2026

**Aufbau.** Das Mikrofonrecht war nach dem `pm clear` aus P9 ohnehin weg —
also ein echter Erstkontakt. Die Lektion hat die Fernwartung gespielt, das
Berechtigungsfenster von Android wurde als echter Tipp über `adb` beantwortet:
„Zmaj erlauben, Audioaufnahmen zu machen?" → **Nicht erlauben**.

**Ergebnis gegen die Kriterien.**

| Kriterium | Ergebnis |
|---|---|
| Aufgabe lässt sich überspringen | ja, und sie kostet **kein Leben** |
| Ab der nächsten Lektion keine Sprechaufgaben | ja — neue Lektion: 12 Aufgaben, davon 0 Sprechaufgaben |
| Nach einem Neustart auch nicht | **erst nach der Behebung** — siehe unten |

Die App sagte dabei das Richtige: „Kein Zugriff auf das Mikrofon. Erlaube ihn
in den Einstellungen deines Geräts oder überspring die Aufgabe." Darunter der
Knopf „Sprechen ist gerade nicht möglich, überspringen".

**Befund — der Ausschluss hielt nur bis zum nächsten Start.**

`hoerenPruefen()` fragt beim Start `available()`, und das sagt nur, dass ein
Erkenner **installiert** ist, nicht dass die App ihn benutzen darf. Gemessen:
nach dem Neustart stand `canSpeak` wieder auf `true`, und die nächste Lektion
hatte prompt wieder zwei Sprechaufgaben. Der Nutzer, der abgelehnt hat, bekam
sie also bei jedem Öffnen der App erneut — und mit ihnen die Tagesaufgabe
„fehlerfrei", die `Lx.skipped === 0` verlangt und damit unerreichbar bleibt.
Genau das sollte der Einbau vom 26.09. verhindern; er wirkte nur bis zum
Schließen der App.

**Die Behebung.** Die Absage wird gemerkt (`zmaj_mikro_nein`), und beim Start
sieht die App zusätzlich nach — **nachsehen, nicht fragen**:
`checkPermissions()` öffnet kein Fenster. Steht dort `denied`, oder ist die
Absage gemerkt, fällt `speak` aus dem Aufgabentopf. Steht dort `granted`,
wird die Merkung gelöscht.

**Gegenprobe, Fassung 35 auf dem Gerät:**

| Schritt | Ergebnis |
|---|---|
| Mikrofon antippen, ablehnen | `canSpeak: false`, Absage gemerkt, kein Leben verloren |
| App hart neu gestartet | `canSpeak: false`, neue Lektion mit **0** Sprechaufgaben |
| Recht in den Geräteeinstellungen erteilt, neu gestartet | `granted`, Merkung von selbst gelöscht, Sprechaufgaben wieder da |

Der Weg zurück steht also offen — die App sperrt niemanden aus, der es sich
anders überlegt.

---

## P11 im Einzelnen — durchgeführt am 28.09.2026

**Aufbau.** Zwei Teile: die Oberfläche am Gerät und die Sprache der Texte.

**Teil 1 — acht Sprachen, vierzig Bildschirme.** Die Fernwartung hat jede
Sprache eingestellt und in jeder fünf Bildschirme abgemessen: Startseite,
Levelansicht, Lektion, Einstellungen, Laden. Gemessen, nicht angesehen — jeder
Textknoten auf ein Muster wie `set.sicherung_suchen` geprüft, jeder Knopf auf
waagerechten Überlauf (`scrollWidth` gegen `clientWidth`, dazu der rechte Rand
gegen die Fensterbreite).

| Kriterium | Ergebnis |
|---|---|
| Kein roher Textschlüssel | keiner, in keiner Sprache |
| Kein Text sprengt den Knopf | **ein Fund** — siehe unten, behoben |
| `texte_pruefen.py` | meldet nichts: 404 Schlüssel in allen acht Sprachen, Platzhalter stimmen überein |

**Der Fund.** Im französischen Laden:

```
Knopf „♥ Regarder une vidéo"   braucht 155 px, hat 138 px   → 17 px zu breit
Zeile „Recharger un cœur"      307 px in 292 px             → dieselbe Ursache
```

Der Knopf steht auf `white-space: nowrap`, damit die Herzen-Zeile nicht
zerfällt — so wollte Ajdin sie am 27.09. Statt das Aussehen wieder
aufzumachen, wurde der Text gekürzt: **„♥ Regarder une vidéo" → „♥ Voir une
vidéo"**. Gleiche Bedeutung, geläufigere Wendung.

**Zwei Fehlalarme**, beide aus der Messung, nicht aus der App:
`kakosepise.info` ist eine Quellenangabe in den Danksagungen und sieht nur aus
wie ein Schlüssel; und `showShop` heißt in Wahrheit `showLaden` — mein
Skriptfehler, der den Laden im ersten Durchlauf gar nicht erst aufmachte.

**Teil 2 — die Sprache der Texte.** Der große Übersetzungsbericht vom
18.09.2026 deckt die Oberfläche ab, aber seitdem sind **elf Texte** dazu-
gekommen oder geändert worden: die acht neuen (`set.aussehen`,
`set.aussehen_sub`, die drei Theme-Knöpfe, `set.sicherung_suchen`,
`task.mikro_offline`, `werbung.keine_anzeige`) und drei geänderte (`app.fuss`,
`app.ueber_kurz`, `werbung.platzhalter`). Die waren noch von niemandem
gelesen.

Dafür lief je ein Prüfer pro Sprache, sieben gleichzeitig, jeder mit dem
deutschen Original daneben und der Erlaubnis nachzuschlagen. **21 Befunde,
alle eingearbeitet.** Die gewichtigsten:

| Sprache | Was | Warum |
|---|---|---|
| Französisch | „cherchez" → „cherche" | Anredebruch: diese eine Zeile siezte, alles andere duzt |
| Französisch | „Réglages" → „Paramètres" | „Réglages" ist der Apple-Begriff, Android sagt „Paramètres" |
| Türkisch | „Yüklemek" → „Geri yüklemek" | „yüklemek" heißt installieren; wiederherstellen ist „geri yüklemek" |
| Türkisch | „dilbilgisi" → „dil bilgisi" | TDK schreibt es getrennt — in einer Sprachlern-App fällt das auf |
| Schwedisch | „som telefonen är inställd" → „följ telefonens inställning" | „inställd" verlangt eine Präposition, der Satz brach ab |
| Dänisch | dasselbe mit „indstillet" | gleicher Fehler, gleiche Ursache: wörtlich aus dem Deutschen |
| Niederländisch | „Versie" → „versie" | Substantive werden klein geschrieben; auch Norwegisch und Französisch |
| Niederländisch | „taak" → „opgave" | „taak" ist für die Tagesaufgaben belegt, die Schwestertexte sagen „opgave" |

Auffällig ist das Muster: Fast alle Befunde sind **Germanismen** — Sätze, die
Wort für Wort aus dem Deutschen übertragen wurden und in der Zielsprache
unvollständig oder steif klingen. Genau die Stellen, die man im eigenen Text
nicht sieht.

**Gegenprobe.** Nach beiden Änderungen, Fassung 37 auf dem Gerät: acht
Sprachen, vierzig Bildschirme, **null Funde**.

---

## P13 im Einzelnen — durchgeführt am 28.09.2026

**Aufbau.** Die Grammatiklevel fangen erst bei Nummer 27 an („Fragen
stellen"), und offen sind bisher nur drei — es sind zwei Level bestanden.
Für die Prüfung wurden die davorliegenden Level kurz als bestanden
eingetragen; die Sicherung von vorher hat den echten Stand danach
zurückgespielt. Gespielt hat die Fernwartung, die Zurück-Taste kam als
echtes Android-Ereignis über `adb`.

**Teil 1 — ein Level mit Grammatikaufgaben.** Level 27 „Fragen stellen", 25
Wörter, sechs Grammatikübungen hinterlegt. Die Lektion enthielt alle
Aufgabenarten auf einmal:

```
intro 8 · gap 2 · mcrev 2 · mc 2 · gram 2 · speak 2 · type 1 · listen 1
```

Beide Grammatikaufgaben kamen richtig durch:

| Frage | Antwort |
|---|---|
| Ja/Nein-Frage: „Sprichst du Deutsch?" | Govoriš li njemački? |
| „___ ideš?" (Wohin gehst du?) | Kuda |

Ergebnis: **10 von 10**, 6 neue Wörter, Level-Fortschritt 24 %.
Die Sprechaufgaben wurden übersprungen — kein Mikrofon an der Fernwartung.

**Teil 2 — eine Geschichte lesen und ihre Fragen beantworten.** „Mira i Rex",
Kinderbuch, passt zu Level „Farben". In der Liste stehen 12 Geschichten,
11 davon gesperrt — die Reihenfolge stimmt also.

Der erste Anlauf ergab 2 von 3, und das war **mein Fehler, nicht der der
App**: mein Treiber zählte den Weiter-Schritt als Frage mit und ordnete
deshalb der zweiten Frage die dritte Antwort zu. Die App hat das richtig
gemeldet („2 von 3 richtig. Lies den Text noch einmal") und die Geschichte
folgerichtig **nicht** als gelesen eingetragen. Der zweite Anlauf über
„Fragen noch einmal" — diesmal mit der Frage aus dem Bildschirm statt aus
einem Zähler — ergab 3 von 3:

```
Wie heißt der Hund?      -> Rex
Welche Farbe hat Rex?    -> braun
Was isst Mira?           -> einen Apfel
```

Danach: „Geschichte geschafft! 🎉", `read` enthält `mira`, die Tagesaufgabe
„Eine Geschichte" zählte mit, das Lesedatum steht im Lernstand, und die
nächste Geschichte ist aufgegangen.

**Teil 3 — das eigentliche Kriterium: die Zurück-Wege.**

| Bildschirm | Zurück führt nach |
|---|---|
| Geschichte mit Ergebnis | Geschichtenliste |
| Geschichtenliste | Nachfrage „Zmaj wirklich schließen?" — oberste Ebene, richtig |
| Levelansicht | Lernpfad |
| Mitten in der Lektion | Nachfrage „Lektion abbrechen? Richtig beantwortete Wörter bleiben gespeichert." |
| ebendort, nach „Abbrechen" | Levelansicht |
| Ergebnisschirm der Lektion | Levelansicht, ohne Nachfrage — richtig, es ist nichts mehr abzubrechen |
| Mitten im Level-Test | Nachfrage „Test abbrechen? Er zählt dann nicht." |
| ebendort, nach „Abbrechen" | Levelansicht |
| Einstellungen | Lernpfad |
| Laden | Lernpfad |

**Kein einziger Bildschirm ist eine Sackgasse.** Kein zweimaliges Drücken
nötig, keine Nachfrage an der falschen Stelle, und die beiden Nachfragen
kommen genau dort, wo wirklich etwas verloren ginge.

**Eine Falle beim Messen**, die festgehalten gehört: Läuft nach einer Lektion
eine Anzeige, geht der erste Tipp auf Zurück an die Anzeige, nicht an die
App. Zweimal sah es dadurch so aus, als täte die Zurück-Taste auf dem
Ergebnisschirm nichts. Nachgewiesen wurde das über einen eigenen Horcher auf
`backButton`: die Ereignisse kamen an, sobald keine Anzeige mehr im Weg
stand. Für die saubere Messung wurde `zeigeWerbung()` kurz stillgelegt und
danach wieder eingeschaltet. **Kein Fehler der App** — aber gut zu wissen,
wenn später wieder jemand die Zurück-Wege misst.

**Aufgeräumt.** Der echte Stand ist zurückgespielt: 77 Wörter, Level
„basics" und „zahlen" bestanden, 550 Münzen, 5 Leben, zwei Lerntage. Die
gelesene Geschichte und die 25 eingetragenen Level sind damit wieder weg —
sie gehörten zur Prüfung, nicht zum Lernstand.
