# Store-Texte für Zmaj

> ## Stand 16.09.2026 – der Store ist das Ziel
>
> **Nicht mehr geparkt.** Die Konten sind raus, der Server ist raus, die
> Rechtstexte stehen öffentlich im Netz, AdMob ist eingebaut. Damit ist
> Google Play kein Plan mehr für irgendwann, sondern der nächste Schritt.
>
> **Herausgeber im Store: SmartDragon.** Unter diesem Namen erscheint die
> App, die Anschrift darunter ist deine. Das Programmkürzel ist
> `de.smartdragon.zmaj` (steht in `zmaj-android/capacitor.config.json`) und
> lässt sich nach der ersten Veröffentlichung nie wieder ändern.
>
> **Was noch fehlt, bevor du auf „Senden“ drückst:** die echten
> AdMob-Kennungen statt der Testkennungen, und – falls du die Vollversion
> verkaufen willst – das Abo in der Play Console. Beides steht unten im
> Abschnitt „Werbung, Preis und was heute stimmt“, mit Datei und Zeile.
>
> **Und trotzdem:** geh vor dem Einreichen jeden Absatz noch einmal gegen
> die App durch, wie sie an dem Tag wirklich ist. Ein Store-Text beschreibt
> den Stand bei der Einreichung, nicht den Plan von vorgestern.

Alles, was Google Play (und später Apple) an Texten verlangt, fertig zum
Kopieren. Die Zeichenzahlen stehen dabei, damit du nichts kürzen musst.

**Diese Datei ist nur zum Abschreiben da.** Die App liest sie nicht.

---

**Geviertstrich in den Kurzbeschreibungen.** Play warnt sonst: „Muss
Geviertstriche statt doppelter Bindestriche oder Halbgeviertstriche
enthalten." Die App wird dann nicht beworben. Deshalb steht in allen acht
Kurzbeschreibungen ein — und kein –. In den langen Beschreibungen ist der
Halbgeviertstrich weiterhin richtig, dort prueft Play das nicht.

## Was Google Play abfragt

Der Store-Eintrag selbst:

| Feld | Grenze | Pflicht |
|---|---|---|
| App-Name | 30 Zeichen | ja |
| Kurzbeschreibung | 80 Zeichen | ja |
| Vollständige Beschreibung | 4000 Zeichen | ja |
| App-Symbol | 512 × 512 px, 32-Bit-PNG **mit** Alphakanal, höchstens 1024 KB | ja |
| Vorstellungsgrafik (Feature-Grafik) | 1024 × 500 px, JPEG oder 24-Bit-PNG **ohne** Alphakanal | ja |
| Screenshots Telefon | 2 bis 8, Kante 320–3840 px, 9 : 16 oder 16 : 9 | ja |
| Screenshots Tablet 7″ und 10″ | je mindestens 4, Kante 1080–7680 px | nur für den Tablet-Eintrag |
| Datenschutzerklärung | **öffentliche Internetadresse** | ja |
| Kategorie | Bildung, dazu bis zu fünf Tags (z. B. Sprachen lernen) | ja |
| Kontakt-E-Mail | zmaj.lernapp@gmail.com | ja |
| Alterseinstufung | Fragebogen | ja |
| Data-Safety | Fragebogen | ja |

Und unter „App-Inhalte“ – das sind eigene Formulare, nicht Teil des
Eintrags. Ohne sie lässt sich nichts veröffentlichen:

| Formular | Deine Antwort |
|---|---|
| App-Zugriff | Alle Funktionen sind ohne besonderen Zugang erreichbar. Es gibt kein Konto, also keine Testzugangsdaten für die Prüfer. |
| Werbung | Ja, die App enthält Werbung. |
| Werbe-ID | Ja, die App verwendet sie – über das AdMob-SDK. Zweck: Werbung/Marketing und Analysen. |
| Datenlöschung | „Meine App lässt das Erstellen von Konten nicht zu.“ Adresse zum Löschen: https://zmaj-lernapp.github.io/konto-loeschen.html |
| Zielgruppe und Inhalte | 16–17 und 18+. Passt zu Punkt 2 der Nutzungsbedingungen („ab 16 Jahren“). Kreuzt du eine Gruppe unter 13 an, greift die Families-Richtlinie, und dann darf AdMob so nicht mehr laufen. |
| Regierung, Finanzen, Gesundheit, Nachrichten | jeweils nein |

Die Werbe-ID steckt wirklich in der App: im zusammengebauten Manifest
(`android/app/build/intermediates/merged_manifest/…`) steht
`com.google.android.gms.permission.AD_ID`. Das legt das AdMob-SDK selbst
dazu, du musst nichts eintragen – aber du musst es angeben.

Jedes Textfeld lässt sich pro Sprache hinterlegen. Wer nur Deutsch
einträgt, bekommt in Schweden auch Deutsch zu sehen.

---

## Werbung, Preis und was heute stimmt

**Die Werbung läuft.** `WERBUNG_LAEUFT` in sprachen.py steht auf `True`,
`WERBUNG_ECHT` in index.html übernimmt den Wert, und dahinter steckt
diesmal ein echtes Netzwerk: das Plugin `@capacitor-community/admob`
(siehe `zmaj-android/package.json`). Die Einwilligung holt Googles eigenes
Fenster über die User Messaging Platform; das selbstgebaute Fenster tritt
zurück, sobald sich das Plugin meldet, und läuft nur noch am PC.

Die Datenschutzerklärung zieht automatisch mit: sprachen.py wählt anhand
von `WERBUNG_LAEUFT` zwischen `set.dsgvo_werbung_aus` und
`set.dsgvo_werbung_an`. Auf der öffentlichen Seite steht deshalb schon der
Abschnitt über Google als Werbepartner. Store-Text und Datenschutzseite
sagen jetzt dasselbe – das war vorher nicht so.

**Deshalb ist der Absatz „Was es kostet“ in allen acht Beschreibungen
getauscht.** Dort steht jetzt der Satz mit der Werbung. Die alte Fassung
„zeigt keine Werbung“ ist weg, sie wäre eine Falschangabe.

### Drei Stellen mit Testkennungen – vor dem Hochladen tauschen

Zurzeit laufen Googles öffentliche Testanzeigen. Die bringen nichts ein,
und in einer veröffentlichten App sind sie ein Regelverstoß:

| Wo | Was steht da | Was hin muss |
|---|---|---|
| `zmaj-android/android/app/src/main/res/values/strings.xml`, `admob_app_id` | `ca-app-pub-3940256099942544~3347511713` | `ca-app-pub-9105747905460295~9760526209` |
| `web/index.html`, `ADMOB_ID.interstitial` | `ca-app-pub-3940256099942544/1033173712` | `ca-app-pub-9105747905460295/9764395638` |
| `web/index.html`, `ADMOB_ID.belohnt` | `ca-app-pub-3940256099942544/5224354917` | `ca-app-pub-9105747905460295/8572576770` |

**Von Hand ist das nicht nötig.** `admob_scharf.py` tauscht alle drei
Kennungen und setzt `ADMOB_TEST` auf `false`, mit Nachkontrolle, dass danach
keine Testkennung mehr in den Quellen steht:

```
python admob_scharf.py            # Probelauf, ändert nichts
python admob_scharf.py --schreiben
python app_bauen.py               # sonst liegt in der Hülle die alte index.html
```

**Erst nach dem geschlossenen Test laufen lassen** und erst, nachdem die
Befunde aus `WERBUNG_PRUEFUNG.md` abgearbeitet sind. Ein Tester, der aus
Hilfsbereitschaft eine echte Anzeige anklickt, erzeugt ungültigen Traffic –
und der kostet im Zweifel das AdMob-Konto, nicht nur die paar Cent.

### Die Vollversion ist eingebaut – der Rest liegt bei dir

Seit dem 19.09.2026 gibt es den Bezahlweg wirklich: die Play Billing
Library 9.1.0 hängt im Android-Teil, das eigene Plugin `ZmajAbo.java`
spricht mit ihr, und in den Einstellungen steht oben der Block
„Vollversion“ mit der Auswahl Monat oder Jahr.

**Preise stehen bewusst nirgends in einer Datei.** Weder in der App noch in
diesem Dokument noch in den AGB. Sie kommen zur Laufzeit von Google
(`getFormattedPrice`) – nur so stimmen sie in jedem Land, und Googles
Zahlungsrichtlinie verlangt, dass der Preis in der App dem im Kauffenster
entspricht. Geplant sind 2,99 € im Monat und 19,99 € im Jahr; eingetragen
werden sie **nur in der Play Console**.

