
## Summe nach Art

  FALSCHE BEDEUTUNG            35
  unnatürlich                  34
  uneinheitlich                29
  nachgetragen                 20
  Grammatik/Rechtschreibung    13
  veraltet                     7
  Zeichensetzung               3
# Übersetzungen der Zmaj-App – Prüfbericht

Stand 18.09.2026. Je Sprache ein Prüfer, der jeden Text gegen das Deutsche gelesen hat,
und ein zweiter, der die Funde zu widerlegen versuchte. Aufgeführt ist nur, was die
Gegenprüfung bestätigt hat (bzw. bei nl/nb/sv, wo sie am Limit scheiterte, was der
Prüfer als sicher markiert hat).

ACHTUNG: Das ist eine gründliche KI-Prüfung, kein Muttersprachler. Vor der
Veröffentlichung gehört je Sprache jemand drüber, der sie wirklich spricht.


==============================================================================
## Englisch   (26 Funde, Gegenprüfung: ja)
==============================================================================

Die englische Fassung ist insgesamt gut: flüssig, freundlich, konsequent geduzt, und die Kernbegriffe level, lesson, streak, streak freeze, coins, full version, Shop und Learning path werden durchgehend gleich benutzt. Bedeutungsfehler bei Doppeldeutigkeiten (Bank, Gericht, See, Rock, Bad, Überweisung) habe ich keine gefunden; die Grammatik-Erklärungen sind sinnvoll ans Englische angepasst („Deutsch“ → „English“ als Tabellenkopf, „anders als im Deutschen“ → „just as in English“). Echte Schwächen sind wenige wörtlich-deutsche Formulierungen („From {p} % the level test is unlocked“, „How much is the price?“, „How high is the interest?“), ein Bedeutungsfehler („I beg your pardon“ für „Ich bitte um Entschuldigung“), zwei Stellen mit „life“ statt „hearts“ bei der Werbebelohnung sowie eine Mischung aus britischer Schreibung in der Oberfläche (personalised, cancelled, postcode) und amerikanischer im Lernstoff (color, center, license, practiced). Platzhalter und Einzahl|Mehrzahl-Trennung stimmen in allen 341 Oberflächenschlüsseln mit dem Deutschen überein, deutsche Reste gibt es keine. Insgesamt klingt es wie eine echte englischsprachige Lern-App. Bei unsicheren Vokabeln habe ich statt im Netz das bosnische Ausgangswort in vokabeln.py nachgesehen (20 Einträge), was mehrere Verdachtsfälle entkräftet hat (z.B. „Svejedno mi je“ → „I do not mind“ ist richtig).


--- FALSCHE BEDEUTUNG (4) ---

  uebersetzungen.py "Ich bitte um Entschuldigung", Zeile 1607   [mittel]
    deutsch : Ich bitte um Entschuldigung
    jetzt   : I beg your pardon
    besser  : I apologize
    warum   : „I beg your pardon“ bedeutet heute fast nur „Wie bitte?“ oder drückt Empörung aus. Bosnisch „Molim za izvinjenje“ ist eine echte Entschuldigung.

  uebersetzungen.py "Notaufnahme / Notarzt", Zeile 1747   [mittel]
    deutsch : Notaufnahme / Notarzt
    jetzt   : emergency service
    besser  : emergency room / ambulance service
    warum   : Bosnisch „hitni prijem / hitna pomoć“ sind zwei Dinge (Notaufnahme und Rettungsdienst); „emergency service“ ist vage und deckt die Notaufnahme nicht ab.

  sprachen.py mail.bestaetigen_betreff, Zeile 751   [gering]
    deutsch : Willkommen bei Zmaj – bitte bestätige deine Adresse
    jetzt   : Welcome to Zmaj – one more click
    besser  : Welcome to Zmaj – please confirm your address
    warum   : Der Betreff sagt im Englischen nicht, worum es geht (Adresse bestätigen); der deutsche Inhalt fehlt.

  uebersetzungen.py "Ich wasche mich", Zeile 1332   [gering]
    deutsch : Ich wasche mich
    jetzt   : I am washing
    besser  : I wash myself
    warum   : Ohne „myself“ fehlt gerade das Reflexive, das in diesem Level (se) gelernt wird; „I am washing“ meint, dass man etwas wäscht.

--- Grammatik/Rechtschreibung (1) ---

  sprachen.py set.stimme_aufnahmen, Zeile 687   [gering]
    deutsch : 1 eigene Aufnahme|{n} eigene Aufnahmen
    jetzt   : 1 own recording|{n} own recordings
    besser  : 1 recording of your own|{n} recordings of your own
    warum   : „own“ steht im Englischen nicht allein vor dem Substantiv („1 own recording“ ist ungrammatisch); es braucht „your own“.

--- veraltet (1) ---

  sprachen.py set.datenschutz_text, Zeile 804 (Abschnitt 5)   [gering]
    deutsch : Du kannst jede Sprechaufgabe überspringen – tippe auf „Kann jetzt nicht sprechen“.
    jetzt   : You can skip any speaking exercise – there is a separate button for that.
    besser  : You can skip any speaking exercise – tap “Speaking is not possible right now, skip”.
    warum   : Der deutsche Text nennt eine Schaltfläche, die englische Fassung nicht. Hinweis: Der deutsche Knopfname „Kann jetzt nicht sprechen“ existiert auch im Deutschen nicht mehr (task.sprechen_skip heißt „Sprechen ist gerade nicht möglich, überspringen“) – das Deutsche ist hier selbst veraltet.

--- uneinheitlich (6) ---

  sprachen.py werbung.lohn_laeuft, Zeile 813   [mittel]
    deutsch : Nach dem Video bekommst du ein Leben.
    jetzt   : You get a life after the video.
    besser  : You get a heart after the video.
    warum   : „Leben“ heißt in der gesamten englischen Oberfläche „hearts“ (leben.*, lektion.*, stat.leben); hier plötzlich „life“.

  sprachen.py werbung.lohn_abholen, Zeile 814   [mittel]
    deutsch : ♥ Leben abholen
    jetzt   : ♥ Collect life
    besser  : ♥ Collect heart
    warum   : Gleiche Inkonsistenz: überall sonst „heart(s)“, hier „life“.

  sprachen.py quest.aufgaben, Zeile 501   [gering]
    deutsch : {n} Aufgabe beantworten|{n} Aufgaben beantworten
    jetzt   : Do {n} exercise|Do {n} exercises
    besser  : Do {n} task|Do {n} tasks
    warum   : „Aufgabe“ heißt sonst überall „task“ (task.tippen_weiter, lektion.uebersprungen, quest.fertig); hier „exercise“.

  sprachen.py set.datenschutz_text, Zeile 804 (Abschnitt 8)   [gering]
    deutsch : Du kannst Auskunft über deine Daten verlangen, sie berichtigen oder löschen lassen, die Verarbeitung einschränken und ihr widersprechen.
    jetzt   : You can ask what data we hold about you, have it corrected, deleted or transferred, restrict its processing and object to it.
    besser  : You can ask what data we hold about you, have it corrected or deleted, restrict its processing and object to it.
    warum   : „or transferred“ (Datenübertragbarkeit) steht nicht im deutschen Text; die beiden Fassungen sagen rechtlich Unterschiedliches.

  sprachen.py set.werbung_pers, Zeile 761   [gering]
    deutsch : Personalisierte Werbung
    jetzt   : Personalised ads
    besser  : Personalized ads
    warum   : Britische Schreibung, während der gesamte Lernstoff amerikanisch schreibt (color, center, license, neighbor, traveling) und die Oberfläche selbst „practiced“ und „neighboring“ verwendet. Ebenso „cancelled“ (2x in set.agb_text) und „Postcode“ (set.anbieter). Eine Variante wählen.

  uebersetzungen.py "Ich möchte ein Haus kaufen", Zeile 1712   [gering]
    deutsch : Ich möchte ein Haus kaufen
    jetzt   : I want to buy a house
    besser  : I would like to buy a house
    warum   : Derselbe Satz mit Punkt (Zeile 1863) heißt „I would like to buy a house.“, und „Ich möchte (m/w)“ ist als „I would like“ gelernt. Auch „Ich möchte reisen / lernen / etwas essen“ (Zeilen 1295, 1316, 1321) sind mit „I want“ übersetzt – uneinheitlich.

--- unnatürlich (13) ---

  sprachen.py level.test_gesperrt, Zeile 594   [mittel]
    deutsch : 🔒 Level-Test ab {p} %
    jetzt   : 🔒 Level test from {p} %
    besser  : 🔒 Level test unlocks at {p} %
    warum   : „from {p} %“ ist das deutsche „ab“ wörtlich übertragen; im Englischen sagt man „unlocks at“ / „at {p} %“.

  sprachen.py level.test_marke, Zeile 596   [mittel]
    deutsch : Ab {p} % ist der Level-Test frei
    jetzt   : From {p} % the level test is unlocked
    besser  : The level test unlocks at {p} %
    warum   : Wörtlich-deutsche Satzstellung mit „From … %“; kein Muttersprachler formuliert so.

  sprachen.py level.note_zu, Zeile 599   [gering]
    deutsch : Jede Lektion füllt den Balken. Ab {p} % wird der Level-Test freigeschaltet. Erst der bestandene Test öffnet das nächste Level.
    jetzt   : Every lesson fills the bar. From {p} % the level test unlocks. Only a passed test opens the next level.
    besser  : Every lesson fills the bar. At {p} % the level test unlocks. Only a passed test opens the next level.
    warum   : Dasselbe „From {p} %“ für „ab“.

  uebersetzungen.py "Wie hoch ist der Preis?", Zeile 1816   [mittel]
    deutsch : Wie hoch ist der Preis?
    jetzt   : How much is the price?
    besser  : What is the price?
    warum   : „How much is the price?“ ist Denglisch; man fragt „What is the price?“ oder „How much is it?“.

  uebersetzungen.py "Wie hoch sind die Zinsen?", Zeile 1681   [mittel]
    deutsch : Wie hoch sind die Zinsen?
    jetzt   : How high is the interest?
    besser  : What is the interest rate?
    warum   : „How high is the interest?“ sagt niemand; üblich ist „What is the interest rate?“.

  sprachen.py konto.regel_klein, Zeile 744   [gering]
    deutsch : Kleinbuchstabe
    jetzt   : small letter
    besser  : lowercase letter
    warum   : Der Fachbegriff für Passwortregeln ist „lowercase letter“; „small letter“ klingt nach Kindersprache.

  sprachen.py konto.fehler_klein, Zeile 748   [gering]
    deutsch : Es fehlt ein Kleinbuchstabe.
    jetzt   : A small letter is missing.
    besser  : A lowercase letter is missing.
    warum   : Siehe konto.regel_klein.

  sprachen.py task.was_heisst, Zeile 611   [gering]
    deutsch : Was heißt auf Bosnisch …
    jetzt   : How do you say it in Bosnian …
    besser  : What is the Bosnian for …
    warum   : Nach den Punkten folgt das Wort; „How do you say it in Bosnian … [Wort]“ ergibt mit dem vorgezogenen „it“ keinen Satz.

  sprachen.py hero.serie_sub, Zeile 547   [gering]
    deutsch : Heute noch nicht geübt.
    jetzt   : Nothing practiced today.
    besser  : No practice yet today.
    warum   : Das „noch“ fehlt; „Nothing practiced today“ klingt nach Tagesende statt nach Aufforderung.

  sprachen.py set.toene_sub, Zeile 678   [gering]
    deutsch : Richtig- und Falsch-Ton, Fanfare am Ende.
    jetzt   : Right and wrong sound, fanfare at the end.
    besser  : Sounds for right and wrong answers, a fanfare at the end.
    warum   : „Right and wrong sound“ liest sich als „richtiger und falscher Klang“; die Bindestrich-Konstruktion aus dem Deutschen trägt nicht.

  uebersetzungen.py "Was gibt's? / Wie läuft's?", Zeile 934   [gering]
    deutsch : Was gibt's? / Wie läuft's?
    jetzt   : What is up? / How is it going?
    besser  : What's up? / How's it going?
    warum   : Der Smalltalk-Gruß existiert im Englischen nur in der Kurzform; „What is up?“ sagt niemand.

  uebersetzungen.py "Wer gehört dazu? Mit bosnischen Formen wie babo, nana, amidža.", Zeile 498   [gering]
    deutsch : Wer gehört dazu? Mit bosnischen Formen wie babo, nana, amidža.
    jetzt   : Who belongs to it? With Bosnian forms such as babo, nana, amidža.
    besser  : Who is part of the family? With Bosnian forms such as babo, nana, amidža.
    warum   : „Who belongs to it?“ ist wörtlich übersetzt und hat im Englischen keinen Bezug („it“).

  sprachen.py set.werbung_google, Zeile 762   [gering]
    deutsch : Einstellung bei Google
    jetzt   : Setting at Google
    besser  : Managed by Google
    warum   : „at Google“ klingt nach Ort/Firma („works at Google“); gemeint ist, dass Google die Einstellung speichert.

