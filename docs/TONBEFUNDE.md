# Befunde an der Tonspur

Aus dem Prüfdurchlauf P3 am 25./26.09.2026. Ajdin hat Wörter aus mehreren
Abschnitten angehört.

---

## Die systematische Hörprobe vom 26.09.2026

Nach den ersten Einzelbefunden hat `ton_auffaellig.py` alle 1502 Aufnahmen
nach zwei Risikoformen durchsucht, und Ajdin hat beide Gruppen über
`web/_probe/aussprache.html` durchgehört.

| Gruppe | geprüft | falsch |
|---|---|---|
| kurz mit stimmhaftem Endlaut (das `sud`-Muster) | 19 | **9** |
| silbisches `r` (kein Vokal daneben) | 26 | **4** |
| zusammen | 45 | 13 |

Einer der 13 ist kein Tonfehler, sondern eine Vokabelfrage (siehe unten).
Bleiben **zwölf Aufnahmen**, und sie fallen in vier Muster:

**Vokal wird gedehnt, der kurz sein muss — sechs Fälle**

| Wort | Datei | Notiz |
|---|---|---|
| bez (ohne) | `w0533.mp3` | das e wird zu lang gezogen |
| kad (als/wenn) | `w0453.mp3` | das a wird zu lang gezogen, es muss kurz sein |
| kod (bei) | `w0532.mp3` | das o ist zu lang, muss kurz sein |
| kroz (durch) | `w0543.mp3` | o muss kurz, nicht lang |
| od (von) | `w0528.mp3` | das o muss kurz, nicht lang |
| zbog (wegen) | `w0524.mp3` | o zu lang **und** g verschluckt |

**Endkonsonant `g` verschluckt — drei Fälle**

| Wort | Datei | Notiz |
|---|---|---|
| dug (Schulden) | `w1009.mp3` | das g wird verschluckt, man hört es nicht |
| zbog (wegen) | `w0524.mp3` | das g muss betont werden |
| prtljag (Gepäck) | `w0832.mp3` | das g wird wieder verschluckt |

**Silbisches `r` zu schnell oder zu schwach — drei Fälle**

| Wort | Datei | Notiz |
|---|---|---|
| brz (schnell) | `w0758.mp3` | das r hört man zu wenig, muss mehr betont werden |
| crkva (Kirche) | `w0854.mp3` | zu schnell — es heißt `cr`, kurze Pause, `kva` |
| crna (schwarz) | `w0070.mp3` | wird auch zu schnell gesprochen |

**Falscher Laut — ein Fall**

| Wort | Datei | Notiz |
|---|---|---|
| sud (Gericht) | `w0984.mp3` | die Stimme sagt `sub` statt `sud` |

Alle zwölf sind mit `bs-BA-GoranNeural` erzeugt. Das Muster deutet auf
eine Eigenheit der Stimme hin: Ein alleinstehendes einsilbiges Wort wird
offenbar als betont behandelt und gedehnt, und der Endkonsonant fällt
dabei weg. `ton_bauen.py` setzt SSML bereits ein (`<prosody rate='-10%'>`
für den Langsam-Modus), der Hebel dafür ist also vorhanden.

### Keine Aussprachefrage: „Gute Besserung"

