# Plan: Codex for Open Source

Stand 04.10.2026. Ziel, Ausgangslage, Bewertungsmodell, Meilensteine,
Kennzahlen und Arbeitsschleife – so genau, dass jeder Schritt prüfbar ist.

---

## 1. Ziel

> **Eine Zusage aus dem Programm „Codex for Open Source“ für
> `zmaj-lernapp/zmaj`** – mindestens eine der drei Leistungen (6 Monate
> ChatGPT Pro mit Codex, API-Credits, Codex Security).

Abgeschickt wird, sobald die Schwellen aus Abschnitt 5 erreicht sind,
**spätestens am 01.11.2026**. Die Bewerbungen werden laufend geprüft; eine
Frist gibt es nicht, eine stärkere Bewerbung schlägt eine frühe.

**Was nicht erreichbar ist: 100 %.** Entschieden wird von Menschen bei
OpenAI nach „relevanter Nutzung, breiter Akzeptanz oder klarer Bedeutung für
das Ökosystem“ und nach dem Budget des Fonds. Ein Repository kann gut
gepflegt sein – Nutzung entsteht draußen. Dieser Plan maximiert, was wir
beeinflussen können, und sagt ehrlich, wo die Grenze liegt.

## 2. Ausgangslage (gemessen am 04.10.2026)

| Kennzahl | Wert | Quelle |
|---|---:|---|
| Sterne / Forks / Beobachter | 0 / 0 / 0 | GitHub |
| Mitwirkende | 1 | GitHub |
| Alter des Repositories | 14 Tage (seit 20.09.2026) | GitHub |
| Play-Store | geschlossener Test seit 23.09.2026 | Play Console |
| Abhängige Repos / Pakete | 0 | GitHub |
| Lizenz vor diesem Umbau | keine (rechtlich kein Open Source) | – |
| Tests / CI vor diesem Umbau | keine | – |

Die Stärke liegt nicht in Zahlen, sondern in der **Lücke**: Duolingo,
Babbel, Busuu, Rosetta Stone und Lingoda bieten weder Bosnisch noch
Kroatisch oder Serbisch an (Recherche der Projektmappe,
`mappe/kapitel2.json`, Belege in `mappe/anhang_quellen.json`). Ein offener,
muttersprachlich geprüfter Bosnisch-Kurs mit Tonspur existiert sonst kaum.

## 3. Bewertungsmodell

Die Programmseite nennt vier Dinge: Maintainer-Rolle, Nutzung/Bedeutung,
aktive Pflege, Nutzung der Credits. Die Gewichte sind **unsere Annahme**,
nicht OpenAIs – sie ordnen nur, wo sich Arbeit lohnt.

| Kriterium | Gewicht | vorher | nach dem Umbau | am Ziel |
|---|---:|---:|---:|---:|
| A. Nutzung und Verbreitung (Sterne, Installationen, Downloads) | 40 % | 0 | 1 | 5 |
| B. Bedeutung fürs Ökosystem (Lücke, offener Datensatz, Zitierbarkeit) | 25 % | 2 | 6 | 8 |
| C. Gesundheit des Projekts (Lizenz, Tests, CI, Sicherheit, Doku) | 15 % | 1 | 9 | 9 |
| D. Konkreter Codex-Einsatz (Workflows, AGENTS.md, Belege) | 15 % | 0 | 7 | 9 |
| E. Maintainer-Rolle eindeutig | 5 % | 8 | 10 | 10 |
| **Gewichtete Punktzahl (0–10)** | | **0,9** | **4,4** | **7,2** |

Rechenweg „nach dem Umbau“: 0,40·1 + 0,25·6 + 0,15·9 + 0,15·7 + 0,05·10 = 4,40.

**Grobe Einschätzung der Zusagewahrscheinlichkeit** (Urteil, keine Messung –
OpenAI veröffentlicht keine Quote):

| Stand | Einschätzung |
|---|---|
| vorher (ohne Lizenz) | unter 5 % |
| nach dem Umbau, ohne Nutzung | 10–15 % |
| am Ziel (Abschnitt 5 erfüllt) | 25–40 % |

Der größte Hebel ist A – und A lässt sich nicht im Repository bauen, nur
draußen gewinnen. Deshalb sind M3 bis M5 die wichtigsten Meilensteine.

## 4. Meilensteine

Jeder Meilenstein hat ein **Abnahmekriterium**, das sich mit Ja/Nein prüfen lässt.

