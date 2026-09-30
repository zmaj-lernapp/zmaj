# -*- coding: utf-8 -*-
"""
entwurf_technik.py  -  ENTWURF, NICHT IN DER APP

Zwei neue Level mit technischem Grundwortschatz. Wunsch eines Testers vom
24.09.2026 (VOKABELN_PLAN.md: "geläufige Wörter wie Maschine, ohne ins
Fachliche abzugleiten"). Themen festgelegt von Ajdin am 30.09.2026:
Werkzeug & Werkstatt, Handy & Computer, Auto & Verkehr, Haushaltsgeräte -
zwei Level, zusammen etwa 60 Wörter.

Diese Datei wird von NICHTS gelesen. vokabeln.py, uebersetzungen.py und
inhalt_bauen.py wissen nichts von ihr, die App zählt weiter 63 Level. Erst
wenn Kübra die Liste durchgesehen hat und die Aufnahmen gemacht sind
(Azure, kostet Guthaben), werden die Blöcke unten in vokabeln.py und die
Übersetzungen in uebersetzungen.py übertragen.

Geprüft beim Schreiben (entwurf_technik_pruefen.py):
  - kein bosnisches Wort steht schon in einem anderen Level
  - keine Bedeutung fällt in einer der acht Sprachen mit einer
    vorhandenen zusammen (sonst wäre die Auswahlaufgabe nicht entscheidbar)
  - jede deutsche Zeile hat alle sieben Übersetzungen

Nachgeschlagen am 01.10.2026:
  kliješta     mit ije, Mehrzahlwort (kakosepise.info, gramarko.com)
  odvijač      bosnische Händler schreiben "odvijači - šrafcigeri"
               (delialati.ba) - beide Formen stehen deshalb drin
  mikrovalna   so bei ekupi.ba/bs, tehnolix.ba, domod.ba; "mikrotalasna"
               nur vereinzelt (superponuda.ba)
  sipati gorivo  Oslobođenje und Radio Sarajevo; "natočiti" auch üblich
  pomoć na cesti  so bei BIHAMK und JP Ceste FBiH
"""

