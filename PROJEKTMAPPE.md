# Projektmappe Zmaj

**Zmaj – Bosnisch lernen**
Eine Android-Anwendung von der Idee bis zur Veröffentlichung

Ajdin Hasić · Klasse 02FSA · Fachrichtung Automatisierungstechnik
Berufs- und Technikerschule Butzbach · Betreuung: Herr Dr. Rosenschon
Bearbeitungszeitraum: 10.08.2026 – 19.03.2027

> **Arbeitsstand:** Kapitel 1 im Entwurf. Alles Weitere folgt Kapitel für
> Kapitel. Am Ende wird daraus ein Word-Dokument im Layout der
> Smartgrow-Mappe.
>
> **Wo `[…]` steht, fehlt eine Angabe, die nur Ajdin kennt.**

---

## Gliederung

Übernommen aus der Smartgrow-Mappe vom 12.05.2026, angepasst auf ein
Softwareprojekt. Was dort Hardware-Aufbau und Spannungsversorgung war, wird
hier Aufbau der Anwendung und Veröffentlichung.

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

*Entwurf — bitte gegenlesen und die Lücken füllen.*

### Der Verfasser

Diese Arbeit wurde als Einzelprojekt durchgeführt. Verfasser ist Ajdin
Hasić, gelernter Elektroniker, derzeit in Vollzeit-Weiterbildung zum
staatlich geprüften Techniker der Fachrichtung Automatisierungstechnik an
der Berufs- und Technikerschule Butzbach, Klasse 02FSA. Die Arbeit wird von
Herrn Dr. Rosenschon betreut und umfasst den Zeitraum vom Schuljahresbeginn
am 10.08.2026 bis zum 19.03.2027, dem letzten Schultag vor den hessischen
Osterferien.

Anders als bei der vorangegangenen Projektarbeit *Smartgrow – Automatisiertes
Gewächszelt*, die im Dreierteam entstand, liegen hier sämtliche Rollen in
einer Hand: Anforderungsanalyse, Konzeption, Entwicklung, Test, Recht und
Veröffentlichung. Diese Bündelung ist eine bewusste Entscheidung und zugleich
die größte Herausforderung des Projekts — sie ist in der Risikoanalyse
(Kapitel 4) gesondert bewertet.

### Das Projekt

**Zmaj** ist eine Android-Anwendung zum Erlernen der bosnischen Sprache.
*Zmaj* ist das bosnische Wort für Drache; das Maskottchen der App ist ein
blauer Drache auf einem Bücherstapel.

Den Anstoß gab ein konkreter, privater Bedarf: Die Ehefrau des Verfassers
wollte Bosnisch lernen, fand dafür aber kein brauchbares Lernmaterial. Die
großen Sprachlernanbieter führen Bosnisch nicht im Programm; verfügbar sind
im Wesentlichen Vokabellisten ohne Grammatik, ohne Tonspur und ohne
strukturierten Aufbau. Aus dieser Lücke entstand die Aufgabenstellung.

Der fachliche Reiz liegt darin, dass das Projekt über die reine
Programmierung deutlich hinausgeht. Um die Anwendung tatsächlich in den
Google Play Store zu bringen, waren unter anderem erforderlich:

- ein angemeldetes Gewerbe (Gewerbeanzeige vom 13.09.2026, bescheinigt am
  21.09.2026 durch die Gemeinde Wettenberg),
- eine Identitätsprüfung durch Google sowie ein Zahlungsprofil,
- ein Impressum und eine Datenschutzerklärung nach DDG und DSGVO in allen
  acht Sprachen der Anwendung,
- eine Einwilligungslösung nach den europäischen Vorgaben für Werbung,
- ein geschlossener Test mit mindestens zwölf Testern über vierzehn Tage,
  den Google seit 2023 für neue Entwicklerkonten verlangt.

Das Projekt bildet damit nicht nur einen Entwicklungsvorgang ab, sondern den
vollständigen Weg von der Idee bis zum verkaufsfähigen Produkt.

### Abgrenzung

Die Anwendung ist kein Prototyp und kein Studienobjekt, sondern ein
tatsächlich veröffentlichtes Produkt mit zahlenden Nutzern
(Abonnement-Vollversion) und Werbefinanzierung. Sie wird über die Abgabe
dieser Arbeit hinaus weitergepflegt.

