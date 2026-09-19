# -*- coding: utf-8 -*-
"""
seite_bauen.py  –  erzeugt die Internetseite für GitHub Pages

Google Play verlangt eine **öffentliche Adresse**, unter der die
Datenschutzerklärung ohne Anmeldung lesbar ist. In der App allein reicht
nicht. Dieses Skript macht aus den Texten in `sprachen.py` drei fertige
Seiten im Ordner `github-seite`:

    index.html                Startseite mit den beiden Links
    datenschutz.html          Datenschutzerklärung, acht Sprachen
    nutzungsbedingungen.html  Nutzungsbedingungen, acht Sprachen

Die Seiten kommen ohne fremde Server aus: keine Schriften, keine Skripte
von außen, alles steht in der Datei selbst.

In Thonny öffnen und auf Run (F5) drücken. Nach jeder Änderung an den
Rechtstexten noch einmal laufen lassen und die Dateien neu hochladen.

Wie die Seiten online kommen, steht in github-seite/LIESMICH.txt.
"""

import io
import os
import sys

ORDNER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(ORDNER, "github-seite")
sys.path.insert(0, ORDNER)
import sprachen

# Nur diese beiden Seiten braucht der Store. Jede bekommt ihre eigene
# Adresse, damit man im Play-Konto genau darauf zeigen kann.
SEITEN = [
    ("datenschutz.html", "set.datenschutz", "set.datenschutz_text"),
    ("nutzungsbedingungen.html", "set.agb", "set.agb_text"),
    # Pflicht nach § 5 DDG, seit es das Gewerbe gibt. Die Angaben stehen zwar
    # auch INNEN in den beiden Texten darüber – das genügt nicht: ein
    # Impressum muss eigens erkennbar und unmittelbar erreichbar sein.
    ("impressum.html", "set.impressum", "set.impressum_text"),
]

STIL = """
:root{--bg:#0B1533;--karte:#132048;--linie:#24366e;--text:#EAF0FF;
      --leise:#9FB0D9;--gelb:#FFCB1F;--blau:#3F66DF}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);line-height:1.65;
     font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
     font-size:16px}
.wrap{max-width:760px;margin:0 auto;padding:28px 20px 70px}
header{display:flex;align-items:center;gap:12px;margin-bottom:26px}
.marke{font-size:26px;font-weight:800;letter-spacing:-.5px}
.marke span{color:var(--gelb)}
h1{font-size:26px;margin:0 0 18px}
a{color:var(--blau)}
a:hover{color:var(--gelb)}
.sprachen{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 26px;padding:0;list-style:none}
.sprachen button{font:inherit;font-size:13px;font-weight:700;cursor:pointer;
  padding:7px 13px;border-radius:999px;border:1px solid var(--linie);
  background:var(--karte);color:var(--leise)}
.sprachen button[aria-current="true"]{background:var(--blau);color:#fff;border-color:var(--blau)}
.karte{background:var(--karte);border:1px solid var(--linie);border-radius:16px;padding:20px 22px}
.recht{color:var(--leise);font-size:15px}
.recht b{color:var(--text);display:inline-block;margin-top:16px}
.recht b:first-child{margin-top:0}
footer{margin-top:34px;color:var(--leise);font-size:13px}
.knopf{display:inline-block;margin:6px 8px 0 0;padding:12px 18px;border-radius:12px;
  background:var(--karte);border:1px solid var(--linie);color:var(--text);
  font-weight:700;text-decoration:none}
.knopf:hover{border-color:var(--blau);color:var(--text)}
@media (max-width:520px){.wrap{padding:20px 14px 50px}h1{font-size:22px}}
"""

SKRIPT = """
(function(){
  var knoepfe = document.querySelectorAll('.sprachen button');
  var teile = document.querySelectorAll('section[data-sprache]');
  function zeige(code){
    var gefunden = false;
    teile.forEach(function(s){
      var an = s.dataset.sprache === code;
      s.hidden = !an;
      if(an) gefunden = true;
    });
    knoepfe.forEach(function(b){ b.setAttribute('aria-current', b.dataset.sprache === code); });
    document.documentElement.lang = code;
    if(!gefunden) zeige('de');
    try{ localStorage.setItem('zmaj_seite_sprache', code); }catch(e){}
  }
  knoepfe.forEach(function(b){ b.addEventListener('click', function(){ zeige(b.dataset.sprache); }); });
  var start = 'de';
  try{ start = localStorage.getItem('zmaj_seite_sprache') || (navigator.language||'de').slice(0,2).toLowerCase(); }catch(e){}
  zeige(start);
})();
"""


def kopf(titel):
    return (
        '<!doctype html>\n<html lang="de">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>%s</title>\n'
        '<style>%s</style>\n'
        '</head>\n<body>\n<div class="wrap">\n'
        '<header><div class="marke">Zmaj<span>.</span></div></header>\n'
    ) % (titel, STIL)


