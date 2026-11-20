# -*- coding: utf-8 -*-
"""Andere bosnische Wörter, die beim Tippen genauso gelten (varianten.py, 12.11.2026).

Bis dahin nahm „Voda je u ___.“ nur flaši - boci war falsch und kostete ein
Leben -, und „Pijem kahvu“ nahm nicht „Pijem kafu“, obwohl das Wort selbst
„kahva / kafa“ heißt. Ajdin: „die ganze app nochmal danach kontrollieren“.
Zuerst nur die eindeutigen Paare, seit dem 14.11.2026 auch die fraglichen aus
Tabelle 2c (Prüfbericht 1.4, F6): „nimm doch kroatische und die anderen rein
die sind nur nicht sichtbar“ - beim Tippen richtig, gezeigt nie.

Getippt wird an zwei Stellen, beide in renderTask(): Schreibaufgabe
(annehmbar()) und Lückensatz. Sie laufen in Lektion, Level-Test, Einstufung,
Fehler-Topf, „Heute fällig“, Markiert und im Zahnarzt-Teil. Beim Satzbau wird
nichts getippt, dort zählt nur, dass die andere Form keine falsche Kachel ist.
In der Auswahl hält geschwister() sie aus den falschen Knöpfen, das Sprechen
bleibt. Den Ablauf in der App prüft tests_e2e/test_varianten.py.

Die Schnappschüsse unten sind ALLES, was dadurch neu richtig wird. Kommt etwas
dazu oder fällt etwas weg, scheitert der Test - dann bitte prüfen und hier
nachtragen.
"""
import ast
import glob
import io
import json
import os
import re
import shutil
import subprocess

import pytest

import inhalt
import varianten

