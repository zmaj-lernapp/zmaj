# Was neu ist – 16. September 2026

Der Tag, an dem aus dem PC-Programm eine App geworden ist. Alles, was einen
Server brauchte, ist entweder ersetzt oder fällt weg.

**Zum Ausprobieren:** am PC wie immer `start.py` in Thonny (**Stop**, dann
**F5**). Für das Handy erst `inhalt_bauen.py`, dann `app_bauen.py`, danach in
Android Studio den Ordner `zmaj-android\android` öffnen.

## Keine Konten mehr

Keine Anmeldung, kein Passwort, keine E-Mail, kein Profilwechsel. Der
Lernstand liegt im Speicher des Geräts, unter `zmaj_stand`. Dazu kommt
`zmaj_id`, eine zufällige Kennung je Gerät: früher zog der Profilname die drei
Tagesaufgaben, ohne Konten hieße jeder gleich und alle bekämen dieselben drei.

Entschieden wird das beim Start an einer einzigen Frage: Antwortet `/api/konto`,
gibt es einen Server, sonst nicht (`MIT_SERVER`). Am PC antwortet `start.py`
weiterhin, samt Anmeldung – die Datei ist unverändert. Das ist der Prüfweg
hier am Schreibtisch, nicht das, was in den Store geht: im Paket liegt kein
Python, also fragt die App niemanden und geht direkt hinein.

Die alten Profildateien sind nicht gelöscht, sie liegen in
`sicherung_konten_2026-09-16`. `konto_zu_sicherung.py` macht daraus
`zmaj-sicherung-<Name>.json` – Dateien, die die App unten unter „Sicherung
einlesen“ annimmt. Passwort, E-Mail und Bestätigungsstand bleiben dabei
draußen, die gehören nicht in einen Lernstand.

## Der Inhalt liegt jetzt in Dateien

`inhalt_bauen.py` schreibt `web/inhalt/<code>.json`, acht Stück zu je rund
180 KB, dazu `liste.json` als Verzeichnis. Das Skript ruft dieselbe Funktion
auf wie der Server (`start.lade_daten`), das Ergebnis kann also nicht
abweichen. Die Tonspur bleibt draußen, die steht in `web/audio/index.json`.

Die App versucht weiter `/api/daten` und nimmt die Datei, wenn niemand
antwortet. **Nach jeder Änderung an Wörtern, Sätzen oder Texten muss
`inhalt_bauen.py` laufen**, sonst sieht das Handy den alten Stand.

`app_bauen.py` kopiert `web/` nach `zmaj-android\www` und ruft `cap sync`.
Vorher prüft es die Tonspur und bricht ab, wenn etwas fehlt – ein halb
stummes Paket soll gar nicht erst entstehen. Sicherungen wie
`index.html.vor_lokal` und die Probeaufnahmen bleiben zurück.

## Sicherung: der Lernstand als Datei

Einstellungen → **Sicherung**, zwei Knöpfe. Gespeichert wird
`zmaj-sicherung-JJJJ-MM-TT.json`: am Handy über das Teilen-Menü, am PC als
Download. Einlesen ersetzt den ganzen Stand, deshalb fragt es vorher nach und
meldet danach, wie viele Wörter und Lerntage angekommen sind.

Das ist kein Beiwerk. Ohne Konto gibt es keine zweite Stelle, an der der
Lernstand liegt – neues Handy ohne Sicherung heißt: von vorn.

## Rückmeldung geht per Mail

Der Knopf öffnet das Mailprogramm mit fertigem Betreff und Text an
`zmaj.lernapp@gmail.com`; daneben steht ein Knopf, der die Adresse in die
Zwischenablage legt, falls kein Mailprogramm eingerichtet ist. Nichts geht
mehr über einen Server. Am PC mit `start.py` läuft der alte Weg über
`/api/feedback` weiter und fällt bei einem Fehler auf die Mail zurück.

## Die Zurück-Taste statt des Beenden-Knopfs

Der Knopf „App beenden“ ist weg – in einer App unten eine Schaltfläche zum
Schließen zu haben, kennt Android nicht. Stattdessen hängt die Zurück-Taste
des Geräts jetzt an einer eigenen Reihenfolge:

| Wo du bist | Was passiert |
|---|---|
| offene Nachfrage | sie wird verneint |
| Einwilligung oder Werbung | nichts, die haben eigene Knöpfe |
| Lektion oder Test | wie der Abbrechen-Knopf, mit Warnung |
| Unterseite | eine Ebene zurück |
| Startseite | „Zmaj wirklich schließen?“, dann speichern und schließen |

