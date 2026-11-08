# -*- coding: utf-8 -*-
"""Wortschatz-Paket 10 (07.11.2026): Sektion 18 · Denken und Meinen.

154 Woerter je mit Beispielsatz, von Ajdin am 07.11.2026 durchgesehen
(Release\\Wortschatz\\paket_10.json, b2_entscheidungen.md), seit dem 08.11.2026 153
Woerter und 154 Saetze. Hier steht, was beim Einbau festgelegt wurde:

- Gruppen ueber 20 Woerter sind wie bei Paket 3 bis 9 auf zwei Level verteilt, Stufe B2
  steht in eigenen Sektionen hinter B1;
- Anzeige mit zwei Formen wie kahva / kafa: uvjeriti / ubijediti, uvjeravati / ubjeđivati,
  rasprava / diskusija, kako bi / kako bih, pritom / pri tome,
  zanimljiv / interesantan. ubjediti und ubijedati zaehlen mit (Nachfrage 7 B), kako bismo
  und kako biste nicht (Nachfrage 2 B);
- eine Form allein genannt: die andere zaehlt mit (Nachfrage 1 B: prije nego, sa jedne
  strane, sa druge strane, usprkos, istaknuti);
- nego i / već i (Nr. 108) ist seit dem 08.11.2026 kein eigenes Wort mehr. Ajdin: „nimm es
  nur rein in einem ganzen satz nur so hört es sich sehr komisch an“. Der Satz bleibt mit
  seiner Aufnahme w5563 im Level einerseits_andererseits (NUR_SATZ), w5562 und w8899 sind
  frei. Es war nie veroeffentlicht (nicht in 617ead1), deshalb kein UMBENANNT.

Die Pruefungen selbst stehen in tests/paket1020_pruefung.py.
"""
from paket1020_pruefung import *  # noqa: F401,F403

LEVEL = ["grundlage_rahmen", "arten_einzelheiten", "forschen_verstehen", "ueberlegen_einschaetzen",
         "vorhersehen_erkennen", "meinung_kritik", "sagen_hervorheben", "daher_damit_bevor",
         "einerseits_andererseits", "trotz_dank", "vor_allem_angeblich", "etwas_beurteilen"]
SEKTION = {
    "grundlage_rahmen": "denkenmeinen", "arten_einzelheiten": "denkenmeinen",
    "forschen_verstehen": "denkenmeinen", "ueberlegen_einschaetzen": "denkenmeinen",
    "vorhersehen_erkennen": "denkenmeinen", "meinung_kritik": "denkenmeinen",
    "sagen_hervorheben": "denkenmeinen", "daher_damit_bevor": "denkenmeinen",
    "einerseits_andererseits": "denkenmeinen", "trotz_dank": "denkenmeinen",
    "vor_allem_angeblich": "denkenmeinen", "etwas_beurteilen": "denkenmeinen",
}

# Die Woerter je Level ohne die Beispielsaetze. Bosnisch genau so, wie Ajdin es
# freigegeben hat - aendert sich hier etwas, aendert sich eine Kennung und damit
# Lernstand (AGENTS.md, Regel 1).
WOERTER = {
    "grundlage_rahmen": ["obzir", "osnova", "okvir", "funkcija", "model", "sklad", "element", "struktura",
                         "princip", "standard", "faktor", "temelj", "karakteristika", "kontekst", "aspekt"],
    "arten_einzelheiten": ["tip", "kategorija", "upotreba", "pojava", "detalj", "opcija", "primjena",
                           "važnost", "okolnost", "poboljšanje", "prioritet", "efekat", "izuzetak", "pristup"],
    "forschen_verstehen": ["istraživanje", "analiza", "um", "teorija", "studija", "svijest", "koncept",
                           "razumijevanje", "perspektiva", "saznanje", "pretpostavka", "uvjerenje", "razum"],
    "ueberlegen_einschaetzen": ["razmatrati", "razmotriti", "pretpostaviti", "pretpostavljati", "zamisliti",
                                "zamišljati", "podrazumijevati", "uvjeriti / ubijediti",
                                "uvjeravati / ubjeđivati", "ocijeniti", "ocjenjivati", "procijeniti",
                                "procjenjivati"],
    "vorhersehen_erkennen": ["predvidjeti", "predviđati", "prepoznati", "prepoznavati", "posmatrati",
                             "analizirati", "povezati", "povezivati", "suočiti se", "suočavati se",
                             "uzrokovati", "nastojati"],
    "meinung_kritik": ["izjava", "komentar", "dogovor", "rasprava / diskusija", "preporuka", "kritika",
                       "tvrdnja", "dijalog", "utisak", "objašnjenje", "argument", "kompromis"],
    "sagen_hervorheben": ["izjaviti", "izjavljivati", "istaći", "isticati", "navesti", "navoditi", "ukazati",
                          "ukazivati", "napomenuti", "napominjati", "pojasniti", "pojašnjavati",
                          "raspravljati", "negirati", "insistirati", "zalagati se", "založiti se"],
    "daher_damit_bevor": ["mada", "no", "niti", "stoga", "osim toga", "budući da", "kako bi / kako bih",
                          "tako da", "prije nego što", "nakon što", "ne samo"],
    "einerseits_andererseits": ["s jedne strane", "s druge strane", "drugim riječima",
                                "naprotiv", "potom", "ujedno", "pritom / pri tome", "doduše", "uostalom",
                                "ionako"],
    "trotz_dank": ["pri", "nad", "prilikom", "povodom", "uprkos", "pomoću", "zahvaljujući", "uoči", "izuzetno",
                   "istovremeno"],
    "vor_allem_angeblich": ["naročito", "pogotovo", "isključivo", "navodno", "znatno", "prilično",
                            "prvenstveno", "očigledno", "slučajno", "praktično", "lično"],
    "etwas_beurteilen": ["osnovni", "dodatan", "ključan", "zanimljiv / interesantan", "opći", "jedinstven",
                         "svjestan", "stvaran", "konkretan", "lažan", "suprotan", "aktivan", "dostupan",
                         "nezavisan", "aktuelan"],
}