# Schreibaufgabe: Kennung des Wortes -> zusätzliche Antworten
WOERTER = {
    "braun:kafena": ["smeđa", "kahvena", "braon"],
    "rosa:roza": ["ružičasta"],
    "jetzt:sada": ["sad"],
    "abend:večer": ["veče"],
    "nachbar:komšija": ["susjed"],
    "hose:pantalone": ["hlače"],
    "grüne bohnen:boranija": ["mahune"],
    "mayonnaise:majonez": ["majoneza"],
    "senf:senf": ["gorušica"],
    "thunfisch:tunjevina": ["tuna"],
    "bosnischer kaffee:bosanska kahva": ["bosanska kafa", "bosanska kava", "domaća kahva", "domaća kafa", "domaća kava"],
    "hahn:horoz": ["pijetao"],
    "lamm:jagnje": ["janje"],
    "insel:ostrvo": ["otok"],
    "luft:zrak": ["vazduh"],
    "flasche:flaša": ["boca"],
    "decke (bettdecke):deka": ["pokrivač", "ćebe", "poplun", "jorgan"],
    "waschbecken:lavabo": ["umivaonik"],
    "nachbarin:komšinica": ["susjeda"],
    "leiter:merdevine": ["ljestve", "skale"],
    "schraube:šaraf": ["vijak", "zavrtanj"],
    "säge:testera": ["pila"],
    "drucker:štampač": ["printer", "pisač"],
    "nie:nikad": ["nikada"],
    "ich trinke kaffee:Pijem kahvu": ["Pijem kafu", "Pijem kavu"],
    "ich rufe den arzt:Zovem doktora": ["Zovem ljekara", "Zovem liječnika"],
    "eine tasse kaffee:šolja kahve": ["šolja kafe", "šolja kave", "šalica kahve", "šalica kafe", "šalica kave"],
    "viele menschen:mnogo ljudi": ["puno ljudi"],
    "viel / viele:mnogo": ["puno"],
    "ich helfe meiner mutter:Pomažem majci": ["Pomažem mami"],
    "am nachmittag:popodne": ["poslijepodne", "poslije podne"],
    "ein kaffee:jedna kahva": ["jedna kafa", "jedna kava"],
    "zwei kaffee:dvije kahve": ["dvije kafe", "dvije kave"],
    "zweimal:dva puta": ["dvaput"],
    "interessant:zanimljivo": ["interesantno"],
    "gepäck:prtljag": ["prtljaga"],
    "büro:kancelarija": ["ured"],
    "ingenieur:inženjer": ["inžinjer"],
    "computer:računar": ["kompjuter", "računalo"],
    "der kaffee ist heiß:Kahva je vruća": ["Kafa je vruća", "Kava je vruća"],
    "gehen wir einen kaffee trinken:Idemo na kahvu": ["Idemo na kafu", "Idemo na kavu"],
    "nachbarn (mehrzahl):komšije": ["susjedi"],
    # Tabelle 2c (Ajdin, 14.11.2026, F6). Die Nummer ist die Zeile der Tabelle.
    "brot:hljeb": ["kruh"],                                   # 1
    "ich esse brot:Jedem hljeb": ["Jedem kruh"],
    "es gibt kein brot:Nema hljeba": ["Nema kruha"],
    "suppe:supa": ["juha"],                                   # 2
    "gehalt:plata": ["plaća"],                                # 3
    "bruttogehalt:bruto plata": ["bruto plaća"],
    "nettogehalt:neto plata": ["neto plaća"],
    "langsam:polako": ["polahko", "sporo"],                            # 4
    "minute:minuta": ["minut"],                               # 5
    "gestern:jučer": ["juče"],                                # 6
    "woche:sedmica": ["hefta", "tjedan"],                               # 7
    "letzte woche:prošle sedmice": ["prošli tjedan", "prošlog tjedna", "prošle hefte"],
    "topf:lonac": ["šerpa"],                                  # 8, bosanski lonac nicht
    "pfanne:tava": ["tiganj"],                                # 9
    "spinat:špinat": ["spanać"],                              # 10
    "garten:bašta": ["bašča", "vrt"],                                # 11
    "tochter:kćerka": ["kći", "kćer", "ćerka"],                        # 12
    "stunde / uhr:sat": ["sahat"],                            # 13
    "geschichte (fach):historija": ["povijest"],              # 14
    "besuch:posjeta": ["posjet"],                             # 15
    "miete:kirija": ["stanarina", "najamnina"],               # 16
    "kühlschrank:frižider": ["hladnjak"],                     # 17
    "backofen:rerna": ["pećnica"],
    "tüte / plastiktüte:kesa": ["vrećica"],
    "essig:sirće": ["ocat"],
    "zimmerdecke:plafon": ["strop"],
    "fabrik:fabrika": ["tvornica"],
    "aprikose:kajsija": ["marelica"],
    "lauch:praziluk": ["poriluk"],
    "handtuch:peškir": ["ručnik"],
    "laden:prodavnica": ["radnja", "trgovina", "dućan"],                           # 18
    "geschäft:radnja": ["prodavnica", "trgovina", "dućan"],
    "hof (am haus):dvorište": ["avlija"],                     # 19
    "hof / innenhof:avlija": ["dvorište"],
    "manchmal:ponekad": ["nekad", "nekada", "katkad", "katkada"],                  # 20, nekada seit der dritten Runde
    "kaffeetasse (traditionell):fildžan": ["findžan"],        # 22 (21 oben bei kafena)
    "auto:auto": ["kola", "automobil"],                                    # 23
    "geld:novac": ["pare"],                                   # 24
    "handy:mobitel": ["mobilni"],                             # 25
    "markt:pijaca": ["pazar", "tržnica"],                                # 26
    "speisekarte:jelovnik": ["meni"],                         # 27
    "formular:obrazac": ["formular"],                         # 28
    "entschuldigung (du):Izvini": ["Oprosti"],                # 29
    "ob:da li": ["je li"],                                    # 31
    "vielen dank:Hvala puno": ["Puno hvala", "Hvala lijepa", "Hvala mnogo", "Mnogo hvala"],   # 32, Mnogo hvala seit 17.11.
    "auf wiedersehen:Doviđenja": ["Do viđenja"],              # 33
    "tschüss:Ćao": ["Zdravo", "Do viđenja"],                            #    das Wort nimmt auch Doviđenja
    "guten abend:Dobro veče": ["Dobra večer"],                # 34
    "am abend:navečer": ["uveče", "uvečer", "naveče"],                            # 35
    "am morgen:ujutro": ["ujutru"],
    "bei meinem freund:kod prijatelja": ["kod druga"],        # 36
    "anrede: freund!:prijatelju!": ["druže!"],
    "fenster:prozor": ["pendžer"],                            # 37 (deka und merdevine oben)
    "wand:zid": ["duvar"],
    "straße:ulica": ["sokak"],
    "schrank:ormar": ["dolap", "orman"],
    "gast:gost": ["musafir"],
    "gäste:gosti": ["musafiri"],
    "medikament:lijek": ["hap"],
    "erkältung:prehlada": ["nahlada"],
    "hefe:kvasac": ["germa"],
    "treppe:stepenice": ["basamaci", "stube"],
    "hund:pas": ["kuče"],
    "stück:komad": ["parče"],
    "metzgerei:mesnica": ["kasapnica"],
    "schulferien:raspust": ["ferije"],
    "haselnuss:lješnjak": ["lješnik"],
    "kürbis:bundeva": ["tikva"],                              # 39
    "granatapfel:nar": ["šipak"],
    "beißen:ugristi": ["ujesti"],
    "verkehr:saobraćaj": ["promet"],
    # Dritte Runde (Ajdin, 14.11.2026 abends, Offen-Liste 5a)
    "entschuldigung (sie):Izvinite": ["Oprostite"],
    "ich habe ein auto:Imam auto": ["Imam kola", "Imam automobil"],
    "im auto:u autu": ["u kolima", "u automobilu"],
    "ich habe kein geld:Nemam novca": ["Nemam para"],
    "auf dem markt:na pijaci": ["na pazaru", "na tržnici"],
    "auf der straße:na ulici": ["na sokaku"],
    "er hat einen hund:On ima psa": ["On ima kuče"],
    # Fragen vom 15.11.2026 (Ajdin abends, 9a bis 9i, Offen-Liste 5d)
    "mit dem auto:autom": ["kolima", "automobilom"],
    # nicht „očev kola“ aus dem "auch"; „očeva kola“ seit den Fragen vom 16.11.2026 (8a);
    # automobil oca und očev automobil seit dem 21.11.2026 (K2 auto -> automobil, ganze Wendung)
    "das auto des vaters:auto oca": ["kola oca", "automobil oca", "očeva kola", "očev automobil"],
    "geld abheben:podići novac": ["podići pare"],
    "geld einzahlen:uplatiti novac": ["uplatiti pare"],
    "wir suchen die straße:Tražimo ulicu": ["Tražimo sokak"],
    "ich habe angst vor hunden:Bojim se pasa": ["Bojim se kučadi", "Plašim se pasa", "Plašim se kučadi"],
    "vorsicht vor dem hund!:Čuvaj se psa!": ["Čuvaj se kučeta!"],
    # „Der Hund hat mich gebissen“ nahm vom 15.11. (9i) bis 16.11.2026 (8b) auch
    # „Kuče me je ujelo“, jetzt nur noch „Pas me je ujeo“ und „Ujeo me je pas“.
    # K2 Wort-Alternativen (Ajdin K2, 20.11.2026; Release\Wortschatz\k2_2026-11-20\final):
    # die 954 Paare in varianten.py. Was bei den Wörtern oben dazukam, steht dort.
    "willkommen:Dobro došli": ["Dobro došao", "Dobro došla", "Dobrodošao", "Dobrodošla"],
    "in ordnung / okay:U redu": ["Važi"],
    "guten appetit:Prijatno": ["Dobar tek"],
    "rot:crvena": ["crven", "crveno"],
    "blau:plava": ["plav", "plavo"],
    "grün:zelena": ["zelen", "zeleno"],
    "gelb:žuta": ["žut", "žuto"],
    "schwarz:crna": ["crn", "crno"],
    "weiß:bijela": ["bijel", "bijelo"],
    "grau:siva": ["siv", "sivo"],
    "orange:narandžasta": ["narančasta", "narandžast", "narandžasto"],
    "lila:ljubičasta": ["ljubičast", "ljubičasto", "lila"],
    "oma:nana": ["nena"],
    "familie:porodica": ["obitelj", "familija"],
    "kartoffel:krompir": ["krumpir"],
    "tomate:paradajz": ["rajčica"],
    "zwiebel:luk": ["crni luk"],
    "reis:riža": ["pirinač"],
    "januar:januar": ["siječanj"],
    "februar:februar": ["veljača"],
    "märz:mart": ["ožujak"],
    "april:april": ["travanj"],
    "mai:maj": ["svibanj"],
    "juni:juni": ["jun", "lipanj"],
    "juli:juli": ["jul", "srpanj"],
    "august:august": ["avgust", "kolovoz"],
    "september:septembar": ["rujan"],
    "oktober:oktobar": ["listopad"],
    "november:novembar": ["studeni"],
    "dezember:decembar": ["prosinac"],
    "bad:kupatilo": ["kupaonica"],
    "wohnzimmer:dnevna soba": ["dnevni boravak"],
    "tisch:sto": ["stol"],
    "herd:šporet": ["štednjak"],
    "warm:toplo": ["topao", "topla"],
    "kalt:hladno": ["hladan", "hladna"],
    "heiß:vruće": ["vruć", "vruća"],
    "baum:drvo": ["stablo"],
    "donner:grmljavina": ["grom"],
    "schatten:hlad": ["sjena"],
    "ohr:uho": ["uvo"],
    "bauch:stomak": ["trbuh"],
    "apotheke:apoteka": ["ljekarna"],
    "fieber:temperatura": ["vrućica"],
    "gute besserung!:Brz oporavak": ["Brzo ozdravi"],
    "einkaufszentrum:tržni centar": ["trgovački centar", "šoping centar"],
    "kasse:kasa": ["blagajna"],
    "kleidung:odjeća": ["roba"],
    "ich nehme das:Uzet ću ovo": ["Ovo ću uzeti", "Ja ću uzeti ovo", "Uzet ću to", "Uzeću ovo"],   # S-futur, seit 21.11.
    "geradeaus:pravo": ["ravno"],
    "bahnhof / haltestelle:stanica": ["stajalište", "kolodvor"],
    "wie viel kostet das?:Koliko košta?": ["Koliko to košta?", "Koliko ovo košta?"],
    "billig:jeftino": ["jeftin", "jeftina"],
    "offen:otvoreno": ["otvoren", "otvorena"],
    "geschlossen:zatvoreno": ["zatvoren", "zatvorena"],
    "sprechen:govoriti": ["pričati"],
    "was gibt's? / wie läuft's?:Šta ima?": ["Što ima?"],
    "kein problem:Nema problema": ["Nije problem"],
    "auf geht's!:Hajmo!": ["Hajdemo!", "Idemo!"],
    "schau mal:Vidi": ["Pogledaj", "Gledaj"],
    "wirklich?:Stvarno?": ["Zaista?", "Zbilja?"],
    "was machst du?:Šta radiš?": ["Što radiš?"],
    "das gefällt mir:Sviđa mi se": ["Dopada mi se"],
    "trockenobst:suho voće": ["suvo voće", "sušeno voće"],
    "blumenkohl:karfiol": ["cvjetača"],
    "karotte:mrkva": ["šargarepa"],
    "knoblauch:bijeli luk": ["češnjak"],
    "petersilie:peršun": ["peršin"],
    "pilze:gljive": ["pečurke"],
    "scharfe paprika:ljuta paprika": ["feferon"],
    "kekse:keks": ["keksi"],
    "lammfleisch:janjetina": ["jagnjetina"],
    "marmelade:džem": ["marmelada"],
    "rindfleisch:junetina": ["govedina"],
    "sahne:slatka pavlaka": ["slatko vrhnje"],
    "saure sahne:kisela pavlaka": ["kiselo vrhnje"],
    "sprudelwasser:kisela voda": ["gazirana voda"],
    "nudeln:tjestenina": ["pašta", "makaroni"],
    "pfeffer:biber": ["papar"],
    "sauerrahm / schmand:pavlaka": ["kiselo vrhnje"],
    "traubenbrand:loza": ["lozovača"],
    "huhn:kokoš": ["kokoška"],
    "küken / hähnchen:pile": ["pilić"],
    "stall:štala": ["staja"],
    "welpe:štene": ["kuče"],
    "schwalbe:lastavica": ["lasta"],
    "storch:roda": ["štrk"],
    "ratte:pacov": ["štakor"],
    "fliege:muha": ["muva"],
    "floh:buha": ["buva"],
    "forelle:pastrmka": ["pastrva"],
    "flohmarkt:buvljak": ["buvlja pijaca"],
    "gefährlich:opasno": ["opasan", "opasna"],
    "verboten:zabranjeno": ["zabranjen", "zabranjena"],
    "vorsicht! / pass auf!:Pazi!": ["Oprez!", "Pazi se!"],
    "brunnen:bunar": ["zdenac"],
    "erde / boden:zemlja": ["tlo"],
    "feld / acker:polje": ["njiva"],
    "höhle:pećina": ["špilja"],
    "hügel:brdo": ["brežuljak"],
    "quelle:izvor": ["vrelo"],
    "wasserfall:vodopad": ["slap"],
    "ast / zweig:grana": ["grančica"],
    "wer?:Ko?": ["Tko?"],
    "was?:Šta?": ["Što?"],
    "wohin?:Kuda?": ["Kamo?"],
    "woher?:Odakle?": ["Otkuda?", "Otkud?"],
    "wer bist du?:Ko si ti?": ["Tko si ti?"],
    "woher kommst du?:Odakle si?": ["Otkuda si?", "Otkud si?"],
    "wohin gehst du?:Kuda ideš?": ["Kamo ideš?"],
    "was ist das?:Šta je to?": ["Što je to?"],
    "was meinst du?:Šta misliš?": ["Što misliš?"],
    "das mädchen:djevojka": ["cura", "djevojčica"],
    "der junge:dječak": ["dečko"],
    "ich wohne:stanujem": ["živim"],
    "aber:ali": ["no"],
    "weil:jer": ["zato što", "pošto"],
    "wenn / falls:ako": ["ukoliko"],
    "deshalb:zato": ["stoga", "zbog toga"],
    "ich glaube nicht:Ne vjerujem": ["Mislim da ne"],
    "niemand:niko": ["nitko"],
    "auch:također": ["takođe"],
    "danach:zatim": ["potom", "nakon toga", "poslije toga"],
    "zuerst:prvo": ["najprije"],
    "wieder:opet": ["ponovno"],
    "sofort:odmah": ["smjesta"],
    "ständig:stalno": ["neprestano"],
    "hier ist / da ist:evo": ["eto"],
    "ganz (der ganze):cijeli": ["cio", "čitav", "čitava", "čitavo"],
    "ich brauche wasser:Trebam vodu": ["Treba mi vode"],
    "ich brauche einen schlüssel:Trebam ključ": ["Treba mi ključ"],
    "gabel:viljuška": ["vilica"],
    "geschirr:suđe": ["posuđe"],
    "geschirr spülen:prati suđe": ["prati posuđe"],
    "teller:tanjir": ["tanjur"],
    "regal / brett:polica": ["regal"],
    "sofa:kauč": ["sofa"],
    "vorhang:zavjesa": ["zastor", "perde"],
    "spiegel:ogledalo": ["zrcalo"],
    "toilette:WC": ["Zahod", "Toalet"],
    "toilettenpapier:toalet papir": ["wc papir", "toaletni papir"],
    "zahnpasta:pasta za zube": ["zubna pasta"],
    "aufräumen:pospremiti": ["spremiti", "srediti"],
    "bügeleisen:pegla": ["glačalo"],
    "bügeln:peglati": ["glačati"],
    "eimer:kanta": ["kofa", "vedro"],
    "müll:smeće": ["đubre"],
    "mülleimer / mülltonne:kanta za smeće": ["kanta za đubre"],
    "staubsauger:usisivač": ["usisavač"],
    "waschmaschine:veš mašina": ["perilica rublja", "mašina za veš"],
    "waschmittel:deterdžent": ["prašak"],
    "wäsche:veš": ["rublje"],
    "wäscheleine:štrik": ["konopac"],
    "aufzug:lift": ["dizalo"],
    "hausmeister:domar": ["kućepazitelj"],
    "ausschalten / ausmachen:ugasiti": ["isključiti"],
    "einschalten / anmachen:upaliti": ["uključiti"],
    "glühbirne:sijalica": ["žarulja"],
    "kohle:ugalj": ["ugljen"],
    "ofen (heizofen):peć": ["furuna"],
    "stecker:utikač": ["šteker"],
    "es funktioniert nicht:Ne radi": ["Ne funkcioniše", "Ne funkcionira"],
    "handwerker / fachmann:majstor": ["obrtnik", "zanatlija"],
    "nagel:ekser": ["čavao"],
    "wasserhahn:slavina": ["pipa", "česma"],
    "werkzeug:alat": ["alatka"],
    "kraftstoff / sprit:gorivo": ["benzin"],
    "tanken:sipati gorivo": ["sipati benzin", "tankati"],
    "parkplatz:parkiralište": ["parkirište", "parking"],
    "parken:parkirati": ["parkovati"],
    "kreuzung:raskrsnica": ["raskrižje", "križanje", "raskršće"],
    "kennzeichen (auto):registracija": ["tablice", "registarske tablice"],
    "autowerkstatt:autoservis": ["servis", "auto servis"],
    "abschleppdienst:šlep služba": ["vučna služba"],
    "pannenhilfe:pomoć na cesti": ["pomoć na putu"],
    "bohrmaschine:bušilica": ["bormašina"],
    "kleber:ljepilo": ["lijepak"],
    "bildschirm:ekran": ["zaslon"],
    "tastatur:tastatura": ["tipkovnica"],
    "fotografieren:slikati": ["fotografisati", "fotografirati"],
    "spülmaschine:mašina za suđe": ["perilica posuđa", "mašina za pranje suđa", "mašina za posuđe"],   # seit 21.11.
    "mikrowelle:mikrovalna": ["mikrotalasna", "mikrovalna pećnica"],
    "wasserkocher:kuhalo za vodu": ["kuvalo za vodu", "čajnik"],
    "föhn:fen": ["sušilo za kosu", "fen za kosu"],
    "klimaanlage:klima": ["klima uređaj"],
    "fernbedienung:daljinski": ["daljinski upravljač"],
    "bedienungsanleitung:uputstvo": ["upute", "uputstvo za upotrebu"],
    "garantie:garancija": ["jamstvo"],
    "von meinem bruder:od mog brata": ["od moga brata", "od mojeg brata"],
    "neben dem haus:pored kuće": ["pokraj kuće", "kraj kuće"],
    "tasse:šolja": ["šalica"],
    "kilo:kilogram": ["kilo", "kila"],
    "genug:dosta": ["dovoljno"],
    "in der nähe von:blizu": ["u blizini"],
    "mit:sa": ["s"],
    "zu / in richtung:prema": ["ka"],
    "über / oberhalb:iznad": ["nad"],
    "unter:ispod": ["pod"],
    "zwischen:između": ["među"],
    "vor (räumlich):ispred": ["pred"],
    "neben:pored": ["pokraj", "kraj"],
    "mit meiner frau:s mojom ženom": ["s mojom suprugom", "sa mojom suprugom"],
    "vor dem essen:prije jela": ["prije obroka"],
    "sag mir:Reci mi": ["Kaži mi"],
    "mir ist kalt:Hladno mi je": ["Zima mi je", "Meni je hladno"],
    "schenken:pokloniti": ["darovati"],
    "mit dem zug:vozom": ["vlakom"],
    "zu fuß:pješke": ["pješice"],
    "unter dem tisch:pod stolom": ["ispod stola"],
    "zug:voz": ["vlak"],
    "flugzeug:avion": ["zrakoplov"],
    "fahrrad:bicikl": ["biciklo"],
    "löffel:kašika": ["žlica"],
    "mit dem löffel:kašikom": ["žlicom"],
    "letztes jahr:prošle godine": ["lani"],
    "vor zwei tagen:prije dva dana": ["prekjučer"],
    "früher:prije": ["ranije"],
    "damals:tada": ["tad"],
    "ich werde arbeiten:Radit ću": ["Radiću"],
    "ich werde kommen:Doći ću": ["Ja ću doći"],
    "wir werden sehen:Vidjet ćemo": ["Mi ćemo vidjeti", "Vidjećemo"],
    "ich werde lernen:Učit ću": ["Ja ću učiti", "Učiću"],
    "ich werde dich anrufen:Nazvat ću te": ["Ja ću te nazvati", "Nazvaću te"],   # S-futur, seit 21.11.
    "ich möchte reisen:Želim putovati": ["Želim da putujem"],
    "ich werde es versuchen:Pokušat ću": ["Probat ću", "Ja ću pokušati", "Pokušaću"],
    "ich muss arbeiten:Moram raditi": ["Moram da radim"],
    "ich muss gehen:Moram ići": ["Moram da idem"],
    "ich kann nicht kommen:Ne mogu doći": ["Ne mogu da dođem"],
    "ich will schlafen:Hoću spavati": ["Hoću da spavam"],
    "ich möchte lernen:Želim učiti": ["Želim da učim"],
    "wir müssen warten:Moramo čekati": ["Moramo da čekamo"],
    "versuchen:pokušati": ["probati"],
    "sich freuen:radovati se": ["veseliti se"],
    "ich freue mich:Radujem se": ["Veselim se"],
    "sich treffen:naći se": ["sastati se"],
    "setz dich!:Sjedi!": ["Sjedni!"],
    "beeil dich!:Požuri!": ["Požuri se!"],
    "sich streiten:svađati se": ["prepirati se"],
    "sich sorgen machen:brinuti se": ["sekirati se"],
    "zähne putzen:prati zube": ["četkati zube"],
    "kochen:kuhati": ["kuvati"],
    "ich koche abendessen:Kuham večeru": ["Spremam večeru", "Pravim večeru", "Kuvam večeru"],   # seit 21.11.
    "einkaufen gehen:ići u kupovinu": ["ići u nabavku"],
    "wäsche waschen:prati veš": ["prati rublje"],
    "jeden tag:svaki dan": ["svakog dana", "svakodnevno"],
    "am wochenende:vikendom": ["vikendima"],
    "bild / foto:slika": ["fotografija"],
    "schlechter:gori": ["lošiji"],
    "zu (zu groß):previše": ["suviše"],
    "einige / ein paar:nekoliko": ["par"],
    "ein paar tage:nekoliko dana": ["par dana"],
    "die hälfte:pola": ["polovina"],
    "ein viertel:četvrt": ["četvrtina"],
    "der letzte:zadnji": ["posljednji"],
    "einmal:jednom": ["jedanput", "jedan put"],
    "beide:oboje": ["obadvoje"],
    "das stimmt:To je tačno": ["To je točno", "Točno je"],
    "das stimmt nicht:To nije tačno": ["To nije točno"],
    "wichtig:važno": ["bitno"],
    "ich habe angst:Bojim se": ["Plašim se"],
    "zum glück:srećom": ["na sreću"],
    "ich mache mir sorgen:Brinem se": ["Sekiram se"],
    "flughafen:aerodrom": ["zračna luka"],
    "koffer:kofer": ["kovčeg"],
    "fahrer:vozač": ["šofer"],
    "autobahn:autoput": ["autocesta"],
    "feier:proslava": ["slavlje"],
    "geschenk:poklon": ["dar"],
    "einladung:poziv": ["pozivnica"],
    "ostern:Uskrs": ["Vaskrs"],
    "tanzen:plesati": ["igrati"],
    "musik:muzika": ["glazba"],
    "gastfreundschaft:gostoprimstvo": ["gostoljubivost"],
    "firma:firma": ["kompanija"],
    "maschine:mašina": ["stroj"],
    "beruf:zanimanje": ["profesija"],
    "lehrer:nastavnik": ["učitelj"],
    "schüler:učenik": ["đak"],
    "universität:univerzitet": ["sveučilište"],
    "hausaufgabe:zadaća": ["domaća zadaća"],
    "marktstand:tezga": ["štand"],
    "metzger:mesar": ["kasap"],
    "supermarkt:supermarket": ["market"],
    "fening (1/100 mark):fening": ["pfenig"],
    "kassenbon / quittung:fiskalni račun": ["račun"],
    "kleingeld:sitno": ["sitniš"],
    "banja luka:Banja Luka": ["Banjaluka"],
    "hauptstadt:glavni grad": ["prijestolnica"],
    "ich fahre nach mostar:Idem u Mostar": ["Idem za mostar"],
    "draußen:vani": ["napolju", "vanka"],
    "konditorei:slastičarna": ["slastičarnica", "poslastičarnica"],
    "eine runde noch:Još jednu turu": ["Još jednu rundu"],
    "nachtisch:desert": ["dezert"],
    "behalten sie das rückgeld:Zadržite kusur": ["Zadržite ostatak"],
    "getrennt:odvojeno": ["posebno", "zasebno"],
    "bäckerei:pekara": ["pekarnica"],
    "lecker:ukusno": ["fino"],
    "rahat lokum (geleewürfel zum kaffee):rahat lokum": ["ratluk", "lokum"],
    "einmachglas:tegla": ["staklenka"],
    "korb:korpa": ["košara"],
    "liter:litar": ["litra"],
    "sack:vreća": ["džak"],
    "bohneneintopf:grah": ["pasulj"],
    "geräuchertes fleisch:suho meso": ["suvo meso"],
    "unter der eisenglocke:ispod sača": ["pod sačem"],
    "ausland:inostranstvo": ["inozemstvo"],
    "die niederlande:Holandija": ["Nizozemska"],
    "die schweiz:Švicarska": ["Švajcarska"],
    "muttersprache:maternji jezik": ["materinji jezik", "materinski jezik"],
    "was bedeutet das?:Šta to znači?": ["Što to znači?"],
    "antwort auf selam alejkum:Alejkumu selam": ["Ve alejkumu selam"],
    "danke für alles:Hvala na svemu": ["Hvala za sve"],
    "grüß dich (muslimischer gruß):Selam alejkum": ["Selamun alejkum", "Es-selamu alejkum"],
    "ich entschuldige mich:Izvinjavam se": ["Ispričavam se"],
    "sich bedanken:zahvaliti se": ["zahvaliti"],
    "sich entschuldigen:izviniti se": ["ispričati se"],
    "wir kennen uns:Poznajemo se": ["Znamo se"],
    "freundeskreis / die clique:raja": ["društvo"],
    "akkordeon:harmonika": ["akordeon"],
    "volksmusik:narodna muzika": ["narodna glazba"],
    "selbstverständlich:Naravno": ["Svakako"],
    "gemeinde / gemeindeamt:općina": ["opština"],
    "personalausweis:lična karta": ["osobna iskaznica"],
    "reisepass:pasoš": ["putovnica"],
    "stempel:pečat": ["štambilj"],
    "kopie:kopija": ["fotokopija"],
    "anwalt:advokat": ["odvjetnik"],
    "notar:notar": ["bilježnik", "javni bilježnik"],
    "botschaft:ambasada": ["veleposlanstvo"],
    "kontoauszug:izvod": ["izvadak"],
    "wechselkurs:kurs": ["tečaj"],
    "euro:euro": ["evro"],
    "grundstück:zemljište": ["parcela"],
    "stockwerk:sprat": ["kat"],
    "lebenslauf:biografija": ["životopis"],
    "rente:penzija": ["mirovina"],
    "zeugnis:svjedočanstvo": ["svjedodžba"],
    "facharzt:specijalista": ["specijalist"],
    "zahnarzt:zubar": ["stomatolog"],
    "blutdruck:krvni pritisak": ["krvni tlak"],
    "ich brauche einen termin:Trebam termin": ["Treba mi termin"],
    "finden:naći": ["pronaći"],
    "was schaust du dir da an?:Šta to gledaš?": ["Što to gledaš?"],
    "begreifen / kapieren:shvatiti": ["skontati"],
    "erfahren:saznati": ["doznati"],
    "angst haben / sich fürchten:bojati se": ["plašiti se"],
    "ich habe es geschafft!:Uspjela sam!": ["Uspjelo mi je!"],
    "was ist passiert?:Šta se desilo?": ["Šta je bilo?", "Što se desilo?", "Što je bilo?", "Što se dogodilo?"],
    "benutzen:koristiti": ["upotrebljavati"],
    "was machst du beruflich?:Čime se baviš?": ["Šta si po zanimanju?"],
    "stellen / legen / tun:staviti": ["metnuti"],
    "sitzen:sjediti": ["sjedjeti"],
    "sich hinlegen:leći": ["legnuti"],
    "sterben:umrijeti": ["preminuti"],
    "interessieren:zanimati": ["interesovati", "interesirati"],
    "abhängen:zavisiti": ["ovisiti"],
    "heiraten (frau):udati se": ["vjenčati se"],
    "heiraten (mann):oženiti se": ["vjenčati se"],
    "ausschalten / ausmachen:gasiti": ["isključivati"],
    "kochen:skuhati": ["skuvati"],
    "liefern:dostaviti": ["isporučiti"],
    "einkauf:kupovina": ["kupnja"],
    "lieferung:dostava": ["isporuka"],
    "bestellung:narudžba": ["narudžbina", "porudžbina"],
    "wert sein / gelten:vrijediti": ["važiti"],
    "geldschein:novčanica": ["banknota"],
    "erfahren:saznavati": ["doznavati"],
    "bemerken:primjećivati": ["opažati", "uočavati"],
    "sagen / mitteilen:kazati": ["reći"],
    "betonen:naglasiti": ["istaći"],
    "betonen:naglašavati": ["isticati"],
    "anheben / aufheben (umgangssprachlich):dići": ["dignuti"],
    "bauen:izgraditi": ["sagraditi"],
    "ermöglichen:omogućavati": ["omogućivati"],
    "respektieren:poštovati": ["poštivati"],
    "ähneln:ličiti": ["sličiti"],
    "sich treffen (verabredet):sastati se": ["naći se"],
    "verteidigen:odbraniti": ["obraniti"],
    "verursachen:izazvati": ["uzrokovati", "prouzrokovati"],
    "verursachen:izazivati": ["uzrokovati"],
    "ausfüllen:popuniti": ["ispuniti"],
    "sich verlaufen:izgubiti se": ["zalutati"],
    "sich verletzen:povrijediti se": ["ozlijediti se"],
    "sich erkälten:prehladiti se": ["nahladiti se"],
    "hilfe!:Upomoć!": ["Pomozite!"],
    "krankenwagen / rettung:hitna": ["hitna pomoć"],
    "feuerwehr:vatrogasci": ["vatrogasna služba"],
    "unfall / unglück:nesreća": ["udes", "nezgoda"],
    "verletzung:povreda": ["ozljeda"],
    "dieb:lopov": ["kradljivac"],
    "lang:dug": ["dugačak", "dugačka", "dugačko"],
    "eng / schmal:uzak": ["tijesan", "tijesna", "tijesno"],
    "stark:jak": ["snažan", "snažna", "snažno"],
    "anders:drugačiji": ["drukčiji", "drukčija", "drukčije"],
    "richtig / genau:tačan": ["točan", "točna", "točno"],
    "trocken:suh": ["suv", "suva", "suvo"],
    "falsch:pogrešan": ["netačan", "kriv", "netačna", "kriva", "netačno", "krivo"],
    "nötig:potreban": ["nužan", "nužna", "nužno"],
    "besonders:poseban": ["specijalan", "specijalna", "specijalno"],
    "gewöhnlich / normal:običan": ["normalan", "normalna", "normalno"],
    "kompliziert:komplikovan": ["komplicirana", "komplicirano"],
    "fleißig:vrijedan": ["marljiv", "marljiva", "marljivo"],
    "höflich / anständig:pristojan": ["uljudan", "uljudna", "uljudno"],
    "egoistisch:sebičan": ["egoističan", "egoistična", "egoistično"],
    "ruhig / gelassen:smiren": ["miran", "mirna", "mirno"],
    "frech / unverschämt:bezobrazan": ["drzak", "drska", "drsko"],
    "schüchtern:stidljiv": ["sramežljiva", "sramežljivo"],
    "gefühl:osjećaj": ["osjećanje"],
    "viel glück!:Sretno!": ["Puno sreće!"],
    "verängstigt / erschrocken:uplašen": ["prestrašen", "prestrašena", "prestrašeno"],
    "bemerken:primijetiti": ["opaziti", "uočiti"],
    "probieren / kosten:probati": ["kušati"],
    "dunkel:taman": ["mračan", "mračna", "mračno"],
    "dunkelheit:mrak": ["tama"],
    "anfassen:dirati": ["dodirivati"],
    "grippe:gripa": ["grip"],
    "diabetes:dijabetes": ["šećerna bolest"],
    "spritze:injekcija": ["šprica"],
    "tablette:tableta": ["pilula"],
    "zigarette:cigareta": ["cigara"],
    "moment / augenblick:trenutak": ["tren"],
    "vormittag:prijepodne": ["dopodne"],
    "vorgestern:prekjučer": ["prekjuče"],
    "ich komme sofort!:Odmah dolazim!": ["Dolazim odmah!"],
    "endlich:konačno": ["najzad"],
    "spiel (match):utakmica": ["meč"],
    "mannschaft:ekipa": ["momčad"],
    "tor (treffer):gol": ["pogodak"],
    "wer hat das tor geschossen?:Ko je dao gol?": ["Ko je zabio gol?", "Ko je postigao gol?",
                                                   "Tko je dao gol?"],   # seit 21.11.
    "üben / trainieren:vježbati": ["trenirati"],
    "theater:pozorište": ["kazalište"],
    "reservieren:rezervisati": ["rezervirati"],
    "fahrplan:red vožnje": ["vozni red"],
    "fehler:greška": ["pogreška"],
    "heft:sveska": ["bilježnica"],
    "zählen:brojati": ["brojiti"],
    "was studierst du?:Šta studiraš?": ["Što studiraš?"],
    "installateur / klempner:vodoinstalater": ["instalater"],
    "angestellter / beamter:službenik": ["činovnik"],
    "rentner:penzioner": ["umirovljenik"],
    "entfernung:udaljenost": ["razdaljina"],
    "länge:dužina": ["duljina"],
    "betrag:iznos": ["suma"],
    "hälfte:polovina": ["polovica", "pola"],
    "viertel (ein viertel von etwas):četvrtina": ["četvrt"],
    "million:milion": ["milijun"],
    "haufen:gomila": ["hrpa"],
    "niveau / ebene:nivo": ["razina"],
    "zeitraum:period": ["razdoblje"],
    "jahrzehnt:decenija": ["desetljeće"],
    "bedeutung (wichtigkeit):značaj": ["važnost"],
    "aufmerksamkeit:pažnja": ["pozornost"],
    "wirklichkeit:stvarnost": ["realnost"],
    "vorgehen / verfahren:postupak": ["procedura"],
    "form:oblik": ["forma"],
    "pflicht / verpflichtung:obaveza": ["obveza"],
    "unterstützung:podrška": ["potpora"],
    "sicherheit:sigurnost": ["bezbjednost"],
    "bursche / fester freund:momak": ["mladić"],
    "persönlichkeit:ličnost": ["osobnost"],
    "fachmann:stručnjak": ["ekspert"],
    "respekt:poštovanje": ["respekt"],
    "scherz:šala": ["vic"],
    "partei:stranka": ["partija"],
    "armee:vojska": ["armija"],
    "konflikt:sukob": ["konflikt"],
    "mord:ubistvo": ["ubojstvo"],
    "erlaubnis:dozvola": ["dopuštenje"],
    "unternehmen:kompanija": ["tvrtka", "firma"],
    "wirtschaft:privreda": ["gospodarstvo", "ekonomija"],
    "direktor:direktor": ["ravnatelj"],
    "gerät:uređaj": ["aparat"],
    "schriftsteller:pisac": ["književnik"],
    "gruppe:grupa": ["skupina"],
    "system:sistem": ["sustav"],
    "ausgezeichnet:odličan": ["izvrstan", "izvrsna", "izvrsno"],
    "insgesamt / alles zusammen:ukupno": ["sveukupno"],
    "letzter (in einer reihe):posljednji": ["zadnji", "zadnja", "zadnje"],
    "nächster:sljedeći": ["idući", "naredni", "iduća", "naredna", "iduće", "naredno"],
    "jetzig:sadašnji": ["trenutni", "trenutna", "trenutno"],
    "regelmäßig:redovan": ["redovit", "redovita", "redovito"],
    "örtlich / lokal:lokalni": ["mjesni", "mjesna", "mjesno"],
    "innerer:unutrašnji": ["unutarnji", "unutarnja", "unutarnje"],
    "stark / kräftig:snažan": ["jak", "jaka", "jako"],
    "modern:moderan": ["suvremen", "suvremena", "suvremeno"],
    "riesig:ogroman": ["golem", "golema", "golemo"],
    "manchmal / früher:nekad": ["nekoć"],
    "plötzlich:odjednom": ["iznenada", "najednom"],
    "momentan / gerade:trenutno": ["trenutačno", "momentalno"],
    "fast / bald:skoro": ["uskoro", "gotovo"],
    "ganz (völlig):sasvim": ["skroz", "potpuno", "posve"],
    "auf keinen fall / gar nicht:nikako": ["nipošto"],
    "ein wenig:pomalo": ["malo"],
    "ungefähr:otprilike": ["približno"],
    "gerade / genau:baš": ["upravo", "tačno"],
    "wenigstens:bar": ["makar"],
    "auch nicht / nicht einmal:ni": ["niti"],
    "wirklich / tatsächlich:zaista": ["stvarno", "doista", "uistinu"],
    "meistens / hauptsächlich:uglavnom": ["većinom"],
    "wahrscheinlich:vjerovatno": ["vjerojatno"],
    "auf jeden fall:svakako": ["u svakom slučaju"],
    "obwohl:iako": ["mada", "premda"],
    "falls:ukoliko": ["u slučaju da"],
    "da / nachdem:pošto": ["budući da", "nakon što"],
    "während:tokom": ["u toku", "za vrijeme", "tijekom"],
    "vor (direkt davor):pred": ["ispred"],
    "zwischen / unter (mehreren):među": ["između"],
    "außer:osim": ["izuzev", "sem"],
    "außerhalb:izvan": ["van"],
    "wegen / um … willen:radi": ["zbog"],
    "sich:sebe": ["se"],
    "jemand:neko": ["netko"],
    "jeder (person):svako": ["svatko"],
    "grundlage:osnova": ["osnov", "baza"],
    "einklang:sklad": ["harmonija"],
    "prinzip:princip": ["načelo"],
    "faktor:faktor": ["čimbenik"],
    "fundament:temelj": ["fundament"],
    "merkmal:karakteristika": ["obilježje", "značajka"],
    "typ:tip": ["vrsta"],
    "gebrauch:upotreba": ["korištenje", "uporaba"],
    "einzelheit:detalj": ["pojedinost"],
    "wichtigkeit:važnost": ["značaj"],
    "vorrang / priorität:prioritet": ["prednost"],
    "wirkung (effekt):efekat": ["učinak"],
    "ausnahme:izuzetak": ["iznimka"],
    "erkenntnis:saznanje": ["spoznaja"],
    "beobachten:posmatrati": ["promatrati"],
    "verursachen (ursache sein):uzrokovati": ["prouzrokovati", "izazvati"],
    "sich bemühen (bestrebt sein):nastojati": ["truditi se"],
    "abmachung:dogovor": ["sporazum"],
    "eindruck:utisak": ["dojam"],
    "diskutieren:raspravljati": ["diskutovati"],
    "bestreiten:negirati": ["poricati", "osporavati"],
    "bestehen auf:insistirati": ["inzistirati"],
    "obgleich:mada": ["iako", "premda"],
    "doch (gehoben):no": ["ali"],
    "noch (weder … noch):niti": ["ni"],
    "daher:stoga": ["zato", "zbog toga"],
    "außerdem:osim toga": ["pored toga", "uz to", "sem toga"],   # seit 21.11.
    "bevor:prije nego što": ["prije no što"],
    "daraufhin:potom": ["zatim", "nakon toga"],
    "zugleich:ujedno": ["istovremeno"],
    "über (gehoben):nad": ["iznad"],
    "trotz:uprkos": ["unatoč"],
    "mithilfe:pomoću": ["uz pomoć"],
    "außerordentlich:izuzetno": ["izvanredno", "iznimno"],
    "gleichzeitig:istovremeno": ["u isto vrijeme", "istodobno"],
    "vor allem:naročito": ["prije svega", "posebno", "osobito"],
    "erheblich:znatno": ["značajno"],
    "ziemlich:prilično": ["poprilično", "dosta"],
    "in erster linie:prvenstveno": ["prije svega", "primarno"],
    "offensichtlich:očigledno": ["očito"],
    "praktisch (so gut wie):praktično": ["praktički"],
    "persönlich:lično": ["osobno"],
    "grundlegend / grund-:osnovni": ["temeljni", "temeljna", "temeljno"],
    "entscheidend (schlüssel-):ključan": ["presudan", "presudna", "presudno"],
    "unabhängig:nezavisan": ["neovisan", "neovisna", "neovisno"],
    "aktuell:aktuelan": ["aktualan", "aktualna", "aktualno"],
    "die jugendlichen:omladina": ["mladi", "mladež"],
    "herkunft:porijeklo": ["podrijetlo"],
    "generation:generacija": ["naraštaj"],
    "haushalt:domaćinstvo": ["kućanstvo"],
    "schwiegertochter:snaha": ["snaja"],
    "schwiegermutter (mutter der frau):punica": ["tašta"],
    "schwiegervater (vater der frau):punac": ["tast"],
    "ehepartner:supružnik": ["bračni drug"],
    "zorn:bijes": ["gnjev"],
    "schlägerei:tuča": ["tučnjava"],
    "spannung (zwischen menschen):napetost": ["tenzija"],
    "verzeihen:opraštati": ["praštati"],
    "schande:sramota": ["bruka"],
    "nerven:nervirati": ["živcirati"],
    "nerven:iznervirati": ["naživcirati"],
    "geduld:strpljenje": ["strpljivost"],
    "versterben:preminuti": ["umrijeti"],
    "verstorben:pokojni": ["preminuli", "preminula", "preminulo"],
    "trennen:odvojiti": ["razdvojiti"],
    "trennen:odvajati": ["razdvajati"],
    "zusammenarbeit:saradnja": ["suradnja"],
    "bericht:izvještaj": ["izvješće"],
    "das leiten / steuern:upravljanje": ["vođenje"],
    "kunde (klient):klijent": ["mušterija"],
    "führung (einer firma):rukovodstvo": ["vodstvo"],
    "manager:menadžer": ["rukovodilac"],
    "mitarbeiter:saradnik": ["suradnik"],
    "leiten / steuern:upravljati": ["rukovoditi"],
    "gründen:osnovati": ["utemeljiti"],
    "zusammenarbeiten:sarađivati": ["surađivati"],
    "beschaffung:nabavka": ["nabava"],
    "werk (betrieb):pogon": ["postrojenje"],
    "auslieferung:isporuka": ["dostava"],
    "transport:transport": ["prijevoz", "prevoz"],
    "lager:skladište": ["magacin"],
    "bereitstellen:obezbijediti": ["osigurati"],
    "bereitstellen:obezbjeđivati": ["osiguravati"],
    "budget:budžet": ["proračun"],
    "finanziell:finansijski": ["financijski", "financijska", "financijsko"],
    "finanzierung:finansiranje": ["financiranje"],
    "finanzieren:finansirati": ["financirati"],
    "kaution / einlage:depozit": ["kaucija"],
    "gewinn (einer firma):dobit": ["profit"],
    "prognose:prognoza": ["predviđanje"],
    "entschädigung:nadoknada": ["kompenzacija", "naknada"],
    "bilanz:bilans": ["bilanca"],
    "insolvenz:stečaj": ["bankrot"],
    "wirtschaftlich:ekonomski": ["gospodarski", "gospodarska", "gospodarsko"],
    "wirtschafts-:privredni": ["gospodarski", "gospodarska", "gospodarsko"],
    "aktie:dionica": ["akcija"],
    "investor:investitor": ["ulagač"],
    "börse:berza": ["burza"],
    "effizient:efikasan": ["učinkovit", "učinkovita", "učinkovito"],
    "stellenausschreibung:konkurs": ["natječaj"],
    "aufstieg (im beruf):napredovanje": ["unapređenje"],
    "verpflichtend:obavezan": ["obvezan", "obvezna", "obvezno"],
    "abwesenheit / freistellung:odsustvo": ["odsutnost"],
    "zeitschrift:časopis": ["magazin"],
    "aufnahme (video, foto):snimak": ["snimka"],
    "marke (produkt):brend": ["marka"],
    "das werben / inserieren:oglašavanje": ["reklamiranje"],
    "bühne / szene:scena": ["pozornica", "bina"],
    "musik-:muzički": ["glazbeni", "glazbena", "glazbeno"],
    "feierlichkeit:svečanost": ["ceremonija"],
    "eintrittskarte:ulaznica": ["karta"],
    "zeitgenössisch / modern:savremen": ["suvremen", "suvremena", "suvremeno"],
    "literatur:književnost": ["literatura"],
    "bibliothek:biblioteka": ["knjižnica"],
    "dichtung / poesie:poezija": ["pjesništvo"],
    "erbe (kulturell):baština": ["nasljeđe"],
    "historisch:historijski": ["povijesni", "istorijski", "povijesna", "istorijska", "povijesno", "istorijsko"],
    "osmanisch:osmanski": ["otomanski", "otomanska", "otomansko"],
    "aufstand:ustanak": ["pobuna"],
    "burg / schloss:dvorac": ["zamak"],
    "historiker:historičar": ["povjesničar", "istoričar"],
    "atom- / nuklear:nuklearni": ["atomski", "atomska", "atomsko"],
    "weltall:svemir": ["kosmos"],
    "verschmutzung:zagađenje": ["onečišćenje"],
    "ansteckung / infektion:zaraza": ["infekcija"],
    "link:link": ["poveznica"],
    "elektronisch:elektronski": ["elektronički", "elektronička", "elektroničko"],
    "suche:pretraga": ["pretraživanje"],
    "löschen (daten):izbrisati": ["obrisati"],
    "suchmaschine:pretraživač": ["tražilica"],
    "abstimmen / wählen:glasati": ["glasovati"],
    "wähler:birač": ["glasač"],
    "waffenstillstand:primirje": ["prekid vatre"],
    "verband / verein:udruženje": ["udruga"],
    "interesse:interes": ["interesovanje"],
    "bevölkerung:stanovništvo": ["populacija"],
    "sünde:grijeh": ["gunah"],
    "gnade:milost": ["rahmet"],
    "paradies (muslimisch):džennet": ["dženet"],
    "hölle (muslimisch):džehennem": ["džehenem"],
    "strafrechtlich:krivični": ["kazneni", "kaznena", "kazneno"],
    "justiz:pravosuđe": ["sudstvo"],
    "kriminalität:kriminal": ["kriminalitet"],
    "tatverdächtiger:osumnjičeni": ["osumnjičenik"],
    "festnahme:hapšenje": ["uhićenje"],
    "festnehmen:uhapsiti": ["uhititi"],
    "zustimmung:saglasnost": ["pristanak", "suglasnost"],
    "befehl / anordnung:naredba": ["naređenje"],
    "gelten:važiti": ["vrijediti"],
    "verlängern:produžiti": ["produljiti"],
    "verlängern:produžavati": ["produljivati"],
    "verzeichnis:popis": ["spisak"],
    "liste:spisak": ["lista", "popis"],
    "briefumschlag:koverta": ["omotnica"],
    "darlehen / anleihe:zajam": ["pozajmica"],
    "darlehen (privat):pozajmica": ["zajam"],
    "kassierer:blagajnik": ["kasir"],
    "bürge:žirant": ["jamac", "garant"],
    "knopf:dugme": ["gumb"],
    "schornstein:dimnjak": ["odžak"],
    "esszimmer:trpezarija": ["blagovaonica"],
    "treppenhaus:stepenište": ["stubište"],
    "fleck:mrlja": ["fleka"],
    "bau (bauen):gradnja": ["izgradnja"],
    "renovieren:renovirati": ["obnoviti"],
    "ziegelstein:cigla": ["opeka"],
    "parzelle:parcela": ["plac"],
    "verlängerung:produženje": ["produljenje"],
    "hochhaus:neboder": ["soliter"],
    "zelle:ćelija": ["stanica"],
    "ader:žila": ["vena"],
    "wirbelsäule:kičma": ["kralježnica"],
    "corona:korona": ["kovid", "covid"],
    "chronisch:hroničan": ["kroničan", "kronična", "kronično"],
    "cholesterin:holesterol": ["kolesterol"],
    "taub:gluh": ["gluv", "gluva", "gluvo"],
    "fettleibigkeit:gojaznost": ["pretilost"],
    "lungenentzündung:upala pluća": ["pneumonija"],
    "chirurgie:hirurgija": ["kirurgija"],
    "chirurg:hirurg": ["kirurg"],
    "hebamme:babica": ["primalja"],
    "ertragen / erleiden:pretrpjeti": ["podnijeti"],
    "gedächtnis:pamćenje": ["memorija"],
    "wettbewerb:takmičenje": ["natjecanje"],
    "punkt (wertung):bod": ["poen"],
    "meister (titelträger):prvak": ["šampion"],
    "trainieren:trenirati": ["vježbati"],
    "sportler:sportista": ["sportaš"],
    "wetteifern / antreten:takmičiti se": ["natjecati se"],
    "eiweiß:protein": ["bjelančevina"],
    "nahrhaft:hranjiv": ["hranljiv", "hranljiva", "hranljivo"],
    "appetit:apetit": ["tek"],
    "wandtafel:tabla": ["ploča"],
    "entschuldigung (schule):opravdanje": ["ispričnica"],
    "sammlung:zbirka": ["kolekcija"],
    "aufsatz (essay):esej": ["sastav"],
    "zusammenfassung:sažetak": ["rezime"],
    "geografie:geografija": ["zemljopis"],
    "experiment:eksperiment": ["pokus"],
    "erfinden:izmisliti": ["izumiti"],
    "deutung:tumačenje": ["interpretacija"],
    "fantasie:mašta": ["fantazija"],
    "abkürzung:skraćenica": ["kratica"],
    "dialekt:dijalekt": ["narječje"],
    "kommunizieren:komunicirati": ["komunikovati"],
    "bemerkung:primjedba": ["opaska"],
    "debatte:debata": ["rasprava", "diskusija"],
    "schild (z. b. verkehrsschild):tablica": ["znak"],
    "ausführlich:detaljan": ["podroban", "podrobna", "podrobno"],
    "vielschichtig:složen": ["kompleksan", "kompleksna", "kompleksno"],
    "theoretisch:teorijski": ["teoretski", "teoretska", "teoretsko"],
    "klären:razjasniti": ["pojasniti"],
    "große halle:dvorana": ["hala"],
    "zentrum (mitte):središte": ["centar"],
    "motorrad:motocikl": ["motor"],
    "kurve:krivina": ["zavoj"],
    "automobil:automobil": ["auto"],
    "autounfall:udes": ["nesreća"],
    "campingplatz:kamp": ["kamping"],
    "reiseziel:destinacija": ["odredište"],
    "erdboden:tlo": ["zemlja"],
    "morgendämmerung:zora": ["svitanje"],
    "insekt:insekt": ["kukac"],
    "delfin:delfin": ["dupin"],
    "kamel:deva": ["kamila"],
    "baumstamm / baum:stablo": ["deblo", "drvo"],
    "bewältigen / meistern:savladati": ["svladati"],
    "bewältigen / meistern:savladavati": ["svladavati"],
    "beenden:okončati": ["završiti"],
    "sich kümmern (um etwas):pobrinuti se": ["postarati se"],
    "fördern / verbessern:unaprijediti": ["poboljšati"],
    "fördern / verbessern:unapređivati": ["poboljšavati"],
    "zusammentragen:prikupiti": ["sakupiti"],
    "zusammentragen:prikupljati": ["sakupljati"],
    "zwingen / treiben:natjerati": ["prisiliti"],
    "sich entschuldigen:izvinjavati se": ["ispričavati se"],
    "druck:pritisak": ["tlak"],
    "form (kondition):forma": ["kondicija"],
    "offenbar:očito": ["očigledno"],
    "wenigstens / auch wenn:makar": ["barem", "bar"],
    "größtenteils:većinom": ["uglavnom"],
    "generell:generalno": ["općenito"],
    "wörtlich:doslovno": ["bukvalno"],
    "annähernd:približno": ["otprilike"],
    "vergeblich:uzalud": ["zaludu"],
    "zweifellos:nesumnjivo": ["nedvojbeno"],
    "direkt:direktno": ["izravno"],
    "gegenseitig:međusobno": ["uzajamno"],
    "richtig (regelgerecht):pravilno": ["ispravno"],
    "schlicht und einfach:naprosto": ["jednostavno"],
    "täglich / alltäglich:svakodnevno": ["dnevno"],
    "zunächst / zuerst:najprije": ["prvo"],
    "unaufhörlich:neprestano": ["neprekidno"],
    "in zukunft:ubuduće": ["u budućnosti"],
    "schließlich:najzad": ["napokon", "konačno"],
    "tagsüber:danju": ["preko dana"],
    "überall:svugdje": ["posvuda"],
    "gegenüber:nasuprot": ["preko puta"],
    "anderswo:drugdje": ["negdje drugo"],
    "wunderschön:divan": ["prekrasan", "prekrasna", "prekrasno"],
    "außergewöhnlich:izuzetan": ["izniman", "iznimna"],
    "unglaublich:nevjerovatan": ["nevjerojatan", "nevjerojatna", "nevjerojatno"],
    "berühmt:čuven": ["slavan", "slavna", "slavno"],
    "geeignet:pogodan": ["prikladan", "prikladna", "prikladno"],
    "notwendig:nužan": ["neophodan", "neophodna", "neophodno"],
    "entsetzlich:užasan": ["grozan", "grozna", "grozno"],
    "komplett / vollständig:kompletan": ["potpun", "potpuna", "potpuno"],
    "unter anderem:između ostalog": ["među ostalim"],
    "so bald wie möglich:što prije": ["čim prije"],
    "prozent:posto": ["postotak", "procenat"],
    "fehlbestand / knappheit:manjak": ["nestašica"],
    "za|vilica": ["čeljust"],
    "za|upala desni": ["upala zubnog mesa"],
    "za|zubni konac": ["konac za zube"],
}