Solange die Produkte dort nicht angelegt und **aktiviert** sind, antwortet
Google auf die Preisabfrage mit OK und einer leeren Liste. Die App zeigt
dann „Das hat gerade nicht geklappt“ – das sieht aus wie ein Programmfehler,
ist aber nur die fehlende Freischaltung.

Für den Store heißt das:

- In der Beschreibung steht das Abo **ohne Zahlen** – der Store zeigt den
  Landespreis von selbst.
- Im Formular zur Alterseinstufung heißt die Antwort auf „Käufe in der App“
  jetzt **ja**.
- Einstufung unter „Steuern und Compliance“: **Dienst**, nicht digitale
  Inhalte. Damit gibt Google dem Käufer selbst 14 Tage Erstattungsanspruch
  und wickelt ihn ab.

Erst wenn das Abo in der Play Console angelegt und der Kauf in der App
eingebaut ist, tauschst du den Absatz gegen den **Ersatzabsatz mit Abo**,
der unter jeder Beschreibung steht. Den Preis nennst du dann so, wie er in
der Console steht, oder du lässt die Zahl weg – im Store sieht der Nutzer
den Preis ohnehin, bevor er kauft, und eine Zahl im Beschreibungstext ist
nur eine Stelle mehr, die veralten kann.

Die Nutzungsbedingungen (`set.agb_text`) beschreiben das Abo schon: Abschluss
über Google Play, Google ist Vertragspartner für die Zahlung, Kündigung im
Google-Konto. Das passt, sobald es das Abo gibt.

### Was die Hörübungen heute wirklich tun

Die alten Beschreibungen sagten, die Sprachausgabe des Geräts lese den Satz
vor. Beides stimmt nicht mehr:

- Es ist **kein Satz, sondern ein Wort**. Die Höraufgabe spielt `w.bs` ab
  und lässt dich zwischen vier Wörtern wählen.
- Es ist **nicht die Stimme des Geräts**. In `web/audio` liegen 2153
  Tondateien: 2141 Wörter und Lückensätze und die 12 Geschichten. Die Sprachausgabe des
  Geräts springt nur ein, wenn zu einem Wort einmal keine Datei da ist –
  und in der Android-App gibt es sie meistens gar nicht, die System-WebView
  kennt `speechSynthesis` nicht.

Deshalb ist der Absatz in allen acht Beschreibungen umgeschrieben.

**Sag dabei nicht „eingesprochen“ oder „echte Stimme“.** Die Dateien kommen
aus einem Sprachdienst (ton_bauen.py, Stimme `bs-BA-…`). Es ist eine feste
bosnische Tonspur, keine Aufnahme eines Menschen. Sprichst du die Wörter
eines Tages selbst ein, darfst du damit werben – vorher nicht.

### Die Sprechaufgabe läuft inzwischen

Der Grund, sie aus den Beschreibungen zu nehmen, ist weggefallen:

- Das Plugin `@capacitor-community/speech-recognition` ist eingebaut und
  übernimmt, was die System-WebView nicht kann.
- `RECORD_AUDIO` steht im Manifest, dazu
  `<uses-feature android:name="android.hardware.microphone"
  android:required="false" />` – Geräte ohne Mikrofon dürfen die App
  trotzdem installieren.
- Die App fragt selbst nach der Erlaubnis, bevor die erste Sprechaufgabe
  kommt (`mikroVorbereiten()` in `web/index.html`).

**Erledigt am 19.09.2026:** Der Absatz steht wieder in allen acht
Beschreibungen, hinter dem Absatz über die Aussprache.

Er ist dabei **neu geschrieben** worden, nicht bloß zurückkopiert. Der alte
Wortlaut sagte „du hörst das Wort und sprichst es ins Mikrofon“ – die App
zeigt das Wort aber geschrieben an, vorgelesen wird es nur, wenn du auf
„Vorsprechen“ tippst. Das ist derselbe Fehlertyp wie „Satz“ statt „Wort“ bei
der Höraufgabe eine Ecke weiter oben: eine Beschreibung, die eine Kleinigkeit
anders darstellt, als die App es tut. Der neue Absatz nennt außerdem, dass die
Spracherkennung die **des Geräts** ist – das passt zu dem, was im
Data-Safety-Formular steht.

---

# 1. Deutsch
**App-Name** (22 Zeichen)

```
Zmaj – Bosnisch lernen
```

**Kurzbeschreibung** (73 Zeichen)

```
Bosnisch lernen für Familie, Alltag und Amt — 63 Levels in kurzen Übungen
```

**Vollständige Beschreibung** (3505 von 4000 Zeichen)

```
Du hast Familie in Bosnien, bosnische Wurzeln oder Schwiegereltern, mit denen du endlich selbst reden willst, ohne dass jemand übersetzt? Zmaj bringt dir Bosnisch bei: 63 Levels, kurze Übungen, vom Alltag bis zum Arbeitsvertrag.

WAS DU LERNST

Drei Sektionen, eine nach der anderen.

"Grundlagen & Alltag" beginnt bei den ersten Wörtern und bei dem, was du jeden Tag brauchst.

"Sätze bauen" zeigt dir, wie aus einzelnen Wörtern eigene Sätze werden.

"Amt & Verträge" nimmt sich das vor, wovor viele Respekt haben: Behördengang, Arbeitsvertrag, Wohnungssuche, Bank, Arzt. Also die Situationen, in denen man sonst jemanden mitnehmen muss.

Insgesamt drin:

• 1668 Wörter und Wendungen
• 290 Lückentext-Sätze
• 16 Grammatik-Lektionen mit zusammen 104 Übungen zu Fällen, Zeiten und Verbbeugung
• 12 Lesegeschichten, jedes Wort antippbar mit Übersetzung
• am Ende jedes Levels ein Test

WIE GEÜBT WIRD

Die Aufgaben wechseln sich ab: Bedeutung erkennen, das bosnische Wort finden, es selbst eintippen, eine Lücke im Satz füllen und die Grammatikübungen.

Die Aussprache bringt die App mit: Zu jedem Wort gehört eine Tondatei mit bosnischer Stimme, und die zwölf Geschichten lassen sich am Stück anhören. In der Höraufgabe spielst du ein Wort ab und wählst, welches es war. So hörst du die Wörter, statt sie nur zu lesen – auch auf einem Gerät, das selbst keine bosnische Stimme kennt.

Bringt dein Gerät eine Spracherkennung mit, kommt die Sprechaufgabe dazu: Das bosnische Wort steht da, auf Knopfdruck hörst du es, und dann sagst du es selbst ins Mikrofon. Die Erkennung deines Geräts gleicht ab, ob es gepasst hat. So bekommst du die Wörter auch über die Lippen, nicht nur ins Ohr.

In den Lesegeschichten tippst du jedes Wort an, das du nicht kennst, und siehst die Übersetzung.

IST BOSNISCH SCHWER ZU LERNEN?

Die Wörter sind das kleinere Problem. Was hakt, sind die Fälle und die Verbbeugung. Genau dafür gibt es die 16 Grammatik-Lektionen mit ihren 104 Übungen: Du arbeitest dich Schritt für Schritt durch, statt Tabellen auswendig zu lernen.

BOSNISCH, KROATISCH ODER SERBISCH?

Die Inhalte folgen dem "Pravopis bosanskoga jezika" von Senahid Halilović. Gelernt wird ijekavisch: mlijeko, lijep, vrijeme. Also so, wie in Bosnien gesprochen wird.

BRAUCHE ICH VORKENNTNISSE?

Nein. Die erste Sektion heißt "Grundlagen & Alltag" und fängt genau dort an.

Und wenn du schon einiges verstehst, weil du es zu Hause gehört hast, dich aber nie mit Fällen und Zeiten beschäftigt hast: Die Grammatik-Lektionen und die Lesegeschichten sind meistens genau der Teil, der dann fehlt.

DRANBLEIBEN

Du hast fünf Leben, die von selbst nachwachsen. Die Lernserie zählt die Tage, an denen du geübt hast, und ein Serienschutz fängt einen verpassten Tag ab, wenn das Leben dazwischenkommt.

DEINE SPRACHE

Die Oberfläche gibt es auf Deutsch, Englisch, Türkisch, Schwedisch, Niederländisch, Norwegisch, Dänisch und Französisch. Praktisch, wenn in der Familie mehrere Sprachen zusammenkommen. Gelernt wird Bosnisch, und nur Bosnisch.

WER IST ZMAJ?

Zmaj heißt auf Bosnisch Drache. Er ist blau und sitzt auf einem Bücherstapel.

WER DIE APP GEBAUT HAT

Eine einzelne Person. Ich habe Zmaj für meine Frau gebaut, weil ich für Bosnisch nichts gefunden habe, das über Vokabellisten hinausgeht. Deshalb steckt in der App genau das, was ihr gefehlt hat: Grammatik zum Üben, Texte zum Lesen und die Sprache, die man auf dem Amt braucht.

WAS ES KOSTET

Zmaj ist kostenlos und finanziert sich über Werbung.

Sretno. Viel Erfolg.
```

