# Changelog

All notable changes to this repository. The app's user-facing release notes
are in the Play Store listing. Format:
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Spaced review of learned words (Leitner box, decided on 28.10.2026):
  every word you know has a level with a fixed interval of 1, 3, 7, 14, 30,
  90 or 180 days. A right answer moves it up one level, also before the
  due date, but at most once a day (a word you already practised today
  stays where it is, and a right answer never brings the date closer); a
  wrong answer moves it back two (never below the first). Every lesson fills up to 3 of its
  10 word slots with due words, marked "Review: <level>" as in the level
  test, never as a speaking task (those can be skipped); new words and the
  "Continue" button stay as they are. The Review tab has a third box, "Due
  today", below the two existing ones, with its own round: lives, streak,
  coins and daily quests as in the other rounds, and a wrong answer also
  goes to the mistakes box. At most 30 due words a day; the rest stays due
  for the following days. The most overdue relative to its interval comes
  first, so a word learned yesterday comes before one that is a few days
  late after 90 days. The review day starts at 4 a.m., so a word learned
  just before midnight is not due minutes later. Words learned before the
  update get their first date spread over the coming weeks, at most 10 a
  day, oldest levels first. Answers in lessons, rounds and level tests
  count, the placement test does not. The progress keeps this in a new
  field `kartei` (level, due day and last practised day per word, days
  counted from 2026-08-01, about 40 bytes per word): in the device
  storage, the backup file (older files without it still load) and the
  cloud backup, where per word the more recently practised state wins.
  New texts in all eight languages.
- Account (Android app, v109): after the first lesson – or the placement
  test – the app asks you to sign in, with Google or with email and
  password ("Forgot password?" included). Existing learners sign in once at
  the next start; the progress on the phone is merged into the account, never
  overwritten. You stay signed in across restarts and updates until you sign
  out or delete the account. Without internet you just keep learning; the
  sign-in comes when the connection is back, never in the middle of a lesson.
  If Firebase or Google fails, "Keep learning for now" works the same way
  until the next start. Progress is backed up at most once a day to Cloud
  Firestore in Frankfurt. Signing out and deleting the account are on the
  profile page; both reset the progress on the phone. Deleting first asks
  for the password or the Google account, so cancelling deletes nothing.
  Accounts can also be deleted by email
  (`konto-loeschen.html`). Switching phones keeps you signed in (Android's
  backup plus a restore key through the Credential Manager). The source keeps
  `CLOUD_AN = false`: without the private `cloud_zugang.json`, the app and the
  web demo behave exactly as before, and a release build (`app_bauen.py
  --aab`) stops unless `--ohne-anmeldung` is given.
- Typing exercises and cloze sentences: an answer one keystroke away from a
  correct one (a letter wrong, missing, extra or two swapped; answers of four
  letters or more) shows "Almost right!" and leaves the field open for one
  more try, without costing a life. This includes a wrong ending ("nedjelji"
  for "nedjelja") and another real word ("deset" for "devet"). One hint
  per task; missing diacritics still count as correct straight away.
- Cloze and tile sentences: in 36 sentences the number now changes from
  task to task ("Sada je sedam sati." – "It is 7 o'clock now."), only with
  the numbers a native speaker approved (`"zahl"` in `vokabeln.py`). The
  Bosnian sentence spells the number out, the translation shows it as a
  digit (Turkish with the right suffix: 7'de, 3'te). Another number only
  comes once its word has been learned (or the numbers level has been
  passed or skipped by the placement test) and the sentence has a recording;
  the new recordings exist only in the store version, so the web demo keeps
  today's number. A retry keeps the number, and mistakes and stars stay one
  entry per sentence. "Dva plus dva je četiri." is now "Dva plus dva su
  četiri."; mistakes and stars on it carry over.
- Family level: twelve more relatives, so that aunts, uncles and cousins
  are named by side as in Bosnian (strina / amidžinica, ujna / daidžinica,
  tetak, amidžić, daidžić, tetić and their female forms, rođaka, nećak,
  nećakinja). amidža and daidža now also show stric and ujak; the pet
  names striko, adžo, ujo and dajo count as correct when typed. Progress
  on the four renamed words (tetka, amidža, daidža, rođak) carries over.
  The app speaks the new words with recordings that only the store
  version contains (`ton_nur_emir.json`); the web demo, the dataset and
  the Anki decks have no audio for them.
