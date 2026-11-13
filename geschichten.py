# -*- coding: utf-8 -*-
"""
geschichten.py  –  DER GESCHICHTEN-PFAD

Die Geschichten sind ein eigener Pfad neben dem Lernpfad, für alle, die auch
lesen wollen. DIE REIHENFOLGE IN DER LISTE IST DIE SCHWIERIGKEIT: die erste
Geschichte ist wie ein Kinderbuch, die letzte ist Amtssprache. Eine Geschichte
wird frei, wenn bei der vorherigen alle Fragen richtig beantwortet wurden.

Aufbau:
  WOERTERBUCH = Wort im Text (klein geschrieben, genau wie es im Text steht)
                → deutsche Bedeutung. Gilt für alle Geschichten.
  GESCHICHTEN = Liste von {
      "id", "titel",
      "stufe":        Beschriftung der Schwierigkeit (z. B. "Kinderbuch")
      "passt_zu":     Level-id aus vokabeln.py, dessen Wörter man kennen sollte
      "text":         der bosnische Text,
      "uebersetzung": die deutsche Übersetzung,
      "vokabeln":     zusätzliche Wörter nur für diese Geschichte (optional),
      "fragen":       [{"frage": "...", "optionen": [...], "richtig": "..."}]
  }

Tipp zum Schreiben neuer Geschichten: kurze Sätze, Wörter aus den Levels davor,
und jedes neue Wort ins WOERTERBUCH eintragen. start.py meldet beim Start,
welche Wörter noch fehlen.

HINWEIS: Claude ist kein Muttersprachler. Texte bitte prüfen.
"""

WOERTERBUCH = {
    # Kleine Wörter
    "i": "und", "a": "und / aber", "ali": "aber", "ili": "oder", "jer": "weil", "da": "dass / ja",
    "u": "in", "na": "auf / an", "iz": "aus", "od": "von", "do": "bis", "sa": "mit", "za": "für",
    "kod": "bei", "bez": "ohne", "o": "über", "pored": "neben", "preko": "über / hinüber", "oko": "etwa / um",
    "iza": "hinter", "tu": "hier / da", "tamo": "dort", "ovdje": "hier",
    "je": "ist", "su": "sind", "sam": "bin", "smo": "sind (wir)", "si": "bist", "ste": "sind (ihr/Sie)",
    "se": "sich", "mi": "mir / wir", "mu": "ihm", "im": "ihnen", "me": "mich", "te": "dich", "nam": "uns",
    "ne": "nicht", "nije": "ist nicht", "nema": "es gibt nicht / hat nicht",
    "to": "das", "ovo": "dies / das", "ovaj": "dieser", "ova": "diese", "onda": "dann", "prvo": "zuerst",
    "poslije": "danach / nach", "prije": "vor / früher", "sada": "jetzt", "već": "schon", "još": "noch",
    "kući": "Haus (Lok.) / nach Hause", "zajedno": "zusammen", "kraju": "Ende (Lok.)",
    "sve": "alles", "svaki": "jeder", "mnogo": "viel / viele", "malo": "wenig / ein bisschen", "nešto": "etwas",
    "moj": "mein", "moja": "meine", "moje": "mein (s)", "moju": "meine (Akk.)", "mog": "meines / meinen",
    "tvoj": "dein", "tvoja": "deine", "naš": "unser", "naša": "unsere", "našu": "unsere (Akk.)", "njegov": "sein", "njen": "ihr",
    "on": "er", "ona": "sie", "oni": "sie (Mehrzahl)", "ja": "ich", "ti": "du", "vi": "ihr / Sie", "tebe": "dich / dir", "sebi": "sich",
    "koliko": "wie viel", "koji": "welche", "gdje": "wo", "kada": "wann", "šta": "was", "ko": "wer", "kako": "wie",
    "danas": "heute", "jučer": "gestern", "sutra": "morgen", "navečer": "abends", "ujutro": "morgens",
    "rano": "früh", "kasno": "spät", "duže": "länger", "ponekad": "manchmal", "uvijek": "immer", "brzo": "schnell",
    "jedan": "ein", "jedna": "eine", "jedno": "ein (s)", "jednu": "eine (Akk.)", "jednog": "einen", "jednoj": "einer (Lok.)",
    "dva": "zwei", "dvije": "zwei (w)", "tri": "drei", "četiri": "vier", "pet": "fünf", "sedam": "sieben", "osam": "acht",
    "deset": "zehn", "jedanaest": "elf", "dvanaest": "zwölf", "šesnaest": "sechzehn", "dvadeset": "zwanzig",
    "osamdeset": "achtzig", "hiljada": "tausend", "petog": "am fünften",
    "sati": "Uhr / Stunden", "minuta": "Minuten", "godina": "Jahre", "godine": "Jahre / Jahr (Gen.)", "dana": "Tage", "dan": "Tag",
    "sedmice": "Woche (Gen.)", "sljedeće": "nächste", "sljedećeg": "nächsten (Gen.)", "prošle": "letzte", "subota": "Samstag",
    "vikendom": "am Wochenende", "mjeseca": "Monat (Gen.)", "mjesecu": "Monat (Lok.)", "augustu": "August (Lok.)",
    "vrijeme": "Zeit / Wetter", "bi": "würde",

    # Verben (Formen, wie sie im Text stehen)
    "zovem": "ich heiße / ich rufe", "zove": "er/sie heißt", "imam": "ich habe", "ima": "er/sie hat / es gibt",
    "imamo": "wir haben", "žive": "sie leben", "volim": "ich liebe", "voli": "er/sie liebt", "ide": "er/sie geht", "idu": "sie gehen",
    "idem": "ich gehe", "idemo": "wir gehen", "kupuje": "er/sie kauft", "kupujem": "ich kaufe", "kupiti": "kaufen",
    "pita": "er/sie fragt", "kaže": "er/sie sagt", "koštaju": "sie kosten", "košta": "es kostet",
    "uzima": "er/sie nimmt", "plaća": "er/sie bezahlt", "ustajem": "ich stehe auf", "tuširam": "ich dusche",
    "doručkujem": "ich frühstücke", "jedem": "ich esse", "jede": "er/sie isst", "jedu": "sie essen", "pijem": "ich trinke",
    "piju": "sie trinken", "radim": "ich arbeite", "kuham": "ich koche", "gledam": "ich schaue",
    "gledaju": "sie schauen", "čitam": "ich lese", "spavam": "ich schlafe", "spava": "er/sie schläft", "spavati": "schlafen",
    "šetaju": "sie spazieren", "sjede": "sie sitzen", "treba": "er/sie braucht", "trebam": "ich brauche",
    "trebate": "Sie brauchen", "trebaju": "sie brauchen", "popunjava": "er/sie füllt aus",
    "potpisuje": "er/sie unterschreibt", "potpisuju": "sie unterschreiben", "žele": "sie möchten",
    "pokazuje": "er/sie zeigt", "pokazala": "gezeigt (w)", "pregovaraju": "sie verhandeln",
    "dogovaraju": "sie vereinbaren", "putovat": "reisen (Zukunft)", "ćemo": "wir werden", "će": "er/sie wird", "ću": "ich werde", "ćeš": "du wirst",
    "prenoćiti": "übernachten", "voziti": "fahren", "ostati": "bleiben", "raduje": "freut sich",
    "nazvat": "anrufen (Zukunft)", "stignemo": "wir ankommen", "traje": "es dauert", "trči": "er/sie rennt", "smije": "er/sie lacht",
    "bio": "war (m)", "bila": "war (w)", "bilo": "war (s)", "bili": "waren", "ustala": "aufgestanden (w)",
    "otišla": "weggegangen (w)", "kupila": "gekauft (w)", "pile": "getrunken haben (w. Mehrz.)",
    "pričale": "geredet haben (w. Mehrz.)", "došao": "gekommen (m)", "kuhali": "gekocht haben",
    "jeste": "ja, ist es", "upisana": "eingetragen", "počela": "begonnen (w)", "razumijem": "ich verstehe",
    "govore": "sie sprechen", "govorim": "ich spreche", "naučiti": "erlernen", "učim": "ich lerne", "mislim": "ich denke",
    "doći": "kommen", "nadam": "ich hoffe", "skuhati": "kochen", "pozdravi": "grüße", "recite": "sagen Sie",
    "odgovara": "er/sie antwortet", "završila": "abgeschlossen (w)", "željela": "wollte (w)", "zarađivati": "verdienen",
    "mogla": "könnte (w)", "početi": "anfangen", "može": "er/sie kann", "objašnjava": "er/sie erklärt",
    "isplaćuje": "wird ausgezahlt", "zahvaljuje": "er/sie bedankt sich", "čekati": "warten",

    # Substantive und Adjektive
    "porodica": "Familie", "porodicu": "Familie (Akk.)", "porodici": "Familie (Lok.)", "muž": "Ehemann",
    "inženjer": "Ingenieur", "brata": "Bruder (Akk.)", "brat": "Bruder", "sestru": "Schwester (Akk.)",
    "sestra": "Schwester", "majka": "Mutter", "nastavnica": "Lehrerin", "babo": "Papa", "pčelar": "Imker",
    "nana": "Oma", "nanu": "Oma (Akk.)", "nani": "Oma (Dat.)", "nane": "Oma (Gen.)", "nano": "Oma! (Anrede)", "dedo": "Opa", "dedu": "Opa (Akk.)",
    "amidže": "Onkel (Gen.)", "djevojčica": "Mädchen", "pas": "Hund", "psa": "Hund (Akk.)",
    "velika": "groß (w)", "veliku": "große (Akk.)", "lijep": "schön (m)", "lijepo": "schön", "stare": "alte",
    "staru": "altes (Akk.)", "starog": "alten", "maloj": "kleinen (Lok.)", "mali": "klein (m)", "dobar": "gut (m)", "dobro": "gut",
    "gotova": "fertig", "jeftinije": "billiger", "stari": "alte / Alt-", "kafen": "braun (m)", "kafena": "braun (w)", "kafeno": "braun (s)", "boja": "Farbe", "bijela": "weiß (w)",
    "žuta": "gelb (w)", "plava": "blau (w)", "novi": "neuen", "draga": "liebe", "ljubazne": "freundlich (Mehrz.)",
    "grad": "Stadt", "grada": "Stadt (Gen.)", "gradu": "Stadt (Lok.)", "park": "Park", "parku": "Park (Lok.)", "sunce": "Sonne",
    "pijacu": "Markt (Akk.)", "pijaci": "Markt (Lok.)", "voća": "Obst (Gen.)", "voće": "Obst", "povrća": "Gemüse (Gen.)",
    "jabuke": "Äpfel", "jabuku": "Apfel (Akk.)", "paradajz": "Tomate", "luk": "Zwiebel", "marke": "Mark (Währung)", "maraka": "Mark (Gen. Mehrz.)",
    "kilogram": "Kilo", "kilograma": "Kilo (Gen.)", "prodavač": "Verkäufer", "hljeb": "Brot", "sir": "Käse",
    "sirom": "Käse (Instr.)", "gotovinom": "bar (mit Bargeld)", "doručak": "Frühstück", "kahvu": "Kaffee (Akk.)",
    "kahva": "Kaffee", "ćevape": "Ćevapi (Akk.)", "pitu": "Pita (Akk.)", "posao": "Arbeit", "posla": "Arbeit (Gen.)",
    "kancelariji": "Büro (Lok.)", "firmi": "Firma (Lok.)", "kolege": "Kollegen", "direktor": "Direktor / Chef",
    "kupovinu": "Einkauf (Akk.)", "večeru": "Abendessen (Akk.)", "televiziju": "Fernsehen (Akk.)", "knjigu": "Buch (Akk.)",
    "hotel": "Hotel", "centru": "Zentrum (Lok.)", "rijeke": "Fluss (Gen.)", "baščaršiju": "Baščaršija (Altstadt)",
    "ručka": "Mittagessen (Gen.)", "mosta": "Brücke (Gen.)", "poklon": "Geschenk", "radnji": "Laden (Lok.)",
    "balkonu": "Balkon (Lok.)", "cvijeće": "Blumen", "cvijeća": "Blumen (Gen.)", "slike": "Bilder", "prirodu": "Natur (Akk.)",
    "autom": "mit dem Auto", "avionom": "mit dem Flugzeug", "vožnja": "Fahrt", "zagrebu": "Zagreb (Lok.)",
    "sarajeva": "Sarajevo (Gen.)", "sarajevu": "Sarajevo (Lok.)", "sarajevo": "Sarajevo",
    "more": "Meer", "bosnu": "Bosnien (Akk.)", "bosni": "Bosnien (Lok.)", "toga": "dessen / danach",
    "kuća": "Haus", "kuću": "Haus (Akk.)", "vrata": "Tür", "prozora": "Fenster (Gen. Mehrz.)",
    "kuhinja": "Küche", "kuhinju": "Küche (Akk.)", "sto": "Tisch", "stolice": "Stühle", "soba": "Zimmer", "sobi": "Zimmer (Lok.)",
    "sobe": "Zimmer (Mehrz.)", "krevet": "Bett", "lampa": "Lampe", "bašta": "Garten", "bašti": "Garten (Lok.)", "baštu": "Garten (Akk.)",
    "drvo": "Baum", "selu": "Dorf (Lok.)", "cijena": "Preis", "cijeni": "Preis (Lok.)",
    "potvrdu": "Bescheinigung (Akk.)", "potvrda": "Bescheinigung", "prebivalištu": "Wohnsitz (Lok.)",
    "općinu": "Gemeindeamt (Akk.)", "šalteru": "Schalter (Lok.)", "dokumenti": "Dokumente", "službenica": "Beamtin",
    "ličnu": "Personal- (Akk.)", "kartu": "Karte / Ausweis (Akk.)", "obrazac": "Formular", "taksa": "Gebühr",
    "taksu": "Gebühr (Akk.)", "pomoći": "Hilfe (Lok.) / helfen", "hvala": "danke", "vam": "Ihnen", "molim": "bitte",
    "agent": "Makler", "nekretnine": "Immobilien", "gruntovnicu": "Grundbuch (Akk.)", "kaparu": "Anzahlung (Akk.)",
    "kupoprodajni": "Kauf-", "ugovor": "Vertrag", "notara": "Notar (Gen.)",
    "razgovor": "Gespräch", "ekonomiju": "Wirtschaft (Akk.)", "iskustva": "Erfahrung (Gen.)",
    "računovodstvu": "Buchhaltung (Lok.)", "njemački": "Deutsch (Sprache)", "engleski": "Englisch", "bosanski": "Bosnisch",
    "uslove": "Bedingungen (Akk.)", "probni": "Probe-", "rad": "Arbeit", "radno": "Arbeits-", "plata": "Gehalt", "odgovor": "Antwort",
    "amina": "Amina (Name)", "ajdin": "Ajdin (Name)", "mira": "Mira (Name)", "rex": "Rex (Hundename)",
}

