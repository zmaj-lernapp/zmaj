# -*- coding: utf-8 -*-
"""
varianten.py  –  andere bosnische Wörter, die beim Tippen genauso gelten

Seit dem 12.11.2026. Die App nahm beim Tippen nur das Wort selbst, sein
"auch" und Wörter mit genau derselben Bedeutung (annehmbar() in
web/index.html). Im Lückensatz galt nicht einmal das "auch" des Wortes:
„Voda je u ___.“ nahm nur flaši, boci war falsch und kostete ein Leben.
Ajdin wollte das für die ganze App: „die ganze app nochmal danach
kontrollieren“. Die Suche danach (Korpus bs-Web, Zahlen unter "beleg") hat
die Paare in eindeutig und fraglich geteilt. Zuerst standen hier nur die
eindeutigen (Tabelle 2a und 2b in Release/Wortschatz/varianten_2026-11-13.md).
Seit dem 14.11.2026 auch die fraglichen aus Tabelle 2c, Ajdin (Prüfbericht
1.4, F6): „oder nimm doch kroatische und die anderen rein die sind nur nicht
sichtbar“. Sie gelten nur beim Tippen, gezeigt oder gelehrt werden sie nie -
wie alle Paare hier: "auch_var" steht nirgends auf dem Bildschirm, nicht als
Kachel und nicht als Knopf.

Ein Paar heißt: Wo a steht, gilt beim Tippen auch b - in derselben Form.
„Pijem kahvu“ nimmt „Pijem kafu“, die Lücke mit flaši nimmt boci. Nur in
diese Richtung: b kann ein anderes Wort sein, das die App mit eigener
Bedeutung kennt (otok heißt im Zahnarzt-Teil Schwellung, puno steht bei
pun „voll“, meni heißt auch „mir“). Darum gilt bei „mir“ nie jelovnik.
Mehrere Paare dürfen dasselbe a haben (kafena: smeđa, kahvena, braon),
dann gilt jedes b für sich.

    "a", "b" : die beiden Wörter, ausgeschrieben. Ein Wort, das sich nicht
               beugt, als Zeichenkette ("sada", "dva puta"). Sonst je Zahl
               (und bei Adjektiven je Geschlecht) die sechs Fälle in der
               Reihenfolge von FAELLE; None, wo die Form fehlt oder unsicher
               ist - dann gilt dort eben nichts zusätzlich. a und b haben
               dieselben Schlüssel und das None an denselben Stellen.
               Der Vokativ fehlt mit Absicht: getippt wird er nirgends, und
               seine Formen schwanken (komšija / komšijo).
    "gilt"   : UEBERALL - in jeder Schreibaufgabe und jedem Lückensatz, auch
                          mitten in einer Wendung („šolja kahve“).
               ALLEIN   - nur, wo das Wort allein die Antwort einer
                          Schreibaufgabe ist. Für Paare mit anderem
                          Geschlecht oder anderer Zahl (večer f. / veče n.,
                          boranija / mahune): in „Dobro veče“ hieße der
                          Tausch „Dobro večer“, das ist falsch.
               [Kennungen] - nur dort: die Kennung eines Wortes (id,
                          „senf:senf“) oder der Text eines Lückensatzes.
                          Für Paare, die nur in einem Zusammenhang gleich
                          sind (zemlja ist auch die Erde, šifra auch ein Code).
    "beleg"  : warum. Nur für uns.

Wie die App es bekommt: varianten_anwenden() unten schreibt beim Bauen
(inhalt.lade_daten()) an jedes Wort, das getippt werden kann, und an jeden
Lückensatz die zusätzlichen Antworten "auch_var". annehmbar() und der
Lückensatz in renderTask() hängen sie an, matches() und fastRichtig() bleiben
wie sie sind. Beim Satzbau wird nichts getippt; dort kommt die Form der
anderen Seite zu "ohne" - sonst läge neben „Ima mnogo djece“ die falsche
Kachel „puno“, die den Satz genauso richtig macht. In der Auswahl hält
geschwister() "auch_var" wie "auch" aus den falschen Knöpfen.
Das Sprechen bleibt, wie es ist: das Wort steht dort ja da.

Keine Regel, die Endungen abschneidet: ein Probelauf zeigte majka -> majci,
prijatelju -> druže, lonac -> lonca, und ein Vergleich über den Wortanfang
hielt gori, gore und gornji für goriti. Deshalb steht jede Form hier
ausgeschrieben, und verglichen werden nur ganze Wörter.

Eine Form, die mehrere Fälle sein kann (komšija: Nom. Sg. oder Gen. Pl.),
gilt nur, wenn alle dasselbe b ergeben. Sonst entscheidet bei einem Wort, das
allein dasteht, der Nominativ (komšije -> susjedi), bei einem Lückensatz der
Eintrag in FALL, und fehlt der, meldet pruefe_varianten() es.

Nur Bausteine, die Python schon mitbringt.
"""

import itertools
import re

FAELLE = ("nom", "gen", "dat", "akk", "instr", "lok")
UEBERALL = "ueberall"
ALLEIN = "allein"

