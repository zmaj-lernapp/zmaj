# -*- coding: utf-8 -*-
"""K2 und K7 in 1.5, eingebaut am 27.11.2026 (Plan 1.5, Offen-Liste, Eingang 27.11.).

Ajdin am 20.11.2026 zu K2: „mach gleich alle und lass emir direkt alle sprechen“. Seine
Antworten auf die Karten stehen in Release/Wortschatz/k2_2026-11-20/final (LIESMICH.md,
neue_woerter_final.json, ordnungszahlen_final.json, varianten_final.json); hier steht,
was davon in die App gekommen ist:

- WOERTER: 97 neue Woerter je Level, mit "auch" und Beispielsatz (None ohne Satz).
- ORDNUNGSZAHLEN: das neue Level ordnungszahlen (K7, O-F1 bis O-F4: alles ja).
- TIPPEN: die 34 Paare, die erst mit den neuen Woertern gehen (varianten.py).
- UMBENANNT: Hose heisst "pantalone / hlače", radnja "Geschäft (kleiner Laden)", dazu
  trgovina "Geschäft (großer Laden)" (Ajdin am 25.11.2026, Variante A).
- TON_OFFEN: Emir hat alles gesprochen (Stimme_Emir_neu/k2_2026-11-21/gewaehlt und
  k2_neu_2026-11-26/gewaehlt), in die Huelle und nach ton_nur_emir.json kommt es im
  Ton-Schritt. Bis dahin bleiben diese Eintraege still. Der Ton-Schritt leert die Menge.
- FRUEHER_IN_SAMMLE: Aufnahmen, die es schon gibt (Geschichte, Grammatik, Paket 5 bis 9)
  und die mit K2 auch eine Vokabel sind. ton_bauen.sammle() bringt sie jetzt frueher;
  ihre Nummer bleibt, die Pruefungen der Nummernfolge lassen sie aus.

ohne_k2() zeigt die Level so, wie die Wortschatz-Pakete sie geliefert haben (wie
grundwoerter_umzug.vor_umzug()). Was K2 selbst verspricht, prueft tests/test_k2.py.
"""

LEVEL_NEU = "ordnungszahlen"
UMBENANNT = {"hose:pantalone": "hose:pantalone / hlače",
             "geschäft:radnja": "geschäft (kleiner laden):radnja"}
GESCHAEFT_GROSS = ("Geschäft (großer Laden)", "trgovina")

