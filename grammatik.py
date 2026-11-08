# -*- coding: utf-8 -*-
"""
grammatik.py  –  GRAMMATIK-LEKTIONEN

Jede Lektion gehört zu einem Level (Schlüssel = Level-id aus vokabeln.py).
Das Level bekommt dann in der App einen Reiter „Grammatik“ mit der Erklärung
und den Übungen. Der Level-Test nimmt bis zu 3 Übungen mit hinein.

Aufbau einer Lektion:
  "erklaerung": Liste aus Absätzen (Text) und Tabellen ({"tabelle": [...]}).
                Die erste Zeile einer Tabelle ist die Überschrift.
  "uebungen":   Liste von Aufgaben mit Auswahl:
                {"frage": "...", "optionen": ["a", "b", "c"], "richtig": "a", "tipp": "..."}
                "richtig" muss genau so in "optionen" stehen.

HINWEIS: Claude ist kein Muttersprachler. Regeln und Beispiele bitte prüfen.
"""

GRAMMATIK = {

    "fragen": {
        "erklaerung": [
            "Fragewörter stehen am Satzanfang, danach kommt das Verb: „Gdje stanuješ?“, „Šta radiš?“.",
            "Für Ja/Nein-Fragen gibt es zwei Wege. Entweder „Da li“ vor den Satz setzen: „Da li govoriš bosanski?“ Oder das kleine „li“ hinter das Verb: „Govoriš li bosanski?“ Beides ist richtig, „li“ hinter dem Verb klingt etwas natürlicher.",
            {"tabelle": [["Deutsch", "Bosnisch", "Beispiel"],
                         ["Wer?", "Ko?", "Ko je to? – Wer ist das?"],
                         ["Was?", "Šta?", "Šta radiš? – Was machst du?"],
                         ["Wo?", "Gdje?", "Gdje si? – Wo bist du?"],
                         ["Wohin?", "Kuda?", "Kuda ideš? – Wohin gehst du?"],
                         ["Wann?", "Kada?", "Kada dolaziš? – Wann kommst du?"],
                         ["Warum?", "Zašto?", "Zašto ne? – Warum nicht?"],
                         ["Wie viel?", "Koliko?", "Koliko košta? – Wie viel kostet es?"]]},
        ],
        "uebungen": [
            {"frage": "„___ stanuješ?“ (Wo wohnst du?)", "optionen": ["Gdje", "Kuda", "Kada"], "richtig": "Gdje", "tipp": "Gdje = wo (Ort), Kuda = wohin (Richtung)."},
            {"frage": "„___ ideš?“ (Wohin gehst du?)", "optionen": ["Gdje", "Kuda", "Ko"], "richtig": "Kuda", "tipp": "Bewegung in eine Richtung: Kuda."},
            {"frage": "Ja/Nein-Frage: „Sprichst du Deutsch?“", "optionen": ["Govoriš li njemački?", "Gdje govoriš njemački?", "Govoriš njemački li?"], "richtig": "Govoriš li njemački?", "tipp": "„li“ steht direkt hinter dem Verb."},
            {"frage": "„___ košta hljeb?“ (Wie viel kostet das Brot?)", "optionen": ["Koliko", "Kako", "Koji"], "richtig": "Koliko", "tipp": "Koliko = wie viel, Kako = wie, Koji = welcher."},
            {"frage": "„___ je to?“ (Wer ist das?)", "optionen": ["Ko", "Šta", "Čiji"], "richtig": "Ko", "tipp": "Ko fragt nach Personen, Šta nach Dingen."},
            {"frage": "Dasselbe wie „Govoriš li bosanski?“", "optionen": ["Da li govoriš bosanski?", "Zašto govoriš bosanski?", "Kada govoriš bosanski?"], "richtig": "Da li govoriš bosanski?", "tipp": "„Da li“ am Anfang oder „li“ nach dem Verb: beides eine Ja/Nein-Frage."},
        ],
    },

    "genus": {
        "erklaerung": [
            "Jedes Substantiv ist männlich (on), weiblich (ona) oder sächlich (ono). Man erkennt es fast immer an der Endung im Nominativ.",
            {"tabelle": [["Endung", "Geschlecht", "Beispiele"],
                         ["Konsonant (brat, grad, sto)", "männlich – on", "moj brat, velik grad"],
                         ["-a (sestra, kuća, voda)", "weiblich – ona", "moja sestra, velika kuća"],
                         ["-o / -e (selo, more, pismo)", "sächlich – ono", "moje selo, veliko more"]]},
            "Adjektive und Besitzwörter passen sich an: moj brat, moja sestra, moje dijete. Velik grad, velika kuća, veliko selo.",
            "Ausnahmen gibt es, zum Beispiel „dijete“ (Kind) ist sächlich, „babo“ und „dedo“ sind männlich, obwohl sie auf -o enden. Berufe haben oft eine weibliche Form auf -ica: nastavnik / nastavnica.",
        ],
        "uebungen": [
            {"frage": "Welches Geschlecht hat „kuća“?", "optionen": ["männlich (on)", "weiblich (ona)", "sächlich (ono)"], "richtig": "weiblich (ona)", "tipp": "Endung -a → weiblich."},
            {"frage": "Welches Geschlecht hat „grad“?", "optionen": ["männlich (on)", "weiblich (ona)", "sächlich (ono)"], "richtig": "männlich (on)", "tipp": "Endet auf einen Konsonanten → männlich."},
            {"frage": "Welches Geschlecht hat „selo“?", "optionen": ["männlich (on)", "weiblich (ona)", "sächlich (ono)"], "richtig": "sächlich (ono)", "tipp": "Endung -o → sächlich."},
            {"frage": "„___ sestra“ (meine Schwester)", "optionen": ["moj", "moja", "moje"], "richtig": "moja", "tipp": "sestra ist weiblich → moja."},
            {"frage": "„___ more“ (großes Meer)", "optionen": ["velik", "velika", "veliko"], "richtig": "veliko", "tipp": "more endet auf -e → sächlich → veliko."},
            {"frage": "„___ babo“ (mein Papa)", "optionen": ["moj", "moja", "moje"], "richtig": "moj", "tipp": "Ausnahme: babo ist männlich, obwohl es auf -o endet."},
            {"frage": "Die weibliche Form von „nastavnik“ (Lehrer)?", "optionen": ["nastavnica", "nastavnika", "nastavnico"], "richtig": "nastavnica", "tipp": "Berufe: -ik → -ica."},
        ],
    },

    "konjugation": {
        "erklaerung": [
            "Verben bekommen je nach Person eine eigene Endung. Deshalb lässt man „ja“, „ti“ usw. meistens weg: „Radim“ heißt schon „ich arbeite“.",
            {"tabelle": [["Person", "biti (sein)", "imati (haben)", "raditi (arbeiten)"],
                         ["ja (ich)", "sam", "imam", "radim"],
                         ["ti (du)", "si", "imaš", "radiš"],
                         ["on / ona (er / sie)", "je", "ima", "radi"],
                         ["mi (wir)", "smo", "imamo", "radimo"],
                         ["vi (ihr / Sie)", "ste", "imate", "radite"],
                         ["oni (sie)", "su", "imaju", "rade"]]},
            "Die meisten Verben folgen dem Muster -m, -š, -, -mo, -te, -ju/-e. „Sam, si, je, smo, ste, su“ sind kurz und stehen nie am Satzanfang: „Ja sam umoran“, nicht „Sam umoran“.",
            "„Vi“ benutzt man auch für die höfliche Anrede einer Person (Sie): „Kako ste?“",
        ],
        "uebungen": [
            {"frage": "„Mi ___ kod kuće.“ (Wir sind zu Hause.)", "optionen": ["sam", "smo", "su"], "richtig": "smo", "tipp": "mi → smo."},
            {"frage": "„Ti ___ dva brata.“ (Du hast zwei Brüder.)", "optionen": ["imam", "imaš", "ima"], "richtig": "imaš", "tipp": "ti → -š."},
            {"frage": "„Oni ___ u Sarajevu.“ (Sie arbeiten in Sarajevo.)", "optionen": ["radi", "radimo", "rade"], "richtig": "rade", "tipp": "oni → -e / -ju."},
            {"frage": "Wie sagt man „ich spreche“?", "optionen": ["govorim", "govoriš", "govori"], "richtig": "govorim", "tipp": "ja → -m."},
            {"frage": "„Kako ___?“ (Wie geht es Ihnen? – höflich)", "optionen": ["si", "ste", "su"], "richtig": "ste", "tipp": "Höflich = vi → ste."},
            {"frage": "Welcher Satz ist richtig?", "optionen": ["Ja sam umoran.", "Sam ja umoran.", "Sam umoran ja."], "richtig": "Ja sam umoran.", "tipp": "„sam“ steht nie an erster Stelle."},
        ],
    },

    "mehrzahl": {
        "erklaerung": [
            "Die Mehrzahl hängt vom Geschlecht ab:",
            {"tabelle": [["Geschlecht", "Endung Mehrzahl", "Beispiele"],
                         ["männlich", "-i (kurze Wörter oft -ovi / -evi)", "prijatelj → prijatelji, grad → gradovi, ključ → ključevi"],
                         ["weiblich", "-e", "sestra → sestre, kuća → kuće"],
                         ["sächlich", "-a", "selo → sela, jaje → jaja"]]},
            "Wichtige Ausnahmen, die man einfach lernt: brat → braća, dijete → djeca, čovjek → ljudi, oko → oči, pas → psi.",
            "Bei manchen männlichen Wörtern ändert sich vor -i der Konsonant: k → c (vojnik → vojnici), und -ac verliert das a (muškarac → muškarci).",
        ],
        "uebungen": [
            {"frage": "Mehrzahl von „kuća“?", "optionen": ["kuće", "kući", "kuća"], "richtig": "kuće", "tipp": "weiblich → -e."},
            {"frage": "Mehrzahl von „grad“?", "optionen": ["grade", "gradovi", "grada"], "richtig": "gradovi", "tipp": "kurzes männliches Wort → -ovi."},
            {"frage": "Mehrzahl von „selo“?", "optionen": ["seli", "sele", "sela"], "richtig": "sela", "tipp": "sächlich → -a."},
            {"frage": "Mehrzahl von „brat“?", "optionen": ["brati", "bratovi", "braća"], "richtig": "braća", "tipp": "Ausnahme, einfach merken."},
            {"frage": "Mehrzahl von „dijete“?", "optionen": ["dijeta", "djeca", "dijeti"], "richtig": "djeca", "tipp": "Ausnahme: djeca."},
            {"frage": "Mehrzahl von „čovjek“ (Mensch)?", "optionen": ["čovjeci", "čovjeki", "ljudi"], "richtig": "ljudi", "tipp": "Ein ganz anderes Wort: ljudi."},
        ],
    },

    "satzbau": {
        "erklaerung": [
            "Verneinung: „ne“ steht direkt vor dem Verb: „Ne razumijem“, „Ne radim“. Nur drei Verben verschmelzen mit ne: biti → nisam/nisi/nije, imati → nemam/nemaš/nema, htjeti → neću/nećeš/neće.",
            "Nebensätze werden mit kleinen Wörtern angehängt, die Wortstellung bleibt danach normal (anders als im Deutschen, wo das Verb ans Ende rückt):",
            {"tabelle": [["Wort", "Bedeutung", "Beispiel"],
                         ["da", "dass", "Mislim da je dobro. – Ich denke, dass es gut ist."],
                         ["jer", "weil", "Ne dolazim jer radim. – Ich komme nicht, weil ich arbeite."],
                         ["da li", "ob", "Pitam se da li dolazi. – Ich frage mich, ob er kommt."],
                         ["ako", "wenn / falls", "Ako pada kiša, ostajem. – Wenn es regnet, bleibe ich."],
                         ["kad", "als / wenn (Zeit)", "Kad dođem, zovem te. – Wenn ich komme, rufe ich dich an."],
                         ["ali", "aber", "Volim kahvu, ali ne volim čaj."]]},
            "Doppelte Verneinung ist Pflicht: „Niko ne zna“ (Niemand weiß es), „Nikad ne kasnim“ (Ich komme nie zu spät). Vor „jer“, „da“ und „ako“ steht kein Komma, wenn der Nebensatz hinter dem Hauptsatz steht: „Ne dolazim jer radim.“",
        ],
        "uebungen": [
            {"frage": "„Ich bin nicht müde.“", "optionen": ["Ne sam umoran.", "Nisam umoran.", "Sam ne umoran."], "richtig": "Nisam umoran.", "tipp": "biti + ne = nisam."},
            {"frage": "„Ich habe keine Zeit.“", "optionen": ["Ne imam vremena.", "Nemam vremena.", "Imam ne vremena."], "richtig": "Nemam vremena.", "tipp": "imati + ne = nemam."},
            {"frage": "„Mislim ___ je dobro.“ (Ich denke, dass es gut ist.)", "optionen": ["da", "jer", "ako"], "richtig": "da", "tipp": "dass = da."},
            {"frage": "„Ne dolazim ___ radim.“ (Ich komme nicht, weil ich arbeite.)", "optionen": ["da", "jer", "ali"], "richtig": "jer", "tipp": "weil = jer."},
            {"frage": "„Niemand weiß es.“", "optionen": ["Niko zna.", "Niko ne zna.", "Ne niko zna."], "richtig": "Niko ne zna.", "tipp": "Doppelte Verneinung: niko + ne."},
            {"frage": "„Pitam se ___ dolazi.“ (Ich frage mich, ob er kommt.)", "optionen": ["da li", "kad", "jer"], "richtig": "da li", "tipp": "ob = da li."},
            {"frage": "Wo steht „ne“?", "optionen": ["Ja razumijem ne.", "Ja ne razumijem.", "Ne ja razumijem."], "richtig": "Ja ne razumijem.", "tipp": "ne steht direkt vor dem Verb."},
        ],
    },

    "faelle1": {
        "erklaerung": [
            "Bosnisch hat sieben Fälle. Der Nominativ ist die Grundform (wer? was?): „Brat radi.“ Der Akkusativ steht beim direkten Objekt (wen? was?): „Vidim brata.“",
            {"tabelle": [["Geschlecht", "Nominativ", "Akkusativ", "Regel"],
                         ["männlich, belebt", "brat, doktor, pas", "brata, doktora, psa", "+ a"],
                         ["männlich, unbelebt", "hljeb, grad, auto", "hljeb, grad, auto", "bleibt gleich"],
                         ["weiblich", "sestra, kahva, kuća", "sestru, kahvu, kuću", "-a → -u"],
                         ["sächlich", "dijete, selo, more", "dijete, selo, more", "bleibt gleich"]]},
            "Besitzwörter und Adjektive ändern sich mit: „Volim svoju majku“, „Znam tvog brata“. „Svoj“ heißt „mein eigener“ und wird benutzt, wenn der Besitzer das Subjekt ist.",
            "Kurze Pronomen im Akkusativ: me (mich), te (dich), ga (ihn), je (sie), nas (uns), vas (euch), ih (sie). Sie stehen an zweiter Stelle im Satz: „Vidim te“, „Volim ga“.",
        ],
        "uebungen": [
            {"frage": "„Vidim ___.“ (Ich sehe die Schwester.)", "optionen": ["sestra", "sestru", "sestri"], "richtig": "sestru", "tipp": "weiblich: -a → -u."},
            {"frage": "„Zovem ___.“ (Ich rufe den Arzt.)", "optionen": ["doktor", "doktora", "doktoru"], "richtig": "doktora", "tipp": "männlich belebt: + a."},
            {"frage": "„Jedem ___.“ (Ich esse Brot.)", "optionen": ["hljeb", "hljeba", "hljebu"], "richtig": "hljeb", "tipp": "männlich unbelebt bleibt gleich."},
            {"frage": "„Pijem ___.“ (Ich trinke Kaffee.)", "optionen": ["kahva", "kahvu", "kahve"], "richtig": "kahvu", "tipp": "kahva ist weiblich → kahvu."},
            {"frage": "„Vidim ___.“ (Ich sehe das Kind.)", "optionen": ["dijete", "dijeta", "djetetu"], "richtig": "dijete", "tipp": "sächlich bleibt gleich."},
            {"frage": "„Volim ___ majku.“ (Ich liebe meine Mutter.)", "optionen": ["svoja", "svoju", "svoje"], "richtig": "svoju", "tipp": "Das Besitzwort geht mit: -u."},
            {"frage": "„Ich sehe dich.“", "optionen": ["Vidim ti.", "Vidim te.", "Vidim tebi."], "richtig": "Vidim te.", "tipp": "dich = te."},
        ],
    },

    "faelle2": {
        "erklaerung": [
            "Der Genitiv antwortet auf „wessen?“ und „woher?“ und steht nach vielen Präpositionen: bez (ohne), iz (aus), od (von), do (bis), kod (bei), pored (neben), blizu (nahe), zbog (wegen).",
            {"tabelle": [["Geschlecht", "Nominativ", "Genitiv", "Regel"],
                         ["männlich", "brat, grad, šećer", "brata, grada, šećera", "+ a"],
                         ["weiblich", "sestra, kuća, voda", "sestre, kuće, vode", "-a → -e"],
                         ["sächlich", "selo, mlijeko, dijete", "sela, mlijeka, djeteta", "-o → -a"]]},
            "Besitz: „kuća moje sestre“ (das Haus meiner Schwester), „auto oca“ (das Auto des Vaters).",
            "Mengen: nach Mengenwörtern und Zahlen ab 5 steht der Genitiv: čaša vode, kilogram jabuka, mnogo ljudi, malo vremena, pet godina.",
            "Verneinung von „haben“ und „es gibt“: „Nemam novca“ (Ich habe kein Geld), „Nema hljeba“ (Es gibt kein Brot).",
        ],
        "uebungen": [
            {"frage": "„Kahva bez ___.“ (Kaffee ohne Zucker.)", "optionen": ["šećer", "šećera", "šećeru"], "richtig": "šećera", "tipp": "bez + Genitiv, männlich + a."},
            {"frage": "„Ja sam iz ___.“ (Ich bin aus Bosnien.)", "optionen": ["Bosna", "Bosnu", "Bosne"], "richtig": "Bosne", "tipp": "iz + Genitiv, weiblich -a → -e."},
            {"frage": "„Čaša ___.“ (Ein Glas Wasser.)", "optionen": ["voda", "vode", "vodu"], "richtig": "vode", "tipp": "Menge + Genitiv."},
            {"frage": "„Kuća moje ___.“ (Das Haus meiner Schwester.)", "optionen": ["sestra", "sestre", "sestri"], "richtig": "sestre", "tipp": "Besitz = Genitiv."},
            {"frage": "„Nemam ___.“ (Ich habe kein Geld.)", "optionen": ["novac", "novca", "novcu"], "richtig": "novca", "tipp": "nemam + Genitiv."},
            {"frage": "„Kod ___.“ (Bei der Oma.)", "optionen": ["nana", "nane", "nanu"], "richtig": "nane", "tipp": "kod + Genitiv."},
            {"frage": "„Čaša ___.“ (Ein Glas Milch.)", "optionen": ["mlijeko", "mlijeka", "mlijeku"], "richtig": "mlijeka", "tipp": "sächlich -o → -a."},
        ],
    },

    "praepositionen": {
        "erklaerung": [
            "Jede Präposition verlangt einen bestimmten Fall. Die wichtigsten Gruppen:",
            {"tabelle": [["Fall", "Präpositionen", "Beispiel"],
                         ["Genitiv", "bez, iz, od, do, kod, pored, blizu, zbog, poslije, prije", "iz grada, kod nane, poslije posla"],
                         ["Akkusativ", "za, kroz; u/na bei Bewegung (wohin?)", "za tebe, kroz grad, idem u grad, idem na pijacu"],
                         ["Lokativ", "u/na bei Ort (wo?), o (über), prema", "u gradu, na pijaci, o poslu"],
                         ["Instrumental", "s/sa, pod, iznad, ispod, između, pred, za (hinter)", "s bratom, pod stolom, između kuća"]]},
            "Merke „u“ und „na“: Bewegung → Akkusativ (Idem u grad), Ort → Lokativ (Ja sam u gradu). Auf Deutsch ist das wie „in die Stadt“ und „in der Stadt“.",
            "„na“ statt „u“ bei: pijaca, posao, fakultet, more, Baščaršija, sto, ulica. Also „idem na posao“, „na pijaci“, „na moru“.",
        ],
        "uebungen": [
            {"frage": "„Idem ___ grad.“ (Ich gehe in die Stadt.)", "optionen": ["u", "na", "iz"], "richtig": "u", "tipp": "Bewegung in etwas hinein: u + Akkusativ."},
            {"frage": "„Ja sam ___ gradu.“ (Ich bin in der Stadt.)", "optionen": ["u", "na", "za"], "richtig": "u", "tipp": "Ort: u + Lokativ (gradu)."},
            {"frage": "„Idem ___ posao.“ (Ich gehe zur Arbeit.)", "optionen": ["u", "na", "kod"], "richtig": "na", "tipp": "posao geht mit na."},
            {"frage": "„Knjiga je ___ stolu.“ (Das Buch ist auf dem Tisch.)", "optionen": ["u", "na", "pod"], "richtig": "na", "tipp": "auf = na."},
            {"frage": "„Poklon je ___ tebe.“ (Das Geschenk ist für dich.)", "optionen": ["za", "od", "sa"], "richtig": "za", "tipp": "für = za + Akkusativ."},
            {"frage": "„Dolazim ___ posla.“ (Ich komme von der Arbeit.)", "optionen": ["sa", "u", "na"], "richtig": "sa", "tipp": "Von einem na-Ort kommt man mit „sa“ (sa posla, sa pijace)."},
            {"frage": "„Sjedim ___ tebe i brata.“ (Ich sitze zwischen dir und dem Bruder.)", "optionen": ["između", "iznad", "pored"], "richtig": "između", "tipp": "zwischen = između."},
        ],
    },

    "faelle3": {
        "erklaerung": [
            "Dativ = wem gebe ich etwas? „Dajem bratu“. Lokativ = wo? nach u, na, o, prema: „u gradu“. Beide Fälle haben dieselben Endungen, deshalb lernt man sie zusammen.",
            {"tabelle": [["Geschlecht", "Nominativ", "Dativ / Lokativ", "Regel"],
                         ["männlich", "brat, grad, prijatelj", "bratu, gradu, prijatelju", "+ u"],
                         ["weiblich", "sestra, škola, kuća", "sestri, školi, kući", "-a → -i"],
                         ["sächlich", "selo, dijete", "selu, djetetu", "-o → -u"]]},
            "Bei weiblichen Wörtern auf -ka, -ga, -ha ändert sich der Konsonant: majka → majci, knjiga → knjizi, Amerika → Americi.",
            "Kurze Pronomen im Dativ: mi (mir), ti (dir), mu (ihm), joj (ihr), nam (uns), vam (euch), im (ihnen). Sie stehen an zweiter Stelle: „Daj mi“, „Hladno mi je“, „Sviđa mi se“.",
        ],
        "uebungen": [
            {"frage": "„Dajem poklon ___.“ (Ich gebe der Schwester ein Geschenk.)", "optionen": ["sestra", "sestru", "sestri"], "richtig": "sestri", "tipp": "Dativ weiblich: -a → -i."},
            {"frage": "„Pomažem ___.“ (Ich helfe der Mutter.)", "optionen": ["majku", "majci", "majke"], "richtig": "majci", "tipp": "majka → majci (k → c)."},
            {"frage": "„Stanujem u ___.“ (Ich wohne in Sarajevo.)", "optionen": ["Sarajevo", "Sarajevu", "Sarajeva"], "richtig": "Sarajevu", "tipp": "u + Lokativ: -o → -u."},
            {"frage": "„Kažem ___.“ (Ich sage es dem Freund.)", "optionen": ["prijatelj", "prijatelja", "prijatelju"], "richtig": "prijatelju", "tipp": "Dativ männlich: + u."},
            {"frage": "„Hladno ___ je.“ (Mir ist kalt.)", "optionen": ["me", "mi", "ja"], "richtig": "mi", "tipp": "mir = mi, an zweiter Stelle."},
            {"frage": "„Govorimo o ___.“ (Wir sprechen über die Arbeit.)", "optionen": ["posao", "posla", "poslu"], "richtig": "poslu", "tipp": "o + Lokativ."},
            {"frage": "„Sviđa ___ se.“ (Es gefällt ihr.)", "optionen": ["joj", "mu", "mi"], "richtig": "joj", "tipp": "ihr = joj, ihm = mu."},
        ],
    },

    "faelle4": {
        "erklaerung": [
            "Instrumental = mit wem? womit? Nach „sa“ (mit) oder ohne Präposition beim Verkehrsmittel: „sa bratom“, „autom“, „vozom“.",
            {"tabelle": [["Geschlecht", "Nominativ", "Instrumental", "Regel"],
                         ["männlich", "brat, auto, voz", "bratom, autom, vozom", "+ om (nach j, č, š, ž: + em: prijateljem)"],
                         ["weiblich", "sestra, kahva", "sestrom, kahvom", "-a → -om"],
                         ["sächlich", "selo, mlijeko", "selom, mlijekom", "-o → -om"]]},
            "Pronomen: sa mnom (mit mir), sa tobom (mit dir), s njim (mit ihm), s njom (mit ihr), sa nama (mit uns), sa vama (mit euch).",
            "Vokativ = die Anrede. Männlich meist + e (brate!, gospodine!, sine!), nach j, č, š, ž + u (prijatelju!). Weiblich auf -a → -o (sestro!, nano!, gospođo!), Kosenamen auf -ica → -ice (Amrice!). Weibliche Vornamen auf -a bleiben meist gleich (Amina!), männliche Vornamen bekommen -e (Ajdine!, Emire!).",
        ],
        "uebungen": [
            {"frage": "„Idem s ___.“ (Ich gehe mit dem Bruder.)", "optionen": ["brata", "bratu", "bratom"], "richtig": "bratom", "tipp": "s/sa + Instrumental: + om."},
            {"frage": "„Putujemo ___.“ (Wir reisen mit dem Auto.)", "optionen": ["auto", "autom", "autu"], "richtig": "autom", "tipp": "Verkehrsmittel: Instrumental ohne Präposition."},
            {"frage": "„Kahva s ___.“ (Kaffee mit Milch.)", "optionen": ["mlijeko", "mlijeka", "mlijekom"], "richtig": "mlijekom", "tipp": "sächlich -o → -om."},
            {"frage": "„Dođi sa ___!“ (Komm mit mir!)", "optionen": ["mene", "mnom", "meni"], "richtig": "mnom", "tipp": "mit mir = sa mnom."},
            {"frage": "Anrede an die Schwester:", "optionen": ["sestra!", "sestro!", "sestru!"], "richtig": "sestro!", "tipp": "weiblich -a → -o."},
            {"frage": "Anrede an den Herrn:", "optionen": ["gospodin!", "gospodine!", "gospodinu!"], "richtig": "gospodine!", "tipp": "männlich + e."},
            {"frage": "Anrede an den Freund:", "optionen": ["prijatelje!", "prijatelju!", "prijatelja!"], "richtig": "prijatelju!", "tipp": "nach j → + u."},
        ],
    },

    "vergangenheit": {
        "erklaerung": [
            "Die Vergangenheit (Perfekt) baut man aus „biti“ in der Gegenwart + dem Partizip auf -o / -la / -lo / -li / -le.",
            {"tabelle": [["Person", "männlich", "weiblich", "Beispiel"],
                         ["ich", "radio sam", "radila sam", "Jučer sam radio. / Jučer sam radila."],
                         ["du", "radio si", "radila si", "Šta si radio? / Šta si radila?"],
                         ["er / sie", "radio je", "radila je", "On je radio. / Ona je radila."],
                         ["wir", "radili smo", "radile smo", "Radili smo cijeli dan."],
                         ["ihr / Sie", "radili ste", "radile ste", "Jeste li radili?"],
                         ["sie (Mehrzahl)", "radili su", "radile su", "Oni su radili."]]},
            "Das Partizip kommt vom Infinitiv: raditi → radio/radila, imati → imao/imala, biti → bio/bila, ići → išao/išla, jesti → jeo/jela, reći → rekao/rekla.",
            "„sam, si, je, smo, ste, su“ stehen an zweiter Stelle im Satz: „Jučer sam bila kod nane“, nicht „Sam jučer bila“. Steht das Subjekt am Anfang, kommt es direkt danach: „Ja sam bila kod nane.“",
        ],
        "uebungen": [
            {"frage": "Eine Frau sagt: „Gestern habe ich gearbeitet.“", "optionen": ["Jučer sam radio.", "Jučer sam radila.", "Jučer radila sam."], "richtig": "Jučer sam radila.", "tipp": "weiblich → -la, „sam“ an zweiter Stelle."},
            {"frage": "„Wir waren in Bosnien.“", "optionen": ["Bili smo u Bosni.", "Smo bili u Bosni.", "Bili su u Bosni."], "richtig": "Bili smo u Bosni.", "tipp": "wir → smo, Partizip -li."},
            {"frage": "„Šta si ___?“ (Was hast du gemacht? – zu einem Mann)", "optionen": ["radio", "radila", "radili"], "richtig": "radio", "tipp": "männlich → -o."},
            {"frage": "Partizip von „ići“ (gehen), männlich:", "optionen": ["išao", "ićio", "idio"], "richtig": "išao", "tipp": "ići ist unregelmäßig: išao / išla."},
            {"frage": "„Ona ___ došla.“ (Sie ist gekommen.)", "optionen": ["je", "si", "su"], "richtig": "je", "tipp": "er/sie → je."},
            {"frage": "„Es war schön.“", "optionen": ["Bio je lijepo.", "Bilo je lijepo.", "Bila je lijepo."], "richtig": "Bilo je lijepo.", "tipp": "unpersönlich „es“ → sächlich -lo."},
        ],
    },

    "zukunft": {
        "erklaerung": [
            "Die Zukunft bildet man mit „htjeti“ in Kurzform + Infinitiv: ću, ćeš, će, ćemo, ćete, će.",
            {"tabelle": [["Person", "Zukunft", "Beispiel"],
                         ["ich", "ću + Infinitiv", "Ja ću raditi. / Radit ću."],
                         ["du", "ćeš", "Ti ćeš doći. / Doći ćeš."],
                         ["er / sie", "će", "On će učiti. / Učit će."],
                         ["wir", "ćemo", "Mi ćemo vidjeti. / Vidjet ćemo."],
                         ["ihr / Sie", "ćete", "Vi ćete putovati."],
                         ["sie (Mehrzahl)", "će", "Oni će doći."]]},
            "Zwei Stellungen: Steht ein Wort davor (ja, sutra, mi), kommt „ću“ an zweite Stelle: „Sutra ću raditi.“ Steht der Infinitiv am Anfang, verliert er das -i: „Radit ću.“ Bei Infinitiven auf -ći bleibt alles: „Doći ću.“ Seit der Rechtschreibung von 2018 darf man bei -ti auch zusammenschreiben: „Radiću.“ Gesprochen wird es immer so.",
            "Verneinung: neću, nećeš, neće, nećemo, nećete, neće: „Neću raditi sutra.“",
        ],
        "uebungen": [
            {"frage": "„Sutra ___ raditi.“ (Morgen werde ich arbeiten.)", "optionen": ["ću", "ćeš", "će"], "richtig": "ću", "tipp": "ich → ću."},
            {"frage": "„Ich werde kommen.“ mit dem Verb am Anfang:", "optionen": ["Doći ću.", "Doć ću.", "Ću doći."], "richtig": "Doći ću.", "tipp": "-ći bleibt ganz, ću dahinter."},
            {"frage": "„Ich werde arbeiten.“ mit dem Verb am Anfang:", "optionen": ["Raditi ću.", "Radit ću.", "Ću raditi."], "richtig": "Radit ću.", "tipp": "-ti verliert das i vor ću."},
            {"frage": "„Mi ___ vidjeti.“ (Wir werden sehen.)", "optionen": ["ću", "ćemo", "ćete"], "richtig": "ćemo", "tipp": "wir → ćemo."},
            {"frage": "„Ich werde morgen nicht arbeiten.“", "optionen": ["Ne ću raditi sutra.", "Neću raditi sutra.", "Ću ne raditi sutra."], "richtig": "Neću raditi sutra.", "tipp": "ne + ću = neću, ein Wort."},
            {"frage": "„Kada ___ doći?“ (Wann wirst du kommen?)", "optionen": ["ću", "ćeš", "ćemo"], "richtig": "ćeš", "tipp": "du → ćeš."},
        ],
    },

    "modal": {
        "erklaerung": [
            "Modalverben stehen vor dem Infinitiv: „Moram raditi“, „Mogu doći“, „Hoću spavati“, „Želim učiti“, „Smijem li pitati?“",
            {"tabelle": [["Verb", "ich", "du", "er / sie", "wir"],
                         ["morati (müssen)", "moram", "moraš", "mora", "moramo"],
                         ["moći (können)", "mogu", "možeš", "može", "možemo"],
                         ["htjeti (wollen)", "hoću", "hoćeš", "hoće", "hoćemo"],
                         ["željeti (möchten)", "želim", "želiš", "želi", "želimo"],
                         ["smjeti (dürfen)", "smijem", "smiješ", "smije", "smijemo"],
                         ["trebati (sollen / brauchen)", "trebam", "trebaš", "treba", "trebamo"]]},
            "„Ne moraš“ heißt „du musst nicht“, aber „ne smiješ“ heißt „du darfst nicht“. Und für Fähigkeiten („ich kann schwimmen“) sagt man „znam plivati“, nicht „mogu“.",
            "Höflicher Wunsch: „Htio bih“ (Mann) / „Htjela bih“ (Frau) = ich hätte gern.",
        ],
        "uebungen": [
            {"frage": "„___ raditi sutra.“ (Ich muss morgen arbeiten.)", "optionen": ["Moram", "Mogu", "Hoću"], "richtig": "Moram", "tipp": "müssen = morati → moram."},
            {"frage": "„___ li mi pomoći?“ (Kannst du mir helfen?)", "optionen": ["Moraš", "Možeš", "Želiš"], "richtig": "Možeš", "tipp": "können = moći → možeš."},
            {"frage": "„Du darfst hier nicht rauchen.“", "optionen": ["Ne moraš ovdje pušiti.", "Ne smiješ ovdje pušiti.", "Ne želiš ovdje pušiti."], "richtig": "Ne smiješ ovdje pušiti.", "tipp": "nicht dürfen = ne smjeti."},
            {"frage": "„Ich kann schwimmen.“ (Fähigkeit)", "optionen": ["Mogu plivati.", "Znam plivati.", "Moram plivati."], "richtig": "Znam plivati.", "tipp": "Gelernte Fähigkeit: znati."},
            {"frage": "Eine Frau sagt: „Ich hätte gern einen Kaffee.“", "optionen": ["Htio bih kahvu.", "Htjela bih kahvu.", "Hoću bih kahvu."], "richtig": "Htjela bih kahvu.", "tipp": "weiblich → htjela bih."},
            {"frage": "„Mi ___ čekati.“ (Wir müssen warten.)", "optionen": ["moram", "moramo", "morate"], "richtig": "moramo", "tipp": "wir → moramo."},
        ],
    },

    "reflexiv": {
        "erklaerung": [
            "Viele Verben haben ein festes „se“ dabei. Es verändert sich nie und steht an zweiter Stelle im Satz: „Zovem se Amina“, „Ja se zovem Amina“, „Kako se zoveš?“",
            {"tabelle": [["Verb", "Bedeutung", "Beispiel"],
                         ["zvati se", "heißen", "Zovem se Ajdin."],
                         ["osjećati se", "sich fühlen", "Osjećam se dobro."],
                         ["radovati se", "sich freuen", "Radujem se!"],
                         ["sjećati se", "sich erinnern", "Sjećam se."],
                         ["naći se", "sich treffen", "Nalazimo se u pet."],
                         ["igrati se", "spielen (Kinder)", "Djeca se igraju."],
                         ["smijati se", "lachen", "Smijem se."]]},
            "Manche Verben gibt es mit und ohne se, mit anderer Bedeutung: prati (waschen) / prati se (sich waschen), zvati (rufen) / zvati se (heißen), igrati (ein Spiel spielen) / igrati se (spielen wie Kinder).",
            "„Sviđa mi se“ (es gefällt mir) hat sogar zwei kleine Wörter: mi + se, immer in dieser Reihenfolge.",
        ],
        "uebungen": [
            {"frage": "„Ich heiße Amina.“", "optionen": ["Zovem Amina.", "Zovem se Amina.", "Se zovem Amina."], "richtig": "Zovem se Amina.", "tipp": "se an zweiter Stelle."},
            {"frage": "„Kako ___ zoveš?“ (Wie heißt du?)", "optionen": ["se", "si", "te"], "richtig": "se", "tipp": "zvati se → se."},
            {"frage": "„Ich fühle mich gut.“", "optionen": ["Osjećam dobro.", "Osjećam se dobro.", "Se osjećam dobro."], "richtig": "Osjećam se dobro.", "tipp": "osjećati se braucht se."},
            {"frage": "„Die Kinder spielen.“", "optionen": ["Djeca igraju.", "Djeca se igraju.", "Djeca igraju se."], "richtig": "Djeca se igraju.", "tipp": "se an zweiter Stelle: Djeca se igraju."},
            {"frage": "„Es gefällt mir.“", "optionen": ["Sviđa se mi.", "Sviđa mi se.", "Mi sviđa se."], "richtig": "Sviđa mi se.", "tipp": "Reihenfolge: mi, dann se."},
            {"frage": "„Ich wasche das Auto.“ (nicht mich!)", "optionen": ["Perem se auto.", "Perem auto.", "Perem auto se."], "richtig": "Perem auto.", "tipp": "Ohne se: etwas anderes waschen."},
        ],
    },

    "adjektive": {
        "erklaerung": [
            "Adjektive richten sich nach dem Substantiv: velik grad (m), velika kuća (w), veliko selo (s). In der Mehrzahl: veliki gradovi, velike kuće, velika sela.",
            "Steigerung: meist mit -iji: star → stariji (älter), nov → noviji, jeftin → jeftiniji. Kurze Adjektive ändern den Stamm: velik → veći, mali → manji, dobar → bolji, loš → gori, lijep → ljepši, skup → skuplji, brz → brži, mlad → mlađi.",
            {"tabelle": [["Grundform", "Vergleich (-er)", "Superlativ (am -sten)"],
                         ["velik", "veći", "najveći"],
                         ["dobar", "bolji", "najbolji"],
                         ["lijep", "ljepši", "najljepši"],
                         ["star", "stariji", "najstariji"],
                         ["skup", "skuplji", "najskuplji"]]},
            "Der Superlativ ist immer naj- + Vergleichsform. „Als“ heißt „nego“ oder „od“: „Sarajevo je veće nego Mostar“ oder „Sarajevo je veće od Mostara“ (od + Genitiv).",
        ],
        "uebungen": [
            {"frage": "„___ kuća“ (großes Haus)", "optionen": ["velik", "velika", "veliko"], "richtig": "velika", "tipp": "kuća ist weiblich."},
            {"frage": "Vergleichsform von „dobar“ (gut)?", "optionen": ["dobriji", "bolji", "najbolji"], "richtig": "bolji", "tipp": "Unregelmäßig: dobar → bolji."},
            {"frage": "„am größten“?", "optionen": ["veći", "najveći", "najvelik"], "richtig": "najveći", "tipp": "naj- + Vergleichsform."},
            {"frage": "„Moj brat je ___ od mene.“ (Mein Bruder ist älter als ich.)", "optionen": ["star", "stariji", "najstariji"], "richtig": "stariji", "tipp": "Vergleich: -iji."},
            {"frage": "„Sarajevo je veće ___ Mostara.“", "optionen": ["od", "nego", "sa"], "richtig": "od", "tipp": "„Mostara“ ist Genitiv → od."},
            {"frage": "„Sarajevo je veće ___ Mostar.“", "optionen": ["od", "nego", "za"], "richtig": "nego", "tipp": "„Mostar“ im Nominativ → nego."},
            {"frage": "Vergleichsform von „skup“ (teuer)?", "optionen": ["skupiji", "skuplji", "skupši"], "richtig": "skuplji", "tipp": "p + j → plj."},
        ],
    },

    "mengen": {
        "erklaerung": [
            "Nach Zahlen ändert sich das Substantiv, und zwar in drei Gruppen:",
            {"tabelle": [["Zahl", "Form", "männlich", "weiblich", "sächlich"],
                         ["1", "wie Nominativ", "jedan brat", "jedna sestra", "jedno selo"],
                         ["2, 3, 4", "Genitiv Einzahl", "dva brata", "dvije sestre", "dva sela"],
                         ["5 und mehr", "Genitiv Mehrzahl", "pet braće", "pet sestara", "pet sela"]]},
            "Die Zahl selbst richtet sich nach dem Geschlecht: jedan/jedna/jedno, dva/dvije, ab drei ist sie gleich: tri, četiri, pet.",
            "Bei 21, 22, 31 gilt wieder die letzte Ziffer: dvadeset jedan brat, dvadeset dva brata, dvadeset pet braće.",
            "Alter: „Imam trideset godina“ (wörtlich: ich habe dreißig Jahre). Uhrzeit: „u pet sati“, „u dva sata“.",
        ],
        "uebungen": [
            {"frage": "„Imam dva ___.“ (Ich habe zwei Brüder.)", "optionen": ["brat", "brata", "braće"], "richtig": "brata", "tipp": "2, 3, 4 → Genitiv Einzahl."},
            {"frage": "„Imam pet ___.“ (Ich habe fünf Brüder.)", "optionen": ["brat", "brata", "braće"], "richtig": "braće", "tipp": "5+ → Genitiv Mehrzahl."},
            {"frage": "„___ sestre“ (zwei Schwestern)", "optionen": ["dva", "dvije", "dvoje"], "richtig": "dvije", "tipp": "weiblich → dvije."},
            {"frage": "„Imam trideset ___.“ (Ich bin dreißig Jahre alt.)", "optionen": ["godina", "godine", "godinu"], "richtig": "godina", "tipp": "30 → Genitiv Mehrzahl: godina."},
            {"frage": "„Ostajemo tri ___.“ (Wir bleiben drei Tage.)", "optionen": ["dan", "dana", "dani"], "richtig": "dana", "tipp": "3 → Genitiv Einzahl: dana."},
            {"frage": "„___ kahve, molim.“ (Zwei Kaffee, bitte.)", "optionen": ["Dva", "Dvije", "Pet"], "richtig": "Dvije", "tipp": "kahva ist weiblich → dvije kahve."},
        ],
    },

    # ---- B1 (Update 1.3, 07.11.2026) ----
    # Zehn Lektionen, von Ajdin am 07.11.2026 abgenommen. Der Schlüssel ist
    # das Level, über jeder Lektion steht ihr Name. Reihenfolge wie im Lernweg.

    # verbpaare
    "tun_machen": {
        "erklaerung": [
            "Viele Verben gibt es als Paar, auf Deutsch heißen beide gleich: kupovati und kupiti = kaufen. Darum stehen in der App oft zwei Wörter dafür. Unvollendet heißt: Die Sache läuft, dauert oder wiederholt sich („Kupujem hljeb.“). Vollendet heißt: Sie passiert einmal und ist erledigt („Kupio sam hljeb.“).",
            {"tabelle": [["unvollendet", "vollendet", "Deutsch"],
                         ["pisati", "napisati", "(fertig) schreiben"],
                         ["čitati", "pročitati", "(durch)lesen"],
                         ["jesti", "pojesti", "(auf)essen"]]},
            "Eselsbrücke: Passt „aufessen“, „durchlesen“ oder „fertig schreiben“, nimm das vollendete Verb. Passt „gerade dabei“, „lange“ oder „immer wieder“, nimm das unvollendete Verb.",
            {"tabelle": [["Hinweis im Satz", "Verb", "Beispiel"],
                         ["cijeli dan (den ganzen Tag)", "unvollendet", "Jučer sam pisao cijeli dan."],
                         ["za pet minuta (in fünf Minuten)", "vollendet", "Napisao sam pismo za pet minuta."],
                         ["kad (wenn es erledigt ist)", "vollendet", "Kad kupim hljeb, doći ću kući."]]},
            "Jetzt gerade geht nur das unvollendete Verb: „Šta radiš?“ – „Pišem pismo.“",
        ],
        "uebungen": [
            {"frage": "„Jučer sam ___ cijeli dan.“ (Gestern habe ich den ganzen Tag geschrieben.)", "optionen": ["pisao", "napisao", "pisati"], "richtig": "pisao", "tipp": "cijeli dan: Es lief den ganzen Tag → unvollendet."},
            {"frage": "„Jučer sam ___ pismo za pet minuta.“ (Gestern habe ich einen Brief in fünf Minuten geschrieben.)", "optionen": ["pisao", "napisati", "napisao"], "richtig": "napisao", "tipp": "za pet minuta: in fünf Minuten fertig → vollendet."},
            {"frage": "„Jučer sam ___ cijeli dan.“ (Gestern habe ich den ganzen Tag gelesen. – eine Frau spricht)", "optionen": ["pročitala", "čitala", "čitati"], "richtig": "čitala", "tipp": "cijeli dan: Es lief den ganzen Tag → unvollendet."},
            {"frage": "„Kad ___ knjigu, ići ću spavati.“ (Wenn ich das Buch durchgelesen habe, gehe ich schlafen.)", "optionen": ["pročitam", "čitam", "čitati"], "richtig": "pročitam", "tipp": "Durchgelesen, die Sache ist erledigt → vollendet."},
            {"frage": "„Nana je jučer ___ cijeli dan.“ (Oma hat gestern den ganzen Tag gekocht.)", "optionen": ["skuhala", "kuhati", "kuhala"], "richtig": "kuhala", "tipp": "cijeli dan: Es lief den ganzen Tag → unvollendet."},
            {"frage": "„Kad ___ hljeb, doći ću kući.“ (Wenn ich das Brot gekauft habe, komme ich nach Hause.)", "optionen": ["kupujem", "kupim", "kupiti"], "richtig": "kupim", "tipp": "Erst ist das Brot gekauft, dann kommst du → vollendet."},
            {"frage": "„Šta radiš? – ___ pismo.“ (Was machst du? – Ich schreibe einen Brief.)", "optionen": ["Pišem", "Napišem", "Pisati"], "richtig": "Pišem", "tipp": "Jetzt gerade → immer das unvollendete Verb."},
        ],
    },

    # praesensstaemme
    "paare_nachholen": {
        "erklaerung": [
            "Bei vielen Verben ändert sich in der Gegenwart der Stamm: pisati → „pišem“, nicht „pisam“. Am Infinitiv sieht man das nicht: čekati bleibt regelmäßig (čekam), plakati wechselt (plačem). Darum lernt man die ich-Form gleich mit.",
            {"tabelle": [["Laut", "Beispiele"],
                         ["s → š", "pisati → pišem, plesati → plešem, rezervisati → rezervišem"],
                         ["z → ž", "kazati → kažem, rezati → režem"],
                         ["k → č", "plakati → plačem, skakati → skačem"],
                         ["g → ž", "lagati → lažem, pomagati → pomažem"],
                         ["t → ć", "kretati → krećem"]]},
            "Der neue Stamm gilt in allen Personen: pišem, pišeš, piše, pišemo, pišete. Nur „oni“ endet auf -u: pišu, kažu, plaču. Vergangenheit und Zukunft bleiben beim Infinitiv: pisao sam, pisat ću.",
            {"tabelle": [["Muster", "Beispiele"],
                         ["-ovati, oft auch -ivati → -ujem", "kupovati → kupujem, pokazivati → pokazujem"],
                         ["-davati → -dajem", "davati → dajem, prodavati → prodajem"],
                         ["kurze Verben: + j", "piti → pijem, čuti → čujem"],
                         ["neuer Vokal im Stamm", "zvati → zovem, prati → perem, slati → šaljem"],
                         ["einzeln merken", "jesti → jedem, uzeti → uzmem, početi → počnem"]]},
        ],
        "uebungen": [
            {"frage": "„___ pismo nani.“ (Ich schreibe Oma einen Brief.)", "optionen": ["Pišem", "Pisam", "Pisim"], "richtig": "Pišem", "tipp": "pisati → pišem: s wird zu š."},
            {"frage": "„Šta ___?“ (Was sagst du?)", "optionen": ["kažeš", "kazaš", "kažiš"], "richtig": "kažeš", "tipp": "kazati → kažem, kažeš: z wird zu ž."},
            {"frage": "„Ne ___, dobro sam.“ (Ich weine nicht, mir geht es gut.)", "optionen": ["plačem", "plakam", "plačim"], "richtig": "plačem", "tipp": "plakati → plačem: k wird zu č."},
            {"frage": "„___ autobus.“ (Ich warte auf den Bus.)", "optionen": ["Čekam", "Čečem", "Čekem"], "richtig": "Čekam", "tipp": "čekati bleibt regelmäßig. Nicht jedes -kati wechselt."},
            {"frage": "„Oni ___ pismo nani.“ (Sie schreiben Oma einen Brief.)", "optionen": ["piše", "pišemo", "pišu"], "richtig": "pišu", "tipp": "Ich-Form auf -em → oni auf -u."},
            {"frage": "„___ ti poruku.“ (Ich schicke dir eine Nachricht.)", "optionen": ["Šaljem", "Slam", "Slajem"], "richtig": "Šaljem", "tipp": "slati → šaljem, šalješ, šalje: einfach merken."},
            {"frage": "„Svako jutro ___ hljeb.“ (Ich kaufe jeden Morgen Brot.)", "optionen": ["kupujem", "kupovam", "kupovim"], "richtig": "kupujem", "tipp": "-ovati wird zu -ujem."},
        ],
    },

    # befehlsform
    "benehmen": {
        "erklaerung": [
            "Die Befehlsform kommt von der Form für „oni“: Vokal + -ju oder -je wird zu -j, alles andere zu -i. Für „ihr“ und „Sie“ kommt -te dazu.",
            {"tabelle": [["Infinitiv", "oni", "du", "ihr / Sie"],
                         ["čitati (lesen)", "čitaju", "čitaj!", "čitajte!"],
                         ["piti (trinken)", "piju", "pij!", "pijte!"],
                         ["bojati se (Angst haben)", "boje se", "boj se!", "bojte se!"],
                         ["raditi (arbeiten)", "rade", "radi!", "radite!"],
                         ["ići (gehen)", "idu", "idi!", "idite!"]]},
            "Merken: biti → budi!, reći → reci!, pomoći → pomozi! Kleine Wörter folgen direkt: „Vrati se!“",
            "Verbieten: nemoj oder nemojte + Infinitiv: „Nemoj ići!“, „Nemojte pušiti!“ Man hört auch: „Nemoj da ideš.“ Kürzer oft ne + Befehlsform: „Ne brini!“ Im Zweifel nimm nemoj.",
            "„Hajde!“ heißt „Komm!“ oder „Los!“. „Lass uns …“: „hajde da“ + Gegenwart oder „hajmo“ + Infinitiv: „Hajde da promijenimo temu.“, „Hajmo popiti kahvu!“",
        ],
        "uebungen": [
            {"frage": "„___ kući!“ (Geh nach Hause!)", "optionen": ["Ide", "Idi", "Idu"], "richtig": "Idi", "tipp": "oni idu → idi! Ide heißt „er geht“, idu „sie gehen“."},
            {"frage": "„___ ovaj tekst do sutra.“ (Lies diesen Text bis morgen.)", "optionen": ["Pročitaj", "Pročitaji", "Pročita"], "richtig": "Pročitaj", "tipp": "oni pročitaju: Vokal + -ju → -j."},
            {"frage": "„___ ovdje, molim Vas.“ (Warten Sie bitte hier.)", "optionen": ["Sačekaj", "Sačekajmo", "Sačekajte"], "richtig": "Sačekajte", "tipp": "Höflich (Sie) → Endung -te."},
            {"frage": "„___ mi istinu, molim te.“ (Sag mir bitte die Wahrheit.)", "optionen": ["Reći", "Reci", "Rečem"], "richtig": "Reci", "tipp": "reći ist der Infinitiv, der Befehl heißt reci!"},
            {"frage": "„___ vikati, dijete spava.“ (Schrei nicht, das Kind schläft.)", "optionen": ["Nemoj", "Nema", "Nisam"], "richtig": "Nemoj", "tipp": "Verbot: nemoj + Infinitiv."},
            {"frage": "„Geh nicht!“", "optionen": ["Nemoj idi!", "Nemoj ideš!", "Nemoj ići!"], "richtig": "Nemoj ići!", "tipp": "Nach nemoj kommt der Infinitiv: ići. Oder mit da: Nemoj da ideš."},
            {"frage": "„Lass uns das Thema wechseln.“", "optionen": ["Idi da promijenimo temu.", "Hajde da promijenimo temu.", "Nemoj promijeniti temu."], "richtig": "Hajde da promijenimo temu.", "tipp": "Lass uns … = hajde da + Gegenwart."},
        ],
    },

    # zeitangaben
    "zeitangaben": {
        "erklaerung": [
            "Ordnungszahlen sind Adjektive: prvi dan, prva kuća, prvo dijete. Meist hängt man -i an: pet → peti, deset → deseti. Bei zusammengesetzten Zahlen ändert sich nur die letzte: dvadeset prvi.",
            {"tabelle": [["Zahl", "der …", "am …"],
                         ["1.", "prvi", "prvog"],
                         ["2.", "drugi", "drugog"],
                         ["3.", "treći", "trećeg"],
                         ["4.", "četvrti", "četvrtog"],
                         ["7.", "sedmi", "sedmog"],
                         ["8.", "osmi", "osmog"]]},
            "Welcher Tag ist es? Nominativ: „Danas je šesti novembar.“ An welchem Tag? Genitiv ohne Präposition, auch beim Monat: „Rođen sam petog marta.“ Bei -bar fällt das a weg: oktobar → oktobra. Und juni → juna.",
            "Im Jahr wird nur die letzte Zahl zur Ordnungszahl: „hiljadu devetsto osamdeset pete godine“ (1985).",
            {"tabelle": [["Wann?", "Form", "Beispiel"],
                         ["am Freitag", "u + Akkusativ", "u petak, u srijedu"],
                         ["freitags", "Instrumental", "petkom, srijedom"],
                         ["im März", "u + Lokativ", "u martu, u julu"],
                         ["im Sommer, im Herbst", "ohne u / mit u", "ljeti, zimi / u proljeće, u jesen"],
                         ["letzte Woche", "meist Genitiv", "prošle sedmice, ove godine"],
                         ["in / vor zwei Tagen", "za / prije", "za dva dana / prije dva dana"]]},
            "„Pola pet“ ist wie „halb fünf“, also 4:30.",
        ],
        "uebungen": [
            {"frage": "„Danas je ___ juni.“ (Heute ist der 7. Juni.)", "optionen": ["sedmi", "sedmog", "sedam"], "richtig": "sedmi", "tipp": "Welcher Tag ist es? Nominativ. Aus sedam wird sedmi."},
            {"frage": "„Rođena sam ___.“ (Ich bin am 3. Oktober geboren.)", "optionen": ["trećeg oktobra", "treći oktobar", "trećeg oktobar"], "richtig": "trećeg oktobra", "tipp": "An welchem Tag? Beides im Genitiv, oktobar verliert das a."},
            {"frage": "„Rođen sam hiljadu devetsto osamdeset ___ godine.“ (Ich bin 1985 geboren.)", "optionen": ["pete", "peti", "pet"], "richtig": "pete", "tipp": "Nur die letzte Zahl wird Ordnungszahl, im Genitiv wie godine."},
            {"frage": "„Mittwochs arbeite ich nicht.“", "optionen": ["Srijedom ne radim.", "Srijeda ne radim.", "U srijedi ne radim."], "richtig": "Srijedom ne radim.", "tipp": "Jede Woche: Instrumental. Nur dieses Mal: u srijedu."},
            {"frage": "„Prošle ___ smo bili kod nane.“ (Letzte Woche waren wir bei Oma.)", "optionen": ["sedmice", "sedmica", "sedmicu"], "richtig": "sedmice", "tipp": "Zwei Wörter ohne Präposition: Genitiv."},
            {"frage": "„Vidimo se ___ dva dana.“ (Wir sehen uns in zwei Tagen.)", "optionen": ["za", "prije", "od"], "richtig": "za", "tipp": "In zwei Tagen = za, vor zwei Tagen = prije."},
            {"frage": "„Dolazim u ___.“ (Ich komme um 4:30.)", "optionen": ["pola pet", "pola četiri", "pet i po"], "richtig": "pola pet", "tipp": "pola pet = halb fünf = 4:30."},
        ],
    },

    # sammelzahlen
    "menge_teil": {
        "erklaerung": [
            "Aus Fragewörtern werden mit ne- Wörter wie „jemand“ und mit ni- Wörter wie „niemand“. Bei ni-Wörtern steht auch ne am Verb: „Ništa ne znam.“",
            {"tabelle": [["Frage", "ne-", "ni-"],
                         ["ko? (wer)", "neko (jemand)", "niko (niemand)"],
                         ["šta? (was)", "nešto (etwas)", "ništa (nichts)"],
                         ["gdje? (wo)", "negdje (irgendwo)", "nigdje (nirgendwo)"],
                         ["kada? (wann)", "nekad (manchmal, früher)", "nikad (nie)"]]},
            "Beugung wie ko und šta: nekoga, nikoga; nečega, ničega. Mit Präposition trennt sich ni ab: ni s kim (mit niemandem), ni o čemu (über nichts). Bei ne- bleibt es zusammen: s nekim, o nečemu.",
            "Sammelzahlen zählen Personen: dvoje für gemischte Gruppen und immer bei djeca („Imam dvoje djece“), dvojica nur für Männer, mit Verb in der Mehrzahl („Dvojica braće žive u Njemačkoj“). Auch „dva brata“ bleibt richtig.",
            {"tabelle": [["Wer?", "2", "3", "4", "beide"],
                         ["gemischt, Kinder", "dvoje", "troje", "četvero / četvoro", "oboje"],
                         ["nur Männer", "dvojica", "trojica", "četvorica", "obojica"],
                         ["nur Frauen", "dvije", "tri", "četiri", "obje"]]},
        ],
        "uebungen": [
            {"frage": "„___ kuca na vrata.“ (Jemand klopft an die Tür.)", "optionen": ["Neko", "Niko", "Nešto"], "richtig": "Neko", "tipp": "jemand = neko, niemand = niko."},
            {"frage": "„___ nisam kupio.“ (Ich habe nichts gekauft.)", "optionen": ["Ništa", "Nešto", "Niko"], "richtig": "Ništa", "tipp": "nichts = ništa, dazu die Verneinung: nisam."},
            {"frage": "„Ich sehe niemanden.“", "optionen": ["Nikoga ne vidim.", "Nikoga vidim.", "Niko ne vidim."], "richtig": "Nikoga ne vidim.", "tipp": "Akkusativ nikoga, dazu ne am Verb."},
            {"frage": "„Ich spreche mit niemandem.“", "optionen": ["Ni s kim ne govorim.", "Ni s kim govorim.", "Ni s koga ne govorim."], "richtig": "Ni s kim ne govorim.", "tipp": "ni + s + kim, dazu ne am Verb."},
            {"frage": "„Imam ___ djece.“ (Ich habe zwei Kinder.)", "optionen": ["dvoje", "dva", "dvije"], "richtig": "dvoje", "tipp": "Bei djeca immer die Sammelzahl."},
            {"frage": "„Amina i Emir: ___ žive u Tuzli.“ (Amina und Emir: Beide leben in Tuzla.)", "optionen": ["oboje", "obojica", "obje"], "richtig": "oboje", "tipp": "Frau und Mann: oboje. Nur Männer: obojica. Nur Frauen: obje."},
            {"frage": "„___ braće žive u Njemačkoj.“ (Zwei Brüder leben in Deutschland.)", "optionen": ["Dvojica", "Dva", "Dvije"], "richtig": "Dvojica", "tipp": "Nur Männer: dvojica, danach braće. Oder einfach: dva brata."},
        ],
    },

    # konditional
    "denken_entscheiden": {
        "erklaerung": [
            "Der Konditional sagt, was man tun würde: bih + Partizip wie in der Vergangenheit. „Došao bih.“ (Ich würde kommen.)",
            {"tabelle": [["Person", "männlich", "weiblich"],
                         ["ich", "bih došao", "bih došla"],
                         ["du, er / sie", "bi došao", "bi došla"],
                         ["wir", "bismo došli", "bismo došle"],
                         ["ihr / Sie", "biste došli", "biste došle"],
                         ["sie (Mehrzahl)", "bi došli", "bi došle"]]},
            "„bih“ steht wie „sam“ an zweiter Stelle: „Ja bih došao“ oder „Došao bih“, nicht „Bih došao“. „ne“ steht getrennt davor: „Ne bih došao.“ Gesprochen hört man oft „bi“ für alle Personen.",
            {"tabelle": [["Wort", "Bedeutung", "Beispiel"],
                         ["kad bih", "wenn ich … würde / hätte", "Kad bih imao vremena, došao bih. – Wenn ich Zeit hätte, würde ich kommen. Genauso geht: Da imam vremena, došao bih."],
                         ["da bih", "um … zu", "Učim da bih razumio nanu. – Ich lerne, um die Oma zu verstehen."],
                         ["da ne bih", "um nicht … zu", "Žurim se da ne bih zakasnio. – Ich beeile mich, um nicht zu spät zu kommen."]]},
            "Nach „kad“ und „da“ ändert sich die Form mit: „Kad bismo imali auto, išli bismo na more.“ Höflich: „Da li biste mi mogli pomoći?“",
        ],
        "uebungen": [
            {"frage": "„Da li ___ mi pomogao?“ (Würdest du mir helfen?)", "optionen": ["bi", "bismo", "biste"], "richtig": "bi", "tipp": "du → bi. „bismo“ und „biste“ brauchen ein Partizip auf -li."},
            {"frage": "Eine Frau sagt: „Ich würde kommen, aber ich habe keine Zeit.“", "optionen": ["Došao bih, ali nemam vremena.", "Došla bih, ali nemam vremena.", "Doći bih, ali nemam vremena."], "richtig": "Došla bih, ali nemam vremena.", "tipp": "weiblich → -la. Immer das Partizip, nie der Infinitiv."},
            {"frage": "„Kad ___ imali auto, išli bismo na more.“ (Wenn wir ein Auto hätten, würden wir ans Meer fahren.)", "optionen": ["bih", "ćemo", "bismo"], "richtig": "bismo", "tipp": "wir → bismo, auch nach „kad“."},
            {"frage": "„Könnten Sie mir helfen?“", "optionen": ["Da li bih mi mogli pomoći?", "Da li biste mi mogli pomoći?", "Da li biste mi moći pomoći?"], "richtig": "Da li biste mi mogli pomoći?", "tipp": "Sie → biste, dazu das Partizip „mogli“."},
            {"frage": "„Ich würde das nicht sagen.“", "optionen": ["Nebih to rekao.", "Bih ne to rekao.", "Ne bih to rekao."], "richtig": "Ne bih to rekao.", "tipp": "„ne“ steht direkt davor und wird getrennt geschrieben."},
            {"frage": "„Učim bosanski ___ razumio nanu.“ (Ich lerne Bosnisch, um die Oma zu verstehen.)", "optionen": ["da bih", "da bismo", "da biste"], "richtig": "da bih", "tipp": "um zu = da + bih, bi, bismo, biste. Hier: ich → da bih."},
            {"frage": "„Žurim se ___ zakasnio.“ (Ich beeile mich, um nicht zu spät zu kommen.)", "optionen": ["da bih ne", "da ne bih", "bih da ne"], "richtig": "da ne bih", "tipp": "um nicht zu = da ne bih."},
        ],
    },

    # besitzadjektive
    "menschen": {
        "erklaerung": [
            "Aus dem Besitzer wird ein Adjektiv, wenn er eine einzelne, bekannte Person ist: „Aminina kuća“ (Aminas Haus), „bratov auto“ (das Auto des Bruders). Die Frage dazu: „Čija je ovo kuća?“",
            {"tabelle": [["Besitzer", "Endung", "Beispiele"],
                         ["männlich, auf Konsonant, dazu babo", "-ov", "brat → bratov, babo → babov"],
                         ["männlich, nach j, lj, nj, č, ć, š, ž", "-ev", "prijatelj → prijateljev, muž → mužev"],
                         ["auf -a (auch Männer), dazu dedo", "-in", "Amina → Aminin, sestra → sestrin, komšija → komšijin, dedo → dedin"],
                         ["zum Merken", "-ev / -in", "otac → očev, majka → majčin"]]},
            "Die Endung richtet sich nach dem Besitz, nicht nach dem Besitzer, und wird wie ein Adjektiv gebeugt: „u sestrinoj kući“.",
            {"tabelle": [["Besitz", "vom Bruder", "von Amina"],
                         ["männlich: auto", "bratov auto", "Aminin auto"],
                         ["weiblich: kuća", "bratova kuća", "Aminina kuća"],
                         ["sächlich: dijete", "bratovo dijete", "Aminino dijete"],
                         ["Mehrzahl: prijatelji", "bratovi prijatelji", "Aminini prijatelji"]]},
            "Hat der Besitzer ein Wort bei sich oder sind es mehrere, steht der Genitiv: „auto mog brata“, „kuća mojih roditelja“.",
        ],
        "uebungen": [
            {"frage": "„___ kuća“ (Aminas Haus)", "optionen": ["Aminin", "Aminina", "Aminino"], "richtig": "Aminina", "tipp": "kuća ist weiblich → Aminina."},
            {"frage": "„___ telefon“ (das Telefon des Bruders)", "optionen": ["bratov", "bratova", "bratovo"], "richtig": "bratov", "tipp": "telefon ist männlich → bratov."},
            {"frage": "„Bili smo u ___ kući.“ (Wir waren im Haus der Schwester.)", "optionen": ["sestrinoj", "sestrovoj", "sestrina"], "richtig": "sestrinoj", "tipp": "sestra endet auf -a → -in. Nach u + Lokativ: -oj."},
            {"frage": "„___ auto“ (das Auto des Freundes)", "optionen": ["prijateljev", "prijateljov", "prijateljin"], "richtig": "prijateljev", "tipp": "Nach lj steht -ev statt -ov."},
            {"frage": "„___ kuća“ (das Haus der Mutter)", "optionen": ["majčina", "majkova", "majčova"], "richtig": "majčina", "tipp": "majka → majčin: k wird zu č."},
            {"frage": "„___ kuća“ (das Haus des Vaters)", "optionen": ["očeva", "otacova", "ocova"], "richtig": "očeva", "tipp": "otac → očev: einfach merken."},
            {"frage": "„___ kuća“ (Papas Haus)", "optionen": ["babova", "babina", "babovo"], "richtig": "babova", "tipp": "babo bekommt -ov, kuća ist weiblich → babova. babin gehört zu baba (Oma)."},
            {"frage": "„das Auto meines Bruders“", "optionen": ["auto mog brata", "mog bratov auto", "moj bratov auto"], "richtig": "auto mog brata", "tipp": "Mit „mog“ dabei steht der Genitiv."},
        ],
    },

    # futur2
    "frueher_spaeter": {
        "erklaerung": [
            "Für die Zukunft steht nach „kad“ und „ako“ oft budem + Partizip (Futur II): „Kad budem imao vremena, doći ću.“ (Wenn ich Zeit habe, komme ich.)",
            {"tabelle": [["Person", "männlich", "weiblich"],
                         ["ich", "budem imao", "budem imala"],
                         ["du", "budeš imao", "budeš imala"],
                         ["er / sie", "bude imao", "bude imala"],
                         ["wir", "budemo imali", "budemo imale"],
                         ["ihr / Sie", "budete imali", "budete imale"],
                         ["sie (Mehrzahl)", "budu imali", "budu imale"]]},
            "Nur im Nebensatz, der Hauptsatz steht in der Zukunft oder als Befehl. „ću“ gehört nicht hinter „kad“, nur in der Frage: „Kad ćeš doći?“",
            "Bei „biti“ reicht budem: „Kad budem u Sarajevu, javit ću ti se.“ „ne“ steht getrennt davor: „Ako ne budem imao vremena, neću doći.“",
            "Bei vollendeten Verben (doći, stići) meist die Gegenwart: „Kad stignem, javit ću ti se.“ Auch nach „ako“: „Ako imam vremena, doći ću.“",
        ],
        "uebungen": [
            {"frage": "„Kad ___ imao vremena, doći ću.“ (Wenn ich Zeit habe, komme ich.)", "optionen": ["bih", "budem", "ću"], "richtig": "budem", "tipp": "Zukunft nach „kad“: budem + Partizip. „Kad bih“ hieße „wenn ich hätte“."},
            {"frage": "„Kad ___ imala vremena, javi se.“ (Wenn du Zeit hast, melde dich. – zu einer Frau)", "optionen": ["budeš", "ćeš", "budete"], "richtig": "budeš", "tipp": "du → budeš, Frau → imala."},
            {"frage": "„Kad ___ imali vremena, javite se.“ (Wenn Sie Zeit haben, melden Sie sich. – höflich)", "optionen": ["budem", "bude", "budete"], "richtig": "budete", "tipp": "Sie → budete, dazu das Partizip auf -li."},
            {"frage": "„Wenn wir Zeit haben, fahren wir ans Meer.“", "optionen": ["Kad budemo imati vremena, ići ćemo na more.", "Kad budemo imali vremena, ići ćemo na more.", "Kad ćemo imati vremena, ići ćemo na more."], "richtig": "Kad budemo imali vremena, ići ćemo na more.", "tipp": "budemo + Partizip, nicht der Infinitiv."},
            {"frage": "„Wenn ich in Sarajevo bin, melde ich mich bei dir.“", "optionen": ["Kad budem u Sarajevu, javit ću ti se.", "Kad ću u Sarajevu, javit ću ti se.", "Kad bih u Sarajevu, javit ću ti se."], "richtig": "Kad budem u Sarajevu, javit ću ti se.", "tipp": "Bei „biti“ reicht budem allein."},
            {"frage": "„Kad ___, javit ću ti se.“ (Wenn ich ankomme, melde ich mich bei dir.)", "optionen": ["stići ću", "stignem", "stigao"], "richtig": "stignem", "tipp": "Vollendetes Verb: einfach die Gegenwart."},
            {"frage": "„Ako ___ imao vremena, neću doći.“ (Wenn ich keine Zeit habe, komme ich nicht.)", "optionen": ["budem ne", "nebudem", "ne budem"], "richtig": "ne budem", "tipp": "„ne“ steht direkt vor budem und wird getrennt geschrieben."},
        ],
    },

    # relativsaetze
    "saetze_verbinden": {
        "erklaerung": [
            "„koji“ entspricht „der, die, das“. Geschlecht und Zahl kommen vom Wort davor, der Fall aus dem Nebensatz: „Čovjek koji radi“ (Nominativ), „Čovjek kojeg vidim“ (Akkusativ).",
            {"tabelle": [["Einzahl", "männlich", "weiblich", "sächlich"],
                         ["Nominativ", "koji", "koja", "koje"],
                         ["Akkusativ", "kojeg (auch koga), unbelebt: koji", "koju", "koje"],
                         ["Genitiv", "kojeg (auch koga)", "koje", "kojeg (auch koga)"],
                         ["Dativ / Lokativ", "kojem (auch kome)", "kojoj", "kojem (auch kome)"],
                         ["Instrumental", "kojim", "kojom", "kojim"]]},
            {"tabelle": [["Mehrzahl", "männlich", "weiblich", "sächlich"],
                         ["Nominativ", "koji", "koje", "koja"],
                         ["Akkusativ", "koje", "koje", "koja"],
                         ["Genitiv", "kojih", "kojih", "kojih"],
                         ["sonst", "kojima", "kojima", "kojima"]]},
            "Eine Präposition steht davor, kleine Wörter direkt dahinter: „Kuća u kojoj živim“, „Knjiga koju sam ti kupila“.",
            "Nach sve, ono, nešto und ništa steht „što“: „Sve što znam“, „To je ono što želim“.",
            "„čiji“ (dessen, deren) richtet sich nach dem Wort dahinter, nicht nach dem Besitzer: „Žena čiji muž radi sa mnom“ (die Frau, deren Mann …).",
        ],
        "uebungen": [
            {"frage": "„To je čovjek ___ živi pored nas.“ (Das ist der Mann, der neben uns wohnt.)", "optionen": ["kojeg", "koji", "kojem"], "richtig": "koji", "tipp": "Er wohnt neben uns: Nominativ → koji."},
            {"frage": "„Čovjek ___ vidiš je moj babo.“ (Der Mann, den du siehst, ist mein Papa.)", "optionen": ["koji", "kojem", "kojeg"], "richtig": "kojeg", "tipp": "Du siehst ihn: Akkusativ, männlich und belebt → kojeg, auch koga."},
            {"frage": "„Telefon ___ sam kupio je skup.“ (Das Telefon, das ich gekauft habe, ist teuer.)", "optionen": ["koji", "koje", "koju"], "richtig": "koji", "tipp": "telefon ist männlich und unbelebt: Akkusativ wie Nominativ → koji."},
            {"frage": "„Kuća u ___ živim je stara.“ (Das Haus, in dem ich wohne, ist alt.)", "optionen": ["koja", "kojoj", "koju"], "richtig": "kojoj", "tipp": "Wo? u + Lokativ, weiblich → kojoj."},
            {"frage": "„Žena s ___ radim je iz Mostara.“ (Die Frau, mit der ich arbeite, ist aus Mostar.)", "optionen": ["kojom", "koja", "kojoj"], "richtig": "kojom", "tipp": "s + Instrumental, weiblich → kojom."},
            {"frage": "„To je sve ___ znam.“ (Das ist alles, was ich weiß.)", "optionen": ["koji", "čiji", "što"], "richtig": "što", "tipp": "Nach sve, ono, nešto, ništa steht što."},
            {"frage": "„To je žena ___ muž radi sa mnom.“ (Das ist die Frau, deren Mann mit mir arbeitet.)", "optionen": ["čiji", "čija", "koja"], "richtig": "čiji", "tipp": "čiji richtet sich nach muž, nicht nach žena."},
        ],
    },

    # pronomen
    "fuerwoerter": {
        "erklaerung": [
            "Die kurze Form ist normal: „Vidim ga.“ Die lange steht nach Präpositionen (kod njega, o njoj) und zur Betonung: „Tebi sam ga dao, a ne njemu.“ Lokativ und Instrumental gibt es nur lang.",
            {"tabelle": [["Person", "Akkusativ / Genitiv", "Dativ / Lokativ", "Instrumental"],
                         ["ja", "mene, me", "meni, mi", "mnom"],
                         ["ti", "tebe, te", "tebi, ti", "tobom"],
                         ["on, ono", "njega, ga", "njemu, mu", "njim"],
                         ["ona", "nju (Genitiv: nje), je", "njoj, joj", "njom"],
                         ["mi", "nas", "nama, nam", "nama"],
                         ["vi", "vas", "vama, vam", "vama"],
                         ["oni, one, ona", "njih, ih", "njima, im", "njima"]]},
            "Mehrere kleine Wörter stehen als Gruppe an zweiter Stelle, immer so:",
            {"tabelle": [["Reihenfolge", "Beispiel"],
                         ["li", "Jesi li mu ga dao?"],
                         ["sam, si …; ću, ćeš …; bih, bi …", "Dao sam mu ga."],
                         ["Dativ: mi, mu, joj …", "Daj mi ga!"],
                         ["Akkusativ, Genitiv: me, ga, je …", "Sjećam ga se."],
                         ["se", "Sviđa mi se."],
                         ["je", "Dao joj ga je."]]},
            "„je“ von biti steht ganz hinten, nach „se“ fällt es meist weg: „Vratio se.“ Das kleine „je“ (sie) wird davor zu „ju“: „Vidio ju je.“",
            "Nach „ne“ kommt erst das Verb: „Ne dam ti ga.“ Nach „nisam“ folgt die Gruppe direkt: „Nisam mu ga dao.“",
        ],
        "uebungen": [
            {"frage": "„Ich habe es ihm gegeben.“", "optionen": ["Dao sam ga mu.", "Dao sam mu ga.", "Dao mu sam ga."], "richtig": "Dao sam mu ga.", "tipp": "Erst sam, dann der Dativ mu, dann der Akkusativ ga."},
            {"frage": "„Er hat es ihr gegeben.“", "optionen": ["Dao joj ga je.", "Dao je joj ga.", "Dao ga joj je."], "richtig": "Dao joj ga je.", "tipp": "Dativ vor Akkusativ, und je steht immer ganz hinten."},
            {"frage": "„Hast du es ihm gegeben?“", "optionen": ["Jesi mu ga li dao?", "Jesi li ga mu dao?", "Jesi li mu ga dao?"], "richtig": "Jesi li mu ga dao?", "tipp": "Erst li, dann mu, dann ga."},
            {"frage": "„Er hat sie gesehen.“", "optionen": ["Vidio je ju.", "Vidio ju je.", "Ju je vidio."], "richtig": "Vidio ju je.", "tipp": "Vor je wird das kleine je (sie) zu ju. Kleine Wörter stehen nie vorn."},
            {"frage": "„Ich erinnere mich an ihn.“", "optionen": ["Sjećam ga se.", "Sjećam se ga.", "Ga se sjećam."], "richtig": "Sjećam ga se.", "tipp": "Erst ga, dann se."},
            {"frage": "„Ja sam kod ___.“ (Ich bin bei ihm.)", "optionen": ["ga", "njemu", "njega"], "richtig": "njega", "tipp": "Nach einer Präposition die lange Form, kod + Genitiv."},
            {"frage": "„Govorimo o ___.“ (Wir sprechen über sie.)", "optionen": ["nju", "njoj", "joj"], "richtig": "njoj", "tipp": "o + Lokativ, den gibt es nur lang."},
        ],
    },

}
