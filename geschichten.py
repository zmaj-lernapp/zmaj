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
    "kući": "nach Hause / zu Hause", "zajedno": "zusammen", "kraju": "Ende (Lok.)",
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
    "kuća": "Haus", "kuću": "Haus (Akk.)", "kući": "Haus (Lok.) / nach Hause", "vrata": "Tür", "prozora": "Fenster (Gen. Mehrz.)",
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
