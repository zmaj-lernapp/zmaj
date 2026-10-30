# Anmeldung und Cloud-Sicherung mit Firebase einrichten

Stand 28.10.2026 (v109). Entschieden am 18.10.2026: Firebase, kostenloser
Tarif Spark. Seit dem 27.10.2026: Die Anmeldung kommt mit v109 und ist
**Pflicht** – mit Google oder mit E-Mail und Passwort, nach der ersten
Lektion. Der ganze Bauplan steht in `Release\Firebase_Plan_v109.md`.

**Für Ajdin gilt `Release\Firebase_Anleitung.md`.** Das ist die
Schritt-für-Schritt-Anleitung für die Konsole, und sie ist maßgeblich. Diese
Datei fasst dieselben Schritte für die Pflege zusammen. Weichen beide
voneinander ab, gilt die Anleitung.

In dieser Datei stehen **keine** Schlüssel, Projekt-IDs oder Client-IDs, und
dort gehören auch nie welche hin – das Repository ist öffentlich. Alles, was
zu genau diesem Projekt gehört, liegt in der privaten Hülle `zmaj-android`.

**Ohne Projekt bleibt alles wie vor v109.** In der Quelle steht
`const CLOUD_AN = false;`. Eingeschaltet wird nur im Bau: `app_bauen.py`
(`cloud_einsetzen`) setzt Projekt-ID, Web-API-Schlüssel und Web-Client-ID in
die Kopie `www/index.html` ein und schaltet dort `CLOUD_AN` ein – aber nur,
wenn `zmaj-android/cloud_zugang.json` existiert. Ohne die Datei: kein Netz,
keine Anmeldeseite, nichts im Gerätespeicher, kein Aufruf des Plugins. Ein
Freigabe-Bau (`app_bauen.py --aab`) bricht ohne die Datei ab; wer bewusst
ohne Anmeldung bauen will, schreibt `--ohne-anmeldung` dazu.

---

## Was gebaut ist

| Teil | Wo |
|---|---|
| Schalter, Platzhalter `CLOUD_PROJEKT`, `CLOUD_SCHLUESSEL`, `CLOUD_CLIENT` | `web/index.html`, Abschnitt CLOUD-SICHERUNG UND ANMELDUNG |
| Firebase über REST, ohne Firebase-Bibliothek: Google, E-Mail/Passwort, Konto anlegen, Passwort vergessen, Bestätigungsmail | `cloudFirestore()` |
| Abgleich: höchstens 1× schreiben am Tag, dazu beim An- und Abmelden | `cloudAbgleich()` |
| Zusammenführen zweier Lernstände | `standZusammenfuehren()` |
| Das Tor nach der ersten Lektion, die Anmeldeseite, Abmelden, Konto löschen | `anmeldungFaellig()`, `anmeldungZeigen()`, `cloudAbmeldenGanz()`, `cloudKontoLoeschen()` |
| Plugin `ZmajAnmeldung`: Google über den Credential Manager, Kopie der Sitzung, Restore-Schlüssel | Hülle, `android/app/src/main/java/de/smartdragon/zmaj/ZmajAnmeldung.java` |
| Werte beim Bauen einsetzen, Abbruch ohne Datei bei `--aab` | `cloud_einsetzen()`, `anmeldung_pruefen()` in `app_bauen.py` |
| Sicherheitsregeln | `firestore.rules` |
| Löschseite, `.nojekyll`, `.well-known/assetlinks.json` | `seite_bauen.py` |
| Kontaktformular (Schalter `KONTAKT_FORMULAR`, Standard aus): Seite `kontakt.html` und Weiterleitung ins Postfach | `seite_bauen.py`, `kontakt_weiterleitung.gs`, Abschnitt 15 |
| Tests | `tests/test_cloud.py`, `tests/test_seite.py`, `tests/test_kontakt.py`, `tests_e2e/test_cloud.py`, `tests_e2e/test_anmeldung.py`, `tests_e2e/test_kontakt.py` (Firebase als Attrappe in `tests_e2e/firebase_attrappe.py`) |

