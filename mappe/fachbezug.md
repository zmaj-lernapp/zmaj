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