**Ersatzabsatz „Was es kostet“ – gilt erst, wenn das Abo im Store steht**

Tausch den Absatz unter „WAS ES KOSTET“ oben gegen diesen hier, sobald das
Abo in der Play Console angelegt und der Kauf in der App eingebaut ist.
Prüf den Preis gegen die Console, oder streich die Zahlen.

```
Zmaj ist kostenlos und finanziert sich über Werbung. Wenn du ohne Werbung und mit unbegrenzten Leben lernen willst, gibt es die Vollversion als Abo – monatlich oder jährlich.
```

**Apple: Untertitel** (30 Zeichen)

```
Wörter, Grammatik, Geschichten
```

**Apple: Schlüsselwörter** (92 Zeichen)

```
bosnisch,bosnien,balkan,sprachkurs,vokabeln,grammatik,serbisch,kroatisch,sarajevo,ijekavisch
```

---

# 2. English

**App-Name** (20 Zeichen)

```
Zmaj – Learn Bosnian
```

**Kurzbeschreibung** (76 Zeichen)

```
Learn Bosnian for family, daily life and paperwork — 43 levels, short drills
```

**Vollständige Beschreibung** (3427 von 4000 Zeichen)

```
Family in Bosnia, Bosnian roots, or Bosnian in-laws: at some point you want to do the talking yourself, without someone translating in between. You probably understand more than you can say. Zmaj teaches you Bosnian: 43 levels, short exercises, from everyday talk to an employment contract.

WHAT YOU LEARN

Three sections, one after the other.

“Basics & everyday life” starts with the first words and with what you need every day.

“Building sentences” shows you how single words turn into sentences of your own.

“Offices & contracts” takes on the part many people are wary of: the government office, the employment contract, finding an apartment, the bank, the doctor. The situations where you would otherwise have to bring someone along.

In total:

• 1668 words and phrases
• 290 fill-in-the-blank sentences
• 16 grammar lessons with 104 exercises in total, on cases, tenses and verb endings
• 12 reading stories, every word tappable for a translation
• a test at the end of every level

HOW YOU PRACTICE

The exercises take turns: recognize the meaning, pick the Bosnian word, type it out yourself, fill the gap in a sentence, and work through the grammar drills.

The pronunciation comes with the app: every word has a sound file in a Bosnian voice, and the twelve stories can be played from beginning to end. In the listening task you play a word and choose which one it was. So you hear the words instead of only reading them – even on a device that has no Bosnian voice of its own.

If your device has speech recognition built in, the speaking task is there too: the Bosnian word in writing, a button to hear it spoken, and then you say it into the microphone yourself. Your device's own recognition checks whether what it heard matches the word.

In the reading stories you tap any word you do not know and see the translation.

IS BOSNIAN HARD TO LEARN?

The words are the smaller problem. What trips people up are the cases and the verb endings. That is exactly what the 16 grammar lessons and their 104 exercises are for: you work through them step by step instead of memorizing tables.

BOSNIAN, CROATIAN OR SERBIAN?

The content follows the “Pravopis bosanskoga jezika” by Senahid Halilović. What you learn is Ijekavian: mlijeko, lijep, vrijeme. The way it is spoken in Bosnia.

DO I NEED ANY PRIOR KNOWLEDGE?

No. The first section is called “Basics & everyday life” and starts right there.

And if you already understand a fair amount because you grew up hearing it at home, but never sat down with cases and tenses: the grammar lessons and the reading stories are usually the missing piece.

KEEPING IT UP

You have five lives and they grow back on their own. The streak counts the days you practiced, and streak protection covers one missed day when life gets in the way.

YOUR LANGUAGE

The interface comes in English, German, Turkish, Swedish, Dutch, Norwegian, Danish and French. Useful when more than one language runs in the family. What you learn is Bosnian, and only Bosnian.

WHO IS ZMAJ?

Zmaj is Bosnian for dragon. He is blue and sits on a stack of books.

WHO BUILT THE APP

One person. I built Zmaj for my wife, because I could not find anything for Bosnian that went beyond vocabulary lists. So the app holds exactly what she was missing: grammar to practice, texts to read, and the language you need at a government office.

WHAT IT COSTS

Zmaj is free and funded by ads.

Sretno. Good luck.
```

**Ersatzabsatz „WHAT IT COSTS“ – gilt erst, wenn das Abo im Store steht**

```
Zmaj is free and funded by ads. If you want to learn without ads and with unlimited lives, there is a full version as a subscription – monthly or yearly.
```

**Apple: Untertitel** (26 Zeichen)

```
Words, grammar and stories
```

**Apple: Schlüsselwörter** (90 Zeichen)

```
bosnian,bosnia,balkan,language,vocabulary,grammar,serbian,croatian,sarajevo,phrases,travel
```

---

# 3. Türkçe

**App-Name** (21 Zeichen)

```
Zmaj – Boşnakça öğren
```

**Kurzbeschreibung** (78 Zeichen)

```
Aile, günlük hayat ve resmî işler için Boşnakça — 43 seviye, kısa alıştırmalar
```

**Vollständige Beschreibung** (3409 von 4000 Zeichen)

