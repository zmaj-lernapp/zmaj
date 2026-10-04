# Übersetzungen – Kandidaten für die Muttersprachler-Prüfung

Stand 04.10.2026. KI-Durchsicht aller 1.728 Vokabeln und 300 Sätze in `data/`
für en, tr, sv, nl, nb, da und fr, jeweils gegen das Deutsche **und** das
Bosnische gelesen. Zusätzlich maschinell geprüft: deutsche Reste (gleiche
Zeichenfolge wie `de`), fehlende Genus-Hinweise bei `(m/w)`-Karten und
Kollisionen, also zwei verschiedene Karten mit derselben Übersetzung.

Vorgehen: Erst wurden Verdachtsfälle gesammelt, dann wurde jeder Fund einmal
zu widerlegen versucht (Ist das Bosnische genauso doppeldeutig? Ist die Form
regional doch üblich? Hat der Bericht vom 18.09.2026 das schon erfasst?).
Nur was das überstanden hat, steht hier. Funde, die schon im
[Prüfbericht vom 18.09.](uebersetzungen-pruefbericht-2026-09-18.md) stehen
und noch nicht umgesetzt sind (z. B. nl „zaak“, nb „Hvems?“, nb „søsteren mins
hus“, da „Om mandagen“), werden nicht wiederholt.

**Das ist keine Muttersprachler-Prüfung.** Je Sprache entscheidet jemand,
der sie spricht. Die Spalte *Sicherheit* sagt nur, wie sicher die KI ist.
Fertige Kommentare für die Sprach-Issues liegen unter `issue-kommentare/`.

Hinweise zur Umsetzung:

- Korrekturen gehören in `uebersetzungen.py`, danach `python3 daten_exportieren.py`.
  Kein Fund verlangt, ein deutsches `de` zu ändern (Regel 1, Wort-IDs).
- Sprachübergreifend: Die Karte `(antwort darauf):Alejkumu selam` hat in allen
  sieben Sprachen nur „(reply to this)“. Steht sie allein in einer Übung, fehlt
  der Bezug. Vorschlag in jeder Sprache: „Antwort auf ‚Selam alejkum‘“.
- Nebenbefund außerhalb des Auftrags: Rund 30 deutsche Schlüssel schreiben
  Umlaute als ae/oe/ue/ss (`Baer`, `Kueken / Haehnchen`, `Hoehle`, `beissen`,
  `Danke fuer die Einladung`, `Hallo (neutral, ueberall)` …) oder lassen
  Háčeks weg (`Hurmasica`, `Teferic`, `Insallah`). Das zu ändern
  setzt den Lernstand dieser Wörter zurück (Regel 1) und gehört deshalb in
  eine eigene, bewusste Entscheidung, nicht in eine Übersetzungskorrektur.

## Übersicht

| Sprache | Funde | davon hoch | davon mittel |
|---|---|---|---|
| Englisch (en) | 9 | 4 | 5 |
| Türkisch (tr) | 6 | 1 | 5 |
| Schwedisch (sv) | 7 | 2 | 5 |
| Niederländisch (nl) | 10 | 3 | 7 |
| Norwegisch (Bokmål) (nb) | 8 | 3 | 5 |
| Dänisch (da) | 11 | 5 | 6 |
| Französisch (fr) | 8 | 1 | 7 |
| **Summe** | **59** | | |

## Englisch (en)

