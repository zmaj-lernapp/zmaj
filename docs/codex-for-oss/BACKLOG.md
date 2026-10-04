# Backlog

Abgearbeitet nach [PLAN.md §7](PLAN.md#7-arbeitsschleife-loop): von oben
nach unten, ein Commit je Punkt, erst abhaken, wenn das Abnahmekriterium
erfüllt und `pytest`, `ruff check .` und `reuse lint` grün sind.

**C** = kann ein Agent allein · **A** = braucht Ajdin (Konto, Entscheidung, Browser)

## Offen

| # | Wer | Punkt | Abnahmekriterium | Hebel (PLAN §3) |
|---|---|---|---|---|
| 8 | A | M1 (inkl. Live-Demo einschalten): PR mergen, Beschreibung, Topics, Discussions, Private Vulnerability Reporting, Branch-Schutz, Labels, Profil | Checkliste in PLAN.md M1 vollständig | C, E |
| 9 | A | M2: Tag `v1.0.0`, Zenodo einschalten → DOI | Release mit 3 Dateien, DOI-Badge | B |
| 10 | A | M3: Play-Produktion (ab 07.10.2026) | öffentlicher Play-Link im README | A |
| 11 | A | `OPENAI_API_KEY` als Secret, damit Codex-Reviews sichtbar laufen | erster PR mit Kommentar „Codex review“ | D |
| 12 | A | Entscheidung: Level 52/58 fragen Wörter aus Level 60 ab (`formell`) | `BEKANNT` in `tests/test_inhalt.py` leer | C |
| 13 | A | Entscheidung: `mappe/` (Schulunterlagen, Name des Betreuers) öffentlich lassen? | entschieden und umgesetzt | Risiko |
| 16 | A | Nach dem 07.10.: `python import_richten.py --schreiben`, dann Build (Sicherheitsfix Backup-Import) | App startet nach Import einer kaputten Sicherung weiter | C |
| 15 | A | OpenSSF-Best-Practices-Badge beantragen (Antworten in `BEST_PRACTICES.md`) | Badge „passing“ im README | B, C |
| 14 | A | M6: Bewerbung abschicken | Bestätigungsmail | Ziel |

## Erledigt

| Punkt | Commit |
|---|---|
| M0: Lizenzen, Datensatz, Tests, CI, AGENTS.md, Codex-Workflows, README, Community-Dateien | `445c8d2` … `01da6f4` |
| Plan, Bewerbungstexte, Zeichengrenzen-Test | `95767bb` |
| #1 Hugging-Face-Datenkarte `data/README.md` mit Test | `9e999cd` |
| #2 Anki-Pakete mit Ton im Release (`anki_bauen.py`) | `752251d` |
| #3 `kennzahlen.py` + `kennzahlen_manuell.json` | `046edbe` |
| #4 Issue-Entwürfe für 7 Übersetzungssprachen + Bosnisch (`ISSUES.md`) | `4e09ded` |
| #5 Ankündigungstexte für HN, Reddit, Vereine (`ANKUENDIGUNGEN.md`) | `17a249a` |
| #6 `store/bilder_machen/bilder_playwright.py`: Store-Bilder in jeder Sprache, plattformunabhängig | `dfcbbc8` |
| #7 Inhaltstests in allen Sprachen: 16 Tabellen, 104 Übungen, 406 Wörterbucheinträge – keine Befunde | `74df921` |
| #8 Live-Demo: `demo_bauen.py` (ohne Werbung, passender Datenschutztext), Pages-Workflow, Tests | `c0e28c4` |
| #9 Test-Werkzeuge mit Prüfsummen gesperrt (Scorecard „Pinned-Dependencies“); Demo-Link in der Bewerbung | `08e8a3b` |
| #10 `docs/ARCHITECTURE.md` auf Englisch | `d8acf36` |
| #11 Test: 39 relative Links in der Doku zeigen auf vorhandene Dateien | `c2bd25f` |
| #12 Social-Preview-Bild 1280×640 auf Englisch (`docs/assets/social-preview.png`) | `7b05ba0` |
| #13 Antworthilfe für das OpenSSF-Best-Practices-Badge | `4ccf2c3` |
| #14 Sicherheitsprüfung Backup-Import: 3 bestätigte Befunde, Fix als `import_richten.py` (im Browser vorher/nachher geprüft) | dieser Commit |