VARIANTEN = [
    # --- Essen und Trinken ---
    {"a": {"sg": ("kahva", "kahve", "kahvi", "kahvu", "kahvom", "kahvi"),
           "pl": ("kahve", "kahva", "kahvama", "kahve", "kahvama", "kahvama")},
     "b": {"sg": ("kafa", "kafe", "kafi", "kafu", "kafom", "kafi"),
           "pl": ("kafe", "kafa", "kafama", "kafe", "kafama", "kafama")},
     "gilt": UEBERALL,
     "beleg": "Wort „kahva / kafa“; bs-Web kafa 56.505 / kahva 6.262, „pijem kafu“ 428 / „pijem kahvu“ 36"},
    {"a": {"sg": ("tunjevina", "tunjevine", "tunjevini", "tunjevinu", "tunjevinom", "tunjevini")},
     "b": {"sg": ("tuna", "tune", "tuni", "tunu", "tunom", "tuni")},
     "gilt": UEBERALL, "beleg": "bs-Web 2.634 / 1.573 (63 %)"},
    {"a": "majonez", "b": "majoneza", "gilt": ALLEIN,
     "beleg": "bs-Web 1.892 / 261 (88 %); m. / f."},
    {"a": "boranija", "b": "mahune", "gilt": ALLEIN,
     "beleg": "bs-Web Formen 1.971 / 745 (73 %); Einzahl / Mehrzahl"},
    {"a": {"sg": ("senf", "senfa", "senfu", "senf", "senfom", "senfu")},
     "b": {"sg": ("gorušica", "gorušice", "gorušici", "gorušicu", "gorušicom", "gorušici")},
     "gilt": ["senf:senf", "Kečap i ___, molim."],
     "beleg": "bs-Web 944 / 1.766 (35 %), hr 25 %, sr 37 %; m. / f., deshalb nur hier"},
    {"a": {"sg": ("pogača", "pogače", "pogači", "pogaču", "pogačom", "pogači")},
     "b": {"sg": ("somun", "somuna", "somunu", "somun", "somunom", "somunu")},
     "gilt": ["Uzet ću ___."],
     "beleg": "Wort pogača mit auch somun; der Satzbau dazu sperrt somun schon"},
    # --- Familie und Menschen ---
    {"a": {"sg": ("majka", "majke", "majci", "majku", "majkom", "majci"),
           "pl": ("majke", "majki", "majkama", "majke", "majkama", "majkama")},
     "b": {"sg": ("mama", "mame", "mami", "mamu", "mamom", "mami"),
           "pl": ("mame", "mama", "mamama", "mame", "mamama", "mamama")},
     "gilt": UEBERALL, "beleg": "Wort majka mit auch mama"},
    {"a": {"sg": ("komšija", "komšije", "komšiji", "komšiju", "komšijom", "komšiji"),
           "pl": ("komšije", "komšija", "komšijama", "komšije", "komšijama", "komšijama")},
     "b": {"sg": ("susjed", "susjeda", "susjedu", "susjeda", "susjedom", "susjedu"),
           "pl": ("susjedi", "susjeda", "susjedima", "susjede", "susjedima", "susjedima")},
     "gilt": UEBERALL,
     "beleg": "bs-Web Lemma susjed 24.700 / komšija 21.761 (53 %); komšiluk / susjedstvo schon freigegeben"},
    {"a": {"sg": ("komšinica", "komšinice", "komšinici", "komšinicu", "komšinicom", "komšinici"),
           "pl": ("komšinice", "komšinica", "komšinicama", "komšinice", "komšinicama", "komšinicama")},
     "b": {"sg": ("susjeda", "susjede", "susjedi", "susjedu", "susjedom", "susjedi"),
           "pl": ("susjede", "susjeda", "susjedama", "susjede", "susjedama", "susjedama")},
     "gilt": UEBERALL, "beleg": "bs-Web Lemma 4.168 / 3.626 (53 %)"},
    {"a": {"sg": ("doktor", "doktora", "doktoru", "doktora", "doktorom", "doktoru"),
           "pl": ("doktori", "doktora", "doktorima", "doktore", "doktorima", "doktorima")},
     "b": {"sg": ("ljekar", "ljekara", "ljekaru", "ljekara", "ljekarom", "ljekaru"),
           "pl": ("ljekari", "ljekara", "ljekarima", "ljekare", "ljekarima", "ljekarima")},
     "gilt": UEBERALL, "beleg": "Ajdin 06.11.2026: „mach doktor/ ljekar“"},
    {"a": {"sg": ("inženjer", "inženjera", "inženjeru", "inženjera", "inženjerom", "inženjeru"),
           "pl": ("inženjeri", "inženjera", "inženjerima", "inženjere", "inženjerima", "inženjerima")},
     "b": {"sg": ("inžinjer", "inžinjera", "inžinjeru", "inžinjera", "inžinjerom", "inžinjeru"),
           "pl": ("inžinjeri", "inžinjera", "inžinjerima", "inžinjere", "inžinjerima", "inžinjerima")},
     "gilt": UEBERALL, "beleg": "bs-Web Formen 6.162 / 15.629 (28 %), hr 6 %, sr 7 %: inžinjer ist die bosnische Form"},
    # --- Zeit und Mengen ---
    {"a": "sada", "b": "sad", "gilt": UEBERALL,
     "beleg": "bs-Web 503.749 / 849.905 (37 %); die App hat sad in 15 Sätzen"},
    {"a": "nikad", "b": "nikada", "gilt": UEBERALL, "beleg": "bs-Web 242.525 / 196.744 (55 %)"},
    {"a": "večer", "b": "veče", "gilt": ALLEIN,
     "beleg": "bs-Web 17.887 / 18.176 (50 %); die App sagt selbst „Dobro veče“; f. / n."},
    {"a": "popodne", "b": "poslijepodne", "gilt": UEBERALL, "beleg": "bs-Web 8.092 / 13.467 (38 %)"},
    {"a": "mnogo", "b": "puno", "gilt": UEBERALL,
     "beleg": "bs-Web 295.354 / 465.018 (39 %), „puno ljudi“ 3.815 / „mnogo ljudi“ 5.790; App: „Hvala puno“"},
    {"a": "dva puta", "b": "dvaput", "gilt": UEBERALL,
     "beleg": "bs-Web 8.948 / 43.798 (17 %), in allen drei Standardsprachen"},
    # --- Farben und Eigenschaften ---
    {"a": "roza", "b": "ružičasta", "gilt": ALLEIN,
     "beleg": "bs-Web Formen 4.107 / 2.109 (66 %); roza beugt sich nicht, die Farben stehen weiblich da"},
    {"a": {"m_sg": ("kafen", "kafenog", "kafenom", "kafen", "kafenim", "kafenom"),
           "f_sg": ("kafena", "kafene", "kafenoj", "kafenu", "kafenom", "kafenoj"),
           "n_sg": ("kafeno", "kafenog", "kafenom", "kafeno", "kafenim", "kafenom"),
           "m_pl": ("kafeni", "kafenih", "kafenim", "kafene", "kafenim", "kafenim"),
           "f_pl": ("kafene", "kafenih", "kafenim", "kafene", "kafenim", "kafenim"),
           "n_pl": ("kafena", "kafenih", "kafenim", "kafena", "kafenim", "kafenim")},
     "b": {"m_sg": ("smeđ", "smeđeg", "smeđem", "smeđ", "smeđim", "smeđem"),
           "f_sg": ("smeđa", "smeđe", "smeđoj", "smeđu", "smeđom", "smeđoj"),
           "n_sg": ("smeđe", "smeđeg", "smeđem", "smeđe", "smeđim", "smeđem"),
           "m_pl": ("smeđi", "smeđih", "smeđim", "smeđe", "smeđim", "smeđim"),
           "f_pl": ("smeđe", "smeđih", "smeđim", "smeđe", "smeđim", "smeđim"),
           "n_pl": ("smeđa", "smeđih", "smeđim", "smeđa", "smeđim", "smeđim")},
     "gilt": UEBERALL, "beleg": "bs-Web Formen 9.518 / 889 (91 %)"},
    {"a": {"m_sg": ("zanimljiv", "zanimljivog", "zanimljivom", "zanimljiv", "zanimljivim", "zanimljivom"),
           "f_sg": ("zanimljiva", "zanimljive", "zanimljivoj", "zanimljivu", "zanimljivom", "zanimljivoj"),
           "n_sg": ("zanimljivo", "zanimljivog", "zanimljivom", "zanimljivo", "zanimljivim", "zanimljivom"),
           "m_pl": ("zanimljivi", "zanimljivih", "zanimljivim", "zanimljive", "zanimljivim", "zanimljivim"),
           "f_pl": ("zanimljive", "zanimljivih", "zanimljivim", "zanimljive", "zanimljivim", "zanimljivim"),
           "n_pl": ("zanimljiva", "zanimljivih", "zanimljivim", "zanimljiva", "zanimljivim", "zanimljivim")},
     "b": {"m_sg": ("interesantan", "interesantnog", "interesantnom", "interesantan", "interesantnim",
                    "interesantnom"),
           "f_sg": ("interesantna", "interesantne", "interesantnoj", "interesantnu", "interesantnom",
                    "interesantnoj"),
           "n_sg": ("interesantno", "interesantnog", "interesantnom", "interesantno", "interesantnim",
                    "interesantnom"),
           "m_pl": ("interesantni", "interesantnih", "interesantnim", "interesantne", "interesantnim",
                    "interesantnim"),
           "f_pl": ("interesantne", "interesantnih", "interesantnim", "interesantne", "interesantnim",
                    "interesantnim"),
           "n_pl": ("interesantna", "interesantnih", "interesantnim", "interesantna", "interesantnim",
                    "interesantnim")},
     "gilt": UEBERALL, "beleg": "Wortschatz-Paket 10 bis 14: zanimljiv / interesantan"},
    # --- Kleidung, Tiere, Natur ---
    {"a": {"pl": ("pantalone", "pantalona", "pantalonama", "pantalone", "pantalonama", "pantalonama")},
     "b": {"pl": ("hlače", "hlača", "hlačama", "hlače", "hlačama", "hlačama")},
     "gilt": UEBERALL, "beleg": "bs-Web Formen 9.254 / 6.521 (59 %), über dem kroatischen Sockel"},
    {"a": {"sg": ("jagnje", "jagnjeta", "jagnjetu", "jagnje", "jagnjetom", "jagnjetu")},
     "b": {"sg": ("janje", "janjeta", "janjetu", "janje", "janjetom", "janjetu")},
     "gilt": UEBERALL, "beleg": "bs-Web Lemma 6.301 / 2.013 (76 %); die App hat janjetina"},
    {"a": {"sg": ("horoz", "horoza", "horozu", "horoza", "horozom", "horozu"),
           "pl": ("horozi", "horoza", "horozima", "horoze", "horozima", "horozima")},
     "b": {"sg": ("pijetao", "pijetla", "pijetlu", "pijetla", "pijetlom", "pijetlu"),
           "pl": ("pijetlovi", "pijetlova", "pijetlovima", "pijetlove", "pijetlovima", "pijetlovima")},
     "gilt": UEBERALL, "beleg": "bs-Web 1.906 / 263 (88 %)"},
    {"a": "ostrvo", "b": "otok", "gilt": ALLEIN,
     "beleg": "bs-Web 49.091 / 24.815 (66 %); n. / m.; im Zahnarzt-Teil heißt otok Schwellung"},
    {"a": {"sg": ("zrak", "zraka", "zraku", "zrak", "zrakom", "zraku")},
     "b": {"sg": ("vazduh", "vazduha", "vazduhu", "vazduh", "vazduhom", "vazduhu")},
     "gilt": UEBERALL, "beleg": "bs-Web 46.329 / 107.243 (30 %), hr 10 %, sr 74 %, beide bosnisch"},
    # --- Zuhause und Werkzeug ---
    {"a": {"sg": ("flaša", "flaše", "flaši", "flašu", "flašom", "flaši"),
           "pl": ("flaše", "flaša", "flašama", "flaše", "flašama", "flašama")},
     "b": {"sg": ("boca", "boce", "boci", "bocu", "bocom", "boci"),
           "pl": ("boce", "boca", "bocama", "boce", "bocama", "bocama")},
     "gilt": UEBERALL,
     "beleg": "bs-Web Lemma boca 26.153 / flaša 6.838 (79 %); boci 2.032 / flaši 301; Kontaktformular 12.11.2026"},
    # lavabo: wie es sich beugt (lavaboa?), ist unsicher - nur Nominativ und Akkusativ.
    {"a": {"sg": ("lavabo", None, None, "lavabo", None, None)},
     "b": {"sg": ("umivaonik", None, None, "umivaonik", None, None)},
     "gilt": UEBERALL, "beleg": "bs-Web Formen 1.476 / 364 (80 %)"},
    {"a": "deka", "b": "pokrivač", "gilt": ALLEIN,
     "beleg": "bs-Web 7.211 / 6.721 (52 %); f. / m."},
    {"a": {"sg": ("šaraf", "šarafa", "šarafu", "šaraf", "šarafom", "šarafu"),
           "pl": ("šarafi", "šarafa", "šarafima", "šarafe", "šarafima", "šarafima")},
     "b": {"sg": ("vijak", "vijka", "vijku", "vijak", "vijkom", "vijku"),
           "pl": ("vijci", "vijaka", "vijcima", "vijke", "vijcima", "vijcima")},
     "gilt": UEBERALL, "beleg": "bs-Web 5.829 / 1.263 (82 %)"},
    {"a": {"pl": ("merdevine", "merdevina", "merdevinama", "merdevine", "merdevinama", "merdevinama")},
     "b": {"pl": ("ljestve", "ljestava", "ljestvama", "ljestve", "ljestvama", "ljestvama")},
     "gilt": UEBERALL, "beleg": "bs-Web Formen 2.254 / 921 (71 %)"},
    {"a": {"sg": ("testera", "testere", "testeri", "testeru", "testerom", "testeri"),
           "pl": ("testere", "testera", "testerama", "testere", "testerama", "testerama")},
     "b": {"sg": ("pila", "pile", "pili", "pilu", "pilom", "pili"),
           "pl": ("pile", "pila", "pilama", "pile", "pilama", "pilama")},
     "gilt": UEBERALL, "beleg": "bs-Web Lemma 5.535 / 41 (99 %)"},
    # --- Reisen, Arbeit, Geräte ---
    {"a": "prtljag", "b": "prtljaga", "gilt": ALLEIN, "beleg": "bs-Web 4.428 / 1.670 (73 %); m. / f."},
    {"a": "kancelarija", "b": "ured", "gilt": ALLEIN, "beleg": "bs-Web Formen 98.992 / 34.741 (74 %); f. / m."},
    {"a": {"sg": ("računar", "računara", "računaru", "računar", "računarom", "računaru"),
           "pl": ("računari", "računara", "računarima", "računare", "računarima", "računarima")},
     "b": {"sg": ("kompjuter", "kompjutera", "kompjuteru", "kompjuter", "kompjuterom", "kompjuteru"),
           "pl": ("kompjuteri", "kompjutera", "kompjuterima", "kompjutere", "kompjuterima", "kompjuterima")},
     "gilt": UEBERALL, "beleg": "bs-Web 14.098 / 30.027 (32 %)"},
    {"a": {"sg": ("štampač", "štampača", "štampaču", "štampač", "štampačem", "štampaču"),
           "pl": ("štampači", "štampača", "štampačima", "štampače", "štampačima", "štampačima")},
     "b": {"sg": ("printer", "printera", "printeru", "printer", "printerom", "printeru"),
           "pl": ("printeri", "printera", "printerima", "printere", "printerima", "printerima")},
     "gilt": UEBERALL, "beleg": "bs-Web 3.248 / 2.574 (56 %)"},
    {"a": {"sg": ("šifra", "šifre", "šifri", "šifru", "šifrom", "šifri")},
     "b": {"sg": ("lozinka", "lozinke", "lozinki", "lozinku", "lozinkom", "lozinki")},
     "gilt": ["Koja je ___ za WiFi?"], "beleg": "Wort „šifra / lozinka“; šifra ist auch ein Code"},
    # --- Amt und Staat ---
    # Ohne Dativ und Lokativ: taksi ist auch das Taxi.
    {"a": {"sg": ("taksa", "takse", None, "taksu", "taksom", None)},
     "b": {"sg": ("naknada", "naknade", None, "naknadu", "naknadom", None)},
     "gilt": ["___ za pasoš je trideset maraka."],
     "beleg": "Wort taksa mit auch naknada; naknada ist auch eine Entschädigung"},
    {"a": {"sg": ("država", "države", "državi", "državu", "državom", "državi")},
     "b": {"sg": ("zemlja", "zemlje", "zemlji", "zemlju", "zemljom", "zemlji")},
     "gilt": ["Švicarska je mala ___."], "beleg": "Wort država mit auch zemlja; zemlja ist auch die Erde"},

    # === Tabelle 2c, Ajdin am 14.11.2026 (Prüfbericht 1.4, F6/V10) ===
    # Zuerst „ne keine kroatischen wörter nur bosnische“, dann: „oder nimm doch
    # kroatische und die anderen rein die sind nur nicht sichtbar“. Alle Zeilen
    # ja, nur beim Tippen und nur von der Form der App zur anderen. Nr. 30 (Gdje
    # für „wohin“) gehört zu F7, Nr. 38 (tisuća) bleibt, wie es ist (ZAHL_SONDER
    # in web/index.html). Anderes Geschlecht oder andere Zahl: nur, wo das Wort
    # allein steht (ALLEIN). Wo die andere Form auch etwas anderes heißt (meni
    # „mir“, kola, pare, sahat, tikva, šipak, ujesti, promet), nur am einen Wort.
    # Nr. 31 und 32 haben in den Lückensätzen „Pitam se ___ li dolazi.“ und
    # „Hvala ___!“ ein "auch" in vokabeln.py: da und puno wären hier Paare für
    # die ganze App, und je, da, puno sind Kacheln in vielen Sätzen.
    {"a": {"sg": ("hljeb", "hljeba", "hljebu", "hljeb", "hljebom", "hljebu")},
     "b": {"sg": ("kruh", "kruha", "kruhu", "kruh", "kruhom", "kruhu")},
     "gilt": UEBERALL, "beleg": "2c Nr. 1; bs-Web Formen 9.910 / 12.912 (43 %), hr 98 %"},
    {"a": {"sg": ("supa", "supe", "supi", "supu", "supom", "supi")},
     "b": {"sg": ("juha", "juhe", "juhi", "juhu", "juhom", "juhi")},
     "gilt": UEBERALL, "beleg": "2c Nr. 2; bs-Web Formen 1.859 / 2.767 (40 %), hr 90 %"},
    # Ohne Genitiv, Dativ und Lokativ: plate und plati sind auch „sie zahlen“, „zahl!“.
    {"a": {"sg": ("plata", None, None, "platu", "platom", None)},
     "b": {"sg": ("plaća", None, None, "plaću", "plaćom", None)},
     "gilt": UEBERALL, "beleg": "2c Nr. 3; bs-Web 76.788 / 76.292 (50 %), hr 95 %"},
    {"a": "polako", "b": "polahko", "gilt": UEBERALL,
     "beleg": "2c Nr. 4; bs-Web 3.897 / 56.494 (6 %), wie lako / lahko"},
    {"a": "minuta", "b": "minut", "gilt": ALLEIN, "beleg": "2c Nr. 5; bs-Web 13 %; f. / m."},
    {"a": "jučer", "b": "juče", "gilt": UEBERALL, "beleg": "2c Nr. 6; bs-Web 39.011 / 98.105 (28 %)"},
    {"a": {"sg": ("sedmica", "sedmice", "sedmici", "sedmicu", "sedmicom", "sedmici")},
     "b": {"sg": ("hefta", "hefte", "hefti", "heftu", "heftom", "hefti")},
     "gilt": UEBERALL, "beleg": "2c Nr. 7; Umgangssprache, bs-Web 1 %"},
    {"a": "lonac", "b": "šerpa", "gilt": ALLEIN,
     "beleg": "2c Nr. 8; „u šerpi“ 322 / „u loncu“ 1.245 (21 %); m. / f., nicht bosanski lonac"},
    {"a": "tava", "b": "tiganj", "gilt": ALLEIN, "beleg": "2c Nr. 9; bs-Web 14 %, sr 79 %; f. / m."},
    {"a": {"sg": ("špinat", "špinata", "špinatu", "špinat", "špinatom", "špinatu")},
     "b": {"sg": ("spanać", "spanaća", "spanaću", "spanać", "spanaćem", "spanaću")},
     "gilt": UEBERALL, "beleg": "2c Nr. 10; bs-Web 1.060 / 5.447 (16 %), sr 91 %"},
    {"a": {"sg": ("bašta", "bašte", "bašti", "baštu", "baštom", "bašti")},
     "b": {"sg": ("bašča", "bašče", "bašči", "bašču", "baščom", "bašči")},
     "gilt": UEBERALL, "beleg": "2c Nr. 11; die bosnische Form (Baščaršija), bs-Web 14 %"},
    {"a": "kćerka", "b": "kći", "gilt": ALLEIN, "beleg": "2c Nr. 12; bs-Web 17 %, hr 72 %"},
    {"a": "kćerka", "b": "kćer", "gilt": ALLEIN, "beleg": "2c Nr. 12; bs-Web 17 %"},
    {"a": "sat", "b": "sahat", "gilt": ["stunde / uhr:sat"],
     "beleg": "2c Nr. 13; bs-Web 1 %; nur das Wort, nicht „Koliko je sati?“"},
    {"a": "historija", "b": "povijest", "gilt": ALLEIN,
     "beleg": "2c Nr. 14; bs-Web 52 %, hr 98 %; andere Beugung"},
    {"a": "posjeta", "b": "posjet", "gilt": ALLEIN, "beleg": "2c Nr. 15; bs-Web 52 %; f. / m."},
    {"a": {"sg": ("kirija", "kirije", "kiriji", "kiriju", "kirijom", "kiriji")},
     "b": {"sg": ("stanarina", "stanarine", "stanarini", "stanarinu", "stanarinom", "stanarini")},
     "gilt": UEBERALL, "beleg": "2c Nr. 16; bs-Web 33 %, hr 84 %"},
    {"a": {"sg": ("kirija", "kirije", "kiriji", "kiriju", "kirijom", "kiriji")},
     "b": {"sg": ("najamnina", "najamnine", "najamnini", "najamninu", "najamninom", "najamnini")},
     "gilt": UEBERALL, "beleg": "2c Nr. 16; bs-Web 33 %, hr 90 %"},
    # Nr. 17: kroatisch geprägt, im bosnischen Web 39 bis 53 %.
    {"a": {"sg": ("frižider", "frižidera", "frižideru", "frižider", "frižiderom", "frižideru")},
     "b": {"sg": ("hladnjak", "hladnjaka", "hladnjaku", "hladnjak", "hladnjakom", "hladnjaku")},
     "gilt": UEBERALL, "beleg": "2c Nr. 17; hladnjak 41 %"},
    {"a": {"sg": ("rerna", "rerne", "rerni", "rernu", "rernom", "rerni")},
     "b": {"sg": ("pećnica", "pećnice", "pećnici", "pećnicu", "pećnicom", "pećnici")},
     "gilt": UEBERALL, "beleg": "2c Nr. 17; pećnica 48 %"},
    {"a": {"sg": ("kesa", "kese", "kesi", "kesu", "kesom", "kesi")},
     "b": {"sg": ("vrećica", "vrećice", "vrećici", "vrećicu", "vrećicom", "vrećici")},
     "gilt": UEBERALL, "beleg": "2c Nr. 17; vrećica 48 % (auch Teebeutel)"},
    {"a": "sirće", "b": "ocat", "gilt": ALLEIN, "beleg": "2c Nr. 17; ocat 44 %; n. / m."},
    {"a": {"sg": ("plafon", "plafona", "plafonu", "plafon", "plafonom", "plafonu")},
     "b": {"sg": ("strop", "stropa", "stropu", "strop", "stropom", "stropu")},
     "gilt": UEBERALL, "beleg": "2c Nr. 17; strop 45 %"},
    {"a": {"sg": ("fabrika", "fabrike", "fabrici", "fabriku", "fabrikom", "fabrici")},
     "b": {"sg": ("tvornica", "tvornice", "tvornici", "tvornicu", "tvornicom", "tvornici")},
     "gilt": UEBERALL, "beleg": "2c Nr. 17; tvornica 39 %"},
    {"a": {"sg": ("kajsija", "kajsije", "kajsiji", "kajsiju", "kajsijom", "kajsiji"),
           "pl": ("kajsije", "kajsija", "kajsijama", "kajsije", "kajsijama", "kajsijama")},
     "b": {"sg": ("marelica", "marelice", "marelici", "marelicu", "marelicom", "marelici"),
           "pl": ("marelice", "marelica", "marelicama", "marelice", "marelicama", "marelicama")},
     "gilt": UEBERALL, "beleg": "2c Nr. 17; marelica 41 %"},
    {"a": {"sg": ("praziluk", "praziluka", "praziluku", "praziluk", "prazilukom", "praziluku")},
     "b": {"sg": ("poriluk", "poriluka", "poriluku", "poriluk", "porilukom", "poriluku")},
     "gilt": UEBERALL, "beleg": "2c Nr. 17; poriluk 53 %"},
    {"a": {"sg": ("peškir", "peškira", "peškiru", "peškir", "peškirom", "peškiru"),
           "pl": ("peškiri", "peškira", "peškirima", "peškire", "peškirima", "peškirima")},
     "b": {"sg": ("ručnik", "ručnika", "ručniku", "ručnik", "ručnikom", "ručniku"),
           "pl": ("ručnici", "ručnika", "ručnicima", "ručnike", "ručnicima", "ručnicima")},
     "gilt": UEBERALL, "beleg": "2c Nr. 17; ručnik 39 %"},
    # Nr. 18 und 19: gegenseitig, beide Wörter stehen in der App.
    {"a": "prodavnica", "b": "radnja", "gilt": ["laden:prodavnica"],
     "beleg": "2c Nr. 18; radnja heißt auch Handlung, darum nur an den beiden Wörtern"},
    {"a": "radnja", "b": "prodavnica", "gilt": ["geschäft:radnja"], "beleg": "2c Nr. 18"},
    {"a": "dvorište", "b": "avlija", "gilt": ["hof (am haus):dvorište"], "beleg": "2c Nr. 19; n. / f."},
    {"a": "avlija", "b": "dvorište", "gilt": ["hof / innenhof:avlija"], "beleg": "2c Nr. 19; f. / n."},
    {"a": "ponekad", "b": "nekad", "gilt": ["manchmal:ponekad"],
     "beleg": "2c Nr. 20; nekad steht in der App als „manchmal / früher“"},
    # Dritte Runde (Ajdin, 14.11.2026 abends): „nekada“ auch, wo „ponekad“ gefragt ist, „Ja“ -
    # die lange Form wie bei nekad selbst (F14 i).
    {"a": "ponekad", "b": "nekada", "gilt": ["manchmal:ponekad"],
     "beleg": "dritte Runde, 14.11.2026; nekad steht schon da, nekada ist die lange Form"},
    # Nr. 21: kafena hat oben schon smeđa (Tabelle 2a).
    {"a": {"m_sg": ("kafen", "kafenog", "kafenom", "kafen", "kafenim", "kafenom"),
           "f_sg": ("kafena", "kafene", "kafenoj", "kafenu", "kafenom", "kafenoj"),
           "n_sg": ("kafeno", "kafenog", "kafenom", "kafeno", "kafenim", "kafenom"),
           "m_pl": ("kafeni", "kafenih", "kafenim", "kafene", "kafenim", "kafenim"),
           "f_pl": ("kafene", "kafenih", "kafenim", "kafene", "kafenim", "kafenim"),
           "n_pl": ("kafena", "kafenih", "kafenim", "kafena", "kafenim", "kafenim")},
     "b": {"m_sg": ("kahven", "kahvenog", "kahvenom", "kahven", "kahvenim", "kahvenom"),
           "f_sg": ("kahvena", "kahvene", "kahvenoj", "kahvenu", "kahvenom", "kahvenoj"),
           "n_sg": ("kahveno", "kahvenog", "kahvenom", "kahveno", "kahvenim", "kahvenom"),
           "m_pl": ("kahveni", "kahvenih", "kahvenim", "kahvene", "kahvenim", "kahvenim"),
           "f_pl": ("kahvene", "kahvenih", "kahvenim", "kahvene", "kahvenim", "kahvenim"),
           "n_pl": ("kahvena", "kahvenih", "kahvenim", "kahvena", "kahvenim", "kahvenim")},
     "gilt": UEBERALL, "beleg": "2c Nr. 21; die Form zu kahva, bs-Web 12 / 219 (5 %)"},
    {"a": "kafena", "b": "braon", "gilt": ALLEIN,
     "beleg": "2c Nr. 21; Alltag, eher serbisch; braon beugt sich nicht"},
    {"a": {"sg": ("fildžan", "fildžana", "fildžanu", "fildžan", "fildžanom", "fildžanu"),
           "pl": ("fildžani", "fildžana", "fildžanima", "fildžane", "fildžanima", "fildžanima")},
     "b": {"sg": ("findžan", "findžana", "findžanu", "findžan", "findžanom", "findžanu"),
           "pl": ("findžani", "findžana", "findžanima", "findžane", "findžanima", "findžanima")},
     "gilt": UEBERALL, "beleg": "2c Nr. 22; zweite Schreibung, bs-Web 139 / 1.182 (11 %)"},
    {"a": "auto", "b": "kola", "gilt": ["auto:auto", "ich habe ein auto:Imam auto"],
     "beleg": "2c Nr. 23; Mehrzahlwort, Adjektive wandern mit - nur das Wort allein; "
              "„Imam kola“ seit der dritten Runde (14.11.2026)"},
    {"a": "novac", "b": "pare", "gilt": ["geld:novac", "geld abheben:podići novac", "geld einzahlen:uplatiti novac"],
     "beleg": "2c Nr. 24; Mehrzahlwort, pare ist auch Mehrzahl von para - nur das Wort allein; "
              "„podići pare“ und „uplatiti pare“ seit den Fragen vom 15.11.2026 (9d, 9e)"},
    # Dritte Runde (Ajdin, 14.11.2026 abends): „Zweite Form auch in ganzen Sätzen“, „Ja“ -
    # genau die Formen, nach denen gefragt war: „Imam kola“ (oben bei auto), „u kolima“,
    # „Nemam para“, „na pazaru“, „na sokaku“, „Supa je u šerpi“, „On ima kuče“. Jede nur
    # an ihrer einen Stelle, keine weiteren gebeugten Formen (kola, pare, šerpa, kuče
    # haben anderes Geschlecht oder andere Zahl, Adjektive und Verben wandern mit).
    {"a": "autu", "b": "kolima", "gilt": ["im auto:u autu"], "beleg": "dritte Runde, 14.11.2026: „u kolima“"},
    {"a": "novca", "b": "para", "gilt": ["ich habe kein geld:Nemam novca"],
     "beleg": "dritte Runde, 14.11.2026: „Nemam para“"},
    {"a": "pijaci", "b": "pazaru", "gilt": ["auf dem markt:na pijaci"],
     "beleg": "dritte Runde, 14.11.2026: „na pazaru“"},
    {"a": "ulici", "b": "sokaku", "gilt": ["auf der straße:na ulici"],
     "beleg": "dritte Runde, 14.11.2026: „na sokaku“"},
    {"a": "loncu", "b": "šerpi", "gilt": ["Supa je u ___."],
     "beleg": "dritte Runde, 14.11.2026: „Supa je u šerpi“"},
    {"a": "psa", "b": "kuče", "gilt": ["er hat einen hund:On ima psa"],
     "beleg": "dritte Runde, 14.11.2026: „On ima kuče“"},
    # Fragen vom 15.11.2026 (Ajdin abends, 9a bis 9i): die zweite Form auch an den
    # neun Stellen, die in der dritten Runde nicht gefragt waren, „ja“, mit genau den
    # Formen, die er bestätigt hat: kolima, kola oca, podići pare und uplatiti pare
    # (oben bei novac), Tražimo sokak, Bojim se kučadi, Čuvaj se kučeta!, Kuče me je
    # ujelo (am 16.11.2026 wieder raus, siehe unten). Wieder jede nur an ihrer Stelle,
    # keine weiteren Formen selbst gebildet.
    # „auto oca“ als ganze Wendung: am Paar auto / kola wäre aus dem "auch" „očev auto“
    # auch „očev kola“ geworden.
    {"a": "autom", "b": "kolima", "gilt": ["mit dem auto:autom", "Putujemo ___."],
     "beleg": "Fragen 15.11.2026, 9a und 9b: „kolima“"},
    {"a": "auto oca", "b": "kola oca", "gilt": ["das auto des vaters:auto oca"],
     "beleg": "Fragen 15.11.2026, 9c: „kola oca“"},
    {"a": "ulicu", "b": "sokak", "gilt": ["wir suchen die straße:Tražimo ulicu"],
     "beleg": "Fragen 15.11.2026, 9f: „Tražimo sokak“"},
    {"a": "pasa", "b": "kučadi", "gilt": ["ich habe angst vor hunden:Bojim se pasa"],
     "beleg": "Fragen 15.11.2026, 9g: „Bojim se kučadi“"},
    {"a": "psa", "b": "kučeta", "gilt": ["vorsicht vor dem hund!:Čuvaj se psa!"],
     "beleg": "Fragen 15.11.2026, 9h: „Čuvaj se kučeta!“"},
    # Fragen vom 16.11.2026 (Ajdin, 8a und 8b). 8a: „očeva kola“ zählt auch, „očev auto“
    # bleibt, „očev kola“ bleibt falsch. Am "auch" „očev auto“ als ganze Wendung, wie
    # „auto oca“ / „kola oca“ oben: mit kola wandert das Adjektiv mit (očeva, Mehrzahl).
    # 8b: „nimm nur pas aber beide“ - bei „Der Hund hat mich gebissen“ gelten nur „Pas me
    # je ujeo“ und „Ujeo me je pas“ (das steht als "auch" am Wort in vokabeln.py, wie beim
    # Satzbau). Das Paar „pas me je ujeo“ / „kuče me je ujelo“ vom
    # 15.11.2026 (9i) ist deshalb wieder raus; die anderen kuče-Formen (On ima kuče,
    # Bojim se kučadi, Čuvaj se kučeta!, kuče allein beim Wort pas) bleiben.
    {"a": "očev auto", "b": "očeva kola", "gilt": ["das auto des vaters:auto oca"],
     "beleg": "Fragen 16.11.2026, 8a/8b: „očeva kola“ zählt auch"},
    {"a": {"sg": ("mobitel", "mobitela", "mobitelu", "mobitel", "mobitelom", "mobitelu")},
     "b": {"sg": ("mobilni", "mobilnog", "mobilnom", "mobilni", "mobilnim", "mobilnom")},
     "gilt": UEBERALL, "beleg": "2c Nr. 25; Alltag"},
    {"a": "pijaca", "b": "pazar", "gilt": ALLEIN,
     "beleg": "2c Nr. 26; bs-Web 44 %; f. / m., pazar ist auch Markttag und Ortsname"},
    {"a": "jelovnik", "b": "meni", "gilt": ["speisekarte:jelovnik"],
     "beleg": "2c Nr. 27; meni heißt auch „mir“ - nur bei der Speisekarte, nie umgekehrt"},
    {"a": {"sg": ("obrazac", "obrasca", "obrascu", "obrazac", "obrascem", "obrascu"),
           "pl": ("obrasci", "obrazaca", "obrascima", "obrasce", "obrascima", "obrascima")},
     "b": {"sg": ("formular", "formulara", "formularu", "formular", "formularom", "formularu"),
           "pl": ("formulari", "formulara", "formularima", "formulare", "formularima", "formularima")},
     "gilt": UEBERALL, "beleg": "2c Nr. 28; Alltag, bs-Web 9 %"},
    {"a": "izvini", "b": "oprosti", "gilt": ["entschuldigung (du):Izvini"],
     "beleg": "2c Nr. 29; bs-Web 65 %; oprosti heißt auch „verzeih“, Oprosti mi ist ein eigenes Wort"},
    # Dritte Runde (Ajdin, 14.11.2026 abends): „Oprostite“ neben „Izvinite“ (Sie-Form),
    # „Ja“. Nur wo die App Izvinite zum Tippen erwartet, wie bei Nr. 29.
    {"a": "izvinite", "b": "oprostite", "gilt": ["entschuldigung (sie):Izvinite", "___, molim Vas."],
     "beleg": "dritte Runde, 14.11.2026; wie izvini / oprosti, oprostite heißt auch „verzeihen Sie“"},
    {"a": "da li", "b": "je li", "gilt": ["ob:da li"], "beleg": "2c Nr. 31; beides Standard, je li 19 %"},
    {"a": "hvala puno", "b": "puno hvala", "gilt": ["vielen dank:Hvala puno"], "beleg": "2c Nr. 32; 17 %"},
    {"a": "hvala puno", "b": "hvala lijepa", "gilt": ["vielen dank:Hvala puno"], "beleg": "2c Nr. 32; 6 %"},
    {"a": "hvala puno", "b": "hvala mnogo", "gilt": ["vielen dank:Hvala puno"], "beleg": "2c Nr. 32; 6 %"},
    {"a": "doviđenja", "b": "do viđenja", "gilt": UEBERALL,
     "beleg": "2c Nr. 33; getrennt geschrieben, bs-Web 308 / 1.247 (20 %)"},
    {"a": "dobro veče", "b": "dobra večer", "gilt": UEBERALL,
     "beleg": "2c Nr. 34; eher kroatisch, bs-Web 30 %, hr 74 %"},
    {"a": "navečer", "b": "uveče", "gilt": UEBERALL, "beleg": "2c Nr. 35; eher serbisch, bs-Web 36 %"},
    {"a": "ujutro", "b": "ujutru", "gilt": UEBERALL, "beleg": "2c Nr. 35; eher serbisch, bs-Web 20 %"},
    # Nr. 36: drug ist beim Wort prijatelj schon "auch".
    {"a": "prijatelja", "b": "druga", "gilt": ["bei meinem freund:kod prijatelja"],
     "beleg": "2c Nr. 36; „kod druga“ 278 / 1.103 (20 %)"},
    {"a": "prijatelju", "b": "druže", "gilt": ["anrede: freund!:prijatelju!"],
     "beleg": "2c Nr. 36; klingt in der Anrede nach Genosse"},
    # Nr. 37: seltene Alltagsformen und Turzismen, im bosnischen Web 1 bis 23 %.
    {"a": {"sg": ("prozor", "prozora", "prozoru", "prozor", "prozorom", "prozoru"),
           "pl": ("prozori", "prozora", "prozorima", "prozore", "prozorima", "prozorima")},
     "b": {"sg": ("pendžer", "pendžera", "pendžeru", "pendžer", "pendžerom", "pendžeru"),
           "pl": ("pendžeri", "pendžera", "pendžerima", "pendžere", "pendžerima", "pendžerima")},
     "gilt": UEBERALL, "beleg": "2c Nr. 37"},
    {"a": {"sg": ("zid", "zida", "zidu", "zid", "zidom", "zidu")},
     "b": {"sg": ("duvar", "duvara", "duvaru", "duvar", "duvarom", "duvaru")},
     "gilt": UEBERALL, "beleg": "2c Nr. 37"},
    {"a": "ulica", "b": "sokak", "gilt": ALLEIN, "beleg": "2c Nr. 37; f. / m."},
    {"a": {"sg": ("ormar", "ormara", "ormaru", "ormar", "ormarom", "ormaru")},
     "b": {"sg": ("dolap", "dolapa", "dolapu", "dolap", "dolapom", "dolapu")},
     "gilt": UEBERALL, "beleg": "2c Nr. 37"},
    {"a": {"sg": ("gost", "gosta", "gostu", "gosta", "gostom", "gostu"),
           "pl": ("gosti", "gostiju", "gostima", "goste", "gostima", "gostima")},
     "b": {"sg": ("musafir", "musafira", "musafiru", "musafira", "musafirom", "musafiru"),
           "pl": ("musafiri", "musafira", "musafirima", "musafire", "musafirima", "musafirima")},
     "gilt": UEBERALL, "beleg": "2c Nr. 37"},
    {"a": {"sg": ("lijek", "lijeka", "lijeku", "lijek", "lijekom", "lijeku")},
     "b": {"sg": ("hap", "hapa", "hapu", "hap", "hapom", "hapu")},
     "gilt": UEBERALL, "beleg": "2c Nr. 37"},
    # Ohne Dativ und Lokativ: prehladi ist auch „erkältet sich“.
    {"a": {"sg": ("prehlada", "prehlade", None, "prehladu", "prehladom", None)},
     "b": {"sg": ("nahlada", "nahlade", None, "nahladu", "nahladom", None)},
     "gilt": UEBERALL, "beleg": "2c Nr. 37"},
    {"a": "kvasac", "b": "germa", "gilt": ALLEIN, "beleg": "2c Nr. 37; m. / f."},
    {"a": "stepenice", "b": "basamaci", "gilt": ALLEIN, "beleg": "2c Nr. 37; f. / m."},
    {"a": "pas", "b": "kuče", "gilt": ALLEIN, "beleg": "2c Nr. 37; m. / n."},
    {"a": "komad", "b": "parče", "gilt": ALLEIN, "beleg": "2c Nr. 37; m. / n."},
    {"a": {"sg": ("mesnica", "mesnice", "mesnici", "mesnicu", "mesnicom", "mesnici")},
     "b": {"sg": ("kasapnica", "kasapnice", "kasapnici", "kasapnicu", "kasapnicom", "kasapnici")},
     "gilt": UEBERALL, "beleg": "2c Nr. 37"},
    {"a": "raspust", "b": "ferije", "gilt": ALLEIN, "beleg": "2c Nr. 37; Einzahl / Mehrzahl"},
    {"a": "deka", "b": "ćebe", "gilt": ALLEIN, "beleg": "2c Nr. 37; ćebe 17 %; f. / n."},
    {"a": {"pl": ("merdevine", "merdevina", "merdevinama", "merdevine", "merdevinama", "merdevinama")},
     "b": {"pl": ("skale", "skala", "skalama", "skale", "skalama", "skalama")},
     "gilt": UEBERALL, "beleg": "2c Nr. 37"},
    {"a": {"sg": ("lješnjak", "lješnjaka", "lješnjaku", "lješnjak", "lješnjakom", "lješnjaku"),
           "pl": ("lješnjaci", "lješnjaka", "lješnjacima", "lješnjake", "lješnjacima", "lješnjacima")},
     "b": {"sg": ("lješnik", "lješnika", "lješniku", "lješnik", "lješnikom", "lješniku"),
           "pl": ("lješnici", "lješnika", "lješnicima", "lješnike", "lješnicima", "lješnicima")},
     "gilt": UEBERALL, "beleg": "2c Nr. 37; lješnik 23 %, hr 1 %"},
    # Nr. 39: die andere Form heißt auch etwas anderes - nur am einen Wort.
    {"a": "bundeva", "b": "tikva", "gilt": ["kürbis:bundeva"],
     "beleg": "2c Nr. 39; 53 %; tikva ist auch der Flaschenkürbis"},
    {"a": "nar", "b": "šipak", "gilt": ["granatapfel:nar"], "beleg": "2c Nr. 39; 25 %; šipak ist auch die Hagebutte"},
    {"a": "ugristi", "b": "ujesti", "gilt": ["beißen:ugristi"],
     "beleg": "2c Nr. 39; 47 %; ujesti eher bei Insekten und Hunden"},
    {"a": "saobraćaj", "b": "promet", "gilt": ["verkehr:saobraćaj"], "beleg": "2c Nr. 39; 69 %; promet ist auch Umsatz"},
]

