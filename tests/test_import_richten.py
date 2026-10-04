# -*- coding: utf-8 -*-
"""import_richten.py passt auf den heutigen Stand von web/index.html.

Das Skript liegt bereit, bis der geschlossene Test vorbei ist. Ändert sich
index.html vorher an einer seiner Stellen, soll das hier auffallen und
nicht erst am Tag des Builds."""
import io
import os


def html(wurzel):
    return io.open(os.path.join(wurzel, "web", "index.html"), encoding="utf-8", newline="").read()


def test_passt_noch_oder_ist_schon_angewendet(wurzel):
    import import_richten
    text = html(wurzel)
    if "const nurTexte = x =>" in text:
        return                       # schon geschrieben - dann gibt es nichts mehr zu prüfen
    neu, fehler = import_richten.anwenden(text)
    assert not fehler, fehler
    for spur in ("nurTexte(d.gewusst)", "anzahlBis(d.leben.anzahl, LEBEN_MAX)",
                 "Object.prototype.hasOwnProperty.call(FARBEN, id)", "const vorher = standAlsObjekt();"):
        assert neu.count(spur) == 1, spur


def test_zweimal_anwenden_bricht_ab(wurzel):
    """Ein zweiter Lauf darf nichts doppelt einbauen."""
    import import_richten
    text = html(wurzel)
    if "const nurTexte = x =>" not in text:
        text, fehler = import_richten.anwenden(text)
        assert not fehler
    _, fehler = import_richten.anwenden(text)
    assert fehler