# Lückensatz: Text -> zusätzliche Antworten
LUECKEN = {
    "Jednu ___, molim.": ["kafu", "kavu"],
    "Moj ___ je dobar čovjek.": ["susjed"],
    "___ za pasoš je trideset maraka.": ["Naknada"],
    "Pijem ___.": ["kafu", "kavu"],
    "Volim svoju ___.": ["mamu"],
    "Pomažem ___.": ["mami"],
    "Kečap i ___, molim.": ["gorušicu"],
    "Uzet ću ___.": ["somun"],
    "Voda je u ___.": ["boci"],
    "Koja je ___ za WiFi?": ["lozinka"],
    "Švicarska je mala ___.": ["zemlja"],
    # Tabelle 2c. „Hvala ___!“ (Nr. 32) und „Pitam se ___ li dolazi.“ (Nr. 31)
    # haben ein "auch" am Lückensatz in vokabeln.py, kein Paar hier.
    "Djeca ne vole ___.": ["spanać"],                        # 10
    "Kolika je ___ mjesečno?": ["stanarina", "najamnina"],   # 16
    "Svi ___ su došli.": ["musafiri"],                       # 37
    "Idem u ___.": ["kasapnicu"],                            # 37
    # Dritte Runde (Ajdin, 14.11.2026 abends, Offen-Liste 5a)
    "___, molim Vas.": ["Oprostite"],
    "Supa je u ___.": ["šerpi"],
    # Fragen vom 15.11.2026 (Ajdin abends, 9b)
    "Putujemo ___.": ["kolima", "automobilom"],
    # K2 Wort-Alternativen (Ajdin K2, 20.11.2026)
    "Januar, ___, mart": ["veljača"],
    "Poslije maja dolazi ___.": ["jun", "lipanj"],
    "___ je zadnji mjesec u godini.": ["Prosinac"],
    "Moj ___ se zove Ajdin.": ["suprug"],
    "Gdje je ___?": ["pekarnica"],
    "Koliko ___?": ["je"],
    "Ja ___ bosanski.": ["pričam"],
    "Šta si po ___?": ["profesiji"],
    "Moja ___ stanuje u selu.": ["nena"],
    "Imate li ___?": ["putovnicu"],
    "___ si?": ["Otkuda", "Otkud"],
    "___ je to?": ["Što"],
    "___ ideš?": ["Kamo"],
    "Nemam vremena ___ radim.": ["zato što", "pošto"],
    "Volim kahvu, ___ ne volim čaj.": ["a"],
    "___ pada kiša, ostajem kod kuće.": ["Ukoliko"],
    "Ne znam kada ___ autobus.": ["stiže"],
    "Poslije posla ___ večeru.": ["kuvam"],
    "Koliko traje ___?": ["put"],
    "Imam ___ za tebe.": ["dar"],
    "U supi je ___.": ["šargarepa"],
    "Na stolu su ___.": ["pečurke"],
    "Danas jedem ___.": ["cvjetaču"],
    "Krava je u ___.": ["staji"],
    "Malo ___ spava.": ["kuče"],
    "Vidi, ___!": ["slap"],
    "Idemo na ___.": ["brežuljak"],
    "U ___ je hladno.": ["špilji"],
    "Ovo je moj ___.": ["tanjur"],
    "Deka je na ___.": ["sofi"],
    "Sutra ___ veš.": ["glačam"],
    "Veš je na ___.": ["konopcu"],
    "Gdje mogu ___ svoj auto?": ["parkovati"],
    "Jabuke su na ___.": ["sniženju", "popustu"],
    "Danas jedemo ___.": ["pasulj"],
    "Zadržite ___.": ["ostatak"],
    "Moj brat radi u ___.": ["inozemstvu"],
    "Nana svira ___.": ["akordeon"],
}