# Antworten mit einer Form, die mehrere Fälle sein kann, die verschiedene b
# ergeben: Text des Lückensatzes (oder Kennung des Wortes) -> Fall ("sg_nom",
# bei Adjektiven "f_sg_akk"). Ein Wort, das allein dasteht, braucht keinen
# Eintrag, dort gilt der Nominativ.
FALL = {
    "Moj ___ je dobar čovjek.": "sg_nom",     # komšija: Nom. Sg. (susjed) oder Gen. Pl. (susjeda)
    "Kečap i ___, molim.": "sg_akk",          # senf: Nom. oder Akk. - gorušica / gorušicu
}

# Wie typable() in web/index.html: nur diese Wörter kommen als
# Schreibaufgabe. tests/test_varianten.py hält beide Stellen zusammen.
TIPPBAR_LAENGE = 14
NIE_TIPPBAR = re.compile(r"[.…→]")


def tippbar(bs):
    return len(bs) <= TIPPBAR_LAENGE and not NIE_TIPPBAR.search(bs) and " / " not in bs


# Ein Wort ist eine Folge von Buchstaben, mit Bindestrich zusammengehängte
# zählen als eines - „kahva“ trifft nicht in „kahva-bar“ und nie in „kahvana“.
WORT = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")
# Höchstens so viele Wörter mit Variante je Antwort. Mit jedem weiteren
# verdoppeln sich die Fassungen, und so lange Antworten tippt niemand.
HOECHSTENS = 2


