# Projektmappe Zmaj

Technikerarbeit von Ajdin Hasić · Abgabe bis **19.03.2027**
(letzter Schultag vor den hessischen Osterferien, 22.03.–02.04.2027)

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

**Warum das trägt:** Die Mappe muss nicht rückblickend erfunden werden. Jeder
Arbeitsschritt seit dem 13.09.2026 steht mit Datum und Begründung in der
Versionsverwaltung, jede Fehlersuche ist protokolliert, und der geschlossene
Test liefert eine echte Inbetriebnahme mit zwölf Anwendern statt einer
Schreibtischprobe.

---

## 1. Vorstellung des Projekts und des Verfassers

*Entwurf — bitte gegenlesen und die Lücken füllen.*

### Der Verfasser

Diese Arbeit wurde als Einzelprojekt durchgeführt. Verfasser ist Ajdin
Hasić, gelernter Elektroniker, derzeit in Vollzeit-Weiterbildung zum
staatlich geprüften Techniker der Fachrichtung […] an der […].

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

*Noch zu ergänzen:* […] Fachrichtung, Schule, Klasse, betreuende Lehrkraft,
Zeitraum der Projektarbeit laut Schule.