def fuss(mit_skript=True, hier=None):
    """hier: Dateiname dieser Seite – der eigene Verweis wird weggelassen.

    Google verlinkt die Datenschutzerklärung direkt. Ohne diese Zeile käme man
    von dort weder zum Impressum noch zu den anderen Texten."""
    anbieter = sprachen.ANBIETER.replace("<br>", " · ")
    andere = [(d, n) for d, n in (("index.html", "Start"),
                                  ("impressum.html", "Impressum"),
                                  ("datenschutz.html", "Datenschutz"),
                                  ("nutzungsbedingungen.html", "Nutzungsbedingungen"),
                                  ("konto-loeschen.html", "Daten löschen"))
              if d != hier]
    verweise = " · ".join('<a href="%s">%s</a>' % (d, n) for d, n in andere)
    teil = '<footer><nav>%s</nav><br>%s</footer>\n</div>\n' % (verweise, anbieter)
    if mit_skript:
        teil += "<script>%s</script>\n" % SKRIPT
    return teil + "</body>\n</html>\n"


def sprachwahl():
    knoepfe = "".join(
        '<li><button type="button" data-sprache="%s">%s</button></li>'
        % (s["code"], s["name"]) for s in sprachen.SPRACHEN)
    return '<ul class="sprachen">%s</ul>\n' % knoepfe


def baue_rechtsseite(datei, titel_schluessel, text_schluessel):
    erste = sprachen.texte(sprachen.GRUNDSPRACHE)
    teile = [kopf("Zmaj – " + erste[titel_schluessel]), sprachwahl()]
    for s in sprachen.SPRACHEN:
        t = sprachen.texte(s["code"])
        text = t[text_schluessel].replace("{anbieter}", t["set.anbieter"])
        teile.append(
            '<section data-sprache="%s" hidden>\n<h1>%s</h1>\n'
            '<div class="karte recht">%s</div>\n</section>\n'
            % (s["code"], t[titel_schluessel], text))
    teile.append(fuss(hier=datei))
    schreibe(datei, "".join(teile))


# Kurztext der Startseite. Bewusst knapp – die Seite ist kein Werbeauftritt,
# sie existiert, weil der Store eine öffentliche Adresse verlangt.
START = {
    "de": ("Bosnisch lernen mit Zmaj",
           "Zmaj ist eine App zum Bosnischlernen: 43 Levels, Grammatik und Geschichten.",
           "Datenschutzerklärung", "Nutzungsbedingungen", "Kontakt"),
    "en": ("Learn Bosnian with Zmaj",
           "Zmaj is an app for learning Bosnian: 43 levels, grammar and stories.",
           "Privacy policy", "Terms of use", "Contact"),
}

# Google Play fragt im Data-Safety-Formular, wie Nutzer ihre Daten wieder
# loswerden. Seit dem 16.09.2026 gibt es keine Konten mehr – die Antwort ist
# also einfach, muss aber öffentlich und ohne Anmeldung lesbar dastehen.
LOESCHEN = {
    "de": {
        "titel": "Daten löschen",
        "text": """
<p><b>Zmaj hat kein Konto</b><br>
Es gibt keine Anmeldung, kein Passwort und keine E-Mail-Adresse. Dein
Lernfortschritt liegt ausschließlich auf deinem Gerät und wird nirgendwo
hochgeladen – auch nicht zu uns.</p>

<p><b>So löschst du alles</b><br>
Du brauchst uns dafür nicht zu fragen und nicht zu erreichen:
lösche die App, oder leere in den Einstellungen deines Geräts ihren
Speicher (<i>Einstellungen → Apps → Zmaj → Speicher → Daten löschen</i>).
Damit ist der Fortschritt weg – bei uns ebenfalls, weil er dort nie war.
Das wirkt sofort.</p>

<p><b>Was gelöscht wird</b><br>
Gelernte Wörter, bestandene Levels, gelesene Geschichten, Lerntage,
Lernzeit, Tagesaufgaben, Münzen, gekaufte Gegenstände, Leben,
Serienschutz, deine Einstellungen und die zufällige Kennung, die beim
ersten Start entsteht.</p>

<p><b>Deine Sicherungsdatei</b><br>
Hast du unter <i>Einstellungen → Sicherung</i> eine Datei gespeichert,
liegt sie dort, wohin du sie gelegt hast. Die müsstest du selbst löschen –
wir kommen nicht an sie heran.</p>

<p><b>Wenn du uns geschrieben hast</b><br>
Eine Rückmeldung per E-Mail bleibt in unserem Postfach, samt deiner
Absenderadresse. Schreib an <a href="mailto:{mail}">{mail}</a>, und wir
löschen sie – innerhalb von 30 Tagen.</p>

<p><b>Die Vollversion</b><br>
Sie hängt an deinem Google-Konto, nicht an uns. Kündigen und löschen
lassen kannst du sie nur dort.</p>
""",
    },
    "en": {
        "titel": "Delete your data",
        "text": """
<p><b>Zmaj has no account</b><br>
There is no sign-in, no password and no email address. Your progress is
held solely on your device and is never uploaded anywhere – not to us
either.</p>

<p><b>How to delete everything</b><br>
You do not need to ask us or get hold of us: delete the app, or clear its
storage in your device settings (<i>Settings → Apps → Zmaj → Storage →
Clear data</i>). Your progress is then gone – with us as well, because it
was never there. This takes effect immediately.</p>

<p><b>What is deleted</b><br>
Words learned, levels passed, stories read, learning days, learning time,
daily tasks, coins, items bought, hearts, streak freezes, your settings
and the random identifier created the first time you start the app.</p>

<p><b>Your backup file</b><br>
If you saved one under <i>Settings → Backup</i>, it is wherever you put
it. You would have to delete that yourself – we cannot reach it.</p>

<p><b>If you have written to us</b><br>
Feedback sent by email stays in our mailbox, together with your sender
address. Write to <a href="mailto:{mail}">{mail}</a> and we will delete
it – within 30 days.</p>

<p><b>The full version</b><br>
It belongs to your Google account, not to us. You can only cancel it and
have it removed there.</p>
""",
    },
}