```
Dedenden, ninenden duya duya bir şeyler anlıyor ama kendin konuşamıyor musun? Boşnak kökenli bir ailede büyüdüysen, Bosna'da akrabaların varsa ya da eşinin ailesiyle aracısız konuşmak istiyorsan: Zmaj sana Boşnakçayı baştan öğretiyor. 43 seviye, kısa alıştırmalar, günlük hayattan iş sözleşmesine kadar.

NELER ÖĞRENİYORSUN?

Üç bölüm, sırayla.

“Temeller ve günlük hayat” ilk kelimelerle başlıyor ve her gün ihtiyaç duyduğun şeyleri veriyor.

“Cümle kurmak” tek tek kelimelerden kendi cümlelerini nasıl kuracağını gösteriyor.

“Resmî işler ve sözleşmeler” birçok kişinin çekindiği kısmı ele alıyor: resmî daire işleri, iş sözleşmesi, ev arama, banka, doktor. Yani normalde yanına birini almak zorunda kaldığın durumlar.

Uygulamanın içinde:

• 1668 kelime ve kalıp
• 290 boşluk doldurma cümlesi
• 16 dil bilgisi dersi, toplam 104 alıştırma: hâller, zamanlar, fiil çekimi
• 12 okuma hikâyesi, her kelimeye dokununca çevirisi
• her seviyenin sonunda bir test

NASIL ALIŞTIRMA YAPIYORSUN?

Alıştırmalar birbirini izliyor: anlamı seçmek, kelimenin Boşnakçasını bulmak, kelimeyi kendin yazmak, cümledeki boşluğu doldurmak ve dil bilgisi alıştırmaları.

Telaffuz uygulamanın içinde geliyor: her kelimenin Boşnakça sesli bir dosyası var, on iki hikâyeyi de baştan sona dinleyebiliyorsun. Dinleme alıştırmasında bir kelimeyi çalıyor, hangisi olduğunu seçiyorsun. Böylece kelimeleri sadece okumakla kalmıyor, duyuyorsun da – cihazında Boşnakça bir ses olmasa bile.

Konuşma alıştırmasında Boşnakça kelime karşında yazılı duruyor; istersen önce bir kez dinliyorsun, sonra mikrofona dokunup kendin söylüyorsun. Cihazının kendi konuşma tanıma özelliği söylediğini kelimeyle karşılaştırıyor. Kelimeler bir kez de senin ağzından çıkmış oluyor – konuşma tanıması olan her cihazda.

Okuma hikâyelerinde bilmediğin her kelimeye dokunuyor, çevirisini görüyorsun.

BOŞNAKÇA ÖĞRENMEK ZOR MU?

Kelimeler işin kolay tarafı. Asıl takıldığın yer hâller ve fiil çekimi oluyor. 16 dil bilgisi dersi ve 104 alıştırma tam bunun için var: tablo ezberlemek yerine adım adım ilerliyorsun.

BOŞNAKÇA MI, HIRVATÇA MI, SIRPÇA MI?

İçerikler Senahid Halilović'in “Pravopis bosanskoga jezika” eserini esas alıyor. Öğrendiğin biçim ijekavca: mlijeko, lijep, vrijeme. Yani Bosna'da konuşulduğu gibi.

ÖN BİLGİ GEREKİYOR MU?

Hayır. İlk bölümün adı “Temeller ve günlük hayat” ve tam oradan başlıyor.

Evde duya duya bir kısmını zaten anlıyorsan ama hâllerle ve zamanlarla hiç uğraşmadıysan: eksik kalan kısım genelde tam olarak dil bilgisi dersleri ve okuma hikâyeleri oluyor.

DEVAMINI GETİRMEK

Beş canın var, harcadıkların kendiliğinden geri geliyor. Seri, alıştırma yaptığın günleri sayıyor; araya hayat girdiğinde seri koruması kaçırdığın bir günü karşılıyor.

SENİN DİLİN

Arayüzü Türkçe, Almanca, İngilizce, İsveççe, Felemenkçe, Norveççe, Danca ve Fransızca olarak kullanabilirsin. Ailede birden fazla dil bir araya geliyorsa işine yarıyor. Öğrenilen dil Boşnakça, sadece Boşnakça.

ZMAJ KİM?

Zmaj, Boşnakçada ejderha demek. Kendisi mavi ve bir kitap yığınının üstünde oturuyor.

UYGULAMAYI KİM YAPTI?

Tek bir kişi. Zmaj'ı eşim için yaptım, çünkü Boşnakça için kelime listelerinin ötesine geçen bir şey bulamadım. Bu yüzden uygulamada tam da onun eksiğini hissettiği şeyler var: çalışılacak dil bilgisi, okunacak metinler ve resmî işlerde gereken dil.

NE KADAR TUTUYOR?

Zmaj ücretsiz ve reklamlarla finanse ediliyor.

Sretno. Başarılar.
```

**Ersatzabsatz „NE KADAR TUTUYOR?“ – gilt erst, wenn das Abo im Store steht**

```
Zmaj ücretsiz ve reklamlarla finanse ediliyor. Reklamsız ve sınırsız canla çalışmak istersen tam sürüm abonelik olarak sunuluyor – aylık veya yıllık.
```

**Apple: Untertitel** (28 Zeichen)

```
Kelime, dilbilgisi ve hikâye
```

**Apple: Schlüsselwörter** (84 Zeichen)

```
boşnakça,bosna,balkan,dil,kelime,dilbilgisi,sırpça,hırvatça,saraybosna,seyahat,öğren
```

---

# 4. Svenska

**App-Name** (23 Zeichen)

```
Zmaj – Lär dig bosniska
```

**Kurzbeschreibung** (76 Zeichen)

```
Lär dig bosniska för familj, vardag och myndigheter — 43 nivåer i korta pass
```

**Vollständige Beschreibung** (3217 von 4000 Zeichen)

```
Har du familj i Bosnien, bosniska rötter eller svärföräldrar som du äntligen vill prata med själv, utan att någon översätter åt dig? Zmaj lär dig bosniska: 43 nivåer, korta övningar, från vardagen till anställningsavtalet.

DET HÄR LÄR DU DIG

Tre sektioner, en i taget.

”Grunderna & vardagen” börjar med de första orden och med det du behöver varje dag.

”Bygga meningar” visar hur enstaka ord blir dina egna meningar.

”Myndigheter & avtal” tar sig an det som många drar sig för: myndighetsbesök, anställningsavtal, bostadsjakt, banken, läkaren. Alltså situationerna där man annars brukar ta med sig någon.

Allt som ingår:

• 1668 ord och uttryck
• 290 meningar med lucka
• 16 grammatiklektioner med sammanlagt 104 övningar om kasus, tempus och verbböjning
• 12 läsberättelser, varje ord går att trycka på för översättning
• ett test i slutet av varje nivå

SÅ HÄR ÖVAR DU

Uppgifterna växlar: känna igen betydelsen, hitta det bosniska ordet, skriva in det själv, fylla luckan i en mening och grammatikövningarna.

Uttalet följer med i appen: varje ord har en ljudfil med bosnisk röst, och de tolv berättelserna går att lyssna på i ett svep. I lyssningsuppgiften spelar du upp ett ord och väljer vilket det var. Så hör du orden i stället för att bara läsa dem – även på en enhet som inte har någon bosnisk röst själv.

I taluppgiften står det bosniska ordet på skärmen. Du kan lyssna på det först, och sedan säger du det själv i mikrofonen. Enhetens egen taligenkänning kontrollerar om det blev rätt. På så sätt får du också säga orden högt – på varje enhet som har taligenkänning.

I läsberättelserna trycker du på varje ord du inte kan och ser översättningen.

ÄR BOSNISKA SVÅRT ATT LÄRA SIG?

Orden är det mindre problemet. Det som skaver är kasusen och verbböjningen. Just därför finns de 16 grammatiklektionerna med sina 104 övningar: du arbetar dig igenom dem steg för steg i stället för att plugga tabeller utantill.

BOSNISKA, KROATISKA ELLER SERBISKA?

Innehållet följer ”Pravopis bosanskoga jezika” av Senahid Halilović. Du lär dig ijekaviska: mlijeko, lijep, vrijeme. Alltså så som det talas i Bosnien.

BEHÖVER JAG FÖRKUNSKAPER?

Nej. Första sektionen heter ”Grunderna & vardagen” och börjar precis där.

Och om du redan förstår en del för att du har hört språket hemma, men aldrig har satt dig in i kasus och tempus: grammatiklektionerna och läsberättelserna är oftast just det som saknas.

FORTSÄTT ÖVA

Du har fem liv som fylls på av sig själva. Streaken räknar dagarna du har övat, och ett streakskydd fångar upp en missad dag när livet kommer emellan.

DITT SPRÅK

Gränssnittet finns på svenska, tyska, engelska, turkiska, nederländska, norska, danska och franska. Praktiskt när flera språk möts i familjen. Det du lär dig är bosniska, och bara bosniska.

VEM ÄR ZMAJ?

Zmaj betyder drake på bosniska. Han är blå och sitter på en bokhög.

VEM SOM HAR BYGGT APPEN

En enda person. Jag byggde Zmaj åt min fru, eftersom jag inte hittade något för bosniska som gick längre än ordlistor. Därför innehåller appen precis det som hon saknade: grammatik att öva på, texter att läsa och språket man behöver hos myndigheterna.

VAD DET KOSTAR

Zmaj är gratis och finansieras med reklam.

Sretno. Lycka till.
```

**Ersatzabsatz „VAD DET KOSTAR“ – gilt erst, wenn das Abo im Store steht**

```
Zmaj är gratis och finansieras med reklam. Vill du lära dig utan reklam och med obegränsade liv, finns fullversionen som prenumeration – per månad eller per år.
```

**Apple: Untertitel** (30 Zeichen)

```
Ord, grammatik och berättelser
```

**Apple: Schlüsselwörter** (82 Zeichen)

```
bosniska,bosnien,balkan,språk,ordförråd,grammatik,serbiska,kroatiska,sarajevo,resa
```

---

# 5. Nederlands

**App-Name** (21 Zeichen)

```
Zmaj – Bosnisch leren
```

**Kurzbeschreibung** (74 Zeichen)

```
Bosnisch leren voor familie, dagelijks leven en overheid — 43 korte levels
```

**Vollständige Beschreibung** (3468 von 4000 Zeichen)