`w0242.mp3` trägt heute **Brzo ozdravi!** — das ist die Du-Form des
Imperativs („werde schnell gesund"). Ajdin am 26.09.2026: „nimm statt das
nimm brz oporavak".

Nachgeschlagen: `oporavak` ist ein maskulines Substantiv und heißt
Genesung (Wiktionary, Aussprache /opǒraʋak/). `brz oporavak` ist damit
grammatisch stimmig und entspricht als Nominalphrase dem deutschen „Gute
Besserung", während die bisherige Form nur die Du-Anrede abdeckt.

Zu ändern sind: `vokabeln.py:335`, danach `inhalt_bauen.py`, und die
Aufnahme muss neu erzeugt werden — der Text ist der Schlüssel, `w0242.mp3`
wird dabei zur Karteileiche.

### Wie gesucht wurde

`ton_auffaellig.py` meldet 48 Aufnahmen als gefährdet. Die zweite
Risikoform kam erst auf Ajdins Hinweis dazu: „das wird wahrscheinlich auch
bei vrt prt smrt usw auch so sein". Die ursprüngliche Suche kannte nur das
`sud`-Muster, und Wörter mit silbischem `r` haben oft gar keinen Vokal —
sie fielen komplett durch. `smrt`, `vrt`, `krv`, `trg` und `vrh` stehen
übrigens gar nicht im Wortschatz, `prst` und `prvi` dagegen schon.

---

## Prüfliste vom 01.10.2026

Ajdin hat über die Prüfliste angehört und entschieden:

| Wort | Datei | Ergebnis |
|---|---|---|
| **sud** (Gericht) | `w0984.mp3` | klingt jetzt richtig (seit 26.09. kroatische Stimme mit Lautschrift) |
| **nju / je** | `w0496.mp3` | falsch: „er sagt inju, es muss nju sein, und das andere Wort ist je“ |
| **skup / skupa** (teuer) | `w0755.mp3` | falsch: „er sagt skop und nicht skup“ |
| **drug / drugarica** (Kumpel) | `w2014.mp3` | falsch: „er sagt dru nicht drug“ – das g fällt wieder weg |

**Mehrere Formen:** Entscheidung „alle Formen sprechen“. Heute spricht
`sprechtext()` in `ton_bauen.py` nur die erste Form, und `audioDatei()` in
`index.html` sucht die Aufnahme ebenfalls nur über die erste Form. Für beide
Formen ändern sich also Erzeugung und Schlüssel; betroffen sind 107 Einträge
(Stand 01.10.2026). Neue Aufnahmen kosten Azure-Guthaben – erst nach Ajdins
Freigabe.

### Erledigt am 01.10.2026 (Prüfliste, Runden 2 und 3)

- **Alle Formen:** 107 neue Aufnahmen mit allen Formen hintereinander
  („moj, moja, moje“), eigener Schlüssel = ganzer Text (`schluessel_alle()`
  in `ton_bauen.py`, `audioDatei()` in `index.html` sucht ihn zuerst). Die
  Aufnahme der ersten Form bleibt für das angetippte Wort in Geschichten.
  Ajdin hat alle angehört, keine beanstandet.
- **nju** (`w0496.mp3`) und **drug** (`w2014.mp3`): kroatische Stimme mit
  Lautschrift. „nju, je“ und „drug, drugarica“ bleiben bei Goran.
- **skup** (`w0755.mp3`): kroatische Stimme mit langem u, Lautschrift von
  Hand („skuːp“, Feld `ipa` in `ton_ausnahmen.json`). Der Eintrag in Level 42
  heißt jetzt „skup / skupa / skupo = teuer (m/w/s)“ – „skup“ allein ist
  auch das Treffen, „skupa“ auch „zusammen“. „skup, skupa, skupo“ bleibt bei
  Goran.
- Fassungen erzeugt mit `ton_varianten2.py`, alles in `web/audio/_probe/`.

## Nachzusprechen

Beide Aufnahmen sind vorhanden und werden gefunden. Beanstandet ist, wie sie
klingen. Eine selbst eingesprochene Datei sticht die erzeugte sofort aus:
einfach über die vorhandene Datei schreiben, der Name bleibt.

| Wort | Datei | Beanstandung |
|---|---|---|
| **sud** (Gericht) | `web/audio/w0984.mp3` | Der Sprecher sagt **sub** statt *sud*. |
| **nju** | `web/audio/w0496.mp3` | „hört sich sehr komisch an" |

Beide sind mit `bs-BA-GoranNeural` erzeugt.

**Zu *nju* kommt etwas dazu:** In der Wortliste steht `nju / je`, gesprochen
wird aber nur *nju*. Das ist so gewollt — `ton_bauen.py` nimmt in
`sprechtext()` ausdrücklich nur die erste Variante —, aber wer zwei Formen
sieht und eine hört, hält es für einen Fehler. Dasselbe betrifft 72 von 1502
Aufnahmen, darunter `moj / moja / moje` und `velik / velika / veliko`.

Ob das bleiben soll, ist eine Entscheidung: Entweder die zweite Form wird
mitgesprochen, oder die Liste zeigt bei Mehrfachformen an, dass nur die
erste zu hören ist. Beides ist Arbeit; nichts zu tun ist vertretbar.

---

## Geprüft und in Ordnung

- **Alle 1502 Aufnahmen sind vorhanden.** `ton_pruefen.py` meldet
  1502 im Index, 1502 aus dem Inhalt erwartet, 19,7 MB.
- **Alle 1668 Vokabeln finden ihre Aufnahme.** Gegen die Schlüsselregel aus
  `index.html` geprüft (`text.split(' / ')[0]`, ohne Satzzeichen am Ende,
  kleingeschrieben): null Fehlschläge.
- **Es wird wirklich nur die erste Variante gesprochen.** Nachgewiesen über
  die Dateigrößen: `moj / moja / moje` ist 11.232 Bytes groß, genauso wie
  `Da`. Bei drei gesprochenen Formen wäre die Datei dreifach so lang.
  Schnitt der 72 Dateien mit Trennzeichen: 11.898 Bytes, Schnitt der kurzen
  ohne: 11.755 Bytes.

---

## Kein Fehler: der fehlende Lautsprecher

Gemeldet für Level 15 (*Molim te*), 38 und 39. Das ist Absicht.

In `wortzeilen()` steht `const kann = known.has(w.id)`, und die Wortliste
zeigt den Lautsprecher nur, wenn `kann` wahr ist. Wörter, die noch nicht
gelernt sind, stehen als `?` da — ohne Lautsprecher, weil er die Aussprache
verraten würde, bevor das Wort dran war.

In der laufenden App nachgestellt:

| | `kann` | Lautsprecher |
|---|---|---|
| Wort nicht gelernt | `false` | nein |
| Wort gelernt | `true` | ja |

`audioDatei('Molim te')` liefert dabei in beiden Fällen `w0331.mp3`. Die
Aufnahme ist also da, sie wird nur nicht angeboten.