def faelle(seite):
    """{Fall: Form} einer Seite: "grund" bei einem Wort, das sich nicht beugt,
    sonst "sg_nom", "pl_akk", "f_sg_dat" usw. Ohne die fehlenden (None)."""
    if isinstance(seite, str):
        return {"grund": seite}
    return {"%s_%s" % (zahl, fall): form for zahl, formen in seite.items()
            for fall, form in zip(FAELLE, formen) if form}


def index(paare=None):
    """{Form von a: [(Nummer des Paars, {Fall: Form von b})]}. Klein
    geschrieben, mehrteilige Formen ("dva puta") mit einem Leerzeichen."""
    aus = {}
    for nr, p in enumerate(VARIANTEN if paare is None else paare):
        fa, fb = faelle(p["a"]), faelle(p["b"])
        je_form = {}
        for fall, form in fa.items():
            if fall in fb:
                je_form.setdefault(form.lower(), {})[fall] = fb[fall]
        for form, ziele in je_form.items():
            aus.setdefault(form, []).append((nr, ziele))
    return aus


def _grundform(fall):
    return fall == "grund" or fall.endswith("_nom")


def _erste(seite):
    """Die erste Form einer Seite, für Meldungen."""
    return next(iter(faelle(seite).values()), "?")


def _ziel(ziele, allein, fall):
    """Welche Form von b für diese Fundstelle gilt, oder None, wenn das
    nicht eindeutig ist."""
    if fall and fall in ziele:
        return ziele[fall]
    if allein:
        for f, b in ziele.items():          # in der Reihenfolge von FAELLE, sg vor pl
            if _grundform(f):
                return b
    verschieden = set(ziele.values())
    return verschieden.pop() if len(verschieden) == 1 else None