# Satzbau: Satz -> was zu "ohne" dazukommt. Fast alles sperrte die App schon
# über "auch" und " / " der Wörter (kahva / kafa, majka mit auch mama); neu
# ist puno neben mnogo.
KACHELN = {
    "Kako si, mama?": ["majka"],
    "Kahva je crna.": ["kafa"],
    "Mama je u kuhinji.": ["majka"],
    "Doktor je u bolnici.": ["ljekar"],
    "Brz oporavak, mama!": ["majka"],
    "Kahva je u džezvi.": ["kafa"],
    "Uzet ću pogaču.": ["somun"],
    "Koja je šifra za WiFi?": ["lozinka"],
    "Moja mama voli kruške.": ["majka"],
    "Moja majka i moj babo.": ["mama"],
    "Kahva bez šećera.": ["kafa"],
    "Kahva bez mlijeka.": ["kafa"],
    "Ima mnogo djece": ["puno"],
    "Na pijaci ima mnogo ljudi.": ["puno"],
    "Kahva sa šećerom.": ["kafa"],
    "Kahva je jako vruća.": ["kafa", "snažno", "vruće"],
    "Može li jedna kahva?": ["kafa"],
    "Švicarska je mala država.": ["zemlja"],
    "Moja majka je Bosanka.": ["mama"],
    "Taksa za pasoš je trideset maraka.": ["naknada"],
    # Tabelle 2c: gesperrt wird in beide Richtungen. Hier ist plaća das Verb
    # („zahlt“) und oprosti „verzeih“ - plata und izvini als falsche Kachel
    # wären harmlos, die Sperre kostet nur eine Auswahl. izvini liegt wegen
    # KACHEL_VERWECHSELBAR ohnehin nie als Kachel.
    "Svako plaća svoje": ["plata"],
    "Molim te, oprosti mi.": ["izvini"],
    # K2 Wort-Alternativen (Ajdin K2, 20.11.2026): die andere Form liegt nie als falsche Kachel da
    "Ja se zovem Amina.": ["sebe"],
    "Kako se zoveš?": ["sebe"],
    "Ja govorim malo bosanski": ["pomalo"],
    "Vidimo se sutra!": ["sebe"],
    "Vidimo se u petak!": ["sebe"],
    "Danas je hladno.": ["hladan", "hladna"],
    "Voda je hladna.": ["hladno"],
    "Nebo je plavo.": ["plava"],
    "Gdje je stanica?": ["ćelija"],
    "Koliko košta hljeb?": ["je"],
    "Šta si radio?": ["što"],
    "Sviđa mi se": ["sebe"],
    "prašak za pecivo": ["deterdžent"],
    "Malo štene spava.": ["pomalo"],
    "Ja se bojim pasa": ["sebe"],
    "U pećini je hladno.": ["hladan", "hladna"],
    "Idemo na brdo.": ["hajmo"],
    "Ne radi bojler.": ["zbog"],
    "Na semaforu je crveno.": ["crvena"],
    "Gdje mogu parkirati svoj auto?": ["automobil"],
    "Ne radi mašina za suđe.": ["zbog"],
    "Šta je to?": ["što"],
    "Danas je hladno i pada kiša.": ["hladan", "hladna"],
    "Nemam vremena jer radim.": ["pošto"],
    "Volim kahvu, ali ne volim čaj.": ["no"],
    "Moja sestra se zove Amina.": ["sebe"],
    "Moj muž se zove Ajdin.": ["sebe", "suprug"],
    "Čuvaj se od psa!": ["sebe"],
    "s mojom ženom": ["sa"],
    "Hladno mi je": ["hladan", "hladna"],
    "govoriti o poslu": ["pričati"],
    "Idem s bratom u grad.": ["sa"],
    "Idemo vozom u Mostar.": ["hajmo"],
    "Pijem kahvu s mlijekom.": ["sa"],
    "Sljedeće godine idemo u Bosnu.": ["hajmo"],
    "Moram sipati gorivo.": ["benzin"],
    "Mogu govoriti bosanski": ["pričati"],
    "Osjećam se dobro.": ["sebe"],
    "Nalazimo se u pet.": ["sebe"],
    "Djeca se igraju.": ["sebe"],
    "Ne sjećam se.": ["sebe"],
    "Kako se osjećaš?": ["sebe"],
    "Radujem se vikendu.": ["sebe"],
    "Učim bosanski svaki dan.": ["svakodnevno"],
    "Svaki dan pijem kahvu.": ["svakodnevno"],
    "Auto je brži od bicikla.": ["automobil"],
    "Decembar je zadnji mjesec u godini.": ["posljednji"],
    "Prvi put sam u Sarajevu.": ["vožnja"],
    "Slažem se s tobom.": ["sa", "sebe"],
    "Ne slažem se": ["sebe"],
    "To je tačno": ["baš"],
    "To nije tačno": ["baš"],
    "Drago mi je zbog tebe": ["radi"],
    "Koliko traje vožnja?": ["put"],
    "Gdje je autobuska stanica?": ["ćelija"],
    "Taksi čeka ispred hotela.": ["pred"],
    "Šta si po zanimanju?": ["što"],
    "Moj brat radi u fabrici.": ["zbog"],
    "Pitam se da li on dolazi.": ["sebe"],
    "Ako pada kiša, ostajem kod kuće.": ["ukoliko"],
    "Moj babo ne radi u julu": ["zbog"],
    "Ja razumijem malo bosanski": ["pomalo"],
    "Vidimo se u subotu": ["sebe"],
    "Moj brat je stariji od mene, ali manji": ["no"],
    "Gdje je moj kusur?": ["ostatak"],
    "Ja živim u Sarajevu": ["stanujem"],
    "Mi idemo u kafić.": ["hajmo"],
    "Možemo li platiti odvojeno?": ["posebno"],
    "Ovo je jako ukusno.": ["snažno"],
    "Idemo u restoran.": ["hajmo"],
    "Jedna porcija je dosta.": ["dovoljno", "prilično"],
    "Idemo na kahvu": ["hajmo"],
    "Živim u Njemačkoj.": ["stanujem"],
    "Moj brat radi u inostranstvu.": ["zbog"],
    "Moj muž je Nijemac.": ["suprug"],
    "Kako se to kaže na bosanskom?": ["sebe"],
    "Drago mi je što smo se upoznali": ["sebe", "šta"],
    "Ova sevdalinka je jako lijepa.": ["snažno"],
    "Idemo na iftar kod nane.": ["hajmo"],
    "Bilo je jako ukusno": ["snažno"],
    "Koliko košta kuća?": ["je"],
}


