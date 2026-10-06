# Changelog

All notable changes to this repository. The app's user-facing release notes
are in the Play Store listing. Format:
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `huelle.py`: the build scripts find the Android shell as `../zmaj-android`
  or `../zmaj-huelle` (fresh clone), or via `ZMAJ_HUELLE`.
- OpenSSF Best Practices entry (project 15225) with badge in the README.
- DOI 10.5281/zenodo.23146609 (Zenodo, all versions) in the README, `CITATION.cff` and the
  dataset documentation.
- Settings: "Rate Zmaj", "Recommend Zmaj" and links to Zmaj on TikTok,
  Instagram and YouTube; the website footer links the same channels.
- Settings: a short notice with a link to Google Play when a subscription is
  on hold because a payment failed.

### Fixed
- Ads: the maximum ad content rating is "General", matching the app's content
  rating; a session started offline now retries AdMob once the device is
  back online; a rewarded video closed early no longer reports "no ad".
- The rating card no longer appears right after a full-screen ad.
- Every purchase button opens the purchase sheet directly.
- "Words in this level" is complete in all interface languages, the
  "level test unlocked" hint appears, and the daily tasks no longer change
  in the middle of the day.
- Speech check: double letters are collapsed again (broken back-reference).
- The dragon rests when animations are off or reduced motion is set, and
  pauses in hidden views.
- Cancelling "Save backup" shows a neutral note instead of an error.

### Changed
- The dataset no longer names text-to-speech as a task or intended use
  (Hugging Face card, datasheet, Zenodo, citation and package keywords). The
  audio is Azure TTS output and must not be used to train speech synthesis;
  the store version of the app uses other recordings that are not part of
  the dataset.

## [1.2.1] – 2026-10-04

### Fixed
- Zenodo archiving: metadata now comes from `.zenodo.json`; Zenodo could not
  read the two licences listed in `CITATION.cff`.

## [1.2.0] – 2026-10-04

### Changed
- Patch scripts share one implementation of the dry-run, anchor and CRLF
  rules (`richten.py`); one parametrized test covers every pending script.
- App content and web demo are written by the same function
  (`inhalt_bauen.schreiben`); output is byte-identical.
- CI caches pip downloads and the Playwright browser, lints once, and
  cancels superseded CodeQL runs. Store feature graphic recompressed
  losslessly (529 KB to 208 KB).
- Python 3.10 is the minimum (3.9 is end of life since October 2025); CI runs
  on 3.10 and 3.13.
- Playwright moved from `requirements-dev.txt` to its own lock file
  `requirements-e2e.txt`, used only by the browser tests.
- The Codex workflows start no runner unless the repository variable
  `CODEX_AN` is `true` (besides the `OPENAI_API_KEY` secret).
- `start.py` only serves the app locally; content loading lives in
  `inhalt.py` (`start.lade_daten` still works).
- `werbung_richten.py` and `werbung_texte.py` reduced to the changes that are
  still open; both dry-run cleanly again and are covered by tests.
- Test backups in `testdaten/` cover the whole course again; a test keeps
  them in step with the content.
- German maintainer notes merged into `ANLEITUNG.md`.
- The web demo on GitHub Pages builds on every push to `master`; the extra
  repository variable `PAGES_DEMO` is no longer needed.

### Removed
- Internal working notes, finished one-off patch and migration scripts and
  their intermediate files. Audio and translation review reports moved to
  `docs/`.
- The old local account server (`konten.py`, `mail.py`, accounts, sessions
  and progress files in `start.py`). Accounts were already switched off in
  the app.

## [1.1.0] – 2026-10-04

### Added
- Parallel corpus for machine translation: `data/parallel.tmx` (TMX 1.4b),
  `data/parallel.jsonl` and `data/parallel/bs-<lang>.tsv`, with schema and tests.
- 20 browser end-to-end tests (`tests_e2e/`, Playwright) in their own CI job.
- Accessibility audit with axe-core; fixes prepared as
  `barrierefreiheit_richten.py` (0 serious/critical findings after applying).
- Second security review; two hardenings prepared as `sicherheit2_richten.py`.
- AI pre-check of all seven translations: 59 candidates posted to the
  translation issues for native speakers to confirm or reject.

### Changed
- `mappe/` (school project documents with names of third parties) removed
  from the public repository.
- Anki packages: every language now has its own note IDs, so several language
  decks can live side by side. Packages from v1.0.0 import as new notes.
- Patch scripts work on Windows checkouts with CRLF line endings; `data/` is
  always checked out with LF.
- Release workflow refuses a tag that already points at another commit and
  starts the PyPI workflow after a release run by hand; the PyPI workflow
  checks that the package version matches the tag.
- Codex workflows: a label event no longer cancels a review already running.

## [1.0.0] – 2026-10-04

First open-source release of the repository and the dataset.

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
- Live web demo without ads (`demo_bauen.py`, GitHub Pages workflow, off
  until enabled).
- Anki packages with audio, one per language, attached to releases
  (`anki_bauen.py`).
- Hugging Face dataset card (`data/README.md`), English architecture overview
  (`docs/ARCHITECTURE.md`), social preview image.
- 13 Mermaid diagrams (data flow, content model, quality gates, review
  sequence, language-correction flow, backup import, governance, roadmap);
  a test keeps their numbers in sync with the dataset.
- Cross-platform store screenshots in any language
  (`store/bilder_machen/bilder_playwright.py`).
- More tests: grammar tables, duplicate answer options, glossary, level
  labels in all eight languages; dead links in the documentation.

- PyPI package `zmaj-bosnian` (`paket/`), Hugging Face upload in the release
  (`hf_hochladen.py`), weekly metrics workflow, AnkiWeb texts, Bosnian README.

### Changed
- Development tools are locked with hashes (`requirements-dev.in` →
  `requirements-dev.txt`) and installed with `--require-hashes` in CI.

### Fixed
- Security review of the backup import: a hand-written backup could lock
  the app at every start (`"gewusst":[1]`), grant unlimited hearts or break
  the review tab. The fix is prepared as `import_richten.py` and applied for
  the first build after the closed test.
- French terms of service: the heading "Rétractation et remboursement" was
  missing, leaving an unbalanced `</b>` before the withdrawal clause.

## 2026-09-23 – closed test on Google Play

- 65 levels, 1,728 words, 16 grammar lessons, 12 stories, eight interface
  languages, synthetic Bosnian audio for every word, sentence and story.