```
Heb je familie in Bosnië, Bosnische roots of schoonouders met wie je eindelijk zelf wilt praten, zonder dat er iemand tussen zit om te vertalen? Zmaj leert je Bosnisch: 43 levels, korte oefeningen, van het dagelijks leven tot het arbeidscontract.

WAT JE LEERT

Drie secties, één voor één.

‘Basis & dagelijks leven’ begint bij de eerste woorden en bij wat je elke dag nodig hebt.

‘Zinnen bouwen’ laat zien hoe losse woorden jouw eigen zinnen worden.

‘Overheid & contracten’ gaat over de dingen waar veel mensen tegenop zien: het loket, het arbeidscontract, een woning zoeken, de bank, de dokter. Precies de situaties waarbij je anders iemand mee moet nemen.

Alles bij elkaar:

• 1668 woorden en uitdrukkingen
• 290 invulzinnen
• 16 grammaticalessen met in totaal 104 oefeningen over naamvallen, tijden en werkwoordsvervoeging
• 12 leesverhalen, elk woord aantikbaar met vertaling
• aan het eind van elk level een toets

HOE JE OEFENT

De opdrachten wisselen elkaar af: de betekenis herkennen, het Bosnische woord kiezen, het zelf intypen, het ontbrekende woord in een zin invullen en de grammaticaoefeningen.

De uitspraak zit in de app: bij elk woord hoort een geluidsbestand met een Bosnische stem, en de twaalf verhalen kun je in één keer beluisteren. Bij de luisteropdracht speel je een woord af en kies je welk woord het was. Zo hoor je de woorden in plaats van ze alleen te lezen – ook op een apparaat dat zelf geen Bosnische stem heeft.

Bij de spreekopdracht staat het Bosnische woord op het scherm. Je kunt het eerst laten horen en daarna zeg je het zelf in de microfoon. De spraakherkenning van je apparaat controleert of het klopt. Zo krijg je de woorden ook echt over je lippen – op elk apparaat met spraakherkenning.

In de leesverhalen tik je elk woord aan dat je niet kent en zie je de vertaling.

IS BOSNISCH MOEILIJK?

De woorden zijn niet het grootste probleem. Wat hapert, zijn de naamvallen en de werkwoordsvervoeging. Daar zijn de 16 grammaticalessen met hun 104 oefeningen voor: je werkt je er stap voor stap doorheen in plaats van tabellen uit je hoofd te leren.

BOSNISCH, KROATISCH OF SERVISCH?

De inhoud volgt de ‘Pravopis bosanskoga jezika’ van Senahid Halilović. Je leert de ijekavische vorm: mlijeko, lijep, vrijeme. Dus zoals er in Bosnië gesproken wordt.

HEB IK VOORKENNIS NODIG?

Nee. De eerste sectie heet ‘Basis & dagelijks leven’ en begint precies daar.

En begrijp je al het een en ander omdat je het thuis hebt gehoord, maar heb je je nooit met naamvallen en tijden beziggehouden? Dan zijn de grammaticalessen en de leesverhalen meestal precies het stuk dat ontbreekt.

VOLHOUDEN

Je hebt vijf levens en die groeien vanzelf weer aan. De leerreeks telt de dagen waarop je hebt geoefend, en een reeksbescherming vangt een gemiste dag op als het leven ertussen komt.

JOUW TAAL

De bediening is er in het Nederlands, Duits, Engels, Turks, Zweeds, Noors, Deens en Frans. Handig als er in de familie meerdere talen samenkomen. Je leert Bosnisch, en alleen Bosnisch.

WIE IS ZMAJ?

Zmaj is Bosnisch voor draak. Hij is blauw en zit op een stapel boeken.

WIE DE APP HEEFT GEMAAKT

Eén persoon. Ik heb Zmaj voor mijn vrouw gebouwd, omdat ik voor Bosnisch niets kon vinden dat verder ging dan woordenlijsten. Daarom zit in de app precies wat zij miste: grammatica om te oefenen, teksten om te lezen en de taal die je bij het loket nodig hebt.

WAT HET KOST

Zmaj is gratis en wordt gefinancierd met advertenties.

Sretno. Veel succes.
```

**Ersatzabsatz „WAT HET KOST“ – gilt erst, wenn das Abo im Store steht**

```
Zmaj is gratis en wordt gefinancierd met advertenties. Wil je zonder advertenties en met onbeperkte levens leren, dan is er de volledige versie als abonnement – per maand of per jaar.
```

**Apple: Untertitel** (29 Zeichen)

```
Woorden, grammatica, verhalen
```

**Apple: Schlüsselwörter** (86 Zeichen)

```
bosnisch,bosnie,balkan,taal,woordenschat,grammatica,servisch,kroatisch,sarajevo,reizen
```

---

# 6. Norsk bokmål

**App-Name** (18 Zeichen)

```
Zmaj – Lær bosnisk
```

**Kurzbeschreibung** (75 Zeichen)

```
Lær bosnisk for familie, hverdag og det offentlige — 43 nivåer, korte økter
```

**Vollständige Beschreibung** (3250 von 4000 Zeichen)

```
Har du familie i Bosnia, bosniske røtter eller svigerforeldre du endelig vil snakke med selv, uten at noen oversetter? Zmaj lærer deg bosnisk: 43 nivåer, korte økter, fra hverdagen til arbeidskontrakten.

DETTE LÆRER DU

Tre seksjoner, én om gangen.

«Grunnlaget & hverdagen» begynner med de første ordene og med det du bruker hver dag.

«Bygge setninger» viser deg hvordan enkeltord blir til dine egne setninger.

«Offentlige kontorer & avtaler» tar for seg det mange kvier seg for: møtet med det offentlige, arbeidskontrakten, boligjakten, banken, legen. Altså situasjonene der du ellers må ha med deg noen.

Til sammen får du:

• 1668 ord og uttrykk
• 290 setninger der du fyller inn ordet som mangler
• 16 grammatikkleksjoner med til sammen 104 øvelser i kasus, tider og verbbøying
• 12 lesehistorier der du kan trykke på hvert ord og få oversettelsen
• en test på slutten av hvert nivå

SLIK ØVER DU

Oppgavetypene veksler: kjenne igjen betydningen, finne ordet på bosnisk, skrive det inn selv, fylle inn ordet som mangler i setningen, og grammatikkøvelsene.

Uttalen følger med i appen: hvert ord har en lydfil med bosnisk stemme, og de tolv lesehistoriene kan du høre i ett strekk. I lytteoppgaven spiller du av et ord og velger hvilket det var. Slik hører du ordene i stedet for bare å lese dem – også på en enhet som ikke har noen bosnisk stemme selv.

I taleoppgaven står det bosniske ordet skrevet, og du kan høre det først om du vil. Så trykker du på mikrofonen og sier ordet, og talegjenkjenningen på enheten din sjekker om det stemmer. Da får du sagt ordene høyt selv, så lenge enheten har talegjenkjenning.

I lesehistoriene trykker du på hvert ord du ikke kjenner, og ser oversettelsen.

ER BOSNISK VANSKELIG Å LÆRE?

Ordene er det minste problemet. Det som stopper opp, er kasusene og verbbøyingen. Nettopp derfor finnes de 16 grammatikkleksjonene med sine 104 øvelser: Du jobber deg gjennom steg for steg i stedet for å pugge tabeller.

BOSNISK, KROATISK ELLER SERBISK?

Innholdet følger «Pravopis bosanskoga jezika» av Senahid Halilović. Du lærer ijekavisk: mlijeko, lijep, vrijeme. Altså slik det snakkes i Bosnia.

MÅ JEG KUNNE NOE FRA FØR?

Nei. Den første seksjonen heter «Grunnlaget & hverdagen» og begynner nettopp der.

Og hvis du allerede forstår en del fordi du har hørt språket hjemme, men aldri har satt deg ned med kasus og tider: Grammatikkleksjonene og lesehistoriene er som regel akkurat den delen som mangler.

HOLDE DET GÅENDE

Du har fem liv, og de fylles på av seg selv. Læringsrekken teller dagene du har øvd, og en rekkebeskyttelse fanger opp én glemt dag når livet kommer i veien.

DITT SPRÅK

Grensesnittet finnes på norsk, engelsk, tysk, tyrkisk, svensk, dansk, nederlandsk og fransk. Praktisk når det er flere språk i familien. Det du lærer, er bosnisk – og bare bosnisk.

HVEM ER ZMAJ?

Zmaj betyr drage på bosnisk. Han er blå og sitter på en stabel med bøker.

HVEM HAR LAGET APPEN?

Én person. Jeg lagde Zmaj til kona mi, fordi jeg ikke fant noe for bosnisk som gikk lenger enn gloselister. Derfor inneholder appen akkurat det hun savnet: grammatikk å øve på, tekster å lese og språket du trenger i møte med det offentlige.

HVA DET KOSTER

Zmaj er gratis og finansieres med reklame.

Sretno. Lykke til.
```

