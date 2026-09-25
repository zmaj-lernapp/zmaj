# Befunde an der Tonspur

Aus dem Prüfdurchlauf P3 am 25./26.09.2026. Ajdin hat Wörter aus mehreren
Abschnitten angehört.

---

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
- **Alle 1108 Vokabeln finden ihre Aufnahme.** Gegen die Schlüsselregel aus
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