In Lektion und Test drückt der Code den vorhandenen Abbrechen-Knopf, statt
dessen Arbeit nachzubauen – so fragt die Taste genauso nach und speichert
genauso. Am PC gibt es keine solche Taste, dort passiert nichts.

## Werbung ist eingebaut – noch mit Testkennungen

Plugin `@capacitor-community/admob`. Die Einwilligung holt Googles eigenes
Fenster (UMP); das selbstgebaute tritt zurück, sobald das Plugin da ist, und
läuft nur noch am PC. Das ist keine Geschmacksfrage: Google verlangt ein
zertifiziertes Fenster, und zwei Stellen, die dasselbe regeln, widersprechen
sich irgendwann. `WERBUNG_LAEUFT` in `sprachen.py` steht auf `True` und
schaltet Werbung, Einwilligung und den passenden Absatz in der
Datenschutzerklärung gemeinsam.

Geht am Plugin etwas schief, läuft die App ohne Werbung weiter. Eine Lernapp,
die wegen einer Anzeige nicht startet, wäre der schlechteste Tausch.

Zurzeit laufen **Googles öffentliche Testanzeigen**. Vor der Veröffentlichung
sind drei Stellen zu tauschen:

| Was | Wo |
|---|---|
| App-ID (`ca-app-pub-…~…`) | `zmaj-android\android\app\src\main\res\values\strings.xml` |
| `ADMOB_ID` (Interstitial, belohnt) | `web/index.html` |
| `ADMOB_TEST` auf `false` | `web/index.html` |

Testanzeigen in einer veröffentlichten App sind ein Regelverstoß.

## Vorspann

Beim Start das Zeichen des Studios: der Drache speit Feuer, daraus tritt der
Name **SmartDragon**. 2,4 s Bewegung, danach 1,5 s Standzeit – ohne die Pause
wechselt die App genau in dem Moment, in dem der Name fertig ist. Weg geht er
erst, wenn die Zeit um **und** die App bereit ist; Antippen setzt die
Wartezeit auf null. Hängt das Skript ganz, blendet ihn eine CSS-Animation von
selbst aus.

## Der Play Store ist das Ziel

Herausgeber **SmartDragon**, `appId de.smartdragon.zmaj`, versionCode 1,
versionName 1.0, minSdk 24, targetSdk 36. Was dafür noch fehlt, steht unten
unter „Noch zu tun“; die Texte liegen in `STORE_TEXTE.md`.

## Rechtstexte stehen öffentlich

`seite_bauen.py` erzeugt vier Dateien in `github-seite`: Startseite,
Datenschutzerklärung, Nutzungsbedingungen und `konto-loeschen.html`. Jede
Rechtsseite enthält alle acht Sprachen, keine Schriften und keine Skripte von
fremden Servern. Gelesen werden sie unter <https://zmaj-lernapp.github.io/>.

`konto-loeschen.html` heißt jetzt **„Daten löschen“** und erklärt, dass es
kein Konto gibt und der Lernstand mit dem Deinstallieren verschwindet. Google
fragt die Adresse im Data-Safety-Formular ab, deshalb behält die Datei ihren
alten Namen – ein neuer Name wäre ein toter Link.

Änderst du etwas an den Rechtstexten in `sprachen.py`, muss `seite_bauen.py`
noch einmal laufen und die Dateien müssen neu hochgeladen werden.

## Gleich geblieben

43 Level in 3 Sektionen, 12 Geschichten, 8 Oberflächensprachen, 1108
Aufnahmen, Leben, Lernserie, Tagesaufgaben, Münzen, Laden.

---

# Rückblick: 14. und 15. September 2026

**Zuerst:** Server neu starten (Thonny **Stop**, dann **F5**), sonst läuft noch
die alte `start.py` im Speicher. Hier steht nur, was sich geändert hat –
Tagesaufgaben und Münzen sind inzwischen normaler Betrieb und stehen in
`ANLEITUNG.md`.

---

## Kein eigener Server im Internet, kein App Store – vorerst

> **Überholt seit dem 16.09.2026.** Der Store ist wieder das Ziel, und die App
> läuft ohne Server: nicht über das Internet, sondern aus Dateien auf dem
> Gerät. Was hier über das Zusammenführen zweier Geräte steht, gilt trotzdem
> weiter – und ist der Grund, warum es keine Konten mehr gibt.