--- Zeichensetzung (1) ---

  sprachen.py set.agb_text, Zeile 802 und set.datenschutz_text, Zeile 804   [gering]
    deutsch : Stand: 16.09.2026
    jetzt   : Last updated: 16.09.2026
    besser  : Last updated: 16 September 2026
    warum   : Deutsches Datumsformat mit Punkten; im Englischen wird 16.09.2026 als 16. September gelesen, aber ungewohnt, und bei anderen Daten (z.B. 03.05.) mehrdeutig.

  NACHGETRAGEN: uebersetzungen.py Grammatik-Übungen, Zeilen 2171, 2173 (auch 2079 und 2269)
    jetzt   : “Idem sa ___.” / “Kahva sa ___.” / “sa, pod, iznad …” / “sa + instrumental: + om.”
    besser  : Bosnischen Aufgabentext unverändert lassen: “Idem s ___.”, “Kahva s ___.”, “s/sa, pod, …”, “s/sa + instrumental: + om.”
    warum   : Die englische Fassung ändert den bosnischen Übungstext (s → sa) gegenüber der deutschen. Wer die App auf Englisch nutzt, lernt in denselben Aufgaben eine andere Form als auf Deutsch; die Tabelle zeigt „sa“ allein, obwohl die Erklärung „s/sa“ lehrt. Kein Fehler im Englischen, aber eine Abweichung zwischen den Sprachfassungen.

  NACHGETRAGEN: uebersetzungen.py „als / wenn (zeitlich)“, Zeile 1088
    jetzt   : when (in time)
    besser  : when (time)
    warum   : „in time“ heißt „rechtzeitig“; der Klammerzusatz sagt damit etwas anderes als das deutsche „zeitlich“. Zeile 2063 übersetzt denselben Zusatz richtig mit „when (time)“.

  NACHGETRAGEN: uebersetzungen.py „Herr“, „Frau“, Zeilen 1597–1598
    jetzt   : Mr / Mrs
    besser  : Mr. / Mrs. (bei amerikanischer Schreibung) – oder britisch beibehalten und die Rechtschreibung insgesamt vereinheitlichen
    warum   : „Mr“ und „Mrs“ ohne Punkt sind britische Schreibweise; der Lernstoff schreibt sonst amerikanisch (color, center, license, check, cell phone, gas station). Gehört zur bereits gemeldeten US/UK-Mischung, war dort aber nicht aufgeführt.

  NACHGETRAGEN: sprachen.py set.datenschutz_text, Zeile 804 (Abschnitt 4)
    jetzt   : We use both only to reply and to fix the fault
    besser  : We use both only to reply and to fix the problem
    warum   : „fault“ bezeichnet im Englischen eine Schuld oder einen technischen Defekt; für eine Rückmeldung zur App ist „problem“ (oder „bug“) das natürliche Wort. Wörtlich-deutsche Wortwahl.
  uneinheitlicher Begriff: Leben -> hearts / heart (überall in der Oberfläche), life (werbung.lohn_laeuft, werbung.lohn_abholen)
  uneinheitlicher Begriff: Aufgabe -> task (task.*, lektion.uebersprungen, quest.fertig: Daily task), exercise (quest.aufgaben, quest.hoeren, quest.luecken: gap-fill, set.datenschutz_text: speaking exercises)
  uneinheitlicher Begriff: Rechtschreibung US/UK -> amerikanisch: color, center, license, neighbor, traveling, gray, mom, apartment, check (Lernstoff); practiced, neighboring (Oberfläche), britisch: Personalised, cancelled, Postcode, enquiries (Oberfläche, vor allem AGB/Datenschutz)
  uneinheitlicher Begriff: Ich möchte -> I would like (Ich möchte (m/w), Ich möchte drei Äpfel, Ich möchte ein Konto eröffnen, Ich möchte ein Haus kaufen.), I want (Ich möchte reisen, Ich möchte lernen, Ich möchte etwas essen, Ich möchte ein Haus kaufen)
  uneinheitlicher Begriff: Laden / Geschäft -> Shop (Oberfläche: laden.titel, tab.laden), shop (Vokabel „Laden“, Wörterbuch), store (Vokabel „Geschäft“)
  uneinheitlicher Begriff: Amtssprache -> Official language (Schwierigkeitsstufe), official language (gesch.summary), official language (Level-Tipp „Behördensprache“)
  uneinheitlicher Begriff: Level, Lektion, Serie, Serienschutz, Münzen, Vollversion, Lernpfad -> level, lesson, streak, streak freeze, coins, full version, learning path – alle durchgehend einheitlich, keine Abweichung gefunden

==============================================================================
## Türkisch   (14 Funde, Gegenprüfung: ja)
==============================================================================

Die türkische Fassung ist insgesamt gut: Die Oberflächentexte sind idiomatisch, knapp und duzen konsequent, die Kernbegriffe (seviye, ders, seri, jeton, tam sürüm, mağaza, can, öğrenme yolu) sind fast durchweg einheitlich, und AGB/Datenschutz sind vollständig und aktuell übersetzt. Der Lernstoff (rund 2200 Einträge) ist sauber, Vokabeln und Lückensätze stimmen bis auf wenige Ausnahmen mit dem Deutschen überein, die Grammatik-Erklärungen sind gut an türkische Leser angepasst. Echte Fehler sind wenige: "abbrechen" wird als "bitir" (beenden) wiedergegeben, "ab 5" wurde zu "größer als 5", "fahren" zu "sürmek" (lenken), "Mütze" zu "şapka", dazu die TDK-widrige Schreibung "% {p}" mit Leerzeichen und einige kleinere Unstimmigkeiten. Es klingt wie eine echte türkische Lern-App.


--- FALSCHE BEDEUTUNG (4) ---

  sprachen.py "lektion.abbrechen" Zeile 998 (ebenso "lektion.abbrechen_frage" 999, "test.abbrechen" 1019, "test.abbrechen_frage" 1020)   [mittel]
    deutsch : ✕ Lektion abbrechen / Lektion abbrechen? / ✕ Test abbrechen / Test abbrechen?
    jetzt   : ✕ Dersi bitir / Ders bitirilsin mi? / ✕ Testi bitir / Test bitirilsin mi?
    besser  : ✕ Dersten çık / Dersten çıkılsın mı? / ✕ Testten çık / Testten çıkılsın mı?
    warum   : "bitirmek" heißt "beenden, fertig machen". Der Nutzer könnte meinen, er schließe die Lektion erfolgreich ab. "Abbrechen" ist "çıkmak/vazgeçmek". Der Folgetext "Ders yarıda kaldı" (lektion.aus) zeigt, dass Abbruch gemeint ist.

  sprachen.py "set.agb_text" Zeile 1064, Abschnitt 6   [gering]
    deutsch : Sie dürfen nicht kopiert und als eigenes Angebot weiterverbreitet werden.
    jetzt   : Kopyalanıp kendi teklifin olarak yayılamaz.
    besser  : Kopyalanıp kendi ürünün gibi dağıtılamaz.
    warum   : "teklif" ist "Angebot" im Sinne von Vorschlag/Preisangebot. Gemeint ist ein eigenes Produkt/Dienst. Falsche Lesart des mehrdeutigen Wortes "Angebot".

  uebersetzungen.py "Mengen: nach Mengenwörtern und Zahlen ab 5 steht der Genitiv: ..." Zeile 4233-4234   [mittel]
    deutsch : Mengen: nach Mengenwörtern und Zahlen ab 5 steht der Genitiv: čaša vode, kilogram jabuka, mnogo ljudi, malo vremena, pet godina.
    jetzt   : Miktarlar: miktar bildiren kelimelerden ve 5'ten büyük sayılardan sonra genitif gelir: čaša vode, kilogram jabuka, mnogo ljudi, malo vremena, pet godina.
    besser  : Miktarlar: miktar bildiren kelimelerden ve 5 ve üzeri sayılardan sonra genitif gelir: čaša vode, kilogram jabuka, mnogo ljudi, malo vremena, pet godina.
    warum   : "5'ten büyük" heißt "größer als 5" und schließt die 5 aus – das Beispiel "pet godina" widerspricht dem direkt. Die Tabelle "5 und mehr" ist mit "5 ve üzeri" korrekt übersetzt.

  uebersetzungen.py "Mütze" Zeile 3159   [gering]
    deutsch : Mütze
    jetzt   : şapka
    besser  : bere
    warum   : "şapka" ist "Hut"; die Mütze (kapa) ist "bere". Die Oberfläche übersetzt laden.hut korrekt mit "Bere".

--- Grammatik/Rechtschreibung (1) ---

  uebersetzungen.py "sie kosten" Zeile 4819   [gering]
    deutsch : sie kosten
    jetzt   : tutuyorlar
    besser  : tutuyor
    warum   : Bei nicht-menschlichen Mehrzahl-Subjekten (Äpfel) steht das Verb im Türkischen im Singular: "Elmalar iki mark tutuyor", nicht "tutuyorlar".

--- veraltet (1) ---

  sprachen.py "set.datenschutz_text" Zeile 1066, Abschnitt 5   [gering]
    deutsch : Du kannst jede Sprechaufgabe überspringen – tippe auf „Kann jetzt nicht sprechen“.
    jetzt   : Her konuşma alıştırmasını atlayabilirsin – bunun için ayrı bir düğme var.
    besser  : Her konuşma alıştırmasını atlayabilirsin – “Şu an konuşmak mümkün değil, atla” düğmesine dokun.
    warum   : Das Deutsche nennt den Knopf, das Türkische nur "dafür gibt es einen eigenen Knopf". Der tatsächliche türkische Knopftext ist task.sprechen_skip.

--- uneinheitlich (5) ---

  sprachen.py "set.datenschutz_text" Zeile 1066, Abschnitt 8   [gering]
    deutsch : Du kannst Auskunft über deine Daten verlangen, sie berichtigen oder löschen lassen, die Verarbeitung einschränken und ihr widersprechen.
    jetzt   : Verilerin hakkında bilgi isteyebilir, verilerini düzelttirebilir, sildirebilir ya da taşınmasını isteyebilir, işlenmesini kısıtlatabilir ve işlenmesine itiraz edebilirsin.
    besser  : Verilerin hakkında bilgi isteyebilir, verilerini düzelttirebilir ya da sildirebilir, işlenmesini kısıtlatabilir ve işlenmesine itiraz edebilirsin.
    warum   : "taşınmasını isteyebilir" (Datenübertragbarkeit) steht nicht im deutschen Text – die Fassungen weichen inhaltlich voneinander ab.

  sprachen.py "mail.bestaetigen_betreff" Zeile 1118   [gering]
    deutsch : Willkommen bei Zmaj – bitte bestätige deine Adresse
    jetzt   : Zmaj'a hoş geldin – son bir adım
    besser  : Zmaj'a hoş geldin – lütfen adresini onayla
    warum   : Der zweite Teil sagt "noch ein letzter Schritt" statt "bitte bestätige deine Adresse"; der Betreff nennt so nicht, worum es geht.

  uebersetzungen.py "wohnen" Zeile 3207   [gering]
    deutsch : wohnen
    jetzt   : ikamet etmek
    besser  : oturmak / yaşamak
    warum   : "ikamet etmek" ist Amtssprache ("ansässig sein"). Überall sonst wird "oturmak" benutzt (ich wohne = oturuyorum, Wo wohnst du? = Nerede oturuyorsun?).

  uebersetzungen.py "Haus (Gen.)" Zeile 5011   [gering]
    deutsch : Haus (Gen.)
    jetzt   : ev (tamlayan)
    besser  : ev (genitif)
    warum   : Einziger Eintrag mit "tamlayan"; alle anderen Genitiv-Vermerke im Wörterbuch heißen "(genitif)".

  uebersetzungen.py "ich sollte (m/w)" Zeile 3585   [gering]
    deutsch : ich sollte (m/w)
    jetzt   : -meliyim (e/k)
    besser  : ich muss: -mem gerek / -meliyim; ich sollte: -sem iyi olur (tavsiye) (e/k)
    warum   : Identisch mit "ich muss" = "-meliyim" (Zeile 3576). Zwei verschiedene bosnische Formen (moram / trebao bih) bekommen dieselbe türkische Bedeutung und sind in der Aufgabe nicht mehr unterscheidbar.