WOERTER = {
    "einkaufen": [
        ("Turnschuhe", "patike", [], None),
        ("Stiefel", "čizme", [], None),
        ("Hausschuhe", "papuče", [], None),
        ("Jeans", "farmerke", [], None),
        ("Pullover", "džemper", [], None),
        ("Mantel", "kaput", [], None),
        ("Hut", "šešir", [], None),
        ("Schal", "šal", [], None),
        ("Handschuhe", "rukavice", [], None),
        ("Trainingsanzug", "trenerka", [], None),
    ],
    "essen": [
        ("Pommes", "pomfrit", [], None),
        ("Pizza", "pica", [], None),
    ],
    "wetter": [
        ("Regenschirm", "kišobran", [], None),
        ("sonnig", "sunčano", [], None),
        ("bewölkt", "oblačno", [], None),
    ],
    "tiere": [
        ("Kätzchen", "mače", [], None),
    ],
    "fragen": [
        ("Seit wann?", "Otkad?", [], None),
    ],
    "geraete": [
        ("Laptop", "laptop", [], None),
        ("Lautsprecher", "zvučnik", [], None),
        ("E-Mail", "mejl", [], None),
    ],
    "routine": [
        ("Wecker", "budilnik", [], None),
        ("Schlafanzug", "pidžama", [], None),
        ("sich rasieren", "brijati se", [], ("Ich rasiere mich", "Brijem se")),
        ("sich kämmen", "češljati se", [], ("Ich kämme mich", "Češljam se")),
        ("sich (das Gesicht) waschen", "umivati se", [], ("Ich wasche mir das Gesicht", "Umivam se")),
        ("baden / sich baden", "kupati se", [], ("Ich bade", "Kupam se")),
    ],
    "kueche_bad": [
        ("Bettlaken", "čaršaf", [], None),
    ],
    "putzen": [
        ("Schwamm", "spužva", [], None),
    ],
    "arbeit": [
        ("Kugelschreiber", "hemijska olovka", ["hemijska"], None),
        ("Lineal", "lenjir", [], None),
        ("Wort", "riječ", [], None),
        ("Spitzer", "rezač", [], None),
    ],
    "kulturlevel": [
        ("Sehur (Mahlzeit vor dem Morgengrauen im Ramadan)", "sehur", [], None),
    ],
    "resto2": [
        ("Serviette", "salveta", [], None),
    ],
    "wie_jemand_ist": [
        ("gutaussehend / hübsch", "zgodan", ["zgodna", "zgodno"], ("Dein Bruder sieht sehr gut aus.", "Tvoj brat je jako zgodan.")),
        ("sympathisch / nett", "simpatičan", ["simpatična", "simpatično"], ("Die neue Nachbarin ist sehr sympathisch.", "Nova komšinica je jako simpatična.")),
        ("langweilig (der langweilige)", "dosadan", ["dosadna", "dosadno"], ("Dieser Film ist so langweilig, dass ich eingeschlafen bin.", "Ovaj film je tako dosadan da sam zaspao.")),
    ],
    "eigenschaften": [
        ("schmutzig (der schmutzige)", "prljav", ["prljava", "prljavo"], ("Stell keinen schmutzigen Teller in den Schrank.", "Ne stavljaj prljav tanjir u ormar.")),
    ],
    "miteinander_umgehen": [
        ("scherzen / Witze machen", "šaliti se", [], ("Sei nicht böse, ich mache nur Spaß.", "Ne ljuti se, samo se šalim.")),
    ],
    "schule": [
        ("Lehrer (Grundschule)", "učitelj", [], ("Unser Lehrer hat uns das Schreiben beigebracht.", "Naš učitelj nas je naučio pisati.")),
    ],
    "sport": [
        ("Torwart", "golman", [], ("Unser Torwart ist der beste der Liga.", "Naš golman je najbolji u ligi.")),
        ("Tennis", "tenis", [], ("Samstags spiele ich mit einem Freund Tennis.", "Subotom igram tenis s prijateljem.")),
        ("Volleyball", "odbojka", [], ("Im Sommer spielen wir am Strand Volleyball.", "Ljeti na plaži igramo odbojku.")),
        ("Trikot", "dres", [], ("Ich habe meinem Sohn das Trikot der Nationalmannschaft gekauft.", "Kupio sam sinu dres reprezentacije.")),
        ("unentschieden", "neriješeno", [], ("Das Spiel endete unentschieden.", "Utakmica je završila neriješeno.")),
    ],
    "hobbys": [
        ("Schach", "šah", [], ("Opa hat mir Schach beigebracht.", "Dedo me je naučio igrati šah.")),
        ("Handyspiel / Videospiel", "igrica", [], ("Die Kinder spielen den ganzen Tag Spiele auf dem Handy.", "Djeca cijeli dan igraju igrice na mobitelu.")),
    ],
    "medien": [
        ("Zeichentrickfilm", "crtani film", ["crtani"], ("Die Kinder schauen jeden Morgen Zeichentrickfilme.", "Djeca svako jutro gledaju crtane filmove.")),
    ],
    "urlaub": [
        ("Sonnenbrille", "sunčane naočale", ["sunčane naočare"], ("Wo ist meine Sonnenbrille?", "Gdje su moje sunčane naočale?")),
        ("Badeanzug", "kupaći kostim", [], ("Pack den Badeanzug ein, wir fahren ans Meer.", "Spakuj kupaći kostim, idemo na more.")),
        ("Boot", "čamac", [], ("Wir haben auf dem See ein Boot gemietet.", "Unajmili smo čamac na jezeru.")),
    ],
    "berufe": [
        ("Fliesenleger", "keramičar", [], ("Der Fliesenleger kommt morgen, um im Bad die Fliesen zu verlegen.", "Keramičar dolazi sutra da postavi pločice u kupatilu.")),
        ("Maler (Anstreicher)", "soboslikar", [], ("Der Maler kommt am Montag, um unsere Wohnung zu streichen.", "Soboslikar dolazi u ponedjeljak da nam okreči stan.")),
    ],
    "krank_sein": [
        ("erkältet", "prehlađen", ["prehlađena"], ("Ich bin erkältet, ich kann heute nicht kommen.", "Prehlađen sam, ne mogu danas doći.")),
    ],
    "beschwerden": [
        ("niesen", "kihati", [], ("Vom Staub muss ich ständig niesen.", "Od prašine stalno kišem.")),
    ],
    "arbeitsplatz": [
        ("Erholung", "odmor", [], ("Nach so einer Woche brauche ich Erholung.", "Poslije ovakve sedmice treba mi odmor.")),
    ],
    "familie_generationen": [
        ("Enkelkind", "unuče", [], ("Wir haben unser erstes Enkelkind bekommen.", "Dobili smo prvo unuče.")),
        ("Witwer", "udovac", [], ("Opa ist schon seit zehn Jahren Witwer.", "Dedo je udovac već deset godina.")),
        ("Schwager (Bruder des Ehemanns)", "djever", [], ("Bei der Hochzeit hat der Bruder des Bräutigams die Braut begleitet.", "Na svadbi je djever pratio mladu.")),
        ("Schwager (Bruder der Ehefrau)", "šurjak", [], ("Der Bruder meiner Frau arbeitet in Deutschland.", "Moj šurjak radi u Njemačkoj.")),
        ("Schwager (Mann der Schwester der Ehefrau)", "badžo", [], ("Mit dem Mann der Schwester meiner Frau gehe ich jeden Samstag angeln.", "S badžom svake subote idem na pecanje.")),
        ("Schwägerin (Schwester des Ehemanns)", "zaova", [], ("Meine Frau versteht sich sehr gut mit ihrer Schwägerin.", "Moja žena se odlično slaže sa svojom zaovom.")),
        ("Schwägerin (Frau des Bruders des Ehemanns)", "jetrva", [], ("Meine Frau und ihre Schwägerin kochen zusammen für Bajram.", "Moja žena i njena jetrva zajedno kuhaju za Bajram.")),
        ("Schwägerin (Schwester der Ehefrau)", "balduza", [], ("Die Schwester meiner Frau kommt am Wochenende zu Besuch.", "Balduza nam dolazi u goste za vikend.")),
        ("Schwägerin (Frau des Bruders der Ehefrau)", "šurnjaja", [], ("Die Frau vom Bruder meiner Frau hat uns eine Pita gebacken.", "Šurnjaja nam je ispekla pitu.")),
    ],
    "liebe_ehe": [
        ("Ring", "prsten", [], ("Sie hat ihren Ring am Strand verloren.", "Izgubila je prsten na plaži.")),
        ("Ehering", "burma", [], ("Er trägt den Ehering an der rechten Hand.", "Nosi burmu na desnoj ruci.")),
        ("sich scheiden lassen", "razvesti se", [], ("Sie haben sich letztes Jahr scheiden lassen.", "Razveli su se prošle godine.")),
        ("geschieden", "razveden", ["razvedena"], ("Mein Nachbar ist geschieden und lebt allein.", "Moj komšija je razveden i živi sam.")),
        ("einen Heiratsantrag machen", "zaprositi", [], ("Ich habe ihr auf der Alten Brücke einen Heiratsantrag gemacht.", "Zaprosio sam je na Starom mostu.")),
        ("Heiratsantrag", "prosidba", [], ("Der Heiratsantrag war eine Überraschung für die ganze Familie.", "Prosidba je bila iznenađenje za cijelu porodicu.")),
    ],
    "gefuehle_genauer": [
        ("Neid", "zavist", [], ("Neid ist eine hässliche Eigenschaft.", "Zavist je ružna osobina.")),
        ("neidisch", "zavidan", ["zavidna", "zavidno"], ("Er ist nicht neidisch, er freut sich über den Erfolg anderer.", "Nije zavidan, raduje se tuđem uspjehu.")),
    ],
    "charakter": [
        ("großzügig", "darežljiv", ["darežljiva", "darežljivo"], ("Papa war immer großzügig zu den Nachbarn.", "Babo je uvijek bio darežljiv prema komšijama.")),
    ],
    "vertraege": [
        ("Erbschaft", "nasljedstvo", [], ("Das Haus haben sie geerbt.", "Kuću su dobili u nasljedstvo.")),
        ("erben", "naslijediti", [], ("Er hat die Wohnung von seiner Tante geerbt.", "Naslijedio je stan od tetke.")),
    ],
    "erziehung_aufwachsen": [
        ("Pubertät", "pubertet", [], ("Unser Sohn ist in die Pubertät gekommen.", "Naš sin je ušao u pubertet.")),
        ("Teenager", "tinejdžer", [], ("Als Teenager habe ich ständig Musik gehört.", "Kao tinejdžer sam stalno slušao muziku.")),
    ],
    "klima_energie": [
        ("Plastik", "plastika", [], ("Plastik verschmutzt Flüsse und das Meer.", "Plastika zagađuje rijeke i more.")),
        ("Recycling", "reciklaža", [], ("Recycling spart Energie und Rohstoffe.", "Reciklaža štedi energiju i sirovine.")),
    ],
    "zeitung_fernsehen": [
        ("Moderator (Fernsehen)", "voditelj", [], ("Der Moderator begrüßte die Gäste im Studio.", "Voditelj je pozdravio goste u studiju.")),
    ],
    "werbung": [
        ("Plakat", "plakat", [], ("An der Wand hing ein Plakat für das Konzert.", "Na zidu je visio plakat za koncert.")),
    ],
    "buerste_kamm": [
        ("Schere", "makaze", [], ("Gib mir die Schere, damit ich das Paket aufmache.", "Daj mi makaze da otvorim paket.")),
    ],
    "an_der_uni": [
        ("Mensa", "menza", [], ("Wir essen in der Mensa zu Mittag.", "Ručamo u studentskoj menzi.")),
        ("Studentenwohnheim", "studentski dom", [], ("Im ersten Jahr habe ich im Studentenwohnheim gewohnt.", "Prve godine sam živio u studentskom domu.")),
    ],
    "kreisverkehr_faehre": [
        ("Helm", "kaciga", [], ("Ohne Helm setz dich nicht aufs Motorrad.", "Bez kacige ne sjedaj na motor.")),
    ],
    "tiere_genauer": [
        ("Hai", "ajkula", [], ("Im Adriatischen Meer gibt es selten Haie.", "U Jadranskom moru rijetko ima ajkula.")),
        ("Krokodil", "krokodil", [], ("Das Krokodil lag am Flussufer.", "Krokodil je ležao na obali rijeke.")),
        ("Giraffe", "žirafa", [], ("Die Giraffe hat einen sehr langen Hals.", "Žirafa ima jako dug vrat.")),
        ("Papagei", "papagaj", [], ("Der Papagei des Nachbarn kann ein paar Wörter.", "Komšijin papagaj zna nekoliko riječi.")),
    ],
    "ernten_pflanzen": [
        ("Buche", "bukva", [], ("Die Buche ist der häufigste Baum in den bosnischen Wäldern.", "Bukva je najčešće drvo u bosanskim šumama.")),
        ("Fichte", "smreka", [], ("Auf dem Berg wachsen hohe Fichten.", "Na planini rastu visoke smreke.")),
        ("Tulpe", "lala", [], ("Im Frühling blühen im Garten Tulpen.", "U proljeće u bašti cvjetaju lale.")),
        ("Tanne", "jela", [], ("Die Tanne bleibt auch im Winter grün.", "Jela ostaje zelena i u zimi.")),
    ],
    "pflanzen_anbau": [
        ("Sonnenblume", "suncokret", [], ("Das Feld war voller Sonnenblumen.", "Polje je bilo puno suncokreta.")),
    ],
    "reisen": [
        ("Taxifahrer", "taksista", [], None),
    ],
    "trauer_beileid": [
        ("Testament", "oporuka", [], ("Opa hat vor seinem Tod ein Testament geschrieben.", "Dedo je prije smrti napisao oporuku.")),
    ],
}