Beides ist zurückgestellt, nicht abgesagt. Die App läuft auf deinem PC, Kübra
kommt über das WLAN dran. Anmeldung, Konten, Mailversand und „Passwort
vergessen“ bleiben wie bisher – der lokale Python-Server geht ja nicht weg.

Der ehrliche Grund: Der Server hätte das Problem gar nicht gelöst, für das er
gedacht war. Beim Speichern von `/api/fortschritt` werden `gewusst`,
`bestanden`, `gelesen`, `tage` und `frost` schlicht **ersetzt**, nicht
zusammengeführt – nur `tagwerk`, `besitz` und die beiden Münzsummen werden
verschmolzen. Zwei Geräte am selben Konto heißt also: Wer zuletzt speichert,
überschreibt den anderen. Daran hätte ein Server im Internet nichts geändert.
Wollen wir ihn später wirklich, muss zuerst dieses Zusammenführen gebaut sein.

## Der Laden hat jetzt einen eigenen Reiter

Vorher steckte er in den Einstellungen, jetzt steht er als dritter Reiter auf
der Startseite neben „📚 Lernpfad“ und „📖 Geschichten“, in zwei Gruppen:

| Für dich | | Accessoires für Zmaj | |
|---|---|---|---|
| Herz auffüllen | 100 | Brille | 800 |
| Serienschutz | 300 | Kopfhörer | 1200 |
| | | Mütze | 1500 |
| | | Krone | 2500 |

Aus der einen Mütze sind vier Stücke geworden. Getragen wird immer nur eins;
nach dem Kauf sitzt es sofort, ein zweites Antippen nimmt es ab. Jedes Stück
hängt an der Kopf-Ebene des Drachen und macht jede Bewegung mit. **Besessen**
steht im Profil auf dem Server, **getragen** nur im Browser des jeweiligen
Geräts – am Handy kann also etwas anderes aufsitzen als am PC. Das ist Absicht.
(Seit dem 16.09. steht beides auf dem Gerät.)

## Die Tonspur

Drei Befehle, in dieser Reihenfolge:

    ton_bauen.py --probe             30 Probewörter zum Anhören
    ton_bauen.py --stimme <name>     der große Lauf
    ton_pruefen.py                   prüft, ob nichts fehlt

Die 30 Probewörter sind genau die, an denen kroatische Stimmen scheitern:
`kahva`, `hljeb`, `babo`, `amidža`, die ijekavischen Formen (`mlijeko`,
`dijete`, `čovjek`) und die Laute č ć dž đ. Der große Lauf holt dann
**1108 Aufnahmen** – 1096 Wörter und die 12 Geschichten. Er ist abbruchsicher:
Vorhandenes wird übersprungen, alle 25 neue Töne schreibt er `index.json`
zwischendurch, du kannst ihn also jederzeit abwürgen. Der Zugangsschlüssel
steht in `tts_zugang.json` und bleibt auf diesem Rechner.

Die Dateien heißen `w0001.mp3` … und `g01.mp3` …, nicht mehr nach dem Wort;
`index.json` sagt, welche Datei zu welchem Text gehört, und die Nummern werden
einmal vergeben und nie geändert. Du bist Muttersprachler – jede Datei, die du
selbst einsprichst und darüberschreibst, sticht die erzeugte sofort aus. Am
besten Level für Level, immer eins voraus.

## Zwei Fehler, die im fertigen Paket alles stumm gelassen hätten

**Die Dateiliste kam vom Server.** `ladeDaten()` las das Feld `audio` aus
`/api/daten`, das `start.py` aus dem Ordner zusammenstellt. In einer Handy-App
gibt es keinen Server, die Liste wäre also leer geblieben – alle Aufnahmen im
Paket, keine einzige auffindbar. Jetzt holt `ladeAudio()` die Zuordnung direkt
aus `audio/index.json`.

**Die Hör-Knöpfe hingen an `speechSynthesis`.** `canListen` war fest
`'speechSynthesis' in window`, und die Android-WebView kennt das nicht. Damit
wären Hör-Knöpfe, der Aufgabentyp „Hören“ und die Tagesaufgabe „Hörübungen“
verschwunden, obwohl 1108 Aufnahmen daneben lagen. Jetzt ist `canListen` wahr,
sobald es eine Computerstimme **oder** Aufnahmen gibt, und `speak()` spielt
erst die Datei und fällt nur bei Fehlern auf die Stimme zurück. Sicherung der
alten Fassung: `web/index.html.vor_audio`.

