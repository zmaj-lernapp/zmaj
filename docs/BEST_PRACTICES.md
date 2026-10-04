# Antworthilfe: OpenSSF Best Practices Badge („passing“)

Anmelden auf https://www.bestpractices.dev mit dem GitHub-Konto
`zmaj-lernapp`, Projekt `https://github.com/zmaj-lernapp/zmaj` anlegen und
die Fragen mit den Belegen unten beantworten. Erst **nach dem Merge** nach
`master`, sonst zeigen die Links ins Leere. Danach das Badge ins README.

Die Gruppen folgen dem Fragebogen. Wo „Met“ steht, reicht der Link als
Begründung. Wo etwas fehlt, steht es dabei – nicht schönreden, die Prüfer
schauen nach.

## Basics

| Kriterium | Antwort | Beleg |
|---|---|---|
| Beschreibung, was das Projekt tut | Met | `README.md` |
| Wie man mitmacht | Met | `CONTRIBUTING.md` |
| Anforderungen an Beiträge | Met | `CONTRIBUTING.md` (Checkliste), `.github/pull_request_template.md` |
| FLOSS-Lizenz | Met | AGPL-3.0-or-later (Code), CC BY-SA 4.0 (Inhalt), `LICENSE`, `REUSE.toml` |
| Lizenz an Standardort | Met | `LICENSE` im Wurzelverzeichnis |
| Grundlegende Doku | Met | `README.md`, `docs/ARCHITECTURE.md`, `ANLEITUNG.md` |
| Doku der externen Schnittstelle | Met | Datensatz: `data/DATASHEET.md`, `data/schema/*.schema.json` |
| Projektseite über HTTPS | Met | GitHub, Demo auf GitHub Pages |
| Diskussionsmöglichkeit | Met | Issues; Discussions nach M1 |
| Englische Doku | Met | README, CONTRIBUTING, SECURITY, ARCHITECTURE |
| Projekt wird gepflegt | Met | Commit-Verlauf |

## Change control

| Kriterium | Antwort | Beleg |
|---|---|---|
| Öffentliches Versionsverwaltungs-Repo | Met | GitHub |
| Zwischenstände sichtbar | Met | Commits zwischen den Releases |
| Verteilte Versionsverwaltung | Met | git |
| Eindeutige Versionsnummern | Met | Tags `v*`, `data-v*` (Release-Workflow) |
| Semantic Versioning | Met | `v1.0.0` |
| Release Notes | Met | `CHANGELOG.md`, GitHub-Releases mit erzeugten Notizen |
| Release Notes nennen behobene Schwachstellen | Met / N/A | bisher keine; SECURITY.md sagt, dass sie genannt werden |

## Reporting

| Kriterium | Antwort | Beleg |
|---|---|---|
| Fehler melden | Met | Issue-Formulare |
| Issue-Tracker | Met | GitHub Issues |
| Reaktion auf Meldungen | Met | `SUPPORT.md`: „within a few days“ |
| Verbesserungswünsche | Met | Formular „Idea or request“ |
| Archiv der Meldungen | Met | GitHub Issues |
| Schwachstellen melden | Met | `SECURITY.md`, Private Vulnerability Reporting (M1 einschalten!) |
| Private Meldung möglich | Met | GitHub Advisories + Mail |
| Antwortzeit ≤ 14 Tage | Met | `SECURITY.md`: 5 Tage |

## Quality

| Kriterium | Antwort | Beleg |
|---|---|---|
| Funktionierendes Build-System | Met | `inhalt_bauen.py`, `daten_exportieren.py`, `demo_bauen.py`; App braucht keinen Build |
| Automatisierte Testsuite | Met | `tests/`, `python3 -m pytest` (50 Tests) |
| Tests in CI | Met | `.github/workflows/ci.yml` |
| Neue Funktionen bekommen Tests | Met | CONTRIBUTING-Checkliste; Beispiel: `test_demo.py` mit `demo_bauen.py` |
| Warnungen des Compilers/Linters | Met | `ruff check .` in CI |
| Warnungen werden behoben | Met | CI schlägt bei ruff-Befunden fehl |

## Security

| Kriterium | Antwort | Beleg |
|---|---|---|
| Kenntnisse sicherer Entwicklung | Met | `SECURITY.md`, `AGENTS.md` (keine Netzzugriffe, keine Geheimnisse) |
| Keine kaputte Kryptografie | N/A | die App verschlüsselt nichts selbst; Prüfsummen SHA-256 |
| Auslieferung über HTTPS / signiert | Met | Play Store (signiertes Bundle), GitHub-Releases mit `SHA256SUMS.txt` |
| Keine öffentlich bekannten, offenen Schwachstellen > 60 Tage | Met | – |
| Keine Zugangsdaten im Repo | Met | `.gitignore`, gitleaks über die ganze Geschichte in CI |

## Analysis

| Kriterium | Antwort | Beleg |
|---|---|---|
| Statische Analyse | Met | CodeQL (`codeql.yml`), ruff |
| Befunde werden behoben | Met | Code-Scanning-Alerts im Security-Tab |
| Dynamische Analyse | Unmet / N/A | kein Fuzzing; ehrlich angeben. Die Inhaltstests prüfen alle 8 Sprachen gegen die echte Ladefunktion |

Fehlt danach noch etwas, als Issue anlegen.