--- unnatürlich (2) ---

  sprachen.py "set.sicherung_fehler" Zeile 884   [gering]
    deutsch : Das hat nicht geklappt.
    jetzt   : Bu işe yaramadı.
    besser  : Olmadı.
    warum   : "Bu işe yaramadı" heißt "Das hat nichts genützt / war nutzlos", nicht "hat nicht geklappt". An anderen Stellen (task.mikro_fehler, konto.fehler_allgemein) steht schon korrekt "Olmadı.".

  uebersetzungen.py "Zeugnis" Zeile 4009   [gering]
    deutsch : Zeugnis
    jetzt   : diploma belgesi
    besser  : karne / diploma
    warum   : "diploma belgesi" ist eine Doppelung und nicht der Begriff für Zeugnis; Schulzeugnis = karne, Arbeitszeugnis = bonservis/referans. Direkt darunter steht schon "Diplom" = "diploma".

--- Zeichensetzung (1) ---

  sprachen.py "level.test_gesperrt" Zeile 954, "level.test_marke" Zeile 956, "level.note_zu" Zeile 959   [gering]
    deutsch : 🔒 Level-Test ab {p} % / Ab {p} % ist der Level-Test frei / ... Ab {p} % wird der Level-Test freigeschaltet ...
    jetzt   : 🔒 Seviye testi % {p} sonra / % {p} sonra seviye testi açılır / ... % {p} sonra seviye testi açılır ...
    besser  : 🔒 Seviye testi %{p} sonra / %{p} sonra seviye testi açılır / Her ders çubuğu doldurur. %{p} sonra seviye testi açılır. Sonraki seviyeyi ancak geçilen bir test açar.
    warum   : Nach TDK steht das Prozentzeichen vor der Zahl und ohne Leerzeichen (%50). "% 50" ist ein verbreiteter Schreibfehler.

  NACHGETRAGEN: uebersetzungen.py "über / oberhalb" Zeile 3441 (Präpositionen), neben "auf (wo)" Zeile 3426
    jetzt   : "über / oberhalb": "üstünde" und "auf (wo)": "üstünde (nerede)"
    besser  : "über / oberhalb": "üzerinde / yukarısında"
    warum   : Zwei verschiedene bosnische Präpositionen (na, iznad) bekommen dieselbe türkische Bedeutung "üstünde"; in einer Aufgabe, die nach dem bosnischen Wort fragt, sind sie nicht unterscheidbar – gleiche Art von Fehler wie bei -meliyim. "yukarısında" gibt "oberhalb" eindeutig wieder.

  NACHGETRAGEN: sprachen.py "set.agb_text" Zeile 1064, Abschnitt 2
    jetzt   : "resmi daireler"
    besser  : "resmî daireler"
    warum   : TDK-Schreibung ist "resmî" mit Dach; überall sonst in der türkischen Fassung steht "resmî" (Sektion 3, Level-Tipp "Resmî daire", "Resmî dil"). Uneinheitliche Rechtschreibung innerhalb derselben Sprache.

  NACHGETRAGEN: sprachen.py "app.ueber_kurz" Zeile 822
    jetzt   : Lütfen bütün içeriği ana dili konuşanlara kontrol ettirin.
    besser  : Lütfen bütün içeriği ana dili konuşanlara kontrol ettir.
    warum   : Einzige Stelle in der Siez-Form ("ettirin"); die ganze App duzt ("dokun", "yaz", "dene"). Ton-Bruch.
  uneinheitlicher Begriff: Aufgabe (in Tagesaufgaben/Lektion) -> görev (quest.fertig, lektion.uebersprungen, task.mikro_blockiert), soru (quest.aufgaben: "{n} soru cevapla"), alıştırma (task.tippen_weiter, Datenschutz: konuşma alıştırmaları)
  uneinheitlicher Begriff: Testmodus / Testbetrieb -> Deneme modu (leben.testmodus), deneme modu (pfad.testmodus), Test modu (konto.testbetrieb)
  uneinheitlicher Begriff: Laden / Geschäft (Lernstoff) -> mağaza (Vokabel "Laden"), dükkân (Vokabel "Geschäft", Geschichten "Laden (Lok.)")
  uneinheitlicher Begriff: Genitiv (Wörterbuch-Vermerk) -> genitif (alle Einträge), tamlayan (nur "Haus (Gen.)")
  uneinheitlicher Begriff: wohnen -> ikamet etmek (Vokabel "wohnen"), oturmak ("ich wohne", "Wo wohnst du?", Lückensätze, Geschichten)
  uneinheitlicher Begriff: Mädchen -> genç kız ("das Mädchen", Geschlecht-Level), kız çocuğu (Geschichten-Wörterbuch "Mädchen")
  uneinheitlicher Begriff: Abbrechen -> Bırak (btn.abbrechen), bitir / bitirilsin mi (lektion.abbrechen, test.abbrechen), yarıda kaldı (lektion.aus)
  uneinheitlicher Begriff: Nicht geklappt -> Olmadı. (task.mikro_fehler, konto.fehler_allgemein), Bu işe yaramadı. (set.sicherung_fehler)

==============================================================================
## Französisch   (24 Funde, Gegenprüfung: ja)
==============================================================================

Die französische Fassung ist insgesamt gut: idiomatisch, durchgehend geduzt, französische Leerzeichen vor ? ! : sowie « » sind fast überall richtig gesetzt, und die Kernbegriffe (niveau, leçon, série, pièces, vies, Version complète, Parcours, Boutique) werden einheitlich verwendet. Die Oberfläche ist gegenüber dem Deutschen vollständig und nicht veraltet; nur in den Rechtstexten gibt es kleine Abweichungen (Datenübertragbarkeit hinzugefügt, Store vs. Boutique, Artikel-Zitierweise). Echte Fehler sind wenige: "Arrêter" als allgemeiner Abbrechen-Knopf, "tarte" für Torte, ein "Retenez" (Sie-Form) mitten im Duz-Text, "en-tête" für Briefanrede sowie mehrere Zählertexte, die bei n=1 grammatisch kaputt sind ("1 niveaux sur 12"). Der Lernstoff (Vokabeln, Lückensätze, Grammatik, Geschichten, Wörterbuch) klingt wie eine echte französische App; die Grammatik-Erklärungen sind sauber übertragen.


--- FALSCHE BEDEUTUNG (4) ---

  uebersetzungen.py "Torte", Zeile 15144   [mittel]
    deutsch : Torte
    jetzt   : tarte
    besser  : gâteau (torta, à la crème)
    warum   : Eine französische „tarte“ ist ein flacher Mürbeteigkuchen mit Belag. Bosnisch „torta“ ist eine Cremetorte, auf Französisch „gâteau“. Zugleich steht „Kuchen“ (kolač) schon als „gâteau“; die Unterscheidung müsste über den Zusatz laufen.

  sprachen.py mail.bestaetigen_betreff, Zeile 2920   [gering]
    deutsch : Willkommen bei Zmaj – bitte bestätige deine Adresse
    jetzt   : Bienvenue sur Zmaj – encore un clic
    besser  : Bienvenue sur Zmaj – confirme ton adresse
    warum   : Der deutsche Betreff sagt, worum es geht (Adresse bestätigen); „encore un clic“ verrät das nicht und wirkt in einer Betreffzeile wie Spam-Sprache.

  uebersetzungen.py "Sie-Form, Höflichkeit, Briefanrede.", Zeile 14203   [gering]
    deutsch : Sie-Form, Höflichkeit, Briefanrede.
    jetzt   : Le vouvoiement, la politesse, l'en-tête d'une lettre.
    besser  : Le vouvoiement, la politesse, les formules d'appel d'une lettre.
    warum   : „en-tête“ ist der Briefkopf (Absender, Datum). Die Briefanrede („Sehr geehrter Herr“) heißt „formule d'appel“. Das Level lehrt genau diese Anreden (Monsieur, / Madame,).

  sprachen.py gesch.kein_eintrag, Zeile 2737   [gering]
    deutsch : Kein Eintrag im Wörterbuch.
    jetzt   : Pas encore dans le lexique.
    besser  : Pas d'entrée dans le lexique.
    warum   : „Pas encore“ verspricht, dass der Eintrag noch kommt – das steht nicht im Deutschen.

--- Grammatik/Rechtschreibung (4) ---

  sprachen.py pfad.summary, Zeile 2710 (ebenso pfad.sektion_stand, Zeile 2712)   [gering]
    deutsch : {done} von {total} Levels geschafft · {k} von {n} Wörtern sitzen
    jetzt   : {done} niveaux sur {total} réussis · {k} mots sur {n} acquis
    besser  : Niveaux réussis : {done} sur {total} · Mots acquis : {k} sur {n}
    warum   : Bei done=1 oder k=1 entsteht „1 niveaux sur 12 réussis“ / „1 mots sur 20 acquis“ – Plural nach 1 ist im Französischen falsch. Im Deutschen hängt der Plural an der Gesamtzahl, im Französischen an der Zahl davor. Gleiches Problem in pfad.sektion_stand „{done} niveaux sur {n}“ → „Niveaux : {done} sur {n}“.

  sprachen.py level.cap, Zeile 2756   [gering]
    deutsch : {done} von {n} Wörtern sitzen
    jetzt   : {done} mots sur {n} acquis
    besser  : Mots acquis : {done} sur {n}
    warum   : Bei done=1: „1 mots sur 20 acquis“ – falscher Plural nach 1.

  sprachen.py gesch.summary, Zeile 2722   [gering]
    deutsch : {done} von {n} Geschichten gelesen · von Kinderbuch bis Amtssprache. ...
    jetzt   : {done} histoires sur {n} lues · de l'album jeunesse à la langue administrative. ...
    besser  : Histoires lues : {done} sur {n} · de l'album jeunesse à la langue administrative. Une histoire est terminée quand toutes les questions ont une bonne réponse.
    warum   : Bei done=1: „1 histoires sur 12 lues“ – falscher Plural nach 1.

  sprachen.py gesch.ergebnis, Zeile 2740   [gering]
    deutsch : {r} von {n} richtig
    jetzt   : {r} bonnes réponses sur {n}
    besser  : Score : {r} sur {n}
    warum   : Bei r=1 (und r=0): „1 bonnes réponses sur 5“ – falscher Plural. Danach wird gesch.geschafft bzw. gesch.nochmal_lesen angehängt, „Score : 3 sur 5 – histoire terminée !“ passt dazu.

