# Cloud-Sicherung mit Firebase einrichten

Stand 19.10.2026. Entschieden am 18.10.2026: Firebase, kostenloser Tarif
Spark, eingeschaltet wird erst **nach dem Produktionsstart**. Bis dahin ist
alles vorbereitet und **aus**.

In dieser Datei stehen **keine** Schlüssel, Projekt-IDs oder Client-IDs, und
dort gehören auch nie welche hin – das Repository ist öffentlich. Alles, was
geheim oder projektbezogen ist, liegt in der privaten Hülle `zmaj-android`.

---

## Was schon fertig ist

| Teil | Wo | Stand |
|---|---|---|
| Schalter `CLOUD_AN = false` | `web/index.html`, Abschnitt CLOUD-SICHERUNG | aus: kein Netz, keine Oberfläche, nichts im Gerätespeicher |
| Zusammenführen zweier Lernstände | `standZusammenfuehren()` in `web/index.html` | fertig, jedes Feld begründet |
| Abgleich: höchstens 1× schreiben am Tag | `cloudAbgleich()` | fertig |
| Firebase über REST (ohne Firebase-Bibliothek) | `cloudFirestore()` | fertig, noch nie gegen ein echtes Projekt gelaufen |
| Sicherheitsregeln | `firestore.rules` | fertig, noch nicht eingespielt |
| Werte beim Bauen einsetzen | `cloud_einsetzen()` in `app_bauen.py` | fertig |
| Tests | `tests_e2e/test_cloud.py`, `tests/test_cloud.py` | grün |

## Was vor dem Einschalten noch fehlt

1. **Das Plugin für die Google-Anmeldung** in der Hülle (Abschnitt 8).
   Google sperrt die Anmeldung in einer WebView, deshalb geht sie nur nativ.
2. **Eine Zeile in den Einstellungen** – „Mit Google sichern", darunter
   „Zuletzt gesichert: …", „Abmelden" und „Konto löschen". Kurz halten,
   Texte in allen acht Sprachen in `sprachen.py`. `cloudLoeschen()` kann
   drei Dinge melden: `true` (alles weg), `'konto bleibt'` (Sicherung weg,
   abgemeldet; Firebase wollte für das Konto eine frische Anmeldung, die
   abgebrochen wurde oder anonym nicht geht) und `false` (nichts gelöscht,
   noch einmal versuchen).
3. **Datenschutzerklärung und Datensicherheits-Formular** (Abschnitt 9 und 10).
4. Dann erst `const CLOUD_AN = true;` in `web/index.html`.

---

## 1. Projekt anlegen

1. <https://console.firebase.google.com> öffnen, mit dem Google-Konto der App
   anmelden.
2. **Projekt hinzufügen**. Name zum Beispiel „Zmaj". Die vorgeschlagene
   Projekt-ID notieren – sie lässt sich später nicht mehr ändern.
3. **Google Analytics: aus.** Die App bindet keine Analyse ein, und das soll
   so bleiben.
4. Tarif: **Spark lassen.** Kein Upgrade auf Blaze, keine Kreditkarte.

## 2. Firestore anlegen

1. Links **Firestore Database** → **Datenbank erstellen**.
2. Edition: **Standard**.
3. Speicherort: **`europe-west3` (Frankfurt)**. Achtung: Der Ort lässt sich
   nie mehr ändern.
4. Im **Produktionsmodus** starten (alles gesperrt). Die richtigen Regeln
   kommen in Schritt 6.

## 3. Anmeldung einschalten

1. Links **Authentication** → **Jetzt starten**.
2. Reiter **Anmeldemethode**:
   - **Google** aktivieren, Support-E-Mail auswählen, speichern. Danach
     zeigt Firebase dort unter „Web SDK-Konfiguration" eine **Web-Client-ID**
     (endet auf `.apps.googleusercontent.com`). Die braucht das Plugin
     (Abschnitt 8).
   - **Anonym** aktivieren. Das ist die Ausweichmöglichkeit ohne
     Google-Konto. Achtung: Wer anonym sichert und die App-Daten löscht,
     kommt nicht mehr an seine Sicherung.
3. **Nicht** auf „Identity Platform" upgraden, auch wenn Firebase es anbietet.
   Mit dem Upgrade gilt eine Grenze von 3.000 täglich aktiven Nutzern im
   kostenlosen Tarif.

## 4. Android-App eintragen und SHA-1-Fingerabdrücke

Ohne die richtigen Fingerabdrücke lehnt Google die Anmeldung auf dem Handy
ab.

1. **Projekteinstellungen** (Zahnrad) → **Allgemein** → **App hinzufügen** →
   Android. Paketname: `de.smartdragon.zmaj` (steht als `ZMAJ_PAKET` in
   `web/index.html`).
2. Die angebotene `google-services.json` wird **nicht** gebraucht – die App
   spricht Firebase über REST an. Nicht herunterladen, nie ins Repository
   (sie steht vorsorglich in `.gitignore`).