# K7: je Wort (de, bs, auch, Satz), in dieser Folge im Level ordnungszahlen
ORDNUNGSZAHLEN = [
    ("der vierte", "četvrti", ["četvrta", "četvrto"], ("Wir wohnen im vierten Stock, und der Aufzug geht nicht.", "Živimo na četvrtom spratu, a lift ne radi.")),
    ("der fünfte", "peti", ["peta", "peto"], ("Mein Gehalt bekomme ich am Fünften des Monats.", "Platu dobivam petog u mjesecu.")),
    ("der sechste", "šesti", ["šesta", "šesto"], ("Mein Sohn geht in die sechste Klasse.", "Moj sin ide u šesti razred.")),
    ("der siebte", "sedmi", ["sedma", "sedmo"], ("Das ist schon das siebte Mal, dass du zu spät kommst!", "Ovo je već sedmi put da kasniš!")),
    ("der achte", "osmi", ["osma", "osmo"], ("Der achte März ist der Frauentag.", "Osmi mart je Dan žena.")),
    ("der neunte", "deveti", ["deveta", "deveto"], ("Unsere Mannschaft steht auf dem neunten Platz in der Liga.", "Naša ekipa je na devetom mjestu u ligi.")),
    ("der zehnte", "deseti", ["deseta", "deseto"], ("Ich bin am zehnten Oktober geboren.", "Rođen sam desetog oktobra.")),
    ("der elfte", "jedanaesti", ["jedanaesta", "jedanaesto"], ("Unser Büro ist im elften Stock.", "Naša kancelarija je na jedanaestom spratu.")),
    ("der zwölfte", "dvanaesti", ["dvanaesta", "dvanaesto"], ("Der Dezember ist der zwölfte Monat des Jahres.", "Decembar je dvanaesti mjesec u godini.")),
    ("der zwanzigste", "dvadeseti", ["dvadeseta", "dvadeseto"], ("Heute feiern wir den zwanzigsten Geburtstag meiner Schwester.", "Danas slavimo sestrin dvadeseti rođendan.")),
    ("der einundzwanzigste", "dvadeset prvi", ["dvadeset prva", "dvadeset prvo"], ("Wir leben im einundzwanzigsten Jahrhundert.", "Živimo u dvadeset prvom stoljeću.")),
    ("der dreißigste", "trideseti", ["trideseta", "trideseto"], ("Die Miete wird bis zum Dreißigsten des Monats bezahlt.", "Kirija se plaća do tridesetog u mjesecu.")),
    ("der fünfzigste", "pedeseti", ["pedeseta", "pedeseto"], ("Papa feiert seinen fünfzigsten Geburtstag.", "Babo slavi pedeseti rođendan.")),
    ("der hundertste", "stoti", ["stota", "stoto"], ("Das sage ich dir schon zum hundertsten Mal!", "Ovo ti govorim već stoti put!")),
    ("der tausendste", "hiljaditi", ["hiljadita", "hiljadito"], ("Er war der tausendste Besucher und hat einen Preis bekommen.", "Bio je hiljaditi posjetilac i dobio je nagradu.")),
]

