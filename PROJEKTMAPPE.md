# Projektmappe Zmaj

**Zmaj – Bosnisch lernen**
Eine Android-Anwendung von der Idee bis zur Veröffentlichung

Ajdin Hasić · Klasse 02FSA · Fachrichtung Automatisierungstechnik
Berufs- und Technikerschule Butzbach · Betreuung: Herr Dr. Rosenschon
Bearbeitungszeitraum: 10.08.2026 – 19.03.2027

> **Arbeitsstand (21.09.2026):** Kapitel 1 ist fertig und liegt als
> Word-Datei vor (`mappe/Zmaj Kapitel 1.docx`, 5 Seiten). Das Thema hat
> Herr Dr. Rosenschon gutgeheißen. Als Nächstes Kapitel 2, das Lastenheft.
>
> **Wo `[…]` steht, fehlt eine Angabe, die nur Ajdin kennt.**

---

## Gliederung

Zu jedem Kapitel steht, woraus es sich belegen lässt.

| | Kapitel | Quelle im Projekt |
|---|---|---|
| 1 | Vorstellung des Projekts und des Verfassers | — |
| 2 | Lastenheft | |
| 2.1 | Einführung in das Projekt | `STORE_TEXTE.md` |
| 2.2 | Ist-Zustand | Marktrecherche |
| 2.3 | Soll-Zustand | `ANLEITUNG.md` |
| 2.4 | Technische Anforderungen | `capacitor.config.json`, `build.gradle` |
| 3 | Konzeptfindung | Git-Historie, Entscheidungsnotizen |
| 4 | Risikoanalyse | `WERBUNG_PRUEFUNG.md` |
| 5 | Projektdurchführung | |
| 5.1 | Umsetzung des Projekts | Git-Historie |
| 5.2 | Aufbau der Anwendung | `web/index.html`, `sprachen.py` |
| 5.3 | Datenhaltung und Ablauflogik | Lernstand, Leben, Wiederholung |
| 5.4 | Veröffentlichung im Play Store | `PRODUKTIONSZUGRIFF.md` |
| 5.5 | Probleme und Lösungsansätze | Git-Historie, Fehlerberichte |
| 5.6 | Controlling und Projektverlauf | Git-Historie mit Datumsangaben |
| 5.7 | Inbetriebnahme und Funktionstest | geschlossener Test, 12 Tester |
| 6 | Anhang | Quelltextauszüge, Screenshots, Belege |

**Warum das trägt:** Die Mappe muss nicht rückblickend erfunden werden. Seit
dem **19.09.2026** steht jeder Arbeitsschritt mit Datum, geänderten Dateien
und Begründung in der Versionsverwaltung — derzeit 27 Einträge. Jede
Fehlersuche ist protokolliert, und der geschlossene Test liefert eine echte
Inbetriebnahme mit zwölf Anwendern statt einer Schreibtischprobe.

> **Achtung, Lücke:** Der Bearbeitungszeitraum beginnt am 10.08.2026, die
> Versionsverwaltung erst am 19.09.2026. Die Dateien selbst sind älter — die
> ersten stammen vom 13.09.2026 —, aber für August und die erste
> Septemberhälfte gibt es kein Schritt-für-Schritt-Protokoll. In Kapitel 5.6
> (Controlling) muss deshalb entweder anders belegt werden, was in dieser
> Zeit geschah, oder es wird offen gesagt. Nicht behaupten, die
> Rückverfolgbarkeit sei lückenlos.

---

## 1. Vorstellung des Projekts und des Verfassers

*287 Wörter. Wie hier geschrieben wird, steht in* `mappe/SCHREIBREGELN.md`.

### 1.1 Der Verfasser

Diese Arbeit wird als Einzelarbeit durchgeführt. Verfasser ist Ajdin Hasić, gelernter Elektroniker, Klasse 02FSA. Die Weiterbildung zum staatlich geprüften Techniker der Fachrichtung Automatisierungstechnik findet in Vollzeit an der Berufs- und Technikerschule Butzbach statt. Die Betreuung übernimmt Herr Dr. Rosenschon. Der Bearbeitungszeitraum reicht vom 10.08.2026 bis zum 19.03.2027.

Aus der Ausbildung liegen Kenntnisse in Elektrotechnik und Steuerungstechnik vor. Die Kenntnisse in der Anwendungsentwicklung wurden selbstständig erarbeitet und in eigenen Projekten angewendet.

Alle Aufgaben liegen in einer Hand: Anforderungsanalyse, Konzeption, Entwicklung, Test, Veröffentlichung und Dokumentation. Die getroffenen Entscheidungen werden in den folgenden Kapiteln begründet.

### 1.2 Das Projekt

Gegenstand der Arbeit ist Zmaj, eine Android-Anwendung zum Erlernen der bosnischen Sprache. Zmaj ist das bosnische Wort für Drache.

Den Anstoß gab ein privater Bedarf. Für Bosnisch war kein brauchbares Lernmaterial zu finden. Die großen Anbieter für Sprachlernsoftware führen die Sprache nicht. Verfügbar sind im Wesentlichen Vokabellisten ohne Grammatik, ohne Tonspur und ohne aufeinander aufbauende Abschnitte.

Die Anwendung richtet sich an Erwachsene mit persönlichem Bezug zu Bosnien und Herzegowina: an Partnerinnen und Partner in deutsch-bosnischen Beziehungen, an angeheiratete Familienangehörige und an Nachkommen der zweiten und dritten Einwanderergeneration, die Bosnisch verstehen, es aber nie lesen und schreiben gelernt haben. Der Schwerpunkt liegt in Deutschland. Die Bedienoberfläche gibt es zusätzlich in sieben weiteren Sprachen, weil die bosnische Diaspora vor allem in diesen Ländern lebt.

Der Lernstoff führt vom Alltag bis zum Arbeitsvertrag. Geübt wird in fünf Formen: hören, schreiben, auswählen, Lücken füllen und sprechen. Zu jeder Vokabel gehört eine bosnische Tonspur.

Die Anwendung ist fertiggestellt und im Google Play Store veröffentlicht. Sie arbeitet vollständig auf dem Gerät, ohne Nutzerkonto und ohne Server. Der Lernstand verlässt das Telefon nicht. Der vollständige Funktionsumfang und die Anforderungen sind im Lastenheft in Kapitel 2 beschrieben.
---

> **Als Word-Datei:** `mappe/Zmaj Kapitel 1.docx`, erzeugt aus
> `mappe/kapitel1.json`. Wie das geht, steht in `mappe/LIESMICH.txt`.