3. Fingerabdrücke eintragen (**Fingerabdruck hinzufügen**), alle drei:
   - **App-Signaturschlüssel** von Google Play: Play Console → Zmaj →
     **App-Integrität** → **App-Signatur** → SHA-1 des Zertifikats des
     App-Signaturschlüssels. So unterschreibt Google die App, die aus dem
     Store kommt.
   - **Upload-Schlüssel**: auf derselben Seite, SHA-1 des
     Upload-Zertifikats. Damit läuft ein selbst gebautes Release-Paket.
   - **Debug-Schlüssel** zum Testen mit `app_bauen.py` ohne `--aab`:
     `keytool -list -v -keystore "%USERPROFILE%\.android\debug.keystore" -alias androiddebugkey -storepass android`
     (Zeile „SHA1").

## 5. Projekt-ID und Schlüssel in die Hülle legen

1. **Projekteinstellungen** → **Allgemein**: dort stehen **Projekt-ID** und
   **Web-API-Schlüssel** (beginnt mit `AIza`).
2. In der Hülle die Datei `zmaj-android\cloud_zugang.json` anlegen:

   ```json
   {"projekt": "PROJEKT-ID", "schluessel": "WEB-API-SCHLUESSEL"}
   ```

   Nur dort. `app_bauen.py` setzt beide Werte beim Bauen in die Kopie
   `www/index.html` ein (`cloud_einsetzen()`), so wie den Dauer-Prüfwert.
   `projekt_sichern.py` lässt die Datei aus der Projekt-Zip heraus.
3. Ohne die Datei bleibt die Cloud aus. Steht `CLOUD_AN` auf `true` und die
   Datei fehlt, bricht der Bau mit einer Meldung ab.
4. Den Schlüssel in der **Google Cloud Console** einschränken
   (<https://console.cloud.google.com> → das Firebase-Projekt → APIs und
   Dienste → Anmeldedaten → der Schlüssel „Browser key" bzw. „Android key"):
   - **API-Einschränkungen**: nur *Identity Toolkit API*, *Token Service API*
     und *Cloud Firestore API*.
   - **Anwendungseinschränkung: keine.** Eine Einschränkung auf Android-Apps
     greift hier nicht – die WebView schickt die Kennung der App nicht mit,
     und jede Anfrage würde abgelehnt.

   Der Web-API-Schlüssel ist kein Passwort; er steht in jeder Firebase-App.
   Geschützt werden die Daten durch die Regeln aus Schritt 6.

## 6. Sicherheitsregeln einspielen

1. **Firestore Database** → Reiter **Regeln**.
2. Den ganzen Inhalt von `firestore.rules` einfügen, **Veröffentlichen**.
3. Prüfen im **Regel-Playground** (gleiche Seite):
   - `get` auf `/users/abc` mit Anmeldung als `abc` → erlaubt
   - `get` auf `/users/abc` mit Anmeldung als `xyz` → abgelehnt
   - `get` auf `/users/abc` ohne Anmeldung → abgelehnt

Die Regeln erlauben nur das eigene Dokument `users/{uid}` mit genau zwei
Textfeldern (`daten` höchstens 400.000 Zeichen, `rev` höchstens 100).

## 7. Datenverarbeitung (AVV)

**Projekteinstellungen** → **Datenschutz**: die Bedingungen zur
Datenverarbeitung (Data Processing Terms) prüfen und annehmen und die
Kontaktdaten für den Datenschutz eintragen. Das ist der
Auftragsverarbeitungsvertrag mit Google.

## 8. Plugin für die Google-Anmeldung (Hülle)

Die App ruft `Capacitor.Plugins.ZmajAnmeldung.googleAusweis()` auf und
erwartet `{idToken: "…"}` zurück (`cloudGoogleAusweis()` in `index.html`).
Gebaut wird es in der Hülle wie die anderen eigenen Plugins:

- Bibliotheken: `androidx.credentials:credentials`,
  `androidx.credentials:credentials-play-services-auth`,
  `com.google.android.libraries.identity.googleid:googleid`.
- `GetGoogleIdOption` (oder `GetSignInWithGoogleOption` für den Knopf) mit
  `setServerClientId(<Web-Client-ID aus Schritt 3>)`. Die Web-Client-ID
  kommt wie der Schlüssel aus der Hülle, nicht aus dem Repository.
- Aus der Antwort `GoogleIdTokenCredential.idToken` an die App geben.
  Abbruch durch den Nutzer: ablehnen – die App nimmt das als „nicht
  angemeldet".
- Die App tauscht das Token selbst bei Firebase ein
  (`accounts:signInWithIdp`).

## 9. Datenschutzerklärung (alle acht Sprachen, `sprachen.py`)

Vor dem Einschalten ergänzen:

- **Freiwillig:** Die Cloud-Sicherung ist aus, bis der Nutzer sie selbst
  einschaltet; die App funktioniert ohne sie vollständig.
- **Zweck:** Sicherung des Lernstands und Umzug auf ein neues Gerät.
- **Welche Daten:** der Lernstand (gelernte Wörter, Level, Lerntage,
  Münzen, gekaufter und getragener Zierrat, Fehler- und Stern-Liste,
  Einstufung), eine zufällige Gerätekennung im Feld `rev`, die
  Firebase-Nutzerkennung; bei Anmeldung mit Google zusätzlich E-Mail-Adresse,
  Name und Profilbild-Adresse aus dem Google-Konto (speichert Firebase
  Authentication). Technisch dazu die IP-Adresse bei jeder Anfrage.
- **Empfänger:** Google Ireland Ltd. (Firebase) als Auftragsverarbeiter.
  Der Lernstand liegt in Frankfurt (`europe-west3`), die **Anmeldedaten von
  Firebase Authentication werden in den USA verarbeitet** – Übermittlung auf
  Grundlage des EU-US Data Privacy Framework (Google LLC ist zertifiziert)
  und der Standardvertragsklauseln.
- **Rechtsgrundlage:** Art. 6 Abs. 1 lit. b DSGVO (die vom Nutzer gewählte
  Funktion).
- **Speicherdauer:** bis der Nutzer die Sicherung löscht.
- **Löschen:** in der App „Konto löschen" (löscht Sicherung und Konto) oder
  per Mail an die Adresse im Impressum.
- Die Premium-Freischaltung steht nie in der Cloud (sie ist nicht Teil des
  Lernstands), und die App überträgt weiterhin keine Analysedaten.

## 10. Play Console

**App-Inhalte → Datensicherheit** neu ausfüllen:

- Daten werden erhoben: **ja**.
- **Persönliche Daten → E-Mail-Adresse** (nur bei Google-Anmeldung) und
  **Nutzer-IDs** – Zweck: App-Funktionen, Kontoverwaltung.
- **App-Aktivitäten → Sonstige Aktionen** (der Lernstand) – Zweck:
  App-Funktionen.
- Bei allen: **optional** (der Nutzer entscheidet), **nicht geteilt**
  (Google ist hier Auftragsverarbeiter), **bei der Übertragung
  verschlüsselt** (HTTPS), **Löschung kann beantragt werden**.
- **Kontolöschung:** Google Play verlangt bei Apps mit Konten einen Weg in
  der App **und** eine Webadresse, über die man die Löschung beantragen kann
  – zum Beispiel ein Abschnitt auf der GitHub-Seite mit der Mailadresse.
  Die Adresse im Formular eintragen.

## 11. Einschalten und prüfen

1. Abschnitte 1 bis 10 erledigt, Plugin und Einstellungszeile gebaut.
2. `const CLOUD_AN = true;` in `web/index.html`.
3. Tests: `pytest`, `ruff check .`, `texte_pruefen.py`, dann die
   Browser-Tests (`tests_e2e`, darin `test_cloud.py`).
4. Auf dem Handy: anmelden, lernen, App in den Hintergrund → in der Firebase
   Console unter Firestore steht `users/<uid>`. Zweites Gerät oder
   Neuinstallation: anmelden → der Lernstand ist zusammengeführt, nichts
   fehlt.
5. In der Firebase Console unter **Nutzung** nachsehen: höchstens ein
   Schreibvorgang je Nutzer und Tag (plus einer beim ersten Anmelden).

## 12. Grenzen und wann es Geld kostet

- **Spark:** 20.000 Schreibvorgänge und 50.000 Lesevorgänge am Tag, 1 GiB
  gespeichert, 10 GiB Datenverkehr im Monat. Darüber antwortet Firestore bis
  zum nächsten Tag mit einem Fehler (`RESOURCE_EXHAUSTED`); die App versucht
  es dann still später noch einmal, auf dem Gerät geht nichts verloren.
- Die App schreibt höchstens einmal am Tag je Nutzer und liest höchstens
  zweimal. Eng wird es ab etwa **12.000–15.000 täglich aktiven Nutzern**.
  Dann auf **Blaze** wechseln und sofort eine **Budget-Warnung von etwa 5 €
  im Monat** setzen – Blaze hat keine harte Kostenbremse.
- Preise und Grenzen vor dem Einschalten noch einmal nachsehen; sie ändern
  sich.

## 13. Anbieter wechseln

Die App kennt Firebase nur in `cloudFirestore()`. Ein anderer Anbieter
(Ausweiche laut Recherche: Cloudflare Workers + D1) braucht einen neuen
Adapter mit denselben vier Funktionen – `anmelden`, `laden`, `speichern`,
`loeschen` – und dasselbe JSON. Am Zusammenführen und an der Bündelung
ändert sich nichts.

## Was man nicht tun sollte

- Keine Schlüssel, Projekt- oder Client-IDs in dieses Repository – auch
  nicht in Tests oder Beispiele.
- Kein Upgrade auf Identity Platform.
- Den Firestore-Speicherort nicht „mal eben" anders wählen – er bleibt für
  immer.
- Kein Firebase-SDK und keine `google-services.json` einbauen; die App
  kommt mit REST aus, und so bleibt der Wechsel einfach.
