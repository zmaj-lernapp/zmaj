# Backlog

Abgearbeitet nach [PLAN.md §7](PLAN.md#7-arbeitsschleife-loop): von oben
nach unten, ein Commit je Punkt, erst abhaken, wenn das Abnahmekriterium
erfüllt und `pytest`, `ruff check .` und `reuse lint` grün sind.

**C** = kann ein Agent allein · **A** = braucht Ajdin (Konto, Entscheidung, Browser)

## Offen

| # | Wer | Punkt | Abnahmekriterium | Hebel (PLAN §3) |
|---|---|---|---|---|
| 7 | C | Weitere Inhaltstests: Grammatik-Tabellen rechteckig, Optionen ohne Dubletten, Wörterbuch ohne Leereinträge | Tests grün oder echte Befunde dokumentiert | C |
| 8 | A | M1: PR mergen, Beschreibung, Topics, Discussions, Private Vulnerability Reporting, Branch-Schutz, Labels, Profil | Checkliste in PLAN.md M1 vollständig | C, E |
| 9 | A | M2: Tag `v1.0.0`, Zenodo einschalten → DOI | Release mit 3 Dateien, DOI-Badge | B |
| 10 | A | M3: Play-Produktion (ab 07.10.2026) | öffentlicher Play-Link im README | A |
| 11 | A | `OPENAI_API_KEY` als Secret, damit Codex-Reviews sichtbar laufen | erster PR mit Kommentar „Codex review“ | D |
| 12 | A | Entscheidung: Level 52/58 fragen Wörter aus Level 60 ab (`formell`) | `BEKANNT` in `tests/test_inhalt.py` leer | C |
| 13 | A | Entscheidung: `mappe/` (Schulunterlagen, Name des Betreuers) öffentlich lassen? | entschieden und umgesetzt | Risiko |
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
| #6 `store/bilder_machen/bilder_playwright.py`: Store-Bilder in jeder Sprache, plattformunabhängig | dieser Commit |
