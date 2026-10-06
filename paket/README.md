# zmaj-bosnian

The open Bosnian course behind the [Zmaj](https://github.com/zmaj-lernapp/zmaj)
app as a Python package: 1,728 words and phrases in 65 levels, 300 cloze
sentences, 12 graded stories with glossary and questions, 16 grammar lessons,
406 glossary entries. Bosnian (Ijekavian, Latin script) with translations
into German, English, Turkish, Swedish, Dutch, Norwegian Bokmål, Danish and
French. No dependencies.

```bash
pip install zmaj-bosnian
```

```python
import zmaj_bosnian as zmaj

for w in zmaj.vocabulary()[:3]:
    print(w["bs"], "→", w["translations"]["en"])
# Merhaba → Hello
# Dobar dan → Good day
# Dobro jutro → Good morning

zmaj.sentences()[0]["cloze"]          # 'Dobar ___'
zmaj.levels()[0]["label"]["de"]       # 'Grundlagen'
zmaj.counts()["words"]                # 1728
```

The same public data is available offline from the command line:

```bash
python -m zmaj_bosnian word
python -m zmaj_bosnian word --lang de
python -m zmaj_bosnian search kuća --lang en
python -m zmaj_bosnian stats
```

`word` prints one random Bosnian word and its meaning. `search` matches
Bosnian words or meanings without regard to case, including Bosnian letters,
and prints every match in course order. Both default to English (`en`);
`--lang` accepts `de`, `en`, `tr`, `sv`, `nl`, `nb`, `da` and `fr`.
`stats` prints the counts returned by `counts()`. No network or extra
dependencies are needed.

Audio files are not in the package (37 MB); every entry has an `audio` path
into the [repository](https://github.com/zmaj-lernapp/zmaj/tree/master/web/audio)
and the dataset zip of each [release](https://github.com/zmaj-lernapp/zmaj/releases).
The audio is synthetic (Microsoft Azure Neural TTS) and must not be used to
train speech synthesis or other speech or voice models, because Microsoft's
terms for that output do not allow it; the store version of the Zmaj app uses
other word and sentence recordings, which are not part of this dataset.

How the data was made, what native speakers reviewed and what they did not:
[DATASHEET](https://github.com/zmaj-lernapp/zmaj/blob/master/data/DATASHEET.md).

**License:** CC BY-SA 4.0. **Attribution:** *Zmaj – Bosnian learning content,
© 2026 Ajdin Hasic, CC BY-SA 4.0, https://github.com/zmaj-lernapp/zmaj*