def _gilt_hier(paar, kennung, wort, allein):
    g = paar["gilt"]
    if g == UEBERALL:
        return True
    if g == ALLEIN:
        return wort and allein
    return kennung in g


def _gross(vorlage, neu):
    return neu[:1].upper() + neu[1:] if vorlage[:1].isupper() else neu


def zusatz(antworten, kennung, wort, fall=None, idx=None):
    """Die zusätzlichen Antworten zu antworten (Liste, " / " schon getrennt)
    und was dabei unklar blieb: (["Pijem kafu"], []).

    kennung: die des Wortes oder der Text des Lückensatzes (für "gilt").
    wort: True bei einer Schreibaufgabe, False beim Lückensatz - nur ein
    Wort darf ALLEIN-Paare nehmen und allein den Nominativ bekommen.
    fall: der Fall aus FALL, sonst None. idx: index(), sonst neu."""
    idx = index() if idx is None else idx
    laengste = max((len(f.split(" ")) for f in idx), default=1)
    raus, probleme = [], []
    schon = {a.strip().lower() for a in antworten}
    for antwort in antworten:
        woerter = list(WORT.finditer(antwort))
        ganz = antwort.strip().rstrip(".!?…").strip().lower()
        treffer, belegt = [], set()
        # Längere Formen zuerst, damit "dva puta" vor einem einzelnen "dva" kommt.
        for n in range(laengste, 0, -1):
            for i in range(len(woerter) - n + 1):
                stueck = woerter[i:i + n]
                if any(j in belegt for j in range(i, i + n)):
                    continue
                if any(not antwort[x.end():y.start()].isspace() for x, y in zip(stueck, stueck[1:])):
                    continue
                von, bis = stueck[0].start(), stueck[-1].end()
                form = " ".join(x.group(0).lower() for x in stueck)
                allein = ganz == antwort[von:bis].lower()
                # Alle Paare mit dieser Form, nicht nur das erste (14.11.2026):
                # kafena nimmt smeđa, kahvena und braon.
                ziele_hier = []
                for nr, ziele in idx.get(form, []):
                    if not _gilt_hier(VARIANTEN[nr], kennung, wort, allein):
                        continue
                    ziel = _ziel(ziele, wort and allein, fall)
                    if ziel is None:
                        probleme.append("Variante [%s] '%s' in '%s': mehrere Fälle (%s) - Fall in "
                                        "FALL angeben" % (kennung, form, antwort, ", ".join(ziele)))
                        continue
                    if ziel not in ziele_hier:
                        ziele_hier.append(ziel)
                if ziele_hier:
                    treffer.append((von, bis, ziele_hier))
                    belegt.update(range(i, i + n))
        if len(treffer) > HOECHSTENS:
            probleme.append("Variante [%s] '%s': %d Wörter mit Varianten, erlaubt sind %d"
                            % (kennung, antwort, len(treffer), HOECHSTENS))
            continue
        treffer.sort()
        # Je Wort: bleibt (None) oder eines seiner b. Alles bleibt = die Antwort selbst.
        for wahl in itertools.product(*[[None] + ziele for _, _, ziele in treffer]):
            if not any(wahl):
                continue
            neu, ende = [], 0
            for (von, bis, _), ziel in zip(treffer, wahl):
                neu.append(antwort[ende:von])
                neu.append(_gross(antwort[von:bis], ziel) if ziel else antwort[von:bis])
                ende = bis
            neu = "".join(neu) + antwort[ende:]
            if neu.strip().lower() not in schon:
                schon.add(neu.strip().lower())
                raus.append(neu)
    return raus, probleme