**Ersatzabsatz „HVA DET KOSTER“ – gilt erst, wenn das Abo im Store steht**

```
Zmaj er gratis og finansieres med reklame. Vil du lære uten reklame og med ubegrenset antall liv, finnes fullversjonen som abonnement – per måned eller per år.
```

**Apple: Untertitel** (29 Zeichen)

```
Ord, grammatikk, fortellinger
```

**Apple: Schlüsselwörter** (80 Zeichen)

```
bosnisk,bosnia,balkan,språk,ordforråd,grammatikk,serbisk,kroatisk,sarajevo,reise
```

---

# 7. Dansk

**App-Name** (18 Zeichen)

```
Zmaj – Lær bosnisk
```

**Kurzbeschreibung** (67 Zeichen)

```
Lær bosnisk til familie, hverdag og myndigheder — 43 korte niveauer
```

**Vollständige Beschreibung** (3366 von 4000 Zeichen)

```
Har du familie i Bosnien, bosniske rødder eller svigerforældre, du endelig selv vil kunne tale med, uden at nogen oversætter? Måske forstår du det meste, men svarer på dansk. Zmaj lærer dig bosnisk: 43 niveauer, korte øvelser, fra hverdagen til ansættelseskontrakten.

DET LÆRER DU

Tre sektioner, en ad gangen.

»Grundlaget & hverdagen« begynder ved de første ord og ved det, du bruger hver dag.

»Bygge sætninger« viser dig, hvordan de enkelte ord bliver til dine egne sætninger.

»Myndigheder & aftaler« tager fat i det, som mange har respekt for: kommunen, ansættelseskontrakten, boligsøgningen, banken, lægen. Altså de situationer, hvor man ellers skal have en med.

I alt er der:

• 1668 ord og vendinger
• 290 sætninger med huller, du skal udfylde
• 16 grammatiklektioner med i alt 104 øvelser i kasus, tider og bøjning af udsagnsord
• 12 læsehistorier, hvor du kan trykke på hvert ord og se oversættelsen
• en test til sidst i hvert niveau

SÅDAN ØVER DU

Opgavetyperne skifter: genkend betydningen, find det bosniske ord, tast ordet ind selv, udfyld hullet i sætningen og grammatikøvelserne.

Udtalen følger med i appen: hvert ord har en lydfil med bosnisk stemme, og de tolv læsehistorier kan du høre i ét stræk. I lytteopgaven afspiller du et ord og vælger, hvilket det var. På den måde hører du ordene i stedet for kun at læse dem – også på en enhed, der ikke selv har en bosnisk stemme.

I taleopgaven står det bosniske ord på skærmen, og du kan få det læst op først. Derefter trykker du på mikrofonen og siger ordet selv, mens enhedens egen talegenkendelse lytter med og tjekker, om det passer. Sådan får du sagt ordene højt, så længe enheden har talegenkendelse indbygget.

I læsehistorierne trykker du på hvert ord, du ikke kender, og ser oversættelsen.

ER BOSNISK SVÆRT AT LÆRE?

Ordene er den nemmeste del. Det, der driller, er kasus og bøjningen af udsagnsordene. Præcis derfor er der 16 grammatiklektioner med 104 øvelser: Du arbejder dig igennem skridt for skridt i stedet for at lære tabeller udenad.

BOSNISK, KROATISK ELLER SERBISK?

Indholdet følger »Pravopis bosanskoga jezika« af Senahid Halilović. Du lærer ijekavisk: mlijeko, lijep, vrijeme. Altså sådan, som der tales i Bosnien.

SKAL JEG KUNNE NOGET I FORVEJEN?

Nej. Den første sektion hedder »Grundlaget & hverdagen« og begynder præcis der.

Og forstår du allerede en del, fordi du har hørt det hjemme, men aldrig har siddet med kasus og tider: Grammatiklektionerne og læsehistorierne er som regel lige netop den del, der mangler.

BLIV VED

Du har fem liv, og de vokser frem igen af sig selv. Din streak tæller de dage, du har øvet dig, og en streakbeskyttelse fanger den dag, du springer over, når hverdagen kommer i vejen.

DIT SPROG

Menuer og tekster findes på dansk, tysk, engelsk, tyrkisk, svensk, nederlandsk, norsk og fransk. Praktisk, når der er flere sprog i familien. Det, du lærer, er bosnisk – og kun bosnisk.

HVEM ER ZMAJ?

Zmaj betyder drage på bosnisk. Han er blå og sidder på en stak bøger.

HVEM DER HAR LAVET APPEN

Én person. Jeg har bygget Zmaj til min kone, fordi jeg ikke kunne finde noget til bosnisk, der rakte ud over gloselister. Derfor er der præcis det i appen, som hun manglede: grammatik at øve på, tekster at læse og det sprog, man har brug for hos myndighederne.

HVAD DET KOSTER

Zmaj er gratis og finansieret af reklamer.

Sretno. Held og lykke.
```

**Ersatzabsatz „HVAD DET KOSTER“ – gilt erst, wenn das Abo im Store steht**

```
Zmaj er gratis og finansieret af reklamer. Vil du lære uden reklamer og med ubegrænsede liv, findes den fulde version som abonnement – pr. måned eller pr. år.
```

**Apple: Untertitel** (28 Zeichen)

```
Ord, grammatik, fortællinger
```

**Apple: Schlüsselwörter** (80 Zeichen)

```
bosnisk,bosnien,balkan,sprog,ordforråd,grammatik,serbisk,kroatisk,sarajevo,rejse
```

---

# 8. Français

**App-Name** (27 Zeichen)

```
Zmaj – Apprendre le bosnien
```

**Kurzbeschreibung** (73 Zeichen)

```
Le bosnien pour la famille, le quotidien et l'administration — 43 niveaux
```

**Vollständige Beschreibung** (3749 von 4000 Zeichen)

```
Tu as de la famille en Bosnie, des racines bosniennes, une belle-famille avec qui tu aimerais enfin parler toi-même, sans que personne ne traduise ? Zmaj t'apprend le bosnien : 43 niveaux, des exercices courts, du quotidien jusqu'au contrat de travail.

CE QUE TU APPRENDS

Trois sections, les unes après les autres.

« Les bases & le quotidien » commence par les tout premiers mots et par ce dont tu as besoin chaque jour.

« Construire des phrases » te montre comment assembler des mots isolés pour en faire tes propres phrases.

« Administration & contrats » s'attaque à ce qui impressionne beaucoup de monde : les démarches administratives, le contrat de travail, la recherche d'un logement, la banque, le médecin. Bref, les situations où il faut d'ordinaire se faire accompagner.

Au total :

• 1668 mots et expressions
• 290 phrases à trous
• 16 leçons de grammaire, 104 exercices en tout, sur les cas, les temps et la conjugaison
• 12 histoires à lire : touche un mot, sa traduction s'affiche
• un test à la fin de chaque niveau

COMMENT ON S'ENTRAÎNE

Les exercices alternent : reconnaître le sens, retrouver le mot bosnien, le taper toi-même, remplir un trou dans une phrase et les exercices de grammaire.

La prononciation est fournie avec l'appli : chaque mot a son fichier audio en voix bosnienne, et les douze histoires s'écoutent d'un bout à l'autre. Dans l'exercice d'écoute, tu lances un mot et tu choisis lequel c'était. Tu entends donc les mots au lieu de seulement les lire – même sur un appareil qui n'a aucune voix bosnienne.

Dans l'exercice de prononciation, le mot bosnien s'affiche à l'écran. Tu peux l'écouter d'abord, puis tu le dis dans le micro. La reconnaissance vocale de ton appareil vérifie au passage si c'était juste. C'est comme ça que tu finis par prononcer les mots toi-même, sur tout appareil doté d'une reconnaissance vocale.

Dans les histoires, tu touches chaque mot que tu ne connais pas et sa traduction s'affiche.

LE BOSNIEN, C'EST DIFFICILE ?

Les mots sont le moindre des problèmes. Ce qui coince, ce sont les cas et la conjugaison. C'est exactement pour ça qu'il y a 16 leçons de grammaire avec leurs 104 exercices : tu avances pas à pas au lieu d'apprendre des tableaux par cœur.

BOSNIEN, CROATE OU SERBE ?

Les contenus suivent le « Pravopis bosanskoga jezika » de Senahid Halilović. L'apprentissage se fait en ijékavien : mlijeko, lijep, vrijeme. Comme on le parle en Bosnie.

FAUT-IL DES BASES ?

Non. La première section s'appelle « Les bases & le quotidien » et commence exactement là.

Et si tu comprends déjà pas mal de choses parce que tu les as entendues à la maison, mais que tu ne t'es jamais penché sur les cas et les temps : les leçons de grammaire et les histoires sont en général la partie qui te manque.

TENIR DANS LA DURÉE

Tu as cinq vies, et elles repoussent toutes seules. La série d'apprentissage compte les jours où tu t'es entraîné, et une protection de série rattrape un jour manqué quand la vie s'en mêle.

DANS TA LANGUE

L'interface existe en allemand, anglais, turc, suédois, néerlandais, norvégien, danois et français. Pratique quand plusieurs langues se croisent dans la famille. La langue apprise, c'est le bosnien, et seulement le bosnien.

QUI EST ZMAJ ?

Zmaj veut dire dragon en bosnien. Il est bleu et il est assis sur une pile de livres.

QUI A FAIT L'APPLI ?

Une seule personne. J'ai construit Zmaj pour ma femme, parce que je n'ai rien trouvé pour le bosnien qui aille plus loin que des listes de vocabulaire. L'appli contient donc exactement ce qui lui manquait : de la grammaire à travailler, des textes à lire et la langue dont on a besoin face à l'administration.

COMBIEN ÇA COÛTE ?

Zmaj est gratuit et financé par la publicité.

Sretno. Bonne chance.
```

