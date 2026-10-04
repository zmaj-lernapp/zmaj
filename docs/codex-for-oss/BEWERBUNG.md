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
| Ich interessiere mich für | alle drei: ChatGPT Pro mit Codex, Codex Security, API-Credits (Codex Security öffnet das Pflichtfeld unten) |
| OpenAI-Organisations-ID | https://platform.openai.com/settings/organization/general → `org-…` |

## Rolle (Primary oder Core Maintainer?)

<!-- feld: rolle -->
Primary maintainer and sole author. I write the code, curate the Bosnian content together with a native speaker whose corrections are final, write the tests, review every change, cut the releases and ship the Android app on Google Play. I am the admin of the repository.
<!-- ende -->

## Wodurch qualifiziert sich dieses Repository? (max. 500)

<!-- feld: qualifikation -->
Duolingo, Babbel, Busuu and Rosetta Stone offer no Bosnian course. Zmaj fills that gap for the diaspora: 1,728 words, 300 sentences, 12 stories and 16 grammar lessons, audio for every item, 8 interface languages. Offline Android app (AGPL 3.0) plus an open dataset (CC BY SA 4.0) as JSON, CSV, Anki and a TMX parallel corpus for low resource NLP. Two releases, CI with browser tests, CodeQL, Scorecard, REUSE. Demo: zmaj-lernapp.github.io/zmaj
<!-- ende -->

## Warum braucht dein Projekt Codex Security? (max. 500)

Pflichtfeld, sobald Codex Security angekreuzt ist. Belege: `import_richten.py`
(Fund und Fix), `KONTEN_AN = false` in `web/index.html`, AdMob und `ZmajAbo`
in `docs/ARCHITECTURE.md`. Im Formular darf am Ende noch
„, which I cannot do alone“ stehen (dann 491 Zeichen).

<!-- feld: security -->
Zmaj runs offline on learners' phones and keeps months of progress there, so one bug can lock a learner out. A first review found exactly that: a crafted backup file crashed the app on every start, with no way back to the settings. The fix is ready and tested. Still unreviewed in depth: the account code, which stays switched off until it is audited, and the bridge to the ads consent dialog and the Play subscription. Codex Security would check every change there.
<!-- ende -->

## Wie wirst du API-Credits für dein Projekt nutzen? (max. 500)

<!-- feld: api -->
Already wired into the repo, waiting for a key: 1) Codex reviews every PR against AGENTS.md (word IDs are learner data, Bosnian is never machine translated). 2) Codex triages language corrections: finds every affected entry, checks the native speaker log, proposes a patch. Next: 3) translation QA across 8 languages before each release, 4) drafting new levels and a Cyrillic edition for native review, 5) release notes.
<!-- ende -->

## Gibt es sonst noch etwas? (max. 500)

<!-- feld: sonstiges -->
Zmaj is a solo project, so every hour Codex saves on maintenance goes into new content. Every exercise stays free, and the course and dataset stay open for other apps, teachers and researchers. Next on the roadmap: more levels and a Cyrillic edition, each checked by a native speaker before it ships.
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