# Kennung -> was dort beim Tippen unsichtbar mitzaehlt (die 34 Paare in varianten.py)
TIPPEN = {
    "jeans:farmerke": ["traperice"],
    "seit wann?:Otkad?": ["otkada", "od kada"],
    "wecker:budilnik": ["budilica"],
    "bettlaken:čaršaf": ["plahta"],
    "schwamm:spužva": ["sunđer"],
    "lineal:lenjir": ["ravnalo"],
    "serviette:salveta": ["ubrus"],
    "torwart:golman": ["vratar"],
    "niesen:kihati": ["kijati"],
    "schere:makaze": ["škare"],
    "hai:ajkula": ["morski pas"],
    "fichte:smreka": ["smrča"],
    "tulpe:lala": ["tulipan"],
    "pizza:pica": ["pizza"],
    "e-mail:mejl": ["e-mail", "imejl"],
    "taxifahrer:taksista": ["taksist"],
    "trainingsanzug:trenerka": ["trenirka"],
    "maler (anstreicher):soboslikar": ["moler"],
    "schwager (bruder des ehemanns):djever": ["dever"],
    "schwager (bruder der ehefrau):šurjak": ["šura"],
    "schwager (mann der schwester der ehefrau):badžo": ["badžanak", "pašanac"],
    "schwägerin (schwester der ehefrau):balduza": ["svastika"],
    "testament:oporuka": ["testament"],
    "spitzer:rezač": ["zarezač", "šiljilo"],
    "der einundzwanzigste:dvadeset prvi": ["dvadeset i prvi", "dvadeset i prva", "dvadeset i prvo"],
    "der tausendste:hiljaditi": ["tisućiti", "tisućita", "tisućito"],
}