Kein Firebase-SDK und keine `google-services.json`: Die Seite spricht
Firebase über REST an, und die Hülle baut so auch ohne Projekt. So bleibt
auch ein späterer Wechsel des Anbieters einfach – ein neuer Adapter mit
`anmelden`, `registrieren`, `laden`, `speichern` und `loeschen` genügt.

---

## 1. Projekt anlegen

1. <https://console.firebase.google.com> öffnen, mit dem Google-Konto der App
   anmelden.
2. **Projekt hinzufügen**, Name „Zmaj“. Als Projekt-ID ist `zmaj-lernapp`
   ein guter Vorschlag. Sie steht später in den Links der Mails und lässt
   sich **nie mehr ändern**.
3. **Google Analytics: aus.** Die App bindet keine Analyse ein.
4. Tarif: **Spark lassen.** Kein Upgrade auf Blaze, keine Kreditkarte.

## 2. Firestore anlegen

1. Links **Firestore Database** → **Datenbank erstellen**.
2. Edition: **Standard**.
3. Speicherort: **`europe-west3` (Frankfurt)**. Der Ort lässt sich nie mehr
   ändern.
4. Im **Produktionsmodus** starten (alles gesperrt). Die richtigen Regeln
   kommen in Schritt 7.

## 3. Anmeldung einschalten

1. Links **Authentication** → **Jetzt starten**.
2. Reiter **Anmeldemethode**:
   - **Google** aktivieren, Support-E-Mail auswählen, speichern. Unter
     „Web SDK-Konfiguration“ steht danach die **Web-Client-ID** (endet auf
     `.apps.googleusercontent.com`) – sie kommt in `cloud_zugang.json` als
     `client`.
   - **E-Mail/Passwort** aktivieren, aber **nicht** „E-Mail-Link (Anmeldung
     ohne Passwort)“.
   - **Anonym: aus.** Der Code dafür steht noch im Adapter (für die Tests),
     angeboten wird es nicht. Eingeschaltet wird es erst für das
     Kontaktformular (Abschnitt 15); `firestore.rules` sperrt `users/{uid}`
     für anonyme Anmeldungen, die App bekommt dadurch nichts Neues.
3. Reiter **Einstellungen**: „Schutz vor E-Mail-Aufzählung“ an lassen, ebenso
   „Registrierung erlauben“ und „Löschen erlauben“.
4. **Nicht** auf **Identity Platform** upgraden, auch wenn Firebase es
   anbietet. Mit dem Upgrade gilt im kostenlosen Tarif eine Grenze von 3.000
   täglich aktiven Nutzern. Mehrfaktor-Anmeldung und Blocking Functions
   gibt es deshalb nicht.