--- uneinheitlich (6) ---

  uebersetzungen.py "Merke „u“ und „na“: ...", Zeile 15575   [mittel]
    deutsch : Merke „u“ und „na“: Bewegung → Akkusativ (Idem u grad), Ort → Lokativ (Ja sam u gradu).
    jetzt   : Retenez « u » et « na » : mouvement → accusatif (Idem u grad, je vais en ville), lieu → locatif (Ja sam u gradu, je suis en ville).
    besser  : Retiens « u » et « na » : mouvement → accusatif (Idem u grad, je vais en ville), lieu → locatif (Ja sam u gradu, je suis en ville).
    warum   : „Retenez“ ist die Sie-/Ihr-Form. Die ganze App duzt (« Réessaie », « Touche un mot »); an dieser einzigen Stelle springt der Text ins Vous.

  sprachen.py set.agb_text, Zeile 2863 (Abschnitt 5)   [mittel]
    deutsch : es gibt keine Zusage, dass sie dauerhaft weitergepflegt oder im Store angeboten wird
    jetzt   : il n'est pas promis qu'elle continue d'être entretenue ni qu'elle reste proposée dans la boutique
    besser  : il n'est pas promis qu'elle continue d'être entretenue ni qu'elle reste proposée sur le Play Store
    warum   : „Boutique“ ist in der App der Name des In-App-Ladens (laden.titel, tab.laden). Hier ist aber der Google Play Store gemeint; für Leser klingt es, als könnte der Münz-Laden verschwinden.

  sprachen.py app.ueber_kurz, Zeile 2622   [gering]
    deutsch : Bitte alle Inhalte mit Muttersprachlern prüfen.
    jetzt   : Faites relire l'ensemble par des locuteurs natifs.
    besser  : À faire relire par des locuteurs natifs.
    warum   : „Faites“ ist Vous-Form; die App duzt sonst durchgehend. Der deutsche Satz ist unpersönlich (Infinitiv), das lässt sich im Französischen ebenso lösen.

  sprachen.py set.datenschutz_text, Zeile 2865 (Abschnitt 8)   [gering]
    deutsch : Du kannst Auskunft über deine Daten verlangen, sie berichtigen oder löschen lassen, die Verarbeitung einschränken und ihr widersprechen.
    jetzt   : Tu peux demander quelles données nous détenons, les faire rectifier, effacer ou transférer, limiter leur traitement et t'y opposer.
    besser  : Tu peux demander quelles données nous détenons, les faire rectifier ou effacer, limiter leur traitement et t'y opposer.
    warum   : „ou transférer“ (Datenübertragbarkeit) steht nicht im deutschen Text. Rechtstexte sollten in allen Sprachen dasselbe versprechen.

  sprachen.py set.dsgvo_werbung_an, Zeile 2867   [gering]
    deutsch : Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO
    jetzt   : consentement au sens de l'art. 6, § 1, a du RGPD
    besser  : consentement au sens de l'art. 6, paragraphe 1, point a, du RGPD
    warum   : Die Datenschutzerklärung (set.datenschutz_text) zitiert dieselbe Norm als „art. 6, paragraphe 1, point f, du RGPD“; zwei Zitierweisen im selben Dokument.

  uebersetzungen.py "Beim Arzt und bei der Krankenkasse: Überweisung, Rezept, Krankschreibung.", Zeile 14215   [gering]
    deutsch : Beim Arzt und bei der Krankenkasse: Überweisung, Rezept, Krankschreibung.
    jetzt   : Chez le médecin et à l'assurance maladie : orientation, ordonnance, arrêt de travail.
    besser  : Chez le médecin et à l'assurance maladie : lettre d'adressage, ordonnance, arrêt de travail.
    warum   : Die Vokabel selbst (Zeile 15353) und der Lückensatz (15483) übersetzen Überweisung mit „lettre d'adressage“ (nachgeschlagen: der in Frankreich gebräuchliche Begriff). Im Level-Tipp steht dagegen „orientation“, das allein kaum verständlich ist.

--- unnatürlich (9) ---

  sprachen.py set.toene_sub, Zeile 2834   [gering]
    deutsch : Richtig- und Falsch-Ton, Fanfare am Ende.
    jetzt   : Son juste et faux, fanfare à la fin.
    besser  : Un son pour juste, un pour faux, fanfare à la fin.
    warum   : „Son juste et faux“ liest sich wie „ein richtiger und falscher Ton“ (ein Ton, der zugleich richtig und falsch ist). Gemeint sind zwei Töne für richtige bzw. falsche Antworten.

  sprachen.py set.agb_text, Zeile 2863 (Abschnitt 6)   [gering]
    deutsch : Sie dürfen nicht kopiert und als eigenes Angebot weiterverbreitet werden.
    jetzt   : Il ne peut pas être copié ni diffusé comme une offre propre.
    besser  : Il ne peut pas être copié ni rediffusé comme si c'était ta propre offre.
    warum   : „comme une offre propre“ ist wörtlich aus dem Deutschen; „offre propre“ versteht ein Franzose eher als „saubere Angebot“. Der Besitzbezug („eigenes“) fehlt.

  sprachen.py set.agb_text, Zeile 2863 (Abschnitt 5)   [gering]
    deutsch : Sie wird in der Freizeit entwickelt
    jetzt   : Elle est développée pendant le temps libre
    besser  : Elle est développée sur notre temps libre
    warum   : „pendant le temps libre“ ohne Bezug klingt übersetzt; die übliche Wendung ist „sur notre/son temps libre“.

  uebersetzungen.py "Sehenswürdigkeit", Zeile 15115   [gering]
    deutsch : Sehenswürdigkeit
    jetzt   : site à voir
    besser  : site touristique
    warum   : „site à voir“ ist kein feststehender Begriff; für znamenitost sagt man „site touristique“, „monument“ oder „curiosité“.

  uebersetzungen.py "Bei manchen männlichen Wörtern ändert sich vor -i der Konsonant ...", Zeile 15551 (ebenso Zeile 15581)   [gering]
    deutsch : Bei manchen männlichen Wörtern ändert sich vor -i der Konsonant
    jetzt   : Chez certains mots masculins, la consonne change devant -i
    besser  : Pour certains mots masculins, la consonne change devant -i
    warum   : „chez“ wird für Personen und Lebewesen benutzt, nicht für Wörter; das ist das deutsche „bei“ wörtlich übertragen. Gleicher Fall in Zeile 15581 („Chez les mots féminins en -ka“ → „Pour les mots féminins en -ka“).

  uebersetzungen.py "„Ich wasche das Auto.“ (nicht mich!)", Zeile 15815   [gering]
    deutsch : „Ich wasche das Auto.“ (nicht mich!)
    jetzt   : « Je lave la voiture. » (pas moi !)
    besser  : « Je lave la voiture. » (et non « me laver » !)
    warum   : „pas moi !“ liest sich als „nicht ich (wasche)“, also als Widerspruch zum Subjekt. Gemeint ist, dass hier kein reflexives „se“ steht.

  sprachen.py profil.gruss, Zeile 2635   [gering]
    deutsch : Merhaba! Ich bin Zmaj, dein Lerndrache.
    jetzt   : Merhaba ! Je suis Zmaj, ton dragon apprenant.
    besser  : Merhaba ! Je suis Zmaj, ton compagnon d'apprentissage.
    warum   : „dragon apprenant“ heißt „lernender Drache“ (der Drache lernt selbst). Gemeint ist der Drache, der beim Lernen hilft.

  sprachen.py hero.serie_sub, Zeile 2704   [gering]
    deutsch : Heute noch nicht geübt.
    jetzt   : Rien fait aujourd'hui.
    besser  : Pas encore d'entraînement aujourd'hui.
    warum   : „Rien fait aujourd'hui“ klingt vorwurfsvoll und lässt das „noch“ weg; das Deutsche ist neutral und offen.

  sprachen.py leben.warten, Zeile 2642   [gering]
    deutsch : ♥ Keine Leben · warten
    jetzt   : ♥ Plus de vies · patiente
    besser  : ♥ Plus de vies · en attente
    warum   : „patiente“ ist ein Imperativ („hab Geduld“); das Deutsche ist eine Statusanzeige. Als Status passt „en attente“ besser.

--- Zeichensetzung (1) ---

  sprachen.py quest.titel bis laden.herz_sub, Zeilen 2656–2671   [gering]
    deutsch : Heute / Alle drei geschafft! / ... statt zwei Stunden zu warten.
    jetzt   : Aujourd’hui / Les trois, c’est fait ! / ... au lieu d’attendre deux heures.
    besser  : Aujourd'hui / Les trois, c'est fait ! / ... au lieu d'attendre deux heures.
    warum   : Dieser Block benutzt den typografischen Apostroph ’, der gesamte Rest der französischen Fassung den geraden Apostroph '. In der Oberfläche fällt der Wechsel auf.

  NACHGETRAGEN: sprachen.py leben.stand, Zeile 2641
    jetzt   : {n} vies sur {max} · la prochaine dans {zeit}
    besser  : Vies : {n} sur {max} · la prochaine dans {zeit}
    warum   : Dasselbe Zählerproblem wie bei pfad.summary, vom ersten Prüfer nicht gemeldet: Bei n=1 steht „1 vies sur 5“ (falscher Plural nach 1), und n=1 kommt bei Leben ständig vor.

  NACHGETRAGEN: sprachen.py laden.schutz, Zeile 2672
    jetzt   : Protection de la série
    besser  : Protection de série
    warum   : set.serie_schutz (2849) und serie.schutz (2648) nennen den Gegenstand „protection de série“; nur im Laden heißt er „Protection de la série“. Der erste Prüfer hat es unter Begriffen notiert, aber nicht als Fehler gemeldet. Ein Kaufgegenstand sollte überall gleich heißen.

  NACHGETRAGEN: sprachen.py serie.schutz_voll, Zeile 2650
    jetzt   : au complet
    besser  : au maximum
    warum   : Wird als „❄ 3 protections de série · au complet“ angezeigt (index.html 1864, 2522). „au complet“ heißt „vollzählig / ausverkauft“ (Hotel, Mannschaft), nicht „Vorrat ist voll“. „au maximum“ sagt, was gemeint ist: Höchstzahl erreicht.

  NACHGETRAGEN: sprachen.py task.luecke, Zeile 2790
    jetzt   : Complète le trou
    besser  : Complète la phrase
    warum   : „compléter un trou“ sagt man nicht; französische Übungsanweisungen lauten „Complète la phrase“ oder „Remplis le trou“. Wörtlich aus dem Deutschen übertragen.

  NACHGETRAGEN: sprachen.py test.zum_pfad, Zeile 2821
    jetzt   : Vers le parcours
    besser  : Aller au parcours
    warum   : Knopfbeschriftung (index.html 3546). „Vers le parcours“ ist kein üblicher Knopftext; die Schwester-Taste lektion.zum_lesen heißt „Aller aux histoires“. Gleiche Bauart wäre „Aller au parcours“.

  NACHGETRAGEN: uebersetzungen.py Level-Tipp „Nebensätze & Verneinung“, Zeile 14152
    jetzt   : Que, parce que, si : construire des phrases plus longues et dire non.
    besser  : Que, parce que, si : construire des phrases plus longues et la négation.
    warum   : „verneinen“ meint hier die grammatische Verneinung (ne vor dem Verb, nisam/nemam/neću), die das Level lehrt. „dire non“ heißt „Nein sagen“ und trifft den Inhalt nicht.

  NACHGETRAGEN: uebersetzungen.py Tipp „dich = te.“, Zeile 15861
    jetzt   : te (accusatif) = te.
    besser  : toi (accusatif) = te.
    warum   : Links soll das Wort in der Oberflächensprache stehen, rechts das bosnische. „te = te“ liest sich als Nonsens-Gleichung, weil das französische und das bosnische Wort zufällig gleich lauten. Das Wörterbuch löst es mit „toi“ („dich / dir“: „toi“, Zeile 16112).
  uneinheitlicher Begriff: Serienschutz -> Protection de série (set.serie_schutz, serie.schutz), Protection de la série (laden.schutz), protections de série (serie.gerettet, Datenschutz)
  uneinheitlicher Begriff: Store / Laden -> Boutique (In-App-Laden: laden.titel, tab.laden), la boutique (für Google Play Store in set.agb_text Abschnitt 5), Google Play Store / Google Play (set.agb_text Abschnitt 7)
  uneinheitlicher Begriff: Aufgabe -> objectif (Tagesaufgabe: quest.fertig, laden.stand, AGB), question (quest.aufgaben „Répondre à {n} question“), exercice (task.tippen_weiter, lektion.uebersprungen, task.mikro_blockiert)
  uneinheitlicher Begriff: Überweisung (Arzt) -> orientation (Level-Tipp Arzt & Versicherung), lettre d'adressage (Vokabel und Lückensatz)
  uneinheitlicher Begriff: Ich möchte -> Je voudrais (Ich möchte (m/w), Ich möchte ein Konto eröffnen, Ich möchte drei Äpfel), Je veux (Ich möchte reisen, Ich möchte lernen, Ich möchte etwas essen)
  uneinheitlicher Begriff: Mensch -> personne (Vokabel „Mensch“, „Mensch → Menschen“), être humain (Übungsfrage „Mehrzahl von čovjek“)
  uneinheitlicher Begriff: Wörterbuch -> lexique (gesch.kein_eintrag), dictionnaire (sonst nirgends benannt; Datenschutz spricht nur von Wörtern)