### 1.4 Bezug zur Fachrichtung Automatisierungstechnik

Eine Sprachlernanwendung ist auf den ersten Blick kein Gegenstand der Automatisierungstechnik. Der Einwand sei deshalb vorweggenommen, bevor er entsteht.

**Was diese Arbeit nicht enthält:** keine Sensorik, keine Antriebe, keine speicherprogrammierbare Steuerung, keinen Feldbus und keinen physikalischen Prozess. Es gibt keine Messgrößen in physikalischen Einheiten und folglich auch keine Regelstrecke, die sich mit einer Übertragungsfunktion beschreiben ließe.

Der Bezug liegt nicht im Gegenstand, sondern in den Entwurfsfragen. Beim Entwurf einer Ablaufsteuerung sind stets dieselben fünf Fragen zu beantworten, gleich ob die Anlage ein Ofen, ein Förderband oder ein Lernablauf ist:

- Welche Zustände gibt es? – Der Lernablauf ist als Zustandsfolge umgesetzt: Aufgabe stellen, Antwort erfassen, bewerten, Folgezustand bestimmen.
- Wodurch wird weitergeschaltet? – Die Übergangsbedingungen ergeben sich aus der Antwort des Anwenders und aus dem bisherigen Lernstand.
- Was ist verriegelt? – Fünf Fehlversuche sperren den Zugang; die Sperre lässt sich weder umgehen noch durch Neustart der Anwendung aufheben.
- Welche Zeiten werden überwacht? – Ein Zeitglied gibt die Sperre nach zwei Stunden schrittweise wieder frei. Ein Tageszähler begrenzt die Werbeeinblendungen und wird um Mitternacht zurückgesetzt.
- Welche Störgrößen greifen ein? – Netzausfall, eingehender Anruf, Wechsel in den Hintergrund und das Beenden der Anwendung während eines laufenden Vorgangs. Jeder dieser Fälle ist als definierter Ablauf behandelt.

Diese fünf Fragen sind am Projekt konkret zu beantworten und nachprüfbar. Die Werkzeuge sind andere als im Schaltschrank; die Entwurfsfragen sind dieselben.

**Rückkopplung im Lernverfahren.** Die Wiederholung der Vokabeln arbeitet rückgekoppelt: Die Antwortgenauigkeit des Anwenders bestimmt den Abstand bis zur nächsten Abfrage. Richtige Antworten vergrößern ihn, falsche verkürzen ihn. Dass es sich dabei nicht um eine nachträgliche Umdeutung handelt, zeigt die Fachliteratur: Tabibian u. a. formulieren die Planung von Wiederholungen in den Proceedings of the National Academy of Sciences ausdrücklich als Problem der Optimalsteuerung und prüfen ihr Ergebnis an Daten eines Sprachlernanbieters. Bewusst nicht behauptet wird, es handle sich um einen Regelkreis im Sinne der Regelungstechnik: Die Strecke ist ein Mensch, eine Sprungantwort ist nicht reproduzierbar, und ein Stabilitätsnachweis ist nicht möglich.

**Abnahme durch eine externe Instanz.** Die Inbetriebnahme erfolgte nicht am Schreibtisch. Zwölf Anwender haben die Anwendung über vierzehn Tage auf ihren eigenen Geräten benutzt. Die Freigabe erteilt Google nach einem Regelwerk, das der Verfasser nicht beeinflussen kann und dessen Verletzung zur Sperrung des Entwicklerkontos führt. Damit steht am Ende keine Selbstzertifizierung, sondern die Abnahme durch eine unabhängige Stelle.

Sollte ein engerer Bezug zur Fachrichtung gewünscht sein, lässt sich die Arbeit ohne Themenwechsel erweitern: um eine Zustandsübergangstabelle des Lernablaufs mit vollständigem Testnachweis je Übergang, um eine Fehlermöglichkeits- und Einflussanalyse der Ablauflogik mit Risikoprioritätszahlen, sowie um eine Verifikationsmatrix, die jede Anforderung des Lastenhefts mit Prüfmethode, Sollwert, Istwert und Prüfdatum belegt. Das Material dafür liegt vor; es wäre in die Prüfform zu bringen.

---

> **Als Word-Datei:** `mappe/Zmaj Kapitel 1.docx`, erzeugt aus
> `mappe/kapitel1.json`. Wie das geht, steht in `mappe/LIESMICH.txt`.