# Ton-Schluessel, deren Aufnahme Emir gesprochen hat, die aber erst im Ton-Schritt in die
# Huelle und nach ton_nur_emir.json kommt (188).
TON_OFFEN = frozenset([
    "ajkula", "babo je uvijek bio darežljiv prema komšijama.", "babo slavi pedeseti rođendan.", "badžo",
    "balduza", "balduza nam dolazi u goste za vikend.", "bez kacige ne sjedaj na motor.", "bio je hiljaditi posjetilac i dobio je nagradu.",
    "brijati se", "brijem se", "budilnik", "bukva",
    "bukva je najčešće drvo u bosanskim šumama.", "burma", "crtani film", "daj mi makaze da otvorim paket.",
    "danas slavimo sestrin dvadeseti rođendan.", "darežljiv", "decembar je dvanaesti mjesec u godini.", "dedo je prije smrti napisao oporuku.",
    "dedo je udovac već deset godina.", "dedo me je naučio igrati šah.", "deseti", "deveti",
    "djeca cijeli dan igraju igrice na mobitelu.", "djeca svako jutro gledaju crtane filmove.", "djever", "dobili smo prvo unuče.",
    "dosadan", "dres", "dvadeset prvi", "dvadeseti",
    "dvanaesti", "džemper", "farmerke", "gdje su moje sunčane naočale?",
    "golman", "hemijska olovka", "hiljaditi", "igrica",
    "izgubila je prsten na plaži.", "jedanaesti", "jela ostaje zelena i u zimi.", "jetrva",
    "kaciga", "kao tinejdžer sam stalno slušao muziku.", "kaput", "keramičar",
    "keramičar dolazi sutra da postavi pločice u kupatilu.", "kihati", "kirija se plaća do tridesetog u mjesecu.", "kišobran",
    "komšijin papagaj zna nekoliko riječi.", "krokodil", "krokodil je ležao na obali rijeke.", "kupam se",
    "kupati se", "kupaći kostim", "kupio sam sinu dres reprezentacije.", "kuću su dobili u nasljedstvo.",
    "lala", "laptop", "lenjir", "ljeti na plaži igramo odbojku.",
    "makaze", "mače", "mejl", "menza",
    "moj komšija je razveden i živi sam.", "moj sin ide u šesti razred.", "moj šurjak radi u njemačkoj.", "moja žena i njena jetrva zajedno kuhaju za bajram.",
    "moja žena se odlično slaže sa svojom zaovom.", "na planini rastu visoke smreke.", "na svadbi je djever pratio mladu.", "na zidu je visio plakat za koncert.",
    "naslijedio je stan od tetke.", "naslijediti", "nasljedstvo", "naš golman je najbolji u ligi.",
    "naš sin je ušao u pubertet.", "naš učitelj nas je naučio pisati.", "naša ekipa je na devetom mjestu u ligi.", "naša kancelarija je na jedanaestom spratu.",
    "ne ljuti se, samo se šalim.", "ne stavljaj prljav tanjir u ormar.", "neriješeno", "nije zavidan, raduje se tuđem uspjehu.",
    "nosi burmu na desnoj ruci.", "nova komšinica je jako simpatična.", "od prašine stalno kišem.", "odbojka",
    "odmor", "oporuka", "osmi", "osmi mart je dan žena.",
    "otkad?", "ovaj film je tako dosadan da sam zaspao.", "ovo je već sedmi put da kasniš!", "ovo ti govorim već stoti put!",
    "papagaj", "papuče", "patike", "pedeseti",
    "peti", "pica", "pidžama", "plakat",
    "plastika", "plastika zagađuje rijeke i more.", "platu dobivam petog u mjesecu.", "polje je bilo puno suncokreta.",
    "pomfrit", "poslije ovakve sedmice treba mi odmor.", "prehlađen", "prehlađen sam, ne mogu danas doći.",
    "prljav", "prosidba", "prosidba je bila iznenađenje za cijelu porodicu.", "prsten",
    "prve godine sam živio u studentskom domu.", "pubertet", "razveden", "razveli su se prošle godine.",
    "razvesti se", "reciklaža", "reciklaža štedi energiju i sirovine.", "rezač",
    "riječ", "rođen sam desetog oktobra.", "ručamo u studentskoj menzi.", "s badžom svake subote idem na pecanje.",
    "salveta", "sehur", "simpatičan", "smreka",
    "soboslikar", "soboslikar dolazi u ponedjeljak da nam okreči stan.", "spakuj kupaći kostim, idemo na more.", "spužva",
    "stoti", "studentski dom", "subotom igram tenis s prijateljem.", "suncokret",
    "sunčane naočale", "taksista", "tenis", "tinejdžer",
    "trenerka", "trideseti", "tvoj brat je jako zgodan.", "u jadranskom moru rijetko ima ajkula.",
    "u proljeće u bašti cvjetaju lale.", "udovac", "umivam se", "umivati se",
    "unajmili smo čamac na jezeru.", "unuče", "utakmica je završila neriješeno.", "učitelj",
    "voditelj", "voditelj je pozdravio goste u studiju.", "zaova", "zaprosio sam je na starom mostu.",
    "zaprositi", "zavidan", "zavist", "zavist je ružna osobina.",
    "zgodan", "zvučnik", "čaršaf", "četvrti",
    "češljam se", "češljati se", "čizme", "šah",
    "šal", "šaliti se", "šesti", "šešir",
    "šurjak", "šurnjaja", "šurnjaja nam je ispekla pitu.", "žirafa",
    "žirafa ima jako dug vrat.", "živimo na četvrtom spratu, a lift ne radi.", "živimo u dvadeset prvom stoljeću.", "pantalone / hlače",
])