5. Reiter **Einstellungen**, Abschnitt **Password policy** (seit
   29.10.2026): Modus **Require**, mindestens 8 Zeichen, Groß- und
   Kleinbuchstabe, Ziffer und Sonderzeichen verlangen. **Force upgrade on
   sign-in** aus lassen – sonst kommt, wer sein Konto mit einem einfacheren
   Passwort angelegt hat, nur noch über „Passwort vergessen?“ hinein (die App
   sagt es dann so). Die App prüft dieselben Regeln schon beim Tippen
   (`PW_REGELN_CLOUD`) und dazu, dass der Teil der Adresse vor dem @ nicht im
   Passwort steht. Strenger als die App darf die Konsole sein (die App
   sagt dann „nicht sicher genug“), lockerer nicht – die Prüfung in der App
   allein ließe sich umgehen. Als Sonderzeichen zählt die App genau die
   Liste aus Firebases Anleitung, den Gravis ` nicht.
6. **Vorlagen:** Absendername „Zmaj“, „Antwort an“ die Support-Adresse. Die
   Mails kommen in der Sprache der App (die App schickt `X-Firebase-Locale`
   mit).

## 4. Android-Apps eintragen (SHA-1)

Ohne die richtigen Fingerabdrücke lehnt Google die Anmeldung auf dem Handy
ab. **Projekteinstellungen** (Zahnrad) → **Allgemein** → **App hinzufügen**
→ Android, zweimal:

- `de.smartdragon.zmaj` mit dem **SHA-1** des **App-Signaturschlüssels**
  und des **Upload-Schlüssels** (beide in der Play Console → Testen und
  veröffentlichen → App-Integrität → App-Signatur).
- `de.smartdragon.zmaj.test` (die Test-App) mit dem **SHA-1** des
  **Debug-Schlüssels**. `keytool` liegt nicht im PATH, es kommt mit Android
  Studio. In PowerShell (zeigt SHA-1 und SHA-256):

  ```powershell
  & "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe" -list -v -keystore "$env:USERPROFILE\.android\debug.keystore" -alias androiddebugkey -storepass android | Select-String "SHA1:","SHA256:"
  ```

Die angebotene `google-services.json` brauchen wir nicht – den Schritt
überspringen.

## 5. Die Werte in die Hülle

In `zmaj-android\cloud_zugang.json` (steht in der `.gitignore` der Hülle):

```json
{"projekt": "<Projekt-ID>", "schluessel": "<Web-API-Schlüssel>", "client": "<Web-Client-ID>"}
```

- Projekt-ID und Web-API-Schlüssel: Projekteinstellungen → Allgemein.
- Web-Client-ID: Schritt 3.
- Als UTF-8 **ohne** BOM speichern, sonst ist die Datei für `app_bauen.py`
  kein gültiges JSON.

`app_bauen.py` prüft die Form aller drei Werte und bricht sonst ab, ohne
einen Wert in der Meldung zu zeigen. Der Web-API-Schlüssel ist kein
Geheimnis im engeren Sinn (er steht in jeder App), aber er gehört zu genau
diesem Projekt.

## 6. Fingerabdrücke für die Webseite (SHA-256)

In `zmaj-android\fingerabdruecke.json` die **SHA-256**-Werte derselben drei
Schlüssel, für `seite_bauen.py` (`.well-known/assetlinks.json`, gebraucht
für die Restore-Schlüssel beim Handywechsel):

```json
{"de.smartdragon.zmaj": ["<SHA-256 App-Signatur>", "<SHA-256 Upload>"],
 "de.smartdragon.zmaj.test": ["<SHA-256 Debug>"]}
```

Die Werte stehen neben den SHA-1 (Play Console bzw. Ausgabe von `keytool`),
in der Form `AA:BB:…` (32 Paare). Ajdin legt die Datei nicht selbst an: Er
schickt laut Anleitung (Schritt 6) nur die SHA-256-Werte, die Datei entsteht
daraus.

## 7. Sicherheitsregeln einspielen

1. **Firestore Database** → **Regeln**.
2. Den ganzen Inhalt von `firestore.rules` aus diesem Repository einfügen,
   **Veröffentlichen**.
3. Im **Regel-Playground** drei Fälle prüfen:
   - angemeldet als `abc`, `get` auf `users/abc` → erlaubt,
   - angemeldet als `abc`, `get` auf `users/xyz` → verweigert,
   - nicht angemeldet, `get` auf `users/abc` → verweigert.

Erlaubt ist nur das eigene Dokument `users/{uid}` mit genau zwei Feldern,
`daten` (höchstens 900.000 Zeichen, bis 28.10.2026 400.000) und `rev`.
Die E-Mail-Adresse steht nicht in Firestore, nur bei Firebase
Authentication. Nach dem Anheben die Regeln einmal neu veröffentlichen,
sonst lehnt Firestore einen Stand über 400.000 Zeichen weiter ab.

Seit dem 28.10.2026 stehen in `firestore.rules` auch die Regeln für das
Kontaktformular (`nachrichten/{uid}`, Abschnitt 15) mit dem Platzhalter
`MELDER_UID`. Solange er dort steht und „Anonym“ aus ist, kann niemand
Nachrichten anlegen oder lesen; die Regeln dürfen also schon jetzt so
veröffentlicht werden. Ist das Kontaktformular eingerichtet, muss
`MELDER_UID` bei jedem neuen Veröffentlichen wieder durch die UID des
Melders ersetzt werden. Sonst bekommt die Weiterleitung 403, und die
Nachrichten bleiben liegen.

## 8. Schlüssel einschränken, Google Auth Platform, Vertrag

1. **Google Cloud Console** → APIs und Dienste → **Anmeldedaten** → der
   Browser-Schlüssel des Projekts → **API-Einschränkungen**: nur Identity
   Toolkit API, Token Service API und Cloud Firestore API. **Keine**
   App-Einschränkung setzen – sonst lehnt Google jede Anfrage aus der
   WebView ab.
2. **Google Auth Platform** → **Zielgruppe**: Status „In Produktion“, sonst
   können sich nur Testnutzer mit Google anmelden. **Branding**: App-Name
   „Zmaj“, Support-Mail, Startseite `https://zmaj-lernapp.github.io/`,
   Datenschutz `https://zmaj-lernapp.github.io/datenschutz.html`,
   Nutzungsbedingungen `https://zmaj-lernapp.github.io/nutzungsbedingungen.html`,
   Kontakt des Entwicklers die Support-Mail, autorisierte Domain
   `zmaj-lernapp.github.io`. Vorerst kein Logo hochladen (könnte eine
   Markenprüfung auslösen).
