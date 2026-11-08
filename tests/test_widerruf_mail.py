# -*- coding: utf-8 -*-
"""Der Text der Widerrufs-Mail in allen Sprachen. Prüfbericht 1.3, G15; den Weg
durch die App prüft tests_e2e/test_widerruf.py."""
import pytest

SPRACHEN = ("de", "en", "tr", "sv", "nl", "nb", "da", "fr")

# So heißt die Bestellnummer in Mail und Kasten, klein geschrieben (schwedisch,
# norwegisch und dänisch im Kasten mit Artikel, der Wortstamm reicht).
BESTELLNUMMER = {"de": "bestellnummer", "en": "order number", "tr": "sipariş numara", "sv": "ordernum",
                 "nl": "bestelnummer", "nb": "ordrenummer", "da": "ordrenummer", "fr": "numéro de commande"}


@pytest.mark.parametrize("code", SPRACHEN)
def test_widerrufs_mail_nennt_den_vertrag(code):
    """§ 356a Abs. 2 BGB: Name, Angaben zum Vertrag, Weg für die Bestätigung.
    Ohne Google und ohne GPA: Die iOS-Fassung nimmt denselben Text."""
    import sprachen
    t = sprachen.TEXTE[code]
    mail = t["set.widerruf_mail"]
    assert mail != t["set.widerruf_text"], code
    zeilen = mail.split("\n")
    assert len(zeilen) == 6 and zeilen[1] == "" and zeilen[4] == "", (code, zeilen)
    assert zeilen[2].rstrip().endswith(":") and zeilen[3].rstrip().endswith(":"), (code, zeilen)
    # t() schneidet bei | ab, und {…} füllt es aus.
    assert "|" not in mail and "{" not in mail, code
    assert "Google" not in mail and "GPA" not in mail, code
    # Der Kasten sagt, dass die Angaben noch einzutragen sind.
    assert BESTELLNUMMER[code] in mail.lower() and BESTELLNUMMER[code] in t["set.widerruf_text"].lower(), code