==============================================================================
## Dänisch   (17 Funde, Gegenprüfung: ja)
==============================================================================

Die dänische Fassung ist insgesamt solide und klingt über weite Strecken wie eine echte dänische App: Duzen, knapper Ton, korrekte Anführungszeichen »…«, sinnvolle Anpassungen (z. B. Datid statt Perfekt, Grammatikhinweis auf dänisches »ikke«). Die Kernbegriffe Niveau, Lektion, Mønter, Fuld version, Butik und Liv sind einheitlich; uneinheitlich sind dagegen Lernserie (række/serie), Serienschutz (rækkebeskyttelse/Seriebeskyttelse), Werbung (annoncer/reklamer) und »unbegrenzte Leben« (ubegrænset med liv/ubegrænsede liv). Echte Bedeutungsfehler gibt es wenige, aber zwei gewichtige: »Mama« ist mit »mormor« (Oma) übersetzt, und »Jeg går i byen med min bror« heißt auf Dänisch »ich gehe mit meinem Bruder feiern«. Dazu kommen ein erfundenes Wort in der Datenschutzerklärung (»kending« für Kennung), die fehlenden dänischen Wörter farbror/morbror und ein paar kleinere Ungenauigkeiten in Vokabeln und Oberfläche. Veraltete Übersetzungen gegenüber dem deutschen Stand habe ich nur an einer Stelle gefunden (Datenschutz, Sprechaufgabe überspringen).


--- FALSCHE BEDEUTUNG (9) ---

  uebersetzungen.py "Mama" (Zeile 12033)   [hoch]
    deutsch : Mama
    jetzt   : mormor
    besser  : mor
    warum   : »mormor« ist die Oma mütterlicherseits. Mama heißt »mor« (Kosewort auch »mor« oder »mors«). Das Wort wird so falsch gelernt.

  uebersetzungen.py "Ich gehe mit dem Bruder in die Stadt." (Zeile 13239)   [mittel]
    deutsch : Ich gehe mit dem Bruder in die Stadt.
    jetzt   : Jeg går i byen med min bror.
    besser  : Jeg tager ind til byen med min bror.
    warum   : »at gå i byen« bedeutet auf Dänisch »ausgehen, feiern gehen« (laut Den Danske Ordbog). Für »in die Stadt gehen« sagt man »tage ind til byen«, so wie es die Grammatikübung (Zeile 13494) auch richtig macht.

  sprachen.py set.datenschutz_text (Zeile 2504)   [mittel]
    deutsch : Eine Zufallskennung wird beim ersten Start erzeugt.
    jetzt   : <b>En tilfældig kending</b> oprettes, første gang du starter appen.
    besser  : <b>Et tilfældigt id</b> oprettes, første gang du starter appen.
    warum   : »kending« heißt auf Dänisch »ein alter Bekannter« (en gammel kending af politiet) oder veraltet »Landkennung«, nie technische Kennung. Nachgeschlagen in Den Danske Ordbog. Üblich sind »id« oder »identifikator«.

  uebersetzungen.py "als / wenn (zeitlich)" (Zeile 12427) und "als / wenn (Zeit)" (Zeile 13403)   [gering]
    deutsch : als / wenn (zeitlich)
    jetzt   : da (i tid)
    besser  : da / når (om tid)
    warum   : Bosnisch »kad« deckt beides ab; im Dänischen ist »da« nur für einmalige Vergangenheit, »når« für Wiederholtes und Zukunft. Das Beispiel direkt darunter (»Kad dođem, zovem te« → »Når jeg kommer …«) und das Geschichten-Wörterbuch (Zeile 13763: »når«) zeigen, dass »da« allein nicht reicht.

  uebersetzungen.py "Notaufnahme / Notarzt" (Zeile 13087)   [gering]
    deutsch : Notaufnahme / Notarzt
    jetzt   : skadestuen
    besser  : skadestue / vagtlæge
    warum   : Der zweite Teil (Notarzt) fehlt in der Übersetzung; dänisch »vagtlæge«. Außerdem steht die bestimmte Form, obwohl alle anderen Vokabeln unbestimmt sind.

  uebersetzungen.py "euch / Ihnen" (Zeile 12545)   [gering]
    deutsch : euch / Ihnen
    jetzt   : til jer
    besser  : til jer / til Dem
    warum   : Die Höflichkeitsform »Ihnen« fehlt; sonst wird »Sie« im Block konsequent mit »De/Dem« wiedergegeben (z. B. »I er / De er«, »Jeg takker Dem«).

  uebersetzungen.py "noch" (Zeile 13820)   [gering]
    deutsch : noch
    jetzt   : stadig
    besser  : endnu / stadig
    warum   : Im Geschichtentext steht »ich verstehe noch nicht alles«; in der Verneinung heißt »noch« auf Dänisch »endnu« (»ikke endnu«), nicht »stadig«. Die Übersetzung der Geschichte selbst (Zeile 13783) benutzt richtig »endnu«.

  sprachen.py test.durchgefallen (Zeile 2459)   [gering]
    deutsch : Ab {n} richtigen Antworten ist es geschafft.
    jetzt   : Du skal bruge {n} rigtige svar.
    besser  : Du skal bruge mindst {n} rigtige svar.
    warum   : »Ab n« heißt mindestens n; die dänische Fassung klingt nach genau n.

  sprachen.py gesch.kein_eintrag (Zeile 2376)   [gering]
    deutsch : Kein Eintrag im Wörterbuch.
    jetzt   : Står ikke i ordlisten endnu.
    besser  : Ingen post i ordbogen.
    warum   : »endnu« (noch nicht) steht nicht im Deutschen und verspricht, dass der Eintrag nachkommt.

--- Grammatik/Rechtschreibung (1) ---

  sprachen.py hero.serie_sub (Zeile 2343) und lektion.heute_geuebt (Zeile 2448)   [gering]
    deutsch : Heute noch nicht geübt. / Heute geübt ✓ Deine Serie geht weiter.
    jetzt   : Ikke øvet dig i dag endnu. / Øvet dig i dag ✓ Din række fortsætter.
    besser  : Du har ikke øvet i dag endnu. / Øvet i dag ✓ Din række fortsætter.
    warum   : Das reflexive »dig« ohne Subjekt »du« ist im Dänischen grammatisch schief; entweder ganzer Satz oder »øvet« ohne »dig«.

--- veraltet (1) ---

  sprachen.py set.datenschutz_text (Zeile 2504), Abschnitt 5   [gering]
    deutsch : Du kannst jede Sprechaufgabe überspringen – tippe auf „Kann jetzt nicht sprechen“.
    jetzt   : Du kan springe enhver taleopgave over – til det er der en egen knap.
    besser  : Du kan springe enhver taleopgave over – tryk på »Det kan ikke lade sig gøre at tale nu, spring over«.
    warum   : Der deutsche Text nennt die Beschriftung der Taste, die dänische Fassung sagt nur »dafür gibt es eine eigene Taste«. Das passt zu einer älteren Fassung; außerdem ist »en egen knap« hier unidiomatisch (»en særskilt knap«).

--- uneinheitlich (2) ---

  sprachen.py laden.schutz / laden.schutz_sub (Zeilen 2311-2312) gegenüber serie.schutz, set.serie_schutz   [mittel]
    deutsch : Serienschutz / Deckt einen ausgelassenen Tag ab, damit die Serie bleibt.
    jetzt   : Seriebeskyttelse / Dækker en dag, du springer over, så serien fortsætter.
    besser  : Rækkebeskyttelse / Dækker en dag, du springer over, så din række fortsætter.
    warum   : Überall sonst heißt die Lernserie »række« und der Schutz »rækkebeskyttelse« (serie.schutz, serie.gerettet, set.serie_schutz, set.datenschutz_text). Nur im Laden steht »serie«. Der Nutzer sieht so zwei Namen für dieselbe Sache.

  sprachen.py set.agb_text (Zeile 2502) und lektion.vollversion (Zeile 2441) gegenüber consent.*, set.einwilligung, werbung.*   [mittel]
    deutsch : Werbung
    jetzt   : reklamer (AGB, lektion.vollversion) / annoncer (Consent, Einstellungen, set.dsgvo_werbung_an, werbung.*)
    besser  : annoncer durchgehend, z. B. lektion.vollversion: »Den fulde version har ubegrænsede liv og ingen annoncer.«
    warum   : Werbung wird abwechselnd »reklamer« und »annoncer« genannt. Die Einstellung heißt »Annoncer«, die Datenschutzerklärung verweist auf »Indstillinger → Annoncer«, die AGB sprechen aber von »reklamer«. Ein Begriff sollte reichen.