3. **Projekteinstellungen** → **Datenschutz**: die
   Datenverarbeitungsbedingungen annehmen, falls sie nicht schon gelten. Das
   ist der Vertrag mit Google über die Auftragsverarbeitung. Die Felder für
   EU-Vertreter und Datenschutzbeauftragten (DSB) leer lassen: Der Anbieter
   sitzt in der EU, und einen DSB braucht es in der Regel erst ab 20
   Personen, die ständig mit den Daten arbeiten.
4. **Nutzer und Berechtigungen**: ein zweites Google-Konto als Inhaber
   eintragen, damit das Projekt nicht an einem einzigen Konto hängt.

## 9. Testen

1. Test-App bauen: `app_bauen.py --nur-abgleich --testwerbung`, dann in
   `zmaj-android\android` `gradlew assembleDebug`. Die Hülle baut auch
   ohne `cloud_zugang.json`; dann ist die Anmeldung einfach aus.
2. Am Handy: Google-Anmeldung, Konto mit E-Mail anlegen (Bestätigungs- und
   Rücksetzmail: Sprache? Spam-Ordner?), abmelden und wieder anmelden,
   Konto löschen (beide Arten), Flugmodus nach Lektion 1, App neu starten,
   Update darüber installieren.
3. Handywechsel (Restore Credentials): Android Studio → Geräteoptionen →
   **Backup App Data**, App deinstallieren und neu installieren, **Restore
   App Data**, App öffnen – man soll angemeldet sein, der Lernstand soll da
   sein. Dabei auch prüfen, ob der Restore-Schlüssel ohne
   `assetlinks.json` angelegt wird.
4. In der Konsole unter **Firestore Database** → **Nutzung** nachsehen, dass
   es höchstens einen Schreibvorgang je Nutzer und Tag gibt.
5. Danach den Freigabe-Bau (R8) aus dem internen Test einmal ganz
   durchspielen: Anmeldung, Kauf, Werbung, Erinnerung, Sprechaufgabe,
   Sicherung.

## 10. Play Console (mit dem Upload von v109)

- **Datensicherheit** neu ausfüllen. Konten: ja, Anlegen per „Nutzername
  und Passwort“ und „OAuth“. Erhoben: **E-Mail-Adresse** (erforderlich,
  App-Funktionen und Kontoverwaltung), **Nutzer-IDs** (erforderlich, wie
  oben), **Name** (optional, nur bei Google), **App-Aktivitäten → Sonstige
  Aktionen** (der Lernstand, erforderlich, App-Funktionen). Nichts davon wird
  geteilt, alles ist bei der Übertragung verschlüsselt, die Löschung kann
  beantragt werden. Die AdMob-Angaben bleiben, auch deren Geräte-IDs. Für
  Firebase kommen keine Geräte-IDs dazu – die Zufallskennung bleibt auf dem
  Gerät.