GESCHICHTEN = [
    {
        "id": "mira", "titel": "Mira i Rex", "stufe": "Kinderbuch", "passt_zu": "farben",
        "text": "Ovo je Mira. Mira je djevojčica. Mira ima psa. Pas se zove Rex. Rex je kafen i mali. Mira voli Rexa. Rex voli Miru. "
                "Mira i Rex idu u park. U parku je sunce. Rex trči. Mira se smije. Onda idu kući. Mira jede jabuku. Rex spava.",
        "uebersetzung": "Das ist Mira. Mira ist ein Mädchen. Mira hat einen Hund. Der Hund heißt Rex. Rex ist braun und klein. Mira liebt Rex. Rex liebt Mira. "
                "Mira und Rex gehen in den Park. Im Park scheint die Sonne. Rex rennt. Mira lacht. Dann gehen sie nach Hause. Mira isst einen Apfel. Rex schläft.",
        "vokabeln": {"rexa": "Rex (Akk.)", "miru": "Mira (Akk.)"},
        "fragen": [
            {"frage": "Wie heißt der Hund?", "optionen": ["Rex", "Mira", "Emir"], "richtig": "Rex"},
            {"frage": "Welche Farbe hat Rex?", "optionen": ["braun", "weiß", "schwarz"], "richtig": "braun"},
            {"frage": "Was isst Mira?", "optionen": ["einen Apfel", "Brot", "Käse"], "richtig": "einen Apfel"},
        ],
    },
    {
        "id": "kuca1", "titel": "Naša kuća", "stufe": "Kinderbuch", "passt_zu": "zuhause",
        "text": "Ovo je naša kuća. Kuća je bijela. Ima velika vrata i četiri prozora. U kući je kuhinja. Kuhinja je žuta. Tu su sto i četiri stolice. "
                "Moja soba je plava. U sobi su krevet i lampa. Iza kuće je bašta. U bašti su jedno drvo i mnogo cvijeća. Volim našu kuću.",
        "uebersetzung": "Das ist unser Haus. Das Haus ist weiß. Es hat eine große Tür und vier Fenster. Im Haus ist eine Küche. Die Küche ist gelb. Da sind ein Tisch und vier Stühle. "
                "Mein Zimmer ist blau. Im Zimmer sind ein Bett und eine Lampe. Hinter dem Haus ist ein Garten. Im Garten sind ein Baum und viele Blumen. Ich liebe unser Haus.",
        "vokabeln": {"kuće": "Haus (Gen.)"},
        "fragen": [
            {"frage": "Welche Farbe hat das Haus?", "optionen": ["weiß", "gelb", "blau"], "richtig": "weiß"},
            {"frage": "Wie viele Fenster hat es?", "optionen": ["vier", "zwei", "sieben"], "richtig": "vier"},
            {"frage": "Was ist hinter dem Haus?", "optionen": ["ein Garten", "ein Park", "eine Straße"], "richtig": "ein Garten"},
        ],
    },
    {
        "id": "porodica", "titel": "Moja porodica", "stufe": "Einfach", "passt_zu": "familie",
        "text": "Zovem se Amina. Imam dvadeset pet godina. Moja porodica je velika. Moj muž se zove Ajdin. On je inženjer. "
                "Imam jednog brata i jednu sestru. Moj brat se zove Emir, a moja sestra se zove Lejla. "
                "Moja majka je nastavnica, a moj babo je pčelar. Moja nana i moj dedo žive u Bosni. Volim svoju porodicu.",
        "uebersetzung": "Ich heiße Amina. Ich bin 25 Jahre alt. Meine Familie ist groß. Mein Mann heißt Ajdin. Er ist Ingenieur. "
                "Ich habe einen Bruder und eine Schwester. Mein Bruder heißt Emir und meine Schwester heißt Lejla. "
                "Meine Mutter ist Lehrerin und mein Papa ist Imker. Meine Oma und mein Opa leben in Bosnien. Ich liebe meine Familie.",
        "vokabeln": {"svoju": "meine eigene (Akk.)", "emir": "Emir (Name)", "lejla": "Lejla (Name)"},
        "fragen": [
            {"frage": "Wie alt ist Amina?", "optionen": ["25", "20", "35"], "richtig": "25"},
            {"frage": "Was ist Ajdin von Beruf?", "optionen": ["Ingenieur", "Imker", "Lehrer"], "richtig": "Ingenieur"},
            {"frage": "Wo leben Oma und Opa?", "optionen": ["in Bosnien", "in Deutschland", "bei Amina"], "richtig": "in Bosnien"},
        ],
    },
    {
        "id": "pijaca", "titel": "Na pijaci", "stufe": "Einfach", "passt_zu": "einkaufen",
        "text": "Danas je subota. Amina ide na pijacu. Na pijaci ima mnogo voća i povrća. Amina kupuje jabuke, paradajz i luk. "
                "„Koliko koštaju jabuke?“ pita Amina. „Dvije marke za kilogram“, kaže prodavač. Amina uzima dva kilograma. "
                "Onda kupuje hljeb i sir. Sve zajedno košta deset maraka. Amina plaća gotovinom i ide kući.",
        "uebersetzung": "Heute ist Samstag. Amina geht auf den Markt. Auf dem Markt gibt es viel Obst und Gemüse. Amina kauft Äpfel, Tomaten und Zwiebeln. "
                "„Wie viel kosten die Äpfel?“ fragt Amina. „Zwei Mark pro Kilo“, sagt der Verkäufer. Amina nimmt zwei Kilo. "
                "Dann kauft sie Brot und Käse. Alles zusammen kostet zehn Mark. Amina zahlt bar und geht nach Hause.",
        "fragen": [
            {"frage": "Welcher Tag ist heute?", "optionen": ["Samstag", "Sonntag", "Montag"], "richtig": "Samstag"},
            {"frage": "Wie viel kostet ein Kilo Äpfel?", "optionen": ["zwei Mark", "zehn Mark", "fünf Mark"], "richtig": "zwei Mark"},
            {"frage": "Wie bezahlt Amina?", "optionen": ["bar", "mit Karte", "gar nicht"], "richtig": "bar"},
        ],
    },
    {
        "id": "dan", "titel": "Moj dan", "stufe": "Einfach", "passt_zu": "routine",
        "text": "Svaki dan ustajem u sedam sati. Prvo se tuširam, a onda doručkujem. Za doručak jedem hljeb sa sirom i pijem kahvu. "
                "U osam idem na posao. Radim u kancelariji do četiri. Poslije posla idem u kupovinu. Navečer kuham večeru i gledam televiziju. "
                "Ponekad čitam knjigu. Idem spavati u jedanaest. Vikendom spavam duže.",
        "uebersetzung": "Jeden Tag stehe ich um sieben Uhr auf. Zuerst dusche ich, dann frühstücke ich. Zum Frühstück esse ich Brot mit Käse und trinke Kaffee. "
                "Um acht gehe ich zur Arbeit. Ich arbeite im Büro bis vier. Nach der Arbeit gehe ich einkaufen. Abends koche ich Abendessen und sehe fern. "
                "Manchmal lese ich ein Buch. Ich gehe um elf schlafen. Am Wochenende schlafe ich länger.",
        "fragen": [
            {"frage": "Wann steht sie auf?", "optionen": ["um sieben", "um acht", "um elf"], "richtig": "um sieben"},
            {"frage": "Bis wann arbeitet sie?", "optionen": ["bis vier", "bis acht", "bis elf"], "richtig": "bis vier"},
            {"frage": "Was macht sie am Wochenende?", "optionen": ["länger schlafen", "arbeiten", "einkaufen"], "richtig": "länger schlafen"},
        ],
    },
    {
        "id": "grad", "titel": "U gradu", "stufe": "Mittel", "passt_zu": "praepositionen",
        "text": "Ajdin i Amina su u Sarajevu. Hotel je u centru grada, pored rijeke. Ujutro idu na Baščaršiju. Tamo piju kahvu i jedu ćevape. "
                "Poslije ručka šetaju preko starog mosta. Amina kupuje poklon za nanu u maloj radnji. "
                "Navečer sjede na balkonu i gledaju grad. „Sarajevo je lijep grad“, kaže Amina.",
        "uebersetzung": "Ajdin und Amina sind in Sarajevo. Das Hotel ist im Zentrum der Stadt, neben dem Fluss. Morgens gehen sie zur Baščaršija. Dort trinken sie Kaffee und essen Ćevapi. "
                "Nach dem Mittagessen spazieren sie über die alte Brücke. Amina kauft in einem kleinen Laden ein Geschenk für die Oma. "
                "Abends sitzen sie auf dem Balkon und schauen auf die Stadt. „Sarajevo ist eine schöne Stadt“, sagt Amina.",
        "fragen": [
            {"frage": "Wo ist das Hotel?", "optionen": ["im Zentrum, neben dem Fluss", "auf dem Berg", "am Bahnhof"], "richtig": "im Zentrum, neben dem Fluss"},
            {"frage": "Was essen sie auf der Baščaršija?", "optionen": ["Ćevapi", "Pita", "Suppe"], "richtig": "Ćevapi"},
            {"frage": "Für wen ist das Geschenk?", "optionen": ["für die Oma", "für den Bruder", "für Ajdin"], "richtig": "für die Oma"},
        ],
    },
    {
        "id": "jucer", "titel": "Jučer", "stufe": "Mittel", "passt_zu": "vergangenheit",
        "text": "Jučer je bio lijep dan. Ustala sam rano i otišla na pijacu. Kupila sam voće i cvijeće. Poslije sam bila kod nane. "
                "Pile smo kahvu i pričale o porodici. Nana mi je pokazala stare slike. Navečer je došao Ajdin i zajedno smo kuhali večeru. "
                "Bio je to dobar dan.",
        "uebersetzung": "Gestern war ein schöner Tag. Ich bin früh aufgestanden und auf den Markt gegangen. Ich habe Obst und Blumen gekauft. Danach war ich bei der Oma. "
                "Wir haben Kaffee getrunken und über die Familie geredet. Die Oma hat mir alte Bilder gezeigt. Abends kam Ajdin und wir haben zusammen Abendessen gekocht. "
                "Das war ein guter Tag.",
        "fragen": [
            {"frage": "Wo war sie nach dem Markt?", "optionen": ["bei der Oma", "bei der Arbeit", "zu Hause"], "richtig": "bei der Oma"},
            {"frage": "Was hat die Oma gezeigt?", "optionen": ["alte Bilder", "den Garten", "ein Buch"], "richtig": "alte Bilder"},
            {"frage": "Wer hat abends gekocht?", "optionen": ["Amina und Ajdin zusammen", "nur die Oma", "niemand"], "richtig": "Amina und Ajdin zusammen"},
        ],
    },
    {
        "id": "put", "titel": "Put u Bosnu", "stufe": "Mittel", "passt_zu": "reisen",
        "text": "Sljedeće sedmice idemo u Bosnu. Putovat ćemo autom jer je jeftinije nego avionom. Vožnja traje oko dvanaest sati. "
                "Prvo ćemo prenoćiti u Zagrebu. Onda ćemo voziti do Sarajeva. U Sarajevu ćemo ostati tri dana kod amidže. "
                "Poslije toga idemo na more. Amina se već raduje. Nazvat ćemo nanu kad stignemo.",
        "uebersetzung": "Nächste Woche fahren wir nach Bosnien. Wir werden mit dem Auto reisen, weil es billiger ist als mit dem Flugzeug. Die Fahrt dauert etwa zwölf Stunden. "
                "Zuerst werden wir in Zagreb übernachten. Dann fahren wir bis Sarajevo. In Sarajevo bleiben wir drei Tage beim Onkel. "
                "Danach fahren wir ans Meer. Amina freut sich schon. Wir rufen die Oma an, wenn wir ankommen.",
        "vokabeln": {"nego": "als (Vergleich)", "kad": "wenn / als"},
        "fragen": [
            {"frage": "Womit reisen sie?", "optionen": ["mit dem Auto", "mit dem Flugzeug", "mit dem Bus"], "richtig": "mit dem Auto"},
            {"frage": "Wie lange dauert die Fahrt?", "optionen": ["etwa 12 Stunden", "etwa 3 Stunden", "2 Tage"], "richtig": "etwa 12 Stunden"},
            {"frage": "Bei wem bleiben sie in Sarajevo?", "optionen": ["beim Onkel", "bei der Oma", "im Hotel"], "richtig": "beim Onkel"},
        ],
    },
    {
        "id": "pismo", "titel": "Pismo nani", "stufe": "Fortgeschritten", "passt_zu": "zukunft",
        "text": "Draga nano, kako si? Mi smo dobro. Prošle sedmice sam počela novi posao u jednoj firmi u centru grada. "
                "Kolege su ljubazne, ali još ne razumijem sve jer govore brzo. Ajdin kaže da ću naučiti. "
                "Navečer učim bosanski, a vikendom idemo u prirodu. Mislim da ćemo u augustu doći kod tebe. "
                "Nadam se da ćeš nam skuhati pitu! Pozdravi dedu. Volim te, tvoja Amina.",
        "uebersetzung": "Liebe Oma, wie geht es dir? Uns geht es gut. Letzte Woche habe ich eine neue Arbeit in einer Firma im Stadtzentrum begonnen. "
                "Die Kollegen sind freundlich, aber ich verstehe noch nicht alles, weil sie schnell sprechen. Ajdin sagt, dass ich es lernen werde. "
                "Abends lerne ich Bosnisch, und am Wochenende gehen wir in die Natur. Ich denke, dass wir im August zu dir kommen. "
                "Ich hoffe, dass du uns eine Pita kochst! Grüß den Opa. Ich liebe dich, deine Amina.",
        "fragen": [
            {"frage": "Was hat Amina letzte Woche begonnen?", "optionen": ["eine neue Arbeit", "einen Sprachkurs", "eine Reise"], "richtig": "eine neue Arbeit"},
            {"frage": "Warum versteht sie nicht alles?", "optionen": ["die Kollegen sprechen schnell", "sie ist müde", "sie hört nicht zu"], "richtig": "die Kollegen sprechen schnell"},
            {"frage": "Wann wollen sie zur Oma kommen?", "optionen": ["im August", "nächste Woche", "im Winter"], "richtig": "im August"},
        ],
    },
    {
        "id": "opcina", "titel": "Na općini", "stufe": "Amtssprache", "passt_zu": "amt",
        "text": "Amina treba potvrdu o prebivalištu. Ide na općinu u osam sati. Na šalteru pita: „Dobar dan, trebam potvrdu o prebivalištu. Koji dokumenti mi trebaju?“ "
                "Službenica kaže: „Trebate ličnu kartu i obrazac. Taksa je pet maraka.“ Amina popunjava obrazac i potpisuje. Onda plaća taksu. "
                "Potvrda je gotova za deset minuta. „Hvala Vam na pomoći“, kaže Amina.",
        "uebersetzung": "Amina braucht eine Wohnsitzbescheinigung. Sie geht um acht Uhr zum Gemeindeamt. Am Schalter fragt sie: „Guten Tag, ich brauche eine Wohnsitzbescheinigung. Welche Dokumente brauche ich?“ "
                "Die Beamtin sagt: „Sie brauchen den Personalausweis und das Formular. Die Gebühr beträgt fünf Mark.“ Amina füllt das Formular aus und unterschreibt. Dann zahlt sie die Gebühr. "
                "Die Bescheinigung ist in zehn Minuten fertig. „Danke für Ihre Hilfe“, sagt Amina.",
        "fragen": [
            {"frage": "Was braucht Amina?", "optionen": ["eine Wohnsitzbescheinigung", "einen Reisepass", "einen Führerschein"], "richtig": "eine Wohnsitzbescheinigung"},
            {"frage": "Welche Dokumente braucht sie?", "optionen": ["Personalausweis und Formular", "Reisepass und Foto", "nur Geld"], "richtig": "Personalausweis und Formular"},
            {"frage": "Wie hoch ist die Gebühr?", "optionen": ["fünf Mark", "zehn Mark", "keine"], "richtig": "fünf Mark"},
        ],
    },
    {
        "id": "kuca", "titel": "Kupujemo kuću", "stufe": "Amtssprache", "passt_zu": "immobilien",
        "text": "Ajdin i Amina žele kupiti kuću u Bosni. Agent za nekretnine im pokazuje staru kuću na selu. Kuća ima tri sobe, veliku kuhinju i baštu. "
                "Cijena je osamdeset hiljada maraka. Ajdin pita: „Je li kuća upisana u gruntovnicu?“ Agent kaže da jeste. "
                "Oni pregovaraju o cijeni i dogovaraju kaparu. Sljedeće sedmice potpisuju kupoprodajni ugovor kod notara.",
        "uebersetzung": "Ajdin und Amina möchten ein Haus in Bosnien kaufen. Der Immobilienmakler zeigt ihnen ein altes Haus auf dem Dorf. Das Haus hat drei Zimmer, eine große Küche und einen Garten. "
                "Der Preis beträgt achtzigtausend Mark. Ajdin fragt: „Ist das Haus im Grundbuch eingetragen?“ Der Makler sagt, ja. "
                "Sie verhandeln über den Preis und vereinbaren eine Anzahlung. Nächste Woche unterschreiben sie den Kaufvertrag beim Notar.",
        "vokabeln": {"li": "(Fragepartikel)"},
        "fragen": [
            {"frage": "Wo steht das Haus?", "optionen": ["auf dem Dorf", "in der Stadt", "am Meer"], "richtig": "auf dem Dorf"},
            {"frage": "Wie viel kostet es?", "optionen": ["80.000 Mark", "8.000 Mark", "800.000 Mark"], "richtig": "80.000 Mark"},
            {"frage": "Wo unterschreiben sie den Vertrag?", "optionen": ["beim Notar", "auf dem Gemeindeamt", "bei der Bank"], "richtig": "beim Notar"},
        ],
    },
    {
        "id": "intervju", "titel": "Razgovor za posao", "stufe": "Amtssprache", "passt_zu": "arbeitsvertrag",
        "text": "Amina ima razgovor za posao u jednoj firmi. Direktor je pita: „Recite nam nešto o sebi.“ "
                "Amina odgovara: „Završila sam ekonomiju i imam tri godine iskustva u računovodstvu. Govorim njemački, engleski i malo bosanski.“ "
                "Direktor pita koliko bi željela zarađivati i kada bi mogla početi. Amina kaže da može početi sljedećeg mjeseca. "
                "Na kraju direktor objašnjava uslove: probni rad traje tri mjeseca, radno vrijeme je od osam do šesnaest sati, a plata se isplaćuje petog u mjesecu. "
                "Amina zahvaljuje i kaže da će čekati odgovor.",
        "uebersetzung": "Amina hat ein Vorstellungsgespräch in einer Firma. Der Direktor fragt sie: „Erzählen Sie uns etwas über sich.“ "
                "Amina antwortet: „Ich habe Wirtschaft studiert und habe drei Jahre Erfahrung in der Buchhaltung. Ich spreche Deutsch, Englisch und ein bisschen Bosnisch.“ "
                "Der Direktor fragt, wie viel sie verdienen möchte und wann sie anfangen könnte. Amina sagt, dass sie nächsten Monat anfangen kann. "
                "Am Ende erklärt der Direktor die Bedingungen: Die Probezeit dauert drei Monate, die Arbeitszeit ist von acht bis sechzehn Uhr, und das Gehalt wird am Fünften des Monats gezahlt. "
                "Amina bedankt sich und sagt, dass sie auf die Antwort warten wird.",
        "fragen": [
            {"frage": "Wie viele Jahre Erfahrung hat Amina?", "optionen": ["drei", "fünf", "zehn"], "richtig": "drei"},
            {"frage": "Wie lange dauert die Probezeit?", "optionen": ["drei Monate", "einen Monat", "ein Jahr"], "richtig": "drei Monate"},
            {"frage": "Wann wird das Gehalt gezahlt?", "optionen": ["am Fünften des Monats", "am Monatsende", "jede Woche"], "richtig": "am Fünften des Monats"},
        ],
    },
]


