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
    konto-loeschen.html       Konto und Daten löschen (Pflicht von Google
                              Play, seit v109 mit dem Weg in der App und
                              per Mail)
    .nojekyll                 damit GitHub Pages .well-known ausliefert
    .well-known/assetlinks.json
                              verbindet die Seite mit der App (Restore-
                              Schlüssel der Anmeldung, seit v109). Nur, wenn
                              zmaj-android/fingerabdruecke.json da ist
    README.md                 Startseite des Repositories, aus seite_readme.md
    favicon.ico, icon-256.png Symbol im Browser-Tab, Kopie von web/icon.ico
                              und web/icon-256.png (der Drache, seit 15.10.2026)

Die Seiten kommen ohne fremde Server aus: keine Schriften, keine Skripte
von außen, alles steht in der Datei selbst.

In Thonny öffnen und auf Run (F5) drücken. Nach jeder Änderung an den
Rechtstexten noch einmal laufen lassen und die Dateien neu hochladen.

Wie die Seiten online kommen, steht in github-seite/LIESMICH.txt.
"""

import io
import json
import os
import re
import shutil
import sys

ORDNER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(ORDNER, "github-seite")
sys.path.insert(0, ORDNER)
import huelle  # noqa: E402
import sprachen  # noqa: E402

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
        # Symbol im Browser-Tab: das App-Symbol (Drache), seit 15.10.2026.
        # Bis dahin hatte die Seite keins, und der Browser fragte vergeblich
        # nach /favicon.ico. Die Dateien liegen neben den Seiten, nichts
        # kommt von fremden Servern. Die App selbst zeigt im Tab weiter die
        # Flagge (web/flagge.png).
        '<link rel="icon" href="favicon.ico" sizes="any">\n'
        '<link rel="icon" type="image/png" href="icon-256.png">\n'
        '<style>%s</style>\n'
        '</head>\n<body>\n<div class="wrap">\n'
        '<header><div class="marke">Zmaj<span>.</span></div></header>\n'
    ) % (titel, STIL)


# Die Kanaele von Zmaj, in jeder Sprache gleich: Plattformnamen werden
# nicht uebersetzt. Nur Verweise, nichts wird eingebettet oder geladen.
# 07.10.2026.
SOZIAL = (("TikTok", "https://www.tiktok.com/@zmaj.learnbosnian"),
          ("Instagram", "https://www.instagram.com/zmaj.learnbosnian/"),
          ("YouTube", "https://www.youtube.com/@zmaj.learnbosnian"))

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
    sozial = " · ".join('<a href="%s" rel="noopener">%s</a>' % (u, n)
                        for n, u in SOZIAL)
    # Das Symbol im Tab ist ein KI-Bild; das sagen wir offen, wie im README
    # und in web/LIZENZEN.txt. Englisch in jeder Sprache - es ist ein
    # Bildnachweis, kein Text der Seite. 15.10.2026.
    ki = "App icon: illustration created with Google Gemini, edited."
    teil = ('<footer><nav>%s</nav><br>%s<br>%s<br><small>%s</small></footer>\n</div>\n'
            % (fuesse, sozial, anbieter, ki))
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

# Google Play verlangt fuer jede App, in der man ein Konto anlegen kann,
# einen Weg zum Loeschen in der App UND eine oeffentliche Seite, die ohne
# Anmeldung lesbar ist. Bis v108 hiess die Antwort "Zmaj hat kein Konto".
# Seit v109 (28.10.2026) ist das Konto Pflicht: in der App sofort, ohne App
# per Mail an die Adresse aus ANBIETER, geloescht von Hand in der
# Firebase-Konsole innerhalb von 30 Tagen (Frage 5 im Plan, nach dem
# Vorschlag gebaut). Die Abschnitte zu Androids Sicherung, zur
# Sicherungsdatei und zu Mails an uns sind dieselben wie vorher.
# Online erst zusammen mit v109 - fuer v108 stimmt die alte Fassung.
LOESCHEN = {
    "de": {
        "titel": "Konto und Daten löschen",
        "text": """