def baue_loeschseite():
    d, e = LOESCHEN["de"], LOESCHEN["en"]
    mail = post_adresse()
    inhalt = (
        '<h1>%s</h1>\n<div class="karte recht">%s</div>\n'
        '<div class="karte recht" style="margin-top:16px" lang="en">'
        '<h1 style="font-size:21px">%s</h1>%s</div>\n'
    ) % (d["titel"], d["text"].replace("{mail}", mail),
         e["titel"], e["text"].replace("{mail}", mail))
    schreibe("konto-loeschen.html", kopf("Zmaj – " + d["titel"]) + inhalt + fuss(mit_skript=False, hier="konto-loeschen.html"))


def baue_startseite():
    d = START["de"]
    e = START["en"]
    inhalt = (
        '<h1>%s</h1>\n<div class="karte">\n<p>%s</p>\n'
        '<p><a class="knopf" href="datenschutz.html">%s</a>'
        '<a class="knopf" href="nutzungsbedingungen.html">%s</a>'
        '<a class="knopf" href="konto-loeschen.html">%s</a>'
        '<a class="knopf" href="impressum.html">%s</a></p>\n'
        '<p class="recht">%s: <a href="mailto:%s">%s</a></p>\n'
        '</div>\n'
        '<div class="karte" style="margin-top:16px" lang="en">\n<p>%s</p>\n'
        '<p><a class="knopf" href="datenschutz.html">%s</a>'
        '<a class="knopf" href="nutzungsbedingungen.html">%s</a>'
        '<a class="knopf" href="konto-loeschen.html">%s</a>'
        '<a class="knopf" href="impressum.html">%s</a></p>\n</div>\n'
    ) % (d[0], d[1], d[2], d[3], LOESCHEN["de"]["titel"],
         sprachen.texte("de")["set.impressum"],
         d[4], post_adresse(), post_adresse(),
         e[1], e[2], e[3], LOESCHEN["en"]["titel"],
         sprachen.texte("en")["set.impressum"])
    schreibe("index.html", kopf("Zmaj – " + d[0]) + inhalt + fuss(mit_skript=False, hier="index.html"))


def post_adresse():
    """Die E-Mail-Adresse aus ANBIETER – die letzte Zeile."""
    letzte = sprachen.ANBIETER.split("<br>")[-1].strip()
    return letzte if "@" in letzte else "kontakt@beispiel.de"


def schreibe(datei, text):
    pfad = os.path.join(ZIEL, datei)
    with io.open(pfad, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("  %-26s %6d Bytes" % (datei, os.path.getsize(pfad)))


if __name__ == "__main__":
    os.makedirs(ZIEL, exist_ok=True)
    print("Seiten für GitHub Pages:")
    if sprachen.anbieter_fehlt():
        print("  ACHTUNG: In sprachen.py steht bei ANBIETER noch ein Platzhalter.")
    if sprachen.ustidnr_fehlt():
        print("  Hinweis: Die USt-IdNr fehlt im Impressum – sie kommt per Post vom")
        print("  Bundeszentralamt. Sobald sie da ist, in ANBIETER eintragen.")
    baue_startseite()
    baue_loeschseite()
    for datei, titel, text in SEITEN:
        baue_rechtsseite(datei, titel, text)
    print("\nFertig in: %s" % ZIEL)
    print("Wie es online kommt, steht in github-seite/LIESMICH.txt")