**Ersatzabsatz „COMBIEN ÇA COÛTE ?“ – gilt erst, wenn das Abo im Store steht**

```
Zmaj est gratuit et financé par la publicité. Si tu veux apprendre sans publicité et avec des vies illimitées, la version complète existe en abonnement – par mois ou par an.
```

**Apple: Untertitel** (28 Zeichen)

```
Mots, grammaire et histoires
```

**Apple: Schlüsselwörter** (90 Zeichen)

```
bosnien,bosnie,balkans,langue,vocabulaire,grammaire,serbe,croate,sarajevo,voyage,apprendre
```

---

# Screenshots

Google will mindestens zwei, zeigt aber bis zu acht. Nimm sechs – mehr
schaut sich niemand an, weniger wirkt dünn.

**Größe:** 1080 × 1920 px (Hochformat) reicht für alle Telefonformate.
Google verlangt: mindestens 320 px Kantenlänge, höchstens 3840 px,
Seitenverhältnis 9 : 16 im Hochformat oder 16 : 9 im Querformat. Format
JPEG oder 24-Bit-PNG ohne Alphakanal.

**So machst du sie:** am besten auf dem Handy, mit der fertigen App – dann
siehst du, was der Nutzer sieht, samt Vorspann und Anzeigenfläche. Geht
auch am PC: App öffnen, Browser auf Handybreite ziehen (in Chrome mit
F12 → Symbol „Gerät wechseln“ → 1080 × 1920), dann pro Bildschirm einen
Screenshot. Achte darauf, dass auf keinem Bild eine Testanzeige mit
Googles Aufschrift „Test Ad“ steht.

| # | Was drauf soll | Warum |
|---|---|---|
| 1 | Der Lernpfad mit den Levels | Das erste Bild entscheidet. Man sieht sofort: Sprachkurs mit Struktur. |
| 2 | Eine Lektion mit Antwortmöglichkeiten | Zeigt, was man wirklich tut. |
| 3 | Die richtige Antwort, Drache freut sich | Das Gefühl, das man kaufen soll. |
| 4 | Eine Grammatik-Lektion | Hebt dich von reinen Vokabel-Apps ab. |
| 5 | Eine Geschichte mit angetipptem Wort | Kann fast keine andere App in dieser Größe. |
| 6 | Lernserie und Leben | Zeigt, dass es ein Spiel ist, keine Karteikarte. |

**Vorstellungsgrafik** (1024 × 500 px, Pflicht): Der Drache links, rechts
„Zmaj – Bosnisch lernen” auf dem dunkelblauen Hintergrund der App. Kein
Gerätebild, keine Screenshots darin – Google lehnt das ab. Liegt fertig als
`store/feature-1024x500.png`. Neu zeichnen lassen kannst du sie, indem du in
`grafiken_bauen.py` den Schalter `ZWEITE_GRAFIK` auf `True` stellst und
danach `_feature.html` im Browser öffnest; das Aussehen selbst steht in
`web/_feature.html`.

**App-Symbol**: 512 × 512 px, ohne runde Ecken (die setzt Google selbst).
Liegt fertig als `store/icon-512.png`, ebenfalls von `grafiken_bauen.py`
erzeugt. Das kleine `web/icon-256.png` ist nur das Symbol für den
Browser-Reiter und reicht für den Store nicht. Änderst du das Symbol, lass
`grafiken_bauen.py` in Thonny noch einmal laufen, statt die Datei von Hand
zu vergrößern.

**Zwei Dinge an den fertigen Bildern prüfen – sie sind gerade vertauscht:**

| Datei | Wie sie heute ist | Was Google will |
|---|---|---|
| `store/icon-512.png` | 512 × 512, 24 Bit, **ohne** Alphakanal | 32-Bit-PNG **mit** Alphakanal |
| `store/feature-1024x500.png` | 1024 × 500, 32 Bit, **mit** Alphakanal | JPEG oder 24-Bit-PNG **ohne** Alphakanal |

Die Maße stimmen beide, es geht nur um den Alphakanal. Beim Symbol schreibt
`grafiken_bauen.py` den PNG-Kopf mit Farbtyp 2 (das ist RGB ohne Alpha) –
das ist die Stelle, an der es sich ändern lässt. Die Vorstellungsgrafik
kommt aus dem Browser und bringt den Alphakanal von dort mit; am
schnellsten speicherst du sie einmal als JPEG. Lehnt die Console eine der
beiden ab, weißt du jetzt, woran es liegt.

---

# Data-Safety-Formular

Google fragt beim Hochladen ab, welche Daten die App sammelt. Falsche
Angaben führen zur Sperrung, also genau so ausfüllen. Stand: keine Konten,
AdMob eingebaut, `WERBUNG_LAEUFT = True`.

**Der Satz, der alles erklärt:** Zmaj selbst erhebt nichts. Alles, was in
diesem Formular steht, erhebt Googles Werbe-SDK. Du kreuzt es trotzdem an –
im Formular haftest du für alles, was in deiner App steckt, auch für
fremden Code.

**Erheben heißt: das Gerät verlassen.** Was nur im Speicher des Geräts
liegt, gehört nicht ins Formular. Deshalb steht dein Lernfortschritt hier
nirgends.

## Die vier Fragen am Anfang

| Frage | Antwort |
|---|---|
| Erhebt oder teilt deine App eine der geforderten Nutzerdatenarten? | **Ja** – wegen AdMob |
| Werden alle Nutzerdaten bei der Übertragung verschlüsselt? | **Ja** – das Werbe-SDK überträgt über TLS, und die App selbst überträgt nichts |
| Bietest du Nutzern eine Möglichkeit, die Löschung ihrer Daten zu verlangen? | **Ja** – App löschen oder Speicher leeren, erklärt unter https://zmaj-lernapp.github.io/konto-loeschen.html |
| Wurden die Angaben unabhängig geprüft? | Nein |

Das eigene Pflichtfeld für die **Kontolöschung** entfällt: Unter
„App-Inhalte → Datenlöschung“ wählst du „Meine App lässt das Erstellen von
Konten nicht zu“. Die Adresse oben kannst du trotzdem eintragen, sie
schadet nicht und beantwortet die Frage vorweg.

## Die vier Datenarten, die du ankreuzt

Alle vier kommen vom AdMob-SDK. Alle vier sind **erhoben *und* geteilt**
(geteilt, weil sie zu Google gehen), keine davon wird nur flüchtig
verarbeitet, keine ist für den Nutzer abwählbar.