| ID | Level | bs | de | jetzt | Vorschlag | Grund | Sicherheit |
|---|---|---|---|---|---|---|---|
| `verkäufer:prodavač` | einkauf_orte | prodavač | Verkäufer | seller | salesperson / shop assistant | Kollidiert mit „Verkäufer (Vertragspartei)“ = „seller“ – zwei Karten mit gleicher Vorgabe. Der Beruf heißt im Englischen salesperson/shop assistant (so auch die genus-Karte „salesperson“ und die weibliche Form „saleswoman“). | hoch |
| `familie:porodica` | familie | porodica | Familie | Family | family | Einziges großgeschriebenes Substantiv der Wortliste; alle anderen Nomen sind klein. | hoch |
| `s0193` | obst | Moja mama voli kruške. | Meine Mama mag Birnen. | My mum likes pears. | My mom likes pears. | Britisch „mum“; die Vokabel „mama“ heißt in der App „mom“, die Rechtschreibung im Lernstoff ist sonst amerikanisch. | hoch |
| `s0239` | putzen | Komšinica zvoni na vrata. | Die Nachbarin klingelt an der Tür. | The neighbour is ringing the doorbell. | The neighbor is ringing the doorbell. | Britisch „neighbour“, die Vokabeln schreiben „neighbor“ / „neighbor (f)“. | hoch |
| `kennzeichen (auto):registracija` | auto_werkstatt | registracija | Kennzeichen (Auto) | number plate | license plate | „number plate“ ist britisch; sonst amerikanisch (trash can, gas station, parking lot). | mittel |
| `stockwerk:sprat` | immobilien | sprat | Stockwerk | storey | floor | „storey“ ist britische Schreibung und im Alltag selten; „floor“ ist das übliche Wort. | mittel |
| `gehen wir einen kaffee trinken:Idemo na kahvu` | essen_gehen | Idemo na kahvu | Gehen wir einen Kaffee trinken | Let us go for a coffee | Let's go for a coffee | „Let us go“ klingt feierlich; die App schreibt bei „Hajmo!“ schon „Let's go!“. | mittel |
| `s0242` | technik | Gdje je moj alat? | Wo ist mein Werkzeug? | Where is my tool? | Where are my tools? | „alat“/„Werkzeug“ ist ein Sammelbegriff; „Where is my tool?“ klingt nach einem einzelnen Gerät. | mittel |
| `(antwort darauf):Alejkumu selam` | kennenlernen | Alejkumu selam | (Antwort darauf) | (reply to this) | reply to “Selam alejkum” | Bezug fehlt: Die Karte steht in Übungen allein, „(Antwort darauf)“ zeigt dann auf nichts. Nur die Übersetzung ändern, der deutsche Schlüssel bleibt. | mittel |

## Türkisch (tr)

| ID | Level | bs | de | jetzt | Vorschlag | Grund | Sicherheit |
|---|---|---|---|---|---|---|---|
| `verkäufer (vertragspartei):prodavac` | immobilien | prodavac | Verkäufer (Vertragspartei) | satıcı | satıcı (sözleşme tarafı) | Kollidiert mit „Verkäufer“ (prodavač) = „satıcı“ – zwei Karten mit gleicher Vorgabe. Die Vertragspartei braucht einen Zusatz. | hoch |
| `familie:porodica` | familie | porodica | Familie | Aile | aile | Großgeschrieben, alle anderen Substantive sind klein. | mittel |
| `mama:mama` | familie | mama | Mama | anneciğim | anne (sevgiyle: anneciğim) | „anneciğim“ ist eine Anrede („meine liebe Mama“), kein Stichwort. Als Karte wirkt es seltsam; ebenso „babacığım“ bei babo. | mittel |
| `die hälfte:pola` | mengen | pola | die Hälfte | yarım | yarı / yarısı | „yarım“ ist das Adjektiv (yarım kilo); das Nomen „die Hälfte“ ist „yarı“/„yarısı“. | mittel |
| `s0296` | kulturlevel | Nana svira harmoniku. | Oma spielt Akkordeon. | Nenem akordeon çalıyor. | Ninem akordeon çalıyor. | Uneinheitlich: Vokabel „nana“ = „nine“, Satz s0077 „Ninem“, aber s0296 „Nenem“ und s0300 „neneme“. Beides ist Türkisch, aber eine Form wählen. | mittel |
| `(antwort darauf):Alejkumu selam` | kennenlernen | Alejkumu selam | (Antwort darauf) | (buna verilen cevap) | (“Selam alejkum”a verilen cevap) | Bezug fehlt: Die Karte steht in Übungen allein, „(Antwort darauf)“ zeigt dann auf nichts. Nur die Übersetzung ändern, der deutsche Schlüssel bleibt. | mittel |

## Schwedisch (sv)

