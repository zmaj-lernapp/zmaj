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
            {"frage": "„Šta si ___?“ zu einem Mann (Was hast du gemacht?)", "optionen": ["radio", "radila", "radili"], "richtig": "radio", "tipp": "männlich → -o."},
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

}