- **Kontolöschung:** in der App ja; als URL
  `https://zmaj-lernapp.github.io/konto-loeschen.html`.
- **App-Zugriff:** „Alle oder einige Funktionen sind eingeschränkt“, dazu
  E-Mail und Passwort eines Testkontos (anlegen in der Firebase-Konsole unter
  **Authentication** → **Nutzer** → „Nutzer hinzufügen“, mit einer Adresse,
  die man lesen kann; welche, steht in der Anleitung, Schritt 10) und der
  Hinweis: *“Sign-in is required after the first lesson. Complete the first
  lesson (each new word is shown first; each wrong answer costs one of 5
  hearts, so answer carefully), tap ‘Continue’, then ‘Sign in with email’ and
  use the account above. You stay signed in. No second factor and no email
  confirmation are needed.”*
- Store-Eintrag auf Sätze wie „ohne Konto“ prüfen.
- **Verzeichnis der Verarbeitungstätigkeiten:** Eintrag „Konto und
  Cloud-Sicherung“.

## 11. Datenschutz und Nutzungsbedingungen

Stehen seit v109 in `sprachen.py` (`set.datenschutz_text`, Abschnitt 3
„Konto und Sicherung in der Cloud“, und `set.agb_text`, Punkte 3, 5 und 8),
in allen acht Sprachen. Die Seiten für GitHub Pages baut `seite_bauen.py`;
**hochladen erst zusammen mit v109**, sonst stimmen sie für v108 nicht.
Die sieben Übersetzungen hat kein Muttersprachler gegengelesen.

## 12. Konto löschen per Mail

Ein Löschantrag per Mail (Betreff „Konto löschen“, von der Adresse des
Kontos) wird von Hand bearbeitet, innerhalb von 30 Tagen:
**Authentication** → **Nutzer** → Konto suchen → **Konto löschen**, dann
**Firestore** → `users/<uid>` löschen, danach dem Absender bestätigen.

## 13. Grenzen im Spark-Tarif

- Firestore: 20.000 Schreibvorgänge und 50.000 Lesevorgänge am Tag für alle
  zusammen. Die App schreibt höchstens einmal am Tag je Nutzer (dazu beim
  An- und Abmelden) – eng wird es ab etwa 12.000 bis 15.000 täglich aktiven
  Nutzern. Dann Blaze mit Budget-Warnung.
- Authentication: 150 Mails zum Zurücksetzen und 1.000 Bestätigungsmails am
  Tag, 100 neue Konten je Stunde und IP-Adresse.
- Wird eine Grenze überschritten, meldet Firebase `RESOURCE_EXHAUSTED` bzw.
  `TOO_MANY_ATTEMPTS_TRY_LATER`. Es geht nichts verloren: Die App lernt mit
  dem Gerätespeicher weiter und versucht es beim nächsten Anlass noch einmal.
- Eine Warnung bei hoher Nutzung gibt es auf Spark nicht: Budget-Warnungen
  brauchen ein Rechnungskonto (Blaze), Warnregeln in Cloud Monitoring kosten
  Geld. Die Nutzung steht unter Zahnrad → **Nutzung und Abrechnung** und
  unter **Firestore Database** → **Nutzung** (Anleitung, Schritt 11).
- Ohne App Check kann auch ein einzelnes Konto die Tagesgrenzen mit Absicht
  ausschöpfen; dann scheitern Abgleich und Abmelden bis zum Zurücksetzen.
  Bekanntes Restrisiko, siehe `SECURITY.md` (Known limitations).

## 14. Restore Credentials (Pflicht ab April 2027)