## Die Anleitung in `web/audio` war nicht ausführbar

Dort stand, die Datei solle genau so heißen wie das bosnische Wort. Das geht
nicht: Windows erlaubt kein `?` und kein `/` im Dateinamen, „Kako se zoveš?“
und „Gladan sam / Gladna sam“ lassen sich gar nicht anlegen. Die App schneidet
Satzzeichen ab, bevor sie sucht, und eine Geschichte hieße nach ihrem ganzen
Text. `web/audio/LIESMICH.txt` ist neu geschrieben.

## Am 15.09. erledigt

- **Die Tonspur steht.** 1108 Aufnahmen in `web/audio`, 14,8 MB, dazu
  `index.json`. Wörter spricht `bs-BA-GoranNeural`, die zwölf Geschichten
  `bs-BA-VesnaNeural`, erzeugt über Azure im Tarif S0 für unter drei Dollar.
  Im Browser geprüft: die App findet und spielt die Dateien, auch bei
  `Kako si?` und `Gladan sam / Gladna sam`, an denen die alte Namensregel
  scheiterte.
- **Die alte Namensregel im Code.** In `start.py` nennen der Kommentar über
  `AUDIO_ORDNER` und der Docstring von `eigene_aufnahmen()` jetzt
  `index.json` statt `<bosnisches Wort>.mp3`.

`ANLEITUNG.md` ist nachgezogen: „Die Tonspur“ ersetzt „Eigene Aufnahmen“, der
Dateibaum nennt `w0001.mp3` und `g01.mp3`, und `ton_bauen.py`, `ton_pruefen.py`
sowie die vier Accessoires stehen darin.

---

## Zum Prüfen (10 Minuten)

1. Am PC starten: Vorspann läuft, danach geht es ohne Anmeldung hinein
2. Startseite: dritter Reiter **🛒 Laden**, darin zwei Überschriften
3. Accessoire kaufen → sitzt sofort, nochmal antippen nimmt es ab
4. Einstellungen → **Sicherung speichern**, dann wieder einlesen: Wörter und
   Lerntage müssen stimmen
5. Einstellungen → Rückmeldung: der Knopf öffnet das Mailprogramm
6. `ton_pruefen.py` starten → muss „Alles vollständig“ melden, Rückgabe 0
7. Am Handy: Zurück-Taste in einer Lektion, auf einer Unterseite, auf der
   Startseite – drei verschiedene Reaktionen

## Noch zu tun

Alles, was noch fehlt, hängt an Konten bei Google – nicht mehr am Code.

- **Signaturschlüssel erzeugen.** In `android\app\build.gradle` steht noch
  kein `signingConfig`, und im Projekt liegt keine `.jks`-Datei. Ohne
  Schlüssel gibt es kein AAB zum Hochladen. Den Schlüssel und sein Passwort
  sichern: geht er verloren, lässt sich die App nie wieder aktualisieren.
- **Play-Entwicklerkonto anlegen** (einmalig 25 $) und bestätigen lassen.
- **D-U-N-S-Nummer beantragen.** Google verlangt sie für Konten, die als
  Unternehmen auftreten – das Gewerbe läuft seit dem 14.09.2026. Die Nummer
  ist kostenlos, dauert aber Tage bis Wochen. Deshalb früh anstoßen.
- **AdMob-Konto anlegen** und die echten Kennungen eintragen, an den drei
  Stellen oben. `ADMOB_TEST` dabei auf `false`.
- **Screenshots machen**, mindestens zwei, besser sechs bis acht. Symbol
  (512 × 512) und Feature-Grafik (1024 × 500) liegen fertig in `store`.
- **Data-Safety-Formular ausfüllen.** Es fragt, was die App sammelt und wohin
  es geht. Zu prüfen ist dabei, was AdMob erhebt – die App selbst schickt
  nichts weg. Die Adresse zum Löschen ist
  `https://zmaj-lernapp.github.io/konto-loeschen.html`.
- **Erste eigene Aufnahmen einsprechen**, Level 1 zuerst.
- **Versionsnummer hochsetzen**, sobald das erste Paket hochgeladen ist:
  `versionCode` steht auf 1 und muss bei jedem Upload größer werden.