def _antworten(*felder):
    """Alle Antworten eines Eintrags, an " / " getrennt."""
    aus = []
    for f in felder:
        for x in ([f] if isinstance(f, str) else list(f or [])):
            aus += [t.strip() for t in str(x).split(" / ") if t.strip()]
    return aus


def _bedeutung(w):
    """Die deutsche Bedeutung, auch in einer anderen Sprache: sie steckt in
    der Kennung „bedeutung:wort“. Im Zahnarzt-Teil (za|wort) ist es de."""
    kennung, bs = str(w.get("id", "")), str(w.get("bs", ""))
    return kennung[:-len(bs) - 1] if kennung.endswith(":" + bs) else str(w.get("de", ""))


def _alle_woerter(daten):
    for kat in daten.get("kategorien", []):
        yield from kat.get("words", [])
    for kat in (daten.get("zahnarzt") or {}).get("kategorien", []):
        yield from kat.get("words", [])


def _wort_zusatz(w, idx):
    if not tippbar(str(w.get("bs", ""))):
        return [], []
    return zusatz(_antworten(w.get("bs"), w.get("auch")), w.get("id"), True, fall=FALL.get(w.get("id")), idx=idx)


def _satz_zusatz(s, idx):
    return zusatz(_antworten(s.get("answer"), s.get("auch")), s.get("text"), False,
                  fall=FALL.get(s.get("text")), idx=idx)