| Kategorie | Datenart | Zwecke | Warum |
|---|---|---|---|
| Standort | Ungefährer Standort | Werbung/Marketing · Analysen · Betrugsprävention und Sicherheit | Google bekommt die IP-Adresse und schätzt daraus die grobe Gegend |
| App-Aktivitäten | App-Interaktionen | dieselben drei | welche Anzeige gezeigt, angetippt, zu Ende gesehen wurde |
| App-Informationen und -Leistung | Diagnosedaten | dieselben drei | Startzeit, Hänger, Energieverbrauch – das SDK misst sich selbst |
| Geräte- oder andere IDs | Geräte- oder andere IDs | dieselben drei | Werbe-ID des Geräts, App-Set-ID, Kennungen angemeldeter Konten |

Diese Aufteilung ist nicht geraten – sie steht so in Googles eigener
Anleitung für AdMob-Herausgeber:

```
https://developers.google.com/admob/android/privacy/play-data-disclosure
```

Schau dort noch einmal nach, bevor du absendest: Google ändert die Liste,
wenn sich das SDK ändert.

Dass es wirklich die Werbe-ID ist, siehst du am zusammengebauten Manifest:
`com.google.android.gms.permission.AD_ID` steht drin, dazu die
ACCESS_ADSERVICES-Rechte. Die legt das SDK selbst dazu.

## Was du NICHT ankreuzt – und warum

Das ist der wichtigere Teil. Jede Zeile hier war früher ein Ja.

| Nicht ankreuzen | Warum nicht |
|---|---|
| Name, E-Mail-Adresse, Benutzername, Passwort, Nutzer-IDs | Es gibt kein Konto mehr. Nichts davon wird abgefragt, nichts gespeichert. |
| App-Aktivität im Sinne von Lernfortschritt | Gelernte Wörter, Levels, Serie, Tagesaufgaben, Münzen, Leben, Einstellungen und die Zufallskennung liegen in `localStorage` und verlassen das Gerät nie. Erhoben ist nur, was übertragen wird. |
| Dateien und Dokumente | Die Sicherungsdatei erzeugt der Nutzer selbst und verschickt sie selbst über das Teilen-Menü. Vom Nutzer angestoßene Weitergabe zählt nicht als Erhebung durch die App. |
| E-Mail-Inhalte | Die Rückmeldung öffnet nur das Mailprogramm des Nutzers. Abgeschickt wird sie von ihm, nicht von der App. |
| Audio, Sprach- oder Tonaufnahmen | **Am 19.09.2026 neu bewertet, weil `RECORD_AUDIO` seitdem im Manifest steht und die Sprechaufgabe läuft.** Die App selbst nimmt nichts auf und speichert nichts. Die Spracherkennung macht das Betriebssystem: Android schickt das Gesprochene an den Dienst des Geräteherstellers und gibt der App nur den erkannten Text zurück. Nach Googles Formular-Hilfe ist nicht anzugeben, was ein anderer Dienst erhebt und worauf die App nie zugreift – die App bekommt die Aufnahme nie zu sehen. Kreuze es also weiterhin nicht an, aber **entscheide es bewusst** und schreib dir die Begründung auf. |
| Zahlungsdaten | Der Kauf läuft über Google Play. Du siehst nur Abrechnungszahlen, nie eine Kartennummer. |
| Absturz- und Fehlerprotokolle von uns | Es ist kein Absturzmelder eingebaut. Was die Play Console dir an Abstürzen zeigt, sammelt Google selbst – das gehört nicht ins Formular. Die Diagnosedaten oben sind die des Werbe-SDK. |
| Genauer Standort, Kontakte, Fotos, Kalender, SMS, Gesundheits- und Fitnessdaten | Nichts davon rührt die App an. |

**Wenn du die Werbung eines Tages abschaltest** (`WERBUNG_LAEUFT = False`
und das Plugin raus), fällt die ganze Tabelle weg. Dann lautet die erste
Frage **Nein**, und das Formular ist in einer Minute fertig.

---

# Alterseinstufung

Der Fragebogen führt bei dieser App auf **USK 0 / PEGI 3**, mit dem Zusatz
„Enthält Werbung“. Beantworte:

- Gewalt, Schimpfwörter, Glücksspiel, Drogen, Sexualität: nein
- Nutzer können Inhalte teilen oder miteinander reden: nein. Das
  Teilen-Menü taucht nur auf, wenn der Nutzer seine eigene
  Sicherungsdatei weitergibt – das ist kein Austausch zwischen Nutzern.
- Standort wird geteilt: nein
- Käufe in der App: **ja**. Die App hat ein Abo über Google Play Billing,
  also gehört hier ja hin - unabhängig davon, ob die Produkte in der
  Console schon aktiv sind. In der Console steht es am 20.09.2026 richtig:
  „Onlinekäufe möglich“ und „Interaktive Elemente: In-App-Einkäufe“.
- Werbung: **ja**

---

# Öffentliche Datenschutzerklärung

Google verlangt eine **Internetadresse**, unter der die
Datenschutzerklärung ohne Anmeldung lesbar ist. In der App allein reicht
nicht.

Das ist erledigt, und zwar wirklich: die Seiten sind online. `seite_bauen.py`
erzeugt aus `sprachen.py` den Ordner `github-seite/`, über GitHub Pages
liegen sie unter:

```
https://zmaj-lernapp.github.io/
https://zmaj-lernapp.github.io/datenschutz.html
https://zmaj-lernapp.github.io/nutzungsbedingungen.html
https://zmaj-lernapp.github.io/konto-loeschen.html
```

In die Play Console gehört die mittlere Adresse, `datenschutz.html`.

Datenschutzerklärung und Nutzungsbedingungen stehen dort in allen acht
Sprachen; oben auf der Seite schaltet man um. Die Löschseite gibt es nur
auf Deutsch und Englisch – das reicht Google, weil Englisch dabei ist.
Willst du sie in allen acht, ist die Stelle dafür `LOESCHEN` in
`seite_bauen.py`; heute stehen dort nur die Blöcke `"de"` und `"en"`.

Die Schritt-für-Schritt-Anleitung zum Hochladen steht in
`github-seite/LIESMICH.txt`. Hast du an den Rechtstexten in `sprachen.py`
etwas geändert, `seite_bauen.py` noch einmal laufen lassen und die Dateien
neu hochladen – von Hand in den HTML-Dateien zu ändern lohnt nicht, beim
nächsten Lauf ist es weg.

**Vor dem Einreichen prüfen:** Rufst du die Adressen am Handy im mobilen
Netz auf, statt im WLAN, siehst du, dass sie wirklich öffentlich sind. Und
prüf, ob der Abschnitt zur Werbung noch zur App passt: solange
`WERBUNG_LAEUFT = True` steht, muss dort Google AdMob als Werbepartner
genannt sein. Das ist der Abschnitt, den Google mit dem Data-Safety-Formular
vergleicht – sagen beide dasselbe, ist die Prüfung unauffällig.

Ein Weg bleibt für später offen: eine **eigene Domain**, etwa 10–15 € im
Jahr. Im Store wirkt `smartdragon.de` ernsthafter als `github.io`. In den
Pages-Einstellungen unter „Custom domain“ eintragen, beim Domain-Anbieter
einen CNAME setzen, die Dateien bleiben dieselben. Änderst du die Adresse,
denk an die drei Stellen, die sie nennen: die Play Console, das
Data-Safety-Formular und das Feld „Datenlöschung“.

---

# Parkplatz: leer

Hier lagen bis zum 19.09.2026 die acht Sätze zur Sprechaufgabe. Sie stehen
jetzt wieder in den Beschreibungen – in neuer Fassung, siehe „Die
Sprechaufgabe läuft inzwischen“ weiter oben. Der Parkplatz bleibt als
Abschnitt stehen, weil er nützlich ist: Was du aus einer Beschreibung
herausnimmst, gehört hierher und nicht in den Papierkorb. Übersetzungen sind
Arbeit, und was einmal weg ist, schreibt niemand ein zweites Mal.


Kommt die Aufgabe zurück, ändert sich das Data-Safety-Formular mit: dann
gehört die Zeile zu Audio noch einmal neu bedacht, und die
Datenschutzerklärung nennt das Mikrofon schon heute (Abschnitt 5).