# Schluessel mit einer Aufnahme von frueher (Geschichte, Grammatik, Paket 5 bis 9), die mit K2
# auch eine Vokabel sind und darum in ton_bauen.sammle() frueher stehen. Ihre Nummer bleibt.
FRUEHER_IN_SAMMLE = frozenset(["jela", "oblačno", "rukavice", "sedmi", "sunčano", "čamac", "trgovina"])


def kennung(de, bs):
    return "%s:%s" % (de.strip().lower(), bs)


def _alle_eintraege():
    for liste in WOERTER.values():
        for de, bs, _, satz in liste:
            yield de, bs
            if satz:
                yield satz
    for de, bs, _, satz in ORDNUNGSZAHLEN:
        yield de, bs
        yield satz
    yield GESCHAEFT_GROSS


# Jede neue Kennung (194): 97 Woerter, ihre 66 Saetze, 15 Ordnungszahlen mit 15 Saetzen, trgovina.
NEU = frozenset(kennung(de, bs) for de, bs in _alle_eintraege())


def ohne_k2(daten):
    """Die Daten aus inhalt.lade_daten() ohne die neuen Eintraege und ohne das Level
    ordnungszahlen. Die Kennung haengt an der deutschen Seite, darum gilt das in jeder Sprache."""
    d = dict(daten)
    d["kategorien"] = [dict(k, words=[w for w in k["words"] if w["id"] not in NEU])
                       for k in daten["kategorien"] if k["id"] != LEVEL_NEU]
    return d
