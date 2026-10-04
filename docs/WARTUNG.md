# Zmaj – Notizen für den Maintainer

Eine Android-App zum Erlernen der bosnischen Sprache. Sie läuft vollständig
auf dem Gerät: kein Nutzerkonto, kein Server, der Lernstand verlässt das
Telefon nicht.

**65 Level** vom Alltag bis zum Arbeitsvertrag · **1728 Vokabeln** mit
bosnischer Tonspur · **16 Grammatikeinheiten** mit 104 Übungen · **12
Lesegeschichten** · Sprechaufgabe mit Spracherkennung · Oberfläche in **acht
Sprachen**

| | |
|---|---|
| Paketname | `de.smartdragon.zmaj` |
| Stand | geschlossener Test, seit 23.09.2026 laufen die 14 Tage |
| Finanzierung | Werbung über AdMob, Vollversion als Abo |

---

## Wo ich anfange, wenn ich lange nicht hier war

| Ich will … | Datei |
|---|---|
| die App am PC starten | `start.py` in Thonny öffnen, **F5** |
| am Lerninhalt arbeiten | `vokabeln.py`, `grammatik.py`, `geschichten.py` |
| Texte der Oberfläche ändern | `sprachen.py` |
| wissen, wie alles zusammenhängt | `ANLEITUNG.md` |
| in den Store | `PRODUKTIONSZUGRIFF.md` |

---

## Die Ordner

```
web/           die App selbst - index.html ist das ganze Programm
store/         Symbol, Vorstellungsgrafik, Screenshots, Logo
mappe/         die Projektmappe für die Technikerschule
github-seite/  Impressum, Datenschutz, Nutzungsbedingungen (erzeugt)
testdaten/     Profile zum Durchtesten
```

Die Android-Hülle liegt **außerhalb** dieses Ordners, daneben unter
`zmaj-android/`. Sie hat ihr eigenes Repository, weil dort der
Signierschlüssel in der Nähe liegt.

---

## Die Skripte

Alle laufen mit dem Python aus Thonny. **`python` gibt es auf diesem Rechner
nicht** — der Interpreter steht unter
`C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe`.

### Täglich

| Skript | Was es tut |
|---|---|
| `start.py` | startet die App am PC zum Ausprobieren |
| `inhalt_bauen.py` | macht aus den Python-Dateien das JSON fürs Handy |
| `app_bauen.py` | bringt den Inhalt in die Android-Hülle und baut das Paket |

### Beim Veröffentlichen

| Skript | Was es tut |
|---|---|
| `seite_bauen.py` | erzeugt die Rechtstexte als Webseite, inklusive `app-ads.txt` |
| `grafiken_bauen.py` | Symbol und Vorstellungsgrafik für den Store |
| `logo_sichern.py` | holt das SmartDragon-Zeichen aus der App als eigene Datei |
| `projekt_sichern.py` | packt den ganzen Stand in zwei Zip-Dateien |

### Liegen bereit für den Build **nach** dem Test

Diese drei dürfen erst laufen, wenn die 14 Tage durch sind — jede
Einreichung setzt Googles Prüfuhr zurück.

| Skript | Was es tut |
|---|---|
| `werbung_richten.py` | behebt 17 der 20 Befunde aus `WERBUNG_PRUEFUNG.md` |
| `werbung_texte.py` | ergänzt die Datenschutzerklärung in acht Sprachen |
| `admob_scharf.py` | tauscht die Testkennungen gegen die echten |
| `dialog_richten.py` | bringt die zwei Dialoge des versteckten Schalters ins App-Design |
| `vorspann_richten.py` | behebt den eingefrorenen Vorspann bei abgeschalteten Animationen |
| `herz_richten.py` | setzt den Lebens-Hinweis unter das Herz statt hinter die Münzen |
| `vorleser_richten.py` | die Geschichte beginnt nach einem angetippten Wort nicht mehr von vorn |
| `zurueck_richten.py` | ein Weg ins Hauptmenü nach Vokabeltest und Geschichte |
| `sicherung_richten.py` | die Meldung nach dem Sichern nennt den Dateinamen |

Alle drei folgen demselben Muster: **erst Probelauf, dann `--schreiben`.**
Ohne den Schalter passiert nichts. Kommt ein gesuchter Textabschnitt nicht
genau einmal vor, brechen sie ab und ändern gar nichts — ein halb geändertes
Programm gibt es damit nicht.

---

## Die Dokumentation

| Datei | Inhalt |
|---|---|
| `ANLEITUNG.md` | wie das Projekt gebaut und betrieben wird |
| `PRODUKTIONSZUGRIFF.md` | der Weg durch die Play Console, mit allen Fristen |
| `STORE_TEXTE.md` | Store-Eintrag, Data Safety, Inhaltseinstufung |
| `WERBUNG_PRUEFUNG.md` | 20 geprüfte Befunde zur Werbeeinbindung |
| `WAS_IST_NEU.md` | was sich zuletzt geändert hat |
| `PROJEKTMAPPE.md` | die Arbeit für die Technikerschule |
| `mappe/SCHREIBREGELN.md` | wie in der Projektmappe geschrieben wird |

---

## Was nie in dieses Repository gehört

`.gitignore` hält es draußen, aber zur Sicherheit hier noch einmal:

- **`tts_zugang.json`** – der Azure-Schlüssel für die Sprachausgabe
- **`mail_zugang.json`** – das Passwort des Postfachs
- **Der Signierschlüssel** und `keystore.properties` – ohne ihn gibt es nie
  wieder ein Update, mit ihm kann jeder eine gefälschte Version bauen.
  Er liegt in `zmaj-schluessel/` neben dem Projekt, **und seit dem
  23.09.2026 zusätzlich auf einem USB-Stick**. Das Passwort steht nirgends
  geschrieben. `projekt_sichern.py` nimmt ihn seither in die Geheim-Zip
  auf – davor fehlte er in jeder Sicherung, weil das Skript seinen Ordner
  gar nicht ansah.
- `fortschritt_*.json`, `sitzungen.json`, `codes.json` – echte Nutzerdaten
- `feedback.txt`, `start.log`, `__pycache__/`

---

*Gebaut von Ajdin Hasić. Das Maskottchen ist ein blauer Drache auf einem
Bücherstapel; zmaj heißt auf Bosnisch Drache.*
