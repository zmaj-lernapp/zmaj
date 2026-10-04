---
pretty_name: "Zmaj: open Bosnian course"
license: cc-by-sa-4.0
language:
  - bs
  - de
  - en
  - tr
  - sv
  - nl
  - nb
  - da
  - fr
multilinguality: multilingual
size_categories:
  - 1K<n<10K
task_categories:
  - translation
  - text-to-speech
tags:
  - bosnian
  - language-learning
  - low-resource
  - vocabulary
  - cloze
  - graded-reader
  - anki
  - heritage-language
configs:
  - config_name: vocabulary
    data_files: vocabulary.csv
    default: true
  - config_name: sentences
    data_files: sentences.csv
  - config_name: parallel
    data_files: parallel.jsonl
---

# Zmaj: open Bosnian course

**1,728 words and phrases, 300 cloze sentences, 12 graded stories, 406
glossary entries and 16 grammar lessons in Bosnian (Ijekavian, Latin
script), each translated into German, English, Turkish, Swedish, Dutch,
Norwegian Bokmål, Danish and French**, with a synthetic Bosnian audio file for
every word, sentence and story.

This is the complete content of [Zmaj](https://github.com/zmaj-lernapp/zmaj),
an offline app for learning Bosnian. It is exported from the app's sources by
`daten_exportieren.py`; CI fails when the two disagree.

| File | Content |
|---|---|
| `vocabulary.csv` / `.json` | words with level, section, 8 translations, audio path |
| `sentences.csv` / `.json` | cloze sentence, answer, full sentence, 8 translations, audio path |
| `stories.json` | story text, translations, glossary, comprehension questions |
| `glossary.json` | reading glossary |
| `grammar.json` | grammar lessons per language |
| `anki/zmaj-bs-<lang>.tsv` | Anki decks, tagged by level |
| `parallel/bs-<lang>.tsv` | Bosnian–X pairs (words, then sentences) for machine translation |
| `parallel.jsonl` / `.tmx` | every word, sentence and story with all translations; TMX 1.4b |
| `manifest.json` | counts and SHA-256 of every file |
| `schema/` | JSON Schemas |

Audio paths point to `web/audio/` in the GitHub repository; the dataset zip
attached to each [GitHub release](https://github.com/zmaj-lernapp/zmaj/releases)
contains the MP3 files.

```python
from datasets import load_dataset
ds = load_dataset("csv", data_files="vocabulary.csv")["train"]
print(ds[0]["bs"], ds[0]["en"])   # Merhaba Hello

pairs = load_dataset("csv", data_files="parallel/bs-en.tsv", sep="\t",
                     quoting=3)["train"]   # 3 = csv.QUOTE_NONE
```

How the data was made, what has been reviewed by native speakers and what has
not, and its limitations: **[DATASHEET.md](DATASHEET.md)**.

**License:** CC BY-SA 4.0. **Attribution:** *Zmaj – Bosnian learning content,
© 2026 Ajdin Hasic, CC BY-SA 4.0, https://github.com/zmaj-lernapp/zmaj*.
The audio is synthetic (Azure Neural TTS); say so when you republish it.
**DOI:** [10.5281/zenodo.23146609](https://doi.org/10.5281/zenodo.23146609) (all versions, Zenodo).