--- unnatürlich (4) ---

  uebersetzungen.py "Onkel (Vaterseite)" / "Onkel (Mutterseite)" (Zeilen 12047-12048)   [mittel]
    deutsch : Onkel (Vaterseite) / Onkel (Mutterseite)
    jetzt   : onkel (på farens side) / onkel (på morens side)
    besser  : farbror / morbror
    warum   : Dänisch hat für amidža/daidža exakt passende Wörter: farbror (Bruder des Vaters) und morbror (Bruder der Mutter), beide in Den Danske Ordbog. Die Umschreibung wirkt wie aus dem Deutschen übertragen. Gleiches gilt für den Lückensatz »Mein Onkel (Vaterseite) ist Imker.« (Zeile 13130): »Min farbror er biavler.«

  sprachen.py task.was_heisst (Zeile 2406)   [gering]
    deutsch : Was heißt auf Bosnisch …
    jetzt   : Hvordan siger man det på bosnisk …
    besser  : Hvad hedder på bosnisk …
    warum   : Nach den Punkten folgt das abgefragte Wort. Mit »det« im Satz ergibt »Hvordan siger man det på bosnisk … hund« keinen Sinn; ohne Objekt (»Hvad hedder på bosnisk … hund«) schon.

  sprachen.py set.feedback_sub (Zeile 2492)   [gering]
    deutsch : die Nachricht kommt per Mail bei uns an
    jetzt   : beskeden når os med e-mail
    besser  : beskeden når os pr. e-mail
    warum   : »med e-mail« ist unidiomatisch; dänisch sagt man »pr. e-mail« oder »via e-mail«.

  sprachen.py set.agb_text (Zeile 2502), Abschnitt 2   [gering]
    deutsch : sie sind keine verbindliche Auskunft
    jetzt   : de er ingen bindende oplysning
    besser  : de er ikke bindende oplysninger
    warum   : »er ingen bindende oplysning« ist eine wörtliche Übertragung von »sind keine«; natürlich ist die Verneinung mit »ikke«.

  NACHGETRAGEN: uebersetzungen.py Zeile 12336 "euer / Ihr (m/w/s)"
    jetzt   : jeres (h/hu/i)
    besser  : jeres / Deres (h/hu/i)
    warum   : Dieselbe Lücke wie bei "euch / Ihnen" (12545): die Höflichkeitsform fehlt, obwohl Sie/De sonst konsequent mitgeführt wird (12358, 12950-12951).

  NACHGETRAGEN: sprachen.py Zeile 2502 set.agb_text, Abschnitt 6
    jetzt   : Det må ikke kopieres og spredes som et eget tilbud.
    besser  : Det må ikke kopieres og spredes som ens eget tilbud.
    warum   : "egen" ohne Possessiv ("et eget ...") bedeutet laut DDO eher "eigenartig, besonders"; der Satz liest sich als "als ein eigentümliches Angebot". Gleiche Schwäche wie "en egen knap" in der Datenschutzerklärung.

  NACHGETRAGEN: uebersetzungen.py Zeilen 12651 "Ich muss gehen", 12658 "Wir müssen warten", 13535 "Mi ___ čekati."
    jetzt   : Jeg må gå / Vi må vente
    besser  : Jeg skal gå / Vi skal vente
    warum   : Im selben Level wird "må" als dürfen eingeführt (12647-12648 "at måtte / jeg må", 13532 "Du må ikke ryge her") und der Tipp 13628 sagt "at skulle = morati → moram". Wenn moram an zwei Stellen trotzdem mit "må" wiedergegeben wird, verschwimmt für den Lernenden genau der Unterschied morati/smjeti, den die Grammatik-Erklärung (13335) betont. "Jeg må gå" ist zwar umgangssprachlich üblich, hier aber didaktisch irreführend.

  NACHGETRAGEN: uebersetzungen.py Zeilen 12914 und 13170 "Am Montag gehe ich zur Arbeit"
    jetzt   : Om mandagen tager jeg på arbejde
    besser  : På mandag tager jeg på arbejde
    warum   : "om mandagen" heißt "montags" (gewohnheitsmäßig); das Deutsche und das bosnische "u ponedjeljak" meinen den einen (kommenden) Montag, dafür sagt Dänisch "på mandag". Die App macht es bei "Wir sehen uns am Samstag" → "Vi ses på lørdag" (12922) richtig.

  NACHGETRAGEN: uebersetzungen.py Zeile 12465 "rufen / anrufen"
    jetzt   : at kalde / at ringe
    besser  : at kalde på / at ringe til
    warum   : "at kalde" allein heißt vor allem "nennen" (kalde nogen noget); "jemanden rufen" ist "kalde på", "anrufen" ist "ringe til". Die Beispielsätze (12453 "Jeg ringer til lægen") haben die Präposition, der Infinitiv-Eintrag nicht.

  NACHGETRAGEN: sprachen.py Zeile 2504 set.datenschutz_text, Abschnitt 8
    jetzt   : Du kan bede om indsigt i dine oplysninger, få dem rettet, slettet eller overført, begrænse behandlingen og gøre indsigelse mod den.
    besser  : Du kan bede om indsigt i dine oplysninger, få dem rettet eller slettet, begrænse behandlingen og gøre indsigelse mod den.
    warum   : "eller overført" (Datenübertragbarkeit) steht nicht im deutschen Text; die dänische Fassung führt ein Recht auf, das der deutsche Stand nicht nennt. Sachlich harmlos, aber die beiden Rechtstexte sollten deckungsgleich sein.
  uneinheitlicher Begriff: Lernserie -> række (serie.tage, hero.serie, set.serie, set.profil_sub, lektion.heute_geuebt), serie (laden.schutz_sub)
  uneinheitlicher Begriff: Serienschutz -> rækkebeskyttelse (serie.schutz, serie.gerettet, set.serie_schutz, set.datenschutz_text), Seriebeskyttelse (laden.schutz), beskyttelse (set.serie_schutz_sub)
  uneinheitlicher Begriff: Werbung -> annoncer (consent.*, set.einwilligung, set.werbung_pers, set.dsgvo_werbung_an, werbung.*), reklamer (set.agb_text, lektion.vollversion)
  uneinheitlicher Begriff: unbegrenzte Leben -> ubegrænset med liv (leben.testmodus, leben.unbegrenzt, lektion.vollversion), ubegrænsede liv (set.agb_text)
  uneinheitlicher Begriff: Laden / Store -> Butik (laden.titel, tab.laden – der In-App-Laden), butikken / Google Play Butik (set.agb_text – der App-Store)
  uneinheitlicher Begriff: Bestanden -> Klaret (zustand.bestanden, level.test_bestanden, level.note_bestanden), Bestået (test.bestanden, test.sektion_fertig, set.datenschutz_text »beståede niveauer«)
  uneinheitlicher Begriff: Wörterbuch -> ordlisten (gesch.kein_eintrag), ordbog (sonst nicht benannt)
  uneinheitlicher Begriff: Level -> niveau (durchgehend einheitlich)
  uneinheitlicher Begriff: Lektion -> lektion (durchgehend einheitlich)
  uneinheitlicher Begriff: Münzen -> mønter (durchgehend einheitlich)
  uneinheitlicher Begriff: Vollversion -> Fuld version / den fulde version (durchgehend einheitlich)
  uneinheitlicher Begriff: Leben -> liv (durchgehend einheitlich)
  uneinheitlicher Begriff: Lernpfad -> Læringssporet / læringssporet (durchgehend einheitlich)
  uneinheitlicher Begriff: Sektion -> Del / delen (durchgehend einheitlich)

==============================================================================
## Niederländisch   (17 Funde, Gegenprüfung: fehlt)
==============================================================================

Die niederländische Fassung ist insgesamt gut: Sie klingt wie eine echte niederländische Lern-App, duzt durchgehend, und die Kernbegriffe (niveau, les, reeks, munten, volledige versie, winkel, levens, leerpad, deel) sind fast überall einheitlich. Die Grammatik-Erklärungen sind sinnvoll ans Niederländische angepasst (z. B. der Hinweis zur Verbstellung im Nebensatz). Echte Fehler sind selten, aber es gibt einige: "sein" ist als "zijn (bezittelijk)" (= besitzanzeigend) statt als Verb erklärt, "Geschäft" wurde zu "zaak" statt "winkel", "Was gibt's?" zu "Wat is er?" (= "Was ist los?"), "Zeugnis" zu "diploma", und in der Datenschutzerklärung fehlt der im Deutschen genannte Knopf zum Überspringen der Sprechaufgabe. Dazu kommen Kleinigkeiten wie "onbeperkt levens" statt "onbeperkte levens" und uneinheitliche Wörter für Aufgabe, Tagesaufgabe und Werbung.


--- FALSCHE BEDEUTUNG (7) ---

  uebersetzungen.py "sein" (Wörter · Verben), Zeile 7722   [hoch]
    deutsch : sein
    jetzt   : zijn (bezittelijk)
    besser  : zijn (werkwoord)
    warum   : "bezittelijk" heißt besitzanzeigend (wie in "bezittelijk voornaamwoord"). Hier ist aber das Verb "sein" (bosnisch biti) gemeint, es steht in der Verben-Liste. Der Lernende bekommt eine falsche Erklärung.

  uebersetzungen.py "Geschäft" (Wörter · Einkaufen und Kleidung), Zeile 7674   [mittel]
    deutsch : Geschäft
    jetzt   : zaak
    besser  : winkel
    warum   : Bosnisch "radnja" ist der Laden. "zaak" bedeutet im Niederländischen vor allem Firma/Betrieb oder Angelegenheit; für den Laden, in dem man einkauft, sagt man "winkel" (so steht es auch bei "Laden" in Zeile 7713).

  uebersetzungen.py "Was gibt's? / Wie läuft's?" (Wörter · Smalltalk), Zeile 7741   [mittel]
    deutsch : Was gibt's? / Wie läuft's?
    jetzt   : Wat is er? / Hoe gaat het?
    besser  : Hoe is het? / Alles goed?
    warum   : "Wat is er?" heißt im Niederländischen in erster Linie "Was ist los? Was hast du?" (besorgt), nicht der lockere Gruß "Šta ima?". Nachgeschlagen: als Gruß empfehlen Wörterbücher "Hoe is het?", "Alles goed?".

  uebersetzungen.py "Zeugnis" (Wörter · Arbeitsvertrag und Bewerbung), Zeile 8542   [mittel]
    deutsch : Zeugnis
    jetzt   : diploma (schoolgetuigschrift)
    besser  : getuigschrift
    warum   : Bosnisch "svjedočanstvo" ist ein Zeugnis/eine Bescheinigung (Schul- oder Arbeitszeugnis), kein Diplom. Direkt darunter steht "Diplom": "diploma" – so haben zwei verschiedene Vokabeln dieselbe Bedeutung.

  uebersetzungen.py "Kinderbuch" Zeile 7415 und sprachen.py gesch.summary Zeile 1639   [gering]
    deutsch : Kinderbuch
    jetzt   : Prentenboek
    besser  : Kinderboek
    warum   : "prentenboek" ist ein Bilderbuch. Die Stufe meint einfache Kindergeschichten; "kinderboek" trifft es genau.

  sprachen.py set.agb_text, Zeile 1780 (Abschnitt 2)   [gering]
    deutsch : die Level zu Amt, Bank, Immobilien und Arbeitsvertrag
    jetzt   : de niveaus over overheid, bank, woning en arbeidsovereenkomst
    besser  : de niveaus over overheid, bank, vastgoed en arbeidsovereenkomst
    warum   : "woning" ist die Wohnung; "Immobilien" ist "vastgoed"/"onroerend goed" (so auch die Vokabel "Immobilie" in Zeile 8492).

  uebersetzungen.py "Schulden" (Wörter · Bank und Geld), Zeile 8481   [gering]
    deutsch : Schulden
    jetzt   : schuld
    besser  : schulden
    warum   : Das Deutsche steht in der Mehrzahl; "schuld" in der Einzahl bedeutet im Niederländischen zuerst Schuld im Sinne von Verschulden. Für Geldschulden sagt man "schulden".

--- Grammatik/Rechtschreibung (2) ---

  sprachen.py leben.testmodus Zeile 1554, leben.unbegrenzt Zeile 1555, lektion.vollversion Zeile 1719, set.agb_text Zeile 1780 (Abschnitt 7)   [gering]
    deutsch : unbegrenzte Leben
    jetzt   : onbeperkt levens
    besser  : onbeperkte levens
    warum   : Vor einem zählbaren Substantiv in der Mehrzahl wird das Adjektiv gebeugt: "onbeperkte levens". "onbeperkt" ohne -e passt nur adverbial oder vor unzählbaren Wörtern ("onbeperkt bellen"). Spiele-Apps schreiben "onbeperkte levens" (nachgeschlagen).

  uebersetzungen.py "am größten" Zeile 8200, "am besten" Zeile 8205, "„am größten“?" Zeile 9012   [gering]
    deutsch : am größten / am besten
    jetzt   : grootst / best
    besser  : het grootst / het best
    warum   : Der niederländische Superlativ als Prädikat braucht "het": "het grootst", "het best(e)". "best" allein wird als Adjektiv oder Ausruf gelesen.

--- veraltet (2) ---

  sprachen.py set.datenschutz_text, Zeile 1782 (Abschnitt 5)   [mittel]
    deutsch : Du kannst jede Sprechaufgabe überspringen – tippe auf „Kann jetzt nicht sprechen“.
    jetzt   : Je kunt elke spreekopdracht overslaan – daarvoor is er een aparte knop.
    besser  : Je kunt elke spreekopdracht overslaan – tik op ‘Spreken kan nu niet, overslaan’.
    warum   : Das Deutsche nennt den Knopf beim Namen, die Übersetzung sagt nur "dafür gibt es einen eigenen Knopf". Der Knopf heißt in der nl-Oberfläche "Spreken kan nu niet, overslaan" (task.sprechen_skip).

  sprachen.py set.datenschutz_text, Zeile 1782 (Abschnitt 8)   [gering]
    deutsch : Du kannst Auskunft über deine Daten verlangen, sie berichtigen oder löschen lassen, die Verarbeitung einschränken und ihr widersprechen.
    jetzt   : Je kunt inzage vragen in je gegevens, ze laten verbeteren, wissen of overdragen, de verwerking beperken en er bezwaar tegen maken.
    besser  : Je kunt inzage vragen in je gegevens, ze laten verbeteren of wissen, de verwerking beperken en er bezwaar tegen maken.
    warum   : "of overdragen" (Datenübertragbarkeit) steht nicht im deutschen Text; die Übersetzung nennt ein Recht mehr als das Original.