def _kachel_sperre(s, app_formen, kacheln, indizes):
    """Die Kacheln, die bei diesem Satzbau-Satz nicht als falsche liegen
    dürfen, weil sie ihn genauso richtig machen: zu jedem Wort im Satz (oder
    in einer erlaubten Reihenfolge), das eine Form eines Paars ist, die Form
    der anderen Seite in denselben Fällen - in beide Richtungen, gilt egal.
    Neben „Ima mnogo djece“ also kein „puno“. Eine andere Form derselben
    Seite bleibt ein guter Fehler („majka“ neben „Volim svoju majku.“), und
    „pile“ (Küken) sperrt nichts, weil die Form dazu, testere, keine Kachel
    der App ist. Nur einzelne Wörter, nur was die App als Kachel hätte."""
    texte = [kacheln(t) for t in [str(s.get("bs", ""))] + [str(a) for a in (s.get("auch") or [])]]
    eigene = {k for t in texte for k in t}
    laengste = max((len(f.split(" ")) for idx in indizes for f in idx), default=1)
    sperre = set()
    for teile in texte:
        stuecke = [" ".join(teile[i:i + n]) for n in range(1, laengste + 1) for i in range(len(teile) - n + 1)]
        for st in stuecke:
            for idx in indizes:
                for _, ziele in idx.get(st, []):
                    sperre |= {f for f in ziele.values() if " " not in f}
    return sorted((sperre & app_formen) - eigene)