def _woerter(daten):
    for kat in daten["kategorien"] + daten["zahnarzt"]["kategorien"]:
        yield from kat["words"]


def test_liste_und_kennungen_sauber(grunddaten):
    assert varianten.pruefe_varianten(grunddaten) == []
    assert varianten.pruefe_kennungen(grunddaten) == []


def test_schreibaufgaben_genau_so(alle_daten):
    """In jeder Sprache dieselben - das Bosnische wird nie übersetzt."""
    for code, daten in alle_daten.items():
        assert {w["id"]: w["auch_var"] for w in _woerter(daten) if "auch_var" in w} == WOERTER, code


def test_lueckensaetze_genau_so(alle_daten):
    for code, daten in alle_daten.items():
        assert {s["text"]: s["auch_var"] for s in daten["saetze"] if "auch_var" in s} == LUECKEN, code


def test_satzbau_sperrt_genau_so(grunddaten):
    import vokabeln
    vorher = {s["bs"]: list(s.get("ohne") or []) for s in inhalt.satzbau_fuer_app(vokabeln.SATZBAU)}
    neu = {}
    for s in grunddaten["satzbau"]:
        alt = vorher[s["bs"]]
        assert s.get("ohne", [])[:len(alt)] == alt, s["bs"]      # was die Autoren sperren, bleibt vorn
        if s.get("ohne", []) != alt:
            neu[s["bs"]] = s["ohne"][len(alt):]
    assert neu == KACHELN


def test_nur_was_getippt_wird_und_nichts_doppelt(grunddaten):
    for w in _woerter(grunddaten):
        if "auch_var" not in w:
            continue
        assert varianten.tippbar(w["bs"]), w["bs"]
        da = {x.lower() for x in [w["bs"]] + list(w.get("auch") or [])}
        for v in w["auch_var"]:
            assert " / " not in v and v == v.strip() and v.lower() not in da, (w["bs"], v)
    for s in grunddaten["saetze"]:
        for v in s.get("auch_var", []):
            assert " / " not in v and v.lower() not in {s["answer"].lower()} | {a.lower() for a in s.get("auch", [])}


def test_was_ajdin_ausgeschlossen_hat_bleibt_draussen(grunddaten, wurzel):
    """zaehlt_nicht der Wortschatz-Pakete (tests/test_paket10.py bis 20): Ajdin hat
    diese Formen beim Tippen ausdrücklich nicht freigegeben."""
    verboten = set()
    for pfad in glob.glob(os.path.join(wurzel, "tests", "test_paket*.py")):
        baum = ast.parse(io.open(pfad, encoding="utf-8").read())
        for knoten in baum.body:
            if isinstance(knoten, ast.Assign) and any(getattr(z, "id", "") == "ZAEHLT_NICHT" for z in knoten.targets):
                for formen in ast.literal_eval(knoten.value).values():
                    # tests/test_paket3.py schreibt eine Form allein ("prsa": "grudi"). Bis
                    # zum 20.11.2026 kamen hier deren Buchstaben an (g, r, u ...), und mit K2
                    # stießen a und s an „___ ne volim čaj“ (ali -> a) und sa -> s.
                    verboten |= {f.lower() for f in ([formen] if isinstance(formen, str) else formen)}
    assert len(verboten) > 10, verboten
    alle = [v.lower() for w in _woerter(grunddaten) for v in w.get("auch_var", [])]
    alle += [v.lower() for s in grunddaten["saetze"] for v in s.get("auch_var", [])]
    assert not verboten & set(alle)
    gebeugt = {f.lower() for p in varianten.VARIANTEN for f in varianten.faelle(p["b"]).values()}
    assert not verboten & gebeugt


# --- der Mechanismus an kleinen Beispielen ---

def _z(antworten, wort=True, kennung="x", fall=None):
    mehr, probleme = varianten.zusatz(antworten, kennung, wort, fall=fall)
    return mehr, probleme


@pytest.mark.parametrize("antwort, wort, mehr", [
    ("flaša", True, ["boca"]),
    ("Daj mi flašu", True, ["Daj mi bocu"]),             # gebeugt, mitten im Satz
    ("Flašu", False, ["Bocu"]),                          # Großschreibung bleibt
    ("Voda je u flaši.", True, ["Voda je u boci."]),
    ("flašica", True, []),                               # nur ganze Wörter
    ("kahvana", True, []),
    ("kahva-bar", True, []),                             # Bindestrich hält zusammen
    ("komšija", True, ["susjed"]),                       # allein: der Nominativ
    ("komšije", True, ["susjedi"]),                      # Gen. Sg. oder Nom. Pl. - allein Nom. Pl.
    ("dva puta dnevno", True, ["dvaput dnevno"]),        # zwei Wörter
    ("dva", True, []),
    ("roza", True, ["ružičasta"]),                       # ALLEIN
    ("roza haljina", True, []),
    ("roza", False, []),                                 # ALLEIN nie im Lückensatz
    ("veče", True, []),                                  # nur von a nach b (večer -> veče)
    ("Dobro veče", True, ["Dobra večer"]),               # Tabelle 2c Nr. 34, die ganze Wendung
    ("Pijem kafu", True, []),
    ("Pijem kahvu sada", True, ["Pijem kahvu sad", "Pijem kafu sada", "Pijem kafu sad",
                                "Pijem kavu sada", "Pijem kavu sad"]),          # kava seit K2 (20.11.2026)
    ("senf", True, []),                                  # Paar mit Kennungen: nur dort
    ("šifra", False, []),
    ("taksi", True, []),                                 # das Taxi, nicht taksa
    # Tabelle 2c (14.11.2026): mehrere Paare mit demselben a
    ("kafena", True, ["smeđa", "kahvena", "braon"]),
    ("kafena haljina", True, ["smeđa haljina", "kahvena haljina"]),      # braon nur allein
    ("kafena kesa", True, ["kafena vrećica", "smeđa kesa", "smeđa vrećica", "kahvena kesa", "kahvena vrećica"]),
    ("bosanski lonac", True, []),                        # šerpa nur beim Wort allein
    ("jelovnik", True, []),                              # meni nur bei „Speisekarte“
    ("meni", True, []),                                  # nur von a nach b: „mir“ nimmt nie jelovnik
    ("Nemam novca", True, []),                           # para nur an „Nemam novca“ (Kennung)
    ("u autu", True, []),                                # kolima nur an „u autu“ (Kennung)
    ("Imam auto", True, []),                             # kola nur an auto und „Imam auto“
    ("autom", True, []),                                 # kolima nur an „mit dem Auto“ und „Putujemo ___.“
    ("auto oca", True, []),                              # kola oca nur an „das Auto des Vaters“
    ("očev auto", True, []),                             # očeva kola nur dort
    ("Pas me je ujeo", True, []),                        # Kuče me je ujelo seit dem 16.11.2026 nirgends
    ("Čuvaj se psa!", True, []),
    ("plati", True, []),                                 # das Verb, nicht plata
])
def test_zusatz_an_beispielen(antwort, wort, mehr):
    assert _z([antwort], wort) == (mehr, [])


def test_zusatz_fall_und_kennung():
    # komšija im Lückensatz: Nom. Sg. (susjed) oder Gen. Pl. (susjeda) - ohne Fall nichts, aber ein Befund
    mehr, probleme = _z(["komšija"], False)
    assert mehr == [] and len(probleme) == 1 and "FALL angeben" in probleme[0]
    assert _z(["komšija"], False, fall="sg_nom") == (["susjed"], [])
    assert _z(["komšija"], False, fall="pl_gen") == (["susjeda"], [])
    assert _z(["flaši"], False) == (["boci"], [])          # Dat. und Lok. - beides boci
    assert _z(["šifra"], False, kennung="Koja je ___ za WiFi?") == (["lozinka"], [])
    assert _z(["senf"], True, kennung="senf:senf") == (["gorušica"], [])
    assert _z(["senf"], False, kennung="Kečap i ___, molim.", fall="sg_akk") == (["gorušicu"], [])


def test_kennungen_der_gefaehrlichen_paare():
    """meni, kola, pare, sahat, tikva, šipak, ujesti und promet heißen auch etwas
    anderes. Sie gelten nur am einen Wort der App, nie umgekehrt."""
    for a, b, kennung in (("jelovnik", "meni", "speisekarte:jelovnik"), ("auto", "kola", "auto:auto"),
                          ("novac", "pare", "geld:novac"), ("sat", "sahat", "stunde / uhr:sat"),
                          ("bundeva", "tikva", "kürbis:bundeva"), ("nar", "šipak", "granatapfel:nar"),
                          ("ugristi", "ujesti", "beißen:ugristi"), ("saobraćaj", "promet", "verkehr:saobraćaj")):
        assert _z([a], True, kennung=kennung) == ([b] + K2_DAZU.get(a, []), []), a
        assert _z([a], True) == ([], []), a                 # an jedem anderen Wort nichts
        assert _z([b], True, kennung=kennung) == ([], []), b
        paare = [p for p in varianten.VARIANTEN if varianten.faelle(p["a"]).get("grund") == a]
        assert [p["gilt"] for p in paare] == [[kennung] + SAETZE_DRITTE_RUNDE.get(a, [])], a


# Dritte Runde (14.11.2026 abends): „Imam kola“ - das Paar auto / kola gilt auch dort.
# Fragen vom 15.11.2026 (9d, 9e): novac / pare auch in „podići novac“ und „uplatiti novac“.
# „auto oca“ hat ein eigenes Paar (die ganze Wendung), das bleibt hier draußen.
SAETZE_DRITTE_RUNDE = {"auto": ["ich habe ein auto:Imam auto"],
                       "novac": ["geld abheben:podići novac", "geld einzahlen:uplatiti novac"]}
# K2 (Ajdin K2, 20.11.2026): automobil zählt an den auto-Stellen mit, auch nur mit
# Kennungen (auto, Imam auto, u autu, autom, „Putujemo ___.“). Bei „Das Auto des Vaters“
# seit dem 21.11.2026 über die ganze Wendung: automobil oca (und očev automobil).
K2_DAZU = {"auto": ["automobil"], "autom": ["automobilom"], "auto oca": ["automobil oca"]}


def test_dasselbe_paar_zweimal_ist_ein_befund(monkeypatch):
    """Dasselbe a darf mehrere b haben (kafena), aber nicht zweimal dasselbe b."""
    monkeypatch.setattr(varianten, "VARIANTEN", [
        {"a": "kafena", "b": "braon", "gilt": varianten.ALLEIN, "beleg": "x"},
        {"a": "kafena", "b": "kahvena", "gilt": varianten.ALLEIN, "beleg": "x"},
        {"a": "kafena", "b": "braon", "gilt": varianten.UEBERALL, "beleg": "x"}])
    probleme = varianten.pruefe_varianten({"kategorien": [], "saetze": []})
    assert probleme == ["Variante kafena / braon: 'kafena' -> 'braon' steht schon bei einem anderen Paar"]


def test_hoechstens_zwei_woerter_je_antwort():
    mehr, probleme = _z(["sada kahvu flašu"], True)
    assert mehr == [] and len(probleme) == 1


