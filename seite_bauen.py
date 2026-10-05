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
    app-ads.txt               eine Zeile für AdMob
    README.md                 Startseite des Repositories, aus seite_readme.md

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
  var fuesse = document.querySelectorAll('[data-fuss]');
  function zeige(code){
    var gefunden = false;
    teile.forEach(function(s){
      var an = s.dataset.sprache === code;
      s.hidden = !an;
      if(an) gefunden = true;
    });
    // Die Fusszeile wandert mit. Gibt es sie in der Sprache nicht,
    // bleibt die englische stehen - wie beim Inhalt darueber.
    var hatFuss = false;
    fuesse.forEach(function(f){ if(f.dataset.fuss === code) hatFuss = true; });
    fuesse.forEach(function(f){
      f.hidden = hatFuss ? (f.dataset.fuss !== code) : (f.dataset.fuss !== 'en');
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


# Das Wort fuer die Startseite. Die uebrigen vier Verweise holen sich ihre
# Beschriftung aus sprachen.py und aus LOESCHEN; nur hierfuer gab es nichts.
# Nachgesehen an Webseiten der jeweiligen Sprache, nicht uebersetzt.
START_WORT = {
    "de": "Start",
    "en": "Home",
    "tr": "Ana Sayfa",     # tdk.gov.tr, Schreibung der tuerkischen Sprachakademie
    "sv": "Start",         # 1177.se und polisen.se, erste Brotkrume
    "nl": "Home",          # rijksoverheid.nl und belastingdienst.nl - auch Behoerden schreiben Home
    "nb": "Forsiden",      # ssb.no und nrk.no, mit Artikel
    "da": "Forside",       # borger.dk und dsb.dk, ohne Artikel
    "fr": "Accueil",       # service-public.gouv.fr, keine Konkurrenzvariante
}


def fuss(mit_skript=True, hier=None):
    """hier: Dateiname dieser Seite – der eigene Verweis wird weggelassen.

    Google verlinkt die Datenschutzerklärung direkt. Ohne diese Zeile käme man
    von dort weder zum Impressum noch zu den anderen Texten."""
    anbieter = sprachen.ANBIETER.replace("<br>", " · ")

    def zeile(code):
        """Die fuenf Verweise in einer Sprache, ohne den auf diese Seite."""
        texte = sprachen.texte(code)
        namen = (("index.html", START_WORT.get(code, START_WORT["en"])),
                 ("impressum.html", texte["set.impressum"]),
                 ("datenschutz.html", texte["set.datenschutz"]),
                 ("nutzungsbedingungen.html", texte["set.agb"]),
                 ("konto-loeschen.html",
                  LOESCHEN.get(code, LOESCHEN["en"])["titel"]))
        return " · ".join('<a href="%s">%s</a>' % (d, n)
                          for d, n in namen if d != hier)

    # Eine Abteilung je Sprache, wie oben im Inhalt. Das Umschalt-Skript
    # blendet sie zusammen mit dem Text um; ohne Skript bleibt die
    # Grundsprache stehen, weil nur die uebrigen sieben hidden sind.
    fuesse = "".join(
        '<span data-fuss="%s"%s>%s</span>'
        % (s["code"], "" if s["code"] == sprachen.GRUNDSPRACHE else " hidden",
           zeile(s["code"]))
        for s in sprachen.SPRACHEN)
    teil = '<footer><nav>%s</nav><br>%s</footer>\n</div>\n' % (fuesse, anbieter)
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
           "Zmaj ist eine App zum Bosnischlernen: 65 Levels, Grammatik und Geschichten.",
           "Datenschutzerklärung", "Nutzungsbedingungen", "Kontakt"),
    "en": ("Learn Bosnian with Zmaj",
           "Zmaj is an app for learning Bosnian: 65 levels, grammar and stories.",
           "Privacy policy", "Terms of use", "Contact"),
    "tr": ("Zmaj ile Boşnakça öğren",
           "Zmaj, Boşnakça öğrenmek için bir uygulamadır: 65 seviye, dilbilgisi ve hikâyeler.",
           "Gizlilik politikası", "Kullanım koşulları", "İletişim"),
    "sv": ("Lär dig bosniska med Zmaj",
           "Zmaj är en app för att lära sig bosniska: 65 nivåer, grammatik och berättelser.",
           "Integritetspolicy", "Användarvillkor", "Kontakt"),
    "nl": ("Bosnisch leren met Zmaj",
           "Zmaj is een app om Bosnisch te leren: 65 niveaus, grammatica en verhalen.",
           "Privacyverklaring", "Gebruiksvoorwaarden", "Contact"),
    "nb": ("Lær bosnisk med Zmaj",
           "Zmaj er en app for å lære bosnisk: 65 nivåer, grammatikk og fortellinger.",
           "Personvernerklæring", "Bruksvilkår", "Kontakt"),
    "da": ("Lær bosnisk med Zmaj",
           "Zmaj er en app til at lære bosnisk: 65 niveauer, grammatik og fortællinger.",
           "Privatlivspolitik", "Brugsvilkår", "Kontakt"),
    "fr": ("Apprendre le bosnien avec Zmaj",
           "Zmaj est une application pour apprendre le bosnien : 65 niveaux, de la grammaire et des histoires.",
           "Politique de confidentialité", "Conditions d'utilisation", "Contact"),
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
Lernfortschritt liegt auf deinem Gerät; die App lädt ihn nirgendwo hoch –
auch nicht zu uns.</p>

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

<p><b>Androids eigene Sicherung</b><br>
Hast du sie in deinem Google-Konto eingeschaltet, liegt dort eine Kopie
der App-Daten, und Android spielt sie bei einer Neuinstallation zurück.
Die löschst du in deinem Google-Konto (Google Drive bzw. Google One →
Sicherungen) – wir kommen nicht an sie heran.</p>

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
kept on your device; the app never uploads it anywhere – not to us either.</p>

<p><b>How to delete everything</b><br>
You do not need to ask us or get hold of us: delete the app, or clear its
storage in your device settings (<i>Settings → Apps → Zmaj → Storage →
Clear data</i>). Your progress is then gone – with us as well, because it
was never there. This takes effect immediately.</p>

<p><b>What is deleted</b><br>
Words learned, levels passed, stories read, learning days, learning time,
daily tasks, coins, items bought, hearts, streak freezes, your settings
and the random identifier created the first time you start the app.</p>

<p><b>Android's own backup</b><br>
If you have turned it on in your Google account, a copy of the app's
data is kept there, and Android restores it when you reinstall. You
delete it in your Google account (Google Drive or Google One → Backups) –
we cannot reach it.</p>

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
    "tr": {
        "titel": "Verilerini sil",
        "text": """
<p><b>Zmaj'ın hesabı yoktur</b><br>
Giriş yok, parola yok, e-posta adresi yok. Öğrenme ilerlemen senin
cihazında durur; uygulama onu hiçbir yere yüklemez – bize de.</p>

<p><b>Her şeyi nasıl silersin</b><br>
Bunun için bize sormana ya da bize ulaşmana gerek yok:
uygulamayı sil ya da cihazının ayarlarından uygulamanın belleğini
temizle (<i>Ayarlar → Uygulamalar → Zmaj → Depolama → Verileri temizle</i>).
Böylece öğrenme ilerlemen kaybolur – bizde de, çünkü zaten hiç bizde
olmadı. Bu anında geçerli olur.</p>

<p><b>Neler silinir</b><br>
Öğrenilen kelimeler, geçilen seviyeler, okunan hikâyeler, öğrenme
günleri, öğrenme süresi, günlük görevler, jetonlar, satın alınan eşyalar,
canlar, seri koruması, ayarların ve uygulamayı ilk açtığında oluşan
rastgele kimlik.</p>

<p><b>Android'in kendi yedeklemesi</b><br>
Bunu Google hesabında açtıysan, uygulama verilerinin bir kopyası orada
durur ve Android onu yeniden kurulumda geri yükler. Onu Google hesabından
silersin (Google Drive ya da Google One → Yedeklemeler) – biz ona
erişemeyiz.</p>

<p><b>Yedek dosyan</b><br>
<i>Ayarlar → Yedek</i> bölümünden bir dosya kaydettiysen, o dosya nereye
koyduysan orada duruyor. Onu senin silmen gerekir – biz ona erişemeyiz.</p>

<p><b>Bize yazdıysan</b><br>
E-postayla gönderdiğin geri bildirim, gönderen adresinle birlikte posta
kutumuzda kalır. <a href="mailto:{mail}">{mail}</a> adresine yaz, sileriz –
30 gün içinde.</p>

<p><b>Tam sürüm</b><br>
Tam sürüm bize değil, Google hesabına bağlıdır. İptal etmeyi de
sildirmeyi de yalnızca oradan yapabilirsin.</p>
""",
    },
    "sv": {
        "titel": "Radera dina data",
        "text": """
<p><b>Zmaj har inget konto</b><br>
Det finns ingen inloggning, inget lösenord och ingen e-postadress. Dina framsteg ligger på din enhet; appen laddar inte upp dem någonstans – inte heller till oss.</p>

<p><b>Så raderar du allt</b><br>
Du behöver varken fråga oss eller få tag på oss: avinstallera appen, eller töm appens lagringsutrymme i enhetens inställningar (<i>Inställningar → Appar → Zmaj → Lagring → Rensa data</i>). Då är dina framsteg borta – hos oss också, eftersom de aldrig fanns där. Det sker direkt.</p>

<p><b>Det här raderas</b><br>
Inlärda ord, klarade nivåer, lästa berättelser, inlärningsdagar, inlärningstid, dagsuppgifter, mynt, föremål du köpt, hjärtan, serieskydd, dina inställningar och den slumpmässiga identifierare som skapas när du startar appen första gången.</p>

<p><b>Androids egen säkerhetskopiering</b><br>
Har du slagit på den i ditt Google-konto finns en kopia av appens data där, och Android återställer den när du installerar om. Den raderar du i ditt Google-konto (Google Drive eller Google One → Säkerhetskopior) – vi kommer inte åt den.</p>

<p><b>Din säkerhetskopia</b><br>
Har du sparat en fil under <i>Inställningar → Säkerhetskopia</i> ligger den kvar där du lade den. Den måste du radera själv – vi kommer inte åt den.</p>

<p><b>Om du har skrivit till oss</b><br>
Ett mejl med feedback blir kvar i vår inkorg, tillsammans med din avsändaradress. Skriv till <a href="mailto:{mail}">{mail}</a>, så raderar vi det – inom 30 dagar.</p>

<p><b>Fullversionen</b><br>
Den är kopplad till ditt Google-konto, inte till oss. Det är bara där du kan säga upp och radera den.</p>
""",
    },
    "nl": {
        "titel": "Je gegevens wissen",
        "text": """
<p><b>Zmaj heeft geen account</b><br>
Er is geen inlog, geen wachtwoord en geen e-mailadres. Je voortgang staat
op je eigen apparaat; de app uploadt hem nergens naartoe – ook niet naar ons.</p>

<p><b>Zo wis je alles</b><br>
Je hoeft het ons daarvoor niet te vragen en ons niet te bereiken:
verwijder de app, of wis in de instellingen van je apparaat de opslag ervan
(<i>Instellingen → Apps → Zmaj → Opslag → Gegevens wissen</i>).
Daarmee is je voortgang weg – bij ons ook, want daar is hij nooit geweest.
Dat werkt meteen.</p>

<p><b>Wat er gewist wordt</b><br>
Geleerde woorden, gehaalde niveaus, gelezen verhalen, leerdagen,
leertijd, dagopdrachten, munten, gekochte voorwerpen, levens,
reeksbescherming, je instellingen en de willekeurige ID-code die bij de
eerste start wordt aangemaakt.</p>

<p><b>De eigen back-up van Android</b><br>
Heb je die in je Google-account aangezet, dan staat daar een kopie van de
gegevens van de app, en Android zet die terug als je de app opnieuw installeert.
Die wis je in je Google-account (Google Drive of Google One → Back-ups) –
wij kunnen er niet bij.</p>

<p><b>Je reservekopie</b><br>
Heb je via <i>Instellingen → Reservekopie</i> een bestand opgeslagen,
dan staat dat waar jij het hebt neergezet. Dat moet je zelf verwijderen –
wij kunnen er niet bij.</p>

<p><b>Als je ons hebt geschreven</b><br>
Een reactie per e-mail blijft in onze mailbox staan, samen met je
afzenderadres. Schrijf naar <a href="mailto:{mail}">{mail}</a>, dan wissen
we hem – binnen 30 dagen.</p>

<p><b>De volledige versie</b><br>
Die is gekoppeld aan je Google-account, niet aan ons. Opzeggen en laten verwijderen
kan alleen daar.</p>
""",
    },
    "nb": {
        "titel": "Slett dataene dine",
        "text": """
<p><b>Zmaj har ingen konto</b><br>
Det finnes ingen innlogging, intet passord og ingen e-postadresse. Framgangen din ligger på enheten din; appen laster den aldri opp noe sted – heller ikke til oss.</p>

<p><b>Slik sletter du alt</b><br>
Du trenger verken å spørre oss eller få tak i oss: Slett appen, eller tøm lagringen dens i innstillingene på enheten din (<i>Innstillinger → Apper → Zmaj → Lagring → Tøm data</i>). Dermed er framgangen borte – hos oss også, for der har den aldri vært. Det virker med en gang.</p>

<p><b>Hva som blir slettet</b><br>
Lærte ord, beståtte nivåer, leste fortellinger, læringsdager, læringstid, dagsoppdrag, mynter, gjenstander du har kjøpt, liv, rekkebeskyttelse, innstillingene dine og den tilfeldige ID-en som blir laget første gang du starter appen.</p>

<p><b>Androids egen sikkerhetskopiering</b><br>
Har du slått den på i Google-kontoen din, ligger det en kopi av appens data der, og Android gjenoppretter den når du installerer appen på nytt. Den sletter du i Google-kontoen din (Google Disk eller Google One → Sikkerhetskopier) – vi har ikke tilgang til den.</p>

<p><b>Sikkerhetskopien din</b><br>
Har du lagret en fil under <i>Innstillinger → Sikkerhetskopi</i>, ligger den der du la den. Den må du slette selv – vi har ikke tilgang til den.</p>

<p><b>Hvis du har skrevet til oss</b><br>
En tilbakemelding på e-post blir liggende i postkassen vår, sammen med avsenderadressen din. Skriv til <a href="mailto:{mail}">{mail}</a>, så sletter vi den – innen 30 dager.</p>

<p><b>Fullversjonen</b><br>
Den hører til Google-kontoen din, ikke til oss. Det er bare der du kan si den opp og få den slettet.</p>
""",
    },
    "da": {
        "titel": "Slet dine data",
        "text": """
<p><b>Zmaj har ingen konto</b><br>
Der er intet login, ingen adgangskode og ingen mailadresse. Dine fremskridt ligger på din enhed; appen sender dem ikke nogen steder hen – heller ikke til os.</p>

<p><b>Sådan sletter du det hele</b><br>
Du behøver ikke at spørge os eller få fat i os:
Slet appen, eller ryd dens lagrede data i din enheds indstillinger
(<i>Indstillinger → Apps → Zmaj → Lagring → Ryd data</i>).
Så er dine fremskridt væk – også hos os, for de har aldrig været der.
Det virker med det samme.</p>

<p><b>Hvad der bliver slettet</b><br>
Lærte ord, beståede niveauer, læste fortællinger, læringsdage,
læringstid, dagsopgaver, mønter, købte genstande, liv,
rækkebeskyttelse, dine indstillinger og det tilfældige id, der bliver
oprettet, første gang du starter appen.</p>

<p><b>Androids egen sikkerhedskopiering</b><br>
Har du slået den til i din Google-konto, ligger der en kopi af appens
data, og Android lægger den tilbage, når du geninstallerer. Den sletter du
i din Google-konto (Google Drev eller Google One → Sikkerhedskopier) –
vi kan ikke komme til den.</p>

<p><b>Din sikkerhedskopi</b><br>
Har du gemt en fil under <i>Indstillinger → Sikkerhedskopi</i>,
ligger den der, hvor du har lagt den. Den skal du selv slette –
vi kan ikke komme til den.</p>

<p><b>Hvis du har skrevet til os</b><br>
Har du sendt os en mail, bliver den liggende i vores indbakke sammen med
din afsenderadresse. Skriv til <a href="mailto:{mail}">{mail}</a>, så
sletter vi den – inden for 30 dage.</p>

<p><b>Fuld version</b><br>
Den er knyttet til din Google-konto, ikke til os. Du kan kun opsige
og slette den dér.</p>
""",
    },
    "fr": {
        "titel": "Supprimer tes données",
        "text": """
<p><b>Zmaj n'a pas de compte</b><br>
Il n'y a ni connexion, ni mot de passe, ni adresse e-mail. Ta progression
reste sur ton appareil ; l'application ne l'envoie nulle part – pas
même chez nous.</p>

<p><b>Comment tout supprimer</b><br>
Tu n'as besoin ni de nous le demander, ni de nous joindre : supprime
l'application, ou vide sa mémoire dans les réglages de ton appareil
(<i>Paramètres → Applications → Zmaj → Stockage → Effacer les données</i>).
Ta progression est alors perdue – chez nous aussi, car elle ne s'y est
jamais trouvée. C'est immédiat.</p>

<p><b>Ce qui est supprimé</b><br>
Les mots appris, les niveaux réussis, les histoires lues, les jours
d'apprentissage, le temps d'apprentissage, les objectifs du jour, les
pièces, les objets achetés, les vies, les protections de série, tes
réglages et l'identifiant aléatoire créé au premier démarrage.</p>

<p><b>La sauvegarde d'Android</b><br>
Si tu l'as activée dans ton compte Google, une copie des données de
l'application s'y trouve, et Android la restaure quand tu réinstalles. Tu
la supprimes dans ton compte Google (Google Drive ou Google One →
Sauvegardes) – nous n'y avons pas accès.</p>

<p><b>Ton fichier de sauvegarde</b><br>
Si tu en as enregistré un dans <i>Réglages → Sauvegarde</i>, il se trouve
là où tu l'as mis. Celui-là, il faudra que tu le supprimes toi-même – nous
n'y avons pas accès.</p>

<p><b>Si tu nous as écrit</b><br>
Un commentaire envoyé par e-mail reste dans notre boîte mail, avec ton
adresse d'expéditeur. Écris-nous à <a href="mailto:{mail}">{mail}</a> et
nous le supprimons – sous 30 jours.</p>

<p><b>La version complète</b><br>
Elle est liée à ton compte Google, pas à nous. Tu ne peux la résilier et la
faire supprimer que là-bas.</p>
""",
    },
}


def baue_loeschseite():
    """Wie die Rechtstexte: eine Abteilung je Sprache, Umschalter oben.

    Frueher standen hier Deutsch und Englisch untereinander auf einer Seite.
    Bei acht Sprachen wird das unuebersichtlich - wer Tuerkisch liest, soll
    nicht an sieben fremden Fassungen vorbeiscrollen muessen.

    Fehlt eine Sprache in LOESCHEN, springt sie auf Englisch. Eine
    verstaendliche fremde Sprache ist besser als eine leere Seite."""
    mail = post_adresse()
    erste = LOESCHEN[sprachen.GRUNDSPRACHE]
    teile = [kopf("Zmaj – " + erste["titel"]), sprachwahl()]
    for s in sprachen.SPRACHEN:
        code = s["code"]
        l = LOESCHEN.get(code, LOESCHEN["en"])
        # lang zeigt auf die Sprache, die wirklich dasteht - bei einer
        # fehlenden Uebersetzung ist das Englisch, nicht code.
        echt = code if code in LOESCHEN else "en"
        teile.append(
            '<section data-sprache="%s" lang="%s" hidden>\n<h1>%s</h1>\n'
            '<div class="karte recht">%s</div>\n</section>\n'
            % (code, echt, l["titel"], l["text"].replace("{mail}", mail)))
    teile.append(fuss(hier="konto-loeschen.html"))
    schreibe("konto-loeschen.html", "".join(teile))


def baue_startseite():
    """Dieselbe Bauweise wie die uebrigen Seiten.

    Die Knopfbeschriftungen stehen in START; nur das Wort fuer Impressum
    kommt aus sprachen.py, weil die App es selbst anzeigt."""
    mail = post_adresse()
    erste = START[sprachen.GRUNDSPRACHE]
    # erste[0] heisst schon "Bosnisch lernen mit Zmaj" - kein Praefix
    teile = [kopf(erste[0]), sprachwahl()]
    for s in sprachen.SPRACHEN:
        code = s["code"]
        k = START.get(code, START["en"])
        l = LOESCHEN.get(code, LOESCHEN["en"])
        echt = code if code in START else "en"
        teile.append(
            '<section data-sprache="%s" lang="%s" hidden>\n<h1>%s</h1>\n'
            '<div class="karte">\n<p>%s</p>\n'
            '<p><a class="knopf" href="datenschutz.html">%s</a>'
            '<a class="knopf" href="nutzungsbedingungen.html">%s</a>'
            '<a class="knopf" href="konto-loeschen.html">%s</a>'
            '<a class="knopf" href="impressum.html">%s</a></p>\n'
            '<p class="recht">%s: <a href="mailto:%s">%s</a></p>\n'
            '</div>\n</section>\n'
            % (code, echt, k[0], k[1], k[2], k[3], l["titel"],
               sprachen.texte(code)["set.impressum"],
               k[4], mail, mail))
    teile.append(fuss(hier="index.html"))
    schreibe("index.html", "".join(teile))


def post_adresse():
    """Die E-Mail-Adresse aus ANBIETER – die Zeile mit dem @.

    Frueher war es schlicht die letzte Zeile. Seit die USt-IdNr dahinter
    steht, waere das die falsche.
    """
    for zeile in sprachen.ANBIETER.split("<br>"):
        if "@" in zeile:
            return zeile.strip()
    return "kontakt@beispiel.de"


# Die Publisher-ID aus dem AdMob-Konto, angelegt am 20.09.2026. Kein
# Geheimnis – sie steht in jeder ausgelieferten App und ist genau dafür da,
# öffentlich nachlesbar zu sein.
#
# app-ads.txt sagt den Werbeeinkäufern: Wer unter diesem Namen Werbeplätze
# in Zmaj verkauft, gehört wirklich zu mir. Ohne die Datei bleibt die
# Anzeigenauslieferung eingeschränkt, und AdMob meldet das nicht als Fehler.
# Gefunden wird sie über die Entwickler-Website aus dem Play-Store-Eintrag:
# Google hängt dort /app-ads.txt an. Die Adresse im Store muss deshalb auf
# zmaj-lernapp.github.io zeigen.
#
# Das f08c47… am Ende ist Googles feste Kennung im ads.txt-Verzeichnis,
# bei allen Publishern dieselbe.
ADMOB_PUBLISHER = "pub-9105747905460295"
APP_ADS = "google.com, %s, DIRECT, f08c47fec0942fa0\n" % ADMOB_PUBLISHER


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
    schreibe("app-ads.txt", APP_ADS)
    # Die Startseite des Repositories. Sie fuehrt mit klickbaren Links zu den
    # fertigen Seiten - noetig, weil GitHub in der Dateiliste nur den
    # HTML-Quelltext zeigt und nicht die lesbare Fassung. Der Text steht in
    # seite_readme.md und wird hier nur kopiert.
    quelle = os.path.join(ORDNER, "seite_readme.md")
    if os.path.exists(quelle):
        schreibe("README.md", io.open(quelle, encoding="utf-8").read())
    else:
        print("  Hinweis: seite_readme.md fehlt - README wird nicht erzeugt.")
    print("\nFertig in: %s" % ZIEL)
    print("Wie es online kommt, steht in github-seite/LIESMICH.txt")