| ID | Level | bs | de | jetzt | Vorschlag | Grund | Sicherheit |
|---|---|---|---|---|---|---|---|
| `verkäufer:prodavač` | einkauf_orte | prodavač | Verkäufer | säljare | expedit / butiksbiträde | Kollidiert mit „Verkäufer (Vertragspartei)“ = „säljare“. Für den Beruf im Laden nutzt die App sonst „expedit“ (genus-Karte, „expedit (kvinna)“). | hoch |
| `familie:porodica` | familie | porodica | Familie | Familj | familj | Großgeschrieben, alle anderen Substantive sind klein. | hoch |
| `somun (fladenbrot zu cevapi):somun` | bosnisch_essen | somun | Somun (Fladenbrot zu Cevapi) | somun (tunnbröd till ćevapi) | somun (pitaliknande bröd till ćevapi) | „tunnbröd“ ist dünnes Weichbrot; somun ist ein dickes, luftiges Hefefladenbrot. | mittel |
| `fladenbrot (rund):pogača` | vorrat | pogača | Fladenbrot (rund) | tunnbröd (runt) | runt bröd (pogača) | Wie oben: pogača ist ein dicker runder Laib, kein „tunnbröd“. Satz s0210 („tunnbrödet“) entsprechend. | mittel |
| `s0257` | einkauf_orte | Jabuke su na akciji. | Die Äpfel sind im Angebot. | Äpplena är på erbjudande. | Det är extrapris på äpplena. | „på erbjudande“ ist kein übliches Schwedisch für „im Angebot“; man sagt „extrapris“ oder „på rea“. | mittel |
| `ich bitte um entschuldigung:Molim za izvinjenje` | formell | Molim za izvinjenje | Ich bitte um Entschuldigung | Jag vill gärna be om ursäkt | Jag vill be om ursäkt | „gärna“ (= gern) passt nicht zu einer Entschuldigung und klingt merkwürdig. | mittel |
| `(antwort darauf):Alejkumu selam` | kennenlernen | Alejkumu selam | (Antwort darauf) | (svar på det) | (svar på ”Selam alejkum”) | Bezug fehlt: Die Karte steht in Übungen allein, „(Antwort darauf)“ zeigt dann auf nichts. Nur die Übersetzung ändern, der deutsche Schlüssel bleibt. | mittel |

## Niederländisch (nl)

| ID | Level | bs | de | jetzt | Vorschlag | Grund | Sicherheit |
|---|---|---|---|---|---|---|---|
| `blätterteig:jufka` | vorrat | jufka | Blätterteig | bladerdeeg | filodeeg (yufka) | jufka ist Yufka/Filo, kein Blätterteig. „bladerdeeg“ ist Butter-Blätterteig – die anderen Sprachen haben „filo“. Der deutsche Schlüssel ist hier selbst ungenau, die Übersetzung sollte dem Bosnischen folgen. | hoch |
| `burek (blaetterteigrolle mit fleisch):burek` | bosnisch_essen | burek | Burek (Blaetterteigrolle mit Fleisch) | burek (bladerdeegrol met vlees) | burek (filodeegrol met vlees) | Wie oben: burek wird aus jufka/Filo gemacht, nicht aus bladerdeeg. | hoch |
| `familie:porodica` | familie | porodica | Familie | Familie | familie | Großgeschrieben und damit identisch mit dem deutschen Schlüssel; Substantive sind sonst klein. | hoch |
| `verkäufer (vertragspartei):prodavac` | immobilien | prodavac | Verkäufer (Vertragspartei) | verkoper | verkoper (contractpartij) | Kollidiert mit „Verkäufer“ (prodavač) = „verkoper“ – zwei Karten mit gleicher Vorgabe. | mittel |
| `wohnung:stan` | zuhause | stan | Wohnung | woning | appartement / flat | „woning“ ist jede Wohnstätte (auch ein Haus); stan ist die Wohnung im Mehrfamilienhaus. | mittel |
| `speiseöl:ulje` | vorrat | ulje | Speiseöl | olie (om te koken) | bakolie / spijsolie | „olie (om te koken)“ ist eine Umschreibung, kein Wort. | mittel |
| `biene:pčela` | wetter | pčela | Biene | honingbij | bij | „honingbij“ ist der Fachbegriff; im Alltag und für „Biene“ ist „bij“ das Wort. | mittel |
| `ich freue mich:Radujem se` | reflexiv | Radujem se | Ich freue mich | Ik verheug me | Ik ben blij | „Ik verheug me“ ohne „erop/erover“ wirkt unvollständig. | mittel |
| `s0029` | familie | Moj amidža je pčelar. | Mein Onkel (Vaterseite) ist Imker. | Mijn oom is imker. | Mijn oom (van vaderskant) is imker. | Die Vaterseite (amidža) geht verloren; die Vokabel hat „oom (van vaderskant)“. In nb wurde dasselbe schon nachgetragen. | mittel |
| `(antwort darauf):Alejkumu selam` | kennenlernen | Alejkumu selam | (Antwort darauf) | (antwoord daarop) | (antwoord op ‘Selam alejkum’) | Bezug fehlt: Die Karte steht in Übungen allein, „(Antwort darauf)“ zeigt dann auf nichts. Nur die Übersetzung ändern, der deutsche Schlüssel bleibt. | mittel |

