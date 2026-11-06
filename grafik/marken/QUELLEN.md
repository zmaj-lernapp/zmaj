# Fremde Zeichen auf der Linkseite

Die Linkseite `links.html` (gebaut von `seite_bauen.py`) zeigt das Abzeichen
von Google Play und die Zeichen von Instagram, TikTok und YouTube. Sie
stehen hier unverändert, so wie sie heruntergeladen wurden, am 31.10.2026.
Die Seite lädt zur Laufzeit nichts davon nach: Die Abzeichen liegen als
Datei neben der Seite, die drei Zeichen stehen als SVG in ihr.

Keins dieser Zeichen fällt unter die Lizenzen dieses Projekts. Es sind
Marken ihrer Inhaber, und sie stehen nur da, um auf die App bei Google Play
und auf unsere eigenen Profile zu verweisen.

## Google Play: `google-play/*.png`

Das Abzeichen „Get it on Google Play“ in den acht Sprachen der Seite, von
Googles Abzeichen-Seite (`play.google.com/intl/en_us/badges/`, sie leitet
inzwischen zum Partner Marketing Hub weiter):

    https://play.google.com/intl/en_us/badges/static/images/badges/<sprache>_badge_web_generic.png

Norwegisch heißt dort `no` und gilt auf der Seite für `nb`.

- Marke von Google LLC, siehe `LICENSES/LicenseRef-Google-Brand.txt`.
- Regeln: https://partnermarketinghub.withgoogle.com/brands/google-play/google-play/lockups-icons-badges/#badges
  (unverändert, mindestens 28 px hoch, ein Viertel der Höhe Freiraum
  ringsum, in der Sprache der Seite). Der Hinweis „Google Play und das
  Google-Play-Logo sind Marken von Google LLC.“ steht klein unten auf der
  Seite.

## Instagram, TikTok, YouTube: `simple-icons/*.svg`

Aus dem npm-Paket `simple-icons` in der Version 16.35.0 (11.10.2026):

    https://cdn.jsdelivr.net/npm/simple-icons@16.35.0/icons/<name>.svg

- Die Daten von Simple Icons stehen unter CC0-1.0
  (https://github.com/simple-icons/simple-icons). Die Zeichen selbst
  bleiben Marken von Meta Platforms (Instagram), ByteDance (TikTok) und
  Google LLC (YouTube).
- Die Pfade bleiben unverändert; die Seite färbt sie nur, weiß auf der
  Markenfarbe (Instagram `#FF0069`, TikTok `#000000`) bzw. in der
  Markenfarbe auf Weiß (YouTube `#FF0000`), die Farben aus
  `data/simple-icons.json` desselben Pakets.
- Regeln: https://www.meta.com/brand/resources/instagram/instagram-brand/,
  https://www.tiktokbrandhub.com/, https://brand.youtube/

## Prüfsummen (SHA-256)

`tests/test_linkseite.py` vergleicht sie, damit keine Datei unbemerkt
verändert wird.

    f72611e2df8e88204009fd896d05d5e8e83c77009c63943bbffa169559934849  google-play/en_badge_web_generic.png
    6760aac0db8d24da21f4fd803a06c6ef26c8849e0bd623420973a5666fd3a4c4  google-play/de_badge_web_generic.png
    78156c4b77c5e4b0c5ccb35cb8e542a6184aa7e7770a31ef06ba70415b410550  google-play/tr_badge_web_generic.png
    acddbc72ae1dc165c78edb16bb93735272377a283fd628d7766e68f396b6e55d  google-play/sv_badge_web_generic.png
    eee155542a2ce35619a7941837d72844beaa8ece34dbf90e958b057004c7e4de  google-play/nl_badge_web_generic.png
    3b4870ac05c2255cdb8712b78b1d2525eaf152c8c4ae244b83ed45e837231b09  google-play/no_badge_web_generic.png
    698c640d7e3865e224cab87455c0a93e757ed52d33def0d293be2016fc54b993  google-play/da_badge_web_generic.png
    57d0e69e021d5d08f1fcacfc44e6dd3c79f5d74627bfbc0f696a88f03fb06c4a  google-play/fr_badge_web_generic.png
    f53af2d1fc5292ba1433b5c1faf50005ce6a997fa302d1816989929f379a59dc  simple-icons/instagram.svg
    6f54ac8d325faacea8935bdc44cbed60206a6b408641799e5fea1cba7c1a0af7  simple-icons/tiktok.svg
    5038808acbbc4e6edda16cbeb1cc6dec80e4e4ee4e227e039c41229fa222aa8c  simple-icons/youtube.svg
