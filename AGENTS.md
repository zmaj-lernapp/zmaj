# AGENTS.md

Guidance for coding agents (Codex, Claude Code, Cline, OpenCode, …) and for
humans who review their work. Read this before changing anything.

## What this repository is

Zmaj is an offline app for learning Bosnian. `web/index.html` is the whole
app (HTML, CSS and JavaScript in one file, no build step, no framework). The
learning content lives in Python data files and is turned into JSON for the
app and into the open dataset in `data/`. The Android shell lives in a
separate, private repository; nothing here needs Android tooling.

| Path | What it is | Edit by hand? |
|---|---|---|
| `vokabeln.py` | 9 sections, 65 levels, 1,728 words, 300 cloze sentences | yes |
| `grammatik.py` | 16 grammar lessons with exercises | yes |
| `geschichten.py` | 12 reading stories and their glossary | yes |
| `uebersetzungen.py` | translations of all content into en, tr, sv, nl, nb, da, fr | yes |
| `sprachen.py` | interface texts in 8 languages, legal texts | yes |
| `web/index.html` | the app | yes |
| `web/audio/` | 2,332 synthesised MP3s + `index.json` | **no** – produced by `ton_bauen.py`, costs money |
| `web/inhalt/` | app content as JSON | **no** – `python3 inhalt_bauen.py` (gitignored) |
| `data/` | open dataset | **no** – `python3 daten_exportieren.py` |
| `*_richten.py` | one-off patch scripts for `web/index.html` | run only when asked |

## Commands

```bash
python3 -m pip install -r requirements-dev.txt   # test tools only; the app needs nothing
python3 -m pytest                                # all checks, ~2 s
ruff check .                                     # lint
python3 daten_exportieren.py                     # rewrite data/ after content changes
python3 inhalt_bauen.py && python3 texte_pruefen.py  # app JSON + UI text check
python3 start.py                                 # run the app at http://localhost:8000
reuse lint                                       # licensing of every file
```

A change is done when `pytest`, `ruff check .` and `reuse lint` pass and
`python3 daten_exportieren.py --pruefen` reports `data/ ist aktuell`.

## Rules that are easy to break

1. **Word IDs are user data.** A word's ID is `"<german meaning, lowercased>:<bosnian>"`
   and the app stores learning progress under it. Changing the German `de` of
   an existing word silently resets that word for every learner. Fix
   translations in `uebersetzungen.py` instead, or call out the reset in the PR.
2. **Bosnian is never translated.** Only meanings are translated. `bs`, sentence
   `text` and story `text` are identical in every language (a test enforces it).
3. **Ijekavian Bosnian**, Latin script, spelling after Halilović's *Pravopis
   bosanskoga jezika*: *mlijeko, lijep, vrijeme*, *kahva*. Do not "correct" to
   Ekavian or Croatian standard forms. Regional variants that families use
   (*kahva/kafa*, *babo/otac*, *hiljada/tisuća*) are deliberate.
4. **A native speaker has the last word.** `WORTSCHATZ_KORREKTUREN.md` overrides
   any dictionary, model or research. Never revert an entry listed there.
5. **Placeholders and HTML must survive translation.** `{anbieter}`, `{n}`, `<b>`,
   `<br>` must appear in every language exactly as in German. Tests check this.
6. **No network at runtime.** The app loads no fonts, scripts or analytics from
   other servers. Do not add CDNs. Third-party files go into `web/` with an
   entry in `web/LIZENZEN.txt` and `REUSE.toml`.
7. **Patch scripts are all-or-nothing.** The `*_richten.py` pattern: dry run by
   default, `--schreiben` to write, abort without changes if an anchor is not
   found exactly once. Follow the same pattern for new ones.
8. **No secrets.** `tts_zugang.json`, `mail_zugang.json`, keystores and anything
   with learner data are gitignored. Never create, print or commit them.

## Style

- Identifiers, comments and maintainer docs are **German**; user-facing
  repository docs (README, CONTRIBUTING, SECURITY) are English. Match the file.
- Comments explain **why**, often with the date and the bug that caused them.
  Keep that habit; do not strip existing comments.
- Python 3.9+, standard library only for anything the app or the build uses.
- Commit messages: short German or English summary line describing the effect
  for the learner, not the mechanics.

## Reviewing a pull request

Look first for: changed word IDs (rule 1), translated Bosnian (rule 2), lost
placeholders or tags (rule 5), new network access (rule 6), and generated
files edited by hand. Then check that the language of a correction is
plausible and that `data/` was regenerated.
