# Bewerbung: Codex for Open Source

Formular: https://openai.com/form/codex-for-oss/ · Bedingungen:
https://developers.openai.com/codex/codex-for-oss-terms

Die Antworten sind **auf Englisch** (die Prüfer lesen Englisch, das Formular
nimmt beides). Jeder Block zwischen `<!-- feld: … -->` und `<!-- ende -->`
wird von `tests/test_bewerbung.py` gezählt: höchstens **470 Zeichen**, damit
nach dem Einsetzen echter Zahlen noch Luft bis zur Grenze von 500 bleibt.

**Vor dem Absenden ausfüllen:** alles in `[eckigen Klammern]` mit den Zahlen
vom Tag (Quellen in PLAN.md, Abschnitt „Messen“). Nichts schätzen, nichts
aufrunden – eine Zahl, die der Prüfer nachzählt und nicht findet, kostet mehr
als eine kleine Zahl.

---

## Feste Felder

| Feld | Eintrag |
|---|---|
| Vorname | Ajdin |
| Nachname | Hasic |
| E-Mail | die Adresse des ChatGPT-Kontos, das Pro bekommen soll |
| GitHub-Benutzername | `zmaj-lernapp` (Profil auf öffentlich stellen, Name und Bild eintragen) |
| GitHub-Repository-URL | https://github.com/zmaj-lernapp/zmaj |
| Ich interessiere mich für | alle drei: ChatGPT Pro mit Codex, Codex Security, API-Credits |
| OpenAI-Organisations-ID | https://platform.openai.com/settings/organization/general → `org-…` |

## Rolle (Primary oder Core Maintainer?)

<!-- feld: rolle -->
Primary maintainer and sole author since the first commit: I write the code, the Bosnian content (as a native speaker) and the tests, review every change, cut releases and publish the Android app on Google Play. Admin of the repository.
<!-- ende -->

## Wodurch qualifiziert sich dieses Repository? (max. 500)

<!-- feld: qualifikation -->
Duolingo, Babbel, Busuu, Rosetta Stone and Lingoda teach no Bosnian. Zmaj fills that gap for the diaspora: an open course (1,728 words, 300 sentences, 12 stories, 16 grammar lessons, audio for every item, 8 languages) as an offline Android app (AGPL) and a CC BY-SA dataset (JSON/CSV/Anki) for low-resource NLP. [N] Play installs, [N] stars, [N] dataset downloads. CI, CodeQL, Scorecard, REUSE. Demo: zmaj-lernapp.github.io/zmaj
<!-- ende -->

## Wie wirst du API-Credits für dein Projekt nutzen? (max. 500)

<!-- feld: api -->
Already wired in the repo: 1) Codex reviews every PR against AGENTS.md (word IDs are learner data; Bosnian is never machine-translated). 2) Codex triages language-correction issues: finds every affected entry, checks the native-speaker log, proposes a patch. Next: 3) translation QA across 8 languages before each release; 4) drafting new levels and a Cyrillic edition for native review; 5) release notes.
<!-- ende -->

## Gibt es sonst noch etwas? (max. 500)

<!-- feld: sonstiges -->
I built Zmaj for my wife, because I could not find anything for Bosnian beyond vocabulary lists. As a one-person project, Codex directly multiplies my time for content over maintenance. A first security review found a crafted backup that locks the app on every start (fix ready); Codex Security would cover the Android shell and billing the same way. Every exercise stays free.
<!-- ende -->

---

## Fassung für „Claude for Open Source“ (Anthropic)

Die harten Schwellen (500 abhängige Repos, 200 000 Downloads im Monat,
20 externe Mitwirkende …) erfüllt Zmaj heute nicht. Das Formular sagt
ausdrücklich: *Don't quite fit? … apply anyway and tell us about it.* Dann so:

<!-- feld: claude_reichweite -->
The open Bosnian course the big apps lack: Duolingo, Babbel, Busuu and Rosetta Stone teach no Bosnian, Croatian or Serbian. Zmaj ships 1,728 words, 300 sentences, 12 stories and 16 grammar lessons with audio for every item in 8 languages, as an offline app (AGPL) and a CC BY-SA dataset for apps, classrooms and low-resource NLP. [N] Play installs, [N] stars, [N] dataset downloads.
<!-- ende -->

<!-- feld: claude_nutzung -->
Maintenance of a one-person project: reviewing content PRs against the rules in AGENTS.md, triaging language corrections from native speakers, translation QA across eight languages, and the next content: more levels and a Cyrillic edition, each reviewed by a native speaker before release.
<!-- ende -->