--- uneinheitlich (3) ---

  uebersetzungen.py Grammatik · Übungsfragen "„Kada ___ doći?“ (Wann wirst du kommen?)", Zeile 8997   [gering]
    deutsch : „Kada ___ doći?“ (Wann wirst du kommen?)
    jetzt   : ‘Kada ___ doći?’ (Wanneer kom je?)
    besser  : ‘Kada ___ doći?’ (Wanneer zul je komen?)
    warum   : Die Übung trainiert die Zukunft (ćeš); der Hinweis lässt das Futur weg. Die Vokabel "Wann wirst du kommen?" (Zeile 8095) heißt "Wanneer zul je komen?" – uneinheitlich.

  sprachen.py task.fast, Zeile 1691   [gering]
    deutsch : Richtig! Mit Sonderzeichen: {wort}
    jetzt   : Goed! Met de bijzondere tekens: {wort}
    besser  : Goed! Met de speciale tekens: {wort}
    warum   : Der übliche Begriff ist "speciale tekens"; konto.regel_zeichen und konto.fehler_zeichen benutzen "speciaal teken". Uneinheitlich.

  sprachen.py mail.bestaetigen_betreff, Zeile 1837   [gering]
    deutsch : Willkommen bei Zmaj – bitte bestätige deine Adresse
    jetzt   : Welkom bij Zmaj – nog één klik
    besser  : Welkom bij Zmaj – bevestig je e-mailadres
    warum   : Der Betreff sagt im Deutschen, worum es geht (Adresse bestätigen); die Übersetzung lässt das weg.

--- unnatürlich (3) ---

  sprachen.py task.was_heisst, Zeile 1684   [gering]
    deutsch : Was heißt auf Bosnisch …
    jetzt   : Hoe zeg je dat in het Bosnisch …
    besser  : Hoe zeg je in het Bosnisch …
    warum   : Nach den Punkten folgt das gefragte Wort. Mit "dat" ist der Satz schon abgeschlossen ("Wie sagt man das …"), dann hängt das Wort doppelt dran.

  sprachen.py konto.regeln_titel, Zeile 1827   [gering]
    deutsch : Das Passwort braucht:
    jetzt   : Het wachtwoord heeft nodig:
    besser  : Het wachtwoord moet bevatten:
    warum   : "heeft nodig:" mit nachfolgender Liste ist wörtlich aus dem Deutschen und klingt nicht niederländisch; "moet bevatten:" ist die übliche Formulierung bei Passwortregeln.

  uebersetzungen.py "getrunken haben (w. Mehrz.)" (Wörterbuch der Geschichten), Zeile 9398   [gering]
    deutsch : getrunken haben (w. Mehrz.)
    jetzt   : dronken (v. meervoud)
    besser  : hebben gedronken (v. meervoud)
    warum   : "dronken" ist zwar das Imperfekt von drinken, wird aber zuerst als Adjektiv "betrunken" gelesen. Die Nachbareinträge ("gekocht", "gekookt", "opgestaan") nutzen das Partizip; "hebben gedronken" ist eindeutig.
  uneinheitlicher Begriff: Aufgabe -> opdracht (quest.fertig, task.tippen_weiter), opgave (task.mikro_blockiert, task.gehoert_no, lektion.uebersprungen), vraag (quest.aufgaben)
  uneinheitlicher Begriff: Tagesaufgabe -> dagopdracht (laden.stand), dagtaken (set.agb_text, set.datenschutz_text)
  uneinheitlicher Begriff: Werbung -> reclame (lektion.vollversion, set.agb_text), advertenties (consent.*, set.einwilligung, set.dsgvo_werbung_an, werbung.ohne)
  uneinheitlicher Begriff: Abbrechen -> Stoppen (btn.abbrechen), afbreken (lektion.abbrechen, test.abbrechen)
  uneinheitlicher Begriff: Serienschutz -> reeksbescherming (laden.schutz, serie.schutz, set.serie_schutz), bescherming (set.serie_schutz_sub)
  uneinheitlicher Begriff: Sonderzeichen -> bijzondere tekens (task.fast), speciaal teken (konto.regel_zeichen, konto.fehler_zeichen)
  uneinheitlicher Begriff: Sicherung -> Reservekopie (set.sicherung, AGB, Datenschutz), kopie (set.sicherung_speichern, set.sicherung_einlesen, set.sicherung_ok, set.sicherung_frage)

==============================================================================
## Norwegisch   (11 Funde, Gegenprüfung: fehlt)
==============================================================================

Die norwegische Fassung ist insgesamt sehr gut: natürliches, idiomatisches Bokmål, freundlich-duzender Ton, keine deutschen Reste, alle 340 Oberflächenschlüssel und alle rund 2090 Lernstoff-Einträge vorhanden, Platzhalter und Einzahl|Mehrzahl-Trennungen intakt. Die Kernbegriffe (nivå, leksjon, rekke/rekka, mynter, fullversjon, butikk, liv, rekkebeskyttelse, læringsløypa) werden durchweg einheitlich benutzt; nur bei "historie/fortelling", "rekka/rekken", "annonser/reklame" und "fullført/bestått" gibt es kleine Schwankungen. Echte Fehler sind wenige: der unmögliche s-Genitiv "søsteren mins hus" (dreimal), das nicht standardsprachliche "hvems" (dreimal), das nicht existierende Wort "utillatt" in den Nutzungsbedingungen, "kjenning" als Übersetzung von "Kennung" in der Datenschutzerklärung und der Briefschluss "Jeg er glad i deg, Amina", der die Unterschrift zur Anrede macht. Die App klingt wie eine echte norwegische Lern-App.


--- FALSCHE BEDEUTUNG (4) ---

  sprachen.py set.datenschutz_text (Zeile 2143), Abschnitt 2   [mittel]
    deutsch : Eine Zufallskennung wird beim ersten Start erzeugt.
    jetzt   : <b>En tilfeldig kjenning</b> lages første gang du starter appen.
    besser  : <b>En tilfeldig ID</b> lages første gang du starter appen.
    warum   : "kjenning" bedeutet laut Bokmålsordboka Bekannter, Ahnung/Anflug ("kjenning av land") oder die altnordische Umschreibung – nie eine technische Kennung. Ein norwegischer Leser versteht den Satz nicht. Gemeint ist eine zufällige ID ("en tilfeldig ID" / "en tilfeldig identifikator").

  uebersetzungen.py Geschichte "Liebe Oma, wie geht es dir? …" (Zeile 11516)   [mittel]
    deutsch : Ich liebe dich, deine Amina.
    jetzt   : Jeg er glad i deg, Amina.
    besser  : Jeg er glad i deg. Din Amina.
    warum   : Im Deutschen ist "deine Amina" die Briefunterschrift. Im Norwegischen wird "Jeg er glad i deg, Amina" als Anrede gelesen – als spräche die Oma Amina an. Die Unterschrift muss als "Din Amina" abgesetzt werden, sonst ist der Absender der Briefgeschichte vertauscht.

  uebersetzungen.py "Mein Onkel (Vaterseite) ist Imker." (Zeile 10863)   [gering]
    deutsch : Mein Onkel (Vaterseite) ist Imker.
    jetzt   : Onkelen min er birøkter.
    besser  : Onkelen min (på farssiden) er birøkter.
    warum   : Der Zusatz "Vaterseite" fehlt. Er ist im Lückensatz die einzige Hilfe, um amidža (Onkel väterlicherseits) von daidža zu unterscheiden; ohne ihn ist die Lücke für norwegische Lernende nicht eindeutig lösbar. Die Vokabelliste selbst hat den Zusatz ("onkel (på farssiden)").

  sprachen.py mail.bestaetigen_betreff (Zeile 2198)   [gering]
    deutsch : Willkommen bei Zmaj – bitte bestätige deine Adresse
    jetzt   : Velkommen til Zmaj – ett klikk igjen
    besser  : Velkommen til Zmaj – bekreft adressen din
    warum   : Der Betreff sagt etwas anderes als das Deutsche: "ett klikk igjen" (noch ein Klick) statt der Aufforderung, die Adresse zu bestätigen. Der Zweck der Mail geht im Betreff verloren.

--- Grammatik/Rechtschreibung (3) ---

  uebersetzungen.py "das Haus meiner Schwester" (Zeile 10217), ebenso in der Grammatik-Erklärung Zeile 11030 und der Übungsfrage Zeile 11223   [hoch]
    deutsch : das Haus meiner Schwester
    jetzt   : søsteren mins hus
    besser  : huset til søsteren min
    warum   : Ein s-Genitiv an das nachgestellte Possessiv ("mins") gibt es im Norwegischen nicht; die Form ist schlicht ungrammatisch. Besitz drückt man mit "huset til …" (oder umgangssprachlich "søstera mi sitt hus") aus. Der Fehler steht an drei Stellen: Vokabel, Genitiv-Erklärung («kuća moje sestre» (søsteren mins hus)) und Übungsfrage («Kuća moje ___.» (Søsteren mins hus.)).

  uebersetzungen.py "Wessen? Woher? Ohne was? Nach Mengen und vielen Präpositionen." (Zeile 9626), "Wessen?" (Zeile 10043), Genitiv-Erklärung Zeile 11028   [mittel]
    deutsch : Wessen?
    jetzt   : Hvems?
    besser  : Hvem sin?
    warum   : "hvems" ist eine Soziolekt-/Umgangsform und wurde aus der Bokmålsordboka gestrichen; standardsprachlich heißt es "hvem sin" (bzw. "hvem sitt/sine"). Betrifft den Level-Tipp ("Hvems? Hvorfra? …"), das Fragewort und die Genitiv-Erklärung ("Genitiv svarer på «hvems?» …").

  sprachen.py set.agb_text (Zeile 2141), Abschnitt 6   [mittel]
    deutsch : 6. Nutzungsrechte und unzulässige Nutzung
    jetzt   : 6. Bruksrett og utillatt bruk
    besser  : 6. Bruksrett og ikke tillatt bruk
    warum   : "utillatt" steht nicht in der Bokmålsordboka (0 Treffer); das Wort gibt es nicht. Korrekt sind "ikke tillatt bruk" oder "utillatelig bruk".

--- veraltet (1) ---

  sprachen.py set.datenschutz_text (Zeile 2143), Abschnitt 5   [gering]
    deutsch : Du kannst jede Sprechaufgabe überspringen – tippe auf „Kann jetzt nicht sprechen“.
    jetzt   : Du kan hoppe over enhver taleoppgave – til det finnes en egen knapp.
    besser  : Du kan hoppe over enhver taleoppgave – trykk på «Det går ikke å snakke nå, hopp over».
    warum   : Das Deutsche nennt den Knopf beim Namen, die Übersetzung sagt nur allgemein "dafür gibt es einen eigenen Knopf". Passt inhaltlich zu einer anderen Fassung. Hinweis: Auch der deutsche Text nennt einen Knopfnamen, den es in der Oberfläche so nicht gibt (task.sprechen_skip heißt "Sprechen ist gerade nicht möglich, überspringen"); der norwegische Vorschlag verwendet den tatsächlichen norwegischen Knopftext.

--- uneinheitlich (2) ---

  sprachen.py quest.geschichte (Zeile 1945)   [gering]
    deutsch : Eine Geschichte fehlerfrei
    jetzt   : En historie uten feil
    besser  : En fortelling uten feil
    warum   : Überall sonst heißen die Geschichten "fortellinger" (Tab, Überschrift, Zähler, Level-Hinweis). Nur die Tagesaufgabe sagt "historie".

  sprachen.py laden.schutz_sub (Zeile 1951)   [gering]
    deutsch : Deckt einen ausgelassenen Tag ab, damit die Serie bleibt.
    jetzt   : Dekker én dag du hopper over, så rekken ikke ryker.
    besser  : Dekker én dag du hopper over, så rekka ikke ryker.
    warum   : Die Lernserie heißt sonst durchgehend "rekka" (a-Form: "Rekka di", "reddet rekka di"); hier einmal "rekken". Beide Formen sind zulässig, aber innerhalb einer App sollte es eine sein.

