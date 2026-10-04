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
| den nächsten Build vorbereiten | unten, „Liegen bereit“ |
| Codex-Review und -Triage einschalten | GitHub, Settings → Secrets and variables → Actions: Secret `OPENAI_API_KEY` und Variable `CODEX_AN` = `true` |

---

## Die Ordner

```
web/           die App selbst - index.html ist das ganze Programm
store/         Symbol, Vorstellungsgrafik, Screenshots, Logo
privat/        interne Unterlagen, nur lokal (in .gitignore)
github-seite/  Impressum, Datenschutz, Nutzungsbedingungen (erzeugt)
testdaten/     Profile zum Durchtesten
```

Die Android-Hülle liegt **außerhalb** dieses Ordners, daneben unter
`zmaj-android/`, in einem eigenen, privaten Repository.

---

## Die Skripte

Alle laufen mit dem Python aus Thonny. **`python` gibt es auf diesem Rechner
nicht** — der Interpreter steht unter
`C:\Users\Ajdin\AppData\Local\Programs\Thonny\python.exe`.

### Täglich

| Skript | Was es tut |
|---|---|
| `start.py` | startet die App am PC zum Ausprobieren (nur Dateien und Inhalt, keine Konten) |
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

Diese Skripte dürfen erst laufen, wenn die 14 Tage durch sind — jede
Einreichung setzt Googles Prüfuhr zurück. Reihenfolge wie in der Tabelle.

| Skript | Was es tut | Stand 04.10.2026 |
|---|---|---|
| `import_richten.py` | eine von Hand geschriebene Sicherung kann die App nicht mehr lahmlegen | Probelauf sauber, getestet |
| `sicherheit2_richten.py` | zwei kleine Härtungen (Konten-Links ohne Konten, Fest-Probe) | Probelauf sauber, getestet |
| `barrierefreiheit_richten.py` | Bildschirmleser und Kontrast: 0 kritische und 0 ernste axe-Befunde statt 20 und 102 | Probelauf sauber, getestet |
| `werbung_richten.py` | letzter Rest der Werbeprüfung: auch das belohnte Video wird vor dem Zeigen noch einmal geprüft (App noch vorne?) | Probelauf sauber, getestet. Am 04.10.2026 auf 2 Änderungen gekürzt, alles andere war von Hand drin oder bewusst anders gelöst (Liste im Skript) |
| `werbung_texte.py` | Datenschutzerklärung in acht Sprachen: Zwecke der Werbung und Ausnahme beim Satz „keine Analyse-Dienste“ | Probelauf sauber, getestet. Die Messwerte standen schon von Hand in allen acht Sprachen und sind herausgenommen. Danach auch `seite_bauen.py` |
| `admob_scharf.py` | tauscht die Testkennungen gegen die echten | zuletzt, nach den Werbe-Skripten |

Alle folgen demselben Muster: **erst Probelauf, dann `--schreiben`.**
Ohne den Schalter passiert nichts. Kommt ein gesuchter Textabschnitt nicht
genau einmal vor, brechen sie ab und ändern gar nichts — ein halb geändertes
Programm gibt es damit nicht. Danach `inhalt_bauen.py`, `seite_bauen.py`,
`app_bauen.py`.

Die früheren Patch-Skripte (Dialoge, Vorspann, Herz, Vorleser, Zurück,
Sicherungsmeldung und andere) sind angewendet und wurden am 04.10.2026
entfernt; sie stehen in der Git-Historie.

---

## Die Dokumentation

| Datei | Inhalt |
|---|---|
| `ANLEITUNG.md` | wie das Projekt gebaut und betrieben wird |
| `docs/ARCHITECTURE.md` | Überblick auf Englisch, mit Diagrammen |
| `WORTSCHATZ_KORREKTUREN.md` | was der Muttersprachler korrigiert hat – geht allem vor |
| `docs/TONBEFUNDE.md` | Prüfung der Aufnahmen |
| `docs/uebersetzungen-pruefbericht-2026-09-18.md` | Prüfung der Übersetzungen |
| `docs/barrierefreiheit-2026-10-04.md` | Prüfung der Barrierefreiheit (axe) |
| `docs/BEST_PRACTICES.md` | Antworten für das OpenSSF-Abzeichen |

Store-Texte, Prüfpläne und Arbeitsnotizen liegen nur lokal in `privat/`.

---

## Was nie in dieses Repository gehört

`.gitignore` hält es draußen, aber zur Sicherheit hier noch einmal:

- **`tts_zugang.json`** – der Azure-Schlüssel für die Sprachausgabe
- **`mail_zugang.json`** – das Passwort des Postfachs
- **Der Signierschlüssel** und `keystore.properties` – ohne ihn gibt es nie
  wieder ein Update, mit ihm kann jeder eine gefälschte Version bauen.
  `projekt_sichern.py` nimmt ihn in die Geheim-Zip auf.
- `fortschritt_*.json`, `sitzungen.json`, `codes.json` – echte Nutzerdaten aus
  der Zeit mit Kontoserver (bis 04.10.2026). Es entstehen keine neuen mehr,
  die Einträge in `.gitignore` bleiben für alte Reste stehen.
- `feedback.txt`, `start.log`, `__pycache__/`

---

*Gebaut von Ajdin Hasić. Das Maskottchen ist ein blauer Drache auf einem
Bücherstapel; zmaj heißt auf Bosnisch Drache.*
