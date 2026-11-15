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
      "passt_zu":     Level-id aus vokabeln.py, dessen Wörter man kennen sollte;
                      höchstens B1, ein B2-Level haben die Leser meist noch nicht
                      offen (Prüfbericht 1.4, B12, 14.11.2026)
      "text":         der bosnische Text,
      "uebersetzung": die deutsche Übersetzung,
      "vokabeln":     zusätzliche Wörter nur für diese Geschichte (optional),
      "fragen":       [{"frage": "...", "optionen": [...], "richtig": "..."}]
  }

Tipp zum Schreiben neuer Geschichten: kurze Sätze, Wörter aus den Levels davor,
und jedes neue Wort ins WOERTERBUCH eintragen. start.py meldet beim Start,
welche Wörter noch fehlen.

Höfliches Vi, Vas, Vam und Vaš (in jeder Form, auch Vašu, Vašeg ...): groß,
sobald EINE Person höflich angeredet wird, überall - in den Gesprächen der
Erzählung genauso wie in Geschriebenem, in Wörtern, Sätzen, Lückensätzen,
Kacheln und in der Grammatik. Ajdin am 15.11.2026: "mach doch alles groß".
Das ersetzt F23 (Prüfbericht 1.4, S7, 14.11.2026: groß nur in Geschriebenem,
im Gespräch klein). Also "Prvo ću Vam pokazati Vašu kancelariju" (die Chefin zu
Haris), "ako Vam odgovara" und "Hvala Vam" (Telefonat), "Hvala Vam na pomoći"
(Amina am Schalter), "kod Vas" (Hasan zu Merima), "I Vas boli grlo?", "Šta Vas
boli", "Dat ću Vam recept" (Wartezimmer, Ärztin), "Jeste li Vi napravili",
"kad Vi odete" (Lejla zum Meister), "molim Vas, javite se" (Nachricht).
Klein bleibt, wo mehrere gemeint sind (ihr, euch): "Ako vam nešto zatreba" zu
Lejla und Emir in b1_voz, "Prsluk će vas držati" zur ganzen Gruppe in
b1_rafting, Emirs Mail an Cousin und Familie in b1_mejl ("kod vas", "ako vam",
"Šta da vam donesem"). Der Ton-Schlüssel ist kleingeschrieben
(ton_bauen.schluessel): groß oder klein kostet keinen neuen Ton, und die
Wortzeiten von opcina (g10) gehören mit "Hvala Vam" wieder genau zum Text.

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
    # ti und vam (Prüfbericht 1.4, B10, 14.11.2026): In den B1-Texten heißt ti
    # jedes Mal "dir" ("Ako ti bilo šta treba"), vam an vier Stellen "euch".
    "on": "er", "ona": "sie", "oni": "sie (Mehrzahl)", "ja": "ich", "ti": "du / dir", "vi": "ihr / Sie", "tebe": "dich / dir", "sebi": "sich",
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
    "doći": "kommen", "nadam": "ich hoffe", "pozdravi": "grüße", "recite": "sagen Sie",
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
    "taksu": "Gebühr (Akk.)", "pomoći": "Hilfe (Lok.) / helfen", "hvala": "danke", "vam": "Ihnen / euch", "molim": "bitte",
    "agent": "Makler", "nekretnine": "Immobilien", "gruntovnicu": "Grundbuch (Akk.)", "kaparu": "Anzahlung (Akk.)",
    "kupoprodajni": "Kauf-", "ugovor": "Vertrag", "notara": "Notar (Gen.)",
    "razgovor": "Gespräch", "ekonomiju": "Wirtschaft (Akk.)", "iskustva": "Erfahrung (Gen.)",
    "računovodstvu": "Buchhaltung (Lok.)", "njemački": "Deutsch (Sprache)", "engleski": "Englisch", "bosanski": "Bosnisch",
    "uslove": "Bedingungen (Akk.)", "probni": "Probe-", "rad": "Arbeit", "radno": "Arbeits-", "plata": "Gehalt", "odgovor": "Antwort",
    "amina": "Amina (Name)", "ajdin": "Ajdin (Name)", "mira": "Mira (Name)", "rex": "Rex (Hundename)",
    # ---- B1-Lesetexte, Paket 1 und 2 (13.11.2026) ------------------------------
    # Jede Wortform der zwölf Texte, die oben noch fehlt, in der Reihenfolge der Texte.
    # Kommt eine Form auch in Paket 3 und 4 vor, steht sie nur hier, mit einer
    # Bedeutung, die in beiden Texten passt (jednom, pravila, žena ...).
    # Adjektive und Possessive mit dem Geschlecht aus dem Text ("zufrieden (m)",
    # "wichtig (w)"), auch wenn die Vokabel alle Formen nennt (Prüfbericht 1.4,
    # B10): Hier steht ein eigener Text, das de der Vokabel bleibt (Kennung).
    # b1_ljeto. kad auch "wann" (Prüfbericht 1.4, B10): "Babo, kad idemo opet?"
    "kad": "als / wenn / wann", "mala": "klein (w)", "svako": "jedes", "ljeto": "Sommer",
    "provodila": "verbracht (w)", "nanina": "Omas (w)", "imala": "gehabt (w)", "ispred": "vor (räumlich)",
    "kuće": "Haus (Gen.)", "orah": "Walnuss / Walnussbaum", "budio": "geweckt (m)", "horoz": "Hahn",
    "kuhinji": "Küche (Lok.)", "pila": "getrunken (w)", "toplo": "warm", "mlijeko": "Milch",
    "doručka": "Frühstück (Gen.)", "išle": "gegangen (w. Mehrz.)", "bere": "pflückt", "zalijeva": "gießt",
    "naučila": "gelernt (w)", "jako": "sehr", "ponosna": "stolz (w)", "popodne": "am Nachmittag", "vruće": "heiß",
    "pa": "und dann / also", "sjedile": "gesessen (w. Mehrz.)", "hladu": "Schatten (Lok.)", "ispod": "unter",
    "oraha": "Walnussbaum (Gen.)", "pričala": "erzählt (w)", "dedi": "Opa (Dat./Lok.)", "vremenu": "Zeit (Lok.)",
    "mlada": "jung (w) / Braut", "slušala": "zugehört (w)", "jela": "gegessen (w)", "trešnje": "Kirschen",
    "komšijine": "des Nachbarn", "bašte": "Garten (Gen.)", "najviše": "am meisten",
    "voljela": "gemocht / geliebt (w)", "subotu": "Samstag (Akk.)", "tada": "damals / dann",
    "pravila": "gemacht (w) / Regeln", "cijela": "ganz (w)", "mirisala": "gerochen / geduftet (w)",
    "tijesto": "Teig", "meso": "Fleisch", "dolazile": "gekommen (w. Mehrz.)",
    "komšinice": "Nachbarinnen / Nachbarin! (Anrede)", "smijale": "gelacht (w. Mehrz.)", "noć": "Nacht",
    "živim": "ich lebe", "njemačkoj": "Deutschland (Lok.)", "ipak": "trotzdem / doch", "dolazim": "ich komme",
    "selo": "Dorf", "čeka": "wartet", "vratima": "Tür (Lok.)", "kao": "wie / als", "nekad": "früher",
    "zagrlim": "ich umarme", "opet": "wieder", "osjećam": "ich fühle", "dijete": "Kind",
    # b1_dijaspora
    "tarik": "Tarik (Name)", "rođen": "geboren (m)", "njegovi": "seine (Mehrz.)", "roditelji": "Eltern",
    "bosne": "Bosnien (Gen.)", "nikad": "nie", "ovog": "dieses (Gen.)", "ljeta": "Sommer (Gen.)",
    "konačno": "endlich", "aerodromu": "Flughafen (Lok.)", "ga": "ihn / es", "čekao": "gewartet (m)",
    "rođak": "Cousin, Verwandter (allgemein)", "haris": "Haris (Name)", "rekao": "gesagt (m)",
    "zagrlio": "umarmt (m)", "nervozan": "nervös (m)", "savršen": "perfekt",
    "brini": "sorg dich (ne brini: keine Sorge)", "smijao": "gelacht (m)", "svi": "alle",
    "razumiju": "sie verstehen", "dijasporu": "Diaspora (Akk.)", "otišli": "gegangen (Mehrz.)", "ulice": "Straßen",
    "bile": "waren (w. Mehrz.)", "pune": "voll (w. Mehrz.)", "turista": "Touristen (Gen.)",
    "malih": "kleinen (Gen. Mehrz.)", "mirisalo": "es roch / duftete", "naručio": "bestellt (m)",
    "ćevapa": "Ćevapi (Gen.)", "s": "mit", "lukom": "Zwiebeln (Instr.)", "jogurt": "Joghurt",
    "najbolje": "das Beste / am besten", "što": "was / dass (im Nebensatz)", "ikad": "jemals", "jeo": "gegessen (m)",
    "šetali": "spaziert (Mehrz.)", "miljacke": "Miljacka (Gen., Fluss in Sarajevo)",
    "vijećnice": "Vijećnica (Gen., Rathaus von Sarajevo)", "pričao": "erzählt (m)", "historiji": "Geschichte (Lok.)",
    "slikao": "fotografiert (m)", "vidio": "gesehen (m)", "žičarom": "mit der Seilbahn",
    "popeli": "hinaufgefahren (Mehrz.)", "trebević": "Trebević (Berg bei Sarajevo)", "odozgo": "von oben",
    "cijeli": "ganz (der ganze)", "svjetla": "Lichter", "polako": "langsam", "palila": "gingen an (Lichter)",
    "govorio": "gesagt / gesprochen (m)", "najljepši": "der schönste", "svijetu": "Welt (Lok.)", "tiho": "leise",
    "sad": "jetzt", "znam": "ich weiß", "pretjerivao": "übertrieben (m)", "spavanja": "Schlafen (Gen.)",
    "nazvao": "angerufen (m)", "roditelje": "Eltern (Akk.)", "ispričao": "erzählt (m)", "obećao": "versprochen (m)",
    # b1_vrijeme
    "petak": "Freitag", "hodžić": "Hodžić (Familienname)", "sjedi": "sitzt",
    "dnevnoj": "Wohn- (dnevna soba: Wohnzimmer)", "vikend": "Wochenende", "planiraju": "sie planen",
    "izlet": "Ausflug", "vrelo": "Quelle", "pažljivo": "aufmerksam", "slušaju": "sie hören zu",
    "vremensku": "Wetter- (Akk.)", "prognozu": "Vorhersage (Akk.)", "radiju": "Radio (Lok.)", "veče": "Abend",
    "slušaoci": "Zuhörer", "biti": "sein", "oblačno": "bewölkt",
    "planinskim": "Berg- (Lok. Mehrz.)", "krajevima": "Gegenden (Lok.)", "moguća": "möglich (w)", "magla": "Nebel",
    "podne": "Mittag", "očekuje": "wird erwartet", "kiša": "Regen", "poslijepodne": "am Nachmittag",
    "grmljavina": "Gewitter", "temperatura": "Temperatur", "petnaest": "fünfzehn", "stepeni": "Grad (Mehrz.)",
    "nedjelju": "Sonntag (Akk.)", "sunčano": "sonnig", "toplije": "wärmer", "temperaturom": "Temperatur (Instr.)",
    "stepena": "Grad (Gen.)", "vidiš": "du siehst", "izleta": "Ausflug (Gen.)", "mama": "Mama",
    "azra": "Azra (Name)", "ako": "wenn / falls", "bude": "sein wird (nach ako / kad)", "padala": "gefallen (w) (Regen, Schnee)",
    "mokri": "nass (Mehrz.)", "predlaže": "schlägt vor", "senad": "Senad (Name)", "možemo": "wir können",
    "napraviti": "machen / zubereiten", "roštiljati": "grillen", "dino": "Dino (Name)",
    "zadovoljan": "zufrieden (m)", "raditi": "arbeiten / tun", "zaista": "wirklich / tatsächlich",
    "sijalo": "geschienen (s)", "spakovala": "eingepackt (w)", "hranu": "Essen (Akk.)", "krenula": "losgefahren (w)",
    "trčao": "gerannt (m)", "po": "durch / (jemanden) holen", "hranio": "gefüttert (m)", "patke": "Enten (Akk.)",
    "umorno": "müde", "prognoza": "Prognose", "tačna": "richtig / genau (w)",
    # b1_voz
    "lejla": "Lejla (Name)", "emir": "Emir (Name)", "prvi": "der erste", "put": "Weg / Mal / Reise",
    "vozom": "mit dem Zug", "mostar": "Mostar", "voz": "Zug", "polazi": "fährt ab", "putovanje": "Reise",
    "sata": "Stunde (Gen.) / Uhr", "puta": "Mal / preko puta: gegenüber", "njih": "sie (Gen. Mehrz.)", "starija": "ältere",
    "žena": "Frau / Ehefrau", "velikom": "großen (Instr.)", "torbom": "Tasche (Instr.)", "putujete": "ihr reist / Sie reisen",
    "djeco": "Kinder! (Anrede)", "morate": "ihr müsst / Sie müssen", "vidjeti": "sehen", "most": "Brücke",
    "budete": "ihr seid (nach kad)", "probajte": "probiert!", "uskoro": "bald", "dolazi": "kommt",
    "kondukter": "Schaffner", "karte": "Fahrkarten", "redu": "Ordnung (Lok.) (u redu: in Ordnung)", "sretan": "glücklich (m)",
    "konjica": "Konjic (Gen.)", "pruga": "Bahngleis", "neretve": "Neretva (Gen.)", "rijeka": "Fluss",
    "zelena": "grün", "planine": "Berge", "visoke": "hoch (Mehrz.)", "strme": "steil (Mehrz.)", "stalno": "ständig",
    "slika": "fotografiert / Bild", "telefonom": "mit dem Handy", "pogledaj": "schau!", "emire": "Emir! (Anrede)",
    "ljepše": "schöner", "nego": "als (Vergleich)", "slikama": "Bildern (Lok.)", "otvara": "öffnet",
    "torbu": "Tasche (Akk.)", "vadi": "holt heraus", "uzmite": "nehmt!", "sama": "selbst / allein (w)",
    "pekla": "gebacken (w)", "nisu": "sind nicht / haben nicht", "gladni": "hungrig (Mehrz.)", "odustaje": "gibt auf",
    "hajde": "los! / komm!", "nemojte": "tut nicht! / tun Sie nicht! (Verbot)", "stidjeti": "sich schämen", "pričaju": "sie reden",
    "mostaru": "Mostar (Lok.)", "devet": "neun", "stiže": "kommt an", "daje": "gibt",
    # svoj (Prüfbericht 1.4, S6): nicht nur "mein eigener", in b1_voz ("Žena im
    # daje svoj broj") und b1_telefon ist es "ihr eigener". Die Vokabel behält
    # ihr de "eigener (mein, dein, sein)", das ist ihre Kennung.
    "svoj": "eigener (mein, dein, sein, ihr …)", "broj": "Zahl / Nummer", "telefona": "Telefon (Gen.)",
    "zatreba": "nötig wird", "nazovite": "ruft an!", "nisi": "du bist nicht", "putu": "Weg / Reise (Lok.)",
    # b1_rafting
    "prijatelji": "Freunde", "julu": "Juli (Lok.)", "bihać": "Bihać", "dugo": "lange", "htjeli": "gewollt (Mehrz.)",
    "probati": "probieren / kosten", "rafting": "Rafting", "uni": "Una (Lok., Fluss)", "una": "Una (Fluss)",
    "najljepših": "der schönsten (Gen. Mehrz.)", "voda": "Wasser", "čista": "sauber / klar (w)",
    "nekim": "manchen (Lok. Mehrz.)", "mjestima": "Stellen (Lok.)", "brza": "schnell (w)",
    "došli": "gekommen (Mehrz.)", "kamp": "Campingplatz", "instruktor": "Lehrer / Instruktor",
    "mirza": "Mirza (Name)", "dao": "gegeben (m)", "kacige": "Helme", "prsluke": "Westen (Akk.)", "vesla": "Paddel",
    "slušajte": "hört zu!", "kažem": "ich sage", "naprijed": "vorwärts / nach vorne", "veslajte": "paddelt!",
    "stop": "Stopp", "prestanite": "hört auf!", "neko": "jemand", "padne": "fällt", "vodu": "Wasser (Akk.)",
    "ostanite": "bleibt!", "mirni": "ruhig (Mehrz.)", "prsluk": "Weste", "vas": "euch / Sie", "držati": "halten",
    "sat": "Stunde / Uhr", "lagan": "leicht (m)", "čamac": "Boot", "mirno": "ruhig", "plovio": "gefahren (Boot, m)",
    "gledali": "geschaut (Mehrz.)", "ptice": "Vögel", "drveće": "Bäume (Sammelwort)", "obali": "Ufer (Lok.)",
    "postala": "geworden (w)", "brža": "schneller (w)", "glasnija": "lauter (w)", "pred": "vor (direkt davor)",
    "njima": "ihnen", "slap": "Wasserfall", "jače": "stärker", "vikao": "gerufen (m)", "skočio": "gesprungen (m)",
    "slapa": "Wasserfall (Gen.)", "pao": "gefallen (m)", "hladna": "kalt (w)", "led": "Eis (gefrorenes Wasser)",
    "držao": "gehalten (m)", "izvukli": "herausgezogen (Mehrz.)", "jesi": "bist du", "li": "(Fragepartikel)",
    "pitao": "gefragt (m)", "jesam": "ja, bin ich", "odgovorio": "geantwortet (m)", "mokar": "nass",
    "kože": "Haut (Gen.)", "stvarno": "wirklich", "budan": "wach", "smijali": "gelacht (Mehrz.)",
    "raftinga": "Rafting (Gen.)", "jeli": "gegessen (Mehrz.)", "pastrmku": "Forelle (Akk.)",
    "dolazimo": "wir kommen",
    # b1_jahorina
    "novu": "neue (Akk.)", "godinu": "Jahr (Akk.)", "jahorinu": "Jahorina (Akk., Berg)", "dobra": "gut (w)",
    "skijašica": "Skifahrerin", "skijao": "Ski gefahren (m)", "naučit": "lernen (naučit ću: ich werde lernen)",
    "samouvjereno": "selbstsicher", "prvog": "ersten (Gen.)", "jutra": "Morgen (Gen.)",
    "iznajmili": "ausgeliehen (Mehrz.)", "skije": "Skier", "skijaške": "Ski- (skijaške cipele: Skischuhe)",
    "cipele": "Schuhe", "štapove": "Stöcke (Akk.)",
    "obukao": "angezogen (m)", "debelu": "dicke (Akk.)", "jaknu": "Jacke (Akk.)", "kapu": "Mütze (Akk.)",
    "rukavice": "Handschuhe", "vani": "draußen", "minus": "minus", "snijega": "Schnee (Gen.)",
    "skoro": "fast / bald", "metar": "Meter", "stazu": "Piste (Akk.)", "školu": "Schule (Akk.)",
    "skijanja": "Skifahren (Gen.)", "njegova": "seine (w)", "instruktorica": "Lehrerin / Instruktorin",
    "djevojka": "Mädchen / Freundin", "strpljenja": "Geduld (Gen.)", "savijte": "beugt!", "koljena": "Knie (Mehrz.)",
    "gledajte": "schaut!", "govorila": "gesagt (w)", "djeca": "Kinder", "šest": "sechs", "lako": "leicht / einfach",
    "prestizala": "überholten (Mehrz.)", "bolje": "besser (Adverb)", "spustio": "heruntergefahren (m)", "niz": "hinunter",
    "malu": "kleine (Akk.)", "ijednog": "einzigen (Gen.)", "pada": "Sturz (Gen.)", "ponosan": "stolz (m)",
    "sjedili": "gesessen (Mehrz.)", "kafiću": "Café (Lok.)", "kamina": "Kamin (Gen.)", "pili": "getrunken (Mehrz.)",
    "čaj": "Tee", "medom": "Honig (Instr.)", "padao": "gefallen (m)", "snijeg": "Schnee", "boli": "tut weh",
    "trećeg": "dritten (Gen.)", "spustili": "heruntergefahren (Mehrz.)", "hotela": "Hotel (Gen.)",
    "žalio": "beschwert (m)", "zime": "Winter (Gen.)", "dolje": "unten",
    # b1_pita
    "studira": "studiert", "beču": "Wien (Lok.)", "praznike": "Ferien (Akk.)", "došla": "gekommen (w)",
    "rekla": "gesagt (w)", "nauči": "bring mir bei!", "pravim": "ich mache", "niko": "niemand", "zna": "er/sie weiß / kann",
    "pravu": "echte (Akk.)", "nasmijala": "aufgelacht (w)", "moraš": "du musst", "strpljiva": "geduldig (w)",
    "pravi": "er/sie macht", "brzinu": "Schnelle (Akk.) (na brzinu: auf die Schnelle)", "zamijesile": "geknetet (w. Mehrz.)", "brašna": "Mehl (Gen.)",
    "vode": "Wasser (Gen.)", "soli": "Salz (Gen.)", "ulja": "Öl (Gen.)", "odmori": "ruht (sich) aus", "odmarati": "ruhen / sich ausruhen",
    "pola": "die Hälfte", "međuvremenu": "Zwischenzeit (Lok.)", "pripremile": "vorbereitet (w. Mehrz.)",
    "nadjev": "Füllung", "oguljile": "geschält (w. Mehrz.)", "krompir": "Kartoffel",
    "isjekle": "geschnitten (w. Mehrz.)", "male": "kleine (Akk. Mehrz.)", "kocke": "Würfel (Akk. Mehrz.)",
    "dodale": "hinzugefügt (w. Mehrz.)", "so": "Salz", "biber": "Pfeffer", "najteži": "der schwerste", "dio": "Teil",
    "stavila": "gelegt (w)", "veliki": "groß (m)", "razvijala": "ausgerollt (w)",
    "oklagijom": "Nudelholz (Instr.)", "dok": "während / bis", "postalo": "geworden (s)", "tanko": "dünn (s)",
    "papir": "Papier", "probala": "probiert (w)", "odmah": "sofort", "poderalo": "gerissen (s)", "meni": "mir",
    "dešavalo": "passiert (s)", "stavile": "gelegt (w. Mehrz.)", "savile": "gerollt (w. Mehrz.)",
    "tepsiju": "Backblech (Akk.)", "vremena": "Zeit (Gen.)", "probao": "probiert (m)", "ovu": "diese (Akk.)",
    "zar": "(zar ne: nicht wahr)", "drugačija": "anders (w)", "odlična": "ausgezeichnet (w)",
    "sretna": "glücklich (w)", "naninu": "Omas (Akk.)", "tajnu": "Geheimnis (Akk.)", "puno": "viel",
    "ljubavi": "Liebe (Gen.)",
    # b1_struja
    "hladno": "kalt (s)", "januarsko": "Januar- (s)", "merima": "Merima (Name)", "baš": "gerade / genau",
    "kuhala": "gekocht (w)", "odjednom": "plötzlich", "nestalo": "weg / verschwunden (s)", "struje": "Strom (Gen.)",
    "zgrada": "Gebäude", "mraku": "Dunkelheit (Lok.)", "sin": "Sohn", "kenan": "Kenan (Name)",
    "uplašio": "erschrocken (m)", "počeo": "begonnen (m)", "plakati": "weinen", "upalila": "eingeschaltet (w)",
    "svjetlo": "Licht", "telefonu": "Telefon (Lok.)", "našla": "gefunden (w)", "svijeće": "Kerzen",
    "ladici": "Schublade (Lok.)", "pokucao": "geklopft (m)", "komšija": "Nachbar", "hasan": "Hasan (Name)",
    "sprata": "Stockwerk (Gen.)", "znate": "wissen Sie / ihr wisst", "desilo": "passiert (s)",
    "zvao": "angerufen (m)", "kažu": "sie sagen", "kvar": "Defekt / Panne", "cijelom": "ganzen (Lok.)",
    "naselju": "Siedlung (Lok.)", "popraviti": "reparieren", "dva-tri": "zwei, drei", "imao": "gehabt (m)",
    "plinski": "Gas-", "šporet": "Herd", "pozvao": "eingeladen (m)", "komšije": "Nachbarn (Mehrzahl)",
    "njegovom": "seiner (Lok.)", "stanu": "Wohnung (Lok.)", "desetak": "etwa zehn", "ljudi": "Leute",
    "komšinica": "Nachbarin", "zehra": "Zehra (Name)", "donijela": "gebracht (w)", "kolače": "Kuchen (Akk. Mehrz.)",
    "mladi": "junge (m)", "bračni": "ehelich / Ehe-", "par": "Paar / ein paar", "donio": "gebracht (m)",
    "gitaru": "Gitarre (Akk.)", "igrala": "gespielt / getanzt (w)", "hodniku": "Flur (Lok.)",
    "odrasli": "Erwachsene", "pričali": "geredet (Mehrz.)", "pjevali": "gesungen (Mehrz.)", "živimo": "wir leben",
    "ovoj": "dieser (Lok.)", "zgradi": "Gebäude (Lok.)", "nismo": "wir sind nicht", "ovako": "so (wie hier)",
    "struja": "Strom", "vratila": "zurückgekommen (w)", "razočarano": "enttäuscht",
    "zapljeskali": "geklatscht (Mehrz.)", "šteta": "schade", "večeri": "Abend (Gen.)", "češće": "öfter",
    "druže": "treffen sich",
    # b1_svadba
    "subote": "Samstag (Gen.)", "oženio": "geheiratet (m)", "adnan": "Adnan (Name)", "sara": "Sara (Name)",
    "tuzle": "Tuzla (Gen.)", "svadba": "Hochzeit", "jednom": "einem (Lok.) / einmal",
    "restoranu": "Restaurant (Lok.)", "došlo": "gekommen (s)", "dvjesto": "zweihundert", "gostiju": "Gäste (Gen.)",
    "rodbina": "Verwandtschaft", "čak": "sogar", "adnanov": "Adnans", "šef": "Chef", "autima": "mit Autos",
    "mladu": "Braut (Akk.)", "cijelim": "ganzen (Instr.)", "putem": "Weg (Instr.)", "trubili": "gehupt (Mehrz.)",
    "izašla": "herausgekommen (w)", "bijeloj": "weißen (Lok.)", "vjenčanici": "Brautkleid (Lok.)",
    "sreće": "Glück (Gen.)", "svirao": "gespielt (Musik, m)", "bend": "Band (Musik)", "mladenci": "Brautpaar",
    "plesali": "getanzt (Mehrz.)", "plesala": "getanzt (w)", "sami": "allein (Mehrz.)", "ustali": "aufgestanden (Mehrz.)",
    "uhvatili": "gefasst (Mehrz.)", "ruke": "Hände (Akk.)", "igrali": "gespielt / getanzt (Mehrz.)",
    "kolo": "Kolo (bosnischer Reigentanz)", "cijele": "ganzen (Gen.)", "sale": "Saal (Gen.)",
    "najmlađih": "der Jüngsten (Gen. Mehrz.)", "najstarijih": "der Ältesten (Gen. Mehrz.)",
    "svojih": "ihrer eigenen (Gen. Mehrz.)", "mene": "mich", "hrane": "Essen (Gen.)", "supa": "Suppe",
    "sarma": "Sarma (Krautwickel)", "pečenje": "Braten", "salate": "Salate", "torta": "Torte", "toliko": "so viel",
    "najela": "satt gegessen (w)", "više": "mehr", "nisam": "ich bin nicht", "plesati": "tanzen",
    "ponoći": "Mitternacht (Gen.)", "rezali": "geschnitten (Mehrz.)", "tortu": "Torte (Akk.)",
    "održao": "gehalten (m)", "kratak": "kurz", "govor": "Rede", "zahvalio": "bedankt (m)",
    "roditeljima": "Eltern (Dat.)", "pogledao": "angeschaut (m)", "saru": "Sara (Akk.)", "nova": "neue (w)",
    "sutradan": "am nächsten Tag", "umorna": "müde (w)",
    # b1_posao
    "završio": "abgeschlossen (m)",
    "elektrotehnički": "Elektrotechnik- (elektrotehnički fakultet: Fakultät für Elektrotechnik)",
    "fakultet": "Fakultät (Studium)", "ponedjeljak": "Montag",
    "zenici": "Zenica (Lok.)", "mogao": "gekonnt (m)", "ustao": "aufgestanden (m)", "košulju": "Hemd (Akk.)",
    "provjerio": "überprüft (m)", "ponio": "mitgenommen (m)", "dokumente": "Dokumente (Akk.)",
    "poslu": "Arbeit (Lok.)", "dočekala": "empfangen (w)", "šefica": "Chefin", "gospođa": "Frau (Anrede)",
    "mujić": "Mujić (Familienname)", "jutro": "Morgen (Tageszeit)", "harise": "Haris! (Anrede)",
    "pokazati": "zeigen", "vašu": "Ihre (Akk.)", "kancelariju": "Büro (Akk.)", "ćete": "ihr werdet",
    "upoznati": "jemanden kennenlernen", "ljubazni": "freundlich (Mehrz.)", "najstariji": "der älteste", "među": "zwischen / unter (mehreren)",
    "nedžad": "Nedžad (Name)", "radi": "er/sie arbeitet", "pitaj": "frag!", "nemoj": "tu nicht! (Verbot)",
    "čitao": "gelesen (m)", "firme": "Firma (Gen.)", "pauzu": "Pause (Akk.)", "znao": "gewusst (m)",
    "pije": "trinkt (se pije: wird getrunken)", "ostao": "geblieben (m)", "stolom": "Tisch (Instr.)", "vratio": "zurückgekommen (m)",
    "njega": "ihn", "obavezna": "Pflicht / verpflichtend (w)", "pauze": "Pause (Gen.)", "dobio": "bekommen (m)", "zadatak": "Aufgabe",
    "morao": "gemusst (m)", "aparat": "Gerät", "trebalo": "gebraucht (s)", "uspio": "geschafft (m)",
    "zadovoljna": "zufrieden (w)", "odlično": "ausgezeichnet", "nazvala": "angerufen (w)", "umoran": "müde (m)",
    "svidjeti": "gefallen",
    # b1_stan
    "selma": "Selma (Name)", "dobila": "bekommen (w)", "traži": "sucht", "stan": "Wohnung",
    "internetu": "Internet (Lok.)", "oglas": "Anzeige / Inserat", "izdajem": "ich vermiete",
    "jednosoban": "Einzimmer-", "grbavici": "Grbavica (Lok., Stadtteil von Sarajevo)", "četrdeset": "vierzig",
    "kvadrata": "Quadratmeter (Gen.)", "treći": "der dritte", "sprat": "Stockwerk", "lift": "Aufzug",
    "namješten": "möbliert", "renoviran": "renoviert", "balkon": "Balkon", "blizini": "Nähe (Lok.)",
    "tramvaj": "Straßenbahn", "škola": "Schule", "prodavnica": "Laden", "kirija": "Miete", "petsto": "fünfhundert",
    "mjesečno": "monatlich", "plus": "plus", "režije": "Nebenkosten", "kućni": "Haus- (kućni ljubimci: Haustiere)",
    "ljubimci": "Lieblinge (kućni ljubimci: Haustiere)", "dozvoljeni": "erlaubt (Mehrz.)",
    "zvati": "rufen / anrufen", "zbog": "wegen", "oglasa": "Anzeige (Gen.)", "slobodan": "frei",
    "marta": "März (Gen.)", "otprilike": "ungefähr", "zimi": "im Winter", "stotinu": "hundert", "ljeti": "im Sommer",
    "manje": "weniger", "grijanje": "Heizung", "centralno": "zentral", "mirna": "ruhig (w)", "sedmično": "pro Woche",
    "vrlo": "sehr (vor Eigenschaften)", "uglavnom": "meistens / hauptsächlich", "stariji": "älter",
    "bih": "würde (ich)", "pogledati": "ansehen / schauen", "vidimo": "wir sehen (uns)", "pogledala": "geschaut / angeschaut (w)",
    "svijetao": "hell", "čist": "sauber (m)", "balkona": "Balkon (Gen.)", "potpisala": "unterschrieben (w)",
    "prvu": "erste (Akk.)", "spavala": "geschlafen (w)", "madracu": "Matratze (Lok.)", "podu": "Boden (Lok.)",
    "presretna": "überglücklich (w)",
    # b1_telefon
    "sjela": "hingesetzt (w)", "kafić": "Café", "baščaršiji": "Baščaršija (Lok.)", "blizu": "in der Nähe von",
    "sebilja": "Sebilj (Gen., Brunnen auf der Baščaršija)", "popila": "getrunken (w)", "platila": "bezahlt (w)",
    "tramvajem": "mit der Straßenbahn", "htjela": "gewollt (w)", "nazvati": "anrufen", "mamu": "Mama (Akk.)",
    "torbi": "Tasche (Lok.)", "tražila": "gesucht (w)", "svugdje": "überall", "jakni": "Jacke (Lok.)",
    "kreveta": "Bett (Gen.)", "ništa": "nichts", "ajdine": "Ajdin! (Anrede)", "nazovi": "ruf an!",
    "telefon": "Telefon", "zvonio": "geklingelt (m)", "javio": "gemeldet (m)", "nervozna": "nervös (w)",
    "njeni": "ihre (Mehrz.)", "brojevi": "Nummern", "ajdinovog": "Ajdins (Gen.)", "napisala": "geschrieben (w)",
    "poruku": "Nachricht (Akk.)", "izgubila": "verloren (w)", "negdje": "irgendwo", "našli": "gefunden (Mehrz.)",
    "javite": "melden Sie sich!", "kasnije": "später", "zazvonio": "geklingelt (einmal, m)", "ajdinov": "Ajdins",
    "konobar": "Kellner", "tom": "diesem (Lok.)", "vaš": "euer / Ihr (m)", "stola": "Tisch (Gen.)",
    "našao": "gefunden (m)", "čistio": "geputzt (m)", "možete": "ihr könnt / Sie können",
    "sačuvat": "aufbewahren (sačuvat ću: ich bewahre auf)", "odahnula": "aufgeatmet (w)", "joj": "ihr (Dativ)",
    "dirao": "angefasst (m)", "dati": "geben", "htio": "wollte (m)", "uzeti": "nehmen", "novac": "Geld",
    "drago": "lieb (bilo bi mi drago: es würde mich freuen)", "dođete": "ihr kommt / Sie kommen",
    "svake": "jede (Gen.)",
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
        # "napraviti pitu" statt "skuhati pitu" (Prüfbericht 1.4, S3; Ajdin, F20,
        # 14.11.2026: "man sagt napraviti pitu nicht skuhati"). Der Ton (g09) gehört
        # noch zum alten Text, die Geschichte wartet bis zur nächsten Vesna-Runde
        # (tests/offen_b1_teil2.py).
        "text":"Draga nano, kako si? Mi smo dobro. Prošle sedmice sam počela novi posao u jednoj firmi u centru grada. "
                "Kolege su ljubazne, ali još ne razumijem sve jer govore brzo. Ajdin kaže da ću naučiti. "
                "Navečer učim bosanski, a vikendom idemo u prirodu. Mislim da ćemo u augustu doći kod tebe. "
                "Nadam se da ćeš nam napraviti pitu! Pozdravi dedu. Volim te, tvoja Amina.",
        "uebersetzung": "Liebe Oma, wie geht es dir? Uns geht es gut. Letzte Woche habe ich eine neue Arbeit in einer Firma im Stadtzentrum begonnen. "
                "Die Kollegen sind freundlich, aber ich verstehe noch nicht alles, weil sie schnell sprechen. Ajdin sagt, dass ich es lernen werde. "
                "Abends lerne ich Bosnisch, und am Wochenende gehen wir in die Natur. Ich denke, dass wir im August zu dir kommen. "
                "Ich hoffe, dass du uns eine Pita machst! Grüß den Opa. Ich liebe dich, deine Amina.",
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
        # "Direktor je pita": je ist hier "sie" (Prüfbericht 1.4, B10)
        "vokabeln": {"je": "ist / sie (Akk.)"},
        "fragen": [
            {"frage": "Wie viele Jahre Erfahrung hat Amina?", "optionen": ["drei", "fünf", "zehn"], "richtig": "drei"},
            {"frage": "Wie lange dauert die Probezeit?", "optionen": ["drei Monate", "einen Monat", "ein Jahr"], "richtig": "drei Monate"},
            {"frage": "Wann wird das Gehalt gezahlt?", "optionen": ["am Fünften des Monats", "am Monatsende", "jede Woche"], "richtig": "am Fünften des Monats"},
        ],
    },
    # ---- B1 (13.11.2026): Lesetexte mit 160 bis 200 Wörtern -------------------
    # Paket 1 und 2 von 4. Die Themen hat Ajdin am 08.11.2026 freigegeben, die drei
    # Proben (Ljeto, Voz, Telefon) am 13.11.2026. Bosnisch ist ein Entwurf von
    # Claude, die fraglichen Stellen prüft Ajdin. Absätze stehen als Leerzeile im
    # Text, die App zeigt sie (white-space: pre-line). Ton folgt (Azure, Vesna).
    {
        "id": "b1_ljeto", "titel": "Ljeto kod nane na selu", "stufe": "B1", "passt_zu": "familie",
        "text": ("Kad sam bila mala, svako ljeto sam provodila kod nane na selu. Nanina kuća nije bila velika, ali je imala veliku baštu, a ispred kuće je bio stari orah.\n\n"
                 "Ujutro me budio horoz. Kad sam ustala, nana je već bila u kuhinji. Ona je pila kahvu, a ja toplo mlijeko. Poslije doručka smo išle u baštu. Nana mi je pokazala kako se bere paradajz i kako se zalijeva cvijeće. Brzo sam to naučila i bila sam jako ponosna.\n\n"
                 "Popodne je bilo vruće, pa smo sjedile u hladu ispod oraha. Nana je pričala o dedi i o vremenu kad je bila mlada. Ja sam slušala i jela trešnje iz komšijine bašte.\n\n"
                 "Najviše sam voljela subotu jer je nana tada pravila pitu. Cijela kuća je mirisala na tijesto, meso i luk. Navečer su dolazile komšinice. Pile su kahvu, pričale i smijale se do kasno u noć.\n\n"
                 "Sada živim i radim u Njemačkoj. Ipak, svako ljeto dolazim na selo. Nana me čeka na vratima, kao nekad. Kad je zagrlim, opet se osjećam kao dijete."),
        "uebersetzung": ("Als ich klein war, habe ich jeden Sommer bei meiner Oma auf dem Dorf verbracht. Omas Haus war nicht groß, aber es hatte einen großen Garten, und vor dem Haus stand ein alter Walnussbaum.\n\n"
                         "Morgens hat mich der Hahn geweckt. Wenn ich aufstand, war Oma schon in der Küche. Sie trank Kaffee und ich warme Milch. Nach dem Frühstück gingen wir in den Garten. Oma hat mir gezeigt, wie man Tomaten pflückt und wie man die Blumen gießt. Ich habe das schnell gelernt und war sehr stolz.\n\n"
                         "Am Nachmittag war es heiß, also saßen wir im Schatten unter dem Walnussbaum. Oma erzählte von Opa und von der Zeit, als sie jung war. Ich hörte zu und aß Kirschen aus dem Garten des Nachbarn.\n\n"
                         "Am liebsten mochte ich den Samstag, weil Oma da Pita machte. Das ganze Haus roch nach Teig, Fleisch und Zwiebeln. Abends kamen die Nachbarinnen. Sie tranken Kaffee, redeten und lachten bis spät in die Nacht.\n\n"
                         "Jetzt lebe und arbeite ich in Deutschland. Trotzdem komme ich jeden Sommer ins Dorf. Oma wartet an der Tür auf mich, wie früher. Wenn ich sie umarme, fühle ich mich wieder wie ein Kind."),
        # "Kad je zagrlim": je ist hier "sie" (Prüfbericht 1.4, B10)
        "vokabeln": {"je": "ist / sie (Akk.)"},
        "fragen": [
            {"frage": "Was stand vor Omas Haus?", "optionen": ["ein alter Walnussbaum", "ein Kirschbaum", "ein Brunnen"], "richtig": "ein alter Walnussbaum"},
            {"frage": "Was trank das Mädchen am Morgen?", "optionen": ["warme Milch", "Kaffee", "Tee"], "richtig": "warme Milch"},
            {"frage": "Warum mochte sie den Samstag am liebsten?", "optionen": ["Oma machte Pita", "die Nachbarinnen kamen", "sie schlief länger"], "richtig": "Oma machte Pita"},
        ],
    },
    {
        "id": "b1_dijaspora", "titel": "Dijaspora prvi put u Sarajevu", "stufe": "B1", "passt_zu": "urlaub",
        # A/B-Liste (Lesetexte_Fragen_AB.md), Ajdin 15.11.2026: L9 B, "deset ćevapa"
        # statt "desetku".
        "text": ("Tarik ima dvadeset godina i rođen je u Njemačkoj. Njegovi roditelji su iz Bosne, ali on nikad nije bio u Sarajevu. Ovog ljeta je konačno došao. Na aerodromu ga je čekao rođak Haris.\n\n"
                 "„Dobro došao!“ rekao je Haris i zagrlio ga. Tarik je bio malo nervozan jer njegov bosanski nije savršen. „Ne brini“, smijao se Haris. „Ovdje svi razumiju dijasporu.“\n\n"
                 "Prvo su otišli na Baščaršiju. Ulice su bile pune turista, a iz malih radnji je mirisalo na kahvu i ćevape. Tarik je naručio deset ćevapa s lukom i jogurt. „Ovo je najbolje što sam ikad jeo!“ rekao je.\n\n"
                 "Poslije ručka su šetali pored Miljacke do Vijećnice. Haris mu je pričao o historiji grada, a Tarik je slikao sve što je vidio. Navečer su se žičarom popeli na Trebević. Odozgo se vidio cijeli grad, a svjetla su se polako palila.\n\n"
                 "„Moj babo je uvijek govorio da je Sarajevo najljepši grad na svijetu“, rekao je Tarik tiho. „Sad znam da nije pretjerivao.“\n\n"
                 "Prije spavanja je nazvao roditelje i sve im ispričao. „Sljedeće godine opet dolazim, ali na duže“, obećao je."),
        "uebersetzung": ("Tarik ist zwanzig Jahre alt und in Deutschland geboren. Seine Eltern kommen aus Bosnien, aber er war noch nie in Sarajevo. Diesen Sommer ist er endlich gekommen. Am Flughafen wartete sein Cousin Haris auf ihn.\n\n"
                         "„Willkommen!“, sagte Haris und umarmte ihn. Tarik war ein bisschen nervös, weil sein Bosnisch nicht perfekt ist. „Keine Sorge“, lachte Haris. „Hier verstehen alle die Diaspora.“\n\n"
                         "Zuerst gingen sie auf die Baščaršija. Die Straßen waren voller Touristen, und aus den kleinen Läden duftete es nach Kaffee und Ćevapi. Tarik bestellte zehn Ćevapi mit Zwiebeln und einen Joghurt. „Das ist das Beste, was ich je gegessen habe!“, sagte er.\n\n"
                         "Nach dem Mittagessen spazierten sie an der Miljacka entlang bis zur Vijećnica. Haris erzählte ihm von der Geschichte der Stadt, und Tarik fotografierte alles, was er sah. Abends fuhren sie mit der Seilbahn auf den Trebević. Von oben sah man die ganze Stadt, und langsam gingen die Lichter an.\n\n"
                         "„Mein Papa hat immer gesagt, dass Sarajevo die schönste Stadt der Welt ist“, sagte Tarik leise. „Jetzt weiß ich, dass er nicht übertrieben hat.“\n\n"
                         "Vor dem Schlafengehen rief er seine Eltern an und erzählte ihnen alles. „Nächstes Jahr komme ich wieder, aber für länger“, versprach er."),
        "vokabeln": {"radnji": "Läden (Gen. Mehrz.)"},
        "fragen": [
            {"frage": "Wo ist Tarik geboren?", "optionen": ["in Deutschland", "in Sarajevo", "in Österreich"], "richtig": "in Deutschland"},
            {"frage": "Was hat Tarik auf der Baščaršija gegessen?", "optionen": ["Ćevapi mit Zwiebeln", "Burek", "Pita mit Käse"], "richtig": "Ćevapi mit Zwiebeln"},
            {"frage": "Womit sind sie auf den Trebević gefahren?", "optionen": ["mit der Seilbahn", "mit dem Auto", "mit der Straßenbahn"], "richtig": "mit der Seilbahn"},
        ],
    },
    {
        "id": "b1_vrijeme", "titel": "Vrijeme za vikend", "stufe": "B1", "passt_zu": "wetter",
        # A/B-Liste, Ajdin 15.11.2026: L10 B "dragi slušaoci" statt "poštovani", L12 B
        # "možemo i roštiljati" statt "napraviti i roštilj". L11 A: "poslijepodne" bleibt.
        "text": ("U petak navečer porodica Hodžić sjedi u dnevnoj sobi. Za vikend planiraju izlet na Vrelo Bosne, pa svi pažljivo slušaju vremensku prognozu na radiju.\n\n"
                 "„Dobro veče, dragi slušaoci. Sutra, u subotu, ujutro će biti oblačno, a u planinskim krajevima moguća je magla. Oko podne se očekuje kiša, a poslijepodne i grmljavina. Temperatura će biti od deset do petnaest stepeni. U nedjelju će biti sunčano i toplije, s temperaturom do dvadeset dva stepena.“\n\n"
                 "„Vidiš, u subotu nema izleta“, kaže mama Azra. „Ako bude padala kiša, svi ćemo biti mokri.“\n\n"
                 "„Onda idemo u nedjelju“, predlaže babo Senad. „Ako bude sunčano, možemo i roštiljati.“\n\n"
                 "Mali Dino nije zadovoljan. „A šta ćemo raditi u subotu?“\n\n"
                 "„U subotu idemo kod nane“, odgovara mama. „Kod nane je uvijek lijepo vrijeme.“\n\n"
                 "U nedjelju ujutro sunce je zaista sijalo. Porodica je spakovala hranu i krenula na Vrelo Bosne. Dino je cijeli dan trčao po parku i hranio patke. Navečer je umorno rekao: „Ova prognoza je bila tačna.“"),
        "uebersetzung": ("Am Freitagabend sitzt Familie Hodžić im Wohnzimmer. Am Wochenende planen sie einen Ausflug zum Vrelo Bosne, deshalb hören alle aufmerksam den Wetterbericht im Radio.\n\n"
                         "„Guten Abend, liebe Hörerinnen und Hörer. Morgen, am Samstag, wird es am Vormittag bewölkt, in den Bergen ist Nebel möglich. Gegen Mittag wird Regen erwartet, am Nachmittag auch Gewitter. Die Temperaturen liegen zwischen zehn und fünfzehn Grad. Am Sonntag wird es sonnig und wärmer, mit Temperaturen bis zweiundzwanzig Grad.“\n\n"
                         "„Siehst du, am Samstag gibt es keinen Ausflug“, sagt Mama Azra. „Wenn es regnet, werden wir alle nass.“\n\n"
                         "„Dann fahren wir am Sonntag“, schlägt Papa Senad vor. „Wenn es sonnig ist, können wir auch grillen.“\n\n"
                         "Der kleine Dino ist nicht zufrieden. „Und was machen wir am Samstag?“\n\n"
                         "„Am Samstag gehen wir zur Oma“, antwortet Mama. „Bei Oma ist immer schönes Wetter.“\n\n"
                         "Am Sonntagmorgen schien wirklich die Sonne. Die Familie packte Essen ein und fuhr zum Vrelo Bosne. Dino rannte den ganzen Tag durch den Park und fütterte die Enten. Abends sagte er müde: „Diese Vorhersage hat gestimmt.“"),
        # "dragi slušaoci" ist Mehrzahl; im WOERTERBUCH steht "lieber" aus b1_mejl
        # ("Dragi Adnane").
        "vokabeln": {"dragi": "liebe (Mehrz.)"},
        "fragen": [
            {"frage": "Wie wird das Wetter am Samstag?", "optionen": ["bewölkt, mit Regen und Gewitter", "sonnig und warm", "kalt, mit Schnee"], "richtig": "bewölkt, mit Regen und Gewitter"},
            {"frage": "Wohin geht die Familie am Samstag?", "optionen": ["zur Oma", "zum Vrelo Bosne", "ins Kino"], "richtig": "zur Oma"},
            {"frage": "Was hat Dino am Sonntag gemacht?", "optionen": ["die Enten gefüttert", "ferngesehen", "bei der Oma geschlafen"], "richtig": "die Enten gefüttert"},
        ],
    },
    {
        "id": "b1_voz", "titel": "Voz Sarajevo–Mostar", "stufe": "B1", "passt_zu": "urlaub",
        "text": ("Lejla i njen brat Emir žive u Njemačkoj. Ovog ljeta su prvi put zajedno u Bosni. Danas idu vozom iz Sarajeva u Mostar. Voz polazi u sedam i petnaest, a putovanje traje oko dva sata.\n\n"
                 "Lejla sjedi pored prozora. Preko puta njih sjedi jedna starija žena s velikom torbom. „Gdje putujete, djeco?“ pita ona. „U Mostar, prvi put“, odgovara Emir. „Onda morate vidjeti Stari most. A kad budete u gradu, probajte i ćevape!“\n\n"
                 "Uskoro dolazi kondukter. „Karte, molim.“ Emir mu pokazuje karte. „Sve je u redu. Sretan put!“\n\n"
                 "Poslije Konjica pruga ide pored Neretve. Rijeka je zelena, a planine su visoke i strme. Lejla stalno slika telefonom. „Pogledaj, Emire! Ovo je ljepše nego na slikama.“\n\n"
                 "Žena otvara torbu i vadi pitu. „Uzmite, sama sam je pekla.“ Emir kaže da nisu gladni, ali žena ne odustaje: „Hajde, nemojte se stidjeti!“ Na kraju jedu pitu i pričaju o Mostaru.\n\n"
                 "Malo poslije devet voz stiže u Mostar. Žena im daje svoj broj telefona. „Ako vam nešto zatreba, nazovite me.“ Lejla se smije: „U Bosni nikad nisi sam na putu.“"),
        "uebersetzung": ("Lejla und ihr Bruder Emir leben in Deutschland. Diesen Sommer sind sie zum ersten Mal zusammen in Bosnien. Heute fahren sie mit dem Zug von Sarajevo nach Mostar. Der Zug fährt um Viertel nach sieben ab, und die Fahrt dauert etwa zwei Stunden.\n\n"
                         "Lejla sitzt am Fenster. Ihnen gegenüber sitzt eine ältere Frau mit einer großen Tasche. „Wohin fahrt ihr, Kinder?“, fragt sie. „Nach Mostar, zum ersten Mal“, antwortet Emir. „Dann müsst ihr die Alte Brücke sehen. Und wenn ihr in der Stadt seid, probiert auch Ćevapi!“\n\n"
                         "Bald kommt der Schaffner. „Fahrkarten, bitte.“ Emir zeigt ihm die Fahrkarten. „Alles in Ordnung. Gute Reise!“\n\n"
                         "Nach Konjic führt die Bahnstrecke an der Neretva entlang. Der Fluss ist grün, und die Berge sind hoch und steil. Lejla fotografiert ständig mit dem Handy. „Schau mal, Emir! Das ist schöner als auf den Bildern.“\n\n"
                         "Die Frau öffnet die Tasche und holt eine Pita heraus. „Nehmt, ich habe sie selbst gebacken.“ Emir sagt, dass sie keinen Hunger haben, aber die Frau gibt nicht auf: „Na los, seid nicht schüchtern!“ Am Ende essen sie die Pita und reden über Mostar.\n\n"
                         "Kurz nach neun kommt der Zug in Mostar an. Die Frau gibt ihnen ihre Telefonnummer. „Wenn ihr etwas braucht, ruft mich an.“ Lejla lacht: „In Bosnien ist man unterwegs nie allein.“"),
        # "sama sam je pekla": je ist hier "sie", die Pita (Prüfbericht 1.4, B10)
        "vokabeln": {"sam": "bin / allein (m)", "je": "ist / sie (Akk.)"},
        "fragen": [
            {"frage": "Wie lange dauert die Fahrt?", "optionen": ["etwa zwei Stunden", "etwa vier Stunden", "eine halbe Stunde"], "richtig": "etwa zwei Stunden"},
            {"frage": "Was muss man in Mostar unbedingt sehen?", "optionen": ["die Alte Brücke", "die Baščaršija", "den Bahnhof"], "richtig": "die Alte Brücke"},
            {"frage": "Warum gibt die Frau ihnen ihre Nummer?", "optionen": ["damit sie anrufen, wenn sie etwas brauchen", "weil sie ihre Fahrkarten verloren haben", "weil sie ihnen Pita verkaufen will"], "richtig": "damit sie anrufen, wenn sie etwas brauchen"},
        ],
    },
    {
        "id": "b1_rafting", "titel": "Rafting na Uni", "stufe": "B1", "passt_zu": "sport",
        "text": ("Emir i njegovi prijatelji su u julu otišli u Bihać. Već dugo su htjeli probati rafting na Uni. Una je jedna od najljepših rijeka u Bosni: voda je čista i zelena, a na nekim mjestima jako brza.\n\n"
                 "Ujutro su došli u kamp pored rijeke. Instruktor Mirza im je dao kacige, prsluke i vesla. „Slušajte me pažljivo“, rekao je. „Kad kažem ‚naprijed‘, veslajte svi zajedno. Kad kažem ‚stop‘, prestanite. Ako neko padne u vodu, ostanite mirni. Prsluk će vas držati.“\n\n"
                 "Prvi sat je bio lagan. Čamac je mirno plovio, a oni su gledali ptice i drveće na obali. Onda je voda postala brža i glasnija. Pred njima je bio slap. „Naprijed! Jače!“ vikao je Mirza. Čamac je skočio preko slapa, a Emir je pao u vodu. Voda je bila hladna kao led, ali prsluk ga je držao. Prijatelji su ga brzo izvukli.\n\n"
                 "„Jesi li dobro?“ pitao je Mirza. „Jesam“, odgovorio je Emir, mokar do kože. „Ali sad sam stvarno budan!“ Svi su se smijali.\n\n"
                 "Poslije raftinga su na obali jeli pastrmku. „Sljedeće godine opet dolazimo“, rekao je Emir."),
        "uebersetzung": ("Emir und seine Freunde sind im Juli nach Bihać gefahren. Sie wollten schon lange einmal Rafting auf der Una ausprobieren. Die Una ist einer der schönsten Flüsse in Bosnien: Das Wasser ist sauber und grün und an manchen Stellen sehr schnell.\n\n"
                         "Am Morgen kamen sie in ein Camp am Fluss. Der Guide Mirza gab ihnen Helme, Schwimmwesten und Paddel. „Hört mir gut zu“, sagte er. „Wenn ich ‚vorwärts‘ sage, paddelt alle zusammen. Wenn ich ‚Stopp‘ sage, hört auf. Wenn jemand ins Wasser fällt, bleibt ruhig. Die Weste hält euch über Wasser.“\n\n"
                         "Die erste Stunde war leicht. Das Boot glitt ruhig dahin, und sie schauten sich die Vögel und die Bäume am Ufer an. Dann wurde das Wasser schneller und lauter. Vor ihnen lag ein Wasserfall. „Vorwärts! Stärker!“, rief Mirza. Das Boot sprang über den Wasserfall, und Emir fiel ins Wasser. Das Wasser war eiskalt, aber die Weste hielt ihn. Seine Freunde zogen ihn schnell wieder heraus.\n\n"
                         "„Alles in Ordnung?“, fragte Mirza. „Ja“, antwortete Emir, nass bis auf die Haut. „Aber jetzt bin ich wirklich wach!“ Alle lachten.\n\n"
                         "Nach dem Rafting aßen sie am Ufer Forelle. „Nächstes Jahr kommen wir wieder“, sagte Emir."),
        "fragen": [
            {"frage": "Wo machen sie Rafting?", "optionen": ["auf der Una", "auf der Neretva", "auf der Drina"], "richtig": "auf der Una"},
            {"frage": "Was passiert am Wasserfall?", "optionen": ["Emir fällt ins Wasser", "das Boot geht kaputt", "Mirza fällt ins Wasser"], "richtig": "Emir fällt ins Wasser"},
            {"frage": "Was essen sie nach dem Rafting?", "optionen": ["Forelle", "Ćevapi mit Zwiebeln", "Burek"], "richtig": "Forelle"},
        ],
    },
    {
        "id": "b1_jahorina", "titel": "Jahorina", "stufe": "B1", "passt_zu": "sport",
        # A/B-Liste, Ajdin 15.11.2026: L16 B "skijaške cipele" statt "pancerice".
        # L17 A: "Prvog jutra" und "Trećeg dana" bleiben.
        "text": ("Amina i Ajdin su za Novu godinu otišli na Jahorinu. Amina je dobra skijašica, ali Ajdin nikad nije skijao. „Naučit ću za jedan dan“, rekao je samouvjereno.\n\n"
                 "Prvog jutra su iznajmili skije, skijaške cipele i štapove. Ajdin je obukao debelu jaknu, kapu i rukavice jer je vani bilo minus osam. Snijega je bilo skoro metar.\n\n"
                 "Amina je otišla na veliku stazu, a Ajdin u školu skijanja. Njegova instruktorica je bila mlada djevojka s mnogo strpljenja. „Polako, malo savijte koljena i gledajte naprijed“, govorila je. Ajdin je do podne pao pet puta. Djeca od šest godina su ga lako prestizala.\n\n"
                 "Popodne je bilo bolje. Spustio se niz malu stazu bez ijednog pada i bio je ponosan kao dijete. Navečer su sjedili u kafiću pored kamina i pili čaj s medom. Vani je opet padao snijeg. „Sve me boli“, rekao je Ajdin, „ali sutra idem opet.“\n\n"
                 "Trećeg dana su se zajedno spustili do hotela. Amina je bila brža, ali Ajdin se nije žalio. „Sljedeće zime ja ću tebe čekati dolje“, smijao se."),
        "uebersetzung": ("Amina und Ajdin sind zu Neujahr auf die Jahorina gefahren. Amina ist eine gute Skifahrerin, aber Ajdin ist noch nie Ski gefahren. „Ich lerne das an einem Tag“, sagte er selbstsicher.\n\n"
                         "Am ersten Morgen liehen sie Skier, Skischuhe und Stöcke aus. Ajdin zog eine dicke Jacke, eine Mütze und Handschuhe an, denn draußen waren es minus acht Grad. Der Schnee lag fast einen Meter hoch.\n\n"
                         "Amina fuhr auf die große Piste und Ajdin in die Skischule. Seine Skilehrerin war eine junge Frau mit viel Geduld. „Langsam, die Knie leicht beugen und nach vorne schauen“, sagte sie immer wieder. Bis Mittag ist Ajdin fünfmal hingefallen. Sechsjährige Kinder überholten ihn mühelos.\n\n"
                         "Am Nachmittag ging es besser. Er fuhr ohne einen einzigen Sturz eine kleine Piste hinunter und war stolz wie ein Kind. Abends saßen sie in einem Café am Kamin und tranken Tee mit Honig. Draußen schneite es wieder. „Mir tut alles weh“, sagte Ajdin, „aber morgen gehe ich wieder.“\n\n"
                         "Am dritten Tag fuhren sie zusammen bis zum Hotel hinunter. Amina war schneller, aber Ajdin beschwerte sich nicht. „Nächsten Winter warte ich unten auf dich“, lachte er."),
        "fragen": [
            {"frage": "Wer kann schon gut Ski fahren?", "optionen": ["Amina", "Ajdin", "beide"], "richtig": "Amina"},
            {"frage": "Wie oft ist Ajdin bis Mittag hingefallen?", "optionen": ["fünfmal", "zweimal", "kein einziges Mal"], "richtig": "fünfmal"},
            {"frage": "Was haben sie abends getrunken?", "optionen": ["Tee mit Honig", "Kaffee", "heiße Schokolade"], "richtig": "Tee mit Honig"},
        ],
    },
    {
        "id": "b1_pita", "titel": "Nanina pita", "stufe": "B1", "passt_zu": "bosnisch_essen",
        # A/B-Liste, Ajdin 15.11.2026: L18 B "razvijala ga oklagijom" statt "razvlačila
        # ga rukama", L19 B "nadjev" statt "fil" (beide Stellen), L21 B "trebalo da
        # odmori" statt "moralo odmarati". L17 A ("Jednog jutra") und L20 A ("savile")
        # bleiben.
        "text": ("Lejla studira u Beču, ali je za praznike došla kući. Jednog jutra je rekla nani: „Nano, nauči me da pravim pitu. U Beču niko ne zna napraviti pravu pitu.“\n\n"
                 "Nana se nasmijala. „Dobro, ali moraš biti strpljiva. Pita se ne pravi na brzinu.“\n\n"
                 "Prvo su zamijesile tijesto od brašna, vode, soli i malo ulja. Tijesto je trebalo da odmori pola sata. U međuvremenu su pripremile nadjev: oguljile su krompir, isjekle ga na male kocke i dodale luk, so i biber.\n\n"
                 "Onda je došao najteži dio. Nana je stavila tijesto na veliki sto i razvijala ga oklagijom dok nije postalo tanko kao papir. Kad je Lejla probala, tijesto se odmah poderalo. „Ne brini“, rekla je nana. „I meni se to dešavalo kad sam bila mlada.“\n\n"
                 "Na kraju su stavile nadjev na tijesto, savile ga i stavile pitu u tepsiju. Pekla se skoro sat vremena, a cijela kuća je mirisala.\n\n"
                 "Kad je dedo probao pitu, rekao je: „Ovu je pravila Lejla, zar ne? Malo je drugačija, ali je odlična.“ Lejla je bila sretna. Sada zna naninu tajnu: puno ljubavi i puno vremena."),
        "uebersetzung": ("Lejla studiert in Wien, aber in den Ferien ist sie nach Hause gekommen. Eines Morgens sagte sie zu ihrer Oma: „Oma, bring mir bei, wie man Pita macht. In Wien kann niemand eine richtige Pita machen.“\n\n"
                         "Oma lachte. „Gut, aber du musst geduldig sein. Pita macht man nicht in Eile.“\n\n"
                         "Zuerst kneteten sie einen Teig aus Mehl, Wasser, Salz und ein wenig Öl. Der Teig musste eine halbe Stunde ruhen. In der Zwischenzeit bereiteten sie die Füllung vor: Sie schälten Kartoffeln, schnitten sie in kleine Würfel und gaben Zwiebeln, Salz und Pfeffer dazu.\n\n"
                         "Dann kam der schwierigste Teil. Oma legte den Teig auf den großen Tisch und rollte ihn mit dem Nudelholz aus, bis er dünn wie Papier war. Als Lejla es versuchte, riss der Teig sofort. „Keine Sorge“, sagte Oma. „Das ist mir auch passiert, als ich jung war.“\n\n"
                         "Zum Schluss legten sie die Füllung auf den Teig, rollten ihn auf und legten die Pita auf das Backblech. Sie backte fast eine Stunde, und das ganze Haus duftete.\n\n"
                         "Als Opa die Pita probierte, sagte er: „Die hat Lejla gemacht, nicht wahr? Sie ist ein bisschen anders, aber ausgezeichnet.“ Lejla war glücklich. Jetzt kennt sie Omas Geheimnis: viel Liebe und viel Zeit."),
        # "Tijesto je trebalo da odmori": trebalo heißt hier "musste"; im WOERTERBUCH
        # steht "gebraucht (s)" aus b1_posao ("Trebalo mu je tri sata").
        "vokabeln": {"pita": "Pita (Gericht)", "trebalo": "musste (s)"},
        "fragen": [
            {"frage": "Wo studiert Lejla?", "optionen": ["in Wien", "in Sarajevo", "in Berlin"], "richtig": "in Wien"},
            {"frage": "Was kommt in die Füllung?", "optionen": ["Kartoffeln, Zwiebeln, Salz und Pfeffer", "Fleisch und Zwiebeln", "Käse und Spinat"], "richtig": "Kartoffeln, Zwiebeln, Salz und Pfeffer"},
            {"frage": "Was sagt der Opa über die Pita?", "optionen": ["sie ist anders, aber ausgezeichnet", "sie ist zu salzig", "sie ist genau wie Omas Pita"], "richtig": "sie ist anders, aber ausgezeichnet"},
        ],
    },
    {
        "id": "b1_struja", "titel": "Komšiluk bez struje", "stufe": "B1", "passt_zu": "miteinander_umgehen",
        # A/B-Liste, Ajdin 15.11.2026: L22 B "Bilo je hladno januarsko veče" (veče
        # sächlich) statt "Bila je hladna januarska večer".
        # "plinski šporet" statt "plinski štednjak" (Prüfbericht 1.4, V13 a; Ajdin, F9 a,
        # 14.11.2026): Der Herd heißt in der App šporet, štednjak steht als kroatisch.
        "text": ("Bilo je hladno januarsko veče. Merima je baš kuhala večeru kad je odjednom nestalo struje. Cijela zgrada je bila u mraku, a njen sin Kenan se uplašio i počeo plakati.\n\n"
                 "Merima je upalila svjetlo na telefonu i našla svijeće u ladici. Onda je neko pokucao na vrata. Bio je to komšija Hasan s trećeg sprata. „Komšinice, je li i kod Vas nestalo struje?“ „Jeste. Znate li šta se desilo?“ „Zvao sam. Kažu da je kvar u cijelom naselju i da će ga popraviti za dva-tri sata.“\n\n"
                 "Hasan je imao plinski šporet, pa je pozvao komšije na čaj. Uskoro je u njegovom stanu bilo desetak ljudi. Komšinica Zehra je donijela kolače, a mladi bračni par s prvog sprata donio je gitaru. Djeca su se igrala u hodniku, a odrasli su pričali, pjevali i smijali se.\n\n"
                 "„Pet godina živimo u ovoj zgradi, a nikad nismo ovako sjedili zajedno“, rekla je Merima.\n\n"
                 "Oko deset sati struja se vratila. Svjetla su se upalila, a svi su malo razočarano zapljeskali. „Šteta“, rekao je Hasan. „Bilo je lijepo bez struje.“ Od te večeri komšije se mnogo češće druže."),
        "uebersetzung": ("Es war ein kalter Januarabend. Merima kochte gerade das Abendessen, als plötzlich der Strom ausfiel. Das ganze Haus war dunkel, und ihr Sohn Kenan erschrak und fing an zu weinen.\n\n"
                         "Merima schaltete das Licht am Handy ein und fand Kerzen in der Schublade. Dann klopfte jemand an die Tür. Es war der Nachbar Hasan aus dem dritten Stock. „Nachbarin, ist bei Ihnen auch der Strom weg?“ „Ja. Wissen Sie, was passiert ist?“ „Ich habe angerufen. Sie sagen, es gibt einen Defekt im ganzen Viertel und sie reparieren ihn in zwei, drei Stunden.“\n\n"
                         "Hasan hatte einen Gasherd, also lud er die Nachbarn zum Tee ein. Bald waren etwa zehn Leute in seiner Wohnung. Die Nachbarin Zehra brachte Kuchen mit, und das junge Ehepaar aus dem ersten Stock brachte eine Gitarre. Die Kinder spielten im Flur, und die Erwachsenen redeten, sangen und lachten.\n\n"
                         "„Wir wohnen seit fünf Jahren in diesem Haus, und noch nie haben wir so zusammengesessen“, sagte Merima.\n\n"
                         "Gegen zehn Uhr kam der Strom zurück. Die Lichter gingen an, und alle klatschten ein bisschen enttäuscht. „Schade“, sagte Hasan. „Ohne Strom war es schön.“ Seit diesem Abend treffen sich die Nachbarn viel öfter."),
        "vokabeln": {"te": "dieser (Gen. w)"},
        "fragen": [
            {"frage": "Warum war es im Haus dunkel?", "optionen": ["der Strom war ausgefallen", "es war Nacht", "alle schliefen"], "richtig": "der Strom war ausgefallen"},
            {"frage": "Warum konnte Hasan Tee kochen?", "optionen": ["er hatte einen Gasherd", "er hatte viele Kerzen", "er hatte einen Generator"], "richtig": "er hatte einen Gasherd"},
            {"frage": "Was ist seit diesem Abend anders?", "optionen": ["die Nachbarn treffen sich öfter", "Merima ist umgezogen", "der Strom fällt jede Woche aus"], "richtig": "die Nachbarn treffen sich öfter"},
        ],
    },
    {
        "id": "b1_svadba", "titel": "Svadba i kolo", "stufe": "B1", "passt_zu": "feiern",
        # A/B-Liste, Ajdin 15.11.2026: L24 B, Kolo heißt "plesati", an allen vier
        # Stellen ("ja alle"). L25 A: "djevojka" bleibt.
        "text": ("Prošle subote se oženio moj brat Adnan. Njegova djevojka Sara je iz Tuzle, pa je svadba bila tamo, u jednom velikom restoranu. Došlo je skoro dvjesto gostiju: rodbina, prijatelji, komšije, pa čak i Adnanov šef.\n\n"
                 "Ujutro smo autima otišli po mladu i cijelim putem trubili. Kad je Sara izašla iz kuće u bijeloj vjenčanici, svi su zapljeskali, a moja mama je odmah počela plakati od sreće.\n\n"
                 "U restoranu je svirao bend. Prvo su mladenci plesali sami, a onda su svi ustali i uhvatili se za ruke. Plesali smo kolo oko cijele sale, od najmlađih do najstarijih. Moja nana je, sa svojih osamdeset godina, plesala duže od mene.\n\n"
                 "Hrane je bilo mnogo: supa, sarma, pečenje, salate i na kraju velika torta. Toliko sam se najela da više nisam mogla plesati.\n\n"
                 "Oko ponoći su mladenci rezali tortu. Adnan je održao kratak govor i zahvalio se roditeljima. Onda je pogledao Saru i rekao: „Od danas smo nova porodica.“\n\n"
                 "Plesali smo i pjevali do tri ujutro. Sutradan sam bila umorna, ali sretna."),
        "uebersetzung": ("Letzten Samstag hat mein Bruder Adnan geheiratet. Seine Freundin Sara kommt aus Tuzla, deshalb war die Hochzeit dort, in einem großen Restaurant. Es kamen fast zweihundert Gäste: Verwandte, Freunde, Nachbarn und sogar Adnans Chef.\n\n"
                         "Am Morgen fuhren wir mit den Autos los, um die Braut abzuholen, und hupten den ganzen Weg. Als Sara im weißen Brautkleid aus dem Haus kam, klatschten alle, und meine Mama fing sofort an, vor Glück zu weinen.\n\n"
                         "Im Restaurant spielte eine Band. Zuerst tanzte das Brautpaar allein, und dann standen alle auf und fassten sich an den Händen. Wir tanzten Kolo durch den ganzen Saal, von den Jüngsten bis zu den Ältesten. Meine Oma tanzte mit ihren achtzig Jahren länger als ich.\n\n"
                         "Es gab viel zu essen: Suppe, Sarma, Braten, Salate und zum Schluss eine große Torte. Ich habe so viel gegessen, dass ich nicht mehr tanzen konnte.\n\n"
                         "Gegen Mitternacht schnitt das Brautpaar die Torte an. Adnan hielt eine kurze Rede und bedankte sich bei den Eltern. Dann sah er Sara an und sagte: „Ab heute sind wir eine neue Familie.“\n\n"
                         "Wir tanzten und sangen bis drei Uhr morgens. Am nächsten Tag war ich müde, aber glücklich."),
        "vokabeln": {"mogla": "konnte / könnte (w)"},
        "fragen": [
            {"frage": "Woher kommt Sara?", "optionen": ["aus Tuzla", "aus Sarajevo", "aus Mostar"], "richtig": "aus Tuzla"},
            {"frage": "Wer hat länger getanzt als die Erzählerin?", "optionen": ["die Oma", "Adnans Chef", "die Mama"], "richtig": "die Oma"},
            {"frage": "Was sagte Adnan am Ende seiner Rede?", "optionen": ["dass sie jetzt eine neue Familie sind", "dass er müde ist", "dass die Torte gut ist"], "richtig": "dass sie jetzt eine neue Familie sind"},
        ],
    },
    {
        "id": "b1_posao", "titel": "Prvi dan na poslu", "stufe": "B1", "passt_zu": "arbeitsplatz",
        # A/B-Liste, Ajdin 15.11.2026: L26 B "elektrotehnički fakultet" statt
        # "elektrotehniku", L27 B "Kolege su bili ljubazni" (auch Männer wie Nedžad),
        # L28 B "kahva je obavezna" statt "svetinja".
        "text": ("Haris je završio elektrotehnički fakultet i u ponedjeljak je počeo raditi u jednoj firmi u Zenici. Noć prije nije mogao spavati. Ustao je u šest, obukao novu košulju i dva puta provjerio je li ponio sve dokumente.\n\n"
                 "Na poslu ga je dočekala šefica, gospođa Mujić. „Dobro jutro, Harise, dobro došli! Prvo ću Vam pokazati Vašu kancelariju, a onda ćete upoznati kolege.“\n\n"
                 "Kolege su bili ljubazni. Najstariji među njima, Nedžad, radi u firmi već dvadeset godina. „Ako ti bilo šta treba, pitaj mene“, rekao je. „I nemoj se stidjeti. Svi smo nekad bili novi.“\n\n"
                 "Prije podne je Haris čitao pravila firme. U deset sati svi su otišli na pauzu, ali Haris nije znao da se u firmi kahva pije zajedno, pa je ostao za stolom. Nedžad se vratio po njega: „Hajde, kahva je obavezna!“\n\n"
                 "Poslije pauze je dobio prvi zadatak: morao je popraviti jedan stari aparat. Trebalo mu je tri sata, ali je uspio. Šefica je bila zadovoljna. „Odlično za prvi dan“, rekla je.\n\n"
                 "Navečer ga je nazvala mama. „Kako je bilo?“ „Umoran sam, ali mislim da će mi se ovdje svidjeti.“"),
        "uebersetzung": ("Haris hat sein Studium der Elektrotechnik abgeschlossen und am Montag angefangen, bei einer Firma in Zenica zu arbeiten. In der Nacht davor konnte er nicht schlafen. Er stand um sechs auf, zog ein neues Hemd an und prüfte zweimal, ob er alle Unterlagen dabeihatte.\n\n"
                         "Bei der Arbeit empfing ihn die Chefin, Frau Mujić. „Guten Morgen, Haris, herzlich willkommen! Zuerst zeige ich Ihnen Ihr Büro, und dann lernen Sie die Kollegen kennen.“\n\n"
                         "Die Kollegen waren freundlich. Der Älteste von ihnen, Nedžad, arbeitet schon seit zwanzig Jahren in der Firma. „Wenn du irgendetwas brauchst, frag mich“, sagte er. „Und sei nicht schüchtern. Wir waren alle mal neu.“\n\n"
                         "Am Vormittag las Haris die Regeln der Firma. Um zehn Uhr gingen alle in die Pause, aber Haris wusste nicht, dass man in der Firma den Kaffee zusammen trinkt, und blieb am Tisch sitzen. Nedžad kam zurück, um ihn zu holen: „Komm, der Kaffee ist Pflicht!“\n\n"
                         "Nach der Pause bekam er seine erste Aufgabe: Er musste ein altes Gerät reparieren. Er brauchte drei Stunden, aber er schaffte es. Die Chefin war zufrieden. „Ausgezeichnet für den ersten Tag“, sagte sie.\n\n"
                         "Abends rief ihn seine Mama an. „Wie war es?“ „Ich bin müde, aber ich glaube, es wird mir hier gefallen.“"),
        "vokabeln": {"bilo": "war (s) / bilo šta: irgendetwas"},
        "fragen": [
            {"frage": "In welcher Stadt arbeitet Haris?", "optionen": ["in Zenica", "in Sarajevo", "in Tuzla"], "richtig": "in Zenica"},
            {"frage": "Warum blieb Haris in der Pause am Tisch?", "optionen": ["er wusste nicht, dass man zusammen Kaffee trinkt", "er trinkt keinen Kaffee", "er hatte zu viel Arbeit"], "richtig": "er wusste nicht, dass man zusammen Kaffee trinkt"},
            {"frage": "Wie lange brauchte er für die erste Aufgabe?", "optionen": ["drei Stunden", "eine Stunde", "den ganzen Tag"], "richtig": "drei Stunden"},
        ],
    },
    {
        "id": "b1_stan", "titel": "Izdajem stan", "stufe": "B1", "passt_zu": "immobilien",
        # A/B-Liste, Ajdin 15.11.2026: L30 B "na madracu" statt "na dušeku". L29 A:
        # "jednosoban stan" bleibt.
        "text": ("Selma je dobila posao u Sarajevu i traži stan. Na internetu je našla ovaj oglas:\n\n"
                 "„Izdajem jednosoban stan na Grbavici. Četrdeset kvadrata, treći sprat, ima lift. Stan je namješten, renoviran i ima balkon. U blizini su tramvaj, škola i prodavnica. Kirija je petsto maraka mjesečno plus režije. Kućni ljubimci nisu dozvoljeni. Zvati poslije pet sati.“\n\n"
                 "Selma je nazvala u pola šest.\n"
                 "„Dobar dan, zovem zbog oglasa. Je li stan još slobodan?“\n"
                 "„Jeste, slobodan je od prvog marta.“\n"
                 "„Koliko su otprilike režije?“\n"
                 "„Zimi oko stotinu maraka, ljeti manje. Grijanje je centralno.“\n"
                 "„Je li zgrada mirna? Dva dana sedmično radim od kuće.“\n"
                 "„Vrlo je mirna. Komšije su uglavnom stariji ljudi.“\n"
                 "„Odlično. Kada bih mogla pogledati stan?“\n"
                 "„Može sutra u šest ako Vam odgovara.“\n"
                 "„Odgovara mi. Hvala Vam, vidimo se sutra!“\n\n"
                 "Sutradan je Selma pogledala stan. Bio je mali, ali svijetao i čist, a s balkona se vidio Trebević. Odmah je potpisala ugovor. Prvu noć je spavala na madracu na podu, ali je bila presretna."),
        "uebersetzung": ("Selma hat eine Stelle in Sarajevo bekommen und sucht eine Wohnung. Im Internet hat sie diese Anzeige gefunden:\n\n"
                         "„Vermiete Einzimmerwohnung in Grbavica. Vierzig Quadratmeter, dritter Stock, mit Aufzug. Die Wohnung ist möbliert, renoviert und hat einen Balkon. In der Nähe: Straßenbahn, Schule und Laden. Miete fünfhundert Mark im Monat plus Nebenkosten. Haustiere nicht erlaubt. Anrufe nach 17 Uhr.“\n\n"
                         "Selma rief um halb sechs an.\n"
                         "„Guten Tag, ich rufe wegen der Anzeige an. Ist die Wohnung noch frei?“\n"
                         "„Ja, sie ist ab dem ersten März frei.“\n"
                         "„Wie hoch sind ungefähr die Nebenkosten?“\n"
                         "„Im Winter etwa hundert Mark, im Sommer weniger. Es gibt Zentralheizung.“\n"
                         "„Ist das Haus ruhig? Ich arbeite zwei Tage pro Woche von zu Hause.“\n"
                         "„Sehr ruhig. Die Nachbarn sind meist ältere Leute.“\n"
                         "„Sehr gut. Wann könnte ich mir die Wohnung ansehen?“\n"
                         "„Morgen um sechs, wenn es Ihnen passt.“\n"
                         "„Das passt mir. Vielen Dank, bis morgen!“\n\n"
                         "Am nächsten Tag sah Selma sich die Wohnung an. Sie war klein, aber hell und sauber, und vom Balkon aus sah man den Trebević. Sie unterschrieb sofort den Vertrag. Die erste Nacht schlief sie auf einer Matratze auf dem Boden, aber sie war überglücklich."),
        "vokabeln": {"odgovara": "passt / antwortet"},
        "fragen": [
            {"frage": "Wie hoch ist die Miete?", "optionen": ["500 Mark im Monat", "100 Mark im Monat", "1.000 Mark im Monat"], "richtig": "500 Mark im Monat"},
            {"frage": "Warum fragt Selma, ob das Haus ruhig ist?", "optionen": ["sie arbeitet zwei Tage pro Woche von zu Hause", "sie hat ein Baby", "sie schläft tagsüber"], "richtig": "sie arbeitet zwei Tage pro Woche von zu Hause"},
            {"frage": "Was sieht man vom Balkon aus?", "optionen": ["den Trebević", "die Miljacka", "die Baščaršija"], "richtig": "den Trebević"},
        ],
    },
    {
        "id": "b1_telefon", "titel": "Izgubljeni telefon", "stufe": "B1", "passt_zu": "geraete",
        "text": ("U petak poslije posla Amina je sjela u kafić na Baščaršiji, blizu Sebilja. Popila je kahvu, platila i otišla kući tramvajem. Kod kuće je htjela nazvati mamu, ali telefona nije bilo u torbi. Tražila ga je svugdje: u jakni, u kuhinji, čak i ispod kreveta. Ništa.\n\n"
                 "„Ajdine, nazovi me, molim te!“ Ajdin je nazvao njen broj. Telefon je zvonio, ali niko se nije javio. Amina je bila nervozna. U telefonu su bili svi njeni brojevi i slike.\n\n"
                 "Onda je s Ajdinovog telefona napisala poruku na svoj broj: „Dobro veče! Izgubila sam ovaj telefon danas oko pet sati, negdje na Baščaršiji. Ako ste ga našli, molim Vas, javite se. Hvala!“\n\n"
                 "Sat kasnije zazvonio je Ajdinov telefon. Javio se konobar koji radi u tom kafiću. „Vaš telefon je bio ispod stola. Našao sam ga kad sam čistio. Možete doći sutra ujutro, sačuvat ću ga.“\n\n"
                 "Amina je odahnula. Sutradan je rano otišla u kafić. Konobar joj je dao telefon i rekao: „Sve je tu, ništa nisam dirao.“ Amina mu je htjela dati deset maraka, ali on nije htio uzeti novac. „Bilo bi mi drago da opet dođete na kahvu“, rekao je.\n\n"
                 "Od tada Amina svake sedmice pije kahvu baš u tom kafiću."),
        "uebersetzung": ("Am Freitag nach der Arbeit setzte sich Amina in ein Café auf der Baščaršija, in der Nähe des Sebilj. Sie trank einen Kaffee, bezahlte und fuhr mit der Straßenbahn nach Hause. Zu Hause wollte sie ihre Mama anrufen, aber das Handy war nicht in der Tasche. Sie suchte es überall: in der Jacke, in der Küche, sogar unter dem Bett. Nichts.\n\n"
                         "„Ajdin, ruf mich bitte an!“ Ajdin rief ihre Nummer an. Das Handy klingelte, aber niemand ging ran. Amina war nervös. Im Handy waren alle ihre Nummern und Bilder.\n\n"
                         "Dann schrieb sie von Ajdins Handy eine Nachricht an ihre eigene Nummer: „Guten Abend! Ich habe dieses Handy heute gegen fünf Uhr verloren, irgendwo auf der Baščaršija. Wenn Sie es gefunden haben, melden Sie sich bitte. Danke!“\n\n"
                         "Eine Stunde später klingelte Ajdins Handy. Es meldete sich ein Kellner, der in diesem Café arbeitet. „Ihr Handy lag unter dem Tisch. Ich habe es beim Putzen gefunden. Sie können morgen früh kommen, ich bewahre es so lange auf.“\n\n"
                         "Amina atmete auf. Am nächsten Tag ging sie früh ins Café. Der Kellner gab ihr das Handy und sagte: „Es ist alles da, ich habe nichts angefasst.“ Amina wollte ihm zehn Mark geben, aber er wollte das Geld nicht nehmen. „Es würde mich freuen, wenn Sie wieder auf einen Kaffee kommen“, sagte er.\n\n"
                         "Seitdem trinkt Amina jede Woche ihren Kaffee genau in diesem Café."),
        "vokabeln": {"koji": "der / welcher (Relativsatz)"},
        "fragen": [
            {"frage": "Wo hat Amina das Handy verloren?", "optionen": ["in einem Café", "in der Straßenbahn", "zu Hause"], "richtig": "in einem Café"},
            {"frage": "Wer hat das Handy gefunden?", "optionen": ["ein Kellner", "Ajdin", "eine Nachbarin"], "richtig": "ein Kellner"},
            {"frage": "Was wollte der Kellner statt Geld?", "optionen": ["dass sie wieder auf einen Kaffee kommt", "zehn Mark", "ein neues Handy"], "richtig": "dass sie wieder auf einen Kaffee kommt"},
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
# noch fehlen. Jede Form steht genau einmal: 159 Formen kommen auch in Paket 1
# und 2 vor und stehen deshalb nur oben, mit einer Bedeutung, die in allen
# Texten passt (Merge vom 13.11.2026). tests/test_inhalt.py prüft das.
# Die Aufnahmen fehlen noch (ton_bauen.py, dann wortzeiten_holen.py), siehe
# WARTET_AUF_TON in tests/test_wortzeiten.py.
#
# HINWEIS: Claude ist kein Muttersprachler. Texte bitte prüfen.
# ---------------------------------------------------------------------------
WOERTERBUCH_B1_2 = {
    # b1_doktor
    "amar": "Amar (Name)", "osjeća": "er/sie fühlt sich",
    "grlo": "Hals (innen) / Kehle", "temperaturu": "Fieber (Akk.)",
    "dom": "Heim (dom zdravlja: Gesundheitszentrum)",
    "zdravlja": "Gesundheit (Gen.)", "zakazao": "vereinbart (m)", "termin": "Termin", "doktorice": "Ärztin (Gen.)",
    "čekaonici": "Wartezimmer (Lok.)", "amara": "Amar (Gen.)", "sjedio": "gesessen (m)",
    "čovjek": "Mensch", "kašljao": "gehustet (m)",
    "bolesni": "krank (Mehrz.)",
    "red": "Reihe (doći na red: drankommen)", "doktorica": "Ärztin",
    "pitala": "gefragt (w)", "objasnio": "erklärt (m)", "pregledala": "untersucht (w)",
    "izmjerila": "gemessen (w)", "imate": "ihr habt / Sie haben", "upalu": "Entzündung (Akk.)", "grla": "Hals (Gen.)",
    "ozbiljno": "ernst",
    "dat": "geben (Zukunft)", "recept": "Rezept",
    "otvorit": "öffnen (otvorit ću bolovanje: ich schreibe krank)", "bolovanje": "Krankschreibung (Akk.)",
    "apoteci": "Apotheke (Lok.)",
    "apotekar": "Apotheker", "lijek": "Medikament",
    "pijte": "trinken Sie (Befehl)", "uzimajte": "nehmen Sie (Befehl)", "tabletu": "Tablette (Akk.)", "dnevno": "täglich",
    "čaja": "Tee (Gen.)",
    "doktora": "Arzt (Gen.)",
    "strašno": "furchtbar", "zdrav": "gesund (m)", "ponovo": "wieder / erneut",
    # b1_selidba, seit 14.11.2026 "Dedo i nana se sele" statt "Selidba" (Offen-
    # Liste, Punkt 3). Von den Formen der alten Geschichte stehen hier nur noch
    # die, die ein Text braucht (nosili, stigli, umorni in b1_utakmica, spratu
    # in b1_kahva, samo in mehreren); die übrigen 31 kamen in keinem Text mehr
    # vor. radio ("funktioniert") ist auch raus: in der neuen Geschichte ist es
    # das Gerät und steht in ihren vokabeln.
    "rasim": "Rasim (Name)", "fadila": "Fadila (Name)", "vlašića": "Vlašić (Gen., Berg über Travnik)",
    "prevelika": "zu groß (w)", "penje": "steigt (penje se: steigt hinauf)", "stepenice": "Treppe (Akk.)",
    "odlučili": "beschlossen (Mehrz.)", "presele": "umziehen (da se presele: dass sie umziehen)",
    "travnik": "Travnik (Stadt)", "kćerke": "Tochter (Gen.)", "alme": "Alma (Gen., Name)",
    "unuk": "Enkel", "edin": "Edin (Name)", "pomogne": "hilft (da pomogne: um zu helfen)",
    "ponijeti": "mitnehmen", "ormar": "Schrank", "drva": "Holz (šporet na drva: Holzherd)",
    "tegli": "Gläser (Gen. Mehrz.)", "zimnice": "Wintervorrat (Gen.)", "uzeo": "genommen (m)",
    "zapisivao": "aufgeschrieben (m)", "ostaje": "bleibt", "fotelju": "Sessel (Akk.)",
    "slušam": "ich höre", "ostali": "geblieben (Mehrz.)", "ključ": "Schlüssel", "dali": "gegeben (Mehrz.)",
    "komšiji": "Nachbar (Dat.)", "punom": "vollen (Lok.)", "kombiju": "Kleinbus (Lok.)",
    "kantu": "Eimer (Akk.)", "spisku": "Liste (Lok.)", "kanti": "Eimer (Lok.)",
    "šljiva": "Pflaumenbaum / Pflaume", "stvar": "Sache / Ding", "prve": "ersten (Gen., w)",
    "novom": "neuen (Lok.)", "skuhala": "gekocht (w)", "zalijevao": "gegossen (m)",
    "svoju": "seine eigene (Akk.)", "šljivu": "Pflaumenbaum (Akk.)", "napokon": "endlich",
    "koja": "die (Relativ) / welche (w)",
    "naviknut": "gewöhnen (naviknut ćemo se: wir werden uns gewöhnen)", "rasime": "Rasim! (Anrede)",
    "nosili": "getragen (Mehrz.)", "stigli": "angekommen (Mehrz.)", "spratu": "Stockwerk (Lok.)",
    "umorni": "müde (Mehrz.)", "samo": "nur",
    # b1_rodjendan
    "napuniti": "füllen (napuniti 30 godina: 30 werden)",
    "trideset": "dreißig", "lamija": "Lamija (Name)", "mjesec": "Monat",
    "tajno": "heimlich", "sprema": "er/sie bereitet vor", "iznenađenje": "Überraschung", "pozvala": "eingeladen (w)",
    "njegove": "seine (Akk. Mehrz.)", "prijatelje": "Freunde (Akk.)",
    "reći": "sagen", "harisu": "Haris (Dat.)", "srijedu": "Mittwoch (Akk.)",
    "posebno": "besonders", "tvojih": "deinen (kod tvojih: bei deinen Eltern)", "tužan": "traurig (m)",
    "mislio": "gedacht (m)", "zaboravili": "vergessen (Mehrz.)", "rođendan": "Geburtstag", "gosti": "Gäste",
    "sakrili": "versteckt (Mehrz.)", "njegovih": "seiner (Gen. Mehrz.)",
    "roditelja": "Eltern (Gen.)", "ugašeno": "ausgeschaltet (s)",
    "šutjeli": "geschwiegen (Mehrz.)", "ušli": "hereingekommen (Mehrz.)", "upalio": "eingeschaltet (m)",
    "stajao": "gestanden (m)",
    "vjerovati": "glauben", "svijeća": "Kerzen (Gen.)",
    "ih": "sie (Akk. Mehrz.)", "ugasio": "ausgemacht (m)", "vikali": "gerufen (Mehrz.)", "bravo": "bravo",
    "dala": "gegeben (w)", "koncert": "Konzert", "njegovog": "seines (Gen.)", "omiljenog": "Lieblings- (Gen.)",
    "pjevača": "Sänger (Gen.)", "mom": "meinem (Lok.)", "životu": "Leben (Lok.)",
    "svima": "allen",
    # b1_utakmica
    "fudbal": "Fußball", "kupio": "gekauft (m)", "utakmicu": "Spiel (Akk.)",
    "reprezentacije": "Nationalmannschaft (Gen.)", "bosna": "Bosnien",
    "hercegovina": "Herzegowina", "igra": "er/sie spielt", "protiv": "gegen", "islanda": "Island (Gen.)",
    "važna": "wichtig (w)", "utakmica": "Spiel (Match)", "evropsko": "Europa- / europäisch (s)",
    "prvenstvo": "Meisterschaft", "utakmice": "Spiel (Gen.)", "krenuli": "losgefahren (Mehrz.)",
    "autoputu": "Autobahn (Lok.)", "vidjeli": "gesehen (Mehrz.)", "auta": "Autos (Gen.)",
    "zastavama": "Fahnen (Instr.)", "stadiona": "Stadion (Gen.)",
    "gužva": "Gedränge / Stau", "navijači": "Fans", "plave": "blaue (Mehrz.)", "majice": "T-Shirts",
    "zmajevi": "Drachen (Spitzname der Nationalmannschaft)", "poluvrijeme": "Halbzeit", "teško": "schwierig",
    "island": "Island", "bolji": "besser", "tridesetoj": "dreißigsten (Lok.)", "minuti": "Minute (Lok.)",
    "gol": "Tor (Treffer)", "sine": "Sohn! (Anrede)", "devedeset": "neunzig",
    "drugom": "zweiten (Lok.)", "poluvremenu": "Halbzeit (Lok.)", "naši": "unsere (Mehrz.)",
    "šezdesetoj": "sechzigsten (Lok.)",
    "kraja": "Ende (Gen.)", "igrač": "Spieler", "stadion": "Stadion",
    "grlio": "umarmt (m)", "babu": "Papa (Akk.)", "ljude": "Leute (Akk.)",
    "koje": "die (Akk. Mehrz.)", "tek": "erst", "glasa": "Stimme (Gen.)",
    "pjevanja": "Singen (Gen.)",
    # b1_zanat
    "odmoru": "Urlaub (Lok.)",
    "svidjela": "gefallen (w)", "ulica": "Straße",
    "kazandžiluk": "Kazandžiluk (Gasse der Kupferschmiede)", "čuje": "hört (se čuje: man hört)",
    "kucanje": "Klopfen / Hämmern", "čekića": "Hammer (Gen.)", "malim": "kleinen (Lok. Mehrz.)",
    "radnjama": "Läden (Lok.)", "majstori": "Handwerker (Mehrz.)", "prave": "sie machen", "stvari": "Sachen / Dinge",
    "bakra": "Kupfer (Gen.)", "ušla": "hineingegangen (w)", "radnju": "Laden (Akk.)",
    "ukrašavao": "verziert (m)", "džezvu": "Kupferkännchen (Akk.)", "izvolite": "Bitte sehr (beim Überreichen)",
    "slobodno": "ruhig / frei", "pogledajte": "schauen Sie (Befehl)", "napravili": "gemacht (Mehrz.)",
    "ove": "diese (Akk. Mehrz.)", "zanat": "Handwerk", "naučio": "gelernt (m)", "oca": "Vater (Gen.)",
    "svog": "seines / eigenen (Gen.)", "majstor": "Handwerker / Fachmann",
    "pokazao": "gezeigt (m)", "džezva": "Kupferkännchen", "bakar": "Kupfer",
    "reže": "schneidet (se reže: wird geschnitten)", "kuca": "klopft / hämmert", "čekićem": "Hammer (Instr.)",
    "ukrašava": "verziert (se ukrašava: wird verziert)", "odete": "ihr geht / Sie gehen",
    "penziju": "Rente (Akk.)", "šutio": "geschwiegen (m)", "banci": "Bank (Lok.)",
    "težak": "schwer (m)", "zarađuje": "verdient (se zarađuje: man verdient)",
    "fildžana": "Kaffeetassen (Gen.)", "neka": "soll / möge",
    "srećom": "Glück (Instr.)", "nje": "ihr / sie (Gen.)",
    "polici": "Regal (Lok.)",
    # b1_kahva
    "teta": "Tante (Anrede für ältere Frauen)", "safija": "Safija (Name)", "živi": "er/sie lebt",
    "istom": "gleichen (Lok.)", "vesela": "fröhlich",
    "nedjelje": "Sonntag (Gen.)", "pokuca": "klopft",
    "svoja": "eigene (Mehrz.)", "kuha": "er/sie kocht",
    "džezvi": "Kupferkännchen (Lok.)", "skine": "nimmt herunter", "šporeta": "Herd (Gen.)", "doda": "fügt hinzu",
    "promiješa": "rührt um", "vrati": "stellt zurück", "vatru": "Feuer (Akk.)", "kratko": "kurz",
    "prekipjeti": "überkochen", "prekipi": "kocht über", "kuhaj": "koch (Befehl)",
    "stolu": "Tisch (Lok.)", "fildžani": "Kaffeetassen", "šećer": "Zucker", "rahat": "rahat lokum: Lokum (Süßigkeit)",
    "lokum": "Lokum (Süßigkeit)", "čaša": "Glas", "uzmemo": "wir nehmen", "komad": "Stück",
    "lokuma": "Lokum (Gen.)", "pijemo": "wir trinken", "e": "na / also (Ausruf)", "prava": "echt",
    "bosanska": "bosnisch (w)", "počnu": "sie fangen an", "priče": "Geschichten",
    "bebu": "Baby (Akk.)", "čiji": "wessen", "zašto": "warum",
    "mujo": "Mujo (Name)", "nikoga": "niemanden", "pozdravio": "gegrüßt (m)", "slušati": "zuhören / anhören",
    "moram": "ich muss", "popiti": "trinken / austrinken",
    "dušo": "Schatz (Anrede)", "uz": "neben / zu / mit",
    "razgovara": "unterhält sich (se razgovara: man unterhält sich)", "sjedim": "ich sitze",
    "kasnim": "Ich komme zu spät",
    # b1_mejl
    "predmet": "Betreff", "dragi": "lieber", "adnane": "Adnan! (Anrede)",
    "tetka": "Tante (Schwester von Vater oder Mutter)", "tetak": "Onkel (Mann der Tante)", "nas": "uns",
    "ovih": "dieser (Gen. Mehrz.)", "mjeseci": "Monate (Gen.)",
    "radili": "gearbeitet (Mehrz.)", "lijepu": "schöne (Akk.)", "vijest": "Neuigkeit / Nachricht",
    "avion": "Flugzeug", "slijećem": "ich lande", "desetog": "am zehnten", "augusta": "August (Gen.)",
    "možeš": "du kannst", "sačekati": "abholen / erwarten",
    "problem": "Problem", "uzet": "nehmen (Zukunft)", "taksi": "Taxi",
    "ostat": "bleiben (Zukunft)", "sedmicu": "Woche (Akk.)",
    "smeta": "es stört", "drugu": "zweite (Akk.)", "goražde": "Goražde (Stadt)", "donesem": "ich bringe (mit)",
    "njemačke": "Deutschland (Gen.)", "tetki": "Tante (Dat.)", "prošli": "vergangen / letzter (zeitlich)",
    "čokolada": "Schokolade", "lješnjacima": "Haselnüsse (Instr.)", "napiši": "schreib (Befehl)",
    "želite": "ihr möchtet / Sie möchten", "sigurno": "sicher", "primijetio": "bemerkt (m)", "pišem": "ich schreibe",
    "bosanskom": "Bosnisch (Lok.)", "mobitelu": "Handy (Lok.)", "griješim": "ich mache Fehler",
    "razgovarati": "sich unterhalten", "grešku": "Fehler (Akk.)",
    "smijati": "lachen", "jedva": "kaum", "čekam": "ich warte",
    # b1_zmaj
    "zmaj": "Drache", "nekoliko": "einige / ein paar", "uči": "er/sie lernt",
    "ponavlja": "er/sie wiederholt", "nove": "neue (Mehrz.)", "riječi": "Wörter",
    "stigao": "angekommen (m)",
    "ponosno": "stolz (Adverb)", "večere": "Abendessen (Gen.)",
    "hoćeš": "du willst", "sarme": "Sarma (Gen.)", "sit": "satt (m)", "tanjir": "Teller",
    "čula": "gehört (w)", "znači": "es bedeutet", "ukusno": "lecker",
    "roštilja": "Grill (Gen.)", "pustio": "gelassen (m)", "vatre": "Feuer (Gen.)",
    "usta": "Mund", "ćevapi": "Ćevapi", "sekundi": "Sekunde (Lok.)", "zagorjeli": "angebrannt (Mehrz.)",
    "stani": "halt (Befehl)", "zmaju": "Drache! (Anrede)", "peku": "grillen / backen (sie)",
    "zmajevom": "Drachen- (Instr.)", "vatrom": "Feuer (Instr.)", "napisao": "geschrieben (m)",
    "mami": "Mama (Dat.)",
    "pomislio": "gedacht (m)", "njena": "ihre (von ihr, w)",
    "najbolja": "die beste", "zato": "deshalb",
    "učiti": "lernen", "dalje": "weiter",
}
WOERTERBUCH.update(WOERTERBUCH_B1_2)

GESCHICHTEN += [
    {
        "id": "b1_doktor", "titel": "Kod doktora", "stufe": "B1", "passt_zu": "in_der_praxis",
        # A/B-Liste, Ajdin 15.11.2026: T1 B "i otvorit ću Vam bolovanje na pet dana"
        # (Vam groß wie überall), T2 B "Uzimajte" statt "Pijte", T3 B "ponovo" statt
        # "opet" (opet = schon wieder, ponovo = erneut).
        "text": ("Amar se već tri dana ne osjeća dobro. Boli ga grlo, ima temperaturu i stalno je umoran. U ponedjeljak ujutro nazvao je dom zdravlja i zakazao termin kod doktorice za deset sati.\n\n"
                 "U čekaonici je bilo mnogo ljudi. Pored Amara je sjedio jedan stariji čovjek koji je stalno kašljao. „I Vas boli grlo?“ pitao je čovjek. „Da, već tri dana“, odgovorio je Amar. „Sada su svi bolesni. To je od ovog vremena.“\n\n"
                 "Kad je došao na red, doktorica ga je pitala: „Šta Vas boli i od kada?“ Amar joj je sve objasnio. Ona ga je pregledala i izmjerila mu temperaturu. „Imate upalu grla. Nije ništa ozbiljno, ali morate se odmarati. Dat ću Vam recept i otvorit ću Vam bolovanje na pet dana.“\n\n"
                 "U apoteci mu je apotekar dao lijek i rekao: „Uzimajte jednu tabletu tri puta dnevno, poslije jela. I pijte mnogo čaja s medom.“\n\n"
                 "Kod kuće je Amar nazvao mamu. „Jesi li bio kod doktora?“ pitala je ona. „Jesam, mama. Nije ništa strašno.“ „Onda dobro. Čaj s medom i u krevet!“ Poslije pet dana Amar je ponovo bio zdrav i vratio se na posao."),
        "uebersetzung": ("Amar fühlt sich schon seit drei Tagen nicht gut. Sein Hals tut weh, er hat Fieber und ist ständig müde. Am Montagmorgen hat er im Gesundheitszentrum angerufen und für zehn Uhr einen Termin bei der Ärztin vereinbart.\n\n"
                         "Im Wartezimmer waren viele Leute. Neben Amar saß ein älterer Mann, der ständig hustete. „Tut Ihnen auch der Hals weh?“, fragte der Mann. „Ja, schon seit drei Tagen“, antwortete Amar. „Jetzt sind alle krank. Das kommt von diesem Wetter.“\n\n"
                         "Als er an der Reihe war, fragte ihn die Ärztin: „Was tut Ihnen weh, und seit wann?“ Amar hat ihr alles erklärt. Sie hat ihn untersucht und bei ihm Fieber gemessen. „Sie haben eine Halsentzündung. Es ist nichts Ernstes, aber Sie müssen sich ausruhen. Ich gebe Ihnen ein Rezept und schreibe Sie für fünf Tage krank.“\n\n"
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
        # Neue Geschichte statt "Selidba" (14.11.2026, Offen-Liste, Punkt 3;
        # Prüfbericht 1.4, F10): Ajdin "mach eine neue geschichte", Entwurf
        # "Dedo i nana se sele" (Release\Selidba_neu_Entwurf.md, Vorschlag 1)
        # angenommen mit "nimm penje uz stepenicama" und "nimm napokon...".
        # Die id bleibt, damit der Lesestand bleibt. Ton folgt in der
        # Vesna-Runde (tests/offen_b1_teil2.py).
        "id": "b1_selidba", "titel": "Dedo i nana se sele", "stufe": "B1", "passt_zu": "erledigen_umziehen",
        "text": ("Dedo Rasim i nana Fadila već četrdeset godina žive u kući na selu ispod Vlašića. Ali bašta im je prevelika, a nana se teško penje uz stepenice. Zato su odlučili da se presele u Travnik, u mali stan blizu kćerke Alme. Zgrada ima lift.\n\n"
                 "U subotu je došao unuk Edin da pomogne. Nana je htjela sve ponijeti: ormar, šporet na drva i trideset tegli zimnice. „Nano, stan ima dvije sobe, a ne deset!“ rekao je Edin. Uzeo je papir i zapisivao šta ide, a šta ostaje.\n\n"
                 "Dedo je htio samo dvije stvari: staru fotelju i radio. „U njoj trideset godina slušam radio. Bez nje ne idem!“ Ormar i šporet su ostali u kući, a ključ su dali komšiji.\n\n"
                 "Edin je u punom kombiju našao kantu koje nije bilo na spisku. U kanti je bila mlada šljiva iz bašte. „Dedo, rekao si samo dvije stvari!“ „Ovo nije stvar“, rekao je dedo. „Ovo je šljiva.“\n\n"
                 "Prve večeri su sjedili na novom balkonu. Nana je skuhala kahvu, a dedo je zalijevao svoju šljivu. „Napokon bašta koja nije prevelika“, rekao je. Nana se nasmijala: „Naviknut ćemo se, Rasime.“"),
        "uebersetzung": ("Opa Rasim und Oma Fadila wohnen schon seit vierzig Jahren in einem Haus auf dem Dorf unterhalb des Vlašić. Aber der Garten ist ihnen zu groß, und Oma fällt das Treppensteigen schwer. Deshalb haben sie beschlossen, nach Travnik zu ziehen, in eine kleine Wohnung in der Nähe ihrer Tochter Alma. Das Gebäude hat einen Aufzug.\n\n"
                         "Am Samstag kam ihr Enkel Edin, um zu helfen. Oma wollte alles mitnehmen: den Schrank, den Holzherd und dreißig Gläser Wintervorrat. „Oma, die Wohnung hat zwei Zimmer, nicht zehn!“, sagte Edin. Er nahm ein Blatt Papier und schrieb auf, was mitkommt und was bleibt.\n\n"
                         "Opa wollte nur zwei Dinge: den alten Sessel und das Radio. „Seit dreißig Jahren höre ich darin Radio. Ohne ihn gehe ich nicht!“ Der Schrank und der Herd blieben im Haus, und den Schlüssel gaben sie dem Nachbarn.\n\n"
                         "Im vollen Kleinbus fand Edin einen Eimer, der nicht auf der Liste stand. Im Eimer war ein junger Pflaumenbaum aus dem Garten. „Opa, du hast nur zwei Dinge gesagt!“ „Das ist kein Ding“, sagte Opa. „Das ist ein Pflaumenbaum.“\n\n"
                         "Am ersten Abend saßen sie auf dem neuen Balkon. Oma kochte Kaffee, und Opa goss seinen Pflaumenbaum. „Endlich ein Garten, der nicht zu groß ist“, sagte er. Oma lachte: „Wir werden uns daran gewöhnen, Rasim.“"),
        # radio ist hier zweimal das Gerät, sonst heißt es "funktioniert" (wie
        # odgovara in b1_stan). njoj und nje meinen den Sessel (fotelja), auf
        # Deutsch "darin" und "ohne ihn". Die übrigen meinen hier etwas anderes
        # als im WOERTERBUCH: teško "schwer" statt "schwierig", uz "hinauf",
        # staru weiblich (fotelja), koje Genitiv nach "nije bilo".
        "vokabeln": {"radio": "Radio / funktioniert (m)",
                     "njoj": "ihr (Lok.) (u njoj: darin, im Sessel)",
                     "nje": "ihr / sie (Gen.) (bez nje: ohne ihn, den Sessel)",
                     "teško": "schwer / mit Mühe",
                     "uz": "hinauf (uz stepenice: die Treppe hinauf)",
                     "staru": "alte (Akk., w)",
                     "koje": "die (Relativ, Gen. w)"},
        # Antworten etwa gleich lang (Prüfbericht 1.4, B13), keine verrät sich.
        "fragen": [
            {"frage": "Wohin ziehen Rasim und Fadila?", "optionen": ["in eine kleine Wohnung in Travnik", "in ein großes Haus in Sarajevo", "in ein anderes Dorf am Vlašić"], "richtig": "in eine kleine Wohnung in Travnik"},
            {"frage": "Welche zwei Dinge wollte der Opa mitnehmen?", "optionen": ["den alten Sessel und das Radio", "den Schrank und den Holzherd", "den großen Tisch und das Bett"], "richtig": "den alten Sessel und das Radio"},
            {"frage": "Was fand Edin im vollen Kleinbus?", "optionen": ["einen Pflaumenbaum im Eimer", "einen Eimer mit Pflaumenmus", "den Schlüssel vom alten Haus"], "richtig": "einen Pflaumenbaum im Eimer"},
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
        "text": ("Lejla je ovog ljeta na odmoru u Sarajevu. Najviše joj se svidjela jedna mala ulica na Baščaršiji. Zove se Kazandžiluk. Tu se cijeli dan čuje kucanje čekića jer u malim radnjama majstori prave stvari od bakra.\n\n"
                 "Lejla je ušla u jednu radnju. Za stolom je sjedio stariji čovjek i polako ukrašavao jednu džezvu. „Izvolite, slobodno pogledajte“, rekao je. „Jeste li Vi napravili sve ove stvari?“ pitala je Lejla. „Jesam. Ovaj zanat sam naučio od oca, a on od svog oca. Naša porodica radi u ovoj radnji više od sto godina.“\n\n"
                 "Majstor joj je pokazao kako se pravi džezva. Prvo se bakar reže, onda se dugo kuca čekićem, a na kraju se ukrašava. „Za jednu džezvu treba mi skoro cijeli dan“, objasnio je.\n\n"
                 "„A ko će raditi kad Vi odete u penziju?“ pitala je Lejla. Majstor je malo šutio. „Moj sin radi u banci. Mladi danas ne žele ovaj posao. Težak je, a ne zarađuje se mnogo.“\n\n"
                 "Lejla je kupila džezvu i šest fildžana za nanu u Njemačkoj. „Neka je sa srećom!“ rekao je majstor. „I pijte kahvu iz nje. Nemojte je samo držati na polici.“"),
        "uebersetzung": ("Lejla ist diesen Sommer im Urlaub in Sarajevo. Am besten gefiel ihr eine kleine Gasse auf der Baščaršija. Sie heißt Kazandžiluk. Hier hört man den ganzen Tag Hämmern, denn in den kleinen Läden machen Handwerker Dinge aus Kupfer.\n\n"
                         "Lejla ging in einen Laden. Am Tisch saß ein älterer Mann und verzierte langsam ein Kupferkännchen. „Bitte sehr, schauen Sie sich ruhig um“, sagte er. „Haben Sie all diese Sachen gemacht?“, fragte Lejla. „Ja. Dieses Handwerk habe ich von meinem Vater gelernt und er von seinem Vater. Unsere Familie arbeitet seit über hundert Jahren in diesem Laden.“\n\n"
                         "Der Meister zeigte ihr, wie man ein Kupferkännchen macht. Zuerst wird das Kupfer geschnitten, dann lange mit dem Hammer bearbeitet, und am Ende wird es verziert. „Für ein Kännchen brauche ich fast einen ganzen Tag“, erklärte er.\n\n"
                         "„Und wer wird hier arbeiten, wenn Sie in Rente gehen?“, fragte Lejla. Der Meister schwieg eine Weile. „Mein Sohn arbeitet bei einer Bank. Die jungen Leute wollen diese Arbeit heute nicht. Sie ist schwer, und man verdient nicht viel.“\n\n"
                         "Lejla kaufte ein Kupferkännchen und sechs Kaffeetassen für ihre Oma in Deutschland. „Viel Freude damit!“, sagte der Meister. „Und trinken Sie Kaffee daraus. Stellen Sie es nicht nur ins Regal.“"),
        # "Nemojte je samo držati": je ist hier "sie", die Džezva (Prüfbericht 1.4, B10)
        "vokabeln": {"sto": "hundert", "jeste": "ihr seid / Sie sind (Jeste li …?: Haben Sie …?)", "mladi": "die Jungen / junge Leute",
                     "je": "ist / sie (Akk.)"},
        "fragen": [
            {"frage": "Woraus machen die Handwerker im Kazandžiluk ihre Sachen?", "optionen": ["aus Kupfer", "aus Holz", "aus Glas"], "richtig": "aus Kupfer"},
            {"frage": "Wie lange braucht der Meister für ein Kupferkännchen?", "optionen": ["fast einen ganzen Tag", "nur eine halbe Stunde", "fast eine ganze Woche"], "richtig": "fast einen ganzen Tag"},
            {"frage": "Wo arbeitet der Sohn des Meisters?", "optionen": ["bei einer Bank", "im Laden des Vaters", "in Deutschland"], "richtig": "bei einer Bank"},
        ],
    },
    {
        "id": "b1_kahva", "titel": "Kahva kod komšinice", "stufe": "B1", "passt_zu": "miteinander_umgehen",
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
                 "Ostat ću dvije sedmice. Prvu sedmicu bih bio kod vas ako vam to ne smeta. Drugu sedmicu idem kod nane u Goražde. Ona me već svaki dan pita kad dolazim.\n\n"
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
        "text": ("Zmaj je mali zmaj koji živi u Njemačkoj. Već nekoliko mjeseci uči bosanski jer ovog ljeta ide kod nane u Mostar. Svako veče ponavlja nove riječi: kuća, voda, hljeb, kahva.\n\n"
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
