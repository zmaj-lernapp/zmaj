<!-- Ajdin: bitte gegenlesen und in deine eigenen Worte bringen. Claude ist
     kein Muttersprachler; die englische README ist die verbindliche Fassung. -->

# Zmaj – učimo bosanski

[English](README.md) · **Bosanski**

**Besplatna aplikacija za učenje bosanskog jezika i otvoreni kurs iza nje.**
75 nivoa od prvog „Merhaba“ do ugovora o radu, 2.040 riječi s izgovorom,
16 lekcija gramatike, 12 priča za čitanje, interfejs na osam jezika.
Napredak ostaje na telefonu; od verzije v109 Android aplikacija ima korisnički
račun (Google ili e-mail) koji ga čuva. Web-demo radi bez računa.

## Za koga je Zmaj

Mnogi u dijaspori – djeca, supružnici, unuci – razumiju bosanski, ali ga ne
govore. Velike aplikacije (Duolingo, Babbel, Busuu) bosanski nemaju. Zmaj uči
ijekavski bosanski kakav se govori u Bosni (*mlijeko, lijep, vrijeme, kahva*),
po *Pravopisu bosanskoga jezika* Senahida Halilovića.

## Probajte

- **U pregledniku:** https://zmaj-lernapp.github.io/zmaj/
- **Na računaru:** `git clone https://github.com/zmaj-lernapp/zmaj.git`, pa `python3 start.py`
- **Android:** Google Play (uskoro)

## Otvoreni podaci

Sav sadržaj kursa je slobodan (CC BY-SA 4.0) u folderu [`data/`](data/):
riječi, rečenice, priče i gramatika na osam jezika, kao JSON, CSV i Anki
špil s izgovorom. Za Python (uskoro): `pip install zmaj-bosnian`.

## Pomozite

Najviše nam treba **oko izvornog govornika**. Ako neka riječ zvuči
neprirodno ili se kod vas kaže drugačije, prijavite to ovdje:
[ispravka jezika](https://github.com/zmaj-lernapp/zmaj/issues/new?template=language_correction.yml).
Git nije potreban.

Licenca: kod AGPL-3.0, sadržaj CC BY-SA 4.0.