# Vorschlag: beide hinter "technik" in Sektion 4. "Auto" passt dort nur
# halb - alternativ Sektion 6 oder eine eigene. Entscheidet Ajdin.
LEVEL = [
    {"id": "auto_werkstatt", "label": "Auto & Werkstatt", "sektion": "zuhause2",
     "tipp": "Tanken, Panne, Werkzeug – was man auf der Straße und in der Werkstatt braucht.",
     "baut_auf": ["technik", "reisen"],
     "words": [
        {"de": "Kraftstoff / Sprit",                 "bs": "gorivo"},
        {"de": "tanken",                             "bs": "sipati gorivo"},
        {"de": "Reifen",                             "bs": "guma"},
        {"de": "Ich habe einen Platten.",            "bs": "Pukla mi je guma."},
        {"de": "Bremse",                             "bs": "kočnica"},
        {"de": "Motor",                              "bs": "motor"},
        {"de": "Autobatterie",                       "bs": "akumulator"},
        {"de": "Sicherheitsgurt",                    "bs": "sigurnosni pojas"},
        {"de": "Parkplatz",                          "bs": "parking"},
        {"de": "parken",                             "bs": "parkirati"},
        {"de": "Ampel",                              "bs": "semafor"},
        {"de": "Kreuzung",                           "bs": "raskrsnica"},
        {"de": "Verkehr",                            "bs": "saobraćaj"},
        {"de": "Stau",                               "bs": "gužva"},
        {"de": "Strafzettel / Bußgeld",              "bs": "kazna"},
        {"de": "Zulassung (Auto)",                   "bs": "registracija"},
        {"de": "Hauptuntersuchung (TÜV)",            "bs": "tehnički pregled"},
        {"de": "Autowerkstatt",                      "bs": "autoservis"},
        {"de": "Abschleppdienst",                    "bs": "šlep služba"},
        {"de": "Pannenhilfe",                        "bs": "pomoć na cesti"},
        {"de": "Schraubenzieher",                    "bs": "odvijač / šrafciger"},
        {"de": "Zange",                              "bs": "kliješta"},
        {"de": "Bohrmaschine",                       "bs": "bušilica"},
        {"de": "bohren",                             "bs": "bušiti"},
        {"de": "Säge",                               "bs": "testera"},
        {"de": "Rollgabelschlüssel (Engländer)",     "bs": "francuski ključ"},
        {"de": "Maßband / Zollstock",                "bs": "metar"},
        {"de": "Kleber",                             "bs": "ljepilo"},
        {"de": "Verlängerungskabel",                 "bs": "produžni kabl"},
        {"de": "Werkstatt",                          "bs": "radionica"},
     ]},
    {"id": "geraete", "label": "Handy, Computer & Geräte", "sektion": "zuhause2",
     "tipp": "Laden, Passwort, Nachricht – und die Geräte im Haushalt.",
     "baut_auf": ["technik", "zuhause"],
     "words": [
        {"de": "Ladegerät",                          "bs": "punjač"},
        {"de": "Akku",                               "bs": "baterija"},
        {"de": "Der Akku ist leer.",                 "bs": "Baterija je prazna."},
        {"de": "aufladen",                           "bs": "napuniti"},
        {"de": "Passwort",                           "bs": "šifra / lozinka"},
        {"de": "Wie ist das WLAN-Passwort?",         "bs": "Koja je šifra za WiFi?"},
        {"de": "Internet",                           "bs": "internet"},
        {"de": "Kein Empfang.",                      "bs": "Nema signala."},
        {"de": "Nachricht",                          "bs": "poruka"},
        {"de": "eine Nachricht schicken",            "bs": "poslati poruku"},
        {"de": "anrufen",                            "bs": "nazvati"},
        {"de": "App",                                "bs": "aplikacija"},
        {"de": "Bildschirm",                         "bs": "ekran"},
        {"de": "Tastatur",                           "bs": "tastatura"},
        {"de": "Drucker",                            "bs": "štampač"},
        {"de": "Kopfhörer",                          "bs": "slušalice"},
        {"de": "fotografieren",                      "bs": "slikati"},
        {"de": "aktualisieren",                      "bs": "ažurirati"},
        {"de": "Spülmaschine",                       "bs": "mašina za suđe"},
        {"de": "Wäschetrockner",                     "bs": "sušilica za veš"},
        {"de": "Mikrowelle",                         "bs": "mikrovalna"},
        {"de": "Toaster",                            "bs": "toster"},
        {"de": "Wasserkocher",                       "bs": "kuhalo za vodu"},
        {"de": "Föhn",                               "bs": "fen"},
        {"de": "Klimaanlage",                        "bs": "klima"},
        {"de": "Ventilator",                         "bs": "ventilator"},
        {"de": "Fernbedienung",                      "bs": "daljinski"},
        {"de": "Kaffeemaschine",                     "bs": "aparat za kahvu"},
        {"de": "Bedienungsanleitung",                "bs": "uputstvo"},
        {"de": "Garantie",                           "bs": "garancija"},
     ]},
]