def test_befund_bei_wort_mit_anderer_bedeutung():
    """Eine Form von a, die die App als eigenes Wort kennt, meldet pruefe_varianten()."""
    daten = {"kategorien": [{"id": "x", "words": [
        {"id": "küken:kahvu", "bs": "kahvu", "de": "Küken"},
        {"id": "tisch:sada", "bs": "sada", "de": "Tisch"}, {"id": "jetzt:sada", "bs": "sada", "de": "jetzt"},
        {"id": "nie / niemals:nikad", "bs": "nikad", "de": "nie / niemals"},
        {"id": "nie:nikad", "bs": "nikad", "de": "nie"}]}],
        "saetze": []}
    probleme = varianten.pruefe_varianten(daten)
    assert any("'kahvu' ist in der App ein eigenes Wort" in p for p in probleme), probleme
    assert any("'sada' steht in der App bei Wörtern mit verschiedener Bedeutung" in p for p in probleme), probleme
    assert not any("'nikad'" in p for p in probleme), probleme     # „nie“ steckt in beiden Bedeutungen


def test_paare_beugen_gleich():
    for p in varianten.VARIANTEN:
        a, b = varianten.faelle(p["a"]), varianten.faelle(p["b"])
        assert set(a) == set(b), p["beleg"]


# --- die App hängt sie an ---

def _html(index_html):
    return index_html.replace("\r\n", "\n")


def test_app_haengt_sie_an_beiden_tippstellen_an(index_html):
    html = _html(index_html)
    assert "return [w.bs, ...gleich, ...(w.auch || []), ...(w.auch_var || [])];" in html
    assert "const antworten = [s.answer, ...(s.auch || []), ...(s.auch_var || [])].join(' / ');" in html
    assert "const _auchAlle = w => [...(w.auch || []), ...(w.auch_var || [])];" in html
    # in geschwister() für beide Richtungen, dazu einmal beim Bau des Verzeichnisses
    # (wortIndex(), seit 20.11.2026, Optimierung Punkt 2)
    assert html.count("_auchAlle(") == 3
    # kachelAblenker() nimmt "ohne" wie bisher
    assert "...(s.ohne || []).map(kachelNorm)" in html


def test_tippbar_wie_in_der_app(index_html):
    """varianten.tippbar() ist typable() aus web/index.html. Ändert sich das
    eine, muss das andere mit - sonst fehlen Varianten oder stehen umsonst da."""
    assert "const typable = w => w.bs.length<=14 && !/[.…→]/.test(w.bs) && !w.bs.includes(' / ');" in _html(index_html)
    assert varianten.TIPPBAR_LAENGE == 14 and varianten.NIE_TIPPBAR.pattern == "[.…→]"


# --- matches() aus web/index.html in node, mit dem echten Inhalt ---

def _stueck(html, anfang, ende):
    assert html.count(anfang) == 1, anfang
    a = html.index(anfang)
    return html[a:html.index(ende, a)]


NODE = r"""
const ein = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const f = new Function(ein.bloecke + '\nreturn {matches, zahlWert, fastRichtig};')();
process.stdout.write(JSON.stringify({
  faelle: ein.faelle.map(([eingabe, antworten]) => f.matches(eingabe, antworten)),
  zahlen: ein.zahlen.map(x => f.zahlWert(x)),
}));
"""

ZAHLEN = {"dvadeset jedan": 21, "dvadeset i jedan": 21, "Trideset i pet": 35, "devedeset i devet": 99,
          "dvadeset i": None, "i jedan": None, "pet i dva": None, "sto i jedan": None, "dvadeset i i jedan": None,
          "dvadeset ili jedan": None,
          # K2 (Ajdin K2, 20.11.2026): dvjesta neben dvjesto, beide 200 (ZAHL_SONDER)
          "dvjesto": 200, "dvjesta": 200, "Dvjesta": 200, "dvjesta pet": None}


@pytest.fixture(scope="module")
def node_ergebnis(index_html, grunddaten):
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    html = _html(index_html)
    bloecke = "\n".join([
        _stueck(html, "const strip = s =>", "\n/* ---------- Gesprochenes vergleichen"),
        _stueck(html, "const ZAHL_EINER = ", "\n/* ---- Zahlen, die wechseln"),
        _stueck(html, "function matches(guess, answer){", "\n/* ---------- Fast richtig: erst ein Hinweis"),
        _stueck(html, "function einTippfehler(a, b){", "\n/* So lange nach dem Hinweis"),
    ])
    faelle = []
    for w in _woerter(grunddaten):
        if "auch_var" in w:
            vorher = [w["bs"]] + list(w.get("auch") or [])
            for v in w["auch_var"]:
                faelle.append((v, " / ".join(vorher), "no"))                      # bis 12.11.2026
                faelle.append((v, " / ".join(vorher + w["auch_var"]), "ok"))      # jetzt
    for s in grunddaten["saetze"]:
        if "auch_var" in s:
            vorher = [s["answer"]] + list(s.get("auch") or [])
            for v in s["auch_var"]:
                faelle.append((v, " / ".join(vorher), "no"))
                faelle.append((v, " / ".join(vorher + s["auch_var"]), "ok"))
    # Nichts anderes wird richtig: andere Fälle des anderen Wortes, das andere Wort im Lückensatz
    for eingabe, wort in (("bocu", "flaša"), ("boce", "flaša"), ("susjeda", "komšija"), ("susjed", "komšije"),
                          ("Pijem kafa", "Pijem kahvu"), ("kafu", "jedna kahva")):
        w = next(x for x in _woerter(grunddaten) if x["bs"] == wort)
        faelle.append((eingabe, " / ".join([w["bs"]] + w.get("auch", []) + w["auch_var"]), "no"))
    for eingabe, text in (("boca", "Voda je u ___."), ("susjeda", "Moj ___ je dobar čovjek."),
                          ("kafa", "Pijem ___."), ("mama", "Volim svoju ___."), ("gorušica", "Kečap i ___, molim.")):
        s = next(x for x in grunddaten["saetze"] if x["text"] == text)
        faelle.append((eingabe, " / ".join([s["answer"]] + s.get("auch", []) + s["auch_var"]), "no"))
    ein = {"bloecke": bloecke, "faelle": [f[:2] for f in faelle], "zahlen": list(ZAHLEN)}
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps(ein), capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=120)
    erg = json.loads(aus.stdout)
    return faelle, erg


def test_matches_vorher_falsch_jetzt_richtig(node_ergebnis):
    faelle, erg = node_ergebnis
    assert len(faelle) > 100
    falsch = [(f, r) for f, r in zip(faelle, erg["faelle"]) if f[2] != r]
    assert falsch == []


def test_zahlen_mit_und(node_ergebnis):
    """dvadeset jedan / dvadeset i jedan: bs-Web 156 / 193. In zahlWert(), damit
    es für jede Zahl gilt, beim Tippen wie beim Sprechen."""
    _, erg = node_ergebnis
    assert dict(zip(ZAHLEN, erg["zahlen"])) == ZAHLEN


def test_zahl_mit_und_in_matches(index_html):
    html = _html(index_html)
    assert "if(teile.length === 3 && teile[1] === 'i') teile.splice(1, 1);" in html
    assert re.search(r"const zg = zahlWert\(g\);", html)


# --- Tabelle 2c (Ajdin, 14.11.2026, Prüfbericht 1.4, F6) in matches() ---

# Je Zeile der Tabelle mindestens ein Beispiel: ("w", Kennung des Wortes) für die
# Schreibaufgabe, ("l", Text) für den Lückensatz, dazu die Eingabe. Bis dahin
# falsch ("no"), jetzt richtig ("ok"). Nr. 30 (Gdje) gehört zu F7, Nr. 38
# (tisuća) bleibt, wie es war.
TABELLE_2C = {
    1: [("w", "brot:hljeb", "kruh"), ("w", "es gibt kein brot:Nema hljeba", "Nema kruha")],
    2: [("w", "suppe:supa", "juha")],
    3: [("w", "gehalt:plata", "plaća"), ("w", "nettogehalt:neto plata", "neto plaća")],
    4: [("w", "langsam:polako", "polahko")],
    5: [("w", "minute:minuta", "minut")],
    6: [("w", "gestern:jučer", "juče")],
    7: [("w", "woche:sedmica", "hefta"), ("w", "letzte woche:prošle sedmice", "prošle hefte")],
    8: [("w", "topf:lonac", "šerpa")],
    9: [("w", "pfanne:tava", "tiganj")],
    10: [("w", "spinat:špinat", "spanać"), ("l", "Djeca ne vole ___.", "spanać")],
    11: [("w", "garten:bašta", "bašča")],
    12: [("w", "tochter:kćerka", "kći"), ("w", "tochter:kćerka", "kćer")],
    13: [("w", "stunde / uhr:sat", "sahat")],
    14: [("w", "geschichte (fach):historija", "povijest")],
    15: [("w", "besuch:posjeta", "posjet")],
    16: [("w", "miete:kirija", "stanarina"), ("l", "Kolika je ___ mjesečno?", "najamnina")],
    17: [("w", "kühlschrank:frižider", "hladnjak"), ("w", "backofen:rerna", "pećnica"),
         ("w", "tüte / plastiktüte:kesa", "vrećica"), ("w", "essig:sirće", "ocat"),
         ("w", "zimmerdecke:plafon", "strop"), ("w", "fabrik:fabrika", "tvornica"),
         ("w", "aprikose:kajsija", "marelica"), ("w", "lauch:praziluk", "poriluk"),
         ("w", "handtuch:peškir", "ručnik")],
    18: [("w", "laden:prodavnica", "radnja"), ("w", "geschäft:radnja", "prodavnica")],
    19: [("w", "hof (am haus):dvorište", "avlija"), ("w", "hof / innenhof:avlija", "dvorište")],
    20: [("w", "manchmal:ponekad", "nekad")],
    21: [("w", "braun:kafena", "braon"), ("w", "braun:kafena", "kahvena")],
    22: [("w", "kaffeetasse (traditionell):fildžan", "findžan")],
    23: [("w", "auto:auto", "kola")],
    24: [("w", "geld:novac", "pare")],
    25: [("w", "handy:mobitel", "mobilni")],
    26: [("w", "markt:pijaca", "pazar")],
    27: [("w", "speisekarte:jelovnik", "meni")],
    28: [("w", "formular:obrazac", "formular")],
    29: [("w", "entschuldigung (du):Izvini", "Oprosti")],
    31: [("w", "ob:da li", "je li"), ("l", "Pitam se ___ li dolazi.", "je")],
    32: [("w", "vielen dank:Hvala puno", "Puno hvala"), ("w", "vielen dank:Hvala puno", "Hvala lijepa"),
         ("w", "vielen dank:Hvala puno", "Hvala mnogo"), ("w", "vielen dank:Hvala puno", "Mnogo hvala"),
         ("l", "Hvala ___!", "lijepa"), ("l", "Hvala ___!", "mnogo")],
    33: [("w", "auf wiedersehen:Doviđenja", "Do viđenja")],
    34: [("w", "guten abend:Dobro veče", "Dobra večer")],
    35: [("w", "am abend:navečer", "uveče"), ("w", "am morgen:ujutro", "ujutru")],
    36: [("w", "bei meinem freund:kod prijatelja", "kod druga"), ("w", "anrede: freund!:prijatelju!", "druže!")],
    37: [("w", "fenster:prozor", "pendžer"), ("w", "wand:zid", "duvar"), ("w", "straße:ulica", "sokak"),
         ("w", "schrank:ormar", "dolap"), ("w", "gast:gost", "musafir"), ("l", "Svi ___ su došli.", "musafiri"),
         ("w", "medikament:lijek", "hap"), ("w", "erkältung:prehlada", "nahlada"), ("w", "hefe:kvasac", "germa"),
         ("w", "treppe:stepenice", "basamaci"), ("w", "hund:pas", "kuče"), ("w", "stück:komad", "parče"),
         ("w", "metzgerei:mesnica", "kasapnica"), ("l", "Idem u ___.", "kasapnicu"),
         ("w", "schulferien:raspust", "ferije"), ("w", "decke (bettdecke):deka", "ćebe"),
         ("w", "leiter:merdevine", "skale"), ("w", "haselnuss:lješnjak", "lješnik")],
    39: [("w", "kürbis:bundeva", "tikva"), ("w", "granatapfel:nar", "šipak"), ("w", "beißen:ugristi", "ujesti"),
         ("w", "verkehr:saobraćaj", "promet")],
}

# Bleibt falsch: die andere Richtung, Wörter mit derselben Form und anderer
# Bedeutung, und wo das Wort nicht allein steht, obwohl Geschlecht oder Zahl
# anders sind (Ajdin: „nur wo das Wort allein steht“). Die sechs Sätze, die Ajdin
# in der dritten Runde freigegeben hat („Nemam para“, „u kolima“ …), stehen unten
# bei DRITTE_RUNDE, die neun vom 15.11.2026 („kola oca“, „uplatiti pare“ …) bei
# FRAGEN_15_11.
GEGEN_2C = [
    ("w", "mir:meni / mi", "jelovnik"),                               # meni heißt auch „mir“
    ("w", "mir ist es egal:Svejedno mi je", "Svejedno jelovnik je"),
    ("w", "mir ist es egal:Svejedno mi je", "Jelovnik je svejedno"),
    ("w", "geld:novac", "para"),                                      # pare nur so, wie es allein steht
    ("w", "das auto des vaters:auto oca", "očev kola"),               # „kola oca“ seit den Fragen vom 15.11. (unten)
    ("w", "krankenwagen / rettung:hitna", "auto hitne pomoći"),       # nie von kola nach auto
    ("l", "Koliko je ___?", "sahata"),                                # sahat nur beim Wort sat
    ("l", "Koliko je ___?", "sahati"),
    ("w", "bosnischer schmortopf:bosanski lonac", "bosanska šerpa"),  # šerpa nur am Wort lonac, šerpi in „Supa je u ___.“
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Pas me je ugrizao"),   # nie von ujesti nach ugristi
    ("w", "verkehrs-:saobraćajni", "prometni"),                       # promet nur beim Wort saobraćaj
    ("w", "verzeih mir:Oprosti mi", "Izvini mi"),                     # nie von oprosti nach izvini
    ("w", "manchmal / früher:nekad", "ponekad"),                      # nie von nekad nach ponekad
    ("w", "handel:trgovina", "prodavnica"),                           # trgovina gehört nicht dazu
    ("w", "voll:pun", "mnogo"),                                       # puno → mnogo nur in „Hvala ___!“
    ("w", "dass:da", "je"),                                           # da → je nur in „Pitam se ___ li dolazi.“
    ("l", "Mislim ___ je dobro.", "je"),
    ("w", "nie:nikad", "nekad"),
]


def _antworten_von(daten, art, wer, ohne_neu=False):
    """Alle Antworten, wie die App sie prüft. ohne_neu: so, wie es vor dem
    14.11.2026 war - ohne auch_var und ohne das "auch" der beiden Lückensätze."""
    if art == "w":
        w = next(x for x in _woerter(daten) if x["id"] == wer)
        mehr = [] if ohne_neu else w.get("auch_var", [])
        return " / ".join([w["bs"]] + list(w.get("auch") or []) + mehr)
    s = next(x for x in daten["saetze"] if x["text"] == wer)
    if ohne_neu:
        return s["answer"]
    return " / ".join([s["answer"]] + list(s.get("auch") or []) + list(s.get("auch_var") or []))


