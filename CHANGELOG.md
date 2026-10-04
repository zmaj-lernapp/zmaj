# Changelog

All notable changes to this repository. The app's user-facing release notes
are in `STORE_TEXTE.md` (section *Versionshinweise*). Format:
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Open source: code under AGPL-3.0-or-later, learning content under
  CC BY-SA 4.0, REUSE 3.3 compliant, trademark policy.
- Open dataset in `data/`: 1,728 words, 300 sentences, 12 stories, 406
  glossary entries and 16 grammar lessons in eight languages, as JSON, CSV
  and Anki decks, with JSON Schemas, a datasheet and SHA-256 manifest
  (`daten_exportieren.py`).
- Test suite (`tests/`) over content, translations, audio, dataset and
  repository; CI on Python 3.9 and 3.13; CodeQL; gitleaks; OpenSSF Scorecard;
  release workflow that publishes the dataset.
- `AGENTS.md` and Codex workflows for pull-request review and language
  triage.
- Contributor docs: README in English, CONTRIBUTING, CODE_OF_CONDUCT,
  SECURITY, SUPPORT, GOVERNANCE, issue forms, CITATION.cff.

### Fixed
- French terms of service: the heading "Rétractation et remboursement" was
  missing, leaving an unbalanced `</b>` before the withdrawal clause.

## 2026-09-23 – closed test on Google Play

- 65 levels, 1,728 words, 16 grammar lessons, 12 stories, eight interface
  languages, synthetic Bosnian audio for every word, sentence and story.
