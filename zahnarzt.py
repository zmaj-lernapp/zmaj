# -*- coding: utf-8 -*-
"""
zahnarzt.py  –  der versteckte Teil "Beim Zahnarzt"

Eine Zahnärztin will mit Patienten reden können, die nur Bosnisch
sprechen. Ajdin am 05.11.2026: "das interssiert 1% der menschen", also versteckt:
siebenmal auf die Versionszeile in den Einstellungen, dann das Wort "zahnarzt"
(ZA_WORT in web/index.html). Das Wort darf öffentlich sein, es schaltet nichts
Bezahltes frei. Danach steht der Teil als eigene Sektion am Ende des Lernpfads.

Geschrieben aus Sicht der Ärztin, Anrede mit Vi, Vas und Vam groß. Bosnisch und
Deutsch stehen genau so in Release\\Wortschatz\\paket_zahnarzt.json, von Ajdin am
06.11.2026 durchgesehen. Was auf eine Aufnahme wartete (Release\\Wortschatz\\v111_wartet_auf_emir.md),
steht seit dem 07.11.2026 mit Wort und Satz an seiner Stelle.

Warum eine eigene Datei und nicht vokabeln.py: KATEGORIEN dort ist alles, was
gezählt wird: Level, Wörter, Fortschritt, Datensatz, Anki, Store-Zahlen. Dieser Teil
zählt nirgends mit, siehe "Beim Zahnarzt" in web/index.html.

Die Kennung eines Wortes ist hier ZA_VORN + bs, nicht "bedeutung:wort" wie in
vokabeln.py. Sie steht in known und passed wie jede andere, und der fehlende
Doppelpunkt hält altenFortschrittUmschreiben() davon ab, sie für ein umbenanntes Wort
zu halten. Ändert sich bs, beginnt das Wort von vorn (tests/test_zahnarzt.py).
Die Aufnahmen: w5206 und folgende in ton_nur_emir.json, in der Reihenfolge dieser
Datei. zubar / stomatolog ist aus den fertigen Aufnahmen beider Wörter gesetzt.
Kommen die Wartenden später nach: Kommentar hier durch Wort und Satz ersetzen,
Nummern ans Ende von ton_nur_emir.json, Übersetzungen aus
Release\\Wortschatz\\v111_wartet_uebersetzungen.json, dann WARTET und WOERTER in
tests/test_zahnarzt.py nachziehen.
"""

ZA_VORN = "za|"

SEKTION = {"id": "zahnarzt", "label": "Beim Zahnarzt",
           "beschreibung": "Fachwörter und Sätze für die Zahnarztpraxis, jedes mit einem Beispielsatz."}