SAETZE = [
    {"kat": "auto_werkstatt", "text": "Moram sipati ___.",        "answer": "gorivo",    "de": "Ich muss tanken."},
    {"kat": "auto_werkstatt", "text": "Pukla mi je ___.",         "answer": "guma",      "de": "Ich habe einen Platten."},
    {"kat": "auto_werkstatt", "text": "Gdje mogu ___ auto?",      "answer": "parkirati", "de": "Wo kann ich das Auto parken?"},
    {"kat": "auto_werkstatt", "text": "Na ___ je crveno.",        "answer": "semaforu",  "de": "Die Ampel ist rot."},
    {"kat": "auto_werkstatt", "text": "Daj mi ___, molim te.",    "answer": "kliješta",  "de": "Gib mir bitte die Zange."},
    {"kat": "geraete",        "text": "Koja je ___ za WiFi?",     "answer": "šifra",     "de": "Wie ist das WLAN-Passwort?"},
    {"kat": "geraete",        "text": "Baterija je ___.",         "answer": "prazna",    "de": "Der Akku ist leer."},
    {"kat": "geraete",        "text": "Gdje je moj ___?",         "answer": "punjač",    "de": "Wo ist mein Ladegerät?"},
    {"kat": "geraete",        "text": "Pošalji mi ___.",          "answer": "poruku",    "de": "Schick mir eine Nachricht."},
    {"kat": "geraete",        "text": "Ne radi ___ za suđe.",     "answer": "mašina",    "de": "Die Spülmaschine funktioniert nicht."},
]