<p><b>In der App</b><br>
Öffne Zmaj, tippe oben auf dein Profil und dann auf <i>Konto löschen</i>.
Das löscht dein Konto und deinen Lernstand sofort – in der Cloud und auf
diesem Handy.</p>

<p><b>Ohne die App</b><br>
Schreib von der E-Mail-Adresse deines Kontos an <a href="mailto:{mail}">{mail}</a>, Betreff
„Konto löschen“. Hast du dich mit Google angemeldet, nimm die Adresse
dieses Google-Kontos. Wir löschen dein Konto und deinen Lernstand
innerhalb von 30 Tagen und bestätigen es dir per E-Mail.</p>

<p><b>Was gelöscht wird</b><br>
Dein Konto (E-Mail-Adresse und Anmeldedaten; bei der Anmeldung mit Google
auch der Name und die Adresse des Profilbilds, die Google dabei übergibt)
und die Kopie deines Lernstands in der Cloud: gelernte Wörter, bestandene
Levels, gelesene Geschichten, Lerntage, Lernzeit, Tagesaufgaben, Münzen,
gekaufte Gegenstände, Leben und Serienschutz. Wir behalten nichts davon. Aus den Sicherungskopien von Firebase
verschwinden die Anmeldedaten danach innerhalb von 180 Tagen. Die
IP-Adressen der Anmeldungen hält Firebase zum Schutz vor Missbrauch
einige Wochen fest.</p>

<p><b>Auf deinem Handy</b><br>
Löschst du in der App, ist der Lernstand dort ebenfalls weg. Sonst
löschst du die App oder leerst ihren Speicher (<i>Einstellungen → Apps →
Zmaj → Speicher → Daten löschen</i>).</p>

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
Sie hängt an deinem Google-Konto bei Google Play, nicht an deinem
Zmaj-Konto. Wer das Konto löscht, kündigt damit kein Abo – das kündigst du
in Google Play.</p>
""",
    },
    "en": {
        "titel": "Delete your account and data",
        "text": """
<p><b>In the app</b><br>
Open Zmaj, tap your profile at the top and then <i>Delete account</i>.
This deletes your account and your progress immediately – in the cloud and
on this phone.</p>

<p><b>Without the app</b><br>
Write from your account’s email address to <a href="mailto:{mail}">{mail}</a> with the subject
“Delete account”. If you signed in with Google, use the address of that
Google account. We delete your account and your progress within 30 days
and confirm it by email.</p>

<p><b>What is deleted</b><br>
Your account (email address and sign-in data; with Google sign-in also the
name and the profile picture address that Google passes on) and the copy of
your progress in the cloud: words learned, levels passed, stories read,
learning days, learning time, daily tasks, coins, items bought, hearts and
streak freezes. We keep none of it. Firebase then removes the sign-in data from its
backups within 180 days. Firebase keeps the IP addresses of sign-ins for a
few weeks to protect against abuse.</p>

<p><b>On your phone</b><br>
If you delete in the app, your progress on the phone is gone as well.
Otherwise delete the app or clear its storage (<i>Settings → Apps → Zmaj →
Storage → Clear data</i>).</p>

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
It belongs to your Google account in Google Play, not to your Zmaj account.
Deleting the account does not cancel a subscription – you cancel it in
Google Play.</p>
""",
    },
    "tr": {
        "titel": "Hesabını ve verilerini sil",
        "text": """
<p><b>Uygulamada</b><br>
Zmaj'ı aç, yukarıda profiline, ardından <i>Hesabı sil</i>'e dokun. Bu,
hesabını ve öğrenme ilerlemeni hemen siler – hem bulutta hem bu telefonda.</p>

<p><b>Uygulama olmadan</b><br>
Hesabının e-posta adresinden <a href="mailto:{mail}">{mail}</a> adresine “Hesabı sil” konulu
bir e-posta yaz. Google ile giriş yaptıysan o Google hesabının adresini
kullan. Hesabını ve ilerlemeni 30 gün içinde sileriz ve bunu sana
e-postayla onaylarız.</p>