Google verlangt für Apps mit Anmeldung die Restore-Credentials-API
(Play-Hilfe 17492799) und misst, ob der Schlüssel auf dem neuen Gerät
abgerufen wird. `ZmajAnmeldung` legt ihn nach jeder Anmeldung an
(`restoreSichern`, user.id = Firebase-uid, keine E-Mail), ruft ihn beim
ersten Start nach einer Installation ab (`restoreHolen`) und löscht ihn beim
Abmelden und beim Löschen des Kontos. Angemeldet wird auf dem neuen Gerät
mit der Sitzung, die Androids Sicherung zurückspielt (Gerätespeicher oder
die Kopie in den SharedPreferences `zmaj_konto`). Eine Prüfung der Signatur
auf einem eigenen Server gibt es nicht; reicht das Google später nicht,
wäre der Ausweg eine Cloud Function (Blaze) oder ein Cloudflare Worker.

## 15. Kontaktformular

Entschieden am 28.10.2026 (Weg A aus `Release\Kontaktformular_Vorschlag.md`):
ein zweiter Weg zur „schnellen elektronischen Kontaktaufnahme“ nach § 5
Abs. 1 Nr. 2 DDG neben der E-Mail, ohne Telefonnummer. Es kostet nichts,
jetzt nicht und später nicht: Firebase bleibt im Tarif Spark ohne
Zahlungsmittel, die Weiterleitung läuft als Apps Script im Gratis-Gmail-Konto
`zmaj.lernapp@gmail.com`. Ajdins Handgriffe stehen in
`Release\Firebase_Anleitung.md`, Schritt 12.

So kommt eine Nachricht an:

1. `kontakt.html` meldet sich anonym an (`accounts:signUp`), legt genau ein
   Dokument `nachrichten/{uid}` an (`text`, `antwort`, `sprache`, `zeit` vom
   Server) und löscht die Anmeldung gleich wieder (`accounts:delete`).
2. `kontakt_weiterleitung.gs` meldet sich alle 5 Minuten als Melder an
   (E-Mail/Passwort), liest `nachrichten`, schickt jede Nachricht als Mail an
   `zmaj.lernapp@gmail.com` (Betreff beginnt mit `[Zmaj-Formular]`, „Antworten
   an“ ist die Adresse aus dem Formular) und löscht das Dokument erst nach dem
   Versand. Die Mail geht nie an die Adresse aus dem Formular.

| Teil | Wo |
|---|---|
| Schalter `KONTAKT_FORMULAR` (Standard: aus), Seitentexte `kontakt.*`, `set.impressum_text_mit_formular`, `set.dsgvo_formular` | `sprachen.py` |
| Die Seite, nur mit Schalter **und** `cloud_zugang.json` (Projekt-ID und Web-API-Schlüssel, dieselbe Datei wie für die App); sonst nennt keine Seite das Formular | `seite_bauen.py`, `baue_kontaktseite()` |
| Anlegen nur anonym unter der eigenen uid, Lesen und Löschen nur für den Melder | `firestore.rules`, `match /nachrichten/{uid}` |
| Weiterleitung, Einrichtung im Kopfkommentar | `kontakt_weiterleitung.gs` |

Einschalten, in dieser Reihenfolge. Der Gmail-Filter kommt zuerst: Sobald
„Anonym“ an ist und die Regeln stehen, kann jeder mit dem öffentlichen
Web-API-Schlüssel per REST eine Nachricht mit fremder Antwortadresse anlegen.
Liefe dann schon das Skript, ginge die Sofortantwort an diese Adresse.

1. Gmail-Filter der Sofortantwort: `-subject:"[Zmaj-Formular]"` dazu. Sonst
   schickt Gmail die Vorlage an die Adresse aus „Antworten an“, also an eine
   Adresse, die jeder ins Formular schreiben kann.
2. **Authentication** → **Anmeldemethode** → **Anonym** aktivieren. Unter
   **Einstellungen** bleiben „Registrierung erlauben“ und „Löschen erlauben“
   an – die Seite braucht beides.
3. **Authentication** → **Nutzer** → **Nutzer hinzufügen**: das Melder-Konto
   (z. B. `zmaj.lernapp+melder@gmail.com`) mit einem eigenen, langen
   Passwort. Das Passwort kommt nur in die Skripteigenschaften.