--- unnatürlich (1) ---

  uebersetzungen.py "Freundin" (Zeile 9785)   [gering]
    deutsch : Freundin
    jetzt   : venn (kvinne)
    besser  : venninne
    warum   : Für die weibliche Freundin gibt es im Norwegischen das ganz gebräuchliche Wort "venninne"; "venn (kvinne)" ist eine Umschreibung, die kein Muttersprachler als Vokabel angeben würde.
  uneinheitlicher Begriff: Geschichte -> fortelling / fortellinger (Tab, Überschrift, Zähler, Level-Hinweis), historie (nur quest.geschichte)
  uneinheitlicher Begriff: Serie (Lernserie) -> rekka / rekke (fast überall), rekken (laden.schutz_sub)
  uneinheitlicher Begriff: Werbung -> annonser (consent, Einstellungen, AGB, Datenschutz, werbung.*), reklame (lektion.vollversion)
  uneinheitlicher Begriff: Bestanden (Level/Test) -> fullført (zustand.bestanden, level.test_bestanden, pfad.summary, test.alles_geschafft), bestått (test.bestanden, test.sektion_fertig, test.durchgefallen, level.note_zu)
  uneinheitlicher Begriff: Tagesaufgabe -> dagsoppdrag (laden.stand), oppdrag (quest.fertig), dagsoppgaver (set.agb_text, set.datenschutz_text)
  uneinheitlicher Begriff: Serienschutz -> rekkebeskyttelse (laden.schutz, set.serie_schutz, serie.schutz, Datenschutz), beskyttelse (set.serie_schutz_sub, verkürzt)
  uneinheitlicher Begriff: Level -> nivå (durchgehend einheitlich)
  uneinheitlicher Begriff: Lektion -> leksjon (durchgehend einheitlich)
  uneinheitlicher Begriff: Münzen -> mynter (durchgehend einheitlich)
  uneinheitlicher Begriff: Vollversion -> fullversjon (durchgehend einheitlich)
  uneinheitlicher Begriff: Laden -> butikk (durchgehend einheitlich)
  uneinheitlicher Begriff: Leben -> liv (durchgehend einheitlich)
  uneinheitlicher Begriff: Lernpfad -> læringsløypa (durchgehend einheitlich)
  uneinheitlicher Begriff: Sektion -> del (durchgehend einheitlich)

==============================================================================
## Schwedisch   (12 Funde, Gegenprüfung: fehlt)
==============================================================================

Die schwedische Fassung ist insgesamt sehr gut: idiomatisch, freundlich, durchgehend geduzt, mit sinnvollen Anpassungen für schwedische Lernende (z.B. Hinweise auf en-/ett-Wörter, BIFF-Regel bei Nebensätzen). Alle Schlüssel, Platzhalter und Einzahl|Mehrzahl-Trennungen stimmen, deutsche Reste gibt es keine. Die echten Fehler sind wenige: ein Grammatikfehler bei „var {tage} dag“, „åktur“ für Fahrt (bedeutet Vergnügungsfahrt), die unnatürliche Wendung „betala i avbetalningar“ sowie einige Begriffs-Inkonsistenzen (Svitskydd/Serieskydd, hjärtan/liv, utveckling/framsteg, Synpunkter/Återkoppling). Es klingt wie eine echte schwedische App.


--- FALSCHE BEDEUTUNG (3) ---

  uebersetzungen.py "Fahrt", Zeile 6042   [mittel]
    deutsch : Fahrt
    jetzt   : åktur
    besser  : resa / färd
    warum   : Laut Svenska Akademiens ordbok ist „åktur“ eine „kortare resa med fordon vanligen för nöjes skull“ – eine Spritztour. Im Level Reisen & Verkehr (Bus, Bahn, zwölf Stunden nach Bosnien) ist „resa“ gemeint; der Beispielsatz daneben übersetzt „Fahrt“ auch schon mit „resan“.

  uebersetzungen.py "Sparen / Ersparnisse", Zeile 6214   [gering]
    deutsch : Sparen / Ersparnisse
    jetzt   : sparande
    besser  : spara / besparingar
    warum   : „Ersparnisse“ (das Ersparte) heißt „besparingar“; „sparande“ ist nur das Sparen als Tätigkeit. Die zweite Hälfte der Bedeutung fehlt.

  uebersetzungen.py "Baščaršija (Altstadt)", Zeile 7220   [gering]
    deutsch : Baščaršija (Altstadt)
    jetzt   : Baščaršija (den gamla basargatan)
    besser  : Baščaršija (gamla stan, den gamla basaren)
    warum   : Baščaršija ist das ganze alte Basarviertel von Sarajevo, keine einzelne Gasse; „basargatan“ (Basargasse) ist sachlich zu eng, und „Altstadt“ heißt „gamla stan“.

--- Grammatik/Rechtschreibung (1) ---

  sprachen.py set.serie_schutz_sub, Zeile 1410   [mittel]
    deutsch : Ein Schutz rettet deine Serie, wenn du einen Tag auslässt. Alle {tage} Tage wächst ein neuer nach, höchstens {max} auf einmal.
    jetzt   : Ett skydd räddar din serie när du hoppar över en dag. Ett nytt växer fram var {tage} dag, som mest {max} åt gången.
    besser  : Ett skydd räddar din serie när du hoppar över en dag. Ett nytt växer fram var {tage}:e dag, som mest {max} åt gången.
    warum   : „var 3 dag“ ist kein Schwedisch; bei Ziffern braucht die Ordnungszahl das Suffix „:e“ (var 3:e dag = alle drei Tage).

--- veraltet (1) ---

  uebersetzungen.py "„Idem s ___.“" Zeile 6713, "„Kahva s ___.“" Zeile 6715, "s/sa, pod, …" Zeile 6621, "s/sa + Instrumental" Zeile 6811   [gering]
    deutsch : „Idem s ___.“ (Ich gehe mit dem Bruder.) / s/sa, pod, iznad, ispod, između, pred, za (hinter) / s/sa + Instrumental: + om.
    jetzt   : ”Idem sa ___.” (Jag går med min bror.) / sa, pod, iznad, ispod, između, pred, za (bakom) / sa + instrumentalis: + om.
    besser  : ”Idem s ___.” (Jag går med min bror.) / s/sa, pod, iznad, ispod, između, pred, za (bakom) / s/sa + instrumentalis: + om.
    warum   : Die deutsche Fassung wurde auf „s/sa“ bzw. „Idem s“ / „Kahva s“ umgestellt, die schwedische zeigt noch das ältere „sa“. Betrifft zwar den bosnischen Teil, ist aber ein Rest einer älteren Fassung – Übungstext und Tabelle weichen vom Deutschen ab.

--- uneinheitlich (5) ---

  sprachen.py laden.schutz, Zeile 1232   [mittel]
    deutsch : Serienschutz
    jetzt   : Svitskydd
    besser  : Serieskydd
    warum   : Überall sonst (serie.schutz, set.serie_schutz, Datenschutztext, serie.gerettet) heißt es „serieskydd“ und die Serie heißt „serie“. Im Laden steht plötzlich „svit“, ein anderer Begriff für dieselbe Sache.

  sprachen.py laden.schutz_sub, Zeile 1233   [mittel]
    deutsch : Deckt einen ausgelassenen Tag ab, damit die Serie bleibt.
    jetzt   : Täcker en missad dag så att sviten lever vidare.
    besser  : Täcker en missad dag så att serien lever vidare.
    warum   : „sviten“ statt „serien“; die Lernserie heißt in der ganzen App „serie“.

  sprachen.py laden.herz_sub, Zeile 1231 (ebenso werbung.lohn_laeuft 1529, werbung.lohn_abholen 1530, set.agb_text 1422 „obegränsat med liv“, set.datenschutz_text 1424 „mynt, liv och serieskydd“)   [gering]
    deutsch : Ein Leben sofort zurück, statt zwei Stunden zu warten.
    jetzt   : Ett liv tillbaka direkt, utan två timmars väntan.
    besser  : Ett hjärta tillbaka direkt, utan två timmars väntan.
    warum   : „Leben“ ist in der Oberfläche durchgehend als „hjärtan“ übersetzt (leben.*, lektion.*, stat.leben, level.keine_leben). An diesen Stellen heißt es „liv“ – zwei Wörter für dieselbe Sache.

  sprachen.py set.profil_sub, Zeile 1388 (ebenso set.konto 1390, set.beenden_frage 1428, set.konto_loeschen_sub 1463, set.agb_text 1422, set.datenschutz_text 1424)   [gering]
    deutsch : Fortschritt, Lernserie und Leben gehören zu diesem Profil.
    jetzt   : Utveckling, serie och hjärtan hör till den här profilen.
    besser  : Framsteg, serie och hjärtan hör till den här profilen.
    warum   : „Fortschritt/Lernstand“ ist in beenden.text, set.sicherung_sub und set.sicherung_frage „framsteg“, hier und in den Rechtstexten „utveckling“. „Utveckling“ ist eher „Entwicklung“; für Lernfortschritt ist „framsteg“ das natürliche Wort.

  sprachen.py set.agb_text, Zeile 1422 (Abschnitt 4)   [gering]
    deutsch : Wenn dir ein Fehler auffällt, schreib uns über das Feedback-Feld in den Einstellungen.
    jetzt   : Hittar du ett fel, skriv till oss via återkopplingsrutan i inställningarna.
    besser  : Hittar du ett fel, skriv till oss under Synpunkter i inställningarna.
    warum   : Der Einstellungsabschnitt heißt in der App „Synpunkter“ (set.feedback). Der Verweis auf „återkopplingsrutan“ führt ins Leere; auch der Datenschutztext nennt den Abschnitt „Återkoppling“.

--- unnatürlich (2) ---

  uebersetzungen.py "Kann ich in Raten zahlen?", Zeile 6224   [mittel]
    deutsch : Kann ich in Raten zahlen?
    jetzt   : Kan jag betala i avbetalningar?
    besser  : Kan jag delbetala?
    warum   : „betala i avbetalningar“ sagt kein Schwede; die üblichen Wendungen sind „delbetala“ oder „köpa på avbetalning“.

  uebersetzungen.py "Beispiele", Zeile 6564   [gering]
    deutsch : Beispiele
    jetzt   : Exempel (flera)
    besser  : Exempel
    warum   : Das ist eine Tabellenüberschrift, kein Vokabeleintrag; „(flera)“ hat dort nichts verloren. Schwedisch hat für Einzahl und Mehrzahl dieselbe Form „exempel“.
  uneinheitlicher Begriff: Leben -> hjärtan (leben.*, lektion.*, stat.leben, level.keine_leben), liv (laden.herz_sub, werbung.lohn_laeuft, werbung.lohn_abholen, AGB, Datenschutz)
  uneinheitlicher Begriff: Serienschutz -> serieskydd (serie.schutz, set.serie_schutz, serie.gerettet, Datenschutz), Svitskydd (laden.schutz)
  uneinheitlicher Begriff: Lernserie / Serie -> serie (fast überall), svit (laden.schutz_sub)
  uneinheitlicher Begriff: Fortschritt / Lernstand -> framsteg (beenden.text, set.sicherung_sub, set.sicherung_frage, pfad/stat), utveckling (set.profil_sub, set.konto, set.beenden_frage, set.konto_loeschen_sub, AGB, Datenschutz)
  uneinheitlicher Begriff: Feedback -> Synpunkter (set.feedback, set.feedback_platzhalter), återkoppling (AGB „återkopplingsrutan“, Datenschutz „4. Återkoppling“)
  uneinheitlicher Begriff: Werbung -> annonser (consent.*, set.einwilligung, set.werbung_*, werbung.*, dsgvo_werbung_an), reklam (set.agb_text Abschnitte 5 und 7)
  uneinheitlicher Begriff: lernen (Lernstoff) -> lära sig (lernen, ich lerne, erlernen), plugga (ich habe gelernt, Ich werde lernen, Ich möchte lernen, Ich lerne jeden Tag Bosnisch, Geschichte 9)
  uneinheitlicher Begriff: Level -> nivå (durchgehend)
  uneinheitlicher Begriff: Lektion -> lektion (durchgehend)
  uneinheitlicher Begriff: Münzen -> mynt (durchgehend)
  uneinheitlicher Begriff: Vollversion -> fullversion (durchgehend)
  uneinheitlicher Begriff: Laden -> butik (durchgehend)
  uneinheitlicher Begriff: Lernpfad -> lärstigen (durchgehend)
  uneinheitlicher Begriff: Sektion -> avsnitt (durchgehend)