### M0 – Repository bereit · erledigt 04.10.2026 · Claude
AGPL-3.0 + CC BY-SA 4.0, REUSE, Datensatz in `data/`, 30 Tests, CI, CodeQL,
gitleaks, Scorecard, Release-Workflow, AGENTS.md, Codex-Workflows,
englisches README, Community-Dateien, Bewerbungstexte.
**Abnahme:** `pytest`, `ruff check .`, `reuse lint`, `actionlint` grün. ✅

### M1 – Einstellungen auf GitHub · Tag 0–1 · Ajdin, 30 Minuten
Nur im Browser möglich, Claude hat dafür keine Rechte:

- [ ] Pull Request `claude/gallant-turing-c49bt1` → `master` mergen
- [ ] **Beschreibung ändern** – sie lautet noch „Private Sicherung des
      Projekts“. Neu: *Learn Bosnian offline: open course with audio in 8
      languages – app (AGPL) and dataset (CC BY-SA)*
- [ ] Topics: `bosnian`, `language-learning`, `dataset`, `low-resource-languages`,
      `anki`, `education`, `offline-first`, `android`, `tts`, `open-data`
- [ ] Settings → General: *Discussions* an, *Wiki* aus
- [ ] Settings → Code security: *Private vulnerability reporting* an,
      *Dependabot alerts* und *security updates* an, *Secret scanning* an
- [ ] Settings → Branches: Regel für `master` – Pull Request nötig,
      Checks `Content & tests`, `REUSE licensing`, `Secret scan` müssen grün sein
- [ ] Labels anlegen: `language-correction`, `translation`, `codex-triage`, `codex-review`,
      `good first issue`, `help wanted`, `needs-native-speaker`
- [ ] Profil `zmaj-lernapp`: öffentlich, Name, Bild (der Drache), Bio,
      Repository anpinnen

**Abnahme:** CI auf `master` grün; Scorecard-Badge zeigt eine Zahl ≥ 6.

### M2 – Erste Veröffentlichung · Tag 1 · Ajdin
```bash
git tag -a v1.0.0 -m "Zmaj 1.0.0" && git push origin v1.0.0
```
Der Release-Workflow hängt Datensatz-Zip, Anki-Zip und Prüfsummen an.
Danach in Zenodo (zenodo.org → GitHub) das Repository einschalten und einen
weiteren Tag pushen: das gibt eine **DOI** – zitierbar, ein starkes Signal für B.
**Abnahme:** Release mit 3 Dateien; DOI-Badge im README.

### M3 – Play Store öffentlich · ab 07.10.2026 · Ajdin
Der geschlossene Test läuft seit 23.09.; die 14 Tage sind am 07.10. um.
Dann Produktionszugriff beantragen (Ablauf in `PRODUKTIONSZUGRIFF.md`).
**Abnahme:** öffentlicher Play-Link im README und im Repo-„Website“-Feld.

### M4 – Datensatz verbreiten · Woche 1–2 · Ajdin, Claude bereitet vor
- Hugging Face: Datensatz `zmaj-lernapp/zmaj-bosnian` mit Datenblatt und Link zurück
- Kaggle: derselbe Datensatz
- AnkiWeb: Stapel „Bosnian – Zmaj (English)“ und „Bosnisch – Zmaj (Deutsch)“
- Wikidata/OPUS-Hinweis, falls passend

**Abnahme:** drei externe Seiten verlinken auf das Repository.

### M5 – Gemeinschaft · Woche 1–3 · Ajdin
- 8 Issues „Review translations: <Sprache>“, Label `good first issue`
- Beiträge (ehrlich, kein Spam, je einmal): r/bih, r/bosnia, r/languagelearning,
  r/Anki, Hacker News „Show HN“, deutsch-bosnische Vereine und
  Facebook-Gruppen, Lehrkräfte für herkunftssprachlichen Unterricht und
  Volkshochschulen mit „Bosnisch/Kroatisch/Serbisch“
- Codex sichtbar einsetzen: mit eigenem kleinem API-Budget `OPENAI_API_KEY`
  als Secret hinterlegen, damit die Bewerbung echte Codex-Reviews zeigen kann

**Abnahme:** Schwellen aus Abschnitt 5.

### M6 – Bewerbung abschicken · sobald Abschnitt 5 erfüllt, spätestens 01.11.2026
`BEWERBUNG.md`: Platzhalter `[N]` mit den Zahlen vom Tag füllen, `pytest`
laufen lassen (Zeichengrenze), abschicken. Parallel die Fassung für
„Claude for Open Source“.
**Abnahme:** Bestätigungsmail von OpenAI.

