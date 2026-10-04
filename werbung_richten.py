# -*- coding: utf-8 -*-
r"""Behebt den letzten offenen Rest der Befunde aus WERBUNG_PRUEFUNG.md.

ACHTUNG - NICHT VOR DEM 07.10.2026 EINREICHEN. Jede Einreichung setzt
Googles Pruefuhr fuer den geschlossenen Test zurueck. Gehoert in denselben
Build wie admob_scharf.py und laeuft VOR ihm.

STAND 04.10.2026 - fast alles ist schon von Hand drin.
Das Skript hatte 16 Ersetzungen in web/index.html und zwei neue Texte in
sprachen.py. Zwischen dem 26. und 30.09.2026 wurden die Befunde direkt in
index.html behoben, oft anders gebaut als hier vorgesehen; das Skript brach
deshalb mit "0 Treffer" ab. Am 04.10.2026 Stelle fuer Stelle verglichen und
alles Erledigte herausgenommen:

  von Hand erledigt, entfernt:
   2       werbungWecker, wird beim Weglegen abgeraeumt (visibilitychange)
   4       ADMOB_TESTGERAETE, initializeForTesting mit Liste
   5 + 10  kein Platzhalter-Kasten auf dem Geraet (zeigeWerbungJetzt)
   6       einwilligungNachziehen() nach Googles Fenster, admobGestartet
   7 + 15  einwilligungFragen(): Vollversion und Geraet fragen nicht selbst
   8       eigene Widerrufszeile (setWiderrufBox) statt der Bedingung hier
   9 + 13  Riegel anzeigeLaeuft mit Sicherheitsleine und fertigEinmal()
  11 + 16  Belohnung am Ereignis onRewardedVideoAdReward
  12 + 17  Knopf zeigt werbung.laedt, Fehlschlag als kurzMeldung mit
           werbung.keine_anzeige (die Texte stehen in allen acht Sprachen;
           werbung.keine aus dem alten Entwurf braucht es nicht mehr)
  14       werbungFuerLeben() raeumt nur auf, wenn der Knopf noch haengt
  19       werbungAbgleichen() beim Start
   1       fuer das Interstitial: darfNoch() nach prepareInterstitial()

  bewusst anders entschieden, entfernt:
   3       maxAdContentRating steht von Hand auf 'Teen' (29.09.2026,
           begruendet im Kommentar in admobStart), nicht auf 'General'.
           Die Konstante ADMOB_EINSTUFUNG gibt es deshalb nicht.
  17       eine Ladefrist auch fuers Interstitial: dort wartet niemand vor
           einem Knopf; haengt prepare, macht die Sicherheitsleine des
           Riegels nach 150 s auf, und darfNoch() verhindert, dass die
           Anzeige danach noch ueber einem anderen Schirm erscheint.

  NOCH OFFEN - das ist alles, was dieses Skript heute tut:
   1       Auch das belohnte Video wird unmittelbar vor dem Zeigen noch
           einmal gefragt, ob es noch darf. Zwischen dem Tipp auf
           "Video ansehen" und dem Zeigen liegen bis zu 15 Sekunden Laden.
           Wer in der Zeit die App weglegt, bekam das Video bisher beim
           Zurueckkommen - eine Anzeige beim Wiedereintritt in die App ist
           bei Google unzulaessig, auch wenn sie vorher angefordert war.
           Von Hand gebaut wurde die Nachpruefung nur fuers Interstitial.

Befund 18 (Datenschutzerklaerung) steht in werbung_texte.py, Befund 20
(Kommentar in strings.xml) erledigt admob_scharf.py.

Probelauf:  python werbung_richten.py
Schreiben:  python werbung_richten.py --schreiben
"""
import richten

INDEX = richten.INDEX

AENDERUNGEN = [
    ("belohntes Video: Nachpruefung nach dem Laden",
     "        return false;\n"
     "      }\n"
     "      /* Punkt 11 und 16 aus WERBUNG_PRUEFUNG.md.\n",
     "        return false;\n"
     "      }\n"
     "      /* Der zweite Blick, wie beim Interstitial unten: bis hierher\n"
     "         konnten 15 Sekunden vergehen, und wer die App inzwischen\n"
     "         weggelegt hat, bekaeme das Video sonst beim Zurueckkommen.\n"
     "         Punkt 1, nachgezogen fuers belohnte Video. */\n"
     "      if(darfNoch && !darfNoch()) return false;\n"
     "      /* Punkt 11 und 16 aus WERBUNG_PRUEFUNG.md.\n"),
    ("belohntes Video: nur, solange die App vorne ist",
     "    else topfNachziehen();\n  });\n}",
     "    else topfNachziehen();\n  }, ()=> !document.hidden);   // Punkt 1: App noch vorne?\n}"),
]


def anwenden(html):
    """(neuer Text, Fehlerliste). Ein Fehler heisst: nichts wird geschrieben."""
    neu, fehler = richten.ersetze_einmal(html, AENDERUNGEN)
    return neu, fehler + richten.gleichgewicht(html, neu)


def main(argv=None):
    return richten.main(argv, AENDERUNGEN, anwenden, "werbung_richten.py")


if __name__ == "__main__":
    raise SystemExit(main())