@pytest.fixture(scope="module")
def node_2c(index_html, grunddaten):
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    html = _html(index_html)
    bloecke = "\n".join([
        _stueck(html, "const strip = s =>", "\n/* ---------- Gesprochenes vergleichen"),
        _stueck(html, "const ZAHL_EINER = ", "\n/* ---- Zahlen, die wechseln"),
        _stueck(html, "function matches(guess, answer){", "\n/* ---------- Fast richtig: erst ein Hinweis"),
        _stueck(html, "function einTippfehler(a, b){", "\n/* So lange nach dem Hinweis"),
    ])
    faelle = []
    for nr, beispiele in TABELLE_2C.items():
        for art, wer, eingabe in beispiele:
            faelle.append(((nr, art, wer, eingabe, "vorher"), eingabe, _antworten_von(grunddaten, art, wer, True)))
            faelle.append(((nr, art, wer, eingabe, "jetzt"), eingabe, _antworten_von(grunddaten, art, wer)))
    for art, wer, eingabe in GEGEN_2C:
        faelle.append((("gegen", art, wer, eingabe), eingabe, _antworten_von(grunddaten, art, wer)))
    ein = {"bloecke": bloecke, "faelle": [f[1:] for f in faelle], "zahlen": []}
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps(ein), capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=120)
    return dict(zip([f[0] for f in faelle], json.loads(aus.stdout)["faelle"]))


def test_tabelle_2c_jede_zeile_hat_ein_beispiel():
    assert set(TABELLE_2C) == set(range(1, 40)) - {30, 38}


def test_tabelle_2c_vorher_falsch_jetzt_richtig(node_2c):
    falsch = {k: v for k, v in node_2c.items() if k[0] != "gegen" and v != ("no" if k[-1] == "vorher" else "ok")}
    assert falsch == {}


def test_tabelle_2c_nichts_anderes_wird_richtig(node_2c):
    falsch = {k: v for k, v in node_2c.items() if k[0] == "gegen" and v != "no"}
    assert falsch == {}
    assert len([k for k in node_2c if k[0] == "gegen"]) == len(GEGEN_2C)


def test_tisuca_bleibt_tausend(index_html):
    """Tabelle 2c Nr. 38: tisuća gilt weiter als 1000 (Ajdin, 14.11.2026). Seit K2
    (Ajdin K2, 20.11.2026) gilt dvjesta neben dvjesto als 200, siehe ZAHLEN oben."""
    assert ("const ZAHL_SONDER = {jedna:1, jedno:1, dvije:2, dvoje:2, tisuca:1000, dvjesta:200};"
            in _html(index_html))


# --- Dritte Runde (Ajdin, 14.11.2026 abends, Offen-Liste 5a) in matches() ---
# Je „Ja“ in Release\Pruefbericht_1.4.md, „Dritte Runde“: bis dahin falsch, jetzt richtig.
DRITTE_RUNDE = [
    ("w", "entschuldigung (sie):Izvinite", "Oprostite"),               # Oprostite neben Izvinite
    ("l", "___, molim Vas.", "Oprostite"),
    ("w", "manchmal:ponekad", "nekada"),                              # nekada bei ponekad
    # Zweite Form auch in ganzen Sätzen, genau diese sieben Stellen
    ("w", "ich habe ein auto:Imam auto", "Imam kola"),
    ("w", "im auto:u autu", "u kolima"),
    ("w", "ich habe kein geld:Nemam novca", "Nemam para"),
    ("w", "auf dem markt:na pijaci", "na pazaru"),
    ("w", "auf der straße:na ulici", "na sokaku"),
    ("l", "Supa je u ___.", "šerpi"),
    ("w", "er hat einen hund:On ima psa", "On ima kuče"),
]
# Bleibt falsch: die du-Form war nicht gefragt, und nie von oprosti nach izvini.
GEGEN_DRITTE_RUNDE = [
    ("w", "entschuldigung (du):Izvini", "Oprostite"),
    ("w", "entschuldigung (sie):Izvinite", "Oprosti"),
    ("w", "verzeih mir:Oprosti mi", "Oprostite mi"),
    ("l", "Molim te, ___ mi.", "oprostite"),
    ("l", "Molim te, ___ mi.", "izvini"),
    ("w", "manchmal:ponekad", "nikada"),                              # nikada heißt „nie“
    ("w", "nie:nikad", "nekada"),
    ("w", "manchmal / früher:nekad", "ponekad"),                      # nie von nekad nach ponekad
    # Keine weiteren gebeugten Formen: nur die sieben Stellen, nur die genannte Form.
    # autom, „Putujemo ___.“, podići / uplatiti novac, „Tražimo ulicu“ und „Čuvaj se psa!“
    # zählen seit den Fragen vom 15.11. (FRAGEN_15_11 unten), „Pas me je ujeo“ nahm
    # vom 15.11. bis zum 16.11.2026 auch „Kuče me je ujelo“ (FRAGEN_16_11 unten).
    ("w", "ich habe ein auto:Imam auto", "Imam kolima"),
    ("w", "im auto:u autu", "u kola"),
    ("w", "er hat einen hund:On ima psa", "On ima kučeta"),
    ("w", "auf der straße:na ulici", "na sokak"),
    ("w", "auf dem markt:na pijaci", "na pazar"),
    ("w", "geld einzahlen:uplatiti novac", "uplatiti para"),
    ("w", "ich habe angst vor hunden:Bojim se pasa", "Bojim se kučeta"),   # Ajdin: „kučadi“
    ("l", "Na pijaci ima mnogo ___.", "pazaru"),
    ("l", "Koliko je ___?", "sahat"),                                 # „Koliko je sahat?“: Ajdin „Ne“
]


def _node_ja_und_gegen(index_html, grunddaten, ja, gegen):
    """Je „ja“ vorher (ohne auch_var) und jetzt, dazu die Gegenproben, durch das
    echte matches() aus web/index.html."""
    if not shutil.which("node"):
        pytest.skip("node fehlt")
    html = _html(index_html)
    bloecke = "\n".join([
        _stueck(html, "const strip = s =>", "\n/* ---------- Gesprochenes vergleichen"),
        _stueck(html, "const ZAHL_EINER = ", "\n/* ---- Zahlen, die wechseln"),
        _stueck(html, "function matches(guess, answer){", "\n/* ---------- Fast richtig: erst ein Hinweis"),
        _stueck(html, "function einTippfehler(a, b){", "\n/* So lange nach dem Hinweis"),
    ])
    faelle = []
    for art, wer, eingabe in ja:
        faelle.append(((art, wer, eingabe, "vorher"), eingabe, _antworten_von(grunddaten, art, wer, True)))
        faelle.append(((art, wer, eingabe, "jetzt"), eingabe, _antworten_von(grunddaten, art, wer)))
    for art, wer, eingabe in gegen:
        faelle.append((("gegen", art, wer, eingabe), eingabe, _antworten_von(grunddaten, art, wer)))
    ein = {"bloecke": bloecke, "faelle": [f[1:] for f in faelle], "zahlen": []}
    aus = subprocess.run(["node", "-e", NODE], input=json.dumps(ein), capture_output=True, text=True,
                         encoding="utf-8", check=True, timeout=120)
    return dict(zip([f[0] for f in faelle], json.loads(aus.stdout)["faelle"]))


@pytest.fixture(scope="module")
def node_dritte(index_html, grunddaten):
    return _node_ja_und_gegen(index_html, grunddaten, DRITTE_RUNDE, GEGEN_DRITTE_RUNDE)


def test_dritte_runde_vorher_falsch_jetzt_richtig(node_dritte):
    falsch = {k: v for k, v in node_dritte.items() if k[0] != "gegen" and v != ("no" if k[-1] == "vorher" else "ok")}
    assert falsch == {}
    assert len([k for k in node_dritte if k[0] != "gegen"]) == 2 * len(DRITTE_RUNDE)


def test_dritte_runde_nichts_anderes_wird_richtig(node_dritte):
    falsch = {k: v for k, v in node_dritte.items() if k[0] == "gegen" and v != "no"}
    assert falsch == {}
    assert len([k for k in node_dritte if k[0] == "gegen"]) == len(GEGEN_DRITTE_RUNDE)


def test_dritte_runde_nein_bleibt_nein(grunddaten):
    """Ajdin „Ne“: „Koliko je sahat?“ (oben in GEGEN_DRITTE_RUNDE) und „Moja je ovo
    kolegica.“ als andere Wortstellung beim Satzbau."""
    s = [x for x in grunddaten["satzbau"] if x["bs"] == "Ovo je moja kolegica."]
    assert len(s) == 1 and not s[0].get("auch"), s
    luecke = [x for x in grunddaten["saetze"] if x["text"] == "Koliko je ___?"]
    assert len(luecke) == 1 and not luecke[0].get("auch") and not luecke[0].get("auch_var"), luecke


# --- Fragen vom 15.11.2026 (Ajdin abends, 9a bis 9i, Offen-Liste 5d) in matches() ---
# Release\Fragen_Ajdin_2026-11-15.md, „Ajdins Antworten“: „9 ja (alle 9a–9i)“, die Formen
# auf Vorschlag bestätigt. Bis dahin falsch, jetzt richtig - mit genau diesen Formen.
FRAGEN_15_11 = [
    ("w", "mit dem auto:autom", "kolima"),                              # 9a
    ("l", "Putujemo ___.", "kolima"),                                   # 9b
    ("w", "das auto des vaters:auto oca", "kola oca"),                  # 9c
    ("w", "geld abheben:podići novac", "podići pare"),                  # 9d
    ("w", "geld einzahlen:uplatiti novac", "uplatiti pare"),            # 9e
    ("w", "wir suchen die straße:Tražimo ulicu", "Tražimo sokak"),      # 9f
    ("w", "ich habe angst vor hunden:Bojim se pasa", "Bojim se kučadi"),   # 9g
    ("w", "vorsicht vor dem hund!:Čuvaj se psa!", "Čuvaj se kučeta!"),  # 9h
    ("w", "vorsicht vor dem hund!:Čuvaj se psa!", "Čuvaj se kučeta"),   #    ohne Ausrufezeichen wie bisher
    # 9i „Kuče me je ujelo“ hat Ajdin am 16.11.2026 zurückgenommen (8b), siehe FRAGEN_16_11.
]
# Bleibt falsch: andere Fälle, das halbe Paar, und dieselben Formen an anderen Stellen.
GEGEN_FRAGEN_15_11 = [
    ("w", "mit dem auto:autom", "kola"),
    ("l", "Putujemo ___.", "kola"),
    ("w", "ich habe ein auto:Imam auto", "Imam kolima"),
    ("w", "das auto des vaters:auto oca", "očev kola"),                 # aus dem "auch" „očev auto“
    ("w", "geld abheben:podići novac", "podići para"),
    ("w", "geld einzahlen:uplatiti novac", "uplatiti para"),
    ("w", "geld:novac", "para"),
    ("w", "wir suchen die straße:Tražimo ulicu", "Tražimo sokaka"),
    ("w", "wir suchen die straße:Tražimo ulicu", "Tražimo sokaku"),
    ("w", "auf der straße:na ulici", "na sokak"),
    ("w", "ich habe angst vor hunden:Bojim se pasa", "Bojim se kučeta"),
    ("w", "ich habe angst vor hunden:Bojim se pasa", "Bojim se kuče"),
    ("w", "vorsicht vor dem hund!:Čuvaj se psa!", "Čuvaj se kuče!"),
    ("w", "vorsicht vor dem hund!:Čuvaj se psa!", "Čuvaj se kučadi!"),
    ("w", "er hat einen hund:On ima psa", "On ima kučeta"),
    ("w", "er hat einen hund:On ima psa", "On ima kučadi"),
    ("w", "hund:pas", "kučadi"),
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Kuče me je ujeo"),     # das Verb wandert mit
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Pas me je ujelo"),
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Ujelo me je kuče"),    # andere Stellung nicht gefragt
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Pas me je ugrizao"),
    ("w", "beißen:ugristi", "ujelo"),
]


@pytest.fixture(scope="module")
def node_fragen_15_11(index_html, grunddaten):
    return _node_ja_und_gegen(index_html, grunddaten, FRAGEN_15_11, GEGEN_FRAGEN_15_11)


def test_fragen_15_11_vorher_falsch_jetzt_richtig(node_fragen_15_11):
    falsch = {k: v for k, v in node_fragen_15_11.items()
              if k[0] != "gegen" and v != ("no" if k[-1] == "vorher" else "ok")}
    assert falsch == {}
    assert len([k for k in node_fragen_15_11 if k[0] != "gegen"]) == 2 * len(FRAGEN_15_11)


def test_fragen_15_11_nichts_anderes_wird_richtig(node_fragen_15_11):
    falsch = {k: v for k, v in node_fragen_15_11.items() if k[0] == "gegen" and v != "no"}
    assert falsch == {}
    assert len([k for k in node_fragen_15_11 if k[0] == "gegen"]) == len(GEGEN_FRAGEN_15_11)


def test_fragen_15_11_nur_an_ihrer_stelle():
    """Jedes neue Paar gilt nur an der Stelle, nach der gefragt war."""
    stellen = {("autom", "kolima"): ["mit dem auto:autom", "Putujemo ___."],
               ("auto oca", "kola oca"): ["das auto des vaters:auto oca"],
               ("ulicu", "sokak"): ["wir suchen die straße:Tražimo ulicu"],
               ("pasa", "kučadi"): ["ich habe angst vor hunden:Bojim se pasa"],
               ("psa", "kučeta"): ["vorsicht vor dem hund!:Čuvaj se psa!"]}
    gefunden = {(p["a"], p["b"]): p["gilt"] for p in varianten.VARIANTEN
                if isinstance(p["a"], str) and (p["a"], p["b"]) in stellen}
    assert gefunden == stellen
    for (a, b), gilt in stellen.items():
        assert _z([a], True) == ([], []), a                                 # anderswo nichts
        assert _z([a], True, kennung=gilt[0]) == ([b] + K2_DAZU.get(a, []), []), a


# --- Fragen vom 16.11.2026 (Ajdin, 8a und 8b, Offen-Liste 6) in matches() ---
# Release\Fragen_Ajdin_2026-11-16.md, „Ajdins Antworten“: 8a „očeva kola“ zählt auch,
# „očev auto“ bleibt. 8b „nimm nur pas aber beide“: bei „Der Hund hat mich gebissen“
# nur „Pas me je ujeo“ und „Ujeo me je pas“, die kuče-Form vom 15.11. (9i) fällt weg.
FRAGEN_16_11 = [
    ("w", "das auto des vaters:auto oca", "očeva kola"),                # 8a
    ("w", "das auto des vaters:auto oca", "Očeva kola"),
]
# Bleibt oder wird falsch: očev kola, die kuče-Formen bei „Der Hund hat mich gebissen“.
GEGEN_FRAGEN_16_11 = [
    ("w", "das auto des vaters:auto oca", "očev kola"),
    ("w", "das auto des vaters:auto oca", "očeva auto"),
    ("w", "das auto des vaters:auto oca", "kola očeva"),
    ("w", "ich habe ein auto:Imam auto", "Imam očeva kola"),
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Kuče me je ujelo."),   # 8b, bis 16.11. richtig
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Kuče me je ujelo"),
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Ujelo me je kuče"),
    ("w", "der hund hat mich gebissen:Pas me je ujeo", "Kuče me je ujeo"),
]
# Richtig: das Wort selbst und, seit dem 16.11.2026, sein "auch" „Ujeo me je pas“ (vorher nur
# beim Satzbau als andere Reihenfolge, beim Tippen falsch).
NUR_PAS = ["Pas me je ujeo", "Ujeo me je pas", "Pas me je ujeo.", "ujeo me je pas"]


@pytest.fixture(scope="module")
def node_fragen_16_11(index_html, grunddaten):
    ja = FRAGEN_16_11 + [("w", "der hund hat mich gebissen:Pas me je ujeo", x) for x in NUR_PAS]
    return _node_ja_und_gegen(index_html, grunddaten, ja, GEGEN_FRAGEN_16_11)


def test_fragen_16_11_oceva_kola_vorher_falsch_jetzt_richtig(node_fragen_16_11):
    for art, wer, eingabe in FRAGEN_16_11:
        assert node_fragen_16_11[(art, wer, eingabe, "vorher")] == "no", eingabe
        assert node_fragen_16_11[(art, wer, eingabe, "jetzt")] == "ok", eingabe