KATEGORIEN = [
    {"id": "za|zaehne", "label": "Zähne und Mund", "sektion": "zahnarzt",
     "tipp": "Zahnarzt, Zahnarten, Kiefer, Nerv und Wurzel.",
     "reihenfolge": True,   # jedes Wort vor seinem Beispielsatz
     "words": [
        {"de": "Zahnarzt", "bs": "zubar / stomatolog", "auch": ["stomatologinja", "zubarka"]},
        {"de": "Mein Bruder ist Zahnarzt in Tuzla.", "bs": "Moj brat je stomatolog u Tuzli."},
        {"de": "Kiefer", "bs": "vilica"},
        {"de": "Mir tut der Unterkiefer beim Kauen weh.", "bs": "Boli me donja vilica kad žvačem."},
        {"de": "Nerv", "bs": "živac"},
        {"de": "Der Nerv in diesem Zahn ist entzündet.", "bs": "Imate upalu živca u ovom zubu."},
        {"de": "Backenzahn", "bs": "kutnjak"},
        {"de": "Der obere Backenzahn ist ziemlich kariös.", "bs": "Gornji kutnjak je dosta pokvaren."},
        {"de": "Schneidezahn", "bs": "sjekutić"},
        {"de": "Das Kind hat sich einen oberen Schneidezahn abgebrochen.", "bs": "Dijete je slomilo gornji sjekutić."},
        {"de": "Eckzahn", "bs": "očnjak"},
        {"de": "Die Spange wird diesen Eckzahn gerade richten.", "bs": "Aparatić će ispraviti ovaj očnjak."},
        {"de": "Weisheitszahn", "bs": "umnjak"},
        {"de": "Ihr Weisheitszahn ist noch nicht durchgebrochen.", "bs": "Umnjak Vam još nije izrastao."},
        {"de": "Milchzahn", "bs": "mliječni zub"},
        {"de": "Beim Kind wackelt ein Milchzahn.", "bs": "Djetetu se klima mliječni zub."},
        {"de": "Zahnwurzel", "bs": "korijen zuba"},
        {"de": "Die Zahnwurzel ist noch gesund.", "bs": "Korijen zuba je još zdrav."},
        {"de": "Zahnfleisch", "bs": "zubno meso", "auch": ["desni"]},
        {"de": "Ihr Zahnfleisch ist etwas entzündet.", "bs": "Zubno meso Vam je malo upaljeno."},
     ]},
    {"id": "za|befund", "label": "Befund und Zahnersatz", "sektion": "zahnarzt",
     "tipp": "Karies, Füllung, Brücke, Prothese und Implantat.",
     "baut_auf": ["za|zaehne"],
     "reihenfolge": True,   # jedes Wort vor seinem Beispielsatz
     "words": [
        {"de": "Karies", "bs": "karijes"},
        {"de": "An diesem Zahn sehe ich Karies.", "bs": "Na ovom zubu vidim karijes."},
        {"de": "Loch im Zahn", "bs": "rupa u zubu"},
        {"de": "Ich habe ein großes Loch im Zahn.", "bs": "Imam veliku rupu u zubu."},
        {"de": "Füllung (Alltag)", "bs": "plomba", "auch": ["ispun"]},
        {"de": "Diese Füllung ist alt, man muss sie ersetzen.", "bs": "Ova plomba je stara, treba je zamijeniti."},
        {"de": "provisorische Füllung", "bs": "privremena plomba"},
        {"de": "Heute setze ich eine provisorische Füllung ein.", "bs": "Danas ću staviti privremenu plombu."},
        {"de": "Zahnbrücke", "bs": "zubni most"},
        {"de": "Die Zahnbrücke ist in sieben Tagen fertig.", "bs": "Zubni most će biti gotov za sedam dana."},
        {"de": "Zahnprothese", "bs": "zubna proteza"},
        {"de": "Oma trägt seit zehn Jahren eine Zahnprothese.", "bs": "Nana nosi protezu već deset godina."},
        {"de": "Zahnimplantat", "bs": "zubni implantat"},
        {"de": "Ein Implantat ist teurer als eine Brücke.", "bs": "Implantat je skuplji od mosta."},
        {"de": "Zahnziehen", "bs": "vađenje zuba"},
        {"de": "Das Zahnziehen dauert nur ein paar Minuten.", "bs": "Vađenje zuba traje samo nekoliko minuta."},
     ]},
    {"id": "za|behandlung", "label": "Die Behandlung", "sektion": "zahnarzt",
     "tipp": "Zahnstein, Betäubung, Röntgen, Abdruck und Zahnseide.",
     "baut_auf": ["za|befund"],
     "reihenfolge": True,   # jedes Wort vor seinem Beispielsatz
     "words": [
        {"de": "Zahnstein", "bs": "zubni kamenac"},
        {"de": "Wir müssen den Zahnstein entfernen.", "bs": "Moramo skinuti zubni kamenac."},
        {"de": "Zahnfleischentzündung", "bs": "upala desni"},
        {"de": "Sie haben eine leichte Zahnfleischentzündung.", "bs": "Imate blagu upalu desni."},
        {"de": "Betäubung", "bs": "anestezija"},
        {"de": "Die Betäubung lässt in zwei Stunden nach.", "bs": "Anestezija će proći za dva sata."},
        {"de": "Röntgenbild", "bs": "rendgenski snimak"},
        {"de": "Das Röntgenbild zeigt eine Entzündung an der Wurzel.", "bs": "Rendgenski snimak pokazuje upalu korijena."},
        {"de": "Zahnabdruck", "bs": "otisak zuba"},
        {"de": "Heute nehmen wir einen Zahnabdruck.", "bs": "Danas ćemo uzeti otisak zuba."},
        {"de": "Zahnaufhellung", "bs": "izbjeljivanje zuba"},
        {"de": "Die Zahnaufhellung wird extra bezahlt.", "bs": "Izbjeljivanje zuba se plaća posebno."},
        {"de": "Zahnseide", "bs": "zubni konac"},
        {"de": "Benutzen Sie Zahnseide?", "bs": "Da li koristite zubni konac?"},
        {"de": "Zahnkrone", "bs": "navlaka", "auch": ["krunica", "zubna krunica"]},
        {"de": "Auf diesen Zahn kommt eine Krone.", "bs": "Na ovaj zub ide navlaka."},
        {"de": "Wurzelkanalbehandlung", "bs": "liječenje kanala", "auch": ["liječenje korijenskih kanala"]},
        {"de": "Dieser Zahn braucht eine Wurzelbehandlung.", "bs": "Ovom zubu treba liječenje kanala."},
        {"de": "Zahnspange", "bs": "aparat za zube"},
        {"de": "Meine Tochter trägt eine Zahnspange.", "bs": "Moja kćerka nosi aparat za zube."},
        {"de": "Schwellung", "bs": "otok", "auch": ["oteklina"]},
        {"de": "Die Schwellung geht in ein paar Tagen zurück.", "bs": "Otok će proći za nekoliko dana."},
     ]},
    {"id": "za|anweisungen", "label": "Anweisungen", "sektion": "zahnarzt",
     "tipp": "Was man im Behandlungsstuhl sagt: Mund auf, zubeißen, ausspülen.",
     "baut_auf": ["za|behandlung"],
     "reihenfolge": True,   # jedes Wort vor seinem Beispielsatz
     "words": [
        {"de": "Öffnen Sie den Mund.", "bs": "Otvorite usta."},
        {"de": "Öffnen Sie bitte den Mund.", "bs": "Otvorite usta, molim Vas."},
        {"de": "Schließen Sie den Mund.", "bs": "Zatvorite usta."},
        {"de": "Schließen Sie den Mund, wir sind fertig.", "bs": "Zatvorite usta, gotovi smo."},
        {"de": "Beißen Sie zu.", "bs": "Zagrizite."},
        {"de": "Beißen Sie zu und sagen Sie, ob es stört.", "bs": "Zagrizite i recite da li smeta."},
        {"de": "Spülen Sie den Mund aus.", "bs": "Isperite usta."},
        {"de": "Spülen Sie den Mund aus und spucken Sie hier aus.", "bs": "Isperite usta i pljunite ovdje."},
        {"de": "Lehnen Sie den Kopf an.", "bs": "Naslonite glavu."},
        {"de": "Lehnen Sie den Kopf an, ich stelle den Stuhl tiefer.", "bs": "Naslonite glavu, spustit ću stolicu."},
        {"de": "Atmen Sie durch die Nase.", "bs": "Dišite kroz nos."},
        {"de": "Atmen Sie durch die Nase, ganz langsam.", "bs": "Dišite kroz nos, samo polako."},
        {"de": "Entspannen Sie sich.", "bs": "Opustite se."},
        {"de": "Entspannen Sie sich, das dauert nicht lange.", "bs": "Opustite se, ovo neće dugo trajati."},
        {"de": "Haben Sie keine Angst.", "bs": "Ne bojte se."},
        {"de": "Haben Sie keine Angst, ich bin vorsichtig.", "bs": "Ne bojte se, bit ću pažljiva."},
        {"de": "Heben Sie die Hand, wenn es wehtut.", "bs": "Podignite ruku ako Vas zaboli."},
        {"de": "Wenn es wehtut, heben Sie sofort die Hand.", "bs": "Ako Vas zaboli, odmah podignite ruku."},
        {"de": "Machen Sie den Mund etwas weiter auf.", "bs": "Otvorite usta malo šire."},
        {"de": "Machen Sie den Mund etwas weiter auf, ich sehe nicht gut.", "bs": "Otvorite usta malo šire, ne vidim dobro."},
        {"de": "Es wird nicht wehtun.", "bs": "Neće boliti.", "auch": ["Neće boljeti."]},
        {"de": "Es wird nicht wehtun, Sie bekommen eine Spritze.", "bs": "Neće boliti, dobit ćete injekciju."},
     ]},
    {"id": "za|fragen", "label": "Fragen", "sektion": "zahnarzt",
     "tipp": "Wo es wehtut, seit wann, Allergien und Schwangerschaft.",
     "baut_auf": ["za|anweisungen"],
     "reihenfolge": True,   # jedes Wort vor seinem Beispielsatz
     "words": [
        {"de": "Tut es Ihnen hier weh?", "bs": "Da li Vas boli ovdje?"},
        {"de": "Tut es Ihnen hier weh, wenn ich drücke?", "bs": "Da li Vas boli ovdje kad pritisnem?"},
        {"de": "Welcher Zahn tut Ihnen weh?", "bs": "Koji zub Vas boli?"},
        {"de": "Welcher Zahn tut Ihnen weh, oben oder unten?", "bs": "Koji zub Vas boli, gornji ili donji?"},
        {"de": "Seit wann tut es Ihnen weh?", "bs": "Od kada Vas boli?"},
        {"de": "Seit wann tut Ihnen dieser Zahn weh?", "bs": "Od kada Vas boli ovaj zub?"},
        {"de": "Tut es weh, wenn Sie zubeißen?", "bs": "Da li Vas boli kad zagrizete?"},
        {"de": "Tut es weh, wenn Sie auf etwas Hartes beißen?", "bs": "Da li Vas boli kad zagrizete nešto tvrdo?"},
        {"de": "Ist er (der Zahn) kälteempfindlich?", "bs": "Da li je osjetljiv na hladno?"},
        {"de": "Ist der Zahn kälteempfindlich?", "bs": "Da li je zub osjetljiv na hladno?"},
        {"de": "Sind Sie gegen ein Medikament allergisch?", "bs": "Da li ste alergični na neki lijek?"},
        {"de": "Sagen Sie mir, ob Sie gegen ein Medikament allergisch sind.", "bs": "Recite mi da li ste alergični na neki lijek."},
        {"de": "Sind Sie schwanger?", "bs": "Da li ste trudni?"},
        {"de": "Sind Sie schwanger oder stillen Sie?", "bs": "Da li ste trudni ili dojite?"},
        {"de": "Wann waren Sie zuletzt beim Zahnarzt?", "bs": "Kada ste zadnji put bili kod zubara?"},
        {"de": "Und wann waren Sie zuletzt beim Zahnarzt?", "bs": "A kada ste zadnji put bili kod zubara?"},
     ]},
    {"id": "za|erklaeren", "label": "Erklären", "sektion": "zahnarzt",
     "tipp": "Den Befund, die Spritze und was danach gilt.",
     "baut_auf": ["za|fragen"],
     "reihenfolge": True,   # jedes Wort vor seinem Beispielsatz
     "words": [
        {"de": "Sie haben Karies.", "bs": "Imate karijes."},
        {"de": "Sie haben an zwei Zähnen Karies.", "bs": "Imate karijes na dva zuba."},
        {"de": "Sie brauchen eine Füllung.", "bs": "Treba Vam plomba."},
        {"de": "Sie brauchen an diesem Zahn eine Füllung.", "bs": "Treba Vam plomba na ovom zubu."},
        {"de": "Wir müssen ein Röntgenbild machen.", "bs": "Moramo napraviti snimak."},
        {"de": "Wir müssen von diesem Zahn ein Röntgenbild machen.", "bs": "Moramo napraviti snimak ovog zuba."},
        {"de": "Ich gebe Ihnen eine Spritze.", "bs": "Dat ću Vam injekciju."},
        {"de": "Ich gebe Ihnen eine Spritze, damit es nicht wehtut.", "bs": "Dat ću Vam injekciju da ne boli."},
        {"de": "Essen Sie zwei Stunden lang nichts.", "bs": "Dva sata nemojte jesti."},
        {"de": "Essen Sie nach der Füllung zwei Stunden lang nichts.", "bs": "Poslije plombe dva sata nemojte jesti."},
        {"de": "Kommen Sie in einer Woche zur Kontrolle.", "bs": "Dođite na kontrolu za sedmicu dana."},
        {"de": "Kommen Sie in einer Woche zur gleichen Zeit zur Kontrolle.", "bs": "Dođite na kontrolu za sedmicu dana, u isto vrijeme."},
        # Zub se mora vaditi. stand hier als Kommentar hinter dem Einzeleintrag; seit dem
        # 07.11.2026 davor, damit jedes Wort vor seinem Satz bleibt (Paket: Nr. 53).
        {"de": "Der Zahn muss gezogen werden.", "bs": "Zub se mora vaditi."},
        {"de": "Es tut mir leid, der Zahn muss gezogen werden.", "bs": "Žao mi je, zub se mora vaditi."},
        {"de": "Ich bin Zahnärztin, wie kann ich Ihnen helfen?", "bs": "Ja sam stomatologinja, kako Vam mogu pomoći?"},
     ]},
    {"id": "za|patienten", "label": "Was Patienten sagen", "sektion": "zahnarzt",
     "tipp": "Schmerzen, Füllung, Schwellung und Angst.",
     "baut_auf": ["za|erklaeren"],
     "reihenfolge": True,   # jedes Wort vor seinem Beispielsatz
     "words": [
        {"de": "Mein Zahn tut weh.", "bs": "Boli me zub."},
        {"de": "Mein Zahn tut schon seit drei Tagen weh.", "bs": "Boli me zub već tri dana."},
        {"de": "Es tut beim Essen weh.", "bs": "Boli me kad jedem."},
        {"de": "Es tut weh, wenn ich etwas Süßes esse.", "bs": "Boli me kad jedem nešto slatko."},
        {"de": "Meine Füllung ist herausgefallen.", "bs": "Ispala mi je plomba."},
        {"de": "Vor zwei Tagen ist mir die Füllung herausgefallen.", "bs": "Ispala mi je plomba prije dva dana."},
        {"de": "Mir ist ein Zahn abgebrochen.", "bs": "Slomio mi se zub."},
        {"de": "Beim Walnussessen ist mir ein Zahn abgebrochen.", "bs": "Slomio mi se zub dok sam jeo orahe."},
        {"de": "Mein Zahnfleisch blutet.", "bs": "Krvare mi desni."},
        {"de": "Mein Zahnfleisch blutet, wenn ich die Zähne putze.", "bs": "Krvare mi desni kad perem zube."},
        {"de": "Meine Wange ist geschwollen.", "bs": "Otekao mi je obraz."},
        {"de": "Über Nacht ist meine Wange angeschwollen.", "bs": "Otekao mi je obraz preko noći."},
        {"de": "Nachts kann ich vor Schmerzen nicht schlafen.", "bs": "Noću ne mogu spavati od bolova."},
        {"de": "Nachts kann ich vor Zahnschmerzen nicht schlafen.", "bs": "Noću ne mogu spavati od bolova u zubu."},
        {"de": "Ich habe Angst vor dem Zahnarzt.", "bs": "Bojim se zubara."},
        {"de": "Ich habe schon seit der Kindheit Angst vor dem Zahnarzt.", "bs": "Bojim se zubara još od djetinjstva."},
     ]},
]
