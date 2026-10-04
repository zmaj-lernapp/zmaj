# -*- coding: utf-8 -*-
"""kennzahlen.py bewertet ohne Netz richtig und nennt dieselben Schwellen wie PLAN.md."""
import io
import os
import re


def test_bewertung_zaehlt_erreichte_schwellen():
    import kennzahlen
    werte = {"sterne": 50, "installationen": 299, "downloads": 100, "mitwirkende": 3,
             "korrekturen": 5, "codex_reviews": 0, "scorecard": None, "verlinkungen": 2}
    zeilen, erreicht = kennzahlen.bewerten(werte)
    assert erreicht == 5
    assert [z[4] for z in zeilen] == [True, False, True, True, True, False, False, True]


def test_hugging_face_zaehlt_zu_den_downloads():
    import kennzahlen
    werte = kennzahlen.zusammenfuehren({"downloads_github": 40}, {"downloads_huggingface": 70})
    assert werte["downloads"] == 110


def test_schwellen_wie_im_plan(wurzel):
    import kennzahlen
    plan = io.open(os.path.join(wurzel, "docs", "codex-for-oss", "PLAN.md"), encoding="utf-8").read()
    abschnitt = plan[plan.index("## 5."):plan.index("## 6.")]
    for _, name, schwelle, ziel in kennzahlen.SCHWELLEN:
        zeile = next((z for z in abschnitt.splitlines() if z.startswith("| " + name)), None)
        assert zeile, name
        zahlen = [float(x.replace(" ", "").replace(",", ".")) for x in re.findall(r"\|\s*([\d ,]+)\s*(?=\|)", zeile)]
        assert float(schwelle) in zahlen and float(ziel) in zahlen, (name, zahlen)