- Lessons, review rounds and level tests: a round star button at the top
  right of the exercise card, next to the dragon, marks a word, cloze
  sentence, tile sentence or grammar exercise for later (one star per
  word, up to 300; not in the placement test or on result screens). The
  Review tab shows a second box, "Marked", built like the unchanged
  mistakes box above it; its round picks up to ten marked items, least
  recently practised first, costs lives like a lesson, and stars stay
  until the learner removes them. The big "Continue" button is
  unchanged. Stars are part of the backup file.
- Lessons: a new exercise builds whole Bosnian sentences from word tiles
  (two per lesson, from level 1 on). Several word orders count as correct,
  a sentence only appears once its words have been met, and mistakes go to
  the Review tab. 357 sentences across all 65 levels (`SATZBAU` in
  `vokabeln.py`), 48 of them new with audio; requested by a tester.
  The answer area is ruled like a notebook with each row of tiles standing
  on its own line, and tiles glide to their place instead of jumping
  (unless "reduce motion" is switched on).
- Settings: monthly subscribers can switch to the yearly plan in the app; the
  price is shown right above the button.
- Reminders: several texts per reminder type that change by day, with Zmaj as
  the sender, and one gentle comeback note after a longer break.
- `huelle.py`: the build scripts find the Android shell as `../zmaj-android`
  or `../zmaj-huelle` (fresh clone), or via `ZMAJ_HUELLE`.
- OpenSSF Best Practices entry (project 15225) with badge in the README.
- DOI 10.5281/zenodo.23146609 (Zenodo, all versions) in the README, `CITATION.cff` and the
  dataset documentation.
- Settings: "Rate Zmaj", "Recommend Zmaj" and links to Zmaj on TikTok,
  Instagram and YouTube; the website footer links the same channels.
- Settings: a short notice with a link to Google Play when a subscription is
  on hold because a payment failed.
- In-app updates through Google Play: an update normally downloads in the
  background while you keep learning, then a small bar offers a restart.
  An update that fixes a severe security issue or another serious bug is
  mandatory (Google's update priority 4 or higher, or a `versionCode` that is
  a multiple of 100).
- `app_bauen.py --pflicht` builds such a mandatory update (next multiple of
  100); normal builds skip multiples of 100, and an unknown switch aborts the
  build before anything is copied.