def varianten_anwenden(daten, kacheln):
    """Schreibt "auch_var" an Wörter (nur die, die getippt werden können) und
    Lückensätze und ergänzt "ohne" beim Satzbau. Liefert neue Listen und
    Einträge, die Inhaltsdateien selbst bleiben unberührt.
    kacheln: inhalt.satz_kacheln - wie die App einen Satz in Kacheln teilt."""
    idx = index()

    def wort(w):
        mehr, _ = _wort_zusatz(w, idx)
        return dict(w, auch_var=mehr) if mehr else w

    def kategorien(liste):
        return [dict(k, words=[wort(w) for w in k.get("words", [])]) for k in liste]

    neu = dict(daten)
    neu["kategorien"] = kategorien(daten.get("kategorien", []))
    if isinstance(daten.get("zahnarzt"), dict):
        neu["zahnarzt"] = dict(daten["zahnarzt"], kategorien=kategorien(daten["zahnarzt"].get("kategorien", [])))
    saetze = []
    for s in daten.get("saetze", []):
        mehr, _ = _satz_zusatz(s, idx)
        saetze.append(dict(s, auch_var=mehr) if mehr else s)
    neu["saetze"] = saetze
    # Kacheln gibt es nur aus dem Lernpfad (kachelAblenker() nimmt CATEGORIES).
    app_formen = set()
    for kat in daten.get("kategorien", []):
        for w in kat.get("words", []):
            for f in _antworten(w.get("bs"), w.get("auch")):
                teile = kacheln(f)
                if len(teile) == 1:
                    app_formen.add(teile[0])
    indizes = (idx, index([dict(p, a=p["b"], b=p["a"]) for p in VARIANTEN]))
    satzbau = []
    for s in daten.get("satzbau", []):
        sperre = _kachel_sperre(s, app_formen, kacheln, indizes)
        alt = s.get("ohne")
        # Ein kaputtes "ohne" (keine Liste) bleibt, wie es ist - pruefe_vokabeln() meldet es.
        if sperre and (alt is None or isinstance(alt, list)):
            s = dict(s, ohne=list(alt or []) + [f for f in sperre if f not in (alt or [])])
        satzbau.append(s)
    neu["satzbau"] = satzbau
    return neu


def pruefe_varianten(daten):
    """Befunde wie in inhalt.pruefe_vokabeln(), das sie mit aufnimmt:
    die Liste selbst, Formen von a, die in der App ein anderes Wort sind, und
    Antworten, bei denen der Fall unklar bleibt."""
    probleme = []
    gesehen = {}
    for nr, p in enumerate(VARIANTEN):
        if set(p) != {"a", "b", "gilt", "beleg"}:
            probleme.append("Variante Nr. %d: Felder a, b, gilt, beleg - nicht %s" % (nr + 1, sorted(p)))
            continue
        name = "Variante %s / %s" % (_erste(p["a"]), _erste(p["b"]))
        a, b = p["a"], p["b"]
        if isinstance(a, str) != isinstance(b, str):
            probleme.append("%s: a und b sind nicht von derselben Art" % name)
            continue
        if isinstance(a, dict):
            if set(a) != set(b):
                probleme.append("%s: a und b haben verschiedene Schlüssel" % name)
            for k in set(a) & set(b):
                if len(a[k]) != len(FAELLE) or len(b[k]) != len(FAELLE):
                    probleme.append("%s [%s]: je %d Fälle" % (name, k, len(FAELLE)))
                elif [x is None for x in a[k]] != [x is None for x in b[k]]:
                    probleme.append("%s [%s]: None nicht an denselben Stellen" % (name, k))
        for f in list(faelle(a).values()) + list(faelle(b).values()):
            if not isinstance(f, str) or f != f.strip() or f != f.lower() or " / " in f or not f:
                probleme.append("%s: Form %r (klein, ohne ' / ', ohne Leerzeichen am Rand)" % (name, f))
        g = p["gilt"]
        if g not in (UEBERALL, ALLEIN) and not (isinstance(g, list) and g and all(isinstance(x, str) for x in g)):
            probleme.append("%s: gilt ist %r" % (name, g))
        # Dieselbe Form von a darf bei mehreren Paaren stehen (kafena: smeđa,
        # kahvena, braon), aber nicht zweimal mit demselben b.
        fb = faelle(b)
        for fall, f in faelle(a).items():
            if not isinstance(f, str) or not isinstance(fb.get(fall), str):
                continue
            schluessel = (f.lower(), fb[fall].lower())
            if schluessel in gesehen and gesehen[schluessel] != nr:
                probleme.append("%s: '%s' -> '%s' steht schon bei einem anderen Paar" % (name, f, fb[fall]))
            gesehen[schluessel] = nr

    # Formen von a, die in der App ein eigenes Wort sind (wie sto: hundert
    # und Tisch, kola: Auto und Gen. von kolo). Nur bei UEBERALL und ALLEIN -
    # ein Paar mit Kennungen gilt ohnehin nur dort, wo es steht. Steht eine
    # Grundform bei mehreren Wörtern, ist das nur ein Befund, wenn ihre
    # Bedeutungen kein Wort teilen: doktor ist „Arzt“ und „Arzt / Ärztin“.
    stichwort = {}
    for w in _alle_woerter(daten):
        for f in _antworten(w.get("bs")):
            stichwort.setdefault(f.lower(), []).append(w)
    for form, liste in index().items():
        for nr, ziele in liste:
            if VARIANTEN[nr]["gilt"] not in (UEBERALL, ALLEIN) or form not in stichwort:
                continue
            woerter = stichwort[form]
            namen = ", ".join(sorted(str(w.get("id")) for w in woerter))
            bedeutungen = [set(re.findall(r"[^\W\d_]+", _bedeutung(w).lower())) for w in woerter]
            if not any(_grundform(f) for f in ziele):
                probleme.append("Variante '%s' ist in der App ein eigenes Wort (%s), "
                                "hier aber eine gebeugte Form" % (form, namen))
            elif len(woerter) > 1 and not set.intersection(*bedeutungen):
                probleme.append("Variante '%s' steht in der App bei Wörtern mit verschiedener Bedeutung (%s)"
                                % (form, namen))

    idx = index()
    for w in _alle_woerter(daten):
        probleme += _wort_zusatz(w, idx)[1]
    for s in daten.get("saetze", []):
        probleme += _satz_zusatz(s, idx)[1]
    return probleme


def pruefe_kennungen(daten):
    """Die Kennungen unter "gilt" und in FALL gibt es
    wirklich. Nur am ganzen Inhalt sinnvoll (tests/test_varianten.py), nicht in
    pruefe_vokabeln(), das auch an kleinen Testinhalten läuft."""
    probleme = []
    woerter = {w.get("id") for w in _alle_woerter(daten)}
    luecken = {s.get("text") for s in daten.get("saetze", [])}
    for p in VARIANTEN:
        if isinstance(p.get("gilt"), list):
            for k in p["gilt"]:
                if k not in woerter and k not in luecken:
                    probleme.append("Variante: Kennung '%s' gibt es nicht" % k)
    alle_faelle = {f for p in VARIANTEN for f in faelle(p["a"])}
    for kennung, fall in FALL.items():
        if kennung not in woerter and kennung not in luecken:
            probleme.append("FALL: Kennung '%s' gibt es nicht" % kennung)
        if fall not in alle_faelle:
            probleme.append("FALL: Fall '%s' gibt es nicht" % fall)
    return probleme