### M7 – Danach
Zusage: Codex Security einschalten, Credits für die Workflows nutzen, im
README danken. Absage: weiter messen, nach drei Monaten mit neuen Zahlen
erneut bewerben, falls das Programm es zulässt.

## 5. Kennzahlen und Schwellen

| Kennzahl | heute | Schwelle zum Abschicken | Ziel | gemessen mit |
|---|---:|---:|---:|---|
| GitHub-Sterne | 0 | 50 | 150 | Repository-Seite |
| Play-Installationen | 0 | 300 | 2 000 | Play Console → Statistiken |
| Datensatz-Downloads (Releases + Hugging Face) | 0 | 100 | 500 | `gh api repos/zmaj-lernapp/zmaj/releases` → `download_count`; HF-Seite |
| externe Mitwirkende (Issue oder PR) | 0 | 3 | 10 | Insights → Contributors, Issues |
| übernommene Sprachkorrekturen | 0 | 5 | 20 | Label `language-correction`, geschlossen |
| Pull Requests mit Codex-Review | 0 | 3 | 10 | Kommentare „Codex review“ |
| OpenSSF Scorecard | – | 6,0 | 7,5 | Badge im README |
| externe Verlinkungen (HF, Kaggle, AnkiWeb, Zenodo) | 0 | 2 | 4 | – |

Abschicken, wenn **mindestens fünf der acht Schwellen** erreicht sind –
oder am 01.11.2026, je nachdem, was zuerst kommt.

**Messen:** `python3 kennzahlen.py` holt die GitHub-Werte selbst und liest den
Rest aus [`kennzahlen_manuell.json`](kennzahlen_manuell.json) (Play Console,
Hugging Face, Scorecard, Verlinkungen – dort mit Datum nachtragen). Es endet
mit 0, sobald fünf Schwellen erreicht sind; `--markdown` gibt die Tabelle zum
Einfügen aus.

## 6. Risiken

| Risiko | Wirkung | Gegenmittel |
|---|---|---|
| Wenig Nutzung bis zum Stichtag | A bleibt schwach | Bewerbung über B und D tragen; Lücke belegen |
| App wirkt kommerziell (Werbung, Abo) | Zweifel an „Open Source“ | Offen benennen (README „Funding, openly“); alles Lernen bleibt frei; Code und Inhalt frei lizenziert |
| Übersetzungen fehlerhaft | Glaubwürdigkeit | Datenblatt sagt es offen; Korrektur-Formular; Sprachprüfer |
| Ein Maintainer | Busfaktor 1 | GOVERNANCE.md, freie Lizenzen, alles im Repo |
| Beschreibung „Private Sicherung“ bleibt stehen | Prüfer stutzt | M1 |
| `mappe/` enthält Schulunterlagen mit Namen Dritter (Betreuer) | Datenschutz | prüfen, ob das öffentlich bleiben soll; sonst aus `master` entfernen |
| `vokabeln.py`: Level 52 und 58 fragen im Test Wörter aus Level 60 ab | Lernende sehen Ungelerntes | inhaltlich entscheiden (Liste `BEKANNT` in `tests/test_inhalt.py`) |

## 7. Arbeitsschleife („Loop“)

Damit die Arbeit ohne neue Anweisung weitergeht, folgt jeder Durchlauf –
egal ob Mensch, Claude oder Codex – demselben Ablauf:

1. **Nehmen:** den obersten offenen Punkt aus `BACKLOG.md`.
2. **Bauen:** kleinste Änderung, die das Abnahmekriterium erfüllt.
3. **Prüfen:** `python3 -m pytest && ruff check . && reuse lint` – rot heißt:
   zurück zu 2, nie weiter.
4. **Festhalten:** ein Commit je Punkt, Autor `zmaj.lernapp@gmail.com`, pushen.
5. **Messen:** Abschnitt 5 aktualisieren, wenn sich eine Zahl bewegt hat.
6. **Abhaken** in `BACKLOG.md`, dann zurück zu 1.

**Abbruch** nur, wenn (a) der Backlog leer ist, (b) ein Punkt eine
Entscheidung von Ajdin braucht – dann wird er als Frage notiert und der
nächste genommen – oder (c) das Budget erreicht ist. Budget ausgeben ist kein
Ziel: jeder Durchlauf muss einen Punkt aus dem Backlog abschließen.