# ---------------------------------------------------------------------------
# B1-LESETEXTE, PAKETE 3 UND 4 (13.11.2026)
#
# Acht Lesetexte für die neue Stufe "B1", je 150 bis 200 Wörter, ijekavisch.
# Sie stehen hinter allen anderen Geschichten und werden wie diese der Reihe
# nach frei. Vorlage: Release\Entscheidungen_2026-11-13\lesetexte_proben.md
# (Entscheidung 14a/15a/16a vom 13.11.2026).
#
# Absätze stehen wie in Paket 1 und 2 als Leerzeile ("\n\n") in Text und
# Übersetzung, die App zeigt sie (white-space: pre-line). Sie gehören zum
# Ton-Schlüssel: erst Absätze, dann ton_bauen.py, sonst spricht Azure zweimal.
# Die Ablenker der Fragen sind ähnlich lang wie die richtige Antwort, weil
# renderChoice() Antworten über 14 Zeichen kleiner setzt (Prüfung 13.11.2026).
#
# WOERTERBUCH_B1_2 sind die Wortformen dieser Texte, die im WOERTERBUCH oben
# noch fehlten. Steht ein Wort schon im WOERTERBUCH, gilt der Eintrag dort.
# Die Aufnahmen fehlen noch (ton_bauen.py, dann wortzeiten_holen.py), siehe
# WARTET_AUF_TON in tests/test_wortzeiten.py.
#
# HINWEIS: Claude ist kein Muttersprachler. Texte bitte prüfen.
# ---------------------------------------------------------------------------
WOERTERBUCH_B1_2 = {
    # b1_doktor
    "amar": "Amar (Name)", "osjeća": "er/sie fühlt sich", "boli": "es tut weh", "ga": "ihn",
    "grlo": "Hals (innen) / Kehle", "temperaturu": "Fieber (Akk.)", "stalno": "ständig", "umoran": "müde (m)",
    "ponedjeljak": "Montag", "nazvao": "angerufen (m)", "dom": "Heim (dom zdravlja: Gesundheitszentrum)",
    "zdravlja": "Gesundheit (Gen.)", "zakazao": "vereinbart (m)", "termin": "Termin", "doktorice": "Ärztin (Gen.)",
    "čekaonici": "Wartezimmer (Lok.)", "ljudi": "Leute", "amara": "Amar (Gen.)", "sjedio": "gesessen (m)",
    "stariji": "älter", "čovjek": "Mensch", "kašljao": "gehustet (m)", "vas": "euch / Sie", "pitao": "gefragt (m)",
    "odgovorio": "geantwortet (m)", "svi": "alle", "bolesni": "krank (Mehrz.)", "ovog": "dieses (Gen.)",
    "kad": "als / wenn (zeitlich)", "red": "Reihe (doći na red: drankommen)", "doktorica": "Arzt / Ärztin",
    "pitala": "gefragt (w)", "joj": "ihr (Dativ)", "objasnio": "erklärt (m)", "pregledala": "untersucht (w)",
    "izmjerila": "gemessen (w)", "imate": "ihr habt / Sie haben", "upalu": "Entzündung (Akk.)", "grla": "Hals (Gen.)",
    "ništa": "Nichts", "ozbiljno": "ernst", "morate": "ihr müsst / Sie müssen", "odmarati": "sich ausruhen",
    "dat": "geben (Zukunft)", "recept": "Rezept", "bolovanju": "Krankschreibung (Lok.)", "apoteci": "Apotheke (Lok.)",
    "apotekar": "Apotheker", "dao": "gegeben (m)", "lijek": "Medikament", "rekao": "gesagt (m)",
    "pijte": "trinken Sie (Befehl)", "tabletu": "Tablette (Akk.)", "puta": "Mal (Gen.)", "dnevno": "täglich",
    "čaja": "Tee (Gen.)", "s": "mit", "medom": "Honig (Instr.)", "kuće": "Haus (Gen.)", "mamu": "Mama (Akk.)",
    "jesi": "bist du", "li": "(Fragepartikel)", "doktora": "Arzt (Gen.)", "jesam": "ja, bin ich", "mama": "Mama",
    "strašno": "furchtbar", "čaj": "Tee", "opet": "wieder", "zdrav": "gesund (m/w)", "vratio": "zurückgekehrt (m)",
    # b1_selidba
    "selma": "Selma (Name)", "dobila": "bekommen (w)", "pa": "und dann / also", "mora": "er/sie muss",
    "preseliti": "umziehen", "tuzle": "Tuzla (Gen.)", "našla": "gefunden (w)", "stan": "Wohnung",
    "grbavici": "Grbavica (Stadtteil, Lok.)", "blizu": "in der Nähe von", "balkon": "Balkon",
    "pogledom": "Blick (Instr.)", "planine": "Berge", "subotu": "Samstag (Akk.)", "došli": "gekommen (Mehrz.)",
    "tarik": "Tarik (Name)", "dvojica": "zwei (Männer)", "prijatelja": "Freunde (Gen. Mehrz.)",
    "cijelo": "ganz (der ganze)", "jutro": "Morgen (Tageszeit)", "nosili": "getragen (Mehrz.)",
    "kutije": "Kisten (Akk.)", "ormar": "Schrank", "kombi": "Kleinbus / Lieferwagen", "imaš": "du hast",
    "ovoj": "dieser (Lok.)", "kutiji": "Kiste (Lok.)", "kamenje": "Steine (Sammelwort)", "smijao": "gelacht (m)",
    "knjige": "Bücher", "rekla": "gesagt (w)", "sata": "Stunden (Gen.)", "vožnje": "Fahrt (Gen.)",
    "stigli": "angekommen (Mehrz.)", "lift": "Aufzug", "zgradi": "Gebäude (Lok.)",
    "radio": "funktioniert / gearbeitet (m)", "petom": "fünften (Lok.)", "spratu": "Stockwerk (Lok.)",
    "morali": "gemusst (Mehrz.)", "nositi": "tragen", "stepenicama": "Treppe (Instr.)",
    "završili": "beendet (Mehrz.)", "umorni": "müde (Mehrz.)", "gladni": "hungrig (Mehrz.)", "neko": "jemand",
    "pokucao": "geklopft (m)", "komšinica": "Nachbarin", "četvrtog": "vierten (Gen.)", "sprata": "Stockwerk (Gen.)",
    "toplom": "warmen (Instr.)", "pitom": "Pita (Instr.)", "hajra": "Hajra (Name)", "ako": "wenn / falls",
    "samo": "nur", "pokucajte": "klopft (Befehl)", "sjeli": "hingesetzt (Mehrz.)", "pod": "Fußboden",
    "nisu": "sind nicht / haben nicht", "kupili": "gekauft (Mehrz.)", "jeli": "gegessen (Mehrz.)",
    "rukama": "Hände (Instr.)", "pogledala": "geschaut (w)", "kroz": "durch", "prozor": "Fenster",
    "nasmijala": "aufgelacht (w)", "pun": "voll", "kutija": "Schachtel / Kiste", "osjećala": "gefühlt (w)",
    "kao": "wie / als",
    # b1_rodjendan
    "haris": "Haris (Name)", "petak": "Freitag", "napuniti": "füllen (napuniti 30 godina: 30 werden)",
    "trideset": "dreißig", "njegova": "sein (m/w/s)", "žena": "Ehefrau", "lamija": "Lamija (Name)", "mjesec": "Monat",
    "tajno": "heimlich", "sprema": "er/sie bereitet vor", "iznenađenje": "Überraschung", "pozvala": "eingeladen (w)",
    "njegove": "seine (Akk. Mehrz.)", "roditelje": "Eltern (Akk.)", "prijatelje": "Freunde (Akk.)", "niko": "niemand",
    "reći": "sagen", "harisu": "Haris (Dat.)", "raditi": "arbeiten", "srijedu": "Mittwoch (Akk.)",
    "posebno": "besonders", "tvojih": "deinen (kod tvojih: bei deinen Eltern)", "tužan": "traurig (m/w)",
    "mislio": "gedacht (m)", "zaboravili": "vergessen (Mehrz.)", "rođendan": "Geburtstag", "gosti": "Gäste",
    "sakrili": "versteckt (Mehrz.)", "stanu": "Wohnung (Lok.)", "njegovih": "seiner (Gen. Mehrz.)",
    "roditelja": "Eltern (Gen.)", "svjetlo": "Licht", "ugašeno": "ausgeschaltet (s)",
    "šutjeli": "geschwiegen (Mehrz.)", "ušli": "hereingekommen (Mehrz.)", "upalio": "eingeschaltet (m)",
    "sretan": "glücklich (m/w)", "stajao": "gestanden (m)", "vratima": "Tür (Lok.)", "mogao": "gekonnt (m)",
    "vjerovati": "glauben", "donijela": "gebracht (w)", "tortu": "Torte (Akk.)", "svijeća": "Kerzen (Gen.)",
    "ih": "sie (Akk. Mehrz.)", "ugasio": "ausgemacht (m)", "vikali": "gerufen (Mehrz.)", "bravo": "bravo",
    "dala": "gegeben (w)", "koncert": "Konzert", "njegovog": "seines (Gen.)", "omiljenog": "Lieblings- (Gen.)",
    "pjevača": "Sänger (Gen.)", "najljepši": "der schönste", "mom": "meinem (Lok.)", "životu": "Leben (Lok.)",
    "ponoći": "Mitternacht (Gen.)", "pjevali": "gesungen (Mehrz.)", "plesali": "getanzt (Mehrz.)", "dugo": "lang",
    "pričao": "erzählt (m)", "svima": "allen", "znao": "gewusst (m)",
    # b1_utakmica
    "kenan": "Kenan (Name)", "jako": "sehr", "fudbal": "Fußball", "kupio": "gekauft (m)", "utakmicu": "Spiel (Akk.)",
    "reprezentacije": "Nationalmannschaft (Gen.)", "zenici": "Zenica (Lok.)", "bosna": "Bosnien",
    "hercegovina": "Herzegowina", "igra": "er/sie spielt", "protiv": "gegen", "islanda": "Island (Gen.)",
    "važna": "wichtig (der wichtige)", "utakmica": "Spiel (Match)", "evropsko": "Europa- / europäisch (s)",
    "prvenstvo": "Meisterschaft", "utakmice": "Spiel (Gen.)", "krenuli": "losgefahren (Mehrz.)", "podne": "Mittag",
    "autoputu": "Autobahn (Lok.)", "vidjeli": "gesehen (Mehrz.)", "auta": "Autos (Gen.)",
    "zastavama": "Fahnen (Instr.)", "ispred": "vor (räumlich)", "stadiona": "Stadion (Gen.)",
    "gužva": "Gedränge / Stau", "navijači": "Fans", "plave": "blaue (Mehrz.)", "majice": "T-Shirts",
    "zmajevi": "Drachen (Spitzname der Nationalmannschaft)", "poluvrijeme": "Halbzeit", "teško": "schwierig",
    "island": "Island", "bolji": "besser", "tridesetoj": "dreißigsten (Lok.)", "minuti": "Minute (Lok.)",
    "gol": "Tor (Treffer)", "polako": "langsam", "sine": "Sohn! (Anrede)", "devedeset": "neunzig",
    "drugom": "zweiten (Lok.)", "poluvremenu": "Halbzeit (Lok.)", "naši": "unsere (Mehrz.)",
    "igrali": "gespielt (Mehrz.)", "bolje": "besser (Adverb)", "šezdesetoj": "sechzigsten (Lok.)",
    "kraja": "Ende (Gen.)", "igrač": "Spieler", "cijeli": "ganz (der ganze)", "stadion": "Stadion",
    "skočio": "gesprungen (m)", "grlio": "umarmt (m)", "babu": "Papa (Akk.)", "ljude": "Leute (Akk.)",
    "koje": "die (Akk. Mehrz.)", "nikad": "nie", "vidio": "gesehen (m)", "tek": "erst", "glasa": "Stimme (Gen.)",
    "pjevanja": "Singen (Gen.)",
    # b1_zanat
    "lejla": "Lejla (Name)", "ljeta": "Sommer (Gen.)", "odmoru": "Urlaub (Lok.)", "najviše": "am meisten",
    "svidjela": "gefallen (w)", "mala": "klein", "ulica": "Straße", "baščaršiji": "Baščaršija (Lok.)",
    "kazandžiluk": "Kazandžiluk (Gasse der Kupferschmiede)", "čuje": "hört (se čuje: man hört)",
    "kucanje": "Klopfen / Hämmern", "čekića": "Hammer (Gen.)", "malim": "kleinen (Lok. Mehrz.)",
    "radnjama": "Läden (Lok.)", "majstori": "Handwerker (Mehrz.)", "prave": "sie machen", "stvari": "Sachen / Dinge",
    "bakra": "Kupfer (Gen.)", "ušla": "hineingegangen (w)", "radnju": "Laden (Akk.)", "stolom": "Tisch (Instr.)",
    "ukrašavao": "verziert (m)", "džezvu": "Kupferkännchen (Akk.)", "izvolite": "Bitte sehr (beim Überreichen)",
    "slobodno": "ruhig / frei", "pogledajte": "schauen Sie (Befehl)", "napravili": "gemacht (Mehrz.)",
    "ove": "diese (Akk. Mehrz.)", "zanat": "Handwerk", "naučio": "gelernt (m)", "oca": "Vater (Gen.)",
    "svog": "seines / eigenen (Gen.)", "radi": "er/sie arbeitet", "više": "mehr", "majstor": "Handwerker / Fachmann",
    "pokazao": "gezeigt (m)", "pravi": "er/sie macht", "džezva": "Kupferkännchen", "bakar": "Kupfer",
    "reže": "schneidet (se reže: wird geschnitten)", "kuca": "klopft / hämmert", "čekićem": "Hammer (Instr.)",
    "ukrašava": "verziert (se ukrašava: wird verziert)", "skoro": "fast / bald", "odete": "ihr geht / Sie gehen",
    "penziju": "Rente (Akk.)", "šutio": "geschwiegen (m)", "sin": "Sohn", "banci": "Bank (Lok.)",
    "težak": "schwer (m)", "zarađuje": "verdient (se zarađuje: man verdient)", "šest": "sechs",
    "fildžana": "Kaffeetassen (Gen.)", "njemačkoj": "Deutschland (Lok.)", "neka": "soll / möge",
    "srećom": "Glück (Instr.)", "nje": "ihr / sie (Gen.)", "nemojte": "tun Sie nicht (Befehl)", "držati": "halten",
    "polici": "Regal (Lok.)",
    # b1_kahva
    "teta": "Tante (Anrede für ältere Frauen)", "safija": "Safija (Name)", "živi": "er/sie lebt",
    "istom": "gleichen (Lok.)", "vrlo": "sehr (vor Eigenschaften)", "vesela": "fröhlich", "svake": "jeden (Gen.)",
    "nedjelje": "Sonntag (Gen.)", "pokuca": "klopft", "komšinice": "Nachbarin! (Anrede)", "hajde": "komm / los",
    "svoja": "eigener (mein, dein, sein)", "pravila": "Regeln", "kuha": "er/sie kocht", "vodu": "Wasser (Akk.)",
    "džezvi": "Kupferkännchen (Lok.)", "skine": "nimmt herunter", "šporeta": "Herd (Gen.)", "doda": "fügt hinzu",
    "promiješa": "rührt um", "vrati": "stellt zurück", "vatru": "Feuer (Akk.)", "kratko": "kurz",
    "prekipjeti": "überkochen", "prekipi": "kocht über", "kuhaj": "koch (Befehl)", "novu": "neue (Akk.)",
    "stolu": "Tisch (Lok.)", "fildžani": "Kaffeetassen", "šećer": "Zucker", "rahat": "rahat lokum: Lokum (Süßigkeit)",
    "lokum": "Lokum (Süßigkeit)", "čaša": "Glas", "vode": "Wasser (Gen.)", "uzmemo": "wir nehmen", "komad": "Stück",
    "lokuma": "Lokum (Gen.)", "pijemo": "wir trinken", "e": "na / also (Ausruf)", "prava": "echt",
    "bosanska": "bosnisch (w)", "počnu": "sie fangen an", "priče": "Geschichten", "oženio": "geheiratet (m)",
    "dobio": "bekommen (m)", "bebu": "Baby (Akk.)", "čiji": "wessen", "zašto": "warum", "komšija": "Nachbar",
    "mujo": "Mujo (Name)", "nikoga": "niemanden", "pozdravio": "gegrüßt (m)", "slušati": "zuhören / anhören",
    "jednom": "einmal", "moram": "ich muss", "popiti": "trinken / austrinken",
    "pije": "trinkt (se pije: wird getrunken)", "brzinu": "Schnelle (Akk.) (na brzinu: auf die Schnelle)",
    "dušo": "Schatz (Anrede)", "uz": "neben / zu / mit",
    "razgovara": "unterhält sich (se razgovara: man unterhält sich)", "tada": "damals", "sjedim": "ich sitze",
    "čak": "sogar", "kasnim": "Ich komme zu spät",
    # b1_mejl
    "predmet": "Betreff", "dolazim": "ich komme", "dragi": "lieber", "adnane": "Adnan! (Anrede)",
    "tetka": "Tante (Schwester von Vater oder Mutter)", "tetak": "Onkel (Mann der Tante)", "nas": "uns",
    "redu": "Ordnung (Lok.) (u redu: in Ordnung)", "ovih": "dieser (Gen. Mehrz.)", "mjeseci": "Monate (Gen.)",
    "radili": "gearbeitet (Mehrz.)", "lijepu": "schöne (Akk.)", "vijest": "Neuigkeit / Nachricht",
    "avion": "Flugzeug", "slijećem": "ich lande", "desetog": "am zehnten", "augusta": "August (Gen.)",
    "popodne": "am Nachmittag", "možeš": "du kannst", "sačekati": "abholen / erwarten",
    "aerodromu": "Flughafen (Lok.)", "problem": "Problem", "uzet": "nehmen (Zukunft)", "taksi": "Taxi",
    "ostat": "bleiben (Zukunft)", "prvu": "erste (Akk.)", "sedmicu": "Woche (Akk.)", "bih": "würde (ich)",
    "smeta": "es stört", "drugu": "zweite (Akk.)", "goražde": "Goražde (Stadt)", "donesem": "ich bringe (mit)",
    "njemačke": "Deutschland (Gen.)", "tetki": "Tante (Dat.)", "prošli": "vergangen / letzter (zeitlich)",
    "put": "Weg / Mal", "čokolada": "Schokolade", "lješnjacima": "Haselnüsse (Instr.)", "napiši": "schreib (Befehl)",
    "želite": "ihr möchtet / Sie möchten", "sigurno": "sicher", "primijetio": "bemerkt (m)", "pišem": "ich schreibe",
    "bosanskom": "Bosnisch (Lok.)", "pola": "die Hälfte", "mobitelu": "Handy (Lok.)", "griješim": "ich mache Fehler",
    "razgovarati": "sich unterhalten", "vidiš": "du siehst", "grešku": "Fehler (Akk.)", "nemoj": "tu nicht (Befehl)",
    "smijati": "lachen", "jedva": "kaum", "čekam": "ich warte", "vidimo": "wir sehen (uns)",
    "rođak": "Cousin, Verwandter (allgemein)", "emir": "Emir (Name)",
    # b1_zmaj
    "zmaj": "Drache", "nekoliko": "einige / ein paar", "uči": "er/sie lernt", "mostar": "Mostar", "svako": "jedes",
    "veče": "Abend", "ponavlja": "er/sie wiederholt", "nove": "neue (Mehrz.)", "riječi": "Wörter", "voda": "Wasser",
    "stigao": "angekommen (m)", "odmah": "sofort", "htio": "wollte (m)", "pokazati": "zeigen",
    "zna": "er/sie weiß / kann", "ponosno": "stolz (Adverb)", "sad": "jetzt", "večere": "Abendessen (Gen.)",
    "hoćeš": "du willst", "sarme": "Sarma (Gen.)", "sit": "satt (m)", "stavila": "gelegt (w)", "tanjir": "Teller",
    "čula": "gehört (w)", "znači": "es bedeutet", "ukusno": "lecker", "sutradan": "am nächsten Tag",
    "dedi": "Opa (Dat.)", "roštilja": "Grill (Gen.)", "pustio": "gelassen (m)", "vatre": "Feuer (Gen.)",
    "usta": "Mund", "ćevapi": "Ćevapi", "sekundi": "Sekunde (Lok.)", "zagorjeli": "angebrannt (Mehrz.)",
    "stani": "halt (Befehl)", "zmaju": "Drache! (Anrede)", "peku": "grillen / backen (sie)",
    "zmajevom": "Drachen- (Instr.)", "vatrom": "Feuer (Instr.)", "napisao": "geschrieben (m)",
    "poruku": "Nachricht (Akk.)", "mami": "Mama (Dat.)", "telefon": "Telefon", "mostaru": "Mostar (Lok.)",
    "pomislio": "gedacht (m)", "strpljiva": "geduldig", "njena": "ihr (von ihr) (m/w/s)",
    "sarma": "Sarma (Krautwickel)", "najbolja": "die beste", "svijetu": "Welt (Lok.)", "zato": "deshalb",
    "učiti": "lernen", "dalje": "weiter",
}
WOERTERBUCH.update({k: v for k, v in WOERTERBUCH_B1_2.items() if k not in WOERTERBUCH})

