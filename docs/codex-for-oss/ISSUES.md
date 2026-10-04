# Issue-Entwürfe: Übersetzungen prüfen lassen

Je Sprache ein Issue zum Kopieren (Titel, Labels, Text). Erzeugt aus
`data/vocabulary.json` am 04.10.2026; die Zahlen stimmen mit dem Datensatz.
Anlegen erst **nach** dem Merge nach `master`, sonst zeigen die Links ins Leere.

Labels für alle: `help wanted`, `good first issue`, `translation`,
`needs-native-speaker`.

Warum diese Issues zuerst: Sie sind klein teilbar (eine Sektion reicht), für
Nicht-Programmierer machbar, und jede übernommene Korrektur zählt in
PLAN.md §5 doppelt – als externe Mitwirkende und als Sprachkorrektur.

---

## English

**Titel:** `Review the English translations`

**Text:**

````markdown
**Native English speaker? Help learners of Bosnian.**

Zmaj teaches Bosnian, and every word, sentence and story is translated into English. The English version was machine-translated from German and checked by AI, but **no native speaker of English has read it yet**. That is what this issue is for.

**How to help (15 minutes is enough for one section):**

1. Open [`data/vocabulary.csv`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/vocabulary.csv) (GitHub shows it as a table). The column `en` is the English meaning of the Bosnian word in column `bs`.
2. Pick a section below and comment "I take section N" so nobody does it twice.
3. Note anything wrong, unnatural or inconsistent and post it here, or open a [language correction](https://github.com/zmaj-lernapp/zmaj/issues/new?template=language_correction.yml) per finding. A list like `Level 3: "brown" → "brown (masc.)"` is perfect.

You do not need to know Bosnian: you check whether the English reads naturally and means the same as the German column `de`. No git, no code.

**Sections**

- [ ] Section 1 · Basics & everyday life – levels 1–15, 341 words, 65 sentences
- [ ] Section 2 · Things you can touch – levels 16–19, 114 words, 20 sentences
- [ ] Section 3 · Animals & nature – levels 20–23, 109 words, 20 sentences
- [ ] Section 4 · At home – levels 24–28, 137 words, 25 sentences
- [ ] Section 5 · Building sentences – levels 29–50, 618 words, 98 sentences
- [ ] Section 6 · Shopping & eating out – levels 51–54, 108 words, 20 sentences
- [ ] Section 7 · Bosnia & origins – levels 55–57, 81 words, 15 sentences
- [ ] Section 8 · People & culture – levels 58–59, 58 words, 10 sentences
- [ ] Section 9 · Offices & contracts – levels 60–65, 162 words, 27 sentences
- [ ] Stories – [`data/stories.json`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/stories.json), key `translations.en`

Thank you! Contributors are credited in the release notes.
````

---

## Turkish

**Titel:** `Review the Turkish translations (Türkçe)`

**Text:**

````markdown
**Anadiliniz Türkçe mi? Boşnakça öğrenenlere yardım edin.**

Zmaj teaches Bosnian, and every word, sentence and story is translated into Turkish. The Turkish version was machine-translated from German and checked by AI, but **no native speaker of Turkish has read it yet**. That is what this issue is for.

**How to help (15 minutes is enough for one section):**

1. Open [`data/vocabulary.csv`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/vocabulary.csv) (GitHub shows it as a table). The column `tr` is the Turkish meaning of the Bosnian word in column `bs`.
2. Pick a section below and comment "I take section N" so nobody does it twice.
3. Note anything wrong, unnatural or inconsistent and post it here, or open a [language correction](https://github.com/zmaj-lernapp/zmaj/issues/new?template=language_correction.yml) per finding. A list like `Level 3: "brown" → "brown (masc.)"` is perfect.

You do not need to know Bosnian: you check whether the Turkish reads naturally and means the same as the German column `de`. No git, no code.

**Sections**

- [ ] Section 1 · Basics & everyday life – levels 1–15, 341 words, 65 sentences
- [ ] Section 2 · Things you can touch – levels 16–19, 114 words, 20 sentences
- [ ] Section 3 · Animals & nature – levels 20–23, 109 words, 20 sentences
- [ ] Section 4 · At home – levels 24–28, 137 words, 25 sentences
- [ ] Section 5 · Building sentences – levels 29–50, 618 words, 98 sentences
- [ ] Section 6 · Shopping & eating out – levels 51–54, 108 words, 20 sentences
- [ ] Section 7 · Bosnia & origins – levels 55–57, 81 words, 15 sentences
- [ ] Section 8 · People & culture – levels 58–59, 58 words, 10 sentences
- [ ] Section 9 · Offices & contracts – levels 60–65, 162 words, 27 sentences
- [ ] Stories – [`data/stories.json`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/stories.json), key `translations.tr`

Thank you! Contributors are credited in the release notes.
````

---

## Swedish

**Titel:** `Review the Swedish translations (Svenska)`

**Text:**

````markdown
**Har du svenska som modersmål? Hjälp den som lär sig bosniska.**

Zmaj teaches Bosnian, and every word, sentence and story is translated into Swedish. The Swedish version was machine-translated from German and checked by AI, but **no native speaker of Swedish has read it yet**. That is what this issue is for.

**How to help (15 minutes is enough for one section):**

1. Open [`data/vocabulary.csv`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/vocabulary.csv) (GitHub shows it as a table). The column `sv` is the Swedish meaning of the Bosnian word in column `bs`.
2. Pick a section below and comment "I take section N" so nobody does it twice.
3. Note anything wrong, unnatural or inconsistent and post it here, or open a [language correction](https://github.com/zmaj-lernapp/zmaj/issues/new?template=language_correction.yml) per finding. A list like `Level 3: "brown" → "brown (masc.)"` is perfect.

You do not need to know Bosnian: you check whether the Swedish reads naturally and means the same as the German column `de`. No git, no code.

**Sections**

- [ ] Section 1 · Basics & everyday life – levels 1–15, 341 words, 65 sentences
- [ ] Section 2 · Things you can touch – levels 16–19, 114 words, 20 sentences
- [ ] Section 3 · Animals & nature – levels 20–23, 109 words, 20 sentences
- [ ] Section 4 · At home – levels 24–28, 137 words, 25 sentences
- [ ] Section 5 · Building sentences – levels 29–50, 618 words, 98 sentences
- [ ] Section 6 · Shopping & eating out – levels 51–54, 108 words, 20 sentences
- [ ] Section 7 · Bosnia & origins – levels 55–57, 81 words, 15 sentences
- [ ] Section 8 · People & culture – levels 58–59, 58 words, 10 sentences
- [ ] Section 9 · Offices & contracts – levels 60–65, 162 words, 27 sentences
- [ ] Stories – [`data/stories.json`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/stories.json), key `translations.sv`

Thank you! Contributors are credited in the release notes.
````

---

## Dutch

**Titel:** `Review the Dutch translations (Nederlands)`

**Text:**

````markdown
**Is Nederlands je moedertaal? Help mensen die Bosnisch leren.**

Zmaj teaches Bosnian, and every word, sentence and story is translated into Dutch. The Dutch version was machine-translated from German and checked by AI, but **no native speaker of Dutch has read it yet**. That is what this issue is for.

**How to help (15 minutes is enough for one section):**

1. Open [`data/vocabulary.csv`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/vocabulary.csv) (GitHub shows it as a table). The column `nl` is the Dutch meaning of the Bosnian word in column `bs`.
2. Pick a section below and comment "I take section N" so nobody does it twice.
3. Note anything wrong, unnatural or inconsistent and post it here, or open a [language correction](https://github.com/zmaj-lernapp/zmaj/issues/new?template=language_correction.yml) per finding. A list like `Level 3: "brown" → "brown (masc.)"` is perfect.

You do not need to know Bosnian: you check whether the Dutch reads naturally and means the same as the German column `de`. No git, no code.

**Sections**

- [ ] Section 1 · Basics & everyday life – levels 1–15, 341 words, 65 sentences
- [ ] Section 2 · Things you can touch – levels 16–19, 114 words, 20 sentences
- [ ] Section 3 · Animals & nature – levels 20–23, 109 words, 20 sentences
- [ ] Section 4 · At home – levels 24–28, 137 words, 25 sentences
- [ ] Section 5 · Building sentences – levels 29–50, 618 words, 98 sentences
- [ ] Section 6 · Shopping & eating out – levels 51–54, 108 words, 20 sentences
- [ ] Section 7 · Bosnia & origins – levels 55–57, 81 words, 15 sentences
- [ ] Section 8 · People & culture – levels 58–59, 58 words, 10 sentences
- [ ] Section 9 · Offices & contracts – levels 60–65, 162 words, 27 sentences
- [ ] Stories – [`data/stories.json`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/stories.json), key `translations.nl`

Thank you! Contributors are credited in the release notes.
````

---

## Norwegian Bokmål

**Titel:** `Review the Norwegian Bokmål translations (Norsk bokmål)`

**Text:**

````markdown
**Har du norsk som morsmål? Hjelp dem som lærer bosnisk.**

Zmaj teaches Bosnian, and every word, sentence and story is translated into Norwegian Bokmål. The Norwegian Bokmål version was machine-translated from German and checked by AI, but **no native speaker of Norwegian Bokmål has read it yet**. That is what this issue is for.

**How to help (15 minutes is enough for one section):**

1. Open [`data/vocabulary.csv`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/vocabulary.csv) (GitHub shows it as a table). The column `nb` is the Norwegian Bokmål meaning of the Bosnian word in column `bs`.
2. Pick a section below and comment "I take section N" so nobody does it twice.
3. Note anything wrong, unnatural or inconsistent and post it here, or open a [language correction](https://github.com/zmaj-lernapp/zmaj/issues/new?template=language_correction.yml) per finding. A list like `Level 3: "brown" → "brown (masc.)"` is perfect.

You do not need to know Bosnian: you check whether the Norwegian Bokmål reads naturally and means the same as the German column `de`. No git, no code.

**Sections**

- [ ] Section 1 · Basics & everyday life – levels 1–15, 341 words, 65 sentences
- [ ] Section 2 · Things you can touch – levels 16–19, 114 words, 20 sentences
- [ ] Section 3 · Animals & nature – levels 20–23, 109 words, 20 sentences
- [ ] Section 4 · At home – levels 24–28, 137 words, 25 sentences
- [ ] Section 5 · Building sentences – levels 29–50, 618 words, 98 sentences
- [ ] Section 6 · Shopping & eating out – levels 51–54, 108 words, 20 sentences
- [ ] Section 7 · Bosnia & origins – levels 55–57, 81 words, 15 sentences
- [ ] Section 8 · People & culture – levels 58–59, 58 words, 10 sentences
- [ ] Section 9 · Offices & contracts – levels 60–65, 162 words, 27 sentences
- [ ] Stories – [`data/stories.json`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/stories.json), key `translations.nb`

Thank you! Contributors are credited in the release notes.
````

---

## Danish

**Titel:** `Review the Danish translations (Dansk)`

**Text:**

````markdown
**Har du dansk som modersmål? Hjælp dem, der lærer bosnisk.**

Zmaj teaches Bosnian, and every word, sentence and story is translated into Danish. The Danish version was machine-translated from German and checked by AI, but **no native speaker of Danish has read it yet**. That is what this issue is for.

**How to help (15 minutes is enough for one section):**

1. Open [`data/vocabulary.csv`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/vocabulary.csv) (GitHub shows it as a table). The column `da` is the Danish meaning of the Bosnian word in column `bs`.
2. Pick a section below and comment "I take section N" so nobody does it twice.
3. Note anything wrong, unnatural or inconsistent and post it here, or open a [language correction](https://github.com/zmaj-lernapp/zmaj/issues/new?template=language_correction.yml) per finding. A list like `Level 3: "brown" → "brown (masc.)"` is perfect.

You do not need to know Bosnian: you check whether the Danish reads naturally and means the same as the German column `de`. No git, no code.

**Sections**

- [ ] Section 1 · Basics & everyday life – levels 1–15, 341 words, 65 sentences
- [ ] Section 2 · Things you can touch – levels 16–19, 114 words, 20 sentences
- [ ] Section 3 · Animals & nature – levels 20–23, 109 words, 20 sentences
- [ ] Section 4 · At home – levels 24–28, 137 words, 25 sentences
- [ ] Section 5 · Building sentences – levels 29–50, 618 words, 98 sentences
- [ ] Section 6 · Shopping & eating out – levels 51–54, 108 words, 20 sentences
- [ ] Section 7 · Bosnia & origins – levels 55–57, 81 words, 15 sentences
- [ ] Section 8 · People & culture – levels 58–59, 58 words, 10 sentences
- [ ] Section 9 · Offices & contracts – levels 60–65, 162 words, 27 sentences
- [ ] Stories – [`data/stories.json`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/stories.json), key `translations.da`

Thank you! Contributors are credited in the release notes.
````

---

## French

**Titel:** `Review the French translations (Français)`

**Text:**

````markdown
**Le français est ta langue maternelle ? Aide ceux qui apprennent le bosnien.**

Zmaj teaches Bosnian, and every word, sentence and story is translated into French. The French version was machine-translated from German and checked by AI, but **no native speaker of French has read it yet**. That is what this issue is for.

**How to help (15 minutes is enough for one section):**

1. Open [`data/vocabulary.csv`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/vocabulary.csv) (GitHub shows it as a table). The column `fr` is the French meaning of the Bosnian word in column `bs`.
2. Pick a section below and comment "I take section N" so nobody does it twice.
3. Note anything wrong, unnatural or inconsistent and post it here, or open a [language correction](https://github.com/zmaj-lernapp/zmaj/issues/new?template=language_correction.yml) per finding. A list like `Level 3: "brown" → "brown (masc.)"` is perfect.

You do not need to know Bosnian: you check whether the French reads naturally and means the same as the German column `de`. No git, no code.

**Sections**

- [ ] Section 1 · Basics & everyday life – levels 1–15, 341 words, 65 sentences
- [ ] Section 2 · Things you can touch – levels 16–19, 114 words, 20 sentences
- [ ] Section 3 · Animals & nature – levels 20–23, 109 words, 20 sentences
- [ ] Section 4 · At home – levels 24–28, 137 words, 25 sentences
- [ ] Section 5 · Building sentences – levels 29–50, 618 words, 98 sentences
- [ ] Section 6 · Shopping & eating out – levels 51–54, 108 words, 20 sentences
- [ ] Section 7 · Bosnia & origins – levels 55–57, 81 words, 15 sentences
- [ ] Section 8 · People & culture – levels 58–59, 58 words, 10 sentences
- [ ] Section 9 · Offices & contracts – levels 60–65, 162 words, 27 sentences
- [ ] Stories – [`data/stories.json`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/stories.json), key `translations.fr`

Thank you! Contributors are credited in the release notes.
````

---

## Bosnisch: zweite Meinung

**Titel:** `Second opinion on the Bosnian (izvorni govornici, javite se!)`

**Text:**

````markdown
**Govorite bosanski kao maternji jezik? Pomozite!**

Zmaj teaches Ijekavian Bosnian as spoken in Bosnia, following Halilović's
*Pravopis bosanskoga jezika*. One native speaker has reviewed every word
(corrections logged in `WORTSCHATZ_KORREKTUREN.md`). A second pair of ears
from another region would make it much better: words that sound unnatural,
forms used only in one city, a better everyday phrase.

Open [`data/vocabulary.csv`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/vocabulary.csv)
(column `bs`) or [`data/sentences.csv`](https://github.com/zmaj-lernapp/zmaj/blob/master/data/sentences.csv),
pick a section, and post what you would say differently and where you are
from. Regional variants are welcome; we keep the ones families really use.

Hvala!
````