def test_fragen_16_11_beide_pas_formen_zaehlen(node_fragen_16_11):
    """Beide pas-Formen gelten, mit und ohne auch_var: sie stehen in bs und "auch", nicht
    in einem Paar von varianten.py."""
    for eingabe in NUR_PAS:
        for wann in ("vorher", "jetzt"):
            assert node_fragen_16_11[("w", "der hund hat mich gebissen:Pas me je ujeo", eingabe, wann)] == "ok", \
                (eingabe, wann)


def test_fragen_16_11_nichts_anderes_wird_richtig(node_fragen_16_11):
    falsch = {k: v for k, v in node_fragen_16_11.items() if k[0] == "gegen" and v != "no"}
    assert falsch == {}
    assert len([k for k in node_fragen_16_11 if k[0] == "gegen"]) == len(GEGEN_FRAGEN_16_11)


def test_fragen_16_11_paare(grunddaten):
    """8a: genau ein neues Paar, nur am "auch" „očev auto“ von „Das Auto des Vaters“.
    8b: kein Paar mehr nach kuče me je ujelo, die anderen kuče-Paare bleiben."""
    paare = {(p["a"], p["b"]): p for p in varianten.VARIANTEN if isinstance(p["a"], str)}
    p = paare[("očev auto", "očeva kola")]
    assert p["gilt"] == ["das auto des vaters:auto oca"]
    assert p["beleg"].startswith("Fragen 16.11.2026, 8a/8b")
    assert _z(["očev auto"], True) == ([], [])
    # očev automobil seit dem 21.11.2026 (K2 auto -> automobil am "auch", eigenes Paar)
    assert _z(["očev auto"], True, kennung="das auto des vaters:auto oca") == (["očeva kola", "očev automobil"], [])
    assert not [k for k in paare if "ujelo" in k[1] or "ujeo" in k[0]]
    # štene -> kuče seit K2 (Ajdin K2, 20.11.2026, V1-104): nur beim Welpen, „kuce ist nur
    # welpe kein ausgewachsener hund“.
    assert {k for k in paare if k[1].startswith("kuč")} == {
        ("pas", "kuče"), ("psa", "kuče"), ("pasa", "kučadi"), ("psa", "kučeta"), ("štene", "kuče")}
    assert paare[("štene", "kuče")]["gilt"] == ["welpe:štene", "Malo ___ spava."]
    w = next(x for x in _woerter(grunddaten) if x["id"] == "der hund hat mich gebissen:Pas me je ujeo")
    assert w["bs"] == "Pas me je ujeo" and w.get("auch") == ["Ujeo me je pas"] and "auch_var" not in w


# --- K2 Wort-Alternativen (Ajdin K2, 20.11.2026): die Neins ---
# Release\Wortschatz\k2_2026-11-20\antworten_ajdin_2026-11-20.txt: 190 Karten, 149 ja und
# 41 nein. Die Ja-Paare stehen in varianten.py (oben in WOERTER, LUECKEN, KACHELN), jedes
# Nein hier mit der Eingabe, die das Paar richtig gemacht hätte (final/abgelehnt_final.json,
# mit dem echten Code ausgerechnet). Sie bleiben falsch, auch wenn später jemand ein Paar
# vorschlägt. Bei V1-96 (dušo) schrieb Ajdin „es kommt auf dem kontext an aber eigentlich
# nein“. S-ekavisch und S-dole waren Sammelfragen: keine ekavischen Formen, kein dole.
# Die Paket-Wörter darunter stehen zusätzlich als ZAEHLT_NICHT in ihrem Paket-Test.
GEGEN_K2 = [
    ("w", "hallo:Merhaba", "Bok"),                                                      # V1-78
    ("w", "hallo (neutral, überall):Zdravo", "Bok"),
    ("w", "tschüss:Ćao", "Bok"),
    ("w", "gern geschehen:Nema na čemu", "Molim"),                                      # V1-80
    ("w", "freut mich:Drago mi je", "Milo mi je"),                                      # V1-82
    ("w", "ćevapi:ćevapi", "ćevapčići"),                                                # V1-86
    ("w", "tante (schwester von vater oder mutter):tetka", "teta"),                     # V1-87
    ("w", "schatz (anrede):dušo", "ljubavi"),                                           # V1-96
    ("w", "schatz (anrede):dušo", "srce"),
    ("w", "blätterteig:jufka", "kore"),                                                 # V1-101
    ("w", "drache:zmaj", "aždaja"),                                                     # V1-105
    ("w", "wildschwein:divlja svinja", "vepar"),                                        # V1-106
    ("w", "hausmeister:domar", "hausmajstor"),                                          # V2-81
    ("w", "verlängerungskabel:produžni kabel", "produžni"),                             # V2-112
    ("w", "personalausweis:lična karta", "osobna karta"),                               # V3-65
    ("w", "gute reise!:Sretan put!", "Srećan put!"),                                    # V3-86
    ("w", "frohes bajram!:Sretan Bajram!", "Srećan Bajram!"),
    ("w", "viel glück!:Sretno!", "Srećno!"),
    ("w", "braut:mlada", "nevjesta"),                                                   # V3-95
    ("w", "ramadan:Ramazan", "Ramadan"),                                                # V3-96
    ("w", "hochzeit:svadba", "vjenčanje"),                                              # V3-97
    ("w", "antwort auf selam alejkum:Alejkumu selam", "Alejkum selam"),                 # V3-101
    ("w", "sieben ćevapi:sedam ćevapa", "sedam ćevapčića"),                             # V3-112
    ("w", "zum ersten mal:prvi put", "po prvi put"),                                    # V3-114
    ("w", "sich erinnern / einfallen:sjetiti se", "prisjetiti se"),                     # V4-3
    ("w", "sich ärgern:ljutiti se", "nervirati se"),                                    # V4-32
    ("w", "einschalten / anmachen:paliti", "uključivati"),                              # V4-33
    ("w", "schlaganfall:moždani udar", "šlog"),                                         # V5-3
    ("w", "blauer fleck:modrica", "masnica"),                                           # V5-4
    ("w", "kindergarten:vrtić", "obdanište"),                                           # V5-21
    ("w", "zentrum:centar", "središte"),                                                # V5-29
    ("w", "richtung (fahrtrichtung):smjer", "pravac"),                                  # V5-30
    ("w", "mangel:nedostatak", "manjak"),                                               # V5-38
    ("w", "schulstunde / augenblick:čas", "sat"),                                       # V5-43
    ("w", "gelegenheit:prilika", "šansa"),                                              # V5-51
    ("w", "lage:položaj", "lokacija"),                                                  # V5-53
    ("w", "feiertag:praznik", "blagdan"),                                               # V5-54
    ("w", "äußerer:vanjski", "spoljna"),                                                # V5-82
    ("w", "äußerer:vanjski", "spoljni"),
    ("w", "äußerer:vanjski", "spoljno"),
    ("w", "grab:grob", "mezar"),                                                        # V6-122
    ("w", "rat (gremium):vijeće", "savjet"),                                            # V7-5
    ("w", "briefumschlag:koverta", "koverat"),                                          # V7-33
    ("w", "zubehör / besteck:pribor", "escajg"),                                        # V7-37
    ("w", "lichtschalter:prekidač", "šalter"),                                          # V7-43
    ("w", "position:pozicija", "položaj"),                                              # V8-81
    ("w", "milch:mlijeko", "mleko"),                                                    # S-ekavisch
    ("w", "wetter:vrijeme", "vreme"),
    ("w", "zeit:vrijeme", "vreme"),
    ("w", "kind:dijete", "dete"),
    ("w", "fluss:rijeka", "reka"),
    ("w", "welt:svijet", "svet"),
    ("w", "singen:pjevati", "pevati"),
    ("w", "nach (zeitlich):poslije", "posle"),
    ("w", "vor (zeitlich):prije", "pre"),
    ("w", "früher:prije", "pre"),
    ("w", "unten:dolje", "dole"),                                                       # S-dole
]


def test_k2_neins_bleiben_falsch(grunddaten):
    """Ohne node: die Eingabe steht nirgends unter den Antworten der Stelle."""
    def n(x):
        return x.strip().rstrip(".!?").strip().lower()
    assert len(GEGEN_K2) == 57 and len(set(GEGEN_K2)) == 57
    for art, wer, eingabe in GEGEN_K2:
        antworten = {n(a) for a in _antworten_von(grunddaten, art, wer).split(" / ")}
        assert n(eingabe) not in antworten, (wer, eingabe)


@pytest.fixture(scope="module")
def node_k2(index_html, grunddaten):
    return _node_ja_und_gegen(index_html, grunddaten, [], GEGEN_K2)


def test_k2_neins_bleiben_falsch_in_matches(node_k2):
    falsch = {k: v for k, v in node_k2.items() if v != "no"}
    assert falsch == {}
    assert len(node_k2) == len(GEGEN_K2)


# --- K2 Nachtrag (21.11.2026, Gegenprüfung): Ja-Formen, die eine längere Wendung verdeckte ---
# An sieben Stellen hatte die ganze Wendung schon eigene Paare (Ovo ću uzeti, Ko je zabio
# gol?, kola oca ...). zusatz() nimmt längere Formen zuerst, das kürzere Paar kam dort nie
# zum Zug: „Uzeću ovo“ (Ajdin K2, S-futur: ja) war beim Tippen weiter falsch. Jetzt steht
# dort die ganze Wendung als eigenes Paar (varianten.py, S-futur und ganz unten).
K2_VERDECKT = [
    ("w", "ich nehme das:Uzet ću ovo", "Uzeću ovo"),                      # S-futur
    ("w", "ich werde dich anrufen:Nazvat ću te", "Nazvaću te"),           # S-futur
    ("w", "wer hat das tor geschossen?:Ko je dao gol?", "Tko je dao gol?"),   # ko -> tko
    ("w", "spülmaschine:mašina za suđe", "mašina za posuđe"),             # suđe -> posuđe
    ("w", "ich koche abendessen:Kuham večeru", "Kuvam večeru"),           # kuham -> kuvam
    ("w", "das auto des vaters:auto oca", "automobil oca"),               # auto -> automobil
    ("w", "das auto des vaters:auto oca", "očev automobil"),              #   am "auch" „očev auto“
    ("w", "außerdem:osim toga", "sem toga"),                              # osim -> sem
]
# Bleibt falsch: die halbe Wendung, andere Formen, und die Wendungen an anderen Stellen.
GEGEN_K2_VERDECKT = [
    ("w", "ich nehme das:Uzet ću ovo", "Uzeću"),
    ("w", "ich werde dich anrufen:Nazvat ću te", "Nazvaću"),
    ("w", "ich werde arbeiten:Radit ću", "Uzeću ovo"),
    ("w", "wer hat das tor geschossen?:Ko je dao gol?", "Tko"),
    ("w", "ich koche abendessen:Kuham večeru", "Kuvam"),
    ("l", "Poslije posla ___ večeru.", "kuvam večeru"),
    ("w", "das auto des vaters:auto oca", "automobil"),
    ("w", "das auto des vaters:auto oca", "očeva automobil"),
    ("w", "das auto des vaters:auto oca", "automobil očev"),
    ("w", "auto:auto", "automobil oca"),
    ("w", "ich habe ein auto:Imam auto", "Imam očev automobil"),
    ("w", "außerdem:osim toga", "sem"),
    ("w", "außer:osim", "sem toga"),
]


@pytest.fixture(scope="module")
def node_k2_verdeckt(index_html, grunddaten):
    return _node_ja_und_gegen(index_html, grunddaten, K2_VERDECKT, GEGEN_K2_VERDECKT)


def test_k2_verdeckte_ja_formen_zaehlen_jetzt(node_k2_verdeckt):
    falsch = {k: v for k, v in node_k2_verdeckt.items()
              if k[0] != "gegen" and v != ("no" if k[-1] == "vorher" else "ok")}
    assert falsch == {}
    assert len([k for k in node_k2_verdeckt if k[0] != "gegen"]) == 2 * len(K2_VERDECKT)


def test_k2_verdeckte_ja_formen_nichts_anderes_wird_richtig(node_k2_verdeckt):
    falsch = {k: v for k, v in node_k2_verdeckt.items() if k[0] == "gegen" and v != "no"}
    assert falsch == {}
    assert len([k for k in node_k2_verdeckt if k[0] == "gegen"]) == len(GEGEN_K2_VERDECKT)


def test_k2_verdeckt_ganze_wendung_nur_an_ihrer_stelle():
    """Die Paare für die ganze Wendung gelten nur am einen Wort. Die kurzen Paare
    gelten sonst weiter wie vorher (ko -> tko überall), die S-futur-Paare gibt es
    nur noch als ganze Wendung, wie auf Ajdins Karte („Uzet ću ovo → Uzeću ovo“)."""
    stellen = {("uzet ću ovo", "uzeću ovo"): "ich nehme das:Uzet ću ovo",
               ("nazvat ću te", "nazvaću te"): "ich werde dich anrufen:Nazvat ću te",
               ("ko je dao gol", "tko je dao gol"): "wer hat das tor geschossen?:Ko je dao gol?",
               ("mašina za suđe", "mašina za posuđe"): "spülmaschine:mašina za suđe",
               ("kuham večeru", "kuvam večeru"): "ich koche abendessen:Kuham večeru",
               ("auto oca", "automobil oca"): "das auto des vaters:auto oca",
               ("očev auto", "očev automobil"): "das auto des vaters:auto oca",
               ("osim toga", "sem toga"): "außerdem:osim toga"}
    gefunden = {(p["a"], p["b"]): p["gilt"] for p in varianten.VARIANTEN
                if isinstance(p["a"], str) and (p["a"], p["b"]) in stellen}
    assert gefunden == {k: [v] for k, v in stellen.items()}
    for (a, b), kennung in stellen.items():
        mehr, probleme = _z([a], True, kennung=kennung)
        assert b in mehr and probleme == [], (a, mehr)
    assert not [p for p in varianten.VARIANTEN if p["a"] in ("uzet ću", "nazvat ću")]
    assert _z(["Ko je tu"], True) == (["Tko je tu"], [])            # ko -> tko sonst überall
    assert _z(["osim toga"], True) == (["sem toga"], [])             # osim -> sem auch


def test_kein_paar_wird_von_einer_laengeren_wendung_verdeckt(grunddaten):
    """Was ein Paar allein an einer Stelle richtig macht, zählt dort auch mit allen
    Paaren zusammen. zusatz() nimmt die längere Form zuerst - hat die ganze Wendung ein
    eigenes Paar, kommt ein kürzeres dort nicht zum Zug. Bis zum 21.11.2026 war das an
    den sieben Stellen aus K2_VERDECKT so. Schlägt das hier an, braucht die ganze Wendung
    ein eigenes Paar mit der Kennung der Stelle."""
    idx = varianten.index()
    je_paar = {}
    for form, liste in idx.items():
        for nr, ziele in liste:
            je_paar.setdefault(nr, {})[form] = [(nr, ziele)]
    stellen = [(True, w["id"], varianten._antworten(w.get("bs"), w.get("auch")), w.get("auch_var", []))
               for w in _woerter(grunddaten) if varianten.tippbar(str(w["bs"]))]
    stellen += [(False, s["text"], varianten._antworten(s.get("answer"), s.get("auch")), s.get("auch_var", []))
                for s in grunddaten["saetze"]]
    woerter = [{m.group(0).lower() for a in st[2] for m in varianten.WORT.finditer(a)} for st in stellen]
    verdeckt, geprueft = [], 0
    for nr, p in enumerate(varianten.VARIANTEN):
        einzel = je_paar.get(nr, {})
        anfang = {f.split(" ")[0] for f in einzel}
        for (wort, kennung, antworten, auch_var), da in zip(stellen, woerter):
            if not anfang & da or (isinstance(p["gilt"], list) and kennung not in p["gilt"]):
                continue
            geprueft += 1
            allein, _ = varianten.zusatz(antworten, kennung, wort, fall=varianten.FALL.get(kennung), idx=einzel)
            schon = {x.lower() for x in antworten + list(auch_var)}
            verdeckt += [(varianten._erste(p["a"]), varianten._erste(p["b"]), kennung, x)
                         for x in allein if x.lower() not in schon]
    assert geprueft > 1000
    assert verdeckt == []