# Übersetzungen: deutscher Text -> Zielsprache, genau wie "texte" in
# uebersetzungen.py. Reihenfolge je Zeile: en, tr, sv, nl, nb, da, fr.
NB = " "
_Z = [
 ("Auto & Werkstatt", "Car & workshop", "Araba ve tamirhane", "Bil & verkstad", "Auto & werkplaats", "Bil & verksted", "Bil & værksted", "Voiture & atelier"),
 ("Handy, Computer & Geräte", "Phone, computer & appliances", "Telefon, bilgisayar ve cihazlar", "Mobil, dator & apparater", "Telefoon, computer & apparaten", "Mobil, datamaskin & apparater", "Mobil, computer & apparater", "Portable, ordinateur & appareils"),
 ("Tanken, Panne, Werkzeug – was man auf der Straße und in der Werkstatt braucht.",
  "Filling up, breakdowns, tools – what you need on the road and in the workshop.",
  "Yakıt almak, arıza, alet – yolda ve tamirhanede ihtiyacın olanlar.",
  "Tanka, motorstopp, verktyg – det du behöver på vägen och i verkstaden.",
  "Tanken, pech, gereedschap – wat je onderweg en in de werkplaats nodig hebt.",
  "Tanke, motorstopp, verktøy – det du trenger på veien og i verkstedet.",
  "Tanke, motorstop, værktøj – det, du har brug for på vejen og i værkstedet.",
  "Faire le plein, panne, outils – ce qu'il te faut sur la route et à l'atelier."),
 ("Laden, Passwort, Nachricht – und die Geräte im Haushalt.",
  "Charging, passwords, messages – and the appliances at home.",
  "Şarj, şifre, mesaj – ve evdeki cihazlar.",
  "Ladda, lösenord, meddelanden – och apparaterna hemma.",
  "Opladen, wachtwoord, berichten – en de apparaten in huis.",
  "Lade, passord, meldinger – og apparatene hjemme.",
  "Oplade, adgangskode, beskeder – og apparaterne derhjemme.",
  "Recharger, mot de passe, messages – et les appareils de la maison."),
 # Level 1
 ("Kraftstoff / Sprit", "fuel", "yakıt", "bränsle", "brandstof", "drivstoff", "brændstof", "carburant"),
 ("tanken", "to fill up (the tank)", "yakıt almak", "tanka", "tanken", "tanke", "tanke", "faire le plein"),
 ("Reifen", "tire", "lastik", "däck", "band (auto)", "dekk", "dæk", "pneu"),
 ("Ich habe einen Platten.", "I have a flat tire.", "Lastiğim patladı.", "Jag har fått punktering.", "Ik heb een lekke band.", "Jeg har fått punktering.", "Jeg er punkteret.", "J'ai crevé."),
 ("Bremse", "brake", "fren", "broms", "rem", "brems", "bremse", "frein"),
 ("Motor", "engine", "motor", "motor", "motor", "motor", "motor", "moteur"),
 ("Autobatterie", "car battery", "akü", "bilbatteri", "accu (auto)", "bilbatteri", "bilbatteri", "batterie de voiture"),
 ("Sicherheitsgurt", "seat belt", "emniyet kemeri", "säkerhetsbälte", "veiligheidsgordel", "bilbelte", "sikkerhedssele", "ceinture de sécurité"),
 ("Parkplatz", "parking lot", "otopark", "parkeringsplats", "parkeerplaats", "parkeringsplass", "parkeringsplads", "parking"),
 ("parken", "to park", "park etmek", "parkera", "parkeren", "parkere", "parkere", "se garer"),
 ("Ampel", "traffic light", "trafik lambası", "trafikljus", "verkeerslicht", "trafikklys", "trafiklys", "feu de circulation"),
 ("Kreuzung", "intersection", "kavşak", "korsning", "kruispunt", "veikryss", "vejkryds", "carrefour"),
 ("Verkehr", "traffic", "trafik", "trafik", "verkeer", "trafikk", "trafik", "circulation"),
 ("Stau", "traffic jam", "trafik sıkışıklığı", "bilkö", "file", "kø (trafikk)", "kø (trafik)", "embouteillage"),
 ("Strafzettel / Bußgeld", "fine / ticket", "trafik cezası", "böter", "boete", "bot", "bøde", "amende"),
 ("Zulassung (Auto)", "car registration", "araç ruhsatı", "registrering (bil)", "kenteken (auto)", "registrering (bil)", "indregistrering (bil)", "immatriculation"),
 ("Hauptuntersuchung (TÜV)", "vehicle inspection", "araç muayenesi", "bilbesiktning", "APK-keuring", "EU-kontroll", "bilsyn", "contrôle technique"),
 ("Autowerkstatt", "car repair shop", "oto tamirhanesi", "bilverkstad", "garage", "bilverksted", "autoværksted", "garage"),
 ("Abschleppdienst", "towing service", "çekici hizmeti", "bärgningstjänst", "sleepdienst", "bergingstjeneste", "bugseringstjeneste", "service de dépannage"),
 ("Pannenhilfe", "roadside assistance", "yol yardımı", "vägassistans", "pechhulp", "veihjelp", "vejhjælp", "assistance routière"),
 ("Schraubenzieher", "screwdriver", "tornavida", "skruvmejsel", "schroevendraaier", "skrutrekker", "skruetrækker", "tournevis"),
 ("Zange", "pliers", "pense", "tång", "tang", "tang", "tang", "pince"),
 ("Bohrmaschine", "drill", "matkap", "borrmaskin", "boormachine", "boremaskin", "boremaskine", "perceuse"),
 ("bohren", "to drill", "delmek", "borra", "boren", "bore", "bore", "percer"),
 ("Säge", "saw", "testere", "såg", "zaag", "sag", "sav", "scie"),
 ("Rollgabelschlüssel (Engländer)", "adjustable wrench", "İngiliz anahtarı", "skiftnyckel", "Engelse sleutel", "skiftenøkkel", "svensknøgle", "clé à molette"),
 ("Maßband / Zollstock", "tape measure", "şerit metre", "måttband", "rolmaat", "målebånd", "målebånd", "mètre ruban"),
 ("Kleber", "glue", "yapıştırıcı", "lim", "lijm", "lim", "lim", "colle"),
 ("Verlängerungskabel", "extension cord", "uzatma kablosu", "förlängningssladd", "verlengsnoer", "skjøteledning", "forlængerledning", "rallonge"),
 ("Werkstatt", "workshop", "atölye", "verkstad", "werkplaats", "verksted", "værksted", "atelier"),
 # Level 2
 ("Ladegerät", "charger", "şarj aleti", "laddare", "oplader", "lader", "oplader", "chargeur"),
 ("Akku", "battery", "batarya", "batteri", "batterij", "batteri", "batteri", "batterie"),
 ("Der Akku ist leer.", "The battery is dead.", "Şarjım bitti.", "Batteriet är slut.", "Mijn batterij is leeg.", "Batteriet er tomt.", "Batteriet er fladt.", "Je n'ai plus de batterie."),
 ("aufladen", "to charge", "şarj etmek", "ladda", "opladen", "lade", "oplade", "recharger"),
 ("Passwort", "password", "şifre", "lösenord", "wachtwoord", "passord", "adgangskode", "mot de passe"),
 ("Wie ist das WLAN-Passwort?", "What's the Wi-Fi password?", "Wi-Fi şifresi ne?", "Vad är wifi-lösenordet?", "Wat is het wifi-wachtwoord?", "Hva er wifi-passordet?", "Hvad er wifi-koden?", "C'est quoi, le code wifi" + NB + "?"),
 ("Internet", "internet", "internet", "internet", "internet", "internett", "internet", "internet"),
 ("Kein Empfang.", "No signal.", "Sinyal yok.", "Ingen täckning.", "Geen bereik.", "Ingen dekning.", "Ingen dækning.", "Pas de réseau."),
 ("Nachricht", "message", "mesaj", "meddelande", "bericht", "melding", "besked", "message"),
 ("eine Nachricht schicken", "to send a message", "mesaj göndermek", "skicka ett meddelande", "een bericht sturen", "sende en melding", "sende en besked", "envoyer un message"),
 ("anrufen", "to call (on the phone)", "aramak (telefonla)", "ringa (i telefon)", "bellen (telefoon)", "ringe (i telefonen)", "ringe op", "appeler (au téléphone)"),
 ("App", "app", "uygulama", "app", "app", "app", "app", "application"),
 ("Bildschirm", "screen", "ekran", "skärm", "scherm", "skjerm", "skærm", "écran"),
 ("Tastatur", "keyboard", "klavye", "tangentbord", "toetsenbord", "tastatur", "tastatur", "clavier"),
 ("Drucker", "printer", "yazıcı", "skrivare", "printer", "skriver", "printer", "imprimante"),
 ("Kopfhörer", "headphones", "kulaklık", "hörlurar", "koptelefoon", "hodetelefoner", "høretelefoner", "écouteurs"),
 ("fotografieren", "to take a photo", "fotoğraf çekmek", "fotografera", "fotograferen", "ta bilde", "tage et billede", "prendre une photo"),
 ("aktualisieren", "to update", "güncellemek", "uppdatera", "bijwerken", "oppdatere", "opdatere", "mettre à jour"),
 ("Spülmaschine", "dishwasher", "bulaşık makinesi", "diskmaskin", "vaatwasser", "oppvaskmaskin", "opvaskemaskine", "lave-vaisselle"),
 ("Wäschetrockner", "tumble dryer", "çamaşır kurutma makinesi", "torktumlare", "droger", "tørketrommel", "tørretumbler", "sèche-linge"),
 ("Mikrowelle", "microwave", "mikrodalga fırın", "mikrovågsugn", "magnetron", "mikrobølgeovn", "mikrobølgeovn", "micro-ondes"),
 ("Toaster", "toaster", "ekmek kızartma makinesi", "brödrost", "broodrooster", "brødrister", "brødrister", "grille-pain"),
 ("Wasserkocher", "electric kettle", "su ısıtıcısı", "vattenkokare", "waterkoker", "vannkoker", "elkedel", "bouilloire"),
 ("Föhn", "hair dryer", "saç kurutma makinesi", "hårtork", "föhn", "hårføner", "hårtørrer", "sèche-cheveux"),
 ("Klimaanlage", "air conditioning", "klima", "luftkonditionering", "airco", "klimaanlegg", "aircondition", "climatisation"),
 ("Ventilator", "fan", "vantilatör", "fläkt", "ventilator", "vifte", "ventilator", "ventilateur"),
 ("Fernbedienung", "remote control", "kumanda", "fjärrkontroll", "afstandsbediening", "fjernkontroll", "fjernbetjening", "télécommande"),
 ("Kaffeemaschine", "coffee maker", "kahve makinesi", "kaffebryggare", "koffiezetapparaat", "kaffetrakter", "kaffemaskine", "cafetière"),
 ("Bedienungsanleitung", "instruction manual", "kullanım kılavuzu", "bruksanvisning", "handleiding", "bruksanvisning", "brugsanvisning", "mode d'emploi"),
 ("Garantie", "warranty", "garanti", "garanti", "garantie", "garanti", "garanti", "garantie"),
 # Sätze
 ("Ich muss tanken.", "I need to fill up.", "Yakıt almam lazım.", "Jag måste tanka.", "Ik moet tanken.", "Jeg må tanke.", "Jeg skal tanke.", "Je dois faire le plein."),
 ("Wo kann ich das Auto parken?", "Where can I park the car?", "Arabayı nereye park edebilirim?", "Var kan jag parkera bilen?", "Waar kan ik de auto parkeren?", "Hvor kan jeg parkere bilen?", "Hvor kan jeg parkere bilen?", "Où est-ce que je peux garer la voiture" + NB + "?"),
 ("Die Ampel ist rot.", "The light is red.", "Işık kırmızı.", "Det är rött ljus.", "Het stoplicht staat op rood.", "Det er rødt lys.", "Der er rødt lys.", "Le feu est rouge."),
 ("Gib mir bitte die Zange.", "Please hand me the pliers.", "Penseyi verir misin lütfen?", "Ge mig tången, tack.", "Geef me de tang even, alsjeblieft.", "Gi meg tanga, er du snill.", "Giv mig lige tangen.", "Passe-moi la pince, s'il te plaît."),
 ("Wo ist mein Ladegerät?", "Where is my charger?", "Şarj aletim nerede?", "Var är min laddare?", "Waar is mijn oplader?", "Hvor er laderen min?", "Hvor er min oplader?", "Où est mon chargeur" + NB + "?"),
 ("Schick mir eine Nachricht.", "Send me a message.", "Bana mesaj at.", "Skicka ett meddelande till mig.", "Stuur me een bericht.", "Send meg en melding.", "Send mig en besked.", "Envoie-moi un message."),
 ("Die Spülmaschine funktioniert nicht.", "The dishwasher isn't working.", "Bulaşık makinesi çalışmıyor.", "Diskmaskinen fungerar inte.", "De vaatwasser doet het niet.", "Oppvaskmaskinen virker ikke.", "Opvaskemaskinen virker ikke.", "Le lave-vaisselle ne marche pas."),
]
SPRACHEN = ["en", "tr", "sv", "nl", "nb", "da", "fr"]
UEBERSETZUNGEN = {c: {z[0]: z[i + 1] for z in _Z} for i, c in enumerate(SPRACHEN)}

# Zum Nachsehen mit Kübra - hier war ich mir nicht sicher.
FRAGEN = [
    ("sipati gorivo", "oder lieber natočiti gorivo? Beides steht in bosnischen Zeitungen."),
    ("testera", "oder pila? Im Standard steht beides, gesagt wird meist testera."),
    ("odvijač / šrafciger", "beide Formen drin - reicht eine?"),
    ("šifra / lozinka", "šifra sagt man, lozinka ist das Wort im Handymenü - beide drin."),
    ("mikrovalna", "oder mikrotalasna? Die Händler in Sarajevo schreiben mikrovalna."),
    ("aparat za kahvu", "kahva wie überall in der App - oder sagt man hier aparat za kafu?"),
    ("slikati", "fotografieren - oder lieber fotografisati?"),
    ("gužva", "heißt Stau UND Gedränge. Reicht das als Wort für Stau?"),
    ("parking", "oder parking mjesto / parkiralište?"),
    ("daljinski", "umgangssprachlich für daljinski upravljač - passt das?"),
]
