# zmaj-lernapp.github.io

Die öffentlichen Seiten zur App **Zmaj – Bosnisch lernen**: Impressum,
Datenschutzerklärung, Nutzungsbedingungen. Google Play verlangt, dass diese
Texte ohne Anmeldung im Netz stehen.

---

## Die Seiten zum Anschauen

**Hier klicken, nicht auf die Dateien darüber.** In der Dateiliste zeigt
GitHub den HTML-Quelltext; lesbar sind die Seiten nur unter ihrer
Internetadresse:

- **[Startseite](https://zmaj-lernapp.github.io/)**
- **[Datenschutzerklärung](https://zmaj-lernapp.github.io/datenschutz.html)**
- **[Impressum](https://zmaj-lernapp.github.io/impressum.html)**
- **[Nutzungsbedingungen](https://zmaj-lernapp.github.io/nutzungsbedingungen.html)**
- **[Daten löschen](https://zmaj-lernapp.github.io/konto-loeschen.html)**

Jede Seite gibt es in acht Sprachen — die Knöpfe stehen oben auf der Seite.

---

## Warum hier Quelltext steht und dort nicht

GitHub hat zwei Aufgaben, die leicht durcheinandergehen:

| | |
|---|---|
| **github.com/…** | der Lagerraum. Zeigt, was in den Dateien steht. |
| **zmaj-lernapp.github.io** | die Auslage. Zeigt, was der Besucher sieht. |

Bei Markdown-Dateien wie dieser hier gibt es oben die Schalter *Preview* und
*Code*. **Bei HTML-Dateien gibt es das nicht** — sie werden immer als
Quelltext angezeigt. Das ist keine Einstellung, die man umlegen kann.

---

## Was hier liegt

| Datei | Wofür |
|---|---|
| `index.html` | Startseite mit den Links |
| `datenschutz.html` | Datenschutzerklärung, acht Sprachen |
| `nutzungsbedingungen.html` | Nutzungsbedingungen, acht Sprachen |
| `impressum.html` | Impressum nach § 5 DDG, acht Sprachen |
| `konto-loeschen.html` | wie man seine Daten löscht — fragt Google im Data-Safety-Formular ab |
| `app-ads.txt` | eine Zeile, die AdMob bestätigt, dass die Werbeplätze in der App wirklich zu diesem Konto gehören |

---

## Geändert wird nicht hier

Die HTML-Dateien sind **erzeugt**. Wer hier etwas von Hand ändert, verliert
es beim nächsten Mal.

Die Texte stehen im Projektordner in `sprachen.py`. Nach einer Änderung dort
`seite_bauen.py` laufen lassen (in Thonny öffnen, **F5**) und die Dateien
neu hochladen. Wie das geht, steht in `github-seite/LIESMICH.txt` — die
Datei bleibt auf dem Rechner und wird nicht mit hochgeladen.