## Norwegisch (Bokmål) (nb)

| ID | Level | bs | de | jetzt | Vorschlag | Grund | Sicherheit |
|---|---|---|---|---|---|---|---|
| `guten appetit:Prijatno` | basics | Prijatno | Guten Appetit | Vel bekomme | God appetitt! | „Vel bekomme“ sagt man auf Norwegisch nach dem Essen (Antwort auf „takk for maten“), nicht davor. | hoch |
| `familie:porodica` | familie | porodica | Familie | Familie | familie | Großgeschrieben und damit identisch mit dem deutschen Schlüssel; Substantive sind sonst klein. | hoch |
| `verkäufer:prodavač` | einkauf_orte | prodavač | Verkäufer | selger | butikkselger / ekspeditør | Kollidiert mit „Verkäufer (Vertragspartei)“ = „selger“; die weibliche Form heißt bereits „butikkselger (kvinne)“, die genus-Karte „ekspeditør“. | hoch |
| `baum:drvo` | wetter | drvo | Baum | tre (plante) | tre (et tre, trær) | „(plante)“ als Zusatz wirkt ungewöhnlich; die Mehrdeutigkeit mit der Zahl drei löst man üblicherweise mit Artikel/Plural. | mittel |
| `cremeschnitte:šampita` | vorrat | šampita | Cremeschnitte | napoleonskake | šampita (kake med marengskrem) | „napoleonskake“ ist Blätterteig mit Vanillecreme (eher kremšnita); šampita hat eine Baiser-/Marengscreme. Andere Sprachen: „meringue“, „maräng“. | mittel |
| `decke (bettdecke):deka` | kueche_bad | deka | Decke (Bettdecke) | pledd | teppe | „pledd“ ist eine Sofadecke/Plaid; der Satz s0235 nutzt für dieselbe deka „Teppet“. Einheitlich „teppe“. | mittel |
| `s0271` | essen_gehen | Ovo je jako ukusno. | Das ist sehr lecker. | Dette er veldig velsmakende. | Dette er veldig godt. | „velsmakende“ ist papiersprachlich; zu Essen sagt man „godt“. | mittel |
| `(antwort darauf):Alejkumu selam` | kennenlernen | Alejkumu selam | (Antwort darauf) | (svar på det) | (svar på «Selam alejkum») | Bezug fehlt: Die Karte steht in Übungen allein, „(Antwort darauf)“ zeigt dann auf nichts. Nur die Übersetzung ändern, der deutsche Schlüssel bleibt. | mittel |

## Dänisch (da)