GESCHICHTEN += [
    {
        "id": "b1_doktor", "titel": "Kod doktora", "stufe": "B1", "passt_zu": "in_der_praxis",
        "text": ("Amar se već tri dana ne osjeća dobro. Boli ga grlo, ima temperaturu i stalno je umoran. U ponedjeljak ujutro nazvao je dom zdravlja i zakazao termin kod doktorice za deset sati.\n\n"
                 "U čekaonici je bilo mnogo ljudi. Pored Amara je sjedio jedan stariji čovjek koji je stalno kašljao. „I vas boli grlo?“ pitao je čovjek. „Da, već tri dana“, odgovorio je Amar. „Sada su svi bolesni. To je od ovog vremena.“\n\n"
                 "Kad je došao na red, doktorica ga je pitala: „Šta vas boli i od kada?“ Amar joj je sve objasnio. Ona ga je pregledala i izmjerila mu temperaturu. „Imate upalu grla. Nije ništa ozbiljno, ali morate se odmarati. Dat ću vam recept, a pet dana ste na bolovanju.“\n\n"
                 "U apoteci mu je apotekar dao lijek i rekao: „Pijte jednu tabletu tri puta dnevno, poslije jela. I pijte mnogo čaja s medom.“\n\n"
                 "Kod kuće je Amar nazvao mamu. „Jesi li bio kod doktora?“ pitala je ona. „Jesam, mama. Nije ništa strašno.“ „Onda dobro. Čaj s medom i u krevet!“ Poslije pet dana Amar je opet bio zdrav i vratio se na posao."),
        "uebersetzung": ("Amar fühlt sich schon seit drei Tagen nicht gut. Sein Hals tut weh, er hat Fieber und ist ständig müde. Am Montagmorgen hat er im Gesundheitszentrum angerufen und für zehn Uhr einen Termin bei der Ärztin vereinbart.\n\n"
                         "Im Wartezimmer waren viele Leute. Neben Amar saß ein älterer Mann, der ständig hustete. „Tut Ihnen auch der Hals weh?“, fragte der Mann. „Ja, schon seit drei Tagen“, antwortete Amar. „Jetzt sind alle krank. Das kommt von diesem Wetter.“\n\n"
                         "Als er an der Reihe war, fragte ihn die Ärztin: „Was tut Ihnen weh, und seit wann?“ Amar hat ihr alles erklärt. Sie hat ihn untersucht und bei ihm Fieber gemessen. „Sie haben eine Halsentzündung. Es ist nichts Ernstes, aber Sie müssen sich ausruhen. Ich gebe Ihnen ein Rezept, und Sie sind fünf Tage krankgeschrieben.“\n\n"
                         "In der Apotheke gab ihm der Apotheker das Medikament und sagte: „Nehmen Sie dreimal täglich eine Tablette, nach dem Essen. Und trinken Sie viel Tee mit Honig.“\n\n"
                         "Zu Hause rief Amar seine Mama an. „Warst du beim Arzt?“, fragte sie. „Ja, Mama. Es ist nichts Schlimmes.“ „Dann ist es gut. Tee mit Honig und ab ins Bett!“ Nach fünf Tagen war Amar wieder gesund und ging wieder zur Arbeit."),
        "vokabeln": {"vremena": "Wetter / Zeit (Gen.)", "jela": "Essen (Gen.)", "koji": "der (Relativ) / welcher"},
        "fragen": [
            {"frage": "Was hat Amar?", "optionen": ["eine Halsentzündung", "eine Ohrenentzündung", "Bauchschmerzen"], "richtig": "eine Halsentzündung"},
            {"frage": "Wie oft soll er die Tablette nehmen?", "optionen": ["dreimal täglich", "zweimal täglich", "nur am Abend"], "richtig": "dreimal täglich"},
            {"frage": "Wie lange ist Amar krankgeschrieben?", "optionen": ["fünf Tage", "drei Tage", "zwei Wochen"], "richtig": "fünf Tage"},
        ],
    },
    {
        "id": "b1_selidba", "titel": "Selidba", "stufe": "B1", "passt_zu": "erledigen_umziehen",
        "text": ("Selma je dobila novi posao u Sarajevu, pa se mora preseliti iz Tuzle. Našla je mali stan na Grbavici, blizu posla. Stan ima dvije sobe, kuhinju i balkon s pogledom na planine.\n\n"
                 "U subotu ujutro došli su njen brat Tarik i dvojica prijatelja. Cijelo jutro su nosili kutije, stolice, krevet i ormar u kombi. „Šta imaš u ovoj kutiji, kamenje?“ smijao se Tarik. „Ne, knjige“, rekla je Selma.\n\n"
                 "Poslije dva sata vožnje stigli su u Sarajevo. Ali lift u zgradi nije radio, a stan je bio na petom spratu. Morali su sve nositi stepenicama. Kad su završili, svi su bili umorni i gladni.\n\n"
                 "Onda je neko pokucao na vrata. Bila je to komšinica s četvrtog sprata, s toplom pitom. „Dobro došli! Ja sam Hajra. Ako vam nešto treba, samo pokucajte.“\n\n"
                 "Sjeli su na pod, jer sto još nisu kupili, i jeli pitu rukama. Selma je pogledala kroz prozor i nasmijala se. Stan je još bio pun kutija, ali ona se već osjećala kao kod kuće."),
        "uebersetzung": ("Selma hat eine neue Arbeit in Sarajevo bekommen, also muss sie aus Tuzla umziehen. Sie hat eine kleine Wohnung in Grbavica gefunden, in der Nähe der Arbeit. Die Wohnung hat zwei Zimmer, eine Küche und einen Balkon mit Blick auf die Berge.\n\n"
                         "Am Samstagmorgen kamen ihr Bruder Tarik und zwei Freunde. Den ganzen Morgen trugen sie Kisten, Stühle, ein Bett und einen Schrank in den Kleinbus. „Was hast du in dieser Kiste, Steine?“, lachte Tarik. „Nein, Bücher“, sagte Selma.\n\n"
                         "Nach zwei Stunden Fahrt kamen sie in Sarajevo an. Aber der Aufzug im Gebäude funktionierte nicht, und die Wohnung lag im fünften Stock. Sie mussten alles über die Treppe tragen. Als sie fertig waren, waren alle müde und hungrig.\n\n"
                         "Dann klopfte jemand an die Tür. Es war die Nachbarin aus dem vierten Stock, mit einer warmen Pita. „Willkommen! Ich bin Hajra. Wenn ihr etwas braucht, klopft einfach.“\n\n"
                         "Sie setzten sich auf den Boden, weil sie noch keinen Tisch gekauft hatten, und aßen die Pita mit den Händen. Selma schaute aus dem Fenster und lachte. Die Wohnung war noch voller Kisten, aber sie fühlte sich schon wie zu Hause."),
        "fragen": [
            {"frage": "Warum zieht Selma um?", "optionen": ["wegen einer neuen Arbeit", "wegen der Miete", "wegen einer größeren Wohnung"], "richtig": "wegen einer neuen Arbeit"},
            {"frage": "Warum mussten sie alles über die Treppe tragen?", "optionen": ["der Aufzug funktionierte nicht", "die Kisten waren zu groß", "die Treppe war schneller"], "richtig": "der Aufzug funktionierte nicht"},
            {"frage": "Was brachte die Nachbarin mit?", "optionen": ["eine warme Pita", "eine warme Suppe", "einen Blumenstrauß"], "richtig": "eine warme Pita"},
        ],
    },
    {
        "id": "b1_rodjendan", "titel": "Rođendansko iznenađenje", "stufe": "B1", "passt_zu": "feiern",
        "text": ("Haris će u petak napuniti trideset godina. Njegova žena Lamija već mjesec dana tajno sprema iznenađenje. Pozvala je njegove roditelje, brata i najbolje prijatelje, ali niko ne smije ništa reći Harisu.\n\n"
                 "„Šta ćemo raditi u petak?“ pitao je Haris u srijedu. „Ništa posebno“, rekla je Lamija. „Idemo kod tvojih na večeru.“ Haris je bio malo tužan. Mislio je da su svi zaboravili njegov rođendan.\n\n"
                 "U petak navečer gosti su se sakrili u stanu njegovih roditelja. Svjetlo je bilo ugašeno i svi su šutjeli. Kad su Haris i Lamija ušli, neko je upalio svjetlo. „Iznenađenje! Sretan rođendan!“ Haris je stajao na vratima i nije mogao vjerovati.\n\n"
                 "Njegova mama je donijela veliku tortu s trideset svijeća. Haris ih je ugasio odjednom, a svi su vikali: „Bravo!“ Onda mu je Lamija dala poklon: dvije karte za koncert njegovog omiljenog pjevača.\n\n"
                 "„Ovo je najljepši rođendan u mom životu“, rekao je Haris. Do ponoći su jeli, pjevali i plesali. A Haris je još dugo pričao svima kako ništa nije znao."),
        "uebersetzung": ("Haris wird am Freitag dreißig. Seine Frau Lamija bereitet schon seit einem Monat heimlich eine Überraschung vor. Sie hat seine Eltern, seinen Bruder und seine besten Freunde eingeladen, aber niemand darf Haris etwas sagen.\n\n"
                         "„Was machen wir am Freitag?“, fragte Haris am Mittwoch. „Nichts Besonderes“, sagte Lamija. „Wir gehen zum Abendessen zu deinen Eltern.“ Haris war ein bisschen traurig. Er dachte, alle hätten seinen Geburtstag vergessen.\n\n"
                         "Am Freitagabend versteckten sich die Gäste in der Wohnung seiner Eltern. Das Licht war aus, und alle schwiegen. Als Haris und Lamija hereinkamen, machte jemand das Licht an. „Überraschung! Alles Gute zum Geburtstag!“ Haris stand in der Tür und konnte es nicht glauben.\n\n"
                         "Seine Mama brachte eine große Torte mit dreißig Kerzen. Haris blies sie auf einmal aus, und alle riefen: „Bravo!“ Dann gab ihm Lamija ein Geschenk: zwei Karten für das Konzert seines Lieblingssängers.\n\n"
                         "„Das ist der schönste Geburtstag meines Lebens“, sagte Haris. Bis Mitternacht aßen, sangen und tanzten sie. Und Haris erzählte noch lange allen, dass er nichts gewusst hatte."),
        "vokabeln": {"smije": "darf (ne smije: darf nicht)", "odjednom": "auf einmal", "karte": "Karten / Tickets", "najbolje": "besten (Akk. Mehrz.)"},
        "fragen": [
            {"frage": "Wie alt wird Haris?", "optionen": ["dreißig", "zwanzig", "vierzig"], "richtig": "dreißig"},
            {"frage": "Wohin wollten Haris und Lamija angeblich gehen?", "optionen": ["zum Abendessen bei seinen Eltern", "zum Abendessen ins Restaurant", "zu einem Konzert"], "richtig": "zum Abendessen bei seinen Eltern"},
            {"frage": "Was schenkte Lamija ihm?", "optionen": ["zwei Konzertkarten", "eine Torte", "zwei Kinokarten"], "richtig": "zwei Konzertkarten"},
        ],
    },
    {
        "id": "b1_utakmica", "titel": "Utakmica", "stufe": "B1", "passt_zu": "sport",
        "text": ("Kenan ima dvanaest godina i jako voli fudbal. Za njegov rođendan babo je kupio dvije karte za utakmicu reprezentacije u Zenici. Bosna i Hercegovina igra protiv Islanda, a to je važna utakmica za Evropsko prvenstvo.\n\n"
                 "Na dan utakmice krenuli su iz Sarajeva već u podne. Na autoputu su vidjeli mnogo auta sa zastavama. Ispred stadiona je bila velika gužva. Navijači su nosili plave majice i pjevali: „Zmajevi, Zmajevi!“\n\n"
                 "Utakmica je počela u osam sati. Prvo poluvrijeme je bilo teško. Island je bio bolji i u tridesetoj minuti je dao gol. Kenan je bio tužan, ali babo mu je rekao: „Polako, sine. Utakmica traje devedeset minuta.“\n\n"
                 "U drugom poluvremenu naši su igrali mnogo bolje. U šezdesetoj minuti i Bosna je dala gol, a pet minuta prije kraja naš igrač je dao još jedan. Cijeli stadion je skočio. Kenan je grlio babu i ljude koje nikad prije nije vidio.\n\n"
                 "Kući su stigli tek poslije ponoći, umorni i bez glasa od pjevanja. „Babo, kad idemo opet?“ pitao je Kenan."),
        "uebersetzung": ("Kenan ist zwölf Jahre alt und liebt Fußball sehr. Zu seinem Geburtstag hat Papa zwei Karten für ein Spiel der Nationalmannschaft in Zenica gekauft. Bosnien und Herzegowina spielt gegen Island, und das ist ein wichtiges Spiel für die Europameisterschaft.\n\n"
                         "Am Tag des Spiels fuhren sie schon mittags in Sarajevo los. Auf der Autobahn sahen sie viele Autos mit Fahnen. Vor dem Stadion war ein großes Gedränge. Die Fans trugen blaue T-Shirts und sangen: „Drachen, Drachen!“\n\n"
                         "Das Spiel begann um acht Uhr. Die erste Halbzeit war schwer. Island war besser und schoss in der dreißigsten Minute ein Tor. Kenan war traurig, aber Papa sagte zu ihm: „Ruhig, mein Sohn. Ein Spiel dauert neunzig Minuten.“\n\n"
                         "In der zweiten Halbzeit spielten unsere viel besser. In der sechzigsten Minute schoss auch Bosnien ein Tor, und fünf Minuten vor dem Ende schoss unser Spieler noch eins. Das ganze Stadion sprang auf. Kenan umarmte Papa und Leute, die er noch nie gesehen hatte.\n\n"
                         "Nach Hause kamen sie erst nach Mitternacht, müde und ohne Stimme vom Singen. „Papa, wann gehen wir wieder?“, fragte Kenan."),
        "vokabeln": {"prvo": "erste (s) / zuerst", "karte": "Karten / Tickets"},
        "fragen": [
            {"frage": "Gegen wen spielt Bosnien?", "optionen": ["gegen Island", "gegen Italien", "gegen Deutschland"], "richtig": "gegen Island"},
            {"frage": "Wer schoss das erste Tor?", "optionen": ["die isländische Mannschaft", "die bosnische Mannschaft", "keine der beiden Mannschaften"], "richtig": "die isländische Mannschaft"},
            {"frage": "Wann kamen sie nach Hause?", "optionen": ["nach Mitternacht", "um zehn Uhr", "am nächsten Mittag"], "richtig": "nach Mitternacht"},
        ],
    },
    {
        "id": "b1_zanat", "titel": "Stari zanat na Baščaršiji", "stufe": "B1", "passt_zu": "arbeitsplatz",
        "text": ("Lejla je ovog ljeta na odmoru u Sarajevu. Najviše joj se svidjela jedna mala ulica na Baščaršiji. Zove se Kazandžiluk. Tu se cijeli dan čuje kucanje čekića, jer u malim radnjama majstori prave stvari od bakra.\n\n"
                 "Lejla je ušla u jednu radnju. Za stolom je sjedio stariji čovjek i polako ukrašavao jednu džezvu. „Izvolite, slobodno pogledajte“, rekao je. „Jeste li vi napravili sve ove stvari?“ pitala je Lejla. „Jesam. Ovaj zanat sam naučio od oca, a on od svog oca. Naša porodica radi u ovoj radnji više od sto godina.“\n\n"
                 "Majstor joj je pokazao kako se pravi džezva. Prvo se bakar reže, onda se dugo kuca čekićem, a na kraju se ukrašava. „Za jednu džezvu treba mi skoro cijeli dan“, objasnio je.\n\n"
                 "„A ko će raditi kad vi odete u penziju?“ pitala je Lejla. Majstor je malo šutio. „Moj sin radi u banci. Mladi danas ne žele ovaj posao. Težak je, a ne zarađuje se mnogo.“\n\n"
                 "Lejla je kupila džezvu i šest fildžana za nanu u Njemačkoj. „Neka je sa srećom!“ rekao je majstor. „I pijte kahvu iz nje. Nemojte je samo držati na polici.“"),
        "uebersetzung": ("Lejla ist diesen Sommer im Urlaub in Sarajevo. Am besten gefiel ihr eine kleine Gasse auf der Baščaršija. Sie heißt Kazandžiluk. Hier hört man den ganzen Tag Hämmern, denn in den kleinen Läden machen Handwerker Dinge aus Kupfer.\n\n"
                         "Lejla ging in einen Laden. Am Tisch saß ein älterer Mann und verzierte langsam ein Kupferkännchen. „Bitte sehr, schauen Sie sich ruhig um“, sagte er. „Haben Sie all diese Sachen gemacht?“, fragte Lejla. „Ja. Dieses Handwerk habe ich von meinem Vater gelernt und er von seinem Vater. Unsere Familie arbeitet seit über hundert Jahren in diesem Laden.“\n\n"
                         "Der Meister zeigte ihr, wie man ein Kupferkännchen macht. Zuerst wird das Kupfer geschnitten, dann lange mit dem Hammer bearbeitet, und am Ende wird es verziert. „Für ein Kännchen brauche ich fast einen ganzen Tag“, erklärte er.\n\n"
                         "„Und wer wird hier arbeiten, wenn Sie in Rente gehen?“, fragte Lejla. Der Meister schwieg eine Weile. „Mein Sohn arbeitet bei einer Bank. Die jungen Leute wollen diese Arbeit heute nicht. Sie ist schwer, und man verdient nicht viel.“\n\n"
                         "Lejla kaufte ein Kupferkännchen und sechs Kaffeetassen für ihre Oma in Deutschland. „Viel Freude damit!“, sagte der Meister. „Und trinken Sie Kaffee daraus. Stellen Sie es nicht nur ins Regal.“"),
        "vokabeln": {"sto": "hundert", "jeste": "ihr seid / Sie sind (Jeste li …?: Haben Sie …?)", "mladi": "die Jungen / junge Leute"},
        "fragen": [
            {"frage": "Woraus machen die Handwerker im Kazandžiluk ihre Sachen?", "optionen": ["aus Kupfer", "aus Holz", "aus Glas"], "richtig": "aus Kupfer"},
            {"frage": "Wie lange braucht der Meister für ein Kupferkännchen?", "optionen": ["fast einen ganzen Tag", "nur eine halbe Stunde", "fast eine ganze Woche"], "richtig": "fast einen ganzen Tag"},
            {"frage": "Wo arbeitet der Sohn des Meisters?", "optionen": ["bei einer Bank", "im Laden des Vaters", "in Deutschland"], "richtig": "bei einer Bank"},
        ],
    },
    {
        "id": "b1_kahva", "titel": "Kahva kod komšinice", "stufe": "B1", "passt_zu": "nachbarn_miteinander",
        "text": ("Moja komšinica, teta Safija, živi na istom spratu kao ja. Ima osamdeset godina, ali je još uvijek vrlo vesela. Svake nedjelje u deset sati pokuca mi na vrata: „Komšinice, hajde na kahvu!“\n\n"
                 "Kod nje kahva ima svoja pravila. Prvo kuha vodu u džezvi. Onda skine džezvu sa šporeta, doda kahvu i promiješa. Džezvu vrati na vatru samo na kratko. „Kahva ne smije prekipjeti“, kaže ona. „Ako prekipi, kuhaj novu.“\n\n"
                 "Na stolu su fildžani, šećer, rahat lokum i čaša vode. Prvo uzmemo komad rahat lokuma, a onda polako pijemo kahvu. „E, ovo je prava bosanska kahva“, kaže teta Safija.\n\n"
                 "Onda počnu priče: ko se oženio, ko je dobio bebu, čiji sin radi u Njemačkoj i zašto komšija Mujo opet nikoga nije pozdravio. Ja ne razumijem sve, ali volim slušati.\n\n"
                 "Jednom sam rekla da moram brzo popiti kahvu jer idem u grad. Teta Safija me pogledala kao da sam rekla nešto strašno. „Kahva se ne pije na brzinu, dušo. Uz kahvu se razgovara. Za kahvu uvijek ima vremena.“ Od tada sjedim do kraja, čak i kad kasnim."),
        "uebersetzung": ("Meine Nachbarin, Tante Safija, wohnt auf demselben Stockwerk wie ich. Sie ist achtzig Jahre alt, aber immer noch sehr fröhlich. Jeden Sonntag um zehn Uhr klopft sie an meine Tür: „Nachbarin, komm auf einen Kaffee!“\n\n"
                         "Bei ihr hat der Kaffee seine eigenen Regeln. Zuerst kocht sie Wasser im Kupferkännchen. Dann nimmt sie das Kännchen vom Herd, gibt den Kaffee dazu und rührt um. Das Kännchen stellt sie nur kurz zurück aufs Feuer. „Der Kaffee darf nicht überkochen“, sagt sie. „Wenn er überkocht, koch einen neuen.“\n\n"
                         "Auf dem Tisch stehen Kaffeetassen, Zucker, Lokum und ein Glas Wasser. Zuerst nehmen wir ein Stück Lokum, und dann trinken wir langsam den Kaffee. „Ja, das ist echter bosnischer Kaffee“, sagt Tante Safija.\n\n"
                         "Dann fangen die Geschichten an: wer geheiratet hat, wer ein Baby bekommen hat, wessen Sohn in Deutschland arbeitet und warum Nachbar Mujo schon wieder niemanden gegrüßt hat. Ich verstehe nicht alles, aber ich höre gern zu.\n\n"
                         "Einmal habe ich gesagt, dass ich den Kaffee schnell austrinken muss, weil ich in die Stadt gehe. Tante Safija sah mich an, als hätte ich etwas Schreckliches gesagt. „Kaffee trinkt man nicht auf die Schnelle, Schatz. Beim Kaffee unterhält man sich. Für Kaffee ist immer Zeit.“ Seitdem bleibe ich bis zum Schluss sitzen, sogar wenn ich spät dran bin."),
        "vokabeln": {"smije": "darf (ne smije: darf nicht)", "vremena": "Wetter / Zeit (Gen.)"},
        "fragen": [
            {"frage": "Wann lädt Tante Safija zum Kaffee ein?", "optionen": ["jeden Sonntag um zehn", "jeden Abend", "jeden Montag um acht"], "richtig": "jeden Sonntag um zehn"},
            {"frage": "Was darf beim Kaffeekochen nicht passieren?", "optionen": ["der Kaffee darf nicht überkochen", "das Wasser darf nicht kochen", "es darf kein Zucker fehlen"], "richtig": "der Kaffee darf nicht überkochen"},
            {"frage": "Was sagt Tante Safija über den Kaffee?", "optionen": ["Für Kaffee ist immer Zeit.", "Kaffee trinkt man schnell.", "Kaffee macht müde."], "richtig": "Für Kaffee ist immer Zeit."},
        ],
    },
    {
        "id": "b1_mejl", "titel": "Mejl rođaku", "stufe": "B1", "passt_zu": "urlaub",
        "text": ("Predmet: Dolazim u augustu!\n\n"
                 "Dragi Adnane, kako si? Kako su tetka i tetak? Nadam se da ste svi dobro. Kod nas je sve u redu, samo smo ovih mjeseci mnogo radili.\n\n"
                 "Imam lijepu vijest: u augustu dolazim u Sarajevo! Već sam kupio kartu za avion. Slijećem desetog augusta u četiri sata popodne. Možeš li me sačekati na aerodromu? Ako ne možeš, nije problem, uzet ću taksi.\n\n"
                 "Ostat ću dvije sedmice. Prvu sedmicu bih bio kod vas, ako vam to ne smeta. Drugu sedmicu idem kod nane u Goražde. Ona me već svaki dan pita kad dolazim.\n\n"
                 "Šta da vam donesem iz Njemačke? Tetki se prošli put jako svidjela ona čokolada s lješnjacima. Napiši mi šta želite.\n\n"
                 "Sigurno si primijetio da ti pišem na bosanskom. Već pola godine učim svaki dan na mobitelu. Još uvijek griješim, ali nadam se da ćemo ovog ljeta razgovarati samo na bosanskom. Ako vidiš grešku, nemoj se smijati!\n\n"
                 "Jedva čekam da se vidimo. Pozdravi sve!\n\n"
                 "Tvoj rođak Emir"),
        "uebersetzung": ("Betreff: Ich komme im August!\n\n"
                         "Lieber Adnan, wie geht es dir? Wie geht es Tante und Onkel? Ich hoffe, euch geht es allen gut. Bei uns ist alles in Ordnung, wir haben in den letzten Monaten nur viel gearbeitet.\n\n"
                         "Ich habe eine schöne Neuigkeit: Im August komme ich nach Sarajevo! Ich habe das Flugticket schon gekauft. Ich lande am zehnten August um vier Uhr nachmittags. Kannst du mich am Flughafen abholen? Wenn du nicht kannst, ist das kein Problem, dann nehme ich ein Taxi.\n\n"
                         "Ich bleibe zwei Wochen. Die erste Woche wäre ich bei euch, wenn euch das nicht stört. Die zweite Woche fahre ich zur Oma nach Goražde. Sie fragt mich schon jeden Tag, wann ich komme.\n\n"
                         "Was soll ich euch aus Deutschland mitbringen? Der Tante hat letztes Mal die Schokolade mit Haselnüssen sehr gut geschmeckt. Schreib mir, was ihr möchtet.\n\n"
                         "Du hast sicher bemerkt, dass ich dir auf Bosnisch schreibe. Ich lerne schon seit einem halben Jahr jeden Tag auf dem Handy. Ich mache immer noch Fehler, aber ich hoffe, dass wir diesen Sommer nur Bosnisch sprechen. Wenn du einen Fehler siehst, lach nicht!\n\n"
                         "Ich kann es kaum erwarten, dass wir uns sehen. Grüß alle!\n\n"
                         "Dein Cousin Emir"),
        "fragen": [
            {"frage": "Wann landet Emir in Sarajevo?", "optionen": ["am zehnten August", "am vierten August", "Ende Juli"], "richtig": "am zehnten August"},
            {"frage": "Wo verbringt er die zweite Woche?", "optionen": ["bei der Oma in Goražde", "bei Adnan in Sarajevo", "in einem Hotel in Mostar"], "richtig": "bei der Oma in Goražde"},
            {"frage": "Worum bittet Emir Adnan?", "optionen": ["ihn am Flughafen abzuholen", "ein Hotel zu buchen", "Schokolade zu kaufen"], "richtig": "ihn am Flughafen abzuholen"},
        ],
    },
    {
        "id": "b1_zmaj", "titel": "Zmaj uči bosanski", "stufe": "B1", "passt_zu": "lernen_studieren",
        "text": ("Zmaj je mali zmaj koji živi u Njemačkoj. Već nekoliko mjeseci uči bosanski, jer ovog ljeta ide kod nane u Mostar. Svako veče ponavlja nove riječi: kuća, voda, hljeb, kahva.\n\n"
                 "Kad je stigao kod nane, odmah je htio pokazati šta zna. „Dobro jutro, nano!“ rekao je ponosno. Nana se nasmijala. „Dobro jutro? Sine, sad je osam sati navečer. Kaže se dobro veče.“\n\n"
                 "Poslije večere nana ga je pitala: „Hoćeš li još sarme?“ Zmaj je bio sit, pa je rekao: „Hvala.“ Nana mu je odmah stavila još tri sarme na tanjir. „Ali nano, rekao sam hvala!“ „Čula sam“, rekla je nana. „Hvala znači da ti je ukusno.“\n\n"
                 "Sutradan je Zmaj htio pomoći dedi oko roštilja. Pustio je malo vatre iz usta, i ćevapi su u sekundi zagorjeli. „Stani, zmaju!“ rekao je dedo. „Ćevapi se peku polako, a ne zmajevom vatrom.“\n\n"
                 "Navečer je Zmaj napisao poruku mami: „Ja sam u Mostar i jedem mnogo sarme.“ Nana je pogledala telefon. „Ne u Mostar, nego u Mostaru.“ Zmaj je pomislio da je bosanski težak. Ali nana je strpljiva, a njena sarma je najbolja na svijetu. Zato će učiti dalje."),
        "uebersetzung": ("Zmaj ist ein kleiner Drache, der in Deutschland lebt. Seit einigen Monaten lernt er schon Bosnisch, weil er diesen Sommer zu seiner Oma nach Mostar fährt. Jeden Abend wiederholt er neue Wörter: kuća, voda, hljeb, kahva.\n\n"
                         "Als er bei der Oma ankam, wollte er sofort zeigen, was er kann. „Guten Morgen, Oma!“, sagte er stolz. Die Oma lachte. „Guten Morgen? Mein Junge, jetzt ist es acht Uhr abends. Man sagt Guten Abend.“\n\n"
                         "Nach dem Abendessen fragte ihn die Oma: „Willst du noch Sarma?“ Zmaj war satt, also sagte er: „Danke.“ Die Oma legte ihm sofort noch drei Sarma auf den Teller. „Aber Oma, ich habe danke gesagt!“ „Ich habe es gehört“, sagte die Oma. „Danke heißt, dass es dir schmeckt.“\n\n"
                         "Am nächsten Tag wollte Zmaj dem Opa am Grill helfen. Er ließ ein bisschen Feuer aus dem Mund, und die Ćevapi waren in einer Sekunde angebrannt. „Halt, Drache!“, sagte der Opa. „Ćevapi grillt man langsam, nicht mit Drachenfeuer.“\n\n"
                         "Abends schrieb Zmaj seiner Mama eine Nachricht: „Ja sam u Mostar i jedem mnogo sarme.“ (Ich bin in Mostar und esse viel Sarma.) Die Oma schaute auf das Handy. „Nicht u Mostar, sondern u Mostaru.“ Zmaj dachte, dass Bosnisch schwer ist. Aber die Oma ist geduldig, und ihre Sarma ist die beste der Welt. Deshalb lernt er weiter."),
        "vokabeln": {"nego": "sondern / als", "koji": "der (Relativ) / welcher"},
        "fragen": [
            {"frage": "Welchen Fehler macht Zmaj, als er ankommt?", "optionen": ["er sagt am Abend „Dobro jutro“", "er vergisst den Namen der Oma", "er kommt zu spät"], "richtig": "er sagt am Abend „Dobro jutro“"},
            {"frage": "Was bedeutet „Hvala“ für die Oma?", "optionen": ["dass es ihm schmeckt", "dass er satt ist", "dass er schlafen will"], "richtig": "dass es ihm schmeckt"},
            {"frage": "Was passiert mit den Ćevapi?", "optionen": ["sie brennen an", "sie werden kalt", "der Hund frisst sie"], "richtig": "sie brennen an"},
        ],
    },
]