# Das Wort steckt im Bestand, nur sein Satz kommt dazu. Hier: das Wort ist ganz heraus,
# allein klang es komisch (Ajdin, 08.11.2026), der Satz bleibt.
NUR_SATZ = {"Govori ne samo bosanski, nego i njemački."}

# "auch" genau nach dem Paket, dazu bei Adjektiven die weiteren Formen aus "formen".
AUCH = {
    "uvjerenje": ["ubjeđenje"], "uvjeriti / ubijediti": ["ubjediti"], "uvjeravati / ubjeđivati": ["ubijedati"],
    "istaći": ["istaknuti"], "prije nego što": ["prije nego"], "s jedne strane": ["sa jedne strane"],
    "s druge strane": ["sa druge strane"], "uprkos": ["usprkos"], "osnovni": ["osnovna", "osnovno"],
    "dodatan": ["dodatna", "dodatno"], "ključan": ["ključna", "ključno"],
    "zanimljiv / interesantan": ["interesantna", "interesantno", "zanimljiva", "zanimljivo"],
    "opći": ["opšti", "opšta", "opšte", "opća", "opće"], "jedinstven": ["jedinstvena", "jedinstveno"],
    "svjestan": ["svjesna", "svjesno"], "stvaran": ["stvarna", "stvarno"],
    "konkretan": ["konkretna", "konkretno"], "lažan": ["lažna", "lažno"], "suprotan": ["suprotna", "suprotno"],
    "aktivan": ["aktivna", "aktivno"], "dostupan": ["dostupna", "dostupno"],
    "nezavisan": ["nezavisna", "nezavisno"], "aktuelan": ["aktuelna", "aktuelno"],
}

# Ajdin: diese Formen zaehlen beim Tippen NICHT (zaehlt_nicht im Paket).
ZAEHLT_NICHT = {
    "efekat": ["efekt"], "kako bi / kako bih": ["kako bismo", "kako biste"],
}

# Partner je Wort, wie im Paket.
PARTNER = {
    "razmatrati": "razmotriti", "razmotriti": "razmatrati", "pretpostaviti": "pretpostavljati",
    "pretpostavljati": "pretpostaviti", "zamisliti": "zamišljati", "zamišljati": "zamisliti",
    "uvjeriti / ubijediti": "uvjeravati / ubjeđivati", "uvjeravati / ubjeđivati": "uvjeriti / ubijediti",
    "ocijeniti": "ocjenjivati", "ocjenjivati": "ocijeniti", "procijeniti": "procjenjivati",
    "procjenjivati": "procijeniti", "predvidjeti": "predviđati", "predviđati": "predvidjeti",
    "prepoznati": "prepoznavati", "prepoznavati": "prepoznati", "povezati": "povezivati",
    "povezivati": "povezati", "suočiti se": "suočavati se", "suočavati se": "suočiti se",
    "izjaviti": "izjavljivati", "izjavljivati": "izjaviti", "istaći": "isticati", "isticati": "istaći",
    "navesti": "navoditi", "navoditi": "navesti", "ukazati": "ukazivati", "ukazivati": "ukazati",
    "napomenuti": "napominjati", "napominjati": "napomenuti", "pojasniti": "pojašnjavati",
    "pojašnjavati": "pojasniti", "zalagati se": "založiti se", "založiti se": "zalagati se",
}


def test_nego_i_steht_nur_noch_im_satz(grunddaten, index_html):
    """Ajdin, 08.11.2026: „nimm es nur rein in einem ganzen satz nur so hört es sich sehr
    komisch an“. Kein Eintrag, keine Aufnahme und kein UMBENANNT zeigt mehr auf das Wort,
    der Satz steht als eigener Eintrag mit seiner Aufnahme vorn im Level."""
    import ton_bauen
    alle = [w for k in grunddaten["kategorien"] for w in k["words"]]
    assert not [w["id"] for w in alle if "nego i" in w["bs"].split(" / ") or "već i" in w["bs"].split(" / ")]
    assert not [w["id"] for w in alle if w["de"] == "sondern auch"]
    k = next(x for x in grunddaten["kategorien"] if x["id"] == "einerseits_andererseits")
    assert k["words"][0]["bs"] == "Govori ne samo bosanski, nego i njemački."
    assert k["words"][0]["de"] == "Er spricht nicht nur Bosnisch, sondern auch Deutsch."
    assert "sondern auch:nego i" not in index_html
    emir = ton_bauen.nur_emir()
    assert "nego i" not in emir and "nego i / već i" not in emir
    assert emir["govori ne samo bosanski, nego i njemački."]["datei"] == "w5563.mp3"