<p><b>Neler silinir</b><br>
Hesabın (e-posta adresi ve giriş bilgileri; Google ile girişte ayrıca
Google'ın ilettiği ad ve profil resminin adresi) ve buluttaki
ilerlemenin kopyası: öğrenilen kelimeler, geçilen seviyeler, okunan
hikâyeler, öğrenme günleri, öğrenme süresi, günlük görevler, jetonlar,
satın alınan eşyalar, canlar ve seri koruması. Hiçbirini saklamayız. Firebase giriş bilgilerini bundan sonra 180 gün
içinde yedeklerinden de siler. Girişlerin IP adreslerini Firebase, kötüye
kullanıma karşı korumak için birkaç hafta saklar.</p>

<p><b>Telefonunda</b><br>
Uygulamada silersen telefondaki ilerlemen de gider. Aksi hâlde uygulamayı
sil ya da depolamasını temizle (<i>Ayarlar → Uygulamalar → Zmaj → Depolama
→ Verileri temizle</i>).</p>

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
Tam sürüm Zmaj hesabına değil, Google Play'deki Google hesabına bağlıdır.
Hesabı silmek aboneliği iptal etmez – onu Google Play'de iptal edersin.</p>
""",
    },
    "sv": {
        "titel": "Radera konto och data",
        "text": """
<p><b>I appen</b><br>
Öppna Zmaj, tryck på din profil högst upp och sedan på <i>Radera konto</i>.
Det raderar ditt konto och dina framsteg direkt – i molnet och på den här
telefonen.</p>

<p><b>Utan appen</b><br>
Skriv från kontots e-postadress till <a href="mailto:{mail}">{mail}</a> med ämnet ”Radera
konto”. Om du loggade in med Google, använd adressen till det
Google-kontot. Vi raderar ditt konto och dina framsteg inom 30 dagar och
bekräftar det via mejl.</p>

<p><b>Det här raderas</b><br>
Ditt konto (e-postadress och inloggningsuppgifter; vid inloggning med
Google även namnet och adressen till profilbilden som Google lämnar över)
och kopian av dina framsteg i molnet: inlärda ord, klarade nivåer, lästa
berättelser, inlärningsdagar, inlärningstid, dagsuppgifter, mynt, föremål
du köpt, hjärtan och serieskydd. Vi sparar inget av det. Därefter tar Firebase bort
inloggningsuppgifterna ur sina säkerhetskopior inom 180 dagar.
IP-adresserna från inloggningarna sparar Firebase i några veckor för att
skydda mot missbruk.</p>

<p><b>På din telefon</b><br>
Raderar du i appen försvinner framstegen även där. Annars avinstallerar du
appen eller tömmer dess lagringsutrymme (<i>Inställningar → Appar → Zmaj →
Lagring → Rensa data</i>).</p>

<p><b>Androids egen säkerhetskopiering</b><br>
Har du slagit på den i ditt Google-konto finns en kopia av appens data där, och Android återställer den när du installerar om. Den raderar du i ditt Google-konto (Google Drive eller Google One → Säkerhetskopior) – vi kommer inte åt den.</p>

<p><b>Din säkerhetskopia</b><br>
Har du sparat en fil under <i>Inställningar → Säkerhetskopia</i> ligger den kvar där du lade den. Den måste du radera själv – vi kommer inte åt den.</p>

<p><b>Om du har skrivit till oss</b><br>
Ett mejl med feedback blir kvar i vår inkorg, tillsammans med din avsändaradress. Skriv till <a href="mailto:{mail}">{mail}</a>, så raderar vi det – inom 30 dagar.</p>

<p><b>Fullversionen</b><br>
Den är kopplad till ditt Google-konto i Google Play, inte till ditt
Zmaj-konto. Att radera kontot säger inte upp något abonnemang – det säger
du upp i Google Play.</p>
""",
    },
    "nl": {
        "titel": "Account en gegevens wissen",
        "text": """
<p><b>In de app</b><br>
Open Zmaj, tik bovenaan op je profiel en dan op <i>Account verwijderen</i>.
Dat verwijdert je account en je voortgang meteen – in de cloud en op deze
telefoon.</p>

<p><b>Zonder de app</b><br>
Schrijf vanaf het e-mailadres van je account naar <a href="mailto:{mail}">{mail}</a> met als
onderwerp ‘Account verwijderen’. Heb je met Google ingelogd, gebruik dan
het adres van dat Google-account. We verwijderen je account en je
voortgang binnen 30 dagen en bevestigen dat per e-mail.</p>

<p><b>Wat er gewist wordt</b><br>
Je account (e-mailadres en inloggegevens; bij inloggen met Google ook de
naam en het adres van de profielfoto die Google doorgeeft) en de kopie van
je voortgang in de cloud: geleerde woorden, gehaalde niveaus, gelezen
verhalen, leerdagen, leertijd, dagopdrachten, munten, gekochte voorwerpen,
levens en reeksbescherming. We bewaren daar niets van. Daarna haalt Firebase de inloggegevens binnen
180 dagen ook uit zijn back-ups. De IP-adressen waarmee is ingelogd
bewaart Firebase enkele weken om misbruik tegen te gaan.</p>

<p><b>Op je telefoon</b><br>
Verwijder je in de app, dan is je voortgang daar ook weg. Anders verwijder
je de app of wis je de opslag ervan (<i>Instellingen → Apps → Zmaj →
Opslag → Gegevens wissen</i>).</p>

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
Die is gekoppeld aan je Google-account in Google Play, niet aan je
Zmaj-account. Wie het account verwijdert, zegt daarmee geen abonnement op –
dat doe je in Google Play.</p>
""",
    },
    "nb": {
        "titel": "Slett konto og data",
        "text": """
<p><b>I appen</b><br>
Åpne Zmaj, trykk på profilen din øverst og deretter på <i>Slett konto</i>.
Det sletter kontoen og framgangen din med en gang – i skyen og på denne
telefonen.</p>

<p><b>Uten appen</b><br>
Skriv fra kontoens e-postadresse til <a href="mailto:{mail}">{mail}</a> med emnet «Slett
konto». Logget du inn med Google, bruk adressen til den Google-kontoen. Vi
sletter kontoen og framgangen din innen 30 dager og bekrefter det på
e-post.</p>

<p><b>Hva som blir slettet</b><br>
Kontoen din (e-postadresse og innloggingsdata; ved innlogging med Google
også navnet og adressen til profilbildet som Google gir videre) og kopien
av framgangen din i skyen: lærte ord, beståtte nivåer, leste fortellinger,
læringsdager, læringstid, dagsoppdrag, mynter, gjenstander du har kjøpt,
liv og rekkebeskyttelse. Vi beholder ingenting av det. Deretter fjerner Firebase
innloggingsdataene fra sine sikkerhetskopier innen 180 dager.
IP-adressene fra innloggingene lagrer Firebase i noen uker for å beskytte
mot misbruk.</p>

<p><b>På telefonen din</b><br>
Sletter du i appen, er framgangen borte der også. Ellers sletter du appen
eller tømmer lagringen dens (<i>Innstillinger → Apper → Zmaj → Lagring →
Tøm data</i>).</p>

<p><b>Androids egen sikkerhetskopiering</b><br>
Har du slått den på i Google-kontoen din, ligger det en kopi av appens data der, og Android gjenoppretter den når du installerer appen på nytt. Den sletter du i Google-kontoen din (Google Disk eller Google One → Sikkerhetskopier) – vi har ikke tilgang til den.</p>

<p><b>Sikkerhetskopien din</b><br>
Har du lagret en fil under <i>Innstillinger → Sikkerhetskopi</i>, ligger den der du la den. Den må du slette selv – vi har ikke tilgang til den.</p>

<p><b>Hvis du har skrevet til oss</b><br>
En tilbakemelding på e-post blir liggende i postkassen vår, sammen med avsenderadressen din. Skriv til <a href="mailto:{mail}">{mail}</a>, så sletter vi den – innen 30 dager.</p>

<p><b>Fullversjonen</b><br>
Den hører til Google-kontoen din i Google Play, ikke til Zmaj-kontoen din.
Å slette kontoen sier ikke opp et abonnement – det sier du opp i Google
Play.</p>
""",
    },
    "da": {
        "titel": "Slet konto og data",
        "text": """
<p><b>I appen</b><br>
Åbn Zmaj, tryk på din profil øverst og derefter på <i>Slet konto</i>. Det
sletter din konto og din fremgang med det samme – i skyen og på denne
telefon.</p>

<p><b>Uden appen</b><br>
Skriv fra kontoens e-mailadresse til <a href="mailto:{mail}">{mail}</a> med emnet »Slet
konto«. Loggede du ind med Google, så brug adressen til den Google-konto.
Vi sletter din konto og din fremgang inden for 30 dage og bekræfter det
på mail.</p>

<p><b>Hvad der bliver slettet</b><br>
Din konto (e-mailadresse og logindata; ved login med Google også navnet og
adressen til profilbilledet, som Google giver videre) og kopien af din
fremgang i skyen: lærte ord, beståede niveauer, læste fortællinger,
læringsdage, læringstid, dagsopgaver, mønter, købte genstande, liv og
rækkebeskyttelse. Vi beholder intet af det. Derefter fjerner Firebase logindataene fra
sine sikkerhedskopier inden for 180 dage. IP-adresserne fra logins gemmer
Firebase i nogle uger for at beskytte mod misbrug.</p>

<p><b>På din telefon</b><br>
Sletter du i appen, er fremgangen også væk dér. Ellers sletter du appen
eller rydder dens lagrede data (<i>Indstillinger → Apps → Zmaj → Lagring →
Ryd data</i>).</p>

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
Den er knyttet til din Google-konto i Google Play, ikke til din
Zmaj-konto. At slette kontoen opsiger ikke et abonnement – det opsiger du
i Google Play.</p>
""",
    },
    "fr": {
        "titel": "Supprimer ton compte et tes données",
        "text": """
<p><b>Dans l'application</b><br>
Ouvre Zmaj, touche ton profil en haut, puis <i>Supprimer le compte</i>.
Cela supprime ton compte et ta progression immédiatement – dans le cloud et
sur ce téléphone.</p>

<p><b>Sans l'application</b><br>
Écris depuis l'adresse e-mail de ton compte à <a href="mailto:{mail}">{mail}</a> avec
l'objet « Supprimer le compte ». Si tu t'es connecté avec Google, utilise
l'adresse de ce compte Google. Nous supprimons ton compte et ta
progression sous 30 jours et te le confirmons par e-mail.</p>

<p><b>Ce qui est supprimé</b><br>
Ton compte (adresse e-mail et données de connexion ; avec la connexion
Google, aussi le nom et l'adresse de la photo de profil que Google
transmet) et la copie de ta progression dans le cloud : les mots appris,
les niveaux réussis, les histoires lues, les jours d'apprentissage, le
temps d'apprentissage, les objectifs du jour, les pièces, les objets
achetés, les vies et les protections de série. Nous n'en gardons rien. Firebase efface ensuite les données de connexion
de ses sauvegardes sous 180 jours. Firebase conserve les adresses IP des
connexions quelques semaines pour se protéger des abus.</p>

<p><b>Sur ton téléphone</b><br>
Si tu supprimes dans l'application, ta progression disparaît aussi du
téléphone. Sinon, supprime l'application ou vide sa mémoire
(<i>Paramètres → Applications → Zmaj → Stockage → Effacer les
données</i>).</p>

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
Elle est liée à ton compte Google dans Google Play, pas à ton compte Zmaj.
Supprimer le compte ne résilie pas un abonnement – tu le résilies dans
Google Play.</p>
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


# Digital Asset Links (28.10.2026, v109). Die Restore-Schluessel der
# Anmeldung (ZmajAnmeldung in der Huelle) gelten fuer die Domain
# zmaj-lernapp.github.io. Ob Google dafuer wie bei Passkeys eine
# assetlinks.json verlangt, sagt die Doku nicht - sie liegt vorsorglich da
# und wird am Handy geprueft (Firebase_Plan_v109.md, 2.8).
# Die SHA-256-Fingerabdruecke der Signaturschluessel sind nicht geheim,
# gehoeren aber zu genau dieser App und stehen deshalb in der privaten
# Huelle, in fingerabdruecke.json:
#     {"de.smartdragon.zmaj": ["AA:BB:...", "..."],
#      "de.smartdragon.zmaj.test": ["..."]}
# (App-Signatur- und Upload-Schluessel fuer die Store-App, der
# Debug-Schluessel fuer die Test-App). Fehlt die Datei, gibt es keine
# assetlinks.json - lieber keine als eine falsche.
FINGERABDRUCK_FORM = re.compile(r"[0-9A-F]{2}(:[0-9A-F]{2}){31}")
RECHTE = ["delegate_permission/common.handle_all_urls", "delegate_permission/common.get_login_creds"]


def assetlinks(datei=None):
    """Der Inhalt von .well-known/assetlinks.json, oder None ohne Datei.
    Bricht ab, wenn ein Fingerabdruck nicht die Form AA:BB:... hat."""
    datei = datei or os.path.join(huelle.ordner(), "fingerabdruecke.json")
    if not os.path.exists(datei):
        return None
    with io.open(datei, encoding="utf-8") as f:
        werte = json.load(f)
    if not isinstance(werte, dict) or not werte:
        raise SystemExit("ABBRUCH: %s ist leer oder kein Objekt." % datei)
    eintraege = []
    for paket, abdruecke in sorted(werte.items()):
        if not re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+", str(paket)) or not isinstance(abdruecke, list) \
                or not abdruecke or not all(FINGERABDRUCK_FORM.fullmatch(str(a).upper()) for a in abdruecke):
            raise SystemExit("ABBRUCH: In %s hat '%s' nicht die erwartete Form "
                             "(Paketname, Liste von SHA-256 wie AA:BB:...)." % (datei, paket))
        eintraege.append({"relation": RECHTE,
                          "target": {"namespace": "android_app", "package_name": paket,
                                     "sha256_cert_fingerprints": [str(a).upper() for a in abdruecke]}})
    return json.dumps(eintraege, indent=2) + "\n"


def schreibe(datei, text):
    pfad = os.path.join(ZIEL, datei)
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with io.open(pfad, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("  %-26s %6d Bytes" % (datei, os.path.getsize(pfad)))


def main():
    """Alle Seiten nach ZIEL. Eine eigene Funktion seit 28.10.2026, damit
    tests/test_seite.py sie in einen Probeordner bauen kann."""
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
    # Ohne .nojekyll laesst GitHub Pages Ordner mit Punkt vorn weg - und
    # damit .well-known (28.10.2026).
    schreibe(".nojekyll", "")
    links = assetlinks()
    if links is None:
        print("  Hinweis: zmaj-android/fingerabdruecke.json fehlt - keine")
        print("  .well-known/assetlinks.json (siehe FIREBASE_EINRICHTEN.md).")
    else:
        schreibe(".well-known/assetlinks.json", links)
    # Die Startseite des Repositories. Sie fuehrt mit klickbaren Links zu den
    # fertigen Seiten - noetig, weil GitHub in der Dateiliste nur den
    # HTML-Quelltext zeigt und nicht die lesbare Fassung. Der Text steht in
    # seite_readme.md und wird hier nur kopiert.
    quelle = os.path.join(ORDNER, "seite_readme.md")
    if os.path.exists(quelle):
        schreibe("README.md", io.open(quelle, encoding="utf-8").read())
    else:
        print("  Hinweis: seite_readme.md fehlt - README wird nicht erzeugt.")
    # Das Symbol fuer den Browser-Tab, siehe kopf(). Kopiert, nicht neu
    # gezeichnet: Quelle ist icon_bauen.py (ANLEITUNG.md, "App-Icon").
    for quelle, datei in (("icon.ico", "favicon.ico"), ("icon-256.png", "icon-256.png")):
        pfad = os.path.join(ZIEL, datei)
        shutil.copyfile(os.path.join(ORDNER, "web", quelle), pfad)
        print("  %-26s %6d Bytes" % (datei, os.path.getsize(pfad)))
    print("\nFertig in: %s" % ZIEL)
    print("Wie es online kommt, steht in github-seite/LIESMICH.txt")


if __name__ == "__main__":
    main()