4. `firestore.rules` in der Konsole neu einfügen, dort `MELDER_UID` durch die
   UID des Melders ersetzen, **Veröffentlichen**. Im Repository bleibt der
   Platzhalter stehen (`tests/test_kontakt.py`), also bei jedem späteren
   Veröffentlichen wieder ersetzen (Abschnitt 7).
5. script.google.com mit `zmaj.lernapp@gmail.com`: Projekt anlegen,
   `kontakt_weiterleitung.gs` einfügen, Skripteigenschaften `PROJEKT`,
   `SCHLUESSEL`, `MELDER_MAIL`, `MELDER_PASSWORT` setzen, `einrichten`
   einmal ausführen und erlauben. Das legt den Auslöser „alle 5 Minuten“ an.
6. In `sprachen.py` `KONTAKT_FORMULAR = True` und `KONTAKT_STAND` auf den Tag
   des Umlegens (`"TT.MM.JJJJ"`); damit geht der „Stand“ der
   Datenschutzerklärung in allen acht Sprachen mit, ohne Datum bricht
   `texte()` ab. Dann `seite_bauen.py` (baut `kontakt.html` und nennt das
   Formular im Impressum der Webseite und in den Fußzeilen) und die App neu
   bauen (Datenschutzerklärung und Impressum, das die App seit dem
   28.10.2026 unter Einstellungen → Über die App zeigt). Seiten
   hochladen.
7. Probe: eine Nachricht über die Seite schicken. Nach höchstens 5 Minuten
   liegt die Mail im Postfach, `nachrichten` ist wieder leer, und unter
   **Nutzer** steht kein anonymes Konto mehr.

Eine Nachricht, die sich nicht verschicken lässt, hält die anderen nicht
auf: Das Skript versucht es noch einmal ohne „Antworten an“ und mit festem
Betreff, und nach drei gescheiterten Läufen schickt es nur einen Hinweis
ohne Inhalt und löscht das Dokument (Kopfkommentar in
`kontakt_weiterleitung.gs`, geprüft in `tests_e2e/test_kontakt.py`).

Grenzen, alle im Gratistarif:

- Authentication: 100 neue Konten je Stunde und IP-Adresse – die anonymen
  Anmeldungen der Seite zählen mit.
- Firestore: Jede Nachricht kostet einen Schreib-, einen Lese- und einen
  Löschvorgang. Die Weiterleitung liest bei jedem Lauf, auch ohne Nachricht
  (eine leere Abfrage zählt als ein Lesevorgang): 288 am Tag von 50.000.
- Apps Script (Gmail-Konto): 100 Mail-Empfänger am Tag, 20.000 Abrufe am Tag,
  90 Minuten Laufzeit für Auslöser am Tag. Im Normalfall reicht das weit.
  Kommen an einem Tag mehr Nachrichten, bleiben die übrigen in Firestore und
  gehen der Reihe nach an den folgenden Tagen hinaus; die letzte Mail des
  Tages meldet den Stau („[Zmaj-Formular] Stau: …“, höchstens einmal am Tag).
- Ohne App Check kann jemand mit vielen anonymen Anmeldungen die
  Schreibvorgänge des Tages aufbrauchen. Dann warten die Cloud-Sicherungen
  bis zum Zurücksetzen; verloren geht nichts (Abschnitt 13).

Notbremse bei Spam: Das Fallenfeld prüft nur der Browser. Ein Skript kommt
daran vorbei und schafft je IP-Adresse rund 100 Nachrichten in der Stunde;
weil die Weiterleitung streng der Reihe nach arbeitet, kämen echte
Nachrichten dann tagelang nicht an. Abhilfe: **Authentication** →
**Anmeldemethode** → **Anonym** deaktivieren. Dann nimmt das Formular nichts
mehr an (es meldet „hat nicht geklappt“ und nennt die E-Mail-Adresse), App
und Mail laufen weiter. Danach in **Firestore Database** die Sammlung
`nachrichten` löschen; echte Nachrichten, die dort noch warten, sind damit
auch weg. Ist es vorbei, „Anonym“ wieder einschalten.