### Changed
- Tablets: from 600 points on the shorter side (Android's "sw600dp") the
  whole app scales up with the screen. Upright, the column fills about
  88 % of the width (10-inch tablet: everything 1.3 times larger); in
  landscape the column stays centred and scales only as far as a lesson
  still fits without scrolling; at most 1.4 times. Lessons, level tests
  and the placement test fill the screen: upright, the dragon and the task
  sit in the middle, the answers below, and Check/Continue at the bottom,
  with room reserved so nothing jumps after an answer. Phones (under 600
  points) look exactly as before. `tests_e2e/test_tablet.py`.
- Account (v109): a new password needs 8 characters with an uppercase and
  a lowercase letter, a digit and a special character, and must not contain
  the part of the email address before the @. A checklist under the field
  ticks off each rule while typing (letters count only A–Z and a–z, as in
  Firebase); the same rules can be enforced in Firebase's password policy.
  The top bar (lives, coins, shop, profile, settings) stays in one row on
  phones down to 360 px wide; the profile button shows only its symbol, and
  the round buttons and the heart take taps on a 48 px tall area. The "You
  are signed in." message is gone. Wherever the app
  says a mail is on its way (confirming a new account, resetting the
  password), one short line says to look in the spam folder too.
- Settings → About shows the legal notice (Impressum) in all eight
  languages, the same text as on the website, readable offline; the
  sign-in screen has it too. Links in the legal texts open in the
  device's browser.
- Privacy policy (app and web demo, all eight languages, dated
  28.10.2026): a paragraph on the website zmaj-lernapp.github.io, which
  GitHub Pages hosts and where GitHub logs visitors' IP addresses. The
  contact form paragraph refers to it instead of repeating it.
- Cloud backup: up to 900,000 bytes per learner instead of 400,000
  characters (`firestore.rules` and `CLOUD_GROESSE_MAX`), measured in
  UTF-8 so the document stays below Firestore's 1 MiB. Merging, the
  backup file and the device storage keep new top-level fields that a
  newer app version adds to the progress, so this version does not drop
  them: the cloud's copy wins, a field the newer version removed stays
  removed, and when space runs short single fields stay out of the
  cloud, never all of them. A newer version keeps its own data in such
  fields only, not inside existing ones like the mistakes box or stars.
- Privacy policy and terms of use in all eight languages describe the
  account: what Firebase stores and where, how long, and how to delete it.
  The terms changed materially (account required), so existing users see the
  "terms changed" note once.
- The cloud backup no longer stores a device identifier (`rev` is a random
  value per write).
- Version number: the footer and Settings → About no longer show a fixed
  "v1.0". `app.fuss` and `app.ueber_kurz` hold `{version}` in all eight
  languages, and `t()` fills it from `APP_VERSION` in `web/index.html`. The
  number lives only in `versionName` in the private shell's
  `android/app/build.gradle` and is always the next store version (v109 is
  1.1, then 1.2, 1.3 … 1.9, 1.10). `app_bauen.py` writes it into the copy
  `www/index.html` (debug and `--nur-abgleich` with "-test") and, only after
  a finished `--aab`, raises it for the next release; a debug build,
  `--nur-abgleich` or a failed build leave it alone. A `versionName` that is
  not `major.minor` stops the build before anything is written. In the
  source, `APP_VERSION` is only a fallback for the web demo and the tests.

### Security
- The hidden developer switch no longer compares against a word in the
  source. `web/index.html` holds a placeholder; `app_bauen.py` inserts a
  PBKDF2 check value from the private Android shell at build time
  (`dauer_wort_setzen.py` creates it), and the build stops without it.
  Switches set with the old word no longer count.

### Added
- A one-time notice after a material change to the terms of use (section 9
  of the terms promised it). `AGB_WESENTLICH` in `web/index.html` holds the
  date of the last material change; new installs only remember it.
- Google Play's own payment-issue message ("fix payment") when a
  subscription payment failed, shown when the app comes to the foreground.

### Changed
- Lessons in the levels Numbers, Days of the week, Months, Numbers in a
  sentence, the verb levels (Conjugating verbs, Past tense, Future &
  plans, "Can, must, want", Daily routine) and Comparing & describing
  introduce their new words in order (jedan to deset, then nula;
  ponedjeljak to nedjelja; januar to decembar; jedan brat, dva brata,
  pet braće …; ja sam, ti si … oni su; bio sam, bio si, bio je …;
  morati, moram, moraš …; velik, veći, najveći; from getting up to going
  to bed) instead of at random (`"reihenfolge": True` in `vokabeln.py`).
  In Basics, Time and Weather & nature only a short series keeps its
  order (the greetings from Dobro jutro to Laku noć, the times of day,
  the seasons; `"reihe"`), the rest stays random. Learners already
  part-way through such a level get the words they have not learned yet
  in the same order; exercises within a lesson, reviews, level tests and
  the placement test stay shuffled.
- `app_bauen.py` converts the audio in the app bundle to Ogg/Opus at
  24 kbit/s (`ton_verkleinern()`, needs ffmpeg; cached in the shell): the
  audio inside the package shrinks from 26.9 MB to 10.2 MB. `web/audio`
  stays MP3 for the web demo, the dataset and the Anki decks.

### Fixed
- First start on a device set to Norwegian reporting "no" or "nn" (instead of
  "nb") now opens in Norwegian instead of English.
- Settings: "Switch to yearly" is hidden during the free trial week, when
  there is no paid month whose remaining days could be carried over.
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
- Full version: the settings row and the purchase box also name what Zmaj
  gets with it (new skins, costumes and a sparkle effect), matching the
  benefits listed on Google Play.
- Terms of service (section 7, all languages, dated 11.10.2026): the full
  version also gives Zmaj skins, costumes and a sparkle effect, which it
  takes off again when the full version ends; "content" now reads
  "learning content".
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