| ID | Level | bs | de | jetzt | Vorschlag | Grund | Sicherheit |
|---|---|---|---|---|---|---|---|
| `dieser / diese / dieses:ovaj / ova / ovo` | genus | ovaj / ova / ovo | dieser / diese / dieses | denne (h/hu/i) | denne / dette (h/hu/i) | Die Neutrumform „dette“ fehlt, obwohl die Karte drei Genera auszeichnet. | hoch |
| `jener / jene / jenes:onaj / ona / ono` | genus | onaj / ona / ono | jener / jene / jenes | den dér (h/hu/i) | den der / det der (h/hu/i) | Neutrum „det der“ fehlt; wie bei „dieser“. | hoch |
| `s0029` | familie | Moj amidža je pčelar. | Mein Onkel (Vaterseite) ist Imker. | Min onkel er biavler. | Min farbror er biavler. | Dänisch hat das genaue Wort (die Vokabel amidža heißt „farbror“); „onkel“ verliert genau das, was der Satz lehrt. | hoch |
| `verkäufer:prodavač` | einkauf_orte | prodavač | Verkäufer | sælger | ekspedient | Kollidiert mit „Verkäufer (Vertragspartei)“ = „sælger“; die weibliche Form heißt „ekspeditrice“, die genus-Karte „ekspedient“. | hoch |
| `familie:porodica` | familie | porodica | Familie | Familie | familie | Großgeschrieben und damit identisch mit dem deutschen Schlüssel; Substantive sind sonst klein. | hoch |
| `mama:mama` | familie | mama | Mama | mor | mor (mama) | Jetzt identisch mit „Mutter“ = „mor“: zwei Karten mit gleicher Vorgabe. (Die Korrektur mormor → mor vom 18.09. hat das erzeugt.) | mittel |
| `anrede: herr!:gospodine!` | faelle4 | gospodine! | Anrede: Herr! | hr.! (tiltale) | min herre! (tiltale) | Die Abkürzung „hr.!“ kann man nicht als Anrede rufen. | mittel |
| `ofen (heizofen):peć` | technik | peć | Ofen (Heizofen) | kakkelovn (ovn til varme) | brændeovn / ovn (til opvarmning) | „kakkelovn“ ist ein historischer Kachelofen; peć ist der gewöhnliche (Holz-)Ofen. | mittel |
| `scharfe paprika:ljuta paprika` | gemuese | ljuta paprika | scharfe Paprika | stærk peberfrugt | chili | „stærk peberfrugt“ sagt man nicht; scharfe Schoten heißen „chili“. | mittel |
| `s0235` | kueche_bad | Deka je na kauču. | Die Bettdecke ist auf dem Sofa. | Dynen ligger på sofaen. | Tæppet ligger på sofaen. | „Dynen“ (Federbett) passt nicht zur Vokabel deka = „tæppe (til sengen)“; uneinheitlich. | mittel |
| `(antwort darauf):Alejkumu selam` | kennenlernen | Alejkumu selam | (Antwort darauf) | (svar på det) | (svar på »Selam alejkum«) | Bezug fehlt: Die Karte steht in Übungen allein, „(Antwort darauf)“ zeigt dann auf nichts. Nur die Übersetzung ändern, der deutsche Schlüssel bleibt. | mittel |

## Französisch (fr)

| ID | Level | bs | de | jetzt | Vorschlag | Grund | Sicherheit |
|---|---|---|---|---|---|---|---|
| `familie:porodica` | familie | porodica | Familie | La famille | famille | Großgeschrieben und mit Artikel; kein anderes Substantiv der Liste hat einen Artikel. | hoch |
| `torte:torta` | feiern | torta | Torte | gâteau | gâteau à la crème (torta) | Kollidiert mit „Kuchen“ = „gâteau“: zwei Karten mit gleicher Vorgabe. Die Korrektur „tarte“ → „gâteau“ hat den Zusatz verloren. | mittel |
| `sack:vreća` | essen_gehen | vreća | Sack | sac | grand sac / sac de jute | Kollidiert mit „Tasche“ = „sac“. | mittel |
| `am montag gehe ich zur arbeit:U ponedjeljak idem na posao` | saetze | U ponedjeljak idem na posao | Am Montag gehe ich zur Arbeit | Le lundi, je vais au travail | Lundi, je vais au travail. | „Le lundi“ heißt „montags, jeden Montag“ (bosnisch „ponedjeljkom“); „U ponedjeljak“ ist ein bestimmter Montag. Satz s0075 identisch. | mittel |
| `s0242` | technik | Gdje je moj alat? | Wo ist mein Werkzeug? | Où est mon outil ? | Où sont mes outils ? | „alat“ ist ein Sammelbegriff (Werkzeug); „mon outil“ ist ein einzelnes Gerät. | mittel |
| `kündigung:otkaz` | arbeitsvertrag | otkaz | Kündigung | licenciement | résiliation (licenciement / démission) | „licenciement“ ist nur die Kündigung durch den Arbeitgeber; otkaz/Kündigung gilt für beide Seiten. | mittel |
| `schweizer / schweizerin:Švicarac / Švicarka` | nationalitaeten | Švicarac / Švicarka | Schweizer / Schweizerin | Suisse / Suissesse | Suisse / Suisse | „Suissesse“ gilt als veraltet; heute sagt man „une Suisse“. | mittel |
| `(antwort darauf):Alejkumu selam` | kennenlernen | Alejkumu selam | (Antwort darauf) | (réponse à cela) | (réponse à « Selam alejkum ») | Bezug fehlt: Die Karte steht in Übungen allein, „(Antwort darauf)“ zeigt dann auf nichts. Nur die Übersetzung ändern, der deutsche Schlüssel bleibt. | mittel |
